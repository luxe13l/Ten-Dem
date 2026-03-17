"""
Виджет аватарки пользователя
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from src.utils.helpers import get_initials, generate_avatar_color
from src.utils.settings import AVATAR_SIZE_MAIN, FONT_FAMILY


class AvatarWidget(QLabel):
    """Виджет для отображения аватарки пользователя."""
    
    def __init__(self, name, avatar_url="", size=AVATAR_SIZE_MAIN, parent=None):
        super().__init__(parent)
        self.name = name
        self.avatar_url = avatar_url
        self.size_val = size
        
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        color = generate_avatar_color(name)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: {size // 2}px;
                font-weight: bold;
                font-size: {size // 2.5}px;
                font-family: {FONT_FAMILY};
            }}
        """)
        
        if not avatar_url:
            self.setText(get_initials(name))