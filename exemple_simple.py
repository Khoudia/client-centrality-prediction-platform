"""
Exemple simple d'utilisation de la plateforme.
Utilisez ce fichier comme point de départ pour vos propres analyses.
"""

from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import CentralityPredictor
from src.visualization.visualizer import NetworkVisualizer
from sklearn.model_selection import train_test_split
import pandas as pd


def exemple_complet():
    """
    Exemple complet : de la donnée à la prédiction.
    """
    print("=" * 60)
    print("EXEMPLE D'UTILISATION DE LA PLATEFORME")
    print("=" * 60)

    # ========================================
    # ÉTAPE 1 : CHARGER LES DONNÉES
    # ========================================
    print("\n1️⃣ CHARGEMENT DES DONNÉES")
    print("-" * 60)

    loader = DataLoader()

    # Générer des données d'exemple (ou utilisez vos propres données)
    df_clients = loader.generate_sample_data(n_clients=100)
    df_interactions = loader.generate_sample_interactions(n_interactions=500)

    print(f"✅ {len(df_clients)} clients chargés")
    print(f"✅ {len(df_interactions)} interactions chargées")

    # Aperçu des données
    print("\nAperçu des clients :")
    print(df_clients.head())

    # ========================================
    # ÉTAPE 2 : CONSTRUIRE LE RÉSEAU
    # ========================================
    print("\n\n2️⃣ CONSTRUCTION ET ANALYSE DU RÉSEAU")
    print("-" * 60)

    analyzer = NetworkAnalyzer(directed=False, weighted=True)
    graph = analyzer.build_network(df_interactions)

    # Statistiques du réseau
    stats = analyzer.get_network_statistics()
    print(f"✅ Réseau construit :")
    print(f"   - Nœuds : {stats['nb_nodes']}")
    print(f"   - Arêtes : {stats['nb_edges']}")
    print(f"   - Densité : {stats['density']:.4f}")
    print(f"   - Clustering moyen : {stats['avg_clustering']:.4f}")

    # ========================================
    # ÉTAPE 3 : CALCULER LES MÉTRIQUES
    # ========================================
    print("\n\n3️⃣ CALCUL DES MÉTRIQUES DE CENTRALITÉ")
    print("-" * 60)

    # Calculer toutes les métriques
    centrality_metrics = analyzer.calculate_all_centralities()
    centrality_df = analyzer.get_centrality_dataframe()

    print(f"✅ {len(centrality_metrics)} métriques calculées :")
    for metric in centrality_metrics.keys():
        print(f"   - {metric}")

    # Top 5 clients par centralité de degré
    print("\n📊 Top 5 clients (centralité de degré) :")
    top_5 = centrality_df.nlargest(5, 'centrality_degree')
    for i, row in enumerate(top_5.iterrows(), 1):
        print(f"   {i}. {row[1]['node_id']}: {row[1]['centrality_degree']:.4f}")

    # ========================================
    # ÉTAPE 4 : PRÉPARER LES DONNÉES ML
    # ========================================
    print("\n\n4️⃣ PRÉPARATION POUR LE MACHINE LEARNING")
    print("-" * 60)

    predictor = CentralityPredictor(model_type='random_forest')

    # Préparer les features et targets
    X, y = predictor.prepare_features(df_clients, centrality_df)
    print(f"✅ Features préparées : {X.shape}")
    print(f"✅ Targets préparées : {y.shape}")

    # Afficher les noms des features
    print(f"\n📋 Features utilisées ({len(X.columns)}) :")
    for i, col in enumerate(X.columns, 1):
        print(f"   {i}. {col}")

    # ========================================
    # ÉTAPE 5 : ENTRAÎNER LES MODÈLES
    # ========================================
    print("\n\n5️⃣ ENTRAÎNEMENT DES MODÈLES")
    print("-" * 60)

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"📊 Données divisées : {len(X_train)} train, {len(X_test)} test")

    # Entraîner
    print("\n🤖 Entraînement en cours...")
    training_scores = predictor.train(X_train, y_train)

    print("\n✅ Entraînement terminé !")
    print("\n📈 Scores de validation croisée (R²) :")
    if training_scores.get('cv_r2_mean') is not None:
        print(f"   • R² = {training_scores['cv_r2_mean']:.4f} "
              f"(+/- {training_scores['cv_r2_std']:.4f})")
    else:
        print(f"   • R² train = {training_scores['train_score']:.4f}")
        print(f"   • R² test = {training_scores['test_score']:.4f}")

    # ========================================
    # ÉTAPE 6 : ÉVALUER LES MODÈLES
    # ========================================
    print("\n\n6️⃣ ÉVALUATION SUR L'ENSEMBLE DE TEST")
    print("-" * 60)

    eval_results = predictor.evaluate(X_test, y_test)

    print("\n📊 Résultats sur le test :")
    print(f"   R² (coefficient de détermination) : {eval_results['r2']:.4f}")
    print(f"   RMSE (erreur quadratique moyenne) : {eval_results['rmse']:.4f}")
    print(f"   MAE (erreur absolue moyenne)      : {eval_results['mae']:.4f}")

    # ========================================
    # ÉTAPE 7 : IMPORTANCE DES FEATURES
    # ========================================
    print("\n\n7️⃣ IMPORTANCE DES FEATURES")
    print("-" * 60)

    # Pour la centralité de degré
    target = 'centrality_degree'
    importance_df = predictor.get_feature_importance(target, top_n=5)

    print(f"\n🔍 Top 5 features pour {target} :")
    for i, row in enumerate(importance_df.iterrows(), 1):
        print(f"   {i}. {row[1]['feature']}: {row[1]['importance']:.4f}")

    # ========================================
    # ÉTAPE 8 : FAIRE DES PRÉDICTIONS
    # ========================================
    print("\n\n8️⃣ PRÉDICTIONS SUR DE NOUVELLES DONNÉES")
    print("-" * 60)

    # Prédire sur l'ensemble de test
    predictions = predictor.predict(X_test)

    print(f"✅ {len(predictions)} prédictions générées")

    # Afficher quelques prédictions
    print("\n📊 Exemples de prédictions vs réalité :")
    for i in range(min(3, len(predictions))):
        print(f"\n   Observation {i+1} :")
        print(f"      Centralité de degré :")
        print(f"         Réel : {y_test.iloc[i]:.4f}")
        print(f"         Prédit : {predictions[i]:.4f}")

    # ========================================
    # ÉTAPE 9 : SAUVEGARDER LES MODÈLES
    # ========================================
    print("\n\n9️⃣ SAUVEGARDE DES MODÈLES")
    print("-" * 60)

    predictor.save_models(prefix='exemple_model')
    print("✅ Modèles sauvegardés dans le dossier 'models/'")

    # ========================================
    # RÉSUMÉ
    # ========================================
    print("\n\n" + "=" * 60)
    print("✅ EXEMPLE TERMINÉ AVEC SUCCÈS !")
    print("=" * 60)
    print("\n📚 Pour aller plus loin :")
    print("   • Explorez l'application web : streamlit run app.py")
    print("   • Consultez les notebooks dans 'notebooks/'")
    print("   • Lisez la documentation dans 'docs/'")
    print("   • Testez avec vos propres données !")
    print("\n")


if __name__ == '__main__':
    exemple_complet()
