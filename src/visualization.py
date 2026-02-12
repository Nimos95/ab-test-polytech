"""
Визуализация результатов A/B-теста
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

# Настройка стилей для красивых графиков
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['font.family'] = 'DejaVu Sans'  # Поддержка русского языка

class ABTestVisualizer:
    """Класс для создания графиков"""
    
    def __init__(self, config):
        self.config = config
        
        # Создаем папку для графиков
        self.figures_dir = Path("reports/figures")
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Папка для графиков: {self.figures_dir}")
    
    def plot_ticket_comparison(self, group_a, group_b):
        """ГРАФИК 1: Сравнение групп (столбчатая диаграмма + box plot)"""
        
        print("\n📈 Создаем график сравнения групп...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # ===== ГРАФИК 1.1: Столбчатая диаграмма со стандартными ошибками =====
        ax1 = axes[0]
        means = [np.mean(group_a), np.mean(group_b)]
        errors = [stats.sem(group_a), stats.sem(group_b)]
        
        bars = ax1.bar([0, 1], means, 
                       yerr=errors, 
                       capsize=10,
                       color=[self.config.COLOR_A, self.config.COLOR_B],
                       edgecolor='black',
                       linewidth=2,
                       alpha=0.8,
                       error_kw={'linewidth': 2, 'ecolor': 'black'})
        
        ax1.set_xticks([0, 1])
        ax1.set_xticklabels([f'{self.config.GROUP_A_NAME}\n(n={len(group_a)})', 
                            f'{self.config.GROUP_B_NAME}\n(n={len(group_b)})'],
                           fontsize=10)
        ax1.set_ylabel('Среднее количество заявок на аудиторию', fontsize=11)
        ax1.set_title('Сравнение средних значений', fontweight='bold', fontsize=12)
        ax1.grid(axis='y', alpha=0.3)
        
        # Добавляем цифры на столбцы
        for bar, mean, err in zip(bars, means, errors):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + err + 0.2,
                    f'{mean:.1f} ± {err:.1f}', 
                    ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # ===== ГРАФИК 1.2: Box plot (распределение) =====
        ax2 = axes[1]
        bp = ax2.boxplot([group_a, group_b], 
                        patch_artist=True,
                        labels=['Группа A', 'Группа B'],
                        widths=0.6)
        
        # Раскрашиваем box plot
        colors = [self.config.COLOR_A, self.config.COLOR_B]
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)
        
        # Настройка линий
        for whisker in bp['whiskers']:
            whisker.set_color('black')
            whisker.set_linewidth(1.2)
        for cap in bp['caps']:
            cap.set_color('black')
            cap.set_linewidth(1.2)
        for median in bp['medians']:
            median.set_color('red')
            median.set_linewidth(2)
        for flier in bp['fliers']:
            flier.set_marker('o')
            flier.set_color('gray')
            flier.set_alpha(0.5)
        
        ax2.set_ylabel('Количество заявок', fontsize=11)
        ax2.set_title('Распределение заявок по аудиториям', fontweight='bold', fontsize=12)
        ax2.grid(axis='y', alpha=0.3)
        
        # Добавляем подписи с медианой
        medians = [np.median(group_a), np.median(group_b)]
        for i, median in enumerate(medians, 1):
            ax2.text(i, median + 0.1, f'медиана: {median:.0f}', 
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.suptitle('A/B-тест: Сравнение контрольной и тестовой групп', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # Сохраняем в разных форматах
        plt.savefig(self.figures_dir / '01_ticket_comparison.png', 
                   dpi=300, bbox_inches='tight')
        plt.savefig(self.figures_dir / '01_ticket_comparison.pdf', 
                   bbox_inches='tight')
        
        print(f"  ✓ Сохранено: {self.figures_dir / '01_ticket_comparison.png'}")
        plt.close()
        return fig
    
    def plot_category_heatmap(self, category_stats):
        """ГРАФИК 2: Тепловая карта категорий проблем"""
        
        print("📊 Создаем тепловую карту категорий проблем...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Берем только колонки A и B
        plot_data = category_stats[['A', 'B']].copy()
        plot_data = plot_data.sort_values('A', ascending=False)
        
        # Создаем тепловую карту
        sns.heatmap(plot_data.T, 
                   annot=True, 
                   fmt='d',
                   cmap='RdYlGn_r',
                   cbar_kws={'label': 'Количество заявок'},
                   linewidths=1,
                   linecolor='white',
                   ax=ax)
        
        ax.set_xlabel('Категория проблемы', fontsize=11, fontweight='bold')
        ax.set_ylabel('Группа', fontsize=11, fontweight='bold')
        ax.set_title('Распределение проблем по категориям и группам', 
                    fontweight='bold', fontsize=14)
        
        # Добавляем проценты изменений
        if 'change_percent' in category_stats.columns:
            for i, category in enumerate(plot_data.index):
                change = category_stats.loc[category, 'change_percent']
                color = 'green' if change < 0 else 'red'
                symbol = '▼' if change < 0 else '▲'
                
                ax.text(i + 0.5, 2.2, 
                       f'{symbol} {abs(change):.0f}%', 
                       ha='center', va='center',
                       color=color, fontweight='bold', fontsize=10)
        
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        
        # Сохраняем
        plt.savefig(self.figures_dir / '02_category_heatmap.png', 
                   dpi=300, bbox_inches='tight')
        plt.savefig(self.figures_dir / '02_category_heatmap.pdf', 
                   bbox_inches='tight')
        
        print(f"  ✓ Сохранено: {self.figures_dir / '02_category_heatmap.png'}")
        plt.close()
        return fig
    
    def plot_daily_trends(self, df_daily):
        """ГРАФИК 3: Динамика заявок по дням"""
        
        if df_daily is None:
            print("  ⚠ Нет данных для графика динамики")
            return
        
        print("📉 Создаем график динамики заявок...")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Сглаживание (7-дневное скользящее среднее)
        if len(df_daily) >= 7:
            df_daily['A_smooth'] = df_daily['A'].rolling(window=7, center=True, min_periods=1).mean()
            df_daily['B_smooth'] = df_daily['B'].rolling(window=7, center=True, min_periods=1).mean()
        
        # Исходные данные (прозрачные точки)
        ax.scatter(df_daily['Дата'], df_daily['A'], 
                  color=self.config.COLOR_A, alpha=0.3, s=20, label='Группа A (ежедневно)')
        ax.scatter(df_daily['Дата'], df_daily['B'], 
                  color=self.config.COLOR_B, alpha=0.3, s=20, label='Группа B (ежедневно)')
        
        # Сглаженные тренды
        if 'A_smooth' in df_daily.columns:
            ax.plot(df_daily['Дата'], df_daily['A_smooth'], 
                   color=self.config.COLOR_A, linewidth=3, alpha=0.8,
                   label='Группа A (тренд)')
            ax.plot(df_daily['Дата'], df_daily['B_smooth'], 
                   color=self.config.COLOR_B, linewidth=3, alpha=0.8,
                   label='Группа B (тренд)')
        
        ax.set_xlabel('Дата', fontsize=11, fontweight='bold')
        ax.set_ylabel('Количество заявок', fontsize=11, fontweight='bold')
        ax.set_title('Динамика заявок по дням', fontweight='bold', fontsize=14)
        ax.legend(loc='best', frameon=True, fancybox=True, shadow=True, fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Форматирование дат
        plt.xticks(rotation=45, fontsize=9)
        plt.yticks(fontsize=9)
        
        # Добавляем горизонтальную линию среднего
        ax.axhline(y=np.mean(df_daily['A']), color=self.config.COLOR_A, 
                  linestyle='--', alpha=0.5, label=f'Среднее A: {np.mean(df_daily["A"]):.1f}')
        ax.axhline(y=np.mean(df_daily['B']), color=self.config.COLOR_B, 
                  linestyle='--', alpha=0.5, label=f'Среднее B: {np.mean(df_daily["B"]):.1f}')
        
        plt.tight_layout()
        
        # Сохраняем
        plt.savefig(self.figures_dir / '03_daily_trends.png', 
                   dpi=300, bbox_inches='tight')
        plt.savefig(self.figures_dir / '03_daily_trends.pdf', 
                   bbox_inches='tight')
        
        print(f"  ✓ Сохранено: {self.figures_dir / '03_daily_trends.png'}")
        plt.close()
        return fig
    
    def plot_effect_size(self, results):
        """ГРАФИК 4: Размер эффекта и доверительный интервал"""
        
        print("🎯 Создаем график размера эффекта...")
        
        fig, ax = plt.subplots(figsize=(10, 2))
        
        diff = results['ttest']['mean_diff']
        ci_lower, ci_upper = results['ttest']['confidence_interval']
        
        # Создаем точечный график с доверительным интервалом
        ax.errorbar(diff, 0, 
                   xerr=[[diff - ci_lower], [ci_upper - diff]],
                   fmt='o', 
                   color='darkblue',
                   markersize=15,
                   capsize=10,
                   capthick=2,
                   elinewidth=3,
                   markeredgecolor='white',
                   markeredgewidth=2)
        
        # Вертикальная линия в нуле (нет эффекта)
        ax.axvline(x=0, color='red', linestyle='--', linewidth=2, 
                  label='Нет эффекта', alpha=0.7)
        
        # Добавляем подписи
        ax.text(diff, 0.15, 
               f'Эффект: {diff:.2f} заявок\n95% ДИ: [{ci_lower:.2f}, {ci_upper:.2f}]',
               ha='center', va='bottom', fontweight='bold', fontsize=11,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
        
        ax.set_xlabel('Разница средних (Группа B - Группа A)', fontsize=11, fontweight='bold')
        ax.set_title('Размер эффекта и 95% доверительный интервал', 
                    fontweight='bold', fontsize=14)
        ax.set_yticks([])
        ax.legend(loc='best', fontsize=10)
        
        # Закрашиваем доверительный интервал
        ax.axvspan(ci_lower, ci_upper, alpha=0.2, color='lightblue')
        
        plt.tight_layout()
        
        # Сохраняем
        plt.savefig(self.figures_dir / '04_effect_size.png', 
                   dpi=300, bbox_inches='tight')
        plt.savefig(self.figures_dir / '04_effect_size.pdf', 
                   bbox_inches='tight')
        
        print(f"  ✓ Сохранено: {self.figures_dir / '04_effect_size.png'}")
        plt.close()
        return fig
    
    def create_dashboard(self, loader, analyzer):
        """ГРАФИК 5: Дашборд (все графики на одном листе)"""
        
        print("🎨 Создаем итоговый дашборд...")
        
        fig = plt.figure(figsize=(20, 12))
        
        # Создаем сетку для графиков
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # ===== 1. Сравнение групп (верхний левый) =====
        ax1 = fig.add_subplot(gs[0, 0])
        means = [np.mean(loader.group_a_tickets), np.mean(loader.group_b_tickets)]
        errors = [stats.sem(loader.group_a_tickets), stats.sem(loader.group_b_tickets)]
        
        bars = ax1.bar([0, 1], means, yerr=errors, capsize=5,
                      color=[self.config.COLOR_A, self.config.COLOR_B],
                      edgecolor='black', alpha=0.8)
        ax1.set_xticks([0, 1])
        ax1.set_xticklabels(['A', 'B'])
        ax1.set_ylabel('Среднее заявок')
        ax1.set_title('Сравнение групп', fontweight='bold')
        
        # Добавляем цифры
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{mean:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # ===== 2. Ключевые метрики (верхний центр) =====
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.axis('off')
        
        # Создаем таблицу с метриками
        metrics_data = [
            ['Метрика', 'Группа A', 'Группа B', 'Изменение'],
            ['Заявок на аудиторию', 
             f"{means[0]:.1f}", 
             f"{means[1]:.1f}", 
             f"{(means[1]-means[0])/means[0]*100:.1f}%"],
            ['p-значение', 
             '', 
             '', 
             f"{analyzer.results['ttest']['p_value']:.4f}"],
            ['Статус', 
             '', 
             '', 
             '✅ ЗНАЧИМО' if analyzer.results['ttest']['significant'] else '❌ НЕ ЗНАЧИМО']
        ]
        
        table = ax2.table(cellText=metrics_data, 
                         loc='center',
                         cellLoc='center',
                         colWidths=[0.25, 0.2, 0.2, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Раскрашиваем заголовок
        for i in range(4):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax2.set_title('Ключевые метрики', fontweight='bold')
        
        # ===== 3. Категории проблем (верхний правый) =====
        ax3 = fig.add_subplot(gs[0, 2])
        
        if hasattr(loader, 'category_stats'):
            top_changes = loader.category_stats.nlargest(5, 'change_percent')
            bottom_changes = loader.category_stats.nsmallest(5, 'change_percent')
            
            # Берем топ-3 улучшения и топ-3 ухудшения
            plot_cats = pd.concat([bottom_changes.head(3), top_changes.tail(3)])
            
            colors = ['green' if x < 0 else 'red' for x in plot_cats['change_percent']]
            
            y_pos = range(len(plot_cats))
            ax3.barh(y_pos, plot_cats['change_percent'], color=colors, alpha=0.7)
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(plot_cats.index, fontsize=8)
            ax3.set_xlabel('Изменение %')
            ax3.set_title('Топ изменений', fontweight='bold')
            ax3.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # ===== 4. Box plot (средний левый) =====
        ax4 = fig.add_subplot(gs[1, 0])
        bp = ax4.boxplot([loader.group_a_tickets, loader.group_b_tickets], 
                        labels=['A', 'B'], patch_artist=True)
        bp['boxes'][0].set_facecolor(self.config.COLOR_A)
        bp['boxes'][1].set_facecolor(self.config.COLOR_B)
        ax4.set_ylabel('Заявок')
        ax4.set_title('Распределение заявок', fontweight='bold')
        
        # ===== 5. Размер эффекта (средний центр) =====
        ax5 = fig.add_subplot(gs[1, 1])
        diff = analyzer.results['ttest']['mean_diff']
        ci_lower, ci_upper = analyzer.results['ttest']['confidence_interval']
        
        ax5.errorbar(diff, 0, 
                    xerr=[[diff - ci_lower], [ci_upper - diff]],
                    fmt='o', color='darkblue', markersize=12, capsize=5)
        ax5.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax5.set_xlabel('Разница средних')
        ax5.set_title(f'Эффект: {diff:.1f} заявок', fontweight='bold')
        ax5.set_yticks([])
        
        # ===== 6. Статус теста (средний правый) =====
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.axis('off')
        
        if analyzer.results['ttest']['significant']:
            status_text = f"✅ ТЕСТ ПРОЙДЕН\n\nСнижение заявок: {analyzer.results['descriptive_stats']['effect']['relative_diff']:.1f}%\np = {analyzer.results['ttest']['p_value']:.4f}"
            color = 'lightgreen'
        else:
            status_text = f"❌ ТЕСТ НЕ ПРОЙДЕН\n\nЭффект: {analyzer.results['descriptive_stats']['effect']['relative_diff']:.1f}%\np = {analyzer.results['ttest']['p_value']:.4f}"
            color = 'lightcoral'
        
        ax6.text(0.5, 0.5, status_text,
                ha='center', va='center',
                fontsize=14, fontweight='bold',
                transform=ax6.transAxes,
                bbox=dict(boxstyle='round,pad=1', facecolor=color, alpha=0.3))
        
        # ===== 7. Динамика (нижний ряд, весь) =====
        if loader.df_daily is not None:
            ax7 = fig.add_subplot(gs[2, :])
            ax7.plot(loader.df_daily['Дата'], loader.df_daily['A'], 
                    color=self.config.COLOR_A, alpha=0.5, label='A')
            ax7.plot(loader.df_daily['Дата'], loader.df_daily['B'], 
                    color=self.config.COLOR_B, alpha=0.5, label='B')
            
            if len(loader.df_daily) >= 7:
                ax7.plot(loader.df_daily['Дата'], 
                        loader.df_daily['A'].rolling(7, center=True).mean(),
                        color=self.config.COLOR_A, linewidth=2, label='A (тренд)')
                ax7.plot(loader.df_daily['Дата'], 
                        loader.df_daily['B'].rolling(7, center=True).mean(),
                        color=self.config.COLOR_B, linewidth=2, label='B (тренд)')
            
            ax7.set_xlabel('Дата')
            ax7.set_ylabel('Заявок')
            ax7.set_title('Динамика заявок по дням', fontweight='bold')
            ax7.legend()
            ax7.tick_params(axis='x', rotation=45)
        
        plt.suptitle('A/B-TEST DASHBOARD: Эффективность новой инструкции', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # Сохраняем
        plt.savefig(self.figures_dir / '05_dashboard.png', 
                   dpi=300, bbox_inches='tight')
        plt.savefig(self.figures_dir / '05_dashboard.pdf', 
                   bbox_inches='tight')
        
        print(f"  ✓ Сохранено: {self.figures_dir / '05_dashboard.png'}")
        plt.close()
        return fig