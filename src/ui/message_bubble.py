"""Message bubble widget."""

from __future__ import annotations

import os

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.database.messages_db import QUICK_REACTIONS
from src.models.message import Message, MessageStatus, MessageType
from src.styles import FONT_FAMILY, RADIUS_MESSAGE
from src.styles.themes import get_theme_colors


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class MessageBubble(QWidget):
    clicked = pyqtSignal(str)
    photo_requested = pyqtSignal(str)
    reaction_clicked = pyqtSignal(str, str)

    def __init__(self, message: Message, is_own: bool, current_user_uid: str = "", parent=None):
        super().__init__(parent)
        self.message = message
        self.is_own = is_own
        self.current_user_uid = current_user_uid
        self.colors = get_theme_colors()
        self._animation: QPropertyAnimation | None = None
        self.build_ui()
        self.refresh()
        self.play_appear_animation()

    def build_ui(self):
        self.setStyleSheet("background: transparent;")
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(4)

        self.row = QHBoxLayout()
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(8)
        if self.is_own:
            self.row.addStretch()

        self.card = QFrame()
        self.card.setMaximumWidth(560)
        self.card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.row.addWidget(self.card)
        if not self.is_own:
            self.row.addStretch()

        self.selection_badge = QLabel("✓")
        self.selection_badge.setFixedSize(24, 24)
        self.selection_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.row.addWidget(self.selection_badge, 0, Qt.AlignmentFlag.AlignBottom)
        self.root.addLayout(self.row)

        self.content_layout = QVBoxLayout(self.card)
        self.content_layout.setContentsMargins(14, 10, 14, 10)
        self.content_layout.setSpacing(8)

        self.forwarded_label = QLabel()
        self.forwarded_label.hide()
        self.content_layout.addWidget(self.forwarded_label)

        self.photo_label = ClickableLabel()
        self.photo_label.setMinimumSize(240, 140)
        self.photo_label.setMaximumSize(360, 260)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setScaledContents(False)
        self.photo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.photo_label.clicked.connect(lambda: self.photo_requested.emit(self.message.id))
        self.photo_label.hide()
        self.content_layout.addWidget(self.photo_label)

        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.content_layout.addWidget(self.content_label)

        self.poll_label = QLabel()
        self.poll_label.setWordWrap(True)
        self.poll_label.hide()
        self.content_layout.addWidget(self.poll_label)

        self.meta_label = QLabel()
        self.meta_label.setAlignment(Qt.AlignmentFlag.AlignRight if self.is_own else Qt.AlignmentFlag.AlignLeft)
        self.content_layout.addWidget(self.meta_label)

        self.reactions_wrap = QWidget()
        self.reactions_wrap.setStyleSheet("background: transparent;")
        self.reactions_row = QHBoxLayout(self.reactions_wrap)
        self.reactions_row.setContentsMargins(0, 0, 0, 0)
        self.reactions_row.setSpacing(6)
        self.reactions_wrap.hide()
        self.root.addWidget(
            self.reactions_wrap,
            0,
            Qt.AlignmentFlag.AlignRight if self.is_own else Qt.AlignmentFlag.AlignLeft,
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.message.id)
        super().mousePressEvent(event)

    def refresh(self):
        self.colors = get_theme_colors()
        bg = self.colors["message_own_bg"] if self.is_own else self.colors["message_other_bg"]
        text = "#FFFFFF" if self.is_own else self.colors["text_primary"]
        meta = "#FFFFFF" if self.is_own else self.colors["text_tertiary"]
        if self.is_own and self.message.status == MessageStatus.READ:
            meta = self.colors["read_check"]
        elif self.is_own and self.message.status == MessageStatus.DELIVERED:
            meta = self.colors["delivered_check"]

        outline = self.colors["accent_primary"] if self.message.is_selected else "transparent"
        self.card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {bg};
                border-radius: {RADIUS_MESSAGE}px;
                border: 1px solid {outline};
            }}
            """
        )
        self.content_label.setStyleSheet(
            f"color: {text}; font-size: 15px; font-family: {FONT_FAMILY}; background: transparent;"
        )
        self.meta_label.setStyleSheet(
            f"color: {meta}; font-size: 11px; font-family: {FONT_FAMILY}; background: transparent;"
        )
        self.forwarded_label.setStyleSheet(
            f"color: {meta}; font-size: 11px; font-family: {FONT_FAMILY}; background: transparent;"
        )
        self.poll_label.setStyleSheet(
            f"color: {text}; font-size: 13px; font-family: {FONT_FAMILY}; "
            "background-color: rgba(255,255,255,0.06); border-radius: 12px; padding: 8px 10px;"
        )
        self.selection_badge.setStyleSheet(
            f"""
            QLabel {{
                background-color: {self.colors['accent_primary'] if self.message.is_selected else self.colors['bg_tertiary']};
                color: white;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
            }}
            """
        )
        self.selection_badge.setVisible(self.message.selection_enabled)

        self.forwarded_label.setVisible(bool(self.message.forwarded_from_uid))
        if self.message.forwarded_from_uid:
            self.forwarded_label.setText("Пересланное сообщение")

        self.content_label.setText(self._content_text())
        self.meta_label.setText(self._meta_text())
        self._refresh_photo_preview()
        self._refresh_poll()
        self._refresh_reactions()

    def update_message(self, message: Message):
        self.message = message
        self.refresh()

    def set_selection_state(self, enabled: bool, selected: bool):
        self.message.selection_enabled = enabled
        self.message.is_selected = selected
        self.refresh()

    def _refresh_photo_preview(self):
        should_show = self.message.message_type in {MessageType.PHOTO, MessageType.VIDEO}
        self.photo_label.setVisible(should_show)
        if not should_show:
            return
        source = self.message.file_url
        if source and os.path.exists(source):
            pixmap = QPixmap(source)
            if not pixmap.isNull():
                self.photo_label.setStyleSheet("background: transparent; border-radius: 16px;")
                self.photo_label.setText("")
                self.photo_label.setPixmap(
                    pixmap.scaled(
                        QSize(320, 220),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                return
        self.photo_label.setText("Открыть медиа")
        self.photo_label.setPixmap(QPixmap())
        self.photo_label.setStyleSheet(
            f"background-color: rgba(255,255,255,0.06); color: {self.colors['text_primary']}; border-radius: 16px;"
        )

    def _refresh_poll(self):
        if self.message.message_type != MessageType.POLL:
            self.poll_label.hide()
            return
        options = "\n".join(f"• {option}" for option in self.message.poll_options)
        self.poll_label.setText(options)
        self.poll_label.show()

    def _refresh_reactions(self):
        while self.reactions_row.count():
            item = self.reactions_row.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        reactions = self.message.reactions or {}
        visible = False
        for emoji in QUICK_REACTIONS:
            users = reactions.get(emoji, [])
            if not users:
                continue
            visible = True
            button = QPushButton(f"{emoji} {len(users)}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            active = self.current_user_uid in users
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {'rgba(47, 128, 237, 0.18)' if active else self.colors['bg_tertiary']};
                    color: {self.colors['text_primary']};
                    border: none;
                    border-radius: 12px;
                    padding: 2px 8px;
                    font-size: 11px;
                }}
                """
            )
            button.setFixedHeight(22)
            button.clicked.connect(lambda _, value=emoji: self.reaction_clicked.emit(self.message.id, value))
            self.reactions_row.addWidget(button)
        self.reactions_wrap.setVisible(visible)

    def play_appear_animation(self):
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self._animation = QPropertyAnimation(effect, b"opacity", self)
        self._animation.setDuration(180)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.finished.connect(lambda: self.setGraphicsEffect(None))
        self._animation.start()

    def _content_text(self):
        if self.message.message_type == MessageType.PHOTO:
            return self.message.text or self.message.file_name or "Фото"
        if self.message.message_type == MessageType.FILE:
            return f"Файл: {self.message.file_name or self.message.text}".strip()
        if self.message.message_type == MessageType.VOICE:
            return "Голосовое сообщение"
        if self.message.message_type == MessageType.VIDEO:
            return self.message.text or "Видео"
        if self.message.message_type == MessageType.POLL:
            return self.message.text
        return self.message.text

    def _meta_text(self):
        parts = [self.message.timestamp.strftime("%H:%M")]
        if self.message.is_edited:
            parts.append("изменено")
        if self.is_own:
            parts.append("✓✓" if self.message.status in (MessageStatus.READ, MessageStatus.DELIVERED) else "✓")
        return "  ".join(parts)
