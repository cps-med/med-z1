# Demographics Implementation Guide
## Adding Age and Gender to DDI Risk Analysis Pipeline

---

## Overview

This document describes the implementation of demographic data (Age and Gender) into the DDI risk analysis pipeline, introduced at the **data preparation stage** per your decision.

**Implementation Date**: 2025-11-27
**Demographics Added**: Age, Gender
**Future Consideration**: Race/Ethnicity (after PhysioNet integration)

---

## Implementation Summary

### What Was Added

**New Notebook:**
- `01c_dataprep_demographics.ipynb` - Extracts patient demographics from CDWWork

**Updated Notebooks:**
- `03_clean.ipynb` - Added demographics cleaning (Part 3.5)
- `04_features.ipynb` - Added demographics join into patient features

**New Data Files:**
- `v1_raw/demographics/patient_demographics.parquet` - Raw demographics
- `v2_clean/demographics/patient_demographics_clean.parquet` - Cleaned demographics

---

## Data Flow

```
CDWWork SPatient.SPatient table
  ↓
01c_dataprep_demographics.ipynb
  ↓
v1_raw/demographics/patient_demographics.parquet
  ↓
03_clean.ipynb (Part 3.5)
  ↓
v2_clean/demographics/patient_demographics_clean.parquet
  ↓
04_features.ipynb (merged into patient features)
  ↓
v3_features/patients_features.parquet (WITH demographics)
```

---

## Detailed Implementation

### Step 1: 01c_dataprep_demographics.ipynb

**Purpose**: Extract patient demographics from SQL Server CDWWork database (SPatient.SPatient schema)

**SQL Query:**
```sql
SELECT DISTINCT
    p.PatientSID,
    p.PatientIEN,
    p.Sta3n,
    p.BirthDateTime AS DateOfBirth,
    p.Gender
FROM SPatient.SPatient p
WHERE p.PatientSID IN (
    -- Only patients with medication records
    SELECT DISTINCT PatientSID FROM RxOut.RxOutpat
    UNION
    SELECT DISTINCT PatientSID FROM BCMA.BCMAMedicationLog
)
ORDER BY p.PatientSID;
```

**Processing:**
1. Query CDWWork SPatient.SPatient table
2. Filter to only patients with medication records (RxOut or BCMA)
3. Calculate Age from DateOfBirth
4. Create AgeGroup categories
5. Write to `v1_raw/demographics/patient_demographics.parquet`

**Output Columns:**
- `PatientSID` - Patient identifier (join key)
- `PatientIEN` - Patient IEN
- `Sta3n` - Station number
- `DateOfBirth` - Date of birth
- `Gender` - Gender code
- `Age` - Calculated age (years)
- `AgeGroup` - Age category (<18, 18-39, 40-64, 65-79, 80+)

---

### Step 2: 03_clean.ipynb - Part 3.5

**Purpose**: Clean and standardize demographics data

**Cleaning Operations:**

1. **Remove Duplicates**
   - Ensure one record per PatientSID

2. **Remove Missing Critical Fields**
   - Drop records missing PatientSID, DateOfBirth, or Gender

3. **Standardize Data Types**
   - PatientSID → int64
   - DateOfBirth → datetime

4. **Standardize Gender Values**
   - Map variations to standard codes:
     - M/MALE → M
     - F/FEMALE → F
     - UNKNOWN/missing → U

5. **Validate Age**
   - Recalculate Age from DateOfBirth
   - Remove unrealistic ages (< 0 or > 120)

6. **Add Derived Features**
   - `AgeGroup` - Age categories for analysis
   - `IsElderly` - Binary flag (1 if age >= 65, else 0)

**Output**: `v2_clean/demographics/patient_demographics_clean.parquet`

**Columns Added:**
- `AgeGroup` - Categorical age groups
- `IsElderly` - Binary elderly flag

---

### Step 3: 04_features.ipynb Updates

**Purpose**: Merge demographics into patient-level features

**Changes Made:**

1. **Load Demographics**
   ```python
   demo_uri = f"s3://{DEST_BUCKET}/v2_clean/demographics/patient_demographics_clean.parquet"
   df_demo = pd.read_parquet(demo_uri, filesystem=fs)
   ```

2. **Merge into Patient Features**
   ```python
   demo_cols = ['PatientSID', 'Age', 'AgeGroup', 'IsElderly', 'Gender']
   patient_features = patient_features.merge(
       df_demo[demo_cols],
       on='PatientSID',
       how='left'
   )
   ```

3. **Result**
   - Demographics now part of `patients_features.parquet`
   - Available for clustering and analysis

---

## How to Run the Updated Pipeline

### Full Pipeline (First Time)

```bash
# 1. Data Preparation
01a_dataprep_ddi.ipynb          # DDI reference data
01b_dataprep_medications.ipynb  # Patient medications
01c_dataprep_demographics.ipynb # Patient demographics (NEW)

# 2. Exploration (optional, no changes needed)
02_explore.ipynb

# 3. Cleaning
03_clean.ipynb                  # Now includes demographics (Part 3.5)

# 4. Feature Engineering
04_features.ipynb               # Now includes demographics merge

# 5. Clustering (next step)
05_clustering.ipynb             # Can now use age/gender features
```

