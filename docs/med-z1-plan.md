# med-z1 – Product & Technical Development Plan

December 7, 2025 • Document version v1.1 (updated with CCOW integration requirements)

## 1. Product Vision

**med-z1** is a next-generation longitudinal health record viewer for the Department of Veterans Affairs, designed to:

- Replace and modernize the current **Joint Longitudinal Viewer (JLV)**.
- Provide fast, consistent access to patient data by sourcing from the **VA Corporate Data Warehouse (CDW)** instead of RPC calls to 140+ VistA instances.
- Seamlessly blend **legacy VistA data** (CDWWork, representing VistA) and **new EHR data** (CDWWork1, representing Oracle Health) in the mock environment, mirroring real CDWWORK/CDWWORK2.
- Introduce **AI-assisted** and **agentic AI** capabilities to help busy clinicians quickly understand a patient’s story, key risks, and gaps in care.

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
    - `CDWWork1` (mock new EHR data; conceptually maps to real CDWWORK2).
  - Both populated with **synthetic, non-PHI/PII data**.

- **Core medallion pipeline:** **Parquet/Delta** files stored in **MinIO** (S3/ADLS Gen2 compatible) on the local Mac.

- **Serving database for the UI:** A small relational DB (preferably **PostgreSQL**, with **SQL Server** as an alternative) to support low-latency per-patient queries.

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

- **Admissions / Encounters** (inpatient and outpatient)
- **Allergies**
- **Demographics**
- **Orders**
- **Problems / Diagnoses**
- **Medications**
- **Laboratory Results**
- **Notes / Documents**
- **Radiology / Imaging**
- **Vitals**
- **Patient Flags**

**DoD-specific views** and data (e.g., CHCS/AHLTA, purely DoD-only domains) are explicitly **out of scope** for early versions. The focus is **VA-internal data** sourced from CDW.

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
     - User enters search criteria (name, SSN, ICN, EDIPI) via header search.
     - Search results display matching patients with key identifiers.
     - User selects a patient from results.
     - User explicitly clicks "Set Context" or similar action to update CCOW vault.
     - App refreshes header to display selected patient demographics.
   - CCOW context is checked **only on initial page load** (no periodic polling in Phase 1).

2. **Patient Longitudinal Summary**
   - Integrated timeline of encounters, problems, medications, labs, and procedures across VistA (from `CDWWork`) and the new EHR (from `CDWWork1`).
   - Display clear source provenance (facility, system, time).

3. **Domain-Specific Views**
   - For each domain (e.g., Medications, Labs, Problems, Notes, Imaging, Vitals, Orders, Admissions), provide:
     - Filterable, sortable tables.
     - Consistent display of key fields and source system.
     - Ability to focus on recent vs. historical data.

4. **Patient Flags & Risk Indicators**
   - Retrieve and display Patient Flags from CDW.
   - Use flags as part of the risk and summary story (Phase 2+).

5. **AI-Assisted Chart Overview (Phase 2+)**
   - Natural-language **chart overview**:
     - Major chronic conditions.
     - Recent admissions/ED visits.
     - Key labs and trends.
     - Notable flags and orders.

6. **AI-Supported Medication Safety (Phase 2+)**
   - Identify **drug-drug interaction (DDI) risk** for the current medication list.
   - Highlight combinations that may warrant pharmacist or clinician review.
   - Eventually integrate multiple sources (e.g., CDW meds + external DDI knowledge base).

7. **Future AI Use of Patient Flags**
   - Incorporate Patient Flag data into risk assessment:
     - Behavioral flags, safety alerts, suicide risk, etc. (as appropriate).
   - Make AI summaries aware of patient flags and incorporate them into the narrative.

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
    - Search by: name, SSN, ICN, EDIPI.
    - Search results displayed inline or as dropdown/overlay.
    - User selects patient from results, then explicitly clicks "Set Context" to update CCOW vault.
  - **On initial page load**:
    - App queries CCOW vault (`GET /ccow/active-patient`).
    - If patient context exists, fetch patient demographics from serving DB and populate header.
    - If no context exists, display "No patient selected" state.

- A **left-hand side navigation bar**:
  - Collapsible (e.g., hamburger icon at top-left).
  - Contains navigation links for:
    - Patient Overview.
    - Admissions/Encounters.
    - Problems.
    - Medications.
    - Labs.
    - Notes/Documents.
    - Imaging.
    - Vitals.
    - Orders.
    - Patient Flags.
    - (Future) AI/Insights.

- A **main content area on the right**:
  - Scrollable main content section below patient header.

