# med-z1 – Product & Technical Development Plan

February 11, 2026 • Document version v1.9

**Related Documentation:**
Refer to `docs/guide/` and `docs/spec/` for project background, implementation approach, developer setup guides, and design specifications for each clinical domain.
Current implementation status is maintained in `docs/spec/implementation-status.md`.

**Changelog:**
- **v1.9 (February 11, 2026):** Adopted `docs/spec/implementation-status.md` as the single source of truth for implementation status. Updated high-level references to current spec/guide file paths.
- **v1.8 (January 20, 2026):** Updated implementation status to reflect 9 clinical domains complete (added Immunizations). Updated Vista RPC Broker to Phase 5 complete (4 domains operational: Vitals, Encounters, Allergies, Medications). Updated AI Clinical Insights to reflect Phase 6 complete (Conversation Memory with PostgreSQL checkpointer). Updated current status dates and counts throughout document.
- **v1.7 (January 10, 2026):** Updated implementation status to reflect 8 clinical domains complete (added Clinical Notes). Updated AI/ML status to reflect Phase 4 completion (AI Clinical Insights operational with 4 tools). Corrected Python dependencies section (polars, uvicorn, Jinja2). Removed SSN search and facility filter from patient search specification per VA policy decisions.
- **v1.6 (December 20, 2025):** Updated CCOW Context Management to v2.0 (multi-user enhancement complete). Added session timeout behavior documentation. Fixed timezone bug in session validation. See `docs/spec/ccow-multi-user-enhancement.md`, `docs/session-timeout-behavior.md`, and `docs/guide/developer-setup-guide.md`.
- **v1.5 (December 18, 2025):** Added User Authentication and Management implementation status. All 8 authentication phases complete (database, routes, middleware, login UI, session management, testing). See `docs/spec/user-auth-design.md`.
- **v1.4 (December 16, 2025):** Updated current status to reflect 7 clinical domains implemented (added Encounters). Noted Laboratory Results ETL completion (UI implementation pending). Updated "Next Priorities" section.
- **v1.3 (December 15, 2025):** Refactored to focus on strategic vision and product planning. Removed redundant technical implementation details (now in `med-z1-implementation-roadmap.md`). Updated current status to reflect 6 clinical domains implemented and Vista Phase 1 complete.
- **v1.2 (December 8, 2025):** Updated with actual implementation details - medallion architecture working, PostgreSQL setup, MinIO client, ETL pipeline complete for patient demographics, actual dependencies and project structure
- **v1.1 (December 7, 2025):** Updated with CCOW integration requirements
- **v1.0 (Initial):** Original strategic plan

## 1. Product Vision

**med-z1** is a next-generation longitudinal health record viewer for the Department of Veterans Affairs, designed to:

- Replace and modernize the current **Joint Longitudinal Viewer (JLV)**.
- Provide fast, consistent access to patient data by sourcing from the **VA Corporate Data Warehouse (CDW)** instead of RPC calls to 140+ VistA instances.
- Seamlessly blend **legacy VistA data** (CDWWork, representing VistA) and **new EHR data** (CDWWork2, representing Oracle Health) in the mock environment, mirroring real CDWWORK/CDWWORK2.
- Simulate real-time RPC calls to VistA sites for current data for designated clinical domains.
- Introduce **AI-assisted** capabilities to help clinicians understand a patient’s history, risks, and care plan.

The application will be built primarily in **Python**, including:

- ETL and **medallion data architecture** pipeline.
- Backend APIs and services.
- AI/ML and agentic components.
- Web UI using **FastAPI + HTMX + Jinja2** (minimal/targeted JavaScript only).

### 1.1 Hybrid Architecture Principle

med-z1 will use a **hybrid** architecture:

- **Source system (simulated for development):**
  - A **local mock CDW** running in Docker using **Microsoft SQL Server 2019**.
  - Two databases:
    - `CDWWork` (mock VistA data; conceptually maps to real CDWWORK).
    - `CDWWork2` (mock new EHR data; conceptually maps to real CDWWORK2).
  - Both populated with **synthetic, non-PHI/PII data**.
  - Mock **VistA sites** available via RPC endpoints.

- **Core medallion pipeline:** **Parquet/Delta** files stored in **MinIO** (S3/ADLS Gen2 compatible) on the local Mac.

- **Serving database for the UI:** A PostgreSQL relational database to support low-latency per-patient queries and RAG-enhanced agentic AI functionality.

In a real deployment, the mock CDW would be replaced by the actual VA CDW, but the medallion + serving architecture remains the same.

---

## 2. Target Users & Core Use Cases

### 2.1 Primary Users

- **Physicians** (attendings, residents, specialists)
- **Nurses and care coordinators**
- **Pharmacists and pharmacy techs**
- **Other clinical support staff** who currently rely on JLV/EHR access.

### 2.2 Initial Clinical Domains (Phase 1+)

For the initial versions of med-z1, the primary clinical domains are:

- **Patient Demographics**
- **Patient Flags**
- **Vital Signs**
- **Inpatient Encounters**
- **Allergies & Adverse Reactions**
- **Medications**
- **Laboratory Results**
- **Clinical Notes**
- **Immunizations**
- **Problems / Diagnoses**
- **Orders**
- **Procedures**
- **Radiology / Imaging**

