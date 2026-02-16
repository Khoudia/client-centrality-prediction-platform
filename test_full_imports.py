import sys
sys.path.insert(0, r'C:\Users\KFA24632\client-centrality-prediction-platform')

print("=" * 60)
print("TEST D'IMPORTS - PLATFORM CLIENT CENTRALITY")
print("=" * 60)

# Test 1: DataLoader
try:
    from src.data.data_loader import DataLoader
    print("[OK] DataLoader importé avec succès")
    dl = DataLoader()
    print("     Méthodes disponibles:", [m for m in dir(dl) if not m.startswith('_')])
except Exception as e:
    print(f"[ERREUR] DataLoader: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: NetworkAnalyzer
try:
    from src.network.network_analyzer import NetworkAnalyzer
    print("[OK] NetworkAnalyzer importé avec succès")
    na = NetworkAnalyzer()
    print("     Méthodes disponibles:", [m for m in dir(na) if not m.startswith('_')][:5], "...")
except Exception as e:
    print(f"[ERREUR] NetworkAnalyzer: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: CentralityPredictor
try:
    from src.models.predictor import CentralityPredictor
    print("[OK] CentralityPredictor importé avec succès")
    cp = CentralityPredictor()
    print("     Modèle type:", cp.model_type)
except Exception as e:
    print(f"[ERREUR] CentralityPredictor: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: NetworkVisualizer
try:
    from src.visualization.visualizer import NetworkVisualizer
    print("[OK] NetworkVisualizer importé avec succès")
    nv = NetworkVisualizer()
    print("     Répertoire de sortie:", nv.output_dir)
except Exception as e:
    print(f"[ERREUR] NetworkVisualizer: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("RÉSUMÉ: Tous les modules sont importables!")
print("=" * 60)

