# Vitals Design Specification - med-z1

**Document Version:** 1.0
**Date:** 2025-12-11
**Status:** Design Phase
**Implementation Phase:** TBD (Post-Dashboard MVP)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Prerequisites](#3-prerequisites)
4. [Data Architecture](#4-data-architecture)
5. [Database Schema](#5-database-schema)
6. [ETL Pipeline Design](#6-etl-pipeline-design)
7. [API Endpoints](#7-api-endpoints)
8. [UI/UX Design](#8-uiux-design)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Testing Strategy](#10-testing-strategy)
11. [Appendices](#11-appendices)

---

## 1. Overview

### 1.1 Purpose

The **Vitals** domain provides comprehensive access to patient vital signs data, enabling clinicians to:
- View current vital signs at a glance (dashboard widget)
- Analyze vital signs trends over time (full vitals page)
- Identify abnormal values and clinical concerns
- Track compliance with vital signs monitoring protocols

Vital signs are fundamental clinical measurements including:
- **Blood Pressure (BP)** - Systolic/Diastolic (mmHg)
- **Temperature (T)** - Fahrenheit or Celsius
- **Pulse (P)** - Heart rate (beats/min)
- **Respiration (R)** - Respiratory rate (breaths/min)
- **Height (HT)** - Inches or centimeters
- **Weight (WT)** - Pounds or kilograms
- **Pain Scale (PN)** - 0-10 scale
- **Pulse Oximetry (POX)** - Oxygen saturation (%)
- **BMI** - Calculated from height/weight

### 1.2 Scope

**In Scope for Initial Implementation:**
- Mock CDW database schema (4 tables: Dimension + Fact + 2 Qualifier tables)
- ETL pipeline: Bronze → Silver → Gold → PostgreSQL
- Dashboard widget with two size options:
  - **Option A:** 1x1 (Standard) - 4-6 recent vitals in 2-column grid
  - **Option B:** 2x1 (Wide) - 6-8 recent vitals with mini-trends
  - Final widget size to be selected after design review
- Full Vitals page with:
  - Chronological table view (grid)
  - Vital signs trends/graphing (Chart.js line charts)
  - Abnormal value highlighting
  - Qualifiers display (hover tooltip + click for details)
  - Imperial/Metric unit toggle
  - BMI calculation and display
  - 6 months historical data (default)
- Read-only functionality
- Standard vital types (BP, T, P, R, WT, HT, PN, POX)

**Out of Scope for Initial Implementation:**
- Vital signs entry/editing (read-only for now)
- Advanced charting (e.g., multi-axis graphs, scatter plots)
- Vital signs warnings/alerts (AI-assisted)
- Custom vital types beyond standard set
- Real-time vital signs streaming
- Integration with medical devices
- Vital signs workflow (review, approval)

### 1.3 Key Design Decisions

1. **Star Schema:** Fact table (`Vital.VitalSign`) + Dimensions (`Dim.VitalType`, `Dim.VitalQualifier`)
2. **Split BP Values:** Systolic and Diastolic stored as separate columns for easier querying/graphing
3. **Qualifiers as Bridge Table:** Many-to-many relationship for flexibility
4. **Widget Shows Latest:** Dashboard widget displays most recent measurement per vital type (1x1 or 2x1 size options)
5. **Full Page Shows Timeline:** Vitals page displays chronological grid with all measurements
6. **BMI Calculation:** Calculated and displayed only on full Vitals page (not in widget)
7. **Historical Depth:** Default to 6 months of vitals data on full page
8. **Qualifiers Display:** Hover for quick preview, click for full details
9. **Unit Toggle:** Imperial/Metric unit conversion toggle on full page
10. **VistA Alignment:** Schema mirrors VistA File #120.5 (GMRV VITAL MEASUREMENT)
11. **Metric and Imperial:** Store both unit systems when possible (e.g., weight in lb and kg)

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Prove the pattern:** Demonstrate ETL and UI patterns scale to time-series clinical data
2. **Clinical value:** Provide essential vital signs information to support clinical decisions
3. **Complete the dashboard:** Enable Vitals widget with meaningful at-a-glance summary
4. **Foundation for graphing:** Establish data structures that support future trending/analytics

### 2.2 Success Criteria

**Data Pipeline:**
- [ ] Mock CDW tables created and populated with sample vitals data (30+ measurements per patient)
- [ ] Bronze ETL extracts all 4 tables to Parquet
- [ ] Silver ETL harmonizes data and resolves lookups (VitalType names, Qualifier names)
- [ ] Gold ETL creates patient-centric vitals view with calculated BMI
- [ ] PostgreSQL serving DB loaded with vitals data

**API:**
- [ ] `GET /api/patient/{icn}/vitals` returns all vitals (JSON)
- [ ] `GET /api/patient/{icn}/vitals/recent` returns latest measurement per type (for widget)
- [ ] `GET /api/patient/{icn}/vitals/{vital_type}/history` returns timeline for specific type
- [ ] `GET /api/dashboard/widget/vitals/{icn}` returns vitals widget HTML
- [ ] `GET /vitals` renders full Vitals page
- [ ] API performance < 500ms for typical patient vitals query

**UI (Widget):**
- [ ] Widget displays on dashboard (1x1 size)
- [ ] Shows 4-6 most critical recent vitals (BP, T, P, R, POX, Pain)
- [ ] Highlights abnormal values (red/yellow indicators)
- [ ] Displays measurement date/time
- [ ] "View All" link navigates to full Vitals page
- [ ] Loading state and error handling work correctly

**UI (Full Page):**
- [ ] Vitals page accessible from sidebar navigation
- [ ] Grid view displays chronological vital signs (date on rows, vital types on columns)
- [ ] Default date range set to 6 months of historical data
- [ ] Each cell shows value, unit, and timestamp
- [ ] Qualifiers display with hybrid approach:
  - Hover tooltip shows abbreviated qualifiers (e.g., "Sitting, L Arm")
  - Click opens modal with full qualifier details, entered by, location
- [ ] Abnormal values highlighted visually (red/yellow color coding)
- [ ] Unit toggle works (Imperial ↔ Metric)
- [ ] BMI calculated and displayed when height and weight available
- [ ] Basic trend visualization for BP, Weight, and Pain (Chart.js line charts)
- [ ] Charts update when unit toggle is changed
- [ ] Responsive design works on mobile/tablet
- [ ] Empty state when no vitals data available

**Quality:**
- [ ] Code follows established patterns from Demographics and Flags
- [ ] Error handling for missing data
- [ ] Logging for debugging
- [ ] Documentation complete

---

## 3. Prerequisites

### 3.1 Completed Work

Before starting Vitals implementation, ensure:
- ✅ Dashboard framework complete (Days 1-3)
- ✅ Demographics widget functional
- ✅ Patient Flags widget functional
- ✅ PostgreSQL serving DB operational
- ✅ MinIO or local Parquet storage available
- ✅ ETL pipeline patterns established (Bronze/Silver/Gold)

### 3.2 Environment Setup

**Required:**
- SQL Server mock CDW running (Docker/Podman)
- PostgreSQL serving DB running
- MinIO or local Parquet storage
- Python 3.11 virtual environment active
- FastAPI application running (port 8000)

**Verify:**
```bash
# Check SQL Server
sqlcmd -S localhost -U sa -P <SA_PASSWORD> -Q "SELECT @@VERSION"

# Check PostgreSQL
docker exec -it postgres16 psql -U postgres -d medz1

# Check Python environment
python --version  # Should be 3.11+
pip list | grep -E "fastapi|sqlalchemy|pyarrow|polars"

# Check FastAPI is running
curl http://localhost:8000/api/patient/current
```

### 3.3 Reference Documents

- `docs/vitals-research-gemini.md` - CDW schema research and JLV patterns
- `docs/patient-dashboard-design.md` - Dashboard widget specifications
- `docs/patient-flags-design.md` - Complete implementation example
- `docs/med-z1-plan.md` - Overall project plan

---

## 4. Data Architecture

### 4.1 Source: Mock CDW (SQL Server)

**Four tables in SQL Server:**

```
CDWWork Database

Dim.VitalType
  - Vital type definitions (BP, Temp, Pulse, etc.)

Vital.VitalSign
  - Fact table with measurements

Dim.VitalQualifier
  - Qualifier definitions (Sitting, Left Arm, etc.)

Vital.VitalSignQualifier
  - Bridge table linking VitalSign → Qualifiers
```

### 4.2 VistA Source Context

The CDW `Vital` domain is sourced from **VistA File #120.5 (GMRV VITAL MEASUREMENT)**.

**Key VistA Fields:**
- Patient (DFN)
- Type (e.g., BLOOD PRESSURE, TEMPERATURE)
- Rate/Value (the actual measurement)
- Date Taken (when vital was measured)
- Hospital Location (where vital was taken)
- Qualifiers (position, cuff size, site)

### 4.3 Medallion Pipeline

```
Mock CDW (SQL Server)
    ↓
Bronze Layer (Parquet)
  - Raw extraction, minimal transformation
  - 4 Parquet files (one per table)
    ↓
Silver Layer (Parquet)
  - Cleaned, harmonized
  - Resolved lookups (VitalType names, Qualifier names, Sta3n)
  - Unit conversions if needed
    ↓
Gold Layer (Parquet)
  - Patient-centric denormalized view
  - VitalSign + VitalType + Qualifiers joined
  - BMI calculated from height/weight
  - Abnormal flags added
    ↓
PostgreSQL Serving DB
  - patient_vitals table (query-optimized)
  - patient_vitals_qualifiers table (optional - can embed in JSON)
```

### 4.4 PostgreSQL Serving Schema

**Two tables in PostgreSQL:**

1. **patient_vitals** - Main vitals data
   - One row per vital sign measurement
   - Includes patient_key, vital_type, value, unit, timestamp
   - Calculated fields: BMI, abnormal_flag
   - Qualifiers embedded as JSON (or separate table)

2. **patient_vitals_qualifiers** (optional) - Qualifier details
   - Many-to-many relationship to patient_vitals
   - Can be denormalized into JSON in patient_vitals for simplicity

---

## 5. Database Schema

### 5.1 Mock CDW Schema (SQL Server)

#### 5.1.1 Dimension Table: Dim.VitalType

**Purpose:** Normalizes vital type strings (e.g., "BLOOD PRESSURE" vs "BP")

**DDL:**
```sql
USE CDWWork;
GO

CREATE SCHEMA Vital;
GO

CREATE TABLE Dim.VitalType (
    VitalTypeSID        INT IDENTITY(1,1) PRIMARY KEY,
    VitalTypeIEN        VARCHAR(50),                    -- VistA File 120.51 IEN
    VitalType           VARCHAR(100) NOT NULL,          -- e.g., "BLOOD PRESSURE"
    Abbreviation        VARCHAR(10) NOT NULL,           -- e.g., "BP"
    UnitOfMeasure       VARCHAR(20),                    -- e.g., "mmHg", "F", "lb"
    Category            VARCHAR(30),                    -- e.g., "VITAL SIGN", "MEASUREMENT"
    IsActive            BIT DEFAULT 1,
    Sta3n               SMALLINT,                       -- If locally defined

    CONSTRAINT UQ_VitalType_Abbr UNIQUE (Abbreviation)
);
GO

PRINT 'Table Dim.VitalType created successfully';
GO
```

**Seed Data (Essential for Vitals Widget):**
```sql
SET IDENTITY_INSERT Dim.VitalType ON;
GO

INSERT INTO Dim.VitalType (VitalTypeSID, VitalType, Abbreviation, UnitOfMeasure, Category, IsActive)
VALUES
    (1, 'BLOOD PRESSURE', 'BP', 'mmHg', 'VITAL SIGN', 1),
    (2, 'TEMPERATURE', 'T', 'F', 'VITAL SIGN', 1),
    (3, 'PULSE', 'P', '/min', 'VITAL SIGN', 1),
    (4, 'RESPIRATION', 'R', '/min', 'VITAL SIGN', 1),
    (5, 'HEIGHT', 'HT', 'in', 'MEASUREMENT', 1),
    (6, 'WEIGHT', 'WT', 'lb', 'MEASUREMENT', 1),
    (7, 'PAIN', 'PN', '0-10', 'VITAL SIGN', 1),
    (8, 'PULSE OXIMETRY', 'POX', '%', 'VITAL SIGN', 1),
    (9, 'BLOOD GLUCOSE', 'BG', 'mg/dL', 'MEASUREMENT', 1),
    (10, 'BMI', 'BMI', 'kg/m^2', 'CALCULATED', 1);
GO

SET IDENTITY_INSERT Dim.VitalType OFF;
GO
```

#### 5.1.2 Fact Table: Vital.VitalSign

**Purpose:** Stores actual vital sign measurements

**DDL:**
```sql
CREATE TABLE Vital.VitalSign (
    VitalSignSID            BIGINT IDENTITY(1,1) PRIMARY KEY,
    PatientSID              BIGINT NOT NULL,
    VitalTypeSID            INT NOT NULL,
    VitalSignTakenDateTime  DATETIME2(3) NOT NULL,      -- When vital was taken
    VitalSignEnteredDateTime DATETIME2(3),               -- When entered into VistA
    ResultValue             VARCHAR(50),                 -- String representation (e.g., "120/80")

    -- Numeric values for querying/graphing
    NumericValue            DECIMAL(10,2),               -- For single-value vitals (temp, pulse, etc.)
    Systolic                INT,                         -- For BP only
    Diastolic               INT,                         -- For BP only

    -- Metric equivalents (optional, for conversion)
    MetricValue             DECIMAL(10,2),               -- E.g., weight in kg, temp in C

    -- Location and staff
    LocationSID             INT,                         -- Hospital location
    EnteredByStaffSID       INT,                         -- Staff who entered

    -- Quality and status
    IsInvalid               CHAR(1) DEFAULT 'N',         -- Soft delete flag
    EnteredInError          CHAR(1) DEFAULT 'N',

    -- Metadata
    Sta3n                   SMALLINT,
    CreatedDateTimeUTC      DATETIME2(3) DEFAULT GETUTCDATE(),
    UpdatedDateTimeUTC      DATETIME2(3),

    CONSTRAINT FK_VitalSign_Type FOREIGN KEY (VitalTypeSID) REFERENCES Dim.VitalType(VitalTypeSID)
);
GO

-- Indexing (Critical for performance)
CREATE INDEX IX_VitalSign_Patient_Date
    ON Vital.VitalSign(PatientSID, VitalSignTakenDateTime DESC);

CREATE INDEX IX_VitalSign_Type_Date
    ON Vital.VitalSign(VitalTypeSID, VitalSignTakenDateTime DESC);

-- Index for recent vitals queries (widget)
CREATE INDEX IX_VitalSign_Patient_Type_Recent
    ON Vital.VitalSign(PatientSID, VitalTypeSID, VitalSignTakenDateTime DESC)
    WHERE IsInvalid = 'N';
GO

PRINT 'Table Vital.VitalSign created successfully';
GO
```

#### 5.1.3 Dimension Table: Dim.VitalQualifier

**Purpose:** Normalizes qualifiers (position, cuff size, site)

**DDL:**
```sql
CREATE TABLE Dim.VitalQualifier (
    VitalQualifierSID   INT IDENTITY(1,1) PRIMARY KEY,
    VitalQualifier      VARCHAR(100) NOT NULL,          -- e.g., "SITTING", "LEFT ARM"
    QualifierType       VARCHAR(50) NOT NULL,           -- e.g., "POSITION", "SITE", "CUFF SIZE"
    VitalQualifierIEN   VARCHAR(50),                    -- VistA IEN
    Sta3n               SMALLINT,
    IsActive            BIT DEFAULT 1
);
GO

PRINT 'Table Dim.VitalQualifier created successfully';
GO
```

**Seed Data (Common VistA Qualifiers):**
```sql
SET IDENTITY_INSERT Dim.VitalQualifier ON;
GO

INSERT INTO Dim.VitalQualifier (VitalQualifierSID, VitalQualifier, QualifierType, IsActive)
VALUES
    -- Position qualifiers
    (1, 'SITTING', 'POSITION', 1),
    (2, 'STANDING', 'POSITION', 1),
    (3, 'LYING', 'POSITION', 1),
    (4, 'SUPINE', 'POSITION', 1),

    -- Site qualifiers
    (5, 'LEFT ARM', 'SITE', 1),
    (6, 'RIGHT ARM', 'SITE', 1),
    (7, 'LEFT LEG', 'SITE', 1),
    (8, 'RIGHT LEG', 'SITE', 1),

    -- Cuff size qualifiers
    (9, 'ADULT', 'CUFF SIZE', 1),
    (10, 'LARGE ADULT', 'CUFF SIZE', 1),
    (11, 'PEDIATRIC', 'CUFF SIZE', 1),
    (12, 'THIGH', 'CUFF SIZE', 1),

    -- Method qualifiers
    (13, 'ORAL', 'METHOD', 1),
    (14, 'RECTAL', 'METHOD', 1),
    (15, 'TYMPANIC', 'METHOD', 1),
    (16, 'AXILLARY', 'METHOD', 1);
GO

SET IDENTITY_INSERT Dim.VitalQualifier OFF;
GO
```

#### 5.1.4 Bridge Table: Vital.VitalSignQualifier

**Purpose:** Many-to-many relationship between VitalSign and Qualifiers

**DDL:**
```sql
CREATE TABLE Vital.VitalSignQualifier (
    VitalSignQualifierSID   BIGINT IDENTITY(1,1) PRIMARY KEY,
    VitalSignSID            BIGINT NOT NULL,
    VitalQualifierSID       INT NOT NULL,

    CONSTRAINT FK_VSQual_Sign FOREIGN KEY (VitalSignSID)
        REFERENCES Vital.VitalSign(VitalSignSID),
    CONSTRAINT FK_VSQual_Qualifier FOREIGN KEY (VitalQualifierSID)
        REFERENCES Dim.VitalQualifier(VitalQualifierSID)
);
GO

-- Index for fast retrieval of qualifiers for a specific vital sign
CREATE INDEX IX_VitalSignQualifier_SignID
    ON Vital.VitalSignQualifier(VitalSignSID);
GO

PRINT 'Table Vital.VitalSignQualifier created successfully';
GO
```

### 5.2 Sample Data Strategy

**Mock Data Requirements:**
- 30-50 vital sign measurements per patient
- Span 12-24 months (for trending)
- Mix of vital types:
  - Every patient: BP, T, P, R (standard vitals)
  - Most patients: WT (weight tracking)
  - Some patients: HT (height - less frequent)
  - Some patients: PN (pain scores), POX (pulse ox)
- Realistic values:
  - BP: 90/60 to 180/110 (some normal, some abnormal)
  - Temp: 97.0F to 103.0F
  - Pulse: 50 to 130 bpm
  - Respiration: 12 to 28 breaths/min
  - Weight: 100 to 350 lbs
  - Pain: 0 to 10
  - POX: 88% to 100%
- Qualifiers on 60-70% of vitals (especially BP)

### 5.3 Gold Schema (Parquet)

**File:** `lake/gold/patient_vitals/patient_vitals.parquet`

**Schema:**
```python
{
    "patient_key": "string",              # ICN
    "vital_sign_id": "int64",             # VitalSignSID
    "vital_type": "string",               # "BLOOD PRESSURE", "TEMPERATURE", etc.
    "vital_abbr": "string",               # "BP", "T", "P", etc.
    "taken_datetime": "timestamp",
    "entered_datetime": "timestamp",
    "result_value": "string",             # Display value (e.g., "120/80", "98.6")
    "numeric_value": "float64",           # For single-value vitals
    "systolic": "int32",                  # For BP
    "diastolic": "int32",                 # For BP
    "metric_value": "float64",            # Converted value (temp in C, weight in kg)
    "unit_of_measure": "string",          # "mmHg", "F", "lb", etc.
    "qualifiers": "string",               # JSON array of qualifiers
    "location": "string",                 # Hospital location name
    "entered_by": "string",               # Staff name
    "abnormal_flag": "string",            # "HIGH", "LOW", "CRITICAL", "NORMAL"
    "bmi": "float64",                     # Calculated BMI (if WT and HT available)
    "source_system": "string",
    "last_updated": "timestamp"
}
```

**Abnormal Flag Logic:**
- **BP**:
  - CRITICAL: Systolic > 180 or < 90, Diastolic > 120 or < 60
  - HIGH: Systolic 140-180, Diastolic 90-120
  - LOW: Systolic 90-100, Diastolic 60-70
  - NORMAL: Otherwise
- **Temperature**:
  - CRITICAL: > 103.0F or < 95.0F
  - HIGH: 100.5F - 103.0F
  - LOW: 95.0F - 97.0F
  - NORMAL: Otherwise
- **Pulse**:
  - CRITICAL: > 130 or < 40
  - HIGH: 100-130
  - LOW: 40-60
  - NORMAL: Otherwise
- **Respiration**:
  - CRITICAL: > 28 or < 8
  - HIGH: 20-28
  - LOW: 8-12
  - NORMAL: Otherwise
- **POX**:
  - CRITICAL: < 88%
  - LOW: 88-92%
  - NORMAL: >= 92%

### 5.4 PostgreSQL Serving Schema

**Table:** `patient_vitals`

```sql
CREATE TABLE patient_vitals (
    vital_id                SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,       -- ICN
    vital_sign_id           BIGINT NOT NULL UNIQUE,     -- Source VitalSignSID
    vital_type              VARCHAR(100) NOT NULL,
    vital_abbr              VARCHAR(10) NOT NULL,
    taken_datetime          TIMESTAMP NOT NULL,
    entered_datetime        TIMESTAMP,
    result_value            VARCHAR(50),
    numeric_value           DECIMAL(10,2),
    systolic                INTEGER,                    -- BP only
    diastolic               INTEGER,                    -- BP only
    metric_value            DECIMAL(10,2),
    unit_of_measure         VARCHAR(20),
    qualifiers              JSONB,                      -- Store as JSON array
    location                VARCHAR(100),
    entered_by              VARCHAR(100),
    abnormal_flag           VARCHAR(20),                -- 'CRITICAL', 'HIGH', 'LOW', 'NORMAL'
    bmi                     DECIMAL(5,2),               -- Calculated
    last_updated            TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_patient_vitals_patient_date
    ON patient_vitals (patient_key, taken_datetime DESC);

CREATE INDEX idx_patient_vitals_type_date
    ON patient_vitals (vital_type, taken_datetime DESC);

-- Index for recent vitals widget queries
CREATE INDEX idx_patient_vitals_recent
    ON patient_vitals (patient_key, vital_abbr, taken_datetime DESC);

-- Index for abnormal vitals queries
CREATE INDEX idx_patient_vitals_abnormal
    ON patient_vitals (abnormal_flag, taken_datetime DESC)
    WHERE abnormal_flag IN ('CRITICAL', 'HIGH');
```

**Note:** Qualifiers stored as JSONB for flexibility. Example:
```json
[
  {"type": "POSITION", "value": "SITTING"},
  {"type": "SITE", "value": "LEFT ARM"},
  {"type": "CUFF SIZE", "value": "ADULT"}
]
```

---

## 6. ETL Pipeline Design

### 6.1 Bronze Layer: `etl/bronze_vitals.py`

**Purpose:** Extract raw data from Mock CDW to Parquet

**Process:**
1. Connect to SQL Server CDWWork database
2. Extract four tables:
   - `Dim.VitalType` → `bronze/vital_type_dim/`
   - `Vital.VitalSign` → `bronze/vital_sign/`
   - `Dim.VitalQualifier` → `bronze/vital_qualifier_dim/`
   - `Vital.VitalSignQualifier` → `bronze/vital_sign_qualifier/`
3. Save as Parquet with minimal transformation
4. Add metadata: `SourceSystem`, `LoadDateTime`
5. Log row counts and any extraction errors

**Example (excerpt):**
```python
# etl/bronze_vitals.py
import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)

def extract_vital_types():
    """Extract Dim.VitalType table to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.VitalType")

    minio_client = MinIOClient()
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )
    engine = create_engine(conn_str)

    query = """
    SELECT
        VitalTypeSID,
        VitalTypeIEN,
        VitalType,
        Abbreviation,
        UnitOfMeasure,
        Category,
        IsActive,
        Sta3n
    FROM Dim.VitalType
    WHERE IsActive = 1
    """

    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vital types from CDWWork")

    # Add metadata
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Write to MinIO
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="vital_type_dim",
        filename="vital_type_dim_raw.parquet"
    )
    minio_client.write_parquet(df, object_key)

    logger.info(f"Bronze extraction complete: {len(df)} vital types")
    return df

def extract_vital_signs():
    """Extract Vital.VitalSign table to Bronze layer."""
    # Similar pattern...
    pass

def extract_vital_qualifiers():
    """Extract Dim.VitalQualifier table to Bronze layer."""
    # Similar pattern...
    pass

def extract_vital_sign_qualifiers():
    """Extract Vital.VitalSignQualifier bridge table to Bronze layer."""
    # Similar pattern...
    pass

if __name__ == "__main__":
    extract_vital_types()
    extract_vital_signs()
    extract_vital_qualifiers()
    extract_vital_sign_qualifiers()
```

### 6.2 Silver Layer: `etl/silver_vitals.py`

**Purpose:** Clean, validate, and enrich Bronze data

**Process:**
1. Read Bronze Parquet files
2. Data quality checks:
   - Validate required fields (PatientSID, VitalTypeSID, TakenDateTime)
   - Check date formats and ranges
   - Verify foreign key relationships
   - Validate value ranges (e.g., BP 0-300, Temp 90-110F)
3. Resolve lookups:
   - VitalType names and abbreviations
   - Qualifier names and types
   - Location names from LocationSID
   - Staff names from StaffSID
4. Unit conversions:
   - Temperature: F ↔ C
   - Weight: lb ↔ kg
   - Height: in ↔ cm
5. Standardize field naming (snake_case)
6. Save to Silver Parquet

**Example (excerpt):**
```python
# etl/silver_vitals.py
import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)

def transform_vital_signs(minio_client, vital_types, qualifiers):
    """Transform Vital.VitalSign from Bronze to Silver."""
    logger.info("Starting Silver transformation: VitalSign")

    # Read Bronze
    bronze_path = build_bronze_path("cdwwork", "vital_sign", "vital_sign_raw.parquet")
    df = minio_client.read_parquet(bronze_path)
    logger.info(f"Read {len(df)} vital signs from Bronze")

    # Clean and standardize
    df = df.with_columns([
        pl.col("VitalSignSID").alias("vital_sign_sid"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("VitalTypeSID").alias("vital_type_sid"),
        pl.col("VitalSignTakenDateTime").cast(pl.Datetime).alias("taken_datetime"),
        pl.col("VitalSignEnteredDateTime").cast(pl.Datetime).alias("entered_datetime"),
        pl.col("ResultValue").str.strip_chars().alias("result_value"),
        pl.col("NumericValue").alias("numeric_value"),
        pl.col("Systolic").alias("systolic"),
        pl.col("Diastolic").alias("diastolic"),
        pl.col("MetricValue").alias("metric_value"),
        pl.col("IsInvalid").alias("is_invalid"),
        pl.col("Sta3n").alias("sta3n"),
    ])

    # Join with vital types
    df = df.join(
        vital_types.select(["vital_type_sid", "vital_type", "abbreviation", "unit_of_measure"]),
        on="vital_type_sid",
        how="left"
    )

    # Calculate metric conversions if missing
    df = df.with_columns([
        # Temp: F to C
        pl.when(
            (pl.col("abbreviation") == "T") & pl.col("metric_value").is_null()
        ).then(
            (pl.col("numeric_value") - 32) * 5 / 9
        ).otherwise(pl.col("metric_value")).alias("metric_value"),

        # Weight: lb to kg
        pl.when(
            (pl.col("abbreviation") == "WT") & pl.col("metric_value").is_null()
        ).then(
            pl.col("numeric_value") * 0.453592
        ).otherwise(pl.col("metric_value")).alias("metric_value"),
    ])

    # Data quality validations
    invalid_count = df.filter(pl.col("vital_type_sid").is_null()).height
    if invalid_count > 0:
        logger.warning(f"Found {invalid_count} vitals with unknown VitalTypeSID")

    # Write to Silver
    silver_path = build_silver_path("vital_sign", "vital_sign_cleaned.parquet")
    minio_client.write_parquet(df, silver_path)

    logger.info(f"Silver transformation complete: {len(df)} vital signs")
    return df
```

### 6.3 Gold Layer: `etl/gold_vitals.py`

**Purpose:** Create patient-centric denormalized view

**Process:**
1. Read Silver Parquet files
2. Join VitalSign + VitalType + Qualifiers
3. Calculate derived values:
   - BMI from most recent Height and Weight
   - Abnormal flags based on clinical ranges
4. Aggregate qualifiers into JSON array per vital sign
5. Map PatientSID → PatientICN using patient demographics
6. Create flattened structure optimized for UI queries
7. Save to Gold Parquet

**Example (excerpt):**
```python
# etl/gold_vitals.py
import polars as pl
from datetime import datetime, timezone
import logging
import json
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)

def calculate_abnormal_flag(df: pl.DataFrame) -> pl.DataFrame:
    """Add abnormal_flag column based on vital type and value."""

    df = df.with_columns([
        # Blood Pressure
        pl.when(
            (pl.col("abbreviation") == "BP") &
            ((pl.col("systolic") > 180) | (pl.col("systolic") < 90) |
             (pl.col("diastolic") > 120) | (pl.col("diastolic") < 60))
        ).then(pl.lit("CRITICAL"))
        .when(
            (pl.col("abbreviation") == "BP") &
            ((pl.col("systolic").is_between(140, 180)) |
             (pl.col("diastolic").is_between(90, 120)))
        ).then(pl.lit("HIGH"))
        .when(
            (pl.col("abbreviation") == "BP") &
            ((pl.col("systolic").is_between(90, 100)) |
             (pl.col("diastolic").is_between(60, 70)))
        ).then(pl.lit("LOW"))

        # Temperature
        .when(
            (pl.col("abbreviation") == "T") &
            ((pl.col("numeric_value") > 103.0) | (pl.col("numeric_value") < 95.0))
        ).then(pl.lit("CRITICAL"))
        .when(
            (pl.col("abbreviation") == "T") &
            (pl.col("numeric_value").is_between(100.5, 103.0))
        ).then(pl.lit("HIGH"))
        .when(
            (pl.col("abbreviation") == "T") &
            (pl.col("numeric_value").is_between(95.0, 97.0))
        ).then(pl.lit("LOW"))

        # Pulse
        .when(
            (pl.col("abbreviation") == "P") &
            ((pl.col("numeric_value") > 130) | (pl.col("numeric_value") < 40))
        ).then(pl.lit("CRITICAL"))
        .when(
            (pl.col("abbreviation") == "P") &
            (pl.col("numeric_value").is_between(100, 130))
        ).then(pl.lit("HIGH"))
        .when(
            (pl.col("abbreviation") == "P") &
            (pl.col("numeric_value").is_between(40, 60))
        ).then(pl.lit("LOW"))

        # Respiration
        .when(
            (pl.col("abbreviation") == "R") &
            ((pl.col("numeric_value") > 28) | (pl.col("numeric_value") < 8))
        ).then(pl.lit("CRITICAL"))
        .when(
            (pl.col("abbreviation") == "R") &
            (pl.col("numeric_value").is_between(20, 28))
        ).then(pl.lit("HIGH"))
        .when(
            (pl.col("abbreviation") == "R") &
            (pl.col("numeric_value").is_between(8, 12))
        ).then(pl.lit("LOW"))

        # Pulse Oximetry
        .when(
            (pl.col("abbreviation") == "POX") &
            (pl.col("numeric_value") < 88)
        ).then(pl.lit("CRITICAL"))
        .when(
            (pl.col("abbreviation") == "POX") &
            (pl.col("numeric_value").is_between(88, 92))
        ).then(pl.lit("LOW"))

        # Default
        .otherwise(pl.lit("NORMAL"))
        .alias("abnormal_flag")
    ])

    return df

def calculate_bmi(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate BMI from most recent height and weight.
    BMI = weight_kg / (height_m ^ 2)
    """
    # Get most recent height and weight per patient
    # (Implementation details...)
    pass

def create_gold_vitals():
    """Create Gold patient vitals view."""
    logger.info("=" * 70)
    logger.info("Starting Gold Vitals Creation")
    logger.info("=" * 70)

    minio_client = MinIOClient()

    # Read Silver data
    vital_signs = minio_client.read_parquet(
        build_silver_path("vital_sign", "vital_sign_cleaned.parquet")
    )
    qualifiers = minio_client.read_parquet(
        build_silver_path("vital_sign_qualifier", "vital_sign_qualifier_cleaned.parquet")
    )
    patient_demographics = minio_client.read_parquet(
        build_gold_path("patient_demographics", "patient_demographics.parquet")
    )

    # Aggregate qualifiers into JSON
    qualifiers_agg = (
        qualifiers
        .group_by("vital_sign_sid")
        .agg([
            pl.struct([
                pl.col("qualifier_type"),
                pl.col("qualifier_value")
            ]).alias("qualifiers")
        ])
        .with_columns([
            # Convert to JSON string
            pl.col("qualifiers").map_elements(
                lambda x: json.dumps([{"type": q["qualifier_type"], "value": q["qualifier_value"]} for q in x]),
                return_dtype=pl.Utf8
            ).alias("qualifiers_json")
        ])
    )

    # Join vitals with qualifiers
    df = vital_signs.join(qualifiers_agg, on="vital_sign_sid", how="left")

    # Calculate abnormal flags
    df = calculate_abnormal_flag(df)

    # Map to patient_key (ICN)
    patient_lookup = patient_demographics.select([
        pl.col("patient_sid").cast(pl.Int64),
        pl.col("patient_key")
    ])
    df = df.join(patient_lookup, on="patient_sid", how="inner")

    # Calculate BMI (separate function)
    # df = calculate_bmi(df)  # Adds BMI column

    # Create final Gold schema
    df_gold = df.select([
        "patient_key",
        "vital_sign_sid",
        "vital_type",
        "abbreviation",
        "taken_datetime",
        "entered_datetime",
        "result_value",
        "numeric_value",
        "systolic",
        "diastolic",
        "metric_value",
        "unit_of_measure",
        pl.col("qualifiers_json").alias("qualifiers"),
        "abnormal_flag",
        # "bmi",  # If calculated
        pl.lit(datetime.now(timezone.utc)).alias("last_updated")
    ])

    # Write to Gold
    gold_path = build_gold_path("patient_vitals", "patient_vitals.parquet")
    minio_client.write_parquet(df_gold, gold_path)

    logger.info(f"Gold vitals creation complete: {len(df_gold)} records")
    return df_gold
```

### 6.4 PostgreSQL Load: `etl/load_vitals.py`

**Purpose:** Load Gold Parquet into PostgreSQL serving DB

**Process:**
1. Read Gold `patient_vitals` Parquet
2. Truncate/replace or upsert into PostgreSQL `patient_vitals` table
3. Handle JSONB conversion for qualifiers
4. Create indexes if not exists
5. Log row counts and performance metrics

**Example:**
```python
# etl/load_vitals.py
import polars as pl
from sqlalchemy import create_engine, text
from config import POSTGRES_CONNECTION_STRING
import logging

logger = logging.getLogger(__name__)

def load_patient_vitals():
    """Load Gold patient vitals into PostgreSQL."""
    logger.info("Loading patient vitals into PostgreSQL...")

    engine = create_engine(POSTGRES_CONNECTION_STRING)

    # Read Gold Parquet
    df = pl.read_parquet("lake/gold/patient_vitals/patient_vitals.parquet")

    # Convert to pandas for SQLAlchemy
    pandas_df = df.to_pandas()

    # Truncate and load
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE patient_vitals"))
        pandas_df.to_sql(
            "patient_vitals",
            conn,
            if_exists="append",
            index=False,
            method="multi"
        )
        logger.info(f"Loaded {len(pandas_df)} vitals to PostgreSQL")

    # Verify load
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM patient_vitals"))
        count = result.scalar()
        logger.info(f"Verification: {count} records in patient_vitals table")

if __name__ == "__main__":
    load_patient_vitals()
```

---

## 7. API Endpoints

### 7.1 Endpoint Summary

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/patient/{icn}/vitals` | Get all vitals for patient (JSON) | JSON |
| GET | `/api/patient/{icn}/vitals/recent` | Get latest vitals per type (for widget) | JSON |
| GET | `/api/patient/{icn}/vitals/{vital_type}/history` | Get timeline for specific vital type | JSON |
| GET | `/api/dashboard/widget/vitals/{icn}` | Get vitals widget HTML | HTML |
| GET | `/vitals` | Full vitals page | HTML |

### 7.2 Get All Vitals (JSON)

**Endpoint:** `GET /api/patient/{icn}/vitals`

**Purpose:** Return all vitals for a patient as JSON

**Query Parameters:**
- `start_date` (optional): Filter vitals after this date
- `end_date` (optional): Filter vitals before this date
- `vital_type` (optional): Filter by vital type abbreviation (e.g., "BP", "T")
- `limit` (optional): Limit number of results (default: 1000)

**Response:**
```json
{
  "patient_icn": "ICN100001",
  "total_vitals": 45,
  "date_range": {
    "earliest": "2024-01-15T08:00:00Z",
    "latest": "2025-12-10T14:30:00Z"
  },
  "vitals": [
    {
      "vital_id": 1234,
      "vital_type": "BLOOD PRESSURE",
      "vital_abbr": "BP",
      "taken_datetime": "2025-12-10T14:30:00Z",
      "result_value": "128/82",
      "systolic": 128,
      "diastolic": 82,
      "unit": "mmHg",
      "abnormal_flag": "NORMAL",
      "qualifiers": [
        {"type": "POSITION", "value": "SITTING"},
        {"type": "SITE", "value": "LEFT ARM"}
      ],
      "location": "Primary Care Clinic",
      "entered_by": "RN Jane Smith"
    },
    {
      "vital_id": 1235,
      "vital_type": "TEMPERATURE",
      "vital_abbr": "T",
      "taken_datetime": "2025-12-10T14:30:00Z",
      "result_value": "98.6",
      "numeric_value": 98.6,
      "unit": "F",
      "abnormal_flag": "NORMAL",
      "qualifiers": [
        {"type": "METHOD", "value": "ORAL"}
      ]
    }
  ]
}
```

**Implementation:**
```python
# app/routes/vitals.py

from fastapi import APIRouter, Query
from typing import Optional
import logging

from app.db.vitals import get_patient_vitals

router = APIRouter(tags=["vitals"])
logger = logging.getLogger(__name__)

@router.get("/{icn}/vitals")
async def get_patient_vitals_json(
    icn: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    vital_type: Optional[str] = None,
    limit: int = Query(default=1000, le=5000)
):
    """Get all vitals for patient as JSON."""
    vitals = get_patient_vitals(
        icn,
        start_date=start_date,
        end_date=end_date,
        vital_type=vital_type,
        limit=limit
    )

    if not vitals:
        return {
            "patient_icn": icn,
            "total_vitals": 0,
            "vitals": []
        }

    # Calculate date range
    dates = [v["taken_datetime"] for v in vitals if v.get("taken_datetime")]
    date_range = {
        "earliest": min(dates) if dates else None,
        "latest": max(dates) if dates else None
    }

    return {
        "patient_icn": icn,
        "total_vitals": len(vitals),
        "date_range": date_range,
        "vitals": vitals
    }
```

### 7.3 Get Recent Vitals (Widget)

**Endpoint:** `GET /api/patient/{icn}/vitals/recent`

**Purpose:** Return most recent measurement for each vital type (used by widget)

**Response:**
```json
{
  "patient_icn": "ICN100001",
  "vitals": {
    "BP": {
      "value": "128/82",
      "taken_datetime": "2025-12-10T14:30:00Z",
      "abnormal_flag": "NORMAL"
    },
    "T": {
      "value": "98.6",
      "taken_datetime": "2025-12-10T14:30:00Z",
      "abnormal_flag": "NORMAL"
    },
    "P": {
      "value": "72",
      "taken_datetime": "2025-12-10T14:30:00Z",
      "abnormal_flag": "NORMAL"
    },
    "R": {
      "value": "16",
      "taken_datetime": "2025-12-10T14:30:00Z",
      "abnormal_flag": "NORMAL"
    },
    "POX": {
      "value": "98",
      "taken_datetime": "2025-12-10T14:30:00Z",
      "abnormal_flag": "NORMAL"
    },
    "PN": {
      "value": "2",
      "taken_datetime": "2025-12-09T10:15:00Z",
      "abnormal_flag": "NORMAL"
    }
  }
}
```

### 7.4 Get Vitals Widget HTML

**Endpoint:** `GET /api/dashboard/widget/vitals/{patient_icn}`

**Purpose:** Return vitals widget HTML for dashboard

**Response:** HTML fragment (see Section 8.2)

---

## 8. UI/UX Design

### 8.1 Vitals Widget (Dashboard)

**Note:** Two widget size options are provided below. **Option A (1x1)** and **Option B (2x1)** are both fully designed. Final selection to be made before implementation.

---

#### 8.1.1 Widget Option A: 1x1 Standard Size

**Widget Size:** 1x1 (Standard)

**Purpose:** Display most recent vital signs at a glance in compact format

**Content:**
- 4-6 most critical recent vitals (BP, T, P, R, POX, Pain)
- Display format: Abbreviation, Value, Unit
- Visual abnormal indicators (colored icons/badges)
- Measurement timestamp (relative: "2h ago" or absolute)
- "View All Vitals" link to full page

**Widget Template:** `app/templates/partials/vitals_widget.html`

```html
<!-- Vitals Widget Content -->
<!-- Widget Header -->
<div class="widget__header">
    <div class="widget__title-group">
        <i class="fa-solid fa-heart-pulse widget__icon"></i>
        <h3 class="widget__title">Vitals</h3>
    </div>
    {% if critical_count > 0 %}
        <span class="badge badge--danger">{{ critical_count }} Critical</span>
    {% elif abnormal_count > 0 %}
        <span class="badge badge--warning">{{ abnormal_count }} Abnormal</span>
    {% endif %}
</div>

<!-- Widget Body -->
<div class="widget__body">
    <div class="widget-vitals">
        {% if vitals_count == 0 %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">No vitals recorded</p>
        {% else %}
            <!-- Recent Vitals Grid -->
            <div class="vitals-grid-widget">
                {% for vital in recent_vitals %}
                <div class="vital-item-widget vital-item-widget--{{ vital.abnormal_flag|lower }}">
                    <div class="vital-item-widget__abbr">
                        {{ vital.vital_abbr }}
                        {% if vital.abnormal_flag != 'NORMAL' %}
                            <i class="fa-solid fa-triangle-exclamation vital-item-widget__warning"></i>
                        {% endif %}
                    </div>
                    <div class="vital-item-widget__value">
                        {{ vital.result_value }}
                    </div>
                    <div class="vital-item-widget__unit">{{ vital.unit }}</div>
                    <div class="vital-item-widget__time">{{ vital.taken_datetime|relative_time }}</div>
                </div>
                {% endfor %}
            </div>

            <!-- View All Link -->
            <div class="widget-action">
                <a href="/vitals" class="btn btn--link btn--sm">
                    <i class="fa-regular fa-arrow-up-right-from-square"></i>
                    View All Vitals
                </a>
            </div>
        {% endif %}
    </div>
</div>
```

**Widget CSS (excerpt):**
```css
/* Vitals Widget Styles */
.vitals-grid-widget {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    padding: 0.5rem 0;
}

.vital-item-widget {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.375rem;
    padding: 0.75rem;
    text-align: center;
}

.vital-item-widget--critical {
    background: #fef2f2;
    border-color: #fca5a5;
}

.vital-item-widget--high,
.vital-item-widget--low {
    background: #fffbeb;
    border-color: #fde68a;
}

.vital-item-widget__abbr {
    font-weight: 600;
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.25rem;
}

.vital-item-widget__value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0.25rem 0;
}

.vital-item-widget__unit {
    font-size: 0.75rem;
    color: #9ca3af;
}

.vital-item-widget__time {
    font-size: 0.625rem;
    color: #9ca3af;
    margin-top: 0.25rem;
}

.vital-item-widget__warning {
    color: #dc2626;
    font-size: 0.875rem;
}
```

---

#### 8.1.2 Widget Option B: 2x1 Wide Size

**Widget Size:** 2x1 (Wide)

**Purpose:** Display more vitals with mini-trend indicators for key measurements

**Content:**
- 6-8 recent vitals (BP, T, P, R, POX, Pain, WT, HT if available)
- Display format: Abbreviation, Value, Unit, Timestamp
- Visual abnormal indicators (colored backgrounds/badges)
- **Mini-trend sparklines** for BP, Weight, and Pain (last 7 days)
- BMI displayed if height/weight available (most recent)
- "View All Vitals" link to full page
- Qualifiers shown as small tags (e.g., "Sitting, L Arm")

**Widget Template:** `app/templates/partials/vitals_widget_wide.html`

```html
<!-- Vitals Widget Content (2x1 Wide) -->
<!-- Widget Header -->
<div class="widget__header">
    <div class="widget__title-group">
        <i class="fa-solid fa-heart-pulse widget__icon"></i>
        <h3 class="widget__title">Vitals</h3>
    </div>
    {% if critical_count > 0 %}
        <span class="badge badge--danger">{{ critical_count }} Critical</span>
    {% elif abnormal_count > 0 %}
        <span class="badge badge--warning">{{ abnormal_count }} Abnormal</span>
    {% endif %}
</div>

<!-- Widget Body -->
<div class="widget__body">
    <div class="widget-vitals-wide">
        {% if vitals_count == 0 %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">No vitals recorded</p>
        {% else %}
            <!-- Recent Vitals Table -->
            <div class="vitals-table-widget">
                <table>
                    <thead>
                        <tr>
                            <th>Vital</th>
                            <th>Value</th>
                            <th>Trend</th>
                            <th>Taken</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Blood Pressure -->
                        {% if recent_vitals.BP %}
                        <tr class="vital-row vital-row--{{ recent_vitals.BP.abnormal_flag|lower }}">
                            <td class="vital-abbr">
                                <strong>BP</strong>
                                {% if recent_vitals.BP.qualifiers %}
                                <span class="vital-qualifiers-tag">{{ recent_vitals.BP.qualifiers|join(', ') }}</span>
                                {% endif %}
                            </td>
                            <td class="vital-value">
                                {{ recent_vitals.BP.result_value }}
                                <span class="vital-unit">mmHg</span>
                                {% if recent_vitals.BP.abnormal_flag != 'NORMAL' %}
                                    <span class="vital-flag vital-flag--{{ recent_vitals.BP.abnormal_flag|lower }}">
                                        {{ recent_vitals.BP.abnormal_flag }}
                                    </span>
                                {% endif %}
                            </td>
                            <td class="vital-trend">
                                {% if recent_vitals.BP.trend_data %}
                                    <canvas class="sparkline" data-values="{{ recent_vitals.BP.trend_data|tojson }}"></canvas>
                                {% else %}
                                    <span class="text-muted">—</span>
                                {% endif %}
                            </td>
                            <td class="vital-time">{{ recent_vitals.BP.taken_datetime|relative_time }}</td>
                        </tr>
                        {% endif %}

                        <!-- Temperature -->
                        {% if recent_vitals.T %}
                        <tr class="vital-row vital-row--{{ recent_vitals.T.abnormal_flag|lower }}">
                            <td class="vital-abbr"><strong>T</strong></td>
                            <td class="vital-value">
                                {{ recent_vitals.T.result_value }}
                                <span class="vital-unit">°F</span>
                                {% if recent_vitals.T.abnormal_flag != 'NORMAL' %}
                                    <span class="vital-flag vital-flag--{{ recent_vitals.T.abnormal_flag|lower }}">
                                        {{ recent_vitals.T.abnormal_flag }}
                                    </span>
                                {% endif %}
                            </td>
                            <td class="vital-trend"><span class="text-muted">—</span></td>
                            <td class="vital-time">{{ recent_vitals.T.taken_datetime|relative_time }}</td>
                        </tr>
                        {% endif %}

                        <!-- Pulse -->
                        {% if recent_vitals.P %}
                        <tr class="vital-row vital-row--{{ recent_vitals.P.abnormal_flag|lower }}">
                            <td class="vital-abbr"><strong>P</strong></td>
                            <td class="vital-value">
                                {{ recent_vitals.P.result_value }}
                                <span class="vital-unit">bpm</span>
                                {% if recent_vitals.P.abnormal_flag != 'NORMAL' %}
                                    <span class="vital-flag vital-flag--{{ recent_vitals.P.abnormal_flag|lower }}">
                                        {{ recent_vitals.P.abnormal_flag }}
                                    </span>
                                {% endif %}
                            </td>
                            <td class="vital-trend"><span class="text-muted">—</span></td>
                            <td class="vital-time">{{ recent_vitals.P.taken_datetime|relative_time }}</td>
                        </tr>
                        {% endif %}

                        <!-- Respiration -->
                        {% if recent_vitals.R %}
                        <tr class="vital-row vital-row--{{ recent_vitals.R.abnormal_flag|lower }}">
                            <td class="vital-abbr"><strong>R</strong></td>
                            <td class="vital-value">
                                {{ recent_vitals.R.result_value }}
                                <span class="vital-unit">/min</span>
                                {% if recent_vitals.R.abnormal_flag != 'NORMAL' %}
                                    <span class="vital-flag vital-flag--{{ recent_vitals.R.abnormal_flag|lower }}">
                                        {{ recent_vitals.R.abnormal_flag }}
                                    </span>
                                {% endif %}
                            </td>
                            <td class="vital-trend"><span class="text-muted">—</span></td>
                            <td class="vital-time">{{ recent_vitals.R.taken_datetime|relative_time }}</td>
                        </tr>
                        {% endif %}

                        <!-- Pulse Oximetry -->
                        {% if recent_vitals.POX %}
                        <tr class="vital-row vital-row--{{ recent_vitals.POX.abnormal_flag|lower }}">
                            <td class="vital-abbr"><strong>POX</strong></td>
                            <td class="vital-value">
                                {{ recent_vitals.POX.result_value }}
                                <span class="vital-unit">%</span>
                                {% if recent_vitals.POX.abnormal_flag != 'NORMAL' %}
                                    <span class="vital-flag vital-flag--{{ recent_vitals.POX.abnormal_flag|lower }}">
                                        {{ recent_vitals.POX.abnormal_flag }}
                                    </span>
                                {% endif %}
                            </td>
                            <td class="vital-trend"><span class="text-muted">—</span></td>
                            <td class="vital-time">{{ recent_vitals.POX.taken_datetime|relative_time }}</td>
                        </tr>
                        {% endif %}

                        <!-- Pain -->
                        {% if recent_vitals.PN %}
                        <tr class="vital-row vital-row--{{ recent_vitals.PN.abnormal_flag|lower }}">
                            <td class="vital-abbr"><strong>Pain</strong></td>
                            <td class="vital-value">
                                {{ recent_vitals.PN.result_value }}
                                <span class="vital-unit">/10</span>
                                {% if recent_vitals.PN.abnormal_flag != 'NORMAL' %}
                                    <span class="vital-flag vital-flag--{{ recent_vitals.PN.abnormal_flag|lower }}">
                                        {{ recent_vitals.PN.abnormal_flag }}
                                    </span>
                                {% endif %}
                            </td>
                            <td class="vital-trend">
                                {% if recent_vitals.PN.trend_data %}
                                    <canvas class="sparkline" data-values="{{ recent_vitals.PN.trend_data|tojson }}"></canvas>
                                {% else %}
                                    <span class="text-muted">—</span>
                                {% endif %}
                            </td>
                            <td class="vital-time">{{ recent_vitals.PN.taken_datetime|relative_time }}</td>
                        </tr>
                        {% endif %}

                        <!-- Weight (if available) -->
                        {% if recent_vitals.WT %}
                        <tr class="vital-row vital-row--normal">
                            <td class="vital-abbr"><strong>WT</strong></td>
                            <td class="vital-value">
                                {{ recent_vitals.WT.result_value }}
                                <span class="vital-unit">lb</span>
                                {% if bmi %}
                                    <span class="vital-bmi">(BMI: {{ bmi }})</span>
                                {% endif %}
                            </td>
                            <td class="vital-trend">
                                {% if recent_vitals.WT.trend_data %}
                                    <canvas class="sparkline" data-values="{{ recent_vitals.WT.trend_data|tojson }}"></canvas>
                                {% else %}
                                    <span class="text-muted">—</span>
                                {% endif %}
                            </td>
                            <td class="vital-time">{{ recent_vitals.WT.taken_datetime|relative_time }}</td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>

            <!-- View All Link -->
            <div class="widget-action">
                <a href="/vitals" class="btn btn--link btn--sm">
                    <i class="fa-regular fa-arrow-up-right-from-square"></i>
                    View All Vitals & Trends
                </a>
            </div>
        {% endif %}
    </div>
</div>
```

**Widget CSS (2x1 Wide - excerpt):**
```css
/* Vitals Widget Wide Styles (2x1) */
.vitals-table-widget {
    width: 100%;
}

.vitals-table-widget table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}

.vitals-table-widget thead {
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
}

.vitals-table-widget th {
    padding: 0.5rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
}

.vitals-table-widget tbody tr {
    border-bottom: 1px solid #f3f4f6;
}

.vitals-table-widget tbody tr:last-child {
    border-bottom: none;
}

.vital-row td {
    padding: 0.625rem 0.5rem;
}

/* Abnormal row highlighting */
.vital-row--critical {
    background: #fef2f2;
}

.vital-row--high,
.vital-row--low {
    background: #fffbeb;
}

.vital-abbr {
    font-weight: 600;
    color: #374151;
    width: 20%;
}

.vital-qualifiers-tag {
    display: block;
    font-size: 0.625rem;
    color: #6b7280;
    font-weight: 400;
    margin-top: 0.125rem;
}

.vital-value {
    font-weight: 700;
    color: #1f2937;
    width: 35%;
}

.vital-unit {
    font-weight: 400;
    font-size: 0.75rem;
    color: #6b7280;
    margin-left: 0.25rem;
}

.vital-flag {
    display: inline-block;
    font-size: 0.625rem;
    font-weight: 600;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    margin-left: 0.5rem;
}

.vital-flag--critical {
    background: #dc2626;
    color: #ffffff;
}

.vital-flag--high,
.vital-flag--low {
    background: #f59e0b;
    color: #ffffff;
}

.vital-bmi {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 400;
    margin-left: 0.5rem;
}

.vital-trend {
    width: 25%;
    text-align: center;
}

.sparkline {
    width: 60px;
    height: 20px;
}

.vital-time {
    font-size: 0.75rem;
    color: #6b7280;
    width: 20%;
    text-align: right;
}
```

**Sparkline Chart JavaScript (using Chart.js):**
```javascript
// Initialize mini sparkline charts for trends
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.sparkline').forEach(canvas => {
        const values = JSON.parse(canvas.dataset.values || '[]');

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: values.map((_, i) => i),
                datasets: [{
                    data: values,
                    borderColor: '#0066cc',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.3
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    });
});
```

**2x1 Widget Example Display:**
```
┌──────────────────────────────────────────────────────────┐
│ ❤️  Vitals                                    ⚠️  1      │
├──────────────────────────────────────────────────────────┤
│ Vital    │ Value          │ Trend        │ Taken        │
├──────────┼────────────────┼──────────────┼──────────────┤
│ BP       │ 158/95 mmHg    │ ───/──       │ 1h ago       │
│ Sitting, │ HIGH           │              │              │
│ L Arm    │                │              │              │
├──────────┼────────────────┼──────────────┼──────────────┤
│ T        │ 98.6 °F        │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ P        │ 88 bpm         │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ R        │ 18 /min        │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ POX      │ 97 %           │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ Pain     │ 3 /10          │ ──▲─▼        │ 2h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ WT       │ 185 lb         │ ──▲──        │ 3d ago       │
│          │ (BMI: 27.3)    │              │              │
└──────────┴────────────────┴──────────────┴──────────────┘
│ [View All Vitals & Trends →]                            │
└──────────────────────────────────────────────────────────┘
```

**Design Comparison: Option A vs Option B**

| Feature | Option A (1x1) | Option B (2x1) |
|---------|---------------|----------------|
| **Space Used** | 1 grid cell | 2 grid cells |
| **Vitals Shown** | 4-6 vitals | 6-8 vitals |
| **Layout** | 2-column grid | Table format |
| **Trends** | No | Yes (sparklines for BP, Pain, WT) |
| **BMI** | No | Yes (if available) |
| **Qualifiers** | No | Yes (as small tags) |
| **Timestamp** | Below each vital | Right column |
| **Density** | Lower | Higher |
| **At-a-Glance** | Easier to scan | More information |
| **Best For** | Quick vital check | Detailed vital review |

**Recommendation:**
- **Option A (1x1):** Best for standard dashboard where space is at premium and user wants quick vital status
- **Option B (2x1):** Best when vitals are high priority and user benefits from trends and more detail without navigating away

---

### 8.2 Full Vitals Page

**Route:** `/vitals`

**Purpose:** Display comprehensive vital signs data with trending

**Page Structure:**
```
┌────────────────────────────────────────────────────────────┐
│ TOPBAR (sticky)                                            │
└────────────────────────────────────────────────────────────┘
┌──────────┬─────────────────────────────────────────────────┐
│          │  VITALS PAGE CONTENT                            │
│  SIDEBAR │  ┌──────────────────────────────────────────┐   │
│          │  │ Page Header                              │   │
│          │  │ "Vitals - [Patient Name]"                │   │
│          │  └──────────────────────────────────────────┘   │
│          │  ┌──────────────────────────────────────────┐   │
│          │  │ Filter/Controls                          │   │
│          │  │ [Date Range] [Vital Type] [View: Grid▼] │   │
│          │  └──────────────────────────────────────────┘   │
│          │  ┌──────────────────────────────────────────┐   │
│          │  │ Vital Signs Grid (Pivot Table)           │   │
│          │  │ Date/Time │ BP    │ T    │ P  │ R │ POX │   │
│          │  │ 12/10 2pm │ 128/82│ 98.6 │ 72 │16 │ 98% │   │
│          │  │ 12/10 8am │ 122/78│ 98.4 │ 68 │14 │ 97% │   │
│          │  │ 12/09 2pm │ 130/85│ 99.1 │ 74 │16 │ 98% │   │
│          │  └──────────────────────────────────────────┘   │
│          │  ┌──────────────────────────────────────────┐   │
│          │  │ Trend Charts                             │   │
│          │  │ [Blood Pressure Trend - Line Chart]      │   │
│          │  │ [Weight Trend - Line Chart]              │   │
│          │  │ [Pain Score Trend - Line Chart]          │   │
│          │  └──────────────────────────────────────────┘   │
└──────────┴─────────────────────────────────────────────────┘
```

**Grid View Features:**
- **Pivot Table:** Date/Time on Y-axis, Vital Types on X-axis
- **Qualifiers Display (Hybrid Approach):**
  - **Hover Tooltip:** Abbreviated qualifiers appear on hover (e.g., "Sitting, L Arm, Adult") for quick reference
  - **Click Modal:** Full qualifier details with entered by, location, and timestamp appear when cell is clicked
- **Color Coding:** Red (critical), Yellow (abnormal), Green (normal)
- **Sorting:** Click column headers to sort by date or vital type
- **Pagination:** Show 20-50 rows per page
- **Default Date Range:** 6 months of historical data
- **Unit Toggle:** Switch between Imperial (°F, lb, in) and Metric (°C, kg, cm)
- **BMI Display:** Calculated BMI shown when both height and weight are available

**Chart View Features:**
- **Line Charts:** Show trends over time using Chart.js
- **Multi-Series:** BP chart shows both Systolic and Diastolic lines
- **Reference Lines:** Normal ranges displayed as shaded areas (e.g., BP 90-140 systolic)
- **Tooltips:** Show exact values, qualifiers, and abnormal flags on hover
- **Zoom/Pan:** Allow users to focus on specific date ranges
- **Unit-Aware:** Charts update when unit toggle is changed (Imperial ↔ Metric)
- **Downloadable:** Export chart as PNG/PDF

**Template:** `app/templates/vitals.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="vitals-page">
    <!-- Page Header -->
    <div class="page-header">
        <h1 class="page-title">
            <i class="fa-solid fa-heart-pulse"></i>
            Vital Signs
        </h1>
        {% if patient %}
        <p class="page-subtitle">{{ patient.name_display }}</p>
        {% endif %}
    </div>

    <!-- Filter/Controls -->
    <div class="vitals-controls">
        <div class="vitals-filters">
            <label>
                Date Range:
                <input type="date" id="filter-start-date" />
                to
                <input type="date" id="filter-end-date" />
                <span class="filter-hint">(Default: Last 6 months)</span>
            </label>
            <label>
                Vital Type:
                <select id="filter-vital-type">
                    <option value="">All Types</option>
                    <option value="BP">Blood Pressure</option>
                    <option value="T">Temperature</option>
                    <option value="P">Pulse</option>
                    <option value="R">Respiration</option>
                    <option value="WT">Weight</option>
                    <option value="POX">Pulse Oximetry</option>
                    <option value="PN">Pain</option>
                </select>
            </label>
            <label>
                Units:
                <select id="filter-units">
                    <option value="imperial" selected>Imperial (°F, lb, in)</option>
                    <option value="metric">Metric (°C, kg, cm)</option>
                </select>
            </label>
        </div>
        <div class="vitals-view-toggle">
            <button class="btn btn--sm btn--primary" id="view-grid">
                <i class="fa-solid fa-table"></i> Grid
            </button>
            <button class="btn btn--sm btn--secondary" id="view-chart">
                <i class="fa-solid fa-chart-line"></i> Charts
            </button>
        </div>
    </div>

    <!-- Grid View -->
    <div class="vitals-grid-view" id="vitals-grid">
        <table class="vitals-table">
            <thead>
                <tr>
                    <th>Date/Time</th>
                    <th>BP<br><span class="th-unit">(mmHg)</span></th>
                    <th>T<br><span class="th-unit">(°F)</span></th>
                    <th>P<br><span class="th-unit">(bpm)</span></th>
                    <th>R<br><span class="th-unit">(br/min)</span></th>
                    <th>POX<br><span class="th-unit">(%)</span></th>
                    <th>Pain<br><span class="th-unit">(0-10)</span></th>
                </tr>
            </thead>
            <tbody>
                {% for row in vitals_grid %}
                <tr>
                    <td class="vitals-table__datetime">{{ row.datetime|format_datetime }}</td>
                    <td class="vitals-table__value vitals-table__value--{{ row.bp_flag|lower }}">
                        {% if row.bp %}
                            <span class="vital-value" data-vital-id="{{ row.bp_id }}" data-qualifiers="{{ row.bp_qualifiers }}">
                                {{ row.bp }}
                            </span>
                        {% else %}
                            <span class="vital-empty">—</span>
                        {% endif %}
                    </td>
                    <td class="vitals-table__value vitals-table__value--{{ row.temp_flag|lower }}">
                        {% if row.temp %}{{ row.temp }}{% else %}<span class="vital-empty">—</span>{% endif %}
                    </td>
                    <td class="vitals-table__value vitals-table__value--{{ row.pulse_flag|lower }}">
                        {% if row.pulse %}{{ row.pulse }}{% else %}<span class="vital-empty">—</span>{% endif %}
                    </td>
                    <td class="vitals-table__value vitals-table__value--{{ row.resp_flag|lower }}">
                        {% if row.resp %}{{ row.resp }}{% else %}<span class="vital-empty">—</span>{% endif %}
                    </td>
                    <td class="vitals-table__value vitals-table__value--{{ row.pox_flag|lower }}">
                        {% if row.pox %}{{ row.pox }}%{% else %}<span class="vital-empty">—</span>{% endif %}
                    </td>
                    <td class="vitals-table__value vitals-table__value--{{ row.pain_flag|lower }}">
                        {% if row.pain %}{{ row.pain }}{% else %}<span class="vital-empty">—</span>{% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Chart View (initially hidden) -->
    <div class="vitals-chart-view" id="vitals-charts" style="display:none;">
        <div class="chart-container">
            <h3>Blood Pressure Trend</h3>
            <canvas id="chart-bp"></canvas>
        </div>
        <div class="chart-container">
            <h3>Weight Trend</h3>
            <canvas id="chart-weight"></canvas>
        </div>
        <div class="chart-container">
            <h3>Pain Score Trend</h3>
            <canvas id="chart-pain"></canvas>
        </div>
    </div>

    <!-- Vital Details Modal (for qualifiers) -->
    <div id="vital-details-modal" class="modal" style="display:none;">
        <div class="modal__content">
            <div class="modal__header">
                <h3>Vital Details</h3>
                <button class="modal__close">&times;</button>
            </div>
            <div class="modal__body" id="vital-details-body">
                <!-- Loaded via HTMX or JS -->
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="/static/vitals.js"></script>
{% endblock %}
```

**Vitals Page CSS (excerpt):**
```css
/* Vitals Page Styles */
.vitals-page {
    padding: 1.5rem;
}

.page-header {
    margin-bottom: 1.5rem;
}

.page-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.vitals-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.5rem;
}

.vitals-filters {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.vitals-filters label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
}

/* Vitals Table */
.vitals-table {
    width: 100%;
    border-collapse: collapse;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border-radius: 0.5rem;
    overflow: hidden;
}

.vitals-table thead {
    background: #f3f4f6;
    border-bottom: 2px solid #e5e7eb;
}

.vitals-table th {
    padding: 0.75rem;
    text-align: center;
    font-weight: 600;
    font-size: 0.875rem;
    color: #374151;
}

.th-unit {
    font-weight: 400;
    font-size: 0.75rem;
    color: #6b7280;
}

.vitals-table td {
    padding: 0.75rem;
    text-align: center;
    border-bottom: 1px solid #f3f4f6;
}

.vitals-table__datetime {
    text-align: left;
    font-weight: 500;
    color: #1f2937;
}

/* Abnormal value highlighting */
.vitals-table__value--critical {
    background: #fef2f2;
    color: #991b1b;
    font-weight: 700;
}

.vitals-table__value--high,
.vitals-table__value--low {
    background: #fffbeb;
    color: #92400e;
    font-weight: 600;
}

.vitals-table__value--normal {
    color: #1f2937;
}

.vital-empty {
    color: #d1d5db;
}

.vital-value {
    cursor: pointer;
    position: relative;
}

.vital-value:hover {
    text-decoration: underline;
}

/* Chart containers */
.chart-container {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
}

.chart-container h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 1rem;
}

.chart-container canvas {
    max-height: 300px;
}
```

**Vitals Page JavaScript (excerpt):**
```javascript
// app/static/vitals.js

// Toggle between grid and chart views
document.getElementById('view-grid').addEventListener('click', () => {
    document.getElementById('vitals-grid').style.display = 'block';
    document.getElementById('vitals-charts').style.display = 'none';
    document.getElementById('view-grid').classList.add('btn--primary');
    document.getElementById('view-grid').classList.remove('btn--secondary');
    document.getElementById('view-chart').classList.remove('btn--primary');
    document.getElementById('view-chart').classList.add('btn--secondary');
});

document.getElementById('view-chart').addEventListener('click', () => {
    document.getElementById('vitals-grid').style.display = 'none';
    document.getElementById('vitals-charts').style.display = 'block';
    document.getElementById('view-chart').classList.add('btn--primary');
    document.getElementById('view-chart').classList.remove('btn--secondary');
    document.getElementById('view-grid').classList.remove('btn--primary');
    document.getElementById('view-grid').classList.add('btn--secondary');

    // Initialize charts if not already done
    if (!window.vitalsChartsInitialized) {
        initializeCharts();
        window.vitalsChartsInitialized = true;
    }
});

// Initialize Chart.js charts
function initializeCharts() {
    // Fetch vital signs data for charting
    const patientICN = getCurrentPatientICN();

    fetch(`/api/patient/${patientICN}/vitals?vital_type=BP&limit=30`)
        .then(res => res.json())
        .then(data => {
            createBPChart(data.vitals);
        });

    fetch(`/api/patient/${patientICN}/vitals?vital_type=WT&limit=30`)
        .then(res => res.json())
        .then(data => {
            createWeightChart(data.vitals);
        });

    fetch(`/api/patient/${patientICN}/vitals?vital_type=PN&limit=30`)
        .then(res => res.json())
        .then(data => {
            createPainChart(data.vitals);
        });
}

function createBPChart(vitals) {
    const ctx = document.getElementById('chart-bp').getContext('2d');
    const dates = vitals.map(v => new Date(v.taken_datetime).toLocaleDateString());
    const systolic = vitals.map(v => v.systolic);
    const diastolic = vitals.map(v => v.diastolic);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Systolic',
                    data: systolic,
                    borderColor: 'rgb(220, 38, 38)',
                    backgroundColor: 'rgba(220, 38, 38, 0.1)',
                    tension: 0.1
                },
                {
                    label: 'Diastolic',
                    data: diastolic,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                annotation: {
                    annotations: {
                        normalSystolic: {
                            type: 'box',
                            yScaleID: 'y',
                            yMin: 90,
                            yMax: 140,
                            backgroundColor: 'rgba(34, 197, 94, 0.1)'
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 50,
                    max: 200
                }
            }
        }
    });
}

function createWeightChart(vitals) {
    // Similar implementation for weight trend
}

function createPainChart(vitals) {
    // Similar implementation for pain score trend
}

// Click handler for vital values (show qualifiers)
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('vital-value')) {
        const vitalId = e.target.dataset.vitalId;
        const qualifiers = JSON.parse(e.target.dataset.qualifiers || '[]');

        // Show modal with qualifiers
        showVitalDetailsModal(vitalId, qualifiers);
    }
});

