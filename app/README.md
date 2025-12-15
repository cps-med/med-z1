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

