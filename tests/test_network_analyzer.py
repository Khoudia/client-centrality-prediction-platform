"""
Tests unitaires pour le module NetworkAnalyzer.
"""

import pytest
import pandas as pd
import networkx as nx
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.network.network_analyzer import NetworkAnalyzer
from src.data.data_loader import DataLoader


class TestNetworkAnalyzer:
    """Tests pour la classe NetworkAnalyzer"""

    @pytest.fixture
    def sample_interactions(self):
        """Fixture pour générer des interactions d'exemple"""
        loader = DataLoader()
        return loader.generate_sample_interactions(n_interactions=100)

    def test_init(self):
        """Test l'initialisation de NetworkAnalyzer"""
        analyzer = NetworkAnalyzer()
        assert analyzer.directed == False
        assert analyzer.weighted == True
        assert analyzer.graph is None

    def test_build_network(self, sample_interactions):
        """Test la construction du réseau"""
        analyzer = NetworkAnalyzer()
        graph = analyzer.build_network(sample_interactions)

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() > 0
        assert graph.number_of_edges() > 0

    def test_calculate_degree_centrality(self, sample_interactions):
        """Test le calcul de la centralité de degré"""
        analyzer = NetworkAnalyzer()
        analyzer.build_network(sample_interactions)

        centrality = analyzer.calculate_degree_centrality()

        assert isinstance(centrality, dict)
        assert len(centrality) > 0
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_calculate_all_centralities(self, sample_interactions):
        """Test le calcul de toutes les métriques"""
        analyzer = NetworkAnalyzer()
        analyzer.build_network(sample_interactions)

        metrics = analyzer.calculate_all_centralities()

        assert 'degree' in metrics
        assert 'betweenness' in metrics
        assert 'closeness' in metrics
        assert 'pagerank' in metrics

    def test_get_centrality_dataframe(self, sample_interactions):
        """Test la conversion en DataFrame"""
        analyzer = NetworkAnalyzer()
        analyzer.build_network(sample_interactions)
        analyzer.calculate_all_centralities()

        df = analyzer.get_centrality_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert 'node_id' in df.columns
        assert 'centrality_degree' in df.columns

    def test_get_network_statistics(self, sample_interactions):
        """Test le calcul des statistiques"""
        analyzer = NetworkAnalyzer()
        analyzer.build_network(sample_interactions)

        stats = analyzer.get_network_statistics()

        assert 'nb_nodes' in stats
        assert 'nb_edges' in stats
        assert 'density' in stats
        assert stats['nb_nodes'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

