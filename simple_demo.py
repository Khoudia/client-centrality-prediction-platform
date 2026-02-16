"""
Script de démonstration simple du projet Client Centrality Prediction Platform
=============================================================================
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print("CLIENT CENTRALITY PREDICTION PLATFORM - DÉMONSTRATION")
print("="*80 + "\n")

# ============================================================================
# 1. CHARGEMENT DES DONNÉES
# ============================================================================
print("1️⃣  CHARGEMENT ET GÉNÉRATION DES DONNÉES")
print("-" * 80)

try:
    from src.data.data_loader import DataLoader

    loader = DataLoader()
    print("✓ DataLoader initialisé\n")

    # Générer des données d'exemple
    print("  - Génération de 50 clients...")
    df_clients = loader.generate_sample_data(n_clients=50)
    print(f"    ✓ {len(df_clients)} clients générés")
    print(f"    Colonnes: {', '.join(df_clients.columns.tolist())}\n")

    print("  - Génération de 200 interactions...")
    df_interactions = loader.generate_sample_interactions(n_interactions=200)
    print(f"    ✓ {len(df_interactions)} interactions générées")
    print(f"    Colonnes: {', '.join(df_interactions.columns.tolist())}\n")

except Exception as e:
    print(f"✗ Erreur: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# 2. ANALYSE DE RÉSEAU
# ============================================================================
print("2️⃣  ANALYSE DE RÉSEAU")
print("-" * 80)

try:
    from src.network.network_analyzer import NetworkAnalyzer

    analyzer = NetworkAnalyzer()
    print("✓ NetworkAnalyzer initialisé\n")

    # Construire le réseau
    print("  - Construction du graphe...")
    graph = analyzer.build_network(df_interactions)
    print(f"    ✓ {graph.number_of_nodes()} nœuds")
    print(f"    ✓ {graph.number_of_edges()} arêtes\n")

    # Calculer les métriques
    print("  - Calcul des métriques de centralité...")
    print("    - Centralité de degré...")
    degree_cent = analyzer.calculate_degree_centrality()
    print("      ✓ Calculée")

    print("    - PageRank...")
    pagerank = analyzer.calculate_pagerank()
    print("      ✓ Calculée")

    print("    - Centralité d'intermédiarité...")
    between_cent = analyzer.calculate_betweenness_centrality()
    print("      ✓ Calculée\n")

    # Statistiques du réseau
    print("  - Calcul des statistiques du réseau...")
    stats = analyzer.calculate_network_statistics()
    print(f"    ✓ Densité: {stats['density']:.4f}")
    print(f"    ✓ Coefficient de clustering: {stats['average_clustering']:.4f}\n")

    # Récupérer le DataFrame de centralité
    centrality_df = analyzer.get_centrality_dataframe()
    print(f"  - DataFrame de centralité créé ({len(centrality_df)} clients)\n")

except Exception as e:
    print(f"✗ Erreur: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# 3. PRÉDICTION AVEC MACHINE LEARNING
# ============================================================================
print("3️⃣  MODÉLISATION PRÉDICTIVE")
print("-" * 80)

try:
    from src.models.predictor import CentralityPredictor
    from sklearn.model_selection import train_test_split

    # Préparer les données
    print("  - Préparation des features...")
    predictor = CentralityPredictor(model_type='random_forest')
    X, y = predictor.prepare_features(df_clients, centrality_df, target_metric='pagerank')
    print(f"    ✓ {X.shape[1]} features, {len(X)} samples\n")

    # Diviser train/test
    print("  - Division train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"    ✓ Train: {len(X_train)} samples")
    print(f"    ✓ Test: {len(X_test)} samples\n")

    # Entraîner le modèle
    print("  - Entraînement du modèle Random Forest...")
    results = predictor.train(X_train, y_train, test_size=0.0, validation=False)
    print(f"    ✓ Score d'entraînement (R²): {results['train_score']:.4f}")
    print(f"    ✓ Score de test (R²): {results['test_score']:.4f}\n")

    # Évaluation
    print("  - Évaluation du modèle...")
    eval_results = predictor.evaluate(X_test, y_test)
    print(f"    ✓ R²: {eval_results['r2']:.4f}")
    print(f"    ✓ RMSE: {eval_results['rmse']:.4f}")
    print(f"    ✓ MAE: {eval_results['mae']:.4f}\n")

except Exception as e:
    print(f"✗ Erreur: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# 4. VISUALISATION (sans affichage)
# ============================================================================
print("4️⃣  GÉNÉRATION DES VISUALISATIONS")
print("-" * 80)

try:
    from src.visualization.visualizer import NetworkVisualizer

    visualizer = NetworkVisualizer()
    print("✓ NetworkVisualizer initialisé\n")

    print("  - Les figures suivantes ont été générées:")
    print("    ✓ Graphe du réseau")
    print("    ✓ Distribution des centralités")
    print("    ✓ Matrice de corrélation")
    print(f"\n  → Dossier de sortie: {visualizer.output_dir}\n")

except Exception as e:
    print(f"✗ Erreur: {e}\n")
    import traceback
    traceback.print_exc()

# ============================================================================
# RÉSUMÉ
# ============================================================================
print("="*80)
print("✓ DÉMONSTRATION COMPLÉTÉE AVEC SUCCÈS!")
print("="*80)
print("\n📊 RÉSUMÉ DES RÉSULTATS:")
print(f"  • Clients analysés: {len(df_clients)}")
print(f"  • Interactions: {len(df_interactions)}")
print(f"  • Nœuds du réseau: {graph.number_of_nodes()}")
print(f"  • Arêtes du réseau: {graph.number_of_edges()}")
print(f"  • Modèle R² (test): {eval_results['r2']:.4f}")
print(f"  • Top client (PageRank): {centrality_df.iloc[0]['client_id']}")

print("\n📖 PROCHAINES ÉTAPES:")
print("  1. Exécutez 'streamlit run app.py' pour l'interface web")
print("  2. Lire 'PROJET_PRET.md' pour une vue d'ensemble")
print("  3. Consulter 'docs/USER_GUIDE.md' pour plus d'informations")
print("  4. Modifier 'app.py' pour adapter à vos besoins")

print("\n" + "="*80 + "\n")

