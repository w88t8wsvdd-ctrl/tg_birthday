#!/usr/bin/env python3
"""Диагностика проблемы с уведомлениями - исправленная версия."""

import sys
import os
import json
from datetime import datetime
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
        return True
    except Exception as e:
        print(f"   ❌ config: {e}")
        return False

def check_data():
    """Проверка файла данных."""
    print("\n2. 📁 Проверка файла данных...")
    try:
        from config import DATA_FILE
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   ✅ Файл существует: {DATA_FILE}")
            print(f"   ✅ Записей: {len(data)}")
            
            # Показываем первые 3 записи
            if data:
                print(f"   📊 Примеры записей:")
                for i, item in enumerate(data[:3], 1):
                    print(f"     {i}. {item.get('name', 'N/A')} - {item.get('birthday', 'N/A')}")
            return True
        else:
            print(f"   ❌ Файл не существует: {DATA_FILE}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка чтения файла: {e}")
        return False

def check_utils():
    """Проверка утилит."""
    print("\n3. ⚙️ Проверка утилит...")
    try:
        from utils import get_today_date, get_tomorrow_date, load_birthdays
        from config import DATA_FILE
        
        today = get_today_date()
        tomorrow = get_tomorrow_date()
        print(f"   ✅ utils: Сегодня - {today}")
        print(f"   ✅ utils: Завтра - {tomorrow}")
        
        # Проверка загрузки данных
        birthdays = load_birthdays(DATA_FILE)
        print(f"   ✅ utils: Данные загружены ({len(birthdays)} записей)")
        
        # Ищем совпадения
        today_birthdays = [b['name'] for b in birthdays if b['birthday'] == today]
        tomorrow_birthdays = [b['name'] for b in birthdays if b['birthday'] == tomorrow]
        
        print(f"   🎂 Совпадений на сегодня: {len(today_birthdays)}")
        print(f"   📅 Совпадений на завтра: {len(tomorrow_birthdays)}")
        
        if today_birthdays:
            print(f"   👤 Сегодня дни рождения у: {', '.join(today_birthdays)}")
        if tomorrow_birthdays:
            print(f"   👤 Завтра дни рождения у: {', '.join(tomorrow_birthdays)}")
            
        return True
    except Exception as e:
        print(f"   ❌ utils: {e}")
        return False

async def check_telegram_api():
    """Асинхронная проверка Telegram API."""
    print("\n5. 🤖 Проверка Telegram API...")
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
        return False

