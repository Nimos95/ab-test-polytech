"""
Вспомогательные функции
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any

def ensure_dir(path):
    """Создание директории, если её нет"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def convert_numpy(obj):
    """Рекурсивное преобразование numpy типов в Python типы"""
    if obj is None:
        return None
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, tuple):
        return [convert_numpy(item) for item in obj]
    elif isinstance(obj, dict):
        return {convert_numpy(k): convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy(item) for item in obj]
    elif isinstance(obj, (np.inf, -np.inf)):
        return None
    elif isinstance(obj, float) and pd.isna(obj):  # проверка на NaN
        return None
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, 'item'):  # для некоторых numpy типов
        try:
            return obj.item()
        except:
            return str(obj)
    else:
        return obj

def save_results(results, filename="results.json"):
    """Сохранение результатов в JSON"""
    
    try:
        # Создаем папку reports если её нет
        output_path = Path("reports") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Конвертируем numpy типы в обычные Python типы
        results_serializable = convert_numpy(results)
        
        # Сохраняем в JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_serializable, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Результаты сохранены в {output_path}")
        return output_path
        
    except Exception as e:
        print(f"⚠ Не удалось сохранить JSON: {e}")
        
        # Сохраняем в текстовый файл как резервный вариант
        try:
            backup_path = Path("reports") / "results_backup.txt"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write("=== РЕЗУЛЬТАТЫ A/B-ТЕСТА ===\n")
                f.write(f"Дата: {datetime.now()}\n\n")
                f.write(str(results))
            print(f"✓ Резервная копия сохранена в {backup_path}")
            return backup_path
        except:
            print("❌ Не удалось сохранить результаты")
            return None

def print_header(text):
    """Красивый вывод заголовка"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def print_success(text):
    """Вывод успешного сообщения"""
    print(f"✅ {text}")

def print_warning(text):
    """Вывод предупреждения"""
    print(f"⚠️ {text}")

def print_error(text):
    """Вывод ошибки"""
    print(f"❌ {text}")