#!/usr/bin/env python3
"""Тест генератора поздравлений."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from greetings_generator import generate_greeting, generate_collective_greeting

def test_generator():
    print("=" * 60)
    print("🧪 ТЕСТ ГЕНЕРАТОРА ПОЗДРАВЛЕНИЙ")
    print("=" * 60)
    
    # Тестовые имена
    test_names = ["Анна", "Иван", "Мария Петровна", "Александр", "Екатерина"]
    
    print("\n🎭 Тест индивидуальных поздравлений:")
    print("-" * 40)
    
    for name in test_names:
        print(f"\n📝 Для '{name}':")
        for i in range(2):  # 2 варианта для каждого имени
            greeting = generate_greeting(name)
            print(f"  Вариант {i+1}: {greeting[:80]}...")
    
    print("\n" + "=" * 60)
    print("👥 Тест коллективных поздравлений:")
    print("-" * 40)
    
    # Тест коллективных
    for i in range(3):
        names = test_names[:i+2]  # 2, 3, 4 имени
        collective = generate_collective_greeting(names)
        print(f"\nДля {len(names)} человек ({', '.join(names)}):")
        print(f"  {collective[:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)

if __name__ == "__main__":
    test_generator()
