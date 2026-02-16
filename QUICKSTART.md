# 🚀 Démarrage Rapide

## ✅ Installation Rapide

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Tester l'installation avec la démo
```bash
python demo.py
```

### 3. Lancer l'application web
```bash
streamlit run app.py
```

## 📁 Structure du Projet

```
client-centrality-prediction-platform/
│
├── 📄 main.py                    # Script principal
├── 📄 app.py                     # Application web Streamlit
├── 📄 demo.py                    # Script de démonstration
├── 📄 requirements.txt           # Dépendances Python
├── 📄 README.md                  # Documentation principale
├── 📄 CHANGELOG.md               # Historique des versions
├── 📄 .gitignore                 # Fichiers à ignorer par Git
│
├── 📂 src/                       # Code source
│   ├── 📂 data/                 # Gestion des données
│   │   ├── __init__.py
│   │   └── data_loader.py       # Chargement et prétraitement
│   │
│   ├── 📂 network/              # Analyse de réseau
│   │   ├── __init__.py
│   │   └── network_analyzer.py  # Calcul des métriques de centralité
│   │
│   ├── 📂 models/               # Modèles prédictifs
│   │   ├── __init__.py
│   │   └── predictor.py         # Random Forest, XGBoost, etc.
│   │
│   ├── 📂 visualization/        # Visualisations
│   │   ├── __init__.py
│   │   └── visualizer.py        # Graphiques et plots
│   │
│   └── 📂 utils/                # Utilitaires
│       ├── __init__.py
│       ├── logger.py            # Système de logging
│       └── config.py            # Gestion de la configuration
│
├── 📂 tests/                    # Tests unitaires
│   ├── __init__.py
│   ├── test_data_loader.py
│   └── test_network_analyzer.py
│
├── 📂 notebooks/                # Notebooks Jupyter
│   ├── 01_exploration_donnees.md
│   └── 02_modelisation.md
│
├── 📂 docs/                     # Documentation
│   ├── TECHNICAL_DOCUMENTATION.md
│   ├── USER_GUIDE.md
│   └── MEMOIRE_GUIDE.md
│
├── 📂 config/                   # Configuration
│   └── config.yaml              # Paramètres du projet
│
├── 📂 data/                     # Données
│   ├── raw/                     # Données brutes
│   └── processed/               # Données traitées
│
├── 📂 models/                   # Modèles sauvegardés
├── 📂 logs/                     # Fichiers de logs
└── 📂 outputs/                  # Sorties
    └── figures/                 # Graphiques générés
```

## 🎯 Fonctionnalités Principales

### 1️⃣ Chargement de Données
- Support CSV, Excel, Parquet
- Génération de données d'exemple
- Prétraitement automatique
- Division train/test

### 2️⃣ Analyse de Réseau
- Construction de graphes NetworkX
- 5 métriques de centralité :
  - ✅ Centralité de degré
  - ✅ Centralité d'intermédiarité
  - ✅ Centralité de proximité
  - ✅ Centralité de vecteur propre
  - ✅ PageRank
- Statistiques du réseau
- Détection de communautés

### 3️⃣ Modèles Prédictifs
- 3 algorithmes ML :
  - 🌲 Random Forest
  - 🚀 XGBoost
  - 📊 Gradient Boosting
- Validation croisée
- Optimisation des hyperparamètres
- Importance des features
- Sauvegarde/chargement de modèles

### 4️⃣ Visualisations
- Graphes de réseaux
- Distributions de centralité
- Comparaisons de métriques
- Matrices de corrélation
- Importance des features
- Résultats de prédictions

### 5️⃣ Application Web
- Interface Streamlit interactive
- Navigation intuitive
- Visualisations en temps réel
- Export des résultats

## 📊 Exemple d'Utilisation

### Utilisation Basique (Python)

```python
from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import CentralityPredictor

# 1. Charger les données
loader = DataLoader()
df_clients = loader.generate_sample_data(100)
df_interactions = loader.generate_sample_interactions(500)

# 2. Analyser le réseau
analyzer = NetworkAnalyzer()
graph = analyzer.build_network(df_interactions)
centrality_df = analyzer.get_centrality_dataframe()

# 3. Prédire la centralité
predictor = CentralityPredictor(model_type='random_forest')
X, y = predictor.prepare_features(df_clients, centrality_df)
predictor.train(X_train, y_train)
predictions = predictor.predict(X_test)
```

### Utilisation avec l'Interface Web

1. Lancez : `streamlit run app.py`
2. Ouvrez : `http://localhost:8501`
3. Naviguez dans les onglets :
   - 🏠 Accueil
   - 📊 Données
   - 🕸️ Réseau
   - 🤖 Prédiction
   - 📈 Visualisation

## 🧪 Tests

### Exécuter tous les tests
```bash
pytest tests/ -v
```

### Tests avec couverture
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentation

- **Guide Utilisateur** : `docs/USER_GUIDE.md`
- **Documentation Technique** : `docs/TECHNICAL_DOCUMENTATION.md`
- **Guide pour le Mémoire** : `docs/MEMOIRE_GUIDE.md`

## 🎓 Pour votre Mémoire

Ce projet est conçu pour être un projet complet de Master en Data Science. Consultez le guide du mémoire pour :

- Structure proposée (100-140 pages)
- Plan détaillé par chapitre
- Méthodologie de recherche
- Timeline suggérée (12 mois)
- Conseils de rédaction

## 🛠️ Technologies Utilisées

- **Python 3.9+**
- **NetworkX** : Analyse de réseaux
- **Scikit-learn** : Machine Learning
- **XGBoost** : Gradient Boosting
- **Pandas & NumPy** : Manipulation de données
- **Matplotlib & Seaborn** : Visualisation
- **Streamlit** : Interface web
- **Pytest** : Tests unitaires

## 📈 Roadmap

### Version 1.0 (Actuelle) ✅
- [x] Structure complète du projet
- [x] Modules principaux
- [x] Application web
- [x] Documentation
- [x] Tests unitaires

### Version 1.1 (À venir)
- [ ] Support des réseaux dynamiques
- [ ] Modèles Deep Learning
- [ ] API REST
- [ ] Dashboard temps réel

### Version 2.0 (Future)
- [ ] Scalabilité (Big Data)
- [ ] Déploiement Cloud
- [ ] Module de recommandation
- [ ] Intégration CRM

## 🤝 Contribution

Pour contribuer :
1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est développé dans le cadre d'un mémoire de Master en Data Science.

## 👤 Auteur

Projet de mémoire - Master Data Science (2025-2026)

## 🙏 Remerciements

- NetworkX community
- Scikit-learn developers
- Streamlit team
- Communauté Python

---

**Bon courage pour votre mémoire ! 🎓🚀**

