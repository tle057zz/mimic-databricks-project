# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Silver Patients
# MAGIC Clean and conform `patients` (PK: `subject_id`).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

src = spark.table(fq_table(BRONZE_SCHEMA, "patients"))

silver = (
    src.dropDuplicates(["subject_id"])
    .withColumn("subject_id", F.col("subject_id").cast("long"))
    .filter(F.col("subject_id").isNotNull())
)

(
    silver.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fq_table(SILVER_SCHEMA, "patients"))
)

print(f"silver.patients: {silver.count()} rows")
silver.printSchema()
