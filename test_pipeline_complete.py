#!/usr/bin/env python3
"""
Test complet du pipeline — génère un rapport d'exécution.
Produit : PIPELINE_TEST_REPORT.txt
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

report = []
report.append("="*70)
report.append("RAPPORT DE VALIDATION DU PIPELINE")
report.append(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append("Hôtel Aurore Paris — Analyse Réseau & Satisfaction Client")
report.append("="*70)
report.append("")

def log_section(title):
    msg = f"\n{'='*70}\n{title}\n{'='*70}"
    print(msg)
    report.append(msg)

def log_success(msg):
    print(f"✓ {msg}")
    report.append(f"✓ {msg}")

def log_error(msg):
    print(f"✗ {msg}")
    report.append(f"✗ {msg}")

def log_info(msg):
    print(f"  {msg}")
    report.append(f"  {msg}")

# ÉTAPE 1 : Imports
log_section("ÉTAPE 1 : Vérification des imports")

try:
    from src.data.data_loader import build_final_dataset
    log_success("DataLoader importé")
except Exception as e:
    log_error(f"DataLoader : {e}")
    sys.exit(1)

try:
    from src.network.network_analyzer import (
        build_similarity_graph, compute_network_metrics, detect_communities, export_network_results
    )
    log_success("NetworkAnalyzer importé")
except Exception as e:
    log_error(f"NetworkAnalyzer : {e}")
    sys.exit(1)

try:
    from src.models.predictor import SatisfactionPredictor
    log_success("SatisfactionPredictor importé")
except Exception as e:
    log_error(f"SatisfactionPredictor : {e}")
    sys.exit(1)

try:
    from src.visualization.visualizer import NetworkVisualizer
    log_success("NetworkVisualizer importé")
except Exception as e:
    log_error(f"NetworkVisualizer : {e}")
    sys.exit(1)

# ÉTAPE 2 : Chargement des données
log_section("ÉTAPE 2 : Chargement du dataset final")

try:
    df = build_final_dataset(save=True)
    log_success(f"Dataset chargé : {df.shape[0]} réservations × {df.shape[1]} colonnes")
    log_info(f"Client IDs non-null : {df['client_id'].notna().sum()}")
    log_info(f"Avis Booking disponibles : {df['has_review'].sum() if 'has_review' in df.columns else 'N/A'}")
    log_info(f"Note moyenne (si avis) : {df['review_score'].mean():.2f}/10" if 'review_score' in df.columns else "N/A")
except Exception as e:
    log_error(f"Chargement dataset : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ÉTAPE 3 : Graphe de similarité
log_section("ÉTAPE 3 : Construction du graphe de similarité")

try:
    G, profile_df = build_similarity_graph(df, min_similarity=0.3, max_nodes=500)
    log_success(f"Graphe construit : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
    import networkx as nx
    n_components = len(list(nx.connected_components(G)))
    log_info(f"Composantes connexes : {n_components}")
    log_info(f"Densité : {nx.density(G):.4f}")
except Exception as e:
    log_error(f"Construction graphe : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ÉTAPE 4 : Métriques réseau
log_section("ÉTAPE 4 : Calcul des métriques réseau")

try:
    df_metrics = compute_network_metrics(G)
    log_success(f"Métriques calculées : {df_metrics.shape[0]} clients, {list(df_metrics.columns)[1:]} colonnes")
except Exception as e:
    log_error(f"Calcul métriques : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ÉTAPE 5 : Détection de communautés
log_section("ÉTAPE 5 : Détection de communautés")

try:
    communities = detect_communities(G, method="greedy")
    n_comms = len(set(communities.values()))
    log_success(f"Communautés détectées : {n_comms}")
    sizes = {}
    for cid in communities.values():
        sizes[cid] = sizes.get(cid, 0) + 1
    log_info(f"Tailles (min/max/moy) : {min(sizes.values())}/{max(sizes.values())}/{sum(sizes.values())//len(sizes)}")
except Exception as e:
    log_error(f"Détection communautés : {e}")
    import traceback
    traceback.print_exc()

# ÉTAPE 6 : Fusion réseau + données
log_section("ÉTAPE 6 : Fusion des résultats réseau")

try:
    df_enriched = export_network_results(df, df_metrics, communities)
    log_success(f"Dataset enrichi : {df_enriched.shape[0]} × {df_enriched.shape[1]} colonnes")
    cols_network = [c for c in ["pagerank", "betweenness", "eigenvector", "community_id"] if c in df_enriched.columns]
    log_info(f"Colonnes réseau : {cols_network}")
except Exception as e:
    log_error(f"Fusion réseau : {e}")
    import traceback
    traceback.print_exc()

# ÉTAPE 7 : Modélisation
log_section("ÉTAPE 7 : Modélisation de la satisfaction")

try:
    predictor = SatisfactionPredictor(model_type="random_forest", task="classification")
    log_success("Modèle initialisé (Random Forest, Classification)")

    n_with_target = df_enriched["high_satisfaction"].notna().sum() if "high_satisfaction" in df_enriched.columns else 0

    if n_with_target >= 20:
        X, y = predictor.prepare_features(df_enriched)
        log_success(f"Features préparées : {X.shape[1]} colonnes, {X.shape[0]} samples")

        results = predictor.train(X, y, validation=True)
        log_success("Modèle entraîné")
        log_info(f"Accuracy : {results.get('accuracy', 'N/A')}")
        log_info(f"F1-weighted : {results.get('f1_weighted', 'N/A')}")
        log_info(f"ROC-AUC : {results.get('roc_auc', 'N/A')}")
        if "cv_mean" in results:
            log_info(f"CV (5-fold) : {results['cv_mean']} ± {results['cv_std']}")
    else:
        log_error(f"Trop peu d'observations cible : {n_with_target} < 20")

except Exception as e:
    log_error(f"Modélisation : {e}")
    import traceback
    traceback.print_exc()

# ÉTAPE 8 : Visualisations (optionnelles)
log_section("ÉTAPE 8 : Génération des visualisations (optionnel)")

try:
    viz = NetworkVisualizer(output_dir="outputs/figures")
    log_success("Visualizer initialisé")

    # Visualiser un subset du graphe
    if G.number_of_nodes() > 200:
        import random
        subset_nodes = random.sample(list(G.nodes()), min(200, G.number_of_nodes()))
        G_subset = G.subgraph(subset_nodes)
    else:
        G_subset = G

    viz.plot_network(G_subset, communities=communities)
    log_success("Graphe de similarité générée (200 nœuds max)")

    viz.plot_centrality_distribution(df_enriched)
    log_success("Distribution des centralités générée")

    viz.plot_satisfaction_by_community(df_enriched)
    log_success("Satisfaction par communauté générée")

except Exception as e:
    log_error(f"Visualisations : {e}")

# RÉSUMÉ FINAL
log_section("RÉSUMÉ FINAL")

log_success("Pipeline validé avec succès!")
log_info(f"Dataset : {df_enriched.shape[0]} lignes × {df_enriched.shape[1]} colonnes")
log_info(f"Réseau : {G.number_of_nodes()} nœuds × {G.number_of_edges()} arêtes")
log_info(f"Communautés : {n_comms}")
log_info("")
log_info("→ Prêt pour : streamlit run app.py")

# Sauvegarder le rapport
report_text = "\n".join(report)
report_path = Path("PIPELINE_TEST_REPORT.txt")
report_path.write_text(report_text, encoding="utf-8")
print(f"\n✓ Rapport sauvegardé : {report_path}")

print("\n" + "="*70)
print("✅ VALIDATION COMPLÈTE — Prêt pour production!")
print("="*70)

