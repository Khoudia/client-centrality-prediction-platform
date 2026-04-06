#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic rapide — vérification des imports et structure du projet.
"""
import sys
import os
from pathlib import Path

# Force UTF-8 output sur Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("DIAGNOSTIC PROJET - Hotel Aurore")
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
    print("  [OK] Tous les imports DataLoader OK")
    tests.append(True)
except Exception as e:
    print(f"  [ERREUR] DataLoader : {e}")
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
    print("  [OK] Tous les imports NetworkAnalyzer OK")
    tests.append(True)
except Exception as e:
    print(f"  [ERREUR] NetworkAnalyzer : {e}")
    tests.append(False)

# Test 3 : SatisfactionPredictor
print("\n[3/5] SatisfactionPredictor")
try:
    from src.models.predictor import (
        SatisfactionPredictor,
        CentralityPredictor,
    )
    print("  [OK] Tous les imports Predictor OK")
    tests.append(True)
except Exception as e:
    print(f"  [ERREUR] Predictor : {e}")
    tests.append(False)

# Test 4 : NetworkVisualizer
print("\n[4/5] NetworkVisualizer")
try:
    from src.visualization.visualizer import NetworkVisualizer
    print("  [OK] Import Visualizer OK")
    tests.append(True)
except Exception as e:
    print(f"  [ERREUR] Visualizer : {e}")
    tests.append(False)

# Test 5 : App.py
print("\n[5/5] Verification app.py (syntaxe)")
try:
    import ast
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()
    ast.parse(code)
    print("  [OK] Syntaxe OK (app.py executable avec Streamlit)")
    tests.append(True)
except Exception as e:
    print(f"  [ERREUR] app.py : {e}")
    tests.append(False)

# Résumé
print("\n" + "="*70)
if all(tests):
    print("[SUCCES] TOUS LES TESTS PASSES (5/5)")
    print("-> Pret pour : streamlit run app.py")
else:
    nb_err = sum(not t for t in tests)
    print(f"[ATTENTION] {nb_err} erreur(s) a corriger sur {len(tests)} tests")
    sys.exit(1)
print("="*70)

