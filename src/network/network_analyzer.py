"""
Module d'analyse de réseau — Hôtel Aurore Paris Gare de Lyon.

Construit un graphe de similarité entre clients/séjours à partir
des caractéristiques de réservation et calcule les métriques réseau.

Architecture :
  - build_similarity_graph()   : graphe pondéré par similarité de profil
  - compute_network_metrics()  : centralités (degree, betweenness, pagerank, eigenvector)
  - detect_communities()       : Louvain / greedy modularity / label propagation
  - export_network_results()   : DataFrame enrichi prêt pour le modèle et l'UI
  - NetworkAnalyzer            : classe principale (conserve l'ancienne API)
"""

import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import networkx as nx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Colonnes utilisées pour calculer la similarité (par ordre de priorité)
# ---------------------------------------------------------------------------
_SIMILARITY_FEATURES = [
    "channel_group",   # canal de distribution
    "pays",            # pays du client
    "room_segment",    # type de chambre
    "amount_bucket",   # segment de prix
    "langue",          # langue
    "arrival_month",   # mois d'arrivée (bucket saisonnier)
    "stay_length",     # durée de séjour (bucket)
]

# Poids accordé à chaque attribut dans le score de similarité
_FEATURE_WEIGHTS = {
    "channel_group":  2.0,
    "pays":           1.5,
    "room_segment":   1.5,
    "amount_bucket":  1.0,
    "langue":         1.0,
    "arrival_month":  0.5,
    "stay_length":    0.5,
}

_TOTAL_WEIGHT = sum(_FEATURE_WEIGHTS.values())


# ===========================================================================
# Fonctions utilitaires
# ===========================================================================

def _bucket_stay(length: float) -> str:
    """Discrétise la durée de séjour en catégories."""
    try:
        l = int(length)
    except (ValueError, TypeError):
        return "unknown"
    if l <= 1:
        return "1n"
    if l <= 3:
        return "2-3n"
    if l <= 7:
        return "4-7n"
    return "8n+"


def _bucket_month(month: float) -> str:
    """Regroupe les mois en saisons."""
    try:
        m = int(month)
    except (ValueError, TypeError):
        return "unknown"
    if m in (12, 1, 2):
        return "hiver"
    if m in (3, 4, 5):
        return "printemps"
    if m in (6, 7, 8):
        return "ete"
    return "automne"


