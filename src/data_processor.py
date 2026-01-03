"""Обработчик данных от Dota 2 Game State Integration."""
import logging
from typing import Dict, Any, Optional, List

from utils import get_players_from_opendota

logger = logging.getLogger(__name__)


class DataProcessor:
    """Обрабатывает и структурирует данные от Dota 2 GSI."""
    
    @staticmethod
    def process_gsi_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает сырые данные от GSI и структурирует их.
        
        Args:
            raw_data: Сырые данные от Dota 2 GSI
            
        Returns:
            Структурированные данные
        """
        processed = {
            "metadata": DataProcessor._extract_metadata(raw_data),
            "map": DataProcessor._extract_map_info(raw_data),
            "player": DataProcessor._extract_player_info(raw_data),
            "hero": DataProcessor._extract_hero_info(raw_data),
            "abilities": DataProcessor._extract_abilities_info(raw_data),
            "items": DataProcessor._extract_items_info(raw_data),
            "buildings": DataProcessor._extract_buildings_info(raw_data),
            "events": DataProcessor._extract_events_info(raw_data),
            "raw_data": raw_data  # Сохраняем оригинальные данные
        }
        
        return processed
    
    @staticmethod
    def _extract_metadata(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает метаданные матча."""
        provider = raw_data.get("provider", {})
        return {
            "name": provider.get("name", "Unknown"),
            "appid": provider.get("appid"),
            "version": provider.get("version"),
            "timestamp": provider.get("timestamp")
        }
    
    @staticmethod
    def _extract_map_info(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о карте/матче."""
        map_data = raw_data.get("map", {})
        return {
            "name": map_data.get("name"),
            "matchid": map_data.get("matchid"),
            "game_time": map_data.get("game_time"),
            "clock_time": map_data.get("clock_time"),
            "daytime": map_data.get("daytime"),
            "nightstalker_night": map_data.get("nightstalker_night"),
            "game_state": map_data.get("game_state"),
            "paused": map_data.get("paused"),
            "win_team": map_data.get("win_team"),
            "customgamename": map_data.get("customgamename"),
            "ward_purchase_cooldown": map_data.get("ward_purchase_cooldown")
        }
    
    @staticmethod
    def _extract_player_info(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию об игроке."""
        player_data = raw_data.get("player", {})
        return {
            "steamid": player_data.get("steamid"),
            "name": player_data.get("name"),
            "activity": player_data.get("activity"),
            "kills": player_data.get("kills"),
            "deaths": player_data.get("deaths"),
            "assists": player_data.get("assists"),
            "last_hits": player_data.get("last_hits"),
            "denies": player_data.get("denies"),
            "kill_streak": player_data.get("kill_streak"),
            "team": player_data.get("team"),
            "gold": player_data.get("gold"),
            "gold_reliable": player_data.get("gold_reliable"),
            "gold_unreliable": player_data.get("gold_unreliable"),
            "gold_from_hero_kills": player_data.get("gold_from_hero_kills"),
            "gold_from_creep_kills": player_data.get("gold_from_creep_kills"),
            "gold_from_income": player_data.get("gold_from_income"),
            "gold_from_shared": player_data.get("gold_from_shared"),
            "gpm": player_data.get("gpm"),
            "xpm": player_data.get("xpm")
        }
    
    @staticmethod
    def _extract_hero_info(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о герое."""
        hero_data = raw_data.get("hero", {})
        return {
            "id": hero_data.get("id"),
            "name": hero_data.get("name"),
            "level": hero_data.get("level"),
            "alive": hero_data.get("alive"),
            "respawn_seconds": hero_data.get("respawn_seconds"),
            "buyback_cost": hero_data.get("buyback_cost"),
            "buyback_cooldown": hero_data.get("buyback_cooldown"),
            "health": hero_data.get("health"),
            "max_health": hero_data.get("max_health"),
            "health_percent": hero_data.get("health_percent"),
            "mana": hero_data.get("mana"),
            "max_mana": hero_data.get("max_mana"),
            "mana_percent": hero_data.get("mana_percent"),
            "silenced": hero_data.get("silenced"),
            "stunned": hero_data.get("stunned"),
            "disarmed": hero_data.get("disarmed"),
            "magicimmune": hero_data.get("magicimmune"),
            "hexed": hero_data.get("hexed"),
            "muted": hero_data.get("muted"),
            "break": hero_data.get("break"),
            "has_debuff": hero_data.get("has_debuff"),
            "selected_units": hero_data.get("selected_units", [])
        }
    
    @staticmethod
    def _extract_abilities_info(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Извлекает информацию о способностях."""
        abilities = raw_data.get("abilities", {})
        result = []
        
        for ability_name, ability_data in abilities.items():
            if isinstance(ability_data, dict):
                result.append({
                    "name": ability_name,
                    "level": ability_data.get("level"),
                    "can_cast": ability_data.get("can_cast"),
                    "passive": ability_data.get("passive"),
                    "ability_active": ability_data.get("ability_active"),
                    "cooldown": ability_data.get("cooldown"),
                    "ultimate": ability_data.get("ultimate")
                })
        
        return result
    
    @staticmethod
    def _extract_items_info(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о предметах."""
        items_data = raw_data.get("items", {})
        
        # Проверяем, что items_data является словарем
        if not isinstance(items_data, dict):
            items_data = {}
        
        return {
            "slot0": DataProcessor._extract_item_info(items_data.get("slot0")),
            "slot1": DataProcessor._extract_item_info(items_data.get("slot1")),
            "slot2": DataProcessor._extract_item_info(items_data.get("slot2")),
            "slot3": DataProcessor._extract_item_info(items_data.get("slot3")),
            "slot4": DataProcessor._extract_item_info(items_data.get("slot4")),
            "slot5": DataProcessor._extract_item_info(items_data.get("slot5")),
            "stash0": DataProcessor._extract_item_info(items_data.get("stash0")),
            "stash1": DataProcessor._extract_item_info(items_data.get("stash1")),
            "stash2": DataProcessor._extract_item_info(items_data.get("stash2")),
            "stash3": DataProcessor._extract_item_info(items_data.get("stash3")),
            "stash4": DataProcessor._extract_item_info(items_data.get("stash4")),
            "stash5": DataProcessor._extract_item_info(items_data.get("stash5")),
            "teleport": DataProcessor._extract_item_info(items_data.get("teleport")),
            "neutral0": DataProcessor._extract_item_info(items_data.get("neutral0"))
        }
    
    @staticmethod
    def _extract_item_info(item_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Извлекает информацию об отдельном предмете."""
        if not item_data or not isinstance(item_data, dict):
            return None
        
        return {
            "name": item_data.get("name"),
            "purchaser": item_data.get("purchaser"),
            "can_cast": item_data.get("can_cast"),
            "cooldown": item_data.get("cooldown"),
            "passive": item_data.get("passive"),
            "charges": item_data.get("charges")
        }
    
    @staticmethod
    def _extract_buildings_info(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о зданиях."""
        buildings_data = raw_data.get("buildings", {})
        
        # Проверяем, что buildings_data является словарем
        if not isinstance(buildings_data, dict):
            buildings_data = {}
        
        def safe_get_health(buildings_dict: Dict[str, Any], team: str, building: str) -> Optional[int]:
            """Безопасно извлекает здоровье здания."""
            if not isinstance(buildings_dict, dict):
                return None
            team_data = buildings_dict.get(team, {})
            if not isinstance(team_data, dict):
                return None
            building_data = team_data.get(building, {})
            if isinstance(building_data, dict):
                return building_data.get("health")
            return None
        
        return {
            "radiant": {
                "dota_goodguys_tower1_top": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower1_top"),
                "dota_goodguys_tower2_top": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower2_top"),
                "dota_goodguys_tower3_top": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower3_top"),
                "dota_goodguys_tower1_mid": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower1_mid"),
                "dota_goodguys_tower2_mid": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower2_mid"),
                "dota_goodguys_tower3_mid": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower3_mid"),
                "dota_goodguys_tower1_bot": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower1_bot"),
                "dota_goodguys_tower2_bot": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower2_bot"),
                "dota_goodguys_tower3_bot": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower3_bot"),
                "dota_goodguys_tower4_top": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower4_top"),
                "dota_goodguys_tower4_bot": safe_get_health(buildings_data, "radiant", "dota_goodguys_tower4_bot"),
                "goodguys_fort": safe_get_health(buildings_data, "radiant", "goodguys_fort")
            },
            "dire": {
                "dota_badguys_tower1_top": safe_get_health(buildings_data, "dire", "dota_badguys_tower1_top"),
                "dota_badguys_tower2_top": safe_get_health(buildings_data, "dire", "dota_badguys_tower2_top"),
                "dota_badguys_tower3_top": safe_get_health(buildings_data, "dire", "dota_badguys_tower3_top"),
                "dota_badguys_tower1_mid": safe_get_health(buildings_data, "dire", "dota_badguys_tower1_mid"),
                "dota_badguys_tower2_mid": safe_get_health(buildings_data, "dire", "dota_badguys_tower2_mid"),
                "dota_badguys_tower3_mid": safe_get_health(buildings_data, "dire", "dota_badguys_tower3_mid"),
                "dota_badguys_tower1_bot": safe_get_health(buildings_data, "dire", "dota_badguys_tower1_bot"),
                "dota_badguys_tower2_bot": safe_get_health(buildings_data, "dire", "dota_badguys_tower2_bot"),
                "dota_badguys_tower3_bot": safe_get_health(buildings_data, "dire", "dota_badguys_tower3_bot"),
                "dota_badguys_tower4_top": safe_get_health(buildings_data, "dire", "dota_badguys_tower4_top"),
                "dota_badguys_tower4_bot": safe_get_health(buildings_data, "dire", "dota_badguys_tower4_bot"),
                "badguys_fort": safe_get_health(buildings_data, "dire", "badguys_fort")
            }
        }
    
    @staticmethod
    def _extract_events_info(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о событиях."""
        events_data = raw_data.get("events", {})
        
        # Проверяем, является ли events_data словарем или списком
        if isinstance(events_data, list):
            # Если это список, возвращаем его как есть
            return {
                "events_list": events_data,
                "roshan": {},
                "courier_kills": [],
                "tower_kills": [],
                "chat": []
            }
        elif isinstance(events_data, dict):
            # Если это словарь, извлекаем данные как обычно
            return {
                "roshan": events_data.get("roshan", {}),
                "courier_kills": events_data.get("courier_kills", []),
                "tower_kills": events_data.get("tower_kills", []),
                "chat": events_data.get("chat", [])
            }
        else:
            # Если это что-то другое, возвращаем пустую структуру
            return {
                "roshan": {},
                "courier_kills": [],
                "tower_kills": [],
                "chat": []
            }
    
    @staticmethod
    def is_match_started(raw_data: Dict[str, Any]) -> bool:
        """Проверяет, начался ли матч."""
        map_data = raw_data.get("map", {})
        game_state = map_data.get("game_state")
        return game_state in ["DOTA_GAMERULES_STATE_GAME_IN_PROGRESS", "DOTA_GAMERULES_STATE_PRE_GAME"]
    
    @staticmethod
    def is_match_ended(raw_data: Dict[str, Any]) -> bool:
        """Проверяет, завершен ли матч."""
        map_data = raw_data.get("map", {})
        game_state = map_data.get("game_state")
        return game_state == "DOTA_GAMERULES_STATE_POST_GAME" or map_data.get("win_team") is not None
    
    @staticmethod
    def extract_players_accounts(raw_data: Dict[str, Any], match_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Извлекает аккаунты всех игроков из данных GSI.
        Пытается получить данные обо всех игроках через OpenDota API, если доступен match_id.
        
        Args:
            raw_data: Сырые данные от Dota 2 GSI
            match_id: ID матча для получения данных через OpenDota API
            
        Returns:
            Список словарей с информацией об игроках (steamid, name, team)
        """
        players = []
        
        # Сначала пытаемся получить данные через OpenDota API, если есть match_id
        if match_id:
            opendota_players = get_players_from_opendota(match_id)
            if opendota_players:
                logger.info(f"Получено {len(opendota_players)} игроков через OpenDota API")
                return opendota_players
        
        # Если OpenDota не сработал, используем данные из GSI
        # Текущий игрок (всегда доступен)
        player_data = raw_data.get("player", {})
        if player_data and isinstance(player_data, dict):
            steamid = player_data.get("steamid")
            name = player_data.get("name")
            team = player_data.get("team")
            
            if steamid:
                players.append({
                    "steamid": str(steamid),
                    "name": name or "Unknown",
                    "team": team
                })
        
        # Дополнительные игроки могут быть в других секциях
        # Проверяем все возможные места, где могут быть данные об игроках
        for key in ["players", "allplayers", "teams"]:
            if key in raw_data:
                additional_data = raw_data[key]
                if isinstance(additional_data, dict):
                    for player_key, player_info in additional_data.items():
                        if isinstance(player_info, dict):
                            steamid = player_info.get("steamid") or player_info.get("account_id")
                            name = player_info.get("name")
                            team = player_info.get("team")
                            
                            if steamid:
                                # Проверяем, не добавили ли мы уже этого игрока
                                if not any(p.get("steamid") == str(steamid) for p in players):
                                    players.append({
                                        "steamid": str(steamid),
                                        "name": name or "Unknown",
                                        "team": team
                                    })
                elif isinstance(additional_data, list):
                    for player_info in additional_data:
                        if isinstance(player_info, dict):
                            steamid = player_info.get("steamid") or player_info.get("account_id")
                            name = player_info.get("name")
                            team = player_info.get("team")
                            
                            if steamid:
                                if not any(p.get("steamid") == str(steamid) for p in players):
                                    players.append({
                                        "steamid": str(steamid),
                                        "name": name or "Unknown",
                                        "team": team
                                    })
        
        return players

