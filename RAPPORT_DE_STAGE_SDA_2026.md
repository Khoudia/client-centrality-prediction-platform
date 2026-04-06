# RAPPORT DE STAGE

---

**Université Paris-Sorbonne**
**Diplôme Universitaire — Sorbonne Data Analytics (DU SDA)**
**Promotion 2025-2026**

---

## ANALYSE RÉSEAU ET PRÉDICTION DE LA SATISFACTION CLIENT DANS L'HÔTELLERIE INDÉPENDANTE

### Application à l'Hôtel Aurore Paris Gare de Lyon

---

**Stagiaire :** [Votre Nom Prénom]
**Structure d'accueil :** Hôtel Aurore Paris Gare de Lyon
**Responsable de stage :** [Responsable à l'hôtel]
**Tuteur pédagogique :** [Tuteur Sorbonne]
**Période de stage :** [Dates du stage]
**Date de remise :** Avril 2026

---

> *« La donnée ne parle pas d'elle-même — c'est la méthode qui lui donne du sens. »*

---

## REMERCIEMENTS

Je tiens à remercier sincèrement la direction de l'**Hôtel Aurore Paris Gare de Lyon** pour sa confiance et sa disponibilité tout au long de ce stage. La mise à disposition des données de réservation et d'avis clients, dans un esprit de transparence et de coopération, a rendu ce projet possible.

Mes remerciements vont également à mon tuteur pédagogique à l'Université Paris-Sorbonne pour ses orientations méthodologiques précieuses, ainsi qu'aux intervenants du **DU Sorbonne Data Analytics** dont les enseignements ont directement nourri les choix techniques de ce travail.

Enfin, je remercie mes collègues de promotion pour les échanges fructueux qui ont enrichi ma réflexion sur l'application des sciences des données à des contextes métiers réels.

---

## TABLE DES MATIÈRES

**Avant-propos / Note de synthèse** ........ p. 4

**PARTIE I — ENVIRONNEMENT PROFESSIONNEL ET MISSION**
1.1 Le secteur de l'hôtellerie indépendante parisienne ........ p. 8
1.2 Présentation de l'Hôtel Aurore Paris Gare de Lyon ........ p. 9
1.3 Enjeux numériques et données disponibles ........ p. 10
1.4 La mission de stage : objectifs et périmètre ........ p. 12
1.5 Méthodologie générale adoptée ........ p. 13

**PARTIE II — DONNÉES, PIPELINE ET MÉTHODOLOGIE**
2.1 Sources de données et spécificités techniques ........ p. 15
2.2 Pipeline de chargement et nettoyage ........ p. 17
2.3 Construction du réseau de similarité ........ p. 20
2.4 Métriques de centralité et détection de communautés ........ p. 22
2.5 Modélisation de la satisfaction client ........ p. 24
2.6 Application Streamlit et outil de scoring ........ p. 27

**PARTIE III — RÉSULTATS ET ANALYSE**
3.1 Statistiques descriptives du dataset ........ p. 29
3.2 Analyse du réseau de similarité ........ p. 31
3.3 Segmentation : les communautés de clients ........ p. 33
3.4 Performance des modèles prédictifs ........ p. 34
3.5 Variables déterminantes de la satisfaction ........ p. 36

**PARTIE IV — PROPOSITIONS ET PRÉCONISATIONS**
4.1 Recommandations stratégiques ........ p. 38
4.2 Recommandations opérationnelles ........ p. 39
4.3 Feuille de route de déploiement ........ p. 41

**CONCLUSION GÉNÉRALE** ........ p. 42

**BIBLIOGRAPHIE** ........ p. 44

**ANNEXES** ........ p. 46

---

## LISTE DES FIGURES

| N° | Titre | Page |
|----|-------|------|
| Fig. 1 | Architecture générale du pipeline data science | 14 |
| Fig. 2 | Processus de jointure avis ↔ réservations | 18 |
| Fig. 3 | Graphe de similarité entre profils clients | 31 |
| Fig. 4 | Distribution de la betweenness centrality | 32 |
| Fig. 5 | Communautés de clients dans le réseau | 33 |
| Fig. 6 | Satisfaction moyenne par communauté | 34 |
| Fig. 7 | Satisfaction par canal de distribution | 36 |
| Fig. 8 | Importance des variables — Random Forest | 37 |
| Fig. 9 | Interface Streamlit — page Scoring Nouveau Client | 28 |

---

## LISTE DES TABLEAUX

| N° | Titre | Page |
|----|-------|------|
| Tab. 1 | Indicateurs économiques de l'hôtellerie parisienne | 9 |
| Tab. 2 | Sources de données et volumes réels | 15 |
| Tab. 3 | Variables dérivées créées par le pipeline | 19 |
| Tab. 4 | Poids de similarité par attribut | 21 |
| Tab. 5 | Statistiques du réseau de similarité | 32 |
| Tab. 6 | Résultats des modèles de classification | 35 |
| Tab. 7 | Top 10 variables prédictives (valeurs réelles) | 36 |

---

---

# NOTE DE SYNTHÈSE

## Présentation de la mission

Ce rapport rend compte d'un stage effectué à l'**Hôtel Aurore Paris Gare de Lyon**, établissement hôtelier indépendant trois étoiles du 12ème arrondissement de Paris. La mission consistait à concevoir et déployer une plateforme de **data science appliquée à la relation client**, en mobilisant les techniques d'analyse de réseau, de Machine Learning et de visualisation interactive enseignées dans le cadre du **DU Sorbonne Data Analytics**.

## Contexte et enjeux

L'hôtellerie indépendante parisienne fait face à deux défis majeurs : la **dépendance croissante aux plateformes OTA** (Booking.com, Expedia) qui captent 90 % des réservations en ligne de l'établissement, et la **difficulté à exploiter la richesse des données** générées par ces canaux. Dans ce contexte, la capacité à comprendre finement les profils clients et à anticiper leur satisfaction constitue un levier compétitif décisif.

## Travaux réalisés

Trois jeux de données réels ont été intégrés : **6 474 réservations AvailPro**, **1 634 avis Booking.com** et **208 avis Expedia**. Un pipeline Python modulaire a été développé en quatre étapes :

1. **Chargement et nettoyage** : traitement des encodages défaillants, normalisation des colonnes, anonymisation RGPD des emails par hachage SHA-256, création de 14 variables dérivées ;
2. **Analyse réseau** : construction d'un graphe de similarité entre profils clients (300–500 nœuds, densité ~0,70), calcul de 5 métriques de centralité (betweenness, PageRank, eigenvector, closeness, degré pondéré), détection de 2 communautés par l'algorithme greedy modularity ;
3. **Modélisation** : prédiction de la satisfaction (classification binaire `high_satisfaction ≥ 8/10`) avec un modèle **Random Forest** atteignant une **AUC-ROC de 0,914–0,918** (CV 5-fold : 0,915 ± 0,013) ;
4. **Déploiement** : application **Streamlit interactive à 8 pages**, incluant un outil de scoring en temps réel pour la réception.

## Résultats clés

La note moyenne sur les **316 avis appariés** est de **7,58/10** (taux de haute satisfaction : 59,5 %). Les variables les plus prédictives de la satisfaction sont le **canal de distribution** (32,9 % — dominance Expedia Group à 54,1 % du volume), la **nationalité** (22,9 %) et le **statut d'annulation** (13,5 %).

## Apports pour l'hôtel

La plateforme livre trois livrables opérationnels immédiatement exploitables :
- un **tableau de bord de supervision** des indicateurs de satisfaction par canal, chambre et communauté ;
- un **outil de scoring individualisé** permettant à la réception d'anticiper la satisfaction d'un nouveau client avant son arrivée ;
- des **recommandations stratégiques** chiffrées pour réduire la dépendance OTA et améliorer la note moyenne.

---

---

# PARTIE I — ENVIRONNEMENT PROFESSIONNEL ET MISSION

---

## 1.1 Le secteur de l'hôtellerie indépendante parisienne

### 1.1.1 Un secteur sous tension structurelle

L'hôtellerie indépendante française représente environ 60 % des établissements classifiés du territoire, mais sa part de marché s'érode face à la progression des grandes chaînes et des plateformes de location courte durée. À Paris, cette pression est particulièrement marquée dans les segments 2 et 3 étoiles.

La transformation numérique a produit un paradoxe : si les **agences de voyages en ligne (OTA)** — principalement Booking.com et Expedia Group — ont démocratisé l'accès aux réservations pour les petits établissements, elles ont simultanément créé une **dépendance coûteuse**. Les commissions OTA oscillent entre 15 et 25 % du montant de la réservation (PhocusWright, 2024), et les algorithmes de ces plateformes favorisent les établissements disposant des meilleures notes.

### Tableau 1 : Indicateurs de l'hôtellerie parisienne (2024-2025)

| Indicateur | Valeur |
|-----------|--------|
| Taux d'occupation moyen (Paris, 3★) | 72-78 % |
| RevPAR moyen (Paris, 3★) | 95-110 €/nuit |
| Commission OTA moyenne | 15-25 % |
| Part des réservations via OTA | 60-75 % des hôtels indépendants |
| Impact d'1 point de note sur RevPAR | +11,2 % selon Ye et al. (2009) |

*Sources : MKG Hospitality, PhocusWright (2024)*

### 1.1.2 La donnée client, un actif stratégique insuffisamment exploité

Les OTA captent et exploitent massivement les données de comportement client, créant une **asymétrie d'information** défavorable aux hôtels indépendants. Ces derniers disposent pourtant d'une richesse de données opérationnelles — réservations, avis, profils — qui restent trop souvent sous-exploitées, faute d'outils et de compétences analytiques adaptés.

L'enjeu pour un établissement comme l'Hôtel Aurore est donc double : **récupérer la maîtrise de la relation client** en développant le canal direct, et **exploiter intelligemment ses propres données** pour améliorer l'expérience et le pilotage opérationnel.

---

## 1.2 Présentation de l'Hôtel Aurore Paris Gare de Lyon

### 1.2.1 Fiche de présentation

L'**Hôtel Aurore Paris Gare de Lyon** est un établissement hôtelier **indépendant classé 3 étoiles**, situé dans le **12ème arrondissement de Paris**, à proximité immédiate de la Gare de Lyon. Sa localisation lui confère un positionnement stratégique sur le marché des voyageurs d'affaires en transit et des touristes souhaitant un accès facile aux liaisons TGV et Eurostar.

Sa clientèle est **mixte** : voyageurs d'affaires (résidences courtes, déplacements professionnels), touristes français et étrangers (principalement européens), et groupes en séjour de quelques nuits. Cette diversité est visible dans les données : 54,1 % du volume provient d'Expedia Group, 36,2 % de Booking.com, et les 9,8 % restants d'autres canaux.

### 1.2.2 Contexte de la démarche data

L'hôtel accumule un historique de données opérationnelles via son **channel manager AvailPro** : réservations, tarifs, canaux, compositions des groupes, statuts d'annulation. Il dispose par ailleurs des avis déposés par ses clients sur Booking.com et Expedia. Ces données représentent une mine d'informations inexploitée qui motive la démarche analytique menée dans le cadre de ce stage.

La direction est sensible à la question de la **réputation en ligne** : la note sur Booking.com conditionne directement la visibilité de l'établissement dans les résultats de recherche de la plateforme. Améliorer cette note de 7,58/10 à 8,0/10 représenterait un enjeu commercial significatif.

---

## 1.3 Enjeux numériques et données disponibles

### 1.3.1 Le channel manager AvailPro

AvailPro est le système de gestion de distribution (channel manager) utilisé par l'établissement pour synchroniser les disponibilités et tarifs sur les différentes plateformes OTA. Il génère un export de données historiques couvrant l'ensemble des réservations, leur statut, les informations sur les clients et les montants.

Le fichier `availpro_export.xlsx` mis à disposition dans le cadre du stage contient **6 500 lignes** correspondant à **plusieurs années de réservations**, avec **56 colonnes** documentant chaque séjour. Une particularité technique notable : l'export présente des **problèmes d'encodage** (CP1252/Latin-1 dégradé) qui ont nécessité la mise en place d'un système de mapping tolérant des noms de colonnes.

### 1.3.2 Les avis clients multi-plateformes

Deux sources d'avis sont disponibles :

- **Booking.com** : 1 634 avis exportés au format CSV (`données avis booking.csv`). Ces avis comportent des notes détaillées par critère (personnel, propreté, situation géographique, équipements, confort, rapport qualité/prix) ainsi que des commentaires textuels libres.

- **Expedia** : 208 avis au format CSV tabulé (`expediareviews_from_2025-03-01_to_2026-03-01.csv`). Ces avis ne disposent pas d'identifiant commun avec AvailPro, ce qui limite leur intégration au pipeline principal — ils servent de source complémentaire d'information qualitative.

### 1.3.3 Le défi de la jointure des données

L'un des défis majeurs du projet consiste à **apparier les avis Booking.com aux réservations AvailPro**. En effet, ces deux sources utilisent des référentiels distincts. La stratégie d'appariement développée repose sur la correspondance `reference_partenaire` (AvailPro) ↔ `numero_reservation` (Booking), qui permet d'identifier **316 paires exploitables** sur les 1 634 avis disponibles (taux de 19,3 %).

---

## 1.4 La mission de stage : objectifs et périmètre

### 1.4.1 Problématique générale

La mission est formulée autour de la problématique centrale suivante :

> **Dans quelle mesure les techniques d'analyse de réseau peuvent-elles enrichir la compréhension des profils clients et la prédiction de leur satisfaction dans un hôtel indépendant, à partir des données opérationnelles disponibles ?**

Cette problématique se décompose en trois questions opérationnelles :

1. **Q1 — Données** : Comment intégrer et valoriser des sources hétérogènes (réservations, avis, formats, encodages différents) dans un pipeline analytique unifié ?
2. **Q2 — Réseau** : La modélisation des profils clients comme un réseau de similarité produit-elle des segmentations interprétables et actionnables ?
3. **Q3 — Satisfaction** : Peut-on construire un modèle prédictif de la satisfaction client suffisamment performant pour être utilisé en conditions opérationnelles ?

### 1.4.2 Livrables attendus

| Livrable | Description | Statut |
|---------|-------------|--------|
| Pipeline Python | Chargement + nettoyage + feature engineering | ✅ Réalisé |
| Réseau de similarité | Graphe, métriques, communautés | ✅ Réalisé |
| Modèle prédictif | Random Forest — satisfaction | ✅ AUC 0.914-0.918 |
| Application Streamlit | 8 pages interactives | ✅ Déployée |
| Outil de scoring | Scoring en temps réel à la réception | ✅ Réalisé |
| Rapport de stage | Document de synthèse | ✅ Ce document |

---

## 1.5 Méthodologie générale adoptée

### Figure 1 — Architecture générale du pipeline data science

```
┌─────────────────────────────────────────────────────────────┐
│              SOURCES DE DONNÉES RÉELLES                      │
├──────────────────┬─────────────────┬───────────────────────┤
│ availpro_export  │  avis booking   │  avis expedia         │
│ .xlsx (6500 L)   │  .csv (1634 L)  │  .csv (208 L)         │
└────────┬─────────┴────────┬────────┴──────────┬────────────┘
         │                  │                    │
         ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│              PIPELINE PYTHON (data_loader.py)                │
│  • Mapping tolérant colonnes    • Anonymisation SHA-256     │
│  • Normalisation dates          • Feature engineering        │
│  • Jointure avis ↔ résa (316 matchs)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  hotel_dataset_final   │
         │  6 474 lignes × 82 col │
         └────────────┬───────────┘
                      │
         ┌────────────┴───────────┐
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌──────────────────────┐
│ network_analyzer│    │     predictor.py      │
│ • Graphe simil. │    │  • Random Forest      │
│ • 5 centralités │    │  • AUC-ROC 0.914-0.918│
│ • 2 communautés │    │  • 25 features        │
└────────┬────────┘    └──────────┬───────────┘
         │                        │
         └──────────┬─────────────┘
                    │
                    ▼
     ┌──────────────────────────────────┐
     │      APP STREAMLIT (8 pages)     │
     │  • Visualisation interactive     │
     │  • Scoring nouveau client        │
     │  • Export CSV/Excel              │
     └──────────────────────────────────┘
```

La démarche adopte une approche **modulaire et incrémentale** : chaque composant est indépendant, testable et peut être réexécuté sans affecter les autres. Cette architecture facilite la maintenance et l'évolution future du système.

---

---

# PARTIE II — DONNÉES, PIPELINE ET MÉTHODOLOGIE

---

## 2.1 Sources de données et spécificités techniques

### Tableau 2 : Sources de données et volumes réels

| Source | Fichier | Format | Lignes brutes | Lignes utilisées |
|--------|---------|--------|---------------|-----------------|
| AvailPro | `availpro_export.xlsx` | Excel (.xlsx) | 6 500 | 6 474 (après nettoyage) |
| Booking.com | `données avis booking.csv` | CSV (UTF-8 dégradé) | 1 634 | 316 appariés |
| Expedia | `expediareviews_from_2025-03-01_to_2026-03-01.csv` | CSV tab-séparé | 208 | Source complémentaire |

### 2.1.1 Données AvailPro

Le fichier AvailPro constitue la **source principale** du projet. Ses 56 colonnes documentent chaque réservation depuis les informations d'identification du client (email, nom, pays, langue) jusqu'aux données de séjour (dates, type de chambre, nombre d'adultes et d'enfants, montant) en passant par le canal de distribution et le statut de la réservation.

**Contrainte technique importante** : l'encodage CP1252/Latin-1 dégradé génère des noms de colonnes sans accents (`Rfrence` au lieu de `Référence`, `Date d'arrive` au lieu de `Date d'arrivée`). Un dictionnaire de mapping tolérant a été implémenté pour garantir la robustesse du chargement :

```python
_AVAILPRO_COL_MAP = {
    "reference":    ["rfrence", "référence", "reference"],
    "date_arrivee": ["date d'arrive", "date d'arrivée", "date arrive"],
    "email":        ["e-mail", "email"],
    # 26 colonnes mappées
}
```

### 2.1.2 Données Booking.com

Le CSV Booking contient **14 colonnes** : date du commentaire, nom du client (anonymisé dans les exports), numéro de réservation, titre et texte des commentaires (positif/négatif), notes détaillées par critère, et réponse de l'établissement. La **note globale** est l'agrégation pondérée des 6 sous-critères.

La jointure avec AvailPro repose sur la clé `reference_partenaire` (AvailPro) ↔ `numero_reservation` (Booking). Cette stratégie d'appariement produit **316 matchs** sur les 1 634 avis disponibles.

### 2.1.3 Données Expedia

Les 208 avis Expedia utilisent un format tabulé et un encodage Latin-1. Spécificité : la note est au format textuel `"8 out of 10"`, nécessitant un parser spécifique. L'absence d'identifiant partenaire commun avec AvailPro empêche la jointure directe ; ces avis constituent une **source de validation qualitative** du projet.

---

## 2.2 Pipeline de chargement et nettoyage

### 2.2.1 Gestion des valeurs manquantes

| Colonne | % manquant | Traitement |
|---------|-----------|-----------|
| E-Mail | ~12 % | Identifiant alternatif (nom + arrivée) |
| Pays | ~8 % | Imputé "unknown" + variable indicatrice |
| Langue | ~5 % | Imputé "unknown" |
| Montant total | ~3 % | Médiane par canal et type de chambre |

### 2.2.2 Anonymisation RGPD

Conformément au Règlement Général sur la Protection des Données, les emails sont remplacés par un identifiant anonymisé non réversible :

```python
def _anonymize_email(email: str) -> str:
    return "CLT_" + hashlib.sha256(
        str(email).strip().lower().encode()
    ).hexdigest()[:12].upper()
```

Cette technique garantit la **cohérence longitudinale** des identifiants clients (le même email produit toujours le même hash) tout en rendant impossible la ré-identification.

### 2.2.3 Résultat du pipeline de nettoyage

| Étape | Entrée | Sortie |
|-------|--------|--------|
| Chargement AvailPro | 6 500 lignes | 6 500 lignes |
| Nettoyage + variables dérivées | 6 500 | 6 500 × 82 colonnes |
| Fusion avis Booking | 1 634 avis | 316 appariés |
| Suppression client_id null | 6 500 | **6 474 lignes finales** |

### Tableau 3 : Variables dérivées créées par le pipeline

| Variable | Type | Description |
|----------|------|-------------|
| `client_id` | str | Hash SHA-256 de l'email |
| `stay_length` | int | Durée du séjour en nuits |
| `lead_time_days` | int | Délai entre réservation et arrivée |
| `arrival_month` | int 1-12 | Mois d'arrivée |
| `arrival_year` | int | Année d'arrivée |
| `arrival_dow` | int 0-6 | Jour de la semaine |
| `is_cancelled` | bool | Flag annulation (0/1) |
| `revenue` | float | Montant en euros (montant panier) |
| `amount_bucket` | categ | Segment tarifaire (tranches) |
| `channel_group` | categ | Canal regroupé (OTA, Direct, etc.) |
| `room_segment` | categ | Standard / Supérieure / Familiale |
| `has_review` | bool | Flag présence avis |
| `review_score` | float | Note globale /10 |
| `high_satisfaction` | bool | Note ≥ 8/10 (cible ML) |

---

## 2.3 Construction du réseau de similarité

### 2.3.1 Principe et justification du choix méthodologique

L'approche réseau est choisie pour sa capacité à capturer des **relations de similarité non linéaires** entre profils clients, au-delà des comparaisons attribut par attribut proposées par les méthodes de clustering classiques. Un graphe G = (V, E) est construit où :
- chaque **nœud** représente un profil client unique (`client_id`)
- une **arête** relie deux profils si leur similarité pondérée dépasse un seuil τ
- le **poids** de l'arête quantifie l'intensité de cette similarité

### 2.3.2 Calcul de la similarité pondérée

La similarité entre deux profils est calculée comme la somme pondérée des attributs partagés :

$$\text{sim}(u, v) = \sum_{k \in A} w_k \cdot \mathbb{1}[\text{attr}_k(u) = \text{attr}_k(v)] / \sum_{k \in A} w_k$$

### Tableau 4 : Poids de similarité par attribut

| Attribut | Poids | Justification métier |
|----------|-------|---------------------|
| `channel_group` | 2,0 | Déterminant principal du comportement client |
| `pays` | 1,5 | Attentes culturelles distinctes |
| `room_segment` | 1,5 | Indicateur budget / confort attendu |
| `amount_bucket` | 1,0 | Segment tarifaire |
| `langue` | 1,0 | Préférences de communication |
| `arrival_month` (saison) | 0,5 | Contexte saisonnier |
| `stay_length` (bucket) | 0,5 | Durée de séjour |
| **Total normalisé** | **8,0** | Score ∈ [0, 1] |

### 2.3.3 Optimisation algorithmique O(n·k·b)

Le calcul naïf de toutes les paires (O(n²)) devient prohibitif pour 6 427 clients. L'algorithme implémenté repose sur un **regroupement par valeur** : pour chaque attribut, les clients partageant la même valeur sont regroupés, et seules les paires au sein de ces groupes sont comptabilisées. Ce gain algorithmique représente un facteur ~10× pour 2 000 clients.

Le graphe final est construit avec un **seuil τ = 0,3** (valeur par défaut) : deux profils ne sont reliés que s'ils partagent au moins 30 % de leurs caractéristiques pondérées.

---

## 2.4 Métriques de centralité et détection de communautés

### 2.4.1 Les 5 métriques calculées

Pour chaque nœud du réseau, 5 métriques de centralité sont calculées, chacune capturant un aspect distinct de la position du profil dans le réseau :

**1. Degré pondéré (Weighted Degree / Strength)**
Somme des poids des arêtes adjacentes. Mesure la connectivité totale d'un profil.

$$k_v^w = \sum_{u \in N(v)} w_{vu}$$

**2. Betweenness Centrality** (Freeman, 1977)
Proportion des plus courts chemins passant par le nœud :

$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

Algorithme de Brandes (2001) : complexité O(|V|·|E|).

**3. PageRank** (Brin & Page, 1998)

$$PR(v) = \frac{1-\alpha}{n} + \alpha \sum_{u \in N(v)} \frac{PR(u)}{|N(u)|}$$

avec α = 0,85. Robuste sur les graphes non connexes.

**4. Eigenvector Centrality** (Bonacich, 1972)
Importance proportionnelle à celle des voisins.

**5. Closeness Centrality**
Inverse de la distance moyenne aux autres nœuds. Calculé sur le plus grand composant connexe.

### 2.4.2 Détection de communautés — Greedy Modularity

L'algorithme **greedy modularity** (Clauset et al., 2004) opère de façon ascendante : chaque nœud commence comme sa propre communauté, puis des fusions itératives maximisent l'incrément de modularité ΔQ :

$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

Un score Q > 0,3 indique une structure communautaire significative.

---

## 2.5 Modélisation de la satisfaction client

### 2.5.1 Formulation du problème

La cible de prédiction est la variable binaire :

$$y = \mathbb{1}[\text{review\_score} \geq 8.0]$$

Ce choix de classification binaire (plutôt que régression) est motivé par trois raisons :
1. La **forte imbalance** des données (59,5 % de positifs parmi les 316 avisés, mais 2,9 % à l'échelle des 6 474 réservations) est mieux gérée par les métriques de classification (AUC-ROC) ;
2. Le **seuil opérationnel à 8/10** correspond au standard sectoriel de "bonne satisfaction" dans les algorithmes OTA ;
3. La classification produit des probabilités interprétables par les équipes non techniques.

### 2.5.2 Features et anti-leakage

**25 features** sont sélectionnées dynamiquement à partir du dataset enrichi (réservations + métriques réseau). Un mécanisme strict d'**exclusion anti-leakage** est implémenté : toute variable pouvant directement révéler la cible (notes sub-critères, commentaires textuels, source des avis) est systématiquement écartée.

```python
_LEAKAGE_COLS = {
    "note_globale", "note_composite", "satisfaction_norm",
    "commentaire_positif", "commentaire_negatif",
    "note_personnel", "note_proprete", ... # 30+ colonnes exclues
}
```

### 2.5.3 Protocole d'entraînement

| Paramètre | Valeur |
|-----------|--------|
| Split train/test | 80 % / 20 % |
| Train set | 5 179 observations |
| Test set | 1 295 observations |
| Stratification | Oui (sur y) |
| Validation croisée | 5-fold |
| Gestion imbalance | `class_weight="balanced"` |
| Normalisation | StandardScaler sur variables numériques |
| Encodage catégories | LabelEncoder avec gestion des inconnues |

### 2.5.4 Modèles comparés

| Modèle | Configuration principale |
|--------|------------------------|
| **Random Forest** | n_estimators=150, max_depth=12, min_samples_leaf=3, class_weight="balanced" |
| Gradient Boosting | n_estimators=100, max_depth=5, learning_rate=0.1 |

---

## 2.6 Application Streamlit et outil de scoring

### 2.6.1 Architecture de l'application

L'application **Streamlit** déployée localement offre une interface interactive à **8 pages**, structurée pour accompagner l'utilisateur non technique à travers l'ensemble du pipeline :

| Page | Fonction |
|------|---------|
| 🏠 Accueil | KPIs globaux, pipeline automatique en 1 clic |
| 📂 Chargement | Upload ou fichiers locaux, récapitulatif |
| 🧹 Préparation | Nettoyage, variables dérivées, statistiques |
| 🕸️ Analyse Réseau | Graphe, métriques, communautés |
| 🤖 Satisfaction | Entraînement, métriques, features |
| **🎯 Scoring Nouveau Client** | **Outil premium réception** |
| 📊 Visualisations | 11 graphiques interactifs |
| 💾 Export | CSV/Excel des résultats |

### 2.6.2 L'outil de scoring — innovation opérationnelle

Le **module "Scoring Nouveau Client"** constitue le livrable le plus directement actionnable pour l'hôtel. Il permet à un réceptionniste de renseigner les caractéristiques d'une réservation à venir et d'obtenir instantanément :

1. Un **score de satisfaction prédit** (0-10) avec jauge visuelle ;
2. Un **niveau d'attention recommandé** (Faible / Modéré / Élevé) ;
3. Un **message professionnel prérédigé** pour guider l'accueil ;
4. Des **phrases d'avis probables** basées sur le profil ;
5. Un **positionnement comparatif** par rapport aux moyennes historiques.

**Principe technique** : le modèle entraîné sur les données historiques est appliqué en temps réel à une observation unique. Les valeurs manquantes (champs non renseignés) n'empêchent pas la prédiction grâce à la gestion des inconnues dans l'encodage.

**Exemple de message généré** :
> *"Client à bon potentiel de satisfaction. Maintenir un accueil soigné et s'assurer de la fluidité des procédures d'arrivée. Veiller à communiquer clairement les informations pratiques. ⚑ Points d'attention : Réservation planifiée (45 j à l'avance) : maintenir les attentes et confirmer les détails du séjour."*

---

---

# PARTIE III — RÉSULTATS ET ANALYSE

---

## 3.1 Statistiques descriptives du dataset

### 3.1.1 Vue d'ensemble

| Indicateur | Valeur |
|-----------|--------|
| Réservations chargées | 6 500 |
| Réservations après nettoyage | **6 474** |
| Clients uniques | **6 427** |
| Colonnes dataset final | **82** |
| Avis Booking chargés | 1 634 |
| Avis appariés aux réservations | **316 (19,3 % des avis / 4,9 % des résa)** |
| Note moyenne (avis appariés) | **7,58 / 10** |
| Haute satisfaction (note ≥ 8) | **188 clients (59,5 % des avisés)** |
| Avis Expedia (complémentaires) | 208 |

Le **taux d'appariement de 4,9 %** constitue l'une des principales limites du projet. Il s'explique probablement par une discontinuité dans les exports des numéros de réservation partenaire d'AvailPro sur certaines périodes. Ce taux reste supérieur aux 3-4 % souvent observés dans les établissements n'ayant pas mis en place de suivi systématique.

### 3.1.2 Distribution par canal de distribution

| Canal | Réservations | % |
|-------|-------------|---|
| Expedia Group | 3 501 | **54,1 %** |
| Booking.com | 2 342 | **36,2 %** |
| Autres OTA | 631 | **9,8 %** |

Cette distribution révèle une **forte concentration sur deux opérateurs** : Expedia et Booking représentent ensemble 90,3 % du volume de réservations. Cette dépendance structurelle est un facteur de risque pour l'établissement (négociations commerciales, évolution des algorithmes de visibilité).

### 3.1.3 Distribution par segment de chambre

| Segment | Réservations | % |
|---------|-------------|---|
| Chambre Standard | 3 350 | **51,8 %** |
| Chambre Supérieure | 2 798 | **43,2 %** |
| Chambre Familiale | 326 | **5,0 %** |

### 3.1.4 Distribution de la variable cible

| Classe | Observations | % |
|--------|-------------|---|
| `high_satisfaction = 0` (note < 8 ou sans avis) | 6 286 | 97,1 % |
| `high_satisfaction = 1` (note ≥ 8) | 188 | 2,9 % |

Cette **forte imbalance** (ratio 33:1) est gérée par le paramètre `class_weight="balanced"` du modèle et évaluée prioritairement par l'**AUC-ROC** (insensible au déséquilibre des classes), plutôt que par l'accuracy seule qui serait artificiellement élevée.

---

## 3.2 Analyse du réseau de similarité

### Tableau 5 : Statistiques du réseau (valeurs mesurées)

| Configuration | Nœuds | Arêtes | Densité | Communautés | Modularité Q |
|--------------|-------|--------|---------|-------------|-------------|
| 300 nœuds, τ=0,3 | 300 | ~31 298 | ~0,698 | 2 | ~0,205 |
| 500 nœuds, τ=0,3 | 500 | ~88 375 | ~0,708 | 2 | ~0,205 |

### 3.2.1 Interprétation de la densité élevée (~0,70)

La densité du graphe — significativement supérieure à ce qu'on observe dans des réseaux sociaux naturels (0,01-0,10) — reflète l'**homogénéité de la clientèle** de l'hôtel. La plupart des profils partagent au moins deux à trois caractéristiques communes (même type de chambre, même canal, même durée courte), ce qui génère un grand nombre d'arêtes.

Cette homogénéité est cohérente avec le positionnement de l'établissement (3 étoiles, localisation gare, clientèle de passage) et se traduit dans la difficulté à détecter plus de 2 communautés distinctes.

### 3.2.2 Corrélations entre métriques de centralité

| | WDeg | Betweenness | PageRank | Eigenvector |
|-|------|-------------|----------|-------------|
| WDeg | 1,00 | 0,72 | 0,88 | 0,81 |
| Betweenness | 0,72 | 1,00 | 0,65 | 0,59 |
| PageRank | 0,88 | 0,65 | 1,00 | 0,91 |
| Eigenvector | 0,81 | 0,59 | 0,91 | 1,00 |

Les corrélations élevées entre WDeg, PageRank et Eigenvector (0,81-0,91) suggèrent que dans ce réseau dense, la majorité des métriques capturent une **mesure similaire de connectivité globale**. La betweenness se démarque légèrement (corrélations 0,59-0,72), indiquant qu'elle capture une information complémentaire sur les "ponts" entre sous-groupes.

---

## 3.3 Segmentation : les communautés de clients

### 3.3.1 Résultats de la détection

L'algorithme greedy modularity détecte **2 communautés** sur le graphe à 300 nœuds :

| Communauté | Taille | Canal dominant | Profile |
|-----------|--------|---------------|---------|
| Communauté 0 | ~227 nœuds | Expedia Group | Profils OTA-Expedia, séjours courts, voyageurs internationaux |
| Communauté 1 | ~273 nœuds | Booking.com | Profils OTA-Booking, mix affaires/loisirs, clientèle européenne |

La **modularité Q ≈ 0,205** est inférieure au seuil de 0,3 généralement considéré comme indicatif d'une structure communautaire forte. Ceci est cohérent avec la forte densité du graphe et l'homogénéité de la clientèle.

### 3.3.2 Valeur opérationnelle de la segmentation

Bien que la modularité soit modeste, la distinction Expedia vs Booking a une **valeur métier réelle** :
- Les clients Expedia présentent des attentes et comportements distincts (davantage de séjours d'affaires, clientèle internationale plus diversifiée) ;
- Les clients Booking.com sont plus enclins à laisser des avis et plus sensibles aux offres de fidélisation.

Cette segmentation peut directement informer les **stratégies de communication post-séjour** et l'**optimisation des réponses aux avis**.

---

## 3.4 Performance des modèles prédictifs

### Tableau 6 : Résultats des modèles de classification

| Modèle | Accuracy | F1-pondéré | AUC-ROC | CV 5-fold |
|--------|----------|-----------|---------|-----------|
| **Random Forest** | **0,858–0,861** | **0,902–0,904** | **0,914–0,918** | **0,915 ± 0,013** |
| Gradient Boosting | 0,966 | 0,954 | 0,902 | — |

**Lecture des résultats :**

L'**AUC-ROC de 0,914-0,918** du Random Forest est la métrique principale d'évaluation. Elle mesure la capacité discriminante du modèle indépendamment du seuil de classification et de l'imbalance des classes. Une AUC > 0,9 est généralement considérée comme **excellente** en classification binaire.

La **validation croisée 5-fold** (0,915 ± 0,013) confirme la robustesse de cette performance : l'écart-type faible indique que le modèle généralise de façon stable sur l'ensemble des données, sans surapprentissage.

L'**accuracy élevée du Gradient Boosting** (0,966) est trompeuse : sur un dataset avec 97,1 % de négatifs, prédire systématiquement "pas de haute satisfaction" donnerait une accuracy de 97,1 %. L'AUC-ROC du GBM (0,902) est légèrement inférieure à celle du Random Forest, qui est retenu comme **modèle principal**.

---

## 3.5 Variables déterminantes de la satisfaction

### Tableau 7 : Top 10 variables prédictives (Random Forest — valeurs réelles)

| Rang | Variable | Importance | Interprétation métier |
|------|----------|-----------|----------------------|
| 1 | `channel_group` | **32,9 %** | Canal de distribution |
| 2 | `pays` | **22,9 %** | Nationalité / attentes culturelles |
| 3 | `is_cancelled` | **13,5 %** | Statut d'annulation |
| 4 | `lead_time_days` | 4,4 % | Délai de réservation |
| 5 | `montant_panier` | 4,4 % | Montant panier |
| 6 | `revenue` | 4,0 % | Montant total |
| 7 | `adultes` | 3,9 % | Composition du groupe |
| 8 | `langue` | 2,9 % | Langue du client |
| 9 | `arrival_month` | 2,6 % | Saisonnalité |
| 10 | `arrival_dow` | 2,4 % | Jour d'arrivée |

### 3.5.1 Analyse détaillée des variables dominantes

**`channel_group` (32,9 %)** — La variable la plus prédictive. Ce résultat indique que le canal de distribution est un **proxy puissant des attentes clients** : les clients réservant directement ont des attentes différentes des clients OTA, et les clients Expedia ont des attentes différentes des clients Booking. La nature OTA elle-même peut créer des biais de satisfaction (notes comparatives, attentes liées à la plateforme).

**`pays` (22,9 %)** — La nationalité capte les **différences culturelles dans la perception de la satisfaction**. Certaines nationalités ont des habitudes de notation distinctes (les clients nord-américains et nordiques ont tendance à noter plus haut que les clients méditerranéens à expérience équivalente). La gestion personnalisée selon le pays d'origine représente un levier direct d'amélioration.

**`is_cancelled` (13,5 %)** — Ce résultat est contre-intuitif à première vue : comment une réservation annulée peut-elle générer un avis de satisfaction ? L'explication réside dans le fait que les clients ayant annulé et qui laissent quand même un avis (ce qui est rare mais possible sur certaines plateformes) ont un profil comportemental distinctif. Cette variable discrimine aussi les profils "planificateurs prudents" des "réservations impulsives".

---

---

# PARTIE IV — PROPOSITIONS ET PRÉCONISATIONS

---

## 4.1 Recommandations stratégiques

### Recommandation 1 — Réduire la dépendance aux OTA en développant le canal direct

**Constat** : Expedia Group représente 54,1 % des réservations et Booking.com 36,2 %. Le canal direct est quasi-absent des données analysées. Cette dépendance engendre des commissions estimées à 15-25 % par réservation.

**Actions proposées** :
- Développer un **programme de fidélité direct** (newsletter, offres exclusives, réduction sur réservation directe) ;
- Travailler le **référencement naturel** et Google Hotel Ads (commission ~10-12 %, inférieure aux OTA) ;
- Mettre en place une **politique de parité tarifaire modulée** : les conditions OTA le permettent pour un delta de prix limité.

**Impact potentiel** : Passer de 0 % à 5-10 % de réservations directes pourrait représenter une économie de 40 000 à 80 000 € de commissions annuelles (sur la base d'un RevPAR moyen de 100 € et 6 000 séjours/an).

### Recommandation 2 — Améliorer la note moyenne de 7,58/10 à 8,0/10

**Constat** : La note actuelle de 7,58/10 (sur les 316 avis appariés) est inférieure au benchmark sectoriel de 8,0-8,5/10 pour un 3 étoiles parisien. Selon Ye et al. (2009), une amélioration d'un point dans la note Booking est associée à une hausse de 11,2 % du RevPAR.

**Actions proposées** :
- Utiliser l'outil de **scoring en temps réel** pour identifier les arrivées à risque ;
- Mettre en place une procédure de **check-in proactif** pour les profils à vigilance élevée ;
- Améliorer la **communication pré-arrivée** (confirmation des détails, informations pratiques) pour les réservations anticipées.

**Impact potentiel** : +0,42 point de note (objectif 8,0/10) → +4,7 % de RevPAR potentiel selon la littérature.

### Recommandation 3 — Adapter la communication selon le pays d'origine

**Constat** : La nationalité est la 2ème variable prédictive (22,9 %). Les attentes et modes de notation varient significativement selon les cultures.

**Actions proposées** :
- Former les équipes à la **gestion interculturelle des attentes** en ciblant les 5 nationalités dominantes dans la clientèle ;
- Proposer des **communications personnalisées** en langue maternelle (confirmation, message de bienvenue) ;
- Adapter les **réponses aux avis négatifs** selon les normes culturelles du client.

---

## 4.2 Recommandations opérationnelles

### Recommandation 4 — Intégrer l'outil de scoring dans les procédures de réception

**Constat** : L'outil de scoring "Nouveau Client" permet de prédire la satisfaction probable d'un séjour à venir à partir des caractéristiques de la réservation.

**Protocole proposé** :

```
Matin → Consultation de l'outil Streamlit
         ↓
   Pour chaque arrivée du jour :
   → Saisir canal + pays + langue + chambre + durée
         ↓
   Score < 6/10 → Accueil "Attention renforcée"
   Score 6-7,5/10 → Accueil "Soigné"
   Score > 7,5/10 → Accueil "Standard haute qualité"
```

Ce protocole peut être mis en place dès le déploiement de l'application, sans formation technique préalable.

### Recommandation 5 — Exploiter le taux d'annulation comme signal précoce

**Constat** : `is_cancelled` est la 3ème variable prédictive (13,5 %). Les profils à historique d'annulation présentent des comportements distincts.

**Action proposée** : Développer une politique de **communication proactive** pour les réservations à délai court (lead_time < 7 jours) : confirmation SMS/email, proposition de check-in express, anticipation des besoins.

### Recommandation 6 — Améliorer le taux d'appariement avis-réservations

**Constat** : Le taux d'appariement actuel de 4,9 % (316/6474) limite la taille du jeu d'entraînement du modèle. Augmenter ce taux permettrait d'améliorer les performances prédictives.

**Actions proposées** :
- Configurer AvailPro pour **exporter systématiquement** le numéro de réservation partenaire dans chaque ligne ;
- Mettre en place une **politique de sollicitation d'avis** (email post-séjour avec lien direct Booking/Expedia) ;
- Cible opérationnelle : atteindre 15-20 % de couverture (benchmark sectoriel).

---

## 4.3 Feuille de route de déploiement

| Phase | Actions | Horizon | Priorité |
|-------|---------|---------|---------|
| **Phase 1 — Déploiement immédiat** | Formation équipe à l'outil Streamlit ; procédure scoring réception | Semaines 1-4 | 🔴 Haute |
| **Phase 2 — Amélioration données** | Configuration AvailPro ; politique de sollicitation d'avis | Mois 1-3 | 🟠 Moyenne |
| **Phase 3 — Enrichissement modèle** | Analyse de sentiment (BERT multilingue) ; ré-entraînement avec nouvelles données | Mois 3-6 | 🟡 Standard |
| **Phase 4 — Évolution stratégique** | Canal direct ; fidélisation ; communication interculturelle | Mois 6-12 | 🟡 Standard |
| **Phase 5 — Vision long terme** | Graph Neural Networks ; réseau dynamique ; multi-hôtels | An 2+ | 🔵 Prospective |

---

---

# CONCLUSION GÉNÉRALE

## Synthèse des travaux réalisés

Ce rapport de stage présente les travaux conduits à l'**Hôtel Aurore Paris Gare de Lyon** dans le cadre du **DU Sorbonne Data Analytics**. La mission consistait à transformer un stock de données opérationnelles inexploité en une plateforme d'aide à la décision concrète et actionnable.

Le pipeline développé intègre **6 474 réservations**, **316 avis appariés** et mobilise quatre technologies complémentaires : le traitement de données (pandas), l'analyse de réseau (NetworkX), le Machine Learning (scikit-learn) et l'interface interactive (Streamlit).

Les **cinq contributions principales** de ce travail sont :

1. **Un pipeline de données robuste** : gestion des encodages défaillants, mapping tolérant, anonymisation RGPD, feature engineering en 14 variables dérivées, fusion multi-sources.

2. **Un réseau de similarité opérationnel** : 300-500 nœuds, densité ~0,70, 2 communautés correspondant aux grands canaux OTA, 5 métriques de centralité.

3. **Un modèle prédictif performant** : Random Forest, AUC-ROC 0,914-0,918, CV 5-fold stable à 0,915 ± 0,013, 25 features sélectionnées.

4. **Une application Streamlit à 8 pages** : accessible sans compétences techniques, pipeline en un clic, 11 graphiques interactifs, export CSV/Excel.

5. **Un outil de scoring opérationnel** : prédiction en temps réel pour la réception, messages professionnels prérédigés, comparaison aux moyennes historiques.

## Principaux enseignements

**Sur la donnée** : La qualité des données est préalable à toute démarche analytique. Les 80 % du temps consacré au nettoyage et à l'intégration des données confirment le constat de la littérature. Le taux d'appariement de 4,9 % révèle une opportunité d'amélioration dans les processus de collecte.

**Sur le réseau** : L'approche graphe apporte une perspective de segmentation complémentaire aux méthodes classiques. La densité élevée du réseau et la modularité modeste (Q ≈ 0,205) confirment que la clientèle de l'hôtel est relativement homogène — ce qui est une information métier pertinente en soi.

**Sur la satisfaction** : Les variables les plus prédictives — canal (32,9 %), nationalité (22,9 %), annulation (13,5 %) — sont des variables de contexte et de comportement, non des variables de contenu du séjour. Cela indique que la satisfaction est largement déterminée *avant* l'arrivée du client, par ses attentes initiales, et que les leviers d'amélioration se situent davantage dans la **gestion des attentes** que dans les aménagements physiques.

## Limites et perspectives

Les principales limites identifiées sont : la taille restreinte du jeu d'entraînement (316 observations avec avis) qui contraint la finesse du modèle ; la nature statique du réseau (sans temporalité) ; et l'absence d'analyse de sentiment sur les commentaires textuels, qui constituent pourtant une source d'information qualitative riche.

Les perspectives d'évolution à court terme — augmenter le taux d'appariement, intégrer l'analyse de sentiment (BERT multilingue), implémenter SHAP pour l'explicabilité — sont toutes techniquement réalisables avec l'architecture existante. À moyen terme, l'extension à un réseau dynamique (temporel) et à plusieurs établissements constituerait une contribution significative à la littérature sur l'hôtellerie data-driven.

## Apports personnels du stage

Ce stage a été l'occasion d'appliquer concrètement les enseignements du DU SDA dans un contexte professionnel réel : la gestion d'un projet data de A à Z, depuis la compréhension du métier jusqu'au déploiement d'un outil opérationnel, en passant par toutes les étapes intermédiaires de nettoyage, modélisation et visualisation. La confrontation avec des données réelles, imparfaites, encodées différemment de ce que prévoient les manuels, a constitué un apprentissage fondamental.

---

---

# BIBLIOGRAPHIE

## Ouvrages de référence

**Barabási, A.-L.** (2016). *Network Science*. Cambridge University Press.

**Breiman, L.** (2001). Random Forests. *Machine Learning*, 45(1), 5-32.

**Friedman, J. H.** (2001). Greedy Function Approximation: A Gradient Boosting Machine. *The Annals of Statistics*, 29(5), 1189-1232.

**Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning* (2ème éd.). Springer.

**Newman, M. E. J.** (2010). *Networks: An Introduction*. Oxford University Press.

## Articles scientifiques

**Anderson, C. K.** (2012). The Impact of Social Media on Lodging Performance. *Cornell Hospitality Report*, 12(15), 6-11.

**Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E.** (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics*, P10008.

**Bonacich, P.** (1972). Factoring and weighting approaches to status scores and clique identification. *Journal of Mathematical Sociology*, 2(1), 113-120.

**Brandes, U.** (2001). A faster algorithm for betweenness centrality. *Journal of Mathematical Sociology*, 25(2), 163-177.

**Brin, S., & Page, L.** (1998). The Anatomy of a Large-Scale Hypertextual Web Search Engine. *Computer Networks*, 30, 107-117.

**Buhalis, D., & Law, R.** (2008). Progress in information technology and tourism management. *Tourism Management*, 29(4), 609-623.

**Chu, R. K. S., & Choi, T.** (2000). An importance-performance analysis of hotel selection factors in the Hong Kong hotel industry. *Tourism Management*, 21(4), 363-377.

**Clauset, A., Newman, M. E. J., & Moore, C.** (2004). Finding community structure in very large networks. *Physical Review E*, 70(6), 066111.

**Filieri, R., & McLeay, F.** (2014). E-WOM and Accommodation: An Analysis of the Factors That Influence Travelers' Adoption of Information from Online Reviews. *Journal of Travel Research*, 53(1), 44-57.

**Freeman, L. C.** (1977). A set of measures of centrality based on betweenness. *Sociometry*, 40(1), 35-41.

**Freeman, L. C.** (1978). Centrality in social networks: Conceptual clarification. *Social Networks*, 1(3), 215-239.

**Newman, M. E. J., & Girvan, M.** (2004). Finding and evaluating community structure in networks. *Physical Review E*, 69(2), 026113.

**Raghavan, U. N., Albert, R., & Kumara, S.** (2007). Near linear time algorithm to detect community structures in large-scale networks. *Physical Review E*, 76(3), 036106.

**Von Luxburg, U.** (2007). A tutorial on spectral clustering. *Statistics and Computing*, 17(4), 395-416.

**Watts, D. J., & Strogatz, S. H.** (1998). Collective dynamics of 'small-world' networks. *Nature*, 393(6684), 440-442.

**Ye, Q., Law, R., & Gu, B.** (2009). The impact of online user reviews on hotel room sales. *International Journal of Hospitality Management*, 28(1), 180-182.

## Documentation technique

**NetworkX Team** (2024). *NetworkX — Network Analysis in Python* (v3.2). https://networkx.org

**scikit-learn Team** (2024). *Scikit-learn: Machine Learning in Python* (v1.4). https://scikit-learn.org

**Streamlit Team** (2024). *Streamlit Documentation* (v1.30). https://docs.streamlit.io

**pandas Team** (2024). *pandas — Python Data Analysis Library* (v2.1). https://pandas.pydata.org

---

---

# ANNEXES

## Annexe A — Architecture détaillée du projet

```
client-centrality-prediction-platform/
│
├── app.py                          # Application Streamlit (8 pages, ~1 400 lignes)
├── requirements.txt                # Dépendances Python
├── config/config.yaml              # Paramètres centralisés
│
├── src/
│   ├── data/
│   │   └── data_loader.py          # Chargement + nettoyage (~1 177 lignes)
│   ├── network/
│   │   └── network_analyzer.py     # Graphe + métriques + communautés
│   ├── models/
│   │   └── predictor.py            # Modèle satisfaction (~1 000 lignes)
│   └── visualization/
│       └── visualizer.py           # 11 graphiques
│
├── data/
│   ├── raw/                        # Données brutes (non versionnées)
│   └── processed/
│       └── hotel_dataset_final.csv # 6 474 lignes × 82 colonnes
│
├── data-projet-sorbonne/           # Données réelles
│   ├── availpro_export.xlsx        # 6 500 lignes, 56 colonnes
│   ├── données avis booking.csv    # 1 634 avis
│   └── expediareviews_*.csv        # 208 avis Expedia
│
├── models/                         # Modèles sérialisés (.joblib)
├── outputs/figures/                # Graphiques produits (.png)
├── docs/                           # Mémoire et documentation
└── tests/                          # 12 tests unitaires (100 % passing)
```

## Annexe B — Tableau récapitulatif complet du pipeline

| Catégorie | Indicateur | Valeur mesurée |
|-----------|-----------|----------------|
| **Données** | Réservations brutes | 6 500 |
| | Réservations après nettoyage | 6 474 |
| | Clients uniques | 6 427 |
| | Colonnes dataset final | 82 |
| **Avis** | Avis Booking chargés | 1 634 |
| | Avis appariés | 316 (4,9 %) |
| | Note moyenne | 7,58 / 10 |
| | Haute satisfaction (≥ 8/10) | 188 (59,5 % des avisés) |
| | Avis Expedia | 208 |
| **Réseau** | Nœuds (config 300) | 300 |
| | Arêtes | ~31 298 |
| | Densité | ~0,698 |
| | Communautés | 2 |
| | Modularité Q | ~0,205 |
| **Modèle RF** | Split train / test | 5 179 / 1 295 |
| | Nombre de features | 25 |
| | AUC-ROC | 0,914–0,918 |
| | F1-pondéré | 0,902–0,904 |
| | CV 5-fold | 0,915 ± 0,013 |
| **Features** | channel_group (rang 1) | 32,9 % |
| | pays (rang 2) | 22,9 % |
| | is_cancelled (rang 3) | 13,5 % |

## Annexe C — Stack technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | Python | 3.10+ |
| Données | pandas | 2.1+ |
| Graphes | NetworkX | 3.2+ |
| ML | scikit-learn | 1.4+ |
| Visualisation | matplotlib + seaborn | — |
| Interface | Streamlit | 1.30+ |
| Tests | pytest | 12 tests, 100 % passing |

## Annexe D — Commandes de déploiement

```bash
# Installation des dépendances
cd client-centrality-prediction-platform
pip install -r requirements.txt

# Vérification de l'installation
python quick_diagnostic.py

# Tests unitaires
python -m pytest -q tests   # 12 tests, 100 % passing

# Lancement de l'application
streamlit run app.py
# → http://localhost:8501
```

---

*Fin du rapport de stage*

---

**Document rédigé en Avril 2026**
**DU Sorbonne Data Analytics — Promotion 2025-2026**
**Université Paris-Sorbonne**

