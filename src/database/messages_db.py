# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional, Callable, Any
from google.cloud.firestore import SERVER_TIMESTAMP
from database.firebase_client import get_db
from models.message import Message

class MessagesDB:
    @staticmethod
    def send_message(from_uid: str, to_uid: str, text: str) -> str:
        db = get_db()
        data = {
            'from_uid': from_uid,
            'to_uid': to_uid,
            'text': text,
            'timestamp': SERVER_TIMESTAMP,
            'read': False,
            'delivered': False
        }
        doc_ref = db.collection('messages').add(data)
        return doc_ref[1].id

    @staticmethod
    def get_messages(uid1: str, uid2: str, limit: int = 50) -> List[Message]:
        db = get_db()
        query1 = db.collection('messages').where('from_uid', '==', uid1).where('to_uid', '==', uid2).order_by('timestamp', direction='desc').limit(limit)
        query2 = db.collection('messages').where('from_uid', '==', uid2).where('to_uid', '==', uid1).order_by('timestamp', direction='desc').limit(limit)
        docs = list(query1.stream()) + list(query2.stream())
        messages = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            if data.get('timestamp'):
                data['datetime'] = data['timestamp'].datetime
            messages.append(Message.from_dict(data))
        messages.sort(key=lambda m: m.timestamp or datetime.min)
        return messages[-limit:] if len(messages) > limit else messages

    @staticmethod
    def listen_for_messages(callback: Callable[[List[Message]], None]) -> Any:
        db = get_db()
        def on_snapshot(doc_snapshot, changes, read_time):
            new_msgs = []
            for change in changes:
                if change.type.name == 'ADDED':
                    data = change.document.to_dict()
                    data['id'] = change.document.id
                    if data.get('timestamp'):
                        data['datetime'] = data['timestamp'].datetime
                    new_msgs.append(Message.from_dict(data))
            if new_msgs:
                callback(new_msgs)
        query = db.collection('messages').order_by('timestamp')
        return query.on_snapshot(on_snapshot)

    @staticmethod
    def mark_as_read(message_id: str):
        get_db().collection('messages').document(message_id).update({'read': True})

    @staticmethod
    def mark_as_delivered(message_id: str):
        get_db().collection('messages').document(message_id).update({'delivered': True})