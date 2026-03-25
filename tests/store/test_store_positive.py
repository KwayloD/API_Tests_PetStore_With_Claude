"""
tests/store/test_store_positive.py — позитивные тесты для /store.

Проверяют успешные сценарии работы с магазином:
получение инвентаря, создание и управление заказами.
"""

from api.store_api import StoreAPI
from utils.validators import ResponseValidator


class TestStorePositive:
    """
    Позитивные тесты для эндпоинтов /store.

    Тесты работают с реальным API Petstore.
    Фикстура created_order создаёт заказ до теста и удаляет после.
    """

    def test_get_inventory(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
    ):
        """
        GET /store/inventory — получение инвентаря магазина.

        Инвентарь — словарь, где ключи — статусы, значения — количество питомцев.
        Например: {"available": 150, "pending": 10, "sold": 45}
        """
        response = store_api.get_inventory()

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        # Инвентарь должен быть словарём
        assert isinstance(response.json(), dict), "Инвентарь должен быть словарём"

    def test_place_order(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        order_payload: dict,
    ):
        """
        POST /store/order — создание нового заказа на покупку питомца.

        Проверяем, что в ответе те же id, petId и quantity, что мы передали.
        """
        response = store_api.place_order(order_payload)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "id", order_payload["id"])
        validator.validate_field(response, "petId", order_payload["petId"])
        validator.validate_field(response, "quantity", order_payload["quantity"])

    def test_get_order_by_id(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        created_order: dict,
    ):
        """
        GET /store/order/{orderId} — получение заказа по ID.

        Фикстура created_order создаёт заказ через API перед тестом.
        Затем тест запрашивает его и проверяет ID в ответе.
        """
        order_id = created_order["id"]
        response = store_api.get_order_by_id(order_id)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "id", order_id)

    def test_delete_order(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        created_order: dict,
    ):
        """
        DELETE /store/order/{orderId} — удаление заказа.

        После удаления API возвращает 200 и ID заказа в поле "message".
        """
        order_id = created_order["id"]
        response = store_api.delete_order(order_id)

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        validator.validate_field(response, "message", str(order_id))
