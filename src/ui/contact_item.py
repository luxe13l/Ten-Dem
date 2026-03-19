"""Contact row widget."""
from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.styles import FONT_FAMILY
from src.styles.themes import get_theme_colors
from src.ui.avatar_widget import AvatarWidget
from src.utils.helpers import format_time, truncate


class ContactItem(QWidget):
    def __init__(self, user, last_message="", unread_count=0, timestamp=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.last_message = last_message
        self.unread_count = unread_count
        self.timestamp = timestamp
        self.colors = get_theme_colors()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        self.avatar = AvatarWidget(self.user.name, self.user.avatar_url)
        layout.addWidget(self.avatar)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        top_row = QHBoxLayout()
        name_label = QLabel(self.user.name)
        name_label.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {self.colors['text_primary']};")
        top_row.addWidget(name_label)
        top_row.addStretch()

        self.time_label = QLabel(format_time(self.timestamp) if self.timestamp else "")
        self.time_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 11px;")
        top_row.addWidget(self.time_label)
        info_layout.addLayout(top_row)

        bottom_row = QHBoxLayout()
        self.message_label = QLabel(truncate(self.last_message or "Нет сообщений", 35))
        self.message_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 13px;")
        self.message_label.setWordWrap(True)
        bottom_row.addWidget(self.message_label, 1)

        if self.unread_count > 0:
            badge = QLabel(str(self.unread_count))
            badge.setFixedSize(22, 22)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet(
                """
                QLabel {
                    background-color: #EF4444;
                    color: white;
                    border-radius: 11px;
                    font-size: 11px;
                    font-weight: 700;
                }
                """
            )
            bottom_row.addWidget(badge)
        info_layout.addLayout(bottom_row)
        layout.addLayout(info_layout, 1)

        self.online_dot = QLabel()
        self.online_dot.setFixedSize(12, 12)
        self.update_status(self.user.status)
        layout.addWidget(self.online_dot)

    def update_preview(self, last_message="", timestamp=None, unread_count=0):
        self.last_message = last_message
        self.timestamp = timestamp
        self.unread_count = unread_count
        self.message_label.setText(truncate(self.last_message or "Нет сообщений", 35))
        self.time_label.setText(format_time(self.timestamp) if self.timestamp else "")

    def update_status(self, status):
        if status == "online":
            self.online_dot.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {self.colors['online']};
                    border: 2px solid {self.colors['bg_secondary']};
                    border-radius: 6px;
                }}
                """
            )
            self.online_dot.show()
        else:
            self.online_dot.hide()

    def sizeHint(self):
        return QSize(280, 70)
