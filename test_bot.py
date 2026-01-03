"""Скрипт для тестирования Discord бота локально."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_processor import DataProcessor
from utils import get_dotabuff_url

def test_bot_functionality():
    """Тестирует функциональность бота без запуска Discord."""
    print("=" * 60)
    print("Тестирование функциональности Discord бота")
    print("=" * 60)
    print()
    
    # Проверяем наличие файлов матчей
    output_dir = Path(__file__).parent / "output"
    if not output_dir.exists():
        print("❌ Папка output не найдена")
        return False
    
    # Ищем последний файл матча
    date_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()], reverse=True)
    match_file = None
    
    for date_dir in date_dirs:
        match_files = sorted(date_dir.glob("match_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if match_files:
            match_file = match_files[0]
            break
    
    if not match_file:
        print("❌ Файлы матчей не найдены")
        print("   Запустите GSI сервер и сыграйте матч в Dota 2")
        return False
    
    print(f"✅ Найден файл матча: {match_file.name}")
    print()
    
    # Загружаем данные
    try:
        with open(match_file, 'r', encoding='utf-8') as f:
            match_data = json.load(f)
        
        # Извлекаем игроков
        current_state = match_data.get("current_state", match_data.get("initial_state", {}))
        raw_data = current_state.get("raw_data", {})
        
        if not raw_data:
            raw_data = current_state
        
        processor = DataProcessor()
        players = processor.extract_players_accounts(raw_data)
        
        if not players:
            print("❌ Игроки не найдены в данных матча")
            return False
        
        print(f"✅ Найдено игроков: {len(players)}")
        print()
        print("Формат вывода бота (как будет в Discord):")
        print("-" * 60)
        
        # Формируем сообщение как в боте
        lines = []
        for player in players:
            name = player.get('name', 'Unknown')
            dotabuff_url = get_dotabuff_url(str(player.get('steamid', '')))
            
            if dotabuff_url:
                line = f"{name} - {dotabuff_url}"
                lines.append(line)
                print(line)
            else:
                steamid = player.get('steamid', 'N/A')
                line = f"{name} - (SteamID: {steamid})"
                lines.append(line)
                print(line)
        
        print("-" * 60)
        print()
        print("✅ Тест пройден! Бот должен работать корректно.")
        print()
        print("Для запуска бота:")
        print("1. Убедитесь, что установлен DISCORD_TOKEN в .env")
        print("2. Запустите: python discord_bot.py")
        print("3. В Discord используйте команду: !match")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bot_functionality()

