# -*- coding: utf-8 -*-
"""
Вспомогательные функции.
"""

from datetime import datetime
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox


def format_time(dt: datetime) -> str:
    """Форматирует время для отображения под сообщением."""
    if not dt:
        return ""
    now = datetime.now()
    if dt.date() == now.date():
        return dt.strftime("%H:%M")
    elif dt.year == now.year:
        return dt.strftime("%d %b, %H:%M")
    else:
        return dt.strftime("%d.%m.%Y, %H:%M")


def format_last_seen(dt: datetime) -> str:
    """Форматирует время последнего визита."""
    if not dt:
        return "давно"
    delta = datetime.now() - dt
    if delta.total_seconds() < 60:
        return "только что"
    elif delta.total_seconds() < 3600:
        minutes = int(delta.total_seconds() // 60)
        return f"{minutes} мин. назад"
    elif delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() // 3600)
        return f"{hours} ч. назад"
    else:
        days = delta.days
        return f"{days} дн. назад"


def get_avatar_pixmap(url: str, size: int) -> QPixmap:
    """Загружает аватарку по URL или возвращает заглушку."""
    # В демо-версии всегда возвращаем заглушку
    pixmap = QPixmap("assets/icons/default_avatar.svg")
    if pixmap.isNull():
        pixmap = QPixmap(size, size)
        pixmap.fill()
    return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                         Qt.TransformationMode.SmoothTransformation)


def show_error(title: str, message: str):
    """Показывает модальное окно с ошибкой."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()