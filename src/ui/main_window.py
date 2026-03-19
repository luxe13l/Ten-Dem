"""Main messenger window."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.database.messages_db import get_chat_summaries
from src.database.users_db import get_all_users, set_online_status
from src.models.user import User
from src.styles import FONT_FAMILY, LEFT_PANEL_WIDTH, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from src.styles.themes import get_theme_colors
from src.ui.chat_widget import ChatWidget
from src.ui.contact_item import ContactItem
from src.ui.contact_info_dialog import ContactInfoDialog
from src.ui.settings_window import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.colors = get_theme_colors(getattr(self.current_user, "theme", "dark"))
        self.current_chat_widget = None
        self.settings_window = None
        self.contact_widgets = {}
        self.init_ui()
        set_online_status(self.current_user.uid, "online")

    def init_ui(self):
        self.setWindowTitle(f"Ten Dem | {self.current_user.name}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(1280, 820)
        self.setStyleSheet(f"background-color: {self.colors['bg_primary']};")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._create_sidebar())
        layout.addWidget(self._create_right_panel(), 1)

    def _create_sidebar(self):
        panel = QWidget()
        panel.setFixedWidth(LEFT_PANEL_WIDTH)
        panel.setStyleSheet(
            f"QWidget {{ background-color: {self.colors['bg_secondary']}; border-right: 1px solid {self.colors['divider']}; }}"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(20, 20, 20, 16)
        title = QLabel("Ten Dem")
        title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.colors['text_primary']};")
        header.addWidget(title)
        header.addStretch()

        settings_btn = QPushButton()
        settings_btn.setFixedSize(40, 40)
        settings_btn.setIcon(QIcon("assets/icons/settings.svg"))
        settings_btn.setIconSize(QSize(18, 18))
        settings_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {self.colors['icon_default']};
                border: none;
                border-radius: 12px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['bg_tertiary']};
                color: {self.colors['text_primary']};
            }}
            """
        )
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn)
        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск")
        self.search_input.textChanged.connect(self.filter_contacts)
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                margin: 0 16px 16px 16px;
                padding: 12px 16px;
                border: 1px solid {self.colors['divider']};
                border-radius: 18px;
                background-color: {self.colors['bg_tertiary']};
                color: {self.colors['text_primary']};
                font-size: 14px;
            }}
            """
        )
        layout.addWidget(self.search_input)

        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self.open_chat)
        self.contacts_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.contacts_list.customContextMenuRequested.connect(self.open_contact_menu)
        self.contacts_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                margin: 0 8px 6px 8px;
                border-radius: 14px;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['bg_tertiary']};
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['bg_tertiary']};
            }}
            """
        )
        layout.addWidget(self.contacts_list, 1)
        return panel

    def _create_right_panel(self):
        self.right_panel = QWidget()
        self.right_panel.setStyleSheet(f"background-color: {self.colors['bg_primary']};")
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel("TD")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(96, 96)
        icon.setStyleSheet(
            f"""
            QLabel {{
                background-color: {self.colors['accent_primary']};
                color: white;
                border-radius: 48px;
                font-size: 30px;
                font-weight: 700;
            }}
            """
        )
        text = QLabel("Выберите чат, чтобы начать общение")
        text.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 18px;")
        placeholder_layout.addWidget(icon)
        placeholder_layout.addSpacing(18)
        placeholder_layout.addWidget(text)
        right_layout.addWidget(self.placeholder)
        return self.right_panel

    def open_settings(self):
        self.settings_window = SettingsWindow(self.current_user, self)
        self.settings_window.settings_saved.connect(self.on_settings_saved)
        self.settings_window.exec()

    def on_settings_saved(self, settings):
        self.current_user.name = settings.get("name", self.current_user.name)
        self.current_user.theme = settings.get("theme", getattr(self.current_user, "theme", "dark"))
        self.colors = get_theme_colors(self.current_user.theme)
        self.setWindowTitle(f"Ten Dem | {self.current_user.name}")
        old = self.takeCentralWidget()
        if old:
            old.deleteLater()
        self.init_ui()
        self.load_contacts()

    def load_contacts(self):
        self.contacts_list.clear()
        self.contact_widgets.clear()
        summaries = get_chat_summaries(self.current_user.uid)
        all_users = get_all_users()
        if not all_users:
            all_users = [
                {"uid": "demo-alex", "name": "Алексей", "phone": "+79991111111", "status": "online"},
                {"uid": "demo-maria", "name": "Мария", "phone": "+79992222222", "status": "offline"},
            ]
        for user_data in all_users:
            if user_data.get("uid") == self.current_user.uid:
                continue
            user = User.from_dict(user_data, user_data.get("uid"))
            summary = summaries.get(user.uid, {})
            item = QListWidgetItem()
            widget = ContactItem(
                user,
                last_message=summary.get("last_message", "Начните разговор"),
                unread_count=summary.get("unread_count", 0),
                timestamp=summary.get("timestamp"),
            )
            item.setSizeHint(widget.sizeHint())
            self.contacts_list.addItem(item)
            self.contacts_list.setItemWidget(item, widget)
            self.contact_widgets[user.uid] = widget

    def filter_contacts(self, text: str):
        text = text.strip().lower()
        for index in range(self.contacts_list.count()):
            item = self.contacts_list.item(index)
            widget = self.contacts_list.itemWidget(item)
            name = getattr(getattr(widget, "user", None), "name", "").lower()
            item.setHidden(text not in name)

    def open_chat(self, item: QListWidgetItem):
        contact_widget = self.contacts_list.itemWidget(item)
        if not contact_widget:
            return
        if self.placeholder is not None:
            self.placeholder.deleteLater()
            self.placeholder = None
        if self.current_chat_widget is not None:
            self.current_chat_widget.deleteLater()
        self.current_chat_widget = ChatWidget(self.current_user, contact_widget.user, self.right_panel)
        self.current_chat_widget.chat_updated.connect(self.refresh_contacts)
        self.right_panel.layout().addWidget(self.current_chat_widget)

    def refresh_contacts(self, _contact_uid: str = ""):
        if not _contact_uid or _contact_uid not in self.contact_widgets:
            self.load_contacts()
            return
        from src.database.messages_db import get_chat_summaries

        summary = get_chat_summaries(self.current_user.uid).get(_contact_uid, {})
        widget = self.contact_widgets.get(_contact_uid)
        if widget:
            widget.update_preview(
                last_message=summary.get("last_message", widget.last_message),
                timestamp=summary.get("timestamp", widget.timestamp),
                unread_count=summary.get("unread_count", widget.unread_count),
            )

    def open_contact_menu(self, pos):
        item = self.contacts_list.itemAt(pos)
        if not item:
            return
        widget = self.contacts_list.itemWidget(item)
        if not widget:
            return
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.setStyleSheet(
            f"""
            QMenu {{ background-color: {self.colors['bg_secondary']}; color: {self.colors['text_primary']}; border: 1px solid {self.colors['divider']}; }}
            QMenu::item {{ padding: 8px 16px; }}
            QMenu::item:selected {{ background-color: {self.colors['bg_tertiary']}; }}
            """
        )
        info_action = menu.addAction("Информация о контакте")
        open_action = menu.addAction("Открыть чат")
        action = menu.exec(self.contacts_list.mapToGlobal(pos))
        if action == open_action:
            self.open_chat(item)
        elif action == info_action:
            ContactInfoDialog(self.current_user, widget.user, self).exec()

    def closeEvent(self, event):
        set_online_status(self.current_user.uid, "offline")
        event.accept()