function showVitalDetailsModal(vitalId, qualifiers) {
    const modal = document.getElementById('vital-details-modal');
    const body = document.getElementById('vital-details-body');

    body.innerHTML = `
        <h4>Qualifiers:</h4>
        <ul>
            ${qualifiers.map(q => `<li><strong>${q.type}:</strong> ${q.value}</li>`).join('')}
        </ul>
    `;

    modal.style.display = 'block';
}
```

---

## 9. Implementation Roadmap

### 9.1 Timeline Overview

**Total Duration:** 6-8 days

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Mock database setup, sample data | SQL scripts executed, data verified |
| 2 | ETL Bronze layer | 4 Parquet files created |
| 3 | ETL Silver layer | Data cleaned, lookups resolved |
| 4 | ETL Gold layer, PostgreSQL load | Gold view created, serving DB loaded |
| 5 | API endpoints | All endpoints working, tested |
| 6 | Vitals widget | Widget displays on dashboard |
| 7 | Full vitals page (grid view) | Vitals page functional |
| 8 | Charts and polish | Trend charts working, testing complete |

### 9.2 Day-by-Day Plan

#### Day 1: Database Setup

**Tasks:**
1. Create `Dim.VitalType` table (CREATE + INSERT scripts)
2. Create `Vital.VitalSign` table (CREATE script)
3. Create `Dim.VitalQualifier` table (CREATE + INSERT scripts)
4. Create `Vital.VitalSignQualifier` table (CREATE script)
5. Generate mock vitals data (30-50 vitals per patient, INSERT script)
6. Execute scripts in CDWWork database
7. Create PostgreSQL `patient_vitals` table (DDL script)
8. Execute DDL in serving database

**Deliverables:**
- `mock/sql-server/cdwwork/create/Dim.VitalType.sql`
- `mock/sql-server/cdwwork/create/Vital.VitalSign.sql`
- `mock/sql-server/cdwwork/create/Dim.VitalQualifier.sql`
- `mock/sql-server/cdwwork/create/Vital.VitalSignQualifier.sql`
- `mock/sql-server/cdwwork/insert/Dim.VitalType.sql`
- `mock/sql-server/cdwwork/insert/Vital.VitalSign.sql` (with sample data)
- `mock/sql-server/cdwwork/insert/Dim.VitalQualifier.sql`
- `mock/sql-server/cdwwork/insert/Vital.VitalSignQualifier.sql` (link vitals → qualifiers)
- `db/ddl/create_patient_vitals_table.sql`

**Testing:**
```bash
# Verify SQL Server tables
sqlcmd -S localhost -U sa -P <SA_PASSWORD> -Q "SELECT COUNT(*) FROM Dim.VitalType"
sqlcmd -S localhost -U sa -P <SA_PASSWORD> -Q "SELECT COUNT(*) FROM Vital.VitalSign"

