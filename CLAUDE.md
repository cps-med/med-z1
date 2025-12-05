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
  etl/           # ETL scripts (Bronze/Silver/Gold transformations)
  mock/          # Mock data subsystem (simulates CDW, SDP, etc.)
    sql-server/  # Microsoft SQL Server schemas and data
      cdwwork/   # VistA-like mock data
      cdwwork1/  # New EHR-like mock data
  ai/            # AI/ML and agentic components
  db/            # Serving DB DDL, migrations (create when needed)
  docs/          # Architecture, design docs, devlog
  lake/          # MinIO/Parquet access configs (create when needed)
  tests/         # Unit/integration tests (create when needed)
```

## Common Development Commands

### Running the FastAPI Application

From project root:
```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Run the FastAPI development server
uvicorn app.main:app --reload

# Access in browser
# http://127.0.0.1:8000/
```

Stop server with CTRL+C.

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
- `Dim` (dimensions: Sta3n, State, etc.)
- `SPatient` (patient demographics, addresses, insurance)
- `SStaff` (staff/providers)
- `Inpat` (inpatient encounters)
- `RxOut` (outpatient medications)
- `BCMA` (medication administration)
- Future: Labs, Vitals, Orders, Flags, Notes, Imaging

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
- All subsystems (app, etl, ai, mock) import from this central configuration

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
- `docs/vision.md` - Problem statement, user personas, user stories (to be created)
- `docs/architecture.md` - Diagrams and architecture decisions (to be created)
- `docs/ai-design.md` - AI/ML, RAG, and DDI use-case designs (to be created)
- `docs/devlog/` - Running design/development notes (to be created)

Subsystem-specific README files:
- `app/README.md` - FastAPI/HTMX application setup and guidance
- `etl/README.md` - ETL setup instructions and data-specific notes
- `mock/README.md` - Mock data subsystem overview
- `ai/README.md` - AI/ML layer guidance

## Development Phases

**Phase 0 (1-2 weeks):** Environment & skeleton setup
**Phase 1 (2-3 weeks):** Mock CDW & Bronze extraction
**Phase 2 (3-5 weeks):** Silver & Gold transformations
**Phase 3 (3-4 weeks):** Serving DB loading & basic UI
**Phase 4 (3-6 weeks):** AI-assisted features (experimental)
**Phase 5 (Ongoing):** Hardening, observability, UX iteration
