#!/usr/bin/env python3
"""
Diagnostic rapide — vérification des imports et structure du projet.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("DIAGNOSTIC PROJET — Hôtel Aurore")
print("="*70)

tests = []

# Test 1 : DataLoader
print("\n[1/5] DataLoader")
try:
    from src.data.data_loader import (
        build_final_dataset,
        DataLoader,
        load_availpro_data,
        load_booking_reviews,
        load_expedia_reviews,
        clean_reservations,
        clean_booking_reviews,
        clean_expedia_reviews,
        merge_reviews_with_reservations,
        _RAW_DIR,
        _PROCESSED_DIR,
    )
    print("  ✓ Tous les imports OK")
    tests.append(True)
except Exception as e:
    print(f"  ✗ ERREUR : {e}")
    tests.append(False)

# Test 2 : NetworkAnalyzer
print("\n[2/5] NetworkAnalyzer")
try:
    from src.network.network_analyzer import (
        NetworkAnalyzer,
        build_similarity_graph,
        compute_network_metrics,
        detect_communities,
        export_network_results,
    )
    print("  ✓ Tous les imports OK")
    tests.append(True)
except Exception as e:
    print(f"  ✗ ERREUR : {e}")
    tests.append(False)

# Test 3 : SatisfactionPredictor
print("\n[3/5] SatisfactionPredictor")
try:
    from src.models.predictor import (
        SatisfactionPredictor,
        CentralityPredictor,
    )
    print("  ✓ Tous les imports OK")
    tests.append(True)
except Exception as e:
    print(f"  ✗ ERREUR : {e}")
    tests.append(False)

# Test 4 : NetworkVisualizer
print("\n[4/5] NetworkVisualizer")
try:
    from src.visualization.visualizer import NetworkVisualizer
    print("  ✓ Import OK")
    tests.append(True)
except Exception as e:
    print(f"  ✗ ERREUR : {e}")
    tests.append(False)

# Test 5 : App.py
print("\n[5/5] Vérification app.py (syntaxe)")
try:
    import ast
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()
    ast.parse(code)
    print("  ✓ Syntaxe OK (app.py exécutable avec Streamlit)")
    tests.append(True)
except Exception as e:
    print(f"  ✗ ERREUR : {e}")
    tests.append(False)

# Résumé
print("\n" + "="*70)
if all(tests):
    print("✅ TOUS LES TESTS PASSÉS")
    print("→ Prêt pour : streamlit run app.py")
else:
    print(f"⚠️ {sum(not t for t in tests)} erreur(s) à corriger")
    sys.exit(1)
print("="*70)

