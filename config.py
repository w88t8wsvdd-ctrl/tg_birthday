import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Список разрешенных пользователей (через запятую в .env)
authorized_ids_str = os.getenv("AUTHORIZED_USER_IDS", "")
AUTHORIZED_USER_IDS = []

if authorized_ids_str:
    # Разделяем по запятой, удаляем пробелы и преобразуем в int
    for user_id in authorized_ids_str.split(","):
        user_id = user_id.strip()
        if user_id:
            try:
                AUTHORIZED_USER_IDS.append(int(user_id))
            except ValueError:
                print(f"Warning: Invalid user ID '{user_id}' in AUTHORIZED_USER_IDS")

# Для обратной совместимости: если используется старый формат с одним пользователем
single_user_id = os.getenv("AUTHORIZED_USER_ID")
if single_user_id and single_user_id.strip():
    try:
        user_id_int = int(single_user_id.strip())
        if user_id_int not in AUTHORIZED_USER_IDS:
            AUTHORIZED_USER_IDS.append(user_id_int)
    except ValueError:
        print(f"Warning: Invalid user ID '{single_user_id}' in AUTHORIZED_USER_ID")

# Проверяем, что есть хотя бы один пользователь
if not AUTHORIZED_USER_IDS:
    print("Error: No authorized users configured. Check your .env file")
    exit(1)

DATA_FILE = "data/birthdays.json"