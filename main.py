import asyncio
import logging
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN, AUTHORIZED_USER_IDS
from handlers import start_command, help_command, handle_file, nearest_command, list_command, test_command, about_command, greet_command
from scheduler import setup_scheduler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start_scheduler():
    """Запускает планировщик в отдельном потоке."""
    setup_scheduler()

def main():
    """Основная функция запуска бота."""

    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("nearest", nearest_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("greet", greet_command))

    # Регистрируем обработчик файлов для каждого авторизованного пользователя
    application.add_handler(MessageHandler(
        filters.Document.ALL & filters.User(user_id=AUTHORIZED_USER_IDS),
        handle_file
    ))

    # Запускаем планировщик в отдельном потоке
    scheduler_thread = Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    logger.info(f"Бот запущен для пользователей: {AUTHORIZED_USER_IDS}")

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
