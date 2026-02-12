"""
Загрузка данных из JIRA
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class JiraDataLoader:
    """Загрузчик данных из JIRA"""
    
    def __init__(self, config):
        self.config = config
        self.df = None
        self.df_daily = None
        self.df_clean = None
        self.classroom_stats = None
        self.category_stats = None
        self.group_a_tickets = []
        self.group_b_tickets = []
    
    def load_data(self):
        """ШАГ 1: Загружаем основной файл с заявками"""
        
        file_path = Path(self.config.DATA_PATH)
        
        if not file_path.exists():
            print(f"❌ Файл {file_path} не найден!")
            print("📁 Скопируйте файлы в папку data/")
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        print(f"📂 Загружаем файл: {file_path.name}")
        
        # Пробуем разные разделители
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8-sig', sep=',')
            print("✓ Разделитель: запятая (,)")
        except:
            try:
                self.df = pd.read_csv(file_path, encoding='utf-8-sig', sep=';')
                print("✓ Разделитель: точка с запятой (;)")
            except:
                self.df = pd.read_csv(file_path, encoding='utf-8-sig')
                print("✓ Разделитель: автоопределение")
        
        # Проверяем, не слиплись ли колонки
        if len(self.df.columns) == 1:
            print("  ⚠ Исправляем слипшиеся колонки...")
            first_col = self.df.columns[0]
            splitted = self.df[first_col].str.split(',', expand=True)
            headers = splitted.iloc[0].tolist()
            data = splitted.iloc[1:]
            self.df = pd.DataFrame(data.values, columns=headers)
            print(f"  ✓ Исправлено! {len(self.df.columns)} колонок")
        
        print(f"✓ Загружено строк: {len(self.df)}")
        print(f"✓ Колонок: {len(self.df.columns)}")
        
        return self.df
    
    def load_daily_data(self):
        """ШАГ 2: Загружаем ежедневную статистику"""
        
        file_path = Path(self.config.DAILY_DATA_PATH)
        
        if not file_path.exists():
            print("⚠ Файл с ежедневной статистикой не найден")
            return None
        
        try:
            self.df_daily = pd.read_csv(file_path, encoding='utf-8-sig', sep=';')
            self.df_daily['Дата'] = pd.to_datetime(self.df_daily['Дата'])
            print(f"✓ Загружено {len(self.df_daily)} дней статистики")
        except:
            try:
                self.df_daily = pd.read_csv(file_path, encoding='utf-8-sig', sep=',')
                self.df_daily['Дата'] = pd.to_datetime(self.df_daily['Дата'])
                print(f"✓ Загружено {len(self.df_daily)} дней статистики")
            except:
                print("⚠ Не удалось загрузить ежедневную статистику")
        
        return self.df_daily
    
    def clean_data(self):
        """ШАГ 3: Очищаем и готовим данные"""
        
        print("\n🧹 Очищаем данные...")
        
        df = self.df.copy()
        
        # 1. ВРЕМЯ РЕШЕНИЯ
        print("  • Обрабатываем время решения...")
        
        # Ищем колонку с временем
        time_col = None
        for col in df.columns:
            if 'время' in col.lower() or 'часы' in col.lower():
                time_col = col
                break
        
        if time_col:
            df['time_resolution_hours'] = df[time_col].astype(str)
            df['time_resolution_hours'] = df['time_resolution_hours'].str.replace(',', '.')
            df['time_resolution_hours'] = df['time_resolution_hours'].str.strip()
            df['time_resolution_hours'] = df['time_resolution_hours'].replace('', np.nan)
            df['time_resolution_hours'] = pd.to_numeric(df['time_resolution_hours'], errors='coerce')
        else:
            df['time_resolution_hours'] = np.nan
        
        # 2. ДАТЫ
        print("  • Обрабатываем даты...")
        try:
            date_col = None
            for col in df.columns:
                if 'created' in col.lower() or 'дата' in col.lower():
                    date_col = col
                    break
            
            if date_col:
                df['created_datetime'] = pd.to_datetime(df[date_col], format='%d/%m/%Y %H:%M', errors='coerce')
                df['created_date'] = df['created_datetime'].dt.date
        except Exception as e:
            print(f"  ⚠ Ошибка обработки дат: {e}")
        
        # 3. ГРУППЫ
        print("  • Определяем группы...")
        group_col = None
        for col in df.columns:
            if 'групп' in col.lower():
                group_col = col
                break
        
        if group_col:
            df['group_numeric'] = df[group_col].map({'A': 0, 'B': 1})
            self.config.COLUMN_GROUP = group_col
        
        # 4. КРИТИЧНЫЕ ЗАЯВКИ
        priority_col = None
        for col in df.columns:
            if 'priority' in col.lower() or 'приоритет' in col.lower():
                priority_col = col
                break
        
        if priority_col:
            df['is_critical'] = (df[priority_col] == 'Highest').astype(int)
        
        # 5. РЕШЕННЫЕ ЗАЯВКИ
        status_col = None
        for col in df.columns:
            if 'status' in col.lower() or 'статус' in col.lower():
                status_col = col
                break
        
        if status_col:
            df['is_resolved'] = df[status_col].isin(['Решена', 'Закрыта']).astype(int)
        
        self.df_clean = df
        print("✓ Данные очищены!")
        
        return df
    
    def prepare_for_analysis(self):
        """ШАГ 4: Готовим данные для анализа"""
        
        print("\n📊 Готовим данные для анализа...")
        
        df = self.df_clean
        
        # 1. Находим колонки
        group_col = None
        for col in df.columns:
            if 'групп' in col.lower():
                group_col = col
                break
        
        audience_col = None
        for col in df.columns:
            if 'аудитор' in col.lower():
                audience_col = col
                break
        
        category_col = None
        for col in df.columns:
            if 'категор' in col.lower() or 'проблем' in col.lower():
                category_col = col
                break
        
        # 2. Агрегация по аудиториям
        if audience_col and group_col:
            classroom_stats = df.groupby([audience_col, group_col]).agg({
                'Issue Key': 'count',
                'time_resolution_hours': 'mean',
                'is_critical': 'sum',
                'is_resolved': 'mean'
            }).rename(columns={
                'Issue Key': 'ticket_count',
                'time_resolution_hours': 'avg_resolution_time',
                'is_critical': 'critical_tickets',
                'is_resolved': 'resolution_rate'
            }).reset_index()
            
            self.classroom_stats = classroom_stats
            self.group_a_tickets = classroom_stats[classroom_stats[group_col] == 'A']['ticket_count'].tolist()
            self.group_b_tickets = classroom_stats[classroom_stats[group_col] == 'B']['ticket_count'].tolist()
        
        # 3. Статистика по категориям
        if category_col and group_col:
            category_stats = df.groupby([category_col, group_col]).size().unstack(fill_value=0)
            
            if 'B' in category_stats.columns:
                category_stats['change'] = category_stats['B'] - category_stats['A']
                category_stats['change_percent'] = ((category_stats['B'] - category_stats['A']) / 
                                                   category_stats['A'] * 100).round(1)
            
            self.category_stats = category_stats
        
        print(f"✓ Аудиторий в группе A: {len(self.group_a_tickets)}")
        print(f"✓ Аудиторий в группе B: {len(self.group_b_tickets)}")
        
        return self.classroom_stats, self.category_stats