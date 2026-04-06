# 🚀 QUICKSTART — Hôtel Aurore Paris · Analyse Réseau & Satisfaction Client

> **DU SDA — Université Paris-Sorbonne — 2025-2026**
> Pipeline validé le 06/04/2026 · Python 3.13 · Windows

---

## ✅ État du projet (validé)

| Étape | Résultat |
|-------|---------|
| Chargement AvailPro | 6 474 réservations |
| Parsing avis Booking | **1 634 avis** (format CSV encapsulé) |
| Jointure avis ↔ réservations | **316 avis liés** via `reference_partenaire` |
| Avis Expedia | 208 avis |
| Note moyenne Booking | **7.58 / 10** |
| Graphe de similarité | 500 nœuds · 88 375 arêtes |
| Métriques réseau | degree · betweenness · pagerank · eigenvector · closeness |
| Modèle satisfaction (RF) | **Accuracy 85.8% · F1 90.2% · ROC-AUC 91.8%** |
| Validation croisée 5-fold | **91.5% ± 1.3%** |

---

## 📁 Fichiers sources

```
data-projet-sorbonne/
├── availpro_export.xlsx                              ← Réservations (6 500 lignes)
├── données avis booking.csv                          ← 1 634 avis Booking (source unique)
└── expediareviews_from_2025-03-01_to_2026-03-01.csv ← 208 avis Expedia
```

> ⚠️ `données avis traités.xlsx` = doublon du CSV → **non utilisé**.

---

## 🛠️ Installation & Lancement

```powershell
# 1. Aller dans le projet
cd "C:\Users\KFA24632\sda-2026\client-centrality-prediction-platform"

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Diagnostic rapide (< 5 sec)
$env:PYTHONUTF8="1"; python quick_diagnostic.py

# 4. Test pipeline complet (60-90 sec) — résultats dans test_quick_result.txt
$env:PYTHONUTF8="1"; python test_quick.py

# 5. Validation complète (plus longue)
$env:PYTHONUTF8="1"; python validate_pipeline.py

# 6. Tests unitaires
python -m pytest -q tests

# 7. Lancer l'application (Windows — streamlit peut ne pas être dans le PATH)
$env:PYTHONUTF8="1"; python -m streamlit run app.py
# → http://localhost:8501
```

---

## 🏗️ Architecture

```
src/data/data_loader.py        ← Chargement + nettoyage + fusion (3 sources)
src/network/network_analyzer.py ← Graphe similarité + métriques + communautés
src/models/predictor.py        ← SatisfactionPredictor (RF / GBT / XGBoost)
src/visualization/visualizer.py ← 11 types de graphiques
app.py                         ← Streamlit 7 pages
data/processed/                ← Dataset final (généré automatiquement)
```

---

## 📊 Variables dérivées clés

| Variable | Description |
|----------|-------------|
| `client_id` | SHA-256 de l'email (anonymisation RGPD) |
| `lead_time_days` | Délai entre achat et arrivée |
| `stay_length` | Durée du séjour (nuits) |
| `channel_group` | booking / direct / expedia_group / metasearch / gds / other_ota |
| `room_segment` | standard / superieure / suite / twin / double |
| `amount_bucket` | Tranche de prix (<80€ → >600€) |
| `has_review` / `review_score` | Avis lié + note /10 |
| `high_satisfaction` | Note ≥ 8/10 (cible modèle) |
| `pagerank`, `betweenness`… | Métriques réseau |

---

## 🎯 Modèle — Performances sur vraies données

```
Accuracy     : 85.79%
F1-weighted  : 90.19%
ROC-AUC      : 91.77%
CV 5-fold    : 91.46% ± 1.29%
Train size   : 5 179   |   Test size : 1 295
Features     : 25 (numériques + catégorielles encodées + réseau)
```

---

## 🐛 Corrections appliquées

| Problème | Correction |
|---------|-----------|
| CSV Booking : 10 lignes au lieu de 1634 | Parser réécrit : détection par regex des dates |
| Guillemets résiduels `""` dans les valeurs | Nettoyage `replace('""', '')` après parsing |
| Jointure 0 match (`6.49e+09` vs `3044529099`) | Normalisation `str(int(float(x)))` des deux côtés |
| `train()` sans argument `y` | Mode DataFrame complet ajouté : `train(df)` |
| Double split dans `app.py` | Entraînement Streamlit aligné sur un seul découpage interne |
| Doublons `centrality_*` dans les features | Alias exclus du dataset enrichi et du modèle |
| `UnicodeEncodeError` Windows | `$env:PYTHONUTF8="1"` + `io.TextIOWrapper` |

---

*Mis à jour : 06/04/2026*
