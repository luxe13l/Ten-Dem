# -*- coding: utf-8 -*-
"""
Настройки приложения: цвета, размеры, пути.
"""

import os

# Приложение
APP_NAME = "Ten Dem Messenger"
ORGANIZATION_NAME = "TenDem"

# Цвета
MY_MESSAGE_COLOR = "#2481CC"
OTHER_MESSAGE_COLOR = "#F1F3F5"
MY_TEXT_COLOR = "#FFFFFF"
OTHER_TEXT_COLOR = "#212529"
SECONDARY_TEXT = "#6C757D"
DIVIDER_COLOR = "#E9ECEF"
BACKGROUND_MAIN = "#F8F9FA"
BACKGROUND_PANEL = "#FFFFFF"

# Размеры
AVATAR_SIZE = 50
MESSAGE_FONT_SIZE = 14
MESSAGE_BORDER_RADIUS = 15

# Пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
STYLES_DIR = os.path.join(ASSETS_DIR, "styles")