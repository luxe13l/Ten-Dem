"""
Экран юридических соглашений Ten Dem
Ссылки прямо в чекбоксах — минимализм и удобство
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QCheckBox, QPushButton, QFrame, QScrollArea,
                             QDialog, QTextBrowser, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QFont
import os


class ClickableLabel(QLabel):
    """Кликабельный текст, который работает как ссылка"""
    clicked = pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QLabel {
                color: #7C3AED;
                text-decoration: underline;
                text-decoration-color: #7C3AED;
            }
            QLabel:hover {
                color: #8B5CF6;
            }
        """)
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class LinkCheckBox(QWidget):
    """Кастомный чекбокс с кликабельной ссылкой в тексте"""
    stateChanged = pyqtSignal(int)
    linkClicked = pyqtSignal(str)
    
    def __init__(self, text_before, link_text, text_after, link_key, parent=None):
        super().__init__(parent)
        self.link_key = link_key
        self.is_checked = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Сам чекбокс (стандартный QCheckBox без текста)
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid #3A3A3A;
                background-color: #1E1E1E;
            }
            QCheckBox::indicator:checked {
                background-color: #7C3AED;
                border: 2px solid #7C3AED;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #8B5CF6;
            }
        """)
        self.checkbox.stateChanged.connect(self.on_state_changed)
        layout.addWidget(self.checkbox)
        
        # Текст до ссылки
        if text_before:
            before_label = QLabel(text_before)
            before_label.setStyleSheet("color: #FFFFFF; font-size: 15px;")
            layout.addWidget(before_label)
        
        # Кликабельная ссылка
        self.link_label = ClickableLabel(link_text)
        self.link_label.clicked.connect(self.on_link_clicked)
        layout.addWidget(self.link_label)
        
        # Текст после ссылки
        if text_after:
            after_label = QLabel(text_after)
            after_label.setStyleSheet("color: #FFFFFF; font-size: 15px;")
            layout.addWidget(after_label)
        
        layout.addStretch()
    
    def on_state_changed(self, state):
        self.is_checked = (state == 2)
        self.stateChanged.emit(state)
    
    def on_link_clicked(self):
        self.linkClicked.emit(self.link_key)
    
    def isChecked(self):
        return self.is_checked


class LegalAgreementWindow(QWidget):
    """Окно юридических соглашений."""
    
    completed = pyqtSignal(bool)
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.link_checkboxes = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Ten Dem — Юридические соглашения")
        self.setMinimumSize(600, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #0A0A0A;
                color: #FFFFFF;
                font-family: 'Inter', sans-serif;
            }
        """)
        
        # Основной контейнер
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Заголовок
        title = QLabel("⚖️ ЮРИДИЧЕСКИЕ ДОГОВОРЫ")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #FFFFFF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Приветственная карточка
        welcome_card = QFrame()
        welcome_card.setStyleSheet("""
            QFrame {
                background-color: #141414;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_card)
        
        hello = QLabel(f"Здравствуйте, {self.user_data.get('name', 'Пользователь')}!")
        hello.setStyleSheet("font-size: 20px; font-weight: 600; color: #FFFFFF;")
        hello.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(hello)
        
        instruction = QLabel("Для завершения регистрации подтвердите согласие с документами ниже")
        instruction.setStyleSheet("font-size: 14px; color: #A0A0A0;")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setWordWrap(True)
        welcome_layout.addWidget(instruction)
        
        layout.addWidget(welcome_card)
        
        # Чекбоксы со ссылками
        agreements = [
            {"before": "Я принимаю условия ", "link": "Пользовательского соглашения", "after": "", "key": "terms"},
            {"before": "Я согласен с ", "link": "Политикой конфиденциальности", "after": "", "key": "privacy"},
            {"before": "Я даю ", "link": "Согласие на обработку данных", "after": "", "key": "consent"},
            {"before": "Я даю ", "link": "Согласие на передачу в Firebase", "after": "", "key": "transfer"},
            {"before": "", "link": "", "after": "Я подтверждаю, что мне есть 14 лет", "key": "age"},
        ]
        
        for agree in agreements:
            if agree["link"]:
                cb = LinkCheckBox(agree["before"], agree["link"], agree["after"], agree["key"])
                cb.linkClicked.connect(self.open_document)
                cb.stateChanged.connect(self.check_all_agreements)
                self.link_checkboxes.append(cb)
                layout.addWidget(cb)
            else:
                cb = QCheckBox(agree["after"])
                cb.setStyleSheet("""
                    QCheckBox {
                        color: #FFFFFF;
                        font-size: 15px;
                        spacing: 12px;
                        padding: 8px 0;
                    }
                    QCheckBox::indicator {
                        width: 22px;
                        height: 22px;
                        border-radius: 6px;
                        border: 2px solid #3A3A3A;
                        background-color: #1E1E1E;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #7C3AED;
                        border: 2px solid #7C3AED;
                    }
                    QCheckBox::indicator:hover {
                        border: 2px solid #8B5CF6;
                    }
                """)
                cb.stateChanged.connect(self.check_all_agreements)
                self.link_checkboxes.append(cb)
                layout.addWidget(cb)
        
        # Подсказка
        hint = QLabel("📍 Нажмите на текст в скобках, чтобы открыть документ")
        hint.setStyleSheet("color: #6B6B6B; font-size: 12px; margin-top: 10px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        
        layout.addStretch()
        
        # Кнопка регистрации
        self.register_btn = QPushButton("🔓 ЗАВЕРШИТЬ РЕГИСТРАЦИЮ")
        self.register_btn.setMinimumHeight(60)
        self.register_btn.setEnabled(False)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED;
                color: white;
                font-size: 18px;
                font-weight: 600;
                border-radius: 16px;
                padding: 16px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #8B5CF6;
            }
            QPushButton:disabled {
                background-color: #2A2A2A;
                color: #6B6B6B;
            }
        """)
        self.register_btn.clicked.connect(self.complete_registration)
        layout.addWidget(self.register_btn)
        
        # Основной layout с прокруткой
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #0A0A0A;")
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def open_document(self, doc_key):
        """Открывает документ в отдельном окне с подстановкой имени"""
        documents = {
            "terms": {"name": "Пользовательское соглашение", "file": "terms.txt"},
            "privacy": {"name": "Политика конфиденциальности", "file": "privacy.txt"},
            "consent": {"name": "Согласие на обработку данных", "file": "consent.txt"},
            "transfer": {"name": "Согласие на передачу в Firebase", "file": "transfer.txt"},
        }
        
        if doc_key not in documents:
            return
        
        doc = documents[doc_key]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(doc["name"])
        dialog.setMinimumSize(700, 600)
        dialog.setStyleSheet("background-color: #141414; color: #FFFFFF;")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel(doc["name"])
        title.setStyleSheet("font-size: 20px; font-weight: 600; padding: 10px;")
        layout.addWidget(title)
        
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 20px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        # Загружаем текст из файла и подставляем имя
        file_path = os.path.join("assets/docs", doc["file"])
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                content = content.replace("[ИМЯ]", self.user_data.get('name', 'Пользователь'))
                text_browser.setText(content)
        except FileNotFoundError:
            text_browser.setText("Документ временно недоступен.\n\nТекст документа:\n\n" + doc["name"] + "\n\nПользователь: " + self.user_data.get('name', 'Пользователь'))
        
        layout.addWidget(text_browser)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def check_all_agreements(self):
        """Проверяет, все ли чекбоксы отмечены"""
        all_checked = all(cb.isChecked() for cb in self.link_checkboxes)
        self.register_btn.setEnabled(all_checked)
    
    def complete_registration(self):
        """Завершает регистрацию"""
        if self.register_btn.isEnabled():
            print(f"✅ Пользователь {self.user_data.get('name')} согласился со всеми условиями")
            self.completed.emit(True)
            self.close()