**DoD-specific views** and data (e.g., CHCS/AHLTA, purely DoD-only domains) are explicitly **out of scope** for early versions. The focus is **VA-internal data** sourced from CDW and the mock real-time VistA service.

### 2.3 Core Use Cases (Initial Scope)

1. **CCOW-Aware Patient Context Management**
   - On application startup, query CCOW Context Vault to retrieve current active patient (if set).
   - Display patient demographics in persistent header area:
     - Patient name, ICN (Integrated Care Number).
     - Last 4 digits of SSN (for verification).
     - Date of birth, calculated age, biological sex.
     - Primary VA facility/station.
   - If no patient context is set in CCOW vault:
     - Display "No patient selected" (or similar) in header.
     - User can search for and select a patient via header search UI.
   - **Patient search and context setting workflow:**
     - User enters search criteria (name, ICN, EDIPI) via header search.
     - Search results display matching patients with key identifiers.
     - User selects a patient from results.
     - User explicitly clicks "Set Context" or similar action to update CCOW vault.
     - App refreshes header to display selected patient demographics.
   - CCOW context is checked **only on initial page load** (no periodic polling in Phase 1).

2. **Patient Longitudinal Summary**
   - Integrated timeline of encounters, problems, medications, labs, and procedures across VistA (from `CDWWork`) and the new EHR (from `CDWWork2`).
   - Display clear source provenance (facility, system, time).

3. **Domain-Specific Views**
   - For each domain (e.g., Medications, Labs, Problems, Notes, Imaging, Vitals, Orders, Admissions), provide:
     - Filterable, sortable tables.
     - Consistent display of key fields and source system.
     - Ability to focus on recent vs. historical data.

4. **Patient Flags & Risk Indicators**
   - Retrieve and display Patient Flags from CDW.
   - Use flags as part of the risk and summary story (Phase 2+).

5. **AI-Assisted Chart Overview** ✅ **IMPLEMENTED**
   - Natural-language **chart overview** via `/insight` conversational interface:
     - Major chronic conditions.
     - Recent admissions/ED visits.
     - Key labs and trends.
     - Clinical notes analysis.
     - Notable flags and orders.
   - Powered by LangGraph agent with OpenAI GPT-4 Turbo.

6. **AI-Supported Medication Safety** ✅ **IMPLEMENTED**
   - Identify **drug-drug interaction (DDI) risk** for the current medication list.
   - Severity assessment with clinical recommendations.
   - Patient flag-aware risk narratives.
   - Integrated with comprehensive patient summaries.

7. **AI-Aware Patient Flags** ✅ **IMPLEMENTED**
   - Patient Flag data incorporated into AI risk assessment.
   - AI summaries are flag-aware and include relevant safety alerts in narratives.
   - Behavioral flags, safety alerts, and clinical risks surfaced in AI responses.

---

## 3. UX & Interaction Model

### 3.1 Overall Layout

med-z1 will use a **dashboard-style layout** with:

- A **persistent patient header** (top of page):
  - **Always visible** across all pages/views.
  - **CCOW-aware**: Displays current patient from CCOW Context Vault.
  - **Patient demographics displayed** (when patient context is set):
    - Patient name and ICN (Integrated Care Number).
    - Last 4 digits of SSN.
    - Date of birth, calculated age, and biological sex.
    - Primary VA facility/station.
  - **When no patient is selected** (CCOW vault empty):
    - Display "No patient selected" or similar message.
  - **Patient search UI** embedded in header:
    - Search bar or button to initiate patient search.
    - Search by: name, ICN, EDIPI.
    - Search results displayed inline or as dropdown/overlay.
    - User selects patient from results, then explicitly clicks "Set Context" to update CCOW vault.
  - **On initial page load**:
    - App queries CCOW vault (`GET /ccow/active-patient`).
    - If patient context exists, fetch patient demographics from serving DB and populate header.
    - If no context exists, display "No patient selected" state.

- A **left-hand side navigation bar**:
  - Collapsible (e.g., hamburger icon at top-left).
  - Contains navigation icons and links for:
    - Dashboard
    - Demographics
    - Vitals
    - Encounters
    - Allergies
    - Medications
    - Labs
    - Notes
    - Immunizations
    - Problems
    - Orders
    - Procedures
    - Imaging
    - Insights

- A **main content area on the right**:
  - Scrollable main content section below patient header.

The design will favor a **single primary page per patient** with:

- A **Dashboard** page showing:
  - A single widget for each clinical domain
  - Widgets vary in size, from 1 to 3 columns wide by 1 row deep

- Multiple **domain-specific pages** are accessible from the side navigation, each focused and uncluttered.

- An AI-assisted **Insights** page that provides RAG and Agentic AI prompts and responses.

### 3.2 Patient Search & Identity Resolution

**User experience:**

- Entry point is a **patient search UI in the header** (always accessible).
- User can search by:
  - Patient **Name**
  - **ICN** (Integrated Care Number)
  - **EDIPI** (DoD ID)
  - Other identifiers (as available in serving DB).

