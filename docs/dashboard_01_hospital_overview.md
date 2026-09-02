# Dashboard 1 — Hospital Overview (Executive Overview)

**Power BI page:** Executive Overview (Page 1 of 4)  
**Data view:** `vw_admission_overview`  
**Live dashboard:** [MIMIC Analytics Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYWIwMDQ2MmItZTk2YS00NmRkLTlmNmUtMDljMjUwYTY1MWU0IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)  
**Export verified:** `data/databricks_output/exports/vw_admission_overview.csv` (275 rows × 18 columns)

---

## 1. Purpose

The Hospital Overview page is the executive entry point to the MIMIC Analytics dashboard. It answers four operational questions at a glance:

1. **How many patients and admissions are in the dataset?**
2. **What are the typical length of stay, readmission rate, and mortality?**
3. **Which admission types, age groups, and insurance plans dominate?**
4. **How do admission volumes trend over time?**

All visuals and KPI cards on this page query a single Gold-layer SQL view — `workspace.mimic.vw_admission_overview` — connected via Databricks SQL Warehouse.

---

## 2. Data Source

### View schema

| Column | Type | Description |
|--------|------|-------------|
| `admission_id` | int | Unique hospital admission identifier |
| `patient_id` | int | Patient identifier (links to `dim_patient`) |
| `gender` | string | F / M |
| `anchor_age` | int | Patient age at anchor year |
| `age_group` | string | 18-34, 35-49, 50-64, 65-79, 80+ |
| `admission_date` | date | Admission timestamp (deidentified) |
| `admission_year` | int | Year extracted from admission date |
| `admission_month` | int | Month number (1–12) |
| `admission_month_name` | string | Month name |
| `admission_type` | string | URGENT, EW EMER., ELECTIVE, etc. |
| `admission_location` | string | Where patient was admitted from |
| `discharge_location` | string | Where patient was discharged to |
| `insurance` | string | MEDICARE, MEDICAID, OTHER |
| `race` | string | Patient race |
| `length_of_stay_days` | float | Discharge − admission in days |
| `ed_duration_hours` | float | Emergency department duration (hours) |
| `died_in_hospital` | bool | In-hospital mortality flag |
| `is_30_day_readmission` | bool | 30-day readmission flag (window function in Gold layer) |

### Data lineage

```
hosp/admissions.csv + hosp/patients.csv
  → Bronze (bronze_admissions, bronze_patients)
  → Silver (silver_admissions, silver_patients)
  → Gold (fact_admission — includes readmission logic)
  → SQL view (vw_admission_overview)
  → Power BI Executive Overview page
```

---

## 3. Page Layout

### KPI cards (top row)

Five cards display headline metrics, powered by DAX measures on `vw_admission_overview`:

| Card | Value | DAX Measure |
|------|-------|-------------|
| Total Patients | 100 | `DISTINCTCOUNT(patient_id)` |
| Total Admissions | 275 | `DISTINCTCOUNT(admission_id)` |
| Average LOS | 6.88 days | `AVERAGE(length_of_stay_days)` |
| Readmission Rate | 19.3% | `DIVIDE([30-Day Readmissions], [Total Admissions], 0)` |
| In-Hospital Deaths | 15 | `CALCULATE(DISTINCTCOUNT(admission_id), died_in_hospital = TRUE())` |

All five values were **verified against the CSV export** — exact match.

### Slicers (left panel)

| Slicer | Values | Effect |
|--------|--------|--------|
| `age_group` | 18-34, 35-49, 50-64, 65-79, 80+ | Filters all visuals by patient age band |
| `admission_type` | 9 types (see Section 4.1) | Filters by admission pathway |
| `gender` | F, M | Filters by patient gender |

Slicers cross-filter all KPI cards and charts on the page.

### Visuals (5 charts)

| # | Chart Type | Title | Field(s) |
|---|-----------|-------|----------|
| 1 | Horizontal bar | Total Admissions by admission_type | `admission_type`, count of `admission_id` |
| 2 | Vertical bar | Patients by Age Group | `age_group`, distinct `patient_id` |
| 3 | Line | Count of admission_id by Year | `admission_year`, count of `admission_id` |
| 4 | Donut | Admissions by Insurance | `insurance`, count of `admission_id` |
| 5 | Vertical bar | Average LOS by admission_type | `admission_type`, average `length_of_stay_days` |

---

## 4. Visual Analysis (Verified)

### 4.1 Total Admissions by admission_type

Emergency ward admissions dominate the hospital's intake profile.

