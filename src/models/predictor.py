"""
Module pour la prédiction de centralité client.

Ce module implémente des modèles de machine learning pour prédire
la centralité des clients basée sur leurs caractéristiques.
"""

import pandas as pd
import numpy as np
import logging
import joblib
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Any
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

logger = logging.getLogger(__name__)


class CentralityPredictor:
    """
    Classe pour prédire la centralité des clients.

    Implémente plusieurs modèles de machine learning pour prédire
    les métriques de centralité basées sur les caractéristiques clients.
    """

    def __init__(self, model_type: str = 'random_forest', random_state: int = 42):
        """
        Initialise le prédicteur.

        Args:
            model_type: Type de modèle ('random_forest', 'xgboost', 'gradient_boosting')
            random_state: Graine aléatoire pour la reproductibilité
        """
        self.model_type = model_type
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.feature_importances = None
        self.evaluation_results = {}
        self.models = {}  # Pour stocker plusieurs modèles

        self._initialize_model()

    def _initialize_model(self):
        """Initialise le modèle selon le type spécifié."""
        logger.info(f"Initialisation du modèle : {self.model_type}")

        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1
            )

        elif self.model_type == 'xgboost':
            if not HAS_XGBOOST:
                logger.warning("XGBoost non installé, utilisation de RandomForest")
                self.model_type = 'random_forest'
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    random_state=self.random_state,
                    n_jobs=-1
                )
            else:
                self.model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=self.random_state,
                    n_jobs=-1
                )

        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=self.random_state
            )

        else:
            logger.warning(f"Modèle '{self.model_type}' inconnu, utilisation de RandomForest")
            self.model_type = 'random_forest'
            self._initialize_model()

    def prepare_features(self, df_clients: pd.DataFrame,
                        df_centrality: pd.DataFrame,
                        target_metric: str = 'pagerank') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prépare les features et la cible pour l'entraînement.

        Args:
            df_clients: DataFrame avec les caractéristiques des clients
            df_centrality: DataFrame avec les métriques de centralité
            target_metric: Métrique de centralité cible

        Returns:
            Tuple (X, y) prêts pour l'entraînement
        """
        logger.info(f"Préparation des features pour la prédiction de {target_metric}...")

        # Fusionner les données
        df_merged = df_clients.merge(df_centrality, on='client_id', how='inner')

        # Sélectionner les features numériques (exclure les identifiants et la cible)
        exclude_cols = {'client_id', 'segment'} | set(df_centrality.columns) - {'client_id'}
        feature_cols = [col for col in df_clients.columns
                       if col not in exclude_cols and df_clients[col].dtype in [np.float64, np.int64]]

        # Ajouter les features numériques du DataFrame de centralité si présentes
        for col in df_merged.columns:
            if col not in feature_cols and col not in {'client_id', target_metric}:
                if df_merged[col].dtype in [np.float64, np.int64]:
                    feature_cols.append(col)

        self.feature_names = feature_cols

        X = df_merged[feature_cols].fillna(0)
        y = df_merged[target_metric]

        logger.info(f"Features préparées : {len(feature_cols)} colonnes, {len(X)} lignes")

        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series,
              test_size: float = 0.2, validation: bool = True) -> Dict[str, float]:
        """
        Entraîne le modèle.

        Args:
            X: Features d'entraînement
            y: Cibles d'entraînement
            test_size: Proportion du test set
            validation: Si True, effectue une validation croisée

        Returns:
            Dictionnaire avec les résultats d'entraînement
        """
        logger.info(f"Entraînement du modèle {self.model_type}...")

        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )

        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Entraînement
        self.model.fit(X_train_scaled, y_train)
        logger.info("Modèle entraîné")

        # Évaluation
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)

        logger.info(f"Score d'entraînement (R²) : {train_score:.4f}")
        logger.info(f"Score de test (R²) : {test_score:.4f}")

        # Validation croisée
        cv_mean = None
        cv_std = None
        if validation:
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train,
                                       cv=5, scoring='r2')
            cv_mean = float(cv_scores.mean())
            cv_std = float(cv_scores.std())
            logger.info(f"Scores de validation croisée : {cv_mean:.4f} (+/- {cv_std:.4f})")

        # Sauvegarde de l'importance des features
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importances = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

        return {
            'model_type': self.model_type,
            'train_score': train_score,
            'test_score': test_score,
            'train_set_size': len(X_train),
            'test_set_size': len(X_test),
            'cv_r2_mean': cv_mean,
            'cv_r2_std': cv_std
        }

    def train_all_models(self, X: pd.DataFrame, y: pd.Series,
                        test_size: float = 0.2) -> Dict[str, Dict]:
        """
        Entraîne tous les modèles disponibles.

        Args:
            X: Features d'entraînement
            y: Cibles d'entraînement
            test_size: Proportion du test set

        Returns:
            Dictionnaire avec les résultats pour chaque modèle
        """
        logger.info("Entraînement de tous les modèles disponibles...")

        results = {}
        model_types = ['random_forest', 'gradient_boosting']
        if HAS_XGBOOST:
            model_types.append('xgboost')

        for model_type in model_types:
            logger.info(f"--- Entraînement du modèle {model_type} ---")
            self.model_type = model_type
            self._initialize_model()

            results[model_type] = self.train(X, y, test_size=test_size, validation=False)
            self.models[model_type] = self.model

        return results

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """
        Évalue le modèle sur un ensemble de test.

        Args:
            X_test: Features de test
            y_test: Cibles de test

        Returns:
            Dictionnaire avec les métriques d'évaluation
        """
        logger.info("Évaluation du modèle...")

        X_test_scaled = self.scaler.transform(X_test)
        predictions = self.model.predict(X_test_scaled)

        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        self.evaluation_results = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'test_set_size': len(X_test)
        }

        logger.info(f"MSE: {mse:.4f}")
        logger.info(f"RMSE: {rmse:.4f}")
        logger.info(f"MAE: {mae:.4f}")
        logger.info(f"R²: {r2:.4f}")

        return self.evaluation_results

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fait des prédictions.

        Args:
            X: Features pour la prédiction

        Returns:
            Prédictions
        """
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def hyperparameter_tuning(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Effectue une recherche d'hyperparamètres.

        Args:
            X: Features d'entraînement
            y: Cibles d'entraînement

        Returns:
            Dictionnaire avec les meilleurs paramètres et score
        """
        logger.info(f"Tuning des hyperparamètres du modèle {self.model_type}...")

        X_scaled = self.scaler.fit_transform(X)

        if self.model_type == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 15, 20],
                'min_samples_split': [2, 5, 10]
            }

        elif self.model_type == 'xgboost':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3]
            }

        elif self.model_type == 'gradient_boosting':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3]
            }

        else:
            return {'error': f'Modèle {self.model_type} non supporté'}

        grid_search = GridSearchCV(
            self.model,
            param_grid,
            cv=5,
            scoring='r2',
            n_jobs=-1
        )

        grid_search.fit(X_scaled, y)

        results = {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'best_estimator': grid_search.best_estimator_
        }

        # Mettre à jour le modèle
        self.model = grid_search.best_estimator_

        logger.info(f"Meilleurs paramètres trouvés : {grid_search.best_params_}")
        logger.info(f"Meilleur score : {grid_search.best_score_:.4f}")

        return results

    def get_feature_importance(self, metric: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
        """
        Retourne l'importance des features.

        Args:
            metric: Métrique ciblée (optionnelle, non utilisée pour un modèle unique)
            top_n: Nombre de features à retourner

        Returns:
            DataFrame avec l'importance des features
        """
        if self.feature_importances is None:
            logger.warning("L'importance des features n'est pas disponible")
            return pd.DataFrame()

        return self.feature_importances.head(top_n)

    def save_models(self, prefix: str = 'model'):
        """
        Sauvegarde le modèle courant et le scaler avec un préfixe.

        Args:
            prefix: Préfixe de sauvegarde
        """
        Path('models').mkdir(parents=True, exist_ok=True)

        model_path = Path('models') / f"{prefix}_{self.model_type}.joblib"
        scaler_path = Path('models') / f"{prefix}_{self.model_type}_scaler.joblib"

        joblib.dump(self.model, str(model_path))
        joblib.dump(self.scaler, str(scaler_path))

        logger.info(f"Modèle sauvegardé en {model_path}")
        logger.info(f"Scaler sauvegardé en {scaler_path}")

    def save_model(self, path: str = 'models/predictor.joblib'):
        """
        Sauvegarde le modèle et le scaler.

        Args:
            path: Chemin de sauvegarde
        """
        Path('models').mkdir(parents=True, exist_ok=True)

        joblib.dump(self.model, path)
        joblib.dump(self.scaler, path.replace('.joblib', '_scaler.joblib'))

        logger.info(f"Modèle sauvegardé en {path}")

    def load_model(self, path: str = 'models/predictor.joblib'):
        """
        Charge un modèle sauvegardé.

        Args:
            path: Chemin du modèle
        """
        self.model = joblib.load(path)
        self.scaler = joblib.load(path.replace('.joblib', '_scaler.joblib'))

        logger.info(f"Modèle chargé depuis {path}")
