# Problems/Diagnoses ETL Pipeline - Testing Guide

**Document Version:** 1.0
**Date:** 2026-02-07
**Status:** Phase 3 Complete - Ready for Testing

---

## Overview

This guide provides step-by-step instructions for testing the complete Problems/Diagnoses ETL pipeline, from mock data in SQL Server through to the PostgreSQL serving database.

**Phases Completed:**
- ✅ **Phase 1:** Mock Data & Schema (Days 1-3)
- ✅ **Phase 2:** ETL Pipeline (Days 4-7)
- ✅ **Phase 3:** PostgreSQL Schema & Load (Days 8-9)

**What's Been Built:**
- 4 SQL Server tables with 73 problem records (55 VistA + 18 Cerner)
- 3 ETL transformation scripts (Bronze → Silver → Gold)
- 1 PostgreSQL serving table with comprehensive indexes
- 1 Load script with verification queries

---

## Prerequisites

Before testing, ensure the following services are running:

1. **SQL Server Container** (ports 1433)
   - CDWWork database (VistA mock data)
   - CDWWork2 database (Cerner mock data)

2. **MinIO Container** (ports 9000, 9001)
   - med-data bucket for Parquet files

3. **PostgreSQL Container** (port 5432)
   - medz1 database

4. **Python Environment**
   - Virtual environment activated: `source .venv/bin/activate`
   - All dependencies installed: `pip install -r requirements.txt`

---

## Step 1: Verify Mock Data (Source)

First, verify that the mock data loaded correctly into SQL Server.

### 1.1 Run Verification Script

```bash
cd /Users/chuck/swdev/med/med-z1
sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -C -i scripts/verify_problems_mock_data.sql
```

### 1.2 Expected Output

You should see:
- **CDWWork:** 55 problems across 7 patients
- **CDWWork2:** 18 problems across 2 patients
- **Total:** 73 problem records

**Sample Output:**
```
CDWWork (VistA) - Problem List Data
3. Outpat.ProblemList (VistA Problem List)
TotalProblems  PatientCount  ActiveProblems  ChronicProblems
55             7             47              38

CDWWork2 (Cerner) - Problem List Data
4. EncMill.ProblemList (Cerner Problem List)
TotalProblems  PatientCount  ActiveProblems  ChronicProblems
18             2             17              16
```

**Key Test Patients:**
- **ICN100001** (Adam Dooree) - High complexity (14 VistA + 8 Cerner = 22 total problems)
- **ICN100010** (Alexander Aminor) - Moderate complexity (10 VistA + 10 Cerner = 20 total problems)

---

## Step 2: Run Bronze ETL (Extract)

Extract raw data from SQL Server to MinIO Parquet files.

### 2.1 Execute Bronze Script

```bash
cd /Users/chuck/swdev/med/med-z1
python -m etl.bronze_problems
```

### 2.2 Expected Output

```
======================================================================
Starting Bronze extraction for all Problems/Diagnoses tables
======================================================================
Starting Bronze extraction: Dim.ICD10
  - Extracted 50 ICD-10 codes from CDWWork
  - Bronze extraction complete: 50 ICD-10 codes written to s3://med-data/bronze/cdwwork/icd10_dim/icd10_dim_raw.parquet

Starting Bronze extraction: Dim.CharlsonMapping
  - Extracted 60 Charlson mappings from CDWWork
  - Bronze extraction complete: 60 Charlson mappings written to s3://med-data/bronze/cdwwork/charlson_mapping/charlson_mapping_raw.parquet

Starting Bronze extraction: Outpat.ProblemList
  - Extracted 55 VistA problem records from CDWWork
  - Bronze extraction complete: 55 VistA problem records written to s3://med-data/bronze/cdwwork/outpat_problemlist/outpat_problemlist_raw.parquet

Starting Bronze extraction: EncMill.ProblemList
  - Extracted 18 Cerner problem records from CDWWork2
  - Bronze extraction complete: 18 Cerner problem records written to s3://med-data/bronze/cdwwork2/encmill_problemlist/encmill_problemlist_raw.parquet

======================================================================
Bronze extraction complete for all Problems/Diagnoses tables
  - ICD-10 Codes: 50 rows
  - Charlson Mappings: 60 rows
  - VistA Problems (CDWWork): 55 rows
  - Cerner Problems (CDWWork2): 18 rows
  - Total Problem Records: 73
======================================================================
```

### 2.3 Verify Parquet Files in MinIO

Open MinIO Console: http://localhost:9001

Navigate to: `med-data/bronze/`

