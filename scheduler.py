from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import atexit
import sys
import os
import asyncio

# Добавляем путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN, AUTHORIZED_USER_IDS, DATA_FILE
from utils import load_birthdays, get_today_date, get_tomorrow_date

logger = logging.getLogger(__name__)

def send_message_sync(bot, chat_id, text, parse_mode='HTML'):
    """Синхронная обертка для отправки сообщений."""
    try:
        # Создаем новый event loop для синхронного вызова
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Запускаем асинхронную функцию синхронно
            result = loop.run_until_complete(
                bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        raise

def send_birthday_notifications():
    """Отправляет уведомления о днях рождения (синхронная версия)."""
    try:
        logger.info("🔄 Начало отправки уведомлений...")
        
        # Проверяем токен
        if not BOT_TOKEN or BOT_TOKEN == 'ваш_токен_бота_от_BotFather':
            logger.error("❌ BOT_TOKEN не установлен или имеет значение по умолчанию")
            return
        
        # Создаем бота
        bot = Bot(token=BOT_TOKEN)
        
        # Проверяем пользователей
        if not AUTHORIZED_USER_IDS:
            logger.error("❌ Нет авторизованных пользователей")
            return
        
        # Загружаем данные
        try:
            birthdays = load_birthdays(DATA_FILE)
            if not birthdays:
                logger.info("📭 Нет данных о днях рождения")
                return
            logger.info(f"📊 Загружено {len(birthdays)} записей")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных: {e}")
            return
        
        # Получаем даты
        try:
            today = get_today_date()
            tomorrow = get_tomorrow_date()
            logger.info(f"📅 Даты: сегодня {today}, завтра {tomorrow}")
        except Exception as e:
            logger.error(f"❌ Ошибка получения дат: {e}")
            return
        
        # Ищем совпадения
        today_birthdays = []
        tomorrow_birthdays = []
        
        try:
            for b in birthdays:
                if 'birthday' not in b or 'name' not in b:
                    continue
                    
                if b['birthday'] == today:
                    today_birthdays.append(b['name'])
                elif b['birthday'] == tomorrow:
                    tomorrow_birthdays.append(b['name'])
                    
            logger.info(f"🎂 Найдено на сегодня: {len(today_birthdays)}")
            logger.info(f"📅 Найдено на завтра: {len(tomorrow_birthdays)}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска совпадений: {e}")
            return
        
        # Формируем сообщения
        from utils import format_birthday_message
        
        messages = []
        
        if today_birthdays:
            try:
                today_message = format_birthday_message(today_birthdays, is_today=True)
                messages.append(today_message)
                logger.info(f"📝 Сообщение на сегодня: {len(today_message)} символов")
            except Exception as e:
                logger.error(f"❌ Ошибка форматирования сообщения на сегодня: {e}")
        
        if tomorrow_birthdays:
            try:
                tomorrow_message = format_birthday_message(tomorrow_birthdays, is_today=False)
                messages.append(tomorrow_message)
                logger.info(f"📝 Сообщение на завтра: {len(tomorrow_message)} символов")
            except Exception as e:
                logger.error(f"❌ Ошибка форматирования сообщения на завтра: {e}")
        
        # Отправляем всем пользователям если есть что отправлять
        if messages:
            message_text = "\n\n".join(messages)
            
            # Добавляем разделитель если нужно
            if today_birthdays or tomorrow_birthdays:
                try:
                    from greetings_generator import get_collective_greeting
                    message_text += f"\n\n{get_collective_greeting()}"
                except ImportError:
                    message_text += f"\n\n🎉 Поздравляем всех именинников!"
            
            logger.info(f"📨 Итоговое сообщение: {len(message_text)} символов")
            
            successful_sends = 0
            failed_sends = 0
            
            for user_id in AUTHORIZED_USER_IDS:
                try:
                    # Используем синхронную обертку
                    send_message_sync(bot, user_id, message_text, 'HTML')
                    logger.info(f"✅ Отправлено пользователю {user_id}")
                    successful_sends += 1
                    
                except TelegramError as e:
                    logger.error(f"❌ Ошибка Telegram пользователю {user_id}: {e}")
                    failed_sends += 1
                except Exception as e:
                    logger.error(f"❌ Общая ошибка отправки пользователю {user_id}: {e}")
                    failed_sends += 1
            
            logger.info(f"📊 Итог: успешно {successful_sends}, ошибок {failed_sends}")
            
        else:
            logger.info("ℹ️ Нет уведомлений для отправки (нет дней рождения)")
            
    except TelegramError as e:
        logger.error(f"❌ Ошибка Telegram API: {e}")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в send_birthday_notifications: {e}")
        import traceback
        logger.error(traceback.format_exc())

def setup_scheduler():
    """Настраивает и запускает планировщик."""
    try:
        logger.info("⏰ Настройка планировщика...")
        
        scheduler = BackgroundScheduler()
        
        # Задача на 09:00 каждый день (по Москве)
        scheduler.add_job(
            send_birthday_notifications,
            CronTrigger(hour=9, minute=00, timezone='Europe/Moscow'),
            id='birthday_notifications',
            name='Ежедневные уведомления о днях рождения',
            replace_existing=True
        )
        
        # Тестовая задача - запуск при старте для проверки
        scheduler.add_job(
            lambda: logger.info("✅ Планировщик инициализирован"),
            'date',
            run_date=None,  # Сразу
            id='init_job',
            name='Инициализация'
        )
        
        # Останавливаем планировщик при выходе
        atexit.register(lambda: scheduler.shutdown(wait=False))
        
        scheduler.start()
        
        # Выводим информацию о задачах
        jobs = scheduler.get_jobs()
        logger.info(f"✅ Планировщик запущен. Задач: {len(jobs)}")
        
        for job in jobs:
            if job.next_run_time:
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"   📅 Задача '{job.name}': следующее выполнение {next_run}")
            else:
                logger.info(f"   📅 Задача '{job.name}': выполнена")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"❌ Ошибка настройки планировщика: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
