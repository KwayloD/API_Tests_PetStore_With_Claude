# Паттерн фикстур

Все фикстуры — в `tests/conftest.py`. Разбиты на 4 группы:

## 1. Синглтоны сессии (`scope="session"`)
Создаются один раз на весь прогон:
```
pet_api, store_api, user_api, validator
```

## 2. Генераторы тестовых данных (`scope="function"`)
Генерируют случайные данные через `Faker` для каждого теста:
```
pet_payload, order_payload, user_payload
```

## 3. Setup/Teardown фикстуры
Создают ресурс через API, передают данные в тест через `yield`, удаляют после:
```
created_pet, created_order, created_user
```
Удаление в teardown **всегда** оборачивать в `try/except` — тест мог уже удалить ресурс сам.

```python
@pytest.fixture
def created_pet(pet_api, pet_payload):
    response = pet_api.create_pet(pet_payload)
    yield response.json()        # ← тест получает данные
    try:
        pet_api.delete_pet(...)  # ← cleanup после теста
    except Exception:
        pass
```

## 4. Mock-фикстуры
Используют `requests_mock` для перехвата HTTP без обращения к реальному API.
URL строится через `BASE_URL`, импортированный из `api.base_client`:
```
mock_inventory, mock_place_order, mock_get_order_wrong_id,
mock_delete_order_error, mock_server_error
```
