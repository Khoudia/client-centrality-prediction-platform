# 🎓 Client Centrality Prediction Platform - Guide de Démarrage Rapide

## 📋 Statut du Projet

✅ **TOUS LES MODULES SONT MAINTENANT CORRIGÉS ET FONCTIONNELS**

Les erreurs de syntaxe ont été résolues :
- ✅ Suppression des caractères BOM (Byte Order Mark) dans les fichiers
- ✅ Importations circulaires corrigées
- ✅ Implémentations complètes créées pour tous les modules
- ✅ Tests d'import validés

## 🚀 Démarrage en 3 Étapes

### Étape 1 : Installation

**Option A - Automatique (Windows)**
```bash
double-cliquez sur : install_new.bat
```

**Option B - Manuel**
```bash
pip install -r requirements_minimal.txt
```

### Étape 2 : Test des Imports

```bash
python test_full_imports.py
```

Résultat attendu :
```
[OK] DataLoader importé avec succès
[OK] NetworkAnalyzer importé avec succès
[OK] CentralityPredictor importé avec succès
[OK] NetworkVisualizer importé avec succès
```

### Étape 3 : Exécution de la Démo

**Option A - Démo Simple**
```bash
python simple_demo.py
```

**Option B - Démo Complète (avec visualisations)**
```bash
python demo.py
```

**Option C - Application Web (Recommandé)**
```bash
streamlit run app.py
```

Cela ouvre automatiquement http://localhost:8501

## 📁 Structure du Projet

```
client-centrality-prediction-platform/
├── src/                        # Code source principal
│   ├── data/                   # Module de chargement de données
│   │   └── data_loader.py      # Classe DataLoader
│   ├── network/                # Module d'analyse de réseau
│   │   └── network_analyzer.py # Classe NetworkAnalyzer
│   ├── models/                 # Module de prédiction
│   │   └── predictor.py        # Classe CentralityPredictor
│   ├── visualization/          # Module de visualisation
│   │   └── visualizer.py       # Classe NetworkVisualizer
│   └── utils/                  # Utilitaires
│       ├── config.py
│       └── logger.py
├── tests/                      # Tests unitaires
├── notebooks/                  # Notebooks Jupyter
├── docs/                       # Documentation
├── data/                       # Données (entrée/sortie)
├── outputs/                    # Figures générées
├── models/                     # Modèles sauvegardés
├── logs/                       # Fichiers de logs
├── app.py                      # Application Streamlit
├── demo.py                     # Démonstration complète
├── simple_demo.py              # Démonstration simple
├── exemple_simple.py           # Exemple d'utilisation
├── requirements.txt            # Dépendances complètes
├── requirements_minimal.txt    # Dépendances minimales
└── README.md                   # Documentation
```

## 🎯 Modules Disponibles

### DataLoader
```python
from src.data.data_loader import DataLoader

loader = DataLoader()
clients = loader.generate_sample_data(n_clients=100)
interactions = loader.generate_sample_interactions(n_interactions=500)
```

### NetworkAnalyzer
```python
from src.network.network_analyzer import NetworkAnalyzer

analyzer = NetworkAnalyzer()
graph = analyzer.build_network(interactions)
metrics = analyzer.calculate_all_centralities()
df = analyzer.get_centrality_dataframe()
```

### CentralityPredictor
```python
from src.models.predictor import CentralityPredictor

predictor = CentralityPredictor(model_type='random_forest')
X, y = predictor.prepare_features(clients, metrics)
predictor.train(X, y)
predictions = predictor.predict(X_test)
```

### NetworkVisualizer
```python
from src.visualization.visualizer import NetworkVisualizer

viz = NetworkVisualizer()
viz.plot_network(graph)
viz.plot_centrality_comparison(df)
viz.plot_feature_importance(importance_df)
```

## 🛠️ Dépendances Minimales

Les bibliothèques essentielles installées :
- numpy, pandas, scipy (données)
- scikit-learn, networkx (ML et réseaux)
- matplotlib, seaborn, plotly (visualisation)
- streamlit (interface web)
- joblib (sauvegarde modèles)

Optionnel (pour meilleures performances) :
- xgboost, lightgbm

## ⚠️ Résolution de Problèmes

### Python ne fonctionne pas

**Solution** : Assurez-vous que Python 3.9+ est installé et ajouté au PATH
```bash
python --version
```

### Erreur d'import lors de `import streamlit`

**Solution** : Installez streamlit
```bash
pip install streamlit
```

### Erreur "ModuleNotFoundError: No module named 'src'"

**Solution** : Assurez-vous d'exécuter les scripts depuis le dossier racine du projet
```bash
cd C:\Users\KFA24632\client-centrality-prediction-platform
python simple_demo.py
```

### Pas de graphiques générés

**Solution** : Créez le dossier de sortie
```bash
mkdir outputs/figures
```

## 📊 Fichiers de Test

**test_full_imports.py** - Teste tous les imports et affiche les méthodes disponibles
```bash
python test_full_imports.py
```

**test_imports_simple.py** - Test basique des imports
```bash
python test_imports_simple.py
```

## 📚 Documentation Complète

Pour plus d'informations, consultez :
- `COMMENCER_ICI.md` - Guide de démarrage complet
- `PROJET_PRET.md` - Vue d'ensemble du projet
- `docs/USER_GUIDE.md` - Guide utilisateur détaillé
- `docs/TECHNICAL_DOCUMENTATION.md` - Documentation technique
- `docs/MEMOIRE_GUIDE.md` - Guide pour votre mémoire

## 🎓 Utilisation pour votre Mémoire

Ce projet fournit :
- ✅ **Architecture modulaire** : Facile à comprendre et à étendre
- ✅ **Code documenté** : Docstrings pour toutes les classes et méthodes
- ✅ **Exemples fonctionnels** : Scripts démo et notebooks
- ✅ **Interface web** : Pour tester rapidement
- ✅ **Guide complet** : Pour rédiger votre mémoire

**Prochaines étapes** :
1. Exécutez `simple_demo.py` pour voir le projet en action
2. Consultez `docs/MEMOIRE_GUIDE.md` pour la structure de votre mémoire
3. Adaptez le code à vos besoins spécifiques
4. Générez vos résultats avec `app.py`

## ✅ Vérification Finale

Pour confirmer que tout fonctionne :

```bash
# 1. Test des imports
python test_full_imports.py

# 2. Démonstration simple
python simple_demo.py

# 3. Application web
streamlit run app.py

# 4. Tests unitaires (optionnel)
pytest tests/ -v
```

**Si tous les tests passent, votre plateforme est prête ! 🎉**

## 📞 Notes Importantes

- Tous les fichiers `__init__.py` ont été corrigés (suppression des BOM)
- Tous les modules implémentent les classes attendues
- Les importations circulaires ont été résolues
- Le code est compatible Python 3.9+

**Bon travail ! Votre plateforme de mémoire est maintenant fonctionnelle ! 🚀**

