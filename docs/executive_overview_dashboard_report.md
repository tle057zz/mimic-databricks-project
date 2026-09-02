# Executive Overview Dashboard — Analysis Report

**Dashboard:** [MIMIC Analytics Dashboard — Executive Overview](https://app.powerbi.com/view?r=eyJrIjoiYWIwMDQ2MmItZTk2YS00NmRkLTlmNmUtMDljMjUwYTY1MWU0IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)  
**Data source:** `data/databricks_output/exports/vw_admission_overview.csv` (275 rows, exported from `workspace.mimic.vw_admission_overview`)  
**Verification:** All KPIs below were recomputed in Python from the export CSV and match the Power BI dashboard exactly.

---

## Executive Summary

The Executive Overview page provides a hospital-wide snapshot of 100 deidentified patients and 275 admissions from the MIMIC-IV demo dataset. Emergency and observation pathways dominate admission volume, while length of stay varies sharply by admission type. The population skews toward older adults (ages 50–79), and roughly one in five admissions is flagged as a 30-day readmission.

---

## KPI Verification

| Metric | Dashboard | Verified (CSV) | DAX Measure |
|--------|-----------|----------------|-------------|
| Total Patients | 100 | **100** | `DISTINCTCOUNT(patient_id)` |
| Total Admissions | 275 | **275** | `DISTINCTCOUNT(admission_id)` |
| Average LOS | 6.88 days | **6.88 days** | `AVERAGE(length_of_stay_days)` |
| Readmission Rate | 19.3% | **19.3%** (53 / 275) | `DIVIDE([30-Day Readmissions], [Total Admissions], 0)` |
| In-Hospital Deaths | 15 | **15** | `CALCULATE(DISTINCTCOUNT(admission_id), died_in_hospital = TRUE())` |

Additional derived metric: **2.75 admissions per patient** on average (275 ÷ 100), with a median of 1 and a maximum of 20 admissions for a single patient.

---

## Key Findings

### 1. Emergency admissions drive volume

**EW EMER.** is the single largest admission type with **104 admissions (37.8%)** of the total, more than double the next category.

| Admission Type | Admissions | Share |
|----------------|------------|-------|
| EW EMER. | 104 | 37.8% |
| OBSERVATION ADMIT | 45 | 16.4% |
| URGENT | 38 | 13.8% |
| EU OBSERVATION | 30 | 10.9% |
| SURGICAL SAME DAY ADMISSION | 18 | 6.5% |
| DIRECT EMER. | 15 | 5.5% |
| ELECTIVE | 13 | 4.7% |
| DIRECT OBSERVATION | 7 | 2.5% |
| AMBULATORY OBSERVATION | 5 | 1.8% |

Observation-related types (OBSERVATION ADMIT, EU OBSERVATION, DIRECT OBSERVATION, AMBULATORY OBSERVATION) together account for **87 admissions (31.6%)**, indicating a substantial short-stay / monitoring pathway alongside traditional emergency volume.

### 2. High volume does not mean longest stays

Although **EW EMER.** has the most admissions, it does not have the longest average length of stay. **URGENT** admissions average **9.9 days** — the highest — followed by **DIRECT EMER.** at **9.4 days**.

| Admission Type | Avg LOS (days) |
|----------------|----------------|
| URGENT | 9.9 |
| DIRECT EMER. | 9.4 |
| ELECTIVE | 8.2 |
| OBSERVATION ADMIT | 8.2 |
| EW EMER. | 7.3 |
| SURGICAL SAME DAY ADMISSION | 5.7 |
| DIRECT OBSERVATION | 1.4 |
| AMBULATORY OBSERVATION | 1.0 |
| EU OBSERVATION | 0.9 |

Observation types cluster at the bottom (0.9–1.4 days), confirming they function as short-stay pathways. Resource planning should treat emergency volume (EW EMER.) and inpatient intensity (URGENT, DIRECT EMER.) as separate operational concerns.

### 3. Patient population skews older

Patients aged **50–79** account for **62 of 100 patients (62%)**. The **50–64** group is the largest single band with **34 patients**, followed by **65–79** with **28**.

| Age Group | Patients |
|-----------|----------|
| 50–64 | 34 |
| 65–79 | 28 |
| 80+ | 16 |
| 35–49 | 15 |
| 18–34 | 7 |

Gender split: **57 male**, **43 female** (unique patients).

### 4. Insurance mix is dominated by OTHER and Medicare

| Insurance | Admissions | Share |
|-----------|------------|-------|
| OTHER | 149 | 54.18% |
| MEDICARE | 104 | 37.82% |
| MEDICAID | 22 | 8.00% |

Medicare and OTHER together cover **92%** of admissions, consistent with an older patient population. Medicaid represents a small minority at 8%.

### 5. Readmissions and mortality

- **53 admissions (19.3%)** are flagged as **30-day readmissions**, validated against `is_30_day_readmission = TRUE`.
- **15 in-hospital deaths** represent **5.5%** of all admissions (`died_in_hospital = TRUE`).
- With 2.75 average admissions per patient, a subset of patients are high utilizers (max 20 admissions for one patient), which likely drives the readmission rate.

### 6. Admissions over time (deidentified years)

Admission dates in MIMIC are shifted for deidentification, so years (2110–2201) are not calendar years. Volume is spread across many years with intermittent peaks — the highest single-year count is **2148 with 13 admissions**, followed by **2147 with 12**. There is no monotonic trend; the pattern reflects the demo subset's synthetic timeline rather than real epidemiology.

---

## Dashboard Filters

The Executive Overview page exposes slicers for:

- **age_group** — 18-34, 35-49, 50-64, 65-79, 80+
- **admission_type** — all 9 types listed above
- **gender** — F, M

Cross-filtering these slicers recalculates all KPI cards and visuals on the page.

---

## Data Lineage

```
hosp/admissions.csv  →  Bronze  →  Silver  →  Gold (fact_admission)
                                              →  vw_admission_overview (SQL view)
                                              →  Power BI Executive Overview page
```

DAX measures on this page query `vw_admission_overview` via Databricks SQL Warehouse. See [`powerbi/mimic_powerbi_dax_measures.md`](../powerbi/mimic_powerbi_dax_measures.md) for full measure definitions.

---

## Verification Script

KPIs were recomputed with:

```python
import pandas as pd

df = pd.read_csv("data/databricks_output/exports/vw_admission_overview.csv")

total_patients = df["patient_id"].nunique()          # 100
total_admissions = df["admission_id"].nunique()      # 275
avg_los = df["length_of_stay_days"].mean()           # 6.88
deaths = df.loc[df["died_in_hospital"], "admission_id"].nunique()  # 15
readmits = df.loc[df["is_30_day_readmission"], "admission_id"].nunique()  # 53
readmission_rate = readmits / total_admissions       # 0.193
```

Full breakdown output is saved in `data/databricks_output/exports/admission_analysis.json`.
