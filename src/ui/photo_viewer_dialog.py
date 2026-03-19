"""Fullscreen photo viewer for chat media."""

from __future__ import annotations

import os
import shutil

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
)

from src.styles.themes import get_theme_colors


class ZoomableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap()
        self._zoom = 1.0
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_source_pixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self._zoom = 1.0
        self._apply_scale()

    def wheelEvent(self, event):
        if self._pixmap.isNull():
            return
        delta = event.angleDelta().y()
        self._zoom = max(0.25, min(4.0, self._zoom + (0.15 if delta > 0 else -0.15)))
        self._apply_scale()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scale()

    def _apply_scale(self):
        if self._pixmap.isNull() or self.width() <= 0 or self.height() <= 0:
            return
        base = self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        scaled = self._pixmap.scaled(
            max(1, int(base.width() * self._zoom)),
            max(1, int(base.height() * self._zoom)),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)


class PhotoViewerDialog(QDialog):
    delete_requested = pyqtSignal(str)

    def __init__(self, items: list[dict], current_index: int = 0, parent=None):
        super().__init__(parent)
        self.items = items
        self.current_index = current_index
        self.colors = get_theme_colors()
        self._drag_start = QPoint()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.Dialog, True)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(4, 9, 16, 0.93);")
        self.build_ui()
        self.load_current()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(18)

        self.content = QFrame()
        self.content.setStyleSheet(
            f"QFrame {{ background-color: {self.colors['bg_secondary']}; border-radius: 26px; }}"
        )
        root.addWidget(self.content, 1)

        frame_layout = QVBoxLayout(self.content)
        frame_layout.setContentsMargins(18, 18, 18, 18)
        frame_layout.setSpacing(16)

        top = QHBoxLayout()
        self.back_button = self._action_button("Назад")
        self.back_button.clicked.connect(self.close)
        top.addWidget(self.back_button)

        self.title_label = QLabel()
        self.title_label.setStyleSheet(
            f"color: {self.colors['text_primary']}; font-size: 15px; font-weight: 600; background: transparent;"
        )
        top.addWidget(self.title_label, 1)

        self.download_button = self._action_button("Скачать")
        self.download_button.clicked.connect(self.download_current)
        top.addWidget(self.download_button)

        self.delete_button = self._action_button("Удалить")
        self.delete_button.clicked.connect(self.delete_current)
        top.addWidget(self.delete_button)
        frame_layout.addLayout(top)

        center = QHBoxLayout()
        center.setSpacing(14)

        self.prev_button = self._nav_button("‹")
        self.prev_button.clicked.connect(self.show_previous)
        center.addWidget(self.prev_button, 0, Qt.AlignmentFlag.AlignVCenter)

        self.image_label = ZoomableImageLabel()
        self.image_label.setMinimumSize(520, 360)
        self.image_label.setStyleSheet("background: transparent;")
        center.addWidget(self.image_label, 1)

        self.next_button = self._nav_button("›")
        self.next_button.clicked.connect(self.show_next)
        center.addWidget(self.next_button, 0, Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addLayout(center, 1)

        self.caption_label = QLabel()
        self.caption_label.setWordWrap(True)
        self.caption_label.setStyleSheet(
            f"color: {self.colors['text_secondary']}; font-size: 13px; background: transparent;"
        )
        frame_layout.addWidget(self.caption_label)

    def _action_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.colors['bg_tertiary']};
                color: {self.colors['text_primary']};
                border: none;
                border-radius: 16px;
                padding: 10px 14px;
            }}
            QPushButton:hover {{ background-color: {self.colors['divider']}; }}
            """
        )
        return button

    def _nav_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(48, 48)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.colors['bg_tertiary']};
                color: {self.colors['text_primary']};
                border: none;
                border-radius: 24px;
                font-size: 26px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self.colors['divider']}; }}
            """
        )
        return button

    def load_current(self):
        if not self.items:
            self.close()
            return
        self.current_index = max(0, min(self.current_index, len(self.items) - 1))
        item = self.items[self.current_index]
        file_path = item.get("file_url", "")
        self.title_label.setText(item.get("file_name") or f"Фото {self.current_index + 1}")
        self.caption_label.setText(item.get("text", ""))

        pixmap = QPixmap(file_path) if file_path and os.path.exists(file_path) else QPixmap()
        if pixmap.isNull():
            self.image_label.setText("Не удалось загрузить фото")
            self.image_label.setPixmap(QPixmap())
        else:
            self.image_label.setText("")
            self.image_label.set_source_pixmap(pixmap)

        self.prev_button.setVisible(len(self.items) > 1)
        self.next_button.setVisible(len(self.items) > 1)

    def show_previous(self):
        if len(self.items) < 2:
            return
        self.current_index = (self.current_index - 1) % len(self.items)
        self.load_current()

    def show_next(self):
        if len(self.items) < 2:
            return
        self.current_index = (self.current_index + 1) % len(self.items)
        self.load_current()

    def download_current(self):
        item = self.items[self.current_index]
        source = item.get("file_url", "")
        if not source or not os.path.exists(source):
            QMessageBox.warning(self, "Файл недоступен", "Исходный файл не найден.")
            return
        target, _ = QFileDialog.getSaveFileName(self, "Сохранить фото", item.get("file_name") or "photo.jpg")
        if not target:
            return
        try:
            shutil.copy2(source, target)
        except OSError as exc:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл: {exc}")

    def delete_current(self):
        item = self.items[self.current_index]
        self.delete_requested.emit(item.get("id", ""))
        self.accept()

    def mousePressEvent(self, event):
        self._drag_start = event.position().toPoint()
        if not self.content.geometry().contains(self._drag_start):
            self.reject()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        delta = event.position().toPoint() - self._drag_start
        if abs(delta.x()) > 80 and abs(delta.x()) > abs(delta.y()):
            if delta.x() > 0:
                self.show_previous()
            else:
                self.show_next()
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.show_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.show_next()
            return
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)
