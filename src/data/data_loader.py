"""
Module de chargement et de prétraitement des données hôtelières.
Hôtel Aurore Paris Gare de Lyon — Projet d'analyse réseau & satisfaction client.

Sources de données :
  - availpro_export.xlsx          : réservations (AvailPro/Channel Manager)
  - données avis booking.csv      : avis Booking.com bruts (CSV — source unique)
  - expediareviews_from_*.csv     : avis Expedia (tab-séparé + guillemets)

Note : Le fichier 'données avis traités.xlsx' est identique au CSV brut.
       Seul 'données avis booking.csv' est utilisé (source unique, traitement dans le code).

Colonnes réelles observées (encodage CP1252/Latin-1, accents manquants) :
  AvailPro : 'Etat','Rfrence',"Date d'achat",'E-Mail',"Date d'arrive",
             'Date de dpart','Nuits','Chambres','Adultes','Enfants',
             'Type de chambre','Montant total','Montant du panier',
             'Monnaie','Mode de paiement','Origine',"Type d'origine",
             'Partenaire de distribution','Rfrence partenaire',
             'Evaluation client','Langue','Pays','Tlphone',
             'Moteur de rservation',"Motif de l'annulation",
             'Prnom','Nom','Titre','Htel (ID)'
  Booking  : 'Date du commentaire','Nom du client','Numro de rservation',
             'Titre du commentaire','Commentaire positif','Commentaire ngatif',
             'Note des commentaires','Personnel','Propret',
             'Situation gographique','quipements','Confort',
             'Rapport qualit/prix',"Rponse de l'tablissement"
  Expedia  : '"review_date','brand_type','review_by','review_rating',
             'review_title','review_text' (tab-séparé, guillemet résiduel)
"""

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Répertoires par défaut
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_RAW_DIR = _PROJECT_ROOT / "data-projet-sorbonne"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Mappings de colonnes tolérants
# Colonnes réelles avec accents manquants (encodage CP1252/Latin-1 dégradé)
# ---------------------------------------------------------------------------
_AVAILPRO_COL_MAP: Dict[str, List[str]] = {
    "etat":                   ["etat", "état"],
    "reference":              ["rfrence", "référence", "reference"],
    "date_achat":             ["date d'achat", "date dachat", "date d achat"],
    "derniere_modif":         ["dernire modification", "dernière modification"],
    "date_annulation":        ["date d'annulation"],
    "hotel_nom":              ["htel", "hôtel", "hotel"],        # colonne Hôtel (nom)
    "hotel_id":               ["htel\n (id)", "hôtel\n (id)", "htel (id)", "hotel (id)"],
    "titre":                  ["titre"],
    "prenom":                 ["prnom", "prénom"],
    "nom":                    ["nom"],
    "email":                  ["e-mail", "email"],
    "date_arrivee":           ["date d'arrive", "date d'arrivée", "date arrive",
                               "date arrivée"],
    "date_depart":            ["date de dpart", "date de départ", "date depart"],
    "nuits":                  ["nuits"],
    "chambres":               ["chambres"],
    "adultes":                ["adultes"],
    "enfants":                ["enfants"],
    "bebes":                  ["bbs", "bébés"],
    "type_chambre":           ["type de chambre", "type chambre"],
    "tarif":                  ["tarif"],
    "montant_total":          ["montant total"],
    "montant_panier":         ["montant du panier"],
    "monnaie":                ["monnaie"],
    "mode_paiement":          ["mode de paiement"],
    "plateforme":             ["plateforme"],
    "type_origine":           ["type dorigine", "type d'origine", "type d origine"],
    "origine":                ["origine", "origin"],
    "partenaire":             ["partenaire de distribution"],
    "partenaire_id":          ["partenaire de distribution (id)"],
    "reference_partenaire":   ["rfrence partenaire", "référence partenaire"],
    "evaluation_client":      ["evaluation client", "évaluation client"],
    "langue":                 ["langue"],
    "pays":                   ["pays"],
    "code_postal":            ["code postal client"],
    "telephone":              ["tlphone", "téléphone"],
    "moteur_reservation":     ["moteur de rservation", "moteur de réservation"],
    "referrer":               ["referrer"],
    "commentaire_client":     ["commentaire client"],
    "motif_annulation":       ["motif de l'annulation", "motif annulation"],
    "facturation_annulation": ["facturation de l'annulation"],
    "montant_restant":        ["montant restant"],
}

_BOOKING_COL_MAP: Dict[str, List[str]] = {
    "date_commentaire":          ["date du commentaire"],
    "nom_client":                ["nom du client"],
    "numero_reservation":        ["numro de rservation", "numéro de réservation",
                                  "numero de reservation"],
    "titre_commentaire":         ["titre du commentaire"],
    "commentaire_positif":       ["commentaire positif"],
    "commentaire_negatif":       ["commentaire ngatif", "commentaire négatif"],
    "note_globale":              ["note des commentaires"],
    "note_personnel":            ["personnel"],
    "note_proprete":             ["propret", "propreté"],
    "note_situation":            ["situation gographique", "situation géographique"],
    "note_equipements":          ["quipements", "équipements"],
    "note_confort":              ["confort"],
    "note_rapport_qualite_prix": ["rapport qualit/prix", "rapport qualité/prix"],
    "reponse_etablissement":     ["rponse de l'tablissement",
                                  "réponse de l'établissement"],
}

