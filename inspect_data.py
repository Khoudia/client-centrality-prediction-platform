"""Script temporaire pour inspecter les colonnes réelles des fichiers de données."""
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

RAW = "data-projet-sorbonne"

# ── AvailPro ─────────────────────────────────────────────────────────────────
print("=" * 60)
print("AVAILPRO")
print("=" * 60)
try:
    df = pd.read_excel(f"{RAW}/availpro_export.xlsx", engine="openpyxl")
    print(f"Shape : {df.shape}")
    print("Colonnes :")
    for c in df.columns:
        print(f"  {repr(c)}")
    print("\nPremières lignes :")
    print(df.head(3).to_string())
except Exception as e:
    print(f"ERREUR : {e}")

# ── Booking avis traités ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("AVIS BOOKING (Excel traité)")
print("=" * 60)
try:
    df2 = pd.read_excel(f"{RAW}/données avis traités.xlsx", engine="openpyxl")
    print(f"Shape : {df2.shape}")
    print("Colonnes :")
    for c in df2.columns:
        print(f"  {repr(c)}")
    print("\nPremières lignes :")
    print(df2.head(3).to_string())
except Exception as e:
    print(f"ERREUR : {e}")

# ── Booking avis CSV ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("AVIS BOOKING (CSV brut)")
print("=" * 60)
try:
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        for sep in [",", ";", "\t"]:
            try:
                df3 = pd.read_csv(f"{RAW}/données avis booking.csv",
                                  sep=sep, encoding=enc, low_memory=False, nrows=5)
                if df3.shape[1] > 2:
                    print(f"Lu avec sep={repr(sep)}, encoding={enc}")
                    print(f"Shape : {df3.shape}")
                    print("Colonnes :")
                    for c in df3.columns:
                        print(f"  {repr(c)}")
                    print(df3.head(3).to_string())
                    break
            except Exception:
                continue
        else:
            continue
        break
except Exception as e:
    print(f"ERREUR : {e}")

# ── Expedia ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("AVIS EXPEDIA")
print("=" * 60)
try:
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        for sep in ["\t", ",", ";"]:
            try:
                df4 = pd.read_csv(
                    f"{RAW}/expediareviews_from_2025-03-01_to_2026-03-01.csv",
                    sep=sep, encoding=enc, low_memory=False, nrows=5)
                if df4.shape[1] > 2:
                    print(f"Lu avec sep={repr(sep)}, encoding={enc}")
                    print(f"Shape : {df4.shape}")
                    print("Colonnes :")
                    for c in df4.columns:
                        print(f"  {repr(c)}")
                    print(df4.head(3).to_string())
                    break
            except Exception:
                continue
        else:
            continue
        break
except Exception as e:
    print(f"ERREUR : {e}")

