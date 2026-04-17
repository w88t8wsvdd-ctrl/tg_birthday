import pandas as pd
import logging
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from config import AUTHORIZED_USER_IDS, DATA_FILE
from utils import save_birthdays, parse_birthday_date, load_birthdays, get_upcoming_birthdays, extract_first_name

logger = logging.getLogger(__name__)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загрузки Excel-файла."""

    user_id = update.effective_user.id

    # Проверяем авторизацию пользователя
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа к этому боту.")
        return

    # Проверяем, что это документ
    if not update.message.document:
        await update.message.reply_text("📎 Пожалуйста, отправьте Excel-файл (.xlsx).")
        return

    document = update.message.document

    # Проверяем расширение файла
    if not document.file_name.endswith('.xlsx'):
        await update.message.reply_text("❌ Пожалуйста, отправьте файл в формате .xlsx")
        return

    try:
        # Скачиваем файл
        file = await document.get_file()
        temp_path = Path(f"temp_{document.file_name}")
        await file.download_to_drive(temp_path)

        # Читаем Excel файл
        df = pd.read_excel(temp_path, engine='openpyxl')

        # Проверяем наличие нужных колонок
        required_columns = ['Имя', 'День рождения']

        # Логируем для отладки
        logger.info(f"Колонки в файле: {list(df.columns)}")

        # Проверяем названия колонок (нечувствительно к регистру и пробелам)
        df.columns = df.columns.str.strip()

        # Проверяем, есть ли нужные колонки
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'имя' in col_lower or 'name' in col_lower:
                column_mapping['Имя'] = col
            elif 'день' in col_lower and 'рожд' in col_lower or 'birthday' in col_lower or 'дата' in col_lower:
                column_mapping['День рождения'] = col

        if not all(key in column_mapping for key in required_columns):
            await update.message.reply_text(
                f'❌ Файл должен содержать столбцы "Имя" и "День рождения"\n'
                f'Найдены колонки: {list(df.columns)}'
            )
            temp_path.unlink(missing_ok=True)
            return

        # Переименовываем колонки для единообразия
        df = df.rename(columns=column_mapping)

        # Обрабатываем данные
        birthdays = []
        errors = []

        for idx, row in df.iterrows():
            try:
                name = str(row['Имя']).strip()
                if not name or name.lower() == 'nan':
                    continue

                birth_date = parse_birthday_date(row['День рождения'])

                birthdays.append({
                    'name': name,
                    'birthday': birth_date
                })

            except Exception as e:
                error_name = str(row.get('Имя', f'Строка {idx}')).strip()
                errors.append(error_name)
                logger.warning(f"Ошибка обработки записи: {e}")

        # Сохраняем данные (общие для всех пользователей)
        if birthdays:
            save_birthdays(birthdays, DATA_FILE)

            # Формируем ответ
            success_msg = f"✅ Данные обновлены! Загружено {len(birthdays)} записей."
            if errors:
                success_msg += f"\n❌ Ошибки в {len(errors)} записях: {', '.join(errors[:5])}"
                if len(errors) > 5:
                    success_msg += f" и еще {len(errors) - 5}"

            await update.message.reply_text(success_msg)
        else:
            await update.message.reply_text("❌ В файле нет корректных данных")

        # Удаляем временный файл
        temp_path.unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Ошибка обработки файла: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке файла")

        # Очищаем временные файлы
        temp_path = Path(f"temp_{document.file_name}")
        temp_path.unlink(missing_ok=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа к этому боту.")
        return
    
    await update.message.reply_text(
        "👋 **Добро пожаловать в Birthday Bot!** 🎉\n\n"
        
        "🤖 **Что умеет этот бот:**\n"
        "• Принимает Excel-файлы с днями рождения\n"
        "• Автоматически отправляет уведомления в 09:00\n"
        "• **Генерирует уникальные поздравления** для каждого именинника\n"
        "• Показывает ближайшие дни рождения\n"
        "• Хранит всю историю дней рождения\n\n"
        
        "📎 **Быстрый старт:**\n"
        "1. Отправьте Excel-файл с двумя столбцами:\n"
        "   • `Имя` (например: Анна)\n"
        "   • `День рождения` (формат: `ДД.ММ`)\n"
        "2. Получайте уведомления каждый день в 09:00\n"
        "3. Используйте команды для управления\n\n"
        
        "🎭 **Особенность:** Автоматическая генерация поздравлений!\n"
        "Каждое поздравление уникально и состоит из 3-5 предложений.\n"
        "Бот учитывает пол, сезон и добавляет эмодзи. 🎂✨\n\n"
        
        "⌨️ **Основные команды:**\n"
        "• `/help` - полная справка со всеми возможностями\n"
        "• `/nearest` - ближайшие дни рождения с поздравлениями\n"
        "• `/list` - весь список дней рождения\n"
        "• `/test` - проверка работы планировщика\n"
        "• `/greet Имя` - тест генерации поздравлений\n\n"
        
        "🚀 **Начните с отправки Excel-файла или используйте `/help` для подробностей!**"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        return
    
    await update.message.reply_text(
        "📋 **Доступные команды:**\n\n"
        
        "📎 **Загрузка данных:**\n"
        "Просто отправьте Excel-файл (.xlsx) со столбцами:\n"
        "• Имя (текст)\n"
        "• День рождения (формат: ДД.ММ, например: 15.03)\n\n"
        
        "⌨️ **Команды:**\n"
        "• `/start` - приветственное сообщение\n"
        "• `/help` - эта справка\n"
        "• `/nearest` - ближайшие дни рождения с уникальными поздравлениями 🎉\n"
        "• `/list` - все дни рождения по порядку\n"
        "• `/test` - проверка работы планировщика\n"
        "• `/greet [имя]` - тест генерации поздравлений для имени\n\n"

        "➕ **Управление списком:**\n"
        "• `/add Имя ДД.ММ` – добавить именинника\n"
        "• `/remove Имя` – удалить всех с таким именем\n"
        "• `/find Имя` – поиск по части имени\n"
        
        "🎭 **Генерация поздравлений:**\n"
        "Бот автоматически создаёт уникальные поздравления:\n"
        "• **Каждое поздравление состоит из 3-5 предложений**\n"
        "• **Все поздравления уникальны** (минимальное повторение)\n"
        "• **Учитывается пол именинника** (определяется по окончанию имени)\n"
        "• **Добавляются сезонные пожелания** (зима/весна/лето/осень)\n"
        "• **Автоматический подбор эмодзи** 🎉✨🎂\n"
        "• **Коллективные поздравления** для нескольких именинников\n\n"
        
        "🔧 **Примеры использования:**\n"
        "`/greet Анна` - покажет 3 разных поздравления для Анны\n"
        "`/nearest` - покажет ближайшие дни рождения с персонализированными поздравлениями\n\n"
        
        "📅 **Автоматические уведомления:**\n"
        "Каждый день в **09:00** вы получите уведомления о днях рождения\n"
        "на сегодня и завтра с **автоматически сгенерированными поздравлениями**!\n\n"
        
        "🔄 **Система генерации:**\n"
        "1. **Обращение к имениннику** - персонализированное начало\n"
        "2. **Основное поздравление** - стандартная фраза\n"
        "3. **1-2 персонализированных пожелания** - здоровье, успех, счастье\n"
        "4. **Завершающая фраза** (опционально) - финальное пожелание\n"
        "5. **Эмодзи** - автоматический подбор по категории\n\n"
        
        "🎯 **Пример готового поздравления:**\n"
        "```\n"
        "Дорогая Анна, с теплотой в сердце поздравляем\n"
        "тебя с днём рождения! Желаем крепкого здоровья,\n"
        "профессиональных успехов и личного счастья!\n"
        "Пусть каждый день будет наполнен радостью! 🎉✨🎂\n"
        "```\n\n"
        
        "🔄 **Важно:**\n"
        "• Отправка нового файла полностью заменяет старые данные\n"
        "• Все авторизованные пользователи работают с общим списком\n"
        "• Планировщик работает по времени сервера (UTC)\n\n"
        
        "📊 **Пример файла для загрузки:**\n"
        "```\n"
        "| Имя       | День рождения |\n"
        "|-----------|---------------|\n"
        "| Анна      | 15.03         |\n"
        "| Иван      | 22.11         |\n"
        "| Мария     | 01.07         |\n"
        "```\n\n"
        
        "❓ **Нужна помощь?**\n"
        "Используйте `/test` для проверки планировщика\n"
        "Используйте `/greet Имя` для теста генерации\n"
        "Используйте `/nearest` для просмотра ближайших дней рождения"
    )

async def nearest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /nearest - показывает ближайшие дни рождения."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа к этому боту.")
        return
    
    try:
        logger.info(f"Команда /nearest от пользователя {user_id}")
        
        # Загружаем данные
        from utils import load_birthdays, get_upcoming_birthdays
        birthdays = load_birthdays(DATA_FILE)
        
        if not birthdays:
            await update.message.reply_text("📭 Список дней рождения пуст.\nОтправьте Excel-файл с данными.")
            return
        
        logger.info(f"Загружено {len(birthdays)} записей")
        
        # Получаем ближайшие дни рождения (на 7 дней вперед)
        upcoming = get_upcoming_birthdays(birthdays, days_ahead=7)
        
        if not upcoming:
            await update.message.reply_text(
                "📅 На ближайшую неделю дней рождения нет.\n"
                "Следующий день рождения будет отображен в ежедневных уведомлениях."
            )
            return
        
        logger.info(f"Найдено {len(upcoming)} ближайших дней рождения")
        
        # Формируем сообщение с поздравлениями
        message_lines = ["📅 **Ближайшие дни рождения:**\n"]
        
        # Группируем по дням
        from collections import defaultdict
        birthdays_by_day = defaultdict(list)
        
        for bd in upcoming:
            birthdays_by_day[bd['day_offset']].append(bd)
        
        logger.info(f"Группировка по дням: {len(birthdays_by_day)} дней")
        
        # Для каждого дня формируем сообщение
        for day_offset in sorted(birthdays_by_day.keys()):
            day_birthdays = birthdays_by_day[day_offset]
            
            # Определяем описание дня
            if day_offset == 0:
                day_desc = "Сегодня"
                emoji = "🎂"
            elif day_offset == 1:
                day_desc = "Завтра"
                emoji = "📅"
            elif day_offset == 2:
                day_desc = "Послезавтра"
                emoji = "📆"
            else:
                day_desc = f"Через {day_offset} дней"
                emoji = "🗓️"
            
            # Полные имена для заголовка
            full_names = [bd['name'] for bd in day_birthdays]
            full_names_str = ", ".join(full_names)
            
            message_lines.append(f"\n{emoji} **{day_desc} ({day_birthdays[0]['date']})**: {full_names_str}")
            
            # Для каждого человека добавляем персональное поздравление
            try:
                from greetings_generator import generate_greeting
                
                for bd in day_birthdays:
                    greeting = generate_greeting(bd['name'])
                    message_lines.append(f"\n  • {greeting}")
                    
            except Exception as e:
                logger.error(f"Ошибка генерации поздравления для {bd['name']}: {e}")
                # Если не удалось сгенерировать, покажем просто имя
                from utils import extract_first_name
                name = extract_first_name(bd['name'])
                message_lines.append(f"\n  • {name} - с Днём рождения! 🎉")
        
        # Добавляем статистику
        today_count = len([b for b in upcoming if b['day_offset'] == 0])
        tomorrow_count = len([b for b in upcoming if b['day_offset'] == 1])
        
        message_lines.append(f"\n📊 **Статистика:**")
        if today_count > 0:
            message_lines.append(f"🎉 Сегодня празднуют: {today_count} человек")
        if tomorrow_count > 0:
            message_lines.append(f"📈 Завтра празднуют: {tomorrow_count} человек")
        
        message_lines.append(f"📋 Всего в ближайшие 7 дней: {len(upcoming)} дней рождения")
        
        # Добавляем общее пожелание
        try:
            from greetings_generator import get_collective_greeting
            if len(upcoming) > 0:
                # Используем имена из upcoming для коллективного поздравления
                upcoming_names = [bd['name'] for bd in upcoming]
                message_lines.append(f"\n{get_collective_greeting(upcoming_names)}")
        except Exception as e:
            logger.error(f"Ошибка генерации коллективного поздравления: {e}")
            message_lines.append(f"\n🎉 Поздравляем всех именинников!")
        
        # Отправляем сообщение (разбиваем если слишком длинное)
        full_message = "\n".join(message_lines)
        logger.info(f"Сообщение сформировано: {len(full_message)} символов")
        
        if len(full_message) > 4000:
            logger.info("Сообщение слишком длинное, разбиваем на части")
            # Разбиваем на части по 4000 символов
            parts = []
            while len(full_message) > 0:
                # Ищем хорошее место для разрыва (конец строки)
                if len(full_message) > 4000:
                    # Ищем последний перенос строки до 4000 символов
                    break_point = full_message[:4000].rfind('\n')
                    if break_point == -1:
                        break_point = 3999
                    part = full_message[:break_point]
                    parts.append(part)
                    full_message = full_message[break_point:].lstrip()
                else:
                    parts.append(full_message)
                    full_message = ""
            
            # Отправляем первую часть
            await update.message.reply_text(parts[0])
            logger.info(f"Отправлена часть 1: {len(parts[0])} символов")
            
            # Отправляем остальные части с задержкой
            for i, part in enumerate(parts[1:], 2):
                await asyncio.sleep(0.5)
                await update.message.reply_text(part)
                logger.info(f"Отправлена часть {i}: {len(part)} символов")
        else:
            await update.message.reply_text(full_message)
            logger.info(f"Сообщение отправлено: {len(full_message)} символов")
        
    except Exception as e:
        logger.error(f"Ошибка в команде /nearest: {e}", exc_info=True)
        error_message = f"❌ Произошла ошибка при получении данных: {str(e)}"
        
        # Добавляем больше информации для отладки
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Детали ошибки: {error_details}")
        
        # Отправляем краткое сообщение об ошибке пользователю
        await update.message.reply_text(
            f"❌ Произошла ошибка при получении данных.\n"
            f"Пожалуйста, попробуйте позже или используйте команду /test для проверки системы."
        )

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /list - показывает все дни рождения."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа к этому боту.")
        return
    
    try:
        # Загружаем данные
        birthdays = load_birthdays(DATA_FILE)
        
        if not birthdays:
            await update.message.reply_text("📭 Список дней рождения пуст.\nОтправьте Excel-файл с данными.")
            return
        
        # Сортируем по дате (по месяцу и дню)
        def sort_key(bd):
            day, month = map(int, bd['birthday'].split('.'))
            return (month, day)
        
        sorted_birthdays = sorted(birthdays, key=sort_key)
        
        # Формируем сообщение - ТОЛЬКО ПОЛНЫЕ ИМЕНА
        message_lines = [f"📋 **Все дни рождения** ({len(sorted_birthdays)} записей):\n"]
        
        # Группируем по месяцам
        months = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        
        current_month = None
        for bd in sorted_birthdays:
            month = int(bd['birthday'].split('.')[1])
            if month != current_month:
                message_lines.append(f"\n**{months[month]}**:")
                current_month = month
            
            # Показываем только полное имя
            message_lines.append(f"  {bd['birthday']} - {bd['name']}")
        
        # Если сообщение слишком длинное, разбиваем на части
        message_text = "\n".join(message_lines)
        if len(message_text) > 4000:  # Ограничение Telegram
            # Разбиваем по месяцам
            parts = []
            current_part = []
            current_length = 0
            
            for line in message_lines:
                if current_length + len(line) + 1 > 4000:
                    parts.append("\n".join(current_part))
                    current_part = [line]
                    current_length = len(line) + 1
                else:
                    current_part.append(line)
                    current_length += len(line) + 1
            
            if current_part:
                parts.append("\n".join(current_part))
            
            # Отправляем первую часть
            await update.message.reply_text(parts[0])
            
            # Отправляем остальные части с задержкой
            for part in parts[1:]:
                await asyncio.sleep(0.5)
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(message_text)
        
    except Exception as e:
        logger.error(f"Ошибка в команде /list: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении данных")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки планировщика."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа.")
        return
    
    try:
        from utils import load_birthdays, get_today_date, get_tomorrow_date
        from config import DATA_FILE
        
        # Загружаем данные
        birthdays = load_birthdays(DATA_FILE)
        
        if not birthdays:
            await update.message.reply_text("📭 Нет данных. Загрузите файл.")
            return
        
        # Получаем даты
        today = get_today_date()
        tomorrow = get_tomorrow_date()
        
        # Ищем совпадения
        today_birthdays = [b['name'] for b in birthdays if b['birthday'] == today]
        tomorrow_birthdays = [b['name'] for b in birthdays if b['birthday'] == tomorrow]
        
        # Формируем сообщение
        message = [
            "🔧 **ТЕСТ ПЛАНИРОВЩИКА**",
            f"📅 Дата проверки: {today}",
            f"📊 Всего записей: {len(birthdays)}",
            "",
            "🎂 **Сегодня:**",
            f"• Совпадений: {len(today_birthdays)}",
            f"• Имена: {', '.join(today_birthdays) if today_birthdays else 'нет'}",
            "",
            "📅 **Завтра:**",
            f"• Совпадений: {len(tomorrow_birthdays)}",
            f"• Имена: {', '.join(tomorrow_birthdays) if tomorrow_birthdays else 'нет'}",
            "",
            "✅ **Что будет отправлено в 09:00:**",
            ""
        ]
        
        # Показываем, что отправит планировщик
        try:
            # Пробуем импортировать format_birthday_message если он есть
            from utils import format_birthday_message
            
            if today_birthdays:
                today_msg = format_birthday_message(today_birthdays, is_today=True)
                message.append(f"• Сегодня:\n{today_msg}")
            
            if tomorrow_birthdays:
                tomorrow_msg = format_birthday_message(tomorrow_birthdays, is_today=False)
                message.append(f"\n• Завтра:\n{tomorrow_msg}")
            
        except ImportError:
            # Если format_birthday_message нет, показываем просто имена
            if today_birthdays:
                message.append(f"• Сегодня: {', '.join(today_birthdays)}")
            
            if tomorrow_birthdays:
                message.append(f"• Завтра: {', '.join(tomorrow_birthdays)}")
        
        if not today_birthdays and not tomorrow_birthdays:
            message.append("• Уведомлений не будет (нет дней рождения)")
        
        await update.message.reply_text("\n".join(message))
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def greet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /greet - тестирует генерацию поздравлений."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа к этому боту.")
        return
    
    try:
        # Импортируем здесь, чтобы избежать ошибок при загрузке
        try:
            from greetings_generator import generate_greeting, generate_collective_greeting
            generator_available = True
        except ImportError:
            generator_available = False
            await update.message.reply_text(
                "⚠️ Генератор поздравлений не найден.\n"
                "Проверьте наличие файла greetings_generator.py"
            )
            return
        
        # Если передан аргумент - имя для теста
        if context.args:
            name = " ".join(context.args)
            
            # Генерируем несколько вариантов поздравлений
            message_lines = [
                f"🎭 **Тест генератора поздравлений для '{name}':**\n",
                "**Сгенерированные поздравления (каждое уникальное):**"
            ]
            
            # Генерируем 3 разных поздравления
            for i in range(1, 4):
                try:
                    greeting = generate_greeting(name, min_sentences=3, max_sentences=5)
                    message_lines.append(f"\n{i}. {greeting}")
                except Exception as e:
                    message_lines.append(f"\n{i}. ❌ Ошибка: {str(e)}")
            
            # Тест коллективного поздравления
            message_lines.append(f"\n**Коллективное поздравление (тест):**")
            try:
                test_names = [name, "Иван", "Мария"]
                collective = generate_collective_greeting(test_names)
                message_lines.append(f"\n{collective}")
            except Exception as e:
                message_lines.append(f"\n❌ Ошибка коллективного поздравления: {str(e)}")
            
            # Отправляем сообщение
            full_message = "\n".join(message_lines)
            
            # Разбиваем на части если слишком длинное (ограничение Telegram 4096 символов)
            if len(full_message) > 4000:
                part1 = full_message[:4000]
                part2 = full_message[4000:]
                await update.message.reply_text(part1)
                await asyncio.sleep(0.5)
                await update.message.reply_text(part2[:4000] if len(part2) > 4000 else part2)
            else:
                await update.message.reply_text(full_message)
            
        else:
            # Без аргументов - общая информация
            message_lines = [
                "🎭 **Генератор уникальных поздравлений:**\n",
                "Бот автоматически генерирует уникальные поздравления из готовых компонентов.",
                "",
                "**Особенности:**",
                "• Каждое поздравление состоит из 3-5 предложений",
                "• Все поздравления уникальны (минимальное повторение)",
                "• Учитывается пол именинника (по окончанию имени)",
                "• Добавляются сезонные пожелания",
                "• Автоматически подбираются эмодзи 🎉✨🎂",
                "",
                "**Использование:**",
                "• `/greet [имя]` - тест генерации для конкретного имени",
                "• `/nearest` - ближайшие дни рождения с уникальными поздравлениями",
                "• Автоматические уведомления в 09:00",
                "",
                "**Примеры:**",
                "`/greet Анна` - покажет 3 разных поздравления для Анны",
                "`/greet Иван` - покажет 3 разных поздравления для Ивана",
                "",
                "**Структура поздравления:**",
                "1. Обращение к имениннику",
                "2. Основное поздравление",
                "3. 1-2 персонализированных пожелания",
                "4. Завершающая фраза (опционально)",
            ]
            
            await update.message.reply_text("\n".join(message_lines))
        
    except Exception as e:
        logger.error(f"Ошибка в команде /greet: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Произошла ошибка: {str(e)}")
        
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about - информация о системе генерации."""
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 У вас нет доступа к этому боту.")
        return
    
    await update.message.reply_text(
        "🎭 **Система генерации уникальных поздравлений**\n\n"
        
        "🤖 **Как это работает:**\n"
        "Бот использует компонентный подход для создания поздравлений.\n"
        "Каждое поздравление собирается из готовых проверенных компонентов.\n\n"
        
        "🧩 **Компоненты системы:**\n"
        "1. **Начала поздравлений** (8 вариантов)\n"
        "   Пример: 'Дорогой {name}, от всей души'\n\n"
        "2. **Основные поздравления** (6 вариантов)\n"
        "   Пример: 'поздравляем тебя с днём рождения!'\n\n"
        "3. **Пожелания по категориям** (15+ вариантов):\n"
        "   • Здоровье (3 варианта)\n"
        "   • Успех и карьера (3 варианта)\n"
        "   • Личное счастье (3 варианта)\n"
        "   • Финансы (2 варианта)\n"
        "   • Общие (4 варианта)\n\n"
        "4. **Гендерные пожелания** (4 женских + 4 мужских)\n"
        "5. **Сезонные пожелания** (по 2 на каждый сезон)\n"
        "6. **Завершения** (6 вариантов)\n"
        "7. **Эмодзи по категориям** (5 категорий)\n\n"
        
        "🔧 **Процесс генерации одного поздравления:**\n"
        "1. Определяется пол именинника по окончанию имени\n"
        "2. Выбирается уникальное начало\n"
        "3. Добавляется основное поздравление\n"
        "4. Подбирается 1-2 уникальных пожелания\n"
        "5. Добавляется завершение (с шансом 50%)\n"
        "6. Подбираются эмодзи (с шансом 70%)\n\n"
        
        "🎯 **Математика уникальности:**\n"
        "• Начала: 8 вариантов\n"
        "• Основные: 6 вариантов\n"
        "• Пожелания: 15+ вариантов\n"
        "• Итого комбинаций: 8 × 6 × 15 × 14 = **более 10,000**\n"
        "(если брать 2 пожелания из 15 с исключением повторений)\n\n"
        
        "🌈 **Сезонность:**\n"
        "Бот определяет текущий сезон и добавляет соответствующие пожелания:\n"
        "• ❄️ Зима - новогодние и зимние пожелания\n"
        "• 🌸 Весна - пожелания обновления и роста\n"
        "• ☀️ Лето - солнечные и теплые пожелания\n"
        "• 🍂 Осень - пожелания мудрости и урожая\n\n"
        
        "👥 **Коллективные поздравления:**\n"
        "Для нескольких именинников генерируется специальное коллективное поздравление\n"
        "с обращением ко всем и общими пожеланиями.\n\n"
        
        "🧪 **Тестирование:**\n"
        "Используйте `/greet Анна` для генерации 3 разных вариантов поздравлений.\n"
        "Каждый запуск создает новые уникальные комбинации!\n\n"
        
        "⚙️ **Технические детали:**\n"
        "• Минимальная длина: 3 предложения\n"
        "• Максимальная длина: 5 предложений\n"
        "• Система избегает повторений компонентов\n"
        "• Все компоненты хранятся в одном файле\n"
        "• Легко расширяется новыми компонентами\n\n"
        
        "📈 **Преимущества этой системы:**\n"
        "✅ Не надоедает - всегда разные поздравления\n"
        "✅ Контроль качества - все компоненты проверены\n"
        "✅ Гибкость - легко добавлять новые компоненты\n"
        "✅ Эффективность - минимальный вес кода\n"
        "✅ Персонализация - учет пола и сезона\n\n"
        
        "🔍 **Подробнее:** `/greet [имя]` - тест генерации\n"
        "📋 **Все команды:** `/help`"
    )