| Admission Type | Admissions | Share | Bar rank |
|----------------|------------|-------|----------|
| **EW EMER.** | **104** | 37.8% | 1st |
| OBSERVATION ADMIT | 45 | 16.4% | 2nd |
| URGENT | 38 | 13.8% | 3rd |
| EU OBSERVATION | 30 | 10.9% | 4th |
| SURGICAL SAME DAY ADMISSION | 18 | 6.5% | 5th |
| DIRECT EMER. | 15 | 5.5% | 6th |
| ELECTIVE | 13 | 4.7% | 7th |
| DIRECT OBSERVATION | 7 | 2.5% | 8th |
| AMBULATORY OBSERVATION | 5 | 1.8% | 9th |

**Insight:** EW EMER. alone accounts for more admissions than the next two types combined. Grouping all observation pathways (OBSERVATION ADMIT + EU OBSERVATION + DIRECT OBSERVATION + AMBULATORY OBSERVATION) yields **87 admissions (31.6%)**, revealing a significant short-stay monitoring channel alongside traditional emergency intake.

**Admission source context:** 134 of 275 admissions (48.7%) originate from the **EMERGENCY ROOM** as the admission location, consistent with EW EMER. dominance.

### 4.2 Patients by Age Group

| Age Group | Patients | Share of 100 |
|-----------|----------|--------------|
| **50–64** | **34** | 34% |
| 65–79 | 28 | 28% |
| 80+ | 16 | 16% |
| 35–49 | 15 | 15% |
| 18–34 | 7 | 7% |

**Insight:** The cohort is heavily weighted toward older adults. Patients aged **50–79 represent 62 of 100 (62%)**. The 18–34 band has only 7 patients — the smallest group.

**Gender:** 57 male, 43 female patients. At the admission level, males have slightly more visits (142 vs 133 admissions).

**Mortality by age** (derived from CSV, not shown on dashboard):

| Age Group | Deaths | Admissions | Mortality Rate |
|-----------|--------|------------|----------------|
| 18–34 | 0 | 12 | 0.0% |
| 35–49 | 0 | 48 | 0.0% |
| 50–64 | 6 | 111 | 5.4% |
| 65–79 | 6 | 72 | 8.3% |
| 80+ | 3 | 32 | 9.4% |

All 15 in-hospital deaths occur in patients aged 50+, with mortality rising with age.

### 4.3 Count of admission_id by Year

Admission years range from **2110 to 2201** — these are **deidentified shifted dates** from MIMIC-IV, not real calendar years. No epidemiological trend should be inferred from this axis.

| Year | Admissions | Note |
|------|------------|------|
| **2148** | **13** | Peak year |
| 2147 | 12 | Second highest |
| 2137 | 9 | |
| 2136 | 9 | |
| 2117 | 8 | |

The line chart shows high year-to-year volatility with intermittent spikes rather than a steady trend. This reflects the small demo subset (100 patients) spread across a wide synthetic timeline.

**Monthly pattern** (supplementary, not on dashboard): September (28), December/July/June (25 each) have the highest admission counts. This may reflect random variation in the demo data rather than true seasonality.

### 4.4 Admissions by Insurance

| Insurance | Admissions | Share |
|-----------|------------|-------|
| **OTHER** | **149** | **54.18%** |
| MEDICARE | 104 | 37.82% |
| MEDICAID | 22 | 8.00% |

**Insight:** Over half of admissions fall under "OTHER" insurance. Medicare covers nearly 38%, aligning with the older age distribution. Medicaid is a small share at 8%.

### 4.5 Average LOS by admission_type

| Admission Type | Avg LOS (days) | LOS rank |
|----------------|----------------|----------|
| **URGENT** | **9.9** | Longest |
| DIRECT EMER. | 9.4 | |
| ELECTIVE | 8.2 | |
| OBSERVATION ADMIT | 8.2 | |
| EW EMER. | 7.3 | |
| SURGICAL SAME DAY ADMISSION | 5.7 | |
| DIRECT OBSERVATION | 1.4 | |
| AMBULATORY OBSERVATION | 1.0 | |
| **EU OBSERVATION** | **0.9** | Shortest |

**Insight:** The chart reveals a clear bimodal pattern:
- **Inpatient-intensive types** (URGENT, DIRECT EMER., ELECTIVE, OBSERVATION ADMIT) average 7–10 days
- **Observation types** (EU OBSERVATION, AMBULATORY OBSERVATION, DIRECT OBSERVATION) average under 1.5 days

EW EMER. has the highest volume (104) but only the 5th-longest average stay (7.3 days). **Volume and bed-day intensity are driven by different admission types** — a key operational distinction for capacity planning.

**LOS distribution** (supplementary): median 4.85 days, 75th percentile 8.77 days, maximum 44.93 days.

---

## 5. Cross-Cutting Analysis

### Readmissions (19.3%)

53 of 275 admissions are flagged as 30-day readmissions. Breakdown by admission type:

