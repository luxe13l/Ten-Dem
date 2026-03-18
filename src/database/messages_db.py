"""
База данных сообщений для Ten Dem
Поддерживает: отправку, получение, редактирование, удаление, статусы
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from src.database.firebase_client import get_db
from src.models.message import Message, MessageType, MessageStatus
import uuid


def send_message(
    from_uid: str,
    to_uid: str,
    text: str = "",
    message_type: MessageType = MessageType.TEXT,
    file_url: str = "",
    file_name: str = "",
    file_size: int = 0,
    duration: int = 0,
    reply_to_id: str = "",
    forwarded_from_uid: str = "",
    disappears_in: int = 0,  # Исчезнет через N секунд
) -> Optional[str]:
    """
    Отправляет сообщение.
    
    Returns:
        ID сообщения или None при ошибке
    """
    try:
        db = get_db()
        if not db:
            return None
        
        message_id = str(uuid.uuid4())
        
        # Время исчезновения (если указано)
        disappears_at = None
        if disappears_in > 0:
            from datetime import timedelta
            disappears_at = datetime.now() + timedelta(seconds=disappears_in)
        
        message_data = {
            'id': message_id,
            'from_uid': from_uid,
            'to_uid': to_uid,
            'text': text,
            'message_type': message_type.value,
            'timestamp': datetime.now(),
            'status': MessageStatus.SENT.value,
            'file_url': file_url,
            'file_name': file_name,
            'file_size': file_size,
            'duration': duration,
            'reply_to_id': reply_to_id,
            'forwarded_from_uid': forwarded_from_uid,
            'is_edited': False,
            'is_deleted': False,
            'disappears_at': disappears_at,
        }
        
        # Сохраняем в коллекцию сообщений
        messages_ref = db.collection('messages')
        messages_ref.add(message_data)
        
        # Обновляем последнее сообщение в чате
        _update_last_message(from_uid, to_uid, message_data)
        
        return message_id
        
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return None


def edit_message(message_id: str, new_text: str) -> bool:
    """
    Редактирует сообщение.
    
    Returns:
        True если успешно
    """
    try:
        db = get_db()
        if not db:
            return False
        
        messages_ref = db.collection('messages')
        query = messages_ref.where('id', '==', message_id).limit(1)
        docs = query.stream()
        
        for doc in docs:
            doc.reference.update({
                'text': new_text,
                'is_edited': True,
                'edited_at': datetime.now(),
            })
            return True
        
        return False
        
    except Exception as e:
        print(f"Ошибка редактирования сообщения: {e}")
        return False


def delete_message(message_id: str, for_everyone: bool = False) -> bool:
    """
    Удаляет сообщение.
    
    Args:
        message_id: ID сообщения
        for_everyone: Если True — удалить для всех, иначе — только для себя
    
    Returns:
        True если успешно
    """
    try:
        db = get_db()
        if not db:
            return False
        
        messages_ref = db.collection('messages')
        query = messages_ref.where('id', '==', message_id).limit(1)
        docs = query.stream()
        
        for doc in docs:
            if for_everyone:
                # Полное удаление
                doc.reference.delete()
            else:
                # Пометить как удалённое
                doc.reference.update({
                    'is_deleted': True,
                    'text': 'Сообщение удалено',
                })
            return True
        
        return False
        
    except Exception as e:
        print(f"Ошибка удаления сообщения: {e}")
        return False


def mark_as_read(message_id: str) -> bool:
    """
    Отмечает сообщение как прочитанное.
    
    Returns:
        True если успешно
    """
    try:
        db = get_db()
        if not db:
            return False
        
        messages_ref = db.collection('messages')
        query = messages_ref.where('id', '==', message_id).limit(1)
        docs = query.stream()
        
        for doc in docs:
            doc.reference.update({
                'status': MessageStatus.READ.value,
            })
            return True
        
        return False
        
    except Exception as e:
        print(f"Ошибка mark_as_read: {e}")
        return False


def mark_chat_as_read(user_uid: str, contact_uid: str) -> bool:
    """
    Отмечает все сообщения в чате как прочитанные.
    
    Returns:
        True если успешно
    """
    try:
        db = get_db()
        if not db:
            return False
        
        messages_ref = db.collection('messages')
        
        # Все сообщения от контакта к пользователю
        query = messages_ref.where('from_uid', '==', contact_uid)\
                           .where('to_uid', '==', user_uid)\
                           .where('status', '!=', MessageStatus.READ.value)
        
        docs = query.stream()
        for doc in docs:
            doc.reference.update({
                'status': MessageStatus.READ.value,
            })
        
        return True
        
    except Exception as e:
        print(f"Ошибка mark_chat_as_read: {e}")
        return False


def get_messages(user_uid: str, contact_uid: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Получает историю переписки.
    
    Returns:
        Список сообщений (словари)
    """
    try:
        db = get_db()
        if not db:
            return []
        
        messages_ref = db.collection('messages')
        
        # Сообщения между пользователями (в обе стороны)
        query = messages_ref.where('from_uid', 'in', [user_uid, contact_uid])\
                           .where('to_uid', 'in', [user_uid, contact_uid])\
                           .order_by('timestamp', direction='DESCENDING')\
                           .limit(limit)
        
        docs = query.stream()
        messages = []
        for doc in docs:
            messages.append({'id': doc.id, **doc.to_dict()})
        
        # Разворачиваем чтобы старые были сверху
        messages.reverse()
        
        return messages
        
    except Exception as e:
        print(f"Ошибка получения сообщений: {e}")
        return []


