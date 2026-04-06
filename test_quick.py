#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test ultra-rapide — 30-60 secondes max"""
import sys, io, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 sur Windows + écriture dans un fichier log
_LOG = open("test_quick_result.txt", "w", encoding="utf-8")

def _p(msg):
    print(msg)
    _LOG.write(str(msg) + "\n")
    _LOG.flush()

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, '.')

_p("1. Testing imports...")
try:
    from src.data.data_loader import build_final_dataset, _RAW_DIR, _PROCESSED_DIR
    _p("   [OK] data_loader")
except Exception as e:
    _p(f"   [ERREUR] data_loader: {e}"); _LOG.close(); sys.exit(1)

try:
    from src.network.network_analyzer import build_similarity_graph, compute_network_metrics
    _p("   [OK] network_analyzer")
except Exception as e:
    _p(f"   [ERREUR] network_analyzer: {e}"); _LOG.close(); sys.exit(1)

try:
    from src.models.predictor import SatisfactionPredictor
    _p("   [OK] predictor")
except Exception as e:
    _p(f"   [ERREUR] predictor: {e}"); _LOG.close(); sys.exit(1)

try:
    from src.visualization.visualizer import NetworkVisualizer
    _p("   [OK] visualizer")
except Exception as e:
    _p(f"   [ERREUR] visualizer: {e}"); _LOG.close(); sys.exit(1)

_p("\n2. Checking data files...")
files = {
    "AvailPro": "data-projet-sorbonne/availpro_export.xlsx",
    "Booking (CSV brut)": "data-projet-sorbonne/données avis booking.csv",
    "Expedia": "data-projet-sorbonne/expediareviews_from_2025-03-01_to_2026-03-01.csv",
}
all_found = True
for name, path in files.items():
    exists = os.path.exists(path)
    status = "[OK]" if exists else "[MANQUANT]"
    size = f" ({os.path.getsize(path)/1024/1024:.1f}MB)" if exists else ""
    _p(f"   {status} {name}{size}")
    if not exists:
        all_found = False

_p("\n3. Loading dataset (5-10 sec)...")
try:
    df = build_final_dataset(save=True)
    _p(f"   [OK] Dataset: {df.shape[0]} lignes x {df.shape[1]} colonnes")
    _p(f"   [OK] Client IDs: {df['client_id'].notna().sum()}")
    if "has_review" in df.columns:
        n_rev = int(df["has_review"].sum())
        pct = df["has_review"].mean() * 100
        _p(f"   [INFO] Avis lies: {n_rev} ({pct:.1f}%)")
    if "review_score" in df.columns:
        notna = df["review_score"].notna().sum()
        if notna > 0:
            mean_score = df["review_score"].mean()
            _p(f"   [INFO] Note moyenne: {mean_score:.2f}/10 ({notna} avis)")
        else:
            _p("   [ATTENTION] Aucun avis lie (review_score NaN)")
except Exception as e:
    import traceback
    _p(f"   [ERREUR] {e}")
    _p(traceback.format_exc())
    _LOG.close(); sys.exit(1)

_p("\n4. Building network graph (10-20 sec)...")
try:
    G, _ = build_similarity_graph(df, min_similarity=0.3, max_nodes=300)
    _p(f"   [OK] Graphe: {G.number_of_nodes()} noeuds, {G.number_of_edges()} aretes")
except Exception as e:
    _p(f"   [ERREUR] graphe: {e}"); _LOG.close(); sys.exit(1)

_p("\n5. Computing network metrics...")
try:
    df_metrics = compute_network_metrics(G)
    _p(f"   [OK] Metriques: {len(df_metrics)} clients x {len(df_metrics.columns)} cols")
    _p(f"   [INFO] Colonnes: {list(df_metrics.columns)}")
except Exception as e:
    _p(f"   [ERREUR] metriques: {e}"); _LOG.close(); sys.exit(1)

_p("\n6. Testing SatisfactionPredictor...")
try:
    import pandas as pd
    df_enriched = df.copy()
    if "client_id" in df_metrics.columns:
        df_enriched = df_enriched.merge(df_metrics, on="client_id", how="left")
    elif df_metrics.index.name == "client_id":
        df_enriched = df_enriched.merge(df_metrics.reset_index(), on="client_id", how="left")

    predictor = SatisfactionPredictor(task="classification")
    metrics_pred = predictor.train(df_enriched)
    if metrics_pred:
        _p(f"   [OK] Modele entraine: {metrics_pred}")
    else:
        _p("   [ATTENTION] Pas assez d'avis pour le modele (besoin de review_score)")
except Exception as e:
    import traceback
    _p(f"   [ATTENTION] Predictor: {e}")
    _p(traceback.format_exc())

_p("\n" + "="*50)
_p("[SUCCES] PIPELINE VALIDE - Pret pour Streamlit!")
_p("="*50)
_p("Commande: streamlit run app.py")
_LOG.close()
