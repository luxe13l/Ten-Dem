# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional, List, Dict, Any
from database.firebase_client import get_db
from models.user import User

class UsersDB:
    @staticmethod
    def get_user(uid: str) -> Optional[User]:
        db = get_db()
        doc = db.collection('users').document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            data['uid'] = doc.id
            return User.from_dict(data)
        return None

    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[User]:
        db = get_db()
        docs = db.collection('users').where('phone', '==', phone).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['uid'] = doc.id
            return User.from_dict(data)
        return None

    @staticmethod
    def get_user_by_name(name: str) -> Optional[User]:
        db = get_db()
        docs = db.collection('users').where('name', '==', name).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['uid'] = doc.id
            return User.from_dict(data)
        return None

    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> str:
        db = get_db()
        default_data = {
            'phone': '',
            'name': '',
            'avatar_url': '',
            'status': 'offline',
            'last_seen': datetime.now(),
            'created_at': datetime.now()
        }
        data_to_save = {**default_data, **user_data}
        doc_ref = db.collection('users').add(data_to_save)
        return doc_ref[1].id

    @staticmethod
    def update_user(uid: str, data: Dict[str, Any]) -> None:
        db = get_db()
        db.collection('users').document(uid).update(data)

    @staticmethod
    def get_all_users(exclude_uid: Optional[str] = None) -> List[User]:
        db = get_db()
        users = []
        docs = db.collection('users').stream()
        for doc in docs:
            if exclude_uid and doc.id == exclude_uid:
                continue
            data = doc.to_dict()
            data['uid'] = doc.id
            users.append(User.from_dict(data))
        return users

    @staticmethod
    def set_online_status(uid: str, status: str) -> None:
        UsersDB.update_user(uid, {'status': status, 'last_seen': datetime.now()})