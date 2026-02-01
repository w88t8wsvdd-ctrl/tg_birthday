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
    # ... (ваши существующие обработчики)
    
    # ЗАПУСКАЕМ ПЛАНИРОВЩИК В ОСНОВНОМ ПОТОКЕ ПЕРЕД run_polling
    logger.info("⏰ Запуск планировщика...")
    scheduler = setup_scheduler()
    
    if scheduler:
        logger.info("✅ Планировщик успешно запущен")
    else:
        logger.error("❌ Не удалось запустить планировщик")
    
    logger.info(f"Бот запущен для пользователей: {AUTHORIZED_USER_IDS}")
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
