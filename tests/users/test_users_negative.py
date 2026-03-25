"""
tests/users/test_users_negative.py — негативные тесты для /user.

Проверяют корректную обработку ошибок при работе
с несуществующими пользователями и невалидными данными.
"""

from api.user_api import UserAPI
from utils.validators import ResponseValidator


class TestUsersNegative:
    """
    Негативные тесты для эндпоинтов /user.

    Намеренно передаём некорректные данные и проверяем коды ошибок.
    """

    def test_get_nonexistent_user(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
    ):
        """
        GET /user/{username} с несуществующим username.

        Пользователя с таким именем заведомо нет в системе.
        Ожидаем: 404 User not found.
        """
        nonexistent_username = "user_that_definitely_does_not_exist_99999"
        response = user_api.get_user(nonexistent_username)

        validator.validate_status_code(response, 404)
        validator.validate_is_json(response)

    def test_get_user_after_deletion(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
        user_payload: dict,
    ):
        """
        GET /user/{username} после удаления пользователя.

        Создаём пользователя, удаляем его, затем пытаемся получить —
        ожидаем 404 User not found.

        Примечание: PUT /user/{несуществующий} в Petstore делает upsert (создаёт),
        а не 404. Поэтому проверяем удаление через связку DELETE → GET.
        """
        username = user_payload["username"]

        # Создаём пользователя
        user_api.create_user(user_payload)

        # Удаляем его
        user_api.delete_user(username)

        # Пытаемся получить удалённого пользователя — должен вернуться 404
        response = user_api.get_user(username)
        validator.validate_status_code(response, 404)
        validator.validate_is_json(response)

    def test_delete_nonexistent_user(
        self,
        user_api: UserAPI,
        validator: ResponseValidator,
    ):
        """
        DELETE /user/{username} для несуществующего пользователя.

        Ожидаем: 404 User not found.
        """
        nonexistent_username = "user_that_definitely_does_not_exist_99999"
        response = user_api.delete_user(nonexistent_username)

        validator.validate_status_code(response, 404)
