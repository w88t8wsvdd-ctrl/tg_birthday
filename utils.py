import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

def load_birthdays(data_file: str) -> list:
    """Загружает данные о днях рождения из JSON-файла."""
    try:
        data_path = Path(data_file)
        if not data_path.exists():
            return []

        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return []

def save_birthdays(birthdays: list, data_file: str) -> bool:
    """Сохраняет данные о днях рождения в JSON-файл."""
    try:
        data_path = Path(data_file)
        data_path.parent.mkdir(parents=True, exist_ok=True)

        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(birthdays, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")
        return False

def get_today_date() -> str:
    """Возвращает текущую дату в формате ДД.ММ."""
    return datetime.now().strftime("%d.%m")

def get_tomorrow_date() -> str:
    """Возвращает завтрашнюю дату в формате ДД.ММ."""
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime("%d.%m")

def parse_birthday_date(date_value) -> str:
    """
    Парсит значение даты и возвращает в формате ДД.ММ.
    Поддерживает разные форматы:
    - datetime объекты
    - строки в формате ДД.ММ, ДД/ММ, ДД-ММ
    - полные даты с годом (YYYY-MM-DD)
    - строки в формате Excel дат
    """
    try:
        # Если это уже datetime объект (pandas может вернуть datetime)
        if isinstance(date_value, datetime):
            return date_value.strftime("%d.%m")

        # Преобразуем в строку
        date_str = str(date_value).strip()

        # Если пустая строка
        if not date_str or date_str.lower() == 'nan' or date_str.lower() == 'nat':
            raise ValueError("Пустая дата")

        # Пробуем разные форматы
        # 1. Форматы с годом
        year_formats = [
            "%Y-%m-%d",  # 2024-01-03
            "%Y-%m-%d %H:%M:%S",  # 2024-01-03 00:00:00
            "%d.%m.%Y",  # 03.01.2024
            "%d/%m/%Y",  # 03/01/2024
            "%d-%m-%Y",  # 03-01-2024
        ]

        # 2. Форматы без года (только день и месяц)
        month_formats = [
            "%d.%m",    # 03.01
            "%d/%m",    # 03/01
            "%d-%m",    # 03-01
            "%d.%m.",   # 03.01.
            "%d %m",    # 03 01
        ]

        # Сначала пробуем форматы с годом
        for fmt in year_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%d.%m")
            except ValueError:
                continue

        # Затем пробуем форматы без года
        for fmt in month_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%d.%m")
            except ValueError:
                continue

        # Если Excel хранит даты как числа (серийные номера дат)
        try:
            # Проверяем, не является ли это числом (Excel serial date)
            if date_str.replace('.', '').isdigit():
                # Excel использует 1 = 01.01.1900
                # Но pandas уже должен был это обработать
                # Если все же дошло сюда, преобразуем
                days = float(date_str)
                # Excel base date: 1899-12-30
                base_date = datetime(1899, 12, 30)
                date_obj = base_date + timedelta(days=days)
                return date_obj.strftime("%d.%m")
        except:
            pass

        # Если ничего не подошло
        raise ValueError(f"Некорректный формат даты: {date_str}")

    except Exception as e:
        logger.error(f"Ошибка парсинга даты '{date_value}': {e}")
        raise

def get_upcoming_birthdays(birthdays: list, days_ahead: int = 7) -> list:
    """
    Возвращает список дней рождения на ближайшие N дней.
    days_ahead: количество дней вперед для поиска (по умолчанию 7)
    """
    if not birthdays:
        return []

    today = datetime.now()
    upcoming = []

    for day_offset in range(days_ahead + 1):  # +1 чтобы включить сегодня
        target_date = today + timedelta(days=day_offset)
        target_date_str = target_date.strftime("%d.%m")

        # Находим дни рождения на эту дату
        for bd in birthdays:
            if bd['birthday'] == target_date_str:
                # Формируем понятное описание дня
                if day_offset == 0:
                    day_desc = "сегодня"
                elif day_offset == 1:
                    day_desc = "завтра"
                elif day_offset == 2:
                    day_desc = "послезавтра"
                else:
                    day_desc = target_date.strftime("%d.%m")

                upcoming.append({
                    'name': bd['name'],
                    'date': bd['birthday'],
                    'day_offset': day_offset,
                    'day_description': day_desc
                })

    # Сортируем по дате
    upcoming.sort(key=lambda x: x['day_offset'])
    return upcoming

# В utils.py добавьте:
def format_birthday_message(names: list, is_today: bool = True) -> str:
    """Форматирует сообщение о днях рождения."""
    if not names:
        return ""
    
    day_word = "Сегодня" if is_today else "Завтра"
    
    if len(names) == 1:
        return f"{day_word} день рождения у {names[0]}!"
    else:
        names_str = ", ".join(names)
        return f"{day_word} дни рождения у: {names_str}!"

def format_birthday_message(names: list, is_today: bool = True) -> str:
    """
    Форматирует сообщение о днях рождения с уникальными поздравлениями.
    
    Args:
        names: список имен
        is_today: True - сегодня, False - завтра
    """
    try:
        from greetings_generator import generate_greeting, generate_collective_greeting
        
        if not names:
            return ""
        
        day_word = "🎂 Сегодня" if is_today else "📅 Завтра"
        
        if len(names) == 1:
            # Для одного человека - персонализированное поздравление
            name = names[0]
            greeting = generate_greeting(name, min_sentences=3, max_sentences=4)
            return f"{day_word} день рождения у {name}!\n\n{greeting}"
        
        else:
            # Для нескольких людей - коллективное поздравление
            names_str = ", ".join(names)
            collective_greeting = generate_collective_greeting(names)
            
            if is_today:
                return f"🎉 {day_word} дни рождения у: {names_str}!\n\n{collective_greeting}"
            else:
                return f"📅 {day_word} дни рождения у: {names_str}!\n\n{collective_greeting}"
                
    except ImportError:
        # Fallback если генератор не установлен
        if len(names) == 1:
            return f"{day_word} день рождения у {names[0]}!"
        else:
            names_str = ", ".join(names)
            return f"{day_word} дни рождения у: {names_str}!"
