"""
Модель сообщения для мессенджера Ten Dem
"""
from datetime import datetime


class Message:
    """Класс представления сообщения."""
    
    def __init__(self, from_uid, to_uid, text, timestamp=None, read=False, delivered=False, id=None):
        self.id = id
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.text = text
        self.timestamp = timestamp or datetime.now()
        self.read = read
        self.delivered = delivered
    
    def to_dict(self):
        """Конвертирует сообщение в словарь для Firebase."""
        return {
            'from_uid': self.from_uid,
            'to_uid': self.to_uid,
            'text': self.text,
            'timestamp': self.timestamp,
            'read': self.read,
            'delivered': self.delivered
        }
    
    @staticmethod
    def from_dict(data, doc_id=None):
        """Создаёт объект Message из словаря Firebase."""
        try:
            timestamp = data.get('timestamp')
            if timestamp and hasattr(timestamp, 'to_pydatetime'):
                timestamp = timestamp.to_pydatetime()
            
            return Message(
                from_uid=data.get('from_uid', ''),
                to_uid=data.get('to_uid', ''),
                text=data.get('text', ''),
                timestamp=timestamp,
                read=data.get('read', False),
                delivered=data.get('delivered', False),
                id=doc_id
            )
        except Exception:
            return Message(from_uid="", to_uid="", text="")
    
    def format_time(self):
        """Форматирует время сообщения."""
        try:
            now = datetime.now()
            msg_date = self.timestamp.date()
            today = now.date()
            
            if msg_date == today:
                return self.timestamp.strftime("%H:%M")
            elif msg_date == today.replace(day=today.day - 1):
                return "вчера"
            elif msg_date.year == today.year:
                return self.timestamp.strftime("%d %b")
            else:
                return self.timestamp.strftime("%d.%m.%Y")
        except Exception:
            return ""
    
    def get_status_icon(self, is_self=True):
        """Возвращает иконку статуса доставки."""
        if not is_self:
            return ""
        
        if self.read:
            return "✓✓"
        elif self.delivered:
            return "✓✓"
        else:
            return "✓"
    
    def __str__(self):
        return self.text