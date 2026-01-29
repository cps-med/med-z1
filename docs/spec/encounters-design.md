# Encounters Domain - Design Specification

**Document Version:** v1.1 (Implementation Complete)
**Last Updated:** December 15, 2025
**Implementation Status:** ✅ **COMPLETE** (All 6 days implemented 2025-12-15)
**Current Scope:** Inpatient Admissions (Phase 1)
**Future Scope:** Outpatient Encounters (Phase 2)

---

## Implementation Summary

**Status:** ✅ Fully implemented and tested
**Implementation Date:** December 15, 2025 (6-day roadmap completed)
**Total Dataset:** 73 encounters across 36 patients
**First Domain to Implement:** Pagination (ADR-005)

**Key Achievements:**
- ✅ Complete ETL pipeline (Bronze → Silver → Gold → PostgreSQL)
- ✅ Dashboard widget (1x1) showing recent encounters
- ✅ Full page with table, filtering, and pagination
- ✅ 73 test encounters with realistic distribution
- ✅ Pagination tested with patients having 30 and 15 encounters
- ✅ Patient ICN mapping fixed (ICN100001 format)
- ✅ "Home + O₂" disposition badge added (teal styling)
- ✅ Breadcrumb consistency established across all domain pages

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Prerequisites](#3-prerequisites)
4. [Data Architecture](#4-data-architecture)
5. [ETL Pipeline](#5-etl-pipeline)
6. [PostgreSQL Serving Database](#6-postgresql-serving-database)
7. [API Design](#7-api-design)
8. [UI Specifications](#8-ui-specifications)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Testing Strategy](#10-testing-strategy)
11. [Future Enhancements](#11-future-enhancements)

---

## 1. Overview

### 1.1 Purpose

The **Encounters domain** provides clinicians with visibility into patient hospital admissions and stays. This design document specifies the implementation of **Phase 1: Inpatient Admissions**, which displays:

- Active inpatient admissions (currently hospitalized)
- Historical inpatient stays (discharged)
- Admission/discharge dates, locations (wards), providers, and diagnoses
- Length of stay calculations

**Phase 2: Outpatient Encounters** (future) will add clinic visits, appointments, and outpatient procedures as a separate implementation (see Section 11).

### 1.2 Scope - Phase 1: Inpatient Admissions

**In Scope:**
- Hospital admissions and inpatient stays from VA facilities
- Active admissions (patient currently hospitalized)
- Historical admissions (discharged patients)
- Admit/discharge dates, ward locations, providers, primary diagnoses
- Length of stay (LOS) calculations
- Dashboard widget (1x1) showing 3-4 recent encounters
- Dedicated full-page view with filtering, sorting, and pagination

**Out of Scope (Phase 1):**
- Outpatient clinic visits (Phase 2 - future)
- Emergency department visits (Phase 2 - future)
- Detailed ward transfer history (Phase 2 enhancement)
- Real-time Vista overlay for T-0 data (Phase 3 - future)
- DoD encounter data (CHCS/AHLTA - explicitly out of scope)

### 1.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Domain Split** | Inpatient only (Phase 1) | Distinct data sources (VistA File #45 PTF vs #9000010), user workflows, and UI requirements warrant separate implementations |
| **Routing Pattern** | Pattern B (dedicated router) | Complex domain with full page view, filtering, and potential for future enhancements (ward transfers, Vista overlay) |
| **CDW Schema** | Modify existing `Inpat.Inpatient` table | Table already exists with basic structure; enhance with discharge fields rather than recreate |
| **Widget Size** | 1x1 (small) | Shows 3-4 recent encounters; full details available on dedicated page |
| **Test Data Volume** | 35 encounters across 36 patients | Sufficient to test active/discharged states, multiple facilities, date ranges, and edge cases |

---

## 2. Objectives and Success Criteria

### 2.1 Data Pipeline Objectives

- [ ] **Bronze Layer**: Extract raw inpatient admission data from `CDWWork.Inpat.Inpatient`
- [ ] **Silver Layer**: Clean, standardize, and resolve patient identity (ICN/PatientKey)
- [ ] **Gold Layer**: Create patient-centric, query-optimized Parquet files
- [ ] **PostgreSQL**: Load encounters into `patient_encounters` table with <2 second query performance

### 2.2 UI Objectives

- [ ] **Dashboard Widget (1x1)**: Display 3-4 most recent encounters with status (active/discharged)
- [ ] **Full Page View**: Comprehensive encounter list with:
  - Active vs discharged filtering
  - Sorting by date, facility, LOS
  - Pagination for patients with many admissions
  - Provider and diagnosis details

### 2.3 Success Criteria

- [ ] Widget loads in <2 seconds for 95% of patients
- [ ] Full page view loads in <3 seconds with 100+ encounters
- [ ] Correctly distinguishes active (current) vs discharged encounters
- [ ] Length of stay calculations accurate (handles ongoing admissions)
- [ ] All 35 test encounters display correctly across test patients
- [ ] Data pipeline runs end-to-end without errors

---

## 3. Prerequisites

### 3.1 Completed Work

**Required Foundations:**
- ✅ Bronze ETL framework (Polars-based extraction)
- ✅ Silver ETL framework (identity resolution, harmonization)
- ✅ Gold ETL framework (patient-centric transformations)
- ✅ PostgreSQL serving database setup
- ✅ FastAPI application with HTMX/Jinja2
- ✅ Dashboard widget system
- ✅ Pattern B routing examples (Vitals domain)

### 3.2 Environment Setup

**SQL Server (Mock CDW):**
- Container: `sqlserver2019` running SQL Server 2019
- Database: `CDWWork`
- Schema: `Inpat` (already exists)
- Table: `Inpat.Inpatient` (modify existing structure)

**PostgreSQL (Serving Database):**
- Container: `postgres16` running PostgreSQL 16
- Database: `medz1`
- New table: `patient_encounters`

**MinIO (Data Lake):**
- Bucket: `med-z1`
- Paths: `bronze/inpatient/`, `silver/inpatient/`, `gold/inpatient/`

---

## 4. Data Architecture

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

### 4.1 Source System - CDWWork.Inpat.Inpatient

**VistA Source:** Patient Treatment File (PTF) #45

**Complete Table Structure** (update `mock/sql-server/cdwwork/create/Inpat.Inpatient.sql`):
```sql
-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Inpat.Inpatient', 'U') IS NOT NULL
    DROP TABLE [Inpat].[Inpatient];
GO

-- Create enhanced Inpatient table with all required fields
CREATE TABLE [Inpat].[Inpatient] (
    -- Primary key
    [InpatientSID] BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Patient reference
    [PatientSID] INT NOT NULL,

    -- Admission details
    [AdmitDateTime] DATETIME2(0) NOT NULL,
    [AdmitLocationSID] INT NULL,
    [AdmittingProviderSID] INT NULL,
    [AdmitDiagnosisICD10] VARCHAR(20) NULL,

    -- Discharge details (NULL if active admission)
    [DischargeDateTime] DATETIME2(0) NULL,
    [DischargeDateSID] INT NULL,
    [DischargeWardLocationSID] INT NULL,
    [DischargeDiagnosisICD10] VARCHAR(20) NULL,
    [DischargeDiagnosis] VARCHAR(100) NULL,
    [DischargeDisposition] VARCHAR(50) NULL,

    -- Calculated fields
    [LengthOfStay] INT NULL,
    [EncounterStatus] VARCHAR(20) NULL, -- 'Active', 'Discharged'

    -- Facility
    [Sta3n] INT NOT NULL
);
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

-- Index on PatientSID for patient-centric queries
CREATE NONCLUSTERED INDEX [IX_Inpatient_PatientSID]
    ON [Inpat].[Inpatient] ([PatientSID]);
GO

-- Composite index for common query pattern (patient encounters sorted by date)
CREATE NONCLUSTERED INDEX [IX_Inpatient_PatientSID_AdmitDateTime]
    ON [Inpat].[Inpatient] ([PatientSID], [AdmitDateTime] DESC);
GO

-- Index on AdmitDateTime for date range queries
CREATE NONCLUSTERED INDEX [IX_Inpatient_AdmitDateTime]
    ON [Inpat].[Inpatient] ([AdmitDateTime] DESC);
GO

-- Index on Sta3n for facility-based queries
CREATE NONCLUSTERED INDEX [IX_Inpatient_Sta3n]
    ON [Inpat].[Inpatient] ([Sta3n]);
GO

-- Index on EncounterStatus for active/discharged filtering
CREATE NONCLUSTERED INDEX [IX_Inpatient_EncounterStatus]
    ON [Inpat].[Inpatient] ([EncounterStatus])
    WHERE [EncounterStatus] IS NOT NULL;
GO
```

**Key Changes from Existing Table:**
- Added 9 new fields for discharge details and diagnoses
- All new fields are nullable (NULL = active admission or data not documented)
- Added 5 indexes to optimize common query patterns:
  - Patient-centric queries (PatientSID)
  - Patient encounters sorted by date (PatientSID + AdmitDateTime)
  - Date range queries (AdmitDateTime)
  - Facility filtering (Sta3n)
  - Active/discharged filtering (EncounterStatus)
- Maintains backward compatibility with existing PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, Sta3n

### 4.2 Test Data Strategy

**Volume:** 35 total encounters across 36 patients

**Distribution:**
- **Active Admissions**: 5 encounters (DischargeDateTime IS NULL)
- **Recent Discharges** (<30 days): 10 encounters
- **Historical Discharges** (30-365 days): 15 encounters
- **Old Discharges** (>365 days): 5 encounters

**Facility Coverage:**
- Site 508 (Atlanta): 12 encounters
- Site 516 (Bay Pines): 10 encounters
- Site 552 (Dayton): 8 encounters
- Site 688 (Washington DC): 5 encounters

**Edge Cases:**
- 1 patient with 5+ admissions (frequent readmissions)
- 2 patients with same-day admit/discharge (observation stays)
- 1 patient with extended LOS (>30 days, ongoing)
- 3 admissions with missing discharge diagnosis (data quality test)

### 4.3 Field Definitions and Business Rules

| Field | Type | Nullable | Business Rule |
|-------|------|----------|---------------|
| `InpatientSID` | BIGINT | No | Surrogate primary key (auto-increment) |
| `PatientSID` | INT | No | Links to SPatient.SPatient |
| `AdmitDateTime` | DATETIME2(0) | No | Admission date/time (required) |
| `DischargeDateTime` | DATETIME2(0) | Yes | NULL = active admission, NOT NULL = discharged |
| `AdmitLocationSID` | INT | Yes | Admitting ward (links to Dim.Location) |
| `DischargeWardLocationSID` | INT | Yes | Discharge ward (may differ from admit ward) |
| `AdmittingProviderSID` | INT | Yes | Admitting physician (links to SStaff.SStaff) |
| `AdmitDiagnosisICD10` | VARCHAR(20) | Yes | ICD-10 code for admit diagnosis |
| `DischargeDiagnosisICD10` | VARCHAR(20) | Yes | ICD-10 code for discharge diagnosis (primary) |
| `DischargeDiagnosis` | VARCHAR(100) | Yes | Human-readable discharge diagnosis |
| `DischargeDisposition` | VARCHAR(50) | Yes | 'Home', 'SNF', 'Rehab', 'AMA', 'Deceased', etc. |
| `LengthOfStay` | INT | Yes | Calculated days (DischargeDate - AdmitDate); NULL if active |
| `EncounterStatus` | VARCHAR(20) | Yes | 'Active' or 'Discharged' (derived from DischargeDateTime) |
| `Sta3n` | INT | No | VA Station Number (e.g., 508, 516, 552, 688) |

**Calculations:**
- **LengthOfStay**: `DATEDIFF(day, AdmitDateTime, DischargeDateTime)` for discharged; NULL for active
- **EncounterStatus**: `'Active'` if DischargeDateTime IS NULL, else `'Discharged'`

---

## 5. ETL Pipeline

### 5.1 Bronze Layer - Raw Extraction

**Script:** `etl/bronze_inpatient.py`

**Purpose:** Extract raw data from `CDWWork.Inpat.Inpatient` with minimal transformation

**SQL Query:**
```sql
SELECT
    i.InpatientSID,
    i.PatientSID,
    i.AdmitDateTime,
    i.DischargeDateTime,
    i.AdmitLocationSID,
    i.DischargeWardLocationSID,
    i.AdmittingProviderSID,
    i.AdmitDiagnosisICD10,
    i.DischargeDiagnosisICD10,
    i.DischargeDiagnosis,
    i.DischargeDisposition,
    i.LengthOfStay,
    i.EncounterStatus,
    i.Sta3n,
    p.PatientICN,
    p.PatientName,
    al.LocationName AS AdmitWard,
    dl.LocationName AS DischargeWard,
    s.StaffName AS AttendingProvider
FROM Inpat.Inpatient i
LEFT JOIN SPatient.SPatient p ON i.PatientSID = p.PatientSID
LEFT JOIN Dim.Location al ON i.AdmitLocationSID = al.LocationSID
LEFT JOIN Dim.Location dl ON i.DischargeWardLocationSID = dl.LocationSID
LEFT JOIN SStaff.SStaff s ON i.AdmittingProviderSID = s.StaffSID
ORDER BY i.AdmitDateTime DESC;
```

**Output:** `bronze/cdwwork/inpatient` (Parquet file in MinIO)

**Partitioning:** None (single file for development; partition by Sta3n in production)

### 5.2 Silver Layer - Cleaning and Harmonization

**Script:** `etl/silver_inpatient.py`

**Transformations:**
1. **Patient Identity Resolution**: Map `PatientSID` → `PatientICN` (unified patient key)
2. **Date Standardization**: Convert DATETIME2 to ISO 8601 strings (`YYYY-MM-DD HH:MM:SS`)
3. **Status Derivation**: Set `EncounterStatus = 'Active'` if `DischargeDateTime IS NULL`, else `'Discharged'`
4. **LOS Calculation**: Compute `LengthOfStay` if missing (for historical data quality)
5. **Facility Name Enrichment**: Join `Sta3n` to facility names (via Dim.Sta3n lookup)
6. **Provider Name Normalization**: Standardize provider name format (Last, First)
7. **Null Handling**: Replace NULL diagnoses with `'Not documented'`

**Output:** `silver/inpatient` (Parquet file in MinIO)

### 5.3 Gold Layer - Patient-Centric Aggregation

**Script:** `etl/gold_inpatient.py`

**Transformations:**
1. **Patient-Centric Grouping**: Group by `PatientICN`
2. **Encounter Sorting**: Order by `AdmitDateTime DESC` (most recent first)
3. **Active Encounter Flag**: Create boolean `is_active` column
4. **Encounter Count Rollups**:
   - `total_admissions` (lifetime count)
   - `active_admissions` (current count)
   - `readmissions_30d` (readmitted within 30 days of prior discharge)
5. **Recent Encounter Summary**: Create nested struct with last 5 encounters for widget use

**Output:** `gold/inpatient` (Parquet file in MinIO)

**Schema:**
```python
{
    "patient_icn": str,
    "patient_key": int,  # Derived from ICN for DB FK
    "total_admissions": int,
    "active_admissions": int,
    "most_recent_admit_date": datetime,
    "most_recent_discharge_date": datetime,
    "encounters": [  # List of encounter dicts
        {
            "inpatient_sid": int,
            "admit_datetime": datetime,
            "discharge_datetime": datetime,
            "admit_ward": str,
            "discharge_ward": str,
            "attending_provider": str,
            "admit_diagnosis_icd10": str,
            "discharge_diagnosis_icd10": str,
            "discharge_diagnosis": str,
            "discharge_disposition": str,
            "length_of_stay": int,
            "encounter_status": str,  # 'Active' or 'Discharged'
            "facility_name": str,
            "sta3n": int
        }
    ]
}
```

---

## 6. PostgreSQL Serving Database

### 6.1 Table Schema - patient_encounters

**DDL Script:** `db/ddl/create_patient_encounters_table.sql`

```sql
-- Encounters (Inpatient Admissions) Table
-- Phase 1: Inpatient only (Outpatient encounters in Phase 2)

CREATE TABLE IF NOT EXISTS patient_encounters (
    encounter_id SERIAL PRIMARY KEY,
    patient_icn VARCHAR(20) NOT NULL,
    patient_key INTEGER NOT NULL,

    -- Core encounter identification
    inpatient_sid BIGINT NOT NULL,  -- Source system surrogate key
    encounter_type VARCHAR(20) DEFAULT 'Inpatient',  -- Future: 'Outpatient', 'ED'
    encounter_status VARCHAR(20),  -- 'Active', 'Discharged'

    -- Admission details
    admit_datetime TIMESTAMP NOT NULL,
    admit_ward VARCHAR(100),
    admit_diagnosis_icd10 VARCHAR(20),

    -- Discharge details (NULL if active admission)
    discharge_datetime TIMESTAMP,
    discharge_ward VARCHAR(100),
    discharge_diagnosis_icd10 VARCHAR(20),
    discharge_diagnosis VARCHAR(200),
    discharge_disposition VARCHAR(50),  -- 'Home', 'SNF', 'Rehab', 'AMA', 'Deceased'

    -- Calculated fields
    length_of_stay INTEGER,  -- Days; NULL if active

    -- Provider and facility
    attending_provider VARCHAR(100),
    facility_name VARCHAR(100),
    sta3n INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX idx_encounters_patient_icn ON patient_encounters(patient_icn);
CREATE INDEX idx_encounters_patient_key ON patient_encounters(patient_key);
CREATE INDEX idx_encounters_admit_date ON patient_encounters(admit_datetime DESC);
CREATE INDEX idx_encounters_status ON patient_encounters(encounter_status);
CREATE INDEX idx_encounters_active_admits
    ON patient_encounters(patient_icn, admit_datetime DESC)
    WHERE encounter_status = 'Active';

-- Foreign key (if patient_demographics table exists)
-- ALTER TABLE patient_encounters
--     ADD CONSTRAINT fk_encounters_patient
--     FOREIGN KEY (patient_key) REFERENCES patient_demographics(patient_key);
```

### 6.2 Data Loading

**Script:** `etl/load_encounters.py`

**Process:**
1. Read Gold Parquet from MinIO (`gold/inpatient`)
2. Flatten nested `encounters` list into individual rows
3. Truncate existing `patient_encounters` table (full reload for Phase 1)
4. Bulk insert via SQLAlchemy `to_sql()` or `psycopg2 COPY`
5. Verify row count and index integrity

**Expected Row Count:** 35 encounters (matches mock CDW data)

---

## 7. API Design

### 7.1 Routing Architecture - Pattern B (Dedicated Router)

**Router File:** `app/routes/encounters.py`

**Rationale for Pattern B:**
- Complex domain with full-page view
- Multiple query patterns (active vs discharged, filtering, sorting)
- Future enhancements planned (ward transfers, Vista overlay, outpatient)
- Separates concerns from `patient.py` (which is already substantial)

### 7.2 API Endpoints

#### 7.2.1 Widget Endpoint - Recent Encounters

**Endpoint:** `GET /patient/{patient_icn}/encounters/widget`

**Purpose:** Fetch 3-4 most recent encounters for dashboard widget display

**Query Parameters:** None (always returns most recent)

**SQL Query:**
```sql
SELECT
    encounter_id,
    inpatient_sid,
    encounter_status,
    admit_datetime,
    discharge_datetime,
    admit_ward,
    attending_provider,
    discharge_diagnosis,
    length_of_stay,
    facility_name,
    sta3n
FROM patient_encounters
WHERE patient_icn = :patient_icn
ORDER BY admit_datetime DESC
LIMIT 4;
```

**Response Format (JSON):**
```json
{
  "patient_icn": "1000000001V123456",
  "total_encounters": 8,
  "active_admissions": 1,
  "recent_encounters": [
    {
      "encounter_id": 42,
      "inpatient_sid": 10015,
      "encounter_status": "Active",
      "admit_datetime": "2025-12-10T14:30:00",
      "discharge_datetime": null,
      "admit_ward": "ICU-2",
      "attending_provider": "Smith, John MD",
      "discharge_diagnosis": null,
      "length_of_stay": null,
      "facility_name": "Atlanta VAMC",
      "sta3n": 508
    },
    {
      "encounter_id": 38,
      "inpatient_sid": 10012,
      "encounter_status": "Discharged",
      "admit_datetime": "2025-11-15T09:00:00",
      "discharge_datetime": "2025-11-18T16:00:00",
      "admit_ward": "Medicine-3A",
      "attending_provider": "Johnson, Mary MD",
      "discharge_diagnosis": "Pneumonia, unspecified",
      "length_of_stay": 3,
      "facility_name": "Atlanta VAMC",
      "sta3n": 508
    }
  ]
}
```

**Template:** `app/templates/widgets/encounters.html`

**HTMX Fragment:** Returns widget HTML (no full page wrapper)

#### 7.2.2 Full Page Endpoint - All Encounters

**Endpoint:** `GET /patient/{patient_icn}/encounters`

**Purpose:** Display comprehensive encounter history with filtering, sorting, and pagination

**Query Parameters:**
- `status` (optional): `'active'`, `'discharged'`, or `'all'` (default: `'all'`)
- `facility` (optional): Filter by Sta3n (e.g., `'508'`)
- `sort` (optional): `'admit_date'` (default), `'discharge_date'`, `'los'`, `'facility'`
- `order` (optional): `'desc'` (default) or `'asc'`
- `page` (optional): Page number for pagination (default: 1)
- `per_page` (optional): Encounters per page (default: 20)

**SQL Query (with filters):**
```sql
SELECT
    encounter_id,
    inpatient_sid,
    encounter_status,
    admit_datetime,
    discharge_datetime,
    admit_ward,
    discharge_ward,
    attending_provider,
    admit_diagnosis_icd10,
    discharge_diagnosis_icd10,
    discharge_diagnosis,
    discharge_disposition,
    length_of_stay,
    facility_name,
    sta3n
FROM patient_encounters
WHERE patient_icn = :patient_icn
  AND (:status = 'all' OR encounter_status = :status)
  AND (:facility IS NULL OR sta3n = :facility)
ORDER BY
    CASE WHEN :sort = 'admit_date' THEN admit_datetime END DESC,
    CASE WHEN :sort = 'discharge_date' THEN discharge_datetime END DESC,
    CASE WHEN :sort = 'los' THEN length_of_stay END DESC,
    CASE WHEN :sort = 'facility' THEN facility_name END ASC
LIMIT :per_page OFFSET :offset;
```

**Template:** `app/templates/encounters.html`

**HTMX Integration:**
- Filter dropdowns trigger `hx-get` to reload table without full page refresh
- Sort headers use `hx-get` with `hx-target="#encounters-table"`
- Pagination uses `hx-get` for seamless page navigation

### 7.3 Database Query Functions

**File:** `app/db/encounters.py`

```python
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)


def get_recent_encounters(icn: str, limit: int = 4) -> List[Dict[str, Any]]:
    """Fetch most recent encounters for widget."""
    query = text("""
        SELECT
            encounter_id,
            inpatient_sid,
            encounter_status,
            admit_datetime,
            discharge_datetime,
            admit_ward,
            attending_provider,
            discharge_diagnosis,
            length_of_stay,
            facility_name,
            sta3n
        FROM patient_encounters
        WHERE patient_icn = :icn
        ORDER BY admit_datetime DESC
        LIMIT :limit
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn, "limit": limit})
        return [dict(row._mapping) for row in result]


def get_encounter_summary(icn: str) -> Dict[str, int]:
    """Get aggregate encounter counts."""
    query = text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN encounter_status = 'Active' THEN 1 ELSE 0 END) as active
        FROM patient_encounters
        WHERE patient_icn = :icn
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn}).fetchone()
        return {"total": result.total or 0, "active": result.active or 0}


def get_all_encounters(
    icn: str,
    status: str = 'all',
    facility: Optional[int] = None,
    sort_by: str = 'admit_date',
    order: str = 'desc',
    page: int = 1,
    per_page: int = 20
) -> List[Dict[str, Any]]:
    """Fetch all encounters with filtering, sorting, pagination."""

    # Build WHERE clause
    where_clauses = ["patient_icn = :icn"]
    params = {"icn": icn, "per_page": per_page, "offset": (page - 1) * per_page}

    if status != 'all':
        where_clauses.append("encounter_status = :status")
        params["status"] = status.capitalize()

    if facility:
        where_clauses.append("sta3n = :facility")
        params["facility"] = facility

    where_sql = " AND ".join(where_clauses)

    # Build ORDER BY clause
    sort_column = {
        'admit_date': 'admit_datetime',
        'discharge_date': 'discharge_datetime',
        'los': 'length_of_stay',
        'facility': 'facility_name'
    }.get(sort_by, 'admit_datetime')

    order_sql = f"{sort_column} {'ASC' if order == 'asc' else 'DESC'}"

    query = text(f"""
        SELECT
            encounter_id,
            inpatient_sid,
            encounter_status,
            admit_datetime,
            discharge_datetime,
            admit_ward,
            discharge_ward,
            attending_provider,
            admit_diagnosis_icd10,
            discharge_diagnosis_icd10,
            discharge_diagnosis,
            discharge_disposition,
            length_of_stay,
            facility_name,
            sta3n
        FROM patient_encounters
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT :per_page OFFSET :offset
    """)

    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._mapping) for row in result]
```

---

## 8. UI Specifications

### 8.1 Dashboard Widget (1x1) - Recent Encounters

**File:** `app/templates/partials/encounters_widget.html`

**Layout:**
```
┌─────────────────────────────────────────┐
│ 🏥 Encounters                           │  (Header with icon and title only)
├─────────────────────────────────────────┤
│ 🏥 12/10/2025 - ICU-2 (Active)          │  (Most recent, highlighted if active)
│    Atlanta VAMC • Dr. Smith             │
├─────────────────────────────────────────┤
│ 11/15/2025 - 11/18/2025 (3 days)        │  (Recent discharge)
│    Medicine-3A • Dr. Johnson            │
│    Pneumonia, unspecified               │
├─────────────────────────────────────────┤
│ 09/22/2025 - 09/25/2025 (3 days)        │  (Older discharge)
│    Surgery-2B • Dr. Williams            │
│    Post-op care                         │
├─────────────────────────────────────────┤
│ ↗ View All Encounters                   │  (Bottom action link)
└─────────────────────────────────────────┘
```

**Key Elements:**
- **Header**: Title with icon only (consistent with Allergies, Medications widgets)
- **Active Indicator**: 🏥 icon or "ACTIVE" badge for current admissions
- **Date Display**:
  - Active: "12/10/2025 - [Ward]"
  - Discharged: "11/15/2025 - 11/18/2025 (3 days)"
- **Provider**: Abbreviated name (e.g., "Dr. Smith")
- **Diagnosis**: Show discharge diagnosis for discharged encounters (1 line, truncated if needed)
- **Facility**: Small text (e.g., "Atlanta VAMC")
- **Max Items**: 3-4 encounters (most recent)
- **View All Link**: Bottom of widget using `widget-action` class with external link icon

**Jinja2 Template Excerpt:**
```html
<!-- Encounters Widget Content -->
<!-- Widget Header -->
<div class="widget__header">
    <div class="widget__title-group">
        <i class="fa-solid fa-hospital widget__icon"></i>
        <h3 class="widget__title">Encounters</h3>
    </div>
    {% if active_count > 0 %}
        <span class="badge badge--warning">{{ active_count }} Active</span>
    {% endif %}
</div>

<!-- Widget Body -->
<div class="widget__body">
    <div class="widget-encounters">
        {% if error %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">
                <i class="fa-solid fa-circle-exclamation"></i> Error loading encounters
            </p>
        {% elif total_count == 0 %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">No encounters recorded</p>
        {% else %}
            <!-- Encounters List (Most Recent 3-4) -->
            <div class="encounters-list-widget">
                {% for enc in encounters %}
                <div class="encounter-item-widget {% if enc.encounter_status == 'Active' %}encounter-item-widget--active{% endif %}">
                    <div class="encounter-item-widget__date">
                        {% if enc.encounter_status == 'Active' %}
                            <i class="fa-solid fa-hospital text-warning"></i>
                            {{ enc.admit_datetime.strftime('%m/%d/%Y') }} - {{ enc.admit_ward }}
                            <span class="badge badge--warning badge--sm">ACTIVE</span>
                        {% else %}
                            {{ enc.admit_datetime.strftime('%m/%d/%Y') }} - {{ enc.discharge_datetime.strftime('%m/%d/%Y') }}
                            ({{ enc.length_of_stay }} day{{ 's' if enc.length_of_stay != 1 else '' }})
                        {% endif %}
                    </div>
                    <div class="encounter-item-widget__details">
                        {{ enc.facility_name }} • {{ enc.attending_provider }}
                    </div>
                    {% if enc.discharge_diagnosis and enc.encounter_status == 'Discharged' %}
                        <div class="encounter-item-widget__diagnosis">{{ enc.discharge_diagnosis }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>

            <!-- View All Link -->
            <div class="widget-action">
                <a href="/patient/{{ patient_icn }}/encounters" class="btn btn--link btn--sm">
                    <i class="fa-regular fa-arrow-up-right-from-square"></i>
                    View All Encounters
                </a>
            </div>
        {% endif %}
    </div>
</div>

<!-- Widget Footer (minimal spacing) -->
<div class="widget__footer"></div>
```

### 8.2 Full Page View - Encounters List

**File:** `app/templates/patient_encounters.html`

**Layout:**
```
┌───────────────────────────────────────────────────────────────┐
│ Patient: [Name] ([ICN])                                        │
│ Encounters - Inpatient Admissions                             │
├───────────────────────────────────────────────────────────────┤
│ Filters:  [Status: All ▼] [Facility: All ▼]   [Apply]        │
├───────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Admit Date ▼ | Discharge Date | Ward | Provider | LOS  │  │  (Table headers - sortable)
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 12/10/2025   | ACTIVE         | ICU-2 | Dr. Smith | -   │  │  (Active admission - highlighted)
│ │ Atlanta VAMC (508)                                       │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 11/15/2025   | 11/18/2025     | Med-3A | Dr. Johnson| 3 │  │  (Discharged)
│ │ Atlanta VAMC (508)                                       │  │
│ │ Discharge Diagnosis: Pneumonia, unspecified             │  │
│ │ Disposition: Home                                        │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ ...                                                      │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ [<< Prev]  Page 1 of 3  [Next >>]                            │  (Pagination)
└───────────────────────────────────────────────────────────────┘
```

**Features:**
1. **Filters**:
   - Status dropdown: All, Active, Discharged
   - Facility dropdown: All, Atlanta VAMC (508), Bay Pines (516), etc.
   - HTMX: `hx-get="/patient/{icn}/encounters?status=active" hx-target="#encounters-table"`

2. **Sortable Columns**:
   - Admit Date (default: descending)
   - Discharge Date
   - Length of Stay
   - Facility
   - HTMX: Click header to toggle sort order

3. **Row Details**:
   - **Line 1**: Dates, Ward, Provider, LOS
   - **Line 2**: Facility name and Sta3n
   - **Line 3** (if discharged): Discharge diagnosis and disposition

4. **Active Admission Highlighting**:
   - Background color: Light blue (#E3F2FD)
   - Bold "ACTIVE" text in Discharge Date column

5. **Pagination**:
   - 20 encounters per page (configurable)
   - HTMX: `hx-get="/patient/{icn}/encounters?page=2"`

**Jinja2 Template Excerpt:**
```html
{% extends "base.html" %}

{% block content %}
<div class="page-header">
  <h1>Encounters - Inpatient Admissions</h1>
  <p>Patient: {{ patient_name }} ({{ patient_icn }})</p>
</div>

<div class="filters">
  <label>Status:
    <select name="status" hx-get="/patient/{{ patient_icn }}/encounters" hx-target="#encounters-table" hx-include="[name='facility']">
      <option value="all" {% if status == 'all' %}selected{% endif %}>All</option>
      <option value="active" {% if status == 'active' %}selected{% endif %}>Active</option>
      <option value="discharged" {% if status == 'discharged' %}selected{% endif %}>Discharged</option>
    </select>
  </label>

  <label>Facility:
    <select name="facility" hx-get="/patient/{{ patient_icn }}/encounters" hx-target="#encounters-table" hx-include="[name='status']">
      <option value="">All</option>
      {% for fac in facilities %}
        <option value="{{ fac.sta3n }}" {% if facility == fac.sta3n|string %}selected{% endif %}>
          {{ fac.name }} ({{ fac.sta3n }})
        </option>
      {% endfor %}
    </select>
  </label>
</div>

<div id="encounters-table">
  <table class="encounters-table">
    <thead>
      <tr>
        <th><a href="#" hx-get="/patient/{{ patient_icn }}/encounters?sort=admit_date&order={{ 'asc' if order == 'desc' else 'desc' }}" hx-target="#encounters-table">Admit Date</a></th>
        <th>Discharge Date</th>
        <th>Ward</th>
        <th>Provider</th>
        <th>LOS</th>
      </tr>
    </thead>
    <tbody>
      {% for enc in encounters %}
        <tr class="{% if enc.encounter_status == 'Active' %}active-encounter{% endif %}">
          <td>{{ enc.admit_datetime.strftime('%m/%d/%Y') }}</td>
          <td>
            {% if enc.encounter_status == 'Active' %}
              <strong>ACTIVE</strong>
            {% else %}
              {{ enc.discharge_datetime.strftime('%m/%d/%Y') }}
            {% endif %}
          </td>
          <td>{{ enc.admit_ward }}</td>
          <td>{{ enc.attending_provider }}</td>
          <td>{{ enc.length_of_stay if enc.length_of_stay else '-' }}</td>
        </tr>
        <tr class="encounter-details">
          <td colspan="5">
            <strong>Facility:</strong> {{ enc.facility_name }} ({{ enc.sta3n }})
            {% if enc.discharge_diagnosis %}
              <br><strong>Discharge Diagnosis:</strong> {{ enc.discharge_diagnosis }}
              <br><strong>Disposition:</strong> {{ enc.discharge_disposition }}
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>

  <!-- Pagination -->
  <div class="pagination">
    {% if page > 1 %}
      <a href="#" hx-get="/patient/{{ patient_icn }}/encounters?page={{ page - 1 }}" hx-target="#encounters-table">&lt;&lt; Prev</a>
    {% endif %}
    <span>Page {{ page }} of {{ total_pages }}</span>
    {% if page < total_pages %}
      <a href="#" hx-get="/patient/{{ patient_icn }}/encounters?page={{ page + 1 }}" hx-target="#encounters-table">Next &gt;&gt;</a>
    {% endif %}
  </div>
</div>
{% endblock %}
```

### 8.3 CSS Styling

**File:** `app/static/styles.css` (add to existing CSS file)

```css
/* Encounters Widget */
.encounters-widget .encounter-item {
    border-left: 3px solid #ccc;
    padding: 8px 12px;
    margin-bottom: 10px;
}

.encounters-widget .encounter-item.active {
    border-left-color: #1976D2;
    background-color: #E3F2FD;
}

.encounters-widget .badge-active {
    background-color: #1976D2;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: bold;
}

.encounters-widget .encounter-date {
    font-weight: 600;
    margin-bottom: 4px;
}

.encounters-widget .encounter-details {
    font-size: 0.9rem;
    color: #555;
}

.encounters-widget .encounter-diagnosis {
    font-size: 0.85rem;
    color: #666;
    font-style: italic;
    margin-top: 4px;
}

/* Full Page Encounters Table */
.encounters-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.encounters-table th {
    background-color: #f5f5f5;
    padding: 12px;
    text-align: left;
    border-bottom: 2px solid #ddd;
}

.encounters-table th a {
    color: #1976D2;
    text-decoration: none;
}

.encounters-table th a:hover {
    text-decoration: underline;
}

.encounters-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #eee;
}

.encounters-table tr.active-encounter {
    background-color: #E3F2FD;
}

.encounters-table tr.encounter-details td {
    font-size: 0.9rem;
    color: #666;
    padding-top: 0;
    padding-bottom: 12px;
}

/* Filters */
.filters {
    margin: 20px 0;
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 4px;
}

.filters label {
    margin-right: 20px;
}

.filters select {
    padding: 5px 10px;
    margin-left: 8px;
}

/* Pagination */
.pagination {
    margin-top: 20px;
    text-align: center;
}

.pagination a {
    margin: 0 10px;
    color: #1976D2;
    text-decoration: none;
}

.pagination a:hover {
    text-decoration: underline;
}
```

---

## 9. Implementation Roadmap

### Day 1: Schema Modifications and Test Data

**Tasks:**
1. ✅ Review existing `Inpat.Inpatient` table structure
2. Update `mock/sql-server/cdwwork/create/Inpat.Inpatient.sql` with complete table definition (including 9 new fields)
3. Generate 35 test encounters:
   - Update existing 15 records with discharge data
   - Create 20 new records (5 active, 15 discharged)
4. Update `mock/sql-server/cdwwork/insert/Inpat.Inpatient.sql` with all 35 encounters
5. Apply schema changes to running SQL Server container (drop and recreate table)
6. Verify data with SQL queries

**Deliverables:**
- [ ] Updated `mock/sql-server/cdwwork/create/Inpat.Inpatient.sql` (complete CREATE TABLE with all fields)
- [ ] Updated `mock/sql-server/cdwwork/insert/Inpat.Inpatient.sql` (35 encounters with discharge data)
- [ ] SQL verification queries document

**Time Estimate:** 3-4 hours

---

### Day 2: Bronze and Silver ETL

**Tasks:**
1. Create `etl/bronze_inpatient.py`:
   - SQL query to extract from `Inpat.Inpatient` with JOINs
   - Write to MinIO `bronze/cdwwork/inpatient`
2. Create `etl/silver_inpatient.py`:
   - Patient identity resolution (PatientSID → PatientICN)
   - Date standardization
   - Status derivation (Active vs Discharged)
   - LOS calculation validation
   - Write to MinIO `silver/inpatient`
3. Test Bronze and Silver scripts
4. Verify Parquet file schemas with Polars

**Deliverables:**
- [ ] `etl/bronze_inpatient.py`
- [ ] `etl/silver_inpatient.py`
- [ ] Bronze Parquet file in MinIO: `bronze/cdwwork/inpatient`
- [ ] Silver Parquet file in MinIO: `silver/inpatient`

**Time Estimate:** 4-5 hours

---

### Day 3: Gold ETL and PostgreSQL Schema

**Tasks:**
1. Create `etl/gold_inpatient.py`:
   - Patient-centric grouping by ICN
   - Encounter sorting (most recent first)
   - Aggregate counts (total admissions, active admissions)
   - Write to MinIO `gold/inpatient`
2. Create `db/ddl/create_patient_encounters_table.sql`:
   - Table schema with indexes
   - Apply to PostgreSQL container
3. Create `etl/load_encounters.py`:
   - Read Gold Parquet
   - Flatten nested encounters
   - Bulk load to PostgreSQL
4. Test full ETL pipeline end-to-end
5. Verify PostgreSQL data with SQL queries

**Deliverables:**
- [ ] `etl/gold_inpatient.py`
- [ ] `db/ddl/create_patient_encounters_table.sql`
- [ ] `etl/load_encounters.py`
- [ ] Gold Parquet file in MinIO: `gold/inpatient`
- [ ] PostgreSQL table populated (35 rows)

**Time Estimate:** 4-5 hours

---

### Day 4: API Routes and Database Queries

**Tasks:**
1. Create `app/db/encounters.py`:
   - `get_recent_encounters()` (widget)
   - `get_encounter_summary()` (counts)
   - `get_all_encounters()` (full page with filters)
2. Create `app/routes/encounters.py`:
   - `GET /patient/{icn}/encounters/widget` (widget endpoint)
   - `GET /patient/{icn}/encounters` (full page endpoint)
3. Register router in `app/main.py`
4. Test endpoints with curl/Postman

**Deliverables:**
- [ ] `app/db/encounters.py`
- [ ] `app/routes/encounters.py`
- [ ] Router registered in `app/main.py`
- [ ] API endpoint tests (manual or automated)

**Time Estimate:** 4-5 hours

---

### Day 5: Widget UI Implementation

**Tasks:**
1. Create `app/templates/partials/encounters_widget.html`:
   - Recent encounters list (3-4 items)
   - Active admission highlighting
   - "View All" link
2. Update `app/static/styles.css` (add widget styles)
3. Update `app/templates/dashboard.html` to include encounters widget
4. Test widget rendering with multiple patients:
   - Patient with active admission
   - Patient with only discharged encounters
   - Patient with no encounters
5. Verify HTMX behavior and responsive design

**Deliverables:**
- [ ] `app/templates/partials/encounters_widget.html`
- [ ] Updated `app/static/styles.css` (widget section)
- [ ] Updated `app/templates/dashboard.html`
- [ ] Widget screenshots for documentation

**Time Estimate:** 3-4 hours

---

### Day 6: Full Page UI Implementation

**Tasks:**
1. Create `app/templates/patient_encounters.html`:
   - Full encounters table with sortable columns
   - Filter dropdowns (status, facility)
   - Pagination controls
2. Update `app/static/styles.css` (add full page styles)
3. Test HTMX interactions:
   - Filter changes (status, facility)
   - Column sorting (admit date, discharge date, LOS)
   - Pagination (prev/next)
4. Test with edge cases:
   - Patient with 1 encounter (no pagination)
   - Patient with 50+ encounters (multi-page)
   - Filter combinations (active only, specific facility)
5. Accessibility review (keyboard navigation, screen reader compatibility)

**Deliverables:**
- [ ] `app/templates/patient_encounters.html`
- [ ] Updated `app/static/styles.css`
- [ ] HTMX functionality verified
- [ ] Accessibility audit checklist

**Time Estimate:** 4-5 hours

---

### Day 7: Testing, Polish, and Documentation

**Tasks:**
1. Write unit tests (`tests/test_encounters.py`):
   - Database query functions
   - ETL transformations (Bronze, Silver, Gold)
2. Write integration tests:
   - API endpoint responses
   - Widget rendering
   - Full page rendering
3. Manual testing checklist:
   - All 36 test patients
   - Active vs discharged encounters
   - Sorting and filtering
   - Pagination
   - Mobile/tablet responsive design
4. Update documentation:
   - `app/README.md` (add Encounters routing example)
   - `docs/spec/med-z1-architecture.md` (confirm Pattern B decision)
   - This design document (mark sections complete)
5. Code review and cleanup

**Deliverables:**
- [ ] `tests/test_encounters.py` (unit and integration tests)
- [ ] Manual testing checklist (completed)
- [ ] Updated documentation
- [ ] Code review notes

**Time Estimate:** 5-6 hours

---

**Total Estimated Time:** 27-34 hours (approximately 1 week of full-time work, or 1.5-2 weeks with other responsibilities)

---

## 10. Testing Strategy

### 10.1 Unit Tests

**File:** `tests/test_encounters.py`

**Coverage Areas:**
1. **Database Query Functions** (`app/db/encounters.py`):
   - `test_get_recent_encounters_returns_correct_limit()`
   - `test_get_recent_encounters_sorted_by_admit_date()`
   - `test_get_encounter_summary_counts_active_correctly()`
   - `test_get_all_encounters_filters_by_status()`
   - `test_get_all_encounters_filters_by_facility()`
   - `test_get_all_encounters_sorts_correctly()`
   - `test_get_all_encounters_pagination()`

2. **ETL Transformations**:
   - `test_bronze_extraction_row_count()`
   - `test_silver_status_derivation()` (Active vs Discharged)
   - `test_silver_los_calculation()`
   - `test_gold_patient_grouping()`
   - `test_gold_encounter_sorting()`

**Example Test:**
```python
import pytest
from app.db.encounters import get_recent_encounters

def test_get_recent_encounters_returns_correct_limit(test_db_session):
    """Verify that get_recent_encounters respects limit parameter."""
    patient_icn = "1000000001V123456"

    # Fetch with limit=4
    encounters = get_recent_encounters(test_db_session, patient_icn, limit=4)

    assert len(encounters) == 4, "Should return exactly 4 encounters"

    # Verify descending order by admit date
    admit_dates = [enc.admit_datetime for enc in encounters]
    assert admit_dates == sorted(admit_dates, reverse=True), "Should be sorted by admit date descending"
```

### 10.2 Integration Tests

**Coverage Areas:**
1. **API Endpoints**:
   - `test_widget_endpoint_returns_json()`
   - `test_widget_endpoint_unauthorized_patient()` (if auth implemented)
   - `test_full_page_endpoint_renders_html()`
   - `test_full_page_filtering_by_status()`
   - `test_full_page_sorting_by_admit_date()`

2. **UI Rendering**:
   - `test_widget_html_contains_recent_encounters()`
   - `test_full_page_active_encounter_highlighted()`
   - `test_pagination_links_present()`

**Example Test:**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_widget_endpoint_returns_json():
    """Verify widget endpoint returns valid JSON."""
    patient_icn = "1000000001V123456"
    response = client.get(f"/patient/{patient_icn}/encounters/widget")

    assert response.status_code == 200
    data = response.json()
    assert "patient_icn" in data
    assert "recent_encounters" in data
    assert len(data["recent_encounters"]) <= 4
```

### 10.3 Manual Testing Checklist

**Pre-Deployment Checklist:**

- [ ] **Widget Display**:
  - [ ] Displays 3-4 recent encounters on dashboard
  - [ ] Active admissions highlighted with badge/icon
  - [ ] "View All" link navigates to full page
  - [ ] Shows "No encounters found" for patients with no admissions

- [ ] **Full Page View**:
  - [ ] All encounters displayed correctly
  - [ ] Active encounters highlighted (blue background)
  - [ ] Discharge diagnosis and disposition shown for discharged encounters
  - [ ] Length of stay calculated correctly

- [ ] **Filtering**:
  - [ ] Status filter: "All", "Active", "Discharged" work correctly
  - [ ] Facility filter: Shows only encounters from selected facility
  - [ ] Filter combinations work (e.g., "Active" + "Atlanta VAMC")

- [ ] **Sorting**:
  - [ ] Admit date sorting (asc/desc)
  - [ ] Discharge date sorting (asc/desc)
  - [ ] Length of stay sorting (asc/desc)
  - [ ] Facility sorting (alphabetical)

- [ ] **Pagination**:
  - [ ] Pages show 20 encounters each (configurable)
  - [ ] "Next" and "Prev" buttons work correctly
  - [ ] No pagination shown for patients with ≤20 encounters

- [ ] **Data Accuracy**:
  - [ ] All 35 test encounters display correctly
  - [ ] Active encounters show correct admit date (no discharge date)
  - [ ] Discharged encounters show correct admit and discharge dates
  - [ ] Provider names display correctly
  - [ ] Facility names and Sta3n values match

- [ ] **HTMX Functionality**:
  - [ ] Filter changes reload table without full page refresh
  - [ ] Sorting changes reload table without full page refresh
  - [ ] Pagination loads new page without full page refresh

- [ ] **Responsive Design**:
  - [ ] Widget readable on mobile (320px width)
  - [ ] Full page table scrolls horizontally on small screens
  - [ ] Touch-friendly controls on tablet/mobile

- [ ] **Accessibility**:
  - [ ] Keyboard navigation works (tab through filters, links)
  - [ ] Active admission status announced by screen readers
  - [ ] Color contrast meets WCAG AA standards
  - [ ] Table headers properly associated with cells

### 10.4 Test Data Coverage

**Patient Scenarios to Test:**

1. **Patient with active admission** (PatientICN: `1000000001V123456`):
   - Verify "ACTIVE" badge shows in widget
   - Verify blue highlighting on full page
   - Verify length of stay is NULL or calculated from current date

2. **Patient with multiple discharged encounters** (PatientICN: `1000000002V234567`):
   - Verify widget shows 4 most recent
   - Verify full page shows all encounters
   - Verify discharge diagnoses display

3. **Patient with no encounters** (PatientICN: `1000000036V999999`):
   - Verify widget shows "No encounters found"
   - Verify full page shows empty state message

4. **Patient with 20+ encounters** (PatientICN: `1000000005V567890`):
   - Verify pagination appears
   - Verify pagination controls work
   - Verify sorting works across pages

5. **Patient with same-day admit/discharge** (PatientICN: `1000000010V111111`):
   - Verify LOS = 0 or 1 (business rule dependent)
   - Verify dates display correctly

---

## 11. Future Enhancements

### 11.1 Phase 2: Outpatient Encounters

**Scope:**
- Clinic visits and appointments (VistA File #9000010)
- Outpatient procedures
- Emergency department visits

**Data Source:**
- CDWWork schema: `Outpat` (new schema to create)
- Primary table: `Outpat.Visit`

**UI Changes:**
- Separate tab or toggle on full page: "Inpatient | Outpatient"
- Widget: Show mix of recent inpatient and outpatient (combined or separate widget?)
- Filters: Add "Encounter Type" dropdown (Inpatient, Outpatient, All)

**Design Decision Needed:**
- **Option A**: Extend this design document with "Phase 2: Outpatient" section
- **Option B**: Create separate `outpatient-encounters-design.md`
- **Recommendation**: Option A (single document) for logical grouping

**Estimated Effort:** 5-7 days (similar to Phase 1)

### 11.2 Ward Transfer History

**Scope:**
- Display ward-to-ward transfers during a single admission
- Shows movement timeline (e.g., ED → ICU → Ward 3A → Discharge)

**Data Source:**
- CDWWork schema: `Inpat` (additional table)
- Potential table: `Inpat.WardMovement` or `Inpat.CensusHistory`

**UI Changes:**
- Expandable row on full page table
- Timeline view showing transfer sequence

**Estimated Effort:** 3-4 days (incremental enhancement)

### 11.3 Real-Time Vista Overlay (T-0 Data)

**Scope:**
- Fetch today's encounters from Vista RPC Broker (not yet in CDW)
- Merge with historical PostgreSQL data
- User-controlled "Refresh from VistA" button

**Implementation:**
- Leverage existing Vista RPC Broker infrastructure
- Create RPC call: `ORQQVI VITALS` equivalent for encounters
- Client-side merge logic (Gold layer + Vista)

**UI Changes:**
- "Refresh from VistA" button on widget and full page
- Visual indicator for Vista-sourced data (e.g., "Updated just now")

**Estimated Effort:** 4-5 days (depends on Vista RPC availability)

### 11.4 Encounter Details Modal

**Scope:**
- Click encounter row to open modal with full details:
  - All diagnosis codes (primary + secondary)
  - All providers (admitting, attending, consulting)
  - Procedure codes performed during stay
  - Linked clinical notes and lab results

**Implementation:**
- HTMX modal trigger
- Additional database queries to fetch related data

**Estimated Effort:** 2-3 days

### 11.5 Readmission Risk Indicator

**Scope:**
- Calculate and display readmission risk (e.g., "Readmitted within 30 days")
- Flag for quality improvement review

**Implementation:**
- ETL: Calculate `readmission_30d` boolean in Gold layer
- UI: Display icon/badge in widget and full page

**Estimated Effort:** 1-2 days

---

## Appendix A: Sample Test Data

### A.1 Sample Encounters (Partial List)

| InpatientSID | PatientSID | AdmitDateTime | DischargeDateTime | AdmitWard | Provider | Diagnosis | LOS | Status | Sta3n |
|--------------|------------|---------------|-------------------|-----------|----------|-----------|-----|--------|-------|
| 10001 | 1001 | 2025-12-10 14:30 | NULL | ICU-2 | Smith, John MD | NULL | NULL | Active | 508 |
| 10002 | 1002 | 2025-11-15 09:00 | 2025-11-18 16:00 | Med-3A | Johnson, Mary MD | Pneumonia, unspecified | 3 | Discharged | 508 |
| 10003 | 1003 | 2025-09-22 08:00 | 2025-09-25 10:00 | Surg-2B | Williams, David MD | Post-op care | 3 | Discharged | 516 |
| 10004 | 1001 | 2025-08-10 13:00 | 2025-08-15 11:00 | Med-4C | Brown, Lisa MD | CHF exacerbation | 5 | Discharged | 508 |
| 10005 | 1005 | 2025-12-12 06:00 | NULL | ICU-1 | Davis, Robert MD | NULL | NULL | Active | 552 |

*(See full dataset in `mock/sql-server/cdwwork/insert/Inpat.Inpatient.sql` after Day 1 completion)*

---

## Appendix B: SQL Queries for Verification

### B.1 Check Active Admissions

```sql
SELECT
    i.InpatientSID,
    p.PatientICN,
    p.PatientName,
    i.AdmitDateTime,
    l.LocationName AS AdmitWard,
    s.StaffName AS AttendingProvider,
    i.Sta3n
FROM Inpat.Inpatient i
LEFT JOIN SPatient.SPatient p ON i.PatientSID = p.PatientSID
LEFT JOIN Dim.Location l ON i.AdmitLocationSID = l.LocationSID
LEFT JOIN SStaff.SStaff s ON i.AdmittingProviderSID = s.StaffSID
WHERE i.DischargeDateTime IS NULL
ORDER BY i.AdmitDateTime DESC;
```

### B.2 Check Encounter Count by Facility

```sql
SELECT
    i.Sta3n,
    COUNT(*) AS TotalEncounters,
    SUM(CASE WHEN i.DischargeDateTime IS NULL THEN 1 ELSE 0 END) AS ActiveAdmissions,
    SUM(CASE WHEN i.DischargeDateTime IS NOT NULL THEN 1 ELSE 0 END) AS DischargedAdmissions
FROM Inpat.Inpatient i
GROUP BY i.Sta3n
ORDER BY i.Sta3n;
```

### B.3 Check Patient with Most Encounters

```sql
SELECT TOP 1
    p.PatientICN,
    p.PatientName,
    COUNT(*) AS EncounterCount
FROM Inpat.Inpatient i
LEFT JOIN SPatient.SPatient p ON i.PatientSID = p.PatientSID
GROUP BY p.PatientICN, p.PatientName
ORDER BY EncounterCount DESC;
```

---

**END OF DESIGN DOCUMENT**

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2025-12-15 | Claude Code | Initial design document for Encounters (Inpatient) Phase 1 |
| v1.1 | 2025-12-15 | Claude Code | ✅ **Implementation complete**. Updated status to reflect all 6 days completed, including ETL pipeline, widget, full page with pagination (ADR-005), patient ICN fix, Home + O₂ badge, and breadcrumb consistency |
