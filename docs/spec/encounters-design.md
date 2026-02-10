# Encounters Domain - Design Specification

**Document Version:** v2.1 (Phase 2 Complete - CDWWork2 Integration)
**Last Updated:** February 10, 2026
**Implementation Status:**
- ✅ **Phase 1 COMPLETE** - CDWWork Inpatient Admissions (December 15, 2025)
- ✅ **Phase 2 COMPLETE** - CDWWork2 Dual-Source Integration (February 10, 2026)
**Current Scope:**
- Phase 1: Inpatient Admissions from CDWWork (VistA sites) - 118 encounters
- Phase 2: Dual-source integration with CDWWork2 (Cerner sites) - 28 additional encounters
- **Total Dataset:** 146 encounters (118 CDWWork + 28 CDWWork2)
**Future Scope:** Outpatient Encounters (Phase 3)

---

## Implementation Summary

**Status:** ✅ Phase 1 & Phase 2 fully implemented and tested
**Phase 1 Implementation Date:** December 15, 2025 (6-day roadmap completed)
**Phase 2 Implementation Date:** February 10, 2026 (5-day roadmap completed)
**Total Dataset:** 146 encounters across 41 patients (118 CDWWork + 28 CDWWork2)
**First Domain to Implement:** Pagination (ADR-005) and Dual-Source Integration

**Phase 1 Key Achievements (December 2025):**
- ✅ Complete ETL pipeline (Bronze → Silver → Gold → PostgreSQL)
- ✅ Dashboard widget (1x1) showing recent encounters
- ✅ Full page with table, filtering, and pagination
- ✅ 73 test encounters with realistic distribution
- ✅ Pagination tested with patients having 30 and 15 encounters
- ✅ Patient ICN mapping fixed (ICN100001 format)
- ✅ "Home + O₂" disposition badge added (teal styling)
- ✅ Breadcrumb consistency established across all domain pages

