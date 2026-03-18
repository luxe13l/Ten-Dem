"""
Мастер регистрации для Ten Dem
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QStackedWidget, 
                             QFrame, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont
from src.database.auth_manager import auth_manager


# ==================== ЭТАП 1: ТЕЛЕФОН ====================
class PhoneStep(QWidget):
    next_step = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 100, 80, 80)
        main_layout.setSpacing(24)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        logo_label = QLabel("Ten Dem")
        logo_label.setStyleSheet("color: #10B981; font-size: 32px; font-weight: 600;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(logo_label)
        
        main_layout.addSpacing(60)
        
        title = QLabel("Введите номер телефона")
        title.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 500;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 (999) 999-99-99")
        self.phone_input.setStyleSheet("""
            background-color: #1A1B1E;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 14px 18px;
            font-size: 16px;
        """)
        self.phone_input.setMaxLength(18)
        self.phone_input.textChanged.connect(self.format_phone)
        main_layout.addWidget(self.phone_input)
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.error_label)
        
        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.setStyleSheet("""
            background-color: #374151;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 14px 28px;
            font-size: 15px;
            font-weight: 500;
        """)
        self.register_btn.setMinimumHeight(48)
        self.register_btn.clicked.connect(self.on_register)
        main_layout.addWidget(self.register_btn)
        
        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_label = QLabel("Уже есть аккаунт?")
        login_label.setStyleSheet("color: #6B7280; font-size: 13px;")
        login_layout.addWidget(login_label)
        login_btn = QLabel("Войти")
        login_btn.setStyleSheet("color: #10B981; font-size: 13px; font-weight: 500;")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.mousePressEvent = lambda e: self.on_login()
        login_layout.addWidget(login_btn)
        main_layout.addLayout(login_layout)
        
        skip_btn = QPushButton("Пропустить")
        skip_btn.setStyleSheet("""
            background-color: transparent;
            color: #6B7280;
            border: none;
            padding: 12px 24px;
            font-size: 13px;
        """)
        skip_btn.setMinimumHeight(44)
        skip_btn.clicked.connect(self.on_skip)
        main_layout.addWidget(skip_btn)
        
        main_layout.addStretch()
    
    def format_phone(self, text):
        digits = ''.join(c for c in text if c.isdigit())
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
    
    def on_register(self):
        phone = ''.join(c for c in self.phone_input.text() if c.isdigit())
        if len(phone) != 11:
            self.error_label.setText("Введите корректный номер")
            return
        self.error_label.clear()
        self.next_step.emit(phone)
    
    def on_login(self):
        self.on_register()
    
    def on_skip(self):
        self.next_step.emit("skip")


# ==================== ЭТАП 2: КОД ====================
class CodeStep(QWidget):
    next_step = pyqtSignal()
    back_step = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verification_id = None
        self.phone = ""
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 100, 80, 80)
        main_layout.setSpacing(24)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        lock_icon = QLabel("🔐")
        lock_icon.setStyleSheet("font-size: 40px;")
        lock_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lock_icon)
        
        title = QLabel("Код подтверждения")
        title.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 500;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        self.subtitle = QLabel("")
        self.subtitle.setStyleSheet("color: #6B7280; font-size: 13px;")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.subtitle)
        
        change_btn = QLabel("Изменить номер")
        change_btn.setStyleSheet("color: #10B981; font-size: 13px;")
        change_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_btn.mousePressEvent = lambda e: self.back_step.emit()
        main_layout.addWidget(change_btn)
        
        main_layout.addSpacing(30)
        
        code_widget = QWidget()
        code_layout = QHBoxLayout(code_widget)
        code_layout.setSpacing(12)
        code_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.code_inputs = []
        for i in range(6):
            inp = QLineEdit()
            inp.setMaxLength(1)
            inp.setFixedSize(48, 60)
            inp.setStyleSheet("""
                background-color: #1A1B1E;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 22px;
                font-weight: 500;
                padding: 0px;
            """)
            inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inp.textChanged.connect(lambda text, idx=i: self.on_code_changed(text, idx))
            inp.installEventFilter(self)
            code_layout.addWidget(inp)
            self.code_inputs.append(inp)
        
        main_layout.addWidget(code_widget)
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.error_label)
        
        main_layout.addSpacing(20)
        
        self.timer_label = QLabel("Отправить код повторно через 60 сек")
        self.timer_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.timer_label)
        
        self.continue_btn = QPushButton("Продолжить")
        self.continue_btn.setStyleSheet("""
            background-color: #374151;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 14px 28px;
            font-size: 15px;
            font-weight: 500;
        """)
        self.continue_btn.setMinimumHeight(48)
        self.continue_btn.setMaximumWidth(280)
        self.continue_btn.setEnabled(False)
        self.continue_btn.clicked.connect(self.on_continue)
        main_layout.addWidget(self.continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addStretch()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.seconds_left = 60
    
    def set_phone(self, phone):
        self.phone = phone
        masked = f"+7 {phone[2:5]} {phone[5:8]} {phone[8:10]} {phone[10:]}"
        self.subtitle.setText(f"Код отправлен на {masked}")
    
    def set_verification_id(self, vid):
        self.verification_id = vid
    
    def on_code_changed(self, text, index):
        if text and not text.isdigit():
            self.code_inputs[index].setText("")
            return
        if text:
            if index < 5:
                self.code_inputs[index + 1].setFocus()
        self.check_code()
    
    def check_code(self):
        code = ''.join(inp.text() for inp in self.code_inputs)
        self.continue_btn.setEnabled(len(code) == 6 and code.isdigit())
    
    def update_timer(self):
        self.seconds_left -= 1
        if self.seconds_left > 0:
            self.timer_label.setText(f"Отправить код повторно через {self.seconds_left} сек")
        else:
            self.timer.stop()
            self.timer_label.setText("Отправить код повторно")
            self.timer_label.setStyleSheet("color: #10B981; font-size: 12px;")
    
    def start_timer(self):
        self.seconds_left = 60
        self.timer.start(1000)
        self.update_timer()
    
    def on_continue(self):
        code = ''.join(inp.text() for inp in self.code_inputs)
        success, message, phone = auth_manager.verify_code(self.verification_id, code)
        if success:
            self.next_step.emit()
        else:
            self.error_label.setText(message)
    
    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj in self.code_inputs and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Backspace and not obj.text():
                index = self.code_inputs.index(obj)
                if index > 0:
                    self.code_inputs[index - 1].setFocus()
        return super().eventFilter(obj, event)


# ==================== ЭТАП 3: ИМЯ ====================
class NameStep(QWidget):
    next_step = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 100, 80, 80)
        main_layout.setSpacing(24)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("Как к вам обращаться?")
        title.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 500;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        main_layout.addSpacing(30)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")
        self.name_input.setMaxLength(20)
        self.name_input.setStyleSheet("""
            background-color: #1A1B1E;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 14px 18px;
            font-size: 15px;
        """)
        self.name_input.textChanged.connect(self.validate)
        main_layout.addWidget(self.name_input)
        
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Фамилия")
        self.surname_input.setMaxLength(20)
        self.surname_input.setStyleSheet("""
            background-color: #1A1B1E;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 14px 18px;
            font-size: 15px;
        """)
        self.surname_input.textChanged.connect(self.validate)
        main_layout.addWidget(self.surname_input)
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.error_label)
        
        main_layout.addSpacing(10)
        
        self.continue_btn = QPushButton("Продолжить")
        self.continue_btn.setEnabled(False)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2937;
                color: #6B7280;
                border: none;
                border-radius: 10px;
                padding: 14px 28px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover:!disabled {
                background-color: #374151;
            }
            QPushButton:disabled {
                background-color: #1F2937;
                color: #6B7280;
            }
            QPushButton:!disabled {
                background-color: #10B981;
                color: #FFFFFF;
            }
            QPushButton:!disabled:hover {
                background-color: #059669;
            }
            QPushButton:!disabled:pressed {
                background-color: #047857;
            }
        """)
        self.continue_btn.setMinimumHeight(48)
        self.continue_btn.clicked.connect(self.on_continue)
        main_layout.addWidget(self.continue_btn)
        
        main_layout.addStretch()
    
    def validate(self):
        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        
        import re
        
        name_valid = False
        if 2 <= len(name) <= 20:
            if re.match(r'^[a-zA-Zа-яА-ЯёЁ]+$', name):
                name_valid = True
        
        surname_valid = False
        if 2 <= len(surname) <= 20:
            if re.match(r'^[a-zA-Zа-яА-ЯёЁ]+$', surname):
                surname_valid = True
        
        self.continue_btn.setEnabled(name_valid and surname_valid)
        
        if name_valid and surname_valid:
            self.error_label.setText("")
    
    def on_continue(self):
        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        
        import re
        
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ]{2,20}$', name):
            self.error_label.setText("Имя должно содержать только буквы (2-20)")
            return
        
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ]{2,20}$', surname):
            self.error_label.setText("Фамилия должна содержать только буквы (2-20)")
            return
        
        self.next_step.emit({'name': name, 'surname': surname})


