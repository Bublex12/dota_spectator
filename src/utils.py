"""Утилиты для работы с данными Dota 2."""
from typing import Optional


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

