import os
from client import AmadeusClient
from transform import get_spark_session, transform_locations
import pandas as pd

# Константы (в реальном проекте их лучше вынести в config.py или .env)
API_KEY = "atFBUXQ0TKW4sEgrYWpmW03o27Ju8g51"
API_SECRET = "GS5XfAkhdsJ0baKT"

def run_pipeline():
    """Главная функция запуска ETL процесса"""
    
    # 1. Инициализация клиента
    client = AmadeusClient(API_KEY, API_SECRET)
    
    # 2. Авторизация
    print("--- Шаг 1: Авторизация ---")
    token = client.get_token()
    if not token:
        print("❌ Не удалось получить токен. Выход.")
        return

    # 3. Извлечение данных с пагинацией
    print("\n--- Шаг 2: Извлечение данных (Pagination) ---")
    # Запрашиваем данные по 10 штук на страницу, максимум 3 страницы
    raw_pdf = client.fetch_locations_paginated(keyword="London", page_limit=10, max_pages=3)
    
    if raw_pdf.empty:
        print("⚠️ Данные не найдены. Выход.")
        return

    # 4. Трансформация в PySpark
    print("\n--- Шаг 3: Трансформация в Spark ---")
    try:
        spark = get_spark_session()
        final_spark_df = transform_locations(spark, raw_pdf)
        
        # Показываем результат
        final_spark_df.show(truncate=False)
        print(f"✅ Успешно обработано строк: {final_spark_df.count()}")

        # 4. Сохранение в разные форматы
        print("Сохранение результатов...")
        final_pdf = final_spark_df.toPandas()
        os.makedirs("output", exist_ok=True)
        
        # Вариант А: JSON (стандарт для веба и данных)
        final_pdf.to_json("output/airports.json", orient="records", indent=4)
        
        # Вариант Б: Excel (если хочешь, чтобы друг открыл файл просто в таблице)
        # Для этого нужно: pip install openpyxl
        final_pdf.to_excel("output/airports.xlsx", index=False)
        
        print("✅ Готово! Проверь папку 'output' — там теперь JSON и Excel файлы.")
        
    except Exception as e:
        print(f"❌ Ошибка в блоке трансформации или сохранения: {e}")
    finally:
        pass

if __name__ == "__main__":
    run_pipeline()