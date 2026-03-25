"""
tests/users/test_users_positive.py — позитивные тесты для /user.

Проверяют успешные CRUD-операции над пользователями:
создание, получение, обновление и удаление.
"""

from api.user_api import UserAPI
from utils.validators import ResponseValidator


class TestUsersPositive:
    """
    Позитивные тесты для эндпоинтов /user.

    Фикстура created_user создаёт пользователя перед тестом
    и гарантирует его удаление после.
    """

    def test_create_user(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
        user_payload: dict,
    ):
        """
        POST /user — создание нового пользователя.

        В ответе поле "message" содержит ID созданного пользователя.
        """
        response = user_api.create_user(user_payload)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        # API возвращает ID пользователя как строку в поле "message"
        validator.validate_field(response, "message", str(user_payload["id"]))

    def test_get_user_by_username(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
        created_user: dict,
    ):
        """
        GET /user/{username} — получение пользователя по username.

        Фикстура created_user сначала создаёт пользователя через API.
        Тест запрашивает его по username и проверяет, что username совпадает.
        """
        username = created_user["username"]
        response = user_api.get_user(username)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "username", username)

    def test_update_user(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
        created_user: dict,
        user_payload: dict,
    ):
        """
        PUT /user/{username} — обновление данных пользователя.

        Обновляем пользователя новыми данными из user_payload.
        В ответе ожидаем ID нового payload (не старого created_user).
        """
        username = created_user["username"]
        response = user_api.update_user(username, user_payload)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "message", str(user_payload["id"]))

    def test_delete_user(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
        created_user: dict,
    ):
        """
        DELETE /user/{username} — удаление пользователя.

        После удаления API возвращает 200 и username в поле "message".
        Фикстура created_user попытается удалить повторно в teardown — это нормально.
        """
        username = created_user["username"]
        response = user_api.delete_user(username)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "message", username)

    def test_login(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
        created_user: dict,
    ):
        """
        GET /user/login — вход в систему с корректными данными.

        Используем данные реально созданного пользователя.
        Ожидаем: 200 и токен сессии в поле "message".
        """
        response = user_api.login(
            username=created_user["username"],
            password=created_user["password"],
        )

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        # Успешный логин возвращает строку вида "logged in user session:12345"
        assert "message" in response.json(), "Ответ должен содержать поле 'message'"
