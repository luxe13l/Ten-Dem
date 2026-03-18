"""
Главное окно мессенджера Ten Dem
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QLineEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from src.models.user import User
from src.database.users_db import get_all_users, set_online_status
from src.ui.chat_widget import ChatWidget
from src.ui.contact_item import ContactItem

# ЗАПАСНЫЕ ЦВЕТА (если settings не загрузился)
try:
    from src.utils.settings import (
        COLOR_BACKGROUND, COLOR_PANEL, COLOR_TEXT_PRIMARY, COLOR_DIVIDER,
        FONT_FAMILY, INPUT_BORDER_RADIUS, COLOR_INPUT_BG, COLOR_INPUT_BORDER,
        COLOR_ACCENT
    )
except ImportError:
    COLOR_BACKGROUND = '#0A0A0A'
    COLOR_PANEL = '#141414'
    COLOR_TEXT_PRIMARY = '#FFFFFF'
    COLOR_DIVIDER = '#2A2A2A'
    FONT_FAMILY = 'Segoe UI'
    INPUT_BORDER_RADIUS = 12
    COLOR_INPUT_BG = '#1E1E1E'
    COLOR_INPUT_BORDER = '#333333'
    COLOR_ACCENT = '#7C3AED'


class MainWindow(QMainWindow):
    """Главное окно мессенджера."""
    
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.current_chat_widget = None
        self.contacts_list = None
        print(f"🔵 Инициализация MainWindow для {current_user.name}...")
        self.init_ui()
        set_online_status(self.current_user.uid, "online")
        print("✅ MainWindow инициализировано")
    
    def init_ui(self):
        """Инициализация интерфейса."""
        try:
            self.setWindowTitle(f"Ten Dem — {self.current_user.name}")
            self.setMinimumSize(1200, 800)
            self.resize(1200, 800)
            self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
            
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QHBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # ЛЕВАЯ ПАНЕЛЬ
            left_panel = QWidget()
            left_panel.setFixedWidth(380)
            left_panel.setStyleSheet(f"""
                QWidget {{
                    background-color: {COLOR_PANEL};
                    border-right: 1px solid {COLOR_DIVIDER};
                }}
            """)
            left_layout = QVBoxLayout(left_panel)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(0)
            
            header = QHBoxLayout()
            header.setContentsMargins(20, 20, 20, 15)
            
            title = QLabel("Ten Dem")
            title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
            title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            header.addWidget(title)
            header.addStretch()
            
            settings_btn = QPushButton("⚙")
            settings_btn.setFixedSize(40, 40)
            settings_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    font-size: 22px;
                    color: {COLOR_TEXT_PRIMARY};
                }}
            """)
            header.addWidget(settings_btn)
            left_layout.addLayout(header)
            
            search_input = QLineEdit()
            search_input.setPlaceholderText("Поиск контактов...")
            search_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLOR_INPUT_BG};
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid {COLOR_INPUT_BORDER};
                    border-radius: {INPUT_BORDER_RADIUS}px;
                    padding: 10px 16px;
                    font-size: 14px;
                    font-family: {FONT_FAMILY};
                    margin: 0 16px 16px;
                }}
            """)
            search_input.textChanged.connect(self.filter_contacts)
            left_layout.addWidget(search_input)
            
            self.contacts_list = QListWidget()
            self.contacts_list.setStyleSheet(f"""
                QListWidget {{
                    background-color: transparent;
                    border: none;
                    outline: none;
                }}
                QListWidget::item {{
                    padding: 5px;
                    border-radius: 8px;
                    margin: 0 8px;
                }}
                QListWidget::item:hover {{
                    background-color: {COLOR_DIVIDER};
                }}
            """)
            self.contacts_list.itemClicked.connect(self.open_chat)
            left_layout.addWidget(self.contacts_list)
            
            main_layout.addWidget(left_panel)
            
            # ПРАВАЯ ПАНЕЛЬ
            self.right_panel = QWidget()
            self.right_panel.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
            right_layout = QVBoxLayout(self.right_panel)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)
            
            self.placeholder_widget = QWidget()
            placeholder_layout = QVBoxLayout(self.placeholder_widget)
            placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            placeholder_icon = QLabel("💬")
            placeholder_icon.setStyleSheet("font-size: 64px;")
            placeholder_layout.addWidget(placeholder_icon)
            
            placeholder_text = QLabel("Выберите чат для начала общения")
            placeholder_text.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 18px; font-family: {FONT_FAMILY};")
            placeholder_layout.addWidget(placeholder_text)
            
            right_layout.addWidget(self.placeholder_widget)
            main_layout.addWidget(self.right_panel, 1)
            
            print("✅ UI инициализирован")
            
        except Exception as e:
            print(f"❌ Ошибка init_ui: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def load_contacts(self):
        """Загружает контакты с таймаутом 10 секунд (чтобы не висело)."""
        try:
            print("🟢 Загрузка контактов...")
            if self.contacts_list is None:
                return
            self.contacts_list.clear()
            
            # ✅ ТАЙМАУТ 10 СЕКУНД
            import threading
            result = [None]
            error = [None]
            
            def fetch_users():
                try:
                    all_users = get_all_users()
                    result[0] = all_users
                except Exception as e:
                    error[0] = e
            
            thread = threading.Thread(target=fetch_users)
            thread.daemon = True
            thread.start()
            thread.join(timeout=10)  # ✅ Ждём максимум 10 секунд
            
            # ✅ Если ошибка или таймаут
            if error[0]:
                print(f"⚠️ Firebase не ответил за 10 сек: {error[0]}")
                self._show_test_contacts()
                return
            
            if result[0]:
                all_users = result[0]
                for user_data in all_users:
                    if user_data['uid'] == self.current_user.uid:
                        continue
                    user = User.from_dict(user_data, user_data['uid'])
                    item = QListWidgetItem(self.contacts_list)
                    contact_widget = ContactItem(user)
                    item.setSizeHint(contact_widget.sizeHint())
                    self.contacts_list.addItem(item)
                    self.contacts_list.setItemWidget(item, contact_widget)
                
                print(f"✅ Загружено контактов: {len(all_users) - 1}")
            else:
                print("⚠️ Контакты не загружены, показываем заглушку")
                self._show_test_contacts()
                
        except Exception as e:
            print(f"❌ Ошибка load_contacts: {e}")
            import traceback
            traceback.print_exc()
            self._show_test_contacts()
    
    def _show_test_contacts(self):
        """Показывает тестовые контакты если Firebase не работает."""
        print("🧪 Показываем тестовые контакты...")
        
        test_users = [
            {'uid': 'test1', 'name': 'Алексей', 'phone': '+79991111111', 'status': 'online'},
            {'uid': 'test2', 'name': 'Мария', 'phone': '+79992222222', 'status': 'offline'},
            {'uid': 'test3', 'name': 'Дмитрий', 'phone': '+79993333333', 'status': 'online'},
            {'uid': 'test4', 'name': 'Елена', 'phone': '+79994444444', 'status': 'offline'},
            {'uid': 'test5', 'name': 'Андрей', 'phone': '+79995555555', 'status': 'online'},
        ]
        
        for user_data in test_users:
            user = User.from_dict(user_data, user_data['uid'])
            item = QListWidgetItem(self.contacts_list)
            contact_widget = ContactItem(user)
            item.setSizeHint(contact_widget.sizeHint())
            self.contacts_list.addItem(item)
            self.contacts_list.setItemWidget(item, contact_widget)
        
        print(f"✅ Показано тестовых контактов: {len(test_users)}")
    
    def filter_contacts(self, text):
        """Фильтрует контакты по поиску."""
        try:
            if self.contacts_list is None:
                return
            for i in range(self.contacts_list.count()):
                item = self.contacts_list.item(i)
                widget = self.contacts_list.itemWidget(item)
                if widget and hasattr(widget, 'user'):
                    item.setHidden(text.lower() not in widget.user.name.lower())
        except Exception:
            pass
    
    def open_chat(self, item):
        """Открывает чат с контактом."""
        try:
            contact_widget = self.contacts_list.itemWidget(item)
            if not contact_widget or not hasattr(contact_widget, 'user'):
                return
            
            contact = contact_widget.user
            
            if self.placeholder_widget:
                self.placeholder_widget.deleteLater()
                self.placeholder_widget = None
            
            if self.current_chat_widget:
                self.current_chat_widget.deleteLater()
            
            self.current_chat_widget = ChatWidget(self.current_user, contact)
            right_layout = self.right_panel.layout()
            right_layout.addWidget(self.current_chat_widget)
            
            print(f"✅ Чат открыт: {contact.name}")
        except Exception as e:
            print(f"❌ Ошибка open_chat: {e}")
            import traceback
            traceback.print_exc()
    
    def closeEvent(self, event):
        """Обработка закрытия окна."""
        try:
            set_online_status(self.current_user.uid, "offline")
            if self.current_chat_widget:
                self.current_chat_widget.close()
            event.accept()
        except Exception:
            event.accept()