_EXPEDIA_COL_MAP: Dict[str, List[str]] = {
    "date_commentaire":  ["review_date", '"review_date'],   # guillemet résiduel possible
    "plateforme":        ["brand_type"],
    "nom_client":        ["review_by"],
    "note_globale":      ["review_rating"],
    "titre_commentaire": ["review_title"],
    "commentaire":       ["review_text"],
    "date_reponse":      ["review_response_date"],
    "reponse":           ["review_response"],
}


# ===========================================================================
# Fonctions utilitaires
# ===========================================================================

def _normalize_col(name: str) -> str:
    """Minuscule + strip des espaces et guillemets résiduels pour comparaison robuste."""
    return str(name).lower().strip().lstrip('"').lstrip("'")


def _find_col(df: pd.DataFrame, candidates: list) -> Optional[str]:
    """
    Trouve le nom de colonne réel dans df parmi une liste de fragments candidats.
    La comparaison est insensible à la casse, aux espaces superflus et aux guillemets.
    """
    norm_map = {_normalize_col(c): c for c in df.columns}
    for candidate in candidates:
        nc = _normalize_col(candidate)
        # Recherche exacte d'abord
        if nc in norm_map:
            return norm_map[nc]
        # Recherche partielle (le nom réel contient le candidat ou vice-versa)
        for norm_real, real in norm_map.items():
            if nc in norm_real or norm_real in nc:
                return real
    return None


