"""
tests/pets/test_pets_positive.py — позитивные тесты для /pet.

Позитивные тесты проверяют, что API работает корректно при
валидных входных данных: правильно создаёт, читает, обновляет и удаляет питомцев.
"""

import pytest

from api.pet_api import PetAPI
from utils.validators import ResponseValidator


class TestPetsPositive:
    """
    Позитивные тесты для эндпоинтов /pet.

    Каждый тест — независимый сценарий.
    Фикстуры из conftest.py обеспечивают подготовку данных и очистку после теста.
    """

    def test_create_pet(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
        pet_payload: dict,
    ):
        """
        POST /pet — создание нового питомца.

        Отправляем данные питомца и проверяем, что:
        - статус ответа 200
        - в ответе те же id и name, что мы передали
        - поле category является словарём с ключами id и name
        - поле tags является списком с ключами id и name
        """
        response = pet_api.create_pet(pet_payload)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "id", pet_payload["id"])
        validator.validate_field(response, "name", pet_payload["name"])
        validator.validate_dict_field(response, "category", ["id", "name"])
        validator.validate_list_field(response, "tags", ["id", "name"])

    @pytest.mark.parametrize("status", ["available", "pending", "sold"])
    def test_get_pets_by_status(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
        status: str,
    ):
        """
        GET /pet/findByStatus — поиск питомцев по статусу.

        Тест запускается 3 раза — для каждого из статусов.
        Проверяем, что каждый питомец в ответе имеет именно запрошенный статус.
        """
        response = pet_api.get_pets_by_status(status)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_list_items_status(response, "status", status)

    def test_get_pet_by_id(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
        created_pet: dict,
    ):
        """
        GET /pet/{petId} — получение питомца по ID.

        Фикстура created_pet сначала создаёт питомца через API,
        затем тест запрашивает его по ID и проверяет ответ.
        """
        pet_id = created_pet["id"]
        response = pet_api.get_pet_by_id(pet_id)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "id", pet_id)
        validator.validate_dict_field(response, "category", ["id", "name"])
        validator.validate_list_field(response, "tags", ["id", "name"])

    def test_update_pet_with_json(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
        pet_payload: dict,
    ):
        """
        PUT /pet — обновление данных питомца через JSON.

        Отправляем полный объект питомца и проверяем, что ответ его отражает.
        """
        response = pet_api.update_pet(pet_payload)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "id", pet_payload["id"])
        validator.validate_field(response, "name", pet_payload["name"])

    def test_update_pet_with_form_data(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
        created_pet: dict,
    ):
        """
        POST /pet/{petId} — обновление имени и статуса питомца через form-data.

        Этот эндпоинт принимает данные не как JSON, а как HTML-форму.
        В ответе поле "message" содержит ID изменённого питомца.
        """
        pet_id = created_pet["id"]
        response = pet_api.update_pet_form(pet_id, name="UpdatedName", status="sold")

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        # API возвращает ID питомца как строку в поле "message"
        validator.validate_field(response, "message", str(pet_id))

    def test_delete_pet(
        self,
        pet_api: PetAPI,
        validator: ResponseValidator,
        created_pet: dict,
    ):
        """
        DELETE /pet/{petId} — удаление питомца.

        После удаления API возвращает 200 и ID удалённого питомца в поле "message".

        Примечание: фикстура created_pet тоже попытается удалить питомца в teardown,
        но получит 404 — это ожидаемо и не влияет на результат теста.
        """
        pet_id = created_pet["id"]
        response = pet_api.delete_pet(pet_id)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "message", str(pet_id))
