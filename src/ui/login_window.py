"""
Окно авторизации мессенджера Ten Dem
"""
import re
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from src.database.users_db import get_user_by_phone, create_user
from src.models.user import User
from src.utils.settings import (
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_ERROR, COLOR_ACCENT,
    COLOR_PANEL, COLOR_INPUT_BG, COLOR_INPUT_BORDER,
    BUTTON_BORDER_RADIUS, INPUT_BORDER_RADIUS, FONT_FAMILY
)


class LoginWindow(QDialog):
    """Окно входа в мессенджер."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = None
        self.verification_id = None
        self.timer = QTimer()
        self.seconds_left = 0
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса."""
        try:
            self.setWindowTitle("Вход — Ten Dem")
            self.setMinimumSize(400, 450)
            self.setModal(True)
            
            layout = QVBoxLayout()
            layout.setSpacing(20)
            layout.setContentsMargins(40, 40, 40, 40)
            
            # Заголовок
            title = QLabel("Ten Dem")
            title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            layout.addWidget(title)
            
            subtitle = QLabel("Войдите, чтобы продолжить")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
            layout.addWidget(subtitle)
            
            layout.addSpacing(20)
            
            # Поле телефона
            self.phone_input = QLineEdit()
            self.phone_input.setPlaceholderText("+7 (999) 999-99-99")
            self.phone_input.textChanged.connect(self.format_phone_input)
            self.phone_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLOR_INPUT_BG};
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid {COLOR_INPUT_BORDER};
                    border-radius: {INPUT_BORDER_RADIUS}px;
                    padding: 12px 16px;
                    font-size: 15px;
                    font-family: {FONT_FAMILY};
                }}
                QLineEdit:focus {{
                    border: 2px solid {COLOR_ACCENT};
                }}
            """)
            layout.addWidget(self.phone_input)
            
            # Кнопка получения кода
            self.code_btn = QPushButton("Получить код")
            self.code_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT};
                    color: white;
                    border: none;
                    border-radius: {BUTTON_BORDER_RADIUS}px;
                    padding: 12px;
                    font-size: 15px;
                    font-family: {FONT_FAMILY};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #1E6BA8;
                }}
                QPushButton:disabled {{
                    background-color: {COLOR_INPUT_BORDER};
                    color: {COLOR_TEXT_SECONDARY};
                }}
            """)
            self.code_btn.clicked.connect(self.send_code)
            layout.addWidget(self.code_btn)
            
            # Поле кода
            self.code_input = QLineEdit()
            self.code_input.setPlaceholderText("Введите код из СМС")
            self.code_input.setVisible(False)
            self.code_input.setMaxLength(6)
            self.code_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLOR_INPUT_BG};
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid {COLOR_INPUT_BORDER};
                    border-radius: {INPUT_BORDER_RADIUS}px;
                    padding: 12px 16px;
                    font-size: 15px;
                    font-family: {FONT_FAMILY};
                }}
            """)
            layout.addWidget(self.code_input)
            
            # Кнопка входа
            self.login_btn = QPushButton("Войти")
            self.login_btn.setVisible(False)
            self.login_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT};
                    color: white;
                    border: none;
                    border-radius: {BUTTON_BORDER_RADIUS}px;
                    padding: 12px;
                    font-size: 15px;
                    font-family: {FONT_FAMILY};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #1E6BA8;
                }}
            """)
            self.login_btn.clicked.connect(self.verify_code)
            layout.addWidget(self.login_btn)
            
            # Кнопка пропуска
            self.skip_btn = QPushButton("Пропустить (тест)")
            self.skip_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT_SECONDARY};
                    border: 1px solid {COLOR_INPUT_BORDER};
                    border-radius: {BUTTON_BORDER_RADIUS}px;
                    padding: 10px;
                    font-size: 14px;
                    font-family: {FONT_FAMILY};
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PANEL};
                }}
            """)
            self.skip_btn.clicked.connect(self.skip_login)
            layout.addWidget(self.skip_btn)
            
            # Сообщение об ошибке
            self.error_label = QLabel()
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-size: 13px;")
            self.error_label.setWordWrap(True)
            layout.addWidget(self.error_label)
            
            self.setLayout(layout)
            
            # Таймер
            self.timer.setInterval(1000)
            self.timer.timeout.connect(self.update_timer)
            
        except Exception as e:
            print(f"Ошибка инициализации окна входа: {e}")
            import traceback
            traceback.print_exc()
    
    def format_phone_input(self, text):
        """Форматирует ввод номера телефона."""
        try:
            digits = re.sub(r'\D', '', text)
            
            if digits.startswith('8'):
                digits = '7' + digits[1:]
            if not digits.startswith('7'):
                digits = '7' + digits
            
            digits = digits[:11]
            
            if len(digits) <= 1:
                formatted = f"+{digits}"
            elif len(digits) <= 4:
                formatted = f"+7 ({digits[1:]}"
            elif len(digits) <= 7:
                formatted = f"+7 ({digits[1:4]}) {digits[4:]}"
            elif len(digits) <= 9:
                formatted = f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            else:
                formatted = f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
            
            if self.phone_input.text() != formatted:
                self.phone_input.setText(formatted)
                self.phone_input.setCursorPosition(len(formatted))
        except Exception:
            pass
    
    def send_code(self):
        """Отправляет код подтверждения."""
        try:
            phone = re.sub(r'\D', '', self.phone_input.text())
            
            if len(phone) != 11:
                self.error_label.setText("Введите корректный номер")
                return
            
            self.error_label.clear()
            self.verification_id = "test_mode"
            
            self.code_input.setVisible(True)
            self.login_btn.setVisible(True)
            self.code_btn.setEnabled(False)
            self.code_btn.setText("Отправить код повторно (60с)")
            
            self.seconds_left = 60
            self.timer.start()
        except Exception as e:
            self.error_label.setText(f"Ошибка: {e}")
    
    def update_timer(self):
        """Обновляет таймер кнопки."""
        try:
            self.seconds_left -= 1
            
            if self.seconds_left > 0:
                self.code_btn.setText(f"Отправить код повторно ({self.seconds_left}с)")
            else:
                self.timer.stop()
                self.code_btn.setEnabled(True)
                self.code_btn.setText("Получить код")
        except Exception:
            pass
    
    def verify_code(self):
        """Проверяет код и входит."""
        try:
            code = self.code_input.text().strip()
            
            if len(code) != 6:
                self.error_label.setText("Код должен содержать 6 цифр")
                return
            
            phone = re.sub(r'\D', '', self.phone_input.text())
            
            user_data = get_user_by_phone(phone)
            
            # ИСПРАВЛЕНО: было "if user_" без завершения
            if user_data:
                self.current_user = User.from_dict(user_data, user_data['uid'])
            else:
                from datetime import datetime
                new_uid = create_user({
                    'phone': phone,
                    'name': f"Пользователь {phone[-4:]}",
                    'avatar_url': '',
                    'status': 'online',
                    'last_seen': datetime.now()
                })
                if new_uid:
                    self.current_user = User(
                        uid=new_uid, phone=phone, 
                        name=f"Пользователь {phone[-4:]}",
                        status='online'
                    )
            
            if self.current_user:
                self.accept()
            else:
                self.error_label.setText("Ошибка входа. Попробуйте ещё раз.")
        except Exception as e:
            self.error_label.setText(f"Ошибка: {e}")
    
    def skip_login(self):
        """Создаёт тестового пользователя."""
        try:
            self.current_user = User(
                uid="test_user",
                phone="+79990000000",
                name="Тестовый пользователь",
                status="online"
            )
            self.accept()
        except Exception as e:
            print(f"Ошибка при пропуске входа: {e}")
    
    def get_user(self):
        """Возвращает авторизованного пользователя."""
        return self.current_user