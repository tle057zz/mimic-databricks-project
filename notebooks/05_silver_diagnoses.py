# Databricks notebook source
# MAGIC %md
# MAGIC # 05 — Silver Diagnoses
# MAGIC Clean `diagnoses_icd` and enrich with `d_icd_diagnoses` (FKs: `subject_id`, `hadm_id`, `icd_code`).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

diagnoses = spark.table(fq_table(BRONZE_SCHEMA, "diagnoses_icd"))
icd_lookup = spark.table(fq_table(BRONZE_SCHEMA, "d_icd_diagnoses")).select(
    "icd_code", "icd_version", "long_title"
)
admissions = spark.table(fq_table(SILVER_SCHEMA, "admissions")).select(
    "subject_id", "hadm_id"
)

silver = (
    diagnoses.withColumn("subject_id", F.col("subject_id").cast("long"))
    .withColumn("hadm_id", F.col("hadm_id").cast("long"))
    .withColumn("seq_num", F.col("seq_num").cast("int"))
    .filter(F.col("icd_code").isNotNull())
    .join(admissions, on=["subject_id", "hadm_id"], how="inner")
    .join(icd_lookup, on=["icd_code", "icd_version"], how="left")
)

(
    silver.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fq_table(SILVER_SCHEMA, "diagnoses"))
)

print(f"silver.diagnoses: {silver.count()} rows")
silver.printSchema()
