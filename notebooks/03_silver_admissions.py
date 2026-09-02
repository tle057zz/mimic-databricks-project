# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Silver Admissions
# MAGIC Clean and conform `admissions` (PK: `hadm_id`, FK: `subject_id`).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

src = spark.table(fq_table(BRONZE_SCHEMA, "admissions"))
patients = spark.table(fq_table(SILVER_SCHEMA, "patients")).select("subject_id")

silver = (
    src.dropDuplicates(["hadm_id"])
    .withColumn("hadm_id", F.col("hadm_id").cast("long"))
    .withColumn("subject_id", F.col("subject_id").cast("long"))
    .filter(F.col("hadm_id").isNotNull() & F.col("subject_id").isNotNull())
    .join(patients, on="subject_id", how="inner")
)

(
    silver.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fq_table(SILVER_SCHEMA, "admissions"))
)

print(f"silver.admissions: {silver.count()} rows")
silver.printSchema()
