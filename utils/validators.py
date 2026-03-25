"""
utils/validators.py — набор методов для проверки HTTP-ответов.

Все методы статические, поэтому не нужно хранить состояние.
Использование:
    validator = ResponseValidator()
    validator.validate_status_code(response, 200)
    validator.validate_field(response, "id", 42)
"""

import json
import requests


class ResponseValidator:
    """
    Класс-валидатор для проверки HTTP-ответов от API.

    Содержит методы для проверки:
    - статус-кода
    - формата JSON
    - значений полей в теле ответа
    - структуры вложенных объектов и списков
    """

    @staticmethod
    def validate_status_code(response: requests.Response, expected: int) -> None:
        """
        Проверяет, что статус-код ответа совпадает с ожидаемым.

        Args:
            response: объект HTTP-ответа
            expected: ожидаемый статус-код (например, 200, 404)
        """
        assert response.status_code == expected, (
            f"Ожидали статус {expected}, получили {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

    @staticmethod
    def validate_is_json(response: requests.Response) -> None:
        """
        Проверяет, что тело ответа является валидным JSON.

        Args:
            response: объект HTTP-ответа
        """
        try:
            response.json()
        except (json.JSONDecodeError, ValueError):
            assert False, f"Ответ не является JSON. Тело: {response.text}"

    @staticmethod
    def validate_field(response: requests.Response, field: str, expected_value) -> None:
        """
        Проверяет, что поле в JSON-ответе имеет ожидаемое значение.

        Args:
            response: объект HTTP-ответа
            field: имя поля в JSON (например, "id", "name")
            expected_value: ожидаемое значение поля
        """
        data = response.json()
        assert field in data, f"Поле '{field}' отсутствует в ответе: {data}"
        assert data[field] == expected_value, (
            f"Поле '{field}': ожидали '{expected_value}', получили '{data[field]}'"
        )

    @staticmethod
    def validate_field_not_equal(
        response: requests.Response, field: str, unexpected_value
    ) -> None:
        """
        Проверяет, что поле в JSON-ответе НЕ равно указанному значению.
        Используется в негативных тестах.

        Args:
            response: объект HTTP-ответа
            field: имя поля в JSON
            unexpected_value: значение, которого НЕ должно быть
        """
        data = response.json()
        assert field in data, f"Поле '{field}' отсутствует в ответе: {data}"
        assert data[field] != unexpected_value, (
            f"Поле '{field}' неожиданно равно '{unexpected_value}'"
        )

    @staticmethod
    def validate_dict_field(
        response: requests.Response, field: str, required_keys: list
    ) -> None:
        """
        Проверяет, что поле является словарём и содержит нужные ключи.

        Args:
            response: объект HTTP-ответа
            field: имя поля в JSON (должно быть словарём)
            required_keys: список ключей, которые обязаны присутствовать
        """
        data = response.json()
        assert field in data, f"Поле '{field}' отсутствует в ответе"
        assert isinstance(data[field], dict), (
            f"Поле '{field}' должно быть словарём, а не {type(data[field]).__name__}"
        )
        missing = [k for k in required_keys if k not in data[field]]
        assert not missing, f"В поле '{field}' отсутствуют ключи: {missing}"

    @staticmethod
    def validate_list_field(
        response: requests.Response, field: str, required_keys: list
    ) -> None:
        """
        Проверяет, что поле является списком словарей, каждый из которых
        содержит нужные ключи.

        Args:
            response: объект HTTP-ответа
            field: имя поля в JSON (должно быть списком)
            required_keys: список ключей, которые должны быть в каждом элементе
        """
        data = response.json()
        assert field in data, f"Поле '{field}' отсутствует в ответе"
        assert isinstance(data[field], list), f"Поле '{field}' должно быть списком"
        for i, item in enumerate(data[field]):
            missing = [k for k in required_keys if k not in item]
            assert not missing, (
                f"Элемент [{i}] в поле '{field}' не содержит ключи: {missing}"
            )

    @staticmethod
    def validate_list_items_status(
        response: requests.Response, field: str, expected_status: str
    ) -> None:
        """
        Проверяет, что у каждого объекта в списке поле `field` равно `expected_status`.
        Используется для проверки фильтрации по статусу.

        Args:
            response: объект HTTP-ответа (тело — список объектов)
            field: имя поля для проверки (например, "status")
            expected_status: ожидаемое значение поля
        """
        items = response.json()
        assert isinstance(items, list), "Ожидался список объектов в теле ответа"
        for i, item in enumerate(items):
            assert item.get(field) == expected_status, (
                f"Элемент [{i}]: ожидали {field}='{expected_status}', "
                f"получили '{item.get(field)}'"
            )