**Expected files:**
- `cdwwork/icd10_dim/icd10_dim_raw.parquet` (50 rows)
- `cdwwork/charlson_mapping/charlson_mapping_raw.parquet` (60 rows)
- `cdwwork/outpat_problemlist/outpat_problemlist_raw.parquet` (55 rows)
- `cdwwork2/encmill_problemlist/encmill_problemlist_raw.parquet` (18 rows)

---

## Step 3: Run Silver ETL (Harmonize)

Harmonize VistA and Cerner schemas, deduplicate, and enrich with ICD-10 reference data.

### 3.1 Execute Silver Script

```bash
python -m etl.silver_problems
```

### 3.2 Expected Output

```
======================================================================
Starting Silver Problems transformation
======================================================================
Step 1: Loading Bronze Parquet files...
  - Loaded 50 ICD-10 codes
  - Loaded 60 Charlson mappings
  - Loaded 55 VistA problem records
  - Loaded 18 Cerner problem records

Step 2: Harmonizing VistA schema...
  - Harmonized 55 VistA records

Step 3: Harmonizing Cerner schema...
  - Harmonized 18 Cerner records

Step 4: Combining VistA and Cerner records...
  - Combined 73 total problem records

Step 5: Deduplicating problems across both systems...
  - Removed 14 duplicate problems
  - Retained 59 unique problems

Step 6: Enriching with ICD-10 reference data...
  - All 59 problems have ICD-10 reference data

Step 7: Adding Silver metadata...
Step 8: Writing to Silver layer...

Silver transformation complete: 59 problems written to s3://med-data/silver/problems/problems_harmonized.parquet

======================================================================
Silver Problems Transformation Summary
======================================================================
  - VistA: 41 problems
  - Cerner: 18 problems
  - Active: 52 problems
  - Chronic conditions: 47
  - Service-connected: 28
  - Problems with Charlson Index mapping: 35
======================================================================
```

**Key Verification Points:**
- **Deduplication:** 73 raw → 59 unique (14 duplicates removed)
  - ICN100001 and ICN100010 exist in BOTH databases
  - Duplicates removed based on: Same ICN + Same ICD-10 Code + Same Onset Date
  - VistA preferred over Cerner when duplicate detected

---

## Step 4: Run Gold ETL (Charlson Index)

Calculate Charlson Comorbidity Index and patient-level aggregations.

### 4.1 Execute Gold Script

```bash
python -m etl.gold_problems
```

### 4.2 Expected Output

```
======================================================================
Starting Gold Problems transformation (Charlson Index)
======================================================================
Step 1: Loading Silver Parquet file...
  - Loaded 59 problem records from Silver

Step 2: Calculating Charlson Comorbidity Index per patient...
  - Filtered to 52 active problems
  - Found 35 active problems with Charlson mappings
  - Aggregated to XX patient-condition pairs
  - Calculated Charlson Index for XX patients

Step 3: Calculating problem counts per patient...
  - Calculated problem counts for XX patients

Step 4: Flagging specific chronic conditions per patient...
  - Created chronic condition flags for XX patients

Step 5: Joining patient-level aggregations...
Step 6: Adding Gold metadata...
Step 7: Writing to Gold layer...

Gold transformation complete: 59 problem records written to s3://med-data/gold/problems/patient_problems.parquet

======================================================================
Gold Problems Transformation Summary
======================================================================
Charlson Index Distribution (unique patients):
  - Min: 0, Max: 8, Mean: 3.50, Median: 4

Patients by Charlson Index range:
  - 0 (No comorbidities): X patients
  - 1-2 (Low): X patients
  - 3-4 (Moderate): X patients
  - 5+ (High): X patients

Patients with specific chronic conditions:
  - CHF: X patients
  - Diabetes: X patients
  - COPD: X patients
  - CKD: X patients
  - Hypertension: X patients
  - Depression: X patients
  - PTSD: X patients
  - Cancer: X patients
======================================================================
```

**Key Verification Points:**
- Charlson Index properly calculated (condition-level aggregation, then sum)
- 15 chronic condition flags set correctly
- Patient-level counts match problem distribution

---

## Step 5: Create PostgreSQL Table

Create the serving database table with all indexes.

### 5.1 Execute DDL Script

```bash
psql -h localhost -p 5432 -U postgres -d medz1 -f db/ddl/create_patient_problems_table.sql
```

### 5.2 Expected Output

```
CREATE SCHEMA
DROP TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
... (13 indexes total)

NOTICE:  =================================================================
NOTICE:  Table clinical.patient_problems created successfully
NOTICE:  Indexes created for optimal query performance
NOTICE:  Schema supports:
NOTICE:    - Dual coding (ICD-10 + SNOMED)
NOTICE:    - Charlson Comorbidity Index calculation
NOTICE:    - 15 chronic condition flags for AI/ML
NOTICE:    - Multi-source harmonization (VistA + Cerner)
NOTICE:    - Patient-level aggregations (denormalized for performance)
NOTICE:  =================================================================
```

