"""Конфигурация приложения для Dota 2 GSI интеграции."""
import os
from pathlib import Path

# Базовый путь проекта
BASE_DIR = Path(__file__).parent.parent

# Настройки сервера
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 3000

# Пути к директориям
OUTPUT_DIR = BASE_DIR / "output"
GSI_CONFIG_DIR = BASE_DIR / "gsi_config"

# Создание директорий при необходимости
OUTPUT_DIR.mkdir(exist_ok=True)
GSI_CONFIG_DIR.mkdir(exist_ok=True)

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Настройки сохранения файлов
SAVE_INTERVAL_SECONDS = 5  # Интервал сохранения данных (в секундах)
MAX_FILE_SIZE_MB = 10  # Максимальный размер файла в МБ

