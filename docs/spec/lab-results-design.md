# Laboratory Results Design Specification - med-z1

**Document Version:** v1.1
**Date:** December 16, 2025
**Status:** ETL Complete, UI Pending
**Implementation Phase:** ✅ ETL Complete (Bronze/Silver/Gold/Load), 🚧 UI Pending
**Current Scope:** Chemistry Labs Only (Phase 1)

**Changelog:**
- **v1.1 (December 16, 2025):** Updated status to reflect ETL completion. All 4 pipeline stages operational (Bronze/Silver/Gold/Load) with 58 lab results in PostgreSQL. UI implementation (widget + full page) pending next phase.
- **v1.0 (December 16, 2025):** Initial design specification

**Implementation Status Source:** `docs/spec/implementation-status.md`

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
11. [Future Enhancements](#11-future-enhancements)
12. [Appendices](#12-appendices)

---

## 1. Overview

### 1.1 Purpose

The **Laboratory Results** domain provides comprehensive access to patient laboratory data, enabling clinicians to:
- View recent lab panels at a glance (dashboard widget - **first 3x1 full-width widget**)
- Review complete lab history with trending (full lab results page)
- Identify abnormal values and critical results
- Track lab trends over time for chronic disease management
- Support clinical decision-making with comprehensive laboratory data

Laboratory data is sourced from VistA File #63 (LAB DATA) and flows into CDW as individual atomic results. Results are grouped by panels (e.g., BMP, CBC, CMP) using AccessionNumber for clinical relevance.

### 1.2 Scope

**In Scope for Phase 1 (Chemistry Labs):**
- Mock CDW database schema:
  - **Dimension table:** `Dim.LabTest` (test definitions with LOINC codes)
  - **Fact table:** `Chem.LabChem` (chemistry lab results)
- ETL pipeline: Bronze → Silver → Gold → PostgreSQL
- Dashboard widget (**3x1 size - full width, first widget of this size**):
  - **Hybrid layout:** Left 2/3 shows recent lab panels side-by-side (e.g., BMP | CBC | LFT)
  - **Right 1/3:** Mini trend sparklines for key tests (e.g., Glucose, Creatinine, Hemoglobin)
  - Each panel shows 3-5 key results with values and abnormal flags
  - Panel headers with collection date
  - "View All Labs" link to full page
  - **Widget Location:** Dashboard, full-width placement (spans 3 columns)
- Full Laboratory Results page with:
  - **Simultaneous table + graph view:**
    - **Top section:** Interactive line chart showing selected test trends over time
    - **Bottom section:** Comprehensive table of all lab results
  - **Table features:**
    - Grouped by panel (AccessionNumber) with expandable rows
    - Columns: Collection Date, Panel/Test Name, Result, Flag, Reference Range, Units
    - Status badges for abnormal flags (H, L, H*, L*, Panic)
    - Sorting by date, test name, or result value
    - Pagination (20 results per page default, options: 20/30/50/100)
  - **Graph features:**
    - Single test selection (dropdown or click from table)
    - Reference range lines (low/high) displayed on graph
    - Hover tooltips showing exact values and dates
    - Chart.js library (consistent with Vitals domain)
  - **Filtering:**
    - Date range selector (30 days, 90 days default, 6 months, 1 year, all)
    - Abnormal results only toggle
  - **Default view:** 90 days of lab history
- Chemistry lab packages only (`VistaPackage = 'CH'`)
- Common lab panels: BMP, CBC, CMP, LFT, Lipid Panel, HgbA1c, TSH, Urinalysis
- LOINC codes included for all tests (supports future interoperability)
- Read-only functionality

**Out of Scope for Phase 1:**
- Microbiology (MI), Cytology (CY), Anatomic Pathology (AP) packages (deferred to Phase 2)
- Lab result entry/editing (read-only for now)
- Multi-test graph overlay (single test only in Phase 1)
- Advanced graph interactions (zoom, pan, click data points)
- Lab alerts and critical value notifications
- Lab ordering/requisition integration
- Result interpretation assistance (AI-powered)
- Historical comparison views (e.g., side-by-side panels from different dates)
- Custom lab panel creation
- Lab result download/export (PDF, CSV)
- Integration with CPRS lab ordering
- Real-time lab result streaming
- Cumulative result views (e.g., all Creatinine results in one table row)

### 1.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Widget Size** | 3x1 (Full Width) | First full-width widget; lab panels benefit from horizontal space to display multiple panels side-by-side |
| **Widget Layout** | Hybrid (Panels + Trends) | Combines current values (panels) with historical context (sparklines) for maximum clinical utility |
| **Lab Packages** | Chemistry Only (Phase 1) | Most commonly viewed package; Microbiology has different UI requirements (text-heavy, organism/sensitivity) |
| **Panel Grouping** | Grouped by AccessionNumber | Matches clinical workflow; clinicians think in panels, not individual tests |
| **Full Page Layout** | Simultaneous Table + Graph | Eliminates tab switching; supports clinical decision-making by showing trends alongside raw data |
| **Routing Pattern** | Pattern B (Dedicated Router) | Complex domain with full page view, graphing, filtering; warrants dedicated router |
| **Graphing Library** | Chart.js | Consistent with Vitals domain; lightweight, well-documented |
| **Pagination Threshold** | 20 results per page | Consistent with Encounters domain; appropriate for 90-day default view |
| **LOINC Codes** | Included in Phase 1 | Supports future interoperability and AI/ML use cases; relatively easy to add during data generation |
| **Default Date Range** | 90 days | Clinical best practice for trend analysis; balances performance and completeness |
| **Reference Ranges** | Horizontal lines on graph | Matches legacy JLV pattern; provides immediate visual context for abnormality assessment |

---

## 2. Objectives and Success Criteria

### 2.1 Data Pipeline Objectives

- [ ] **Bronze Layer**: Extract raw lab data from `CDWWork.Chem.LabChem` with `Dim.LabTest` lookups
- [ ] **Silver Layer**: Clean, standardize, resolve patient identity (ICN/PatientKey), parse numeric results
- [ ] **Gold Layer**: Create patient-centric, panel-grouped Parquet files optimized for querying
- [ ] **PostgreSQL**: Load lab results into `patient_lab_results` table with <2 second query performance for 90-day range

### 2.2 UI Objectives

- [ ] **Dashboard Widget (3x1)**: Display 3-4 recent lab panels with key results and mini trend sparklines
- [ ] **Full Page View**: Comprehensive lab results with:
  - Panel-grouped table (expandable rows)
  - Interactive trend graph for individual tests
  - Date range filtering (30d, 90d, 6mo, 1yr, all)
  - Abnormal results filter toggle
  - Pagination for large result sets
  - Reference range display in table and graph

### 2.3 Success Criteria

- [ ] Widget loads in <2 seconds for 95% of patients
- [ ] Full page view loads in <3 seconds with 90 days of lab data
- [ ] Graph renders smoothly with up to 100 data points
- [ ] Correctly identifies and highlights abnormal results (H, L, H*, L*, Panic)
- [ ] Panel grouping accurately reflects AccessionNumber relationships
- [ ] All 80-100 test lab results display correctly across test patients
- [ ] Reference range lines display correctly on graphs
- [ ] Pagination works correctly with different page size options (20/30/50/100)
- [ ] Date range filtering updates both table and graph appropriately
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
- ✅ Dashboard widget system (1x1, 2x1 widgets implemented)
- ✅ Pattern B routing examples (Vitals, Encounters domains)
- ✅ Chart.js graphing implementation (Vitals domain)

### 3.2 Environment Setup

**SQL Server (Mock CDW):**
- Container: `sqlserver2019` running SQL Server 2019
- Database: `CDWWork`
- Schema: `Dim` (for LabTest dimension)
- Schema: `Chem` (for LabChem fact table)
- New tables: `Dim.LabTest`, `Chem.LabChem`

**PostgreSQL (Serving Database):**
- Container: `postgres16` running PostgreSQL 16
- Database: `medz1`
- New table: `patient_lab_results`

**MinIO (Data Lake):**
- Bucket: `med-z1`
- Paths: `bronze/labs/`, `silver/labs/`, `gold/labs/`

---

## 4. Data Architecture

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

### 4.1 Source System - CDWWork Schema

**VistA Source:** LAB DATA File #63, LABORATORY TEST File #60

#### 4.1.1 Dim.LabTest (Test Definitions)

Replicates VistA File #60 (LABORATORY TEST). Contains test definitions, LOINC codes, and reference ranges.

**DDL Script:** `mock/sql-server/cdwwork/create/Dim.LabTest.sql`

```sql
-- Create Dim schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Dim')
BEGIN
    EXEC('CREATE SCHEMA Dim');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Dim.LabTest', 'U') IS NOT NULL
    DROP TABLE [Dim].[LabTest];
GO

-- Create LabTest dimension table
CREATE TABLE [Dim].[LabTest] (
    -- Primary key
    [LabTestSID] INT IDENTITY(1,1) PRIMARY KEY,

    -- Test identification
    [LabTestName] VARCHAR(100) NOT NULL,
    [LabTestCode] VARCHAR(50),           -- Local VistA Code or IEN
    [LoincCode] VARCHAR(20),             -- LOINC code for interoperability

    -- Panel classification
    [IsPanel] BIT DEFAULT 0,             -- 1 if this is a panel header, 0 if atomic test
    [PanelName] VARCHAR(100),            -- Panel this test belongs to (e.g., 'BMP', 'CBC')

    -- Units and reference ranges
    [Units] VARCHAR(50),                 -- Default units (e.g., 'mg/dL', 'mmol/L')
    [RefRangeLow] VARCHAR(20),           -- Default low reference value
    [RefRangeHigh] VARCHAR(20),          -- Default high reference value
    [RefRangeText] VARCHAR(100),         -- Full reference range text (e.g., '135 - 145 mg/dL')

    -- Package classification
    [VistaPackage] VARCHAR(10) DEFAULT 'CH',  -- CH=Chemistry, MI=Microbiology, etc.

    -- Metadata
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),
    [IsActive] BIT DEFAULT 1
);
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

-- Index on LabTestName for lookups
CREATE NONCLUSTERED INDEX [IX_LabTest_LabTestName]
    ON [Dim].[LabTest] ([LabTestName]);
GO

-- Index on LoincCode for interoperability queries
CREATE NONCLUSTERED INDEX [IX_LabTest_LoincCode]
    ON [Dim].[LabTest] ([LoincCode])
    WHERE [LoincCode] IS NOT NULL;
GO

-- Index on PanelName for panel-based queries
CREATE NONCLUSTERED INDEX [IX_LabTest_PanelName]
    ON [Dim].[LabTest] ([PanelName])
    WHERE [PanelName] IS NOT NULL;
GO

-- Index on VistaPackage for package filtering
CREATE NONCLUSTERED INDEX [IX_LabTest_VistaPackage]
    ON [Dim].[LabTest] ([VistaPackage]);
GO
```

**Key Fields:**
- `LabTestSID`: Surrogate primary key
- `LabTestName`: Human-readable test name (e.g., "Sodium", "Hemoglobin")
- `LoincCode`: LOINC code (e.g., "2951-2" for Sodium)
- `IsPanel`: Boolean flag (1 = panel header like "BMP", 0 = atomic test)
- `PanelName`: Panel association (e.g., "BMP", "CBC", "CMP")
- `Units`: Default units (e.g., "mmol/L", "g/dL")
- `RefRangeLow/High`: Reference range boundaries for abnormality detection
- `VistaPackage`: Package code ('CH' for Chemistry in Phase 1)

#### 4.1.2 Chem.LabChem (Lab Results - Fact Table)

Replicates VistA File #63 (LAB DATA). This is the high-volume fact table containing millions of lab results.

**DDL Script:** `mock/sql-server/cdwwork/create/Chem.LabChem.sql`

```sql
-- Create Chem schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Chem')
BEGIN
    EXEC('CREATE SCHEMA Chem');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Chem.LabChem', 'U') IS NOT NULL
    DROP TABLE [Chem].[LabChem];
GO

-- Create LabChem fact table
CREATE TABLE [Chem].[LabChem] (
    -- Primary key
    [LabChemSID] BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Foreign keys
    [PatientSID] INT NOT NULL,           -- FK to SPatient.SPatient
    [LabTestSID] INT NOT NULL,           -- FK to Dim.LabTest
    [LabOrderSID] INT NULL,              -- FK to Lab.LabOrder (optional)

    -- Panel grouping
    [AccessionNumber] VARCHAR(50),       -- Critical for grouping panel results (e.g., "CH 1234")

    -- Result data
    [Result] VARCHAR(100),               -- Text representation (e.g., "140", "Positive", "<5.0")
    [ResultNumeric] DECIMAL(18,4),       -- Parsed numeric value for graphing (NULL if non-numeric)
    [ResultUnit] VARCHAR(50),            -- Unit at time of result (may differ from default)

    -- Flags and ranges
    [AbnormalFlag] VARCHAR(10),          -- 'H' (High), 'L' (Low), 'H*' (Critical High), 'L*' (Critical Low), 'Panic'
    [RefRange] VARCHAR(50),              -- Range string at time of result (e.g., "135 - 145")

    -- Temporal data
    [CollectionDateTime] DATETIME2(0),   -- When specimen was collected (clinical relevance)
    [ResultDateTime] DATETIME2(0),       -- When result was verified/reported

    -- Administrative
    [VistaPackage] VARCHAR(10) DEFAULT 'CH',  -- CH=Chemistry, MI=Micro, CY=Cyto, AP=Anatomic Path
    [LocationSID] INT,                   -- Collection location (Inpatient Ward, Outpatient Clinic, ER)
    [Sta3n] INT NOT NULL,                -- VA Station Number

    -- Metadata
    [PerformingLabSID] INT,              -- Lab that performed the test
    [OrderingProviderSID] INT,           -- Provider who ordered the test
    [SpecimenType] VARCHAR(50)           -- Specimen type (e.g., "Blood", "Serum", "Urine")
);
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

-- Index on PatientSID for patient-centric queries
CREATE NONCLUSTERED INDEX [IX_LabChem_PatientSID]
    ON [Chem].[LabChem] ([PatientSID]);
GO

-- Composite index for patient labs sorted by date
CREATE NONCLUSTERED INDEX [IX_LabChem_PatientSID_CollectionDateTime]
    ON [Chem].[LabChem] ([PatientSID], [CollectionDateTime] DESC);
GO

-- Index on CollectionDateTime for date range queries
CREATE NONCLUSTERED INDEX [IX_LabChem_CollectionDateTime]
    ON [Chem].[LabChem] ([CollectionDateTime] DESC);
GO

-- Index on AccessionNumber for panel grouping
CREATE NONCLUSTERED INDEX [IX_LabChem_AccessionNumber]
    ON [Chem].[LabChem] ([AccessionNumber])
    WHERE [AccessionNumber] IS NOT NULL;
GO

-- Index on LabTestSID for test-specific queries
CREATE NONCLUSTERED INDEX [IX_LabChem_LabTestSID]
    ON [Chem].[LabChem] ([LabTestSID]);
GO

-- Index on AbnormalFlag for filtering abnormal results
CREATE NONCLUSTERED INDEX [IX_LabChem_AbnormalFlag]
    ON [Chem].[LabChem] ([AbnormalFlag])
    WHERE [AbnormalFlag] IS NOT NULL;
GO

-- Composite index for patient + test trending queries
CREATE NONCLUSTERED INDEX [IX_LabChem_PatientSID_LabTestSID_CollectionDateTime]
    ON [Chem].[LabChem] ([PatientSID], [LabTestSID], [CollectionDateTime] DESC);
GO
```

**Key Fields:**
- `LabChemSID`: Surrogate primary key
- `PatientSID`: Links to patient
- `LabTestSID`: Links to test definition (Dim.LabTest)
- `AccessionNumber`: Groups related tests into panels (e.g., all BMP tests share same accession)
- `Result`: Text result (handles numeric and non-numeric results)
- `ResultNumeric`: Parsed numeric value for graphing and trending
- `AbnormalFlag`: Abnormality indicator ('H', 'L', 'H*', 'L*', 'Panic', NULL)
- `RefRange`: Reference range at time of result (can vary by age, sex, etc.)
- `CollectionDateTime`: **Primary timestamp for clinical relevance** (when specimen drawn)
- `ResultDateTime`: When result became available
- `VistaPackage`: Package code ('CH' for Chemistry in Phase 1)

### 4.2 Test Data Strategy

**Volume:** 80-100 total lab results across 36 patients

**Panel Distribution (8-10 common panels):**
1. **BMP (Basic Metabolic Panel)** - 15 panels × 7 tests = 105 results
   - Sodium, Potassium, Chloride, CO2, BUN, Creatinine, Glucose
2. **CBC (Complete Blood Count)** - 12 panels × 8 tests = 96 results
   - WBC, RBC, Hemoglobin, Hematocrit, Platelets, MCV, MCH, MCHC
3. **CMP (Comprehensive Metabolic Panel)** - 8 panels × 14 tests = 112 results
   - All BMP tests + Calcium, Total Protein, Albumin, Total Bilirubin, Alkaline Phosphatase, AST, ALT
4. **LFT (Liver Function Tests)** - 10 panels × 6 tests = 60 results
   - Total Bilirubin, Direct Bilirubin, Alkaline Phosphatase, AST, ALT, Total Protein
5. **Lipid Panel** - 10 panels × 5 tests = 50 results
   - Total Cholesterol, LDL, HDL, Triglycerides, VLDL
6. **HgbA1c** - 8 individual tests (not panel)
7. **TSH (Thyroid Stimulating Hormone)** - 6 individual tests
8. **Urinalysis** - 5 panels × 10 tests = 50 results
   - Color, Clarity, Specific Gravity, pH, Protein, Glucose, Ketones, Blood, Leukocyte Esterase, Nitrites

**Total Results:** Approximately 80-100 individual lab results (after balancing panel distribution)

**Temporal Distribution:**
- **Recent (<30 days):** 30% of results
- **30-90 days:** 40% of results
- **90-180 days:** 20% of results
- **>180 days:** 10% of results

**Abnormality Distribution:**
- **Normal:** 70% of results (AbnormalFlag = NULL)
- **High (H):** 15% of results
- **Low (L):** 12% of results
- **Critical High (H*):** 2% of results
- **Critical Low (L*):** 1% of results
- **Panic:** <1% of results

**Patient Coverage:**
- 20 patients with multiple lab panels (chronic disease management)
- 10 patients with single lab panels (annual checkup)
- 6 patients with no lab results (edge case testing)

**Edge Cases:**
- 2 patients with critical/panic values (ICU/ER scenarios)
- 3 patients with all normal results (healthy patients)
- 2 patients with non-numeric results (e.g., "Positive", "Negative", "<5.0")
- 1 patient with 20+ lab results over 90 days (frequent monitoring)

### 4.3 Common Lab Panels and LOINC Codes

**Appendix A** contains comprehensive table of test definitions with LOINC codes for all tests.

---

## 5. Database Schema

### 5.1 PostgreSQL Serving Database

#### 5.1.1 Table Schema - patient_lab_results

**DDL Script:** `db/ddl/create_patient_lab_results_table.sql`

```sql
-- Laboratory Results Table
-- Phase 1: Chemistry labs only (Microbiology, Cytology, Anatomic Path in Phase 2)

CREATE TABLE IF NOT EXISTS patient_lab_results (
    lab_result_id BIGSERIAL PRIMARY KEY,
    patient_icn VARCHAR(20) NOT NULL,
    patient_key INTEGER NOT NULL,

    -- Test identification
    lab_test_sid INTEGER NOT NULL,       -- Source system surrogate key (Dim.LabTest)
    lab_test_name VARCHAR(100) NOT NULL,
    loinc_code VARCHAR(20),
    panel_name VARCHAR(100),             -- Panel association (e.g., 'BMP', 'CBC')

    -- Panel grouping
    accession_number VARCHAR(50),        -- Groups related tests into panel

    -- Result data
    result VARCHAR(100),                 -- Text result (e.g., "140", "Positive")
    result_numeric DECIMAL(18,4),        -- Numeric result for graphing (NULL if non-numeric)
    result_unit VARCHAR(50),

    -- Abnormality indicators
    abnormal_flag VARCHAR(10),           -- 'H', 'L', 'H*', 'L*', 'Panic', NULL
    ref_range VARCHAR(50),               -- Reference range text (e.g., "135 - 145")
    ref_range_low VARCHAR(20),           -- Parsed low value
    ref_range_high VARCHAR(20),          -- Parsed high value

    -- Temporal data
    collection_datetime TIMESTAMP NOT NULL,
    result_datetime TIMESTAMP,

    -- Administrative
    vista_package VARCHAR(10) DEFAULT 'CH',
    facility_name VARCHAR(100),
    sta3n INTEGER,
    performing_lab VARCHAR(100),
    ordering_provider VARCHAR(100),
    specimen_type VARCHAR(50),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX idx_lab_results_patient_icn
    ON patient_lab_results(patient_icn);

CREATE INDEX idx_lab_results_patient_key
    ON patient_lab_results(patient_key);

CREATE INDEX idx_lab_results_collection_date
    ON patient_lab_results(collection_datetime DESC);

-- Composite index for patient labs sorted by date (most common query)
CREATE INDEX idx_lab_results_patient_collection_date
    ON patient_lab_results(patient_icn, collection_datetime DESC);

-- Index for panel grouping queries
CREATE INDEX idx_lab_results_accession_number
    ON patient_lab_results(accession_number)
    WHERE accession_number IS NOT NULL;

-- Index for test-specific trending queries
CREATE INDEX idx_lab_results_patient_test_date
    ON patient_lab_results(patient_icn, lab_test_sid, collection_datetime DESC);

-- Index for abnormal results filtering
CREATE INDEX idx_lab_results_abnormal_flag
    ON patient_lab_results(abnormal_flag)
    WHERE abnormal_flag IS NOT NULL;

-- Index for panel name queries
CREATE INDEX idx_lab_results_panel_name
    ON patient_lab_results(panel_name)
    WHERE panel_name IS NOT NULL;

-- Foreign key (if patient_demographics table exists)
-- ALTER TABLE patient_lab_results
--     ADD CONSTRAINT fk_lab_results_patient
--     FOREIGN KEY (patient_key) REFERENCES patient_demographics(patient_key);
```

**Key Design Notes:**
- `collection_datetime` is the primary temporal field (when specimen was drawn)
- `accession_number` enables panel grouping (all tests in a panel share same accession)
- Both text (`result`) and numeric (`result_numeric`) result fields support non-numeric results
- Separate `ref_range_low` and `ref_range_high` fields enable graph rendering of reference lines
- `abnormal_flag` enables quick filtering of abnormal results
- Indexes optimized for: patient-centric queries, date range filtering, panel grouping, test trending

---

## 6. ETL Pipeline Design

### 6.1 Bronze Layer - Raw Extraction

**Script:** `etl/bronze_labs.py`

**Purpose:** Extract raw lab data from `CDWWork.Chem.LabChem` with `Dim.LabTest` lookups

**SQL Query:**
```sql
SELECT
    lc.LabChemSID,
    lc.PatientSID,
    lc.LabTestSID,
    lc.AccessionNumber,
    lc.Result,
    lc.ResultNumeric,
    lc.ResultUnit,
    lc.AbnormalFlag,
    lc.RefRange,
    lc.CollectionDateTime,
    lc.ResultDateTime,
    lc.VistaPackage,
    lc.LocationSID,
    lc.Sta3n,
    lc.PerformingLabSID,
    lc.OrderingProviderSID,
    lc.SpecimenType,
    -- Patient info
    p.PatientICN,
    p.PatientName,
    -- Test info
    lt.LabTestName,
    lt.LabTestCode,
    lt.LoincCode,
    lt.PanelName,
    lt.Units AS DefaultUnits,
    lt.RefRangeLow AS DefaultRefRangeLow,
    lt.RefRangeHigh AS DefaultRefRangeHigh,
    lt.RefRangeText AS DefaultRefRangeText,
    -- Location info
    loc.LocationName AS CollectionLocation
FROM Chem.LabChem lc
LEFT JOIN SPatient.SPatient p ON lc.PatientSID = p.PatientSID
LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
LEFT JOIN Dim.Location loc ON lc.LocationSID = loc.LocationSID
WHERE lc.VistaPackage = 'CH'  -- Chemistry only for Phase 1
ORDER BY lc.CollectionDateTime DESC;
```

**Output:** `bronze/cdwwork/labs` (Parquet file in MinIO)

**Partitioning:** None (single file for development; partition by Sta3n in production)

### 6.2 Silver Layer - Cleaning and Harmonization

**Script:** `etl/silver_labs.py`

**Transformations:**
1. **Patient Identity Resolution**: Map `PatientSID` → `PatientICN` (unified patient key)
2. **Date Standardization**: Convert DATETIME2 to ISO 8601 strings (`YYYY-MM-DD HH:MM:SS`)
3. **Numeric Result Parsing**: Validate and clean `ResultNumeric` field:
   - Handle special cases: "<5.0" → 5.0 (with flag), ">1000" → 1000 (with flag)
   - Set to NULL if non-numeric text result (e.g., "Positive", "Negative")
4. **Reference Range Parsing**: Split `RefRange` text into `RefRangeLow` and `RefRangeHigh`:
   - Parse "135 - 145" → low=135, high=145
   - Parse "<5.0" → low=NULL, high=5.0
   - Parse ">200" → low=200, high=NULL
5. **Abnormal Flag Standardization**: Normalize abnormal flags:
   - Valid values: 'H', 'L', 'H*', 'L*', 'Panic', NULL
   - Reject invalid values, log warnings
6. **Unit Standardization**: Use `ResultUnit` if present, fallback to `DefaultUnits` from Dim.LabTest
7. **Panel Name Enrichment**: Ensure all results have `PanelName` populated (from Dim.LabTest)
8. **Null Handling**: Replace NULL panel names with 'Individual Test' for ungrouped results

**Output:** `silver/labs` (Parquet file in MinIO)

### 6.3 Gold Layer - Patient-Centric Aggregation

**Script:** `etl/gold_labs.py`

**Transformations:**
1. **Patient-Centric Grouping**: Group by `PatientICN`
2. **Panel Grouping**: Group results by `AccessionNumber` within each patient
3. **Result Sorting**: Order by `CollectionDateTime DESC` (most recent first)
4. **Panel Rollups**: Create panel-level summaries:
   - Most recent panel collection date
   - Count of tests in panel
   - Abnormal result count per panel
5. **Test Trending Preparation**: For widget sparklines:
   - Identify key tests for trending (Glucose, Creatinine, Hemoglobin, Potassium)
   - Extract last 10 results per key test for sparkline rendering
6. **Recent Lab Summary**: Create nested struct with last 3-4 panels for widget use

**Output:** `gold/labs` (Parquet file in MinIO)

**Schema:**
```python
{
    "patient_icn": str,
    "patient_key": int,  # Derived from ICN for DB FK
    "total_lab_results": int,
    "total_panels": int,
    "abnormal_count": int,
    "most_recent_collection_date": datetime,
    "panels": [  # List of panel dicts (grouped by AccessionNumber)
        {
            "accession_number": str,
            "panel_name": str,
            "collection_datetime": datetime,
            "test_count": int,
            "abnormal_count": int,
            "results": [  # List of result dicts within panel
                {
                    "lab_chem_sid": int,
                    "lab_test_sid": int,
                    "lab_test_name": str,
                    "loinc_code": str,
                    "result": str,
                    "result_numeric": float,
                    "result_unit": str,
                    "abnormal_flag": str,
                    "ref_range": str,
                    "ref_range_low": str,
                    "ref_range_high": str,
                    "collection_datetime": datetime,
                    "result_datetime": datetime,
                    "facility_name": str,
                    "sta3n": int
                }
            ]
        }
    ],
    "trending_tests": {  # Pre-computed for widget sparklines
        "glucose": [{"date": datetime, "value": float}, ...],
        "creatinine": [{"date": datetime, "value": float}, ...],
        "hemoglobin": [{"date": datetime, "value": float}, ...],
        "potassium": [{"date": datetime, "value": float}, ...]
    }
}
```

### 6.4 Data Loading - PostgreSQL

**Script:** `etl/load_labs.py`

**Process:**
1. Read Gold Parquet from MinIO (`gold/labs`)
2. Flatten nested `panels` → `results` into individual rows
3. Truncate existing `patient_lab_results` table (full reload for Phase 1)
4. Bulk insert via SQLAlchemy `to_sql()` or `psycopg2 COPY`
5. Verify row count and index integrity

**Expected Row Count:** 80-100 individual lab results (matches mock CDW data)

---

## 7. API Endpoints

### 7.1 Routing Architecture - Pattern B (Dedicated Router)

**Router File:** `app/routes/labs.py`

**Rationale for Pattern B:**
- Complex domain with full-page view and graphing
- Multiple query patterns (panel grouping, test trending, date filtering)
- Future enhancements planned (Microbiology, graph interactions, AI interpretation)
- Separates concerns from `patient.py` (already substantial)

### 7.2 API Endpoints

#### 7.2.1 Widget Endpoint - Recent Lab Panels

**Endpoint:** `GET /patient/{patient_icn}/labs/widget`

**Purpose:** Fetch 3-4 most recent lab panels for dashboard widget display (3x1 layout)

**Query Parameters:** None (always returns most recent panels)

**SQL Query:**
```sql
-- Get recent panels (grouped by AccessionNumber)
WITH RecentPanels AS (
    SELECT DISTINCT
        accession_number,
        panel_name,
        collection_datetime,
        COUNT(*) OVER (PARTITION BY accession_number) as test_count,
        ROW_NUMBER() OVER (ORDER BY collection_datetime DESC) as rn
    FROM patient_lab_results
    WHERE patient_icn = :patient_icn
      AND accession_number IS NOT NULL
      AND collection_datetime >= NOW() - INTERVAL '90 days'
    ORDER BY collection_datetime DESC
)
SELECT
    lr.lab_result_id,
    lr.lab_test_name,
    lr.loinc_code,
    lr.panel_name,
    lr.accession_number,
    lr.result,
    lr.result_numeric,
    lr.result_unit,
    lr.abnormal_flag,
    lr.ref_range,
    lr.collection_datetime
FROM patient_lab_results lr
INNER JOIN RecentPanels rp ON lr.accession_number = rp.accession_number
WHERE lr.patient_icn = :patient_icn
  AND rp.rn <= 3  -- Get top 3 most recent panels
ORDER BY lr.collection_datetime DESC, lr.accession_number, lr.lab_test_name;
```

**Response Format (JSON):**
```json
{
  "patient_icn": "ICN100001",
  "total_panels": 12,
  "recent_panels": [
    {
      "accession_number": "CH 20251210-001",
      "panel_name": "BMP",
      "collection_datetime": "2025-12-10T08:30:00",
      "test_count": 7,
      "abnormal_count": 1,
      "results": [
        {
          "lab_test_name": "Sodium",
          "result": "142",
          "result_unit": "mmol/L",
          "abnormal_flag": null,
          "ref_range": "135 - 145"
        },
        {
          "lab_test_name": "Potassium",
          "result": "5.2",
          "result_unit": "mmol/L",
          "abnormal_flag": "H",
          "ref_range": "3.5 - 5.0"
        }
        // ... 5 more BMP results
      ]
    },
    {
      "accession_number": "CH 20251205-002",
      "panel_name": "CBC",
      "collection_datetime": "2025-12-05T14:15:00",
      "test_count": 8,
      "abnormal_count": 0,
      "results": [
        // ... 8 CBC results
      ]
    },
    {
      "accession_number": "CH 20251201-003",
      "panel_name": "Lipid Panel",
      "collection_datetime": "2025-12-01T09:00:00",
      "test_count": 5,
      "abnormal_count": 2,
      "results": [
        // ... 5 Lipid Panel results
      ]
    }
  ],
  "trending_tests": {
    "glucose": [
      {"date": "2025-12-10", "value": 105},
      {"date": "2025-11-15", "value": 98},
      {"date": "2025-10-20", "value": 102}
    ],
    "creatinine": [
      {"date": "2025-12-10", "value": 1.1},
      {"date": "2025-11-15", "value": 1.0},
      {"date": "2025-10-20", "value": 0.9}
    ]
  }
}
```

**Template:** `app/templates/partials/labs_widget.html`

**HTMX Fragment:** Returns widget HTML (no full page wrapper)

#### 7.2.2 Full Page Endpoint - All Lab Results

**Endpoint:** `GET /patient/{patient_icn}/labs`

**Purpose:** Display comprehensive lab history with table and graph views

**Query Parameters:**
- `date_range` (optional): `'30d'`, `'90d'` (default), `'6mo'`, `'1yr'`, `'all'`
- `abnormal_only` (optional): `'true'` or `'false'` (default)
- `sort` (optional): `'date'` (default), `'test_name'`, `'result'`
- `order` (optional): `'desc'` (default) or `'asc'`
- `page` (optional): Page number for pagination (default: 1)
- `per_page` (optional): Results per page (default: 20, options: 20/30/50/100)

**SQL Query (with filters):**
```sql
SELECT
    lab_result_id,
    lab_test_sid,
    lab_test_name,
    loinc_code,
    panel_name,
    accession_number,
    result,
    result_numeric,
    result_unit,
    abnormal_flag,
    ref_range,
    ref_range_low,
    ref_range_high,
    collection_datetime,
    result_datetime,
    facility_name,
    sta3n,
    ordering_provider,
    specimen_type
FROM patient_lab_results
WHERE patient_icn = :patient_icn
  AND collection_datetime >= :start_date  -- Based on date_range parameter
  AND (:abnormal_only = FALSE OR abnormal_flag IS NOT NULL)
ORDER BY
    CASE WHEN :sort = 'date' THEN collection_datetime END DESC,
    CASE WHEN :sort = 'test_name' THEN lab_test_name END ASC,
    CASE WHEN :sort = 'result' THEN result_numeric END DESC
LIMIT :per_page OFFSET :offset;
```

**Template:** `app/templates/patient_labs.html`

**HTMX Integration:**
- Filter controls (date range, abnormal only) trigger `hx-get` to reload table and graph
- Sort headers use `hx-get` with `hx-target="#labs-table"`
- Pagination uses `hx-get` for seamless page navigation
- Test selection dropdown triggers graph update via `hx-get` to `#labs-graph`

#### 7.2.3 Graph Data Endpoint - Test Trending

**Endpoint:** `GET /patient/{patient_icn}/labs/trend/{lab_test_sid}`

**Purpose:** Fetch time-series data for a single test to render trend graph

**Query Parameters:**
- `date_range` (optional): `'30d'`, `'90d'` (default), `'6mo'`, `'1yr'`, `'all'`

**SQL Query:**
```sql
SELECT
    collection_datetime,
    result_numeric,
    abnormal_flag,
    ref_range_low,
    ref_range_high,
    result_unit
FROM patient_lab_results
WHERE patient_icn = :patient_icn
  AND lab_test_sid = :lab_test_sid
  AND result_numeric IS NOT NULL
  AND collection_datetime >= :start_date
ORDER BY collection_datetime ASC;  -- Ascending for graph rendering
```

**Response Format (JSON):**
```json
{
  "patient_icn": "ICN100001",
  "lab_test_sid": 42,
  "lab_test_name": "Glucose",
  "loinc_code": "2345-7",
  "result_unit": "mg/dL",
  "ref_range_low": "70",
  "ref_range_high": "100",
  "data_points": [
    {
      "date": "2025-09-15T08:00:00",
      "value": 95,
      "abnormal_flag": null
    },
    {
      "date": "2025-10-20T09:15:00",
      "value": 102,
      "abnormal_flag": "H"
    },
    {
      "date": "2025-11-15T07:45:00",
      "value": 98,
      "abnormal_flag": null
    },
    {
      "date": "2025-12-10T08:30:00",
      "value": 105,
      "abnormal_flag": "H"
    }
  ],
  "total_results": 4,
  "abnormal_count": 2
}
```

**Template:** `app/templates/partials/labs_graph.html`

**HTMX Fragment:** Returns graph HTML with Chart.js initialization

### 7.3 Database Query Functions

**File:** `app/db/labs.py`

```python
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging
from datetime import datetime, timedelta
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)


def get_date_filter(date_range: str) -> datetime:
    """Convert date_range string to start_date datetime."""
    now = datetime.now()
    if date_range == '30d':
        return now - timedelta(days=30)
    elif date_range == '6mo':
        return now - timedelta(days=180)
    elif date_range == '1yr':
        return now - timedelta(days=365)
    elif date_range == 'all':
        return datetime(1900, 1, 1)  # Effectively no filter
    else:  # default '90d'
        return now - timedelta(days=90)


def get_recent_panels(icn: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Fetch most recent lab panels for widget."""
    query = text("""
        WITH RecentPanels AS (
            SELECT DISTINCT
                accession_number,
                panel_name,
                collection_datetime,
                COUNT(*) OVER (PARTITION BY accession_number) as test_count,
                ROW_NUMBER() OVER (ORDER BY collection_datetime DESC) as rn
            FROM patient_lab_results
            WHERE patient_icn = :icn
              AND accession_number IS NOT NULL
              AND collection_datetime >= NOW() - INTERVAL '90 days'
        )
        SELECT
            lr.lab_result_id,
            lr.lab_test_name,
            lr.loinc_code,
            lr.panel_name,
            lr.accession_number,
            lr.result,
            lr.result_numeric,
            lr.result_unit,
            lr.abnormal_flag,
            lr.ref_range,
            lr.collection_datetime
        FROM patient_lab_results lr
        INNER JOIN RecentPanels rp ON lr.accession_number = rp.accession_number
        WHERE lr.patient_icn = :icn
          AND rp.rn <= :limit
        ORDER BY lr.collection_datetime DESC, lr.accession_number, lr.lab_test_name
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn, "limit": limit})
        rows = [dict(row._mapping) for row in result]

    # Group results by panel (accession_number)
    panels = {}
    for row in rows:
        acc = row['accession_number']
        if acc not in panels:
            panels[acc] = {
                'accession_number': acc,
                'panel_name': row['panel_name'],
                'collection_datetime': row['collection_datetime'],
                'results': []
            }
        panels[acc]['results'].append({
            'lab_test_name': row['lab_test_name'],
            'result': row['result'],
            'result_unit': row['result_unit'],
            'abnormal_flag': row['abnormal_flag'],
            'ref_range': row['ref_range']
        })

    return list(panels.values())


def get_trending_tests(icn: str, test_names: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch trending data for key tests (for widget sparklines)."""
    if test_names is None:
        test_names = ['Glucose', 'Creatinine', 'Hemoglobin', 'Potassium']

    trends = {}
    for test_name in test_names:
        query = text("""
            SELECT
                collection_datetime,
                result_numeric
            FROM patient_lab_results
            WHERE patient_icn = :icn
              AND lab_test_name = :test_name
              AND result_numeric IS NOT NULL
              AND collection_datetime >= NOW() - INTERVAL '180 days'
            ORDER BY collection_datetime DESC
            LIMIT 10
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"icn": icn, "test_name": test_name})
            trends[test_name.lower()] = [
                {"date": row.collection_datetime, "value": float(row.result_numeric)}
                for row in result
            ]

    return trends


def get_all_lab_results(
    icn: str,
    date_range: str = '90d',
    abnormal_only: bool = False,
    sort_by: str = 'date',
    order: str = 'desc',
    page: int = 1,
    per_page: int = 20
) -> Tuple[List[Dict[str, Any]], int]:
    """Fetch all lab results with filtering, sorting, pagination."""

    # Calculate start date
    start_date = get_date_filter(date_range)

    # Build WHERE clause
    where_clauses = ["patient_icn = :icn", "collection_datetime >= :start_date"]
    params = {
        "icn": icn,
        "start_date": start_date,
        "per_page": per_page,
        "offset": (page - 1) * per_page
    }

    if abnormal_only:
        where_clauses.append("abnormal_flag IS NOT NULL")

    where_sql = " AND ".join(where_clauses)

    # Build ORDER BY clause
    sort_column = {
        'date': 'collection_datetime',
        'test_name': 'lab_test_name',
        'result': 'result_numeric'
    }.get(sort_by, 'collection_datetime')

    order_sql = f"{sort_column} {'ASC' if order == 'asc' else 'DESC'}"

    # Get total count
    count_query = text(f"""
        SELECT COUNT(*)
        FROM patient_lab_results
        WHERE {where_sql}
    """)

    with engine.connect() as conn:
        total_count = conn.execute(count_query, params).scalar()

    # Get paginated results
    query = text(f"""
        SELECT
            lab_result_id,
            lab_test_sid,
            lab_test_name,
            loinc_code,
            panel_name,
            accession_number,
            result,
            result_numeric,
            result_unit,
            abnormal_flag,
            ref_range,
            ref_range_low,
            ref_range_high,
            collection_datetime,
            result_datetime,
            facility_name,
            sta3n,
            ordering_provider,
            specimen_type
        FROM patient_lab_results
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT :per_page OFFSET :offset
    """)

    with engine.connect() as conn:
        result = conn.execute(query, params)
        results = [dict(row._mapping) for row in result]

    return results, total_count


def get_test_trend(
    icn: str,
    lab_test_sid: int,
    date_range: str = '90d'
) -> Dict[str, Any]:
    """Fetch time-series data for a single test (for graphing)."""

    start_date = get_date_filter(date_range)

    query = text("""
        SELECT
            lab_test_name,
            loinc_code,
            collection_datetime,
            result_numeric,
            abnormal_flag,
            ref_range_low,
            ref_range_high,
            result_unit
        FROM patient_lab_results
        WHERE patient_icn = :icn
          AND lab_test_sid = :lab_test_sid
          AND result_numeric IS NOT NULL
          AND collection_datetime >= :start_date
        ORDER BY collection_datetime ASC
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "icn": icn,
            "lab_test_sid": lab_test_sid,
            "start_date": start_date
        })
        rows = [dict(row._mapping) for row in result]

    if not rows:
        return None

    # Build response
    first_row = rows[0]
    return {
        "lab_test_sid": lab_test_sid,
        "lab_test_name": first_row['lab_test_name'],
        "loinc_code": first_row['loinc_code'],
        "result_unit": first_row['result_unit'],
        "ref_range_low": first_row['ref_range_low'],
        "ref_range_high": first_row['ref_range_high'],
        "data_points": [
            {
                "date": row['collection_datetime'],
                "value": float(row['result_numeric']),
                "abnormal_flag": row['abnormal_flag']
            }
            for row in rows
        ],
        "total_results": len(rows),
        "abnormal_count": sum(1 for row in rows if row['abnormal_flag'] is not None)
    }
```

---

## 8. UI/UX Design

### 8.1 Dashboard Widget (3x1 Full-Width) - Recent Lab Panels

**File:** `app/templates/partials/labs_widget.html`

**Layout (Hybrid: Panels + Trends):**
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 🧪 Laboratory Results                                                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┬─────────────────────┬─────────────────────┬──────────────────┐  │
│ │ BMP - 12/10/2025    │ CBC - 12/05/2025    │ Lipid - 12/01/2025  │ Trending         │  │
│ │ 8:30 AM             │ 2:15 PM             │ 9:00 AM             │                  │  │
│ ├─────────────────────┼─────────────────────┼─────────────────────┼──────────────────┤  │
│ │ Sodium: 142 ✓       │ WBC: 7.2 ✓          │ Total Chol: 220 ⚠️  │ Glucose          │  │
│ │ Potassium: 5.2 ⚠️   │ RBC: 4.8 ✓          │ LDL: 145 ⚠️         │ ╱╲╱╲_╱           │  │
│ │ Chloride: 101 ✓     │ Hemoglobin: 14.2 ✓  │ HDL: 45 ✓           │ 95→105 mg/dL     │  │
│ │ CO2: 24 ✓           │ Hematocrit: 42 ✓    │ Triglycerides: 150✓ │                  │  │
│ │ BUN: 18 ✓           │ Platelets: 250 ✓    │ VLDL: 30 ✓          │ Creatinine       │  │
│ │ Creatinine: 1.1 ✓   │ MCV: 88 ✓           │                     │ ─────────        │  │
│ │ Glucose: 105 ⚠️     │                     │                     │ 0.9→1.1 mg/dL    │  │
│ └─────────────────────┴─────────────────────┴─────────────────────┴──────────────────┘  │
│ ↗ View All Lab Results                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Header**: "🧪 Laboratory Results" with lab flask icon
- **Three-Column Panel Layout (Left 2/3):**
  - Each column shows one recent lab panel
  - Panel header: Panel name + collection date/time
  - 5-7 key results per panel
  - Abnormal flag indicators: ✓ (normal), ⚠️ (H/L), 🔴 (H*/L*/Panic)
  - Result format: "Test: Value Unit Flag"
- **Trending Section (Right 1/3):**
  - Mini sparklines for 2-3 key tests (Glucose, Creatinine, Hemoglobin)
  - Simple ASCII-art style line chart or actual mini chart.js graphs
  - Shows trend direction and latest value
- **View All Link**: Bottom of widget using `widget-action` class
- **Responsive**: On mobile, stack panels vertically, hide trending section

**Jinja2 Template Excerpt:**
```html
<!-- Labs Widget Content -->
<div class="widget widget--3x1">
    <!-- Widget Header -->
    <div class="widget__header">
        <div class="widget__title-group">
            <i class="fa-solid fa-flask widget__icon"></i>
            <h3 class="widget__title">Laboratory Results</h3>
        </div>
        {% if total_panels > 0 %}
            <span class="badge badge--info">{{ total_panels }} Panels (90 days)</span>
        {% endif %}
    </div>

    <!-- Widget Body -->
    <div class="widget__body">
        {% if error %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">
                <i class="fa-solid fa-circle-exclamation"></i> Error loading lab results
            </p>
        {% elif total_panels == 0 %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">No lab results available</p>
        {% else %}
            <div class="labs-widget-layout">
                <!-- Left 2/3: Recent Panels -->
                <div class="labs-widget-panels">
                    {% for panel in recent_panels[:3] %}
                    <div class="lab-panel-card">
                        <div class="lab-panel-card__header">
                            <span class="lab-panel-card__name">{{ panel.panel_name }}</span>
                            <span class="lab-panel-card__date">
                                {{ panel.collection_datetime.strftime('%m/%d/%Y') }}<br>
                                <small>{{ panel.collection_datetime.strftime('%I:%M %p') }}</small>
                            </span>
                        </div>
                        <div class="lab-panel-card__results">
                            {% for result in panel.results[:7] %}
                            <div class="lab-result-item">
                                <span class="lab-result-item__name">{{ result.lab_test_name }}:</span>
                                <span class="lab-result-item__value">{{ result.result }}</span>
                                <span class="lab-result-item__unit">{{ result.result_unit }}</span>
                                {% if result.abnormal_flag %}
                                    {% if result.abnormal_flag in ['H*', 'L*', 'Panic'] %}
                                        <i class="fa-solid fa-circle-exclamation text-danger" title="Critical"></i>
                                    {% else %}
                                        <i class="fa-solid fa-triangle-exclamation text-warning" title="Abnormal"></i>
                                    {% endif %}
                                {% else %}
                                    <i class="fa-solid fa-check text-success" title="Normal"></i>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <!-- Right 1/3: Trending Sparklines -->
                <div class="labs-widget-trends">
                    <h4 class="labs-widget-trends__title">Trending</h4>
                    {% if trending_tests %}
                        {% for test_name, data_points in trending_tests.items() %}
                        {% if data_points|length > 0 %}
                        <div class="trend-sparkline">
                            <div class="trend-sparkline__header">{{ test_name|title }}</div>
                            <canvas id="sparkline-{{ test_name }}" width="120" height="40"></canvas>
                            <div class="trend-sparkline__latest">
                                {{ data_points[0].value }}
                                <small>{{ data_points[0].date.strftime('%m/%d') }}</small>
                            </div>
                        </div>
                        <script>
                            // Render mini sparkline chart using Chart.js
                            const ctx{{ test_name }} = document.getElementById('sparkline-{{ test_name }}').getContext('2d');
                            new Chart(ctx{{ test_name }}, {
                                type: 'line',
                                data: {
                                    labels: {{ data_points|map(attribute='date')|map('string')|list|tojson }},
                                    datasets: [{
                                        data: {{ data_points|map(attribute='value')|list|tojson }},
                                        borderColor: '#06b6d4',
                                        borderWidth: 2,
                                        fill: false,
                                        pointRadius: 0
                                    }]
                                },
                                options: {
                                    responsive: false,
                                    plugins: { legend: { display: false } },
                                    scales: {
                                        x: { display: false },
                                        y: { display: false }
                                    }
                                }
                            });
                        </script>
                        {% endif %}
                        {% endfor %}
                    {% endif %}
                </div>
            </div>

            <!-- View All Link -->
            <div class="widget-action">
                <a href="/labs?patient_icn={{ patient_icn }}" class="btn btn--link btn--sm">
                    <i class="fa-regular fa-arrow-up-right-from-square"></i>
                    View All Lab Results
                </a>
            </div>
        {% endif %}
    </div>

    <!-- Widget Footer -->
    <div class="widget__footer"></div>
</div>
```

### 8.2 Full Page View - Laboratory Results

**File:** `app/templates/patient_labs.html`

**Layout (Simultaneous Table + Graph):**
```
┌───────────────────────────────────────────────────────────────────────────────┐
│ Dashboard > Laboratory Results                                (Breadcrumb)    │
├───────────────────────────────────────────────────────────────────────────────┤
│ Patient: [Name] ([ICN])                                                       │
│ Laboratory Results - Chemistry                                                │
├───────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐   │
│ │ Graph: Glucose (mg/dL)                                 [Select Test ▼]  │   │
│ │ ┌───────────────────────────────────────────────────────────────────┐   │   │
│ │ │                                                                   │   │   │
│ │ │   110 ┼─────────────────────────────────────────────────●         │   │   │
│ │ │   100 ┼───────────────────────────────●─────────────────┘ ← High  │   │   │
│ │ │    90 ┼───────●───────●───────────────┘                           │   │   │
│ │ │    80 ┼───────┘                                                   │   │   │
│ │ │    70 ┼ ← Low                                                     │   │   │
│ │ │       └────────┴────────┴────────┴────────┴────────┴──────        │   │   │
│ │ │       09/15  10/20   11/15   12/10                                │   │   │
│ │ └───────────────────────────────────────────────────────────────────┘   │   │
│ └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│ Filters: [Date: 90 days ▼] [☐ Abnormal Only]                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐   │
│ │ Date ▼   │ Panel/Test         │ Result │ Flag │ Ref Range  │ Units      │   │
│ ├─────────────────────────────────────────────────────────────────────────┤   │
│ │ 12/10 8:30a BMP Panel (▶ expand)                                        │   │
│ │ 12/10      Sodium               142      ✓      135 - 145    mmol/L     │   │
│ │ 12/10      Potassium            5.2      ⚠️      3.5 - 5.0     mmol/L   │   │
│ │ 12/10      Chloride             101      ✓      98 - 107      mmol/L    │   │
│ │ 12/10      CO2                  24       ✓      22 - 29       mmol/L    │   │
│ │ 12/10      BUN                  18       ✓      7 - 20        mg/dL     │   │
│ │ 12/10      Creatinine           1.1      ✓      0.7 - 1.3     mg/dL     │   │
│ │ 12/10      Glucose              105      ⚠️      70 - 100      mg/dL    │   │
│ ├─────────────────────────────────────────────────────────────────────────┤   │
│ │ 12/05 2:15p CBC Panel (▶ expand)                                        │   │
│ │ ...                                                                     │   │
│ └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│ [<< Prev]  Page 1 of 4  [Next >>]   Per page: [20 ▼]                          │
└───────────────────────────────────────────────────────────────────────────────┘
```

**Features:**

**1. Graph Section (Top):**
- Dropdown to select test for trending (populated with all tests that have numeric results)
- Line chart showing selected test values over time (x-axis: date, y-axis: result value)
- Reference range lines (horizontal): low and high thresholds
- Data points colored by abnormal flag (green=normal, orange=H/L, red=H*/L*/Panic)
- Hover tooltip shows exact value, date, flag, reference range
- Chart.js library (consistent with Vitals)

**2. Filter Controls:**
- Date range dropdown: 30 days, 90 days (default), 6 months, 1 year, all
- Abnormal only checkbox: filters to show only results with abnormal flags
- HTMX: triggers table and graph reload on change

**3. Table Section (Bottom):**
- **Panel Grouping**: Results grouped by AccessionNumber with expandable panel headers
  - Panel header row: "BMP Panel (▶ expand)" - click to expand/collapse individual tests
  - Expanded view shows all tests in panel
  - Collapsed view shows panel name, date, abnormal count
- **Columns**:
  - Collection Date & Time
  - Panel/Test Name
  - Result
  - Flag (icon: ✓, ⚠️, 🔴)
  - Reference Range
  - Units
- **Sortable headers**: Click to sort by date, test name, or result value
- **Pagination**: 20 results per page (default), with 20/30/50/100 options

**4. Responsive Design:**
- Graph: Full width on desktop, scrollable on mobile
- Table: Horizontal scroll on mobile, all columns visible

**Jinja2 Template Excerpt:**
```html
{% extends "base.html" %}

{% block content %}
<div class="breadcrumb">
    <a href="/">Dashboard</a> &gt; Laboratory Results
</div>

<div class="page-header">
    <h1>Laboratory Results - Chemistry</h1>
    <p class="patient-info">Patient: {{ patient_name }} ({{ patient_icn }})</p>
</div>

<!-- Graph Section -->
<div class="labs-graph-section">
    <div class="labs-graph-header">
        <h2>Trend Graph</h2>
        <select id="test-selector" name="lab_test_sid"
                hx-get="/patient/{{ patient_icn }}/labs/trend"
                hx-target="#labs-graph"
                hx-include="[name='date_range']">
            <option value="">Select a test to graph...</option>
            {% for test in available_tests %}
            <option value="{{ test.lab_test_sid }}">{{ test.lab_test_name }}</option>
            {% endfor %}
        </select>
    </div>
    <div id="labs-graph">
        {% if selected_test %}
            {% include "partials/labs_graph.html" %}
        {% else %}
            <p class="text-muted" style="text-align: center; padding: 2rem;">
                Select a test from the dropdown above to view trends
            </p>
        {% endif %}
    </div>
</div>

<!-- Filters -->
<div class="filters">
    <label>Date Range:
        <select name="date_range"
                hx-get="/patient/{{ patient_icn }}/labs"
                hx-target="#labs-content"
                hx-include="[name='abnormal_only'], [name='lab_test_sid']">
            <option value="30d" {% if date_range == '30d' %}selected{% endif %}>30 days</option>
            <option value="90d" {% if date_range == '90d' %}selected{% endif %}>90 days</option>
            <option value="6mo" {% if date_range == '6mo' %}selected{% endif %}>6 months</option>
            <option value="1yr" {% if date_range == '1yr' %}selected{% endif %}>1 year</option>
            <option value="all" {% if date_range == 'all' %}selected{% endif %}>All</option>
        </select>
    </label>

    <label>
        <input type="checkbox" name="abnormal_only" value="true"
               {% if abnormal_only %}checked{% endif %}
               hx-get="/patient/{{ patient_icn }}/labs"
               hx-target="#labs-content"
               hx-include="[name='date_range'], [name='lab_test_sid']">
        Abnormal Results Only
    </label>
</div>

<!-- Table Section -->
<div id="labs-content">
    {% if lab_results %}
    <table class="labs-table">
        <thead>
            <tr>
                <th>
                    <a href="#" hx-get="/patient/{{ patient_icn }}/labs?sort=date&order={{ 'asc' if order == 'desc' else 'desc' }}"
                       hx-target="#labs-content">
                        Collection Date
                    </a>
                </th>
                <th>Panel / Test Name</th>
                <th>Result</th>
                <th>Flag</th>
                <th>Reference Range</th>
                <th>Units</th>
            </tr>
        </thead>
        <tbody>
            {% for panel in grouped_results %}
            <!-- Panel Header Row (Collapsible) -->
            <tr class="panel-header-row" data-accession="{{ panel.accession_number }}">
                <td>{{ panel.collection_datetime.strftime('%m/%d/%Y %I:%M %p') }}</td>
                <td colspan="5">
                    <span class="panel-expand-icon">▶</span>
                    <strong>{{ panel.panel_name }} Panel</strong>
                    {% if panel.abnormal_count > 0 %}
                        <span class="badge badge--warning">{{ panel.abnormal_count }} abnormal</span>
                    {% endif %}
                </td>
            </tr>
            <!-- Panel Results (Initially Hidden) -->
            {% for result in panel.results %}
            <tr class="panel-result-row" data-accession="{{ panel.accession_number }}" style="display: none;">
                <td>{{ result.collection_datetime.strftime('%m/%d/%Y') }}</td>
                <td style="padding-left: 2rem;">{{ result.lab_test_name }}</td>
                <td>{{ result.result }}</td>
                <td>
                    {% if result.abnormal_flag %}
                        {% if result.abnormal_flag in ['H*', 'L*', 'Panic'] %}
                            <i class="fa-solid fa-circle-exclamation text-danger" title="Critical {{ result.abnormal_flag }}"></i>
                        {% else %}
                            <i class="fa-solid fa-triangle-exclamation text-warning" title="{{ result.abnormal_flag }}"></i>
                        {% endif %}
                    {% else %}
                        <i class="fa-solid fa-check text-success" title="Normal"></i>
                    {% endif %}
                </td>
                <td>{{ result.ref_range }}</td>
                <td>{{ result.result_unit }}</td>
            </tr>
            {% endfor %}
            {% endfor %}
        </tbody>
    </table>

    <!-- Pagination -->
    <div class="pagination">
        {% if page > 1 %}
            <a href="#" hx-get="/patient/{{ patient_icn }}/labs?page={{ page - 1 }}&per_page={{ per_page }}"
               hx-target="#labs-content"
               hx-include="[name='date_range'], [name='abnormal_only']">
                &lt;&lt; Prev
            </a>
        {% endif %}
        <span>Page {{ page }} of {{ total_pages }}</span>
        <label>
            Per page:
            <select name="per_page"
                    hx-get="/patient/{{ patient_icn }}/labs?page=1"
                    hx-target="#labs-content"
                    hx-include="[name='date_range'], [name='abnormal_only']">
                <option value="20" {% if per_page == 20 %}selected{% endif %}>20</option>
                <option value="30" {% if per_page == 30 %}selected{% endif %}>30</option>
                <option value="50" {% if per_page == 50 %}selected{% endif %}>50</option>
                <option value="100" {% if per_page == 100 %}selected{% endif %}>100</option>
            </select>
        </label>
        {% if page < total_pages %}
            <a href="#" hx-get="/patient/{{ patient_icn }}/labs?page={{ page + 1 }}&per_page={{ per_page }}"
               hx-target="#labs-content"
               hx-include="[name='date_range'], [name='abnormal_only']">
                Next &gt;&gt;
            </a>
        {% endif %}
    </div>
    {% else %}
    <p class="text-muted" style="text-align: center; padding: 2rem;">
        No lab results found for selected filters
    </p>
    {% endif %}
</div>

<!-- JavaScript for Panel Expand/Collapse -->
<script>
document.addEventListener('click', function(e) {
    if (e.target.closest('.panel-header-row')) {
        const row = e.target.closest('.panel-header-row');
        const accession = row.dataset.accession;
        const icon = row.querySelector('.panel-expand-icon');
        const resultRows = document.querySelectorAll(`.panel-result-row[data-accession="${accession}"]`);

        resultRows.forEach(r => {
            r.style.display = r.style.display === 'none' ? 'table-row' : 'none';
        });

        icon.textContent = icon.textContent === '▶' ? '▼' : '▶';
    }
});
</script>
{% endblock %}
```

### 8.3 Graph Partial Template

**File:** `app/templates/partials/labs_graph.html`

```html
<div class="lab-trend-graph">
    <h3>{{ test_data.lab_test_name }} ({{ test_data.result_unit }})</h3>
    <canvas id="lab-trend-chart" width="800" height="300"></canvas>
    <p class="graph-summary">
        {{ test_data.total_results }} results | {{ test_data.abnormal_count }} abnormal
    </p>
</div>

<script>
const ctx = document.getElementById('lab-trend-chart').getContext('2d');
const chartData = {
    labels: {{ test_data.data_points | map(attribute='date') | map('string') | list | tojson }},
    datasets: [{
        label: '{{ test_data.lab_test_name }}',
        data: {{ test_data.data_points | map(attribute='value') | list | tojson }},
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
        borderWidth: 2,
        pointBackgroundColor: function(context) {
            const flag = {{ test_data.data_points | map(attribute='abnormal_flag') | list | tojson }}[context.dataIndex];
            if (flag === 'H*' || flag === 'L*' || flag === 'Panic') return '#dc2626';  // red
            if (flag === 'H' || flag === 'L') return '#f59e0b';  // orange
            return '#10b981';  // green
        },
        pointRadius: 6,
        pointHoverRadius: 8
    }]
};

// Add reference range lines if available
{% if test_data.ref_range_low %}
chartData.datasets.push({
    label: 'Low Reference',
    data: Array({{ test_data.data_points | length }}).fill({{ test_data.ref_range_low }}),
    borderColor: '#ef4444',
    borderWidth: 1,
    borderDash: [5, 5],
    pointRadius: 0,
    fill: false
});
{% endif %}

{% if test_data.ref_range_high %}
chartData.datasets.push({
    label: 'High Reference',
    data: Array({{ test_data.data_points | length }}).fill({{ test_data.ref_range_high }}),
    borderColor: '#ef4444',
    borderWidth: 1,
    borderDash: [5, 5],
    pointRadius: 0,
    fill: false
});
{% endif %}

new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const flag = {{ test_data.data_points | map(attribute='abnormal_flag') | list | tojson }}[context.dataIndex];
                        let label = context.dataset.label + ': ' + context.parsed.y;
                        if (flag) label += ' (' + flag + ')';
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Collection Date'
                }
            },
            y: {
                title: {
                    display: true,
                    text: '{{ test_data.lab_test_name }} ({{ test_data.result_unit }})'
                }
            }
        }
    }
});
</script>
```

### 8.4 CSS Styling

**File:** `app/static/styles.css` (add to existing CSS file)

```css
/* ===================================
   Laboratory Results Widget (3x1)
   =================================== */

.widget--3x1 {
    grid-column: span 3;  /* Full width widget */
}

.labs-widget-layout {
    display: grid;
    grid-template-columns: 2fr 1fr;  /* 2/3 panels, 1/3 trends */
    gap: 1.5rem;
}

.labs-widget-panels {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}

.lab-panel-card {
    background: #f9fafb;
    border-radius: 0.5rem;
    padding: 0.75rem;
    border: 1px solid #e5e7eb;
}

.lab-panel-card__header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #d1d5db;
}

.lab-panel-card__name {
    font-weight: 600;
    font-size: 0.9rem;
    color: #1f2937;
}

.lab-panel-card__date {
    font-size: 0.75rem;
    color: #6b7280;
    text-align: right;
}

.lab-panel-card__results {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}

.lab-result-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.85rem;
}

.lab-result-item__name {
    font-weight: 500;
    color: #374151;
    min-width: 90px;
}

.lab-result-item__value {
    font-weight: 600;
    color: #111827;
}

.lab-result-item__unit {
    color: #6b7280;
    font-size: 0.8rem;
}

.lab-result-item i {
    margin-left: auto;
    font-size: 0.85rem;
}

/* Trending Section */
.labs-widget-trends {
    background: #f9fafb;
    border-radius: 0.5rem;
    padding: 0.75rem;
    border: 1px solid #e5e7eb;
}

.labs-widget-trends__title {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: #1f2937;
}

.trend-sparkline {
    margin-bottom: 1rem;
}

.trend-sparkline__header {
    font-size: 0.8rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.25rem;
}

.trend-sparkline__latest {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

/* Responsive: Stack on mobile */
@media (max-width: 768px) {
    .labs-widget-layout {
        grid-template-columns: 1fr;
    }

    .labs-widget-panels {
        grid-template-columns: 1fr;
    }

    .labs-widget-trends {
        display: none;  /* Hide trends on mobile */
    }
}

/* ===================================
   Laboratory Results Full Page
   =================================== */

.labs-graph-section {
    background: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 2rem;
    border: 1px solid #e5e7eb;
}

.labs-graph-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.labs-graph-header h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
}

#test-selector {
    padding: 0.5rem 1rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.9rem;
}

.lab-trend-graph {
    padding: 1rem;
}

.lab-trend-graph h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1f2937;
}

.graph-summary {
    text-align: center;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #6b7280;
}

/* Labs Table */
.labs-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    background: white;
}

.labs-table th {
    background: #f9fafb;
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.875rem;
    color: #374151;
    border-bottom: 2px solid #e5e7eb;
}

.labs-table th a {
    color: #06b6d4;
    text-decoration: none;
}

.labs-table th a:hover {
    text-decoration: underline;
}

.labs-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #e5e7eb;
    font-size: 0.875rem;
}

.panel-header-row {
    background: #f3f4f6;
    cursor: pointer;
    font-weight: 600;
}

.panel-header-row:hover {
    background: #e5e7eb;
}

.panel-expand-icon {
    display: inline-block;
    width: 1rem;
    margin-right: 0.5rem;
    transition: transform 0.2s;
}

.panel-result-row {
    background: white;
}

.panel-result-row:hover {
    background: #f9fafb;
}

/* Abnormal Flag Icons */
.text-success {
    color: #10b981;
}

.text-warning {
    color: #f59e0b;
}

.text-danger {
    color: #dc2626;
}

/* Filters */
.filters {
    display: flex;
    gap: 1.5rem;
    align-items: center;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}

.filters label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #374151;
}

.filters select,
.filters input[type="checkbox"] {
    margin-left: 0.5rem;
}

.filters select {
    padding: 0.375rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.875rem;
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
    padding: 1rem;
}

.pagination a {
    color: #06b6d4;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
}

.pagination a:hover {
    background: #f3f4f6;
}

.pagination span {
    font-size: 0.9rem;
    color: #6b7280;
}

.pagination select {
    padding: 0.375rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.875rem;
}
```

---

## 9. Implementation Roadmap

### Day 1: CDW Schema and Test Data Generation

**Tasks:**
1. Create `mock/sql-server/cdwwork/create/Dim.LabTest.sql`
   - Dimension table with LOINC codes
   - 8-10 lab panels (BMP, CBC, CMP, LFT, Lipid, etc.)
   - 50-60 individual test definitions
2. Create `mock/sql-server/cdwwork/create/Chem.LabChem.sql`
   - Fact table for lab results
   - Indexes for patient-centric and date range queries
3. Generate test data:
   - Create `mock/sql-server/cdwwork/insert/Dim.LabTest.sql`
   - Populate with 50-60 test definitions (see Appendix A for LOINC codes)
   - Create `mock/sql-server/cdwwork/insert/Chem.LabChem.sql`
   - Generate 80-100 lab results across 36 patients
   - 30% abnormal rate, mix of panels and individual tests
4. Apply schema and data to running SQL Server container
5. Verify with SQL queries (see Appendix B)

**Deliverables:**
- [ ] `mock/sql-server/cdwwork/create/Dim.LabTest.sql`
- [ ] `mock/sql-server/cdwwork/create/Chem.LabChem.sql`
- [ ] `mock/sql-server/cdwwork/insert/Dim.LabTest.sql`
- [ ] `mock/sql-server/cdwwork/insert/Chem.LabChem.sql`
- [ ] SQL verification queries document

**Time Estimate:** 4-5 hours

---

### Day 2: Bronze and Silver ETL

**Tasks:**
1. Create `etl/bronze_labs.py`:
   - SQL query to extract from `Chem.LabChem` with JOINs to `Dim.LabTest`, `SPatient.SPatient`, `Dim.Location`
   - Filter `VistaPackage = 'CH'` (Chemistry only)
   - Write to MinIO `bronze/cdwwork/labs`
2. Create `etl/silver_labs.py`:
   - Patient identity resolution (PatientSID → PatientICN)
   - Date standardization (ISO 8601)
   - Numeric result parsing (handle "<5.0", ">1000", "Positive", etc.)
   - Reference range parsing ("135 - 145" → low=135, high=145)
   - Abnormal flag standardization
   - Write to MinIO `silver/labs`
3. Test Bronze and Silver scripts
4. Verify Parquet file schemas with Polars

**Deliverables:**
- [ ] `etl/bronze_labs.py`
- [ ] `etl/silver_labs.py`
- [ ] Bronze Parquet file in MinIO: `bronze/cdwwork/labs`
- [ ] Silver Parquet file in MinIO: `silver/labs`

**Time Estimate:** 5-6 hours

---

### Day 3: Gold ETL and PostgreSQL Schema

**Tasks:**
1. Create `etl/gold_labs.py`:
   - Patient-centric grouping by ICN
   - Panel grouping by AccessionNumber
   - Result sorting (most recent first)
   - Panel rollups (count, abnormal count)
   - Trending test extraction (Glucose, Creatinine, Hemoglobin, Potassium)
   - Write to MinIO `gold/labs`
2. Create `db/ddl/create_patient_lab_results_table.sql`:
   - Table schema with indexes
   - Apply to PostgreSQL container
3. Create `etl/load_labs.py`:
   - Read Gold Parquet
   - Flatten nested panels → results
   - Bulk load to PostgreSQL
4. Test full ETL pipeline end-to-end
5. Verify PostgreSQL data with SQL queries

**Deliverables:**
- [ ] `etl/gold_labs.py`
- [ ] `db/ddl/create_patient_lab_results_table.sql`
- [ ] `etl/load_labs.py`
- [ ] Gold Parquet file in MinIO: `gold/labs`
- [ ] PostgreSQL table populated (80-100 rows)

**Time Estimate:** 5-6 hours

---

### Day 4: API Routes and Database Queries

**Tasks:**
1. Create `app/db/labs.py`:
   - `get_recent_panels()` (widget)
   - `get_trending_tests()` (widget sparklines)
   - `get_all_lab_results()` (full page with filters)
   - `get_test_trend()` (graph data)
2. Create `app/routes/labs.py`:
   - `GET /patient/{icn}/labs/widget` (widget endpoint)
   - `GET /patient/{icn}/labs` (full page endpoint)
   - `GET /patient/{icn}/labs/trend/{lab_test_sid}` (graph data endpoint)
3. Register router in `app/main.py`
4. Test endpoints with curl/Postman

**Deliverables:**
- [ ] `app/db/labs.py`
- [ ] `app/routes/labs.py`
- [ ] Router registered in `app/main.py`
- [ ] API endpoint tests (manual or automated)

**Time Estimate:** 5-6 hours

---

### Day 5: Widget UI Implementation (3x1)

**Tasks:**
1. Create `app/templates/partials/labs_widget.html`:
   - Hybrid layout: 3 panels + trending section
   - Panel cards with key results
   - Abnormal flag indicators
   - Mini Chart.js sparklines for trending tests
   - "View All Labs" link
2. Update `app/static/styles.css` (add widget styles)
3. Update `app/templates/dashboard.html` to include 3x1 labs widget
   - Adjust grid layout to accommodate full-width widget
4. Test widget rendering with multiple patients:
   - Patient with multiple panels
   - Patient with abnormal results
   - Patient with no lab results
5. Verify HTMX behavior and responsive design

**Deliverables:**
- [ ] `app/templates/partials/labs_widget.html`
- [ ] Updated `app/static/styles.css` (widget section)
- [ ] Updated `app/templates/dashboard.html` (3x1 grid support)
- [ ] Widget screenshots for documentation

**Time Estimate:** 4-5 hours

---

### Day 6: Full Page UI - Table View

**Tasks:**
1. Create `app/templates/patient_labs.html`:
   - Page header with breadcrumb
   - Filter controls (date range, abnormal only)
   - Panel-grouped table with expandable rows
   - Sortable columns (date, test name, result)
   - Pagination controls (20/30/50/100 per page)
2. Update `app/static/styles.css` (add table styles)
3. Test table rendering:
   - Panel grouping (expand/collapse)
   - Abnormal flag icons
   - Sorting functionality
   - Pagination with different page sizes
4. Test HTMX interactions (filters, sorting, pagination)

**Deliverables:**
- [ ] `app/templates/patient_labs.html` (table section)
- [ ] Updated `app/static/styles.css` (table styles)
- [ ] Panel expand/collapse JavaScript
- [ ] HTMX functionality verified

**Time Estimate:** 4-5 hours

---

### Day 7: Chart.js Integration (DEFERRED) ⏸️

**Original Plan:** Implement Chart.js sparklines in widget and full-page trending charts

**What Was Attempted:**
1. Added Chart.js 4.4.1 library to `base.html`
2. Implemented sparkline canvases in widget trending section
3. Created JavaScript initialization with Chart.js line charts
4. Added CSS styling for chart containers
5. Implemented safeguards against re-initialization

**Issues Encountered:**
- **HTMX Content Swapping Timing**: Widget is loaded dynamically via HTMX, causing chart initialization/destruction conflicts
- **Chart Lifecycle Management**: Inline scripts in HTMX partials execute unpredictably during content swaps
- **Unreliable Display**: Charts would appear briefly then disappear, or work only after multiple hard refreshes
- **Global State Issues**: Safeguards prevented over-initialization but couldn't solve DOM destruction problem

**Root Cause:**
Chart.js requires stable DOM elements for canvas rendering. When HTMX swaps widget content, canvases are destroyed and recreated, but the inline script's global flag prevents re-execution. This creates orphaned Chart.js instances referencing destroyed DOM elements.

**Decision: Revert to Simple Placeholders**
- Restored simple text-based trend indicators: `<i class="fa-solid fa-chart-line"></i> X points`
- Removed Chart.js library (not being used)
- Removed all chart initialization JavaScript
- Updated CSS to style placeholder indicators
- All trending **data infrastructure remains intact** (queries, data points, etc.)

**Rationale:**
- Widget sparklines are **nice-to-have**, not critical functionality
- Lab results table data is fully functional and provides core value
- Charting can be implemented more reliably on **full Labs page** (no HTMX complexity)
- Proper solution requires HTMX event listeners in base template, not inline scripts
- Time better spent on other clinical domains

**Deliverables:**
- [x] Trending data queries (working)
- [x] Widget trending section layout (working)
- [x] Simple placeholder indicators (reverted to this)
- [ ] ~~Chart.js sparklines~~ (deferred)
- [ ] ~~Full-page trending chart~~ (deferred)

**Future Implementation Path** (when revisited):
1. Move chart initialization to separate static JS file: `app/static/js/labs-charts.js`
2. Use HTMX event listeners in base template: `htmx:afterSwap` event
3. Implement on full Labs page first (simpler, no HTMX widget complexity)
4. Consider using `hx-preserve` attribute to prevent canvas destruction
5. Or implement as separate chart modal/view (non-HTMX)

**Time Spent:** 3-4 hours (troubleshooting)
**Status:** ✅ Reverted to stable baseline, trending data infrastructure complete

---

### Day 8: Testing, Polish, and Documentation

**Tasks:**
1. Write unit tests (`tests/test_labs.py`):
   - Database query functions
   - ETL transformations (Bronze, Silver, Gold)
   - Reference range parsing
   - Panel grouping logic
2. Write integration tests:
   - API endpoint responses
   - Widget rendering
   - Full page rendering
   - Graph data endpoint
3. Manual testing checklist:
   - All 36 test patients
   - Different panel types (BMP, CBC, CMP, etc.)
   - Abnormal flag display (H, L, H*, L*, Panic)
   - Panel grouping and expansion
   - Filtering and pagination
   - Graph rendering with reference ranges
   - Mobile/tablet responsive design
4. Update documentation:
   - `app/README.md` (add Labs routing example)
   - `docs/spec/med-z1-architecture.md` (add 3x1 widget pattern, confirm Pattern B decision)
   - This design document (mark sections complete)
5. Code review and cleanup

**Deliverables:**
- [ ] `tests/test_labs.py` (unit and integration tests)
- [ ] Manual testing checklist (completed)
- [ ] Updated documentation
- [ ] Code review notes

**Time Estimate:** 5-6 hours

---

**Total Estimated Time:** 36-44 hours (approximately 1.5-2 weeks of full-time work, or 2-3 weeks with other responsibilities)

---

## 10. Testing Strategy

### 10.1 Unit Tests

**File:** `tests/test_labs.py`

**Coverage Areas:**
1. **Database Query Functions** (`app/db/labs.py`):
   - `test_get_recent_panels_returns_correct_limit()`
   - `test_get_recent_panels_groups_by_accession_number()`
   - `test_get_trending_tests_returns_correct_tests()`
   - `test_get_all_lab_results_filters_by_date_range()`
   - `test_get_all_lab_results_filters_abnormal_only()`
   - `test_get_all_lab_results_pagination()`
   - `test_get_test_trend_returns_ascending_dates()`
   - `test_date_filter_conversion()`

2. **ETL Transformations**:
   - `test_bronze_extraction_row_count()`
   - `test_silver_numeric_result_parsing()` (handles "<5.0", ">1000", "Positive")
   - `test_silver_reference_range_parsing()` ("135 - 145" → low=135, high=145)
   - `test_silver_abnormal_flag_standardization()`
   - `test_gold_panel_grouping()`
   - `test_gold_trending_test_extraction()`

**Example Test:**
```python
import pytest
from app.db.labs import get_recent_panels, parse_ref_range

def test_get_recent_panels_groups_by_accession_number(test_db_session):
    """Verify that recent panels are correctly grouped by AccessionNumber."""
    patient_icn = "ICN100001"

    # Fetch 2 most recent panels
    panels = get_recent_panels(test_db_session, patient_icn, limit=2)

    assert len(panels) == 2, "Should return exactly 2 panels"

    # Each panel should have multiple results
    for panel in panels:
        assert 'accession_number' in panel
        assert 'panel_name' in panel
        assert 'results' in panel
        assert len(panel['results']) > 0, "Each panel should have at least one result"

        # All results in panel should share same accession number
        for result in panel['results']:
            # (would check this in actual implementation)
            pass

def test_silver_reference_range_parsing():
    """Test parsing of various reference range formats."""
    assert parse_ref_range("135 - 145") == ("135", "145")
    assert parse_ref_range("<5.0") == (None, "5.0")
    assert parse_ref_range(">200") == ("200", None)
    assert parse_ref_range("Negative") == (None, None)
```

### 10.2 Integration Tests

**Coverage Areas:**
1. **API Endpoints**:
   - `test_widget_endpoint_returns_recent_panels()`
   - `test_full_page_endpoint_renders_html()`
   - `test_full_page_filtering_by_date_range()`
   - `test_full_page_abnormal_only_filter()`
   - `test_graph_data_endpoint_returns_time_series()`

2. **UI Rendering**:
   - `test_widget_html_contains_panel_cards()`
   - `test_widget_sparklines_render()`
   - `test_full_page_table_panel_grouping()`
   - `test_graph_reference_range_lines_display()`
   - `test_pagination_links_present()`

**Example Test:**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_widget_endpoint_returns_recent_panels():
    """Verify widget endpoint returns correct structure."""
    patient_icn = "ICN100001"
    response = client.get(f"/patient/{patient_icn}/labs/widget")

    assert response.status_code == 200
    data = response.json()

    assert "patient_icn" in data
    assert "recent_panels" in data
    assert "trending_tests" in data
    assert len(data["recent_panels"]) <= 3  # Max 3 panels for widget

    # Verify panel structure
    if len(data["recent_panels"]) > 0:
        panel = data["recent_panels"][0]
        assert "accession_number" in panel
        assert "panel_name" in panel
        assert "collection_datetime" in panel
        assert "results" in panel
        assert len(panel["results"]) > 0

def test_full_page_filtering_by_date_range():
    """Verify date range filter works correctly."""
    patient_icn = "ICN100001"

    # Get 30-day results
    response = client.get(f"/patient/{patient_icn}/labs?date_range=30d")
    assert response.status_code == 200
    # (Would verify that all results are within 30 days)

    # Get 1-year results
    response = client.get(f"/patient/{patient_icn}/labs?date_range=1yr")
    assert response.status_code == 200
    # (Would verify larger result set)
```

### 10.3 Manual Testing Checklist

**Pre-Deployment Checklist:**

- [ ] **Widget Display**:
  - [ ] Displays 3 recent lab panels in grid layout
  - [ ] Each panel shows 5-7 key test results
  - [ ] Abnormal flags display correctly (✓, ⚠️, 🔴)
  - [ ] Panel headers show panel name and collection date/time
  - [ ] Trending sparklines render for key tests (Glucose, Creatinine, etc.)
  - [ ] "View All Labs" link navigates to full page
  - [ ] Shows "No lab results available" for patients with no labs

- [ ] **Full Page View - Table**:
  - [ ] All lab results displayed in table
  - [ ] Panel grouping works (click to expand/collapse)
  - [ ] Expandable rows show all tests in panel
  - [ ] Abnormal flags display correctly in Flag column
  - [ ] Reference ranges display in separate column
  - [ ] Collection date and time formatted correctly

- [ ] **Full Page View - Graph**:
  - [ ] Test selection dropdown populated with all numeric tests
  - [ ] Selecting a test renders line chart
  - [ ] Reference range lines (low/high) display as red dashed lines
  - [ ] Data points colored by abnormal flag (green/orange/red)
  - [ ] Hover tooltips show exact value, date, flag, and reference range
  - [ ] X-axis shows dates in readable format
  - [ ] Y-axis shows test values with units
  - [ ] Graph updates when date range filter changes

- [ ] **Filtering**:
  - [ ] Date range filter: 30 days, 90 days, 6 months, 1 year, all
  - [ ] Abnormal only checkbox filters to show only H, L, H*, L*, Panic results
  - [ ] Filter changes update both table and graph
  - [ ] Filter combinations work (e.g., "30 days" + "Abnormal only")

- [ ] **Sorting**:
  - [ ] Collection date sorting (asc/desc)
  - [ ] Test name sorting (alphabetical)
  - [ ] Result value sorting (numeric, asc/desc)
  - [ ] Sort indicator shows current sort column and direction

- [ ] **Pagination**:
  - [ ] Pages show 20 results each (default)
  - [ ] "Next" and "Prev" buttons work correctly
  - [ ] Page selector dropdown (20/30/50/100) works
  - [ ] No pagination shown for patients with ≤20 results
  - [ ] Page count displays correctly ("Page X of Y")

- [ ] **Data Accuracy**:
  - [ ] All 80-100 test lab results display correctly
  - [ ] Panel grouping accurate (all BMP tests grouped together, etc.)
  - [ ] Abnormal flags match expected values (30% abnormal rate)
  - [ ] Reference ranges display correctly for each test
  - [ ] Numeric result parsing handles "<5.0", ">1000" correctly
  - [ ] LOINC codes display (if shown in UI)

- [ ] **HTMX Functionality**:
  - [ ] Filter changes reload table without full page refresh
  - [ ] Sorting changes reload table without full page refresh
  - [ ] Pagination loads new page without full page refresh
  - [ ] Test selection updates graph without full page refresh

- [ ] **Responsive Design**:
  - [ ] Widget readable on mobile (320px width)
  - [ ] Widget panels stack vertically on mobile
  - [ ] Trending section hidden on mobile (optional)
  - [ ] Full page table scrolls horizontally on small screens
  - [ ] Graph responsive on tablet/mobile
  - [ ] Touch-friendly controls on tablet/mobile

- [ ] **Accessibility**:
  - [ ] Keyboard navigation works (tab through filters, links)
  - [ ] Abnormal flag icons have alt text or aria-labels
  - [ ] Color contrast meets WCAG AA standards
  - [ ] Table headers properly associated with cells
  - [ ] Graph has accessible data table fallback (optional)

### 10.4 Test Data Coverage

**Patient Scenarios to Test:**

1. **Patient with multiple lab panels (ICN100001)**:
   - Verify widget shows 3 most recent panels
   - Verify full page shows all panels with pagination
   - Verify trending sparklines render

2. **Patient with all normal results (ICN100005)**:
   - Verify all results show green ✓ flag
   - Verify "Abnormal only" filter returns no results

3. **Patient with critical/panic values (ICN100010)**:
   - Verify red 🔴 flag displays
   - Verify critical values highlighted in table
   - Verify graph shows critical data points in red

4. **Patient with no lab results (ICN100036)**:
   - Verify widget shows "No lab results available"
   - Verify full page shows empty state message

5. **Patient with 50+ lab results (ICN100003)**:
   - Verify pagination appears
   - Verify pagination controls work
   - Verify graph renders with many data points

6. **Patient with non-numeric results (ICN100008)**:
   - Verify text results display ("Positive", "Negative")
   - Verify non-numeric results excluded from graph dropdown

---

## 11. Future Enhancements

### 11.1 Phase 2: Microbiology Labs (MI Package)

**Scope:**
- Add `VistaPackage = 'MI'` support
- Display organism identification and antibiotic sensitivity
- Text-heavy results require different UI (expandable text areas)
- Separate widget section or dedicated tab on full page

**Data Source:**
- CDWWork schema: `Micro.Microbiology` (separate table from Chemistry)
- VistA File #63.05 (Microbiology subfile)

**UI Changes:**
- Widget: Add "Microbiology" tab or separate section
- Full page: Add "Microbiology" tab alongside Chemistry
- Table: Additional columns for Organism, Sensitivity, Interpretation

**Estimated Effort:** 5-7 days (similar to Chemistry implementation)

### 11.2 Phase 3: Cytology and Anatomic Pathology (CY, AP Packages)

**Scope:**
- Add `VistaPackage IN ('CY', 'AP')` support
- Display pathology reports and cytology results
- Very text-heavy, often multi-paragraph reports

**UI Changes:**
- Full-text search capability
- Report viewer (modal or dedicated page)
- Possibly separate from Chemistry/Microbiology due to different workflow

**Estimated Effort:** 7-10 days (more complex due to report formatting)

### 11.3 Multi-Test Graph Overlay

**Scope:**
- Allow user to select multiple tests to overlay on same graph
- Requires dual Y-axes for different units (e.g., Glucose mg/dL vs Potassium mmol/L)
- Improves trend comparison (e.g., BUN and Creatinine together for renal function)

**Implementation:**
- Update graph endpoint to accept array of `lab_test_sid` values
- Chart.js configuration for multiple datasets
- UI: Multi-select dropdown or checkbox list

**Estimated Effort:** 3-4 days

### 11.4 Graph Zoom and Pan

**Scope:**
- Allow user to zoom in on specific date ranges within graph
- Pan left/right to view different time periods
- Reset to default view

**Implementation:**
- Chart.js zoom plugin
- Touch gesture support for mobile
- Zoom controls (buttons or mouse wheel)

**Estimated Effort:** 2-3 days

### 11.5 Lab Result Export (PDF, CSV)

**Scope:**
- Export filtered lab results to PDF or CSV
- PDF: Formatted report with header, patient info, table of results
- CSV: Raw data for further analysis in Excel/R/Python

**Implementation:**
- Backend: Generate PDF using ReportLab or WeasyPrint
- Backend: Generate CSV using Pandas
- UI: "Export" button with format selector dropdown

**Estimated Effort:** 3-4 days

### 11.6 Cumulative Result Views

**Scope:**
- Display all results for a single test in one table row
- Columns: Test name, multiple date columns with values
- Easier to see trends at a glance without graph

**Example:**
```
| Test       | 12/10 | 11/15 | 10/20 | 09/15 |
|------------|-------|-------|-------|-------|
| Glucose    | 105⚠️ | 98✓   | 102⚠️ | 95✓   |
| Creatinine | 1.1✓  | 1.0✓  | 0.9✓  | 0.9✓  |
```

**Implementation:**
- Pivot query to transform rows to columns
- UI: Toggle between "Chronological" and "Cumulative" view

**Estimated Effort:** 4-5 days

### 11.7 AI-Powered Result Interpretation

**Scope:**
- LLM-based interpretation of abnormal results
- Contextual explanations (e.g., "High glucose may indicate diabetes or pre-diabetes")
- Risk stratification (e.g., "Trending upward, recommend follow-up")

**Implementation:**
- Integrate with OpenAI API or local LLM
- Prompt engineering for medical interpretation
- Display interpretations in expandable sections or tooltips

**Estimated Effort:** 7-10 days (requires careful prompt design and validation)

### 11.8 Lab Alerts and Critical Value Notifications

**Scope:**
- Proactive alerts for critical/panic values
- Email or in-app notifications when new critical result arrives
- Alert log/history

**Implementation:**
- Background job to monitor new lab results
- Alert generation and delivery system
- UI: Alert badge, notification center

**Estimated Effort:** 5-7 days

---

## 12. Appendices

### Appendix A: Common Lab Tests with LOINC Codes

**Basic Metabolic Panel (BMP) - 7 Tests:**

| Test Name | LOINC Code | Units | Ref Range Low | Ref Range High |
|-----------|------------|-------|---------------|----------------|
| Sodium | 2951-2 | mmol/L | 135 | 145 |
| Potassium | 2823-3 | mmol/L | 3.5 | 5.0 |
| Chloride | 2075-0 | mmol/L | 98 | 107 |
| Carbon Dioxide (CO2) | 2028-9 | mmol/L | 22 | 29 |
| Blood Urea Nitrogen (BUN) | 3094-0 | mg/dL | 7 | 20 |
| Creatinine | 2160-0 | mg/dL | 0.7 | 1.3 |
| Glucose | 2345-7 | mg/dL | 70 | 100 |

**Complete Blood Count (CBC) - 8 Tests:**

| Test Name | LOINC Code | Units | Ref Range Low | Ref Range High |
|-----------|------------|-------|---------------|----------------|
| White Blood Cell Count (WBC) | 6690-2 | K/uL | 4.5 | 11.0 |
| Red Blood Cell Count (RBC) | 789-8 | M/uL | 4.5 | 5.9 |
| Hemoglobin | 718-7 | g/dL | 13.5 | 17.5 |
| Hematocrit | 4544-3 | % | 40 | 52 |
| Platelet Count | 777-3 | K/uL | 150 | 400 |
| Mean Corpuscular Volume (MCV) | 787-2 | fL | 80 | 100 |
| Mean Corpuscular Hemoglobin (MCH) | 785-6 | pg | 27 | 33 |
| MCH Concentration (MCHC) | 786-4 | g/dL | 32 | 36 |

**Comprehensive Metabolic Panel (CMP) - 14 Tests:**
(Includes all 7 BMP tests plus 7 additional tests)

| Test Name | LOINC Code | Units | Ref Range Low | Ref Range High |
|-----------|------------|-------|---------------|----------------|
| Calcium | 17861-6 | mg/dL | 8.5 | 10.5 |
| Total Protein | 2885-2 | g/dL | 6.0 | 8.3 |
| Albumin | 1751-7 | g/dL | 3.5 | 5.5 |
| Total Bilirubin | 1975-2 | mg/dL | 0.1 | 1.2 |
| Alkaline Phosphatase | 6768-6 | U/L | 30 | 120 |
| AST (Aspartate Aminotransferase) | 1920-8 | U/L | 10 | 40 |
| ALT (Alanine Aminotransferase) | 1742-6 | U/L | 7 | 56 |

**Liver Function Tests (LFT) - 6 Tests:**

| Test Name | LOINC Code | Units | Ref Range Low | Ref Range High |
|-----------|------------|-------|---------------|----------------|
| Total Bilirubin | 1975-2 | mg/dL | 0.1 | 1.2 |
| Direct Bilirubin | 1968-7 | mg/dL | 0.0 | 0.3 |
| Alkaline Phosphatase | 6768-6 | U/L | 30 | 120 |
| AST | 1920-8 | U/L | 10 | 40 |
| ALT | 1742-6 | U/L | 7 | 56 |
| Total Protein | 2885-2 | g/dL | 6.0 | 8.3 |

**Lipid Panel - 5 Tests:**

| Test Name | LOINC Code | Units | Ref Range Low | Ref Range High |
|-----------|------------|-------|---------------|----------------|
| Total Cholesterol | 2093-3 | mg/dL | 0 | 200 |
| LDL Cholesterol | 18262-6 | mg/dL | 0 | 100 |
| HDL Cholesterol | 2085-9 | mg/dL | 40 | 60 |
| Triglycerides | 2571-8 | mg/dL | 0 | 150 |
| VLDL Cholesterol | 13457-7 | mg/dL | 5 | 40 |

**Individual Tests (Not Part of Panels):**

| Test Name | LOINC Code | Units | Ref Range Low | Ref Range High |
|-----------|------------|-------|---------------|----------------|
| Hemoglobin A1c | 4548-4 | % | 4.0 | 5.6 |
| TSH (Thyroid Stimulating Hormone) | 3016-3 | mIU/L | 0.4 | 4.0 |
| PSA (Prostate Specific Antigen) | 2857-1 | ng/mL | 0.0 | 4.0 |
| Vitamin D, 25-Hydroxy | 1989-3 | ng/mL | 30 | 100 |
| B-Type Natriuretic Peptide (BNP) | 30934-4 | pg/mL | 0 | 100 |

**Urinalysis - 10 Tests:**

| Test Name | LOINC Code | Units | Ref Range |
|-----------|------------|-------|-----------|
| Color | 5778-6 | - | Yellow |
| Clarity | 5767-9 | - | Clear |
| Specific Gravity | 5811-5 | - | 1.005 - 1.030 |
| pH | 5803-2 | - | 4.5 - 8.0 |
| Protein | 5804-0 | - | Negative |
| Glucose | 5792-7 | - | Negative |
| Ketones | 5797-6 | - | Negative |
| Blood | 5794-3 | - | Negative |
| Leukocyte Esterase | 5799-2 | - | Negative |
| Nitrite | 5802-4 | - | Negative |

**Total Test Definitions:** 57 tests across 8 panels + 5 individual tests

---

### Appendix B: SQL Verification Queries

**B.1 Check Lab Test Dimension Table**

```sql
-- Verify Dim.LabTest populated correctly
SELECT
    LabTestSID,
    LabTestName,
    LoincCode,
    PanelName,
    Units,
    RefRangeLow,
    RefRangeHigh,
    VistaPackage,
    IsPanel
FROM Dim.LabTest
ORDER BY PanelName, LabTestName;
```

**B.2 Check Lab Result Count by Panel**

```sql
-- Count lab results grouped by panel
SELECT
    lt.PanelName,
    COUNT(*) AS ResultCount,
    SUM(CASE WHEN lc.AbnormalFlag IS NOT NULL THEN 1 ELSE 0 END) AS AbnormalCount
FROM Chem.LabChem lc
LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
WHERE lc.VistaPackage = 'CH'
GROUP BY lt.PanelName
ORDER BY ResultCount DESC;
```

**B.3 Check Patient with Most Lab Results**

```sql
-- Find patient with most lab results
SELECT TOP 1
    p.PatientICN,
    p.PatientName,
    COUNT(*) AS LabResultCount
FROM Chem.LabChem lc
LEFT JOIN SPatient.SPatient p ON lc.PatientSID = p.PatientSID
WHERE lc.VistaPackage = 'CH'
GROUP BY p.PatientICN, p.PatientName
ORDER BY LabResultCount DESC;
```

**B.4 Check Recent Panels for Test Patient**

```sql
-- Get recent lab panels for a specific patient (grouped by AccessionNumber)
SELECT
    lc.AccessionNumber,
    lt.PanelName,
    lc.CollectionDateTime,
    COUNT(*) AS TestCount,
    SUM(CASE WHEN lc.AbnormalFlag IS NOT NULL THEN 1 ELSE 0 END) AS AbnormalCount
FROM Chem.LabChem lc
LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
LEFT JOIN SPatient.SPatient p ON lc.PatientSID = p.PatientSID
WHERE p.PatientICN = 'ICN100001'  -- Test patient
  AND lc.VistaPackage = 'CH'
  AND lc.AccessionNumber IS NOT NULL
GROUP BY lc.AccessionNumber, lt.PanelName, lc.CollectionDateTime
ORDER BY lc.CollectionDateTime DESC;
```

**B.5 Check Abnormal Flag Distribution**

```sql
-- Check distribution of abnormal flags
SELECT
    AbnormalFlag,
    COUNT(*) AS Count,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Chem.LabChem WHERE VistaPackage = 'CH') AS DECIMAL(5,2)) AS Percentage
FROM Chem.LabChem
WHERE VistaPackage = 'CH'
GROUP BY AbnormalFlag
ORDER BY Count DESC;
```

**B.6 Check LOINC Code Coverage**

```sql
-- Verify LOINC codes populated
SELECT
    COUNT(*) AS TotalTests,
    SUM(CASE WHEN LoincCode IS NOT NULL THEN 1 ELSE 0 END) AS TestsWithLoinc,
    CAST(SUM(CASE WHEN LoincCode IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS LoincCoveragePercent
FROM Dim.LabTest;
```

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2025-12-16 | Claude Code | Initial design document for Laboratory Results (Chemistry) Phase 1. 3x1 widget (hybrid layout), simultaneous table + graph full page view, 90-day default, 20/page pagination. |
| v1.1 | 2025-12-16 | Claude Code | Updated Day 7 to document Chart.js sparkline attempt and decision to defer charting due to HTMX content swapping issues. Reverted to simple placeholder indicators. Trending data infrastructure complete and functional. |

---

**END OF DESIGN DOCUMENT**
