#!/usr/bin/env python3
"""Проверка работы планировщика."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import setup_scheduler
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    logger.info("🧪 Тестируем планировщик отдельно от бота...")
    
    # Запускаем планировщик
    scheduler = setup_scheduler()
    
    if not scheduler:
        logger.error("❌ Не удалось запустить планировщик")
        return
    
    # Ждем и показываем информацию о задачах
    logger.info("⏳ Ждем 30 секунд...")
    time.sleep(2)
    
    # Проверяем задачи
    jobs = scheduler.get_jobs()
    logger.info(f"📋 Найдено задач: {len(jobs)}")
    
    for job in jobs:
        logger.info(f"  📝 Задача: {job.name}")
        if job.next_run_time:
            logger.info(f"    ⏰ Следующий запуск: {job.next_run_time}")
        else:
            logger.info(f"    ⚠️ Без следующего запуска")
    
    # Запускаем уведомления вручную
    logger.info("🎯 Запускаем уведомления вручную...")
    from scheduler import send_birthday_notifications
    send_birthday_notifications()
    
    # Ожидаем
    logger.info("⏳ Ожидаем завершения... (Ctrl+C для выхода)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n👋 Завершаем проверку")
        scheduler.shutdown()

if __name__ == '__main__':
    main()