- Search results display matching patients with:
  - Name, date of birth, age, sex.
  - ICN, last 4 of SSN.
  - Facility/station.
  - Key demographic hints to avoid wrong-patient selection.

- **Patient selection and CCOW context setting:**
  - User selects a patient from search results.
  - User clicks **"Set Context"** or similar explicit action button.
  - App makes `PUT /ccow/active-patient` request to CCOW vault with selected patient's ICN.
  - On successful vault update:
    - App fetches full patient demographics from serving DB.
    - Patient header refreshes to display selected patient information.
    - App navigates to Patient Overview page (or remains on current page with updated context).

**Under the hood:**

- CDW's internal SIDs (e.g., `InpatientSID`, `PatientSID`, `RxOutpatSID`) are **technical keys** for internal joins and are not primary identity elements in the UI.
- med-z1 will:
  - Resolve to a **canonical identity** (ICN) when available.
  - Represent patients in the UI and medallion layers keyed primarily by ICN and/or a derived `PatientKey`.
  - **CCOW vault stores patient_id as ICN** for consistency.
  - Keep the **initial identity logic simple** in early versions:
    - No complex merged-identity handling.
    - Focus on "1 ICN = 1 patient" in the mock environment.

### 3.3 Layout & Customization Philosophy

- Early versions will provide a **strong, opinionated default layout**:
  - No drag-and-drop layouts or heavy customization in Phase 1.
  - Focus on clean, predictable views and clear navigation.
- Later phases may add:
  - Per-user **saved filters** (e.g., default date ranges).
  - Favorite domain shortcuts.
  - Theme switching or accessibility presets.

### 3.4 Accessibility & Performance Goals

- Design will be **508-friendly by default**:
  - Semantic HTML structure.
  - Keyboard navigability across navigation and tables.
  - Sufficient color contrast and optional high-contrast mode.

- **Performance target (aspirational):**
  - **Patient Overview page** should load in **under 4 seconds for 90% of patients** when using pre-fetched medallion data in the serving DB.
  - This is a major improvement over the current JLV model (often ~20 seconds due to real-time RPC calls).

Data freshness indicators and ETL status will be **initially treated as admin-level concerns**, not shown prominently in the clinician UI.

**Implementation Reference:** See `docs/spec/patient-topbar-design.md` for detailed UI specifications, mockups, and code examples for the patient-aware topbar.

---

## 4. Technology Stack

### 4.1 Core Languages & Frameworks

- **Language:** Python 3.11 (for maximum compatibility with dependencies)
- **Backend Web Framework:** FastAPI
- **Templating:** Jinja2
- **Interactive UX:** HTMX

**Rationale:** Python 3.11 is chosen as the baseline for med-z1 because it offers a strong balance of performance and ecosystem stability. Many core dependencies for this project—data/ML libraries, database drivers, and AI tooling—have mature, well-tested support for 3.11, while newer Python versions can still lag slightly in compatible binary wheels and integrations. Standardizing on 3.11 reduces friction when installing and upgrading dependencies, while still benefiting from the “Faster CPython” improvements over older versions (3.9/3.10). Future upgrades to 3.12+ can be evaluated in a separate experimental environment once the full stack is known to be compatible.

### 4.2 Data & Medallion Architecture

**High-Level Approach:**

med-z1 implements a **medallion data architecture** (Bronze → Silver → Gold) using:
- **Source:** Mock CDW (SQL Server) with VistA-like schemas
- **Data Lake:** MinIO (S3-compatible) storing Parquet files
- **Processing:** Polars for transformations, SQLAlchemy for database connectivity
- **Serving:** PostgreSQL database optimized for low-latency patient queries

**Layers:**
- **Bronze:** Raw data from mock CDW with minimal transformation
- **Silver:** Cleaned, harmonized data with unified patient identity (ICN)
- **Gold:** Curated, query-optimized views ready for UI consumption

**ETL Patterns:**
- Direct Python script execution for development (`python -m etl.bronze_patient`)
- Future: Orchestration with Prefect, Airflow, or Azure Data Factory

> **For detailed medallion implementation, ETL patterns, code examples, and current pipeline status, see `docs/spec/med-z1-implementation-roadmap.md` Section 11.**

### 4.3 Serving Database

**Database:** PostgreSQL 16 (running in Docker)
- Database name: `medz1`
- Optimized for low-latency per-patient queries
- Populated from Gold layer Parquet files

**Design Pattern:**
- One table per clinical domain (e.g., `patient_demographics`, `patient_vitals`, `patient_medications`)
- Primary key: `patient_key` (ICN-based)
- Indexes on frequently queried fields (ICN, name, SSN, dates, station)

**Future Extension:** pgvector for AI/ML embeddings

> **For complete PostgreSQL schema details, DDL scripts, and loading patterns, see `docs/spec/med-z1-implementation-roadmap.md` Section 10.**

### 4.4 Mock CDW Subsystem

**Purpose:** Simulate VA Corporate Data Warehouse for local development with synthetic data only (no PHI/PII).

**Implementation:**
- **Container:** Microsoft SQL Server 2019 (Docker)
- **Databases:**
  - `CDWWork` – VistA-like data
  - `CDWWork2` – Oracle Health-like data
