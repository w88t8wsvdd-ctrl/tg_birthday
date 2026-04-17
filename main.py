# main.py - полная исправленная версия:

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, AUTHORIZED_USER_IDS
from handlers import (
    start_command, 
    help_command, 
    handle_file, 
    nearest_command, 
    list_command, 
    test_command, 
    about_command, 
    greet_command
)
from scheduler import setup_scheduler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Простой эхо-обработчик для теста
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простой обработчик для проверки."""
    user_id = update.effective_user.id
    logger.info(f"Сообщение от {user_id}: {update.message.text}")
    
    if user_id in AUTHORIZED_USER_IDS:
        await update.message.reply_text(f"📝 Я получил: {update.message.text}")

# Команда для проверки статуса
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка статуса бота."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа.")
        return
    
    await update.message.reply_text(
        f"🤖 **Статус бота**\n\n"
        f"✅ Бот работает\n"
        f"👤 Ваш ID: {user_id}\n"
        f"📊 Авторизованных пользователей: {len(AUTHORIZED_USER_IDS)}\n"
        f"🔧 Команды: /start, /help, /nearest, /list, /test, /about, /greet, /status"
    )

def main():
    """Основная функция запуска бота."""
    
    if not BOT_TOKEN or BOT_TOKEN == 'ваш_токен_бота_от_BotFather':
        logger.error("❌ BOT_TOKEN не установлен. Проверьте .env файл!")
        return
    
    logger.info(f"🚀 Запуск бота для пользователей: {AUTHORIZED_USER_IDS}")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд В ПРАВИЛЬНОМ ПОРЯДКЕ
    # Важно: более специфичные команды должны быть выше
    
    # 1. Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("nearest", nearest_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("greet", greet_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("find", find_command))
    
    # 2. Обработчик файлов
    application.add_handler(MessageHandler(
        filters.Document.ALL & filters.User(user_id=AUTHORIZED_USER_IDS),
        handle_file
    ))
    
    # 3. Эхо-обработчик для отладки (должен быть ПОСЛЕДНИМ)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(user_id=AUTHORIZED_USER_IDS),
        echo
    ))
    
    # Запускаем планировщик
    logger.info("⏰ Настройка планировщика...")
    try:
        scheduler = setup_scheduler()
        if scheduler:
            logger.info("✅ Планировщик запущен")
            
            # Показываем задачи планировщика
            jobs = scheduler.get_jobs()
            logger.info(f"📋 Задач в планировщике: {len(jobs)}")
            for job in jobs:
                logger.info(f"  • {job.name}: {job.next_run_time}")
        else:
            logger.error("❌ Не удалось запустить планировщик")
    except Exception as e:
        logger.error(f"❌ Ошибка планировщика: {e}")
    
    # Запускаем бота
    logger.info("🤖 Бот запущен и готов к работе!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # Очищаем старые обновления
    )

if __name__ == '__main__':
    main()
