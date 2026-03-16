# src/ui/main_window.py
# -*- coding: utf-8 -*-

"""
Главное окно мессенджера.
Слева список контактов, справа область чата.
При клике на контакт открывается окно переписки.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.firebase_client import get_db
from database.users_db import UsersDB
from database.messages_db import MessagesDB
from ui.contact_item import ContactItemWidget
from ui.chat_window import ChatWindow
from models.user import User
from utils.settings import APP_NAME


class MainWindow(QMainWindow):
    """Главное окно со списком контактов и областью чата."""

    def __init__(self, current_user: User):
        """
        Инициализация главного окна.

        Args:
            current_user (User): текущий авторизованный пользователь.
        """
        super().__init__()
        self.current_user = current_user
        self.contacts = []               # список всех пользователей кроме текущего
        self.contact_widgets = {}         # uid -> виджет для быстрого обновления
        self.current_chat_widget = None   # виджет текущего открытого чата
        self.users_listener = None        # слушатель изменений пользователей

        self.setWindowTitle(f"{APP_NAME} — {current_user.name}")
        self.setMinimumSize(900, 600)

        # Центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Сплиттер для разделения списка контактов и области чата
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Левая панель — список контактов
        self.contacts_list = QListWidget()
        self.contacts_list.setObjectName("contactsList")
        self.contacts_list.setMaximumWidth(320)
        self.contacts_list.setMinimumWidth(280)
        self.contacts_list.setStyleSheet("""
            QListWidget {
                background-color: #F8F9FA;
                border: none;
                outline: none;
            }
            QListWidget::item {
                border: none;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #E9ECEF;
            }
        """)
        self.contacts_list.itemClicked.connect(self.on_contact_selected)
        self.splitter.addWidget(self.contacts_list)

        # Правая панель (изначально пустая с заглушкой)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.placeholder = QLabel("Выберите контакт для начала общения")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_font = QFont()
        placeholder_font.setPointSize(16)
        placeholder_font.setBold(True)
        self.placeholder.setFont(placeholder_font)
        self.placeholder.setStyleSheet("color: #ADB5BD;")
        self.right_layout.addWidget(self.placeholder)

        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([300, 600])

        # Загрузка списка контактов
        self.load_contacts()

        # Запуск слушателя изменений пользователей (статусы онлайн)
        self.start_users_listener()

    def load_contacts(self):
        """Загружает список всех пользователей, кроме текущего, и отображает их."""
        self.contacts_list.clear()
        self.contact_widgets.clear()
        users = UsersDB.get_all_users(exclude_uid=self.current_user.uid)
        self.contacts = users

        for user in users:
            self.add_contact_to_list(user)

    def add_contact_to_list(self, user: User):
        """Добавляет одного контакта в список."""
        # Получаем последнее сообщение между текущим пользователем и этим контактом
        messages = MessagesDB.get_messages(self.current_user.uid, user.uid, limit=1)
        last_msg = messages[0] if messages else None
        last_msg_text = last_msg.text if last_msg else ""
        last_msg_time = last_msg.timestamp if last_msg else None
        unread_count = 0  # TODO: реализовать подсчёт непрочитанных

        # Создаём кастомный виджет контакта
        item = QListWidgetItem()
        widget = ContactItemWidget(
            user=user,
            last_message=last_msg_text,
            last_message_time=last_msg_time,
            unread_count=unread_count
        )
        item.setSizeHint(widget.sizeHint())
        self.contacts_list.addItem(item)
        self.contacts_list.setItemWidget(item, widget)
        self.contact_widgets[user.uid] = widget

    def start_users_listener(self):
        """Запускает слушатель изменений коллекции users для обновления статусов онлайн."""
        db = get_db()

        def on_snapshot(doc_snapshot, changes, read_time):
            # Обновляем статусы для изменившихся документов
            for change in changes:
                if change.type.name == 'MODIFIED':
                    data = change.document.to_dict()
                    uid = change.document.id
                    if uid == self.current_user.uid:
                        continue  # свои изменения не обрабатываем
                    if uid in self.contact_widgets:
                        # Обновляем виджет (статус и last_seen)
                        widget = self.contact_widgets[uid]
                        widget.user.status = data.get('status', widget.user.status)
                        if 'last_seen' in data:
                            widget.user.last_seen = data['last_seen']
                        # Обновляем отображение статуса в виджете
                        widget.update_status()

        # Подписываемся на все документы users
        query = db.collection('users')
        self.users_listener = query.on_snapshot(on_snapshot)

    def on_contact_selected(self, item: QListWidgetItem):
        """
        Обработчик клика по контакту.
        Открывает окно чата с выбранным контактом.

        Args:
            item (QListWidgetItem): выбранный элемент.
        """
        widget = self.contacts_list.itemWidget(item)
        if not isinstance(widget, ContactItemWidget):
            return

        contact = widget.user

        # Удаляем старый чат, если есть
        if self.current_chat_widget:
            self.current_chat_widget.deleteLater()
            self.current_chat_widget = None

        # Создаём новый чат
        self.current_chat_widget = ChatWindow(self.current_user, contact)

        # Вставляем в правую панель (заменяем заглушку)
        self.right_layout.insertWidget(0, self.current_chat_widget)
        self.placeholder.hide()

    def closeEvent(self, event):
        """При закрытии окна отписываемся от слушателя."""
        if self.users_listener:
            self.users_listener.unsubscribe()
        event.accept()