- **Schemas:** `Dim`, `SPatient`, `SStaff`, `Inpat`, `RxOut`, `BCMA`, `Vital`, `LabChem`, etc.

**Key Conventions:**
- Surrogate primary keys: `*SID` columns (e.g., `PatientSID`, `InpatientSID`)
- Station identifier: `Sta3n` field in most tables
- Foreign key constraints lightweight or omitted for simplicity

**Data:** Version-controlled DDL and INSERT scripts in `mock/sql-server/cdwwork/` and `mock/sql-server/cdwwork2/`.

### 4.5 CCOW Context Management (v2.0 - Multi-User)

* **Purpose:**

  * Implement a simplified version of the HL7 CCOW (Clinical Context Object Workgroup) standard for **patient context synchronization** across applications.
  * Provide a **single source of truth** for the currently active patient context, enabling med-z1 and other clinical applications to stay synchronized during clinical workflows.
  * **v2.0 Enhancement:** Support **multi-user context isolation** - each authenticated user maintains their own independent active patient context.

* **Implementation (v2.0):**

  * **FastAPI service** running on port 8001 (separate from main app on port 8000).
  * **Thread-safe in-memory vault** (`vault.py`) with per-user context storage (dictionary keyed by `user_id`).
  * **Session-based authentication** - validates `session_id` cookie against PostgreSQL `auth.sessions` table.
  * **User context isolation** - `user_id` automatically extracted from validated session (prevents spoofing).
  * **REST API endpoints** for getting, setting, and clearing active patient context (all require authentication).
  * **Context persistence** - user's patient context survives logout/login cycles (supports multi-application workflows).
  * **History tracking** - user-scoped and global context change history with filtering.
  * **Stale context cleanup** - automatic removal of contexts inactive for 24+ hours.
  * Pydantic models for request/response validation with `user_id`, `email`, and timestamps.

* **Key Features (v2.0):**

  * ✅ **Multi-user isolation** - Each user has independent patient context
  * ✅ **Session validation** - Direct PostgreSQL query for security
  * ✅ **Context persistence** - Survives med-z1 logout (critical for multi-app workflows)
  * ✅ **History filtering** - User-scoped (`scope=user`) or global (`scope=global`)
  * ✅ **Admin endpoints** - Get all contexts, manual cleanup
  * ✅ **Timezone-aware** - Fixed session expiry comparison bug

* **Integration Points:**

  * med-z1 web app (`app/`) calls CCOW service when user selects a patient, forwards `session_id` cookie.
  * All authenticated routes (dashboard, patient pages, etc.) get active patient from CCOW.
  * Future integration: external clinical applications (CPRS, imaging viewers, pharmacy systems) can query/set context with their own session cookies.
  * Configuration: `CCOW_ENABLED=true`, `CCOW_URL=http://localhost:8001` in `.env`.

* **Security Model (v2.0):**

  * `session_id` cookie required for all context endpoints (except health check).
  * `user_id` extracted from validated PostgreSQL session (not from request body).
  * Session expiry, active status, and user active status all validated.
  * Prevents user_id spoofing attacks.

**Implementation Reference:**
- **Design:** `docs/spec/ccow-vault-design.md` (v1.1 baseline), `docs/spec/ccow-multi-user-enhancement.md` (v2.0 spec)
- **Testing Guide:** `docs/guide/ccow-v2.1-testing-guide.md`
- **API Testing:** Use curl or Insomnia with `session_id` cookie (see testing guide)

### 4.6 AI & Agentic

**✅ IMPLEMENTED (Phase 6 Complete - January 20, 2026)**

* **LLM:** OpenAI GPT-4 Turbo (`gpt-4-turbo-preview`)

* **Framework:** LangGraph for agent workflow orchestration

* **Libraries:**
  * `langchain==1.2.0` - LLM application framework
  * `langchain-openai==1.1.6` - OpenAI integration
  * `langgraph==1.0.5` - Agent workflow orchestration (Phase 1-5)
  * `langgraph-checkpoint-postgres==2.0.16` - Persistent conversation memory (Phase 6)
  * `psycopg[binary,pool]>=3.1.0` - PostgreSQL async driver for checkpointer (Phase 6)
  * `openai==2.14.0` - OpenAI API client
  * `markdown==3.10` - Markdown rendering for AI responses

* **Operational AI Tools (4):**
  1. `check_ddi_risks` - Drug-drug interaction analysis with severity assessment
  2. `get_patient_summary` - Comprehensive patient overview including demographics, medications, vitals, allergies, encounters, and clinical notes
  3. `analyze_vitals_trends` - Statistical vitals analysis with clinical interpretation
  4. `get_clinical_notes_summary` - Clinical note queries with filtering by type and date range

* **User Interface:** `/insight` conversational AI page with LangGraph agent and chat interface