# ==================== ЭТАП 4: USERNAME ====================
class UsernameStep(QWidget):
    next_step = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.username_timer = QTimer()
        self.username_timer.setSingleShot(True)
        self.username_timer.timeout.connect(self.check_username)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 100, 80, 80)
        main_layout.setSpacing(24)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("Придумайте username")
        title.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 500;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Люди смогут найти вас по #username")
        subtitle.setStyleSheet("color: #6B7280; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(30)
        
        username_widget = QWidget()
        username_widget.setStyleSheet("background-color: #1A1B1E; border-radius: 10px;")
        username_layout = QHBoxLayout(username_widget)
        username_layout.setContentsMargins(16, 0, 16, 0)
        username_layout.setSpacing(10)
        
        hash_icon = QLabel("#")
        hash_icon.setStyleSheet("color: #6B7280; font-size: 18px; font-weight: 600; background-color: transparent;")
        username_layout.addWidget(hash_icon)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите username")
        self.username_input.setMaxLength(20)
        self.username_input.setStyleSheet("""
            background-color: transparent;
            color: #FFFFFF;
            border: none;
            padding: 14px 8px;
            font-size: 16px;
        """)
        self.username_input.textChanged.connect(self.on_username_changed)
        username_layout.addWidget(self.username_input)
        
        main_layout.addWidget(username_widget)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.error_label)
        
        main_layout.addSpacing(10)
        
        self.continue_btn = QPushButton("Продолжить")
        self.continue_btn.setEnabled(False)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2937;
                color: #6B7280;
                border: none;
                border-radius: 10px;
                padding: 14px 28px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover:!disabled {
                background-color: #374151;
            }
            QPushButton:disabled {
                background-color: #1F2937;
                color: #6B7280;
            }
            QPushButton:!disabled {
                background-color: #10B981;
                color: #FFFFFF;
            }
            QPushButton:!disabled:hover {
                background-color: #059669;
            }
            QPushButton:!disabled:pressed {
                background-color: #047857;
            }
        """)
        self.continue_btn.setMinimumHeight(48)
        self.continue_btn.clicked.connect(self.on_continue)
        main_layout.addWidget(self.continue_btn)
        
        main_layout.addStretch()
    
    def on_username_changed(self, text):
        self.username_timer.stop()
        self.status_label.setText("")
        self.continue_btn.setEnabled(False)
        
        username = text.strip()
        if len(username) >= 3 and len(username) <= 20:
            self.username_timer.start(500)
    
    def check_username(self):
        username = self.username_input.text().strip()
        
        if len(username) < 3:
            self.status_label.setText("Минимум 3 символа")
            self.status_label.setStyleSheet("color: #EF4444; font-size: 12px;")
            self.continue_btn.setEnabled(False)
            return
        
        if len(username) > 20:
            self.status_label.setText("Максимум 20 символов")
            self.status_label.setStyleSheet("color: #EF4444; font-size: 12px;")
            self.continue_btn.setEnabled(False)
            return
        
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self.status_label.setText("Только латиница, цифры и _")
            self.status_label.setStyleSheet("color: #EF4444; font-size: 12px;")
            self.continue_btn.setEnabled(False)
            return
        
        available = auth_manager.check_username_available(username)
        if available:
            self.status_label.setText("✓ Доступен")
            self.status_label.setStyleSheet("color: #10B981; font-size: 12px;")
            self.continue_btn.setEnabled(True)
        else:
            self.status_label.setText("✗ Занят")
            self.status_label.setStyleSheet("color: #EF4444; font-size: 12px;")
            self.continue_btn.setEnabled(False)
    
    def on_continue(self):
        username = self.username_input.text().strip()
        if not username:
            self.error_label.setText("Введите username")
            return
        self.next_step.emit(username)


# ==================== ЭТАП 5: ЗАГРУЗКА (7 СЕКУНД) ====================
class LoadingStep(QWidget):
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #0F0F12;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(24)
        
        self.spinner = QLabel("⏳")
        self.spinner.setStyleSheet("font-size: 56px; color: #FFFFFF;")
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.spinner)
        
        self.label = QLabel("Подготавливаем...")
        self.label.setStyleSheet("color: #FFFFFF; font-size: 15px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedSize(280, 4)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #25262B;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 2px;
            }
        """)
        main_layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.elapsed = 0
        self.duration = 7000  # ✅ РОВНО 7 СЕКУНД
        self.step = 100
    
    def start_loading(self):
        self.elapsed = 0
        self.progress.setValue(0)
        self.timer.start(self.step)
    
    def update_progress(self):
        self.elapsed += self.step
        progress = min(100, int((self.elapsed / self.duration) * 100))
        self.progress.setValue(progress)
        
        if self.elapsed >= self.duration:
            self.timer.stop()
            self.finished.emit()  # ✅ Через 7 секунд вызываем finished


