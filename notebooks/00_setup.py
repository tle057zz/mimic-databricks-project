# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Setup
# MAGIC Shared configuration for the MIMIC medallion pipeline.

# COMMAND ----------

from pyspark.sql import SparkSession

# Catalog / schema names (adjust for your workspace)
CATALOG = "mimic"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# Local / DBFS path to landed CSV.GZ files
RAW_DATA_PATH = "/Workspace/mimic-databricks-project/data/raw"
# Example DBFS alternative: "dbfs:/FileStore/mimic/raw"

BRONZE_TABLES = [
    "patients",
    "admissions",
    "transfers",
    "diagnoses_icd",
    "procedures_icd",
    "prescriptions",
    "d_icd_diagnoses",
]

# COMMAND ----------

def fq_table(schema: str, table: str) -> str:
    return f"{CATALOG}.{schema}.{table}"


def ensure_schemas(spark: SparkSession) -> None:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
    for schema in (BRONZE_SCHEMA, SILVER_SCHEMA, GOLD_SCHEMA):
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema}")


# COMMAND ----------

spark = SparkSession.builder.getOrCreate()
ensure_schemas(spark)

print("Setup complete")
print(f"Catalog: {CATALOG}")
print(f"Raw path: {RAW_DATA_PATH}")
print(f"Bronze tables: {BRONZE_TABLES}")
