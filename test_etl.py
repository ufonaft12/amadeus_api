import pytest
import pandas as pd
from transform import transform_locations, get_spark_session

# Добавляем фикстуру, которая создает SparkSession для тестов
@pytest.fixture(scope="session")
def spark_session():
    return get_spark_session()

def test_transform_logic(spark_session):
    # 1. Готовим тестовые данные (имитируем ответ API)
    data = {
        'name': ['Heathrow Airport'],
        'iataCode': ['LHR'],
        'subType': ['AIRPORT'],
        'address.cityName': ['London'],
        'address.countryName': ['United Kingdom']
    }
    pdf = pd.DataFrame(data)
    
    # 2. Запускаем трансформацию
    result_df = transform_locations(spark_session, pdf)
    
    # 3. Проверяем результат
    assert result_df.count() == 1
    assert "location_name" in result_df.columns
    assert result_df.collect()[0]['code'] == 'LHR'
    print("✅ Тест логики трансформации пройден!")