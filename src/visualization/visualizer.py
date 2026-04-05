"""
Module de visualisation — Hôtel Aurore Paris Gare de Lyon.

Graphiques produits :
  - Réseau de similarité avec communautés colorées
  - Distribution des métriques de centralité
  - Satisfaction moyenne par communauté
  - Satisfaction par canal de distribution
  - Satisfaction par type de chambre
  - Revenu moyen par communauté
  - Top profils centraux
  - Importance des features du modèle
  - Comparaison multi-modèles
  - Matrices de corrélation

Toutes les fonctions ignorent automatiquement les colonnes non numériques
là où un calcul numérique est attendu.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import matplotlib
matplotlib.use("Agg")          # backend sans display (compatible Streamlit)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import networkx as nx
import seaborn as sns

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Style global
# ---------------------------------------------------------------------------
sns.set_style("whitegrid")
plt.rcParams.update({
    "figure.figsize": (12, 7),
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

_PALETTE = sns.color_palette("tab10")

# Couleurs par canal
_CHANNEL_COLORS = {
    "booking":       "#003580",
    "direct":        "#2ecc71",
    "expedia_group": "#ff6600",
    "metasearch":    "#9b59b6",
    "airbnb":        "#e74c3c",
    "gds":           "#1abc9c",
    "other_ota":     "#95a5a6",
    "unknown":       "#bdc3c7",
}


def _close(fig: plt.Figure) -> None:
    """Ferme proprement une figure pour libérer la mémoire."""
    plt.close(fig)


def _save(fig: plt.Figure, path: Path, filename: str) -> Path:
    """Sauvegarde une figure et retourne le chemin."""
    path.mkdir(parents=True, exist_ok=True)
    fp = path / filename
    fig.savefig(fp, dpi=150, bbox_inches="tight")
    logger.info(f"Figure sauvegardée : {fp}")
    return fp


# ===========================================================================
# Classe principale
# ===========================================================================

class NetworkVisualizer:
    """
    Visualiseur principal pour les données de l'Hôtel Aurore Paris.
    """

    def __init__(self, output_dir: str = "outputs/figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Répertoire de sortie : {self.output_dir}")

    # ------------------------------------------------------------------
    # 1. Réseau avec communautés
    # ------------------------------------------------------------------

    def plot_network(
        self,
        graph: nx.Graph,
        centrality_metric: Optional[Dict] = None,
        communities: Optional[Dict[str, int]] = None,
        title: str = "Réseau de similarité clients",
        figsize: Tuple[int, int] = (14, 10),
        save: bool = True,
        max_nodes_display: int = 500,
    ) -> plt.Figure:
        """
        Visualise le graphe du réseau.

        Si communities est fourni, les nœuds sont colorés par communauté.
        Sinon, la couleur reflète la centralité.

        Args:
            graph              : Graphe NetworkX
            centrality_metric  : Dict {node: valeur} pour la taille des nœuds
            communities        : Dict {node: community_id} pour la couleur
            title              : Titre
            figsize            : Taille de la figure
            save               : Sauvegarder l'image
            max_nodes_display  : Sous-échantillonnage si graphe trop grand

        Returns:
            Figure matplotlib
        """
        logger.info(f"Visualisation du réseau ({graph.number_of_nodes()} nœuds)…")

        # Sous-échantillonnage pour la lisibilité
        G = graph
        if G.number_of_nodes() > max_nodes_display:
            nodes_sample = list(G.nodes())[:max_nodes_display]
            G = G.subgraph(nodes_sample)
            logger.info(f"Sous-graphe affiché : {max_nodes_display} nœuds")

        fig, ax = plt.subplots(figsize=figsize)

        if G.number_of_nodes() == 0:
            ax.text(0.5, 0.5, "Graphe vide", ha="center", va="center", fontsize=14)
            ax.axis("off")
            return fig

        # Layout
        k = max(0.3, 2.0 / np.sqrt(G.number_of_nodes()))
        pos = nx.spring_layout(G, k=k, iterations=30, seed=42)

        # Couleurs par communauté
        if communities:
            comm_ids = sorted(set(communities.values()))
            cmap = cm.get_cmap("tab20", max(len(comm_ids), 1))
            node_colors = [
                cmap(communities.get(n, 0) % 20) for n in G.nodes()
            ]
            # Légende communautés (max 10)
            patches = [
                mpatches.Patch(color=cmap(c % 20), label=f"Comm. {c}")
                for c in comm_ids[:10]
            ]
            ax.legend(handles=patches, loc="upper left", fontsize=8,
                      title="Communautés", title_fontsize=9)
        elif centrality_metric:
            vals = np.array([centrality_metric.get(n, 0.0) for n in G.nodes()])
            if vals.max() > 0:
                vals = vals / vals.max()
            node_colors = [plt.cm.YlOrRd(v) for v in vals]
        else:
            node_colors = "steelblue"

        # Tailles proportionnelles à la centralité
        if centrality_metric:
            sizes = np.array([centrality_metric.get(n, 0.0) for n in G.nodes()])
            mx = sizes.max() if sizes.max() > 0 else 1
            sizes = 50 + 300 * sizes / mx
        else:
            sizes = 80

        # Épaisseur des arêtes proportionnelle au poids
        edges = G.edges(data=True)
        weights = np.array([d.get("weight", 0.5) for _, _, d in edges])
        if len(weights) > 0 and weights.max() > 0:
            weights = 0.3 + 1.5 * weights / weights.max()
        else:
            weights = [0.5] * G.number_of_edges()

        nx.draw_networkx_edges(G, pos, alpha=0.15, width=weights, ax=ax,
                               edge_color="gray")
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=sizes,
                               alpha=0.85, ax=ax)

        if G.number_of_nodes() <= 30:
            nx.draw_networkx_labels(G, pos, font_size=7, ax=ax)

        ax.set_title(title, fontweight="bold", pad=15)
        ax.axis("off")
        plt.tight_layout()

        if save:
            _save(fig, self.output_dir, "network_communities.png")
        return fig

    # ------------------------------------------------------------------
    # 2. Distribution des centralités
    # ------------------------------------------------------------------

    def plot_centrality_distribution(
        self,
        df_centrality: pd.DataFrame,
        figsize: Tuple[int, int] = (14, 9),
        save: bool = True,
    ) -> plt.Figure:
        """
        Affiche la distribution des métriques de centralité disponibles.
        """
        # Colonnes numériques (exclure client_id et node_id)
        metrics = [
            c for c in df_centrality.select_dtypes(include=[np.number]).columns
            if c not in ("client_id", "node_id", "community_id")
        ]
        if not metrics:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Aucune métrique numérique", ha="center")
            return fig

        n_cols = min(3, len(metrics))
        n_rows = int(np.ceil(len(metrics) / n_cols))
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = np.array(axes).flatten()

        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            data = df_centrality[metric].dropna()
            ax.hist(data, bins=30, color=_PALETTE[idx % 10], alpha=0.75, edgecolor="white")
            ax.axvline(data.mean(), color="red", lw=1.5, ls="--", label=f"Moy. {data.mean():.3f}")
            ax.set_xlabel(metric)
            ax.set_ylabel("Fréquence")
            ax.set_title(f"Distribution — {metric}", fontweight="bold")
            ax.legend(fontsize=8)

        for idx in range(len(metrics), len(axes)):
            axes[idx].axis("off")

        plt.suptitle("Distribution des métriques de centralité", fontsize=14, fontweight="bold", y=1.01)
        plt.tight_layout()

        if save:
            _save(fig, self.output_dir, "centrality_distribution.png")
        return fig

    # ------------------------------------------------------------------
    # 3. Satisfaction moyenne par communauté
    # ------------------------------------------------------------------

    def plot_satisfaction_by_community(
        self,
        df: pd.DataFrame,
        score_col: str = "review_score",
        comm_col: str = "community_id",
        figsize: Tuple[int, int] = (12, 6),
        save: bool = True,
    ) -> plt.Figure:
        """
        Boxplot + barre de la satisfaction moyenne par communauté.
        """
        for col in [score_col, comm_col]:
            if col not in df.columns:
                logger.warning(f"Colonne '{col}' absente — graphique ignoré.")
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Colonne '{col}' absente", ha="center")
                return fig

        df_valid = df[[score_col, comm_col]].dropna()
        df_valid[comm_col] = df_valid[comm_col].astype(int)

        top_comms = (
            df_valid[comm_col]
            .value_counts()
            .head(12)
            .index.tolist()
        )
        df_valid = df_valid[df_valid[comm_col].isin(top_comms)]

        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Boxplot
        ax = axes[0]
        groups = [
            df_valid[df_valid[comm_col] == c][score_col].values
            for c in sorted(top_comms)
        ]
        ax.boxplot(groups, labels=[f"C{c}" for c in sorted(top_comms)],
                   patch_artist=True,
                   boxprops=dict(facecolor="steelblue", alpha=0.6))
        ax.set_xlabel("Communauté")
        ax.set_ylabel("Note d'avis (/10)")
        ax.set_title("Distribution de la satisfaction par communauté", fontweight="bold")
        ax.grid(True, alpha=0.3)

        # Barre : note moyenne
        ax2 = axes[1]
        means = df_valid.groupby(comm_col)[score_col].mean().sort_values(ascending=False).head(12)
        colors = [_PALETTE[i % 10] for i in range(len(means))]
        bars = ax2.bar([f"C{c}" for c in means.index], means.values, color=colors,
                       edgecolor="white")
        ax2.axhline(df_valid[score_col].mean(), color="red", lw=1.5, ls="--",
                    label=f"Moy. globale {df_valid[score_col].mean():.2f}")
        for bar, val in zip(bars, means.values):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                     f"{val:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax2.set_xlabel("Communauté")
        ax2.set_ylabel("Note moyenne (/10)")
        ax2.set_title("Note moyenne par communauté", fontweight="bold")
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, "satisfaction_by_community.png")
        return fig

    # ------------------------------------------------------------------
    # 4. Satisfaction par canal
    # ------------------------------------------------------------------

    def plot_satisfaction_by_channel(
        self,
        df: pd.DataFrame,
        score_col: str = "review_score",
        channel_col: str = "channel_group",
        figsize: Tuple[int, int] = (12, 5),
        save: bool = True,
    ) -> plt.Figure:
        """
        Barre horizontale : note moyenne par canal avec comptage.
        """
        for col in [score_col, channel_col]:
            if col not in df.columns:
                logger.warning(f"Colonne '{col}' absente.")
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Colonne '{col}' absente", ha="center")
                return fig

        df_valid = df[[score_col, channel_col]].dropna(subset=[score_col])
        stats = (
            df_valid.groupby(channel_col)[score_col]
            .agg(["mean", "count", "std"])
            .sort_values("mean", ascending=True)
        )

        fig, ax = plt.subplots(figsize=figsize)
        colors = [_CHANNEL_COLORS.get(c, "#95a5a6") for c in stats.index]
        bars = ax.barh(stats.index, stats["mean"], color=colors, edgecolor="white",
                       xerr=stats["std"], capsize=4, alpha=0.85)

        # Annoter avec le nombre d'avis
        for bar, (_, row) in zip(bars, stats.iterrows()):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                    f"n={int(row['count'])}", va="center", fontsize=9)

        ax.axvline(df_valid[score_col].mean(), color="red", lw=1.5, ls="--",
                   label=f"Moy. {df_valid[score_col].mean():.2f}")
        ax.set_xlabel("Note moyenne (/10)")
        ax.set_title("Satisfaction client par canal de distribution", fontweight="bold")
        ax.set_xlim(0, min(11, stats["mean"].max() + 2))
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, "satisfaction_by_channel.png")
        return fig

    # ------------------------------------------------------------------
    # 5. Satisfaction par type de chambre
    # ------------------------------------------------------------------

    def plot_satisfaction_by_room(
        self,
        df: pd.DataFrame,
        score_col: str = "review_score",
        room_col: str = "room_segment",
        figsize: Tuple[int, int] = (10, 5),
        save: bool = True,
    ) -> plt.Figure:
        """
        Violin plot : distribution de la satisfaction par type de chambre.
        """
        for col in [score_col, room_col]:
            if col not in df.columns:
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Colonne '{col}' absente", ha="center")
                return fig

        df_valid = df[[score_col, room_col]].dropna(subset=[score_col])
        order = (
            df_valid.groupby(room_col)[score_col]
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        )

        fig, ax = plt.subplots(figsize=figsize)
        data_by_room = [
            df_valid[df_valid[room_col] == r][score_col].dropna().values
            for r in order
        ]
        parts = ax.violinplot(data_by_room, positions=range(len(order)),
                              showmedians=True, showmeans=False)
        for pc in parts["bodies"]:
            pc.set_facecolor("steelblue")
            pc.set_alpha(0.6)

        # Overlay boxplot
        ax.boxplot(data_by_room, positions=range(len(order)), widths=0.15,
                   patch_artist=False, medianprops=dict(color="red", lw=2))

        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(order, rotation=20, ha="right")
        ax.set_ylabel("Note d'avis (/10)")
        ax.set_title("Satisfaction par type de chambre", fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, "satisfaction_by_room.png")
        return fig

    # ------------------------------------------------------------------
    # 6. Revenu moyen par communauté
    # ------------------------------------------------------------------

    def plot_revenue_by_community(
        self,
        df: pd.DataFrame,
        revenue_col: str = "revenue",
        comm_col: str = "community_id",
        figsize: Tuple[int, int] = (12, 5),
        save: bool = True,
    ) -> plt.Figure:
        """
        Barre : revenu moyen et total par communauté.
        """
        for col in [revenue_col, comm_col]:
            if col not in df.columns:
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Colonne '{col}' absente", ha="center")
                return fig

        df_valid = df[[revenue_col, comm_col]].dropna()
        df_valid[comm_col] = df_valid[comm_col].astype(int)
        stats = (
            df_valid.groupby(comm_col)[revenue_col]
            .agg(["mean", "sum", "count"])
            .nlargest(12, "sum")
        )

        fig, axes = plt.subplots(1, 2, figsize=figsize)

        for ax, col_plot, title, fmt in [
            (axes[0], "mean", "Revenu moyen par communauté (€)", ".0f"),
            (axes[1], "sum",  "Revenu total par communauté (€)", ".0f"),
        ]:
            colors = [_PALETTE[i % 10] for i in range(len(stats))]
            bars = ax.bar([f"C{c}" for c in stats.index], stats[col_plot],
                          color=colors, edgecolor="white")
            for bar, val in zip(bars, stats[col_plot]):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                        f"{val:{fmt}}€", ha="center", va="bottom", fontsize=8)
            ax.set_title(title, fontweight="bold")
            ax.set_xlabel("Communauté")
            ax.set_ylabel("€")
            ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, "revenue_by_community.png")
        return fig

    # ------------------------------------------------------------------
    # 7. Top profils centraux
    # ------------------------------------------------------------------

    def plot_top_central_profiles(
        self,
        df: pd.DataFrame,
        centrality_col: str = "pagerank",
        top_n: int = 15,
        figsize: Tuple[int, int] = (12, 6),
        save: bool = True,
    ) -> plt.Figure:
        """
        Barre horizontale : top N clients par PageRank (ou autre métrique).
        Enrichie avec le canal et la note si disponibles.
        """
        if centrality_col not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, f"Colonne '{centrality_col}' absente", ha="center")
            return fig

        top = df.nlargest(top_n, centrality_col).copy()
        top["label"] = top["client_id"].astype(str)
        if "channel_group" in top.columns:
            top["label"] += " [" + top["channel_group"].fillna("?") + "]"

        colors = "steelblue"
        if "channel_group" in top.columns:
            colors = [_CHANNEL_COLORS.get(c, "#95a5a6") for c in top["channel_group"].fillna("unknown")]

        fig, ax = plt.subplots(figsize=figsize)
        bars = ax.barh(top["label"][::-1], top[centrality_col][::-1],
                       color=colors[::-1] if isinstance(colors, list) else colors,
                       edgecolor="white")

        # Overlay note si disponible
        if "review_score" in top.columns:
            ax2 = ax.twiny()
            ax2.scatter(
                top["review_score"][::-1].values,
                range(len(top)),
                color="red", zorder=5, s=50, label="Note (/10)",
            )
            ax2.set_xlabel("Note d'avis (/10)", color="red")
            ax2.tick_params(axis="x", colors="red")
            ax2.legend(loc="lower right", fontsize=8)

        ax.set_xlabel(centrality_col)
        ax.set_title(f"Top {top_n} clients — {centrality_col}", fontweight="bold")
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, f"top_central_profiles_{centrality_col}.png")
        return fig

    # ------------------------------------------------------------------
    # 8. Importance des features
    # ------------------------------------------------------------------

    def plot_feature_importance(
        self,
        df_importance: pd.DataFrame,
        top_n: int = 15,
        figsize: Tuple[int, int] = (10, 7),
        save: bool = True,
    ) -> plt.Figure:
        """
        Barre horizontale de l'importance des features.
        """
        if df_importance is None or df_importance.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Importance non disponible", ha="center")
            return fig

        top = df_importance.head(top_n)
        norm = top["importance"] / top["importance"].max()
        colors = [plt.cm.RdYlGn(v) for v in norm]

        fig, ax = plt.subplots(figsize=figsize)
        bars = ax.barh(top["feature"][::-1], top["importance"][::-1],
                       color=colors[::-1], edgecolor="white")
        for bar, val in zip(bars, top["importance"][::-1]):
            ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
                    f"{val:.3f}", va="center", fontsize=9)

        ax.set_xlabel("Importance (Gini)")
        ax.set_title(f"Top {top_n} features — modèle de satisfaction", fontweight="bold")
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, "feature_importance.png")
        return fig

    # ------------------------------------------------------------------
    # 9. Comparaison multi-modèles
    # ------------------------------------------------------------------

    def plot_model_comparison(
        self,
        results: Dict[str, Dict],
        metric: str = "f1_weighted",
        figsize: Tuple[int, int] = (10, 5),
        save: bool = True,
    ) -> plt.Figure:
        """
        Barre : comparaison des modèles sur une métrique donnée.
        """
        models = [k for k, v in results.items() if "error" not in v]
        if not models:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Aucun résultat disponible", ha="center")
            return fig

        scores = [results[m].get(metric, results[m].get("r2", 0)) for m in models]
        colors = [_PALETTE[i % 10] for i in range(len(models))]

        fig, ax = plt.subplots(figsize=figsize)
        bars = ax.bar(models, scores, color=colors, edgecolor="white")
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{score:.4f}", ha="center", fontweight="bold")

        ax.set_ylabel(metric.upper())
        ax.set_title(f"Comparaison des modèles — {metric}", fontweight="bold")
        ax.set_ylim(0, min(1.0, max(scores) * 1.2) if scores else 1.0)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, f"model_comparison_{metric}.png")
        return fig

    # ------------------------------------------------------------------
    # 10. Matrice de corrélation
    # ------------------------------------------------------------------

    def plot_correlation_matrix(
        self,
        df: pd.DataFrame,
        figsize: Tuple[int, int] = (10, 8),
        save: bool = True,
    ) -> plt.Figure:
        """
        Heatmap de corrélation sur les colonnes numériques pertinentes.
        """
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclure les identifiants
        num_cols = [c for c in num_cols if c not in ("client_id", "node_id")]
        if len(num_cols) < 2:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Pas assez de colonnes numériques", ha="center")
            return fig

        corr = df[num_cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))

        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(
            corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, square=True, ax=ax, linewidths=0.5,
            cbar_kws={"label": "Corrélation"},
        )
        ax.set_title("Matrice de corrélation des variables numériques",
                     fontweight="bold", pad=15)
        plt.tight_layout()

        if save:
            _save(fig, self.output_dir, "correlation_matrix.png")
        return fig

    # ------------------------------------------------------------------
    # 11. Statistiques du réseau (ancienne API conservée)
    # ------------------------------------------------------------------

    def plot_network_statistics(
        self,
        stats: Dict[str, float],
        figsize: Tuple[int, int] = (10, 5),
        save: bool = True,
    ) -> plt.Figure:
        """
        Barre : statistiques globales du réseau.
        """
        plot_keys = {
            "density": "Densité",
            "average_clustering": "Clust. moyen",
            "modularity": "Modularité",
        }
        plot_data = {v: stats[k] for k, v in plot_keys.items() if k in stats}

        if not plot_data:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Statistiques réseau non disponibles", ha="center")
            return fig

        fig, ax = plt.subplots(figsize=figsize)
        colors = [_PALETTE[i % 10] for i in range(len(plot_data))]
        bars = ax.bar(list(plot_data.keys()), list(plot_data.values()), color=colors,
                      edgecolor="white")
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                    f"{bar.get_height():.4f}", ha="center", fontweight="bold", fontsize=10)

        ax.set_title("Statistiques globales du réseau", fontweight="bold")
        ax.set_ylabel("Valeur")
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()

        if save:
            _save(fig, self.output_dir, "network_statistics.png")
        return fig

    # ------------------------------------------------------------------
    # 12. Comparaison centralités (ancienne API)
    # ------------------------------------------------------------------

    def plot_centrality_comparison(
        self,
        df_centrality: pd.DataFrame,
        top_n: int = 15,
        figsize: Tuple[int, int] = (14, 8),
        save: bool = True,
    ) -> plt.Figure:
        """
        Compare les différentes métriques de centralité (top N).
        """
        metrics = [
            c for c in df_centrality.select_dtypes(include=[np.number]).columns
            if c not in ("community_id",)
        ]
        if not metrics:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Aucune métrique disponible", ha="center")
            return fig

        n_cols = min(3, len(metrics))
        n_rows = int(np.ceil(len(metrics) / n_cols))
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = np.array(axes).flatten()

        id_col = "client_id" if "client_id" in df_centrality.columns else df_centrality.columns[0]

        for idx, metric in enumerate(metrics[:len(axes)]):
            ax = axes[idx]
            top = df_centrality.nlargest(top_n, metric)
            labels = top[id_col].astype(str).str[:12].values
            ax.barh(range(len(top)), top[metric].values, color=_PALETTE[idx % 10])
            ax.set_yticks(range(len(top)))
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_xlabel(metric)
            ax.set_title(f"Top {top_n} — {metric}", fontweight="bold")
            ax.invert_yaxis()

        for idx in range(len(metrics), len(axes)):
            axes[idx].axis("off")

        plt.suptitle("Comparaison des métriques de centralité", fontsize=13,
                     fontweight="bold", y=1.01)
        plt.tight_layout()

        if save:
            _save(fig, self.output_dir, "centrality_comparison.png")
        return fig

    # ------------------------------------------------------------------
    # 13. Prédictions vs réel (régression)
    # ------------------------------------------------------------------

    def plot_prediction_results(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        metric_name: str = "satisfaction",
        figsize: Tuple[int, int] = (12, 5),
        save: bool = True,
    ) -> plt.Figure:
        """
        Nuage de points Réel vs Prédit + histogramme des résidus.
        """
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Réel vs Prédit
        ax = axes[0]
        ax.scatter(y_true, y_pred, alpha=0.5, s=30, edgecolors="none", color="steelblue")
        lim = (min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max()))
        ax.plot(lim, lim, "r--", lw=1.5, label="Parfait")
        ax.set_xlabel("Valeurs réelles")
        ax.set_ylabel("Valeurs prédites")
        ax.set_title(f"Réel vs Prédit — {metric_name}", fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Résidus
        ax2 = axes[1]
        residuals = y_true - y_pred
        ax2.hist(residuals, bins=25, color="steelblue", alpha=0.7, edgecolor="white")
        ax2.axvline(0, color="red", lw=1.5, ls="--")
        ax2.set_xlabel("Résidu (réel − prédit)")
        ax2.set_ylabel("Fréquence")
        ax2.set_title("Distribution des résidus", fontweight="bold")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        if save:
            _save(fig, self.output_dir, f"prediction_residuals_{metric_name}.png")
        return fig
