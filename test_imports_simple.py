#!/usr/bin/env python
"""Test simple"""
print("Script test lancé")

try:
    from src.data.data_loader import DataLoader
    print("✓ DataLoader importé")
except Exception as e:
    print(f"✗ Erreur DataLoader: {e}")

try:
    from src.network.network_analyzer import NetworkAnalyzer
    print("✓ NetworkAnalyzer importé")
except Exception as e:
    print(f"✗ Erreur NetworkAnalyzer: {e}")

try:
    from src.models.predictor import CentralityPredictor
    print("✓ CentralityPredictor importé")
except Exception as e:
    print(f"✗ Erreur CentralityPredictor: {e}")

try:
    from src.visualization.visualizer import NetworkVisualizer
    print("✓ NetworkVisualizer importé")
except Exception as e:
    print(f"✗ Erreur NetworkVisualizer: {e}")

print("Test terminé")

