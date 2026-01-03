# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**med-z1** is a next-generation longitudinal health record viewer for the Department of Veterans Affairs, designed to replace the current Joint Longitudinal Viewer (JLV). It provides fast, consistent access to patient data sourced from the VA Corporate Data Warehouse (CDW) and introduces AI-assisted capabilities to help clinicians understand patient stories, key risks, and gaps in care.

**Key Design Principles:**
- Python-based (Python 3.11) for all components: ETL, backend APIs, AI/ML, and web UI
- Medallion data architecture (Bronze/Silver/Gold) using Parquet files in MinIO
- FastAPI + HTMX + Jinja2 for the web UI (minimal JavaScript)
- Mock CDW environment using Microsoft SQL Server 2019 with synthetic data only
- Single shared Python environment (`.venv/`), single `.env` file, single `config.py` module at project root

## Project Structure

```
med-z1/
  app/           # FastAPI + HTMX + Jinja2 web application
  ccow/          # CCOW Context Management Vault service
  vista/         # VistA RPC Broker Simulator (real-time data, T-0)
  etl/           # ETL scripts (Bronze/Silver/Gold transformations)
  mock/          # Mock data subsystem (simulates CDW, SDP, etc.)
    sql-server/  # Microsoft SQL Server schemas and data
      cdwwork/   # VistA-like mock data
      cdwwork2/  # Cerner/Oracle Health-like mock data
    shared/      # Shared patient registry (ICN/DFN mappings)
  ai/            # AI/ML and agentic components
  db/            # Serving DB DDL, migrations (create when needed)
  docs/          # Architecture, design docs
  lake/          # MinIO/Parquet access configs (create when needed)
  scripts/       # All testing, debugging, and utility scripts (both ad-hoc and formal tests)
```

## Common Development Commands

### Running the FastAPI Applications

From project root:
```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Run the main med-z1 web application (port 8000)
uvicorn app.main:app --reload

# Run the CCOW Context Vault service (port 8001, separate terminal)
uvicorn ccow.main:app --reload --port 8001

# Run the Vista RPC Broker Simulator (port 8003, separate terminal)
uvicorn vista.app.main:app --reload --port 8003

# Access in browser
# Main app: http://127.0.0.1:8000/
# CCOW service: http://127.0.0.1:8001/
# CCOW API docs: http://127.0.0.1:8001/docs
# Vista service: http://127.0.0.1:8003/
# Vista API docs: http://127.0.0.1:8003/docs
```

Stop servers with CTRL+C.

### Python Environment Setup

```bash
# Create virtual environment (Python 3.11)
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

- Copy `.env` template and configure with local values for database connections, MinIO endpoints, etc.
- Sensitive information (passwords, secrets) should be obtained from peer developers or secure storage
- Configuration is centralized in `config.py` at project root

## Architecture Highlights

### Architecture Decision Records and Design Patterns

**IMPORTANT:** Before implementing new features or making design decisions, consult `docs/architecture.md` for established patterns and architectural guidance.

**Key Architecture Documents:**
- **`docs/architecture.md`** - Central repository for architectural decisions, patterns, and rationale
  - API routing patterns (when to use patient.py vs dedicated routers)
  - Data architecture (Medallion pattern, identity resolution)
  - Technology choices (FastAPI, HTMX, PostgreSQL)
  - Architecture Decision Records (ADRs) documenting major decisions

**When to Consult architecture.md:**
- ✅ Before adding API endpoints for a new clinical domain
- ✅ When deciding between routing patterns (Pattern A vs Pattern B)
- ✅ Before making changes that affect system-wide patterns
- ✅ When questioning why something was implemented a certain way
- ✅ Before proposing alternative architectural approaches

**When to Update architecture.md:**
- ✅ After making a significant architectural decision
- ✅ When establishing a new pattern that should be followed consistently
- ✅ When rejecting an alternative approach (document why)
- ✅ When resolving architectural inconsistencies or ambiguities

**Development Workflow:**
1. Check if architecture.md addresses your design question
2. If pattern exists, follow it for consistency
3. If pattern doesn't exist or doesn't fit, propose new pattern
4. Document new architectural decisions in architecture.md as ADRs
5. Update relevant subsystem READMEs (e.g., `app/README.md`) with practical guidance

**Example: Adding a New Clinical Domain**
```
Question: "Should I create app/routes/medications.py or add to app/routes/patient.py?"

