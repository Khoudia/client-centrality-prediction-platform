"""
Application Streamlit pour la plateforme de prédiction de centralité client.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ajouter le dossier src au path
sys.path.append(str(Path(__file__).parent / "src"))

from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import CentralityPredictor
from src.visualization.visualizer import NetworkVisualizer
from src.utils.config import load_config

# Configuration de la page
st.set_page_config(
    page_title="Plateforme de Prédiction de Centralité Client",
    page_icon="📊",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="main-header">📊 Plateforme de Prédiction de Centralité Client</h1>',
            unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choisir une page",
    ["🏠 Accueil", "📊 Données", "🕸️ Réseau", "🤖 Prédiction", "📈 Visualisation"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### À propos")
st.sidebar.info(
    "Plateforme d'analyse et de prédiction de la centralité des clients dans un réseau.\n\n"
    "**Projet de mémoire** - Master Data Science"
)

# Initialiser les objets dans la session
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = DataLoader()
if 'network_analyzer' not in st.session_state:
    st.session_state.network_analyzer = NetworkAnalyzer()
if 'predictor' not in st.session_state:
    st.session_state.predictor = CentralityPredictor()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = NetworkVisualizer()

# PAGE ACCUEIL
if page == "🏠 Accueil":
    st.header("Bienvenue sur la Plateforme de Prédiction de Centralité Client")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🎯 Objectifs
        - Analyser les réseaux de clients
        - Calculer les métriques de centralité
        - Prédire la centralité future
        - Visualiser les résultats
        """)

    with col2:
        st.markdown("""
        ### 🔧 Fonctionnalités
        - Chargement de données
        - Analyse de réseau
        - Machine Learning
        - Visualisations interactives
        """)

    with col3:
        st.markdown("""
        ### 📚 Métriques
        - Centralité de degré
        - Centralité d'intermédiarité
        - Centralité de proximité
        - Centralité de vecteur propre
        - PageRank
        """)

    st.markdown("---")

    st.subheader("📖 Guide d'utilisation")
    with st.expander("Comment utiliser cette plateforme ?"):
        st.markdown("""
        1. **Données**: Chargez vos données clients et interactions
        2. **Réseau**: Construisez et analysez le réseau
        3. **Prédiction**: Entraînez les modèles de prédiction
        4. **Visualisation**: Explorez les résultats visuellement
        """)

# PAGE DONNÉES
elif page == "📊 Données":
    st.header("Gestion des Données")

    tab1, tab2, tab3 = st.tabs(["Charger les données", "Données clients", "Interactions"])

    with tab1:
        st.subheader("Charger vos données")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Données Clients")
            uploaded_clients = st.file_uploader(
                "Charger le fichier clients (CSV/Excel)",
                type=['csv', 'xlsx'],
                key='clients'
            )

            if uploaded_clients:
                st.success("Fichier clients chargé!")

            if st.button("Générer données d'exemple - Clients"):
                df_clients = st.session_state.data_loader.generate_sample_data(100)
                st.session_state.df_clients = df_clients
                st.success("100 clients d'exemple générés!")

        with col2:
            st.markdown("### Données Interactions")
            uploaded_interactions = st.file_uploader(
                "Charger le fichier interactions (CSV)",
                type=['csv'],
                key='interactions'
            )

            if uploaded_interactions:
                st.success("Fichier interactions chargé!")

            if st.button("Générer données d'exemple - Interactions"):
                df_interactions = st.session_state.data_loader.generate_sample_interactions(500)
                st.session_state.df_interactions = df_interactions
                st.success("500 interactions d'exemple générées!")

    with tab2:
        st.subheader("Aperçu des données clients")

        if 'df_clients' in st.session_state:
            df = st.session_state.df_clients

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Nombre de clients", len(df))
            col2.metric("Nombre de features", df.shape[1])
            col3.metric("CA moyen", f"{df['chiffre_affaires'].mean():.2f}€")
            col4.metric("Satisfaction moy.", f"{df['score_satisfaction'].mean():.2f}/5")

            st.dataframe(df.head(10), use_container_width=True)

            st.markdown("### Statistiques descriptives")
            st.dataframe(df.describe(), use_container_width=True)
        else:
            st.warning("Aucune donnée client chargée. Générez des données d'exemple.")

    with tab3:
        st.subheader("Aperçu des interactions")

        if 'df_interactions' in st.session_state:
            df = st.session_state.df_interactions

            col1, col2, col3 = st.columns(3)
            col1.metric("Nombre d'interactions", len(df))
            col2.metric("Clients uniques (source)", df['client_source'].nunique())
            col3.metric("Poids moyen", f"{df['weight'].mean():.3f}")

            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.warning("Aucune interaction chargée. Générez des données d'exemple.")

