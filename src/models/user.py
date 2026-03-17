"""
Модель пользователя для мессенджера Ten Dem
"""
from datetime import datetime, timedelta


class User:
    """Класс представления пользователя."""
    
    def __init__(self, uid, phone, name, avatar_url="", status="offline", last_seen=None):
        self.uid = uid
        self.phone = phone
        self.name = name
        self.avatar_url = avatar_url
        self.status = status
        self.last_seen = last_seen or datetime.now()
    
    def to_dict(self):
        """Конвертирует объект в словарь для Firebase."""
        return {
            'phone': self.phone,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'status': self.status,
            'last_seen': self.last_seen
        }
    
    @staticmethod
    def from_dict(data, doc_id=None):
        """Создаёт объект User из словаря Firebase."""
        try:
            last_seen = data.get('last_seen')
            if last_seen and hasattr(last_seen, 'to_pydatetime'):
                last_seen = last_seen.to_pydatetime()
            
            return User(
                uid=doc_id or data.get('uid', ''),
                phone=data.get('phone', ''),
                name=data.get('name', ''),
                avatar_url=data.get('avatar_url', ''),
                status=data.get('status', 'offline'),
                last_seen=last_seen
            )
        except Exception:
            return User(uid="", phone="", name="Неизвестный")
    
    def get_online_status(self):
        """Возвращает статус онлайн."""
        try:
            if self.status == "online":
                return "online"
            
            if not self.last_seen:
                return "был(а) давно"
            
            if datetime.now() - self.last_seen < timedelta(minutes=5):
                return "был(а) недавно"
            
            return f"был(а) {self.last_seen.strftime('%d.%m %H:%M')}"
        except Exception:
            return "offline"
    
    def __str__(self):
        return self.name