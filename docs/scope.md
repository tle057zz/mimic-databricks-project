# Scope & Source Tables

Final project bronze scope from MIMIC-IV demo `hosp/`:

| Table | File | Role |
|-------|------|------|
| patients | `patients.csv.gz` | Demographics |
| admissions | `admissions.csv.gz` | Hospital stays |
| transfers | `transfers.csv.gz` | Ward/ICU moves |
| diagnoses_icd | `diagnoses_icd.csv.gz` | Diagnoses |
| procedures_icd | `procedures_icd.csv.gz` | Procedures |
| prescriptions | `prescriptions.csv.gz` | Medications |
| d_icd_diagnoses | `d_icd_diagnoses.csv.gz` | ICD lookup |

## Keys

- `subject_id` — patient
- `hadm_id` — admission
- `transfer_id` — transfer event
- `icd_code` (+ `icd_version`) — diagnosis dictionary
