"""
Виджет чата для встраивания в главное окно
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QScrollArea, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from src.models.user import User
from src.models.message import Message
from src.database.messages_db import (send_message, get_messages, 
                                       listen_for_messages, mark_as_read,
                                       mark_chat_as_read)
from src.ui.message_bubble import MessageBubble
from src.ui.avatar_widget import AvatarWidget
from src.utils.settings import (
    COLOR_BACKGROUND, COLOR_PANEL, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_DIVIDER, COLOR_ACCENT, COLOR_ACCENT_HOVER, FONT_FAMILY, 
    FONT_SIZE_NAME, INPUT_BORDER_RADIUS, BUTTON_BORDER_RADIUS,
    COLOR_INPUT_BG, COLOR_INPUT_BORDER, COLOR_ONLINE
)


class ChatWidget(QWidget):
    """Виджет чата для встраивания в главное окно."""
    
    message_sent = pyqtSignal()
    
    def __init__(self, current_user, contact, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.contact = contact
        self.message_listener = None
        self.typing_timer = QTimer()
        self.typing_timer.setInterval(2000)
        self.typing_timer.timeout.connect(self.stop_typing)
        self.is_recording = False
        
        # Инициализируем атрибуты ДО использования
        self.messages_layout = None
        self.scroll = None
        self.message_input = None
        
        self.init_ui()
        self.load_messages()
        self.listen_for_messages()
        
    def init_ui(self):
        """Инициализация интерфейса."""
        try:
            self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
            
            # Основной макет
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # === ШАПКА ===
            # Создаём QWidget для шапки чтобы применить стиль
            header_widget = QWidget()
            header_widget.setStyleSheet(f"background-color: {COLOR_PANEL}; border-bottom: 1px solid {COLOR_DIVIDER};")
            header = QHBoxLayout(header_widget)
            header.setContentsMargins(15, 12, 15, 12)
            
            # Аватарка
            avatar = AvatarWidget(self.contact.name, self.contact.avatar_url, 40)
            header.addWidget(avatar)
            
            # Имя и статус
            info = QVBoxLayout()
            info.setContentsMargins(10, 0, 0, 0)
            name_label = QLabel(self.contact.name)
            name_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_NAME, QFont.Weight.Bold))
            name_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            self.status_label = QLabel(self.contact.get_online_status())
            self.status_label.setStyleSheet(f"color: {COLOR_ONLINE}; font-size: 12px;")
            info.addWidget(name_label)
            info.addWidget(self.status_label)
            header.addLayout(info)
            header.addStretch()
            
            main_layout.addWidget(header_widget)
            
            # === ОБЛАСТЬ СООБЩЕНИЙ ===
            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setStyleSheet(f"""
                QScrollArea {{
                    border: none;
                    background-color: {COLOR_BACKGROUND};
                }}
            """)
            
            self.messages_container = QWidget()
            self.messages_layout = QVBoxLayout(self.messages_container)
            self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.messages_layout.setSpacing(5)
            self.messages_layout.setContentsMargins(15, 15, 15, 15)
            
            self.scroll.setWidget(self.messages_container)
            main_layout.addWidget(self.scroll, 1)
            
            # === ПАНЕЛЬ ВВОДА ===
            input_widget = QWidget()
            input_widget.setStyleSheet(f"background-color: {COLOR_PANEL};")
            input_panel = QHBoxLayout(input_widget)
            input_panel.setContentsMargins(15, 15, 15, 15)
            
            # Кнопка прикрепления
            self.attach_btn = QPushButton("📎")
            self.attach_btn.setFixedSize(44, 44)
            self.attach_btn.setToolTip("Прикрепить файл")
            self.attach_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT_SECONDARY};
                    border: none;
                    font-size: 20px;
                    border-radius: 22px;
                }}
                QPushButton:hover {{ 
                    background-color: {COLOR_DIVIDER}; 
                    color: {COLOR_TEXT_PRIMARY};
                }}
            """)
            self.attach_btn.clicked.connect(self.attach_file)
            input_panel.addWidget(self.attach_btn)
            
            # Поле ввода текста
            self.message_input = QTextEdit()
            self.message_input.setPlaceholderText("Написать сообщение...")
            self.message_input.setMaximumHeight(100)
            self.message_input.setMinimumHeight(44)
            self.message_input.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {COLOR_INPUT_BG};
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid {COLOR_INPUT_BORDER};
                    border-radius: {INPUT_BORDER_RADIUS}px;
                    padding: 10px 16px;
                    font-size: 15px;
                    font-family: {FONT_FAMILY};
                }}
                QTextEdit:focus {{
                    border: 2px solid {COLOR_ACCENT};
                }}
            """)
            self.message_input.textChanged.connect(self.on_text_changed)
            input_panel.addWidget(self.message_input, 1)
            
            # Кнопка отправки
            self.send_btn = QPushButton("➤")
            self.send_btn.setFixedSize(44, 44)
            self.send_btn.setToolTip("Отправить сообщение")
            self.send_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT};
                    color: white;
                    border: none;
                    border-radius: 22px;
                    font-size: 18px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
                QPushButton:hover {{ 
                    background-color: {COLOR_ACCENT_HOVER}; 
                }}
            """)
            self.send_btn.clicked.connect(self.send_message)
            input_panel.addWidget(self.send_btn)
            
            # Кнопка голоса
            self.voice_btn = QPushButton("🎤")
            self.voice_btn.setFixedSize(44, 44)
            self.voice_btn.setToolTip("Записать голосовое")
            self.voice_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_DIVIDER};
                    color: {COLOR_TEXT_PRIMARY};
                    border: none;
                    border-radius: 22px;
                    font-size: 18px;
                }}
                QPushButton:hover {{ 
                    background-color: {COLOR_TEXT_SECONDARY};
                    color: white;
                }}
            """)
            self.voice_btn.setCheckable(True)
            self.voice_btn.toggled.connect(self.toggle_voice_recording)
            input_panel.addWidget(self.voice_btn)
            
            main_layout.addWidget(input_widget)
            
            self.setLayout(main_layout)
            self.message_input.installEventFilter(self)
            
        except Exception as e:
            print(f"Ошибка инициализации виджета чата: {e}")
            import traceback
            traceback.print_exc()
    
    def eventFilter(self, obj, event):
        """Перехватывает нажатие Enter."""
        from PyQt6.QtCore import QEvent, Qt
        if obj == self.message_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def on_text_changed(self):
        """Обработчик изменения текста."""
        try:
            if self.typing_timer:
                text = self.message_input.toPlainText().strip()
                if text:
                    self.typing_timer.start()
                else:
                    self.stop_typing()
        except Exception:
            pass
    
    def stop_typing(self):
        """Останавливает статус 'печатает'."""
        if self.typing_timer:
            self.typing_timer.stop()
    
    def attach_file(self):
        """Открывает диалог выбора файла."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите файл",
                "",
                "Все файлы (*);;Изображения (*.png *.jpg *.jpeg);;Документы (*.pdf *.doc);;Видео (*.mp4 *.avi)"
            )
            
            if file_path:
                QMessageBox.information(self, "Файл", f"Файл выбран: {file_path}\n(Загрузка будет в следующей версии)")
        except Exception as e:
            print(f"Ошибка прикрепления файла: {e}")
    
    def toggle_voice_recording(self, checked):
        """Переключает режим записи голоса."""
        try:
            self.is_recording = checked
            if checked:
                self.voice_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_ACCENT};
                        color: white;
                        border: none;
                        border-radius: 22px;
                        font-size: 18px;
                    }}
                """)
            else:
                self.voice_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_DIVIDER};
                        color: {COLOR_TEXT_PRIMARY};
                        border: none;
                        border-radius: 22px;
                        font-size: 18px;
                    }}
                """)
        except Exception as e:
            print(f"Ошибка записи голоса: {e}")
    
    def load_messages(self):
        """Загружает историю переписки."""
        try:
            # Проверяем что атрибуты инициализированы
            if self.messages_layout is None:
                print("Ошибка: messages_layout не инициализирован")
                return
                
            # Очищаем контейнер
            while self.messages_layout.count():
                item = self.messages_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Получаем сообщения
            messages_data = get_messages(self.current_user.uid, self.contact.uid)
            
            for msg_data in messages_data:
                msg = Message.from_dict(msg_data, msg_data.get('id'))
                is_self = msg.from_uid == self.current_user.uid
                
                bubble = MessageBubble(msg, is_self)
                self.messages_layout.addWidget(bubble)
            
            # Прокручиваем вниз
            if self.scroll:
                self.scroll.verticalScrollBar().setValue(
                    self.scroll.verticalScrollBar().maximum()
                )
            
            self.mark_messages_read()
            
        except Exception as e:
            print(f"Ошибка загрузки сообщений: {e}")
    
    def send_message(self):
        """Отправляет новое сообщение."""
        try:
            if self.message_input is None:
                return
                
            text = self.message_input.toPlainText().strip()
            
            if not text:
                return
            
            msg_id = send_message(
                from_uid=self.current_user.uid,
                to_uid=self.contact.uid,
                text=text
            )
            
            if msg_id:
                from datetime import datetime
                msg = Message(
                    id=msg_id,
                    from_uid=self.current_user.uid,
                    to_uid=self.contact.uid,
                    text=text,
                    timestamp=datetime.now(),
                    delivered=True
                )
                
                bubble = MessageBubble(msg, is_self=True)
                if self.messages_layout:
                    self.messages_layout.addWidget(bubble)
                
                self.message_input.clear()
                
                if self.scroll:
                    self.scroll.verticalScrollBar().setValue(
                        self.scroll.verticalScrollBar().maximum()
                    )
                
                self.stop_typing()
                self.message_sent.emit()
                
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
    
    def listen_for_messages(self):
        """Подписывается на новые сообщения."""
        try:
            def on_new_message(msg_data):
                if msg_data['from_uid'] == self.current_user.uid:
                    return
                
                msg = Message.from_dict(msg_data, msg_data.get('id'))
                bubble = MessageBubble(msg, is_self=False)
                
                if self.messages_layout:
                    self.messages_layout.addWidget(bubble)
                
                if self.scroll:
                    self.scroll.verticalScrollBar().setValue(
                        self.scroll.verticalScrollBar().maximum()
                    )
                
                if msg.id:
                    mark_as_read(msg.id)
                
                self.message_sent.emit()
            
            self.message_listener = listen_for_messages(
                user_uid=self.current_user.uid,
                callback=on_new_message
            )
        except Exception as e:
            print(f"Ошибка подписки на сообщения: {e}")
    
    def mark_messages_read(self):
        """Отмечает сообщения как прочитанные."""
        try:
            mark_chat_as_read(self.current_user.uid, self.contact.uid)
        except Exception as e:
            print(f"Ошибка mark_messages_read: {e}")
    
    def closeEvent(self, event):
        """Отписывается от слушателя при закрытии."""
        try:
            if self.message_listener and callable(self.message_listener):
                self.message_listener()
            self.stop_typing()
            event.accept()
        except Exception:
            event.accept()