The design will favor a **single primary page per patient** with:

- A **Patient Overview** page showing:
  - Demographics & identifiers (also shown in header).
  - Key problems and flags.
  - Brief AI-generated overview (Phase 2+).
  - A longitudinal timeline visualization (Phase 2 or 3).

Domain-specific pages are accessible from the side navigation, each focused and uncluttered.

### 3.2 Patient Search & Identity Resolution

**User experience:**

- Entry point is a **patient search UI in the header** (always accessible).
- User can search by:
  - Patient **Name** (with optional facility filter).
  - **SSN** (full or partial).
  - **ICN** (Integrated Care Number).
  - **EDIPI** (DoD ID).
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

---

## 4. Technology Stack

### 4.1 Core Languages & Frameworks

- **Language:** Python 3.11 (for maximum compatibility with dependencies)
- **Backend Web Framework:** FastAPI
- **Templating:** Jinja2
- **Interactive UX:** HTMX

**Rationale:** Python 3.11 is chosen as the baseline for med-z1 because it offers a strong balance of performance and ecosystem stability. Many core dependencies for this project—data/ML libraries, database drivers, and AI tooling—have mature, well-tested support for 3.11, while newer Python versions can still lag slightly in compatible binary wheels and integrations. Standardizing on 3.11 reduces friction when installing and upgrading dependencies, while still benefiting from the “Faster CPython” improvements over older versions (3.9/3.10). Future upgrades to 3.12+ can be evaluated in a separate experimental environment once the full stack is known to be compatible.

### 4.2 Data & Medallion

- **Source DB (development):**  
  - Mock CDW subsystem:
    - SQL Server 2019 Docker container.
    - Two databases:
      - `CDWWork` for VistA-like data (mock of real CDWWORK).
      - `CDWWork1` for new EHR–like data (mock of real CDWWORK2).
    - Schemas and tables named to closely resemble real CDW patterns.
    - Synthetic sample data only.

- **Data Lake Storage:** MinIO (S3/ADLS Gen2 compatible).
- **File Formats:** Parquet (Bronze, Silver, Gold), possible Delta format later.
- **Data Processing:** 
  - Polars and/or Pandas.
  - DuckDB for querying Parquet/MinIO efficiently.

- **ETL Orchestration (initial):**
  - Python scripts under `etl/` (with file names conveying Bronze/Silver/Gold roles).
  - Option to move to Prefect, Airflow, or Azure Data Factory later.

### 4.3 Serving Database

- **Preferred:** PostgreSQL
  - Tables for patient-centric and domain-centric views built from Gold Parquet.
  - Optional extension: **pgvector** for embeddings.

- **Alternate:** SQL Server
  - Same serving schema patterns; uses existing T-SQL expertise.

FastAPI will primarily talk to the serving DB for interactive UI work and may call specialized services that read from Gold Parquet for more complex analytics.

### 4.4 Mock CDW Subsystem

- **Container:** Microsoft SQL Server 2019 image (Docker).
- **Databases:**
  - `CDWWork` – mock VistA data.
  - `CDWWork1` – mock new EHR data.
- **Schemas:**
  - `Dim`, `SPatient`, `SStaff`, `Inpat`, `RxOut`, `BCMA`, and others as needed (e.g., Labs, Vitals, Orders, Flags).

- **Artifacts & folder organization:**

```text
  mock/
    sql-server/
      cdwwork/
        create/     # CREATE DATABASE, schemas, tables, indexes for CDWWork
        insert/     # INSERT / BULK INSERT scripts for CDWWork synthetic data
      cdwwork1/
        create/     # CREATE DATABASE, schemas, tables, indexes for CDWWork1
        insert/     # INSERT / BULK INSERT scripts for CDWWork1 synthetic data
```

* This keeps the structure lean and focused on SQL Server schema and data setup needed for the mock environment.

* **Key conventions:**

  * Each core table has a `*SID` column (e.g., `PatientSID`, `InpatientSID`, `RxOutpatSID`, `BCMADispensedDrugSID`, `StateSID`).
  * These `*SID` columns are treated as **surrogate primary keys**, typically with **clustered primary key constraints and supporting nonclustered indexes** on frequently filtered columns (e.g., `Sta3n`, `PatientSID`, `IssueDateTime`).
  * Foreign key constraints may be **lightweight or omitted** in the mock environment to keep ETL simple and fast, but relationship patterns will be followed consistently.

