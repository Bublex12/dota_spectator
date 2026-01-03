"""Discord бот для получения информации о матчах Dota 2."""
import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_processor import DataProcessor
from utils import get_dotabuff_url

# Настройки бота
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
COMMAND_PREFIX = "!"


def get_latest_match_file() -> Optional[Path]:
    """Находит последний файл матча."""
    output_dir = Path(__file__).parent / "output"
    
    if not output_dir.exists():
        return None
    
    # Ищем последний файл по датам
    date_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()], reverse=True)
    
    for date_dir in date_dirs:
        match_files = sorted(date_dir.glob("match_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if match_files:
            return match_files[0]
    
    return None


def get_players_from_match(match_file: Path) -> List[Dict[str, Any]]:
    """Извлекает игроков из файла матча."""
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
        # Получаем match_id для запроса к OpenDota
        match_id = match_data.get("match_id")
        players = processor.extract_players_accounts(raw_data, match_id)
        
        # Добавляем ссылки на Dotabuff
        players_with_links = []
        for player in players:
            player_dict = player.copy()
            steamid = player.get("steamid")
            if steamid:
                dotabuff_url = get_dotabuff_url(str(steamid))
                player_dict["dotabuff_url"] = dotabuff_url
            players_with_links.append(player_dict)
        
        return players_with_links
    except Exception as e:
        print(f"Ошибка при чтении файла матча: {e}")
        return []


# Создаем бота
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    """Вызывается при готовности бота."""
    print(f'{bot.user} подключился к Discord!')
    print(f'Бот работает на {len(bot.guilds)} серверах')


@bot.command(name='match')
async def match_command(ctx):
    """
    Команда !match - выводит список игроков текущего матча с ссылками на Dotabuff.
    Формат: Ник - Dotabuff ссылка
    """
    # Получаем последний файл матча
    match_file = get_latest_match_file()
    
    if not match_file:
        await ctx.send("❌ Файлы матчей не найдены. Убедитесь, что сервер GSI запущен и матч активен.")
        return
    
    # Извлекаем игроков
    players = get_players_from_match(match_file)
    
    if not players:
        await ctx.send("❌ Игроки не найдены в данных матча.")
        return
    
    # Формируем сообщение в формате "Ник - Dotabuff ссылка"
    lines = []
    
    for player in players:
        name = player.get('name', 'Unknown')
        dotabuff_url = player.get('dotabuff_url')
        
        if dotabuff_url:
            # Формат: Ник - Dotabuff ссылка
            lines.append(f"{name} - {dotabuff_url}")
        else:
            # Если нет ссылки на Dotabuff, пропускаем игрока или показываем без ссылки
            steamid = player.get('steamid', 'N/A')
            if steamid != 'N/A':
                # Пытаемся создать ссылку вручную
                dotabuff_url = get_dotabuff_url(str(steamid))
                if dotabuff_url:
                    lines.append(f"{name} - {dotabuff_url}")
                else:
                    lines.append(f"{name} - (SteamID: {steamid})")
            else:
                lines.append(f"{name} - (нет SteamID)")
    
    message_text = "\n".join(lines)
    
    # Discord имеет лимит на длину сообщения (2000 символов)
    # Если сообщение слишком длинное, разбиваем на части
    if len(message_text) > 2000:
        # Разбиваем на части по 1900 символов
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 для переноса строки
            
            if current_length + line_length > 1900:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        # Отправляем первое сообщение
        await ctx.send(chunks[0])
        
        # Отправляем остальные части
        for chunk in chunks[1:]:
            await ctx.send(chunk)
    else:
        await ctx.send(message_text)


@bot.command(name='ping')
async def ping_command(ctx):
    """Проверка работы бота."""
    await ctx.send('Pong! Бот работает.')


def main():
    """Запуск Discord бота."""
    if not DISCORD_TOKEN:
        print("ОШИБКА: Не указан DISCORD_TOKEN!")
        print("Установите переменную окружения DISCORD_TOKEN или добавьте её в .env файл")
        print("\nПример:")
        print("  export DISCORD_TOKEN='ваш_токен_бота'")
        print("  # или")
        print("  set DISCORD_TOKEN=ваш_токен_бота  # Windows")
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("ОШИБКА: Неверный токен бота!")
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    main()

