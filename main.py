"""
Module principal de la plateforme de prédiction de centralité client.
"""

import sys
from pathlib import Path

# Ajouter le dossier src au path Python
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger
from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import CentralityPredictor
from src.visualization.visualizer import NetworkVisualizer

logger = setup_logger(__name__)


def main():
    """
    Point d'entrée principal de l'application.
    """
    logger.info("🚀 Démarrage de la plateforme de prédiction de centralité client")

    try:
        # 1. Chargement des données
        logger.info("📊 Chargement des données...")
        data_loader = DataLoader()

        # 2. Analyse du réseau
        logger.info("🕸️  Analyse du réseau...")
        network_analyzer = NetworkAnalyzer()

        # 3. Prédiction de centralité
        logger.info("🤖 Entraînement des modèles de prédiction...")
        predictor = CentralityPredictor()

        # 4. Visualisation
        logger.info("📈 Génération des visualisations...")
        visualizer = NetworkVisualizer()

        logger.info("✅ Processus terminé avec succès!")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution: {str(e)}")
        raise


if __name__ == '__main__':
    main()