* **Usage:**

  * Acts as the **source-of-truth** for development and testing.
  * Provides stable, version-controlled "fixtures" for ETL and UI tests.
  * CDWWork1 will mirror CDWWork conceptually but may intentionally differ in column naming and structure for some tables to exercise Silver-layer harmonization logic.

### 4.5 CCOW Context Management

* **Purpose:**

  * Implement a simplified version of the HL7 CCOW (Clinical Context Object Workgroup) standard for **patient context synchronization** across applications.
  * Provide a **single source of truth** for the currently active patient context, enabling med-z1 and other clinical applications to stay synchronized during clinical workflows.

* **Implementation:**

  * **FastAPI service** running on port 8001 (separate from main app on port 8000).
  * **Thread-safe in-memory vault** (`vault.py`) for managing current patient context and change history.
  * **REST API endpoints** for getting, setting, and clearing active patient context.
  * Pydantic models for request/response validation.

* **Scope (Development/Testing):**

  * Mock/development implementation to demonstrate CCOW-like context synchronization patterns.
  * Support local development and testing scenarios.
  * Foundation for future production CCOW integration with real clinical applications.

* **Explicitly Out of Scope (Phase 1):**

  * Full CCOW standard compliance.
  * Authentication/authorization.
  * Persistent storage (vault resets on service restart).
  * Multi-user or multi-session contexts.
  * Real-time push notifications (WebSocket/SSE).

* **Integration Points:**

  * med-z1 web app (`app/`) will call CCOW service when user selects a patient.
  * Future integration: external clinical applications (CPRS, imaging viewers, pharmacy systems) can query/set context.
  * Configuration: `CCOW_BASE_URL = "http://localhost:8001"` in `.env`.

### 4.6 AI & Agentic

* **LLM/AI Access:**

  * OpenAI-compatible client or other cloud/local model APIs.

* **Libraries:**

  * `transformers`, `openai`-style clients.
  * `sentence-transformers` (or equivalent) for embeddings.
  * `langchain` / `langgraph` for agent workflows (optional but likely).

* **Primary AI Use Cases (early):**

  * **Chart overview** summarization.
  * **Drug-drug interaction risk** assessment based on med list and possibly lab/flag context.
  * Early use of **Patient Flag data** in risk narratives.

* **Vector Store:**

  * Initially: local (Chroma/FAISS).
  * Later: **pgvector** in PostgreSQL if desired.

### 4.7 Tooling & Dev Experience

* **IDE:** VS Code (Python, Jupyter, Docker, SQL extensions).
* **Environment:** `venv` + `.env` with python-dotenv.
* **Testing:** `pytest`.
* **Linting/Formatting:** `ruff`, `black`, `mypy` (optional).
* **Containers:** Docker/Podman for SQL Server, MinIO, PostgreSQL, optionally FastAPI app.

---

## 5. High-Level Project Layout

The initial project structure is:

```text
med-z1/
  docs/
    med-z1-plan.md   # This plan (Document version v1 and future revisions)
    vision.md        # Problem statement, user personas, key user stories
    architecture.md  # Diagrams and architecture decisions
    ai-design.md     # AI/ML, RAG, DDI use-case designs

  app/               # FastAPI + HTMX + Jinja2 application code
    main.py
    templates/
    static/
    README.md        # Developer setup and app-specific notes

  ccow/              # CCOW Context Management Vault service
    main.py          # FastAPI service for CCOW context synchronization
    vault.py         # Thread-safe in-memory context vault
    models.py        # Pydantic models for context requests/responses
    README.md        # CCOW setup and usage instructions

  etl/               # ETL scripts implementing Bronze/Silver/Gold logic
    README.md        # Developer setup instructions and ETL/data-specific notes

  lake/              # Configs/utilities for MinIO, Parquet access
  mock/              # Mock data subsystem (mocks CDW, SDP, DDI, other)
    sql-server/      # Microsoft SQL Server
      cdwwork/
        create/      # CREATE DATABASE, schemas, tables, indexes for CDWWork
        insert/      # INSERT / BULK INSERT scripts for CDWWork synthetic data
      cdwwork1/
        create/      # CREATE DATABASE, schemas, tables, indexes for CDWWork1
        insert/      # INSERT / BULK INSERT scripts for CDWWork1 synthetic data
  ai/                # AI/ML & agentic components (create when needed)
    README.md        #
  db/                # Serving DB DDL, migrations, etc. (create when needed)
  tests/             # Unit/integration tests (as you add them)
```

