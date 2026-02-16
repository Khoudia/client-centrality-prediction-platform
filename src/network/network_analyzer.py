"""
Module pour l'analyse de réseau des clients.

Ce module implémente l'analyse de réseaux sociaux et professionnels
pour identifier l'importance/centralité des clients.
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, Tuple, List, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """
    Classe pour analyser les réseaux de clients.

    Fournit des méthodes pour construire des graphes, calculer les
    métriques de centralité et analyser les propriétés du réseau.
    """

    def __init__(self, graph: Optional[nx.Graph] = None):
        """
        Initialise l'analyseur de réseau.

        Args:
            graph: Graphe NetworkX optionnel (par défaut, créé vide)
        """
        self.graph = graph or nx.Graph()
        self.centrality_metrics = {}
        self.network_stats = {}

    def build_network(self, df_interactions: pd.DataFrame,
                     weight_col: str = 'weight',
                     source_col: str = 'client_source',
                     target_col: str = 'client_target') -> nx.Graph:
        """
        Construit un graphe à partir d'un DataFrame d'interactions.

        Args:
            df_interactions: DataFrame avec colonnes source, target, weight
            weight_col: Nom de la colonne de poids
            source_col: Nom de la colonne source
            target_col: Nom de la colonne cible

        Returns:
            Graphe NetworkX construit
        """
        logger.info(f"Construction du graphe avec {len(df_interactions)} interactions...")

        self.graph = nx.Graph()

        for _, row in df_interactions.iterrows():
            source = row[source_col]
            target = row[target_col]
            weight = row.get(weight_col, 1.0)

            self.graph.add_edge(source, target, weight=float(weight))

        logger.info(f"Graphe créé : {self.graph.number_of_nodes()} nœuds, "
                   f"{self.graph.number_of_edges()} arêtes")

        return self.graph

    def calculate_degree_centrality(self) -> Dict[str, float]:
        """
        Calcule la centralité de degré.

        Returns:
            Dictionnaire {nœud: centralité}
        """
        centrality = nx.degree_centrality(self.graph)
        self.centrality_metrics['degree'] = centrality
        logger.info("Centralité de degré calculée")
        return centrality

    def calculate_betweenness_centrality(self) -> Dict[str, float]:
        """
        Calcule la centralité d'intermédiarité.

        Returns:
            Dictionnaire {nœud: centralité}
        """
        centrality = nx.betweenness_centrality(self.graph, weight='weight')
        self.centrality_metrics['betweenness'] = centrality
        logger.info("Centralité d'intermédiarité calculée")
        return centrality

    def calculate_closeness_centrality(self) -> Dict[str, float]:
        """
        Calcule la centralité de proximité.

        Returns:
            Dictionnaire {nœud: centralité}
        """
        centrality = nx.closeness_centrality(self.graph, distance='weight')
        self.centrality_metrics['closeness'] = centrality
        logger.info("Centralité de proximité calculée")
        return centrality

    def calculate_eigenvector_centrality(self, max_iter: int = 100) -> Dict[str, float]:
        """
        Calcule la centralité de vecteur propre.

        Args:
            max_iter: Nombre maximum d'itérations

        Returns:
            Dictionnaire {nœud: centralité}
        """
        try:
            centrality = nx.eigenvector_centrality(
                self.graph,
                weight='weight',
                max_iter=max_iter
            )
            self.centrality_metrics['eigenvector'] = centrality
            logger.info("Centralité de vecteur propre calculée")
            return centrality
        except Exception as e:
            logger.warning(f"Erreur dans le calcul de la centralité de vecteur propre: {e}")
            # Retourner une centralité de degré en fallback
            return self.calculate_degree_centrality()

    def calculate_pagerank(self, alpha: float = 0.85) -> Dict[str, float]:
        """
        Calcule le PageRank.

        Args:
            alpha: Paramètre d'amortissement (damping factor)

        Returns:
            Dictionnaire {nœud: PageRank}
        """
        centrality = nx.pagerank(self.graph, alpha=alpha, weight='weight')
        self.centrality_metrics['pagerank'] = centrality
        logger.info("PageRank calculé")
        return centrality

    def calculate_all_centralities(self) -> Dict[str, Dict[str, float]]:
        """
        Calcule toutes les métriques de centralité.

        Returns:
            Dictionnaire avec toutes les centralités
        """
        logger.info("Calcul de toutes les métriques de centralité...")

        self.calculate_degree_centrality()
        self.calculate_betweenness_centrality()
        self.calculate_closeness_centrality()
        self.calculate_eigenvector_centrality()
        self.calculate_pagerank()

        logger.info(f"Métriques calculées : {list(self.centrality_metrics.keys())}")

        return self.centrality_metrics

    def get_centrality_dataframe(self) -> pd.DataFrame:
        """
        Retourne un DataFrame avec toutes les centralités.

        Returns:
            DataFrame avec colonnes pour chaque métrique
        """
        if not self.centrality_metrics:
            self.calculate_all_centralities()

        df = pd.DataFrame(self.centrality_metrics)
        df = df.reset_index()
        df.columns = ['client_id'] + list(self.centrality_metrics.keys())

        # Alias columns attendues par la demo
        df['node_id'] = df['client_id']
        if 'degree' in df.columns:
            df['centrality_degree'] = df['degree']
        if 'betweenness' in df.columns:
            df['centrality_betweenness'] = df['betweenness']
        if 'closeness' in df.columns:
            df['centrality_closeness'] = df['closeness']
        if 'eigenvector' in df.columns:
            df['centrality_eigenvector'] = df['eigenvector']
        if 'pagerank' in df.columns:
            df['centrality_pagerank'] = df['pagerank']

        return df.sort_values('pagerank', ascending=False)

    def calculate_network_statistics(self) -> Dict[str, float]:
        """
        Calcule les statistiques globales du réseau.

        Returns:
            Dictionnaire avec statistiques du réseau
        """
        logger.info("Calcul des statistiques du réseau...")

        stats = {
            'n_nodes': self.graph.number_of_nodes(),
            'n_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'average_clustering': nx.average_clustering(self.graph),
        }

        # Alias keys attendues par la demo
        stats['nb_nodes'] = stats['n_nodes']
        stats['nb_edges'] = stats['n_edges']
        stats['avg_clustering'] = stats['average_clustering']

        # Calcul du diamètre si le graphe est connexe
        if nx.is_connected(self.graph):
            stats['diameter'] = nx.diameter(self.graph)
            stats['average_shortest_path'] = nx.average_shortest_path_length(self.graph)
        else:
            # Pour les graphes non-connexes
            largest_cc = max(nx.connected_components(self.graph), key=len)
            subgraph = self.graph.subgraph(largest_cc)
            stats['diameter'] = nx.diameter(subgraph)
            stats['average_shortest_path'] = nx.average_shortest_path_length(subgraph)
            stats['n_connected_components'] = nx.number_connected_components(self.graph)

        self.network_stats = stats
        logger.info(f"Statistiques du réseau : {stats}")

        return stats

    def get_network_statistics(self) -> Dict[str, float]:
        """
        Alias pour conserver l'API attendue par la demo.
        """
        return self.calculate_network_statistics()

    def detect_communities(self, method: str = 'louvain') -> Dict[int, set]:
        """
        Détecte les communautés dans le réseau.

        Args:
            method: Méthode de détection ('louvain', 'greedy', 'label_propagation')

        Returns:
            Dictionnaire {community_id: set(nodes)}
        """
        logger.info(f"Détection de communautés avec la méthode '{method}'...")

        if method == 'louvain':
            try:
                from networkx.algorithms import community
                communities = community.greedy_modularity_communities(self.graph)
                communities_dict = {i: set(c) for i, c in enumerate(communities)}
            except Exception as e:
                logger.warning(f"Erreur Louvain: {e}, utilisation de greedy")
                communities_dict = self._detect_communities_greedy()

        elif method == 'greedy':
            communities_dict = self._detect_communities_greedy()

        elif method == 'label_propagation':
            communities_dict = self._detect_communities_label_propagation()

        else:
            logger.warning(f"Méthode '{method}' inconnue, utilisation de greedy")
            communities_dict = self._detect_communities_greedy()

        logger.info(f"Communautés détectées : {len(communities_dict)}")
        return communities_dict

    def _detect_communities_greedy(self) -> Dict[int, set]:
        """Détection de communautés avec l'algorithme greedy."""
        try:
            from networkx.algorithms import community
            communities = community.greedy_modularity_communities(self.graph)
            return {i: set(c) for i, c in enumerate(communities)}
        except Exception as e:
            logger.error(f"Erreur détection greedy: {e}")
            return {0: set(self.graph.nodes())}

    def _detect_communities_label_propagation(self) -> Dict[int, set]:
        """Détection de communautés avec label propagation."""
        try:
            from networkx.algorithms import community
            communities = community.label_propagation_communities(self.graph)
            return {i: set(c) for i, c in enumerate(communities)}
        except Exception as e:
            logger.error(f"Erreur label propagation: {e}")
            return {0: set(self.graph.nodes())}

    def get_top_nodes(self, metric: str = 'pagerank', top_n: int = 10) -> pd.DataFrame:
        """
        Retourne les N nœuds les plus importants selon une métrique.

        Args:
            metric: Métrique de centralité à utiliser
            top_n: Nombre de nœuds à retourner

        Returns:
            DataFrame avec les top nœuds
        """
        if metric not in self.centrality_metrics:
            logger.warning(f"Métrique '{metric}' non trouvée, calcul de toutes les métriques")
            self.calculate_all_centralities()

        centrality = self.centrality_metrics[metric]
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        df = pd.DataFrame(sorted_nodes, columns=['client_id', metric])
        return df.head(top_n)

    def get_neighbors(self, node: str) -> set:
        """
        Retourne les voisins directs d'un nœud.

        Args:
            node: ID du nœud

        Returns:
            Ensemble des voisins
        """
        if node in self.graph:
            return set(self.graph.neighbors(node))
        return set()

    def get_node_degree(self, node: str) -> int:
        """
        Retourne le degré d'un nœud.

        Args:
            node: ID du nœud

        Returns:
            Degré du nœud
        """
        return self.graph.degree(node, weight='weight')
