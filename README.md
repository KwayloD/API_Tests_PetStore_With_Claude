# API Tests — PetStore

Автоматизированные API-тесты для публичного [Swagger Petstore](https://petstore.swagger.io/v2).
Проект написан на Python с использованием `pytest` и `requests`.

---

## Содержание

- [Стек технологий](#стек-технологий)
- [Структура проекта](#структура-проекта)
- [Архитектура](#архитектура)
- [Запуск тестов](#запуск-тестов)
- [Логирование](#логирование)
- [Тестируемые эндпоинты](#тестируемые-эндпоинты)
- [Типы тестов](#типы-тестов)
- [Как добавить новый тест](#как-добавить-новый-тест)

---

## Стек технологий

| Библиотека       | Версия  | Назначение                                              |
|------------------|---------|---------------------------------------------------------|
| `pytest`         | latest  | Фреймворк для запуска тестов                            |
| `requests`       | latest  | HTTP-клиент для отправки запросов к API                 |
| `requests-mock`  | latest  | Перехват HTTP-запросов для мок-тестов                   |
| `faker`          | latest  | Генерация случайных тестовых данных (имена, email и т.д.) |
| `python-dotenv`  | latest  | Загрузка переменных окружения из файла `.env`           |

Установка зависимостей:
```bash
pip install -r requirements.txt
```

---

## Структура проекта

```
API_Tests_PetStore_With_Claude/
│
├── api/                          # HTTP-клиенты для работы с API
│   ├── base_client.py            # Базовый класс: методы GET/POST/PUT/DELETE + логирование
│   ├── pet_api.py                # Клиент для /pet (питомцы)
│   ├── store_api.py              # Клиент для /store (магазин и заказы)
│   └── user_api.py               # Клиент для /user (пользователи)
│
├── tests/                        # Все тесты
│   ├── conftest.py               # Фикстуры: API-клиенты, генераторы данных, моки, хуки
│   │
│   ├── pets/                     # Тесты для /pet
│   │   ├── test_pets_positive.py # Позитивные: создание, чтение, обновление, удаление
│   │   └── test_pets_negative.py # Негативные: несуществующий ID, невалидный ID
│   │
│   ├── store/                    # Тесты для /store
│   │   ├── test_store_positive.py  # Позитивные: инвентарь, заказы
│   │   ├── test_store_negative.py  # Негативные: несуществующий/невалидный заказ
│   │   └── test_store_mock.py      # Мок-тесты: кастомные ответы, 500 ошибка
│   │
│   └── users/                    # Тесты для /user
│       ├── test_users_positive.py  # Позитивные: CRUD + логин
│       └── test_users_negative.py  # Негативные: несуществующий пользователь
│
├── utils/                        # Вспомогательные модули
│   ├── logger.py                 # Настройка логирования (файл + консоль)
│   └── validators.py             # Класс ResponseValidator — проверка HTTP-ответов
│
├── logs/
│   └── test_run.log              # Лог-файл (создаётся автоматически при запуске)
│
├── .env                          # Переменные окружения (BASE_URL)
├── .gitignore
├── pytest.ini                    # Настройки pytest
├── requirements.txt
└── README.md
```

---

## Архитектура

### Слой API-клиентов (`api/`)

Все клиенты построены на наследовании:

```
BaseClient          ← общая логика: сессия, заголовки, HTTP-методы, логирование
    ├── PetAPI      ← методы: create_pet, get_pet_by_id, update_pet, delete_pet, ...
    ├── StoreAPI    ← методы: get_inventory, place_order, get_order_by_id, ...
    └── UserAPI     ← методы: create_user, get_user, update_user, delete_user, login, ...
```

`BaseClient` использует `requests.Session` — это позволяет переиспользовать TCP-соединение
и хранить общие заголовки (`Accept`, `Content-Type`, `api_key`).

> **Важно:** при отправке form-data (`data=`) в POST-запросе нужно передать
> `headers={"Content-Type": None}`, чтобы убрать дефолтный `application/json`
> и позволить `requests` автоматически выставить `application/x-www-form-urlencoded`.

### Слой валидации (`utils/validators.py`)

`ResponseValidator` — класс со статическими методами для проверки ответов:

| Метод                        | Что проверяет                                             |
|------------------------------|-----------------------------------------------------------|
| `validate_status_code`       | Статус-код совпадает с ожидаемым                          |
| `validate_is_json`           | Тело ответа — валидный JSON                               |
| `validate_field`             | Поле в JSON равно ожидаемому значению                     |
| `validate_field_not_equal`   | Поле в JSON НЕ равно значению (для негативных тестов)     |
| `validate_dict_field`        | Поле является словарём с нужными ключами                  |
| `validate_list_field`        | Поле является списком словарей с нужными ключами          |
| `validate_list_items_status` | Все элементы списка имеют нужное значение поля            |

### Фикстуры (`tests/conftest.py`)

Фикстуры разбиты на 4 группы:

**1. API-клиенты** (`scope="session"` — создаются один раз на всю сессию):
```python
pet_api, store_api, user_api, validator
```

**2. Payload-фикстуры** (`scope="function"` — новые данные для каждого теста):
```python
pet_payload, order_payload, user_payload
```

**3. Setup/Teardown** — создают ресурс через API перед тестом и удаляют после:
```python
created_pet, created_order, created_user
```
Используют `yield` — код до `yield` выполняется до теста, после — в teardown:
```python
@pytest.fixture
def created_pet(pet_api, pet_payload):
    response = pet_api.create_pet(pet_payload)
    yield response.json()        # ← тест получает данные созданного питомца
    pet_api.delete_pet(...)      # ← удаляется после теста (даже если тест упал)
```

**4. Mock-фикстуры** — перехватывают HTTP-запросы, не обращаясь к реальному API:
```python
mock_inventory, mock_place_order, mock_get_order_wrong_id,
mock_delete_order_error, mock_server_error
```

---

## Запуск тестов

```bash
# Все тесты
python -m pytest

# Конкретный модуль
python -m pytest tests/pets/

# Только позитивные
python -m pytest tests/pets/test_pets_positive.py

# Только моки
python -m pytest tests/store/test_store_mock.py

# С подробным выводом (уже задано в pytest.ini)
python -m pytest -v

# Остановить после первого падения
python -m pytest -x

# Запустить тест по имени
python -m pytest -k "test_create_pet"
```

### Настройки pytest.ini

```ini
pythonpath = .        # позволяет импортировать from api.pet_api import PetAPI
testpaths = tests     # ищет тесты только в папке tests/
addopts = -v --tb=short
log_cli = true        # живой вывод логов в консоль во время выполнения
log_cli_level = INFO
```

---

## Логирование

Логи записываются в `logs/test_run.log` и выводятся в консоль во время выполнения.

Формат одного теста в логе:

```
=================================================================
[POSITIVE] test_get_user_by_username
Path: tests/users/test_users_positive.py::TestUsersPositive::test_get_user_by_username
=================================================================
REQUEST:  POST https://petstore.swagger.io/v2/user
STATUS:   200
RESPONSE: {'code': 200, 'type': 'unknown', 'message': '3610'}
RESULT: PASSED
-----------------------------------------------------------------
```

Логирование реализовано на двух уровнях:
- **`base_client.py`** — логирует каждый HTTP-запрос (метод, URL, статус, тело ответа)
- **`conftest.py` (pytest-хуки)** — логирует начало/конец каждого теста и итоговый результат

---

## Тестируемые эндпоинты

| Ресурс  | Метод  | Эндпоинт                    | Описание                          |
|---------|--------|-----------------------------|-----------------------------------|
| Pet     | POST   | `/pet`                      | Создать питомца                   |
| Pet     | GET    | `/pet/findByStatus`         | Найти питомцев по статусу         |
| Pet     | GET    | `/pet/{petId}`              | Получить питомца по ID            |
| Pet     | PUT    | `/pet`                      | Обновить питомца (JSON)           |
| Pet     | POST   | `/pet/{petId}`              | Обновить питомца (form-data)      |
| Pet     | DELETE | `/pet/{petId}`              | Удалить питомца                   |
| Store   | GET    | `/store/inventory`          | Получить инвентарь                |
| Store   | POST   | `/store/order`              | Создать заказ                     |
| Store   | GET    | `/store/order/{orderId}`    | Получить заказ по ID              |
| Store   | DELETE | `/store/order/{orderId}`    | Удалить заказ                     |
| User    | POST   | `/user`                     | Создать пользователя              |
| User    | GET    | `/user/{username}`          | Получить пользователя             |
| User    | PUT    | `/user/{username}`          | Обновить пользователя             |
| User    | DELETE | `/user/{username}`          | Удалить пользователя              |
| User    | GET    | `/user/login`               | Войти в систему                   |

---

## Типы тестов

### Позитивные (`test_*_positive.py`)
Проверяют успешные сценарии при валидных входных данных.
Используют фикстуры `created_*` для изоляции: каждый тест создаёт
свои данные и удаляет их после завершения.

### Негативные (`test_*_negative.py`)
Проверяют обработку ошибок при невалидных данных.
Примеры сценариев:
- Запрос несуществующего ресурса → `404`
- Передача строки вместо числового ID → `404` (Petstore возвращает 404, а не 400)
- Попытка получить удалённого пользователя → `404`

> **Quirk публичного Petstore:** API крайне лоялен к входным данным.
> Например, `PUT /user/{несуществующий}` делает upsert вместо 404,
> а `GET /user/login` с пустыми данными возвращает 200.

### Мок-тесты (`test_*_mock.py`)
Используют `requests-mock` для перехвата запросов без обращения к реальному API.
Позволяют тестировать:
- Нестандартные статус-коды (например, 201 вместо 200)
- Ситуации, которые сложно воспроизвести на реальном API (500 ошибка)
- Поведение клиента при несоответствии данных в ответе

---

## Как добавить новый тест

### 1. Добавить метод в API-клиент (если нужен новый эндпоинт)

```python
# api/pet_api.py
def find_pets_by_tags(self, tags: list) -> requests.Response:
    """GET /pet/findByTags"""
    return self.get("/pet/findByTags", params={"tags": tags})
```

### 2. Добавить фикстуру в conftest.py (если нужны новые тестовые данные)

```python
# tests/conftest.py
@pytest.fixture
def my_payload() -> dict:
    return {"field": fake.word()}
```

### 3. Написать тест в нужном файле

```python
# tests/pets/test_pets_positive.py
def test_find_pets_by_tags(self, pet_api, validator):
    response = pet_api.find_pets_by_tags(["tag1", "tag2"])
    validator.validate_status_code(response, 200)
    validator.validate_is_json(response)
```

### Правила именования

| Что                | Соглашение                          | Пример                        |
|--------------------|-------------------------------------|-------------------------------|
| Файл теста         | `test_{ресурс}_{тип}.py`           | `test_pets_positive.py`       |
| Класс тестов       | `Test{Ресурс}{Тип}`                | `TestPetsPositive`            |
| Метод теста        | `test_{действие}_{условие}`        | `test_get_pet_not_found`      |
| Фикстура payload   | `{ресурс}_payload`                 | `pet_payload`                 |
| Фикстура с данными | `created_{ресурс}`                 | `created_pet`                 |
| Мок-фикстура       | `mock_{описание}`                  | `mock_inventory`              |
