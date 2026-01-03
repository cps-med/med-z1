# app

This is the initial FastAPI + HTMX + Jinja UI shell for med-z1. Current pages are demo-only (overview, HTMX basics, timer) and will be gradually replaced with JLV-like patient views.

## Overview

**app** is a subsystem of the med-z1 application that provides a web-based interface for exploring and understanding data stored in the application's data mart. It is built using a modern Python stack centered on FastAPI, HTMX, and Jinja2 templates, with support for connecting to Microsoft SQL Server and other backend data sources.

The app subsystem is developed with **Python + FastAPI + HTMX + Jinja2**, using traditional server-side rendering (SSR) enhanced with lightweight, dynamic interactions powered by HTMX. The application uses standard web technologies—HTML, CSS, and JavaScript—along with clean, component-driven templates for consistent UI design.

## Dependencies

From project root folder:
```
pip install fastapi "uvicorn[standard]" jinja2 python-multipart
```

Then:
```
cd med-z1
uvicorn app.main:app --reload
```

---

## Routing Architecture

### Quick Reference: When to Use Which Pattern

**Pattern A: Add routes to `app/routes/patient.py`**
- ✅ Domain only needs JSON API endpoints
- ✅ Domain uses modal overlays (no full page)
- ✅ Domain in early implementation (API-first)
- Examples: Flags, Allergies

**Pattern B: Create dedicated `app/routes/<domain>.py`**
- ✅ Domain has full page view at `/patient/{icn}/<domain>`
- ✅ Domain needs complex filtering/sorting/charting
- ✅ Domain has multiple page routes
- Examples: Vitals

### Code Examples

#### Pattern A: Routes in patient.py
```python
# app/routes/patient.py
from app.db.patient_allergies import get_patient_allergies

@router.get("/{icn}/allergies")
async def get_patient_allergies_json(icn: str):
    allergies = get_patient_allergies(icn)
    return {"patient_icn": icn, "allergies": allergies}
```

#### Pattern B: Dedicated Router File
```python
# app/routes/vitals.py

# API router
router = APIRouter(prefix="/api/patient", tags=["vitals"])

@router.get("/{icn}/vitals")
async def get_patient_vitals_endpoint(icn: str):
    vitals = get_patient_vitals(icn)
    return {"patient_icn": icn, "vitals": vitals}

# Page router (for full pages)
page_router = APIRouter(tags=["vitals-pages"])

@page_router.get("/patient/{icn}/vitals")
async def get_vitals_page(request: Request, icn: str):
    vitals = get_patient_vitals(icn)
    return templates.TemplateResponse("patient_vitals.html", {...})
```

**For detailed architecture decisions and rationale, see:** `docs/architecture.md`

---

## Query Layer Patterns

### Location Field Pattern (IMPORTANT - 2025-12-16)

**Problem:** Clinical domains that reference `Dim.Location` for location data must follow a consistent three-column pattern. Query/schema mismatches cause UI rendering failures.

**Standard Pattern:** All domains MUST store and SELECT three columns for location fields:
1. **`*_id`** - Foreign key to `Dim.Location` (e.g., `location_id`, `admit_location_id`)
2. **`*_name`** - Denormalized location name (e.g., `location_name`, `collection_location`)
3. **`*_type`** - Denormalized location type (e.g., `location_type`, `collection_location_type`)

**Why?**
- **Performance:** Avoids JOIN with `Dim.Location` on every query
- **Simplicity:** Templates reference `location_name` directly without lookups
- **Consistency:** Uniform pattern across all domains reduces errors

### Code Examples

#### ✅ CORRECT: Vitals Query (app/db/vitals.py)
```python
def get_patient_vitals(icn: str, limit: int = 100):
    query = text("""
        SELECT
            vital_id,
            patient_key,
            vital_type,
            vital_abbr,
            taken_datetime,
            result_value,
            unit_of_measure,
            location_id,        -- All three columns
            location_name,      -- required
            location_type,      --
            entered_by,
            abnormal_flag
        FROM patient_vitals
        WHERE patient_key = :icn
        ORDER BY taken_datetime DESC
        LIMIT :limit
    """)

    with engine.connect() as conn:
        results = conn.execute(query, {"icn": icn, "limit": limit}).fetchall()

        vitals = []
        for row in results:
            vitals.append({
                "vital_id": row[0],
                "patient_key": row[1],
                "vital_type": row[2],
                "vital_abbr": row[3],
                "taken_datetime": str(row[4]) if row[4] else None,
                "result_value": row[5],
                "unit_of_measure": row[6],
                "location_id": row[7],       # Index matches SELECT order
                "location_name": row[8],     #
                "location_type": row[9],     #
                "entered_by": row[10],       # Shifted indices after adding columns
                "abnormal_flag": row[11],    #
            })

        return vitals
```

