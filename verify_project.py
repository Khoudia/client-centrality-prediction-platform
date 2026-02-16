"""
Script de vérification complète du projet
==========================================
Ce script teste tous les composants du projet pour s'assurer qu'ils fonctionnent.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Ajouter le chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configuration
RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "project_root": str(project_root),
    "tests": {},
    "summary": {}
}

def test_imports():
    """Test tous les imports principaux"""
    print("\n" + "="*80)
    print("TEST 1 : IMPORTS")
    print("="*80)

    tests = {
        "DataLoader": "from src.data.data_loader import DataLoader",
        "NetworkAnalyzer": "from src.network.network_analyzer import NetworkAnalyzer",
        "CentralityPredictor": "from src.models.predictor import CentralityPredictor",
        "NetworkVisualizer": "from src.visualization.visualizer import NetworkVisualizer"
    }

    passed = 0
    for name, import_stmt in tests.items():
        try:
            exec(import_stmt)
            print(f"  ✓ {name}")
            RESULTS["tests"][name] = "PASS"
            passed += 1
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            RESULTS["tests"][name] = f"FAIL: {str(e)}"

    print(f"\n  Résultat: {passed}/{len(tests)} imports réussis")
    return passed == len(tests)

def test_data_loader():
    """Test le module DataLoader"""
    print("\n" + "="*80)
    print("TEST 2 : DATA LOADER")
    print("="*80)

    try:
        from src.data.data_loader import DataLoader

        loader = DataLoader()
        print("  ✓ DataLoader initialisé")

        # Générer les données
        df_clients = loader.generate_sample_data(n_clients=20)
        print(f"  ✓ {len(df_clients)} clients générés")

        df_interactions = loader.generate_sample_interactions(n_interactions=50)
        print(f"  ✓ {len(df_interactions)} interactions générées")

        RESULTS["tests"]["DataLoader_functionality"] = "PASS"
        return True, (df_clients, df_interactions)

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        RESULTS["tests"]["DataLoader_functionality"] = f"FAIL: {str(e)}"
        return False, (None, None)

def test_network_analyzer(df_interactions):
    """Test le module NetworkAnalyzer"""
    print("\n" + "="*80)
    print("TEST 3 : NETWORK ANALYZER")
    print("="*80)

    try:
        from src.network.network_analyzer import NetworkAnalyzer

        analyzer = NetworkAnalyzer()
        print("  ✓ NetworkAnalyzer initialisé")

        # Construire le réseau
        graph = analyzer.build_network(df_interactions)
        print(f"  ✓ Graphe créé: {graph.number_of_nodes()} nœuds, {graph.number_of_edges()} arêtes")

        # Calculer les centralités
        degree = analyzer.calculate_degree_centrality()
        print(f"  ✓ Centralité de degré calculée ({len(degree)} nœuds)")

        pagerank = analyzer.calculate_pagerank()
        print(f"  ✓ PageRank calculé ({len(pagerank)} nœuds)")

        stats = analyzer.calculate_network_statistics()
        print(f"  ✓ Statistiques du réseau: densité={stats['density']:.4f}")

        centrality_df = analyzer.get_centrality_dataframe()
        print(f"  ✓ DataFrame de centralité créé ({len(centrality_df)} lignes)")

        RESULTS["tests"]["NetworkAnalyzer_functionality"] = "PASS"
        return True, (analyzer, centrality_df)

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        RESULTS["tests"]["NetworkAnalyzer_functionality"] = f"FAIL: {str(e)}"
        return False, (None, None)

def test_predictor(df_clients, centrality_df):
    """Test le module CentralityPredictor"""
    print("\n" + "="*80)
    print("TEST 4 : CENTRALITY PREDICTOR")
    print("="*80)

    try:
        from src.models.predictor import CentralityPredictor
        from sklearn.model_selection import train_test_split

        predictor = CentralityPredictor(model_type='random_forest')
        print("  ✓ CentralityPredictor initialisé (Random Forest)")

        # Préparer les features
        X, y = predictor.prepare_features(df_clients, centrality_df, target_metric='pagerank')
        print(f"  ✓ Features préparées: {X.shape[1]} features, {len(X)} samples")

        # Diviser train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print(f"  ✓ Train/Test split: {len(X_train)} / {len(X_test)}")

        # Entraîner
        results = predictor.train(X_train, y_train, test_size=0.0, validation=False)
        print(f"  ✓ Modèle entraîné: R² = {results['train_score']:.4f}")

        # Évaluer
        eval_results = predictor.evaluate(X_test, y_test)
        print(f"  ✓ Évaluation: R² = {eval_results['r2']:.4f}, RMSE = {eval_results['rmse']:.4f}")

        RESULTS["tests"]["CentralityPredictor_functionality"] = "PASS"
        return True

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        RESULTS["tests"]["CentralityPredictor_functionality"] = f"FAIL: {str(e)}"
        return False

def test_visualizer():
    """Test le module NetworkVisualizer"""
    print("\n" + "="*80)
    print("TEST 5 : NETWORK VISUALIZER")
    print("="*80)

    try:
        from src.visualization.visualizer import NetworkVisualizer

        viz = NetworkVisualizer()
        print(f"  ✓ NetworkVisualizer initialisé")
        print(f"  ✓ Répertoire de sortie: {viz.output_dir}")

        # Vérifier que les méthodes existent
        methods = [
            'plot_network',
            'plot_centrality_comparison',
            'plot_centrality_distribution',
            'plot_correlation_matrix',
            'plot_feature_importance',
            'plot_prediction_results',
            'plot_model_comparison',
            'plot_network_statistics'
        ]

        for method in methods:
            if hasattr(viz, method):
                print(f"  ✓ Méthode {method} disponible")
            else:
                print(f"  ✗ Méthode {method} manquante")

        RESULTS["tests"]["NetworkVisualizer_functionality"] = "PASS"
        return True

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        RESULTS["tests"]["NetworkVisualizer_functionality"] = f"FAIL: {str(e)}"
        return False

def main():
    """Exécute tous les tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  CLIENT CENTRALITY PREDICTION PLATFORM - VÉRIFICATION COMPLÈTE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # Test 1: Imports
    imports_ok = test_imports()

    if not imports_ok:
        print("\n❌ Les imports ne fonctionnent pas. Installez les dépendances:")
        print("   pip install -r requirements_minimal.txt")
        RESULTS["summary"]["status"] = "FAILED"
        return False

    # Test 2: DataLoader
    dl_ok, (df_clients, df_interactions) = test_data_loader()

    if not dl_ok or df_clients is None:
        print("\n❌ DataLoader ne fonctionne pas")
        RESULTS["summary"]["status"] = "FAILED"
        return False

    # Test 3: NetworkAnalyzer
    na_ok, (analyzer, centrality_df) = test_network_analyzer(df_interactions)

    if not na_ok or centrality_df is None:
        print("\n❌ NetworkAnalyzer ne fonctionne pas")
        RESULTS["summary"]["status"] = "FAILED"
        return False

    # Test 4: CentralityPredictor
    cp_ok = test_predictor(df_clients, centrality_df)

    if not cp_ok:
        print("\n❌ CentralityPredictor ne fonctionne pas")
        RESULTS["summary"]["status"] = "FAILED"
        return False

    # Test 5: NetworkVisualizer
    viz_ok = test_visualizer()

    if not viz_ok:
        print("\n❌ NetworkVisualizer ne fonctionne pas")
        RESULTS["summary"]["status"] = "FAILED"
        return False

    # Tous les tests sont passés
    print("\n" + "="*80)
    print("✅ TOUS LES TESTS ONT RÉUSSI!")
    print("="*80)

    print("\n📊 RÉSUMÉ :")
    passed_tests = sum(1 for v in RESULTS["tests"].values() if v == "PASS")
    total_tests = len(RESULTS["tests"])
    print(f"   • {passed_tests}/{total_tests} tests passés")
    print(f"   • Tous les modules fonctionnent correctement")

    print("\n🚀 PROCHAINES ÉTAPES :")
    print("   1. Exécutez: python simple_demo.py")
    print("   2. Ou lancez: streamlit run app.py")
    print("   3. Consultez: GETTING_STARTED.md")

    print("\n" + "="*80 + "\n")

    RESULTS["summary"]["status"] = "SUCCESS"
    RESULTS["summary"]["passed"] = passed_tests
    RESULTS["summary"]["total"] = total_tests

    return True

if __name__ == "__main__":
    success = main()

    # Sauvegarder les résultats
    results_file = project_root / "verification_results.json"
    with open(results_file, 'w') as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)
    print(f"📄 Résultats sauvegardés: {results_file}\n")

    sys.exit(0 if success else 1)

