"""
Клиент мессенджера на PyQt6 и Firebase Firestore.

Для работы необходим файл сервисного аккаунта Firebase (firebase-key.json),
который можно скачать в консоли Firebase: Project settings → Service accounts → Generate new private key.

Установка зависимостей:
    pip install PyQt6 firebase-admin

Запуск:
    python client.py

При входе указывается имя пользователя. Все сообщения сохраняются в коллекции "messages" с полем room="general".
Список контактов формируется из коллекции "users" (все, кто когда-либо входил).
"""

import sys
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QTextBrowser, QLineEdit,
    QPushButton, QDialog, QLabel, QLineEdit as QLineEditDialog, QMessageBox
)

# ==================== НАСТРОЙКА FIREBASE ====================
# Путь к файлу сервисного аккаунта (JSON)
FIREBASE_CREDENTIALS = "firebase-key.json"

# Инициализация Firebase Admin SDK
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ==================== ПОТОК ДЛЯ СЛУШАТЕЛЯ СООБЩЕНИЙ ====================
class MessageListenerThread(QThread):
    """
    Поток, который подписывается на новые сообщения в коллекции messages
    и испускает сигнал с каждым новым сообщением.
    """
    new_message = pyqtSignal(dict)

    def __init__(self, db, room="general"):
        super().__init__()
        self.db = db
        self.room = room
        self._running = True
        self._snapshot = None

    def run(self):
        # Функция обратного вызова при изменении коллекции
        def on_snapshot(doc_snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'ADDED':  # Новое сообщение
                    doc_dict = change.document.to_dict()
                    doc_dict['id'] = change.document.id
                    # Преобразуем Timestamp в datetime для удобства
                    if 'timestamp' in doc_dict and doc_dict['timestamp']:
                        ts = doc_dict['timestamp']
                        if hasattr(ts, 'datetime'):
                            doc_dict['datetime'] = ts.datetime
                    self.new_message.emit(doc_dict)

        # Запрашиваем только сообщения из нужной комнаты, сортируем по времени
        query = self.db.collection('messages').where('room', '==', self.room).order_by('timestamp')
        self._snapshot = query.on_snapshot(on_snapshot)

        # Держим поток живым
        while self._running:
            self.msleep(500)

    def stop(self):
        self._running = False
        if self._snapshot:
            self._snapshot.unsubscribe()
        self.quit()
        self.wait()

# ==================== ДИАЛОГ ВХОДА ====================
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.user_name = None  # здесь сохранится имя после успешного входа
        self.setWindowTitle("Вход в мессенджер")
        self.setFixedSize(300, 150)
        self.setModal(True)

        layout = QVBoxLayout()

        label = QLabel("Введите ваше имя:")
        self.edit_name = QLineEditDialog()
        self.edit_name.setPlaceholderText("Например, Иван")

        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.handle_login)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")

        layout.addWidget(label)
        layout.addWidget(self.edit_name)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def handle_login(self):
        name = self.edit_name.text().strip()
        if not name:
            self.status_label.setText("Имя не может быть пустым")
            return

        # Проверяем, есть ли пользователь в коллекции users
        user_ref = db.collection('users').document(name)  # используем имя как ID для простоты
        user_doc = user_ref.get()

        if not user_doc.exists:
            # Если нет, создаём нового пользователя
            user_ref.set({
                'name': name,
                'created_at': firestore.SERVER_TIMESTAMP
            })
        else:
            # Если уже есть, можно обновить время последнего входа
            user_ref.update({
                'last_seen': firestore.SERVER_TIMESTAMP
            })

        self.user_name = name
        self.accept()

