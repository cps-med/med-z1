# Clinical Notes Domain - Design Specification

**Document Version:** v2.3 (Phase 1 Complete)
**Date:** January 2, 2026
**Last Updated:** January 2, 2026
**Status:** Phase 1 Implementation Complete ✅ | Phase 2 Not Started
**Implementation Status:** Phase 1 (VistA/CDWWork) - COMPLETE (Days 1-7) ✅
**Current Scope:** All Note Classes from Both VistA (CDWWork) and Cerner (CDWWork2) Sources

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
12. [Appendices](#12-appendices)

---

## 1. Overview

### 1.1 Purpose

The **Clinical Notes domain** provides comprehensive access to patient clinical documentation, enabling clinicians to:
- View recent clinical notes at a glance (dashboard widget)
- Review complete note history with filtering by note type
- Read full narrative clinical documentation (SOAP notes, consultation notes, discharge summaries, imaging reports)
- Support clinical decision-making with comprehensive documentation access
- Enable AI-powered insights using narrative clinical data (Phase 2)

Clinical notes represent the narrative "why" and "how" of patient care, making them the highest-value data source for AI-assisted clinical insights, care gap analysis, and patient story summarization.

In the context of clinical notes, SOAP is an acronym for a standard documentation format used by healthcare providers to structure patient progress notes. It stands for:

- S — Subjective: The patient's reported symptoms, complaints, and history (e.g., "Patient reports chest pain...").
- O — Objective: Measurable data gathered by the clinician, such as vital signs, physical exam findings, and laboratory results.
- A — Assessment: The clinician's diagnosis, impression, or status of the patient's condition (e.g., "Hypertension - Well controlled").
- P — Plan: The treatment strategy, including medication changes, ordered tests, patient education, and follow-up instructions.

### 1.2 Scope

**Architecture:** Unified Design, Phased Implementation
- **Design Scope:** Both VistA (CDWWork) and Cerner (CDWWork2) data sources
- **Phase 1 Implementation:** VistA/CDWWork (8 days)
- **Phase 2 Implementation:** Cerner/CDWWork2 (3-4 days)

**In Scope - Phase 1 (VistA/CDWWork):**

**Mock CDW Database Schema - CDWWork (VistA):**
- **Dimension table:** `Dim.TIUDocumentDefinition` (note type definitions and classifications)
- **Fact table:** `TIU.TIUDocument_8925` (note metadata)
- **Text table:** `TIU.TIUDocumentText` (note content)

**In Scope - Phase 2 (Cerner/CDWWork2):**

**Mock CDW Database Schema - CDWWork2 (Cerner):**
- **Dimension table:** `Dim.ClinicalEventCode` (event type definitions, equivalent to TIUDocumentDefinition)
- **Fact table:** `Clinical.ClinicalEvent` (clinical event metadata, equivalent to TIUDocument_8925)
- **Text table:** `Clinical.ClinicalEventBlob` (note content, equivalent to TIUDocumentText)

**ETL Pipeline (Both Phases):** Bronze → Silver → Gold → PostgreSQL
- Bronze: Separate extraction for VistA and Cerner
- Silver: Harmonization and merging of both sources
- Gold: Unified patient-centric aggregation
- PostgreSQL: Source-agnostic serving table

**Dashboard Widget (2x1 size - active implementation):**
- Shows 2-3 most recent clinical notes
- Note type badges (Progress Note, Consult, Discharge Summary, Imaging)
- First 100-150 characters of note text (preview)
- Date, author, and facility (condensed layout)
- "View All Notes" link to full page
- **Note:** A 2x2 Enhanced Detail design was also created but archived in favor of more compact dashboard (see Section 1.4)

**Full Clinical Notes Page:**
- Comprehensive note list with filtering:
  - Note class dropdown (All, Progress Notes, Consults, Discharge Summaries, Imaging)
  - Date range selector (30 days, 90 days default, 6 months, 1 year, all)
  - Author filter (dropdown of providers)
- Note display:
  - Expandable rows (click to read full note text)
  - Note metadata: Date, Type, Author, Facility, Status
  - Full narrative text with preserved formatting
- Pagination (10 notes per page default, options: 10/20/50)
- Sorting by date (most recent first default)

**All Note Classes (Unified Table Approach):**
- **Progress Notes** (General Medicine, Cardiology, etc.)
- **Consults** (Specialty consultation notes)
- **Discharge Summaries** (Inpatient discharge documentation)
- **Imaging Reports** (Radiology, CT, MRI reports)

**Data Volume:**
- **Phase 1 (VistA):** 100-150 realistic clinical notes across 36 test patients
- **Phase 2 (Cerner):** 30-50 additional notes (total 130-200 notes)
- **Patient Distribution:** Most patients have notes from one system; 3-4 patients have notes from both (simulating transferred care)

**AI-Ready Schema Elements:**
- Vector embeddings column (for future RAG implementation)
- AI-generated summary column (for future use)
- Key entities JSONB column (for future NER extraction)

**Read-only functionality**

**Out of Scope for Phase 1:**
- Clinical note authoring/editing
- Electronic signature workflow
- Addendum/amendment functionality
- Note templates and macros
- Copy-forward functionality
- Voice dictation integration
- CDA/CCD XML rendering (treat as text notes)
- Full-text search across note content (defer to Phase 2)
- AI-powered summarization (defer to Phase 2)
- Vista RPC Broker overlay for T-0 notes (defer to Phase 2)
- Advanced note actions (print, export to PDF)
- Note versioning and audit trail
- Co-signature workflows
- DoD clinical notes (CHCS/AHLTA)

### 1.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Dual-Source Architecture** | Unified Design, Phased Implementation | Design PostgreSQL schema for both sources now (avoids migration pain); implement VistA first, add Cerner later without schema changes |
| **Unified vs Separate Tables** | Unified `clinical_notes` table | All note types are "Documents" differentiated by class; avoids technical debt of separate tables |
| **Widget Size** | 2x1 (wide, single row) | Balances dashboard density with note preview usefulness; shows 2-3 recent notes with condensed metadata; users can click through for details. A 2x2 design was evaluated but deemed too large for dashboard overview purpose (see Section 1.4) |
| **Routing Pattern** | Pattern B (dedicated router) | Complex domain with full page view, filtering, expandable content; warrants dedicated router |
| **CDW Schema** | TIU (Text Integration Utilities) | Matches VA CDW structure; authentic replication of VistA File #8925 |
| **Note Classes in Phase 1** | All 4 classes (Progress, Consult, Discharge, Imaging) | Unified table makes this feasible; provides richer dataset for future AI insights |
| **Test Data Volume** | 100-150 notes | Sufficient to test pagination, filtering, multiple note types per patient |
| **Note Content Realism** | Realistic SOAP narratives (200-500 words) | Essential for future AI insights; worth upfront effort to generate authentic clinical text |
| **Pagination Threshold** | 10 notes per page | Notes are text-heavy; fewer per page improves readability |
| **AI Schema Elements** | Include in Phase 1 schema, defer population | Avoids future migration; adds minimal complexity now |
| **VistA Overlay** | Document pattern, defer implementation | Consistent with other domains; implement after core UI working |
| **CDA/CCD Handling** | Treat as regular note types | No special XML rendering needed; CDA imports stored as text |
| **Full-Text Search** | Defer to Phase 2 | Pairs well with AI summarization; basic filtering sufficient for Phase 1 |
| **Source System Visibility** | Show in note detail metadata only | Clinicians care about content, not source; include for lineage but not prominent |
| **Cerner Facilities** | Distinct Sta3n values (600s range) | Differentiates Cerner sites from VistA sites; reflects real VA Cerner rollout patterns |
| **Bronze Extraction** | Separate Bronze files, merge in Silver | Keeps Bronze source-specific and simple; Silver handles harmonization clearly |
| **Patient Distribution** | Mixed: most in one system, 3-4 in both | Simulates real VA where most veterans stay in one system, few transfer between VistA/Cerner facilities |

### 1.4 Dashboard Widget Design Alternatives

Two dashboard widget designs were created and evaluated for Clinical Notes:

#### **Option 1: 2x1 Compact (Active Implementation)**

**Layout:** 2 columns wide × 1 row tall (standard widget height ~275px)

**Features:**
- Shows 2-3 most recent clinical notes
- Condensed metadata (date + author on same line)
- Shorter text previews (2-line clamp, ~100 characters)
- Summary pills showing note distribution by class
- Compact note item cards with essential information only

**Pros:**
- ✅ Better dashboard density - doesn't dominate the screen
- ✅ Faster visual scanning - less overwhelming
- ✅ Appropriate for dashboard "glance" purpose
- ✅ Consistent with other domain widget patterns (Medications is 2x1)
- ✅ Encourages users to click through to full page for details

**Cons:**
- ❌ Less detail visible per note
- ❌ Users must click to see full note metadata
- ❌ Shorter text previews may not provide enough context

**Use Case:** Quick dashboard overview to see recent activity and note types

---

#### **Option 2: 2x2 Enhanced Detail (Archived)**

**Layout:** 2 columns wide × 2 rows tall (double height ~551px)

**Features:**
- Shows 3-4 most recent clinical notes
- Full metadata display (date, author, facility on separate lines)
- Extended text previews (3-line clamp, ~150-200 characters)
- Summary pills showing note distribution by class
- Enhanced note item cards with comprehensive information

**Pros:**
- ✅ More context visible without clicking
- ✅ Richer metadata (author, facility, days since note)
- ✅ Longer text previews provide better clinical context
- ✅ Fewer clicks needed to understand recent activity

**Cons:**
- ❌ Takes significant dashboard real estate (2×2 grid cells)
- ❌ May overwhelm users on initial dashboard view
- ❌ Inconsistent with dashboard "summary" philosophy
- ❌ No other domain uses 2x2 widget size (except possibly future problems list)

**Use Case:** Could be revived as a user preference setting in future, or as specialized "clinical notes dashboard" view

---

**Decision:** Implement **Option 1 (2x1 Compact)** as the active design.

**Rationale:**
- Dashboard should provide quick overview, not detailed reading
- Users who want to read notes will navigate to full Clinical Notes page
- Maintains visual balance with other dashboard widgets
- Follows principle: "Dashboard = awareness; Full page = detailed review"
- 2x2 size felt too prominent for a single domain among 12+ domains

**Future Consideration:**
The 2x2 Enhanced Detail design could be offered as a user preference setting in a future phase, allowing power users or specialists who frequently review notes to opt for the larger, more detailed widget.

---

## 2. Objectives and Success Criteria

### 2.1 Data Pipeline Objectives

**Phase 1 (VistA):**
- [ ] **Bronze Layer**: Extract raw note data from `CDWWork.TIU.TIUDocument_8925` with joins to `TIU.TIUDocumentText` and `Dim.TIUDocumentDefinition`
- [ ] **Silver Layer**: Clean, standardize, resolve patient identity (ICN/PatientKey), classify note types
- [ ] **Gold Layer**: Create patient-centric, query-optimized Parquet files with note text
- [ ] **PostgreSQL**: Load notes into source-agnostic `patient_clinical_notes` table with <2 second query performance for 90-day range

**Phase 2 (Cerner):**
- [ ] **Bronze Layer**: Extract raw note data from `CDWWork2.Clinical.ClinicalEvent` with joins to `Clinical.ClinicalEventBlob` and `Dim.ClinicalEventCode`
- [ ] **Silver Layer**: Harmonize Cerner data to match VistA structure, merge with existing Silver data
- [ ] **Gold Layer**: Integrate Cerner notes into existing patient-centric aggregations
- [ ] **PostgreSQL**: Load Cerner notes into same `patient_clinical_notes` table (no schema changes required)

### 2.2 UI Objectives

- [ ] **Dashboard Widget (2x1)**: Display 2-3 most recent notes with type badges and text previews (compact layout)
- [ ] **Full Page View**: Comprehensive note list with:
  - Note class filtering (Progress Notes, Consults, Discharge Summaries, Imaging)
  - Date range filtering (30d, 90d default, 6mo, 1yr, all)
  - Author filtering (dropdown of providers)
  - Expandable rows to read full note text
  - Pagination (10 notes per page)
  - Sorting by date (most recent first)

### 2.3 Success Criteria

- [ ] Widget loads in <2 seconds for 95% of patients
- [ ] Full page view loads in <3 seconds with 90 days of notes
- [ ] Expandable note text displays correctly with preserved formatting
- [ ] Correctly classifies and filters notes by type (Progress, Consult, Discharge, Imaging)
- [ ] All 100-150 VistA test notes display correctly (Phase 1)
- [ ] All 30-50 Cerner test notes display correctly and merge seamlessly with VistA notes (Phase 2)
- [ ] Source system correctly tracked in database but not prominent in UI
- [ ] Patients with notes from both systems show unified timeline
- [ ] Pagination works correctly with 10/20/50 notes per page options
- [ ] Author filter shows only providers who have authored notes for the patient
- [ ] Data pipeline runs end-to-end without errors for both sources
- [ ] Note text is realistic and clinically appropriate for future AI use

---

## 3. Prerequisites

### 3.1 Completed Work

**Required Foundations:**
- ✅ Bronze ETL framework (Polars-based extraction)
- ✅ Silver ETL framework (identity resolution, harmonization)
- ✅ Gold ETL framework (patient-centric transformations)
- ✅ PostgreSQL serving database setup
- ✅ FastAPI application with HTMX/Jinja2
- ✅ Dashboard widget system (1x1, 2x1, 3x1 widgets implemented)
- ✅ Pattern B routing examples (Vitals, Encounters, Labs domains)
- ✅ Expandable row patterns (can reference from other domains or create new)

### 3.2 Environment Setup

**SQL Server (Mock CDW):**
- Container: `sqlserver2019` running SQL Server 2019
- **Database: `CDWWork`** (Phase 1)
  - Schema: `TIU` (Text Integration Utilities)
  - Schema: `Dim` (for TIUDocumentDefinition dimension)
  - New tables: `Dim.TIUDocumentDefinition`, `TIU.TIUDocument_8925`, `TIU.TIUDocumentText`
- **Database: `CDWWork2`** (Phase 2)
  - Schema: `Clinical` (for ClinicalEvent fact tables)
  - Schema: `Dim` (for ClinicalEventCode dimension)
  - New tables: `Dim.ClinicalEventCode`, `Clinical.ClinicalEvent`, `Clinical.ClinicalEventBlob`

**PostgreSQL (Serving Database):**
- Container: `postgres16` running PostgreSQL 16
- Database: `medz1`
- New table: `patient_clinical_notes`
- pgvector extension (for future AI embeddings)

**MinIO (Data Lake):**
- Bucket: `med-z1`
- Paths: `bronze/clinical_notes/`, `silver/clinical_notes/`, `gold/clinical_notes/`

---

## 4. Data Architecture

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

---

### 4.1 Source System - CDWWork TIU Schema

**VistA Source:** Text Integration Utilities (TIU) File #8925, Document Definition File #8925.1

The VA CDW TIU schema is a direct extraction from VistA's clinical documentation system. It uses a three-table design separating metadata, text content, and note type definitions.

#### 4.1.1 Dim.TIUDocumentDefinition (Note Type Definitions)

Replicates VistA File #8925.1 (TIU DOCUMENT DEFINITION). Contains note type metadata and classification hierarchy.

**DDL Script:** `mock/sql-server/cdwwork/create/Dim.TIUDocumentDefinition.sql`

```sql
USE CDWWork;
GO

-- Create Dim schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Dim')
BEGIN
    EXEC('CREATE SCHEMA Dim');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Dim.TIUDocumentDefinition', 'U') IS NOT NULL
    DROP TABLE [Dim].[TIUDocumentDefinition];
GO

-- Create TIUDocumentDefinition dimension table
CREATE TABLE [Dim].[TIUDocumentDefinition] (
    -- Primary key
    [DocumentDefinitionSID] INT IDENTITY(1,1) PRIMARY KEY,

    -- Note type identification
    [TIUDocumentTitle] VARCHAR(200) NOT NULL,       -- Local title (e.g., "GEN MED PROGRESS NOTE")
    [DocumentClass] VARCHAR(100),                   -- High-level class: 'Progress Notes', 'Consults', 'Discharge Summaries', 'Imaging'
    [VHAEnterpriseStandardTitle] VARCHAR(200),      -- Standardized VA title (e.g., "Physician Progress Note")

    -- Status
    [InactiveFlag] CHAR(1) DEFAULT 'N',             -- 'Y' if retired, 'N' if active

    -- Metadata
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),
    [ModifiedDate] DATETIME2(0) DEFAULT GETDATE()
);
GO

-- Create indexes
SET QUOTED_IDENTIFIER ON;
GO

CREATE NONCLUSTERED INDEX [IX_TIUDocumentDefinition_DocumentClass]
    ON [Dim].[TIUDocumentDefinition] ([DocumentClass])
    WHERE [DocumentClass] IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX [IX_TIUDocumentDefinition_Title]
    ON [Dim].[TIUDocumentDefinition] ([TIUDocumentTitle]);
GO

CREATE NONCLUSTERED INDEX [IX_TIUDocumentDefinition_StandardTitle]
    ON [Dim].[TIUDocumentDefinition] ([VHAEnterpriseStandardTitle])
    WHERE [VHAEnterpriseStandardTitle] IS NOT NULL;
GO
```

**Key Fields:**
- `DocumentDefinitionSID`: Surrogate primary key
- `TIUDocumentTitle`: Local site-specific title (varies by VA facility)
- `DocumentClass`: High-level classification for UI filtering
  - `'Progress Notes'`
  - `'Consults'`
  - `'Discharge Summaries'`
  - `'Imaging'`
- `VHAEnterpriseStandardTitle`: Standardized title across VA enterprise
- `InactiveFlag`: Whether this note type is still in use

#### 4.1.2 TIU.TIUDocument_8925 (Note Metadata - Fact Table)

Replicates VistA File #8925 (TIU DOCUMENT). Contains note metadata without the text content for performance.

**DDL Script:** `mock/sql-server/cdwwork/create/TIU.TIUDocument_8925.sql`

```sql
USE CDWWork;
GO

-- Create TIU schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'TIU')
BEGIN
    EXEC('CREATE SCHEMA TIU');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('TIU.TIUDocument_8925', 'U') IS NOT NULL
    DROP TABLE [TIU].[TIUDocument_8925];
GO

-- Create TIUDocument_8925 fact table
CREATE TABLE [TIU].[TIUDocument_8925] (
    -- Primary key
    [TIUDocumentSID] BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Station and patient
    [Sta3n] SMALLINT NOT NULL,                      -- Station Number (e.g., 508, 516, 552)
    [TIUDocumentIEN] VARCHAR(50) NOT NULL,          -- VistA internal entry number (File #8925)
    [PatientSID] BIGINT NOT NULL,                   -- FK to SPatient.SPatient

    -- Note type
    [DocumentDefinitionSID] INT NOT NULL,           -- FK to Dim.TIUDocumentDefinition

    -- Visit/Encounter linkage
    [VisitSID] BIGINT NULL,                         -- FK to Encounter (Inpatient or Outpatient)

    -- Temporal data
    [ReferenceDateTime] DATETIME2(3) NOT NULL,      -- Clinical date (when note applies to)
    [EntryDateTime] DATETIME2(3) NOT NULL,          -- When note was created/dictated

    -- Status and workflow
    [Status] VARCHAR(50) DEFAULT 'COMPLETED',       -- 'COMPLETED', 'UNSIGNED', 'RETRACTED', 'AMENDED'

    -- Authorship
    [AuthorSID] BIGINT NULL,                        -- FK to SStaff.SStaff (primary author)
    [CosignerSID] BIGINT NULL,                      -- FK to SStaff.SStaff (attending/supervisor)

    -- Metadata
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),
    [ModifiedDate] DATETIME2(0) DEFAULT GETDATE(),

    -- Foreign key constraints
    CONSTRAINT FK_TIUDocument_Definition FOREIGN KEY ([DocumentDefinitionSID])
        REFERENCES [Dim].[TIUDocumentDefinition] ([DocumentDefinitionSID])
);
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

-- Index on PatientSID for patient-centric queries
CREATE NONCLUSTERED INDEX [IX_TIUDocument_PatientSID]
    ON [TIU].[TIUDocument_8925] ([PatientSID]);
GO

-- Composite index for patient notes sorted by date
CREATE NONCLUSTERED INDEX [IX_TIUDocument_PatientSID_ReferenceDateTime]
    ON [TIU].[TIUDocument_8925] ([PatientSID], [ReferenceDateTime] DESC);
GO

-- Index on ReferenceDateTime for date range queries
CREATE NONCLUSTERED INDEX [IX_TIUDocument_ReferenceDateTime]
    ON [TIU].[TIUDocument_8925] ([ReferenceDateTime] DESC);
GO

-- Index on Sta3n for facility queries
CREATE NONCLUSTERED INDEX [IX_TIUDocument_Sta3n]
    ON [TIU].[TIUDocument_8925] ([Sta3n]);
GO

-- Index on Status for filtering
CREATE NONCLUSTERED INDEX [IX_TIUDocument_Status]
    ON [TIU].[TIUDocument_8925] ([Status])
    WHERE [Status] IS NOT NULL;
GO

-- Index on AuthorSID for author filtering
CREATE NONCLUSTERED INDEX [IX_TIUDocument_AuthorSID]
    ON [TIU].[TIUDocument_8925] ([AuthorSID])
    WHERE [AuthorSID] IS NOT NULL;
GO
```

**Key Fields:**
- `TIUDocumentSID`: Surrogate primary key
- `PatientSID`: Links to patient
- `DocumentDefinitionSID`: Links to note type definition
- `ReferenceDateTime`: **Primary timestamp** - when the note applies clinically
- `EntryDateTime`: When the note was authored/typed
- `Status`: Workflow state ('COMPLETED', 'UNSIGNED', 'RETRACTED', 'AMENDED')
- `AuthorSID`: Primary author (links to SStaff.SStaff)
- `CosignerSID`: Attending/supervisor (for resident notes)
- `VisitSID`: Links to encounter (inpatient or outpatient)

#### 4.1.3 TIU.TIUDocumentText (Note Content)

Stores the actual clinical narrative text. Separated from metadata table for performance (text is heavy, not always needed).

**DDL Script:** `mock/sql-server/cdwwork/create/TIU.TIUDocumentText.sql`

```sql
USE CDWWork;
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('TIU.TIUDocumentText', 'U') IS NOT NULL
    DROP TABLE [TIU].[TIUDocumentText];
GO

-- Create TIUDocumentText table
CREATE TABLE [TIU].[TIUDocumentText] (
    -- Foreign key to TIUDocument_8925
    [TIUDocumentSID] BIGINT NOT NULL,

    -- Note content
    [DocumentText] VARCHAR(MAX),                    -- Full clinical narrative

    -- Optional checksum for change detection
    [Checksum] VARCHAR(100) NULL,

    -- Primary key and foreign key constraint
    CONSTRAINT PK_TIUDocumentText PRIMARY KEY ([TIUDocumentSID]),
    CONSTRAINT FK_TIUDocumentText_Fact FOREIGN KEY ([TIUDocumentSID])
        REFERENCES [TIU].[TIUDocument_8925] ([TIUDocumentSID])
);
GO
```

**Key Fields:**
- `TIUDocumentSID`: Foreign key to TIUDocument_8925 (one-to-one relationship)
- `DocumentText`: Full note text (VARCHAR(MAX) supports up to 2GB of text)
- `Checksum`: Optional hash for detecting text changes

#### 4.1.4 Source System - CDWWork2 Clinical Schema (Cerner/Oracle Health)

**Cerner Source:** Millennium `CLINICAL_EVENT` table

**Phase 2 Implementation**

The Cerner Millennium architecture treats clinical notes as "Clinical Events" with a specific event class (`EventClass = 'DOC'`). This is fundamentally different from VistA's TIU architecture but maps to the same clinical concepts.

**Key Differences from VistA:**
- Uses `ClinicalEvent` instead of `TIUDocument`
- Event codes (vs Document Definitions) define note types
- Text stored in "Blob" tables (Binary Large Objects)
- Different field naming conventions (EventEndDateTime vs ReferenceDateTime, ResultStatus vs Status)
- Same underlying clinical data and standardized VHA titles

**CDWWork2 Table Structure:**

1. **`Dim.ClinicalEventCode`** - Note type definitions (equivalent to `Dim.TIUDocumentDefinition`)
   - Maps Cerner event codes to standardized classifications
   - Uses same `VHAEnterpriseStandardTitle` values as VistA for harmonization
   - Includes `DocumentClass` field mapping to same 4 classes (Progress Notes, Consults, Discharge Summaries, Imaging)

2. **`Clinical.ClinicalEvent`** - Note metadata fact table (equivalent to `TIU.TIUDocument_8925`)
   - `ClinicalEventSID` (surrogate primary key)
   - `EventEndDateTime` (equivalent to ReferenceDateTime - clinical date)
   - `PerformedDateTime` (equivalent to EntryDateTime - authored date)
   - `ResultStatus` (equivalent to Status: 'AUTH' = COMPLETED, 'IN ERROR' = RETRACTED)
   - `VerifiedByStaffSID` (equivalent to AuthorSID - primary author)
   - Same `PatientSID` and `Sta3n` as VistA (shared dimension tables)

3. **`Clinical.ClinicalEventBlob`** - Note content (equivalent to `TIU.TIUDocumentText`)
   - `EventBlobText` (full clinical narrative)
   - One-to-one relationship with `ClinicalEvent`

**Complete Schema Details:** See [Appendix E](#appendix-e-cdwwork2-cerneroraclehealth-schema-specifications) for full DDL scripts, indexes, seed data, and field mapping reference.

**Cerner Facilities (Distinct Sta3n Values):**
- 612 (Columbus VAMC) - Ohio Cerner pilot site
- 648 (Portland VAMC) - Oregon Cerner rollout
- 663 (Puget Sound VA) - Washington Cerner site

**Test Data Volume (Phase 2):**
- 30-50 clinical notes across the 3 Cerner facilities
- Same note class distribution as VistA (Progress Notes, Consults, Discharge Summaries, Imaging)
- 3 patients with notes from both VistA and Cerner facilities (simulating transferred care)

### 4.2 Test Data Strategy

**Overall Approach:** Unified Design, Phased Data Generation
- **Phase 1 (VistA):** 100-150 notes across 36 patients, 4 VistA facilities
- **Phase 2 (Cerner):** 30-50 additional notes, 3 Cerner facilities, 3 patients with dual-system notes
- **Total:** 130-200 clinical notes when both phases complete

---

#### 4.2.1 Phase 1: VistA Test Data

**Volume:** 100-150 clinical notes across 36 patients

**Note Class Distribution:**

| Note Class | Count | Notes per Patient Range | Example Titles |
|------------|-------|------------------------|----------------|
| Progress Notes | 50-60 | 1-8 | General Medicine Progress Note, Cardiology Progress Note, Primary Care Note |
| Consults | 25-30 | 0-3 | Cardiology Consult, Nephrology Consult, Psychiatry Consult |
| Discharge Summaries | 15-20 | 0-2 | Inpatient Discharge Summary, Observation Discharge Summary |
| Imaging Reports | 15-20 | 0-3 | Chest X-Ray Report, CT Scan Report, MRI Report |

**Temporal Distribution:**
- **Recent (<30 days):** 25% of notes
- **30-90 days:** 35% of notes
- **90-180 days:** 25% of notes
- **>180 days:** 15% of notes

**Patient Coverage:**
- 5 patients with extensive note history (15+ notes) - chronic disease management
- 15 patients with moderate note history (5-10 notes) - typical outpatient care
- 10 patients with minimal notes (1-4 notes) - healthy, infrequent visitors
- 6 patients with no notes (edge case testing)

**Edge Cases:**
- 2 patients with unsigned notes (Status = 'UNSIGNED')
- 1 patient with retracted note (Status = 'RETRACTED')
- 2 patients with cosigned notes (resident notes with attending cosigner)
- 3 patients with all 4 note classes represented
- 2 patients with notes from multiple facilities (transferred care)

**Note Content Structure:**

**Progress Notes (SOAP Format):**
```
SUBJECTIVE:
Patient presents for follow-up of [condition]. Reports [symptoms/complaints].
Compliance with medications: [good/fair/poor].

OBJECTIVE:
Vitals: BP [value], HR [value], Temp [value]
Physical Exam: [relevant findings]
Recent Labs: [relevant results]

ASSESSMENT:
1. [Primary diagnosis] - [status/description]
2. [Secondary diagnosis] - [status/description]

PLAN:
1. [Intervention/medication]
2. [Follow-up instructions]
3. [Patient education]

Electronically signed by: [Provider Name], MD
Date: [ReferenceDateTime]
```

**Consult Notes:**
```
REASON FOR CONSULT: [Chief complaint/reason]

HISTORY OF PRESENT ILLNESS:
[Detailed narrative]

PAST MEDICAL HISTORY:
[Relevant conditions]

MEDICATIONS:
[Current medications]

PHYSICAL EXAMINATION:
[Focused exam relevant to consult]

IMPRESSION:
[Assessment of consulting condition]

RECOMMENDATIONS:
1. [Recommendation 1]
2. [Recommendation 2]
3. [Follow-up plan]

[Specialty] Consult completed by: [Provider Name], MD
```

**Discharge Summaries:**
```
ADMISSION DATE: [date]
DISCHARGE DATE: [date]

ADMITTING DIAGNOSIS: [diagnosis]
DISCHARGE DIAGNOSIS: [final diagnosis]

HOSPITAL COURSE:
[Narrative of hospital stay, treatments, procedures]

DISCHARGE MEDICATIONS:
[Medication list with instructions]

DISCHARGE INSTRUCTIONS:
[Patient instructions, activity restrictions, diet]

FOLLOW-UP:
[Appointments, lab work, imaging]

Discharge summary completed by: [Provider Name], MD
```

**Imaging Reports:**
```
EXAM: [Imaging study type]
INDICATION: [Reason for study]

TECHNIQUE:
[Technical details of study]

FINDINGS:
[Detailed radiologic findings]

IMPRESSION:
[Summary and clinical significance]

Reported by: [Radiologist Name], MD
```

---

#### 4.2.2 Phase 2: Cerner Test Data

**Volume:** 30-50 clinical notes across 3 Cerner facilities

**Note Class Distribution:**

| Note Class | Count | Example Titles (Cerner-style) |
|------------|-------|------------------------------|
| Progress Notes | 15-20 | Physician Note - General, Physician Note - Cardiology, Primary Care Provider Note |
| Consults | 8-10 | Consult Note - Cardiology, Consult Note - Nephrology, Consult Note - Psychiatry |
| Discharge Summaries | 4-6 | Discharge Summary - Inpatient, Discharge Summary - Observation |
| Imaging Reports | 3-4 | Radiology Report - Chest X-Ray, Radiology Report - CT Scan |

**Facility Distribution:**

| Sta3n | Facility Name | System | Note Count |
|-------|---------------|--------|------------|
| 612 | Columbus VAMC | Cerner | 12-15 |
| 648 | Portland VAMC | Cerner | 10-12 |
| 663 | Puget Sound VA | Cerner | 8-10 |

**Patients with Dual-System Notes (Transferred Care):**

| Patient ICN | VistA Facility | Cerner Facility | Scenario |
|-------------|----------------|-----------------|----------|
| ICN100003 | 508 (Atlanta) | 612 (Columbus) | Transfer from Atlanta VistA to Columbus Cerner |
| ICN100015 | 516 (Bay Pines) | 648 (Portland) | Transfer from Bay Pines VistA to Portland Cerner |
| ICN100028 | 552 (Dayton) | 663 (Puget Sound) | Transfer from Dayton VistA to Puget Sound Cerner |

**Temporal Distribution (Same as VistA):**
- Recent (<30 days): 30% of Cerner notes
- 30-90 days: 40% of Cerner notes
- 90-180 days: 20% of Cerner notes
- >180 days: 10% of Cerner notes

**Content Style:**
- Use same SOAP format as VistA notes (clinical content standardized across VA)
- Use Cerner-style titles to differentiate source (e.g., "Physician Note - General" vs "GEN MED PROGRESS NOTE")
- Map to same VHAEnterpriseStandardTitle values for proper harmonization
- Map to same DocumentClass values (Progress Notes, Consults, Discharge Summaries, Imaging)

**Edge Cases to Include:**
- 1 patient with note from Cerner facility showing 'MODIFIED' ResultStatus (equivalent to AMENDED)
- 1 patient with 'IN ERROR' ResultStatus note (equivalent to RETRACTED)

---

### 4.3 Note Type Definitions (Seed Data)

**Dimension Table Seed Data:** `mock/sql-server/cdwwork/insert/Dim.TIUDocumentDefinition.sql`

| DocumentDefinitionSID | TIUDocumentTitle | DocumentClass | VHAEnterpriseStandardTitle |
|-----------------------|------------------|---------------|----------------------------|
| 100 | GEN MED PROGRESS NOTE | Progress Notes | Physician Progress Note |
| 101 | CARDIOLOGY PROGRESS NOTE | Progress Notes | Cardiology Progress Note |
| 102 | PRIMARY CARE NOTE | Progress Notes | Primary Care Progress Note |
| 103 | SPECIALTY CLINIC NOTE | Progress Notes | Specialty Care Progress Note |
| 200 | CARDIOLOGY CONSULT | Consults | Cardiology Consultation Note |
| 201 | NEPHROLOGY CONSULT | Consults | Nephrology Consultation Note |
| 202 | PSYCHIATRY CONSULT | Consults | Psychiatry Consultation Note |
| 203 | NEUROLOGY CONSULT | Consults | Neurology Consultation Note |
| 300 | DISCHARGE SUMMARY | Discharge Summaries | Inpatient Discharge Summary |
| 301 | OBSERVATION DISCHARGE | Discharge Summaries | Observation Discharge Summary |
| 400 | CHEST X-RAY REPORT | Imaging | Radiology Report - Chest X-Ray |
| 401 | CT SCAN REPORT | Imaging | Radiology Report - CT Scan |
| 402 | MRI REPORT | Imaging | Radiology Report - MRI |

---

## 5. ETL Pipeline

**Strategy:** Separate Bronze files for each source, merge in Silver layer

- **Phase 1:** VistA extraction only
- **Phase 2:** Add Cerner extraction, update Silver to merge both sources

### 5.1 Bronze Layer - Raw Extraction

#### 5.1.1 Phase 1: VistA Extraction

**Script:** `etl/bronze_clinical_notes_vista.py`

**Purpose:** Extract raw note data from CDWWork TIU schema with minimal transformation

**SQL Query:**
```sql
SELECT
    d.TIUDocumentSID,
    d.Sta3n,
    d.TIUDocumentIEN,
    d.PatientSID,
    d.DocumentDefinitionSID,
    d.VisitSID,
    d.ReferenceDateTime,
    d.EntryDateTime,
    d.Status,
    d.AuthorSID,
    d.CosignerSID,

    -- Join to get patient identity
    p.PatientICN,
    p.PatientName,

    -- Join to get note type classification
    def.TIUDocumentTitle,
    def.DocumentClass,
    def.VHAEnterpriseStandardTitle,

    -- Join to get author information
    auth.StaffName AS AuthorName,
    cosign.StaffName AS CosignerName,

    -- Join to get note text
    txt.DocumentText,

    -- Join to get facility name
    fac.FacilityName

FROM TIU.TIUDocument_8925 d

LEFT JOIN SPatient.SPatient p ON d.PatientSID = p.PatientSID
LEFT JOIN Dim.TIUDocumentDefinition def ON d.DocumentDefinitionSID = def.DocumentDefinitionSID
LEFT JOIN SStaff.SStaff auth ON d.AuthorSID = auth.StaffSID
LEFT JOIN SStaff.SStaff cosign ON d.CosignerSID = cosign.StaffSID
LEFT JOIN TIU.TIUDocumentText txt ON d.TIUDocumentSID = txt.TIUDocumentSID
LEFT JOIN Dim.Facility fac ON d.Sta3n = fac.Sta3n

WHERE d.Status IN ('COMPLETED', 'UNSIGNED', 'RETRACTED')  -- Exclude draft/deleted
ORDER BY d.ReferenceDateTime DESC;
```

**Output:** `bronze/cdwwork/clinical_notes` (Parquet file in MinIO)

**Partitioning:** None for development; partition by Sta3n or Year(ReferenceDateTime) in production

---

#### 5.1.2 Phase 2: Cerner Extraction

**Script:** `etl/bronze_clinical_notes_cerner.py`

**Purpose:** Extract raw note data from CDWWork2 Clinical schema with minimal transformation

**SQL Query:**
```sql
SELECT
    e.ClinicalEventSID,
    e.Sta3n,
    e.PatientSID,
    e.EventCodeSID,
    e.VisitSID,
    e.EventEndDateTime,      -- Maps to ReferenceDateTime
    e.PerformedDateTime,     -- Maps to EntryDateTime
    e.ResultStatus,          -- Maps to Status ('AUTH' = COMPLETED, 'IN ERROR' = RETRACTED)
    e.VerifiedByStaffSID,    -- Maps to AuthorSID
    e.CosignStaffSID,        -- Maps to CosignerSID

    -- Join to get patient identity (shared with CDWWork)
    p.PatientICN,
    p.PatientName,

    -- Join to get note type classification
    ec.EventCodeDesc,        -- Maps to TIUDocumentTitle
    ec.DocumentClass,
    ec.VHAEnterpriseStandardTitle,  -- Same as VistA!

    -- Join to get author information (shared with CDWWork)
    auth.StaffName AS AuthorName,
    cosign.StaffName AS CosignerName,

    -- Join to get note text
    txt.EventBlobText,       -- Maps to DocumentText

    -- Join to get facility name (shared with CDWWork)
    fac.FacilityName

FROM Clinical.ClinicalEvent e

LEFT JOIN SPatient.SPatient p ON e.PatientSID = p.PatientSID
LEFT JOIN Dim.ClinicalEventCode ec ON e.EventCodeSID = ec.EventCodeSID
LEFT JOIN SStaff.SStaff auth ON e.VerifiedByStaffSID = auth.StaffSID
LEFT JOIN SStaff.SStaff cosign ON e.CosignStaffSID = cosign.StaffSID
LEFT JOIN Clinical.ClinicalEventBlob txt ON e.ClinicalEventSID = txt.ClinicalEventSID
LEFT JOIN Dim.Facility fac ON e.Sta3n = fac.Sta3n

WHERE ec.EventClass = 'DOC'  -- Filter for document events (clinical notes)
  AND e.ResultStatus IN ('AUTH', 'MODIFIED', 'IN ERROR')  -- Exclude drafts
ORDER BY e.EventEndDateTime DESC;
```

**Output:** `bronze/cdwwork2/clinical_notes` (Parquet file in MinIO)

**Partitioning:** None for development; partition by Sta3n or Year(EventEndDateTime) in production

**Note:** Bronze extractions are kept separate by source system. Merging happens in Silver layer.

---

### 5.2 Silver Layer - Cleaning and Harmonization

**Script:** `etl/silver_clinical_notes.py`

**Purpose:** Harmonize both VistA and Cerner data into unified schema, then merge into single Silver dataset

**Dual-Source Processing:**
1. **Phase 1:** Process VistA Bronze only
2. **Phase 2:** Process both VistA and Cerner Bronze, merge into single Silver file

**Transformations (Applied to Both Sources):**
1. **Patient Identity Resolution**: Map `PatientSID` → `PatientICN` (unified patient key)
2. **Source System Tagging**: Add `source_system` column ('VistA' or 'Cerner')
3. **Source ID Preservation**:
   - VistA: Populate `tiu_document_sid`, set `clinical_event_sid` to NULL
   - Cerner: Populate `clinical_event_sid`, set `tiu_document_sid` to NULL
4. **Field Harmonization** (map Cerner → VistA equivalents):
   - `EventCodeDesc` → `note_title`
   - `EventEndDateTime` → `reference_datetime`
   - `PerformedDateTime` → `entry_datetime`
   - `EventBlobText` → `note_text`
5. **Status Mapping**:
   - VistA: Use Status as-is ('COMPLETED', 'UNSIGNED', 'RETRACTED')
   - Cerner: Map ResultStatus ('AUTH' → 'COMPLETED', 'IN ERROR' → 'RETRACTED', 'MODIFIED' → 'AMENDED')
6. **Date Standardization**: Convert DATETIME2 to ISO 8601 strings (`YYYY-MM-DD HH:MM:SS`)
7. **Note Class Normalization**: Ensure DocumentClass values are standardized across both sources
8. **Author Name and Credentials Extraction**:
   - Standardize author_name to "Last, First Suffix" format
   - Extract author_credentials from SStaff.Title field or parse from author name (e.g., "MD", "DO", "NP", "PA")
9. **Text Cleaning**:
   - Strip control characters and excessive whitespace
   - Preserve line breaks and paragraph structure
   - Remove null bytes
10. **Null Handling**: Replace NULL text with `'[No note text available]'`

**Merging Strategy:**
- Concatenate VistA and Cerner DataFrames (Polars `concat`)
- Sort by patient_icn, then reference_datetime DESC
- No deduplication needed (notes from different systems are distinct events)

**Output:** `silver/clinical_notes` (Parquet file in MinIO)

**Schema (Unified for Both Sources):**
```python
{
    # Source lineage
    "source_system": str,  # 'VistA' or 'Cerner'
    "tiu_document_sid": int,  # Populated for VistA, NULL for Cerner
    "clinical_event_sid": int,  # Populated for Cerner, NULL for VistA

    # Patient identity
    "patient_icn": str,
    "patient_sid": int,

    # Note metadata (harmonized)
    "note_title": str,
    "note_class": str,  # 'Progress Notes', 'Consults', 'Discharge Summaries', 'Imaging'
    "standard_title": str,
    "reference_datetime": datetime,
    "entry_datetime": datetime,
    "status": str,  # 'COMPLETED', 'UNSIGNED', 'RETRACTED', 'AMENDED'
    "author_name": str,
    "author_credentials": str,  # 'MD', 'DO', 'NP', 'PA', 'RN', etc.
    "cosigner_name": str,
    "note_text": str,  # Full cleaned text
    "facility_name": str,
    "sta3n": int,
    "visit_sid": int
}
```

### 5.3 Gold Layer - Patient-Centric Aggregation

**Script:** `etl/gold_clinical_notes.py`

**Transformations:**
1. **Patient-Centric Grouping**: Group by `PatientICN`
2. **Note Sorting**: Order by `ReferenceDateTime DESC` (most recent first)
3. **Note Count Rollups**:
   - `total_notes` (lifetime count)
   - `notes_by_class` (count per note class: Progress, Consult, Discharge, Imaging)
   - `recent_notes_30d` (count of notes in last 30 days)
4. **Text Preview Generation**: Create 150-character preview for widget display
5. **Author Aggregation**: Create list of unique authors for filter dropdown
6. **AI Preparation** (columns reserved for Phase 2):
   - `embedding_vector`: NULL (to be populated with vector embeddings)
   - `ai_summary`: NULL (to be populated with AI-generated summary)
   - `key_entities`: NULL (to be populated with NER extraction)

**Output:** `gold/clinical_notes` (Parquet file in MinIO)

**Schema:**
```python
{
    "patient_icn": str,
    "patient_key": int,  # Derived from ICN for DB FK
    "total_notes": int,
    "notes_by_class": {
        "Progress Notes": int,
        "Consults": int,
        "Discharge Summaries": int,
        "Imaging": int
    },
    "recent_notes_30d": int,
    "most_recent_note_date": datetime,
    "authors": List[str],  # Unique list of author names
    "notes": [  # List of note dicts
        {
            "tiu_document_sid": int,
            "note_title": str,
            "note_class": str,
            "standard_title": str,
            "reference_datetime": datetime,
            "entry_datetime": datetime,
            "status": str,
            "author_name": str,
            "cosigner_name": str,
            "note_text": str,
            "text_preview": str,  # First 150 chars
            "facility_name": str,
            "sta3n": int,
            # AI columns (reserved for Phase 2)
            "embedding_vector": None,
            "ai_summary": None,
            "key_entities": None
        }
    ]
}
```

---

## 6. PostgreSQL Serving Database

### 6.1 Table Schema - patient_clinical_notes

**DDL Script:** `db/ddl/create_patient_clinical_notes_table.sql`

```sql
-- Clinical Notes Table
-- Dual-Source Architecture: VistA (CDWWork) + Cerner (CDWWork2)
-- Phase 1: VistA notes only
-- Phase 2: Add Cerner notes (no schema changes required)
-- AI-ready schema with reserved columns for embeddings and summaries

CREATE TABLE IF NOT EXISTS patient_clinical_notes (
    note_id BIGSERIAL PRIMARY KEY,
    patient_icn VARCHAR(20) NOT NULL,
    patient_key INTEGER NOT NULL,

    -- Source lineage (dual-source architecture)
    source_system VARCHAR(10) NOT NULL,     -- 'VistA' or 'Cerner'
    tiu_document_sid BIGINT,                -- Populated if source_system = 'VistA', NULL otherwise
    clinical_event_sid BIGINT,              -- Populated if source_system = 'Cerner', NULL otherwise

    -- Note identification (normalized across sources)
    note_title VARCHAR(200) NOT NULL,
    note_class VARCHAR(100),  -- 'Progress Notes', 'Consults', 'Discharge Summaries', 'Imaging'
    standard_title VARCHAR(200),

    -- Note content
    note_text TEXT,  -- Full clinical narrative
    text_preview VARCHAR(200),  -- First 150-200 chars for widget display

    -- Temporal data
    reference_datetime TIMESTAMP NOT NULL,  -- Clinical date (primary sort)
    entry_datetime TIMESTAMP,  -- When note was authored

    -- Status and workflow
    status VARCHAR(50),  -- 'COMPLETED', 'UNSIGNED', 'RETRACTED', 'AMENDED'

    -- Authorship
    author_name VARCHAR(100),
    author_credentials VARCHAR(20),  -- 'MD', 'DO', 'NP', 'PA', 'RN', etc.
    cosigner_name VARCHAR(100),

    -- Administrative
    facility_name VARCHAR(100),
    sta3n INTEGER,
    visit_sid BIGINT,  -- Link to encounter (if applicable)

    -- AI/RAG columns (Phase 2 - reserved for future use)
    embedding_vector vector(1536),  -- OpenAI ada-002 embedding dimension
    ai_summary TEXT,  -- AI-generated summary
    key_entities JSONB,  -- Extracted entities (medications, diagnoses, etc.)

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_source_system_sid CHECK (
        (source_system = 'VistA' AND tiu_document_sid IS NOT NULL AND clinical_event_sid IS NULL) OR
        (source_system = 'Cerner' AND clinical_event_sid IS NOT NULL AND tiu_document_sid IS NULL)
    )
);

-- Indexes for common query patterns
CREATE INDEX idx_clinical_notes_patient_icn
    ON patient_clinical_notes(patient_icn);

CREATE INDEX idx_clinical_notes_patient_key
    ON patient_clinical_notes(patient_key);

CREATE INDEX idx_clinical_notes_reference_datetime
    ON patient_clinical_notes(reference_datetime DESC);

CREATE INDEX idx_clinical_notes_patient_ref_datetime
    ON patient_clinical_notes(patient_icn, reference_datetime DESC);

CREATE INDEX idx_clinical_notes_note_class
    ON patient_clinical_notes(note_class)
    WHERE note_class IS NOT NULL;

CREATE INDEX idx_clinical_notes_author
    ON patient_clinical_notes(author_name)
    WHERE author_name IS NOT NULL;

CREATE INDEX idx_clinical_notes_status
    ON patient_clinical_notes(status)
    WHERE status IS NOT NULL;

CREATE INDEX idx_clinical_notes_source_system
    ON patient_clinical_notes(source_system);

-- Full-text search index (Phase 2 - for note text search)
-- CREATE INDEX idx_clinical_notes_text_search
--     ON patient_clinical_notes USING gin(to_tsvector('english', note_text));

-- Vector similarity search index (Phase 2 - for AI/RAG)
-- CREATE INDEX idx_clinical_notes_embedding_vector
--     ON patient_clinical_notes USING ivfflat (embedding_vector vector_cosine_ops)
--     WITH (lists = 100);

-- Foreign key (if patient_demographics table exists)
-- ALTER TABLE patient_clinical_notes
--     ADD CONSTRAINT fk_clinical_notes_patient
--     FOREIGN KEY (patient_key) REFERENCES patient_demographics(patient_key);

-- Comments on dual-source columns
COMMENT ON COLUMN patient_clinical_notes.source_system IS 'Source EHR system: VistA or Cerner';
COMMENT ON COLUMN patient_clinical_notes.tiu_document_sid IS 'VistA TIU Document SID (NULL for Cerner notes)';
COMMENT ON COLUMN patient_clinical_notes.clinical_event_sid IS 'Cerner Clinical Event SID (NULL for VistA notes)';

-- Comment on AI columns
COMMENT ON COLUMN patient_clinical_notes.embedding_vector IS 'Vector embedding for semantic search (Phase 2)';
COMMENT ON COLUMN patient_clinical_notes.ai_summary IS 'AI-generated summary for quick review (Phase 2)';
COMMENT ON COLUMN patient_clinical_notes.key_entities IS 'Extracted clinical entities: medications, diagnoses, procedures (Phase 2)';
```

**Key Design Elements:**
- **Dual-Source Architecture**: `source_system` column with `tiu_document_sid` (VistA) or `clinical_event_sid` (Cerner), enforced by check constraint
- **Source-Agnostic Schema**: No schema changes required when adding Cerner notes in Phase 2
- **Data Lineage**: Preserves original source system IDs for traceability
- **AI-Ready Schema**: Includes `embedding_vector`, `ai_summary`, `key_entities` columns (unpopulated in Phase 1)
- **pgvector Support**: Uses `vector(1536)` type for OpenAI embeddings (requires pgvector extension)
- **Full-Text Search Ready**: Commented index for future full-text search capability
- **Text Preview**: Dedicated column for widget display (avoids loading full text for dashboard)
- **Comprehensive Indexing**: Optimized for patient-centric queries, date ranges, filtering, and source system filtering

### 6.2 Data Loading

**Script:** `etl/load_clinical_notes.py`

**Process:**
1. Read Gold Parquet from MinIO (`gold/clinical_notes`)
2. Flatten nested `notes` list into individual rows
3. **Phase 1:** Truncate existing table, load VistA notes only
4. **Phase 2:** Append Cerner notes to existing VistA notes (no truncate, incremental load)
5. Bulk insert via SQLAlchemy `to_sql()` or `psycopg2 COPY`
6. Verify row count and index integrity
7. Test query performance (90-day queries should be <2 seconds)
8. Verify source_system check constraint is enforced

**Expected Row Count:**
- **Phase 1:** 100-150 VistA notes
- **Phase 2:** 130-200 total notes (VistA + Cerner)

**Performance Targets:**
- Load time: <10 seconds for 150 notes (Phase 1), <15 seconds for 200 notes (Phase 2)
- Query time (90 days, single patient): <2 seconds
- Widget query (4 most recent notes): <1 second
- Dual-system patient query (notes from both VistA and Cerner): <2 seconds

---

## 7. API Design

### 7.1 Routing Architecture - Pattern B (Dedicated Router)

**Router File:** `app/routes/notes.py`

**Rationale for Pattern B:**
- Complex domain with full-page view
- Multiple query patterns (note class filtering, date ranges, author filtering)
- Text-heavy content requires expandable rows
- Future enhancements planned (full-text search, AI summarization, Vista overlay)
- Separates concerns from `patient.py`

### 7.2 API Endpoints

#### 7.2.1 Widget Endpoint - Recent Notes

**Endpoint:** `GET /patient/{patient_icn}/notes/widget`

**Purpose:** Fetch 3-4 most recent clinical notes for dashboard widget display

**Query Parameters:** None (always returns most recent)

**SQL Query:**
```sql
SELECT
    note_id,
    tiu_document_sid,
    note_title,
    note_class,
    reference_datetime,
    author_name,
    author_credentials,
    facility_name,
    text_preview,
    status
FROM patient_clinical_notes
WHERE patient_icn = :patient_icn
  AND status = 'COMPLETED'  -- Exclude unsigned/retracted from widget
ORDER BY reference_datetime DESC
LIMIT 4;
```

**Response Format (JSON):**
```json
{
  "patient_icn": "1000000001V123456",
  "total_notes": 42,
  "notes_by_class": {
    "Progress Notes": 25,
    "Consults": 8,
    "Discharge Summaries": 5,
    "Imaging": 4
  },
  "recent_notes": [
    {
      "note_id": 1523,
      "tiu_document_sid": 50012,
      "note_title": "GEN MED PROGRESS NOTE",
      "note_class": "Progress Notes",
      "reference_datetime": "2025-12-28T10:30:00",
      "author_name": "Smith, John",
      "author_credentials": "MD",
      "facility_name": "Atlanta VAMC",
      "text_preview": "SUBJECTIVE: Patient presents for follow-up of hypertension and diabetes. Reports good medication compliance. Blood sugars have been running 120-140 mg/dL...",
      "status": "COMPLETED"
    },
    {
      "note_id": 1498,
      "tiu_document_sid": 49876,
      "note_title": "CARDIOLOGY CONSULT",
      "note_class": "Consults",
      "reference_datetime": "2025-12-15T14:00:00",
      "author_name": "Johnson, Mary",
      "author_credentials": "MD",
      "facility_name": "Atlanta VAMC",
      "text_preview": "REASON FOR CONSULT: Evaluate for coronary artery disease. Patient with chest pain on exertion. HISTORY OF PRESENT ILLNESS: 68-year-old male with...",
      "status": "COMPLETED"
    }
  ]
}
```

**Template:** `app/templates/partials/notes_widget.html`

**HTMX Fragment:** Returns widget HTML (no full page wrapper)

#### 7.2.2 Full Page Endpoint - All Notes

**Endpoint:** `GET /patient/{patient_icn}/notes`

**Purpose:** Display comprehensive clinical notes with filtering, sorting, and pagination

**Query Parameters:**
- `note_class` (optional): `'all'` (default), `'Progress Notes'`, `'Consults'`, `'Discharge Summaries'`, `'Imaging'`
- `date_range` (optional): `'30'`, `'90'` (default), `'180'`, `'365'`, `'all'` (days)
- `author` (optional): Filter by author name (from dropdown)
- `status` (optional): `'all'` (default), `'COMPLETED'`, `'UNSIGNED'`, `'RETRACTED'`
- `sort` (optional): `'date'` (default), `'author'`, `'type'`
- `order` (optional): `'desc'` (default) or `'asc'`
- `page` (optional): Page number for pagination (default: 1)
- `per_page` (optional): Notes per page (default: 10, options: 10/20/50)

**SQL Query (with filters):**
```sql
SELECT
    note_id,
    tiu_document_sid,
    note_title,
    note_class,
    standard_title,
    reference_datetime,
    entry_datetime,
    status,
    author_name,
    author_credentials,
    cosigner_name,
    facility_name,
    sta3n,
    text_preview,
    note_text
FROM patient_clinical_notes
WHERE patient_icn = :patient_icn
  AND (:note_class = 'all' OR note_class = :note_class)
  AND (
    :date_range = 'all' OR
    reference_datetime >= NOW() - INTERVAL ':date_range days'
  )
  AND (:author IS NULL OR author_name = :author)
  AND (:status = 'all' OR status = :status)
ORDER BY
    CASE WHEN :sort = 'date' THEN reference_datetime END DESC,
    CASE WHEN :sort = 'author' THEN author_name END ASC,
    CASE WHEN :sort = 'type' THEN note_class END ASC
LIMIT :per_page OFFSET :offset;
```

**Template:** `app/templates/patient_notes.html`

**HTMX Integration:**
- Filter dropdowns trigger `hx-get` to reload table without full page refresh
- Sort headers use `hx-get` with `hx-target="#notes-table"`
- Pagination uses `hx-get` for seamless page navigation
- "Expand" buttons use `hx-get` to load full note text on demand

#### 7.2.3 Note Detail Endpoint - Full Text

**Endpoint:** `GET /patient/{patient_icn}/notes/{note_id}`

**Purpose:** Fetch full note text for expandable row display

**Query Parameters:** None

**SQL Query:**
```sql
SELECT
    note_id,
    tiu_document_sid,
    note_title,
    note_class,
    standard_title,
    reference_datetime,
    entry_datetime,
    status,
    author_name,
    author_credentials,
    cosigner_name,
    facility_name,
    sta3n,
    note_text
FROM patient_clinical_notes
WHERE note_id = :note_id
  AND patient_icn = :patient_icn;
```

**Template:** `app/templates/partials/note_detail.html`

**HTMX Fragment:** Returns note text HTML (injected into expandable row)

### 7.3 Database Query Functions

**File:** `app/db/notes.py`

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


def get_recent_notes(icn: str, limit: int = 4) -> List[Dict[str, Any]]:
    """Fetch most recent clinical notes for widget."""
    query = text("""
        SELECT
            note_id,
            tiu_document_sid,
            note_title,
            note_class,
            reference_datetime,
            author_name,
            author_credentials,
            facility_name,
            text_preview,
            status
        FROM patient_clinical_notes
        WHERE patient_icn = :icn
          AND status = 'COMPLETED'
        ORDER BY reference_datetime DESC
        LIMIT :limit
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn, "limit": limit})
        return [dict(row._mapping) for row in result]


def get_notes_summary(icn: str) -> Dict[str, Any]:
    """Get aggregate note counts by class."""
    query = text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN note_class = 'Progress Notes' THEN 1 ELSE 0 END) as progress_notes,
            SUM(CASE WHEN note_class = 'Consults' THEN 1 ELSE 0 END) as consults,
            SUM(CASE WHEN note_class = 'Discharge Summaries' THEN 1 ELSE 0 END) as discharge_summaries,
            SUM(CASE WHEN note_class = 'Imaging' THEN 1 ELSE 0 END) as imaging
        FROM patient_clinical_notes
        WHERE patient_icn = :icn
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn}).fetchone()
        return {
            "total": result.total or 0,
            "Progress Notes": result.progress_notes or 0,
            "Consults": result.consults or 0,
            "Discharge Summaries": result.discharge_summaries or 0,
            "Imaging": result.imaging or 0
        }


def get_all_notes(
    icn: str,
    note_class: str = 'all',
    date_range: str = '90',
    author: Optional[str] = None,
    status: str = 'all',
    sort_by: str = 'date',
    order: str = 'desc',
    page: int = 1,
    per_page: int = 10
) -> List[Dict[str, Any]]:
    """Fetch all notes with filtering, sorting, pagination."""

    # Build WHERE clause
    where_clauses = ["patient_icn = :icn"]
    params = {
        "icn": icn,
        "per_page": per_page,
        "offset": (page - 1) * per_page
    }

    if note_class != 'all':
        where_clauses.append("note_class = :note_class")
        params["note_class"] = note_class

    if date_range != 'all':
        where_clauses.append("reference_datetime >= NOW() - INTERVAL :date_range")
        params["date_range"] = f"{date_range} days"

    if author:
        where_clauses.append("author_name = :author")
        params["author"] = author

    if status != 'all':
        where_clauses.append("status = :status")
        params["status"] = status

    where_sql = " AND ".join(where_clauses)

    # Build ORDER BY clause
    sort_column = {
        'date': 'reference_datetime',
        'author': 'author_name',
        'type': 'note_class'
    }.get(sort_by, 'reference_datetime')

    order_sql = f"{sort_column} {'ASC' if order == 'asc' else 'DESC'}"

    query = text(f"""
        SELECT
            note_id,
            tiu_document_sid,
            note_title,
            note_class,
            standard_title,
            reference_datetime,
            entry_datetime,
            status,
            author_name,
            author_credentials,
            cosigner_name,
            facility_name,
            sta3n,
            text_preview
        FROM patient_clinical_notes
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT :per_page OFFSET :offset
    """)

    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._mapping) for row in result]


def get_note_detail(icn: str, note_id: int) -> Optional[Dict[str, Any]]:
    """Fetch full note text for expandable row."""
    query = text("""
        SELECT
            note_id,
            tiu_document_sid,
            note_title,
            note_class,
            standard_title,
            reference_datetime,
            entry_datetime,
            status,
            author_name,
            author_credentials,
            cosigner_name,
            facility_name,
            sta3n,
            note_text
        FROM patient_clinical_notes
        WHERE note_id = :note_id
          AND patient_icn = :icn
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"note_id": note_id, "icn": icn}).fetchone()
        return dict(result._mapping) if result else None


def get_note_authors(icn: str) -> List[str]:
    """Get unique list of authors for filter dropdown."""
    query = text("""
        SELECT DISTINCT author_name
        FROM patient_clinical_notes
        WHERE patient_icn = :icn
          AND author_name IS NOT NULL
        ORDER BY author_name
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn})
        return [row.author_name for row in result]
```

---

## 8. UI Specifications

### 8.1 Dashboard Widget Specifications

The Clinical Notes widget supports two layout options:
- **8.1.1 - 2x1 Compact Widget**: Standard two-column width, single-row height (existing pattern)
- **8.1.2 - 2x2 Enhanced Detail Widget**: Two-column width, two-row height (first multi-row widget in med-z1)

**Implementation Priority**: **2x1 Compact is the active implementation.** The 2x2 Enhanced Detail design was fully implemented but archived in favor of better dashboard density (see Section 1.4 for decision rationale). Both designs are documented below for completeness.

---

#### 8.1.1 Dashboard Widget (2x1) - Compact View

**File:** `app/templates/partials/notes_widget.html`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📄 Clinical Notes                                           │  (Header with icon and title)
├─────────────────────────────────────────────────────────────┤
│ [Progress Note] 12/28/2025 • Dr. Smith • Atlanta VAMC       │  (Most recent note)
│ SUBJECTIVE: Patient presents for follow-up of HTN and DM.   │  (Text preview - 150 chars)
│ Reports good medication compliance...                       │
├─────────────────────────────────────────────────────────────┤
│ [Consult] 12/15/2025 • Dr. Johnson • Atlanta VAMC           │  (Second note)
│ REASON FOR CONSULT: Evaluate for CAD. Patient with chest    │
│ pain on exertion...                                         │
├─────────────────────────────────────────────────────────────┤
│ [Discharge] 11/20/2025 • Dr. Williams • Bay Pines VAMC      │  (Third note)
│ ADMISSION DATE: 11/17/2025. DISCHARGE DATE: 11/20/2025.     │
│ Admitted for pneumonia...                                   │
├─────────────────────────────────────────────────────────────┤
│ ↗ View All Clinical Notes (42 total)                        │  (Bottom action link)
└─────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Header**: Title with document icon
- **Note Type Badges**: Color-coded badges
  - Progress Note: Blue (#1976D2)
  - Consult: Purple (#7B1FA2)
  - Discharge Summary: Green (#388E3C)
  - Imaging: Orange (#F57C00)
- **Date Display**: "MM/DD/YYYY" format
- **Author**: Abbreviated format (e.g., "Dr. Smith")
- **Text Preview**: First 100-150 characters of note text
- **Max Items**: 3-4 notes (most recent)
- **View All Link**: Shows total note count

**Jinja2 Template:**
```html
<!-- Clinical Notes Widget Content -->
<!-- Widget Header -->
<div class="widget__header">
    <div class="widget__title-group">
        <i class="fa-solid fa-file-medical widget__icon"></i>
        <h3 class="widget__title">Clinical Notes</h3>
    </div>
    {% if total_count > 0 %}
        <span class="badge badge--info">{{ total_count }} Total</span>
    {% endif %}
</div>

<!-- Widget Body -->
<div class="widget__body">
    <div class="widget-notes">
        {% if error %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">
                <i class="fa-solid fa-circle-exclamation"></i> Error loading notes
            </p>
        {% elif total_count == 0 %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">No clinical notes recorded</p>
        {% else %}
            <!-- Notes List (Most Recent 3-4) -->
            <div class="notes-list-widget">
                {% for note in recent_notes %}
                <div class="note-item-widget">
                    <!-- Note header with type badge -->
                    <div class="note-item-widget__header">
                        <span class="note-badge note-badge--{{ note.note_class|replace(' ', '-')|lower }}">
                            {{ note.note_class|replace(' Notes', '')|replace(' Summaries', '') }}
                        </span>
                        <span class="note-item-widget__date">
                            {{ note.reference_datetime.strftime('%m/%d/%Y') }}
                        </span>
                    </div>

                    <!-- Note metadata -->
                    <div class="note-item-widget__meta">
                        {{ note.author_name }} • {{ note.facility_name }}
                    </div>

                    <!-- Note text preview -->
                    <div class="note-item-widget__preview">
                        {{ note.text_preview }}
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- View All Link -->
            <div class="widget-action">
                <a href="/patient/{{ patient_icn }}/notes" class="btn btn--link btn--sm">
                    <i class="fa-regular fa-arrow-up-right-from-square"></i>
                    View All Clinical Notes ({{ total_count }} total)
                </a>
            </div>
        {% endif %}
    </div>
</div>

<!-- Widget Footer -->
<div class="widget__footer"></div>
```

---

#### 8.1.2 Dashboard Widget (2x2) - Enhanced Detail View (ARCHIVED)

**File:** `app/templates/partials/notes_widget.html` (implemented but archived - see Section 1.4)

**Widget Size:** 2 columns wide × 2 rows tall

**Status:** This design was fully implemented but replaced with the 2x1 Compact layout for better dashboard density. Documented here for potential future use as a user preference option.

**Layout:**
```
┌───────────────────────────────────────────────────────────────────────────────┐
│ 📄 Clinical Notes                                                             │  (Header with icon and title)
├───────────────────────────────────────────────────────────────────────────────┤
│ Progress Note                                                                 │  (Note class - full text, not badge)
│ 12/28/2025 at 14:30 • Dr. Jonathan Smith, MD • Atlanta VA Medical Center      │  (Full metadata line)
│ Status: Completed                                                             │  (Status)
│                                                                               │
│ SUBJECTIVE: Patient presents for routine follow-up of hypertension and        │
│ diabetes mellitus. Reports good medication compliance and no adverse          │
│ effects. Blood pressure log shows values ranging 128-138/78-84. Fasting       │
│ glucose readings 110-125 mg/dL. Denies chest pain, SOB, or edema.             │  (250-300 char preview)
├───────────────────────────────────────────────────────────────────────────────┤
│ Consult                                                                       │
│ 12/15/2025 at 09:15 • Dr. Emily Johnson, MD • Atlanta VA Medical Center       │
│ Status: Completed                                                             │
│                                                                               │
│ REASON FOR CONSULT: Evaluate for coronary artery disease. Patient with        │
│ chest pain on exertion, family history of CAD. HISTORY: 68-year-old male      │
│ veteran presents with 3-month history of substernal chest pressure with       │
│ moderate exertion. No radiation. Relieved with rest...                        │  (250-300 char preview)
├───────────────────────────────────────────────────────────────────────────────┤
│ Discharge Summary                                                             │
│ 11/20/2025 at 16:45 • Dr. Michael Williams, MD • Bay Pines VA Medical Center  │
│ Status: Completed                                                             │
│                                                                               │
│ ADMISSION DATE: 11/17/2025. DISCHARGE DATE: 11/20/2025. ADMITTING DIAGNOSIS:  │
│ Community-acquired pneumonia. HOSPITAL COURSE: Patient admitted with fever,   │
│ productive cough, and infiltrate on CXR. Treated with IV antibiotics.         │
│ Clinical improvement noted by hospital day 2. Transitioned to oral...         │  (250-300 char preview)
├───────────────────────────────────────────────────────────────────────────────┤
│ ↗ View All Clinical Notes (42 total)                                          │  (Bottom action link)
└───────────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**

- **Header**: Title with document icon
- **Note Class Display**: Full text format instead of compact badge (e.g., "Progress Note", "Consult", "Discharge Summary", "Imaging Report")
- **Complete DateTime**: Full date and time format "MM/DD/YYYY at HH:MM"
- **Author**: Full name with credentials (e.g., "Dr. Jonathan Smith, MD")
- **Facility**: Complete facility name (e.g., "Atlanta VA Medical Center")
- **Status**: Explicit status display (e.g., "Status: Completed")
- **Text Preview**: 250-300 characters of note text (significantly more than 2x1 compact view)
- **Max Items**: 3 notes (balanced quantity for 2-row height)
- **View All Link**: Shows total note count

**Enhanced Features Compared to 2x1:**

| Feature | 2x1 Compact | 2x2 Enhanced Detail |
|---------|-------------|---------------------|
| Widget Height | 1 row | 2 rows |
| Note Count | 3-4 notes | 3 notes (balanced) |
| Preview Length | 100-150 characters | 250-300 characters |
| Date Format | MM/DD/YYYY | MM/DD/YYYY at HH:MM |
| Author Format | Abbreviated (Dr. Smith) | Full with credentials (Dr. Jonathan Smith, MD) |
| Facility | Short name | Full facility name |
| Status Display | Hidden | Explicit (Status: Completed) |
| Note Class | Compact badge | Full text label |
| Space Efficiency | More notes, less detail | More detail per note |

**Design Rationale:**

The 2x2 Enhanced Detail widget addresses a key pain point in clinical documentation review: the need to click through to the full page to get sufficient context about a note. By providing:

1. **Longer Previews (250-300 chars)**: Clinicians can often determine note relevance without opening the full view
2. **Complete Metadata**: Full timestamps, credentials, and facility names support clinical decision-making
3. **Explicit Status**: Surface important status information (Amended, Retracted) directly in the widget
4. **Quality Over Quantity**: 3 notes with rich detail is more valuable than 4 notes with minimal context

This design leverages the additional vertical space to reduce cognitive load and minimize navigation clicks for the most common use case: "What are the most recent significant clinical notes?"

**Jinja2 Template:**
```html
<!-- Clinical Notes Widget Content (2x2 Enhanced Detail Layout) -->
<!-- Widget Header -->
<div class="widget__header">
    <div class="widget__title-group">
        <i class="fa-solid fa-file-medical widget__icon"></i>
        <h3 class="widget__title">Clinical Notes</h3>
    </div>
    {% if total_count > 0 %}
        <span class="badge badge--info">{{ total_count }} Total</span>
    {% endif %}
</div>

<!-- Widget Body -->
<div class="widget__body widget__body--enhanced">
    <div class="widget-notes widget-notes--2x2">
        {% if error %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">
                <i class="fa-solid fa-circle-exclamation"></i> Error loading notes
            </p>
        {% elif total_count == 0 %}
            <p class="text-muted" style="padding: 1rem; text-align: center;">No clinical notes recorded</p>
        {% else %}
            <!-- Notes List (Most Recent 3) -->
            <div class="notes-list-widget notes-list-widget--enhanced">
                {% for note in recent_notes[:3] %}
                <div class="note-item-widget note-item-widget--enhanced">
                    <!-- Note class as full text label -->
                    <div class="note-item-widget__class-label">
                        {{ note.note_class }}
                    </div>

                    <!-- Complete metadata line -->
                    <div class="note-item-widget__metadata-full">
                        <span class="note-item-widget__datetime">
                            {{ note.reference_datetime.strftime('%m/%d/%Y at %H:%M') }}
                        </span>
                        <span class="note-item-widget__separator">•</span>
                        <span class="note-item-widget__author-full">
                            {{ note.author_name }}{% if note.author_credentials %}, {{ note.author_credentials }}{% endif %}
                        </span>
                        <span class="note-item-widget__separator">•</span>
                        <span class="note-item-widget__facility-full">
                            {{ note.facility_name }}
                        </span>
                    </div>

                    <!-- Status display -->
                    <div class="note-item-widget__status">
                        <span class="note-status note-status--{{ note.status|lower|replace(' ', '-') }}">
                            Status: {{ note.status }}
                        </span>
                    </div>

                    <!-- Extended text preview (250-300 chars) -->
                    <div class="note-item-widget__preview-extended">
                        {{ note.text_preview_extended }}
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- View All Link -->
            <div class="widget-action">
                <a href="/patient/{{ patient_icn }}/notes" class="btn btn--link btn--sm">
                    <i class="fa-regular fa-arrow-up-right-from-square"></i>
                    View All Clinical Notes ({{ total_count }} total)
                </a>
            </div>
        {% endif %}
    </div>
</div>

<!-- Widget Footer -->
<div class="widget__footer"></div>
```

**Backend Data Requirements:**

The 2x2 widget requires an extended preview field in addition to the standard preview:

```python
# app/routes/notes.py (or app/routes/patient.py)

@router.get("/patient/{patient_icn}/notes/widget")
async def get_notes_widget(patient_icn: str, layout: str = "2x2"):
    """
    Fetch recent notes for dashboard widget.

    Args:
        patient_icn: Patient ICN
        layout: Widget layout ("2x1" or "2x2")

    Returns:
        Dict with recent_notes, total_count, layout-specific fields
    """
    # Fetch most recent 3-4 notes
    query = """
        SELECT
            note_id,
            note_title,
            note_class,
            reference_datetime,
            author_name,
            author_credentials,
            facility_name,
            status,
            text_preview,
            -- Extended preview for 2x2 layout
            CASE
                WHEN LENGTH(note_text) > 300 THEN SUBSTRING(note_text, 1, 300) || '...'
                ELSE note_text
            END AS text_preview_extended
        FROM patient_clinical_notes
        WHERE patient_icn = :patient_icn
        ORDER BY reference_datetime DESC
        LIMIT 4
    """

    # Execute query and return appropriate data based on layout
    recent_notes = execute_query(query, {"patient_icn": patient_icn})

    return {
        "recent_notes": recent_notes,
        "total_count": get_total_count(patient_icn),
        "layout": layout
    }
```

**CSS Styling Requirements:**

See Section 8.1.3 for complete CSS specifications including:
- `.widget--2x2` class for multi-row grid placement
- `.note-item-widget--enhanced` for enhanced detail styling
- `.note-item-widget__class-label` for full-text class labels
- `.note-item-widget__metadata-full` for complete metadata line
- `.note-item-widget__preview-extended` for longer previews
- Responsive adjustments for mobile/tablet breakpoints

---

#### 8.1.3 CSS Specifications for Dashboard Widgets

**File:** `app/static/styles.css`

**Multi-Row Widget Grid Support:**

```css
/* ============================================
   MULTI-ROW WIDGET SUPPORT
   ============================================ */

/* 2x2 Widget: 2 columns wide, 2 rows tall */
.widget--2x2 {
    grid-column: span 2;
    grid-row: span 2;
}

/* 1x2 Widget: 1 column wide, 2 rows tall */
.widget--1x2 {
    grid-column: span 1;
    grid-row: span 2;
}

/* Responsive: Tablet (2-column grid) */
@media (max-width: 1024px) and (min-width: 768px) {
    .widget--2x2 {
        grid-column: span 2;  /* Full width on 2-column grid */
        grid-row: span 2;
    }

    .widget--1x2 {
        grid-column: span 1;
        grid-row: span 2;
    }
}

/* Responsive: Mobile (1-column grid, stacked) */
@media (max-width: 767px) {
    .widget--2x2,
    .widget--1x2 {
        grid-column: span 1;  /* Single column */
        grid-row: auto;       /* Height adjusts to content */
    }
}
```

**Clinical Notes Widget Styling (2x1 Compact):**

```css
/* ============================================
   CLINICAL NOTES WIDGET - 2x1 COMPACT
   ============================================ */

.notes-list-widget {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.note-item-widget {
    padding: 0.75rem;
    background: #f9fafb;
    border-radius: 0.375rem;
    border-left: 3px solid #d1d5db;
}

.note-item-widget__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.375rem;
}

.note-badge {
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 0.25rem;
    font-weight: 600;
    text-transform: uppercase;
}

.note-badge--progress-notes {
    background: #BBDEFB;
    color: #1976D2;
}

.note-badge--consults {
    background: #E1BEE7;
    color: #7B1FA2;
}

.note-badge--discharge-summaries {
    background: #C8E6C9;
    color: #388E3C;
}

.note-badge--imaging {
    background: #FFE0B2;
    color: #F57C00;
}

.note-item-widget__date {
    font-size: 0.875rem;
    color: #6b7280;
    font-weight: 500;
}

.note-item-widget__meta {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 0.375rem;
}

.note-item-widget__preview {
    font-size: 0.875rem;
    color: #374151;
    line-height: 1.5;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
```

**Clinical Notes Widget Styling (2x2 Enhanced Detail):**

```css
/* ============================================
   CLINICAL NOTES WIDGET - 2x2 ENHANCED DETAIL
   ============================================ */

.widget-notes--2x2 {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.widget__body--enhanced {
    flex: 1;
    overflow-y: auto;
}

.notes-list-widget--enhanced {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.note-item-widget--enhanced {
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.5rem;
    border-left: 4px solid #3b82f6;
}

/* Note class as full-text label */
.note-item-widget__class-label {
    font-size: 1rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.5rem;
}

/* Complete metadata line */
.note-item-widget__metadata-full {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 0.375rem;
    line-height: 1.5;
}

.note-item-widget__datetime {
    font-weight: 500;
    color: #374151;
}

.note-item-widget__separator {
    margin: 0 0.375rem;
    color: #d1d5db;
}

.note-item-widget__author-full {
    font-weight: 500;
}

.note-item-widget__facility-full {
    font-style: normal;
}

/* Status display */
.note-item-widget__status {
    margin-bottom: 0.5rem;
}

.note-status {
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 0.25rem;
    font-weight: 600;
    display: inline-block;
}

.note-status--completed {
    background: #D1FAE5;
    color: #065F46;
}

.note-status--amended {
    background: #FEF3C7;
    color: #92400E;
}

.note-status--retracted {
    background: #FEE2E2;
    color: #991B1B;
}

/* Extended text preview */
.note-item-widget__preview-extended {
    font-size: 0.875rem;
    color: #374151;
    line-height: 1.6;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 4;  /* More lines for extended preview */
    -webkit-box-orient: vertical;
}

/* Responsive adjustments for 2x2 widget */
@media (max-width: 1024px) {
    .note-item-widget--enhanced {
        padding: 0.75rem;
    }

    .note-item-widget__class-label {
        font-size: 0.9375rem;
    }

    .note-item-widget__preview-extended {
        -webkit-line-clamp: 3;  /* Reduce preview lines on tablet */
    }
}

@media (max-width: 767px) {
    .notes-list-widget--enhanced {
        gap: 0.75rem;
    }

    .note-item-widget__metadata-full {
        font-size: 0.8125rem;
        line-height: 1.4;
    }

    .note-item-widget__preview-extended {
        font-size: 0.8125rem;
        -webkit-line-clamp: 3;  /* Further reduce on mobile */
    }
}
```

---

#### 8.1.4 Dashboard Widget Placement and Order

**Updated Dashboard Widget Order** (aligned with sidebar navigation):

1. Demographics (1x1)
2. Vitals (1x1)
3. Encounters (1x1)
4. Allergies (1x1)
5. Medications (2x1)
6. Laboratory Results (3x1)
7. Problems (1x1, placeholder)
8. Orders (1x1, placeholder)
9. Procedures (1x1, placeholder)
10. **Clinical Notes (2x1)** ← Wide widget (2 columns)
11. Immunizations (1x1, placeholder)
12. Imaging (1x1, placeholder)

**Grid Layout Example** (3-column desktop grid):

```
Row 1:  [ Demographics ] [ Vitals      ] [ Encounters  ]
Row 2:  [ Allergies    ] [ Medications -------------- ]
Row 3:  [ Labs ---------------------------------------- ]
Row 4:  [ Problems     ] [ Orders      ] [ Procedures  ]
Row 5:  [ Clinical Notes ------------- ] [ Immun.      ]
Row 6:  [ Imaging      ] [             ] [             ]
```

**Visual Explanation:**
- **Row 1**: Demographics (1x1), Vitals (1x1), Encounters (1x1)
- **Row 2**: Allergies (1x1), Medications (2x1 spanning columns 2-3)
- **Row 3**: Laboratory Results (3x1 spanning all 3 columns)
- **Row 4**: Problems (1x1), Orders (1x1), Procedures (1x1)
- **Row 5**: Clinical Notes (2x1 spanning columns 1-2), Immunizations (1x1)
- **Row 6**: Imaging (1x1) and empty cells

**Responsive Behavior:**

- **Desktop (≥1025px)**: 3-column grid as shown above
- **Tablet (768px-1024px)**: 2-column grid, Notes becomes full-width 2x1
- **Mobile (<768px)**: 1-column grid, all widgets stack vertically with standard heights

---

#### 8.1.5 Implementation Dependencies

**Files Requiring Updates:**

1. **`app/static/styles.css`**:
   - Add `.widget--2x2` and `.widget--1x2` classes (Section 8.1.3)
   - Add enhanced detail widget styling (`.note-item-widget--enhanced`, etc.)
   - Update responsive media queries to handle multi-row widgets
   - **Estimated effort**: 30 minutes

2. **`app/templates/dashboard.html`**:
   - Update widget order to match new sidebar navigation order
   - Add `widget--2x2` class to Clinical Notes widget container
   - Add `widget--1x2` class to Immunizations widget container
   - Verify grid layout handles multi-row widgets correctly
   - **Estimated effort**: 15 minutes

3. **`app/templates/partials/sidebar.html`** (or equivalent):
   - Update sidebar navigation order to match dashboard widget order
   - Ensure consistent ordering: Demographics → Vitals → Encounters → ... → Notes → Immunizations → Imaging
   - **Estimated effort**: 10 minutes

4. **`app/templates/partials/notes_widget.html`**:
   - Implement 2x2 Enhanced Detail layout as specified in Section 8.1.2
   - Add conditional logic for layout selection (if supporting both 2x1 and 2x2)
   - Include extended preview field and complete metadata rendering
   - **Estimated effort**: 45 minutes

5. **`app/routes/notes.py`** (or `app/routes/patient.py`):
   - Add `text_preview_extended` field to widget data query (250-300 chars)
   - Add `author_credentials` field if not already present
   - Ensure `facility_name` returns full facility name, not abbreviation
   - Add layout parameter to widget endpoint (optional, if supporting both layouts)
   - **Estimated effort**: 20 minutes

6. **`docs/spec/patient-dashboard-design.md`**:
   - Update widget specifications to document multi-row support
   - Add Clinical Notes (2x2) and Immunizations (1x2) to widget inventory
   - Update grid layout examples
   - **Estimated effort**: 15 minutes

**Total Implementation Effort (2x2 widget only)**: ~2.5 hours

**Testing Requirements:**
- Verify 2x2 widget displays correctly in 3-column desktop grid
- Test responsive behavior on tablet (2-column) and mobile (1-column)
- Verify widget order matches sidebar navigation order
- Test with patients having 0, 1, 2, and 3+ notes
- Verify extended preview truncation at 300 characters
- Test status display for Completed, Amended, and Retracted notes
- Verify "View All" link navigates correctly

---

### 8.2 Full Page View - Clinical Notes List

**File:** `app/templates/patient_notes.html`

**Layout:**
```
┌───────────────────────────────────────────────────────────────┐
│ Home > Dashboard > Clinical Notes                            │ (Breadcrumb)
│                                                               │
│ Clinical Notes                                                │ (Page title)
│ Patient: [Name] ([ICN])                                      │
├───────────────────────────────────────────────────────────────┤
│ Filters:                                                      │
│ [Note Type: All ▼] [Date Range: 90 days ▼] [Author: All ▼]  │
│ [Status: All ▼]  [Apply Filters]                            │
├───────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Date ▼ | Type | Author | Facility                      │  │ (Table headers - sortable)
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 12/28/2025 | [Progress Note] | Dr. Smith | Atlanta     │  │ (Note row - collapsed)
│ │ SUBJECTIVE: Patient presents for follow-up of HTN...   │  │ (Text preview)
│ │ [+ Expand to read full note]                            │  │ (Expand button)
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 12/15/2025 | [Consult] | Dr. Johnson | Atlanta         │  │ (Note row - expanded)
│ │ ┌───────────────────────────────────────────────────┐  │  │
│ │ │ CARDIOLOGY CONSULT                                 │  │  │ (Full note text)
│ │ │                                                     │  │  │
│ │ │ REASON FOR CONSULT: Evaluate for CAD              │  │  │
│ │ │                                                     │  │  │
│ │ │ HISTORY OF PRESENT ILLNESS:                       │  │  │
│ │ │ 68-year-old male with chest pain on exertion...   │  │  │
│ │ │                                                     │  │  │
│ │ │ [Full note text displayed here]                   │  │  │
│ │ │                                                     │  │  │
│ │ │ Cardiology Consult by: Dr. Johnson, MD            │  │  │
│ │ │ Date: 12/15/2025 14:00                            │  │  │
│ │ └───────────────────────────────────────────────────┘  │  │
│ │ [- Collapse note]                                       │  │ (Collapse button)
│ ├─────────────────────────────────────────────────────────┤  │
│ │ ...                                                     │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ [<< Prev]  Page 1 of 5  [Next >>]                           │ (Pagination)
└───────────────────────────────────────────────────────────────┘
```

**Features:**

1. **Filters**:
   - Note Type dropdown: All, Progress Notes, Consults, Discharge Summaries, Imaging
   - Date Range dropdown: 30 days, 90 days (default), 6 months, 1 year, All
   - Author dropdown: All, [List of unique authors for this patient]
   - Status dropdown: All, Completed, Unsigned, Retracted
   - HTMX: `hx-get="/patient/{icn}/notes?note_class=Consults&date_range=90" hx-target="#notes-table"`

2. **Sortable Columns**:
   - Date (default: descending)
   - Type (alphabetical)
   - Author (alphabetical)
   - HTMX: Click header to toggle sort order

3. **Row Details**:
   - **Collapsed state**:
     - Line 1: Date | Note Type Badge | Author | Facility
     - Line 2: Text preview (first 150 chars)
     - Line 3: "Expand to read full note" button
   - **Expanded state**:
     - Full note text in formatted box
     - Preserved line breaks and paragraph structure
     - Note metadata footer (author, date, cosigner if applicable)
     - "Collapse note" button

4. **Note Type Badges** (color-coded):
   - **Progress Note**: Blue background (#E3F2FD), blue text (#1976D2)
   - **Consult**: Purple background (#F3E5F5), purple text (#7B1FA2)
   - **Discharge Summary**: Green background (#E8F5E9), green text (#388E3C)
   - **Imaging**: Orange background (#FFF3E0), orange text (#F57C00)

5. **Pagination**:
   - 10 notes per page (default)
   - Options: 10, 20, 50 notes per page
   - HTMX: `hx-get="/patient/{icn}/notes?page=2&per_page=10"`

6. **Status Indicators**:
   - **COMPLETED**: No special indicator (default)
   - **UNSIGNED**: Warning badge (yellow)
   - **RETRACTED**: Error badge (red strikethrough)

**Jinja2 Template Excerpt:**
```html
{% extends "base.html" %}

{% block content %}
<!-- Page Header -->
<div class="page-header">
    <div class="page-header__breadcrumb">
        <a href="/" class="breadcrumb-link">
            <i class="fa-solid fa-house"></i>
            Dashboard
        </a>
        <i class="fa-solid fa-chevron-right"></i>
        <span class="breadcrumb-current">Clinical Notes</span>
    </div>
    <div class="page-header__title-group">
        <h1 class="page-header__title">Clinical Notes</h1>
        <p class="page-header__subtitle">Patient: {{ patient.name_display }} ({{ patient.icn }})</p>
    </div>
</div>

<!-- Filters -->
<div class="filters-container">
    <form hx-get="/patient/{{ patient.icn }}/notes" hx-target="#notes-table" hx-trigger="change">
        <div class="filters-row">
            <label>
                Note Type:
                <select name="note_class">
                    <option value="all" {% if note_class == 'all' %}selected{% endif %}>All</option>
                    <option value="Progress Notes" {% if note_class == 'Progress Notes' %}selected{% endif %}>Progress Notes</option>
                    <option value="Consults" {% if note_class == 'Consults' %}selected{% endif %}>Consults</option>
                    <option value="Discharge Summaries" {% if note_class == 'Discharge Summaries' %}selected{% endif %}>Discharge Summaries</option>
                    <option value="Imaging" {% if note_class == 'Imaging' %}selected{% endif %}>Imaging</option>
                </select>
            </label>

            <label>
                Date Range:
                <select name="date_range">
                    <option value="30" {% if date_range == '30' %}selected{% endif %}>Last 30 Days</option>
                    <option value="90" {% if date_range == '90' %}selected{% endif %}>Last 90 Days</option>
                    <option value="180" {% if date_range == '180' %}selected{% endif %}>Last 6 Months</option>
                    <option value="365" {% if date_range == '365' %}selected{% endif %}>Last Year</option>
                    <option value="all" {% if date_range == 'all' %}selected{% endif %}>All</option>
                </select>
            </label>

            <label>
                Author:
                <select name="author">
                    <option value="">All</option>
                    {% for auth in authors %}
                        <option value="{{ auth }}" {% if author == auth %}selected{% endif %}>{{ auth }}</option>
                    {% endfor %}
                </select>
            </label>

            <label>
                Status:
                <select name="status">
                    <option value="all" {% if status == 'all' %}selected{% endif %}>All</option>
                    <option value="COMPLETED" {% if status == 'COMPLETED' %}selected{% endif %}>Completed</option>
                    <option value="UNSIGNED" {% if status == 'UNSIGNED' %}selected{% endif %}>Unsigned</option>
                    <option value="RETRACTED" {% if status == 'RETRACTED' %}selected{% endif %}>Retracted</option>
                </select>
            </label>
        </div>
    </form>
</div>

<!-- Notes Table -->
<div id="notes-table">
    <div class="notes-list">
        {% if notes|length == 0 %}
            <div class="empty-state">
                <i class="fa-solid fa-file-medical fa-3x"></i>
                <p>No clinical notes found for the selected filters.</p>
            </div>
        {% else %}
            {% for note in notes %}
            <div class="note-row" id="note-{{ note.note_id }}">
                <!-- Note Header (always visible) -->
                <div class="note-row__header">
                    <div class="note-row__meta">
                        <span class="note-badge note-badge--{{ note.note_class|replace(' ', '-')|lower }}">
                            {{ note.note_class|replace(' Notes', '')|replace(' Summaries', '') }}
                        </span>
                        <span class="note-row__date">{{ note.reference_datetime.strftime('%m/%d/%Y %H:%M') }}</span>
                        <span class="note-row__author">{{ note.author_name }}</span>
                        <span class="note-row__facility">{{ note.facility_name }}</span>

                        {% if note.status != 'COMPLETED' %}
                            <span class="badge badge--{{ 'warning' if note.status == 'UNSIGNED' else 'error' }}">
                                {{ note.status }}
                            </span>
                        {% endif %}
                    </div>

                    <!-- Expand/Collapse Button -->
                    <button class="btn btn--icon btn--sm note-toggle"
                            hx-get="/patient/{{ patient.icn }}/notes/{{ note.note_id }}"
                            hx-target="#note-content-{{ note.note_id }}"
                            hx-swap="innerHTML"
                            onclick="this.classList.toggle('expanded')">
                        <i class="fa-solid fa-chevron-down"></i>
                    </button>
                </div>

                <!-- Note Preview (collapsed state) -->
                <div class="note-row__preview">
                    {{ note.text_preview }}
                </div>

                <!-- Note Full Text (expanded state - loaded on demand) -->
                <div id="note-content-{{ note.note_id }}" class="note-row__content" style="display: none;">
                    <!-- Content loaded via HTMX when expanded -->
                </div>
            </div>
            {% endfor %}
        {% endif %}
    </div>

    <!-- Pagination -->
    <div class="pagination">
        {% if page > 1 %}
            <a href="#" hx-get="/patient/{{ patient.icn }}/notes?page={{ page - 1 }}&per_page={{ per_page }}&note_class={{ note_class }}&date_range={{ date_range }}&author={{ author }}&status={{ status }}"
               hx-target="#notes-table"
               class="btn btn--secondary">
                <i class="fa-solid fa-chevron-left"></i> Previous
            </a>
        {% endif %}

        <span class="pagination__info">Page {{ page }} of {{ total_pages }}</span>

        {% if page < total_pages %}
            <a href="#" hx-get="/patient/{{ patient.icn }}/notes?page={{ page + 1 }}&per_page={{ per_page }}&note_class={{ note_class }}&date_range={{ date_range }}&author={{ author }}&status={{ status }}"
               hx-target="#notes-table"
               class="btn btn--secondary">
                Next <i class="fa-solid fa-chevron-right"></i>
            </a>
        {% endif %}

        <!-- Per Page Selector -->
        <select name="per_page"
                hx-get="/patient/{{ patient.icn }}/notes?page=1&note_class={{ note_class }}&date_range={{ date_range }}&author={{ author }}&status={{ status }}"
                hx-target="#notes-table"
                hx-trigger="change">
            <option value="10" {% if per_page == 10 %}selected{% endif %}>10 per page</option>
            <option value="20" {% if per_page == 20 %}selected{% endif %}>20 per page</option>
            <option value="50" {% if per_page == 50 %}selected{% endif %}>50 per page</option>
        </select>
    </div>
</div>
{% endblock %}
```

**Note Detail Partial Template:**
`app/templates/partials/note_detail.html`

```html
<!-- Full Note Text (loaded on demand) -->
<div class="note-full-text">
    <div class="note-full-text__header">
        <h4>{{ note.note_title }}</h4>
        {% if note.standard_title and note.standard_title != note.note_title %}
            <p class="text-muted">{{ note.standard_title }}</p>
        {% endif %}
    </div>

    <div class="note-full-text__body">
        <pre>{{ note.note_text }}</pre>
    </div>

    <div class="note-full-text__footer">
        <div class="note-full-text__metadata">
            <strong>Author:</strong> {{ note.author_name }}<br>
            {% if note.cosigner_name %}
                <strong>Cosigner:</strong> {{ note.cosigner_name }}<br>
            {% endif %}
            <strong>Date:</strong> {{ note.reference_datetime.strftime('%B %d, %Y at %H:%M') }}<br>
            <strong>Facility:</strong> {{ note.facility_name }}<br>
            <strong>Status:</strong> {{ note.status }}
        </div>
    </div>
</div>
```

### 8.3 CSS Styling

**File:** `app/static/styles.css` (add to existing CSS file)

```css
/* ===================================================================
   Clinical Notes Widget
   =================================================================== */
.notes-list-widget {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.note-item-widget {
    border-left: 3px solid #ccc;
    padding: 0.75rem 1rem;
    background: #fafafa;
    border-radius: 4px;
}

.note-item-widget__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.note-item-widget__date {
    font-size: 0.9rem;
    color: #666;
}

.note-item-widget__meta {
    font-size: 0.85rem;
    color: #555;
    margin-bottom: 0.5rem;
}

.note-item-widget__preview {
    font-size: 0.9rem;
    color: #333;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

/* Note Type Badges */
.note-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.note-badge--progress-notes {
    background: #E3F2FD;
    color: #1976D2;
}

.note-badge--consults {
    background: #F3E5F5;
    color: #7B1FA2;
}

.note-badge--discharge-summaries {
    background: #E8F5E9;
    color: #388E3C;
}

.note-badge--imaging {
    background: #FFF3E0;
    color: #F57C00;
}

/* ===================================================================
   Clinical Notes Full Page
   =================================================================== */
.filters-container {
    background: #f9f9f9;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1.5rem;
}

.filters-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    align-items: flex-end;
}

.filters-row label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.9rem;
    font-weight: 500;
}

.filters-row select {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.9rem;
    min-width: 150px;
}

/* Notes List */
.notes-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.note-row {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 1rem;
    background: #fff;
    transition: box-shadow 0.15s ease;
}

.note-row:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.note-row__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.note-row__meta {
    display: flex;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
}

.note-row__date {
    font-weight: 600;
    color: #333;
}

.note-row__author,
.note-row__facility {
    font-size: 0.9rem;
    color: #666;
}

.note-row__preview {
    font-size: 0.95rem;
    color: #555;
    line-height: 1.5;
    margin-bottom: 0.5rem;
    font-style: italic;
}

.note-toggle {
    transition: transform 0.2s ease;
}

.note-toggle.expanded {
    transform: rotate(180deg);
}

.note-row__content {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
}

/* Full Note Text Display */
.note-full-text__header h4 {
    margin: 0 0 0.5rem 0;
    color: #1976D2;
}

.note-full-text__body {
    background: #f5f5f5;
    border-left: 3px solid #1976D2;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}

.note-full-text__body pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    margin: 0;
}

.note-full-text__footer {
    background: #fafafa;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    font-size: 0.85rem;
}

.note-full-text__metadata {
    color: #666;
    line-height: 1.6;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #999;
}

.empty-state i {
    color: #ccc;
    margin-bottom: 1rem;
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
}

.pagination__info {
    font-size: 0.9rem;
    color: #666;
}

.pagination select {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.85rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .filters-row {
        flex-direction: column;
        gap: 0.75rem;
    }

    .filters-row label {
        width: 100%;
    }

    .filters-row select {
        width: 100%;
    }

    .note-row__meta {
        flex-direction: column;
        gap: 0.5rem;
        align-items: flex-start;
    }

    .pagination {
        flex-wrap: wrap;
    }
}
```

---

## 9. Implementation Roadmap

**Two-Phase Approach:**
- **Phase 1 (Days 1-8):** VistA/CDWWork implementation - Complete functional system with 100-150 notes
- **Phase 2 (Days 9-12):** Cerner/CDWWork2 implementation - Add 30-50 notes, no schema changes

**Total Estimated Time:** 11-13 days (49-58 hours)

---

## Phase 1: VistA/CDWWork Implementation (Days 1-7) ✅ COMPLETE

**Completion Date:** January 2, 2026
**Actual Implementation Time:** 7 days (Day 8 testing/polish merged into Days 1-7)

### Day 1: VistA CDW Schema and Seed Data ✅ COMPLETE

**Tasks:**
1. Create `mock/sql-server/cdwwork/create/Dim.TIUDocumentDefinition.sql`
2. Create `mock/sql-server/cdwwork/create/TIU.TIUDocument_8925.sql`
3. Create `mock/sql-server/cdwwork/create/TIU.TIUDocumentText.sql`
4. Create dimension seed data: `mock/sql-server/cdwwork/insert/Dim.TIUDocumentDefinition.sql` (13 note type definitions)
5. Generate 100-150 realistic clinical notes with SOAP structure
6. Create fact/text seed data: `mock/sql-server/cdwwork/insert/TIU.TIUDocument_8925.sql` and `TIU.TIUDocumentText.sql`
7. Apply schema changes to SQL Server container
8. Verify data with SQL queries

**Deliverables:**
- [x] `mock/sql-server/cdwwork/create/Dim.TIUDocumentDefinition.sql`
- [x] `mock/sql-server/cdwwork/create/TIU.TIUDocument_8925.sql`
- [x] `mock/sql-server/cdwwork/create/TIU.TIUDocumentText.sql`
- [x] `mock/sql-server/cdwwork/insert/Dim.TIUDocumentDefinition.sql`
- [x] `mock/sql-server/cdwwork/insert/TIU.TIUDocument_8925.sql`
- [x] `mock/sql-server/cdwwork/insert/TIU.TIUDocumentText.sql`
- [x] SQL verification queries document
- [x] 100+ realistic note texts generated (actual: 106 notes)

**Time Estimate:** 6-8 hours (note text generation is time-intensive)
**Actual Time:** ~7 hours

---

### Day 2: Bronze and Silver ETL ✅ COMPLETE

**Tasks:**
1. Create `etl/bronze_clinical_notes_vista.py`:
   - SQL query with JOINs to TIUDocumentText, TIUDocumentDefinition, SPatient, SStaff
   - Write to MinIO `bronze/cdwwork/clinical_notes`
2. Create `etl/silver_clinical_notes.py`:
   - Patient identity resolution (PatientSID → PatientICN)
   - Date standardization
   - Text cleaning (control characters, excessive whitespace)
   - Author name formatting and credentials extraction (from SStaff.Title)
   - Write to MinIO `silver/clinical_notes`
3. Test Bronze and Silver scripts
4. Verify Parquet file schemas with Polars

**Deliverables:**
- [x] `etl/bronze_clinical_notes_vista.py`
- [x] `etl/silver_clinical_notes.py`
- [x] Bronze Parquet file in MinIO: `bronze/cdwwork/clinical_notes`
- [x] Silver Parquet file in MinIO: `silver/clinical_notes`

**Time Estimate:** 4-5 hours
**Actual Time:** ~5 hours

---

### Day 3: Gold ETL and PostgreSQL Schema ✅ COMPLETE

**Tasks:**
1. Create `etl/gold_clinical_notes.py`:
   - Patient-centric grouping by ICN
   - Note sorting (most recent first)
   - Note count rollups by class
   - Text preview generation (150 chars)
   - Author list aggregation
   - Write to MinIO `gold/clinical_notes`
2. Create `db/ddl/create_patient_clinical_notes_table.sql`:
   - Table schema with AI columns (embedding_vector, ai_summary, key_entities)
   - Indexes
   - Apply to PostgreSQL container
3. Install pgvector extension in PostgreSQL (for vector embeddings)
4. Create `etl/load_clinical_notes.py`:
   - Read Gold Parquet
   - Flatten nested notes
   - Bulk load to PostgreSQL
5. Test full ETL pipeline end-to-end
6. Verify PostgreSQL data with SQL queries

**Deliverables:**
- [x] `etl/gold_clinical_notes.py`
- [x] `db/ddl/patient_clinical_notes.sql`
- [x] `etl/load_clinical_notes.py`
- [x] Gold Parquet file in MinIO: `gold/clinical_notes`
- [x] PostgreSQL table populated (106 rows)
- [x] pgvector extension installed

**Time Estimate:** 5-6 hours
**Actual Time:** ~6 hours

---

### Day 4: API Routes and Database Queries ✅ COMPLETE

**Tasks:**
1. Create `app/db/notes.py`:
   - `get_recent_notes()` (widget)
   - `get_notes_summary()` (counts by class)
   - `get_all_notes()` (full page with filters)
   - `get_note_detail()` (full text for expand)
   - `get_note_authors()` (author dropdown)
2. Create `app/routes/notes.py`:
   - `GET /patient/{icn}/notes/widget` (widget endpoint)
   - `GET /patient/{icn}/notes` (full page endpoint)
   - `GET /patient/{icn}/notes/{note_id}` (note detail endpoint)
3. Register router in `app/main.py`
4. Test endpoints with curl/Postman

**Deliverables:**
- [x] `app/db/notes.py`
- [x] `app/routes/notes.py`
- [x] Router registered in `app/main.py`
- [x] API endpoint tests (manual testing complete)

**Time Estimate:** 5-6 hours
**Actual Time:** ~5 hours

---

### Day 5: Widget UI Implementation (2x1 Compact) ✅ COMPLETE

**Implementation Note:** Originally designed as 2x2 Enhanced Detail, but implemented as 2x1 Compact for better dashboard density (see Section 1.4 for design decision rationale).

**Tasks:**
1. Create `app/templates/partials/notes_widget.html` (2x2 Enhanced Detail layout per Section 8.1.2):
   - Recent notes list (3 notes - balanced for 2-row height)
   - Full-text note class labels (not compact badges)
   - Complete metadata (full datetime, author with credentials, full facility name)
   - Explicit status display
   - Extended text previews (250-300 characters)
   - "View All Notes" link
2. Update `app/static/styles.css`:
   - Add multi-row widget support: `.widget--2x2` and `.widget--1x2` classes (Section 8.1.3)
   - Add 2x2 Enhanced Detail widget styles (`.note-item-widget--enhanced`, etc.)
   - Add responsive breakpoints for multi-row widgets
   - Add color-coded status badges (Completed, Amended, Retracted)
3. Update `app/templates/dashboard.html`:
   - Add notes widget with `widget--2x2` class
   - Reorder widgets to match sidebar navigation (Section 8.1.4):
     Demographics → Vitals → Encounters → Allergies → Medications → Labs → Problems → Orders → Procedures → Notes → Immunizations → Imaging
   - Update Immunizations widget to `widget--1x2` placeholder
4. Update `app/templates/partials/sidebar.html` (or equivalent):
   - Update navigation order to match dashboard widget order
   - Ensure Clinical Notes link positioned between Procedures and Immunizations
5. Test widget rendering with multiple patients:
   - Patient with all note types
   - Patient with only progress notes
   - Patient with no notes
   - Patient with 1-2 notes (verify layout doesn't break)
6. Verify HTMX behavior and responsive design:
   - Desktop (3-column): 2x2 widget occupies 2 cols × 2 rows
   - Tablet (2-column): 2x2 widget full-width
   - Mobile (1-column): widget stacks, auto height

**Deliverables:**
- [x] `app/templates/partials/notes_widget.html` (2x1 Compact - design change)
- [x] Updated `app/static/styles.css` (2x1 widget styles)
- [x] Updated `app/templates/dashboard.html` (widget order updated)
- [x] Updated sidebar navigation (navigation order updated)
- [x] Widget tested with multiple patient scenarios

**Time Estimate:** 5-6 hours (increased from 4-5 due to multi-row CSS and widget reordering)
**Actual Time:** ~5 hours

---

### Day 6-7: Full Page UI Implementation ✅ COMPLETE

**Tasks:**
1. Create `app/templates/patient_notes.html`:
   - Filter controls (note class, date range, author, status)
   - Notes table with collapsible rows
   - Sortable headers
   - Pagination controls
2. Create `app/templates/partials/note_detail.html`:
   - Full note text display
   - Note metadata footer
3. Update `app/static/styles.css` (add full page styles)
4. Implement HTMX interactions:
   - Filter changes reload table
   - Expand/collapse note rows
   - Pagination
5. Test with edge cases:
   - Patient with 50+ notes (multi-page)
   - Filter combinations
   - Different note types
6. Test expandable note text formatting
7. Accessibility review (keyboard navigation, screen readers)

**Deliverables:**
- [x] `app/templates/patient_notes.html` (with Status column - 6-column layout)
- [x] `app/templates/partials/note_detail.html`
- [x] Updated `app/static/styles.css` (comprehensive notes page styles + alignment fixes)
- [x] HTMX functionality verified (filters, sorting, pagination, expand/collapse)
- [x] Card-style layout with visual separation between notes
- [x] Column alignment issues resolved (header/content padding adjustments)
- [x] Status badge alignment fine-tuned (negative margin compensation)

**Time Estimate:** 8-10 hours (2 days)
**Actual Time:** ~10 hours

**Implementation Notes:**
- Added dedicated Status column to table (6-column grid: Date, Type, Status, Title, Author, Facility)
- Fixed column header alignment by matching padding between header (1.75rem) and row content (0.75rem body + 1rem collapsed)
- Fine-tuned Status badge alignment with -0.25rem negative left margin to compensate for badge internal padding
- Implemented card-style note rows with 0.75rem gap for better visual separation
- Fixed HTMX page duplication issue by adding `hx-select="#notes-table-container"` to all HTMX interactions
- Responsive design: Desktop (6 cols) → Tablet (5 cols, hide Facility) → Mobile (stacked)

---

### Day 8: Testing, Polish, and Documentation ✅ MERGED INTO DAYS 1-7

**Tasks:**
1. Write unit tests (`tests/test_clinical_notes.py`):
   - Database query functions
   - ETL transformations (Bronze, Silver, Gold)
2. Write integration tests:
   - API endpoint responses
   - Widget rendering
   - Full page rendering
   - Expandable rows
3. Manual testing checklist:
   - All 36 test patients
   - All note types display correctly
   - Filtering and sorting
   - Pagination
   - Expand/collapse functionality
   - Mobile/tablet responsive design
4. Update documentation:
   - `app/README.md` (add Clinical Notes routing example)
   - `docs/spec/med-z1-architecture.md` (confirm Pattern B decision)
   - This design document (mark sections complete)
5. Code review and cleanup

**Note:** Testing and polish were integrated throughout Days 1-7 rather than as a separate day.

**Deliverables:**
- [x] Manual testing completed throughout implementation
- [x] Integration testing via browser (all features verified)
- [x] Documentation updated (this document)
- [x] Code review and cleanup completed

**Time Estimate:** 6-7 hours
**Actual Time:** Merged into Days 1-7 (iterative testing approach)

---

## Phase 1 Implementation Summary

**Phase 1 Total Estimated Time:** 39-48 hours
**Phase 1 Actual Time:** ~38 hours (7 days, efficient implementation)

**Phase 1 Deliverables - ALL COMPLETE ✅:**
- ✅ Complete VistA Clinical Notes implementation (106 notes across 36 patients)
- ✅ Source-agnostic PostgreSQL schema (ready for Cerner Phase 2)
- ✅ Dashboard widget (2x1 Compact) displaying VistA notes with text preview
- ✅ Full page view with filtering (type, date range, author, status), sorting, pagination
- ✅ All ETL pipeline stages operational (Bronze/Silver/Gold/Load)
- ✅ Status column with dedicated display and proper alignment
- ✅ Card-style layout with visual separation between notes
- ✅ HTMX-powered dynamic interactions (no page reloads)
- ✅ Responsive design (desktop/tablet/mobile)
- ✅ Comprehensive manual testing and documentation
- ✅ **AI-Ready:** PostgreSQL table includes embedding_vector, ai_summary, key_entities columns for future AI integration

---

## Phase 2: Cerner/CDWWork2 Implementation (Days 9-12)

**Prerequisites:** Phase 1 complete and tested

**Note:** Phase 2 builds on existing infrastructure. No UI or PostgreSQL schema changes required!

### Day 9: Cerner CDW Schema and Seed Data

**Tasks:**
1. Create CDWWork2 database if not exists
2. Create `mock/sql-server/cdwwork2/create/Dim.ClinicalEventCode.sql`
3. Create `mock/sql-server/cdwwork2/create/Clinical.ClinicalEvent.sql`
4. Create `mock/sql-server/cdwwork2/create/Clinical.ClinicalEventBlob.sql`
5. Create dimension seed data: `mock/sql-server/cdwwork2/insert/Dim.ClinicalEventCode.sql` (13 Cerner note types)
6. Generate 30-50 realistic Cerner clinical notes with SOAP structure
   - Use Cerner-style titles (e.g., "Physician Note - General")
   - Map to same VHAEnterpriseStandardTitle as VistA
   - Include 3 patients with notes from both VistA and Cerner facilities
7. Create fact/text seed data: `mock/sql-server/cdwwork2/insert/Clinical.ClinicalEvent.sql` and `Clinical.ClinicalEventBlob.sql`
8. Apply schema changes to SQL Server container
9. Verify data with SQL queries

**Deliverables:**
- [ ] `mock/sql-server/cdwwork2/create/Dim.ClinicalEventCode.sql`
- [ ] `mock/sql-server/cdwwork2/create/Clinical.ClinicalEvent.sql`
- [ ] `mock/sql-server/cdwwork2/create/Clinical.ClinicalEventBlob.sql`
- [ ] `mock/sql-server/cdwwork2/insert/Dim.ClinicalEventCode.sql`
- [ ] `mock/sql-server/cdwwork2/insert/Clinical.ClinicalEvent.sql`
- [ ] `mock/sql-server/cdwwork2/insert/Clinical.ClinicalEventBlob.sql`
- [ ] 30-50 realistic Cerner note texts generated
- [ ] SQL verification queries for CDWWork2

**Time Estimate:** 4-5 hours (less than Phase 1 Day 1 due to template reuse)

---

### Day 10: Cerner Bronze and Silver ETL

**Tasks:**
1. Create `etl/bronze_clinical_notes_cerner.py`:
   - SQL query with JOINs to ClinicalEventBlob, ClinicalEventCode, SPatient, SStaff
   - Filter for EventClass = 'DOC'
   - Write to MinIO `bronze/cdwwork2/clinical_notes`
2. Update `etl/silver_clinical_notes.py`:
   - Add Cerner Bronze file reading
   - Implement field harmonization (EventCodeDesc → note_title, etc.)
   - Map Cerner ResultStatus → standard status ('AUTH' → 'COMPLETED')
   - Add source_system tagging ('Cerner')
   - Populate clinical_event_sid, set tiu_document_sid to NULL
   - Merge VistA and Cerner DataFrames
   - Write unified Silver file
3. Test Bronze and Silver scripts
4. Verify merged Silver Parquet contains both VistA and Cerner notes

**Deliverables:**
- [ ] `etl/bronze_clinical_notes_cerner.py`
- [ ] Updated `etl/silver_clinical_notes.py` (dual-source)
- [ ] Bronze Parquet file in MinIO: `bronze/cdwwork2/clinical_notes`
- [ ] Updated Silver Parquet file in MinIO: `silver/clinical_notes` (merged)

**Time Estimate:** 3-4 hours

---

### Day 11: Gold ETL and PostgreSQL Load

**Tasks:**
1. Update `etl/gold_clinical_notes.py` (if needed):
   - Verify Gold script handles merged Silver data correctly
   - Patient-centric grouping should work across both sources
   - Note count rollups should include Cerner notes
   - Test with merged Silver data
2. Update `etl/load_clinical_notes.py`:
   - Change from truncate to append mode (preserve existing VistA notes)
   - Load Cerner notes into same PostgreSQL table
   - Verify source_system check constraint is enforced
   - Verify tiu_document_sid is NULL for Cerner notes
   - Verify clinical_event_sid is populated for Cerner notes
3. Run full ETL pipeline (Bronze → Silver → Gold → PostgreSQL)
4. Verify PostgreSQL data with SQL queries:
   - Total count (should be 130-200 notes)
   - Count by source_system
   - Dual-system patients (3 patients should have notes from both)

**Deliverables:**
- [ ] Updated `etl/gold_clinical_notes.py` (if changes needed)
- [ ] Updated `etl/load_clinical_notes.py` (append mode)
- [ ] Gold Parquet file in MinIO: `gold/clinical_notes` (merged)
- [ ] PostgreSQL table with 130-200 notes (VistA + Cerner)
- [ ] Verification queries showing dual-source data

**Time Estimate:** 3-4 hours

---

### Day 12: UI Verification and Testing

**Tasks:**
1. Verify UI displays merged notes correctly (no code changes expected):
   - Dashboard widget shows most recent notes (may include Cerner notes)
   - Full page shows all notes sorted by date (VistA + Cerner interleaved)
   - Filtering by note class works across both sources
   - Pagination works with merged dataset
2. Test dual-system patients:
   - Patient ICN100003 (Atlanta VistA + Columbus Cerner)
   - Patient ICN100015 (Bay Pines VistA + Portland Cerner)
   - Patient ICN100028 (Dayton VistA + Puget Sound Cerner)
   - Verify notes display in unified timeline
3. Verify source_system column populated correctly (VistA vs Cerner)
4. Test filtering and sorting with 130-200 total notes
5. Performance testing:
   - Widget load time with dual-source data
   - Full page load time with 90-day filter
   - Query performance for dual-system patients
6. Update tests in `tests/test_clinical_notes.py`:
   - Add tests for Cerner notes
   - Add tests for dual-system patients
   - Add tests for source_system filtering
7. Update documentation:
   - Mark Phase 2 sections complete in design doc
   - Update `app/README.md` with dual-source notes

**Deliverables:**
- [ ] UI verified with dual-source data (no changes needed)
- [ ] Dual-system patient testing complete
- [ ] Performance testing results
- [ ] Updated test suite (Cerner coverage)
- [ ] Updated documentation

**Time Estimate:** 3-4 hours

---

**Phase 2 Total Estimated Time:** 13-17 hours (approximately 2-3 full working days)

**Phase 2 Deliverables:**
- ✅ Cerner CDWWork2 schema and seed data (30-50 notes)
- ✅ Cerner Bronze extraction pipeline
- ✅ Updated Silver layer with dual-source harmonization
- ✅ PostgreSQL table with 130-200 merged notes (no schema changes!)
- ✅ UI displays VistA and Cerner notes seamlessly
- ✅ 3 patients with notes from both systems (transferred care scenarios)
- ✅ Comprehensive testing with dual-source data
- ✅ Complete documentation

**Combined Phase 1 + Phase 2 Total Time:** 51-64 hours (approximately 7-9 full working days, or 10-13 calendar days with other responsibilities)

---

## 10. Testing Strategy

### 10.1 Unit Tests

**File:** `tests/test_clinical_notes.py`

**Coverage Areas:**
1. **Database Query Functions** (`app/db/notes.py`):
   - `test_get_recent_notes_returns_correct_limit()`
   - `test_get_recent_notes_excludes_unsigned_retracted()`
   - `test_get_notes_summary_counts_by_class()`
   - `test_get_all_notes_filters_by_class()`
   - `test_get_all_notes_filters_by_date_range()`
   - `test_get_all_notes_filters_by_author()`
   - `test_get_all_notes_pagination()`
   - `test_get_note_detail_returns_full_text()`
   - `test_get_note_authors_unique_list()`

2. **ETL Transformations**:
   - `test_bronze_extraction_row_count()`
   - `test_silver_text_cleaning()`
   - `test_silver_author_formatting()`
   - `test_gold_patient_grouping()`
   - `test_gold_text_preview_generation()`
   - `test_gold_note_class_counts()`

**Example Test:**
```python
import pytest
from app.db.notes import get_recent_notes, get_notes_summary

def test_get_recent_notes_returns_correct_limit():
    """Verify that get_recent_notes respects limit parameter."""
    patient_icn = "1000000001V123456"

    # Fetch with limit=4
    notes = get_recent_notes(patient_icn, limit=4)

    assert len(notes) <= 4, "Should return at most 4 notes"

    # Verify descending order by reference date
    ref_dates = [note['reference_datetime'] for note in notes]
    assert ref_dates == sorted(ref_dates, reverse=True), "Should be sorted by date descending"


def test_get_notes_summary_counts_by_class():
    """Verify note counts by class are accurate."""
    patient_icn = "1000000001V123456"

    summary = get_notes_summary(patient_icn)

    assert 'total' in summary
    assert 'Progress Notes' in summary
    assert 'Consults' in summary
    assert 'Discharge Summaries' in summary
    assert 'Imaging' in summary

    # Verify sum of classes equals total
    class_sum = (
        summary['Progress Notes'] +
        summary['Consults'] +
        summary['Discharge Summaries'] +
        summary['Imaging']
    )
    assert class_sum == summary['total'], "Sum of classes should equal total"
```

### 10.2 Integration Tests

**Coverage Areas:**
1. **API Endpoints**:
   - `test_widget_endpoint_returns_json()`
   - `test_widget_endpoint_excludes_unsigned_notes()`
   - `test_full_page_endpoint_renders_html()`
   - `test_full_page_filtering_by_class()`
   - `test_full_page_filtering_by_date_range()`
   - `test_full_page_filtering_by_author()`
   - `test_note_detail_endpoint_returns_full_text()`

2. **UI Rendering**:
   - `test_widget_html_contains_note_type_badges()`
   - `test_widget_html_contains_text_previews()`
   - `test_full_page_expandable_rows()`
   - `test_pagination_links_present()`

**Example Test:**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_widget_endpoint_returns_json():
    """Verify widget endpoint returns valid JSON."""
    patient_icn = "1000000001V123456"
    response = client.get(f"/patient/{patient_icn}/notes/widget")

    assert response.status_code == 200
    data = response.json()
    assert "patient_icn" in data
    assert "recent_notes" in data
    assert len(data["recent_notes"]) <= 4


def test_full_page_filtering_by_class():
    """Verify filtering by note class works correctly."""
    patient_icn = "1000000001V123456"
    response = client.get(f"/patient/{patient_icn}/notes?note_class=Consults")

    assert response.status_code == 200
    # Check HTML contains only Consult notes
    assert "Consults" in response.text or "Consult" in response.text
```

### 10.3 Manual Testing Checklist

**Pre-Deployment Checklist:**

- [ ] **Widget Display**:
  - [ ] Displays 3-4 most recent notes on dashboard
  - [ ] Note type badges color-coded correctly
  - [ ] Text previews truncated to ~150 chars
  - [ ] "View All Notes" link navigates to full page
  - [ ] Shows "No clinical notes recorded" for patients with no notes

- [ ] **Full Page View**:
  - [ ] All notes displayed correctly
  - [ ] Note type badges match note class
  - [ ] Text previews display in collapsed state
  - [ ] Expand/collapse functionality works
  - [ ] Full note text displays with preserved formatting

- [ ] **Filtering**:
  - [ ] Note Type filter: All, Progress Notes, Consults, Discharge Summaries, Imaging work correctly
  - [ ] Date Range filter: 30d, 90d, 6mo, 1yr, All work correctly
  - [ ] Author filter: Shows only authors for patient, filtering works
  - [ ] Status filter: All, Completed, Unsigned, Retracted work correctly
  - [ ] Filter combinations work (e.g., "Consults" + "90 days" + specific author)

- [ ] **Sorting**:
  - [ ] Date sorting (asc/desc)
  - [ ] Author sorting (alphabetical)
  - [ ] Type sorting (alphabetical)

- [ ] **Pagination**:
  - [ ] Pages show 10 notes each (default)
  - [ ] 10/20/50 per page options work
  - [ ] "Next" and "Previous" buttons work correctly
  - [ ] No pagination shown for patients with ≤10 notes

- [ ] **Data Accuracy**:
  - [ ] All 100-150 test notes display correctly
  - [ ] Note classes correctly assigned (Progress, Consult, Discharge, Imaging)
  - [ ] Author names display correctly
  - [ ] Dates display in correct format
  - [ ] Facility names and Sta3n values match
  - [ ] Unsigned notes show warning badge
  - [ ] Retracted notes show error badge

- [ ] **HTMX Functionality**:
  - [ ] Filter changes reload table without full page refresh
  - [ ] Expand/collapse loads full note text without full page refresh
  - [ ] Pagination loads new page without full page refresh
  - [ ] Sorting changes reload table without full page refresh

- [ ] **Responsive Design**:
  - [ ] Widget readable on mobile (320px width)
  - [ ] Full page table scrolls or stacks on small screens
  - [ ] Touch-friendly controls on tablet/mobile
  - [ ] Expandable rows work on mobile

- [ ] **Accessibility**:
  - [ ] Keyboard navigation works (tab through filters, expand buttons)
  - [ ] Note type badges have sufficient color contrast
  - [ ] Screen readers announce note class and status
  - [ ] Expand/collapse buttons accessible via keyboard

### 10.4 Test Data Coverage

**Patient Scenarios to Test:**

1. **Patient with all note types** (ICN: `1000000001V123456`):
   - Verify all 4 note classes present
   - Verify filtering by each class works
   - Verify note type badges display correctly

2. **Patient with many notes** (ICN: `1000000002V234567`):
   - 20+ notes spanning multiple pages
   - Verify pagination appears and works
   - Verify date range filtering reduces results appropriately

3. **Patient with only progress notes** (ICN: `1000000005V567890`):
   - Verify widget shows only progress note badges
   - Verify filtering by "Consults" returns empty

4. **Patient with unsigned notes** (ICN: `1000000010V111111`):
   - Verify unsigned notes show warning badge
   - Verify unsigned notes excluded from widget

5. **Patient with retracted note** (ICN: `1000000012V333333`):
   - Verify retracted note shows error badge with strikethrough
   - Verify retracted notes excluded from widget

6. **Patient with no notes** (ICN: `1000000036V999999`):
   - Verify widget shows "No clinical notes recorded"
   - Verify full page shows empty state message

7. **Patient with cosigned notes** (ICN: `1000000008V888888`):
   - Verify cosigner name displays in note detail
   - Verify cosigner appears in metadata footer

---

## 11. Future Enhancements

### 11.1 Phase 2: Full-Text Search

**Scope:**
- Search across note text content
- Keyword highlighting in results
- Boolean operators (AND, OR, NOT)
- Phrase search ("exact match")

**Implementation:**
- PostgreSQL full-text search using `tsvector` and `tsquery`
- GIN index on `to_tsvector('english', note_text)`
- Search input field in filter bar
- Highlighted search terms in note text display

**Estimated Effort:** 3-4 days

### 11.2 Phase 2: AI-Powered Summarization

**Scope:**
- Auto-generate concise summaries of long notes (200-500 words → 2-3 sentences)
- Display summaries in collapsed state instead of raw text preview
- "Read AI Summary" vs "Read Full Note" options
- Batch summarization job for historical notes

**Implementation:**
- OpenAI GPT-4 or Claude API for summarization
- Populate `ai_summary` column in database
- ETL job to generate summaries for new notes
- UI toggle between summary and full text

**Estimated Effort:** 5-6 days

### 11.3 Phase 2: Named Entity Recognition (NER)

**Scope:**
- Extract structured data from note text:
  - Medications mentioned
  - Diagnoses/conditions
  - Procedures performed
  - Lab results referenced
- Store in `key_entities` JSONB column
- Display as structured metadata in note detail view
- Enable filtering by entity (e.g., "Show all notes mentioning Lisinopril")

**Implementation:**
- SpaCy medical NER model (scispacy) or cloud NER API
- Batch extraction job for historical notes
- JSONB query support in PostgreSQL
- UI badges for extracted entities

**Estimated Effort:** 6-8 days

### 11.4 Phase 2: Semantic Search (Vector Embeddings)

**Scope:**
- "Find notes similar to this one" functionality
- Semantic search (meaning-based, not keyword-based)
- Support AI Insights questions like "What notes discuss cardiovascular issues?"

**Implementation:**
- Generate vector embeddings for all notes using OpenAI ada-002
- Populate `embedding_vector` column
- Create ivfflat index in pgvector
- Cosine similarity search
- Integrate with AI Insights chat interface

**Estimated Effort:** 6-8 days

### 11.5 Phase 3: VistA RPC Broker Overlay (T-0 Notes)

**Scope:**
- Fetch today's notes from VistA RPC Broker (not yet in CDW)
- Merge with historical PostgreSQL data
- User-controlled "Refresh from VistA" button
- Visual indicator for VistA-sourced notes

**Implementation:**
- VistA RPC: `TIU GET RECORD LIST` (or equivalent)
- Client-side merge logic (Gold layer + VistA)
- Cache in session (similar to Vitals Vista overlay)
- UI: "Refresh VistA" button, "Updated just now" badge

**Estimated Effort:** 5-7 days (depends on VistA RPC availability)

### 11.6 Phase 3: Note Addenda and Amendments

**Scope:**
- Display note addenda (additional information added after signing)
- Show amendment history (corrections to original note)
- Version timeline for amended notes

**Implementation:**
- Additional CDW table: `TIU.TIUDocumentAddendum`
- Link addenda to parent note
- UI: Expandable "Addenda" section below note text
- Timeline view for amendments

**Estimated Effort:** 4-5 days

### 11.7 Phase 3: Note Export (PDF, Print)

**Scope:**
- Export individual notes to PDF
- Print-friendly formatting
- Batch export multiple notes

**Implementation:**
- Python PDF generation library (ReportLab, WeasyPrint)
- Print CSS media queries
- Download endpoint: `GET /patient/{icn}/notes/{note_id}/export`

**Estimated Effort:** 2-3 days

### 11.8 Long-Term: Note Authoring (Out of Scope for Med-Z1 v1)

**Scope:**
- Create new clinical notes
- Note templates (SOAP, H&P, Procedure Note)
- Electronic signature workflow
- Cosigner/attending approval

**Implementation:**
- Full CRUD operations on notes
- Rich text editor (TinyMCE, CKEditor)
- Workflow state machine (Draft → Unsigned → Completed)
- Integration with VA PKI for electronic signature

**Estimated Effort:** 4-6 weeks (major feature)

---

## 12. Appendices

### Appendix A: VistA TIU File Structure Reference

**VistA File #8925 (TIU DOCUMENT)**

Key fields (mapped to CDW):
- `.01` - Document IEN (→ TIUDocumentIEN)
- `.02` - Patient IEN (→ PatientSID via lookup)
- `.03` - Visit IEN (→ VisitSID)
- `.04` - Author IEN (→ AuthorSID)
- `.05` - Document Definition IEN (→ DocumentDefinitionSID)
- `1201` - Status (→ Status: COMPLETED, UNSIGNED, RETRACTED)
- `1301` - Reference Date/Time (→ ReferenceDateTime)
- `1401` - Entry Date/Time (→ EntryDateTime)
- `1204` - Cosigner IEN (→ CosignerSID)

**VistA File #8925.1 (TIU DOCUMENT DEFINITION)**

Key fields:
- `.01` - Name (→ TIUDocumentTitle)
- `.04` - Type (CLASS: PROGRESS NOTES, DISCHARGE SUMMARIES, etc. → DocumentClass)
- `.07` - VHA Enterprise Standard Title (→ VHAEnterpriseStandardTitle)
- `.1` - Inactive Flag (→ InactiveFlag)

### Appendix B: Common Note Type Definitions

**Progress Notes:**
- General Medicine Progress Note
- Cardiology Progress Note
- Primary Care Note
- Specialty Clinic Note
- Nurse Practitioner Note
- Resident Progress Note

**Consults:**
- Cardiology Consultation
- Nephrology Consultation
- Psychiatry Consultation
- Neurology Consultation
- Pulmonology Consultation
- Gastroenterology Consultation

**Discharge Summaries:**
- Inpatient Discharge Summary
- Observation Discharge Summary
- ICU Discharge Summary

**Imaging Reports:**
- Chest X-Ray Report
- CT Scan Report
- MRI Report
- Ultrasound Report

### Appendix C: Sample Note Text Templates

**Progress Note (SOAP Format):**
```
SUBJECTIVE:
Patient presents for follow-up of hypertension and type 2 diabetes mellitus.
Reports medication compliance with Lisinopril 20mg daily and Metformin 1000mg BID.
Blood sugars have been running 120-140 mg/dL fasting.
Denies chest pain, shortness of breath, or peripheral edema.

OBJECTIVE:
Vitals: BP 138/82, HR 72, Temp 98.4°F, O2 Sat 97% on RA
Weight: 185 lbs (unchanged from last visit)
Physical Exam:
- General: Alert, oriented x3, no acute distress
- Cardiovascular: Regular rate and rhythm, no murmurs
- Respiratory: Clear to auscultation bilaterally
- Extremities: No edema, pulses 2+ bilaterally

Recent Labs (12/15/2025):
- HgbA1c: 7.2%
- BMP: Within normal limits, Creatinine 1.1
- Lipid Panel: LDL 102, HDL 48, Triglycerides 145

ASSESSMENT:
1. Hypertension - Well controlled on current regimen
2. Type 2 Diabetes Mellitus - Suboptimal control (HgbA1c 7.2%)
3. Hyperlipidemia - At goal

PLAN:
1. Continue Lisinopril 20mg daily
2. Increase Metformin to 1000mg TID with meals (total 3000mg/day)
3. Continue Atorvastatin 40mg daily
4. Recheck HgbA1c in 3 months
5. Follow up in 3 months or sooner if problems
6. Patient education on diabetic diet and exercise

Electronically signed by: John Smith, MD
Date: 12/28/2025 10:45
```

**Consult Note:**
```
CARDIOLOGY CONSULTATION NOTE

REASON FOR CONSULT: Evaluate for coronary artery disease

HISTORY OF PRESENT ILLNESS:
68-year-old male veteran with chest pain on exertion for past 2 months.
Pain described as pressure-like, substernal, radiating to left arm.
Occurs with walking >2 blocks, relieved with rest after 5-10 minutes.
No pain at rest. No associated dyspnea, diaphoresis, or nausea.

PAST MEDICAL HISTORY:
- Hypertension
- Type 2 Diabetes Mellitus
- Hyperlipidemia
- Former smoker (quit 10 years ago, 30 pack-year history)

MEDICATIONS:
- Lisinopril 20mg daily
- Metformin 1000mg BID
- Atorvastatin 40mg daily
- Aspirin 81mg daily

PHYSICAL EXAMINATION:
Vitals: BP 142/88, HR 76, RR 16, O2 Sat 98%
Cardiovascular: Regular rate and rhythm, no murmurs, rubs, or gallops
Respiratory: Clear to auscultation bilaterally
Peripheral pulses: 2+ throughout, no edema

DIAGNOSTIC DATA:
EKG: Normal sinus rhythm, no acute ST-T changes
Recent Stress Test (12/10/2025): Positive for reversible inferior wall defect
Echo: LVEF 55%, mild LVH, no valvular abnormalities

IMPRESSION:
1. Stable angina, likely coronary artery disease
2. Positive stress test with inferior wall ischemia
3. Multiple cardiac risk factors (HTN, DM, HLD, former smoker)

RECOMMENDATIONS:
1. Recommend cardiac catheterization to evaluate coronary anatomy
2. Start Beta Blocker: Metoprolol 25mg BID
3. Continue antiplatelet therapy with Aspirin
4. Consider adding sublingual Nitroglycerin for chest pain episodes
5. Discuss revascularization options (PCI vs CABG) based on cath findings
6. Will follow patient throughout hospitalization

Thank you for this consultation.

Cardiology Consult completed by: Mary Johnson, MD
Date: 12/15/2025 14:30
```

**Discharge Summary:**
```
DISCHARGE SUMMARY

ADMISSION DATE: 11/17/2025
DISCHARGE DATE: 11/20/2025

ADMITTING DIAGNOSIS: Community-acquired pneumonia
DISCHARGE DIAGNOSIS: Community-acquired pneumonia, resolved

HOSPITAL COURSE:
72-year-old male admitted with 5 days of productive cough, fever, and dyspnea.
Chest X-ray showed right lower lobe infiltrate consistent with pneumonia.
Blood cultures negative. Sputum culture grew Streptococcus pneumoniae.

Treated with IV Ceftriaxone 1g daily for 3 days, then transitioned to oral
Amoxicillin-Clavulanate 875mg BID to complete 7-day course.

Fever resolved by hospital day 2. Oxygen saturation improved from 88% on RA
at admission to 95% on RA by discharge. Repeat chest X-ray on day 3 showed
improvement of infiltrate.

DISCHARGE MEDICATIONS:
1. Amoxicillin-Clavulanate 875mg PO BID x 4 more days (7 days total)
2. Lisinopril 20mg PO daily (home medication)
3. Metformin 1000mg PO BID (home medication)
4. Atorvastatin 40mg PO daily (home medication)

DISCHARGE INSTRUCTIONS:
- Complete full course of antibiotics
- Rest and increase fluid intake
- Return to ER if fever >101°F, worsening shortness of breath, or chest pain
- No heavy lifting or strenuous activity for 1 week
- Follow low-sodium, diabetic diet

FOLLOW-UP:
- Primary Care follow-up in 1 week
- Repeat Chest X-ray in 4-6 weeks to ensure resolution of infiltrate

Discharge summary completed by: David Williams, MD
Date: 11/20/2025 11:00
```

**Imaging Report:**
```
RADIOLOGY REPORT

EXAM: Chest X-Ray, 2 views (PA and Lateral)
DATE: 12/20/2025
PATIENT: [Name], ICN: 1000000001V123456

INDICATION: Chronic cough, rule out infiltrate

TECHNIQUE:
PA and lateral views of the chest were obtained.

COMPARISON:
Prior chest X-ray dated 06/15/2025

FINDINGS:
Lungs: Clear. No focal infiltrate, mass, or effusion.
Heart: Normal size and contour.
Mediastinum: Unremarkable. No widening or lymphadenopathy.
Bones: Degenerative changes of the thoracic spine, stable.
Soft Tissues: Unremarkable.

IMPRESSION:
1. No acute cardiopulmonary process.
2. Stable degenerative changes of thoracic spine.

Reported by: Robert Davis, MD (Radiology)
Date: 12/20/2025 15:45
```

### Appendix D: SQL Verification Queries

**Check Total Note Count:**
```sql
SELECT COUNT(*) AS TotalNotes
FROM TIU.TIUDocument_8925;
```

**Check Note Count by Class:**
```sql
SELECT
    def.DocumentClass,
    COUNT(*) AS NoteCount
FROM TIU.TIUDocument_8925 d
LEFT JOIN Dim.TIUDocumentDefinition def ON d.DocumentDefinitionSID = def.DocumentDefinitionSID
GROUP BY def.DocumentClass
ORDER BY NoteCount DESC;
```

**Check Patient with Most Notes:**
```sql
SELECT TOP 1
    p.PatientICN,
    p.PatientName,
    COUNT(*) AS NoteCount
FROM TIU.TIUDocument_8925 d
LEFT JOIN SPatient.SPatient p ON d.PatientSID = p.PatientSID
GROUP BY p.PatientICN, p.PatientName
ORDER BY NoteCount DESC;
```

**Check Notes by Status:**
```sql
SELECT
    Status,
    COUNT(*) AS NoteCount
FROM TIU.TIUDocument_8925
GROUP BY Status
ORDER BY NoteCount DESC;
```

**Check Sample Note Text:**
```sql
SELECT TOP 5
    d.TIUDocumentSID,
    p.PatientICN,
    def.TIUDocumentTitle,
    def.DocumentClass,
    d.ReferenceDateTime,
    LEFT(txt.DocumentText, 200) AS TextPreview
FROM TIU.TIUDocument_8925 d
LEFT JOIN SPatient.SPatient p ON d.PatientSID = p.PatientSID
LEFT JOIN Dim.TIUDocumentDefinition def ON d.DocumentDefinitionSID = def.DocumentDefinitionSID
LEFT JOIN TIU.TIUDocumentText txt ON d.TIUDocumentSID = txt.TIUDocumentSID
ORDER BY d.ReferenceDateTime DESC;
```

### Appendix E: CDWWork2 (Cerner/Oracle Health) Schema Specifications

**Phase 2 Implementation Reference**

This appendix provides complete specifications for the CDWWork2 (Cerner Millennium / Oracle Health) mock database schemas. These schemas will be implemented in Phase 2 and complement the VistA (CDWWork) schemas defined in Section 4.

---

#### E.1 Cerner Architecture Overview

**Key Differences from VistA:**
- Cerner Millennium uses **Clinical Events** instead of TIU Documents
- Notes are stored as Clinical Events with `EventClass = 'DOC'`
- Event codes (similar to TIU Document Definitions) define note types
- Text stored in "Blob" tables (Binary Large Objects / CLOBs)

**Cerner to VistA Equivalents:**
| Cerner Table | VistA Equivalent | Purpose |
|--------------|------------------|---------|
| `Dim.ClinicalEventCode` | `Dim.TIUDocumentDefinition` | Note type definitions |
| `Clinical.ClinicalEvent` | `TIU.TIUDocument_8925` | Note metadata (fact table) |
| `Clinical.ClinicalEventBlob` | `TIU.TIUDocumentText` | Note content (text) |

---

#### E.2 Dim.ClinicalEventCode (Note Type Definitions)

**Purpose:** Maps Cerner event codes to standardized note classifications. Equivalent to `Dim.TIUDocumentDefinition`.

**DDL Script:** `mock/sql-server/cdwwork2/create/Dim.ClinicalEventCode.sql`

```sql
USE CDWWork2;
GO

-- Create Dim schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Dim')
BEGIN
    EXEC('CREATE SCHEMA Dim');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Dim.ClinicalEventCode', 'U') IS NOT NULL
    DROP TABLE [Dim].[ClinicalEventCode];
GO

-- Create ClinicalEventCode dimension table
CREATE TABLE [Dim].[ClinicalEventCode] (
    -- Primary key
    [EventCodeSID] INT IDENTITY(1,1) PRIMARY KEY,

    -- Event identification
    [EventCode] VARCHAR(50) NOT NULL,              -- Cerner Code (e.g., "72000", "72100")
    [EventCodeDesc] VARCHAR(200) NOT NULL,         -- The Title (e.g., "Physician Note - General")
    [EventClass] VARCHAR(50) DEFAULT 'DOC',        -- Filter for 'DOC' to find notes

    -- Standardization (maps to same VHA titles as VistA!)
    [VHAEnterpriseStandardTitle] VARCHAR(200),     -- e.g., "Physician Progress Note"
    [DocumentClass] VARCHAR(100),                  -- 'Progress Notes', 'Consults', 'Discharge Summaries', 'Imaging'

    -- Status
    [InactiveFlag] CHAR(1) DEFAULT 'N',            -- 'Y' if retired, 'N' if active

    -- Metadata
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),
    [ModifiedDate] DATETIME2(0) DEFAULT GETDATE()
);
GO

-- Create indexes
SET QUOTED_IDENTIFIER ON;
GO

CREATE NONCLUSTERED INDEX [IX_ClinicalEventCode_EventClass]
    ON [Dim].[ClinicalEventCode] ([EventClass])
    WHERE [EventClass] IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX [IX_ClinicalEventCode_EventCode]
    ON [Dim].[ClinicalEventCode] ([EventCode]);
GO

CREATE NONCLUSTERED INDEX [IX_ClinicalEventCode_DocumentClass]
    ON [Dim].[ClinicalEventCode] ([DocumentClass])
    WHERE [DocumentClass] IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX [IX_ClinicalEventCode_StandardTitle]
    ON [Dim].[ClinicalEventCode] ([VHAEnterpriseStandardTitle])
    WHERE [VHAEnterpriseStandardTitle] IS NOT NULL;
GO
```

**Seed Data:** `mock/sql-server/cdwwork2/insert/Dim.ClinicalEventCode.sql`

```sql
USE CDWWork2;
GO

SET IDENTITY_INSERT [Dim].[ClinicalEventCode] ON;

INSERT INTO [Dim].[ClinicalEventCode]
(EventCodeSID, EventCode, EventCodeDesc, EventClass, VHAEnterpriseStandardTitle, DocumentClass)
VALUES
-- Progress Notes (Cerner-style naming)
(1000, '72000', 'Physician Note - General', 'DOC', 'Physician Progress Note', 'Progress Notes'),
(1001, '72010', 'Physician Note - Cardiology', 'DOC', 'Cardiology Progress Note', 'Progress Notes'),
(1002, '72020', 'Primary Care Provider Note', 'DOC', 'Primary Care Progress Note', 'Progress Notes'),
(1003, '72030', 'Specialty Clinic Note', 'DOC', 'Specialty Care Progress Note', 'Progress Notes'),

-- Consults (Cerner-style naming)
(1100, '73000', 'Consult Note - Cardiology', 'DOC', 'Cardiology Consultation Note', 'Consults'),
(1101, '73010', 'Consult Note - Nephrology', 'DOC', 'Nephrology Consultation Note', 'Consults'),
(1102, '73020', 'Consult Note - Psychiatry', 'DOC', 'Psychiatry Consultation Note', 'Consults'),
(1103, '73030', 'Consult Note - Neurology', 'DOC', 'Neurology Consultation Note', 'Consults'),

-- Discharge Summaries (Cerner-style naming)
(1200, '74000', 'Discharge Summary - Inpatient', 'DOC', 'Inpatient Discharge Summary', 'Discharge Summaries'),
(1201, '74010', 'Discharge Summary - Observation', 'DOC', 'Observation Discharge Summary', 'Discharge Summaries'),

-- Imaging Reports (Cerner-style naming)
(1300, '75000', 'Radiology Report - Chest X-Ray', 'DOC', 'Radiology Report - Chest X-Ray', 'Imaging'),
(1301, '75010', 'Radiology Report - CT Scan', 'DOC', 'Radiology Report - CT Scan', 'Imaging'),
(1302, '75020', 'Radiology Report - MRI', 'DOC', 'Radiology Report - MRI', 'Imaging');

SET IDENTITY_INSERT [Dim].[ClinicalEventCode] OFF;
GO
```

---

#### E.3 Clinical.ClinicalEvent (Note Metadata - Fact Table)

**Purpose:** Stores clinical note metadata. Equivalent to `TIU.TIUDocument_8925`.

**DDL Script:** `mock/sql-server/cdwwork2/create/Clinical.ClinicalEvent.sql`

```sql
USE CDWWork2;
GO

-- Create Clinical schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Clinical')
BEGIN
    EXEC('CREATE SCHEMA Clinical');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Clinical.ClinicalEvent', 'U') IS NOT NULL
    DROP TABLE [Clinical].[ClinicalEvent];
GO

-- Create ClinicalEvent fact table
CREATE TABLE [Clinical].[ClinicalEvent] (
    -- Primary key
    [ClinicalEventSID] BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Foreign keys
    [PatientSID] BIGINT NOT NULL,                  -- FK to SPatient.SPatient (shared with CDWWork)
    [EventCodeSID] INT NOT NULL,                   -- FK to Dim.ClinicalEventCode
    [VisitSID] BIGINT NULL,                        -- FK to Encounter (Inpatient or Outpatient)

    -- Temporal data (Cerner field names)
    [EventEndDateTime] DATETIME2(3) NOT NULL,      -- Equivalent to ReferenceDateTime (clinical date)
    [PerformedDateTime] DATETIME2(3) NOT NULL,     -- Equivalent to EntryDateTime (when authored)

    -- Status and workflow (Cerner terminology)
    [ResultStatus] VARCHAR(50) DEFAULT 'AUTH',     -- 'AUTH' (Authenticated/Verified) = COMPLETED
                                                   -- 'IN ERROR' = RETRACTED
                                                   -- 'MODIFIED' = AMENDED

    -- Authorship (Cerner field names)
    [VerifiedByStaffSID] BIGINT NULL,              -- Equivalent to AuthorSID (primary author)
    [CosignStaffSID] BIGINT NULL,                  -- Equivalent to CosignerSID

    -- Administrative
    [Sta3n] SMALLINT NOT NULL,                     -- VA Station Number

    -- Metadata
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),
    [ModifiedDate] DATETIME2(0) DEFAULT GETDATE(),

    -- Foreign key constraint
    CONSTRAINT FK_ClinicalEvent_EventCode FOREIGN KEY ([EventCodeSID])
        REFERENCES [Dim].[ClinicalEventCode] ([EventCodeSID])
);
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

-- Index on PatientSID for patient-centric queries
CREATE NONCLUSTERED INDEX [IX_ClinicalEvent_PatientSID]
    ON [Clinical].[ClinicalEvent] ([PatientSID]);
GO

-- Composite index for patient events sorted by date
CREATE NONCLUSTERED INDEX [IX_ClinicalEvent_PatientSID_EventEndDateTime]
    ON [Clinical].[ClinicalEvent] ([PatientSID], [EventEndDateTime] DESC);
GO

-- Index on EventEndDateTime for date range queries
CREATE NONCLUSTERED INDEX [IX_ClinicalEvent_EventEndDateTime]
    ON [Clinical].[ClinicalEvent] ([EventEndDateTime] DESC);
GO

-- Index on Sta3n for facility queries
CREATE NONCLUSTERED INDEX [IX_ClinicalEvent_Sta3n]
    ON [Clinical].[ClinicalEvent] ([Sta3n]);
GO

-- Index on ResultStatus for filtering
CREATE NONCLUSTERED INDEX [IX_ClinicalEvent_ResultStatus]
    ON [Clinical].[ClinicalEvent] ([ResultStatus])
    WHERE [ResultStatus] IS NOT NULL;
GO

-- Index on VerifiedByStaffSID for author filtering
CREATE NONCLUSTERED INDEX [IX_ClinicalEvent_VerifiedByStaffSID]
    ON [Clinical].[ClinicalEvent] ([VerifiedByStaffSID])
    WHERE [VerifiedByStaffSID] IS NOT NULL;
GO
```

---

#### E.4 Clinical.ClinicalEventBlob (Note Content)

**Purpose:** Stores the actual clinical narrative text. Equivalent to `TIU.TIUDocumentText`.

**DDL Script:** `mock/sql-server/cdwwork2/create/Clinical.ClinicalEventBlob.sql`

```sql
USE CDWWork2;
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Clinical.ClinicalEventBlob', 'U') IS NOT NULL
    DROP TABLE [Clinical].[ClinicalEventBlob];
GO

-- Create ClinicalEventBlob table
CREATE TABLE [Clinical].[ClinicalEventBlob] (
    -- Foreign key to ClinicalEvent
    [ClinicalEventSID] BIGINT NOT NULL,

    -- Note content
    [EventBlobText] VARCHAR(MAX),                  -- Full clinical narrative
    [CompressionMethod] VARCHAR(20) DEFAULT 'NONE', -- 'NONE' for mock environment

    -- Metadata
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),

    -- Primary key and foreign key constraint
    CONSTRAINT PK_ClinicalEventBlob PRIMARY KEY ([ClinicalEventSID]),
    CONSTRAINT FK_ClinicalEventBlob_Event FOREIGN KEY ([ClinicalEventSID])
        REFERENCES [Clinical].[ClinicalEvent] ([ClinicalEventSID])
);
GO
```

---

#### E.5 Field Mapping Reference (VistA ↔ Cerner)

**Critical for Silver Layer Harmonization**

| Standard Field | VistA Source | Cerner Source | Transformation Notes |
|----------------|--------------|---------------|----------------------|
| `source_system` | `'VistA'` (constant) | `'Cerner'` (constant) | Hardcoded based on source |
| `tiu_document_sid` | `TIUDocumentSID` | `NULL` | Only populated for VistA |
| `clinical_event_sid` | `NULL` | `ClinicalEventSID` | Only populated for Cerner |
| `note_title` | `TIUDocumentTitle` | `EventCodeDesc` | Direct mapping |
| `note_class` | `DocumentClass` | `DocumentClass` | Both map to same 4 classes |
| `standard_title` | `VHAEnterpriseStandardTitle` | `VHAEnterpriseStandardTitle` | Same field name in both! |
| `reference_datetime` | `ReferenceDateTime` | `EventEndDateTime` | Direct mapping |
| `entry_datetime` | `EntryDateTime` | `PerformedDateTime` | Direct mapping |
| `status` | `Status` | `ResultStatus` | Map: 'AUTH' → 'COMPLETED', 'IN ERROR' → 'RETRACTED' |
| `author_name` | `AuthorSID` → lookup | `VerifiedByStaffSID` → lookup | Same SStaff table |
| `cosigner_name` | `CosignerSID` → lookup | `CosignStaffSID` → lookup | Same SStaff table |
| `note_text` | `DocumentText` | `EventBlobText` | Direct mapping |
| `facility_name` | `Sta3n` → lookup | `Sta3n` → lookup | Same Dim.Facility table |

**Silver Layer Transformation Example:**

```python
# Pseudocode for Silver harmonization
if source == 'VistA':
    normalized_row = {
        'source_system': 'VistA',
        'tiu_document_sid': row['TIUDocumentSID'],
        'clinical_event_sid': None,
        'reference_datetime': row['ReferenceDateTime'],
        'status': row['Status'],  # Already 'COMPLETED', 'UNSIGNED', etc.
        # ... other fields
    }
elif source == 'Cerner':
    normalized_row = {
        'source_system': 'Cerner',
        'tiu_document_sid': None,
        'clinical_event_sid': row['ClinicalEventSID'],
        'reference_datetime': row['EventEndDateTime'],
        'status': map_cerner_status(row['ResultStatus']),  # 'AUTH' → 'COMPLETED'
        # ... other fields
    }
```

---

#### E.6 Cerner Facilities (Distinct Sta3n Values)

**Phase 2 Test Data - Cerner-Enabled Facilities:**

| Sta3n | Facility Name | System | Notes |
|-------|--------------|--------|-------|
| 612 | Columbus VAMC | Cerner | Ohio Cerner pilot site |
| 648 | Portland VAMC | Cerner | Oregon Cerner rollout |
| 663 | Puget Sound VA | Cerner | Washington Cerner site |

**VistA Facilities (from Phase 1):**

| Sta3n | Facility Name | System |
|-------|--------------|--------|
| 508 | Atlanta VAMC | VistA |
| 516 | Bay Pines VAMC | VistA |
| 552 | Dayton VAMC | VistA |
| 688 | Washington DC VAMC | VistA |

**Patients with Notes from Both Systems (Transferred Care):**
- Patient ICN100003: Notes from 508 (VistA) and 612 (Cerner) - simulates transfer from Atlanta to Columbus
- Patient ICN100015: Notes from 516 (VistA) and 648 (Cerner) - simulates transfer from Bay Pines to Portland
- Patient ICN100028: Notes from 552 (VistA) and 663 (Cerner) - simulates transfer from Dayton to Puget Sound

---

#### E.7 Cerner Test Data Volume and Distribution

**Total Cerner Notes:** 30-50

**Distribution by Class:**
- Progress Notes: 15-20 notes
- Consults: 8-10 notes
- Discharge Summaries: 4-6 notes
- Imaging Reports: 3-4 notes

**Distribution by Facility:**
- Sta3n 612 (Columbus): 12-15 notes
- Sta3n 648 (Portland): 10-12 notes
- Sta3n 663 (Puget Sound): 8-10 notes

**Temporal Distribution:**
- Recent (<30 days): 30% of Cerner notes
- 30-90 days: 40% of Cerner notes
- 90-180 days: 20% of Cerner notes
- >180 days: 10% of Cerner notes

**Content Style:**
- Use same SOAP format as VistA notes (clinical content is standardized)
- Use Cerner-style titles (e.g., "Physician Note - General" vs "GEN MED PROGRESS NOTE")
- Ensure VHAEnterpriseStandardTitle maps to same values as VistA for proper classification

---

#### E.8 Implementation Notes

**Phase 2 Implementation Sequence:**
1. Create CDWWork2 database and schemas (Day 9)
2. Populate Dim.ClinicalEventCode with seed data (Day 9)
3. Generate 30-50 Cerner notes with realistic content (Day 9)
4. Populate Clinical.ClinicalEvent and Clinical.ClinicalEventBlob (Day 9)
5. Create Bronze extraction script for Cerner (Day 10)
6. Update Silver script to harmonize and merge Cerner data (Day 10)
7. Test Gold aggregation with merged data (Day 11)
8. Load Cerner notes into PostgreSQL (Day 11)
9. Verify UI displays merged notes correctly (Day 12)
10. Test filtering, sorting, pagination with dual-source data (Day 12)

**No PostgreSQL Schema Changes Required:**
- The source-agnostic schema designed in Phase 1 handles Cerner data without modification
- `source_system`, `tiu_document_sid`, and `clinical_event_sid` columns accommodate both sources
- UI code requires no changes (data is pre-harmonized in Silver layer)

---

**END OF APPENDIX E**

---

**END OF DESIGN DOCUMENT**

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-02 | Claude Code | Initial comprehensive design specification for Clinical Notes domain. Includes all note classes (Progress Notes, Consults, Discharge Summaries, Imaging), 2x1 widget, full page with filtering/pagination, AI-ready schema, 100-150 realistic test notes, and 8-day implementation roadmap. |
| v2.0 | 2026-01-02 | Claude Code | **Major update: Dual-Source Architecture.** Expanded scope to include both VistA (CDWWork) and Cerner (CDWWork2) data sources. Added Appendix E with complete CDWWork2 schema specifications (Dim.ClinicalEventCode, Clinical.ClinicalEvent, Clinical.ClinicalEventBlob). Updated PostgreSQL schema to be source-agnostic with source_system column and nullable SIDs. Restructured implementation as Phase 1 (VistA, 8 days) and Phase 2 (Cerner, 3-4 days). Total test data: 130-200 notes. Added field mapping reference for Silver layer harmonization. Defined Cerner facilities with distinct Sta3n values (600s range). |
| v2.1 | 2026-01-02 | Claude Code | **Dashboard Widget Update: Multi-Row Support.** Restructured Section 8.1 to include both 2x1 Compact and 2x2 Enhanced Detail widget specifications. Added Section 8.1.2 with comprehensive 2x2 widget design (first multi-row widget in med-z1): 3 notes with 250-300 character previews, complete metadata (full datetime, author credentials, facility name), explicit status display, and full-text note class labels. Added Section 8.1.3 with complete CSS specifications for `.widget--2x2` and `.widget--1x2` classes including responsive breakpoints. Added Section 8.1.4 documenting updated dashboard widget order (aligned with sidebar navigation) and grid layout examples. Added Section 8.1.5 with implementation dependencies (6 files requiring updates, ~2.5 hour effort estimate). Updated Immunizations to 1x2 placeholder widget. |
| v2.2 | 2026-01-02 | Claude Code | **Implementation-Ready Corrections.** **Critical fix:** Added `author_credentials VARCHAR(20)` field throughout: PostgreSQL schema (Section 6.1), Silver ETL schema (Section 5.2), all API endpoint queries (Sections 7.2.1, 7.2.2, 7.2.3), database query functions (Section 7.3), and JSON response examples. Added credentials extraction to Silver ETL transformations (from SStaff.Title field). **Minor fixes:** Updated Day 2 roadmap to use `etl/bronze_clinical_notes_vista.py` (consistent with dual-source architecture). Updated Day 5 roadmap to specify 2x2 Enhanced Detail widget implementation (not 2x1), added multi-row CSS tasks, dashboard widget reordering tasks, and sidebar navigation updates. Increased Day 5 estimate from 4-5 hours to 5-6 hours. Updated Phase 1 total from 38-47 hours to 39-48 hours. Updated overall total from 48-57 hours to 49-58 hours. Document status changed to "Ready for Implementation". |
