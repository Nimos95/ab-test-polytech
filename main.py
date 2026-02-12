#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A/B-тестирование эффективности новой инструкции для мультимедийных систем
Петербургский политехнический университет
"""

import sys
from pathlib import Path

# Добавляем путь к нашим модулям
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.data_loader import JiraDataLoader
from src.analysis import ABTestAnalyzer
from src.visualization import ABTestVisualizer
from src.utils import save_results, print_header, print_success, print_warning

def main():
    """Запуск анализа A/B-теста"""
    
    print_header("A/B-TEST: Анализ эффективности новой инструкции")
    print("Петербургский политехнический университет\n")
    
    # ===== ШАГ 1: ЗАГРУЗКА ДАННЫХ =====
    print("📁 ШАГ 1: Загрузка данных...")
    loader = JiraDataLoader(config)
    
    try:
        df = loader.load_data()
    except FileNotFoundError as e:
        print_error(f"Файл не найден: {e}")
        print("\nСкопируйте ваши CSV файлы в папку 'data':")
        print("  - jira_simple_export.csv")
        print("  - jira_daily_stats.csv (если есть)")
        return
    
    # Загружаем ежедневную статистику
    df_daily = loader.load_daily_data()
    
    # ===== ШАГ 2: ОЧИСТКА ДАННЫХ =====
    print("\n🧹 ШАГ 2: Очистка данных...")
    df_clean = loader.clean_data()
    
    # ===== ШАГ 3: ПОДГОТОВКА К АНАЛИЗУ =====
    print("\n📊 ШАГ 3: Подготовка данных для анализа...")
    classroom_stats, category_stats = loader.prepare_for_analysis()
    
    # Проверяем, что данные загружены
    if len(loader.group_a_tickets) == 0 or len(loader.group_b_tickets) == 0:
        print_error("Не удалось получить данные по группам!")
        return
    
    print_success(f"Группа A: {len(loader.group_a_tickets)} аудиторий")
    print_success(f"Группа B: {len(loader.group_b_tickets)} аудиторий")
    
    # ===== ШАГ 4: СТАТИСТИЧЕСКИЙ АНАЛИЗ =====
    print("\n🔬 ШАГ 4: Статистический анализ...")
    analyzer = ABTestAnalyzer(config)
    results = analyzer.run_full_analysis(
        loader.group_a_tickets,
        loader.group_b_tickets,
        category_stats
    )
    
    # ===== ШАГ 5: ВИЗУАЛИЗАЦИЯ =====
    print("\n🎨 ШАГ 5: Создание графиков...")
    visualizer = ABTestVisualizer(config)
    
    # Создаем все графики
    visualizer.plot_ticket_comparison(loader.group_a_tickets, loader.group_b_tickets)
    visualizer.plot_category_heatmap(category_stats)
    
    if loader.df_daily is not None:
        visualizer.plot_daily_trends(loader.df_daily)
    
    visualizer.plot_effect_size(results)
    visualizer.create_dashboard(loader, analyzer)
    
    # ===== ШАГ 6: СОХРАНЕНИЕ РЕЗУЛЬТАТОВ =====
    print("\n💾 ШАГ 6: Сохранение результатов...")
    save_results(results, "ab_test_results.json")
    
    # ===== ШАГ 7: ВЫВОД РЕЗУЛЬТАТОВ =====
    print("\n📋 ШАГ 7: Результаты анализа:")
    analyzer.print_summary()
    
    print("\n" + "="*70)
    print("✅ ПРОЕКТ УСПЕШНО ЗАВЕРШЕН!")
    print("="*70)
    print("\n📁 Созданные файлы:")
    print("  • reports/figures/ - все графики")
    print("  • reports/ab_test_results.json - результаты в JSON")
    print("\n👉 Откройте папку reports/figures/ чтобы увидеть визуализации!")

if __name__ == "__main__":
    main()