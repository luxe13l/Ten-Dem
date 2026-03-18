"""
Модель сообщения для мессенджера Ten Dem
Поддерживает: текст, фото, файлы, голосовые, видео, ответы, пересылку
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class MessageType(Enum):
    """Типы сообщений."""
    TEXT = "text"
    PHOTO = "photo"
    FILE = "file"
    VOICE = "voice"
    VIDEO = "video"


class MessageStatus(Enum):
    """Статусы доставки сообщения."""
    SENT = "sent"           # ✓ Отправлено
    DELIVERED = "delivered" # ✓✓ Доставлено (серая)
    READ = "read"           # ✓✓ Прочитано (зелёная)


class Message:
    """Модель сообщения."""
    
    def __init__(
        self,
        id: str,
        from_uid: str,
        to_uid: str,
        text: str = "",
        message_type: MessageType = MessageType.TEXT,
        timestamp: datetime = None,
        status: MessageStatus = MessageStatus.SENT,
        file_url: str = "",
        file_name: str = "",
        file_size: int = 0,
        duration: int = 0,  # Для голосовых/видео (в секундах)
        reply_to_id: str = "",  # ID сообщения, на которое отвечаем
        forwarded_from_uid: str = "",  # ID пользователя, от которого переслано
        is_edited: bool = False,
        edited_at: datetime = None,
        is_deleted: bool = False,
        disappears_at: datetime = None,  # Для исчезающих сообщений
    ):
        self.id = id
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.text = text
        self.message_type = message_type
        self.timestamp = timestamp or datetime.now()
        self.status = status
        self.file_url = file_url
        self.file_name = file_name
        self.file_size = file_size
        self.duration = duration
        self.reply_to_id = reply_to_id
        self.forwarded_from_uid = forwarded_from_uid
        self.is_edited = is_edited
        self.edited_at = edited_at
        self.is_deleted = is_deleted
        self.disappears_at = disappears_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует сообщение в словарь для Firebase."""
        return {
            'id': self.id,
            'from_uid': self.from_uid,
            'to_uid': self.to_uid,
            'text': self.text,
            'message_type': self.message_type.value,
            'timestamp': self.timestamp,
            'status': self.status.value,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'duration': self.duration,
            'reply_to_id': self.reply_to_id,
            'forwarded_from_uid': self.forwarded_from_uid,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at,
            'is_deleted': self.is_deleted,
            'disappears_at': self.disappears_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], message_id: str = None):
        """Создаёт сообщение из словаря Firebase."""
        return cls(
            id=message_id or data.get('id', ''),
            from_uid=data.get('from_uid', ''),
            to_uid=data.get('to_uid', ''),
            text=data.get('text', ''),
            message_type=MessageType(data.get('message_type', 'text')),
            timestamp=data.get('timestamp', datetime.now()),
            status=MessageStatus(data.get('status', 'sent')),
            file_url=data.get('file_url', ''),
            file_name=data.get('file_name', ''),
            file_size=data.get('file_size', 0),
            duration=data.get('duration', 0),
            reply_to_id=data.get('reply_to_id', ''),
            forwarded_from_uid=data.get('forwarded_from_uid', ''),
            is_edited=data.get('is_edited', False),
            edited_at=data.get('edited_at'),
            is_deleted=data.get('is_deleted', False),
            disappears_at=data.get('disappears_at'),
        )
    
    def is_own(self, current_user_uid: str) -> bool:
        """Проверяет, является ли сообщение своим."""
        return self.from_uid == current_user_uid
    
    def get_display_text(self) -> str:
        """Возвращает текст для отображения в списке чатов."""
        if self.is_deleted:
            return "Сообщение удалено"
        
        if self.message_type == MessageType.PHOTO:
            return "📷 Фото"
        elif self.message_type == MessageType.FILE:
            return f"📁 {self.file_name}"
        elif self.message_type == MessageType.VOICE:
            return f"🎤 Голосовое ({self.duration}с)"
        elif self.message_type == MessageType.VIDEO:
            return f"📹 Видео ({self.duration}с)"
        else:
            return self.text[:40] + "..." if len(self.text) > 40 else self.text