* **Conversation Memory (Phase 6):**
  * ✅ **PostgreSQL checkpointer** - LangGraph AsyncPostgresSaver for persistent chat history
  * ✅ **User-scoped threads** - Thread ID format: `{user_id}_{patient_icn}` for multi-user isolation
  * ✅ **Cross-session persistence** - Conversations survive page refreshes and login sessions
  * ✅ **Clear chat history** - User-controlled conversation reset button
  * ✅ **System message optimization** - Injected only on first message (prevents accumulation)
  * ✅ **Schema:** 4 tables in `public` schema (checkpoints, checkpoint_writes, checkpoint_blobs, checkpoint_migrations)
  * 📝 **Configuration:** `LANGGRAPH_CHECKPOINT_URL` in `config.py`

* **Implemented Use Cases:**
  * ✅ Chart overview summarization with clinical notes context
  * ✅ Drug-drug interaction (DDI) risk assessment
  * ✅ Patient flag-aware risk narratives
  * ✅ Clinical note analysis and synthesis
  * ✅ Vital sign trend analysis with statistical significance
  * ✅ Follow-up questions with conversation context (Phase 6)

* **Vector Store:** Not yet implemented (future: pgvector in PostgreSQL for semantic search)

> **For complete AI implementation details, see `docs/spec/ai-insight-design.md` (v2.4)**

### 4.7 Tooling & Dev Experience

* **IDE:** VS Code (Python, Jupyter, Docker, SQL extensions)
* **Environment:** `venv` + `.env` with python-dotenv
* **Testing:** `pytest`
* **Containers:** Docker for SQL Server, MinIO, PostgreSQL

**Key Python Dependencies (requirements.txt):**
- `boto3==1.35.76` - MinIO/S3 client
- `polars>=1.0.0` - DataFrame library (flexible versioning)
- `pyarrow==18.1.0` - Parquet support
- `sqlalchemy==2.0.36` - Database ORM
- `pyodbc==5.2.0` - SQL Server driver
- `psycopg2-binary==2.9.11` - PostgreSQL driver
- `fastapi==0.123.9` - Web framework
- `uvicorn==0.38.0` - ASGI server
- `Jinja2==3.1.6` - Template engine
- `python-dotenv==1.2.1` - Environment configuration
- `connectorx==0.3.3` - Available but optional (compatibility issues with Polars 1.x)

Note: AI/ML dependencies (langchain, langgraph, openai) detailed in section 4.6.

### 4.8 Vista RPC Broker - Real-Time Data Layer

**Purpose:** Bridge the T-0 (today) data freshness gap that exists when relying solely on the Corporate Data Warehouse.

#### The Challenge: T-0 Data Freshness Gap

The VA Corporate Data Warehouse (CDW) operates on a **nightly batch update schedule**, meaning data in CDW is always **at least T-1 (yesterday's data)**. While this is acceptable for historical analysis and trending, it creates a critical gap for clinicians who need **T-0 (today's) real-time information** during active patient encounters.

**Real-World Scenarios Where T-0 Data Matters:**

- **Morning Vitals:** A patient's blood pressure taken at 8:00 AM today won't appear in CDW until tomorrow's batch runs. Clinicians reviewing the patient at 10:00 AM need to see those vitals now.
- **Medication Administration:** BCMA (Bar Code Medication Administration) records from today's shift are invisible in CDW until tomorrow. Pharmacists and nurses need real-time medication administration status.
- **New Allergies:** An allergy documented this morning during triage must be immediately visible to prescribers to prevent adverse reactions.
- **Recent Lab Results:** Critical lab results from this morning need to be available now, not tomorrow.

**Current JLV Limitation:**

The existing Joint Longitudinal Viewer (JLV) attempts to solve this by making **real-time RPC calls to 140+ VistA instances** for every query, resulting in:
- ❌ Slow performance (~20 seconds average page load)
- ❌ High network overhead
- ❌ Poor user experience
- ❌ Scalability challenges

med-z1's architecture addresses this with a **hybrid dual-source approach**.

#### The Solution: Dual-Source Data Pattern

med-z1 implements a **strategic dual-source data pattern** that leverages the best of both worlds:

**Primary Source - PostgreSQL Serving Database (T-1 and earlier):**
- Fast, indexed queries for historical data
- Pre-aggregated Gold layer views
- Consistent <2 second response times
- Handles 95% of typical clinical queries

**Secondary Source - Vista RPC Broker (T-0, today):**
- Real-time queries to simulated VistA instances when needed
- User-controlled "Refresh from VistA" button (not automatic)
- Fetches only today's data, merged with historical PostgreSQL data
- Targeted, on-demand freshness

**How It Works:**

