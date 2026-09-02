# Dashboard 4 — Hospital Operations

**Power BI page:** Hospital Operations (Page 4 of 4)  
**Data views:** `vw_transfer_analysis` + `vw_procedure_analysis`  
**Live dashboard:** [MIMIC Analytics Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYWIwMDQ2MmItZTk2YS00NmRkLTlmNmUtMDljMjUwYTY1MWU0IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)  
**Exports verified:** `vw_transfer_analysis.csv` (1,190 rows) · `vw_procedure_analysis.csv` (722 rows)  
**HTML report:** [report/dashboard_04_hospital_operations.html](../report/dashboard_04_hospital_operations.html)

---

## 1. Purpose

The Hospital Operations page combines patient movement and clinical procedure data — tracking transfers between care units, event types, transfer durations, and procedure volumes.

**Questions this page answers:**

1. How many transfer events occur and how long do patients stay in each unit?
2. Which care units see the most traffic?
3. What types of transfer events dominate (admit, transfer, discharge, ED)?
4. How many procedures are performed, and which codes and age groups lead?

---

## 2. Data Sources

### vw_transfer_analysis

| Column | Description |
|--------|-------------|
| `transfer_id` | Unique transfer event identifier |
| `patient_id` / `admission_id` | Patient and admission keys |
| `event_type` | ADMIT · TRANSFER · DISCHARGE · ED |
| `care_unit` | Hospital unit name (blank for discharge events) |
| `transfer_duration_hours` | Hours between transfer in and out |
| `admission_type`, `gender`, `age_group` | Admission demographics |

### vw_procedure_analysis

| Column | Description |
|--------|-------------|
| `procedure_key` | Unique procedure row key |
| `procedure_code` | ICD-9 or ICD-10 procedure code |
| `icd_version` | 9 or 10 |
| `is_primary_procedure` | TRUE for sequence 1 |
| `procedure_date` | Procedure timestamp (deidentified) |
| `admission_type`, `gender`, `age_group` | Admission demographics |

---

## 3. KPI Cards

| Card | Value | Source | DAX |
|------|-------|--------|-----|
| Total Transfers | 1,190 (1K in PBI) | `vw_transfer_analysis` | `COUNTROWS(...)` |
| Transferred Patients | 100 | `vw_transfer_analysis` | `DISTINCTCOUNT(patient_id)` |
| Avg Transfer Duration | 51.22 hrs | `vw_transfer_analysis` | `AVERAGE(transfer_duration_hours)` |
| Total Procedures | 722 | `vw_procedure_analysis` | `COUNTROWS(...)` |
| Procedure Patients | 92 | `vw_procedure_analysis` | `DISTINCTCOUNT(patient_id)` |

**Derived:** 4.3 transfer events per admission; 8 patients without procedure records; 187 admissions (68%) have procedures.

---

## 4. Transfer Analysis

### Visual 1 — Transfers by care_unit

| Care Unit | Transfers |
|-----------|-----------|
| (Blank) | 275 |
| EMERGENCY DEPARTMENT | 236 |
| MEDICINE | 77 |
| MED/SURG | 48 |
| NEUROLOGY | 46 |

**Finding:** Blank = discharge events (one per admission). ED leads named units at 236.

### Visual 2 — Avg transfer duration by care_unit

| Care Unit | Avg Hours |
|-----------|-----------|
| MEDICINE/CARDIOLOGY INTERMEDIATE | 332.21 |
| PSYCHIATRY | 195.85 |
| HEMATOLOGY/ONCOLOGY | 126.45 |
| VASCULAR | 105.09 |
| CORONARY CARE UNIT (CCU) | 96.00 |

### Visual 3 — Transfers by event_type

| Event Type | Count | Share |
|------------|-------|-------|
| TRANSFER | 404 | 33.95% |
| DISCHARGE | 275 | 23.11% |
| ADMIT | 275 | 23.11% |
| ED | 236 | 19.83% |

---

## 5. Procedure Analysis

### Visual 4 — Procedures by age_group

| Age Group | Procedures |
|-----------|------------|
| 50–64 | 286 |
| 65–79 | 208 |
| 35–49 | 130 |
| 80+ | 62 |
| 18–34 | 36 |

### Visual 5 — Procedures by procedure_code

| Code | Count | ICD |
|------|-------|-----|
| 02HV33Z | 23 | 10 |
| 3897 | 22 | 9 |
| 966 | 18 | 9 |
| 9671 | 15 | 9 |
| 3893 / 3961 | 13 each | 9 |

ICD-9: 401 (55.5%) · ICD-10: 321 (44.5%)

---

## 6. DAX Measures

```DAX
Total Transfers = COUNTROWS(vw_transfer_analysis)
Transferred Patients = DISTINCTCOUNT(vw_transfer_analysis[patient_id])
Avg Transfer Duration = AVERAGE(vw_transfer_analysis[transfer_duration_hours])
Total Procedures = COUNTROWS(vw_procedure_analysis)
Procedure Patients = DISTINCTCOUNT(vw_procedure_analysis[patient_id])
```

---

## 7. Key Takeaways

1. **1,190 transfer events** — 4.3 per admission; all 100 patients tracked.
2. **TRANSFER events lead** at 34%; ADMIT and DISCHARGE each = 275 (one per admission).
3. **ED dominates named units** — 236 events; shortest avg duration (~3.4 hrs).
4. **Longest stays** — Medicine/Cardiology Intermediate (~332 hrs).
5. **722 procedures** — 92 patients; 50–64 age group leads at 39.6%.
6. **Top codes** — catheter insertion, ventilation, enteral nutrition.

---

## 8. Verification

```python
import pandas as pd
tx = pd.read_csv("data/databricks_output/exports/vw_transfer_analysis.csv")
pr = pd.read_csv("data/databricks_output/exports/vw_procedure_analysis.csv")
assert len(tx) == 1190
assert tx["patient_id"].nunique() == 100
assert round(tx["transfer_duration_hours"].mean(), 2) == 51.22
assert len(pr) == 722
assert pr["patient_id"].nunique() == 92
```

Machine-readable output: `data/databricks_output/exports/hospital_operations_analysis.json`
