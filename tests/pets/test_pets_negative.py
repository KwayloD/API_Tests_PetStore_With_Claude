"""
tests/pets/test_pets_negative.py — негативные тесты для /pet.

Негативные тесты проверяют, что API корректно обрабатывает ошибочные запросы:
возвращает правильные коды ошибок при несуществующих ресурсах или невалидных данных.
"""

from api.pet_api import PetAPI
from utils.validators import ResponseValidator


class TestPetsNegative:
    """
    Негативные тесты для эндпоинтов /pet.

    Эти тесты намеренно передают некорректные данные,
    чтобы убедиться, что API возвращает подходящие коды ошибок.
    """

    def test_get_pet_not_found(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
    ):
        """
        GET /pet/{petId} с несуществующим ID.

        Питомца с ID 999999999 заведомо нет в системе.
        Ожидаем: 404 Pet not found.
        """
        nonexistent_id = 999999999
        response = pet_api.get_pet_by_id(nonexistent_id)

        validator.validate_status_code(response, 404)
        validator.validate_is_json(response)

    def test_get_pet_invalid_id(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
    ):
        """
        GET /pet/{petId} с невалидным ID (строка вместо числа).

        API ожидает числовой ID. Строка "not-a-number" вызывает NumberFormatException
        на сервере. Petstore возвращает 404 (а не 400, как описано в Swagger).
        """
        invalid_id = "not-a-number"
        response = pet_api.get_pet_by_id(invalid_id)

        validator.validate_status_code(response, 404)
        validator.validate_is_json(response)

    def test_delete_nonexistent_pet(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
    ):
        """
        DELETE /pet/{petId} для несуществующего питомца.

        Ожидаем: 404 Pet not found.
        """
        nonexistent_id = 999999999
        response = pet_api.delete_pet(nonexistent_id)

        validator.validate_status_code(response, 404)
