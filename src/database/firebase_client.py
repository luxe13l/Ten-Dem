"""
Модуль инициализации Firebase для мессенджера Ten Dem
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore


_db_client = None


def init_firebase():
    """Инициализирует Firebase Admin SDK."""
    global _db_client
    
    try:
        key_path = os.path.join(os.path.dirname(__file__), '..', '..', 'firebase-key.json')
        key_path = os.path.abspath(key_path)
        
        print(f"Поиск ключа Firebase: {key_path}")
        
        if not os.path.exists(key_path):
            print(f"ОШИБКА: файл ключа Firebase не найден: {key_path}")
            print("Поместите firebase-key.json в корень проекта")
            return None
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            print("Firebase успешно инициализирован")
        
        _db_client = firestore.client()
        return _db_client
        
    except FileNotFoundError as e:
        print(f"Ошибка: файл ключа не найден - {e}")
        return None
    except Exception as e:
        print(f"Ошибка инициализации Firebase: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_db():
    """Возвращает клиент Firestore."""
    global _db_client
    
    if _db_client is None:
        _db_client = init_firebase()
    
    return _db_client