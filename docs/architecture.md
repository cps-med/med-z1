# med-z1 Architecture Documentation

**Document Version:** 1.0
**Date:** 2025-12-12
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
│                        med-z1 System                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐     ┌──────────────┐   │
│  │  Web UI      │      │  CCOW Vault  │     │  AI/ML       │   │
│  │  (FastAPI)   │◄────►│  (FastAPI)   │     │  Services    │   │
│  │  Port 8000   │      │  Port 8001   │     │              │   │
│  └──────┬───────┘      └──────────────┘     └──────────────┘   │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │           PostgreSQL Serving Database                 │      │
│  │  (patient_demographics, patient_allergies, etc.)     │      │
│  └──────────────────────────────────────────────────────┘      │
│         ▲                                                        │
│         │ ETL Pipeline                                          │
│         │                                                        │
│  ┌──────┴───────────────────────────────────────────────┐      │
│  │              MinIO Object Storage (S3)                │      │
│  │         Bronze → Silver → Gold (Parquet)             │      │
│  └──────────────────────────────────────────────────────┘      │
│         ▲                                                        │
│         │ ETL Extraction                                        │
│         │                                                        │
│  ┌──────┴───────────────────────────────────────────────┐      │
│  │        Mock CDW (SQL Server 2019)                     │      │
│  │  CDWWork (VistA) + CDWWork1 (Oracle Health)          │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

**Web UI (app/):**
- FastAPI application serving HTML via Jinja2 templates
- HTMX for dynamic updates without full page reloads
- Routes organized by function: patient, dashboard, vitals, etc.
- Direct queries to PostgreSQL serving database

**CCOW Vault (ccow/):**
- Separate FastAPI service for patient context management
- Thread-safe in-memory context storage
- REST API for get/set/clear active patient
- Enables context synchronization across applications

**ETL Pipeline (etl/):**
- Bronze: Raw extraction from mock CDW to Parquet
- Silver: Cleaned, harmonized, joined data
- Gold: Curated, query-optimized views with ICN/patient_key
- PostgreSQL Load: Final serving database tables

**Mock CDW (mock/sql-server/):**
- Development-only SQL Server 2019 database
- Synthetic, non-PHI/PII data only
- Two databases: CDWWork (VistA-like), CDWWork1 (Oracle Health-like)

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

@router.get("/{icn}/allergies")              # JSON API
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
| Labs          | TBD               | B (rec) | TBD        | TBD     | **ETL Complete** - UI implementation pending |
| Problems      | TBD               | A or B  | TBD        | TBD     | Planned - Pattern depends on complexity      |
| Orders        | TBD               | B (rec) | TBD        | TBD     | Planned - Complex workflow domain            |
| Notes         | TBD               | B (rec) | TBD        | TBD     | Planned - Text-heavy domain                  |
| Imaging       | TBD               | B (rec) | TBD        | TBD     | Planned - May need external viewer           |
| Immunizations | TBD               | A or B  | TBD        | TBD     | Later Phase - Pattern TBD                    |
| Procedures    | TBD               | A or B  | TBD        | TBD     | Later Phase - Pattern TBD                    |

**Important Note on Patient Flags (Design Decision 2025-12-14):**
- Patient Flags uses a **modal-only UI pattern** accessed via topbar "View Flags" button with badge count
- **No dashboard widget** (previously implemented, now removed)
- **No dedicated full page** (deemed unnecessary - modal provides sufficient functionality)
- This is an intentional deviation from the standard widget + page pattern
- Rationale: Flags are critical safety alerts best displayed on-demand via persistent topbar access

### 3.4 Decision Matrix: When to Create a Dedicated Router

**Create dedicated router file (`app/routes/<domain>.py`) when:**
- ✅ Domain has a full page view with URL like `/patient/{icn}/<domain>`
- ✅ Domain requires complex page-level filtering, sorting, or charting
- ✅ Domain has multiple page routes (list view, detail view, etc.)
- ✅ Separation improves maintainability (>300 lines of route code)

**Keep routes in `patient.py` when:**
- ✅ Domain only needs JSON API endpoints
- ✅ Domain uses modal overlays instead of full pages
- ✅ Domain is in early implementation (API-first approach)
- ✅ Domain is tightly coupled to patient context

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

### 4.1 Medallion Architecture (Bronze → Silver → Gold)

**Bronze Layer:**
- Raw data extracted from source systems (CDWWork, CDWWork1)
- Minimal transformations (column name cleanup only)
- Stored as Parquet in MinIO: `med-z1/bronze/<source>/<domain>/`
- One-to-one with source tables

**Silver Layer:**
- Cleaned, validated, standardized data
- Joins across dimensions (e.g., allergen names, reactions)
- Cross-source harmonization (VistA + Oracle Health)
- Stored as Parquet in MinIO: `med-z1/silver/<domain>/`
- Derived fields (e.g., `is_drug_allergy`, flags)

**Gold Layer:**
- Business-ready, curated views
- Joined with patient demographics for ICN/patient_key
- Sorted and optimized for UI consumption
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
- ✅ **DO** update source INSERT scripts in `mock/sql-server/cdwwork/insert/`
- ✅ **DO** ensure database can be rebuilt from scratch
- ✅ **DO** rerun full ETL pipeline after source data changes
- ❌ **DO NOT** use temporary UPDATE/patch scripts (violates rebuild-from-scratch principle)
- ❌ **DO NOT** leave obsolete scripts in repository

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

**Current State (Development):**
- ❌ No authentication (local development only)
- ❌ No authorization (all data accessible)
- ✅ CCOW context management (patient selection only)

**Future State (Production):**
- ✅ SSO integration (VA PIV/CAC)
- ✅ Role-based access control (RBAC)
- ✅ Audit logging (all data access)
- ✅ PHI/PII protections per VA policy

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

---

## Appendices

### A. Related Documentation

- `docs/med-z1-plan.md` - Product and technical development plan
- `docs/patient-dashboard-design.md` - Dashboard and widget system design
- `docs/vitals-design.md` - Vitals implementation specification
- `docs/patient-flags-design.md` - Patient Flags implementation specification
- `docs/allergies-design.md` - Allergies implementation specification
- `docs/demographics-design.md` - Demographics implementation specification
- `docs/encounters-design.md` - Encounters (Inpatient) implementation specification
- `app/README.md` - FastAPI application developer guide
- `CLAUDE.md` - Project guidance for Claude Code assistant

### B. Glossary

- **ICN:** Integrated Care Number (patient identifier)
- **SID:** Surrogate ID (internal database key)
- **CDW:** Corporate Data Warehouse (VA data warehouse)
- **CCOW:** Clinical Context Object Workgroup (context management standard)
- **Medallion Architecture:** Bronze/Silver/Gold data pipeline pattern
- **HTMX:** HTML over-the-wire library for dynamic UI updates

---

**End of Document**

**Document Status:** Version 1.0 - Initial Architecture Documentation
**Next Review:** After each major feature implementation
**Maintainers:** Development team
