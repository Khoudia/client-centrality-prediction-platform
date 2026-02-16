# Notebook de modélisation

Ce notebook couvre l'entraînement et l'évaluation des modèles de prédiction.

## Import et préparation

```python
import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import CentralityPredictor
from src.visualization.visualizer import NetworkVisualizer

%matplotlib inline
```

## Préparation des données

```python
# Charger les données
loader = DataLoader()
df_clients = loader.generate_sample_data(n_clients=100)
df_interactions = loader.generate_sample_interactions(n_interactions=500)

# Construire le réseau et calculer les métriques
analyzer = NetworkAnalyzer()
graph = analyzer.build_network(df_interactions)
centrality_metrics = analyzer.calculate_all_centralities()
centrality_df = analyzer.get_centrality_dataframe()

print(f"Données préparées: {len(df_clients)} clients, {len(centrality_df)} nœuds")
```

## Entraînement des modèles

```python
# Initialiser le prédicteur
predictor = CentralityPredictor(model_type='random_forest')

# Préparer les features
X, y = predictor.prepare_features(df_clients, centrality_df)

print(f"Features: {X.shape}")
print(f"Targets: {y.shape}")

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Entraîner les modèles
training_scores = predictor.train(X_train, y_train)

print("\nScores d'entraînement (validation croisée):")
for metric, scores in training_scores.items():
    print(f"  {metric}: R² = {scores['cv_r2_mean']:.4f} (+/- {scores['cv_r2_std']:.4f})")
```

## Évaluation

```python
# Évaluer sur l'ensemble de test
eval_results = predictor.evaluate(X_test, y_test)

# Afficher les résultats
results_df = pd.DataFrame(eval_results).T
display(results_df)

# Visualiser les résultats pour une métrique
visualizer = NetworkVisualizer()
metric = 'centrality_degree'

if metric in predictor.models:
    y_pred = predictor.models[metric].predict(X_test)
    visualizer.plot_prediction_results(
        y_test[metric],
        y_pred,
        metric_name=metric
    )
```

## Importance des features

```python
# Analyser l'importance des features
for target in predictor.models.keys():
    importance_df = predictor.get_feature_importance(target, top_n=10)
    
    if not importance_df.empty:
        print(f"\nImportance des features pour {target}:")
        display(importance_df)
        
        visualizer.plot_feature_importance(
            importance_df,
            title=f"Importance des Features - {target}"
        )
```

## Comparaison de modèles

```python
# Comparer différents types de modèles
model_types = ['random_forest', 'xgboost', 'gradient_boosting']
comparison_results = {}

for model_type in model_types:
    print(f"\n=== Entraînement {model_type} ===")
    
    predictor_temp = CentralityPredictor(model_type=model_type)
    predictor_temp.train(X_train, y_train)
    eval_results = predictor_temp.evaluate(X_test, y_test)
    
    comparison_results[model_type] = eval_results

# Créer un DataFrame de comparaison
comparison_data = []
for model_type, results in comparison_results.items():
    for metric, scores in results.items():
        comparison_data.append({
            'model': model_type,
            'metric': metric,
            'r2': scores['r2'],
            'rmse': scores['rmse'],
            'mae': scores['mae']
        })

comparison_df = pd.DataFrame(comparison_data)
display(comparison_df)
```

## Sauvegarde des modèles

```python
# Sauvegarder le meilleur modèle
predictor.save_models(prefix='best_model')
print("Modèles sauvegardés dans le dossier 'models/'")
```

