"""
tests/store/test_store_mock.py — тесты с мок-данными для /store.

В отличие от остальных тестов, здесь реальные HTTP-запросы НЕ отправляются.
Библиотека requests-mock перехватывает запросы и возвращает заранее
настроенные ответы из фикстур conftest.py.

Мок-тесты полезны для:
- Симуляции редких или труднодостижимых ситуаций (500 ошибка, неверный ID)
- Тестирования поведения клиента при специфичных данных
- Тестирования без зависимости от внешнего API
"""

from api.store_api import StoreAPI
from utils.validators import ResponseValidator


class TestStoreMock:
    """
    Тесты с мок-данными для эндпоинтов /store.

    Каждый тест использует фикстуру из conftest.py, которая настраивает мок
    перед выполнением теста. После теста мок автоматически удаляется.
    """

    def test_get_inventory_returns_mock_data(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        mock_inventory: dict,
    ):
        """
        GET /store/inventory — проверка с мок-данными.

        Мок возвращает кастомный инвентарь с полем "custom_field",
        которого нет в реальном API. Проверяем, что клиент корректно
        возвращает именно мок-ответ.
        """
        response = store_api.get_inventory()

        validator.validate_status_code(response, 200)
        validator.validate_is_json(response)
        # Поле "custom_field" есть только в мок-ответе — это гарантирует,
        # что мы проверяем именно мок, а не реальный API
        assert "custom_field" in response.json(), (
            "В ответе должно быть кастомное поле из мока"
        )

    def test_place_order_returns_201(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        mock_place_order: dict,
    ):
        """
        POST /store/order — мок возвращает статус 201 вместо реального 200.

        Симулируем нестандартное поведение сервера и проверяем,
        что клиент корректно передаёт этот статус-код.
        """
        # Тело запроса не важно — мок игнорирует его и всегда возвращает
        # заранее заданный ответ
        response = store_api.place_order(mock_place_order)

        validator.validate_status_code(response, 201)
        validator.validate_is_json(response)
        validator.validate_field(response, "id", mock_place_order["id"])
        validator.validate_field(response, "petId", mock_place_order["petId"])
        validator.validate_field(response, "quantity", mock_place_order["quantity"])

    def test_get_order_returns_wrong_id(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        mock_get_order_wrong_id: tuple,
    ):
        """
        Негативный мок-тест: запрашиваем заказ по ID=199, а в ответе ID=99.

        Симулирует ошибку сервера, когда он возвращает не тот ресурс.
        Проверяем, что ID в ответе НЕ совпадает с запрошенным.
        """
        requested_id, _ = mock_get_order_wrong_id
        response = store_api.get_order_by_id(requested_id)

        validator.validate_status_code(response, 400)
        validator.validate_is_json(response)
        # Убеждаемся, что ID в ответе не равен запрошенному
        validator.validate_field_not_equal(response, "id", requested_id)

    def test_delete_order_returns_error(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        mock_delete_order_error: tuple,
    ):
        """
        Негативный мок-тест: при удалении заказа сервер возвращает ошибку 400.

        Сообщение в ответе не совпадает с ID заказа —
        проверяем, что поле "message" не равно str(order_id).
        """
        order_id, _ = mock_delete_order_error
        response = store_api.delete_order(order_id)

        validator.validate_status_code(response, 400)
        validator.validate_is_json(response)
        validator.validate_field_not_equal(response, "message", str(order_id))

    def test_get_inventory_server_error(
        self,
        store_api: StoreAPI,
        validator: ResponseValidator,
        mock_server_error: None,
    ):
        """
        Тест обработки серверной ошибки 500 (Internal Server Error).

        Симулируем сбой сервера и проверяем, что клиент
        корректно получает и передаёт статус 500.
        """
        response = store_api.get_inventory()

        validator.validate_status_code(response, 500)
        validator.validate_is_json(response)
