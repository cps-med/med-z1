# CDWWork2 (Oracle Health/Cerner) Mock Database - Design Document

**Document Version:** 1.1
**Date:** 2025-12-17
**Last Updated:** 2025-12-17
**Status:** ✅ Ready for Implementation - All Open Questions Resolved
**Implementation Phase:** Not Started

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Background and Context](#3-background-and-context)
4. [Mock Database Architecture](#4-mock-database-architecture)
5. [Code Set System Design](#5-code-set-system-design)
6. [Clinical Domain Schemas](#6-clinical-domain-schemas)
7. [Patient Identity and Site Assignment](#7-patient-identity-and-site-assignment)
8. [ETL Architecture Changes](#8-etl-architecture-changes)
9. [Data Source Lineage Tracking](#9-data-source-lineage-tracking)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Testing Strategy](#11-testing-strategy)
12. [Open Questions and Future Considerations](#12-open-questions-and-future-considerations)
13. [Appendices](#13-appendices)

---

## 1. Overview

### 1.1 Purpose

The **CDWWork2** mock database extends the med-z1 application's data layer to simulate the VA Corporate Data Warehouse's Oracle Health (Cerner Millennium) database. This enables the application to:

- **Test multi-source data integration** - Combine data from both VistA (CDWWork) and Oracle Health (CDWWork2) systems
- **Simulate real VA architecture** - Mirror the dual-database structure used in production VA CDW
- **Support Cerner site migration scenarios** - Test patient data from sites that have transitioned from VistA to Oracle Health
- **Validate Silver layer harmonization** - Prove ETL can merge disparate data models into unified output
- **Prepare for production deployment** - Ensure med-z1 works with both legacy and modern VA EHR systems

### 1.2 Real-World Context

As of late 2024, the VA is in the midst of a multi-year transition from legacy VistA systems to the Oracle Health (formerly Cerner Millennium) electronic health record platform. This transition creates a **dual-source data environment**:

**CDWWork (Legacy VistA Data)**:
- Data from 130+ VistA sites nationwide
- Patient-centric data model (organized around veteran's longitudinal record)
- Schema structure: `Dim.*`, `SPatient.*`, `Inpat.*`, `RxOut.*`, etc.
- Updated nightly from VistA sites via VX130 extraction process

**CDWWork2 (Oracle Health Data)**:
- Data from ~5-8 "go-live" Cerner sites (expanding over time)
- Encounter-centric data model (organized around specific visits/admissions)
- Schema structure: `*Mill` suffix (e.g., `AllergyMill`, `EncMill`, `VitalMill`)
- Syndicated from Cerner Millennium (~1,200 source tables)
- Uses consolidated Code Set system (`NDimMill.CodeValue`) instead of many dimension tables

**Critical Distinction**: A given VA site exists in **only one** database:
- Sites that have "gone live" with Cerner → Data in CDWWork2
- Sites still using VistA → Data in CDWWork
- Historical data (pre-migration) for Cerner sites → Still in CDWWork

### 1.3 Scope

**In Scope for Initial Implementation:**
- Separate CDWWork2 database in same SQL Server instance as CDWWork
- Five core schemas: `NDimMill`, `VeteranMill`, `EncMill`, `AllergyMill`, `VitalMill`, `LabMill`
- Three designated Cerner sites (Sta3n 648, 663, 531)
- Shared patient identities across CDWWork and CDWWork2 (same PatientSID/ICN)
- Encounter-centric data model with mandatory encounter linkage
- Consolidated Code Set system (`NDimMill.CodeValue` with essential code sets)
- Dual-source Bronze ETL extraction (`bronze/cdwwork/`, `bronze/cdwwork2/`)
- Enhanced Silver ETL with VistA ↔ Cerner harmonization logic
- Data source lineage tracking in Gold/PostgreSQL layers
- Initial clinical domains: Demographics, Encounters, Vitals, Allergies, Labs

**Out of Scope for Initial Implementation:**
- Full Cerner Millennium table replication (~1,200 tables - only core clinical domains)
- CDWWork3 "converged" database simulation (using CDWWork2 directly instead)
- Advanced Code Set metadata tables beyond `CodeValue` (e.g., `CodeValueSet`, `CodeSystem`)
- Medication administration (MedMill) - deferred to Phase 2
- Orders (OrderMill) - deferred to later phase
- Clinical notes (DocMill) - deferred to later phase
- Real-time Cerner data feeds (mock is static like CDWWork)
- Multi-site patient matching/deduplication (assume clean PatientSID mapping)

### 1.4 Key Design Decisions

1. **Separate Database**: CDWWork2 as distinct database, not merged into CDWWork
2. **"Mill" Schema Naming**: Follow Cerner convention with "Mill" suffix for all schemas
3. **Shared Patient Identities**: Same PatientSID values for same patients across both databases
4. **Designated Cerner Sites**: Three specific sites (648, 663, 531) exclusively in CDWWork2
5. **Encounter-First Design**: Create realistic encounters before populating clinical data
6. **Simplified Code Sets**: Start with 8-10 essential code sets, expand as needed
7. **Dual-Source Bronze**: Separate Bronze extraction paths, merge in Silver layer
8. **Source Lineage Tracking**: Add `data_source` column to all Gold/PostgreSQL tables
9. **Domain-by-Domain Rollout**: Implement one clinical domain at a time, not big bang
10. **Recent Data Only**: CDWWork2 contains post-migration data (last 6-12 months), historical data remains in CDWWork
11. **Encounter-Centric Foreign Keys**: All clinical records require `EncounterSID` (non-NULL)
12. **Code Value Denormalization**: Store both `CodeValueSID` and resolved `Display` text for performance

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Dual-Source Integration**: Successfully merge VistA and Cerner data into unified Silver/Gold layers
2. **Architectural Validation**: Prove med-z1's medallion architecture scales to multi-source scenarios
3. **Data Model Harmonization**: Bridge patient-centric (VistA) and encounter-centric (Cerner) data models
4. **Site Migration Simulation**: Enable testing of "patient treated at both VistA and Cerner sites" scenarios
5. **Source Transparency**: Maintain data lineage so consumers know which EHR system originated each record

### 2.2 Success Criteria

**Technical Success**:
- ✅ CDWWork2 database created with 5+ schemas and 15+ tables
- ✅ 3-4 synthetic patients have data in both CDWWork and CDWWork2
- ✅ ETL pipeline successfully extracts from both sources to Bronze
- ✅ Silver layer merges VistA and Cerner data without duplication
- ✅ Gold layer includes `data_source` column showing origin ("CDWWork" or "CDWWork2")
- ✅ PostgreSQL queries return merged results with source attribution
- ✅ UI displays combined data transparently (source visible in details/tooltips)

**Functional Success**:
- ✅ Patient with vitals at both VistA and Cerner sites sees all vitals in UI
- ✅ Demographics page shows unified patient information from both sources
- ✅ Allergies page combines drug allergies from VistA sites and Cerner sites
- ✅ Labs page displays results from both CDWWork and CDWWork2 labs
- ✅ Cross-source deduplication works correctly (no duplicate records for same event)

**Operational Success**:
- ✅ Mock database can be rebuilt from scratch (scripts only, no manual steps)
- ✅ ETL runtime increases by <20% when processing both sources
- ✅ Documentation clearly explains VistA ↔ Cerner field mappings
- ✅ New developers can add CDWWork2 tables following established patterns

### 2.3 Non-Goals

- **Not** attempting 100% Cerner Millennium schema fidelity (only core clinical domains)
- **Not** simulating real Cerner data quality issues (clean data only)
- **Not** implementing full HL7 FHIR transformation (internal data model only)
- **Not** testing CDWWork3 convergence patterns (out of scope)
- **Not** supporting bi-directional data sync (read-only mock data)

---

## 3. Background and Context

### 3.1 VistA vs. Oracle Health Data Models

The fundamental difference between CDWWork and CDWWork2 stems from the underlying EHR philosophies:

**VistA (CDWWork) - Patient-Centric Model**:
```
Philosophy: "Build a complete picture of the veteran's health over time"

Patient (SPatient.Spatient)
 ├─> Allergies (Allergy.PatientAllergy) - many per patient
 ├─> Vitals (Vital.VitalSign) - many per patient
 ├─> Medications (RxOut.RxOutpat) - many per patient
 └─> Lab Results (Chem.LabChem) - many per patient

Query Pattern: "Give me all vitals for Patient 1001"
```

**Cerner (CDWWork2) - Encounter-Centric Model**:
```
Philosophy: "Document what happened during each healthcare encounter"

Patient (VeteranMill.SPerson)
 └─> Encounters (EncMill.Encounter) - many per patient
      ├─> Allergies (AllergyMill.PersonAllergy) - documented during encounter
      ├─> Vitals (VitalMill.VitalResult) - measured during encounter
      ├─> Medications (MedMill.MedicationOrder) - ordered during encounter
      └─> Lab Results (LabMill.LabResult) - collected during encounter

Query Pattern: "Give me all vitals collected during Encounter 5001 for Patient 1001"
```

**Implications for med-z1**:
- Silver layer must "flatten" Cerner's encounter hierarchy for patient-centric queries
- PostgreSQL serving tables remain patient-centric (UI queries by ICN, not EncounterID)
- Encounter information preserved as metadata (useful for context, not primary key)
- Harmonization logic maps Cerner's EncounterSID → optional encounter_id in PostgreSQL

### 3.2 Schema Naming Conventions

**CDWWork (VistA)**:
```sql
-- Schemas named after clinical domains or VistA packages
Dim           -- Dimension tables (reference data)
SPatient      -- Patient demographics and administration
Inpat         -- Inpatient encounters
RxOut         -- Outpatient pharmacy
BCMA          -- Barcode Medication Administration
Vital         -- Vital signs
Allergy       -- Allergies and adverse reactions
Chem          -- Chemistry lab results
```

**CDWWork2 (Cerner Millennium)**:
```sql
-- Schemas suffixed with "Mill" (Millennium)
NDimMill      -- Reference/dimension data (consolidated code sets)
VeteranMill   -- Patient/person demographics
EncMill       -- Encounters (visits, admissions)
AllergyMill   -- Allergy and adverse reaction events
VitalMill     -- Vital sign measurements (clinical events)
LabMill       -- Laboratory results
MedMill       -- Medication orders and administration (future)
OrderMill     -- Clinical orders (future)
DocMill       -- Clinical documentation (future)
```

**Naming Rationale**:
- Clear separation prevents accidental cross-database queries
- "Mill" suffix indicates Cerner Millennium origin
- Mirrors real VA CDW naming conventions for authenticity

### 3.3 The Code Set System

**Problem**: VistA uses dozens of small dimension tables for categorical data. Cerner uses a different approach.

**VistA Approach (Many Small Tables)**:
```sql
-- Separate dimension table for each categorical type
Dim.VitalType       -- 8-10 rows (BP, Temp, Pulse, etc.)
Dim.VitalQualifier  -- 15-20 rows (Standing, Sitting, etc.)
Dim.AllergySeverity -- 3-4 rows (MILD, MODERATE, SEVERE)
Dim.Reaction        -- 30-40 rows (HIVES, RASH, ANAPHYLAXIS, etc.)
-- ... dozens more dimension tables
```

**Cerner Approach (One Large Table with Code Sets)**:
```sql
-- Single table with CodeValueSetID to differentiate types
NDimMill.CodeValue
  CodeValueSID    -- Unique ID (primary key)
  CodeValueSetID  -- Identifies the "set" (e.g., 27 = Ethnicity, 38 = Marital Status)
  Display         -- Human-readable label
  DisplayKey      -- Uppercase searchable key

-- Example data:
CodeValueSID | CodeValueSetID | Display              | DisplayKey
-------------|----------------|----------------------|--------------------
101          | 27             | Hispanic or Latino   | HISPANIC OR LATINO
102          | 27             | Not Hispanic/Latino  | NOT HISPANIC OR LATINO
201          | 38             | Married              | MARRIED
202          | 38             | Divorced             | DIVORCED
4001         | 72             | Systolic BP          | SYSTOLIC BP
4002         | 72             | Body Temperature     | BODY TEMPERATURE
```

**Trade-offs**:
- ✅ Cerner: Fewer tables to manage (1 vs. 50+)
- ✅ VistA: Simpler queries (direct FK to dimension table)
- ⚠️ Cerner: Must always filter by `CodeValueSetID` in WHERE clause
- ⚠️ VistA: Schema proliferation (new dimension table for each category)

**med-z1 Strategy**: Start with simplified Code Set approach (8-10 essential sets), expand as needed.

### 3.4 Encounter-Centric Foreign Keys

**Critical Pattern**: Every clinical record in CDWWork2 **must** link to an encounter.

**Example - Allergy Documentation**:

```sql
-- VistA (CDWWork): Encounter link is optional
INSERT INTO Allergy.PatientAllergy (
    PatientAllergySID, PatientSID, AllergenSID, EnteredDateTime, ...
) VALUES (
    1, 1001, 45, '2024-03-15 10:30:00', ...
    -- No EncounterSID - allergy may have been entered outside of a specific visit
);

-- Cerner (CDWWork2): Encounter link is REQUIRED
INSERT INTO AllergyMill.PersonAllergy (
    AllergyInstanceSID, PatientSID, EncounterSID, SubstanceDisplay, ...
) VALUES (
    1, 1001, 5001, 'PENICILLIN VK 500MG', ...
    -- EncounterSID 5001 REQUIRED - tracks WHICH visit/admission the allergy was documented
);
```

**Implications**:
- Must create realistic encounters in `EncMill.Encounter` before populating clinical data
- Every CDWWork2 clinical insert needs a valid `EncounterSID`
- Silver layer can preserve or discard encounter linkage (med-z1 uses encounter as optional metadata)

---

## 4. Mock Database Architecture

### 4.1 Database Structure

**SQL Server Instance Organization**:
```
Docker Container: sqlserver (Microsoft SQL Server 2019)
├── master (system database)
├── CDWWork (existing - VistA data)
│   ├── Dim schema (dimension tables)
│   ├── SPatient schema (patient data)
│   ├── Inpat schema (inpatient encounters)
│   ├── RxOut schema (outpatient pharmacy)
│   ├── BCMA schema (medication administration)
│   ├── Vital schema (vital signs)
│   ├── Allergy schema (allergies)
│   └── Chem schema (lab results)
└── CDWWork2 (NEW - Oracle Health/Cerner data)
    ├── NDimMill schema (reference/code sets)
    ├── VeteranMill schema (patient demographics)
    ├── EncMill schema (encounters)
    ├── AllergyMill schema (allergies)
    ├── VitalMill schema (vitals)
    └── LabMill schema (labs)
```

**Rationale for Separate Database**:
- Mirrors real VA CDW architecture (CDWWork ≠ CDWWork2)
- Clear separation of concerns (VistA vs. Cerner)
- Independent rebuild/testing (can drop CDWWork2 without affecting CDWWork)
- Simplifies ETL source routing (connection string determines source)
- Enables different collation/settings if needed

### 4.2 Schema Organization

**NDimMill (Reference/Dimension Data)**:
```sql
-- Consolidated code sets table (replaces dozens of VistA Dim.* tables)
NDimMill.CodeValue            -- Code set master table

-- Future: Additional reference tables as needed
-- NDimMill.CodeValueSet      -- Code set metadata (deferred)
-- NDimMill.EventCode         -- Clinical event types (deferred)
```

**VeteranMill (Patient Demographics)**:
```sql
VeteranMill.SPerson           -- Core patient demographics
-- Future: Address, insurance, disability, etc.
```

**EncMill (Encounters)**:
```sql
EncMill.Encounter             -- Visits, admissions, contacts
-- Future: Encounter providers, diagnoses, etc.
```

**AllergyMill (Allergies)**:
```sql
AllergyMill.PersonAllergy     -- Allergy instances
AllergyMill.AdverseReaction   -- Reactions (bridge table to CodeValue)
```

**VitalMill (Vital Signs)**:
```sql
VitalMill.VitalResult         -- Vital sign measurements
```

**LabMill (Laboratory)**:
```sql
LabMill.LabResult             -- Lab test results
```

### 4.3 File Organization

**Directory Structure**:
```
mock/sql-server/
├── cdwwork/                  (existing - VistA)
│   ├── create/
│   │   ├── db_database.sql
│   │   ├── db_schemas.sql
│   │   ├── Dim.*.sql
│   │   └── ...
│   └── insert/
│       ├── _master.sql
│       ├── Dim.*.sql
│       └── ...
└── cdwwork2/                 (NEW - Cerner)
    ├── create/
    │   ├── db_database.sql   -- CREATE DATABASE CDWWork2
    │   ├── db_schemas.sql    -- CREATE SCHEMA NDimMill, VeteranMill, etc.
    │   ├── NDimMill.CodeValue.sql
    │   ├── VeteranMill.SPerson.sql
    │   ├── EncMill.Encounter.sql
    │   ├── AllergyMill.PersonAllergy.sql
    │   ├── AllergyMill.AdverseReaction.sql
    │   ├── VitalMill.VitalResult.sql
    │   ├── LabMill.LabResult.sql
    │   └── _master.sql       -- Orchestration script
    └── insert/
        ├── _master.sql       -- Orchestration script
        ├── NDimMill.CodeValue.sql  -- Populate code sets
        ├── VeteranMill.SPerson.sql
        ├── EncMill.Encounter.sql   -- MUST run before clinical data
        ├── AllergyMill.PersonAllergy.sql
        ├── VitalMill.VitalResult.sql
        └── LabMill.LabResult.sql
```

**Script Execution Pattern**:
```bash
# Create CDWWork2 database and schemas
docker exec -i sqlserver /opt/mssql-tools18/bin/sqlcmd ... \
  < mock/sql-server/cdwwork2/create/_master.sql

# Populate CDWWork2 tables (code sets → patients → encounters → clinical data)
docker exec -i sqlserver /opt/mssql-tools18/bin/sqlcmd ... \
  < mock/sql-server/cdwwork2/insert/_master.sql
```

---

## 5. Code Set System Design

### 5.1 Core Table Schema

**NDimMill.CodeValue**:
```sql
CREATE TABLE NDimMill.CodeValue (
    CodeValueSID        BIGINT          PRIMARY KEY,  -- Unique surrogate ID
    CodeValueID         BIGINT,                       -- Original Cerner ID (for reference)
    CodeValueSetID      INT             NOT NULL,     -- The "set" this code belongs to
    CDFMeaning          VARCHAR(50),                  -- Internal system meaning
    Display             VARCHAR(100)    NOT NULL,     -- Human-readable label
    DisplayKey          VARCHAR(100),                 -- Uppercase searchable key
    ActiveInd           BIT             DEFAULT 1,    -- Is this code active?
    Description         VARCHAR(255),                 -- Longer description (optional)

    INDEX IX_CodeValueSet (CodeValueSetID, Display)   -- Optimize lookups by set
);
```

**Field Descriptions**:
- **CodeValueSID**: Primary key, unique across all code sets (no collisions)
- **CodeValueSetID**: Identifies which category (e.g., 27 = Ethnicity, 38 = Marital Status)
- **Display**: User-facing text (e.g., "Hispanic or Latino", "Married")
- **DisplayKey**: Uppercase version for case-insensitive searches
- **ActiveInd**: Allows soft-deletion of deprecated codes without breaking FKs

### 5.2 Essential Code Sets (Initial Implementation)

| CodeValueSetID | Category | Purpose | Example Values | Table Count |
|---------------|----------|---------|----------------|-------------|
| 27 | Ethnicity | Patient demographics | Hispanic/Latino, Not Hispanic/Latino | 2-3 |
| 38 | Marital Status | Patient demographics | Married, Divorced, Single, Widowed | 4-5 |
| 48 | Gender | Patient demographics | Male, Female, Unknown | 3-4 |
| 72 | Vital Event Types | Vital sign measurements | Systolic BP, Diastolic BP, Temperature, Pulse, Respiration | 10-12 |
| 90 | Result Units | Lab/vital units | mmHg, F, C, mg/dL, mEq/L | 15-20 |
| 261 | Admit Status | Encounter status | Active, Discharged, Left AMA | 5-6 |
| 281 | Encounter Type | Encounter classification | Inpatient, Outpatient, Emergency | 4-5 |
| 4002 | Allergy Severity | Allergy severity levels | Mild, Moderate, Severe | 3-4 |
| 4003 | Allergy Reaction | Adverse reactions | Hives, Rash, Anaphylaxis, Nausea | 20-30 |
| 6000 | Abnormal Flag | Lab result interpretation | Normal, High, Critical High, Low | 6-8 |

**Total Initial Codes**: ~100-150 rows in `NDimMill.CodeValue`

### 5.3 Usage Pattern Examples

**Query Pattern - Get All Marital Statuses**:
```sql
-- Retrieve all values in the "Marital Status" code set (38)
SELECT CodeValueSID, Display
FROM NDimMill.CodeValue
WHERE CodeValueSetID = 38
  AND ActiveInd = 1
ORDER BY Display;

-- Result:
-- CodeValueSID | Display
-- -------------|----------
-- 201          | Divorced
-- 202          | Married
-- 203          | Single
-- 204          | Widowed
```

**Join Pattern - Resolve Code in Patient Demographics**:
```sql
-- Get patient with resolved marital status text
SELECT
    p.PatientSID,
    p.PatientName,
    cv.Display AS MaritalStatus
FROM VeteranMill.SPerson p
LEFT JOIN NDimMill.CodeValue cv
    ON p.MaritalStatusCodeValueSID = cv.CodeValueSID
WHERE p.PatientSID = 1001;
```

**Denormalization Pattern** (Recommended for Performance):
```sql
-- Store BOTH CodeValueSID (for FK integrity) AND Display text (for fast queries)
CREATE TABLE VitalMill.VitalResult (
    VitalResultSID          BIGINT PRIMARY KEY,
    PatientSID              BIGINT,
    EncounterSID            BIGINT,
    EventCodeValueSID       BIGINT,        -- FK to NDimMill.CodeValue
    EventType               VARCHAR(50),   -- Denormalized "Systolic BP" (no JOIN needed)
    ResultUnitsCodeValueSID BIGINT,        -- FK to NDimMill.CodeValue
    ResultUnits             VARCHAR(20),   -- Denormalized "mmHg" (no JOIN needed)
    ...
);
```

**Rationale**: Reduces JOINs in Bronze/Silver ETL and improves query performance.

### 5.4 Code Set Population Script

**File**: `mock/sql-server/cdwwork2/insert/NDimMill.CodeValue.sql`

```sql
USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- CodeValueSetID 27: Ethnicity
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(2701, 27, 'Hispanic or Latino', 'HISPANIC OR LATINO'),
(2702, 27, 'Not Hispanic or Latino', 'NOT HISPANIC OR LATINO'),
(2703, 27, 'Unknown', 'UNKNOWN');

-- CodeValueSetID 38: Marital Status
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(3801, 38, 'Married', 'MARRIED'),
(3802, 38, 'Divorced', 'DIVORCED'),
(3803, 38, 'Single', 'SINGLE'),
(3804, 38, 'Widowed', 'WIDOWED'),
(3805, 38, 'Unknown', 'UNKNOWN');

-- CodeValueSetID 48: Gender
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(4801, 48, 'Male', 'MALE'),
(4802, 48, 'Female', 'FEMALE'),
(4803, 48, 'Unknown', 'UNKNOWN');

-- CodeValueSetID 72: Vital Event Types
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(7201, 72, 'Systolic BP', 'SYSTOLIC BP'),
(7202, 72, 'Diastolic BP', 'DIASTOLIC BP'),
(7203, 72, 'Temperature', 'TEMPERATURE'),
(7204, 72, 'Pulse', 'PULSE'),
(7205, 72, 'Respiration', 'RESPIRATION'),
(7206, 72, 'Pulse Oximetry', 'PULSE OXIMETRY'),
(7207, 72, 'Height', 'HEIGHT'),
(7208, 72, 'Weight', 'WEIGHT'),
(7209, 72, 'Pain Scale', 'PAIN SCALE');

-- CodeValueSetID 90: Result Units
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(9001, 90, 'mmHg', 'MMHG'),
(9002, 90, 'F', 'F'),
(9003, 90, 'C', 'C'),
(9004, 90, 'bpm', 'BPM'),
(9005, 90, 'breaths/min', 'BREATHS/MIN'),
(9006, 90, '%', '%'),
(9007, 90, 'in', 'IN'),
(9008, 90, 'cm', 'CM'),
(9009, 90, 'lb', 'LB'),
(9010, 90, 'kg', 'KG'),
(9011, 90, 'mg/dL', 'MG/DL'),
(9012, 90, 'mEq/L', 'MEQ/L');

-- CodeValueSetID 261: Admit Status
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(26101, 261, 'Active', 'ACTIVE'),
(26102, 261, 'Discharged', 'DISCHARGED'),
(26103, 261, 'Left AMA', 'LEFT AMA'),
(26104, 261, 'Transferred', 'TRANSFERRED');

-- CodeValueSetID 281: Encounter Type
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(28101, 281, 'Inpatient', 'INPATIENT'),
(28102, 281, 'Outpatient', 'OUTPATIENT'),
(28103, 281, 'Emergency', 'EMERGENCY'),
(28104, 281, 'Telehealth', 'TELEHEALTH');

-- CodeValueSetID 4002: Allergy Severity
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(400201, 4002, 'Mild', 'MILD'),
(400202, 4002, 'Moderate', 'MODERATE'),
(400203, 4002, 'Severe', 'SEVERE');

-- CodeValueSetID 4003: Allergy Reactions
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(400301, 4003, 'Hives', 'HIVES'),
(400302, 4003, 'Rash', 'RASH'),
(400303, 4003, 'Itching', 'ITCHING'),
(400304, 4003, 'Swelling', 'SWELLING'),
(400305, 4003, 'Anaphylaxis', 'ANAPHYLAXIS'),
(400306, 4003, 'Nausea', 'NAUSEA'),
(400307, 4003, 'Vomiting', 'VOMITING'),
(400308, 4003, 'Diarrhea', 'DIARRHEA'),
(400309, 4003, 'Difficulty Breathing', 'DIFFICULTY BREATHING'),
(400310, 4003, 'Hypotension', 'HYPOTENSION');

-- CodeValueSetID 6000: Abnormal Flag
INSERT INTO NDimMill.CodeValue (CodeValueSID, CodeValueSetID, Display, DisplayKey) VALUES
(600001, 6000, 'Normal', 'NORMAL'),
(600002, 6000, 'High', 'HIGH'),
(600003, 6000, 'Critical High', 'CRITICAL HIGH'),
(600004, 6000, 'Low', 'LOW'),
(600005, 6000, 'Critical Low', 'CRITICAL LOW'),
(600006, 6000, 'Abnormal', 'ABNORMAL');

GO

PRINT 'NDimMill.CodeValue populated with essential code sets';
GO
```

---

## 6. Clinical Domain Schemas

### 6.1 Demographics - VeteranMill.SPerson

**Purpose**: Core patient demographics for Cerner sites.

**Schema**:
```sql
CREATE TABLE VeteranMill.SPerson (
    PatientSID              BIGINT          PRIMARY KEY,  -- Shared with CDWWork
    PatientICN              VARCHAR(50)     NOT NULL,     -- Integration Control Number
    PatientName             VARCHAR(255),
    SSN                     VARCHAR(11),                  -- Format: 123-45-6789
    DateOfBirth             DATE,

    -- Code Set References (with denormalized display text)
    GenderCodeValueSID      BIGINT,                       -- FK to NDimMill.CodeValue (Set 48)
    Gender                  VARCHAR(20),                  -- Denormalized: "Male"

    MaritalStatusCodeValueSID BIGINT,                     -- FK to NDimMill.CodeValue (Set 38)
    MaritalStatus           VARCHAR(50),                  -- Denormalized: "Married"

    EthnicityCodeValueSID   BIGINT,                       -- FK to NDimMill.CodeValue (Set 27)
    Ethnicity               VARCHAR(100),                 -- Denormalized: "Hispanic or Latino"

    -- Contact Info
    StreetAddress           VARCHAR(255),
    City                    VARCHAR(100),
    State                   VARCHAR(2),                   -- Two-letter code
    ZipCode                 VARCHAR(10),
    PhoneNumber             VARCHAR(20),
    EmailAddress            VARCHAR(100),

    -- Metadata
    CreatedDateTime         DATETIME2       DEFAULT GETDATE(),
    UpdatedDateTime         DATETIME2,
    Sta3n                   INT,                          -- Station number (648, 663, or 531)

    INDEX IX_PatientICN (PatientICN),
    INDEX IX_Sta3n (Sta3n)
);
```

**Key Design Points**:
- **PatientSID**: Same values as CDWWork's `SPatient.Spatient.PatientSID` for shared patients
- **Code Set FKs**: Store both SID and denormalized text for performance
- **Sta3n**: Identifies which Cerner site manages this patient (648, 663, or 531)

**VistA ↔ Cerner Field Mapping**:

| CDWWork (VistA) | CDWWork2 (Cerner) | Notes |
|----------------|------------------|-------|
| `SPatient.Spatient.PatientSID` | `VeteranMill.SPerson.PatientSID` | Shared primary key |
| `SPatient.Spatient.PatientICN` | `VeteranMill.SPerson.PatientICN` | Shared ICN |
| `SPatient.Spatient.PatientName` | `VeteranMill.SPerson.PatientName` | Direct mapping |
| `SPatient.Spatient.DOB` | `VeteranMill.SPerson.DateOfBirth` | Column name differs |
| `SPatient.Spatient.Gender` | `NDimMill.CodeValue (Set 48) → Gender` | VistA uses text, Cerner uses code set |
| `SPatient.Spatient.MaritalStatus` | `NDimMill.CodeValue (Set 38) → MaritalStatus` | VistA uses text, Cerner uses code set |

### 6.2 Encounters - EncMill.Encounter

**Purpose**: Capture all healthcare encounters (visits, admissions) at Cerner sites.

**Schema**:
```sql
CREATE TABLE EncMill.Encounter (
    EncounterSID            BIGINT          PRIMARY KEY,
    EncounterID             BIGINT,                       -- Original Cerner encounter ID
    PatientSID              BIGINT          NOT NULL,     -- FK to VeteranMill.SPerson

    -- Encounter Type/Status (with denormalized display text)
    EncounterTypeCodeValueSID BIGINT,                     -- FK to NDimMill.CodeValue (Set 281)
    EncounterType           VARCHAR(50),                  -- Denormalized: "Inpatient"

    AdmitStatusCodeValueSID BIGINT,                       -- FK to NDimMill.CodeValue (Set 261)
    AdmitStatus             VARCHAR(50),                  -- Denormalized: "Active"

    -- Dates/Times
    AdmitDateTime           DATETIME2       NOT NULL,
    DischargeDateTime       DATETIME2,                    -- NULL if still active

    -- Location (reuse CDWWork Dim.Location if possible, or create EncMill.Location)
    AdmitLocationSID        INT,                          -- FK to Dim.Location (shared)
    AdmitLocationName       VARCHAR(100),                 -- Denormalized

    DischargeLocationSID    INT,
    DischargeLocationName   VARCHAR(100),

    -- Metadata
    Sta3n                   INT             NOT NULL,     -- Station (648, 663, or 531)

    INDEX IX_Patient (PatientSID),
    INDEX IX_AdmitDateTime (AdmitDateTime),
    INDEX IX_Sta3n (Sta3n)
);
```

**Key Design Points**:
- **EncounterSID**: Primary key for all encounter references
- **Encounter Type**: Inpatient, Outpatient, Emergency, Telehealth
- **Admit/Discharge Dates**: Tracks encounter timeline
- **Location**: Reuse `Dim.Location` from CDWWork for simplicity (shared dimension)

**Sample Data**:
```sql
-- Patient 1001 has 3 encounters at Portland (648) - Cerner site
INSERT INTO EncMill.Encounter (EncounterSID, PatientSID, EncounterTypeCodeValueSID, EncounterType,
    AdmitStatusCodeValueSID, AdmitStatus, AdmitDateTime, DischargeDateTime, Sta3n)
VALUES
(5001, 1001, 28101, 'Inpatient', 26102, 'Discharged', '2024-09-15 08:00', '2024-09-20 14:30', 648),
(5002, 1001, 28102, 'Outpatient', 26102, 'Discharged', '2024-11-03 10:15', '2024-11-03 11:00', 648),
(5003, 1001, 28102, 'Outpatient', 26102, 'Discharged', '2024-12-01 09:30', '2024-12-01 10:15', 648);
```

### 6.3 Allergies - AllergyMill Schema

**Purpose**: Document allergies and adverse reactions at Cerner sites.

**6.3.1 AllergyMill.PersonAllergy**:
```sql
CREATE TABLE AllergyMill.PersonAllergy (
    AllergyInstanceSID      BIGINT          PRIMARY KEY,
    PatientSID              BIGINT          NOT NULL,     -- FK to VeteranMill.SPerson
    EncounterSID            BIGINT          NOT NULL,     -- FK to EncMill.Encounter (REQUIRED)

    -- Allergen Information
    SubstanceDisplay        VARCHAR(255)    NOT NULL,     -- e.g., "PENICILLIN VK 500MG"
    AllergenClassDisplay    VARCHAR(100),                 -- e.g., "PENICILLIN" (standardized)
    AllergenType            VARCHAR(50),                  -- DRUG, FOOD, ENVIRONMENTAL

    -- Severity (with denormalized display)
    SeverityCodeValueSID    BIGINT,                       -- FK to NDimMill.CodeValue (Set 4002)
    Severity                VARCHAR(50),                  -- Denormalized: "Severe"

    -- Status
    ActiveInd               BIT             DEFAULT 1,    -- Is allergy still active?

    -- Documentation
    Comments                TEXT,                         -- Free-text clinical notes
    EnteredDateTime         DATETIME2       NOT NULL,
    EnteredByStaffSID       BIGINT,                       -- FK to SStaff.SStaff (shared)

    -- Metadata
    Sta3n                   INT             NOT NULL,

    INDEX IX_Patient (PatientSID),
    INDEX IX_Encounter (EncounterSID),
    INDEX IX_AllergenType (AllergenType),
    INDEX IX_Active (ActiveInd)
);
```

**6.3.2 AllergyMill.AdverseReaction** (Bridge Table):
```sql
CREATE TABLE AllergyMill.AdverseReaction (
    AdverseReactionSID      BIGINT          PRIMARY KEY,
    AllergyInstanceSID      BIGINT          NOT NULL,     -- FK to PersonAllergy

    -- Reaction (with denormalized display)
    ReactionCodeValueSID    BIGINT          NOT NULL,     -- FK to NDimMill.CodeValue (Set 4003)
    Reaction                VARCHAR(100),                 -- Denormalized: "Hives"

    INDEX IX_AllergyInstance (AllergyInstanceSID)
);
```

**VistA ↔ Cerner Field Mapping**:

| CDWWork (VistA) | CDWWork2 (Cerner) | Notes |
|----------------|------------------|-------|
| `Allergy.PatientAllergy.PatientAllergySID` | `AllergyMill.PersonAllergy.AllergyInstanceSID` | Different column name |
| `Allergy.PatientAllergy.PatientSID` | `AllergyMill.PersonAllergy.PatientSID` | Direct mapping |
| `Dim.Allergen.AllergenName` | `AllergyMill.PersonAllergy.SubstanceDisplay` | VistA uses FK, Cerner stores text |
| `Dim.AllergySeverity.SeverityName` | `NDimMill.CodeValue (Set 4002) → Severity` | VistA uses Dim table, Cerner uses code set |
| N/A (optional in VistA) | `AllergyMill.PersonAllergy.EncounterSID` | **REQUIRED** in Cerner |
| `Allergy.PatientAllergyReaction` | `AllergyMill.AdverseReaction` | Both use bridge table pattern |

**Sample Data**:
```sql
-- Patient 1001 has penicillin allergy documented during Encounter 5001
INSERT INTO AllergyMill.PersonAllergy (AllergyInstanceSID, PatientSID, EncounterSID,
    SubstanceDisplay, AllergenClassDisplay, AllergenType, SeverityCodeValueSID, Severity,
    ActiveInd, Comments, EnteredDateTime, Sta3n)
VALUES
(1, 1001, 5001, 'PENICILLIN VK 500MG', 'PENICILLIN', 'DRUG', 400203, 'Severe', 1,
 'Patient developed anaphylaxis after first dose. EpiPen administered.',
 '2024-09-15 10:00', 648);

-- Reactions for this allergy
INSERT INTO AllergyMill.AdverseReaction (AdverseReactionSID, AllergyInstanceSID,
    ReactionCodeValueSID, Reaction)
VALUES
(1, 1, 400305, 'Anaphylaxis'),
(2, 1, 400301, 'Hives'),
(3, 1, 400304, 'Swelling');
```

### 6.4 Vitals - VitalMill.VitalResult

**Purpose**: Store vital sign measurements from Cerner sites.

**Schema**:
```sql
CREATE TABLE VitalMill.VitalResult (
    VitalResultSID          BIGINT          PRIMARY KEY,
    PatientSID              BIGINT          NOT NULL,     -- FK to VeteranMill.SPerson
    EncounterSID            BIGINT          NOT NULL,     -- FK to EncMill.Encounter (REQUIRED)

    -- Vital Type (with denormalized display)
    EventCodeValueSID       BIGINT          NOT NULL,     -- FK to NDimMill.CodeValue (Set 72)
    EventType               VARCHAR(50),                  -- Denormalized: "Systolic BP"

    -- Result Value
    ResultValue             VARCHAR(100),                 -- The measurement (e.g., "120", "98.6")
    ResultValueNumeric      DECIMAL(10,2),                -- Numeric version for calculations

    -- Units (with denormalized display)
    ResultUnitsCodeValueSID BIGINT,                       -- FK to NDimMill.CodeValue (Set 90)
    ResultUnits             VARCHAR(20),                  -- Denormalized: "mmHg"

    -- When/Where
    EventDateTime           DATETIME2       NOT NULL,
    LocationSID             INT,                          -- FK to Dim.Location (shared)
    LocationName            VARCHAR(100),                 -- Denormalized

    -- Who
    VerifiedPersonnelSID    BIGINT,                       -- FK to SStaff.SStaff (shared)

    -- Metadata
    Sta3n                   INT             NOT NULL,

    INDEX IX_Patient (PatientSID),
    INDEX IX_Encounter (EncounterSID),
    INDEX IX_EventType (EventCodeValueSID),
    INDEX IX_EventDateTime (EventDateTime)
);
```

**Key Design Points**:
- **Event-Based Model**: Each vital measurement is a discrete "event" (not aggregated like VistA's BP)
- **Split BP Values**: Systolic and Diastolic stored as separate rows (not columns like VistA)
- **Numeric Conversion**: Store both text (`ResultValue`) and numeric (`ResultValueNumeric`) for charting

**VistA ↔ Cerner Field Mapping**:

| CDWWork (VistA) | CDWWork2 (Cerner) | Notes |
|----------------|------------------|-------|
| `Vital.VitalSign.VitalSignSID` | `VitalMill.VitalResult.VitalResultSID` | Different column name |
| `Vital.VitalSign.VitalType` | `NDimMill.CodeValue (Set 72) → EventType` | VistA uses Dim.VitalType, Cerner uses code set |
| `Vital.VitalSign.VitalResultNumeric` | `VitalMill.VitalResult.ResultValueNumeric` | Direct mapping (concept) |
| `Vital.VitalSign.Units` | `NDimMill.CodeValue (Set 90) → ResultUnits` | VistA stores text, Cerner uses code set |
| `Vital.VitalSign.BPSystolic` / `BPDiastolic` | **Two rows** in VitalMill.VitalResult | VistA uses columns, Cerner uses separate event rows |
| N/A (optional) | `VitalMill.VitalResult.EncounterSID` | **REQUIRED** in Cerner |

**Sample Data** (Blood Pressure - Split into Two Rows):
```sql
-- Patient 1001 BP measurement during Encounter 5001: 135/88 mmHg
-- VistA would store this as ONE row with two columns (BPSystolic=135, BPDiastolic=88)
-- Cerner stores this as TWO rows (one for systolic, one for diastolic)

INSERT INTO VitalMill.VitalResult (VitalResultSID, PatientSID, EncounterSID,
    EventCodeValueSID, EventType, ResultValue, ResultValueNumeric,
    ResultUnitsCodeValueSID, ResultUnits, EventDateTime, Sta3n)
VALUES
-- Systolic BP
(1, 1001, 5001, 7201, 'Systolic BP', '135', 135.0, 9001, 'mmHg', '2024-09-15 08:30', 648),
-- Diastolic BP
(2, 1001, 5001, 7202, 'Diastolic BP', '88', 88.0, 9001, 'mmHg', '2024-09-15 08:30', 648);

-- Temperature
(3, 1001, 5001, 7203, 'Temperature', '98.6', 98.6, 9002, 'F', '2024-09-15 08:30', 648),
-- Pulse
(4, 1001, 5001, 7204, 'Pulse', '72', 72.0, 9004, 'bpm', '2024-09-15 08:30', 648);
```

### 6.5 Labs - LabMill.LabResult

**Purpose**: Store laboratory test results from Cerner sites.

**Schema**:
```sql
CREATE TABLE LabMill.LabResult (
    LabResultSID            BIGINT          PRIMARY KEY,
    PatientSID              BIGINT          NOT NULL,     -- FK to VeteranMill.SPerson
    EncounterSID            BIGINT          NOT NULL,     -- FK to EncMill.Encounter (REQUIRED)

    -- Test Identification
    LabTestCodeValueSID     BIGINT          NOT NULL,     -- FK to NDimMill.CodeValue (could use separate set)
    LabTestName             VARCHAR(100),                 -- Denormalized: "Glucose"
    LoincCode               VARCHAR(20),                  -- Standard LOINC code

    -- Result Value
    ResultValue             VARCHAR(255),                 -- The result (numeric or text)
    ResultValueNumeric      DECIMAL(18,6),                -- Numeric version (NULL for non-numeric)

    -- Reference Range
    NormalRangeLow          VARCHAR(50),
    NormalRangeHigh         VARCHAR(50),

    -- Abnormal Flag (with denormalized display)
    AbnormalFlagCodeValueSID BIGINT,                      -- FK to NDimMill.CodeValue (Set 6000)
    AbnormalFlag            VARCHAR(50),                  -- Denormalized: "High"

    -- Units
    ResultUnits             VARCHAR(50),

    -- When/Where
    ResultDateTime          DATETIME2       NOT NULL,
    CollectionDateTime      DATETIME2,
    SpecimenID              BIGINT,                       -- FK to specimen table (future)
    CollectionLocationSID   INT,                          -- FK to Dim.Location (shared)
    CollectionLocation      VARCHAR(100),                 -- Denormalized

    -- Metadata
    Sta3n                   INT             NOT NULL,

    INDEX IX_Patient (PatientSID),
    INDEX IX_Encounter (EncounterSID),
    INDEX IX_LabTest (LabTestCodeValueSID),
    INDEX IX_ResultDateTime (ResultDateTime)
);
```

**VistA ↔ Cerner Field Mapping**:

| CDWWork (VistA) | CDWWork2 (Cerner) | Notes |
|----------------|------------------|-------|
| `Chem.LabChem.LabChemSID` | `LabMill.LabResult.LabResultSID` | Different column name |
| `Dim.LabTest.LabTestName` | `LabMill.LabResult.LabTestName` | VistA uses FK to Dim, Cerner denormalizes |
| `Chem.LabChem.LabChemResultValue` | `LabMill.LabResult.ResultValue` | Direct mapping |
| `Chem.LabChem.ReferenceRangeLow/High` | `LabMill.LabResult.NormalRangeLow/High` | Column name differs |
| N/A (VistA uses text) | `NDimMill.CodeValue (Set 6000) → AbnormalFlag` | Cerner uses structured code set |
| N/A (optional) | `LabMill.LabResult.EncounterSID` | **REQUIRED** in Cerner |

**Sample Data**:
```sql
-- Patient 1001 Glucose lab during Encounter 5001
INSERT INTO LabMill.LabResult (LabResultSID, PatientSID, EncounterSID,
    LabTestName, LoincCode, ResultValue, ResultValueNumeric,
    NormalRangeLow, NormalRangeHigh, AbnormalFlagCodeValueSID, AbnormalFlag,
    ResultUnits, ResultDateTime, Sta3n)
VALUES
(1, 1001, 5001, 'Glucose', '2345-7', '145', 145.0,
 '70', '100', 600002, 'High', 'mg/dL', '2024-09-15 12:00', 648);
```

---

## 7. Patient Identity and Site Assignment

### 7.1 Shared Patient Identity Strategy

**Core Principle**: The same synthetic patient exists in **both** CDWWork and CDWWork2 with identical PatientSID and ICN values.

**Rationale**:
- Simulates real-world scenario: Veterans seek care at both VistA and Cerner sites
- Enables Silver layer to JOIN data from both sources on PatientSID
- Tests cross-source data aggregation and deduplication
- Mirrors VA's Master Patient Index (MPI) identity resolution

**Implementation**:

```sql
-- CDWWork (VistA) - Patient 1001
INSERT INTO SPatient.Spatient (PatientSID, PatientICN, PatientName, ...)
VALUES (1001, '1000000001V123456', 'SMITH,JOHN ALPHA', ...);

-- CDWWork2 (Cerner) - SAME Patient 1001
INSERT INTO VeteranMill.SPerson (PatientSID, PatientICN, PatientName, ...)
VALUES (1001, '1000000001V123456', 'SMITH,JOHN ALPHA', ...);
```

**Shared Patient Registry**:

| PatientSID | ICN | Patient Name | VistA Sites (Sta3n) | Cerner Sites (Sta3n) | Total Sites |
|-----------|-----|--------------|---------------------|---------------------|-------------|
| 1001 | 1000000001V123456 | SMITH,JOHN ALPHA | 508, 509, 200 | 648 | 4 |
| 1002 | 1000000002V234567 | DOE,JANE BRAVO | 508 | 648, 663 | 3 |
| 1003 | 1000000003V345678 | JOHNSON,ROBERT CHARLIE | 509, 200, 500 | 531 | 4 |
| 1004 | 1000000004V456789 | WILLIAMS,MARY DELTA | 630 | (none) | 1 |

**Key Points**:
- **Patient 1001**: Has data in CDWWork (3 VistA sites) AND CDWWork2 (1 Cerner site) - tests cross-source merge
- **Patient 1002**: Has data in CDWWork (1 VistA site) AND CDWWork2 (2 Cerner sites) - tests multi-Cerner aggregation
- **Patient 1003**: Has data in both databases - balanced distribution
- **Patient 1004**: Has data ONLY in CDWWork - tests single-source scenario

### 7.2 Site Assignment Strategy

**Designated Cerner Sites** (CDWWork2 only):
- **Sta3n 648** - Portland VA Medical Center (Oregon)
- **Sta3n 663** - Seattle/Puget Sound VA (Washington)
- **Sta3n 531** - Boise VA Medical Center (Idaho)

**Designated VistA Sites** (CDWWork only):
- **Sta3n 508** - Atlanta VA Medical Center (Georgia)
- **Sta3n 509** - Augusta VA Medical Center (Georgia)
- **Sta3n 516** - C.W. Bill Young VA Medical Center (Bay Pines, Florida)
- **Sta3n 552** - Dayton VA Medical Center (Ohio)
- **Sta3n 200** - Alexandria (used in Vista RPC Broker simulator)
- **Sta3n 500** - Anchorage (used in Vista RPC Broker simulator)
- **Sta3n 630** - Palo Alto (used in Vista RPC Broker simulator)

**Total Sites**: 7 VistA sites, 3 Cerner sites (10 sites total)

**Mutual Exclusivity**: A site's data exists in **either** CDWWork **or** CDWWork2, never both.

#### 7.2.1 Considerations for Site List Expansion

**Adding Sta3n 516 and 552 to VistA Sites:**

**Impacts** (All Positive):
- ✅ **More realistic simulation**: 7 VistA sites better represents the scale of VistA deployment (130+ real sites)
- ✅ **Better test coverage**: More sites enables testing multi-site data aggregation patterns
- ✅ **No architectural changes**: Site list is data-only (WHERE clause filters)
- ✅ **No schema changes**: Patient and clinical tables already support arbitrary Sta3n values
- ✅ **Scalable pattern**: Can easily add more sites in future (up to ~130 VistA sites theoretically)

**Implementation Changes Required** (Minor):
- ⚠️ Update ETL WHERE clauses: Add `516, 552` to site filters in Bronze extraction queries
- ⚠️ Update test assertions: Change expected site sets from `{508, 509, 200, 500, 630}` to `{508, 509, 516, 552, 200, 500, 630}`
- ⚠️ Optional mock data: If you populate data for these sites, add INSERT scripts (not required for initial implementation)

**Performance Implications**: None significant
- ETL queries use `WHERE Sta3n IN (...)` which is indexed
- Adding 2 sites to a 7-value IN clause has negligible performance impact
- If you populate data for these sites, ETL runtime scales linearly (acceptable)

**Recommendation**: ✅ **No negative impacts identified. Safe to add these sites.**

**Example - Patient 1001 Care Timeline**:
```
2020-2022: Treated at Atlanta VAMC (Sta3n 508) - VistA site
           → Data in CDWWork
           → 15 vitals, 3 allergies, 10 medications

2023-2024 (pre-migration): Treated at Portland VAMC (Sta3n 648) - Still on VistA
                           → Data in CDWWork (historical)
                           → 8 vitals, 0 new allergies, 5 medications

2024 (Sept - Go-Live): Portland migrates to Cerner
                       → New data in CDWWork2 (post-migration)
                       → 5 vitals, 1 allergy update, 3 medications

2024 (Dec - Current): Active patient at Portland (Cerner site)
                      → Latest data in CDWWork2
                      → Med-z1 UI shows COMBINED data from both sources
```

### 7.3 Historical Data Strategy

**Rule**: CDWWork2 contains **only post-migration data** for Cerner sites.

**Timeline Simulation**:
- **Portland (Sta3n 648)** - "Go-Live" date: 2024-09-01
  - Data before 2024-09-01 → CDWWork (VistA era)
  - Data on/after 2024-09-01 → CDWWork2 (Cerner era)

- **Seattle (Sta3n 663)** - "Go-Live" date: 2024-06-01
  - Data before 2024-06-01 → CDWWork
  - Data on/after 2024-06-01 → CDWWork2

- **Boise (Sta3n 531)** - "Go-Live" date: 2024-11-01
  - Data before 2024-11-01 → CDWWork
  - Data on/after 2024-11-01 → CDWWork2

**Implications**:
- Bronze ETL must extract from BOTH databases
- Silver ETL merges records with date-based filtering (no duplicates)
- PostgreSQL contains unified timeline with `data_source` attribution

**Example - Patient 1001 Vitals Distribution**:
```sql
-- CDWWork: 20 vitals from 2020-2024 (all VistA sites)
SELECT COUNT(*) FROM Vital.VitalSign WHERE PatientSID = 1001 AND Sta3n IN (508, 509);
-- Result: 20 vitals

-- CDWWork2: 5 vitals from Sept-Dec 2024 (Portland Cerner site only)
SELECT COUNT(*) FROM VitalMill.VitalResult WHERE PatientSID = 1001 AND Sta3n = 648;
-- Result: 5 vitals

-- PostgreSQL (merged): 25 total vitals with data_source column
SELECT COUNT(*), data_source FROM patient_vitals WHERE patient_key = '1000000001V123456'
GROUP BY data_source;
-- Result: 20 from 'CDWWork', 5 from 'CDWWork2'
```

---

## 8. ETL Architecture Changes

### 8.1 Dual-Source Bronze Extraction

**Current Pattern** (Single Source - CDWWork):
```python
# etl/bronze_vitals.py (existing)
def extract_vitals():
    """Extract vitals from CDWWork (VistA)."""
    conn_str = build_connection_string(CDWWORK_DB_CONFIG)
    df = pl.read_database(query, conn_str)
    save_to_minio(df, "bronze/cdwwork/vital_sign")
```

**Enhanced Pattern** (Dual Source - CDWWork + CDWWork2):
```python
# etl/bronze_vitals.py (ENHANCED)
def extract_vitals_cdwwork():
    """Extract vitals from CDWWork (VistA sites)."""
    conn_str = build_connection_string(CDWWORK_DB_CONFIG)

    query = """
    SELECT
        VitalSignSID,
        PatientSID,
        VitalType,
        BPSystolic,
        BPDiastolic,
        Temperature,
        VitalDateTime,
        Sta3n,
        'CDWWork' AS source_database  -- ✅ Add source attribution
    FROM Vital.VitalSign
    WHERE Sta3n IN (508, 509, 516, 552, 200, 500, 630)  -- VistA sites only
    """

    df = pl.read_database(query, conn_str)
    save_to_minio(df, "bronze/cdwwork/vital_sign")
    logger.info(f"Extracted {len(df)} vitals from CDWWork")


def extract_vitals_cdwwork2():
    """Extract vitals from CDWWork2 (Cerner sites)."""
    conn_str = build_connection_string(CDWWORK2_DB_CONFIG)  # New config

    query = """
    SELECT
        VitalResultSID,
        PatientSID,
        EncounterSID,
        EventType,             -- Denormalized vital type
        ResultValueNumeric,
        ResultUnits,
        EventDateTime,
        Sta3n,
        'CDWWork2' AS source_database  -- ✅ Add source attribution
    FROM VitalMill.VitalResult
    WHERE Sta3n IN (648, 663, 531)  -- Cerner sites only
    """

    df = pl.read_database(query, conn_str)
    save_to_minio(df, "bronze/cdwwork2/vital_result")
    logger.info(f"Extracted {len(df)} vitals from CDWWork2")


def main():
    """Orchestrate both extractions."""
    extract_vitals_cdwwork()   # VistA sites → bronze/cdwwork/
    extract_vitals_cdwwork2()  # Cerner sites → bronze/cdwwork2/
```

**Key Changes**:
- Separate functions for each source database
- Different output paths: `bronze/cdwwork/` vs. `bronze/cdwwork2/`
- Add `source_database` column in Bronze layer for lineage tracking
- Filter by Sta3n to enforce site exclusivity

### 8.2 Silver Layer Harmonization

**Purpose**: Merge VistA and Cerner vitals into unified schema with standardized column names.

**Challenge**: Different data models must be reconciled:
- VistA: BP stored as two columns (`BPSystolic`, `BPDiastolic`) in one row
- Cerner: BP stored as two separate rows (`EventType = 'Systolic BP'` and `'Diastolic BP'`)

**Silver ETL Pattern**:
```python
# etl/silver_vitals.py (ENHANCED)
import polars as pl

def harmonize_vista_vitals():
    """Transform VistA vitals to common schema."""
    df_vista = pl.read_parquet("bronze/cdwwork/vital_sign")

    # Unpivot BP columns into multiple rows (match Cerner format)
    df_systolic = df_vista.filter(pl.col("BPSystolic").is_not_null()).select([
        pl.col("VitalSignSID").alias("vital_id"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.lit("Systolic BP").alias("vital_type"),
        pl.col("BPSystolic").alias("result_value_numeric"),
        pl.lit("mmHg").alias("units"),
        pl.col("VitalDateTime").alias("vital_datetime"),
        pl.col("Sta3n").alias("sta3n"),
        pl.col("source_database"),
    ])

    df_diastolic = df_vista.filter(pl.col("BPDiastolic").is_not_null()).select([
        pl.col("VitalSignSID").alias("vital_id"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.lit("Diastolic BP").alias("vital_type"),
        pl.col("BPDiastolic").alias("result_value_numeric"),
        pl.lit("mmHg").alias("units"),
        pl.col("VitalDateTime").alias("vital_datetime"),
        pl.col("Sta3n").alias("sta3n"),
        pl.col("source_database"),
    ])

    # Similar unpivot for Temperature, Pulse, etc.
    # ...

    # Combine all vital types
    df_vista_harmonized = pl.concat([df_systolic, df_diastolic, ...])
    return df_vista_harmonized


def harmonize_cerner_vitals():
    """Transform Cerner vitals to common schema."""
    df_cerner = pl.read_parquet("bronze/cdwwork2/vital_result")

    # Cerner already in "one row per vital type" format
    df_cerner_harmonized = df_cerner.select([
        pl.col("VitalResultSID").alias("vital_id"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("EventType").alias("vital_type"),
        pl.col("ResultValueNumeric").alias("result_value_numeric"),
        pl.col("ResultUnits").alias("units"),
        pl.col("EventDateTime").alias("vital_datetime"),
        pl.col("Sta3n").alias("sta3n"),
        pl.col("source_database"),
    ])

    return df_cerner_harmonized


def merge_vitals():
    """Merge VistA and Cerner vitals into unified Silver layer."""
    df_vista = harmonize_vista_vitals()
    df_cerner = harmonize_cerner_vitals()

    # Combine both sources
    df_merged = pl.concat([df_vista, df_cerner])

    # Deduplication (if same vital exists in both sources - unlikely but possible)
    # Rule: Keep Cerner version if duplicate (newer data)
    df_merged = df_merged.sort(["source_database"], descending=True)  # CDWWork2 before CDWWork
    df_merged = df_merged.unique(subset=["patient_sid", "vital_type", "vital_datetime"], keep="first")

    # Save to Silver layer
    save_to_minio(df_merged, "silver/vitals")
    logger.info(f"Merged {len(df_merged)} vitals from both sources")
```

**Harmonization Rules**:
1. **Column Renaming**: Map source-specific columns to standard names
2. **Data Type Conversion**: Ensure consistent types (DATETIME2, DECIMAL, VARCHAR)
3. **Unit Standardization**: Convert all temps to Fahrenheit, all weights to pounds (or flag units)
4. **Null Handling**: Unified NULL representation
5. **Deduplication**: Prefer Cerner data if same event exists in both sources

### 8.3 Gold Layer Source Attribution

**Purpose**: Preserve data lineage for transparency and debugging.

**Pattern**:
```python
# etl/gold_vitals.py (ENHANCED)
def create_gold_vitals():
    """Create Gold vitals with patient ICN join and source attribution."""
    df_silver = pl.read_parquet("silver/vitals")
    df_patients = pl.read_parquet("gold/patients")  # Has patient_key (ICN)

    # Join with patient demographics to get ICN
    df_gold = df_silver.join(
        df_patients.select(["patient_sid", "patient_key"]),
        on="patient_sid",
        how="left"
    ).select([
        pl.col("patient_key"),           # ICN (e.g., "1000000001V123456")
        pl.col("vital_type"),
        pl.col("result_value_numeric"),
        pl.col("units"),
        pl.col("vital_datetime"),
        pl.col("sta3n"),
        pl.col("source_database"),       # ✅ Preserve source lineage
    ])

    # Sort by patient and datetime
    df_gold = df_gold.sort(["patient_key", "vital_datetime"], descending=[False, True])

    save_to_minio(df_gold, "gold/vitals")
```

**Gold Schema (Parquet)**:
```
patient_key           : STRING          # ICN
vital_type            : STRING          # "Systolic BP"
result_value_numeric  : DOUBLE          # 135.0
units                 : STRING          # "mmHg"
vital_datetime        : DATETIME        # 2024-09-15 08:30:00
sta3n                 : INT             # 648
source_database       : STRING          # "CDWWork2"  ✅ Lineage preserved
```

### 8.4 PostgreSQL Load with Source Tracking

**Schema Enhancement**:
```sql
-- db/ddl/create_patient_vitals_table.sql (ENHANCED)
CREATE TABLE patient_vitals (
    vital_id                SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,
    vital_type              VARCHAR(50),
    result_value_numeric    DECIMAL(10,2),
    units                   VARCHAR(20),
    vital_datetime          TIMESTAMP,
    sta3n                   INTEGER,
    data_source             VARCHAR(20),           -- ✅ NEW: 'CDWWork' or 'CDWWork2'
    location_id             INTEGER,
    location_name           VARCHAR(100),
    location_type           VARCHAR(50),

    INDEX idx_patient_key (patient_key),
    INDEX idx_vital_datetime (vital_datetime),
    INDEX idx_data_source (data_source)           -- ✅ NEW: Enable filtering by source
);
```

**Load Script**:
```python
# etl/load_vitals.py (ENHANCED)
def load_vitals_to_postgres():
    """Load Gold vitals into PostgreSQL with source attribution."""
    df = pl.read_parquet("gold/vitals")

    # Convert to pandas for SQLAlchemy
    df_pandas = df.to_pandas()

    # Insert into PostgreSQL
    engine = create_engine(POSTGRES_CONNECTION_STRING)
    df_pandas.to_sql('patient_vitals', engine, if_exists='replace', index=False)

    logger.info(f"Loaded {len(df)} vitals into PostgreSQL")

    # Log source distribution
    source_counts = df.group_by("source_database").count()
    logger.info(f"Source distribution: {source_counts}")
    # Example output: CDWWork: 20, CDWWork2: 5
```

### 8.5 Configuration Updates

**config.py** (Enhanced):
```python
# Existing CDWWork config
CDWWORK_DB_CONFIG = {
    "server": "localhost",
    "name": "CDWWork",
    "user": os.getenv("SQL_SERVER_USER"),
    "password": os.getenv("SQL_SERVER_PASSWORD"),
    "driver": "ODBC Driver 18 for SQL Server",
}

# ✅ NEW: CDWWork2 config
CDWWORK2_DB_CONFIG = {
    "server": "localhost",        # Same SQL Server instance
    "name": "CDWWork2",            # Different database
    "user": os.getenv("SQL_SERVER_USER"),
    "password": os.getenv("SQL_SERVER_PASSWORD"),
    "driver": "ODBC Driver 18 for SQL Server",
}
```

**.env** (Enhanced):
```bash
# Existing settings
SQL_SERVER_USER=sa
SQL_SERVER_PASSWORD=YourStrongPassword

# ✅ NEW: Optional CDWWork2-specific settings (if needed)
# CDWWORK2_ENABLED=true  # Feature flag to enable/disable CDWWork2 processing
```

---

## 9. Data Source Lineage Tracking

### 9.1 Purpose and Rationale

**User Requirement**: "med-z1 application should retain knowledge of whether data was sourced from CDWWork vs CDWWork2."

**Why Track Lineage?**:
1. **Transparency**: Clinicians can see which EHR system originated each record
2. **Debugging**: Developers can trace data quality issues to specific sources
3. **Auditing**: Track data provenance for compliance and troubleshooting
4. **Future Features**: Enable "Show only VistA data" or "Show only Cerner data" filters
5. **Data Quality Analysis**: Compare data completeness/accuracy across sources

### 9.2 Implementation Strategy

**Three-Tier Lineage Tracking**:

#### Tier 1: Bronze Layer
- Add `source_database` column during extraction
- Values: `"CDWWork"` or `"CDWWork2"`
- Purpose: Preserve origin for ETL debugging

#### Tier 2: Silver/Gold Layers
- Propagate `source_database` column through all transformations
- Purpose: Enable source-based analysis in data lake

#### Tier 3: PostgreSQL Serving Database
- Add `data_source` column to all clinical tables
- Values: `"CDWWork"` or `"CDWWork2"`
- Purpose: Enable UI display and optional filtering

### 9.3 PostgreSQL Schema Pattern

**Standard Pattern for All Clinical Tables**:
```sql
CREATE TABLE patient_<domain> (
    <domain>_id             SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,
    -- ... domain-specific columns ...
    sta3n                   INTEGER,
    data_source             VARCHAR(20),           -- ✅ REQUIRED: 'CDWWork' or 'CDWWork2'
    encounter_id            INTEGER,               -- ✅ OPTIONAL: NULL for VistA, populated for Cerner (Q4 Decision)

    INDEX idx_patient_key (patient_key),
    INDEX idx_data_source (data_source),          -- ✅ Enable source filtering
    INDEX idx_encounter_id (encounter_id)         -- ✅ Enable encounter-based queries (optional)
);
```

**Note on encounter_id** (per Q4 decision):
- **VistA data**: `encounter_id = NULL` (most clinical records not linked to encounters in VistA)
- **Cerner data**: `encounter_id = <EncounterSID>` (always populated, required in Cerner model)
- **Future enhancement**: Can backfill VistA encounter_id from `Inpat.Inpatient` for inpatient records
- **UI handling**: Display encounter context when available, gracefully handle NULL values

**Examples**:

**Demographics**:
```sql
CREATE TABLE patient_demographics (
    patient_key         VARCHAR(50) PRIMARY KEY,
    patient_name        VARCHAR(255),
    date_of_birth       DATE,
    gender              VARCHAR(20),
    -- ... other columns ...
    data_source         VARCHAR(20),  -- ✅ Which database provided demographics
);
```

**Vitals**:
```sql
CREATE TABLE patient_vitals (
    vital_id            SERIAL PRIMARY KEY,
    patient_key         VARCHAR(50) NOT NULL,
    vital_type          VARCHAR(50),
    result_value_numeric DECIMAL(10,2),
    vital_datetime      TIMESTAMP,
    sta3n               INTEGER,
    data_source         VARCHAR(20),  -- ✅ Which database provided this vital
    encounter_id        INTEGER,      -- ✅ Optional: NULL for VistA, populated for Cerner (Q4 Decision)
);
```

**Allergies**:
```sql
CREATE TABLE patient_allergies (
    allergy_id          SERIAL PRIMARY KEY,
    patient_key         VARCHAR(50) NOT NULL,
    allergen_name       VARCHAR(255),
    severity            VARCHAR(50),
    entered_datetime    TIMESTAMP,
    sta3n               INTEGER,
    data_source         VARCHAR(20),  -- ✅ Which database provided this allergy
    encounter_id        INTEGER,      -- ✅ Optional: NULL for VistA, populated for Cerner (Q4 Decision)
);
```

**Labs**:
```sql
CREATE TABLE patient_labs (
    lab_id              SERIAL PRIMARY KEY,
    patient_key         VARCHAR(50) NOT NULL,
    test_name           VARCHAR(100),
    result_value        VARCHAR(255),
    result_datetime     TIMESTAMP,
    sta3n               INTEGER,
    data_source         VARCHAR(20),  -- ✅ Which database provided this lab
    encounter_id        INTEGER,      -- ✅ Optional: NULL for VistA, populated for Cerner (Q4 Decision)
);
```

### 9.4 UI Display Patterns

**Option 1: Tooltip/Hover (Recommended)**:
```html
<!-- Vitals Page - Full Table -->
<tr>
    <td>Systolic BP</td>
    <td>135 mmHg</td>
    <td>2024-09-15 08:30</td>
    <td>
        <span class="badge badge-cerner" title="Source: CDWWork2 (Cerner)">
            Portland VAMC
        </span>
    </td>
</tr>
```

**Option 2: Badge/Icon**:
```html
<!-- Allergies Page - Card View -->
<div class="allergy-card">
    <h4>
        PENICILLIN
        <span class="badge badge-cerner">Cerner</span>
    </h4>
    <p>Severity: Severe</p>
    <p class="text-muted">Documented at Portland VAMC (648)</p>
</div>
```

**Option 3: Details/Metadata Section**:
```html
<!-- Details Modal/Expandable -->
<div class="metadata">
    <dl>
        <dt>Data Source</dt>
        <dd>CDWWork2 (Oracle Health/Cerner)</dd>

        <dt>Facility</dt>
        <dd>Portland VA Medical Center (Sta3n 648)</dd>

        <dt>Documented</dt>
        <dd>2024-09-15 10:00 AM</dd>
    </dl>
</div>
```

**Option 4: Optional Filter** (Future Enhancement):
```html
<!-- Filter Controls -->
<div class="filters">
    <label>
        <input type="checkbox" name="source" value="CDWWork" checked>
        VistA Sites
    </label>
    <label>
        <input type="checkbox" name="source" value="CDWWork2" checked>
        Cerner Sites
    </label>
</div>
```

### 9.5 Query Layer Pattern

**Database Query Function** (app/db/vitals.py):
```python
def get_all_vitals(icn: str) -> List[Dict[str, Any]]:
    """Get all vitals for patient with source attribution."""
    query = text("""
        SELECT
            vital_id,
            patient_key,
            vital_type,
            result_value_numeric,
            units,
            vital_datetime,
            sta3n,
            data_source,          -- ✅ Include in SELECT
            location_name
        FROM patient_vitals
        WHERE patient_key = :icn
        ORDER BY vital_datetime DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn})
        vitals = []
        for row in result:
            vitals.append({
                "vital_id": row[0],
                "patient_key": row[1],
                "vital_type": row[2],
                "result_value_numeric": row[3],
                "units": row[4],
                "vital_datetime": row[5],
                "sta3n": row[6],
                "data_source": row[7],      # ✅ Return to caller
                "location_name": row[8],
            })
        return vitals
```

**Template Usage** (app/templates/patient_vitals.html):
```html
{% for vital in vitals %}
<tr>
    <td>{{ vital.vital_type }}</td>
    <td>{{ vital.result_value_numeric }} {{ vital.units }}</td>
    <td>{{ vital.vital_datetime }}</td>
    <td>
        {{ vital.location_name }}
        <!-- ✅ Show source badge -->
        {% if vital.data_source == 'CDWWork2' %}
        <span class="badge badge-cerner" title="Oracle Health (Cerner)">C</span>
        {% else %}
        <span class="badge badge-vista" title="VistA">V</span>
        {% endif %}
    </td>
</tr>
{% endfor %}
```

### 9.6 Best Practices Summary

**DO**:
- ✅ Add `data_source` column to ALL clinical tables (vitals, allergies, labs, meds, encounters)
- ✅ Add `encounter_id` column to ALL clinical tables (NULL for VistA, populated for Cerner - Q4 Decision)
- ✅ Populate during PostgreSQL load from Gold Parquet
- ✅ Index `data_source` column for efficient filtering
- ✅ Index `encounter_id` column for optional encounter-based queries
- ✅ Include in all SELECT queries (even if not immediately displayed)
- ✅ Display in UI tooltips/badges for transparency
- ✅ Document source values in data dictionary ("CDWWork" vs "CDWWork2")
- ✅ Handle NULL encounter_id gracefully in UI (don't display if NULL)

**DON'T**:
- ❌ Use cryptic codes (use full names: "CDWWork", not "C1" or "1")
- ❌ Make source display prominent/distracting (subtle tooltip is better)
- ❌ Filter out source column in query layer (preserve for future features)
- ❌ Forget to add to new clinical domains as they're implemented
- ❌ Require encounter_id to be non-NULL (it's optional for VistA data)

**Future Enhancements**:
- Add `data_source_timestamp` (when data was extracted from source)
- Add `etl_run_id` (which ETL batch loaded this record)
- Add `source_record_id` (original SID from source database)
- Backfill VistA `encounter_id` from `Inpat.Inpatient` for inpatient clinical records

---

## 10. Implementation Roadmap

### 10.1 Phase Breakdown

**Phase 1: Foundation** (2-3 weeks)
- Create CDWWork2 database and schemas
- Implement `NDimMill.CodeValue` with essential code sets (8-10 sets)
- Create `VeteranMill.SPerson` (demographics)
- Create `EncMill.Encounter` (core encounter table)
- Populate 3-4 shared patients
- Populate 10-15 encounters per patient at Cerner sites
- Test cross-database patient identity (same PatientSID/ICN)

**Phase 2: First Clinical Domain - Vitals** (2-3 weeks)
- Create `VitalMill.VitalResult` schema
- Populate 5-10 vitals per encounter (BP split into separate rows)
- Enhance Bronze ETL: `extract_vitals_cdwwork2()`
- Enhance Silver ETL: Harmonize VistA + Cerner vitals
- Enhance Gold ETL: Add `data_source` column
- Update PostgreSQL schema: Add `data_source` column
- Update query layer: Include source in SELECT
- Update UI: Display source badge/tooltip
- Test merged vitals display for Patient 1001

**Phase 3: Second Clinical Domain - Allergies** (2-3 weeks)
- Create `AllergyMill.PersonAllergy` and `AllergyMill.AdverseReaction` schemas
- Populate 2-5 allergies per patient at Cerner sites
- Enhance Bronze/Silver/Gold ETL (same pattern as Vitals)
- Update PostgreSQL schema
- Update query layer and UI
- Test allergy merge and deduplication

**Phase 4: Third Clinical Domain - Labs** (2-3 weeks)
- Create `LabMill.LabResult` schema
- Populate 10-20 lab results per patient
- Enhance ETL pipeline (same pattern)
- Update PostgreSQL, query layer, UI
- Test lab result merge

**Phase 5: Fourth Clinical Domain - Demographics** (1-2 weeks)
- Enhance `VeteranMill.SPerson` with complete fields
- Update Bronze/Silver/Gold ETL for demographics
- Update `patient_demographics` table with `data_source`
- Test demographics merge (prefer Cerner if present, VistA otherwise)

**Phase 6: Testing and Validation** (1-2 weeks)
- Create comprehensive cross-source test scenarios
- Performance testing (ETL runtime with dual sources)
- UI testing (verify source badges display correctly)
- Documentation updates

### 10.2 Detailed Task Breakdown (Phase 1)

**Week 1: Database Foundation**

**Day 1-2: Database and Schema Creation**
- Create `mock/sql-server/cdwwork2/create/db_database.sql`
- Create `mock/sql-server/cdwwork2/create/db_schemas.sql` (5 schemas)
- Create master orchestration script `_master.sql`
- Test database creation (drop/recreate)

**Day 3-4: Code Set System**
- Create `mock/sql-server/cdwwork2/create/NDimMill.CodeValue.sql`
- Create `mock/sql-server/cdwwork2/insert/NDimMill.CodeValue.sql` (8-10 code sets)
- Test code set queries (validate CodeValueSetID filtering)
- Document code set reference (Appendix)

**Day 5: Demographics Table**
- Create `mock/sql-server/cdwwork2/create/VeteranMill.SPerson.sql`
- Document VistA ↔ Cerner field mapping
- Test schema creation

**Week 2: Patient and Encounter Data**

**Day 1-2: Patient Population**
- Create `mock/sql-server/cdwwork2/insert/VeteranMill.SPerson.sql`
- Insert 3-4 patients (same PatientSID as CDWWork)
- Verify cross-database identity (JOIN test)
- Document shared patient registry

**Day 3: Encounter Schema**
- Create `mock/sql-server/cdwwork2/create/EncMill.Encounter.sql`
- Document encounter types and status codes
- Test schema creation

**Day 4-5: Encounter Population**
- Create `mock/sql-server/cdwwork2/insert/EncMill.Encounter.sql`
- Insert 10-15 encounters per patient
- Distribute across 3 Cerner sites (648, 663, 531)
- Mix encounter types (Inpatient, Outpatient, Emergency)
- Verify EncounterSID uniqueness

**Week 3: Testing and Documentation**

**Day 1-2: Cross-Database Testing**
- Write SQL test queries (JOIN CDWWork + CDWWork2)
- Verify patient identity resolution
- Test site exclusivity (no data overlap)
- Validate encounter linkage

**Day 3-4: Configuration Updates**
- Add `CDWWORK2_DB_CONFIG` to `config.py`
- Update `.env` with any new settings
- Test database connections from Python

**Day 5: Documentation**
- Update `docs/cdwwork2-design.md` with Phase 1 completion status
- Update `mock/README.md` with CDWWork2 instructions
- Create developer quickstart guide

### 10.3 Success Metrics

**Phase 1 Complete When**:
- ✅ CDWWork2 database created with 5 schemas
- ✅ `NDimMill.CodeValue` populated with 100+ rows (8-10 code sets)
- ✅ 3-4 patients in `VeteranMill.SPerson` with same PatientSID as CDWWork
- ✅ 40-60 encounters in `EncMill.Encounter` (10-15 per patient)
- ✅ SQL JOIN between `CDWWork.SPatient.Spatient` and `CDWWork2.VeteranMill.SPerson` returns shared patients
- ✅ Configuration updated and tested
- ✅ Documentation complete

**Phase 2 Complete When** (Vitals):
- ✅ `VitalMill.VitalResult` populated with 50+ vitals across all patients
- ✅ Bronze ETL extracts from both databases to separate paths
- ✅ Silver ETL merges and harmonizes VistA + Cerner vitals
- ✅ Gold layer includes `data_source` column
- ✅ PostgreSQL `patient_vitals` table has `data_source` column
- ✅ UI displays vitals from both sources with source badge/tooltip
- ✅ Patient 1001 shows 25 total vitals (20 VistA + 5 Cerner)

**Full Implementation Complete When**:
- ✅ All 5 clinical domains implemented (Demographics, Vitals, Allergies, Labs, Encounters)
- ✅ ETL pipeline processes both sources with <20% runtime increase
- ✅ All PostgreSQL tables have `data_source` column
- ✅ UI displays source attribution in all clinical views
- ✅ Cross-source test scenarios pass (single-source, multi-source, duplicates)
- ✅ Documentation complete with VistA ↔ Cerner field mappings

### 10.4 Dependencies and Risks

**Dependencies**:
- Existing CDWWork database must remain stable (no breaking changes)
- MinIO Bronze/Silver/Gold bucket structure must support dual sources
- PostgreSQL serving database must have capacity for additional columns
- UI templates must accommodate source badges without layout disruption

**Risks and Mitigations**:

| Risk | Impact | Mitigation |
|------|--------|-----------|
| ETL runtime doubles with dual sources | High | Optimize Bronze queries, add parallel extraction, benchmark early |
| Schema divergence (VistA vs Cerner) complicates Silver harmonization | High | Create detailed field mappings upfront, test with real data patterns |
| Deduplication logic fails (duplicate records in UI) | Medium | Implement robust canonical key matching, add integration tests |
| `data_source` column forgotten in new domains | Medium | Add to checklist, code review requirement, automated schema validation |
| Developer confusion about routing patterns | Low | Clear documentation, naming conventions, examples in each domain |

---

## 11. Testing Strategy

### 11.1 Unit Testing

**Bronze ETL Tests**:
```python
# tests/etl/test_bronze_vitals_cdwwork2.py
def test_extract_vitals_cdwwork2():
    """Test Bronze extraction from CDWWork2."""
    extract_vitals_cdwwork2()

    # Verify Parquet file created
    assert minio_client.file_exists("bronze/cdwwork2/vital_result")

    # Verify data structure
    df = pl.read_parquet("bronze/cdwwork2/vital_result")
    assert "VitalResultSID" in df.columns
    assert "EventType" in df.columns
    assert "source_database" in df.columns

    # Verify source attribution
    assert df.select("source_database").unique()[0] == "CDWWork2"

    # Verify Cerner sites only
    assert set(df.select("Sta3n").unique()) <= {648, 663, 531}
```

**Silver ETL Tests**:
```python
# tests/etl/test_silver_vitals_dual_source.py
def test_merge_vitals_from_both_sources():
    """Test Silver merge of VistA + Cerner vitals."""
    merge_vitals()

    df = pl.read_parquet("silver/vitals")

    # Verify both sources present
    sources = set(df.select("source_database").unique())
    assert sources == {"CDWWork", "CDWWork2"}

    # Verify no duplicates
    duplicates = df.group_by(["patient_sid", "vital_type", "vital_datetime"]).count()
    assert duplicates.filter(pl.col("count") > 1).is_empty()

    # Verify schema standardization
    assert df.select("vital_type").is_not_null().all()
    assert df.select("result_value_numeric").dtype == pl.Float64
```

### 11.2 Integration Testing

**Cross-Database Patient Identity**:
```python
# tests/integration/test_cross_database_identity.py
def test_shared_patient_identity():
    """Verify same patient exists in both databases with same PatientSID/ICN."""
    # Query CDWWork
    df_vista = query_cdwwork("SELECT PatientSID, PatientICN FROM SPatient.Spatient")

    # Query CDWWork2
    df_cerner = query_cdwwork2("SELECT PatientSID, PatientICN FROM VeteranMill.SPerson")

    # Find shared patients
    shared = df_vista.join(df_cerner, on=["PatientSID", "PatientICN"], how="inner")

    # Verify at least 3 patients shared
    assert len(shared) >= 3

    # Verify ICN format
    assert all(shared.select("PatientICN").str.contains(r"\d{10}V\d{6}"))
```

**Site Exclusivity**:
```python
# tests/integration/test_site_exclusivity.py
def test_no_site_overlap():
    """Verify sites exist in only one database, not both."""
    vista_sites = {508, 509, 516, 552, 200, 500, 630}
    cerner_sites = {648, 663, 531}

    # Verify no intersection
    assert vista_sites.isdisjoint(cerner_sites)

    # Verify CDWWork contains only VistA sites
    df_vista_vitals = query_cdwwork("SELECT DISTINCT Sta3n FROM Vital.VitalSign")
    assert set(df_vista_vitals["Sta3n"]) <= vista_sites

    # Verify CDWWork2 contains only Cerner sites
    df_cerner_vitals = query_cdwwork2("SELECT DISTINCT Sta3n FROM VitalMill.VitalResult")
    assert set(df_cerner_vitals["Sta3n"]) <= cerner_sites
```

### 11.3 End-to-End Testing

**Scenario 1: Patient with Data in Both Sources**:
```python
# tests/e2e/test_dual_source_patient.py
def test_patient_1001_vitals_from_both_sources():
    """Patient 1001 has vitals at both VistA and Cerner sites."""
    # Run full ETL pipeline
    run_etl_pipeline("vitals")

    # Query PostgreSQL
    vitals = query_postgres("""
        SELECT vital_type, vital_datetime, sta3n, data_source
        FROM patient_vitals
        WHERE patient_key = '1000000001V123456'
        ORDER BY vital_datetime DESC
    """)

    # Verify mixed sources
    sources = set(vitals["data_source"])
    assert sources == {"CDWWork", "CDWWork2"}

    # Verify count (20 VistA + 5 Cerner = 25 total)
    assert len(vitals) == 25
    assert vitals[vitals["data_source"] == "CDWWork"].shape[0] == 20
    assert vitals[vitals["data_source"] == "CDWWork2"].shape[0] == 5

    # Verify chronological order (newest first)
    assert vitals.iloc[0]["data_source"] == "CDWWork2"  # Most recent from Cerner
```

**Scenario 2: Patient with Data in One Source Only**:
```python
def test_patient_1004_vitals_vista_only():
    """Patient 1004 has vitals only at VistA sites."""
    run_etl_pipeline("vitals")

    vitals = query_postgres("""
        SELECT data_source FROM patient_vitals
        WHERE patient_key = '1000000004V456789'
    """)

    # Verify single source
    assert set(vitals["data_source"]) == {"CDWWork"}
```

### 11.4 UI Testing

**Manual Test Plan**:
1. Load Vitals page for Patient 1001
2. Verify table shows 25 vitals (20 + 5)
3. Verify source badges display correctly ("V" for VistA, "C" for Cerner)
4. Hover over Cerner badge, verify tooltip shows "Oracle Health (Cerner)"
5. Verify Portland VAMC (648) vitals show Cerner badge
6. Verify Atlanta VAMC (508) vitals show VistA badge
7. Test sorting by date (mixed sources should interleave correctly)

**Automated UI Test** (Future):
```python
# tests/ui/test_vitals_source_display.py
def test_vitals_page_shows_source_badges(selenium):
    """Verify source badges display in Vitals UI."""
    driver = selenium
    driver.get("http://localhost:8000/patient/1000000001V123456/vitals")

    # Find all source badges
    vista_badges = driver.find_elements(By.CSS_SELECTOR, ".badge-vista")
    cerner_badges = driver.find_elements(By.CSS_SELECTOR, ".badge-cerner")

    # Verify both badge types present
    assert len(vista_badges) > 0
    assert len(cerner_badges) > 0

    # Verify tooltip content
    cerner_badge = cerner_badges[0]
    assert cerner_badge.get_attribute("title") == "Oracle Health (Cerner)"
```

### 11.5 Performance Testing

**ETL Runtime Benchmarks**:
```python
# tests/performance/test_etl_runtime.py
import time

def test_dual_source_etl_performance():
    """Verify ETL runtime increases by <20% with dual sources."""
    # Baseline: Single source (CDWWork only)
    start = time.time()
    extract_vitals_cdwwork()
    baseline_time = time.time() - start

    # Dual source: CDWWork + CDWWork2
    start = time.time()
    extract_vitals_cdwwork()
    extract_vitals_cdwwork2()
    dual_source_time = time.time() - start

    # Calculate overhead
    overhead_pct = (dual_source_time - baseline_time) / baseline_time * 100

    # Verify <20% overhead
    assert overhead_pct < 20, f"ETL overhead {overhead_pct:.1f}% exceeds 20% threshold"
```

**PostgreSQL Query Performance**:
```python
def test_query_performance_with_source_column():
    """Verify adding data_source column doesn't degrade query performance."""
    # Query without source filter
    start = time.time()
    vitals = query_postgres("SELECT * FROM patient_vitals WHERE patient_key = '1000000001V123456'")
    baseline_time = time.time() - start

    # Query with source filter
    start = time.time()
    vitals = query_postgres("""
        SELECT * FROM patient_vitals
        WHERE patient_key = '1000000001V123456' AND data_source = 'CDWWork2'
    """)
    filtered_time = time.time() - start

    # Verify query times are comparable (<50ms difference)
    assert abs(filtered_time - baseline_time) < 0.05
```

---

## 12. Open Questions and Future Considerations

### 12.1 Open Questions

**Q1: Should demographics prefer Cerner or VistA data when both exist?**
- **Context**: Patient 1001 has demographics in both CDWWork and CDWWork2. Which should be canonical?
- **Options**:
  - A) Always prefer Cerner (newer system)
  - B) Always prefer VistA (more complete historical data)
  - C) Merge fields (use Cerner for some, VistA for others)
- **Recommendation**: Option A - Prefer Cerner if present (assume more up-to-date)
- **Decision**: ✅ **APPROVED - Option A** (2025-12-17)
  - **Implementation**: Silver/Gold demographics ETL will prioritize CDWWork2 data when patient exists in both databases
  - **Logic**: `COALESCE(cerner.field, vista.field)` pattern in SQL/Polars
  - **Rationale**: Cerner is newer system, likely to have most current contact info, demographic updates

**Q2: Should UI show "Go-Live" date for Cerner sites?**
- **Context**: Helpful context to explain why data before X date is VistA, after is Cerner
- **Example**: "Portland VAMC (648) transitioned to Oracle Health on 2024-09-01"
- **Recommendation**: Add to Demographics page "Site Info" section
- **Decision**: ✅ **APPROVED - Add to Demographics page** (2025-12-17)
  - **Implementation**: Create `site_go_live_dates` reference table or config mapping
  - **UI Location**: Demographics page, "Treatment Sites" or "Site Information" section
  - **Display Format**: "Portland VAMC (648) - Oracle Health site (Go-Live: Sep 2024)"
  - **Benefits**: Helps users understand data source transitions, educational value

**Q3: Should source badges be user-configurable (show/hide)?**
- **Context**: Some users may not care about source, find badges distracting
- **Options**:
  - A) Always show (transparency)
  - B) Show by default, user can hide via settings
  - C) Hide by default, user can show via settings
- **Recommendation**: Option A for Phase 1 (always show), Option B for Phase 2 (user preference)
- **Decision**: ✅ **APPROVED - Option A for Phase 1** (2025-12-17)
  - **Phase 1**: Always show source badges (transparency, data quality validation)
  - **Phase 2**: Add user preference setting to hide badges (deferred, no timeline yet)
  - **Rationale**: Early phases need visibility for debugging, validation; can add flexibility later

**Q4: How to handle encounters in VistA data (CDWWork)?**
- **Context**: VistA has `Inpat.Inpatient` table (inpatient encounters), but many clinical records don't link to encounters
- **Options**:
  - A) Leave NULL for VistA clinical records without encounters
  - B) Create synthetic encounters for VistA data to match Cerner pattern
  - C) Add optional `encounter_id` column (NULL for VistA, populated for Cerner)
- **Recommendation**: Option C - Optional encounter linkage in PostgreSQL
- **Decision**: ✅ **APPROVED - Option C** (2025-12-17)
  - **Implementation**: Add `encounter_id INTEGER NULL` column to all clinical tables in PostgreSQL
  - **VistA Data**: `encounter_id = NULL` for most records (encounter linkage is optional in VistA)
  - **Cerner Data**: `encounter_id = <EncounterSID>` (always populated, required in Cerner)
  - **Future Enhancement**: Optionally backfill VistA encounter_id from `Inpat.Inpatient` table for inpatient data
  - **UI**: Encounter information displayed when available, gracefully handle NULL

### 12.2 Future Enhancements

**Enhancement 1: CDWWork3 Integration**
- **Description**: Add third source database (CDWWork3 "converged" model)
- **Timeline**: Phase 7+ (after all CDWWork2 domains complete)
- **Effort**: 4-6 weeks
- **Dependencies**: Need to understand real CDWWork3 schema (research required)

**Enhancement 2: Site Migration Timeline Visualization**
- **Description**: UI page showing which sites use VistA vs Cerner, with go-live dates
- **Timeline**: Phase 8+
- **Effort**: 1-2 weeks
- **Value**: Educational for users, helps explain data source distribution

**Enhancement 3: Source-Based Filtering**
- **Description**: UI filter to show "VistA data only" or "Cerner data only"
- **Timeline**: Phase 9+
- **Effort**: 1-2 weeks (backend already supports via `data_source` column)
- **Value**: Useful for data quality analysis, troubleshooting

**Enhancement 4: Data Quality Comparison Reports**
- **Description**: Analytics showing completeness/accuracy differences between sources
- **Example**: "Cerner vitals have 95% location data, VistA vitals have 60%"
- **Timeline**: Phase 10+ (AI/ML phase)
- **Effort**: 3-4 weeks
- **Value**: Identify data quality gaps, inform EHR training

**Enhancement 5: Encounter-Based Views**
- **Description**: UI view organized by encounters instead of domain
- **Example**: "Show all data collected during Encounter 5001 (2024-09-15 admission)"
- **Timeline**: Phase 11+
- **Effort**: 4-6 weeks (new UI paradigm)
- **Value**: Matches Cerner's encounter-centric workflow

### 12.3 Long-Term Considerations

**Real Production Deployment**:
- Will need access to actual CDWWork2 schema documentation
- May need additional schemas beyond "Mill" suffixes (e.g., `Doc`, `Order`, `Med`)
- Code sets will expand to hundreds (need scalable Code Set management)
- Performance tuning for multi-source queries at scale (millions of records)
- HIPAA compliance for source attribution (ensure lineage doesn't leak PHI)

**Cerner API Integration** (Future):
- Real Cerner systems have APIs (HL7 FHIR, Cerner Millennium APIs)
- May want to simulate API access pattern in addition to CDW batch extracts
- Could add `data_source = 'CernerAPI'` for real-time data vs. CDW batch data

**Multi-Tenant Considerations**:
- If med-z1 deployed to multiple VA regions, may need region-specific CDWWork2 instances
- Site assignment logic may need to be configuration-driven (not hardcoded)

---

## 13. Appendices

### 13.1 VistA ↔ Cerner Field Mapping Reference

**Demographics**:

| Domain | CDWWork (VistA) | CDWWork2 (Cerner) | Mapping Notes |
|--------|----------------|------------------|---------------|
| Demographics | `SPatient.Spatient.PatientSID` | `VeteranMill.SPerson.PatientSID` | Direct mapping (shared key) |
| Demographics | `SPatient.Spatient.PatientICN` | `VeteranMill.SPerson.PatientICN` | Direct mapping (shared key) |
| Demographics | `SPatient.Spatient.PatientName` | `VeteranMill.SPerson.PatientName` | Direct mapping |
| Demographics | `SPatient.Spatient.DOB` | `VeteranMill.SPerson.DateOfBirth` | Column name differs |
| Demographics | `SPatient.Spatient.Gender` (text) | `NDimMill.CodeValue (Set 48)` → `Gender` | VistA text, Cerner code set |
| Demographics | `SPatient.Spatient.MaritalStatus` (text) | `NDimMill.CodeValue (Set 38)` → `MaritalStatus` | VistA text, Cerner code set |

**Allergies**:

| Domain | CDWWork (VistA) | CDWWork2 (Cerner) | Mapping Notes |
|--------|----------------|------------------|---------------|
| Allergies | `Allergy.PatientAllergy.PatientAllergySID` | `AllergyMill.PersonAllergy.AllergyInstanceSID` | Column name differs |
| Allergies | `Dim.Allergen.AllergenName` | `AllergyMill.PersonAllergy.SubstanceDisplay` | VistA FK, Cerner text |
| Allergies | `Dim.AllergySeverity.SeverityName` | `NDimMill.CodeValue (Set 4002)` → `Severity` | VistA Dim table, Cerner code set |
| Allergies | `Allergy.PatientAllergyReaction` | `AllergyMill.AdverseReaction` | Both use bridge table |
| Allergies | N/A (optional) | `AllergyMill.PersonAllergy.EncounterSID` | **REQUIRED** in Cerner |

**Vitals**:

| Domain | CDWWork (VistA) | CDWWork2 (Cerner) | Mapping Notes |
|--------|----------------|------------------|---------------|
| Vitals | `Vital.VitalSign.VitalSignSID` | `VitalMill.VitalResult.VitalResultSID` | Column name differs |
| Vitals | `Dim.VitalType.VitalTypeName` | `NDimMill.CodeValue (Set 72)` → `EventType` | VistA Dim table, Cerner code set |
| Vitals | `Vital.VitalSign.BPSystolic` (column) | `VitalMill.VitalResult` (row with EventType='Systolic BP') | VistA column, Cerner row |
| Vitals | `Vital.VitalSign.BPDiastolic` (column) | `VitalMill.VitalResult` (row with EventType='Diastolic BP') | VistA column, Cerner row |
| Vitals | `Vital.VitalSign.Units` (text) | `NDimMill.CodeValue (Set 90)` → `ResultUnits` | VistA text, Cerner code set |
| Vitals | N/A (optional) | `VitalMill.VitalResult.EncounterSID` | **REQUIRED** in Cerner |

**Labs**:

| Domain | CDWWork (VistA) | CDWWork2 (Cerner) | Mapping Notes |
|--------|----------------|------------------|---------------|
| Labs | `Chem.LabChem.LabChemSID` | `LabMill.LabResult.LabResultSID` | Column name differs |
| Labs | `Dim.LabTest.LabTestName` | `LabMill.LabResult.LabTestName` | VistA FK, Cerner denormalized |
| Labs | `Chem.LabChem.LabChemResultValue` | `LabMill.LabResult.ResultValue` | Direct mapping |
| Labs | `Chem.LabChem.ReferenceRangeLow` | `LabMill.LabResult.NormalRangeLow` | Column name differs |
| Labs | N/A (text) | `NDimMill.CodeValue (Set 6000)` → `AbnormalFlag` | VistA text, Cerner code set |
| Labs | N/A (optional) | `LabMill.LabResult.EncounterSID` | **REQUIRED** in Cerner |

### 13.2 Code Set Reference

**Essential Code Sets for Initial Implementation**:

| CodeValueSetID | Category | Row Count | Status | Notes |
|---------------|----------|-----------|--------|-------|
| 27 | Ethnicity | 3 | ✅ Required | Hispanic/Not Hispanic/Unknown |
| 38 | Marital Status | 5 | ✅ Required | Married/Divorced/Single/Widowed/Unknown |
| 48 | Gender | 3 | ✅ Required | Male/Female/Unknown |
| 72 | Vital Event Types | 9 | ✅ Required | BP, Temp, Pulse, Resp, O2, Ht, Wt, Pain |
| 90 | Result Units | 12 | ✅ Required | mmHg, F, C, bpm, %, lb, kg, mg/dL, etc. |
| 261 | Admit Status | 4 | ✅ Required | Active/Discharged/Left AMA/Transferred |
| 281 | Encounter Type | 4 | ✅ Required | Inpatient/Outpatient/Emergency/Telehealth |
| 4002 | Allergy Severity | 3 | ✅ Required | Mild/Moderate/Severe |
| 4003 | Allergy Reactions | 10 | ✅ Required | Hives, Rash, Anaphylaxis, Nausea, etc. |
| 6000 | Abnormal Flag | 6 | ✅ Required | Normal/High/Critical High/Low/Critical Low |

**Future Code Sets** (Phase 2+):
- **Set 100**: Race categories
- **Set 200**: Lab test categories
- **Set 300**: Medication routes
- **Set 400**: Medication frequencies
- **Set 500**: Diagnosis codes (ICD-10 linkage)

### 13.3 Sample SQL Queries

**Query 1: Find Shared Patients**:
```sql
-- Patients in both CDWWork and CDWWork2
SELECT
    v.PatientSID,
    v.PatientICN,
    v.PatientName AS VistaName,
    c.PatientName AS CernerName
FROM CDWWork.SPatient.Spatient v
INNER JOIN CDWWork2.VeteranMill.SPerson c
    ON v.PatientSID = c.PatientSID
    AND v.PatientICN = c.PatientICN
ORDER BY v.PatientSID;
```

**Query 2: Count Vitals by Source**:
```sql
-- Count vitals from VistA sites
SELECT COUNT(*) AS VistaVitals
FROM CDWWork.Vital.VitalSign
WHERE Sta3n IN (508, 509, 200, 500, 630);

-- Count vitals from Cerner sites
SELECT COUNT(*) AS CernerVitals
FROM CDWWork2.VitalMill.VitalResult
WHERE Sta3n IN (648, 663, 531);
```

**Query 3: Resolve Code Set Value**:
```sql
-- Get marital status display text for a patient
SELECT
    p.PatientName,
    cv.Display AS MaritalStatus
FROM CDWWork2.VeteranMill.SPerson p
LEFT JOIN CDWWork2.NDimMill.CodeValue cv
    ON p.MaritalStatusCodeValueSID = cv.CodeValueSID
WHERE p.PatientSID = 1001;
```

**Query 4: Patient Timeline (Cross-Source)**:
```sql
-- Combine vitals from both sources for Patient 1001
SELECT
    'CDWWork' AS Source,
    VitalType,
    VitalResultNumeric AS Value,
    Units,
    VitalDateTime,
    Sta3n
FROM CDWWork.Vital.VitalSign
WHERE PatientSID = 1001

UNION ALL

SELECT
    'CDWWork2' AS Source,
    EventType AS VitalType,
    ResultValueNumeric AS Value,
    ResultUnits AS Units,
    EventDateTime AS VitalDateTime,
    Sta3n
FROM CDWWork2.VitalMill.VitalResult
WHERE PatientSID = 1001

ORDER BY VitalDateTime DESC;
```

### 13.4 Directory Structure Summary

```
med-z1/
├── mock/
│   └── sql-server/
│       ├── cdwwork/                 (existing - VistA)
│       │   ├── create/
│       │   └── insert/
│       └── cdwwork2/                (NEW - Cerner)
│           ├── create/
│           │   ├── db_database.sql
│           │   ├── db_schemas.sql
│           │   ├── NDimMill.CodeValue.sql
│           │   ├── VeteranMill.SPerson.sql
│           │   ├── EncMill.Encounter.sql
│           │   ├── AllergyMill.PersonAllergy.sql
│           │   ├── AllergyMill.AdverseReaction.sql
│           │   ├── VitalMill.VitalResult.sql
│           │   ├── LabMill.LabResult.sql
│           │   └── _master.sql
│           └── insert/
│               ├── NDimMill.CodeValue.sql
│               ├── VeteranMill.SPerson.sql
│               ├── EncMill.Encounter.sql
│               ├── AllergyMill.PersonAllergy.sql
│               ├── VitalMill.VitalResult.sql
│               ├── LabMill.LabResult.sql
│               └── _master.sql
│
├── etl/
│   ├── bronze_vitals.py             (ENHANCED - dual source)
│   ├── bronze_allergies.py          (ENHANCED)
│   ├── bronze_labs.py               (ENHANCED)
│   ├── silver_vitals.py             (ENHANCED - harmonization)
│   ├── silver_allergies.py          (ENHANCED)
│   ├── silver_labs.py               (ENHANCED)
│   ├── gold_vitals.py               (ENHANCED - source attribution)
│   ├── gold_allergies.py            (ENHANCED)
│   ├── gold_labs.py                 (ENHANCED)
│   ├── load_vitals.py               (ENHANCED - data_source column)
│   └── ...
│
├── db/
│   └── ddl/
│       ├── create_patient_vitals_table.sql    (ENHANCED - data_source column)
│       ├── create_patient_allergies_table.sql (ENHANCED)
│       ├── create_patient_labs_table.sql      (ENHANCED)
│       └── ...
│
├── app/
│   ├── db/
│   │   ├── vitals.py                (ENHANCED - SELECT data_source)
│   │   ├── allergies.py             (ENHANCED)
│   │   └── ...
│   └── templates/
│       ├── patient_vitals.html      (ENHANCED - source badges)
│       ├── patient_allergies.html   (ENHANCED)
│       └── ...
│
├── config.py                        (ENHANCED - CDWWORK2_DB_CONFIG)
├── .env                             (ENHANCED - optional settings)
│
└── docs/
    ├── cdwwork2-design.md           (THIS DOCUMENT)
    ├── architecture.md              (UPDATE - add dual-source patterns)
    └── ...
```

### 13.5 Related Documentation

**Primary References**:
- `docs/cdwwork2-database-research.md` - Initial research findings (AI agent report)
- `docs/architecture.md` - System architecture and routing decisions
- `docs/med-z1-plan.md` - Overall product roadmap
- `mock/README.md` - Mock data subsystem overview (UPDATE with CDWWork2)
- `CLAUDE.md` - Project guidance (UPDATE with CDWWork2 patterns)

**Design Documents to Update**:
- `docs/vitals-design.md` - Add CDWWork2 source notes
- `docs/allergies-design.md` - Add CDWWork2 source notes
- `docs/demographics-design.md` - Add CDWWork2 source notes
- Future domain design docs - Include CDWWork2 from day one

**ETL Documentation**:
- `etl/README.md` - ETL pipeline overview (UPDATE with dual-source pattern)

**Database Documentation**:
- `db/README.md` - Serving database overview (UPDATE with data_source column pattern)

---

## Document Change Log

**Version 1.1** (2025-12-17):
- Added Sta3n 516 and 552 to VistA sites list (Section 7.2)
- Added Section 7.2.1: Considerations for Site List Expansion
- Updated ETL code examples with new site filters (Section 8.1)
- Updated test code with new site sets (Section 11.2)
- Resolved all 4 Open Questions in Section 12.1:
  - **Q1**: Approved Option A - Prefer Cerner demographics when both exist
  - **Q2**: Approved - Add Go-Live dates to Demographics page
  - **Q3**: Approved Option A for Phase 1 - Always show source badges
  - **Q4**: Approved Option C - Add optional `encounter_id` column to all clinical tables
- Updated PostgreSQL schema patterns with `encounter_id` column (Section 9.3)
- Updated Best Practices Summary with encounter_id guidance (Section 9.6)
- Total VistA sites: 7 (was 5), Total sites: 10 (was 8)

**Version 1.0** (2025-12-17):
- Initial design document created
- All sections complete (13 total)
- Comprehensive coverage of CDWWork2 mock database design
- Detailed implementation roadmap (6 phases)
- Data source lineage tracking strategy
- VistA ↔ Cerner field mapping reference
- Ready for user review and implementation kickoff

---

**End of Document**
