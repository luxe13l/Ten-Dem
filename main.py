"""
Точка входа в мессенджер Ten Dem
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.database.firebase_client import init_firebase
from src.ui.registration_wizard import RegistrationWizard
from src.ui.main_window import MainWindow


# ✅ ГЛОБАЛЬНАЯ ПЕРЕМЕННАЯ (чтобы окно не удалилось)
main_window_ref = None


def main():
    print("=== ЗАПУСК TEN DEM ===")
    
    try:
        print("1. Инициализация Firebase...")
        init_firebase()
        
        print("2. Создание QApplication...")
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
        
        print("3. Создание окна регистрации...")
        wizard = RegistrationWizard()
        wizard.registration_complete.connect(lambda data: on_registration_complete(data, wizard, app))
        
        print("4. Показ окна регистрации...")
        wizard.show()
        
        print("5. Запуск...")
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
    
    try:
        # Закрываем окно регистрации
        wizard.close()
        wizard.deleteLater()
        
        # Создаём объект User из данных
        from src.models.user import User
        current_user = User(
            uid=data.get('uid', ''),
            phone=data.get('phone', ''),
            name=data.get('name', '')
        )
        
        print("6. Создание главного окна мессенджера...")
        
        # ✅ СОЗДАЁМ главное окно
        main_window_ref = MainWindow(current_user)
        
        print("7. Показ главного окна...")
        main_window_ref.show()
        main_window_ref.raise_()
        main_window_ref.activateWindow()
        
        # ✅ ПРОВЕРКА ПОСЛЕ show()
        print(f"✅ Окно видно ПОСЛЕ show(): {main_window_ref.isVisible()}")
        print(f"✅ Размер окна: {main_window_ref.size()}")
        
        # ✅ Загружаем контакты ПОСЛЕ показа окна (не блокирует UI)
        print("8. Загрузка контактов...")
        main_window_ref.load_contacts()
        
        print("✅ Мессенджер запущен!")
        
    except Exception as e:
        print(f"❌ Ошибка создания MainWindow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()