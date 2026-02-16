"""
Module utilitaire pour charger la configuration.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Charge le fichier de configuration YAML.

    Args:
        config_path: Chemin vers le fichier de configuration

    Returns:
        Dictionnaire de configuration
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")

    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

