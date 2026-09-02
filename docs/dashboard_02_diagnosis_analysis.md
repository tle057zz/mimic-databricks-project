# Dashboard 2 — Diagnosis Analysis

**Power BI page:** Diagnosis Analysis (Page 2 of 4)  
**Data view:** `vw_diagnosis_analysis`  
**Live dashboard:** [MIMIC Analytics Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYWIwMDQ2MmItZTk2YS00NmRkLTlmNmUtMDljMjUwYTY1MWU0IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)  
**Export verified:** `data/databricks_output/exports/vw_diagnosis_analysis.csv` (4,506 rows × 14 columns)  
**HTML report:** [report/dashboard_02_diagnosis_analysis.html](../report/dashboard_02_diagnosis_analysis.html)

---

## 1. Purpose

The Diagnosis Analysis page explores ICD-coded clinical conditions across admissions — distinguishing primary admitting diagnoses from secondary comorbidities, and linking diagnosis patterns to patient demographics and length of stay.

**Questions this page answers:**

1. How many diagnosis records exist per patient and admission?
2. What are the most common primary and secondary diagnoses?
3. How do diagnosis volumes vary by age group and gender?
4. Which conditions are associated with the longest hospital stays?

All visuals query a single Gold-layer SQL view — `workspace.mimic.vw_diagnosis_analysis` — connected via Databricks SQL Warehouse.

---

## 2. Data Source

### View schema

| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | int | Patient identifier |
| `admission_id` | int | Hospital admission identifier |
| `diagnosis_key` | string | Unique diagnosis row key |
| `icd_code` | string | ICD-9 or ICD-10 code |
| `icd_version` | int | 9 or 10 |
| `diagnosis_sequence` | int | Order on the admission (1 = primary) |
| `is_primary_diagnosis` | bool | TRUE when sequence = 1 |
| `diagnosis_title` | string | Human-readable ICD description |
| `admission_date` | date | Admission timestamp (deidentified) |
| `admission_type` | string | URGENT, EW EMER., ELECTIVE, etc. |
| `length_of_stay_days` | float | Discharge − admission in days |
| `gender` | string | F / M |
| `anchor_age` | int | Patient age at anchor year |
| `age_group` | string | 18-34, 35-49, 50-64, 65-79, 80+ |

### Data lineage

```
hosp/diagnoses_icd.csv + hosp/d_icd_diagnoses.csv + hosp/admissions.csv + hosp/patients.csv
  → Bronze → Silver → Gold (fact_diagnosis)
  → SQL view (vw_diagnosis_analysis)
  → Power BI Diagnosis Analysis page
```

---

## 3. KPI Cards

| Card | Value | DAX Measure |
|------|-------|-------------|
| Diagnosed Patients | 100 | `DISTINCTCOUNT(patient_id)` |
| Diagnosis Records | 4,506 (5K in PBI) | `COUNTROWS(vw_diagnosis_analysis)` |
| Primary Diagnoses | 275 | `CALCULATE(COUNTROWS(...), is_primary_diagnosis = TRUE())` |

All three values **verified against the CSV export** — exact match.

**Derived metrics:**

- 16.4 diagnosis records per admission (4,506 ÷ 275)
- One primary diagnosis per admission (275 primary = 275 admissions)
- 93.9% of rows are secondary/comorbidity codes

---

## 4. Slicers

| Slicer | Values | Effect |
|--------|--------|--------|
| `age_group` | 18-34 · 35-49 · 50-64 · 65-79 · 80+ | Filters all visuals |
| `gender` | F · M | Filters all visuals |
| `admission_type` | 9 admission types | Filters all visuals |

---

## 5. Visual Analysis

### Visual 1 — Top 10 Primary Diagnoses

| Diagnosis | Count |
|-----------|-------|
| Coronary atherosclerosis of native coronary artery | 7 |
| Acute kidney failure, unspecified | 7 |
| Cerebral aneurysm, nonruptured | 4 |
| Non-ST elevation (NSTEMI) myocardial infarction | 4 |
| Aortic valve disorders | 4 |
| Other postoperative infection | 4 |

**Finding:** Primary admitting diagnoses are cardiovascular and renal. No single condition dominates; top 10 cover 42 admissions (15.3%).

### Visual 2 — Top 10 Diagnoses (All Records)

| Diagnosis | Records |
|-----------|---------|
| Unspecified essential hypertension | 68 |
| Hyperlipidemia, unspecified | 57 |
| Acute kidney failure, unspecified | 56 |
| Other and unspecified hyperlipidemia | 55 |
| Hypothyroidism, unspecified | 47 |

**Finding:** Secondary comorbidities reflect chronic cardiometabolic burden — hypertension and hyperlipidemia variants dominate.

### Visual 3 — Diagnosis Records by age_group and gender

| Age Group | Female | Male | Total |
|-----------|--------|------|-------|
| 50–64 | 627 | **1,286** | **1,913** |
| 65–79 | 658 | 615 | 1,273 |
| 80+ | 357 | 214 | 571 |
| 35–49 | 425 | 185 | 610 |
| 18–34 | 115 | 24 | 139 |

**Finding:** 50–64 males are the largest segment (28.5% of all diagnosis records). Overall gender split is nearly even (F: 2,182 · M: 2,324).

### Visual 4 — Average LOS by diagnosis_title

Top conditions by mean stay: ~44.93 days (catatonic schizophrenia, foreign body in larynx, etc.) and ~34.08 days (acute systolic heart failure, Takotsubo syndrome, etc.).

**Finding:** Longest stays tie to rare acute events, not high-frequency chronic conditions. Power BI rounds to ~45 and ~34 days.

---

## 6. Cross-Cutting Analysis

### ICD version mix

| Version | Records | Share |
|---------|---------|-------|
| ICD-10 | 2,313 | 51.3% |
| ICD-9 | 2,193 | 48.7% |

### Diagnosis volume by admission type

EW EMER. leads at 1,853 records (41.1%), followed by OBSERVATION ADMIT (20.6%) and URGENT (15.7%) — consistent with Dashboard 1 admission volumes.

---

## 7. DAX Measures

```DAX
Diagnosis Records = COUNTROWS(vw_diagnosis_analysis)

Diagnosed Patients = DISTINCTCOUNT(vw_diagnosis_analysis[patient_id])

Primary Diagnoses =
CALCULATE(
    COUNTROWS(vw_diagnosis_analysis),
    vw_diagnosis_analysis[is_primary_diagnosis] = TRUE()
)
```

Full reference: [powerbi/mimic_powerbi_dax_measures.md](../powerbi/mimic_powerbi_dax_measures.md)

---

## 8. Key Takeaways

1. **High coding density** — ~16.4 diagnoses per admission; Power BI rounds 4,506 to 5K.
2. **Primary = acute/cardiac** — coronary disease and acute kidney failure lead admitting diagnoses.
3. **Secondary = chronic metabolic** — hypertension, hyperlipidemia, hypothyroidism dominate.
4. **50–64 male skew** — largest diagnosis volume segment.
5. **LOS ≠ frequency** — longest stays from rare acute events, not common chronic codes.
6. **ICD-9/10 mix** — nearly even split across the demo subset.

---

## 9. Verification

```python
import pandas as pd
df = pd.read_csv("data/databricks_output/exports/vw_diagnosis_analysis.csv")
assert df["patient_id"].nunique() == 100
assert len(df) == 4506
assert (df["is_primary_diagnosis"].astype(str).str.lower() == "true").sum() == 275
```

Machine-readable output: `data/databricks_output/exports/diagnosis_analysis.json`
