# Команды запуска

```bash
# Все тесты
python -m pytest

# Тесты одного ресурса
python -m pytest tests/pets/
python -m pytest tests/store/
python -m pytest tests/users/

# Конкретный файл
python -m pytest tests/pets/test_pets_positive.py

# Один тест по имени
python -m pytest -k "test_create_pet"

# Установка зависимостей
pip install -r requirements.txt
```
