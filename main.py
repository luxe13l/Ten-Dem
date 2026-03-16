#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Точка входа в приложение Ten Dem Messenger.
Загружает настройки, инициализирует Firebase, показывает окно входа.
"""

import sys
import os

# Добавляем путь к src в sys.path для удобства импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from database.firebase_client import init_firebase
from ui.login_window import LoginWindow
from utils.settings import APP_NAME, ORGANIZATION_NAME


def main():
    # Настройки приложения
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
   

    # Инициализация Firebase (читает firebase-key.json из корня проекта)
    try:
        init_firebase()
    except Exception as e:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Ошибка Firebase",
                             f"Не удалось инициализировать Firebase: {e}\n"
                             "Убедитесь, что файл firebase-key.json находится в папке с программой.")
        sys.exit(1)

    # Показываем окно входа
    login_window = LoginWindow()
    if login_window.exec() == LoginWindow.DialogCode.Accepted:
        # После успешного входа открываем главное окно
        from ui.main_window import MainWindow
        main_win = MainWindow(login_window.current_user)
        main_win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()