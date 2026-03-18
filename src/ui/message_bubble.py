"""
Пузырёк сообщения для чата Ten Dem
Современный минимализм — дизайн-система v2.0
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.models.message import Message, MessageType, MessageStatus
from src.utils.settings import (
    MESSAGE_OWN_BG, MESSAGE_OWN_TEXT,
    MESSAGE_OTHER_BG, MESSAGE_OTHER_TEXT,
    TEXT_TERTIARY, TEXT_ON_ACCENT,
    READ_CHECK, DELIVERED_CHECK,
    FONT_FAMILY, FONT_SIZE_MESSAGE, FONT_SIZE_TIME,
    RADIUS_MESSAGE, PADDING_CARD
)


class MessageBubble(QWidget):
    """Пузырёк сообщения."""
    
    def __init__(self, message: Message, is_own: bool, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_own = is_own
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        try:
            # Главный layout
            main_layout = QHBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            if self.is_own:
                main_layout.addStretch()
            
            # Карточка сообщения
            self.bubble = QFrame()
            self.bubble.setStyleSheet(f"""
                QFrame {{
                    background-color: {MESSAGE_OWN_BG if self.is_own else MESSAGE_OTHER_BG};
                    color: {MESSAGE_OWN_TEXT if self.is_own else MESSAGE_OTHER_TEXT};
                    border-radius: {RADIUS_MESSAGE}px;
                    padding: {PADDING_CARD}px;
                }}
            """)
            
            # Скругление углов (разное для своих/чужих)
            if self.is_own:
                self.bubble.setStyleSheet(self.bubble.styleSheet() + f"""
                    QFrame {{
                        border-top-left-radius: {RADIUS_MESSAGE}px;
                        border-top-right-radius: {RADIUS_MESSAGE}px;
                        border-bottom-left-radius: {RADIUS_MESSAGE}px;
                        border-bottom-right-radius: 4px;
                    }}
                """)
            else:
                self.bubble.setStyleSheet(self.bubble.styleSheet() + f"""
                    QFrame {{
                        border-top-left-radius: {RADIUS_MESSAGE}px;
                        border-top-right-radius: {RADIUS_MESSAGE}px;
                        border-bottom-left-radius: 4px;
                        border-bottom-right-radius: {RADIUS_MESSAGE}px;
                    }}
                """)
            
            bubble_layout = QVBoxLayout(self.bubble)
            bubble_layout.setSpacing(4)
            
            # Если это ответ на сообщение
            if self.message.reply_to_id:
                reply_label = QLabel("↩️ Ответ на сообщение")
                reply_label.setStyleSheet(f"""
                    color: {TEXT_ON_ACCENT if self.is_own else TEXT_TERTIARY};
                    font-size: 11px;
                    font-style: italic;
                """)
                bubble_layout.addWidget(reply_label)
            
            # Тип сообщения
            if self.message.message_type == MessageType.PHOTO:
                content_label = QLabel("📷 Фото")
            elif self.message.message_type == MessageType.FILE:
                content_label = QLabel(f"📁 {self.message.file_name}")
            elif self.message.message_type == MessageType.VOICE:
                content_label = QLabel(f"🎤 Голосовое ({self.message.duration}с)")
            elif self.message.message_type == MessageType.VIDEO:
                content_label = QLabel(f"📹 Видео ({self.message.duration}с)")
            else:
                content_label = QLabel(self.message.text)
            
            content_label.setStyleSheet(f"""
                color: {MESSAGE_OWN_TEXT if self.is_own else MESSAGE_OTHER_TEXT};
                font-size: {FONT_SIZE_MESSAGE}px;
                font-family: {FONT_FAMILY};
                font-weight: {400};
            """)
            content_label.setWordWrap(True)
            bubble_layout.addWidget(content_label)
            
            # Нижняя строка (время + галочки)
            bottom_layout = QHBoxLayout()
            bottom_layout.setSpacing(4)
            bottom_layout.addStretch() if self.is_own else None
            
            # Время
            time_label = QLabel(self.message.timestamp.strftime("%H:%M"))
            time_label.setStyleSheet(f"""
                color: {TEXT_ON_ACCENT if self.is_own else TEXT_TERTIARY};
                font-size: {FONT_SIZE_TIME}px;
                font-family: {FONT_FAMILY};
                opacity: 0.7;
            """)
            bottom_layout.addWidget(time_label)
            
            # Галочки (только для своих сообщений)
            if self.is_own:
                check_icon = self._get_check_icon()
                if check_icon:
                    check_label = QLabel(check_icon)
                    check_label.setStyleSheet(f"""
                        color: {READ_CHECK if self.message.status == MessageStatus.READ else DELIVERED_CHECK};
                        font-size: {FONT_SIZE_TIME}px;
                    """)
                    bottom_layout.addWidget(check_label)
            
            bottom_layout.addStretch() if not self.is_own else None
            bubble_layout.addLayout(bottom_layout)
            
            # Если сообщение отредактировано
            if self.message.is_edited:
                edited_label = QLabel("(изм.)")
                edited_label.setStyleSheet(f"""
                    color: {TEXT_ON_ACCENT if self.is_own else TEXT_TERTIARY};
                    font-size: 10px;
                    opacity: 0.6;
                """)
                bottom_layout.addWidget(edited_label)
            
            main_layout.addWidget(self.bubble)
            
            if not self.is_own:
                main_layout.addStretch()
            
            # Максимальная ширина 70%
            self.setMaximumWidth(int(self.parent().width() * 0.7) if self.parent() else 500)
            
        except Exception as e:
            print(f"Ошибка инициализации пузырька: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_check_icon(self) -> str:
        """Возвращает иконку галочки."""
        if self.message.status == MessageStatus.READ:
            return "✓✓"  # Прочитано
        elif self.message.status == MessageStatus.DELIVERED:
            return "✓✓"  # Доставлено
        else:
            return "✓"   # Отправлено
    
    def update_status(self, status: MessageStatus):
        """Обновляет статус сообщения."""
        self.message.status = status
        # Перерисовываем галочки
        self.init_ui()