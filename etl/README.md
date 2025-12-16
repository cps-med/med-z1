# ETL Pipeline - med-z1

ETL functionality to retrieve, process, and store data from CDWWork (SQL Server) into the Medallion Architecture (Bronze/Silver/Gold) and PostgreSQL serving database.

## Overview

The **etl** subsystem implements a Medallion Architecture data pipeline with three layers:

- **Bronze Layer**: Raw data extraction from source systems to Parquet files in MinIO
- **Silver Layer**: Cleaned, validated, and joined data with resolved lookups
- **Gold Layer**: Business-logic enriched, denormalized views ready for serving

Data flows from SQL Server (CDWWork mock database) → Bronze Parquet → Silver Parquet → Gold Parquet → PostgreSQL serving database.

## Architecture

```
Source Systems          Bronze Layer         Silver Layer         Gold Layer        Serving Database
──────────────          ────────────         ────────────         ──────────        ────────────────
SQL Server (CDWWork) ──┐
                       ├──> Parquet ──┐
Tables:                │    (MinIO)   │
- Dim.VitalType        │              ├──────> Parquet ──┐
- Vital.VitalSign      │              │        (MinIO)   │
- Dim.VitalQualifier   │              │                  ├──────> Parquet ────────> PostgreSQL
- Vital.VitalSignQual  │              │                  │        (MinIO)           (medz1)
- SPatient.Patient     │              │                  │
- SPatient.Address     │              │                  │                          Tables:
- Inpat.Inpatient      │              │                  │                           - patient_vitals
- RxOut.RxOutpat       │              │                  │                           - patient_demographics
- etc.                 │              │                  │                           - patient_flags
                       └──────────────┴──────────────────┘                           - etc.

Key Characteristics:
- Bronze: Schema-on-read, minimal transformation
- Silver: Schema-on-write, cleaned & joined
- Gold: Business logic, aggregations, denormalized
```

## Implemented ETL Scripts

### Patient Demographics
- **bronze_patient.py** - Extract patient demographics, addresses, insurance from CDWWork
- **silver_patient.py** - Clean and join patient data, resolve lookups
- **gold_patient.py** - Create patient-centric view with combined demographics
- **load_patient.py** - Load into PostgreSQL patient_demographics table

**Run:**
```bash
python -m etl.bronze_patient
python -m etl.silver_patient
python -m etl.gold_patient
python -m etl.load_patient
```

### Patient Flags
- **bronze_patient_flags.py** - Extract flag definitions, assignments, history from CDWWork
- **silver_patient_flags.py** - Clean and join flag data
- **gold_patient_flags.py** - Create patient-flag denormalized view
- **load_patient_flags.py** - Load into PostgreSQL patient_flags table

**Run:**
```bash
python -m etl.bronze_patient_flags
python -m etl.silver_patient_flags
python -m etl.gold_patient_flags
python -m etl.load_patient_flags
```

### Vitals (✅ Complete)
- **bronze_vitals.py** ✅ - Extract vitals, types, qualifiers from CDWWork (4 tables)
- **silver_vitals.py** ✅ - Clean, join, aggregate qualifiers as JSON
- **gold_vitals.py** ✅ - Add BMI calculation, abnormal flags, patient-centric view
- **load_vitals.py** ✅ - Load into PostgreSQL patient_vitals table

**Run:**
```bash
# Bronze: Extract 4 tables (10 types, 7,801 vitals, 16 qualifiers, 4,576 links)
python -m etl.bronze_vitals

# Silver: Clean and join (7,801 vitals, 19 columns)
python -m etl.silver_vitals

# Gold: Add business logic (8,730 vitals with BMI, flags)
python -m etl.gold_vitals

# Load: Insert into PostgreSQL (8,730 vitals)
python -m etl.load_vitals
```

**Status:** ✅ Complete (2025-12-13). All 4 pipeline stages operational.

### Laboratory Results (✅ ETL Complete - 2025-12-16)
- **bronze_labs.py** ✅ - Extract lab tests, results from CDWWork (2 tables: Dim.LabTest, Chem.LabChem)
- **silver_labs.py** ✅ - Clean, join, calculate reference range bounds, abnormal/critical flags
- **gold_labs.py** ✅ - Add patient ICN resolution, facility names, enriched metadata
- **load_labs.py** ✅ - Load into PostgreSQL patient_labs table

**Run:**
```bash
# Bronze: Extract 2 tables (17 test types, 58 lab results)
python -m etl.bronze_labs

# Silver: Clean and join (58 lab results, 27 columns with parsed ranges)
python -m etl.silver_labs

# Gold: Add patient identity and facility enrichment (58 results, 34 columns)
python -m etl.gold_labs

# Load: Insert into PostgreSQL (58 lab results)
python -m etl.load_labs
```

**Key Features:**
- Three-column location pattern: `location_id`, `collection_location`, `collection_location_type`
- Reference range parsing: Extracts low/high numeric bounds from text (e.g., "135 - 145" → 135.0, 145.0)
- Abnormal flag detection: `H` (High), `L` (Low), `H*` (Critical High), `L*` (Critical Low), `PANIC`
- LOINC code support: Standard lab test identifiers
- Panel grouping: Accession number links results from same specimen/panel
- Specimen type tracking: "Serum", "Whole Blood", etc.

**Lab Panels Implemented:**
- Basic Metabolic Panel (BMP): Sodium, Potassium, Chloride, CO2, BUN, Creatinine, Glucose
- Lipid Panel: Total Cholesterol, HDL, LDL, Triglycerides
- Complete Blood Count (CBC): WBC, RBC, Hemoglobin, Hematocrit, Platelets

