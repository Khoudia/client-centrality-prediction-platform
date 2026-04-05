"""
Script de validation du pipeline complet — Hôtel Aurore Paris.
Redirige les résultats vers pipeline_test_results.txt pour debug.
"""
import sys
import os
import logging

# Forcer le répertoire courant
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

# Logger vers fichier
logging.basicConfig(
    level=logging.WARNING,  # silencieux sauf erreurs
    format="%(levelname)s %(message)s"
)

OUT = open("pipeline_test_results.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    OUT.write(msg + "\n")
    OUT.flush()

try:
    # ── 1. Dataset ───────────────────────────────────────────────────────────
    import pandas as pd
    df = pd.read_csv("data/processed/hotel_dataset_final.csv")
    log(f"[STEP1] Dataset : {df.shape[0]} lignes x {df.shape[1]} cols")
    log(f"[STEP1] Clients uniques   : {df['client_id'].nunique()}")
    log(f"[STEP1] Avec avis         : {int(df['has_review'].sum())}")
    log(f"[STEP1] Note moy.         : {df['review_score'].mean():.2f}/10")
    log(f"[STEP1] high_satisfaction : {int(df['high_satisfaction'].sum())}")
    log(f"[STEP1] Canaux            : {df['channel_group'].value_counts().to_dict()}")
    log(f"[STEP1] Chambres          : {df['room_segment'].value_counts().to_dict()}")

    # ── 2. Réseau ────────────────────────────────────────────────────────────
    from src.network.network_analyzer import NetworkAnalyzer
    na = NetworkAnalyzer()
    G = na.build_similarity_graph(df, min_similarity=0.3, max_nodes=300)
    comms = na.detect_communities(method="greedy")
    df_m = na.compute_network_metrics()
    df_e = na.export_network_results(df)
    stats = na.calculate_network_statistics()
    log(f"[STEP2] Nœuds             : {G.number_of_nodes()}")
    log(f"[STEP2] Arêtes            : {G.number_of_edges()}")
    log(f"[STEP2] Communautés       : {len(set(comms.values()))}")
    log(f"[STEP2] Densité           : {stats.get('density', 'N/A')}")
    log(f"[STEP2] Clustering moyen  : {stats.get('average_clustering', 'N/A')}")
    log(f"[STEP2] Modularité        : {stats.get('modularity', 'N/A')}")
    log(f"[STEP2] Dataset enrichi   : {df_e.shape}")
    log(f"[STEP2] Métriques         : {[c for c in df_m.columns if c != 'client_id']}")

    # ── 3. Modèle ────────────────────────────────────────────────────────────
    from src.models.predictor import SatisfactionPredictor

    pred = SatisfactionPredictor(model_type="random_forest", task="classification")
    X, y = pred.prepare_features(df_e)
    log(f"[STEP3] Obs. d'entraîn.   : {len(X)}")
    log(f"[STEP3] Classes           : {y.value_counts().to_dict()}")
    log(f"[STEP3] Nb features       : {len(pred.feature_names)}")
    log(f"[STEP3] Features          : {pred.feature_names}")

    res = pred.train(X, y, validation=True)
    log(f"[STEP3] Accuracy          : {res.get('accuracy')}")
    log(f"[STEP3] F1-weighted       : {res.get('f1_weighted')}")
    log(f"[STEP3] ROC-AUC           : {res.get('roc_auc')}")
    log(f"[STEP3] CV-mean (5-fold)  : {res.get('cv_mean')}")
    log(f"[STEP3] CV-std            : {res.get('cv_std')}")

    fi = pred.get_feature_importance(top_n=10)
    log("[STEP3] Top 10 features :")
    for _, r in fi.iterrows():
        log(f"         {r['feature']:<30} {r['importance']:.4f}")

    # Comparaison multi-modèles
    pred2 = SatisfactionPredictor(task="classification")
    X2, y2 = pred2.prepare_features(df_e)
    multi = pred2.train_all_models(X2, y2)
    log("[STEP3] Comparaison modèles :")
    for mname, mres in multi.items():
        if "error" not in mres:
            log(f"         {mname:<22} acc={mres.get('accuracy','?')}  f1={mres.get('f1_weighted','?')}  auc={mres.get('roc_auc','?')}")
        else:
            log(f"         {mname:<22} ERREUR: {mres['error']}")

    # ── 4. Visualisations ────────────────────────────────────────────────────
    from src.visualization.visualizer import NetworkVisualizer
    viz = NetworkVisualizer()

    figs = [
        ("plot_network",                  lambda: viz.plot_network(G, communities=comms, save=True)),
        ("plot_centrality_distribution",  lambda: viz.plot_centrality_distribution(df_m, save=True)),
        ("plot_satisfaction_by_channel",  lambda: viz.plot_satisfaction_by_channel(df_e, save=True)),
        ("plot_satisfaction_by_room",     lambda: viz.plot_satisfaction_by_room(df_e, save=True)),
        ("plot_satisfaction_by_community",lambda: viz.plot_satisfaction_by_community(df_e, save=True)),
        ("plot_revenue_by_community",     lambda: viz.plot_revenue_by_community(df_e, save=True)),
        ("plot_top_central_profiles",     lambda: viz.plot_top_central_profiles(df_e, save=True)),
        ("plot_feature_importance",       lambda: viz.plot_feature_importance(fi, save=True)),
        ("plot_correlation_matrix",       lambda: viz.plot_correlation_matrix(df_e, save=True)),
        ("plot_network_statistics",       lambda: viz.plot_network_statistics(stats, save=True)),
        ("plot_model_comparison",         lambda: viz.plot_model_comparison(multi, save=True)),
    ]

    for name, fn in figs:
        try:
            fn()
            log(f"[STEP4] OK  {name}")
        except Exception as e:
            log(f"[STEP4] ERR {name}: {e}")

    log("\n=== PIPELINE COMPLET — SUCCÈS ===")

except Exception as exc:
    import traceback
    log(f"\n[ERREUR FATALE] {exc}")
    log(traceback.format_exc())

finally:
    OUT.close()
    print("Résultats écrits dans pipeline_test_results.txt")

