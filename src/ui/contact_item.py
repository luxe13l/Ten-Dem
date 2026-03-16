# -*- coding: utf-8 -*-
"""
Виджет для отображения контакта в списке слева.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont

from models.user import User
from utils.helpers import get_avatar_pixmap, format_last_seen
from utils.settings import AVATAR_SIZE


class ContactItemWidget(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # Аватарка
        avatar_label = QLabel()
        avatar_label.setFixedSize(AVATAR_SIZE, AVATAR_SIZE)
        pixmap = get_avatar_pixmap(self.user.avatar_url, AVATAR_SIZE)
        avatar_label.setPixmap(pixmap)
        avatar_label.setScaledContents(True)
        avatar_label.setStyleSheet("border-radius: {}px;".format(AVATAR_SIZE // 2))
        layout.addWidget(avatar_label)

        # Информация о пользователе
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(self.user.name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)

        status_text = "В сети" if self.user.status == "online" else format_last_seen(self.user.last_seen)
        status_label = QLabel(status_text)
        status_label.setStyleSheet("color: #6C757D; font-size: 12px;")
        info_layout.addWidget(status_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Индикатор онлайн
        if self.user.status == "online":
            online_indicator = QLabel()
            online_indicator.setFixedSize(10, 10)
            online_indicator.setStyleSheet("background-color: #28A745; border-radius: 5px;")
            layout.addWidget(online_indicator)

    def sizeHint(self):
        return QSize(250, 70)