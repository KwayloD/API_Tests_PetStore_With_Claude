"""
api/base_client.py — базовый HTTP-клиент.

Все специализированные клиенты (PetAPI, StoreAPI, UserAPI) наследуются от BaseClient.
Здесь реализована общая логика: отправка запросов, заголовки, логирование.
"""

import os

import requests
from dotenv import load_dotenv

from utils.logger import setup_logger

# Загружаем переменные из файла .env
load_dotenv()

# Базовый URL API. Берётся из .env, по умолчанию — публичный Petstore
BASE_URL = os.getenv("BASE_URL", "https://petstore.swagger.io/v2")


class BaseClient:
    """
    Базовый HTTP-клиент для взаимодействия с REST API.

    Инкапсулирует:
    - общие заголовки запросов
    - методы GET, POST, PUT, DELETE
    - логирование каждого запроса и ответа

    Все специализированные API-клиенты наследуются от этого класса
    и добавляют методы, специфичные для своего ресурса.
    """

    # Заголовки, которые отправляются с каждым запросом
    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "api_key": "special-key",
    }

    def __init__(self):
        self.base_url = BASE_URL
        # Session переиспользует TCP-соединение — это эффективнее, чем
        # создавать новое соединение для каждого запроса
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.logger = setup_logger()

    def _log_request(self, method: str, url: str, response: requests.Response) -> None:
        """Логирует метод, URL, статус-код и тело ответа."""
        self.logger.info(f"REQUEST:  {method} {url}")
        self.logger.info(f"STATUS:   {response.status_code}")
        try:
            # Пробуем распарсить как JSON для читаемого вывода
            body = str(response.json())
            if len(body) > 400:
                body = body[:400] + " ..."
        except Exception:
            body = response.text[:400] if response.text else "(empty)"
        self.logger.info(f"RESPONSE: {body}")

    def get(self, endpoint: str, params: dict = None) -> requests.Response:
        """
        Выполняет GET-запрос.

        Args:
            endpoint: путь эндпоинта, например "/pet/findByStatus"
            params: query-параметры, например {"status": "available"}
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        self._log_request("GET", url, response)
        return response

    def post(
        self, endpoint: str, json: dict = None, data: dict = None
    ) -> requests.Response:
        """
        Выполняет POST-запрос.

        Args:
            endpoint: путь эндпоинта
            json: тело запроса в формате JSON (словарь)
            data: тело запроса в формате form-data (словарь)
        """
        url = f"{self.base_url}{endpoint}"
        if data is not None:
            # Когда отправляем form-data, нужно убрать дефолтный Content-Type: application/json,
            # чтобы requests автоматически выставил application/x-www-form-urlencoded
            response = self.session.post(url, data=data, headers={"Content-Type": None})
        else:
            response = self.session.post(url, json=json)
        self._log_request("POST", url, response)
        return response

    def put(self, endpoint: str, json: dict = None) -> requests.Response:
        """
        Выполняет PUT-запрос.

        Args:
            endpoint: путь эндпоинта
            json: тело запроса в формате JSON
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=json)
        self._log_request("PUT", url, response)
        return response

    def delete(self, endpoint: str) -> requests.Response:
        """
        Выполняет DELETE-запрос.

        Args:
            endpoint: путь эндпоинта, например "/pet/42"
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        self._log_request("DELETE", url, response)
        return response