1. Consult: docs/architecture.md Section 3 (API Routing Architecture)
2. Decision Matrix: Does domain need full page view with complex filtering?
   - Yes → Pattern B: Create dedicated router (like Vitals)
   - No → Pattern A: Add to patient.py (like Flags, Allergies)
3. Follow established pattern for consistency
4. If neither pattern fits, document new pattern as ADR in architecture.md
```

**Consistency Over Flexibility:**
med-z1 follows **strong, opinionated patterns** to ensure maintainability as the codebase grows. When in doubt, favor consistency with existing patterns over novel approaches, even if the novel approach seems slightly better in isolation. This reduces cognitive load for developers and makes the codebase more predictable.

### Data Architecture

**Source Systems (Development):**
- Mock CDW running in Docker (SQL Server 2019)
  - `CDWWork` database: VistA-like data (maps to real CDWWORK)
  - `CDWWork2` database: Cerner/Oracle Health-like data (maps to real CDWWORK2)
- Both populated with synthetic, non-PHI/PII data only

**Medallion Pipeline:**
- **Bronze Layer:** Raw data from mock CDW, minimal transformation, stored as Parquet in MinIO
- **Silver Layer:** Cleaned and harmonized data across CDWWork and CDWWork2, unified patient identity (ICN/PatientKey)
- **Gold Layer:** Curated, query-friendly views optimized for UI consumption

**Serving Database:**
- PostgreSQL (preferred) or SQL Server
- Contains patient-centric and domain-centric views built from Gold Parquet
- Supports low-latency per-patient queries for the UI

### Mock CDW Schema Patterns

**Key Conventions:**
- Each core table has a `*SID` column (e.g., `PatientSID`, `InpatientSID`, `RxOutpatSID`) serving as surrogate primary key
- `Sta3n` indicates facility/station
- Foreign key constraints are lightweight or omitted in mock environment for simplicity
- CDWWork2 intentionally uses different naming conventions to exercise Silver-layer harmonization

**Major Schemas in CDWWork:**
- `Dim` (dimensions: Sta3n, State, PatientRecordFlag, TIUDocumentDefinition, etc.)
- `SPatient` (patient demographics, addresses, insurance, PatientRecordFlagAssignment, PatientRecordFlagHistory)
- `SStaff` (staff/providers)
- `Inpat` (inpatient encounters)
- `RxOut` (outpatient medications)
- `BCMA` (medication administration)
- `Vital` (vital signs)
- `Allergy` (patient allergies and reactions)
- `Chem` (laboratory results)
- `TIU` (clinical notes - Text Integration Utilities)
- Future: Orders, Imaging, Immunizations, Problems, Procedures

**Patient Flags Tables (added 2025-12-10):**
- `Dim.PatientRecordFlag` - Flag definitions (National Cat I, Local Cat II)
- `SPatient.PatientRecordFlagAssignment` - Patient → Flag assignments with review tracking
- `SPatient.PatientRecordFlagHistory` - Audit trail with sensitive narrative text

**Clinical Notes Tables (added 2026-01-02):**
- `Dim.TIUDocumentDefinition` - Note type definitions (Progress Notes, Consults, Discharge Summaries, Imaging Reports)
- `TIU.TIUDocument_8925` - Clinical note metadata (VistA File #8925)
- `TIU.TIUDocumentText` - Full clinical note narrative text (SOAP format)

### Web Application Architecture

**Technology Stack:**
- **Framework:** FastAPI (Python 3.11)
- **Templating:** Jinja2
- **Interactive UX:** HTMX (server-side rendering with dynamic updates)
- **Static Assets:** CSS, minimal JavaScript
- **Configuration:** Centralized in root-level `config.py`, using python-dotenv

**Layout Philosophy:**
- Dashboard-style layout with collapsible left-hand navigation
- Single primary page per patient with domain-specific views accessible from side nav
- Strong, opinionated default layout (no drag-and-drop in Phase 1)
- 508-friendly by default: semantic HTML, keyboard navigability, color contrast

**Performance Goals:**
- Patient Overview page should load in under 4 seconds for 90% of patients (vs. ~20 seconds in current JLV)

### CCOW Context Management

**Purpose:**
- Implement HL7 CCOW-like patient context synchronization across applications
- Provide single source of truth for currently active patient
- Enable med-z1 and external clinical apps to maintain synchronized context

**Implementation:**
- Separate FastAPI service on port 8001
- Thread-safe in-memory context vault
- REST API for get/set/clear active patient context
- Development/testing scope (not full CCOW standard compliance)

**Key Endpoints:**
- `GET /ccow/active-patient` - Get current patient context
- `PUT /ccow/active-patient` - Set patient context
- `DELETE /ccow/active-patient` - Clear patient context
- `GET /ccow/history` - View context change history

**Integration:**
- med-z1 web app calls CCOW when user selects patient
- Configuration: `CCOW_BASE_URL = "http://localhost:8001"`

### VistA RPC Broker Simulator (Real-Time Data Layer)

**Purpose:**
- Simulate VA VistA Remote Procedure Call (RPC) interface for real-time data (T-0, today)
- Complement historical PostgreSQL data (T-1 and earlier) with current-day clinical data
- Enable testing of "Refresh from VistA" UI pattern without accessing real VistA systems

**Critical Architecture:**
- **Dual-Source Data**: PostgreSQL (T-1+, fast) + Vista (T-0, 1-3s latency)
- **ICN → DFN Resolution**: Automatic identity translation per VistA site
- **Site Selection Policy**: Default 3 sites max, per-domain limits, hard cap of 10
- **Merge/Dedupe**: Canonical event keys, Vista preferred for T-1+, no duplicates

**Implementation:**
- Separate FastAPI service on port 8003 (future)
- Multi-site simulation (3 sites: Alexandria 200, Anchorage 500, Palo Alto 630)
- JSON-based data files with T-0/T-1 relative notation (always "fresh")
- Configurable simulated network latency (1-3 seconds)
- Development/testing scope (Level 1 fidelity: data format only)

**Key Endpoints** (future):
- `POST /rpc/execute?site={sta3n}&icn={icn}` - Execute RPC with ICN
- `GET /sites` - List available VistA sites
- `GET /health` - Service health check

**Integration:**
- `app/services/vista_client.py` - HTTP client for med-z1 app
- `app/services/realtime_overlay.py` (future) - Merge/dedupe orchestration
- Configuration: `VISTA_SERVICE_URL = "http://localhost:8003"`
- UI Pattern: User-controlled "Refresh from VistA" button (no auto-fetch)

**Phase 1 Domains:** Demographics, Vitals, Allergies, Medications (~15 RPCs)

**Design Document:** `docs/vista-rpc-broker-design.md` (v1.2)
**Implementation Timeline:** Phase 8 (5-6 weeks, after Encounters + Labs)

### AI/ML Components

**Primary Use Cases (Early Phases):**
- Chart overview summarization
- Drug-drug interaction (DDI) risk assessment
- Patient flag-aware risk narratives

**Libraries:**
- OpenAI-compatible clients or other LLM APIs
- `transformers`, `sentence-transformers` for embeddings
- `langchain`/`langgraph` for agent workflows (optional)

**Vector Store:**
- Initially local (Chroma/FAISS)
- Later: pgvector in PostgreSQL

### Clinical Domains (Complete Scope)

**Implemented Domains (7):**
1. ✅ Dashboard - Patient overview with clinical widgets
2. ✅ Demographics - Full implementation (widget + dedicated page with comprehensive information)
3. ✅ Vitals - Full implementation (widget + dedicated page with charts)
4. ✅ Patient Flags - Modal-only implementation (topbar button, no widget/dedicated page)
5. ✅ Allergies - Full implementation (widget + dedicated page)
6. ✅ Medications - Full implementation (2x1 widget + dedicated page)
7. ✅ Encounters - Full implementation (1x1 widget + dedicated page with pagination) - **Completed 2025-12-15**

**ETL Complete, UI Pending (1):**
8. 🔧 Labs - **ETL pipeline complete** (Bronze/Silver/Gold/Load), 58 results in PostgreSQL. UI implementation pending (3x1 widget recommended) - **ETL Completed 2025-12-16**

**Placeholder Domains (6):**
9. 🚧 Problems - Diagnoses and problem list
10. 🚧 Orders - Clinical orders and requests
11. 🚧 Notes - Clinical notes and documents
12. 🚧 Imaging - Radiology and imaging studies
13. 🚧 Immunizations - Vaccination history (Later Phase)
14. 🚧 Procedures - Surgical and procedural history (Later Phase)

**UI Implementation Notes:**
- **Patient Flags**: Modal-only (accessible via topbar "View Flags" button with badge count). No dashboard widget or dedicated page per design decision 2025-12-14.
- **Encounters**: First domain to implement pagination (ADR-005). Shows inpatient admissions only (outpatient visits deferred to Phase 2). Default page size: 20, supports 10/20/50/100 per page.
- **Laboratory Results**: Recommended as 3x1 full-width widget to display multiple lab panels side-by-side with trend sparklines.
- **All other domains**: Follow Pattern A (patient.py routes) or Pattern B (dedicated router) based on complexity (see `docs/architecture.md` Section 3).

**DoD-specific views** (CHCS/AHLTA) are explicitly out of scope for early versions.

## Important Implementation Notes

### Identity Resolution

- In the UI and medallion layers, patients are keyed primarily by ICN (Integrated Care Number) and/or a derived `PatientKey`
- Internal CDW SIDs (e.g., `InpatientSID`, `PatientSID`, `RxOutpatSID`) are technical keys for joins, not primary identity elements in the UI
- Initial identity logic is simple: "1 ICN = 1 patient" in the mock environment (no complex merged-identity handling in early phases)

### Location Field Patterns

**IMPORTANT:** Clinical domains that use `Dim.Location` must follow consistent naming patterns in PostgreSQL schemas and queries.

**Established Patterns (as of 2025-12-16):**

1. **Vitals Domain**:
   - Schema columns: `location_id` (INT), `location_name` (VARCHAR), `location_type` (VARCHAR)
   - Query usage: Always SELECT all three columns
   - Template usage: Use `location_name` for display, `location_type` for filtering

2. **Laboratory Results Domain**:
   - Schema columns: `location_id` (INT), `collection_location` (VARCHAR), `collection_location_type` (VARCHAR)
   - Query usage: Always SELECT all three columns
   - Template usage: Use `collection_location` for display (note: different name to reflect specimen collection)

3. **Encounters Domain**:
   - Schema columns: `admit_location_id/name/type` AND `discharge_location_id/name/type` (6 total)
   - Query usage: Always SELECT all six columns
   - Template usage: Both admit and discharge locations available for display

**Common Mistake to Avoid:**
- ❌ **DO NOT** use single `location` column - always use three columns (id, name, type)
- ❌ **DO NOT** SELECT only the ID column - always include name and type for display
- ✅ **DO** update both schema DDL AND query layer when adding location support
- ✅ **DO** verify queries work after schema changes (prevents "column does not exist" errors)

**Root-Level Fix Philosophy:**
- Fix location data in source INSERT scripts (e.g., `Vital.VitalSign.sql`, `Chem.LabChem.sql`)
- Do NOT use post-load UPDATE scripts (patch/fix pattern)
- Ensure database can be rebuilt from scratch on new developer machines

### Configuration Management

- **Single shared Python environment** at project root: `.venv/`
- **Single shared .env file** at project root
- **Single shared config module:** `config.py` at project root
- All subsystems (app, ccow, etl, ai, mock) import from this central configuration

### SQL Server Scripting Patterns

When creating SQL Server scripts for the mock CDW, follow these conventions:

**QUOTED_IDENTIFIER Requirement:**
- Always include `SET QUOTED_IDENTIFIER ON;` before CREATE INDEX and INSERT statements
- Required for filtered indexes (indexes with WHERE clauses)
- Required when inserting into tables that have filtered indexes
- Example pattern:
  ```sql
  USE CDWWork;
  GO

  SET QUOTED_IDENTIFIER ON;
  GO

  CREATE INDEX IX_Example ON TableName (Column1, Column2)
      WHERE Column1 IS NOT NULL;  -- Filtered index
  GO
  ```

**Field Sizing:**
- Carefully consider field sizes for categorical data
- Example: Patient Record Flag categories are 'I' and 'II', requiring CHAR(2), not CHAR(1)
- Test INSERT statements with actual data values to validate field sizes

**Script Organization:**
- Separate CREATE and INSERT scripts for each table
- Location: `mock/sql-server/cdwwork/create/` and `mock/sql-server/cdwwork/insert/`
- Use GO statements to batch commands appropriately
- Include PRINT statements for execution feedback

**Master Script Maintenance (CRITICAL):**
- **ALWAYS update `_master.sql` scripts when adding new tables**
- Location: `mock/sql-server/cdwwork/create/_master.sql` and `mock/sql-server/cdwwork/insert/_master.sql`
- These scripts orchestrate the creation and population of the entire mock CDW database
- New developers and database rebuilds depend on these scripts being complete and current
- **Update timing:** Immediately upon completing Day 1 (schema + seed data) of any new domain
- **Dependency order matters:**
  - Dimension tables must be listed before fact tables that reference them
  - Parent tables must be created/populated before child tables with FK constraints
  - Example: `Dim.TIUDocumentDefinition` → `TIU.TIUDocument_8925` → `TIU.TIUDocumentText`
- **Both databases:** Remember to update CDWWork2 master scripts when implementing Cerner/Oracle Health schemas
- **Verification:** After updating master scripts, test by running them in a clean container to ensure all dependencies are satisfied

### Database Schema Management

**PostgreSQL Serving Database:**

The project uses two approaches for managing the PostgreSQL serving database schema, depending on the development phase:

**Initial Development (Current Phase):**
- **DDL Scripts:** Located in `db/ddl/`
- Purpose: Create tables from scratch
- Safe to drop/recreate tables (no production data)
- Examples: `patient_demographics.sql`, `create_patient_flags_tables.sql`
- Run directly via psql or docker exec

**Production/Mature Phase (Future):**
- **Migration Scripts:** Will be located in `db/migrations/` (when needed)
- Purpose: Evolve schema incrementally without data loss
- Versioned, sequential changes (e.g., `001_add_column.sql`, `002_add_index.sql`)
- Tracks which migrations have been applied
- Each migration typically has "up" (apply) and optionally "down" (rollback) operations
- Common tools: Alembic (Python/SQLAlchemy), Flyway, Liquibase

**When to Switch:**
- Use DDL scripts during initial development and prototyping
- Switch to migrations when:
  - Database contains real data that must be preserved
  - Multiple developers need schema synchronization
  - Production deployment requires zero-downtime schema changes
  - Need audit trail of all schema changes

**Directory Structure:**
```
db/
  ddl/           # Initial schema creation scripts (drop/create safe)
  migrations/    # Incremental schema changes (future, when needed)
  seeds/         # Sample/test data scripts (future, if needed)
