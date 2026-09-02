# Raw landing zone

Symlink or copy the seven scoped `hosp/` CSV.GZ files here before bronze ingestion.

```bash
# from mimic-databricks-project/
ln -sf ../../hosp/patients.csv.gz data/raw/
ln -sf ../../hosp/admissions.csv.gz data/raw/
ln -sf ../../hosp/transfers.csv.gz data/raw/
ln -sf ../../hosp/diagnoses_icd.csv.gz data/raw/
ln -sf ../../hosp/procedures_icd.csv.gz data/raw/
ln -sf ../../hosp/prescriptions.csv.gz data/raw/
ln -sf ../../hosp/d_icd_diagnoses.csv.gz data/raw/
```
