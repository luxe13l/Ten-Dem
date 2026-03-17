"""
Модуль работы с пользователями в Firebase Firestore
"""
from datetime import datetime
from src.database.firebase_client import get_db


def get_user_by_phone(phone):
    """Получает пользователя по номеру телефона."""
    try:
        db = get_db()
        if db is None:
            return None
        
        users_ref = db.collection('users')
        query = users_ref.where('phone', '==', phone).limit(1)
        docs = query.stream()
        
        for doc in docs:
            return {'uid': doc.id, **doc.to_dict()}
        
        return None
        
    except Exception as e:
        print(f"Ошибка получения пользователя: {e}")
        return None


def create_user(user_data):
    """Создаёт нового пользователя в базе."""
    try:
        db = get_db()
        if db is None:
            return ""
        
        users_ref = db.collection('users')
        doc_ref = users_ref.add(user_data)
        
        return doc_ref[1].id
        
    except Exception as e:
        print(f"Ошибка создания пользователя: {e}")
        return ""


def update_user(uid, data):
    """Обновляет данные пользователя."""
    try:
        db = get_db()
        if db is None:
            return False
        
        # Проверяем существование документа перед обновлением
        users_ref = db.collection('users')
        doc = users_ref.document(uid).get()
        
        if not doc.exists:
            print(f"Предупреждение: документ {uid} не найден, создаём новый")
            # Создаём новый документ с данными
            new_data = {**data, 'uid': uid}
            users_ref.document(uid).set(new_data)
            return True
        
        users_ref.document(uid).update(data)
        return True
        
    except Exception as e:
        print(f"Ошибка обновления пользователя: {e}")
        return False


def get_all_users():
    """Получает список всех пользователей."""
    try:
        db = get_db()
        if db is None:
            return []
        
        users_ref = db.collection('users')
        docs = users_ref.stream()
        
        return [{'uid': doc.id, **doc.to_dict()} for doc in docs]
        
    except Exception as e:
        print(f"Ошибка получения списка пользователей: {e}")
        return []


def set_online_status(uid, status):
    """Устанавливает статус онлайн/оффлайн."""
    try:
        db = get_db()
        if db is None:
            return False
        
        data = {
            'status': status,
            'last_seen': datetime.now()
        }
        
        return update_user(uid, data)
        
    except Exception as e:
        print(f"Ошибка обновления статуса: {e}")
        return False