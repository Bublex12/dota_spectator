"""Менеджер для сохранения данных матча в JSON файлы."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from config import OUTPUT_DIR, MAX_FILE_SIZE_MB

logger = logging.getLogger(__name__)


class FileManager:
    """Управляет сохранением данных матча в JSON файлы."""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        """
        Инициализация менеджера файлов.
        
        Args:
            output_dir: Директория для сохранения файлов
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.current_match_id: Optional[str] = None
        self.current_file_path: Optional[Path] = None
        
    def _generate_filename(self, match_id: Optional[str] = None) -> str:
        """
        Генерирует уникальное имя файла для матча.
        
        Args:
            match_id: ID матча (если доступен)
            
        Returns:
            Имя файла
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if match_id:
            return f"match_{match_id}_{timestamp}.json"
        return f"match_{timestamp}.json"
    
    def _get_match_directory(self) -> Path:
        """
        Получает директорию для текущей даты.
        
        Returns:
            Path к директории
        """
        date_dir = self.output_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True)
        return date_dir
    
    def start_new_match(self, match_data: Dict[str, Any]) -> Path:
        """
        Начинает новый матч и создает файл для него.
        
        Args:
            match_data: Начальные данные матча
            
        Returns:
            Path к созданному файлу
        """
        # Пытаемся получить ID матча из данных
        match_id = match_data.get("map", {}).get("matchid") or match_data.get("matchid")
        
        if match_id:
            self.current_match_id = str(match_id)
        else:
            self.current_match_id = None
        
        # Проверяем, существует ли уже файл для этого матча
        # Ищем файлы с таким же match_id в текущей директории
        match_dir = self._get_match_directory()
        
        if self.current_match_id:
            # Ищем существующий файл с таким же match_id
            existing_files = list(match_dir.glob(f"match_{self.current_match_id}_*.json"))
            if existing_files:
                # Используем самый новый файл
                self.current_file_path = max(existing_files, key=lambda p: p.stat().st_mtime)
                logger.debug(f"Найден существующий файл матча: {self.current_file_path}")
                return self.current_file_path
        
        # Если файл уже установлен и существует, используем его
        if self.current_file_path and self.current_file_path.exists():
            logger.debug(f"Используем существующий файл: {self.current_file_path}")
            return self.current_file_path
            
        # Создаем новый файл
        filename = self._generate_filename(self.current_match_id)
        self.current_file_path = match_dir / filename
        
        # Сохраняем начальные данные
        initial_data = {
            "match_start": datetime.now().isoformat(),
            "match_id": self.current_match_id,
            "initial_state": match_data
        }
        
        self._save_to_file(initial_data)
        logger.info(f"Начат новый матч, файл: {self.current_file_path}")
        
        return self.current_file_path
    
    def save_match_data(self, data: Dict[str, Any]) -> None:
        """
        Сохраняет данные матча в файл.
        
        Args:
            data: Данные для сохранения
        """
        if not self.current_file_path or not self.current_file_path.exists():
            # Если файл еще не создан, создаем его
            self.start_new_match(data)
            return
        
        # Загружаем существующие данные
        existing_data = self._load_from_file()
        
        # Если файл пустой или поврежден, пересоздаем его
        if not existing_data:
            logger.warning(f"Файл {self.current_file_path} пустой или поврежден, пересоздаем")
            self.start_new_match(data)
            return
        
        # Добавляем новые данные с временной меткой
        if "updates" not in existing_data:
            existing_data["updates"] = []
            
        existing_data["updates"].append({
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        
        # Обновляем последнее состояние
        existing_data["last_update"] = datetime.now().isoformat()
        existing_data["current_state"] = data
        
        self._save_to_file(existing_data)
    
    def _save_to_file(self, data: Dict[str, Any]) -> None:
        """
        Сохраняет данные в JSON файл.
        
        Args:
            data: Данные для сохранения
        """
        try:
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {self.current_file_path}: {e}")
            raise
    
    def _load_from_file(self) -> Dict[str, Any]:
        """
        Загружает данные из текущего файла.
        
        Returns:
            Словарь с данными или пустой словарь если файл не существует
        """
        if not self.current_file_path or not self.current_file_path.exists():
            return {}
            
        try:
            with open(self.current_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Ошибка при загрузке файла {self.current_file_path}: {e}")
            return {}
    
    def finalize_match(self, final_data: Dict[str, Any]) -> None:
        """
        Завершает матч и добавляет финальные данные.
        
        Args:
            final_data: Финальные данные матча
        """
        if not self.current_file_path:
            return
            
        existing_data = self._load_from_file()
        existing_data["match_end"] = datetime.now().isoformat()
        existing_data["final_state"] = final_data
        
        self._save_to_file(existing_data)
        logger.info(f"Матч завершен, файл: {self.current_file_path}")
        
        # Сбрасываем текущий матч
        self.current_match_id = None
        self.current_file_path = None

