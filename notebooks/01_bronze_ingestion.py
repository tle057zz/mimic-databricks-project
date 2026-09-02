# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Bronze Ingestion
# MAGIC Load scoped `hosp/` CSV.GZ files into Bronze Delta tables (raw, as-is).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import DataFrame


def read_raw_csv(table_name: str) -> DataFrame:
    path = f"{RAW_DATA_PATH}/{table_name}.csv.gz"
    return (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .option("compression", "gzip")
        .csv(path)
    )


def write_bronze(df: DataFrame, table_name: str) -> None:
    target = fq_table(BRONZE_SCHEMA, table_name)
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(target)
    )
    print(f"Wrote {target} ({df.count()} rows)")


# COMMAND ----------

for table in BRONZE_TABLES:
    df = read_raw_csv(table)
    write_bronze(df, table)

print("Bronze ingestion complete")