# Verify PostgreSQL table
docker exec -it postgres16 psql -U postgres -d medz1 -c "\d patient_vitals"
```

#### Day 2: Bronze ETL

**Tasks:**
1. Create `etl/bronze_vitals.py`
2. Implement extraction for all 4 tables
3. Run Bronze extracts
4. Verify Parquet files in MinIO/local lake

**Deliverables:**
- `etl/bronze_vitals.py`
- Bronze Parquet files:
  - `bronze/vital_type_dim/*.parquet`
  - `bronze/vital_sign/*.parquet`
  - `bronze/vital_qualifier_dim/*.parquet`
  - `bronze/vital_sign_qualifier/*.parquet`

**Testing:**
```bash
python -m etl.bronze_vitals
ls -lh lake/bronze/vital_*/*.parquet
```

#### Day 3: Silver ETL

**Tasks:**
1. Create `etl/silver_vitals.py`
2. Implement data cleaning and validation
3. Resolve Sta3n lookups (facility names)
4. Resolve VitalType and Qualifier lookups
5. Implement unit conversions (F↔C, lb↔kg)
6. Run Silver transformation
7. Verify output Parquet

**Deliverables:**
- `etl/silver_vitals.py`
- Silver Parquet files with cleaned data

**Testing:**
```bash
python -m etl.silver_vitals
# Verify joins worked correctly
# Check unit conversions
# Spot-check 5-10 vitals for accuracy
```

#### Day 4: Gold ETL & PostgreSQL Load

**Tasks:**
1. Create `etl/gold_vitals.py`
2. Implement patient-centric denormalized view
3. Join VitalSign + VitalType + Qualifiers
4. Calculate BMI from height/weight
5. Calculate abnormal flags
6. Aggregate qualifiers into JSON
7. Run Gold transformation
8. Create `etl/load_vitals.py`
9. Load Gold Parquet into PostgreSQL
10. Verify data in serving database

**Deliverables:**
- `etl/gold_vitals.py`
- `etl/load_vitals.py`
- Gold Parquet with patient vitals
- PostgreSQL `patient_vitals` table populated

**Testing:**
```bash
python -m etl.gold_vitals
python -m etl.load_vitals

