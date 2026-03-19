"""
Точка входа в мессенджер Ten Dem
"""
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.database.firebase_client import init_firebase
from src.database.yandex_storage import init_yandex_storage
from src.ui.registration_wizard import RegistrationWizard
from src.ui.main_window import MainWindow


main_window_ref = None


def main():
    print("=== ЗАПУСК TEN DEM ===")
    
    try:
        print("1. Инициализация Firebase...")
        init_firebase()
        
        print("2. Инициализация Яндекс.Хранилища...")
        init_yandex_storage(
            access_key=os.getenv('YANDEX_ACCESS_KEY'),
            secret_key=os.getenv('YANDEX_SECRET_KEY'),
            bucket_name=os.getenv('YANDEX_BUCKET_NAME')
        )
        
        print("3. Создание QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Ten Dem")
        app.setStyle("Fusion")
        
        app.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #0F0F12;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        print("4. Создание окна регистрации...")
        wizard = RegistrationWizard()
        wizard.registration_complete.connect(lambda data: on_registration_complete(data, wizard, app))
        
        print("5. Показ окна регистрации...")
        wizard.show()
        
        print("6. Запуск...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter...")
        sys.exit(1)


def on_registration_complete(data, wizard, app):
    """Обработка завершения регистрации/входа"""
    global main_window_ref
    
    print(f"✅ Регистрация завершена: {data}")
    
    wizard.close()
    wizard.deleteLater()
    
    from src.models.user import User
    current_user = User(
        uid=data.get('uid', ''),
        phone=data.get('phone', ''),
        name=data.get('name', '')
    )
    
    print("7. Создание главного окна мессенджера...")
    main_window_ref = MainWindow(current_user)
    
    print("8. Показ главного окна...")
    main_window_ref.show()
    main_window_ref.raise_()
    main_window_ref.activateWindow()
    
    print(f"✅ Окно видно: {main_window_ref.isVisible()}")
    
    print("9. Загрузка контактов...")
    main_window_ref.load_contacts()
    
    print("✅ Мессенджер запущен!")


if __name__ == "__main__":
    main()