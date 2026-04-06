# NOTE DE SYNTHÈSE

---

**DU Sorbonne Data Analytics — Promotion 2025-2026**
**Université Paris-Sorbonne**

---

**Stagiaire :** [Votre Nom Prénom]
**Structure d'accueil :** Hôtel Aurore Paris Gare de Lyon
**Période :** [Dates du stage]
**Date :** Avril 2026

---

## ANALYSE RÉSEAU ET PRÉDICTION DE LA SATISFACTION CLIENT
### Hôtel Aurore Paris Gare de Lyon

---

## 1. Contexte et enjeux de la mission

L'Hôtel Aurore Paris Gare de Lyon, établissement indépendant 3 étoiles du 12ème arrondissement de Paris, réalise plus de 90 % de ses réservations via deux plateformes OTA — Expedia Group (54,1 %) et Booking.com (36,2 %). Cette dépendance génère des commissions importantes (15-25 % par réservation) et crée une asymétrie d'information défavorable : les plateformes exploitent les données clients bien mieux que l'hôtel lui-même.

Parallèlement, l'établissement dispose d'un historique riche de données opérationnelles (réservations, avis, profils clients) qui restaient jusqu'ici inexploitées. La mission de stage visait à transformer cette ressource en un outil concret d'aide à la décision, en mobilisant les techniques de **data science**, d'**analyse de réseau** et de **Machine Learning**.

---

## 2. Travaux réalisés

### 2.1 Construction du pipeline de données

Trois sources hétérogènes ont été intégrées :
- **6 474 réservations AvailPro** (Excel, 56 colonnes, encodage Latin-1 dégradé) ;
- **1 634 avis Booking.com** (CSV brut, 14 colonnes) ;
- **208 avis Expedia** (CSV tabulé, format de note textuel "8 out of 10").

Un pipeline Python modulaire a été développé pour :
- charger et normaliser les données malgré leurs imperfections (mapping tolérant, gestion des encodages) ;
- anonymiser les données personnelles par hachage SHA-256 (conformité RGPD) ;
- créer 14 variables dérivées métier (durée de séjour, délai de réservation, canal regroupé, etc.) ;
- apparier les avis aux réservations via clé partenaire → **316 paires exploitables** (4,9 % du volume).

### 2.2 Analyse réseau

Un **graphe de similarité** a été construit entre profils clients : deux clients sont reliés si leurs caractéristiques (canal, pays, type de chambre, langue, durée, montant) partagent un score de similarité pondéré supérieur à 0,3. Sur 300 nœuds échantillonnés, le graphe présente :
- **~31 298 arêtes**, densité ~0,70 ;
- **2 communautés** correspondant aux canaux OTA dominants (Expedia vs Booking) ;
- **modularité Q ≈ 0,205** (structure communautaire modeste, cohérente avec l'homogénéité de la clientèle) ;
- 5 métriques de centralité calculées (betweenness, PageRank, eigenvector, closeness, degré pondéré).

### 2.3 Modélisation de la satisfaction

La satisfaction est modélisée comme une classification binaire (haute satisfaction = note ≥ 8/10). Le modèle **Random Forest** atteint une **AUC-ROC de 0,914-0,918** (CV 5-fold : 0,915 ± 0,013), confirmant une performance excellente sur un problème fortement déséquilibré (2,9 % de positifs à l'échelle du dataset complet).

Les **variables les plus prédictives** sont le canal de distribution (32,9 %), la nationalité (22,9 %) et le statut d'annulation (13,5 %). Ces résultats indiquent que la satisfaction est largement conditionnée par les attentes initiales du client — déterminées avant son arrivée — plutôt que par les seuls attributs du séjour.

### 2.4 Déploiement de l'application

Une application **Streamlit à 8 pages** a été déployée, incluant un module original de **"Scoring Nouveau Client"** : la réception peut saisir les caractéristiques d'une réservation à venir et obtenir instantanément un score de satisfaction prédit, un message d'accueil professionnel prérédigé et un positionnement par rapport aux moyennes historiques.

---

## 3. Résultats clés

| Indicateur | Valeur |
|-----------|--------|
| Réservations analysées | 6 474 |
| Avis appariés | 316 (4,9 %) |
| Note moyenne observée | **7,58 / 10** |
| Taux haute satisfaction | **59,5 %** (parmi les avisés) |
| AUC-ROC Random Forest | **0,914 – 0,918** |
| CV 5-fold | **0,915 ± 0,013** |
| 1ère variable prédictive | canal (32,9 %) |
| 2ème variable prédictive | nationalité (22,9 %) |

---

## 4. Préconisations

**Court terme — immédiat :**
- Intégrer l'outil de scoring dans la procédure quotidienne de la réception pour anticiper les arrivées à risque ;
- Former les équipes à la lecture et l'utilisation des indicateurs Streamlit.

**Moyen terme — 3-6 mois :**
- Améliorer le taux d'appariement avis-réservations (cible : 15-20 %) par une meilleure configuration AvailPro et une politique de sollicitation post-séjour ;
- Développer la communication interculturelle personnalisée selon les 5 nationalités dominantes.

**Stratégique — 6-12 mois :**
- Développer le canal direct (objectif : 5-10 % des réservations) pour réduire la dépendance OTA ;
- Viser l'amélioration de la note moyenne de 7,58/10 à 8,0/10 (impact estimé : +4,7 % RevPAR selon la littérature).

---

## 5. Apports du stage

Ce stage a permis de mettre en œuvre un **projet data science end-to-end** dans un contexte professionnel réel : de l'intégration de données hétérogènes au déploiement d'un outil opérationnel, en passant par l'analyse de réseau et la modélisation Machine Learning. L'application des compétences acquises dans le DU SDA (Python, NetworkX, scikit-learn, Streamlit) à des données réelles, avec leurs imperfections et leurs contraintes métier, a constitué un enrichissement majeur.

La valeur ajoutée du stage pour l'établissement est concrète et immédiatement exploitable : un pipeline documenté, une application déployée, et une feuille de route chiffrée pour l'amélioration de la satisfaction client.

---

*Note de synthèse — DU Sorbonne Data Analytics 2025-2026*
*Université Paris-Sorbonne — Avril 2026*