# Verify PostgreSQL data
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM patient_vitals"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT * FROM patient_vitals WHERE patient_key = 'ICN100001' LIMIT 10"
```

#### Day 5: API Development

**Tasks:**
1. Create `app/db/vitals.py` (database query functions)
2. Create `app/routes/vitals.py` (API endpoints)
3. Implement endpoints:
   - `GET /api/patient/{icn}/vitals`
   - `GET /api/patient/{icn}/vitals/recent`
   - `GET /api/patient/{icn}/vitals/{vital_type}/history`
   - `GET /api/dashboard/widget/vitals/{icn}`
4. Test with curl

**Deliverables:**
- `app/db/vitals.py`
- `app/routes/vitals.py` (updated)
- All endpoints working

**Testing:**
```bash
# Test JSON endpoint
curl http://localhost:8000/api/patient/ICN100001/vitals | jq

# Test recent vitals endpoint
curl http://localhost:8000/api/patient/ICN100001/vitals/recent | jq

# Test vital type history
curl http://localhost:8000/api/patient/ICN100001/vitals/BP/history | jq
```

#### Day 6: Vitals Widget

**Tasks:**
1. Create `app/templates/partials/vitals_widget.html`
2. Update `app/routes/dashboard.py` to add vitals widget endpoint
3. Add vitals widget to dashboard template
4. Add CSS for vitals widget
5. Test in browser

**Deliverables:**
- `app/templates/partials/vitals_widget.html`
- Updated `app/routes/dashboard.py`
- Updated `app/static/styles.css` (vitals widget styles)
- Vitals widget visible on dashboard

**Testing:**
- View dashboard with patient selected
- Verify vitals widget displays recent vitals
- Verify abnormal flags highlighted
- Test with different patients (various vital patterns)

#### Day 7: Full Vitals Page (Grid View)

**Tasks:**
1. Create `app/templates/vitals.html`
2. Implement vitals grid pivot logic (backend)
3. Add route handler for `/vitals` page
4. Add CSS for vitals table
5. Implement cell click for qualifiers modal
6. Test responsive design

**Deliverables:**
- `app/templates/vitals.html`
- Updated `app/routes/vitals.py`
- Vitals page functional with grid view

**Testing:**
- Navigate to /vitals from sidebar
- Verify grid displays vitals correctly
- Test cell click to show qualifiers
- Test filtering by date range and vital type
- Test responsive design on mobile

#### Day 8: Charts and Polish

**Tasks:**
1. Implement Chart.js integration
2. Create BP trend chart
3. Create weight trend chart
4. Create pain score trend chart
5. Add view toggle (Grid ↔ Charts)
6. Polish UI/UX
7. Add error handling and loading states
8. Performance testing
9. Documentation updates

**Deliverables:**
- Trend charts functional
- View toggle working
- All features polished
- Documentation updated

**Testing:**
- Test all charts with different patients
- Test view toggle
- Performance check (page load < 3 seconds)
- Test edge cases (no vitals, single vital, etc.)

---

## 10. Testing Strategy

### 10.1 Unit Tests

**File:** `tests/test_vitals.py`

```python
import pytest
from app.db.vitals import get_patient_vitals, get_recent_vitals

