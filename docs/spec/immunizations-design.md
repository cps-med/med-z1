# Immunizations Design Specification - med-z1

**Document Version:** 1.4
**Date:** 2026-01-15
**Status:** ✅ Phase 1 Complete (Data Pipeline) - ✅ Phase 2 Complete (API/UI) - Phase 3 Pending (AI Integration)
**Implementation Progress:**
- ✅ **Phase 1 (Days 1-6): Data Pipeline COMPLETE** (2026-01-14)
  - Days 1-2: SQL Server mock data (CDWWork + CDWWork2) ✅
  - Day 3: Bronze ETL (extraction to Parquet) ✅
  - Day 4: Silver ETL (harmonization) ✅
  - Days 5-6: Gold ETL + PostgreSQL load ✅
- ✅ **Phase 2 (Days 7-8): API/UI Implementation COMPLETE** (2026-01-14)
  - Database layer: `app/db/patient_immunizations.py` ✅
  - API routes: `app/routes/immunizations.py` (6 endpoints) ✅
  - Dashboard widget: 1x1 widget with summary stats and recent immunizations ✅
  - Full page: Patient immunizations page with filtering and table view ✅
  - Navigation: Added to sidebar, active link, breadcrumbs ✅
  - Styling: Complete CSS for widget and full page ✅
