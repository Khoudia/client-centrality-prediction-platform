"""
Module de modélisation de la satisfaction client — Hôtel Aurore Paris.

Cible principale : prédiction de la note d'avis (régression) ou
classification binaire high_satisfaction (note ≥ 8/10).

Features utilisées :
  - Variables de réservation : stay_length, lead_time_days, arrival_month,
    arrival_dow, nuits, adultes
  - Variables de canal / profil : channel_group, room_segment, pays, langue
  - Variables réseau (optionnelles) : pagerank, betweenness, eigenvector,
    weighted_degree, community_id
  - Variables financières : revenue, amount_bucket

Modèles comparés :
  - RandomForestClassifier / Regressor
  - GradientBoostingClassifier / Regressor
  - XGBoost (si disponible)
"""

import logging
import joblib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    xgb = None  # type: ignore[assignment]
    HAS_XGBOOST = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Features candidates (détection dynamique dans le dataset)
# ---------------------------------------------------------------------------
_NUMERIC_FEATURES = [
    "stay_length", "lead_time_days", "arrival_month", "arrival_dow",
    "nuits", "adultes", "enfants", "revenue",
    # Variables réseau (optionnelles)
    "pagerank", "betweenness", "eigenvector", "weighted_degree",
    "closeness", "community_id",
]

_CATEGORICAL_FEATURES = [
    "channel_group", "room_segment", "pays", "langue", "amount_bucket",
]

# Colonnes à ne JAMAIS utiliser comme features (fuite d'information ou identifiants)
_LEAKAGE_COLS = {
    # Identifiants directs
    "client_id", "node_id", "email", "telephone", "prenom", "nom",
    "titre", "code_postal",
    # Références de réservation
    "reference", "reference_partenaire", "partenaire_id",
    # Hôtel (un seul hôtel dans le dataset → valeur constante)
    "hotel_nom", "hotel_id", "hôtel (id)",
    # Dates brutes
    "date_achat", "date_arrivee", "date_depart", "derniere_modif", "date_annulation",
    # Statut annulation
    "etat", "motif_annulation", "facturation_annulation", "montant_restant",
    # Notes d'avis : cible → fuite si incluse comme feature
    "note_globale", "note_composite", "review_score", "satisfaction_norm",
    "high_satisfaction",
    "note_personnel", "note_proprete", "note_situation",
    "note_equipements", "note_confort", "note_rapport_qualite_prix",
    "has_review", "commentaire_positif", "commentaire_negatif",
    "reponse_etablissement", "titre_commentaire",
    "source", "date_commentaire",
    # Alias rétrocompatibilité à exclure pour éviter les doublons
    "centrality_degree", "centrality_betweenness", "centrality_closeness",
    "centrality_eigenvector", "centrality_pagerank",
    # Colonnes financières redondantes / à fuite
    "garantie", "montant_total",
    # Colonnes AvailPro sans valeur prédictive (binaires constantes ou admin)
    "tarifs multiples", "demande de réservation", "code promo",
    "visibilité du code promo", "assurance annulation",
    "compte société", "utilisateur compte société", "société",
    "opt-in hôtel accepté", "opt-in partenaires accepté",
    # Colonnes texte brutes non encodées
    "referrer", "commentaire_client", "moteur_reservation",
    "plateforme", "tarif", "monnaie",
}


# ===========================================================================
# Fonctions utilitaires
# ===========================================================================

def _encode_categoricals(df: pd.DataFrame, cat_cols: List[str]) -> pd.DataFrame:
    """
    Encode les colonnes catégorielles par Label Encoding.
    Robuste : ignore les colonnes absentes, gère les NaN.
    """
    df = df.copy()
    for col in cat_cols:
        if col not in df.columns:
            continue
        df[col] = df[col].fillna("unknown").astype(str)
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
    return df


