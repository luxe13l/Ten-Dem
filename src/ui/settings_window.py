"""Settings dialog with real state saving."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from src.database.local_store import load_store, save_store
from src.database.users_db import update_user
from src.styles import FONT_FAMILY, RADIUS_BUTTON, RADIUS_CARD
from src.styles.themes import apply_theme, get_theme_colors


class SettingsWindow(QDialog):
    settings_saved = pyqtSignal(dict)

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.colors = get_theme_colors(getattr(self.current_user, "theme", "dark"))
        self.form_controls = {}
        self.settings = self._load_settings()
        self.init_ui()

    def _load_settings(self):
        return load_store().get("settings", {}).get(
            self.current_user.uid,
            {
                "name": self.current_user.name,
                "username": getattr(self.current_user, "username", ""),
                "bio": getattr(self.current_user, "bio", ""),
                "theme": getattr(self.current_user, "theme", "dark"),
                "font_scale": 15,
                "sound": True,
                "push": True,
                "preview": True,
                "dnd": False,
            },
        )

    def init_ui(self):
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.resize(820, 640)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: {self.colors['bg_secondary']}; border-radius: 24px; }}")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_content(), 1)
        layout.addWidget(self._create_footer())

    def _create_header(self):
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background-color: {self.colors['bg_tertiary']}; border-bottom: 1px solid {self.colors['divider']}; border-radius: 24px 24px 0 0; }}"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 20, 24, 20)
        title = QLabel("Настройки")
        title.setStyleSheet(f"color: {self.colors['text_primary']}; font-size: 22px; font-weight: 600;")
        layout.addWidget(title)
        layout.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(38, 38)
        close_btn.setStyleSheet(self._icon_style())
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        return frame

    def _create_content(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        layout.addWidget(self._profile_section())
        layout.addWidget(self._appearance_section())
        layout.addWidget(self._notifications_section())
        layout.addWidget(self._privacy_section())
        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _profile_section(self):
        section, layout = self._section("Профиль")
        row = QHBoxLayout()
        avatar = QLabel((self.current_user.name or "?")[0].upper())
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(72, 72)
        avatar.setStyleSheet(
            f"QLabel {{ background-color: {self.colors['accent_primary']}; color: white; border-radius: 36px; font-size: 28px; font-weight: 700; }}"
        )
        row.addWidget(avatar)
        text_layout = QVBoxLayout()
        name_label = QLabel(self.current_user.name or "Пользователь")
        name_label.setStyleSheet(f"color: {self.colors['text_primary']}; font-size: 18px; font-weight: 600;")
        text_layout.addWidget(name_label)
        phone_label = QLabel(self.current_user.phone or "")
        phone_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 13px;")
        text_layout.addWidget(phone_label)
        row.addLayout(text_layout)
        row.addStretch()
        layout.addLayout(row)

        self.form_controls["name"] = self._line_edit(self.settings.get("name", self.current_user.name), "Имя")
        self.form_controls["username"] = self._line_edit(self.settings.get("username", getattr(self.current_user, "username", "")), "@username")
        self.form_controls["bio"] = self._line_edit(self.settings.get("bio", getattr(self.current_user, "bio", "")), "О себе")
        layout.addWidget(self.form_controls["name"])
        layout.addWidget(self.form_controls["username"])
        layout.addWidget(self.form_controls["bio"])
        return section

    def _appearance_section(self):
        section, layout = self._section("Оформление")
        row = QHBoxLayout()
        label = QLabel("Тема")
        label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 14px;")
        row.addWidget(label)
        row.addStretch()
        combo = QComboBox()
        combo.addItems(["Темная", "Светлая", "Системная"])
        combo.setCurrentText({"dark": "Темная", "light": "Светлая", "system": "Системная"}.get(self.settings.get("theme", "dark"), "Темная"))
        combo.setStyleSheet(self._input_style())
        self.form_controls["theme"] = combo
        row.addWidget(combo)
        layout.addLayout(row)

        slider_label = QLabel("Размер текста")
        slider_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 14px;")
        layout.addWidget(slider_label)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(12)
        slider.setMaximum(20)
        slider.setValue(int(self.settings.get("font_scale", 15)))
        self.form_controls["font_scale"] = slider
        layout.addWidget(slider)
        return section

    def _notifications_section(self):
        section, layout = self._section("Уведомления")
        for key, title in [("sound", "Звук сообщений"), ("push", "Push-уведомления"), ("preview", "Показывать текст"), ("dnd", "Не беспокоить")]:
            box = QCheckBox(title)
            box.setChecked(bool(self.settings.get(key, False)))
            box.setStyleSheet(
                f"""
                QCheckBox {{ color: {self.colors['text_primary']}; font-size: 14px; spacing: 10px; }}
                QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 1px solid {self.colors['divider']}; }}
                QCheckBox::indicator:checked {{ background-color: {self.colors['accent_primary']}; border-color: {self.colors['accent_primary']}; }}
                """
            )
            self.form_controls[key] = box
            layout.addWidget(box)
        return section

    def _privacy_section(self):
        section, layout = self._section("Конфиденциальность")
        for left, right in [("Кто видит онлайн", "Все"), ("Кто может писать", "Все"), ("Кто может звонить", "Контакты")]:
            row = QHBoxLayout()
            left_label = QLabel(left)
            left_label.setStyleSheet(f"color: {self.colors['text_primary']}; font-size: 14px;")
            row.addWidget(left_label)
            row.addStretch()
            right_label = QLabel(right)
            right_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 13px;")
            row.addWidget(right_label)
            layout.addLayout(row)
        return section

    def _create_footer(self):
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background-color: {self.colors['bg_tertiary']}; border-top: 1px solid {self.colors['divider']}; border-radius: 0 0 24px 24px; }}"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.addStretch()
        cancel = QPushButton("Отмена")
        cancel.setFixedSize(120, 44)
        cancel.setStyleSheet(self._secondary_button_style())
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)
        save = QPushButton("Сохранить")
        save.setFixedSize(140, 44)
        save.setStyleSheet(self._primary_button_style())
        save.clicked.connect(self.on_save)
        layout.addWidget(save)
        return frame

    def on_save(self):
        payload = {
            "name": self.form_controls["name"].text().strip() or self.current_user.name,
            "username": self.form_controls["username"].text().strip(),
            "bio": self.form_controls["bio"].text().strip(),
            "theme": {"Темная": "dark", "Светлая": "light", "Системная": "system"}.get(self.form_controls["theme"].currentText(), "dark"),
            "font_scale": self.form_controls["font_scale"].value(),
            "sound": self.form_controls["sound"].isChecked(),
            "push": self.form_controls["push"].isChecked(),
            "preview": self.form_controls["preview"].isChecked(),
            "dnd": self.form_controls["dnd"].isChecked(),
        }
        store = load_store()
        store.setdefault("settings", {})[self.current_user.uid] = payload
        save_store(store)
        self.current_user.name = payload["name"]
        self.current_user.username = payload["username"]
        self.current_user.bio = payload["bio"]
        self.current_user.theme = payload["theme"]
        update_user(self.current_user.uid, {"name": payload["name"], "username": payload["username"], "bio": payload["bio"], "theme": payload["theme"]})
        apply_theme(QApplication.instance(), payload["theme"])
        self.settings_saved.emit(payload)
        self.accept()

    def _section(self, title: str):
        section = QFrame()
        section.setStyleSheet(f"QFrame {{ background-color: {self.colors['bg_tertiary']}; border-radius: {RADIUS_CARD}px; }}")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        label = QLabel(title)
        label.setStyleSheet(f"color: {self.colors['text_primary']}; font-size: 16px; font-weight: 600;")
        layout.addWidget(label)
        return section, layout

    def _line_edit(self, value: str, placeholder: str):
        field = QLineEdit(value)
        field.setPlaceholderText(placeholder)
        field.setStyleSheet(self._input_style())
        return field

    def _input_style(self):
        return f"""
        QLineEdit, QComboBox {{
            background-color: {self.colors['bg_primary']};
            color: {self.colors['text_primary']};
            border: 1px solid {self.colors['divider']};
            border-radius: {RADIUS_BUTTON}px;
            padding: 12px 14px;
            font-size: 14px;
            font-family: {FONT_FAMILY};
        }}
        """

    def _primary_button_style(self):
        return f"QPushButton {{ background-color: {self.colors['accent_primary']}; color: white; border: none; border-radius: {RADIUS_BUTTON}px; font-size: 14px; font-weight: 600; }}"

    def _secondary_button_style(self):
        return f"QPushButton {{ background-color: transparent; color: {self.colors['text_secondary']}; border: 1px solid {self.colors['divider']}; border-radius: {RADIUS_BUTTON}px; font-size: 14px; font-weight: 500; }}"

    def _icon_style(self):
        return f"""
        QPushButton {{
            background-color: transparent;
            color: {self.colors['text_secondary']};
            border: none;
            border-radius: 12px;
            font-size: 16px;
        }}
        QPushButton:hover {{
            background-color: {self.colors['bg_primary']};
            color: {self.colors['text_primary']};
        }}
        """
