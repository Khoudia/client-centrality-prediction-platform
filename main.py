"""Point d’entrée léger pour le projet Hôtel Aurore Paris."""

import sys
from pathlib import Path

# Ajouter le dossier src au path Python
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger
from src.data.data_loader import DataLoader
from src.network.network_analyzer import NetworkAnalyzer
from src.models.predictor import SatisfactionPredictor
from src.visualization.visualizer import NetworkVisualizer

logger = setup_logger(__name__)


def main():
    """
    Point d'entrée principal du projet.
    Réalise un smoke test des composants principaux puis invite à lancer Streamlit.
    """
    logger.info("🚀 Démarrage de la plateforme Hôtel Aurore Paris")

    try:
        # 1. Chargement des données
        logger.info("📊 Initialisation du chargeur de données...")
        data_loader = DataLoader()

        # 2. Analyse du réseau
        logger.info("🕸️  Initialisation du module réseau...")
        network_analyzer = NetworkAnalyzer()

        # 3. Modélisation de la satisfaction
        logger.info("🤖 Initialisation du modèle de satisfaction...")
        predictor = SatisfactionPredictor()

        # 4. Visualisation
        logger.info("📈 Initialisation du module de visualisation...")
        visualizer = NetworkVisualizer()

        logger.info("✅ Composants initialisés avec succès")
        logger.info("➡️ Lancez l'application avec : python -m streamlit run app.py")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution: {str(e)}")
        raise


if __name__ == '__main__':
    main()
