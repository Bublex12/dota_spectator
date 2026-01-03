"""Скрипт для определения IP адреса сервера для GSI конфигурации."""
import socket
import sys

def get_local_ip():
    """Получает локальный IP адрес машины."""
    try:
        # Подключаемся к внешнему адресу (не отправляем данные)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def get_public_ip():
    """Получает публичный IP адрес (требует интернет)."""
    try:
        import urllib.request
        with urllib.request.urlopen('https://api.ipify.org', timeout=3) as response:
            return response.read().decode('utf-8')
    except Exception:
        return None

def main():
    """Основная функция."""
    print("=" * 60)
    print("Определение IP адреса для GSI конфигурации")
    print("=" * 60)
    print()
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print("Варианты настройки:")
    print()
    
    if local_ip:
        print(f"1. Локальная сеть (для Dota 2 на том же компьютере или в локальной сети):")
        print(f"   http://{local_ip}:3000/")
        print()
    
    if public_ip:
        print(f"2. Публичный IP (для удаленного сервера):")
        print(f"   http://{public_ip}:3000/")
        print()
        print("   ⚠️  ВНИМАНИЕ: Убедитесь, что:")
        print("   - Порт 3000 открыт в файрволе")
        print("   - Сервер доступен из интернета")
        print()
    
    print("3. Локальный хост (только если Dota 2 на том же компьютере):")
    print("   http://127.0.0.1:3000/")
    print()
    
    print("=" * 60)
    print("Инструкция:")
    print("1. Скопируйте файл gsi_config/gamestate_integration_dota2.cfg.example")
    print("2. Переименуйте в gamestate_integration_dota2.cfg")
    print(f"3. Замените YOUR_SERVER_IP на один из адресов выше")
    print("4. Скопируйте файл в папку конфигурации Dota 2:")
    print("   Windows: C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\cfg\\")
    print("=" * 60)

if __name__ == "__main__":
    main()

