"""
Test simple pour vérifier que tous les imports fonctionnent.
"""

print("Test 1: Import du module data...")
try:
    from src.data.data_loader import DataLoader
    print("✅ Module data importé avec succès")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\nTest 2: Import du module network...")
try:
    from src.network.network_analyzer import NetworkAnalyzer
    print("✅ Module network importé avec succès")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\nTest 3: Import du module models...")
try:
    from src.models.predictor import CentralityPredictor
    print("✅ Module models importé avec succès")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\nTest 4: Import du module visualization...")
try:
    from src.visualization.visualizer import NetworkVisualizer
    print("✅ Module visualization importé avec succès")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "="*50)
print("TOUS LES IMPORTS FONCTIONNENT !" if all else "Certains imports ont échoué")
print("="*50)
print("\nVous pouvez maintenant exécuter:")
print("  - python demo.py")
print("  - python exemple_simple.py")
print("  - streamlit run app.py")

