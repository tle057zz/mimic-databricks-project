# MIMIC Databricks Project

Medallion-architecture pipeline (Bronze → Silver → Gold) over scoped tables from the [MIMIC-IV Clinical Database Demo v2.2](https://physionet.org/content/mimic-iv-demo/2.2/).

**[Reports home](report/index.html)** · **[Project report](report/report.html)** · **[Dashboard 1](report/dashboard_01_hospital_overview.html)** · **[Dashboard 2](report/dashboard_02_diagnosis_analysis.html)** · **[Dashboard 3](report/dashboard_03_medication_analysis.html)** · **[Dashboard 4](report/dashboard_04_hospital_operations.html)** · **[Power BI](https://app.powerbi.com/view?r=eyJrIjoiYWIwMDQ2MmItZTk2YS00NmRkLTlmNmUtMDljMjUwYTY1MWU0IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)**

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

The full PhysioNet download includes `hosp/` (hospital tables) and `icu/` (ICU tables). **This project uses 7 tables from `hosp/` only** — ICU data is out of scope.

### Raw Data (`data/raw/`)

The seven scoped source files are stored in `data/raw/` and committed to this repository. They were extracted from the `hosp/` folder of the [PhysioNet download](https://physionet.org/content/mimic-iv-demo/2.2/).

| File | Rows | Size | Description |
|------|------|------|-------------|
| `patients.csv` | 100 | 3.5 KB | Patient demographics |
| `admissions.csv` | 275 | 46 KB | Hospital admissions |
| `transfers.csv` | 1,190 | 100 KB | Ward/ICU transfers |
| `diagnoses_icd.csv` | 4,506 | 126 KB | ICD diagnoses |
| `procedures_icd.csv` | 722 | 28 KB | ICD procedures |
| `prescriptions.csv` | 18,087 | 3.0 MB | Medications |
| `d_icd_diagnoses.csv` | 109,775 | 8.4 MB | ICD diagnosis lookup (reference) |

Row counts exclude the header line. On Databricks, these files are uploaded to a Unity Catalog Volume (`raw_data`) for bronze ingestion.

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

## Repository Structure

```
.
├── data/raw/                 # Scoped CSV source files (7 tables)
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
│   └── mimic_powerbi_dax_measures.md
├── docs/                     # Project documentation
├── report/                   # HTML reports (start at report/index.html)
│   ├── index.html
│   ├── report.html
│   └── dashboard_01_hospital_overview.html
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

**[MIMIC Analytics Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYWIwMDQ2MmItZTk2YS00NmRkLTlmNmUtMDljMjUwYTY1MWU0IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)**

Power BI connects to the `workspace.mimic` reporting views (`vw_admission_overview`, `vw_diagnosis_analysis`, etc.) created by `06_reporting_views`. Source files and connection notes are in the `powerbi/` folder.

**Dashboard analysis:** [Dashboard 1](report/dashboard_01_hospital_overview.html) · [Dashboard 2](report/dashboard_02_diagnosis_analysis.html) · [Dashboard 3](report/dashboard_03_medication_analysis.html) · [Dashboard 4](report/dashboard_04_hospital_operations.html) — verified against CSV exports in `data/databricks_output/exports/`.

### Dashboard pages

| # | Page | Data View | Report |
|---|------|-----------|--------|
| 1 | Hospital Overview | `vw_admission_overview` | [report/dashboard_01_hospital_overview.html](report/dashboard_01_hospital_overview.html) |
| 2 | Diagnosis Analysis | `vw_diagnosis_analysis` | [report/dashboard_02_diagnosis_analysis.html](report/dashboard_02_diagnosis_analysis.html) |
| 3 | Medication Analysis | `vw_prescription_analysis` | [report/dashboard_03_medication_analysis.html](report/dashboard_03_medication_analysis.html) |
| 4 | Hospital Operations | `vw_transfer_analysis` + `vw_procedure_analysis` | [report/dashboard_04_hospital_operations.html](report/dashboard_04_hospital_operations.html) |

## DAX Measures

The dashboard uses **18 DAX measures** across four report pages. Canonical definitions are in [`powerbi/mimic_powerbi_dax_measures.md`](powerbi/mimic_powerbi_dax_measures.md).

### 1. Hospital Overview

```dax
Total Patients =
DISTINCTCOUNT(vw_admission_overview[patient_id])
```

```dax
Total Admissions =
DISTINCTCOUNT(vw_admission_overview[admission_id])
```

```dax
Average LOS =
AVERAGE(vw_admission_overview[length_of_stay_days])
```

```dax
In-Hospital Deaths =
CALCULATE(
    DISTINCTCOUNT(vw_admission_overview[admission_id]),
    vw_admission_overview[died_in_hospital] = TRUE()
)
```

```dax
30-Day Readmissions =
CALCULATE(
    DISTINCTCOUNT(vw_admission_overview[admission_id]),
    vw_admission_overview[is_30_day_readmission] = TRUE()
)
```

```dax
Readmission Rate =
DIVIDE(
    [30-Day Readmissions],
    [Total Admissions],
    0
)
```

> Format `Readmission Rate` as a percentage.

### 2. Diagnosis Analysis

```dax
Diagnosis Records =
COUNTROWS(vw_diagnosis_analysis)
```

```dax
Diagnosed Patients =
DISTINCTCOUNT(vw_diagnosis_analysis[patient_id])
```

```dax
Primary Diagnoses =
CALCULATE(
    COUNTROWS(vw_diagnosis_analysis),
    vw_diagnosis_analysis[is_primary_diagnosis] = TRUE()
)
```

### 3. Medication Analysis

```dax
Total Prescriptions =
COUNTROWS(vw_prescription_analysis)
```

```dax
Patients Receiving Medication =
DISTINCTCOUNT(vw_prescription_analysis[patient_id])
```

```dax
Unique Drugs =
DISTINCTCOUNT(vw_prescription_analysis[drug_name])
```

```dax
Avg Prescription Duration =
AVERAGE(
    vw_prescription_analysis[prescription_duration_days]
)
```

### 4. Hospital Operations

```dax
Total Transfers =
COUNTROWS(vw_transfer_analysis)
```

```dax
Transferred Patients =
DISTINCTCOUNT(vw_transfer_analysis[patient_id])
```

```dax
Avg Transfer Duration =
AVERAGE(vw_transfer_analysis[transfer_duration_hours])
```

```dax
Total Procedures =
COUNTROWS(vw_procedure_analysis)
```

```dax
Procedure Patients =
DISTINCTCOUNT(vw_procedure_analysis[patient_id])
```

## Quick Start

### Clone and explore

```bash
git clone <your-repo-url>
cd mimic-databricks-project
open report/index.html      # reports hub — navigate to all HTML pages
```

Source CSV files are already in `data/raw/`. No additional download is required to inspect the data locally.

### Databricks setup

1. Upload the seven CSV files from `data/raw/` to a Unity Catalog Volume at `workspace.mimic.raw_data`.
2. Import or sync the notebooks from `notebooks/databricks_notebooks/`.
3. Create the **MIMIC Daily ETL Pipeline** job with tasks `01` → `06` in sequence.
4. Run the job, then connect Power BI to the SQL Warehouse querying `workspace.mimic` views.

### Re-downloading source data from PhysioNet

If you need to refresh `data/raw/` from the original download:

```bash
# Download the full demo dataset
wget -r -N -c -np https://physionet.org/files/mimic-iv-demo/2.2/

# Copy the 7 scoped hosp/ tables into data/raw/
for t in patients admissions transfers diagnoses_icd procedures_icd prescriptions d_icd_diagnoses; do
  cp mimic-iv-demo/2.2/hosp/${t}.csv.gz data/raw/
  gzip -dc "data/raw/${t}.csv.gz" > "data/raw/${t}.csv"
done
```

## Citation

When using this dataset, cite:

> Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV Clinical Database Demo (version 2.2). *PhysioNet*. https://doi.org/10.13026/dp1f-ex47

See also the [MIMIC-IV online documentation](https://mimic.mit.edu/) for schema details and clinical concept derivations.
