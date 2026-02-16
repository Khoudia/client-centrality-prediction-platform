# Guide Utilisateur

## Introduction

Bienvenue dans la Plateforme de Prédiction de Centralité Client ! Cette application vous permet d'analyser les réseaux de clients et de prédire leur centralité.

## Installation

### Prérequis
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le projet**
```bash
cd client-centrality-prediction-platform
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Vérifier l'installation**
```bash
python main.py
```

## Utilisation de l'Application Web

### Lancement
```bash
streamlit run app.py
```

Ouvrez votre navigateur à l'adresse : `http://localhost:8501`

### Navigation

#### 🏠 Accueil
- Vue d'ensemble du projet
- Objectifs et fonctionnalités
- Guide d'utilisation rapide

#### 📊 Données
**Onglet "Charger les données"**
- Chargez vos propres fichiers (CSV/Excel)
- Ou générez des données d'exemple pour tester

**Format des données attendu :**

**Fichier Clients :**
| client_id | age | anciennete_mois | chiffre_affaires | nb_transactions | segment | score_satisfaction |
|-----------|-----|-----------------|------------------|-----------------|---------|-------------------|
| C0001     | 35  | 24              | 15000            | 120             | Gold    | 4.5               |

**Fichier Interactions :**
| client_source | client_target | weight | type_interaction |
|---------------|---------------|--------|------------------|
| C0001         | C0002         | 0.8    | recommandation   |

**Onglet "Données clients"**
- Aperçu des données chargées
- Statistiques descriptives
- Métriques clés

**Onglet "Interactions"**
- Aperçu des interactions
- Statistiques sur les connexions

#### 🕸️ Réseau
**Onglet "Construction & Stats"**
1. Cliquez sur "🔨 Construire le réseau"
2. Consultez les statistiques :
   - Nombre de nœuds et d'arêtes
   - Densité du réseau
   - Connexité
   - Coefficient de clustering

**Onglet "Métriques de centralité"**
1. Cliquez sur "📊 Calculer toutes les métriques"
2. Explorez les différentes métriques :
   - Centralité de degré
   - Centralité d'intermédiarité
   - Centralité de proximité
   - Centralité de vecteur propre
   - PageRank
3. Visualisez le top 10 des clients pour chaque métrique

#### 🤖 Prédiction
**Onglet "Entraînement"**
1. Choisissez le type de modèle :
   - Random Forest (recommandé pour débuter)
   - XGBoost (meilleure performance)
   - Gradient Boosting (bon compromis)
2. Ajustez la proportion de test (par défaut 20%)
3. Cliquez sur "🚀 Entraîner les modèles"
4. Consultez les résultats d'entraînement

**Onglet "Évaluation"**
- Consultez les métriques de performance (R², MSE, RMSE, MAE)
- Visualisez l'importance des features
- Identifiez les variables les plus prédictives

#### 📈 Visualisation
**Onglet "Distributions"**
- Sélectionnez une métrique de centralité
- Observez la distribution des valeurs
- Consultez les statistiques (moyenne, médiane, écart-type)

**Onglet "Corrélations"**
- Matrice de corrélation entre les métriques
- Identifiez les relations entre différentes centralités

## Utilisation en Ligne de Commande

### Script Principal
```bash
python main.py
```

Ce script exécute le workflow complet :
1. Chargement des données
2. Analyse du réseau
3. Entraînement des modèles
4. Génération des visualisations

### Personnalisation
Modifiez le fichier `config/config.yaml` pour :
- Changer les chemins des données
- Ajuster les hyperparamètres des modèles
- Modifier les métriques calculées
- Personnaliser les visualisations

## Utilisation avec Jupyter Notebooks

Deux notebooks sont fournis dans le dossier `notebooks/` :

### 1. Exploration des données
```bash
jupyter notebook notebooks/01_exploration_donnees.md
```
- Chargement et exploration des données
- Analyse statistique
- Premières visualisations

### 2. Modélisation
```bash
jupyter notebook notebooks/02_modelisation.md
```
- Préparation des features
- Entraînement des modèles
- Évaluation et comparaison
- Optimisation des hyperparamètres

## Cas d'Usage Typiques

### Cas 1 : Identifier les clients influents
1. Chargez vos données clients et interactions
2. Construisez le réseau
3. Calculez la centralité de degré et PageRank
4. Identifiez le top 10% des clients les plus centraux
5. Utilisez ces informations pour vos campagnes marketing

### Cas 2 : Prédire la centralité de nouveaux clients
1. Entraînez les modèles sur les clients existants
2. Pour chaque nouveau client, collectez ses caractéristiques
3. Utilisez le modèle pour prédire sa centralité future
4. Adaptez votre stratégie d'engagement en conséquence

### Cas 3 : Analyser les communautés
1. Construisez le réseau
2. Détectez les communautés (méthode Louvain)
3. Analysez les caractéristiques de chaque communauté
4. Personnalisez vos offres par communauté

## Interprétation des Résultats

### Métriques de Centralité

**Centralité de Degré** (0-1)
- Valeur élevée = Client très connecté
- Utilisation : Identifier les hubs du réseau

**Centralité d'Intermédiarité** (0-1)
- Valeur élevée = Client pont entre groupes
- Utilisation : Identifier les connecteurs

**Centralité de Proximité** (0-1)
- Valeur élevée = Client proche de tous
- Utilisation : Diffusion d'information

**PageRank** (0-1)
- Valeur élevée = Client influent
- Utilisation : Marketing d'influence

### Métriques de Performance des Modèles

**R² (Coefficient de détermination)** (0-1)
- > 0.7 : Très bon modèle
- 0.5-0.7 : Bon modèle
- < 0.5 : Modèle à améliorer

**RMSE (Root Mean Squared Error)**
- Plus faible = meilleur
- À comparer avec l'échelle des valeurs

**MAE (Mean Absolute Error)**
- Erreur moyenne en unités originales
- Facile à interpréter

## Résolution de Problèmes

### Le réseau n'est pas connexe
- C'est normal pour certains réseaux
- Certaines métriques (diamètre) ne seront pas calculées
- Considérez l'analyse par composante connexe

### Les prédictions sont mauvaises
- Vérifiez la qualité des données
- Augmentez la taille de l'échantillon
- Essayez différents types de modèles
- Ajoutez plus de features pertinentes

### L'application est lente
- Réduisez la taille du réseau
- Utilisez l'échantillonnage
- Désactivez certaines visualisations

## Support

Pour toute question ou problème :
1. Consultez la documentation technique
2. Vérifiez les logs dans le dossier `logs/`
3. Consultez les exemples dans `notebooks/`

## Bonnes Pratiques

1. **Commencez petit** : Testez avec des données d'exemple
2. **Validez vos données** : Vérifiez la qualité avant l'analyse
3. **Documentez** : Notez vos paramètres et résultats
4. **Itérez** : Testez différentes configurations
5. **Sauvegardez** : Exportez régulièrement vos résultats