# handlers.py – добавить функции

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление нового именинника: /add Имя ДД.ММ"""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 Нет доступа.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ Использование: `/add Имя ДД.ММ`\n"
            "Пример: `/add Анна 15.03`", parse_mode='Markdown'
        )
        return

    # Последний аргумент – дата, остальное – имя (могут быть пробелы)
    *name_parts, date_str = context.args
    name = ' '.join(name_parts).strip()
    
    # Валидация даты
    try:
        from utils import parse_birthday_date
        birthday = parse_birthday_date(date_str)
    except Exception:
        await update.message.reply_text("❌ Неверный формат даты. Используйте ДД.ММ (например, 15.03)")
        return

    from utils import add_birthday
    success, msg = add_birthday(name, birthday, DATA_FILE)
    await update.message.reply_text(msg)

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление именинника: /remove Имя (удаляет всех с таким именем)"""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("❌ Укажите имя для удаления: `/remove Анна`", parse_mode='Markdown')
        return

    name = ' '.join(context.args).strip()
    from utils import remove_birthday
    success, msg, count = remove_birthday(name, DATA_FILE)
    await update.message.reply_text(msg)

async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск по имени: /find Анна"""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("🚫 Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("❌ Укажите имя для поиска: `/find Анна`", parse_mode='Markdown')
        return

    name = ' '.join(context.args).strip()
    from utils import find_birthday
    results = find_birthday(name, DATA_FILE)
    if not results:
        await update.message.reply_text(f"❌ Ничего не найдено для '{name}'.")
        return

    # Сортируем по дате
    results.sort(key=lambda x: (int(x['birthday'].split('.')[1]), int(x['birthday'].split('.')[0])))
    lines = [f"🔍 Найдено {len(results)} записей:"]
    for b in results:
        lines.append(f"  • {b['name']} – {b['birthday']}")
    await update.message.reply_text("\n".join(lines))
    
