"""Скрипт для получения аккаунтов игроков из последнего матча."""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_processor import DataProcessor
from utils import get_dotabuff_url, get_opendota_url

def get_latest_match_file():
    """Находит последний файл матча."""
    output_dir = Path(__file__).parent / "output"
    
    if not output_dir.exists():
        print("Папка output не найдена. Запустите матч в Dota 2.")
        return None
    
    # Ищем последний файл по датам
    date_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()], reverse=True)
    
    for date_dir in date_dirs:
        match_files = sorted(date_dir.glob("match_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if match_files:
            return match_files[0]
    
    return None

def main():
    """Основная функция."""
    match_file = get_latest_match_file()
    
    if not match_file:
        print("Файлы матчей не найдены.")
        return
    
    try:
        with open(match_file, 'r', encoding='utf-8') as f:
            match_data = json.load(f)
        
        # Извлекаем аккаунты из последнего состояния
        current_state = match_data.get("current_state", match_data.get("initial_state", {}))
        raw_data = current_state.get("raw_data", {})
        
        # Если нет raw_data, пробуем использовать сам current_state
        if not raw_data:
            raw_data = current_state
        
        processor = DataProcessor()
        players = processor.extract_players_accounts(raw_data)
        
        if players:
            print(f"\nАккаунты игроков из матча ({len(players)}):")
            print("=" * 80)
            for i, player in enumerate(players, 1):
                name = player.get('name', 'Unknown')
                steamid = player.get('steamid', 'N/A')
                team = player.get('team', 'N/A')
                print(f"{i}. {name}")
                print(f"   SteamID: {steamid}")
                print(f"   Команда: {team}")
                
                # Добавляем ссылки на Dotabuff и OpenDota
                if steamid and steamid != 'N/A':
                    dotabuff_url = get_dotabuff_url(steamid)
                    opendota_url = get_opendota_url(steamid)
                    
                    if dotabuff_url:
                        print(f"   Dotabuff: {dotabuff_url}")
                    if opendota_url:
                        print(f"   OpenDota: {opendota_url}")
                print()
        else:
            print("Игроки не найдены в данных матча.")
            print("\nПопробуйте:")
            print("1. Убедитесь, что матч активен")
            print("2. Проверьте, что сервер получает данные от Dota 2")
            print("3. Откройте файл матча напрямую для просмотра данных")
            
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