Note: This project will use a single, shared Python environment (`.venv/`), a single, shared python-dotenv file (`.env`), and a single, shared configuration module (`config.py). These three files are located in the project root folder.

### 5.3 Mock Schema Design – CDWWork (VistA-like)

Representative starter tables (inspired by your existing DDL):

* **Database:** `CDWWork`
* **Schemas & Tables:**

  * `Dim.Sta3n`
  * `Dim.State`
  * `SPatient.SPatient`
  * `SPatient.SPatientAddress`
  * `SStaff.SStaff`
  * `Inpat.Inpatient`
  * `RxOut.RxOutpat`
  * `BCMA.BCMADispensedDrug`
  * Later: `LabChem.LabChem`, `LabMicro.LabMicro`, `Vital.Vital`, `Orders.Orders`, `Flag.Flag`, etc.

**Key patterns:**

* `*SID` columns as surrogate primary keys.
* `Sta3n` indicating facility/station.
* Separate dimension tables (e.g., `Dim.Sta3n`, `Dim.State`) referenced via SIDs.

### 5.4 Mock Schema Design – CDWWork1 (Oracle Health–like)

**Goal:** Mirror CDWWork conceptually but:

* Use **slightly different naming conventions** to exercise Silver harmonization logic.
* Optionally represent a smaller subset of facilities and patients.

**Examples:**

* `SPatient1.Patient` instead of `SPatient.SPatient`.
* `Inpat1.Encounter` instead of `Inpat.Inpatient`.
* Medication tables with similar content but different column names or structure.

**Design choices:**

* Maintain the `*SID` pattern (e.g., `PatientSID1`, `EncounterSID1`) to keep joins straightforward.
* Use overlapping identifiers (e.g., ICN, EDIPI) so Silver can unify patient identity across CDWWork and CDWWork1.

### 5.5 Serving Database Design (Conceptual)

The serving DB (PostgreSQL preferred) will expose:

* **patient**

  * `patient_id` (internal key)
  * `icn`
  * `name`, `dob`, `sex`
  * `primary_facility`, etc.

* **patient_timeline_event**

  * `event_id`
  * `patient_id`
  * `event_type` (admission, discharge, lab, med, note, imaging, vitals, flag)
  * `event_timestamp`
  * `facility`
  * `source_system` (VistA, new EHR)
  * `summary` (short description)
  * `details_json` (optional payload)

* **patient_medication**

  * `med_id`
  * `patient_id`
  * `drug_name`
  * `dose`, `route`, `frequency`
  * `start_date`, `stop_date`
  * `ordering_provider`
  * `source_system`

* **patient_lab_result**

  * `lab_id`
  * `patient_id`
  * `test_name`
  * `specimen`
  * `result_value`
  * `unit`
  * `reference_range`
  * `result_datetime`
  * `abnormal_flag`

* **patient_problem**, **patient_flag**, **patient_order**, **patient_vital** tables with similar patterns.

This database is used by the FastAPI/HTMX app to satisfy per-patient and per-domain queries with minimal joins and predictable performance.

### 5.6 Mock Data Generation

* **Approach:**

  * Use Python scripts to generate CSVs for each table.
  * Load into SQL Server via:

    * `BULK INSERT`,
    * `bcp`, or
    * SQLAlchemy-based loaders.

* **Coverage:**

  * Multiple patients across multiple sites (`Sta3n`).
  * Mixture of chronic and acute conditions.
  * Sufficient volume to test partitioning and performance (but controllable for local development).

---

## 6. Data & Medallion Design (Conceptual)

### 6.1 Bronze Layer (MinIO – `med-z1-bronze`)

**Goal:** Land raw mock CDW data in Parquet, preserving source semantics and lineage.

**Design:**

* Extract from `CDWWork` and `CDWWork1` with minimal transformation:

  * `bronze_patient`
  * `bronze_patient_address`
  * `bronze_encounter`
  * `bronze_medication_outpat`
  * `bronze_medication_bcma`
  * `bronze_lab_result` (when added)
  * `bronze_vital`
  * `bronze_order`
  * `bronze_patient_flag`
  * `bronze_dim_sta3n`
  * `bronze_dim_state`

* Store in MinIO as Parquet, partitioned by key dimensions (e.g., `sta3n`, `year`, `month`).

* Add metadata such as `SourceSystem`, `SourceDatabase`, and `LoadDateTime`.

### 6.2 Silver Layer (MinIO – `med-z1-silver`)

* Clean and standardize entities across CDWWork and CDWWork1.
* Harmonize patient, meds, encounters, labs, problems, vitals, orders, and flags into consistent schemas keyed by ICN/`PatientKey`.

### 6.3 Gold Layer (MinIO – `med-z1-gold`)

* Build curated, query-friendly views:

  * `gold_patient_summary`
  * `gold_patient_timeline_events`
  * `gold_patient_medications`
  * `gold_lab_trends`

Gold remains in Parquet/Delta but is also used to populate the serving DB.

---

## 7. Security, Privacy & Compliance (Conceptual)

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

## 8. Development Roadmap & Milestones

### 8.1 Phase 0 – Environment & Skeleton (1–2 weeks)

* Set up the repo with:

  * Basic directory structure (`docs/`, `app/`, `etl/`, `mock/`, `lake/`, etc.).
  * `docs/med-z1-plan.md` as the living plan document (Document version v1 and future revisions).
* Create Python 3.11 venv.
* Implement FastAPI + Jinja2 + one HTMX interaction in `app/`.
* Stand up Docker compose for SQL Server (mock CDW), MinIO, PostgreSQL.

### 8.2 Phase 1 – Mock CDW & Bronze Extraction (2–3 weeks)

* Populate `mock/sql-server/cdwwork/create` and `cdwwork1/create` with DDL for key domains (Patients, Meds, Encounters, Flags).
* Populate `mock/sql-server/cdwwork/insert` and `cdwwork1/insert` with data-load scripts for synthetic data.
* Implement Bronze extract scripts in `etl/` (starting with Patients + Medications).

### 8.3 Phase 2 – Silver & Gold Transformations in the Lake (3–5 weeks)

* Implement Silver and Gold transformations for Patients, Meds, Encounters, Labs (when added), Problems, Flags.
* Produce `gold_patient_summary` and `gold_patient_timeline_events`.

### 8.4 Phase 3 – Serving DB Loading & Basic UI (3–4 weeks)

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
    * Search form accepts: name, SSN, ICN, EDIPI.
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

### 8.5 Phase 4 – AI-Assisted Features (Experimental) (3–6 weeks)

* Implement chart overview summarization using Gold data.
* Prototype DDI risk analysis based on Gold medications.
* Experiment with patient flag–aware risk messaging.

### 8.6 Phase 5 – Hardening, Observability & UX Iteration (Ongoing)

* Add logging, metrics, performance tuning.
* Iterate on UX and accessibility.
* Add tests and CI as the project matures.

---

## 9. Assumptions & Open Questions

* Mock CDW schemas will remain reasonably stable once the initial set is defined, with incremental additions over time.
* MinIO on local macOS is adequate to simulate ADLS Gen2/S3 patterns for early medallion work.
* PostgreSQL is available and acceptable for serving DB tasks; if not, SQL Server can be used.

**Open questions (to be refined over time):**

* Exact schema design for CDWWork1 (how much to diverge from CDWWork to best exercise Silver harmonization).
* Which AI model(s) to use for:

  * Chart overview summarization.
  * DDI risk commentary.
* When and how to introduce a proper orchestration layer (e.g., Prefect, Airflow, or ADF).

---

## 10. Documentation & Learning Artifacts

Maintain documentation as part of the med-z1 repo under `docs/`:  

* `docs/med-z1-plan.md`

  * Contains this plan (Document version v1 and future revisions).

* `docs/vision.md` (optional, to be created)

  * Refined problem statement, target users, and user stories.

* `docs/architecture.md` (optional, to be created)

  * Diagrams and explanations of:

    * High-level architecture.
    * Mock CDW schema relationships.
    * Medallion data flows.
    * Serving layer design.

* `docs/ai-design.md` (optional, to be created)

  * Notes on models, prompts, RAG design, DDI risk logic, and agent workflows.

---

## 11. Next Steps (Actionable)

1. Ensure `docs/med-z1-plan.md` (Document version v1) is saved as the current baseline plan and update it incrementally as the design evolves.

2. Ensure your existing T-SQL DDL for `CDWWork` aligns with the modeling conventions above (SIDs as PKs where appropriate, index strategy).

3. Begin designing `CDWWork1`:

   * Mirror a subset of `CDWWork` tables (Patients, Inpatient, RxOut, BCMA, etc.).
   * Introduce intentional structural differences to support Silver harmonization.

4. Implement Phase 0 if not already done:

   * Python 3.11 venv.
   * Basic FastAPI app + Jinja2 + one HTMX interaction.
   * Docker compose with SQL Server (`CDWWork`/`CDWWork1`), MinIO, and PostgreSQL.

5. Start Phase 1 Bronze extraction:

   * Implement minimal Bronze extractors for Patients and Medications from both `CDWWork` and `CDWWork1`.
