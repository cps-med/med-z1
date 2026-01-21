# Patient-Aware Topbar – Design & Implementation Guide

January 21, 2026 • Document version v3.0

---

## Implementation Status

✅ **Phase 2 COMPLETE** (December 2025)
- Topbar with patient demographics display
- CCOW integration with patient search
- Patient search modal (Name, ICN, EDIPI search)
- Manual refresh functionality
- Real PostgreSQL database integration

✅ **Phase 3 COMPLETE** (December 2025)
- Patient flags full implementation
- 15 patient flags in database (12 active)
- Flag history tracking with sensitive narrative text
- HTMX lazy loading for performance
- Badge count display with color coding for overdue flags

✅ **CCOW v2.0 COMPLETE** (December 2025)
- Multi-user context isolation
- Session-based context persistence
- User-specific patient context across applications

✅ **Additional Features Implemented**:
- Deceased patient indicator with optional death date
- Review status calculation (CURRENT, DUE SOON, OVERDUE)
- National/Local flag categorization

**Related Documentation:**
- `docs/spec/patient-flags-design.md` - Patient Flags Phase 3 complete design specification
- `docs/spec/ccow-v2-implementation-summary.md` - CCOW v2.0 multi-user context implementation
- `docs/spec/ccow-multi-user-enhancement.md` - CCOW v2.0 detailed design document

---

## Table of Contents

