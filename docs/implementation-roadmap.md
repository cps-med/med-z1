# med-z1 Implementation Roadmap – Vertical Slice Strategy

December 7, 2025 • Document version v1.1
**Last Updated:** December 15, 2025

> **Related Documentation:**
> - **Strategic Vision & Product Planning:** See `med-z1-plan.md` for product vision, user personas, core use cases, and UX strategy
> - **Architecture Decisions & Patterns:** See `architecture.md` for ADRs (Architecture Decision Records) and design patterns

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

| Phase | Focus | Duration | Status |
|-------|-------|----------|--------|
| **Phase 1** | Minimal Viable Data Pipeline | 1-2 weeks | ✅ Complete |
| **Phase 2** | Topbar UI with Real Data | 1 week | ✅ Complete |
| **Phase 2.5** | Demographics Enhancement | 1 week | ✅ Complete (2025-12-11) |
| **Phase 3** | Patient Flags Domain | 1 week | ✅ Complete (2025-12-11) |
| **Phase 4** | Vitals Domain | 1 week | ✅ Complete (2025-12-12) |
| **Phase 5** | Allergies Domain | 1 week | ✅ Complete (2025-12-12) |
| **Phase 6** | Medications Domain (RxOut + BCMA) | 2 weeks | ✅ Complete (2025-12-13) |

**Functional Patient-Aware UI: ✅ Delivered**
**Clinical Domains Implemented: 6** (Demographics, Demographics Enhanced, Flags, Vitals, Allergies, Medications)

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
- ✅ Already have 36 patients in mock CDW
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
- Week 2-3: Build topbar UI with real patient search (36 patients)
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
- ✅ 36 patients loaded and queryable
- ✅ Python scripts to run the full pipeline end-to-end
- ✅ Proven pattern for Bronze → Silver → Gold → PostgreSQL

### 4.2 Data Scope

**Source Table:** `SPatient.SPatient` (in mock SQL Server CDWWork database)

**Patient Count:** 36 patients (from your existing insert script)

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
│   └─ SPatient.SPatient table (36 patients)                  │
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
│   └─ patient_demographics table (36 rows)                   │
│      - Indexed for fast searches (ICN, name, SSN)           │
│      - Ready for FastAPI queries                            │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Detailed Task Breakdown

#### Task 1.1: Set Up Prerequisites (0.5 day)

**PostgreSQL Setup:**

**Overview:**

PostgreSQL serves as the **serving database** for med-z1, providing low-latency access to curated Gold-layer data for the FastAPI/HTMX UI. Unlike SQL Server, PostgreSQL uses a different approach to database selection:

- **SQL Server approach:** Use `USE dbname;` to switch databases within a session
- **PostgreSQL approach:** Specify the database when connecting using the `-d` flag (no `USE` statement)

For this project:
- Default database: `postgres` (created automatically by PostgreSQL)
- Med-z1 database: `medz1` (we will create this)
- Password authentication: Set at Docker container creation via `POSTGRES_PASSWORD` environment variable
- The same password applies to all databases accessed by the `postgres` user

**Docker Setup:**

```bash
# Create PostgreSQL container with password
docker run -d \
    --name postgres16 \
    -e POSTGRES_PASSWORD=yourpassword \
    -p 5432:5432 \
    -v postgres16-data:/var/lib/postgresql/data \
    postgres:16

# Verify container is running
docker ps | grep postgres16
```

**Create the medz1 Database:**

```bash
# Connect to the default 'postgres' database
docker exec -it postgres16 psql -U postgres -d medz1

# In the psql prompt, create the medz1 database
CREATE DATABASE medz1;

# List all databases to verify creation
\l

# Exit psql
\q
```

**Connect to medz1 Database:**

```bash
# Connect directly to medz1 database (password will be prompted if configured)
docker exec -it postgres16 psql -U postgres -d medz1

# Alternative: Non-interactive connection (useful for scripts)
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT current_database();"
```

**Run SQL Scripts via Docker Exec:**

```bash
# Method 1: Pipe SQL file into docker exec (recommended)
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/patient_demographics.sql

# Method 2: Copy file into container, then execute
docker cp db/ddl/patient_demographics.sql postgres16:/tmp/
docker exec -it postgres16 psql -U postgres -d medz1 -f /tmp/patient_demographics.sql

# Method 3: Execute single-line SQL directly
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT * FROM patient_demographics LIMIT 5;"
```

**Useful Interactive psql Commands:**

Once connected via `docker exec -it postgres16 psql -U postgres -d medz1`, use these commands:

| Command | Description |
|---------|-------------|
| `\l` | List all databases |
| `\dt` | List all tables in current database |
| `\d table_name` | Describe table schema (columns, types, constraints) |
| `\d+ table_name` | Describe table with additional details (indexes, size) |
| `\di` | List all indexes |
| `\du` | List all users/roles |
| `\c dbname` | Connect to a different database |
| `\q` | Quit psql |
| `\timing` | Toggle query execution timing |
| `\x` | Toggle expanded display (useful for wide tables) |
| `\i filename.sql` | Execute SQL file (if file is inside container) |
| `\?` | Show all psql commands |
| `\h SQL_COMMAND` | Show help for SQL command (e.g., `\h CREATE TABLE`) |

**Verify PostgreSQL Setup:**

```bash
# Check medz1 database exists and is accessible
docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt"

# Verify patient_demographics table was created
docker exec -it postgres16 psql -U postgres -d medz1 -c "\d patient_demographics"

# Count rows (should be 0 initially)
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM patient_demographics;"
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
pip install boto3 polars pyarrow sqlalchemy pyodbc psycopg2-binary duckdb
```

