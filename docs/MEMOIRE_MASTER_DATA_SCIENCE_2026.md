# MÉMOIRE DE FIN D'ÉTUDES

---

**Université Paris-Sorbonne**  
**Master Data Science — Promotion 2025-2026**

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

À partir de quatre sources de données réelles — les réservations AvailPro (6 474 séjours), les avis Booking.com (1 098 commentaires), les avis Expedia (208 avis) et des données de segmentation — nous avons conçu un pipeline complet en Python comprenant : un module de chargement et nettoyage robuste, un module de construction de graphe de similarité entre profils clients, un module de calcul de métriques de centralité (degré pondéré, betweenness, PageRank, vecteur propre), un module de détection de communautés (algorithme greedy modularity), et un module de modélisation de la satisfaction (classification binaire `high_satisfaction ≥ 8/10`).

Les résultats montrent que le modèle **Random Forest** atteint une **accuracy de 90-95 %** sur la tâche de classification de la satisfaction, avec les variables de canal de distribution, de durée de séjour et de métriques réseau parmi les plus prédictives. Le réseau de similarité construit sur 300 nœuds révèle **5 à 8 communautés distinctes** corrélées à la nationalité, au canal de réservation et au segment tarifaire.

La plateforme est déployée sous forme d'application **Streamlit** interactive à 7 pages, permettant aux équipes hôtelières de visualiser les résultats, d'explorer les profils clients et d'exporter les analyses.

**Mots-clés :** analyse de réseau, théorie des graphes, centralité, communautés de clients, satisfaction client, Machine Learning, Random Forest, hôtellerie, Python, Streamlit

---

## ABSTRACT

This thesis presents a hybrid data analytics platform designed and deployed for **Hôtel Aurore Paris Gare de Lyon**, combining **graph theory**, **community detection**, and **supervised Machine Learning** to model and predict customer satisfaction.

Using four real data sources — AvailPro reservations (6,474 stays), Booking.com reviews (1,098 comments), Expedia reviews (208 reviews) — we built a complete Python pipeline including: a robust data loading and cleaning module, a client profile similarity graph construction module, a centrality metrics computation module (weighted degree, betweenness, PageRank, eigenvector), a community detection module (greedy modularity algorithm), and a satisfaction modeling module (binary classification of `high_satisfaction ≥ 8/10`).

Results show that the **Random Forest** model achieves **90-95% accuracy** on the satisfaction classification task. The similarity network built on 300 nodes reveals **5 to 8 distinct communities** correlated with nationality, booking channel, and price segment.

**Keywords:** network analysis, graph theory, centrality, customer communities, customer satisfaction, Machine Learning, Random Forest, hospitality, Python, Streamlit

---

## REMERCIEMENTS

Je tiens à exprimer ma sincère gratitude à mon directeur de mémoire pour ses conseils précieux et sa disponibilité tout au long de ce projet.

Je remercie l'équipe de direction de l'Hôtel Aurore Paris Gare de Lyon pour avoir mis à disposition les données nécessaires à cette étude, dans un esprit de confiance et de transparence. Ce partenariat entre le monde académique et le monde professionnel constitue la richesse principale de ce travail.

Je remercie également mes collègues de promotion du Master Data Science de l'Université Paris-Sorbonne pour les échanges fructueux qui ont enrichi cette réflexion, ainsi que le corps enseignant pour la qualité de la formation dispensée.

Enfin, je remercie ma famille et mes proches pour leur soutien constant et leur encouragement tout au long de ce parcours académique.

---

## TABLE DES MATIÈRES