# ==================== ГЛАВНЫЙ МАСТЕР ====================
class RegistrationWizard(QWidget):
    registration_complete = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ten Dem")
        self.setMinimumSize(500, 700)
        self.resize(500, 700)
        self.setStyleSheet("background-color: #0F0F12;")
        
        self.phone = ""
        self.verification_id = None
        self.user_data = {}
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: transparent;")
        
        self.phone_step = PhoneStep()
        self.code_step = CodeStep()
        self.name_step = NameStep()
        self.username_step = UsernameStep()
        self.loading_step = LoadingStep()  # ✅ БЕЗ ЭТАПА ВЫБОРА ТЕМЫ
        
        self.stack.addWidget(self.phone_step)      # 0
        self.stack.addWidget(self.code_step)       # 1
        self.stack.addWidget(self.name_step)       # 2
        self.stack.addWidget(self.username_step)   # 3
        self.stack.addWidget(self.loading_step)    # 4  ✅
        
        main_layout.addWidget(self.stack)
        
        self.phone_step.next_step.connect(self.on_phone_submitted)
        self.code_step.next_step.connect(self.on_code_verified)
        self.code_step.back_step.connect(lambda: self.go_to_step(0))
        self.name_step.next_step.connect(self.on_name_submitted)
        self.username_step.next_step.connect(self.on_username_submitted)
        self.loading_step.finished.connect(self.on_loading_finished)  # ✅
        
        main_layout.addStretch()
    
    def on_phone_submitted(self, phone):
        if phone == "skip":
            self.registration_complete.emit({
                'uid': 'test_user',
                'phone': '+79990000000',
                'name': 'Тестовый',
                'surname': 'Пользователь',
                'username': 'test'
            })
            return
        
        self.phone = phone
        success, message, verification_id = auth_manager.send_verification_code(phone)
        
        if success:
            self.verification_id = verification_id
            self.code_step.set_phone(phone)
            self.code_step.set_verification_id(verification_id)
            self.code_step.start_timer()
            self.stack.setCurrentIndex(1)
        else:
            self.phone_step.error_label.setText(message)
    
    def on_code_verified(self):
        self.stack.setCurrentIndex(2)
    
    def on_name_submitted(self, data):
        self.user_data.update(data)
        self.stack.setCurrentIndex(3)
    
    def on_username_submitted(self, username):
        self.user_data['username'] = username
        # ✅ СРАЗУ ПЕРЕХОДИМ К ЗАГРУЗКЕ (без выбора темы)
        self.stack.setCurrentIndex(4)
        self.loading_step.start_loading()
    
    def on_loading_finished(self):
        """✅ Загрузка завершена (7 секунд прошло)"""
        self.registration_complete.emit({
            'uid': '',
            'phone': self.phone,
            'name': self.user_data.get('name', ''),
            'surname': self.user_data.get('surname', ''),
            'username': self.user_data.get('username', '')
        })
    
    def go_to_step(self, index):
        self.stack.setCurrentIndex(index)