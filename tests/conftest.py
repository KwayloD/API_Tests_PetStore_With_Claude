"""
tests/conftest.py — центральный файл фикстур для всего проекта.

Pytest автоматически находит этот файл и делает все фикстуры доступными
для тестов в директории tests/ и всех её поддиректориях.

Фикстуры разбиты на группы:
1. API-клиенты       — объекты для отправки запросов
2. Payload-фикстуры  — генерация случайных тестовых данных
3. Setup/Teardown    — создают ресурс перед тестом и удаляют после
4. Mock-фикстуры     — подменяют реальные HTTP-запросы
"""

from datetime import datetime, timezone

import pytest
from faker import Faker

from api.base_client import BASE_URL
from api.pet_api import PetAPI
from api.store_api import StoreAPI
from api.user_api import UserAPI
from utils.validators import ResponseValidator

# Faker генерирует случайные тестовые данные (имена, email, числа и т.д.)
fake = Faker()


# =============================================================================
# API-КЛИЕНТЫ
# scope="session" означает, что объект создаётся один раз на всю тест-сессию
# =============================================================================

@pytest.fixture(scope="session")
def pet_api() -> PetAPI:
    """Клиент для работы с эндпоинтами /pet."""
    return PetAPI()


@pytest.fixture(scope="session")
def store_api() -> StoreAPI:
    """Клиент для работы с эндпоинтами /store."""
    return StoreAPI()


@pytest.fixture(scope="session")
def user_api() -> UserAPI:
    """Клиент для работы с эндпоинтами /user."""
    return UserAPI()


@pytest.fixture(scope="session")
def validator() -> ResponseValidator:
    """Валидатор для проверки HTTP-ответов. Один экземпляр на всю сессию."""
    return ResponseValidator()


# =============================================================================
# PAYLOAD-ФИКСТУРЫ (генераторы тестовых данных)
# scope="function" — новые данные генерируются для каждого теста
# =============================================================================

@pytest.fixture
def pet_payload() -> dict:
    """
    Генерирует случайные данные для создания питомца.

    Возвращает словарь, готовый к отправке в POST /pet.
    ID выбирается из диапазона 1000–9999, чтобы снизить вероятность
    конфликта с существующими данными в публичном Petstore.
    """
    return {
        "id": fake.random_int(min=1000, max=9999),
        "category": {
            "id": fake.random_int(min=1, max=100),
            "name": fake.word(),
        },
        "name": fake.first_name(),
        "photoUrls": [fake.image_url()],
        "tags": [
            {
                "id": fake.random_int(min=1, max=100),
                "name": fake.word(),
            }
        ],
        "status": fake.random_element(elements=["available", "pending", "sold"]),
    }


@pytest.fixture
def order_payload() -> dict:
    """
    Генерирует случайные данные для создания заказа.

    Возвращает словарь, готовый к отправке в POST /store/order.
    Petstore принимает orderId от 1 до 10 — используем этот диапазон.
    """
    return {
        "id": fake.random_int(min=1, max=10),
        "petId": fake.random_int(min=1000, max=9999),
        "quantity": fake.random_int(min=1, max=10),
        # Формат даты, который принимает Petstore API
        "shipDate": (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"
        ),
        "status": fake.random_element(elements=["placed", "approved", "delivered"]),
        "complete": fake.boolean(),
    }


@pytest.fixture
def user_payload() -> dict:
    """
    Генерирует случайные данные для создания пользователя.

    Возвращает словарь, готовый к отправке в POST /user.
    К username добавляется случайное число для уникальности.
    """
    return {
        "id": fake.random_int(min=1, max=9999),
        "username": fake.user_name() + str(fake.random_int(min=100, max=999)),
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "phone": fake.phone_number(),
        "userStatus": 0,
    }


# =============================================================================
# SETUP/TEARDOWN ФИКСТУРЫ
# Создают ресурс перед тестом и гарантируют удаление после.
# Используют yield — код до yield выполняется до теста, после — после.
# =============================================================================

@pytest.fixture
def created_pet(pet_api: PetAPI, pet_payload: dict) -> dict:
    """
    Создаёт питомца перед тестом и удаляет его после завершения.

    Возвращает данные созданного питомца (JSON из ответа API).
    Teardown гарантирует чистоту — питомец будет удалён даже если тест упал.

    Пример использования в тесте:
        def test_get_pet(self, pet_api, validator, created_pet):
            response = pet_api.get_pet_by_id(created_pet["id"])
    """
    # SETUP: создаём питомца
    response = pet_api.create_pet(pet_payload)
    assert response.status_code == 200, f"Не удалось создать питомца: {response.text}"
    pet_data = response.json()

    yield pet_data  # <-- здесь выполняется тест

    # TEARDOWN: удаляем питомца после теста
    try:
        pet_api.delete_pet(pet_data["id"])
    except Exception:
        pass  # питомец мог быть удалён самим тестом — это нормально


@pytest.fixture
def created_order(store_api: StoreAPI, order_payload: dict) -> dict:
    """
    Создаёт заказ перед тестом и удаляет его после завершения.

    Возвращает данные созданного заказа (JSON из ответа API).
    """
    # SETUP: создаём заказ
    response = store_api.place_order(order_payload)
    assert response.status_code == 200, f"Не удалось создать заказ: {response.text}"
    order_data = response.json()

    yield order_data  # <-- здесь выполняется тест

    # TEARDOWN: удаляем заказ
    try:
        store_api.delete_order(order_data["id"])
    except Exception:
        pass