### Part 1: Design & Requirements
1. [Executive Summary](#1-executive-summary)
2. [Requirements Summary](#2-requirements-summary)
3. [Visual Design & Layout](#3-visual-design--layout)
4. [Recommended Architecture](#4-recommended-architecture)
5. [Key Design Decisions](#5-key-design-decisions)

### Part 2: Implementation Guide
6. [Prerequisites & Setup](#6-prerequisites--setup)
7. [Development Process Overview](#7-development-process-overview)
8. [Implementation Strategy & Order](#8-implementation-strategy--order)
9. [File Structure & Components](#9-file-structure--components)
10. [Backend Implementation](#10-backend-implementation)
11. [Frontend Implementation](#11-frontend-implementation)
12. [Styling & Interactions](#12-styling--interactions)

### Part 3: Quality & Deployment
13. [Testing Strategy](#13-testing-strategy)
14. [Common Pitfalls & Troubleshooting](#14-common-pitfalls--troubleshooting)
15. [Success Criteria](#15-success-criteria)
16. [Deployment Approach](#16-deployment-approach)

### Part 4: Reference
17. [API Endpoint Reference](#17-api-endpoint-reference)
18. [CSS Improvement Recommendations](#18-css-improvement-recommendations)

### Appendices
- [Appendix A: Data Flow Examples](#appendix-a-data-flow-examples)
- [Appendix B: Quick Start Guide](#appendix-b-quick-start-guide)
- [Appendix C: Implementation Checklist](#appendix-c-implementation-checklist)
- [Appendix D: Document History](#appendix-d-document-history)

---

# Part 1: Design & Requirements

## 1. Executive Summary

This document provides comprehensive design and implementation guidance for the patient-aware topbar in the med-z1 application. The topbar displays CCOW-synchronized patient demographics and provides action buttons for patient selection and flags viewing.

**This document implements Phase 2 from `implementation-roadmap.md`.**

### 1.1 Key Objectives

- Display active patient demographics in topbar (name, ICN, DOB, age, sex, station)
- Integrate with CCOW Context Vault for patient context synchronization
- Provide patient search capability via modal dialog
- Support manual refresh of patient context from CCOW vault
- Maintain existing UI/UX patterns and styling conventions
- Use HTMX for dynamic updates without full page reloads

### 1.2 Scope

**Phase 2 - Implemented (December 2025):**
- ✅ Topbar redesign with patient demographics area
- ✅ CCOW vault integration on application startup
- ✅ Patient search modal with search results (Name, ICN, EDIPI search)
- ✅ Patient flags modal with View Flags button
- ✅ Manual "Refresh Patient" functionality
- ✅ HTMX-powered dynamic updates
- ✅ Responsive design
- ✅ Real PostgreSQL database integration

**Phase 3 - Implemented (December 2025):**
- ✅ Patient flags full implementation with real data
- ✅ Flag history tracking with sensitive narrative text
- ✅ Review status calculation (CURRENT, DUE SOON, OVERDUE)
- ✅ HTMX lazy loading for flag details
- ✅ Badge count display with color coding

**CCOW v2.0 - Implemented (December 2025):**
- ✅ Multi-user context isolation
- ✅ Session-based patient context persistence
- ✅ User-specific context across applications

**Additional Features Implemented:**
- ✅ Deceased patient indicator with optional death date

**Out of Scope (Future Enhancements):**
- Advanced patient search filters (fuzzy matching, date ranges)
- Real-time CCOW context updates (polling/WebSocket)
- Patient flag creation/editing interface

**Search Functionality Note:**
- SSN search is **not implemented** per VA policy (moving away from SSN as identifier)
- SSN is displayed (masked) but not searchable
- Supported search types: Name, ICN, EDIPI

---

## 2. Requirements Summary

### 2.1 Patient Demographics Display (Upper Left)

**Format:** Two-line display

**Line 1:** `DOOREE, Adam (M, 45)` or `DOOREE, Adam (M, 45) • deceased`
- Larger, bold text (similar to existing `header_title`)
- Format: `LASTNAME, Firstname (Sex, Age)`
- Optional deceased indicator: `• deceased` shown if `deceased_flag = 'Y'`
- Hover on deceased indicator shows death date if available

**Line 2:** `ICN: ICN100001 | SSN: ***-**-6789 | DOB: 1980-01-02 | Station: 508`
- Smaller text (similar to existing `header_subtitle`)
- ICN displayed as-is from database (may have "ICN" prefix or VA V-format like "1016V123456")
- SSN masked to last 4 digits
- Station shows code (e.g., "508") with optional facility name

**Note on ICN Formats:**
The database contains two ICN formats:
- **Most patients (26)**: `ICN100001`, `ICN100002`, etc. (with "ICN" prefix)
- **Some patients (10)**: `1016V123456`, `1017V234567`, etc. (VA V-format)

Both formats are valid and searchable.

**No Patient State:** Prominent call-to-action
- **Line 1:** "No patient selected" (muted color, bold)
- **Line 2:** "Click 'Select Patient' to begin" (muted, italic)

### 2.2 Action Buttons (Upper Right)

**Button 1: "View Patient Flags"**
- Opens modal/dialog overlay with flag details
- ✅ **Production Implementation:** Full flags functionality complete (Phase 3 - December 2025)
- Displays real patient flags from PostgreSQL database
- Disabled (grayed out) when no patient is active
- Shows badge with flag count when flags are present
- Badge color: Red/warning for overdue flags, default otherwise

**Button 2: "Select Patient"**
- Opens modal/dialog overlay with patient search form
- Always enabled
- Search results display within modal
- User selects patient to set CCOW context
- Supports search by: Name, ICN, EDIPI (NOT SSN)

**Button 3: "Refresh Patient"**
- Re-queries CCOW vault to refresh patient context
- Always enabled
- Updates patient demographics display via HTMX

### 2.3 CCOW Integration Behavior

**On Application Startup:**
1. Query CCOW vault (`GET /ccow/active-patient`)
2. If patient context exists:
   - Fetch patient demographics from PostgreSQL (using ICN from vault)
   - Populate patient header with demographics
3. If no patient context exists:
   - Display "No patient selected" message

**On Page Navigation:**
- Do NOT re-query CCOW vault
- Patient header remains unchanged

**On Manual Refresh:**
- User clicks "Refresh Patient" button
- Re-query CCOW vault
- Update patient header based on current vault state

**On Patient Selection:**
- User searches and selects patient from modal
- Update CCOW vault (`PUT /ccow/active-patient` with selected ICN)
- Fetch patient demographics
- Update patient header
- Close modal

### 2.4 Fallback Behavior

**If CCOW Service Unavailable:**
- Default to "No patient selected" state
- Log error to console/logs
- Do not block application startup
- User can still search and select patients (CCOW updates will fail silently)

---

## 3. Visual Design & Layout

### 3.1 Topbar Layout (Wireframe)

**With Active Patient:**
```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  ☰  │ DOOREE, Adam (M, 45)                       │ [View Patient Flags ②]       │
│     │ ICN: ICN100001 | SSN: ***-**-6789 |        │ [Select Patient]              │
│     │ DOB: 1980-01-02 | Station: 508             │ [Refresh Patient]             │
└──────────────────────────────────────────────────────────────────────────────────┘
```

**When No Patient Selected:**
```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  ☰  │ No patient selected                        │ [View Patient Flags]         │
│     │ Click 'Select Patient' to begin             │   (disabled)                 │
│     │                                             │ [Select Patient]             │
│     │                                             │ [Refresh Patient]            │
└──────────────────────────────────────────────────────────────────────────────────┘
```

**Legend:**
- `☰` - Hamburger menu icon (existing sidebar toggle)
- `②` - Red badge showing flag count
- Disabled buttons shown in gray

### 3.2 Button States

| Button              | No Patient | Patient (No Flags) | Patient (With Flags) |
|---------------------|------------|--------------------|-----------------------|
| View Patient Flags  | Disabled   | Enabled            | Enabled + Badge       |
| Select Patient      | Enabled    | Enabled            | Enabled               |
| Refresh Patient     | Enabled    | Enabled            | Enabled               |

### 3.3 Modal Layouts

**Patient Search Modal:**
```
┌─────────────────────────────────────────────────────┐
│  Select Patient                                  ✕  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Search by Name, ICN, or EDIPI                      │
│  ┌───────────────────────────────────────────────┐  │
│  │ Enter patient name, ICN, EDIPI...             │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  Search Type: ○ Name  ○ ICN  ○ EDIPI                │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │ DOOREE, Adam (M, 45)                          │  │
│  │ ICN: ICN100001 | SSN: ***-**-6789 | DOB: ...  │  │
│  ├───────────────────────────────────────────────┤  │
│  │ MIIFAA, Barry (F, 50)                         │  │
│  │ ICN: ICN100002 | SSN: ***-**-4321 | DOB: ...  │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Patient Flags Modal (✅ Production - Phase 3 Complete):**
```
┌─────────────────────────────────────────────────────┐
│  Patient Flags                                   ✕  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │ ⚠ High Risk for Suicide                       │  │
│  │ Category: BEHAVIORAL                          │  │
│  │ Active Date: 2024-01-15                       │  │
│  │ Review Date: 2025-01-15                       │  │
│  │ Patient flagged for suicide risk assessment   │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  Note: Full flags implementation in Phase 3       │
└─────────────────────────────────────────────────────┘
```

---

## 4. Recommended Architecture

### 4.1 Topbar Structure

**Approach: HTMX-powered partial templates**

**Rationale:**
- **Dynamic Updates**: Patient demographics update without full page reload
- **Separation of Concerns**: Patient header logic isolated from base template
- **Reusability**: Patient header partial can be reused elsewhere
- **HTMX Integration**: Leverages existing HTMX dependency (already loaded in `base.html:14`)
- **Performance**: Avoids full page reloads, only swaps the patient header section
- **Maintainability**: Easier to test and modify patient header independently

### 4.2 Template Structure

```
app/templates/
  base.html                          # Main layout (modified topbar)
  partials/
    patient_header.html               # Patient demographics display (HTMX target)
    patient_search_modal.html         # Patient search modal
    patient_search_results.html       # Search results partial (HTMX target)
    patient_flags_modal.html          # Patient flags modal (production)
    patient_flags_content.html        # Flag cards display (Phase 3)
    flag_card.html                    # Individual flag card (Phase 3)
    flag_history.html                 # Flag history timeline (Phase 3)
```

### 4.3 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Startup Flow                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Browser loads   │
                    │  base.html       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  HTMX triggers   │
                    │  hx-get on load  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ GET /api/patient/current │
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │  Query CCOW Vault        │
                    │  GET /ccow/active-patient│
                    └────────┬─────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
        ┌────────────────┐      ┌──────────────┐
        │ Patient Found  │      │ No Patient   │
        └────────┬───────┘      └──────┬───────┘
                 │                      │
                 ▼                      ▼
        ┌────────────────┐      ┌──────────────────┐
        │ Fetch patient  │      │ Render header    │
        │ demographics   │      │ with "No patient │
        │ from PostgreSQL│      │ selected" message│
        └────────┬───────┘      └──────┬───────────┘
                 │                      │
                 ▼                      │
        ┌────────────────┐              │
        │ Render header  │              │
        │ with patient   │              │
        │ demographics   │              │
        └────────┬───────┘              │
                 │                      │
                 └──────────┬───────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ HTMX swaps      │
                   │ patient header  │
                   │ into topbar     │
                   └─────────────────┘
```

For complete patient selection flow, see [Appendix A: Data Flow Examples](#appendix-a-data-flow-examples).

---

## 5. Key Design Decisions

### 5.1 Why HTMX?

**Decision:** Use HTMX for all dynamic updates (patient header, search results, modals)

**Rationale:**
- Maintains server-side rendering philosophy (no React/Vue complexity)
- No complex JavaScript state management
- Graceful degradation (works without JS)
- Minimal client-side code
- Excellent developer experience

**Alternative Considered:** Full JavaScript SPA (React, Vue)
- **Rejected:** Too much complexity for simple patient context switching

### 5.2 Why CCOW Integration Pattern?

**Decision:** Query CCOW once on startup, then manual refresh only

**Rationale:**
- Avoids excessive network requests
- User controls when context updates (explicit action)
- Simple, predictable behavior
- No WebSocket/polling complexity

**Alternative Considered:** Real-time polling every 5 seconds
- **Rejected:** Unnecessary network overhead, battery drain on mobile

### 5.3 Why Two-Line Patient Display?

**Decision:**
```
Line 1: DOOREE, Adam (M, 45)           [Bold, large]
Line 2: ICN: ICN100001 | SSN: ***-**-6789 | DOB: ... | Station: 508
```

**Rationale:**
- Maximizes information density
- Maintains readability
- Matches existing header pattern
- Name prominence (most important identifier for clinicians)

**Alternative Considered:** Single-line compact format
- **Rejected:** Too cramped, hard to scan

### 5.4 Why Modal-Based Search?

**Decision:** Patient search in modal overlay (not inline, not sidebar)

**Rationale:**
- Focused user experience (modal directs attention)
- Doesn't disrupt main layout
- Mobile-friendly (full-screen on small devices)
- Clear entry/exit points

**Alternative Considered:** Inline search bar in topbar
- **Rejected:** Too cramped, no space for results

### 5.5 Why Remove SSN Search?

**Decision:** Do not implement SSN search; display SSN but don't search by it

**Rationale:**
- VA policy: Moving away from SSN as primary identifier
- Security/privacy concerns
- SSN still displayed (masked) for verification purposes
- ICN is primary identifier going forward

---

# Part 2: Implementation Guide

## 6. Prerequisites & Setup

### 6.1 Prerequisites Checklist

Before starting implementation, verify:

**Phase 1 Complete:**
- [ ] PostgreSQL `patient_demographics` table exists and has 36 patients
- [ ] Can query: `SELECT * FROM patient_demographics LIMIT 5;`
- [ ] Gold Parquet files exist: `lake/gold/patient_demographics/patient_demographics.parquet`

**CCOW Service:**
- [ ] CCOW service running on port 8001
- [ ] Can access: `http://localhost:8001/docs`
- [ ] CCOW vault API responds: `curl http://localhost:8001/ccow/active-patient`

**Database Connectivity:**
- [ ] Can connect to PostgreSQL from Python
- [ ] Test: `python -c "from sqlalchemy import create_engine; from config import DATABASE_URL; engine = create_engine(DATABASE_URL); print('Connected!')"`

**Configuration:**
- [ ] `.env` has `DATABASE_URL` for PostgreSQL
- [ ] `.env` has `CCOW_BASE_URL=http://localhost:8001`
- [ ] `.env` has `CCOW_ENABLED=true`
- [ ] `config.py` loads these settings correctly

**Python Environment:**
- [ ] Python 3.11 virtual environment activated (`.venv`)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] FastAPI, HTMX, SQLAlchemy, psycopg2-binary installed

**Development Tools:**
- [ ] Browser DevTools familiar (Network tab for HTMX debugging)
- [ ] Code editor ready (VS Code, PyCharm, etc.)

### 6.2 Quick Environment Verification

Run these commands to verify setup:

```bash
# Verify PostgreSQL connection
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM patient_demographics;"
# Expected: 36

# Verify CCOW service
curl http://localhost:8001/ccow/active-patient
# Expected: 404 (no patient set) or 200 with patient data

# Verify Python can connect to PostgreSQL
python -c "
from sqlalchemy import create_engine
from config import DATABASE_URL
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute('SELECT COUNT(*) FROM patient_demographics')
    print(f'Patient count: {result.fetchone()[0]}')
"
# Expected: Patient count: 36

# Verify CCOW client
python -c "
from app.utils.ccow_client import ccow_client
patient = ccow_client.get_active_patient()
print(f'Current patient: {patient}')
"
# Expected: Current patient: None (or ICN if set)
```

### 6.3 Directory Structure Setup

Create required directories:

```bash
# From project root
mkdir -p app/db app/routes app/utils app/templates/partials
touch app/db/__init__.py app/routes/__init__.py app/utils/__init__.py
```

Verify structure:
```bash
tree app/ -L 2
# Expected:
# app/
# ├── db/
# │   └── __init__.py
# ├── routes/
# │   └── __init__.py
# ├── utils/
# │   └── __init__.py
# ├── templates/
# │   ├── base.html
# │   └── partials/
# ├── static/
# │   ├── styles.css
# │   └── app.js
# └── main.py
```

---

## 7. Development Process Overview

### 7.1 Four-Stage Implementation

Phase 2 implementation follows a four-stage process:

**Stage 1: Backend Foundation (Days 1-2)**
- Database query layer (`app/db/patient.py`)
- CCOW client utility (`app/utils/ccow_client.py`)
- Patient API routes (`app/routes/patient.py`)
- Real PostgreSQL integration

**Stage 2: UI Templates (Days 3-4, Phase 3 additions)**
- Modified topbar (`app/templates/base.html`)
- Patient header partial (`patient_header.html`)
- Patient search modal (`patient_search_modal.html`)
- Search results partial (`patient_search_results.html`)
- Flags modal (`patient_flags_modal.html`) - ✅ Production complete
- Flags content templates (Phase 3): `patient_flags_content.html`, `flag_card.html`, `flag_history.html`

**Stage 3: Styling & Interactions (Day 4)**
- CSS additions (`app/static/styles.css`)
- JavaScript modal handlers (`app/static/app.js`)
- HTMX event listeners
- Responsive design adjustments

**Stage 4: Integration & Testing (Day 5)**
- End-to-end workflow testing
- CCOW integration verification
- Responsive design testing
- Accessibility review
- Error scenario handling

### 7.2 Daily Development Breakdown

**Day 1: Backend Layer**
- Morning: Implement `app/db/patient.py` (database queries)
- Afternoon: Implement `app/utils/ccow_client.py` (CCOW HTTP client)
- Evening: Test database queries and CCOW client independently

**Day 2: API Routes**
- Morning: Implement `app/routes/patient.py` (all endpoints)
- Afternoon: Test endpoints with curl/Postman
- Evening: Verify PostgreSQL data flowing correctly

**Day 3: UI Templates (Part 1)**
- Morning: Modify `base.html` topbar structure
- Afternoon: Implement `patient_header.html` partial
- Evening: Test HTMX initial load (`GET /api/patient/current`)

**Day 4: UI Templates (Part 2) + Styling**
- Morning: Implement search modal templates
- Afternoon: Add CSS styles
- Evening: Add JavaScript modal handlers

**Day 5: Integration & Testing**
- Morning: End-to-end workflow testing
- Afternoon: Fix bugs, edge cases
- Evening: Final polish, documentation

---

## 8. Implementation Strategy & Order

### 8.1 Recommended Approach: Vertical Slice

**Strategy:** Build one complete workflow end-to-end, then expand

**Workflow Priority (Historical - All Complete):**
1. **First:** Display patient header (read-only, no selection) - ✅ Complete
2. **Second:** Patient search and selection - ✅ Complete
3. **Third:** Refresh patient functionality - ✅ Complete
4. **Fourth:** Flags modal - ✅ Complete (Phase 3 production implementation)

**Why this order?**
- Get visual feedback quickly (motivating)
- Can demo progress daily
- Discovers integration issues early
- Each workflow builds on previous

### 8.2 Alternative Approach: Backend-First

**Strategy:** Complete all backend, then all frontend

**Order:**
1. Database layer + CCOW client (Day 1-2)
2. All API routes (Day 2-3)
3. All templates (Day 4-5)
4. Testing (Day 5-6)

**When to use:**
- Prefer backend work
- Want to test APIs independently first
- Team has separate frontend/backend developers

### 8.3 Critical Files Priority

**Create in this order:**

1. **First (Essential):**
   - `app/db/patient.py` - Database queries
   - `app/utils/ccow_client.py` - CCOW client
   - `app/routes/patient.py` - API routes

2. **Second (Core UI):**
   - `app/templates/partials/patient_header.html`
   - Modify `app/templates/base.html` (topbar only)

3. **Third (Search):**
   - `app/templates/partials/patient_search_modal.html`
   - `app/templates/partials/patient_search_results.html`

4. **Fourth (Polish):**
   - `app/static/styles.css` additions
   - `app/static/app.js` additions
   - `app/templates/partials/patient_flags_modal.html` (✅ production complete)

---

## 9. File Structure & Components

### 9.1 New Files to Create

```
app/
  db/
    __init__.py
    patient.py                        # NEW - Database query layer

  routes/
    __init__.py
    patient.py                        # NEW - Patient API endpoints

  utils/
    __init__.py
    ccow_client.py                    # NEW - CCOW HTTP client

  templates/
    partials/
      patient_header.html             # NEW - Patient demographics display
      patient_search_modal.html       # NEW - Search modal
      patient_search_results.html     # NEW - Search results
      patient_flags_modal.html        # NEW - Flags modal (production)
      patient_flags_content.html      # Phase 3 - Flag cards display
      flag_card.html                  # Phase 3 - Individual flag card
      flag_history.html               # Phase 3 - Flag history timeline
```

### 9.2 Files to Modify

```
app/
  templates/
    base.html                         # MODIFY - Update topbar (lines 70-96)

  static/
    styles.css                        # MODIFY - Add ~200 lines CSS
    app.js                            # MODIFY - Add ~60 lines JavaScript

  main.py                             # MODIFY - Include patient routes
```

### 9.3 Complete Directory Structure

```
med-z1/
  app/
    db/
      __init__.py
      patient.py                      ← NEW
    routes/
      __init__.py
      patient.py                      ← NEW
    utils/
      __init__.py
      ccow_client.py                  ← NEW
    templates/
      base.html                       ← MODIFY
      partials/
        patient_header.html           ← NEW
        patient_search_modal.html     ← NEW
        patient_search_results.html   ← NEW
        patient_flags_modal.html      ← NEW
    static/
      styles.css                      ← MODIFY
      app.js                          ← MODIFY
    main.py                           ← MODIFY

  docs/
    patient-topbar-design.md          ← THIS DOCUMENT
    implementation-roadmap.md
    ccow-vault-design.md
```

---

## 10. Backend Implementation

### 10.1 Database Query Layer

**File:** `app/db/patient.py`

**Purpose:** Encapsulate all patient database queries using real PostgreSQL.

```python
# app/db/patient.py

"""
Patient Database Query Layer

Provides functions to query the patient_demographics table in PostgreSQL.
This module encapsulates all SQL queries for patient data.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Simple pooling for development
    echo=False,  # Set to True to see SQL queries in logs
)


def get_patient_demographics(icn: str) -> Optional[Dict[str, Any]]:
    """
    Get patient demographics by ICN.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with patient demographics or None if not found
    """
    query = text("""
        SELECT
            patient_key,
            icn,
            ssn_last4,
            name_last,
            name_first,
            name_middle,
            name_display,
            dob,
            age,
            sex,
            primary_station,
            primary_station_name,
            source_system,
            last_updated
        FROM patient_demographics
        WHERE icn = :icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"icn": icn}).fetchone()

            if result:
                return {
                    "patient_key": result[0],
                    "icn": result[1],
                    "ssn_last4": result[2],
                    "name_last": result[3],
                    "name_first": result[4],
                    "name_middle": result[5],
                    "name_display": result[6],
                    "dob": str(result[7]) if result[7] else None,
                    "age": result[8],
                    "sex": result[9],
                    "primary_station": result[10],
                    "primary_station_name": result[11],
                    "source_system": result[12],
                    "last_updated": str(result[13]) if result[13] else None,
                }

            return None

    except Exception as e:
        logger.error(f"Error fetching patient demographics for ICN {icn}: {e}")
        return None


def search_patients(
    query: str,
    search_type: str = "name",
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for patients.

    Args:
        query: Search query string
        search_type: Type of search - 'name', 'icn', or 'edipi'
        limit: Maximum number of results

    Returns:
        List of patient dictionaries
    """
    try:
        if search_type == "name":
            sql_query = text("""
                SELECT
                    icn,
                    name_display,
                    dob,
                    age,
                    sex,
                    ssn_last4,
                    primary_station
                FROM patient_demographics
                WHERE name_last ILIKE :query OR name_first ILIKE :query
                ORDER BY name_last, name_first
                LIMIT :limit
            """)
            params = {"query": f"%{query}%", "limit": limit}

        elif search_type == "icn":
            sql_query = text("""
                SELECT
                    icn,
                    name_display,
                    dob,
                    age,
                    sex,
                    ssn_last4,
                    primary_station
                FROM patient_demographics
                WHERE icn = :query
                LIMIT :limit
            """)
            params = {"query": query, "limit": limit}

        elif search_type == "edipi":
            # EDIPI not yet implemented in database
            # Return empty results for now
            logger.warning("EDIPI search not yet implemented")
            return []

        else:
            logger.warning(f"Unknown search type: {search_type}")
            return []

        with engine.connect() as conn:
            results = conn.execute(sql_query, params).fetchall()

            return [
                {
                    "icn": row[0],
                    "name_display": row[1],
                    "dob": str(row[2]) if row[2] else None,
                    "age": row[3],
                    "sex": row[4],
                    "ssn_last4": row[5],
                    "station": row[6],
                }
                for row in results
            ]

    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        return []


def get_patient_flags(icn: str) -> Dict[str, Any]:
    """
    Get patient flags by ICN.

    NOTE: ✅ Phase 3 COMPLETE - Production implementation available.
    This function shown here is historical reference only.

    PRODUCTION CODE: See app/db/patient_flags.py for actual implementation.
    - get_patient_flags(icn: str) -> List[Dict[str, Any]]
    - get_flag_count(icn: str) -> int
    - get_flag_history(assignment_id: int) -> List[Dict[str, Any]]
    - get_active_flags_count(icn: str) -> int

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with flags array and count
    """
    # Historical mock code - REPLACED by production implementation
    # See: app/db/patient_flags.py (238 lines of production code)
    logger.info(f"get_patient_flags called for {icn}")

    # Production code queries clinical.patient_flags table in PostgreSQL
    # Returns real flag data with review status, history, and narrative text
```

**Testing the database layer:**

```bash
# Test in Python REPL
python -c "
from app.db.patient import get_patient_demographics, search_patients

# Test get by ICN (with ICN prefix)
patient = get_patient_demographics('ICN100001')
print(f'Patient: {patient[\"name_display\"] if patient else \"Not found\"}')

# Test with VA V-format
patient_v = get_patient_demographics('1016V123456')
print(f'Patient (V-format): {patient_v[\"name_display\"] if patient_v else \"Not in DB\"}')

# Test search by name
results = search_patients('DOOR', 'name')
print(f'Found {len(results)} patients')
for p in results:
    print(f'  - {p[\"name_display\"]} (ICN: {p[\"icn\"]})')
"
```

### 10.2 CCOW Client Utility

**File:** `app/utils/ccow_client.py`

```python
# app/utils/ccow_client.py

"""
CCOW Context Vault Client Utility

Provides convenience functions for med-z1/app to interact with the CCOW vault.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

from config import CCOW_ENABLED, CCOW_URL

logger = logging.getLogger(__name__)


class CCOWClient:
    """Simple HTTP client for interacting with the CCOW Context Vault."""

    def __init__(self, base_url: str = CCOW_URL, enabled: bool = CCOW_ENABLED):
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled

    def set_active_patient(self, patient_id: str, set_by: str = "med-z1") -> bool:
        """
        Notify CCOW vault of an active patient change.

        Args:
            patient_id: ICN of the patient to set
            set_by: Application name setting the context

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            logger.debug("CCOW is disabled; skipping set_active_patient call")
            return False

        try:
            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={"patient_id": patient_id, "set_by": set_by},
                timeout=2.0,
            )
            response.raise_for_status()
            logger.info("Set CCOW active patient context to %s", patient_id)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to set CCOW context: %s", exc)
            return False

    def get_active_patient(self) -> Optional[str]:
        """
        Retrieve the current patient_id (ICN) from CCOW.

        Returns:
            patient_id if set, or None if no active context or on error.
        """
        if not self.enabled:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                timeout=2.0,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return data.get("patient_id")
        except requests.RequestException as exc:
            logger.error("Failed to get CCOW context: %s", exc)
            return None

    def clear_active_patient(self, cleared_by: str = "med-z1") -> bool:
        """
        Clear the active patient context in CCOW.

        Args:
            cleared_by: Application name clearing the context

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            return False

        try:
            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by},
                timeout=2.0,
            )
            if response.status_code == 404:
                logger.warning("No active CCOW patient context to clear")
                return False

            response.raise_for_status()
            logger.info("Cleared CCOW active patient context")
            return True
        except requests.RequestException as exc:
            logger.error("Failed to clear CCOW context: %s", exc)
            return False


# Global client instance for convenience
ccow_client = CCOWClient()
```

**Testing the CCOW client:**

```bash
# Test in Python REPL
python -c "
from app.utils.ccow_client import ccow_client

# Test get (should be None initially)
patient = ccow_client.get_active_patient()
print(f'Current patient: {patient}')

# Test set (with ICN prefix)
success = ccow_client.set_active_patient('ICN100001')
print(f'Set patient: {success}')

# Test get again
patient = ccow_client.get_active_patient()
print(f'Current patient: {patient}')

# Also test with VA V-format
success = ccow_client.set_active_patient('1016V123456')
print(f'Set patient (V-format): {success}')

# Test clear
success = ccow_client.clear_active_patient()
print(f'Cleared: {success}')
"
```

### 10.3 Patient API Routes

**File:** `app/routes/patient.py`

```python
# app/routes/patient.py

"""
Patient API Routes

Handles all patient-related API endpoints for the topbar UI.
Returns HTML partials for HTMX swapping and JSON for API consumers.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.utils.ccow_client import ccow_client
from app.db.patient import get_patient_demographics, search_patients, get_patient_flags

router = APIRouter(prefix="/api/patient", tags=["patient"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/current", response_class=HTMLResponse)
async def get_current_patient(request: Request):
    """
    Get current patient from CCOW vault and return demographics partial.
    Called on initial page load via HTMX (hx-trigger="load").
    """
    try:
        # Query CCOW vault
        patient_id = ccow_client.get_active_patient()

        if not patient_id:
            # No active patient in vault
            return templates.TemplateResponse(
                "partials/patient_header.html",
                {"request": request, "patient": None}
            )

        # Fetch patient demographics from PostgreSQL
        patient = get_patient_demographics(patient_id)

        if not patient:
            logger.warning(f"Patient {patient_id} from CCOW not found in database")
            return templates.TemplateResponse(
                "partials/patient_header.html",
                {"request": request, "patient": None}
            )

        return templates.TemplateResponse(
            "partials/patient_header.html",
            {"request": request, "patient": patient}
        )

    except Exception as e:
        logger.error(f"Error getting current patient: {e}")
        return templates.TemplateResponse(
            "partials/patient_header.html",
            {"request": request, "patient": None}
        )


@router.get("/refresh", response_class=HTMLResponse)
async def refresh_patient(request: Request):
    """
    Re-query CCOW vault and return updated demographics partial.
    Called when user clicks "Refresh Patient" button.
    """
    # Same logic as get_current_patient
    return await get_current_patient(request)


@router.post("/set-context", response_class=HTMLResponse)
async def set_patient_context(request: Request):
    """
    Set patient context in CCOW vault and return demographics partial.
    Called when user selects a patient from search results.
    """
    try:
        form_data = await request.form()
        icn = form_data.get("icn")

        if not icn:
            raise HTTPException(status_code=400, detail="ICN required")

        # Update CCOW vault
        success = ccow_client.set_active_patient(patient_id=icn, set_by="med-z1")

        if not success:
            logger.warning(f"Failed to set CCOW context for {icn}")

        # Fetch patient demographics from PostgreSQL
        patient = get_patient_demographics(icn)

        if not patient:
            logger.error(f"Patient {icn} not found in database")
            raise HTTPException(status_code=404, detail="Patient not found")

        return templates.TemplateResponse(
            "partials/patient_header.html",
            {"request": request, "patient": patient}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting patient context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=HTMLResponse)
async def search_patients_endpoint(
    request: Request,
    query: str = "",
    search_type: str = "name"
):
    """
    Search for patients and return results partial.
    Called via HTMX from patient search modal (hx-trigger="keyup changed delay:500ms").

    Supported search types: name, icn, edipi (NOT ssn per VA policy)
    """
    try:
        if not query or len(query) < 2:
            return templates.TemplateResponse(
                "partials/patient_search_results.html",
                {"request": request, "results": None, "query": None}
            )

        # Query PostgreSQL for matching patients
        results = search_patients(query, search_type, limit=20)

        return templates.TemplateResponse(
            "partials/patient_search_results.html",
            {"request": request, "results": results, "query": query}
        )

    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/demographics")
async def get_patient_demographics_json(icn: str):
    """
    Get patient demographics as JSON (for future API use).
    """
    patient = get_patient_demographics(icn)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@router.get("/{icn}/flags")
async def get_patient_flags_json(icn: str):
    """
    Get patient flags as JSON.

    NOTE: ✅ Phase 3 COMPLETE - Production implementation in app/routes/patient.py
    """
    # Production code: from app.db.patient_flags import get_patient_flags
    flags_data = get_patient_flags(icn)
    return flags_data


@router.get("/flags-content", response_class=HTMLResponse)
async def get_patient_flags_modal_content(request: Request):
    """
    Get patient flags modal content (HTML partial).
    Called when patient flags modal is opened (hx-trigger="revealed").

    NOTE: ✅ Phase 3 COMPLETE - Production implementation with HTMX lazy loading
    """
    # Get current patient from CCOW (v2.0 multi-user context)
    patient_id = ccow_client.get_active_patient(request)

    if not patient_id:
        return "<p class='text-muted'>No active patient selected</p>"

    # Get flags from PostgreSQL (production)
    flags_data = get_patient_flags(patient_id)
    flags = flags_data.get("flags", [])

    if not flags:
        return "<p class='text-muted'>No active flags for this patient</p>"

    # Render flags HTML with proper templates (production)
    html = '<div class="flags-list">'
    for flag in flags:
        html += f'''
        <div class="flag-item flag-item--high-risk">
            <h3>{flag["flag_name"]}</h3>
            <p><strong>Category:</strong> {flag["category"]}</p>
            <p><strong>Active Date:</strong> {flag["active_date"]}</p>
            <p><strong>Review Date:</strong> {flag.get("review_date", "N/A")}</p>
            <p>{flag["narrative"]}</p>
        </div>
        '''
    html += '</div>'
    html += '<p class="text-muted"><em>Note: Full flags implementation in Phase 3</em></p>'

    return html
```

### 10.4 Include Routes in Main App

**File:** `app/main.py` (modifications)

Add these lines to your existing `app/main.py`:

```python
# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import patient routes
from app.routes import patient

app = FastAPI(title="med-z1")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(patient.router)

# ... rest of existing code
```

**Testing the routes:**

```bash
# Start the FastAPI app
uvicorn app.main:app --reload

# In another terminal, test endpoints
curl http://localhost:8000/api/patient/current
curl "http://localhost:8000/api/patient/search?query=DOOR&search_type=name"
curl http://localhost:8000/api/patient/ICN100001/demographics
curl http://localhost:8000/api/patient/ICN100001/flags

# Test with VA V-format ICN
curl http://localhost:8000/api/patient/1016V123456/demographics
```

---

## 11. Frontend Implementation

### 11.1 Modified `base.html` Topbar

**File:** `app/templates/base.html`

**Instructions:** Replace lines 70-96 (existing topbar) with the following:

```html
<!-- app/templates/base.html -->
<!-- Lines 70-96: Replace existing topbar with this: -->

<header class="topbar">
    <div class="topbar__left">
        <button
            class="btn btn--icon"
            type="button"
            data-toggle-sidebar
            aria-label="Toggle sidebar"
        >
            ☰
        </button>

        <!-- HTMX-powered patient header partial -->
        <div
            id="patient-header-container"
            hx-get="/api/patient/current"
            hx-trigger="load"
            hx-swap="innerHTML"
        >
            <!-- Initial loading state -->
            <div class="patient-header">
                <div class="patient-header__title">Loading patient context...</div>
            </div>
        </div>
    </div>

    <div class="topbar__right">
        <button
            id="btn-patient-flags"
            class="btn btn--secondary"
            data-modal-open="patient-flags-modal"
            disabled
            title="View patient flags (Phase 3)"
        >
            <i class="fa-regular fa-flag"></i>
            View Patient Flags
            <span id="flags-badge" class="badge badge--warning" style="display:none;">0</span>
        </button>

        <button
            id="btn-select-patient"
            class="btn btn--primary"
            data-modal-open="patient-search-modal"
        >
            <i class="fa-regular fa-user"></i>
            Select Patient
        </button>

        <button
            id="btn-refresh-patient"
            class="btn btn--secondary"
            hx-get="/api/patient/refresh"
            hx-target="#patient-header-container"
            hx-swap="innerHTML"
            title="Refresh patient context from CCOW vault"
        >
            <i class="fa-regular fa-refresh"></i>
            Refresh
        </button>
    </div>
</header>

<!-- Include modal templates at end of body, before closing </body> tag -->
<!-- Add these lines just before </body> -->
{% include "partials/patient_search_modal.html" %}
{% include "partials/patient_flags_modal.html" %}
```

### 11.2 Patient Header Partial

**File:** `app/templates/partials/patient_header.html`

```html
<!-- app/templates/partials/patient_header.html -->

{% if patient %}
<div class="patient-header patient-header--active">
    <h1 class="patient-header__title">
        {{ patient.name_display }} ({{ patient.sex }}, {{ patient.age }})
    </h1>
    <p class="patient-header__subtitle">
        ICN: {{ patient.icn }} |
        SSN: ***-**-{{ patient.ssn_last4 }} |
        DOB: {{ patient.dob }} |
        Station: {{ patient.primary_station }}
        {% if patient.primary_station_name %}
        ({{ patient.primary_station_name }})
        {% endif %}
    </p>
</div>
<!-- Note: patient.icn may be "ICN100001" or "1016V123456" format -->

<script>
    // Enable/update patient flags button
    document.getElementById('btn-patient-flags').disabled = false;

    // Fetch flag count and update badge (production implementation)
    fetch('/api/patient/{{ patient.icn }}/flags')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('flags-badge');
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(err => console.error('Failed to load flag count:', err));
</script>

{% else %}
<div class="patient-header patient-header--empty">
    <h1 class="patient-header__title">
        No patient selected
    </h1>
    <p class="patient-header__subtitle">
        Click 'Select Patient' to begin
    </p>
</div>

<script>
    // Disable patient flags button
    document.getElementById('btn-patient-flags').disabled = true;
    document.getElementById('flags-badge').style.display = 'none';
</script>
{% endif %}
```

### 11.3 Patient Search Modal

**File:** `app/templates/partials/patient_search_modal.html`

```html
<!-- app/templates/partials/patient_search_modal.html -->

<div id="patient-search-modal" class="modal" style="display: none;">
    <div class="modal__overlay" data-modal-close="patient-search-modal"></div>
    <div class="modal__container">
        <div class="modal__header">
            <h2>Select Patient</h2>
            <button
                class="modal__close"
                data-modal-close="patient-search-modal"
                aria-label="Close"
            >
                &times;
            </button>
        </div>

        <div class="modal__body">
            <form class="patient-search-form">
                <div class="form-group">
                    <label for="search-query">Search by Name, ICN, or EDIPI</label>
                    <input
                        type="text"
                        id="search-query"
                        name="query"
                        class="form-control"
                        placeholder="Enter patient name, ICN, EDIPI..."
                        hx-get="/api/patient/search"
                        hx-trigger="keyup changed delay:500ms"
                        hx-target="#search-results"
                        hx-include="[name='search_type']"
                        autocomplete="off"
                    />
                </div>

                <div class="form-group">
                    <label>Search Type</label>
                    <div class="radio-group">
                        <label>
                            <input type="radio" name="search_type" value="name" checked>
                            Name
                        </label>
                        <label>
                            <input type="radio" name="search_type" value="icn">
                            ICN
                        </label>
                        <label>
                            <input type="radio" name="search_type" value="edipi">
                            EDIPI
                        </label>
                    </div>
                    <p class="form-help">Note: SSN search not available per VA policy</p>
                </div>
            </form>

            <div id="search-results" class="search-results">
                <p class="text-muted">Enter search criteria above</p>
            </div>
        </div>
    </div>
</div>
```

### 11.4 Patient Search Results Partial

**File:** `app/templates/partials/patient_search_results.html`

```html
<!-- app/templates/partials/patient_search_results.html -->

{% if results %}
<div class="search-results__list">
    {% for patient in results %}
    <div
        class="search-result-item"
        hx-post="/api/patient/set-context"
        hx-vals='{"icn": "{{ patient.icn }}"}'
        hx-target="#patient-header-container"
        hx-swap="innerHTML"
        data-modal-close="patient-search-modal"
        tabindex="0"
        role="button"
    >
        <div class="search-result-item__main">
            <strong>{{ patient.name_display }}</strong>
            <span class="text-muted">({{ patient.sex }}, {{ patient.age }})</span>
        </div>
        <div class="search-result-item__details">
            ICN: {{ patient.icn }} |
            SSN: ***-**-{{ patient.ssn_last4 }} |
            DOB: {{ patient.dob }} |
            Station: {{ patient.station }}
        </div>
    </div>
    {% endfor %}
</div>
{% elif query %}
<p class="text-muted">No patients found matching "{{ query }}"</p>
{% else %}
<p class="text-muted">Enter search criteria above</p>
{% endif %}
```

### 11.5 Patient Flags Modal (✅ Production Implementation)

**Status:** Phase 3 COMPLETE - Full production implementation with real data

**Files:**
- `app/templates/partials/patient_flags_modal.html` - Modal shell
- `app/templates/partials/patient_flags_content.html` - Flag cards display
- `app/templates/partials/flag_card.html` - Individual flag cards
- `app/templates/partials/flag_history.html` - Flag history timeline

**File:** `app/templates/partials/patient_flags_modal.html`

```html
<!-- app/templates/partials/patient_flags_modal.html -->
<!-- ✅ Production Implementation - Phase 3 Complete -->

<div id="patient-flags-modal" class="modal" style="display: none;">
    <div class="modal__overlay" data-modal-close="patient-flags-modal"></div>
    <div class="modal__container modal__container--large">
        <div class="modal__header">
            <h2>Patient Flags</h2>
            <button
                class="modal__close"
                data-modal-close="patient-flags-modal"
                aria-label="Close"
            >
                &times;
            </button>
        </div>

        <div
            class="modal__body"
            id="patient-flags-content"
            hx-get="/api/patient/flags-content"
            hx-trigger="revealed"
            hx-swap="innerHTML"
        >
            <p class="text-muted">Loading patient flags...</p>
        </div>
    </div>
</div>
```

---

## 12. Styling & Interactions

### 12.1 CSS Additions

**File:** `app/static/styles.css`

**Instructions:** Add the following CSS to the end of your existing `styles.css`:

```css
/* ============================================
   Patient Header Styles
   ============================================ */

.patient-header {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0; /* Allow text truncation */
}

.patient-header__title {
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.2;
    margin: 0;
    color: var(--text-primary, #1a1a1a);
}

.patient-header--empty .patient-header__title {
    color: var(--text-muted, #666);
    font-weight: 600;
}

.patient-header__subtitle {
    font-size: 0.875rem;
    line-height: 1.4;
    margin: 0;
    color: var(--text-secondary, #555);
}

.patient-header--empty .patient-header__subtitle {
    color: var(--text-muted, #999);
    font-style: italic;
}

/* Badge for flag count */
.badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1;
    color: #fff;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 10px;
    margin-left: 0.5rem;
}

.badge--warning {
    background-color: #dc3545;
}

/* ============================================
   Modal Styles
   ============================================ */

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal__overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    cursor: pointer;
}

.modal__container {
    position: relative;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    z-index: 1001;
}

.modal__container--large {
    max-width: 900px;
}

.modal__header {
    padding: 1.5rem;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal__header h2 {
    margin: 0;
    font-size: 1.5rem;
}

.modal__close {
    background: none;
    border: none;
    font-size: 2rem;
    line-height: 1;
    cursor: pointer;
    color: #666;
    padding: 0;
    width: 2rem;
    height: 2rem;
}

.modal__close:hover {
    color: #000;
}

.modal__body {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
}

/* ============================================
   Patient Search Styles
   ============================================ */

.patient-search-form {
    margin-bottom: 1.5rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #333;
}

.form-help {
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.25rem;
    font-style: italic;
}

.form-control {
    width: 100%;
    padding: 0.5rem 0.75rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.form-control:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.radio-group {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.radio-group label {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-weight: normal;
}

.search-results {
    min-height: 200px;
}

.search-results__list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.search-result-item {
    padding: 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.search-result-item:hover,
.search-result-item:focus {
    background-color: #f5f5f5;
    border-color: #007bff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    outline: none;
}

.search-result-item__main {
    margin-bottom: 0.25rem;
}

.search-result-item__details {
    font-size: 0.875rem;
    color: #666;
}

.text-muted {
    color: #999;
    font-style: italic;
}

/* ============================================
   Patient Flags Styles (Phase 3)
   ============================================ */

.flags-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.flag-item {
    padding: 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #fff;
}

.flag-item--high-risk {
    border-left: 4px solid #dc3545;
    background-color: #fff5f5;
}

.flag-item h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    color: #dc3545;
}

.flag-item p {
    margin: 0.25rem 0;
    font-size: 0.875rem;
}

/* ============================================
   Responsive Adjustments
   ============================================ */

@media (max-width: 768px) {
    .patient-header__subtitle {
        font-size: 0.75rem;
    }

    .topbar__right {
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .btn {
        font-size: 0.875rem;
        padding: 0.5rem 0.75rem;
    }

    .modal__container {
        width: 95%;
        max-height: 90vh;
    }

    .radio-group {
        flex-direction: column;
        gap: 0.5rem;
    }
}

/* ============================================
   Accessibility Improvements
   ============================================ */

button:focus-visible,
a:focus-visible,
input:focus-visible,
.search-result-item:focus-visible {
    outline: 2px solid #007bff;
    outline-offset: 2px;
}

/* Ensure text meets WCAG AA contrast */
.patient-header__subtitle,
.search-result-item__details {
    color: #555; /* Ensures sufficient contrast */
}
```

### 12.2 JavaScript Additions

**File:** `app/static/app.js`

**Instructions:** Add the following JavaScript to the end of your existing `app.js`:

```javascript
/* ============================================
   Modal Handling
   ============================================ */

// Open modal
document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-modal-open]');
    if (trigger) {
        const modalId = trigger.getAttribute('data-modal-open');
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent background scroll

            // Focus first input if exists
            const firstInput = modal.querySelector('input, button');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }
});

// Close modal
document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-modal-close]');
    if (trigger) {
        const modalId = trigger.getAttribute('data-modal-close');
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scroll
        }
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal[style*="display: flex"]');
        modals.forEach(modal => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        });
    }
});

/* ============================================
   HTMX Event Listeners for Modal Integration
   ============================================ */

// Close modal after successful patient selection
document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.detail.target.id === 'patient-header-container') {
        // Close patient search modal if open
        const searchModal = document.getElementById('patient-search-modal');
        if (searchModal && searchModal.style.display === 'flex') {
            searchModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
});

// Clear search input when modal closes
document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-modal-close="patient-search-modal"]');
    if (trigger) {
        const searchInput = document.getElementById('search-query');
        if (searchInput) {
            searchInput.value = '';
        }
        const resultsDiv = document.getElementById('search-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = '<p class="text-muted">Enter search criteria above</p>';
        }
    }
});

/* ============================================
   Search Result Keyboard Navigation
   ============================================ */

document.addEventListener('keydown', (e) => {
    // Handle Enter key on search result items
    if (e.key === 'Enter' && e.target.classList.contains('search-result-item')) {
        e.target.click();
    }
});

/* ============================================
   Debug Helpers (Development Only)
   ============================================ */

// Log HTMX requests in console (helpful for debugging)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.body.addEventListener('htmx:beforeRequest', (e) => {
        console.log('HTMX Request:', e.detail.requestConfig.verb, e.detail.requestConfig.path);
    });

    document.body.addEventListener('htmx:afterSwap', (e) => {
        console.log('HTMX Swap complete:', e.detail.target.id);
    });

    document.body.addEventListener('htmx:responseError', (e) => {
        console.error('HTMX Error:', e.detail);
    });
}
```

---

# Part 3: Quality & Deployment

## 13. Testing Strategy

### 13.1 Quick Smoke Tests

**After Stage 1 (Backend):**

```bash
# Test database queries
python -c "
from app.db.patient import get_patient_demographics, search_patients
print('Testing get_patient_demographics...')
p = get_patient_demographics('ICN100001')
print(f'✓ Found patient: {p[\"name_display\"] if p else \"ERROR\"}')

# Test VA V-format
p_v = get_patient_demographics('1016V123456')
print(f'✓ Found patient (V-format): {p_v[\"name_display\"] if p_v else \"Not in DB\"}')

print('Testing search_patients...')
results = search_patients('DOOR', 'name')
print(f'✓ Found {len(results)} patients')
"

# Test CCOW client
python -c "
from app.utils.ccow_client import ccow_client
print('Testing CCOW client...')
patient = ccow_client.get_active_patient()
print(f'✓ Current patient: {patient or \"None\"}')
"

# Test API endpoints (with app running)
curl -s http://localhost:8000/api/patient/current | grep -q "patient-header" && echo "✓ /current works"
curl -s "http://localhost:8000/api/patient/search?query=DOOR&search_type=name" | grep -q "DOOREE" && echo "✓ /search works"
curl -s http://localhost:8000/api/patient/ICN100001/demographics | grep -q "ICN100001" && echo "✓ /demographics works"
```

**After Stage 2 (UI):**

1. Start app: `uvicorn app.main:app --reload`
2. Open browser: `http://localhost:8000`
3. Open DevTools Network tab
4. Verify HTMX request fires to `/api/patient/current`
5. Check patient header appears (or "No patient selected")

**After Stage 3 (Interactions):**

1. Click "Select Patient" → Modal opens
2. Type "DOOR" → Results appear after 500ms
3. Click patient → Header updates, modal closes
4. Click "Refresh Patient" → Header re-queries CCOW

### 13.2 Manual Testing Checklist

#### CCOW Integration
- [ ] Start app with CCOW running, patient set → Header shows patient
- [ ] Start app with CCOW running, no patient → Header shows "No patient selected"
- [ ] Start app with CCOW NOT running → Header shows "No patient selected" (graceful degradation)
- [ ] Start CCOW after app running → Refresh button updates header correctly
- [ ] Set patient in CCOW externally → Refresh button loads new patient

#### Patient Selection
- [ ] Click "Select Patient" → Modal opens
- [ ] Type in search field → Results appear after 500ms delay
- [ ] Type < 2 characters → No results shown
- [ ] Click patient in results → Modal closes, header updates, CCOW updated
- [ ] Click outside modal (overlay) → Modal closes
- [ ] Press ESC key → Modal closes
- [ ] Change search type radio buttons → Search re-executes with new type
- [ ] Search by name: "DOOR" → Returns correct results
- [ ] Search by ICN: "ICN100001" → Returns exact match
- [ ] Search by ICN: "1016V123456" → Returns exact match (VA V-format)
- [ ] Search by EDIPI: (not implemented) → Shows message

#### Refresh Button
- [ ] Click "Refresh Patient" with patient in CCOW → Header updates
- [ ] Click "Refresh Patient" with no patient in CCOW → Header shows "No patient selected"
- [ ] Change patient in CCOW vault externally → Refresh button loads new patient

#### Patient Flags (✅ Production - Phase 3 Complete)
- [x] With no patient selected → "View Patient Flags" button disabled
- [x] With patient selected → Button enabled
- [x] Click "View Patient Flags" → Modal opens with real patient flag data
- [x] Close flags modal → Modal closes properly
- [x] Badge shows actual flag count from database
- [x] Flag history lazy loading works
- [x] Review status indicators display correctly

#### Responsive Design
- [ ] Test on desktop (1920x1080)
- [ ] Test on laptop (1366x768)
- [ ] Test on tablet (768x1024)
- [ ] Test on mobile (375x667)
- [ ] Patient header wraps appropriately on narrow screens
- [ ] Buttons stack/wrap on very narrow screens

#### Accessibility
- [ ] Tab through all interactive elements (keyboard navigation works)
- [ ] Shift+Tab navigates backwards correctly
- [ ] ESC key closes modals
- [ ] ARIA labels present on icon-only buttons
- [ ] Screen reader can read patient demographics
- [ ] Color contrast meets WCAG AA standards
- [ ] Focus indicators visible on all interactive elements
- [ ] Enter key activates search result items

#### Error Scenarios
- [ ] CCOW vault returns 500 error → Graceful fallback
- [ ] Search endpoint times out → Error handling
- [ ] Set context fails → User notified
- [ ] Invalid ICN provided → Appropriate error handling
- [ ] PostgreSQL connection fails → Graceful degradation

### 13.3 Automated Testing (Future)

**File:** `tests/test_patient_routes.py`

```python
# tests/test_patient_routes.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_current_patient_no_ccow():
    """Test patient header when no CCOW patient set."""
    response = client.get("/api/patient/current")
    assert response.status_code == 200
    assert "No patient selected" in response.text


def test_search_patients_by_name():
    """Test patient search by name."""
    response = client.get("/api/patient/search?query=DOOR&search_type=name")
    assert response.status_code == 200
    assert "DOOREE" in response.text or "No patients found" in response.text


def test_search_patients_short_query():
    """Test that short queries return no results."""
    response = client.get("/api/patient/search?query=D&search_type=name")
    assert response.status_code == 200
    assert "Enter search criteria" in response.text


def test_get_patient_demographics_json():
    """Test patient demographics JSON endpoint."""
    response = client.get("/api/patient/ICN100001/demographics")
    # Will be 404 if patient doesn't exist, or 200 with data
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "icn" in data


def test_get_patient_flags_json():
    """Test patient flags JSON endpoint (✅ Production - Phase 3 Complete)."""
    response = client.get("/api/patient/ICN100001/flags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Returns array of flag objects
    if len(data) > 0:
        assert "assignment_id" in data[0]
        assert "flag_name" in data[0]
```

Run tests:
```bash
pytest tests/test_patient_routes.py -v
```

---

## 14. Common Pitfalls & Troubleshooting

### 14.1 HTMX Issues

**Problem:** HTMX requests not firing

**Symptoms:**
- Patient header shows "Loading patient context..." indefinitely
- Network tab shows no requests to `/api/patient/current`

**Solutions:**
1. Verify HTMX is loaded in `base.html`: `<script src="https://unpkg.com/htmx.org@1.9.10"></script>`
2. Check browser console for JavaScript errors
3. Verify `hx-get`, `hx-trigger`, `hx-target` attributes are correct
4. Check `hx-swap` is set correctly (`innerHTML` for most cases)

**Debug Command:**
```javascript
// In browser console
document.body.addEventListener('htmx:beforeRequest', (e) => console.log('HTMX:', e.detail));
```

---

**Problem:** HTMX target not found

**Symptoms:**
- Console error: "Target element not found"
- Header doesn't update after patient selection

**Solutions:**
1. Verify `id="patient-header-container"` exists in HTML
2. Check `hx-target="#patient-header-container"` spelling matches exactly
3. Ensure target element exists before HTMX tries to swap

---

**Problem:** Modal doesn't close after patient selection

**Symptoms:**
- Patient header updates, but modal stays open
- Have to click "X" or ESC to close

**Solutions:**
1. Verify `data-modal-close="patient-search-modal"` attribute on search result items
2. Check JavaScript event listener for `htmx:afterSwap` is registered
3. Ensure modal ID matches in data attribute

**Fix:**
```javascript
// In app.js - ensure this listener exists
document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.detail.target.id === 'patient-header-container') {
        const searchModal = document.getElementById('patient-search-modal');
        if (searchModal && searchModal.style.display === 'flex') {
            searchModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
});
```

### 14.2 CSS Issues

**Problem:** Modal overlay z-index wrong (modal behind content)

**Symptoms:**
- Can't click modal content
- Modal appears behind sidebar or other elements

**Solutions:**
1. Verify `.modal` has `z-index: 1000`
2. Verify `.modal__container` has `z-index: 1001`
3. Check no other elements have higher z-index
4. Ensure `.modal__overlay` is positioned absolutely within `.modal`

**CSS Fix:**
```css
.modal {
    z-index: 1000;
    position: fixed;
}

.modal__overlay {
    z-index: 1000;
}

.modal__container {
    z-index: 1001;
    position: relative;
}
```

---

**Problem:** Badge not hiding when count is 0

**Symptoms:**
- Badge shows "0" instead of hiding
- Badge visible even when no flags

**Solutions:**
1. Verify JavaScript sets `display: 'none'` when count is 0
2. Check `#flags-badge` ID matches in JavaScript

**JavaScript Fix:**
```javascript
if (data.count > 0) {
    badge.textContent = data.count;
    badge.style.display = 'inline-block';
} else {
    badge.style.display = 'none'; // Ensure this line exists
}
```

### 14.3 PostgreSQL Issues

**Problem:** Database connection fails

**Symptoms:**
- Error: "psycopg2.OperationalError: could not connect to server"
- Patient search returns no results even for known patients

**Solutions:**
1. Verify PostgreSQL container is running: `docker ps | grep postgres16`
2. Check DATABASE_URL in `.env` is correct
3. Test connection: `psql -h localhost -U postgres -d medz1 -c "SELECT 1"`
4. Verify `patient_demographics` table exists: `\dt` in psql

**Connection String Format:**
```bash
# .env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/medz1
```

---

**Problem:** Search returns no results for existing patients

**Symptoms:**
- Search by name "DOOR" returns empty
- Know patients exist in database

**Solutions:**
1. Verify patients in database: `SELECT COUNT(*) FROM patient_demographics;`
2. Check column names match SQL query: `\d patient_demographics`
3. Verify search query uses `ILIKE` for case-insensitive: `name_last ILIKE '%DOOR%'`
4. Check data exists: `SELECT name_last, name_first FROM patient_demographics LIMIT 5;`

**SQL Test:**
```sql
-- Test search query directly
SELECT name_display, icn FROM patient_demographics
WHERE name_last ILIKE '%DOOR%' OR name_first ILIKE '%DOOR%';
```

### 14.4 CCOW Integration Issues

**Problem:** CCOW service not responding

**Symptoms:**
- Patient header always shows "No patient selected"
- Console errors about connection refused

**Solutions:**
1. Verify CCOW service is running: `curl http://localhost:8001/docs`
2. Check CCOW_BASE_URL in `.env`: `CCOW_BASE_URL=http://localhost:8001`
3. Verify CCOW_ENABLED is true: `CCOW_ENABLED=true`
4. Check CCOW service logs for errors

**Test CCOW:**
```bash
# Test CCOW service directly
curl http://localhost:8001/ccow/active-patient

# Should return:
# 404 if no patient set
# 200 with patient_id if set
```

---

**Problem:** CCOW updates but patient header doesn't refresh

**Symptoms:**
- Set patient in CCOW via curl
- Patient header still shows "No patient selected"
- Refresh button doesn't work

**Solutions:**
1. Click "Refresh Patient" button (doesn't auto-refresh)
2. Verify Refresh button has correct `hx-get` and `hx-target` attributes
3. Check network tab shows request to `/api/patient/refresh`

**Expected Behavior:**
- CCOW updates are NOT automatic (by design)
- User must click "Refresh Patient" to query CCOW

### 14.5 Search Functionality Issues

**Problem:** Search triggers too fast (every keystroke)

**Symptoms:**
- Network tab shows request on every key press
- Search feels laggy

**Solutions:**
1. Verify `hx-trigger="keyup changed delay:500ms"` on search input
2. Check delay value (500ms is good balance)
3. Ensure `changed` modifier is present (prevents duplicate requests)

**Correct HTMX Attribute:**
```html
<input
    hx-get="/api/patient/search"
    hx-trigger="keyup changed delay:500ms"
    ...
/>
```

---

**Problem:** Changing search type doesn't trigger new search

**Symptoms:**
- Type "DOOR", get results
- Change from "Name" to "ICN"
- Results don't update

**Solutions:**
1. Verify `hx-include="[name='search_type']"` on search input
2. Check radio buttons have `name="search_type"` attribute
3. Add `hx-trigger="change"` to radio buttons

**Fix - Add to radio buttons:**
```html
<input
    type="radio"
    name="search_type"
    value="name"
    hx-get="/api/patient/search"
    hx-trigger="change"
    hx-include="#search-query"
    hx-target="#search-results"
>
```

---

## 15. Success Criteria

### 15.1 Functional Requirements

**Phase 2 - Complete (December 2025):**
- [x] Can search all 36 patients by name (case-insensitive)
- [x] Can search by ICN (exact match)
- [x] EDIPI search shows "not implemented" message (graceful)
- [x] Patient demographics display correctly in topbar
- [x] CCOW integration works (get, set, refresh)
- [x] Modals open and close smoothly
- [x] "View Patient Flags" button functional
- [x] No JavaScript console errors
- [x] No Python exceptions in logs

**Phase 3 - Complete (December 2025):**
- [x] Patient flags display real data from PostgreSQL
- [x] Flag badge count shows active flag count
- [x] Badge color coding (red for overdue flags)
- [x] National/Local flag categorization
- [x] Review status calculation (CURRENT, DUE SOON, OVERDUE)
- [x] Flag history lazy loading with HTMX
- [x] Sensitive narrative text display

**Performance - Complete:**
- [x] Search responds in < 500ms (fast user experience)
- [x] HTMX swaps are smooth (no visible flicker)
- [x] Responsive on mobile/tablet/desktop
- [x] Keyboard accessible (Tab, Enter, ESC work)

**Out of Scope (Future Enhancements):**
- ❌ SSN search functionality (removed per VA policy)
- ❌ Real-time CCOW polling (manual refresh only)
- ❌ Flag creation/editing interface

### 15.2 Non-Functional Requirements

**Performance - Complete:**
- [x] Initial page load < 2 seconds
- [x] Patient search < 500ms (database query time)
- [x] HTMX swap < 100ms (DOM update time)
- [x] No memory leaks (test with DevTools Performance tab)

**Accessibility - Complete:**
- [x] WCAG AA color contrast (use browser contrast checker)
- [x] Keyboard navigation works for all interactive elements
- [x] Screen reader compatible (test with VoiceOver/NVDA)
- [x] Focus indicators visible
- [x] ARIA labels present where needed

**Reliability - Complete:**
- [x] Graceful degradation when CCOW unavailable
- [x] Graceful degradation when PostgreSQL unavailable
- [x] Error messages are user-friendly (no stack traces)
- [x] Logs capture errors for debugging

**Maintainability - Complete:**
- [x] Code follows existing patterns
- [x] SQL queries are readable and commented
- [x] Templates use consistent naming
- [x] CSS follows BEM-like conventions

### 15.3 Integration Success

**Phase 1 → Phase 2 Integration - Complete:**
- [x] PostgreSQL `clinical.patient_demographics` table is queried successfully
- [x] All 36 patients from Phase 1 ETL are searchable
- [x] Data quality is good (no NULL name fields, valid ages)

**CCOW Integration - Complete:**
- [x] CCOW service is accessible from med-z1 app
- [x] Patient context can be set and retrieved
- [x] Errors are handled gracefully
- [x] CCOW v2.0: Multi-user context isolation implemented
- [x] Session-based context persistence implemented

**Phase 3 Integration - Complete:**
- [x] Database layer implemented: `app/db/patient_flags.py` (238 lines)
- [x] Templates complete: 4 flag-related template files
- [x] API endpoints complete: All flag routes return real data
- [x] ETL pipeline complete: Bronze → Silver → Gold → PostgreSQL
- [x] 15 patient flags in database (12 active)

---

## 16. Deployment Approach

### 16.1 Direct Cutover (Recommended)

**Strategy:** Replace old topbar with new topbar in one deployment

**Steps:**
1. Complete all Phase 2 implementation
2. Test thoroughly in development
3. Backup current `base.html`, `styles.css`, `app.js`
4. Deploy new files to production
5. Monitor for errors
6. Rollback if critical issues found (restore backups)

**Why Recommended:**
- Simpler deployment (no feature flag complexity)
- Users see consistent experience
- Easier to test (one code path)
- Faster iteration

**Rollback Plan:**
```bash
# If critical issues found
cp base.html.backup app/templates/base.html
cp styles.css.backup app/static/styles.css
cp app.js.backup app/static/app.js
# Restart app
```

### 16.2 Pre-Deployment Checklist

**Code Quality:**
- [ ] All tests pass: `pytest tests/`
- [ ] No Python syntax errors: `python -m py_compile app/**/*.py`
- [ ] No JavaScript errors in browser console
- [ ] No CSS validation errors

**Functionality:**
- [ ] All success criteria met (see Section 15)
- [ ] Manual testing checklist complete
- [ ] Tested on multiple browsers (Chrome, Firefox, Safari)
- [ ] Tested on multiple devices (desktop, tablet, mobile)

**Documentation:**
- [ ] Code comments added where needed
- [ ] README updated if necessary
- [ ] CLAUDE.md updated if new patterns introduced

**Database:**
- [ ] PostgreSQL `patient_demographics` table has 36 patients
- [ ] All patients have valid data (no NULLs in required fields)
- [ ] Indexes are present (see Phase 1 DDL)

**Services:**
- [ ] CCOW service is running and accessible
- [ ] PostgreSQL is running and accessible
- [ ] All containers are healthy: `docker ps`

### 16.3 Post-Deployment Verification

**Immediate (0-5 minutes):**
1. Load application: `http://localhost:8000`
2. Verify patient header loads (no errors)
3. Test patient search (select a patient)
4. Verify CCOW integration (refresh button)
5. Check browser console for errors
6. Check application logs for exceptions

**Short-term (5-30 minutes):**
1. Test all search types (name, ICN, EDIPI)
2. Test responsive design on mobile device
3. Test keyboard navigation
4. Test error scenarios (CCOW unavailable, etc.)
5. Monitor logs for any unexpected errors

**Long-term (1-24 hours):**
1. Monitor user feedback
2. Check error rates in logs
3. Monitor performance metrics
4. Verify no memory leaks (check process memory usage)

---

# Part 4: Reference

## 17. API Endpoint Reference

### 17.1 Endpoint Summary

| Endpoint | Method | Description | Response Type |
|----------|--------|-------------|---------------|
| `/api/patient/current` | GET | Get current patient from CCOW | HTML partial |
| `/api/patient/refresh` | GET | Refresh patient from CCOW | HTML partial |
| `/api/patient/set-context` | POST | Set patient context | HTML partial |
| `/api/patient/search` | GET | Search patients | HTML partial |
| `/api/patient/{icn}/demographics` | GET | Get patient demographics | JSON |
| `/api/patient/{icn}/flags` | GET | Get patient flags | JSON |
| `/api/patient/flags-content` | GET | Get flags modal content | HTML partial |

### 17.2 Detailed Specifications

#### GET /api/patient/current

**Description:** Get current patient from CCOW vault and return demographics partial HTML.

**Query Parameters:** None

**Response:** HTML partial (`patient_header.html` rendered)

**Logic:**
1. Query CCOW vault: `ccow_client.get_active_patient()`
2. If patient ICN found:
   - Query PostgreSQL: `get_patient_demographics(icn)`
   - Render `patient_header.html` with patient data
3. If no patient found:
   - Render `patient_header.html` with `patient=None`

**HTMX Usage:**
```html
<div
    id="patient-header-container"
    hx-get="/api/patient/current"
    hx-trigger="load"
    hx-swap="innerHTML"
>
```

**Example Response (Patient Found):**
```html
<div class="patient-header patient-header--active">
    <h1 class="patient-header__title">
        DOOREE, Adam (M, 45)
    </h1>
    <p class="patient-header__subtitle">
        ICN: ICN100001 | SSN: ***-**-6789 | DOB: 1980-01-02 | Station: 508
    </p>
</div>
<script>
    document.getElementById('btn-patient-flags').disabled = false;
    // ... flag count logic
</script>
```

**Example Response (No Patient):**
```html
<div class="patient-header patient-header--empty">
    <h1 class="patient-header__title">
        No patient selected
    </h1>
    <p class="patient-header__subtitle">
        Click 'Select Patient' to begin
    </p>
</div>
<script>
    document.getElementById('btn-patient-flags').disabled = true;
</script>
```

---

#### GET /api/patient/refresh

**Description:** Re-query CCOW vault and return updated demographics partial.

**Query Parameters:** None

**Response:** HTML partial (same as `/current`)

**Logic:** Identical to `GET /api/patient/current`

**HTMX Usage:**
```html
<button
    hx-get="/api/patient/refresh"
    hx-target="#patient-header-container"
    hx-swap="innerHTML"
>
    Refresh
</button>
```

---

#### POST /api/patient/set-context

**Description:** Set patient context in CCOW vault and return demographics partial.

**Form Data:**
- `icn` (required): Patient ICN to set

**Response:** HTML partial (`patient_header.html` rendered)

**Logic:**
1. Validate ICN from form data
2. Update CCOW vault: `ccow_client.set_active_patient(icn)`
3. Query PostgreSQL: `get_patient_demographics(icn)`
4. Render `patient_header.html` with patient data

**HTMX Usage:**
```html
<div
    class="search-result-item"
    hx-post="/api/patient/set-context"
    hx-vals='{"icn": "100001"}'
    hx-target="#patient-header-container"
    hx-swap="innerHTML"
>
```

**Error Responses:**
- `400` if ICN missing
- `404` if patient not found in database
- `500` if CCOW update fails

---

#### GET /api/patient/search

**Description:** Search for patients and return results partial HTML.

**Query Parameters:**
- `query` (required): Search query string (min 2 characters)
- `search_type` (required): Type of search - `name`, `icn`, or `edipi`

**Response:** HTML partial (`patient_search_results.html` rendered)

**Logic:**
1. If query < 2 characters: Return empty results
2. Query PostgreSQL: `search_patients(query, search_type, limit=20)`
3. Render results partial

**HTMX Usage:**
```html
<input
    hx-get="/api/patient/search"
    hx-trigger="keyup changed delay:500ms"
    hx-target="#search-results"
    hx-include="[name='search_type']"
/>
```

**Example Response (Results Found):**
```html
<div class="search-results__list">
    <div class="search-result-item" hx-post="/api/patient/set-context" ...>
        <div class="search-result-item__main">
            <strong>DOOREE, Adam</strong>
            <span class="text-muted">(M, 45)</span>
        </div>
        <div class="search-result-item__details">
            ICN: ICN100001 | SSN: ***-**-6789 | DOB: 1980-01-02 | Station: 508
        </div>
    </div>
    <!-- More results... -->
</div>
```

**Example Response (No Results):**
```html
<p class="text-muted">No patients found matching "XYZ"</p>
```

---

#### GET /api/patient/{icn}/demographics

**Description:** Get patient demographics as JSON (for API consumers).

**Path Parameters:**
- `icn` (required): Patient ICN

**Response:** JSON object with patient demographics

**Example Response:**
```json
{
  "patient_key": "ICN100001",
  "icn": "ICN100001",
  "ssn_last4": "6789",
  "name_last": "DOOREE",
  "name_first": "Adam",
  "name_middle": null,
  "name_display": "DOOREE, Adam",
  "dob": "1980-01-02",
  "age": 45,
  "sex": "M",
  "primary_station": "508",
  "primary_station_name": "Atlanta VA Medical Center",
  "source_system": "CDWWork",
  "last_updated": "2025-12-09 10:30:00"
}
```

**Error Responses:**
- `404` if patient not found

---

#### GET /api/patient/{icn}/flags

**Description:** ✅ Get patient flags as JSON (Phase 3 COMPLETE - Production).

**Path Parameters:**
- `icn` (required): Patient ICN

**Response:** JSON array with flag objects

**Example Response:**
```json
[
  {
    "assignment_id": 1,
    "flag_name": "High Risk for Suicide",
    "flag_type": "BEHAVIORAL",
    "category": "I",
    "category_name": "National",
    "assignment_date": "2024-01-15",
    "review_date": "2025-01-15",
    "owner_site": "508",
    "owner_site_name": "Atlanta VAMC",
    "review_status": "OVERDUE",
    "is_active": true
  }
]
```

**Implementation:** Queries `clinical.patient_flags` table in PostgreSQL via `app/db/patient_flags.py`.

---

#### GET /api/patient/flags-content

**Description:** ✅ Get patient flags modal content as HTML partial (Phase 3 COMPLETE - Production).

**Query Parameters:** None

**Response:** HTML with formatted flags

**Logic:**
1. Get current patient ICN from CCOW
2. If no patient: Return "No patient selected" message
3. Query flags: `get_patient_flags(icn)`
4. Render flags as HTML

**HTMX Usage:**
```html
<div
    id="patient-flags-content"
    hx-get="/api/patient/flags-content"
    hx-trigger="revealed"
    hx-swap="innerHTML"
>
```

**Example Response:**
```html
<div class="flags-list">
    <div class="flag-item flag-item--high-risk">
        <h3>High Risk for Suicide</h3>
        <p><strong>Category:</strong> BEHAVIORAL</p>
        <p><strong>Active Date:</strong> 2024-01-15</p>
        <p><strong>Review Date:</strong> 2025-01-15</p>
        <p>Patient flagged for suicide risk assessment</p>
    </div>
</div>
<p class="text-muted"><em>Note: Full flags implementation in Phase 3</em></p>
```

---

## 18. CSS Improvement Recommendations

### 18.1 CSS Custom Properties (Variables)

For future enhancement, consider adding CSS variables for easier theming:

```css
:root {
    /* Colors */
    --color-primary: #007bff;
    --color-secondary: #6c757d;
    --color-danger: #dc3545;
    --color-warning: #ffc107;

    --text-primary: #1a1a1a;
    --text-secondary: #555;
    --text-muted: #999;

    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;

    /* Borders */
    --border-radius: 4px;
    --border-color: #e0e0e0;

    /* Typography */
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.25rem;
    --font-size-xl: 1.5rem;
}
```

**Usage:**
```css
.patient-header__title {
    font-size: var(--font-size-lg);
    color: var(--text-primary);
}
```

**Benefits:**
- Easy theming (change one variable, updates everywhere)
- Consistent spacing and colors
- Easier maintenance

### 18.2 Animation & Transitions

For smoother UX, consider adding transitions:

```css
.modal {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}

.modal[style*="display: flex"] {
    opacity: 1;
}

.btn {
    transition: all 0.2s ease-in-out;
}

.search-result-item {
    transition: all 0.2s ease-in-out;
}
```

### 18.3 Utility Classes

For reusable styles:

```css
/* Text utilities */
.text-muted { color: var(--text-muted); }
.text-bold { font-weight: 700; }
.text-sm { font-size: var(--font-size-sm); }

/* Spacing utilities */
.mt-1 { margin-top: var(--spacing-sm); }
.mb-1 { margin-bottom: var(--spacing-sm); }
.p-2 { padding: var(--spacing-md); }

/* Display utilities */
.d-flex { display: flex; }
.d-none { display: none; }
.gap-1 { gap: var(--spacing-sm); }
```

---

# Appendices

## Appendix A: Data Flow Examples

### A.1 Complete Patient Selection Flow

**Scenario:** User searches for and selects a patient

**Step-by-step data flow:**

1. **User clicks "Select Patient" button**
   ```html
   <button data-modal-open="patient-search-modal">Select Patient</button>
   ```
   - JavaScript event listener fires
   - Modal CSS set to `display: flex`
   - Modal becomes visible

2. **User types "DOOR" in search input**
   ```html
   <input
       hx-get="/api/patient/search"
       hx-trigger="keyup changed delay:500ms"
       hx-include="[name='search_type']"
   />
   ```
   - User types: "D" (< 2 chars, no request)
   - User types: "DO" (2 chars, waits 500ms)
   - After 500ms delay: HTMX fires GET request
   - Request: `GET /api/patient/search?query=DO&search_type=name`

3. **Backend processes search request**
   ```python
   # app/routes/patient.py
   @router.get("/search")
   async def search_patients_endpoint(query="DO", search_type="name"):
       results = search_patients("DO", "name", limit=20)
       # Returns: [{"icn": "ICN100001", "name_display": "DOOREE, Adam", ...}, ...]
       return templates.TemplateResponse("partials/patient_search_results.html", {...})
   ```

4. **PostgreSQL query executes**
   ```python
   # app/db/patient.py
   def search_patients(query="DO", search_type="name"):
       sql_query = text("""
           SELECT icn, name_display, dob, age, sex, ssn_last4, primary_station
           FROM patient_demographics
           WHERE name_last ILIKE '%DO%' OR name_first ILIKE '%DO%'
           ORDER BY name_last, name_first
           LIMIT 20
       """)
       # Returns matching patients
   ```

5. **HTMX swaps search results**
   - Response HTML:
   ```html
   <div class="search-results__list">
       <div class="search-result-item" hx-post="/api/patient/set-context" ...>
           <strong>DOOREE, Adam</strong> (M, 45)
           ICN: ICN100001 | SSN: ***-**-6789 | ...
       </div>
       <!-- More results -->
   </div>
   ```
   - HTMX swaps this into `#search-results` div
   - User sees results instantly

6. **User clicks "DOOREE, Adam" result**
   ```html
   <div
       class="search-result-item"
       hx-post="/api/patient/set-context"
       hx-vals='{"icn": "ICN100001"}'
       hx-target="#patient-header-container"
       hx-swap="innerHTML"
       data-modal-close="patient-search-modal"
   >
   ```
   - HTMX fires POST request
   - Request: `POST /api/patient/set-context` with form data `icn=ICN100001`

7. **Backend updates CCOW and fetches demographics**
   ```python
   # app/routes/patient.py
   @router.post("/set-context")
   async def set_patient_context(icn="ICN100001"):
       # Update CCOW vault
       ccow_client.set_active_patient("ICN100001")

       # Fetch from PostgreSQL
       patient = get_patient_demographics("ICN100001")

       # Render patient header
       return templates.TemplateResponse("partials/patient_header.html", {
           "patient": patient
       })
   ```

8. **CCOW vault updated**
   ```
   PUT /ccow/active-patient
   Body: {"patient_id": "ICN100001", "set_by": "med-z1"}
   ```
   - CCOW service stores: `{"patient_id": "ICN100001", "timestamp": "...", "set_by": "med-z1"}`

9. **PostgreSQL query for full demographics**
   ```sql
   SELECT patient_key, icn, ssn_last4, name_last, name_first, ...
   FROM patient_demographics
   WHERE icn = 'ICN100001'
   ```
   - Returns complete patient record
   - Query also works with VA V-format: `WHERE icn = '1016V123456'`

10. **HTMX swaps patient header**
    - Response HTML:
    ```html
    <div class="patient-header patient-header--active">
        <h1>DOOREE, Adam (M, 45)</h1>
        <p>ICN: ICN100001 | SSN: ***-**-6789 | DOB: 1980-01-02 | Station: 508</p>
    </div>
    <script>
        document.getElementById('btn-patient-flags').disabled = false;
        // Fetch flag count...
    </script>
    ```
    - HTMX swaps this into `#patient-header-container`
    - Patient header updates instantly

11. **Modal closes automatically**
    ```javascript
    // app.js
    document.body.addEventListener('htmx:afterSwap', (e) => {
        if (e.detail.target.id === 'patient-header-container') {
            const searchModal = document.getElementById('patient-search-modal');
            searchModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    });
    ```
    - HTMX event fires after swap
    - JavaScript closes modal
    - User sees updated patient header

**Total time:** ~500-1000ms (user experience feels instant)

**Network requests:** 2 (search + set context)

**Database queries:** 2 (search + get demographics)

---

## Appendix B: Quick Start Guide

### B.1 30-Minute Quick Start

**Goal:** Get patient topbar working in 30 minutes

**Prerequisites:** Phase 1 complete, PostgreSQL with 36 patients

**Steps:**

1. **Create directories (2 min)**
   ```bash
   mkdir -p app/db app/routes app/utils app/templates/partials
   touch app/db/__init__.py app/routes/__init__.py app/utils/__init__.py
   ```

2. **Copy database layer (5 min)**
   - Copy `app/db/patient.py` from Section 10.1
   - Test: `python -c "from app.db.patient import get_patient_demographics; print(get_patient_demographics('100001'))"`

3. **Copy CCOW client (3 min)**
   - Copy `app/utils/ccow_client.py` from Section 10.2
   - Test: `python -c "from app.utils.ccow_client import ccow_client; print(ccow_client.get_active_patient())"`

4. **Copy patient routes (5 min)**
   - Copy `app/routes/patient.py` from Section 10.3
   - Update `app/main.py` to include router (Section 10.4)

5. **Copy patient header template (3 min)**
   - Copy `app/templates/partials/patient_header.html` from Section 11.2

6. **Update base.html (5 min)**
   - Backup: `cp app/templates/base.html app/templates/base.html.backup`
   - Replace topbar section with code from Section 11.1

7. **Copy search modal templates (5 min)**
   - Copy `patient_search_modal.html` from Section 11.3
   - Copy `patient_search_results.html` from Section 11.4
   - Copy `patient_flags_modal.html` from Section 11.5

8. **Add CSS (10 min)**
   - Copy CSS from Section 12.1 to end of `app/static/styles.css`

9. **Add JavaScript (5 min)**
   - Copy JavaScript from Section 12.2 to end of `app/static/app.js`

10. **Test (5 min)**
    ```bash
    # Start app
    uvicorn app.main:app --reload

    # Open browser
    open http://localhost:8000

    # Test patient search
    # - Click "Select Patient"
    # - Type "DOOR"
    # - Click patient
    # - Verify header updates
    ```

**Total: 30 minutes**

---

## Appendix C: Implementation Checklist

**Status:** ✅ All items complete (December 2025)

### C.1 Backend Setup - Complete
- [x] Create `app/db/__init__.py`
- [x] Create `app/db/patient.py` with database queries
- [x] Create `app/db/patient_flags.py` with production flag queries (Phase 3)
- [x] Test database queries in Python REPL
- [x] Create `app/utils/__init__.py`
- [x] Create `app/utils/ccow_client.py`
- [x] Test CCOW client in Python REPL
- [x] Create `app/routes/__init__.py`
- [x] Create `app/routes/patient.py` with all endpoints
- [x] Update `app/main.py` to include patient router
- [x] Test endpoints with curl/browser

### C.2 Frontend Templates - Complete
- [x] Create `app/templates/partials/` directory
- [x] Create `patient_header.html` partial
- [x] Create `patient_search_modal.html`
- [x] Create `patient_search_results.html`
- [x] Create `patient_flags_modal.html`
- [x] Create `patient_flags_content.html` (Phase 3)
- [x] Create `flag_card.html` (Phase 3)
- [x] Create `flag_history.html` (Phase 3)
- [x] Backup `app/templates/base.html`
- [x] Update `base.html` topbar section
- [x] Add modal includes to end of `base.html`

### C.3 Styling & Interactions - Complete
- [x] Backup `app/static/styles.css`
- [x] Add patient header styles to `styles.css`
- [x] Add modal styles to `styles.css`
- [x] Add search form styles to `styles.css`
- [x] Add flag styles to `styles.css` (Phase 3)
- [x] Add deceased indicator styles (additional feature)
- [x] Add responsive adjustments to `styles.css`
- [x] Backup `app/static/app.js`
- [x] Add modal handling JavaScript to `app.js`
- [x] Add HTMX event listeners to `app.js`

### C.4 Integration Testing - Complete
- [x] Start app: `uvicorn app.main:app --reload`
- [x] Test initial load (HTMX request fires)
- [x] Test "Select Patient" button (modal opens)
- [x] Test patient search by name
- [x] Test patient search by ICN
- [x] Test patient selection (header updates)
- [x] Test modal close (ESC key)
- [x] Test "Refresh Patient" button
- [x] Test CCOW integration (with service running)
- [x] Test CCOW v2.0 multi-user context isolation
- [x] Test CCOW graceful fallback (with service stopped)
- [x] Test patient flags display (Phase 3)
- [x] Test flag history lazy loading (Phase 3)

### C.5 Quality Assurance - Complete
- [x] Test on desktop browser (1920x1080)
- [x] Test on mobile browser (375x667)
- [x] Test keyboard navigation (Tab, Enter, ESC)
- [x] Check browser console (no errors)
- [x] Check application logs (no exceptions)
- [x] Test all success criteria (Section 15)
- [x] Review code for security issues
- [x] Review code for accessibility issues

### C.6 Documentation - Complete
- [x] Update README if needed
- [x] Update CLAUDE.md with new patterns
- [x] Document configuration changes
- [x] Create patient-flags-design.md (Phase 3)
- [x] Create ccow-v2-implementation-summary.md
- [x] Note deviations from design doc

---

## Appendix D: Document History

| Version | Date       | Author | Notes                                      |
|---------|------------|--------|--------------------------------------------|
| v1.0    | 2025-12-07 | Chuck  | Initial specification for topbar redesign  |
| v2.0    | 2025-12-09 | Chuck  | Comprehensive update with implementation guidance<br>- Renamed to patient-topbar-design.md<br>- Added development process overview<br>- Added prerequisites and setup section<br>- Added implementation strategy section<br>- Removed SSN search per VA policy<br>- Updated all code to use real PostgreSQL<br>- Marked patient flags as Phase 3<br>- Added complete data flow examples<br>- Added testing strategy with smoke tests<br>- Added common pitfalls section<br>- Added success criteria section<br>- Updated to direct cutover deployment<br>- Reorganized into 4 parts + appendices |
| v3.0    | 2026-01-21 | Chuck | Implementation status update<br>- Marked Phase 2 as complete (December 2025)<br>- Marked Phase 3 (Patient Flags) as complete (December 2025)<br>- Marked CCOW v2.0 as complete (December 2025)<br>- Added deceased patient indicator documentation<br>- Updated all success criteria and checklists to checked status<br>- Removed obsolete "Phase 3 placeholder" references<br>- Updated API endpoint documentation with production status<br>- Added cross-references to new documentation<br>- Updated Section 10 with production code references<br>- Comprehensive accuracy review for current implementation |

---

**End of Document**

**For questions or clarifications, refer to:**
- `implementation-roadmap.md` - Overall project phases and strategy
- `ccow-vault-design.md` - CCOW Context Vault technical specification
- `CLAUDE.md` - Project-wide development guidance

**Implementation support:**
- Phase 1 complete: ETL pipeline with 36 patients in PostgreSQL
- Phase 2 (this document): Topbar UI with real data
- Phase 3 (next): Patient flags full implementation
