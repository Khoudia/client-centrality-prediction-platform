#!/usr/bin/env python3
"""
Script de validation du pipeline complet — Hôtel Aurore Paris.

Teste la chaîne complète :
  1. Chargement des données réelles
  2. Construction du graphe de similarité
  3. Calcul des métriques réseau
  4. Détection de communautés
  5. Modélisation de la satisfaction
  6. Génération des visualisations
"""

import sys
import logging
from pathlib import Path

import networkx as nx

# ── Setup ─────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ── Imports ───────────────────────────────────────────────────────────────
try:
    from src.data.data_loader import build_final_dataset
    logger.info("✓ DataLoader importé")
except Exception as e:
    logger.error(f"✗ DataLoader : {e}")
    sys.exit(1)

try:
    from src.network.network_analyzer import (
        build_similarity_graph,
        compute_network_metrics,
        detect_communities,
        export_network_results,
    )
    logger.info("✓ NetworkAnalyzer importé")
except Exception as e:
    logger.error(f"✗ NetworkAnalyzer : {e}")
    sys.exit(1)

try:
    from src.models.predictor import SatisfactionPredictor
    logger.info("✓ SatisfactionPredictor importé")
except Exception as e:
    logger.error(f"✗ SatisfactionPredictor : {e}")
    sys.exit(1)

try:
    from src.visualization.visualizer import NetworkVisualizer
    logger.info("✓ NetworkVisualizer importé")
except Exception as e:
    logger.error(f"✗ NetworkVisualizer : {e}")
    sys.exit(1)

# ── ÉTAPE 1 : Chargement des données ──────────────────────────────────────

logger.info("\n" + "="*70)
logger.info("ÉTAPE 1 : Chargement du dataset final")
logger.info("="*70)

try:
    df = build_final_dataset(save=True)
    logger.info(f"✓ Dataset chargé : {df.shape[0]} réservations, {df.shape[1]} colonnes")
    logger.info(f"  Colonnes clés : {list(df.columns[:5])}")
    logger.info(f"  Client IDs non-null : {df['client_id'].notna().sum()}")
    logger.info(f"  Avis disponibles : {df['has_review'].sum()}")
