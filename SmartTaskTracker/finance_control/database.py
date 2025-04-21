#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для работы с базой данных SQLite
"""

import os
import sqlite3
from datetime import datetime


class Database:
    """Класс для работы с базой данных SQLite"""
    
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
        # Проверка наличия категорий расходов
        cursor.execute("SELECT COUNT(*) as count FROM categories WHERE type = 'expense'")
        if cursor.fetchone()['count'] == 0:
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
            conn.commit()
        
        # Проверка наличия категорий доходов
        cursor.execute("SELECT COUNT(*) as count FROM categories WHERE type = 'income'")
        if cursor.fetchone()['count'] == 0:
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
    
    def add_category(self, name, color, category_type):
        """
        Добавить новую категорию
        
        Args:
            name (str): Название категории
            color (str): Цвет категории в формате HEX (#RRGGBB)
            category_type (str): Тип категории ('income' или 'expense')
            
        Returns:
            int: ID добавленной категории или None в случае ошибки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверка на существование категории с таким именем и типом
            cursor.execute(
                "SELECT id FROM categories WHERE name = ? AND type = ?",
                (name, category_type)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Категория уже существует
                return existing['id']
            
            # Добавление новой категории
            cursor.execute(
                "INSERT INTO categories (name, color, type) VALUES (?, ?, ?)",
                (name, color, category_type)
            )
            conn.commit()
            
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении категории: {e}")
            return None
        finally:
            conn.close()
    
    def update_category(self, category_id, name, color):
        """
        Обновить категорию
        
        Args:
            category_id (int): ID категории
            name (str): Новое название категории
            color (str): Новый цвет категории в формате HEX (#RRGGBB)
            
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE categories SET name = ?, color = ? WHERE id = ?",
                (name, color, category_id)
            )
            conn.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении категории: {e}")
            return False
        finally:
            conn.close()
    
    def delete_category(self, category_id):
        """
        Удалить категорию
        
        Args:
            category_id (int): ID категории
            
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Сначала обновляем все транзакции с этой категорией, устанавливая категорию NULL
            cursor.execute(
                "UPDATE transactions SET category_id = NULL WHERE category_id = ?",
                (category_id,)
            )
            
            # Затем удаляем саму категорию
            cursor.execute(
                "DELETE FROM categories WHERE id = ?",
                (category_id,)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении категории: {e}")
            return False
        finally:
            conn.close()
    
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
    
    def get_category_by_id(self, category_id):
        """
        Получить категорию по ID
        
        Args:
            category_id (int): ID категории
            
        Returns:
            dict: Данные категории или None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM categories WHERE id = ?",
                (category_id,)
            )
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'name': row['name'],
                    'color': row['color'],
                    'type': row['type']
                }
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении категории: {e}")
            return None
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
                date = datetime.now()
            
            # Если дата представлена в виде строки, преобразуем ее в объект datetime
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    date = datetime.now()
            
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
    
    def update_transaction(self, transaction_id, amount, category_id, description, date, transaction_type):
        """
        Обновить транзакцию
        
        Args:
            transaction_id (int): ID транзакции
            amount (float): Сумма транзакции
            category_id (int): ID категории
            description (str): Описание транзакции
            date (datetime или str): Дата транзакции
            transaction_type (str): Тип транзакции ('income' или 'expense')
            
        Returns:
            bool: True в случае успеха, False в случае ошибки
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
            
            # Если дата представлена в виде строки, проверим ее формат
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Неверный формат даты. Используйте формат ГГГГ-ММ-ДД")
            
            # Форматирование даты в строку ISO
            date_str = date.strftime("%Y-%m-%d")
            
            cursor.execute(
                """
                UPDATE transactions 
                SET amount = ?, category_id = ?, date = ?, description = ?, type = ? 
                WHERE id = ?
                """,
                (amount, category_id, date_str, description, transaction_type, transaction_id)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except (sqlite3.Error, ValueError) as e:
            print(f"Ошибка при обновлении транзакции: {e}")
            return False
        finally:
            conn.close()
    
    def delete_transaction(self, transaction_id):
        """
        Удалить транзакцию
        
        Args:
            transaction_id (int): ID транзакции
            
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM transactions WHERE id = ?",
                (transaction_id,)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении транзакции: {e}")
            return False
        finally:
            conn.close()
    
    def get_transaction_by_id(self, transaction_id):
        """
        Получить транзакцию по ID
        
        Args:
            transaction_id (int): ID транзакции
            
        Returns:
            dict: Данные транзакции или None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT t.*, c.name as category_name, c.color as category_color 
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?
                """,
                (transaction_id,)
            )
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'amount': row['amount'],
                    'category_id': row['category_id'],
                    'category_name': row['category_name'],
                    'category_color': row['category_color'],
                    'date': row['date'],
                    'description': row['description'],
                    'type': row['type']
                }
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении транзакции: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_transactions(self):
        """
        Получить все транзакции
        
        Returns:
            list: Список всех транзакций
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT t.*, c.name as category_name, c.color as category_color 
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                ORDER BY t.date DESC
                """
            )
            
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
    
    def get_transactions_by_type(self, transaction_type):
        """
        Получить транзакции по типу
        
        Args:
            transaction_type (str): Тип транзакции ('income' или 'expense')
            
        Returns:
            list: Список транзакций указанного типа
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT t.*, c.name as category_name, c.color as category_color 
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.type = ?
                ORDER BY t.date DESC
                """,
                (transaction_type,)
            )
            
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
            print(f"Ошибка при получении транзакций по типу: {e}")
            return []
        finally:
            conn.close()
    
    def get_transactions_by_date_range(self, start_date, end_date=None):
        """
        Получить транзакции за период
        
        Args:
            start_date (datetime или str): Начало периода
            end_date (datetime или str, optional): Конец периода
            
        Returns:
            list: Список транзакций за указанный период
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Преобразование дат в строки, если они переданы как объекты datetime
            if isinstance(start_date, datetime):
                start_date = start_date.strftime("%Y-%m-%d")
            
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            elif isinstance(end_date, datetime):
                end_date = end_date.strftime("%Y-%m-%d")
            
            cursor.execute(
                """
                SELECT t.*, c.name as category_name, c.color as category_color 
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.date BETWEEN ? AND ?
                ORDER BY t.date DESC
                """,
                (start_date, end_date)
            )
            
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
            print(f"Ошибка при получении транзакций за период: {e}")
            return []
        finally:
            conn.close()
    
    def get_transactions_by_category(self, category_id):
        """
        Получить транзакции по категории
        
        Args:
            category_id (int): ID категории
            
        Returns:
            list: Список транзакций по указанной категории
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT t.*, c.name as category_name, c.color as category_color 
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.category_id = ?
                ORDER BY t.date DESC
                """,
                (category_id,)
            )
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'id': row['id'],
                    'amount': row['amount'],
                    'category_id': row['category_id'],
                    'category_name': row['category_name'],
                    'category_color': row['category_color'],
                    'date': row['date'],
                    'description': row['description'],
                    'type': row['type']
                })
            
            return transactions
        except sqlite3.Error as e:
            print(f"Ошибка при получении транзакций по категории: {e}")
            return []
        finally:
            conn.close()
    
    def get_expenses_by_category(self, start_date=None, end_date=None):
        """
        Получить сумму расходов по категориям за определенный период
        
        Args:
            start_date (datetime или str, optional): Начало периода
            end_date (datetime или str, optional): Конец периода
            
        Returns:
            list: Список с суммами расходов по категориям
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Подготовка дат для запроса
            date_condition = ""
            params = []
            
            if start_date or end_date:
                date_condition = " AND "
                
                if start_date and end_date:
                    if isinstance(start_date, datetime):
                        start_date = start_date.strftime("%Y-%m-%d")
                    if isinstance(end_date, datetime):
                        end_date = end_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                elif start_date:
                    if isinstance(start_date, datetime):
                        start_date = start_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date >= ?"
                    params.append(start_date)
                elif end_date:
                    if isinstance(end_date, datetime):
                        end_date = end_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date <= ?"
                    params.append(end_date)
            
            # Запрос на суммы расходов по категориям
            query = f"""
            SELECT 
                COALESCE(c.id, 0) as category_id, 
                COALESCE(c.name, 'Без категории') as category_name,
                COALESCE(c.color, '#607D8B') as category_color,
                SUM(t.amount) as total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense'{date_condition}
            GROUP BY COALESCE(c.id, 0), COALESCE(c.name, 'Без категории'), COALESCE(c.color, '#607D8B')
            ORDER BY total DESC
            """
            
            cursor.execute(query, params)
            
            result = []
            for row in cursor.fetchall():
                result.append({
                    'category_id': row['category_id'],
                    'category_name': row['category_name'],
                    'category_color': row['category_color'],
                    'total': row['total']
                })
            
            return result
        except sqlite3.Error as e:
            print(f"Ошибка при получении расходов по категориям: {e}")
            return []
        finally:
            conn.close()
    
    def get_income_by_category(self, start_date=None, end_date=None):
        """
        Получить сумму доходов по категориям за определенный период
        
        Args:
            start_date (datetime или str, optional): Начало периода
            end_date (datetime или str, optional): Конец периода
            
        Returns:
            list: Список с суммами доходов по категориям
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Подготовка дат для запроса
            date_condition = ""
            params = []
            
            if start_date or end_date:
                date_condition = " AND "
                
                if start_date and end_date:
                    if isinstance(start_date, datetime):
                        start_date = start_date.strftime("%Y-%m-%d")
                    if isinstance(end_date, datetime):
                        end_date = end_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                elif start_date:
                    if isinstance(start_date, datetime):
                        start_date = start_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date >= ?"
                    params.append(start_date)
                elif end_date:
                    if isinstance(end_date, datetime):
                        end_date = end_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date <= ?"
                    params.append(end_date)
            
            # Запрос на суммы доходов по категориям
            query = f"""
            SELECT 
                COALESCE(c.id, 0) as category_id, 
                COALESCE(c.name, 'Без категории') as category_name,
                COALESCE(c.color, '#607D8B') as category_color,
                SUM(t.amount) as total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'income'{date_condition}
            GROUP BY COALESCE(c.id, 0), COALESCE(c.name, 'Без категории'), COALESCE(c.color, '#607D8B')
            ORDER BY total DESC
            """
            
            cursor.execute(query, params)
            
            result = []
            for row in cursor.fetchall():
                result.append({
                    'category_id': row['category_id'],
                    'category_name': row['category_name'],
                    'category_color': row['category_color'],
                    'total': row['total']
                })
            
            return result
        except sqlite3.Error as e:
            print(f"Ошибка при получении доходов по категориям: {e}")
            return []
        finally:
            conn.close()
    
    def get_transactions_by_month(self, start_date=None, end_date=None):
        """
        Получить суммы транзакций по месяцам
        
        Args:
            start_date (datetime или str, optional): Начало периода
            end_date (datetime или str, optional): Конец периода
            
        Returns:
            list: Список с суммами транзакций по месяцам
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Подготовка дат для запроса
            date_condition = ""
            params = []
            
            if start_date or end_date:
                date_condition = " WHERE "
                
                if start_date and end_date:
                    if isinstance(start_date, datetime):
                        start_date = start_date.strftime("%Y-%m-%d")
                    if isinstance(end_date, datetime):
                        end_date = end_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                elif start_date:
                    if isinstance(start_date, datetime):
                        start_date = start_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date >= ?"
                    params.append(start_date)
                elif end_date:
                    if isinstance(end_date, datetime):
                        end_date = end_date.strftime("%Y-%m-%d")
                    
                    date_condition += "t.date <= ?"
                    params.append(end_date)
            
            # Запрос на суммы по месяцам
            query = f"""
            SELECT 
                strftime('%Y-%m', t.date) as month,
                t.type,
                SUM(t.amount) as total
            FROM transactions t
            {date_condition}
            GROUP BY strftime('%Y-%m', t.date), t.type
            ORDER BY month ASC
            """
            
            cursor.execute(query, params)
            
            # Преобразуем результаты в словарь с данными по месяцам
            monthly_data = {}
            for row in cursor.fetchall():
                month = row['month']
                transaction_type = row['type']
                total = row['total']
                
                if month not in monthly_data:
                    monthly_data[month] = {
                        'month': month,
                        'income': 0,
                        'expense': 0,
                        'balance': 0
                    }
                
                monthly_data[month][transaction_type] = total
                
                # Обновляем баланс
                balance = monthly_data[month]['income'] - monthly_data[month]['expense']
                monthly_data[month]['balance'] = balance
            
            # Преобразуем словарь в список и сортируем по месяцам
            result = list(monthly_data.values())
            result.sort(key=lambda x: x['month'])
            
            return result
        except sqlite3.Error as e:
            print(f"Ошибка при получении транзакций по месяцам: {e}")
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