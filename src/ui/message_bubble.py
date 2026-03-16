# src/ui/message_bubble.py
# -*- coding: utf-8 -*-

"""
Кастомный виджет пузырька сообщения.
Отображает одно сообщение с выравниванием в зависимости от отправителя,
цветом фона, временем и статусом доставки/прочтения.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from models.message import Message
from utils.settings import MY_MESSAGE_COLOR, OTHER_MESSAGE_COLOR
from utils.helpers import format_time


class MessageBubble(QWidget):
    """Виджет пузырька сообщения."""

    def __init__(self, message: Message, is_self: bool, parent=None):
        """
        Инициализация пузырька.

        Args:
            message (Message): объект сообщения.
            is_self (bool): True, если сообщение от текущего пользователя.
            parent (QWidget, optional): родительский виджет.
        """
        super().__init__(parent)
        self.message = message
        self.is_self = is_self

        self.init_ui()

    def init_ui(self):
        """Создание интерфейса пузырька."""
        # Основной горизонтальный layout для выравнивания всего блока
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Контейнер для пузырька (QFrame) - будет иметь фон и скругления
        self.bubble_frame = QFrame()
        self.bubble_frame.setMaximumWidth(500)  # ограничение ширины
        self.bubble_frame.setSizePolicy(
            QWidget.SizePolicy.Maximum,
            QWidget.SizePolicy.Preferred
        )

        # Внутренний layout пузырька (текст + нижняя строка)
        bubble_layout = QVBoxLayout(self.bubble_frame)
        bubble_layout.setSpacing(4)
        bubble_layout.setContentsMargins(12, 8, 12, 6)

        # Текст сообщения
        self.text_label = QLabel(self.message.text)
        self.text_label.setWordWrap(True)
        text_font = QFont()
        text_font.setPointSize(14)
        self.text_label.setFont(text_font)
        bubble_layout.addWidget(self.text_label)

        # Нижняя строка (время и статус)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(4)

        # Время
        self.time_label = QLabel(format_time(self.message.timestamp))
        time_font = QFont()
        time_font.setPointSize(11)
        self.time_label.setFont(time_font)
        bottom_layout.addWidget(self.time_label)

        # Статус (только для своих сообщений)
        if self.is_self:
            bottom_layout.addStretch()
            self.status_label = QLabel(self.get_status_text())
            status_font = QFont()
            status_font.setPointSize(11)
            self.status_label.setFont(status_font)
            bottom_layout.addWidget(self.status_label)

        bubble_layout.addLayout(bottom_layout)

        # Применяем стили в зависимости от отправителя
        self.apply_styles()

        # Добавляем пузырёк в основной layout с соответствующим выравниванием
        if self.is_self:
            main_layout.addStretch()
            main_layout.addWidget(self.bubble_frame)
        else:
            main_layout.addWidget(self.bubble_frame)
            main_layout.addStretch()

    def apply_styles(self):
        """Применяет цвета и скругления в зависимости от is_self."""
        if self.is_self:
            bg_color = MY_MESSAGE_COLOR
            text_color = "white"
            time_color = "rgba(255, 255, 255, 0.7)"
            status_color = "rgba(255, 255, 255, 0.7)"
        else:
            bg_color = OTHER_MESSAGE_COLOR
            text_color = "#212529"
            time_color = "#6C757D"
            status_color = "#6C757D"

        self.bubble_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 15px;
            }}
        """)

        self.text_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        self.time_label.setStyleSheet(f"color: {time_color}; background: transparent;")

        if self.is_self and hasattr(self, 'status_label'):
            self.status_label.setStyleSheet(f"color: {status_color}; background: transparent;")

    def get_status_text(self) -> str:
        """
        Возвращает текстовое представление статуса сообщения.
        В реальном проекте можно использовать иконки или эмодзи.
        """
        if self.message.read:
            return "✓✓"  # прочитано (две синие галочки)
        elif self.message.delivered:
            return "✓✓"  # доставлено (две серые галочки)
        else:
            return "✓"   # отправлено (одна серая галочка)

    def update_message(self, message: Message):
        """Обновляет содержимое пузырька (например, при изменении статуса)."""
        self.message = message
        self.text_label.setText(message.text)
        self.time_label.setText(format_time(message.timestamp))
        if self.is_self and hasattr(self, 'status_label'):
            self.status_label.setText(self.get_status_text())