# ==================== ГЛАВНОЕ ОКНО ====================
class MainWindow(QMainWindow):
    def __init__(self, user_name):
        super().__init__()
        self.user_name = user_name
        self.messages_listener = None
        self.message_ids = set()  # для избежания дубликатов

        self.setWindowTitle(f"Мессенджер — {self.user_name}")
        self.setMinimumSize(800, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Сплиттер для разделения списка контактов и чата
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Левая панель — список контактов (все пользователи, кроме себя)
        self.contacts_list = QListWidget()
        self.contacts_list.setMaximumWidth(250)
        self.contacts_list.setMinimumWidth(200)
        self.contacts_list.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:selected {
                background-color: #cce5ff;
            }
        """)
        splitter.addWidget(self.contacts_list)

        # Правая панель — чат
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)

        # Область сообщений (QTextBrowser)
        self.messages_display = QTextBrowser()
        self.messages_display.setOpenExternalLinks(False)
        self.messages_display.setReadOnly(True)
        self.messages_display.setStyleSheet("""
            QTextBrowser {
                background-color: #e5ddd5;
                border: none;
                font-size: 14px;
                padding: 10px;
            }
        """)
        chat_layout.addWidget(self.messages_display)

        # Нижняя панель ввода
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Напишите сообщение...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: white;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("➤")
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2481CC;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1a5a8c;
            }
        """)
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        chat_layout.addLayout(input_layout)

        splitter.addWidget(chat_widget)
        splitter.setSizes([200, 600])

        # Загружаем список контактов
        self.load_contacts()

        # Загружаем историю сообщений
        self.load_message_history()

        # Запускаем слушатель новых сообщений
        self.start_message_listener()

    def load_contacts(self):
        """Загружает список всех пользователей из Firestore (кроме текущего)."""
        users_ref = db.collection('users')
        users = users_ref.stream()
        self.contacts_list.clear()
        for user in users:
            if user.id != self.user_name:  # user.id — это имя (документ назван по имени)
                data = user.to_dict()
                display_name = data.get('name', user.id)
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, user.id)
                self.contacts_list.addItem(item)

    def load_message_history(self):
        """Загружает все сообщения из комнаты general и отображает их."""
        messages_ref = db.collection('messages').where('room', '==', 'general').order_by('timestamp')
        messages = messages_ref.stream()
        self.messages_display.clear()
        self.message_ids.clear()
        for msg in messages:
            msg_dict = msg.to_dict()
            msg_dict['id'] = msg.id
            self.message_ids.add(msg.id)
            # Преобразуем Timestamp в datetime
            if 'timestamp' in msg_dict and msg_dict['timestamp']:
                ts = msg_dict['timestamp']
                if hasattr(ts, 'datetime'):
                    msg_dict['datetime'] = ts.datetime
            self.display_message(msg_dict)

    def start_message_listener(self):
        """Запускает поток для прослушивания новых сообщений."""
        self.messages_listener = MessageListenerThread(db, room="general")
        self.messages_listener.new_message.connect(self.on_new_message)
        self.messages_listener.start()

    def stop_message_listener(self):
        if self.messages_listener:
            self.messages_listener.stop()
            self.messages_listener = None

    def on_new_message(self, msg_data):
        """Обрабатывает новое сообщение от слушателя."""
        if msg_data['id'] not in self.message_ids:
            self.message_ids.add(msg_data['id'])
            self.display_message(msg_data)

    def display_message(self, msg_data):
        """
        Отображает одно сообщение в QTextBrowser с форматированием в стиле Telegram.
        """
        sender = msg_data.get('from', 'Неизвестный')
        text = msg_data.get('text', '')
        is_me = (sender == self.user_name)

        # Определяем стиль сообщения
        if is_me:
            bubble_color = "#2481CC"  # синий
            text_color = "white"
            alignment = "right"
            float_style = "right"
            # Имя отправителя не показываем для своих сообщений
            sender_html = ""
        else:
            bubble_color = "#F1F3F5"  # серый
            text_color = "black"
            alignment = "left"
            float_style = "left"
            sender_html = f"<div style='font-size: 12px; color: #666; margin-bottom: 3px; text-align: left;'>{sender}</div>"

        # Время сообщения
        time_str = ""
        if 'datetime' in msg_data:
            time_str = msg_data['datetime'].strftime("%H:%M")
        elif 'timestamp' in msg_data and msg_data['timestamp']:
            ts = msg_data['timestamp']
            if hasattr(ts, 'datetime'):
                time_str = ts.datetime.strftime("%H:%M")

        # Формируем HTML для сообщения
        message_html = f"""
        <div style='margin-bottom: 15px; overflow: hidden;'>
            {sender_html}
            <div style='background-color: {bubble_color}; color: {text_color};
                        border-radius: 15px; padding: 8px 12px;
                        max-width: 70%; float: {float_style}; clear: both;'>
                {text}
            </div>
            <div style='font-size: 11px; color: #999; text-align: {alignment};
                        margin-top: 3px; clear: both;'>
                {time_str}
            </div>
        </div>
        """

        # Добавляем в конец QTextBrowser
        cursor = self.messages_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.messages_display.setTextCursor(cursor)
        self.messages_display.insertHtml(message_html)
        # Прокрутка вниз
        scrollbar = self.messages_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        """Отправляет сообщение в Firestore."""
        text = self.message_input.text().strip()
        if not text:
            return

        # Данные сообщения
        message_data = {
            'from': self.user_name,
            'text': text,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'room': 'general'
        }

        # Сохраняем в Firestore
        db.collection('messages').add(message_data)

        # Очищаем поле ввода
        self.message_input.clear()

    def closeEvent(self, event):
        """При закрытии окна останавливаем слушатель."""
        self.stop_message_listener()
        event.accept()

# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================
def main():
    app = QApplication(sys.argv)

    # Диалог входа
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        user_name = login_dialog.user_name
        window = MainWindow(user_name)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()