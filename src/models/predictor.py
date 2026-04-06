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

        self._target_col = (
            "high_satisfaction" if task == "classification" else "review_score"
        )
        self._initialize_model()

    # ------------------------------------------------------------------
    # Initialisation du modèle
    # ------------------------------------------------------------------

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

        # Encoder les catégorielles
        df_encoded = _encode_categoricals(df_valid, cat_feats)

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
