"""Утилиты для работы с данными Dota 2."""
from typing import Optional, List, Dict, Any
import urllib.request
import json


def get_dotabuff_url(steamid: str) -> Optional[str]:
    """
    Генерирует ссылку на профиль Dotabuff по SteamID.
    
    Args:
        steamid: SteamID игрока (SteamID64, например 76561198218419015)
        
    Returns:
        URL профиля на Dotabuff или None, если SteamID невалидный
    """
    if not steamid:
        return None
    
    # Убираем пробелы и проверяем, что это число
    steamid = str(steamid).strip()
    
    # Проверяем, что это валидный SteamID64 (начинается с 7656119)
    if not steamid.isdigit():
        return None
    
    # SteamID64 должен начинаться с 7656119 и быть длиной 17 символов
    if len(steamid) == 17 and steamid.startswith("7656119"):
        return f"https://www.dotabuff.com/players/{steamid}"
    
    # Если это более короткий SteamID, пытаемся конвертировать
    # Но обычно GSI возвращает уже SteamID64
    return None


def get_opendota_url(steamid: str) -> Optional[str]:
    """
    Генерирует ссылку на профиль OpenDota по SteamID.
    
    Args:
        steamid: SteamID игрока (SteamID64)
        
    Returns:
        URL профиля на OpenDota или None, если SteamID невалидный
    """
    if not steamid:
        return None
    
    steamid = str(steamid).strip()
    
    if not steamid.isdigit():
        return None
    
    if len(steamid) == 17 and steamid.startswith("7656119"):
        return f"https://www.opendota.com/players/{steamid}"
    
    return None


def get_players_from_opendota(match_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Получает информацию обо всех игроках матча через OpenDota API.
    
    Args:
        match_id: ID матча (например, "8633245667")
        
    Returns:
        Список игроков с информацией (steamid, name, team) или None при ошибке
    """
    try:
        url = f"https://api.opendota.com/api/matches/{match_id}"
        
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            players = []
            
            # OpenDota возвращает игроков в массиве players
            if "players" in data and isinstance(data["players"], list):
                for player in data["players"]:
                    account_id = player.get("account_id")
                    # account_id может быть None для анонимных игроков
                    if account_id:
                        # Конвертируем account_id в SteamID64
                        steamid64 = account_id_to_steamid64(account_id)
                        if steamid64:
                            players.append({
                                "steamid": str(steamid64),
                                "name": player.get("personaname") or player.get("name") or "Unknown",
                                "team": "radiant" if player.get("isRadiant") else "dire"
                            })
            
            return players if players else None
            
    except Exception as e:
        print(f"Ошибка при получении данных из OpenDota: {e}")
        return None


def account_id_to_steamid64(account_id: int) -> Optional[str]:
    """
    Конвертирует account_id в SteamID64.
    
    Args:
        account_id: Account ID игрока
        
    Returns:
        SteamID64 в виде строки или None
    """
    if not account_id:
        return None
    
    # Формула конвертации: SteamID64 = account_id + 76561197960265728
    steamid64 = account_id + 76561197960265728
    return str(steamid64)

