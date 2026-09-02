# Databricks notebook source
# MAGIC %md
# MAGIC # 08 — Gold Dimensions
# MAGIC Build dimension tables for analytics (patient, admission, ICD).

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

# dim_patient
dim_patient = spark.table(fq_table(SILVER_SCHEMA, "patients")).select(
    F.col("subject_id").alias("patient_sk"),
    "subject_id",
    "gender",
    "anchor_age",
    "anchor_year",
    "anchor_year_group",
    "dod",
)

# dim_admission
dim_admission = spark.table(fq_table(SILVER_SCHEMA, "admissions")).select(
    F.col("hadm_id").alias("admission_sk"),
    "hadm_id",
    "subject_id",
    "admittime",
    "dischtime",
    "admission_type",
    "admission_location",
    "discharge_location",
    "insurance",
    "language",
    "marital_status",
    "race",
    "hospital_expire_flag",
)

# dim_icd_diagnosis
dim_icd = (
    spark.table(fq_table(BRONZE_SCHEMA, "d_icd_diagnoses"))
    .dropDuplicates(["icd_code", "icd_version"])
    .select(
        F.concat_ws("|", "icd_code", "icd_version").alias("icd_sk"),
        "icd_code",
        "icd_version",
        "long_title",
    )
)

for name, df in [
    ("dim_patient", dim_patient),
    ("dim_admission", dim_admission),
    ("dim_icd_diagnosis", dim_icd),
]:
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fq_table(GOLD_SCHEMA, name))
    )
    print(f"gold.{name}: {df.count()} rows")

print("Gold dimensions complete")
