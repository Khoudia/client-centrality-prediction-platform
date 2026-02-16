"""
Tests unitaires pour le module DataLoader.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.data.data_loader import DataLoader


class TestDataLoader:
    """Tests pour la classe DataLoader"""

    def test_init(self):
        """Test l'initialisation du DataLoader"""
        loader = DataLoader()
        assert loader.data_path is not None
        assert loader.processed_path is not None

    def test_generate_sample_data(self):
        """Test la génération de données d'exemple"""
        loader = DataLoader()
        df = loader.generate_sample_data(n_clients=50)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 50
        assert 'client_id' in df.columns
        assert 'chiffre_affaires' in df.columns

    def test_generate_sample_interactions(self):
        """Test la génération d'interactions d'exemple"""
        loader = DataLoader()
        df = loader.generate_sample_interactions(n_interactions=100)

        assert isinstance(df, pd.DataFrame)
        assert 'client_source' in df.columns
        assert 'client_target' in df.columns
        assert 'weight' in df.columns
        # Vérifier qu'il n'y a pas d'auto-boucles
        assert all(df['client_source'] != df['client_target'])

    def test_preprocess_data(self):
        """Test le prétraitement des données"""
        loader = DataLoader()
        df = loader.generate_sample_data(n_clients=30)

        df_processed = loader.preprocess_data(df)

        assert isinstance(df_processed, pd.DataFrame)
        assert len(df_processed) > 0

    def test_split_train_test(self):
        """Test la division train/test"""
        loader = DataLoader()
        df = loader.generate_sample_data(n_clients=100)

        train_df, test_df = loader.split_train_test(df, test_size=0.2)

        assert len(train_df) == 80
        assert len(test_df) == 20
        assert len(train_df) + len(test_df) == len(df)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

