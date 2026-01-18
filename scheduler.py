from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from config import BOT_TOKEN, AUTHORIZED_USER_IDS, DATA_FILE
from utils import load_birthdays, get_today_date, get_tomorrow_date

logger = logging.getLogger(__name__)

def send_birthday_notifications():
    """Отправляет уведомления о днях рождения всем авторизованным пользователям."""
    try:
        bot = Bot(token=BOT_TOKEN)

        # Загружаем общие данные
        birthdays = load_birthdays(DATA_FILE)
        if not birthdays:
            logger.info("Нет данных о днях рождения")
            return

        # Получаем даты
        today = get_today_date()
        tomorrow = get_tomorrow_date()

        # Ищем совпадения
        today_birthdays = [b['name'] for b in birthdays if b['birthday'] == today]
        tomorrow_birthdays = [b['name'] for b in birthdays if b['birthday'] == tomorrow]

        # Формируем сообщение
        messages = []

        if today_birthdays:
            names = ', '.join(today_birthdays)
            messages.append(f"🎂 Сегодня день рождения у: {names}!")

        if tomorrow_birthdays:
            names = ', '.join(tomorrow_birthdays)
            messages.append(f"📅 Завтра день рождения у: {names}")

        # Отправляем всем пользователям если есть что отправлять
        if messages:
            message_text = "\n".join(messages)
            for user_id in AUTHORIZED_USER_IDS:
                try:
                    bot.send_message(chat_id=user_id, text=message_text)
                    logger.info(f"Отправлено уведомление пользователю {user_id}")
                except Exception as e:
                    logger.error(f"Ошибка отправки пользователю {user_id}: {e}")
        else:
            logger.info("Нет дней рождения на сегодня/завтра")

    except TelegramError as e:
        logger.error(f"Ошибка Telegram при отправке уведомления: {e}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {e}")

def setup_scheduler():
    """Настраивает и запускает планировщик."""
    scheduler = BlockingScheduler()

    # Задача на 09:00 каждый день
    scheduler.add_job(
        send_birthday_notifications,
        CronTrigger(hour=9, minute=0),
        id='birthday_notifications',
        name='Ежедневные уведомления о днях рождения',
        replace_existing=True
    )

    logger.info(f"Планировщик запущен. Пользователей: {len(AUTHORIZED_USER_IDS)}")
    logger.info(f"Уведомления будут отправляться в 09:00 каждый день.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Планировщик остановлен")