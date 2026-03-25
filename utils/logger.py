"""
utils/logger.py — настройка логирования для всего проекта.

Логи пишутся в файл logs/test_run.log и выводятся в консоль (через pytest.ini).
"""

import logging
import os


def setup_logger(name: str = "api_tests") -> logging.Logger:
    """
    Создаёт и возвращает настроенный логгер.

    Если логгер с таким именем уже существует (и имеет обработчики),
    просто возвращает его — это предотвращает дублирование записей в лог.

    Args:
        name: имя логгера (по умолчанию "api_tests")

    Returns:
        Готовый к использованию объект Logger
    """
    logger = logging.getLogger(name)

    # Если обработчики уже добавлены — возвращаем существующий логгер
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Формат: время — уровень — сообщение
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # --- Запись в файл ---
    # Создаём папку logs/, если её нет
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "test_run.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
