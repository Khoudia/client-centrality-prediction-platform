"""Script de démonstration rapide du pipeline hôtelier en mode échantillon."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import SatisfactionPredictor
from src.visualization.visualizer import NetworkVisualizer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Exécute une démonstration complète en mode démo, sans données réelles."""
    logger.info("=== DÉMO HÔTEL Aurore Paris — Mode échantillon ===\n")

    loader = DataLoader()
    df_clients = loader.generate_sample_data(n_clients=120)
    logger.info(f"1️⃣ Données de démo générées : {len(df_clients)} lignes")

    analyzer = NetworkAnalyzer()
    graph = analyzer.build_similarity_graph(df_clients, min_similarity=0.3, max_nodes=120)
    communities = analyzer.detect_communities(method="greedy")
    df_metrics = analyzer.compute_network_metrics()
    df_enriched = analyzer.export_network_results(df_clients)
    stats = analyzer.get_network_statistics()

    logger.info(
        "2️⃣ Réseau : %s nœuds | %s arêtes | densité=%s | communautés=%s",
        graph.number_of_nodes(),
        graph.number_of_edges(),
        stats.get("density"),
        len(set(communities.values())) if communities else 0,
    )

    top_5 = df_metrics.nlargest(5, "pagerank")[["client_id", "pagerank"]]
    logger.info("3️⃣ Top 5 profils centraux (PageRank) :")
    for _, row in top_5.iterrows():
        logger.info("   • %s : %.4f", row["client_id"], row["pagerank"])

    predictor = SatisfactionPredictor(model_type="random_forest", task="classification")
    X, y = predictor.prepare_features(df_enriched)
    results = predictor.train(X, y, validation=True)
    logger.info("4️⃣ Modèle satisfaction : %s", results)

    importance_df = predictor.get_feature_importance(top_n=5)
    if not importance_df.empty:
        logger.info("5️⃣ Top 5 variables explicatives :")
        for _, row in importance_df.iterrows():
            logger.info("   • %s : %.4f", row["feature"], row["importance"])

    viz = NetworkVisualizer()
    viz.plot_network(graph, communities=communities, save=True)
    viz.plot_centrality_distribution(df_metrics, save=True)
    viz.plot_feature_importance(importance_df, save=True)
    logger.info("6️⃣ Figures sauvegardées dans outputs/figures/")

    predictor.save_models(prefix="demo_model")
    logger.info("7️⃣ Modèle sauvegardé dans models/")

    logger.info("\n=== DÉMO TERMINÉE AVEC SUCCÈS ===")
    logger.info("• Lancer l'application : python -m streamlit run app.py")
    logger.info("• Exécuter les validations : python test_quick.py")


if __name__ == '__main__':
    main()

