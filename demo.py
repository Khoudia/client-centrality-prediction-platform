"""
Script d'exemple pour tester rapidement la plateforme.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import CentralityPredictor
from src.visualization.visualizer import NetworkVisualizer
from src.utils.logger import setup_logger
from sklearn.model_selection import train_test_split

logger = setup_logger(__name__)


def main():
    """
    Exemple d'utilisation complète de la plateforme.
    """
    logger.info("=== DÉMO DE LA PLATEFORME ===\n")

    # 1. GÉNÉRATION DES DONNÉES D'EXEMPLE
    logger.info("1️⃣ Génération des données d'exemple...")
    loader = DataLoader()
    df_clients = loader.generate_sample_data(n_clients=100)
    df_interactions = loader.generate_sample_interactions(n_interactions=500)
    logger.info(f"   ✓ {len(df_clients)} clients générés")
    logger.info(f"   ✓ {len(df_interactions)} interactions générées\n")

    # 2. CONSTRUCTION ET ANALYSE DU RÉSEAU
    logger.info("2️⃣ Construction et analyse du réseau...")
    analyzer = NetworkAnalyzer()
    graph = analyzer.build_network(df_interactions)

    stats = analyzer.get_network_statistics()
    logger.info(f"   ✓ Réseau construit: {stats['nb_nodes']} nœuds, {stats['nb_edges']} arêtes")
    logger.info(f"   ✓ Densité: {stats['density']:.4f}")
    logger.info(f"   ✓ Clustering moyen: {stats['avg_clustering']:.4f}\n")

    # 3. CALCUL DES MÉTRIQUES DE CENTRALITÉ
    logger.info("3️⃣ Calcul des métriques de centralité...")
    centrality_metrics = analyzer.calculate_all_centralities()
    centrality_df = analyzer.get_centrality_dataframe()
    logger.info(f"   ✓ {len(centrality_metrics)} métriques calculées")

    # Top 5 clients par centralité de degré
    top_5 = centrality_df.nlargest(5, 'centrality_degree')
    logger.info("\n   Top 5 clients (centralité de degré):")
    for _, row in top_5.iterrows():
        logger.info(f"      • {row['node_id']}: {row['centrality_degree']:.4f}")
    logger.info("")

    # 4. ENTRAÎNEMENT DES MODÈLES
    logger.info("4️⃣ Entraînement des modèles prédictifs...")
    predictor = CentralityPredictor(model_type='random_forest')

    # Préparer les features
    X, y = predictor.prepare_features(df_clients, centrality_df)
    logger.info(f"   ✓ Features préparées: {X.shape}")

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Entraîner
    training_scores = predictor.train(X_train, y_train)
    logger.info("\n   Scores d'entraînement (validation croisée):")
    if training_scores.get('cv_r2_mean') is not None:
        logger.info(f"      • R² = {training_scores['cv_r2_mean']:.4f} "
                   f"(+/- {training_scores['cv_r2_std']:.4f})")
    else:
        logger.info(f"      • R² train = {training_scores['train_score']:.4f}")
        logger.info(f"      • R² test = {training_scores['test_score']:.4f}")

    # 5. ÉVALUATION
    logger.info("\n5️⃣ Évaluation sur l'ensemble de test...")
    eval_results = predictor.evaluate(X_test, y_test)
    logger.info("\n   Résultats sur le test:")
    logger.info(f"      • R² = {eval_results['r2']:.4f}")
    logger.info(f"      • RMSE = {eval_results['rmse']:.4f}")
    logger.info(f"      • MAE = {eval_results['mae']:.4f}")

    # 6. IMPORTANCE DES FEATURES
    logger.info("\n6️⃣ Analyse de l'importance des features...")
    target = 'centrality_degree'
    importance_df = predictor.get_feature_importance(target, top_n=5)
    logger.info(f"\n   Top 5 features pour {target}:")
    for _, row in importance_df.iterrows():
        logger.info(f"      • {row['feature']}: {row['importance']:.4f}")

    # 7. SAUVEGARDE
    logger.info("\n7️⃣ Sauvegarde des modèles...")
    predictor.save_models(prefix='demo_model')
    logger.info("   ✓ Modèles sauvegardés dans le dossier 'models/'\n")

    logger.info("=== DÉMO TERMINÉE AVEC SUCCÈS ===")
    logger.info("\nPour aller plus loin:")
    logger.info("  • Lancez l'application web: streamlit run app.py")
    logger.info("  • Explorez les notebooks dans 'notebooks/'")
    logger.info("  • Consultez la documentation dans 'docs/'\n")


if __name__ == '__main__':
    main()