### 5.3 Verify Table Structure

```bash
psql -h localhost -p 5432 -U postgres -d medz1 -c "\d+ clinical.patient_problems"
```

You should see ~60 columns including:
- Primary keys (problem_id, patient_icn, patient_key)
- Dual coding (icd10_code, snomed_code)
- Charlson Index fields (charlson_index, charlson_condition_count)
- 15 chronic condition flags (has_chf, has_diabetes, etc.)
- Patient-level aggregations (active_problem_count, etc.)

---

## Step 6: Load Data to PostgreSQL

Load Gold Parquet data into PostgreSQL serving table.

### 6.1 Execute Load Script

```bash
python -m etl.load_problems
```

### 6.2 Expected Output

```
======================================================================
PostgreSQL Load: Problems/Diagnoses
======================================================================
Step 1: Loading Gold problems...
  - Loaded 59 problem records from Gold layer

Step 2: Transforming to match PostgreSQL schema...
  - Prepared 59 problem records for PostgreSQL

Step 3: Connecting to PostgreSQL...
Step 4: Truncating existing patient_problems table...
  - Table truncated

Step 5: Loading data into PostgreSQL...
  - Loaded 59 problem records into patient_problems table

Step 6: Verifying data...
  - Verified: 59 rows in patient_problems table
  - Patients: 7

  - Problem status distribution:
    Active: 52 problems
    Resolved: 7 problems

  - Top 5 ICD-10 categories (active problems):
    Cardiovascular: 18 problems
    Endocrine/Metabolic: 12 problems
    Respiratory: 8 problems
    ...

  - Charlson Index distribution (unique patients):
    Min: 0, Max: 8, Mean: 3.57, Median: 4.00

  - Patients by Charlson Index range:
    0 (No comorbidities): X patients
    1-2 (Low): X patients
    3-4 (Moderate): X patients
    5+ (High): X patients

  - Patients with specific chronic conditions:
    CHF: X, Diabetes: X, COPD: X, CKD: X
    Hypertension: X, Depression: X, PTSD: X, Cancer: X

  - Active service-connected problems: XX

  - Problems by source EHR:
    VistA: 41 problems
    Cerner: 18 problems

  - Sample active problems (most recent 5):
    ICN100001: I50.23 - Acute on chronic systolic (congestive) hear... (Active, 2019-05-10, VistA)
    ...

======================================================================
✓ PostgreSQL load complete: 59 problem records loaded
======================================================================
```

---

## Step 7: Verify PostgreSQL Data

Run verification queries to confirm data integrity.

### 7.1 Test Patient Lookup (ICN100001 - Adam Dooree)

```bash
psql -h localhost -p 5432 -U postgres -d medz1
```

```sql
-- Get patient's Charlson Index and active problems
SELECT
    patient_key,
    charlson_index,
    charlson_condition_count,
    active_problem_count,
    has_chf,
    has_diabetes,
    has_copd,
    has_ckd
FROM clinical.patient_problems
WHERE patient_key = 'ICN100001'
LIMIT 1;
```

**Expected Result:**
- Charlson Index: 7-8 (high complexity patient)
- Active problem count: ~14
- Chronic condition flags: CHF=TRUE, Diabetes=TRUE, CKD=TRUE

### 7.2 Test Active Problems Query

```sql
-- Get active problems for patient
SELECT
    icd10_code,
    icd10_description,
    icd10_category,
    problem_status,
    onset_date,
    service_connected,
    source_ehr
FROM clinical.patient_problems
WHERE patient_key = 'ICN100001'
  AND problem_status = 'Active'
ORDER BY onset_date DESC;
```

**Expected Result:**
- 12-14 active problems
- Mixed VistA and Cerner sources (after deduplication)
- ICD-10 codes like: I50.23 (CHF), E11.22 (Diabetes with CKD), N18.3 (CKD Stage 3)

### 7.3 Test Charlson Index Distribution

```sql
-- Get Charlson Index distribution across all patients
SELECT
    CASE
        WHEN charlson_index = 0 THEN '0 (No comorbidities)'
        WHEN charlson_index BETWEEN 1 AND 2 THEN '1-2 (Low)'
        WHEN charlson_index BETWEEN 3 AND 4 THEN '3-4 (Moderate)'
        WHEN charlson_index >= 5 THEN '5+ (High)'
    END as complexity,
    COUNT(DISTINCT patient_key) as patient_count
FROM clinical.patient_problems
GROUP BY
    CASE
        WHEN charlson_index = 0 THEN '0 (No comorbidities)'
        WHEN charlson_index BETWEEN 1 AND 2 THEN '1-2 (Low)'
        WHEN charlson_index BETWEEN 3 AND 4 THEN '3-4 (Moderate)'
        WHEN charlson_index >= 5 THEN '5+ (High)'
    END
ORDER BY MIN(charlson_index);
```