async def send_real_notification():
    """Реальная отправка тестового уведомления."""
    print("\n" + "=" * 60)
    print("🚀 РЕАЛЬНАЯ ОТПРАВКА ТЕСТОВОГО УВЕДОМЛЕНИЯ")
    print("=" * 60)
    
    try:
        from telegram import Bot
        from config import BOT_TOKEN, AUTHORIZED_USER_IDS
        
        if not AUTHORIZED_USER_IDS:
            print("❌ Нет авторизованных пользователей")
            return False
        
        bot = Bot(token=BOT_TOKEN)
        
        # Получаем данные для персонализированного сообщения
        from utils import get_today_date, load_birthdays
        from config import DATA_FILE
        
        today = get_today_date()
        birthdays = load_birthdays(DATA_FILE)
        today_birthdays = [b['name'] for b in birthdays if b['birthday'] == today]
        
        if today_birthdays:
            test_message = (
                f"🎂 **Тестовое уведомление**\n\n"
                f"Сегодня ({today}) день рождения у:\n"
                f"{', '.join(today_birthdays)}\n\n"
                f"✅ Система работает корректно!\n"
                f"🕐 Время проверки: {datetime.now().strftime('%H:%M:%S')}"
            )
        else:
            test_message = (
                f"🔔 **Тестовое уведомление**\n\n"
                f"Сегодня ({today}) дней рождения нет.\n"
                f"✅ Система работает корректно!\n"
                f"🕐 Время проверки: {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"Уведомления будут приходить каждый день в 09:00!"
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
        import traceback
        traceback.print_exc()
        return False

async def test_scheduler_function():
    """Тестирует функцию планировщика напрямую."""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ ФУНКЦИИ ПЛАНИРОВЩИКА")
    print("=" * 60)
    
    try:
        # Импортируем нужные функции
        from utils import get_today_date, get_tomorrow_date, load_birthdays, format_birthday_message
        from config import DATA_FILE, AUTHORIZED_USER_IDS
        from telegram import Bot
        from config import BOT_TOKEN
        
        # Загружаем данные
        birthdays = load_birthdays(DATA_FILE)
        today = get_today_date()
        tomorrow = get_tomorrow_date()
        
        print(f"📅 Сегодня: {today}, Завтра: {tomorrow}")
        print(f"📊 Всего записей: {len(birthdays)}")
        
        # Ищем совпадения
        today_birthdays = [b['name'] for b in birthdays if b['birthday'] == today]
        tomorrow_birthdays = [b['name'] for b in birthdays if b['birthday'] == tomorrow]
        
        print(f"🎂 На сегодня: {len(today_birthdays)}, На завтра: {len(tomorrow_birthdays)}")
        
        # Формируем сообщение
        messages = []
        
        if today_birthdays:
            today_message = format_birthday_message(today_birthdays, is_today=True)
            messages.append(today_message)
            print(f"\n📝 Сообщение на сегодня:\n{today_message[:100]}...")
        
        if tomorrow_birthdays:
            tomorrow_message = format_birthday_message(tomorrow_birthdays, is_today=False)
            messages.append(tomorrow_message)
            print(f"\n📝 Сообщение на завтра:\n{tomorrow_message[:100]}...")
        
        if messages:
            message_text = "\n\n".join(messages)
            print(f"\n📨 Итоговое сообщение ({len(message_text)} символов):")
            print("-" * 40)
            print(message_text[:200] + "..." if len(message_text) > 200 else message_text)
            print("-" * 40)
            
            # Проверяем, можем ли отправить
            print("\n🔍 Проверка возможности отправки...")
            bot = Bot(token=BOT_TOKEN)
            
            for user_id in AUTHORIZED_USER_IDS:
                try:
                    # Пробуем отправить короткое тестовое сообщение
                    await bot.send_message(
                        chat_id=user_id,
                        text="✅ Тест отправки сообщений работает!",
                        parse_mode='HTML'
                    )
                    print(f"   ✅ Пользователь {user_id}: отправка работает")
                except Exception as e:
                    print(f"   ❌ Пользователь {user_id}: {e}")
                    
            return True
        else:
            print("\nℹ️ Нет сообщений для отправки (нет дней рождения)")
            return True
            
    except Exception as e:
        print(f"\n❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main_async():
    """Асинхронная основная функция."""
    
    # Проверка системы
    if not check_system():
        print("\n❌ Проблема с конфигурацией")
        return
    
    if not check_data():
        print("\n❌ Проблема с данными")
        return
    
    if not check_utils():
        print("\n❌ Проблема с утилитами")
        return
    
    print("\n" + "=" * 60)
    print("✅ БАЗОВАЯ СИСТЕМА ПРОВЕРЕНА")
    print("=" * 60)
    
    # Проверяем Telegram API
    telegram_ok = await check_telegram_api()
    
    if not telegram_ok:
        print("\n⚠️ Telegram API не работает. Проверьте токен.")
        return
    
    # Тестируем функцию планировщика
    print("\n" + "=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ПОЛНОЙ ЦЕПОЧКИ")
    print("=" * 60)
    
    await test_scheduler_function()
    
    # Предлагаем отправить реальное уведомление
    print("\n" + "=" * 60)
    print("📨 ОТПРАВИТЬ РЕАЛЬНОЕ ТЕСТОВОЕ УВЕДОМЛЕНИЕ?")
    print("=" * 60)
    print("Это отправит настоящее сообщение всем пользователям.")
    
    try:
        # В неинтерактивном режиме (Railway) просто пропускаем
        print("\nДля отправки введите 'y', для пропуска - любую другую клавишу...")
        
        # Читаем из stdin если доступно
        import select
        if select.select([sys.stdin], [], [], 5)[0]:
            choice = sys.stdin.readline().strip().lower()
        else:
            print("\n⏰ Таймаут, пропускаем интерактивную часть...")
            choice = 'n'
            
        if choice == 'y':
            await send_real_notification()
        else:
            print("\n⚠️ Тестовая отправка пропущена.")
            
    except Exception as e:
        print(f"\n⚠️ Интерактивный режим недоступен: {e}")
        print("Пропускаем отправку...")
    
    print("\n" + "=" * 60)
    print("🎉 ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 60)
    print("\n📋 РЕКОМЕНДАЦИИ:")
    print("1. Если все тесты пройдены ✅ - система работает")
    print("2. Уведомления будут отправляться в 09:00 каждый день")
    print("3. Используйте команду /test в боте для проверки")
    print("4. Проверьте логи планировщика")

def main():
    """Синхронная точка входа."""
    try:
        # Запускаем асинхронную функцию
        if hasattr(asyncio, 'run'):
            asyncio.run(main_async())
        else:
            # Для старых версий Python
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main_async())
    except KeyboardInterrupt:
        print("\n\n👋 Диагностика прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")

if __name__ == '__main__':
    main()