**Data Volume:** 58 lab results across 36 synthetic patients (3 facilities: Sta3n 508, 516, 552)

**Status:** ✅ ETL Complete (2025-12-16). UI implementation pending.

**Important Note - Location Field Pattern:**
This domain was the first to implement the standardized three-column location pattern from day one. All location references include ID, name, and type for consistency with Vitals and Encounters domains. See `docs/architecture.md` Section 4.3 for detailed pattern documentation.

## Prerequisites

**Required Services:**
- SQL Server (CDWWork) running on localhost:1433
- MinIO running on localhost:9000 with bucket `med-z1`
- PostgreSQL (medz1 database) running
- Python 3.11+ virtual environment activated

**Environment Variables:**
Configured in `.env` at project root:
- `CDWWORK_DB_PASSWORD` - SQL Server sa password
- `MINIO_ENDPOINT` - MinIO endpoint (default: localhost:9000)
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- PostgreSQL connection variables

**Python Dependencies:**
```bash
pip install polars sqlalchemy pyarrow pyodbc psycopg2-binary python-dotenv
```

## Common Tasks

### Run Complete Pipeline (Example: Vitals)

```bash
# 1. Ensure SQL Server tables exist and have data
./mock/sql-server/cdwwork/vitals_setup.sh

# 2. Run Bronze extraction
python -m etl.bronze_vitals

# 3. Run Silver transformation
python -m etl.silver_vitals

# 4. Run Gold transformation (when implemented)
python -m etl.gold_vitals

# 5. Load into PostgreSQL (when implemented)
python -m etl.load_vitals
```

### Verify Data at Each Layer

**Bronze Layer:**
```bash
python -c "
from lake.minio_client import MinIOClient, build_bronze_path
minio = MinIOClient()
path = build_bronze_path('cdwwork', 'vital_sign', 'vital_sign_raw.parquet')
df = minio.read_parquet(path)
print(f'Bronze vitals: {len(df)} rows, {len(df.columns)} columns')
print(df.head(3))
"
```

**Silver Layer:**
```bash
python -c "
from lake.minio_client import MinIOClient, build_silver_path
minio = MinIOClient()
path = build_silver_path('vitals', 'vitals_cleaned.parquet')
df = minio.read_parquet(path)
print(f'Silver vitals: {len(df)} rows, {len(df.columns)} columns')
print(df.head(3))
"
```

**Gold Layer:**
```bash
python -c "
from lake.minio_client import MinIOClient, build_gold_path
minio = MinIOClient()
path = build_gold_path('vitals', 'vitals_final.parquet')
df = minio.read_parquet(path)
print(f'Gold vitals: {len(df)} rows, {len(df.columns)} columns')
print(df.head(3))
"
```

**PostgreSQL:**
```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM patient_vitals;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT * FROM patient_vitals LIMIT 3;"
```

## Troubleshooting

**"Connection refused" errors:**
- Check that SQL Server is running: `sqlcmd -S 127.0.0.1,1433 -U sa -P "${CDWWORK_DB_PASSWORD}" -Q "SELECT @@VERSION"`
- Verify MinIO is running: `curl http://localhost:9000`
- Verify PostgreSQL is running: `docker ps | grep postgres`

**"Module not found" errors:**
- Ensure virtual environment is activated: `which python` should show `.venv/bin/python`
- Install dependencies: `pip install -r requirements.txt`

**"Invalid column name" errors:**
- Verify source table schema matches query: `sqlcmd -Q "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'VitalSign'"`
- Check for typos in column names or wrong assumptions about schema

**"MinIO bucket does not exist" errors:**
- Create bucket via MinIO console: http://localhost:9001 (default login: minioadmin/minioadmin)
- Or use Python: `minio.ensure_bucket()`

## Design Documents

For detailed ETL pipeline specifications, see:
- `docs/vitals-design.md` - Complete Vitals implementation plan (Days 1-8)
- `docs/patient-flags-design.md` - Patient Flags implementation example
- `docs/demographics-enhancement-design.md` - Demographics ETL patterns

## Development Guidelines

**When creating new ETL scripts:**

1. **Follow the established pattern**: Bronze → Silver → Gold → Load
2. **Use Polars DataFrames**: Fast and memory-efficient
3. **Add logging**: Use Python's logging module with INFO level for progress
4. **Handle errors gracefully**: Check for missing files, null values, invalid data
5. **Write idempotent scripts**: Re-running should produce same results
6. **Document data transformations**: Add comments explaining business logic
7. **Use helper functions**: Reuse `build_bronze_path()`, `build_silver_path()`, etc.
8. **Test with small datasets first**: Verify logic before processing large tables

**File naming convention:**
- `bronze_<domain>.py` - Extract from source system
- `silver_<domain>.py` - Clean and join
- `gold_<domain>.py` - Business logic and aggregations
- `load_<domain>.py` - Load into serving database

**Example structure:**
```python
import polars as pl
from lake.minio_client import MinIOClient, build_bronze_path
import logging

logger = logging.getLogger(__name__)

def extract_my_table():
    """Extract MyTable from CDWWork to Bronze layer."""
    logger.info("Starting Bronze extraction: MyTable")
    minio_client = MinIOClient()

    # Query source system
    # Transform minimally
    # Write to Bronze

    logger.info(f"Bronze extraction complete: {len(df)} rows")
    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extract_my_table()
```

---

**Last Updated:** 2025-12-16
**Recent Changes:** Added Laboratory Results ETL documentation (complete Bronze/Silver/Gold/Load pipeline). Updated Vitals status to fully complete. Documented location field pattern standardization.
