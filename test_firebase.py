import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
import os

print("Текущая папка:", os.getcwd())
print("Файлы в папке:", os.listdir('.'))

try:
    # Проверяем наличие ключа
    if not os.path.exists("firebase-key.json"):
        print("❌ Файл firebase-key.json не найден!")
        print("Положи файл ключа в папку и переименуй в firebase-key.json")
    else:
        # Указываем путь к ключу
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
        
        # Подключаемся к базе
        db = firestore.client()
        
        # Пишем тестовое сообщение
        doc_ref = db.collection("test").document("hello")
        doc_ref.set({
            "message": "Ten Dem работает!",
            "timestamp": time.time()
        })
        
        print("✅ Тестовая запись создана!")
        
        # Читаем обратно
        doc = doc_ref.get()
        if doc.exists:
            print(f"✅ Прочитано: {doc.to_dict()}")
        else:
            print("❌ Документ не найден")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")