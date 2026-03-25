# Архитектура проекта

## Иерархия API-клиентов

```
BaseClient  (api/base_client.py)
    ├── PetAPI    (api/pet_api.py)
    ├── StoreAPI  (api/store_api.py)
    └── UserAPI   (api/user_api.py)
```

`BaseClient` хранит `requests.Session`, дефолтные заголовки, логгер и методы GET/POST/PUT/DELETE.
Дочерние клиенты добавляют только методы конкретных эндпоинтов.

`BASE_URL` загружается из `.env` и экспортируется из `api/base_client.py` — импортировать именно оттуда (например, в mock-фикстурах для построения URL).

## Особенность POST с form-data

Когда `BaseClient.post()` вызывается с `data=` (form-data), он передаёт `headers={"Content-Type": None}`, чтобы убрать сессионный `application/json`. Без этого сервер возвращает 415.

## Структура тестов

```
tests/
├── conftest.py          # единственный источник всех фикстур
├── pets/
│   ├── test_pets_positive.py
│   └── test_pets_negative.py
├── store/
│   ├── test_store_positive.py
│   ├── test_store_negative.py
│   └── test_store_mock.py
└── users/
    ├── test_users_positive.py
    └── test_users_negative.py
```