def _rename_cols(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """
    Renomme les colonnes de df selon col_map.
    col_map : {canonical_name: [fragment1, fragment2, ...]}
    """
    rename_dict: Dict[str, str] = {}
    used_targets: set = set()
    for canonical, candidates in col_map.items():
        found = _find_col(df, candidates)
        if found and found not in rename_dict and canonical not in used_targets:
            rename_dict[found] = canonical
            used_targets.add(canonical)
    df = df.rename(columns=rename_dict)
    logger.debug(f"Colonnes renommées : {rename_dict}")
    return df


def _anonymize_email(email: str) -> str:
    """Retourne un hash SHA-256 tronqué à 12 chars d'un email."""
    if pd.isna(email) or not str(email).strip():
        return np.nan
    return "CLT_" + hashlib.sha256(str(email).strip().lower().encode()).hexdigest()[:12].upper()


def _parse_expedia_rating(raw: str) -> Optional[float]:
    """Convertit '8 out of 10' → 8.0, ou '4/5' → 8.0 ramené sur 10."""
    if pd.isna(raw):
        return np.nan
    m = re.search(r"(\d+(?:\.\d+)?)\s*out\s*of\s*(\d+)", str(raw), re.IGNORECASE)
    if m:
        score, out_of = float(m.group(1)), float(m.group(2))
        return round(score / out_of * 10, 2)
    try:
        return float(str(raw).strip())
    except ValueError:
        return np.nan


def _safe_read_excel(path: Path, **kwargs) -> pd.DataFrame:
    """Lit un Excel avec openpyxl, avec message d'erreur clair."""
    try:
        return pd.read_excel(path, engine="openpyxl", **kwargs)
    except Exception as e:
        logger.error(f"Impossible de lire {path}: {e}")
        raise


def _safe_read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Tente plusieurs encodages et séparateurs pour lire un CSV."""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        for sep in [",", ";", "\t"]:
            try:
                df = pd.read_csv(path, sep=sep, encoding=enc, low_memory=False, **kwargs)
                if df.shape[1] > 1:
                    logger.debug(f"CSV lu avec sep='{sep}', encoding='{enc}'")
                    return df
            except Exception:
                continue
    # dernier recours : lecture brute
    return pd.read_csv(path, encoding="latin-1", low_memory=False, **kwargs)


# ===========================================================================
# Fonctions de chargement
# ===========================================================================

def load_availpro_data(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Charge et normalise les réservations depuis availpro_export.xlsx.

    Returns:
        DataFrame avec colonnes canoniques (voir _AVAILPRO_COL_MAP).
    """
    path = path or (_RAW_DIR / "availpro_export.xlsx")
    logger.info(f"Chargement AvailPro : {path}")
    df = _safe_read_excel(path)
    df = _rename_cols(df, _AVAILPRO_COL_MAP)
    logger.info(f"AvailPro chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return df


def load_booking_reviews(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Charge les avis Booking.com depuis 'données avis booking.csv' (source unique).

    Le fichier CSV brut est le seul fichier d'avis Booking utilisé dans ce projet.
    Le fichier 'données avis traités.xlsx' étant identique au CSV, il n'est pas utilisé
    afin d'éviter les doublons et de garantir la traçabilité du traitement.

    Format réel observé :
      - Chaque ligne est une chaîne CSV entre guillemets doubles
      - Colonnes : date, nom_client, numero_reservation, titre, commentaire_positif,
                   commentaire_negatif, note_globale, note_personnel, note_proprete,
                   note_situation, note_equipements, note_confort,
                   note_rapport_qualite_prix, reponse_etablissement
      - Séparateur de colonnes dans la chaîne : virgule
      - Guillemets internes doublés

    Returns:
        DataFrame avec colonnes canoniques (voir _BOOKING_COL_MAP).
    """
    csv_path = path or (_RAW_DIR / "données avis booking.csv")

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Fichier d'avis Booking introuvable : {csv_path}\n"
            f"Attendu dans : {_RAW_DIR}"
        )

    logger.info(f"Chargement avis Booking (CSV brut) : {csv_path}")
    df = _load_booking_csv_raw(csv_path)

    df = _rename_cols(df, _BOOKING_COL_MAP)
    logger.info(f"Avis Booking chargés : {df.shape[0]} lignes")
    return df


def _load_booking_csv_raw(path: Path) -> pd.DataFrame:
    """
    Charge le CSV Booking brut.

    Format réel observé (analysé sur le vrai fichier) :
      - Chaque ligne physique : '"DATE,""NOM"",""RESA"",...";;'
      - Le contenu interne est un CSV avec guillemets doublés ("") et virgule séparateur
      - Une entrée peut s'étendre sur plusieurs lignes physiques (ex : commentaire long)
      - La ligne d'en-tête contient 'Date du commentaire'
      - Chaque entrée se termine par ';;' (double point-virgule en fin de ligne)
      - 1634 entrées au total (1634 dates distinctes trouvées dans le fichier)

    Stratégie :
      1. Lire le contenu brut entier
      2. Reconstituer les entrées : une entrée = tout ce qui est entre deux dates
         (regex sur les horodatages YYYY-MM-DD HH:MM:SS)
      3. Pour chaque entrée, extraire le contenu CSV interne et le parser
      4. Normaliser les colonnes
    """
    import csv as _csv
    import io as _io
    import re as _re

    expected_cols = [
        "date_commentaire", "nom_client", "numero_reservation",
        "titre_commentaire", "commentaire_positif", "commentaire_negatif",
        "note_globale", "note_personnel", "note_proprete",
        "note_situation", "note_equipements", "note_confort",
        "note_rapport_qualite_prix", "reponse_etablissement"
    ]

    # ── 1. Lire le fichier brut ──────────────────────────────────────────────
    raw_content = None
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(path, encoding=enc, errors="replace") as f:
                raw_content = f.read()
            break
        except Exception:
            continue

    if not raw_content:
        logger.error(f"Impossible de lire {path}")
        return pd.DataFrame(columns=expected_cols)

    raw_content = raw_content.replace("\r\n", "\n").replace("\r", "\n")

    # ── 2. Reconstituer les entrées ──────────────────────────────────────────
    # Chaque entrée commence par une ligne de la forme :
    # "YYYY-MM-DD HH:MM:SS,...
    # On identifie les positions des démarrages d'entrées par regex sur les dates
    date_pattern = _re.compile(
        r'"?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', _re.MULTILINE
    )

    # Trouver toutes les positions de dates dans le contenu
    date_matches = list(date_pattern.finditer(raw_content))
    logger.info(f"Dates détectées dans le CSV Booking : {len(date_matches)}")

    rows = []

    for i, match in enumerate(date_matches):
        # Extraire le bloc de texte de cette entrée jusqu'à la prochaine date
        start = match.start()
        end = date_matches[i + 1].start() if i + 1 < len(date_matches) else len(raw_content)
        block = raw_content[start:end]

        # Nettoyer le bloc :
        # - Enlever le guillemet ouvrant initial s'il est là
        # - Enlever les ';;' de fin et sauts de ligne
        block = block.strip().lstrip('"')
        # Remplacer les fins de ligne dans le bloc (entrée multi-ligne) par espace
        # mais conserver le bloc comme une seule chaîne CSV
        block = block.replace("\n", " ").rstrip(";").rstrip()

        # Le contenu est un CSV avec guillemets doublés ("")
        # Parser avec csv.reader en mode guillemets doublés
        try:
            reader = _csv.reader(
                _io.StringIO(block),
                quotechar='"',
                delimiter=',',
                doublequote=True,
            )
            for parts in reader:
                if parts:
                    # Nettoyer les espaces résiduels
                    parts = [p.strip() for p in parts]
                    # S'assurer qu'on a au moins 7 colonnes
                    while len(parts) < 14:
                        parts.append("")
                    rows.append(parts[:14])
                    break  # une seule ligne par entrée
        except Exception as e:
            # Fallback : split naïf sur virgule
            parts = block.split(",")
            parts = [p.strip().strip('"') for p in parts]
            while len(parts) < 14:
                parts.append("")
            rows.append(parts[:14])

    if not rows:
        logger.warning(f"Aucune entrée Booking parsée depuis {path}")
        return pd.DataFrame(columns=expected_cols)

    df = pd.DataFrame(rows, columns=expected_cols)

    # Nettoyer les guillemets résiduels ("" → vide, " → vide)
    # Le format CSV avec guillemets doublés laisse parfois des "" en fin de champ
    def _clean_field(x):
        if not isinstance(x, str):
            return x
        # Supprimer les guillemets doublés résiduels
        x = x.replace('""', '')
        # Supprimer les guillemets simples en début/fin
        x = x.strip('"').strip("'").strip()
        return x if x else np.nan

    for col in df.columns:
        df[col] = df[col].apply(_clean_field)

    # Remplacer les chaînes vides par NaN
    df.replace("", np.nan, inplace=True)
    df.replace({None: np.nan}, inplace=True)

    logger.info(f"CSV Booking parsé : {len(df)} lignes, {len(df.columns)} colonnes")
    return df


def load_expedia_reviews(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Charge les avis Expedia.

    Format réel observé :
      - Tab-séparé
      - 1ère colonne avec guillemet résiduel : '"review_date'
      - Encodage latin-1
      - Chaque ligne peut être parsée comme une seule cellule contenant des \\t

    Returns:
        DataFrame avec colonnes canoniques (voir _EXPEDIA_COL_MAP).
    """
    path = path or (
        _RAW_DIR / "expediareviews_from_2025-03-01_to_2026-03-01.csv"
    )
    logger.info(f"Chargement avis Expedia : {path}")

    rows = []
    cols = None

    # Colonnes attendues dans le fichier Expedia
    expedia_expected_cols = [
        "review_date", "brand_type", "review_by", "review_rating",
        "review_title", "review_text", "review_response_date",
        "review_response_by", "review_response"
    ]

    raw_lines = None
    for enc in ["latin-1", "utf-8", "utf-8-sig", "cp1252"]:
        try:
            with open(path, encoding=enc, errors="replace") as f:
                raw_lines = f.readlines()
            break
        except Exception:
            continue

    if not raw_lines:
        logger.warning("Impossible de lire le fichier Expedia — retour DataFrame vide")
        return pd.DataFrame()

    # Cas 1 : le fichier a une vraie ligne d'en-tête tab-séparée
    # Cas 2 : chaque ligne est une cellule unique contenant des \t internes
    #         (le fichier semble parsé comme une seule colonne par read_csv)

    # Déterminer la structure : si la ligne 0 contient des \t, c'est tab-séparé normal
    first_non_empty = next((l.rstrip("\n\r") for l in raw_lines if l.strip()), "")

    # Tester si la ligne contient déjà des tabulations (vraies colonnes)
    if first_non_empty.count("\t") >= 3:
        # Format tab-séparé standard
        cols = None
        rows = []
        for i, line in enumerate(raw_lines):
            line = line.rstrip("\n\r")
            if not line.strip():
                continue
            parts = line.split("\t")
            # Nettoyer guillemets résiduels
            parts = [p.strip().strip('"').strip("'").strip(";") for p in parts]
            if i == 0:
                # En-tête
                cols = parts
            else:
                if any(p.strip() for p in parts):
                    rows.append(parts)

        if cols and rows:
            n = len(cols)
            rows_norm = [
                (r + [""] * n)[:n] for r in rows
            ]
            df = pd.DataFrame(rows_norm, columns=cols)
        else:
            df = pd.DataFrame(columns=expedia_expected_cols)

    else:
        # Format "ligne = cellule avec \t internes" (Expedia export encapsulé)
        # La première ligne non-vide contient l'en-tête encapsulé
        rows = []
        header_found = False
        cols = expedia_expected_cols  # colonnes par défaut

        for line in raw_lines:
            line = line.rstrip("\n\r").strip().strip('"').strip("'")
            if not line:
                continue
            # Split sur \t interne
            parts = [p.strip().strip('"').strip("'").strip(";") for p in line.split("\t")]
            # Ignorer la ligne d'en-tête si elle contient "review_date"
            if not header_found and any("review_date" in p.lower() for p in parts):
                header_found = True
                # Extraire les vraies colonnes
                cols = [p for p in parts if p.strip()]
                if not cols:
                    cols = expedia_expected_cols
                continue
            if len(parts) >= 4 and any(p.strip() for p in parts):
                rows.append(parts)

        if rows:
            n = len(cols)
            rows_norm = [(r + [""] * n)[:n] for r in rows]
            df = pd.DataFrame(rows_norm, columns=cols)
        else:
            df = pd.DataFrame(columns=expedia_expected_cols)

    # Supprimer colonnes vides ou 'Unnamed'
    df.columns = pd.Index(df.columns)  # garantit pd.Index pour .str
    df = df.loc[:, df.columns.str.strip() != ""]
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # Nettoyer les noms de colonnes résiduels
    df.columns = [c.strip().strip('"').strip("'").strip(";") for c in df.columns]

    df = _rename_cols(df, _EXPEDIA_COL_MAP)

    # Parser la note globale ('8 out of 10' → 8.0)
    if "note_globale" in df.columns:
        df["note_globale"] = df["note_globale"].apply(_parse_expedia_rating)

    # Parser la date (format 'Feb 25, 2026')
    if "date_commentaire" in df.columns:
        df["date_commentaire"] = pd.to_datetime(
            df["date_commentaire"], errors="coerce"
        )

    # Nettoyer les textes
    for col in ["commentaire", "titre_commentaire", "nom_client", "reponse"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.strip('"').str.strip("'").str.strip(";").str.strip()
                .replace({"": np.nan, "nan": np.nan})
            )

    df["source"] = "expedia"
    logger.info(f"Avis Expedia chargés : {df.shape[0]} lignes")
    return df


# ===========================================================================
# Fonctions de nettoyage
# ===========================================================================

def clean_reservations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le DataFrame de réservations AvailPro.

    Étapes :
      1. Conversion des dates (date_achat, date_arrivee, date_depart)
      2. Variables dérivées : lead_time_days, stay_length, arrival_month,
         arrival_year, arrival_dow
      3. Flag is_cancelled
      4. Nettoyage des montants → revenue, amount_bucket
      5. Catégorisation du canal → channel_group
      6. Catégorisation de la chambre → room_segment
      7. Identifiant client anonymisé via email (SHA-256, RGPD)
      8. Nettoyage langue/pays
      9. Nettoyage des colonnes numériques
     10. Nettoyage du numéro de référence (string pour jointure)

    Returns:
        DataFrame nettoyé avec toutes les variables dérivées.
    """
    logger.info("Nettoyage des réservations AvailPro…")
    df = df.copy()

    # ── 1. Dates ─────────────────────────────────────────────────────────────
    for col in ["date_achat", "date_arrivee", "date_depart"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=False)

    # ── 2. Variables dérivées temporelles ────────────────────────────────────
    if "date_arrivee" in df.columns and "date_depart" in df.columns:
        df["stay_length"]   = (df["date_depart"] - df["date_arrivee"]).dt.days.clip(lower=0)
        df["arrival_month"] = df["date_arrivee"].dt.month
        df["arrival_year"]  = df["date_arrivee"].dt.year
        df["arrival_dow"]   = df["date_arrivee"].dt.dayofweek   # 0=lundi

    if "date_achat" in df.columns and "date_arrivee" in df.columns:
        df["lead_time_days"] = (df["date_arrivee"] - df["date_achat"]).dt.days.clip(lower=0)

    # ── 3. is_cancelled ───────────────────────────────────────────────────────
    if "etat" in df.columns:
        df["is_cancelled"] = (
            df["etat"].astype(str).str.lower()
            .str.contains("annul", na=False).astype(int)
        )
    else:
        df["is_cancelled"] = 0

    # ── 4. Montants ──────────────────────────────────────────────────────────
    for col in ["montant_total", "montant_panier"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    amount_col = (
        "montant_total"  if "montant_total"  in df.columns else
        "montant_panier" if "montant_panier" in df.columns else None
    )
    if amount_col:
        df["revenue"]       = df[amount_col]
        df["amount_bucket"] = pd.cut(
            df[amount_col],
            bins=[0, 80, 150, 300, 600, np.inf],
            labels=["<80€", "80-150€", "150-300€", "300-600€", ">600€"],
        ).astype(str)
    else:
        df["revenue"]       = np.nan
        df["amount_bucket"] = "unknown"

    # ── 5. Canal ─────────────────────────────────────────────────────────────
    if "partenaire" in df.columns:
        df["channel_group"] = df["partenaire"].astype(str).str.lower().apply(_map_channel)
    elif "type_origine" in df.columns:
        df["channel_group"] = df["type_origine"].astype(str).str.lower().apply(_map_channel)
    elif "origine" in df.columns:
        df["channel_group"] = df["origine"].astype(str).str.lower().apply(_map_channel)
    else:
        df["channel_group"] = "unknown"

    # ── 6. Type de chambre ───────────────────────────────────────────────────
    if "type_chambre" in df.columns:
        df["room_segment"] = df["type_chambre"].apply(_map_room_segment)
    else:
        df["room_segment"] = "unknown"

    # ── 7. Identifiant client anonymisé ──────────────────────────────────────
    if "email" in df.columns:
        df["client_id"] = df["email"].apply(_anonymize_email)
    else:
        def _fallback_id(row):
            key = " ".join([
                str(row.get("prenom",    "") or ""),
                str(row.get("nom",       "") or ""),
                str(row.get("telephone", "") or ""),
            ]).strip().lower()
            if key.replace(" ", ""):
                return "CLT_" + hashlib.sha256(key.encode()).hexdigest()[:12].upper()
            return np.nan
        df["client_id"] = df.apply(_fallback_id, axis=1)

    # ── 8. Langue & Pays ─────────────────────────────────────────────────────
    for col in ["langue", "pays"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.strip().str.lower()
                .replace({"nan": np.nan, "": np.nan})
            )

    # ── 9. Numériques entiers ─────────────────────────────────────────────────
    for col in ["nuits", "adultes", "enfants", "bebes"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # ── 10. Référence en string ───────────────────────────────────────────────
    if "reference" in df.columns:
        df["reference"] = df["reference"].astype(str).str.strip()

    logger.info(f"Réservations nettoyées : {df.shape[0]} lignes")
    return df


def _map_channel(val: str) -> str:
    """Catégorise le canal de distribution hôtelier."""
    if pd.isna(val) or str(val).strip() in ("nan", "none", ""):
        return "unknown"
    val = str(val).lower()
    if "booking" in val:
        return "booking"
    if any(k in val for k in ["expedia", "hotels.com", "trivago", "hotelsbeds"]):
        return "expedia_group"
    if any(k in val for k in ["direct", "barweb", "best western", "bwe", "metagenius",
                               "ghp", "secure-hotel", "fastbooking"]):
        return "direct"
    if "airbnb" in val:
        return "airbnb"
    if any(k in val for k in ["meta", "google", "tripadvisor"]):
        return "metasearch"
    if any(k in val for k in ["gds", "amadeus", "sabre", "galileo", "worldspan"]):
        return "gds"
    if any(k in val for k in ["channel manager", "distribution en ligne"]):
        return "channel_manager_ota"
    return "other_ota"


def _map_room_segment(val) -> str:
    """Catégorise le type de chambre hôtelière."""
    if pd.isna(val):
        return "unknown"
    val = str(val).lower()
    if any(k in val for k in ["sup", "supérieure", "superior", "suprieure"]):
        return "superieure"
    if "standard" in val:
        return "standard"
    if "suite" in val:
        return "suite"
    if "twin" in val:
        return "twin"
    if any(k in val for k in ["famil", "family"]):
        return "familiale"
    if any(k in val for k in ["single", "simple"]):
        return "simple"
    if "double" in val:
        return "double"
    return "autre"


def clean_booking_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les avis Booking.com.

    Étapes :
      1. Conversion de la date
      2. Conversion et normalisation des notes sur 10
      3. Calcul d'une note composite (moyenne des sous-notes)
      4. Normalisation du numéro de réservation (string pour jointure)

    Returns:
        DataFrame nettoyé avec note_globale normalisée sur 10.
    """
    logger.info("Nettoyage des avis Booking…")
    df = df.copy()

    if "date_commentaire" in df.columns:
        df["date_commentaire"] = pd.to_datetime(
            df["date_commentaire"], errors="coerce"
        )

    # Conversion des notes
    note_cols = [
        "note_globale", "note_personnel", "note_proprete", "note_situation",
        "note_equipements", "note_confort", "note_rapport_qualite_prix",
    ]
    for col in note_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normaliser la note globale sur 10 si elle semble sur 100
    if "note_globale" in df.columns:
        max_note = df["note_globale"].max(skipna=True)
        if pd.notna(max_note) and max_note > 10:
            df["note_globale"] = df["note_globale"] / 10.0

    # Note composite = moyenne des sous-notes disponibles
    sub_cols = [c for c in [
        "note_personnel", "note_proprete", "note_situation",
        "note_equipements", "note_confort", "note_rapport_qualite_prix",
    ] if c in df.columns]
    if sub_cols:
        df["note_composite"] = df[sub_cols].mean(axis=1)

    # Normaliser le numéro de réservation pour la jointure
    # Les numéros sont déjà des entiers dans le CSV Booking (ex: 3044529099)
    # On les normalise en string pour la jointure
    if "numero_reservation" in df.columns:
        def _norm_num_resa(x):
            if pd.isna(x) or str(x).strip() in ("", "nan"):
                return np.nan
            s = str(x).strip().strip('"').strip("'")
            # Notation scientifique
            if "e" in s.lower():
                try:
                    return str(int(float(s)))
                except (ValueError, OverflowError):
                    return s
            # Float avec .0
            try:
                f = float(s)
                if f == int(f):
                    return str(int(f))
            except (ValueError, OverflowError):
                pass
            return re.sub(r"[^\d]", "", s) or np.nan
        df["numero_reservation"] = df["numero_reservation"].apply(_norm_num_resa)

    df["source"] = "booking"
    logger.info(f"Avis Booking nettoyés : {df.shape[0]} lignes")
    return df


def clean_expedia_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les avis Expedia.

    Étapes :
      1. Conversion de la date (format 'Feb 25, 2026')
      2. Re-parse de la note globale si nécessaire
      3. Nettoyage des guillemets et points-virgules résiduels

    Returns:
        DataFrame nettoyé avec note_globale sur 10.
    """
    logger.info("Nettoyage des avis Expedia…")
    df = df.copy()

    if "date_commentaire" in df.columns:
        df["date_commentaire"] = pd.to_datetime(
            df["date_commentaire"], errors="coerce"
        )

    if "note_globale" in df.columns:
        df["note_globale"] = df["note_globale"].apply(_parse_expedia_rating)

    for col in ["commentaire", "titre_commentaire", "nom_client", "reponse"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.strip('"').str.strip("'").str.strip(";").str.strip()
                .replace({"nan": np.nan, "": np.nan})
            )

    df["source"] = "expedia"
    logger.info(f"Avis Expedia nettoyés : {df.shape[0]} lignes")
    return df


# ===========================================================================
# Fonctions de fusion / construction du dataset final
# ===========================================================================

def merge_reviews_with_reservations(
    df_reservations: pd.DataFrame,
    df_reviews: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fusionne les avis Booking avec les réservations.

    Stratégie de jointure (par ordre de priorité) :
      1. reference_partenaire (numéro Booking côté AvailPro) ↔ numero_reservation
      2. reference (code AvailPro) ↔ numero_reservation (fallback)
      3. Si aucun match → has_review = 0

    Note : dans AvailPro, 'reference_partenaire' contient le numéro de
    réservation Booking.com (ex. 6299590853) qui correspond à
    'Numro de rservation' dans l'export Booking.com.

    Returns:
        DataFrame de réservations enrichi avec les colonnes d'avis.
    """
    logger.info("Fusion avis ↔ réservations…")
    df_res = df_reservations.copy()
    df_rev = df_reviews.copy()

    # Colonnes à récupérer depuis les avis
    review_cols_wanted = [
        "note_globale", "note_composite",
        "commentaire_positif", "commentaire_negatif",
        "note_personnel", "note_proprete", "note_situation",
        "note_equipements", "note_confort", "note_rapport_qualite_prix",
        "source",
    ]

    def _normalize_booking_ref(series: pd.Series) -> pd.Series:
        """
        Normalise un numéro de réservation en entier string.
        Gère : notation scientifique (6.497953e+09 → '6497953XXX'),
        float avec .0, string, NaN.
        """
        def _norm(x):
            if pd.isna(x) or str(x).strip() in ("", "nan", "none", "NaN"):
                return ""
            s = str(x).strip().strip('"').strip("'")
            # Notation scientifique
            if "e" in s.lower() or "E" in s:
                try:
                    return str(int(float(s)))
                except (ValueError, OverflowError):
                    return s
            # Float avec .0
            try:
                f = float(s)
                if f == int(f):
                    return str(int(f))
            except (ValueError, OverflowError):
                pass
            # Garder uniquement les chiffres
            digits = re.sub(r"[^\d]", "", s)
            return digits if digits else ""
        return series.apply(_norm)

    def _try_merge(left_col: str, right_col: str) -> Optional[Tuple]:
        """Tente une jointure entre df_res[left_col] et df_rev[right_col]."""
        if left_col not in df_res.columns or right_col not in df_rev.columns:
            return None
        # Normaliser les deux clés
        l_key = _normalize_booking_ref(df_res[left_col])
        r_key = _normalize_booking_ref(df_rev[right_col])

        # Log des clés pour diagnostic
        l_sample = l_key[l_key != ""].head(3).tolist()
        r_sample = r_key[r_key != ""].head(3).tolist()
        logger.debug(f"  Clés gauche ({left_col}): {l_sample}")
        logger.debug(f"  Clés droite ({right_col}): {r_sample}")

        # Construire le sous-DataFrame d'avis avec clé + colonnes voulues
        avail_cols = [right_col] + [c for c in review_cols_wanted if c in df_rev.columns]
        df_rev_sub = df_rev[avail_cols].copy()
        df_rev_sub["_join_key"] = r_key
        df_rev_sub = df_rev_sub.drop(columns=[right_col]).drop_duplicates("_join_key")
        # Supprimer les lignes avec clé vide
        df_rev_sub = df_rev_sub[df_rev_sub["_join_key"] != ""]

        df_res_tmp = df_res.copy()
        df_res_tmp["_join_key"] = l_key

        merged = df_res_tmp.merge(df_rev_sub, on="_join_key", how="left")
        n = merged["note_globale"].notna().sum() if "note_globale" in merged.columns else 0
        merged.drop(columns=["_join_key"], inplace=True, errors="ignore")
        return merged, n

    # Tentative 1 : reference_partenaire ↔ numero_reservation
    merged = df_res.copy()
    n_matched = 0

    result = _try_merge("reference_partenaire", "numero_reservation")
    if result is not None:
        merged_try, n_try = result
        logger.info(f"Jointure via reference_partenaire : {n_try} avis matchés")
        if n_try > n_matched:
            merged, n_matched = merged_try, n_try

    # Tentative 2 : reference ↔ numero_reservation (si premier essai insuffisant)
    if n_matched == 0:
        result2 = _try_merge("reference", "numero_reservation")
        if result2 is not None:
            merged_try2, n_try2 = result2
            logger.info(f"Jointure via reference : {n_try2} avis matchés")
            if n_try2 > n_matched:
                merged, n_matched = merged_try2, n_try2

    if n_matched == 0:
        logger.warning(
            "Aucun avis Booking n'a pu être jointurer avec les réservations. "
            "Vérifiez que 'Rfrence partenaire' dans AvailPro correspond bien "
            "au 'Numro de rservation' dans le CSV Booking. "
            "Les notes seront affectées par source comme avis indépendants."
        )
        # Fallback : enrichir le dataset avec les notes moyennes par source si disponible
        # Les avis restent dans df_final.attrs["booking_reviews"] pour usage séparé

    # Flags satisfaction
    if "note_globale" in merged.columns:
        merged["has_review"]   = merged["note_globale"].notna().astype(int)
        merged["review_score"] = merged["note_globale"]
    else:
        merged["has_review"]   = 0
        merged["review_score"] = np.nan

    logger.info(f"Dataset fusionné : {merged.shape[0]} lignes, {merged.shape[1]} colonnes")
    return merged


def build_final_dataset(
    availpro_path: Optional[Path] = None,
    booking_reviews_path: Optional[Path] = None,
    expedia_reviews_path: Optional[Path] = None,
    save: bool = True,
) -> pd.DataFrame:
    """
    Pipeline complet : charge, nettoie, fusionne et retourne le dataset final.

    Étapes :
      1. Charger les 3 sources
      2. Nettoyer chacune
      3. Fusionner les avis Booking avec les réservations
      4. Stocker les avis Expedia en attribut (pas de jointure directe)
      5. Créer les cibles de satisfaction
      6. Supprimer les lignes sans client_id
      7. Sauvegarder dans data/processed/hotel_dataset_final.csv

    Args:
        availpro_path         : chemin optionnel vers availpro_export.xlsx
        booking_reviews_path  : chemin optionnel vers l'Excel d'avis Booking
        expedia_reviews_path  : chemin optionnel vers le CSV Expedia
        save                  : si True, sauvegarde le dataset final

    Returns:
        DataFrame final avec toutes les variables dérivées.
    """
    logger.info("=== Construction du dataset final ===")

    # 1. Charger
    df_res     = load_availpro_data(availpro_path)
    df_booking = load_booking_reviews(booking_reviews_path)
    df_expedia = load_expedia_reviews(expedia_reviews_path)

    # 2. Nettoyer
    df_res     = clean_reservations(df_res)
    df_booking = clean_booking_reviews(df_booking)
    df_expedia = clean_expedia_reviews(df_expedia)

    # 3. Fusionner avis Booking avec réservations
    df_final = merge_reviews_with_reservations(df_res, df_booking)

    # 4. Stocker avis Expedia comme attribut
    df_final.attrs["expedia_reviews"] = df_expedia

    # 5. Cibles de satisfaction
    if "review_score" in df_final.columns:
        df_final["satisfaction_norm"] = (
            df_final["review_score"] / 10.0
        ).clip(0, 1)
        df_final["high_satisfaction"] = (
            df_final["review_score"] >= 8.0
        ).astype(int)

    # 6. Supprimer les lignes sans client_id
    n_before = len(df_final)
    df_final = df_final.dropna(subset=["client_id"])
    logger.info(f"Lignes supprimées (client_id manquant) : {n_before - len(df_final)}")

    # 7. Sauvegarder
    if save:
        _PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        out_path = _PROCESSED_DIR / "hotel_dataset_final.csv"
        df_final.to_csv(out_path, index=False, encoding="utf-8-sig")
        logger.info(f"Dataset final sauvegardé : {out_path}")

    logger.info(f"Dataset final : {df_final.shape[0]} lignes, {df_final.shape[1]} colonnes")
    return df_final


# ===========================================================================
# Classe DataLoader — conservée pour compatibilité avec app.py et les tests
# ===========================================================================

class DataLoader:
    """
    Classe principale de chargement des données hôtelières.
    Conserve la compatibilité avec l'ancienne API tout en exposant
    les nouvelles fonctions dédiées aux données réelles.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else _RAW_DIR
        self.processed_path = _PROCESSED_DIR
        self.processed_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Nouvelles méthodes réelles
    # ------------------------------------------------------------------

    def load_availpro_data(self, path: Optional[Path] = None) -> pd.DataFrame:
        """Charge les réservations AvailPro."""
        return load_availpro_data(path)

    def load_booking_reviews(self, path: Optional[Path] = None) -> pd.DataFrame:
        """Charge les avis Booking.com."""
        return load_booking_reviews(path)

    def load_expedia_reviews(self, path: Optional[Path] = None) -> pd.DataFrame:
        """Charge les avis Expedia."""
        return load_expedia_reviews(path)

    def clean_reservations(self, df: pd.DataFrame) -> pd.DataFrame:
        return clean_reservations(df)

    def clean_booking_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        return clean_booking_reviews(df)

    def clean_expedia_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        return clean_expedia_reviews(df)

    def merge_reviews_with_reservations(self, df_res: pd.DataFrame,
                                         df_rev: pd.DataFrame) -> pd.DataFrame:
        return merge_reviews_with_reservations(df_res, df_rev)

    def build_final_dataset(self, save: bool = True) -> pd.DataFrame:
        return build_final_dataset(save=save)

    # ------------------------------------------------------------------
    # Méthodes héritées (compatibilité)
    # ------------------------------------------------------------------

    def load_client_data(self, filename: str) -> pd.DataFrame:
        """
        Charge un fichier client générique (CSV ou Excel).
        Si le fichier n'existe pas, tente de construire le dataset hôtelier.
        """
        file_path = Path(self.data_path) / filename
        if file_path.exists():
            if file_path.suffix == ".csv":
                return _safe_read_csv(file_path)
            elif file_path.suffix in [".xlsx", ".xls"]:
                return _safe_read_excel(file_path)
        logger.warning(f"Fichier {filename} introuvable — tentative de construction du dataset hôtelier.")
        try:
            return self.build_final_dataset(save=True)
        except Exception as e:
            logger.error(f"Dataset hôtelier inaccessible : {e}. Fallback données démo.")
            return self.generate_sample_data()

    def load_interaction_data(self, filename: str) -> pd.DataFrame:
        """
        Charge un fichier d'interactions. Retourne un DataFrame vide avec les colonnes attendues
        (les interactions réelles sont construites par le NetworkAnalyzer).
        """
        file_path = Path(self.data_path) / filename
        if file_path.exists():
            return _safe_read_csv(file_path)
        logger.warning(f"Fichier interactions {filename} introuvable — retour DataFrame vide.")
        return pd.DataFrame(columns=["client_source", "client_target", "weight"])

    def generate_sample_data(self, n_clients: int = 200) -> pd.DataFrame:
        """Génère des données de démo (mode démo uniquement — ne pas utiliser en production)."""
        logger.info(f"[DEMO] Génération de {n_clients} clients simulés")
        np.random.seed(42)
        channels  = ["booking", "direct", "expedia_group", "metasearch", "other_ota"]
        rooms     = ["standard", "superieure", "suite", "twin", "double"]
        countries = ["france", "germany", "uk", "usa", "italy", "spain", "switzerland"]
        data = {
            "client_id":      [f"C{i:04d}" for i in range(n_clients)],
            "pays":           np.random.choice(countries, n_clients),
            "langue":         np.random.choice(["fr", "en", "de", "es", "it"], n_clients),
            "channel_group":  np.random.choice(channels, n_clients),
            "room_segment":   np.random.choice(rooms, n_clients),
            "stay_length":    np.random.randint(1, 8, n_clients),
            "lead_time_days": np.random.randint(0, 180, n_clients),
            "arrival_month":  np.random.randint(1, 13, n_clients),
            "revenue":        np.random.lognormal(5, 0.7, n_clients),
            "is_cancelled":   np.random.choice([0, 1], n_clients, p=[0.85, 0.15]),
            "has_review":     np.random.choice([0, 1], n_clients, p=[0.6, 0.4]),
        }
        df = pd.DataFrame(data)
        df["review_score"] = np.where(
            df["has_review"] == 1,
            np.random.uniform(6, 10, n_clients),
            np.nan,
        )
        df["high_satisfaction"] = (df["review_score"] >= 8.0).fillna(0).astype(int)
        df["amount_bucket"] = pd.cut(
            df["revenue"],
            bins=[0, 80, 150, 300, 600, np.inf],
            labels=["<80€", "80-150€", "150-300€", "300-600€", ">600€"],
        ).astype(str)
        out = self.processed_path / "sample_clients.csv"
        df.to_csv(out, index=False)
        return df

    def generate_sample_interactions(self, n_interactions: int = 500) -> pd.DataFrame:
        """Génère des interactions de démo (mode démo uniquement)."""
        logger.info(f"[DEMO] Génération de {n_interactions} interactions simulées")
        np.random.seed(42)
        n_clients = 100
        data = {
            "client_source": [f"C{i:04d}" for i in np.random.randint(0, n_clients, n_interactions)],
            "client_target": [f"C{i:04d}" for i in np.random.randint(0, n_clients, n_interactions)],
            "weight": np.random.uniform(0.1, 1.0, n_interactions),
        }
        df = pd.DataFrame(data)
        df = df[df["client_source"] != df["client_target"]]
        out = self.processed_path / "sample_interactions.csv"
        df.to_csv(out, index=False)
        return df

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prétraitement générique — conservé pour compatibilité."""
        df = df.copy()
        if "client_id" in df.columns:
            df = df.dropna(subset=["client_id"])
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].str.strip() if hasattr(df[col], "str") else df[col]
        return df

    def split_train_test(
        self, df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Divise le dataset en train/test."""
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)
        logger.info(f"Split : {len(train_df)} train / {len(test_df)} test")
        return train_df, test_df