### 7.4 Test ICD-10 Category Grouping

```sql
-- Get active problems grouped by ICD-10 category
SELECT
    icd10_category,
    COUNT(*) as problem_count,
    COUNT(DISTINCT patient_key) as patient_count
FROM clinical.patient_problems
WHERE problem_status = 'Active'
  AND icd10_category IS NOT NULL
GROUP BY icd10_category
ORDER BY problem_count DESC;
```

---

## Troubleshooting

### Issue: Bronze extraction fails with SQL connection error

**Solution:**
```bash
# Check SQL Server is running
docker ps | grep sql-server

# Test connection manually
sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -C -Q "SELECT @@VERSION"
```

### Issue: MinIO write fails

**Solution:**
```bash
# Check MinIO is running
docker ps | grep minio

# Verify bucket exists
mc ls local/med-data
```

### Issue: PostgreSQL load fails with table not found

**Solution:**
```bash
# Recreate table
psql -h localhost -p 5432 -U postgres -d medz1 -f db/ddl/create_patient_problems_table.sql
```

### Issue: Deduplication count doesn't match expectations

**Expected Behavior:**
- ICN100001 exists in BOTH CDWWork (14 problems) and CDWWork2 (8 problems)
- ICN100010 exists in BOTH CDWWork (10 problems) and CDWWork2 (10 problems)
- Deduplication removes problems where: Same ICN + Same ICD-10 Code + Same Onset Date
- VistA is preferred over Cerner when duplicate detected
- Expected duplicates: ~14 (varies based on overlapping diagnoses)

---

## Success Criteria

✅ **Bronze Layer:**
- 4 Parquet files created in MinIO
- 73 total problem records extracted (55 VistA + 18 Cerner)

✅ **Silver Layer:**
- Schema harmonization complete (VistA and Cerner unified)
- Deduplication applied (~14 duplicates removed)
- ICD-10 reference data enrichment successful
- 59 unique problem records

✅ **Gold Layer:**
- Charlson Index calculated for all patients
- Patient-level aggregations correct
- 15 chronic condition flags set
- 59 problem records with full enrichment

✅ **PostgreSQL:**
- Table created with 13 indexes
- 59 problem records loaded
- Verification queries return expected results
- Data integrity maintained (ICNs, codes, dates)

---

## Next Steps

After successful ETL pipeline testing, the following phases remain:

**Phase 4: VistA RPC Mock Data (Days 10-11)**
- Create ORQQPL LIST RPC mock data with T-notation dates
- Enable "Refresh VistA" real-time overlay

**Phase 5: Database Query Layer (Day 12)**
- Create `app/db/patient_problems.py` query functions
- Implement filtering, sorting, pagination

**Phase 6: UI Implementation (Days 13-16)**
- API endpoints (6 total)
- 2x1 dashboard widget with Charlson Index badge
- Full page view with ICD-10 category grouping
- "Refresh VistA" button integration

**Phase 7: AI Integration (Days 17-18)**
- Update AI system prompts with `assess_disease_burden` tool
- Enable Charlson-aware clinical insights

---

## File Manifest

**ETL Scripts (3 files):**
- `etl/bronze_problems.py` - Extract from SQL Server to Parquet
- `etl/silver_problems.py` - Harmonize and deduplicate
- `etl/gold_problems.py` - Calculate Charlson Index

**Database Files (2 files):**
- `db/ddl/create_patient_problems_table.sql` - PostgreSQL DDL
- `etl/load_problems.py` - Load Gold to PostgreSQL

**Mock Data Files (8 files):**
- `mock/sql-server/cdwwork/create/Dim.ICD10.sql`
- `mock/sql-server/cdwwork/insert/Dim.ICD10.sql`
- `mock/sql-server/cdwwork/create/Dim.CharlsonMapping.sql`
- `mock/sql-server/cdwwork/insert/Dim.CharlsonMapping.sql`
- `mock/sql-server/cdwwork/create/Outpat.ProblemList.sql`
- `mock/sql-server/cdwwork/insert/Outpat.ProblemList.sql`
- `mock/sql-server/cdwwork2/create/EncMill.ProblemList.sql`
- `mock/sql-server/cdwwork2/insert/EncMill.ProblemList.sql`

**Verification Script:**
- `scripts/verify_problems_mock_data.sql`

**Documentation:**
- `docs/spec/problems-design.md` - Complete design specification
- `docs/spec/problems-etl-testing-guide.md` - This file

---

**End of Testing Guide**
