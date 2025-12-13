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

