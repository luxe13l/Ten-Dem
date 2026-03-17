"""
Виджет контакта в списке чатов
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from src.models.user import User
from src.ui.avatar_widget import AvatarWidget
from src.utils.helpers import format_time, truncate
from src.utils.settings import (
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_ONLINE, 
    COLOR_UNREAD_BADGE, COLOR_PANEL, FONT_FAMILY, COLOR_INPUT_BG
)


class ContactItem(QWidget):
    """Виджет для отображения контакта в списке чатов."""
    
    def __init__(self, user, last_message="", unread_count=0, timestamp=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.last_message = last_message
        self.unread_count = unread_count
        self.timestamp = timestamp
        
        self.setObjectName("contactItem")
        self.init_ui()
    
    def init_ui(self):
        """Создаёт интерфейс виджета."""
        try:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(12, 10, 12, 10)
            layout.setSpacing(12)
            
            self.avatar = AvatarWidget(self.user.name, self.user.avatar_url)
            layout.addWidget(self.avatar)
            
            info_layout = QVBoxLayout()
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(3)
            
            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)
            
            name_label = QLabel(self.user.name)
            name_label.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
            name_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            top_row.addWidget(name_label)
            
            top_row.addStretch()
            
            self.time_label = QLabel()
            self.time_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            if self.timestamp:
                self.time_label.setText(format_time(self.timestamp))
            top_row.addWidget(self.time_label)
            
            info_layout.addLayout(top_row)
            
            bottom_row = QHBoxLayout()
            bottom_row.setContentsMargins(0, 0, 0, 0)
            
            self.message_label = QLabel(truncate(self.last_message or "Нет сообщений", 35))
            self.message_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
            self.message_label.setWordWrap(True)
            bottom_row.addWidget(self.message_label, 1)
            
            if self.unread_count > 0:
                self.unread_badge = QLabel(str(self.unread_count))
                self.unread_badge.setFixedSize(22, 22)
                self.unread_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.unread_badge.setStyleSheet(f"""
                    background-color: {COLOR_UNREAD_BADGE};
                    color: white;
                    border-radius: 11px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                """)
                bottom_row.addWidget(self.unread_badge)
            
            info_layout.addLayout(bottom_row)
            layout.addLayout(info_layout, 1)
            
            self.online_dot = QLabel()
            self.online_dot.setFixedSize(12, 12)
            self.update_status(self.user.status)
            layout.addWidget(self.online_dot)
            
        except Exception as e:
            print(f"Ошибка инициализации контакта: {e}")
    
    def update_status(self, status):
        """Обновляет индикатор онлайн-статуса."""
        try:
            if status == "online":
                self.online_dot.setStyleSheet(f"""
                    background-color: {COLOR_ONLINE};
                    border: 2px solid {COLOR_PANEL};
                    border-radius: 6px;
                """)
                self.online_dot.show()
            else:
                self.online_dot.hide()
        except Exception:
            pass
    
    def sizeHint(self):
        """Предпочтительный размер виджета."""
        return QSize(280, 70)