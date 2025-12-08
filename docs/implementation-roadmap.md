# med-z1 Implementation Roadmap – Vertical Slice Strategy

December 7, 2025 • Document version v1.0

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Strategic Approach: Vertical Slice](#2-strategic-approach-vertical-slice)
3. [Why Not "ETL First" or "UI First"?](#3-why-not-etl-first-or-ui-first)
4. [Phase 1: Minimal Viable Data Pipeline](#4-phase-1-minimal-viable-data-pipeline)
5. [Phase 2: Topbar UI with Real Data](#5-phase-2-topbar-ui-with-real-data)
6. [Phase 3: Expand Horizontally](#6-phase-3-expand-horizontally)
7. [Phase 4: Additional Domains](#7-phase-4-additional-domains)
8. [Phase 5: AI/ML and Advanced Features](#8-phase-5-aiml-and-advanced-features)
9. [Gold Schema Design](#9-gold-schema-design)
10. [PostgreSQL Schema](#10-postgresql-schema)
11. [ETL Implementation Patterns](#11-etl-implementation-patterns)
12. [Timeline and Priorities](#12-timeline-and-priorities)
13. [Success Criteria](#13-success-criteria)
14. [Related Documentation](#14-related-documentation)

---

## 1. Executive Summary

This document provides tactical, step-by-step guidance for implementing the med-z1 longitudinal health record viewer. It recommends a **vertical slice strategy** that builds one complete end-to-end data flow (from mock CDW to UI) before expanding to additional clinical domains.

### 1.1 Core Recommendation

**Build the smallest possible end-to-end system first:**

```text
Mock SQL Server (CDWWork.SPatient.SPatient table)
    ↓
Bronze Layer (MinIO.med-data.Parquet) - Patient demographics extract
    ↓
Silver Layer (MinIO.med-data.Parquet) - Cleaned patient data
    ↓
Gold Layer (MinIO.med-data.Parquet) - Patient demographics view
    ↓
PostgreSQL Serving DB - patient_demographics table
    ↓
FastAPI + HTMX UI - Patient-aware topbar with search
```

**Then expand horizontally** to other clinical domains (flags, medications, encounters, labs, etc.).

### 1.2 Key Benefits

- ✅ Validates entire architecture with real data in **2 weeks**
- ✅ Proves medallion pattern works before scaling
- ✅ Delivers functional UI quickly (patient search, CCOW integration)
- ✅ Reveals data quality issues early
- ✅ Provides tangible progress for demos/stakeholders
- ✅ Establishes reusable patterns for additional domains

### 1.3 Timeline Overview

| Phase | Focus | Duration | Deliverable |
|-------|-------|----------|-------------|
| **Phase 1** | Minimal Viable Data Pipeline | 1-2 weeks | Bronze/Silver/Gold Parquet + PostgreSQL for patient demographics |
| **Phase 2** | Topbar UI with Real Data | 1 week | Functional patient search, CCOW integration, 37 real patients |
| **Phase 3** | Patient Flags Domain | 1 week | Flags pipeline + "View Flags" modal working |
| **Phase 4** | Medications Domain | 1-2 weeks | RxOut/BCMA pipeline + Medications UI page |
| **Phase 5** | Expand & Polish | Ongoing | More domains, CDWWork1, AI/ML, production hardening |

**Total Time to Functional Patient-Aware UI: 2-3 weeks**

---

## 2. Strategic Approach: Vertical Slice

### 2.1 What is a Vertical Slice?

A **vertical slice** means building one complete feature end-to-end through all layers of the architecture:

- ✅ Data source (Mock SQL Server)
- ✅ Bronze extraction
- ✅ Silver transformation
- ✅ Gold curation
- ✅ Serving database
- ✅ API endpoint
- ✅ UI component

Instead of building all of Bronze, then all of Silver, then all of Gold (horizontal layers), you build one narrow but complete path through the system.

### 2.2 Why Vertical Slices Work

**Proves the Architecture:**
- Validates that Mock CDW → Parquet → PostgreSQL → FastAPI → UI works
- Reveals integration issues early
- Demonstrates the medallion pattern with real data

**Enables Iteration:**
- Can demo a working feature quickly
- Get feedback from stakeholders
- Discover requirements gaps early

**Reduces Risk:**
- Don't invest weeks in ETL before knowing if the UI pattern works
- Don't build elaborate mocks that get thrown away
- Fail fast if architecture has issues

**Establishes Patterns:**
- First domain is hardest (establish conventions)
- Subsequent domains follow the proven pattern
- Copy-paste-modify for similar domains

### 2.3 The Vertical Slice for med-z1

**Our first vertical slice: Patient Demographics**

This is the perfect first slice because:
- ✅ Required for topbar UI (from `patient-topbar-redesign-spec.md`)
- ✅ Relatively simple data (one main table: `SPatient.SPatient`)
- ✅ No complex joins or aggregations
- ✅ Already have 37 patients in mock CDW
- ✅ Enables CCOW integration testing
- ✅ Foundation for all other clinical domains

---

## 3. Why Not "ETL First" or "UI First"?

### 3.1 The "ETL First" Trap

**Approach:** Build entire medallion pipeline for all domains before any UI work.

**Problems:**
- ⏱️ **Time to value:** 2-3 weeks before seeing any UI progress
- 🎯 **Misaligned priorities:** May build data transformations that UI doesn't need
- 🐛 **Late validation:** Can't test UI patterns work with real data
- 📊 **Data assumptions:** May discover data quality issues after UI is designed
- 😴 **Stakeholder fatigue:** Weeks of "backend work" with nothing to show

**Example Scenario:**
- Week 1-2: Build Bronze extractors for all domains
- Week 3: Build Silver transformations
- Week 4: Build Gold views
- Week 5: Finally start UI work
- Week 6: Discover UI needs different data shape, rework ETL

**Total Time to First Demo:** 5-6 weeks

### 3.2 The "UI First with Mocks" Trap

**Approach:** Build entire UI with hardcoded mock data, then connect real ETL later.

**Problems:**
- 🎭 **False progress:** UI looks good but has no real data
- 🔄 **Double work:** Build mocking infrastructure, then throw it away
- 🚫 **Wrong abstractions:** Mock data hides real-world complexity
- 🐛 **Edge cases:** Won't discover data quality issues until late
- 🎨 **Over-design:** May build UI features that real data can't support
- 😰 **Rework anxiety:** Team knows "the hard part" (real data) is still ahead

**Example Scenario:**
- Week 1: Build topbar with 3 hardcoded patients
- Week 2: Build search modal with mock data
- Week 3: Build medications page with mock data
- Week 4: Start building ETL, discover mock data was unrealistic
- Week 5-6: Rework UI to handle real data edge cases

**Total Time to Production-Ready System:** 6-7 weeks

### 3.3 The Vertical Slice Advantage

**Approach:** Build minimal ETL for one domain, then build UI for that domain with real data.

**Benefits:**
- ✅ **Fast validation:** Working system in 2 weeks
- ✅ **Real data from day 1:** No rework when switching from mocks
- ✅ **Architecture proof:** Validates entire stack works together
- ✅ **Incremental progress:** Each week delivers working features
- ✅ **Pattern establishment:** First domain is template for others
- ✅ **Stakeholder confidence:** Tangible progress every sprint

**Example Scenario:**
- Week 1-2: Build Bronze/Silver/Gold for patient demographics + PostgreSQL
- Week 2-3: Build topbar UI with real patient search (37 patients)
- Week 3: Add patient flags domain
- Week 4: Add medications domain
- Each week: Working, demo-able features

**Total Time to Production-Ready Core System:** 4-5 weeks

---

## 4. Phase 1: Minimal Viable Data Pipeline

**Duration:** 1-2 weeks

**Goal:** Build the smallest possible end-to-end data pipeline for patient demographics only.

### 4.1 What Success Looks Like

At the end of Phase 1, you will have:

- ✅ Bronze Parquet files with raw patient data from `SPatient.SPatient`
- ✅ Silver Parquet files with cleaned, standardized patient data
- ✅ Gold Parquet files with patient demographics view
- ✅ PostgreSQL database with `patient_demographics` table
- ✅ 37 patients loaded and queryable
- ✅ Python scripts to run the full pipeline end-to-end
- ✅ Proven pattern for Bronze → Silver → Gold → PostgreSQL

### 4.2 Data Scope

**Source Table:** `SPatient.SPatient` (in mock SQL Server CDWWork database)

**Patient Count:** 37 patients (from your existing insert script)

**Fields Needed for Topbar UI:**
- Patient ID (PatientSID, ICN)
- Name (last, first, middle)
- Demographics (DOB, sex, age)
- Identifiers (SSN, last 4 digits)
- Location (primary station/facility)

### 4.3 Architecture Flow

```text
┌─────────────────────────────────────────────────────────────┐
│ Mock SQL Server (CDWWork)                                   │
│   └─ SPatient.SPatient table (37 patients)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   etl/bronze_patient.py   │
              └───────────┬───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Bronze Layer (MinIO or local Parquet)                       │
│   lake/bronze/patient/patient_raw.parquet                   │
│   - Raw extract from SPatient.SPatient                      │
│   - All columns preserved                                   │
│   - SourceSystem, LoadDateTime added                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   etl/silver_patient.py   │
              └───────────┬───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Silver Layer (MinIO or local Parquet)                       │
│   lake/silver/patient/patient_cleaned.parquet               │
│   - Cleaned NULL/-1 values                                  │
│   - Standardized field names                                │
│   - Date formatting (ISO 8601)                              │
│   - Calculated fields (age from DOB)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌──────────────────────────────────────┐
        │   etl/gold_patient_demographics.py   │
        └───────────────┬──────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Gold Layer (MinIO or local Parquet)                         │
│ lake/gold/patient_demographics/patient_demographics.parquet │
│   - Final patient demographics view                         │
│   - Optimized for queries                                   │
│   - Includes facility names (joined from Dim.Sta3n)         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │   etl/load_postgress_patient.py   │
        └───────────────┬───────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL Serving Database                                 │
│   └─ patient_demographics table (37 rows)                   │
│      - Indexed for fast searches (ICN, name, SSN)           │
│      - Ready for FastAPI queries                            │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Detailed Task Breakdown

#### Task 1.1: Set Up Prerequisites (0.5 day)

**PostgreSQL Setup:**
```bash
# Install PostgreSQL (if not already installed)
brew install postgresql@16  # macOS

# or use Docker
docker run -d \
    --name postgres16 \
    -e POSTGRES_PASSWORD=yourpassword \
    -p 5432:5432 \
    -v postgres16-data:/var/lib/postgresql/data \
    postgres:16

# Test connection (if PSQL app installed on mac)
psql -h localhost -U postgres -d postgres16

# Test connection (via docker exec command)
docker exec -it postgres16 psql -U postgres -d postgres
```

**MinIO Setup (or use local filesystem):**
```bash
# Option A: Use MinIO
docker run -d --name med-insight-minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=password \
  -v $HOME/minio-data:/data \
  quay.io/minio/minio server /data --console-address ":9001"

# Option B: Use local filesystem (simpler for Phase 1)
mkdir -p lake/bronze lake/silver lake/gold
```

**Python Dependencies:**
```bash
pip install boto3 polars pyarrow psycopg2-binary sqlalchemy duckdb
```

**Deliverable:** PostgreSQL running, MinIO or local filesystem ready

---

#### Task 1.1.1: MinIO Storage Configuration (Option A - Recommended)

**Purpose:** Configure MinIO for Parquet file storage using the medallion architecture.

**Overview:**

MinIO provides S3-compatible object storage that enables:
- ✅ Scalable data lake architecture
- ✅ Easy integration with cloud deployments (AWS S3, Azure Blob, GCS)
- ✅ Cost-effective local development
- ✅ Production-ready storage with versioning and lifecycle policies
- ✅ Native support for analytics tools (DuckDB, Polars, Spark)

**Bucket Structure:**

The `med-z1` bucket organizes data using the medallion architecture:

```text
med-z1/
  ├── bronze/              # Raw data from source systems
  │   ├── cdwwork/         # CDWWork (VistA-like) data
  │   │   ├── patient/
  │   │   │   └── patient_raw.parquet
  │   │   ├── encounter/
  │   │   ├── medication/
  │   │   └── lab/
  │   └── cdwwork1/        # CDWWork1 (Oracle Health-like) data
  │       ├── patient/
  │       └── ...
  │
  ├── silver/              # Cleaned, harmonized data
  │   ├── patient/
  │   │   └── patient_cleaned.parquet
  │   ├── encounter/
  │   ├── medication/
  │   └── lab/
  │
  ├── gold/                # Query-optimized, curated views
  │   ├── patient_demographics/
  │   │   └── patient_demographics.parquet
  │   ├── medication_summary/
  │   ├── encounter_timeline/
  │   └── lab_results/
  │
  └── ai/                  # AI/ML artifacts (future use)
      ├── embeddings/
      ├── models/
      └── vectors/
```

**Configuration Setup:**

1. **Verify .env Configuration:**

Your `.env` file should include:

```bash
# MinIO S3-compatible storage configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY="admin#123#2025"
MINIO_BUCKET_NAME=med-z1
MINIO_USE_SSL=false
USE_MINIO=true
```

2. **Verify config.py Settings:**

The `config.py` module automatically loads MinIO configuration:

```python
from config import MINIO_CONFIG

# MINIO_CONFIG contains:
# {
#     "endpoint": "localhost:9000",
#     "access_key": "admin",
#     "secret_key": "admin#123#2025",
#     "bucket_name": "med-z1",
#     "use_ssl": False,
# }
```

3. **Verify MinIO Container is Running:**

```bash
# Check if MinIO is running
docker ps | grep minio

# Access MinIO admin console
# Open browser: http://localhost:9001
# Login with: admin / admin#123#2025
```

4. **Verify med-z1 Bucket Exists:**

```bash
# Option 1: Use MinIO admin console (http://localhost:9001)
# Navigate to "Buckets" and verify "med-z1" exists

# Option 2: Use Python
python -c "
from lake.minio_client import get_default_client
client = get_default_client()
print('MinIO client connected successfully!')
print(f'Bucket: {client.bucket_name}')
"
```

**Using the MinIO Client:**

The `lake/minio_client.py` module provides a reusable interface for all ETL operations.

**Basic Usage Examples:**

```python
# Import the MinIO client
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path, build_gold_path
import polars as pl

# Initialize client (uses config.py settings)
minio_client = MinIOClient()

# Example 1: Write Bronze layer Parquet
df_bronze = pl.DataFrame({
    "PatientSID": [1, 2, 3],
    "ICN": ["100001", "100002", "100003"],
    "PatientName": ["DOE,JOHN", "SMITH,JANE", "JOHNSON,BOB"],
})

# Build standardized path
bronze_path = build_bronze_path(
    source_system="cdwwork",
    domain="patient",
    filename="patient_raw.parquet"
)
# Result: "bronze/cdwwork/patient/patient_raw.parquet"

# Write to MinIO
minio_client.write_parquet(df_bronze, bronze_path)

# Example 2: Read Bronze layer Parquet
df_bronze = minio_client.read_parquet(bronze_path)
print(f"Read {len(df_bronze)} rows from Bronze layer")

# Example 3: Write Silver layer Parquet
df_silver = df_bronze.with_columns([
    pl.col("PatientSID").alias("patient_sid"),
    pl.col("ICN").alias("icn"),
])

silver_path = build_silver_path(
    domain="patient",
    filename="patient_cleaned.parquet"
)
# Result: "silver/patient/patient_cleaned.parquet"

minio_client.write_parquet(df_silver, silver_path)

# Example 4: Write Gold layer Parquet
df_gold = df_silver.select([
    pl.col("patient_sid"),
    pl.col("icn"),
])

gold_path = build_gold_path(
    view_name="patient_demographics",
    filename="patient_demographics.parquet"
)
# Result: "gold/patient_demographics/patient_demographics.parquet"

minio_client.write_parquet(df_gold, gold_path)

# Example 5: Check if file exists
if minio_client.exists(bronze_path):
    print("Bronze file exists!")

# Example 6: Read specific columns only
df_subset = minio_client.read_parquet(
    bronze_path,
    columns=["PatientSID", "ICN"]
)
```

**Complete ETL Example with MinIO:**

Here's how to update the ETL pipeline to use MinIO:

```python
# etl/bronze_patient.py (MinIO version)

import polars as pl
from datetime import datetime, timezone
import logging
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_patient_bronze():
    """Extract patient data from CDWWork to Bronze layer in MinIO."""

    logger.info("Starting Bronze patient extraction...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Connection string for source database
    conn_str = (
        f"mssql://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['database']}"
    )

    # Extract query
    query = """
    SELECT
        PatientSID,
        PatientIEN,
        Sta3n,
        PatientName,
        PatientLastName,
        PatientFirstName,
        PatientMiddleName,
        ICN,
        SSN,
        DOB,
        Sex,
        SourceSystemCode
    FROM SPatient.SPatient
    WHERE TestPatient = 'N' OR TestPatient = 'Y'
    """

    # Read data from source database
    df = pl.read_database(query, conn_str)

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="patient",
        filename="patient_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} patients written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extract_patient_bronze()
```

```python
# etl/silver_patient.py (MinIO version)

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def transform_patient_silver():
    """Transform Bronze patient data to Silver layer in MinIO."""

    logger.info("Starting Silver patient transformation...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Bronze Parquet from MinIO
    bronze_path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
    df = minio_client.read_parquet(bronze_path)

    # Calculate current age from DOB
    today = datetime.now(timezone.utc).date()

    # Transform and clean data
    df = df.with_columns([
        # Standardize field names
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("ICN").alias("icn"),
        pl.col("SSN").alias("ssn"),

        # Clean name fields
        pl.col("PatientLastName").str.strip().alias("name_last"),
        pl.col("PatientFirstName").str.strip().alias("name_first"),
        pl.col("PatientMiddleName").str.strip().alias("name_middle"),

        # Create display name
        (pl.col("PatientLastName").str.strip() + ", " +
         pl.col("PatientFirstName").str.strip()).alias("name_display"),

        # Handle dates
        pl.col("DOB").cast(pl.Date).alias("dob"),

        # Calculate age
        ((pl.lit(today).cast(pl.Date) - pl.col("DOB").cast(pl.Date)).dt.days() / 365.25)
            .cast(pl.Int32).alias("age"),

        # Standardize sex
        pl.col("Sex").str.strip().alias("sex"),

        # Extract SSN last 4
        pl.col("SSN").str.slice(-4).alias("ssn_last4"),

        # Station
        pl.col("Sta3n").cast(pl.Utf8).alias("primary_station"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Select final columns
    df = df.select([
        "patient_sid",
        "icn",
        "ssn",
        "ssn_last4",
        "name_last",
        "name_first",
        "name_middle",
        "name_display",
        "dob",
        "age",
        "sex",
        "primary_station",
        "source_system",
        "last_updated",
    ])

    # Build Silver path
    silver_path = build_silver_path("patient", "patient_cleaned.parquet")

    # Write to MinIO
    minio_client.write_parquet(df, silver_path)

    logger.info(
        f"Silver transformation complete: {len(df)} patients written to "
        f"s3://{minio_client.bucket_name}/{silver_path}"
    )

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    transform_patient_silver()
```

```python
# etl/gold_patient_demographics.py (MinIO version)

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def create_gold_patient_demographics():
    """Create Gold patient demographics view in MinIO."""

    logger.info("Starting Gold patient demographics creation...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Silver Parquet from MinIO
    silver_path = build_silver_path("patient", "patient_cleaned.parquet")
    df_patient = minio_client.read_parquet(silver_path)

    # Add station names (simplified for Phase 1)
    station_names = {
        "508": "Portland VA Medical Center",
        "516": "Bay Pines VA Healthcare System",
        "552": "Dayton VA Medical Center",
    }

    df_patient = df_patient.with_columns([
        pl.col("primary_station").map_dict(station_names, default="Unknown Facility")
            .alias("primary_station_name")
    ])

    # Create patient_key (use ICN)
    df_patient = df_patient.with_columns([
        pl.col("icn").alias("patient_key")
    ])

    # Final Gold schema
    df_gold = df_patient.select([
        "patient_key",
        "icn",
        "ssn",
        "ssn_last4",
        "name_last",
        "name_first",
        "name_middle",
        "name_display",
        "dob",
        "age",
        "sex",
        "primary_station",
        "primary_station_name",
        "source_system",
        "last_updated",
    ])

    # Build Gold path
    gold_path = build_gold_path(
        "patient_demographics",
        "patient_demographics.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df_gold, gold_path)

    logger.info(
        f"Gold creation complete: {len(df_gold)} patients written to "
        f"s3://{minio_client.bucket_name}/{gold_path}"
    )

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_gold_patient_demographics()
```

```python
# etl/load_postgres_patient.py (MinIO version)

import polars as pl
from sqlalchemy import create_engine
import logging
from config import DATABASE_URL  # PostgreSQL connection string
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_patient_demographics_to_postgres():
    """Load Gold patient demographics from MinIO to PostgreSQL."""

    logger.info("Loading patient demographics to PostgreSQL...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Gold Parquet from MinIO
    gold_path = build_gold_path(
        "patient_demographics",
        "patient_demographics.parquet"
    )
    df = minio_client.read_parquet(gold_path)

    # Convert Polars to Pandas (for SQLAlchemy compatibility)
    df_pandas = df.to_pandas()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load to PostgreSQL (truncate and reload)
    df_pandas.to_sql(
        "patient_demographics",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
    )

    logger.info(f"Loaded {len(df)} patients to PostgreSQL")

    # Verify
    result = engine.execute("SELECT COUNT(*) FROM patient_demographics").fetchone()
    logger.info(f"Verification: {result[0]} rows in patient_demographics table")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_patient_demographics_to_postgres()
```

**Testing Your MinIO Setup:**

```bash
# 1. Install new dependencies
pip install -r requirements.txt

# 2. Test MinIO connection
python -c "
from lake.minio_client import MinIOClient
import polars as pl

client = MinIOClient()
print(f'✓ Connected to MinIO at {client.endpoint}')
print(f'✓ Using bucket: {client.bucket_name}')

# Test write
test_df = pl.DataFrame({'test': [1, 2, 3]})
client.write_parquet(test_df, 'test/test.parquet')
print('✓ Write test passed')

# Test read
result_df = client.read_parquet('test/test.parquet')
print(f'✓ Read test passed: {len(result_df)} rows')

# Cleanup
client.delete('test/test.parquet')
print('✓ All tests passed!')
"

# 3. Run Bronze extraction
python etl/bronze_patient.py

# 4. Verify in MinIO console
# Open http://localhost:9001
# Navigate to med-z1 bucket
# Verify bronze/cdwwork/patient/patient_raw.parquet exists

# 5. Run full pipeline
python etl/run_patient_pipeline.py
```

**Benefits of MinIO Approach:**

- **Local Development:** Works identically to production S3 storage
- **Scalability:** Handles large datasets efficiently
- **Analytics Integration:** DuckDB, Polars, and Spark can read directly from MinIO
- **Versioning:** MinIO supports object versioning for audit trails
- **Cloud Migration:** Easy migration to AWS S3, Azure Blob, or GCS
- **Cost-Effective:** Free for local development, pay-as-you-go in cloud

**When to Use MinIO vs Local Filesystem:**

Use **MinIO** (Option A) if:
- ✅ Building production-ready system
- ✅ Need cloud deployment path
- ✅ Working with large datasets (>1GB)
- ✅ Need analytics tool integration
- ✅ Want object versioning/lifecycle policies

Use **Local Filesystem** (Option B) if:
- ✅ Rapid prototyping only
- ✅ Very small datasets (<100MB)
- ✅ No cloud deployment plans
- ✅ Minimal dependencies preferred

**Deliverable:** MinIO configured, `lake/minio_client.py` module working, test Parquet files can be written and read

---

#### Task 1.2: Create Gold Schema Design (0.5 day)

**File:** `docs/schemas/patient_demographics_gold_schema.md`

Document the Gold layer schema (see [Section 9](#9-gold-schema-design) below).

**Deliverable:** Schema definition document

---

#### Task 1.3: Create PostgreSQL Schema (0.5 day)

**File:** `db/ddl/patient_demographics.sql`

See [Section 10](#10-postgresql-schema) for complete SQL.

**Test:**
```bash
psql -h localhost -U postgres -d medz1 -f db/ddl/patient_demographics.sql
```

**Deliverable:** `patient_demographics` table created in PostgreSQL

---

#### Task 1.4: Build Bronze Patient Extractor (1 day)

**File:** `etl/bronze_patient.py`

**Purpose:** Extract raw data from `SPatient.SPatient` and write to Bronze Parquet.

**Example Code Skeleton:**
```python
# etl/bronze_patient.py

import polars as pl
from datetime import datetime, timezone
import logging
from config import CDWWORK_DB_CONFIG

logger = logging.getLogger(__name__)


def extract_patient_bronze():
    """Extract patient data from CDWWork to Bronze layer."""

    logger.info("Starting Bronze patient extraction...")

    # Connection string
    conn_str = f"mssql://{CDWWORK_DB_CONFIG['user']}:{CDWWORK_DB_CONFIG['password']}@{CDWWORK_DB_CONFIG['server']}/{CDWWORK_DB_CONFIG['database']}"

    # Extract query
    query = """
    SELECT
        PatientSID,
        PatientIEN,
        Sta3n,
        PatientName,
        PatientLastName,
        PatientFirstName,
        PatientMiddleName,
        Confidential,
        TestPatient,
        PatientStatus,
        PatientType,
        PatientTypeCode,
        ICN,
        ScrSSN,
        SSN,
        SSNUnknown,
        SSNVerificationStatus,
        Pseudo,
        Restricted,
        AgeInYears,
        DOB,
        DOD,
        DeceasedDateTime,
        Deceased,
        Sex,
        Gender,
        Religion,
        ReligionSID,
        MaritalStatus,
        MaritalStatusSID,
        -- ... additional fields as needed
        SourceSystemCode
    FROM SPatient.SPatient
    WHERE TestPatient = 'N'  -- Exclude test patients for production
       OR TestPatient = 'Y'  -- But include for dev/testing
    """

    # Read data
    df = pl.read_database(query, conn_str)

    # Add metadata
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Write to Bronze Parquet
    output_path = "lake/bronze/patient/patient_raw.parquet"
    df.write_parquet(output_path)

    logger.info(f"Bronze extraction complete: {len(df)} patients written to {output_path}")

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extract_patient_bronze()
```

**Test:**
```bash
python etl/bronze_patient.py
# Should see: "Bronze extraction complete: 37 patients written to lake/bronze/patient/patient_raw.parquet"

# Verify Parquet file
python -c "import polars as pl; print(pl.read_parquet('lake/bronze/patient/patient_raw.parquet').head())"
```

**Deliverable:** Bronze Parquet file with 37 patients

---

#### Task 1.5: Build Silver Patient Transformer (1 day)

**File:** `etl/silver_patient.py`

**Purpose:** Clean and standardize patient data.

**Transformations:**
- Handle NULLs and -1 sentinel values
- Standardize field names (snake_case)
- Format dates (ISO 8601)
- Calculate age from DOB
- Clean string fields (trim whitespace)
- Standardize sex/gender codes

**Example Code Skeleton:**
```python
# etl/silver_patient.py

import polars as pl
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def transform_patient_silver():
    """Transform Bronze patient data to Silver layer."""

    logger.info("Starting Silver patient transformation...")

    # Read Bronze
    df = pl.read_parquet("lake/bronze/patient/patient_raw.parquet")

    # Calculate current age from DOB
    today = datetime.now(timezone.utc).date()

    df = df.with_columns([
        # Standardize field names
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("ICN").alias("icn"),
        pl.col("SSN").alias("ssn"),

        # Clean name fields
        pl.col("PatientLastName").str.strip().alias("name_last"),
        pl.col("PatientFirstName").str.strip().alias("name_first"),
        pl.col("PatientMiddleName").str.strip().alias("name_middle"),

        # Create display name
        (pl.col("PatientLastName").str.strip() + ", " +
         pl.col("PatientFirstName").str.strip()).alias("name_display"),

        # Handle dates
        pl.col("DOB").cast(pl.Date).alias("dob"),

        # Calculate age
        ((pl.lit(today).cast(pl.Date) - pl.col("DOB").cast(pl.Date)).dt.days() / 365.25)
            .cast(pl.Int32).alias("age"),

        # Standardize sex
        pl.col("Sex").str.strip().alias("sex"),

        # Extract SSN last 4
        pl.col("SSN").str.slice(-4).alias("ssn_last4"),

        # Station
        pl.col("Sta3n").cast(pl.Utf8).alias("primary_station"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Select final columns
    df = df.select([
        "patient_sid",
        "icn",
        "ssn",
        "ssn_last4",
        "name_last",
        "name_first",
        "name_middle",
        "name_display",
        "dob",
        "age",
        "sex",
        "primary_station",
        "source_system",
        "last_updated",
    ])

    # Write to Silver Parquet
    output_path = "lake/silver/patient/patient_cleaned.parquet"
    df.write_parquet(output_path)

    logger.info(f"Silver transformation complete: {len(df)} patients written to {output_path}")

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    transform_patient_silver()
```

**Test:**
```bash
python etl/silver_patient.py

# Verify Silver Parquet
python -c "import polars as pl; df = pl.read_parquet('lake/silver/patient/patient_cleaned.parquet'); print(df.head()); print(f'Columns: {df.columns}')"
```

**Deliverable:** Silver Parquet file with cleaned patient data

---

#### Task 1.6: Build Gold Patient Demographics View (1 day)

**File:** `etl/gold_patient_demographics.py`

**Purpose:** Create final patient demographics view, joining with facility names.

**Example Code Skeleton:**
```python
# etl/gold_patient_demographics.py

import polars as pl
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def create_gold_patient_demographics():
    """Create Gold patient demographics view."""

    logger.info("Starting Gold patient demographics creation...")

    # Read Silver patient data
    df_patient = pl.read_parquet("lake/silver/patient/patient_cleaned.parquet")

    # Read station dimension (if you have it)
    # For Phase 1, you can hardcode station names or skip this join
    station_names = {
        "508": "Portland VA Medical Center",
        "516": "Bay Pines VA Healthcare System",
        "552": "Dayton VA Medical Center",
    }

    # Add station names
    df_patient = df_patient.with_columns([
        pl.col("primary_station").map_dict(station_names, default="Unknown Facility")
            .alias("primary_station_name")
    ])

    # Create patient_key (use ICN or PatientSID)
    df_patient = df_patient.with_columns([
        pl.col("icn").alias("patient_key")
    ])

    # Final Gold schema
    df_gold = df_patient.select([
        "patient_key",
        "icn",
        "ssn",
        "ssn_last4",
        "name_last",
        "name_first",
        "name_middle",
        "name_display",
        "dob",
        "age",
        "sex",
        "primary_station",
        "primary_station_name",
        "source_system",
        "last_updated",
    ])

    # Write to Gold Parquet
    output_path = "lake/gold/patient_demographics/patient_demographics.parquet"
    df_gold.write_parquet(output_path)

    logger.info(f"Gold creation complete: {len(df_gold)} patients written to {output_path}")

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_gold_patient_demographics()
```

**Test:**
```bash
python etl/gold_patient_demographics.py

# Verify Gold Parquet
python -c "import polars as pl; df = pl.read_parquet('lake/gold/patient_demographics/patient_demographics.parquet'); print(df.head()); print(f'Total patients: {len(df)}')"
```

**Deliverable:** Gold Parquet file with patient demographics view

---

#### Task 1.7: Load Gold into PostgreSQL (0.5 day)

**File:** `etl/load_postgres_patient.py`

**Purpose:** Read Gold Parquet and load into PostgreSQL.

**Example Code Skeleton:**
```python
# etl/load_postgres_patient.py

import polars as pl
from sqlalchemy import create_engine
import logging
from config import DATABASE_URL  # PostgreSQL connection string

logger = logging.getLogger(__name__)


def load_patient_demographics_to_postgres():
    """Load Gold patient demographics to PostgreSQL."""

    logger.info("Loading patient demographics to PostgreSQL...")

    # Read Gold Parquet
    df = pl.read_parquet("lake/gold/patient_demographics/patient_demographics.parquet")

    # Convert Polars to Pandas (for SQLAlchemy compatibility)
    df_pandas = df.to_pandas()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load to PostgreSQL (truncate and reload)
    df_pandas.to_sql(
        "patient_demographics",
        engine,
        if_exists="replace",  # Or "append" if you want to preserve existing data
        index=False,
        method="multi",  # Faster bulk insert
    )

    logger.info(f"Loaded {len(df)} patients to PostgreSQL")

    # Verify
    result = engine.execute("SELECT COUNT(*) FROM patient_demographics").fetchone()
    logger.info(f"Verification: {result[0]} rows in patient_demographics table")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_patient_demographics_to_postgres()
```

**Test:**
```bash
python etl/load_postgres_patient.py

# Verify in PostgreSQL
psql -h localhost -U postgres -d medz1 -c "SELECT COUNT(*) FROM patient_demographics;"
# Should show: 37

psql -h localhost -U postgres -d medz1 -c "SELECT icn, name_display, age, sex FROM patient_demographics LIMIT 5;"
```

**Deliverable:** PostgreSQL `patient_demographics` table populated with 37 patients

---

#### Task 1.8: Create End-to-End Pipeline Script (0.5 day)

**File:** `etl/run_patient_pipeline.py`

**Purpose:** Orchestrate the entire pipeline in correct order.

```python
# etl/run_patient_pipeline.py

import logging
from etl.bronze_patient import extract_patient_bronze
from etl.silver_patient import transform_patient_silver
from etl.gold_patient_demographics import create_gold_patient_demographics
from etl.load_postgres_patient import load_patient_demographics_to_postgres

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_patient_pipeline():
    """Run the complete patient demographics pipeline."""

    logger.info("=" * 60)
    logger.info("Starting Patient Demographics Pipeline")
    logger.info("=" * 60)

    try:
        # Step 1: Bronze extraction
        logger.info("\n[1/4] Bronze Extraction")
        extract_patient_bronze()

        # Step 2: Silver transformation
        logger.info("\n[2/4] Silver Transformation")
        transform_patient_silver()

        # Step 3: Gold creation
        logger.info("\n[3/4] Gold Creation")
        create_gold_patient_demographics()

        # Step 4: Load to PostgreSQL
        logger.info("\n[4/4] PostgreSQL Load")
        load_patient_demographics_to_postgres()

        logger.info("\n" + "=" * 60)
        logger.info("Pipeline Complete!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_patient_pipeline()
```

**Test:**
```bash
python etl/run_patient_pipeline.py
```

**Deliverable:** Working end-to-end pipeline

---

### 4.5 Phase 1 Success Criteria

At the end of Phase 1, verify:

- [ ] Bronze Parquet exists: `lake/bronze/patient/patient_raw.parquet`
- [ ] Silver Parquet exists: `lake/silver/patient/patient_cleaned.parquet`
- [ ] Gold Parquet exists: `lake/gold/patient_demographics/patient_demographics.parquet`
- [ ] PostgreSQL table `patient_demographics` has 37 rows
- [ ] Can query patients by ICN: `SELECT * FROM patient_demographics WHERE icn = '100001'`
- [ ] Can search by name: `SELECT * FROM patient_demographics WHERE name_last ILIKE 'DOOREE%'`
- [ ] All 37 patients have valid age, sex, ssn_last4
- [ ] Pipeline runs end-to-end without errors

---

## 5. Phase 2: Topbar UI with Real Data

**Duration:** 1 week

**Goal:** Implement the patient-aware topbar using real PostgreSQL data.

### 5.1 What Success Looks Like

At the end of Phase 2, you will have:

- ✅ Database query layer (`app/db/patient.py`)
- ✅ Patient API routes (`app/routes/patient.py`)
- ✅ CCOW client utility (`app/utils/ccow_client.py`)
- ✅ Topbar UI with patient demographics display
- ✅ Patient search modal with real search results
- ✅ CCOW integration (query on startup, set on selection, manual refresh)
- ✅ All 37 patients searchable by name, SSN, ICN
- ✅ Fully functional patient-aware application

### 5.2 Detailed Task Breakdown

#### Task 2.1: Create Database Query Layer (1 day)

**File:** `app/db/patient.py`

**Purpose:** Encapsulate all patient database queries.

```python
# app/db/patient.py

from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Or use QueuePool for production
    echo=False,
)


def get_patient_demographics(icn: str) -> Optional[Dict[str, Any]]:
    """
    Get patient demographics by ICN.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with patient demographics or None if not found
    """
    query = text("""
        SELECT
            patient_key,
            icn,
            ssn_last4,
            name_last,
            name_first,
            name_middle,
            name_display,
            dob,
            age,
            sex,
            primary_station,
            primary_station_name,
            source_system,
            last_updated
        FROM patient_demographics
        WHERE icn = :icn
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn}).fetchone()

        if result:
            return {
                "patient_key": result[0],
                "icn": result[1],
                "ssn_last4": result[2],
                "name_last": result[3],
                "name_first": result[4],
                "name_middle": result[5],
                "name_display": result[6],
                "dob": str(result[7]),  # Convert date to string
                "age": result[8],
                "sex": result[9],
                "primary_station": result[10],
                "primary_station_name": result[11],
                "source_system": result[12],
                "last_updated": str(result[13]),
            }

        return None


def search_patients(
    query: str,
    search_type: str = "name",
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for patients.

    Args:
        query: Search query string
        search_type: Type of search - 'name', 'ssn', 'icn', 'edipi'
        limit: Maximum number of results

    Returns:
        List of patient dictionaries
    """
    if search_type == "name":
        sql_query = text("""
            SELECT
                icn,
                name_display,
                dob,
                age,
                sex,
                ssn_last4,
                primary_station
            FROM patient_demographics
            WHERE name_last ILIKE :query OR name_first ILIKE :query
            ORDER BY name_last, name_first
            LIMIT :limit
        """)
        params = {"query": f"%{query}%", "limit": limit}

    elif search_type == "ssn":
        sql_query = text("""
            SELECT
                icn,
                name_display,
                dob,
                age,
                sex,
                ssn_last4,
                primary_station
            FROM patient_demographics
            WHERE ssn_last4 = :query
            ORDER BY name_last, name_first
            LIMIT :limit
        """)
        params = {"query": query, "limit": limit}

    elif search_type == "icn":
        sql_query = text("""
            SELECT
                icn,
                name_display,
                dob,
                age,
                sex,
                ssn_last4,
                primary_station
            FROM patient_demographics
            WHERE icn = :query
            LIMIT :limit
        """)
        params = {"query": query, "limit": limit}

    else:
        # EDIPI not implemented yet
        return []

    with engine.connect() as conn:
        results = conn.execute(sql_query, params).fetchall()

        return [
            {
                "icn": row[0],
                "name_display": row[1],
                "dob": str(row[2]),
                "age": row[3],
                "sex": row[4],
                "ssn_last4": row[5],
                "station": row[6],
            }
            for row in results
        ]
```

**Test:**
```python
# Test the query functions
from app.db.patient import get_patient_demographics, search_patients

# Test get by ICN
patient = get_patient_demographics("100001")
print(patient)

# Test search by name
results = search_patients("DOOREE", "name")
print(results)
```

**Deliverable:** Working database query layer

---

#### Task 2.2: Implement Patient Routes (1 day)

Use the implementation from `patient-topbar-redesign-spec.md` Section 10.

**Files:**
- `app/routes/patient.py` - All patient API endpoints
- `app/utils/ccow_client.py` - CCOW client utility

**Key Changes from Spec:**
- Replace mock data with `get_patient_demographics()` and `search_patients()` calls
- Import from `app.db.patient`

**Deliverable:** Working API endpoints that return real data

---

#### Task 2.3: Implement Topbar Templates (2 days)

Use the templates from `patient-topbar-redesign-spec.md` Section 7.

**Files:**
- `app/templates/base.html` - Modified topbar
- `app/templates/partials/patient_header.html`
- `app/templates/partials/patient_search_modal.html`
- `app/templates/partials/patient_search_results.html`
- `app/templates/partials/patient_flags_modal.html` (placeholder)

**Deliverable:** Working topbar UI

---

#### Task 2.4: Add CSS and JavaScript (0.5 day)

Use the CSS and JavaScript from `patient-topbar-redesign-spec.md` Sections 8 and 9.

**Files:**
- `app/static/styles.css` - Add modal and patient header styles
- `app/static/app.js` - Add modal handling

**Deliverable:** Styled, functional modals

---

#### Task 2.5: Integration Testing (0.5 day)

Test all workflows:

- [ ] Start app → CCOW query → Patient header displays if patient in vault
- [ ] Start app → No CCOW patient → "No patient selected" message
- [ ] Click "Select Patient" → Modal opens
- [ ] Type "DOOREE" → Search results appear
- [ ] Click patient → CCOW updated, header refreshes, modal closes
- [ ] Click "Refresh Patient" → Re-queries CCOW, header updates
- [ ] Search by SSN last 4 → Correct results
- [ ] Search by ICN → Exact match

**Deliverable:** Fully functional patient-aware topbar

---

### 5.3 Phase 2 Success Criteria

- [ ] Can search all 37 patients by name
- [ ] Can search by SSN last 4
- [ ] Can search by ICN
- [ ] Patient demographics display correctly in topbar
- [ ] CCOW integration works end-to-end
- [ ] Modal opens and closes smoothly
- [ ] "View Patient Flags" button disabled when no patient
- [ ] Responsive design works on mobile/tablet
- [ ] No console errors in browser

---

## 6. Phase 3: Expand Horizontally

**Duration:** 1 week

**Goal:** Add Patient Flags as the second clinical domain, proving the pattern scales.

### 6.1 Why Patient Flags Next?

- ✅ Completes the topbar UI ("View Patient Flags" button)
- ✅ Relatively simple domain (one table)
- ✅ Demonstrates you can add new domains following established pattern
- ✅ Provides clinical value (safety alerts)

### 6.2 Tasks

1. **Add Flags to Mock CDW** (if not present)
   - Create `Flag.Flag` table in CDWWork
   - Add sample flags for 5-10 patients

2. **Build Flags ETL Pipeline**
   - `etl/bronze_flag.py`
   - `etl/silver_flag.py`
   - `etl/gold_patient_flags.py`
   - PostgreSQL `patient_flags` table

3. **Implement Flags API**
   - `GET /api/patient/{icn}/flags`
   - `GET /api/patient/flags-content`

4. **Implement Flags Modal UI**
   - Update `patient_flags_modal.html` with real template
   - Display flags with categories, dates, narratives

5. **Update Patient Header**
   - Enable "View Flags" button when patient selected
   - Show flag count badge

### 6.3 Success Criteria

- [ ] Flags data flows from Mock CDW → Bronze → Silver → Gold → PostgreSQL
- [ ] "View Patient Flags" button shows badge with count
- [ ] Clicking button opens modal with formatted flags
- [ ] Flags display categories, dates, narratives
- [ ] Modal handles patients with 0 flags gracefully

---

## 7. Phase 4: Additional Domains

**Duration:** 1-2 weeks per domain

**Goal:** Add Medications, Encounters, Labs, etc. following the proven pattern.

### 7.1 Recommended Domain Order

1. **Medications (RxOut + BCMA)** - Complex (multiple tables), high clinical value
2. **Encounters (Inpat)** - Foundation for timeline views
3. **Labs (LabChem)** - Demonstrates trending/charting
4. **Vitals** - Similar to Labs
5. **Orders** - Complex workflow domain
6. **Notes/Documents** - Text-heavy domain

### 7.2 Pattern for Each Domain

For each new domain, repeat:

1. **ETL Pipeline:**
   - Bronze extraction (may need multiple source tables)
   - Silver transformation (harmonize if from CDWWork1)
   - Gold view (query-optimized)
   - PostgreSQL table(s)

2. **API Endpoints:**
   - `GET /api/patient/{icn}/{domain}` - Get data for patient
   - Additional endpoints as needed (filters, date ranges, etc.)

3. **UI Page:**
   - Create dedicated page (e.g., `/patient/{icn}/medications`)
   - Add to sidebar navigation
   - Implement domain-specific visualizations

4. **Testing:**
   - Verify data quality
   - Test UI interactions
   - Performance testing

---

## 8. Phase 5: AI/ML and Advanced Features

**Duration:** Ongoing (3-6 weeks for initial features)

**Goal:** Add AI-assisted features using Gold Parquet data.

### 8.1 AI/ML Use Cases

**Phase 5A: Chart Overview Summarization**
- Read Gold Parquet for patient (encounters, meds, problems, labs)
- Generate natural language summary
- Display in Patient Overview page

**Phase 5B: Drug-Drug Interaction Detection**
- Read Gold medications Parquet
- Query DDI knowledge base
- Highlight risky combinations

**Phase 5C: Patient Flag-Aware Summaries**
- Incorporate flags into AI narrative
- Generate risk-aware care recommendations

### 8.2 Architecture

```
Gold Parquet (DuckDB/Polars queries)
    ↓
AI/ML Service (LangChain/LangGraph)
    ↓
OpenAI/Anthropic API
    ↓
FastAPI Endpoint
    ↓
UI Display (with "AI-generated" disclaimer)
```

**Key Design Decisions:**
- AI/ML reads directly from Gold Parquet (no need for PostgreSQL)
- Use DuckDB for fast analytical queries
- Cache AI responses to reduce API costs
- Always label AI-generated content

---

## 9. Gold Schema Design

### 9.1 Patient Demographics Gold Schema

**File:** `lake/gold/patient_demographics/patient_demographics.parquet`

**Schema:**

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `patient_key` | string | Internal key (ICN) | Derived |
| `icn` | string | Integrated Care Number | `SPatient.SPatient.ICN` |
| `ssn` | string | Full SSN (encrypted in prod) | `SPatient.SPatient.SSN` |
| `ssn_last4` | string | Last 4 digits for display | Derived from SSN |
| `name_last` | string | Last name | `SPatient.SPatient.PatientLastName` |
| `name_first` | string | First name | `SPatient.SPatient.PatientFirstName` |
| `name_middle` | string | Middle name | `SPatient.SPatient.PatientMiddleName` |
| `name_display` | string | Formatted name ("LAST, First") | Derived |
| `dob` | date | Date of birth | `SPatient.SPatient.DOB` |
| `age` | integer | Current age | Calculated from DOB |
| `sex` | string | Biological sex (M/F/U) | `SPatient.SPatient.Sex` |
| `gender` | string | Gender identity | `SPatient.SPatient.Gender` |
| `primary_station` | string | Sta3n code | `SPatient.SPatient.Sta3n` |
| `primary_station_name` | string | Facility name | Join from `Dim.Sta3n` |
| `veteran_status` | string | "VETERAN", "NON-VETERAN", etc. | `SPatient.SPatient.PatientType` |
| `source_system` | string | "CDWWork" or "CDWWork1" | Metadata |
| `last_updated` | timestamp | ETL timestamp | Metadata |

**Design Notes:**
- `patient_key` = `icn` for simplicity (no complex merged identities yet)
- `ssn` should be encrypted/hashed in production (plain text in dev)
- `age` is calculated at ETL time (recalculate daily or on query)
- `primary_station_name` requires join with `Dim.Sta3n` table

---

## 10. PostgreSQL Schema

### 10.1 Patient Demographics Table

**File:** `db/ddl/patient_demographics.sql`

```sql
-- db/ddl/patient_demographics.sql

-- Drop table if exists (for development)
DROP TABLE IF EXISTS patient_demographics CASCADE;

-- Create patient demographics table
CREATE TABLE patient_demographics (
    patient_key VARCHAR(50) PRIMARY KEY,
    icn VARCHAR(50) UNIQUE NOT NULL,
    ssn VARCHAR(64),  -- Encrypted or hashed in production
    ssn_last4 VARCHAR(4),
    name_last VARCHAR(100),
    name_first VARCHAR(100),
    name_middle VARCHAR(50),
    name_display VARCHAR(200),
    dob DATE,
    age INTEGER,
    sex VARCHAR(1),
    gender VARCHAR(50),
    primary_station VARCHAR(10),
    primary_station_name VARCHAR(200),
    veteran_status VARCHAR(50),
    source_system VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_patient_icn ON patient_demographics(icn);
CREATE INDEX idx_patient_name_last ON patient_demographics(name_last);
CREATE INDEX idx_patient_name_first ON patient_demographics(name_first);
CREATE INDEX idx_patient_ssn_last4 ON patient_demographics(ssn_last4);
CREATE INDEX idx_patient_station ON patient_demographics(primary_station);
CREATE INDEX idx_patient_dob ON patient_demographics(dob);

-- Add comments for documentation
COMMENT ON TABLE patient_demographics IS 'Patient demographics from Gold layer - optimized for UI queries';
COMMENT ON COLUMN patient_demographics.patient_key IS 'Internal unique identifier (currently same as ICN)';
COMMENT ON COLUMN patient_demographics.icn IS 'Integrated Care Number - primary VA patient identifier';
COMMENT ON COLUMN patient_demographics.ssn_last4 IS 'Last 4 digits of SSN for display/verification';
COMMENT ON COLUMN patient_demographics.name_display IS 'Formatted name for UI display (LAST, First)';
COMMENT ON COLUMN patient_demographics.age IS 'Current age calculated from DOB';
```

**Design Notes:**
- Primary key is `patient_key` (currently = ICN, but allows for future flexibility)
- `icn` has UNIQUE constraint (one row per patient)
- Indexes on searchable fields (`name_last`, `name_first`, `ssn_last4`, `icn`)
- `ssn` column for future encrypted storage (not displayed in UI)
- Comments for developer documentation

---

## 11. ETL Implementation Patterns

### 11.1 Bronze Layer Pattern

**Purpose:** Extract raw data from source system with minimal transformation.

**Key Principles:**
- Preserve all source columns
- Add metadata columns: `SourceSystem`, `LoadDateTime`
- No business logic transformations
- No data cleaning
- Partition by date or facility if needed

**Standard Metadata Columns:**
```python
df = df.with_columns([
    pl.lit("CDWWork").alias("SourceSystem"),
    pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
])
```

### 11.2 Silver Layer Pattern

**Purpose:** Clean, standardize, and harmonize data.

**Key Transformations:**
- Handle NULLs and sentinel values (-1, "Unknown", etc.)
- Standardize field names (snake_case)
- Format dates (ISO 8601)
- Calculate derived fields (age from DOB)
- Clean string fields (trim, uppercase/lowercase)
- Standardize codes (sex: M/F/U, marital status, etc.)
- Merge CDWWork + CDWWork1 data (when ready)

**Standard Cleaning Patterns:**
```python
# Handle -1 sentinel values
pl.when(pl.col("FieldName") == -1).then(None).otherwise(pl.col("FieldName"))

# Trim whitespace
pl.col("FieldName").str.strip()

# Uppercase/Lowercase
pl.col("FieldName").str.to_uppercase()
pl.col("FieldName").str.to_lowercase()

# Date formatting
pl.col("DateField").cast(pl.Date)
```

### 11.3 Gold Layer Pattern

**Purpose:** Create query-optimized, business-friendly views.

**Key Characteristics:**
- Denormalized for query performance
- Include calculated fields
- Join dimension tables (facility names, lookup values)
- Filter to active/relevant data only
- Optimize column order for common queries
- Add business-friendly field names

**Standard Joins:**
```python
# Join facility names
df = df.join(
    df_facilities,
    left_on="Sta3n",
    right_on="Sta3n",
    how="left"
)
```

### 11.4 PostgreSQL Loading Pattern

**Purpose:** Efficiently load Gold Parquet into PostgreSQL.

**Loading Strategies:**

**Option A: Full Reload (Simple, for small tables)**
```python
df_pandas.to_sql(
    "table_name",
    engine,
    if_exists="replace",  # Truncate and reload
    index=False,
    method="multi",
)
```

**Option B: Upsert (For incremental updates)**
```python
# Use ON CONFLICT for upsert
# Requires custom SQL
```

**Option C: Delete + Insert (For date-partitioned data)**
```python
# Delete rows for date range
# Insert new rows
```

---

## 12. Timeline and Priorities

### 12.1 Week-by-Week Breakdown

**Week 1: Phase 1 - Data Pipeline Foundation**
- Days 1-2: PostgreSQL/MinIO setup, schema design
- Days 3-4: Bronze + Silver ETL for patient demographics
- Day 5: Gold ETL + PostgreSQL load, end-to-end testing

**Week 2: Phase 2 - Topbar UI (Part 1)**
- Days 1-2: Database query layer, patient routes, CCOW client
- Days 3-4: Topbar templates, modals, CSS/JavaScript
- Day 5: Integration testing, bug fixes

**Week 3: Phase 2 - Topbar UI (Part 2) + Phase 3 Start**
- Days 1-2: Final topbar polish, edge case handling
- Days 3-5: Patient Flags ETL pipeline

**Week 4: Phase 3 - Patient Flags UI**
- Days 1-3: Flags API endpoints, modal UI
- Days 4-5: Testing, polish, demo preparation

**Weeks 5+: Phase 4 - Additional Domains**
- Week 5-6: Medications domain (RxOut + BCMA)
- Week 7: Encounters domain (Inpat)
- Week 8+: Labs, Vitals, Orders, etc.

### 12.2 Milestone Demos

**Milestone 1 (End of Week 2):**
- ✅ Demo patient search with 37 real patients
- ✅ Demo CCOW integration
- ✅ Show end-to-end data flow diagram

**Milestone 2 (End of Week 4):**
- ✅ Demo patient flags
- ✅ Show two complete domains (demographics + flags)
- ✅ Demonstrate pattern repeatability

**Milestone 3 (End of Week 8):**
- ✅ Demo medications page
- ✅ Demo encounters timeline
- ✅ Show 4-5 clinical domains working

### 12.3 Risk Mitigation

**Risk: ETL takes longer than expected**
- Mitigation: Start with minimal Bronze (just required fields)
- Can add more fields incrementally

**Risk: PostgreSQL performance issues**
- Mitigation: Add indexes early, monitor query plans
- Can optimize later with materialized views

**Risk: UI complexity grows**
- Mitigation: Keep Phase 2 scope tight (just topbar)
- Defer additional UI pages until Phase 4

**Risk: CCOW integration issues**
- Mitigation: CCOW service already built and tested
- Can disable CCOW temporarily if needed (feature flag)

---

## 13. Success Criteria

### 13.1 Technical Success Criteria

**Data Pipeline:**
- [ ] Bronze → Silver → Gold → PostgreSQL runs end-to-end
- [ ] Pipeline completes in < 5 minutes for 37 patients
- [ ] All 37 patients have complete demographics
- [ ] No NULL values in required fields (name, DOB, sex)
- [ ] Age calculated correctly from DOB
- [ ] Facility names resolved correctly

**UI Functionality:**
- [ ] Patient search returns results in < 500ms
- [ ] CCOW integration works (get, set, refresh)
- [ ] Topbar displays correctly on desktop, tablet, mobile
- [ ] Modals open/close smoothly
- [ ] No JavaScript errors in console
- [ ] All HTMX triggers work correctly

**Data Quality:**
- [ ] All ICNs are unique
- [ ] All SSN last 4 digits are valid
- [ ] All ages are reasonable (0-120)
- [ ] All sex values are M/F/U
- [ ] All station codes are valid

### 13.2 Business Success Criteria

- [ ] Clinician can find a patient in < 10 seconds
- [ ] Patient demographics display is clear and readable
- [ ] System demonstrates "faster than JLV" (< 4 seconds vs ~20 seconds)
- [ ] Pattern is proven and documented for additional domains
- [ ] Stakeholders are confident in architecture

### 13.3 Learning Success Criteria

- [ ] Team understands medallion architecture
- [ ] Team can add new domains independently
- [ ] ETL patterns are documented and reusable
- [ ] PostgreSQL schema design is validated
- [ ] HTMX patterns are understood and repeatable

---

## 14. Related Documentation

### 14.1 Architecture and Planning

- **`med-z1-plan.md`** - High-level strategic plan and architecture overview
- **`ccow-vault-design.md`** - CCOW Context Vault technical specification
- **`patient-topbar-redesign-spec.md`** - Patient topbar UI detailed specification

### 14.2 Subsystem Documentation

- **`app/README.md`** - FastAPI application setup and usage
- **`etl/README.md`** - ETL subsystem documentation (to be created)
- **`ccow/README.md`** - CCOW service documentation
- **`mock/README.md`** - Mock CDW documentation

### 14.3 Schema Documentation

- **`db/ddl/`** - PostgreSQL DDL scripts
- **`docs/schemas/`** - Gold layer schema definitions (to be created)

### 14.4 Development Guides

- **`CLAUDE.md`** - Project-wide development guidance for Claude Code
- **`README.md`** - Project overview and quick start

---

## Document History

| Version | Date       | Author | Notes                                      |
|---------|------------|--------|--------------------------------------------|
| v1.0    | 2025-12-07 | Chuck  | Initial implementation roadmap             |

---

**End of Document**
