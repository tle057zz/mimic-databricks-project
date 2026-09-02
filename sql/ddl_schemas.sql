-- DDL placeholders for Gold dimensional model
-- Adjust catalog/schema names to match 00_setup.py

CREATE CATALOG IF NOT EXISTS mimic;
CREATE SCHEMA IF NOT EXISTS mimic.bronze;
CREATE SCHEMA IF NOT EXISTS mimic.silver;
CREATE SCHEMA IF NOT EXISTS mimic.gold;

-- Example gold table stubs (created by notebooks 08/09 as Delta)
-- dim_patient, dim_admission, dim_icd_diagnosis
-- fact_diagnoses, fact_procedures, fact_prescriptions, fact_transfers
