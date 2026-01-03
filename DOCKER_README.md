# Docker Deployment Guide

Инструкция по развертыванию проекта с помощью Docker Compose.

## Требования

- Docker
- Docker Compose

## Быстрый старт

1. **Создайте файл `.env` в корне проекта:**
   ```env
   DISCORD_TOKEN=ваш_токен_discord_бота
   ```

2. **Соберите и запустите контейнеры:**
   ```bash
   docker-compose up -d
   ```

3. **Проверьте статус:**
   ```bash
   docker-compose ps
   ```

4. **Просмотрите логи:**
   ```bash
   # Логи GSI сервера
   docker-compose logs -f gsi-server
   
   # Логи Discord бота
   docker-compose logs -f discord-bot
   ```

## Остановка

```bash
docker-compose down
```

## Пересборка после изменений

```bash
docker-compose build --no-cache
docker-compose up -d
```

## Структура сервисов

### GSI Server
- **Порт:** 3000
- **Назначение:** Прием данных от Dota 2 Game State Integration
- **Volumes:** 
  - `./output` - папка для сохранения данных матчей
  - `./gsi_config` - конфигурация GSI

### Discord Bot
- **Назначение:** Discord бот с командой `!match`
- **Volumes:**
  - `./output` - чтение данных матчей
  - `./.env` - токен бота (read-only)

## Настройка

### Изменение порта GSI сервера

Отредактируйте `docker-compose.yml`:
```yaml
ports:
  - "3000:3000"  # измените на нужный порт
```

### Переменные окружения

Можно добавить в `docker-compose.yml`:
```yaml
environment:
  - SERVER_HOST=0.0.0.0
  - SERVER_PORT=3000
  - LOG_LEVEL=INFO
```

## Проверка работы

1. **GSI сервер:**
   ```bash
   curl http://localhost:3000/
   ```

2. **Discord бот:**
   - Зайдите в Discord
   - Используйте команду `!match` в канале, где находится бот

## Устранение неполадок

### Бот не запускается

Проверьте токен в `.env`:
```bash
docker-compose logs discord-bot
```

### GSI сервер не получает данные

1. Убедитесь, что порт 3000 открыт
2. Проверьте конфигурацию GSI в Dota 2
3. Проверьте логи:
   ```bash
   docker-compose logs gsi-server
   ```

### Файлы не сохраняются

Проверьте права доступа к папке `output`:
```bash
chmod -R 777 output
```

## Обновление

```bash
# Остановить контейнеры
docker-compose down

# Обновить код (git pull)

# Пересобрать и запустить
docker-compose build
docker-compose up -d
```

## Полезные команды

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Перезапуск конкретного сервиса
docker-compose restart discord-bot

# Выполнение команды в контейнере
docker-compose exec gsi-server python get_players.py

# Очистка (удаление контейнеров и volumes)
docker-compose down -v
```