def test_get_patient_vitals():
    """Test retrieving vitals for patient with data."""
    vitals = get_patient_vitals("ICN100001")
    assert len(vitals) > 0
    assert vitals[0]["vital_type"] in ["BLOOD PRESSURE", "TEMPERATURE", "PULSE"]

def test_get_recent_vitals():
    """Test retrieving most recent vital per type."""
    recent = get_recent_vitals("ICN100001")
    assert "BP" in recent or "T" in recent or "P" in recent
    if "BP" in recent:
        assert "systolic" in recent["BP"]
        assert "diastolic" in recent["BP"]

def test_abnormal_flag_calculation():
    """Test abnormal flag logic."""
    # High BP
    vitals = get_patient_vitals("ICN100001", vital_type="BP")
    high_bp = [v for v in vitals if v.get("systolic", 0) > 140]
    if high_bp:
        assert high_bp[0]["abnormal_flag"] in ["HIGH", "CRITICAL"]
```

### 10.2 Integration Tests

**Test Scenarios:**
1. End-to-end ETL pipeline
2. API endpoints return correct data
3. Widget displays on dashboard
4. Full vitals page renders
5. Charts load correctly

### 10.3 UI Tests (Manual)

**Test Cases:**
- [ ] Widget shows recent vitals (BP, T, P, R)
- [ ] Abnormal values highlighted correctly
- [ ] Grid view displays vitals chronologically
- [ ] Cell click shows qualifiers modal
- [ ] Charts display trends accurately
- [ ] View toggle (Grid ↔ Charts) works
- [ ] Filtering by date range works
- [ ] Filtering by vital type works
- [ ] Responsive design on mobile
- [ ] Empty state when no vitals
- [ ] Loading states display correctly
- [ ] Error handling works (patient not found, etc.)

---

## 11. Appendices

### Appendix A: VistA File Mappings

**VistA File #120.5 (GMRV VITAL MEASUREMENT)**

| VistA Field | CDW Column | Description |
|-------------|------------|-------------|
| .01 | VitalSignTakenDateTime | Date/Time Vital Taken |
| .02 | PatientSID | Patient (DFN) |
| .03 | VitalTypeSID | Type of Vital (pointer to 120.51) |
| .04 | EnteredByStaffSID | Entered By |
| .05 | LocationSID | Hospital Location |
| 1.2 | ResultValue | Rate (the value) |
| 1.3 | NumericValue | Numeric value (parsed) |
| 5 | Qualifiers | Qualifiers (sub-file) |

**VistA File #120.51 (GMRV VITAL TYPE)**

Maps to `Dim.VitalType`

### Appendix B: Abnormal Value Reference Ranges

| Vital | Normal Range | Low | High | Critical |
|-------|--------------|-----|------|----------|
| BP Systolic | 100-139 mmHg | 90-99 | 140-179 | <90 or ≥180 |
| BP Diastolic | 70-89 mmHg | 60-69 | 90-119 | <60 or ≥120 |
| Temperature | 97.0-99.9°F | 95.0-96.9 | 100.5-103.0 | <95.0 or >103.0 |
| Pulse | 60-100 bpm | 40-59 | 101-130 | <40 or >130 |
| Respiration | 12-20 br/min | 8-11 | 21-28 | <8 or >28 |
| Pulse Ox | ≥92% | 88-91 | N/A | <88 |
| Pain | 0-3 | N/A | 4-7 | 8-10 |

### Appendix C: Sample SQL Queries

**Get all vitals for a patient:**
```sql
SELECT
    vital_type,
    result_value,
    taken_datetime,
    abnormal_flag,
    qualifiers
