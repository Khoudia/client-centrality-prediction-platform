# 🏨 Hôtel Aurore Paris — Analyse Réseau & Satisfaction Client

Plateforme d'analyse de données hôtelières basée sur les **vraies données** de l'Hôtel Aurore Paris Gare de Lyon.  
**DU SDA — Université Paris-Sorbonne — 2025-2026**

---

## 🎯 Objectifs

| # | Objectif |
|---|----------|
| 1 | Charger et nettoyer les données de réservations (AvailPro) et d'avis (Booking.com, Expedia) |
| 2 | Construire un **réseau de similarité** entre profils clients/séjours |
| 3 | Calculer des **métriques de centralité** (PageRank, Betweenness, Eigenvector, Closeness) |
| 4 | Détecter des **communautés** de clients similaires (Greedy / Label Propagation / Louvain) |
| 5 | **Modéliser la satisfaction client** (classification ≥8/10 ou régression note) |
| 6 | Visualiser et exporter les résultats via une **application Streamlit** |

---

## 📊 Résultats obtenus (données réelles — validés le 06/04/2026)

| Indicateur | Valeur |
|------------|--------|
| Réservations chargées | **6 474** |
| Clients uniques | **6 427** |
| Avis Booking matchés | **316** (sur 1 634) |
| Avis Expedia | **208** |
| Note moyenne Booking | **7.58 / 10** |
| Haute satisfaction (≥8) | **188 clients** |
| Canaux principaux | Expedia Group 54%, Booking 36%, Other OTA 10% |
| Chambres | Standard 52%, Supérieure 43%, Familiale 5% |
| **Réseau — Nœuds** | **500** (validation complète) |
| **Réseau — Arêtes** | **88 375** |
| **Réseau — Densité** | **0.708** |
| **Réseau — Modularité** | **0.205** |
| **Modèle RF — Accuracy** | **85.8%** |
| **Modèle GB — Accuracy** | **96.6%** ⭐ meilleur |
| **ROC-AUC RF** | **91.8%** |
| **CV 5-fold RF** | **91.5%** |

**Top features prédictives observées** : `channel_group`, `pays`, `is_cancelled`, `lead_time_days`, `revenue`

---

## 📁 Structure du projet

```
client-centrality-prediction-platform/
├── app.py                           # Application Streamlit (7 pages)
├── requirements.txt                 # Dépendances Python
├── data-projet-sorbonne/            # ⚠️ Données brutes (non versionnées)
│   ├── availpro_export.xlsx         # 6 500 réservations AvailPro
│   ├── données avis booking.csv     # 1 634 avis Booking.com (source unique)
│   └── expediareviews_*.csv         # 208 avis Expedia (tab-séparé)
├── data/processed/                  # Datasets générés automatiquement
│   └── hotel_dataset_final.csv      # Dataset principal (6 474 lignes, 82 cols)
├── models/                          # Modèles sauvegardés (.joblib)
├── outputs/figures/                 # Graphiques exportés (.png)
└── src/
    ├── data/data_loader.py          # Chargement, nettoyage, fusion
    ├── network/network_analyzer.py  # Graphe de similarité, centralités, communautés
    ├── models/predictor.py          # Modèle de satisfaction (RF / GB / XGB)
    └── visualization/visualizer.py  # 11 types de graphiques
```

---

## 🚀 Démarrage rapide

### 1. Installation des dépendances

```powershell
pip install -r requirements.txt
```

### 2. Lancement de l'application Streamlit

```powershell
python -m streamlit run app.py
```

→ L'application démarre sur **http://localhost:8501**

### 3. Pipeline automatique (recommandé)

Dans la barre latérale, cliquez sur **"🚀 Tout exécuter (pipeline)"** pour :
- Charger les 3 fichiers de données
- Nettoyer et fusionner les données
- Construire le graphe de similarité (800 nœuds max par défaut)
- Calculer les métriques réseau (degree, betweenness, pagerank, eigenvector, closeness)
- Détecter les communautés (méthode greedy)
- Entraîner le modèle Random Forest

### 4. Mode pas à pas

| Page | Action |
|------|--------|
| 📂 Chargement | Charger AvailPro + Booking + Expedia |
| 🧹 Préparation | Nettoyer, créer les variables dérivées, fusionner |
| 🕸️ Réseau | Construire le graphe, calculer les métriques |
| 🤖 Satisfaction | Entraîner le modèle de prédiction |
| 📊 Visualisations | Explorer les 11 graphiques disponibles |
| 💾 Export | Télécharger CSV/Excel + sauvegarder le modèle |

