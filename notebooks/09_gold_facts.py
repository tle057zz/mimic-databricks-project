# Databricks notebook source
# MAGIC %md
# MAGIC # 09 — Gold Facts
# MAGIC Build fact tables: diagnoses, procedures, prescriptions, transfers.

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

fact_diagnoses = spark.table(fq_table(SILVER_SCHEMA, "diagnoses")).select(
    "subject_id",
    "hadm_id",
    "seq_num",
    "icd_code",
    "icd_version",
    "long_title",
)

fact_procedures = spark.table(fq_table(SILVER_SCHEMA, "procedures")).select(
    "subject_id",
    "hadm_id",
    "seq_num",
    "icd_code",
    "icd_version",
    "chartdate",
)

fact_prescriptions = spark.table(fq_table(SILVER_SCHEMA, "prescriptions")).select(
    "subject_id",
    "hadm_id",
    "pharmacy_id",
    "starttime",
    "stoptime",
    "drug_type",
    "drug",
    "dose_val_rx",
    "dose_unit_rx",
    "route",
)

fact_transfers = spark.table(fq_table(SILVER_SCHEMA, "transfers")).select(
    "transfer_id",
    "subject_id",
    "hadm_id",
    "eventtype",
    "careunit",
    "intime",
    "outtime",
)

for name, df in [
    ("fact_diagnoses", fact_diagnoses),
    ("fact_procedures", fact_procedures),
    ("fact_prescriptions", fact_prescriptions),
    ("fact_transfers", fact_transfers),
]:
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fq_table(GOLD_SCHEMA, name))
    )
    print(f"gold.{name}: {df.count()} rows")

print("Gold facts complete")