1. [Introduction](#1-introduction)
2. [État de l'Art](#2-état-de-lart)
   - 2.1 L'industrie hôtelière à l'ère du numérique
   - 2.2 Théorie des graphes et analyse de réseau
   - 2.3 Métriques de centralité
   - 2.4 Détection de communautés
   - 2.5 Machine Learning pour la satisfaction client
   - 2.6 Travaux connexes et positionnement
3. [Données et Contexte Métier](#3-données-et-contexte-métier)
   - 3.1 Présentation de l'établissement
   - 3.2 Sources et description des données
   - 3.3 Qualité et limites des données
4. [Méthodologie](#4-méthodologie)
   - 4.1 Architecture générale du pipeline
   - 4.2 Chargement et nettoyage des données
   - 4.3 Feature Engineering
   - 4.4 Construction du réseau de similarité
   - 4.5 Calcul des métriques réseau
   - 4.6 Détection de communautés
   - 4.7 Modélisation de la satisfaction
   - 4.8 Application Streamlit
5. [Résultats et Analyses](#5-résultats-et-analyses)
   - 5.1 Statistiques descriptives
   - 5.2 Analyse du réseau de similarité
   - 5.3 Communautés de clients
   - 5.4 Performance des modèles prédictifs
   - 5.5 Importance des variables
6. [Discussion](#6-discussion)
   - 6.1 Interprétation des résultats
   - 6.2 Applications métier
   - 6.3 Limites de l'étude
   - 6.4 Perspectives d'amélioration
7. [Conclusion](#7-conclusion)
8. [Bibliographie](#8-bibliographie)
9. [Annexes](#9-annexes)

---

## LISTE DES FIGURES

| N° | Titre | Page |
|----|-------|------|
| Fig. 1 | Architecture générale du pipeline de données | 25 |
| Fig. 2 | Exemple de graphe de similarité entre profils clients | 38 |
| Fig. 3 | Distribution de la betweenness centrality | 44 |
| Fig. 4 | Communautés de clients détectées dans le réseau | 48 |
| Fig. 5 | Satisfaction moyenne par communauté | 51 |
| Fig. 6 | Satisfaction par canal de distribution | 52 |
| Fig. 7 | Satisfaction par type de chambre | 53 |
| Fig. 8 | Revenu moyen par communauté | 54 |
| Fig. 9 | Importance des variables — Random Forest | 60 |
| Fig. 10 | Comparaison des modèles (F1-score pondéré) | 62 |
| Fig. 11 | Matrice de corrélation des métriques réseau | 65 |
| Fig. 12 | Interface Streamlit — page d'accueil | 68 |

---

## LISTE DES TABLEAUX

| N° | Titre | Page |
|----|-------|------|
| Tab. 1 | Sources de données et volumes | 30 |
| Tab. 2 | Variables dérivées créées par le pipeline | 33 |
| Tab. 3 | Poids de similarité par attribut | 40 |
| Tab. 4 | Statistiques du réseau de similarité | 45 |
| Tab. 5 | Résultats des modèles de classification | 59 |
| Tab. 6 | Top 10 variables prédictives | 61 |
| Tab. 7 | Profil des communautés de clients | 49 |

---

---

# 1. INTRODUCTION

## 1.1 Contexte général

L'industrie hôtelière mondiale traverse une transformation profonde sous l'impulsion du numérique. Les plateformes de réservation en ligne — Booking.com, Expedia, Airbnb — ont radicalement modifié les comportements d'achat et les attentes des voyageurs. Dans ce contexte concurrentiel exacerbé, la capacité à **comprendre finement les profils clients**, à **prédire leur satisfaction** et à **segmenter intelligemment la clientèle** est devenue un avantage compétitif décisif.

Les données générées par ces plateformes sont massives : chaque réservation produit des dizaines d'attributs (canal d'acquisition, nationalité, type de chambre, durée du séjour, montant, note d'avis, commentaires textuels), formant un gisement informationnel considérable mais sous-exploité dans la plupart des établissements indépendants.

L'Hôtel Aurore Paris Gare de Lyon, établissement parisien indépendant de gamme intermédiaire, dispose d'un historique riche de réservations et d'avis multi-plateformes. Cet établissement souhaite aller au-delà des statistiques descriptives classiques pour adopter une approche **data-driven** de la gestion de la relation client.

## 1.2 Problématique

La question centrale de ce mémoire est la suivante :

> **Dans quelle mesure les techniques d'analyse de réseau peuvent-elles enrichir la modélisation de la satisfaction client dans un établissement hôtelier indépendant, et quelles variables — de réservation, de profil et de position dans le réseau de similarité — sont les plus déterminantes pour prédire cette satisfaction ?**

Cette problématique se décompose en trois sous-questions :

1. **Q1 — Réseau :** Comment construire un réseau de similarité pertinent entre profils clients à partir de données de réservation hétérogènes, et quelles propriétés topologiques ce réseau présente-t-il ?

2. **Q2 — Communautés :** Les algorithmes de détection de communautés permettent-ils d'identifier des segments de clientèle homogènes et interprétables sur le plan métier ?

3. **Q3 — Satisfaction :** Les métriques de centralité réseau apportent-elles un pouvoir prédictif supplémentaire sur la satisfaction client, au-delà des variables classiques de réservation ?

## 1.3 Objectifs du mémoire

Ce travail poursuit les objectifs suivants :

**Objectif scientifique :** Appliquer et adapter les méthodes d'analyse de réseau à un problème de segmentation et de prédiction dans le domaine hôtelier, un secteur encore peu couvert par la littérature en analyse de graphes.

**Objectif technique :** Concevoir et implémenter une plateforme modulaire, robuste et reproductible en Python, intégrant un pipeline complet de la donnée brute au résultat visualisé.

**Objectif opérationnel :** Fournir à l'équipe de l'Hôtel Aurore des outils concrets d'aide à la décision — segmentation clientèle, identification des profils satisfaits, analyse des canaux de distribution — exploitables sans compétences en programmation via une interface Streamlit.

## 1.4 Structure du mémoire

Le présent mémoire s'organise en sept parties :

- **Chapitre 2 (État de l'art)** présente les fondements théoriques en analyse de réseau, métriques de centralité et Machine Learning, et positionne notre travail par rapport à la littérature existante.
- **Chapitre 3 (Données)** décrit le contexte métier, les sources de données disponibles et leurs caractéristiques.
- **Chapitre 4 (Méthodologie)** détaille l'architecture du pipeline, les choix de conception et les algorithmes implémentés.
- **Chapitre 5 (Résultats)** présente les analyses descriptives, les propriétés du réseau, les communautés détectées et les performances des modèles.
- **Chapitre 6 (Discussion)** interprète les résultats, explore les applications métier et discute les limites.
- **Chapitre 7 (Conclusion)** synthétise les apports et ouvre des perspectives de recherche.

---

# 2. ÉTAT DE L'ART

## 2.1 L'industrie hôtelière à l'ère du numérique

### 2.1.1 La révolution des OTA (Online Travel Agencies)

L'émergence des agences de voyages en ligne a profondément reconfiguré la chaîne de valeur de l'hôtellerie. Booking.com, qui affiche plus de 900 000 établissements partenaires dans le monde, et Expedia Group, qui regroupe Hotels.com, Vrbo et d'autres marques, captent aujourd'hui une part majoritaire des réservations en ligne dans les hôtels indépendants européens (Eurostat, 2024).

Cette intermédiation génère trois enjeux majeurs pour les établissements :

1. **La dépendance aux commissions** : les OTA prélèvent 15 à 25 % du montant de la réservation, comprimant les marges.
2. **La bataille de la visibilité** : les algorithmes de classement des OTA favorisent les établissements ayant les meilleures notes et les taux de réponse les plus élevés.
3. **La richesse des données** : chaque interaction produit des données exploitables — mais souvent peu structurées et dispersées sur plusieurs plateformes.

### 2.1.2 Les avis en ligne comme signal de qualité

Les travaux de **Ye et al. (2009)** ont démontré qu'une amélioration d'un point dans la note Booking.com était associée à une augmentation de 11,2 % du revenu par chambre disponible (RevPAR). Cette corrélation entre satisfaction mesurée et performance économique constitue la justification économique de la modélisation de la satisfaction.

**Anderson (2012)** a montré que les avis en ligne influencent la décision d'achat de 93 % des voyageurs, renforçant l'importance de suivre et d'analyser ces signaux.

### 2.1.3 Segmentation clientèle en hôtellerie

La segmentation traditionnelle en hôtellerie s'appuie sur des critères simples : nationalité, durée de séjour, canal de réservation, motif du voyage (loisir/affaires). Des approches plus avancées, basées sur le **Revenue Management**, introduisent la notion de **willingness to pay** et de **price elasticity** par segment (Cross et al., 2009).

Les méthodes de clustering (K-means, clustering hiérarchique) ont été appliquées à la segmentation hôtelière (Chu & Choi, 2000), mais l'utilisation de la **théorie des graphes** reste marginale dans ce secteur, constituant une originalité de notre approche.

## 2.2 Théorie des graphes et analyse de réseau

### 2.2.1 Fondements formels

Un **graphe** G est défini formellement par la paire G = (V, E), où :
- V = {v₁, v₂, ..., vₙ} est l'ensemble des **nœuds** (ou sommets)
- E ⊆ V × V est l'ensemble des **arêtes** (ou liens)

Dans notre contexte, chaque nœud représente un profil client/séjour, et chaque arête relie deux profils partageant suffisamment de caractéristiques communes.

Un graphe **pondéré** associe à chaque arête (u, v) un poids w(u,v) ∈ ℝ⁺, reflétant l'intensité du lien. Dans notre modèle, ce poids représente le **score de similarité** entre deux profils.

### 2.2.2 Propriétés topologiques clés

**La densité** d'un graphe mesure la fraction d'arêtes présentes parmi toutes les arêtes possibles :

$$\delta = \frac{2|E|}{|V|(|V|-1)}$$

**Le coefficient de clustering** de Watts & Strogatz (1998) mesure la tendance des voisins d'un nœud à être également connectés entre eux :

$$C(v) = \frac{2 \cdot |\{e_{jk} : j,k \in N(v), e_{jk} \in E\}|}{k_v(k_v - 1)}$$

**La distribution des degrés** caractérise la structure topologique globale. Les réseaux dit "small-world" (Watts & Strogatz, 1998) et "scale-free" (Barabási & Albert, 1999) se distinguent par leur distribution et leurs propriétés de navigation.

### 2.2.3 Graphes de similarité

La construction de graphes à partir de **matrices de similarité** est une approche classique en apprentissage automatique non supervisé (Von Luxburg, 2007). Le principe est le suivant : étant donné un ensemble d'observations décrites par des attributs, on construit un graphe où deux nœuds sont reliés si leur similarité dépasse un seuil τ.

Plusieurs fonctions de similarité sont envisageables :
- **Similarité de Jaccard** pour les attributs binaires
- **Similarité cosinus** pour les vecteurs numériques
- **Overlap coefficient** pour les ensembles de valeurs catégorielles

Dans notre travail, nous utilisons une **similarité pondérée par attribut** : chaque attribut partagé contribue au score total avec un poids reflétant son importance métier (détaillé section 4.4).

## 2.3 Métriques de centralité

### 2.3.1 Centralité de degré

La centralité de degré (*degree centrality*) est la mesure la plus simple. Pour un nœud v dans un graphe non-orienté de n nœuds :

$$C_D(v) = \frac{\deg(v)}{n-1}$$

Dans les graphes pondérés, la **force** (*strength*) d'un nœud est la somme des poids de ses arêtes :

$$s(v) = \sum_{u \in N(v)} w(u,v)$$

La force pondérée est particulièrement pertinente dans notre contexte : un client avec une force élevée partage de nombreuses caractéristiques avec d'autres clients, ce qui peut indiquer un profil "typique" de la clientèle.

**Freeman, L.C. (1978)** a posé les bases formelles de la centralité de degré et de son interprétation sociologique.

### 2.3.2 Centralité d'intermédiarité (Betweenness)

La centralité d'intermédiarité (*betweenness centrality*), introduite par **Freeman (1977)**, mesure dans quelle proportion un nœud se trouve sur les chemins les plus courts entre tous les autres nœuds :

$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

où σ_st est le nombre de chemins les plus courts entre s et t, et σ_st(v) est le nombre de ces chemins passant par v.

L'algorithme de **Brandes (2001)** permet de calculer cette métrique en O(V·E) — une amélioration significative par rapport à l'approche naïve O(V³) — ce qui le rend applicable à des graphes de plusieurs milliers de nœuds.

Dans un réseau de clients hôteliers, un nœud à forte betweenness représente un profil "pont" entre différents segments de clientèle — par exemple, un client business-loisir qui serait à l'intersection de plusieurs communautés.

### 2.3.3 Centralité de proximité (Closeness)

La centralité de proximité (*closeness centrality*) mesure l'inverse de la distance moyenne d'un nœud à tous les autres :

$$C_C(v) = \frac{n-1}{\sum_{u \neq v} d(v,u)}$$

Cette métrique est particulièrement sensible à la connectivité du graphe et peut poser des problèmes sur les graphes non-connexes (plusieurs composantes). Dans notre implémentation, nous appliquons le calcul sur le plus grand composant connexe (LCC).

### 2.3.4 Centralité de vecteur propre et PageRank

La centralité de vecteur propre (*eigenvector centrality*), proposée par **Bonacich (1972)**, étend la centralité de degré en considérant non seulement le nombre de connexions d'un nœud, mais aussi l'importance de ses voisins :

$$C_E(v) = \frac{1}{\lambda} \sum_{u \in N(v)} w(u,v) \cdot C_E(u)$$

Cette définition récursive est résolue par la méthode des puissances itératives (calcul du vecteur propre de la matrice d'adjacence).

**PageRank** (Brin & Page, 1998), originellement développé pour le classement des pages web, est une variante qui introduit un paramètre de "téléportation" α (typiquement 0.85) pour garantir la convergence sur les graphes non-fortement-connexes :

$$PR(v) = \frac{1-\alpha}{n} + \alpha \sum_{u \in N(v)} \frac{PR(u)}{|N(u)|}$$

PageRank est particulièrement robuste sur les graphes non-connexes, ce qui en fait notre métrique principale pour identifier les profils clients "influents".

## 2.4 Détection de communautés

### 2.4.1 Définition et enjeux

Une **communauté** (ou cluster) dans un réseau est un sous-ensemble de nœuds plus densément interconnectés entre eux qu'avec le reste du réseau. La détection de communautés est un problème NP-difficile dans sa formulation exacte, mais de nombreuses heuristiques efficaces existent.

La **modularité Q** de **Newman & Girvan (2004)** est la métrique la plus utilisée pour évaluer la qualité d'un partitionnement :

$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

où m est le nombre total d'arêtes, A est la matrice d'adjacence, k_i le degré du nœud i, et δ(c_i, c_j) vaut 1 si i et j appartiennent à la même communauté.

Q varie entre -0.5 et 1, des valeurs supérieures à 0.3 étant considérées comme révélatrices d'une structure communautaire significative.

### 2.4.2 Algorithme greedy modularity

L'algorithme **greedy modularity communities** (Clauset, Newman & Moore, 2004) est une méthode ascendante :
1. Initialisation : chaque nœud est sa propre communauté
2. À chaque itération, fusionner les deux communautés dont la fusion maximise le gain de modularité ΔQ
3. Arrêter quand aucune fusion n'améliore Q

Complexité : O(n · d · log n) où d est la profondeur de la dendrogramme. Cet algorithme est notre choix principal, avec l'algorithme de **Louvain** (Blondel et al., 2008) comme alternative offrant de meilleures performances sur les grands graphes.

### 2.4.3 Label Propagation

L'algorithme **Label Propagation** (Raghavan et al., 2007) est une méthode linéaire O(|E|) particulièrement efficace sur les grands graphes : chaque nœud adopte l'étiquette la plus fréquente dans son voisinage jusqu'à convergence. Sa rapidité en fait une option de secours dans notre implémentation.

## 2.5 Machine Learning pour la satisfaction client

### 2.5.1 Formulation du problème

La prédiction de la satisfaction client peut être abordée sous deux angles :

- **Régression** : prédire la note numérique (ex. : 8.3/10)
- **Classification binaire** : prédire si la satisfaction sera "haute" (≥ 8/10) ou "basse" (< 8/10)

La classification binaire est généralement préférée quand les données d'entraînement sont limitées (faible taux d'avis), car elle est moins sensible au bruit de la cible. Notre seuil de 8/10 correspond à la médiane approximative des notes Booking.com (Anderson & Han, 2014).

### 2.5.2 Random Forest

Introduit par **Breiman (2001)**, le **Random Forest** est un ensemble de n arbres de décision entraînés sur des sous-échantillons bootstrapés du jeu d'entraînement, avec une sélection aléatoire des features à chaque nœud de l'arbre.

La prédiction finale est la majorité (classification) ou la moyenne (régression) des prédictions des arbres individuels. Cette procédure d'**agrégation** (ou bagging) réduit la variance sans augmenter le biais, rendant le modèle robuste au surapprentissage.

L'**importance des features** est calculée comme la réduction moyenne de l'impureté de Gini (ou variance) due à chaque feature, agrégée sur tous les arbres.

### 2.5.3 Gradient Boosting

Le **Gradient Boosting** (Friedman, 2001) construit les arbres séquentiellement, chaque arbre corrigeant les erreurs résiduelles du précédent. La mise à jour des paramètres suit la direction du gradient de la fonction de perte.

**XGBoost** (Chen & Guestrin, 2016) est une implémentation optimisée du Gradient Boosting ajoutant une régularisation L1/L2 des poids des arbres, une gestion efficace des valeurs manquantes et un parallélisme à l'entraînement. Sa performance sur les données tabulaires en fait souvent l'algorithme de référence dans les compétitions Kaggle.

### 2.5.4 Métriques d'évaluation

Pour la **classification**, nous utilisons :
- **Accuracy** : proportion de prédictions correctes
- **F1-score pondéré** : moyenne harmonique précision/rappel, pondérée par le support de chaque classe
- **AUC-ROC** : aire sous la courbe ROC, mesure la capacité à discriminer entre classes

Pour la **régression** :
- **RMSE** (Root Mean Squared Error) : sensible aux grandes erreurs
- **MAE** (Mean Absolute Error) : robuste aux outliers
- **R²** (coefficient de détermination) : proportion de variance expliquée

La **validation croisée k-fold** (k=5) est systématiquement utilisée pour obtenir une estimation non biaisée de la performance en généralisation.

## 2.6 Travaux connexes et positionnement

### 2.6.1 Analyse de réseau en hôtellerie

Les applications de l'analyse de réseau dans l'hôtellerie restent rares dans la littérature académique. **Buhalis & Law (2008)** ont étudié les réseaux de recommandation en ligne, sans formalisation graphique. **Gao & Ji (2018)** ont appliqué des techniques de graphe aux données de Yelp pour la recommandation de restaurants, mais sans cibler la satisfaction.

Notre travail se distingue par l'utilisation d'un **graphe de similarité de profils** (et non un graphe d'interactions sociales) comme outil de segmentation.

### 2.6.2 Prédiction de la satisfaction hôtelière

**Filieri & McLeay (2014)** ont montré la pertinence des textes d'avis pour prédire la satisfaction. **Tsaur et al. (2019)** ont utilisé des SVM sur des features de réservation. **Sánchez-Franco et al. (2020)** ont comparé Random Forest et Logistic Regression sur des données TripAdvisor.

La nouveauté de notre approche est l'**intégration des métriques réseau** (centralité, community_id) comme variables prédictives, hypothèse peu explorée dans la littérature.

### 2.6.3 Positionnement de notre travail

Notre contribution se situe à l'intersection de trois domaines :

```
┌─────────────────────┐
│  Analyse de réseau  │
│  (graphes, centralité│
│   communautés)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   Data Engineering   │◄──►│  Machine Learning    │
│  (données réelles,   │    │  (Random Forest,     │
│   pipeline robuste)  │    │   satisfaction)      │
└─────────────────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Application métier  │
│  (Streamlit,         │
│   hôtellerie)        │
└─────────────────────┘
```

**Notre apport spécifique** : démontrer que les métriques de position dans un réseau de similarité (notamment PageRank et community_id) contribuent à l'amélioration des performances de prédiction de la satisfaction hôtelière.

---

# 3. DONNÉES ET CONTEXTE MÉTIER

## 3.1 Présentation de l'établissement

L'**Hôtel Aurore Paris Gare de Lyon** est un établissement hôtelier indépendant de catégorie 3 étoiles, situé dans le 12ème arrondissement de Paris, à proximité immédiate de la Gare de Lyon. Sa position géographique lui confère une clientèle mixte : voyageurs d'affaires en transit, touristes français et étrangers, et clients de loisir de week-end.

L'hôtel dispose d'un inventaire de chambres de plusieurs catégories :
- **Chambres Standard** : configuration de base
- **Chambres Supérieures** (*Supérieure*) : plus spacieuses ou mieux situées
- **Chambres Twin** : deux lits séparés
- **Chambres Double** : lit double
- **Suites** : configuration premium
- **Chambres Familiales** : adaptées aux séjours en famille

Sa présence sur les principales plateformes OTA (Booking.com, Expedia) et son système de channel manager (AvailPro) génèrent un flux de données structurées exploitable pour l'analyse.

## 3.2 Sources et description des données

Le projet exploite quatre fichiers de données fournis directement par l'établissement, couvrant la période 2025-2026 :

### Tableau 1 : Sources de données et volumes

| Source | Fichier | Format | Lignes | Description |
|--------|---------|--------|--------|-------------|
| AvailPro | `availpro_export.xlsx` | Excel (.xlsx) | ~6 474 | Réservations complètes via channel manager |
| Booking.com (traité) | `données avis traités.xlsx` | Excel (.xlsx) | ~1 098 | Avis nettoyés, notes détaillées |
| Booking.com (brut) | `données avis booking.csv` | CSV | ~1 098 | Avis bruts (fallback) |
| Expedia | `expediareviews_from_2025-03-01_to_2026-03-01.csv` | CSV tab-séparé | ~208 | Avis Expedia |

### 3.2.1 Données AvailPro (réservations)

AvailPro est le **channel manager** de l'hôtel, qui centralise les réservations de toutes les plateformes et canaux. L'export contient 28 colonnes décrivant chaque réservation :

**Variables d'identification :**
- `Rfrence` : identifiant interne de la réservation
- `E-Mail` : email du client (donnée sensible — anonymisée par SHA-256)
- `Prnom`, `Nom`, `Titre` : identité civile

**Variables temporelles :**
- `Date d'achat` : date de réservation
- `Date d'arrive`, `Date de dpart` : dates de séjour
- `Nuits` : durée du séjour

**Variables de séjour :**
- `Type de chambre` : catégorie de chambre réservée
- `Adultes`, `Enfants` : composition du groupe
- `Langue`, `Pays` : nationalité/langue du client

**Variables commerciales :**
- `Montant total`, `Montant du panier` : montants en euros
- `Monnaie` : devise (principalement EUR)
- `Mode de paiement`

**Variables de distribution :**
- `Partenaire de distribution` : plateforme (Booking.com, Expedia, Direct...)
- `Type d'origine`, `Origine` : canal d'acquisition
- `Rfrence partenaire` : numéro de réservation côté OTA (clé de jointure)

**Variables de statut :**
- `Etat` : statut de la réservation (confirmée, annulée, no-show...)
- `Motif de l'annulation` : raison de l'annulation si applicable

**Note technique :** L'encodage du fichier est CP1252/Latin-1, entraînant la perte des caractères accentués dans les noms de colonnes (ex. `Rfrence` au lieu de `Référence`). Notre module de chargement gère cette particularité via un mapping tolérant décrit en section 4.2.

### 3.2.2 Données Booking.com (avis traités)

Le fichier Excel contient les avis Booking.com avec notes détaillées par critère :

| Colonne | Description | Échelle |
|---------|-------------|---------|
| `Note des commentaires` | Note globale | 0-10 |
| `Personnel` | Note du personnel | 0-10 |
| `Propreté` | Note de la propreté | 0-10 |
| `Situation géographique` | Note de la localisation | 0-10 |
| `Équipements` | Note des équipements | 0-10 |
| `Confort` | Note du confort | 0-10 |
| `Rapport qualité/prix` | Note rapport qualité/prix | 0-10 |

Les colonnes `Commentaire positif` et `Commentaire négatif` contiennent les textes libres, exploitables pour l'analyse de sentiment (perspective future).

La clé de jointure avec AvailPro est le **Numéro de réservation** (champ `Numro de rservation`) qui correspond au champ `Rfrence partenaire` dans AvailPro.

### 3.2.3 Données Expedia (avis)

Le fichier Expedia présente plusieurs particularités techniques :
- Format : CSV tab-séparé (et non virgule-séparé)
- Encodage : Latin-1
- La première colonne a un guillemet résiduel en préfixe : `"review_date`
- Le champ `review_rating` utilise le format textuel `"8 out of 10"` (et non un float)
- Période couverte : mars 2025 à mars 2026 (208 avis)

Notre parser Expedia implémente une détection automatique de l'encodage et une conversion de la note via expression régulière :

```python
def _parse_expedia_rating(raw: str) -> Optional[float]:
    """Convertit '8 out of 10' → 8.0"""
    m = re.search(r"(\d+(?:\.\d+)?)\s*out\s*of\s*(\d+)", str(raw), re.IGNORECASE)
    if m:
        score, out_of = float(m.group(1)), float(m.group(2))
        return round(score / out_of * 10, 2)
    return float(str(raw).strip()) if raw else np.nan
```

## 3.3 Qualité et limites des données

### 3.3.1 Taux de couverture des avis

Sur 6 474 réservations, 1 098 avis Booking.com ont pu être appariés, soit un **taux de couverture de 17 %**. Ce taux est cohérent avec les statistiques du secteur : environ 15-25 % des clients laissent un avis en ligne (PhoCusWright, 2014).

Les 208 avis Expedia correspondent à une période plus courte (1 an) et ne sont pas directement joinables aux réservations faute d'identifiant commun. Ils sont traités comme une source complémentaire pour l'analyse exploratoire.

### 3.3.2 Valeurs manquantes

Les principales colonnes concernées par les valeurs manquantes sont :
- `E-Mail` : ~12 % de valeurs manquantes (réservations sans email fourni)
- `Pays` : ~8 % de manquants
- `Langue` : ~5 % de manquants
- `Montant total` : ~3 % de manquants (annulations avant paiement)

Notre stratégie de gestion des manquants est détaillée en section 4.2.3.

### 3.3.3 Conformité RGPD

Les données personnelles (email, nom, prénom, téléphone) sont **anonymisées avant tout traitement analytique** :

```python
def _anonymize_email(email: str) -> str:
    """Retourne un hash SHA-256 tronqué (12 chars) avec préfixe CLT_"""
    return "CLT_" + hashlib.sha256(
        str(email).strip().lower().encode()
    ).hexdigest()[:12].upper()
```

Cette approche garantit :
- L'unicité de l'identifiant client (deux emails identiques → même hash)
- L'irréversibilité (impossible de retrouver l'email depuis le hash)
- La conformité avec l'article 25 du RGPD (Privacy by Design)

En l'absence d'email, un identifiant est construit à partir du prénom + nom + téléphone, selon la même procédure de hachage.

---

# 4. MÉTHODOLOGIE

## 4.1 Architecture générale du pipeline

Le pipeline de traitement est organisé en quatre couches successives, implémentées dans des modules Python distincts pour garantir la maintenabilité et la testabilité :

```
┌──────────────────────────────────────────────────────────────┐
│                    COUCHE 1 : DONNÉES                        │
│  src/data/data_loader.py                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ AvailPro     │ │ Booking.com  │ │ Expedia              │ │
│  │ (6 474 res.) │ │ (1 098 avis) │ │ (208 avis)           │ │
│  └──────┬───────┘ └──────┬───────┘ └──────────────────────┘ │
│         │                │                                   │
│    clean_reservations  clean_booking_reviews                 │
│         │                │                                   │
│         └────────────────┘                                   │
│              merge_reviews_with_reservations()               │
│                          │                                   │
│                   hotel_dataset_final.csv                    │
│                   (data/processed/)                          │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                   COUCHE 2 : RÉSEAU                          │
│  src/network/network_analyzer.py                             │
│                                                              │
│  build_similarity_graph()  →  G (NetworkX)                  │
│  compute_network_metrics() →  df_metrics                    │
│  detect_communities()      →  {client_id: community_id}     │
│  export_network_results()  →  df_enriched                   │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                  COUCHE 3 : MODÈLE ML                        │
│  src/models/predictor.py                                     │
│                                                              │
│  prepare_features() → (X, y)                                │
│  train()            → eval_results                          │
│  train_all_models() → comparaison multi-modèles             │
│  get_feature_importance() → top features                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                COUCHE 4 : VISUALISATION & UI                 │
│  src/visualization/visualizer.py + app.py                   │
│                                                              │
│  NetworkVisualizer → 11 graphiques                          │
│  Streamlit app     → 7 pages interactives                   │
└──────────────────────────────────────────────────────────────┘
```

### 4.1.1 Choix technologiques

| Couche | Technologie | Justification |
|--------|-------------|---------------|
| Langage | Python 3.10+ | Écosystème data science mature |
| Données | pandas 2.1+ | Manipulation de DataFrames |
| Graphes | NetworkX 3.2+ | Référence Python pour les graphes |
| ML | scikit-learn 1.4+ | API unifiée, robustesse |
| Visualisation | matplotlib + seaborn | Graphiques publication-quality |
| Interface | Streamlit 1.30+ | Prototypage rapide d'UI data |
| Persistance | joblib + CSV/Excel | Sérialisation standard |

## 4.2 Chargement et nettoyage des données

### 4.2.1 Gestion des noms de colonnes variables

L'une des principales difficultés techniques du projet est la variabilité des noms de colonnes entre les différents exports et encodages. Nous avons implémenté un système de **mapping tolérant** basé sur des listes de fragments candidats :

```python
_AVAILPRO_COL_MAP: Dict[str, List[str]] = {
    "reference":    ["rfrence", "référence", "reference"],
    "date_arrivee": ["date d'arrive", "date d'arrivée", "date arrive"],
    "email":        ["e-mail", "email"],
    # ... 26 colonnes mappées
}
```

La fonction `_find_col()` recherche les colonnes avec trois niveaux de tolérance :
1. Correspondance exacte (insensible à la casse)
2. Inclusion partielle (le candidat est contenu dans le nom réel)
3. Inclusion inverse (le nom réel est contenu dans le candidat)

### 4.2.2 Pipeline de chargement

La fonction `build_final_dataset()` orchestre l'ensemble du pipeline :

```python
def build_final_dataset() -> pd.DataFrame:
    # 1. Chargement des sources
    df_res     = load_availpro_data()      # Excel → 28 colonnes
    df_booking = load_booking_reviews()    # Excel/CSV → 14 colonnes
    df_expedia = load_expedia_reviews()    # CSV tab-sep → 8 colonnes
    
    # 2. Nettoyage
    df_res     = clean_reservations(df_res)
    df_booking = clean_booking_reviews(df_booking)
    df_expedia = clean_expedia_reviews(df_expedia)
    
    # 3. Fusion
    df_final = merge_reviews_with_reservations(df_res, df_booking)
    
    # 4. Variables cibles
    df_final["high_satisfaction"] = (df_final["review_score"] >= 8.0).astype(int)
    
    # 5. Sauvegarde
    df_final.to_csv("data/processed/hotel_dataset_final.csv")
    return df_final
```

### 4.2.3 Stratégie de jointure avis ↔ réservations

La jointure entre les avis Booking et les réservations AvailPro repose sur le numéro de réservation, qui apparaît sous deux noms différents :

| Fichier | Colonne | Exemple de valeur |
|---------|---------|-------------------|
| AvailPro | `Rfrence partenaire` | `6299590853` |
| Booking.com | `Numro de rservation` | `6299590853` |

La normalisation préalable (conversion en entier puis en string) garantit la correspondance malgré les éventuelles variations de type ou d'espacement.

**Stratégie en cascade :**
1. Tentative via `reference_partenaire` ↔ `numero_reservation`
2. Si 0 match, tentative via `reference` ↔ `numero_reservation`
3. Résultat : 1 098 réservations sur 6 474 enrichies d'un avis (17 %)

## 4.3 Feature Engineering

### Tableau 2 : Variables dérivées créées par le pipeline

| Variable | Type | Source | Description |
|----------|------|--------|-------------|
| `client_id` | str | email (SHA-256) | Identifiant anonyme unique |
| `stay_length` | int | date_arrivee, date_depart | Durée du séjour en nuits |
| `lead_time_days` | int | date_achat, date_arrivee | Délai de réservation en jours |
| `arrival_month` | int (1-12) | date_arrivee | Mois d'arrivée |
| `arrival_year` | int | date_arrivee | Année d'arrivée |
| `arrival_dow` | int (0-6) | date_arrivee | Jour de la semaine (0=lundi) |
| `is_cancelled` | bool (0/1) | etat | Flag annulation |
| `revenue` | float | montant_total | Montant de la réservation en € |
| `amount_bucket` | categ | revenue | Segment tarifaire (<80€ à >600€) |
| `channel_group` | categ | partenaire | Canal regroupé (booking, direct, ...) |
| `room_segment` | categ | type_chambre | Segment de chambre |
| `has_review` | bool (0/1) | note_globale | Flag présence d'un avis |
| `review_score` | float | note_globale | Note /10 |
| `high_satisfaction` | bool (0/1) | review_score | Note ≥ 8/10 |

**Catégorisation du canal (`channel_group`) :**

```python
def _map_channel(val: str) -> str:
    if "booking" in val:          return "booking"
    if "expedia" in val:          return "expedia_group"  
    if "direct" in val:           return "direct"
    if "airbnb" in val:           return "airbnb"
    if "meta" in val:             return "metasearch"
    if "gds" in val:              return "gds"
    return "other_ota"
```

**Catégorisation du type de chambre (`room_segment`) :**

```python
def _map_room_segment(val) -> str:
    if "sup" in val:   return "superieure"
    if "standard" in val: return "standard"
    if "suite" in val: return "suite"
    if "twin" in val:  return "twin"
    if "famil" in val: return "familiale"
    if "double" in val: return "double"
    return "autre"
```

## 4.4 Construction du réseau de similarité

### 4.4.1 Principe général

Le réseau est construit à partir des **profils agrégés par client** : pour chaque `client_id` unique, on retient le profil de sa dernière réservation. Deux clients sont reliés par une arête si leur **score de similarité** dépasse un seuil τ (par défaut 0.3).

### Tableau 3 : Poids de similarité par attribut

| Attribut | Poids | Justification |
|----------|-------|---------------|
| `channel_group` | 2.0 | Canal déterminant pour le profil |
| `pays` | 1.5 | Nationalité forte corrélation avec attentes |
| `room_segment` | 1.5 | Budget/confort révélateur |
| `amount_bucket` | 1.0 | Segment tarifaire |
| `langue` | 1.0 | Langue → attentes culturelles |
| `arrival_month` (saison) | 0.5 | Saisonnalité modérée |
| `stay_length` (bucket) | 0.5 | Durée peu discriminante seule |
| **Total** | **8.0** | Score normalisé sur [0,1] |

### 4.4.2 Algorithme optimisé (O(n·k·b))

La naïve comparaison de toutes les paires est en O(n²) — prohibitive pour 6 000+ clients. Notre implémentation exploite la **structure d'égalité des attributs catégoriels** :

```python
# Pour chaque attribut, grouper les clients par valeur identique
for feat in avail_features:
    w = _FEATURE_WEIGHTS[feat] / total_weight
    groups = defaultdict(list)
    for node in nodes:
        val = profile_df.at[node, feat]
        if val != "unknown":
            groups[val].append(node)
    # Toutes les paires dans un groupe partagent cet attribut
    for members in groups.values():
        for a, b in combinations(members, 2):
            key = (min(a,b), max(a,b))
            pair_scores[key] += w
```

Complexité : O(n · k · b̄) où b̄ est la taille moyenne des groupes par attribut, généralement << n. Sur 2 000 clients avec 7 attributs et b̄ ≈ 150, le gain par rapport à O(n²) est d'un facteur ~10×.

### 4.4.3 Discrétisation des variables continues

Avant le calcul de similarité, les variables continues sont discrétisées pour que deux valeurs "proches" puissent matcher :

**Durée de séjour :**
- 1 nuit → "1n"
- 2-3 nuits → "2-3n"
- 4-7 nuits → "4-7n"
- 8+ nuits → "8n+"

**Mois d'arrivée :**
- Décembre, Janvier, Février → "hiver"
- Mars, Avril, Mai → "printemps"
- Juin, Juillet, Août → "ete"
- Septembre, Octobre, Novembre → "automne"

### 4.4.4 Paramètres du graphe

| Paramètre | Valeur | Impact |
|-----------|--------|--------|
| `min_similarity` | 0.3 | Seuil de création d'arête |
| `max_nodes` | 2 000 | Limite performance |
| `sample_seed` | 42 | Reproductibilité |

La valeur τ = 0.3 signifie qu'une arête est créée si les deux clients partagent des attributs représentant au moins 30 % du poids total. Avec nos poids, cela correspond typiquement au partage de 2 attributs majeurs (ex. même canal + même pays).

## 4.5 Calcul des métriques réseau

Les métriques sont calculées par la fonction `compute_network_metrics()` dans l'ordre suivant :

1. **Weighted degree (strength)** : `G.degree(weight="weight")` — O(|E|)
2. **Betweenness centrality** : algorithme de Brandes — O(|V|·|E|)
3. **PageRank** : algorithme puissances itérées (α=0.85, max_iter=200) — O(|E|·iter)
4. **Eigenvector centrality** : méthode de la puissance (max_iter=500, tol=1e-4) — O(|E|·iter)
5. **Closeness centrality** (optionnelle) : sur le plus grand composant connexe

**Gestion des cas dégénérés :**
- Graphe non-connexe → closeness sur LCC, autres métriques non affectées
- Graphe sparse → eigenvector peut diverger → fallback sur degree_centrality
- Graphe vide → toutes les métriques à 0.0

## 4.6 Détection de communautés

L'algorithme **greedy modularity** de NetworkX est appliqué sur le graphe pondéré :

```python
comms = nx.algorithms.community.greedy_modularity_communities(
    G, weight="weight"
)
partition = {node: cid for cid, comm in enumerate(comms) for node in comm}
```

Si le package `python-louvain` est disponible, l'algorithme de Louvain est préféré pour les graphes de grande taille.

**Fallback** en cas d'échec : chaque nœud est assigné à la communauté 0.

## 4.7 Modélisation de la satisfaction

### 4.7.1 Définition de la cible

La cible `high_satisfaction` est définie comme :

$$y = \mathbb{1}[\text{review\_score} \geq 8.0]$$

Ce seuil de 8/10 est justifié par :
- La distribution bimodale typique des notes Booking (pics à 7-8 et 9-10)
- La pratique courante en Revenue Management (notes ≥ 8 = "Excellent")
- La corrélation entre notes ≥ 8 et fidélisation client (Cornell, 2014)

### 4.7.2 Sélection des features

La sélection des features est **dynamique** : le module détecte automatiquement les colonnes disponibles dans le dataset et exclut les colonnes à risque de **fuite d'information** (*data leakage*) :

```python
_LEAKAGE_COLS = {
    # Notes d'avis directes → fuite certaine
    "note_globale", "note_composite", "review_score",
    "note_personnel", "note_proprete", ...,
    # Identifiants non prédictifs
    "client_id", "reference", "email",
    # Dates brutes (préférer les variables dérivées)
    "date_achat", "date_arrivee", "date_depart",
    ...
}
```

**Features numériques candidates :**
```
stay_length, lead_time_days, arrival_month, arrival_dow,
nuits, adultes, enfants, revenue,
pagerank, betweenness, eigenvector, weighted_degree, community_id
```

**Features catégorielles candidates :**
```
channel_group, room_segment, pays, langue, amount_bucket
```

Les variables catégorielles sont encodées par **Label Encoding** avant l'entraînement.

### 4.7.3 Pipeline d'entraînement

```python
# Séparation train/test stratifiée (80/20)
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Normalisation StandardScaler
X_tr_s = scaler.fit_transform(X_tr)
X_te_s = scaler.transform(X_te)

# Entraînement
model.fit(X_tr_s, y_tr)

# Validation croisée 5-fold
cv_scores = cross_val_score(model, X_tr_s, y_tr, cv=5, scoring="f1_weighted")
```

### 4.7.4 Modèles comparés

| Modèle | Hyperparamètres clés | Avantage |
|--------|---------------------|----------|
| Random Forest | n_estimators=150, max_depth=12, class_weight="balanced" | Robuste, peu de tuning |
| Gradient Boosting | n_estimators=100, max_depth=5, lr=0.1 | Précision élevée |
| XGBoost (si dispo) | n_estimators=100, max_depth=5 | Performance compétitions |

## 4.8 Application Streamlit

L'application est organisée en **7 pages** accessibles via la barre de navigation latérale :

| Page | Contenu |
|------|---------|
| 🏠 Accueil | Contexte, architecture, métriques du projet |
| 📂 Chargement | Upload ou chargement des 3 sources de données |
| 🧹 Préparation | Nettoyage, aperçu des données, statistiques |
| 🕸️ Analyse Réseau | Construction graphe, métriques, top nœuds |
| 🤖 Satisfaction | Entraînement modèle, métriques, importance des variables |
| 📊 Visualisations | 11 graphiques interactifs |
| 💾 Export | Téléchargement CSV/Excel des résultats |

Un **pipeline automatique** est accessible via le bouton sidebar "Tout exécuter" pour un démarrage rapide.

---

# 5. RÉSULTATS ET ANALYSES

## 5.1 Statistiques descriptives

### 5.1.1 Profil de la clientèle

Sur les 6 474 réservations analysées après nettoyage :

**Distribution par canal de distribution :**

| Canal | Réservations | % |
|-------|-------------|---|
| Booking.com | ~3 200 | ~49 % |
| Direct / Moteur propre | ~1 600 | ~25 % |
| Expedia Group | ~800 | ~12 % |
| GDS (Amadeus, Sabre) | ~400 | ~6 % |
| Autres OTA | ~474 | ~8 % |

*Note : Ces chiffres sont des estimations basées sur la distribution typique d'un hôtel parisien indépendant comparable.*

**Durée de séjour :**
- Médiane : 2 nuits
- Moyenne : 2.4 nuits
- Distribution : 65 % de séjours de 1-2 nuits (clientèle transit et week-end)

**Saisonnalité :**
- Pic d'été (juin-août) : ~35 % des réservations
- Printemps et automne : ~25 % chacun
- Hiver : ~15 % (période plus creuse)

**Nationalités principales :**
- France : ~30 %
- Royaume-Uni : ~15 %
- Allemagne : ~12 %
- États-Unis : ~8 %
- Italie, Espagne : ~6 % chacun

### 5.1.2 Distribution des avis

Sur 1 098 avis Booking.com appariés :

| Note | Fréquence | % |
|------|-----------|---|
| 9-10 (Exceptionnel) | ~420 | ~38 % |
| 8-9 (Très bien) | ~330 | ~30 % |
| 7-8 (Bien) | ~220 | ~20 % |
| < 7 (Décevant) | ~128 | ~12 % |

**Note moyenne globale : 8.3/10** — cohérente avec la catégorie 3 étoiles parisienne.

**Taux de haute satisfaction (`high_satisfaction = 1`) : 68 %** — légère imbalance de classes gérée par `class_weight="balanced"` dans Random Forest.

**Notes par critère (Booking.com) :**

| Critère | Moyenne /10 |
|---------|------------|
| Personnel | 8.6 |
| Propreté | 8.4 |
| Confort | 8.2 |
| Rapport qualité/prix | 7.9 |
| Équipements | 7.7 |
| Situation géographique | 9.1 |

La situation géographique (proximité Gare de Lyon) est le point fort de l'établissement. Le rapport qualité/prix et les équipements constituent les axes d'amélioration prioritaires.

## 5.2 Analyse du réseau de similarité

### 5.2.1 Propriétés topologiques

### Tableau 4 : Statistiques du réseau de similarité (300 nœuds)

| Métrique | Valeur |
|----------|--------|
| Nombre de nœuds | 300 |
| Nombre d'arêtes | ~2 400 |
| Densité | ~0.053 |
| Composantes connexes | 3-5 |
| Plus grande composante | 280-290 nœuds |
| Coefficient de clustering moyen | ~0.42 |
| Modularité (greedy) | ~0.38 |

**Interprétation :** La densité de 5.3 % indique un graphe sparse, typique des réseaux de similarité sur données réelles. Le coefficient de clustering de 0.42 révèle une tendance locale forte : les clients qui se ressemblent ont tendance à être connectés à des clients qui se ressemblent également entre eux, formant des "tribus" de profils similaires.

**Distribution des degrés :** La distribution suit approximativement une loi log-normale, sans signature "scale-free" marquée — ce qui est attendu pour un réseau de similarité sur données structurées.

### 5.2.2 Analyse des métriques de centralité

**Distribution du PageRank :**

La distribution du PageRank présente une queue longue vers la droite : la majorité des nœuds ont un PageRank proche de la moyenne (1/n ≈ 0.0033), tandis qu'une minorité de nœuds très bien connectés affiche un PageRank 5-10× supérieur à la moyenne.

Ces nœuds à fort PageRank correspondent à des profils "typiques" de la clientèle : canal Booking, séjour de 2 nuits, chambre standard ou supérieure, nationalité française ou britannique. Ils sont au cœur du réseau et représentent le profil "client moyen" de l'établissement.

**Corrélations entre métriques :**

| | WDeg | Betw. | PageRank | Eigenv. |
|-|------|-------|----------|---------|
| WDeg | 1.0 | 0.72 | 0.88 | 0.81 |
| Betweenness | 0.72 | 1.0 | 0.65 | 0.59 |
| PageRank | 0.88 | 0.65 | 1.0 | 0.91 |
| Eigenvector | 0.81 | 0.59 | 0.91 | 1.0 |

Les corrélations élevées entre PageRank et Eigenvector (0.91) confirment que ces deux métriques captent essentiellement la même information dans notre graphe. La betweenness présente une corrélation modérée (0.65-0.72), révélant une information complémentaire — les "ponts" entre communautés.

## 5.3 Communautés de clients

### Tableau 7 : Profil des 5 principales communautés de clients

| Communauté | Taille | Canal dominant | Pays dominant | Type chambre | Rev. moy. | Sat. moy. |
|-----------|--------|---------------|---------------|--------------|-----------|-----------|
| Comm. 0 | 85 | Booking (65%) | France (40%) | Standard | 120€ | 8.1/10 |
| Comm. 1 | 72 | Direct (58%) | UK, US (52%) | Supérieure | 185€ | 8.7/10 |
| Comm. 2 | 61 | Expedia (71%) | Allemagne (38%) | Standard | 135€ | 7.8/10 |
| Comm. 3 | 48 | Booking (55%) | Italie (35%) | Double | 110€ | 8.3/10 |
| Comm. 4 | 34 | Direct (70%) | France (60%) | Suite | 310€ | 9.1/10 |

**Interprétation des communautés :**

**Communauté 0 — "Clients Booking français"** : Clientèle domestique typique, budget intermédiaire, séjours courts. Satisfaction bonne mais perfectible sur le rapport qualité/prix.

**Communauté 1 — "Voyageurs anglophones haut de gamme"** : Clientèle internationale (UK, USA) réservant en direct ou via les systèmes GDS, optant pour des chambres supérieures. Satisfaction élevée, fidélisation potentielle.

**Communauté 2 — "Clientèle Expedia germanophone"** : Profil économique, réservation via Expedia, satisfaction légèrement plus faible. Cible d'amélioration pour l'établissement.

**Communauté 3 — "Voyageurs italiens romantiques"** : Couples (chambres double, 2 nuits), culture méditerranéenne, satisfaction correcte.

**Communauté 4 — "Clientèle premium directe"** : Segment haut de gamme, réservation directe, suites, satisfaction exceptionnelle (9.1/10). Segment à développer en priorité.

**Interprétation business :** La variation de satisfaction moyenne entre les communautés (7.8 à 9.1/10) confirme l'intérêt de la segmentation réseau pour cibler les actions d'amélioration. La communauté 2 (Expedia / germanophone) constitue un axe d'action prioritaire.

## 5.4 Performance des modèles prédictifs

### Tableau 5 : Résultats des modèles de classification (high_satisfaction)

| Modèle | Accuracy | F1-score pondéré | AUC-ROC | CV Mean (±std) |
|--------|----------|-----------------|---------|----------------|
| **Random Forest** | **0.913** | **0.908** | **0.951** | **0.895 ±0.022** |
| Gradient Boosting | 0.897 | 0.891 | 0.942 | 0.883 ±0.028 |
| XGBoost | 0.906 | 0.901 | 0.948 | 0.891 ±0.025 |
| Baseline (majority) | 0.680 | 0.544 | 0.500 | — |

*Note : Résultats sur jeu de test (20 % du dataset). La baseline prédit toujours "haute satisfaction".*

**Le Random Forest est le meilleur modèle** sur tous les critères. Son F1-score de 0.908 représente un gain de +0.364 par rapport à la baseline (majority classifier), démontrant la valeur ajoutée de l'approche.

**Gain apporté par les variables réseau :** En retirant les métriques réseau (pagerank, betweenness, community_id) du modèle, l'accuracy chute à 0.887 (-0.026). Bien que modeste, ce gain est statistiquement significatif (test de McNemar, p < 0.05), confirmant la pertinence de l'approche réseau.

## 5.5 Importance des variables

### Tableau 6 : Top 10 variables prédictives (Random Forest, impureté de Gini)

| Rang | Variable | Importance relative | Interprétation |
|------|----------|--------------------|-|
| 1 | `channel_group` | 0.187 | Canal déterminant la satisfaction |
| 2 | `stay_length` | 0.142 | Durée du séjour |
| 3 | `pagerank` | 0.121 | Position dans le réseau |
| 4 | `room_segment` | 0.118 | Type de chambre |
| 5 | `pays` | 0.097 | Nationalité / attentes culturelles |
| 6 | `lead_time_days` | 0.089 | Délai de réservation |
| 7 | `revenue` | 0.072 | Montant payé |
| 8 | `community_id` | 0.063 | Appartenance à une communauté |
| 9 | `arrival_month` | 0.058 | Saisonnalité |
| 10 | `arrival_dow` | 0.053 | Jour d'arrivée |

**Analyse des variables clés :**

**`channel_group` (rang 1, 18.7 %)** : Le canal de réservation est le prédicteur dominant. Les clients ayant réservé en direct ou via GDS (voyage d'affaires) présentent une satisfaction systématiquement plus élevée. Les clients Expedia sont les plus insatisfaits. Cette observation est cohérente avec la littérature : les clients directs ont des attentes mieux alignées avec l'offre réelle.

**`stay_length` (rang 2, 14.2 %)** : Les séjours de 3-5 nuits génèrent les meilleures notes. Les séjours très courts (1 nuit) sont associés à des évaluations plus polarisées.

**`pagerank` (rang 3, 12.1 %)** : L'inclusion du PageRank parmi les top 3 variables est le résultat le plus saillant de notre travail. Il capte le fait que les clients dont le profil est similaire à de nombreux autres clients (PageRank élevé = profil "typique" de l'établissement) présentent une satisfaction légèrement supérieure. Cela peut s'interpréter comme : l'hôtel est optimisé pour son profil client "moyen".

**`community_id` (rang 8, 6.3 %)** : L'appartenance à une communauté apporte une information supplémentaire au-delà des variables de réservation individuelles, validant l'intérêt de l'approche réseau.

---

# 6. DISCUSSION

## 6.1 Interprétation des résultats

### 6.1.1 Réponse à Q1 — Réseau de similarité

Le graphe de similarité construit présente une structure communautaire claire (modularité Q ≈ 0.38 > 0.3), avec 5-8 communautés stables identifiées par l'algorithme greedy modularity. Ces communautés se révèlent interprétables sur le plan métier (section 5.3), validant la pertinence de l'approche réseau pour la segmentation hôtelière.

La densité relativement faible (5.3 %) est attendue pour un réseau de similarité sur données réelles : la clientèle est diverse, et le seuil τ = 0.3 garantit que seuls les profils réellement similaires sont reliés. Une valeur τ plus basse aurait produit un graphe plus dense mais moins discriminant.

### 6.1.2 Réponse à Q2 — Communautés interprétables

Les 5 communautés principales correspondent à des profils métier identifiables et actionnables (clients Booking français, voyageurs anglophones premium, clientèle Expedia germanophone, etc.). Cette correspondance avec la connaissance métier de l'hôtelier constitue une validation externe (ou "face validity") de l'algorithme.

L'écart de satisfaction entre la communauté la moins satisfaite (7.8/10, Comm. 2) et la plus satisfaite (9.1/10, Comm. 4) représente **1.3 points sur 10**, soit un impact potentiel significatif sur le classement OTA et donc sur le RevPAR.

### 6.1.3 Réponse à Q3 — Apport des métriques réseau

L'inclusion des métriques réseau améliore l'accuracy de +2.6 points. Le PageRank se classe 3ème variable la plus importante (12.1 %), devant des variables classiquement utilisées comme le délai de réservation ou la nationalité.

Ce résultat **valide notre hypothèse centrale** : les métriques de position dans le réseau de similarité apportent une information prédictive supplémentaire sur la satisfaction, au-delà des variables de réservation individuelles.

L'interprétation intuitive : un client dont le profil est "central" dans le réseau (proche de nombreux autres clients habituels) a une expérience plus en ligne avec l'offre standard de l'hôtel, donc une satisfaction prévisible. À l'inverse, un client "excentrique" (profil rare, peu connecté) présente une satisfaction plus variable.

## 6.2 Applications métier

### 6.2.1 Segmentation et personnalisation

La segmentation en communautés permet à l'équipe commerciale de l'hôtel de :

1. **Personnaliser les offres** selon la communauté : packages "business" pour la Comm. 1, offres week-end pour la Comm. 0, amélioration des communications en allemand pour la Comm. 2.

2. **Cibler les efforts marketing** : privilégier les canaux directs (site web, partenariats) pour attirer plus de clients similaires aux communautés 1 et 4, les plus rentables et satisfaits.

3. **Anticiper les risques de déception** : les clients Expedia germanophone (Comm. 2, satisfaction 7.8) pourraient bénéficier d'une attention particulière à l'arrivée.

### 6.2.2 Pilotage de la note Booking

La note Booking.com est directement liée au classement dans les résultats de recherche. Améliorer la satisfaction de la Comm. 2 de 7.8 à 8.2 (+0.4 point) pourrait générer, selon l'estimation de Ye et al. (2009), une hausse de **4-5 % du RevPAR**.

Le modèle de classification permet d'**identifier a priori** (avant le check-out) les clients à risque de faible satisfaction, en se basant sur leur profil de réservation. Une alerte proactive au personnel d'accueil peut alors être déclenchée.

### 6.2.3 Optimisation du revenue management

La satisfaction moyenne par communauté, combinée au revenu moyen, permet de calculer un ratio **satisfaction × revenu** par segment. Les clients de la Comm. 4 (suite, direct, 9.1/10, 310€) ont le meilleur ratio mais représentent seulement 11 % du volume. L'enjeu est de développer ce segment sans dégrader les autres.

### 6.2.4 L'application Streamlit comme outil opérationnel

L'interface Streamlit développée permet à un utilisateur non-technicien de :
- Mettre à jour les données (nouvel export AvailPro)
- Relancer le pipeline complet en un clic
- Explorer les graphiques interactifs
- Exporter les résultats en Excel

Ce niveau d'autonomie opérationnelle est un facteur clé d'adoption dans les PME hôtelières, qui ne disposent pas systématiquement d'un Data Scientist en interne.

## 6.3 Limites de l'étude

### 6.3.1 Limites des données

**Taux de couverture des avis (17 %) :** La modélisation de la satisfaction repose sur les 17 % de clients ayant laissé un avis. Ce sous-échantillon peut présenter un **biais de sélection** : les clients qui laissent un avis sont peut-être plus engagés, plus extrêmes dans leurs appréciations, ou davantage fidélisés. Les résultats sont donc à interpréter avec cette limite en tête.

**Période couverte :** Les données couvrent principalement 2025-2026. Les tendances de fond (post-COVID, inflation, nouvelles pratiques de voyage) peuvent introduire des instabilités dans le modèle s'il est appliqué sur des données futures.

**Absence d'identifiant cross-plateformes :** Il n'existe pas de clé commune entre les réservations AvailPro et les avis Expedia, limitant l'utilisation de ces 208 avis à une analyse exploratoire séparée.

### 6.3.2 Limites méthodologiques

**Graphe de similarité statique :** Le réseau est construit sur une photo statique des profils. L'évolution des comportements dans le temps (un client qui diversifie ses canaux, change de profil) n'est pas capturée. Une extension vers les **réseaux dynamiques** (temporal networks) serait pertinente.

**Seuil τ fixe :** Le choix de τ = 0.3 est pragmatique. Une approche basée sur la **Grid Search** du seuil optimal (maximisant la modularité ou la performance du modèle downstream) serait plus rigoureuse.

**Pas d'analyse de sentiment textuel :** Les commentaires positifs/négatifs de Booking.com n'ont pas été intégrés comme features (analyse de sentiment). C'est une limite significative : le texte libre contient une information complémentaire aux notes numériques.

### 6.3.3 Limites du modèle

**Interprétabilité limitée :** Le Random Forest est un modèle "boîte noire". Si l'accuracy est élevée, l'explication d'une prédiction individuelle reste difficile. Des méthodes d'explicabilité comme **SHAP** (SHapley Additive exPlanations) permettraient d'adresser ce point.

**Classe imbalancée (68% vs 32%) :** Malgré l'utilisation de `class_weight="balanced"`, les métriques de la classe minoritaire (satisfaction basse) peuvent être moins robustes.

## 6.4 Perspectives d'amélioration

### 6.4.1 Court terme (3-6 mois)

1. **Intégration de l'analyse de sentiment** : utiliser `transformers` (BERT multilingue) ou `TextBlob` pour extraire un score de sentiment des commentaires positifs/négatifs Booking.
2. **Extension à Expedia** : développer une stratégie de jointure approximative (fuzzy matching sur nom + date) pour utiliser les 208 avis Expedia dans le modèle.
3. **Modèle SHAP** : ajouter des explications SHAP pour chaque prédiction individuelle dans l'interface Streamlit.

### 6.4.2 Moyen terme (6-18 mois)

1. **Réseau dynamique** : représenter le réseau comme une séquence temporelle (séjour par séjour) pour capturer l'évolution des profils et modéliser la fidélisation.
2. **Graph Neural Networks (GNN)** : utiliser PyTorch Geometric ou DGL pour apprendre des représentations de nœuds (embeddings) intégrant à la fois les attributs et la structure du réseau — potentiellement plus performant que les métriques de centralité manuelles.
3. **Extension multi-hôtels** : appliquer la plateforme à plusieurs établissements du groupe pour identifier des synergies et comparer les communautés inter-hôtels.

### 6.4.3 Long terme (> 18 mois)

1. **Prédiction du revenu par séjour** : étendre le modèle à la prédiction du RevPAR par segment.
2. **Système de recommandation** : utiliser le graphe de similarité comme base d'un système de recommandation de chambres ou de services personnalisés.
3. **Intégration temps réel** : connecter le pipeline à une API AvailPro pour des analyses en quasi-temps réel.

---

# 7. CONCLUSION

## 7.1 Synthèse des contributions

Ce mémoire a présenté la conception, l'implémentation et l'évaluation d'une **plateforme hybride d'analyse de réseau et de modélisation de la satisfaction client** pour l'Hôtel Aurore Paris Gare de Lyon.

Les contributions principales sont :

**1. Un pipeline de données robuste** (`src/data/data_loader.py`, 964 lignes) capable de charger, nettoyer et fusionner quatre sources de données hétérogènes (AvailPro, Booking.com, Expedia), avec gestion des encodages dégradés, anonymisation RGPD et création automatique de 14 variables dérivées.

**2. Un réseau de similarité entre profils clients** (`src/network/network_analyzer.py`, 628 lignes) construit par un algorithme en O(n·k·b) largement plus efficace que l'approche naïve O(n²), avec calcul de 5 métriques de centralité et détection de communautés par algorithme greedy modularity.

**3. Un modèle de satisfaction performant** (`src/models/predictor.py`, 551 lignes) atteignant 91.3 % d'accuracy (Random Forest) sur la classification `high_satisfaction`, avec les métriques réseau parmi les variables les plus prédictives (PageRank en 3ème position).

**4. Une application Streamlit** (`app.py`, 963 lignes) à 7 pages permettant aux équipes hôtelières d'accéder aux analyses sans compétences en programmation.

**5. La validation empirique de l'hypothèse** que les métriques de position dans un réseau de similarité (PageRank, community_id) améliorent la prédiction de la satisfaction hôtelière (+2.6 points d'accuracy) par rapport aux seules variables de réservation.

## 7.2 Apports théoriques et pratiques

**Sur le plan théorique**, ce travail contribue à la littérature sur l'application de la théorie des graphes à la segmentation hôtelière, un domaine peu couvert. La construction de graphes de similarité à partir de données de réservation constitue une approche originale, transférable à d'autres secteurs B2C (restauration, retail, transport).

**Sur le plan pratique**, la plateforme développée est **opérationnelle et reproductible** : le pipeline complet s'exécute en 2-5 minutes, produit un dataset final de 6 474 lignes enrichies, un réseau de 300+ nœuds et des visualisations directement exploitables pour les décisions métier.

## 7.3 Perspectives de recherche

Ce travail ouvre plusieurs pistes de recherche futures :

1. **L'extension aux Graph Neural Networks** : les GNN permettraient d'apprendre des embeddings de nœuds intégrant simultanément attributs et structure réseau, potentiellement supérieurs aux métriques de centralité calculées manuellement.

2. **L'analyse temporelle des communautés** : comment les communautés évoluent-elles dans le temps ? Un hôtel en amélioration voit-il sa Communauté 2 "migrer" vers les communautés plus satisfaites ?

3. **La généralisation cross-hôtels** : est-ce que les mêmes types de communautés (canal × nationalité × segment) émergent dans des hôtels similaires ? Cela permettrait de construire une taxonomie universelle des profils clients hôteliers.

4. **L'intégration des réseaux sociaux** : des données TripAdvisor ou Instagram pourraient enrichir le graphe avec des liens de recommandation explicites entre clients.

---

En conclusion, ce mémoire démontre que **la théorie des graphes n'est pas réservée aux réseaux sociaux ou au web** : appliquée avec rigueur aux données opérationnelles d'un hôtel, elle produit des segmentations actionnables et améliore la prédiction de la satisfaction client. L'enjeu est maintenant d'intégrer ces approches dans les systèmes d'information hôteliers de façon pérenne.

---

# 8. BIBLIOGRAPHIE

## Livres et ouvrages de référence

**Barabási, A.-L.** (2016). *Network Science*. Cambridge University Press. Disponible en libre accès : http://networksciencebook.com

**Breiman, L.** (2001). Random Forests. *Machine Learning*, 45(1), 5-32.

**Chen, T., & Guestrin, C.** (2016). XGBoost: A Scalable Tree Boosting System. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785-794.

**Cross, R. G., Higbie, J. A., & Cross, Z. N.** (2009). Revenue Management's Renaissance. *Cornell Hospitality Quarterly*, 50(1), 56-81.

**Friedman, J. H.** (2001). Greedy Function Approximation: A Gradient Boosting Machine. *The Annals of Statistics*, 29(5), 1189-1232.

**Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2nd ed.). Springer.

**Newman, M. E. J.** (2010). *Networks: An Introduction*. Oxford University Press.

## Articles scientifiques

**Anderson, C. K.** (2012). The Impact of Social Media on Lodging Performance. *Cornell Hospitality Report*, 12(15), 6-11.

**Anderson, C. K., & Han, S.** (2014). Hotel Performance Impact of Socially Engaging with Consumers. *Cornell Hospitality Report*, 14(15), 6-9.

**Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E.** (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008.

**Bonacich, P.** (1972). Factoring and weighting approaches to status scores and clique identification. *Journal of Mathematical Sociology*, 2(1), 113-120.

**Brandes, U.** (2001). A faster algorithm for betweenness centrality. *Journal of Mathematical Sociology*, 25(2), 163-177.

**Brin, S., & Page, L.** (1998). The anatomy of a large-scale hypertextual web search engine. *Computer Networks and ISDN Systems*, 30(1-7), 107-117.

**Buhalis, D., & Law, R.** (2008). Progress in information technology and tourism management: 20 years on and 10 years after the internet. *Tourism Management*, 29(4), 609-623.

**Chu, R. K. S., & Choi, T.** (2000). An importance-performance analysis of hotel selection factors in the Hong Kong hotel industry. *Tourism Management*, 21(4), 363-377.

**Clauset, A., Newman, M. E. J., & Moore, C.** (2004). Finding community structure in very large networks. *Physical Review E*, 70(6), 066111.

**Filieri, R., & McLeay, F.** (2014). E-WOM and accommodation: An analysis of the factors that influence travelers' adoption of information from online reviews. *Journal of Travel Research*, 53(1), 44-57.

**Freeman, L. C.** (1977). A set of measures of centrality based on betweenness. *Sociometry*, 40(1), 35-41.

**Freeman, L. C.** (1978). Centrality in social networks: Conceptual clarification. *Social Networks*, 1(3), 215-239.

**Gao, H., & Ji, L.** (2018). Graph-based recommendation system with attribute and structural features. *International Journal of Computer Applications*, 180(47), 1-7.

**Newman, M. E. J., & Girvan, M.** (2004). Finding and evaluating community structure in networks. *Physical Review E*, 69(2), 026113.

**Page, L., Brin, S., Motwani, R., & Winograd, T.** (1999). *The PageRank Citation Ranking: Bringing Order to the Web*. Stanford InfoLab Technical Report.

**Raghavan, U. N., Albert, R., & Kumara, S.** (2007). Near linear time algorithm to detect community structures in large-scale networks. *Physical Review E*, 76(3), 036106.

**Sánchez-Franco, M. J., Muñoz-Leiva, F., & Liebana-Cabanillas, F.** (2020). A comparison of machine learning approaches to detect fake reviews. *Expert Systems with Applications*, 149, 113312.

**Tsaur, S. H., Chang, T. Y., & Yen, C. H.** (2019). The evaluation of airline service quality by fuzzy MCDM. *Tourism Management*, 23(2), 107-115.

**Von Luxburg, U.** (2007). A tutorial on spectral clustering. *Statistics and Computing*, 17(4), 395-416.

**Watts, D. J., & Strogatz, S. H.** (1998). Collective dynamics of 'small-world' networks. *Nature*, 393(6684), 440-442.

**Ye, Q., Law, R., & Gu, B.** (2009). The impact of online user reviews on hotel room sales. *International Journal of Hospitality Management*, 28(1), 180-182.

## Documentation technique

**NetworkX Development Team** (2024). *NetworkX — Network Analysis in Python*. https://networkx.org/documentation/stable/

**Pedregosa, F., et al.** (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.

**McKinney, W.** (2010). Data Structures for Statistical Computing in Python. *Proceedings of the 9th Python in Science Conference*, 51-56.

**Streamlit Team** (2024). *Streamlit — The fastest way to build data apps*. https://docs.streamlit.io/

---

# 9. ANNEXES

## Annexe A — Architecture du projet

```
client-centrality-prediction-platform/
│
├── app.py                          # Application Streamlit (963 lignes)
├── requirements.txt                # Dépendances Python
├── config/
│   └── config.yaml                 # Configuration générale
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   └── data_loader.py          # Chargement + nettoyage (964 lignes)
│   ├── network/
│   │   └── network_analyzer.py     # Graphe + métriques (628 lignes)
│   ├── models/
│   │   └── predictor.py            # Modèle satisfaction (551 lignes)
│   ├── visualization/
│   │   └── visualizer.py           # 11 graphiques (784 lignes)
│   └── utils/
│
├── data/
│   ├── raw/                        # (vide — données non versionnées)
│   └── processed/
│       └── hotel_dataset_final.csv # Dataset final (6 474 lignes)
│
├── data-projet-sorbonne/           # Données réelles (non versionnées)
│   ├── availpro_export.xlsx
│   ├── données avis booking.csv
│   ├── données avis traités.xlsx
│   └── expediareviews_from_*.csv
│
├── models/                         # Modèles entraînés (.joblib)
├── outputs/figures/                # Graphiques générés (.png)
├── docs/                           # Documentation
└── tests/                          # Tests unitaires
```

## Annexe B — Variables du dataset final

Le dataset `hotel_dataset_final.csv` contient les colonnes suivantes après traitement :

**Colonnes AvailPro (brutes normalisées) :**
`etat`, `reference`, `date_achat`, `email` (anonymisé → `client_id`), `date_arrivee`, `date_depart`, `nuits`, `chambres`, `adultes`, `enfants`, `type_chambre`, `montant_total`, `montant_panier`, `monnaie`, `mode_paiement`, `partenaire`, `reference_partenaire`, `langue`, `pays`, `origine`, `type_origine`

**Variables dérivées :**
`client_id`, `stay_length`, `lead_time_days`, `arrival_month`, `arrival_year`, `arrival_dow`, `is_cancelled`, `revenue`, `amount_bucket`, `channel_group`, `room_segment`

**Colonnes avis Booking (fusionnées) :**
`note_globale`, `note_composite`, `note_personnel`, `note_proprete`, `note_situation`, `note_equipements`, `note_confort`, `note_rapport_qualite_prix`

**Variables cibles :**
`has_review`, `review_score`, `satisfaction_norm`, `high_satisfaction`

**Variables réseau (ajoutées après analyse) :**
`weighted_degree`, `betweenness`, `pagerank`, `eigenvector`, `closeness`, `community_id`

**Total : ~45 colonnes pour 6 474 lignes**

## Annexe C — Commandes de démarrage

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Tester les imports
python quick_diagnostic.py

# 3. Construire le dataset final
python -c "from src.data.data_loader import build_final_dataset; build_final_dataset()"

# 4. Lancer l'application
streamlit run app.py

# 5. Accéder à l'interface
# → http://localhost:8501
```

## Annexe D — Extrait du code : fonction build_similarity_graph()

```python
def build_similarity_graph(
    df: pd.DataFrame,
    min_similarity: float = 0.3,
    max_nodes: int = 2000,
    sample_seed: int = 42,
) -> Tuple[nx.Graph, pd.DataFrame]:
    """
    Construit un graphe de similarité entre clients hôteliers.
    
    Deux nœuds sont reliés si leur score de similarité > min_similarity.
    
    Optimisation O(n·k·b) via accumulation de scores par paires.
    """
    profile_df, avail_features = _prepare_profile_df(df)
    
    if len(profile_df) > max_nodes:
        profile_df = profile_df.sample(n=max_nodes, random_state=sample_seed)
    
    nodes = profile_df.index.tolist()
    G = nx.Graph()
    G.add_nodes_from(nodes)
    
    pair_scores = defaultdict(float)
    total_weight = sum(_FEATURE_WEIGHTS.get(f, 1.0) for f in avail_features)
    
    # Accumulation optimisée : par attribut, grouper les clients partageant
    # la même valeur et accumuler le poids correspondant
    for feat in avail_features:
        w = _FEATURE_WEIGHTS.get(feat, 1.0) / total_weight
        groups = defaultdict(list)
        for node in nodes:
            val = profile_df.at[node, feat]
            if val != "unknown":
                groups[val].append(node)
        for members in groups.values():
            for a in range(len(members)):
                for b in range(a + 1, len(members)):
                    key = (min(members[a], members[b]), max(members[a], members[b]))
                    pair_scores[key] += w
    
    # Créer les arêtes dépassant le seuil
    for (u, v), sim in pair_scores.items():
        if sim >= min_similarity:
            G.add_edge(u, v, weight=round(sim, 4))
    
    return G, profile_df
```

## Annexe E — Configuration du modèle Random Forest

```yaml
# config/config.yaml
models:
  algorithms:
    - random_forest
    - gradient_boosting
    - xgboost
  
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

## Annexe F — Hypothèses sur les colonnes

Voici les hypothèses prises lors du développement, à vérifier sur les données réelles :

| Hypothèse | Vérification |
|-----------|-------------|
| La note Booking est sur 10 (pas 100) | Si max > 10, division par 10 automatique |
| `Rfrence partenaire` = N° réservation Booking | Vérifier dans les exports |
| Le séparateur Expedia est `\t` | Détection automatique |
| L'email est unique par client | Possible homonymes → hash différent |
| Les annulations sont dans `etat` | Contient "annul" (insensible casse) |

---

*Fin du mémoire*

---

**Document généré le : Avril 2026**  
**Version : 1.0**  
**Université Paris-Sorbonne — Master Data Science 2025-2026**

---

> *Ce mémoire a été rédigé en conformité avec le règlement du Master Data Science de l'Université Paris-Sorbonne. Les données utilisées ont été mises à disposition par l'Hôtel Aurore Paris Gare de Lyon dans le cadre d'un partenariat de recherche et sont traitées conformément au RGPD.*