```

### Code Quality and Testing

The project uses:
- `pytest` for testing (configured in `pytest.ini` with cache relocated to `.cache/pytest`)
- `ruff`, `black`, `mypy` for linting and formatting (optional)
- Docker/Podman for SQL Server, MinIO, PostgreSQL containers

**Script Organization:**
- **`scripts/`** - All testing, debugging, and utility scripts (consolidated approach for simplicity)
  - Place all scripts here, not in project root
  - **Formal pytest tests:** Use `test_*.py` naming convention for automated tests
  - **Ad-hoc utilities:** Use descriptive names (e.g., `minio_test.py`, `update_vitals_locations.py`)
  - Examples: pytest test suites, MinIO connection tests, manual CCOW vault tests, Parquet file readers, data update utilities
  - Run tests with: `pytest scripts/` or configure `testpaths = scripts` in `pytest.ini`

### Security and Privacy

- **Local development uses ONLY synthetic, non-PHI/PII data**
- All mock data is version-controlled and safe for public repositories
- Real-data environments will require PHI/PII handling per VA standards, SSO, RBAC, and comprehensive audit logging

## Reference Documentation

### Core Architecture and Planning Documents

**Primary Reference (Consult First):**
- **`docs/architecture.md`** - System architecture and routing decisions (Document version v1.0) ✅ Complete
  - **Purpose:** Authoritative source for architectural decisions, patterns, and rationale
  - **When to Use:** Before designing new features, when choosing between patterns, when questioning existing designs
  - **Contents:** API routing patterns, data architecture, ADRs (Architecture Decision Records)
  - **Living Document:** Updated when new architectural decisions are made

**Product Planning:**
- `docs/med-z1-plan.md` - Complete product and technical development plan (Document version v1)
  - High-level roadmap, phases, feature priorities
  - Product vision and strategic direction

**Design Specifications (Feature-Specific):**
- `docs/patient-dashboard-design.md` - Dashboard and widget system specification (Document version v1.1)
- `docs/patient-flags-design.md` - Phase 3 Patient Flags implementation specification (Document version v1.2)
- `docs/vitals-design.md` - Vitals implementation specification ✅ Complete
- `docs/allergies-design.md` - Allergies implementation specification (Days 1-5 complete)
- `docs/demographics-design.md` - Demographics full page implementation (Document version v2.2) ✅ Complete
- `docs/vista-rpc-broker-design.md` - VistA RPC Broker Simulator specification (Document version v1.2) ✅ Design Complete
  - Real-time data layer (T-0, today)
  - ICN → DFN resolution, site selection policy, merge/dedupe rules
  - 6-phase implementation plan (~5-6 weeks)

**Future Planning:**
- `docs/vision.md` - Problem statement, user personas, user stories (to be created)
- `docs/ai-design.md` - AI/ML, RAG, and DDI use-case designs (to be created)

### Subsystem-Specific README Files (Practical Guidance)

- **`app/README.md`** - FastAPI/HTMX application setup and routing patterns
  - Quick reference for API routing decisions (Pattern A vs Pattern B)
  - Real-time data integration patterns (Vista RPC Broker)
  - Code examples for implementing new domains
  - Links to `docs/architecture.md` for detailed rationale
- `ccow/README.md` - CCOW Context Vault setup and usage
- `vista/README.md` - VistA RPC Broker simulator setup and RPC reference (future)
- `etl/README.md` - ETL setup instructions and data-specific notes
- `mock/README.md` - Mock data subsystem overview
- `ai/README.md` - AI/ML layer guidance

### Document Hierarchy and When to Use Each

```
┌─────────────────────────────────────────────────────────────────┐
│ "Why was this decision made?" → docs/architecture.md            │
│   (Authoritative architectural decisions and ADRs)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│ "How do I implement this?" → app/README.md, etl/README.md, etc. │
│   (Practical quick reference with code examples)                │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│ "What was built and how?" → docs/<domain>-design.md             │
│   (Feature-specific implementation details and context)         │
└─────────────────────────────────────────────────────────────────┘
```

**Typical Workflow:**
1. **Planning a new feature?** → Start with `docs/architecture.md` to understand patterns
2. **Implementing the feature?** → Check `app/README.md` for quick code examples
3. **Documenting the feature?** → Create/update `docs/<domain>-design.md` with implementation details
4. **Made a new architectural decision?** → Add ADR to `docs/architecture.md`

## Development Phases

**Phase 0 (1-2 weeks):** Environment & skeleton setup
**Phase 1 (2-3 weeks):** Mock CDW & Bronze extraction
**Phase 2 (3-5 weeks):** Silver & Gold transformations
**Phase 3 (3-4 weeks):** Serving DB loading, basic UI, CCOW integration
**Phase 4 (3-6 weeks):** AI-assisted features (experimental)
**Phase 5 (Ongoing):** Hardening, observability, UX iteration
