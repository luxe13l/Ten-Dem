# -*- coding: utf-8 -*-
"""
Модуль инициализации Firebase Admin SDK.
Предоставляет функции для получения клиента Firestore.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional

# Глобальные переменные для хранения состояния
_initialized: bool = False
_db: Optional[firestore.Client] = None


def init_firebase() -> firestore.Client:
    """
    Инициализирует Firebase Admin SDK, используя файл ключа service account.

    Файл ключа должен называться 'firebase-key.json' и находиться в корневой папке проекта
    (рядом с main.py). Если файл не найден или ключ неверен, выбрасывается исключение.

    Возвращает:
        firestore.Client: клиент Firestore.

    Исключения:
        FileNotFoundError: если файл ключа не найден.
        Exception: при ошибках инициализации Firebase.
    """
    global _initialized, _db
    if _initialized:
        return _db

    # Определяем путь к корню проекта (где лежит main.py)
    # Текущий файл: src/database/firebase_client.py
    current_dir = os.path.dirname(os.path.abspath(__file__))          # src/database
    src_dir = os.path.dirname(current_dir)                            # src
    project_root = os.path.dirname(src_dir)                           # корень проекта
    key_path = os.path.join(project_root, 'firebase-key.json')

    if not os.path.exists(key_path):
        raise FileNotFoundError(
            f"Файл ключа Firebase не найден: {key_path}\n"
            "Убедитесь, что файл firebase-key.json находится в папке с программой."
        )

    try:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        _initialized = True
        return _db
    except Exception as e:
        # Перехватываем любые ошибки Firebase (неверный формат ключа, проблемы с сетью и т.д.)
        raise Exception(f"Ошибка инициализации Firebase: {e}")


def get_db() -> firestore.Client:
    """
    Возвращает клиент Firestore. Если Firebase ещё не инициализирован,
    автоматически вызывает init_firebase().

    Возвращает:
        firestore.Client: клиент Firestore.

    Исключения:
        Exception: если не удалось инициализировать Firebase.
    """
    if not _initialized:
        return init_firebase()
    return _db