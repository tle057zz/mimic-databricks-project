# Databricks notebook source
# MAGIC %md
# MAGIC # 07 — Silver Prescriptions
# MAGIC Clean and conform `prescriptions` (FKs: `subject_id`, `hadm_id`).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

src = spark.table(fq_table(BRONZE_SCHEMA, "prescriptions"))
admissions = spark.table(fq_table(SILVER_SCHEMA, "admissions")).select(
    "subject_id", "hadm_id"
)

silver = (
    src.withColumn("subject_id", F.col("subject_id").cast("long"))
    .withColumn("hadm_id", F.col("hadm_id").cast("long"))
    .filter(F.col("subject_id").isNotNull() & F.col("hadm_id").isNotNull())
    .join(admissions, on=["subject_id", "hadm_id"], how="inner")
)

(
    silver.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fq_table(SILVER_SCHEMA, "prescriptions"))
)

print(f"silver.prescriptions: {silver.count()} rows")
silver.printSchema()
