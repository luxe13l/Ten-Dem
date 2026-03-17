"""
Виджет пузырька сообщения
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QFont

from src.models.message import Message
from src.utils.settings import (
    COLOR_MESSAGE_OWN, COLOR_MESSAGE_OTHER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, MESSAGE_BORDER_RADIUS, MESSAGE_PADDING_X,
    MESSAGE_PADDING_Y, FONT_FAMILY, FONT_SIZE_MESSAGE, FONT_SIZE_TIME,
    COLOR_TEXT_ON_ACCENT
)


class MessageBubble(QWidget):
    """Виджет для отображения одного сообщения."""
    
    def __init__(self, message, is_self, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_self = is_self
        
        self.padding_x = MESSAGE_PADDING_X
        self.padding_y = MESSAGE_PADDING_Y
        self.border_radius = MESSAGE_BORDER_RADIUS
        self.max_width = 400
        
        self.init_ui()
    
    def init_ui(self):
        """Создаёт интерфейс пузырька."""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(2)
            
            self.text_label = QLabel(self.message.text)
            self.text_label.setWordWrap(True)
            self.text_label.setStyleSheet(f"""
                color: {COLOR_TEXT_ON_ACCENT if self.is_self else COLOR_TEXT_PRIMARY};
                font-size: {FONT_SIZE_MESSAGE}px;
                font-family: {FONT_FAMILY};
                padding: {self.padding_y}px {self.padding_x}px 2px;
            """)
            layout.addWidget(self.text_label)
            
            meta_layout = QHBoxLayout()
            meta_layout.setContentsMargins(0, 0, self.padding_x, self.padding_y // 2)
            
            if not self.is_self:
                meta_layout.addStretch()
            
            self.meta_label = QLabel()
            self.update_meta()
            self.meta_label.setStyleSheet(f"""
                color: {COLOR_TEXT_ON_ACCENT if self.is_self else COLOR_TEXT_SECONDARY};
                font-size: {FONT_SIZE_TIME}px;
                font-family: {FONT_FAMILY};
            """)
            meta_layout.addWidget(self.meta_label)
            
            if self.is_self:
                meta_layout.addStretch()
            
            layout.addLayout(meta_layout)
            
            self.setAlignment(Qt.AlignmentFlag.AlignRight if self.is_self else Qt.AlignmentFlag.AlignLeft)
            self.update_style()
            
        except Exception as e:
            print(f"Ошибка инициализации пузырька: {e}")
    
    def update_style(self):
        """Обновляет стиль."""
        try:
            if self.is_self:
                self.setStyleSheet(f"""
                    QWidget {{
                        background-color: {COLOR_MESSAGE_OWN};
                        border-radius: {self.border_radius}px;
                        margin-left: 60px;
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    QWidget {{
                        background-color: {COLOR_MESSAGE_OTHER};
                        border-radius: {self.border_radius}px;
                        margin-right: 60px;
                    }}
                """)
        except Exception:
            pass
    
    def update_meta(self):
        """Обновляет время и статус."""
        try:
            status_icon = self.message.get_status_icon(self.is_self)
            self.meta_label.setText(f"{self.message.format_time()} {status_icon}")
        except Exception:
            pass
    
    def sizeHint(self):
        """Вычисляет предпочтительный размер."""
        try:
            text_width = self.text_label.sizeHint().width()
            width = min(text_width + self.padding_x * 2, self.max_width)
            height = self.text_label.sizeHint().height() + 30
            
            return QSize(width, height)
        except Exception:
            return QSize(200, 50)
    
    def paintEvent(self, event):
        """Кастомная отрисовка."""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            if self.is_self:
                painter.setBrush(QColor(COLOR_MESSAGE_OWN))
            else:
                painter.setBrush(QColor(COLOR_MESSAGE_OTHER))
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), self.border_radius, self.border_radius)
            
            super().paintEvent(event)
        except Exception:
            super().paintEvent(event)