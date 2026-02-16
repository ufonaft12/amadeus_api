from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F
import pandas as pd

def get_spark_session() -> SparkSession:
    return SparkSession.builder.appName("AmadeusETL").getOrCreate()

def transform_locations(spark: SparkSession, pdf: pd.DataFrame) -> DataFrame:
    """Типизированная функция трансформации"""
    if pdf.empty:
        raise ValueError("Pandas DataFrame is empty")
        
    df = spark.createDataFrame(pdf)
    
    return df.select(
        F.col("name").alias("location_name"),
        F.col("iataCode").alias("code"),
        F.col("subType").alias("type"),
        F.col("`address.cityName`").alias("city")
    ).filter(F.col("type") == "AIRPORT")