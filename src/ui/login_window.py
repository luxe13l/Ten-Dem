# src/ui/login_window.py
# -*- coding: utf-8 -*-

"""
Окно входа (упрощённое, без SMS, используется номер телефона).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from auth.login_manager import LoginManager
from models.user import User
from utils.helpers import show_error


class LoginWindow(QDialog):
    """Диалог входа по номеру телефона (без подтверждения)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ten Dem — вход")
        self.setFixedSize(350, 250)
        self.setModal(True)

        self.current_user = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Добро пожаловать")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel("Введите номер телефона для входа")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #6C757D; font-size: 14px;")
        layout.addWidget(subtitle)

        # Поле ввода телефона
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 XXX XXX XX XX")
        self.phone_input.setInputMask("+7 999 999 99 99;_")
        self.phone_input.setFixedHeight(45)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CED4DA;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #2481CC;
            }
        """)
        layout.addWidget(self.phone_input)

        # Кнопка входа
        self.login_btn = QPushButton("Войти")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2481CC;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1A5A8C;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        # Кнопка пропуска (тестовый режим)
        self.skip_btn = QPushButton("Пропустить (тестовый режим)")
        self.skip_btn.setFixedHeight(35)
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6C757D;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #2481CC;
            }
        """)
        self.skip_btn.clicked.connect(self.skip_login)
        layout.addWidget(self.skip_btn)

        layout.addStretch()

    def handle_login(self):
        """Обработка входа по номеру."""
        phone = self.phone_input.text().replace(" ", "").replace("_", "")
        if len(phone) < 12 or not phone.startswith("+7"):
            show_error("Ошибка", "Введите корректный номер телефона в формате +7 XXX XXX XX XX")
            return

        try:
            # Вход/регистрация через LoginManager
            self.current_user = LoginManager.login_or_register(phone)
            self.accept()
        except Exception as e:
            show_error("Ошибка", f"Не удалось войти: {e}")

    def skip_login(self):
        """Тестовый вход без номера."""
        self.current_user = User(
            uid="test_user",
            phone="+79990000000",
            name="Тестовый Пользователь",
            avatar_url="",
            status="online",
            last_seen=None
        )
        self.accept()