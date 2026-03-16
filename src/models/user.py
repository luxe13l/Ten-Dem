# -*- coding: utf-8 -*-
"""
Модель пользователя для мессенджера.
Содержит основные поля и методы преобразования.
"""

from datetime import datetime
from typing import Optional


class User:
    """Класс, представляющий пользователя мессенджера."""

    def __init__(self,
                 uid: str,
                 phone: str,
                 name: str,
                 avatar_url: str = "",
                 status: str = "offline",
                 last_seen: Optional[datetime] = None):
        """
        Инициализация пользователя.

        Args:
            uid (str): уникальный идентификатор пользователя.
            phone (str): номер телефона.
            name (str): отображаемое имя.
            avatar_url (str, optional): ссылка на аватар.
            status (str, optional): статус ("online" или "offline").
            last_seen (datetime, optional): время последнего визита.
        """
        self.uid = uid
        self.phone = phone
        self.name = name
        self.avatar_url = avatar_url
        self.status = status
        self.last_seen = last_seen

    def to_dict(self) -> dict:
        """
        Преобразует объект пользователя в словарь для сохранения в Firestore.
        (Поле uid не включается, так как оно является идентификатором документа.)

        Returns:
            dict: словарь с данными пользователя.
        """
        return {
            'phone': self.phone,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'status': self.status,
            'last_seen': self.last_seen
        }

    @staticmethod
    def from_dict(data: dict) -> 'User':
        """
        Создаёт объект User из словаря, полученного из Firestore.

        Args:
            data (dict): словарь с полями пользователя (включая 'uid').

        Returns:
            User: объект пользователя.
        """
        return User(
            uid=data.get('uid', ''),
            phone=data.get('phone', ''),
            name=data.get('name', ''),
            avatar_url=data.get('avatar_url', ''),
            status=data.get('status', 'offline'),
            last_seen=data.get('last_seen')
        )

    def get_online_status(self) -> str:
        """
        Возвращает локализованный статус пользователя для отображения.

        Если статус "online" — возвращает "в сети".
        Иначе вычисляет время с last_seen:
            - менее 1 минуты назад: "только что"
            - менее 1 часа: "X мин. назад"
            - менее 1 дня: "X ч. назад"
            - иначе: дата в формате "дд.мм.гггг".

        Returns:
            str: строка статуса.
        """
        if self.status == "online":
            return "в сети"
        if not self.last_seen:
            return "давно"

        now = datetime.now()
        delta = now - self.last_seen
        seconds = delta.total_seconds()

        if seconds < 60:
            return "только что"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} мин. назад"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} ч. назад"
        else:
            return self.last_seen.strftime("%d.%m.%Y")