**Note on Database Connectivity:**
- We use **SQLAlchemy + pyodbc** for SQL Server connectivity (most reliable)
- `connectorx` is available but may have Arrow compatibility issues with certain Polars versions
- For production, SQLAlchemy provides better connection pooling and error handling

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
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_patient_bronze():
    """Extract patient data from CDWWork to Bronze layer in MinIO."""

    logger.info("Starting Bronze patient extraction...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    logger.info(f"Created DB connection string")

    # Create SQLAlchemy engine
    engine = create_engine(conn_str)

    # Extract query
    query = """
    SELECT
        PatientSID,
        PatientIEN,
        Sta3n,
        PatientName,
        PatientLastName,
        PatientFirstName,
        TestPatientFlag,
        PatientType,
        PatientICN,
        ScrSSN,
        PatientSSN,
        SSNVerificationStatus,
        Age,
        BirthDateTime,
        DeceasedFlag,
        DeathDateTime,
        Gender,
        SelfIdentifiedGender,
        Religion,
        MaritalStatus,
        VeteranFlag,
        ServiceConnectedFlag
        -- Note: SourceSystemCode does not exist in the table
        -- It will be added as metadata in the ETL process
    FROM SPatient.SPatient
    WHERE TestPatientFlag = 'N' OR TestPatientFlag = 'Y'
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} patients from CDWWork")

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
        pl.col("PatientICN").alias("icn"),
        pl.col("PatientSSN").alias("ssn"),

        # Clean name fields
        pl.col("PatientLastName").str.strip_chars().alias("name_last"),
        pl.col("PatientFirstName").str.strip_chars().alias("name_first"),

        # Create display name
        (pl.col("PatientLastName").str.strip_chars() + ", " +
         pl.col("PatientFirstName").str.strip_chars()).alias("name_display"),

        # Handle dates
        pl.col("BirthDateTime").cast(pl.Date).alias("dob"),

        # Calculate age
        ((pl.lit(today).cast(pl.Date) - pl.col("BirthDateTime").cast(pl.Date)).dt.total_days() / 365.25)
            .cast(pl.Int32).alias("age"),

        # Standardize sex
        pl.col("Gender").str.strip_chars().alias("sex"),

        # Extract SSN last 4
        pl.col("PatientSSN").str.slice(-4).alias("ssn_last4"),

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
        "508": "Atlanta VA Medical Center",
        "516": "Bay Pines VA Healthcare System",
        "552": "Dayton VA Medical Center",
        "668": "Washington DC VA Medical Center",
    }

    df_patient = df_patient.with_columns([
        pl.col("primary_station").replace_strict(station_names, default="Unknown Facility")
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
    conn_str = f"mssql://{CDWWORK_DB_CONFIG['user']}:{CDWWORK_DB_CONFIG['password']}@{CDWWORK_DB_CONFIG['server']}/{CDWWORK_DB_CONFIG['name']}"

    # Extract query
    query = """
    SELECT
        PatientSID,
        PatientIEN,
        Sta3n,
        PatientName,
        PatientLastName,
        PatientFirstName,
        TestPatientFlag,
        PatientType,
        PatientICN,
        ScrSSN,
        PatientSSN,
        SSNVerificationStatus,
        Age,
        BirthDateTime,
        DeceasedFlag,
        DeathDateTime,
        Gender,
        SelfIdentifiedGender,
        Religion,
        ReligionSID,
        MaritalStatus,
        MaritalStatusSID,
        VeteranFlag,
        ServiceConnectedFlag
        -- Note: SourceSystemCode does not exist in the table
        -- It will be added as metadata in the ETL process
    FROM SPatient.SPatient
    WHERE TestPatientFlag = 'N'  -- Exclude test patients for production
       OR TestPatientFlag = 'Y'  -- But include for dev/testing
    """

    # Read data from database using URI
    df = pl.read_database_uri(query, conn_str)

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
# Should see: "Bronze extraction complete: 36 patients written to lake/bronze/patient/patient_raw.parquet"

# Verify Parquet file
python -c "import polars as pl; print(pl.read_parquet('lake/bronze/patient/patient_raw.parquet').head())"
```

**Deliverable:** Bronze Parquet file with 36 patients

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
        pl.col("PatientICN").alias("icn"),
        pl.col("PatientSSN").alias("ssn"),

        # Clean name fields
        pl.col("PatientLastName").str.strip_chars().alias("name_last"),
        pl.col("PatientFirstName").str.strip_chars().alias("name_first"),

        # Create display name
        (pl.col("PatientLastName").str.strip_chars() + ", " +
         pl.col("PatientFirstName").str.strip_chars()).alias("name_display"),

        # Handle dates
        pl.col("BirthDateTime").cast(pl.Date).alias("dob"),

        # Calculate age
        ((pl.lit(today).cast(pl.Date) - pl.col("BirthDateTime").cast(pl.Date)).dt.total_days() / 365.25)
            .cast(pl.Int32).alias("age"),

        # Standardize sex
        pl.col("Gender").str.strip_chars().alias("sex"),

        # Extract SSN last 4
        pl.col("PatientSSN").str.slice(-4).alias("ssn_last4"),

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
        "508": "Atlanta VA Medical Center",
        "516": "Bay Pines VA Healthcare System",
        "552": "Dayton VA Medical Center",
        "668": "Washington DC VA Medical Center",
    }

    # Add station names
    df_patient = df_patient.with_columns([
        pl.col("primary_station").replace_strict(station_names, default="Unknown Facility")
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
# Should show: 36

psql -h localhost -U postgres -d medz1 -c "SELECT icn, name_display, age, sex FROM patient_demographics LIMIT 5;"
```

**Deliverable:** PostgreSQL `patient_demographics` table populated with 36 patients

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
- [ ] PostgreSQL table `patient_demographics` has 36 rows
- [ ] Can query patients by ICN: `SELECT * FROM patient_demographics WHERE icn = '100001'`
- [ ] Can search by name: `SELECT * FROM patient_demographics WHERE name_last ILIKE 'DOOREE%'`
- [ ] All 36 patients have valid age, sex, ssn_last4
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
- ✅ All 36 patients searchable by name, SSN, ICN
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

- [ ] Can search all 36 patients by name
- [ ] Can search by SSN last 4
- [ ] Can search by ICN
- [ ] Patient demographics display correctly in topbar
- [ ] CCOW integration works end-to-end
- [ ] Modal opens and closes smoothly
- [ ] "View Patient Flags" button disabled when no patient
- [ ] Responsive design works on mobile/tablet
- [ ] No console errors in browser

---

## 6. Phase 2.5: Demographics Enhancement ✅ Complete (2025-12-11)

**Duration:** 1 week

**Goal:** Enhance Demographics widget with address, phone, and insurance information.

### 6.1 Completed Work

✅ Created `Dim.InsuranceCompany` table in CDWWork
✅ Added mock data for 17 insurance companies
✅ Updated ETL pipeline to include patient addresses and insurance
✅ Enhanced PostgreSQL `patient_demographics` table
✅ Updated Demographics widget to display contact and insurance sections

**Reference:** `docs/demographics-enhancement-design.md`

---

## 7. Phase 3: Patient Flags Domain ✅ Complete (2025-12-11)

**Duration:** 1 week (5 days actual)

**Goal:** Add Patient Flags as the second clinical domain, proving the pattern scales.

### 7.1 Why Patient Flags?

- ✅ Completes the topbar UI ("View Patient Flags" button)
- ✅ Critical safety alerts for clinical staff
- ✅ Demonstrates domain pattern repeatability
- ✅ Relatively complex (3 tables: Dim, Assignment, History)

### 7.2 Completed Tasks

✅ Created 3 tables in Mock CDW (Dim.PatientRecordFlag, SPatient.PatientRecordFlagAssignment, SPatient.PatientRecordFlagHistory)
✅ Built complete ETL pipeline (Bronze/Silver/Gold)
✅ Created PostgreSQL serving tables (patient_flags, patient_flag_history)
✅ Implemented 3 API endpoints with JSON and HTML responses
✅ Built flags modal UI with National/Local separation
✅ Implemented lazy-loaded flag history with sensitive data
✅ Added flag count badge with color coding (overdue = red)

### 7.3 Success Criteria Achieved

✅ Flags data flows from Mock CDW → Bronze → Silver → Gold → PostgreSQL
✅ "View Patient Flags" button shows badge with count
✅ Clicking button opens modal with formatted flags
✅ Flags display categories, dates, review status, and narratives
✅ Modal handles patients with 0 flags gracefully
✅ Review status calculation (CURRENT, DUE SOON, OVERDUE)

**Reference:** `docs/patient-flags-design.md` (v1.2)

### 7.4 UI Implementation Decision (2025-12-14)

**Decision:** Patient Flags will use **modal-only UI pattern** (no dashboard widget, no dedicated page)

**Rationale:**
- Flags are critical safety alerts best accessed on-demand via persistent topbar button
- Modal provides sufficient functionality for viewing flags and history
- Reduces dashboard clutter - flags don't need continuous visibility like vitals or allergies
- Topbar "View Flags" button with badge count provides always-visible access

**Changes Made:**
- ❌ Removed Patient Flags widget from dashboard (previously in row 1, position 3)
- ❌ Removed Patient Flags link from sidebar
- ✅ Retained topbar "View Flags" button with badge count
- ✅ Retained flags modal with full flag details and history

**Impact:** Dashboard row 1, position 3 now available for Encounters widget

---

## 8. Phase 4: Vitals Domain ✅ Complete (2025-12-12)

**Duration:** 8 days

**Goal:** Add Vitals as a full clinical domain with widget, full page, and charting.

### 8.1 Completed Work

✅ Created `Vital.VitalSign` table in CDWWork with 9 vital types
✅ Generated 2,100+ mock vital measurements across 37 patients
✅ Built complete ETL pipeline (Bronze/Silver/Gold)
✅ Created PostgreSQL serving table with 2,100+ records
✅ Implemented Vitals widget on dashboard (most recent readings)
✅ Built full Vitals page with comprehensive vital history
✅ Added interactive Chart.js visualizations (BP, Temp, HR, RR, SpO2, BMI)
✅ Implemented date range filtering (7 days, 30 days, 90 days, 1 year, all)
✅ Added vital details modal with trend analysis

### 8.2 Success Criteria Achieved

✅ Vitals widget displays 6 most recent vital signs
✅ "View Full History" link navigates to dedicated vitals page
✅ Full page shows complete vital history with filtering
✅ Chart.js visualizations render correctly with responsive design
✅ Date range filtering updates both table and charts
✅ Modal shows individual vital details with trend indicators
✅ Performance < 500ms for typical patient

**Reference:** `docs/vitals-design.md`

---

## 9. Phase 5: Allergies Domain ✅ Complete (2025-12-12)

**Duration:** 9 days (includes comprehensive testing)

**Goal:** Add Allergies as a critical safety domain with widget and full page.

### 9.1 Completed Work

✅ Created `SPatient.PatientAllergy` table in CDWWork
✅ Created `Dim.AllergyReactant` dimension table with 50+ allergens
✅ Created `Dim.AllergyReaction` dimension table with 30+ reactions
✅ Generated 117 mock allergy records across 31 patients
✅ Built complete ETL pipeline (Bronze/Silver/Gold)
✅ Created PostgreSQL serving table with allergy data
✅ Implemented Allergies widget on dashboard
✅ Built full Allergies page with comprehensive allergy listing
✅ Added severity-based color coding (SEVERE = red, MODERATE = orange, MILD = yellow)
✅ Implemented "No Known Allergies" handling
✅ Added allergy details modal

### 9.2 Success Criteria Achieved

✅ Allergies widget displays active allergies with severity indicators
✅ "View All Allergies" link navigates to dedicated allergies page
✅ Full page shows complete allergy history grouped by severity
✅ Severity color coding consistent across widget and full page
✅ Modal shows detailed allergy information (reactions, onset, notes)
✅ "No Known Allergies" displays correctly for patients without allergies
✅ Performance < 500ms for typical patient

**Reference:** `docs/allergies-design.md`

---

## 10. Phase 6: Medications Domain (RxOut + BCMA) - ✅ Complete

**Duration:** 1 day (accelerated implementation)
**Completion Date:** 2025-12-13
**Status:** ✅ Complete - Full vertical slice delivered

**Goal:** Implement comprehensive medications domain integrating outpatient prescriptions (RxOut) and inpatient medication administrations (BCMA).

### 10.1 Implementation Progress

**✅ Completed Work (Days 1-4):**

**Day 1: Database Setup and Dimension Tables** (2025-12-13)
- Created 2 drug dimension tables in mock CDW:
  - `Dim.LocalDrug` (58 drugs)
  - `Dim.NationalDrug` (40 drugs)
- Populated with DEA-scheduled controlled substances and common medications

**Day 2: Bronze ETL** (2025-12-13)
- Created `etl/bronze_medications.py`
- Extracted 5 tables to Bronze Parquet:
  - `Dim.LocalDrug` (58 rows)
  - `Dim.NationalDrug` (40 rows)
  - `RxOut.RxOutpat` (111 prescriptions)
  - `RxOut.RxOutpatFill` (31 fills)
  - `BCMA.BCMAMedicationLog` (52 administration events)

**Day 3: Silver ETL** (2025-12-13)
- Created `etl/silver_medications.py`
- Harmonized data with drug lookups (LocalDrug → NationalDrug)
- Resolved provider and facility names
- Fixed stale NationalDrugSID issue (used dimension table mapping instead of fact table values)
- Generated 2 Silver files:
  - `medications_rxout_cleaned.parquet` (111 rows)
  - `medications_bcma_cleaned.parquet` (52 rows)

**Day 4: Gold ETL and PostgreSQL Load** (2025-12-13)
- Created `etl/gold_patient_medications.py`
- Implemented patient ICN resolution (`ICN{100000 + patient_sid}`)
- Calculated computed flags (is_active, is_controlled_substance, administration_variance, is_iv_medication)
- Generated 2 Gold files:
  - `medications_rxout_final.parquet` (111 rows)
  - `medications_bcma_final.parquet` (52 rows)
- Created `db/ddl/create_patient_medications_tables.sql`
- Created `etl/load_medications.py`
- Loaded 163 total records to PostgreSQL:
  - `patient_medications_outpatient` (111 rows, 23 unique patients, 14 controlled substances)
  - `patient_medications_inpatient` (52 rows, 20 unique patients, 7 controlled substances)
- Created 17 indexes (11 on outpatient, 6 on inpatient)

**Day 5: API Endpoints (Part 1)** (2025-12-13) ✅
- Created `app/db/medications.py` with database query functions
- Created `app/routes/medications.py` with API endpoints
- Implemented endpoints:
  - `GET /api/patient/{icn}/medications` (with filters)
  - `GET /api/patient/{icn}/medications/recent`
  - `GET /api/patient/{icn}/medications/{medication_id}/details`
  - `GET /api/dashboard/widget/medications/{icn}` (HTML)
  - `GET /patient/{icn}/medications` (full page route)
- Registered routers in `app/main.py`
- Tested all endpoints successfully

**Day 6: Widget Template and HTML Rendering** (2025-12-13) ✅
- Created `app/templates/partials/medications_widget.html`
- Added CSS styles for two-column widget layout to `app/static/styles.css`
- Fixed `get_recent_medications()` to remove 90-day date filter
- Tested widget endpoint with multiple patients (ICN100001, ICN100002, ICN100015)
- Verified HTMX-compatible HTML rendering
- Controlled substance badges and status badges working correctly

**Day 7: Dashboard Widget Integration** (2025-12-13) ✅
- Updated `app/templates/dashboard.html` to replace medications placeholder with HTMX widget
- Widget configured as `widget--2x1` (spans 2 columns in dashboard grid)
- HTMX attributes: `hx-get="/api/patient/dashboard/widget/medications/{icn}"`, `hx-trigger="load"`
- Widget loads automatically on dashboard page load
- Verified two-column layout (Outpatient left, Inpatient right)
- Responsive grid layout working (desktop: 3 cols, tablet: 2 cols, mobile: 1 col)
- "View All Medications" link routes to `/patient/{icn}/medications`

**Day 8: Full Medications Page (Part 1)** (2025-12-13) ✅
- Created `app/templates/patient_medications.html` with full page layout
- Added 250+ lines of CSS for medications page styling
- Summary stats bar: Total, Outpatient, Inpatient, Active, Controlled
- Filter controls: Time Period (30d/90d/6mo/1yr/all), Type (all/outpatient/inpatient), Status (active/expired/discontinued), Sort
- Chronological table with columns: Date, Medication, Type, Status/Details, Provider
- Controlled substance highlighting (yellow background on rows)
- Responsive design with mobile scrolling
- Tested filters and sorting successfully

**Additional Polish Items (Optional - Deferred):**
- Day 9: Expandable row details for full medication info (deferred)
- Day 10: Additional testing and visual polish (deferred)

**Success Criteria - All Achieved ✅:**
- ✅ Drug dimension tables created (58 local, 40 national)
- ✅ Bronze ETL complete (5 Parquet files)
- ✅ Silver ETL complete (drug lookups resolved)
- ✅ Gold ETL complete (patient-centric views)
- ✅ PostgreSQL tables loaded (163 records)
- ✅ API endpoints complete (4 endpoints tested and working)
- ✅ Dashboard widget (2x1 two-column layout, HTMX-loaded)
- ✅ Full medications page (chronological table with filtering)

**Design Document:** See `docs/medications-design.md` (v1.1) for complete implementation specification.

### 10.2 Completion Summary

**Final Deliverables:**
1. ✅ **Complete ETL Pipeline**: Bronze → Silver → Gold → PostgreSQL (163 medication records)
2. ✅ **API Endpoints**: 4 endpoints with filtering, sorting, and details
3. ✅ **Dashboard Widget**: 2x1 two-column widget (Outpatient/Inpatient) with HTMX loading
4. ✅ **Full Medications Page**: Chronological table with comprehensive filtering and sorting
5. ✅ **Sidebar Integration**: Active medications link in navigation

**UI Polish Applied:**
- Fixed sidebar link: Changed from disabled to active
- Fixed page responsiveness: Updated `.page-container` to use full width and respond to sidebar collapse/expand
- Consistent layout: All pages (Dashboard, Vitals, Allergies, Medications) now use same responsive pattern

**User Acceptance:**
- User tested widget and full page
- User confirmed medications implementation is complete and operational
- All feedback addressed and applied

**Phase 6 Complete:** 2025-12-13 (1 day implementation - Days 1-8 accelerated)

---

## 11. Phase 7a: Demographics Full Page Implementation - ✅ Complete

**Duration:** 4 days (actual)
**Start Date:** 2025-12-14
**Completion Date:** 2025-12-14
**Status:** ✅ Complete - All Days (1-4) Implemented

**Goal:** Add full demographics page with Phase 2 fields (marital status, religion, service connected %, deceased status) to complement the existing demographics widget.

### 11.1 Implementation Progress

**✅ Day 1 Complete (2025-12-14): Database Schema & Bronze ETL**
- ✅ Created `etl/bronze_patient_disability.py` for SPatientDisability extraction
- ✅ Extracted 10 disability records to Bronze Parquet
- ✅ Updated `db/ddl/patient_demographics.sql` to v3.0 with 5 new columns:
  - `marital_status` VARCHAR(25)
  - `religion` VARCHAR(50)
  - `service_connected_percent` DECIMAL(5,2)
  - `deceased_flag` CHAR(1)
  - `death_date` DATE
- ✅ Executed DDL in PostgreSQL (36 patients, 27 columns total)
- ✅ Verified Bronze Parquet row count matches source table (10 records)
- ✅ Verified PostgreSQL schema has all new columns with correct data types

**✅ Day 2 Complete (2025-12-14): Silver & Gold ETL Updates**
- ✅ Updated `etl/silver_patient.py` to v3.0:
  - Read Bronze patient_disability data
  - Joined disability data to get service_connected_percent
  - Extracted marital_status, religion, deceased_flag, death_date from existing patient Bronze
  - Added 5 Phase 2 fields to Silver schema (23 columns total)
- ✅ Updated `etl/gold_patient.py` to v3.0:
  - Included 5 Phase 2 fields in Gold schema (27 columns total)
- ✅ Ran Silver ETL successfully (36 patients, 10 service connected records joined)
- ✅ Ran Gold ETL successfully (36 patients with all Phase 2 fields)
- ✅ Verified all Phase 2 fields present with valid data in Parquet files

**✅ Day 3 Complete (2025-12-14): PostgreSQL Load & API Endpoints**
- ✅ Loaded updated Gold data to PostgreSQL (36 patients with 27 columns)
- ✅ Verified Phase 2 fields in PostgreSQL with sample data:
  - marital_status: DIVORCED, MARRIED, WIDOWED, SEPARATED
  - religion: Christian, Muslim, Morman, Jewish
  - service_connected_percent: 51%
  - deceased_flag: N (for living patients)
- ✅ Updated `app/db/patient.py::get_patient_demographics()`:
  - Added 5 Phase 2 fields to SQL SELECT
  - Added 5 Phase 2 fields to return dictionary
  - Tested successfully (returns all 25 fields)
- ✅ Created `app/routes/demographics.py` with Pattern B router:
  - Implemented `GET /patient/{icn}/demographics` page route
  - Implemented `GET /demographics` redirect route (placeholder)
  - Added error handling and logging
- ✅ Registered demographics router in `app/main.py`
- ✅ Tested database query function (returns all Phase 2 fields correctly)

**✅ Day 4 Complete (2025-12-14): Full Page Template & Styling**
- ✅ Created `app/templates/patient_demographics.html` with 4-section layout:
  - Personal Information (name, ICN, DOB, age, sex, marital status, religion, facility)
  - Contact Information (phone, address)
  - Insurance Information (primary insurance)
  - Military Service & Eligibility (service connected %)
- ✅ Added CSS to `app/static/styles.css` (~90 lines):
  - Demographics page styles (.demo-section-card, .demo-grid, .demo-field)
  - Deceased badge styles (.deceased-badge)
  - Responsive grid (2-col desktop → 1-col mobile)
- ✅ Updated demographics widget:
  - Added "View Full Demographics" link using widget-action pattern
  - Added minimal footer (0.25rem padding) for visual spacing
  - Updated all widgets with standard minimal footer component
- ✅ Tested full page with deceased patient (ICN1011530429) - Badge displays correctly
- ✅ Tested with patients with/without service_connected_percent - "Not Available" displays correctly
- ✅ Verified responsive design on all breakpoints

**Widget Footer Design Decision (2025-12-14):**
- Implemented minimal footer as standard component across all widgets
- Footer padding: 0.25rem (62.5% reduction from original 0.75rem)
- Total footer height: ~9px (vs original ~24px)
- Provides subtle breathing room at bottom of widgets without feeling cramped
- Applied to: Vitals, Allergies, Medications, Demographics widgets
- See `docs/patient-dashboard-design.md` for detailed rationale

### 11.2 Success Criteria

**All Criteria Met:**
- ✅ Complete ETL pipeline (Bronze → Silver → Gold → PostgreSQL) with Phase 2 fields
- ✅ All Phase 2 data in PostgreSQL (36 patients with 27 columns)
- ✅ Database query function returns all 25 fields
- ✅ Demographics router registered and accessible (Pattern B)
- ✅ API endpoint implemented (`GET /patient/{icn}/demographics`)
- ✅ Full demographics page displays all 4 sections correctly
- ✅ Deceased badge appears for deceased patients only
- ✅ "Not Available" displays for missing optional fields
- ✅ Widget → full page navigation works
- ✅ Responsive design works on all screen sizes
- ✅ Minimal footer provides visual breathing room

**Design Document:** See `docs/demographics-design.md` (v2.2) for complete implementation specification.

**Phase 7a Status:** ✅ Complete - Widget and Full Page Implemented

---

### 11.3 Future Domains (After Demographics Full Page Complete)

**Phase 7: Core Clinical Domains (Priority Order)**
1. ✅ **Medications (RxOut + BCMA)** - Complete (2025-12-13)
2. 🚧 **Encounters (Inpat/Outpat)** - **Next Priority** - Foundation for timeline views
   - **Scope:** Inpatient admissions, outpatient visits, ED encounters
   - **Widget:** 1x1 - Recent encounters (last 3-6 months)
   - **Full Page:** Chronological encounter history with diagnoses, providers, facilities
   - **Rationale:** Foundational domain for understanding patient care timeline
   - **UI Status:** Placeholder added to sidebar (after Vitals) and dashboard (row 1, position 3) - 2025-12-14
3. ✅ **Labs (LabChem)** - Table view complete, charting deferred
   - **Widget:** **3x1 (full width)** - Recent lab panels side-by-side with trend placeholders
   - **Full Page:** Complete lab history with filtering, sorting, abnormal value highlighting
   - **Implementation Status (2025-12-16):**
     - ✅ Widget: 3x1 hybrid layout (lab panels + trending section with placeholder indicators)
     - ✅ Full Page: Table view with filtering, sorting, panel grouping
     - ✅ Data Infrastructure: Trending data queries and 90-day history working
     - ✅ Sidebar link activated and functional
     - ⏸️ Charting: Chart.js sparklines deferred due to HTMX timing issues (see lab-results-design.md v1.1)
     - Future: Implement charting on full page (non-HTMX) or via HTMX event listeners
4. 🚧 **Problems/Diagnoses** - Clinical context and problem list
   - **Widget:** 1x1 or 2x1 - Active problems
   - **Full Page:** Problem list with onset dates, status, providers
5. 🚧 **Orders** - Complex workflow domain
   - **Widget:** 1x1 or 3x1 (TBD) - Recent orders timeline
   - **Full Page:** Order history with status tracking
6. 🚧 **Notes/Documents** - Text-heavy domain
   - **Widget:** 1x1 - Recent note titles/dates
   - **Full Page:** Searchable note repository with preview/full view

**Phase 8: Later Domains**
7. 🚧 **Radiology/Imaging** - Integration with external viewers
   - **Widget:** 1x1 - Recent imaging studies
   - **Full Page:** Imaging history with thumbnail previews, report links
8. 🚧 **Immunizations** - Patient safety and preventive care
   - **Widget:** 1x1 - Recent immunizations and due vaccines
   - **Full Page:** Complete immunization record with lot numbers, sites
   - **UI Status:** Placeholder added to sidebar and dashboard (row 5, position 1) - 2025-12-14
9. 🚧 **Procedures** - Surgical and procedural history
   - **Widget:** 1x1 - Recent procedures
   - **Full Page:** Procedure history with CPT codes, providers, outcomes
   - **UI Status:** Placeholder added to sidebar and dashboard (row 5, position 2) - 2025-12-14

### 10.3 Proven Pattern for Each Domain

For each new domain, follow the established pattern:

1. **ETL Pipeline:**
   - Bronze extraction (may need multiple source tables)
   - Silver transformation (harmonize if from CDWWork1)
   - Gold view (query-optimized)
   - PostgreSQL table(s)

2. **API Endpoints:**
   - `GET /api/patient/{icn}/{domain}` - Get data for patient
   - Additional endpoints as needed (filters, date ranges, details modal)

3. **UI Components:**
   - Dashboard widget (summary view)
   - Full page (comprehensive view)
   - Details modal (individual record details)
   - Charts/visualizations where applicable

4. **Testing:**
   - ETL pipeline validation
   - API endpoint testing
   - UI functionality and responsiveness
   - Performance benchmarking

---

## 11. Phase 7: AI/ML and Advanced Features (Future)

**Duration:** Ongoing (3-6 weeks for initial features)

**Goal:** Add AI-assisted features using Gold Parquet data.

### 11.1 AI/ML Use Cases

**Phase 7A: Chart Overview Summarization**
- Read Gold Parquet for patient (encounters, meds, problems, labs, vitals, allergies)
- Generate natural language summary
- Display in Patient Overview page

**Phase 7B: Drug-Drug Interaction Detection**
- Read Gold medications Parquet
- Query DDI knowledge base
- Highlight risky combinations
- Cross-reference with patient allergies

**Phase 7C: Patient Flag-Aware Summaries**
- Incorporate flags into AI narrative
- Generate risk-aware care recommendations
- Consider allergies, vitals trends, and active conditions

**Phase 7D: Vital Sign Trend Analysis**
- AI-powered anomaly detection in vital trends
- Predictive warnings for deteriorating conditions
- Integration with flags system for high-risk patients

### 11.2 Architecture

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
- Use DuckDB for fast analytical queries across domains
- Cache AI responses to reduce API costs
- Always label AI-generated content
- Leverage existing domains (Vitals, Allergies, Flags) for richer context

---

## 11.3 Phase 8: Vista RPC Broker Simulator (Real-Time Data Layer)

**Status:** 🚧 In Development - Phase 3 MVP Complete (2025-12-17)
**Duration:** 5-6 weeks (Phases 1-6 as defined in vista-rpc-broker-design.md)
**Priority:** Medium - Addresses T-0 (today) data latency gap
**Current Progress:** ✅ 50% complete (Phase 1-3 complete: Walking Skeleton, Multi-Site Support, Vitals MVP)

### Overview

**Purpose:** Simulate VA VistA Remote Procedure Call (RPC) interface to enable real-time data (T-0, today) queries alongside historical PostgreSQL data (T-1 and earlier). This addresses the architectural limitation where CDW is always at least T-1 (nightly batch updates) and provides fresher data for clinical decision-making.

**Design Document:** `docs/vista-rpc-broker-design.md` (v1.2)

### Key Architecture Decisions

**Dual-Source Data Pattern:**
- **PostgreSQL (T-1 and earlier):** Fast, cached, historical data via ETL pipeline
- **Vista RPC Broker (T-0, today):** Real-time queries with 1-3 second latency per site
- **User-Controlled Refresh:** "Refresh from VistA" button (no automatic fetching)

**Critical Performance Controls:**
- **Site Selection Policy:** Default to top 3 most recent treating facilities (Section 2.8)
- **Per-Domain Limits:** Vitals (2 sites), Allergies (5), Medications (3), Demographics (1)
- **Hard Maximum:** 10 sites per query, requires explicit user action to exceed default
- **Time Budget:** 15 seconds max, show partial results if incomplete

**ICN ↔ DFN Resolution:**
- Med-z1 routes use ICN (Integrated Care Number)
- Vista handlers receive DFN (local VistA site identifier)
- Automatic translation at HTTP boundary (Section 2.7)

**Merge/Deduplication Rules:**
- Canonical event keys per domain (datetime + type + sta3n + id)
- Priority: Vista data preferred for T-1 and T-0, PostgreSQL for older data
- Deterministic deduplication across multiple site responses (Section 2.9.1)

### Implementation Phases

| Phase | Focus | Duration | Status | Key Deliverables |
|-------|-------|----------|--------|------------------|
| **Phase 1** | Walking Skeleton | 1 week | ✅ Complete (Days 1-5/5) | ✅ Patient registry with real data<br>✅ DataLoader (ICN→DFN resolution)<br>✅ RPCHandler base class<br>✅ RPCRegistry infrastructure<br>✅ First RPC handler (ORWPT PTINQ)<br>✅ M-Serializer<br>✅ FastAPI integration<br>✅ 94 tests, 100% passing<br>✅ Comprehensive README.md |
| **Phase 2** | Multi-Site Support | 1 week | ✅ Complete (Days 6-7/7) | ✅ VistaClient with site selection<br>✅ 3 sites (200, 500, 630)<br>✅ Domain-specific site limits<br>✅ T-notation date parsing<br>✅ Multi-site RPC calls<br>✅ 42 unit tests + manual guide<br>✅ 136 total tests (100% passing) |
| **Phase 3** | Vitals MVP | 3 days | ✅ Complete (2025-12-17) | ✅ GMV LATEST VM RPC handler<br>✅ Merge/dedupe logic (318 lines)<br>✅ UI "Refresh from VistA" button<br>✅ Green site badges<br>✅ T-notation date system<br>✅ End-to-end integration<br>✅ 305 PG + 10 Vista = 315 vitals |
| **Phase 4** | Additional Vitals RPCs | 1 week | ⏳ Not Started | GMV EXTRACT REC, GMV MANAGER, date-range queries |
| **Phase 5** | Allergies & Medications | 1 week | ⏳ Not Started | 8 RPCs across 2 domains, additional merge/dedupe |
| **Phase 6** | Polish & Documentation | 1 week | ⏳ Not Started | Error handling, performance tuning, docs |

### Dependencies

**Prerequisites:**
- ✅ Core domains implemented (Demographics, Vitals, Allergies, Medications) - Complete
- ✅ PostgreSQL serving database operational - Complete
- ✅ Patient registry with ICN/DFN mappings (`mock/shared/patient_registry.json`) - Complete (2025-12-15)
- 🚧 Realtime Overlay Service (can be Phase 6-7 enhancement) - Future

**Phase 1 Progress** (Completed 2025-12-15):
- ✅ **Day 1:** Project structure + patient registry with 3 real test patients
  - `vista/` directory structure created
  - `mock/shared/patient_registry.json` populated with actual PostgreSQL data
  - ICN100001 (316 records), ICN100010 (305 records), ICN100013 (312 records)
- ✅ **Day 2:** DataLoader service implementation
  - ICN→DFN resolution working for all 3 sites (200, 500, 630)
  - 13 unit tests, 100% passing
- ✅ **Day 3:** RPC handler infrastructure
  - RPCHandler abstract base class
  - RPCRegistry with dispatch mechanism
  - 19 unit tests, 100% passing
- ✅ **Day 4:** M-Serializer and first RPC handler
  - VistA format conversion utilities (caret-delimited, FileMan dates)
  - PatientInquiryHandler (ORWPT PTINQ) implementation
  - 50 unit tests (34 M-Serializer + 16 handler), 100% passing
- ✅ **Day 5:** FastAPI HTTP service and integration testing
  - Complete HTTP API on port 8003 (`vista/app/main.py`)
  - Multi-site support (3 sites: 200, 500, 630)
  - Integration tests via curl (patient found, site switching, error conditions)
  - Comprehensive documentation (`vista/README.md` - 580 lines)

**Phase 2 Progress** (Completed 2025-12-17):
- ✅ **Day 6:** VistaClient implementation
  - `app/services/vista_client.py` (310 lines) - HTTP client for Vista service
  - Intelligent site selection with domain-specific limits
  - T-notation date parsing (T-0, T-7, T-30)
  - Multi-site parallel RPC calls
  - 42 comprehensive unit tests
- ✅ **Day 7:** Testing and documentation
  - `app/services/test_vista_manual.py` - 7 end-to-end scenarios
  - `vista/MANUAL_TESTING.md` - Comprehensive testing guide
  - All edge cases validated (negative limits, invalid domains, etc.)
  - 136 total tests across both subsystems (100% passing)

**Phase 3 MVP Progress** (Completed 2025-12-17):
- ✅ **Step 1:** Vitals RPC Handler (1-2 hours actual)
  - `vista/app/handlers/vitals.py` (146 lines) - GMV LATEST VM implementation
  - Test data for 3 sites with T-notation dates
  - Unit tests for vitals handler
  - Curl testing verified
- ✅ **Step 2:** Merge/Deduplication Logic (2-3 hours actual)
  - `app/services/realtime_overlay.py` (318 lines)
  - FileMan datetime parsing
  - Vista vitals parsing (caret-delimited format)
  - Canonical key deduplication (type|datetime|location)
  - Vista preferred for T-1+ conflicts
  - Comprehensive unit tests
- ✅ **Step 3:** UI Integration (2-3 hours actual)
  - `GET /patient/{icn}/vitals-realtime` endpoint
  - "Refresh from VistA" button with HTMX
  - Green site badges: "⚡ Site 200", "⚡ Site 500"
  - Loading spinner and freshness indicator
  - End-to-end testing: 305 PG + 10 Vista = 315 vitals
  - Badge CSS fix (`badge--success` class added)
- ✅ **Bonus:** T-Notation Date System
  - Automatic date conversion in DataLoader
  - No daily manual updates required
  - Test data always appears fresh

**Subsystem Location:**
```
vista/
  app/
    main.py                    # FastAPI service (port 8003)
    services/
      vista_server.py          # Per-site RPC handler
      cluster.py               # Multi-site management
      data_loader.py           # JSON data loading + ICN→DFN resolution
      dispatcher.py            # RPC routing
    handlers/
      demographics.py          # ORWPT* RPCs
      vitals.py                # GMV* RPCs
      allergies.py             # ORQQAL* RPCs
      medications.py           # ORWPS*, PSO* RPCs
    utils/
      m_serializer.py          # VistA format conversion
      temporal.py              # T-0/T-1 date parsing
  data/
    sites/
      200/, 500/, 630/         # Per-site JSON data files
  config/
    sites.json                 # Site registry
```

### Realtime Overlay Service (Phase 6-7 Enhancement)

**Purpose:** Centralize real-time data orchestration to keep routes thin and maintainable.

**Rationale:** After 2-3 domains establish the pattern, refactor common logic into:
- `app/services/realtime_overlay.py`
- Enforces site selection policy consistently
- Applies merge/dedupe rules uniformly
- Handles partial failures gracefully
- Prevents code duplication across domain routes

**API:**
```python
class RealtimeOverlayService:
    async def get_domain_with_overlay(
        icn: str, domain: str, include_realtime: bool = True
    ) -> DomainOverlayResult
```

**Timeline:** Implement after Vista Phase 6 completes, then refactor existing "Refresh from VistA" endpoints.

### Success Metrics

- ✅ 90th percentile "Refresh from VistA" response time: <10 seconds
- ✅ No domain queries >10 sites by default
- ✅ Partial failures show clear completeness indicators
- ✅ No duplicate data in merged PostgreSQL + Vista results
- ✅ Med-z1 UI can fetch T-0 data on-demand for 4 domains (Demographics, Vitals, Allergies, Medications)

### Open Questions

1. **When to implement?** After core domains (Encounters, Labs, Problems) or sooner?
   - **Recommendation:** After Encounters + Labs are complete (establishes broader domain coverage baseline)
2. **Which domains get real-time support first?** All 4 Phase 1 domains or subset?
   - **Recommendation:** Start with Vitals + Medications (highest clinical value for T-0 data)

---

## 9. Gold Schema Design

### 9.1 Patient Demographics Gold Schema

**File:** `lake/gold/patient_demographics/patient_demographics.parquet`

**Schema:**

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `patient_key` | string | Internal key (ICN) | Derived |
| `icn` | string | Integrated Care Number | `SPatient.SPatient.PatientICN` |
| `ssn` | string | Full SSN (encrypted in prod) | `SPatient.SPatient.PatientSSN` |
| `ssn_last4` | string | Last 4 digits for display | Derived from PatientSSN |
| `name_last` | string | Last name | `SPatient.SPatient.PatientLastName` |
| `name_first` | string | First name | `SPatient.SPatient.PatientFirstName` |
| `name_display` | string | Formatted name ("LAST, First") | Derived |
| `dob` | date | Date of birth | `SPatient.SPatient.BirthDateTime` |
| `age` | integer | Current age | Calculated from BirthDateTime |
| `sex` | string | Biological sex (M/F/U) | `SPatient.SPatient.Gender` |
| `gender` | string | Gender identity | `SPatient.SPatient.SelfIdentifiedGender` |
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

### 12.1 Actual Implementation Timeline

**Weeks 1-2: Phase 1 & 2 - Foundation ✅ Complete**
- Week 1: PostgreSQL/MinIO setup, Bronze/Silver/Gold ETL for patient demographics
- Week 2: Topbar UI with patient search, CCOW integration, database query layer

**Week 3: Phase 2.5 - Demographics Enhancement ✅ Complete (2025-12-11)**
- Added address, phone, and insurance information to Demographics widget
- Enhanced ETL pipeline with additional source tables
- Updated PostgreSQL schema and widget templates

**Week 4: Phase 3 - Patient Flags ✅ Complete (2025-12-11)**
- Days 1-2: Mock CDW tables, Bronze/Silver/Gold ETL pipeline
- Days 3-4: API endpoints, database queries, flag history
- Day 5: Flags modal UI with badge, lazy-loaded history

**Week 5: Phase 4 - Vitals ✅ Complete (2025-12-12)**
- Days 1-4: Mock CDW tables, ETL pipeline, PostgreSQL load
- Days 5-8: Vitals widget, full page, Chart.js visualizations, filtering

**Week 6: Phase 5 - Allergies ✅ Complete (2025-12-12)**
- Days 1-4: Mock CDW tables, dimension tables, ETL pipeline
- Days 5-9: Allergies widget, full page, severity coding, testing

**Current Status:** 5 clinical domains implemented, proven patterns established

**Next Steps:** Medications → Encounters → Labs → Orders

### 12.2 Milestone Demos

**Milestone 1 (Week 2) ✅ Complete:**
- ✅ Demo patient search with 36 real patients
- ✅ Demo CCOW integration
- ✅ Show end-to-end data flow diagram

**Milestone 2 (Week 4) ✅ Complete:**
- ✅ Demo patient flags with badge and modal
- ✅ Show three complete domains (demographics, demographics enhanced, flags)
- ✅ Demonstrate pattern repeatability

**Milestone 3 (Week 6) ✅ Complete:**
- ✅ Demo Vitals page with Chart.js visualizations
- ✅ Demo Allergies page with severity coding
- ✅ Show 5 clinical domains working (Demographics, Demographics Enhanced, Flags, Vitals, Allergies)
- ✅ Demonstrate dashboard widget pattern

**Next Milestone (Future):**
- [ ] Demo Medications page (RxOut + BCMA integration)
- [ ] Demo Encounters timeline
- [ ] Show 7+ clinical domains working

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

**Data Pipeline: ✅ Achieved**
- ✅ Bronze → Silver → Gold → PostgreSQL runs end-to-end for all 5 domains
- ✅ Pipeline completes in < 5 minutes for 36 patients
- ✅ All 36 patients have complete demographics
- ✅ No NULL values in required fields (name, DOB, sex)
- ✅ Age calculated correctly from DOB
- ✅ Facility names resolved correctly via Sta3n lookups

**UI Functionality: ✅ Achieved**
- ✅ Patient search returns results in < 500ms
- ✅ CCOW integration works (get, set, refresh)
- ✅ Topbar displays correctly on desktop, tablet, mobile
- ✅ Modals open/close smoothly (Flags, Vitals, Allergies)
- ✅ No JavaScript errors in console
- ✅ All HTMX triggers work correctly

**Data Quality: ✅ Achieved**
- ✅ All ICNs are unique (37 patients with unique identifiers)
- ✅ All SSN last 4 digits are valid
- ✅ All ages are reasonable (18-89 years in mock data)
- ✅ All sex values are M/F
- ✅ All station codes are valid and resolved to facility names

**Additional Success Criteria: ✅ Achieved**
- ✅ Dashboard widgets implemented for all domains
- ✅ Full page views implemented for Vitals and Allergies
- ✅ Chart.js visualizations working (Vitals domain)
- ✅ Severity-based color coding implemented (Allergies, Flags)
- ✅ Date range filtering working (Vitals domain)
- ✅ Lazy-loaded details modals (Flags history, Vital details, Allergy details)

### 13.2 Business Success Criteria

- ✅ Clinician can find a patient in < 10 seconds (typically < 2 seconds)
- ✅ Patient demographics display is clear and readable (enhanced with address/insurance)
- ✅ System demonstrates "faster than JLV" (< 2 seconds typical vs ~20 seconds in JLV)
- ✅ Pattern is proven and documented for additional domains (5 domains successfully implemented)
- ✅ Stakeholders are confident in architecture (medallion pattern validated across all domains)

### 13.3 Learning Success Criteria

- ✅ Team understands medallion architecture (Bronze → Silver → Gold → PostgreSQL)
- ✅ Team can add new domains independently (Vitals and Allergies followed same pattern)
- ✅ ETL patterns are documented and reusable (consistent across all 5 domains)
- ✅ PostgreSQL schema design is validated (serving database pattern proven)
- ✅ HTMX patterns are understood and repeatable (modals, widgets, full pages)
- ✅ Chart.js integration pattern established (Vitals domain)
- ✅ Widget + Full Page pattern established (all domains)

---

## 14. Related Documentation

### 14.1 Architecture and Planning

- **`docs/architecture.md`** - System architecture and routing decisions (Document v1.0) ✅ Complete
- **`med-z1-plan.md`** - High-level strategic plan and architecture overview
- **`ccow-vault-design.md`** - CCOW Context Vault technical specification (v1.1)
- **`patient-topbar-redesign-spec.md`** - Patient topbar UI detailed specification (v2.0)

### 14.2 Domain-Specific Design Documents

- **`patient-dashboard-design.md`** - Dashboard widget system specification (v1.1) ✅ Complete
- **`demographics-enhancement-design.md`** - Demographics enhancement (v1.1) ✅ Complete (2025-12-11)
- **`patient-flags-design.md`** - Patient Flags implementation (v1.2) ✅ Complete (2025-12-11)
- **`vitals-design.md`** - Vitals implementation ✅ Complete (2025-12-12)
- **`allergies-design.md`** - Allergies implementation ✅ Complete (2025-12-12)

### 14.3 Subsystem Documentation

- **`app/README.md`** - FastAPI application setup and routing patterns
- **`etl/README.md`** - ETL subsystem documentation (to be created)
- **`ccow/README.md`** - CCOW service documentation
- **`mock/README.md`** - Mock CDW documentation

### 14.4 Schema Documentation

- **`db/ddl/`** - PostgreSQL DDL scripts for all domains
  - `patient_demographics.sql` - Patient demographics serving table
  - `create_patient_flags_tables.sql` - Patient flags serving tables
  - Additional DDL scripts for Vitals and Allergies domains

### 14.5 Development Guides

- **`CLAUDE.md`** - Project-wide development guidance for Claude Code
- **`README.md`** - Project overview and quick start

---

## Document History

| Version | Date       | Author | Notes                                      |
|---------|------------|--------|--------------------------------------------|
| v1.0    | 2025-12-07 | Chuck  | Initial implementation roadmap             |
| v1.1    | 2025-12-13 | Claude | Updated to reflect actual implementation order and completed work |

---

**Summary of Changes in v1.1:**

**Completed Phases:**
- ✅ Phase 1: Minimal Viable Data Pipeline (Patient Demographics)
- ✅ Phase 2: Topbar UI with Real Data (Patient Search, CCOW)
- ✅ Phase 2.5: Demographics Enhancement (Address, Phone, Insurance) - 2025-12-11
- ✅ Phase 3: Patient Flags Domain - 2025-12-11
- ✅ Phase 4: Vitals Domain (Widget, Full Page, Charts) - 2025-12-12
- ✅ Phase 5: Allergies Domain (Widget, Full Page, Severity Coding) - 2025-12-12

**Actual Implementation Order:**
The implementation followed: Demographics → Demographics Enhancement → Patient Flags → Vitals → Allergies

This order differs from the original plan (which suggested Medications and Encounters before Vitals), but proves the pattern's flexibility and validates the medallion architecture across diverse clinical domains.

**Key Achievements:**
- 5 clinical domains fully operational
- Proven ETL pattern (Bronze → Silver → Gold → PostgreSQL)
- Established UI patterns (Dashboard widget + Full page + Details modal)
- Chart.js integration for data visualization
- Responsive design across all components
- Performance targets met (< 500ms API responses, < 2s page loads)

**Next Priorities:**
- Medications (RxOut + BCMA) - High clinical value, complex multi-table domain
- Encounters (Inpat) - Foundation for timeline views
- Labs (LabChem) - Similar to Vitals with trending/charting

---

**End of Document**