1. **Default Behavior:** Page loads show fast PostgreSQL data (T-1 and earlier)
2. **User Action:** Clinician clicks "Refresh from VistA" for a specific domain
3. **Real-Time Fetch:** Vista RPC Broker queries relevant sites for T-0 data
4. **Intelligent Merge:** System deduplicates and merges Vista + PostgreSQL results
5. **Display:** User sees complete timeline (historical + today's data)

**Performance Controls:**

- **Site Selection Policy:** Default to top 3 most recent treating facilities (not all 140+ sites)
- **Per-Domain Limits:** Vitals (2 sites), Allergies (5 sites), Medications (3 sites)
- **Time Budget:** 15 second maximum, show partial results if incomplete
- **User Control:** Explicit refresh action required (no automatic polling)

#### User Benefits

**For Clinicians:**
- ✅ **Faster Default Experience:** Sub-2-second page loads from PostgreSQL (vs. JLV's ~20 seconds)
- ✅ **Fresher Data When Needed:** Access to today's data with a single button click
- ✅ **Complete Timeline:** Seamless view of historical + current data
- ✅ **No Workflow Disruption:** Familiar "refresh" pattern from current EHR systems

**For VA IT Operations:**
- ✅ **Reduced Network Load:** 95% of queries use local PostgreSQL, not 140+ RPC calls
- ✅ **Better Scalability:** Caching + controlled refresh vs. constant real-time queries
- ✅ **Improved Reliability:** PostgreSQL uptime >> distributed VistA RPC availability

**Strategic Advantage Over Current JLV:**

med-z1 delivers both **speed** (fast PostgreSQL queries) AND **freshness** (on-demand Vista queries), solving the performance vs. currency dilemma that plagues current JLV.

#### Architecture Overview

**Implementation:**
- Separate FastAPI service running on port 8003
- HTTP-based API simulating VistA Remote Procedure Call (RPC) interface
- Multi-site support with automatic ICN→DFN (site-specific patient ID) resolution
- VistA-compatible response format (caret-delimited, FileMan dates)

**Integration with med-z1:**
- med-z1 web app calls Vista RPC Broker service via HTTP
- User-triggered "Refresh from VistA" buttons in domain pages (Vitals, Medications, Allergies, etc.)
- Transparent merge/deduplication of PostgreSQL + Vista results
- Clear visual indicators showing data freshness and completeness

**Data Flow:**
```
User clicks "Refresh from VistA"
       ↓
med-z1 app → Vista RPC Broker Service → Simulated VistA sites (JSON data)
       ↓
Vista returns T-0 data (caret-delimited VistA format)
       ↓
med-z1 merges with PostgreSQL T-1 data
       ↓
User sees complete timeline (deduplicated, sorted)
```

**Development Environment:**

In development, the Vista RPC Broker uses **JSON-based patient data files** that simulate VistA responses. In production, it would connect to real VistA systems via broker connections.

#### Implementation Status & Roadmap

**✅ Phases 1-5 Complete (January 13, 2026):**

**Phase 1: Infrastructure Foundation**
- DataLoader, RPCHandler framework, RPCRegistry
- Multi-site support (3 sites: 200 ALEXANDRIA, 500 ANCHORAGE, 630 PALO ALTO)
- First working RPC handler (ORWPT PTINQ - Patient Inquiry)
- VistA format conversion utilities (M-Serializer)
- Complete FastAPI HTTP service with 82 passing tests

**Phase 2: Multi-Site Support & Client**
- `app/services/vista_client.py` - HTTP client with intelligent site selection
- Domain-specific site limits (vitals=2, allergies=3-5, medications=3, encounters=3)
- T-notation date parsing (T-0, T-7, T-30, etc.)
- 42 unit tests for vista_client (100% pass rate)

**Phase 3: Vitals Domain Integration**
- GMV LATEST VM RPC handler
- Merge/dedupe with PostgreSQL data
- "Refresh VistA" button in Vitals page
- Session-based caching (30-min TTL)

**Phase 4: Encounters & Allergies Domains**
- ORWCV ADMISSIONS RPC (inpatient encounters, 90-day lookback)
- ORQQAL LIST RPC (patient allergies, safety-critical coverage)
- HTMX + OOB swaps pattern established

**Phase 5: Medications Domain** (January 13, 2026)
- ORWPS COVER RPC (active outpatient medications)
- 69 mock medications across 3 sites
- Session cache integration for filter persistence
- Status filter logic refined (inpatient always included)
- Merge/dedupe with canonical key: `{site}:{prescription_number}`

**📊 Current Status:**
- ✅ **4 clinical domains** with full "Refresh VistA" functionality operational
- ✅ **Domains Complete:** Vitals (GMV), Encounters (ORWCV), Allergies (ORQQAL), Medications (ORWPS)
- ✅ **Total test coverage:** ~168 tests (94 Vista service + 42 VistaClient + 32 domain integration)
- 🎯 **27% of planned domains complete** (4 of ~15)

**📋 Future Phases (Planned):**
- **Phase 6:** Laboratory Results domain (ORQORB namespace)
- **Phase 7:** Clinical Notes domain (TIU namespace)
- **Phase 8:** Additional domains as prioritized (Problems, Orders, Procedures, Imaging)

**Technical Documentation:**

> **For detailed Vista RPC Broker technical design, RPC specifications, merge/deduplication algorithms, and implementation patterns, see:**
> - `docs/spec/vista-rpc-broker-design.md` (v2.0) - Complete technical specification ✅ **Updated for Phase 5**
> - `docs/spec/med-z1-implementation-roadmap.md` Section 11.5 - Implementation status and phases
> - `vista/README.md` - Developer/operator guide

**Configuration:**
- Vista service URL: `VISTA_SERVICE_URL = "http://localhost:8003"` (dev environment)
- Site registry: `vista/app/config/sites.json` ✅
- Patient data: `mock/shared/patient_registry.json`

---

## 5. Project Structure

**High-Level Organization:**

```text
med-z1/
  app/                 # FastAPI + HTMX web application (port 8000)
  ccow/                # CCOW Context Vault service (port 8001)
  vista/               # Vista RPC Broker simulator (port 8003)
  etl/                 # ETL scripts (Bronze/Silver/Gold transformations)
  ai/                  # AI/ML components (LangGraph agent, tools, prompts)
  lake/                # MinIO client utilities
  db/                  # PostgreSQL DDL scripts
  mock/                # Mock CDW (SQL Server schemas and data)
  docs/                # Design specifications and plans
  scripts/             # Testing, debugging, and utility scripts
  notebook/            # Jupyter notebooks for data exploration

  .venv/               # Shared Python environment
  .env                 # Environment configuration
  config.py            # Centralized configuration
  requirements.txt     # Python dependencies
  docker-compose.yaml  # Docker services (SQL Server, MinIO, PostgreSQL)
  README.md            # Project overview and setup instructions
  CLAUDE.md            # Claude Code guidance and project conventions
  pytest.ini           # Test framework configuration
```

**Configuration Philosophy:**
- Single shared Python environment (`.venv/`)
- Single shared `.env` file at project root
- Single shared `config.py` module for all subsystems

> **For detailed project structure, file locations, and implementation status, see `docs/spec/med-z1-implementation-roadmap.md` Section 12 and `CLAUDE.md`.**

---

## 6. Development Phases & Current Status

### 6.1 Current Implementation Status

Implementation status is maintained in:
- `docs/spec/implementation-status.md` (single source of truth)

Use this plan document for product strategy and phase planning. Use the status document for current implementation counts and completion state.

### 6.2 Technology Decisions Made

**Database Connectivity:**
- ✅ SQLAlchemy 2.0 + pyodbc (chosen for reliability)
- ❌ ConnectorX (rejected due to Arrow compatibility issues with Polars 1.x)

**Data Processing:**
- ✅ Polars 1.18 (API differences from 0.x documented)
- ✅ SQLAlchemy for database connections
- ✅ boto3 for MinIO (S3-compatible)

**Serving Database:**
- ✅ PostgreSQL 16 (chosen over SQL Server alternative)

**ETL Patterns:**
- ✅ Direct Python module execution (`python -m etl.bronze_patient`)
- Future: Consider Prefect/Airflow for orchestration

---

## 7. Data Architecture - Medallion Pattern (Conceptual)

med-z1 implements a **medallion data architecture** with three layers of increasing refinement:

**Bronze Layer (Raw Data):**
- Extracts raw data from mock CDW with minimal transformation
- Preserves source semantics and lineage
- Stored as Parquet in MinIO (`lake/bronze/`)
- Includes metadata: `SourceSystem`, `SourceDatabase`, `LoadDateTime`

**Silver Layer (Cleaned & Harmonized):**
- Cleans and standardizes data across CDWWork and CDWWork2
- Harmonizes patient identity across systems (ICN/PatientKey)
- Consistent schemas across clinical domains
- Stored as Parquet in MinIO (`lake/silver/`)

**Gold Layer (Query-Optimized):**
- Curated, query-friendly views for UI consumption
- Optimized for per-patient and per-domain queries
- Stored as Parquet in MinIO (`lake/gold/`)
- Loaded into PostgreSQL serving database for low-latency access

**Data Flow:**
```
Mock CDW (SQL Server) → Bronze → Silver → Gold → PostgreSQL Serving DB → FastAPI UI
```

> **For detailed Gold schemas, ETL implementation patterns, and code examples, see `docs/spec/med-z1-implementation-roadmap.md` Section 9 and Section 11.**

---

## 8. Security, Privacy & Compliance (Conceptual)

* **Local development:**

  * Only synthetic, non-PHI/PII data.
  * Local containers only (no external exposure).

* **Future real-data environments:**

  * PHI/PII handling per VA standards.
  * Authentication/authorization (e.g., SSO, RBAC).
  * Comprehensive audit logging of user access to patient data.
  * Environment separation: dev, test, prod with distinct CDW endpoints and credentials.

* **AI Safety:**

  * Guardrails against hallucinations in clinical summaries.
  * Clear UI labels indicating AI-generated content.
  * Never override authoritative clinical data; AI is advisory only.

---

## 9. Development Roadmap & Milestones

### 9.1 Phase 0 – Environment & Skeleton (1–2 weeks)

* Set up the repo with:

  * Basic directory structure (`docs/`, `app/`, `etl/`, `mock/`, `lake/`, etc.).
  * `docs/med-z1-plan.md` as the living plan document (Document version v1 and future revisions).
* Create Python 3.11 venv.
* Implement FastAPI + Jinja2 + one HTMX interaction in `app/`.
* Stand up Docker compose for SQL Server (mock CDW), MinIO, PostgreSQL.

### 9.2 Phase 1 – Mock CDW & Bronze Extraction (2–3 weeks)

* Populate `mock/sql-server/cdwwork/create` and `cdwwork1/create` with DDL for key domains (Patients, Meds, Encounters, Flags).
* Populate `mock/sql-server/cdwwork/insert` and `cdwwork1/insert` with data-load scripts for synthetic data.
* Implement Bronze extract scripts in `etl/` (starting with Patients + Medications).

### 9.3 Phase 2 – Silver & Gold Transformations in the Lake (3–5 weeks)

* Implement Silver and Gold transformations for Patients, Meds, Encounters, Labs (when added), Problems, Flags.
* Produce `gold_patient_summary` and `gold_patient_timeline_events`.

### 9.4 Phase 3 – Serving DB Loading & Basic UI (3–4 weeks)

* Load Gold into the serving DB.
* Build patient search, patient overview, and at least one domain view (e.g., Medications) with the side-nav layout.
* **Implement CCOW Context Management service:**
  * Stand up CCOW FastAPI service on port 8001.
  * Ensure CCOW vault is accessible at `http://localhost:8001`.
  * Test CCOW API endpoints independently (`GET`, `PUT`, `DELETE /ccow/active-patient`).
* **Integrate CCOW with med-z1 web app:**
  * **On application startup/page load:**
    * Query CCOW vault (`GET /ccow/active-patient`) to retrieve current patient context.
    * If patient context exists (ICN returned):
      * Fetch patient demographics from serving DB using ICN.
      * Populate patient header with: name, ICN, last 4 SSN, DOB, age, sex, primary facility.
    * If no patient context exists (404 response):
      * Display "No patient selected" message in header.
  * **Implement patient search UI in header:**
    * Search bar/button in header area (always accessible).
    * Search form accepts: name, ICN, EDIPI.
    * Query serving DB for matching patients.
    * Display search results with key demographics and identifiers.
  * **Implement patient selection and CCOW context setting:**
    * User selects patient from search results.
    * User clicks "Set Context" button (explicit action required).
    * App makes `PUT /ccow/active-patient` with patient's ICN and `set_by: "med-z1"`.
    * On successful vault update:
      * Fetch patient demographics from serving DB.
      * Refresh patient header with selected patient information.
      * Navigate to Patient Overview page (or stay on current page with updated context).
  * **Configuration:**
    * Add `CCOW_BASE_URL=http://localhost:8001` to `.env`.
    * Import from `config.py` in app code.
  * **Test end-to-end workflow:**
    * Test app startup with no CCOW context (verify "No patient selected" state).
    * Test patient search and selection workflow.
    * Test "Set Context" action and header refresh.
    * Test app restart with existing CCOW context (verify patient header populates correctly).

### 9.5 Phase 4-6 – AI-Assisted Features ✅ **COMPLETE** (January 20, 2026)

**Phase 4: Core AI Tools** (January 3, 2026)
* ✅ Implemented chart overview summarization using Gold data + clinical notes
* ✅ Implemented DDI risk analysis based on Gold medications with severity assessment
* ✅ Implemented patient flag–aware risk messaging
* ✅ Deployed LangGraph conversational AI interface at `/insight`
* ✅ 4 operational AI tools with OpenAI GPT-4 Turbo integration

**Phase 5: Clinical Notes Integration** (January 4, 2026)
* ✅ Integrated clinical notes data with AI patient summaries
* ✅ Implemented `get_clinical_notes_summary` tool with type/date filtering
* ✅ 500-char note previews for context optimization

**Phase 6: Conversation Memory** (January 20, 2026)
* ✅ PostgreSQL checkpointer with LangGraph AsyncPostgresSaver
* ✅ User-scoped thread IDs (`{user_id}_{patient_icn}`)
* ✅ Cross-session conversation persistence
* ✅ Clear chat history functionality
* ✅ System message optimization (first-message-only injection)

**See:** `docs/spec/ai-insight-design.md` (v2.4) for complete implementation details.

### 9.6 Phase 5 – Hardening, Observability & UX Iteration (Ongoing)

* Add logging, metrics, performance tuning.
* Iterate on UX and accessibility.
* Add tests and CI as the project matures.

---

## 10. Assumptions & Open Questions

* Mock CDW schemas will remain reasonably stable once the initial set is defined, with incremental additions over time.
* MinIO on local macOS is adequate to simulate ADLS Gen2/S3 patterns for early medallion work.
* PostgreSQL is available and acceptable for serving DB tasks; if not, SQL Server can be used.

**Resolved Questions:**

* ✅ AI model selection: OpenAI GPT-4 Turbo chosen for clinical decision support (chart overview, DDI risk, clinical notes analysis)
* ✅ Clinical notes integration: Completed with 500-char previews for context optimization
* ✅ AI framework selection: LangGraph chosen for agent workflow orchestration
* ✅ Conversation memory strategy: PostgreSQL checkpointer with user-scoped threads (Phase 6 complete)
* ✅ Vista RPC integration pattern: Established with 4 domains operational (Vitals, Encounters, Allergies, Medications)

**Open Questions (to be refined over time):**

* Exact schema design for CDWWork2 (how much to diverge from CDWWork to best exercise Silver harmonization).
* When and how to introduce a proper orchestration layer (e.g., Prefect, Airflow, or ADF) for ETL workflows.
* Vector store implementation timeline and approach (pgvector vs. dedicated vector DB).
