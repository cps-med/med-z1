# med-z1 Architecture Documentation

**Document Version:** 1.1
**Date:** 2025-12-30
**Last Updated:** 2025-12-30 (Added ADR-008: Vista Session Caching for AI Integration)
**Status:** Living Document

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [API Routing Architecture](#api-routing-architecture)
4. [Data Architecture](#data-architecture)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Architecture Decision Records](#architecture-decision-records)

---

## 1. Overview

This document captures architectural decisions, patterns, and rationale for the med-z1 longitudinal health record viewer. It serves as the authoritative reference for understanding system design choices and guiding future development.

**Key Principles:**
- Python-first: All components use Python 3.11+
- Medallion data architecture: Bronze/Silver/Gold data layers
- Server-side rendering: FastAPI + HTMX + Jinja2 (minimal JavaScript)
- Consistency over flexibility: Strong, opinionated patterns

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        med-z1 System                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐      ┌───────────────┐                      │
│   │   CCOW Vault  │      │ VistA Service │                      │
│   │   (FastAPI)   │◄────►│   (FastAPI)   │                      │
│   │   Port 8001   │      │   Port 8003   │                      │
│   └───────────────┘      └─────┬─────────┘                      │
│             ▲ Active           │ T-0                            │
│             │ Patient          │                                │
│             ▼ Context          ▼                                │
│   ┌──────────────────────────────────┐      ┌───────────────┐   │
│   │              Web UI              │      │     AI/ML     │   │
│   │             (FastAPI)            │◄────►│     Tools     │   │
│   │             Port 8000            │      │  (LangGraph)  │   │
│   └──────────────────────────────────┘      └───────────────┘   │
│             ▲                                                   │
│             │ T-1 and prior                                     │
│   ┌─────────┴───────────────────────────────────────────────┐   │
│   │              PostgreSQL Serving Database                │   │
│   │    (demographics, allergies, labs, vitals, etc.)        │   │
│   └─────────────────────────────────────────────────────────┘   │
│             ▲                                                   │
│             │ ETL Pipeline                                      │
│   ┌─────────┴───────────────────────────────────────────────┐   │
│   │               MinIO Object Storage (S3)                 │   │
│   │           Bronze → Silver → Gold (Parquet)              │   │
│   └─────────────────────────────────────────────────────────┘   │
│             ▲                                                   │
│             │ ETL Pipeline                                      │
│   ┌─────────┴───────────────────────────────────────────────┐   │
│   │               Mock CDW (SQL Server 2019)                │   │
│   │       CDWWork (VistA) + CDWWork2 (Oracle Health)        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

**Web UI (app/):**
- FastAPI application serving HTML via Jinja2 templates
- HTMX for dynamic updates without full page reloads
- Routes organized by function: patient, dashboard, vitals, etc.
- Queries PostgreSQL serving database for historical data (T-1 and earlier)
- Integrates with VistA Service for real-time data (T-0, today)
- Communicates with CCOW Vault for patient context management
- Invokes AI/ML Tools for clinical insights and decision support

**CCOW Vault (ccow/):**
- Separate FastAPI service for patient context management (Port 8001)
- Thread-safe in-memory context storage
- REST API for get/set/clear active patient
- Enables context synchronization across applications
- Bidirectional communication with Web UI for active patient tracking

**VistA Service (vista/):**
- Separate FastAPI service simulating VA VistA RPC Broker (Port 8003)
- Provides real-time clinical data (T-0, today) complementing historical PostgreSQL data
- Multi-site simulation (3 sites: Alexandria 200, Anchorage 500, Palo Alto 630)
- Automatic ICN → DFN resolution per site
- Session-based caching (30-minute TTL) for performance
- Simulated network latency (1-3 seconds per site) for realistic testing
- Supports "Refresh VistA" UI pattern for on-demand real-time data retrieval
- **Implemented RPCs (6):** ORWPT PTINQ (demographics), GMV LATEST VM (vitals), ORWCV ADMISSIONS (encounters), ORQQAL LIST (allergies), ORWPS COVER (medications), ORQQPL LIST (problems)

**AI/ML Tools (ai/):**
- LangGraph-powered clinical decision support agents
- Integrates with Web UI via FastAPI endpoints
- Accesses both PostgreSQL data (T-1+) and cached VistA data (T-0) for comprehensive analysis
- **Implemented Tools (4):**
  - `check_ddi_risks` - Drug-drug interaction analysis
  - `get_patient_summary` - Comprehensive patient overview (demographics, meds, vitals, allergies, encounters, notes, problems with Charlson Index)
  - `analyze_vitals_trends` - Statistical vitals analysis with clinical interpretation
  - `get_clinical_notes_summary` - Query clinical notes with filtering
- OpenAI GPT-4 Turbo backend with centralized prompt management
- Session-aware: Uses Vista session cache when available (see ADR-008)

**PostgreSQL Serving Database:**
- Fast, indexed queries for historical clinical data (T-1 and earlier)
- Organized into schemas: `auth` (authentication), `clinical` (patient data)
- Clinical tables: demographics, vitals, allergies, medications, flags, encounters, labs, clinical notes, immunizations, problems
- Loaded from Gold layer Parquet files via ETL pipeline
- Supports complex filtering, sorting, and pagination
- Used by Web UI and AI/ML Tools for data retrieval

**MinIO Object Storage (S3):**
- Medallion architecture: Bronze → Silver → Gold layers
- Stores Parquet files for each transformation stage
- Bronze: Raw extracts from Mock CDW, minimal transformation
- Silver: Cleaned, harmonized, joined data across sources (CDWWork + CDWWork2)
- Gold: Curated, query-optimized views ready for PostgreSQL load
- Enables reproducible ETL pipeline with audit trail

**ETL Pipeline (etl/):**
- Bronze: Raw extraction from mock CDW to Parquet
- Silver: Cleaned, harmonized, joined data
- Gold: Curated, query-optimized views with ICN/patient_key
- PostgreSQL Load: Final serving database tables
- Full pipeline execution: `python -m etl.bronze_<domain> && python -m etl.silver_<domain> && python -m etl.gold_<domain> && python -m etl.load_<domain>`

**Mock CDW (mock/sql-server/):**
- Development-only SQL Server 2019 database
- Synthetic, non-PHI/PII data only
- Two databases: CDWWork (VistA-like), CDWWork2 (Oracle Health-like)
- Comprehensive schemas: Dim, SPatient, Vital, Allergy, RxOut, BCMA, Inpat, Chem, TIU, Immun (138 immunizations)
- Simulates VA Corporate Data Warehouse structure and content
- Data source for Bronze ETL extraction

---

## 3. API Routing Architecture

### 3.1 Overview

The med-z1 FastAPI application uses a **modular router architecture** with patterns that vary by domain based on implementation stage and UI requirements.

**Core Pattern:**
- All JSON API endpoints live under `/api/patient/{icn}/<domain>`
- Database query functions live in `app/db/<domain>.py`
- Route handlers live in `app/routes/` (either `patient.py` or dedicated router file)

### 3.2 Router Organization Patterns

We use **two accepted patterns** depending on domain complexity and UI requirements:

#### Pattern A: Routes in patient.py (Flags, Allergies)
**Use when:**
- Domain has simple API-only requirements
- Domain uses modal overlays instead of full pages
- Domain is in early implementation stages

**Structure:**
```
app/
  db/
    patient_allergies.py       # Database queries
  routes/
    patient.py                  # Contains allergy API endpoints
```

**Endpoints:**
```python
# In app/routes/patient.py
router = APIRouter(prefix="/api/patient", tags=["patient"])

@router.get("/{icn}/allergies")               # JSON API
@router.get("/{icn}/allergies/critical")      # JSON API
@router.get("/{icn}/allergies/{id}/details")  # JSON API
```

**Examples:** Patient Flags, Allergies (Day 5 complete)

---

#### Pattern B: Dedicated Router File (Vitals)
**Use when:**
- Domain has full page views (not just modals)
- Domain requires complex filtering/sorting UI
- Domain has widget + full page + API endpoints

**Structure:**
```
app/
  db/
    vitals.py                   # Database queries
  routes/
    vitals.py                   # API and page routes
```

**Endpoints:**
```python
# In app/routes/vitals.py

# API router for JSON endpoints
router = APIRouter(prefix="/api/patient", tags=["vitals"])

@router.get("/{icn}/vitals")                     # JSON API
@router.get("/{icn}/vitals/recent")              # JSON API
@router.get("/dashboard/widget/vitals/{icn}")    # Widget HTML

# Page router for full page views
page_router = APIRouter(tags=["vitals-pages"])

@page_router.get("/vitals")                      # Redirect
@page_router.get("/patient/{icn}/vitals")        # Full page HTML
```

**Examples:** Vitals (complete with full page view)

---

### 3.3 Domain-Specific Routing Decisions

| Domain        | Router Location    | Pattern | Full Page? | Widget? | Rationale                                    |
|---------------|-------------------|---------|------------|---------|----------------------------------------------|
| Demographics  | `demographics.py` | B       | Yes        | Yes     | Full page with comprehensive patient information |
| Flags         | `patient.py`      | A       | **No**     | **No**  | **Modal-only** via topbar button (see note below) |
| Allergies     | `allergies.py`    | B       | Yes        | Yes     | Full implementation with dedicated page      |
| Vitals        | `vitals.py`       | B       | Yes        | Yes     | Complex filtering/charting needs full page   |
| Medications   | `medications.py`  | B       | Yes        | Yes     | Full implementation with 2x1 widget          |
| Encounters    | `encounters.py`   | B       | Yes        | Yes     | **Complete** - First domain with pagination  |
| Notes         | `notes.py`        | B       | Yes        | Yes     | **Complete (2026-01-02)** - Text-heavy domain with filtering |
| Immunizations | `immunizations.py`| B       | Yes        | Yes     | **Complete (2026-01-14)** - Multi-source harmonization |
| Problems      | `problems.py`     | B       | Yes        | Yes     | **Complete (2026-02-08)** - Charlson Index, ICD-10 grouping |
| Labs          | TBD               | B (rec) | TBD        | TBD     | **ETL Complete** - UI implementation pending |
| Orders        | TBD               | B (rec) | TBD        | TBD     | Planned - Complex workflow domain            |
| Imaging       | TBD               | B (rec) | TBD        | TBD     | Planned - May need external viewer           |
| Procedures    | TBD               | A or B  | TBD        | TBD     | Later Phase - Pattern TBD                    |

**Important Note on Patient Flags (Design Decision 2025-12-14):**
- Patient Flags uses a **modal-only UI pattern** accessed via topbar "View Flags" button with badge count
- **No dashboard widget** (previously implemented, now removed)
- **No dedicated full page** (deemed unnecessary - modal provides sufficient functionality)
- This is an intentional deviation from the standard widget + page pattern
- Rationale: Flags are critical safety alerts best displayed on-demand via persistent topbar access

### 3.4 Decision Matrix: When to Create a Dedicated Router

**Create dedicated router file (`app/routes/<domain>.py`) when:**
- Domain has a full page view with URL like `/patient/{icn}/<domain>`
- Domain requires complex page-level filtering, sorting, or charting
- Domain has multiple page routes (list view, detail view, etc.)
- Separation improves maintainability (>300 lines of route code)

**Keep routes in `patient.py` when:**
- Domain only needs JSON API endpoints
- Domain uses modal overlays instead of full pages
- Domain is in early implementation (API-first approach)
- Domain is tightly coupled to patient context

### 3.5 Endpoint URL Conventions

**JSON API Endpoints:**
```
GET  /api/patient/{icn}/<domain>                    # List all
GET  /api/patient/{icn}/<domain>/<item_id>          # Get one
GET  /api/patient/{icn}/<domain>/<item_id>/details  # Get details
GET  /api/patient/{icn}/<domain>/critical           # Get subset
POST /api/patient/{icn}/<domain>                    # Create (future)
PUT  /api/patient/{icn}/<domain>/<item_id>          # Update (future)
```

**Widget HTML Endpoints:**
```
GET /api/dashboard/widget/<domain>/{icn}            # Widget partial
```

**Full Page Endpoints:**
```
GET /<domain>                                        # Redirect to current patient
GET /patient/{icn}/<domain>                          # Full page view
```

### 3.6 Architecture Decision: Why This Pattern?

**Decision Date:** 2025-12-12
**Decision Maker(s):** Development team
**Status:** Accepted

**Context:**
- Vitals was implemented first with dedicated router (Pattern B)
- Flags and Allergies implemented later in patient.py (Pattern A)
- User questioned inconsistency during Day 5 allergies implementation

**Decision:**
Keep both patterns as valid architectural choices based on domain requirements.

**Rationale:**
1. **Pattern A is simpler** for API-only domains (reduces file count)
2. **Pattern B provides better separation** for complex domains with full pages
3. **Both patterns are consistent where it matters:** All JSON APIs under `/api/patient/{icn}/`
4. **Refactoring cost > benefit** - Vitals works well, no need to move it
5. **Future flexibility** - Domains can migrate from A→B as they mature

**Consequences:**
- ✅ Developers have clear decision criteria for new domains
- ✅ No breaking changes to existing working code
- ⚠️ Need to document pattern choice in design specs
- ⚠️ Code review should verify correct pattern selection

**Alternatives Considered:**
1. **All routes in patient.py** - Rejected: Would make patient.py too large (>1000 lines)
2. **All domains get dedicated routers** - Rejected: Over-engineering for simple domains
3. **Refactor vitals into patient.py** - Rejected: Unnecessary churn, vitals works well

---

## 4. Data Architecture

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

### 4.1 Medallion Architecture (Bronze → Silver → Gold)

**Bronze Layer:**
- Raw data extracted from source systems (CDWWork, CDWWork2)
- Minimal transformations (column name cleanup only)
- Stored as Parquet in MinIO: `med-z1/bronze/<source>/<domain>/`
- One-to-one with source tables

**Bronze Layer Naming Convention:**
- **Dimension tables:** `{domain}_dim` (suffix pattern)
  - Examples: `vaccine_dim`, `vital_type_dim`, `lab_test_dim`, `local_drug_dim`
- **Fact tables:** `{domain_name}` (no suffix)
  - Examples: `immunization`, `vital_sign`, `lab_chem`, `tiu_clinical_notes`
- **Parquet files:** `{table_name}_raw.parquet`
  - Examples: `vaccine_dim_raw.parquet`, `patient_immunization_raw.parquet`
- **Rationale:** Suffix pattern clearly distinguishes dimension vs fact tables; `_raw` suffix indicates unprocessed Bronze layer data

**Silver Layer:**
- Cleaned, validated, standardized data
- Joins across dimensions (e.g., allergen names, reactions)
- Cross-source harmonization (VistA + Oracle Health)
- Stored as Parquet in MinIO: `med-z1/silver/<domain>/`
- Derived fields (e.g., `is_drug_allergy`, flags)

**Silver Layer Naming Convention:**
- **Dimension tables:** `{domain}_dim` (same suffix pattern as Bronze)
  - Examples: `lab_test_dim`, `tiu_document_definition_dim`, `vaccine_dim`
- **Fact tables:** `{domain_name}` with descriptive suffix indicating processing
  - Examples: `vitals_merged`, `patient_allergies_cleaned`, `lab_chem`, `immunization_harmonized`
- **Parquet files:** `{table_name}.parquet` (no `_raw` suffix since data is cleaned)
  - Examples: `lab_test_dim.parquet`, `vitals_merged.parquet`, `immunization_harmonized.parquet`
- **Rationale:** Maintains `_dim` suffix for easy identification of reference data; descriptive suffixes on fact tables indicate processing stage; removal of `_raw` signals cleaned state

**Gold Layer:**
- Business-ready, curated views
- Joined with patient demographics for ICN/patient_key
- Sorted and optimized for UI consumption

**Gold Layer Naming Convention:**
- **View-based naming:** `{business_view_name}` (no technical suffixes)
  - Examples: `patient_demographics`, `clinical_notes`, `labs`, `patient_vitals`, `patient_immunizations`
- **Parquet files:** `{view_name}_final.parquet` (indicates ready for serving database)
  - Examples: `patient_demographics_final.parquet`, `clinical_notes_final.parquet`, `labs_final.parquet`
- **Rationale:** Business-friendly names reflect UI/query perspective; `_final` suffix indicates production-ready data optimized for PostgreSQL load
- Stored as Parquet in MinIO: `med-z1/gold/<domain>/`
- Ready for PostgreSQL loading

**Serving Database (PostgreSQL):**
- Loaded from Gold Parquet files
- Patient-centric views for low-latency queries
- Used directly by FastAPI app for UI rendering

### 4.2 Patient Identity Resolution

**Primary Identifier:** ICN (Integrated Care Number)
- Mapped as `patient_key` in Gold and PostgreSQL
- Joined from `patient_sid` in Silver layer via Gold patient demographics
- Used in all API routes: `/api/patient/{icn}/<domain>`

**Internal Keys (SIDs):**
- `PatientSID`, `InpatientSID`, `RxOutpatSID`, etc.
- Used for joins within Bronze/Silver layers only
- **Not exposed in UI or API responses**

### 4.3 Location Field Patterns

**IMPORTANT:** Clinical domains that use `Dim.Location` reference data must follow a consistent three-column pattern for location fields.

#### 4.3.1 Standard Location Field Structure

All domains that reference location data must store three pieces of information:
1. **Location ID** - Foreign key to `Dim.Location` (e.g., `LocationSID`)
2. **Location Name** - Denormalized location name for display (e.g., "Medicine Ward 5A")
3. **Location Type** - Denormalized location type for context (e.g., "Inpatient", "Laboratory")

**Why Three Columns?**
- **Performance:** Avoids JOIN with `Dim.Location` for every query
- **Simplicity:** Templates can directly reference `location_name` without lookups
- **Resilience:** Query layer remains functional even if dimension table changes
- **Consistency:** Uniform pattern across all clinical domains

#### 4.3.2 Domain-Specific Implementations

**Vitals Domain:**
```sql
-- PostgreSQL Schema (db/ddl/create_patient_vitals_table.sql)
CREATE TABLE patient_vitals (
    vital_id                    SERIAL PRIMARY KEY,
    patient_key                 VARCHAR(50) NOT NULL,
    -- ... other columns ...
    location_id                 INTEGER,              -- LocationSID
    location_name               VARCHAR(100),         -- "MEDICINE WARD 5A"
    location_type               VARCHAR(50),          -- "Inpatient"
    -- ... other columns ...
);

-- Query Layer (app/db/vitals.py)
SELECT
    vital_id, patient_key, vital_type,
    location_id, location_name, location_type,  -- All three columns
    -- ... other columns ...
FROM patient_vitals
WHERE patient_key = :icn;

-- Template Usage (app/templates/patient_vitals.html)
{% if vital.location_name %}
    <div class="vital-meta">Location: {{ vital.location_name }}</div>
{% endif %}
```

**Laboratory Results Domain:**
```sql
-- PostgreSQL Schema (db/ddl/create_patient_labs_table.sql)
CREATE TABLE patient_labs (
    lab_id                      SERIAL PRIMARY KEY,
    patient_key                 VARCHAR(50) NOT NULL,
    -- ... other columns ...
    location_id                 INTEGER,              -- LocationSID
    collection_location         VARCHAR(100),         -- "Laboratory - Main Lab"
    collection_location_type    VARCHAR(50),          -- "Laboratory"
    -- ... other columns ...
);

-- Gold Transformation (etl/gold_labs.py)
df_gold = df_silver.join(
    df_location,
    left_on="location_sid",
    right_on="location_sid",
    how="left"
).select([
    pl.col("location_sid").alias("location_id"),
    pl.col("location_name").alias("collection_location"),
    pl.col("location_type").alias("collection_location_type"),
    # ... other columns ...
])
```

**Encounters Domain:**
```sql
-- PostgreSQL Schema (db/ddl/create_patient_encounters_table.sql)
-- Note: Encounters has TWO locations (admit + discharge)
CREATE TABLE patient_encounters (
    encounter_id                SERIAL PRIMARY KEY,
    patient_key                 VARCHAR(50) NOT NULL,
    -- Admit location
    admit_location_id           INTEGER,
    admit_location_name         VARCHAR(100),
    admit_location_type         VARCHAR(50),
    -- Discharge location
    discharge_location_id       INTEGER,
    discharge_location_name     VARCHAR(100),
    discharge_location_type     VARCHAR(50),
    -- ... other columns ...
);

-- Query Layer (app/db/encounters.py)
SELECT
    encounter_id, patient_key,
    admit_location_id, admit_location_name, admit_location_type,
    discharge_location_id, discharge_location_name, discharge_location_type,
    -- ... other columns ...
FROM patient_encounters
WHERE patient_key = :icn;
```

#### 4.3.3 Common Mistakes and Fixes

**❌ Mistake 1: Using Single `location` Column**
```sql
-- WRONG - old pattern, causes query/schema mismatches
SELECT location FROM patient_vitals;  -- Column doesn't exist
```

**✅ Fix: Always SELECT All Three Columns**
```sql
-- CORRECT
SELECT location_id, location_name, location_type FROM patient_vitals;
```

**❌ Mistake 2: Selecting Only ID Column**
```sql
-- WRONG - defeats purpose of denormalization
SELECT location_id FROM patient_vitals;  -- Need name for display
```

**✅ Fix: SELECT All Three Even If Not Immediately Needed**
```sql
-- CORRECT - future-proof for template changes
SELECT location_id, location_name, location_type FROM patient_vitals;
```

**❌ Mistake 3: Updating Schema Without Updating Queries**
```sql
-- Schema changed from single 'location' to three columns
-- But queries still reference old column name
SELECT location FROM patient_vitals;  -- Error: column doesn't exist
```

**✅ Fix: Update Schema, Queries, Templates Together**
1. Update DDL script: Add three columns, remove old column
2. Update query layer: SELECT all three columns, update row parsing indices
3. Update templates: Reference `location_name` instead of `location`
4. Rerun ETL pipeline: Regenerate data with new structure
5. Test all views: Widget, full page, API endpoints

#### 4.3.4 Root-Level Fix Philosophy

**When fixing location field issues:**
- **DO** update source INSERT scripts in `mock/sql-server/cdwwork/insert/`
- **DO** ensure database can be rebuilt from scratch
- **DO** rerun full ETL pipeline after source data changes
- **DO NOT** use temporary UPDATE/patch scripts (violates rebuild-from-scratch principle)
- **DO NOT** leave obsolete scripts in repository

**Example: Labs Domain Location Fix (2025-12-16)**
```bash
# Step 1: Update source INSERT script with LocationSID values
# File: mock/sql-server/cdwwork/insert/Chem.LabChem.sql
INSERT INTO [Chem].[LabChem]
([PatientSID], [LabTestSID], ..., [LocationSID], [Sta3n], ...)
VALUES (1001, 1, ..., 33, 508, ...);  -- LocationSID added

# Step 2: Rebuild mock database from scratch
docker exec -i sqlserver bash -c "/opt/mssql-tools18/bin/sqlcmd ..."

# Step 3: Rerun ETL pipeline (Bronze → Silver → Gold → Load)
python -m etl.bronze_labs
python -m etl.silver_labs
python -m etl.gold_labs
python -m etl.load_labs

# Result: 58 lab results with proper location fields in PostgreSQL
```

#### 4.3.5 Implementation Checklist

When implementing location fields for a new domain:

- [ ] **Schema (DDL):** Define three columns: `*_id`, `*_name`, `*_type`
- [ ] **Source Data:** Ensure INSERT scripts populate LocationSID
- [ ] **Bronze ETL:** Extract LocationSID from source
- [ ] **Silver ETL:** Join with `Dim.Location` to get name/type
- [ ] **Gold ETL:** Include all three columns in final output
- [ ] **PostgreSQL Load:** Map to schema columns correctly
- [ ] **Query Layer:** SELECT all three columns in all queries
- [ ] **Row Parsing:** Update dictionary indices after adding columns
- [ ] **Templates:** Reference `*_name` for display, not old single column
- [ ] **Testing:** Verify widget, full page, and API endpoints render location

**See Also:** ADR-006 (Location Field Patterns)

---

## 5. Authentication and Authorization

### 5.1 Current Implementation (Development/Testing)

**Authentication Status:** **IMPLEMENTED (2025-12-18)**

med-z1 now includes a complete session-based authentication system designed for development and testing environments. While production deployment will require VA SSO integration, the current implementation provides robust authentication for development, testing, and demonstration purposes.

#### 5.1.1 Database Schema (`auth` Schema)

**Tables:**
- `auth.users` - User credentials and profile information
  - UUID primary key, email (unique username), bcrypt password hash
  - Profile fields: display_name, first_name, last_name, home_site_sta3n
  - Account status: is_active, is_locked, failed_login_attempts
  - Audit fields: created_at, updated_at, last_login_at
- `auth.sessions` - Active user sessions with timeout enforcement
  - UUID session_id (used in session cookie)
  - Foreign key to users table (CASCADE delete)
  - Session lifecycle: created_at, last_activity_at, expires_at
  - Session metadata: ip_address, user_agent
  - Configurable timeout (default: 15 minutes inactivity)
- `auth.audit_logs` - Comprehensive audit trail
  - All authentication events logged (login, logout, failures, timeouts)
  - Event context: user_id, email, IP address, user agent
  - Success/failure tracking with failure reasons
  - Indexed by user, event type, and timestamp

**See:** `db/ddl/create_auth_tables.sql`

#### 5.1.2 Middleware Layer

**AuthMiddleware** (`app/middleware/auth.py` - 168 lines):
- Intercepts all HTTP requests before route handlers
- Public routes bypass authentication: `/login`, `/static`, `/docs`, etc.
- Protected routes require valid session:
  1. Extracts `session_id` from cookie
  2. Validates session in database (active, not expired)
  3. Extends session timeout on activity (sliding window)
  4. Injects user context into `request.state.user`
- Invalid/expired sessions → redirect to `/login` with cookie cleared
- Session extension: Updates `last_activity_at` + `expires_at` on every request

**Middleware Ordering** (CRITICAL):
```python
# In app/main.py
app.add_middleware(SessionMiddleware, ...)  # Vista cache (added first)
app.add_middleware(AuthMiddleware)          # Authentication (added second)

# Execution order (reverse of add order):
# Request:  AuthMiddleware → SessionMiddleware → Route
# Response: Route → SessionMiddleware → AuthMiddleware
```

**See:** `app/middleware/auth.py`

#### 5.1.3 Routes and Endpoints

**Authentication Routes** (`app/routes/auth.py` - 326 lines):
- `GET /login` - Login page (public)
- `POST /login` - Process login credentials
  - Validates email and password (bcrypt hash verification)
  - Creates new session in database
  - Invalidates all previous sessions for user (security best practice)
  - Sets `session_id` cookie (HttpOnly, SameSite=lax)
  - Comprehensive audit logging (success/failure, IP, user agent)
- `POST /logout` - Terminate session
  - Invalidates session in database
  - Clears both cookies: `session_id` (auth) and `session` (Vista cache)
  - Logs logout event to audit trail
- `GET /logout` - Redirect to login (handles bookmarked /logout URLs)

**Database Layer** (`app/db/auth.py` - 503 lines):
- User management: `create_user()`, `get_user_by_email()`, `verify_password()`
- Session management: `create_session()`, `get_session()`, `extend_session()`, `invalidate_session()`
- Audit logging: `log_audit_event()` for all authentication events
- Password security: bcrypt hashing with 12 rounds (configurable)

**See:** `app/routes/auth.py`, `app/db/auth.py`

#### 5.1.4 Session Management

**Session Cookie Configuration:**
```python
# config.py
SESSION_COOKIE_NAME = "session_id"          # Auth session cookie
SESSION_TIMEOUT_MINUTES = 15                # Inactivity timeout
SESSION_COOKIE_HTTPONLY = True              # JavaScript cannot access
SESSION_COOKIE_SECURE = False               # True in production (HTTPS only)
SESSION_COOKIE_SAMESITE = "lax"             # CSRF protection
```

**Dual Cookie Architecture:**
1. **`session_id` cookie** (AuthMiddleware) - Stores session UUID for authentication
   - References `auth.sessions` table in PostgreSQL
   - Contains only session ID, no user data
   - Cleared on logout
2. **`session` cookie** (SessionMiddleware) - Stores Vista cache data
   - Signed cookie containing session data (itsdangerous)
   - Stores Vista RPC responses for AI integration
   - Cleared on logout
   - See ADR-008 for Vista Session Caching details

**Session Lifecycle:**
1. **Login:** User credentials validated → new session created in DB → `session_id` cookie set
2. **Activity:** Every request extends `last_activity_at` and `expires_at` (sliding window)
3. **Timeout:** Session expires after 15 minutes of inactivity → redirect to login
4. **Logout:** Session invalidated in DB → both cookies cleared

#### 5.1.5 Security Features

**Password Security:**
- Bcrypt hashing with 12 rounds (configurable via `BCRYPT_ROUNDS`)
- Passwords never stored in plaintext
- Password strength requirements (future enhancement)

**Session Security:**
- Session ID stored server-side (PostgreSQL), not in cookie payload
- HttpOnly cookies (JavaScript cannot access)
- SameSite=lax (CSRF protection)
- Secure flag in production (HTTPS only)
- Session timeout with sliding window
- All previous sessions invalidated on new login

**Audit Trail:**
- All login attempts logged (success/failure)
- Failed login reasons tracked (user not found, invalid password, account locked)
- Logout events logged
- Session timeouts logged
- IP address and user agent captured
- Audit logs indexed for security review and compliance

**Account Lockout:**
- Failed login attempt counter
- Account locking capability (`is_locked` flag)
- Automatic lockout after N failures (future enhancement)

#### 5.1.6 Test Users

**Development Users** (created via `scripts/create_test_users.py`):

- `clinician.alpha@va.gov` - Primary test user
- `clinician.bravo@va.gov` - Secondary test user
- All test users have a common password (development only)

### 5.2 Authorization (Future State)

**Current State:** **NOT IMPLEMENTED**

- All authenticated users have full access to all patient data
- No role-based access control (RBAC)
- No row-level security (RLS)
- No data sensitivity classifications

**Future Enhancements (Production):**  

- Role-based access control (RBAC)
  - Roles: Clinician, Nurse, Pharmacist, Administrator, Read-Only
  - Permission system for data domains (vitals, meds, notes, etc.)
- Row-level security for sensitive data
  - Patient flags with narrative text (restricted to need-to-know)
  - Mental health data (restricted access)
  - Substance abuse treatment records (42 CFR Part 2)
- Break-the-glass emergency access
  - Override restrictions with audit trail and justification
- Site-based access controls
  - Users limited to home site data by default
  - Cross-site access with justification

### 5.3 Production Requirements (Future)

**SSO Integration:**
- VA PIV/CAC card authentication
- SAML/OAuth integration with VA identity provider
- Multi-factor authentication (MFA)

**Compliance:**
- HIPAA compliance (PHI protection)
- VA Directive 6500 (IT security)
- FISMA controls
- Audit log retention (minimum 7 years)

**See Also:**
- ADR-008: Vista Session Caching for AI Integration (dual cookie architecture)
- `config.py`: Authentication configuration variables
- `app/middleware/auth.py`: Authentication middleware implementation

---

## 6. Architecture Decision Records

### ADR-001: API Routing Patterns (2025-12-12)
**Status:** Accepted
**Context:** Need consistent but flexible routing as domains mature
**Decision:** Support both Pattern A (patient.py) and Pattern B (dedicated router)
**Consequences:** Clear criteria documented; both patterns valid
**See:** Section 3.2-3.6 above

### ADR-002: Medallion Data Architecture (2025-12-10)
**Status:** Accepted
**Context:** Need scalable, auditable ETL pipeline
**Decision:** Use Bronze/Silver/Gold medallion pattern with Parquet + MinIO
**Consequences:** Clear separation of concerns; easy to replay transformations
**See:** Section 4.1 above

### ADR-003: Server-Side Rendering with HTMX (2025-12-08)
**Status:** Accepted
**Context:** Need fast, accessible UI without heavy JavaScript framework
**Decision:** FastAPI + Jinja2 + HTMX for server-side rendering
**Consequences:** Simple development model; excellent 508 compliance; fast page loads

### ADR-004: PostgreSQL as Serving Database (2025-12-08)
**Status:** Accepted
**Context:** Need low-latency queries for UI; Gold Parquet not query-optimized
**Decision:** Load Gold Parquet into PostgreSQL for serving database
**Consequences:** Fast queries; SQL-friendly for developers; easy indexing

### ADR-005: Pagination Pattern for Full Page Views (2025-12-15)
**Status:** Accepted (Implemented in Encounters domain - 2025-12-15)
**Context:** Some clinical domains (Encounters, Labs, Notes) can have 50+ records per patient, making single-page display impractical. Need consistent pagination pattern across all full page views.

**Decision:** Implement simple Prev/Next pagination pattern with page size selector:
- **Default page size:** 20 items per page
- **Page size options:** 10, 20, 50, 100 items per page (dropdown selector)
- **Navigation:** Previous and Next buttons (no numbered page buttons)
- **Page indicator:** "Page X of Y (Z total items)" for context
- **Technology:** Standard HTML links (no HTMX) for simplicity and URL shareability
- **Conditional display:** Disabled Prev when on page 1; disabled Next when on last page
- **URL parameters:** `?page=N&page_size=N&filter_*=true` for state preservation

**Implementation Pattern:**
```html
<!-- Pagination Controls -->
<div class="pagination">
  {% if page > 1 %}
    <a href="#"
       hx-get="/patient/{{ patient_icn }}/encounters?page={{ page - 1 }}"
       hx-target="#encounters-table">
      &lt;&lt; Prev
    </a>
  {% endif %}
  <span>Page {{ page }} of {{ total_pages }}</span>
  {% if page < total_pages %}
    <a href="#"
       hx-get="/patient/{{ patient_icn }}/encounters?page={{ page + 1 }}"
       hx-target="#encounters-table">
      Next &gt;&gt;
    </a>
  {% endif %}
</div>
```

**Backend Implementation:**
```python
# Database query with pagination
def get_all_encounters(
    icn: str,
    page: int = 1,
    per_page: int = 20
) -> List[Dict[str, Any]]:
    offset = (page - 1) * per_page
    query = text(f"""
        SELECT ...
        FROM patient_encounters
        WHERE patient_icn = :icn
        ORDER BY admit_datetime DESC
        LIMIT :per_page OFFSET :offset
    """)
    # Calculate total_pages = ceil(total_count / per_page)
```

**Alternatives Considered:**
1. **Numbered page links (1, 2, 3, ...):** Rejected - adds complexity; overwhelming for 10+ pages
2. **Infinite scroll:** Rejected - not ideal for medical data; users need discrete page boundaries
3. **Load all data client-side:** Rejected - poor performance for 100+ records; increases page load time
4. **"Load More" button:** Rejected - users lose ability to navigate back to specific pages

**Consequences:**
- ✅ **Positive:**
  - Consistent UX across all domains (Encounters, Labs, Notes, Orders)
  - Simple to implement and maintain
  - Accessible (keyboard navigation, screen reader friendly)
  - Performant and scalable (works for any data size)
  - Shareable URLs (includes page state in query parameters)
  - Page size selector allows user preference
- ⚠️ **Trade-offs:**
  - No direct jump to specific page (acceptable for most use cases; can add later if needed)
  - Requires backend support for OFFSET/LIMIT queries
- 🔮 **Future Enhancements:**
  - Jump to page input box (useful for 10+ pages)
  - "Showing X-Y of Z total" alternative display
  - First/Last page buttons for very long lists

**Implementation Results:** Successfully implemented in Encounters domain with 30+ records per patient. Page size selector (10/20/50/100) works well for varying data sizes. Filter state properly preserved across page navigation.
**See:** `docs/encounters-design.md` Section 8.2

### ADR-006: Location Field Patterns (2025-12-16)
**Status:** Accepted
**Context:** Clinical domains (Vitals, Labs, Encounters) reference `Dim.Location` for location data. Initial implementations used inconsistent patterns (single `location` column vs. three-column structure), causing query/schema mismatches and UI rendering failures.

**Problem:** After Encounters domain was enhanced with location fields, Vitals UI broke because queries still referenced old single `location` column while schema had been changed to three columns (`location_id`, `location_name`, `location_type`). This caused SQL errors and empty widget displays.

**Decision:** Standardize on **three-column location pattern** for all domains:
1. **`*_id`** - Foreign key to `Dim.Location` (e.g., `location_id`, `admit_location_id`)
2. **`*_name`** - Denormalized location name for display (e.g., `location_name`, `collection_location`)
3. **`*_type`** - Denormalized location type for context (e.g., `location_type`, `collection_location_type`)

**Rationale:**
1. **Performance:** Avoids JOIN with `Dim.Location` on every query (denormalized name/type)
2. **Simplicity:** Templates can directly reference `location_name` without lookups
3. **Consistency:** Uniform pattern across all clinical domains reduces cognitive load
4. **Resilience:** Query layer remains functional even if dimension table structure changes

**Implementation Requirements:**
- All domains MUST SELECT all three columns in queries (even if not immediately displayed)
- Schema changes MUST be accompanied by query layer and template updates
- Source data fixes MUST be applied at root level (INSERT scripts, not UPDATE patches)
- Full ETL pipeline MUST be rerun after source data changes

**Consequences:**
- ✅ **Positive:**
  - Prevents future query/schema mismatches
  - Consistent pattern simplifies onboarding new developers
  - Clear checklist for implementing location fields in new domains
  - Templates future-proof (can add location display without query changes)
- ⚠️ **Trade-offs:**
  - Slight data duplication (denormalized name/type)
  - Requires discipline to update schema, queries, templates together
- ⚠️ **Migration Required:**
  - Existing domains (Vitals, Encounters) updated to follow pattern
  - Labs domain implemented with pattern from day one

**Alternatives Considered:**
1. **Single `location` VARCHAR column** - Rejected: Lost referential integrity, no type information
2. **ID-only with JOINs** - Rejected: Poor performance, added query complexity
3. **Domain-specific patterns** - Rejected: Inconsistency causes maintenance burden

**See:** Section 4.3 (Location Field Patterns) for detailed implementation guidance

### ADR-007: PostgreSQL Schema Organization (2025-12-24)
**Status:** Accepted
**Context:** Clinical domain tables (patient_demographics, patient_vitals, patient_allergies, etc.) were initially created in the PostgreSQL default `public` schema, while authentication tables used a dedicated `auth` schema. This implicit decision led to inconsistent schema organization and maintenance challenges as the project grew.

**Problem:**
1. **Organizational Clarity:** All clinical tables mixed with system tables in `public` schema
2. **Security/Permissions:** Difficult to apply schema-level access controls
3. **Namespace Management:** Potential for naming conflicts as project scales
4. **Inconsistency:** Auth tables in dedicated `auth` schema, but clinical tables in `public`
5. **Documentation:** Setup guide incorrectly assumed `clinical` schema existed

**Decision:** Organize all clinical domain tables under a dedicated `clinical` schema:
- **Schema structure:**
  - `auth.*` - Authentication and session management tables (already implemented)
  - `clinical.*` - All clinical domain tables (patient demographics, vitals, allergies, medications, flags, encounters, labs, etc.)
  - `public` - Reserved for system/utility tables if needed

**Implementation:**
1. **DDL Scripts:** Add `CREATE SCHEMA IF NOT EXISTS clinical;` and prefix all clinical tables with `clinical.`
2. **ETL Load Scripts:** Add `schema="clinical"` parameter to pandas `.to_sql()` calls
3. **Application Queries:** Update all SQL queries to reference `clinical.table_name`
4. **Documentation:** Fix verification commands in setup guides

**Rationale:**
1. **Logical Separation:** Clear boundaries between auth, clinical data, and future schemas (analytics, audit, etc.)
2. **Security:** Easier to apply schema-level permissions (e.g., read-only access for reporting users)
3. **Maintainability:** Table listings (`\dt`) become more organized and understandable
4. **Scalability:** Prevents naming conflicts as new domains are added
5. **Consistency:** Mirrors the pattern established with `auth` schema

**Consequences:**
- ✅ **Positive:**
  - Clean separation of concerns by functional area
  - Easier to reason about database structure
  - Simplified permission management for production
  - Consistent pattern for future schema additions (e.g., `analytics`, `audit`)
  - Better developer experience (`\dt clinical.*` shows only clinical tables)
- ⚠️ **Migration Required:**
  - All DDL scripts updated with `CREATE SCHEMA IF NOT EXISTS clinical;`
  - All ETL load scripts updated to specify `schema="clinical"`
  - All application database queries updated to reference `clinical.*`
  - Documentation (linux-setup-guide.md) corrected with proper schema references
- ⚠️ **Trade-offs:**
  - Slightly longer table references (`clinical.patient_demographics` vs `patient_demographics`)
  - Requires schema prefix in all queries (can use `SET search_path` to mitigate)

**Alternatives Considered:**
1. **Continue using public schema** - Rejected: Poor organization, difficult to manage at scale
2. **Schema per domain (vitals, labs, meds)** - Rejected: Over-fragmentation; too many schemas to manage
3. **Single med-z1 schema for everything** - Rejected: Loses separation between auth and clinical concerns

**Implementation Timeline:** 2025-12-24 - Complete refactoring of all DDL, ETL, and application code

**See:**
- Section 4.2 (Data Architecture - PostgreSQL Serving Database)
- `db/ddl/` - All DDL scripts now create tables in `clinical` schema
- `etl/load_*.py` - All load scripts use `schema="clinical"` parameter

### ADR-008: Vista Session Caching for AI Integration (2025-12-30)
**Status:** Accepted
**Context:** AI Clinical Insights tools need access to real-time Vista data (T-0, today) in addition to historical PostgreSQL data (T-1 and earlier). Initial approach of storing full merged datasets in session cookies failed due to browser cookie size limit (4096 bytes).

**Problem:**
1. **Browser Cookie Limit:** Merged datasets (305 PG + 10 Vista = 315 vitals records) exceed 4096-byte limit
   - Error: "Set-Cookie header is ignored... size must be <= 4096 characters"
   - Original session size: ~40KB (10x over limit)
2. **AI Tool Data Access:** LangChain tools need request context to access session data
3. **Session Persistence:** Cache must survive page navigation and be cleared on logout
4. **User Experience:** Should be transparent - no separate "refresh for AI" action required

**Decision:** Implement session-based caching of Vista RPC responses with on-demand merging
- **Cache Storage:** Store only raw Vista RPC response strings in session cookie (~1-2KB)
- **Merge Strategy:** Fetch PostgreSQL data + merge with cached Vista responses when needed (page loads, AI tools)
- **Session Management:** Use Starlette SessionMiddleware with `path="/"` parameter
- **TTL:** 30-minute cache expiration (configurable)
- **Cleanup:** Clear both `session_id` (auth) and `session` (Vista cache) cookies on logout

**Implementation:**

**Service Layer** (`app/services/vista_cache.py` - 367 lines):
```python
class VistaSessionCache:
    @staticmethod
    def set_cached_data(request, patient_icn, domain, vista_responses, sites, stats):
        # Store raw RPC responses (NOT merged data)
        request.session["vista_cache"][patient_icn][domain] = {
            "vista_responses": vista_responses,  # Dict[site_id, response_string]
            "timestamp": datetime.now().isoformat(),
            "sites": sites,
            "stats": stats
        }

    @staticmethod
    def get_cached_data(request, patient_icn, domain):
        # Returns cached Vista responses if not expired (30 min TTL)
        # Returns None if missing or expired
```

**Middleware Configuration** (`app/main.py`):
```python
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    max_age=SESSION_COOKIE_MAX_AGE,
    https_only=False,  # True in production
    same_site="lax",
    path="/"  # CRITICAL: Ensures cookie sent with all requests
)
```

**Integration Points:**
1. **Vitals Page:** `/patient/{icn}/vitals/realtime` caches Vista responses after "Refresh from VistA"
2. **Page Loads:** `/patient/{icn}/vitals` merges PG + cached Vista on initial load
3. **AI Tools:** `VitalsTrendAnalyzer` merges PG + cached Vista for analysis
4. **Logout:** `POST /logout` clears both session cookies

**Rationale:**
1. **Cookie Size:** Reduced from ~40KB to ~1.5KB (under 4096 limit)
2. **Performance:** On-demand merge takes ~1-3 seconds (acceptable for AI analysis)
3. **Simplicity:** No Redis/database session storage needed
4. **Transparency:** Users see green "Vista Cached" badge, AI automatically uses cache
5. **Consistency:** Follows existing med-z1 pattern of minimal state management

**Consequences:**
- ✅ **Positive:**
  - AI tools automatically use real-time Vista data when available
  - No separate "Refresh Vista for AI" button needed
  - Session cookie persists across navigation (path="/")
  - Automatic cleanup on logout
  - Scalable: No server-side session storage
- ⚠️ **Trade-offs:**
  - Merge happens on-demand (small latency: ~1-3 seconds)
  - Cache limited by session TTL (30 minutes)
  - Multiple domains (vitals, meds, etc.) share session space
- ⚠️ **Security Considerations:**
  - Session cookie signed with `SESSION_SECRET_KEY` (HMAC)
  - HTTPS-only in production (`https_only=True`)
  - SameSite=lax (CSRF protection)

**Alternatives Considered:**
1. **Server-side session storage (Redis)** - Rejected: Adds infrastructure complexity; overkill for MVP
2. **Store merged data in session** - Rejected: Exceeds cookie size limit
3. **Separate Vista fetch for AI** - Rejected: Poor UX; duplicates RPC calls
4. **LocalStorage (client-side)** - Rejected: Not accessible from server-side AI tools

**Implementation Timeline:** 2025-12-30 - Phase 3 Week 3 (AI Clinical Insights)

**See:**
- `docs/ai-insight-design.md` - Section 2.5 (Vista Session Caching Architecture)
- `app/services/vista_cache.py` - Cache management service
- `ai/services/vitals_trend_analyzer.py` - AI tool integration

---

## Appendices

### A. Related Documentation

- `docs/spec/med-z1-plan.md` - Product and technical development plan
- `docs/spec/ai-insight-design.md` - AI Clinical Insights implementation specification (Phase 1 MVP Complete)
- `docs/spec/patient-dashboard-design.md` - Dashboard and widget system design
- `docs/spec/vitals-design.md` - Vitals implementation specification
- `docs/spec/patient-flags-design.md` - Patient Flags implementation specification
- `docs/spec/allergies-design.md` - Allergies implementation specification
- `docs/spec/demographics-design.md` - Demographics implementation specification
- `docs/spec/encounters-design.md` - Encounters (Inpatient) implementation specification
- `app/README.md` - FastAPI application developer guide
- `CLAUDE.md` - Project guidance for Claude Code assistant

### B. Glossary

- **CCOW:** Clinical Context Object Workgroup (context management standard)
- **CDW:** Corporate Data Warehouse (VA data warehouse)
- **DFN:** Divisional File Number (VistA patient identifier, site-specific)
- **HTMX:** HTML over-the-wire library for dynamic UI updates
- **ICN:** Integrated Care Number (patient identifier)
- **IEN:** Internal Entry Number (VistA record identifier within a specific file/table at a specific site)
- **Medallion Architecture:** Bronze/Silver/Gold data pipeline pattern
- **PHI/PII:** Protected Health Information / Personally Identifiable Information
- **RPC:** Remote Procedure Call (VistA inter-system communication protocol)
- **SID:** Surrogate ID (internal database key)
- **Sta3n:** Station Number (VA facility identifier)

---

**End of Document**

**Document Status:** Version 1.0 - Initial Architecture Documentation
**Next Review:** After each major feature implementation
**Maintainers:** Development team
