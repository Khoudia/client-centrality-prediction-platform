"""
Module pour la visualisation des résultats.

Ce module fournit des fonctions pour visualiser les graphes de réseau,
les métriques de centralité et les résultats de prédiction.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

logger = logging.getLogger(__name__)

# Configuration du style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class NetworkVisualizer:
    """
    Classe pour visualiser les réseaux et les résultats d'analyse.
    """

    def __init__(self, output_dir: str = 'outputs/figures'):
        """
        Initialise le visualiseur.

        Args:
            output_dir: Répertoire de sortie pour les figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Répertoire de sortie : {self.output_dir}")

    def plot_network(self, graph: nx.Graph,
                    centrality_metric: Optional[Dict] = None,
                    title: str = "Réseau de clients",
                    figsize: Tuple[int, int] = (14, 10),
                    save: bool = True) -> plt.Figure:
        """
        Visualise le graphe du réseau.

        Args:
            graph: Graphe NetworkX à visualiser
            centrality_metric: Dictionnaire de centralité pour colorer les nœuds
            title: Titre du graphe
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création de la visualisation du réseau...")

        fig, ax = plt.subplots(figsize=figsize)

        # Layout du graphe
        if graph.number_of_nodes() > 100:
            pos = nx.spring_layout(graph, k=0.5, iterations=20, seed=42)
        else:
            pos = nx.spring_layout(graph, k=1, iterations=50, seed=42)

        # Couleurs basées sur la centralité
        if centrality_metric:
            node_colors = [centrality_metric.get(node, 0) for node in graph.nodes()]
            cmap = 'YlOrRd'
        else:
            node_colors = 'lightblue'
            cmap = None

        # Tailles des nœuds
        node_sizes = [100 + 300 * (centrality_metric.get(node, 0) if centrality_metric else 1)
                     for node in graph.nodes()]

        # Dessin du réseau
        nx.draw_networkx_nodes(
            graph, pos,
            node_color=node_colors,
            node_size=node_sizes,
            cmap=cmap,
            alpha=0.8,
            ax=ax
        )

        nx.draw_networkx_edges(
            graph, pos,
            alpha=0.2,
            width=0.5,
            ax=ax
        )

        # Étiquettes (seulement pour les petits réseaux)
        if graph.number_of_nodes() <= 30:
            nx.draw_networkx_labels(
                graph, pos,
                font_size=8,
                font_weight='bold',
                ax=ax
            )

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()

        if save:
            filepath = self.output_dir / f"network_{title.replace(' ', '_')}.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig

    def plot_centrality_comparison(self, df_centrality: pd.DataFrame,
                                   top_n: int = 15,
                                   figsize: Tuple[int, int] = (14, 8),
                                   save: bool = True) -> plt.Figure:
        """
        Compare les différentes métriques de centralité.

        Args:
            df_centrality: DataFrame avec les métriques
            top_n: Nombre de clients à afficher
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création du graphique de comparaison des centralités...")

        # Récupérer les colonnes de centralité
        metrics = [col for col in df_centrality.columns if col != 'client_id']

        fig, axes = plt.subplots(2, 3, figsize=figsize)
        axes = axes.flatten()

        for idx, metric in enumerate(metrics):
            if idx < len(axes):
                ax = axes[idx]

                # Top N clients
                top_clients = df_centrality.nlargest(top_n, metric)

                ax.barh(range(len(top_clients)), top_clients[metric].values, color='steelblue')
                ax.set_yticks(range(len(top_clients)))
                ax.set_yticklabels(top_clients['client_id'].values, fontsize=9)
                ax.set_xlabel(metric, fontweight='bold')
                ax.set_title(f"Top {top_n} clients ({metric})", fontweight='bold')
                ax.invert_yaxis()

        # Masquer les subplots inutilisés
        for idx in range(len(metrics), len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "centrality_comparison.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig

    def plot_centrality_distribution(self, df_centrality: pd.DataFrame,
                                    figsize: Tuple[int, int] = (14, 8),
                                    save: bool = True) -> plt.Figure:
        """
        Affiche la distribution des métriques de centralité.

        Args:
            df_centrality: DataFrame avec les métriques
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création du graphique de distribution...")

        metrics = [col for col in df_centrality.columns if col != 'client_id']

        fig, axes = plt.subplots(2, 3, figsize=figsize)
        axes = axes.flatten()

        for idx, metric in enumerate(metrics):
            if idx < len(axes):
                ax = axes[idx]

                ax.hist(df_centrality[metric], bins=30, color='steelblue', alpha=0.7, edgecolor='black')
                ax.set_xlabel(metric, fontweight='bold')
                ax.set_ylabel('Fréquence')
                ax.set_title(f"Distribution - {metric}", fontweight='bold')
                ax.grid(True, alpha=0.3)

        # Masquer les subplots inutilisés
        for idx in range(len(metrics), len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "centrality_distribution.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig

    def plot_correlation_matrix(self, df_centrality: pd.DataFrame,
                               figsize: Tuple[int, int] = (10, 8),
                               save: bool = True) -> plt.Figure:
        """
        Affiche la matrice de corrélation entre les métriques.

        Args:
            df_centrality: DataFrame avec les métriques
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création de la matrice de corrélation...")

        metrics = [col for col in df_centrality.columns if col != 'client_id']
        corr_matrix = df_centrality[metrics].corr()

        fig, ax = plt.subplots(figsize=figsize)

        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, ax=ax, cbar_kws={'label': 'Corrélation'})

        ax.set_title("Matrice de corrélation des métriques de centralité",
                    fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "correlation_matrix.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig

    def plot_feature_importance(self, df_importance: pd.DataFrame,
                               top_n: int = 15,
                               figsize: Tuple[int, int] = (10, 8),
                               save: bool = True) -> plt.Figure:
        """
        Affiche l'importance des features du modèle.

        Args:
            df_importance: DataFrame avec colonnes 'feature' et 'importance'
            top_n: Nombre de features à afficher
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création du graphique d'importance des features...")

        fig, ax = plt.subplots(figsize=figsize)

        top_features = df_importance.head(top_n)

        ax.barh(range(len(top_features)), top_features['importance'].values, color='forestgreen')
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'].values)
        ax.set_xlabel('Importance', fontweight='bold')
        ax.set_title(f'Top {top_n} Features Importance', fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "feature_importance.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig

    def plot_prediction_results(self, y_true: np.ndarray,
                               y_pred: np.ndarray,
                               metric_name: str = 'centralité',
                               figsize: Tuple[int, int] = (12, 5),
                               save: bool = True) -> plt.Figure:
        """
        Compare les prédictions avec les valeurs réelles.

        Args:
            y_true: Valeurs réelles
            y_pred: Prédictions
            metric_name: Nom de la métrique
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création du graphique de prédictions...")

        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Graphique 1 : Réel vs Prédit
        ax1 = axes[0]
        ax1.scatter(y_true, y_pred, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)

        # Ligne de tendance parfaite
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Parfait')

        ax1.set_xlabel('Valeurs réelles', fontweight='bold')
        ax1.set_ylabel('Valeurs prédites', fontweight='bold')
        ax1.set_title(f'Réel vs Prédit ({metric_name})', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Graphique 2 : Résidus
        ax2 = axes[1]
        residuals = y_true - y_pred
        ax2.scatter(y_pred, residuals, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        ax2.axhline(y=0, color='r', linestyle='--', lw=2)

        ax2.set_xlabel('Valeurs prédites', fontweight='bold')
        ax2.set_ylabel('Résidus', fontweight='bold')
        ax2.set_title('Analyse des résidus', fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            filepath = self.output_dir / f"prediction_results_{metric_name}.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig

    def plot_model_comparison(self, results: Dict[str, Dict[str, float]],
                             metric: str = 'r2',
                             figsize: Tuple[int, int] = (10, 6),
                             save: bool = True) -> plt.Figure:
        """
        Compare les performances de différents modèles.

        Args:
            results: Dictionnaire des résultats par modèle
            metric: Métrique à comparer
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création du graphique de comparaison des modèles...")

        fig, ax = plt.subplots(figsize=figsize)

        models = list(results.keys())
        scores = [results[model].get(metric, 0) for model in models]

        colors = plt.cm.Set3(np.linspace(0, 1, len(models)))
        bars = ax.bar(models, scores, color=colors, edgecolor='black', linewidth=1.5)

        # Ajouter les valeurs sur les barres
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.3f}',
                   ha='center', va='bottom', fontweight='bold')

        ax.set_ylabel(metric.upper(), fontweight='bold')
        ax.set_title(f'Comparaison des modèles ({metric.upper()})', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(scores) * 1.15)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save:
            filepath = self.output_dir / f"model_comparison_{metric}.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig

    def plot_network_statistics(self, stats: Dict[str, float],
                               figsize: Tuple[int, int] = (10, 6),
                               save: bool = True) -> plt.Figure:
        """
        Affiche les statistiques du réseau.

        Args:
            stats: Dictionnaire des statistiques du réseau
            figsize: Taille de la figure
            save: Si True, sauvegarde l'image

        Returns:
            Figure matplotlib
        """
        logger.info(f"Création du graphique de statistiques du réseau...")

        fig, ax = plt.subplots(figsize=figsize)

        # Filtrer les statistiques pertinentes pour la visualisation
        plot_stats = {}
        for key, value in stats.items():
            if key in ['density', 'average_clustering', 'average_shortest_path']:
                plot_stats[key] = value

        if not plot_stats:
            logger.warning("Pas de statistiques à afficher")
            return fig

        bars = ax.bar(range(len(plot_stats)), list(plot_stats.values()),
                      color='steelblue', edgecolor='black', linewidth=1.5)

        ax.set_xticks(range(len(plot_stats)))
        ax.set_xticklabels(list(plot_stats.keys()), rotation=15)
        ax.set_ylabel('Valeur', fontweight='bold')
        ax.set_title('Statistiques du réseau', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "network_statistics.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Figure sauvegardée : {filepath}")

        return fig
