"""
Окно настроек Ten Dem
С размытым фоном и всеми параметрами
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QSlider,
                             QCheckBox, QComboBox, QLineEdit, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QGraphicsDropShadowEffect

from src.styles import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY,
    ACCENT_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    DIVIDER, FONT_FAMILY, RADIUS_CARD, RADIUS_BUTTON
)


class SettingsWindow(QDialog):
    """Окно настроек с размытым фоном."""
    
    settings_saved = pyqtSignal(dict)
    
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("Настройки")
        self.setMinimumSize(800, 600)
        self.resize(800, 600)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        main_container = QFrame()
        main_container.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SECONDARY};
                border-radius: 16px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 0)
        main_container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = self._create_header()
        layout.addWidget(header)
        
        content = self._create_content()
        layout.addWidget(content, 1)
        
        buttons = self._create_buttons()
        layout.addWidget(buttons)
        
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(main_container)
        self.layout().setContentsMargins(20, 20, 20, 20)
    
    def _create_header(self):
        """Создаёт шапку настроек."""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TERTIARY};
                border-bottom: 1px solid {DIVIDER};
                border-radius: 16px 16px 0 0;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        
        title = QLabel("⚙ Настройки")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        """)
        layout.addWidget(title)
        layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9CA3AF;
                font-size: 20px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return header
    
    def _create_content(self):
        """Создаёт контент настроек."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BG_SECONDARY};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #333;
                border-radius: 3px;
            }}
        """)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        profile_section = self._create_profile_section()
        layout.addWidget(profile_section)
        
        appearance_section = self._create_appearance_section()
        layout.addWidget(appearance_section)
        
        notifications_section = self._create_notifications_section()
        layout.addWidget(notifications_section)
        
        privacy_section = self._create_privacy_section()
        layout.addWidget(privacy_section)
        
        data_section = self._create_data_section()
        layout.addWidget(data_section)
        
        layout.addStretch()
        scroll.setWidget(content)
        
        return scroll
    
    def _create_profile_section(self):
        """Раздел: Профиль."""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TERTIARY};
                border-radius: {RADIUS_CARD}px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        title = QLabel("👤 Профиль")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
        """)
        layout.addWidget(title)
        
        avatar_layout = QHBoxLayout()
        
        avatar_name = self.current_user.name[0].upper() if self.current_user.name else "?"
        avatar = QLabel(avatar_name)
        avatar.setFixedSize(80, 80)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {ACCENT_PRIMARY};
                color: #FFFFFF;
                border-radius: 40px;
                font-size: 32px;
                font-weight: 600;
            }}
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(avatar)
        
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.current_user.name)
        name_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 600;
        """)
        info_layout.addWidget(name_label)
        
        phone_label = QLabel(self.current_user.phone)
        phone_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 14px;
        """)
        info_layout.addWidget(phone_label)
        
        avatar_layout.addLayout(info_layout)
        avatar_layout.addStretch()
        
        change_avatar_btn = QPushButton("📷 Сменить фото")
        change_avatar_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: {RADIUS_BUTTON}px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #2A2A2A;
            }}
        """)
        avatar_layout.addWidget(change_avatar_btn)
        
        layout.addLayout(avatar_layout)
        
        name_input = QLineEdit(self.current_user.name)
        name_input.setPlaceholderText("Имя")
        name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {DIVIDER};
                border-radius: {RADIUS_BUTTON}px;
                padding: 12px 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {ACCENT_PRIMARY};
            }}
        """)
        layout.addWidget(name_input)
        
        username_input = QLineEdit()
        username_input.setPlaceholderText("@username")
        username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {DIVIDER};
                border-radius: {RADIUS_BUTTON}px;
                padding: 12px 16px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(username_input)
        
        bio_input = QLineEdit()
        bio_input.setPlaceholderText("О себе")
        bio_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {DIVIDER};
                border-radius: {RADIUS_BUTTON}px;
                padding: 12px 16px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(bio_input)
        
        return section
    
    def _create_appearance_section(self):
        """Раздел: Оформление."""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TERTIARY};
                border-radius: {RADIUS_CARD}px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        title = QLabel("🎨 Оформление")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
        """)
        layout.addWidget(title)
        
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Тема:")
        theme_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        theme_layout.addWidget(theme_label)
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Тёмная", "Светлая", "Системная"])
        theme_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {DIVIDER};
                border-radius: {RADIUS_BUTTON}px;
                padding: 8px 12px;
                font-size: 14px;
            }}
        """)
        theme_layout.addWidget(theme_combo)
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout)
        
        return section
    
    def _create_notifications_section(self):
        """Раздел: Уведомления."""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TERTIARY};
                border-radius: {RADIUS_CARD}px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        title = QLabel("🔔 Уведомления")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
        """)
        layout.addWidget(title)
        
        notifications = [
            ("📬 Звук сообщений", True),
            ("📱 Push-уведомления", True),
            ("👁️ Предпросмотр текста", True),
            ("🌙 Не беспокоить", False),
        ]
        
        for text, checked in notifications:
            checkbox = QCheckBox(text)
            checkbox.setChecked(checked)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {TEXT_PRIMARY};
                    font-size: 14px;
                    spacing: 8px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {ACCENT_PRIMARY};
                }}
            """)
            layout.addWidget(checkbox)
        
        return section
    
    def _create_privacy_section(self):
        """Раздел: Конфиденциальность."""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TERTIARY};
                border-radius: {RADIUS_CARD}px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        title = QLabel("🔒 Конфиденциальность")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
        """)
        layout.addWidget(title)
        
        privacy_options = [
            ("Кто видит мой онлайн", "Все"),
            ("Кто может писать мне", "Все"),
            ("Кто может звонить мне", "Все"),
        ]
        
        for text, value in privacy_options:
            option_layout = QHBoxLayout()
            
            option_label = QLabel(text)
            option_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px;")
            option_layout.addWidget(option_label)
            
            option_layout.addStretch()
            
            option_value = QLabel(value)
            option_value.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
            option_layout.addWidget(option_value)
            
            arrow = QLabel("›")
            arrow.setStyleSheet(f"color: {TEXT_TERTIARY}; font-size: 18px;")
            option_layout.addWidget(arrow)
            
            layout.addLayout(option_layout)
        
        return section
    
    def _create_data_section(self):
        """Раздел: Данные и память."""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TERTIARY};
                border-radius: {RADIUS_CARD}px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        title = QLabel("💾 Данные и память")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
        """)
        layout.addWidget(title)
        
        storage_layout = QHBoxLayout()
        storage_label = QLabel("Использование хранилища:")
        storage_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        storage_layout.addWidget(storage_label)
        storage_layout.addStretch()
        storage_value = QLabel("156 MB")
        storage_value.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: 600;")
        storage_layout.addWidget(storage_value)
        layout.addLayout(storage_layout)
        
        clear_btn = QPushButton("🗑️ Очистить кэш")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: {RADIUS_BUTTON}px;
                padding: 12px 24px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #2A2A2A;
            }}
        """)
        layout.addWidget(clear_btn)
        
        return section
    
    def _create_buttons(self):
        """Кнопки сохранения/отмены."""
        buttons = QFrame()
        buttons.setFixedHeight(80)
        buttons.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TERTIARY};
                border-top: 1px solid {DIVIDER};
                border-radius: 0 0 16px 16px;
            }}
        """)
        
        layout = QHBoxLayout(buttons)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)
        layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(120, 44)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 1px solid {DIVIDER};
                border-radius: {RADIUS_BUTTON}px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {BG_SECONDARY};
            }}
        """)
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Сохранить")
        save_btn.setFixedSize(120, 44)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: {RADIUS_BUTTON}px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #8B5CF6;
            }}
        """)
        save_btn.clicked.connect(self.on_save)
        layout.addWidget(save_btn)
        
        return buttons
    
    def on_save(self):
        """Сохраняет настройки."""
        settings = {
            'name': '...',
            'theme': 'dark',
            'notifications': True,
        }
        self.settings_saved.emit(settings)
        self.close()