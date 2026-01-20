#!/usr/bin/env python3
"""Диагностика проблемы с уведомлениями."""

import sys
import os
import json
from datetime import datetime, timedelta
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_system():
    print("🔧 ДИАГНОСТИКА СИСТЕМЫ УВЕДОМЛЕНИЙ")
    print("=" * 60)
    
    # 1. Проверка базовых импортов
    print("\n1. 📦 Проверка импортов...")
    try:
        from config import BOT_TOKEN, AUTHORIZED_USER_IDS, DATA_FILE
        print(f"   ✅ config: BOT_TOKEN={'установлен' if BOT_TOKEN else 'НЕТ'}")
        print(f"   ✅ config: Пользователи: {AUTHORIZED_USER_IDS}")
        print(f"   ✅ config: Файл данных: {DATA_FILE}")
    except Exception as e:
        print(f"   ❌ config: {e}")
        return False
    
    # 2. Проверка файла данных
    print("\n2. 📁 Проверка файла данных...")
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   ✅ Файл существует: {DATA_FILE}")
            print(f"   ✅ Записей: {len(data)}")
            
            # Показываем первые 3 записи
            if data:
                print(f"   📊 Примеры записей:")
                for i, item in enumerate(data[:3], 1):
                    print(f"     {i}. {item.get('name', 'N/A')} - {item.get('birthday', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Ошибка чтения файла: {e}")
            return False
    else:
        print(f"   ❌ Файл не существует: {DATA_FILE}")
        print(f"   💡 Решение: отправьте Excel-файл боту")
        return False
    
    # 3. Проверка утилит
    print("\n3. ⚙️ Проверка утилит...")
    try:
        from utils import get_today_date, get_tomorrow_date, load_birthdays
        today = get_today_date()
        tomorrow = get_tomorrow_date()
        print(f"   ✅ utils: Сегодня - {today}")
        print(f"   ✅ utils: Завтра - {tomorrow}")
        
        # Проверка загрузки данных
        birthdays = load_birthdays(DATA_FILE)
        print(f"   ✅ utils: Данные загружены ({len(birthdays)} записей)")
    except Exception as e:
        print(f"   ❌ utils: {e}")
        return False
    
    # 4. Проверка планировщика
    print("\n4. ⏰ Проверка планировщика...")
    try:
        from scheduler import send_birthday_notifications
        print("   ✅ Функция send_birthday_notifications найдена")
        
        # Тестовая проверка данных
        birthdays = load_birthdays(DATA_FILE)
        today = get_today_date()
        tomorrow = get_tomorrow_date()
        
        today_birthdays = [b['name'] for b in birthdays if b['birthday'] == today]
        tomorrow_birthdays = [b['name'] for b in birthdays if b['birthday'] == tomorrow]
        
        print(f"   📅 Совпадений на сегодня ({today}): {len(today_birthdays)}")
        print(f"   📅 Совпадений на завтра ({tomorrow}): {len(tomorrow_birthdays)}")
        
        if today_birthdays:
            print(f"   🎂 Сегодня: {', '.join(today_birthdays)}")
        if tomorrow_birthdays:
            print(f"   📅 Завтра: {', '.join(tomorrow_birthdays)}")
        
    except Exception as e:
        print(f"   ❌ scheduler: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True  # Пропускаем проверку Telegram API для синхронной проверки

async def check_telegram_api():
    """Асинхронная проверка Telegram API."""
    print("\n5. 🤖 Проверка Telegram API (асинхронно)...")
    try:
        from telegram import Bot
        from config import BOT_TOKEN
        
        if not BOT_TOKEN or BOT_TOKEN == 'ваш_токен_бота_от_BotFather':
            print(f"   ❌ BOT_TOKEN не установлен или имеет значение по умолчанию")
            return False
        
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        print(f"   ✅ Бот: @{me.username} ({me.first_name})")
        print(f"   ✅ Бот ID: {me.id}")
        return True
        
    except Exception as e:
        print(f"   ❌ Telegram API: {e}")
        print(f"   💡 Проверьте BOT_TOKEN в .env файле")
        return False

def test_notification():
    """Тест отправки уведомления."""
    print("\n" + "=" * 60)
    print("🚀 ТЕСТ ОТПРАВКИ УВЕДОМЛЕНИЯ")
    print("=" * 60)
    
    try:
        from scheduler import send_birthday_notifications
        from config import AUTHORIZED_USER_IDS
        
        print("🔄 Запуск функции отправки уведомлений...")
        
        # Мокаем отправку для теста
        import scheduler
        original_send = scheduler.Bot.send_message
        sent_messages = []
        
        def mock_send_message(chat_id, text, **kwargs):
            sent_messages.append((chat_id, text))
            print(f"\n📨 МОК-ОТПРАВКА пользователю {chat_id}:")
            print("-" * 40)
            print(text)
            print("-" * 40)
            return True
        
        scheduler.Bot.send_message = mock_send_message
        
        # Запускаем
        send_birthday_notifications()
        
        # Восстанавливаем
        scheduler.Bot.send_message = original_send
        
        if sent_messages:
            print(f"\n✅ Уведомления сгенерированы: {len(sent_messages)}")
            for chat_id, text in sent_messages:
                print(f"   👤 Пользователь {chat_id}: {len(text)} символов")
        else:
            print("\nℹ️ Уведомлений не было (нет дней рождения на сегодня/завтра)")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

async def manual_notification():
    """Ручная отправка тестового уведомления."""
    print("\n" + "=" * 60)
    print("👨‍💻 РУЧНАЯ ОТПРАВКА УВЕДОМЛЕНИЯ")
    print("=" * 60)
    
    try:
        from telegram import Bot
        from config import BOT_TOKEN, AUTHORIZED_USER_IDS
        
        if not AUTHORIZED_USER_IDS:
            print("❌ Нет авторизованных пользователей")
            return
        
        bot = Bot(token=BOT_TOKEN)
        
        test_message = (
            "🔔 **ТЕСТОВОЕ УВЕДОМЛЕНИЕ**\n\n"
            f"Время отправки: {datetime.now().strftime('%H:%M:%S')}\n"
            f"Бот работает! ✅\n\n"
            "Если вы видите это сообщение, значит:\n"
            "1. 🤖 Бот активен\n"
            "2. 📨 Отправка сообщений работает\n"
            "3. 👤 Вы авторизованы\n\n"
            "🎉 Поздравления будут приходить каждый день в 09:00!"
        )
        
        successful = 0
        for user_id in AUTHORIZED_USER_IDS:
            try:
                await bot.send_message(chat_id=user_id, text=test_message, parse_mode='Markdown')
                print(f"✅ Тестовое сообщение отправлено пользователю {user_id}")
                successful += 1
            except Exception as e:
                print(f"❌ Ошибка отправки пользователю {user_id}: {e}")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

async def main_async():
    """Асинхронная основная функция."""
    if check_system():
        print("\n" + "=" * 60)
        print("✅ СИСТЕМА ПРОВЕРЕНА")
        print("=" * 60)
        
        # Проверяем Telegram API
        telegram_ok = await check_telegram_api()
        
        if telegram_ok:
            # Тест уведомлений
            test_notification()
            
            # Предлагаем ручную отправку
            print("\n" + "=" * 60)
            choice = input("Отправить тестовое уведомление? (y/n): ")
            if choice.lower() == 'y':
                await manual_notification()
        else:
            print("\n⚠️ Telegram API не работает. Проверьте токен и подключение.")
        
    else:
        print("\n" + "=" * 60)
        print("❌ ЕСТЬ ПРОБЛЕМЫ В СИСТЕМЕ")
        print("=" * 60)

def main():
    """Синхронная точка входа."""
    # Запускаем асинхронную функцию
    if hasattr(asyncio, 'run'):
        asyncio.run(main_async())
    else:
        # Для старых версий Python
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_async())

if __name__ == '__main__':
    main()
