#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FinanceControl - Простая CLI версия без зависимостей от PyQt6
Командная строка для базового управления финансовыми данными
"""

import os
import sys
import datetime
import sqlite3
import json


class SimpleDatabase:
    """Упрощенный класс для работы с базой данных SQLite"""
    
    def __init__(self, db_path='finance.db'):
        """
        Инициализация базы данных
        
        Args:
            db_path (str): Путь к файлу базы данных
        """
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """
        Получить соединение с базой данных
        
        Returns:
            sqlite3.Connection: Объект соединения с базой данных
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Инициализировать базу данных и создать таблицы, если их нет"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Создание таблицы категорий
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            type TEXT NOT NULL
        )
        ''')
        
        # Создание таблицы транзакций
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL,
            category_id INTEGER,
            date TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        conn.commit()
        
        # Добавление стандартных категорий, если их нет
        self._create_default_categories(cursor, conn)
        
        conn.close()
    
    def _create_default_categories(self, cursor, conn):
        """
        Создать стандартные категории, если их нет
        
        Args:
            cursor (sqlite3.Cursor): Курсор БД
            conn (sqlite3.Connection): Соединение с БД
        """
        # Проверяем, есть ли таблица и категории
        try:
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            category_count = cursor.fetchone()['count']
            
            if category_count == 0:
                # Добавление стандартных категорий расходов
                expense_categories = [
                    ("Продукты", "#4CAF50", "expense"),  # Зеленый
                    ("Транспорт", "#2196F3", "expense"),  # Синий
                    ("Жилье", "#FFC107", "expense"),      # Желтый
                    ("Развлечения", "#9C27B0", "expense"), # Фиолетовый
                    ("Здоровье", "#F44336", "expense"),   # Красный
                    ("Одежда", "#FF9800", "expense"),     # Оранжевый
                    ("Образование", "#795548", "expense"), # Коричневый
                    ("Прочее", "#607D8B", "expense")      # Серо-синий
                ]
                
                cursor.executemany(
                    "INSERT INTO categories (name, color, type) VALUES (?, ?, ?)",
                    expense_categories
                )
                
                # Добавление стандартных категорий доходов
                income_categories = [
                    ("Зарплата", "#4CAF50", "income"),     # Зеленый
                    ("Фриланс", "#2196F3", "income"),      # Синий
                    ("Инвестиции", "#FFC107", "income"),   # Желтый
                    ("Подарки", "#9C27B0", "income"),      # Фиолетовый
                    ("Прочее", "#607D8B", "income")        # Серо-синий
                ]
                
                cursor.executemany(
                    "INSERT INTO categories (name, color, type) VALUES (?, ?, ?)",
                    income_categories
                )
                
                conn.commit()
        except sqlite3.Error:
            # Возможно, таблица еще не создана или структура изменилась
            pass
    
    def get_categories(self, category_type=None):
        """
        Получить список категорий
        
        Args:
            category_type (str, optional): Тип категории ('income', 'expense' или None для всех)
            
        Returns:
            list: Список категорий
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if category_type:
                cursor.execute(
                    "SELECT * FROM categories WHERE type = ? ORDER BY name",
                    (category_type,)
                )
            else:
                cursor.execute("SELECT * FROM categories ORDER BY type, name")
            
            # Преобразование в список словарей
            categories = []
            for row in cursor.fetchall():
                categories.append({
                    'id': row['id'],
                    'name': row['name'],
                    'color': row['color'],
                    'type': row['type']
                })
            
            return categories
        except sqlite3.Error as e:
            print(f"Ошибка при получении категорий: {e}")
            return []
        finally:
            conn.close()
    
    def add_transaction(self, amount, category_id, description="", transaction_type="expense", date=None):
        """
        Добавить новую транзакцию
        
        Args:
            amount (float): Сумма транзакции
            category_id (int): ID категории
            description (str, optional): Описание транзакции
            transaction_type (str, optional): Тип транзакции ('income' или 'expense')
            date (datetime, optional): Дата транзакции
            
        Returns:
            int: ID добавленной транзакции или None в случае ошибки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверка типа транзакции
            if transaction_type not in ['income', 'expense']:
                raise ValueError("Неверный тип транзакции. Используйте 'income' или 'expense'")
            
            # Проверка суммы
            if amount <= 0:
                raise ValueError("Сумма транзакции должна быть положительным числом")
            
            # Подготовка даты
            if date is None:
                date = datetime.datetime.now()
            
            # Если дата представлена в виде строки, преобразуем ее в объект datetime
            if isinstance(date, str):
                try:
                    date = datetime.datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    date = datetime.datetime.now()
            
            # Форматирование даты в строку ISO
            date_str = date.strftime("%Y-%m-%d")
            
            cursor.execute(
                "INSERT INTO transactions (amount, category_id, date, description, type) VALUES (?, ?, ?, ?, ?)",
                (amount, category_id, date_str, description, transaction_type)
            )
            
            conn.commit()
            return cursor.lastrowid
        except (sqlite3.Error, ValueError) as e:
            print(f"Ошибка при добавлении транзакции: {e}")
            return None
        finally:
            conn.close()
    
    def get_transactions(self, transaction_type=None, start_date=None, end_date=None):
        """
        Получить транзакции с опциональной фильтрацией
        
        Args:
            transaction_type (str, optional): Тип транзакции ('income', 'expense' или None для всех)
            start_date (str, optional): Начальная дата в формате YYYY-MM-DD
            end_date (str, optional): Конечная дата в формате YYYY-MM-DD
            
        Returns:
            list: Список транзакций
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Создание базового запроса
            query = """
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            """
            
            conditions = []
            params = []
            
            # Добавление фильтра по типу
            if transaction_type:
                conditions.append("t.type = ?")
                params.append(transaction_type)
            
            # Добавление фильтра по датам
            if start_date:
                conditions.append("t.date >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("t.date <= ?")
                params.append(end_date)
            
            # Формирование полного запроса
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY t.date DESC"
            
            cursor.execute(query, params)
            
            # Преобразование в список словарей
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'id': row['id'],
                    'amount': row['amount'],
                    'category_id': row['category_id'],
                    'category_name': row['category_name'] if row['category_name'] else "Без категории",
                    'category_color': row['category_color'] if row['category_color'] else "#607D8B",
                    'date': row['date'],
                    'description': row['description'],
                    'type': row['type']
                })
            
            return transactions
        except sqlite3.Error as e:
            print(f"Ошибка при получении транзакций: {e}")
            return []
        finally:
            conn.close()
    
    def get_balance(self):
        """
        Получить текущий баланс (доходы - расходы)
        
        Returns:
            float: Сумма баланса
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Получение суммы доходов
            cursor.execute(
                "SELECT SUM(amount) as total FROM transactions WHERE type = 'income'"
            )
            income_row = cursor.fetchone()
            total_income = income_row['total'] if income_row and income_row['total'] is not None else 0
            
            # Получение суммы расходов
            cursor.execute(
                "SELECT SUM(amount) as total FROM transactions WHERE type = 'expense'"
            )
            expense_row = cursor.fetchone()
            total_expense = expense_row['total'] if expense_row and expense_row['total'] is not None else 0
            
            # Вычисление баланса
            balance = total_income - total_expense
            
            return balance
        except sqlite3.Error as e:
            print(f"Ошибка при получении баланса: {e}")
            return 0
        finally:
            conn.close()


class SimpleFinanceControlCLI:
    """Упрощенный интерфейс командной строки для управления финансами"""
    
    def __init__(self):
        """Инициализация приложения"""
        self.db = SimpleDatabase()
        self.running = True
    
    def display_menu(self):
        """Отображение главного меню"""
        print("\n" + "=" * 50)
        print("FINANCE CONTROL - УПРАВЛЕНИЕ ЛИЧНЫМИ ФИНАНСАМИ")
        print("=" * 50)
        print("1. Добавить доход")
        print("2. Добавить расход")
        print("3. Просмотр транзакций")
        print("4. Просмотр текущего баланса")
        print("5. Просмотр категорий")
        print("0. Выход")
        print("-" * 50)
    
    def run(self):
        """Запуск приложения"""
        while self.running:
            self.display_menu()
            choice = input("Выберите пункт меню: ")
            
            try:
                if choice == "1":
                    self.add_transaction("income")
                elif choice == "2":
                    self.add_transaction("expense")
                elif choice == "3":
                    self.view_transactions()
                elif choice == "4":
                    self.show_balance()
                elif choice == "5":
                    self.view_categories()
                elif choice == "0":
                    self.running = False
                    print("Выход из программы...")
                else:
                    print("Неверный выбор. Попробуйте еще раз.")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
    
    def add_transaction(self, transaction_type):
        """
        Добавление транзакции
        
        Args:
            transaction_type (str): Тип транзакции ('income' или 'expense')
        """
        transaction_name = "доход" if transaction_type == "income" else "расход"
        print(f"\nДобавление: {transaction_name}")
        print("-" * 50)
        
        # Выбор категории
        categories = self.db.get_categories(transaction_type)
        print("Доступные категории:")
        for i, category in enumerate(categories):
            print(f"{i+1}. {category['name']}")
        
        category_choice = input("Выберите номер категории: ")
        try:
            idx = int(category_choice) - 1
            if idx < 0 or idx >= len(categories):
                print("Неверный выбор категории.")
                return
            category_id = categories[idx]['id']
        except (ValueError, IndexError):
            print("Неверный ввод.")
            return
        
        # Ввод суммы
        amount_str = input("Введите сумму: ")
        try:
            amount = float(amount_str.replace(',', '.'))
            if amount <= 0:
                print("Сумма должна быть положительным числом.")
                return
        except ValueError:
            print("Неверный формат суммы.")
            return
        
        # Ввод описания
        description = input("Введите описание (необязательно): ")
        
        # Ввод даты (по умолчанию - текущая)
        date_str = input("Введите дату в формате ГГГГ-ММ-ДД (пусто для текущей даты): ")
        if date_str:
            try:
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("Неверный формат даты. Используется текущая дата.")
                date = datetime.datetime.now()
        else:
            date = datetime.datetime.now()
        
        # Добавление транзакции
        transaction_id = self.db.add_transaction(
            amount=amount,
            category_id=category_id,
            description=description,
            transaction_type=transaction_type,
            date=date
        )
        
        if transaction_id:
            print(f"{transaction_name.capitalize()} успешно добавлен.")
        else:
            print(f"Ошибка при добавлении транзакции.")
    
    def view_transactions(self):
        """Просмотр транзакций с фильтрацией"""
        print("\nПросмотр транзакций")
        print("-" * 50)
        
        # Выбор типа транзакций
        print("Тип транзакций:")
        print("1. Все")
        print("2. Только доходы")
        print("3. Только расходы")
        
        type_choice = input("Выберите тип: ")
        transaction_type = None
        
        if type_choice == "2":
            transaction_type = "income"
        elif type_choice == "3":
            transaction_type = "expense"
        
        # Выбор периода
        print("\nПериод:")
        print("1. Все время")
        print("2. Текущий месяц")
        print("3. Предыдущий месяц")
        print("4. Текущий год")
        print("5. Произвольный период")
        
        period_choice = input("Выберите период: ")
        
        start_date = None
        end_date = None
        
        today = datetime.datetime.now()
        
        if period_choice == "2":  # Текущий месяц
            start_date = datetime.datetime(today.year, today.month, 1).strftime("%Y-%m-%d")
            if today.month == 12:
                end_date = datetime.datetime(today.year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                end_date = datetime.datetime(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
            end_date = end_date.strftime("%Y-%m-%d")
        
        elif period_choice == "3":  # Предыдущий месяц
            if today.month == 1:
                start_date = datetime.datetime(today.year - 1, 12, 1)
                end_date = datetime.datetime(today.year, 1, 1) - datetime.timedelta(days=1)
            else:
                start_date = datetime.datetime(today.year, today.month - 1, 1)
                end_date = datetime.datetime(today.year, today.month, 1) - datetime.timedelta(days=1)
            
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")
        
        elif period_choice == "4":  # Текущий год
            start_date = datetime.datetime(today.year, 1, 1).strftime("%Y-%m-%d")
            end_date = datetime.datetime(today.year, 12, 31).strftime("%Y-%m-%d")
        
        elif period_choice == "5":  # Произвольный период
            start_date_str = input("Введите начальную дату в формате ГГГГ-ММ-ДД: ")
            try:
                datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
                start_date = start_date_str
            except ValueError:
                print("Неверный формат даты.")
                return
            
            end_date_str = input("Введите конечную дату в формате ГГГГ-ММ-ДД (Enter для текущей даты): ")
            if end_date_str:
                try:
                    datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
                    end_date = end_date_str
                except ValueError:
                    print("Неверный формат даты.")
                    return
            else:
                end_date = today.strftime("%Y-%m-%d")
        
        # Получение и отображение транзакций
        transactions = self.db.get_transactions(transaction_type, start_date, end_date)
        
        if not transactions:
            print("\nТранзакции не найдены.")
            return
        
        print(f"\nНайдено транзакций: {len(transactions)}")
        print("-" * 89)
        print(f"{'ID':<5} {'Дата':<12} {'Тип':<10} {'Категория':<20} {'Сумма':<12} {'Описание':<30}")
        print("-" * 89)
        
        for t in transactions:
            type_text = "Доход" if t['type'] == 'income' else "Расход"
            print(f"{t['id']:<5} {t['date']:<12} {type_text:<10} {t['category_name']:<20} {t['amount']:<12.2f} {t['description']:<30}")
        
        print("-" * 89)
        
        # Суммы по типам
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        balance = total_income - total_expense
        
        print(f"Общий доход: {total_income:.2f} руб.")
        print(f"Общий расход: {total_expense:.2f} руб.")
        print(f"Баланс за период: {balance:.2f} руб.")
    
    def show_balance(self):
        """Отображение текущего баланса и статистики"""
        balance = self.db.get_balance()
        
        print("\nТекущий баланс")
        print("-" * 50)
        print(f"Баланс: {balance:.2f} руб.")
        
        # Получение всех транзакций
        transactions = self.db.get_transactions()
        
        # Суммы по типам
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        
        print(f"Общий доход: {total_income:.2f} руб.")
        print(f"Общий расход: {total_expense:.2f} руб.")
        
        # Расчет доходов и расходов за текущий месяц
        today = datetime.datetime.now()
        start_of_month = datetime.datetime(today.year, today.month, 1).strftime("%Y-%m-%d")
        end_of_month = today.strftime("%Y-%m-%d")
        
        monthly_transactions = self.db.get_transactions(None, start_of_month, end_of_month)
        monthly_income = sum(t['amount'] for t in monthly_transactions if t['type'] == 'income')
        monthly_expense = sum(t['amount'] for t in monthly_transactions if t['type'] == 'expense')
        
        print(f"\nДоход за текущий месяц: {monthly_income:.2f} руб.")
        print(f"Расход за текущий месяц: {monthly_expense:.2f} руб.")
        print(f"Баланс за текущий месяц: {monthly_income - monthly_expense:.2f} руб.")
    
    def view_categories(self):
        """Просмотр категорий"""
        print("\nКатегории")
        print("-" * 50)
        
        # Категории расходов
        expense_categories = self.db.get_categories("expense")
        
        print("Категории расходов:")
        print("-" * 30)
        
        if not expense_categories:
            print("Категории расходов не найдены.")
        else:
            for c in expense_categories:
                print(f"{c['id']:<5} {c['name']:<25} {c['color']}")
        
        # Категории доходов
        income_categories = self.db.get_categories("income")
        
        print("\nКатегории доходов:")
        print("-" * 30)
        
        if not income_categories:
            print("Категории доходов не найдены.")
        else:
            for c in income_categories:
                print(f"{c['id']:<5} {c['name']:<25} {c['color']}")


def main():
    """Основная функция программы"""
    app = SimpleFinanceControlCLI()
    app.run()


if __name__ == "__main__":
    main()