def _prepare_profile_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare un DataFrame de profils client normalisés pour le calcul de similarité.
    - Sélectionne les colonnes pertinentes
    - Discrétise les variables continues (stay_length, arrival_month)
    - Remplit les NaN par 'unknown'
    - Déduplique par client_id (on prend le profil le plus récent)
    """
    df = df.copy()

    # Discrétiser si les colonnes numériques sont présentes
    if "stay_length" in df.columns:
        df["stay_length"] = df["stay_length"].apply(_bucket_stay)
    if "arrival_month" in df.columns:
        df["arrival_month"] = df["arrival_month"].apply(_bucket_month)

    # Sélectionner les features disponibles
    avail = [f for f in _SIMILARITY_FEATURES if f in df.columns]
    if not avail:
        raise ValueError(
            "Aucune colonne de similarité disponible. "
            f"Colonnes attendues : {_SIMILARITY_FEATURES}"
        )

    cols = ["client_id"] + avail
    profile = df[cols].copy()

    # Remplir les manquants
    for col in avail:
        profile[col] = profile[col].fillna("unknown").astype(str).str.lower().str.strip()

    # Dédupliquer (garder la dernière ligne par client)
    profile = profile.drop_duplicates(subset="client_id", keep="last")
    profile = profile.set_index("client_id")

    logger.info(f"Profils préparés : {len(profile)} clients, {len(avail)} attributs")
    return profile, avail


# ===========================================================================
# Fonctions publiques
# ===========================================================================

def compute_similarity_weight(row_a: pd.Series, row_b: pd.Series,
                               features: List[str]) -> float:
    """
    Calcule le poids de similarité entre deux profils client.

    Chaque attribut partagé ajoute son poids. Le score est normalisé sur [0, 1].

    Args:
        row_a : série de profil client A
        row_b : série de profil client B
        features : liste des features à comparer

    Returns:
        Score de similarité entre 0 et 1.
    """
    score = 0.0
    total = sum(_FEATURE_WEIGHTS.get(f, 1.0) for f in features)
    for feat in features:
        a, b = str(row_a.get(feat, "unknown")), str(row_b.get(feat, "unknown"))
        if a != "unknown" and b != "unknown" and a == b:
            score += _FEATURE_WEIGHTS.get(feat, 1.0)
    return round(score / total, 4) if total > 0 else 0.0


def build_similarity_graph(
    df: pd.DataFrame,
    min_similarity: float = 0.3,
    max_nodes: int = 2000,
    sample_seed: int = 42,
) -> Tuple[nx.Graph, pd.DataFrame]:
    """
    Construit un graphe de similarité entre clients hôteliers.

    Deux nœuds sont reliés si leur score de similarité dépasse min_similarity.
    Le poids de l'arête est le score de similarité.

    Optimisation : la similarité est calculée en groupant les nœuds partageant
    la même valeur pour chaque attribut (O(n·k) au lieu de O(n²)).

    Args:
        df             : DataFrame final avec colonnes client_id + features
        min_similarity : Seuil minimal de similarité pour créer une arête
        max_nodes      : Nombre maximal de nœuds (sous-échantillonnage si dépassé)
        sample_seed    : Graine de l'échantillonnage

    Returns:
        Tuple (graphe NetworkX, DataFrame de profils)
    """
    logger.info(f"Construction du graphe de similarité (seuil={min_similarity})…")

    profile_df, avail_features = _prepare_profile_df(df)

    # Sous-échantillonnage si trop de clients
    if len(profile_df) > max_nodes:
        logger.warning(
            f"Trop de clients ({len(profile_df)}) — sous-échantillonnage à {max_nodes}"
        )
        profile_df = profile_df.sample(n=max_nodes, random_state=sample_seed)

    nodes = profile_df.index.tolist()
    n = len(nodes)
    logger.info(f"Calcul des similarités pour {n} clients…")

    G = nx.Graph()
    G.add_nodes_from(nodes)

    # ── Calcul optimisé via accumulation de scores par paires ──────────────
    # Pour chaque attribut : trouver tous les couples (i, j) qui partagent la
    # même valeur, accumuler le poids correspondant.
    # Complexité : O(n · k · b) où b = taille moyenne des groupes << n.
    from collections import defaultdict
    pair_scores: dict = defaultdict(float)
    total_weight = sum(_FEATURE_WEIGHTS.get(f, 1.0) for f in avail_features)

    for feat in avail_features:
        w = _FEATURE_WEIGHTS.get(feat, 1.0) / total_weight
        # Grouper les indices par valeur de l'attribut
        groups: dict = defaultdict(list)
        for node in nodes:
            val = profile_df.at[node, feat]
            if val != "unknown":
                groups[val].append(node)
        # Pour chaque groupe, tous les couples partagent cet attribut
        for members in groups.values():
            for a in range(len(members)):
                for b in range(a + 1, len(members)):
                    key = (members[a], members[b]) if members[a] < members[b] else (members[b], members[a])
                    pair_scores[key] += w

    # Construire les arêtes dont le score dépasse le seuil
    edges_added = 0
    for (u, v), sim in pair_scores.items():
        if sim >= min_similarity:
            G.add_edge(u, v, weight=round(sim, 4))
            edges_added += 1

    logger.info(
        f"Graphe construit : {G.number_of_nodes()} nœuds, "
        f"{G.number_of_edges()} arêtes (seuil={min_similarity})"
    )
    return G, profile_df


def compute_network_metrics(G: nx.Graph) -> pd.DataFrame:
    """
    Calcule les métriques de centralité réseau.

    Métriques calculées :
      - weighted_degree (force / strength)
      - betweenness_centrality
      - pagerank
      - eigenvector_centrality
      - closeness_centrality (optionnelle)

    Args:
        G : graphe NetworkX (peut être non-connexe)

    Returns:
        DataFrame indexé par client_id avec une colonne par métrique.
    """
    logger.info(f"Calcul des métriques réseau pour {G.number_of_nodes()} nœuds…")

    if G.number_of_nodes() == 0:
        logger.warning("Graphe vide — aucune métrique calculable.")
        return pd.DataFrame(
            columns=[
                "client_id",
                "weighted_degree",
                "betweenness",
                "pagerank",
                "eigenvector",
                "closeness",
            ]
        )

    results: Dict[str, Dict] = {}

    # 1. Weighted degree (strength)
    wdeg = dict(G.degree(weight="weight"))
    results["weighted_degree"] = wdeg
    logger.debug("weighted_degree calculé")

    # 2. Betweenness centrality
    try:
        results["betweenness"] = nx.betweenness_centrality(G, weight="weight", normalized=True)
        logger.debug("betweenness calculé")
    except Exception as e:
        logger.warning(f"betweenness échoué : {e}")
        results["betweenness"] = {n: 0.0 for n in G.nodes()}

    # 3. PageRank
    try:
        results["pagerank"] = nx.pagerank(G, alpha=0.85, weight="weight", max_iter=200)
        logger.debug("pagerank calculé")
    except Exception as e:
        logger.warning(f"pagerank échoué : {e}")
        results["pagerank"] = {n: 1.0 / G.number_of_nodes() for n in G.nodes()}

    # 4. Eigenvector centrality (robuste aux graphes peu denses)
    try:
        results["eigenvector"] = nx.eigenvector_centrality(
            G, weight="weight", max_iter=500, tol=1e-4
        )
        logger.debug("eigenvector calculé")
    except Exception as e:
        logger.warning(f"eigenvector échoué (graphe trop sparse ?) : {e} — fallback degree")
        results["eigenvector"] = nx.degree_centrality(G)

    # 5. Closeness (optionnelle — sur le plus grand composant connexe)
    try:
        if nx.is_connected(G):
            results["closeness"] = nx.closeness_centrality(G)
        else:
            # Sur le plus grand composant
            lcc = G.subgraph(max(nx.connected_components(G), key=len))
            cl = nx.closeness_centrality(lcc)
            results["closeness"] = {n: cl.get(n, 0.0) for n in G.nodes()}
        logger.debug("closeness calculé")
    except Exception as e:
        logger.warning(f"closeness échoué : {e}")
        results["closeness"] = {n: 0.0 for n in G.nodes()}

    df_metrics = pd.DataFrame(results)
    df_metrics.index.name = "client_id"
    df_metrics = df_metrics.reset_index()

    logger.info(f"Métriques calculées : {list(results.keys())}")
    return df_metrics


def detect_communities(G: nx.Graph, method: str = "greedy") -> Dict[str, int]:
    """
    Détecte les communautés dans le graphe.

    Args:
        G      : graphe NetworkX
        method : 'greedy' | 'louvain' | 'label_propagation'

    Returns:
        Dictionnaire {client_id: community_id}.
    """
    logger.info(f"Détection de communautés (méthode={method})…")

    if G.number_of_nodes() == 0:
        logger.warning("Graphe vide — aucune communauté à détecter.")
        return {}

    from networkx.algorithms import community as nx_comm

    try:
        if method == "louvain":
            try:
                import community as python_louvain  # python-louvain package
                partition = python_louvain.best_partition(G, weight="weight")
                logger.info(f"Louvain : {len(set(partition.values()))} communautés")
                return partition
            except ImportError:
                logger.warning("python-louvain non installé — fallback greedy")
                method = "greedy"

        if method == "greedy":
            comms = nx_comm.greedy_modularity_communities(G, weight="weight")
        elif method == "label_propagation":
            comms = nx_comm.label_propagation_communities(G)
        else:
            logger.warning(f"Méthode '{method}' inconnue — fallback greedy")
            comms = nx_comm.greedy_modularity_communities(G, weight="weight")

        partition = {}
        for cid, comm in enumerate(comms):
            for node in comm:
                partition[node] = cid

        logger.info(f"Communautés détectées : {len(comms)}")
        return partition

    except Exception as e:
        logger.error(f"Détection de communautés échouée : {e}")
        return {n: 0 for n in G.nodes()}


def export_network_results(
    df_original: pd.DataFrame,
    df_metrics: pd.DataFrame,
    communities: Dict[str, int],
) -> pd.DataFrame:
    """
    Fusionne les données originales avec les métriques réseau et les communautés.

    Args:
        df_original : dataset principal (avec client_id)
        df_metrics  : DataFrame des métriques réseau
        communities : dictionnaire {client_id: community_id}

    Returns:
        DataFrame enrichi.
    """
    logger.info("Fusion des résultats réseau avec le dataset principal…")

    df_comm = pd.DataFrame(
        list(communities.items()), columns=["client_id", "community_id"]
    )

    df_out = df_original.copy()
    df_out = df_out.merge(df_metrics, on="client_id", how="left")
    df_out = df_out.merge(df_comm, on="client_id", how="left")

    # Remplir les NaN (clients isolés — pas dans le graphe)
    for col in ["weighted_degree", "betweenness", "pagerank", "eigenvector", "closeness"]:
        if col in df_out.columns:
            df_out[col] = df_out[col].fillna(0.0)
    if "community_id" in df_out.columns:
        df_out["community_id"] = df_out["community_id"].fillna(-1).astype(int)

    logger.info(f"Dataset enrichi : {df_out.shape[0]} lignes, {df_out.shape[1]} colonnes")
    return df_out


# ===========================================================================
# Classe NetworkAnalyzer — conservée pour compatibilité
# ===========================================================================

class NetworkAnalyzer:
    """
    Classe principale d'analyse réseau hôtelière.

    Orchestre la construction du graphe de similarité, le calcul des
    métriques de centralité et la détection de communautés.

    Conserve l'ancienne API (build_network, calculate_all_centralities, …)
    tout en exposant les nouvelles fonctions.
    """

    def __init__(
        self,
        graph: Optional[nx.Graph] = None,
        directed: bool = False,
        weighted: bool = True,
    ):
        self.directed = directed
        self.weighted = weighted
        default_graph = nx.DiGraph() if directed else nx.Graph()
        self.graph: nx.Graph = graph or default_graph
        self.centrality_metrics: Dict[str, Dict] = {}
        self.network_stats: Dict = {}
        self._communities: Dict[str, int] = {}
        self._profile_df: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Nouvelle API : graphe de similarité
    # ------------------------------------------------------------------

    def build_similarity_graph(
        self,
        df: pd.DataFrame,
        min_similarity: float = 0.3,
        max_nodes: int = 2000,
    ) -> nx.Graph:
        """Construit le graphe de similarité à partir du dataset hôtelier."""
        self.graph, self._profile_df = build_similarity_graph(
            df, min_similarity=min_similarity, max_nodes=max_nodes
        )
        return self.graph

    def compute_network_metrics(self) -> pd.DataFrame:
        """Calcule et stocke les métriques réseau."""
        df_metrics = compute_network_metrics(self.graph)
        # Stocker dans le format attendu par l'ancienne API
        for col in df_metrics.columns:
            if col != "client_id":
                self.centrality_metrics[col] = dict(
                    zip(df_metrics["client_id"], df_metrics[col])
                )
        return df_metrics

    def detect_communities(self, method: str = "greedy") -> Dict[str, int]:
        """Détecte les communautés et les stocke."""
        self._communities = detect_communities(self.graph, method=method)
        return self._communities

    def export_network_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """Retourne le dataset enrichi avec métriques et communautés."""
        df_metrics = self.get_centrality_dataframe()
        keep_cols = [
            c for c in df_metrics.columns
            if c in {
                "client_id",
                "weighted_degree",
                "degree",
                "betweenness",
                "closeness",
                "eigenvector",
                "pagerank",
            }
        ]
        df_metrics = df_metrics[keep_cols].copy()
        return export_network_results(df, df_metrics, self._communities)

    # ------------------------------------------------------------------
    # Ancienne API — conservée pour compatibilité avec les tests et app.py
    # ------------------------------------------------------------------

    def build_network(
        self,
        df_interactions: pd.DataFrame,
        weight_col: str = "weight",
        source_col: str = "client_source",
        target_col: str = "client_target",
    ) -> nx.Graph:
        """
        Construit un graphe depuis un DataFrame d'interactions explicites.
        Conservé pour la rétrocompatibilité / mode démo.
        """
        logger.info(f"Construction du graphe depuis {len(df_interactions)} interactions…")
        self.graph = nx.DiGraph() if self.directed else nx.Graph()
        for _, row in df_interactions.iterrows():
            src = row.get(source_col)
            tgt = row.get(target_col)
            w = float(row.get(weight_col, 1.0))
            if pd.notna(src) and pd.notna(tgt) and src != tgt:
                self.graph.add_edge(src, tgt, weight=w)
        logger.info(
            f"Graphe : {self.graph.number_of_nodes()} nœuds, "
            f"{self.graph.number_of_edges()} arêtes"
        )
        return self.graph

    def calculate_degree_centrality(self) -> Dict[str, float]:
        c = nx.degree_centrality(self.graph)
        self.centrality_metrics["degree"] = c
        return c

    def calculate_betweenness_centrality(self) -> Dict[str, float]:
        try:
            c = nx.betweenness_centrality(self.graph, weight="weight")
        except Exception:
            c = nx.betweenness_centrality(self.graph)
        self.centrality_metrics["betweenness"] = c
        return c

    def calculate_closeness_centrality(self) -> Dict[str, float]:
        c = nx.closeness_centrality(self.graph)
        self.centrality_metrics["closeness"] = c
        return c

    def calculate_eigenvector_centrality(self, max_iter: int = 500) -> Dict[str, float]:
        try:
            c = nx.eigenvector_centrality(self.graph, weight="weight", max_iter=max_iter)
        except Exception as e:
            logger.warning(f"Eigenvector échoué ({e}) — fallback degree")
            c = nx.degree_centrality(self.graph)
        self.centrality_metrics["eigenvector"] = c
        return c

    def calculate_pagerank(self, alpha: float = 0.85) -> Dict[str, float]:
        c = nx.pagerank(self.graph, alpha=alpha, weight="weight", max_iter=200)
        self.centrality_metrics["pagerank"] = c
        return c

    def calculate_all_centralities(self) -> Dict[str, Dict[str, float]]:
        """Calcule toutes les métriques de centralité disponibles."""
        logger.info("Calcul de toutes les métriques de centralité…")
        self.calculate_degree_centrality()
        self.calculate_betweenness_centrality()
        self.calculate_closeness_centrality()
        self.calculate_eigenvector_centrality()
        self.calculate_pagerank()

        # Weighted degree (strength) si poids disponibles
        wdeg = dict(self.graph.degree(weight="weight"))
        self.centrality_metrics["weighted_degree"] = wdeg

        logger.info(f"Métriques calculées : {list(self.centrality_metrics.keys())}")
        return self.centrality_metrics

    def get_centrality_dataframe(self) -> pd.DataFrame:
        """Retourne un DataFrame avec toutes les centralités calculées."""
        if not self.centrality_metrics:
            self.calculate_all_centralities()

        df = pd.DataFrame(self.centrality_metrics)
        df.index.name = "client_id"
        df = df.reset_index()

        # Alias attendus par l'ancienne API
        for metric in ["degree", "betweenness", "closeness", "eigenvector", "pagerank"]:
            if metric in df.columns:
                df[f"centrality_{metric}"] = df[metric]

        df["node_id"] = df["client_id"]

        # Trier par pagerank si disponible
        sort_col = "pagerank" if "pagerank" in df.columns else df.columns[1]
        return df.sort_values(sort_col, ascending=False).reset_index(drop=True)

    def calculate_network_statistics(self) -> Dict:
        """Calcule les statistiques globales du réseau."""
        logger.info("Calcul des statistiques du réseau…")
        G = self.graph

        stats = {
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "density": round(nx.density(G), 6),
            "is_connected": nx.is_connected(G) if G.number_of_nodes() > 0 else False,
            "n_connected_components": nx.number_connected_components(G),
        }
        stats["nb_nodes"] = stats["n_nodes"]
        stats["nb_edges"] = stats["n_edges"]

        try:
            stats["average_clustering"] = round(nx.average_clustering(G, weight="weight"), 4)
            stats["avg_clustering"] = stats["average_clustering"]
        except Exception:
            stats["average_clustering"] = 0.0
            stats["avg_clustering"] = 0.0

        # Diamètre et chemin moyen : seulement sur petits graphes (< 500 nœuds)
        # pour éviter les calculs O(n²) prohibitifs sur les graphes denses
        if G.number_of_nodes() > 0 and G.number_of_nodes() <= 500:
            try:
                if stats["is_connected"]:
                    stats["diameter"] = nx.diameter(G)
                    stats["average_shortest_path"] = round(
                        nx.average_shortest_path_length(G), 4
                    )
                else:
                    lcc = G.subgraph(max(nx.connected_components(G), key=len))
                    if lcc.number_of_nodes() <= 500:
                        stats["diameter"] = nx.diameter(lcc)
                        stats["average_shortest_path"] = round(
                            nx.average_shortest_path_length(lcc), 4
                        )
            except Exception as e:
                logger.warning(f"Diamètre / chemin moyen non calculable : {e}")
        else:
            logger.info(
                f"Graphe trop grand ({G.number_of_nodes()} nœuds) — "
                "diamètre/chemin moyen ignorés pour des raisons de performance."
            )

        # Modularité si des communautés ont été détectées
        if self._communities:
            try:
                from networkx.algorithms.community.quality import modularity
                comm_sets = defaultdict(set)
                for node, cid in self._communities.items():
                    comm_sets[cid].add(node)
                stats["modularity"] = round(
                    modularity(G, list(comm_sets.values()), weight="weight"), 4
                )
            except Exception as e:
                logger.warning(f"Modularité non calculable : {e}")

        self.network_stats = stats
        logger.info(f"Stats réseau : {stats}")
        return stats

    def get_network_statistics(self) -> Dict:
        """Alias pour compatibilité."""
        return self.calculate_network_statistics()

    def get_top_nodes(self, metric: str = "pagerank", top_n: int = 10) -> pd.DataFrame:
        """Retourne les N clients les plus centraux selon une métrique."""
        if metric not in self.centrality_metrics:
            self.calculate_all_centralities()
        centrality = self.centrality_metrics.get(metric, {})
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return pd.DataFrame(sorted_nodes[:top_n], columns=["client_id", metric])

    def get_neighbors(self, node: str) -> set:
        if node in self.graph:
            return set(self.graph.neighbors(node))
        return set()

    def get_node_degree(self, node: str) -> float:
        return float(self.graph.degree(node, weight="weight"))
