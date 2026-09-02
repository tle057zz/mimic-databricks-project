# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Silver Transfers
# MAGIC Clean and conform `transfers` (PK: `transfer_id`, FKs: `subject_id`, `hadm_id`).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

src = spark.table(fq_table(BRONZE_SCHEMA, "transfers"))
admissions = spark.table(fq_table(SILVER_SCHEMA, "admissions")).select(
    "subject_id", "hadm_id"
)

silver = (
    src.dropDuplicates(["transfer_id"])
    .withColumn("transfer_id", F.col("transfer_id").cast("long"))
    .withColumn("subject_id", F.col("subject_id").cast("long"))
    .withColumn("hadm_id", F.col("hadm_id").cast("long"))
    .filter(F.col("transfer_id").isNotNull())
    .join(admissions, on=["subject_id", "hadm_id"], how="left")
)

(
    silver.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fq_table(SILVER_SCHEMA, "transfers"))
)

print(f"silver.transfers: {silver.count()} rows")
silver.printSchema()