FROM patient_vitals
WHERE patient_key = 'ICN100001'
ORDER BY taken_datetime DESC
LIMIT 50;
```

**Get most recent vital per type:**
```sql
SELECT DISTINCT ON (vital_abbr)
    vital_abbr,
    result_value,
    taken_datetime,
    abnormal_flag
FROM patient_vitals
WHERE patient_key = 'ICN100001'
ORDER BY vital_abbr, taken_datetime DESC;
```

**Get BP trend over last 30 days:**
```sql
SELECT
    taken_datetime,
    systolic,
    diastolic,
    abnormal_flag
FROM patient_vitals
WHERE patient_key = 'ICN100001'
  AND vital_abbr = 'BP'
  AND taken_datetime >= NOW() - INTERVAL '30 days'
ORDER BY taken_datetime;
```

### Appendix D: File Structure

```
med-z1/
  docs/
    vitals-design.md                          # This document
    vitals-research-gemini.md                 # Research from Gemini
  mock/sql-server/cdwwork/
    create/
      Dim.VitalType.sql
      Vital.VitalSign.sql
      Dim.VitalQualifier.sql
      Vital.VitalSignQualifier.sql
    insert/
      Dim.VitalType.sql
      Vital.VitalSign.sql
      Dim.VitalQualifier.sql
      Vital.VitalSignQualifier.sql
  db/ddl/
    create_patient_vitals_table.sql
  etl/
    bronze_vitals.py
    silver_vitals.py
    gold_vitals.py
    load_vitals.py
  app/
    db/
      vitals.py                               # Database query functions
    routes/
      vitals.py                               # API endpoints
    templates/
      vitals.html                             # Full vitals page
      partials/
        vitals_widget.html                    # Dashboard widget
    static/
      styles.css                              # Add vitals styles
      vitals.js                               # Vitals page JavaScript
  tests/
    test_vitals.py
    test_vitals_api.py
    test_vitals_etl.py
```

---

**End of Specification**

**Document Status:** Design Complete
**Next Steps:** Update patient-dashboard-design.md with Vitals widget specification
**Implementation:** Ready to begin when approved