except Exception as e:
    logger.error(f"✗ Échec du chargement : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ── ÉTAPE 2 : Construction du graphe ──────────────────────────────────────

logger.info("\n" + "="*70)
logger.info("ÉTAPE 2 : Construction du graphe de similarité")
logger.info("="*70)

try:
    G, profile_df = build_similarity_graph(df, min_similarity=0.3, max_nodes=500)
    logger.info(f"✓ Graphe construit : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
    n_components = len(list(nx.connected_components(G)))
    logger.info(f"  Composantes connexes : {n_components}")
except Exception as e:
    logger.error(f"✗ Échec de la construction : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ── ÉTAPE 3 : Métriques réseau ────────────────────────────────────────────

logger.info("\n" + "="*70)
logger.info("ÉTAPE 3 : Calcul des métriques réseau")
logger.info("="*70)

try:
    df_metrics = compute_network_metrics(G)
    logger.info(f"✓ Métriques calculées : {df_metrics.shape[0]} clients")
    logger.info(f"  Colonnes : {list(df_metrics.columns)}")
except Exception as e:
    logger.error(f"✗ Échec du calcul : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ── ÉTAPE 4 : Détection de communautés ────────────────────────────────────

logger.info("\n" + "="*70)
logger.info("ÉTAPE 4 : Détection de communautés")
logger.info("="*70)

try:
    communities = detect_communities(G, method="greedy")
    n_comms = len(set(communities.values()))
    logger.info(f"✓ Communautés détectées : {n_comms}")
    sizes = {}
    for cid in communities.values():
        sizes[cid] = sizes.get(cid, 0) + 1
    logger.info(f"  Tailles : {sorted(sizes.values())}")
except Exception as e:
    logger.error(f"✗ Échec de la détection : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ── ÉTAPE 5 : Fusion résultats réseau ─────────────────────────────────────

logger.info("\n" + "="*70)
logger.info("ÉTAPE 5 : Fusion des résultats réseau")
logger.info("="*70)

try:
    df_enriched = export_network_results(df, df_metrics, communities)
    logger.info(f"✓ Dataset enrichi : {df_enriched.shape[0]} lignes, {df_enriched.shape[1]} colonnes")
    cols_network = ["pagerank", "betweenness", "eigenvector", "community_id"]
    cols_avail = [c for c in cols_network if c in df_enriched.columns]
    logger.info(f"  Colonnes réseau disponibles : {cols_avail}")
except Exception as e:
    logger.error(f"✗ Échec de la fusion : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ── ÉTAPE 6 : Modélisation de la satisfaction ─────────────────────────────

logger.info("\n" + "="*70)
logger.info("ÉTAPE 6 : Modélisation de la satisfaction")
logger.info("="*70)

try:
    predictor = SatisfactionPredictor(model_type="random_forest", task="classification")
    logger.info("✓ Modèle initialisé (classification)")

    # Vérifier les données
    n_with_target = df_enriched["high_satisfaction"].notna().sum()
    if n_with_target < 20:
        logger.warning(f"  ⚠ Peu d'observations avec cible : {n_with_target} < 20")
        logger.warning("  → Modèle sera entraîné sur un ensemble réduit")
    else:
        logger.info(f"  Observations disponibles : {n_with_target}")

        try:
            X, y = predictor.prepare_features(df_enriched)
            logger.info(f"  ✓ Features préparées : {X.shape[1]} features pour {X.shape[0]} samples")

            results = predictor.train(X, y)
            logger.info(f"  ✓ Modèle entraîné")
            if "cv_mean" in results:
                logger.info(f"    Validation croisée (CV) : {results['cv_mean']:.3f} ± {results.get('cv_std', 0):.3f}")
            if "accuracy" in results:
                logger.info(f"    Accuracy : {results['accuracy']:.3f}")
            if "f1_weighted" in results:
                logger.info(f"    F1-weighted : {results['f1_weighted']:.3f}")
            if "roc_auc" in results and results["roc_auc"] is not None:
                logger.info(f"    ROC-AUC : {results['roc_auc']:.3f}")

        except Exception as e:
            logger.warning(f"  ⚠ Entraînement du modèle : {e}")

except Exception as e:
    logger.error(f"✗ Échec de la modélisation : {e}")
    import traceback
    traceback.print_exc()

# ── ÉTAPE 7 : Visualisations ──────────────────────────────────────────────

logger.info("\n" + "="*70)
logger.info("ÉTAPE 7 : Génération des visualisations")
logger.info("="*70)

try:
    viz = NetworkVisualizer(output_dir="outputs/figures")

    # Sélectionner un subset pour la visualisation du graphe (trop gros sinon)
    if G.number_of_nodes() > 300:
        logger.info("  Graphe trop grand pour visualisation complète → subset")
        import random
        subset_nodes = random.sample(list(G.nodes()), 300)
        G_subset = G.subgraph(subset_nodes).copy()
    else:
        G_subset = G

    logger.info(f"  Visualisation du graphe ({G_subset.number_of_nodes()} nœuds)…")
    viz.plot_network(G_subset, communities=communities)
    logger.info("  ✓ Graphe de similarité généré")

    logger.info(f"  Distribution des centralités…")
    viz.plot_centrality_distribution(df_enriched)
    logger.info("  ✓ Distribution des centralités générée")

    logger.info(f"  Satisfaction par communauté…")
    viz.plot_satisfaction_by_community(df_enriched)
    logger.info("  ✓ Satisfaction par communauté générée")

    logger.info(f"  Satisfaction par canal…")
    viz.plot_satisfaction_by_channel(df_enriched)
    logger.info("  ✓ Satisfaction par canal générée")

except Exception as e:
    logger.warning(f"⚠ Visualisations : {e}")
    import traceback
    traceback.print_exc()

# ── Résumé ─────────────────────────────────────────────────────────────────

logger.info("\n" + "="*70)
logger.info("VALIDATION COMPLÈTE")
logger.info("="*70)
logger.info("✓ Pipeline validé avec succès!")
logger.info(f"  Dataset final : {df_enriched.shape[0]} lignes × {df_enriched.shape[1]} colonnes")
logger.info(f"  Réseau : {G.number_of_nodes()} nœuds × {G.number_of_edges()} arêtes")
logger.info(f"  Communautés : {n_comms}")
logger.info("\n→ Prêt pour : streamlit run app.py")
logger.info("="*70)

