"""
Виджет аватарки для Ten Dem
Современный минимализм — дизайн-система v2.0
"""
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen

from src.utils.settings import (
    AVATAR_LIST, AVATAR_CHAT, AVATAR_PROFILE,
    FONT_FAMILY, ONLINE, BG_TERTIARY, TEXT_PRIMARY
)


class AvatarWidget(QWidget):
    """Виджет аватарки пользователя."""
    
    def __init__(self, name: str = "", avatar_url: str = "", size: int = 52, parent=None):
        super().__init__(parent)
        self.name = name
        self.avatar_url = avatar_url
        self.size = size
        self.is_online = False
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setFixedSize(self.size, self.size)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_TERTIARY};
                border-radius: {self.size // 2}px;
            }}
        """)
        
        # Layout для аватарки
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Если есть URL аватарки — загружаем (пока заглушка)
        if self.avatar_url:
            # TODO: Загрузка изображения по URL
            pass
        
        # Буква имени
        initial = self.get_initial()
        self.label = QLabel(initial)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: {self.size // 3}px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        """)
        layout.addWidget(self.label)
        
        # Индикатор онлайн (опционально)
        self.online_indicator = None
    
    def get_initial(self) -> str:
        """Получает первую букву имени."""
        if self.name:
            return self.name[0].upper()
        return "?"
    
    def set_online(self, is_online: bool):
        """Устанавливает статус онлайн."""
        self.is_online = is_online
        self.update()
    
    def paintEvent(self, event):
        """Рисует индикатор онлайн."""
        super().paintEvent(event)
        
        if self.is_online:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Зелёный кружок в правом нижнем углу
            indicator_size = self.size // 5
            painter.setBrush(QBrush(QColor(ONLINE)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawEllipse(
                self.width() - indicator_size - 2,
                self.height() - indicator_size - 2,
                indicator_size,
                indicator_size
            )
            painter.end()