"""
api/pet_api.py — клиент для работы с эндпоинтами /pet.

Содержит методы для CRUD-операций над питомцами в Petstore API.
"""

import requests

from api.base_client import BaseClient


class PetAPI(BaseClient):
    """
    API-клиент для ресурса /pet.

    Наследует от BaseClient все HTTP-методы и логирование.
    Добавляет методы, специфичные для работы с питомцами.

    Пример использования:
        pet_api = PetAPI()
        response = pet_api.create_pet({"id": 1, "name": "Rex", ...})
    """

    def create_pet(self, pet_data: dict) -> requests.Response:
        """
        Создаёт нового питомца.
        Эндпоинт: POST /pet

        Args:
            pet_data: словарь с данными питомца (id, name, status и т.д.)
        """
        return self.post("/pet", json=pet_data)

    def get_pets_by_status(self, status: str) -> requests.Response:
        """
        Возвращает список питомцев по статусу.
        Эндпоинт: GET /pet/findByStatus

        Args:
            status: "available", "pending" или "sold"
        """
        return self.get("/pet/findByStatus", params={"status": status})

    def get_pet_by_id(self, pet_id) -> requests.Response:
        """
        Возвращает питомца по ID.
        Эндпоинт: GET /pet/{petId}

        Args:
            pet_id: числовой ID питомца (или строка для негативных тестов)
        """
        return self.get(f"/pet/{pet_id}")

    def update_pet(self, pet_data: dict) -> requests.Response:
        """
        Обновляет данные питомца через JSON.
        Эндпоинт: PUT /pet

        Args:
            pet_data: полный объект питомца с обновлёнными полями
        """
        return self.put("/pet", json=pet_data)

    def update_pet_form(self, pet_id: int, name: str, status: str) -> requests.Response:
        """
        Обновляет имя и статус питомца через form-data.
        Эндпоинт: POST /pet/{petId}

        Args:
            pet_id: ID питомца для обновления
            name: новое имя питомца
            status: новый статус ("available", "pending", "sold")
        """
        return self.post(f"/pet/{pet_id}", data={"name": name, "status": status})

    def delete_pet(self, pet_id: int) -> requests.Response:
        """
        Удаляет питомца по ID.
        Эндпоинт: DELETE /pet/{petId}

        Args:
            pet_id: ID питомца для удаления
        """
        return self.delete(f"/pet/{pet_id}")
