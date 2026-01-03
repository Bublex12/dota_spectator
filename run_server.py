"""Скрипт для запуска Dota 2 GSI сервера."""
import sys
from pathlib import Path

# Добавляем папку src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from server import main

if __name__ == "__main__":
    main()

