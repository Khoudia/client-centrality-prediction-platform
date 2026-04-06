"""Exemple simple aligné sur le pipeline hôtelier actuel."""

from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import SatisfactionPredictor
from src.visualization.visualizer import NetworkVisualizer


def exemple_complet():
    """Montre le flux démo : données -> réseau -> satisfaction -> figures."""
    print("=" * 60)
    print("EXEMPLE SIMPLE — HÔTEL AURORE PARIS")
    print("=" * 60)

    loader = DataLoader()
    df_clients = loader.generate_sample_data(n_clients=100)
    print(f"\n1️⃣ Dataset démo chargé : {df_clients.shape}")
    print(df_clients.head())

    analyzer = NetworkAnalyzer()
    graph = analyzer.build_similarity_graph(df_clients, min_similarity=0.3, max_nodes=100)
    communities = analyzer.detect_communities(method="greedy")
    df_metrics = analyzer.compute_network_metrics()
    df_enriched = analyzer.export_network_results(df_clients)
    stats = analyzer.get_network_statistics()

    print("\n2️⃣ Réseau de similarité")
    print(f"   - Nœuds : {graph.number_of_nodes()}")
    print(f"   - Arêtes : {graph.number_of_edges()}")
    print(f"   - Densité : {stats['density']:.4f}")
    print(f"   - Communautés : {len(set(communities.values())) if communities else 0}")

    print("\n3️⃣ Top 5 profils par PageRank")
    print(df_metrics.nlargest(5, "pagerank")[["client_id", "pagerank"]].to_string(index=False))

    predictor = SatisfactionPredictor(model_type="random_forest", task="classification")
    X, y = predictor.prepare_features(df_enriched)
    results = predictor.train(X, y, validation=True)

    print("\n4️⃣ Modèle de satisfaction")
    for key, value in results.items():
        print(f"   - {key}: {value}")

    print("\n5️⃣ Top features")
    print(predictor.get_feature_importance(top_n=5).to_string(index=False))

    viz = NetworkVisualizer()
    viz.plot_network(graph, communities=communities, save=True)
    viz.plot_centrality_distribution(df_metrics, save=True)
    viz.plot_satisfaction_by_channel(df_enriched, save=True)

    print("\n6️⃣ Figures sauvegardées dans outputs/figures/")
    print("\n✅ EXEMPLE TERMINÉ AVEC SUCCÈS")
    print("   • Lancer Streamlit : python -m streamlit run app.py")
    print("   • Tester le pipeline : python test_quick.py\n")


if __name__ == '__main__':
    exemple_complet()
