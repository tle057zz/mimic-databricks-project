# MIMIC Databricks Project

Medallion-architecture pipeline (Bronze → Silver → Gold) over scoped tables from the [MIMIC-IV Clinical Database Demo v2.2](https://physionet.org/content/mimic-iv-demo/2.2/).

## Technologies & Concepts

The project demonstrates practical use of:

| Technology / Concept | Application |
|---------------------|-------------|
| Databricks | Lakehouse development environment |
| Unity Catalog | Data organisation and governance |
| Unity Catalog Volumes | Raw file storage |
| Apache Spark | Distributed data processing |
| PySpark | ETL transformations |
| Spark SQL | Analytical querying |
| Delta Lake | Managed analytical tables |
| Medallion Architecture | Bronze, Silver and Gold processing |
| Window Functions | 30-day readmission logic |
| Data Quality Testing | Validation and integrity checks |
| Dimensional Modelling | Facts and dimensions |
| Databricks Jobs | Pipeline / DAG orchestration |
| SQL Warehouse | BI query endpoint |
| Power BI | Interactive analytics and dashboards |
| DAX | Business metrics |

## Data Source

| | |
|---|---|
| **Dataset** | MIMIC-IV Clinical Database Demo |
| **Version** | 2.2 (Jan 31, 2023) |
| **Publisher** | PhysioNet |
| **URL** | https://physionet.org/content/mimic-iv-demo/2.2/ |
| **DOI** | [10.13026/dp1f-ex47](https://doi.org/10.13026/dp1f-ex47) |
| **License** | Open Data Commons Open Database License v1.0 |

The demo is an openly available subset of [MIMIC-IV](https://mimic.mit.edu/) — deidentified electronic health records from Beth Israel Deaconess Medical Center. It contains **100 patients** with the same schema as the full database, but excludes free-text clinical notes. Tables without patient-level data (prefixed `d_`) are included in full.

### Download Layout

The dataset was downloaded from PhysioNet into the parent workspace:

```
mimic-iv-clinical-database-demo-2.2/
├── hosp/                   # Hospital-level tables (admissions, labs, meds, etc.)
├── icu/                    # ICU-level tables (chartevents, inputevents, etc.)
├── demo_subject_id.csv     # List of 100 subject_id in the demo subset
├── README.txt
├── LICENSE.txt
└── mimic-databricks-project/
    └── data/raw/           # Project landing zone (see below)
```

This project uses **7 tables from `hosp/`** only. The `icu/` folder is available in the download but is out of scope for the current pipeline.

### Project Raw Data (`data/raw/`)

Scoped source files are landed in `data/raw/` for bronze ingestion. Each table is available as:

- **`.csv.gz`** — symlinks to the original files in `../../hosp/` (as downloaded from PhysioNet)
- **`.csv`** — uncompressed exports for local inspection and tools that don't read gzip

| File | Source | Rows | Size | Description |
|------|--------|------|------|-------------|
| `patients.csv` | `hosp/patients.csv.gz` | 100 | 3.5 KB | Patient demographics |
| `admissions.csv` | `hosp/admissions.csv.gz` | 275 | 46 KB | Hospital admissions |
| `transfers.csv` | `hosp/transfers.csv.gz` | 1,190 | 100 KB | Ward/ICU transfers |
| `diagnoses_icd.csv` | `hosp/diagnoses_icd.csv.gz` | 4,506 | 126 KB | ICD diagnoses |
| `procedures_icd.csv` | `hosp/procedures_icd.csv.gz` | 722 | 28 KB | ICD procedures |
| `prescriptions.csv` | `hosp/prescriptions.csv.gz` | 18,087 | 3.0 MB | Medications |
| `d_icd_diagnoses.csv` | `hosp/d_icd_diagnoses.csv.gz` | 109,775 | 8.4 MB | ICD diagnosis lookup (reference) |

Row counts exclude the header line.

## Source Tables (Bronze)

| Table | Description | Primary Key | Foreign Keys |
|-------|-------------|-------------|--------------|
| `patients` | Patient demographics | `subject_id` | — |
| `admissions` | Hospital admissions | `hadm_id` | `subject_id` |
| `transfers` | Ward/ICU transfers | `transfer_id` | `subject_id`, `hadm_id` |
| `diagnoses_icd` | Diagnoses | — | `subject_id`, `hadm_id`, `icd_code` |
| `procedures_icd` | Procedures | — | `subject_id`, `hadm_id`, `icd_code` |
| `prescriptions` | Medications | — | `subject_id`, `hadm_id` |
| `d_icd_diagnoses` | ICD lookup | `icd_code` | — |

## Project Structure

```
mimic-databricks-project/
├── data/raw/                 # Scoped CSV / CSV.GZ from hosp/
├── notebooks/
│   ├── databricks_notebooks/ # Deployed notebooks (HTML exports from Databricks)
│   │   ├── 01_bronze_ingestion.html
│   │   ├── 02_silver_transformations.html
│   │   ├── 03_gold_dimensions.html
│   │   ├── 04_gold_facts.html
│   │   ├── 05_data_quality.html
│   │   ├── 06_reporting_views.html
│   │   ├── 07_business_analysis.html
│   │   └── Inspect Delta Lake features.html
│   ├── 00_setup.py           # Local / dev notebook stubs
│   ├── 01_bronze_ingestion.py
│   ├── 02_silver_patients.py … 11_analytics.py
├── sql/                      # DDL / standalone SQL
├── powerbi/                  # Power BI reports / connections
├── docs/                     # Project documentation
└── README.md
```

The `databricks_notebooks/` folder contains HTML exports of the notebooks deployed and run in Databricks. The numbered `.py` files in `notebooks/` are local development stubs that mirror the same medallion flow.

## Databricks ETL Pipeline

The production pipeline runs as a Databricks Job named **MIMIC Daily ETL Pipeline**. Tasks execute sequentially on **Serverless** compute, each depending on the previous step completing successfully.

```
Bronze → silver → dimensions → facts → quality → views
```

| Task | Notebook | Layer | Description |
|------|----------|-------|-------------|
| Bronze | `01_bronze_ingestion` | Bronze | Create `workspace.mimic` schema; load raw CSV from Unity Catalog Volume into Delta tables |
| silver | `02_silver_transformations` | Silver | Clean, type-cast, deduplicate, and enforce referential integrity across all 7 entities |
| dimensions | `03_gold_dimensions` | Gold | Build `dim_patient` and `dim_diagnosis` dimension tables |
| facts | `04_gold_facts` | Gold | Build fact tables with business logic (e.g. readmission flags on admissions) |
| quality | `05_data_quality` | QA | Run validation checks; persist results to `data_quality_results` |
| views | `06_reporting_views` | Gold | Create SQL views for Power BI and ad-hoc reporting |

All Delta tables and views are stored under **`workspace.mimic`**.

### Run History

The job has been run manually with all tasks succeeding. Typical end-to-end duration is **~1–3 minutes** on Serverless for the demo dataset.

## Databricks Notebooks

### Pipeline notebooks (in job)

| Notebook | Output tables / views |
|----------|----------------------|
| `01_bronze_ingestion` | `bronze_patients`, `bronze_admissions`, `bronze_transfers`, `bronze_diagnoses`, `bronze_procedures`, `bronze_prescriptions`, `bronze_diagnosis_lookup` |
| `02_silver_transformations` | `silver_patients`, `silver_admissions`, `silver_transfers`, `silver_diagnoses`, `silver_procedures`, `silver_prescriptions`, `silver_diagnosis_lookup` |
| `03_gold_dimensions` | `dim_patient`, `dim_diagnosis` |
| `04_gold_facts` | `fact_admission` (with readmission logic), `fact_diagnosis`, `fact_procedure`, `fact_prescription`, `fact_transfer` |
| `05_data_quality` | `data_quality_results` — checks for invalid dates, orphan admissions, orphan diagnoses |
| `06_reporting_views` | `vw_admission_overview`, `vw_diagnosis_analysis`, `vw_prescription_analysis`, `vw_transfer_analysis`, `vw_procedure_analysis` |

### Supporting notebooks (not in job)

| Notebook | Purpose |
|----------|---------|
| `07_business_analysis` | Exploratory KPIs — admissions by type, patients by age group, top diagnoses |
| `Inspect Delta Lake features` | Utility notebook for inspecting Delta table metadata and history |

## Suggested Run Order

**Databricks (production):** trigger the **MIMIC Daily ETL Pipeline** job, or run notebooks `01` → `06` in order.

**Local development:** use the stub notebooks in `notebooks/`:

1. `00_setup` — catalogs, schemas, paths, shared helpers
2. `01_bronze_ingestion` — load the 7 source tables into Bronze
3. `02`–`07` — clean and conform each entity into Silver
4. `08_gold_dimensions` / `09_gold_facts` — dimensional model
5. `10_data_quality` — validation checks
6. `11_analytics` — exploratory / reporting queries

## Power BI Dashboard

The published dashboard built from the Gold layer reporting views is available here:

**[MIMIC Analytics Dashboard](https://app.powerbi.com/view?r=eyJrIjoiOWFjMmJiNjktMDY1OC00OGFjLTg0ODgtNTkwYzBiYmEwYjc2IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)**

Power BI connects to the `workspace.mimic` reporting views (`vw_admission_overview`, `vw_diagnosis_analysis`, etc.) created by `06_reporting_views`. Source files and connection notes are in the `powerbi/` folder.

## Quick Start (local / Databricks)

If `data/raw/` is not already populated, symlink the scoped tables from the downloaded `hosp/` folder:

```bash
cd mimic-databricks-project
ln -sf ../../hosp/patients.csv.gz data/raw/
ln -sf ../../hosp/admissions.csv.gz data/raw/
ln -sf ../../hosp/transfers.csv.gz data/raw/
ln -sf ../../hosp/diagnoses_icd.csv.gz data/raw/
ln -sf ../../hosp/procedures_icd.csv.gz data/raw/
ln -sf ../../hosp/prescriptions.csv.gz data/raw/
ln -sf ../../hosp/d_icd_diagnoses.csv.gz data/raw/
```

To create uncompressed CSV copies (optional):

```bash
for t in patients admissions transfers diagnoses_icd procedures_icd prescriptions d_icd_diagnoses; do
  gzip -dc "../../hosp/${t}.csv.gz" > "data/raw/${t}.csv"
done
```

Then run notebooks in order on Databricks (or adapt paths for local Spark).

## Citation

When using this dataset, cite:

> Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV Clinical Database Demo (version 2.2). *PhysioNet*. https://doi.org/10.13026/dp1f-ex47

See also the [MIMIC-IV online documentation](https://mimic.mit.edu/) for schema details and clinical concept derivations.
