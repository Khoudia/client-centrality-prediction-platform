"""Script d'exploration des données réelles pour l'Hôtel Aurore Paris."""
import subprocess
import sys

# Installer openpyxl si absent
subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data-projet-sorbonne")

def explore_file(path, file_type="csv", sep=",", encoding="utf-8"):
    print(f"\n{'='*60}")
    print(f"FICHIER: {os.path.basename(path)}")
    print(f"{'='*60}")
    try:
        if file_type == "xlsx":
            df = pd.read_excel(path, engine="openpyxl")
        elif file_type == "csv":
            # Essayer plusieurs encodages
            for enc in [encoding, "latin-1", "cp1252", "utf-8-sig"]:
                try:
                    for s in [sep, ";", ","]:
                        try:
                            df = pd.read_csv(path, sep=s, encoding=enc, low_memory=False)
                            if df.shape[1] > 1:
                                break
                        except:
                            continue
                    break
                except:
                    continue
        print(f"Shape: {df.shape}")
        print(f"Colonnes ({len(df.columns)}): {list(df.columns)}")
        print(f"\nTypes:")
        print(df.dtypes)
        print(f"\nAperçu (3 premières lignes):")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 200)
        print(df.head(3).to_string())
        print(f"\nValeurs manquantes:")
        print(df.isnull().sum()[df.isnull().sum() > 0])
        return df
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return None

# Explorer tous les fichiers (données avis traités.xlsx supprimé — doublon du CSV brut)
files = {
    "availpro_export.xlsx": {"type": "xlsx"},
    "données avis booking.csv": {"type": "csv", "sep": ";"},
    "expediareviews_from_2025-03-01_to_2026-03-01.csv": {"type": "csv"},
}

dfs = {}
for fname, params in files.items():
    path = os.path.join(DATA_DIR, fname)
    if os.path.exists(path):
        df = explore_file(path, file_type=params.get("type", "csv"),
                         sep=params.get("sep", ","))
        dfs[fname] = df
    else:
        print(f"\nFICHIER NON TROUVÉ: {fname}")

print("\n\nEXPLORATION TERMINÉE")

