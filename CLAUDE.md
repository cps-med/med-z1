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
  etl/           # ETL scripts (Bronze/Silver/Gold transformations)
  mock/          # Mock data subsystem (simulates CDW, SDP, etc.)
    sql-server/  # Microsoft SQL Server schemas and data
      cdwwork/   # VistA-like mock data
      cdwwork1/  # New EHR-like mock data
  ai/            # AI/ML and agentic components
  db/            # Serving DB DDL, migrations (create when needed)
  docs/          # Architecture, design docs
  lake/          # MinIO/Parquet access configs (create when needed)
  tests/         # Unit/integration tests (create when needed)
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

# Access in browser
# Main app: http://127.0.0.1:8000/
# CCOW service: http://127.0.0.1:8001/
# CCOW API docs: http://127.0.0.1:8001/docs
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

### Data Architecture

**Source Systems (Development):**
- Mock CDW running in Docker (SQL Server 2019)
  - `CDWWork` database: VistA-like data (maps to real CDWWORK)
  - `CDWWork1` database: Oracle Health-like data (maps to real CDWWORK2)
- Both populated with synthetic, non-PHI/PII data only

**Medallion Pipeline:**
- **Bronze Layer:** Raw data from mock CDW, minimal transformation, stored as Parquet in MinIO
- **Silver Layer:** Cleaned and harmonized data across CDWWork and CDWWork1, unified patient identity (ICN/PatientKey)
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
- CDWWork1 intentionally uses different naming conventions to exercise Silver-layer harmonization

**Major Schemas in CDWWork:**
- `Dim` (dimensions: Sta3n, State, PatientRecordFlag, etc.)
- `SPatient` (patient demographics, addresses, insurance, PatientRecordFlagAssignment, PatientRecordFlagHistory)
- `SStaff` (staff/providers)
- `Inpat` (inpatient encounters)
- `RxOut` (outpatient medications)
- `BCMA` (medication administration)
- Future: Labs, Vitals, Orders, Notes, Imaging

**Patient Flags Tables (added 2025-12-10):**
- `Dim.PatientRecordFlag` - Flag definitions (National Cat I, Local Cat II)
- `SPatient.PatientRecordFlagAssignment` - Patient → Flag assignments with review tracking
- `SPatient.PatientRecordFlagHistory` - Audit trail with sensitive narrative text

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

### Clinical Domains (Initial Scope)

Focus areas for Phase 1+:
- Admissions/Encounters (inpatient and outpatient)
- Allergies
- Demographics
- Orders
- Problems/Diagnoses
- Medications
- Laboratory Results
- Notes/Documents
- Radiology/Imaging
- Vitals
- Patient Flags

DoD-specific views (CHCS/AHLTA) are explicitly out of scope for early versions.

## Important Implementation Notes

### Identity Resolution

- In the UI and medallion layers, patients are keyed primarily by ICN (Integrated Care Number) and/or a derived `PatientKey`
- Internal CDW SIDs (e.g., `InpatientSID`, `PatientSID`, `RxOutpatSID`) are technical keys for joins, not primary identity elements in the UI
- Initial identity logic is simple: "1 ICN = 1 patient" in the mock environment (no complex merged-identity handling in early phases)

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
- `pytest` for testing
- `ruff`, `black`, `mypy` for linting and formatting (optional)
- Docker/Podman for SQL Server, MinIO, PostgreSQL containers

### Security and Privacy

- **Local development uses ONLY synthetic, non-PHI/PII data**
- All mock data is version-controlled and safe for public repositories
- Real-data environments will require PHI/PII handling per VA standards, SSO, RBAC, and comprehensive audit logging

## Reference Documentation

For detailed information, see:
- `docs/med-z1-plan.md` - Complete product and technical development plan (Document version v1)
- `docs/patient-flags-design.md` - Phase 3 Patient Flags implementation specification (Document version v1.2)
- `docs/vision.md` - Problem statement, user personas, user stories (to be created)
- `docs/architecture.md` - Diagrams and architecture decisions (to be created)
- `docs/ai-design.md` - AI/ML, RAG, and DDI use-case designs (to be created)

Subsystem-specific README files:
- `app/README.md` - FastAPI/HTMX application setup and guidance
- `ccow/README.md` - CCOW Context Vault setup and usage
- `etl/README.md` - ETL setup instructions and data-specific notes
- `mock/README.md` - Mock data subsystem overview
- `ai/README.md` - AI/ML layer guidance

## Development Phases

**Phase 0 (1-2 weeks):** Environment & skeleton setup
**Phase 1 (2-3 weeks):** Mock CDW & Bronze extraction
**Phase 2 (3-5 weeks):** Silver & Gold transformations
**Phase 3 (3-4 weeks):** Serving DB loading, basic UI, CCOW integration
**Phase 4 (3-6 weeks):** AI-assisted features (experimental)
**Phase 5 (Ongoing):** Hardening, observability, UX iteration
