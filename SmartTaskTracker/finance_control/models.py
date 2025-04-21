#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль с моделями данных
"""

from datetime import datetime


class Transaction:
    """Модель транзакции (доход или расход)"""
    
    def __init__(self, amount, category_id=None, description="", 
                 transaction_type="expense", date=None, transaction_id=None):
        """
        Инициализация транзакции
        
        Args:
            amount (float): Сумма транзакции
            category_id (int, optional): ID категории
            description (str, optional): Описание транзакции
            transaction_type (str, optional): Тип транзакции ('income' или 'expense')
            date (datetime, optional): Дата транзакции
            transaction_id (int, optional): ID транзакции в базе данных
        """
        self.id = transaction_id
        self.amount = float(amount)
        self.category_id = category_id
        self.description = description
        self.type = transaction_type
        
        # Если дата не указана, используем текущую
        if date is None:
            self.date = datetime.now()
        elif isinstance(date, str):
            try:
                self.date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                self.date = datetime.now()
        else:
            self.date = date
        
        # Дополнительные атрибуты для хранения информации о категории
        self.category_name = None
        self.category_color = None
    
    @classmethod
    def from_dict(cls, data):
        """
        Создать объект транзакции из словаря
        
        Args:
            data (dict): Словарь с данными транзакции
            
        Returns:
            Transaction: Объект транзакции
        """
        transaction = cls(
            amount=data['amount'],
            category_id=data.get('category_id'),
            description=data.get('description', ''),
            transaction_type=data.get('type', 'expense'),
            date=data.get('date'),
            transaction_id=data.get('id')
        )
        
        # Добавляем информацию о категории, если она есть
        transaction.category_name = data.get('category_name')
        transaction.category_color = data.get('category_color')
        
        return transaction
    
    def to_dict(self):
        """
        Преобразовать объект транзакции в словарь
        
        Returns:
            dict: Словарь с данными транзакции
        """
        return {
            'id': self.id,
            'amount': self.amount,
            'category_id': self.category_id,
            'category_name': self.category_name,
            'category_color': self.category_color,
            'description': self.description,
            'type': self.type,
            'date': self.date.strftime("%Y-%m-%d")
        }
    
    def __str__(self):
        """
        Строковое представление транзакции
        
        Returns:
            str: Строка с информацией о транзакции
        """
        transaction_type = "Доход" if self.type == 'income' else "Расход"
        category = f" - {self.category_name}" if self.category_name else ""
        return f"{transaction_type}: {self.amount:.2f} руб.{category} ({self.date.strftime('%Y-%m-%d')})"


class Category:
    """Модель категории транзакций"""
    
    def __init__(self, name, color="#607D8B", category_type="expense", category_id=None):
        """
        Инициализация категории
        
        Args:
            name (str): Название категории
            color (str, optional): Цвет категории в формате HEX (#RRGGBB)
            category_type (str, optional): Тип категории ('income' или 'expense')
            category_id (int, optional): ID категории в базе данных
        """
        self.id = category_id
        self.name = name
        self.color = color
        self.type = category_type
    
    @classmethod
    def from_dict(cls, data):
        """
        Создать объект категории из словаря
        
        Args:
            data (dict): Словарь с данными категории
            
        Returns:
            Category: Объект категории
        """
        return cls(
            name=data['name'],
            color=data.get('color', "#607D8B"),
            category_type=data.get('type', 'expense'),
            category_id=data.get('id')
        )
    
    def to_dict(self):
        """
        Преобразовать объект категории в словарь
        
        Returns:
            dict: Словарь с данными категории
        """
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'type': self.type
        }
    
    def __str__(self):
        """
        Строковое представление категории
        
        Returns:
            str: Строка с информацией о категории
        """
        category_type = "Доход" if self.type == 'income' else "Расход"
        return f"{self.name} ({category_type})"