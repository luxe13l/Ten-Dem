# -*- coding: utf-8 -*-
"""
Модель сообщения для мессенджера.
Содержит поля и методы для работы с сообщениями.
"""

from datetime import datetime
from typing import Optional


class Message:
    """Класс, представляющий сообщение в чате."""

    def __init__(self,
                 from_uid: str,
                 to_uid: str,
                 text: str,
                 timestamp: Optional[datetime] = None,
                 message_id: str = "",
                 read: bool = False,
                 delivered: bool = False):
        """
        Инициализация сообщения.

        Args:
            from_uid (str): идентификатор отправителя.
            to_uid (str): идентификатор получателя.
            text (str): текст сообщения.
            timestamp (datetime, optional): время отправки.
            message_id (str, optional): идентификатор сообщения (заполняется после сохранения).
            read (bool, optional): прочитано ли сообщение.
            delivered (bool, optional): доставлено ли сообщение.
        """
        self.id = message_id
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.text = text
        self.timestamp = timestamp
        self.read = read
        self.delivered = delivered

    def to_dict(self) -> dict:
        """
        Преобразует объект сообщения в словарь для сохранения в Firestore.
        Поле id не включается, так как это идентификатор документа.

        Returns:
            dict: словарь с данными сообщения.
        """
        return {
            'from_uid': self.from_uid,
            'to_uid': self.to_uid,
            'text': self.text,
            'timestamp': self.timestamp,
            'read': self.read,
            'delivered': self.delivered
        }

    @staticmethod
    def from_dict(data: dict) -> 'Message':
        """
        Создаёт объект Message из словаря, полученного из Firestore.

        Args:
            data (dict): словарь с полями сообщения (включая 'id').

        Returns:
            Message: объект сообщения.
        """
        return Message(
            message_id=data.get('id', ''),
            from_uid=data.get('from_uid', ''),
            to_uid=data.get('to_uid', ''),
            text=data.get('text', ''),
            timestamp=data.get('datetime') or data.get('timestamp'),  # поддержка обоих ключей
            read=data.get('read', False),
            delivered=data.get('delivered', False)
        )

    def format_time(self) -> str:
        """
        Возвращает время отправки сообщения в формате "ЧЧ:ММ".
        Если временная метка отсутствует, возвращает пустую строку.

        Returns:
            str: отформатированное время.
        """
        if self.timestamp:
            return self.timestamp.strftime("%H:%M")
        return ""

    def get_status_icon(self) -> str:
        """
        Возвращает строковое представление статуса сообщения:
        - "✓" — отправлено (доставлено неизвестно или ещё нет)
        - "✓✓" — доставлено (delivered = true, read = false)
        - "✓✓" — прочитано (read = true) — но для визуального отличия можно использовать эмодзи,
                 однако в интерфейсе цвет будет задаваться отдельно.

        Returns:
            str: иконка статуса.
        """
        if self.read:
            return "✓✓"  # прочитано (две галочки)
        elif self.delivered:
            return "✓✓"  # доставлено (тоже две, но серые)
        else:
            return "✓"   # отправлено