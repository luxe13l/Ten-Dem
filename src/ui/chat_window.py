# src/ui/chat_window.py
# -*- coding: utf-8 -*-

"""
Окно переписки с выбранным контактом.
Отображает сообщения в виде пузырьков, поддерживает отправку и получение в реальном времени.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame,
    QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QTextCursor

from database.messages_db import MessagesDB
from models.message import Message
from models.user import User
from ui.message_bubble import MessageBubble
from utils.helpers import format_time
from utils.settings import MY_MESSAGE_COLOR, OTHER_MESSAGE_COLOR


class ChatWindow(QWidget):
    """Виджет чата с конкретным контактом."""

    def __init__(self, current_user: User, contact: User):
        """
        Инициализация окна чата.

        Args:
            current_user (User): текущий пользователь.
            contact (User): собеседник.
        """
        super().__init__()
        self.current_user = current_user
        self.contact = contact
        self.messages = []           # список всех сообщений в этом чате
        self.message_widgets = []    # список виджетов сообщений
        self.messages_listener = None  # слушатель новых сообщений

        self.init_ui()
        self.load_messages()
        self.listen_for_new_messages()

    def init_ui(self):
        """Создаёт интерфейс окна чата."""
        # Главный вертикальный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Шапка чата
        header = self.create_header()
        main_layout.addWidget(header)

        # Область сообщений (скроллируемая)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #F8F9FA;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F8F9FA;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CED4DA;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ADB5BD;
            }
        """)

        # Контейнер для сообщений
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)

        self.scroll_area.setWidget(self.messages_container)
        main_layout.addWidget(self.scroll_area)

        # Панель ввода сообщения
        input_panel = self.create_input_panel()
        main_layout.addWidget(input_panel)

    def create_header(self) -> QWidget:
        """Создаёт шапку чата с именем контакта и кнопкой назад."""
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            background-color: white;
            border-bottom: 1px solid #E9ECEF;
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        # Кнопка "Назад" (стрелка)
        self.back_button = QPushButton("←")
        self.back_button.setFixedSize(40, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 24px;
                color: #2481CC;
            }
            QPushButton:hover {
                color: #1A5A8C;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        # Аватарка контакта (круглая)
        avatar_label = QLabel()
        avatar_label.setFixedSize(50, 50)
        avatar_label.setStyleSheet("""
            border-radius: 25px;
            background-color: #E9ECEF;
        """)
        # Здесь можно добавить загрузку реальной аватарки
        avatar_label.setText("")  # Заглушка
        layout.addWidget(avatar_label)

        # Информация о контакте
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(self.contact.name)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)

        self.status_label = QLabel(self.contact.get_online_status())
        self.status_label.setStyleSheet("color: #6C757D; font-size: 13px;")
        info_layout.addWidget(self.status_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        return header

    def create_input_panel(self) -> QWidget:
        """Создаёт панель ввода сообщения с кнопкой отправки."""
        panel = QWidget()
        panel.setFixedHeight(80)
        panel.setStyleSheet("""
            background-color: white;
            border-top: 1px solid #E9ECEF;
        """)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        # Поле ввода текста
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Напишите сообщение...")
        self.message_input.setFixedHeight(45)
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CED4DA;
                border-radius: 22px;
                padding: 0 20px;
                font-size: 15px;
                background-color: #F8F9FA;
            }
            QLineEdit:focus {
                border-color: #2481CC;
                background-color: white;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)

        # Кнопка отправки (с иконкой)
        self.send_button = QPushButton()
        self.send_button.setFixedSize(45, 45)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2481CC;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #1A5A8C;
            }
            QPushButton:pressed {
                background-color: #0E3A5C;
            }
        """)
        # Текстовая заглушка для иконки (можно заменить на QIcon)
        self.send_button.setText("➤")
        self.send_button.setStyleSheet(self.send_button.styleSheet() + """
            QPushButton {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        return panel

    def load_messages(self):
        """Загружает историю сообщений из Firestore."""
        messages = MessagesDB.get_messages(self.current_user.uid, self.contact.uid, limit=50)
        self.messages = messages
        for message in messages:
            self.add_message_to_ui(message, animate=False)

        # Прокрутка вниз после загрузки
        QTimer.singleShot(100, self.scroll_to_bottom)

    def add_message_to_ui(self, message: Message, animate: bool = True):
        """
        Добавляет сообщение в интерфейс.

        Args:
            message (Message): сообщение для отображения.
            animate (bool): если True, добавляет анимацию появления.
        """
        # Проверяем, не добавлено ли уже это сообщение
        if hasattr(message, 'id') and message.id:
            for msg in self.messages:
                if hasattr(msg, 'id') and msg.id == message.id:
                    return

        self.messages.append(message)

        is_me = (message.from_uid == self.current_user.uid)
        bubble = MessageBubble(message, is_me)

        # Анимация появления (простейшая - через стиль)
        if animate:
            bubble.setStyleSheet(bubble.styleSheet() + """
                QLabel {
                    animation: fadeIn 0.3s;
                }
            """)

        self.messages_layout.addWidget(bubble)
        self.message_widgets.append(bubble)

        # Прокрутка вниз
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Прокручивает область сообщений в самый низ."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        """Отправляет сообщение."""
        text = self.message_input.text().strip()
        if not text:
            return

        # Создаём временное сообщение для оптимистичного интерфейса
        temp_message = Message(
            from_uid=self.current_user.uid,
            to_uid=self.contact.uid,
            text=text,
            read=False,
            delivered=False
        )

        # Добавляем в интерфейс сразу
        self.add_message_to_ui(temp_message)

        # Очищаем поле ввода
        self.message_input.clear()

        # Отправляем в Firebase
        try:
            message_id = MessagesDB.send_message(
                self.current_user.uid,
                self.contact.uid,
                text
            )
            # Можно обновить ID у временного сообщения, но для простоты пропустим
        except Exception as e:
            # В случае ошибки показываем уведомление и удаляем сообщение
            from utils.helpers import show_error
            show_error("Ошибка", f"Не удалось отправить сообщение: {e}")
            # Удаляем последнее добавленное сообщение
            if self.message_widgets:
                last_widget = self.message_widgets.pop()
                last_widget.deleteLater()

    def listen_for_new_messages(self):
        """Подписывается на новые сообщения в реальном времени."""
        def on_new_messages(new_messages):
            for message in new_messages:
                # Проверяем, относится ли сообщение к этому чату
                if (message.from_uid == self.current_user.uid and message.to_uid == self.contact.uid) or \
                   (message.from_uid == self.contact.uid and message.to_uid == self.current_user.uid):
                    self.add_message_to_ui(message)

        self.messages_listener = MessagesDB.listen_for_messages(on_new_messages)

    def go_back(self):
        """Возврат к списку контактов (закрытие чата)."""
        # Сигнал для родительского окна
        self.deleteLater()

    def update_contact_status(self):
        """Обновляет статус контакта (вызывается извне)."""
        self.status_label.setText(self.contact.get_online_status())

    def closeEvent(self, event):
        """При закрытии окна отписываемся от слушателя."""
        if self.messages_listener:
            self.messages_listener.unsubscribe()
        event.accept()