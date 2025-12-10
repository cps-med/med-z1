# Patient Flags Design Specification - med-z1 Phase 3

**Document Version:** 1.0
**Last Updated:** 2025-12-09
**Phase:** Phase 3 - Patient Flags Domain Implementation
**Duration Estimate:** 1 week (5-7 days)

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
11. [Security and Privacy](#11-security-and-privacy)
12. [Appendices](#12-appendices)

---

## 1. Overview

### 1.1 Purpose

Phase 3 adds **Patient Record Flags** as the second clinical domain in med-z1, proving that the medallion data pipeline and UI patterns established in Phase 2 can scale to additional domains.

Patient flags are critical safety alerts displayed to clinical staff when accessing patient records. They include:
- **High Risk for Suicide** - Critical mental health alerts
- **Behavioral Flags** - Disruptive or threatening behavior history
- **Violence Prevention** - Safety protocols for staff
- **Clinical Flags** - Communicable disease, elopement risk, etc.
- **Administrative Flags** - Research participation, special handling

### 1.2 Scope

**In Scope for Phase 3:**
- Mock CDW database schema (3 tables in SQL Server)
- ETL pipeline: Bronze → Silver → Gold → PostgreSQL
- API endpoints for flag retrieval
- "View Flags" modal UI with real data
- Flag count badge on topbar button
- Category I (National) and Category II (Local) flags
- Review status calculation (CURRENT, DUE SOON, OVERDUE)
- Sensitive narrative text handling

**Out of Scope for Phase 3:**
- Flag creation/editing (read-only for now)
- Flag workflow (assignment, review, inactivation) - display only
- AI-generated DDI flags (Phase 5B)
- Real-time HL7 synchronization
- Multi-facility flag filtering (show all flags in Phase 3)

### 1.3 Key Design Decisions

1. **Three-table architecture:** Dimension (Dim.PatientRecordFlag), Assignment (SPatient.PatientRecordFlagAssignment), History (SPatient.PatientRecordFlagHistory)
2. **Sensitive data in SPatient schema:** Narrative text contains PHI and safety details
3. **Lazy loading:** Load flag list first, narrative details only when user clicks "View Details"
4. **Read-only implementation:** No flag creation/editing in Phase 3
5. **VistA alignment:** Schema closely mirrors VistA files #26.11, #26.13, #26.14, #26.15

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Prove the pattern:** Demonstrate that the Phase 2 ETL and UI patterns scale to additional domains
2. **Clinical value:** Provide essential safety information to clinicians
3. **Complete the topbar:** Enable the "View Flags" button with real data and badge count

### 2.2 Success Criteria

**Data Pipeline:**
- [ ] Mock CDW tables created and populated with sample data
- [ ] Bronze ETL extracts all 3 tables to Parquet
- [ ] Silver ETL harmonizes data (minimal in single-source mock)
- [ ] Gold ETL creates patient-centric flag view
- [ ] PostgreSQL serving DB loaded with flag data

**API:**
- [ ] `GET /api/patient/{icn}/flags` returns all active flags
- [ ] `GET /api/patient/flags-content` returns flags modal HTML
- [ ] Flag count endpoint works for badge display
- [ ] API performance < 500ms for typical patient

**UI:**
- [ ] "View Flags" button shows correct count badge
- [ ] Modal opens and displays formatted flags
- [ ] Flags show category, dates, review status
- [ ] "View Details" expands to show narrative (lazy loaded)
- [ ] Modal handles patients with 0 flags gracefully
- [ ] Responsive design works on mobile/tablet

**Quality:**
- [ ] Code follows established patterns from Phase 2
- [ ] Error handling for missing data
- [ ] Logging for debugging
- [ ] Documentation updated

---

## 3. Prerequisites

### 3.1 Completed Work

Before starting Phase 3, ensure Phase 2 is complete:
-  Patient demographics ETL pipeline working
-  PostgreSQL serving DB operational
-  Patient-aware topbar functional
-  Patient selection workflow tested
-  CCOW integration working

### 3.2 Environment Setup

**Required:**
- SQL Server mock CDW running (Docker/Podman)
- PostgreSQL serving DB running
- MinIO or local Parquet storage
- Python 3.11 virtual environment active
- FastAPI application running (port 8000)
- CCOW vault running (port 8001)

**Note:** Replace `<SA_PASSWORD>` with your SQL Server SA password in all sqlcmd commands below.

**Verify:**
```bash
# Check SQL Server
sqlcmd -S localhost -U sa -P <SA_PASSWORD> -Q "SELECT @@VERSION"

# Check PostgreSQL
docker exec -it postgres16 psql -U postgres -d postgres
SELECT version();

# Check Python environment
python --version  # Should be 3.11+
pip list | grep -E "fastapi|sqlalchemy|pyarrow"

# Check FastAPI is running
curl http://localhost:8000/api/patient/current
```

### 3.3 Reference Documents

- `docs/patient-flags-research.md` - CDW schema research and VistA mappings
- `docs/implementation-roadmap.md` - Overall project plan
- `app/templates/partials/patient_flags_modal.html` - Modal placeholder from Phase 2

---

## 4. Data Architecture

### 4.1 Source: Mock CDW (SQL Server)

**Three tables in SQL Server:**

```
CDWWork Database

Dim.PatientRecordFlag
 - Flag definitions (National and Local)
SPatient.PatientRecordFlagAssignment
 - Patient → Flag linkages
SPatient.PatientRecordFlagHistory
 -  Audit trail with narrative text
```

**See:** `mock/sql-server/cdwwork/create/*.sql` and `insert/*.sql`

### 4.2 Medallion Pipeline

```
Mock CDW (SQL Server)
    ↓
Bronze Layer (Parquet)
  - Raw extraction, minimal transformation
  - 3 Parquet files (one per table)
    ↓
Silver Layer (Parquet)
  - Cleaned, harmonized (minimal for single-source)
  - Resolved lookups (Sta3n names, etc.)
    ↓
Gold Layer (Parquet)
  - Patient-centric denormalized view
  - Review status calculated
  - Assignment → History joined
    ↓
PostgreSQL Serving DB
  - patient_flags table (query-optimized)
  - patient_flag_history table (sensitive)
```

### 4.3 PostgreSQL Serving Schema

**Two tables in PostgreSQL:**

1. **patient_flags** - Denormalized view for list queries
   - Combines Assignment + most recent History
   - Includes review status (CURRENT, DUE SOON, OVERDUE)
   - No narrative text (for performance)

2. **patient_flag_history** - Complete audit trail
   - Contains sensitive narrative text
   - Loaded only when user requests details
   - One row per history event

---

## 5. Database Schema

### 5.1 Mock CDW Schema (SQL Server)

See `docs/patient-flags-research.md` Section 3.2 for complete DDL.

**Summary:**

**Dim.PatientRecordFlag** (12 flags)
- PatientRecordFlagSID (PK)
- FlagName, FlagType, FlagCategory ('I' or 'II')
- ReviewFrequencyDays, ReviewNotificationDays
- NationalFlagIEN or LocalFlagIEN

**SPatient.PatientRecordFlagAssignment** (~19 assignments across 16 patients)
- PatientRecordFlagAssignmentSID (PK)
- PatientSID (FK to SPatient.SPatient)
- FlagName (denormalized)
- IsActive, AssignmentStatus
- AssignmentDateTime, InactivationDateTime
- OwnerSiteSta3n, ReviewFrequencyDays
- NextReviewDateTime

**SPatient.PatientRecordFlagHistory** (~28 history records)
- PatientRecordFlagHistorySID (PK)
- PatientRecordFlagAssignmentSID (FK)
- HistoryDateTime, ActionCode (1-5), ActionName
- EnteredByDUZ, ApprovedByDUZ
- **HistoryComments** (NVARCHAR(MAX) - SENSITIVE)
- EventSiteSta3n

### 5.2 Gold Schema (Parquet)

**File:** `lake/gold/patient_flags/patient_flags.parquet`

**Schema:**
```python
{
    "patient_key": "string",          # ICN
    "assignment_id": "int64",         # Assignment SID
    "flag_name": "string",
    "flag_category": "string",        # "I" or "II"
    "flag_type": "string",            # "CLINICAL", "BEHAVIORAL", etc.
    "is_active": "bool",
    "assignment_status": "string",    # "ACTIVE", "INACTIVE"
    "assignment_date": "timestamp",
    "inactivation_date": "timestamp",
    "owner_site": "string",           # Sta3n
    "owner_site_name": "string",      # Resolved facility name
    "review_frequency_days": "int32",
    "next_review_date": "timestamp",
    "review_status": "string",        # "CURRENT", "DUE SOON", "OVERDUE"
    "last_action_date": "timestamp",
    "last_action": "string",
    "last_action_by": "string"
    # Note: No narrative text in Gold - kept in History table
}
```

### 5.3 PostgreSQL Schema

**Table:** `patient_flags`

```sql
CREATE TABLE patient_flags (
    flag_id                 SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,   -- ICN
    assignment_id           BIGINT NOT NULL,
    flag_name               VARCHAR(100) NOT NULL,
    flag_category           VARCHAR(2) NOT NULL,    -- 'I' or 'II'
    flag_type               VARCHAR(30),
    is_active               BOOLEAN NOT NULL,
    assignment_status       VARCHAR(20) NOT NULL,
    assignment_date         TIMESTAMP NOT NULL,
    inactivation_date       TIMESTAMP,
    owner_site              VARCHAR(10),
    owner_site_name         VARCHAR(100),
    review_frequency_days   INTEGER,
    next_review_date        TIMESTAMP,
    review_status           VARCHAR(20),            -- 'CURRENT', 'DUE SOON', 'OVERDUE'
    last_action_date        TIMESTAMP,
    last_action             VARCHAR(50),
    last_action_by          VARCHAR(100),
    last_updated            TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_patient_flags_patient ON patient_flags (patient_key, is_active);
CREATE INDEX idx_patient_flags_review ON patient_flags (review_status, next_review_date);
```

**Table:** `patient_flag_history`

```sql
CREATE TABLE patient_flag_history (
    history_id              SERIAL PRIMARY KEY,
    assignment_id           BIGINT NOT NULL,
    patient_key             VARCHAR(50) NOT NULL,
    history_date            TIMESTAMP NOT NULL,
    action_code             SMALLINT NOT NULL,      -- 1-5
    action_name             VARCHAR(50) NOT NULL,
    entered_by_duz          INTEGER NOT NULL,
    entered_by_name         VARCHAR(100),
    approved_by_duz         INTEGER NOT NULL,
    approved_by_name        VARCHAR(100),
    tiu_document_ien        INTEGER,
    history_comments        TEXT,                   -- SENSITIVE narrative
    event_site              VARCHAR(10),
    created_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_flag_history_assignment ON patient_flag_history (assignment_id, history_date DESC);
CREATE INDEX idx_flag_history_patient ON patient_flag_history (patient_key, history_date DESC);
```

---

## 6. ETL Pipeline Design

### 6.1 Bronze Layer: `etl/bronze_patient_flags.py`

**Purpose:** Extract raw data from Mock CDW to Parquet

**Process:**
1. Connect to SQL Server CDWWork database
2. Extract three tables:
   - `Dim.PatientRecordFlag` → `bronze/patient_record_flag_dim/`
   - `SPatient.PatientRecordFlagAssignment` → `bronze/patient_record_flag_assignment/`
   - `SPatient.PatientRecordFlagHistory` → `bronze/patient_record_flag_history/`
3. Save as Parquet with minimal transformation
4. Log row counts and any extraction errors

**Example:**
```python
# etl/bronze_patient_flags.py
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine, text
from config import CDW_CONNECTION_STRING
import logging

logger = logging.getLogger(__name__)

def extract_flag_dimension():
    """Extract Dim.PatientRecordFlag table to Bronze Parquet."""
    engine = create_engine(CDW_CONNECTION_STRING)
    query = text("SELECT * FROM Dim.PatientRecordFlag WHERE IsActive = 1")

    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()
        logger.info(f"Extracted {len(rows)} flag definitions")

        # Convert to PyArrow table and save
        # ... (convert to Parquet)

def extract_flag_assignments():
    """Extract SPatient.PatientRecordFlagAssignment to Bronze Parquet."""
    # Similar pattern...

def extract_flag_history():
    """Extract SPatient.PatientRecordFlagHistory to Bronze Parquet."""
    # Similar pattern...

if __name__ == "__main__":
    extract_flag_dimension()
    extract_flag_assignments()
    extract_flag_history()
```

**Output Files:**
```
lake/bronze/patient_record_flag_dim/patient_record_flag_dim_20251209.parquet
lake/bronze/patient_record_flag_assignment/patient_record_flag_assignment_20251209.parquet
lake/bronze/patient_record_flag_history/patient_record_flag_history_20251209.parquet
```

### 6.2 Silver Layer: `etl/silver_patient_flags.py`

**Purpose:** Clean, validate, and enrich Bronze data

**Process:**
1. Read Bronze Parquet files
2. Data quality checks:
   - Validate required fields (FlagName, PatientSID, etc.)
   - Check date formats
   - Verify foreign key relationships
3. Resolve lookups:
   - Station names from Sta3n codes
   - Provider names from DUZ values (if available)
4. Harmonization (minimal in single-source mock):
   - Standardize date formats to UTC timestamps
   - Ensure consistent field naming
5. Save to Silver Parquet

**Example:**
```python
# etl/silver_patient_flags.py
import polars as pl
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_station_lookup():
    """Load Sta3n � Station Name mapping."""
    # Read from CDW or cached lookup table
    return pl.read_parquet("lake/silver/dim_sta3n/dim_sta3n.parquet")

def clean_assignments(bronze_df: pl.DataFrame, station_lookup: pl.DataFrame) -> pl.DataFrame:
    """Clean and enrich flag assignments."""
    df = bronze_df.clone()

    # Resolve station names
    df = df.join(
        station_lookup.select(["Sta3n", "Sta3nName"]),
        left_on="OwnerSiteSta3n",
        right_on="Sta3n",
        how="left"
    ).rename({"Sta3nName": "OwnerSiteName"})

    # Validate required fields
    assert df["PatientSID"].null_count() == 0, "Missing PatientSID values"
    assert df["FlagName"].null_count() == 0, "Missing FlagName values"

    # Convert dates to UTC timestamps
    df = df.with_columns([
        pl.col("AssignmentDateTime").dt.replace_time_zone("UTC"),
        pl.col("NextReviewDateTime").dt.replace_time_zone("UTC")
    ])

    logger.info(f"Cleaned {len(df)} assignment records")
    return df

def process_silver_layer():
    """Main Silver layer processing."""
    station_lookup = load_station_lookup()

    # Process assignments
    bronze_assignments = pl.read_parquet("lake/bronze/patient_record_flag_assignment/*.parquet")
    silver_assignments = clean_assignments(bronze_assignments, station_lookup)
    silver_assignments.write_parquet("lake/silver/patient_record_flag_assignment/patient_record_flag_assignment.parquet")

    # Process history (similar pattern)
    # Process dimension (minimal cleaning)
```

### 6.3 Gold Layer: `etl/gold_patient_flags.py`

**Purpose:** Create patient-centric denormalized view

**Process:**
1. Read Silver Parquet files
2. Join Assignment � Dimension � History (latest action only)
3. Calculate review status:
   - CURRENT: next_review_date > (today + notification_days)
   - DUE SOON: today d next_review_date d (today + notification_days)
   - OVERDUE: next_review_date < today
4. Map PatientSID � PatientICN using patient demographics
5. Create flattened structure optimized for UI queries
6. Save to Gold Parquet

**Example:**
```python
# etl/gold_patient_flags.py
import polars as pl
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def calculate_review_status(df: pl.DataFrame) -> pl.DataFrame:
    """Add review_status column based on dates."""
    today = datetime.now()

    return df.with_columns([
        pl.when(pl.col("NextReviewDateTime").is_null())
          .then(pl.lit("N/A"))
          .when(pl.col("NextReviewDateTime") < today)
          .then(pl.lit("OVERDUE"))
          .when(
              (pl.col("NextReviewDateTime") - timedelta(days=pl.col("ReviewNotificationDays"))) <= today
          )
          .then(pl.lit("DUE SOON"))
          .otherwise(pl.lit("CURRENT"))
          .alias("ReviewStatus")
    ])

def create_patient_flags_view():
    """Create Gold patient-centric flag view."""
    # Load Silver data
    assignments = pl.read_parquet("lake/silver/patient_record_flag_assignment/*.parquet")
    history = pl.read_parquet("lake/silver/patient_record_flag_history/*.parquet")
    patient_demographics = pl.read_parquet("lake/gold/patient_demographics/*.parquet")

    # Get most recent history for each assignment
    latest_history = (
        history
        .sort("HistoryDateTime", descending=True)
        .groupby("PatientRecordFlagAssignmentSID")
        .first()
        .select([
            "PatientRecordFlagAssignmentSID",
            "HistoryDateTime",
            "ActionName",
            "EnteredByName"
        ])
        .rename({
            "HistoryDateTime": "LastActionDate",
            "ActionName": "LastAction",
            "EnteredByName": "LastActionBy"
        })
    )

    # Join assignments with latest history
    df = (
        assignments
        .join(latest_history, on="PatientRecordFlagAssignmentSID", how="left")
        .join(
            patient_demographics.select(["PatientSID", "ICN"]),
            left_on="PatientSID",
            right_on="PatientSID",
            how="inner"
        )
        .rename({"ICN": "PatientKey"})
    )

    # Calculate review status
    df = calculate_review_status(df)

    # Select and rename columns for Gold schema
    gold_df = df.select([
        "PatientKey",
        pl.col("PatientRecordFlagAssignmentSID").alias("AssignmentID"),
        "FlagName",
        "FlagCategory",
        "FlagType",
        "IsActive",
        "AssignmentStatus",
        "AssignmentDateTime",
        "InactivationDateTime",
        "OwnerSiteSta3n",
        "OwnerSiteName",
        "ReviewFrequencyDays",
        "NextReviewDateTime",
        "ReviewStatus",
        "LastActionDate",
        "LastAction",
        "LastActionBy"
    ])

    logger.info(f"Created Gold view with {len(gold_df)} flag records")
    gold_df.write_parquet("lake/gold/patient_flags/patient_flags.parquet")
```

### 6.4 PostgreSQL Load: `etl/load_patient_flags.py`

**Purpose:** Load Gold Parquet into PostgreSQL serving DB

**Process:**
1. Read Gold patient_flags Parquet
2. Truncate/replace or upsert into PostgreSQL patient_flags table
3. Read Silver history Parquet (with narrative text)
4. Load into patient_flag_history table
5. Create indexes if not exists
6. Log row counts

**Example:**
```python
# etl/load_patient_flags.py
import polars as pl
from sqlalchemy import create_engine, text
from config import POSTGRES_CONNECTION_STRING
import logging

logger = logging.getLogger(__name__)

def load_patient_flags():
    """Load Gold patient flags into PostgreSQL."""
    engine = create_engine(POSTGRES_CONNECTION_STRING)

    # Read Gold Parquet
    df = pl.read_parquet("lake/gold/patient_flags/patient_flags.parquet")

    # Convert to pandas for SQLAlchemy (or use Polars write_database when stable)
    pandas_df = df.to_pandas()

    # Truncate and load
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE patient_flags"))
        pandas_df.to_sql(
            "patient_flags",
            conn,
            if_exists="append",
            index=False,
            method="multi"
        )
        logger.info(f"Loaded {len(pandas_df)} patient flags to PostgreSQL")

def load_flag_history():
    """Load Silver history into PostgreSQL."""
    # Similar pattern for patient_flag_history table
    # Includes sensitive narrative text
    pass

if __name__ == "__main__":
    load_patient_flags()
    load_flag_history()
```

---

## 7. API Endpoints

### 7.1 Endpoint Summary

| Method | Endpoint | Purpose | Response Type |
|--------|----------|---------|---------------|
| GET | `/api/patient/{icn}/flags` | Get all flags for patient (JSON) | JSON |
| GET | `/api/patient/flags-content` | Get flags modal HTML for current patient | HTML |
| GET | `/api/patient/{icn}/flags/{assignment_id}/history` | Get history for specific flag | JSON |

### 7.2 Get Patient Flags (JSON)

**Endpoint:** `GET /api/patient/{icn}/flags`

**Purpose:** Return all flags for a patient as JSON (for future API consumers)

**Request:**
```http
GET /api/patient/ICN100001/flags HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "patient_icn": "ICN100001",
  "total_flags": 1,
  "active_flags": 1,
  "national_flags": 1,
  "local_flags": 0,
  "overdue_count": 0,
  "flags": [
    {
      "assignment_id": 1,
      "flag_name": "HIGH RISK FOR SUICIDE",
      "flag_category": "I",
      "flag_type": "CLINICAL",
      "is_active": true,
      "assignment_status": "ACTIVE",
      "assignment_date": "2024-11-15T09:30:00Z",
      "owner_site": "518",
      "owner_site_name": "Northport VA Medical Center",
      "review_frequency_days": 90,
      "next_review_date": "2025-04-15T10:00:00Z",
      "review_status": "CURRENT",
      "last_action_date": "2025-01-15T10:00:00Z",
      "last_action": "CONTINUE",
      "last_action_by": "Dr. Emily Rodriguez"
    }
  ]
}
```

**Implementation:**
```python
# app/routes/patient.py

@router.get("/{icn}/flags")
async def get_patient_flags_json(icn: str):
    """Get patient flags as JSON."""
    from app.db.patient_flags import get_patient_flags

    flags = get_patient_flags(icn)

    if not flags:
        return {
            "patient_icn": icn,
            "total_flags": 0,
            "active_flags": 0,
            "national_flags": 0,
            "local_flags": 0,
            "overdue_count": 0,
            "flags": []
        }

    active_flags = [f for f in flags if f["is_active"]]
    national_flags = [f for f in active_flags if f["flag_category"] == "I"]
    local_flags = [f for f in active_flags if f["flag_category"] == "II"]
    overdue_flags = [f for f in active_flags if f["review_status"] == "OVERDUE"]

    return {
        "patient_icn": icn,
        "total_flags": len(flags),
        "active_flags": len(active_flags),
        "national_flags": len(national_flags),
        "local_flags": len(local_flags),
        "overdue_count": len(overdue_flags),
        "flags": flags
    }
```

### 7.3 Get Flags Modal Content (HTML)

**Endpoint:** `GET /api/patient/flags-content`

**Purpose:** Return formatted HTML for flags modal (HTMX target)

**Request:**
```http
GET /api/patient/flags-content HTTP/1.1
Host: localhost:8000
```

**Response:** HTML fragment

**Implementation:**
```python
# app/routes/patient.py

@router.get("/flags-content", response_class=HTMLResponse)
async def get_patient_flags_modal_content(request: Request):
    """Get patient flags modal content (HTML partial)."""
    from app.utils.ccow_client import ccow_client
    from app.db.patient_flags import get_patient_flags

    # Get current patient from CCOW
    patient_id = ccow_client.get_active_patient()

    if not patient_id:
        return "<p class='text-muted'>No active patient selected</p>"

    # Get flags from database
    flags = get_patient_flags(patient_id)

    if not flags:
        return "<p class='text-muted'>No active flags for this patient</p>"

    # Separate by category and status
    active_flags = [f for f in flags if f["is_active"]]
    national_flags = [f for f in active_flags if f["flag_category"] == "I"]
    local_flags = [f for f in active_flags if f["flag_category"] == "II"]

    # Render using template
    return templates.TemplateResponse(
        "partials/patient_flags_content.html",
        {
            "request": request,
            "national_flags": national_flags,
            "local_flags": local_flags,
            "total_count": len(active_flags)
        }
    )
```

### 7.4 Get Flag History (JSON)

**Endpoint:** `GET /api/patient/{icn}/flags/{assignment_id}/history`

**Purpose:** Return complete history timeline for a specific flag

**Request:**
```http
GET /api/patient/ICN100001/flags/1/history HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "assignment_id": 1,
  "patient_icn": "ICN100001",
  "flag_name": "HIGH RISK FOR SUICIDE",
  "history": [
    {
      "history_date": "2025-01-15T10:00:00Z",
      "action_code": 2,
      "action_name": "CONTINUE",
      "entered_by": "Dr. Emily Rodriguez",
      "approved_by": "Dr. Michael Chen (Chief of Staff)",
      "narrative": "Reviewed in Suicide Prevention team meeting 1/15/25...",
      "event_site": "518"
    },
    {
      "history_date": "2024-11-15T09:30:00Z",
      "action_code": 1,
      "action_name": "NEW ASSIGNMENT",
      "entered_by": "Dr. Sarah Johnson",
      "approved_by": "Dr. Michael Chen (Chief of Staff)",
      "narrative": "Flag created after ED visit for suicidal ideation...",
      "event_site": "518"
    }
  ]
}
```

**Implementation:**
```python
# app/routes/patient.py

@router.get("/{icn}/flags/{assignment_id}/history")
async def get_flag_history(icn: str, assignment_id: int):
    """Get complete history for a specific flag assignment."""
    from app.db.patient_flags import get_flag_history

    history = get_flag_history(assignment_id, icn)

    if not history:
        raise HTTPException(status_code=404, detail="Flag history not found")

    return {
        "assignment_id": assignment_id,
        "patient_icn": icn,
        "flag_name": history[0]["flag_name"],  # All records have same flag name
        "history": history
    }
```

### 7.5 Database Query Layer

**File:** `app/db/patient_flags.py`

```python
# app/db/patient_flags.py
from sqlalchemy import create_engine, text
from config import POSTGRES_CONNECTION_STRING
import logging

logger = logging.getLogger(__name__)
engine = create_engine(POSTGRES_CONNECTION_STRING)

def get_patient_flags(patient_icn: str) -> list[dict]:
    """
    Get all flags for a patient.
    Returns list of flag dictionaries.
    """
    query = text("""
        SELECT
            flag_id,
            assignment_id,
            flag_name,
            flag_category,
            flag_type,
            is_active,
            assignment_status,
            assignment_date,
            inactivation_date,
            owner_site,
            owner_site_name,
            review_frequency_days,
            next_review_date,
            review_status,
            last_action_date,
            last_action,
            last_action_by
        FROM patient_flags
        WHERE patient_key = :patient_icn
          AND is_active = true
        ORDER BY
            CASE WHEN flag_category = 'I' THEN 1 ELSE 2 END,
            assignment_date DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"patient_icn": patient_icn})
        rows = result.fetchall()

        flags = []
        for row in rows:
            flags.append({
                "flag_id": row[0],
                "assignment_id": row[1],
                "flag_name": row[2],
                "flag_category": row[3],
                "flag_type": row[4],
                "is_active": row[5],
                "assignment_status": row[6],
                "assignment_date": row[7].isoformat() if row[7] else None,
                "inactivation_date": row[8].isoformat() if row[8] else None,
                "owner_site": row[9],
                "owner_site_name": row[10],
                "review_frequency_days": row[11],
                "next_review_date": row[12].isoformat() if row[12] else None,
                "review_status": row[13],
                "last_action_date": row[14].isoformat() if row[14] else None,
                "last_action": row[15],
                "last_action_by": row[16]
            })

        logger.info(f"Retrieved {len(flags)} flags for patient {patient_icn}")
        return flags

def get_flag_history(assignment_id: int, patient_icn: str) -> list[dict]:
    """
    Get complete history timeline for a specific flag assignment.
    Includes SENSITIVE narrative text.
    """
    query = text("""
        SELECT
            history_id,
            history_date,
            action_code,
            action_name,
            entered_by_name,
            approved_by_name,
            history_comments,
            event_site
        FROM patient_flag_history
        WHERE assignment_id = :assignment_id
          AND patient_key = :patient_icn
        ORDER BY history_date DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "assignment_id": assignment_id,
            "patient_icn": patient_icn
        })
        rows = result.fetchall()

        history = []
        for row in rows:
            history.append({
                "history_id": row[0],
                "history_date": row[1].isoformat() if row[1] else None,
                "action_code": row[2],
                "action_name": row[3],
                "entered_by": row[4],
                "approved_by": row[5],
                "narrative": row[6],  # SENSITIVE
                "event_site": row[7]
            })

        logger.info(f"Retrieved {len(history)} history records for assignment {assignment_id}")
        return history

def get_flag_count(patient_icn: str) -> dict:
    """Get flag counts for badge display."""
    query = text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN flag_category = 'I' THEN 1 ELSE 0 END) as national,
            SUM(CASE WHEN flag_category = 'II' THEN 1 ELSE 0 END) as local,
            SUM(CASE WHEN review_status = 'OVERDUE' THEN 1 ELSE 0 END) as overdue
        FROM patient_flags
        WHERE patient_key = :patient_icn
          AND is_active = true
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"patient_icn": patient_icn})
        row = result.fetchone()

        return {
            "total": row[0] or 0,
            "national": row[1] or 0,
            "local": row[2] or 0,
            "overdue": row[3] or 0
        }
```

---

## 8. UI/UX Design

### 8.1 Topbar Integration

**Current State (Phase 2):**
- "View Flags" button is **disabled**
- No badge count displayed
- Modal exists but shows placeholder content

**Phase 3 Changes:**

1. **Enable button when patient selected:**
```javascript
// app/static/app.js
// Update after patient header loads
document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.detail.target.id === 'patient-header-container') {
        const patientHeader = e.detail.target.querySelector('.patient-header--active');
        const flagsBtn = document.getElementById('btn-patient-flags');

        if (patientHeader && flagsBtn) {
            // Patient is selected - enable flags button
            flagsBtn.disabled = false;

            // Fetch flag count and update badge
            updateFlagBadge();
        }
    }
});

function updateFlagBadge() {
    const icn = getCurrentPatientICN();  // Extract from patient header
    if (!icn) return;

    fetch(`/api/patient/${icn}/flags`)
        .then(res => res.json())
        .then(data => {
            const badge = document.getElementById('flags-badge');
            if (data.active_flags > 0) {
                badge.textContent = data.active_flags;
                badge.style.display = 'inline';

                // Red badge if overdue flags exist
                if (data.overdue_count > 0) {
                    badge.classList.add('badge--danger');
                    badge.classList.remove('badge--warning');
                } else {
                    badge.classList.add('badge--warning');
                    badge.classList.remove('badge--danger');
                }
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(err => console.error('Failed to fetch flag count:', err));
}
```

2. **Badge Display:**
```html
<!-- base.html topbar button -->
<button
    id="btn-patient-flags"
    class="btn btn--secondary"
    data-modal-open="patient-flags-modal"
    disabled
    title="View patient flags"
>
    <i class="fa-regular fa-flag"></i>
    View Flags
    <span id="flags-badge" class="badge badge--warning" style="display:none;">0</span>
</button>
```

### 8.2 Flags Modal Design

**Template:** `app/templates/partials/patient_flags_content.html`

**Structure:**
```html
<!-- Patient flags modal body content -->
{% if total_count == 0 %}
    <p class="text-muted">No active flags for this patient</p>
{% else %}
    <!-- Summary banner -->
    <div class="flags-summary">
        <p><strong>{{ total_count }}</strong> active flag{{ 's' if total_count != 1 else '' }}</p>
        <p class="text-muted">
            {{ national_flags|length }} National (Category I) |
            {{ local_flags|length }} Local (Category II)
        </p>
    </div>

    <!-- National Flags Section -->
    {% if national_flags %}
    <div class="flags-section">
        <h3 class="flags-section__title">
            <i class="fa-solid fa-flag"></i>
            National Flags (Category I)
        </h3>
        {% for flag in national_flags %}
            {% include "partials/flag_card.html" %}
        {% endfor %}
    </div>
    {% endif %}

    <!-- Local Flags Section -->
    {% if local_flags %}
    <div class="flags-section">
        <h3 class="flags-section__title">
            <i class="fa-regular fa-flag"></i>
            Local Flags (Category II)
        </h3>
        {% for flag in local_flags %}
            {% include "partials/flag_card.html" %}
        {% endfor %}
    </div>
    {% endif %}
{% endif %}
```

**Template:** `app/templates/partials/flag_card.html`

```html
<!-- Individual flag card -->
<div class="flag-card flag-card--{{ flag.flag_type|lower }} flag-card--{{ flag.review_status|lower|replace(' ', '-') }}">
    <div class="flag-card__header">
        <h4 class="flag-card__title">
            {% if flag.flag_type == 'CLINICAL' %}
                <i class="fa-solid fa-notes-medical"></i>
            {% elif flag.flag_type == 'BEHAVIORAL' %}
                <i class="fa-solid fa-user-shield"></i>
            {% elif flag.flag_type == 'RESEARCH' %}
                <i class="fa-solid fa-flask"></i>
            {% else %}
                <i class="fa-solid fa-flag"></i>
            {% endif %}
            {{ flag.flag_name }}
        </h4>
        <span class="flag-card__badge badge badge--{{ 'danger' if flag.review_status == 'OVERDUE' else 'warning' if flag.review_status == 'DUE SOON' else 'info' }}">
            {{ flag.review_status }}
        </span>
    </div>

    <div class="flag-card__metadata">
        <div class="flag-card__meta-item">
            <span class="label">Assigned:</span>
            <span class="value">{{ flag.assignment_date|format_date }}</span>
        </div>
        <div class="flag-card__meta-item">
            <span class="label">Owner Site:</span>
            <span class="value">{{ flag.owner_site_name }} ({{ flag.owner_site }})</span>
        </div>
        {% if flag.next_review_date %}
        <div class="flag-card__meta-item">
            <span class="label">Review Due:</span>
            <span class="value">{{ flag.next_review_date|format_date }}</span>
        </div>
        {% endif %}
        {% if flag.last_action %}
        <div class="flag-card__meta-item">
            <span class="label">Last Action:</span>
            <span class="value">{{ flag.last_action }} on {{ flag.last_action_date|format_date }} by {{ flag.last_action_by }}</span>
        </div>
        {% endif %}
    </div>

    <!-- Collapsible Details Section (lazy loaded) -->
    <details class="flag-card__details">
        <summary class="flag-card__summary">
            <i class="fa-solid fa-chevron-down"></i>
            View Safety Details & History
        </summary>
        <div class="flag-card__narrative"
             hx-get="/api/patient/{{ flag.patient_key }}/flags/{{ flag.assignment_id }}/history"
             hx-trigger="revealed once"
             hx-swap="innerHTML">
            <p class="text-muted">Loading details...</p>
        </div>
    </details>
</div>
```

**Narrative Display Template:** Returned by history endpoint

```html
<!-- Narrative and history timeline -->
<div class="flag-narrative">
    <div class="flag-narrative__warning">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <strong>Sensitive Safety Information</strong>
    </div>

    {% for event in history %}
    <div class="flag-history-event">
        <div class="flag-history-event__header">
            <strong>{{ event.action_name }}</strong>
            <span class="text-muted">{{ event.history_date|format_datetime }}</span>
        </div>
        <div class="flag-history-event__metadata">
            <p><strong>Entered by:</strong> {{ event.entered_by }}</p>
            <p><strong>Approved by:</strong> {{ event.approved_by }}</p>
            {% if event.event_site %}
            <p><strong>Site:</strong> {{ event.event_site }}</p>
            {% endif %}
        </div>
        {% if event.narrative %}
        <div class="flag-history-event__narrative">
            <p>{{ event.narrative }}</p>
        </div>
        {% endif %}
    </div>
    {% endfor %}
</div>
```

### 8.3 CSS Styles

**File:** `app/static/styles.css`

```css
/* ========================================
   Patient Flags Styles
   ======================================== */

/* Flag Summary */
.flags-summary {
    background: #f8f9fa;
    border-left: 4px solid #0066cc;
    padding: 1rem;
    margin-bottom: 1.5rem;
}

.flags-summary p {
    margin: 0.25rem 0;
}

/* Flags Section */
.flags-section {
    margin-bottom: 2rem;
}

.flags-section__title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Flag Card */
.flag-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #6b7280;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Flag type colors */
.flag-card--clinical {
    border-left-color: #dc2626;  /* Red */
}

.flag-card--behavioral {
    border-left-color: #ea580c;  /* Orange */
}

.flag-card--research {
    border-left-color: #0066cc;  /* Blue */
}

.flag-card--administrative {
    border-left-color: #6b7280;  /* Gray */
}

/* Review status highlights */
.flag-card--overdue {
    background: #fef2f2;  /* Light red tint */
}

.flag-card--due-soon {
    background: #fffbeb;  /* Light yellow tint */
}

/* Flag Card Header */
.flag-card__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
}

.flag-card__title {
    font-size: 1rem;
    font-weight: 600;
    margin: 0;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.flag-card__badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
}

/* Metadata Grid */
.flag-card__metadata {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.flag-card__meta-item {
    font-size: 0.875rem;
}

.flag-card__meta-item .label {
    font-weight: 600;
    color: #6b7280;
}

.flag-card__meta-item .value {
    color: #1f2937;
}

/* Details/Summary */
.flag-card__details {
    margin-top: 0.75rem;
    border-top: 1px solid #e5e7eb;
    padding-top: 0.75rem;
}

.flag-card__summary {
    cursor: pointer;
    font-weight: 600;
    color: #0066cc;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 0.25rem;
}

.flag-card__summary::-webkit-details-marker {
    display: none;
}

.flag-card__summary:hover {
    background: #f3f4f6;
}

.flag-card__details[open] .flag-card__summary i {
    transform: rotate(180deg);
}

/* Narrative Display */
.flag-narrative {
    margin-top: 1rem;
}

.flag-narrative__warning {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 0.25rem;
    padding: 0.75rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #991b1b;
    font-weight: 600;
}

.flag-history-event {
    background: #f9fafb;
    border-left: 3px solid #6b7280;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 0.25rem;
}

.flag-history-event:first-of-type {
    border-left-color: #0066cc;  /* Highlight most recent */
}

.flag-history-event__header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.flag-history-event__metadata p {
    margin: 0.25rem 0;
    font-size: 0.875rem;
    color: #6b7280;
}

.flag-history-event__narrative {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 0.25rem;
    padding: 0.75rem;
    margin-top: 0.75rem;
}

.flag-history-event__narrative p {
    margin: 0;
    line-height: 1.5;
    color: #1f2937;
}

/* Badge Colors */
.badge--danger {
    background: #dc2626;
    color: #ffffff;
}

.badge--warning {
    background: #f59e0b;
    color: #ffffff;
}

.badge--info {
    background: #0066cc;
    color: #ffffff;
}

/* Responsive Design */
@media (max-width: 768px) {
    .flag-card__metadata {
        grid-template-columns: 1fr;
    }

    .flag-card__header {
        flex-direction: column;
        gap: 0.5rem;
    }
}
```

---

## 9. Implementation Roadmap

### 9.1 Timeline Overview

**Total Duration:** 5-7 days

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Mock database setup, sample data | SQL scripts executed, data verified |
| 2-3 | ETL pipeline (Bronze/Silver/Gold) | Parquet files generated, PostgreSQL loaded |
| 4 | API endpoints and database queries | API routes working, tested with curl |
| 5 | UI templates and styling | Modal displays flags, badge works |
| 6 | Testing and refinement | All success criteria met |
| 7 | Buffer for issues and documentation | README updated, ready for demo |

### 9.2 Day-by-Day Plan

#### Day 1: Database Setup

**Note:** Replace `<SA_PASSWORD>` with your SQL Server SA password in all sqlcmd commands below.

**Tasks:**
1.  Execute create scripts (already created in this session)
   ```bash
   cd mock/sql-server/cdwwork/create
   sqlcmd -S localhost -U sa -P <SA_PASSWORD> -i Dim.PatientRecordFlag.sql
   sqlcmd -S localhost -U sa -P <SA_PASSWORD> -i SPatient.PatientRecordFlagAssignment.sql
   sqlcmd -S localhost -U sa -P <SA_PASSWORD> -i SPatient.PatientRecordFlagHistory.sql
   ```

2.  Execute insert scripts (already created in this session)
   ```bash
   cd mock/sql-server/cdwwork/insert
   sqlcmd -S localhost -U sa -P <SA_PASSWORD> -i Dim.PatientRecordFlag.sql
   sqlcmd -S localhost -U sa -P <SA_PASSWORD> -i SPatient.PatientRecordFlagAssignment.sql
   sqlcmd -S localhost -U sa -P <SA_PASSWORD> -i SPatient.PatientRecordFlagHistory.sql
   ```

3. Verify data
   ```sql
   -- Check record counts
   SELECT COUNT(*) FROM Dim.PatientRecordFlag;                 -- Expect 12
   SELECT COUNT(*) FROM SPatient.PatientRecordFlagAssignment;  -- Expect 19
   SELECT COUNT(*) FROM SPatient.PatientRecordFlagHistory;     -- Expect 28

   -- Sample queries
   SELECT TOP 5 * FROM Dim.PatientRecordFlag;
   SELECT TOP 5 * FROM SPatient.PatientRecordFlagAssignment WHERE IsActive = 1;
   SELECT TOP 5 * FROM SPatient.PatientRecordFlagHistory ORDER BY HistoryDateTime DESC;
   ```

4. Create PostgreSQL tables
   ```bash
   psql -h localhost -U postgres -d medz1 -f db/create_patient_flags_tables.sql
   ```

#### Day 2: Bronze ETL

**Tasks:**
1. Create `etl/bronze_patient_flags.py`
2. Extract three tables to Parquet
3. Verify Parquet files created
4. Run manually, verify output:
   ```bash
   python etl/bronze_patient_flags.py
   ls -lh lake/bronze/patient_record_flag_*/*.parquet
   ```

#### Day 3: Silver and Gold ETL

**Tasks:**
1. Create `etl/silver_patient_flags.py`
   - Clean data, resolve Sta3n lookups
2. Create `etl/gold_patient_flags.py`
   - Join tables, calculate review status, create patient-centric view
3. Create `etl/load_patient_flags.py`
   - Load into PostgreSQL
4. Test end-to-end pipeline:
   ```bash
   python etl/bronze_patient_flags.py
   python etl/silver_patient_flags.py
   python etl/gold_patient_flags.py
   python etl/load_patient_flags.py
   ```
5. Verify PostgreSQL data:
   ```sql
   SELECT COUNT(*) FROM patient_flags;         -- Expect 19
   SELECT COUNT(*) FROM patient_flag_history;  -- Expect 28
   SELECT * FROM patient_flags WHERE patient_key = 'ICN100001';
   ```

#### Day 4: API Development

**Tasks:**
1. Create `app/db/patient_flags.py` (database query layer)
2. Update `app/routes/patient.py` with three new endpoints:
   - `GET /api/patient/{icn}/flags` (JSON)
   - `GET /api/patient/flags-content` (HTML)
   - `GET /api/patient/{icn}/flags/{assignment_id}/history` (JSON)
3. Test with curl:
   ```bash
   # Get flags JSON
   curl http://localhost:8000/api/patient/ICN100001/flags

   # Get flags modal content (first set CCOW context)
   curl -X PUT http://localhost:8001/ccow/active-patient \
     -H "Content-Type: application/json" \
     -d '{"patient_id": "ICN100001", "set_by": "test"}'
   curl http://localhost:8000/api/patient/flags-content

   # Get flag history
   curl http://localhost:8000/api/patient/ICN100001/flags/1/history
   ```

#### Day 5: UI Implementation

**Tasks:**
1. Update `app/static/app.js`:
   - Add `updateFlagBadge()` function
   - Enable flags button when patient selected
2. Create `app/templates/partials/patient_flags_content.html`
3. Create `app/templates/partials/flag_card.html`
4. Add CSS to `app/static/styles.css`
5. Update `base.html` if needed (badge HTML already exists from Phase 2)
6. Test in browser:
   - Select patient
   - Verify "View Flags" button enables
   - Verify badge appears with correct count
   - Open modal, verify flags display
   - Click "View Details", verify narrative loads

#### Day 6: Testing and Refinement

**Tasks:**
1. Test all patients (especially those with 0 flags, 1 flag, multiple flags)
2. Test review status colors (CURRENT, DUE SOON, OVERDUE)
3. Test responsive design on mobile/tablet
4. Test keyboard navigation
5. Test error cases:
   - Patient with no flags
   - No patient selected
   - Database connection failure
6. Performance testing:
   - Measure API response times
   - Check HTMX swap speed
   - Verify lazy loading works
7. Fix any bugs discovered
8. Code review and cleanup

#### Day 7: Documentation and Wrap-up

**Tasks:**
1. Update `README.md` files in relevant directories
2. Add inline code comments
3. Update `docs/implementation-roadmap.md` to mark Phase 3 complete
4. Create demo script or video
5. Prepare handoff notes
6. Buffer for any remaining issues

---

## 10. Testing Strategy

### 10.1 Unit Tests

**File:** `tests/test_patient_flags.py`

```python
import pytest
from app.db.patient_flags import get_patient_flags, get_flag_count, get_flag_history

def test_get_patient_flags_with_data():
    """Test retrieving flags for patient with flags."""
    flags = get_patient_flags("ICN100001")
    assert len(flags) > 0
    assert flags[0]["flag_name"] == "HIGH RISK FOR SUICIDE"
    assert flags[0]["is_active"] is True

def test_get_patient_flags_no_data():
    """Test retrieving flags for patient with no flags."""
    flags = get_patient_flags("ICN100036")  # Patient with no flags
    assert len(flags) == 0

def test_get_flag_count():
    """Test flag count calculation."""
    counts = get_flag_count("ICN100010")  # Patient with 2 flags
    assert counts["total"] == 2
    assert counts["national"] == 2
    assert counts["local"] == 0

def test_get_flag_history():
    """Test flag history retrieval."""
    history = get_flag_history(1, "ICN100001")
    assert len(history) > 0
    assert history[0]["action_name"] in ["NEW ASSIGNMENT", "CONTINUE", "INACTIVATE"]
    assert "narrative" in history[0]

def test_review_status_calculation():
    """Test review status is calculated correctly."""
    flags = get_patient_flags("ICN100009")  # Patient with OVERDUE flag
    overdue_flags = [f for f in flags if f["review_status"] == "OVERDUE"]
    assert len(overdue_flags) > 0
```

### 10.2 Integration Tests

**File:** `tests/test_patient_flags_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_patient_flags_json():
    """Test JSON flags endpoint."""
    response = client.get("/api/patient/ICN100001/flags")
    assert response.status_code == 200
    data = response.json()
    assert "flags" in data
    assert data["total_flags"] > 0

def test_get_flags_modal_content_no_patient():
    """Test modal content with no active patient in CCOW."""
    # Clear CCOW context first
    response = client.get("/api/patient/flags-content")
    assert response.status_code == 200
    assert "No active patient" in response.text

def test_get_flag_history():
    """Test flag history endpoint."""
    response = client.get("/api/patient/ICN100001/flags/1/history")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert len(data["history"]) > 0
```

### 10.3 ETL Tests

**File:** `tests/test_patient_flags_etl.py`

```python
import pytest
import polars as pl
from pathlib import Path

def test_bronze_extraction():
    """Test Bronze layer creates Parquet files."""
    bronze_path = Path("lake/bronze/patient_record_flag_assignment")
    assert bronze_path.exists()

    df = pl.read_parquet(bronze_path / "*.parquet")
    assert len(df) > 0
    assert "PatientSID" in df.columns
    assert "FlagName" in df.columns

def test_gold_review_status():
    """Test Gold layer calculates review status correctly."""
    gold_path = Path("lake/gold/patient_flags/patient_flags.parquet")
    df = pl.read_parquet(gold_path)

    assert "ReviewStatus" in df.columns
    statuses = df["ReviewStatus"].unique().to_list()
    assert set(statuses).issubset({"CURRENT", "DUE SOON", "OVERDUE", "N/A"})

def test_postgres_load():
    """Test data loaded into PostgreSQL."""
    from app.db.patient_flags import get_patient_flags

    # Verify at least one patient has flags
    flags = get_patient_flags("ICN100001")
    assert len(flags) > 0
```

### 10.4 UI Tests (Manual)

**Test Scenarios:**

1. **No Patient Selected**
   - [ ] "View Flags" button is disabled
   - [ ] Badge is hidden

2. **Patient with 0 Flags**
   - [ ] Button enables when patient selected
   - [ ] Badge shows "0" or is hidden
   - [ ] Modal shows "No active flags" message

3. **Patient with 1 Flag**
   - [ ] Button enables
   - [ ] Badge shows "1"
   - [ ] Modal displays 1 flag card
   - [ ] Flag card shows all metadata
   - [ ] "View Details" expands to show narrative

4. **Patient with Multiple Flags**
   - [ ] Badge shows correct count
   - [ ] National flags appear first
   - [ ] Local flags appear second
   - [ ] Review status badges colored correctly

5. **Review Status Colors**
   - [ ] CURRENT flags: blue badge, white background
   - [ ] DUE SOON flags: yellow badge, light yellow background
   - [ ] OVERDUE flags: red badge, light red background

6. **Responsive Design**
   - [ ] Modal scrolls on mobile
   - [ ] Flag cards stack on narrow screens
   - [ ] Metadata grid adapts to screen size

7. **Accessibility**
   - [ ] Keyboard navigation works (Tab, Enter, Esc)
   - [ ] Screen reader can read flag names
   - [ ] Color contrast meets WCAG AA standards

---

## 11. Security and Privacy

### 11.1 Sensitive Data Handling

**Narrative Text Classification:**
- **Highly Sensitive:** Contains specific threat details, safety instructions, clinical reasoning
- **PHI:** Includes patient behaviors, mental health details, staff interactions
- **Protected:** Must be logged when accessed, restricted to authorized users

**Implementation:**

1. **Lazy Loading:** Narrative text not loaded until user clicks "View Details"
   ```javascript
   // Only fetch history when details revealed
   hx-trigger="revealed once"
   ```

2. **Access Logging:**
   ```python
   # app/db/patient_flags.py
   def get_flag_history(assignment_id: int, patient_icn: str) -> list[dict]:
       # ... fetch history ...

       # Log access to sensitive narrative
       logger.warning(
           f"SENSITIVE ACCESS: User viewed flag narrative for patient {patient_icn}, "
           f"assignment {assignment_id}"
       )

       return history
   ```

3. **Separate Tables:** Narrative in `patient_flag_history` table, not in main `patient_flags` table

### 11.2 Authorization (Future)

Phase 3 does not implement user authentication/authorization (development mode).

**Phase 4+ Requirements:**
- User must have `VIEW_PATIENT_FLAGS` permission
- Sensitive narrative requires `VIEW_FLAG_NARRATIVE` permission (higher level)
- Audit log all flag accesses with user ID, timestamp, patient ICN

### 11.3 Data Retention

**Development Mock:**
- Data persists indefinitely for testing

**Production:**
- Follow VA data retention policies
- Inactive flags may be archived after N years
- Audit logs retained per VHA directives

---

## 12. Appendices

### Appendix A: Sample Queries

**Get all active flags for a patient with review status:**
```sql
SELECT
    flag_name,
    flag_category,
    assignment_date,
    next_review_date,
    review_status,
    CASE
        WHEN review_status = 'OVERDUE' THEN DATEDIFF(day, next_review_date, GETDATE())
        ELSE NULL
    END as days_overdue
FROM patient_flags
WHERE patient_key = 'ICN100001'
  AND is_active = true
ORDER BY
    CASE WHEN flag_category = 'I' THEN 1 ELSE 2 END,
    CASE WHEN review_status = 'OVERDUE' THEN 1 WHEN review_status = 'DUE SOON' THEN 2 ELSE 3 END;
```

**Get patients with overdue flags:**
```sql
SELECT
    patient_key,
    COUNT(*) as overdue_count,
    MIN(next_review_date) as earliest_overdue
FROM patient_flags
WHERE is_active = true
  AND review_status = 'OVERDUE'
GROUP BY patient_key
ORDER BY earliest_overdue;
```

**Get flag activity summary by type:**
```sql
SELECT
    flag_type,
    COUNT(*) as total_flags,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_flags,
    SUM(CASE WHEN review_status = 'OVERDUE' THEN 1 ELSE 0 END) as overdue_flags
FROM patient_flags
GROUP BY flag_type
ORDER BY total_flags DESC;
```

### Appendix B: Error Codes

| Code | Meaning | HTTP Status |
|------|---------|-------------|
| FLAG_NOT_FOUND | Flag assignment not found | 404 |
| FLAG_HISTORY_NOT_FOUND | No history for assignment | 404 |
| PATIENT_NOT_FOUND | Patient ICN not found | 404 |
| DB_CONNECTION_ERROR | Database connection failed | 500 |
| INVALID_ICN_FORMAT | ICN format validation failed | 400 |

### Appendix C: Performance Benchmarks

**Target Response Times:**

| Operation | Target | Acceptable |
|-----------|--------|------------|
| Get patient flags (JSON) | < 200ms | < 500ms |
| Get flags modal content (HTML) | < 300ms | < 600ms |
| Get flag history | < 150ms | < 400ms |
| ETL Bronze extraction | < 30s | < 60s |
| ETL Gold transformation | < 45s | < 90s |
| PostgreSQL load | < 20s | < 40s |

### Appendix D: File Structure

```
med-z1/
   docs/
      patient-flags-research.md         # CDW research (this session)
      patient-flags-design.md           # This specification
   mock/sql-server/cdwwork/
      create/
         Dim.PatientRecordFlag.sql
         SPatient.PatientRecordFlagAssignment.sql
         SPatient.PatientRecordFlagHistory.sql
      insert/
          Dim.PatientRecordFlag.sql
          SPatient.PatientRecordFlagAssignment.sql
          SPatient.PatientRecordFlagHistory.sql
   etl/
      bronze_patient_flags.py
      silver_patient_flags.py
      gold_patient_flags.py
      load_patient_flags.py
   app/
      db/
         patient_flags.py
      routes/
         patient.py                    # Update with new endpoints
      templates/partials/
         patient_flags_content.html
         flag_card.html
      static/
          styles.css                    # Add flag styles
          app.js                        # Add badge update logic
   tests/
       test_patient_flags.py
       test_patient_flags_api.py
       test_patient_flags_etl.py
```

### Appendix E: References

- `docs/patient-flags-research.md` - CDW schema research
- `docs/implementation-roadmap.md` - Overall project plan
- `docs/patient-topbar-design.md` - Phase 2 design (pattern reference)
- VHA Directive 2010-053 - Patient Record Flags
- [VA VDL - PRF HL7 Specification](https://www.va.gov/vdl/documents/clinical/patient_record_flags/prfhl7is.doc)

---

**End of Specification**

**Document Status:** Ready for Implementation
**Next Step:** Begin Day 1 tasks (database setup already completed in this session)
