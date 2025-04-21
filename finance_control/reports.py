#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для генерации отчетов и визуализации данных
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QPainter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartGenerator:
    """Класс для генерации графиков и визуализаций"""
    
    @staticmethod
    def generate_category_pie_chart(data, chart_title="Распределение по категориям"):
        """
        Создать круговую диаграмму расходов/доходов по категориям
        
        Args:
            data (list): Список данных для диаграммы (словари с 'category_name', 'total', 'category_color')
            chart_title (str, optional): Заголовок диаграммы
            
        Returns:
            QChartView: Виджет с круговой диаграммой
        """
        # Создание серии для круговой диаграммы
        series = QPieSeries()
        
        # Добавление данных в серию
        total_amount = sum(item['total'] for item in data)
        
        for item in data:
            category = item['category_name']
            amount = item['total']
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            
            # Добавление сектора
            slice = series.append(f"{category} - {amount:.2f} руб.", amount)
            slice.setLabel(f"{category} ({percentage:.1f}%)")
            
            # Установка цвета
            if 'category_color' in item and item['category_color']:
                color = item['category_color']
                slice.setBrush(Qt.GlobalColor.blue)
            
            # Выделяем сектор (отодвигаем от центра)
            slice.setExploded(True)
            slice.setExplodeDistanceFactor(0.05)
        
        # Создание графика
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(chart_title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Создание виджета для отображения графика
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        return chart_view
    
    @staticmethod
    def generate_monthly_bar_chart(data, chart_title="Доходы и расходы по месяцам"):
        """
        Создать гистограмму доходов и расходов по месяцам
        
        Args:
            data (list): Список данных для гистограммы (словари с 'month', 'income', 'expense')
            chart_title (str, optional): Заголовок гистограммы
            
        Returns:
            QChartView: Виджет с гистограммой
        """
        # Создание наборов данных для гистограммы
        income_set = QBarSet("Доходы")
        expense_set = QBarSet("Расходы")
        
        # Установка цветов для наборов
        income_set.setColor(Qt.GlobalColor.green)
        expense_set.setColor(Qt.GlobalColor.red)
        
        # Категории (метки месяцев)
        categories = []
        
        # Добавление данных в наборы
        for item in data:
            month_date = datetime.strptime(item['month'], "%Y-%m")
            month_label = month_date.strftime("%b %Y")
            
            income_set.append(item['income'])
            expense_set.append(item['expense'])
            categories.append(month_label)
        
        # Создание серии
        series = QBarSeries()
        series.append(income_set)
        series.append(expense_set)
        
        # Создание графика
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(chart_title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Создание осей
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        # Настройка легенды
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Создание виджета для отображения графика
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        return chart_view
    
    @staticmethod
    def generate_matplotlib_pie_chart(data, title="Распределение по категориям"):
        """
        Создать круговую диаграмму с использованием Matplotlib
        
        Args:
            data (list): Список данных для диаграммы (словари с 'category_name', 'total', 'category_color')
            title (str, optional): Заголовок диаграммы
            
        Returns:
            FigureCanvas: Холст с круговой диаграммой
        """
        # Создание фигуры и осей
        fig = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        # Проверка наличия данных
        if not data or sum(item['total'] for item in data) == 0:
            ax.text(0.5, 0.5, "Нет данных для отображения", ha='center', va='center')
            fig.tight_layout()
            return FigureCanvas(fig)
        
        # Подготовка данных для диаграммы
        labels = [item['category_name'] for item in data]
        sizes = [item['total'] for item in data]
        colors = [item.get('category_color', '#607D8B') for item in data]
        
        # Выделение самого большого сектора
        explode = [0.1 if s == max(sizes) else 0 for s in sizes]
        
        # Создание круговой диаграммы
        wedges, texts, autotexts = ax.pie(
            sizes, 
            explode=explode, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%', 
            shadow=True, 
            startangle=90
        )
        
        # Настройка текста внутри секторов
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Настройка диаграммы
        ax.axis('equal')  # Обеспечивает круглую форму
        ax.set_title(title)
        
        # Компактное размещение
        fig.tight_layout()
        
        # Создание холста для отображения
        canvas = FigureCanvas(fig)
        return canvas
    
    @staticmethod
    def generate_matplotlib_bar_chart(data, title="Доходы и расходы по месяцам"):
        """
        Создать гистограмму с использованием Matplotlib
        
        Args:
            data (list): Список данных для гистограммы (словари с 'month', 'income', 'expense', 'balance')
            title (str, optional): Заголовок гистограммы
            
        Returns:
            FigureCanvas: Холст с гистограммой
        """
        # Создание фигуры и осей
        fig = Figure(figsize=(10, 6), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        # Проверка наличия данных
        if not data:
            ax.text(0.5, 0.5, "Нет данных для отображения", ha='center', va='center')
            fig.tight_layout()
            return FigureCanvas(fig)
        
        # Подготовка данных для гистограммы
        months = [datetime.strptime(item['month'], "%Y-%m") for item in data]
        incomes = [item['income'] for item in data]
        expenses = [item['expense'] for item in data]
        balances = [item['balance'] for item in data]
        
        # Создание гистограммы
        bar_width = 0.25
        x = np.arange(len(months))
        
        # Рисуем столбцы
        ax.bar(x - bar_width, incomes, bar_width, label='Доходы', color='green', alpha=0.7)
        ax.bar(x, expenses, bar_width, label='Расходы', color='red', alpha=0.7)
        ax.bar(x + bar_width, balances, bar_width, label='Баланс', color='blue', alpha=0.7)
        
        # Настройка осей
        month_labels = [dt.strftime("%b %Y") for dt in months]
        ax.set_xticks(x)
        ax.set_xticklabels(month_labels, rotation=45, ha='right')
        
        # Добавление сетки, заголовка и легенды
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.set_title(title)
        ax.set_xlabel('Месяц')
        ax.set_ylabel('Сумма (руб.)')
        ax.legend()
        
        # Компактное размещение
        fig.tight_layout()
        
        # Создание холста для отображения
        canvas = FigureCanvas(fig)
        return canvas


class ReportGenerator:
    """Класс для генерации финансовых отчетов"""
    
    @staticmethod
    def generate_monthly_report(transactions, year, month):
        """
        Сгенерировать месячный отчет
        
        Args:
            transactions (list): Список транзакций
            year (int): Год
            month (int): Месяц (1-12)
            
        Returns:
            dict: Отчет в виде словаря со статистикой
        """
        # Преобразование месяца в формат строки с ведущим нулем
        month_str = f"{month:02d}"
        
        # Фильтрация транзакций за указанный месяц
        monthly_transactions = [
            t for t in transactions 
            if t['date'].startswith(f"{year}-{month_str}")
        ]
        
        # Суммы доходов и расходов
        total_income = sum(t['amount'] for t in monthly_transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in monthly_transactions if t['type'] == 'expense')
        balance = total_income - total_expense
        
        # Группировка расходов по категориям
        expenses_by_category = {}
        for t in monthly_transactions:
            if t['type'] == 'expense':
                category = t['category_name']
                if category not in expenses_by_category:
                    expenses_by_category[category] = 0
                expenses_by_category[category] += t['amount']
        
        # Сортировка категорий по убыванию суммы
        expenses_by_category = {
            k: v for k, v in sorted(
                expenses_by_category.items(), 
                key=lambda item: item[1], 
                reverse=True
            )
        }
        
        # Группировка доходов по категориям
        income_by_category = {}
        for t in monthly_transactions:
            if t['type'] == 'income':
                category = t['category_name']
                if category not in income_by_category:
                    income_by_category[category] = 0
                income_by_category[category] += t['amount']
        
        # Сортировка категорий по убыванию суммы
        income_by_category = {
            k: v for k, v in sorted(
                income_by_category.items(), 
                key=lambda item: item[1], 
                reverse=True
            )
        }
        
        # Формирование отчета
        report = {
            'year': year,
            'month': month,
            'month_name': datetime(year, month, 1).strftime('%B'),
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'expenses_by_category': expenses_by_category,
            'income_by_category': income_by_category,
            'transactions_count': len(monthly_transactions)
        }
        
        return report
    
    @staticmethod
    def generate_annual_report(transactions, year):
        """
        Сгенерировать годовой отчет
        
        Args:
            transactions (list): Список транзакций
            year (int): Год
            
        Returns:
            dict: Отчет в виде словаря со статистикой
        """
        # Фильтрация транзакций за указанный год
        annual_transactions = [
            t for t in transactions 
            if t['date'].startswith(f"{year}")
        ]
        
        # Суммы доходов и расходов
        total_income = sum(t['amount'] for t in annual_transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in annual_transactions if t['type'] == 'expense')
        balance = total_income - total_expense
        
        # Группировка по месяцам
        monthly_data = {}
        for month in range(1, 13):
            month_str = f"{month:02d}"
            monthly_transactions = [
                t for t in annual_transactions 
                if t['date'].startswith(f"{year}-{month_str}")
            ]
            
            month_income = sum(t['amount'] for t in monthly_transactions if t['type'] == 'income')
            month_expense = sum(t['amount'] for t in monthly_transactions if t['type'] == 'expense')
            month_balance = month_income - month_expense
            
            month_name = datetime(year, month, 1).strftime('%B')
            
            monthly_data[month] = {
                'month_name': month_name,
                'income': month_income,
                'expense': month_expense,
                'balance': month_balance,
                'transactions_count': len(monthly_transactions)
            }
        
        # Группировка расходов по категориям
        expenses_by_category = {}
        for t in annual_transactions:
            if t['type'] == 'expense':
                category = t['category_name']
                if category not in expenses_by_category:
                    expenses_by_category[category] = 0
                expenses_by_category[category] += t['amount']
        
        # Сортировка категорий по убыванию суммы
        expenses_by_category = {
            k: v for k, v in sorted(
                expenses_by_category.items(), 
                key=lambda item: item[1], 
                reverse=True
            )
        }
        
        # Группировка доходов по категориям
        income_by_category = {}
        for t in annual_transactions:
            if t['type'] == 'income':
                category = t['category_name']
                if category not in income_by_category:
                    income_by_category[category] = 0
                income_by_category[category] += t['amount']
        
        # Сортировка категорий по убыванию суммы
        income_by_category = {
            k: v for k, v in sorted(
                income_by_category.items(), 
                key=lambda item: item[1], 
                reverse=True
            )
        }
        
        # Формирование отчета
        report = {
            'year': year,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'monthly_data': monthly_data,
            'expenses_by_category': expenses_by_category,
            'income_by_category': income_by_category,
            'transactions_count': len(annual_transactions)
        }
        
        return report
    
    @staticmethod
    def generate_period_report(transactions, start_date, end_date):
        """
        Сгенерировать отчет за произвольный период
        
        Args:
            transactions (list): Список транзакций
            start_date (datetime или str): Начало периода
            end_date (datetime или str): Конец периода
            
        Returns:
            dict: Отчет в виде словаря со статистикой
        """
        # Преобразование дат в строковый формат, если они переданы как datetime
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")
        
        # Фильтрация транзакций за указанный период
        period_transactions = [
            t for t in transactions 
            if start_date <= t['date'] <= end_date
        ]
        
        # Суммы доходов и расходов
        total_income = sum(t['amount'] for t in period_transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in period_transactions if t['type'] == 'expense')
        balance = total_income - total_expense
        
        # Группировка расходов по категориям
        expenses_by_category = {}
        for t in period_transactions:
            if t['type'] == 'expense':
                category = t['category_name']
                if category not in expenses_by_category:
                    expenses_by_category[category] = 0
                expenses_by_category[category] += t['amount']
        
        # Сортировка категорий по убыванию суммы
        expenses_by_category = {
            k: v for k, v in sorted(
                expenses_by_category.items(), 
                key=lambda item: item[1], 
                reverse=True
            )
        }
        
        # Группировка доходов по категориям
        income_by_category = {}
        for t in period_transactions:
            if t['type'] == 'income':
                category = t['category_name']
                if category not in income_by_category:
                    income_by_category[category] = 0
                income_by_category[category] += t['amount']
        
        # Сортировка категорий по убыванию суммы
        income_by_category = {
            k: v for k, v in sorted(
                income_by_category.items(), 
                key=lambda item: item[1], 
                reverse=True
            )
        }
        
        # Формирование отчета
        report = {
            'start_date': start_date,
            'end_date': end_date,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'expenses_by_category': expenses_by_category,
            'income_by_category': income_by_category,
            'transactions_count': len(period_transactions)
        }
        
        return report
    
    @staticmethod
    def generate_text_report(report):
        """
        Сгенерировать текстовый отчет на основе данных отчета
        
        Args:
            report (dict): Данные отчета
            
        Returns:
            str: Текстовый отчет
        """
        # Определение типа отчета и формирование заголовка
        if 'month' in report:
            # Месячный отчет
            title = f"Финансовый отчет за {report['month_name']} {report['year']} года"
        elif 'start_date' in report:
            # Отчет за произвольный период
            title = f"Финансовый отчет за период с {report['start_date']} по {report['end_date']}"
        else:
            # Годовой отчет
            title = f"Финансовый отчет за {report['year']} год"
        
        # Формирование текста отчета
        text_report = f"{title}\n"
        text_report += "=" * len(title) + "\n\n"
        
        # Общая статистика
        text_report += "ОБЩАЯ СТАТИСТИКА\n"
        text_report += "-" * 20 + "\n"
        text_report += f"Количество транзакций: {report['transactions_count']}\n"
        text_report += f"Общий доход: {report['total_income']:.2f} руб.\n"
        text_report += f"Общий расход: {report['total_expense']:.2f} руб.\n"
        text_report += f"Баланс: {report['balance']:.2f} руб.\n\n"
        
        # Статистика по доходам
        text_report += "ДОХОДЫ ПО КАТЕГОРИЯМ\n"
        text_report += "-" * 20 + "\n"
        if report['income_by_category']:
            for category, amount in report['income_by_category'].items():
                percentage = amount / report['total_income'] * 100 if report['total_income'] > 0 else 0
                text_report += f"{category}: {amount:.2f} руб. ({percentage:.1f}%)\n"
        else:
            text_report += "Нет данных о доходах за указанный период.\n"
        text_report += "\n"
        
        # Статистика по расходам
        text_report += "РАСХОДЫ ПО КАТЕГОРИЯМ\n"
        text_report += "-" * 20 + "\n"
        if report['expenses_by_category']:
            for category, amount in report['expenses_by_category'].items():
                percentage = amount / report['total_expense'] * 100 if report['total_expense'] > 0 else 0
                text_report += f"{category}: {amount:.2f} руб. ({percentage:.1f}%)\n"
        else:
            text_report += "Нет данных о расходах за указанный период.\n"
        text_report += "\n"
        
        # Если это годовой отчет, добавляем статистику по месяцам
        if 'monthly_data' in report:
            text_report += "СТАТИСТИКА ПО МЕСЯЦАМ\n"
            text_report += "-" * 20 + "\n"
            for month in range(1, 13):
                month_data = report['monthly_data'][month]
                text_report += f"{month_data['month_name']}:\n"
                text_report += f"  Доход: {month_data['income']:.2f} руб.\n"
                text_report += f"  Расход: {month_data['expense']:.2f} руб.\n"
                text_report += f"  Баланс: {month_data['balance']:.2f} руб.\n"
                text_report += f"  Количество транзакций: {month_data['transactions_count']}\n\n"
        
        # Дата и время формирования отчета
        text_report += f"\nОтчет сформирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return text_report
    
    @staticmethod
    def save_report_to_file(text_report, filename=None):
        """
        Сохранить текстовый отчет в файл
        
        Args:
            text_report (str): Текст отчета
            filename (str, optional): Имя файла. Если не указано, генерируется автоматически
            
        Returns:
            str: Путь к сохраненному файлу
        """
        # Если имя файла не указано, генерируем его автоматически
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finance_report_{timestamp}.txt"
        
        # Путь для сохранения в текущей директории
        file_path = os.path.join(os.getcwd(), filename)
        
        # Сохранение отчета в файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        return file_path