@pytest.fixture
def created_user(user_api: UserAPI, user_payload: dict) -> dict:
    """
    Создаёт пользователя перед тестом и удаляет его после завершения.

    Возвращает payload пользователя (не ответ API, т.к. в ответе только id).
    Из payload можно достать username и другие нужные поля.
    """
    # SETUP: создаём пользователя
    response = user_api.create_user(user_payload)
    assert response.status_code == 200, f"Не удалось создать пользователя: {response.text}"

    yield user_payload  # <-- здесь выполняется тест

    # TEARDOWN: удаляем пользователя
    try:
        user_api.delete_user(user_payload["username"])
    except Exception:
        pass


# =============================================================================
# MOCK-ФИКСТУРЫ
# Используют библиотеку requests-mock для перехвата HTTP-запросов.
# Реальные запросы НЕ отправляются — ответ задаётся заранее.
# =============================================================================

@pytest.fixture
def mock_inventory(requests_mock) -> dict:
    """
    Мок для GET /store/inventory.

    Подменяет реальный ответ API кастомными данными.
    Добавляет поле "custom_field", которого нет в реальном API —
    это позволяет проверить, что клиент возвращает именно мок-ответ.
    """
    data = {
        "available": fake.random_int(min=10, max=100),
        "pending": fake.random_int(min=1, max=50),
        "sold": fake.random_int(min=1, max=50),
        "custom_field": "mock_value",  # уникальное поле для идентификации мок-ответа
    }
    requests_mock.get(f"{BASE_URL}/store/inventory", json=data, status_code=200)
    return data


@pytest.fixture
def mock_place_order(requests_mock) -> dict:
    """
    Мок для POST /store/order.

    Возвращает статус 201 (Created) вместо реального 200 —
    симулирует нестандартное поведение сервера.
    """
    data = {
        "id": 999,
        "petId": 888,
        "quantity": 5,
        "shipDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000",
        "status": "placed",
        "complete": False,
    }
    requests_mock.post(f"{BASE_URL}/store/order", json=data, status_code=201)
    return data


@pytest.fixture
def mock_get_order_wrong_id(requests_mock) -> tuple:
    """
    Мок для GET /store/order/{orderId}.

    Симулирует ситуацию: запрашиваем заказ с ID=199,
    но сервер возвращает ответ с ID=99 (другой заказ) и статус 400.

    Returns:
        Кортеж (запрошенный_id, данные_ответа)
    """
    requested_id = 199
    response_data = {
        "id": 99,  # намеренно другой ID — это тестируемое поведение
        "petId": 555,
        "quantity": 3,
        "status": "placed",
        "complete": True,
    }
    requests_mock.get(
        f"{BASE_URL}/store/order/{requested_id}",
        json=response_data,
        status_code=400,
    )
    return requested_id, response_data


@pytest.fixture
def mock_delete_order_error(requests_mock) -> tuple:
    """
    Мок для DELETE /store/order/{orderId}.

    Симулирует ошибку при удалении: сервер возвращает 400
    и сообщение, не совпадающее с переданным ID заказа.

    Returns:
        Кортеж (id_заказа, данные_ответа)
    """
    order_id = 99
    response_data = {
        "code": 400,
        "type": "error",
        "message": "order not found",  # не равно str(order_id) — это тестируемое поведение
    }
    requests_mock.delete(
        f"{BASE_URL}/store/order/{order_id}",
        json=response_data,
        status_code=400,
    )
    return order_id, response_data


@pytest.fixture
def mock_server_error(requests_mock) -> None:
    """
    Мок для симуляции ошибки 500 (Internal Server Error).

    Подменяет ответ GET /store/inventory на серверную ошибку.
    Используется для проверки, что клиент корректно обрабатывает 5xx ответы.
    """
    requests_mock.get(
        f"{BASE_URL}/store/inventory",
        json={"message": "Internal Server Error"},
        status_code=500,
    )


# =============================================================================
# PYTEST HOOKS — расширенное логирование хода тестов
# Хуки автоматически вызываются pytest-ом до и после каждого теста.
# =============================================================================

def _get_test_type(nodeid: str) -> str:
    """
    Определяет тип теста по имени файла.

    Пример: "tests/pets/test_pets_positive.py::..." → "POSITIVE"
    """
    if "_positive" in nodeid:
        return "POSITIVE"
    elif "_negative" in nodeid:
        return "NEGATIVE"
    elif "_mock" in nodeid:
        return "MOCK"
    return "UNKNOWN"


def pytest_runtest_logstart(nodeid: str, location: tuple) -> None:
    """
    Хук pytest: вызывается перед запуском каждого теста.

    Записывает в лог визуальный разделитель, тип и полное имя теста.
    nodeid пример: "tests/pets/test_pets_positive.py::TestPetsPositive::test_create_pet"
    """
    from utils.logger import setup_logger

    logger = setup_logger()
    test_type = _get_test_type(nodeid)
    # Берём только имя функции (часть после последнего ::)
    test_name = nodeid.split("::")[-1]

    logger.info("")
    logger.info("=" * 65)
    logger.info(f"[{test_type}] {test_name}")
    logger.info(f"Path: {nodeid}")
    logger.info("=" * 65)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """
    Хук pytest: вызывается после каждой фазы теста (setup / call / teardown).

    Логируем итог только для фазы "call" — это и есть выполнение самого теста.
    Фазы "setup" и "teardown" — подготовка и очистка фикстур, их не логируем.
    """
    if report.when != "call":
        return

    from utils.logger import setup_logger

    logger = setup_logger()

    if report.passed:
        logger.info("RESULT: PASSED")
    elif report.failed:
        logger.info("RESULT: FAILED")
        # Выводим сокращённое описание ошибки (первые 600 символов)
        error_text = str(report.longrepr)[:600]
        logger.info(f"ERROR:  {error_text}")
    elif report.skipped:
        logger.info("RESULT: SKIPPED")

    logger.info("-" * 65)
    logger.info("")