| Admission Type | Readmissions | Type-level rate |
|----------------|-------------|-----------------|
| EW EMER. | 25 | 24.0% |
| OBSERVATION ADMIT | 9 | 20.0% |
| URGENT | 6 | 15.8% |
| DIRECT EMER. | 5 | 33.3% |
| SURGICAL SAME DAY ADMISSION | 3 | 16.7% |
| ELECTIVE | 2 | 15.4% |
| EU OBSERVATION | 2 | 6.7% |
| DIRECT OBSERVATION | 1 | 14.3% |
| AMBULATORY OBSERVATION | 0 | 0.0% |

**DIRECT EMER.** has the highest type-level readmission rate (33.3%), though based on only 15 admissions. EW EMER. contributes the most readmission events in absolute terms (25).

### In-hospital mortality (15 deaths, 5.5%)

| Admission Type | Deaths |
|----------------|--------|
| EW EMER. | 6 |
| URGENT | 5 |
| OBSERVATION ADMIT | 3 |
| DIRECT EMER. | 1 |

All 15 deaths are reflected in the discharge location field as **DIED** (15 records). An additional 5 patients were discharged to **HOSPICE**.

### Discharge destinations

| Discharge Location | Admissions | Share |
|--------------------|------------|-------|
| HOME HEALTH CARE | 76 | 27.6% |
| HOME | 72 | 26.2% |
| SKILLED NURSING FACILITY | 36 | 13.1% |
| DIED | 15 | 5.5% |
| REHAB | 13 | 4.7% |
| CHRONIC/LONG TERM ACUTE CARE | 9 | 3.3% |
| HOSPICE | 5 | 1.8% |
| Other | 29 | 10.5% |

Over half of discharges (53.8%) go directly home or with home health care. Post-acute facilities (SNF, rehab, long-term care) account for 21.1%.

### High-utilizer patients

| Patient ID | Admissions |
|------------|------------|
| 10014354 | 20 |
| 10015860 | 13 |
| 10002930 | 12 |
| 10040025 | 10 |
| 10039708 | 10 |

The top 5 patients account for **65 admissions (23.6%)** of the total. One patient alone has 20 admissions. These high utilizers disproportionately drive the 2.75 average admissions/patient and the 19.3% readmission rate.

---

## 6. DAX Measures on This Page

Six measures are used on the Hospital Overview page. Full definitions in [`powerbi/mimic_powerbi_dax_measures.md`](../powerbi/mimic_powerbi_dax_measures.md).

```dax
Total Patients =
DISTINCTCOUNT(vw_admission_overview[patient_id])

Total Admissions =
DISTINCTCOUNT(vw_admission_overview[admission_id])

Average LOS =
AVERAGE(vw_admission_overview[length_of_stay_days])

In-Hospital Deaths =
CALCULATE(
    DISTINCTCOUNT(vw_admission_overview[admission_id]),
    vw_admission_overview[died_in_hospital] = TRUE()
)

30-Day Readmissions =
CALCULATE(
    DISTINCTCOUNT(vw_admission_overview[admission_id]),
    vw_admission_overview[is_30_day_readmission] = TRUE()
)

Readmission Rate =
DIVIDE(
    [30-Day Readmissions],
    [Total Admissions],
    0
)
```

---

## 7. Key Takeaways

1. **Emergency-driven intake** — EW EMER. is the dominant admission pathway (37.8%), with observation types adding another 31.6%.
2. **Older adult cohort** — 62% of patients are aged 50–79; all mortality occurs in this age range and above.
3. **Volume ≠ intensity** — EW EMER. drives volume but URGENT/DIRECT EMER. drive bed-days (9.9 and 9.4 day average LOS).
4. **Readmission burden** — 19.3% readmission rate, concentrated in EW EMER. (25 events) and driven partly by high-utilizer patients.
5. **Insurance concentration** — 92% of admissions are OTHER or Medicare; Medicaid is minimal at 8%.
6. **Post-acute discharge** — 27.6% discharged to home health care, 13.1% to skilled nursing facilities.
7. **Demo limitations** — 100-patient subset with deidentified dates; findings illustrate pipeline capability, not population epidemiology.

---

## 8. Verification

All figures recomputed from `data/databricks_output/exports/vw_admission_overview.csv` using Python/pandas. Machine-readable output: `data/databricks_output/exports/admission_analysis.json`.

```python
import pandas as pd

df = pd.read_csv("data/databricks_output/exports/vw_admission_overview.csv")

assert df["patient_id"].nunique() == 100
assert df["admission_id"].nunique() == 275
assert round(df["length_of_stay_days"].mean(), 2) == 6.88
assert df.loc[df["died_in_hospital"], "admission_id"].nunique() == 15
assert df.loc[df["is_30_day_readmission"], "admission_id"].nunique() == 53
assert round(53 / 275, 3) == 0.193
```

**HTML report:** [report/dashboard_01_hospital_overview.html](../report/dashboard_01_hospital_overview.html)
