"""
Виджет чата для Ten Dem
Интеграция: Firebase (сообщения) + Яндекс (файлы)
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QScrollArea, QFrame, 
                             QMenu, QApplication, QInputDialog, QMessageBox,
                             QFileDialog)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import time
import os

from src.models.message import Message, MessageType, MessageStatus
from src.database.messages_db import send_message, edit_message, delete_message
from src.ui.message_bubble import MessageBubble
from src.styles import (
    COLOR_BACKGROUND, COLOR_PANEL, COLOR_TEXT_PRIMARY, COLOR_DIVIDER,
    COLOR_ACCENT, FONT_FAMILY, PADDING_CARD
)


class ChatWidget(QWidget):
    """Виджет чата."""
    
    message_sent = pyqtSignal(object)
    
    def __init__(self, current_user, contact, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.contact = contact
        self.messages = []
        self.pinned_message = None
        self.replying_to = None
        
        # ✅ Защита от пустого имени
        if not self.contact.name:
            self.contact.name = "Пользователь"
        
        self.init_ui()
        self.load_messages()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ШАПКА ЧАТА
        header = self._create_header()
        main_layout.addWidget(header)
        
        # ОБЛАСТЬ СООБЩЕНИЙ
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.messages_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #333;
                border-radius: 3px;
                min-height: 20px;
            }
        """)
        
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()
        
        self.messages_scroll.setWidget(self.messages_container)
        main_layout.addWidget(self.messages_container, 1)
        
        # ПАНЕЛЬ ВВОДА
        input_panel = self._create_input_panel()
        main_layout.addWidget(input_panel)
    
    def _create_header(self):
        """Создаёт шапку чата."""
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_PANEL};
                border-bottom: 1px solid {COLOR_DIVIDER};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Аватар + Имя
        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)
        
        avatar_name = self.contact.name[0].upper() if self.contact.name else "?"
        avatar = QLabel(avatar_name)
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {COLOR_ACCENT};
                color: #FFFFFF;
                border-radius: 20px;
                font-size: 18px;
                font-weight: 600;
            }}
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(avatar)
        
        name_layout = QVBoxLayout()
        name_layout.setSpacing(2)
        
        name_label = QLabel(self.contact.name)
        name_label.setStyleSheet(f"""
            color: {COLOR_TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        """)
        name_layout.addWidget(name_label)
        
        status_label = QLabel("в сети")
        status_label.setStyleSheet("""
            color: #10B981;
            font-size: 13px;
        """)
        name_layout.addWidget(status_label)
        
        info_layout.addLayout(name_layout)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Кнопка меню
        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(40, 40)
        menu_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9CA3AF;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border-radius: 8px;
            }
        """)
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: #FFFFFF;
            }
            QMenu::item:hover {
                background-color: #2A2A2A;
            }
        """)
        
        menu.addAction("🔍 Поиск")
        menu.addAction("🔕 Уведомления")
        menu.addAction("📌 Закреплённые")
        menu.addSeparator()
        menu.addAction("🗑️ Очистить историю")
        menu.addAction("🚫 Удалить чат")
        
        menu_btn.setMenu(menu)
        layout.addWidget(menu_btn)
        
        return header
    
    def _create_input_panel(self):
        """Создаёт панель ввода сообщений."""
        panel = QFrame()
        panel.setFixedHeight(80)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_PANEL};
                border-top: 1px solid {COLOR_DIVIDER};
            }}
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Кнопка прикрепления
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(48, 48)
        attach_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9CA3AF;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border-radius: 24px;
            }
        """)
        attach_btn.clicked.connect(self.on_attach_clicked)
        layout.addWidget(attach_btn)
        
        # Поле ввода
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Написать сообщение...")
        self.input_field.setMaximumHeight(100)
        self.input_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1E1E1E;
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid #333;
                border-radius: 24px;
                padding: 12px 16px;
                font-size: 15px;
                font-family: {FONT_FAMILY};
                selection-background-color: {COLOR_ACCENT};
            }}
            QTextEdit:focus {{
                border: 2px solid {COLOR_ACCENT};
            }}
        """)
        self.input_field.textChanged.connect(self.on_text_changed)
        self.input_field.installEventFilter(self)
        layout.addWidget(self.input_field, 1)
        
        # Кнопка отправки
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(48, 48)
        self.send_btn.setEnabled(False)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                border: none;
                color: #FFFFFF;
                font-size: 20px;
                border-radius: 24px;
            }}
            QPushButton:hover {{
                background-color: #8B5CF6;
            }}
            QPushButton:disabled {{
                background-color: #333;
                color: #666;
            }}
        """)
        self.send_btn.clicked.connect(self.on_send_clicked)
        layout.addWidget(self.send_btn)
        
        return panel
    
    def load_messages(self):
        """Загружает сообщения из базы данных."""
        self.add_test_messages()
    
    def add_test_messages(self):
        """Добавляет тестовые сообщения."""
        test_messages = [
            Message(id='1', from_uid=self.contact.uid, to_uid=self.current_user.uid, text="Привет! Как дела?"),
            Message(id='2', from_uid=self.current_user.uid, to_uid=self.contact.uid, text="Всё отлично!", status=MessageStatus.READ),
        ]
        for msg in test_messages:
            self.add_message_to_ui(msg)
    
    def add_message_to_ui(self, message: Message):
        """Добавляет сообщение в UI."""
        is_own = message.from_uid == self.current_user.uid
        bubble = MessageBubble(message, is_own)
        
        bubble.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        bubble.customContextMenuRequested.connect(lambda pos, m=message: self.show_message_menu(pos, m))
        
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        self.messages.append(message)
        
        # Прокрутка вниз
        self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()
        )
    
    def show_message_menu(self, pos, message: Message):
        """Показывает контекстное меню сообщения."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: #FFFFFF;
            }
            QMenu::item:hover {
                background-color: #2A2A2A;
            }
        """)
        
        reply_action = menu.addAction("↩️ Ответить")
        edit_action = menu.addAction("✏️ Редактировать")
        forward_action = menu.addAction("➡️ Переслать")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Удалить")
        
        action = menu.exec(self.mapToGlobal(pos))
        
        if action == reply_action:
            self.reply_to_message(message)
        elif action == edit_action:
            self.edit_message(message)
        elif action == forward_action:
            self.forward_message(message)
        elif action == delete_action:
            self.delete_message(message)
    
    def on_send_clicked(self):
        """Отправляет сообщение."""
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        
        message = Message(
            id=str(hash(text + str(time.time()))),
            from_uid=self.current_user.uid,
            to_uid=self.contact.uid,
            text=text,
            message_type=MessageType.TEXT,
            status=MessageStatus.SENT
        )
        
        send_message(
            from_uid=self.current_user.uid,
            to_uid=self.contact.uid,
            text=text
        )
        
        self.add_message_to_ui(message)
        self.input_field.clear()
        self.send_btn.setEnabled(False)
        
        # Имитация ответа
        QTimer.singleShot(2000, lambda: self.simulate_reply())
    
    def simulate_reply(self):
        """Имитирует ответ собеседника."""
        import random
        replies = ["Отлично!", "Понял", "Круто!", "👍"]
        message = Message(
            id=str(hash(str(random.random()))),
            from_uid=self.contact.uid,
            to_uid=self.current_user.uid,
            text=random.choice(replies),
            message_type=MessageType.TEXT
        )
        self.add_message_to_ui(message)
    
    def on_text_changed(self):
        """Обрабатывает изменение текста."""
        text = self.input_field.toPlainText().strip()
        self.send_btn.setEnabled(len(text) > 0)
    
    def on_attach_clicked(self):
        """Клик по кнопке прикрепления - открывает меню."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QMenu::item {
                padding: 10px 16px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QMenu::item:hover {
                background-color: #2A2A2A;
            }
        """)
        
        photo_action = menu.addAction("📷 Фото/Видео")
        file_action = menu.addAction("📁 Файл")
        voice_action = menu.addAction("🎤 Голосовое")
        
        action = menu.exec(self.mapToGlobal(self.sender().pos()))
        
        if action == photo_action:
            self.attach_photo()
        elif action == file_action:
            self.attach_file()
        elif action == voice_action:
            self.record_voice()
    
    def attach_photo(self):
        """Прикрепить фото - загрузка в Яндекс.Хранилище."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите фото", "",
            "Images (*.png *.jpg *.jpeg *.gif)"
        )
        if file_path:
            print(f"📷 Фото выбрано: {file_path}")
            
            # ✅ Загружаем в Яндекс.Хранилище
            try:
                from src.database.yandex_storage import yandex_storage
                
                if yandex_storage:
                    file_url = yandex_storage.upload_message_file(
                        self.contact.uid,
                        file_path,
                        os.path.basename(file_path)
                    )
                    
                    if file_url:
                        print(f"✅ Фото загружено в Яндекс: {file_url}")
                        self.send_message(
                            f"📷 Фото",
                            message_type=MessageType.PHOTO,
                            file_url=file_url
                        )
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось загрузить фото")
                else:
                    print("⚠️ Яндекс.Хранилище не инициализировано")
                    self.send_message(
                        f"📷 Фото: {os.path.basename(file_path)}",
                        message_type=MessageType.PHOTO,
                        file_url=file_path
                    )
                    
            except Exception as e:
                print(f"❌ Ошибка загрузки фото: {e}")
                self.send_message(
                    f"📷 Фото: {os.path.basename(file_path)}",
                    message_type=MessageType.PHOTO,
                    file_url=file_path
                )
    
    def attach_file(self):
        """Прикрепить файл - загрузка в Яндекс.Хранилище."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "",
            "All Files (*)"
        )
        if file_path:
            print(f"📁 Файл выбран: {file_path}")
            
            # ✅ Загружаем в Яндекс.Хранилище
            try:
                from src.database.yandex_storage import yandex_storage
                
                if yandex_storage:
                    file_url = yandex_storage.upload_message_file(
                        self.contact.uid,
                        file_path,
                        os.path.basename(file_path)
                    )
                    
                    if file_url:
                        print(f"✅ Файл загружен в Яндекс: {file_url}")
                        self.send_message(
                            f"📁 {os.path.basename(file_path)}",
                            message_type=MessageType.FILE,
                            file_url=file_url
                        )
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось загрузить файл")
                else:
                    print("⚠️ Яндекс.Хранилище не инициализировано")
                    self.send_message(
                        f"📁 {os.path.basename(file_path)}",
                        message_type=MessageType.FILE,
                        file_url=file_path
                    )
                    
            except Exception as e:
                print(f"❌ Ошибка загрузки файла: {e}")
                self.send_message(
                    f"📁 {os.path.basename(file_path)}",
                    message_type=MessageType.FILE,
                    file_url=file_path
                )
    
    def record_voice(self):
        """Записать голосовое."""
        print("🎤 Запись голосового...")
        QMessageBox.information(self, "Голосовое", "Функция записи в разработке")
    
    def send_message(self, text, message_type=MessageType.TEXT, file_url=""):
        """Отправляет сообщение."""
        if not text:
            return
        
        message = Message(
            id=str(hash(text + str(time.time()))),
            from_uid=self.current_user.uid,
            to_uid=self.contact.uid,
            text=text,
            message_type=message_type,
            status=MessageStatus.SENT,
            file_url=file_url
        )
        
        send_message(
            from_uid=self.current_user.uid,
            to_uid=self.contact.uid,
            text=text,
            message_type=message_type,
            file_url=file_url
        )
        
        self.add_message_to_ui(message)
        self.input_field.clear()
        self.send_btn.setEnabled(False)
    
    def reply_to_message(self, message: Message):
        """Ответить на сообщение."""
        self.input_field.setFocus()
        self.input_field.setPlaceholderText(f"↩️ Ответ: {message.text[:30]}...")
        self.replying_to = message
    
    def edit_message(self, message: Message):
        """Редактировать сообщение."""
        if message.from_uid != self.current_user.uid:
            return
        
        new_text, ok = QInputDialog.getText(
            self, "Редактировать сообщение", "",
            text=message.text
        )
        
        if ok and new_text:
            edit_message(message.id, new_text)
            print(f"✏️ Сообщение отредактировано: {new_text}")
    
    def forward_message(self, message: Message):
        """Переслать сообщение."""
        print(f"➡️ Переслать: {message.text}")
        QMessageBox.information(self, "Пересылка", "Функция пересылки в разработке")
    
    def delete_message(self, message: Message):
        """Удалить сообщение."""
        reply = QMessageBox.question(
            self, "Удалить сообщение",
            "Удалить для всех или только для себя?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            delete_message(message.id, for_everyone=True)
            print("🗑️ Сообщение удалено для всех")
        elif reply == QMessageBox.StandardButton.No:
            delete_message(message.id, for_everyone=False)
            print("🗑️ Сообщение удалено для себя")
    
    def eventFilter(self, obj, event):
        """Перехватывает события."""
        from PyQt6.QtCore import QEvent
        
        if obj == self.input_field and event.type() == QEvent.Type.KeyPress:
            from PyQt6.QtGui import QKeyEvent
            key_event = event
            if key_event.key() == Qt.Key.Key_Return and not key_event.modifiers():
                if self.send_btn.isEnabled():
                    self.on_send_clicked()
                return True
        
        return super().eventFilter(obj, event)