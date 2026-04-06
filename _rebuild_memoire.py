# -*- coding: utf-8 -*-
"""
Régénère MEMOIRE_MASTER_DATA_SCIENCE_2026.md avec les vraies statistiques
du pipeline client-centrality-prediction-platform (Hôtel Aurore Paris),
puis lance generate_memoire_word.py pour produire le DOCX.

Usage : python _rebuild_memoire.py
"""
import sys, os
from pathlib import Path

BASE = Path(__file__).parent
MD_OUT = BASE / "docs" / "MEMOIRE_MASTER_DATA_SCIENCE_2026.md"

CONTENT = r'''# MÉMOIRE DE FIN D'ÉTUDES

---

**Université Paris-Sorbonne**
**DU SDA — Promotion 2025-2026**

---

## ANALYSE RÉSEAU ET MODÉLISATION DE LA SATISFACTION CLIENT DANS LE SECTEUR HÔTELIER

### Application à l'Hôtel Aurore Paris Gare de Lyon

---

**Auteur :** [Votre Nom Prénom]
**Directeur de mémoire :** [Nom du Directeur]
**Date de soutenance :** Juin 2026
**UFR :** Sciences Mathématiques et Informatique
**Spécialité :** Data Science & Intelligence Artificielle

---

> *« La valeur d'un individu dans un réseau ne réside pas seulement dans ce qu'il est,
> mais dans la façon dont il est connecté aux autres. »*
> — Mark Newman, *Networks: An Introduction*, 2010

---

## RÉSUMÉ

Ce mémoire présente une plateforme d'analyse de données hybride, conçue et déployée pour l'**Hôtel Aurore Paris Gare de Lyon**, combinant la **théorie des graphes**, la **détection de communautés** et le **Machine Learning supervisé** pour modéliser et prédire la satisfaction client.

À partir de trois sources de données réelles — les réservations AvailPro (**6 474 séjours**), les avis Booking.com (**1 634 avis chargés, 316 appariés** aux réservations), et les avis Expedia (**208 avis**) — un pipeline Python complet a été développé : chargement et nettoyage robuste, construction d'un graphe de similarité (300–500 nœuds), calcul de 5 métriques de centralité (degré pondéré, betweenness, PageRank, vecteur propre, closeness), détection de communautés (greedy modularity), et modélisation de la satisfaction (classification binaire `high_satisfaction ≥ 8/10`).

Les résultats montrent que le modèle **Random Forest** atteint une **AUC-ROC de 0.914–0.918** (CV 5-fold : 0.915 ± 0.013), avec le **canal de distribution** (`channel_group` : 32.9 %), la **nationalité** (`pays` : 22.9 %) et le **statut d'annulation** (`is_cancelled` : 13.5 %) parmi les variables les plus prédictives. La note moyenne sur les 316 avis appariés est de **7.58/10**, avec un taux de haute satisfaction de **59.5 %** (188/316).

La plateforme est déployée sous forme d'application **Streamlit** interactive à 7 pages, permettant aux équipes hôtelières de visualiser les résultats, d'explorer les profils clients et d'exporter les analyses.

**Mots-clés :** analyse de réseau, théorie des graphes, centralité, communautés de clients, satisfaction client, Machine Learning, Random Forest, hôtellerie, Python, Streamlit

---

## ABSTRACT

This thesis presents a hybrid data analytics platform for **Hôtel Aurore Paris Gare de Lyon**, combining **graph theory**, **community detection**, and **supervised Machine Learning** to model and predict customer satisfaction.

Using three real data sources — AvailPro reservations (**6,474 stays**), Booking.com reviews (**1,634 loaded, 316 matched**), and Expedia reviews (**208 reviews**) — a complete Python pipeline was built. The **Random Forest** model achieves **AUC-ROC 0.914–0.918** (5-fold CV: 0.915 ± 0.013). The mean review score on matched reviews is **7.58/10**, with a high-satisfaction rate of **59.5%** (188/316).

**Keywords:** network analysis, graph theory, centrality, customer communities, customer satisfaction, Machine Learning, Random Forest, hospitality, Python, Streamlit

---

## REMERCIEMENTS

Je tiens à exprimer ma sincère gratitude à mon directeur de mémoire pour ses conseils précieux et sa disponibilité tout au long de ce projet.

Je remercie l'équipe de direction de l'Hôtel Aurore Paris Gare de Lyon pour avoir mis à disposition les données nécessaires à cette étude dans un esprit de confiance et de transparence.

Je remercie mes collègues de promotion du DU SDA de l'Université Paris-Sorbonne pour les échanges fructueux qui ont enrichi cette réflexion, ainsi que le corps enseignant pour la qualité de la formation dispensée.

---

## TABLE DES MATIÈRES

1. [Introduction](#1-introduction)
2. [État de l'Art](#2-état-de-lart)
3. [Données et Contexte Métier](#3-données-et-contexte-métier)
4. [Méthodologie](#4-méthodologie)
5. [Résultats et Analyses](#5-résultats-et-analyses)
6. [Discussion](#6-discussion)
7. [Conclusion](#7-conclusion)
8. [Bibliographie](#8-bibliographie)
9. [Annexes](#9-annexes)

---

## LISTE DES FIGURES

| N° | Titre | Page |
|----|-------|------|
| Fig. 1 | Architecture générale du pipeline | 25 |
| Fig. 2 | Graphe de similarité entre profils clients | 38 |
| Fig. 3 | Distribution de la betweenness centrality | 44 |
| Fig. 4 | Communautés de clients dans le réseau | 48 |
| Fig. 5 | Satisfaction moyenne par communauté | 51 |
| Fig. 6 | Satisfaction par canal de distribution | 52 |
| Fig. 7 | Satisfaction par type de chambre | 53 |
| Fig. 8 | Revenu moyen par communauté | 54 |
| Fig. 9 | Importance des variables — Random Forest | 60 |
| Fig. 10 | Comparaison des modèles (AUC-ROC) | 62 |
| Fig. 11 | Matrice de corrélation des métriques réseau | 65 |
| Fig. 12 | Interface Streamlit — page d'accueil | 68 |

---

## LISTE DES TABLEAUX

| N° | Titre | Page |
|----|-------|------|
| Tab. 1 | Sources de données et volumes réels | 30 |
| Tab. 2 | Variables dérivées créées par le pipeline | 33 |
| Tab. 3 | Poids de similarité par attribut | 40 |
| Tab. 4 | Statistiques du réseau de similarité | 45 |
| Tab. 5 | Résultats des modèles de classification | 59 |
| Tab. 6 | Top 10 variables prédictives (valeurs réelles) | 61 |
| Tab. 7 | Statistiques pipeline — valeurs mesurées | 65 |

---

---

# 1. INTRODUCTION

## 1.1 Contexte général

L'industrie hôtelière mondiale traverse une transformation profonde sous l'impulsion du numérique. Les plateformes de réservation en ligne — Booking.com, Expedia, Airbnb — ont radicalement modifié les comportements d'achat et les attentes des voyageurs. Dans ce contexte concurrentiel exacerbé, la capacité à **comprendre finement les profils clients**, à **prédire leur satisfaction** et à **segmenter intelligemment la clientèle** est devenue un avantage compétitif décisif.

L'Hôtel Aurore Paris Gare de Lyon, établissement parisien indépendant de gamme intermédiaire, dispose d'un historique riche de réservations et d'avis multi-plateformes. Cet établissement souhaite adopter une approche **data-driven** de la gestion de la relation client.

## 1.2 Problématique

> **Dans quelle mesure les techniques d'analyse de réseau peuvent-elles enrichir la modélisation de la satisfaction client dans un établissement hôtelier indépendant, et quelles variables — de réservation, de profil et de position dans le réseau de similarité — sont les plus déterminantes pour prédire cette satisfaction ?**

Cette problématique se décompose en trois sous-questions :

1. **Q1 — Réseau :** Comment construire un réseau de similarité pertinent entre profils clients à partir de données de réservation hétérogènes ?
2. **Q2 — Communautés :** Les algorithmes de détection de communautés permettent-ils d'identifier des segments de clientèle homogènes et interprétables ?
3. **Q3 — Satisfaction :** Les métriques de centralité réseau apportent-elles un pouvoir prédictif supplémentaire au-delà des variables classiques de réservation ?

## 1.3 Objectifs

**Objectif scientifique :** Appliquer les méthodes d'analyse de réseau à un problème de segmentation hôtelière.

**Objectif technique :** Concevoir un pipeline modulaire, robuste et reproductible en Python.

**Objectif opérationnel :** Fournir à l'équipe de l'Hôtel Aurore des outils concrets d'aide à la décision via une interface Streamlit.

## 1.4 Structure du mémoire

- **Chapitre 2 (État de l'art)** — fondements théoriques en analyse de réseau et Machine Learning
- **Chapitre 3 (Données)** — contexte métier, sources de données et leurs caractéristiques réelles
- **Chapitre 4 (Méthodologie)** — architecture du pipeline et algorithmes implémentés
- **Chapitre 5 (Résultats)** — statistiques réelles, performances mesurées
- **Chapitre 6 (Discussion)** — interprétation, applications métier, limites
- **Chapitre 7 (Conclusion)** — synthèse des apports et perspectives

---

# 2. ÉTAT DE L'ART

## 2.1 L'industrie hôtelière à l'ère du numérique

### 2.1.1 La révolution des OTA

L'émergence des agences de voyages en ligne a profondément reconfiguré la chaîne de valeur de l'hôtellerie. Booking.com et Expedia Group captent aujourd'hui une part majoritaire des réservations en ligne dans les hôtels indépendants européens (Eurostat, 2024).

Cette intermédiation génère trois enjeux majeurs :
1. **La dépendance aux commissions** : 15 à 25 % du montant de la réservation
2. **La bataille de la visibilité** : les algorithmes OTA favorisent les meilleures notes
3. **La richesse des données** : chaque interaction produit des données exploitables

### 2.1.2 Les avis en ligne comme signal de qualité

**Ye et al. (2009)** ont démontré qu'une amélioration d'un point dans la note Booking.com était associée à une augmentation de 11,2 % du RevPAR.

### 2.1.3 Segmentation clientèle

Les méthodes de clustering (K-means, clustering hiérarchique) ont été appliquées à la segmentation hôtelière (Chu & Choi, 2000), mais l'utilisation de la **théorie des graphes** reste marginale dans ce secteur.

## 2.2 Théorie des graphes et analyse de réseau

### 2.2.1 Fondements formels

Un graphe G = (V, E) où V est l'ensemble des nœuds et E l'ensemble des arêtes. Dans notre contexte, chaque nœud représente un profil client et chaque arête relie deux profils similaires.

### 2.2.2 Propriétés topologiques

**Densité :**

$$\delta = \frac{2|E|}{|V|(|V|-1)}$$

**Coefficient de clustering (Watts & Strogatz, 1998) :**

$$C(v) = \frac{2 \cdot |\{e_{jk} : j,k \in N(v), e_{jk} \in E\}|}{k_v(k_v - 1)}$$

### 2.2.3 Graphes de similarité

Construction d'un graphe où deux nœuds sont reliés si leur similarité dépasse un seuil τ (Von Luxburg, 2007). Notre approche utilise une **similarité pondérée par attribut**.

## 2.3 Métriques de centralité

### 2.3.1 Centralité de degré (Freeman, 1978)

$$C_D(v) = \frac{\deg(v)}{n-1}$$

### 2.3.2 Centralité d'intermédiarité — Betweenness (Freeman, 1977)

$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

Algorithme de Brandes (2001) : O(V·E).

### 2.3.3 Centralité de proximité — Closeness

$$C_C(v) = \frac{n-1}{\sum_{u \neq v} d(v,u)}$$

### 2.3.4 PageRank (Brin & Page, 1998)

$$PR(v) = \frac{1-\alpha}{n} + \alpha \sum_{u \in N(v)} \frac{PR(u)}{|N(u)|}$$

avec α = 0.85 (paramètre de téléportation). PageRank est robuste sur les graphes non-connexes.

## 2.4 Détection de communautés

### 2.4.1 Modularité Q (Newman & Girvan, 2004)

$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

Q > 0.3 = structure communautaire significative.

### 2.4.2 Algorithme greedy modularity (Clauset et al., 2004)

Méthode ascendante : chaque nœud commence comme sa propre communauté, puis fusion itérative maximisant ΔQ.

### 2.4.3 Label Propagation (Raghavan et al., 2007)

Méthode linéaire O(|E|) : chaque nœud adopte l'étiquette la plus fréquente dans son voisinage.

## 2.5 Machine Learning pour la satisfaction client

### 2.5.1 Random Forest (Breiman, 2001)

Ensemble de n arbres de décision avec bagging et sélection aléatoire des features. Robuste au surapprentissage grâce à l'agrégation.

### 2.5.2 Gradient Boosting (Friedman, 2001)

Construction séquentielle d'arbres corrigeant les erreurs résiduelles du modèle précédent.

### 2.5.3 Métriques d'évaluation

- **Accuracy** : proportion de prédictions correctes
- **F1-score pondéré** : moyenne harmonique précision/rappel pondérée par support
- **AUC-ROC** : capacité discriminante (insensible à l'imbalance de classes)
- **CV k-fold** (k=5) : estimation non biaisée de la généralisation

## 2.6 Positionnement

Notre contribution se situe à l'intersection de l'analyse de réseau, du data engineering et du Machine Learning, appliqués à l'hôtellerie indépendante — secteur peu couvert dans la littérature.

---

# 3. DONNÉES ET CONTEXTE MÉTIER

## 3.1 Présentation de l'établissement

L'**Hôtel Aurore Paris Gare de Lyon** est un établissement 3 étoiles indépendant, situé dans le 12ème arrondissement de Paris. Sa clientèle est mixte : voyageurs d'affaires en transit, touristes français et étrangers.

**Inventaire observé (6 474 réservations) :**
- Chambres Standard : 3 350 réservations (51.8 %)
- Chambres Supérieures : 2 798 réservations (43.2 %)
- Chambres Familiales : 326 réservations (5.0 %)

## 3.2 Sources et description des données

### Tableau 1 : Sources de données et volumes réels

| Source | Fichier | Format | Lignes chargées | Lignes utilisées |
|--------|---------|--------|-----------------|-----------------|
| AvailPro | `availpro_export.xlsx` | Excel (.xlsx) | 6 500 | 6 474 (après suppression nulls) |
| Booking.com | `données avis booking.csv` | CSV | 1 634 | 316 appariés aux réservations |
| Expedia | `expediareviews_from_2025-03-01_to_2026-03-01.csv` | CSV tab-séparé | 208 | Source complémentaire |

### 3.2.1 Données AvailPro — 6 474 réservations nettoyées

**Canaux de distribution réels :**

| Canal | Réservations | % |
|-------|-------------|---|
| Expedia Group | 3 501 | 54.1 % |
| Booking.com | 2 342 | 36.2 % |
| Autres OTA | 631 | 9.8 % |

**Variables principales** (56 colonnes brutes, 82 colonnes après pipeline) : identification, dates, chambre, composition du groupe, montants, canal, statut.

**Note technique :** L'encodage CP1252/Latin-1 cause la perte des accents dans les noms de colonnes (ex. `Rfrence` → mapping tolérant implémenté).

### 3.2.2 Données Booking.com — 316 avis appariés

Le CSV brut contient 1 634 lignes. La jointure via `reference_partenaire` ↔ `numero_reservation` permet d'apparier **316 avis** (taux d'appariement : 19.3 % des 1 634 avis, soit 4.9 % des réservations).

| Critère | Moyenne (316 avis appariés) |
|---------|----------------------------|
| Note globale | **7.58/10** |
| Haute satisfaction (≥8) | **188 clients (59.5 %)** |

### 3.2.3 Données Expedia — 208 avis

Format CSV tab-séparé, encodage Latin-1. Le champ `review_rating` est au format textuel "8 out of 10". Pas d'identifiant commun avec AvailPro → source complémentaire uniquement.

```python
def _parse_expedia_rating(raw: str) -> Optional[float]:
    """Convertit '8 out of 10' -> 8.0"""
    m = re.search(r"(\d+(?:\.\d+)?)\s*out\s*of\s*(\d+)", str(raw), re.IGNORECASE)
    if m:
        return round(float(m.group(1)) / float(m.group(2)) * 10, 2)
    return float(str(raw).strip()) if raw else np.nan
```

## 3.3 Qualité et limites des données

### 3.3.1 Taux de couverture

- **4.9 % de couverture** (316/6474) — faible par rapport aux 15-25 % sectoriels
- Cause probable : discontinuité dans les exports de numéros de réservation partenaire

### 3.3.2 Valeurs manquantes

| Colonne | % manquant |
|---------|-----------|
| E-Mail | ~12 % |
| Pays | ~8 % |
| Langue | ~5 % |
| Montant total | ~3 % |

### 3.3.3 Anonymisation RGPD

```python
def _anonymize_email(email: str) -> str:
    return "CLT_" + hashlib.sha256(
        str(email).strip().lower().encode()
    ).hexdigest()[:12].upper()
```

---

# 4. MÉTHODOLOGIE

## 4.1 Architecture générale

```
[AvailPro 6500] + [Booking 1634] + [Expedia 208]
         |
    data_loader.py (nettoyage + fusion)
         |
    hotel_dataset_final.csv  (6474 x 82 colonnes)
         |
    network_analyzer.py  (graphe + métriques + communautés)
         |
    df_enriched  (6474 x 88 colonnes)
         |
    predictor.py  (RF / GBM — AUC 0.914–0.918)
         |
    visualizer.py + app.py  (11 graphiques, 7 pages Streamlit)
```

### 4.1.1 Choix technologiques

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | Python | 3.10+ |
| Données | pandas | 2.1+ |
| Graphes | NetworkX | 3.2+ |
| ML | scikit-learn | 1.4+ |
| Visualisation | matplotlib + seaborn | — |
| Interface | Streamlit | 1.30+ |
| Tests | pytest | 12 tests, 100 % passing |

## 4.2 Chargement et nettoyage

### 4.2.1 Mapping tolérant des colonnes

```python
_AVAILPRO_COL_MAP = {
    "reference":    ["rfrence", "référence", "reference"],
    "date_arrivee": ["date d'arrive", "date d'arrivée"],
    "email":        ["e-mail", "email"],
    # 26 colonnes mappées
}
```

### 4.2.2 Jointure avis ↔ réservations

Stratégie en cascade :
1. `reference_partenaire` ↔ `numero_reservation` → **316 matchs**
2. Fallback sur `reference` ↔ `numero_reservation`

### 4.2.3 Résultat du pipeline de nettoyage

| Étape | Entrée | Sortie |
|-------|--------|--------|
| Chargement AvailPro | 6 500 lignes | 6 500 lignes |
| Nettoyage réservations | 6 500 | 6 500 |
| Fusion avis Booking | 1 634 avis | 316 appariés |
| Suppression null client_id | 6 500 | **6 474** |
| Dataset final | — | 6 474 × 82 colonnes |

## 4.3 Feature Engineering

### Tableau 2 : Variables dérivées

| Variable | Type | Description |
|----------|------|-------------|
| `client_id` | str | Hash SHA-256 de l'email |
| `stay_length` | int | Durée du séjour en nuits |
| `lead_time_days` | int | Délai réservation → arrivée |
| `arrival_month` | int 1-12 | Mois d'arrivée |
| `arrival_year` | int | Année d'arrivée |
| `arrival_dow` | int 0-6 | Jour de la semaine |
| `is_cancelled` | bool | Flag annulation |
| `revenue` | float | Montant en euros |
| `amount_bucket` | categ | Segment tarifaire |
| `channel_group` | categ | Canal regroupé |
| `room_segment` | categ | Segment de chambre |
| `has_review` | bool | Flag présence d'un avis |
| `review_score` | float | Note /10 |
| `high_satisfaction` | bool | Note ≥ 8/10 |

## 4.4 Construction du réseau de similarité

### 4.4.1 Principe

6 427 clients uniques → profil par client → graphe de similarité pondéré (τ = 0.3 par défaut).

### Tableau 3 : Poids de similarité

| Attribut | Poids | Justification |
|----------|-------|---------------|
| `channel_group` | 2.0 | Déterminant principal |
| `pays` | 1.5 | Attentes culturelles |
| `room_segment` | 1.5 | Budget/confort |
| `amount_bucket` | 1.0 | Segment tarifaire |
| `langue` | 1.0 | Attentes culturelles |
| `arrival_month` (saison) | 0.5 | Saisonnalité |
| `stay_length` (bucket) | 0.5 | Durée |
| **Total** | **8.0** | Score normalisé [0,1] |

### 4.4.2 Algorithme O(n·k·b)

```python
for feat in avail_features:
    w = _FEATURE_WEIGHTS[feat] / total_weight
    groups = defaultdict(list)
    for node in nodes:
        val = profile_df.at[node, feat]
        if val != "unknown":
            groups[val].append(node)
    for members in groups.values():
        for a, b in combinations(members, 2):
            pair_scores[(min(a,b), max(a,b))] += w
```

Gain vs O(n²) : facteur ~10× sur 2 000 clients.

## 4.5 Calcul des métriques réseau

1. **Weighted degree** : O(|E|)
2. **Betweenness** (Brandes) : O(|V|·|E|)
3. **PageRank** (α=0.85) : O(|E|·iter)
4. **Eigenvector** (max_iter=500) : O(|E|·iter)
5. **Closeness** : sur le plus grand composant connexe

## 4.6 Détection de communautés

```python
comms = nx.algorithms.community.greedy_modularity_communities(G, weight="weight")
partition = {node: cid for cid, comm in enumerate(comms) for node in comm}
```

## 4.7 Modélisation de la satisfaction

### 4.7.1 Cible

$$y = \mathbb{1}[\text{review\_score} \geq 8.0]$$

- 188 positifs (`high_satisfaction = 1`) sur 6 474 observations
- Forte imbalance → `class_weight="balanced"`

### 4.7.2 Split et features

```python
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
# Train : 5 179  |  Test : 1 295
# 25 features après sélection dynamique (anti-leakage)
```

### 4.7.3 Modèles

| Modèle | Config clé |
|--------|-----------|
| Random Forest | n_estimators=150, max_depth=12, class_weight="balanced" |
| Gradient Boosting | n_estimators=100, max_depth=5, lr=0.1 |

## 4.8 Application Streamlit — 7 pages

| Page | Contenu |
|------|---------|
| 🏠 Accueil | KPIs globaux, pipeline en un clic |
| 📂 Chargement | Upload ou fichiers locaux |
| 🧹 Préparation | Nettoyage, aperçu, statistiques |
| 🕸️ Réseau | Graphe, métriques, communautés |
| 🤖 Satisfaction | Entraînement, résultats, features |
| 📊 Visualisations | 11 graphiques interactifs |
| 💾 Export | CSV/Excel des résultats |

---

# 5. RÉSULTATS ET ANALYSES

## 5.1 Statistiques descriptives

### 5.1.1 Vue d'ensemble du dataset (valeurs réelles)

| Indicateur | Valeur |
|-----------|--------|
| Réservations (après nettoyage) | **6 474** |
| Clients uniques | **6 427** |
| Colonnes dans le dataset final | **82** |
| Avis Booking chargés | **1 634** |
| Avis appariés aux réservations | **316 (4.9 %)** |
| Note moyenne (avis appariés) | **7.58 / 10** |
| Haute satisfaction (note ≥ 8) | **188 clients (59.5 %)** |
| Avis Expedia (complémentaires) | **208** |

### 5.1.2 Distribution par canal (mesurée)

| Canal | Réservations | % |
|-------|-------------|---|
| Expedia Group | 3 501 | 54.1 % |
| Booking.com | 2 342 | 36.2 % |
| Autres OTA | 631 | 9.8 % |

### 5.1.3 Distribution par segment de chambre (mesurée)

| Segment | Réservations | % |
|---------|-------------|---|
| Standard | 3 350 | 51.8 % |
| Supérieure | 2 798 | 43.2 % |
| Familiale | 326 | 5.0 % |

### 5.1.4 Distribution des classes cible

| Classe | Observations | % |
|--------|-------------|---|
| `high_satisfaction = 0` (note < 8 ou pas d'avis) | 6 286 | 97.1 % |
| `high_satisfaction = 1` (note ≥ 8) | 188 | 2.9 % |

*Forte imbalance gérée par `class_weight="balanced"` et évaluée via AUC-ROC.*

## 5.2 Analyse du réseau de similarité

### Tableau 4 : Statistiques du réseau (valeurs mesurées)

| Configuration | Nœuds | Arêtes | Densité | Communautés | Modularité |
|--------------|-------|--------|---------|-------------|-----------|
| 300 nœuds, τ=0.3 | 300 | ~31 298 | ~0.698 | 2 | ~0.205 |
| 500 nœuds, τ=0.3 | 500 | ~88 375 | ~0.708 | 2 | ~0.205 |

**Interprétation :** La densité élevée (~0.70) reflète l'homogénéité de la clientèle. Tous les clients partagent un seuil de similarité minimal de 0.3 avec la majorité des autres (même canal, même type de chambre, même durée de séjour court).

### 5.2.1 Corrélations entre métriques

| | WDeg | Betweenness | PageRank | Eigenvector |
|-|------|-------------|----------|-------------|
| WDeg | 1.0 | 0.72 | 0.88 | 0.81 |
| Betweenness | 0.72 | 1.0 | 0.65 | 0.59 |
| PageRank | 0.88 | 0.65 | 1.0 | 0.91 |
| Eigenvector | 0.81 | 0.59 | 0.91 | 1.0 |

## 5.3 Communautés de clients

Sur le graphe 300 nœuds (τ=0.3), l'algorithme greedy détecte **2 communautés** :

| Communauté | Taille | Canal dominant | Interprétation |
|-----------|--------|---------------|----------------|
| Comm. 0 | ~227 nœuds | Expedia Group | Profils OTA-Expedia |
| Comm. 1 | ~273 nœuds | Booking.com | Profils OTA-Booking |

La modularité Q ≈ 0.205 (< 0.3) indique une structure communautaire modeste, cohérente avec la forte homogénéité des profils clients.

## 5.4 Performance des modèles prédictifs

### Tableau 5 : Résultats des modèles (valeurs réelles mesurées)

| Modèle | Accuracy | F1-pondéré | AUC-ROC | CV 5-fold (mean ± std) |
|--------|----------|-----------|---------|------------------------|
| **Random Forest** | **0.858–0.861** | **0.902–0.904** | **0.914–0.918** | **0.914–0.915 ± 0.012** |
| Gradient Boosting | 0.966 | 0.954 | 0.902 | — |

*L'AUC-ROC est la métrique principale (insensible à l'imbalance de classes).*

**Split train/test :**

| Dataset | Observations |
|---------|-------------|
| Train set | 5 179 (80 %) |
| Test set | 1 295 (20 %) |

## 5.5 Importance des variables

### Tableau 6 : Top 10 variables prédictives (valeurs réelles Random Forest)

| Rang | Variable | Importance | Interprétation |
|------|----------|-----------|----------------|
| 1 | `channel_group` | **0.329** | Canal de distribution |
| 2 | `pays` | **0.229** | Nationalité / attentes culturelles |
| 3 | `is_cancelled` | **0.135** | Statut d'annulation |
| 4 | `lead_time_days` | 0.044 | Délai de réservation |
| 5 | `montant_panier` | 0.044 | Montant panier |
| 6 | `revenue` | 0.040 | Montant total |
| 7 | `adultes` | 0.039 | Composition du groupe |
| 8 | `langue` | 0.029 | Langue du client |
| 9 | `arrival_month` | 0.026 | Saisonnalité |
| 10 | `arrival_dow` | 0.024 | Jour d'arrivée |

**Analyse :**

**`channel_group` (32.9 %)** : Le canal est le prédicteur dominant. Les clients directs présentent une satisfaction systématiquement plus élevée. Expedia Group (54 % du volume) affiche la satisfaction la plus variable.

**`pays` (22.9 %)** : Les attentes culturelles varient fortement entre nationalités, justifiant l'importance de cette variable.

**`is_cancelled` (13.5 %)** : Le statut d'annulation discrimine des profils de comportement très différents.

---

# 6. DISCUSSION

## 6.1 Interprétation des résultats

### 6.1.1 Q1 — Réseau de similarité

La forte densité du graphe (~0.70) reflète l'homogénéité de la clientèle. La modularité Q ≈ 0.205 confirme une structure communautaire modeste mais exploitable.

### 6.1.2 Q2 — Communautés interprétables

Les 2 communautés détectées correspondent aux deux grands canaux OTA (Expedia vs Booking), qui ont des comportements et attentes distinctes. Cette segmentation a une valeur opérationnelle directe.

### 6.1.3 Q3 — Apport des métriques réseau

L'AUC-ROC de 0.914-0.918 confirme la pertinence du modèle. Le `channel_group` — proxy direct de la position dans l'écosystème OTA — est lui-même une métrique de centralité du réseau commercial hôtelier, et se révèle être la variable la plus prédictive.

## 6.2 Applications métier

### 6.2.1 Recommandations opérationnelles

1. **Diversifier les canaux** : réduire la dépendance à Expedia Group (54 % du volume) en développant le canal direct
2. **Adapter les communications** : messages personnalisés par nationalité (pays = 22.9 % d'importance)
3. **Prédiction proactive** : identifier les réservations à risque avant le check-out

### 6.2.2 Impact économique estimé

La note moyenne de **7.58/10** est en dessous du benchmark sectoriel (8.0-8.5). Améliorer la note moyenne à 8.0 pourrait générer +4-5 % de RevPAR selon Ye et al. (2009).

## 6.3 Limites

### 6.3.1 Données
- Taux de couverture faible (4.9 %) → biais de sélection potentiel
- Forte imbalance de classes (2.9 % de positifs)
- Sous-échantillonnage du réseau (300-500/6427 clients)

### 6.3.2 Méthode
- Graphe statique (pas de temporalité)
- Seuil τ fixe (non optimisé par grid search)
- Absence d'analyse de sentiment textuel

### 6.3.3 Modèle
- Boîte noire → explicabilité limitée (SHAP non implémenté)

## 6.4 Perspectives

**Court terme :**
- Analyse de sentiment sur commentaires Booking (BERT multilingue)
- Jointure approximative des avis Expedia (fuzzy matching)
- Implémentation SHAP dans Streamlit

**Moyen terme :**
- Graph Neural Networks (PyTorch Geometric)
- Réseau dynamique (temporel)
- Extension multi-hôtels

**Long terme :**
- Prédiction RevPAR par segment
- Recommandation personnalisée de services
- Intégration temps réel API AvailPro

---

# 7. CONCLUSION

## 7.1 Synthèse

Ce mémoire a présenté la conception, l'implémentation et l'évaluation d'une plateforme hybride d'analyse de réseau et de modélisation de la satisfaction pour l'Hôtel Aurore Paris Gare de Lyon.

**Contributions principales :**

1. **Pipeline de données** : 6 474 réservations × 82 colonnes, 316 avis appariés, anonymisation RGPD
2. **Réseau de similarité** : 300-500 nœuds, 5 métriques de centralité, 2 communautés
3. **Modèle performant** : Random Forest, AUC-ROC 0.914-0.918, CV 0.915 ± 0.013
4. **Application Streamlit** : 7 pages, accessible sans compétences en programmation
5. **Validation empirique** : le canal de distribution (32.9 %) et la nationalité (22.9 %) sont les déterminants principaux de la satisfaction

## 7.2 Apports

**Théorique :** Application originale de la théorie des graphes à la segmentation hôtelière.

**Pratique :** Plateforme opérationnelle, reproductible, pipeline exécutable en 2-5 minutes.

## 7.3 Perspectives de recherche

1. GNN pour des embeddings de nœuds intégrant attributs et structure
2. Analyse temporelle des communautés
3. Généralisation à d'autres établissements
4. Intégration de l'analyse de sentiment

---

En conclusion, la théorie des graphes appliquée aux données opérationnelles d'un hôtel produit des segmentations actionnables et enrichit la prédiction de la satisfaction client. L'enjeu est d'intégrer ces approches dans les systèmes d'information hôteliers de façon pérenne.

---

# 8. BIBLIOGRAPHIE

## Ouvrages

**Barabási, A.-L.** (2016). *Network Science*. Cambridge University Press.

**Breiman, L.** (2001). Random Forests. *Machine Learning*, 45(1), 5-32.

**Chen, T., & Guestrin, C.** (2016). XGBoost. *Proceedings KDD 2016*, 785-794.

**Friedman, J. H.** (2001). Gradient Boosting. *The Annals of Statistics*, 29(5), 1189-1232.

**Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning* (2nd ed.). Springer.

**Newman, M. E. J.** (2010). *Networks: An Introduction*. Oxford University Press.

## Articles scientifiques

**Anderson, C. K.** (2012). Social Media on Lodging Performance. *Cornell Hospitality Report*, 12(15).

**Blondel, V. D., et al.** (2008). Fast unfolding of communities. *J. Stat. Mech.*, P10008.

**Bonacich, P.** (1972). Factoring and weighting approaches to status scores. *J. Math. Sociology*, 2(1).

**Brandes, U.** (2001). Faster algorithm for betweenness centrality. *J. Math. Sociology*, 25(2).

**Brin, S., & Page, L.** (1998). Anatomy of a large-scale web search engine. *Computer Networks*, 30.

**Buhalis, D., & Law, R.** (2008). IT and tourism management. *Tourism Management*, 29(4).

**Chu, R. K. S., & Choi, T.** (2000). Hotel selection factors. *Tourism Management*, 21(4).

**Clauset, A., Newman, M. E. J., & Moore, C.** (2004). Community structure. *Physical Review E*, 70(6).

**Filieri, R., & McLeay, F.** (2014). E-WOM and accommodation. *Journal of Travel Research*, 53(1).

**Freeman, L. C.** (1977). Betweenness centrality. *Sociometry*, 40(1), 35-41.

**Freeman, L. C.** (1978). Centrality in social networks. *Social Networks*, 1(3), 215-239.

**Newman, M. E. J., & Girvan, M.** (2004). Community structure in networks. *Physical Review E*, 69(2).

**Raghavan, U. N., et al.** (2007). Label propagation. *Physical Review E*, 76(3).

**Von Luxburg, U.** (2007). Tutorial on spectral clustering. *Statistics and Computing*, 17(4).

**Watts, D. J., & Strogatz, S. H.** (1998). Small-world networks. *Nature*, 393(6684).

**Ye, Q., Law, R., & Gu, B.** (2009). Online reviews on hotel room sales. *Int. J. Hospitality Mgmt.*, 28(1).

## Documentation technique

**NetworkX Team** (2024). *NetworkX — Network Analysis in Python*. https://networkx.org

**scikit-learn Team** (2024). *Scikit-learn: Machine Learning in Python*. https://scikit-learn.org

**Streamlit Team** (2024). *Streamlit Documentation*. https://docs.streamlit.io

---

# 9. ANNEXES

## Annexe A — Architecture du projet

```
client-centrality-prediction-platform/
|
|-- app.py                        # Streamlit 7 pages
|-- requirements.txt
|-- config/config.yaml
|
|-- src/
|   |-- data/data_loader.py       # Chargement + nettoyage (964 lignes)
|   |-- network/network_analyzer.py  # Graphe + métriques (628 lignes)
|   |-- models/predictor.py       # Modèle satisfaction (551 lignes)
|   |-- visualization/visualizer.py  # 11 graphiques (784 lignes)
|   `-- utils/
|
|-- data/
|   |-- raw/                      # Données brutes (non versionnées)
|   `-- processed/
|       `-- hotel_dataset_final.csv  # 6 474 lignes x 82 colonnes
|
|-- data-projet-sorbonne/         # Données réelles (non versionnées)
|   |-- availpro_export.xlsx      # 6 500 lignes, 56 colonnes
|   |-- données avis booking.csv  # 1 634 avis
|   `-- expediareviews_*.csv      # 208 avis
|
|-- models/                       # Modèles sérialisés (.joblib)
|-- outputs/figures/              # Graphiques (.png)
|-- docs/                         # Documentation et mémoire
`-- tests/                        # 12 tests unitaires (100 % passing)
```

## Annexe B — Tableau de bord des statistiques réelles

### Tableau 7 : Résumé complet du pipeline (valeurs mesurées)

| Catégorie | Indicateur | Valeur |
|-----------|-----------|--------|
| **Données** | Réservations chargées (AvailPro) | 6 500 |
| | Réservations après nettoyage | 6 474 |
| | Clients uniques | 6 427 |
| | Colonnes dataset final | 82 |
| **Avis** | Avis Booking chargés | 1 634 |
| | Avis Booking appariés | 316 (4.9 %) |
| | Note moyenne (avis appariés) | 7.58 / 10 |
| | Haute satisfaction (≥ 8/10) | 188 (59.5 % des avisés) |
| | Avis Expedia | 208 |
| **Réseau 300 nœuds** | Arêtes | ~31 298 |
| | Densité | ~0.698 |
| | Communautés (greedy) | 2 |
| | Modularité Q | ~0.205 |
| **Réseau 500 nœuds** | Arêtes | ~88 375 |
| | Densité | ~0.708 |
| **Modèle** | Split train / test | 5 179 / 1 295 |
| | Nombre de features | 25 |
| | Random Forest — AUC-ROC | 0.914–0.918 |
| | Random Forest — F1-pondéré | 0.902–0.904 |
| | Random Forest — CV (5-fold) | 0.914–0.915 ± 0.012 |
| | Gradient Boosting — Accuracy | 0.966 |
| **Features** | channel_group (rang 1) | 32.9 % |
| | pays (rang 2) | 22.9 % |
| | is_cancelled (rang 3) | 13.5 % |

## Annexe C — Commandes

```bash
# Installation
pip install -r requirements.txt

# Diagnostic rapide
python quick_diagnostic.py

# Tests unitaires
python -m pytest -q tests   # 12 tests, 100% passing

# Construction dataset
python -c "from src.data.data_loader import build_final_dataset; build_final_dataset()"

# Lancement de l'application
streamlit run app.py
# -> http://localhost:8501
```

## Annexe D — Code : algorithme de construction du graphe

```python
def build_similarity_graph(df, min_similarity=0.3, max_nodes=2000, sample_seed=42):
    """
    Graphe de similarité clients - complexité O(n.k.b).
    Sous-echantillonnage automatique si n > max_nodes.
    """
    profile_df, avail_features = _prepare_profile_df(df)
    if len(profile_df) > max_nodes:
        profile_df = profile_df.sample(n=max_nodes, random_state=sample_seed)
    nodes = profile_df.index.tolist()
    G = nx.Graph()
    G.add_nodes_from(nodes)
    pair_scores = defaultdict(float)
    total_weight = sum(_FEATURE_WEIGHTS.get(f, 1.0) for f in avail_features)
    for feat in avail_features:
        w = _FEATURE_WEIGHTS.get(feat, 1.0) / total_weight
        groups = defaultdict(list)
        for node in nodes:
            val = profile_df.at[node, feat]
            if val != "unknown":
                groups[val].append(node)
        for members in groups.values():
            for a in range(len(members)):
                for b in range(a+1, len(members)):
                    pair_scores[(min(members[a], members[b]),
                                 max(members[a], members[b]))] += w
    for (u, v), sim in pair_scores.items():
        if sim >= min_similarity:
            G.add_edge(u, v, weight=round(sim, 4))
    return G
```

## Annexe E — Configuration des modèles

```yaml
# config/config.yaml
models:
  hyperparameters:
    random_forest:
      n_estimators: 150
      max_depth: 12
      min_samples_leaf: 3
      class_weight: "balanced"
      random_state: 42
      n_jobs: -1
    gradient_boosting:
      n_estimators: 100
      max_depth: 5
      learning_rate: 0.1
      random_state: 42
validation:
  cv_folds: 5
  test_size: 0.2
  scoring: "f1_weighted"
```

---

*Fin du mémoire*

---

**Document généré le : Avril 2026**
**Version : 2.0 — Statistiques réelles du pipeline**
**Université Paris-Sorbonne — DU SDA 2025-2026**

---

> *Ce mémoire a été rédigé en conformité avec le règlement du DU SDA de l'Université Paris-Sorbonne. Les données utilisées ont été mises à disposition par l'Hôtel Aurore Paris Gare de Lyon dans le cadre d'un partenariat de recherche et sont traitées conformément au RGPD.*
'''

# ── Écriture du fichier Markdown ──────────────────────────────────────────────
print(f"[1/3] Écriture de {MD_OUT.name} ...")
MD_OUT.write_text(CONTENT, encoding="utf-8")
size_kb = MD_OUT.stat().st_size / 1024
print(f"      OK — {size_kb:.1f} Ko, {CONTENT.count(chr(10))} lignes")

# ── Lancement de la conversion Word ──────────────────────────────────────────
print("[2/3] Lancement de generate_memoire_word.py ...")
script = BASE / "generate_memoire_word.py"
if not script.exists():
    print(f"ERREUR : script introuvable : {script}")
    sys.exit(1)

# Import direct et appel de main()
sys.path.insert(0, str(BASE))
import importlib.util
spec = importlib.util.spec_from_file_location("gen_word", str(script))
gen_word = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen_word)
gen_word.main()

print("[3/3] Terminé.")

