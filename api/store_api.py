"""
api/store_api.py — клиент для работы с эндпоинтами /store.

Содержит методы для управления заказами и получения инвентаря.
"""

import requests

from api.base_client import BaseClient


class StoreAPI(BaseClient):
    """
    API-клиент для ресурса /store.

    Наследует от BaseClient все HTTP-методы и логирование.
    Добавляет методы, специфичные для работы с магазином.

    Пример использования:
        store_api = StoreAPI()
        response = store_api.get_inventory()
    """

    def get_inventory(self) -> requests.Response:
        """
        Возвращает инвентарь магазина — количество питомцев по статусам.
        Эндпоинт: GET /store/inventory
        """
        return self.get("/store/inventory")

    def place_order(self, order_data: dict) -> requests.Response:
        """
        Создаёт новый заказ на покупку питомца.
        Эндпоинт: POST /store/order

        Args:
            order_data: словарь с данными заказа (id, petId, quantity и т.д.)
        """
        return self.post("/store/order", json=order_data)

    def get_order_by_id(self, order_id) -> requests.Response:
        """
        Возвращает заказ по ID.
        Эндпоинт: GET /store/order/{orderId}

        Args:
            order_id: числовой ID заказа (или строка для негативных тестов)
        """
        return self.get(f"/store/order/{order_id}")

    def delete_order(self, order_id) -> requests.Response:
        """
        Удаляет заказ по ID.
        Эндпоинт: DELETE /store/order/{orderId}

        Args:
            order_id: числовой ID заказа для удаления
        """
        return self.delete(f"/store/order/{order_id}")
