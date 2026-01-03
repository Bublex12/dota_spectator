FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml requirements.txt ./

# Установка зависимостей через uv
RUN uv pip install --system -r requirements.txt

# Копируем исходный код
COPY src/ ./src/
COPY *.py ./
COPY gsi_config/ ./gsi_config/

# Создаем папку для выходных данных
RUN mkdir -p output

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# По умолчанию запускаем GSI сервер
# Railway будет использовать startCommand из railway.json
CMD ["python", "src/server.py"]