**Phase 2 Key Achievements (February 2026):**
- ✅ Dual-source ETL pipeline supporting CDWWork (VistA) + CDWWork2 (Cerner)
- ✅ Bronze extraction from CDWWork2 EncMill.Encounter (28 encounters)
- ✅ Silver layer refactored for schema harmonization (21-column unified schema)
- ✅ Gold layer with `data_source` and `encounter_type` tracking
- ✅ PostgreSQL schema updated with `data_source` and `encounter_type` columns
- ✅ Query layer updated to return data provenance fields
- ✅ UI data source badges (Cerner/VistA) added to widget and full page
- ✅ Thompson family patients (Bailey, Alananah, Joe) demonstrate dual-source integration
- ✅ Support for INPATIENT and OUTPATIENT encounter types (CDWWork2)
- ✅ Integration tests verified for all Thompson patients (53 total encounters)

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
10. [Phase 2: CDWWork2 Integration](#10-phase-2-cdwwork2-integration)
11. [Testing Strategy](#11-testing-strategy)
12. [Future Enhancements](#12-future-enhancements)

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

## 10. Phase 2: CDWWork2 Integration ✅ **COMPLETE** (February 10, 2026)

### 10.1 Overview and Objectives

**Phase 2 Goal**: Enhance the Encounters domain to process and display encounter data from both CDWWork (VistA sites) and CDWWork2 (Cerner/Oracle Health sites) as a unified dataset.

**Implementation Status**: ✅ Completed February 10, 2026
**Total Duration**: 5 days (Bronze → Silver → Gold → PostgreSQL → Query Layer → UI)
**Total Records**: 146 encounters (118 CDWWork + 28 CDWWork2)
**Test Patients**: Thompson siblings (ICN200001-200003) - 53 encounters across 3 patients

**Key Objectives**:
1. **Bronze Layer Extraction**: Create Bronze ETL extraction for CDWWork2 `EncMill.Encounter` table
2. **Silver Layer Harmonization**: Merge CDWWork `Inpat.Inpatient` and CDWWork2 `EncMill.Encounter` into common schema
3. **Schema Alignment**: Map divergent field structures to unified Silver schema
4. **Data Source Tracking**: Add `data_source` column throughout pipeline (Silver → Gold → PostgreSQL)
5. **UI Transparency**: Display encounter source (VistA vs Cerner) in user interface
6. **Test Coverage**: Validate dual-source workflow with Thompson patients (ICN200001-200003)

**Business Value**:
- **Complete Patient View**: Veterans treated at both VistA and Cerner sites see all encounters in one place
- **Site Migration Support**: Handle patients who transition between EHR systems (e.g., Bay Pines VistA → Walla Walla Cerner)
- **Production Readiness**: Prepare med-z1 for real-world VA environment with mixed EHR sites

### 10.2 Source System Comparison

#### 10.2.1 CDWWork (VistA) - Inpatient Only

**Table**: `CDWWork.Inpat.Inpatient`
**VistA Source**: Patient Treatment File (PTF) #45
**Scope**: Inpatient admissions only (no outpatient visits)

**Key Characteristics**:
- **Patient-centric model**: Linked directly to `SPatient.SPatient` via `PatientSID`
- **Inpatient-only**: Only hospital admissions, not clinic visits
- **Surrogate Key**: `InpatientSID` (BIGINT IDENTITY)
- **Identity Field**: `PatientSID` (requires ICN lookup for cross-system join)

**Schema (19 columns)**:
```sql
CREATE TABLE [Inpat].[Inpatient] (
    -- Primary key
    [InpatientSID] BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Patient reference (requires ICN lookup)
    [PatientSID] INT NOT NULL,

    -- Admission details
    [AdmitDateTime] DATETIME2(0) NOT NULL,
    [AdmitLocationSID] INT NULL,           -- FK to Dim.Location
    [AdmittingProviderSID] INT NULL,       -- FK to SStaff.SStaff
    [AdmitDiagnosisICD10] VARCHAR(20) NULL,

    -- Discharge details (NULL = active admission)
    [DischargeDateTime] DATETIME2(0) NULL,
    [DischargeDateSID] INT NULL,
    [DischargeWardLocationSID] INT NULL,   -- FK to Dim.Location
    [DischargeDiagnosisICD10] VARCHAR(20) NULL,
    [DischargeDiagnosis] VARCHAR(100) NULL,
    [DischargeDisposition] VARCHAR(50) NULL,

    -- Calculated fields
    [LengthOfStay] INT NULL,
    [EncounterStatus] VARCHAR(20) NULL,    -- 'Active' or 'Discharged'

    -- Facility
    [Sta3n] INT NOT NULL
);
```

**Encounter Types**: Inpatient only (no type field needed)

#### 10.2.2 CDWWork2 (Cerner) - Multi-Type Encounters

**Table**: `CDWWork2.EncMill.Encounter`
**Cerner Source**: Cerner Millennium Encounter table
**Scope**: All encounter types (Inpatient, Outpatient, Emergency)

**Key Characteristics**:
- **Encounter-centric model**: Central table for all clinical data linkage
- **Multi-type encounters**: INPATIENT, OUTPATIENT, EMERGENCY
- **Surrogate Key**: `EncounterSID` (BIGINT IDENTITY)
- **Identity Field**: `PatientICN` (direct, no lookup needed)
- **Denormalized**: Includes provider/location names (not just SIDs)

**Schema (15 columns)**:
```sql
CREATE TABLE EncMill.Encounter (
    -- Primary key
    EncounterSID BIGINT PRIMARY KEY IDENTITY(1,1),

    -- Patient reference (direct ICN)
    PersonSID BIGINT NOT NULL,             -- FK to VeteranMill.SPerson
    PatientICN VARCHAR(50) NOT NULL,       -- Direct ICN (no lookup needed!)

    -- Facility
    Sta3n VARCHAR(10) NOT NULL,            -- Note: VARCHAR vs INT in CDWWork
    FacilityName VARCHAR(200) NULL,        -- Denormalized

    -- Encounter classification
    EncounterType VARCHAR(50) NOT NULL,    -- 'INPATIENT', 'OUTPATIENT', 'EMERGENCY'

    -- Timing (three date fields)
    EncounterDate DATETIME NOT NULL,       -- Primary encounter date
    AdmitDate DATETIME NULL,               -- For inpatient encounters
    DischargeDate DATETIME NULL,           -- For discharged inpatients

    -- Location (denormalized names, no SIDs)
    LocationName VARCHAR(200) NULL,
    LocationType VARCHAR(50) NULL,         -- 'CLINIC', 'WARD', 'ED'

    -- Provider (denormalized, no SID required)
    ProviderName VARCHAR(200) NULL,
    ProviderSID BIGINT NULL,               -- Optional FK

    -- Metadata
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE()
);
```

**Encounter Types**: INPATIENT, OUTPATIENT, EMERGENCY (explicit field)

#### 10.2.3 Schema Differences - Field Mapping

| Concept | CDWWork (Inpat.Inpatient) | CDWWork2 (EncMill.Encounter) | Harmonization Strategy |
|---------|---------------------------|------------------------------|------------------------|
| **Primary Key** | `InpatientSID` | `EncounterSID` | Map both to `encounter_record_id` in Silver |
| **Patient Identity** | `PatientSID` (INT, requires JOIN to get ICN) | `PatientICN` (VARCHAR, direct) | CDWWork: JOIN `SPatient.SPatient` to resolve ICN |
| **Encounter Type** | Implicit "INPATIENT" (no field) | `EncounterType` (INPATIENT/OUTPATIENT/EMERGENCY) | CDWWork: Add literal "INPATIENT" |
| **Primary Date** | `AdmitDateTime` (admission date) | `EncounterDate` (primary date), `AdmitDate` (admission) | CDWWork: Use `AdmitDateTime` for both<br>CDWWork2: Use `EncounterDate` as primary, `AdmitDate` if available |
| **Discharge Date** | `DischargeDateTime` | `DischargeDate` | Direct mapping (both nullable) |
| **Location Fields** | `AdmitLocationSID` (FK), `DischargeWardLocationSID` (FK) | `LocationName` (VARCHAR), `LocationType` (VARCHAR) | CDWWork: JOIN `Dim.Location` to resolve names<br>CDWWork2: Use direct values |
| **Provider Fields** | `AdmittingProviderSID` (FK) | `ProviderName` (VARCHAR), `ProviderSID` (optional) | CDWWork: JOIN `SStaff.SStaff` to resolve name<br>CDWWork2: Use `ProviderName` directly |
| **Diagnosis** | `AdmitDiagnosisICD10`, `DischargeDiagnosisICD10`, `DischargeDiagnosis` | Not in Encounter table (in separate tables) | CDWWork: Include diagnosis fields<br>CDWWork2: Leave NULL (Phase 2), add later |
| **Disposition** | `DischargeDisposition` | Not in Encounter table | CDWWork: Include<br>CDWWork2: Leave NULL |
| **Length of Stay** | `LengthOfStay` (INT, pre-calculated) | Not in Encounter table | Calculate in Silver for both: `DischargeDate - AdmitDate` |
| **Encounter Status** | `EncounterStatus` ('Active'/'Discharged') | Derived from `DischargeDate` | Derive in Silver: NULL discharge date → 'Active' |
| **Facility** | `Sta3n` (INT) | `Sta3n` (VARCHAR), `FacilityName` (denormalized) | Cast CDWWork2 Sta3n to INT, add facility name lookup |
| **Data Source** | N/A (implicit CDWWork) | N/A (implicit CDWWork2) | Add `data_source` column in Silver: 'CDWWork' or 'CDWWork2' |

**Key Insight**: CDWWork2 is **more denormalized** (includes names directly), while CDWWork requires **more JOINs** to resolve SIDs.

### 10.3 Common Silver Schema Definition

To harmonize CDWorkWork and CDWWork2 encounters, we define a **unified Silver schema** with these columns:

**Silver Schema: `silver/encounters/encounters_merged.parquet`**

| Column Name | Type | Source | Description |
|-------------|------|--------|-------------|
| `patient_icn` | VARCHAR | Both | Harmonized patient identifier (ICN format) |
| `encounter_record_id` | BIGINT | Both | Source-specific surrogate key (InpatientSID or EncounterSID) |
| `encounter_type` | VARCHAR | Both | 'INPATIENT', 'OUTPATIENT', 'EMERGENCY' |
| `encounter_date` | DATETIME | Both | Primary encounter date (admit date for inpatients) |
| `admit_date` | DATETIME | Both | Admission date (NULL for outpatient/emergency) |
| `discharge_date` | DATETIME | Both | Discharge date (NULL if active) |
| `length_of_stay` | INT | Calculated | Days between admit and discharge (NULL if active) |
| `facility_sta3n` | VARCHAR | Both | Station number (as string for consistency) |
| `facility_name` | VARCHAR | Both | Facility name (via lookup or direct) |
| `admit_location_name` | VARCHAR | Both | Admission ward/clinic name |
| `admit_location_type` | VARCHAR | Both | 'WARD', 'CLINIC', 'ED', etc. |
| `discharge_location_name` | VARCHAR | CDWWork | Discharge ward name (NULL for CDWWork2) |
| `discharge_location_type` | VARCHAR | CDWWork | Discharge ward type (NULL for CDWWork2) |
| `provider_name` | VARCHAR | Both | Attending/responsible provider name |
| `admit_diagnosis_icd10` | VARCHAR | CDWWork | Admission diagnosis code (NULL for CDWWork2 Phase 2) |
| `discharge_diagnosis_icd10` | VARCHAR | CDWWork | Discharge diagnosis code (NULL for CDWWork2 Phase 2) |
| `discharge_diagnosis` | VARCHAR | CDWWork | Discharge diagnosis text (NULL for CDWWork2 Phase 2) |
| `discharge_disposition` | VARCHAR | CDWWork | 'Home', 'SNF', 'Rehab', 'AMA', etc. (NULL for CDWWork2 Phase 2) |
| `encounter_status` | VARCHAR | Calculated | 'Active' or 'Discharged' (derived from discharge_date) |
| `data_source` | VARCHAR | Metadata | 'CDWWork' or 'CDWWork2' (source system) |
| `last_updated` | DATETIME | Metadata | ETL processing timestamp |

**Design Notes**:
- **CDWWork2 NULL fields**: Diagnosis and disposition fields will be NULL in Phase 2 (added in later phase when we implement Cerner diagnosis tables)
- **Encounter types**: CDWWork only has 'INPATIENT', CDWWork2 includes 'OUTPATIENT' and 'EMERGENCY' (future UI enhancement)
- **Sta3n data type**: Unified as VARCHAR (CDWWork2 uses VARCHAR, CDWWork uses INT → cast to VARCHAR)
- **Location denormalization**: Both sources resolve to location names (CDWWork via JOIN, CDWWork2 direct)

### 10.4 ETL Pipeline Design

#### 10.4.1 Bronze Layer - New Script

**Create**: `etl/bronze_cdwwork2_encounters.py`

**Purpose**: Extract raw encounter data from `CDWWork2.EncMill.Encounter`

**Implementation Pattern**: Follow `etl/bronze_cdwwork2_vitals.py` (existing reference)

**SQL Query**:
```python
query = """
SELECT
    EncounterSID,
    PersonSID,
    PatientICN,
    Sta3n,
    FacilityName,
    EncounterType,
    EncounterDate,
    AdmitDate,
    DischargeDate,
    LocationName,
    LocationType,
    ProviderName,
    ProviderSID,
    IsActive,
    CreatedDate
FROM EncMill.Encounter
WHERE IsActive = 1
ORDER BY EncounterDate DESC
"""
```

**Output**: `bronze/cdwwork2/encounters/encounters_raw.parquet`

**Metadata Columns**:
- `SourceSystem`: 'CDWWork2' (literal)
- `LoadDateTime`: Current UTC timestamp

**Key Code Structure**:
```python
#!/usr/bin/env python3
"""
Bronze extraction: CDWWork2 Encounters (EncMill.Encounter)
Extracts all encounter types from Cerner/Oracle Health CDWWork2 database.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine
import polars as pl

from config import CDWWORK2_DB_CONFIG
from etl.minio_utils import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_encounters():
    """Extract EncMill.Encounter to Bronze layer."""

    logger.info("=" * 70)
    logger.info("Extracting CDWWork2 Encounters (EncMill.Encounter)...")
    logger.info("=" * 70)

    # Build connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK2_DB_CONFIG['user']}:"
        f"{CDWWORK2_DB_CONFIG['password']}@"
        f"{CDWWORK2_DB_CONFIG['server']}/"
        f"{CDWWORK2_DB_CONFIG['name']}?"
        f"driver={CDWWORK2_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query (see above)
    query = """..."""

    logger.info("Executing query...")
    df = pl.read_database(query, connection=engine)
    logger.info(f"  - Extracted {len(df)} encounters")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Write to MinIO Bronze layer
    minio_client = MinIOClient()
    object_key = build_bronze_path("cdwwork2", "encounters", "encounters_raw.parquet")

    logger.info(f"Writing to MinIO: {object_key}")
    minio_client.write_parquet(df, object_key)

    logger.info("=" * 70)
    logger.info(f"Bronze extraction complete: {len(df)} encounters")
    logger.info(f"  - Written to: s3://{minio_client.bucket_name}/{object_key}")
    logger.info("=" * 70)

    engine.dispose()
    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_encounters()
```

**Testing**:
```bash
# Run Bronze extraction
python etl/bronze_cdwwork2_encounters.py

# Verify Parquet file created
mc ls medz1/bronze/cdwwork2/encounters/

# Validate data
python -c "
from etl.minio_utils import MinIOClient
client = MinIOClient()
df = client.read_parquet('bronze/cdwwork2/encounters/encounters_raw.parquet')
print(f'Total encounters: {len(df)}')
print(f'Encounter types: {df[\"EncounterType\"].value_counts()}')
print(df.head())
"
```

**Expected Output** (Thompson patients):
- Bailey (ICN200001): 7 encounters (Sta3n 687, Walla Walla VAMC)
- Alananah (ICN200002): 3 encounters (Sta3n 687, Walla Walla VAMC)
- Joe (ICN200003): 2 encounters (Sta3n 687, Walla Walla VAMC)
- **Total**: 12 CDWWork2 encounters

#### 10.4.2 Silver Layer - Enhanced Dual-Source Transformation

**Modify**: `etl/silver_inpatient.py` → Refactor to dual-source pattern

**Current State**: Only processes CDWWork `Inpat.Inpatient`

**New Structure** (follow `etl/silver_vitals.py` pattern):
1. **Rename existing function**: `transform_inpatient_silver()` → `transform_cdwwork_encounters()`
2. **Add new function**: `transform_cdwwork2_encounters()`
3. **Add main function**: `transform_encounters_silver()` (merges both sources)

**Function 1: `transform_cdwwork_encounters()`**

Transform CDWWork inpatient data to common Silver schema:

```python
def transform_cdwwork_encounters(minio_client, sta3n_lookup, patient_icn_lookup):
    """
    Transform CDWWork (VistA) inpatient encounters to common Silver schema.
    Returns Polars DataFrame with harmonized encounters.
    """
    logger.info("=" * 70)
    logger.info("Transforming CDWWork (VistA) encounters...")
    logger.info("=" * 70)

    # Step 1: Load Bronze files
    logger.info("Step 1: Loading CDWWork Bronze files...")
    inpatient_path = build_bronze_path("cdwwork", "inpatient", "inpatient_raw.parquet")
    df = minio_client.read_parquet(inpatient_path)
    logger.info(f"  - Loaded {len(df)} inpatient encounters")

    # Step 2: Resolve PatientICN (CDWWork uses PatientSID)
    logger.info("Step 2: Resolving PatientICN...")
    df = df.join(
        patient_icn_lookup.select([
            pl.col("PatientSID"),
            pl.col("PatientICN").alias("patient_icn")
        ]),
        on="PatientSID",
        how="left"
    )

    # Step 3: Resolve Sta3n lookup (facility names)
    logger.info("Step 3: Resolving Sta3n lookups...")
    df = df.with_columns([
        pl.col("Sta3n").cast(pl.Utf8).alias("Sta3n")
    ])
    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # Step 4: Transform to common Silver schema
    logger.info("Step 4: Transforming to common schema...")
    df = df.with_columns([
        # Identity
        pl.col("patient_icn"),

        # Encounter identification
        pl.col("InpatientSID").alias("encounter_record_id"),
        pl.lit("INPATIENT").alias("encounter_type"),  # CDWWork has inpatient only

        # Dates
        pl.col("AdmitDateTime").alias("encounter_date"),  # Primary date
        pl.col("AdmitDateTime").alias("admit_date"),      # Also admission date
        pl.col("DischargeDateTime").alias("discharge_date"),
        pl.col("LengthOfStay").alias("length_of_stay"),

        # Facility
        pl.col("Sta3n").alias("facility_sta3n"),
        pl.col("facility_name"),

        # Locations (from Bronze JOINs)
        pl.col("AdmitWard").alias("admit_location_name"),
        pl.lit("WARD").alias("admit_location_type"),  # CDWWork inpatient = ward
        pl.col("DischargeWard").alias("discharge_location_name"),
        pl.lit("WARD").alias("discharge_location_type"),

        # Provider
        pl.col("AttendingProvider").alias("provider_name"),

        # Diagnoses (CDWWork has these, CDWWork2 doesn't in Phase 2)
        pl.col("AdmitDiagnosisICD10").alias("admit_diagnosis_icd10"),
        pl.col("DischargeDiagnosisICD10").alias("discharge_diagnosis_icd10"),
        pl.col("DischargeDiagnosis").alias("discharge_diagnosis"),
        pl.col("DischargeDisposition").alias("discharge_disposition"),

        # Status
        pl.col("EncounterStatus").alias("encounter_status"),

        # Data source
        pl.lit("CDWWork").alias("data_source"),

        # Metadata
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Step 5: Select final columns (common Silver schema)
    logger.info("Step 5: Selecting final columns...")
    df = df.select([
        "patient_icn",
        "encounter_record_id",
        "encounter_type",
        "encounter_date",
        "admit_date",
        "discharge_date",
        "length_of_stay",
        "facility_sta3n",
        "facility_name",
        "admit_location_name",
        "admit_location_type",
        "discharge_location_name",
        "discharge_location_type",
        "provider_name",
        "admit_diagnosis_icd10",
        "discharge_diagnosis_icd10",
        "discharge_diagnosis",
        "discharge_disposition",
        "encounter_status",
        "data_source",
        "last_updated",
    ])

    logger.info(f"CDWWork transformation complete: {len(df)} encounters")
    return df
```

**Function 2: `transform_cdwwork2_encounters()`**

Transform CDWWork2 encounter data to common Silver schema:

```python
def transform_cdwwork2_encounters(minio_client, sta3n_lookup):
    """
    Transform CDWWork2 (Oracle Health) encounters to common Silver schema.
    Returns Polars DataFrame with harmonized encounters.
    """
    logger.info("=" * 70)
    logger.info("Transforming CDWWork2 (Oracle Health) encounters...")
    logger.info("=" * 70)

    # Step 1: Load Bronze files
    logger.info("Step 1: Loading CDWWork2 Bronze files...")
    encounters_path = build_bronze_path("cdwwork2", "encounters", "encounters_raw.parquet")
    df = minio_client.read_parquet(encounters_path)
    logger.info(f"  - Loaded {len(df)} encounters")

    # Step 2: Resolve Sta3n lookup (CDWWork2 has FacilityName, but may need standardization)
    logger.info("Step 2: Resolving Sta3n lookups...")
    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name_lookup")
        ]),
        on="Sta3n",
        how="left"
    )
    # Use CDWWork2's FacilityName if present, otherwise use lookup
    df = df.with_columns([
        pl.when(pl.col("FacilityName").is_not_null())
            .then(pl.col("FacilityName"))
            .otherwise(pl.col("facility_name_lookup"))
            .alias("facility_name")
    ])

    # Step 3: Calculate length of stay (CDWWork2 doesn't have pre-calculated)
    logger.info("Step 3: Calculating length of stay...")
    df = df.with_columns([
        pl.when(pl.col("DischargeDate").is_not_null())
            .then(
                (pl.col("DischargeDate").cast(pl.Date) -
                 pl.col("AdmitDate").cast(pl.Date)).dt.total_days()
            )
            .otherwise(pl.lit(None))
            .alias("length_of_stay")
    ])

    # Step 4: Derive encounter status
    logger.info("Step 4: Deriving encounter status...")
    df = df.with_columns([
        pl.when(pl.col("DischargeDate").is_null())
            .then(pl.lit("Active"))
            .otherwise(pl.lit("Discharged"))
            .alias("encounter_status")
    ])

    # Step 5: Transform to common Silver schema
    logger.info("Step 5: Transforming to common schema...")
    df = df.with_columns([
        # Identity (CDWWork2 already has PatientICN!)
        pl.col("PatientICN").alias("patient_icn"),

        # Encounter identification
        pl.col("EncounterSID").alias("encounter_record_id"),
        pl.col("EncounterType").alias("encounter_type"),  # INPATIENT, OUTPATIENT, EMERGENCY

        # Dates
        pl.col("EncounterDate").alias("encounter_date"),
        pl.col("AdmitDate").alias("admit_date"),
        pl.col("DischargeDate").alias("discharge_date"),
        pl.col("length_of_stay"),

        # Facility
        pl.col("Sta3n").alias("facility_sta3n"),
        pl.col("facility_name"),

        # Locations (CDWWork2 has name/type directly)
        pl.col("LocationName").alias("admit_location_name"),
        pl.col("LocationType").alias("admit_location_type"),
        pl.lit(None).cast(pl.Utf8).alias("discharge_location_name"),  # CDWWork2 doesn't have separate discharge location
        pl.lit(None).cast(pl.Utf8).alias("discharge_location_type"),

        # Provider (CDWWork2 has name directly)
        pl.col("ProviderName").alias("provider_name"),

        # Diagnoses (NULL for CDWWork2 Phase 2 - not in Encounter table)
        pl.lit(None).cast(pl.Utf8).alias("admit_diagnosis_icd10"),
        pl.lit(None).cast(pl.Utf8).alias("discharge_diagnosis_icd10"),
        pl.lit(None).cast(pl.Utf8).alias("discharge_diagnosis"),
        pl.lit(None).cast(pl.Utf8).alias("discharge_disposition"),

        # Status
        pl.col("encounter_status"),

        # Data source
        pl.lit("CDWWork2").alias("data_source"),

        # Metadata
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Step 6: Select final columns (common Silver schema)
    logger.info("Step 6: Selecting final columns...")
    df = df.select([
        "patient_icn",
        "encounter_record_id",
        "encounter_type",
        "encounter_date",
        "admit_date",
        "discharge_date",
        "length_of_stay",
        "facility_sta3n",
        "facility_name",
        "admit_location_name",
        "admit_location_type",
        "discharge_location_name",
        "discharge_location_type",
        "provider_name",
        "admit_diagnosis_icd10",
        "discharge_diagnosis_icd10",
        "discharge_diagnosis",
        "discharge_disposition",
        "encounter_status",
        "data_source",
        "last_updated",
    ])

    logger.info(f"CDWWork2 transformation complete: {len(df)} encounters")
    return df
```

**Function 3: `transform_encounters_silver()` (main entry point)**

Merge both sources and write unified Silver layer:

```python
def transform_encounters_silver():
    """
    Transform Bronze encounters from both CDWWork and CDWWork2 to Silver layer.
    Harmonizes schemas, adds data_source tracking, and merges into single dataset.
    """

    logger.info("=" * 70)
    logger.info("Starting Silver encounters transformation (CDWWork + CDWWork2)")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Load shared lookup tables
    sta3n_lookup = load_sta3n_lookup()
    patient_icn_lookup = load_patient_icn_lookup()

    # Transform CDWWork encounters
    df_cdwwork = transform_cdwwork_encounters(minio_client, sta3n_lookup, patient_icn_lookup)

    # Transform CDWWork2 encounters
    df_cdwwork2 = transform_cdwwork2_encounters(minio_client, sta3n_lookup)

    # ==================================================================
    # Merge both sources
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Merging CDWWork and CDWWork2 encounters...")
    logger.info("=" * 70)

    df_merged = pl.concat([df_cdwwork, df_cdwwork2], how="vertical")
    logger.info(f"  - Total encounters after merge: {len(df_merged)}")
    logger.info(f"    - CDWWork: {len(df_cdwwork)}")
    logger.info(f"    - CDWWork2: {len(df_cdwwork2)}")

    # ==================================================================
    # Sort and deduplicate (if needed)
    # ==================================================================
    # Sort by patient_icn, encounter_date, data_source
    df_merged = df_merged.sort(["patient_icn", "encounter_date", "data_source"])

    # Check for potential duplicates
    dup_check = df_merged.group_by(["patient_icn", "encounter_date", "admit_location_name"]).agg([
        pl.count().alias("count")
    ]).filter(pl.col("count") > 1)

    if len(dup_check) > 0:
        logger.warning(f"Found {len(dup_check)} potential duplicate encounters (same patient + date + location)")
        logger.warning("Keeping all records (no deduplication in Phase 2)")
    else:
        logger.info("No duplicate encounters found")

    # ==================================================================
    # Write to Silver layer
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Writing to Silver layer...")
    logger.info("=" * 70)

    silver_path = build_silver_path("encounters", "encounters_merged.parquet")
    minio_client.write_parquet(df_merged, silver_path)

    logger.info("=" * 70)
    logger.info(f"Silver transformation complete: {len(df_merged)} encounters written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{silver_path}")
    logger.info(f"  - CDWWork (VistA): {len(df_cdwwork)} encounters")
    logger.info(f"  - CDWWork2 (Oracle Health): {len(df_cdwwork2)} encounters")
    logger.info("=" * 70)

    return df_merged


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_encounters_silver()
```

**Testing Silver Layer**:
```bash
# Run Silver transformation
python etl/silver_inpatient.py

# Verify merged Parquet file
mc ls medz1/silver/encounters/

# Validate data
python -c "
from etl.minio_utils import MinIOClient
client = MinIOClient()
df = client.read_parquet('silver/encounters/encounters_merged.parquet')
print(f'Total encounters: {len(df)}')
print('\\nBy data source:')
print(df.groupby('data_source').count())
print('\\nBy encounter type:')
print(df.groupby('encounter_type').count())
"
```

**Expected Silver Output**:
- CDWWork encounters: ~73 (existing inpatient data)
- CDWWork2 encounters: 12 (Thompson patients at Walla Walla)
- **Total Silver encounters**: ~85

#### 10.4.3 Gold Layer - Verify Data Source Column

**Modify**: `etl/gold_inpatient.py` (minimal changes expected)

**Key Change**: Ensure `data_source` column is propagated from Silver to Gold

**Verification Steps**:
1. Read `silver/encounters/encounters_merged.parquet` (not old CDWWork-only path)
2. Confirm `data_source` column exists in Gold output
3. Test Gold transformation

```python
# In gold_inpatient.py, verify Silver path
silver_path = build_silver_path("encounters", "encounters_merged.parquet")  # Updated path
df_silver = minio_client.read_parquet(silver_path)

# Ensure data_source column is included in Gold schema
df_gold = df_silver.select([
    "patient_icn",
    "patient_key",
    "encounter_record_id",
    "encounter_type",
    "encounter_date",
    "admit_date",
    "discharge_date",
    "length_of_stay",
    "facility_sta3n",
    "facility_name",
    "admit_location_name",
    "provider_name",
    "discharge_diagnosis",
    "discharge_disposition",
    "encounter_status",
    "data_source",  # <--- Ensure this is included!
    "last_updated",
])
```

**Testing**:
```bash
python etl/gold_inpatient.py

# Verify data_source column exists
python -c "
from etl.minio_utils import MinIOClient
client = MinIOClient()
df = client.read_parquet('gold/inpatient/encounters.parquet')
print('Columns:', df.columns)
assert 'data_source' in df.columns, 'Missing data_source column!'
print('✓ data_source column present')
"
```

#### 10.4.4 PostgreSQL Loading - Add Data Source Column

**Modify**: `db/ddl/create_patient_encounters_table.sql` (ALTER TABLE)

**Add Column**:
```sql
-- Add data_source column to patient_encounters table
ALTER TABLE patient_encounters
ADD COLUMN IF NOT EXISTS data_source VARCHAR(20);

-- Add index for data source filtering (optional)
CREATE INDEX IF NOT EXISTS idx_encounters_data_source
ON patient_encounters(data_source);

-- Verify column added
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'patient_encounters' AND column_name = 'data_source';
```

**Apply Schema Change**:
```bash
# Connect to PostgreSQL and apply ALTER TABLE
docker exec -i postgres16 psql -U medz1user -d medz1 < db/ddl/add_encounters_data_source.sql
```

**Modify**: `etl/load_encounters.py` (minimal changes)

**Key Change**: Ensure `data_source` column is included in PostgreSQL INSERT

```python
# In load_encounters.py, verify column list includes data_source
columns_to_load = [
    'patient_icn',
    'patient_key',
    'inpatient_sid',  # Maps to encounter_record_id in Silver
    'encounter_type',
    'encounter_status',
    'admit_datetime',
    'discharge_datetime',
    'admit_ward',
    'discharge_ward',
    'attending_provider',
    'admit_diagnosis_icd10',
    'discharge_diagnosis_icd10',
    'discharge_diagnosis',
    'discharge_disposition',
    'length_of_stay',
    'facility_name',
    'sta3n',
    'data_source',  # <--- New column
    'created_at',
    'updated_at',
]
```

**Testing**:
```bash
# Run PostgreSQL load
python etl/load_encounters.py

# Verify data_source column populated
docker exec -i postgres16 psql -U medz1user -d medz1 -c "
SELECT data_source, encounter_type, COUNT(*)
FROM patient_encounters
GROUP BY data_source, encounter_type
ORDER BY data_source, encounter_type;
"

# Expected output:
#  data_source | encounter_type | count
# -------------+----------------+-------
#  CDWWork     | INPATIENT      |    73
#  CDWWork2    | INPATIENT      |     7
#  CDWWork2    | OUTPATIENT     |     5
```

### 10.5 UI Enhancements

#### 10.5.1 Data Source Badge Design

**Purpose**: Visually indicate which EHR system (VistA or Cerner) provided each encounter

**Design Options**:

**Option A: Discrete Badge** (Recommended)
```html
<!-- Full page encounter row -->
<td>
    {{ enc.admit_datetime.strftime('%m/%d/%Y') }}
    {% if enc.data_source == 'CDWWork2' %}
        <span class="badge badge--cerner badge--xs" title="Oracle Health (Cerner)">C</span>
    {% else %}
        <span class="badge badge--vista badge--xs" title="VistA">V</span>
    {% endif %}
</td>
```

**Styling**:
```css
/* Data source badges */
.badge--vista {
    background-color: #4CAF50;  /* Green for VistA */
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.7rem;
    font-weight: bold;
    margin-left: 6px;
}

.badge--cerner {
    background-color: #2196F3;  /* Blue for Cerner */
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.7rem;
    font-weight: bold;
    margin-left: 6px;
}

.badge--xs {
    font-size: 0.65rem;
    padding: 1px 4px;
}
```

**Option B: Icon with Tooltip**
```html
<td>
    {{ enc.admit_datetime.strftime('%m/%d/%Y') }}
    {% if enc.data_source == 'CDWWork2' %}
        <i class="fa-solid fa-c data-source-icon data-source-icon--cerner"
           title="Oracle Health (Cerner)"></i>
    {% else %}
        <i class="fa-solid fa-v data-source-icon data-source-icon--vista"
           title="VistA"></i>
    {% endif %}
</td>
```

**Option C: Facility Name Suffix**
```html
<td>{{ enc.facility_name }} {% if enc.data_source == 'CDWWork2' %}(Cerner){% endif %}</td>
```

**Recommendation**: Use **Option A (Badge)** for primary implementation. Badges are:
- Visually distinct
- Space-efficient
- Consistent with existing med-z1 badge patterns
- Accessible (tooltip provides full context)

#### 10.5.2 Widget Updates

**File**: `app/templates/partials/encounters_widget.html`

**Change**: Add data source badge to each encounter item

```html
<div class="encounter-item-widget__date">
    {% if enc.encounter_status == 'Active' %}
        <i class="fa-solid fa-hospital text-warning"></i>
        {{ enc.admit_datetime.strftime('%m/%d/%Y') }} - {{ enc.admit_ward }}
        <span class="badge badge--warning badge--sm">ACTIVE</span>
        {% if enc.data_source == 'CDWWork2' %}
            <span class="badge badge--cerner badge--xs" title="Oracle Health (Cerner)">C</span>
        {% endif %}
    {% else %}
        {{ enc.admit_datetime.strftime('%m/%d/%Y') }} - {{ enc.discharge_datetime.strftime('%m/%d/%Y') }}
        ({{ enc.length_of_stay }} day{{ 's' if enc.length_of_stay != 1 else '' }})
        {% if enc.data_source == 'CDWWork2' %}
            <span class="badge badge--cerner badge--xs" title="Oracle Health (Cerner)">C</span>
        {% endif %}
    {% endif %}
</div>
```

**Design Note**: Only show Cerner badge (not VistA) to reduce visual clutter - VistA is the "default" source

#### 10.5.3 Full Page Updates

**File**: `app/templates/patient_encounters.html`

**Change 1**: Add data source badge to table rows

```html
<tbody>
  {% for enc in encounters %}
    <tr class="{% if enc.encounter_status == 'Active' %}active-encounter{% endif %}">
      <td>
          {{ enc.admit_datetime.strftime('%m/%d/%Y') }}
          {% if enc.data_source == 'CDWWork2' %}
              <span class="badge badge--cerner badge--xs" title="Oracle Health (Cerner)">C</span>
          {% endif %}
      </td>
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
        {% if enc.data_source == 'CDWWork2' %}
            <span class="text-muted"> · Source: Oracle Health (Cerner)</span>
        {% endif %}
        {% if enc.discharge_diagnosis %}
          <br><strong>Discharge Diagnosis:</strong> {{ enc.discharge_diagnosis }}
          <br><strong>Disposition:</strong> {{ enc.discharge_disposition }}
        {% endif %}
      </td>
    </tr>
  {% endfor %}
</tbody>
```

**Change 2**: Add optional data source filter (future enhancement)

```html
<div class="filters">
  <label>Status:
    <select name="status" hx-get="/patient/{{ patient_icn }}/encounters" hx-target="#encounters-table">
      <option value="all">All</option>
      <option value="active">Active</option>
      <option value="discharged">Discharged</option>
    </select>
  </label>

  <label>Data Source:
    <select name="data_source" hx-get="/patient/{{ patient_icn }}/encounters" hx-target="#encounters-table">
      <option value="all">All Sources</option>
      <option value="CDWWork">VistA Sites</option>
      <option value="CDWWork2">Cerner Sites</option>
    </select>
  </label>
</div>
```

#### 10.5.4 API Query Layer Updates

**File**: `app/db/encounters.py`

**Change**: Add `data_source` column to all SELECT statements

```python
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
            sta3n,
            data_source  -- <--- NEW COLUMN
        FROM patient_encounters
        WHERE patient_icn = :icn
        ORDER BY admit_datetime DESC
        LIMIT :limit
    """)
    # ... rest of function unchanged
```

**Apply same change to**:
- `get_encounter_summary()` (no change needed - aggregate function)
- `get_all_encounters()` (add `data_source` to SELECT list)

**Optional**: Add data source filter parameter

```python
def get_all_encounters(
    icn: str,
    status: str = 'all',
    facility: Optional[int] = None,
    data_source: str = 'all',  # <--- NEW PARAMETER
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

    if data_source != 'all':  # <--- NEW FILTER
        where_clauses.append("data_source = :data_source")
        params["data_source"] = data_source

    # ... rest of function unchanged
```

### 10.6 Test Data - Thompson Patients

#### 10.6.1 Thompson Patient Overview

**Purpose**: Thompson siblings (Bailey, Alananah, Joe) provide test cases for CDWWork2 encounters

**Patient Profiles**:

| Patient | ICN | PersonSID (CDWWork2) | PatientSID (CDWWork) | Site Transition |
|---------|-----|---------------------|----------------------|-----------------|
| Bailey Thompson | ICN200001 | 3001 | 2001 | Bay Pines FL (516) → Walla Walla WA (687) |
| Alananah Thompson | ICN200002 | 3002 | 2002 | Bay Pines FL (516) → Walla Walla WA (687) |
| Joe Thompson | ICN200003 | 3003 | 2003 | Bay Pines FL (516) → Walla Walla WA (687) |

**Scenario**: Three siblings served at Bay Pines VA (VistA/Sta3n 516) until February 2025, then relocated to Walla Walla VA (Cerner/Sta3n 687)

**Data Distribution**:
- **CDWWork encounters**: Historical data at Bay Pines (Sta3n 516) before February 2025
- **CDWWork2 encounters**: Current data at Walla Walla (Sta3n 687) from February 2025 onward

#### 10.6.2 Thompson CDWWork2 Encounter Data

**File**: `mock/sql-server/cdwwork2/insert/Thompson-Bailey.sql` (already created)

**Bailey Thompson - 7 Encounters**:
- 5 Outpatient clinic visits (Primary Care, Cardiology)
- 2 Inpatient admissions (CHF exacerbation, Pneumonia)
- Date range: 2025-02-15 to 2026-02-01

**File**: `mock/sql-server/cdwwork2/insert/Thompson-Alananah.sql` (already created)

**Alananah Thompson - 3 Encounters**:
- 3 Outpatient clinic visits (Primary Care)
- 0 Inpatient admissions (healthy control relative to Bailey)
- Date range: 2025-02-15 to 2026-02-01

**File**: `mock/sql-server/cdwwork2/insert/Thompson-Joe.sql` (already created)

**Joe Thompson - 2 Encounters**:
- 2 Outpatient clinic visits (Primary Care)
- 0 Inpatient admissions (healthiest of three siblings)
- Date range: 2025-02-15 to 2026-02-01

**Total CDWWork2 Encounters**: 12 (7 Bailey + 3 Alananah + 2 Joe)

**Verification Query**:
```sql
-- Verify Thompson CDWWork2 encounters
USE CDWWork2;
GO

SELECT
    e.PatientICN,
    e.EncounterType,
    e.EncounterDate,
    e.LocationName,
    e.ProviderName,
    e.FacilityName
FROM EncMill.Encounter e
WHERE e.PatientICN IN ('ICN200001', 'ICN200002', 'ICN200003')
ORDER BY e.PatientICN, e.EncounterDate;
GO

-- Expected: 12 encounters (7 Bailey, 3 Alananah, 2 Joe)
```

### 10.7 Implementation Roadmap

**Phase 2 Timeline**: 4-5 days of focused work

#### Day 1: Bronze Layer (2-3 hours)
- ✅ Prerequisite: Thompson CDWWork2 scripts already created and populated
- Create `etl/bronze_cdwwork2_encounters.py` following vitals pattern
- Test Bronze extraction
- Verify Parquet file in MinIO (`bronze/cdwwork2/encounters/`)
- Validate data (12 Thompson encounters)

**Deliverables**:
- `etl/bronze_cdwwork2_encounters.py`
- Bronze Parquet file with 12 encounters
- Verification script output

#### Day 2-3: Silver Layer (6-8 hours)
- Refactor `etl/silver_inpatient.py` to dual-source pattern
  - Rename existing logic to `transform_cdwwork_encounters()`
  - Create `transform_cdwwork2_encounters()`
  - Create `transform_encounters_silver()` main function
- Test Silver transformation
- Verify merged output (~85 encounters = 73 CDWWork + 12 CDWWork2)
- Validate common schema alignment

**Deliverables**:
- Updated `etl/silver_inpatient.py` (dual-source)
- Silver Parquet file (`silver/encounters/encounters_merged.parquet`)
- Schema validation output

#### Day 3: Gold Layer & PostgreSQL (3-4 hours)
- Update `etl/gold_inpatient.py` to read from new Silver path
- Verify `data_source` column propagated
- Add `data_source` column to PostgreSQL `patient_encounters` table
- Update `etl/load_encounters.py` to include `data_source` in INSERT
- Test full ETL pipeline end-to-end
- Verify PostgreSQL data includes both sources

**Deliverables**:
- Updated `etl/gold_inpatient.py`
- PostgreSQL ALTER TABLE script
- Updated `etl/load_encounters.py`
- PostgreSQL verification queries

#### Day 4: API & UI (4-5 hours)
- Update `app/db/encounters.py` to SELECT `data_source` column
- Add CSS for data source badges (`.badge--vista`, `.badge--cerner`)
- Update widget template to show Cerner badge
- Update full page template to show source indicators
- Test UI with Thompson patients
- Verify badges display correctly

**Deliverables**:
- Updated `app/db/encounters.py`
- Updated CSS (`app/static/styles.css`)
- Updated `app/templates/partials/encounters_widget.html`
- Updated `app/templates/patient_encounters.html`
- UI screenshots

#### Day 5: Testing & Documentation (3-4 hours)
- Run full ETL pipeline (`scripts/run_all_etl.sh`)
- Test all three Thompson patients in UI
- Verify encounter counts match expectations
- Write integration tests
- Update this design document (mark Phase 2 complete)
- Update `docs/spec/cdwwork2-design.md` (add Phase 5 status)
- Code review and cleanup

**Deliverables**:
- ETL pipeline run log
- Test results
- Updated documentation
- Phase 2 completion status

**Total Estimated Time**: 18-24 hours (~3-5 days)

### 10.8 Success Criteria

**Phase 2 Complete When**:

**ETL Pipeline**:
- ✅ Bronze ETL extracts 12 CDWWork2 encounters
- ✅ Silver ETL produces ~85 merged encounters (73 CDWWork + 12 CDWWork2)
- ✅ Gold Parquet includes `data_source` column
- ✅ PostgreSQL `patient_encounters` table has `data_source` column
- ✅ PostgreSQL contains ~85 total encounters with correct source attribution

**Data Quality**:
- ✅ No duplicate encounters (same patient + date + location)
- ✅ All Thompson encounters (12) visible in UI
- ✅ Encounter types correctly mapped (INPATIENT → INPATIENT, etc.)
- ✅ Facility names resolved correctly (Walla Walla VAMC for Sta3n 687)

**UI Verification**:
- ✅ Bailey Thompson encounters page shows 7 CDWWork2 encounters with Cerner badge
- ✅ Alananah Thompson encounters page shows 3 CDWWork2 encounters with Cerner badge
- ✅ Joe Thompson encounters page shows 2 CDWWork2 encounters with Cerner badge
- ✅ Existing patients (ICN100001-ICN100013) continue to show CDWWork encounters (no regression)
- ✅ Data source badges render correctly and have accessible tooltips

**Documentation**:
- ✅ Phase 2 marked complete in this document
- ✅ `docs/spec/cdwwork2-design.md` updated with Phase 5 (Encounters) status
- ✅ Code comments explain dual-source harmonization logic

### 10.9 Known Limitations (Phase 2)

1. **CDWWork2 Diagnosis Fields**: NULL in Phase 2 (Cerner diagnoses are in separate tables, not in `EncMill.Encounter`)
   - **Impact**: Discharge diagnosis/disposition only shown for CDWWork encounters
   - **Future**: Add CDWWork2 diagnosis linkage in Phase 3

2. **Encounter Type Filtering**: UI currently supports "All", "Active", "Discharged" filters
   - **Missing**: "Inpatient", "Outpatient", "Emergency" type filter
   - **Future**: Add encounter type dropdown in UI enhancement phase

3. **Discharge Location**: CDWWork2 doesn't track discharge ward separately from admit ward
   - **Impact**: `discharge_location_name` NULL for CDWWork2 encounters
   - **Future**: Investigate if Cerner tracks discharge location in ward transfer tables

4. **Deduplication**: Current implementation keeps all records if potential duplicates detected
   - **Impact**: Same encounter may appear twice if data overlaps (unlikely in current mock data)
   - **Future**: Implement canonical encounter matching logic (ICN + admit date + facility)

5. **Real-Time Data**: Phase 2 does not include Vista RPC overlay for T-0 encounters
   - **Future**: Add "Refresh from Vista" button in Phase 3 (per Vitals domain pattern)

### 10.10 Phase 2 Implementation Results ✅

**Completion Date:** February 10, 2026
**Implementation Duration:** 5 days (Day 1-5 roadmap completed)

**Final Metrics:**
- **Total Encounters**: 146 (118 CDWWork + 28 CDWWork2)
- **Patients with Dual-Source Data**: 5 (Adam, Alexander, Bailey, Alananah, Joe)
- **Thompson Family Encounters**: 53 total (39 Bailey + 11 Alananah + 3 Joe)
- **Encounter Types Supported**: INPATIENT, OUTPATIENT
- **Data Sources Tracked**: CDWWork (VistA), CDWWork2 (Cerner)
- **Facilities Represented**: 11 total (7 VistA sites + 4 Cerner sites)

**Technical Deliverables Completed:**
1. ✅ **Bronze Layer**: `etl/bronze_cdwwork2_encounters.py` - Extracts 28 CDWWork2 encounters
2. ✅ **Silver Layer**: `etl/silver_inpatient.py` - Refactored for dual-source harmonization (555 lines)
3. ✅ **Gold Layer**: `etl/gold_inpatient.py` - Preserves `data_source` and `encounter_type` fields
4. ✅ **PostgreSQL**: Added `data_source` and `encounter_type` columns to `patient_encounters` table
5. ✅ **Load Script**: `etl/load_encounters.py` - Maps new Gold schema to PostgreSQL
6. ✅ **Query Layer**: All 4 functions in `app/db/encounters.py` updated to return data provenance
7. ✅ **UI Widget**: `encounters_widget.html` - Data source badges (Cerner/VistA) added
8. ✅ **UI Full Page**: `encounters_content.html` - Source column added to table with badges
9. ✅ **Integration Tests**: All Thompson patients verified with dual-source data

**User-Visible Features:**
- **Data Source Badges**: Blue "Cerner" badges for CDWWork2 data, gray "VistA" badges for CDWWork data
- **Encounter Type Support**: Both INPATIENT and OUTPATIENT encounters displayed
- **Complete Patient History**: Veterans see all encounters from both VistA and Cerner sites in unified view
- **Site Transition Tracking**: Thompson patients demonstrate Bay Pines (VistA) → Walla Walla (Cerner) migration

**Thompson Family Validation Results:**
```
Bailey Thompson (ICN200001):
  Total encounters: 39
  Data sources: CDWWork=32, CDWWork2=7
  Encounter types: INPATIENT=34, OUTPATIENT=5
  Facilities: Bay Pines FL (VistA) + Walla Walla WA (Cerner)

Alananah Thompson (ICN200002):
  Total encounters: 11
  Data sources: CDWWork=8, CDWWork2=3
  Encounter types: INPATIENT=8, OUTPATIENT=3
  Facilities: Bay Pines FL (VistA) + Walla Walla WA (Cerner)

Joe Thompson (ICN200003):
  Total encounters: 3
  Data sources: CDWWork=1, CDWWork2=2
  Encounter types: INPATIENT=1, OUTPATIENT=2
  Facilities: Bay Pines FL (VistA) + Walla Walla WA (Cerner)
```

**Backward Compatibility:**
- Legacy `transform_inpatient_silver()` function maintained with deprecation warning
- Legacy `transform_inpatient_gold()` function maintained with deprecation warning
- Existing query functions extended (not replaced) to preserve API compatibility

**Known Limitations (By Design):**
- Diagnosis fields NULL for CDWWork2 encounters (diagnosis tables not yet integrated)
- Discharge disposition NULL for CDWWork2 encounters (not tracked in EncMill.Encounter)
- Discharge location NULL for CDWWork2 encounters (single location field only)
- Outpatient encounters not yet displayed prominently in UI (future Phase 3)

---

## 11. Testing Strategy

### 11.1 Unit Tests

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
| v1.1 | 2025-12-15 | Claude Code | ✅ **Phase 1 implementation complete**. Updated status to reflect all 6 days completed, including ETL pipeline, widget, full page with pagination (ADR-005), patient ICN fix, Home + O₂ badge, and breadcrumb consistency |
| v2.0 | 2026-02-09 | Claude Code | 🚧 **Phase 2 design added** - CDWWork2 Integration. Added comprehensive Section 10 covering: dual-source ETL architecture, schema harmonization (CDWWork Inpat.Inpatient ↔ CDWWork2 EncMill.Encounter), Bronze/Silver/Gold pipeline design, PostgreSQL data_source column, UI badges for source attribution, Thompson patient test data (12 CDWWork2 encounters), 4-5 day implementation roadmap with detailed code examples, success criteria, and known limitations. Total addition: ~2,000 lines of detailed technical specification. |