# PAGE RÉSEAU
elif page == "🕸️ Réseau":
    st.header("Analyse du Réseau")

    if 'df_interactions' not in st.session_state:
        st.warning("⚠️ Veuillez d'abord charger les données d'interactions dans la page 'Données'.")
    else:
        tab1, tab2 = st.tabs(["Construction & Stats", "Métriques de centralité"])

        with tab1:
            st.subheader("Construction du réseau")

            if st.button("🔨 Construire le réseau"):
                with st.spinner("Construction du réseau en cours..."):
                    graph = st.session_state.network_analyzer.build_network(
                        st.session_state.df_interactions
                    )
                    st.session_state.graph = graph
                    st.success("✅ Réseau construit avec succès!")

            if 'graph' in st.session_state:
                st.subheader("Statistiques du réseau")

                stats = st.session_state.network_analyzer.get_network_statistics()

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Nœuds", stats['nb_nodes'])
                col2.metric("Arêtes", stats['nb_edges'])
                col3.metric("Densité", f"{stats['density']:.4f}")
                col4.metric("Connexe", "✅" if stats['is_connected'] else "❌")

                col1, col2 = st.columns(2)
                col1.metric("Clustering moyen", f"{stats['avg_clustering']:.4f}")

                if 'diameter' in stats:
                    col2.metric("Diamètre", stats['diameter'])

        with tab2:
            if 'graph' not in st.session_state:
                st.warning("Construisez d'abord le réseau dans l'onglet précédent.")
            else:
                st.subheader("Calcul des métriques de centralité")

                if st.button("📊 Calculer toutes les métriques"):
                    with st.spinner("Calcul des métriques en cours..."):
                        centrality_metrics = st.session_state.network_analyzer.calculate_all_centralities()
                        centrality_df = st.session_state.network_analyzer.get_centrality_dataframe()
                        st.session_state.centrality_df = centrality_df
                        st.success("✅ Métriques calculées!")

                if 'centrality_df' in st.session_state:
                    df = st.session_state.centrality_df

                    st.markdown("### Top 10 clients par métrique")

                    metric = st.selectbox(
                        "Choisir une métrique",
                        ['degree', 'betweenness', 'closeness', 'eigenvector', 'pagerank']
                    )

                    col_name = f'centrality_{metric}'
                    top_clients = df.nlargest(10, col_name)[['node_id', col_name]]

                    st.dataframe(top_clients, use_container_width=True)

# PAGE PRÉDICTION
elif page == "🤖 Prédiction":
    st.header("Modèles de Prédiction")

    if 'df_clients' not in st.session_state or 'centrality_df' not in st.session_state:
        st.warning("⚠️ Veuillez d'abord charger les données et calculer les métriques de centralité.")
    else:
        tab1, tab2 = st.tabs(["Entraînement", "Évaluation"])

        with tab1:
            st.subheader("Configuration du modèle")

            col1, col2 = st.columns(2)

            with col1:
                model_type = st.selectbox(
                    "Type de modèle",
                    ['random_forest', 'xgboost', 'gradient_boosting']
                )

            with col2:
                test_size = st.slider("Proportion test", 0.1, 0.4, 0.2)

            if st.button("🚀 Entraîner les modèles"):
                with st.spinner("Entraînement en cours..."):
                    predictor = CentralityPredictor(model_type=model_type)

                    # Préparer les données
                    X, y = predictor.prepare_features(
                        st.session_state.df_clients,
                        st.session_state.centrality_df
                    )

                    # Split
                    from sklearn.model_selection import train_test_split
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=test_size, random_state=42
                    )

                    # Entraînement
                    training_scores = predictor.train(X_train, y_train)

                    # Évaluation
                    eval_results = predictor.evaluate(X_test, y_test)

                    # Stocker dans la session
                    st.session_state.predictor = predictor
                    st.session_state.X_train = X_train
                    st.session_state.X_test = X_test
                    st.session_state.y_train = y_train
                    st.session_state.y_test = y_test
                    st.session_state.eval_results = eval_results

                    st.success("✅ Modèles entraînés avec succès!")

                    # Afficher les résultats
                    st.markdown("### Résultats d'entraînement")
                    results_df = pd.DataFrame([eval_results])
                    st.dataframe(results_df, use_container_width=True)

        with tab2:
            if 'eval_results' not in st.session_state:
                st.warning("Entraînez d'abord les modèles dans l'onglet précédent.")
            else:
                st.subheader("Résultats d'évaluation")

                results_df = pd.DataFrame([st.session_state.eval_results])
                st.dataframe(results_df, use_container_width=True)

                # Importance des features
                st.markdown("### Importance des features")

                metric = st.selectbox(
                    "Choisir une métrique",
                    list(st.session_state.predictor.models.keys())
                )

                importance_df = st.session_state.predictor.get_feature_importance(metric, top_n=10)

                if not importance_df.empty:
                    st.bar_chart(
                        data=importance_df.set_index('feature')['importance']
                    )

# PAGE VISUALISATION
elif page == "📈 Visualisation":
    st.header("Visualisations")

    if 'centrality_df' not in st.session_state:
        st.warning("⚠️ Calculez d'abord les métriques de centralité.")
    else:
        tab1, tab2 = st.tabs(["Distributions", "Corrélations"])

        with tab1:
            st.subheader("Distribution des métriques de centralité")

            metric = st.selectbox(
                "Choisir une métrique",
                ['degree', 'betweenness', 'closeness', 'eigenvector', 'pagerank']
            )

            col_name = f'centrality_{metric}'
            df = st.session_state.centrality_df

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Histogramme")
                st.bar_chart(df[col_name].value_counts().sort_index())

            with col2:
                st.markdown("#### Statistiques")
                st.metric("Moyenne", f"{df[col_name].mean():.4f}")
                st.metric("Médiane", f"{df[col_name].median():.4f}")
                st.metric("Écart-type", f"{df[col_name].std():.4f}")

        with tab2:
            st.subheader("Matrice de corrélation")

            # Sélectionner les colonnes de centralité
            centrality_cols = [col for col in st.session_state.centrality_df.columns
                              if col.startswith('centrality_')]

            corr = st.session_state.centrality_df[centrality_cols].corr()

            st.dataframe(corr, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Plateforme de Prédiction de Centralité Client | Master Data Science 2025-2026"
    "</div>",
    unsafe_allow_html=True
)

