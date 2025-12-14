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
| Encounters    | TBD               | B (rec) | TBD        | TBD     | Planned - High priority (foundation domain)  |
| Labs          | TBD               | B (rec) | TBD        | TBD     | Planned - 3x1 widget recommended for panels  |
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

---

## Appendices

### A. Related Documentation

- `docs/med-z1-plan.md` - Product and technical development plan
- `docs/patient-dashboard-design.md` - Dashboard and widget system design
- `docs/vitals-design.md` - Vitals implementation specification
- `docs/patient-flags-design.md` - Patient Flags implementation specification
- `docs/allergies-design.md` - Allergies implementation specification
- `docs/demographics-design.md` - Demographics implementation specification
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
