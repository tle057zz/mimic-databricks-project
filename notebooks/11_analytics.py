# Databricks notebook source
# MAGIC %md
# MAGIC # 11 — Analytics
# MAGIC Sample gold-layer analytics for reporting / Power BI.

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## Admissions by type

# COMMAND ----------

spark.sql(
    f"""
    SELECT admission_type, COUNT(*) AS n_admissions
    FROM {fq_table(GOLD_SCHEMA, "dim_admission")}
    GROUP BY admission_type
    ORDER BY n_admissions DESC
    """
).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Top diagnoses

# COMMAND ----------

spark.sql(
    f"""
    SELECT icd_code, long_title, COUNT(*) AS n
    FROM {fq_table(GOLD_SCHEMA, "fact_diagnoses")}
    GROUP BY icd_code, long_title
    ORDER BY n DESC
    LIMIT 20
    """
).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prescription volume by drug

# COMMAND ----------

spark.sql(
    f"""
    SELECT drug, COUNT(*) AS n_rx
    FROM {fq_table(GOLD_SCHEMA, "fact_prescriptions")}
    WHERE drug IS NOT NULL
    GROUP BY drug
    ORDER BY n_rx DESC
    LIMIT 20
    """
).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transfers by care unit

# COMMAND ----------

spark.sql(
    f"""
    SELECT careunit, COUNT(*) AS n_transfers
    FROM {fq_table(GOLD_SCHEMA, "fact_transfers")}
    GROUP BY careunit
    ORDER BY n_transfers DESC
    """
).display()
