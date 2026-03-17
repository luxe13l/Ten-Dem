"""
Точка входа в мессенджер Ten Dem
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Добавляем корень проекта в путь импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow
from src.database.firebase_client import init_firebase
from src.utils.settings import COLOR_BACKGROUND, COLOR_TEXT_PRIMARY


def main():
    """Запуск приложения."""
    try:
        # Инициализация Firebase
        print("Инициализация Firebase...")
        init_firebase()
        
        # Создаём приложение
        print("Создание приложения...")
        app = QApplication(sys.argv)
        app.setApplicationName("Ten Dem")
        app.setStyle("Fusion")
        
        # Устанавливаем глобальный стиль
        app.setStyleSheet(f"""
            QMainWindow, QDialog, QWidget {{
                background-color: {COLOR_BACKGROUND};
                color: {COLOR_TEXT_PRIMARY};
                font-family: Segoe UI, Arial, sans-serif;
            }}
            QLineEdit, QTextEdit {{
                color: {COLOR_TEXT_PRIMARY};
                selection-background-color: #2481CC;
                selection-color: white;
            }}
            QPushButton {{
                color: white;
            }}
        """)
        
        # Показываем окно входа
        print("Показ окна входа...")
        login = LoginWindow()
        
        if login.exec() == 1 and login.get_user():
            # Успешный вход — показываем главное окно
            print("Вход успешен, показываем главное окно...")
            main_window = MainWindow(login.get_user())
            main_window.show()
            sys.exit(app.exec())
        else:
            # Отмена входа
            print("Вход отменён")
            sys.exit(0)
            
    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()