---

## 📦 Données utilisées

| Fichier | Source | Contenu |
|---------|--------|---------|
| `availpro_export.xlsx` | AvailPro / Channel Manager | Réservations, dates, canal, montant, chambre, client |
| `données avis booking.csv` | Booking.com | 1 634 avis bruts (source unique, traitement dans le code) |
| `expediareviews_from_*.csv` | Expedia | 208 avis tab-séparés format `X out of 10` |

---

## 🔧 Modules principaux

### `src/data/data_loader.py`
- `load_availpro_data()` — 6 500 réservations, colonnes canoniques robustes
- `load_booking_reviews()` — 1 634 avis, jointure sur numéro de réservation
- `load_expedia_reviews()` — 208 avis, parsing `"X out of 10"` → /10
- `clean_reservations()` — variables dérivées : `stay_length`, `lead_time_days`, `channel_group`, `room_segment`, `amount_bucket`, `client_id` (SHA-256)
- `merge_reviews_with_reservations()` — jointure via `reference_partenaire` ↔ `numero_reservation`
- `build_final_dataset()` — pipeline complet → `data/processed/hotel_dataset_final.csv`

### `src/network/network_analyzer.py`
- `build_similarity_graph()` — graphe pondéré (similarité de profil sur 7 attributs)
- `compute_network_metrics()` — weighted_degree, betweenness, pagerank, eigenvector, closeness
- `detect_communities()` — greedy (défaut) / label_propagation / Louvain
- `export_network_results()` — dataset enrichi avec toutes les métriques

### `src/models/predictor.py`
- `SatisfactionPredictor` — classification `high_satisfaction` (≥8/10) ou régression
- Features automatiquement sélectionnées, colonnes à fuite exclues
- Modèles : Random Forest, Gradient Boosting (+ XGBoost si installé)
- `train_all_models()` — comparaison automatique
- `CentralityPredictor` — alias de compatibilité

### `src/visualization/visualizer.py`
11 graphiques disponibles : réseau, centralités, satisfaction par canal/chambre/communauté, revenu, top profils, importance features, comparaison modèles, matrice de corrélation, stats réseau

---

## 📝 Hypothèses et choix techniques

| Hypothèse | Justification |
|-----------|---------------|
| Jointure via `Rfrence partenaire` ↔ `Numro de rservation` | Seule clé commune entre AvailPro et Booking |
| Email → `client_id` anonymisé SHA-256 tronqué 12 chars | Protection RGPD |
| Note globale ÷ 10 si > 10 | Certains exports Booking sont sur 100 |
| `high_satisfaction` = note ≥ 8.0/10 | Seuil standard hôtellerie |
| Seuil similarité réseau = 0.30 | 7 attributs, équilibre densité/pertinence |
| Diamètre/chemin moyen désactivés si > 500 nœuds | Performance O(n²) prohibitive |
| `partenaire_id`, `Garantie`, `montant_total` exclus du modèle | Fuite d'information ou doublon |

---

## 🧪 Commandes de test

```powershell
# Test des imports
python -c "from src.data.data_loader import build_final_dataset; print('data_loader OK')"
python -c "from src.network.network_analyzer import NetworkAnalyzer; print('network OK')"
python -c "from src.models.predictor import SatisfactionPredictor; print('predictor OK')"
python -c "from src.visualization.visualizer import NetworkVisualizer; print('visualizer OK')"

# Tests unitaires
python -m pytest -q tests

# Tests pipeline (données réelles)
python test_quick.py
python validate_pipeline.py
python run_pipeline_test.py
# → résultats dans pipeline_test_results.txt

# Test pipeline mode démo (sans données réelles)
python -c "
from src.data.data_loader import DataLoader
dl = DataLoader()
df = dl.generate_sample_data(200)
from src.network.network_analyzer import NetworkAnalyzer
na = NetworkAnalyzer()
na.build_similarity_graph(df, min_similarity=0.3, max_nodes=200)
comms = na.detect_communities()
print(f'Graphe: {na.graph.number_of_nodes()} noeuds, {na.graph.number_of_edges()} aretes')
print('Pipeline démo OK')
"

# Lancer l'application
python -m streamlit run app.py
```

---

## ⚙️ Dépendances principales

| Package | Usage |
|---------|-------|
| `pandas`, `numpy` | Traitement des données |
| `openpyxl`, `xlrd` | Lecture Excel |
| `scikit-learn`, `joblib` | Modèles ML |
| `networkx` | Analyse de réseau |
| `matplotlib`, `seaborn` | Visualisations |
| `streamlit` | Application web |
