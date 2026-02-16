# Notebook d'exploration des données

Ce notebook permet d'explorer les données clients et les interactions.

## Import des bibliothèques

```python
import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.visualization.visualizer import NetworkVisualizer

%matplotlib inline
```

## Chargement des données

```python
# Initialiser le loader
loader = DataLoader()

# Générer des données d'exemple
df_clients = loader.generate_sample_data(n_clients=100)
df_interactions = loader.generate_sample_interactions(n_interactions=500)

# Afficher les premières lignes
print("Données clients:")
display(df_clients.head())

print("\nDonnées interactions:")
display(df_interactions.head())
```

## Analyse exploratoire

```python
# Statistiques descriptives
print("Statistiques des clients:")
display(df_clients.describe())

# Distribution de l'âge
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.hist(df_clients['age'], bins=20, edgecolor='black')
plt.xlabel('Âge')
plt.ylabel('Fréquence')
plt.title('Distribution de l\'âge des clients')

# Distribution du chiffre d'affaires
plt.subplot(1, 2, 2)
plt.hist(df_clients['chiffre_affaires'], bins=20, edgecolor='black')
plt.xlabel('Chiffre d\'affaires')
plt.ylabel('Fréquence')
plt.title('Distribution du CA')
plt.tight_layout()
plt.show()
```

## Analyse du réseau

```python
# Construire le réseau
analyzer = NetworkAnalyzer()
graph = analyzer.build_network(df_interactions)

# Statistiques du réseau
stats = analyzer.get_network_statistics()
print("Statistiques du réseau:")
for key, value in stats.items():
    print(f"  {key}: {value}")

# Calculer les métriques de centralité
centrality_metrics = analyzer.calculate_all_centralities()
centrality_df = analyzer.get_centrality_dataframe()

print("\nTop 10 clients par centralité de degré:")
display(centrality_df.nlargest(10, 'centrality_degree')[['node_id', 'centrality_degree']])
```

## Visualisation

```python
# Initialiser le visualizer
visualizer = NetworkVisualizer()

# Comparer les métriques de centralité
visualizer.plot_centrality_comparison(
    centrality_df,
    title="Comparaison des Métriques de Centralité"
)

# Matrice de corrélation
centrality_cols = [col for col in centrality_df.columns if col.startswith('centrality_')]
visualizer.plot_correlation_matrix(
    centrality_df[centrality_cols],
    title="Corrélations entre Métriques de Centralité"
)
```

