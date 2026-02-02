#!/usr/bin/env python3
"""Минимальный тестовый бот для проверки работы команд."""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из config.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN, AUTHORIZED_USER_IDS

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простая тестовая команда."""
    user_id = update.effective_user.id
    await update.message.reply_text(f"✅ Тест работает! Ваш ID: {user_id}\n"
                                   f"Авторизован: {user_id in AUTHORIZED_USER_IDS}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Тестовый бот запущен!\n"
                                  "Команды:\n"
                                  "/test - проверка работы\n"
                                  "/id - ваш ID")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Ваш ID: {update.effective_user.id}")

def main():
    """Запуск минимального бота."""
    if not BOT_TOKEN or BOT_TOKEN == 'ваш_токен_бота_от_BotFather':
        print("❌ Установите BOT_TOKEN в .env файле!")
        return
    
    print(f"🤖 Запуск тестового бота...")
    print(f"👤 Авторизованные пользователи: {AUTHORIZED_USER_IDS}")
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_command))
    app.add_handler(CommandHandler("id", get_id))
    
    # Запускаем бота
    print("✅ Бот запущен. Отправьте /start в Telegram")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
