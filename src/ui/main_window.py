"""
Главное окно мессенджера со списком контактов
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.models.user import User
from src.database.users_db import get_all_users, set_online_status
from src.ui.chat_widget import ChatWidget
from src.ui.contact_item import ContactItem
from src.ui.settings_window import SettingsWindow
from src.utils.settings import (
    COLOR_BACKGROUND, COLOR_PANEL, COLOR_TEXT_PRIMARY, COLOR_DIVIDER,
    FONT_FAMILY, INPUT_BORDER_RADIUS, COLOR_INPUT_BG, COLOR_INPUT_BORDER,
    COLOR_ACCENT
)


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.message_listener = None
        self.settings_window = None
        self.current_chat_widget = None
        self.contacts_list = None  # Инициализируем атрибут
        self.init_ui()
        self.load_contacts()
        
        set_online_status(self.current_user.uid, "online")
        
    def init_ui(self):
        """Инициализация интерфейса."""
        try:
            self.setWindowTitle(f"Ten Dem — {self.current_user.name}")
            self.setMinimumSize(1200, 800)
            self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
            
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QHBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # === ЛЕВАЯ ПАНЕЛЬ: Контакты ===
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
            
            # Шапка левой панели
            header = QHBoxLayout()
            header.setContentsMargins(20, 20, 20, 15)
            
            title = QLabel("Ten Dem")
            title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
            title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            header.addWidget(title)
            
            header.addStretch()
            
            # Кнопка настроек
            settings_btn = QPushButton("⚙")
            settings_btn.setFixedSize(40, 40)
            settings_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    font-size: 22px;
                    color: {COLOR_TEXT_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {COLOR_DIVIDER};
                    border-radius: 20px;
                }}
            """)
            settings_btn.clicked.connect(self.open_settings)
            header.addWidget(settings_btn)
            
            left_layout.addLayout(header)
            
            # Поиск
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
                QLineEdit:focus {{
                    border: 2px solid {COLOR_ACCENT};
                }}
            """)
            search_input.textChanged.connect(self.filter_contacts)
            left_layout.addWidget(search_input)
            
            # Список контактов
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
                QListWidget::item:selected {{
                    background-color: {COLOR_DIVIDER};
                }}
            """)
            self.contacts_list.itemClicked.connect(self.open_chat)
            left_layout.addWidget(self.contacts_list)
            
            main_layout.addWidget(left_panel)
            
            # === ПРАВАЯ ПАНЕЛЬ: Область чата ===
            self.right_panel = QWidget()
            self.right_panel.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
            right_layout = QVBoxLayout(self.right_panel)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)
            
            # Заглушка (показываем когда чат не выбран)
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
            
        except Exception as e:
            print(f"Ошибка инициализации главного окна: {e}")
            import traceback
            traceback.print_exc()
    
    def load_contacts(self):
        """Загружает список контактов."""
        try:
            if self.contacts_list is None:
                print("Ошибка: contacts_list не инициализирован")
                return
                
            self.contacts_list.clear()
            
            all_users = get_all_users()
            
            for user_data in all_users:
                if user_data['uid'] == self.current_user.uid:
                    continue
                
                user = User.from_dict(user_data, user_data['uid'])
                
                item = QListWidgetItem(self.contacts_list)
                contact_widget = ContactItem(user)
                item.setSizeHint(contact_widget.sizeHint())
                self.contacts_list.addItem(item)
                self.contacts_list.setItemWidget(item, contact_widget)
        except Exception as e:
            print(f"Ошибка загрузки контактов: {e}")
            import traceback
            traceback.print_exc()
    
    def filter_contacts(self, text):
        """Фильтрует контакты по поиску."""
        try:
            if self.contacts_list is None:
                return
                
            for i in range(self.contacts_list.count()):
                item = self.contacts_list.item(i)
                widget = self.contacts_list.itemWidget(item)
                if widget and hasattr(widget, 'user'):
                    if text.lower() in widget.user.name.lower():
                        item.setHidden(False)
                    else:
                        item.setHidden(True)
        except Exception:
            pass
    
    def open_chat(self, item):
        """Открывает чат в правой панели."""
        try:
            contact_widget = self.contacts_list.itemWidget(item)
            if not contact_widget or not hasattr(contact_widget, 'user'):
                return
            
            contact = contact_widget.user
            
            # Удаляем заглушку
            if self.placeholder_widget:
                self.placeholder_widget.deleteLater()
                self.placeholder_widget = None
            
            # Удаляем предыдущий чат если есть
            if self.current_chat_widget:
                self.current_chat_widget.deleteLater()
            
            # Создаём новый виджет чата
            self.current_chat_widget = ChatWidget(self.current_user, contact)
            
            # Добавляем в правую панель
            right_layout = self.right_panel.layout()
            right_layout.addWidget(self.current_chat_widget)
            
            # Подключаем сигнал обновления
            self.current_chat_widget.message_sent.connect(self.refresh_contacts)
            
        except Exception as e:
            print(f"Ошибка открытия чата: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_contacts(self):
        """Обновляет список контактов."""
        try:
            self.load_contacts()
        except Exception:
            pass
    
    def open_settings(self):
        """Открывает окно настроек."""
        try:
            self.settings_window = SettingsWindow(self.current_user)
            self.settings_window.show()
        except Exception as e:
            print(f"Ошибка открытия настроек: {e}")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        try:
            set_online_status(self.current_user.uid, "offline")
            
            if self.message_listener and callable(self.message_listener):
                self.message_listener()
            
            if self.current_chat_widget:
                self.current_chat_widget.close()
            
            event.accept()
        except Exception:
            event.accept()