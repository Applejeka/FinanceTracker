#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль с графическим интерфейсом PyQt6
"""

import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QTabWidget, QSpinBox, QFormLayout, QGroupBox, QDialogButtonBox,
    QSplitter, QFrame, QFileDialog, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QDateTime, QSize
from PyQt6.QtGui import QIcon, QColor, QFont, QPixmap

from .database import Database
from .models import Transaction, Category
from .reports import ChartGenerator, ReportGenerator


class MainWindow(QMainWindow):
    """Основное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация базы данных
        self.db = Database()
        
        # Настройка параметров окна
        self.setWindowTitle("FinanceControl - Управление личными финансами")
        self.setMinimumSize(1000, 700)
        
        # Создание центрального виджета
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Основной макет
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Создание вкладок
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Добавление вкладок
        self.setup_dashboard_tab()
        self.setup_transactions_tab()
        self.setup_categories_tab()
        self.setup_analytics_tab()
        self.setup_settings_tab()
        
        # Загрузка данных
        self.load_data()
    
    def setup_dashboard_tab(self):
        """Настройка вкладки 'Главная'"""
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        
        # Верхняя часть - Основные показатели
        metrics_group = QGroupBox("Основные показатели")
        metrics_layout = QHBoxLayout(metrics_group)
        
        # Баланс
        balance_widget = QWidget()
        balance_layout = QVBoxLayout(balance_widget)
        self.balance_label = QLabel("Текущий баланс")
        self.balance_value = QLabel("0.00 руб.")
        self.balance_value.setStyleSheet("font-size: 24px; font-weight: bold;")
        balance_layout.addWidget(self.balance_label)
        balance_layout.addWidget(self.balance_value)
        
        # Доходы
        income_widget = QWidget()
        income_layout = QVBoxLayout(income_widget)
        self.income_label = QLabel("Общий доход")
        self.income_value = QLabel("0.00 руб.")
        self.income_value.setStyleSheet("font-size: 18px; color: green;")
        income_layout.addWidget(self.income_label)
        income_layout.addWidget(self.income_value)
        
        # Расходы
        expense_widget = QWidget()
        expense_layout = QVBoxLayout(expense_widget)
        self.expense_label = QLabel("Общий расход")
        self.expense_value = QLabel("0.00 руб.")
        self.expense_value.setStyleSheet("font-size: 18px; color: red;")
        expense_layout.addWidget(self.expense_label)
        expense_layout.addWidget(self.expense_value)
        
        # Добавление виджетов в макет
        metrics_layout.addWidget(balance_widget)
        metrics_layout.addWidget(income_widget)
        metrics_layout.addWidget(expense_widget)
        
        # Кнопки для быстрого доступа
        buttons_layout = QHBoxLayout()
        
        add_income_btn = QPushButton("Добавить доход")
        add_income_btn.clicked.connect(lambda: self.show_add_transaction_dialog("income"))
        
        add_expense_btn = QPushButton("Добавить расход")
        add_expense_btn.clicked.connect(lambda: self.show_add_transaction_dialog("expense"))
        
        view_report_btn = QPushButton("Сформировать отчет")
        view_report_btn.clicked.connect(self.show_report_dialog)
        
        buttons_layout.addWidget(add_income_btn)
        buttons_layout.addWidget(add_expense_btn)
        buttons_layout.addWidget(view_report_btn)
        
        # Последние транзакции
        recent_group = QGroupBox("Последние транзакции")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(5)
        self.recent_transactions_table.setHorizontalHeaderLabels(
            ["Дата", "Тип", "Категория", "Сумма", "Описание"]
        )
        self.recent_transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        recent_layout.addWidget(self.recent_transactions_table)
        
        # Добавление всех элементов на вкладку
        dashboard_layout.addWidget(metrics_group)
        dashboard_layout.addLayout(buttons_layout)
        dashboard_layout.addWidget(recent_group)
        
        self.tabs.addTab(dashboard_widget, "Главная")
    
    def setup_transactions_tab(self):
        """Настройка вкладки 'Транзакции'"""
        transactions_widget = QWidget()
        transactions_layout = QVBoxLayout(transactions_widget)
        
        # Фильтры
        filters_group = QGroupBox("Фильтры")
        filters_layout = QHBoxLayout(filters_group)
        
        # Период
        period_widget = QWidget()
        period_layout = QFormLayout(period_widget)
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        
        period_layout.addRow("С:", self.date_from)
        period_layout.addRow("По:", self.date_to)
        
        # Тип транзакции
        type_widget = QWidget()
        type_layout = QFormLayout(type_widget)
        
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItem("Все", "all")
        self.transaction_type_combo.addItem("Доходы", "income")
        self.transaction_type_combo.addItem("Расходы", "expense")
        
        type_layout.addRow("Тип:", self.transaction_type_combo)
        
        # Категория
        category_widget = QWidget()
        category_layout = QFormLayout(category_widget)
        
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("Все категории", 0)
        
        category_layout.addRow("Категория:", self.category_filter_combo)
        
        # Кнопка применения фильтров
        apply_filters_btn = QPushButton("Применить фильтры")
        apply_filters_btn.clicked.connect(self.apply_transaction_filters)
        
        # Добавление всех фильтров
        filters_layout.addWidget(period_widget)
        filters_layout.addWidget(type_widget)
        filters_layout.addWidget(category_widget)
        filters_layout.addWidget(apply_filters_btn)
        
        # Таблица транзакций
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(
            ["ID", "Дата", "Тип", "Категория", "Сумма", "Описание"]
        )
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setColumnHidden(0, True)  # Скрываем колонку с ID
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        
        add_transaction_btn = QPushButton("Добавить")
        add_transaction_btn.clicked.connect(lambda: self.show_add_transaction_dialog())
        
        edit_transaction_btn = QPushButton("Редактировать")
        edit_transaction_btn.clicked.connect(self.edit_selected_transaction)
        
        delete_transaction_btn = QPushButton("Удалить")
        delete_transaction_btn.clicked.connect(self.delete_selected_transaction)
        
        actions_layout.addWidget(add_transaction_btn)
        actions_layout.addWidget(edit_transaction_btn)
        actions_layout.addWidget(delete_transaction_btn)
        
        # Добавление всех элементов на вкладку
        transactions_layout.addWidget(filters_group)
        transactions_layout.addWidget(self.transactions_table)
        transactions_layout.addLayout(actions_layout)
        
        self.tabs.addTab(transactions_widget, "Транзакции")
    
    def setup_categories_tab(self):
        """Настройка вкладки 'Категории'"""
        categories_widget = QWidget()
        categories_layout = QHBoxLayout(categories_widget)
        
        # Расходные категории
        expense_categories_group = QGroupBox("Категории расходов")
        expense_categories_layout = QVBoxLayout(expense_categories_group)
        
        self.expense_categories_table = QTableWidget()
        self.expense_categories_table.setColumnCount(3)
        self.expense_categories_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Цвет"]
        )
        self.expense_categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.expense_categories_table.setColumnHidden(0, True)  # Скрываем колонку с ID
        
        expense_actions_layout = QHBoxLayout()
        
        add_expense_category_btn = QPushButton("Добавить")
        add_expense_category_btn.clicked.connect(lambda: self.show_add_category_dialog("expense"))
        
        edit_expense_category_btn = QPushButton("Редактировать")
        edit_expense_category_btn.clicked.connect(lambda: self.edit_selected_category("expense"))
        
        delete_expense_category_btn = QPushButton("Удалить")
        delete_expense_category_btn.clicked.connect(lambda: self.delete_selected_category("expense"))
        
        expense_actions_layout.addWidget(add_expense_category_btn)
        expense_actions_layout.addWidget(edit_expense_category_btn)
        expense_actions_layout.addWidget(delete_expense_category_btn)
        
        expense_categories_layout.addWidget(self.expense_categories_table)
        expense_categories_layout.addLayout(expense_actions_layout)
        
        # Доходные категории
        income_categories_group = QGroupBox("Категории доходов")
        income_categories_layout = QVBoxLayout(income_categories_group)
        
        self.income_categories_table = QTableWidget()
        self.income_categories_table.setColumnCount(3)
        self.income_categories_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Цвет"]
        )
        self.income_categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.income_categories_table.setColumnHidden(0, True)  # Скрываем колонку с ID
        
        income_actions_layout = QHBoxLayout()
        
        add_income_category_btn = QPushButton("Добавить")
        add_income_category_btn.clicked.connect(lambda: self.show_add_category_dialog("income"))
        
        edit_income_category_btn = QPushButton("Редактировать")
        edit_income_category_btn.clicked.connect(lambda: self.edit_selected_category("income"))
        
        delete_income_category_btn = QPushButton("Удалить")
        delete_income_category_btn.clicked.connect(lambda: self.delete_selected_category("income"))
        
        income_actions_layout.addWidget(add_income_category_btn)
        income_actions_layout.addWidget(edit_income_category_btn)
        income_actions_layout.addWidget(delete_income_category_btn)
        
        income_categories_layout.addWidget(self.income_categories_table)
        income_categories_layout.addLayout(income_actions_layout)
        
        # Добавление групп на вкладку
        categories_layout.addWidget(expense_categories_group)
        categories_layout.addWidget(income_categories_group)
        
        self.tabs.addTab(categories_widget, "Категории")
    
    def setup_analytics_tab(self):
        """Настройка вкладки 'Аналитика'"""
        analytics_widget = QWidget()
        analytics_layout = QVBoxLayout(analytics_widget)
        
        # Панель с параметрами
        params_group = QGroupBox("Параметры анализа")
        params_layout = QHBoxLayout(params_group)
        
        # Выбор периода
        period_widget = QWidget()
        period_layout = QFormLayout(period_widget)
        
        self.analytics_date_from = QDateEdit()
        self.analytics_date_from.setDate(QDate.currentDate().addMonths(-3))
        self.analytics_date_from.setCalendarPopup(True)
        
        self.analytics_date_to = QDateEdit()
        self.analytics_date_to.setDate(QDate.currentDate())
        self.analytics_date_to.setCalendarPopup(True)
        
        period_layout.addRow("С:", self.analytics_date_from)
        period_layout.addRow("По:", self.analytics_date_to)
        
        # Тип анализа
        type_widget = QWidget()
        type_layout = QVBoxLayout(type_widget)
        
        self.analytics_type_combo = QComboBox()
        self.analytics_type_combo.addItem("Расходы по категориям", "expense_by_category")
        self.analytics_type_combo.addItem("Доходы по категориям", "income_by_category")
        self.analytics_type_combo.addItem("Динамика по месяцам", "monthly_dynamics")
        
        type_layout.addWidget(QLabel("Тип анализа:"))
        type_layout.addWidget(self.analytics_type_combo)
        
        # Кнопка обновления графиков
        update_charts_btn = QPushButton("Обновить графики")
        update_charts_btn.clicked.connect(self.update_analytics_charts)
        
        # Добавление всех элементов в группу параметров
        params_layout.addWidget(period_widget)
        params_layout.addWidget(type_widget)
        params_layout.addWidget(update_charts_btn)
        
        # Область для графиков
        charts_group = QGroupBox("Визуализация")
        self.charts_layout = QVBoxLayout(charts_group)
        
        # Макет для графиков
        self.chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_widget)
        self.charts_layout.addWidget(self.chart_widget)
        
        # Кнопки для управления отчетами
        reports_layout = QHBoxLayout()
        
        create_report_btn = QPushButton("Сформировать отчет")
        create_report_btn.clicked.connect(self.show_report_dialog)
        
        save_chart_btn = QPushButton("Сохранить график")
        save_chart_btn.clicked.connect(self.save_current_chart)
        
        reports_layout.addWidget(create_report_btn)
        reports_layout.addWidget(save_chart_btn)
        
        # Добавление всех элементов на вкладку
        analytics_layout.addWidget(params_group)
        analytics_layout.addWidget(charts_group)
        analytics_layout.addLayout(reports_layout)
        
        self.tabs.addTab(analytics_widget, "Аналитика")

    
    def setup_settings_tab(self):
        """Настройка вкладки 'Настройки'"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Общие настройки
        general_group = QGroupBox("Общие настройки")
        general_layout = QFormLayout(general_group)
        
        # Дополнительные настройки можно добавить здесь
        
        # База данных
        database_group = QGroupBox("База данных")
        database_layout = QVBoxLayout(database_group)
        
        db_path_layout = QHBoxLayout()
        db_path_label = QLabel("Путь к базе данных:")
        self.db_path_edit = QLineEdit(self.db.db_path)
        self.db_path_edit.setReadOnly(True)
        
        browse_db_btn = QPushButton("Обзор")
        browse_db_btn.clicked.connect(self.browse_db_path)
        
        db_path_layout.addWidget(db_path_label)
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(browse_db_btn)
        
        # Кнопки действий с базой данных
        db_actions_layout = QHBoxLayout()
        
        backup_db_btn = QPushButton("Создать резервную копию")
        backup_db_btn.clicked.connect(self.backup_database)
        
        restore_db_btn = QPushButton("Восстановить из копии")
        restore_db_btn.clicked.connect(self.restore_database)
        
        db_actions_layout.addWidget(backup_db_btn)
        db_actions_layout.addWidget(restore_db_btn)
        
        database_layout.addLayout(db_path_layout)
        database_layout.addLayout(db_actions_layout)
        
        # О программе
        about_group = QGroupBox("О программе")
        about_layout = QVBoxLayout(about_group)
        
        about_text = QLabel(
            "FinanceControl v1.0.0\n"
            "Приложение для учета и анализа личных финансов\n\n"
            "© 2023 - Все права защищены"
        )
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        about_layout.addWidget(about_text)
        
        # Добавление всех групп на вкладку
        settings_layout.addWidget(general_group)
        settings_layout.addWidget(database_group)
        settings_layout.addWidget(about_group)
        settings_layout.addStretch()
        
        self.tabs.addTab(settings_widget, "Настройки")
    
    def load_data(self):
        """Загрузка данных при запуске приложения"""
        self.load_dashboard_data()
        self.load_categories()
        self.load_transactions()
        self.update_analytics_charts()
    
    def load_dashboard_data(self):
        """Загрузка данных для главной панели"""
        # Получение баланса
        balance = self.db.get_balance()
        self.balance_value.setText(f"{balance:.2f} руб.")
        
        # Если баланс отрицательный, покажем его красным
        if balance < 0:
            self.balance_value.setStyleSheet("font-size: 24px; font-weight: bold; color: red;")
        else:
            self.balance_value.setStyleSheet("font-size: 24px; font-weight: bold; color: green;")
        
        # Получение данных о доходах и расходах
        income_transactions = self.db.get_transactions_by_type("income")
        expense_transactions = self.db.get_transactions_by_type("expense")
        
        total_income = sum(t['amount'] for t in income_transactions)
        total_expense = sum(t['amount'] for t in expense_transactions)
        
        self.income_value.setText(f"{total_income:.2f} руб.")
        self.expense_value.setText(f"{total_expense:.2f} руб.")
        
        # Загрузка последних транзакций
        all_transactions = self.db.get_all_transactions()
        recent_transactions = all_transactions[:10]  # Берем только 10 последних
        
        # Очистка таблицы
        self.recent_transactions_table.setRowCount(0)
        
        # Заполнение таблицы транзакциями
        for transaction in recent_transactions:
            row_position = self.recent_transactions_table.rowCount()
            self.recent_transactions_table.insertRow(row_position)
            
            # Дата
            date_item = QTableWidgetItem(transaction['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_transactions_table.setItem(row_position, 0, date_item)
            
            # Тип
            type_text = "Доход" if transaction['type'] == 'income' else "Расход"
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Установка цвета в зависимости от типа
            if transaction['type'] == 'income':
                type_item.setForeground(QColor(0, 128, 0))  # Зеленый
            else:
                type_item.setForeground(QColor(255, 0, 0))  # Красный
                
            self.recent_transactions_table.setItem(row_position, 1, type_item)
            
            # Категория
            category_item = QTableWidgetItem(transaction['category_name'])
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_transactions_table.setItem(row_position, 2, category_item)
            
            # Сумма
            amount_text = f"{transaction['amount']:.2f} руб."
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.recent_transactions_table.setItem(row_position, 3, amount_item)
            
            # Описание
            description_item = QTableWidgetItem(transaction['description'])
            self.recent_transactions_table.setItem(row_position, 4, description_item)
    
    def load_categories(self):
        """Загрузка категорий"""
        # Получение категорий расходов
        expense_categories = self.db.get_categories("expense")
        
        # Очистка таблицы
        self.expense_categories_table.setRowCount(0)
        
        # Заполнение таблицы
        for category in expense_categories:
            row_position = self.expense_categories_table.rowCount()
            self.expense_categories_table.insertRow(row_position)
            
            # ID
            id_item = QTableWidgetItem(str(category['id']))
            self.expense_categories_table.setItem(row_position, 0, id_item)
            
            # Название
            name_item = QTableWidgetItem(category['name'])
            self.expense_categories_table.setItem(row_position, 1, name_item)
            
            # Цвет
            color_item = QTableWidgetItem(category['color'])
            color_item.setBackground(QColor(category['color']))
            self.expense_categories_table.setItem(row_position, 2, color_item)
        
        # Получение категорий доходов
        income_categories = self.db.get_categories("income")
        
        # Очистка таблицы
        self.income_categories_table.setRowCount(0)
        
        # Заполнение таблицы
        for category in income_categories:
            row_position = self.income_categories_table.rowCount()
            self.income_categories_table.insertRow(row_position)
            
            # ID
            id_item = QTableWidgetItem(str(category['id']))
            self.income_categories_table.setItem(row_position, 0, id_item)
            
            # Название
            name_item = QTableWidgetItem(category['name'])
            self.income_categories_table.setItem(row_position, 1, name_item)
            
            # Цвет
            color_item = QTableWidgetItem(category['color'])
            color_item.setBackground(QColor(category['color']))
            self.income_categories_table.setItem(row_position, 2, color_item)
        
        # Заполнение фильтра категорий на вкладке транзакций
        self.category_filter_combo.clear()
        self.category_filter_combo.addItem("Все категории", 0)
        
        for category in expense_categories:
            self.category_filter_combo.addItem(f"[Расход] {category['name']}", category['id'])
        
        for category in income_categories:
            self.category_filter_combo.addItem(f"[Доход] {category['name']}", category['id'])
    
    def load_transactions(self):
        """Загрузка транзакций"""
        # Получение всех транзакций
        transactions = self.db.get_all_transactions()
        
        # Очистка таблицы
        self.transactions_table.setRowCount(0)
        
        # Заполнение таблицы
        for transaction in transactions:
            row_position = self.transactions_table.rowCount()
            self.transactions_table.insertRow(row_position)
            
            # ID
            id_item = QTableWidgetItem(str(transaction['id']))
            self.transactions_table.setItem(row_position, 0, id_item)
            
            # Дата
            date_item = QTableWidgetItem(transaction['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(row_position, 1, date_item)
            
            # Тип
            type_text = "Доход" if transaction['type'] == 'income' else "Расход"
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Установка цвета в зависимости от типа
            if transaction['type'] == 'income':
                type_item.setForeground(QColor(0, 128, 0))  # Зеленый
            else:
                type_item.setForeground(QColor(255, 0, 0))  # Красный
                
            self.transactions_table.setItem(row_position, 2, type_item)
            
            # Категория
            category_item = QTableWidgetItem(transaction['category_name'])
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(row_position, 3, category_item)
            
            # Сумма
            amount_text = f"{transaction['amount']:.2f} руб."
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(row_position, 4, amount_item)
            
            # Описание
            description_item = QTableWidgetItem(transaction['description'])
            self.transactions_table.setItem(row_position, 5, description_item)
    
    def apply_transaction_filters(self):
        """Применение фильтров на вкладке транзакций"""
        # Получение параметров фильтрации
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        
        transaction_type = self.transaction_type_combo.currentData()
        category_id = self.category_filter_combo.currentData()
        
        # Получение всех транзакций за выбранный период
        transactions = self.db.get_transactions_by_date_range(date_from, date_to)
        
        # Фильтрация по типу транзакции
        if transaction_type != "all":
            transactions = [t for t in transactions if t['type'] == transaction_type]
        
        # Фильтрация по категории
        if category_id != 0:
            transactions = [t for t in transactions if t['category_id'] == category_id]
        
        # Очистка таблицы
        self.transactions_table.setRowCount(0)
        
        # Заполнение таблицы
        for transaction in transactions:
            row_position = self.transactions_table.rowCount()
            self.transactions_table.insertRow(row_position)
            
            # ID
            id_item = QTableWidgetItem(str(transaction['id']))
            self.transactions_table.setItem(row_position, 0, id_item)
            
            # Дата
            date_item = QTableWidgetItem(transaction['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(row_position, 1, date_item)
            
            # Тип
            type_text = "Доход" if transaction['type'] == 'income' else "Расход"
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Установка цвета в зависимости от типа
            if transaction['type'] == 'income':
                type_item.setForeground(QColor(0, 128, 0))  # Зеленый
            else:
                type_item.setForeground(QColor(255, 0, 0))  # Красный
                
            self.transactions_table.setItem(row_position, 2, type_item)
            
            # Категория
            category_item = QTableWidgetItem(transaction['category_name'])
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(row_position, 3, category_item)
            
            # Сумма
            amount_text = f"{transaction['amount']:.2f} руб."
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(row_position, 4, amount_item)
            
            # Описание
            description_item = QTableWidgetItem(transaction['description'])
            self.transactions_table.setItem(row_position, 5, description_item)




    
    def update_analytics_charts(self):
        """Обновление графиков на вкладке аналитики"""
        # Очистка текущего макета
        for i in reversed(range(self.chart_layout.count())):
            widget = self.chart_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Получение параметров для анализа
        date_from = self.analytics_date_from.date().toString("yyyy-MM-dd")
        date_to = self.analytics_date_to.date().toString("yyyy-MM-dd")
        
        analytics_type = self.analytics_type_combo.currentData()
        
        # Создание соответствующего графика
        if analytics_type == "expense_by_category":
            # Расходы по категориям
            expense_data = self.db.get_expenses_by_category(date_from, date_to)
            if expense_data:
                chart = ChartGenerator.generate_matplotlib_pie_chart(
                    expense_data, 
                    title=f"Расходы по категориям ({date_from} - {date_to})"
                )
                self.chart_layout.addWidget(chart)
            else:
                no_data_label = QLabel("Нет данных для отображения")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.chart_layout.addWidget(no_data_label)
        
        elif analytics_type == "income_by_category":
            # Доходы по категориям
            income_data = self.db.get_income_by_category(date_from, date_to)
            if income_data:
                chart = ChartGenerator.generate_matplotlib_pie_chart(
                    income_data, 
                    title=f"Доходы по категориям ({date_from} - {date_to})"
                )
                self.chart_layout.addWidget(chart)
            else:
                no_data_label = QLabel("Нет данных для отображения")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.chart_layout.addWidget(no_data_label)
        
        elif analytics_type == "monthly_dynamics":
            # Динамика по месяцам
            monthly_data = self.db.get_transactions_by_month(date_from, date_to)
            if monthly_data:
                chart = ChartGenerator.generate_matplotlib_bar_chart(
                    monthly_data,
                    title=f"Динамика доходов и расходов по месяцам ({date_from} - {date_to})"
                )
                self.chart_layout.addWidget(chart)
            else:
                no_data_label = QLabel("Нет данных для отображения")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.chart_layout.addWidget(no_data_label)
    
    def show_add_transaction_dialog(self, transaction_type=None):
        """Показать диалог добавления транзакции"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление транзакции")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Форма для ввода данных
        form_layout = QFormLayout()
        
        # Тип транзакции
        transaction_type_combo = QComboBox()
        transaction_type_combo.addItem("Расход", "expense")
        transaction_type_combo.addItem("Доход", "income")
        
        if transaction_type:
            # Установка выбранного типа, если он указан
            index = 0 if transaction_type == "expense" else 1
            transaction_type_combo.setCurrentIndex(index)
        
        form_layout.addRow("Тип:", transaction_type_combo)
        
        # Сумма
        amount_edit = QLineEdit()
        amount_edit.setPlaceholderText("Введите сумму")
        form_layout.addRow("Сумма:", amount_edit)
        
        # Категория
        category_combo = QComboBox()
        
        # Заполнение списка категорий в зависимости от типа транзакции
        def update_categories():
            category_combo.clear()
            category_type = transaction_type_combo.currentData()
            categories = self.db.get_categories(category_type)
            
            for category in categories:
                category_combo.addItem(category['name'], category['id'])
        
        # Обновление списка категорий при изменении типа транзакции
        transaction_type_combo.currentIndexChanged.connect(update_categories)
        
        # Начальное заполнение
        update_categories()
        
        form_layout.addRow("Категория:", category_combo)
        
        # Дата
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        form_layout.addRow("Дата:", date_edit)
        
        # Описание
        description_edit = QTextEdit()
        description_edit.setPlaceholderText("Введите описание (необязательно)")
        description_edit.setMaximumHeight(100)
        form_layout.addRow("Описание:", description_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(buttons)
        
        # Обработка результата диалога
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Получение данных из формы
                selected_type = transaction_type_combo.currentData()
                amount = float(amount_edit.text().replace(',', '.'))
                category_id = category_combo.currentData()
                date = date_edit.date().toString("yyyy-MM-dd")
                description = description_edit.toPlainText()
                
                # Проверка суммы
                if amount <= 0:
                    raise ValueError("Сумма должна быть положительным числом")
                
                # Добавление транзакции
                self.db.add_transaction(
                    amount=amount,
                    category_id=category_id,
                    description=description,
                    transaction_type=selected_type,
                    date=date
                )
                
                # Обновление данных
                self.load_data()
                
                QMessageBox.information(
                    self,
                    "Успех",
                    "Транзакция успешно добавлена"
                )
            
            except ValueError as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при добавлении транзакции: {str(e)}"
                )
    
    def edit_selected_transaction(self):
        """Редактирование выбранной транзакции"""
        # Получение выбранной строки
        selected_row = self.transactions_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите транзакцию для редактирования"
            )
            return
        
        # Получение ID транзакции
        transaction_id = int(self.transactions_table.item(selected_row, 0).text())
        
        # Получение данных о транзакции
        transaction = self.db.get_transaction_by_id(transaction_id)
        if not transaction:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Транзакция не найдена"
            )
            return
        
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование транзакции")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Форма для ввода данных
        form_layout = QFormLayout()
        
        # Тип транзакции
        transaction_type_combo = QComboBox()
        transaction_type_combo.addItem("Расход", "expense")
        transaction_type_combo.addItem("Доход", "income")
        
        # Установка текущего типа
        index = 0 if transaction['type'] == "expense" else 1
        transaction_type_combo.setCurrentIndex(index)
        
        form_layout.addRow("Тип:", transaction_type_combo)
        
        # Сумма
        amount_edit = QLineEdit(str(transaction['amount']))
        form_layout.addRow("Сумма:", amount_edit)
        
        # Категория
        category_combo = QComboBox()
        
        # Заполнение списка категорий в зависимости от типа транзакции
        def update_categories():
            category_combo.clear()
            category_type = transaction_type_combo.currentData()
            categories = self.db.get_categories(category_type)
            
            for category in categories:
                category_combo.addItem(category['name'], category['id'])
                
                # Выбор текущей категории
                if category['id'] == transaction['category_id']:
                    category_combo.setCurrentText(category['name'])
        
        # Обновление списка категорий при изменении типа транзакции
        transaction_type_combo.currentIndexChanged.connect(update_categories)
        
        # Начальное заполнение
        update_categories()
        
        form_layout.addRow("Категория:", category_combo)
        
        # Дата
        date_edit = QDateEdit()
        date_edit.setDate(QDate.fromString(transaction['date'], "yyyy-MM-dd"))
        date_edit.setCalendarPopup(True)
        form_layout.addRow("Дата:", date_edit)
        
        # Описание
        description_edit = QTextEdit(transaction['description'])
        description_edit.setMaximumHeight(100)
        form_layout.addRow("Описание:", description_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(buttons)
        
        # Обработка результата диалога
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Получение данных из формы
                selected_type = transaction_type_combo.currentData()
                amount = float(amount_edit.text().replace(',', '.'))
                category_id = category_combo.currentData()
                date = date_edit.date().toString("yyyy-MM-dd")
                description = description_edit.toPlainText()
                
                # Проверка суммы
                if amount <= 0:
                    raise ValueError("Сумма должна быть положительным числом")
                
                # Обновление транзакции
                success = self.db.update_transaction(
                    transaction_id=transaction_id,
                    amount=amount,
                    category_id=category_id,
                    description=description,
                    date=date,
                    transaction_type=selected_type
                )
                
                if success:
                    # Обновление данных
                    self.load_data()
                    
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Транзакция успешно обновлена"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось обновить транзакцию"
                    )
            
            except ValueError as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при обновлении транзакции: {str(e)}"
                )
    
    def delete_selected_transaction(self):
        """Удаление выбранной транзакции"""
        # Получение выбранной строки
        selected_row = self.transactions_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите транзакцию для удаления"
            )
            return
        
        # Получение ID транзакции
        transaction_id = int(self.transactions_table.item(selected_row, 0).text())
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту транзакцию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Удаление транзакции
            success = self.db.delete_transaction(transaction_id)
            
            if success:
                # Обновление данных
                self.load_data()
                
                QMessageBox.information(
                    self,
                    "Успех",
                    "Транзакция успешно удалена"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Не удалось удалить транзакцию"
                )
    
    def show_add_category_dialog(self, category_type):
        """Показать диалог добавления категории"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Добавление категории {'расходов' if category_type == 'expense' else 'доходов'}")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Форма для ввода данных
        form_layout = QFormLayout()
        
        # Название категории
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Введите название категории")
        form_layout.addRow("Название:", name_edit)
        
        # Цвет категории
        color_edit = QLineEdit("#607D8B")  # Стандартный цвет
        form_layout.addRow("Цвет (HEX):", color_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(buttons)
        
        # Обработка результата диалога
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Получение данных из формы
                name = name_edit.text().strip()
                color = color_edit.text().strip()
                
                # Проверка названия
                if not name:
                    raise ValueError("Название категории не может быть пустым")
                
                # Добавление категории
                category_id = self.db.add_category(
                    name=name,
                    color=color,
                    category_type=category_type
                )
                
                if category_id:
                    # Обновление данных
                    self.load_categories()
                    
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Категория успешно добавлена"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось добавить категорию"
                    )
            
            except ValueError as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при добавлении категории: {str(e)}"
                )
    
    def edit_selected_category(self, category_type):
        """Редактирование выбранной категории"""
        # Определение таблицы в зависимости от типа категории
        table = self.expense_categories_table if category_type == "expense" else self.income_categories_table
        
        # Получение выбранной строки
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите категорию для редактирования"
            )
            return
        
        # Получение ID категории
        category_id = int(table.item(selected_row, 0).text())
        
        # Получение данных о категории
        category = self.db.get_category_by_id(category_id)
        if not category:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Категория не найдена"
            )
            return
        
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование категории")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Форма для ввода данных
        form_layout = QFormLayout()
        
        # Название категории
        name_edit = QLineEdit(category['name'])
        form_layout.addRow("Название:", name_edit)
        
        # Цвет категории
        color_edit = QLineEdit(category['color'])
        form_layout.addRow("Цвет (HEX):", color_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(buttons)
        
        # Обработка результата диалога
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Получение данных из формы
                name = name_edit.text().strip()
                color = color_edit.text().strip()
                
                # Проверка названия
                if not name:
                    raise ValueError("Название категории не может быть пустым")
                
                # Обновление категории
                success = self.db.update_category(
                    category_id=category_id,
                    name=name,
                    color=color
                )
                
                if success:
                    # Обновление данных
                    self.load_categories()
                    
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Категория успешно обновлена"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось обновить категорию"
                    )
            
            except ValueError as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при обновлении категории: {str(e)}"
                )
    
    def delete_selected_category(self, category_type):
        """Удаление выбранной категории"""
        # Определение таблицы в зависимости от типа категории
        table = self.expense_categories_table if category_type == "expense" else self.income_categories_table
        
        # Получение выбранной строки
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите категорию для удаления"
            )
            return
        
        # Получение ID категории
        category_id = int(table.item(selected_row, 0).text())
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту категорию? Транзакции, связанные с этой категорией, останутся, но будут без категории.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Удаление категории
            success = self.db.delete_category(category_id)
            
            if success:
                # Обновление данных
                self.load_categories()
                self.load_transactions()
                
                QMessageBox.information(
                    self,
                    "Успех",
                    "Категория успешно удалена"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Не удалось удалить категорию"
                )
    
    def show_report_dialog(self):
        """Показать диалог генерации отчета"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Генерация отчета")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Форма для ввода данных
        form_layout = QFormLayout()
        
        # Тип отчета
        report_type_combo = QComboBox()
        report_type_combo.addItem("Месячный отчет", "monthly")
        report_type_combo.addItem("Годовой отчет", "annual")
        report_type_combo.addItem("Произвольный период", "custom")
        
        form_layout.addRow("Тип отчета:", report_type_combo)
        
        # Контейнер для параметров отчета
        params_widget = QWidget()
        params_layout = QFormLayout(params_widget)
        
        # Виджеты для разных типов отчетов
        # Месячный отчет
        year_spin = QSpinBox()
        year_spin.setRange(2000, datetime.now().year)
        year_spin.setValue(datetime.now().year)
        
        month_combo = QComboBox()
        for i in range(1, 13):
            month_name = datetime(2023, i, 1).strftime('%B')
            month_combo.addItem(month_name, i)
        month_combo.setCurrentIndex(datetime.now().month - 1)
        
        # Годовой отчет
        annual_year_spin = QSpinBox()
        annual_year_spin.setRange(2000, datetime.now().year)
        annual_year_spin.setValue(datetime.now().year)
        
        # Произвольный период
        date_from = QDateEdit()
        date_from.setDate(QDate.currentDate().addMonths(-1))
        date_from.setCalendarPopup(True)
        
        date_to = QDateEdit()
        date_to.setDate(QDate.currentDate())
        date_to.setCalendarPopup(True)
        
        # Функция для обновления параметров отчета в зависимости от типа
        def update_report_params():
            # Очистка текущих параметров
            for i in reversed(range(params_layout.count())):
                if params_layout.itemAt(i).widget():
                    params_layout.itemAt(i).widget().setParent(None)
            
            report_type = report_type_combo.currentData()
            
            if report_type == "monthly":
                params_layout.addRow("Год:", year_spin)
                params_layout.addRow("Месяц:", month_combo)
            elif report_type == "annual":
                params_layout.addRow("Год:", annual_year_spin)
            elif report_type == "custom":
                params_layout.addRow("Начало периода:", date_from)
                params_layout.addRow("Конец периода:", date_to)
        
        # Обновление параметров при выборе типа отчета
        report_type_combo.currentIndexChanged.connect(update_report_params)
        
        # Инициализация параметров
        update_report_params()
        
        form_layout.addRow(params_widget)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(buttons)
        
        # Обработка результата диалога
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Получение всех транзакций
                all_transactions = self.db.get_all_transactions()
                
                report_type = report_type_combo.currentData()
                report = None
                
                if report_type == "monthly":
                    # Месячный отчет
                    selected_year = year_spin.value()
                    selected_month = month_combo.currentData()
                    
                    report = ReportGenerator.generate_monthly_report(
                        all_transactions, selected_year, selected_month
                    )
                
                elif report_type == "annual":
                    # Годовой отчет
                    selected_year = annual_year_spin.value()
                    
                    report = ReportGenerator.generate_annual_report(
                        all_transactions, selected_year
                    )
                
                elif report_type == "custom":
                    # Отчет за произвольный период
                    start_date = date_from.date().toString("yyyy-MM-dd")
                    end_date = date_to.date().toString("yyyy-MM-dd")
                    
                    report = ReportGenerator.generate_period_report(
                        all_transactions, start_date, end_date
                    )
                
                if report:
                    # Генерация текстового отчета
                    text_report = ReportGenerator.generate_text_report(report)
                    
                    # Показ диалога с отчетом и возможностью сохранения
                    self.show_report_text_dialog(text_report)
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось сгенерировать отчет"
                    )
            
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при генерации отчета: {str(e)}"
                )
    
    def show_report_text_dialog(self, report_text):
        """Показать диалог с текстом отчета"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Финансовый отчет")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Текстовое поле с отчетом
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(report_text)
        text_edit.setFont(QFont("Courier New", 10))
        
        layout.addWidget(text_edit)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить в файл")
        save_btn.clicked.connect(lambda: self.save_report_to_file(report_text))
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def save_report_to_file(self, report_text):
        """Сохранить отчет в файл"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчет",
            os.path.join(os.getcwd(), "finance_report.txt"),
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        
        if filename:
            try:
                # Сохранение отчета в файл
                file_path = ReportGenerator.save_report_to_file(report_text, filename)
                
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Отчет успешно сохранен в файл:\n{file_path}"
                )
            
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при сохранении отчета: {str(e)}"
                )
    
    def save_current_chart(self):
        """Сохранить текущий график"""
        # Получение текущего графика с вкладки аналитики
        chart_widget = None
        
        for i in range(self.chart_layout.count()):
            widget = self.chart_layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                chart_widget = widget
                break
        
        if not chart_widget:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "График не найден или не поддерживает сохранение"
            )
            return
        
        # Диалог выбора файла
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            os.path.join(os.getcwd(), "finance_chart.png"),
            "Изображения (*.png *.jpg *.pdf);;Все файлы (*.*)"
        )
        
        if filename:
            try:
                # Сохранение графика
                chart_widget.figure.savefig(filename, dpi=300, bbox_inches='tight')
                
                QMessageBox.information(
                    self,
                    "Успех",
                    f"График успешно сохранен в файл:\n{filename}"
                )
            
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при сохранении графика: {str(e)}"
                )
    
    def browse_db_path(self):
        """Выбор пути к файлу базы данных"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать файл базы данных",
            os.getcwd(),
            "База данных SQLite (*.db);;Все файлы (*.*)"
        )
        
        if filename:
            self.db_path_edit.setText(filename)
    
    def backup_database(self):
        """Создание резервной копии базы данных"""
        # Диалог выбора файла
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Создать резервную копию",
            os.path.join(os.getcwd(), f"finance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"),
            "База данных SQLite (*.db);;Все файлы (*.*)"
        )
        
        if filename:
            try:
                # Копирование файла базы данных
                import shutil
                shutil.copy2(self.db.db_path, filename)
                
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Резервная копия успешно создана в файл:\n{filename}"
                )
            
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Ошибка при создании резервной копии: {str(e)}"
                )
    
    def restore_database(self):
        """Восстановление базы данных из резервной копии"""
        # Диалог выбора файла
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать резервную копию",
            os.getcwd(),
            "База данных SQLite (*.db);;Все файлы (*.*)"
        )
        
        if filename:
            # Подтверждение восстановления
            reply = QMessageBox.warning(
                self,
                "Подтверждение",
                "Восстановление из резервной копии заменит текущую базу данных. Все несохраненные данные будут потеряны.\n\nПродолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Копирование файла резервной копии
                    import shutil
                    shutil.copy2(filename, self.db.db_path)
                    
                    # Переинициализация базы данных
                    self.db = Database(self.db.db_path)
                    
                    # Обновление данных
                    self.load_data()
                    
                    QMessageBox.information(
                        self,
                        "Успех",
                        "База данных успешно восстановлена из резервной копии"
                    )
                
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        f"Ошибка при восстановлении базы данных: {str(e)}"
                    )


def main():
    """Основная функция программы"""
    app = QApplication(sys.argv)
    
    # Установка стилей
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())