#### ✅ CORRECT: Labs Query (app/db/labs.py - future)
```python
def get_patient_labs(icn: str, limit: int = 100):
    query = text("""
        SELECT
            lab_id,
            patient_key,
            lab_test_name,
            result_value,
            result_numeric,
            result_unit,
            abnormal_flag,
            collection_datetime,
            location_id,                    -- All three columns
            collection_location,            -- Domain-specific name
            collection_location_type,       -- Domain-specific name
            specimen_type
        FROM patient_labs
        WHERE patient_key = :icn
        ORDER BY collection_datetime DESC
        LIMIT :limit
    """)

    with engine.connect() as conn:
        results = conn.execute(query, {"icn": icn, "limit": limit}).fetchall()

        labs = []
        for row in results:
            labs.append({
                "lab_id": row[0],
                "patient_key": row[1],
                "lab_test_name": row[2],
                "result_value": row[3],
                "result_numeric": row[4],
                "result_unit": row[5],
                "abnormal_flag": row[6],
                "collection_datetime": str(row[7]) if row[7] else None,
                "location_id": row[8],
                "collection_location": row[9],
                "collection_location_type": row[10],
                "specimen_type": row[11],
            })

        return labs
```

#### ✅ CORRECT: Encounters Query (app/db/encounters.py)
```python
def get_patient_encounters(icn: str):
    # Note: Encounters has TWO locations (admit + discharge)
    query = text("""
        SELECT
            encounter_id,
            patient_key,
            inpatient_id,
            admit_datetime,
            admit_location_id,          -- Admit location (3 columns)
            admit_location_name,        --
            admit_location_type,        --
            discharge_datetime,
            discharge_location_id,      -- Discharge location (3 columns)
            discharge_location_name,    --
            discharge_location_type,    --
            encounter_status
        FROM patient_encounters
        WHERE patient_key = :icn
        ORDER BY admit_datetime DESC
    """)

    with engine.connect() as conn:
        results = conn.execute(query, {"icn": icn}).fetchall()

        encounters = []
        for row in results:
            encounters.append({
                "encounter_id": row[0],
                "patient_key": row[1],
                "inpatient_id": row[2],
                "admit_datetime": str(row[3]) if row[3] else None,
                "admit_location_id": row[4],
                "admit_location_name": row[5],
                "admit_location_type": row[6],
                "discharge_datetime": str(row[7]) if row[7] else None,
                "discharge_location_id": row[8],
                "discharge_location_name": row[9],
                "discharge_location_type": row[10],
                "encounter_status": row[11],
            })

        return encounters
```

#### ❌ WRONG: Selecting Only ID Column
```python
# DO NOT DO THIS
query = text("""
    SELECT
        vital_id,
        patient_key,
        location_id  -- ❌ Missing name and type
    FROM patient_vitals
    WHERE patient_key = :icn
""")
# Problem: Template can't display location name, defeating denormalization purpose
```

#### ❌ WRONG: Using Old Single Column
```python
# DO NOT DO THIS
query = text("""
    SELECT
        vital_id,
        patient_key,
        location  -- ❌ Column doesn't exist (old pattern)
    FROM patient_vitals
    WHERE patient_key = :icn
""")
# Problem: SQL error "column 'location' does not exist"
```

### Template Usage

```html
<!-- app/templates/patient_vitals.html -->
{% for vital in vitals %}
  <tr>
    <td>{{ vital.taken_datetime[:10] }}</td>
    <td>{{ vital.vital_type }}</td>
    <td>{{ vital.result_value }} {{ vital.unit_of_measure }}</td>
    <td>
      {% if vital.location_name %}
        {{ vital.location_name }}
        <span class="location-type">({{ vital.location_type }})</span>
      {% endif %}
    </td>
  </tr>
{% endfor %}
```

### When Schema Changes Require Query Updates