def _select_features(
    df: pd.DataFrame,
    target_col: str,
    extra_exclude: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    """
    Détermine dynamiquement les features numériques et catégorielles disponibles.

    La comparaison avec _LEAKAGE_COLS est normalisée (minuscule, strip) pour
    être robuste aux accents manquants et aux majuscules.

    Returns:
        Tuple (num_features, cat_features)
    """
    # Normaliser _LEAKAGE_COLS en minuscule pour la comparaison
    exclude_norm = {str(c).lower().strip() for c in _LEAKAGE_COLS}
    if extra_exclude:
        exclude_norm.update(str(c).lower().strip() for c in extra_exclude)
    exclude_norm.add(str(target_col).lower().strip())

    def _is_excluded(col: str) -> bool:
        return col.lower().strip() in exclude_norm

    num_feats = [
        c for c in _NUMERIC_FEATURES
        if c in df.columns and not _is_excluded(c)
    ]
    cat_feats = [
        c for c in _CATEGORICAL_FEATURES
        if c in df.columns and not _is_excluded(c)
    ]

    # Ajouter d'éventuelles colonnes numériques non prévues (ex. métriques réseau)
    for col in df.select_dtypes(include=[np.number]).columns:
        if not _is_excluded(col) and col not in num_feats and col not in cat_feats:
            num_feats.append(col)

    logger.debug(f"Features numériques : {num_feats}")
    logger.debug(f"Features catégorielles : {cat_feats}")
    return num_feats, cat_feats


# ===========================================================================
# Classe SatisfactionPredictor
# ===========================================================================

class SatisfactionPredictor:
    """
    Prédit la satisfaction client de l'Hôtel Aurore Paris.

    Deux modes :
      - regression   : prédit la note d'avis (0–10)
      - classification: prédit high_satisfaction (0/1)

    Expose la même API que l'ancienne CentralityPredictor pour la
    compatibilité avec app.py.
    """

    def __init__(
        self,
        model_type: str = "random_forest",
        task: str = "classification",
        random_state: int = 42,
    ):
        """
        Args:
            model_type : 'random_forest' | 'gradient_boosting' | 'xgboost'
            task       : 'classification' | 'regression'
            random_state : graine aléatoire
        """
        self.model_type = model_type
        self.task = task
        self.random_state = random_state

        self.model = None
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.cat_features: List[str] = []
        self.feature_importances: Optional[pd.DataFrame] = None
        self.evaluation_results: Dict = {}
        self.models: Dict[str, Any] = {}  # Résultats multi-modèles
        # Stockage des encodeurs catégoriels pour l'inférence sur nouvelle observation
        self._label_encoders: Dict[str, LabelEncoder] = {}

        self._target_col = (
            "high_satisfaction" if task == "classification" else "review_score"
        )
        self._initialize_model()

    # ------------------------------------------------------------------
    # Initialisation du modèle
    # ------------------------------------------------------------------

    def _fit_and_encode(self, df: pd.DataFrame, cat_cols: List[str]) -> pd.DataFrame:
        """
        Encode les colonnes catégorielles et stocke les LabelEncoders
        pour permettre l'inférence sur une seule observation ultérieure.
        Robuste : ignore les colonnes absentes, gère les NaN.
        """
        df = df.copy()
        for col in cat_cols:
            if col not in df.columns:
                continue
            df[col] = df[col].fillna("unknown").astype(str)
            le = LabelEncoder()
            le.fit(df[col])
            self._label_encoders[col] = le
            df[col] = le.transform(df[col])
        return df

    def _initialize_model(self):
        """Instancie le modèle selon task et model_type."""
        logger.info(f"Init modèle : {self.model_type} / {self.task}")

        clf_map = {
            "random_forest": RandomForestClassifier(
                n_estimators=150, max_depth=12,
                min_samples_leaf=3, class_weight="balanced",
                random_state=self.random_state, n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100, max_depth=5,
                learning_rate=0.1, random_state=self.random_state,
            ),
        }
        reg_map = {
            "random_forest": RandomForestRegressor(
                n_estimators=150, max_depth=12,
                min_samples_leaf=3, random_state=self.random_state, n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=100, max_depth=5,
                learning_rate=0.1, random_state=self.random_state,
            ),
        }

        if HAS_XGBOOST:
            clf_map["xgboost"] = xgb.XGBClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.1,
                use_label_encoder=False, eval_metric="logloss",
                random_state=self.random_state, n_jobs=-1,
            )
            reg_map["xgboost"] = xgb.XGBRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.1,
                random_state=self.random_state, n_jobs=-1,
            )

        model_map = clf_map if self.task == "classification" else reg_map
        mt = self.model_type if self.model_type in model_map else "random_forest"
        if mt != self.model_type:
            logger.warning(f"Modèle '{self.model_type}' inconnu → 'random_forest'")
            self.model_type = mt

        self.model = model_map[mt]

    # ------------------------------------------------------------------
    # Préparation des données
    # ------------------------------------------------------------------

    def prepare_features(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = None,
        extra_exclude: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Sélectionne, encode et prépare les features pour l'entraînement.

        Args:
            df           : DataFrame principal (réservations + métriques réseau)
            target_col   : Nom de la colonne cible (auto-détectée si None)
            extra_exclude: Colonnes supplémentaires à exclure

        Returns:
            Tuple (X, y)
        """
        target = target_col or self._target_col

        df_work = df.copy()

        # Vérifier que la cible existe
        if target not in df.columns:
            if self.task == "classification" and "review_score" in df.columns and df["review_score"].notna().sum() > 10:
                target = "_derived_high_satisfaction"
                df_work[target] = (pd.to_numeric(df_work["review_score"], errors="coerce") >= 8.0).astype(int)
                logger.warning(
                    "Cible 'high_satisfaction' absente → variable dérivée depuis 'review_score'."
                )
            # Fallback : chercher la première colonne disponible
            if target not in df_work.columns:
                for alt in ["review_score", "note_globale", "high_satisfaction",
                            "note_composite", "satisfaction_norm"]:
                    if alt in df_work.columns and df_work[alt].notna().sum() > 10:
                        target = alt
                        logger.warning(f"Cible '{self._target_col}' absente → fallback '{target}'")
                        break
                else:
                    raise ValueError(
                        f"Aucune colonne cible trouvée. "
                        f"Attendues : review_score / high_satisfaction"
                    )

        # Filtrer les lignes avec cible non nulle
        df_valid = df_work[df_work[target].notna()].copy()
        if len(df_valid) < 20:
            raise ValueError(
                f"Trop peu d'observations avec {target} renseigné "
                f"({len(df_valid)}). Vérifiez la jointure avis ↔ réservations."
            )

        num_feats, cat_feats = _select_features(df_valid, target, extra_exclude)
        self.cat_features = cat_feats

        # Encoder les catégorielles et stocker les encodeurs pour l'inférence
        df_encoded = self._fit_and_encode(df_valid, cat_feats)

        all_feats = num_feats + cat_feats
        # Garder uniquement les features présentes
        all_feats = [f for f in all_feats if f in df_encoded.columns]
        self.feature_names = all_feats

        X = df_encoded[all_feats].fillna(0)
        y = df_valid[target]

        # Si tâche de classification, s'assurer que y est entier
        if self.task == "classification":
            y = y.astype(int)

        logger.info(
            f"Features préparées : {len(all_feats)} colonnes, "
            f"{len(X)} observations, cible='{target}'"
        )
        return X, y

    def _should_stratify(self, y: pd.Series) -> bool:
        """Retourne True si le stratify est applicable en classification."""
        if self.task != "classification":
            return False
        try:
            counts = y.value_counts(dropna=False)
        except Exception:
            return False
        return y.nunique() > 1 and not counts.empty and counts.min() >= 2

    def _update_feature_importances(self, n_features: int) -> None:
        """Met à jour le tableau d'importance des variables si disponible."""
        if not hasattr(self.model, "feature_importances_"):
            self.feature_importances = None
            return

        feat_names = (
            self.feature_names
            if self.feature_names
            else [f"feature_{i}" for i in range(n_features)]
        )
        self.feature_importances = pd.DataFrame({
            "feature": feat_names,
            "importance": self.model.feature_importances_,
        }).sort_values("importance", ascending=False)

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Entraîne le modèle sur un jeu déjà découpé sans re-spliter les données."""
        if len(X_train) < 2:
            raise ValueError("Jeu d'entraînement insuffisant pour ajuster le modèle.")
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        self._update_feature_importances(X_train.shape[1])

    # ------------------------------------------------------------------
    # Entraînement
    # ------------------------------------------------------------------

    def train(
        self,
        X,
        y: Optional[pd.Series] = None,
        test_size: float = 0.2,
        validation: bool = True,
        target_col: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Entraîne le modèle et évalue ses performances.

        Modes d'appel :
          - predictor.train(X, y)          : X=features DataFrame, y=Series cible
          - predictor.train(df)            : df=DataFrame complet (auto-préparation)
          - predictor.train(df, target_col="ma_cible")  : idem avec cible explicite

        Args:
            X          : Features DataFrame OU DataFrame complet (si y=None)
            y          : Série cible (optionnelle si X est le DataFrame complet)
            test_size  : Proportion du jeu de test
            validation : Si True, effectue une validation croisée 5-fold
            target_col : Nom de la colonne cible (utilisé si X est DataFrame complet)

        Returns:
            Dictionnaire de métriques.
        """
        # Mode "DataFrame complet" : X est un DataFrame, y n'est pas fourni
        if y is None and isinstance(X, pd.DataFrame):
            try:
                X_prep, y_prep = self.prepare_features(X, target_col=target_col)
            except ValueError as e:
                logger.warning(f"Préparation features impossible : {e}")
                return {}
            return self.train(X_prep, y_prep, test_size=test_size,
                              validation=validation)

        # Mode standard : X et y fournis
        logger.info(f"Entraînement du modèle {self.model_type} ({self.task})…")

        if len(X) < 20:
            logger.warning(f"Trop peu d'observations ({len(X)}) pour entraîner le modèle.")
            return {}

        if self.task == "classification" and getattr(y, "nunique", lambda: 0)() < 2:
            logger.warning("Une seule classe présente dans la cible — entraînement impossible.")
            return {}

        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state,
            stratify=y if self._should_stratify(y) else None,
        )

        self.fit(X_tr, y_tr)
        X_te_s = self.scaler.transform(X_te)

        results = self._evaluate_internal(X_te_s, y_te)
        results["train_set_size"] = len(X_tr)
        results["test_set_size"] = len(X_te)
        results["model_type"] = self.model_type
        results["task"] = self.task
        results["n_features"] = len(self.feature_names) if self.feature_names else X_tr.shape[1]

        if validation and len(X_tr) >= 50:
            cv_scoring = "f1_weighted" if self.task == "classification" else "r2"
            try:
                cv_folds = min(5, max(2, len(X_tr) // 10))
                cv_model = make_pipeline(StandardScaler(), clone(self.model))
                cv_scores = cross_val_score(
                    cv_model, X_tr, y_tr, cv=cv_folds,
                    scoring=cv_scoring
                )
                results["cv_mean"] = round(float(cv_scores.mean()), 4)
                results["cv_std"] = round(float(cv_scores.std()), 4)
            except Exception as e:
                logger.warning(f"Validation croisée échouée : {e}")


        self.evaluation_results = results
        logger.info(f"Résultats : {results}")
        return results

    def _evaluate_internal(self, X_test_scaled, y_test) -> Dict:
        """Calcule les métriques selon la tâche."""
        y_pred = self.model.predict(X_test_scaled)

        if self.task == "classification":
            acc = round(accuracy_score(y_test, y_pred), 4)
            f1 = round(f1_score(y_test, y_pred, average="weighted", zero_division=0), 4)
            try:
                y_prob = self.model.predict_proba(X_test_scaled)[:, 1]
                auc = round(roc_auc_score(y_test, y_prob), 4)
            except Exception:
                auc = None
            return {"accuracy": acc, "f1_weighted": f1, "roc_auc": auc}
        else:
            mse = mean_squared_error(y_test, y_pred)
            return {
                "rmse": round(np.sqrt(mse), 4),
                "mae": round(mean_absolute_error(y_test, y_pred), 4),
                "r2": round(r2_score(y_test, y_pred), 4),
            }

    # ------------------------------------------------------------------
    # Comparaison multi-modèles
    # ------------------------------------------------------------------

    def train_all_models(
        self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2
    ) -> Dict[str, Dict]:
        """
        Entraîne et compare tous les modèles disponibles.

        Returns:
            Dictionnaire {model_name: métriques}.
        """
        logger.info("Comparaison multi-modèles…")
        all_results = {}
        model_types = ["random_forest", "gradient_boosting"]
        if HAS_XGBOOST:
            model_types.append("xgboost")

        for mt in model_types:
            try:
                self.model_type = mt
                self._initialize_model()
                res = self.train(X, y, test_size=test_size, validation=False)
                all_results[mt] = res
                self.models[mt] = {
                    "model": self.model,
                    "scaler": self.scaler,
                    "results": res,
                }
            except Exception as e:
                logger.warning(f"Modèle {mt} échoué : {e}")
                all_results[mt] = {"error": str(e)}

        return all_results

    # ------------------------------------------------------------------
    # Prédiction
    # ------------------------------------------------------------------

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Prédit sur de nouvelles données."""
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné.")
        X_s = self.scaler.transform(X.fillna(0))
        return self.model.predict(X_s)

    def predict_proba(self, X: pd.DataFrame) -> Optional[np.ndarray]:
        """Probabilités de classe (classification uniquement)."""
        if self.task != "classification" or not hasattr(self.model, "predict_proba"):
            return None
        X_s = self.scaler.transform(X.fillna(0))
        return self.model.predict_proba(X_s)

    # ------------------------------------------------------------------
    # Prédiction sur une seule observation (nouvel onglet Scoring)
    # ------------------------------------------------------------------

    def _encode_single_categoricals(self, row: dict) -> dict:
        """
        Encode les variables catégorielles d'une observation unique
        en utilisant les LabelEncoders stockés lors de l'entraînement.
        Les catégories inconnues sont ramenées à "unknown" (ou 0 par défaut).
        """
        row = row.copy()
        for col in self.cat_features:
            if col not in row:
                row[col] = 0
                continue
            val = row[col]
            if val is None or (isinstance(val, float) and np.isnan(val)):
                row[col] = 0
                continue
            val_str = str(val)
            if col in self._label_encoders:
                le = self._label_encoders[col]
                known = set(le.classes_)
                if val_str not in known:
                    val_str = "unknown" if "unknown" in known else None
                if val_str is not None:
                    row[col] = int(le.transform([val_str])[0])
                else:
                    row[col] = 0
            else:
                row[col] = 0
        return row

    @staticmethod
    def _get_satisfaction_level(score: float) -> dict:
        """Retourne les informations de niveau de satisfaction selon le score."""
        if score >= 9.0:
            return {
                "satisfaction_level": "Satisfaction très probable",
                "level_color": "green",
                "level_icon": "🟢",
                "level_num": 4,
                "vigilance": "Faible",
                "attention": "Standard",
                "conseil": (
                    "Maintenir l'excellence du service. Ce profil est à fort potentiel "
                    "de fidélisation. Valoriser la qualité de l'expérience dès le check-in."
                ),
            }
        elif score >= 7.5:
            return {
                "satisfaction_level": "Satisfaction élevée",
                "level_color": "#2ecc71",
                "level_icon": "🟡",
                "level_num": 3,
                "vigilance": "Faible à modérée",
                "attention": "Soignée",
                "conseil": (
                    "Accueil chaleureux et fluide. Valoriser la qualité de l'expérience. "
                    "S'assurer de la clarté des informations à l'arrivée."
                ),
            }
        elif score >= 6.0:
            return {
                "satisfaction_level": "Satisfaction moyenne",
                "level_color": "orange",
                "level_icon": "🟠",
                "level_num": 2,
                "vigilance": "Modérée",
                "attention": "Renforcée",
                "conseil": (
                    "Veiller à la clarté des informations, à la fluidité de l'arrivée "
                    "et au confort perçu. Anticiper les besoins potentiels."
                ),
            }
        else:
            return {
                "satisfaction_level": "Satisfaction fragile",
                "level_color": "red",
                "level_icon": "🔴",
                "level_num": 1,
                "vigilance": "Élevée",
                "attention": "Très attentive",
                "conseil": (
                    "Anticiper les besoins et prévoir une prise en charge proactive "
                    "dès l'arrivée. Soigner chaque étape du séjour."
                ),
            }

    @staticmethod
    def _generate_receptionist_message(score: float, client_dict: dict) -> str:
        """
        Génère un message professionnel, bienveillant et exploitable pour la réception.
        Le message est orienté qualité de service — jamais discriminatoire.
        """
        if score >= 9.0:
            base = (
                "Client à fort potentiel de satisfaction. "
                "Accueil chaleureux recommandé et mise en valeur de la qualité "
                "de l'expérience dès le check-in. Proposer une présentation "
                "soignée des services de l'hôtel."
            )
        elif score >= 7.5:
            base = (
                "Client à bon potentiel de satisfaction. "
                "Maintenir un accueil soigné et s'assurer de la fluidité "
                "des procédures d'arrivée. Veiller à communiquer clairement "
                "les informations pratiques."
            )
        elif score >= 6.0:
            base = (
                "Accueil recommandé : attentionné et rassurant. "
                "Veiller à une prise en charge fluide à l'arrivée "
                "et à une information claire sur les services de l'hôtel. "
                "Anticiper les questions fréquentes."
            )
        else:
            base = (
                "Prévoir une attention particulière à la clarté des explications "
                "et au confort perçu lors de l'arrivée. "
                "Anticiper les besoins du client et assurer un suivi "
                "attentif durant le séjour."
            )

        extras = []
        stay = client_dict.get("stay_length", 0) or 0
        lead = client_dict.get("lead_time_days", 0) or 0
        enfants = client_dict.get("enfants", 0) or 0
        adultes = client_dict.get("adultes", 0) or 0
        month = client_dict.get("arrival_month")

        if stay >= 5:
            extras.append(
                f"Séjour prolongé ({stay:.0f} nuits) : "
                "proposer les services adaptés et veiller au confort dans la durée"
            )
        elif stay == 1:
            extras.append(
                "Séjour d'une nuit : check-in et check-out efficaces, "
                "informations essentielles bien communiquées"
            )
        if lead == 0:
            extras.append(
                "Réservation de dernière minute : "
                "accueil rapide et efficace, anticiper les attentes immédiates"
            )
        elif lead > 60:
            extras.append(
                f"Réservation planifiée ({lead:.0f} jours à l'avance) : "
                "maintenir les attentes et confirmer les détails du séjour"
            )
        if enfants > 0:
            extras.append(
                "Famille avec enfants : "
                "veiller à la convivialité, signaler les équipements famille"
            )
        if adultes >= 3:
            extras.append(
                "Groupe de plusieurs adultes : "
                "coordonner les chambres et informations pratiques de groupe"
            )
        if month in (12, 1, 2):
            extras.append("Arrivée en période hivernale : confort thermique à soigner")
        elif month in (7, 8):
            extras.append("Arrivée en haute saison : gérer l'attente avec fluidité")

        if extras:
            base += "\n\n⚑ Points d'attention : " + " — ".join(extras) + "."

        return base

    @staticmethod
    def _generate_probable_reviews(score: float, client_dict: dict) -> List[str]:
        """
        Génère des phrases d'avis probables basées sur le score prédit
        et les caractéristiques du client.
        """
        channel = client_dict.get("channel_group", "")
        stay = client_dict.get("stay_length", 0) or 0
        enfants = client_dict.get("enfants", 0) or 0

        if score >= 9.0:
            base_phrases = [
                "L'accueil a été excellent et l'équipe très professionnelle.",
                "La localisation est idéale et le confort de la chambre irréprochable.",
                "Un séjour très satisfaisant, que je recommande vivement.",
                "L'hôtel répond parfaitement aux attentes, très bon rapport qualité/prix.",
            ]
        elif score >= 7.5:
            base_phrases = [
                "L'accueil a été agréable et la localisation très pratique.",
                "Le séjour s'est passé dans de bonnes conditions, personnel attentionné.",
                "Bonne expérience globale, hôtel bien situé près de la gare.",
                "Chambre propre et confortable, équipe réactive.",
            ]
        elif score >= 6.0:
            base_phrases = [
                "Le séjour était convenable, avec quelques points d'amélioration possibles.",
                "La localisation est un point fort, mais certains aspects pourraient être améliorés.",
                "Séjour correct dans l'ensemble, accueil standard.",
                "L'hôtel remplit sa fonction, mais l'expérience pourrait être plus personnalisée.",
            ]
        else:
            base_phrases = [
                "Le séjour ne correspondait pas tout à fait aux attentes initiales.",
                "Des améliorations seraient souhaitables, notamment sur l'accueil et le confort.",
                "Expérience en deçà des espérances, certains aspects méritent attention.",
            ]

        # Ajustements contextuels
        if stay >= 5:
            base_phrases.append(
                f"Pour un séjour de {stay:.0f} nuits, la qualité des services "
                "sur la durée est un élément clé."
            )
        if enfants > 0:
            base_phrases.append(
                "L'hôtel convient aux familles, les équipements dédiés "
                "sont appréciés."
            )
        if channel and "direct" in str(channel).lower():
            base_phrases.append(
                "La réservation directe a permis une communication fluide avant l'arrivée."
            )

        return base_phrases[:4]

    def _get_prediction_factors(self, row: dict) -> dict:
        """
        Identifie les facteurs favorables et les points de vigilance
        basés sur les valeurs fournies et l'importance des features.
        """
        favorable = []
        vigilance_pts = []

        if self.feature_importances is not None:
            top_features = self.feature_importances.head(8)["feature"].tolist()
        else:
            top_features = list(row.keys())[:8]

        for feat in top_features:
            val = row.get(feat)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                vigilance_pts.append(f"`{feat}` non renseigné (valeur manquante)")
                continue

            # Heuristiques métier
            if feat == "stay_length":
                if val >= 3:
                    favorable.append(f"Durée de séjour de {val:.0f} nuits (signal positif)")
                elif val == 1:
                    vigilance_pts.append("Séjour d'une nuit (satisfaction plus difficile à fidéliser)")
            elif feat == "lead_time_days":
                if val > 30:
                    favorable.append(f"Réservation anticipée ({val:.0f} j) — attentes gérables")
                elif val == 0:
                    vigilance_pts.append("Réservation last-minute (attentes à cadrer rapidement)")
            elif feat == "adultes":
                if val >= 3:
                    vigilance_pts.append(f"Groupe de {val:.0f} adultes — coordination requise")
            elif feat == "enfants":
                if val > 0:
                    vigilance_pts.append(f"Famille avec {val:.0f} enfant(s) — attentes spécifiques")

        return {"favorable": favorable, "vigilance": vigilance_pts}

    def predict_single(self, client_dict: dict) -> dict:
        """
        Prédit la satisfaction pour un seul nouveau client/séjour.

        Le modèle doit avoir été entraîné au préalable (appel à train()).
        Les valeurs manquantes sont gérées automatiquement (remplacement par 0).
        Les catégories inconnues sont ramenées à "unknown" ou 0.

        Args:
            client_dict: Dictionnaire {nom_feature: valeur}.
                         Les clés ne correspondant pas aux features du modèle
                         sont ignorées silencieusement.

        Returns:
            Dictionnaire structuré avec :
                - prediction        : valeur prédite (0/1 ou float)
                - probability       : probabilité de haute satisfaction
                - score             : score 0-10 interprétable
                - satisfaction_level: libellé textuel du niveau
                - level_icon        : emoji indicateur
                - level_num         : rang 1-4
                - vigilance         : niveau de vigilance recommandé
                - attention         : niveau d'attention requis
                - conseil           : conseil synthétique
                - receptionist_msg  : message professionnel pour la réception
                - probable_reviews  : liste de phrases d'avis probables
                - feature_factors   : dict {favorable, vigilance} des facteurs
                - features_used     : dict des features fournies
                - n_features_provided, n_features_total : couverture de features
        """
        if self.model is None:
            raise ValueError(
                "Le modèle n'a pas été entraîné. Appelez .train() d'abord."
            )
        if not self.feature_names:
            raise ValueError(
                "Aucune feature connue. Le modèle doit être entraîné via .prepare_features()."
            )

        # 1. Construire la ligne avec toutes les features attendues (NaN par défaut)
        row: dict = {feat: np.nan for feat in self.feature_names}

        # 2. Remplir avec les valeurs fournies (uniquement les features connues)
        for key, val in client_dict.items():
            if key in row:
                row[key] = val

        # 3. Encoder les catégorielles
        row = self._encode_single_categoricals(row)

        # 4. Remplir les NaN restants avec 0
        for feat in self.feature_names:
            if feat not in row or (isinstance(row[feat], float) and np.isnan(row[feat])):
                row[feat] = 0

        # 5. Construire le DataFrame de prédiction
        X_single = pd.DataFrame([row])[self.feature_names].fillna(0)

        # 6. Mettre à l'échelle
        X_scaled = self.scaler.transform(X_single)

        # 7. Prédire
        if self.task == "classification":
            pred_val = int(self.model.predict(X_scaled)[0])
            prob_high: Optional[float] = None
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(X_scaled)[0]
                prob_high = float(proba[1]) if len(proba) > 1 else float(proba[0])
            # Score 0-10 interprétable
            score = (prob_high * 10) if prob_high is not None else (8.5 if pred_val == 1 else 5.0)
        else:
            score_raw = float(self.model.predict(X_scaled)[0])
            score = max(0.0, min(10.0, score_raw))
            pred_val = 1 if score >= 8 else 0
            prob_high = score / 10.0

        # 8. Niveaux et interprétations
        level_info = self._get_satisfaction_level(score)
        receptionist_msg = self._generate_receptionist_message(score, client_dict)
        probable_reviews = self._generate_probable_reviews(score, client_dict)
        feature_factors = self._get_prediction_factors(row)

        n_provided = sum(
            1 for k in client_dict
            if k in self.feature_names and client_dict[k] is not None
        )

        return {
            "prediction": pred_val,
            "probability": round(prob_high, 4) if prob_high is not None else None,
            "score": round(score, 2),
            **level_info,
            "receptionist_msg": receptionist_msg,
            "probable_reviews": probable_reviews,
            "feature_factors": feature_factors,
            "features_used": {k: v for k, v in client_dict.items()},
            "n_features_provided": n_provided,
            "n_features_total": len(self.feature_names),
        }

    # ------------------------------------------------------------------
    # Accesseurs
    # ------------------------------------------------------------------

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """Évalue le modèle sur un jeu de test externe."""
        X_s = self.scaler.transform(X_test.fillna(0))
        results = self._evaluate_internal(X_s, y_test)
        self.evaluation_results = results
        return results

    def get_feature_importance(
        self, metric: Optional[str] = None, top_n: int = 15
    ) -> pd.DataFrame:
        """Retourne l'importance des features (top_n)."""
        if self.feature_importances is None:
            logger.warning("Importance des features non disponible.")
            return pd.DataFrame(columns=["feature", "importance"])
        return self.feature_importances.head(top_n)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_model(self, path: str = "models/satisfaction_predictor.joblib"):
        Path("models").mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        joblib.dump(self.scaler, path.replace(".joblib", "_scaler.joblib"))
        logger.info(f"Modèle sauvegardé : {path}")

    def save_models(self, prefix: str = "model"):
        """Sauvegarde le modèle courant avec préfixe."""
        self.save_model(f"models/{prefix}_{self.model_type}.joblib")

    def load_model(self, path: str = "models/satisfaction_predictor.joblib"):
        self.model = joblib.load(path)
        self.scaler = joblib.load(path.replace(".joblib", "_scaler.joblib"))
        logger.info(f"Modèle chargé : {path}")

    # ------------------------------------------------------------------
    # Compatibilité avec l'ancienne API CentralityPredictor
    # ------------------------------------------------------------------

    def hyperparameter_tuning(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Grille d'hyperparamètres simplifiée."""
        from sklearn.model_selection import GridSearchCV
        X_s = self.scaler.fit_transform(X.fillna(0))
        param_grid = {
            "random_forest": {
                "n_estimators": [100, 200],
                "max_depth": [8, 12],
                "min_samples_leaf": [2, 5],
            },
            "gradient_boosting": {
                "n_estimators": [100, 200],
                "max_depth": [3, 5],
                "learning_rate": [0.05, 0.1],
            },
        }.get(self.model_type, {"n_estimators": [100]})

        scoring = "f1_weighted" if self.task == "classification" else "r2"
        gs = GridSearchCV(self.model, param_grid, cv=5, scoring=scoring, n_jobs=-1)
        gs.fit(X_s, y)
        self.model = gs.best_estimator_
        logger.info(f"Meilleurs params : {gs.best_params_} (score={gs.best_score_:.4f})")
        return {"best_params": gs.best_params_, "best_score": gs.best_score_}


# ===========================================================================
# Alias — CentralityPredictor redirige vers SatisfactionPredictor
# ===========================================================================

class CentralityPredictor(SatisfactionPredictor):
    """
    Alias de compatibilité : l'ancienne CentralityPredictor est remplacée par
    SatisfactionPredictor mais conserve le même nom pour ne pas casser app.py.
    """

    def __init__(self, model_type: str = "random_forest", random_state: int = 42):
        super().__init__(model_type=model_type, task="classification",
                         random_state=random_state)
        logger.info(
            "CentralityPredictor → SatisfactionPredictor (tâche=classification)"
        )
