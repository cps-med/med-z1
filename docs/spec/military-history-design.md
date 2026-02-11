# Patient Military History Enhancement - Design Specification

**Document Version:** v1.0
**Last Updated:** February 6, 2026
**Implementation Status:** 📋 **PLANNED** (Not yet implemented)
**Current State:** Only `service_connected_percent` field is used from rich disability data
**Target State:** Full military history tracking with environmental exposures

**Implementation Status Source:** `docs/spec/implementation-status.md`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Prerequisites](#3-prerequisites)
4. [Current State Analysis](#4-current-state-analysis)
5. [Implementation Plan](#5-implementation-plan)
   - [Phase 1: Expand Disability Mock Data](#phase-1-expand-disability-mock-data)
   - [Phase 2: New Table & ETL Pipeline](#phase-2-new-table--etl-pipeline)
   - [Phase 3: UI Enhancements](#phase-3-ui-enhancements)
   - [Phase 4: AI Integration](#phase-4-ai-integration)
6. [Testing Strategy](#6-testing-strategy)
7. [Future Enhancements](#7-future-enhancements)

---

## 1. Overview

### 1.1 Purpose

The **Patient Military History Enhancement** expands the med-z1 application to fully utilize rich military service and environmental exposure data currently stored but underutilized in the CDW disability tables. This enhancement provides clinicians with critical context about:

- **Service-connected disability percentages** (expanded coverage and realistic ranges)
- **Environmental exposures** (Agent Orange, radiation, POW status, Camp Lejeune, Gulf War)
- **Special health considerations** based on service history
- **Priority group indicators** for VA care eligibility

### 1.2 Business Value

**Why This Matters:**

1. **Clinical Decision Support:** Environmental exposures are linked to specific health conditions:
   - Agent Orange: Cancers, diabetes, heart disease (Vietnam veterans)
   - Ionizing Radiation: Cancer risks, special monitoring protocols
   - POW Status: PTSD, complex trauma, special benefits
   - Camp Lejeune: Water contamination-related cancers
   - Gulf War Illness: Burn pit exposure, multi-symptom syndromes

2. **Care Coordination:** Service-connected percentage determines:
   - Priority groups for VA care
   - Medication copay requirements
   - Special eligibility for programs
   - Discharge planning considerations

3. **AI/ML Enhancement:** Exposure data enables more nuanced clinical risk assessments and patient summaries

### 1.3 Scope

**In Scope:**
- Expand service-connected disability mock data (0-100% range, 30+ patients)
- Create new `clinical.patient_military_history` table
- Complete ETL pipeline (Bronze → Silver → Gold → PostgreSQL)
- UI enhancements: Environmental exposure badges, priority indicators, tooltips
- AI integration: Include exposure data in patient summaries

**Out of Scope (This Phase):**
- Detailed service dates, branch, rank, deployment locations (future enhancement)
- Ward transfer history or service-related medical records
- DoD military personnel data integration (DMDC/DEERS)

### 1.4 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **New Table** | Create `clinical.patient_military_history` | Cleaner separation of concerns, room for expansion, matches real VHA data architecture |
| **Data Coverage** | 30+ patients with disability records (79%+ coverage) | Realistic testing, diverse percentages (0-100%), supports UI/AI testing |
| **UI Location** | Expand Demographics page | Military history is demographic context, natural fit |
| **AI Integration** | Include in demographics summary | Exposures are risk factors, relevant to clinical decision support |

---

## 2. Objectives and Success Criteria

### 2.1 Data Pipeline Objectives

- [ ] **Mock Data**: 30+ patients with service-connected percentages (0-100% realistic distribution)
- [ ] **Bronze Layer**: Extract all 14 fields from `SPatient.SPatientDisability`
- [ ] **Silver Layer**: Clean, standardize, and resolve patient identity
- [ ] **Gold Layer**: Create patient-centric military history Parquet files
- [ ] **PostgreSQL**: Load into `clinical.patient_military_history` table

### 2.2 UI Objectives

- [ ] **Demographics Page**: Display service-connected percentage with priority group indicator
- [ ] **Environmental Exposures**: Badge display for Agent Orange, POW, radiation, Camp Lejeune, Gulf War
- [ ] **Tooltips**: Context-sensitive help for service-connected percentage meanings
- [ ] **Widget**: Consider adding military history summary to dashboard widget (optional)

### 2.3 AI Objectives

- [ ] **Context Builder**: Include environmental exposures in patient demographics summary
- [ ] **Query Support**: Enable queries like "Does this patient have toxic exposure history?"
- [ ] **Risk Assessment**: LLM can reference exposures in clinical risk narratives

### 2.4 Success Criteria

- [ ] 79%+ of test patients have service-connected data (30 of 38 patients)
- [ ] Full range of percentages represented (0%, 10%, 20%...100%)
- [ ] Environmental exposure flags display correctly in UI
- [ ] AI includes exposure context when present
- [ ] Data pipeline runs end-to-end without errors
- [ ] PostgreSQL queries return in <500ms

---

## 3. Prerequisites

### 3.1 Completed Work

**Required Foundations:**
- Bronze ETL framework (Polars-based extraction)
- Silver ETL framework (identity resolution, harmonization)
- Gold ETL framework (patient-centric transformations)
- PostgreSQL serving database setup
- Demographics page implementation (full page with sections)
- AI Clinical Insights (PatientContextBuilder service)
- Existing disability ETL (`bronze_patient_disability.py` extracts all fields)

### 3.2 Environment Setup

**SQL Server (Mock CDW):**
- Container: `sqlserver2019`
- Database: `CDWWork`
- Table: `SPatient.SPatientDisability` (already exists with 12 records)

**PostgreSQL (Serving Database):**
- Container: `postgres16`
- Database: `medz1`
- New table: `clinical.patient_military_history` (to be created)

**MinIO (Data Lake):**
- Bucket: `med-z1`
- Existing path: `bronze/cdwwork/patient_disability/` (Bronze already extracts all fields)

---

## 4. Current State Analysis

### 4.1 Data Flow - Current State

```
SQL Server CDWWork                  Bronze Layer (MinIO)           Silver Layer
┌─────────────────────────┐         ┌──────────────────┐         ┌────────────────┐
│ SPatient.               │         │ patient_         │         │ patient_       │
│ SPatientDisability      │────────>│ disability_raw   │────────>│ cleaned        │
│                         │         │ .parquet         │         │ .parquet       │
│ 14 fields extracted     │         │                  │         │                │
│ - ServiceConnectedFlag  │         │ All 14 fields    │         │ Only 1 field   │
│ - ServiceConnectedPct   │         │                  │         │ extracted      │
│ - AgentOrangeCode       │         │                  │         │                │
│ - RadiationCode         │         │                  │         │ Drops 13       │
│ - POWStatusCode         │         │                  │         │ fields         │
│ - CampLejeuneFlag       │         │                  │         │                │
│ - (9 more fields...)    │         │                  │         │                │
└─────────────────────────┘         └──────────────────┘         └────────────────┘
```

**Current Silver Layer Logic (`etl/silver_patient.py` lines 171-177):**
```python
# Select service connected percent from disability (Phase 2)
# Logic: One record per patient (most recent if multiple exist)
df_service_connected = (
    df_disability
    .select([
        pl.col("PatientSID").alias("patient_sid_disability"),
        pl.col("ServiceConnectedPercent").alias("service_connected_percent"),  # ← Only this field
    ])
    .unique(subset=["patient_sid_disability"])
)
```

**Problem:** 13 valuable fields are dropped in Silver layer, never making it to Gold/PostgreSQL/UI/AI.

### 4.2 Current PostgreSQL Schema

**Table:** `clinical.patient_demographics`
**Field:** `service_connected_percent DECIMAL(5,2)` ← Only disability-related field

### 4.3 Current UI Display

**Demographics Full Page:**
- ✅ Shows service-connected percentage in "Military Service & Eligibility" section
- ❌ No environmental exposure information
- ❌ No priority group indicator
- ❌ No tooltips explaining percentage meanings

**Dashboard Widget:**
- ❌ Does not display military history at all

### 4.4 Current AI Integration

**PatientContextBuilder** (`ai/services/patient_context.py` lines 99-101):
```python
sc_pct = demo.get('service_connected_percent')
if sc_pct is not None:
    text += f", service-connected disability {int(sc_pct)}%"
```
- ✅ Includes service-connected percentage
- ❌ Does not include environmental exposures

---

## 5. Implementation Plan

---

## Phase 1: Expand Disability Mock Data

**Goal:** Create realistic, diverse service-connected disability records for 30+ patients (79%+ coverage) with percentages ranging from 0-100%.

**Time Estimate:** 2-3 hours

---

### Task 1.1: Generate Disability Records

**Update:** `mock/sql-server/cdwwork/insert/SPatient.SPatientDisability.sql`

**Current State:** 12 records (31.6% coverage), mostly 50.5%, limited diversity

**Target State:** 30+ records (79%+ coverage), realistic distribution:
- 0%: ~20% of records (evaluated but not service-connected)
- 10-30%: ~35% of records
- 40-60%: ~25% of records
- 70-90%: ~15% of records
- 100%: ~5% of records (Total & Permanent Disability)

**Copy/Paste Code:**

```sql
/*
|--------------------------------------------------------------------------------
| Insert: SPatient.SPatientDisability.sql
|--------------------------------------------------------------------------------
| Expanded test data with realistic service-connected percentages and exposures
| Version: v2.0 (2026-02-06) - Military History Enhancement
|
| SPatientDisabilitySID => 1001 series (existing)
|                       => 1100 series (new records)
|
| Environmental Exposure Codes:
| - AgentOrangeExposureCode: Y=Yes, N=No, U=Unknown
| - IonizingRadiationCode: Y=Yes, N=No, U=Unknown
| - POWStatusCode: Y=Yes, N=No, U=Unknown
| - SHADFlag: Y=Yes, N=No, U=Unknown (Shipboard Hazard and Defense)
| - SWAsiaCode: Y=Yes, N=No, U=Unknown (Southwest Asia/Gulf War)
| - CampLejeuneFlag: Y=Yes, N=No
|--------------------------------------------------------------------------------
*/

-- Set the active database
USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Clear existing data
DELETE FROM SPatient.SPatientDisability;
GO

-- Insert expanded disability records
INSERT INTO SPatient.SPatientDisability
(
    SPatientDisabilitySID, PatientSID, PatientIEN, Sta3n, ClaimFolderInstitutionSID,
    ServiceConnectedFlag, ServiceConnectedPercent,
    AgentOrangeExposureCode, IonizingRadiationCode, POWStatusCode, SHADFlag,
    AgentOrangeLocation, POWLocation, SWAsiaCode, CampLejeuneFlag
)
VALUES
-- ========================================
-- Existing Records (Updated)
-- ========================================

-- Patient 1001: Adam Dooree - Vietnam veteran, Agent Orange exposure
(1001, 1001, 'PtIEN15401', 508, 11001, 'Y', 70.0, 'Y', 'N', 'N', 'N', 'VIETNAM', NULL, 'N', 'N'),

-- Patient 1002: Barry Miifaa - Gulf War veteran
(1002, 1002, 'PtIEN15402', 508, 11001, 'Y', 40.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1003: Carol Soola - Moderate service-connected conditions
(1003, 1003, 'PtIEN15403', 508, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1004: Debby Tiidoo - Low service-connected percentage
(1004, 1004, 'PtIEN15404', 508, 11001, 'Y', 20.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1005: Edward Dooree - Evaluated but not service-connected
(1005, 1005, 'PtIEN15405', 508, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1006: Francine Miifaa - Camp Lejeune exposure
(1006, 1006, 'PtIEN15406', 516, 11001, 'Y', 60.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'Y'),

-- Patient 1007: Adam Amajor - Former POW, high disability
(1007, 1007, 'PtIEN15407', 516, 11001, 'Y', 100.0, 'N', 'N', 'Y', 'N', NULL, 'VIETNAM', 'N', 'N'),

-- Patient 1008: Barry Bmajor - Low disability percentage
(1008, 1008, 'PtIEN15408', 516, 11001, 'Y', 10.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1606021: ZZDUCK, DONN - Moderate disability
(1021, 1606021, 'PtIEN887021', 508, 11001, 'Y', 30.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1606026: ZZZ, TEST - Gulf War veteran with radiation exposure
(1026, 1606026, 'PtIEN887026', 516, 11001, 'Y', 80.0, 'N', 'Y', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1026: Margaret E Wilson - DECEASED - WWII era veteran
(1027, 1026, 'PtIEN1026', 508, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1027: Robert J Anderson - DECEASED - OIF/OEF combat veteran with PTSD
(1028, 1027, 'PtIEN1027', 528, 11001, 'Y', 70.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- ========================================
-- New Records (Expanded Coverage)
-- ========================================

-- Patient 1009: Claire Cmajor - Moderate disability
(1100, 1009, 'PtIEN15409', 552, 11001, 'Y', 40.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1010: Alexander Aminor - High disability, Gulf War
(1101, 1010, 'PtIEN15410', 688, 11001, 'Y', 90.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1011: George Harris - Low disability
(1102, 1011, 'PtIEN15411', 508, 11001, 'Y', 10.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1012: Helen Martinez - Evaluated but not service-connected
(1103, 1012, 'PtIEN15412', 516, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1013: Irving Thompson - Moderate disability
(1104, 1013, 'PtIEN15413', 552, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1014: Joyce Kim - Agent Orange exposure
(1105, 1014, 'PtIEN15414', 688, 11001, 'Y', 60.0, 'Y', 'N', 'N', 'N', 'VIETNAM', NULL, 'N', 'N'),

-- Patient 1015: Kenneth Wilson - Low disability
(1106, 1015, 'PtIEN15415', 508, 11001, 'Y', 20.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1016V123456: Marcus Johnson - High disability
(1107, 1016, 'PtIEN15416', 516, 11001, 'Y', 80.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1017V234567: Sarah Williams - Moderate disability
(1108, 1017, 'PtIEN15417', 552, 11001, 'Y', 30.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1018V345678: David Chen - Evaluated but not service-connected
(1109, 1018, 'PtIEN15418', 688, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1019V456789: Linda Rodriguez - Camp Lejeune exposure
(1110, 1019, 'PtIEN15419', 508, 11001, 'Y', 40.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'Y'),

-- Patient 1020V567890: Robert Thompson - Total & Permanent Disability
(1111, 1020, 'PtIEN15420', 516, 11001, 'Y', 100.0, 'N', 'Y', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1021V678901: Patricia Garcia - Low disability
(1112, 1021, 'PtIEN15421', 552, 11001, 'Y', 10.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1022V789012: James Anderson - Gulf War veteran
(1113, 1022, 'PtIEN15422', 688, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1023V890123: Barbara Lee - Moderate disability
(1114, 1023, 'PtIEN15423', 508, 11001, 'Y', 60.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1024V901234: Charles White - Low disability
(1115, 1024, 'PtIEN15424', 516, 11001, 'Y', 20.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1025V012345: Dorothy Martinez - High disability
(1116, 1025, 'PtIEN15425', 552, 11001, 'Y', 90.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1011533925: ZZTEST, DONNA R - Moderate disability
(1117, 1011533925, 'PtIEN533925', 508, 11001, 'Y', 40.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1051720886: ZZTEST, APPLE - Low disability
(1118, 1051720886, 'PtIEN720886', 516, 11001, 'Y', 30.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1060349008: ZZTEST, ABC - Evaluated but not service-connected
(1119, 1060349008, 'PtIEN349008', 552, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N');

GO

-- Verify inserted records
PRINT 'Total disability records inserted:';
SELECT COUNT(*) AS TotalRecords FROM SPatient.SPatientDisability;

PRINT 'Distribution by service-connected percentage:';
SELECT
    CASE
        WHEN ServiceConnectedPercent = 0 THEN '0% (Not SC)'
        WHEN ServiceConnectedPercent BETWEEN 1 AND 30 THEN '10-30%'
        WHEN ServiceConnectedPercent BETWEEN 31 AND 60 THEN '40-60%'
        WHEN ServiceConnectedPercent BETWEEN 61 AND 90 THEN '70-90%'
        WHEN ServiceConnectedPercent > 90 THEN '100% (T&P)'
    END AS PercentageRange,
    COUNT(*) AS RecordCount
FROM SPatient.SPatientDisability
GROUP BY
    CASE
        WHEN ServiceConnectedPercent = 0 THEN '0% (Not SC)'
        WHEN ServiceConnectedPercent BETWEEN 1 AND 30 THEN '10-30%'
        WHEN ServiceConnectedPercent BETWEEN 31 AND 60 THEN '40-60%'
        WHEN ServiceConnectedPercent BETWEEN 61 AND 90 THEN '70-90%'
        WHEN ServiceConnectedPercent > 90 THEN '100% (T&P)'
    END
ORDER BY PercentageRange;

PRINT 'Environmental exposure summary:';
SELECT
    SUM(CASE WHEN AgentOrangeExposureCode = 'Y' THEN 1 ELSE 0 END) AS AgentOrange,
    SUM(CASE WHEN IonizingRadiationCode = 'Y' THEN 1 ELSE 0 END) AS Radiation,
    SUM(CASE WHEN POWStatusCode = 'Y' THEN 1 ELSE 0 END) AS POW,
    SUM(CASE WHEN CampLejeuneFlag = 'Y' THEN 1 ELSE 0 END) AS CampLejeune,
    SUM(CASE WHEN SWAsiaCode = 'Y' THEN 1 ELSE 0 END) AS GulfWar
FROM SPatient.SPatientDisability;
GO
```

### Task 1.2: Apply Mock Data to SQL Server

**Command:**

```bash
# From project root
docker exec -i sqlserver2019 /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "AllieD-1993-2025-z1" -d CDWWork -C \
  -i /path/to/mock/sql-server/cdwwork/insert/SPatient.SPatientDisability.sql
```

**Or use file copy method:**

```bash
# Copy SQL file into container
docker cp mock/sql-server/cdwwork/insert/SPatient.SPatientDisability.sql \
  sqlserver2019:/tmp/insert_disability.sql

# Execute SQL file
docker exec -i sqlserver2019 /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "AllieD-1993-2025-z1" -d CDWWork -C \
  -i /tmp/insert_disability.sql
```

### Task 1.3: Verify Mock Data

**Verification SQL:**

```sql
-- Connect to SQL Server and run these queries

-- 1. Total records
SELECT COUNT(*) AS TotalRecords
FROM SPatient.SPatientDisability;
-- Expected: 30 records

-- 2. Distribution check
SELECT
    ServiceConnectedPercent,
    COUNT(*) AS PatientCount
FROM SPatient.SPatientDisability
GROUP BY ServiceConnectedPercent
ORDER BY ServiceConnectedPercent;

-- 3. Exposure flags check
SELECT
    COUNT(*) AS TotalRecords,
    SUM(CASE WHEN AgentOrangeExposureCode = 'Y' THEN 1 ELSE 0 END) AS AgentOrange,
    SUM(CASE WHEN IonizingRadiationCode = 'Y' THEN 1 ELSE 0 END) AS Radiation,
    SUM(CASE WHEN POWStatusCode = 'Y' THEN 1 ELSE 0 END) AS POW,
    SUM(CASE WHEN CampLejeuneFlag = 'Y' THEN 1 ELSE 0 END) AS CampLejeune,
    SUM(CASE WHEN SWAsiaCode = 'Y' THEN 1 ELSE 0 END) AS GulfWar
FROM SPatient.SPatientDisability;
-- Expected: 3 Agent Orange, 2 Radiation, 1 POW, 2 Camp Lejeune, 7 Gulf War

-- 4. Sample data spot-check
SELECT TOP 5
    PatientSID,
    ServiceConnectedPercent,
    AgentOrangeExposureCode,
    POWStatusCode,
    SWAsiaCode
FROM SPatient.SPatientDisability
ORDER BY ServiceConnectedPercent DESC;
```

**Deliverables:**
- [ ] Updated `mock/sql-server/cdwwork/insert/SPatient.SPatientDisability.sql` with 30 records
- [ ] SQL Server table updated with new data
- [ ] Verification queries confirm correct counts and distribution

---

## Phase 2: New Table & ETL Pipeline

**Goal:** Create `clinical.patient_military_history` table and complete ETL pipeline to populate it with all disability fields.

**Time Estimate:** 6-8 hours

---

### Task 2.1: Create PostgreSQL Schema

**New File:** `db/ddl/create_patient_military_history_table.sql`

**Copy/Paste Code:**

```sql
-- ---------------------------------------------------------------------
-- create_patient_military_history_table.sql
-- ---------------------------------------------------------------------
-- Create patient_military_history table in PostgreSQL for med-z1 serving DB
-- This table stores military service history and environmental exposures
-- ---------------------------------------------------------------------
-- Version History:
--   v1.0 (2026-02-06): Initial schema - Military History Enhancement
-- ---------------------------------------------------------------------

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (for development - use migrations in production)
DROP TABLE IF EXISTS clinical.patient_military_history CASCADE;

-- Create patient military history table
CREATE TABLE clinical.patient_military_history (
    patient_key VARCHAR(50) PRIMARY KEY,
    icn VARCHAR(50) NOT NULL,

    -- Service Connection
    service_connected_flag CHAR(1),
    service_connected_percent DECIMAL(5,2),

    -- Environmental Exposures
    agent_orange_exposure CHAR(1),
    agent_orange_location VARCHAR(50),
    ionizing_radiation CHAR(1),
    pow_status CHAR(1),
    pow_location VARCHAR(50),
    shad_flag CHAR(1),  -- Shipboard Hazard and Defense
    sw_asia_exposure CHAR(1),  -- Southwest Asia (Gulf War)
    camp_lejeune_flag CHAR(1),

    -- Metadata
    source_system VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_military_history_icn ON clinical.patient_military_history(icn);
CREATE INDEX idx_military_history_sc_percent ON clinical.patient_military_history(service_connected_percent);
CREATE INDEX idx_military_history_agent_orange ON clinical.patient_military_history(agent_orange_exposure) WHERE agent_orange_exposure = 'Y';
CREATE INDEX idx_military_history_pow ON clinical.patient_military_history(pow_status) WHERE pow_status = 'Y';
CREATE INDEX idx_military_history_gulf_war ON clinical.patient_military_history(sw_asia_exposure) WHERE sw_asia_exposure = 'Y';

-- Add comments for documentation
COMMENT ON TABLE clinical.patient_military_history IS 'Patient military service history and environmental exposures from Gold layer';
COMMENT ON COLUMN clinical.patient_military_history.patient_key IS 'Internal unique identifier (currently same as ICN)';
COMMENT ON COLUMN clinical.patient_military_history.service_connected_flag IS 'Y=Service Connected, N=Not Service Connected';
COMMENT ON COLUMN clinical.patient_military_history.service_connected_percent IS 'VA disability rating percentage (0-100)';
COMMENT ON COLUMN clinical.patient_military_history.agent_orange_exposure IS 'Y=Exposed to Agent Orange (Vietnam era), N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.agent_orange_location IS 'Location of Agent Orange exposure (e.g., VIETNAM)';
COMMENT ON COLUMN clinical.patient_military_history.ionizing_radiation IS 'Y=Exposed to ionizing radiation, N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.pow_status IS 'Y=Former Prisoner of War, N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.pow_location IS 'Location of POW captivity';
COMMENT ON COLUMN clinical.patient_military_history.shad_flag IS 'Shipboard Hazard and Defense exposure flag';
COMMENT ON COLUMN clinical.patient_military_history.sw_asia_exposure IS 'Y=Southwest Asia (Gulf War) service, N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.camp_lejeune_flag IS 'Y=Camp Lejeune water contamination exposure, N=No';

-- Verify table creation
SELECT 'patient_military_history table created successfully in clinical schema (v1.0)' AS status;
```

**Apply to PostgreSQL:**

```bash
# From project root
docker exec -i postgres16 psql -U postgres -d medz1 \
  < db/ddl/create_patient_military_history_table.sql
```

### Task 2.2: Update Silver Layer ETL

**Modify File:** `etl/silver_patient.py`

**Current Code (lines 169-177):**
```python
# Select service connected percent from disability (Phase 2)
# Logic: One record per patient (most recent if multiple exist)
df_service_connected = (
    df_disability
    .select([
        pl.col("PatientSID").alias("patient_sid_disability"),
        pl.col("ServiceConnectedPercent").alias("service_connected_percent"),
    ])
    .unique(subset=["patient_sid_disability"])
)
```

**Replace With:**
```python
# Select service connected data from disability (Phase 2, expanded Phase 4)
# Logic: One record per patient (most recent if multiple exist)
# NOTE: Full disability data now extracted for new patient_military_history table
df_service_connected = (
    df_disability
    .select([
        pl.col("PatientSID").alias("patient_sid_disability"),
        pl.col("ServiceConnectedPercent").alias("service_connected_percent"),  # Keep for demographics table
    ])
    .unique(subset=["patient_sid_disability"])
)
logger.info(f"Selected {len(df_service_connected)} service connected records for demographics")
```

**Note:** The existing `silver_patient.py` logic can remain unchanged for now since it only populates `clinical.patient_demographics.service_connected_percent`. We'll create a separate Silver transformation for the new table.

### Task 2.3: Create New Silver ETL Script

**New File:** `etl/silver_patient_military_history.py`

**Copy/Paste Code:**

```python
# ---------------------------------------------------------------------
# etl/silver_patient_military_history.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version for military history
#  - read from med-z1/bronze/cdwwork/patient_disability
#  - read from med-z1/bronze/cdwwork/patient (for ICN resolution)
#  - join and transform data
#  - save to med-z1/silver/patient_military_history as military_history_cleaned.parquet
# ---------------------------------------------------------------------
# Version History:
#   v1.0 (2026-02-06): Initial Silver transformation - Military History Enhancement
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a module:
#  $ cd med-z1
#  $ python -m etl.silver_patient_military_history
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def transform_military_history_silver():
    """Transform Bronze patient disability data to Silver layer for military history."""

    logger.info("Starting Silver patient military history transformation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Bronze Patient Parquet from MinIO (for ICN resolution)
    patient_path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
    df_patient = minio_client.read_parquet(patient_path)
    logger.info(f"Bronze patient data read: {len(df_patient)} records")

    # Read Bronze Patient Disability Parquet from MinIO
    disability_path = build_bronze_path("cdwwork", "patient_disability", "patient_disability_raw.parquet")
    df_disability = minio_client.read_parquet(disability_path)
    logger.info(f"Bronze patient disability data read: {len(df_disability)} records")

    # Transform and clean disability data
    df_disability_cleaned = df_disability.with_columns([
        # Standardize field names
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("ServiceConnectedFlag").str.strip_chars().alias("service_connected_flag"),
        pl.col("ServiceConnectedPercent").alias("service_connected_percent"),

        # Environmental exposures
        pl.col("AgentOrangeExposureCode").str.strip_chars().alias("agent_orange_exposure"),
        pl.col("AgentOrangeLocation").str.strip_chars().alias("agent_orange_location"),
        pl.col("IonizingRadiationCode").str.strip_chars().alias("ionizing_radiation"),
        pl.col("POWStatusCode").str.strip_chars().alias("pow_status"),
        pl.col("POWLocation").str.strip_chars().alias("pow_location"),
        pl.col("SHADFlag").str.strip_chars().alias("shad_flag"),
        pl.col("SWAsiaCode").str.strip_chars().alias("sw_asia_exposure"),
        pl.col("CampLejeuneFlag").str.strip_chars().alias("camp_lejeune_flag"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
    ])

    # Deduplicate: One record per patient (most recent if multiple exist)
    df_disability_cleaned = df_disability_cleaned.unique(subset=["patient_sid"])
    logger.info(f"After deduplication: {len(df_disability_cleaned)} military history records")

    # Join with patient data to get ICN
    df_patient_icn = df_patient.select([
        pl.col("PatientSID"),
        pl.col("PatientICN").alias("icn"),
    ])

    df = df_disability_cleaned.join(
        df_patient_icn,
        left_on="patient_sid",
        right_on="PatientSID",
        how="inner"  # Only keep disability records with valid patient ICN
    )
    logger.info(f"After ICN join: {len(df)} military history records")

    # Add timestamp
    df = df.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Select final columns
    df = df.select([
        "patient_sid",
        "icn",
        "service_connected_flag",
        "service_connected_percent",
        "agent_orange_exposure",
        "agent_orange_location",
        "ionizing_radiation",
        "pow_status",
        "pow_location",
        "shad_flag",
        "sw_asia_exposure",
        "camp_lejeune_flag",
        "source_system",
        "last_updated",
    ])

    # Build Silver path
    silver_path = build_silver_path("patient_military_history", "military_history_cleaned.parquet")

    # Write to MinIO
    minio_client.write_parquet(df, silver_path)
    logger.info("Silver Parquet file written to MinIO")

    logger.info(
        f"Silver transformation complete: {len(df)} military history records written to "
        f"s3://{minio_client.bucket_name}/{silver_path}"
    )

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_military_history_silver()
```

### Task 2.4: Create Gold ETL Script

**New File:** `etl/gold_patient_military_history.py`

**Copy/Paste Code:**

```python
# ---------------------------------------------------------------------
# etl/gold_patient_military_history.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver version
#  - read from med-z1/silver/patient_military_history
#  - save to med-z1/gold/patient_military_history as military_history.parquet
# ---------------------------------------------------------------------
# Version History:
#   v1.0 (2026-02-06): Initial Gold transformation - Military History Enhancement
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a module:
#  $ cd med-z1
#  $ python -m etl.gold_patient_military_history
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def create_gold_military_history():
    """Create Gold patient military history view in MinIO."""

    logger.info("Starting Gold patient military history creation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Silver Parquet from MinIO
    silver_path = build_silver_path("patient_military_history", "military_history_cleaned.parquet")
    df_military = minio_client.read_parquet(silver_path)
    logger.info(f"Silver military history data read: {len(df_military)} records")

    # Create patient_key (use ICN)
    df_military = df_military.with_columns([
        pl.col("icn").alias("patient_key")
    ])

    # Final Gold schema
    df_gold = df_military.select([
        "patient_key",
        "patient_sid",  # Keep for potential joins
        "icn",
        "service_connected_flag",
        "service_connected_percent",
        "agent_orange_exposure",
        "agent_orange_location",
        "ionizing_radiation",
        "pow_status",
        "pow_location",
        "shad_flag",
        "sw_asia_exposure",
        "camp_lejeune_flag",
        "source_system",
        "last_updated",
    ])

    # Build Gold path
    gold_path = build_gold_path(
        "patient_military_history",
        "military_history.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df_gold, gold_path)

    logger.info(
        f"Gold creation complete: {len(df_gold)} military history records written to "
        f"s3://{minio_client.bucket_name}/{gold_path}"
    )

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    create_gold_military_history()
```

### Task 2.5: Create Load Script

**New File:** `etl/load_military_history.py`

**Copy/Paste Code:**

```python
# ---------------------------------------------------------------------
# etl/load_military_history.py
# ---------------------------------------------------------------------
# Load PostgreSQL DB with Gold layer patient military history data
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a module:
#  $ cd med-z1
#  $ python -m etl.load_military_history
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from sqlalchemy import create_engine, text
import logging
from config import DATABASE_URL  # PostgreSQL connection string
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_military_history_to_postgres():
    """Load Gold patient military history from MinIO to PostgreSQL."""

    logger.info("Loading patient military history to PostgreSQL...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Gold Parquet from MinIO
    gold_path = build_gold_path(
        "patient_military_history",
        "military_history.parquet"
    )
    df = minio_client.read_parquet(gold_path)

    logger.info(f"Read {len(df)} military history records from Gold layer")

    # Convert Polars to Pandas (for SQLAlchemy compatibility)
    df_pandas = df.to_pandas()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load to PostgreSQL (truncate and reload)
    df_pandas.to_sql(
        "patient_military_history",
        engine,
        schema="clinical",
        if_exists="replace",
        index=False,
        method="multi",
    )

    logger.info(f"Loaded {len(df)} military history records to PostgreSQL")

    # Verify
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_military_history")).fetchone()
        logger.info(f"Verification: {result[0]} rows in patient_military_history table")

        # Summary stats
        result = conn.execute(text("""
            SELECT
                COUNT(*) as total_records,
                SUM(CASE WHEN service_connected_flag = 'Y' THEN 1 ELSE 0 END) as service_connected_count,
                SUM(CASE WHEN agent_orange_exposure = 'Y' THEN 1 ELSE 0 END) as agent_orange_count,
                SUM(CASE WHEN pow_status = 'Y' THEN 1 ELSE 0 END) as pow_count,
                SUM(CASE WHEN sw_asia_exposure = 'Y' THEN 1 ELSE 0 END) as gulf_war_count,
                SUM(CASE WHEN camp_lejeune_flag = 'Y' THEN 1 ELSE 0 END) as camp_lejeune_count
            FROM clinical.patient_military_history
        """)).fetchone()
        logger.info(f"Summary: {result[1]} service connected, {result[2]} Agent Orange, "
                   f"{result[3]} POW, {result[4]} Gulf War, {result[5]} Camp Lejeune")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_military_history_to_postgres()
```

### Task 2.6: Run Complete ETL Pipeline

**Commands:**

```bash
# From project root

# 1. Run Bronze extraction (already complete - extracts all fields)
python -m etl.bronze_patient_disability

# 2. Run Silver transformation (new military history script)
python -m etl.silver_patient_military_history

# 3. Run Gold transformation
python -m etl.gold_patient_military_history

# 4. Apply PostgreSQL schema
docker exec -i postgres16 psql -U postgres -d medz1 \
  < db/ddl/create_patient_military_history_table.sql

# 5. Load to PostgreSQL
python -m etl.load_military_history
```

### Task 2.7: Verify PostgreSQL Data

**Verification SQL:**

```sql
-- Connect to PostgreSQL and run these queries

-- 1. Total records
SELECT COUNT(*) as total_records
FROM clinical.patient_military_history;
-- Expected: 30 records

-- 2. Service connected distribution
SELECT
    service_connected_percent,
    COUNT(*) as patient_count
FROM clinical.patient_military_history
GROUP BY service_connected_percent
ORDER BY service_connected_percent;

-- 3. Environmental exposures summary
SELECT
    COUNT(*) as total_records,
    SUM(CASE WHEN agent_orange_exposure = 'Y' THEN 1 ELSE 0 END) as agent_orange,
    SUM(CASE WHEN ionizing_radiation = 'Y' THEN 1 ELSE 0 END) as radiation,
    SUM(CASE WHEN pow_status = 'Y' THEN 1 ELSE 0 END) as pow,
    SUM(CASE WHEN camp_lejeune_flag = 'Y' THEN 1 ELSE 0 END) as camp_lejeune,
    SUM(CASE WHEN sw_asia_exposure = 'Y' THEN 1 ELSE 0 END) as gulf_war
FROM clinical.patient_military_history;

-- 4. Sample data spot-check
SELECT
    icn,
    service_connected_percent,
    agent_orange_exposure,
    pow_status,
    sw_asia_exposure
FROM clinical.patient_military_history
WHERE service_connected_percent >= 70
ORDER BY service_connected_percent DESC;

-- 5. Join test with demographics
SELECT
    d.icn,
    d.name_display,
    m.service_connected_percent,
    m.agent_orange_exposure,
    m.sw_asia_exposure
FROM clinical.patient_demographics d
LEFT JOIN clinical.patient_military_history m ON d.patient_key = m.patient_key
LIMIT 10;
```

**Deliverables:**
- [ ] `db/ddl/create_patient_military_history_table.sql`
- [ ] `etl/silver_patient_military_history.py`
- [ ] `etl/gold_patient_military_history.py`
- [ ] `etl/load_military_history.py`
- [ ] PostgreSQL table populated with 30 records
- [ ] Verification queries confirm correct data

---

## Phase 3: UI Enhancements

**Goal:** Update Demographics page to display environmental exposures with badges, priority indicators, and tooltips.

**Time Estimate:** 4-5 hours

---

### Task 3.1: Create Database Query Function

**New File:** `app/db/military_history.py`

**Copy/Paste Code:**

```python
# ---------------------------------------------------------------------
# app/db/military_history.py
# ---------------------------------------------------------------------
# Database query functions for patient military history
# ---------------------------------------------------------------------

from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)


def get_patient_military_history(icn: str) -> Optional[Dict[str, Any]]:
    """
    Get military history for a specific patient by ICN.

    Args:
        icn: Patient ICN (Integrated Care Number)

    Returns:
        Dictionary with military history data, or None if not found

    Example:
        {
            'service_connected_flag': 'Y',
            'service_connected_percent': 70.0,
            'agent_orange_exposure': 'Y',
            'agent_orange_location': 'VIETNAM',
            'ionizing_radiation': 'N',
            'pow_status': 'N',
            'pow_location': None,
            'shad_flag': 'N',
            'sw_asia_exposure': 'Y',
            'camp_lejeune_flag': 'N',
        }
    """
    engine = create_engine(DATABASE_URL)

    query = text("""
        SELECT
            patient_key,
            icn,
            service_connected_flag,
            service_connected_percent,
            agent_orange_exposure,
            agent_orange_location,
            ionizing_radiation,
            pow_status,
            pow_location,
            shad_flag,
            sw_asia_exposure,
            camp_lejeune_flag,
            source_system,
            last_updated
        FROM clinical.patient_military_history
        WHERE icn = :icn
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn}).fetchone()

        if not result:
            logger.debug(f"No military history found for patient ICN: {icn}")
            return None

        return {
            "patient_key": result[0],
            "icn": result[1],
            "service_connected_flag": result[2],
            "service_connected_percent": float(result[3]) if result[3] is not None else None,
            "agent_orange_exposure": result[4],
            "agent_orange_location": result[5],
            "ionizing_radiation": result[6],
            "pow_status": result[7],
            "pow_location": result[8],
            "shad_flag": result[9],
            "sw_asia_exposure": result[10],
            "camp_lejeune_flag": result[11],
            "source_system": result[12],
            "last_updated": result[13],
        }


def get_priority_group(service_connected_percent: Optional[float]) -> Dict[str, Any]:
    """
    Determine VA priority group based on service-connected percentage.

    Args:
        service_connected_percent: Service-connected disability percentage (0-100)

    Returns:
        Dictionary with priority group info

    Example:
        {
            'group': '1',
            'label': 'Priority Group 1',
            'badge_class': 'badge--danger',
            'description': 'High priority - 70%+ service connected'
        }
    """
    if service_connected_percent is None:
        return {
            'group': None,
            'label': None,
            'badge_class': None,
            'description': None
        }

    if service_connected_percent >= 70:
        return {
            'group': '1',
            'label': 'Priority Group 1',
            'badge_class': 'badge--danger',
            'description': 'High priority - 70%+ service connected'
        }
    elif service_connected_percent >= 50:
        return {
            'group': '2',
            'label': 'Priority Group 2',
            'badge_class': 'badge--warning',
            'description': 'Priority - 50-69% service connected'
        }
    elif service_connected_percent >= 30:
        return {
            'group': '3',
            'label': 'Priority Group 3',
            'badge_class': 'badge--info',
            'description': 'Standard - 30-49% service connected'
        }
    elif service_connected_percent >= 10:
        return {
            'group': '4-6',
            'label': 'Priority Group 4-6',
            'badge_class': 'badge--secondary',
            'description': 'Standard - 10-29% service connected'
        }
    else:
        return {
            'group': '7-8',
            'label': 'Priority Group 7-8',
            'badge_class': 'badge--secondary',
            'description': 'Standard eligibility'
        }
```

### Task 3.2: Update Demographics Route

**Modify File:** `app/routes/demographics.py`

**Add import at top:**
```python
from app.db.military_history import get_patient_military_history, get_priority_group
```

**Modify the `get_patient_demographics_page` function (lines 24-64):**

**Current code:**
```python
@page_router.get("/patient/{icn}/demographics", response_class=HTMLResponse)
async def get_patient_demographics_page(request: Request, icn: str):
    """..."""
    logger.info(f"Demographics page requested for patient ICN: {icn}")

    # Get patient demographics from database
    patient = get_patient_demographics(icn)

    if not patient:
        logger.warning(f"Patient not found for ICN: {icn}")
        raise HTTPException(status_code=404, detail="Patient not found")

    # Render full demographics page template
    return templates.TemplateResponse(
        "patient_demographics.html",
        get_base_context(
            request,
            patient=patient,
            active_page="demographics"
        )
    )
```

**Replace with:**
```python
@page_router.get("/patient/{icn}/demographics", response_class=HTMLResponse)
async def get_patient_demographics_page(request: Request, icn: str):
    """
    Full Demographics page for a specific patient.

    Displays comprehensive demographic information including:
    - Basic demographics (name, DOB, age, sex, SSN, ICN)
    - Contact information (phone, address)
    - Insurance information
    - Marital status, religion
    - Service connected percentage with priority group
    - Environmental exposures (Agent Orange, radiation, POW, etc.)
    - Deceased status and date (if applicable)

    Args:
        request: FastAPI Request object
        icn: Patient ICN

    Returns:
        HTMLResponse with patient demographics page

    Raises:
        HTTPException: 404 if patient not found
    """
    logger.info(f"Demographics page requested for patient ICN: {icn}")

    # Get patient demographics from database
    patient = get_patient_demographics(icn)

    if not patient:
        logger.warning(f"Patient not found for ICN: {icn}")
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get military history (if available)
    military_history = get_patient_military_history(icn)

    # Determine priority group based on service connected percentage
    priority_group = None
    if military_history and military_history.get('service_connected_percent') is not None:
        priority_group = get_priority_group(military_history['service_connected_percent'])

    # Render full demographics page template
    return templates.TemplateResponse(
        "patient_demographics.html",
        get_base_context(
            request,
            patient=patient,
            military_history=military_history,
            priority_group=priority_group,
            active_page="demographics"
        )
    )
```

### Task 3.3: Update Demographics Template

**Modify File:** `app/templates/patient_demographics.html`

**Replace Section 4 (lines 118-136) with enhanced version:**

```html
        <!-- Section 4: Military Service & Eligibility -->
        <div class="demo-section-card">
            <h2 class="demo-section-card__title">
                <i class="fa-solid fa-flag-usa"></i>
                Military Service & Eligibility
            </h2>
            <div class="demo-grid">
                <div class="demo-field">
                    <span class="demo-field__label">
                        Service Connected %
                        <i class="fa-solid fa-circle-info demo-tooltip"
                           title="Percentage of disability related to military service. Affects care priority and benefits eligibility."
                           style="color: var(--color-gray-500); cursor: help; margin-left: 4px;">
                        </i>
                    </span>
                    <span class="demo-field__value">
                        {% if military_history and military_history.service_connected_percent is not none %}
                            {{ military_history.service_connected_percent|int }}%

                            <!-- Priority Group Badge -->
                            {% if priority_group and priority_group.group %}
                            <span class="badge {{ priority_group.badge_class }}"
                                  style="margin-left: 8px;"
                                  title="{{ priority_group.description }}">
                                {{ priority_group.label }}
                            </span>
                            {% endif %}
                        {% else %}
                            Not Available
                        {% endif %}
                    </span>
                </div>

                <!-- Environmental Exposures -->
                {% if military_history %}
                <div class="demo-field demo-field--full-width">
                    <span class="demo-field__label">
                        Environmental Exposures
                        <i class="fa-solid fa-circle-info demo-tooltip"
                           title="Known exposures during military service that may affect health. Important for screening and monitoring."
                           style="color: var(--color-gray-500); cursor: help; margin-left: 4px;">
                        </i>
                    </span>
                    <span class="demo-field__value">
                        <div class="exposure-badges" style="display: flex; gap: 8px; flex-wrap: wrap;">
                            {% if military_history.agent_orange_exposure == 'Y' %}
                            <span class="badge badge--warning"
                                  title="Agent Orange exposure ({{ military_history.agent_orange_location or 'Location unknown' }})">
                                <i class="fa-solid fa-leaf"></i> Agent Orange
                            </span>
                            {% endif %}

                            {% if military_history.ionizing_radiation == 'Y' %}
                            <span class="badge badge--danger"
                                  title="Ionizing radiation exposure - increased cancer risk, special monitoring required">
                                <i class="fa-solid fa-radiation"></i> Radiation
                            </span>
                            {% endif %}

                            {% if military_history.pow_status == 'Y' %}
                            <span class="badge badge--danger"
                                  title="Former Prisoner of War ({{ military_history.pow_location or 'Location unknown' }}) - special benefits and care">
                                <i class="fa-solid fa-handcuffs"></i> Former POW
                            </span>
                            {% endif %}

                            {% if military_history.camp_lejeune_flag == 'Y' %}
                            <span class="badge badge--warning"
                                  title="Camp Lejeune water contamination exposure (1953-1987) - linked to specific cancers">
                                <i class="fa-solid fa-droplet"></i> Camp Lejeune
                            </span>
                            {% endif %}

                            {% if military_history.sw_asia_exposure == 'Y' %}
                            <span class="badge badge--info"
                                  title="Gulf War / Southwest Asia service - potential burn pit exposure and Gulf War Illness">
                                <i class="fa-solid fa-fire"></i> Gulf War
                            </span>
                            {% endif %}

                            {% if military_history.shad_flag == 'Y' %}
                            <span class="badge badge--info"
                                  title="Shipboard Hazard and Defense exposure">
                                <i class="fa-solid fa-ship"></i> SHAD
                            </span>
                            {% endif %}

                            <!-- No exposures message -->
                            {% if military_history.agent_orange_exposure != 'Y'
                               and military_history.ionizing_radiation != 'Y'
                               and military_history.pow_status != 'Y'
                               and military_history.camp_lejeune_flag != 'Y'
                               and military_history.sw_asia_exposure != 'Y'
                               and military_history.shad_flag != 'Y' %}
                            <span style="color: var(--color-gray-600); font-style: italic;">
                                No documented exposures
                            </span>
                            {% endif %}
                        </div>
                    </span>
                </div>
                {% endif %}
            </div>
        </div>
```

### Task 3.4: Add CSS Styles

**Modify File:** `app/static/styles.css`

**Add these styles (search for existing badge styles and add near them):**

```css
/* =================================================================
   Environmental Exposure Badges
   ================================================================= */

.exposure-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.813rem;
    font-weight: 600;
    line-height: 1.2;
    white-space: nowrap;
}

.badge--danger {
    background-color: var(--color-error-light);
    color: var(--color-error-dark);
    border: 1px solid var(--color-error);
}

.badge--warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffc107;
}

.badge--info {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #17a2b8;
}

.badge--secondary {
    background-color: var(--color-gray-100);
    color: var(--color-gray-700);
    border: 1px solid var(--color-gray-300);
}

.badge i {
    font-size: 0.875rem;
}

/* Tooltip icon styling */
.demo-tooltip {
    cursor: help;
    color: var(--color-gray-500);
    margin-left: 4px;
    font-size: 0.875rem;
}

.demo-tooltip:hover {
    color: var(--color-primary);
}
```

### Task 3.5: Test UI

**Manual Testing Checklist:**

```bash
# 1. Start application
uvicorn app.main:app --reload

# 2. Navigate to demographics page for patients with military history
# Test URLs:
http://127.0.0.1:8000/patient/ICN100001/demographics  # 70% SC, Agent Orange
http://127.0.0.1:8000/patient/ICN100007/demographics  # 100% SC, Former POW
http://127.0.0.1:8000/patient/ICN100010/demographics  # 90% SC, Gulf War
http://127.0.0.1:8000/patient/ICN100006/demographics  # 60% SC, Camp Lejeune
http://127.0.0.1:8000/patient/ICN100005/demographics  # 0% SC (evaluated but not connected)

# 3. Verify display elements:
# [ ] Service connected percentage displays correctly
# [ ] Priority group badge shows with correct color
# [ ] Tooltip appears on hover for SC% label
# [ ] Environmental exposure badges display correctly
# [ ] Badge colors match exposure type (warning/danger/info)
# [ ] Tooltip appears on hover for exposure badges
# [ ] "No documented exposures" message shows for patients without exposures
# [ ] Layout is responsive (test mobile/tablet views)
```

**Deliverables:**
- [ ] `app/db/military_history.py`
- [ ] Updated `app/routes/demographics.py`
- [ ] Updated `app/templates/patient_demographics.html`
- [ ] Updated `app/static/styles.css`
- [ ] Manual testing checklist completed
- [ ] Screenshots for documentation

---

## Phase 4: AI Integration

**Goal:** Update PatientContextBuilder to include environmental exposures in patient summaries sent to LLM.

**Time Estimate:** 2-3 hours

---

### Task 4.1: Update AI Context Builder

**Modify File:** `ai/services/patient_context.py`

**Add import at top (around line 24):**
```python
from app.db.military_history import get_patient_military_history
```

**Modify `get_demographics_summary` method (around lines 65-118):**

**Find this section:**
```python
# Add service-connected percentage if available
sc_pct = demo.get('service_connected_percent')
if sc_pct is not None:
    text += f", service-connected disability {int(sc_pct)}%"

# Add primary care station
station_name = demo.get('primary_station_name')
if station_name:
    text += f"\nPrimary care: {station_name}"
```

**Replace with:**
```python
# Add service-connected percentage and exposures if available
military_history = get_patient_military_history(self.icn)
if military_history:
    sc_pct = military_history.get('service_connected_percent')
    if sc_pct is not None:
        text += f", service-connected disability {int(sc_pct)}%"

        # Add priority context for high-priority veterans
        if sc_pct >= 70:
            text += " (high priority care)"

    # Add environmental exposures
    exposures = []
    if military_history.get('agent_orange_exposure') == 'Y':
        location = military_history.get('agent_orange_location')
        if location:
            exposures.append(f"Agent Orange ({location})")
        else:
            exposures.append("Agent Orange")

    if military_history.get('ionizing_radiation') == 'Y':
        exposures.append("ionizing radiation")

    if military_history.get('pow_status') == 'Y':
        location = military_history.get('pow_location')
        if location:
            exposures.append(f"Former POW ({location})")
        else:
            exposures.append("Former POW")

    if military_history.get('camp_lejeune_flag') == 'Y':
        exposures.append("Camp Lejeune water contamination")

    if military_history.get('sw_asia_exposure') == 'Y':
        exposures.append("Gulf War service")

    if military_history.get('shad_flag') == 'Y':
        exposures.append("SHAD (shipboard hazard)")

    if exposures:
        text += f"\nEnvironmental exposures: {', '.join(exposures)}"

# Add primary care station
station_name = demo.get('primary_station_name')
if station_name:
    text += f"\nPrimary care: {station_name}"
```

### Task 4.2: Test AI Integration

**Test Script:** `scripts/test_ai_military_context.py`

**Copy/Paste Code:**

```python
"""
Test AI integration with military history data.
Tests that PatientContextBuilder includes environmental exposures.
"""

from ai.services.patient_context import PatientContextBuilder

# Test patients with different exposure profiles
test_patients = [
    ("ICN100001", "Adam Dooree - Agent Orange exposure"),
    ("ICN100007", "Adam Amajor - Former POW"),
    ("ICN100010", "Alexander Aminor - Gulf War veteran"),
    ("ICN100006", "Francine Miifaa - Camp Lejeune exposure"),
    ("ICN100005", "Edward Dooree - 0% service connected"),
]

print("=" * 80)
print("AI Military History Context Test")
print("=" * 80)

for icn, description in test_patients:
    print(f"\n{'=' * 80}")
    print(f"Patient: {description}")
    print(f"ICN: {icn}")
    print(f"{'=' * 80}\n")

    builder = PatientContextBuilder(icn)
    demographics = builder.get_demographics_summary()

    print(demographics)
    print()

    # Verify exposure mentions
    if "Agent Orange" in demographics:
        print("✅ Agent Orange exposure detected in context")
    if "Former POW" in demographics:
        print("✅ POW status detected in context")
    if "Gulf War" in demographics:
        print("✅ Gulf War exposure detected in context")
    if "Camp Lejeune" in demographics:
        print("✅ Camp Lejeune exposure detected in context")
    if "high priority care" in demographics:
        print("✅ High priority care indicator detected")

print("\n" + "=" * 80)
print("Test complete")
print("=" * 80)
```

**Run test:**
```bash
python scripts/test_ai_military_context.py
```

**Expected Output Examples:**

```
Patient: Adam Dooree - Agent Orange exposure
ICN: ICN100001
================================================================================

Patient Name: Dooree, Adam
45-year-old male veteran (DOB: 1979-05-15), service-connected disability 70% (high priority care)
Environmental exposures: Agent Orange (VIETNAM)
Primary care: Atlanta, GA VA Medical Center
Address: Atlanta, GA 30301

✅ Agent Orange exposure detected in context
✅ High priority care indicator detected
```

### Task 4.3: Test AI Queries

**Manual Test in UI:**

1. Navigate to: `http://127.0.0.1:8000/insight`
2. Select patient: ICN100001 (Adam Dooree - Agent Orange)
3. Ask: "What environmental exposures does this patient have?"
4. Expected response should mention Agent Orange and Vietnam service
5. Ask: "What special health considerations apply to this veteran?"
6. Expected response should reference service-connected disability and exposure risks

**Deliverables:**
- [ ] Updated `ai/services/patient_context.py`
- [ ] Test script `scripts/test_ai_military_context.py`
- [ ] AI query test results documented
- [ ] Verification that exposures appear in AI responses

---

## 6. Testing Strategy

### 6.1 Unit Tests

**File:** `tests/test_military_history.py` (create if needed)

**Coverage Areas:**
```python
def test_get_patient_military_history_found()
def test_get_patient_military_history_not_found()
def test_get_priority_group_high_70_percent()
def test_get_priority_group_medium_50_percent()
def test_get_priority_group_low_30_percent()
def test_get_priority_group_minimal_10_percent()
def test_get_priority_group_zero_percent()
def test_get_priority_group_none()
```

### 6.2 Integration Tests

**Coverage Areas:**
1. **ETL Pipeline** (`tests/test_etl_military_history.py`):
   - Bronze extraction includes all 14 fields
   - Silver transformation cleans and joins correctly
   - Gold transformation creates patient_key
   - Load populates PostgreSQL correctly

2. **API Endpoints** (`tests/test_demographics_military.py`):
   - Demographics page includes military history
   - Priority group badge displays correctly
   - Exposure badges display correctly

3. **AI Integration** (`tests/test_ai_military_context.py`):
   - PatientContextBuilder includes exposures
   - AI responses reference military history

### 6.3 Manual Testing Checklist

**Data Pipeline:**
- [ ] 30 disability records in SQL Server
- [ ] Bronze Parquet contains 30 records with all 14 fields
- [ ] Silver Parquet contains 30 records with cleaned data
- [ ] Gold Parquet contains 30 records with patient_key
- [ ] PostgreSQL table contains 30 records
- [ ] Exposure flags match source data

**UI Display:**
- [ ] Service connected percentage displays correctly
- [ ] Priority group badges show correct colors
- [ ] Environmental exposure badges display
- [ ] Tooltips appear on hover
- [ ] "No documented exposures" message shows correctly
- [ ] Layout responsive on mobile/tablet
- [ ] Patients without military history show "Not Available"

**AI Integration:**
- [ ] Demographics summary includes exposures
- [ ] High priority care indicator shows for 70%+
- [ ] AI queries about exposures work correctly
- [ ] Patient summaries reference military context

---

## 7. Future Enhancements

### 7.1 Additional Military History Fields (Phase 5+)

**Potential Expansions:**
- Service dates (enlistment, discharge)
- Branch of service (Army, Navy, Air Force, Marines, Coast Guard)
- Rank at discharge
- Deployment locations and dates
- Combat zones
- Awards and decorations
- Character of discharge (Honorable, General, etc.)

**Database Schema Extension:**
```sql
ALTER TABLE clinical.patient_military_history ADD COLUMN
    service_start_date DATE,
    service_end_date DATE,
    branch_of_service VARCHAR(50),
    rank_at_discharge VARCHAR(50),
    deployment_locations TEXT,  -- JSON or comma-separated
    combat_veteran_flag CHAR(1),
    character_of_discharge VARCHAR(50);
```

### 7.2 Dashboard Widget Enhancement

**Potential Addition:**
- Small military history widget on dashboard
- Shows service-connected percentage
- Shows exposure badges (compact view)
- Links to full demographics page

**Widget Mockup:**
```html
<div class="widget widget--1x1">
    <div class="widget__header">
        <i class="fa-solid fa-flag-usa"></i>
        <h3 class="widget__title">Military History</h3>
    </div>
    <div class="widget__body">
        <div class="military-summary">
            <div class="sc-percent-display">
                <span class="sc-value">70%</span>
                <span class="sc-label">Service Connected</span>
            </div>
            <div class="exposure-badges-compact">
                <span class="badge badge--warning">Agent Orange</span>
                <span class="badge badge--info">Gulf War</span>
            </div>
        </div>
    </div>
</div>
```

### 7.3 Advanced AI Queries

**Potential AI Tool Enhancements:**
- `check_exposure_related_conditions()` - Screen for exposure-related diseases
- `get_va_benefits_eligibility()` - Explain benefits based on disability rating
- `recommend_preventive_screening()` - Suggest screenings based on exposures

**Example AI Query:**
```
User: "What preventive screenings should this patient have based on military history?"

AI Response (with exposure context):
"Based on Adam Dooree's Agent Orange exposure during Vietnam service, recommend:
1. Annual diabetes screening (Agent Orange-related risk)
2. Cardiovascular monitoring (increased heart disease risk)
3. Prostate cancer screening starting age 50 (elevated risk)
4. Respiratory evaluation if symptoms present
5. PTSD screening (combat veteran)"
```

### 7.4 Real-Time Vista Integration

**Future Enhancement:**
- Query real-time military history from VistA (File #2)
- Merge with CDW data for comprehensive view
- Handle discrepancies between sources
- Refresh button for latest data

---

**End of Implementation Plan**

---

## Document Approval

**Prepared By:** Claude (AI Assistant)
**Date:** February 6, 2026
**Reviewed By:** [Pending]
**Approved By:** [Pending]

**Change Log:**
- v1.0 (2026-02-06): Initial design specification created
