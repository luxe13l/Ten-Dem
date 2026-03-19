"""Contact info dialog."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.database.messages_db import get_media_gallery
from src.styles.themes import get_theme_colors


class ContactInfoDialog(QDialog):
    def __init__(self, current_user, contact, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.contact = contact
        self.colors = get_theme_colors(getattr(current_user, "theme", "dark"))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Информация о контакте")
        self.resize(420, 520)
        self.setModal(True)
        self.setStyleSheet(f"background-color: {self.colors['bg_primary']}; color: {self.colors['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        avatar = QLabel((self.contact.name or "?")[0].upper())
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(76, 76)
        avatar.setStyleSheet(
            f"QLabel {{ background-color: {self.colors['accent_primary']}; color: white; border-radius: 38px; font-size: 30px; font-weight: 700; }}"
        )
        layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignHCenter)

        name = QLabel(self.contact.name or "Пользователь")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setStyleSheet(f"color: {self.colors['text_primary']}; font-size: 24px; font-weight: 700;")
        layout.addWidget(name)

        username = getattr(self.contact, "username", "")
        username_label = QLabel(f"@{username}" if username else "username не указан")
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 14px;")
        layout.addWidget(username_label)

        for title, value in [
            ("Телефон", self.contact.phone or "не указан"),
            ("Статус", "в сети" if self.contact.status == "online" else "не в сети"),
            ("О себе", getattr(self.contact, "bio", "") or "пусто"),
        ]:
            card = QFrame()
            card.setStyleSheet(f"QFrame {{ background-color: {self.colors['bg_secondary']}; border: 1px solid {self.colors['divider']}; border-radius: 18px; }}")
            row = QVBoxLayout(card)
            row.setContentsMargins(16, 14, 16, 14)
            caption = QLabel(title)
            caption.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 12px;")
            row.addWidget(caption)
            text = QLabel(value)
            text.setWordWrap(True)
            text.setStyleSheet(f"color: {self.colors['text_primary']}; font-size: 15px; font-weight: 500;")
            row.addWidget(text)
            layout.addWidget(card)

        photos = len(get_media_gallery(self.current_user.uid, self.contact.uid, "photo"))
        files = len(get_media_gallery(self.current_user.uid, self.contact.uid, "file"))
        media = QFrame()
        media.setStyleSheet(f"QFrame {{ background-color: {self.colors['bg_secondary']}; border: 1px solid {self.colors['divider']}; border-radius: 18px; }}")
        media_layout = QHBoxLayout(media)
        media_layout.setContentsMargins(16, 14, 16, 14)
        for left, right in [("Фото", str(photos)), ("Файлы", str(files))]:
            block = QVBoxLayout()
            key = QLabel(left)
            key.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 12px;")
            val = QLabel(right)
            val.setStyleSheet(f"color: {self.colors['text_primary']}; font-size: 18px; font-weight: 700;")
            block.addWidget(key)
            block.addWidget(val)
            media_layout.addLayout(block)
            media_layout.addStretch()
        layout.addWidget(media)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(
            f"QPushButton {{ background-color: {self.colors['accent_primary']}; color: white; border: none; border-radius: 16px; padding: 12px; font-weight: 600; }}"
        )
        layout.addWidget(close_btn)
