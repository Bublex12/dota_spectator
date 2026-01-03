"""HTTP сервер для приема данных от Dota 2 Game State Integration."""
import logging
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from config import SERVER_HOST, SERVER_PORT, LOG_LEVEL, LOG_FORMAT
from data_processor import DataProcessor
from file_manager import FileManager
from utils import get_dotabuff_url, get_opendota_url

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = FastAPI(title="Dota 2 GSI Server", version="1.0.0")

# Инициализация компонентов
data_processor = DataProcessor()
file_manager = FileManager()

# Состояние сервера
match_in_progress = False
current_match_id = None


@app.get("/")
async def root():
    """Корневой endpoint для проверки работы сервера."""
    return {
        "status": "running",
        "service": "Dota 2 GSI Server",
        "match_in_progress": match_in_progress,
        "current_match_id": current_match_id
    }


@app.post("/")
async def receive_gsi_data(request: Request):
    """
    Основной endpoint для приема данных от Dota 2 GSI.
    
    Dota 2 отправляет POST запросы с JSON данными о текущем состоянии игры.
    """
    global match_in_progress
    
    try:
        # Получаем данные из запроса
        raw_data: Dict[str, Any] = await request.json()
        
        if not raw_data:
            logger.warning("Получен пустой запрос")
            return JSONResponse(
                status_code=200,
                content={"status": "ok", "message": "Empty data received"}
            )
        
        # Логируем получение данных
        logger.debug(f"Получены данные GSI: {raw_data.get('map', {}).get('game_state', 'Unknown')}")
        
        # Обрабатываем данные
        processed_data = data_processor.process_gsi_data(raw_data)
        
        # Получаем ID текущего матча
        map_data = raw_data.get("map", {})
        incoming_match_id = map_data.get("matchid")
        if incoming_match_id:
            incoming_match_id = str(incoming_match_id)
        
        # Проверяем состояние матча
        is_started = data_processor.is_match_started(raw_data)
        is_ended = data_processor.is_match_ended(raw_data)
        
        global current_match_id
        
        # Определяем, это новый матч или продолжение текущего
        if incoming_match_id:
            incoming_match_id = str(incoming_match_id)
            # Если match_id изменился, это новый матч
            if incoming_match_id != current_match_id:
                # Завершаем предыдущий матч, если он был
                if match_in_progress and file_manager.current_file_path:
                    file_manager.finalize_match(processed_data)
                # Начинаем новый матч
                current_match_id = incoming_match_id
                match_in_progress = True
                file_manager.start_new_match(processed_data)
                logger.info(f"Матч начался (ID: {current_match_id})")
                
                # Выводим аккаунты игроков
                players = data_processor.extract_players_accounts(raw_data)
                if players:
                    logger.info(f"Игроки в матче ({len(players)}):")
                    for player in players:
                        logger.info(f"  - {player.get('name', 'Unknown')} (SteamID: {player.get('steamid')}, Team: {player.get('team')})")
            else:
                # Продолжение текущего матча - сохраняем данные
                if not file_manager.current_file_path:
                    # Файл не создан, создаем
                    file_manager.start_new_match(processed_data)
                else:
                    # Обновляем существующий файл
                    file_manager.save_match_data(processed_data)
        elif is_started and not is_ended:
            # Матч идет, но match_id нет (может быть демо или локальная игра)
            if not match_in_progress or not file_manager.current_file_path:
                # Создаем новый файл
                match_in_progress = True
                file_manager.start_new_match(processed_data)
                logger.info("Матч начался (без ID)")
                
                # Выводим аккаунты игроков
                players = data_processor.extract_players_accounts(raw_data)
                if players:
                    logger.info(f"Игроки в матче ({len(players)}):")
                    for player in players:
                        logger.info(f"  - {player.get('name', 'Unknown')} (SteamID: {player.get('steamid')}, Team: {player.get('team')})")
            else:
                # Обновляем существующий файл
                file_manager.save_match_data(processed_data)
        
        # Если матч завершен
        if is_ended and match_in_progress:
            if file_manager.current_file_path:
                file_manager.finalize_match(processed_data)
            match_in_progress = False
            current_match_id = None
            file_manager.current_file_path = None
            logger.info("Матч завершен")
        
        # Возвращаем успешный ответ
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "processed": True}
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке данных GSI: {e}", exc_info=True)
        # Все равно возвращаем 200, чтобы Dota 2 не повторяла запросы
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "match_in_progress": match_in_progress
    }


@app.get("/players")
async def get_players():
    """
    Endpoint для получения аккаунтов игроков из последних полученных данных.
    """
    # Получаем последний файл матча, если он существует
    if file_manager.current_file_path and file_manager.current_file_path.exists():
        try:
            import json
            with open(file_manager.current_file_path, 'r', encoding='utf-8') as f:
                match_data = json.load(f)
            
            # Извлекаем аккаунты из последнего состояния
            current_state = match_data.get("current_state", match_data.get("initial_state", {}))
            raw_data = current_state.get("raw_data", {})
            
            players = data_processor.extract_players_accounts(raw_data)
            
            # Добавляем ссылки на Dotabuff и OpenDota для каждого игрока
            players_with_links = []
            for player in players:
                player_dict = player.copy()
                steamid = player.get("steamid")
                if steamid:
                    player_dict["dotabuff_url"] = get_dotabuff_url(str(steamid))
                    player_dict["opendota_url"] = get_opendota_url(str(steamid))
                players_with_links.append(player_dict)
            
            return {
                "status": "ok",
                "players": players_with_links,
                "count": len(players_with_links)
            }
        except Exception as e:
            logger.error(f"Ошибка при получении данных игроков: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    else:
        return {
            "status": "no_match",
            "message": "Нет активного матча"
        }


def main():
    """Запуск сервера."""
    logger.info(f"Запуск Dota 2 GSI сервера на {SERVER_HOST}:{SERVER_PORT}")
    logger.info("Ожидание данных от Dota 2...")
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level=LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()

