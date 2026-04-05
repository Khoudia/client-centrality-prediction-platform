#!/usr/bin/env python3
"""Test ultra-rapide — 30 secondes max"""
import sys
sys.path.insert(0, '.')

print("1. Testing imports...")
try:
    from src.data.data_loader import build_final_dataset, _RAW_DIR, _PROCESSED_DIR
    print("   ✓ data_loader OK")
except Exception as e:
    print(f"   ✗ {e}"); sys.exit(1)

try:
    from src.network.network_analyzer import build_similarity_graph, compute_network_metrics
    print("   ✓ network_analyzer OK")
except Exception as e:
    print(f"   ✗ {e}"); sys.exit(1)

try:
    from src.models.predictor import SatisfactionPredictor
    print("   ✓ predictor OK")
except Exception as e:
    print(f"   ✗ {e}"); sys.exit(1)

try:
    from src.visualization.visualizer import NetworkVisualizer
    print("   ✓ visualizer OK")
except Exception as e:
    print(f"   ✗ {e}"); sys.exit(1)

print("\n2. Checking data files...")
import os
files = {
    "AvailPro": "data-projet-sorbonne/availpro_export.xlsx",
    "Booking (Excel)": "data-projet-sorbonne/données avis traités.xlsx",
    "Booking (CSV)": "data-projet-sorbonne/données avis booking.csv",
    "Expedia": "data-projet-sorbonne/expediareviews_from_2025-03-01_to_2026-03-01.csv",
}

for name, path in files.items():
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    size = f" ({os.path.getsize(path)/1024/1024:.1f}MB)" if exists else ""
    print(f"   {status} {name}{size}")

print("\n3. Loading dataset (5-10 sec)...")
try:
    df = build_final_dataset(save=True)
    print(f"   ✓ Dataset loaded: {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"   ✓ Client IDs: {df['client_id'].notna().sum()}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Building network graph (10-20 sec)...")
try:
    G, _ = build_similarity_graph(df, min_similarity=0.3, max_nodes=300)
    print(f"   ✓ Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n5. Computing network metrics...")
try:
    df_metrics = compute_network_metrics(G)
    print(f"   ✓ Metrics: {len(df_metrics)} clients × {len(df_metrics.columns)} metrics")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ PIPELINE VALIDATED - Ready for Streamlit!")
print("="*50)
print("\nNext: streamlit run app.py")

