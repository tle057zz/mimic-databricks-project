# Databricks notebook source
# MAGIC %md
# MAGIC # 06 — Silver Procedures
# MAGIC Clean and conform `procedures_icd` (FKs: `subject_id`, `hadm_id`, `icd_code`).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

src = spark.table(fq_table(BRONZE_SCHEMA, "procedures_icd"))
admissions = spark.table(fq_table(SILVER_SCHEMA, "admissions")).select(
    "subject_id", "hadm_id"
)

silver = (
    src.withColumn("subject_id", F.col("subject_id").cast("long"))
    .withColumn("hadm_id", F.col("hadm_id").cast("long"))
    .withColumn("seq_num", F.col("seq_num").cast("int"))
    .filter(F.col("icd_code").isNotNull())
    .join(admissions, on=["subject_id", "hadm_id"], how="inner")
)

(
    silver.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fq_table(SILVER_SCHEMA, "procedures"))
)

print(f"silver.procedures: {silver.count()} rows")
silver.printSchema()