### If You've Already Run Previous Notebooks

**Option A: Just add demographics (recommended)**
```bash
# 1. Extract demographics
01c_dataprep_demographics.ipynb

# 2. Re-run cleaning (to clean demographics)
03_clean.ipynb

# 3. Re-run feature engineering (to include demographics)
04_features.ipynb

# 4. Continue with clustering
05_clustering.ipynb
```

**Option B: Full refresh**
Run all notebooks from 01a through 04_features to ensure consistency.

---

## Demographics Features in Patient Dataset

After running the updated pipeline, `v3_features/patients_features.parquet` will include:

### Demographic Features

| Feature | Type | Description | Example | Clinical Use |
|---------|------|-------------|---------|--------------|
| `Age` | int | Patient age in years | 72 | Age-stratified analysis |
| `AgeGroup` | categorical | Age category | "65-79" | Clustering by age group |
| `IsElderly` | binary | Elderly flag (65+) | 1 | Identify elderly patients |
| `Gender` | categorical | Gender code | "M" | Gender-specific analysis |

### Combined with Existing Features

These demographics are now **combined** with medication and DDI features:

- `Age` + `unique_medications` = Age-medication interaction
- `IsElderly` + `is_polypharmacy` = Elderly polypharmacy flag
- `Gender` + `ddi_severity_High` = Gender-specific high-risk patients
- `AgeGroup` clusters = Age-stratified patient groups

---

## Example Use Cases

### 1. Age-Stratified Clustering (05_clustering.ipynb)

**Before:**
- Cluster patients only by medication/DDI features

**Now:**
- Cluster patients by Age + Medication + DDI risk
- Identify clusters like:
  - "Elderly high-risk polypharmacy"
  - "Middle-age moderate DDI"
  - "Young low-risk"

### 2. Elderly Risk Analysis (06_analysis.ipynb)

**Questions you can now answer:**
- Are elderly patients (65+) at higher DDI risk?
- What's the DDI density for elderly vs non-elderly?
- Which age group has highest polypharmacy rate?

**Example Analysis:**
```python
# Compare DDI risk by age group
patient_features.groupby('AgeGroup').agg({
    'ddi_pair_count': 'mean',
    'total_ddi_risk_score': 'mean',
    'is_high_ddi_risk': 'sum'
})
```

### 3. Gender-Specific Patterns

**Questions you can now answer:**
- Do males/females have different DDI patterns?
- Are certain interactions more common in one gender?

### 4. Age-Adjusted Risk Scoring

**Future use:**
- Personalized risk scores: "For a 78-year-old patient, DDI risk is X%"
- Age-specific thresholds for intervention

---

## Data Quality Considerations

### Age Validation

**Checks Performed:**
- ✅ No negative ages
- ✅ No ages > 120
- ✅ Age recalculated from DateOfBirth for consistency

### Gender Standardization

**Mappings:**
- M/MALE → M
- F/FEMALE → F
- UNKNOWN/missing → U

### Missing Data Handling

**Strategy:**
- Left join: Patients without demographics still appear in features
- Age/Gender = NULL if not found
- Can filter or impute as needed in analysis

---

## PhysioNet Integration (Future)

When you add PhysioNet MIMIC-IV data, you mentioned wanting to analyze **care coordination between VA and non-VA settings**.

### How Demographics Will Help

**VA vs Non-VA Analysis:**
```
Patient 1005:
  Age: 72 (elderly)
  VA medications: 5
  Non-VA medications: 3
  Total DDI pairs: 8 (some cross-system)

→ Elderly patient with fragmented care DDI risk
```

**Equity Analysis:**
- Compare VA-only vs VA+Community patients
- Identify if age/gender affects care fragmentation
- Detect disparities in DDI risk by demographics

### What to Add from PhysioNet

When ready, extract from MIMIC-IV:
- Age (subject_age or calculate from anchor_year)
- Gender (from patients table)
- Use same pipeline (01c, 03, 04)

---

## Summary

✅ **Completed:**
- Created `01c_dataprep_demographics.ipynb`
- Updated `03_clean.ipynb` with demographics cleaning
- Updated `04_features.ipynb` with demographics merge
- Demographics (Age, Gender) now available in patient features

✅ **Benefits:**
- Age-stratified clustering and analysis
- Gender-specific pattern detection
- Elderly risk identification
- Foundation for PhysioNet care coordination analysis

✅ **Next Steps:**
1. Run `01c_dataprep_demographics.ipynb` to extract demographics
2. Re-run `03_clean.ipynb` to clean demographics
3. Re-run `04_features.ipynb` to merge demographics
4. Continue to `05_clustering.ipynb` with enhanced features

---

*Implementation complete - Demographics integrated at data prep stage as requested*
