"""
Точка входа в мессенджер Ten Dem
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.database.firebase_client import init_firebase
from src.ui.registration_wizard import RegistrationWizard


def main():
    print("=== ЗАПУСК TEN DEM ===")
    
    try:
        # Инициализация Firebase
        print("1. Инициализация Firebase...")
        init_firebase()
        
        # Создание приложения
        print("2. Создание QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Ten Dem")
        app.setStyle("Fusion")
        
        # Глобальный стиль - тёмная тема
        app.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #0F0F12;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit, QTextEdit {
                background-color: #25262B;
                color: #FFFFFF;
                border: 1px solid #3C3E44;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 15px;
                selection-background-color: #6C5CE7;
                selection-color: #FFFFFF;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #6C5CE7;
            }
            QPushButton {
                background-color: #6C5CE7;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #5A4EC7;
            }
            QPushButton:pressed {
                background-color: #4A3FB8;
            }
            QPushButton:disabled {
                background-color: #2A2B30;
                color: #5D5F67;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1A1B1E;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #3C3E44;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6C5CE7;
            }
        """)
        
        # Создание мастера регистрации
        print("3. Создание окна регистрации...")
        wizard = RegistrationWizard()
        wizard.registration_complete.connect(lambda data: on_registration_complete(data, wizard))
        
        print("4. Показ окна...")
        wizard.show()
        
        print("5. Запуск...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter...")
        sys.exit(1)


def on_registration_complete(data, wizard):
    """Обработка завершения регистрации."""
    print(f"✅ Регистрация завершена: {data}")
    # Здесь будет создание главного окна
    wizard.close()


if __name__ == "__main__":
    main()