"""
Application Streamlit — Analyse Réseau & Satisfaction Client
Hôtel Aurore Paris Gare de Lyon

Pages :
  1. 🏠 Accueil
  2. 📂 Chargement des données
  3. 🧹 Préparation & Nettoyage
  4. 🕸️ Analyse Réseau
  5. 🤖 Satisfaction & Modélisation
  6. 📊 Visualisations
  7. 💾 Export des résultats
"""

import sys
import io
import logging
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# ── Chemin src ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from src.data.data_loader import (
    DataLoader,
    load_availpro_data,
    load_booking_reviews,
    load_expedia_reviews,
    clean_reservations,
    clean_booking_reviews,
    clean_expedia_reviews,
    merge_reviews_with_reservations,
    _PROCESSED_DIR,
    _RAW_DIR,
)
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import SatisfactionPredictor
from src.visualization.visualizer import NetworkVisualizer

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config page ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hôtel Aurore — Analyse & Satisfaction",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-header { font-size:2.2rem; color:#1f3c88; font-weight:700; text-align:center; margin-bottom:1rem; }
.kpi-box { background:#f4f6fb; padding:0.8rem 1.2rem; border-radius:8px; border-left:4px solid #1f3c88; }
.section-title { color:#1f3c88; font-size:1.3rem; font-weight:600; margin-top:1rem; }
/* Scoring panel styles */
.score-panel { background:linear-gradient(135deg,#1f3c88 0%,#2d5be3 100%);
    color:white; padding:1.5rem; border-radius:12px; text-align:center; margin-bottom:1rem; }
.score-value { font-size:3.5rem; font-weight:800; }
.score-label { font-size:1.1rem; opacity:0.9; margin-top:0.3rem; }
.level-badge-green  { background:#27ae60; color:white; padding:0.4rem 1rem; border-radius:20px; font-weight:600; }
.level-badge-yellow { background:#f39c12; color:white; padding:0.4rem 1rem; border-radius:20px; font-weight:600; }
.level-badge-orange { background:#e67e22; color:white; padding:0.4rem 1rem; border-radius:20px; font-weight:600; }
.level-badge-red    { background:#e74c3c; color:white; padding:0.4rem 1rem; border-radius:20px; font-weight:600; }
.recep-msg { background:#eaf4fb; border-left:4px solid #2980b9;
    padding:1rem 1.2rem; border-radius:8px; font-size:0.95rem; line-height:1.6; }
.review-phrase { background:#f8f9fa; border-radius:6px; padding:0.6rem 1rem;
    margin:0.3rem 0; font-style:italic; color:#444; }
.factor-good { color:#27ae60; font-weight:600; }
.factor-warn { color:#e67e22; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _ss(key: str, default=None):
    """Raccourci session_state."""
    return st.session_state.get(key, default)


def _set(key: str, value):
    st.session_state[key] = value


def _first_available_df(*keys: str):
    """Retourne le premier DataFrame disponible en session_state."""
    for key in keys:
        value = _ss(key)
        if value is not None:
            return value
    return None


def _load_uploaded_with_loader(uploaded_file, suffix: str, loader_func):
    """Passe un fichier uploadé par un parseur robuste basé sur un chemin temporaire."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = Path(tmp.name)
    try:
        return loader_func(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    return buf.getvalue()


def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


# ── Initialisation session ────────────────────────────────────────────────────
for key, default in [
    ("data_loader",       None),
    ("network_analyzer",  None),
    ("predictor",         None),
    ("visualizer",        None),
    ("df_raw_res",        None),
    ("df_raw_booking",    None),
    ("df_raw_expedia",    None),
    ("df_clean_res",      None),
    ("df_clean_booking",  None),
    ("df_clean_expedia",  None),
    ("df_final",          None),
    ("graph",             None),
    ("df_metrics",        None),
    ("communities",       {}),
    ("df_enriched",       None),
    ("X_train",           None),
    ("X_test",            None),
    ("y_train",           None),
    ("y_test",            None),
    ("eval_results",      None),
    ("multi_results",     None),
    ("predictor_obj",     None),
    ("current_task_type", "classification"),
    # Onglet Scoring Nouveau Client
    ("scoring_result",    None),
    ("scoring_dict",      None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state["visualizer"] is None:
    st.session_state["visualizer"] = NetworkVisualizer()
if st.session_state["data_loader"] is None:
    st.session_state["data_loader"] = DataLoader()
if st.session_state["network_analyzer"] is None:
    st.session_state["network_analyzer"] = NetworkAnalyzer()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/hotel.png", width=60)
st.sidebar.title("🏨 Hôtel Aurore Paris")
st.sidebar.markdown("**Analyse Réseau & Satisfaction Client**")
st.sidebar.markdown("---")

PAGES = [
    "🏠 Accueil",
    "📂 Chargement des données",
    "🧹 Préparation & Nettoyage",
    "🕸️ Analyse Réseau",
    "🤖 Satisfaction & Modélisation",
    "🎯 Scoring Nouveau Client",
    "📊 Visualisations",
    "💾 Export",
]
page = st.sidebar.radio("Navigation", PAGES)

# Pipeline rapide
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Pipeline automatique")
if st.sidebar.button("Tout exécuter (pipeline)"):
    with st.spinner("Pipeline en cours…"):
        try:
            dl = st.session_state["data_loader"]
            df_f = dl.build_final_dataset(save=True)
            _set("df_final", df_f)

            na = st.session_state["network_analyzer"]
            na.build_similarity_graph(df_f, min_similarity=0.3, max_nodes=800)
            comms = na.detect_communities(method="greedy")
            df_m = na.compute_network_metrics()
            df_e = na.export_network_results(df_f)
            _set("graph", na.graph)
            _set("communities", comms)
            _set("df_metrics", df_m)
            _set("df_enriched", df_e)

            pred = SatisfactionPredictor(model_type="random_forest", task="classification")
            X, y = pred.prepare_features(df_e)
            results = pred.train(X, y, validation=True)
            _set("predictor_obj", pred)
            _set("eval_results", results)

            st.sidebar.success("✅ Pipeline terminé !")
        except Exception as ex:
            st.sidebar.error(f"Erreur pipeline : {ex}")

st.sidebar.markdown("---")
st.sidebar.info(
    "**Données** : AvailPro · Booking · Expedia\n\n"
    "DU SDA 2025-2026"
)

# =============================================================================
# PAGE 1 — ACCUEIL
# =============================================================================
if page == "🏠 Accueil":
    st.markdown('<h1 class="main-header">🏨 Hôtel Aurore Paris Gare de Lyon</h1>',
                unsafe_allow_html=True)
    st.markdown("#### Plateforme d'analyse réseau & modélisation de la satisfaction client")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🎯 Objectifs")
        st.markdown("""
- Analyser les **profils clients** depuis les données réelles
- Construire un **réseau de similarité** entre séjours
- Détecter des **communautés** de clients
- **Modéliser la satisfaction** à partir des avis Booking & Expedia
        """)
    with col2:
        st.markdown("### 🔧 Pipeline")
        st.markdown("""
1. Chargement des données hôtelières
2. Nettoyage & création de variables
3. Construction du graphe de similarité
4. Calcul des métriques réseau
5. Détection de communautés
6. Modèle de satisfaction (RF / XGB)
7. Visualisation & export
        """)
    with col3:
        st.markdown("### 📁 Données sources")
        st.markdown("""
| Fichier | Contenu |
|---------|---------|
| `availpro_export.xlsx` | ~6 500 réservations |
| `données avis booking.csv` | 1 634 avis Booking (CSV brut) |
| `expediareviews_*.csv` | 208 avis Expedia |
        """)

    st.markdown("---")
    with st.expander("📖 Guide d'utilisation rapide"):
        st.markdown("""
**Option 1 — Pipeline automatique** : utilisez le bouton **"Tout exécuter"** dans la barre latérale.

**Option 2 — Pas à pas** :
1. **📂 Chargement** : chargez ou confirmez les fichiers source
2. **🧹 Préparation** : nettoyage, variables dérivées, fusion avis
3. **🕸️ Réseau** : construisez le graphe, calculez les métriques, détectez les communautés
4. **🤖 Satisfaction** : entraînez le modèle de prédiction
5. **📊 Visualisations** : explorez tous les graphiques
6. **💾 Export** : téléchargez les résultats

> ℹ️ **Seuil de similarité** : 0.3 par défaut (deux clients sont reliés s'ils partagent au moins 30% de leurs caractéristiques pondérées).
        """)

    # KPIs si données chargées
    if _ss("df_final") is not None:
        df = _ss("df_final")
        st.markdown("### 📊 Tableau de bord — Données chargées")
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Réservations", f"{len(df):,}")
        k2.metric("Clients uniques", f"{df['client_id'].nunique():,}")
        k3.metric("Avec avis Booking", f"{int(df['has_review'].sum()):,}" if "has_review" in df.columns else "—")
        if "review_score" in df.columns:
            k4.metric("Note moy. Booking", f"{df['review_score'].mean():.2f}/10")
        if "revenue" in df.columns:
            k5.metric("Revenu moy.", f"{df['revenue'].mean():.0f}€")

        # Deuxième rangée de KPIs
        k6, k7, k8, k9, k10 = st.columns(5)
        if "high_satisfaction" in df.columns:
            hs = int(df["high_satisfaction"].sum())
            k6.metric("Haute satisfaction (≥8)", f"{hs:,}")
        if "channel_group" in df.columns:
            top_ch = df["channel_group"].value_counts().index[0]
            k7.metric("Canal dominant", top_ch)
        if "room_segment" in df.columns:
            top_rm = df["room_segment"].value_counts().index[0]
            k8.metric("Chambre dominante", top_rm)
        if "is_cancelled" in df.columns:
            canc_rate = df["is_cancelled"].mean() * 100
            k9.metric("Taux d'annulation", f"{canc_rate:.1f}%")
        if "arrival_year" in df.columns:
            years = sorted(df["arrival_year"].dropna().unique().astype(int))
            k10.metric("Période", f"{years[0]}–{years[-1]}" if len(years) > 1 else str(years[0]))

        # Réseau si disponible
        if _ss("graph") is not None:
            G = _ss("graph")
            na = st.session_state["network_analyzer"]
            stats = na.network_stats or {}
            st.markdown("### 🕸️ Réseau de similarité")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Nœuds", G.number_of_nodes())
            r2.metric("Arêtes", G.number_of_edges())
            r3.metric("Densité", f"{stats.get('density', 0):.4f}")
            r4.metric("Communautés", len(set(_ss("communities").values())) if _ss("communities") else "—")

        # Modèle si disponible
        if _ss("eval_results") is not None:
            eval_r = _ss("eval_results")
            st.markdown("### 🤖 Modèle de satisfaction")
            m1, m2, m3 = st.columns(3)
            if "accuracy" in eval_r:
                m1.metric("Accuracy", f"{eval_r['accuracy']:.2%}")
            if "f1_weighted" in eval_r:
                m2.metric("F1-weighted", f"{eval_r['f1_weighted']:.4f}")
            if "roc_auc" in eval_r:
                m3.metric("ROC-AUC", f"{eval_r['roc_auc']:.4f}")

# =============================================================================
# PAGE 2 — CHARGEMENT DES DONNÉES
# =============================================================================
elif page == "📂 Chargement des données":
    st.header("📂 Chargement des données hôtelières")

    tab_auto, tab_upload = st.tabs(["📁 Fichiers locaux (recommandé)", "⬆️ Upload manuel"])

    # --- Onglet fichiers locaux ---
    with tab_auto:
        st.markdown(f"**Répertoire attendu** : `{_RAW_DIR}`")

        files = {
            "AvailPro (réservations)": _RAW_DIR / "availpro_export.xlsx",
            "Avis Booking (CSV brut)": _RAW_DIR / "données avis booking.csv",
            "Avis Expedia": _RAW_DIR / "expediareviews_from_2025-03-01_to_2026-03-01.csv",
        }

        for label, path in files.items():
            exists = path.exists()
            icon = "✅" if exists else "❌"
            st.markdown(f"{icon} `{path.name}` — {label}")

        st.markdown("---")

        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("📥 Charger les réservations"):
                with st.spinner("Chargement AvailPro…"):
                    try:
                        df = load_availpro_data()
                        _set("df_raw_res", df)
                        st.success(f"✅ {len(df):,} réservations chargées")
                        st.dataframe(df.head(5), use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        with col_btn2:
            if st.button("📥 Charger les avis Booking"):
                with st.spinner("Chargement avis Booking…"):
                    try:
                        df = load_booking_reviews()
                        _set("df_raw_booking", df)
                        st.success(f"✅ {len(df):,} avis Booking chargés")
                        st.dataframe(df.head(5), use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        with col_btn3:
            if st.button("📥 Charger les avis Expedia"):
                with st.spinner("Chargement avis Expedia…"):
                    try:
                        df = load_expedia_reviews()
                        _set("df_raw_expedia", df)
                        st.success(f"✅ {len(df):,} avis Expedia chargés")
                        st.dataframe(df.head(5), use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    # --- Onglet upload ---
    with tab_upload:
        st.info("Uploadez vos propres fichiers si les fichiers locaux ne sont pas disponibles.")
        up_res = st.file_uploader("Réservations (xlsx)", type=["xlsx", "xls"], key="up_res")
        up_bk  = st.file_uploader("Avis Booking (csv brut)", type=["csv"], key="up_bk")
        up_ex  = st.file_uploader("Avis Expedia (csv)", type=["csv"], key="up_ex")

        if up_res:
            try:
                df = _load_uploaded_with_loader(up_res, Path(up_res.name).suffix or ".xlsx", load_availpro_data)
                _set("df_raw_res", df)
                st.success(f"✅ Réservations uploadées : {len(df):,} lignes")
            except Exception as e:
                st.error(f"Erreur upload réservations : {e}")

        if up_bk:
            try:
                suffix = Path(up_bk.name).suffix or ".csv"
                df = _load_uploaded_with_loader(up_bk, suffix, load_booking_reviews)
                _set("df_raw_booking", df)
                st.success(f"✅ Avis Booking uploadés : {len(df):,} lignes")
            except Exception as e:
                st.error(f"Erreur upload Booking : {e}")

        if up_ex:
            try:
                df = _load_uploaded_with_loader(up_ex, Path(up_ex.name).suffix or ".csv", load_expedia_reviews)
                _set("df_raw_expedia", df)
                st.success(f"✅ Avis Expedia uploadés : {len(df):,} lignes")
            except Exception as e:
                st.error(f"Erreur upload Expedia : {e}")

    # Récapitulatif
    st.markdown("---")
    st.markdown("### Récapitulatif des données chargées")
    for label, key in [
        ("Réservations brutes", "df_raw_res"),
        ("Avis Booking bruts", "df_raw_booking"),
        ("Avis Expedia bruts", "df_raw_expedia"),
    ]:
        df = _ss(key)
        if df is not None:
            st.success(f"✅ **{label}** : {len(df):,} lignes × {df.shape[1]} colonnes")
        else:
            st.warning(f"⚠️ **{label}** : non chargé")

# =============================================================================
# PAGE 3 — PRÉPARATION & NETTOYAGE
# =============================================================================
elif page == "🧹 Préparation & Nettoyage":
    st.header("🧹 Préparation & Nettoyage des données")

    st.markdown("""
    Cette étape :
    - Nettoie les réservations (dates, variables dérivées, anonymisation)
    - Nettoie les avis Booking & Expedia
    - Fusionne les avis avec les réservations via le numéro de réservation
    - Génère le **dataset final** utilisé pour l'analyse réseau et la modélisation
    """)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Options")
        max_nodes = st.number_input("Nb max clients (réseau)", 100, 5000, 1000, step=100)
        use_demo = st.checkbox("Mode démonstration (données simulées)", value=False)

        if st.button("🔄 Construire le dataset final", type="primary"):
            with st.spinner("Nettoyage et fusion en cours…"):
                try:
                    if use_demo:
                        dl = st.session_state["data_loader"]
                        df_final = dl.generate_sample_data(n_clients=300)
                        st.info("Mode démo : données simulées")
                    else:
                        # Utiliser les données brutes si déjà chargées, sinon charger depuis le disque
                        dl = st.session_state["data_loader"]

                        df_res = _ss("df_raw_res")
                        if df_res is None:
                            df_res = load_availpro_data()

                        df_bk = _ss("df_raw_booking")
                        if df_bk is None:
                            df_bk = load_booking_reviews()

                        df_ex = _ss("df_raw_expedia")
                        if df_ex is None:
                            df_ex = load_expedia_reviews()

                        # Nettoyage
                        df_res_clean = clean_reservations(df_res)
                        df_bk_clean  = clean_booking_reviews(df_bk)
                        df_ex_clean  = clean_expedia_reviews(df_ex)

                        _set("df_clean_res",     df_res_clean)
                        _set("df_clean_booking", df_bk_clean)
                        _set("df_clean_expedia", df_ex_clean)

                        # Fusion
                        df_final = merge_reviews_with_reservations(df_res_clean, df_bk_clean)
                        df_final.attrs["expedia_reviews"] = df_ex_clean

                        # Score satisfaction
                        if "review_score" in df_final.columns:
                            df_final["satisfaction_norm"] = (df_final["review_score"] / 10).clip(0, 1)
                            df_final["high_satisfaction"] = (df_final["review_score"] >= 8).astype(int)

                        df_final = df_final.dropna(subset=["client_id"])

                        # Sauvegarder
                        _PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
                        out = _PROCESSED_DIR / "hotel_dataset_final.csv"
                        df_final.to_csv(out, index=False, encoding="utf-8-sig")

                    _set("df_final", df_final)
                    st.success(f"✅ Dataset final : {len(df_final):,} lignes × {df_final.shape[1]} colonnes")

                except Exception as e:
                    st.error(f"Erreur : {e}")
                    logger.exception(e)

    with col2:
        if _ss("df_final") is not None:
            df = _ss("df_final")
            st.markdown("#### Aperçu du dataset final")

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Lignes", f"{len(df):,}")
            k2.metric("Colonnes", df.shape[1])
            k3.metric("Clients uniques", f"{df['client_id'].nunique():,}")
            if "has_review" in df.columns:
                k4.metric("Avec avis", f"{df['has_review'].sum():,}")

            st.dataframe(df.head(10), use_container_width=True)

            with st.expander("📊 Statistiques descriptives"):
                num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                st.dataframe(df[num_cols].describe(), use_container_width=True)

            with st.expander("🗂️ Valeurs manquantes"):
                miss = df.isnull().sum()
                miss = miss[miss > 0].sort_values(ascending=False)
                if not miss.empty:
                    st.bar_chart(miss)
                else:
                    st.success("Aucune valeur manquante !")

            if "channel_group" in df.columns:
                st.markdown("#### Répartition par canal")
                ch = df["channel_group"].value_counts()
                st.bar_chart(ch)

# =============================================================================
# PAGE 4 — ANALYSE RÉSEAU
# =============================================================================
elif page == "🕸️ Analyse Réseau":
    st.header("🕸️ Analyse du Réseau de Similarité")

    if _ss("df_final") is None:
        st.warning("⚠️ Construisez d'abord le dataset final dans la page **Préparation & Nettoyage**.")
        st.stop()

    df = _ss("df_final")

    tab1, tab2, tab3 = st.tabs(["Construction du graphe", "Métriques de centralité", "Communautés"])

    # --- Onglet 1 : Construction ---
    with tab1:
        st.subheader("Construction du graphe de similarité")
        col1, col2, col3 = st.columns(3)
        with col1:
            min_sim = st.slider("Seuil de similarité minimum", 0.1, 0.9, 0.3, 0.05)
        with col2:
            max_nodes = st.number_input("Nb max de nœuds", 50, 3000, 800, step=50)
        with col3:
            comm_method = st.selectbox("Méthode de détection", ["greedy", "label_propagation", "louvain"])

        if st.button("🔨 Construire le réseau", type="primary"):
            with st.spinner("Construction du graphe…"):
                try:
                    na = st.session_state["network_analyzer"]
                    G = na.build_similarity_graph(df, min_similarity=min_sim, max_nodes=max_nodes)
                    comms = na.detect_communities(method=comm_method)
                    _set("graph", G)
                    _set("communities", comms)
                    st.success(f"✅ Graphe construit : **{G.number_of_nodes()} nœuds** — **{G.number_of_edges()} arêtes**")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    logger.exception(e)

        if _ss("graph") is not None:
            G = _ss("graph")
            na = st.session_state["network_analyzer"]
            stats = na.get_network_statistics()

            st.markdown("#### Statistiques du réseau")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Nœuds", stats.get("n_nodes", "—"))
            c2.metric("Arêtes", stats.get("n_edges", "—"))
            c3.metric("Densité", f"{stats.get('density', 0):.5f}")
            c4.metric("Composantes", stats.get("n_connected_components", "—"))
            c5.metric("Clustering moy.", f"{stats.get('avg_clustering', 0):.4f}")

            if "modularity" in stats:
                st.metric("Modularité", f"{stats['modularity']:.4f}")

            # Visualisation réseau
            st.markdown("#### Visualisation")
            viz = _ss("visualizer")
            comms = _ss("communities")
            fig = viz.plot_network(G, communities=comms, save=True)
            st.pyplot(fig)

    # --- Onglet 2 : Métriques ---
    with tab2:
        if _ss("graph") is None:
            st.warning("Construisez d'abord le graphe dans l'onglet précédent.")
            st.stop()

        if st.button("📊 Calculer les métriques de centralité"):
            with st.spinner("Calcul des centralités…"):
                try:
                    na = st.session_state["network_analyzer"]
                    df_m = na.compute_network_metrics()
                    df_e = na.export_network_results(_ss("df_final"))
                    _set("df_metrics", df_m)
                    _set("df_enriched", df_e)
                    st.success(f"✅ Métriques calculées pour {len(df_m):,} clients")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    logger.exception(e)

        if _ss("df_metrics") is not None:
            df_m = _ss("df_metrics")
            metric_cols = [c for c in df_m.columns if c != "client_id"]
            selected_metric = st.selectbox("Métrique à afficher", metric_cols, index=0)

            st.markdown(f"#### Top 20 clients — {selected_metric}")
            top20 = df_m.nlargest(20, selected_metric)[["client_id", selected_metric]]
            st.dataframe(top20, use_container_width=True)

            viz = _ss("visualizer")
            fig = viz.plot_centrality_distribution(df_m, save=True)
            st.pyplot(fig)

    # --- Onglet 3 : Communautés ---
    with tab3:
        comms = _ss("communities")
        if not comms:
            st.info("⏳ Construisez d'abord le graphe avec détection de communautés (onglet **Construction**).")
        else:
            comm_series = pd.Series(comms, name="community_id")
            n_comms = comm_series.nunique()

            c1, c2, c3 = st.columns(3)
            c1.metric("Nombre de communautés", n_comms)
            c2.metric("Nœuds assignés", len(comm_series))
            sizes = comm_series.value_counts().sort_index()
            c3.metric("Taille moy. communauté", f"{sizes.mean():.0f}")

            st.markdown("#### Taille des communautés")
            st.bar_chart(sizes)

            df_enr = _ss("df_enriched")
            if df_enr is not None:
                viz = _ss("visualizer")
                col_left, col_right = st.columns(2)
                if "review_score" in df_enr.columns:
                    with col_left:
                        st.markdown("#### Satisfaction par communauté")
                        fig = viz.plot_satisfaction_by_community(df_enr, save=True)
                        st.pyplot(fig)
                if "revenue" in df_enr.columns:
                    with col_right:
                        st.markdown("#### Revenu par communauté")
                        fig = viz.plot_revenue_by_community(df_enr, save=True)
                        st.pyplot(fig)

                # Tableau récapitulatif par communauté
                if "community_id" in df_enr.columns:
                    st.markdown("#### Profil moyen par communauté")
                    num_cols = [c for c in ["review_score", "revenue", "stay_length",
                                            "lead_time_days", "pagerank"]
                                if c in df_enr.columns]
                    cat_cols = [c for c in ["channel_group", "room_segment", "pays"]
                                if c in df_enr.columns]
                    agg_dict = {c: "mean" for c in num_cols}
                    agg_dict["client_id"] = "count"

                    def _mode_val(x):
                        vc = x.value_counts()
                        return vc.index[0] if len(vc) > 0 else "?"

                    for cc in cat_cols:
                        agg_dict[cc] = _mode_val

                    summary = df_enr.groupby("community_id").agg(agg_dict).round(2)
                    summary.columns = [c.replace("client_id", "n_clients") for c in summary.columns]
                    st.dataframe(summary, use_container_width=True)

# =============================================================================
# PAGE 5 — SATISFACTION & MODÉLISATION
# =============================================================================
elif page == "🤖 Satisfaction & Modélisation":
    st.header("🤖 Modélisation de la Satisfaction Client")

    df_model = _first_available_df("df_enriched", "df_final")
    if df_model is None:
        st.warning("⚠️ Construisez d'abord le dataset final (page **Préparation & Nettoyage**).")
        st.stop()

    # Statistiques rapides sur les données disponibles
    with st.expander("📊 Aperçu des données disponibles pour la modélisation", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lignes totales", f"{len(df_model):,}")
        has_rev = int(df_model["has_review"].sum()) if "has_review" in df_model.columns else 0
        c2.metric("Avec avis (cible disponible)", f"{has_rev:,}")
        if "review_score" in df_model.columns:
            c3.metric("Note moy.", f"{df_model['review_score'].mean():.2f}/10")
        if "high_satisfaction" in df_model.columns:
            hs = int(df_model["high_satisfaction"].sum())
            c4.metric("Haute satisfaction (≥8)", f"{hs:,}")
        net_cols = [c for c in ["pagerank", "betweenness", "eigenvector", "weighted_degree"]
                    if c in df_model.columns]
        if net_cols:
            st.info(f"✅ Variables réseau disponibles : {', '.join(net_cols)}")
        else:
            st.warning("⚠️ Variables réseau absentes — construisez d'abord le réseau pour les inclure.")

    tab1, tab2, tab3 = st.tabs(["⚙️ Configuration & Entraînement", "📈 Résultats", "🔀 Comparaison modèles"])

    with tab1:
        st.subheader("Configuration du modèle")

        col1, col2, col3 = st.columns(3)
        with col1:
            task_type = st.selectbox(
                "Tâche",
                ["classification", "regression"],
                help="Classification : high_satisfaction (0/1) | Régression : note /10",
                key="task_type_select",
            )
        with col2:
            model_type = st.selectbox(
                "Modèle", ["random_forest", "gradient_boosting"],
                key="model_type_select",
            )
        with col3:
            test_size = st.slider("Proportion test", 0.1, 0.4, 0.2, key="test_size_slider")

        do_cv = st.checkbox("Validation croisée (5-fold)", value=True, key="do_cv_check")

        # Sauvegarder task_type dans session_state pour y accéder depuis tab3
        _set("current_task_type", task_type)

        if st.button("🚀 Entraîner le modèle", type="primary", key="btn_train"):
            with st.spinner("Entraînement en cours…"):
                try:
                    pred = SatisfactionPredictor(model_type=model_type, task=task_type)
                    X, y = pred.prepare_features(df_model)
                    results = pred.train(X, y, test_size=test_size, validation=do_cv)
                    eval_res = results.copy()

                    _set("predictor_obj", pred)
                    _set("X_train", None)
                    _set("X_test", None)
                    _set("y_train", None)
                    _set("y_test", None)
                    _set("eval_results", {**results, **eval_res})

                    st.success("✅ Modèle entraîné avec succès !")
                    st.markdown("#### Métriques d'évaluation")
                    kpi_items = {k: v for k, v in eval_res.items()
                                 if isinstance(v, (int, float)) and v is not None}
                    if kpi_items:
                        kpi_cols = st.columns(len(kpi_items))
                        for col, (k, v) in zip(kpi_cols, kpi_items.items()):
                            col.metric(k.replace("_", " ").upper(), f"{v:.4f}")
                    else:
                        st.warning("Aucune métrique calculable pour cette configuration.")

                except Exception as e:
                    st.error(f"Erreur : {e}")
                    logger.exception(e)

    with tab2:
        if _ss("predictor_obj") is None:
            st.info("⏳ Entraînez d'abord un modèle dans l'onglet **Configuration**.")
        else:
            pred = _ss("predictor_obj")
            eval_res = _ss("eval_results") or {}
            st.subheader("Résultats d'évaluation")

            # KPIs
            metrics_display = {k: v for k, v in eval_res.items()
                               if isinstance(v, (int, float)) and v is not None}
            if metrics_display:
                cols = st.columns(min(len(metrics_display), 5))
                for col, (k, v) in zip(cols, metrics_display.items()):
                    col.metric(k.replace("_", " ").upper(), f"{v:.4f}")

            # Importance des features
            st.markdown("#### Importance des features")
            imp = pred.get_feature_importance(top_n=15)
            if not imp.empty:
                viz = _ss("visualizer")
                fig = viz.plot_feature_importance(imp, save=True)
                st.pyplot(fig)
                with st.expander("Tableau détaillé"):
                    st.dataframe(imp, use_container_width=True)
            else:
                st.info("Importance des features non disponible pour ce modèle.")

            # Features utilisées
            with st.expander("🗂️ Features utilisées par le modèle"):
                st.write(pred.feature_names)

    with tab3:
        st.subheader("Comparaison multi-modèles")
        # Récupérer task_type depuis session_state (indépendant de l'onglet actif)
        current_task = _ss("current_task_type") or "classification"

        if st.button("⚡ Comparer tous les modèles", key="btn_compare"):
            with st.spinner("Comparaison Random Forest vs Gradient Boosting…"):
                try:
                    df_m2 = _first_available_df("df_enriched", "df_final")
                    pred2 = SatisfactionPredictor(task=current_task)
                    X2, y2 = pred2.prepare_features(df_m2)
                    multi_res = pred2.train_all_models(X2, y2)
                    _set("multi_results", multi_res)
                    st.success("✅ Comparaison terminée")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    logger.exception(e)

        if _ss("multi_results"):
            multi = _ss("multi_results")
            st.markdown("#### Résultats comparatifs")
            rows = []
            for m_name, res in multi.items():
                row = {"modèle": m_name}
                row.update({k: round(v, 4) for k, v in res.items()
                             if isinstance(v, (int, float)) and v is not None})
                rows.append(row)
            st.dataframe(pd.DataFrame(rows).set_index("modèle"), use_container_width=True)

            metric_key = "f1_weighted" if current_task == "classification" else "r2"
            viz = _ss("visualizer")
            fig = viz.plot_model_comparison(multi, metric=metric_key, save=True)
            st.pyplot(fig)

# =============================================================================
# PAGE 6 — SCORING NOUVEAU CLIENT  (onglet premium)
# =============================================================================
elif page == "🎯 Scoring Nouveau Client":
    st.markdown(
        '<h1 class="main-header">🎯 Satisfaction & Scoring Nouveau Client</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Outil premium réception** — Renseignez les caractéristiques d'un séjour "
        "et obtenez une estimation de la satisfaction probable ainsi qu'un message "
        "d'accueil personnalisé."
    )
    st.markdown("---")

    # ── Vérification modèle ──────────────────────────────────────────────────
    pred_obj = _ss("predictor_obj")
    df_ref   = _first_available_df("df_enriched", "df_final")

    if pred_obj is None or pred_obj.model is None:
        st.warning(
            "⚠️ Aucun modèle disponible. Veuillez d'abord entraîner un modèle "
            "dans la page **🤖 Satisfaction & Modélisation** "
            "(ou utilisez le **Pipeline automatique** dans la barre latérale)."
        )
        st.info(
            "💡 **Conseil rapide** : cliquez sur **Tout exécuter (pipeline)** "
            "dans la barre latérale pour initialiser toute la chaîne en une seule action."
        )
        st.stop()

    st.success(
        f"✅ Modèle chargé : **{pred_obj.model_type}** — tâche : **{pred_obj.task}** "
        f"— {len(pred_obj.feature_names)} features"
    )

    # ── Collecte des options depuis les données réelles ───────────────────────
    def _get_options(col: str, defaults: list) -> list:
        if df_ref is not None and col in df_ref.columns:
            opts = [str(v) for v in df_ref[col].dropna().unique() if str(v).strip()]
            opts = sorted(set(opts))
            return opts if opts else defaults
        return defaults

    channels     = _get_options("channel_group", ["Direct", "Booking.com", "Expedia", "Agence", "Téléphone", "Autre"])
    room_segs    = _get_options("room_segment",  ["Standard", "Supérieure", "Deluxe", "Suite", "Autre"])
    amt_buckets  = _get_options("amount_bucket", ["< 100€", "100-200€", "200-400€", "400-800€", "> 800€"])
    pays_opts    = _get_options("pays",          ["France", "Royaume-Uni", "Allemagne", "Italie", "Espagne", "USA", "Belgique", "Autre"])
    langue_opts  = _get_options("langue",        ["fr", "en", "de", "it", "es", "nl", "Autre"])

    MOIS_LABELS = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
    }
    NO_VALUE = "(non renseigné)"

    # ── Formulaire ───────────────────────────────────────────────────────────
    with st.form("form_scoring_client"):
        st.markdown("### 📋 Caractéristiques du nouveau séjour")
        st.caption("Les champs non renseignés n'empêchent pas la prédiction.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Profil & canal**")
            channel = st.selectbox(
                "Canal de réservation",
                [NO_VALUE] + channels,
                key="sc_channel",
            )
            partenaire = st.text_input(
                "Partenaire / Source (optionnel)",
                key="sc_partner",
                placeholder="ex : Booking.com, Direct site…",
            )
            pays = st.selectbox("Nationalité / Pays", [NO_VALUE] + pays_opts, key="sc_pays")
            langue = st.selectbox("Langue", [NO_VALUE] + langue_opts, key="sc_langue")

        with col2:
            st.markdown("**Séjour**")
            room_seg = st.selectbox("Type de chambre", [NO_VALUE] + room_segs, key="sc_room")
            arrival_month = st.selectbox(
                "Mois d'arrivée",
                [NO_VALUE] + [f"{k} — {v}" for k, v in MOIS_LABELS.items()],
                key="sc_month",
            )
            stay_length = st.number_input(
                "Durée du séjour (nuits)",
                min_value=0, max_value=60, value=0, step=1,
                key="sc_stay",
                help="Laissez 0 si inconnu",
            )
            lead_time = st.number_input(
                "Délai de réservation (jours avant arrivée)",
                min_value=0, max_value=730, value=0, step=1,
                key="sc_lead",
                help="Laissez 0 si réservé aujourd'hui ou inconnu",
            )

        with col3:
            st.markdown("**Composition & tarif**")
            amount_bucket = st.selectbox(
                "Tranche de montant", [NO_VALUE] + amt_buckets, key="sc_amount"
            )
            adultes = st.number_input(
                "Nombre d'adultes", min_value=0, max_value=10, value=1, step=1,
                key="sc_adults",
            )
            enfants = st.number_input(
                "Nombre d'enfants", min_value=0, max_value=10, value=0, step=1,
                key="sc_children",
            )
            st.markdown("&nbsp;")
            st.markdown("&nbsp;")

        submitted = st.form_submit_button(
            "🔮 Prédire la satisfaction", type="primary", use_container_width=True
        )

    # ── Traitement à la soumission ────────────────────────────────────────────
    if submitted:
        client_dict: dict = {}

        if channel != NO_VALUE:
            client_dict["channel_group"] = channel
        if pays != NO_VALUE:
            client_dict["pays"] = pays
        if langue != NO_VALUE:
            client_dict["langue"] = langue
        if room_seg != NO_VALUE:
            client_dict["room_segment"] = room_seg
        if amount_bucket != NO_VALUE:
            client_dict["amount_bucket"] = amount_bucket
        if arrival_month != NO_VALUE:
            try:
                client_dict["arrival_month"] = int(arrival_month.split(" — ")[0])
            except Exception:
                pass
        if stay_length > 0:
            client_dict["stay_length"] = int(stay_length)
        if lead_time > 0:
            client_dict["lead_time_days"] = int(lead_time)
        if adultes > 0:
            client_dict["adultes"] = int(adultes)
        if enfants > 0:
            client_dict["enfants"] = int(enfants)

        try:
            with st.spinner("Calcul du score de satisfaction…"):
                result = pred_obj.predict_single(client_dict)
            _set("scoring_result", result)
            _set("scoring_dict", client_dict)
        except Exception as exc:
            st.error(f"❌ Erreur lors de la prédiction : {exc}")
            logger.exception(exc)

    # ── Affichage des résultats ───────────────────────────────────────────────
    result = _ss("scoring_result")

    if result is not None:
        score       = result["score"]
        level_num   = result["level_num"]
        level_icon  = result["level_icon"]
        level_lbl   = result["satisfaction_level"]
        vigilance   = result["vigilance"]
        attention   = result["attention"]
        conseil     = result["conseil"]
        rec_msg     = result["receptionist_msg"]
        prob_reviews= result["probable_reviews"]
        f_factors   = result["feature_factors"]
        probability = result.get("probability")
        n_prov      = result["n_features_provided"]
        n_tot       = result["n_features_total"]

        st.markdown("---")
        st.markdown("## 📊 Résultats de l'analyse")

        # ── BLOC 1 : Score de satisfaction ────────────────────────────────────
        st.markdown("### 1️⃣ Score de satisfaction prédit")

        # Palette de couleur
        gauge_color = {"green": "#27ae60", "#2ecc71": "#2ecc71", "orange": "#e67e22",
                       "red": "#e74c3c"}.get(result["level_color"], "#2980b9")

        col_score, col_jauge, col_meta = st.columns([1, 2, 1])

        with col_score:
            st.markdown(
                f"<div class='score-panel' style='background:linear-gradient(135deg,{gauge_color} 0%,{gauge_color}aa 100%);'>"
                f"<div class='score-value'>{score:.1f}<span style='font-size:1.5rem'>/10</span></div>"
                f"<div class='score-label'>{level_icon} {level_lbl}</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        with col_jauge:
            st.markdown("**Jauge de satisfaction**")
            st.progress(min(score / 10.0, 1.0))
            if probability is not None:
                st.caption(f"Probabilité de haute satisfaction : **{probability:.1%}**")
            levels = ["🔴 Fragile", "🟠 Moyenne", "🟡 Élevée", "🟢 Très probable"]
            for i, lbl in enumerate(levels, 1):
                marker = " ◀ **ce client**" if i == level_num else ""
                st.markdown(f"{'&nbsp;' * (i * 4)}{lbl}{marker}", unsafe_allow_html=True)

        with col_meta:
            st.metric("Vigilance", vigilance)
            st.metric("Couverture features", f"{n_prov}/{n_tot}")
            badge_class = {4: "green", 3: "yellow", 2: "orange", 1: "red"}.get(level_num, "green")
            st.markdown(
                f"<br><span class='level-badge-{badge_class}'>{level_icon} {level_lbl}</span>",
                unsafe_allow_html=True,
            )

        # ── BLOC 2 : Interprétation métier ────────────────────────────────────
        st.markdown("---")
        st.markdown("### 2️⃣ Interprétation métier")

        i1, i2, i3 = st.columns(3)
        with i1:
            st.markdown("**Niveau d'attention recommandé**")
            st.info(f"🎯 {attention}")
        with i2:
            st.markdown("**Niveau de vigilance**")
            st.info(f"⚠️ {vigilance}")
        with i3:
            st.markdown("**Potentiel d'expérience positive**")
            potential = {4: "Très élevé ✨", 3: "Élevé 👍", 2: "Modéré 🔄", 1: "À construire 🛠️"}
            st.info(potential.get(level_num, "—"))

        st.markdown("**Conseils de personnalisation de l'accueil**")
        st.markdown(
            f"<div class='recep-msg' style='border-color:{gauge_color};'>💡 {conseil}</div>",
            unsafe_allow_html=True,
        )

        # ── BLOC 3 : Message au réceptionniste ────────────────────────────────
        st.markdown("---")
        st.markdown("### 3️⃣ Message au réceptionniste")
        st.caption("Message professionnel, bienveillant et directement exploitable par la réception.")

        # Formater les sauts de ligne
        msg_lines = rec_msg.replace("\n\n", "\n").split("\n")
        formatted_msg = "<br>".join(msg_lines)

        st.markdown(
            f"<div class='recep-msg'>"
            f"<strong>📋 Consigne d'accueil</strong><br><br>"
            f"{formatted_msg}"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Bouton de copie (via text_area copiable)
        with st.expander("📋 Copier ce message"):
            st.text_area(
                "Message prêt à copier :",
                value=rec_msg,
                height=150,
                key="ta_recep_msg",
                label_visibility="collapsed",
            )

        # ── BLOC 4 : Avis probable ────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 4️⃣ Avis probable / Phrases probables")
        st.caption(
            "Basé sur le profil et le score prédit — indicatif, non garanti."
        )

        if prob_reviews:
            for phrase in prob_reviews:
                st.markdown(
                    f"<div class='review-phrase'>💬 {phrase}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aucune phrase générée pour ce profil.")

        themes_col1, themes_col2 = st.columns(2)
        with themes_col1:
            st.markdown("**Thèmes probables de satisfaction**")
            if level_num >= 3:
                st.markdown("- ✅ Accueil et personnel\n- ✅ Localisation\n- ✅ Confort")
            elif level_num == 2:
                st.markdown("- ✅ Localisation\n- 🔄 Accueil standard\n- 🔄 Rapport qualité/prix")
            else:
                st.markdown("- 🔄 Localisation\n- ⚠️ Attentes à confirmer")
        with themes_col2:
            st.markdown("**Points de vigilance possibles**")
            if level_num >= 3:
                st.markdown("- ℹ️ Peu de points critiques attendus")
            else:
                st.markdown("- ⚠️ Clarté des informations à l'arrivée\n- ⚠️ Confort perçu\n- ⚠️ Fluidité du check-in")

        # ── BLOC 5 : Comparaison ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 5️⃣ Comparaison avec les données historiques")

        if df_ref is not None and "review_score" in df_ref.columns:
            avg_global = df_ref["review_score"].mean()
            avg_global_norm = avg_global  # déjà en /10

            c1, c2, c3 = st.columns(3)
            c1.metric("Score prédit (ce client)", f"{score:.1f}/10")
            c2.metric("Moyenne globale hôtel", f"{avg_global_norm:.2f}/10")
            delta_val = score - avg_global_norm
            c3.metric(
                "Écart à la moyenne",
                f"{delta_val:+.2f}",
                delta=f"{delta_val:+.2f}",
                delta_color="normal",
            )

            # Comparaison par canal
            client_dict_ss = _ss("scoring_dict") or {}
            ch_val = client_dict_ss.get("channel_group")
            if ch_val and "channel_group" in df_ref.columns:
                df_ch = df_ref[df_ref["channel_group"] == ch_val]
                if len(df_ch) >= 5:
                    avg_ch = df_ch["review_score"].mean()
                    st.markdown(
                        f"**Canal `{ch_val}`** — Moyenne historique : **{avg_ch:.2f}/10** "
                        f"({len(df_ch):,} réservations) — Écart : **{score - avg_ch:+.2f}**"
                    )

            # Comparaison par communauté si disponible
            comms_dict = _ss("communities")
            if comms_dict and "community_id" in df_ref.columns:
                st.info(
                    "ℹ️ La comparaison par communauté nécessite que le nouveau client "
                    "soit assigné à une communauté (disponible après analyse réseau)."
                )

            # Mini-tableau positionnement
            st.markdown("**Positionnement global**")
            pct_below = (df_ref["review_score"] < score).mean() * 100
            st.progress(min(pct_below / 100, 1.0))
            st.caption(
                f"Ce score est supérieur à **{pct_below:.0f}%** des réservations historiques."
            )
        else:
            st.info(
                "⏳ Les données historiques ne sont pas disponibles. "
                "Chargez et préparez les données pour afficher cette comparaison."
            )

        # ── BLOC 6 : Explication ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 6️⃣ Explication de la prédiction")

        tab_factors, tab_importance = st.tabs(
            ["🔍 Facteurs identifiés", "📊 Importance des variables"]
        )

        with tab_factors:
            fav  = f_factors.get("favorable", [])
            vig  = f_factors.get("vigilance", [])

            col_f, col_v = st.columns(2)
            with col_f:
                st.markdown("**✅ Facteurs favorables**")
                if fav:
                    for item in fav:
                        st.markdown(
                            f"<span class='factor-good'>✅ {item}</span>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown("_Aucun facteur particulier identifié_")

            with col_v:
                st.markdown("**⚠️ Points de vigilance**")
                if vig:
                    for item in vig:
                        st.markdown(
                            f"<span class='factor-warn'>⚠️ {item}</span>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown("_Aucun point de vigilance particulier_")

        with tab_importance:
            imp_df = pred_obj.get_feature_importance(top_n=10)
            if not imp_df.empty:
                st.markdown("**Top 10 variables les plus influentes dans le modèle**")
                st.bar_chart(imp_df.set_index("feature")["importance"])
                with st.expander("Tableau détaillé"):
                    st.dataframe(imp_df, use_container_width=True)
            else:
                st.info("Importance des variables non disponible pour ce modèle.")

        # ── Récapitulatif des paramètres saisis ───────────────────────────────
        with st.expander("🗂️ Récapitulatif des paramètres saisis"):
            client_dict_ss = _ss("scoring_dict") or {}
            if client_dict_ss:
                recap_data = [
                    {"Paramètre": k, "Valeur": str(v)}
                    for k, v in client_dict_ss.items()
                ]
                st.dataframe(pd.DataFrame(recap_data), use_container_width=True)
            else:
                st.write("Aucun paramètre enregistré.")

        st.markdown("---")
        st.caption(
            "⚠️ Ce score est une estimation probabiliste basée sur les données historiques. "
            "Il ne constitue pas un jugement sur la qualité du client et doit être utilisé "
            "uniquement pour optimiser la qualité de l'accueil."
        )

# =============================================================================
# PAGE 7 — VISUALISATIONS
# =============================================================================
elif page == "📊 Visualisations":
    st.header("📊 Visualisations")

    df_viz = _first_available_df("df_enriched", "df_final")
    if df_viz is None:
        st.warning("⚠️ Construisez d'abord le dataset (page Préparation) et/ou le réseau.")
        st.stop()

    viz = _ss("visualizer")

    viz_choice = st.selectbox("Choisir un graphique", [
        "Réseau de similarité",
        "Distribution des centralités",
        "Satisfaction par communauté",
        "Satisfaction par canal",
        "Satisfaction par type de chambre",
        "Revenu par communauté",
        "Top profils centraux",
        "Importance des features",
        "Comparaison des modèles",
        "Matrice de corrélation",
    ])

    if viz_choice == "Réseau de similarité":
        G = _ss("graph")
        if G is None:
            st.warning("Construisez le réseau dans la page **Analyse Réseau**.")
        else:
            na = st.session_state["network_analyzer"]
            pm = _ss("communities") or {}
            fig = viz.plot_network(G, communities=pm, save=False)
            st.pyplot(fig)

    elif viz_choice == "Distribution des centralités":
        df_m = _ss("df_metrics")
        if df_m is None:
            st.warning("Calculez les métriques réseau d'abord.")
        else:
            fig = viz.plot_centrality_distribution(df_m, save=False)
            st.pyplot(fig)

    elif viz_choice == "Satisfaction par communauté":
        fig = viz.plot_satisfaction_by_community(df_viz, save=False)
        st.pyplot(fig)

    elif viz_choice == "Satisfaction par canal":
        fig = viz.plot_satisfaction_by_channel(df_viz, save=False)
        st.pyplot(fig)

    elif viz_choice == "Satisfaction par type de chambre":
        fig = viz.plot_satisfaction_by_room(df_viz, save=False)
        st.pyplot(fig)

    elif viz_choice == "Revenu par communauté":
        fig = viz.plot_revenue_by_community(df_viz, save=False)
        st.pyplot(fig)

    elif viz_choice == "Top profils centraux":
        metric_opts = [c for c in df_viz.columns
                       if c in ("pagerank", "betweenness", "eigenvector", "weighted_degree", "closeness")]
        if metric_opts:
            selected = st.selectbox("Métrique", metric_opts)
            top_n = st.slider("Nombre de profils", 5, 30, 15)
            fig = viz.plot_top_central_profiles(df_viz, centrality_col=selected,
                                                top_n=top_n, save=False)
            st.pyplot(fig)
        else:
            st.warning("Aucune métrique réseau disponible. Calculez-les dans la page Analyse Réseau.")

    elif viz_choice == "Importance des features":
        pred = _ss("predictor_obj")
        if pred is None:
            st.warning("Entraînez un modèle dans la page **Satisfaction & Modélisation**.")
        else:
            fig = viz.plot_feature_importance(pred.get_feature_importance(top_n=15), save=False)
            st.pyplot(fig)

    elif viz_choice == "Comparaison des modèles":
        multi = _ss("multi_results")
        if multi is None:
            st.warning("Lancez la comparaison multi-modèles dans la page **Satisfaction & Modélisation**.")
        else:
            metric_key = st.selectbox("Métrique", ["f1_weighted", "accuracy", "roc_auc", "r2", "rmse"])
            fig = viz.plot_model_comparison(multi, metric=metric_key, save=False)
            st.pyplot(fig)

    elif viz_choice == "Matrice de corrélation":
        fig = viz.plot_correlation_matrix(df_viz, save=False)
        st.pyplot(fig)

# =============================================================================
# PAGE 8 — EXPORT
# =============================================================================
elif page == "💾 Export":
    st.header("💾 Export des résultats")

    exports = {
        "Dataset final (réservations + avis)": ("df_final", "hotel_dataset_final"),
        "Dataset enrichi (+ métriques réseau)": ("df_enriched", "hotel_dataset_enriched"),
        "Métriques réseau": ("df_metrics", "network_metrics"),
    }

    for label, (key, filename) in exports.items():
        df_exp = _ss(key)
        if df_exp is not None:
            st.markdown(f"#### {label}")
            st.caption(f"{len(df_exp):,} lignes × {df_exp.shape[1]} colonnes")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label=f"⬇️ Télécharger CSV",
                    data=_df_to_csv_bytes(df_exp),
                    file_name=f"{filename}.csv",
                    mime="text/csv",
                    key=f"csv_{key}",
                )
            with col2:
                st.download_button(
                    label=f"⬇️ Télécharger Excel",
                    data=_df_to_excel_bytes(df_exp),
                    file_name=f"{filename}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"xlsx_{key}",
                )
        else:
            st.info(f"⏳ **{label}** — non disponible (pipeline à exécuter)")

    # Export des communautés
    comms = _ss("communities")
    if comms:
        st.markdown("#### Communautés détectées")
        df_comm = pd.DataFrame(list(comms.items()), columns=["client_id", "community_id"])
        st.dataframe(df_comm.head(10), use_container_width=True)
        st.download_button(
            "⬇️ Télécharger les communautés (CSV)",
            data=_df_to_csv_bytes(df_comm),
            file_name="communities.csv",
            mime="text/csv",
            key="csv_comm",
        )

    # Export du modèle
    pred = _ss("predictor_obj")
    if pred is not None:
        st.markdown("---")
        st.markdown("#### Modèle de satisfaction")
        if st.button("💾 Sauvegarder le modèle (joblib)"):
            try:
                pred.save_model()
                st.success("✅ Modèle sauvegardé dans `models/satisfaction_predictor.joblib`")
            except Exception as e:
                st.error(f"Erreur : {e}")

        # Résultats
        eval_res = _ss("eval_results")
        if eval_res:
            st.markdown("#### Métriques du modèle")
            st.json({k: round(v, 4) for k, v in eval_res.items()
                     if isinstance(v, (int, float)) and v is not None})

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem;'>"
    "🏨 Hôtel Aurore Paris Gare de Lyon — Analyse Réseau & Satisfaction Client "
    "| DU SDA 2025-2026"
    "</div>",
    unsafe_allow_html=True,
)

