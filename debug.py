# debug.py
import pandas as pd

# Протестируйте чтение вашего файла отдельно
df = pd.read_excel('birthdays.xlsx', engine='openpyxl')
print("Колонки:", df.columns.tolist())
print("\nТипы данных:")
print(df.dtypes)
print("\nПервые 5 строк:")
print(df.head())
print("\nПримеры дат:")
for i, date_val in enumerate(df['День рождения'].head(10)):
    print(f"  {i}: {date_val} (тип: {type(date_val)})")