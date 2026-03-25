# Логирование

Логи пишутся в `logs/test_run.log` (создаётся автоматически) и выводятся в консоль через `log_cli = true` в `pytest.ini`.

## Структура блока теста в логе

```
=================================================================
[POSITIVE] test_create_pet
Path: tests/pets/test_pets_positive.py::TestPetsPositive::test_create_pet
=================================================================
REQUEST:  POST https://petstore.swagger.io/v2/pet
STATUS:   200
RESPONSE: {'id': 1234, 'name': 'Rex', ...}
RESULT: PASSED
-----------------------------------------------------------------
```

## Где реализовано

- **`api/base_client.py` → `_log_request()`** — логирует каждый HTTP-запрос (метод, URL, статус, тело ответа, до 400 символов)
- **`tests/conftest.py` → `pytest_runtest_logstart()`** — пишет заголовок блока с типом теста `[POSITIVE/NEGATIVE/MOCK]` перед каждым тестом
- **`tests/conftest.py` → `pytest_runtest_logreport()`** — пишет `RESULT: PASSED/FAILED` после фазы `call`; при падении добавляет первые 600 символов ошибки
