# Medications Design Specification - med-z1

**Document Version:** 1.4
**Date:** 2026-01-13 (VistA Real-Time Integration Complete)
**Status:** ✅ Phase 1 Complete (Days 1-8) | ✅ VistA Real-Time Integration Complete (Days 1-3) | Filter UI Enhancement Specified (Day 9 Pending)
**Implementation Phase:** Days 1-8 Complete + VistA Integration Complete | Day 9 Pending (Filter UI Refactoring)

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
9. [Filter UI Enhancement Specification](#9-filter-ui-enhancement-specification) ⭐ **NEW**
10. [Implementation Completion Summary](#10-implementation-completion-summary)
11. [Real-Time VistA Integration ("Refresh from VistA")](#11-real-time-vista-integration-refresh-from-vista) ⭐ **NEW**
12. [Testing Strategy](#12-testing-strategy)
13. [Security and Privacy](#13-security-and-privacy)
14. [Appendices](#14-appendices)
   - [Appendix A: Original Implementation Roadmap (Days 1-12 Plan)](#appendix-a-original-implementation-roadmap-days-1-12-plan)
   - [Appendix B: VistA File Mappings](#appendix-b-vista-file-mappings)
   - [Appendix C: Mock Data Summary](#appendix-c-mock-data-summary)
   - [Appendix D: Glossary](#appendix-d-glossary)
   - [Appendix E: Data Quality Issues](#appendix-e-data-quality-issues)

---

## 1. Overview

### 1.1 Purpose

The **Medications** domain provides comprehensive access to patient medication data from both outpatient and inpatient sources, enabling clinicians to:
- View current and recent medications at a glance (dashboard widget)
- Review complete medication history across care settings (full medications page)
- Identify active prescriptions, fills/refills, and inpatient administrations
- Track medication status (ACTIVE, DISCONTINUED, EXPIRED)
- Support safe prescribing through comprehensive medication reconciliation
- Identify controlled substances requiring special monitoring

Medications data is sourced from two primary VistA systems:
- **RxOut (Outpatient Pharmacy)** - Prescriptions written for outpatients, filled at VA pharmacies or CMOP (mail)
- **BCMA (Bar Code Medication Administration)** - Medications administered to inpatients at the bedside

### 1.2 Scope

**In Scope for Initial Implementation:**
- Mock CDW database schema (10 tables total):
  - **2 new Dimension tables:** `Dim.LocalDrug`, `Dim.NationalDrug`
  - **4 RxOut tables:** `RxOut.RxOutpat`, `RxOut.RxOutpatFill`, `RxOut.RxOutpatSig`, `RxOut.RxOutpatMedInstructions`
  - **4 BCMA tables:** `BCMA.BCMAMedicationLog`, `BCMA.BCMADispensedDrug`, `BCMA.BCMAAdditive`, `BCMA.BCMASolution`
- ETL pipeline: Bronze → Silver → Gold → PostgreSQL
- Dashboard widget (**2x1 size - wide**):
  - **Two-column layout:** Left = Outpatient (RxOut), Right = Inpatient (BCMA)
  - Shows 8-10 most recent medications (4-5 per column)
  - Each column has header with count badge ("4 Active" for outpatient, "5 Recent" for inpatient)
  - Displays medication name, dose, date, status
  - Controlled substance indicators (⚠️ + DEA schedule)
  - "View All Medications" link to full page
  - **Widget Location:** Dashboard second row, right side (next to Allergies widget 1x1)
- Full Medications page with:
  - **Chronological table view** (similar to Vitals pattern)
  - **Unified display** of RxOut and BCMA medications in a single timeline
  - Columns: Date, Medication Name, Dose, Route, Type (Inpt/Outpt), Status, Provider
  - Status badges (ACTIVE, DISCONTINUED, EXPIRED)
  - Controlled substance indicators (⚠️ C-II, C-III, C-IV)
  - Filtering by date range (30 days, 90 days, 6 months, 1 year, all)
  - Expandable row details (click to expand for full prescription/administration details)
- Read-only functionality
- Must-have features:
  1. ✅ Outpatient prescriptions (RxOut.RxOutpat)
  2. ✅ Prescription fills/refills (RxOut.RxOutpatFill)
  3. ✅ BCMA inpatient administration (BCMA.BCMAMedicationLog)
  4. ✅ Medication status (ACTIVE, DISCONTINUED, EXPIRED)
  5. ✅ Controlled substance indicators (DEA Schedule)

**Out of Scope for Initial Implementation:**
- Medication entry/editing (read-only for now)
- Drug-drug interaction (DDI) detection (deferred to AI/ML phase)
- Sig/Instructions display (RxOut.RxOutpatSig - defer to Phase 2)
- IV medications detail (BCMA additives/solutions - defer to Phase 2)
- Refills remaining display (defer to Phase 2)
- Medication reconciliation workflow
- Integration with CPRS/medication ordering
- Real-time medication alerts
- Advanced filtering (by drug class, provider, status)
- Medication adherence tracking
- Cost/pricing information

### 1.3 Key Design Decisions

1. **Widget: Two-Column Layout (2x1 size):** Widget uses wider 2x1 format with left column for outpatient medications and right column for inpatient medications
2. **Widget Placement:** Second row of dashboard, right side, next to Allergies widget (1x1)
3. **Unified Timeline View (Full Page):** Both RxOut (outpatient) and BCMA (inpatient) medications displayed in a single chronological table, sorted by date descending
4. **Visual Type Indicators:** Each medication has a badge showing source/type:
   - **"Outpatient"** badge for RxOut prescriptions (green background)
   - **"Inpatient"** badge for BCMA administrations (blue background)
5. **Chronological Table (Vitals Pattern):** Similar to Vitals full page, medications displayed in a sortable, filterable table
6. **Widget Shows Separated Sources:** Dashboard widget shows 4-5 medications per column (outpatient left, inpatient right) for clear source distinction
7. **Two-Table ETL:** Separate Gold/PostgreSQL tables for RxOut and BCMA, unified via UNION query in API for full page
8. **Drug Dimension Tables:** Create `Dim.LocalDrug` and `Dim.NationalDrug` to support future AI/ML and drug name standardization
9. **Controlled Substance Highlighting:** Visual indicators (⚠️ badge + DEA schedule) for controlled substances
10. **Status-Based Filtering:** Default view shows ACTIVE + recent (90 days) medications; user can expand to "All"
11. **VistA Alignment:**
    - RxOut schema mirrors VistA File #52 (PRESCRIPTION)
    - BCMA schema mirrors VistA File #53.79 (BCMA MEDICATION LOG)
12. **Expandable Details:** Click row to expand and show full prescription details (provider, pharmacy, quantity, days supply, etc.)

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Clinical Value:** Provide comprehensive medication history to support safe prescribing and medication reconciliation
2. **Unified View:** Demonstrate ability to combine outpatient and inpatient medication data in a single coherent interface
3. **Prove Complex Pattern:** Show ETL and UI patterns scale to complex multi-table domains (8 source tables)
4. **Foundation for AI/ML:** Establish data structures (drug dimensions) that support future DDI detection and medication-related analytics

### 2.2 Success Criteria

**Data Pipeline:**
- [x] Mock CDW dimension tables created: `Dim.LocalDrug`, `Dim.NationalDrug` with 50+ drugs (✅ 58 local drugs, 40 national drugs)
- [x] RxOut tables populated with 22+ prescriptions and 32+ fills across 10 patients (✅ 111 prescriptions, 31 fills)
- [x] BCMA tables populated with 20+ medication administrations across 8 inpatient stays (✅ 52 administration events)
- [x] Bronze ETL extracts all 10 tables to Parquet (✅ 5 Bronze Parquet files created)
- [x] Silver ETL harmonizes data and resolves drug lookups (LocalDrug → NationalDrug) (✅ 2 Silver files: 111 RxOut, 52 BCMA)
- [x] Gold ETL creates two patient-centric views: `gold_patient_medications_rxout` and `gold_patient_medications_bcma` (✅ 2 Gold files created)
- [x] PostgreSQL serving DB loaded with medication data (2 tables: `patient_medications_outpatient`, `patient_medications_inpatient`) (✅ 163 total records loaded)

**API:**
- [ ] `GET /api/patient/{icn}/medications` returns all medications (JSON, unified from both sources)
- [ ] `GET /api/patient/{icn}/medications/recent` returns recent medications for widget (last 90 days, both sources)
- [ ] `GET /api/patient/{icn}/medications/{medication_id}/details` returns full medication details
- [ ] `GET /api/dashboard/widget/medications/{icn}` returns medications widget HTML
- [ ] `GET /patient/{icn}/medications` renders full Medications page
- [ ] API performance < 1000ms for typical patient medication query (both sources)

**UI (Widget):**
- [ ] Widget displays on dashboard (**2x1 size - wide format**)
- [ ] **Two-column layout:**
  - [ ] Left column: Outpatient medications (4-5 most recent active RxOut prescriptions)
  - [ ] Right column: Inpatient medications (4-5 most recent BCMA administrations)
- [ ] Each column has header with count badge (e.g., "4 Active" for outpatient, "5 Recent" for inpatient)
- [ ] Each medication shows:
  - Medication name with dose (e.g., "METFORMIN HCL 500MG TAB")
  - Date (issue date for RxOut, administration date for BCMA)
  - Status (ACTIVE/DISCONTINUED for RxOut, GIVEN/HELD for BCMA)
- [ ] Controlled substances show ⚠️ indicator + DEA schedule
- [ ] "View All Medications" link at bottom navigates to full page
- [ ] Loading state and error handling work correctly
- [ ] Empty state for each column when no medications (e.g., "No outpatient medications" / "No inpatient medications")
- [ ] Widget positioned in dashboard second row, right side (next to Allergies widget)

**UI (Full Page):**
- [ ] Medications page accessible from sidebar navigation
- [ ] Chronological table view with columns:
  - Date (sortable)
  - Medication Name with Dose
  - Route (PO, IV, SC, etc.)
  - Type (badge: Inpatient/Outpatient or BCMA/RxOut)
  - Status (ACTIVE/DISCONTINUED/EXPIRED for RxOut; GIVEN/HELD/REFUSED for BCMA)
  - Provider
  - Controlled Substance indicator (if applicable)
- [ ] Default shows last 90 days, filterable to 30d/6mo/1yr/all
- [ ] Rows are expandable (click to show full details):
  - **RxOut details:** Prescription number, pharmacy, quantity, days supply, refills allowed/remaining, expiration date
  - **BCMA details:** Scheduled time, action type, administered by, ward, variance info
- [ ] Controlled substances highlighted with ⚠️ badge + DEA schedule (C-II, C-III, C-IV)
- [ ] Sort by date (descending by default), medication name, type
- [ ] Responsive design works on mobile/tablet
- [ ] Empty state when no medications in selected date range

**Quality:**
- [ ] Code follows established patterns from Demographics, Flags, Vitals, and Allergies
- [ ] Error handling for missing data (e.g., drug not found in dimension table)
- [ ] Logging for debugging
- [ ] Documentation complete

---

## 3. Prerequisites

### 3.1 Completed Work

Before starting Medications implementation, ensure:
- ✅ Dashboard framework complete
- ✅ Demographics widget functional
- ✅ Patient Flags widget functional
- ✅ Vitals widget functional
- ✅ Allergies widget functional
- ✅ PostgreSQL serving DB operational
- ✅ MinIO or local Parquet storage available
- ✅ ETL pipeline patterns established (Bronze/Silver/Gold)
- ✅ Chronological table UI pattern established (Vitals)

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

- `docs/implementation-roadmap.md` - Phase 6 medications implementation plan
- `docs/patient-dashboard-design.md` - Dashboard widget specifications
- `docs/vitals-design.md` - Chronological table UI pattern reference
- `docs/allergies-design.md` - Card-based UI and dimension table patterns
- `docs/spec/med-z1-architecture.md` - API routing patterns (Pattern A vs Pattern B)
- `docs/med-z1-plan.md` - Overall project plan
- VA VistA Pharmacy documentation (Outpatient Pharmacy PSO, BCMA)

---

## 4. Data Architecture

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

---

### 4.1 Source: Mock CDW (SQL Server)

**Ten tables in SQL Server:**

```
CDWWork Database

Dimension Tables (NEW - to be created):
  Dim.LocalDrug
    - Local facility drug file entries
    - Maps to VA Formulary local drug definitions

  Dim.NationalDrug
    - National Drug File (NDF) entries
    - Standardized drug names and NDC codes

RxOut Schema (Outpatient Pharmacy) - EXISTING:
  RxOut.RxOutpat
    - Main prescription table
    - One row per prescription order
    - Links to patient, provider, drug

  RxOut.RxOutpatFill
    - Fill/refill transactions
    - One row per fill (original + refills)
    - Links to RxOutpat (parent prescription)

  RxOut.RxOutpatSig
    - Structured dosing instructions (Sig codes)
    - One or more rows per prescription
    - Defer to Phase 2

  RxOut.RxOutpatMedInstructions
    - Additional medication instructions
    - Free-text and structured instructions
    - Defer to Phase 2

BCMA Schema (Inpatient Medication Administration) - EXISTING:
  BCMA.BCMAMedicationLog
    - Main medication administration log
    - One row per administration event (GIVEN, HELD, REFUSED, etc.)
    - Links to patient, inpatient stay, drug

  BCMA.BCMADispensedDrug
    - Dispensed drug details for inpatient orders
    - Defer detailed use to Phase 2

  BCMA.BCMAAdditive
    - IV additives (potassium, vitamins, etc.)
    - Defer to Phase 2

  BCMA.BCMASolution
    - IV solutions (NS, D5W, etc.)
    - Defer to Phase 2
```

### 4.2 VistA Source Context

#### RxOut (Outpatient Pharmacy)

The CDW `RxOut` domain is sourced from **VistA File #52 (PRESCRIPTION)**.

**Key VistA Fields (File #52):**
- Patient (DFN)
- Drug (pointer to File #50 - DRUG)
- Issue Date
- Provider
- Quantity
- Days Supply
- # of Refills
- Refills Remaining
- Prescription Number
- Status (ACTIVE, DISCONTINUED, EXPIRED, etc.)
- RX Type (MAIL, WINDOW, CMOP)
- DEA Schedule (for controlled substances)
- Pharmacy
- Clinic

**RxOut.RxOutpatFill** represents individual fill transactions:
- Fill Number (0 = original, 1+ = refills)
- Fill Date
- Released Date
- Dispensing Pharmacist
- Quantity Dispensed
- Fill Status
- Fill Cost

#### BCMA (Inpatient Medication Administration)

The CDW `BCMA` domain is sourced from **VistA File #53.79 (BCMA MEDICATION LOG)**.

**Key VistA Fields (File #53.79):**
- Patient (DFN)
- Inpatient stay (pointer to File #405 - MOVEMENT)
- Action Type (GIVEN, HELD, REFUSED, MISSING DOSE, etc.)
- Action Status (COMPLETED, PENDING, etc.)
- Action Date/Time (actual administration time)
- Scheduled Date/Time (when it was supposed to be given)
- Ordered Date/Time (when provider ordered it)
- Administered By (staff)
- Ordering Provider
- Drug (pointer to File #50 - DRUG)
- Dosage Ordered
- Dosage Given
- Route (PO, IV, IM, SC, etc.)
- Schedule (QD, BID, TID, Q4H, PRN, etc.)
- Ward Location
- Variance Flag (Y/N - if administration deviated from plan)
- Variance Type (HELD, REFUSED, LATE, etc.)
- Variance Reason
- Variance Comment (free text)
- IV Flag (Y/N)
- IV Type (IVPB, Continuous, etc.)
- Infusion Rate

**JLV Context:**
- JLV displays medications in a unified "Medications" tab
- Distinguishes between "Outpatient Meds" and "Inpatient Meds"
- Shows medication name, dose, route, frequency, status, provider
- Supports drill-down for full prescription/administration details

### 4.3 Medallion Pipeline

```
Mock CDW (SQL Server)
    ↓
Bronze Layer (Parquet)
  - Raw extraction, minimal transformation
  - 10 Parquet files (one per table):
    - bronze_dim_local_drug.parquet (NEW)
    - bronze_dim_national_drug.parquet (NEW)
    - bronze_rxout_rxoutpat.parquet
    - bronze_rxout_rxoutpatfill.parquet
    - bronze_rxout_rxoutpatsig.parquet (defer use to Phase 2)
    - bronze_rxout_rxoutpatmedinstructions.parquet (defer use to Phase 2)
    - bronze_bcma_medicationlog.parquet
    - bronze_bcma_dispenseddrug.parquet (defer use to Phase 2)
    - bronze_bcma_additive.parquet (defer use to Phase 2)
    - bronze_bcma_solution.parquet (defer use to Phase 2)
    ↓
Silver Layer (Parquet)
  - Cleaned, harmonized
  - Drug lookups resolved (LocalDrugSID → LocalDrug name → NationalDrug name)
  - Sta3n resolved to facility names
  - Provider lookups resolved
  - Two silver files for Phase 1:
    - silver_medications_rxout.parquet (RxOutpat + RxOutpatFill joined)
    - silver_medications_bcma.parquet (BCMAMedicationLog with lookups)
    ↓
Gold Layer (Parquet)
  - Patient-centric denormalized views
  - Two gold files:
    - gold_patient_medications_rxout.parquet
      - Prescription + latest fill joined
      - Drug names (local + national) denormalized
      - Status calculated (ACTIVE if not discontinued/expired)
      - Controlled substance flag added
    - gold_patient_medications_bcma.parquet
      - Administration events with drug names
      - Ward names, provider names denormalized
      - Action type standardized
    ↓
PostgreSQL Serving DB
  - Two tables:
    - patient_medications_outpatient (from gold_patient_medications_rxout)
    - patient_medications_inpatient (from gold_patient_medications_bcma)
  - API uses UNION query to merge both for unified display
```

### 4.4 PostgreSQL Serving Schema

**Two tables in PostgreSQL:**

1. **patient_medications_outpatient** - RxOut (outpatient prescriptions)
   - One row per prescription (may include latest fill info)
   - Key fields: patient_icn, drug_name_local, drug_name_national, issue_date, rx_status, dea_schedule, provider_name, pharmacy_name

2. **patient_medications_inpatient** - BCMA (inpatient administrations)
   - One row per medication administration event
   - Key fields: patient_icn, drug_name_local, drug_name_national, action_datetime, action_type, administered_by, ward_name

**Unified API Query Pattern:**
```sql
-- API performs UNION of both tables
SELECT * FROM (
  SELECT
    patient_icn,
    drug_name_local AS medication,
    issue_date AS date,
    'Outpatient' AS type,
    rx_status AS status,
    ...
  FROM patient_medications_outpatient
  WHERE patient_icn = :icn

  UNION ALL

  SELECT
    patient_icn,
    drug_name_local AS medication,
    action_datetime AS date,
    'Inpatient' AS type,
    action_type AS status,
    ...
  FROM patient_medications_inpatient
  WHERE patient_icn = :icn
) unified_meds
ORDER BY date DESC
```

---

## 5. Database Schema

### 5.1 Mock CDW Tables (SQL Server)

#### 5.1.1 NEW: Dim.LocalDrug

**Purpose:** Local facility drug file - maps to VA Formulary local drug definitions

**Schema:**
```sql
CREATE TABLE Dim.LocalDrug
(
  LocalDrugSID              BIGINT         NOT NULL PRIMARY KEY,
  LocalDrugIEN              VARCHAR(50)    NOT NULL,
  Sta3n                     SMALLINT       NOT NULL,
  NationalDrugSID           BIGINT         NULL,
  NationalDrugIEN           VARCHAR(50)    NULL,
  DrugNameWithoutDose       VARCHAR(120)   NULL,
  DrugNameWithDose          VARCHAR(150)   NULL,
  GenericName               VARCHAR(120)   NULL,
  VAProductName             VARCHAR(150)   NULL,
  Strength                  VARCHAR(50)    NULL,
  Unit                      VARCHAR(50)    NULL,
  DosageForm                VARCHAR(50)    NULL,  -- TAB, CAP, INJ, etc.
  DrugClass                 VARCHAR(100)   NULL,  -- e.g., "ANTIHYPERTENSIVE"
  DrugClassCode             VARCHAR(20)    NULL,
  ActiveIngredient          VARCHAR(120)   NULL,
  Inactive                  CHAR(1)        NULL,
  InactiveDate              DATETIME       NULL
);
```

**Indexes:**
```sql
CREATE INDEX IX_LocalDrugSID ON Dim.LocalDrug (LocalDrugSID);
CREATE INDEX IX_NationalDrugSID ON Dim.LocalDrug (NationalDrugSID);
CREATE INDEX IX_Sta3n ON Dim.LocalDrug (Sta3n);
```

**Sample Data (5-10 drugs):**
- METFORMIN HCL 500MG TAB
- LISINOPRIL 10MG TAB
- ATORVASTATIN CALCIUM 20MG TAB
- ALBUTEROL SULFATE HFA 90MCG INHALER
- TRAMADOL HCL 50MG TAB (C-IV)
- HYDROCODONE-ACETAMINOPHEN 5-325MG TAB (C-II)
- INSULIN GLARGINE 100UNIT/ML INJ
- WARFARIN SODIUM 5MG TAB
- CEFTRIAXONE SODIUM 1GM IVPB

#### 5.1.2 NEW: Dim.NationalDrug

**Purpose:** National Drug File (NDF) - standardized drug names and NDC codes

**Schema:**
```sql
CREATE TABLE Dim.NationalDrug
(
  NationalDrugSID           BIGINT         NOT NULL PRIMARY KEY,
  NationalDrugIEN           VARCHAR(50)    NOT NULL,
  NationalDrugName          VARCHAR(120)   NULL,
  GenericName               VARCHAR(120)   NULL,
  VAGenericName             VARCHAR(120)   NULL,
  TradeName                 VARCHAR(120)   NULL,
  NDCCode                   VARCHAR(20)    NULL,  -- National Drug Code
  DrugClass                 VARCHAR(100)   NULL,
  DrugClassCode             VARCHAR(20)    NULL,
  DEASchedule               VARCHAR(10)    NULL,  -- C-II, C-III, C-IV, C-V
  ControlledSubstanceFlag   CHAR(1)        NULL,
  ActiveIngredients         VARCHAR(250)   NULL,
  Inactive                  CHAR(1)        NULL,
  InactiveDate              DATETIME       NULL
);
```

**Indexes:**
```sql
CREATE INDEX IX_NationalDrugSID ON Dim.NationalDrug (NationalDrugSID);
CREATE INDEX IX_NDCCode ON Dim.NationalDrug (NDCCode);
CREATE INDEX IX_DEASchedule ON Dim.NationalDrug (DEASchedule);
```

**Sample Data (matching LocalDrug):**
- METFORMIN (generic antidiabetic)
- LISINOPRIL (ACE inhibitor)
- ATORVASTATIN (statin)
- ALBUTEROL (bronchodilator)
- TRAMADOL (opioid analgesic, C-IV)
- HYDROCODONE (opioid analgesic, C-II)
- INSULIN GLARGINE (long-acting insulin)
- WARFARIN (anticoagulant)
- CEFTRIAXONE (cephalosporin antibiotic)

#### 5.1.3 Existing RxOut Tables

**RxOut.RxOutpat** - Already created and populated with 22 prescriptions
- Key fields: RxOutpatSID, PatientSID, LocalDrugSID, NationalDrugSID, DrugNameWithDose, IssueDateTime, RxStatus, DEASchedule, ControlledSubstanceFlag, Quantity, DaysSupply, RefillsAllowed, RefillsRemaining

**RxOut.RxOutpatFill** - Already created and populated with 32 fills
- Key fields: RxOutpatFillSID, RxOutpatSID (FK), PatientSID, FillNumber, FillDateTime, ReleasedDateTime, FillStatus, QuantityDispensed

**RxOut.RxOutpatSig** - Already created (defer use to Phase 2)

**RxOut.RxOutpatMedInstructions** - Already created (defer use to Phase 2)

#### 5.1.4 Existing BCMA Tables

**BCMA.BCMAMedicationLog** - Already created and populated with 20 administrations
- Key fields: BCMAMedicationLogSID, PatientSID, InpatientSID, LocalDrugSID, NationalDrugSID, DrugNameWithDose, ActionType, ActionStatus, ActionDateTime, ScheduledDateTime, AdministeredByStaffSID, Route, Schedule, WardLocationSID, VarianceFlag, VarianceType, IVFlag

**BCMA.BCMADispensedDrug** - Already created (defer use to Phase 2)

**BCMA.BCMAAdditive** - Already created (defer use to Phase 2)

**BCMA.BCMASolution** - Already created (defer use to Phase 2)

### 5.2 PostgreSQL Serving DB Schema

#### 5.2.1 patient_medications_outpatient

**Purpose:** Denormalized outpatient prescription data for fast queries

**Schema:**
```sql
CREATE TABLE patient_medications_outpatient (
  id                          SERIAL PRIMARY KEY,
  patient_icn                 VARCHAR(50) NOT NULL,
  patient_key                 VARCHAR(100),
  rx_outpat_sid               BIGINT NOT NULL,
  rx_outpat_ien               VARCHAR(50),
  sta3n                       SMALLINT,
  facility_name               VARCHAR(100),

  -- Drug information
  local_drug_sid              BIGINT,
  national_drug_sid           BIGINT,
  drug_name_local             VARCHAR(150),
  drug_name_national          VARCHAR(120),
  drug_generic_name           VARCHAR(120),
  dosage_form                 VARCHAR(50),

  -- Prescription details
  prescription_number         VARCHAR(50),
  issue_date                  TIMESTAMP,
  rx_status                   VARCHAR(30),
  rx_type                     VARCHAR(30),  -- MAIL, WINDOW, CMOP

  -- Controlled substance
  dea_schedule                VARCHAR(10),
  controlled_substance_flag   CHAR(1),

  -- Quantity and supply
  quantity                    NUMERIC(12,4),
  days_supply                 INT,
  refills_allowed             INT,
  refills_remaining           INT,
  unit_dose                   VARCHAR(50),

  -- Dates
  expiration_date             TIMESTAMP,
  discontinued_date           TIMESTAMP,
  discontinue_reason          VARCHAR(100),

  -- Provider and pharmacy
  provider_sid                INT,
  provider_name               VARCHAR(100),
  ordering_provider_sid       INT,
  ordering_provider_name      VARCHAR(100),
  pharmacy_sid                INT,
  pharmacy_name               VARCHAR(100),
  clinic_name                 VARCHAR(100),

  -- Latest fill information (optional - from RxOutpatFill)
  last_fill_number            INT,
  last_fill_date              TIMESTAMP,
  last_released_date          TIMESTAMP,
  last_fill_status            VARCHAR(30),
  last_quantity_dispensed     NUMERIC(12,4),

  -- Metadata
  created_at                  TIMESTAMP DEFAULT NOW(),
  updated_at                  TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_patient_meds_outpt_icn ON patient_medications_outpatient(patient_icn);
CREATE INDEX idx_patient_meds_outpt_issue_date ON patient_medications_outpatient(issue_date DESC);
CREATE INDEX idx_patient_meds_outpt_status ON patient_medications_outpatient(rx_status);
CREATE INDEX idx_patient_meds_outpt_dea ON patient_medications_outpatient(dea_schedule) WHERE dea_schedule IS NOT NULL;
```

#### 5.2.2 patient_medications_inpatient

**Purpose:** Denormalized inpatient medication administration data for fast queries

**Schema:**
```sql
CREATE TABLE patient_medications_inpatient (
  id                          SERIAL PRIMARY KEY,
  patient_icn                 VARCHAR(50) NOT NULL,
  patient_key                 VARCHAR(100),
  bcma_med_log_sid            BIGINT NOT NULL,
  bcma_med_log_ien            VARCHAR(50),
  sta3n                       SMALLINT,
  facility_name               VARCHAR(100),

  -- Drug information
  local_drug_sid              BIGINT,
  national_drug_sid           BIGINT,
  drug_name_local             VARCHAR(150),
  drug_name_national          VARCHAR(120),
  drug_generic_name           VARCHAR(120),

  -- Inpatient stay
  inpatient_sid               BIGINT,
  inpatient_ien               VARCHAR(50),

  -- Administration details
  action_type                 VARCHAR(30),  -- GIVEN, HELD, REFUSED, MISSING DOSE
  action_status               VARCHAR(30),  -- COMPLETED, PENDING
  action_datetime             TIMESTAMP,
  scheduled_datetime          TIMESTAMP,
  ordered_datetime            TIMESTAMP,

  -- Dosage
  dosage_ordered              VARCHAR(100),
  dosage_given                VARCHAR(100),
  route                       VARCHAR(50),   -- PO, IV, IM, SC, etc.
  unit_of_administration      VARCHAR(50),

  -- Schedule
  schedule_type               VARCHAR(30),   -- SCHEDULED, PRN, CONTINUOUS
  schedule                    VARCHAR(50),   -- QD, BID, TID, Q4H PRN, etc.
  administration_unit         VARCHAR(50),

  -- Staff and location
  administered_by_staff_sid   INT,
  administered_by_name        VARCHAR(100),
  ordering_provider_sid       INT,
  ordering_provider_name      VARCHAR(100),
  ward_location_sid           INT,
  ward_name                   VARCHAR(100),

  -- Variance tracking
  variance_flag               CHAR(1),
  variance_type               VARCHAR(50),   -- HELD, REFUSED, LATE, etc.
  variance_reason             VARCHAR(100),
  variance_comment            VARCHAR(500),

  -- IV details
  iv_flag                     CHAR(1),
  iv_type                     VARCHAR(30),
  infusion_rate               VARCHAR(50),

  -- Metadata
  created_at                  TIMESTAMP DEFAULT NOW(),
  updated_at                  TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_patient_meds_inpt_icn ON patient_medications_inpatient(patient_icn);
CREATE INDEX idx_patient_meds_inpt_action_date ON patient_medications_inpatient(action_datetime DESC);
CREATE INDEX idx_patient_meds_inpt_action_type ON patient_medications_inpatient(action_type);
CREATE INDEX idx_patient_meds_inpt_inpatient_sid ON patient_medications_inpatient(inpatient_sid);
```

---

## 6. ETL Pipeline Design

### 6.1 Bronze Layer - Raw Extraction

**Script:** `etl/bronze_medications.py`

**Purpose:** Extract raw data from Mock CDW to Parquet files

**Tables to Extract (Phase 1 - Priority):**
1. `Dim.LocalDrug` → `bronze_dim_local_drug.parquet` (NEW - must create first)
2. `Dim.NationalDrug` → `bronze_dim_national_drug.parquet` (NEW - must create first)
3. `RxOut.RxOutpat` → `bronze_rxout_rxoutpat.parquet`
4. `RxOut.RxOutpatFill` → `bronze_rxout_rxoutpatfill.parquet`
5. `BCMA.BCMAMedicationLog` → `bronze_bcma_medicationlog.parquet`

**Deferred to Phase 2:**
- `RxOut.RxOutpatSig`
- `RxOut.RxOutpatMedInstructions`
- `BCMA.BCMADispensedDrug`
- `BCMA.BCMAAdditive`
- `BCMA.BCMASolution`

**Pseudocode:**
```python
def extract_medications_bronze():
    """
    Extract medications tables from CDW to Bronze Parquet
    """
    # Connect to SQL Server
    conn = get_cdw_connection()

    # Extract dimension tables (NEW)
    extract_table(conn, "Dim.LocalDrug", "bronze_dim_local_drug.parquet")
    extract_table(conn, "Dim.NationalDrug", "bronze_dim_national_drug.parquet")

    # Extract RxOut tables
    extract_table(conn, "RxOut.RxOutpat", "bronze_rxout_rxoutpat.parquet")
    extract_table(conn, "RxOut.RxOutpatFill", "bronze_rxout_rxoutpatfill.parquet")

    # Extract BCMA tables
    extract_table(conn, "BCMA.BCMAMedicationLog", "bronze_bcma_medicationlog.parquet")

    logging.info("Bronze extraction complete")
```

### 6.2 Silver Layer - Harmonization

**Script:** `etl/silver_medications.py`

**Purpose:** Clean, harmonize, and enrich data with lookups

**Two Silver Outputs:**
1. `silver_medications_rxout.parquet` - Outpatient prescriptions with fills
2. `silver_medications_bcma.parquet` - Inpatient administrations

**Transformations:**

**For RxOut:**
- Join `RxOutpat` + `RxOutpatFill` (left join to get latest fill per prescription)
- Resolve `LocalDrugSID` → `LocalDrug.DrugNameWithDose` and `NationalDrug.NationalDrugName`
- Resolve `Sta3n` → `Dim.Sta3n.FacilityName`
- Resolve `ProviderSID` → `SStaff.Staff.StaffName`
- Calculate `rx_status_computed` (ACTIVE if not discontinued and not expired)
- Add `controlled_substance_indicator` (Y/N based on DEASchedule)

**For BCMA:**
- Start with `BCMAMedicationLog`
- Resolve `LocalDrugSID` → drug names
- Resolve `Sta3n` → facility names
- Resolve `AdministeredByStaffSID` → staff names
- Resolve `OrderingProviderSID` → provider names
- Resolve `WardLocationSID` → ward names
- Standardize `ActionType` (capitalize, trim)

**Pseudocode:**
```python
def transform_medications_silver():
    """
    Transform Bronze to Silver with lookups and joins
    """
    # Load dimension tables
    local_drug_df = pl.read_parquet("bronze_dim_local_drug.parquet")
    national_drug_df = pl.read_parquet("bronze_dim_national_drug.parquet")
    sta3n_df = pl.read_parquet("bronze_dim_sta3n.parquet")
    staff_df = pl.read_parquet("bronze_sstaff_staff.parquet")

    # Transform RxOut
    rxoutpat_df = pl.read_parquet("bronze_rxout_rxoutpat.parquet")
    rxoutpatfill_df = pl.read_parquet("bronze_rxout_rxoutpatfill.parquet")

    # Get latest fill per prescription
    latest_fill = rxoutpatfill_df.sort("FillDateTime", descending=True).group_by("RxOutpatSID").first()

    # Join prescriptions with latest fill
    rxout_silver = (
        rxoutpat_df
        .join(latest_fill, on="RxOutpatSID", how="left", suffix="_fill")
        .join(local_drug_df, left_on="LocalDrugSID", right_on="LocalDrugSID", how="left")
        .join(national_drug_df, left_on="NationalDrugSID", right_on="NationalDrugSID", how="left")
        .join(sta3n_df, on="Sta3n", how="left")
        .join(staff_df, left_on="ProviderSID", right_on="StaffSID", how="left", suffix="_provider")
    )

    rxout_silver.write_parquet("silver_medications_rxout.parquet")

    # Transform BCMA
    bcma_df = pl.read_parquet("bronze_bcma_medicationlog.parquet")

    bcma_silver = (
        bcma_df
        .join(local_drug_df, left_on="LocalDrugSID", right_on="LocalDrugSID", how="left")
        .join(national_drug_df, left_on="NationalDrugSID", right_on="NationalDrugSID", how="left")
        .join(sta3n_df, on="Sta3n", how="left")
        .join(staff_df, left_on="AdministeredByStaffSID", right_on="StaffSID", how="left", suffix="_admin")
        .join(staff_df, left_on="OrderingProviderSID", right_on="StaffSID", how="left", suffix="_provider")
        # Ward lookup would go here if we have Dim.WardLocation
    )

    bcma_silver.write_parquet("silver_medications_bcma.parquet")

    logging.info("Silver transformation complete")
```

### 6.3 Gold Layer - Patient-Centric Views

**Script:** `etl/gold_patient_medications.py`

**Purpose:** Create denormalized patient-centric medication views

**Two Gold Outputs:**
1. `gold_patient_medications_rxout.parquet`
2. `gold_patient_medications_bcma.parquet`

**Transformations:**

**For RxOut Gold:**
- Select and rename columns for consistency
- Add `patient_icn` (from PatientIEN or derived)
- Add computed columns:
  - `is_controlled_substance` (boolean)
  - `is_active` (boolean: not discontinued and not expired)
  - `days_until_expiration` (if active)
- Sort by `IssueDateTime` descending

**For BCMA Gold:**
- Select and rename columns for consistency
- Add `patient_icn`
- Add computed columns:
  - `administration_variance` (boolean: variance_flag = 'Y')
  - `is_iv_medication` (boolean: iv_flag = 'Y')
- Sort by `ActionDateTime` descending

**Pseudocode:**
```python
def create_gold_patient_medications():
    """
    Create Gold layer patient-centric medication views
    """
    # Load Silver data
    rxout_df = pl.read_parquet("silver_medications_rxout.parquet")
    bcma_df = pl.read_parquet("silver_medications_bcma.parquet")

    # Create RxOut Gold
    rxout_gold = (
        rxout_df
        .with_columns([
            pl.col("PatientIEN").alias("patient_icn"),
            pl.col("DrugNameWithDose").alias("drug_name_local"),
            pl.col("NationalDrugName").alias("drug_name_national"),
            (pl.col("DEASchedule").is_not_null()).alias("is_controlled_substance"),
            (
                (pl.col("DiscontinuedDateTime").is_null()) &
                (pl.col("ExpirationDateTime") > pl.lit(datetime.now()))
            ).alias("is_active"),
        ])
        .sort("IssueDateTime", descending=True)
    )

    rxout_gold.write_parquet("gold_patient_medications_rxout.parquet")

    # Create BCMA Gold
    bcma_gold = (
        bcma_df
        .with_columns([
            pl.col("PatientIEN").alias("patient_icn"),
            pl.col("DrugNameWithDose").alias("drug_name_local"),
            pl.col("NationalDrugName").alias("drug_name_national"),
            (pl.col("VarianceFlag") == 'Y').alias("administration_variance"),
            (pl.col("IVFlag") == 'Y').alias("is_iv_medication"),
        ])
        .sort("ActionDateTime", descending=True)
    )

    bcma_gold.write_parquet("gold_patient_medications_bcma.parquet")

    logging.info("Gold layer creation complete")
```

### 6.4 PostgreSQL Load

**Script:** `etl/load_patient_medications.py`

**Purpose:** Load Gold Parquet into PostgreSQL serving tables

**Process:**
1. Drop and recreate `patient_medications_outpatient` table
2. Drop and recreate `patient_medications_inpatient` table
3. Load `gold_patient_medications_rxout.parquet` → `patient_medications_outpatient`
4. Load `gold_patient_medications_bcma.parquet` → `patient_medications_inpatient`
5. Create indexes
6. Verify row counts

**Pseudocode:**
```python
def load_medications_to_postgres():
    """
    Load Gold Parquet to PostgreSQL serving DB
    """
    # Connect to PostgreSQL
    conn = get_postgres_connection()

    # Load RxOut
    rxout_df = pl.read_parquet("gold_patient_medications_rxout.parquet")
    rxout_df.write_database("patient_medications_outpatient", conn, if_exists="replace")

    # Load BCMA
    bcma_df = pl.read_parquet("gold_patient_medications_bcma.parquet")
    bcma_df.write_database("patient_medications_inpatient", conn, if_exists="replace")

    # Create indexes (if not auto-created)
    create_indexes(conn)

    # Verify
    verify_load(conn)

    logging.info("PostgreSQL load complete")
```

---

## 7. API Endpoints

### 7.1 Medications API Endpoints

Following **Pattern B** from `docs/spec/med-z1-architecture.md` - Medications is a complex domain requiring dedicated router.

**File:** `app/routes/medications.py`

#### 7.1.1 GET /api/patient/{icn}/medications

**Purpose:** Get all medications for a patient (unified RxOut + BCMA)

**Query Parameters:**
- `date_from` (optional): ISO date string (default: 90 days ago)
- `date_to` (optional): ISO date string (default: today)
- `type_filter` (optional): "outpatient", "inpatient", or "all" (default: "all")
- `status_filter` (optional): "active", "discontinued", "expired", "all" (default: "all")

**Response:** JSON array of medications
```json
{
  "patient_icn": "1000000001V123456",
  "medications": [
    {
      "id": "rxout_5001",
      "type": "outpatient",
      "medication_name": "METFORMIN HCL 500MG TAB",
      "generic_name": "METFORMIN",
      "date": "2025-01-15T10:30:00",
      "status": "ACTIVE",
      "route": "PO",
      "provider": "Dr. Jane Smith",
      "facility": "VA PORTLAND",
      "controlled_substance": false,
      "dea_schedule": null
    },
    {
      "id": "bcma_9001",
      "type": "inpatient",
      "medication_name": "LISINOPRIL 10MG TAB",
      "generic_name": "LISINOPRIL",
      "date": "2025-01-01T08:05:00",
      "status": "GIVEN",
      "route": "PO",
      "administered_by": "Nurse John Doe",
      "ward": "4 WEST MEDICAL",
      "controlled_substance": false,
      "dea_schedule": null
    }
  ],
  "total_count": 45,
  "outpatient_count": 22,
  "inpatient_count": 23
}
```

**Implementation:**
```python
@router.get("/api/patient/{icn}/medications")
async def get_patient_medications(
    icn: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    type_filter: str = "all",
    status_filter: str = "all",
    db: Session = Depends(get_db)
):
    """
    Get all medications for patient (unified RxOut + BCMA)
    """
    # Query outpatient
    outpatient_query = db.query(PatientMedicationsOutpatient).filter(
        PatientMedicationsOutpatient.patient_icn == icn
    )

    if date_from:
        outpatient_query = outpatient_query.filter(
            PatientMedicationsOutpatient.issue_date >= date_from
        )

    if status_filter != "all":
        outpatient_query = outpatient_query.filter(
            PatientMedicationsOutpatient.rx_status == status_filter.upper()
        )

    outpatient_meds = outpatient_query.all()

    # Query inpatient
    inpatient_query = db.query(PatientMedicationsInpatient).filter(
        PatientMedicationsInpatient.patient_icn == icn
    )

    if date_from:
        inpatient_query = inpatient_query.filter(
            PatientMedicationsInpatient.action_datetime >= date_from
        )

    inpatient_meds = inpatient_query.all()

    # Merge and format
    medications = []

    for med in outpatient_meds:
        medications.append({
            "id": f"rxout_{med.rx_outpat_sid}",
            "type": "outpatient",
            "medication_name": med.drug_name_local,
            "generic_name": med.drug_generic_name,
            "date": med.issue_date.isoformat(),
            "status": med.rx_status,
            "route": "PO",  # Most outpatient are PO
            "provider": med.provider_name,
            "facility": med.facility_name,
            "controlled_substance": med.controlled_substance_flag == 'Y',
            "dea_schedule": med.dea_schedule
        })

    for med in inpatient_meds:
        medications.append({
            "id": f"bcma_{med.bcma_med_log_sid}",
            "type": "inpatient",
            "medication_name": med.drug_name_local,
            "generic_name": med.drug_generic_name,
            "date": med.action_datetime.isoformat(),
            "status": med.action_type,
            "route": med.route,
            "administered_by": med.administered_by_name,
            "ward": med.ward_name,
            "controlled_substance": False,  # Would need to join to NationalDrug
            "dea_schedule": None
        })

    # Sort by date descending
    medications.sort(key=lambda x: x["date"], reverse=True)

    return {
        "patient_icn": icn,
        "medications": medications,
        "total_count": len(medications),
        "outpatient_count": len(outpatient_meds),
        "inpatient_count": len(inpatient_meds)
    }
```

#### 7.1.2 GET /api/patient/{icn}/medications/recent

**Purpose:** Get recent medications for widget (last 90 days for outpatient ACTIVE, last 7 days for inpatient)

**Query Parameters:**
- `outpatient_limit` (optional): Max outpatient meds (default: 5)
- `inpatient_limit` (optional): Max inpatient meds (default: 5)

**Response:** JSON with separated outpatient and inpatient medications
```json
{
  "patient_icn": "1000000001V123456",
  "outpatient": [
    {
      "medication_name": "METFORMIN HCL 500MG TAB",
      "date": "2025-01-15",
      "status": "ACTIVE",
      "controlled_substance": false,
      "dea_schedule": null
    },
    {
      "medication_name": "TRAMADOL HCL 50MG TAB",
      "date": "2024-03-10",
      "status": "ACTIVE",
      "controlled_substance": true,
      "dea_schedule": "C-IV"
    },
    ...
  ],
  "inpatient": [
    {
      "medication_name": "LISINOPRIL 10MG TAB",
      "datetime": "2025-01-01T08:05:00",
      "action_type": "GIVEN",
      "controlled_substance": false
    },
    {
      "medication_name": "LEVOTHYROXINE 50MCG TAB",
      "datetime": "2025-01-02T20:05:00",
      "action_type": "HELD",
      "controlled_substance": false
    },
    ...
  ],
  "outpatient_count": 4,
  "inpatient_count": 5
}
```

#### 7.1.3 GET /api/patient/{icn}/medications/{medication_id}/details

**Purpose:** Get full details for a specific medication (for expandable row)

**Response:** JSON with full medication details

**For RxOut:**
```json
{
  "id": "rxout_5001",
  "type": "outpatient",
  "prescription_number": "2024-001-0001",
  "medication_name": "METFORMIN HCL 500MG TAB",
  "generic_name": "METFORMIN",
  "issue_date": "2025-01-15T10:30:00",
  "status": "ACTIVE",
  "rx_type": "MAIL",
  "quantity": 180,
  "days_supply": 90,
  "unit_dose": "1 TAB",
  "refills_allowed": 5,
  "refills_remaining": 3,
  "expiration_date": "2025-01-15",
  "provider": "Dr. Jane Smith",
  "pharmacy": "VA PORTLAND MAIN PHARMACY",
  "clinic": "PRIMARY CARE CLINIC",
  "controlled_substance": false,
  "dea_schedule": null,
  "last_fill": {
    "fill_number": 2,
    "fill_date": "2025-07-15T09:00:00",
    "quantity_dispensed": 90,
    "status": "COMPLETED"
  }
}
```

**For BCMA:**
```json
{
  "id": "bcma_9001",
  "type": "inpatient",
  "medication_name": "LISINOPRIL 10MG TAB",
  "generic_name": "LISINOPRIL",
  "action_type": "GIVEN",
  "action_status": "COMPLETED",
  "action_datetime": "2025-01-01T08:05:00",
  "scheduled_datetime": "2025-01-01T08:00:00",
  "ordered_datetime": "2025-01-01T03:45:00",
  "dosage_ordered": "10MG",
  "dosage_given": "10MG",
  "route": "PO",
  "schedule": "QD",
  "schedule_type": "SCHEDULED",
  "administered_by": "Nurse John Doe",
  "ordering_provider": "Dr. Jane Smith",
  "ward": "4 WEST MEDICAL",
  "variance_flag": false,
  "variance_type": null,
  "variance_reason": null,
  "iv_medication": false
}
```

#### 7.1.4 GET /api/dashboard/widget/medications/{icn}

**Purpose:** Return medications widget HTML (HTMX response for 2x1 widget)

**Response:** HTML fragment with two-column layout
```html
<div class="widget-content medications-widget widget-2x1">
  <div class="widget-header">
    <h3>Medications</h3>
  </div>

  <div class="medications-columns">
    <!-- Left Column: Outpatient -->
    <div class="medications-column outpatient-column">
      <div class="column-header">
        <h4>Outpatient (Active)</h4>
        <span class="badge badge-count">4</span>
      </div>
      <div class="medications-list">
        <div class="medication-item">
          <div class="med-name">METFORMIN HCL 500MG TAB</div>
          <div class="med-meta">
            <span class="med-date">01/15/2025</span>
            <span class="med-status status-active">ACTIVE</span>
          </div>
        </div>
        <!-- ... more outpatient meds ... -->
      </div>
    </div>

    <!-- Right Column: Inpatient -->
    <div class="medications-column inpatient-column">
      <div class="column-header">
        <h4>Inpatient (Recent)</h4>
        <span class="badge badge-count">5</span>
      </div>
      <div class="medications-list">
        <div class="medication-item">
          <div class="med-name">LISINOPRIL 10MG TAB</div>
          <div class="med-meta">
            <span class="med-date">01/01 08:05</span>
            <span class="med-status status-given">GIVEN</span>
          </div>
        </div>
        <!-- ... more inpatient meds ... -->
      </div>
    </div>
  </div>

  <a href="/patient/{icn}/medications" class="widget-footer-link">
    View All Medications →
  </a>
</div>
```

#### 7.1.5 GET /patient/{icn}/medications

**Purpose:** Render full Medications page (Jinja2 template)

**Response:** Full HTML page with chronological table

**Template:** `app/templates/medications.html`

---

## 8. UI/UX Design

### 8.1 Dashboard Widget

**Location:** Patient dashboard second row, right side (next to Allergies widget 1x1)
**Size:** 2x1 (wide widget - double width)

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ Medications                                                         │
├──────────────────────────────────┬──────────────────────────────────┤
│ Outpatient (Active)         [4]  │ Inpatient (Recent)          [5]  │
├──────────────────────────────────┼──────────────────────────────────┤
│ METFORMIN HCL 500MG TAB          │ LISINOPRIL 10MG TAB              │
│ 01/15/2025  ACTIVE               │ 01/01 08:05  GIVEN               │
│                                  │                                  │
│ LISINOPRIL 10MG TAB              │ METFORMIN HCL 500MG TAB          │
│ 01/15/2025  ACTIVE               │ 01/01 12:10  GIVEN               │
│                                  │                                  │
│ ATORVASTATIN 20MG TAB            │ SERTRALINE HCL 100MG TAB         │
│ 02/20/2024  ACTIVE               │ 02/02 21:10  GIVEN               │
│                                  │                                  │
│ ⚠️ TRAMADOL HCL 50MG TAB [C-IV]  │ HYDROCODONE 5-325MG [C-II]       │
│ 03/10/2024  ACTIVE               │ 01/02 14:35  GIVEN               │
│                                  │                                  │
│                                  │ LEVOTHYROXINE 50MCG TAB          │
│                                  │ 01/02 20:05  HELD                │
│                                  │                                  │
├──────────────────────────────────┴──────────────────────────────────┤
│                      View All Medications →                         │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Two-column layout** (left: outpatient, right: inpatient)
- **Left Column (Outpatient):**
  - Shows 4-5 most recent ACTIVE outpatient prescriptions (RxOut)
  - Each medication shows: name + dose, issue date, status (ACTIVE/DISCONTINUED)
  - Controlled substances show ⚠️ icon + DEA schedule
  - Header shows count of active prescriptions
- **Right Column (Inpatient):**
  - Shows 4-5 most recent inpatient administrations (BCMA)
  - Each medication shows: name + dose, administration date/time, action type (GIVEN/HELD/REFUSED)
  - Controlled substances show ⚠️ icon + DEA schedule
  - Header shows count of recent administrations
- Wider format allows more vertical space per medication for better readability
- "View All Medications →" link at bottom navigates to full page
- Empty states:
  - Left column: "No active outpatient medications"
  - Right column: "No recent inpatient administrations"

**HTML Structure:**
```html
<div class="widget medications-widget widget-2x1">
  <div class="widget-header">
    <h3>Medications</h3>
  </div>

  <div class="medications-columns">
    <!-- Left Column: Outpatient -->
    <div class="medications-column outpatient-column">
      <div class="column-header">
        <h4>Outpatient (Active)</h4>
        <span class="badge badge-count">4</span>
      </div>

      <div class="medications-list">
        <!-- Outpatient medication -->
        <div class="medication-item">
          <div class="med-name">METFORMIN HCL 500MG TAB</div>
          <div class="med-meta">
            <span class="med-date">01/15/2025</span>
            <span class="med-status status-active">ACTIVE</span>
          </div>
        </div>

        <div class="medication-item">
          <div class="med-name">LISINOPRIL 10MG TAB</div>
          <div class="med-meta">
            <span class="med-date">01/15/2025</span>
            <span class="med-status status-active">ACTIVE</span>
          </div>
        </div>

        <div class="medication-item">
          <div class="med-name">ATORVASTATIN 20MG TAB</div>
          <div class="med-meta">
            <span class="med-date">02/20/2024</span>
            <span class="med-status status-active">ACTIVE</span>
          </div>
        </div>

        <!-- Controlled substance -->
        <div class="medication-item controlled-substance">
          <div class="med-name">
            <span class="controlled-icon">⚠️</span>
            TRAMADOL HCL 50MG TAB
            <span class="dea-schedule">[C-IV]</span>
          </div>
          <div class="med-meta">
            <span class="med-date">03/10/2024</span>
            <span class="med-status status-active">ACTIVE</span>
          </div>
        </div>
      </div>

      <div class="empty-state" style="display: none;">
        No active outpatient medications
      </div>
    </div>

    <!-- Right Column: Inpatient -->
    <div class="medications-column inpatient-column">
      <div class="column-header">
        <h4>Inpatient (Recent)</h4>
        <span class="badge badge-count">5</span>
      </div>

      <div class="medications-list">
        <!-- Inpatient medication -->
        <div class="medication-item">
          <div class="med-name">LISINOPRIL 10MG TAB</div>
          <div class="med-meta">
            <span class="med-date">01/01 08:05</span>
            <span class="med-status status-given">GIVEN</span>
          </div>
        </div>

        <div class="medication-item">
          <div class="med-name">METFORMIN HCL 500MG TAB</div>
          <div class="med-meta">
            <span class="med-date">01/01 12:10</span>
            <span class="med-status status-given">GIVEN</span>
          </div>
        </div>

        <div class="medication-item">
          <div class="med-name">SERTRALINE HCL 100MG TAB</div>
          <div class="med-meta">
            <span class="med-date">02/02 21:10</span>
            <span class="med-status status-given">GIVEN</span>
          </div>
        </div>

        <!-- Controlled substance inpatient -->
        <div class="medication-item controlled-substance">
          <div class="med-name">
            <span class="controlled-icon">⚠️</span>
            HYDROCODONE 5-325MG TAB
            <span class="dea-schedule">[C-II]</span>
          </div>
          <div class="med-meta">
            <span class="med-date">01/02 14:35</span>
            <span class="med-status status-given">GIVEN</span>
          </div>
        </div>

        <div class="medication-item">
          <div class="med-name">LEVOTHYROXINE 50MCG TAB</div>
          <div class="med-meta">
            <span class="med-date">01/02 20:05</span>
            <span class="med-status status-held">HELD</span>
          </div>
        </div>
      </div>

      <div class="empty-state" style="display: none;">
        No recent inpatient administrations
      </div>
    </div>
  </div>

  <a href="/patient/{icn}/medications" class="widget-footer-link">
    View All Medications →
  </a>
</div>
```

**CSS Classes:**
```css
/* Widget 2x1 Layout */
.widget-2x1 {
  grid-column: span 2;  /* Takes 2 columns in dashboard grid */
}

.medications-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;  /* Two equal columns */
  gap: 1rem;
  padding: 1rem;
}

.medications-column {
  display: flex;
  flex-direction: column;
}

.outpatient-column {
  border-right: 1px solid #e0e0e0;
  padding-right: 0.5rem;
}

.inpatient-column {
  padding-left: 0.5rem;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.column-header h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.badge-count {
  background-color: #6c757d;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
}

/* Medication Items */
.medication-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.med-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 0.25rem;
}

.med-meta {
  font-size: 0.75rem;
  color: #666;
  display: flex;
  gap: 0.5rem;
}

.controlled-icon {
  color: #dc3545; /* red */
  font-size: 1rem;
}

.dea-schedule {
  color: #dc3545;
  font-weight: bold;
  font-size: 0.75rem;
}

.status-active {
  color: #28a745;
  font-weight: 600;
}

.status-given {
  color: #28a745;
  font-weight: 600;
}

.status-held {
  color: #ffc107;
  font-weight: 600;
}

.status-discontinued {
  color: #6c757d;
  font-weight: 600;
}

.empty-state {
  color: #999;
  font-style: italic;
  text-align: center;
  padding: 2rem 0;
}
```

### 8.2 Full Medications Page

**URL:** `/patient/{icn}/medications`
**Layout:** Chronological table (similar to Vitals page)

**Page Structure:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ [← Back to Dashboard]    Medications - Adam Dooree                  │
├─────────────────────────────────────────────────────────────────────┤
│ Filter: [Last 90 days ▼]  Type: [All ▼]  Status: [All ▼]           │
├─────────────────────────────────────────────────────────────────────┤
│ Date       │ Medication           │ Type      │ Status  │ Provider  │
├────────────┼──────────────────────┼───────────┼─────────┼───────────┤
│ 01/15/2025 │ METFORMIN HCL        │ Outpatient│ ACTIVE  │ Dr. Smith │
│  10:30 AM  │ 500MG TAB            │           │         │           │
│            │ [Click to expand for details]                          │
├────────────┼──────────────────────┼───────────┼─────────┼───────────┤
│ 01/01/2025 │ LISINOPRIL 10MG TAB  │ Inpatient │ GIVEN   │ Dr. Smith │
│  08:05 AM  │                      │ (BCMA)    │         │ (Admin:   │
│            │                      │           │         │  Nurse    │
│            │                      │           │         │  Doe)     │
├────────────┼──────────────────────┼───────────┼─────────┼───────────┤
│ 03/10/2024 │ ⚠️ TRAMADOL HCL 50MG│ Outpatient│ ACTIVE  │ Dr. Jones │
│  11:45 AM  │ TAB [C-IV]           │           │         │           │
│            │ CONTROLLED SUBSTANCE                                   │
├────────────┼──────────────────────┼───────────┼─────────┼───────────┤
│ ...        │ ...                  │ ...       │ ...     │ ...       │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
1. **Filtering:**
   - Date range: 30 days, 90 days, 6 months, 1 year, All
   - Type: All, Outpatient, Inpatient
   - Status: All, Active, Discontinued, Expired (for outpatient)

2. **Table Columns:**
   - **Date:** Date/time of issue (RxOut) or administration (BCMA)
   - **Medication:** Drug name with dose, controlled substance indicator
   - **Type:** Badge (Outpatient/Inpatient or RxOut/BCMA)
   - **Status:** ACTIVE/DISCONTINUED/EXPIRED (RxOut) or GIVEN/HELD/REFUSED (BCMA)
   - **Provider:** Prescribing provider (RxOut) or ordering provider (BCMA)
   - **Route:** PO, IV, IM, SC, etc. (mostly for BCMA)

3. **Expandable Rows:**
   - Click row to expand and show full details
   - **RxOut expanded view:**
     - Prescription number
     - Pharmacy name
     - Quantity and days supply
     - Refills allowed/remaining
     - Expiration date
     - Clinic
     - Last fill information (fill number, date, quantity)
   - **BCMA expanded view:**
     - Order number
     - Scheduled time vs actual administration time
     - Dosage ordered vs given
     - Route and schedule (QD, BID, PRN, etc.)
     - Administered by (nurse name)
     - Ward location
     - Variance information (if held/refused/late)

4. **Visual Indicators:**
   - Controlled substances: ⚠️ icon + red highlight + DEA schedule
   - Type badges: Color-coded (green for outpatient, blue for inpatient)
   - Status badges: Color-coded (green for ACTIVE/GIVEN, yellow for HELD, red for DISCONTINUED/REFUSED)

5. **Sorting:**
   - Default: Date descending (most recent first)
   - Allow sorting by: Date, Medication name, Type, Status

6. **Responsive Design:**
   - Mobile/tablet: Stack columns vertically, show medication name + type + date as primary info

**HTML Structure:**
```html
<div class="page-container medications-page">
  <div class="page-header">
    <a href="/patient/{icn}" class="back-link">← Back to Dashboard</a>
    <h1>Medications - Adam Dooree</h1>
  </div>

  <div class="filters">
    <select id="date-filter" class="form-select">
      <option value="30">Last 30 days</option>
      <option value="90" selected>Last 90 days</option>
      <option value="180">Last 6 months</option>
      <option value="365">Last 1 year</option>
      <option value="all">All</option>
    </select>

    <select id="type-filter" class="form-select">
      <option value="all" selected>All Types</option>
      <option value="outpatient">Outpatient Only</option>
      <option value="inpatient">Inpatient Only</option>
    </select>

    <select id="status-filter" class="form-select">
      <option value="all" selected>All Statuses</option>
      <option value="active">Active Only</option>
      <option value="discontinued">Discontinued</option>
      <option value="expired">Expired</option>
    </select>
  </div>

  <table class="medications-table">
    <thead>
      <tr>
        <th>Date</th>
        <th>Medication</th>
        <th>Type</th>
        <th>Status</th>
        <th>Provider</th>
      </tr>
    </thead>
    <tbody>
      <!-- Outpatient medication row -->
      <tr class="medication-row" data-id="rxout_5001">
        <td class="date-cell">
          01/15/2025<br>
          <span class="time">10:30 AM</span>
        </td>
        <td class="medication-cell">
          <strong>METFORMIN HCL 500MG TAB</strong><br>
          <span class="generic">Generic: METFORMIN</span>
        </td>
        <td class="type-cell">
          <span class="badge badge-outpatient">Outpatient</span>
        </td>
        <td class="status-cell">
          <span class="badge status-active">ACTIVE</span>
        </td>
        <td class="provider-cell">
          Dr. Jane Smith
        </td>
      </tr>
      <tr class="details-row" id="details-rxout-5001" style="display: none;">
        <td colspan="5">
          <div class="medication-details">
            <h4>Prescription Details</h4>
            <dl>
              <dt>Prescription Number:</dt>
              <dd>2024-001-0001</dd>

              <dt>Pharmacy:</dt>
              <dd>VA PORTLAND MAIN PHARMACY</dd>

              <dt>Quantity:</dt>
              <dd>180 tablets (90 day supply)</dd>

              <dt>Refills:</dt>
              <dd>3 remaining of 5 allowed</dd>

              <dt>Expiration:</dt>
              <dd>01/15/2026</dd>

              <dt>Clinic:</dt>
              <dd>PRIMARY CARE CLINIC</dd>

              <dt>Last Fill:</dt>
              <dd>Fill #2 on 07/15/2025 (90 tablets dispensed)</dd>
            </dl>
          </div>
        </td>
      </tr>

      <!-- Inpatient medication row -->
      <tr class="medication-row" data-id="bcma_9001">
        <td class="date-cell">
          01/01/2025<br>
          <span class="time">08:05 AM</span>
        </td>
        <td class="medication-cell">
          <strong>LISINOPRIL 10MG TAB</strong><br>
          <span class="generic">Generic: LISINOPRIL</span>
        </td>
        <td class="type-cell">
          <span class="badge badge-inpatient">Inpatient (BCMA)</span>
        </td>
        <td class="status-cell">
          <span class="badge status-given">GIVEN</span>
        </td>
        <td class="provider-cell">
          Dr. Jane Smith<br>
          <span class="admin-by">Admin: Nurse John Doe</span>
        </td>
      </tr>
      <tr class="details-row" id="details-bcma-9001" style="display: none;">
        <td colspan="5">
          <div class="medication-details">
            <h4>Administration Details</h4>
            <dl>
              <dt>Order Number:</dt>
              <dd>IP-2025-001001</dd>

              <dt>Scheduled Time:</dt>
              <dd>01/01/2025 08:00 AM</dd>

              <dt>Actual Time:</dt>
              <dd>01/01/2025 08:05 AM</dd>

              <dt>Dosage:</dt>
              <dd>10MG ordered, 10MG given</dd>

              <dt>Route:</dt>
              <dd>PO (by mouth)</dd>

              <dt>Schedule:</dt>
              <dd>QD (once daily)</dd>

              <dt>Administered By:</dt>
              <dd>Nurse John Doe</dd>

              <dt>Ward:</dt>
              <dd>4 WEST MEDICAL</dd>

              <dt>Variance:</dt>
              <dd>None</dd>
            </dl>
          </div>
        </td>
      </tr>

      <!-- Controlled substance row -->
      <tr class="medication-row controlled-substance" data-id="rxout_5005">
        <td class="date-cell">
          03/10/2024<br>
          <span class="time">11:45 AM</span>
        </td>
        <td class="medication-cell">
          <span class="controlled-icon">⚠️</span>
          <strong>TRAMADOL HCL 50MG TAB</strong>
          <span class="dea-schedule">[C-IV]</span><br>
          <span class="generic">Generic: TRAMADOL</span><br>
          <span class="controlled-label">CONTROLLED SUBSTANCE</span>
        </td>
        <td class="type-cell">
          <span class="badge badge-outpatient">Outpatient</span>
        </td>
        <td class="status-cell">
          <span class="badge status-active">ACTIVE</span>
        </td>
        <td class="provider-cell">
          Dr. Sarah Jones
        </td>
      </tr>

      <!-- More rows... -->
    </tbody>
  </table>

  <div class="empty-state" style="display: none;">
    <p>No medications found for the selected filters.</p>
  </div>
</div>
```

**JavaScript (HTMX + minimal custom):**
```javascript
// Toggle expandable row details
document.addEventListener('click', (e) => {
  if (e.target.closest('.medication-row')) {
    const row = e.target.closest('.medication-row');
    const id = row.dataset.id;
    const detailsRow = document.getElementById(`details-${id}`);

    if (detailsRow.style.display === 'none') {
      detailsRow.style.display = 'table-row';
    } else {
      detailsRow.style.display = 'none';
    }
  }
});

// Filter handling (HTMX trigger to reload table)
document.getElementById('date-filter').addEventListener('change', (e) => {
  htmx.trigger('#medications-table', 'reload');
});
```

---
## 9. Filter UI Enhancement Specification

**Document Version:** 1.2
**Date:** 2026-01-13
**Status:** Specification Complete - Implementation Pending
**Objective:** Refactor filter controls from button pills to dropdowns for improved space efficiency and consistency with Clinical Notes domain

### 9.1 Overview

This section specifies the enhancement of the Medications full page filter controls to improve UI density and consistency across clinical domains. The current implementation uses button pills for Time Period, Type, and Status filters, which consume significant vertical space and become cramped when the sidebar is expanded. The proposed solution converts these to dropdown `<select>` elements while maintaining all functionality and adding HTMX for automatic filtering.

**Key Benefits:**
- ✅ **Space efficiency:** Single-row layout when space permits (vs. current 3-4 rows)
- ✅ **Consistency:** Aligns with Clinical Notes domain (newest reference implementation)
- ✅ **Better UX:** No page reloads with HTMX automatic filtering
- ✅ **Predictable layout:** Filters remain in consistent positions (Status always visible)
- ✅ **Accessibility:** Improved keyboard navigation with native `<select>` elements
- ✅ **Future-proof:** Easy to extend with additional filter options

### 9.2 Current State vs. Proposed State

#### Current Implementation (Button Pills)

**Layout:** 3-4 rows of filter controls (stacked vertically)

```
Row 1: Time Period:  [30 Days] [90 Days] [6 Months] [1 Year] [All Time]
Row 2: Type:         [All (8)] [Outpatient (4)] [Inpatient (4)]
Row 3: Status:       [All Status] [Active (4)] [Expired] [Discontinued]  (conditional)
Row 4: Sort:         [Date (Newest First) ▼]
```

**Characteristics:**
- Button pills (`<a>` tags with `.filter-pill` class)
- Full page reload on filter change (URL navigation)
- Status filter conditionally hidden when Type = "Inpatient"
- Count badges in Type filter pills
- Each filter group in separate `.filter-group` container
- Responsive behavior: Pills wrap to multiple lines

**Space consumption:** ~180-220px vertical height (depending on Status visibility)

---

#### Proposed Implementation (Dropdowns with HTMX)

**Layout:** Single row when space permits, two rows on narrow viewports

**Single-Row Layout (>1200px viewport width, sidebar collapsed):**
```
[Time Period ▼] [Type ▼] [Status ▼] [Sort ▼]
```
*(Each label has a black-and-white FontAwesome icon prefix)*

**Two-Row Layout (≤1200px viewport width, sidebar expanded):**
```
Row 1: [Time Period ▼] [Type ▼]
Row 2: [Status ▼]      [Sort ▼]
```
*(Each label has a black-and-white FontAwesome icon prefix)*

**Characteristics:**
- Dropdown `<select>` elements for all filters
- HTMX form with automatic submission on change (no page reload)
- Status filter always visible (disabled when Type = "Inpatient")
- Count badges in dropdown options (e.g., "Outpatient (4)")
- Black-and-white FontAwesome icons in filter labels for visual hierarchy
- Single `.medications-filters` form container (following Clinical Notes pattern)
- Responsive behavior: Flexbox wrapping at defined breakpoint

**Space consumption:** ~50-60px vertical height (single row) or ~100-110px (two rows)
**Space savings:** ~60-70% reduction in vertical height

### 9.3 Design Specifications

#### 9.3.1 Filter Controls

**Time Period Filter:**
- **Label:** Time Period:
- **Icon:** `fa-calendar-days` (black-and-white FontAwesome icon)
- **Options:**
  ```
  Last 30 Days
  Last 90 Days (default)
  Last 6 Months
  Last Year
  All Time
  ```
- **Default:** 90 Days
- **Parameter:** `date_range` (values: 30, 90, 180, 365, "all")

**Type Filter:**
- **Label:** Type:
- **Icon:** `fa-pills` (black-and-white FontAwesome icon)
- **Options with counts:**
  ```
  All (8)
  Outpatient (4)
  Inpatient (4)
  ```
- **Default:** All
- **Parameter:** `medication_type` (values: "all", "outpatient", "inpatient")
- **Note:** Counts dynamically updated based on current data

**Status Filter:**
- **Label:** Status:
- **Icon:** `fa-circle-check` (black-and-white FontAwesome icon)
- **Options with counts:**
  ```
  All Statuses
  Active (4)
  Expired
  Discontinued
  ```
- **Default:** All Statuses
- **Parameter:** `status` (values: "all", "ACTIVE", "EXPIRED", "DISCONTINUED")
- **Behavior:**
  - Always visible (not conditional)
  - Disabled when Type = "Inpatient" (greyed out, not selectable)
  - When disabled, automatically reset to "All Statuses"
- **Note:** Only applies to outpatient medications

**Sort Control:**
- **Label:** Sort:
- **Icon:** `fa-sort` (black-and-white FontAwesome icon)
- **Options:**
  ```
  Date (Newest First) - default
  Date (Oldest First)
  Medication Name (A-Z)
  Type (Inpatient/Outpatient)
  ```
- **Default:** Date (Newest First)
- **Parameter:** `sort_by` (combined field + order)
- **Values:**
  - `date_desc` - Date (Newest First) [default]
  - `date_asc` - Date (Oldest First)
  - `drug_name` - Medication Name (A-Z)
  - `type` - Type (Inpatient/Outpatient)
- **Note:** Backend parses combined value into separate `sort_field` and `sort_order` for database queries

#### 9.3.2 Visual Design

**Filter Form Container:**
```css
.medications-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  padding: 1rem 1.5rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}
```

**Filter Group (Each filter):**
```css
.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group__label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.filter-group__label i {
  margin-right: 0.25rem;
  color: #6b7280;
}
```

**Dropdown Select Styling:**
```css
.filter-select {
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: #ffffff;
  background-image: url("data:image/svg+xml,..."); /* Dropdown arrow */
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1rem;
  font-size: 0.875rem;
  color: #111827;
  cursor: pointer;
  min-width: 150px;
  appearance: none;
  transition: border-color 0.15s ease;
}

.filter-select:hover {
  border-color: #9ca3af;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-select:disabled {
  background-color: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}
```

**Responsive Breakpoint:**
```css
/* Single-row layout (default) */
@media (min-width: 1201px) {
  .medications-filters {
    flex-wrap: nowrap;
  }
}

/* Two-row layout (sidebar expanded or narrow viewport) */
@media (max-width: 1200px) {
  .medications-filters {
    flex-wrap: wrap;
  }

  .filter-group:nth-child(1),
  .filter-group:nth-child(2) {
    /* Time Period and Type on first row */
    flex: 1 1 calc(50% - 0.5rem);
  }

  .filter-group:nth-child(3),
  .filter-group:nth-child(4) {
    /* Status and Sort on second row */
    flex: 1 1 calc(50% - 0.5rem);
  }
}

/* Mobile (stacked) */
@media (max-width: 768px) {
  .filter-group {
    flex: 1 1 100%;
  }
}
```

### 9.4 HTML Implementation

**Complete Filter Form (HTMX):**

```html
<!-- Filters and Controls -->
<div class="medications-controls">
    <!-- Filter Section -->
    <form class="medications-filters"
          hx-get="/patient/{{ patient.icn }}/medications"
          hx-target="#medications-table-container"
          hx-select="#medications-table-container"
          hx-swap="outerHTML"
          hx-push-url="true"
          hx-trigger="change">

        <!-- Time Period Filter -->
        <div class="filter-group">
            <label class="filter-group__label">
                <i class="fa-solid fa-calendar-days"></i>
                Time Period:
            </label>
            <select name="date_range" class="filter-select">
                <option value="30" {% if days_filter == 30 %}selected{% endif %}>Last 30 Days</option>
                <option value="90" {% if days_filter == 90 %}selected{% endif %}>Last 90 Days</option>
                <option value="180" {% if days_filter == 180 %}selected{% endif %}>Last 6 Months</option>
                <option value="365" {% if days_filter == 365 %}selected{% endif %}>Last Year</option>
                <option value="all" {% if days_filter == 'all' or days_filter == 3650 %}selected{% endif %}>All Time</option>
            </select>
        </div>

        <!-- Type Filter -->
        <div class="filter-group">
            <label class="filter-group__label">
                <i class="fa-solid fa-pills"></i>
                Type:
            </label>
            <select name="medication_type" class="filter-select">
                <option value="all" {% if medication_type_filter == 'all' %}selected{% endif %}>
                    All ({{ total_count }})
                </option>
                <option value="outpatient" {% if medication_type_filter == 'outpatient' %}selected{% endif %}>
                    Outpatient ({{ counts.outpatient_total or 0 }})
                </option>
                <option value="inpatient" {% if medication_type_filter == 'inpatient' %}selected{% endif %}>
                    Inpatient ({{ counts.inpatient_total or 0 }})
                </option>
            </select>
        </div>

        <!-- Status Filter (always visible, disabled for inpatient) -->
        <div class="filter-group">
            <label class="filter-group__label">
                <i class="fa-solid fa-circle-check"></i>
                Status:
            </label>
            <select name="status"
                    class="filter-select"
                    {% if medication_type_filter == 'inpatient' %}disabled{% endif %}>
                <option value="all" {% if not status_filter or status_filter == 'all' %}selected{% endif %}>
                    All Statuses
                </option>
                <option value="ACTIVE" {% if status_filter == 'ACTIVE' %}selected{% endif %}>
                    Active ({{ counts.outpatient_active or 0 }})
                </option>
                <option value="EXPIRED" {% if status_filter == 'EXPIRED' %}selected{% endif %}>
                    Expired
                </option>
                <option value="DISCONTINUED" {% if status_filter == 'DISCONTINUED' %}selected{% endif %}>
                    Discontinued
                </option>
            </select>
        </div>

        <!-- Sort Control -->
        <div class="filter-group">
            <label class="filter-group__label">
                <i class="fa-solid fa-sort"></i>
                Sort:
            </label>
            <select name="sort_by" class="filter-select">
                <option value="date_desc" {% if sort_by == 'date' and sort_order == 'desc' %}selected{% endif %}>
                    Date (Newest First)
                </option>
                <option value="date_asc" {% if sort_by == 'date' and sort_order == 'asc' %}selected{% endif %}>
                    Date (Oldest First)
                </option>
                <option value="drug_name" {% if sort_by == 'drug_name' %}selected{% endif %}>
                    Medication Name (A-Z)
                </option>
                <option value="type" {% if sort_by == 'type' %}selected{% endif %}>
                    Type (Inpatient/Outpatient)
                </option>
            </select>
        </div>
    </form>
</div>

<!-- Medications Table Container (HTMX target) -->
<div id="medications-table-container">
    <!-- Table content here (keep existing structure) -->
    <div class="medications-table-container">
        <table class="medications-table">
            <!-- Existing table structure unchanged -->
        </table>
    </div>

    <!-- Result Count -->
    <div class="results-count">
        Showing {{ total_count }} medication{{ 's' if total_count != 1 else '' }}
        {% if days_filter < 3650 %}
            from the last {% if days_filter == 30 %}30 days{% elif days_filter == 90 %}90 days{% elif days_filter == 180 %}6 months{% elif days_filter == 365 %}year{% endif %}
        {% endif %}
    </div>
</div>
```

### 9.5 HTMX Integration Pattern

The filter form uses HTMX to provide seamless, no-reload filtering following the Clinical Notes pattern:

**Key HTMX Attributes:**
- `hx-get="/patient/{icn}/medications"` - Endpoint to fetch filtered results
- `hx-target="#medications-table-container"` - Replace table container with response
- `hx-select="#medications-table-container"` - Extract only table container from response
- `hx-swap="outerHTML"` - Replace entire target element
- `hx-push-url="true"` - Update browser URL for bookmarkability
- `hx-trigger="change"` - Trigger on any select change

**Backend Route Updates:**

The existing `/patient/{icn}/medications` route needs minimal changes:

```python
@page_router.get("/patient/{icn}/medications")
async def get_patient_medications_page(
    request: Request,
    icn: str,
    date_range: str = "90",  # Changed from days to date_range
    medication_type: str = "all",
    status: Optional[str] = None,
    sort_by: str = "date_desc",  # Combined sort parameter
    db: Session = Depends(get_db),
):
    """
    Render full medications page with filtering.

    Supports both full page load and HTMX partial updates.
    """
    # Parse sort_by combined parameter
    if sort_by == "date_desc":
        sort_field, sort_order = "date", "desc"
    elif sort_by == "date_asc":
        sort_field, sort_order = "date", "asc"
    elif sort_by == "drug_name":
        sort_field, sort_order = "drug_name", "asc"
    elif sort_by == "type":
        sort_field, sort_order = "type", "asc"
    else:
        sort_field, sort_order = "date", "desc"

    # Convert date_range to days
    days_map = {"30": 30, "90": 90, "180": 180, "365": 365, "all": 3650}
    days_filter = days_map.get(date_range, 90)

    # Auto-reset status when type is inpatient
    if medication_type == "inpatient":
        status = None

    # Fetch medications (existing logic)
    medications = get_medications(
        icn=icn,
        db=db,
        days=days_filter,
        medication_type=medication_type,
        status=status,
        sort_by=sort_field,
        sort_order=sort_order
    )

    # ... rest of existing logic

    return templates.TemplateResponse(
        "patient_medications.html",
        context={
            "request": request,
            "patient": patient,
            "medications": medications,
            "total_count": len(medications),
            "counts": counts,
            "days_filter": days_filter,
            "date_range_filter": date_range,  # For dropdown selection
            "medication_type_filter": medication_type,
            "status_filter": status,
            "sort_by": sort_field,
            "sort_order": sort_order,
        }
    )
```

**JavaScript Enhancement (Optional):**

Add client-side logic to auto-reset Status when Type changes to "Inpatient":

```javascript
// Add to patient_medications.html or global JS
document.addEventListener('DOMContentLoaded', function() {
    const typeSelect = document.querySelector('select[name="medication_type"]');
    const statusSelect = document.querySelector('select[name="status"]');

    if (typeSelect && statusSelect) {
        typeSelect.addEventListener('change', function() {
            if (this.value === 'inpatient') {
                statusSelect.value = 'all';
                statusSelect.disabled = true;
            } else {
                statusSelect.disabled = false;
            }
        });
    }
});
```

### 9.6 Accessibility Enhancements

**Keyboard Navigation:**
- All filters are native `<select>` elements with full keyboard support
- Tab order: Time Period → Type → Status → Sort
- Arrow keys navigate dropdown options
- Enter/Space to open/select
- Escape to close dropdown

**Screen Reader Support:**
```html
<label class="filter-group__label" for="medication-type-filter">
    <i class="fa-solid fa-pills" aria-hidden="true"></i>
    Type:
</label>
<select name="medication_type"
        id="medication-type-filter"
        class="filter-select"
        aria-label="Filter medications by type">
    <option value="all">All ({{ total_count }})</option>
    <!-- ... -->
</select>
```

**Focus Indicators:**
```css
.filter-select:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .filter-select {
        border-width: 2px;
    }
}
```

### 9.7 Implementation Roadmap

**Day 9: Filter UI Refactoring (Estimated: 3-4 hours)**

#### Task Breakdown

**Task 1: Update HTML Template (1 hour)**
- [ ] Replace filter pills with HTMX form in `patient_medications.html`
- [ ] Add filter icons to labels
- [ ] Update dropdown options with count badges
- [ ] Add `#medications-table-container` wrapper
- [ ] Update sort control to use combined `sort_by` parameter
- [ ] Add Status filter auto-disable logic

**Task 2: Update CSS Styles (1 hour)**
- [ ] Add `.medications-filters` form container styles
- [ ] Add `.filter-group` and `.filter-group__label` styles
- [ ] Add `.filter-select` dropdown styles (normal, hover, focus, disabled)
- [ ] Add responsive breakpoint rules (1200px, 768px)
- [ ] Remove old `.filter-pills` styles (keep for backward compatibility initially)
- [ ] Test responsive behavior (sidebar collapsed/expanded)

**Task 3: Update Backend Route (30 minutes)**
- [ ] Update parameter names in `app/routes/medications.py`
  - `days` → `date_range`
  - Add `sort_by` combined parameter parsing
- [ ] Add auto-reset logic for Status when Type = "Inpatient"
- [ ] Update template context variables
- [ ] Test API response with HTMX request headers

**Task 4: Optional JavaScript Enhancement (30 minutes)**
- [ ] Add client-side Status reset on Type change
- [ ] Add form validation (if needed)
- [ ] Test cross-browser compatibility

**Task 5: Testing (1 hour)**
- [ ] Test all filter combinations
- [ ] Test HTMX partial updates (no page reload)
- [ ] Test URL state preservation (bookmarks work)
- [ ] Test responsive layouts at different viewport widths
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility
- [ ] Test with sidebar collapsed/expanded
- [ ] Test Status filter disabled state (Type = Inpatient)
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)

#### Acceptance Criteria

- [x] All filters use dropdown `<select>` elements
- [x] HTMX automatic filtering works (no page reload)
- [x] Single-row layout displays correctly when space permits
- [x] Two-row layout activates at 1200px breakpoint
- [x] Count badges display in dropdown options
- [x] Icons display in filter labels
- [x] Status filter always visible but disabled for Inpatient type
- [x] Sort dropdown maintains existing functionality
- [x] URL state preserved (bookmarkable filter combinations)
- [x] Keyboard navigation works flawlessly
- [x] Screen reader announces filter changes
- [x] Responsive behavior matches specification
- [x] All existing functionality maintained (no regressions)

### 9.8 Migration Strategy

**Backward Compatibility:**

During development, maintain both old and new filter implementations side-by-side:

1. **Phase 1:** Add new filter form, keep old pills hidden
2. **Phase 2:** Test new implementation thoroughly
3. **Phase 3:** Enable new filters, remove old pills
4. **Phase 4:** Clean up unused CSS

**Feature Flag (Optional):**

```python
# config.py
USE_DROPDOWN_FILTERS = True  # Toggle for testing

# patient_medications.html
{% if USE_DROPDOWN_FILTERS %}
    <!-- New dropdown filters -->
{% else %}
    <!-- Old button pill filters -->
{% endif %}
```

### 9.9 Benefits Summary

**Quantifiable Improvements:**
- **Space savings:** 60-70% reduction in filter control height
- **Fewer clicks:** Automatic HTMX filtering vs. page reload
- **Better consistency:** Aligns with 2 other clinical domains (Clinical Notes, Encounters page size selector)
- **Accessibility:** Native `<select>` elements vs. custom pill buttons

**User Experience:**
- ✅ Faster filtering (no page reload)
- ✅ Less scrolling (compact layout)
- ✅ Predictable interface (Status always visible)
- ✅ Better keyboard navigation
- ✅ Cleaner visual design

**Developer Experience:**
- ✅ Easier to maintain (standard form pattern)
- ✅ HTMX reduces JavaScript complexity
- ✅ Consistent pattern across domains
- ✅ Easy to extend with new filter options

---

## 10. Implementation Completion Summary

**Status:** ✅ **COMPLETE** (2025-12-13)

### 10.1 What Was Delivered

**Full Vertical Slice - Days 1-8 Completed:**

1. **ETL Pipeline (Days 1-4)** ✅
   - Bronze extraction: 5 Parquet files (drug dimensions, RxOut, BCMA)
   - Silver transformation: Drug lookups, harmonization, patient resolution
   - Gold curation: Patient-centric views with computed fields
   - PostgreSQL loading: 163 medication records across 2 tables

2. **API Endpoints (Day 5)** ✅
   - `GET /api/patient/{icn}/medications` - List with filters
   - `GET /api/patient/{icn}/medications/recent` - Dashboard widget data
   - `GET /api/patient/{icn}/medications/{medication_id}/details` - Single medication
   - `GET /api/dashboard/widget/medications/{icn}` - Widget HTML

3. **Dashboard Widget (Days 6-7)** ✅
   - 2x1 two-column layout (Outpatient left, Inpatient right)
   - Shows 4 most recent medications per column
   - Controlled substance badges with DEA schedule
   - HTMX-loaded, responsive to sidebar collapse/expand

4. **Full Medications Page (Day 8)** ✅
   - Chronological table view
   - Comprehensive filtering: Time Period, Type, Status
   - Sort options: Date, Drug Name, Type
   - Summary stats bar
   - Controlled substance highlighting
   - Responsive layout using full page width

5. **UI Polish** ✅
   - Active sidebar link for Medications
   - Responsive page layout (responds to sidebar collapse/expand)
   - Consistent styling with other clinical domain pages

### 10.2 User Acceptance

- User tested dashboard widget and full medications page
- User provided feedback on responsiveness and layout
- All feedback items addressed and implemented
- **User confirmed: "I consider Medications complete and operational"**

### 10.3 Deferred Features

The following features from the original implementation roadmap (see Appendix A) were deferred as the current implementation meets user requirements:

- **Original Day 9:** Expandable row details (click to expand full medication info) - *Deferred to future iteration*
- **Original Day 10:** Additional testing and visual polish - *Deferred to future iteration*
- **Original Day 11-12:** Documentation and review - *Deferred to future iteration*

**Note:** The Filter UI refactoring is now specified separately in Section 9 as a new enhancement (estimated 3-4 hours) and is the current priority for the next day of work on this domain.

### 10.4 Key Technical Achievements

1. **Unified Medication Model:** Successfully combined RxOut (outpatient) and BCMA (inpatient) into single coherent view
2. **Drug Dimension Hierarchy:** LocalDrug → NationalDrug lookups working correctly
3. **DEA Schedule Tracking:** Controlled substance identification and highlighting
4. **Patient ICN Resolution:** Clean mapping from source SIDs to ICN-based Gold layer
5. **Responsive UI Pattern:** Established consistent full-width responsive layout for all pages

### 10.5 Data Quality Notes

- **Patient Coverage:** 10 patients (ICN100001-ICN100010) with medications
- **Outpatient Medications:** 22 records (4 per patient average)
- **Inpatient Medications:** 20 records (administration events)
- **Controlled Substances:** 1 (HYDROCODONE-ACETAMINOPHEN)
- **Date Range:** Medications from 2024-2025 (older than 90-day default filter)

**Recommendation:** Users should use "All Time" or "1 Year" filter to see all medications in demo environment.

### 10.6 Files Created/Modified

**Created:**
- `etl/bronze_medications.py` (Bronze ETL script)
- `etl/silver_medications.py` (Silver ETL script)
- `etl/gold_patient_medications.py` (Gold ETL script)
- `etl/load_medications.py` (PostgreSQL loader)
- `db/ddl/create_patient_medications_tables.sql` (Database schema)
- `app/db/medications.py` (Database query layer, 409 lines)
- `app/routes/medications.py` (API routes, 326 lines)
- `app/templates/patient_medications.html` (Full page template, 320 lines)
- `app/templates/partials/medications_widget.html` (Widget template)
- Mock data SQL scripts (3 files: RxOutpat, RxOutpatFill, BCMAMedicationLog)

**Modified:**
- `app/main.py` (Added medication routers)
- `app/static/styles.css` (+500 lines for medications styling)
- `app/templates/base.html` (Activated medications sidebar link, fixed `.page-container` responsiveness)
- `docs/spec/medications-design.md` (This document - **updated 2026-01-13 with Section 9: Filter UI Enhancement Specification**)
- `docs/implementation-roadmap.md` (Phase 6 marked complete)

### 10.7 Success Metrics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| ETL Pipeline | Complete vertical slice | 163 records loaded | ✅ |
| API Endpoints | 4 functional endpoints | 4 tested and working | ✅ |
| Dashboard Widget | 2x1 HTMX widget | Live on dashboard | ✅ |
| Full Page | Table with filters | Fully functional | ✅ |
| User Acceptance | User confirms complete | Confirmed 2025-12-13 | ✅ |
| Sidebar Integration | Active link | Implemented | ✅ |
| Page Responsiveness | Responds to sidebar | Fixed and working | ✅ |

---

**Phase 6: Medications Domain - COMPLETE** ✅

**Implementation Date:** 2025-12-13 (1 day accelerated delivery)

---

## 11. Real-Time VistA Integration ("Refresh VistA")

**Added:** 2026-01-13
**Status:** ✅ **COMPLETE** (Implemented 2026-01-13)
**Actual Effort:** 3 days (Day 1: Mock data & handlers, Day 2-3: Backend/Frontend integration)
**Button Label:** "Refresh VistA" (standardized across all domains)

**Implementation Summary:**
- ✅ Day 1: Vista RPC handler (ORWPS COVER), mock data for 3 sites (69 medications), 30 unit tests passing
- ✅ Day 2-3: Parser functions, realtime endpoint, template updates, session cache integration
- ✅ Additional: Facility column added, provider field populated, status filter fixes, cache persistence for filter changes

### 11.1 Overview and Objectives

#### Purpose

Add "Refresh from VistA" functionality to the Medications page, enabling users to fetch real-time (T-0, today) medication data from VistA sites to complement historical PostgreSQL data (T-1 and earlier).

#### Key Objectives

1. **Real-Time Data Access**: Query VistA sites for active outpatient medications issued today (T-0)
2. **Multi-Site Aggregation**: Fetch from up to 3 VistA sites per patient (domain-specific limit)
3. **Seamless Merging**: Combine VistA responses with PostgreSQL data without duplicates
4. **Consistent UX**: Follow established "Refresh from VistA" pattern from Vitals, Encounters, Allergies domains
5. **Performance**: Complete refresh operation in <5 seconds (3 sites × 1-3 second latency)

#### Scope

**IN SCOPE:**
- ✅ Outpatient medications only (RxOut / VistA File #52)
- ✅ Active medications filter (STATUS='ACTIVE')
- ✅ ORWPS COVER RPC (cover sheet - active meds summary)
- ✅ Multi-site querying (up to 3 sites per patient)
- ✅ Canonical key deduplication: `{site}:{prescription_number}`
- ✅ Session-based caching (30-minute TTL)
- ✅ HTMX-based refresh button in page header
- ✅ All 4 test patients (ICN100001, ICN100010, ICN100013, ICN100002)

**OUT OF SCOPE (Future Phases):**
- ❌ Inpatient medications (BCMA) - defer to Phase 6+
- ❌ Additional RPCs (ORWPS DETAIL, ORWPS ACTIVE, PSO SUPPLY)
- ❌ Historical date-range queries (last 90 days, etc.)
- ❌ Prescription detail drill-down (single RX detail view)
- ❌ Refill history from VistA

---

### 11.2 VistA RPC Specification

#### RPC: ORWPS COVER

**Purpose:** Retrieve active outpatient medications for a patient (medication "cover sheet")

**Namespace:** ORWPS (Order Entry/Results Reporting - Pharmacy)

**Parameters:**
- `DFN` (string): Site-specific patient identifier (resolved from ICN automatically)

**Response Format:** Multi-line string, one medication per line, caret-delimited (^)

**Field Structure (7 fields):**
```
RX_NUMBER^DRUG_NAME^STATUS^QUANTITY/DAYS_SUPPLY^REFILLS_REMAINING^ISSUE_DATE^EXPIRATION_DATE
```

**Field Definitions:**

1. **RX_NUMBER** (string): Prescription number (unique identifier at site)
   - Example: `2860066`
   - Format: Numeric string, typically 7 digits
   - **Critical for deduplication**: Used as part of canonical event key

2. **DRUG_NAME** (string): Medication name (local drug name from VistA formulary)
   - Example: `LISINOPRIL 10MG TAB`
   - Format: Drug name + strength + dosage form
   - May differ from national drug name

3. **STATUS** (string): Prescription status
   - Values: `ACTIVE`, `DISCONTINUED`, `EXPIRED`, `SUSPENDED`
   - For this implementation: Filter to `ACTIVE` only

4. **QUANTITY/DAYS_SUPPLY** (string): Quantity dispensed / days supply
   - Example: `60/90` (60 tablets for 90 days)
   - Format: `{quantity}/{days_supply}`
   - Both are numeric, separated by forward slash

5. **REFILLS_REMAINING** (string): Number of refills left
   - Example: `3` (3 refills remaining)
   - Format: Single digit or number
   - `0` indicates no refills left

6. **ISSUE_DATE** (string): Date prescription was issued (FileMan format)
   - Example: `3241115.1035` (Nov 15, 2024 at 10:35)
   - Format: FileMan date/time (YYYMMDD.HHMM)
   - Must be parsed to ISO 8601 for PostgreSQL compatibility

7. **EXPIRATION_DATE** (string): Date prescription expires (FileMan format)
   - Example: `3251115.0000` (Nov 15, 2025)
   - Format: FileMan date (YYYMMDD)
   - Empty if not set

**Example Response:**

```
2860066^LISINOPRIL 10MG TAB^ACTIVE^60/90^3^3241115.1035^3251115
2860067^METFORMIN HCL 500MG TAB^ACTIVE^120/180^5^3241115.1030^3251115
2860068^ATORVASTATIN CALCIUM 20MG TAB^ACTIVE^30/30^11^3241110.0900^3251110
2860070^ASPIRIN 81MG TAB^ACTIVE^90/90^0^3241201.1420^3251201
```

**Error Handling:**

- **No medications**: Returns empty string (`""`)
- **Patient not found**: Returns empty string (DFN not valid at this site)
- **RPC not available**: HTTP 404 or error response from Vista service

---

### 11.3 Mock Data Schema and Examples

#### File Structure

Create 3 new JSON files in Vista data directory:
- `vista/app/data/sites/200/medications.json`
- `vista/app/data/sites/500/medications.json`
- `vista/app/data/sites/630/medications.json`

#### JSON Schema

```json
{
  "site_sta3n": "200",
  "site_name": "Alexandria VA Medical Center",
  "medications": [
    {
      "dfn": "100001",
      "rx_number": "2860066",
      "drug_name": "LISINOPRIL 10MG TAB",
      "status": "ACTIVE",
      "quantity": "60",
      "days_supply": "90",
      "refills_remaining": "3",
      "issue_date": "T-7.1035",
      "expiration_date": "T+358.0000",
      "_note": "ICN100001 (DOOREE, ADAM) - Chronic HTN medication"
    }
  ]
}
```

#### Field Specifications

| Field | Type | Required | T-Notation | Description |
|-------|------|----------|------------|-------------|
| `dfn` | string | Yes | No | Site-specific patient identifier |
| `rx_number` | string | Yes | No | Prescription number (7 digits typical) |
| `drug_name` | string | Yes | No | Drug name + strength + form |
| `status` | string | Yes | No | Always "ACTIVE" for this phase |
| `quantity` | string | Yes | No | Total quantity dispensed |
| `days_supply` | string | Yes | No | Number of days supply |
| `refills_remaining` | string | Yes | No | Refills left (0-11 typical) |
| `issue_date` | string | Yes | **YES** | FileMan date/time with T-notation |
| `expiration_date` | string | Yes | **YES** | FileMan date with T-notation |
| `_note` | string | No | No | Human-readable comment (ignored by parser) |

#### T-Notation Date Examples

**Issue Dates (Recent):**
- `T-0.0930` = Today at 09:30 (new prescription issued this morning)
- `T-1.1430` = Yesterday at 14:30 (filled yesterday)
- `T-7.1035` = 7 days ago at 10:35 (last week)
- `T-14.0800` = 14 days ago at 08:00 (2 weeks ago)
- `T-30.1200` = 30 days ago at 12:00 (last month)

**Expiration Dates (Future):**
- `T+30.0000` = 30 days from now (1 month supply)
- `T+90.0000` = 90 days from now (3 month supply)
- `T+365.0000` = 365 days from now (1 year from issue)

**Why T-Notation?**
- Ensures medications always appear "fresh" without daily manual updates
- Automatically calculates FileMan dates based on current system date
- Matches established pattern from Vitals, Encounters, Allergies domains

#### Mock Data Coverage Plan

**Site 200 (Alexandria) - 5 DFNs:**
- DFN 100001 (ICN100001): 6-8 active meds (chronic conditions)
- DFN 100010 (ICN100010): 5-7 active meds
- DFN 100020 (ICN100002): 5-6 active meds
- DFN 100002 (ICN100010 orphaned): 3-4 active meds (intentional overlap with 100010)
- DFN 100003 (ICN100013 orphaned): 4-5 active meds

**Site 500 (Anchorage) - 5 DFNs:**
- DFN 500001 (ICN100001): 5-7 active meds (**overlap with Site 200 DFN 100001**)
- DFN 500010 (ICN100010): 4-6 active meds (**overlap with Site 200 DFN 100010**)
- DFN 500020 (ICN100002): 5-6 active meds
- DFN 200001 (ICN100010 orphaned): 3-4 active meds
- DFN 200002 (ICN100013 orphaned): 4-5 active meds

**Site 630 (Palo Alto) - 6 DFNs:**
- DFN 630001 (ICN100001): 5-6 active meds (**overlap with Sites 200, 500**)
- DFN 630013 (ICN100013): 7-9 active meds (elder patient, polypharmacy)
- DFN 630020 (ICN100002): 4-5 active meds
- DFN 300001, 300002, 630002 (ICN100013 orphaned): 3-4 active meds each (**overlap with 630013**)

**Total Volume:** ~85-120 active medication records across 3 sites

**Deduplication Test Data:**
- Patient ICN100001: 2-3 medications with same RX_NUMBER at Sites 200, 500, 630
- Patient ICN100010: Orphaned DFNs duplicate some meds from primary DFNs
- Patient ICN100013: High DFN count (6 DFNs) stress tests deduplication

**Medication Mix:**
- **Chronic conditions** (60%): HTN (Lisinopril, Amlodipine), DM (Metformin, Glipizide), Hyperlipidemia (Atorvastatin, Simvastatin)
- **Cardiac** (20%): Beta-blockers (Metoprolol), Anticoagulants (Warfarin), Aspirin
- **Pain management** (10%): NSAIDs (Ibuprofen), Controlled substances (Hydrocodone C-II, Tramadol C-IV)
- **Other** (10%): PPIs (Omeprazole), Vitamins (Vitamin D), Inhalers (Albuterol)

**Controlled Substances:** 3-5 per site (Schedule II-IV) for testing `is_controlled_substance` flag

---

### 11.4 Vista RPC Handler Implementation

**File:** `vista/app/handlers/medications.py`

**Handler Class:** `MedicationsCoverHandler`

**RPC Name:** `ORWPS COVER`

#### Implementation Requirements

**1. Extend BaseRPCHandler**

```python
from vista.app.handlers.base import BaseRPCHandler
from vista.app.core.data_loader import DataLoader

class MedicationsCoverHandler(BaseRPCHandler):
    """
    Handler for ORWPS COVER RPC - Active outpatient medications (cover sheet).

    Returns active medications for a patient in VistA caret-delimited format.
    """

    def get_rpc_name(self) -> str:
        return "ORWPS COVER"

    def execute(self, params: list, site_sta3n: str, data_loader: DataLoader) -> str:
        """
        Execute ORWPS COVER RPC.

        Args:
            params: [DFN] - Patient DFN at this site
            site_sta3n: Site station number (200, 500, 630)
            data_loader: DataLoader instance for accessing medications.json

        Returns:
            Multi-line string with active medications (caret-delimited)
            Empty string if patient not found or no active medications
        """
```

**2. Parameter Validation**

- Require exactly 1 parameter (DFN)
- Validate DFN is non-empty string
- Return empty string if invalid (don't raise exception)

**3. Data Loading**

- Load `medications.json` for the specified site
- Filter medications by DFN
- Filter by status='ACTIVE' (only active meds)

**4. Date Conversion (T-Notation → FileMan)**

- Convert `issue_date` and `expiration_date` from T-notation to FileMan format
- Use existing T-notation parser from `data_loader.py` (lines 200-250)
- Example: `T-7.1035` → `3260106.1035` (Jan 6, 2026 at 10:35, assuming today is Jan 13, 2026)

**5. Response Formatting**

- Build multi-line string, one medication per line
- Format: `RX_NUMBER^DRUG_NAME^STATUS^QUANTITY/DAYS_SUPPLY^REFILLS_REMAINING^ISSUE_DATE^EXPIRATION_DATE`
- Join lines with newline (`\n`)
- Example:
  ```
  2860066^LISINOPRIL 10MG TAB^ACTIVE^60/90^3^3260106.1035^3270106
  2860067^METFORMIN HCL 500MG TAB^ACTIVE^120/180^5^3260106.1030^3270106
  ```

**6. Error Handling**

- Patient not found (DFN not in medications.json): Return empty string `""`
- No active medications: Return empty string `""`
- File not found: Raise exception (should not happen in normal operation)

**7. Unit Tests**

Create `vista/app/tests/test_medications_handler.py`:
- Test valid DFN returns medications
- Test invalid DFN returns empty string
- Test T-notation date conversion
- Test caret-delimited format
- Test active-only filtering (if we add EXPIRED/DISCONTINUED meds later)
- Test multi-site consistency (same RPC works at Sites 200, 500, 630)

#### Registration

**File:** `vista/app/main.py`

Add handler registration during site initialization (around line 150):

```python
from vista.app.handlers.medications import MedicationsCoverHandler

# Register handlers
site_manager.register_handler("200", MedicationsCoverHandler())
site_manager.register_handler("500", MedicationsCoverHandler())
site_manager.register_handler("630", MedicationsCoverHandler())
```

---

### 11.5 Backend Realtime Endpoint

**File:** `app/routes/medications.py`

**Route:** `GET /patient/{icn}/medications/realtime`

**Purpose:** Fetch real-time medications from VistA sites, merge with PostgreSQL data, return HTMX partial

#### Endpoint Specification

```python
@page_router.get("/patient/{icn}/medications/realtime", response_class=HTMLResponse)
async def get_medications_realtime(
    request: Request,
    icn: str,
    medication_type: Optional[str] = Query("all", regex="^(outpatient|inpatient|all)$"),
    status: Optional[str] = Query("all"),
    date_range: Optional[str] = Query("all"),
    sort_by: Optional[str] = Query("date_desc", regex="^(date_desc|date_asc|drug_name|type)$")
):
    """
    Realtime medications endpoint - Fetch T-0 data from VistA and merge with PostgreSQL.

    This endpoint:
    1. Queries VistA sites for active medications (T-0, today)
    2. Fetches PostgreSQL medications (T-1 and earlier)
    3. Merges and deduplicates by canonical key: {site}:{prescription_number}
    4. Applies filters and sorting
    5. Returns HTMX partial for swap into #vista-refresh-area

    Args:
        icn: Patient ICN
        medication_type: Filter by type ('outpatient', 'inpatient', 'all')
        status: Filter by status (for outpatient: 'ACTIVE', 'DISCONTINUED', etc.)
        date_range: Show medications from date range ('30', '90', '180', '365', 'all')
        sort_by: Combined sort field and order ('date_desc', 'date_asc', 'drug_name', 'type')

    Returns:
        HTMX partial with merged medications table and freshness indicator (OOB swap)
    """
```

#### Implementation Steps

**Step 1: Log and Validate** (Lines 10-20)

```python
logger.info(f"Medications realtime refresh requested for patient {icn}")

# Get patient demographics
patient = get_patient_demographics(icn)
if not patient:
    logger.warning(f"Patient {icn} not found")
    return templates.TemplateResponse(
        "patient_medications.html",
        get_base_context(request, patient=None, error="Patient not found")
    )
```

**Step 2: Query VistA Sites** (Lines 25-50)

```python
from app.services.vista_client import VistaClient

# Initialize VistA client
vista_client = VistaClient()

# Get target sites for medications domain (up to 3 sites)
target_sites = vista_client.get_target_sites(icn, domain='medications')
logger.info(f"Querying {len(target_sites)} VistA sites for medications: {target_sites}")

# Call ORWPS COVER RPC at all target sites (parallel)
vista_results = await vista_client.call_rpc_multi_site(
    sites=target_sites,
    rpc_name="ORWPS COVER",
    params=[icn]  # ICN auto-converted to DFN per site
)

# Extract successful responses
vista_responses = {
    site: result["response"]
    for site, result in vista_results.items()
    if result["success"]
}

logger.info(f"VistA responses received from {len(vista_responses)} of {len(target_sites)} sites")
```

**Step 3: Parse VistA Responses** (Lines 55-85)

```python
from app.services.realtime_overlay import parse_vista_medications

# Parse VistA medication responses into standardized format
vista_medications = []
for site_sta3n, response_text in vista_responses.items():
    parsed_meds = parse_vista_medications(response_text, site_sta3n, icn)
    vista_medications.extend(parsed_meds)
    logger.debug(f"Parsed {len(parsed_meds)} medications from site {site_sta3n}")

logger.info(f"Total VistA medications parsed: {len(vista_medications)}")
```

**Step 4: Fetch PostgreSQL Medications** (Lines 90-100)

```python
# Get PostgreSQL medications (T-1 and earlier)
# Apply NO date filter here - will filter after merge
pg_medications = get_patient_medications(
    icn,
    limit=500,
    medication_type=None,  # Get all types
    status=None,           # Get all statuses
    days=None              # No date filter
)

logger.info(f"PostgreSQL medications fetched: {len(pg_medications)}")
```

**Step 5: Merge and Deduplicate** (Lines 105-120)

```python
from app.services.realtime_overlay import merge_medications_data

# Merge VistA (T-0) with PostgreSQL (T-1+), deduplicate by canonical key
merged_medications, merge_stats = merge_medications_data(
    pg_medications=pg_medications,
    vista_results=vista_responses,
    icn=icn
)

logger.info(
    f"Merged medications: {len(merged_medications)} total "
    f"({merge_stats['vista_count']} from VistA, "
    f"{merge_stats['pg_count']} from PG, "
    f"{merge_stats['duplicates_removed']} duplicates removed)"
)
```

**Step 6: Cache VistA Responses** (Lines 125-135)

```python
from app.services.vista_cache import VistaSessionCache

# Store raw VistA responses in session cache (30-min TTL)
cache = VistaSessionCache()
cache.set_cached_data(
    request=request,
    patient_icn=icn,
    domain='medications',
    vista_responses=vista_responses,
    sites=list(target_sites),
    stats=merge_stats
)
```

**Step 7: Apply Filters and Sorting** (Lines 140-175)

```python
# Parse sort_by parameter
if sort_by == "date_desc":
    sort_field, sort_order = "date", "desc"
elif sort_by == "date_asc":
    sort_field, sort_order = "date", "asc"
elif sort_by == "drug_name":
    sort_field, sort_order = "drug_name", "asc"
elif sort_by == "type":
    sort_field, sort_order = "type", "asc"
else:
    sort_field, sort_order = "date", "desc"

# Convert date_range to days
days_map = {"30": 30, "90": 90, "180": 180, "365": 365, "all": 3650}
days_filter = days_map.get(date_range, 3650)

# Apply filters to merged data
filtered_medications = apply_medication_filters(
    medications=merged_medications,
    medication_type=medication_type if medication_type != 'all' else None,
    status=status if status != 'all' else None,
    days=days_filter
)

# Sort medications
filtered_medications = sort_medications(
    medications=filtered_medications,
    sort_field=sort_field,
    sort_order=sort_order
)

logger.info(f"Filtered/sorted medications: {len(filtered_medications)}")
```

**Step 8: Get Counts** (Lines 180-185)

```python
# Get medication counts (unfiltered, for summary bar)
counts = get_medication_counts(icn)
```

**Step 9: Return HTMX Partial** (Lines 190-215)

```python
# Build freshness message for OOB swap
from datetime import datetime
current_time = datetime.now().strftime("%H:%M")
freshness_message = f"Data current through: {datetime.now().strftime('%Y-%m-%d')} (refreshed at {current_time})"

# Return template response with vista_refreshed=True
return templates.TemplateResponse(
    "patient_medications.html",
    get_base_context(
        request,
        patient=patient,
        medications=filtered_medications,
        counts=counts,
        medication_type_filter=medication_type,
        status_filter=status,
        days_filter=days_filter,
        date_range_filter=date_range,
        sort_by=sort_field,
        sort_order=sort_order,
        total_count=len(filtered_medications),
        active_page="medications",
        vista_refreshed=True,
        vista_sites=list(target_sites),
        vista_stats=merge_stats,
        freshness_message=freshness_message
    )
)
```

#### Error Handling

```python
except Exception as e:
    logger.error(f"Error during medications realtime refresh for {icn}: {e}")
    return templates.TemplateResponse(
        "patient_medications.html",
        get_base_context(
            request,
            patient=patient,
            error=f"Error fetching real-time medications: {str(e)}",
            active_page="medications"
        )
    )
```

---

### 11.6 Merge and Deduplication Logic

**File:** `app/services/realtime_overlay.py`

**New Functions:** `parse_vista_medications()`, `merge_medications_data()`

#### Function 1: parse_vista_medications()

**Purpose:** Parse ORWPS COVER RPC response into standardized medication dictionaries

```python
def parse_vista_medications(
    vista_response: str,
    site_sta3n: str,
    icn: str
) -> List[Dict[str, Any]]:
    """
    Parse VistA ORWPS COVER response into standardized medication records.

    Args:
        vista_response: Raw RPC response (multi-line, caret-delimited)
        site_sta3n: Site station number (200, 500, 630)
        icn: Patient ICN (for reference)

    Returns:
        List of medication dictionaries with standardized fields

    Example Input:
        "2860066^LISINOPRIL 10MG TAB^ACTIVE^60/90^3^3260106.1035^3270106\n
         2860067^METFORMIN HCL 500MG TAB^ACTIVE^120/180^5^3260106.1030^3270106"

    Example Output:
        [
            {
                "medication_id": "rxout_vista_200_2860066",
                "type": "outpatient",
                "source": "vista",
                "source_site": "200",
                "patient_icn": "ICN100001",
                "prescription_number": "2860066",
                "drug_name_local": "LISINOPRIL 10MG TAB",
                "status": "ACTIVE",
                "quantity": 60.0,
                "days_supply": 90,
                "refills_remaining": 3,
                "issue_date": "2026-01-06 10:35:00",
                "expiration_date": "2027-01-06",
                "canonical_key": "200:2860066",
                "_vista_raw": "2860066^LISINOPRIL 10MG TAB^ACTIVE^60/90^3^3260106.1035^3270106"
            },
            ...
        ]
    """
```

**Implementation Details:**

1. **Split Response by Lines**
   ```python
   if not vista_response or not vista_response.strip():
       return []

   lines = vista_response.strip().split('\n')
   medications = []
   ```

2. **Parse Each Line**
   ```python
   for line_num, line in enumerate(lines, 1):
       if not line.strip():
           continue

       try:
           fields = line.split('^')
           if len(fields) != 7:
               logger.warning(f"Unexpected field count in VistA medication: {len(fields)} (expected 7)")
               continue
   ```

3. **Extract Fields**
   ```python
   rx_number = fields[0].strip()
   drug_name = fields[1].strip()
   status = fields[2].strip()
   qty_days = fields[3].strip()  # Format: "60/90"
   refills = fields[4].strip()
   issue_date_fm = fields[5].strip()
   exp_date_fm = fields[6].strip()
   ```

4. **Parse Quantity/Days Supply**
   ```python
   # Split "60/90" into quantity and days_supply
   if '/' in qty_days:
       qty_str, days_str = qty_days.split('/')
       quantity = float(qty_str.strip())
       days_supply = int(days_str.strip())
   else:
       quantity = None
       days_supply = None
   ```

5. **Convert FileMan Dates to ISO 8601**
   ```python
   from app.services.realtime_overlay import parse_fileman_datetime

   # Issue date (includes time)
   issue_date = None
   if issue_date_fm:
       issue_dt = parse_fileman_datetime(issue_date_fm)
       if issue_dt:
           issue_date = issue_dt.isoformat()

   # Expiration date (date only, set time to midnight)
   expiration_date = None
   if exp_date_fm:
       exp_dt = parse_fileman_datetime(exp_date_fm + ".0000")  # Add midnight time
       if exp_dt:
           expiration_date = exp_dt.date().isoformat()
   ```

6. **Build Standardized Medication Dictionary**
   ```python
   medication = {
       "medication_id": f"rxout_vista_{site_sta3n}_{rx_number}",
       "type": "outpatient",
       "source": "vista",
       "source_site": site_sta3n,
       "is_realtime": True,
       "patient_icn": icn,
       "prescription_number": rx_number,
       "drug_name_local": drug_name,
       "drug_name_national": None,  # Not in ORWPS COVER response
       "status": status,
       "quantity": quantity,
       "days_supply": days_supply,
       "refills_remaining": int(refills) if refills.isdigit() else None,
       "issue_date": issue_date,
       "expiration_date": expiration_date,
       "date": issue_date,  # Use issue_date as primary date for sorting

       # Canonical key for deduplication
       "canonical_key": f"{site_sta3n}:{rx_number}",

       # Store raw VistA line for debugging
       "_vista_raw": line.strip()
   }

   medications.append(medication)
   ```

7. **Error Handling**
   ```python
   except Exception as e:
       logger.error(f"Error parsing VistA medication line {line_num}: {e}")
       logger.debug(f"Problematic line: {line}")
       continue  # Skip this medication, continue with others

   return medications
   ```

#### Function 2: merge_medications_data()

**Purpose:** Merge PostgreSQL medications with VistA responses, deduplicate by canonical key

```python
def merge_medications_data(
    pg_medications: List[Dict[str, Any]],
    vista_results: Dict[str, str],
    icn: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Merge PostgreSQL medications (T-1+) with VistA responses (T-0), deduplicate.

    Deduplication Strategy:
    - Canonical key: {site}:{prescription_number}
    - Vista data preferred for T-1+ overlap (most current)
    - PostgreSQL provides historical baseline
    - Remove exact duplicates

    Args:
        pg_medications: Medications from PostgreSQL (list of dicts)
        vista_results: Raw VistA RPC responses per site {site: response_text}
        icn: Patient ICN

    Returns:
        Tuple of (merged_medications, merge_stats)
        - merged_medications: Deduplicated list sorted by date desc
        - merge_stats: Statistics about merge operation
    """
```

**Implementation Details:**

1. **Parse All VistA Responses**
   ```python
   vista_medications = []
   for site_sta3n, response_text in vista_results.items():
       parsed = parse_vista_medications(response_text, site_sta3n, icn)
       vista_medications.extend(parsed)

   logger.info(f"Parsed {len(vista_medications)} medications from VistA")
   ```

2. **Add Canonical Keys to PostgreSQL Medications**
   ```python
   # Add canonical_key to PG medications if not present
   for med in pg_medications:
       if 'canonical_key' not in med:
           # Extract site from medication_id or use default
           # medication_id format: "rxout_123" (no site in PG)
           # For PG meds, canonical key is just prescription_number
           # (site unknown, so deduplication works across all sites)
           rx_num = med.get('prescription_number') or med.get('source_id', '')
           med['canonical_key'] = f"pg:{rx_num}"  # PG prefix to avoid false matches
           med['source'] = 'postgresql'
   ```

3. **Build Canonical Key Index (Vista Medications)**
   ```python
   vista_by_key = {}
   for med in vista_medications:
       key = med['canonical_key']
       if key in vista_by_key:
           # Duplicate within Vista results (multi-site)
           logger.warning(f"Duplicate Vista medication: {key}")
           # Keep most recent by issue_date
           existing = vista_by_key[key]
           if med.get('issue_date', '') > existing.get('issue_date', ''):
               vista_by_key[key] = med
       else:
           vista_by_key[key] = med
   ```

4. **Merge: Vista Preferred**
   ```python
   merged = []
   pg_keys_seen = set()

   # Add all Vista medications first (T-0, most current)
   merged.extend(vista_by_key.values())
   vista_keys = set(vista_by_key.keys())

   # Add PG medications that don't overlap with Vista
   for med in pg_medications:
       pg_key = med['canonical_key']

       # Check if this PG med overlaps with any Vista med
       # Since PG meds don't have site, check prescription_number only
       rx_num = med.get('prescription_number')
       overlaps = any(key.endswith(f":{rx_num}") for key in vista_keys)

       if not overlaps:
           merged.append(med)
           pg_keys_seen.add(pg_key)
   ```

5. **Sort by Date Descending (Most Recent First)**
   ```python
   merged.sort(key=lambda m: m.get('date') or '', reverse=True)
   ```

6. **Calculate Merge Statistics**
   ```python
   merge_stats = {
       'vista_count': len(vista_medications),
       'pg_count': len(pg_medications),
       'merged_count': len(merged),
       'duplicates_removed': len(pg_medications) - len(pg_keys_seen),
       'vista_keys': list(vista_by_key.keys()),
       'pg_keys_included': list(pg_keys_seen)
   }

   return merged, merge_stats
   ```

**Canonical Key Examples:**

| Scenario | PG Key | Vista Key | Result |
|----------|--------|-----------|--------|
| Same RX at same site | `pg:2860066` | `200:2860066` | Vista wins (more current) |
| Different RX numbers | `pg:2860066` | `200:2860070` | Both included |
| Same RX at different sites | `pg:2860066` | `200:2860066`, `500:2860066` | All Vista versions + no PG (overlaps) |
| PG only (no Vista match) | `pg:2860066` | (none) | PG included |
| Vista only (new today) | (none) | `200:2860099` | Vista included |

---

### 11.7 Template Integration

**File:** `app/templates/patient_medications.html`

**Changes Required:**

#### 1. Add Vista Refresh Controls Section (After Page Header, Before Summary Bar)

**Insert at line ~48 (after page header, before summary stats):**

```html
        <!-- VistA Refresh Controls -->
        <div class="vista-refresh-controls">
            <!-- Freshness Message (updated via OOB swap) -->
            <div class="freshness-message" id="freshness-message">
                {% if vista_refreshed %}
                    <i class="fa-solid fa-circle-check"></i>
                    <span>{{ freshness_message }}</span>
                    <span class="vista-cached-badge" title="Vista data cached for {{ vista_sites|length }} sites">
                        <i class="fa-solid fa-database"></i>
                        Vista Cached ({{ vista_sites|length }} sites)
                    </span>
                {% else %}
                    <i class="fa-solid fa-clock"></i>
                    <span>Data current through yesterday (PostgreSQL)</span>
                {% endif %}
            </div>

            <!-- Refresh Button -->
            <div class="vista-refresh-button-container">
                <button
                    type="button"
                    hx-get="/patient/{{ patient.icn }}/medications/realtime?medication_type={{ medication_type_filter }}&status={{ status_filter or 'all' }}&date_range={{ date_range_filter }}&sort_by={{ sort_by }}_{{ sort_order }}"
                    hx-target="#vista-refresh-area"
                    hx-swap="outerHTML"
                    hx-indicator="#vista-loading"
                    aria-label="Refresh data from VistA sites"
                    class="btn btn--secondary vista-refresh-btn">
                    <i class="fa-solid fa-rotate"></i>
                    Refresh from VistA
                </button>

                <!-- Loading Indicator -->
                <div id="vista-loading" class="htmx-indicator">
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    <span>Querying VistA sites...</span>
                </div>
            </div>
        </div>
```

**CSS Classes (already exist in styles.css from Vitals domain):**
- `.vista-refresh-controls`
- `.freshness-message`
- `.vista-cached-badge`
- `.vista-refresh-button-container`
- `.vista-refresh-btn`
- `.htmx-indicator`

#### 2. Wrap Main Content in #vista-refresh-area

**Wrap the summary bar, filters, and table (lines ~52 onwards) in a refresh target div:**

```html
        <!-- VistA Refresh Area (HTMX Target) -->
        <div id="vista-refresh-area">

            <!-- Summary Stats Bar -->
            <div class="medications-summary-bar">
                <!-- Existing summary stats code -->
            </div>

            <!-- Filters and Controls -->
            <div class="medications-controls">
                <!-- Existing filter form -->
            </div>

            <!-- Medications Table Container -->
            <div id="medications-table-container">
                <!-- Existing table or empty state -->
            </div>

        </div> <!-- End #vista-refresh-area -->
```

**Note:** The `#vista-refresh-area` div must wrap:
- Summary stats bar
- Filter controls
- Medications table container

This ensures the entire data area is replaced on refresh, but the Vista refresh button remains fixed at the top.

#### 3. Add Vista Source Badges to Medication Rows

**In the medication table loop (around line 220), add source indicator:**

```html
                            <!-- Medication Name -->
                            <td class="medication-cell medication-cell--medication">
                                <div class="medication-name">
                                    {{ med.drug_name_local or med.drug_name or '—' }}

                                    <!-- Vista Source Badge (if from VistA) -->
                                    {% if med.source == 'vista' %}
                                        <span class="badge badge--success badge--sm" title="Real-time data from VistA Site {{ med.source_site }}">
                                            <i class="fa-solid fa-bolt"></i>
                                            Site {{ med.source_site }}
                                        </span>
                                    {% endif %}

                                    <!-- Controlled Substance Badge -->
                                    {% if med.is_controlled %}
                                        <span class="badge badge--warning badge--sm" title="Controlled Substance">
                                            <i class="fa-solid fa-triangle-exclamation"></i>
                                            {{ med.dea_schedule }}
                                        </span>
                                    {% endif %}
                                </div>
                                <!-- Existing medication details code -->
                            </td>
```

#### 4. Add Out-of-Band (OOB) Freshness Message Swap

**At the END of the template (after table, before closing divs), add OOB swap:**

```html
        {% if vista_refreshed %}
            <!-- Out-of-Band Swap: Update Freshness Message -->
            <div class="freshness-message" id="freshness-message" hx-swap-oob="true">
                <i class="fa-solid fa-circle-check"></i>
                <span>{{ freshness_message }}</span>
                <span class="vista-cached-badge" title="Vista data cached for {{ vista_sites|length }} sites">
                    <i class="fa-solid fa-database"></i>
                    Vista Cached ({{ vista_sites|length }} sites)
                </span>
            </div>
        {% endif %}
```

**What is OOB Swap?**
- HTMX `hx-swap-oob="true"` allows updating elements OUTSIDE the main target
- The `#freshness-message` div at the top of the page gets updated even though the main swap target is `#vista-refresh-area`
- Enables simultaneous update of:
  1. Main content area (medications table)
  2. Freshness indicator (at top of page)

---

### 11.8 Testing Strategy

#### Unit Tests

**1. Vista RPC Handler Tests** (`vista/app/tests/test_medications_handler.py`)

```python
def test_medications_cover_valid_dfn():
    """Test ORWPS COVER returns medications for valid DFN"""

def test_medications_cover_invalid_dfn():
    """Test ORWPS COVER returns empty string for invalid DFN"""

def test_medications_cover_date_conversion():
    """Test T-notation dates convert to FileMan format correctly"""

def test_medications_cover_format():
    """Test response is caret-delimited with 7 fields per line"""

def test_medications_cover_multi_site():
    """Test same RPC works consistently across Sites 200, 500, 630"""
```

**2. Parser Tests** (`app/tests/test_realtime_overlay.py`)

```python
def test_parse_vista_medications_valid_response():
    """Test parse_vista_medications handles valid multi-line response"""

def test_parse_vista_medications_empty_response():
    """Test parse_vista_medications handles empty string"""

def test_parse_vista_medications_invalid_field_count():
    """Test parse_vista_medications skips lines with wrong field count"""

def test_parse_fileman_datetime():
    """Test FileMan date conversion (already exists, verify works for meds)"""
```

**3. Merge/Dedupe Tests** (`app/tests/test_medications_merge.py`)

```python
def test_merge_medications_no_overlap():
    """Test merge when PG and Vista have different prescriptions"""

def test_merge_medications_same_rx():
    """Test merge prefers Vista when same prescription_number"""

def test_merge_medications_multi_site_dedup():
    """Test deduplication when same RX appears at multiple sites"""

def test_merge_medications_canonical_key():
    """Test canonical key format: {site}:{prescription_number}"""

def test_merge_statistics():
    """Test merge_stats returns correct counts"""
```

#### Integration Tests

**4. End-to-End Vista Refresh** (Manual Browser Testing)

**Test Case 1: ICN100001 (Dooree, Adam) - Multi-Site with Overlaps**

1. Navigate to `/patient/ICN100001/medications`
2. Initial load shows PostgreSQL medications only (4 outpatient)
3. Click "Refresh from VistA" button
4. Verify:
   - Loading spinner appears
   - Query completes in <5 seconds
   - Medications refresh with Vista data (badges visible)
   - Freshness message updates: "Data current through: [today] (refreshed at [HH:MM])"
   - Vista Cached badge shows "Vista Cached (3 sites)"
   - Green badges on Vista medications: "⚡ Site 200", "⚡ Site 500", "⚡ Site 630"
   - No duplicate medications (same RX_NUMBER from different sites deduplicated)
   - Total count increased (T-0 meds added)
5. Check browser console for merge stats log
6. Verify session cache: navigate away and back, Vista data persists (30 min)

**Test Case 2: Filter Preservation After Refresh**

1. Navigate to `/patient/ICN100001/medications`
2. Change filters: Type=Outpatient, Status=Active, Time Period=Last 30 Days
3. Click "Refresh from VistA"
4. Verify:
   - Filters remain selected after refresh
   - URL query params preserved: `?medication_type=outpatient&status=ACTIVE&date_range=30`
   - Filtered results shown (not all medications)

**Test Case 3: Partial Failure Handling**

1. Stop Vista service: `kill $(lsof -ti:8003)`
2. Navigate to `/patient/ICN100001/medications`
3. Click "Refresh from VistA"
4. Verify:
   - Page doesn't crash (graceful fallback)
   - PostgreSQL data still displays
   - Error message or partial success indicator shown
5. Restart Vista service and retry

**Test Case 4: Deduplication Verification**

1. Navigate to `/patient/ICN100013/medications` (highest DFN count: 6 DFNs)
2. Note PostgreSQL count: 9 outpatient medications
3. Click "Refresh from VistA"
4. Verify:
   - Merged count > PG count (new T-0 meds added)
   - No duplicates visible (same drug/RX from multiple sites appears once)
   - Merge stats in console show duplicates_removed > 0
5. Check that medications with Vista badges have `source="vista"` in DOM

**Test Case 5: Controlled Substances**

1. Navigate to patient with controlled substances
2. Refresh from VistA
3. Verify:
   - Controlled substance badges visible (⚠ C-II, C-IV, etc.)
   - Summary bar "Controlled Substances" count includes Vista meds
   - Vista-sourced controlled substances flagged correctly

#### Performance Tests

**6. Response Time Validation**

- Measure realtime endpoint response time: Target <5 seconds (3 sites × 1-3 sec latency)
- Concurrent user testing: 5 users refresh simultaneously (verify no bottleneck)
- Large dataset: Patient with 50+ PostgreSQL meds + 30 Vista meds (verify merge scales)

---

### 11.9 Implementation Tasks

**Phase 5: Medications Real-Time VistA Integration (2-3 Days)**

#### Day 1: Vista Infrastructure (4-6 hours)

**Task 1.1: Create Vista RPC Handler** (2 hours)
- [ ] Create `vista/app/handlers/medications.py`
- [ ] Implement `MedicationsCoverHandler` class
- [ ] Add parameter validation (DFN required)
- [ ] Implement response formatting (caret-delimited, 7 fields)
- [ ] Add T-notation date conversion (reuse existing parser)
- [ ] Register handler in `vista/app/main.py` for all 3 sites
- [ ] Write unit tests (5 test cases)
- [ ] Verify tests pass: `pytest vista/app/tests/test_medications_handler.py -v`

**Task 1.2: Create Mock Data Files** (2-3 hours)
- [ ] Create `vista/app/data/sites/200/medications.json` (30-40 meds, 5 DFNs)
- [ ] Create `vista/app/data/sites/500/medications.json` (25-35 meds, 5 DFNs)
- [ ] Create `vista/app/data/sites/630/medications.json` (30-45 meds, 6 DFNs)
- [ ] Include all 4 test patients (ICN100001, ICN100010, ICN100013, ICN100002)
- [ ] Add intentional overlaps for deduplication testing
- [ ] Include 3-5 controlled substances per site
- [ ] Use T-notation for all dates (T-0 to T-30, expiration T+30 to T+365)
- [ ] Verify JSON syntax valid: `jq . vista/app/data/sites/*/medications.json`

**Task 1.3: Test Vista Service** (1 hour)
- [ ] Start Vista service: `uvicorn vista.app.main:app --reload --port 8003`
- [ ] Test ORWPS COVER RPC via curl:
  ```bash
  curl -X POST "http://localhost:8003/rpc/execute?site=200&icn=ICN100001" \
       -H "Content-Type: application/json" \
       -d '{"rpc_name": "ORWPS COVER", "params": ["ICN100001"]}'
  ```
- [ ] Verify response: Multi-line, caret-delimited, 7 fields
- [ ] Test all 3 sites (200, 500, 630)
- [ ] Test all 4 patients

#### Day 2: Backend Integration (4-6 hours)

**Task 2.1: Implement Parser** (1.5 hours)
- [ ] Add `parse_vista_medications()` to `app/services/realtime_overlay.py`
- [ ] Parse caret-delimited format (7 fields)
- [ ] Convert FileMan dates to ISO 8601
- [ ] Parse quantity/days_supply (split "60/90")
- [ ] Build standardized medication dictionaries
- [ ] Add canonical key: `{site}:{prescription_number}`
- [ ] Write unit tests for parser
- [ ] Verify tests pass: `pytest app/tests/test_realtime_overlay.py::test_parse_vista_medications -v`

**Task 2.2: Implement Merge Logic** (2 hours)
- [ ] Add `merge_medications_data()` to `app/services/realtime_overlay.py`
- [ ] Parse all Vista responses (call parse_vista_medications per site)
- [ ] Build canonical key index for Vista medications
- [ ] Deduplicate within Vista results (multi-site)
- [ ] Merge with PostgreSQL medications (Vista preferred)
- [ ] Calculate merge statistics
- [ ] Write unit tests for merge logic (4 test cases)
- [ ] Verify tests pass: `pytest app/tests/test_medications_merge.py -v`

**Task 2.3: Implement Realtime Endpoint** (2-3 hours)
- [ ] Add `get_medications_realtime()` to `app/routes/medications.py`
- [ ] Import VistaClient, call `call_rpc_multi_site()` (3 sites)
- [ ] Parse Vista responses (call `parse_vista_medications()`)
- [ ] Fetch PostgreSQL medications
- [ ] Merge data (call `merge_medications_data()`)
- [ ] Cache Vista responses (30-min TTL)
- [ ] Apply filters and sorting to merged data
- [ ] Return HTMX partial with `vista_refreshed=True`
- [ ] Add error handling (try/except)
- [ ] Test endpoint via curl:
  ```bash
  curl "http://localhost:8000/patient/ICN100001/medications/realtime"
  ```

#### Day 3: Frontend Integration & Testing (4-6 hours)

**Task 3.1: Update Template** (2 hours)
- [ ] Open `app/templates/patient_medications.html`
- [ ] Insert vista-refresh-controls section (after page header, line ~48)
- [ ] Add freshness message with OOB swap placeholder
- [ ] Add "Refresh from VistA" button with HTMX attributes
- [ ] Add loading spinner (#vista-loading)
- [ ] Wrap summary bar + filters + table in `#vista-refresh-area` div
- [ ] Add Vista source badges to medication rows (`{% if med.source == 'vista' %}`)
- [ ] Add OOB swap for freshness message at end of template
- [ ] Verify HTML syntax valid

**Task 3.2: Browser Testing** (2-3 hours)
- [ ] Start all services (PostgreSQL, Vista, med-z1 app)
- [ ] Test ICN100001: Multi-site refresh, verify overlaps deduplicated
- [ ] Test ICN100010: Verify orphaned DFNs don't create duplicates
- [ ] Test ICN100013: Stress test with 6 DFNs (high deduplication load)
- [ ] Test ICN100002: Baseline patient (minimal overlaps)
- [ ] Test filter preservation after refresh (type, status, date range, sort)
- [ ] Test Vista badges visible on refreshed medications
- [ ] Test freshness message updates correctly
- [ ] Test Vista Cached badge shows site count
- [ ] Test controlled substance badges (⚠ C-II, C-IV)
- [ ] Test performance: refresh completes in <5 seconds
- [ ] Test partial failure: stop Vista service, verify graceful fallback
- [ ] Test cache persistence: navigate away and back, Vista data persists

**Task 3.3: Documentation Updates** (1 hour)
- [ ] Update `docs/spec/vista-rpc-broker-design.md`:
  - Change header status to "Phase 5 COMPLETE"
  - Add Changelog v1.9 (2026-01-13)
  - Expand Section 6.4 (Medications RPC Specification)
  - Mark Phase 5 as complete in Phase tracking
- [ ] Update `vista/README.md`:
  - Change status to "Phase 5 Complete - Demographics, Vitals, Encounters, Allergies, Medications"
  - Add ORWPS COVER to RPC list
  - Update test patient notes (medications added)
- [ ] Update `CLAUDE.md`:
  - Change status to "OPERATIONAL - Phases 1-5 Complete"
  - Add ORWPS COVER to implemented RPCs list
  - Update Phase tracking
- [ ] Update this document (`medications-design.md`):
  - Change status to "Implementation Complete"
  - Update version to 1.3
  - Add implementation completion date

---

### 11.10 Success Criteria

**Functional Requirements:**
- ✅ "Refresh from VistA" button appears in medications page header
- ✅ Button queries up to 3 VistA sites per patient
- ✅ ORWPS COVER RPC returns active medications in correct format
- ✅ Vista responses parse correctly (7 fields, caret-delimited)
- ✅ FileMan dates convert to ISO 8601
- ✅ Merge logic combines PostgreSQL + Vista without duplicates
- ✅ Canonical key deduplication works: `{site}:{prescription_number}`
- ✅ Vista-sourced medications show green badges ("⚡ Site 200")
- ✅ Freshness message updates via OOB swap
- ✅ Filters and sorting preserved after refresh
- ✅ Session cache stores Vista responses (30-min TTL)

**Performance Requirements:**
- ✅ Refresh completes in <5 seconds (3 sites × 1-3 sec latency)
- ✅ Page remains responsive during refresh (HTMX loading spinner)
- ✅ No UI freeze or timeout errors

**Data Quality Requirements:**
- ✅ No duplicate medications in merged view (same RX from multiple sites)
- ✅ Vista data preferred over PostgreSQL for T-1+ overlap
- ✅ Controlled substances flagged correctly (Vista and PG)
- ✅ Merge statistics logged (vista_count, pg_count, duplicates_removed)

**Testing Requirements:**
- ✅ Unit tests pass for RPC handler (5 tests)
- ✅ Unit tests pass for parser (4 tests)
- ✅ Unit tests pass for merge logic (4 tests)
- ✅ End-to-end browser tests pass (5 test cases)
- ✅ Performance test validates <5 second response time

**Documentation Requirements:**
- ✅ vista-rpc-broker-design.md updated (Phase 5 complete)
- ✅ vista/README.md updated (RPCs list, capabilities)
- ✅ CLAUDE.md updated (implementation status)
- ✅ medications-design.md updated (this section complete)

---

### 11.11 Future Enhancements (Phase 6+)

**Potential Future Features (NOT in Phase 5 scope):**

1. **Inpatient Medications (BCMA)**
   - Add BCMA RPC handler for inpatient medication administrations
   - Merge both outpatient (ORWPS) and inpatient (BCMA) in realtime endpoint
   - Support dual-source refresh (RxOut + BCMA)

2. **Additional Outpatient RPCs**
   - ORWPS DETAIL: Single prescription detail view (drill-down)
   - ORWPS ACTIVE: Alternative to ORWPS COVER
   - PSO SUPPLY: Refill history and supply details

3. **Historical Date-Range Queries**
   - Add `DAYS_BACK` parameter to ORWPS COVER RPC
   - Support last 90 days, last year queries from VistA
   - Merge T-90 to T-1 from VistA with PostgreSQL (broader overlap)

4. **Prescription Detail Modal**
   - Click medication row to open detail modal
   - Call ORWPS DETAIL RPC for full prescription information
   - Show SIG (full dosing instructions), refill history, provider notes

5. **Partial Failure UI Indicators**
   - Show "2 of 3 sites responded" badge
   - Color-code badges by site response status (green=success, red=failed)
   - Allow user to retry failed sites

6. **Manual Site Selection**
   - Add site picker UI (checkboxes for Sites 200, 500, 630)
   - Override default site selection (3 sites)
   - Allow user to query specific sites only

7. **AI Clinical Insights Integration**
   - Extend AI insights to use cached Vista medication data
   - Drug-drug interaction (DDI) checking with real-time meds
   - Medication reconciliation assistant (compare PG vs Vista)

---

**End of Section 11: Real-Time VistA Integration**

---

## 12. Testing Strategy

### 12.1 ETL Testing

**Bronze Layer:**
- [ ] Verify all 5 tables extract successfully
- [ ] Verify row counts match CDW tables
- [ ] Verify Parquet schema matches CDW schema
- [ ] Test with empty tables (graceful handling)

**Silver Layer:**
- [ ] Verify drug name lookups resolve correctly (LocalDrug → NationalDrug)
- [ ] Verify Sta3n → facility name lookups
- [ ] Verify provider name lookups
- [ ] Verify RxOutpat + RxOutpatFill join produces correct latest fill
- [ ] Test with missing drug records (should not break pipeline)

**Gold Layer:**
- [ ] Verify patient_icn population
- [ ] Verify is_controlled_substance flag accurate
- [ ] Verify is_active flag accurate (not discontinued and not expired)
- [ ] Verify administration_variance flag accurate
- [ ] Verify sorting (date descending)

**PostgreSQL Load:**
- [ ] Verify row counts match Gold Parquet files
- [ ] Verify indexes created
- [ ] Verify data types correct
- [ ] Test query performance (< 1000ms for typical patient)

### 12.2 API Testing

**GET /api/patient/{icn}/medications:**
- [ ] Test with valid ICN → returns unified medications list
- [ ] Test with invalid ICN → returns empty list or 404
- [ ] Test with date_from/date_to filters → returns correct date range
- [ ] Test with type_filter=outpatient → returns only RxOut
- [ ] Test with type_filter=inpatient → returns only BCMA
- [ ] Test with status_filter=active → returns only active RxOut meds
- [ ] Test response time < 1000ms

**GET /api/patient/{icn}/medications/recent:**
- [ ] Test returns max 8 medications
- [ ] Test returns last 90 days
- [ ] Test mix of RxOut and BCMA
- [ ] Test patient with 0 medications → returns empty array

**GET /api/patient/{icn}/medications/{medication_id}/details:**
- [ ] Test with rxout_XXXX ID → returns RxOut details
- [ ] Test with bcma_XXXX ID → returns BCMA details
- [ ] Test with invalid ID → returns 404
- [ ] Test response includes all expected fields

**GET /api/dashboard/widget/medications/{icn}:**
- [ ] Test returns valid HTML fragment
- [ ] Test widget renders correctly in dashboard
- [ ] Test with 0 medications → shows empty state
- [ ] Test with 20+ medications → shows 8 + "more" indicator

**GET /patient/{icn}/medications:**
- [ ] Test page renders correctly
- [ ] Test table populated with medications
- [ ] Test filters work (date, type, status)
- [ ] Test sorting works
- [ ] Test expandable rows work
- [ ] Test with 0 medications → shows empty state

### 12.3 UI Testing

**Dashboard Widget:**
- [ ] Verify widget loads on patient selection
- [ ] Verify 6-8 medications displayed
- [ ] Verify type badges render correctly (color-coded)
- [ ] Verify controlled substance indicators show
- [ ] Verify "View All" link navigates to full page
- [ ] Verify empty state displays when no medications
- [ ] Test on mobile/tablet (responsive)

**Full Medications Page:**
- [ ] Verify table renders with all columns
- [ ] Verify RxOut rows display correctly
- [ ] Verify BCMA rows display correctly
- [ ] Verify type badges color-coded correctly
- [ ] Verify controlled substance rows highlighted
- [ ] Verify date range filter works
- [ ] Verify type filter works
- [ ] Verify status filter works
- [ ] Verify expandable row details work:
  - Click to expand
  - RxOut details show prescription info
  - BCMA details show administration info
- [ ] Test sorting by date, medication name
- [ ] Test empty state
- [ ] Test on mobile/tablet (responsive)

### 12.4 Integration Testing

**End-to-End:**
- [ ] Run full ETL pipeline → verify data in PostgreSQL
- [ ] Select patient in dashboard → verify medications widget loads
- [ ] Click "View All" → verify full page loads
- [ ] Apply filters → verify table updates
- [ ] Expand row → verify details load
- [ ] Test with 5 different patients (varied medication profiles)

**Performance:**
- [ ] Measure ETL pipeline execution time (< 5 minutes for full pipeline)
- [ ] Measure API response times:
  - /medications endpoint: < 1000ms
  - /medications/recent endpoint: < 500ms
  - /medications/{id}/details endpoint: < 300ms
- [ ] Measure page load time (< 2 seconds)

---

## 13. Security and Privacy

### 13.1 Data Sensitivity

Medications data is **highly sensitive PHI/PII**:
- Drug names can reveal medical conditions (e.g., HIV meds, psych meds)
- Controlled substances indicate pain management or substance use
- Inpatient medications reveal hospitalizations
- Medication adherence can impact care decisions

### 13.2 Access Control

**Initial Implementation (Development):**
- All mock data is **synthetic and non-PHI**
- No real patient data used
- No authentication required for development environment

**Production Requirements (Future):**
- Require VA SSO authentication (SSOi, IAM)
- Implement role-based access control (RBAC):
  - Clinicians: Read access to medications for patients under their care
  - Pharmacists: Read access + ability to view fill history
  - Patients: Read access to own medications via My HealtheVet
  - Auditors: Read-only access for compliance review
- Audit all medication views (log patient_icn, user_id, timestamp)
- Implement "break-the-glass" for emergency access

### 13.3 Data Handling

**In Transit:**
- Use HTTPS for all API calls (TLS 1.2+)
- Encrypt WebSocket connections (if used for real-time updates)

**At Rest:**
- Encrypt PostgreSQL database (column-level encryption for sensitive fields)
- Encrypt Parquet files in MinIO (server-side encryption)
- Encrypt backup files

**Logging:**
- Redact drug names in application logs (log drug_id, not drug_name)
- Redact patient identifiers in debug logs
- Implement secure audit logging with tamper-proof storage

### 13.4 Controlled Substances

Controlled substance data (DEA Schedule II-V) requires special handling:
- Flag controlled substances in UI (⚠️ indicator)
- Audit all views of controlled substance prescriptions
- Implement additional access controls for Schedule II (opioids)
- Alert on unusual access patterns (e.g., staff viewing own controlled Rx)

---

## 14. Appendices

**Note:** See Appendix A for the Original Implementation Roadmap (Days 1-12 Plan).

## Appendix A: Original Implementation Roadmap (Days 1-12 Plan)

**Note:** This section contains the original implementation plan. Days 1-8 were completed (2025-12-13). The remaining days (9-12) were deferred as optional enhancements. The current priority is the Filter UI Enhancement specified in Section 9.

### A.1 Day-by-Day Plan (10-12 days estimated)

#### Day 1: Database Setup and Dimension Tables
**Goal:** Create new dimension tables and populate with sample data

**Tasks:**
- [ ] Create `Dim.LocalDrug` table DDL script
- [ ] Create `Dim.NationalDrug` table DDL script
- [ ] Generate 50+ sample drugs covering common medication classes:
  - Antihypertensives (Lisinopril, Amlodipine, Metoprolol, Losartan)
  - Antidiabetics (Metformin, Insulin Glargine)
  - Statins (Atorvastatin, Simvastatin)
  - Analgesics/Opioids (Tramadol, Hydrocodone, Ibuprofen)
  - Mental health (Sertraline, Alprazolam, Gabapentin)
  - Antibiotics (Amoxicillin, Ceftriaxone)
  - Respiratory (Albuterol, Omeprazole)
  - Anticoagulants (Warfarin, Aspirin)
- [ ] Populate with INSERT scripts
- [ ] Verify LocalDrug → NationalDrug linkage
- [ ] Update existing RxOut.RxOutpat and BCMA.BCMAMedicationLog to reference new LocalDrugSID values
- [ ] Run SQL Server scripts to create and populate tables
- [ ] Verify 50+ drugs in Dim.LocalDrug, 30+ in Dim.NationalDrug

**Deliverable:** Mock CDW dimension tables created and populated

---

#### Day 2: Bronze ETL ✅
**Goal:** Extract raw medication data from CDW to Parquet
**Status:** Complete - 2025-12-13

**Tasks:**
- [x] Create `etl/bronze_medications.py`
- [x] Implement extraction for:
  - `Dim.LocalDrug` → `bronze_dim_local_drug.parquet` (58 rows)
  - `Dim.NationalDrug` → `bronze_dim_national_drug.parquet` (40 rows)
  - `RxOut.RxOutpat` → `bronze_rxout_rxoutpat.parquet` (111 rows)
  - `RxOut.RxOutpatFill` → `bronze_rxout_rxoutpatfill.parquet` (31 rows)
  - `BCMA.BCMAMedicationLog` → `bronze_bcma_medicationlog.parquet` (52 rows)
- [x] Add logging and error handling
- [x] Test extraction for all patients
- [x] Verify row counts match CDW
- [x] Verify Parquet file structure

**Deliverable:** Bronze Parquet files created ✅

---

#### Day 3: Silver ETL ✅
**Goal:** Harmonize and enrich medication data with lookups
**Status:** Complete - 2025-12-13

**Tasks:**
- [x] Create `etl/silver_medications.py`
- [x] Implement RxOut Silver transformation:
  - Join RxOutpat + RxOutpatFill (latest fill per prescription)
  - Resolve LocalDrugSID → drug names (local + national)
  - Resolve Sta3n → facility names
  - Resolve ProviderSID → provider names
  - Calculate rx_status_computed
- [x] Implement BCMA Silver transformation:
  - Resolve LocalDrugSID → drug names
  - Resolve Sta3n → facility names
  - Resolve AdministeredByStaffSID → staff names
  - Resolve OrderingProviderSID → provider names
- [x] Test Silver ETL
- [x] Verify drug name lookups are correct
- [x] Output:
  - `medications_rxout_cleaned.parquet` (111 rows)
  - `medications_bcma_cleaned.parquet` (52 rows)

**Key Fix Applied:** Used NationalDrugSID from LocalDrug dimension table instead of stale values in fact tables to ensure correct drug name lookups.

**Deliverable:** Silver Parquet files with enriched data ✅

---

#### Day 4: Gold ETL and PostgreSQL Load ✅
**Goal:** Create patient-centric views and load to serving DB
**Status:** Complete - 2025-12-13

**Tasks:**
- [x] Create `etl/gold_patient_medications.py`
- [x] Implement RxOut Gold transformation:
  - Select and rename columns
  - Add patient_icn (ICN resolution: `ICN{100000 + patient_sid}`)
  - Add is_controlled_substance flag
  - Add is_active flag
  - Add days_until_expiration
  - Sort by IssueDateTime descending
- [x] Implement BCMA Gold transformation:
  - Select and rename columns
  - Add patient_icn
  - Add administration_variance flag
  - Add is_iv_medication flag
  - Sort by ActionDateTime descending
- [x] Create PostgreSQL DDL script:
  - `db/ddl/create_patient_medications_tables.sql` (both tables in one file)
- [x] Create `etl/load_medications.py`
- [x] Load Gold Parquet → PostgreSQL
- [x] Create indexes (11 indexes on outpatient, 6 on inpatient)
- [x] Verify row counts and data quality

**Results:**
- Gold Parquet files created:
  - `medications_rxout_final.parquet` (111 rows, 0 active due to past dates in mock data)
  - `medications_bcma_final.parquet` (52 rows)
- PostgreSQL tables loaded:
  - `patient_medications_outpatient` (111 rows, 23 unique patients, 14 controlled substances)
  - `patient_medications_inpatient` (52 rows, 20 unique patients, 7 controlled substances)
- Total: 163 medication records across both tables

**Data Quality Issue Identified:** See Section 12.4 for details on duplicate RxOutpatSID values in mock data.

**Deliverable:** PostgreSQL tables populated with medication data ✅

---

#### Day 5: API Endpoints (Part 1) ✅
**Goal:** Implement core medications API endpoints
**Status:** Complete - 2025-12-13

**Tasks:**
- [x] Create `app/routes/medications.py`
- [x] Create database query layer: `app/db/medications.py` (following established pattern instead of SQLAlchemy models)
- [x] Implement `GET /api/patient/{icn}/medications`
  - Query both tables (outpatient and inpatient)
  - Merge results with unified format
  - Apply filters (medication_type, status, days)
  - Sort by date descending
  - Returns JSON with counts and metadata
- [x] Implement `GET /api/patient/{icn}/medications/recent`
  - Last 90 days
  - Limit 8 (4 per type)
  - Both sources separated for widget
- [x] Implement `GET /api/patient/{icn}/medications/{medication_id}/details`
  - Parse medication_id (rxout_XXXX or bcma_XXXX format)
  - Return full medication details
- [x] Register routers in `app/main.py`
- [x] Test API endpoints with curl
- [x] Verify JSON response structure

**Testing Results:**
- ✅ `/api/patient/ICN101001/medications` - Returns 8 combined medications
- ✅ `/api/patient/ICN101001/medications?medication_type=outpatient` - Returns 4 outpatient medications
- ✅ `/api/patient/ICN101001/medications?medication_type=inpatient` - Returns inpatient medications with BCMA data
- ✅ `/api/patient/ICN101001/medications/recent` - Returns separated outpatient/inpatient lists
- ✅ `/api/patient/ICN101001/medications/rxout_40/details` - Returns full medication details
- ✅ Counts include: outpatient_total, outpatient_active, outpatient_controlled, inpatient_total, inpatient_controlled

**Deliverable:** Core API endpoints functional ✅

---

#### Day 6: API Endpoints (Part 2) and Widget HTML ✅
**Goal:** Implement details endpoint and widget HTML endpoint

**Tasks:**
- [x] Implement `GET /api/patient/{icn}/medications/{medication_id}/details`
  - Parse medication_id (rxout_XXXX or bcma_XXXX)
  - Query appropriate table
  - Return full details
- [x] Implement `GET /api/dashboard/widget/medications/{icn}`
  - Query recent medications
  - Render widget HTML template
  - Return HTMX-compatible fragment
- [x] Create widget template: `app/templates/partials/medications_widget.html`
- [x] Test widget HTML endpoint
- [x] Verify HTMX integration

**Deliverable:** All API endpoints complete, widget HTML rendering

**Completed:** 2025-12-13

**Implementation Notes:**
- Widget template created at `app/templates/partials/medications_widget.html` (following existing pattern)
- CSS styles added to `app/static/styles.css` for two-column layout
- Widget displays 4 outpatient + 4 inpatient medications (most recent)
- Controlled substance badges with DEA schedule display
- Empty states for columns with no data
- Fixed date filtering issue: Removed 90-day filter from `get_recent_medications()` to show most recent medications regardless of age (better for demo/testing environment)
- Widget tested successfully with multiple patients:
  - ICN100001: 4 outpatient + 4 inpatient (shows controlled substance badge)
  - ICN100002: 2 outpatient + 3 inpatient
  - ICN100015: No medications (empty state works correctly)
- All CSS classes properly applied and verified in stylesheet

---

#### Day 7: Dashboard Widget Integration (2x1 Layout) ✅
**Goal:** Integrate medications widget into dashboard with 2x1 two-column layout

**Tasks:**
- [x] Update `app/templates/dashboard.html` to include medications widget
- [x] Configure dashboard grid to accommodate 2x1 widget
- [x] Add HTMX trigger to load widget on patient selection
- [x] Style widget CSS for 2x1 layout:
  - Two-column grid layout (outpatient left, inpatient right)
  - Column headers with count badges
  - Controlled substance indicators
  - Status badges (color-coded)
  - Responsive layout (handled by existing CSS grid)
- [x] Test widget loading with multiple patients
- [x] Test with patients having both types and no medications

**Deliverable:** Medications widget (2x1) live on dashboard

**Completed:** 2025-12-13

**Implementation Notes:**
- Replaced placeholder widget in `app/templates/dashboard.html` with HTMX-loaded widget
- Widget configured as `widget--2x1` to span 2 columns in 3-column grid
- HTMX attributes: `hx-get="/api/patient/dashboard/widget/medications/{{ patient.icn }}"`, `hx-trigger="load"`, `hx-swap="innerHTML"`
- Widget loads automatically when dashboard page loads
- Existing CSS grid layout properly accommodates 2x1 widget:
  - Desktop: 3 columns (widget spans 2)
  - Tablet: 2 columns (widget spans full width)
  - Mobile: 1 column (all widgets full width)
- Widget displays:
  - Left column: Outpatient medications (most recent 4)
  - Right column: Inpatient medications (most recent 4)
  - Controlled substance badges with DEA schedule
  - Status badges (ACTIVE, EXPIRED, DISCONTINUED)
  - Count badges in column headers
  - "View All Medications" link routes to `/patient/{icn}/medications`
- Verified widget loading with:
  - ICN100001: Shows both outpatient and inpatient medications
  - ICN100015: Shows "No medications recorded" empty state

---

#### Day 8: Full Medications Page (Part 1) ✅
**Goal:** Create chronological table page with filtering

**Tasks:**
- [x] Create route `GET /patient/{icn}/medications` in `app/routes/medications.py` (already existed from Day 5)
- [x] Create template `app/templates/patient_medications.html`
- [x] Implement chronological table:
  - Table structure (Date, Medication, Type, Status, Provider)
  - Row rendering for RxOut medications
  - Row rendering for BCMA medications
  - Type badges (color-coded: blue for outpatient, gray for inpatient)
  - Status badges (color-coded: green=active, gray=expired, red=discontinued)
  - Controlled substance indicators (yellow background on rows, warning badge with DEA schedule)
- [x] Implement filtering:
  - Date range filter pills (30d, 90d, 6mo, 1yr, all time)
  - Type filter pills (all, outpatient, inpatient)
  - Status filter pills (all, active, expired, discontinued) - shown for outpatient only
  - Sort dropdown (date newest/oldest, drug name, type)
- [x] Test page rendering
- [x] Test filters (all filters working correctly)

**Deliverable:** Full medications page with table and filters

**Completed:** 2025-12-13

**Implementation Notes:**
- Created `app/templates/patient_medications.html` with full page layout
- Added comprehensive CSS styles to `app/static/styles.css` (250+ lines)
- Summary stats bar shows: Total, Outpatient, Inpatient, Active, Controlled Substances
- Filter controls organized into groups: Time Period, Type, Status (conditional), Sort
- Chronological table with columns: Date, Medication, Type, Status/Details, Provider
- Controlled substance rows highlighted with yellow background (`medication-row--controlled`)
- Responsive design: table scrolls horizontally on mobile, hides provider column on tablet
- Empty state handling: Shows different messages for filtered vs no medications
- Tested successfully:
  - ICN100001 with days=3650: Shows 8 medications (4 outpatient + 4 inpatient)
  - Outpatient filter: Shows 4 medications
  - Inpatient filter: Shows 4 medications
  - Active status filter: Shows 4 active medications
  - ICN100015 (no meds): Shows empty state
- Filter pills use active state styling (blue background when selected)
- Sort dropdown provides 4 options (date desc/asc, drug name, type)
- Default filter: 90 days (adjustable via filter pills)

---

#### Day 9: Full Medications Page (Part 2) - Expandable Details
**Goal:** Add expandable row details for full medication info

**Tasks:**
- [ ] Implement expandable row JavaScript:
  - Click row to expand
  - Show/hide details
  - Load details on demand (HTMX call to /details endpoint)
- [ ] Create detail templates:
  - RxOut details (prescription info, pharmacy, fills, etc.)
  - BCMA details (administration info, schedule, variance, etc.)
- [ ] Style detail panels
- [ ] Test expansion/collapse
- [ ] Test details loading for both RxOut and BCMA

**Deliverable:** Expandable row details working

---

#### Day 10: Testing and Polish
**Goal:** End-to-end testing and UI polish

**Tasks:**
- [ ] Test full ETL pipeline (Bronze → Silver → Gold → PostgreSQL)
- [ ] Test all API endpoints with various patients
- [ ] Test widget with 0, 5, 10, 20+ medications
- [ ] Test full page with different filters
- [ ] Test expandable details for multiple medications
- [ ] Visual polish:
  - Alignment and spacing
  - Badge colors and contrast
  - Controlled substance highlighting
  - Mobile responsiveness
- [ ] Performance testing (API response times < 1000ms)
- [ ] Error handling:
  - Patient not found
  - No medications
  - Database errors
- [ ] Logging review

**Deliverable:** Medications domain fully tested and polished

---

#### Day 11-12: Documentation and Review (Optional)
**Goal:** Complete documentation and design review

**Tasks:**
- [ ] Update `docs/medications-design.md` with implementation notes
- [ ] Document any deviations from design
- [ ] Create user guide section in docs
- [ ] Code review and refactoring
- [ ] Performance optimization if needed
- [ ] Prepare demo for stakeholders

**Deliverable:** Medications domain complete and documented

---

### A.2 Dependencies and Risks

**Dependencies:**
- ✅ Dashboard framework functional
- ✅ PostgreSQL serving DB operational
- ✅ ETL pipeline patterns established
- ✅ Existing RxOut and BCMA mock data

**Risks:**
1. **Drug Dimension Complexity:** Creating LocalDrug and NationalDrug with realistic linkages may take longer than expected
   - **Mitigation:** Start simple, focus on 20-30 drugs initially, expand later

2. **API Performance:** Querying two tables (RxOut + BCMA) and merging in memory may be slow for patients with 100+ medications
   - **Mitigation:** Add database indexes, implement pagination if needed, cache recent results

3. **UI Complexity:** Chronological table with mixed RxOut/BCMA data and expandable details is more complex than previous domains
   - **Mitigation:** Reuse Vitals table pattern, implement MVP first, add polish iteratively

4. **Data Quality:** Existing mock data may have inconsistencies in drug references
   - **Mitigation:** Audit and fix mock data during Day 1, ensure referential integrity

---

### Appendix B: VistA File Mappings

**VistA File #52 (PRESCRIPTION) → CDW RxOut.RxOutpat**

| VistA Field | VistA Field Name | CDW Column | Notes |
|-------------|------------------|------------|-------|
| .01 | PRESCRIPTION NUMBER | PrescriptionNumber | Unique prescription identifier |
| 2 | PATIENT | PatientSID | Foreign key to SPatient.Patient |
| 4 | DRUG | LocalDrugSID | Foreign key to Dim.LocalDrug |
| 6 | PROVIDER | ProviderSID | Prescribing provider |
| 8 | QTY (QUANTITY) | Quantity | Number of units dispensed |
| 22 | # OF REFILLS | RefillsAllowed | Max refills allowed |
| 9 | DAYS SUPPLY | DaysSupply | Number of days medication will last |
| 100 | STATUS | RxStatus | ACTIVE, DISCONTINUED, EXPIRED, etc. |
| 11 | MAIL/WINDOW | RxType | MAIL, WINDOW, CMOP |
| 26 | EXPIRATION DATE | ExpirationDateTime | Date prescription expires |
| 27 | ISSUE DATE | IssueDateTime | Date prescription written |

**VistA File #52 (PRESCRIPTION) Sub-file #52.01 (REFILL) → CDW RxOut.RxOutpatFill**

| VistA Field | VistA Field Name | CDW Column | Notes |
|-------------|------------------|------------|-------|
| .01 | REFILL # | FillNumber | 0 = original, 1+ = refills |
| 1 | REFILL DATE | FillDateTime | Date fill dispensed |
| 2 | RELEASED DATE/TIME | ReleasedDateTime | Date released to patient |
| 4 | QTY | QuantityDispensed | Quantity dispensed for this fill |
| 8 | PHARMACIST | DispensingPharmacistSID | Pharmacist who filled |

**VistA File #53.79 (BCMA MEDICATION LOG) → CDW BCMA.BCMAMedicationLog**

| VistA Field | VistA Field Name | CDW Column | Notes |
|-------------|------------------|------------|-------|
| .01 | LOG DATE/TIME | TransactionDateTime | Transaction timestamp |
| .02 | PATIENT | PatientSID | Foreign key to SPatient.Patient |
| .03 | ACTION STATUS | ActionStatus | COMPLETED, PENDING, etc. |
| .04 | ACTION TYPE | ActionType | GIVEN, HELD, REFUSED, MISSING DOSE |
| .05 | ORDERABLE ITEM | LocalDrugSID | Drug administered |
| .06 | SCHEDULE DATE/TIME | ScheduledDateTime | When medication was scheduled |
| .07 | ACTION DATE/TIME | ActionDateTime | When medication was given/held/refused |
| .08 | ADMINISTERED BY | AdministeredByStaffSID | Nurse who administered |
| .09 | DOSAGE ORDERED | DosageOrdered | Dose ordered by provider |
| .10 | DOSAGE GIVEN | DosageGiven | Actual dose given |
| .11 | ROUTE | Route | PO, IV, IM, SC, etc. |
| .12 | SCHEDULE | Schedule | QD, BID, TID, Q4H, PRN, etc. |

### Appendix C: Mock Data Summary

**Dimension Tables (NEW - to be created):**
- `Dim.LocalDrug`: 50+ drugs
- `Dim.NationalDrug`: 30+ drugs

**RxOut Tables (EXISTING):**
- `RxOut.RxOutpat`: 22 prescriptions across 10 patients
- `RxOut.RxOutpatFill`: 32 fills (original + refills)

**BCMA Tables (EXISTING):**
- `BCMA.BCMAMedicationLog`: 20 administration events across 8 inpatient stays

**Patient Coverage:**
- 10 patients with outpatient prescriptions
- 8 patients with inpatient administrations
- Mix of chronic, acute, controlled substances
- Intentional drug-drug interactions for future AI/ML work

### Appendix D: Glossary

**Terms:**
- **BCMA:** Bar Code Medication Administration - VistA inpatient medication administration system
- **CDW:** Corporate Data Warehouse - VA's centralized data repository
- **CMOP:** Consolidated Mail Outpatient Pharmacy - VA's mail-order pharmacy
- **DEA Schedule:** Drug Enforcement Administration controlled substance classification (C-II through C-V)
- **DDI:** Drug-Drug Interaction
- **IEN:** Internal Entry Number - VistA's unique record identifier
- **NDF:** National Drug File - VA's standardized drug formulary
- **PHI:** Protected Health Information
- **RxOut:** Outpatient Pharmacy domain in CDW (from VistA File #52)
- **SID:** Surrogate ID - CDW's unique record identifier
- **Sig:** Signatura - Dosing instructions printed on prescription label
- **VistA:** Veterans Health Information Systems and Technology Architecture

**Medication Statuses (RxOut):**
- **ACTIVE:** Prescription is current and refillable
- **DISCONTINUED:** Prescription was discontinued by provider
- **EXPIRED:** Prescription has passed expiration date
- **SUSPENDED:** Prescription temporarily on hold

**Action Types (BCMA):**
- **GIVEN:** Medication administered successfully
- **HELD:** Medication not given (nurse's discretion or provider order)
- **REFUSED:** Patient refused medication
- **MISSING DOSE:** Medication not available (e.g., pharmacy delay)
- **NOT GIVEN:** Medication skipped for other reasons

**Routes:**
- **PO:** By mouth (oral)
- **IV:** Intravenous
- **IM:** Intramuscular
- **SC:** Subcutaneous
- **IVPB:** Intravenous piggyback (intermittent IV)

**Schedules:**
- **QD:** Once daily
- **BID:** Twice daily
- **TID:** Three times daily
- **QID:** Four times daily
- **Q4H:** Every 4 hours
- **PRN:** As needed
- **QHS:** At bedtime

### Appendix E: Data Quality Issues

**Issue: Duplicate RxOutpatSID Values in Mock Data**

**Problem:**
During Day 4 implementation (PostgreSQL Load), discovered that the mock `RxOut.RxOutpat` table contains 4 duplicate `RxOutpatSID` values:
- RxOutpatSID 5019 (2 occurrences)
- RxOutpatSID 5020 (2 occurrences)
- RxOutpatSID 5021 (2 occurrences)
- RxOutpatSID 5022 (2 occurrences)

Each duplicate SID is assigned to different prescriptions for different patients with different medications. For example:
- `rx_outpat_id=5021` appears for two different patients with different drugs (ALPRAZOLAM vs another medication)

This violates the expected uniqueness constraint on the surrogate key column, which should be unique across all rows.

**Root Cause:**
The mock data was populated with duplicate SID values, likely due to data generation scripts reusing the same ID ranges across different test scenarios without proper deduplication.

**Solution Implemented:**
Removed `UNIQUE` constraints from the PostgreSQL serving database schema:
- `patient_medications_outpatient.rx_outpat_id` - Changed from `BIGINT NOT NULL UNIQUE` to `BIGINT NOT NULL`
- `patient_medications_inpatient.bcma_log_id` - Changed from `BIGINT NOT NULL UNIQUE` to `BIGINT NOT NULL` (preventative, no duplicates found in BCMA data)

Updated file: `db/ddl/create_patient_medications_tables.sql`

**Impact:**
- **No functional impact on application queries or logic.** All patient-centric queries use `patient_icn` as the primary identifier, and medication queries use the auto-generated `medication_outpatient_id` and `medication_inpatient_id` primary keys.
- **Development/testing acceptable.** The duplicate SIDs do not affect the UI, API, or data integrity for the purposes of this development environment.
- **Production note:** Real CDW data would have unique SIDs. This issue is specific to the mock data environment.

**Future Work (Optional):**
May regenerate mock `RxOut.RxOutpat` data with unique SIDs to improve overall mock data quality and better align with production CDW data characteristics. This would involve:
1. Updating the mock data INSERT scripts to ensure unique RxOutpatSID values
2. Re-running the Bronze, Silver, and Gold ETL pipelines
3. Reloading PostgreSQL serving database
4. Restoring the UNIQUE constraints in the DDL

**Status:** Accepted as-is for current phase. May address in future mock data quality improvement initiative.

---

### Appendix F: Future Enhancements (Out of Scope for Phase 1)

**Phase 2 Features:**
1. **Sig/Instructions Display:** Show structured dosing instructions (RxOut.RxOutpatSig)
2. **IV Medications Detail:** Display IV additives and solutions (BCMA.BCMAAdditive, BCMA.BCMASolution)
3. **Refills Remaining:** Show refill count and "refill needed" alerts
4. **Medication Reconciliation:** Compare medications across care transitions
5. **Advanced Filtering:** Filter by drug class, provider, facility

**Phase 3 Features (AI/ML):**
1. **Drug-Drug Interaction Detection:** Identify risky medication combinations
2. **Allergy Cross-Check:** Alert when medication conflicts with patient allergies
3. **Medication Adherence Tracking:** Flag missed doses or unfilled prescriptions
4. **Predictive Analytics:** Identify patients at risk for adverse drug events

**Phase 4 Features (Integration):**
1. **CPRS Integration:** Allow medication ordering from med-z1
2. **My HealtheVet Integration:** Patient-facing medication list
3. **Real-Time BCMA Updates:** Live medication administration updates
4. **Pharmacy Benefit Manager (PBM) Integration:** Cost and formulary info

---


**End of Document**
