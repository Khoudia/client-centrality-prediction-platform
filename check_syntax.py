"""Vérifie la syntaxe de tous les modules Python du projet."""
import ast
import sys
from pathlib import Path

root = Path(r"C:\Users\KFA24632\sda-2026\client-centrality-prediction-platform")
files = [
    root / "app.py",
    root / "src" / "data" / "data_loader.py",
    root / "src" / "network" / "network_analyzer.py",
    root / "src" / "models" / "predictor.py",
    root / "src" / "visualization" / "visualizer.py",
]

all_ok = True
for f in files:
    try:
        src = f.read_text(encoding="utf-8")
        ast.parse(src)
        print(f"OK  {f.name}")
    except SyntaxError as e:
        print(f"ERR {f.name}: {e}")
        all_ok = False
    except Exception as e:
        print(f"ERR {f.name}: {e}")
        all_ok = False

if all_ok:
    print("\n=== Tous les fichiers sont syntaxiquement corrects ===")
else:
    print("\n=== Des erreurs ont été trouvées ===")
    sys.exit(1)

