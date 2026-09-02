# Raw landing zone

Seven scoped CSV files from the MIMIC-IV demo `hosp/` folder, committed to this repository.

| File | Description |
|------|-------------|
| `patients.csv` | Patient demographics |
| `admissions.csv` | Hospital admissions |
| `transfers.csv` | Ward/ICU transfers |
| `diagnoses_icd.csv` | ICD diagnoses |
| `procedures_icd.csv` | ICD procedures |
| `prescriptions.csv` | Medications |
| `d_icd_diagnoses.csv` | ICD diagnosis lookup |

Source: [MIMIC-IV Clinical Database Demo v2.2](https://physionet.org/content/mimic-iv-demo/2.2/) — copy from the `hosp/` folder of the PhysioNet download.

On Databricks, upload these files to the Unity Catalog Volume used by `01_bronze_ingestion`.
