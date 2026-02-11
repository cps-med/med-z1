# Family Health / Family History - Design Specification

**Document Version:** v1.0  
**Created:** 2026-02-11  
**Last Updated:** 2026-02-11  
**Status:** PLANNED (Design Complete, Implementation Pending)  
**Clinical Domain Name (Program):** Family Health  
**UI Display Name (Widget + Detail Page):** Family History  
**Sidebar Link Name:** History

**Implementation Status Source:** `docs/spec/implementation-status.md`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Clinical Context and Research Inputs](#3-clinical-context-and-research-inputs)
4. [Mock SQL Server Design](#4-mock-sql-server-design)
5. [ETL Pipeline Design](#5-etl-pipeline-design)
6. [PostgreSQL Serving Design](#6-postgresql-serving-design)
7. [API and UI Design](#7-api-and-ui-design)
8. [AI Insights Opportunities](#8-ai-insights-opportunities)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Testing Strategy](#10-testing-strategy)
11. [Open Questions](#11-open-questions)
12. [References](#12-references)

---

## 1. Overview

### 1.1 Purpose

This design adds a new clinical domain to med-z1 for family-history data, modeled as:

- **VistA-style data in `CDWWork`** (patient-centric)
- **Cerner/Oracle Health data in `CDWWork2`** (encounter-centric)
- Unified downstream representation for dashboard, full page, and AI Insights

### 1.2 Scope

**In Scope:**
- New mock SQL Server create/insert scripts for both `cdwwork` and `cdwwork2`
- Family-history table design with dimension/fact modeling
- Bronze/Silver/Gold/PostgreSQL pipeline plan
- Dashboard widget and detail page design
- Sidebar and dashboard widget order updates
- AI Insights integration opportunities and phased plan
- Initial mock data includes both adult/chronic and pediatric family-history patterns

**Out of Scope (for this enhancement):**
- VistA real-time RPC overlay for family history (explicitly deferred)
- Write-back/edit workflows (read-only display)
- External clinical guideline engine for hereditary risk scoring
- Unstructured NLP extraction from TIU/Health Factors for this phase

### 1.3 Naming and Route Conventions

To reconcile naming requirements:

- Domain key (internal): `family_history`
- Dashboard widget title: `Family History`
- Detail page title: `Family History`
- Sidebar label: `History`
- Suggested route: `/history` (redirect to patient-specific `/patient/{icn}/history`)
- CDWWork2 table naming remains med-z1-consistent: `EncMill.FamilyHistory`

### 1.4 History Domain Direction

Navigation label `History` is treated as a broader umbrella direction that can grow to include:
- Family history (this phase)
- Social history (future)
- Surgical history (future)

Implementation for this phase remains family-history only, with naming chosen to support future expansion.

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. Add realistic family-history mock data for both source systems.
2. Preserve source differences while harmonizing for UI/AI use.
3. Keep dashboard/sidebar ordering aligned with requested sequence.
4. Establish reusable patterns for future hereditary-risk enhancements.

### 2.2 Success Criteria

**Data Model:**
- [ ] `CDWWork` includes at least 1 dimension + 1 fact for family history.
- [ ] `CDWWork2` includes at least 1 fact for family history and uses `NDimMill.CodeValue` for dimensions.
- [ ] Mock data populated for core test patients (including Thompson cohort where appropriate).

**Pipeline:**
- [ ] Bronze extraction scripts created for new tables.
- [ ] Silver harmonization creates a single normalized family-history dataset.
- [ ] Gold patient-centric output produced and loaded to PostgreSQL.

**UI/Navigation:**
- [ ] New **1x1** `Family History` dashboard widget implemented.
- [ ] New full detail page implemented.
- [ ] Sidebar uses label `History`.
- [ ] Widget/sidebar order updated to: Demographics, Tasks, Vitals, Allergies, History, Medications, Immunizations, Labs, Notes, Encounters, Orders, Procedures (2x1), Problems, Imaging (2x1).

**AI:**
- [ ] Family-history context appears in patient summary.
- [ ] At least one dedicated family-history retrieval tool is available.

---

## 3. Clinical Context and Research Inputs

### 3.1 Practical Modeling Basis

Public VA CDW family-history table documentation is limited. This design uses:

1. Existing med-z1 CDW patterns (`CDWWork` patient-centric vs `CDWWork2` encounter-centric).
2. VistA/PCC family-history concepts (family member relationship + condition + status + dates).
3. Oracle/Cerner FHIR FamilyMemberHistory resource semantics for relationship/condition/verification.

### 3.2 Core Clinical Data Elements

Minimum harmonized fields:

- Patient identity (`PatientSID`/`PersonSID`, `ICN`)
- Family member relationship (mother/father/sibling/child/etc.)
- Condition code + display text
- Clinical status (active/resolved/inactive/unknown)
- Onset age or age range (if available)
- Note/comment text
- Recorder/provider/source metadata
- Source lineage (`CDWWork` vs `CDWWork2`)

---

## 4. Mock SQL Server Design

### 4.1 Path Clarification

Existing med-z1 folder names are:
- `mock/sql-server/cdwwork` (not `cdwork`)
- `mock/sql-server/cdwwork2` (not `cdwork2`)

This design follows current repository naming.

### 4.2 CDWWork (VistA-style) - Proposed Tables

**Schema:** `Outpat` + `Dim`
**Modeling Approach:** Structured mock tables only (no unstructured TIU/HF extraction in this phase)

**New Dimension Tables:**
1. `Dim.FamilyRelationship`
   - `FamilyRelationshipSID` (PK)
   - `RelationshipCode` (e.g., MTH, FTH, SIS, BRO, SON, DAU, MGM)
   - `RelationshipName`
   - `Degree` (First, Second, Other)
   - `IsActive`

2. `Dim.FamilyCondition`
   - `FamilyConditionSID` (PK)
   - `SNOMEDCode` (nullable)
   - `ICD10Code` (nullable)
   - `ConditionName`
   - `ConditionCategory` (Cancer, Cardio, Metabolic, Neuro, Psych, Other)
   - `HereditaryRiskFlag`
   - `IsActive`

**New Fact Table:**
1. `Outpat.FamilyHistory`
   - `FamilyHistorySID` (PK, BIGINT IDENTITY)
   - `PatientSID` (FK to `SPatient.SPatient`)
   - `Sta3n`
   - `FamilyRelationshipSID` (FK)
   - `FamilyConditionSID` (FK)
   - `FamilyMemberGender` (nullable)
   - `OnsetAgeYears` (nullable)
   - `DeceasedFlag` (nullable)
   - `ClinicalStatus` (Active/Resolved/Unknown)
   - `RecordedDateTime`
   - `EnteredDateTime`
   - `ProviderSID` (nullable)
   - `LocationSID` (nullable)
   - `CommentText` (nullable)
   - `IsActive`

**Create Scripts:**
- `mock/sql-server/cdwwork/create/Dim.FamilyRelationship.sql`
- `mock/sql-server/cdwwork/create/Dim.FamilyCondition.sql`
- `mock/sql-server/cdwwork/create/Outpat.FamilyHistory.sql`

**Insert Scripts:**
- `mock/sql-server/cdwwork/insert/Dim.FamilyRelationship.sql`
- `mock/sql-server/cdwwork/insert/Dim.FamilyCondition.sql`
- `mock/sql-server/cdwwork/insert/Outpat.FamilyHistory.sql`

### 4.3 CDWWork2 (Cerner-style) - Proposed Tables

**Schema:** `EncMill` (+ existing `NDimMill` code sets)

**Dimension Strategy:**
- Reuse `NDimMill.CodeValue` as the dimension layer.
- Add code sets:
  - `FAMILY_RELATIONSHIP`
  - `FAMILY_HISTORY_CONDITION`
  - `FAMILY_HISTORY_STATUS`

**New Fact Table:**
1. `EncMill.FamilyHistory`
   - `FamilyHistorySID` (PK, BIGINT IDENTITY)
   - `EncounterSID` (FK to `EncMill.Encounter`, NOT NULL)
   - `PersonSID` (FK to `VeteranMill.SPerson`, NOT NULL)
   - `PatientICN`
   - `Sta3n`
   - `RelationshipCodeSID` (FK to `NDimMill.CodeValue`)
   - `ConditionCodeSID` (FK to `NDimMill.CodeValue`)
   - `StatusCodeSID` (FK to `NDimMill.CodeValue`)
   - `FamilyMemberName` (nullable)
   - `FamilyMemberAge` (nullable)
   - `OnsetAgeYears` (nullable)
   - `NotedDateTime`
   - `DocumentedBy`
   - `CommentText` (nullable)
   - `IsActive`

**Create Scripts:**
- `mock/sql-server/cdwwork2/create/EncMill.FamilyHistory.sql`

**Insert Scripts:**
- `mock/sql-server/cdwwork2/insert/EncMill.FamilyHistory.sql`
- Update `mock/sql-server/cdwwork2/insert/NDimMill.CodeValue.sql` with family-history code sets

### 4.4 Master Script Updates

Add create/insert includes to:
- `mock/sql-server/cdwwork/create/_master.sql`
- `mock/sql-server/cdwwork/insert/_master.sql`
- `mock/sql-server/cdwwork2/create/_master.sql`
- `mock/sql-server/cdwwork2/insert/_master.sql`

---

## 5. ETL Pipeline Design

### 5.1 Bronze

New extracts:
- `etl/bronze_family_history.py` (recommended combined pattern) or split by source:
  - `bronze/cdwwork/outpat_family_history/`
  - `bronze/cdwwork2/encmill_family_history/`
  - Optional: family-history dimension extracts for CDWWork

### 5.2 Silver

Create harmonized transformation:
- `etl/silver_family_history.py`
- Output: `silver/family_history/family_history_cleaned.parquet`

Transformation responsibilities:
- Join relationship/condition text
- Normalize status values across source systems
- Standardize column names (`patient_icn`, `relationship`, `condition_name`, `onset_age_years`, `noted_datetime`)
- Add `data_source` lineage column
- Deduplicate by (`patient_icn`, `relationship`, `condition_name`, `noted_date`)

### 5.3 Gold

Create patient-centric dataset:
- `etl/gold_family_history.py`
- Output: `gold/patient_family_history/patient_family_history_final.parquet`

Potential derived fields:
- `first_degree_relative_flag`
- `risk_condition_group`
- `family_history_count_active`

---

## 6. PostgreSQL Serving Design

### 6.1 New Table

`clinical.patient_family_history`

Proposed columns:
- `id` BIGSERIAL PK
- `patient_icn` VARCHAR(50) NOT NULL
- `data_source` VARCHAR(20) NOT NULL
- `relationship` VARCHAR(100) NOT NULL
- `relationship_degree` VARCHAR(20) NULL
- `condition_name` VARCHAR(255) NOT NULL
- `condition_code` VARCHAR(50) NULL
- `condition_system` VARCHAR(20) NULL
- `condition_category` VARCHAR(80) NULL
- `clinical_status` VARCHAR(30) NULL
- `onset_age_years` INT NULL
- `recorded_datetime` TIMESTAMP NULL
- `facility` VARCHAR(120) NULL
- `provider_name` VARCHAR(120) NULL
- `comment_text` TEXT NULL
- `is_active` BOOLEAN DEFAULT TRUE
- `created_at` TIMESTAMP DEFAULT NOW()

Indexes:
- `(patient_icn, recorded_datetime DESC)`
- `(patient_icn, is_active)`
- `(patient_icn, condition_category)`

### 6.2 DB Access Layer

Add:
- `app/db/patient_family_history.py`

Functions:
- `get_patient_family_history(icn, days=None, relationship=None, category=None, active_only=False)`
- `get_recent_family_history(icn, limit=5)`
- `get_family_history_counts(icn)`

---

## 7. API and UI Design

### 7.1 API Endpoints

New route module:
- `app/routes/family_history.py`

Endpoints:
1. `GET /api/patient/{icn}/history` (JSON)
2. `GET /api/patient/{icn}/history/recent` (JSON for widget)
3. `GET /api/patient/dashboard/widget/history/{icn}` (HTML partial)
4. `GET /patient/{icn}/history` (full page)
5. `GET /patient/{icn}/history/filtered` (HTMX partial rows)
6. `GET /history` (CCOW-based redirect)

### 7.2 Dashboard Widget

**Name:** `Family History`  
**Size:** `1x1` (initial requirement)

Widget content:
- 4-6 most recent/most clinically significant family-history entries
- compact relationship + condition rows (e.g., `Mother - Breast cancer`)
- summary counts (total, first-degree, active/high-risk)
- link: `View Full History`

### 7.3 Full Detail Page

**Page Title:** `Family History`  
**Sidebar Label:** `History`

Layout pattern aligns with existing domains:
- breadcrumb `Dashboard > Family History`
- summary cards (total conditions, first-degree count, high-risk count)
- table columns:
  - Relationship
  - Condition
  - Category
  - Onset Age
  - Status
  - Recorded Date
  - Source (CDWWork/CDWWork2)
- filters:
  - Relationship
  - Condition Category
  - Time period
  - Active only

Default sort:
- `Recorded Date DESC` (most recent recorded first)

### 7.4 Dashboard and Sidebar Reordering

Required order after adding History:
1. Demographics
2. Tasks
3. Vitals
4. Allergies
5. History
6. Medications
7. Immunizations
8. Labs
9. Notes
10. Encounters
11. Orders
12. Procedures (**update to 2x1**)
13. Problems
14. Imaging (**update to 2x1**)

Primary touchpoints:
- `app/templates/dashboard.html`
- `app/templates/base.html`
- related widget CSS sizing in `app/static/styles.css`

---

## 8. AI Insights Opportunities

### 8.1 Phase 1 (Low Risk, High Value)

Add family history to patient context summary:
- "Family history notable for mother with breast cancer and father with type 2 diabetes."

Update:
- `ai/services/patient_context.py`

Default behavior:
- Always call out first-degree relative findings explicitly when present.

### 8.2 Phase 2 (Tooling)

Add tool:
- `get_family_history(icn, relationship=None, category=None, active_only=True)`

Use cases:
- "Any first-degree cardiac history?"
- "Does family history increase diabetes risk context?"

### 8.3 Phase 3 (Reasoning Enhancements)

Optional derived insight prompts:
- hereditary risk markers (non-diagnostic)
- preventive-care suggestion framing (screening discussion prompts)

Safety notes:
- Keep outputs as supportive context, not deterministic risk prediction.
- Include source and uncertainty language when data is sparse/incomplete.
- Present first-degree findings as risk context only, not diagnosis.

---

## 9. Implementation Roadmap

### Phase 1 - Mock SQL Foundations (1-2 days)
- Create CDWWork family-history dimension/fact DDL + inserts
- Create CDWWork2 family-history fact DDL + inserts
- Update all `_master.sql` scripts
- Validate database build from scratch

Phase Exit Criteria:
- [ ] New create/insert scripts execute successfully in both databases.
- [ ] New tables exist with expected columns, FKs, and indexes.
- [ ] Sample rows present for both adult and pediatric family-history patterns.

Manual Testing:
- Rebuild mock SQL databases with create + insert master scripts.
- Run `SELECT TOP 20 *` checks on each new table and verify referential integrity.
- Verify Thompson and baseline demo patients have family-history rows where expected.

### Phase 2 - ETL (1-2 days)
- Bronze extraction for both sources
- Silver harmonization and dedup
- Gold patient-centric output

Phase Exit Criteria:
- [ ] Bronze files written for both sources.
- [ ] Silver harmonized output produced with `data_source`.
- [ ] Gold patient-centric output available and schema-validated.

Manual Testing:
- Run Bronze, Silver, and Gold jobs in order.
- Inspect Parquet outputs for key columns (`patient_icn`, `relationship`, `condition_name`, `recorded_datetime`).
- Spot-check dedup behavior on repeated conditions across sources.

### Phase 3 - PostgreSQL Serving Layer (0.5-1 day)
- Create `clinical.patient_family_history`
- Add load script and DB access functions

Phase Exit Criteria:
- [ ] `clinical.patient_family_history` created with indexes.
- [ ] Gold-to-PostgreSQL load completes without errors.
- [ ] DB access functions return expected records for test ICNs.

Manual Testing:
- Execute PostgreSQL migration/load and verify row counts.
- Run direct SQL queries by ICN and compare with Gold Parquet samples.
- Exercise DB access functions from a Python shell or route-level smoke test.

### Phase 4 - API Endpoints (0.5-1 day)
- Create `app/routes/family_history.py`
- Add endpoint: `GET /api/patient/{icn}/history`
- Add endpoint: `GET /api/patient/{icn}/history/recent`
- Add endpoint: `GET /api/patient/dashboard/widget/history/{icn}`
- Add endpoint: `GET /patient/{icn}/history`
- Add endpoint: `GET /patient/{icn}/history/filtered`
- Add endpoint: `GET /history` (CCOW redirect)
- Register router in `app/main.py`

Phase Exit Criteria:
- [ ] All six endpoints respond successfully.
- [ ] Endpoint payloads and HTML fragments match expected schema/layout.
- [ ] Error/empty states return safe responses (no server exception pages).

Manual Testing:
- Call all endpoints with valid ICN, invalid ICN, and no-patient context cases.
- Verify `/history` redirect follows CCOW patient context correctly.
- Confirm filter endpoint updates rows correctly for relationship/category/time filters.

### Phase 5 - UI + Navigation (1-2 days)
- Add 1x1 dashboard widget (`Family History`)
- Add full `/history` page + filters
- Reorder sidebar and dashboard widgets
- Keep Procedures and Imaging as placeholders, resize both to 2x1

Phase Exit Criteria:
- [ ] Dashboard shows `Family History` widget as 1x1.
- [ ] Full history page renders with default sort `Recorded Date DESC`.
- [ ] Sidebar and dashboard order match required sequence.
- [ ] Procedures/Imaging placeholders render at 2x1.

Manual Testing:
- Open dashboard and verify widget order/size visually.
- Navigate via sidebar `History` link and validate table/filter behavior.
- Test responsive layouts (desktop/tablet/mobile) for order and sizing consistency.
- Verify no regressions in adjacent widgets (Meds, Immunizations, Labs, Notes, Encounters).

### Phase 6 - AI Integration (0.5-1 day)
- Add context enrichment
- Add optional dedicated retrieval tool
- Add prompt guidance and validation examples

Phase Exit Criteria:
- [ ] Patient summary includes family-history context when data exists.
- [ ] First-degree relative findings are explicitly highlighted.
- [ ] Tool output is source-attributed and uses uncertainty language when needed.

Manual Testing:
- Run AI summary prompts for patients with and without family-history data.
- Ask first-degree risk-context questions and verify explicit highlighting.
- Validate responses avoid deterministic diagnosis language.

**Estimated Total:** 5 to 8 days

---

## 10. Testing Strategy

### 10.1 Data Tests
- SQL FK integrity checks for new tables
- Row-count assertions for each test patient
- Null/enum validation for key fields (relationship/status/condition)

### 10.2 Pipeline Tests
- Bronze extract success for both sources
- Silver harmonization correctness (field-level spot checks)
- Gold output and PostgreSQL load validation

### 10.3 API/UI Tests
- Endpoint response and filter behavior
- Widget loads via HTMX and handles empty state
- Detail page sorting/filtering and source badges
- Sidebar + dashboard order verification against required list

### 10.4 AI Tests
- Family-history context appears in summary
- Tool responses return structured and source-attributed data
- No over-assertive clinical claims

---

## 11. Open Questions

All previously open questions were resolved on 2026-02-11:

1. CDWWork2 naming remains med-z1-consistent: `EncMill.FamilyHistory`.
2. CDWWork/VistA modeling uses structured mock tables only.
3. Full page default sort is most recent recorded.
4. Initial mock data includes both pediatric and adult/chronic patterns.
5. Sidebar `History` is a broader umbrella direction (family/social/surgical), with this phase implementing family history.
6. Procedures/Imaging remain placeholders and are resized to 2x1.
7. AI summaries explicitly highlight first-degree findings when present.

---

## 12. References

- HL7 FHIR R4 FamilyMemberHistory Resource: https://www.hl7.org/fhir/familymemberhistory.html  
- Oracle Health Millennium FHIR - FamilyMemberHistory (R4): https://docs.oracle.com/en/industries/health/millennium-platform-apis/mfrap/op-familymemberhistory-post.html  
- VistA/PCC file listings including V Family History (File 9000014) and Family Relation (File 9999999.36): https://www.vistapedia.com/index.php/VA_FileMan_Entries_(globals)_by_Number  
- Existing med-z1 architecture and source patterns:
  - `docs/spec/cdwwork2-design.md`
  - `docs/spec/patient-dashboard-design.md`
  - `mock/sql-server/cdwwork/create/_master.sql`
  - `mock/sql-server/cdwwork2/create/_master.sql`
