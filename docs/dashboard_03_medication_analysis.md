# Dashboard 3 — Medication Analysis

**Power BI page:** Medication Analysis (Page 3 of 4)  
**Data view:** `vw_prescription_analysis`  
**Live dashboard:** [MIMIC Analytics Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYWIwMDQ2MmItZTk2YS00NmRkLTlmNmUtMDljMjUwYTY1MWU0IiwidCI6ImJlOTdiY2NhLWEzZTItNDc4Yy1iMWM1LWQ5YTRkMWI2NTY3YyJ9)  
**Export verified:** `data/databricks_output/exports/vw_prescription_analysis.csv` (18,087 rows × 17 columns)  
**HTML report:** [report/dashboard_03_medication_analysis.html](../report/dashboard_03_medication_analysis.html)

---

## 1. Purpose

The Medication Analysis page explores inpatient pharmacy orders — drug frequency, administration routes, prescription duration, and drug-type classification.

**Questions this page answers:**

1. How many prescriptions were ordered across the cohort?
2. Which drugs and administration routes dominate?
3. What is the typical prescription duration?
4. How do medication patterns vary by age, gender, route, and drug type?

All visuals query `workspace.mimic.vw_prescription_analysis` via Databricks SQL Warehouse.

---

## 2. Data Source

### View schema

| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | int | Patient identifier |
| `admission_id` | int | Hospital admission identifier |
| `pharmacy_id` | int | Unique pharmacy order identifier |
| `drug_name` | string | Medication name |
| `drug_type` | string | MAIN · BASE · ADDITIVE |
| `product_strength` | string | Formulation / strength |
| `dose_value` | float | Ordered dose amount |
| `dose_unit` | string | Dose unit (mg, UNIT, etc.) |
| `doses_per_24_hours` | float | Frequency |
| `administration_route` | string | IV · PO · SC · etc. |
| `prescription_start_date` | date | Order start (deidentified) |
| `prescription_duration_days` | float | Order duration in days |
| `admission_type` | string | Admission category |
| `length_of_stay_days` | float | Admission LOS |
| `gender` | string | F / M |
| `anchor_age` | int | Patient age |
| `age_group` | string | Age band |

### Data lineage

```
hosp/prescriptions.csv + hosp/admissions.csv + hosp/patients.csv
  → Bronze → Silver → Gold (fact_prescription)
  → SQL view (vw_prescription_analysis)
  → Power BI Medication Analysis page
```

---

## 3. KPI Cards

| Card | Value | DAX Measure |
|------|-------|-------------|
| Total Prescriptions | 18,087 (18K in PBI) | `COUNTROWS(vw_prescription_analysis)` |
| Patients Receiving Medication | 100 | `DISTINCTCOUNT(patient_id)` |
| Unique Drugs | 626 (598 in PBI) | `DISTINCTCOUNT(drug_name)` |
| Avg Prescription Duration | 2.71 days | `AVERAGE(prescription_duration_days)` |

All four values **verified against the CSV export**. Power BI rounds totals and may show 598 unique drugs on an earlier snapshot; current export has 626 distinct drug names.

**Derived:** ~72.3 prescriptions per admission (250 of 275 admissions have pharmacy records).

---

## 4. Slicers

| Slicer | Values |
|--------|--------|
| `administration_route` | 34 routes (IV, PO/NG, PO, SC, IV DRIP, …) |
| `age_group` | 18-34 · 35-49 · 50-64 · 65-79 · 80+ |
| `gender` | F · M |
| `drug_type` | MAIN · BASE · ADDITIVE |

---

## 5. Visual Analysis

### Visual 1 — Top 10 Medications

| Drug | Prescriptions |
|------|---------------|
| Insulin | 915 |
| 0.9% Sodium Chloride | 810 |
| Potassium Chloride | 610 |
| Sodium Chloride 0.9% Flush | 585 |
| Furosemide | 510 |
| 5% Dextrose | 492 |
| Bag | 454 |
| Magnesium Sulfate | 402 |
| Metoprolol Tartrate | 371 |
| Acetaminophen | 344 |

**Finding:** Top 10 = 30.4% of all orders. Insulin and IV fluids dominate — consistent with acute inpatient care and diabetes comorbidity.

### Visual 2 — Prescriptions by administration_route

| Route | Share |
|-------|-------|
| IV | 45.44% |
| PO/NG | 21.24% |
| PO | 12.11% |
| SC | 6.91% |
| IV DRIP | 5.67% |

**Finding:** Parenteral routes (IV + IV DRIP) exceed 51%. Top 5 routes = 90.4%.

### Visual 3 — Prescriptions by drug_type

| Type | Prescriptions | Share |
|------|---------------|-------|
| MAIN | 14,391 | 79.6% |
| BASE | 3,677 | 20.3% |
| ADDITIVE | 19 | 0.1% |

### Visual 4 — Average prescription duration by drug_name

Longest averages: Clotrimazole (~23 days), Aluminum Hydroxide (~23 days), Clonidine Patch (~18 days). Overall mean = 2.71 days.

**Finding:** Long durations are rare-drug outliers on extended stays; most orders are short-course.

---

## 6. DAX Measures

```DAX
Total Prescriptions = COUNTROWS(vw_prescription_analysis)

Patients Receiving Medication =
DISTINCTCOUNT(vw_prescription_analysis[patient_id])

Unique Drugs = DISTINCTCOUNT(vw_prescription_analysis[drug_name])

Avg Prescription Duration =
AVERAGE(vw_prescription_analysis[prescription_duration_days])
```

---

## 7. Key Takeaways

1. **18K prescriptions** — ~72 per admission; all 100 patients medicated.
2. **IV-first** — 45.4% IV; fluids and electrolytes in top 10.
3. **Insulin leads** — 915 orders; aligns with Dashboard 2 comorbidity profile.
4. **MAIN dominates** — 79.6% active therapeutics vs 20.3% BASE fluids.
5. **Short typical duration** — 2.71 days average.

---

## 8. Verification

```python
import pandas as pd
df = pd.read_csv("data/databricks_output/exports/vw_prescription_analysis.csv")
assert len(df) == 18087
assert df["patient_id"].nunique() == 100
assert df["drug_name"].nunique() == 626
assert round(df["prescription_duration_days"].mean(), 2) == 2.71
```

Machine-readable output: `data/databricks_output/exports/prescription_analysis.json`
