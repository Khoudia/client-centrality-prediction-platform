"""
Module de chargement et de prétraitement des données.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Classe pour charger et prétraiter les données client.
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialise le chargeur de données.

        Args:
            data_path: Chemin vers les données (optionnel)
        """
        self.data_path = data_path or Path("data/raw")
        self.processed_path = Path("data/processed")

        # Créer les dossiers s'ils n'existent pas
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)

    def load_client_data(self, filename: str) -> pd.DataFrame:
        """
        Charge les données des clients.

        Args:
            filename: Nom du fichier de données

        Returns:
            DataFrame contenant les données clients
        """
        logger.info(f"Chargement des données depuis {filename}")

        file_path = Path(self.data_path) / filename

        if not file_path.exists():
            logger.warning(f"Fichier {filename} non trouvé. Génération de données d'exemple.")
            return self.generate_sample_data()

        # Déterminer le type de fichier et charger
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_path.suffix == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Format de fichier non supporté: {file_path.suffix}")

        logger.info(f"Données chargées: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        return df

    def load_interaction_data(self, filename: str) -> pd.DataFrame:
        """
        Charge les données d'interactions entre clients.

        Args:
            filename: Nom du fichier d'interactions

        Returns:
            DataFrame contenant les interactions
        """
        logger.info(f"Chargement des interactions depuis {filename}")

        file_path = Path(self.data_path) / filename

        if not file_path.exists():
            logger.warning(f"Fichier {filename} non trouvé. Génération d'interactions d'exemple.")
            return self.generate_sample_interactions()

        df = pd.read_csv(file_path)
        logger.info(f"Interactions chargées: {df.shape[0]} lignes")
        return df

    def generate_sample_data(self, n_clients: int = 100) -> pd.DataFrame:
        """
        Génère des données d'exemple pour les tests.

        Args:
            n_clients: Nombre de clients à générer

        Returns:
            DataFrame avec des données d'exemple
        """
        logger.info(f"Génération de {n_clients} clients d'exemple")

        np.random.seed(42)

        data = {
            'client_id': [f'C{i:04d}' for i in range(n_clients)],
            'age': np.random.randint(18, 75, n_clients),
            'anciennete_mois': np.random.randint(1, 120, n_clients),
            'chiffre_affaires': np.random.lognormal(10, 1.5, n_clients),
            'nb_transactions': np.random.randint(1, 500, n_clients),
            'segment': np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'], n_clients),
            'score_satisfaction': np.random.uniform(1, 5, n_clients)
        }

        df = pd.DataFrame(data)

        # Sauvegarder les données d'exemple
        output_path = self.processed_path / 'sample_clients.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"Données d'exemple sauvegardées dans {output_path}")

        return df

    def generate_sample_interactions(self, n_interactions: int = 500) -> pd.DataFrame:
        """
        Génère des interactions d'exemple entre clients.

        Args:
            n_interactions: Nombre d'interactions à générer

        Returns:
            DataFrame avec des interactions d'exemple
        """
        logger.info(f"Génération de {n_interactions} interactions d'exemple")

        np.random.seed(42)
        n_clients = 100

        data = {
            'client_source': [f'C{i:04d}' for i in np.random.randint(0, n_clients, n_interactions)],
            'client_target': [f'C{i:04d}' for i in np.random.randint(0, n_clients, n_interactions)],
            'weight': np.random.uniform(0.1, 1.0, n_interactions),
            'type_interaction': np.random.choice(['recommandation', 'co-achat', 'reseau_social'], n_interactions)
        }

        df = pd.DataFrame(data)

        # Éviter les auto-boucles
        df = df[df['client_source'] != df['client_target']]

        # Sauvegarder les interactions d'exemple
        output_path = self.processed_path / 'sample_interactions.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"Interactions d'exemple sauvegardées dans {output_path}")

        return df

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite les données (nettoyage, encodage, normalisation).

        Args:
            df: DataFrame à prétraiter

        Returns:
            DataFrame prétraité
        """
        logger.info("Prétraitement des données...")

        df_processed = df.copy()

        # Gestion des valeurs manquantes
        df_processed = df_processed.dropna(subset=['client_id'])

        # Conversion des types si nécessaire
        if 'chiffre_affaires' in df_processed.columns:
            df_processed['chiffre_affaires'] = pd.to_numeric(df_processed['chiffre_affaires'], errors='coerce')

        logger.info(f"Prétraitement terminé: {df_processed.shape[0]} lignes conservées")

        return df_processed

    def split_train_test(self, df: pd.DataFrame, test_size: float = 0.2,
                         random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Divise les données en ensembles d'entraînement et de test.

        Args:
            df: DataFrame à diviser
            test_size: Proportion de l'ensemble de test
            random_state: Graine aléatoire pour la reproductibilité

        Returns:
            Tuple (train_df, test_df)
        """
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            df, test_size=test_size, random_state=random_state
        )

        logger.info(f"Données divisées: {len(train_df)} train, {len(test_df)} test")

        return train_df, test_df