**Checklist when adding location fields to existing domain:**
1. ✅ **Update DDL** in `db/ddl/create_<domain>_table.sql` (add 3 columns)
2. ✅ **Update ETL Gold/Load** scripts to populate all 3 columns
3. ✅ **Update all queries** in `app/db/<domain>.py` to SELECT all 3 columns
4. ✅ **Update row parsing** logic (adjust dictionary indices after new columns)
5. ✅ **Update templates** to reference `*_name` instead of old column
6. ✅ **Rerun ETL pipeline** (Bronze → Silver → Gold → Load)
7. ✅ **Test all views** (widget, full page, API endpoints)

**Example Real Bug (Vitals - 2025-12-16):**
- Schema changed from single `location` VARCHAR to three columns
- Queries still referenced old column name → SQL error
- Empty widget displays ("No vitals found") despite 8,730 records in database
- Fix: Updated 3 query functions + 1 template reference

**See Also:** `docs/architecture.md` Section 4.3 (Location Field Patterns) for complete architectural guidance

---

## Real-Time Data Integration (Vista RPC Broker)

### Overview

Med-z1 uses a **dual-source data architecture**:
- **PostgreSQL (T-1 and earlier):** Fast, cached historical data from CDW via ETL pipeline
- **Vista RPC Broker (T-0, today):** Real-time queries with 1-3 second latency per site

**Design Document:** `docs/vista-rpc-broker-design.md` (v1.2)

### Integration Patterns

**User-Controlled Refresh:**
- Show PostgreSQL data by default (fast page loads)
- "Refresh from VistA" button for real-time T-0 data
- No automatic fetching (user maintains control)

**Implementation:** `app/services/vista_client.py`

```python
from app.services.vista_client import VistaClient

vista = VistaClient()

@router.get("/patient/{icn}/vitals-realtime")
async def get_vitals_realtime(icn: str):
    # 1. Fetch historical from PostgreSQL (T-2 and earlier)
    historical = await db.get_vitals(icn, days=7, exclude_today=True)

    # 2. Get target sites based on treating facilities
    target_sites = get_target_sites(icn, domain="vitals")  # Returns top 2 sites

    # 3. Fetch real-time from Vista (T-0, today)
    vista_results = await vista.call_rpc_multi_site(
        sites=target_sites,
        rpc_name="GMV LATEST VM",
        params=[icn]  # ICN automatically translated to DFN per site
    )

    # 4. Parse and merge (deduplicate, prefer Vista for T-1+)
    today_vitals = []
    for site, response in vista_results.items():
        if response.success:
            parsed = vista.parse_vitals_response(response.data)
            today_vitals.extend(parsed)

    # 5. Merge with historical data (no duplicates)
    all_vitals = merge_postgresql_and_vista_data(
        postgresql_data=historical,
        vista_data=today_vitals,
        domain="vitals"
    )

    return templates.TemplateResponse("patient/vitals.html", {
        "vitals": all_vitals,
        "data_current_through": datetime.now().strftime("%b %d, %Y"),
        "completeness": "complete" if all succeeded else "partial"
    })
```

### Site Selection Policy

**Default Limits** (prevents "query all 140 sites" failure mode):
```python
DOMAIN_SITE_LIMITS = {
    "vitals": 2,        # Freshest data, recent care
    "allergies": 5,     # Safety-critical, wider search
    "medications": 3,   # Balance freshness + comprehensiveness
    "demographics": 1,  # Typically unchanged
    "labs": 3,          # Recent results most relevant
    "default": 3,       # Conservative default
}
```

**Hard Maximum:** 10 sites per query (requires explicit user action to exceed 5)

### Merge/Deduplication Rules

**Canonical Event Keys** (per domain):
```python
CANONICAL_KEYS = {
    "vitals": ("date_time", "type", "sta3n", "vital_id"),
    "allergies": ("allergen", "allergen_type", "sta3n", "allergy_id"),
    "medications": ("rx_number", "sta3n"),
}
```

**Priority Rules:**
- Dates >= T-1: Prefer Vista (fresher, real-time)
- Dates < T-1: Use PostgreSQL only
- Duplicates: Keep Vista, discard PostgreSQL

**Implementation:** `app/services/realtime_overlay.py` (future Phase 6-7 enhancement)

### UI Pattern (HTMX)

