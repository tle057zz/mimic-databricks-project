# Databricks notebook source
# MAGIC %md
# MAGIC # 10 — Data Quality
# MAGIC Referential integrity and null checks across Bronze / Silver / Gold.

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

from pyspark.sql import functions as F

checks = []


def add_check(name: str, ok: bool, detail: str = "") -> None:
    checks.append({"check": name, "passed": ok, "detail": detail})
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


patients = spark.table(fq_table(SILVER_SCHEMA, "patients"))
admissions = spark.table(fq_table(SILVER_SCHEMA, "admissions"))
diagnoses = spark.table(fq_table(SILVER_SCHEMA, "diagnoses"))

# PK uniqueness
add_check(
    "patients.subject_id unique",
    patients.count() == patients.select("subject_id").distinct().count(),
)
add_check(
    "admissions.hadm_id unique",
    admissions.count() == admissions.select("hadm_id").distinct().count(),
)

# FK: admissions.subject_id → patients
orphan_adm = admissions.join(
    patients.select("subject_id"), on="subject_id", how="left_anti"
).count()
add_check("admissions → patients FK", orphan_adm == 0, f"orphans={orphan_adm}")

# FK: diagnoses → admissions
orphan_dx = diagnoses.join(
    admissions.select("subject_id", "hadm_id"),
    on=["subject_id", "hadm_id"],
    how="left_anti",
).count()
add_check("diagnoses → admissions FK", orphan_dx == 0, f"orphans={orphan_dx}")

# Null PKs
add_check(
    "patients.subject_id not null",
    patients.filter(F.col("subject_id").isNull()).count() == 0,
)

dq = spark.createDataFrame(checks)
(
    dq.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fq_table(GOLD_SCHEMA, "data_quality_results"))
)

failed = [c for c in checks if not c["passed"]]
print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed")
if failed:
    raise AssertionError(f"{len(failed)} data quality check(s) failed")
