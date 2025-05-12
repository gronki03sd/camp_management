from pathlib import Path

from .apps import ThemeConfig

APP_NAME = ThemeConfig.name
APPS_DIR = Path(__file__).resolve().parent.parent.parent