```html
<div id="vitals-container">
  <h3>Vitals (Last 7 Days)</h3>
  <p class="data-freshness">Data current through: {{ data_current_through }}</p>

  {% if completeness == "partial" %}
    <p class="warning">Real-time refresh incomplete - {{ sites_responded }} of {{ sites_total }} sites responded</p>
  {% endif %}

  <button
    hx-get="/patient/{{ patient_icn }}/vitals-realtime"
    hx-target="#vitals-container"
    hx-swap="outerHTML"
    hx-indicator="#vitals-spinner"
    class="btn-refresh">
    Refresh from VistA
  </button>

  <div id="vitals-spinner" class="htmx-indicator">
    🔄 Fetching real-time data from VistA sites...
  </div>

  <!-- Vitals table/chart -->
</div>
```

### When to Implement

**Prerequisites:**
- Core domains implemented (Demographics, Vitals, Allergies, Medications)
- Patient registry with ICN/DFN mappings created
- Vista RPC Broker service operational (port 8003)

**Timeline:** After Encounters + Labs domains complete (establishes baseline)

---

## AI Clinical Insights

### Overview

Med-Z1 provides AI-powered clinical decision support via a conversational interface at `/insight`. The AI subsystem uses LangGraph to orchestrate tool calls and provide evidence-based clinical insights.

**Access:** Navigate to `/insight` or `/insight/{icn}` from patient dashboard

### Available AI Tools (Phase 4 Complete - 2026-01-03)

The AI agent has access to **4 LangChain tools** for querying clinical data:

1. **`check_ddi_risks`** - Drug-drug interaction analysis
   - Analyzes medication list for interactions
   - Returns severity levels and clinical recommendations
   - Source: `ai/tools/medication_tools.py`

2. **`get_patient_summary`** - Comprehensive patient overview
   - Returns: Demographics, medications, vitals, allergies, encounters, **recent clinical notes (last 3)** ⭐
   - Source: `ai/tools/patient_tools.py`
   - Uses: `ai/services/patient_context.py` → `PatientContextBuilder`

3. **`analyze_vitals_trends`** - Statistical vitals analysis
   - Trend analysis with statistical significance testing
   - Clinical interpretation of vital sign patterns
   - Source: `ai/tools/vitals_tools.py`

4. **`get_clinical_notes_summary`** - Targeted clinical notes queries ⭐ **NEW (Phase 4)**
   - Parameters: `patient_icn`, `note_type` (optional), `days` (default 90), `limit` (default 5)
   - Filters: Progress Notes, Consults, Discharge Summaries, Imaging Reports
   - Returns: Formatted note summaries with 500-char previews
   - Source: `ai/tools/notes_tools.py`

### Example Queries

**General Overview:**
- "What are the key clinical risks for this patient?"
- "Summarize this patient's recent clinical activity"

**Drug Interactions:**
- "Are there any drug-drug interaction concerns?"
- "Is it safe to add this medication?"

**Clinical Notes (Phase 4):** ⭐ **NEW**
- "What did recent clinical notes say about this patient?"
- "Show me consult notes from the last 6 months"
- "What did the cardiology consult recommend?"
- "Summarize recent progress notes"
- "What imaging studies were done recently?"

**Vitals Analysis:**
- "How is the patient's blood pressure control?"
- "Show me weight trends over time"

**Combined Queries:**
- "Check DDI risks and summarize recent notes"
- "What are the key clinical risks? Include recent clinical notes."

### Architecture

**LangGraph Agent Flow:**
```
User Question
    ↓
System Prompt (ai/prompts/system_prompts.py)
    ↓
LangGraph Agent (ai/agents/insight_agent.py)
    ↓
Tool Selection (autonomous)
    ↓
Tool Execution (ai/tools/*)
    ↓
Context Building (ai/services/patient_context.py)
    ↓
Database Queries (app/db/*.py)
    ↓
Response Synthesis (GPT-4)
    ↓
User Response (markdown → HTML)
```

**Key Components:**
- **System Prompts:** `ai/prompts/system_prompts.py` - Centralized prompt management
- **Suggested Questions:** `ai/prompts/suggested_questions.py` - UI question chips (system-wide)
- **Agent:** `ai/agents/insight_agent.py` - LangGraph orchestration
- **Tools:** `ai/tools/*.py` - LangChain @tool decorated functions
- **Context Builder:** `ai/services/patient_context.py` - Formats DB queries for LLM
- **Routes:** `app/routes/insight.py` - FastAPI endpoints for chat interface

