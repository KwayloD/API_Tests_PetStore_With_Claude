"""
tests/store/test_store_negative.py — негативные тесты для /store.

Проверяют корректную обработку ошибок при работе с несуществующими
или невалидными заказами.
"""

from api.store_api import StoreAPI
from utils.validators import ResponseValidator


class TestStoreNegative:
    """
    Негативные тесты для эндпоинтов /store.

    Передаём некорректные данные и проверяем, что API возвращает
    подходящие HTTP-коды ошибок.
    """

    def test_get_order_not_found(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
    ):
        """
        GET /store/order/{orderId} с несуществующим ID.

        Заказа с ID 999999999 в системе нет.
        Ожидаем: 404 Order Not Found.
        """
        nonexistent_id = 999999999
        response = store_api.get_order_by_id(nonexistent_id)

        validator.validate_status_code(response, 404)
        validator.validate_is_json(response)

    def test_get_order_invalid_id(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
    ):
        """
        GET /store/order/{orderId} с невалидным ID (строка вместо числа).

        API ожидает числовой orderId. Строка вызывает NumberFormatException на сервере.
        Petstore возвращает 404 (а не 400, как описано в Swagger).
        """
        invalid_id = "invalid-id"
        response = store_api.get_order_by_id(invalid_id)

        validator.validate_status_code(response, 404)
        validator.validate_is_json(response)
