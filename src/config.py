"""
Настройки проекта A/B-тестирования
"""

from dataclasses import dataclass

@dataclass
class ABTestConfig:
    """Все настройки в одном месте"""
    
    # Пути к данным - ВАЖНО: укажите правильные имена ваших файлов!
    DATA_PATH: str = "data/jira_simple_export.csv"
    DAILY_DATA_PATH: str = "data/jira_daily_stats.csv"
    
    # Названия групп
    GROUP_A_NAME: str = "Контрольная (старая инструкция)"
    GROUP_B_NAME: str = "Тестовая (новая инструкция)"
    GROUP_A_LABEL: str = "A"
    GROUP_B_LABEL: str = "B"
    
    # Статистические параметры
    ALPHA: float = 0.05  # Уровень значимости (5%)
    
    # Цвета для графиков
    COLOR_A: str = "#FF6B6B"  # Красный
    COLOR_B: str = "#4ECDC4"  # Бирюзовый
    
    # Названия колонок в вашем CSV файле
    COLUMN_GROUP: str = "Группа A/B теста"
    COLUMN_TICKET: str = "Issue Key"
    COLUMN_TIME: str = "Время решения (часы)"
    COLUMN_CATEGORY: str = "Категория проблемы"
    COLUMN_PRIORITY: str = "Priority"
    COLUMN_STATUS: str = "Status"
    COLUMN_DATE: str = "Created"

# Создаем экземпляр настроек
config = ABTestConfig()