### Suggested Questions

**Purpose:** Guide clinicians toward high-value queries that showcase agent capabilities.

**Location:** `ai/prompts/suggested_questions.py`

**Current Questions:**
1. "What are the key clinical risks for this patient?"
2. "Are there any drug-drug interaction concerns?"
3. "What did recent clinical notes say about this patient?"

**Design Principles:**
- Demonstrate available tools (DDI, vitals, notes, patient summary)
- Broad enough to apply to most patients
- Specific enough to yield actionable insights

**Usage:**
```python
# app/routes/insight.py
from ai.prompts.suggested_questions import SUGGESTED_QUESTIONS

suggested_questions = SUGGESTED_QUESTIONS
```

**To modify questions:** Edit the `SUGGESTED_QUESTIONS` list in `ai/prompts/suggested_questions.py`

### Configuration (config.py)

```python
# OpenAI LLM Settings
OPENAI_MODEL = "gpt-4-turbo"
OPENAI_TEMPERATURE = 0.3  # Low for clinical accuracy

# Clinical Notes for AI (Phase 4)
AI_NOTES_PREVIEW_LENGTH = 500     # Characters per note (optimal context vs cost)
AI_NOTES_SUMMARY_LIMIT = 3        # Notes in patient summaries
AI_NOTES_QUERY_DAYS = 90          # Default lookback period
AI_NOTES_MAX_LIMIT = 10           # Performance/cost cap
```

### Performance Characteristics

**Response Times:**
- Simple queries (DDI check): < 3 seconds
- Patient summary with notes: < 5 seconds (p90)
- Complex multi-tool queries: < 8 seconds

**Token Usage:**
- Patient summary (no notes): ~1,600 tokens
- Patient summary (with 3 notes): ~1,975 tokens (+375)
- Targeted notes query (5 notes): ~625 tokens
- Cost per summary with notes: ~$0.0004 (negligible)

**Note Preview Strategy:**
- UI uses 200-char previews (display optimization)
- AI uses 500-char previews (clinical context optimization)
- Captures SOAP opening (Subjective, Objective, Assessment start)
- 50× cheaper than full text, sufficient for most queries

### Testing the AI

**Start Services:**
```bash
# Terminal 1: CCOW service
uvicorn ccow.main:app --reload --port 8001

# Terminal 2: Main app
uvicorn app.main:app --reload
```

**Test Flow:**
1. Navigate to `http://127.0.0.1:8000/insight`
2. Login with: `clinician.alpha@va.gov` / `VaDemo2025!`
3. Search for patient: `ICN100001`
4. Click suggested questions or type custom queries
5. Observe tool usage in response ("Sources checked: ...")

### Phase 4 Implementation Notes

**What Changed (2026-01-03):**
- ✅ Created `ai/prompts/system_prompts.py` (centralized prompt architecture)
- ✅ Created `ai/prompts/suggested_questions.py` (system-wide question management)
- ✅ Added 5 AI notes config parameters to `config.py`
- ✅ Created `get_recent_notes_for_ai()` in `app/db/notes.py` (500-char previews)
- ✅ Enhanced `PatientContextBuilder` with `get_notes_summary()` method
- ✅ Updated `build_comprehensive_summary()` to include notes section
- ✅ Created `get_clinical_notes_summary()` tool in `ai/tools/notes_tools.py`
- ✅ Updated `ALL_TOOLS` to include 4th tool
- ✅ Refactored suggested questions from inline list to `ai/prompts/` module
- ✅ Updated suggested questions to include note-based query
- ✅ Integrated system prompt into `app/routes/insight.py`

**Design Reference:** `docs/spec/ai-insight-design.md` (Phase 4 complete)

---

## Project Structure

```
app/
  db/                   # Database query layer (SQLAlchemy)
    patient.py          # Patient demographics queries
    patient_allergies.py
    patient_flags.py
    vitals.py
  routes/               # FastAPI route handlers
    patient.py          # Patient, flags, allergies API routes
    dashboard.py        # Dashboard routes
    vitals.py          # Vitals API + page routes
  static/               # CSS, JavaScript, images
    styles.css
  templates/            # Jinja2 HTML templates
    partials/           # HTMX-compatible HTML partials
    base.html           # Base template
    dashboard.html
  utils/                # Utility modules
    ccow_client.py      # CCOW context management
  main.py              # FastAPI application entry point
```

