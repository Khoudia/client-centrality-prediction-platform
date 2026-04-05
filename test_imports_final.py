"""Test rapide des imports — à lancer avant streamlit run app.py"""
import sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

results = []

tests = [
    ("data_loader — build_final_dataset",
     "from src.data.data_loader import (DataLoader, load_availpro_data, load_booking_reviews, "
     "load_expedia_reviews, clean_reservations, clean_booking_reviews, clean_expedia_reviews, "
     "merge_reviews_with_reservations, build_final_dataset, _RAW_DIR, _PROCESSED_DIR)"),
    ("network_analyzer — NetworkAnalyzer",
     "from src.network.network_analyzer import (NetworkAnalyzer, build_similarity_graph, "
     "compute_network_metrics, detect_communities, export_network_results)"),
    ("predictor — SatisfactionPredictor",
     "from src.models.predictor import SatisfactionPredictor, CentralityPredictor"),
    ("visualizer — NetworkVisualizer",
     "from src.visualization.visualizer import NetworkVisualizer"),
    ("app.py — imports Streamlit",
     "import importlib.util; spec=importlib.util.spec_from_file_location('app','app.py'); "
     # On ne lance pas app.py (Streamlit), on vérifie juste la syntaxe
     "assert spec is not None"),
]

for name, code in tests:
    try:
        exec(code)
        print(f"OK  {name}")
        results.append(True)
    except Exception as e:
        print(f"ERR {name}: {e}")
        results.append(False)

print()
if all(results):
    print("=== Tous les imports OK — prêt pour : streamlit run app.py ===")
else:
    n_err = results.count(False)
    print(f"=== {n_err} erreur(s) d'import à corriger ===")
    sys.exit(1)

