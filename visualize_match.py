"""Скрипт для создания визуализации матча из JSON файла."""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.font_manager as fm

sys.path.insert(0, str(Path(__file__).parent / "src"))
from utils import get_dotabuff_url, get_opendota_url

# Настройка шрифтов для поддержки кириллицы
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']


def load_match_data(json_path: Path) -> Dict[str, Any]:
    """Загружает данные матча из JSON файла."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_final_state(match_data: Dict[str, Any]) -> Dict[str, Any]:
    """Получает финальное состояние матча."""
    if "final_state" in match_data:
        return match_data["final_state"]
    elif "current_state" in match_data:
        return match_data["current_state"]
    else:
        return match_data.get("initial_state", {})


def format_time(seconds: int) -> str:
    """Форматирует время в формат MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def create_match_visualization(match_data: Dict[str, Any], json_path: Optional[Path] = None, output_path: Optional[Path] = None) -> Path:
    """Создает визуализацию матча и сохраняет как изображение."""
    
    final_state = get_final_state(match_data)
    raw_data = final_state.get("raw_data", final_state)
    
    # Извлекаем данные
    map_data = raw_data.get("map", {})
    player_data = raw_data.get("player", {})
    hero_data = raw_data.get("hero", {})
    
    match_id = match_data.get("match_id", "Unknown")
    match_start = match_data.get("match_start", "")
    game_time = map_data.get("game_time", 0)
    clock_time = map_data.get("clock_time", 0)
    
    # Создаем фигуру
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor('#0a0a0a')
    
    # Основной контейнер
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.2, 
                          left=0.05, right=0.95, top=0.95, bottom=0.05)
    
    # === ЗАГОЛОВОК ===
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    ax_title.set_facecolor('#0a0a0a')
    
    title_text = f"Dota 2 Match #{match_id}"
    ax_title.text(0.5, 0.7, title_text, 
                  fontsize=32, fontweight='bold', color='#ffffff',
                  ha='center', va='center')
    
    if match_start:
        try:
            start_dt = datetime.fromisoformat(match_start.replace('Z', '+00:00'))
            start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            start_str = match_start
        ax_title.text(0.5, 0.3, f"Started: {start_str}", 
                     fontsize=14, color='#888888',
                     ha='center', va='center')
    
    # === ИНФОРМАЦИЯ ОБ ИГРОКЕ ===
    ax_player = fig.add_subplot(gs[1, 0])
    ax_player.set_facecolor('#1a1a1a')
    ax_player.axis('off')
    
    player_name = player_data.get("name", "Unknown")
    hero_name = hero_data.get("name", "Unknown")
    # Убираем префикс npc_dota_hero_
    if hero_name.startswith("npc_dota_hero_"):
        hero_name = hero_name.replace("npc_dota_hero_", "").replace("_", " ").title()
    
    ax_player.text(0.1, 0.9, "Player Info", fontsize=18, fontweight='bold', 
                   color='#4a9eff', transform=ax_player.transAxes)
    ax_player.text(0.1, 0.75, f"Name: {player_name}", fontsize=14, 
                   color='#ffffff', transform=ax_player.transAxes)
    ax_player.text(0.1, 0.6, f"Hero: {hero_name}", fontsize=14, 
                   color='#ffffff', transform=ax_player.transAxes)
    
    steamid = player_data.get("steamid", "N/A")
    ax_player.text(0.1, 0.45, f"SteamID: {steamid}", fontsize=12, 
                   color='#888888', transform=ax_player.transAxes)
    
    # Добавляем ссылку на Dotabuff
    dotabuff_url = get_dotabuff_url(str(steamid)) if steamid != "N/A" else None
    if dotabuff_url:
        # Разбиваем длинную ссылку на несколько строк для лучшей читаемости
        ax_player.text(0.1, 0.25, "Dotabuff Profile:", fontsize=10, 
                      color='#888888', transform=ax_player.transAxes)
        # Показываем только домен и ID для компактности
        profile_id = dotabuff_url.split('/')[-1]
        ax_player.text(0.1, 0.1, f"dotabuff.com/players/{profile_id}", fontsize=9, 
                      color='#4a9eff', transform=ax_player.transAxes,
                      style='italic')
    
    # === СТАТИСТИКА ===
    ax_stats = fig.add_subplot(gs[1, 1])
    ax_stats.set_facecolor('#1a1a1a')
    ax_stats.axis('off')
    
    kills = player_data.get("kills", 0)
    deaths = player_data.get("deaths", 0)
    assists = player_data.get("assists", 0)
    kda = f"{kills}/{deaths}/{assists}"
    
    last_hits = player_data.get("last_hits", 0)
    denies = player_data.get("denies", 0)
    gold = player_data.get("gold", 0)
    gpm = player_data.get("gpm", 0)
    xpm = player_data.get("xpm", 0)
    level = hero_data.get("level", 1)
    
    ax_stats.text(0.1, 0.9, "Statistics", fontsize=18, fontweight='bold', 
                  color='#4a9eff', transform=ax_stats.transAxes)
    ax_stats.text(0.1, 0.75, f"K/D/A: {kda}", fontsize=14, 
                  color='#ffffff', transform=ax_stats.transAxes)
    ax_stats.text(0.1, 0.6, f"Level: {level}", fontsize=14, 
                  color='#ffffff', transform=ax_stats.transAxes)
    ax_stats.text(0.1, 0.45, f"Last Hits: {last_hits} | Denies: {denies}", 
                  fontsize=12, color='#ffffff', transform=ax_stats.transAxes)
    ax_stats.text(0.1, 0.3, f"Gold: {gold:,} ({gpm} GPM)", 
                  fontsize=12, color='#ffd700', transform=ax_stats.transAxes)
    ax_stats.text(0.1, 0.15, f"XPM: {xpm}", 
                  fontsize=12, color='#00ff88', transform=ax_stats.transAxes)
    
    # === ГРАФИК ЗДОРОВЬЯ И МАНЫ ===
    ax_hp_mana = fig.add_subplot(gs[2, 0])
    ax_hp_mana.set_facecolor('#1a1a1a')
    
    health = hero_data.get("health", 0)
    max_health = hero_data.get("max_health", 1)
    mana = hero_data.get("mana", 0)
    max_mana = hero_data.get("max_mana", 1)
    
    health_percent = (health / max_health * 100) if max_health > 0 else 0
    mana_percent = (mana / max_mana * 100) if max_mana > 0 else 0
    
    # Бар здоровья
    bar1 = ax_hp_mana.barh(0, health_percent, height=0.3, color='#ff4444', 
                           edgecolor='#ffffff', linewidth=2)
    ax_hp_mana.barh(0, 100, height=0.3, color='#333333', alpha=0.3, 
                    edgecolor='#ffffff', linewidth=2)
    ax_hp_mana.text(50, 0, f"HP: {health}/{max_health}", 
                   fontsize=14, color='#ffffff', ha='center', va='center',
                   fontweight='bold')
    
    # Бар маны
    bar2 = ax_hp_mana.barh(0.5, mana_percent, height=0.3, color='#4444ff', 
                           edgecolor='#ffffff', linewidth=2)
    ax_hp_mana.barh(0.5, 100, height=0.3, color='#333333', alpha=0.3, 
                    edgecolor='#ffffff', linewidth=2)
    ax_hp_mana.text(50, 0.5, f"MP: {mana}/{max_mana}", 
                   fontsize=14, color='#ffffff', ha='center', va='center',
                   fontweight='bold')
    
    ax_hp_mana.set_xlim(0, 100)
    ax_hp_mana.set_ylim(-0.2, 0.8)
    ax_hp_mana.set_xticks([])
    ax_hp_mana.set_yticks([])
    ax_hp_mana.spines['top'].set_visible(False)
    ax_hp_mana.spines['right'].set_visible(False)
    ax_hp_mana.spines['bottom'].set_visible(False)
    ax_hp_mana.spines['left'].set_visible(False)
    ax_hp_mana.set_facecolor('#1a1a1a')
    
    # === ПРЕДМЕТЫ ===
    ax_items = fig.add_subplot(gs[2, 1])
    ax_items.set_facecolor('#1a1a1a')
    ax_items.axis('off')
    
    items_data = raw_data.get("items", {})
    items_list = []
    for slot in ["slot0", "slot1", "slot2", "slot3", "slot4", "slot5"]:
        item = items_data.get(slot, {})
        if item and item.get("name") and item.get("name") != "empty":
            item_name = item.get("name", "").replace("item_", "").replace("_", " ").title()
            items_list.append(item_name)
    
    ax_items.text(0.1, 0.9, "Items", fontsize=18, fontweight='bold', 
                 color='#4a9eff', transform=ax_items.transAxes)
    
    if items_list:
        y_pos = 0.75
        for i, item_name in enumerate(items_list[:6]):  # Показываем до 6 предметов
            ax_items.text(0.1, y_pos, f"• {item_name}", fontsize=11, 
                        color='#ffffff', transform=ax_items.transAxes)
            y_pos -= 0.12
    else:
        ax_items.text(0.1, 0.5, "No items", fontsize=12, 
                     color='#888888', transform=ax_items.transAxes)
    
    # Время матча внизу
    game_time_str = format_time(game_time)
    clock_time_str = format_time(max(0, clock_time)) if clock_time >= 0 else "Pre-game"
    ax_items.text(0.5, 0.05, f"Time: {game_time_str} | Clock: {clock_time_str}", 
                 fontsize=10, color='#888888', ha='center', transform=ax_items.transAxes)
    
    # Сохраняем изображение
    if output_path is None:
        if json_path:
            # Сохраняем в той же папке, что и JSON файл
            output_path = json_path.parent / f"match_{match_id}_visualization.png"
        else:
            # Сохраняем в текущей директории
            output_path = Path(f"match_{match_id}_visualization.png")
    
    plt.savefig(output_path, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    
    return output_path


def main():
    """Основная функция."""
    if len(sys.argv) < 2:
        print("Использование: python visualize_match.py <путь_к_json_файлу>")
        print("\nПример:")
        print("  python visualize_match.py output/2026-01-03/match_123.json")
        return
    
    json_path = Path(sys.argv[1])
    
    if not json_path.exists():
        print(f"Ошибка: Файл {json_path} не найден")
        return
    
    try:
        print(f"Загрузка данных из {json_path}...")
        match_data = load_match_data(json_path)
        
        print("Создание визуализации...")
        output_path = create_match_visualization(match_data, json_path)
        
        print(f"Визуализация сохранена: {output_path}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

