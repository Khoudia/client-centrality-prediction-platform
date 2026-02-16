# Documentation Technique

## Architecture du Projet

### Vue d'ensemble

La plateforme de prédiction de centralité client est structurée en modules indépendants et réutilisables :

```
client-centrality-prediction-platform/
├── src/                    # Code source
│   ├── data/              # Gestion des données
│   ├── network/           # Analyse de réseau
│   ├── models/            # Modèles ML
│   ├── visualization/     # Visualisation
│   └── utils/             # Utilitaires
├── tests/                 # Tests unitaires
├── notebooks/             # Notebooks Jupyter
├── data/                  # Données
├── models/                # Modèles entraînés
├── config/                # Configuration
└── docs/                  # Documentation
```

## Modules Principaux

### 1. Module Data (`src/data/`)

**DataLoader** : Gestion du chargement et du prétraitement des données

**Méthodes principales :**
- `load_client_data()` : Charge les données clients
- `load_interaction_data()` : Charge les interactions
- `generate_sample_data()` : Génère des données d'exemple
- `preprocess_data()` : Prétraite les données
- `split_train_test()` : Divise en train/test

### 2. Module Network (`src/network/`)

**NetworkAnalyzer** : Analyse des réseaux et calcul des métriques de centralité

**Méthodes principales :**
- `build_network()` : Construit le graphe NetworkX
- `calculate_degree_centrality()` : Centralité de degré
- `calculate_betweenness_centrality()` : Centralité d'intermédiarité
- `calculate_closeness_centrality()` : Centralité de proximité
- `calculate_eigenvector_centrality()` : Centralité de vecteur propre
- `calculate_pagerank_centrality()` : PageRank
- `calculate_all_centralities()` : Calcule toutes les métriques
- `detect_communities()` : Détection de communautés

### 3. Module Models (`src/models/`)

**CentralityPredictor** : Modèles de prédiction de centralité

**Modèles supportés :**
- Random Forest
- XGBoost
- Gradient Boosting

**Méthodes principales :**
- `prepare_features()` : Prépare les features
- `train()` : Entraîne les modèles
- `predict()` : Génère des prédictions
- `evaluate()` : Évalue les modèles
- `save_models()` / `load_models()` : Sauvegarde/charge
- `hyperparameter_tuning()` : Optimise les hyperparamètres

### 4. Module Visualization (`src/visualization/`)

**NetworkVisualizer** : Visualisation des réseaux et résultats

**Méthodes principales :**
- `plot_network()` : Visualise le réseau
- `plot_centrality_distribution()` : Distribution d'une métrique
- `plot_centrality_comparison()` : Compare les métriques
- `plot_feature_importance()` : Importance des features
- `plot_prediction_results()` : Résultats de prédiction
- `plot_correlation_matrix()` : Matrice de corrélation

## Métriques de Centralité

### 1. Centralité de Degré
Mesure le nombre de connexions directes d'un nœud.
```
C_D(v) = deg(v) / (n - 1)
```

### 2. Centralité d'Intermédiarité
Mesure à quel point un nœud est sur le chemin le plus court entre d'autres nœuds.
```
C_B(v) = Σ(σ_st(v) / σ_st)
```

### 3. Centralité de Proximité
Mesure la proximité moyenne d'un nœud à tous les autres.
```
C_C(v) = (n - 1) / Σd(v, t)
```

### 4. Centralité de Vecteur Propre
Mesure l'influence d'un nœud basée sur l'influence de ses voisins.

### 5. PageRank
Algorithme utilisé par Google, mesure l'importance relative.

## Workflow Typique

### 1. Chargement des Données
```python
from src.data.data_loader import DataLoader

loader = DataLoader()
df_clients = loader.load_client_data('clients.csv')
df_interactions = loader.load_interaction_data('interactions.csv')
```

### 2. Construction et Analyse du Réseau
```python
from src.network.network_analyzer import NetworkAnalyzer

analyzer = NetworkAnalyzer()
graph = analyzer.build_network(df_interactions)
centrality_metrics = analyzer.calculate_all_centralities()
centrality_df = analyzer.get_centrality_dataframe()
```

### 3. Entraînement des Modèles
```python
from src.models.predictor import CentralityPredictor

predictor = CentralityPredictor(model_type='random_forest')
X, y = predictor.prepare_features(df_clients, centrality_df)

# Split et entraînement
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
predictor.train(X_train, y_train)

# Évaluation
eval_results = predictor.evaluate(X_test, y_test)
```

### 4. Visualisation
```python
from src.visualization.visualizer import NetworkVisualizer

visualizer = NetworkVisualizer()
visualizer.plot_network(graph)
visualizer.plot_centrality_comparison(centrality_df)
```

## Configuration

Le fichier `config/config.yaml` contient tous les paramètres configurables :

- Chemins des données
- Paramètres du réseau
- Métriques à calculer
- Hyperparamètres des modèles
- Paramètres de validation
- Style de visualisation

## Tests

Exécuter tous les tests :
```bash
pytest tests/ -v
```

Exécuter avec couverture :
```bash
pytest tests/ --cov=src --cov-report=html
```

## Déploiement de l'Application Web

Lancer l'application Streamlit :
```bash
streamlit run app.py
```

L'application sera accessible à `http://localhost:8501`

## Bonnes Pratiques

1. **Données** : Toujours vérifier la qualité des données avant l'analyse
2. **Réseau** : Vérifier la connexité du graphe avant certains calculs
3. **Modèles** : Utiliser la validation croisée pour éviter le surapprentissage
4. **Performance** : Pour les grands réseaux, considérer l'échantillonnage

## Dépendances Principales

- **NetworkX** : Analyse de réseaux
- **Scikit-learn** : Machine Learning
- **XGBoost** : Gradient Boosting optimisé
- **Pandas/NumPy** : Manipulation de données
- **Matplotlib/Seaborn** : Visualisation
- **Streamlit** : Interface web

## Références

- Newman, M. E. J. (2010). Networks: An Introduction
- Barabási, A.-L. (2016). Network Science
- Documentation NetworkX : https://networkx.org/
- Documentation Scikit-learn : https://scikit-learn.org/

