"""
Окно настроек мессенджера Ten Dem
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCheckBox, QScrollArea, QWidget,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.models.user import User
from src.database.users_db import update_user
from src.ui.avatar_widget import AvatarWidget
from src.utils.settings import (
    COLOR_BACKGROUND, COLOR_PANEL, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_DIVIDER, COLOR_ACCENT, FONT_FAMILY, AVATAR_SIZE_SETTINGS,
    COLOR_ERROR, BUTTON_BORDER_RADIUS
)


class SettingsWindow(QDialog):
    """Окно настроек пользователя."""
    
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса."""
        try:
            self.setWindowTitle("Настройки — Ten Dem")
            self.setMinimumSize(500, 650)
            self.setModal(True)
            self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
            
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # === ШАПКА ===
            header = QHBoxLayout()
            header.setContentsMargins(20, 15, 20, 15)
            header.setStyleSheet(f"background-color: {COLOR_PANEL}; border-bottom: 1px solid {COLOR_DIVIDER};")
            
            back_btn = QPushButton("←")
            back_btn.setFixedSize(40, 40)
            back_btn.clicked.connect(self.close)
            back_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT_PRIMARY};
                    border: none;
                    border-radius: 20px;
                    font-size: 22px;
                }}
                QPushButton:hover {{ 
                    background-color: {COLOR_DIVIDER}; 
                }}
            """)
            header.addWidget(back_btn)
            
            title = QLabel("Настройки")
            title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
            title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            header.addWidget(title)
            
            header.addStretch()
            layout.addLayout(header)
            
            # === КОНТЕНТ ===
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet(f"""
                QScrollArea {{
                    border: none;
                    background-color: {COLOR_BACKGROUND};
                }}
            """)
            
            content = QWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(20)
            
            # === ПРОФИЛЬ ===
            profile_section = QWidget()
            profile_section.setStyleSheet(f"background-color: {COLOR_PANEL}; border-radius: 12px;")
            profile_layout = QVBoxLayout(profile_section)
            profile_layout.setContentsMargins(20, 20, 20, 20)
            profile_layout.setSpacing(15)
            
            # Аватарка
            self.avatar = AvatarWidget(self.current_user.name, self.current_user.avatar_url, AVATAR_SIZE_SETTINGS)
            self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            profile_layout.addWidget(self.avatar)
            
            # Имя
            name_label = QLabel(self.current_user.name)
            name_label.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            profile_layout.addWidget(name_label)
            
            # Телефон
            phone_label = QLabel(self.current_user.phone)
            phone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            phone_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
            profile_layout.addWidget(phone_label)
            
            # Кнопка редактирования
            edit_btn = QPushButton("Редактировать профиль")
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_ACCENT};
                    border: 1px solid {COLOR_ACCENT};
                    border-radius: {BUTTON_BORDER_RADIUS}px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-family: {FONT_FAMILY};
                }}
                QPushButton:hover {{ 
                    background-color: {COLOR_ACCENT}; 
                    color: white; 
                }}
            """)
            edit_btn.clicked.connect(self.edit_profile)
            profile_layout.addWidget(edit_btn)
            
            content_layout.addWidget(profile_section)
            
            # === НАСТРОЙКИ ===
            settings_section = QWidget()
            settings_section.setStyleSheet(f"background-color: {COLOR_PANEL}; border-radius: 12px;")
            settings_layout = QVBoxLayout(settings_section)
            settings_layout.setContentsMargins(20, 20, 20, 20)
            settings_layout.setSpacing(15)
            
            # Уведомления
            notifications_check = QCheckBox("Уведомления")
            notifications_check.setFont(QFont(FONT_FAMILY, 15))
            notifications_check.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            notifications_check.setChecked(True)
            settings_layout.addWidget(notifications_check)
            
            # Звук сообщений
            sound_check = QCheckBox("Звук сообщений")
            sound_check.setFont(QFont(FONT_FAMILY, 15))
            sound_check.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            sound_check.setChecked(True)
            settings_layout.addWidget(sound_check)
            
            # Показывать статус онлайн
            online_check = QCheckBox("Показывать статус онлайн")
            online_check.setFont(QFont(FONT_FAMILY, 15))
            online_check.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            online_check.setChecked(True)
            settings_layout.addWidget(online_check)
            
            content_layout.addWidget(settings_section)
            
            # === О ПРОГРАММЕ ===
            about_section = QWidget()
            about_section.setStyleSheet(f"background-color: {COLOR_PANEL}; border-radius: 12px;")
            about_layout = QVBoxLayout(about_section)
            about_layout.setContentsMargins(20, 20, 20, 20)
            
            version_label = QLabel("Версия: 1.0.0")
            version_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
            about_layout.addWidget(version_label)
            
            about_label = QLabel("Ten Dem — мессенджер нового поколения")
            about_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
            about_layout.addWidget(about_label)
            
            content_layout.addWidget(about_section)
            
            # === ВЫЙТИ ===
            logout_btn = QPushButton("Выйти из аккаунта")
            logout_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ERROR};
                    color: white;
                    border: none;
                    border-radius: {BUTTON_BORDER_RADIUS}px;
                    padding: 14px;
                    font-size: 15px;
                    font-family: {FONT_FAMILY};
                    font-weight: bold;
                }}
                QPushButton:hover {{ 
                    background-color: #c82333; 
                }}
            """)
            logout_btn.clicked.connect(self.logout)
            content_layout.addWidget(logout_btn)
            
            content_layout.addStretch()
            
            scroll.setWidget(content)
            layout.addWidget(scroll)
            
            self.setLayout(layout)
            
        except Exception as e:
            print(f"Ошибка инициализации настроек: {e}")
            import traceback
            traceback.print_exc()
    
    def edit_profile(self):
        """Открывает диалог редактирования профиля."""
        try:
            QMessageBox.information(self, "Редактирование", 
                "Функция редактирования профиля будет доступна в следующей версии.\n\n"
                "Вы сможете изменить:\n"
                "• Имя пользователя\n"
                "• Аватарку\n"
                "• Статус")
        except Exception as e:
            print(f"Ошибка редактирования профиля: {e}")
    
    def logout(self):
        """Выполняет выход из аккаунта."""
        try:
            from src.database.users_db import set_online_status
            set_online_status(self.current_user.uid, "offline")
            
            reply = QMessageBox.question(
                self, 
                "Выход", 
                "Вы действительно хотите выйти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.close()
                # Здесь можно вернуть пользователя к окну входа
        except Exception as e:
            print(f"Ошибка выхода: {e}")