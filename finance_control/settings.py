#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль настроек приложения
"""

import os
import json


class Settings:
    """Класс для управления настройками приложения"""
    
    DEFAULT_SETTINGS = {
        "database": {
            "path": "finance.db"
        },
        "interface": {
            "theme": "Fusion",
            "language": "ru_RU"
        },
        "analytics": {
            "default_period": "month"
        }
    }
    
    def __init__(self, settings_file="settings.json"):
        """
        Инициализация настроек
        
        Args:
            settings_file (str): Путь к файлу настроек
        """
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """
        Загрузка настроек из файла
        
        Returns:
            dict: Настройки приложения
        """
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка при загрузке настроек: {e}")
                return self.DEFAULT_SETTINGS.copy()
        else:
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """
        Сохранение настроек в файл
        
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")
            return False
    
    def get(self, section, key, default=None):
        """
        Получение значения настройки
        
        Args:
            section (str): Раздел настроек
            key (str): Ключ настройки
            default: Значение по умолчанию, если настройка не найдена
            
        Returns:
            any: Значение настройки или значение по умолчанию
        """
        return self.settings.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """
        Установка значения настройки
        
        Args:
            section (str): Раздел настроек
            key (str): Ключ настройки
            value: Новое значение настройки
            
        Returns:
            bool: True в случае успеха
        """
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
        return True
    
    def reset_to_defaults(self):
        """
        Сброс настроек к значениям по умолчанию
        
        Returns:
            bool: True в случае успеха
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save_settings()