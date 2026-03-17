"""
Модуль работы с сообщениями в Firebase Firestore
"""
from datetime import datetime
from firebase_admin import firestore
from src.database.firebase_client import get_db


def send_message(from_uid, to_uid, text):
    """
    Отправляет сообщение между пользователями.
    """
    try:
        db = get_db()
        if db is None:
            return ""
        
        message_data = {
            'from_uid': from_uid,
            'to_uid': to_uid,
            'text': text,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'read': False,
            'delivered': False
        }
        
        messages_ref = db.collection('messages')
        doc_ref = messages_ref.add(message_data)
        
        return doc_ref[1].id
        
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return ""


def get_messages(uid1, uid2, limit=50):
    """
    Получает историю переписки между двумя пользователями.
    """
    try:
        db = get_db()
        if db is None:
            return []
        
        messages_ref = db.collection('messages')
        
        query = messages_ref.where(
            'from_uid', 'in', [uid1, uid2]
        ).where(
            'to_uid', 'in', [uid1, uid2]
        ).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
        
        docs = query.stream()
        messages = []
        
        for doc in docs:
            msg_data = doc.to_dict()
            if 'timestamp' in msg_data and hasattr(msg_data['timestamp'], 'to_pydatetime'):
                msg_data['timestamp'] = msg_data['timestamp'].to_pydatetime()
            messages.append({'id': doc.id, **msg_data})
        
        return sorted(messages, key=lambda x: x['timestamp'])
        
    except Exception as e:
        print(f"Ошибка получения сообщений: {e}")
        return []


def listen_for_messages(user_uid, callback):
    """
    Подписывается на новые сообщения для пользователя.
    """
    try:
        db = get_db()
        if db is None:
            return lambda: None
        
        messages_ref = db.collection('messages')
        query = messages_ref.where('to_uid', '==', user_uid).order_by('timestamp')
        
        def on_snapshot(docs, changes, read_time):
            for change in changes:
                if change.type.name == 'ADDED':
                    msg_data = change.document.to_dict()
                    if 'timestamp' in msg_data and hasattr(msg_data['timestamp'], 'to_pydatetime'):
                        msg_data['timestamp'] = msg_data['timestamp'].to_pydatetime()
                    callback({'id': change.document.id, **msg_data})
        
        return query.on_snapshot(on_snapshot)
        
    except Exception as e:
        print(f"Ошибка подписки на сообщения: {e}")
        return lambda: None


def mark_as_read(message_id):
    """
    Отмечает сообщение как прочитанное.
    """
    try:
        db = get_db()
        if db is None:
            return False
        
        db.collection('messages').document(message_id).update({'read': True})
        return True
    except Exception as e:
        print(f"Ошибка mark_as_read: {e}")
        return False


def mark_as_delivered(message_id):
    """
    Отмечает сообщение как доставленное.
    """
    try:
        db = get_db()
        if db is None:
            return False
        
        db.collection('messages').document(message_id).update({'delivered': True})
        return True
    except Exception as e:
        print(f"Ошибка mark_as_delivered: {e}")
        return False


def get_unread_count(user_uid):
    """
    Получает количество непрочитанных сообщений.
    """
    try:
        db = get_db()
        if db is None:
            return 0
        
        messages_ref = db.collection('messages')
        query = messages_ref.where('to_uid', '==', user_uid).where('read', '==', False)
        
        return len(list(query.stream()))
        
    except Exception as e:
        print(f"Ошибка получения непрочитанных: {e}")
        return 0


def mark_chat_as_read(user_uid, contact_uid):
    """
    Отмечает все сообщения от контакта как прочитанные.
    """
    try:
        db = get_db()
        if db is None:
            return False
        
        messages_ref = db.collection('messages')
        
        query = messages_ref.where(
            'from_uid', '==', contact_uid
        ).where(
            'to_uid', '==', user_uid
        ).where(
            'read', '==', False
        )
        
        docs = query.stream()
        for doc in docs:
            doc.reference.update({'read': True})
        
        return True
    except Exception as e:
        print(f"Ошибка mark_chat_as_read: {e}")
        return False