def listen_for_messages(user_uid: str, callback: Callable) -> Callable:
    """
    Подписывается на новые сообщения.
    
    Args:
        user_uid: ID текущего пользователя
        callback: Функция обратного вызова при новом сообщении
    
    Returns:
        Функция для отписки
    """
    try:
        db = get_db()
        if not db:
            return lambda: None
        
        messages_ref = db.collection('messages')
        
        def on_snapshot(docs, changes, read_time):
            for doc in docs:
                data = {'id': doc.id, **doc.to_dict()}
                # Только сообщения для текущего пользователя
                if data.get('to_uid') == user_uid:
                    callback(data)
        
        # Слушаем сообщения для этого пользователя
        query = messages_ref.where('to_uid', '==', user_uid)\
                           .order_by('timestamp', direction='DESCENDING')\
                           .limit(10)
        
        listener = query.on_snapshot(on_snapshot)
        
        return lambda: listener.remove()
        
    except Exception as e:
        print(f"Ошибка listen_for_messages: {e}")
        return lambda: None


def _update_last_message(uid1: str, uid2: str, message_data: Dict[str, Any]):
    """Обновляет последнее сообщение в чате (для списка контактов)."""
    try:
        db = get_db()
        if not db:
            return
        
        chats_ref = db.collection('chats')
        
        # ID чата — отсортированные UID
        chat_id = '_'.join(sorted([uid1, uid2]))
        
        chat_data = {
            'participants': [uid1, uid2],
            'last_message': message_data.get('text', ''),
            'last_message_type': message_data.get('message_type', 'text'),
            'last_message_time': message_data.get('timestamp', datetime.now()),
            'updated_at': datetime.now(),
        }
        
        chats_ref.document(chat_id).set(chat_data, merge=True)
        
    except Exception as e:
        print(f"Ошибка _update_last_message: {e}")


# ==================== НОВЫЕ ФУНКЦИИ ДЛЯ ЭТАПА 1 ====================

def get_message_by_id(message_id: str) -> Optional[Dict[str, Any]]:
    """Получает сообщение по ID."""
    try:
        db = get_db()
        if not db:
            return None
        
        messages_ref = db.collection('messages')
        query = messages_ref.where('id', '==', message_id).limit(1)
        docs = query.stream()
        
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        
        return None
        
    except Exception as e:
        print(f"Ошибка get_message_by_id: {e}")
        return None


def forward_message(
    from_uid: str,
    to_uid: str,
    original_message_id: str,
    new_to_uid: str,
) -> Optional[str]:
    """
    Пересылает сообщение.
    
    Returns:
        ID нового сообщения или None
    """
    try:
        original = get_message_by_id(original_message_id)
        if not original:
            return None
        
        return send_message(
            from_uid=from_uid,
            to_uid=new_to_uid,
            text=original.get('text', ''),
            message_type=MessageType(original.get('message_type', 'text')),
            file_url=original.get('file_url', ''),
            file_name=original.get('file_name', ''),
            file_size=original.get('file_size', 0),
            duration=original.get('duration', 0),
            forwarded_from_uid=from_uid,
        )
        
    except Exception as e:
        print(f"Ошибка forward_message: {e}")
        return None


def get_media_gallery(user_uid: str, contact_uid: str, media_type: str = 'photo') -> List[Dict[str, Any]]:
    """
    Получает галерею медиа из чата.
    
    Args:
        media_type: 'photo', 'video', 'file', 'voice'
    
    Returns:
        Список медиа-сообщений
    """
    try:
        db = get_db()
        if not db:
            return []
        
        messages_ref = db.collection('messages')
        
        query = messages_ref.where('from_uid', 'in', [user_uid, contact_uid])\
                           .where('to_uid', 'in', [user_uid, contact_uid])\
                           .where('message_type', '==', media_type)\
                           .order_by('timestamp', direction='DESCENDING')
        
        docs = query.stream()
        media = []
        for doc in docs:
            data = {'id': doc.id, **doc.to_dict()}
            if not data.get('is_deleted', False):
                media.append(data)
        
        return media
        
    except Exception as e:
        print(f"Ошибка get_media_gallery: {e}")
        return []