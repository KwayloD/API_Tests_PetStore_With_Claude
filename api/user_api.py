"""
api/user_api.py — клиент для работы с эндпоинтами /user.

Содержит методы для CRUD-операций над пользователями,
а также для входа и выхода из системы.
"""

import requests

from api.base_client import BaseClient


class UserAPI(BaseClient):
    """
    API-клиент для ресурса /user.

    Наследует от BaseClient все HTTP-методы и логирование.
    Добавляет методы, специфичные для работы с пользователями.

    Пример использования:
        user_api = UserAPI()
        response = user_api.create_user({"id": 1, "username": "john_doe", ...})
    """

    def create_user(self, user_data: dict) -> requests.Response:
        """
        Создаёт нового пользователя.
        Эндпоинт: POST /user

        Args:
            user_data: словарь с данными пользователя
        """
        return self.post("/user", json=user_data)

    def get_user(self, username: str) -> requests.Response:
        """
        Возвращает пользователя по username.
        Эндпоинт: GET /user/{username}

        Args:
            username: имя пользователя для поиска
        """
        return self.get(f"/user/{username}")

    def update_user(self, username: str, user_data: dict) -> requests.Response:
        """
        Обновляет данные пользователя по username.
        Эндпоинт: PUT /user/{username}

        Args:
            username: имя пользователя для обновления
            user_data: новые данные пользователя
        """
        return self.put(f"/user/{username}", json=user_data)

    def delete_user(self, username: str) -> requests.Response:
        """
        Удаляет пользователя по username.
        Эндпоинт: DELETE /user/{username}

        Args:
            username: имя пользователя для удаления
        """
        return self.delete(f"/user/{username}")

    def login(self, username: str, password: str) -> requests.Response:
        """
        Выполняет вход в систему.
        Эндпоинт: GET /user/login

        Args:
            username: имя пользователя
            password: пароль
        """
        return self.get("/user/login", params={"username": username, "password": password})

    def logout(self) -> requests.Response:
        """
        Выполняет выход из системы.
        Эндпоинт: GET /user/logout
        """
        return self.get("/user/logout")