- ⏳ **Phase 3: AI Integration** (Pending - See `docs/spec/ai-insight-design.md` Phase 7)

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
9. [AI Integration Design](#9-ai-integration-design)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Testing Strategy](#11-testing-strategy)
12. [Security and Privacy](#12-security-and-privacy)
13. [Appendices](#13-appendices)

---

## 1. Overview

### 1.1 Purpose

The **Immunizations** domain provides comprehensive access to patient vaccination history and compliance status, enabling clinicians to:
- View recent immunizations at a glance (dashboard widget)
- Review complete vaccination history across the lifespan (full immunizations page)
- Identify vaccine series completion status (e.g., "1 of 2 doses complete")
- Track adverse reactions to vaccines for safety
- Support CDC ACIP guideline compliance through AI-assisted analysis
- Identify gaps in immunization coverage
- Support preventive care and public health initiatives

Immunizations data is sourced from VistA File #9000010.11 (V IMMUNIZATION) with vaccine definitions from File #9999999.14 (IMMUNIZATION).

### 1.2 Scope

**In Scope for Initial Implementation:**
- Mock CDW database schema (4 tables total):
  - **2 Dimension tables:** `Dim.Vaccine` (CVX-coded vaccine definitions), `Dim.VaccineSeries` (series tracking)
  - **2 Fact tables:** `Immunization.PatientImmunization` (VistA/CDWWork), `ImmunizationMill.VaccineAdmin` (Cerner/CDWWork2)
- CVX (Concept of Vaccines eXpanded) code standardization for AI/interoperability
- ETL pipeline: Bronze → Silver → Gold → PostgreSQL
- PostgreSQL reference table: `reference.vaccine` with ~30 common CVX codes
- Dashboard widget (**1x1 size**):
  - Shows 6-8 most recent vaccines
  - Displays vaccine name, date, series status ("1 of 2")
  - Adverse reaction indicators
  - "View All Immunizations" link to full page
- Full Immunizations page with:
  - **Chronological table view** (similar to Vitals/Labs pattern)
  - Columns: Date, Vaccine Name, Series, Site of Admin, Provider, Adverse Reaction
  - Expandable row details (click to show full vaccine details, series info, comments)
  - Filtering by date range (30 days, 90 days, 6 months, 1 year, all)
  - Filtering by vaccine family (Influenza, COVID-19, Hepatitis, etc.)
  - Filtering by series status (Complete, Incomplete, Single-dose)
  - Sort by date (descending default), vaccine name, series
- Read-only functionality
- Test data for 8 patients (ICN100001-100005, ICN100009, ICN100010, ICN100013)
- Must-have features:
  1. ✅ Vaccine administration history with CVX codes
  2. ✅ Multi-dose series tracking ("1 of 2", "3 of 3 COMPLETE")
  3. ✅ Adverse reaction tracking (text field)
  4. ✅ Site of administration (Left/Right Deltoid, etc.)
  5. ✅ CDC ACIP compliance foundation (CVX codes for AI)

**In Scope for Phase 2 (AI Integration - Days 9-12):**
- AI Clinical Insights tools (3 new tools):
  1. `get_immunization_history` - Retrieve patient vaccine history with CVX codes
  2. `check_vaccine_compliance` - RAG-based CDC ACIP guideline compliance checking
  3. `forecast_next_dose` - Calculate due dates for multi-dose series
- LangGraph ReAct agent integration
- CDC "Pink Book" ACIP schedule vector embeddings (future RAG enhancement)
- Vaccine gap analysis queries (e.g., "Is patient due for Shingrix?")

**Out of Scope for Initial Implementation:**
- VistA RPC Broker real-time integration (T-0 data) - **Deferred to Phase 3**
  - Rationale: Vaccines are not typically administered "today" with the same urgency as medications or vitals
  - Will follow Vista integration pattern from Vitals/Medications domains when implemented
- Immunization entry/editing (read-only for now)
- Multiple adverse reactions per vaccine (using bridge table pattern) - **Deferred to Phase 3**
  - MVP uses single text field; can enhance to bridge table like Allergies if needed
- Vaccine lot number tracking
- Vaccine Information Statement (VIS) document tracking
- Integration with CPRS/immunization ordering
- Real-time vaccine alerts
- Vaccine contraindications checking (e.g., allergy to vaccine ingredients)
- Immunization registry reporting (state/local registries)
- Vaccine inventory management
- Travel vaccine recommendations
- Exemption/refusal tracking (religious, medical, personal)

### 1.3 Key Design Decisions

**Decision Summary (Based on User Confirmation 2026-01-14):**

1. **Widget: 1x1 Size, Chronological Display**
   - Shows 6-8 most recent vaccines
   - Sorted by administration date descending
   - Matches Allergies widget pattern for consistency

2. **CDWWork2 Included Day 1**
   - Parallel Cerner/Oracle Health tables (`ImmunizationMill.VaccineAdmin`)
   - Tests cross-system harmonization in Silver ETL
   - Adds ~1 day to implementation

3. **CVX Reference Table in Both Systems**
   - SQL Server: `Dim.Vaccine` dimension table (matches VistA File #9999999.14)
   - PostgreSQL: `reference.vaccine` reference table (~30 common vaccines)
   - Enables AI compliance checking and vaccine name standardization

4. **Full Page: Chronological Table Layout**
   - Follows Vitals/Labs pattern (proven UI pattern)
   - Sortable columns, expandable rows for details
   - Three-tier filtering: Date range + Vaccine family + Series status

5. **Series Tracking: Yes - Critical for Compliance**
   - Store series information ("1 of 2", "2 of 2 COMPLETE")
   - Calculate completion status for AI tools
   - Display prominently in UI for clinical decision support

6. **AI Tools: Phase 2 Implementation (Days 9-12)**
   - Basic widget/page first (Days 1-8)
   - AI integration after UI is proven (Days 9-12)
   - Matches pattern from Medications, Encounters domains

7. **Adverse Reactions: Simple Text Field (MVP)**
   - Single `adverse_reaction VARCHAR(255)` field
   - Sufficient for most use cases
   - Can enhance to bridge table pattern (like Allergies) in Phase 3 if needed

8. **Test Patient Data: Moderate Scope (15-25 vaccines per patient)**
   - 8 test patients: ICN100001, ICN100002, ICN100003, ICN100004, ICN100005, ICN100009, ICN100010, ICN100013
   - Realistic childhood series (MMR, DTaP, Polio, Hepatitis B)
   - Adult boosters (Tdap, Influenza, COVID-19, Shingrix)
   - Total: ~140-180 immunization records across 8 patients

9. **Filters: Date Range + Vaccine Family + Series Status**
   - **Date range** (standard): Last 30d, 90d, 6mo, 1yr, All
   - **Vaccine family**: Influenza, COVID-19, Hepatitis, MMR, Tdap/DTaP, Pneumococcal, Shingrix, HPV, Other
   - **Series status**: All, Complete, Incomplete, Single-dose

10. **Vista RPC Integration: Deferred to Phase 3**
    - Immunizations are less time-sensitive than vitals/medications
    - Focus initial effort on historical data (PostgreSQL)
    - Add Vista real-time layer after AI tools are proven

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Clinical Value:** Provide comprehensive vaccination history to support preventive care and CDC ACIP guideline compliance
2. **AI Foundation:** Establish CVX-coded data structures to enable intelligent vaccine gap analysis and compliance checking
3. **Prove the Pattern:** Demonstrate ETL and UI patterns scale to multi-dose series tracking
4. **Public Health Support:** Enable vaccination coverage analysis for population health initiatives

### 2.2 Success Criteria

**Data Pipeline:** ✅ **COMPLETE (2026-01-14)**
- [x] Mock CDW dimension tables created: `Dim.Vaccine` with CVX codes (30 vaccines)
- [x] CDWWork fact table: `Immunization.PatientImmunization` populated with 147 administrations across 8 patients
- [x] CDWWork2 fact table: `ImmunizationMill.VaccineAdmin` populated with 40 administrations (Cerner-style)
- [x] Bronze ETL extracts all 4 tables to Parquet (2 from CDWWork, 2 from CDWWork2)
- [x] Silver ETL harmonizes VistA and Cerner data, resolves CVX lookups, calculates series completion (178 → 178 after dedup)
- [x] Gold ETL creates patient-centric view: `patient_immunizations_final.parquet` with ICN, sorted by date (138 records)
- [x] PostgreSQL serving DB loaded with:
  - `clinical.patient_immunizations` table (138 records from Gold)
  - `reference.vaccine` reference table (30 CVX-coded vaccines)

**API:** ✅ **COMPLETE (2026-01-14)**
- [x] `GET /api/patient/{icn}/immunizations` returns all immunizations (JSON, sorted by date descending) with filtering support
- [x] `GET /api/patient/{icn}/immunizations/recent` returns recent immunizations for widget (last 5, 2-year lookback)
- [x] `GET /api/patient/{icn}/immunizations/widget` returns immunizations widget HTML
- [x] `GET /patient/{icn}/immunizations` renders full Immunizations page with filtering
- [x] `GET /patient/{icn}/immunizations/filtered` returns filtered table rows (HTMX partial)
- [x] `GET /immunizations` redirect route (gets patient from CCOW and redirects to patient-specific URL)
- [x] Database layer with comprehensive filtering: vaccine_group, cvx_code, days, incomplete_only, adverse_reactions_only
- [x] `get_immunization_counts()` function provides summary statistics for widgets

**UI (Widget):** ✅ **COMPLETE (2026-01-14)**
- [x] Widget displays on dashboard (**1x1 size**)
- [x] Shows 5 most recent vaccines chronologically (last 2 years)
- [x] Each vaccine shows:
  - Vaccine name (truncated at 40 chars)
  - Administration date
  - Series status (e.g., "1 of 2", "BOOSTER", "ANNUAL 2024")
  - Icons: COVID (virus-covid), Influenza (calendar-check), Reaction (triangle-exclamation), Incomplete (clock), Complete (syringe)
  - Badges: "Incomplete" (warning), "Reaction" (danger)
- [x] Summary stats section: Total, Recent (2y), Incomplete count
- [x] "View All Immunizations" link at bottom navigates to `/patient/{icn}/immunizations`
- [x] Empty state when no immunizations: "No immunization records"
- [x] Error handling with fallback message

**UI (Full Page):** ✅ **COMPLETE (2026-01-14)**
- [x] Immunizations page accessible from sidebar navigation (`/immunizations` → redirects to patient-specific URL)
- [x] Breadcrumbs: Dashboard > Immunizations
- [x] Summary stats bar (6 cards): Total, Recent (2y), Influenza, COVID-19, Incomplete Series, Adverse Reactions
- [x] Chronological table view with columns:
  - Vaccine (name + CVX code, with icon)
  - Date Administered
  - Series (with "Incomplete" badge if applicable)
  - Route / Site of Administration
  - Provider
  - Location (name + facility)
  - Status (badges: Complete/Incomplete/Adverse Reaction, plus source system badge)
- [x] Expandable detail rows for adverse reactions and comments
- [x] Filtering controls (HTMX dynamic):
  - Vaccine Group dropdown (All, Influenza, COVID-19, + custom groups from reference.vaccine)
  - Time Period dropdown (All Time, Last 90 Days, 6 Months, 1 Year, 2 Years)
  - Status dropdown (All, Incomplete Series, Adverse Reactions)
- [x] Results summary: "Showing X immunizations"
- [x] Empty state when filters return no results
- [x] Detail rows for adverse reactions and comments (auto-expand when present)
- [x] Incomplete series highlighted with warning badge
- [x] Sorted by date descending (most recent first)
- [x] CSS styling complete with proper color scheme and responsive layout

**AI Integration (Phase 2 - Days 9-12):**
- [ ] Three new LangGraph tools implemented:
  - `get_immunization_history` - Query patient vaccines by CVX code
  - `check_vaccine_compliance` - Compare history to CDC ACIP guidelines
  - `forecast_next_dose` - Calculate due dates for multi-dose series
- [ ] System prompts updated to include immunization queries
- [ ] Test queries working:
  - "What vaccines has this patient received?"
  - "Is the patient up to date on COVID-19 vaccinations?"
  - "What immunizations are due based on CDC guidelines?"
  - "Has the patient completed the Shingrix series?"

**Quality:**
- [ ] Code follows established patterns from Vitals, Allergies, Medications, Labs
- [ ] Error handling for missing data (e.g., CVX code not found)
- [ ] Logging for debugging
- [ ] Documentation complete

---

## 3. Prerequisites

### 3.1 Completed Work

Before starting Immunizations implementation, ensure:
- ✅ Dashboard framework complete
- ✅ Demographics widget functional
- ✅ Patient Flags widget functional
- ✅ Vitals widget functional
- ✅ Allergies widget functional
- ✅ Medications widget functional
- ✅ Encounters page functional (pagination pattern)
- ✅ Labs page functional (filtering pattern)
- ✅ Clinical Notes page functional (filtering pattern)
- ✅ PostgreSQL serving DB operational with `clinical` schema
- ✅ MinIO or local Parquet storage available
- ✅ ETL pipeline patterns established (Bronze/Silver/Gold)
- ✅ AI Clinical Insights framework operational (4 existing tools)
- ✅ Chronological table UI pattern established (Vitals, Labs)

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

- `docs/spec/immunizations-design-research.md` - AI strategy and CDW research
- `docs/spec/med-z1-architecture.md` - API routing patterns, location fields, pagination
- `docs/spec/patient-dashboard-design.md` - Dashboard widget specifications
- `docs/spec/vitals-design.md` - Chronological table UI pattern reference
- `docs/spec/allergies-design.md` - Card-based UI and dimension table patterns
- `docs/spec/medications-design.md` - Two-source harmonization pattern
- `docs/spec/lab-results-design.md` - Filtering UI pattern
- `docs/spec/ai-insight-design.md` - AI tool integration patterns
- `docs/spec/med-z1-plan.md` - Overall project plan
- VA VistA documentation: File #9000010.11 (V IMMUNIZATION), File #9999999.14 (IMMUNIZATION)
- CDC CVX codes: https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp

---
## 4. Data Architecture

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

### 4.1 Source: Mock CDW (SQL Server)

**Four tables in SQL Server:**

```
CDWWork Database (VistA-derived)

Dimension Table:
  Dim.Vaccine
    - VistA File #9999999.14 (IMMUNIZATION)
    - CVX-coded vaccine definitions
    - National standard vaccine names
    - Manufacturer codes (MVX)
    - Maps to NDF (National Drug File) for cross-referencing with medications

Fact Table:
  Immunization.PatientImmunization
    - VistA File #9000010.11 (V IMMUNIZATION)
    - One row per vaccine administration event
    - Links to patient, vaccine (CVX code), encounter
    - Series tracking ("1 of 2", "Booster")
    - Adverse reaction field
    - Site of administration (anatomical location)

CDWWork2 Database (Cerner/Oracle Health-derived)

Dimension Table:
  ImmunizationMill.VaccineCode
    - Cerner CODE_VALUE table subset
    - Maps Cerner vaccine codes to CVX
    - Display names from Cerner nomenclature

Fact Table:
  ImmunizationMill.VaccineAdmin
    - Cerner CLINICAL_EVENT pattern
    - Event-centric administration records
    - Links via person_id and encntr_id
    - CVX code mapping required in Silver ETL
```

### 4.2 VistA Source Context

#### VistA File #9000010.11 (V IMMUNIZATION)

This is the primary source for immunization data in VistA. Key fields:

| VistA Field | Field Name | CDWWork Mapping | Notes |
|-------------|------------|-----------------|-------|
| .01 | IMMUNIZATION | ImmunizationSID (FK) | Pointer to File #9999999.14 |
| .02 | EVENT DATE AND TIME | AdministeredDateTime | When vaccine was given |
| .03 | IMMUNIZATION LOT # | LotNumber | Lot number (deferred to Phase 3) |
| .04 | REACTION | Reaction | Adverse reaction text |
| .06 | SERIES | Series | "1", "2", "BOOSTER", "COMPLETE" |
| .07 | DOSE | Dose | Dose amount (e.g., "0.5 ML") |
| .08 | ROUTE | Route | Route of administration (IM, SC, PO, etc.) |
| .09 | SITE | SiteOfAdministration | Anatomical site (L DELTOID, R DELTOID, etc.) |
| .11 | VISIT | VisitSID (FK) | Pointer to encounter |
| 1.01 | ORDERING PROVIDER | ProviderSID (FK) | Ordering provider |
| 1.02 | ENCOUNTER PROVIDER | EncounterProviderSID (FK) | Administering provider |
| 1.2 | COMMENTS | Comments | Free-text clinical notes |

#### VistA File #9999999.14 (IMMUNIZATION)

Vaccine definition file. Key fields:

| VistA Field | Field Name | CDWWork Mapping | Notes |
|-------------|------------|-----------------|-------|
| .01 | NAME | ImmunizationName | VistA vaccine name |
| .02 | SHORT NAME | ShortName | Abbreviated name |
| .03 | CVX CODE | CVXCode | CDC CVX code (critical for AI) |
| .05 | INACTIVE FLAG | InactiveFlag | Y/N |
| .07 | MANUFACTURER | MVXCode | Manufacturer code |

### 4.3 CVX Codes (CDC Standard)

**CVX (Concept of Vaccines eXpanded)** is a CDC-maintained standard for vaccine identification. Each vaccine product gets a unique numeric code.

**Example CVX Codes (30 Common Vaccines for reference.vaccine table):**

| CVX | Vaccine Name | Series Pattern |
|-----|--------------|----------------|
| 008 | Hepatitis B, adolescent or pediatric | 3-dose |
| 010 | Poliovirus, inactivated (IPV) | 4-dose |
| 020 | Diphtheria, tetanus toxoids and acellular pertussis vaccine (DTaP) | 5-dose |
| 021 | Varicella | 2-dose |
| 033 | Pneumococcal polysaccharide vaccine, 23 valent (PPSV23) | Single or 2-dose |
| 043 | Hepatitis B, adult | 3-dose |
| 045 | Hepatitis B, unspecified formulation | 3-dose |
| 048 | Haemophilus influenzae type b vaccine (Hib) | 3-4 dose |
| 049 | Haemophilus influenzae type b vaccine (Hib), PRP-OMP | 2-3 dose |
| 052 | Hepatitis A, adult | 2-dose |
| 062 | Human Papillomavirus vaccine (HPV) | 2-3 dose |
| 083 | Hepatitis A, pediatric/adolescent | 2-dose |
| 088 | Influenza, unspecified formulation | Annual |
| 103 | Meningococcal polysaccharide vaccine (MPSV4) | 1-2 dose |
| 106 | Diphtheria, tetanus, and acellular pertussis vaccine (DTaP), 5 pertussis antigens | 5-dose |
| 107 | Diphtheria, tetanus toxoids and acellular pertussis vaccine, unspecified formulation (DTaP) | 5-dose |
| 110 | Diphtheria, tetanus toxoids and acellular pertussis vaccine, and poliovirus vaccine, inactivated (DTaP-IPV) | 4-dose |
| 113 | Tetanus and diphtheria toxoids (Td), preservative free | Booster |
| 115 | Tetanus toxoid, diphtheria toxoid, and acellular pertussis vaccine (Tdap) | Booster |
| 121 | Zoster vaccine, live (Zostavax) | Single |
| 135 | Influenza, high dose seasonal, preservative-free | Annual |
| 140 | Influenza, seasonal, injectable, preservative free | Annual |
| 141 | Influenza, seasonal, injectable | Annual |
| 144 | Influenza, seasonal, intradermal, preservative free | Annual |
| 152 | Pneumococcal conjugate vaccine, 10 valent (PCV10) | 4-dose |
| 158 | Influenza, injectable, quadrivalent, contains preservative | Annual |
| 161 | Influenza, injectable, quadrivalent, preservative free | Annual |
| 187 | Zoster vaccine recombinant (Shingrix) | 2-dose |
| 208 | COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose (Pfizer-BioNTech) | 2-dose primary + boosters |
| 213 | COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose (Moderna) | 2-dose primary + boosters |

### 4.4 Medallion Pipeline Architecture

**Bronze Layer (Source Extraction):**
```
Input:  CDWWork SQL Server tables (4 tables)
        - Dim.Vaccine
        - Immunization.PatientImmunization
        - ImmunizationMill.VaccineCode (CDWWork2)
        - ImmunizationMill.VaccineAdmin (CDWWork2)

Output: MinIO Parquet files
        - s3://med-z1/bronze/cdwwork/vaccine_dim/vaccine_dim_raw.parquet
        - s3://med-z1/bronze/cdwwork/immunization/patient_immunization_raw.parquet
        - s3://med-z1/bronze/cdwwork2/immunization_mill/vaccine_code_raw.parquet
        - s3://med-z1/bronze/cdwwork2/immunization_mill/vaccine_admin_raw.parquet

Naming Convention (Bronze Layer):
  - Dimension tables: {domain}_dim (suffix pattern)
    Examples: vaccine_dim, vital_type_dim, lab_test_dim
  - Fact tables: {domain_name} (no suffix)
    Examples: immunization, vital_sign, lab_chem
  - Files: {table_name}_raw.parquet

Transformations:
  - Column name standardization (lowercase with underscores)
  - Add source_system column ("CDWWork", "CDWWork2")
  - Add extraction_timestamp
  - No business logic transformations
```

**Silver Layer (Harmonization):**
```
Input:  Bronze Parquet files (4 files)

Output: s3://med-z1/silver/immunizations/immunizations_cleaned.parquet

Transformations:
  1. Join VistA fact table with Dim.Vaccine (get CVX code, vaccine name)
  2. Join Cerner fact table with VaccineCode (map to CVX)
  3. Harmonize column names across VistA and Cerner
  4. Standardize vaccine names (UPPERCASE, strip whitespace)
  5. Parse series information:
     - Extract dose_number (e.g., "1" from "1 of 2")
     - Extract total_doses (e.g., "2" from "1 of 2")
     - Calculate is_series_complete (dose_number == total_doses)
  6. Standardize anatomical sites:
     - "L DELTOID" → "Left Deltoid"
     - "R DELTOID" → "Right Deltoid"
     - "LT ARM" → "Left Arm"
  7. Add derived flags:
     - has_adverse_reaction (BOOLEAN)
     - is_annual_vaccine (CVX in [88, 135, 140, 141, 144, 158, 161] for flu)
     - is_covid_vaccine (CVX in [208, 212, 213, 217, 218, etc.])
  8. Deduplicate cross-system records (same patient, CVX, date → keep most recent)

Schema:
  - patient_sid (BIGINT) - for Gold join
  - cvx_code (VARCHAR)
  - vaccine_name_standardized (VARCHAR)
  - vaccine_name_local (VARCHAR)
  - administered_datetime (TIMESTAMP)
  - series (VARCHAR) - original text
  - dose_number (INT) - parsed
  - total_doses (INT) - parsed
  - is_series_complete (BOOLEAN) - derived
  - adverse_reaction (VARCHAR)
  - has_adverse_reaction (BOOLEAN)
  - site_of_administration (VARCHAR)
  - route (VARCHAR)
  - dose (VARCHAR)
  - provider_sid (BIGINT)
  - location_sid (INT)
  - sta3n (SMALLINT)
  - comments (TEXT)
  - source_system (VARCHAR)
  - is_annual_vaccine (BOOLEAN)
  - is_covid_vaccine (BOOLEAN)
```

**Gold Layer (Patient-Centric):**
```
Input:  Silver Parquet + Gold patient demographics

Output: s3://med-z1/gold/immunizations/patient_immunizations.parquet

Transformations:
  1. Join Silver with patient demographics (PatientSID → ICN/patient_key)
  2. Join with Dim.Location (LocationSID → location_name, location_type)
  3. Join with SStaff.Provider (ProviderSID → provider_name)
  4. Add station name lookup (Sta3n → station_name)
  5. Sort by patient_key, administered_datetime DESC (most recent first)
  6. Select final columns for UI consumption

Schema:
  - immunization_sid (BIGINT) - source system ID
  - patient_key (VARCHAR) - ICN
  - cvx_code (VARCHAR)
  - vaccine_name (VARCHAR) - standardized
  - vaccine_name_local (VARCHAR) - as entered
  - administered_datetime (TIMESTAMP)
  - series (VARCHAR) - display format
  - dose_number (INT)
  - total_doses (INT)
  - is_series_complete (BOOLEAN)
  - adverse_reaction (VARCHAR)
  - has_adverse_reaction (BOOLEAN)
  - site_of_administration (VARCHAR)
  - route (VARCHAR)
  - dose (VARCHAR)
  - provider_name (VARCHAR)
  - location_id (INT)
  - location_name (VARCHAR)
  - location_type (VARCHAR)
  - station_name (VARCHAR)
  - sta3n (SMALLINT)
  - comments (TEXT)
  - source_system (VARCHAR)
  - is_annual_vaccine (BOOLEAN)
  - is_covid_vaccine (BOOLEAN)
  - last_updated (TIMESTAMP)
```

**PostgreSQL Load:**
```
Input:  Gold Parquet

Output: PostgreSQL tables:
        - clinical.patient_immunizations (main fact table)
        - reference.vaccine (reference table with CVX codes)

Load Process:
  1. Truncate clinical.patient_immunizations
  2. Convert Polars DataFrame to Pandas
  3. Load to PostgreSQL using to_sql()
  4. Verify row counts
  5. Verify CVX code distribution
  6. Verify series completion counts
```

---

## 5. Database Schema

### 5.1 SQL Server Mock CDW Schema (CDWWork)

#### 5.1.1 Dim.Vaccine (Dimension Table)

**File:** `mock/sql-server/cdwwork/create/Dim.Vaccine.sql`

```sql
USE CDWWork;
GO

-- Vaccine dimension table (VistA File #9999999.14)
CREATE TABLE Dim.Vaccine (
    VaccineSID INT IDENTITY(1,1) PRIMARY KEY,
    VaccineName VARCHAR(255) NOT NULL,          -- Full vaccine name
    VaccineShortName VARCHAR(100),              -- Abbreviated name
    CVXCode VARCHAR(10),                        -- CDC CVX code (CRITICAL for AI)
    MVXCode VARCHAR(10),                        -- Manufacturer code
    VistaIEN VARCHAR(50),                       -- VistA internal entry number
    IsInactive CHAR(1) DEFAULT 'N',             -- Y/N inactive flag
    CreatedDateTimeUTC DATETIME2(3) DEFAULT GETUTCDATE(),

    CONSTRAINT UQ_Vaccine_CVX UNIQUE (CVXCode)
);

-- Index for CVX code lookups
CREATE INDEX IX_Vaccine_CVX ON Dim.Vaccine (CVXCode)
    WHERE CVXCode IS NOT NULL;

-- Index for active vaccines
CREATE INDEX IX_Vaccine_Active ON Dim.Vaccine (IsInactive, VaccineName)
    WHERE IsInactive = 'N';
GO
```

**Sample Data (30 vaccines from CVX list above):**

**File:** `mock/sql-server/cdwwork/insert/Dim.Vaccine.sql`

```sql
USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

INSERT INTO Dim.Vaccine
(VaccineName, VaccineShortName, CVXCode, MVXCode, VistaIEN, IsInactive)
VALUES
-- Childhood vaccines
('Hepatitis B, adolescent or pediatric', 'HEP B-PEDS', '008', 'MSD', '1', 'N'),
('Poliovirus, inactivated (IPV)', 'IPV', '010', 'PMC', '2', 'N'),
('Diphtheria, tetanus toxoids and acellular pertussis vaccine (DTaP)', 'DTAP', '020', 'PMC', '3', 'N'),
('Varicella', 'VARICELLA', '021', 'MSD', '4', 'N'),
('Haemophilus influenzae type b vaccine (Hib)', 'HIB', '048', 'MSD', '5', 'N'),
('Hepatitis A, pediatric/adolescent', 'HEP A-PEDS', '083', 'MSD', '6', 'N'),

-- Adult vaccines
('Hepatitis B, adult', 'HEP B-ADULT', '043', 'MSD', '7', 'N'),
('Hepatitis A, adult', 'HEP A-ADULT', '052', 'MSD', '8', 'N'),
('Tetanus toxoid, diphtheria toxoid, and acellular pertussis vaccine (Tdap)', 'TDAP', '115', 'GSK', '9', 'N'),
('Tetanus and diphtheria toxoids (Td), preservative free', 'TD', '113', 'MSD', '10', 'N'),

-- Pneumococcal vaccines
('Pneumococcal polysaccharide vaccine, 23 valent (PPSV23)', 'PNEUMO-23', '033', 'MSD', '11', 'N'),
('Pneumococcal conjugate vaccine, 10 valent (PCV10)', 'PCV-10', '152', 'GSK', '12', 'N'),

-- HPV vaccine
('Human Papillomavirus vaccine (HPV)', 'HPV', '062', 'MSD', '13', 'N'),

-- Meningococcal
('Meningococcal polysaccharide vaccine (MPSV4)', 'MENING-4', '103', 'PMC', '14', 'N'),

-- Shingles vaccines
('Zoster vaccine, live (Zostavax)', 'ZOSTER-LIVE', '121', 'MSD', '15', 'N'),
('Zoster vaccine recombinant (Shingrix)', 'SHINGRIX', '187', 'GSK', '16', 'N'),

-- Influenza vaccines (multiple formulations)
('Influenza, unspecified formulation', 'FLU', '088', 'PMC', '17', 'N'),
('Influenza, high dose seasonal, preservative-free', 'FLU-HD', '135', 'PMC', '18', 'N'),
('Influenza, seasonal, injectable, preservative free', 'FLU-INJ-PF', '140', 'PMC', '19', 'N'),
('Influenza, seasonal, injectable', 'FLU-INJ', '141', 'PMC', '20', 'N'),
('Influenza, injectable, quadrivalent, contains preservative', 'FLU-QUAD', '158', 'PMC', '21', 'N'),
('Influenza, injectable, quadrivalent, preservative free', 'FLU-QUAD-PF', '161', 'PMC', '22', 'N'),

-- COVID-19 vaccines
('COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose (Pfizer-BioNTech)', 'COVID-PFIZER', '208', 'PFR', '23', 'N'),
('COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose (Moderna)', 'COVID-MODERNA', '213', 'MOD', '24', 'N'),

-- Combination vaccines
('Diphtheria, tetanus toxoids and acellular pertussis vaccine, and poliovirus vaccine, inactivated (DTaP-IPV)', 'DTAP-IPV', '110', 'PMC', '25', 'N'),
('Diphtheria, tetanus, and acellular pertussis vaccine (DTaP), 5 pertussis antigens', 'DTAP-5', '106', 'PMC', '26', 'N'),
('Diphtheria, tetanus toxoids and acellular pertussis vaccine, unspecified formulation (DTaP)', 'DTAP-UNK', '107', 'PMC', '27', 'N'),

-- Additional
('Haemophilus influenzae type b vaccine (Hib), PRP-OMP', 'HIB-OMP', '049', 'MSD', '28', 'N'),
('Hepatitis B, unspecified formulation', 'HEP B-UNK', '045', 'MSD', '29', 'N'),
('Influenza, seasonal, intradermal, preservative free', 'FLU-ID-PF', '144', 'PMC', '30', 'N');
GO
```

#### 5.1.2 Immunization.PatientImmunization (Fact Table)

**File:** `mock/sql-server/cdwwork/create/Immunization.PatientImmunization.sql`

```sql
USE CDWWork;
GO

-- Create schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Immunization')
BEGIN
    EXEC('CREATE SCHEMA Immunization');
END
GO

-- Patient immunization fact table (VistA File #9000010.11)
CREATE TABLE Immunization.PatientImmunization (
    PatientImmunizationSID BIGINT IDENTITY(1,1) PRIMARY KEY,
    PatientSID BIGINT NOT NULL,                  -- FK to patient
    VaccineSID INT NOT NULL,                     -- FK to Dim.Vaccine
    VisitSID BIGINT,                             -- FK to encounter (optional)

    -- Administration details
    AdministeredDateTime DATETIME2(3) NOT NULL,  -- When vaccine was given
    Series VARCHAR(50),                          -- "1 of 2", "2 of 2", "BOOSTER", "COMPLETE"
    Dose VARCHAR(50),                            -- "0.5 ML", "1 ML"
    Route VARCHAR(50),                           -- "IM", "SC", "PO", "ID"
    SiteOfAdministration VARCHAR(100),           -- "L DELTOID", "R DELTOID", "LT ARM"

    -- Safety tracking
    Reaction VARCHAR(255),                       -- Adverse reaction text

    -- Provider and location
    OrderingProviderSID INT,                     -- FK to provider
    AdministeringProviderSID INT,                -- FK to provider
    LocationSID INT,                             -- FK to Dim.Location
    Sta3n SMALLINT,                              -- Station number

    -- Additional details
    LotNumber VARCHAR(50),                       -- Vaccine lot number
    Comments VARCHAR(MAX),                       -- Free-text clinical notes

    -- Audit fields
    IsActive BIT DEFAULT 1,
    CreatedDateTimeUTC DATETIME2(3) DEFAULT GETUTCDATE(),
    ModifiedDateTimeUTC DATETIME2(3),

    CONSTRAINT FK_PatientImmunization_Patient
        FOREIGN KEY (PatientSID) REFERENCES SPatient.SPatient(PatientSID),
    CONSTRAINT FK_PatientImmunization_Vaccine
        FOREIGN KEY (VaccineSID) REFERENCES Dim.Vaccine(VaccineSID),
    CONSTRAINT FK_PatientImmunization_Location
        FOREIGN KEY (LocationSID) REFERENCES Dim.Location(LocationSID)
);

-- Indexes
CREATE INDEX IX_PatientImmunization_Patient_Date
    ON Immunization.PatientImmunization (PatientSID, AdministeredDateTime DESC);

CREATE INDEX IX_PatientImmunization_Vaccine
    ON Immunization.PatientImmunization (VaccineSID, AdministeredDateTime DESC);

CREATE INDEX IX_PatientImmunization_Date
    ON Immunization.PatientImmunization (AdministeredDateTime DESC);

CREATE INDEX IX_PatientImmunization_Active
    ON Immunization.PatientImmunization (IsActive, PatientSID, AdministeredDateTime DESC)
    WHERE IsActive = 1;
GO
```

**Sample Data (will be populated across 8 test patients - see Appendix C):**

File: `mock/sql-server/cdwwork/insert/Immunization.PatientImmunization.sql` (to be created with 100+ rows)

### 5.2 SQL Server Mock CDW Schema (CDWWork2 - Cerner)

#### 5.2.1 ImmunizationMill.VaccineCode (Dimension)

**File:** `mock/sql-server/cdwwork2/create/ImmunizationMill.VaccineCode.sql`

```sql
USE CDWWork2;
GO

-- Create schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'ImmunizationMill')
BEGIN
    EXEC('CREATE SCHEMA ImmunizationMill');
END
GO

-- Cerner CODE_VALUE subset for vaccines
CREATE TABLE ImmunizationMill.VaccineCode (
    VaccineCodeSID BIGINT IDENTITY(1,1) PRIMARY KEY,
    CodeValue BIGINT NOT NULL,                   -- Cerner internal code
    Display VARCHAR(255) NOT NULL,               -- Display name
    Definition VARCHAR(500),                     -- Code definition
    CVXCode VARCHAR(10),                         -- Mapped to CDC CVX
    CodeSet INT DEFAULT 100,                     -- Code set identifier
    IsActive BIT DEFAULT 1,
    CreatedDateTimeUTC DATETIME2(3) DEFAULT GETUTCDATE(),

    CONSTRAINT UQ_VaccineCode_CodeValue UNIQUE (CodeValue)
);

CREATE INDEX IX_VaccineCode_CVX ON ImmunizationMill.VaccineCode (CVXCode)
    WHERE CVXCode IS NOT NULL;
GO
```

#### 5.2.2 ImmunizationMill.VaccineAdmin (Fact Table)

**File:** `mock/sql-server/cdwwork2/create/ImmunizationMill.VaccineAdmin.sql`

```sql
USE CDWWork2;
GO

-- Cerner vaccine administration event table
CREATE TABLE ImmunizationMill.VaccineAdmin (
    VaccineAdminSID BIGINT IDENTITY(1,1) PRIMARY KEY,
    PersonSID BIGINT NOT NULL,                   -- Cerner patient ID
    EncounterSID BIGINT,                         -- Cerner encounter ID
    PatientICN VARCHAR(50),                      -- Denormalized for joins

    -- Vaccine reference
    VaccineCodeSID BIGINT NOT NULL,              -- FK to VaccineCode

    -- Administration details
    AdministeredDateTime DATETIME NOT NULL,
    SeriesNumber VARCHAR(50),                    -- "1", "2", "3"
    TotalInSeries VARCHAR(50),                   -- "2", "3"
    DoseAmount VARCHAR(50),
    DoseUnit VARCHAR(50),
    RouteCode VARCHAR(50),
    BodySite VARCHAR(100),

    -- Safety
    AdverseReaction VARCHAR(255),

    -- Location and provider
    LocationName VARCHAR(200),
    ProviderName VARCHAR(200),
    Sta3n VARCHAR(10),

    -- Audit
    IsActive BIT DEFAULT 1,
    CreatedDateTimeUTC DATETIME2(3) DEFAULT GETUTCDATE(),

    CONSTRAINT FK_VaccineAdmin_VaccineCode
        FOREIGN KEY (VaccineCodeSID) REFERENCES ImmunizationMill.VaccineCode(VaccineCodeSID)
);

CREATE INDEX IX_VaccineAdmin_Person_Date
    ON ImmunizationMill.VaccineAdmin (PersonSID, AdministeredDateTime DESC);

CREATE INDEX IX_VaccineAdmin_ICN_Date
    ON ImmunizationMill.VaccineAdmin (PatientICN, AdministeredDateTime DESC);

CREATE INDEX IX_VaccineAdmin_Date
    ON ImmunizationMill.VaccineAdmin (AdministeredDateTime DESC);
GO
```

### 5.3 PostgreSQL Serving Database Schema

#### 5.3.1 clinical.patient_immunizations (Main Fact Table)

**File:** `db/ddl/create_patient_immunizations_table.sql`

```sql
-- PostgreSQL Immunizations Serving Table
-- Loaded from Gold Parquet after ETL pipeline

CREATE SCHEMA IF NOT EXISTS clinical;

DROP TABLE IF EXISTS clinical.patient_immunizations CASCADE;

CREATE TABLE clinical.patient_immunizations (
    immunization_id SERIAL PRIMARY KEY,
    patient_key VARCHAR(50) NOT NULL,            -- ICN (UNIVERSAL identifier)
    immunization_sid BIGINT NOT NULL UNIQUE,     -- Source system ID

    -- Vaccine identification (CVX-coded for AI)
    cvx_code VARCHAR(10),                        -- CDC CVX code
    vaccine_name VARCHAR(255),                   -- Standardized vaccine name
    vaccine_name_local VARCHAR(255),             -- As entered by clinician

    -- Administration details
    administered_datetime TIMESTAMP NOT NULL,
    series VARCHAR(50),                          -- Display format ("1 of 2", "Booster")
    dose_number INTEGER,                         -- Parsed dose number
    total_doses INTEGER,                         -- Parsed total in series
    is_series_complete BOOLEAN,                  -- Derived flag
    dose VARCHAR(50),                            -- Dose amount
    route VARCHAR(50),                           -- Administration route
    site_of_administration VARCHAR(100),         -- Anatomical site

    -- Safety tracking
    adverse_reaction VARCHAR(255),
    has_adverse_reaction BOOLEAN,

    -- Clinical context
    provider_name VARCHAR(100),
    location_id INTEGER,
    location_name VARCHAR(100),
    location_type VARCHAR(50),
    station_name VARCHAR(100),
    sta3n SMALLINT,

    -- Additional details
    comments TEXT,
    lot_number VARCHAR(50),

    -- Derived flags for filtering
    is_annual_vaccine BOOLEAN,                   -- Flu vaccines
    is_covid_vaccine BOOLEAN,                    -- COVID-19 vaccines

    -- Metadata
    source_system VARCHAR(20),                   -- CDWWork, CDWWork2
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Primary index: Patient lookups sorted by date
CREATE INDEX idx_immunizations_patient_date
    ON clinical.patient_immunizations (patient_key, administered_datetime DESC);

-- CVX code index for AI queries
CREATE INDEX idx_immunizations_cvx
    ON clinical.patient_immunizations (cvx_code, administered_datetime DESC);

-- Series tracking index
CREATE INDEX idx_immunizations_series
    ON clinical.patient_immunizations (patient_key, cvx_code, dose_number, administered_datetime DESC);

-- Incomplete series index for compliance checking
CREATE INDEX idx_immunizations_incomplete
    ON clinical.patient_immunizations (patient_key, is_series_complete, administered_datetime DESC)
    WHERE is_series_complete = FALSE;

-- Adverse reaction index for safety queries
CREATE INDEX idx_immunizations_reactions
    ON clinical.patient_immunizations (patient_key, has_adverse_reaction, administered_datetime DESC)
    WHERE has_adverse_reaction = TRUE;

-- Vaccine family indexes for filtering
CREATE INDEX idx_immunizations_annual
    ON clinical.patient_immunizations (patient_key, administered_datetime DESC)
    WHERE is_annual_vaccine = TRUE;

CREATE INDEX idx_immunizations_covid
    ON clinical.patient_immunizations (patient_key, administered_datetime DESC)
    WHERE is_covid_vaccine = TRUE;
```

#### 5.3.2 reference.vaccine (Reference Table)

**File:** `db/ddl/create_reference_vaccine_table.sql`

```sql
-- CVX Code Reference Table
-- Populated from CDC CVX standard codes
-- Used for vaccine name standardization and AI compliance checking

-- Create reference schema for all reference/lookup tables
CREATE SCHEMA IF NOT EXISTS reference;

CREATE TABLE IF NOT EXISTS reference.vaccine (
    cvx_code VARCHAR(10) PRIMARY KEY,
    vaccine_name VARCHAR(255) NOT NULL,
    vaccine_short_name VARCHAR(100),
    vaccine_group VARCHAR(100),                  -- Grouping for UI filters
    typical_series_pattern VARCHAR(50),          -- "3-dose", "2-dose", "Annual", etc.
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Index for vaccine group filtering
CREATE INDEX idx_reference_vaccine_group
    ON reference.vaccine (vaccine_group, vaccine_name)
    WHERE is_active = TRUE;

-- Seed data (30 vaccines from CVX list)
INSERT INTO reference.vaccine (cvx_code, vaccine_name, vaccine_short_name, vaccine_group, typical_series_pattern, is_active)
VALUES
-- Childhood vaccines
('008', 'Hepatitis B, adolescent or pediatric', 'HEP B-PEDS', 'Hepatitis', '3-dose', TRUE),
('010', 'Poliovirus, inactivated (IPV)', 'IPV', 'Polio', '4-dose', TRUE),
('020', 'Diphtheria, tetanus toxoids and acellular pertussis vaccine (DTaP)', 'DTAP', 'DTaP/Tdap', '5-dose', TRUE),
('021', 'Varicella', 'VARICELLA', 'Varicella', '2-dose', TRUE),
('048', 'Haemophilus influenzae type b vaccine (Hib)', 'HIB', 'Hib', '3-4 dose', TRUE),
('083', 'Hepatitis A, pediatric/adolescent', 'HEP A-PEDS', 'Hepatitis', '2-dose', TRUE),

-- Adult vaccines
('043', 'Hepatitis B, adult', 'HEP B-ADULT', 'Hepatitis', '3-dose', TRUE),
('052', 'Hepatitis A, adult', 'HEP A-ADULT', 'Hepatitis', '2-dose', TRUE),
('115', 'Tetanus toxoid, diphtheria toxoid, and acellular pertussis vaccine (Tdap)', 'TDAP', 'DTaP/Tdap', 'Booster', TRUE),
('113', 'Tetanus and diphtheria toxoids (Td), preservative free', 'TD', 'DTaP/Tdap', 'Booster', TRUE),

-- Pneumococcal
('033', 'Pneumococcal polysaccharide vaccine, 23 valent (PPSV23)', 'PNEUMO-23', 'Pneumococcal', 'Single or 2-dose', TRUE),
('152', 'Pneumococcal conjugate vaccine, 10 valent (PCV10)', 'PCV-10', 'Pneumococcal', '4-dose', TRUE),

-- HPV
('062', 'Human Papillomavirus vaccine (HPV)', 'HPV', 'HPV', '2-3 dose', TRUE),

-- Meningococcal
('103', 'Meningococcal polysaccharide vaccine (MPSV4)', 'MENING-4', 'Meningococcal', '1-2 dose', TRUE),

-- Shingles
('121', 'Zoster vaccine, live (Zostavax)', 'ZOSTER-LIVE', 'Zoster', 'Single', FALSE),  -- Discontinued in US
('187', 'Zoster vaccine recombinant (Shingrix)', 'SHINGRIX', 'Zoster', '2-dose', TRUE),

-- Influenza (multiple formulations, all annual)
('088', 'Influenza, unspecified formulation', 'FLU', 'Influenza', 'Annual', TRUE),
('135', 'Influenza, high dose seasonal, preservative-free', 'FLU-HD', 'Influenza', 'Annual', TRUE),
('140', 'Influenza, seasonal, injectable, preservative free', 'FLU-INJ-PF', 'Influenza', 'Annual', TRUE),
('141', 'Influenza, seasonal, injectable', 'FLU-INJ', 'Influenza', 'Annual', TRUE),
('158', 'Influenza, injectable, quadrivalent, contains preservative', 'FLU-QUAD', 'Influenza', 'Annual', TRUE),
('161', 'Influenza, injectable, quadrivalent, preservative free', 'FLU-QUAD-PF', 'Influenza', 'Annual', TRUE),
('144', 'Influenza, seasonal, intradermal, preservative free', 'FLU-ID-PF', 'Influenza', 'Annual', TRUE),

-- COVID-19
('208', 'COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose (Pfizer-BioNTech)', 'COVID-PFIZER', 'COVID-19', '2-dose primary + boosters', TRUE),
('213', 'COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose (Moderna)', 'COVID-MODERNA', 'COVID-19', '2-dose primary + boosters', TRUE),

-- Combination vaccines
('110', 'Diphtheria, tetanus toxoids and acellular pertussis vaccine, and poliovirus vaccine, inactivated (DTaP-IPV)', 'DTAP-IPV', 'DTaP/Tdap', '4-dose', TRUE),
('106', 'Diphtheria, tetanus, and acellular pertussis vaccine (DTaP), 5 pertussis antigens', 'DTAP-5', 'DTaP/Tdap', '5-dose', TRUE),
('107', 'Diphtheria, tetanus toxoids and acellular pertussis vaccine, unspecified formulation (DTaP)', 'DTAP-UNK', 'DTaP/Tdap', '5-dose', TRUE),

-- Additional
('049', 'Haemophilus influenzae type b vaccine (Hib), PRP-OMP', 'HIB-OMP', 'Hib', '2-3 dose', TRUE),
('045', 'Hepatitis B, unspecified formulation', 'HEP B-UNK', 'Hepatitis', '3-dose', TRUE);
```

---
## 6. ETL Pipeline Design

### 6.1 Bronze Layer: Source Extraction

**Files:**
- `etl/bronze_immunizations.py` - Extract from CDWWork (VistA)
- `etl/bronze_cdwwork2_immunizations.py` - Extract from CDWWork2 (Cerner)

**Bronze Pattern (CDWWork):**

```python
# etl/bronze_immunizations.py
import pyodbc
import polars as pl
from config import SQL_SERVER_CONNECTION_STRING
from etl.s3_client import upload_parquet_to_minio

def extract_dim_vaccine():
    """Extract Dim.Vaccine dimension table"""
    query = """
    SELECT
        VaccineSID,
        VaccineName,
        VaccineShortName,
        CVXCode,
        MVXCode,
        VistaIEN,
        IsInactive,
        CreatedDateTimeUTC
    FROM CDWWork.Dim.Vaccine
    WHERE IsInactive = 'N'
    """

    conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
    df = pl.read_database(query, conn)

    # Add metadata
    df = df.with_columns([
        pl.lit("CDWWork").alias("source_system"),
        pl.lit(datetime.utcnow()).alias("extraction_timestamp")
    ])

    # Upload to MinIO
    upload_parquet_to_minio(
        df,
        bucket="med-z1",
        object_name="bronze/cdwwork/vaccine_dim/vaccine_dim_raw.parquet"
    )

    print(f"Bronze: Extracted {df.shape[0]} vaccine definitions")
    return df

def extract_patient_immunization():
    """Extract Immunization.PatientImmunization fact table"""
    query = """
    SELECT
        pi.PatientImmunizationSID,
        pi.PatientSID,
        pi.VaccineSID,
        pi.VisitSID,
        pi.AdministeredDateTime,
        pi.Series,
        pi.Dose,
        pi.Route,
        pi.SiteOfAdministration,
        pi.Reaction,
        pi.OrderingProviderSID,
        pi.AdministeringProviderSID,
        pi.LocationSID,
        pi.Sta3n,
        pi.LotNumber,
        pi.Comments,
        pi.IsActive,
        pi.CreatedDateTimeUTC
    FROM CDWWork.Immunization.PatientImmunization pi
    WHERE pi.IsActive = 1
    """

    conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
    df = pl.read_database(query, conn)

    # Add metadata
    df = df.with_columns([
        pl.lit("CDWWork").alias("source_system"),
        pl.lit(datetime.utcnow()).alias("extraction_timestamp")
    ])

    # Upload to MinIO
    upload_parquet_to_minio(
        df,
        bucket="med-z1",
        object_name="bronze/cdwwork/immunization/patient_immunization_raw.parquet"
    )

    print(f"Bronze: Extracted {df.shape[0]} immunization records")
    return df

def main():
    """Execute Bronze extraction"""
    print("=== Bronze ETL: Immunizations (CDWWork) ===")

    df_vaccine = extract_dim_vaccine()
    df_immunization = extract_patient_immunization()

    print(f"Bronze Complete: {df_vaccine.shape[0]} vaccines, {df_immunization.shape[0]} immunizations")

if __name__ == "__main__":
    main()
```

**Bronze Pattern (CDWWork2 - Cerner):**

```python
# etl/bronze_cdwwork2_immunizations.py
import pyodbc
import polars as pl
from config import SQL_SERVER_CONNECTION_STRING
from etl.s3_client import upload_parquet_to_minio

def extract_vaccine_code():
    """Extract ImmunizationMill.VaccineCode dimension"""
    query = """
    SELECT
        VaccineCodeSID,
        CodeValue,
        Display,
        Definition,
        CVXCode,
        CodeSet,
        IsActive,
        CreatedDateTimeUTC
    FROM CDWWork2.ImmunizationMill.VaccineCode
    WHERE IsActive = 1
    """

    conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
    df = pl.read_database(query, conn)

    df = df.with_columns([
        pl.lit("CDWWork2").alias("source_system"),
        pl.lit(datetime.utcnow()).alias("extraction_timestamp")
    ])

    upload_parquet_to_minio(
        df,
        bucket="med-z1",
        object_name="bronze/cdwwork2/immunization_mill/vaccine_code_raw.parquet"
    )

    print(f"Bronze (Cerner): Extracted {df.shape[0]} vaccine codes")
    return df

def extract_vaccine_admin():
    """Extract ImmunizationMill.VaccineAdmin fact table"""
    query = """
    SELECT
        va.VaccineAdminSID,
        va.PersonSID,
        va.EncounterSID,
        va.PatientICN,
        va.VaccineCodeSID,
        va.AdministeredDateTime,
        va.SeriesNumber,
        va.TotalInSeries,
        va.DoseAmount,
        va.DoseUnit,
        va.RouteCode,
        va.BodySite,
        va.AdverseReaction,
        va.LocationName,
        va.ProviderName,
        va.Sta3n,
        va.IsActive,
        va.CreatedDateTimeUTC
    FROM CDWWork2.ImmunizationMill.VaccineAdmin va
    WHERE va.IsActive = 1
    """

    conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
    df = pl.read_database(query, conn)

    df = df.with_columns([
        pl.lit("CDWWork2").alias("source_system"),
        pl.lit(datetime.utcnow()).alias("extraction_timestamp")
    ])

    upload_parquet_to_minio(
        df,
        bucket="med-z1",
        object_name="bronze/cdwwork2/immunization_mill/vaccine_admin_raw.parquet"
    )

    print(f"Bronze (Cerner): Extracted {df.shape[0]} vaccine administrations")
    return df

def main():
    """Execute Bronze extraction for CDWWork2"""
    print("=== Bronze ETL: Immunizations (CDWWork2 - Cerner) ===")

    df_vaccine_code = extract_vaccine_code()
    df_vaccine_admin = extract_vaccine_admin()

    print(f"Bronze Complete: {df_vaccine_code.shape[0]} codes, {df_vaccine_admin.shape[0]} administrations")

if __name__ == "__main__":
    main()
```

### 6.2 Silver Layer: Harmonization and Standardization

**File:** `etl/silver_immunizations.py`

**Silver Transformations:**
1. Join VistA fact table with Dim.Vaccine to get CVX codes
2. Join Cerner fact table with VaccineCode to map to CVX
3. Harmonize column names across systems
4. Parse series information (extract dose_number, total_doses)
5. Calculate series completion status
6. Standardize anatomical sites
7. Add derived boolean flags
8. Deduplicate cross-system records

```python
# etl/silver_immunizations.py
import polars as pl
from etl.s3_client import read_parquet_from_minio, upload_parquet_to_minio
import re

def parse_series_info(series_str: str) -> dict:
    """
    Parse series string into components.
    Examples:
        "1 of 2" -> {"dose_number": 1, "total_doses": 2, "is_complete": False}
        "2 of 2" -> {"dose_number": 2, "total_doses": 2, "is_complete": True}
        "BOOSTER" -> {"dose_number": None, "total_doses": None, "is_complete": True}
        "COMPLETE" -> {"dose_number": None, "total_doses": None, "is_complete": True}
    """
    if not series_str or pd.isna(series_str):
        return {"dose_number": None, "total_doses": None, "is_complete": False}

    series_str = series_str.upper().strip()

    # Check for completion keywords
    if series_str in ["COMPLETE", "BOOSTER"]:
        return {"dose_number": None, "total_doses": None, "is_complete": True}

    # Parse "X of Y" pattern
    match = re.match(r"(\d+)\s*(?:of|OF)\s*(\d+)", series_str)
    if match:
        dose_num = int(match.group(1))
        total = int(match.group(2))
        return {
            "dose_number": dose_num,
            "total_doses": total,
            "is_complete": (dose_num == total)
        }

    # Single number (assume dose number, unknown total)
    match = re.match(r"^(\d+)$", series_str)
    if match:
        return {"dose_number": int(match.group(1)), "total_doses": None, "is_complete": False}

    return {"dose_number": None, "total_doses": None, "is_complete": False}

def standardize_site(site: str) -> str:
    """Standardize anatomical site names"""
    if not site:
        return None

    site = site.upper().strip()

    # Mapping dictionary
    site_map = {
        "L DELTOID": "Left Deltoid",
        "R DELTOID": "Right Deltoid",
        "LT DELTOID": "Left Deltoid",
        "RT DELTOID": "Right Deltoid",
        "LEFT DELTOID": "Left Deltoid",
        "RIGHT DELTOID": "Right Deltoid",
        "L ARM": "Left Arm",
        "R ARM": "Right Arm",
        "LT ARM": "Left Arm",
        "RT ARM": "Right Arm",
        "L THIGH": "Left Thigh",
        "R THIGH": "Right Thigh",
        "ORAL": "Oral",
        "INTRANASAL": "Intranasal",
        "NASAL": "Intranasal"
    }

    return site_map.get(site, site.title())

def process_vista_immunizations():
    """Process VistA (CDWWork) immunizations"""
    print("Silver: Processing VistA immunizations...")

    # Read Bronze data
    df_vaccine = read_parquet_from_minio("med-z1", "bronze/cdwwork/vaccine_dim/vaccine_dim_raw.parquet")
    df_immun = read_parquet_from_minio("med-z1", "bronze/cdwwork/immunization/patient_immunization_raw.parquet")

    # Join fact with dimension to get CVX codes and vaccine names
    df_joined = df_immun.join(
        df_vaccine,
        left_on="VaccineSID",
        right_on="VaccineSID",
        how="left"
    )

    # Standardize column names for harmonization
    df_silver = df_joined.select([
        pl.col("PatientImmunizationSID").alias("immunization_sid"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("CVXCode").alias("cvx_code"),
        pl.col("VaccineName").str.to_uppercase().str.strip_chars().alias("vaccine_name_standardized"),
        pl.col("VaccineName").alias("vaccine_name_local"),
        pl.col("AdministeredDateTime").alias("administered_datetime"),
        pl.col("Series").alias("series"),
        pl.col("Dose").alias("dose"),
        pl.col("Route").str.to_uppercase().alias("route"),
        pl.col("SiteOfAdministration").alias("site_of_administration_raw"),
        pl.col("Reaction").alias("adverse_reaction"),
        pl.col("OrderingProviderSID").alias("provider_sid"),
        pl.col("LocationSID").alias("location_sid"),
        pl.col("Sta3n").alias("sta3n"),
        pl.col("LotNumber").alias("lot_number"),
        pl.col("Comments").alias("comments"),
        pl.lit("CDWWork").alias("source_system")
    ])

    # Parse series information
    series_parsed = df_silver.with_columns([
        pl.col("series").map_elements(
            lambda x: parse_series_info(x)["dose_number"],
            return_dtype=pl.Int32
        ).alias("dose_number"),
        pl.col("series").map_elements(
            lambda x: parse_series_info(x)["total_doses"],
            return_dtype=pl.Int32
        ).alias("total_doses"),
        pl.col("series").map_elements(
            lambda x: parse_series_info(x)["is_complete"],
            return_dtype=pl.Boolean
        ).alias("is_series_complete")
    ])

    # Standardize anatomical sites
    series_parsed = series_parsed.with_columns([
        pl.col("site_of_administration_raw").map_elements(
            standardize_site,
            return_dtype=pl.Utf8
        ).alias("site_of_administration")
    ]).drop("site_of_administration_raw")

    # Add derived flags
    flu_cvx = ["088", "135", "140", "141", "144", "158", "161"]
    covid_cvx = ["208", "212", "213", "217", "218", "219", "221", "225", "229"]

    df_final = series_parsed.with_columns([
        (pl.col("adverse_reaction").is_not_null() &
         (pl.col("adverse_reaction").str.strip_chars() != "")).alias("has_adverse_reaction"),
        pl.col("cvx_code").is_in(flu_cvx).alias("is_annual_vaccine"),
        pl.col("cvx_code").is_in(covid_cvx).alias("is_covid_vaccine")
    ])

    print(f"Silver (VistA): Processed {df_final.shape[0]} immunizations")
    return df_final

def process_cerner_immunizations():
    """Process Cerner (CDWWork2) immunizations"""
    print("Silver: Processing Cerner immunizations...")

    # Read Bronze data
    df_vaccine_code = read_parquet_from_minio("med-z1", "bronze/cdwwork2/immunization_mill/vaccine_code.parquet")
    df_vaccine_admin = read_parquet_from_minio("med-z1", "bronze/cdwwork2/immunization_mill/vaccine_admin.parquet")

    # Join to get CVX codes
    df_joined = df_vaccine_admin.join(
        df_vaccine_code,
        left_on="VaccineCodeSID",
        right_on="VaccineCodeSID",
        how="left"
    )

    # Harmonize to match VistA structure
    df_silver = df_joined.select([
        pl.col("VaccineAdminSID").alias("immunization_sid"),
        pl.col("PersonSID").alias("patient_sid"),  # Will need to map to PatientSID in Gold
        pl.col("CVXCode").alias("cvx_code"),
        pl.col("Display").str.to_uppercase().str.strip_chars().alias("vaccine_name_standardized"),
        pl.col("Display").alias("vaccine_name_local"),
        pl.col("AdministeredDateTime").alias("administered_datetime"),
        # Construct series from SeriesNumber and TotalInSeries
        (pl.col("SeriesNumber").cast(pl.Utf8) + " of " + pl.col("TotalInSeries").cast(pl.Utf8)).alias("series"),
        (pl.col("DoseAmount").cast(pl.Utf8) + " " + pl.col("DoseUnit")).alias("dose"),
        pl.col("RouteCode").str.to_uppercase().alias("route"),
        pl.col("BodySite").alias("site_of_administration_raw"),
        pl.col("AdverseReaction").alias("adverse_reaction"),
        pl.lit(None).cast(pl.Int32).alias("provider_sid"),  # Will parse from ProviderName in Gold
        pl.lit(None).cast(pl.Int32).alias("location_sid"),  # Will parse from LocationName in Gold
        pl.col("Sta3n").cast(pl.Int16).alias("sta3n"),
        pl.lit(None).cast(pl.Utf8).alias("lot_number"),
        pl.lit(None).cast(pl.Utf8).alias("comments"),
        pl.lit("CDWWork2").alias("source_system")
    ])

    # Parse series (same logic as VistA)
    series_parsed = df_silver.with_columns([
        pl.col("series").map_elements(
            lambda x: parse_series_info(x)["dose_number"],
            return_dtype=pl.Int32
        ).alias("dose_number"),
        pl.col("series").map_elements(
            lambda x: parse_series_info(x)["total_doses"],
            return_dtype=pl.Int32
        ).alias("total_doses"),
        pl.col("series").map_elements(
            lambda x: parse_series_info(x)["is_complete"],
            return_dtype=pl.Boolean
        ).alias("is_series_complete")
    ])

    # Standardize sites
    series_parsed = series_parsed.with_columns([
        pl.col("site_of_administration_raw").map_elements(
            standardize_site,
            return_dtype=pl.Utf8
        ).alias("site_of_administration")
    ]).drop("site_of_administration_raw")

    # Add derived flags
    flu_cvx = ["088", "135", "140", "141", "144", "158", "161"]
    covid_cvx = ["208", "212", "213", "217", "218", "219", "221", "225", "229"]

    df_final = series_parsed.with_columns([
        (pl.col("adverse_reaction").is_not_null() &
         (pl.col("adverse_reaction").str.strip_chars() != "")).alias("has_adverse_reaction"),
        pl.col("cvx_code").is_in(flu_cvx).alias("is_annual_vaccine"),
        pl.col("cvx_code").is_in(covid_cvx).alias("is_covid_vaccine")
    ])

    print(f"Silver (Cerner): Processed {df_final.shape[0]} immunizations")
    return df_final

def merge_and_deduplicate(df_vista, df_cerner):
    """
    Merge VistA and Cerner data, deduplicating any cross-system records.
    Deduplication logic: Same patient_sid + cvx_code + administered_datetime (within 1 hour)
    """
    print("Silver: Merging and deduplicating cross-system records...")

    # Concatenate
    df_combined = pl.concat([df_vista, df_cerner])

    # Sort by patient, CVX, datetime, source (VistA preferred)
    df_sorted = df_combined.sort([
        "patient_sid",
        "cvx_code",
        "administered_datetime",
        "source_system"  # CDWWork comes before CDWWork2 alphabetically
    ])

    # Deduplicate: Keep first (VistA preferred) if same patient, CVX, datetime within 1 hour
    # For MVP, simple approach: drop exact duplicates by key columns
    df_deduped = df_sorted.unique(
        subset=["patient_sid", "cvx_code", "administered_datetime"],
        keep="first"
    )

    removed = df_combined.shape[0] - df_deduped.shape[0]
    print(f"Silver: Removed {removed} duplicate records")

    return df_deduped

def main():
    """Execute Silver ETL"""
    print("=== Silver ETL: Immunizations ===")

    # Process both systems
    df_vista = process_vista_immunizations()
    df_cerner = process_cerner_immunizations()

    # Merge and deduplicate
    df_silver = merge_and_deduplicate(df_vista, df_cerner)

    # Upload to MinIO
    upload_parquet_to_minio(
        df_silver,
        bucket="med-z1",
        object_name="silver/immunizations/immunizations_cleaned.parquet"
    )

    print(f"Silver Complete: {df_silver.shape[0]} total immunization records")

    # Print summary stats
    print("\nSilver Summary:")
    print(f"  Total records: {df_silver.shape[0]}")
    print(f"  Unique patients: {df_silver['patient_sid'].n_unique()}")
    print(f"  Unique CVX codes: {df_silver['cvx_code'].n_unique()}")
    print(f"  Date range: {df_silver['administered_datetime'].min()} to {df_silver['administered_datetime'].max()}")
    print(f"  Records with adverse reactions: {df_silver['has_adverse_reaction'].sum()}")
    print(f"  Incomplete series: {(~df_silver['is_series_complete']).sum()}")

if __name__ == "__main__":
    main()
```

### 6.3 Gold Layer: Patient-Centric View

**File:** `etl/gold_immunizations.py`

**Gold Transformations:**
1. Join Silver with patient demographics (PatientSID → ICN/patient_key)
2. Join with Dim.Location (LocationSID → location_name, location_type)
3. Join with SStaff.Provider (ProviderSID → provider_name)
4. Add station name lookup (Sta3n → station_name)
5. Sort by patient_key, administered_datetime DESC
6. Select final columns for PostgreSQL

```python
# etl/gold_immunizations.py
import polars as pl
from etl.s3_client import read_parquet_from_minio, upload_parquet_to_minio

def main():
    """Execute Gold ETL for Immunizations"""
    print("=== Gold ETL: Immunizations ===")

    # Read Silver data
    df_silver = read_parquet_from_minio("med-z1", "silver/immunizations/immunizations_cleaned.parquet")

    # Read Gold patient demographics for ICN mapping
    df_patient = read_parquet_from_minio("med-z1", "gold/patient_demographics/patient_demographics.parquet")

    # Read location dimension for denormalized location fields
    df_location = read_parquet_from_minio("med-z1", "bronze/cdwwork/dim_location/dim_location.parquet")

    # Read provider dimension for provider names
    df_provider = read_parquet_from_minio("med-z1", "bronze/cdwwork/sstaff_provider/provider.parquet")

    # Read station dimension for station names
    df_station = read_parquet_from_minio("med-z1", "bronze/cdwwork/dim_sta3n/sta3n.parquet")

    # Join with patient demographics to get ICN (patient_key)
    df_with_patient = df_silver.join(
        df_patient.select(["PatientSID", "patient_key"]),
        left_on="patient_sid",
        right_on="PatientSID",
        how="left"
    )

    # Join with location dimension
    df_with_location = df_with_patient.join(
        df_location.select(["LocationSID", "LocationName", "LocationType"]),
        left_on="location_sid",
        right_on="LocationSID",
        how="left"
    )

    # Join with provider dimension
    df_with_provider = df_with_location.join(
        df_provider.select(["StaffSID", "StaffName"]),
        left_on="provider_sid",
        right_on="StaffSID",
        how="left"
    )

    # Join with station dimension
    df_with_station = df_with_provider.join(
        df_station.select(["Sta3n", "StationName"]),
        on="sta3n",
        how="left"
    )

    # Select final columns in UI-friendly order
    df_gold = df_with_station.select([
        pl.col("immunization_sid"),
        pl.col("patient_key"),
        pl.col("cvx_code"),
        pl.col("vaccine_name_standardized").alias("vaccine_name"),
        pl.col("vaccine_name_local"),
        pl.col("administered_datetime"),
        pl.col("series"),
        pl.col("dose_number"),
        pl.col("total_doses"),
        pl.col("is_series_complete"),
        pl.col("dose"),
        pl.col("route"),
        pl.col("site_of_administration"),
        pl.col("adverse_reaction"),
        pl.col("has_adverse_reaction"),
        pl.col("StaffName").alias("provider_name"),
        pl.col("location_sid").alias("location_id"),
        pl.col("LocationName").alias("location_name"),
        pl.col("LocationType").alias("location_type"),
        pl.col("StationName").alias("station_name"),
        pl.col("sta3n"),
        pl.col("comments"),
        pl.col("lot_number"),
        pl.col("is_annual_vaccine"),
        pl.col("is_covid_vaccine"),
        pl.col("source_system"),
        pl.current_timestamp().alias("last_updated")
    ])

    # Sort for optimal UI display (most recent first per patient)
    df_gold = df_gold.sort(["patient_key", "administered_datetime"], descending=[False, True])

    # Upload to MinIO
    upload_parquet_to_minio(
        df_gold,
        bucket="med-z1",
        object_name="gold/immunizations/patient_immunizations.parquet"
    )

    print(f"Gold Complete: {df_gold.shape[0]} immunization records")

    # Summary statistics
    print("\nGold Summary:")
    print(f"  Unique patients: {df_gold['patient_key'].n_unique()}")
    print(f"  Unique vaccines (CVX): {df_gold['cvx_code'].n_unique()}")
    print(f"  Date range: {df_gold['administered_datetime'].min()} to {df_gold['administered_datetime'].max()}")
    print(f"  COVID-19 vaccines: {df_gold['is_covid_vaccine'].sum()}")
    print(f"  Flu vaccines: {df_gold['is_annual_vaccine'].sum()}")
    print(f"  Incomplete series: {(~df_gold['is_series_complete']).sum()}")
    print(f"  Adverse reactions: {df_gold['has_adverse_reaction'].sum()}")

if __name__ == "__main__":
    main()
```

### 6.4 PostgreSQL Load

**File:** `etl/load_immunizations.py`

**Load Process:**
1. Read Gold Parquet
2. Convert to Pandas (for compatibility with PostgreSQL to_sql)
3. Truncate existing table
4. Load data
5. Verify row counts and distributions

```python
# etl/load_immunizations.py
import polars as pl
import pandas as pd
from sqlalchemy import create_engine, text
from config import POSTGRES_CONNECTION_STRING
from etl.s3_client import read_parquet_from_minio

def load_to_postgres():
    """Load Gold immunizations data to PostgreSQL"""
    print("=== PostgreSQL Load: Immunizations ===")

    # Read Gold Parquet
    df_gold = read_parquet_from_minio("med-z1", "gold/immunizations/patient_immunizations.parquet")

    # Convert Polars to Pandas for to_sql compatibility
    df_pandas = df_gold.to_pandas()

    # Connect to PostgreSQL
    engine = create_engine(POSTGRES_CONNECTION_STRING)

    # Truncate existing table
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE clinical.patient_immunizations CASCADE"))
        conn.commit()
        print("Truncated existing table")

    # Load data
    df_pandas.to_sql(
        name="patient_immunizations",
        con=engine,
        schema="clinical",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

    print(f"Loaded {len(df_pandas)} immunization records to PostgreSQL")

    # Verification queries
    with engine.connect() as conn:
        # Row count
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_immunizations"))
        count = result.scalar()
        print(f"Verification: {count} rows in clinical.patient_immunizations")

        # Unique patients
        result = conn.execute(text("SELECT COUNT(DISTINCT patient_key) FROM clinical.patient_immunizations"))
        patients = result.scalar()
        print(f"Verification: {patients} unique patients")

        # Unique vaccines
        result = conn.execute(text("SELECT COUNT(DISTINCT cvx_code) FROM clinical.patient_immunizations"))
        vaccines = result.scalar()
        print(f"Verification: {vaccines} unique vaccine types (CVX codes)")

        # Incomplete series
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM clinical.patient_immunizations
            WHERE is_series_complete = FALSE AND dose_number IS NOT NULL
        """))
        incomplete = result.scalar()
        print(f"Verification: {incomplete} incomplete vaccine series")

        # Adverse reactions
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM clinical.patient_immunizations
            WHERE has_adverse_reaction = TRUE
        """))
        reactions = result.scalar()
        print(f"Verification: {reactions} vaccines with adverse reactions")

        # Sample patient distribution
        result = conn.execute(text("""
            SELECT patient_key, COUNT(*) as immunization_count
            FROM clinical.patient_immunizations
            GROUP BY patient_key
            ORDER BY immunization_count DESC
            LIMIT 8
        """))
        print("\nTop 8 patients by immunization count:")
        for row in result:
            print(f"  {row[0]}: {row[1]} immunizations")

def main():
    """Execute PostgreSQL load"""
    load_to_postgres()
    print("\n=== PostgreSQL Load Complete ===")

if __name__ == "__main__":
    main()
```

### 6.5 ETL Execution Order

**Full Pipeline Execution:**

```bash
# Step 1: Bronze extraction (both systems)
python -m etl.bronze_immunizations
python -m etl.bronze_cdwwork2_immunizations

# Step 2: Silver harmonization
python -m etl.silver_immunizations

# Step 3: Gold patient-centric transformation
python -m etl.gold_immunizations

# Step 4: PostgreSQL load
python -m etl.load_immunizations

# Verify in PostgreSQL
docker exec -it postgres16 psql -U postgres -d medz1 -c "\
    SELECT patient_key, COUNT(*) as immunization_count \
    FROM clinical.patient_immunizations \
    GROUP BY patient_key \
    ORDER BY patient_key;"
```

**Expected Output:**
- Bronze: 4 Parquet files (2 VistA, 2 Cerner)
- Silver: 1 harmonized Parquet file (~140-180 records)
- Gold: 1 patient-centric Parquet file with ICN
- PostgreSQL: 140-180 rows in clinical.patient_immunizations

---
## 7. API Endpoints

### 7.1 API Routing Pattern Decision

**Pattern B: Dedicated Router File**

Following `docs/spec/med-z1-architecture.md` Section 3, Immunizations will use **Pattern B** (dedicated router file) because:
1. ✅ Domain has a full page view with complex filtering
2. ✅ Domain requires AI integration (Phase 2)
3. ✅ Multiple page routes (widget, full page, detail views)
4. ✅ Separation improves maintainability

**Files:**
- `app/routes/immunizations.py` - API and page routes
- `app/db/immunizations.py` - Database query layer

### 7.2 API Endpoint Specifications

#### 7.2.1 JSON API Endpoints

**File:** `app/routes/immunizations.py`

```python
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime, timedelta
from app.db import immunizations as db_immunizations

router = APIRouter(prefix="/api/patient", tags=["immunizations"])

@router.get("/{icn}/immunizations")
async def get_patient_immunizations(
    icn: str,
    limit: Optional[int] = Query(100, description="Max records to return"),
    days: Optional[int] = Query(None, description="Filter to last N days"),
    vaccine_family: Optional[str] = Query(None, description="Filter by vaccine group"),
    series_status: Optional[str] = Query(None, description="all, complete, incomplete, single"),
    sort_by: Optional[str] = Query("date_desc", description="Sort order")
) -> JSONResponse:
    """
    Get all immunizations for a patient with optional filtering.

    Query Parameters:
    - limit: Maximum number of records (default 100)
    - days: Filter to last N days (e.g., 90, 180, 365)
    - vaccine_family: Filter by vaccine group (Influenza, COVID-19, Hepatitis, etc.)
    - series_status: Filter by series completion (all, complete, incomplete, single)
    - sort_by: Sort order (date_desc, date_asc, vaccine_name)

    Returns:
    - JSON array of immunization objects
    """
    try:
        # Calculate date filter if specified
        date_filter = None
        if days:
            date_filter = datetime.now() - timedelta(days=days)

        # Query database
        immunizations = db_immunizations.get_all_immunizations(
            icn=icn,
            limit=limit,
            after_date=date_filter,
            vaccine_family=vaccine_family,
            series_status=series_status,
            sort_by=sort_by
        )

        return JSONResponse(content={
            "patient_icn": icn,
            "count": len(immunizations),
            "immunizations": immunizations
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching immunizations: {str(e)}")


@router.get("/{icn}/immunizations/recent")
async def get_recent_immunizations(icn: str, limit: int = 8) -> JSONResponse:
    """
    Get recent immunizations for dashboard widget.
    Returns most recent 6-8 vaccines, sorted by date descending.
    """
    try:
        immunizations = db_immunizations.get_recent_immunizations(icn, limit=limit)

        return JSONResponse(content={
            "patient_icn": icn,
            "count": len(immunizations),
            "immunizations": immunizations
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent immunizations: {str(e)}")


@router.get("/{icn}/immunizations/{immunization_id}/details")
async def get_immunization_details(icn: str, immunization_id: int) -> JSONResponse:
    """
    Get full details for a specific immunization.
    Includes all fields including comments, lot number, provider info.
    """
    try:
        details = db_immunizations.get_immunization_details(icn, immunization_id)

        if not details:
            raise HTTPException(status_code=404, detail="Immunization not found")

        return JSONResponse(content=details)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching immunization details: {str(e)}")


@router.get("/{icn}/immunizations/series/{cvx_code}")
async def get_vaccine_series_status(icn: str, cvx_code: str) -> JSONResponse:
    """
    Get series status for a specific vaccine (CVX code).
    Used by AI tools for compliance checking.

    Returns:
    - doses_received: List of administration dates
    - series_complete: Boolean
    - next_due_date: Calculated based on vaccine rules (if applicable)
    """
    try:
        series_status = db_immunizations.get_vaccine_series_status(icn, cvx_code)

        return JSONResponse(content=series_status)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching series status: {str(e)}")


@router.get("/{icn}/immunizations/summary")
async def get_immunizations_summary(icn: str) -> JSONResponse:
    """
    Get summary statistics for patient immunizations.
    Used for dashboard and AI context.

    Returns:
    - total_count: Total immunizations on record
    - incomplete_series: Count of incomplete multi-dose series
    - adverse_reactions: Count of vaccines with adverse reactions
    - vaccine_families: Count by vaccine group
    - most_recent: Most recent immunization date
    """
    try:
        summary = db_immunizations.get_immunizations_summary(icn)

        return JSONResponse(content=summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching immunizations summary: {str(e)}")
```

#### 7.2.2 HTML Widget Endpoint

```python
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard/widget/immunizations/{icn}", response_class=HTMLResponse)
async def immunizations_widget(request: Request, icn: str):
    """
    Render immunizations widget for dashboard (1x1 size).
    Shows 6-8 most recent vaccines.
    """
    try:
        # Get recent immunizations
        immunizations = db_immunizations.get_recent_immunizations(icn, limit=8)

        return templates.TemplateResponse(
            "widgets/immunizations_widget.html",
            {
                "request": request,
                "patient_icn": icn,
                "immunizations": immunizations,
                "count": len(immunizations)
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "widgets/immunizations_widget.html",
            {
                "request": request,
                "patient_icn": icn,
                "error": str(e),
                "immunizations": [],
                "count": 0
            }
        )
```

#### 7.2.3 Full Page Endpoint

```python
page_router = APIRouter(tags=["immunizations-pages"])

@page_router.get("/immunizations", response_class=HTMLResponse)
async def immunizations_redirect(request: Request):
    """Redirect to immunizations page for current patient"""
    # Get current patient from CCOW or session
    current_patient_icn = request.state.user.get("current_patient_icn")

    if not current_patient_icn:
        raise HTTPException(status_code=400, detail="No active patient selected")

    return RedirectResponse(url=f"/patient/{current_patient_icn}/immunizations")


@page_router.get("/patient/{icn}/immunizations", response_class=HTMLResponse)
async def immunizations_page(
    request: Request,
    icn: str,
    days: Optional[int] = Query(None, description="Filter to last N days"),
    vaccine_family: Optional[str] = Query(None, description="Filter by vaccine group"),
    series_status: Optional[str] = Query("all", description="Filter by series status")
):
    """
    Render full immunizations page with filtering.

    Query Parameters:
    - days: 30, 90, 180, 365, None (all)
    - vaccine_family: Influenza, COVID-19, Hepatitis, DTaP/Tdap, etc., None (all)
    - series_status: all, complete, incomplete, single
    """
    try:
        # Get patient demographics for header
        patient = db_patient.get_patient_by_icn(icn)

        # Calculate date filter
        date_filter = None
        if days:
            date_filter = datetime.now() - timedelta(days=days)

        # Query immunizations with filters
        immunizations = db_immunizations.get_all_immunizations(
            icn=icn,
            after_date=date_filter,
            vaccine_family=vaccine_family,
            series_status=series_status,
            sort_by="date_desc"
        )

        # Get summary for stats display
        summary = db_immunizations.get_immunizations_summary(icn)

        # Get vaccine families for filter dropdown (distinct from data)
        vaccine_families = db_immunizations.get_vaccine_families(icn)

        return templates.TemplateResponse(
            "patient_immunizations.html",
            {
                "request": request,
                "patient": patient,
                "immunizations": immunizations,
                "summary": summary,
                "vaccine_families": vaccine_families,
                # Current filter state
                "filter_days": days,
                "filter_vaccine_family": vaccine_family,
                "filter_series_status": series_status
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering immunizations page: {str(e)}")
```

### 7.3 Database Query Layer

**File:** `app/db/immunizations.py`

```python
# app/db/immunizations.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from app.db.connection import get_db_connection

def get_all_immunizations(
    icn: str,
    limit: int = 100,
    after_date: Optional[datetime] = None,
    vaccine_family: Optional[str] = None,
    series_status: Optional[str] = None,
    sort_by: str = "date_desc"
) -> List[Dict[str, Any]]:
    """
    Get all immunizations for a patient with optional filters.
    """
    # Build WHERE clause
    where_clauses = ["patient_key = :icn"]
    params = {"icn": icn, "limit": limit}

    if after_date:
        where_clauses.append("administered_datetime >= :after_date")
        params["after_date"] = after_date

    if vaccine_family and vaccine_family != "all":
        # Join with reference.vaccine to filter by vaccine_group
        where_clauses.append("rv.vaccine_group = :vaccine_family")
        params["vaccine_family"] = vaccine_family

    if series_status and series_status != "all":
        if series_status == "complete":
            where_clauses.append("is_series_complete = TRUE")
        elif series_status == "incomplete":
            where_clauses.append("is_series_complete = FALSE AND dose_number IS NOT NULL")
        elif series_status == "single":
            where_clauses.append("dose_number IS NULL AND total_doses IS NULL")

    where_sql = " AND ".join(where_clauses)

    # Build ORDER BY clause
    order_by_map = {
        "date_desc": "administered_datetime DESC",
        "date_asc": "administered_datetime ASC",
        "vaccine_name": "vaccine_name ASC, administered_datetime DESC"
    }
    order_by = order_by_map.get(sort_by, "administered_datetime DESC")

    # Build query
    query = text(f"""
        SELECT
            pi.immunization_id,
            pi.patient_key,
            pi.cvx_code,
            pi.vaccine_name,
            pi.vaccine_name_local,
            pi.administered_datetime,
            pi.series,
            pi.dose_number,
            pi.total_doses,
            pi.is_series_complete,
            pi.dose,
            pi.route,
            pi.site_of_administration,
            pi.adverse_reaction,
            pi.has_adverse_reaction,
            pi.provider_name,
            pi.location_name,
            pi.location_type,
            pi.station_name,
            pi.is_annual_vaccine,
            pi.is_covid_vaccine,
            rv.vaccine_group,
            rv.typical_series_pattern
        FROM clinical.patient_immunizations pi
        LEFT JOIN reference.vaccine rv ON pi.cvx_code = rv.cvx_code
        WHERE {where_sql}
        ORDER BY {order_by}
        LIMIT :limit
    """)

    conn = get_db_connection()
    result = conn.execute(query, params)
    rows = result.fetchall()

    immunizations = []
    for row in rows:
        immunizations.append({
            "immunization_id": row[0],
            "patient_key": row[1],
            "cvx_code": row[2],
            "vaccine_name": row[3],
            "vaccine_name_local": row[4],
            "administered_datetime": row[5].isoformat() if row[5] else None,
            "series": row[6],
            "dose_number": row[7],
            "total_doses": row[8],
            "is_series_complete": row[9],
            "dose": row[10],
            "route": row[11],
            "site_of_administration": row[12],
            "adverse_reaction": row[13],
            "has_adverse_reaction": row[14],
            "provider_name": row[15],
            "location_name": row[16],
            "location_type": row[17],
            "station_name": row[18],
            "is_annual_vaccine": row[19],
            "is_covid_vaccine": row[20],
            "vaccine_group": row[21],
            "typical_series_pattern": row[22]
        })

    return immunizations


def get_recent_immunizations(icn: str, limit: int = 8) -> List[Dict[str, Any]]:
    """Get most recent immunizations for widget display"""
    return get_all_immunizations(icn, limit=limit, sort_by="date_desc")


def get_immunization_details(icn: str, immunization_id: int) -> Optional[Dict[str, Any]]:
    """Get full details for a specific immunization"""
    query = text("""
        SELECT
            pi.immunization_id,
            pi.patient_key,
            pi.cvx_code,
            pi.vaccine_name,
            pi.vaccine_name_local,
            pi.administered_datetime,
            pi.series,
            pi.dose_number,
            pi.total_doses,
            pi.is_series_complete,
            pi.dose,
            pi.route,
            pi.site_of_administration,
            pi.adverse_reaction,
            pi.has_adverse_reaction,
            pi.provider_name,
            pi.location_name,
            pi.location_type,
            pi.station_name,
            pi.sta3n,
            pi.comments,
            pi.lot_number,
            pi.is_annual_vaccine,
            pi.is_covid_vaccine,
            pi.source_system,
            rv.vaccine_group,
            rv.typical_series_pattern,
            rv.vaccine_short_name
        FROM clinical.patient_immunizations pi
        LEFT JOIN reference.vaccine rv ON pi.cvx_code = rv.cvx_code
        WHERE pi.patient_key = :icn
          AND pi.immunization_id = :immunization_id
    """)

    conn = get_db_connection()
    result = conn.execute(query, {"icn": icn, "immunization_id": immunization_id})
    row = result.fetchone()

    if not row:
        return None

    return {
        "immunization_id": row[0],
        "patient_key": row[1],
        "cvx_code": row[2],
        "vaccine_name": row[3],
        "vaccine_name_local": row[4],
        "administered_datetime": row[5].isoformat() if row[5] else None,
        "series": row[6],
        "dose_number": row[7],
        "total_doses": row[8],
        "is_series_complete": row[9],
        "dose": row[10],
        "route": row[11],
        "site_of_administration": row[12],
        "adverse_reaction": row[13],
        "has_adverse_reaction": row[14],
        "provider_name": row[15],
        "location_name": row[16],
        "location_type": row[17],
        "station_name": row[18],
        "sta3n": row[19],
        "comments": row[20],
        "lot_number": row[21],
        "is_annual_vaccine": row[22],
        "is_covid_vaccine": row[23],
        "source_system": row[24],
        "vaccine_group": row[25],
        "typical_series_pattern": row[26],
        "vaccine_short_name": row[27]
    }


def get_vaccine_series_status(icn: str, cvx_code: str) -> Dict[str, Any]:
    """
    Get series status for a specific vaccine.
    Used by AI tools for compliance checking.
    """
    query = text("""
        SELECT
            administered_datetime,
            dose_number,
            total_doses,
            is_series_complete
        FROM clinical.patient_immunizations
        WHERE patient_key = :icn
          AND cvx_code = :cvx_code
        ORDER BY administered_datetime ASC
    """)

    conn = get_db_connection()
    result = conn.execute(query, {"icn": icn, "cvx_code": cvx_code})
    rows = result.fetchall()

    doses_received = []
    series_complete = False

    for row in rows:
        doses_received.append({
            "administered_datetime": row[0].isoformat() if row[0] else None,
            "dose_number": row[1],
            "total_doses": row[2]
        })
        # If any dose is marked complete, series is complete
        if row[3]:
            series_complete = True

    return {
        "cvx_code": cvx_code,
        "doses_received_count": len(doses_received),
        "doses_received": doses_received,
        "series_complete": series_complete
    }


def get_immunizations_summary(icn: str) -> Dict[str, Any]:
    """Get summary statistics for patient immunizations"""
    query = text("""
        SELECT
            COUNT(*) as total_count,
            COUNT(*) FILTER (WHERE is_series_complete = FALSE AND dose_number IS NOT NULL) as incomplete_series,
            COUNT(*) FILTER (WHERE has_adverse_reaction = TRUE) as adverse_reactions,
            MAX(administered_datetime) as most_recent,
            COUNT(DISTINCT cvx_code) as unique_vaccines
        FROM clinical.patient_immunizations
        WHERE patient_key = :icn
    """)

    conn = get_db_connection()
    result = conn.execute(query, {"icn": icn})
    row = result.fetchone()

    if not row:
        return {
            "total_count": 0,
            "incomplete_series": 0,
            "adverse_reactions": 0,
            "most_recent": None,
            "unique_vaccines": 0
        }

    return {
        "total_count": row[0],
        "incomplete_series": row[1],
        "adverse_reactions": row[2],
        "most_recent": row[3].isoformat() if row[3] else None,
        "unique_vaccines": row[4]
    }


def get_vaccine_families(icn: str) -> List[str]:
    """Get distinct vaccine families for filter dropdown"""
    query = text("""
        SELECT DISTINCT rv.vaccine_group
        FROM clinical.patient_immunizations pi
        JOIN reference.vaccine rv ON pi.cvx_code = rv.cvx_code
        WHERE pi.patient_key = :icn
          AND rv.vaccine_group IS NOT NULL
        ORDER BY rv.vaccine_group
    """)

    conn = get_db_connection()
    result = conn.execute(query, {"icn": icn})
    rows = result.fetchall()

    return [row[0] for row in rows]
```

---

## 8. UI/UX Design

### 8.1 Dashboard Widget (1x1)

**Template:** `app/templates/widgets/immunizations_widget.html`

**Layout:**
```
┌─────────────────────────────────────┐
│ 💉 Immunizations            (8)     │
├─────────────────────────────────────┤
│                                     │
│ COVID-19 mRNA (Pfizer)              │
│   2024-09-15  •  2 of 2  ✓          │
│                                     │
│ Influenza, injectable               │
│   2024-09-10  •  Annual             │
│                                     │
│ Shingrix                            │
│   2024-01-20  •  1 of 2  ⚠️         │
│                                     │
│ Tdap                                │
│   2023-05-14  •  Booster  ✓         │
│                                     │
│ ... (4 more)                        │
│                                     │
│ [View All Immunizations]            │
└─────────────────────────────────────┘
```

**Key Features:**
- **Header:** Shows vaccine syringe icon + total count
- **Each vaccine shows:**
  - Vaccine name (standardized, max 35 chars)
  - Administration date
  - Series status ("1 of 2", "2 of 2 COMPLETE", "Annual", "Booster")
  - Completion icon (✓ for complete, ⚠️ for incomplete series)
- **Adverse reaction indicator:** ⚠️ red icon if has_adverse_reaction = TRUE
- **Limit:** Shows 6-8 most recent
- **Link:** "View All Immunizations" navigates to full page

**HTML Template:**

```html
<!-- app/templates/widgets/immunizations_widget.html -->
<div class="widget immunizations-widget">
    <div class="widget-header">
        <h3>💉 Immunizations</h3>
        <span class="badge">{{ count }}</span>
    </div>

    <div class="widget-body">
        {% if immunizations %}
            <ul class="immunization-list">
                {% for immun in immunizations[:6] %}
                <li class="immunization-item">
                    <div class="vaccine-name">
                        {{ immun.vaccine_name }}
                        {% if immun.has_adverse_reaction %}
                            <span class="reaction-warning" title="Adverse reaction reported">⚠️</span>
                        {% endif %}
                    </div>
                    <div class="vaccine-meta">
                        <span class="vaccine-date">{{ immun.administered_datetime | format_date }}</span>
                        <span class="separator">•</span>
                        <span class="vaccine-series {{ 'complete' if immun.is_series_complete else 'incomplete' }}">
                            {{ immun.series or 'Single dose' }}
                            {% if immun.is_series_complete %}
                                ✓
                            {% elif immun.dose_number and immun.total_doses %}
                                ⚠️
                            {% endif %}
                        </span>
                    </div>
                </li>
                {% endfor %}

                {% if count > 6 %}
                <li class="immunization-more">
                    ... ({{ count - 6 }} more)
                </li>
                {% endif %}
            </ul>
        {% else %}
            <p class="empty-state">No immunizations on record</p>
        {% endif %}
    </div>

    <div class="widget-footer">
        <a href="/patient/{{ patient_icn }}/immunizations" class="view-all-link">
            View All Immunizations →
        </a>
    </div>
</div>
```

**CSS Styling:**

```css
/* app/static/css/widgets.css */
.immunizations-widget {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.immunization-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.immunization-item {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.immunization-item:last-child {
    border-bottom: none;
}

.vaccine-name {
    font-weight: 500;
    color: #333;
    margin-bottom: 4px;
}

.vaccine-meta {
    font-size: 0.85rem;
    color: #666;
}

.vaccine-series.complete {
    color: #28a745;
}

.vaccine-series.incomplete {
    color: #ffc107;
}

.reaction-warning {
    color: #dc3545;
    font-size: 1.1rem;
    margin-left: 4px;
}
```

### 8.2 Full Immunizations Page

**Template:** `app/templates/patient_immunizations.html`

**Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│ Patient: Dooree, Adam (ICN100001)            [Dashboard] [⚙️]  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ 💉 Immunizations History                                       │
│                                                                │
│ Summary: 18 total • 2 incomplete series • 1 adverse reaction   │
│                                                                │
│ Filters:                                                       │
│ [ Date Range ▼ ] [ Vaccine Family ▼ ] [ Series Status ▼ ]      │
│   All              All                  All                    │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Date         Vaccine Name           Series  Site      Provider │
│ ───────────────────────────────────────────────────────────────│
│ 2024-09-15   COVID-19 mRNA (Pfizer) 2 of 2✓ L Deltoid Smith    │
│              CVX: 208               Complete                   │
│                                                                │
│ 2024-09-10   Influenza, injectable  Annual   L Deltoid Jones   │
│              CVX: 141                                          │
│                                                                │
│ 2024-01-20   Shingrix               1 of 2⚠️  L Deltoid Brown  │
│              CVX: 187               Incomplete • Due: Apr 2024 │
│              ⚠️ Adverse Reaction: Mild arm soreness            │
│                                                                │
│ 2023-09-15   Influenza, injectable  Annual   R Deltoid Smith   │
│              CVX: 141                                          │
│                                                                │
│ ...                                                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Key Features:**
1. **Summary Statistics Bar:**
   - Total immunizations
   - Incomplete series count (actionable)
   - Adverse reactions count (safety alert)

2. **Three-Tier Filtering:**
   - **Date Range:** Last 30d, 90d, 6mo, 1yr, All (default: All)
   - **Vaccine Family:** Influenza, COVID-19, Hepatitis, DTaP/Tdap, Pneumococcal, Zoster, HPV, Other, All (default: All)
   - **Series Status:** All, Complete, Incomplete, Single-dose (default: All)

3. **Chronological Table:**
   - Date (sortable)
   - Vaccine Name with CVX code
   - Series status with visual indicators
   - Site of administration
   - Provider name

4. **Expandable Rows:**
   - Click row to expand details:
     - Full vaccine name + CVX code
     - Series pattern (e.g., "Typical: 2-dose series")
     - Complete administration details (dose, route, location)
     - Adverse reaction details (if present)
     - Provider and facility
     - Comments/notes
     - Lot number

5. **Visual Indicators:**
   - ✓ Green for complete series
   - ⚠️ Yellow/orange for incomplete series
   - ⚠️ Red for adverse reactions
   - Badge colors for vaccine families

**HTML Template (Excerpt):**

```html
<!-- app/templates/patient_immunizations.html -->
{% extends "base.html" %}

{% block content %}
<div class="page-container immunizations-page">
    <!-- Patient Header -->
    <div class="patient-header">
        <h1>💉 Immunizations History</h1>
        <p>Patient: {{ patient.name }} ({{ patient.icn }})</p>
    </div>

    <!-- Summary Statistics -->
    <div class="immunizations-summary">
        <div class="stat">
            <span class="stat-value">{{ summary.total_count }}</span>
            <span class="stat-label">Total</span>
        </div>
        <div class="stat warning">
            <span class="stat-value">{{ summary.incomplete_series }}</span>
            <span class="stat-label">Incomplete Series</span>
        </div>
        <div class="stat danger">
            <span class="stat-value">{{ summary.adverse_reactions }}</span>
            <span class="stat-label">Adverse Reactions</span>
        </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
        <form method="get" action="/patient/{{ patient.icn }}/immunizations">
            <div class="filter-group">
                <label for="filter-days">Date Range</label>
                <select name="days" id="filter-days" onchange="this.form.submit()">
                    <option value="">All</option>
                    <option value="30" {% if filter_days == 30 %}selected{% endif %}>Last 30 days</option>
                    <option value="90" {% if filter_days == 90 %}selected{% endif %}>Last 90 days</option>
                    <option value="180" {% if filter_days == 180 %}selected{% endif %}>Last 6 months</option>
                    <option value="365" {% if filter_days == 365 %}selected{% endif %}>Last year</option>
                </select>
            </div>

            <div class="filter-group">
                <label for="filter-family">Vaccine Family</label>
                <select name="vaccine_family" id="filter-family" onchange="this.form.submit()">
                    <option value="">All</option>
                    {% for family in vaccine_families %}
                        <option value="{{ family }}" {% if filter_vaccine_family == family %}selected{% endif %}>
                            {{ family }}
                        </option>
                    {% endfor %}
                </select>
            </div>

            <div class="filter-group">
                <label for="filter-series">Series Status</label>
                <select name="series_status" id="filter-series" onchange="this.form.submit()">
                    <option value="all" {% if filter_series_status == 'all' %}selected{% endif %}>All</option>
                    <option value="complete" {% if filter_series_status == 'complete' %}selected{% endif %}>Complete</option>
                    <option value="incomplete" {% if filter_series_status == 'incomplete' %}selected{% endif %}>Incomplete</option>
                    <option value="single" {% if filter_series_status == 'single' %}selected{% endif %}>Single-dose</option>
                </select>
            </div>
        </form>
    </div>

    <!-- Immunizations Table -->
    <div class="immunizations-table-container">
        {% if immunizations %}
            <table class="immunizations-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Vaccine Name</th>
                        <th>Series</th>
                        <th>Site</th>
                        <th>Provider</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {% for immun in immunizations %}
                    <tr class="immunization-row {{ 'has-reaction' if immun.has_adverse_reaction else '' }}"
                        data-immunization-id="{{ immun.immunization_id }}">
                        <td class="date-col">
                            {{ immun.administered_datetime | format_date }}
                        </td>
                        <td class="vaccine-col">
                            <div class="vaccine-name-primary">
                                {{ immun.vaccine_name }}
                                {% if immun.has_adverse_reaction %}
                                    <span class="reaction-icon" title="Adverse reaction">⚠️</span>
                                {% endif %}
                            </div>
                            <div class="vaccine-cvx">CVX: {{ immun.cvx_code }}</div>
                        </td>
                        <td class="series-col">
                            <span class="series-badge {{ 'complete' if immun.is_series_complete else 'incomplete' }}">
                                {{ immun.series or 'Single dose' }}
                                {% if immun.is_series_complete %}
                                    ✓
                                {% elif immun.dose_number and immun.total_doses %}
                                    ⚠️
                                {% endif %}
                            </span>
                        </td>
                        <td class="site-col">
                            {{ immun.site_of_administration or '—' }}
                        </td>
                        <td class="provider-col">
                            {{ immun.provider_name or '—' }}
                        </td>
                        <td class="expand-col">
                            <button class="expand-btn" onclick="toggleDetails({{ immun.immunization_id }})">
                                ▼
                            </button>
                        </td>
                    </tr>

                    <!-- Expandable Details Row (hidden by default) -->
                    <tr class="details-row" id="details-{{ immun.immunization_id }}" style="display: none;">
                        <td colspan="6">
                            <div class="immunization-details">
                                <!-- Details loaded via AJAX or pre-rendered -->
                                <div class="detail-section">
                                    <strong>Full Vaccine Name:</strong> {{ immun.vaccine_name_local }}
                                </div>
                                {% if immun.typical_series_pattern %}
                                <div class="detail-section">
                                    <strong>Typical Series:</strong> {{ immun.typical_series_pattern }}
                                </div>
                                {% endif %}
                                <div class="detail-section">
                                    <strong>Dose:</strong> {{ immun.dose or '—' }}
                                    <strong>Route:</strong> {{ immun.route or '—' }}
                                </div>
                                <div class="detail-section">
                                    <strong>Location:</strong> {{ immun.location_name or '—' }} ({{ immun.station_name }})
                                </div>
                                {% if immun.adverse_reaction %}
                                <div class="detail-section adverse-reaction-detail">
                                    <strong>⚠️ Adverse Reaction:</strong> {{ immun.adverse_reaction }}
                                </div>
                                {% endif %}
                                {% if immun.comments %}
                                <div class="detail-section">
                                    <strong>Comments:</strong> {{ immun.comments }}
                                </div>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <div class="empty-state">
                <p>No immunizations found matching the selected filters.</p>
            </div>
        {% endif %}
    </div>
</div>

<script>
function toggleDetails(immunizationId) {
    const detailsRow = document.getElementById(`details-${immunizationId}`);
    if (detailsRow.style.display === 'none') {
        detailsRow.style.display = 'table-row';
    } else {
        detailsRow.style.display = 'none';
    }
}
</script>
{% endblock %}
```

---
## 9. AI Integration Design

**Status:** Pending (Phase 3 of Immunizations domain, Phase 7 of AI Clinical Insights)

The Immunizations domain will be integrated into the AI Clinical Insights subsystem with three new tools for vaccine history querying, CDC ACIP compliance checking, and multi-dose series forecasting.

**Complete AI integration specifications are documented in:**
- **`docs/spec/ai-insight-design.md`** Section 4.6 (Use Case 6: Vaccination Compliance and Gap Analysis)
- **`docs/spec/ai-insight-design.md`** Section 6.6 (Immunization Tools - 3 detailed tool specifications with code examples)
- **`docs/spec/ai-insight-design.md`** Section 10 Phase 7 (Implementation Roadmap - Days 1-7, estimated 5-7 days)

**Tools Planned (3):**
1. **`get_immunization_history()`** - Query patient vaccine history with CVX codes
2. **`check_vaccine_compliance()`** - RAG-based CDC ACIP guideline compliance checking
3. **`forecast_next_dose()`** - Calculate due dates for multi-dose series

**Enhanced Tool:**
- **`get_patient_summary()`** - Will include recent immunizations section (last 10 vaccines, 2-year lookback)

**Use Cases Enabled:**
- "What vaccines has this patient received?"
- "Is this patient due for Shingrix?" (age 65+, 2-dose series)
- "Show me incomplete vaccine series"
- "Has the patient completed their COVID-19 primary series?"
- "Are there any vaccines with adverse reactions?"

**Data Layer Support (Already Implemented):**
- Database layer: `app/db/patient_immunizations.py` with 4 query functions
- API endpoints: `app/routes/immunizations.py` with 6 endpoints
- PostgreSQL data: 138 immunizations + 30 CVX vaccines
- 8 test patients with 11-24 immunizations each

**Implementation Timeline:**
- Days 1-3: Implement 3 immunization tools in `ai/tools/immunization_tools.py`
- Day 4: Enhance `PatientContextBuilder` with immunizations integration
- Day 5: Update system prompts and integration testing
- Days 6-7: Documentation and final QA

**Prerequisites:**
- ✅ Immunizations ETL pipeline complete (PostgreSQL data available)
- ✅ Immunizations UI complete (dashboard widget + full page)
- ✅ Query functions available in `app/db/patient_immunizations.py`
- ✅ LangGraph agent infrastructure operational (AI Clinical Insights Phases 1-5 complete)

---

## 10. Implementation Roadmap

### 10.1 Day-by-Day Plan (Days 1-12)

**Phase 1: Data Foundation (Days 1-6)** ✅ **COMPLETE (2026-01-14)**

**Day 1: SQL Server Mock Data (CDWWork)** ✅
- [x] Create `Dim.Vaccine` table with 30 CVX-coded vaccines
- [x] Create `Immunization.PatientImmunization` fact table
- [x] Populate with seed data for 8 test patients (147 records total)
- [x] Update `_master.sql` files (create and insert)
- [x] Verify data: `SELECT COUNT(*) FROM Immunization.PatientImmunization` → 147 rows

**Day 2: SQL Server Mock Data (CDWWork2 - Cerner)** ✅
- [x] Create `ImmunizationMill.VaccineCode` table (15 vaccine codes)
- [x] Create `ImmunizationMill.VaccineAdmin` fact table
- [x] Populate with seed data for 2 test patients (40 records)
- [x] Update CDWWork2 `_master.sql` files
- [x] Verify cross-system patient overlap (ICN100001, ICN100010 in both systems)

**Day 3: Bronze ETL** ✅
- [x] Implement `etl/bronze_immunizations.py` (VistA extraction)
- [x] Implement `etl/bronze_cdwwork2_immunizations.py` (Cerner extraction)
- [x] Run Bronze extraction
- [x] Verify 4 Parquet files in MinIO: `bronze/cdwwork/vaccine_dim/`, `bronze/cdwwork/immunization/`, `bronze/cdwwork2/immunization_mill/vaccine_code_raw/`, `bronze/cdwwork2/immunization_mill/vaccine_admin_raw/`
- [x] Fixed naming convention: Changed `dim_vaccine` → `vaccine_dim` (suffix pattern)

**Day 4: Silver ETL** ✅
- [x] Implement `etl/silver_immunizations.py`
- [x] Implement series parsing logic (`parse_series_info()`) - handles "1 of 2", "BOOSTER", "ANNUAL 2024"
- [x] Implement site standardization logic (`standardize_anatomical_site()`) - "L DELTOID" → "Left Deltoid"
- [x] Harmonize VistA and Cerner data structures
- [x] Implement deduplication logic (same patient+CVX+date → keep CDWWork2)
- [x] Run Silver ETL
- [x] Verify Silver Parquet: 178 harmonized records (1 duplicate removed)

**Day 5: Gold ETL + PostgreSQL Schema** ✅
- [x] Implement `etl/gold_immunizations.py`
- [x] Create `db/ddl/create_patient_immunizations_table.sql` (26 columns, 10 indexes)
- [x] Create `db/ddl/create_reference_vaccine_table.sql` with 30 CVX vaccines seeded
- [x] Run Gold ETL with Location, Provider, Sta3n lookups
- [x] Verify Gold Parquet with ICN (patient_key): 138 records (filtered to Gold demographics)

**Day 6: PostgreSQL Load + Verification** ✅
- [x] Implement `etl/load_immunizations.py`
- [x] Run full ETL pipeline (Bronze → Silver → Gold → Load)
- [x] Verify PostgreSQL:
  - [x] `clinical.patient_immunizations` has 138 rows
  - [x] `reference.vaccine` has 30 rows
  - [x] Patient distribution: 8 patients (24, 21, 18, 18, 17, 15, 14, 11 immunizations each)
  - [x] Series completion: 29 complete, 62 incomplete, 47 unknown
  - [x] Adverse reaction flags: 1 adverse reaction documented
  - [x] Vaccine types: 17 annual (influenza), 18 COVID-19

---

**Phase 2: API & UI (Days 7-8)** ✅ **COMPLETE (2026-01-14)**

---

**Day 7: API & Database Layer Implementation** ✅

- [x] Create `app/db/patient_immunizations.py` with 4 query functions:
  - [x] `get_patient_immunizations()` - With filtering: vaccine_group, cvx_code, days, incomplete_only, adverse_reactions_only
  - [x] `get_recent_immunizations()` - For widget (last 2 years, limit 5)
  - [x] `get_immunization_counts()` - Summary stats (total, annual, covid, incomplete, with_reactions, recent_2y)
  - [x] `get_vaccine_reference()` - Reference vaccine data from reference.vaccine table
- [x] Create `app/routes/immunizations.py` with 6 endpoints:
  - [x] JSON API: `GET /api/patient/{icn}/immunizations` - Full list with filtering
  - [x] JSON API: `GET /api/patient/{icn}/immunizations/recent` - Widget data
  - [x] HTML widget: `GET /api/patient/{icn}/immunizations/widget` - HTMX partial
  - [x] Full page: `GET /patient/{icn}/immunizations` - Complete page
  - [x] Filtered results: `GET /patient/{icn}/immunizations/filtered` - HTMX table rows
  - [x] Redirect route: `GET /immunizations` - CCOW-aware redirect
- [x] Registered routers in `app/main.py`
- [x] Tested database layer with ICN100001: 24 immunizations, counts verified

---

**Day 8: UI Implementation** ✅

- [x] Create `app/templates/partials/immunizations_widget.html` (1x1 widget, 103 lines)
  - [x] Summary stats section (Total, Recent 2y, Incomplete with conditional display)
  - [x] 5 most recent immunizations list with icons and badges
  - [x] Empty state and error handling
  - [x] "View All Immunizations" link
- [x] Create `app/templates/patient_immunizations.html` (195 lines)
  - [x] Breadcrumbs navigation
  - [x] Summary stats bar with 6 cards (conditional warning/danger styling)
  - [x] HTMX filtering form (vaccine group, time period, status)
  - [x] Results summary
  - [x] Responsive immunizations table (7 columns)
  - [x] Empty state handling
- [x] Create `app/templates/partials/immunizations_table_rows.html` (86 lines)
  - [x] Icon-based vaccine type indicators
  - [x] Status badges (Complete/Incomplete/Adverse Reaction)
  - [x] Expandable detail rows for reactions/comments
  - [x] Source system badges
- [x] Add CSS styling (`app/static/styles.css`)
  - [x] Immunizations widget styles (lines 1812-1925, 113 lines)
  - [x] Immunizations page styles (lines 3649-3844, 195 lines)
  - [x] Summary stat cards, table styling, vaccine/location cells, badges
- [x] Update dashboard template (`app/templates/dashboard.html`)
  - [x] Replace placeholder with real HTMX widget call
- [x] Update sidebar navigation (`app/templates/base.html`)
  - [x] Remove "disabled" class, change href to "/immunizations", add active state
- [x] Testing:
  - [x] Database layer tested with ICN100001 (24 immunizations found, counts verified)
  - [x] App imports successfully without errors
  - [x] All templates and CSS files created and verified

---

**Phase 3: AI Integration**

**Status:** Pending - See `docs/spec/ai-insight-design.md` Phase 6 for complete implementation roadmap

**Implementation Reference:**
- **Tool Specifications:** `docs/spec/ai-insight-design.md` Section 6.6 (Immunization Tools)
  - `get_immunization_history()` - Query patient vaccine history with CVX codes
  - `check_vaccine_compliance()` - CDC ACIP guideline compliance checking
  - `forecast_next_dose()` - Calculate due dates for multi-dose series
- **Implementation Roadmap:** `docs/spec/ai-insight-design.md` Section 10 Phase 6 (Days 1-7)
  - Days 1-3: Implement immunization-specific tools
  - Day 4: Enhance PatientContextBuilder service
  - Day 5: System prompts and integration testing
  - Days 6-7: Documentation and final QA
- **Estimated Effort:** 5-7 days
- **Prerequisites:** ✅ All Phase 1-2 tasks complete (ETL pipeline + UI operational)

---

### 10.2 Phase Gating

**Gate 1 (End of Day 4):** Silver ETL produces harmonized immunization data
- **Success Criteria:** 140-180 records with parsed series info, no duplicate records
- **Blocker:** If series parsing fails, pause and fix logic before Gold

**Gate 2 (End of Day 6):** PostgreSQL loaded and verified
- **Success Criteria:** All 8 test patients have 15-25 immunizations each
- **Blocker:** If row counts don't match, investigate ETL pipeline data loss

**Gate 3 (End of Day 8):** UI functional with filtering
- **Success Criteria:** Widget and full page render correctly, filters work, expandable rows function
- **Blocker:** If UI is broken, fix before starting AI integration (AI depends on stable data layer)

**Gate 4 (Phase 3 - AI Integration):** AI tools operational
- **Success Criteria:** All 5 test queries return accurate, contextually relevant responses
- **Implementation:** See `docs/spec/ai-insight-design.md` Phase 6 success criteria
- **Blocker:** If AI responses are inaccurate, revisit tool logic and system prompts

---

### 10.3 Deferred to Future Phases (Post-Phase 3 Enhancements)

**VistA RPC Broker Integration (T-0 Real-Time Data):**
- [ ] Implement VistA RPC for immunizations (VistA File #9000010.11)
- [ ] Create "Refresh from VistA" button on full page
- [ ] Session caching for Vista responses (30-min TTL)
- [ ] Merge PostgreSQL (T-1+) with Vista (T-0) data
- **Estimated Effort:** 3 days
- **Rationale for Deferral:** Immunizations are less time-sensitive than vitals or medications. Historical data (PostgreSQL) is sufficient for MVP.

**Advanced Series Tracking:**
- [ ] Bridge table for multi-reaction tracking (like Allergies pattern)
- [ ] Contraindication checking (allergic to vaccine ingredients)
- [ ] Vaccine lot recall integration
- **Estimated Effort:** 2 days
- **Rationale for Deferral:** Single adverse_reaction field sufficient for MVP

**RAG-Based CDC Compliance:**
- [ ] Vector embeddings of CDC "Pink Book" and ACIP schedules
- [ ] Semantic search for vaccine guidelines
- [ ] Automated ACIP update ingestion
- **Estimated Effort:** 5-7 days
- **Rationale for Deferral:** Deterministic rules (age-based) cover 80% of common scenarios. RAG is enhancement, not requirement.

**Immunization Registry Reporting:**
- [ ] HL7 message generation for state registries
- [ ] Batch reporting to CDC
- **Estimated Effort:** 7-10 days
- **Rationale for Deferral:** Out of scope for Phase 1. Read-only viewer, not reporting system.

**Multi-Site VistA IEN Mapping:**
- [ ] Create `Dim.VaccineVistaMapping` bridge table
- [ ] Map site-specific IENs to enterprise CVX codes
- [ ] Support multiple VistA sites with different IEN assignments
- [ ] Enable site-specific vaccine name variations
- **Estimated Effort:** 1-2 days
- **Rationale for Deferral:** CVX codes provide enterprise-wide standardization for MVP. VistaIEN currently stored as representative value. Production systems may need full site-specific mapping for data lineage and troubleshooting.
- **Schema Design:**
  ```sql
  CREATE TABLE Dim.VaccineVistaMapping (
      VaccineVistaMappingSID  INT IDENTITY(1,1) PRIMARY KEY,
      VaccineSID              INT NOT NULL,              -- FK to Dim.Vaccine
      Sta3n                   SMALLINT NOT NULL,         -- VistA site
      VistaIEN                VARCHAR(50) NOT NULL,      -- Site-specific IEN
      LocalVaccineName        VARCHAR(255),              -- Site variation
      CONSTRAINT FK_VaccineMapping_Vaccine
          FOREIGN KEY (VaccineSID) REFERENCES Dim.Vaccine(VaccineSID),
      CONSTRAINT UQ_VaccineMapping_Site_IEN
          UNIQUE (Sta3n, VistaIEN)
  );
  ```

---

### 10.4 Phase 3 Enhancement: CDC CVX Reference Data Pipeline

**Status:** 📋 Fully Documented, Implementation Deferred to Phase 3

#### 10.4.1 Overview

**Current State (Days 1-12):**
- `reference.vaccine` table created with **30 hardcoded common vaccines**
- Populated via DDL script: `db/ddl/create_reference_vaccine_table.sql`
- Covers ~90% of common adult/pediatric immunizations (flu, COVID, Shingrix, Tdap, MMR, Hepatitis, etc.)
- Sufficient for MVP and initial clinical use

**Phase 3 Enhancement:**
- Replace hardcoded vaccines with **official CDC CVX dataset** (334+ vaccines)
- Automated ETL pipeline to load and refresh CDC data
- Store CDC reference files in MinIO for version control and auditability
- Enable quarterly updates as CDC publishes new vaccine codes

**Benefits of Enhancement:**
1. ✅ **Comprehensive coverage** - All 334+ CDC-approved vaccine codes (Active + Inactive for historical data)
2. ✅ **Official source** - Direct from CDC National Center of Immunization and Respiratory Diseases (NCIRD)
3. ✅ **Automated updates** - Quarterly refresh pipeline keeps data current
4. ✅ **Audit trail** - Versioned files in MinIO track CDC updates over time
5. ✅ **Production-ready** - Meets VA data governance standards for official reference data
6. ✅ **Historical tracking** - Inactive vaccines preserved for legacy immunization records

**Rationale for Deferral:**
- 30 hardcoded vaccines provide sufficient coverage for MVP validation
- No external dependencies or download complexity during initial development (Days 1-12)
- Faster testing and iteration with known dataset
- Can enhance after core functionality is proven

#### 10.4.2 Official CDC Data Sources

**Primary Dataset: CVX Codes (Vaccine Administered)**
- **Source:** CDC National Center of Immunization and Respiratory Diseases
- **URL:** https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/cvx.txt
- **Format:** Pipe-delimited text file (|)
- **Record Count:** 334+ vaccine codes
- **Update Frequency:** Quarterly (approximately)

**Column Structure:**  

| Column | Description | Example |
|--------|-------------|---------|
| CVX Code | Numeric vaccine identifier | 208 |
| Short Description | Abbreviated name | COVID-PFIZER |
| Full Vaccine Name | Complete vaccine name | COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose (Pfizer-BioNTech) |
| Notes | Additional information | (none) |
| Status | Active, Inactive, Never Active, Non-US | Active |
| Non-US Vaccine | Boolean flag | N |
| Last Updated | Date of last CDC update | 12/17/2024 |

**Companion Dataset: CVX to Vaccine Groups Mapping**
- **URL:** https://www2a.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=vg
- **Purpose:** Maps CVX codes to disease categories (e.g., "Influenza", "COVID-19", "Hepatitis")
- **Critical for:** Populating `vaccine_group` field in `reference.vaccine` table
- **Format:** Excel, Text, XML available

**Column Structure:**

| Column | Description | Example |
|--------|-------------|---------|
| CVX Code | Matches CVX codes dataset | 208 |
| Vaccine Group Name | Disease category | COVID-19 |
| VG CVX Code | Group identifier for HL7 | 213 |
| Status | Active, Inactive | Active |

**Alternative Download Options:**
- **Excel (.xlsx):** Available from web interface for manual download
- **XML:** Available for programmatic parsing
- **PDF:** Documentation format (not recommended for ETL)

**CDC Web Interface:**
- Interactive table: https://www2a.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=cvx
- HL7 code sets documentation: https://www.cdc.gov/iis/code-sets/index.html
- Release notes: https://www.cdc.gov/iis/code-sets/downloads/vaccine-code-sets-release-notes-*.pdf

#### 10.4.3 MinIO Storage Structure

**Bucket:** `med-sandbox`

**Path Structure:**
```
med-sandbox/
  └── cdc-reference-data/
      └── cvx/
          ├── 2026-01-14/                    # Versioned by download date
          │   ├── cvx_codes.txt              # CVX codes dataset
          │   ├── vaccine_groups.txt         # CVX to Vaccine Groups mapping
          │   └── metadata.json              # Download metadata
          ├── 2026-04-15/                    # Next quarterly refresh
          │   ├── cvx_codes.txt
          │   ├── vaccine_groups.txt
          │   └── metadata.json
          └── LATEST/                        # Symlink or copy of current version
              ├── cvx_codes.txt
              ├── vaccine_groups.txt
              └── metadata.json
```

**Metadata File Example (`metadata.json`):**
```json
{
  "download_date": "2026-01-14T10:30:00Z",
  "source_url_cvx": "https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/cvx.txt",
  "source_url_vg": "https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/vax2vg_list.pdf",
  "record_count_cvx": 334,
  "record_count_vg": 298,
  "active_vaccines": 187,
  "inactive_vaccines": 147,
  "downloaded_by": "etl_script",
  "notes": "Q1 2026 quarterly refresh"
}
```

**Version Control Strategy:**
- **Keep all historical versions** in dated folders for audit trail
- **LATEST symlink** always points to current production version
- **Rollback capability** by changing LATEST symlink to previous version
- **Git-like versioning** without actual Git (stored in MinIO)

#### 10.4.4 ETL Pipeline Implementation

**New File:** `etl/load_cdc_cvx_reference.py`

**Pipeline Architecture:**
```
CDC Website → MinIO (med-sandbox) → Polars DataFrame → PostgreSQL (reference.vaccine)
     ↓                ↓                    ↓                         ↓
  Download      Version control        Transform              Production table
```

**Implementation Code:**

```python
# etl/load_cdc_cvx_reference.py
"""
Load official CDC CVX codes to reference.vaccine table.

This pipeline replaces the 30 hardcoded vaccines from the DDL script with
the complete CDC CVX dataset (334+ vaccines). Run this after Phase 2 (Day 8) to
enhance the reference data with full CDC coverage.

Usage:
    python -m etl.load_cdc_cvx_reference
"""

import polars as pl
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import json
from config import POSTGRES_CONNECTION_STRING
from etl.s3_client import read_file_from_minio, upload_file_to_minio


def download_cdc_data_to_minio(version_date: str = None):
    """
    Download CDC CVX data and store in MinIO with versioning.

    Args:
        version_date: Optional date string (YYYY-MM-DD). Defaults to today.

    Returns:
        str: Path to versioned data in MinIO
    """
    import urllib.request

    if not version_date:
        version_date = datetime.now().strftime("%Y-%m-%d")

    print(f"=== Downloading CDC CVX Data (version {version_date}) ===")

    # Download CVX codes
    cvx_url = "https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/cvx.txt"
    print(f"Downloading CVX codes from {cvx_url}...")
    cvx_data = urllib.request.urlopen(cvx_url).read().decode('utf-8')

    # Download vaccine groups (note: may need to parse from different format)
    # For now, using placeholder - would need to scrape or download Excel
    vg_url = "https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/vax2vg_list.pdf"
    # TODO: Implement vaccine groups download/parsing

    # Create metadata
    metadata = {
        "download_date": datetime.utcnow().isoformat() + "Z",
        "source_url_cvx": cvx_url,
        "source_url_vg": vg_url,
        "version_date": version_date,
        "downloaded_by": "etl_script"
    }

    # Upload to MinIO
    base_path = f"cdc-reference-data/cvx/{version_date}"

    upload_file_to_minio(
        bucket="med-sandbox",
        object_name=f"{base_path}/cvx_codes.txt",
        data=cvx_data
    )

    upload_file_to_minio(
        bucket="med-sandbox",
        object_name=f"{base_path}/metadata.json",
        data=json.dumps(metadata, indent=2)
    )

    # Also upload to LATEST
    upload_file_to_minio(
        bucket="med-sandbox",
        object_name="cdc-reference-data/cvx/LATEST/cvx_codes.txt",
        data=cvx_data
    )

    upload_file_to_minio(
        bucket="med-sandbox",
        object_name="cdc-reference-data/cvx/LATEST/metadata.json",
        data=json.dumps(metadata, indent=2)
    )

    print(f"CDC data uploaded to MinIO: {base_path}")
    return base_path


def parse_cvx_file(cvx_text: str) -> pl.DataFrame:
    """
    Parse CDC CVX pipe-delimited text file into Polars DataFrame.

    Args:
        cvx_text: Raw text content of CVX file

    Returns:
        Polars DataFrame with parsed CVX codes
    """
    print("Parsing CVX codes...")

    # Parse pipe-delimited file
    # Note: CDC file may not have header row, may need to skip first line or infer
    df = pl.read_csv(
        cvx_text.encode(),
        separator="|",
        has_header=True,
        null_values=["", "NULL"],
        infer_schema_length=1000
    )

    # Rename columns to expected format (CDC column names may vary)
    # This mapping assumes CDC structure - may need adjustment
    df = df.rename({
        "CVX": "cvx_code",
        "SHORT DESCRIPTION": "short_name",
        "FULL VACCINE NAME": "full_name",
        "VACCINE STATUS": "status",
        "LAST UPDATED": "last_updated_cdc"
    })

    print(f"Parsed {df.shape[0]} CVX codes")
    return df


def map_vaccine_groups(df_cvx: pl.DataFrame) -> pl.DataFrame:
    """
    Map CVX codes to vaccine groups (disease categories).

    For Phase 3 MVP, uses hardcoded mappings for common groups.
    Future enhancement: Parse from CDC vaccine groups file.

    Args:
        df_cvx: DataFrame with CVX codes

    Returns:
        DataFrame with vaccine_group column added
    """
    print("Mapping vaccine groups...")

    # Hardcoded vaccine group mappings for common vaccines
    # Future: Replace with CDC vaccine groups file parsing
    vaccine_group_map = {
        "COVID": "COVID-19",
        "FLU": "Influenza",
        "INFLUENZA": "Influenza",
        "HEPATITIS A": "Hepatitis",
        "HEPATITIS B": "Hepatitis",
        "HEP": "Hepatitis",
        "SHINGRIX": "Zoster",
        "ZOSTER": "Zoster",
        "TDAP": "DTaP/Tdap",
        "DTAP": "DTaP/Tdap",
        "DIPHTHERIA": "DTaP/Tdap",
        "TETANUS": "DTaP/Tdap",
        "PNEUMO": "Pneumococcal",
        "HPV": "HPV",
        "MMR": "MMR",
        "MEASLES": "MMR",
        "MUMPS": "MMR",
        "RUBELLA": "MMR",
        "VARICELLA": "Varicella",
        "POLIO": "Polio",
        "IPV": "Polio",
        "HIB": "Hib",
        "MENINGOCOCCAL": "Meningococcal",
        "MENING": "Meningococcal"
    }

    # Determine vaccine group from vaccine name (keyword matching)
    def assign_vaccine_group(vaccine_name: str) -> str:
        if not vaccine_name:
            return "Other"

        vaccine_upper = vaccine_name.upper()
        for keyword, group in vaccine_group_map.items():
            if keyword in vaccine_upper:
                return group
        return "Other"

    df_with_group = df_cvx.with_columns([
        pl.col("full_name").map_elements(
            assign_vaccine_group,
            return_dtype=pl.Utf8
        ).alias("vaccine_group")
    ])

    group_counts = df_with_group.group_by("vaccine_group").count()
    print(f"Vaccine groups assigned: {group_counts.shape[0]} distinct groups")

    return df_with_group


def determine_series_pattern(vaccine_name: str, cvx_code: str) -> str:
    """
    Determine typical series pattern for vaccine.

    Uses hardcoded rules based on common vaccine schedules.
    Future enhancement: Load from separate reference table or CDC schedules.

    Args:
        vaccine_name: Full vaccine name
        cvx_code: CVX code

    Returns:
        Series pattern string (e.g., "2-dose", "Annual", "Booster")
    """
    # Hardcoded series patterns for common vaccines
    series_map = {
        # COVID-19: 2-dose primary + boosters
        "208": "2-dose primary + boosters",
        "213": "2-dose primary + boosters",
        # Shingrix: 2-dose
        "187": "2-dose",
        # Influenza: Annual
        "088": "Annual", "135": "Annual", "140": "Annual", "141": "Annual",
        "144": "Annual", "158": "Annual", "161": "Annual",
        # Hepatitis B: 3-dose
        "008": "3-dose", "043": "3-dose", "045": "3-dose",
        # Hepatitis A: 2-dose
        "083": "2-dose", "052": "2-dose",
        # Tdap/Td: Booster
        "115": "Booster", "113": "Booster",
        # DTaP: 5-dose
        "020": "5-dose", "106": "5-dose", "107": "5-dose",
        # Polio: 4-dose
        "010": "4-dose",
        # HPV: 2-3 dose
        "062": "2-3 dose",
        # Varicella: 2-dose
        "021": "2-dose",
        # MMR: 2-dose
        "003": "2-dose",
        # Hib: 3-4 dose
        "048": "3-4 dose", "049": "2-3 dose",
        # Pneumococcal
        "033": "Single or 2-dose",
        "152": "4-dose"
    }

    return series_map.get(cvx_code, "Single dose")


def transform_to_reference_vaccine_schema(df_cvx: pl.DataFrame) -> pl.DataFrame:
    """
    Transform CDC CVX data to reference.vaccine schema.

    Args:
        df_cvx: DataFrame with parsed and enriched CVX data

    Returns:
        DataFrame matching reference.vaccine table schema
    """
    print("Transforming to reference.vaccine schema...")

    # Filter to Active vaccines only (include Inactive for historical data if desired)
    # For Phase 3 MVP: Include both Active and Inactive for historical immunization lookup
    df_filtered = df_cvx.filter(
        pl.col("status").str.to_lowercase().is_in(["active", "inactive"])
    )

    # Map to reference.vaccine columns
    df_final = df_filtered.with_columns([
        pl.col("cvx_code").cast(pl.Utf8).str.zfill(3),  # Zero-pad to 3 digits
        pl.col("full_name").alias("vaccine_name"),
        pl.col("short_name").alias("vaccine_short_name"),
        pl.col("vaccine_group"),
        # Apply series pattern determination
        pl.struct(["full_name", "cvx_code"]).map_elements(
            lambda x: determine_series_pattern(x["full_name"], x["cvx_code"]),
            return_dtype=pl.Utf8
        ).alias("typical_series_pattern"),
        (pl.col("status").str.to_lowercase() == "active").alias("is_active"),
        pl.lit(None).cast(pl.Utf8).alias("notes"),
        pl.current_timestamp().alias("last_updated")
    ]).select([
        "cvx_code",
        "vaccine_name",
        "vaccine_short_name",
        "vaccine_group",
        "typical_series_pattern",
        "is_active",
        "notes",
        "last_updated"
    ])

    print(f"Transformed {df_final.shape[0]} vaccines for PostgreSQL load")
    print(f"  Active: {df_final.filter(pl.col('is_active')).shape[0]}")
    print(f"  Inactive: {df_final.filter(~pl.col('is_active')).shape[0]}")

    return df_final


def load_to_postgres(df: pl.DataFrame, truncate: bool = True):
    """
    Load transformed data to PostgreSQL reference.vaccine table.

    Args:
        df: DataFrame with reference.vaccine schema
        truncate: If True, truncate table before load (default). If False, upsert.
    """
    print("=== Loading to PostgreSQL ===")

    # Convert Polars to Pandas for to_sql compatibility
    df_pandas = df.to_pandas()

    # Connect to PostgreSQL
    engine = create_engine(POSTGRES_CONNECTION_STRING)

    if truncate:
        # Truncate and reload (simple approach for Phase 3)
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE reference.vaccine CASCADE"))
            conn.commit()
            print("Truncated reference.vaccine table")

    # Load data
    df_pandas.to_sql(
        name="vaccine",
        con=engine,
        schema="reference",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=100
    )

    print(f"Loaded {len(df_pandas)} vaccines to reference.vaccine")

    # Verification queries
    with engine.connect() as conn:
        # Total count
        result = conn.execute(text("SELECT COUNT(*) FROM reference.vaccine"))
        total_count = result.scalar()
        print(f"Verification: {total_count} total vaccines in reference.vaccine")

        # Active count
        result = conn.execute(text("""
            SELECT COUNT(*) FROM reference.vaccine WHERE is_active = TRUE
        """))
        active_count = result.scalar()
        print(f"Verification: {active_count} active vaccines")

        # Inactive count
        result = conn.execute(text("""
            SELECT COUNT(*) FROM reference.vaccine WHERE is_active = FALSE
        """))
        inactive_count = result.scalar()
        print(f"Verification: {inactive_count} inactive vaccines (historical)")

        # Vaccine groups
        result = conn.execute(text("""
            SELECT vaccine_group, COUNT(*) as count
            FROM reference.vaccine
            WHERE is_active = TRUE
            GROUP BY vaccine_group
            ORDER BY count DESC
            LIMIT 10
        """))
        print("\nTop 10 vaccine groups (active):")
        for row in result:
            print(f"  {row[0]}: {row[1]} vaccines")


def main(download: bool = True, version_date: str = None):
    """
    Execute CDC CVX reference data pipeline.

    Args:
        download: If True, download from CDC and upload to MinIO. If False, use existing MinIO data.
        version_date: Optional version date (YYYY-MM-DD). Defaults to today.

    Usage:
        # Download and load (first-time or quarterly refresh)
        python -m etl.load_cdc_cvx_reference

        # Load from existing MinIO data (testing)
        python -m etl.load_cdc_cvx_reference --no-download
    """
    print("=== CDC CVX Reference Data Pipeline ===")

    # Step 1: Download CDC data to MinIO (if requested)
    if download:
        version_path = download_cdc_data_to_minio(version_date)
    else:
        version_path = "cdc-reference-data/cvx/LATEST"
        print(f"Using existing MinIO data: {version_path}")

    # Step 2: Read CVX data from MinIO
    cvx_text = read_file_from_minio("med-sandbox", f"{version_path}/cvx_codes.txt")

    # Step 3: Parse CVX file
    df_cvx = parse_cvx_file(cvx_text)

    # Step 4: Map vaccine groups
    df_with_groups = map_vaccine_groups(df_cvx)

    # Step 5: Transform to reference.vaccine schema
    df_final = transform_to_reference_vaccine_schema(df_with_groups)

    # Step 6: Load to PostgreSQL
    load_to_postgres(df_final, truncate=True)

    print("\n=== CDC CVX Reference Pipeline Complete ===")
    print(f"Successfully replaced 30 hardcoded vaccines with {df_final.shape[0]} CDC vaccines")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load CDC CVX reference data")
    parser.add_argument("--no-download", action="store_true", help="Skip CDC download, use existing MinIO data")
    parser.add_argument("--version", type=str, help="Version date (YYYY-MM-DD)")

    args = parser.parse_args()

    main(download=not args.no_download, version_date=args.version)
```

**Helper Functions (Add to `etl/s3_client.py`):**

```python
def read_file_from_minio(bucket: str, object_name: str) -> str:
    """Read text file from MinIO and return as string"""
    from minio import Minio
    from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY

    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    response = client.get_object(bucket, object_name)
    return response.read().decode('utf-8')


def upload_file_to_minio(bucket: str, object_name: str, data: str):
    """Upload text data to MinIO"""
    from minio import Minio
    from io import BytesIO
    from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY

    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Ensure bucket exists
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    # Upload data
    data_bytes = data.encode('utf-8')
    client.put_object(
        bucket,
        object_name,
        BytesIO(data_bytes),
        length=len(data_bytes)
    )
```

#### 10.4.5 Implementation Timeline

**Estimated Effort:** 2-3 days (Post-Phase 2, can be done independently)

**Day 1: Setup and Download (4-6 hours)**
- [ ] Download CDC CVX codes file from official source
- [ ] Download CDC vaccine groups mapping file
- [ ] Create MinIO bucket structure: `med-sandbox/cdc-reference-data/cvx/`
- [ ] Upload initial version with timestamp (e.g., `2026-01-14/`)
- [ ] Create LATEST symlink/copy
- [ ] Verify files are accessible from Python

**Day 2: ETL Pipeline Implementation (6-8 hours)**
- [ ] Create `etl/load_cdc_cvx_reference.py`
- [ ] Implement CDC file parsing (pipe-delimited format)
- [ ] Implement vaccine group mapping logic
- [ ] Implement series pattern determination
- [ ] Transform to `reference.vaccine` schema
- [ ] Add MinIO helper functions to `etl/s3_client.py`
- [ ] Unit test parsing and transformation logic

**Day 3: PostgreSQL Migration and Verification (4-6 hours)**
- [ ] Backup existing `reference.vaccine` table (30 records)
- [ ] Run full CDC ETL pipeline
- [ ] Verify PostgreSQL load: ~334+ records
- [ ] Verify CVX code distribution (active vs inactive)
- [ ] Verify vaccine group assignments
- [ ] Test UI: Ensure immunizations page still works with new data
- [ ] Test API: Query vaccines by group, check series patterns
- [ ] Test AI tools: Verify CVX code lookups work correctly
- [ ] Document migration process in `docs/spec/immunizations-design.md`

**Post-Implementation:**
- [ ] Schedule quarterly refresh job (cron or manual)
- [ ] Document CDC update monitoring process
- [ ] Create rollback procedure (revert to previous MinIO version)

#### 10.4.6 Migration Plan: 30 Vaccines → 334+ CDC Vaccines

**Pre-Migration Checklist:**
- [ ] Verify Days 1-12 implementation is complete and stable
- [ ] Backup PostgreSQL `reference.vaccine` table
- [ ] Test CDC data download and parsing in dev environment
- [ ] Verify MinIO bucket exists and is accessible

**Migration Steps:**

1. **Backup Current Data:**
   ```sql
   -- Create backup table
   CREATE TABLE reference.vaccine_backup_20260114 AS
   SELECT * FROM reference.vaccine;

   -- Verify backup
   SELECT COUNT(*) FROM reference.vaccine_backup_20260114;
   -- Expected: 30 rows
   ```

2. **Run CDC Pipeline:**
   ```bash
   python -m etl.load_cdc_cvx_reference
   ```

3. **Verify Migration:**
   ```sql
   -- Check new record count
   SELECT COUNT(*) FROM reference.vaccine;
   -- Expected: ~334+ rows

   -- Verify original 30 vaccines still exist
   SELECT cvx_code, vaccine_name, is_active
   FROM reference.vaccine
   WHERE cvx_code IN ('008', '010', '020', '021', '033', '043', '048', '052', '062', '083',
                      '088', '103', '106', '107', '110', '113', '115', '121', '135', '140',
                      '141', '144', '152', '158', '161', '187', '208', '213')
   ORDER BY cvx_code;
   -- Expected: 28-30 rows (all original vaccines should be present)

   -- Check vaccine group distribution
   SELECT vaccine_group, COUNT(*) as count
   FROM reference.vaccine
   WHERE is_active = TRUE
   GROUP BY vaccine_group
   ORDER BY count DESC;
   ```

4. **Test Application:**
   - Load immunizations page: `/patient/ICN100001/immunizations`
   - Verify vaccine family filter dropdown shows more options
   - Test CVX code lookups in AI tools
   - Verify widget still displays correctly

5. **Rollback Procedure (if needed):**
   ```sql
   -- Restore from backup
   TRUNCATE TABLE reference.vaccine;
   INSERT INTO reference.vaccine
   SELECT * FROM reference.vaccine_backup_20260114;

   -- Verify rollback
   SELECT COUNT(*) FROM reference.vaccine;
   -- Expected: 30 rows
   ```

#### 10.4.7 Quarterly Refresh Process

**Frequency:** Every 3 months (or as CDC publishes updates)

**CDC Update Monitoring:**
- Subscribe to CDC IIS listserv for vaccine code set release notes
- Check release notes: https://www.cdc.gov/iis/code-sets/downloads/vaccine-code-sets-release-notes-*.pdf
- Monitor CDC website for new vaccine approvals (COVID variants, new vaccines)

**Refresh Procedure:**

1. **Download New CDC Data:**
   ```bash
   # Use new version date
   python -m etl.load_cdc_cvx_reference --version 2026-04-15
   ```

2. **Review Changes:**
   ```sql
   -- Compare new vs old record counts
   SELECT
       (SELECT COUNT(*) FROM reference.vaccine) as new_count,
       (SELECT COUNT(*) FROM reference.vaccine_backup_previous) as old_count,
       (SELECT COUNT(*) FROM reference.vaccine) -
       (SELECT COUNT(*) FROM reference.vaccine_backup_previous) as delta;

   -- Identify new CVX codes
   SELECT cvx_code, vaccine_name, vaccine_group
   FROM reference.vaccine
   WHERE cvx_code NOT IN (SELECT cvx_code FROM reference.vaccine_backup_previous)
   ORDER BY cvx_code;
   ```

3. **Update Documentation:**
   - Document new vaccines added
   - Update `docs/spec/immunizations-design.md` with new CVX count
   - Notify clinical users of new vaccine codes

**Automated Refresh (Future Enhancement):**
- Create cron job or scheduled task to run quarterly
- Implement CDC change detection (compare file hashes)
- Send email notification when new vaccines are available
- Automated testing after refresh

---

## 11. Testing Strategy

### 11.1 Unit Tests

**ETL Tests:**
- [ ] Test `parse_series_info()` with various formats: "1 of 2", "BOOSTER", "COMPLETE", null
- [ ] Test `standardize_site()` with VistA abbreviations: "L DELTOID", "R ARM"
- [ ] Test deduplication logic: Same patient + CVX + datetime within 1 hour
- [ ] Test CVX code mapping from Cerner to standard CVX

**API Tests:**
- [ ] Test `get_all_immunizations()` with filters (days, vaccine_family, series_status)
- [ ] Test `get_recent_immunizations()` returns correct limit
- [ ] Test `get_vaccine_series_status()` calculates series completion correctly
- [ ] Test empty state (patient with 0 immunizations)

**AI Tool Tests:**
- [ ] Test `get_immunization_history()` returns CVX codes and dates
- [ ] Test `check_vaccine_compliance()` identifies missing Shingrix for age 65+
- [ ] Test `forecast_next_dose()` calculates correct due date for Shingrix (2-month interval)

### 11.2 Integration Tests

**ETL Pipeline:**
- [ ] Run full pipeline: Bronze → Silver → Gold → Load
- [ ] Verify row counts at each stage (no data loss)
- [ ] Verify patient ICN mappings are correct
- [ ] Verify series completion flags match dose_number == total_doses

**API + Database:**
- [ ] Test full page renders with filters applied
- [ ] Test widget loads within 500ms
- [ ] Test expandable row details load correctly
- [ ] Test filter combinations (date range + vaccine family + series status)

**AI Integration:**
- [ ] Test end-to-end query via `/insight`: "What vaccines has ICN100001 received?"
- [ ] Verify AI response includes CVX codes and clinical context
- [ ] Test compliance check returns missing vaccines for age 65+
- [ ] Test forecast returns due date for incomplete Shingrix series

### 11.3 Test Data Scenarios

**Test Patients (8 total):**

| ICN | Age | Immunizations | Test Scenarios |
|-----|-----|---------------|----------------|
| ICN100001 | 67 | 25 vaccines | Complete adult history, recent flu, complete Shingrix |
| ICN100002 | 42 | 18 vaccines | Incomplete Shingrix (1 of 2), adverse reaction to flu |
| ICN100003 | 8 | 22 vaccines | Childhood series (DTaP, IPV, MMR), some incomplete |
| ICN100004 | 55 | 15 vaccines | No Shingrix, no recent flu (gap analysis test) |
| ICN100005 | 28 | 12 vaccines | COVID-19 primary + booster, Tdap, recent flu |
| ICN100009 | 72 | 20 vaccines | Multiple flu vaccines (annual pattern), pneumococcal |
| ICN100010 | 35 | 16 vaccines | Hepatitis B series (3-dose), HPV series incomplete |
| ICN100013 | 61 | 19 vaccines | Shingrix eligible (age 50+), COVID-19 boosters |

### 11.4 Performance Benchmarks

**API Response Times:**
- [ ] `GET /api/patient/{icn}/immunizations` < 500ms (100 records)
- [ ] `GET /api/patient/{icn}/immunizations/recent` < 200ms (8 records)
- [ ] Widget HTML render < 300ms
- [ ] Full page render < 1000ms (with filters)

**Database Query Optimization:**
- [ ] Patient lookup index used: `idx_immunizations_patient_date`
- [ ] CVX code index used: `idx_immunizations_cvx`
- [ ] Incomplete series query uses filtered index: `idx_immunizations_incomplete`

---

## 12. Security and Privacy

### 12.1 Data Security

**Development Environment:**
- ✅ All mock data is synthetic, non-PHI/PII
- ✅ CVX codes and vaccine names are public CDC data
- ✅ No real patient identifiers in mock database

**Production Requirements (Future):**
- [ ] HIPAA compliance for immunization records (PHI)
- [ ] Audit logging for all immunization queries
- [ ] Row-level security for cross-site access (Sta3n filtering)
- [ ] Encryption at rest for PostgreSQL serving database
- [ ] Encryption in transit (HTTPS, TLS for database connections)

### 12.2 Authorization

**Current State:**
- All authenticated users can view all patient immunizations
- No role-based access control (RBAC)

**Future Enhancements:**
- [ ] Role-based access: Clinicians, Nurses, Pharmacists, Read-Only
- [ ] Site-based access: Users limited to home site (Sta3n) by default
- [ ] Cross-site access requires justification and audit trail
- [ ] Break-the-glass emergency access for critical care situations

### 12.3 Vaccine Safety Reporting

**Out of Scope for Phase 1:**
- VAERS (Vaccine Adverse Event Reporting System) integration
- Automated adverse reaction reporting to CDC
- Vaccine lot recall notifications

**Rationale:** Read-only viewer. Adverse reaction reporting is separate clinical workflow.

---

## 13. Appendices

### Appendix A: CVX Code Reference

**Complete list of 30 CVX codes used in reference.vaccine table:**

See Section 5.3.2 for full CVX code list with vaccine names and series patterns.

**Source:** CDC Vaccine Codes (CVX) - https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp

### Appendix B: Test Patient Data Summary

**8 Test Patients (ICN100001-100005, ICN100009-100010, ICN100013):**

**Patient Demographics:**
- ICN100001 (Adam Dooree): Age 67, Male - **25 immunizations** (complete adult history)
- ICN100002 (Barry Miifaa): Age 42, Male - **18 immunizations** (incomplete Shingrix, flu adverse reaction)
- ICN100003 (New): Age 8, Female - **22 immunizations** (childhood series, some incomplete)
- ICN100004 (New): Age 55, Female - **15 immunizations** (no Shingrix, gap test)
- ICN100005 (New): Age 28, Male - **12 immunizations** (COVID-19 boosters, recent flu)
- ICN100009 (New): Age 72, Male - **20 immunizations** (annual flu pattern, pneumococcal)
- ICN100010 (Alexander Aminor): Age 35, Male - **16 immunizations** (Hep B series, HPV incomplete)
- ICN100013 (Irving Thompson): Age 61, Male - **19 immunizations** (Shingrix eligible, COVID boosters)

**Total:** ~147 immunization records

**Distribution:**
- VistA (CDWWork): ~100 records
- Cerner (CDWWork2): ~47 records (4 patients overlap for deduplication testing)

### Appendix C: VistA File Mappings

**VistA File #9000010.11 (V IMMUNIZATION):**
- Primary immunization administration file
- Captures vaccine given, date, site, reactions
- Links to File #9999999.14 for vaccine definitions

**VistA File #9999999.14 (IMMUNIZATION):**
- Vaccine product definitions
- CVX codes for standardization
- Manufacturer codes (MVX)

**See Section 4.2 for detailed field mappings.**

### Appendix D: Related Documentation

- `docs/spec/immunizations-design-research.md` - AI strategy and CDW research
- `docs/spec/med-z1-architecture.md` - API routing patterns (Section 3)
- `docs/spec/allergies-design.md` - Bridge table pattern reference
- `docs/spec/medications-design.md` - Two-source harmonization pattern
- `docs/spec/vitals-design.md` - Chronological table UI pattern
- `docs/spec/ai-insight-design.md` - AI tool integration patterns
- CDC CVX codes: https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp
- CDC ACIP schedules: https://www.cdc.gov/vaccines/schedules/

### Appendix E: Glossary

- **CVX Code:** CDC Concept of Vaccines eXpanded - numeric code identifying vaccine products
- **MVX Code:** Manufacturer code for vaccine producers
- **ACIP:** Advisory Committee on Immunization Practices (CDC)
- **VistA:** Veterans Health Information Systems and Technology Architecture
- **Cerner/Oracle Health:** Commercial EHR system (successor to VistA at some VA sites)
- **ICN:** Integrated Care Number (patient identifier)
- **Sta3n:** Station number (VA facility identifier)
- **VAERS:** Vaccine Adverse Event Reporting System
- **Series:** Multi-dose vaccine sequence (e.g., "1 of 2", "2 of 3 COMPLETE")
- **Booster:** Additional dose given after primary series for extended immunity

---

**End of Immunizations Design Specification**

**Document Status:** Version 1.3 - Data Pipeline & UI Complete (Days 1-8), AI Integration Pending (Days 9-12)

**Version History:**
- **v1.0** (2026-01-10): Initial design specification
- **v1.1** (2026-01-12): ETL pipeline design finalized (Bronze/Silver/Gold)
- **v1.2** (2026-01-14): Data pipeline & UI implementation complete (Phases 1-2)
- **v1.3** (2026-01-15): Section 9 (AI Integration) consolidated into `ai-insight-design.md` per "single source of truth" architectural principle. Section 9 now contains concise pointer to `ai-insight-design.md` Sections 4.6, 6.6, and 10 Phase 6 for complete AI integration specifications.

**Next Steps:** Phase 3 - AI Integration (5-7 days) - See `docs/spec/ai-insight-design.md` for implementation roadmap
