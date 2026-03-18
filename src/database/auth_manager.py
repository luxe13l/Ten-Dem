"""
Менеджер аутентификации Firebase для Ten Dem
"""
from src.database.firebase_client import get_db
from datetime import datetime


class AuthManager:
    """Управление аутентификацией пользователей."""
    
    def __init__(self):
        self.db = get_db()
        self.current_user = None
        self._temp_codes = {}  # Временное хранилище кодов
    
    def send_verification_code(self, phone):
        """
        Отправляет код подтверждения на номер телефона.
        
        Args:
            phone (str): Номер телефона
        
        Returns:
            tuple: (success: bool, message: str, verification_id: str)
        """
        try:
            # ДЛЯ ТЕСТА: генерируем код
            import random
            code = str(random.randint(100000, 999999))
            verification_id = f"test_{phone}_{datetime.now().timestamp()}"
            
            # Сохраняем код во временное хранилище
            self._temp_codes[verification_id] = {
                'phone': phone,
                'code': code,
                'created': datetime.now()
            }
            
            print(f"📱 Код для {phone}: {code} (тестовый режим)")
            
            return True, "Код отправлен", verification_id
            
        except Exception as e:
            return False, f"Ошибка отправки кода: {e}", ""
    
    def verify_code(self, verification_id, code):
        """
        Проверяет код подтверждения.
        
        Args:
            verification_id (str): ID верификации
            code (str): Введённый пользователем код
        
        Returns:
            tuple: (success: bool, message: str, phone: str)
        """
        try:
            if verification_id not in self._temp_codes:
                return False, "Неверный код верификации", ""
            
            stored = self._temp_codes[verification_id]
            
            # Проверяем не истёк ли код (5 минут)
            if (datetime.now() - stored['created']).total_seconds() > 300:
                return False, "Код истёк", ""
            
            # Проверяем код (для теста принимаем любой 6-значный)
            if len(code) != 6 or not code.isdigit():
                return False, "Код должен содержать 6 цифр", ""
            
            # Для теста всегда успешно
            phone = stored['phone']
            
            # Очищаем код
            del self._temp_codes[verification_id]
            
            return True, "Код подтверждён", phone
            
        except Exception as e:
            return False, f"Ошибка проверки кода: {e}", ""
    
    def check_username_available(self, username):
        """
        Проверяет доступность username.
        
        Args:
            username (str): Желаемый username
        
        Returns:
            bool: True если свободен
        """
        try:
            if not self.db:
                return True  # Если нет БД — считаем свободным
            
            users_ref = self.db.collection('users')
            
            # Запрос к Firebase
            query = users_ref.where('username', '==', username).limit(1)
            docs = query.stream()
            
            # Проверяем есть ли результаты
            result = len(list(docs)) == 0
            
            return result
            
        except Exception as e:
            print(f"Ошибка проверки username: {e}")
            return True  # При ошибке считаем свободным
    
    def create_user_profile(self, phone, name, surname, username):
        """
        Создаёт профиль пользователя в Firestore.
        
        Args:
            phone (str): Номер телефона
            name (str): Имя
            surname (str): Фамилия
            username (str): Username
        
        Returns:
            tuple: (success: bool, user_id: str, message: str)
        """
        try:
            if not self.db:
                return False, "", "База данных не подключена"
            
            # Проверяем username
            if not self.check_username_available(username):
                return False, "", "Username уже занят"
            
            users_ref = self.db.collection('users')
            
            user_data = {
                'phone': phone,
                'name': name,
                'surname': surname,
                'username': username,
                'full_name': f"{name} {surname}",
                'avatar_url': '',
                'status': 'online',
                'last_seen': datetime.now(),
                'theme': 'dark',
                'created_at': datetime.now()
            }
            
            doc_ref = users_ref.add(user_data)
            user_id = doc_ref[1].id
            
            self.current_user = {
                'uid': user_id,
                **user_data
            }
            
            return True, user_id, "Профиль создан"
            
        except Exception as e:
            return False, "", f"Ошибка создания профиля: {e}"
    
    def get_user_by_phone(self, phone):
        """
        Получает пользователя по номеру телефона.
        
        Args:
            phone (str): Номер телефона
        
        Returns:
            dict or None: Данные пользователя или None
        """
        try:
            if not self.db:
                return None
            
            users_ref = self.db.collection('users')
            query = users_ref.where('phone', '==', phone).limit(1)
            docs = query.stream()
            
            for doc in docs:
                return {'uid': doc.id, **doc.to_dict()}
            
            return None
            
        except Exception as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
    
    def set_current_user(self, user_data):
        """Устанавливает текущего пользователя."""
        self.current_user = user_data
    
    def get_current_user(self):
        """Получает текущего пользователя."""
        return self.current_user


# Глобальный экземпляр
auth_manager = AuthManager()