"""Test complet du pipeline hôtelier — données réelles."""
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── 1. Data Loader ────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 1 — DATASET FINAL")
print("=" * 60)
df = pd.read_csv("data/processed/hotel_dataset_final.csv")
print(f"Shape        : {df.shape}")
print(f"Clients      : {df['client_id'].nunique()}")
print(f"Avec avis    : {df['has_review'].sum()}")
if "review_score" in df.columns:
    print(f"Note moy.    : {df['review_score'].mean():.2f}/10")
print(f"Canaux       : {df['channel_group'].value_counts().to_dict()}")
print(f"Chambres     : {df['room_segment'].value_counts().to_dict()}")

# ── 2. Réseau ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2 — RÉSEAU DE SIMILARITÉ")
print("=" * 60)
from src.network.network_analyzer import NetworkAnalyzer
na = NetworkAnalyzer()
G = na.build_similarity_graph(df, min_similarity=0.3, max_nodes=500)
print(f"Nœuds        : {G.number_of_nodes()}")
print(f"Arêtes       : {G.number_of_edges()}")

comms = na.detect_communities(method="greedy")
print(f"Communautés  : {len(set(comms.values()))}")

df_m = na.compute_network_metrics()
print(f"Métriques    : {list(df_m.columns)}")

stats = na.calculate_network_statistics()
print(f"Densité      : {stats.get('density'):.6f}")
print(f"Composantes  : {stats.get('n_connected_components')}")
if "modularity" in stats:
    print(f"Modularité   : {stats['modularity']:.4f}")

df_e = na.export_network_results(df)
print(f"Dataset enrichi : {df_e.shape}")

# ── 3. Modèle satisfaction ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3 — MODÈLE DE SATISFACTION")
print("=" * 60)
from src.models.predictor import SatisfactionPredictor
pred = SatisfactionPredictor(model_type="random_forest", task="classification")
X, y = pred.prepare_features(df_e)
print(f"Features     : {pred.feature_names}")
print(f"Observations : {len(X)}")
print(f"Classes      : {y.value_counts().to_dict()}")
results = pred.train(X, y, validation=True)
print(f"Accuracy     : {results.get('accuracy')}")
print(f"F1-weighted  : {results.get('f1_weighted')}")
print(f"ROC-AUC      : {results.get('roc_auc')}")
print(f"CV-mean      : {results.get('cv_mean')}")

fi = pred.get_feature_importance(top_n=10)
print("\nTop features :")
print(fi.to_string(index=False))

# ── 4. Visualiseur ────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4 — VISUALISATIONS")
print("=" * 60)
from src.visualization.visualizer import NetworkVisualizer
viz = NetworkVisualizer()

fig1 = viz.plot_network(G, communities=comms, save=True)
print("✅ Réseau sauvegardé")

fig2 = viz.plot_centrality_distribution(df_m, save=True)
print("✅ Distribution centralités")

fig3 = viz.plot_satisfaction_by_channel(df_e, save=True)
print("✅ Satisfaction par canal")

fig4 = viz.plot_satisfaction_by_room(df_e, save=True)
print("✅ Satisfaction par chambre")

fig5 = viz.plot_feature_importance(fi, save=True)
print("✅ Importance des features")

fig6 = viz.plot_correlation_matrix(df_e, save=True)
print("✅ Matrice de corrélation")

print("\n" + "=" * 60)
print("✅ PIPELINE COMPLET — SUCCÈS")
print("=" * 60)

