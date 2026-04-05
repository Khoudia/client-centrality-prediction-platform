# 🚀 QUICKSTART — Hôtel Aurore Paris

## Prérequis

- Python 3.10+
- Les 4 fichiers de données dans `data-projet-sorbonne/`

## Installation en 1 commande

```bash
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run app.py
```

→ http://localhost:8501

## Pipeline automatique

Dans la barre latérale → **"🚀 Tout exécuter (pipeline)"**

Résultat attendu :
- 6 474 réservations chargées
- 1 098 avis Booking matchés
- Note moyenne : 8.37/10
- Modèle RF : Accuracy 91.7%, ROC-AUC 96.8%

## Test rapide en ligne de commande

```bash
# Générer le dataset final (données réelles)
python -c "
import logging; logging.basicConfig(level=logging.INFO)
from src.data.data_loader import build_final_dataset
df = build_final_dataset(save=True)
print(f'OK — {len(df)} réservations, {df[\"has_review\"].sum()} avis matchés')
"

# Test pipeline complet avec log
python run_pipeline_test.py
# Résultats dans : pipeline_test_results.txt
```

## Pages de l'application

| Page | Description |
|------|-------------|
| 🏠 Accueil | Tableau de bord global |
| 📂 Chargement | Charger les 4 sources de données |
| 🧹 Préparation | Nettoyer et fusionner les données |
| 🕸️ Analyse Réseau | Graphe de similarité + métriques + communautés |
| 🤖 Satisfaction | Modèle de prédiction RF/GB |
| 📊 Visualisations | 11 graphiques interactifs |
| 💾 Export | CSV/Excel + sauvegarde modèle |
