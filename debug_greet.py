#!/usr/bin/env python3
"""Отладка команды /greet."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Тестирование импортов...")

try:
    # Пробуем импортировать генератор
    from greetings_generator import generate_greeting, generate_collective_greeting
    print("✅ greetings_generator импортирован успешно")
    
    # Тест генерации
    test_name = "Анна"
    greeting = generate_greeting(test_name)
    print(f"✅ Генерация работает: {greeting[:50]}...")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Проверьте наличие файла greetings_generator.py")
    
except Exception as e:
    print(f"❌ Другая ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 Проверка структуры проекта:")
for file in os.listdir('.'):
    if file.endswith('.py'):
        print(f"  {file}")
