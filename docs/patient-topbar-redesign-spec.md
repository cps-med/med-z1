# Patient-Aware Topbar Redesign – Technical Specification

December 7, 2025 • Document version v1.0

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Requirements Summary](#2-requirements-summary)
3. [Recommended Architecture](#3-recommended-architecture)
4. [Visual Design & Layout](#4-visual-design--layout)
5. [File Structure & New Files](#5-file-structure--new-files)
6. [Backend API Endpoints](#6-backend-api-endpoints)
7. [Implementation Details](#7-implementation-details)
8. [CSS Additions](#8-css-additions)
9. [JavaScript for Modal Handling](#9-javascript-for-modal-handling)
10. [Backend Route Implementation](#10-backend-route-implementation)
11. [Implementation Checklist](#11-implementation-checklist)
12. [CSS Improvement Recommendations](#12-css-improvement-recommendations)
13. [Testing Strategy](#13-testing-strategy)
14. [Rollout Plan](#14-rollout-plan)
15. [Summary & Next Steps](#15-summary--next-steps)

---

## 1. Executive Summary

This specification outlines the redesign of `app/templates/base.html` topbar to display CCOW-synchronized patient demographics and provide action buttons for patient flags and patient selection. The implementation will use HTMX for dynamic updates, modals for patient selection/flags, and follow the existing FastAPI + Jinja2 + HTMX architecture.

### 1.1 Key Objectives

- Display active patient demographics in topbar (name, ICN, SSN, DOB, age, sex, station)
- Integrate with CCOW Context Vault for patient context synchronization
- Provide patient search capability via modal dialog
- Provide patient flags viewing via modal dialog
- Support manual refresh of patient context from CCOW vault
- Maintain existing UI/UX patterns and styling conventions

### 1.2 Scope

**In Scope:**
- Topbar redesign with patient demographics area
- CCOW vault integration on application startup
- Patient search modal with search results
- Patient flags modal (placeholder implementation)
- Manual "Refresh Patient" functionality
- HTMX-powered dynamic updates
- Responsive design

**Out of Scope (Future Enhancements):**
- Connection to real serving database (using mock data initially)
- Advanced patient search filters
- Patient flags detailed implementation
- Real-time CCOW context updates (polling/WebSocket)
- Multi-user context isolation
- Session-based patient context persistence

---

## 2. Requirements Summary

### 2.1 Patient Demographics Display (Upper Left)

**Format:** Two-line display
- **Line 1:** `DOOREE, Adam (M, 45)` - Larger, bold text (like current `header_title`)
- **Line 2:** `ICN: 100001 | SSN: ***-**-6789 | DOB: 1980-01-02 | Station: 508` - Smaller text (like current `header_subtitle`)

**No Patient State:** Prominent call-to-action
- **Line 1:** "No patient selected" - Larger, bold text (muted color)
- **Line 2:** "Click 'Select Patient' to begin" - Smaller text (muted, italic)

### 2.2 Action Buttons (Upper Right)

**Button 1: "View Patient Flags"**
- Opens modal/dialog overlay with flag details
- Disabled (grayed out) when no patient is active
- Shows badge with flag count when flags are present
- Badge color: Red/warning color

**Button 2: "Select Patient"**
- Opens modal/dialog overlay with patient search form
- Always enabled
- Search results display within modal
- User selects patient, clicks to set CCOW context

**Button 3: "Refresh Patient"**
- Re-queries CCOW vault to refresh patient context
- Always enabled
- Updates patient demographics display via HTMX

### 2.3 CCOW Integration Behavior

**On Application Startup:**
1. Query CCOW vault (`GET /ccow/active-patient`)
2. If patient context exists:
   - Fetch patient demographics from serving DB (using ICN from vault)
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

---

## 3. Recommended Architecture

### 3.1 Topbar Structure Recommendation

**Recommended Approach: HTMX-powered partial template**

**Rationale:**
- **Dynamic Updates**: Patient demographics need to update when user selects a patient or clicks "Refresh Patient" without full page reload
- **Separation of Concerns**: Patient header logic isolated from base template
- **Reusability**: Patient header partial can be reused if needed elsewhere
- **HTMX Integration**: Leverages existing HTMX dependency (already loaded in `base.html:14`)
- **Performance**: Avoids full page reloads, only swaps the patient header section
- **Maintainability**: Easier to test and modify patient header independently

### 3.2 Template Structure

```
app/templates/
  base.html                          # Main layout (modified topbar)
  partials/
    patient_header.html               # Patient demographics display (HTMX target)
    patient_search_modal.html         # Patient search modal
    patient_search_results.html       # Search results partial (HTMX target)
    patient_flags_modal.html          # Patient flags modal
```

### 3.3 Data Flow Architecture

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
        │ from serving DB│      │ selected" message│
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


┌─────────────────────────────────────────────────────────────────┐
│                   Patient Selection Flow                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ User clicks      │
                    │ "Select Patient" │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Modal opens      │
                    │ (JavaScript)     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │ User types search query│
                    │ (HTMX triggers on      │
                    │ keyup with 500ms delay)│
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ GET /api/patient/search  │
                    │ ?query=...&search_type=..│
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ Search results rendered  │
                    │ (patient_search_results) │
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ User clicks a patient    │
                    │ (HTMX triggers POST)     │
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ POST /api/patient/       │
                    │      set-context         │
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ Update CCOW Vault        │
                    │ PUT /ccow/active-patient │
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ Fetch patient demographics│
                    │ from serving DB          │
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ Render patient_header.html│
                    │ with patient data        │
                    └────────┬─────────────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ HTMX swaps patient header│
                    │ Modal closes (JavaScript)│
                    └──────────────────────────┘
```

---

## 4. Visual Design & Layout

### 4.1 Topbar Layout (Wireframe)

**With Active Patient:**
```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  ☰  │ DOOREE, Adam (M, 45)                       │ [View Patient Flags ②]       │
│     │ ICN: 100001 | SSN: ***-**-6789 |           │ [Select Patient]              │
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

### 4.2 Button States

| Button              | No Patient | Patient (No Flags) | Patient (With Flags) |
|---------------------|------------|--------------------|-----------------------|
| View Patient Flags  | Disabled   | Enabled            | Enabled + Badge       |
| Select Patient      | Enabled    | Enabled            | Enabled               |
| Refresh Patient     | Enabled    | Enabled            | Enabled               |

### 4.3 Modal Layouts

**Patient Search Modal:**
```
┌─────────────────────────────────────────────────────┐
│  Select Patient                                  ✕  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Search by Name, SSN, ICN, or EDIPI                 │
│  ┌───────────────────────────────────────────────┐  │
│  │ Enter patient name, SSN, ICN...               │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  Search Type: ○ Name  ○ SSN  ○ ICN  ○ EDIPI         │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │ DOOREE, Adam (M, 45)                          │  │
│  │ ICN: 100001 | SSN: ***-**-6789 | DOB: ...     │  │
│  ├───────────────────────────────────────────────┤  │
│  │ MIIFAA, Barry (F, 50)                         │  │
│  │ ICN: 100002 | SSN: ***-**-4321 | DOB: ...     │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Patient Flags Modal:**
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
│  ┌───────────────────────────────────────────────┐  │
│  │ ⚠ Missing Appointments - 3 in last 6 months   │  │
│  │ Category: ADMINISTRATIVE                      │  │
│  │ ...                                           │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 5. File Structure & New Files

### 5.1 Files to Create

```
app/
  templates/
    partials/
      patient_header.html           # NEW - Patient demographics partial
      patient_search_modal.html     # NEW - Patient search modal
      patient_search_results.html   # NEW - Search results partial
      patient_flags_modal.html      # NEW - Patient flags modal
  routes/
    patient.py                      # NEW - Patient-related routes
  utils/
    ccow_client.py                  # NEW - CCOW HTTP client
  static/
    styles.css                      # MODIFY - Add patient header styles
    app.js                          # MODIFY - Add modal handling
```

### 5.2 Files to Modify

```
app/
  templates/
    base.html                       # MODIFY - Update topbar structure
  main.py                          # MODIFY - Include patient routes
```

### 5.3 Directory Structure (Complete)

```
med-z1/
  app/
    templates/
      base.html
      partials/
        patient_header.html           ← NEW
        patient_search_modal.html     ← NEW
        patient_search_results.html   ← NEW
        patient_flags_modal.html      ← NEW
    routes/
      __init__.py
      patient.py                      ← NEW
    utils/
      __init__.py
      ccow_client.py                  ← NEW
    static/
      styles.css                      ← MODIFY
      app.js                          ← MODIFY
      images/
    main.py                           ← MODIFY
  docs/
    patient-topbar-redesign-spec.md   ← THIS DOCUMENT
    med-z1-plan.md
    ccow-vault-design.md
```

---

## 6. Backend API Endpoints

### 6.1 Required Endpoints Summary

| Endpoint                        | Method | Description                                    |
|---------------------------------|--------|------------------------------------------------|
| `/api/patient/current`          | GET    | Get current patient from CCOW, return HTML     |
| `/api/patient/refresh`          | GET    | Re-query CCOW vault, return HTML               |
| `/api/patient/set-context`      | POST   | Set patient context in CCOW, return HTML       |
| `/api/patient/search`           | GET    | Search patients, return HTML results           |
| `/api/patient/{icn}/demographics` | GET  | Get patient demographics JSON                  |
| `/api/patient/{icn}/flags`      | GET    | Get patient flags JSON                         |
| `/api/patient/flags-content`    | GET    | Get patient flags modal content HTML           |

### 6.2 Endpoint Details

#### 6.2.1 Get Current Patient

```
GET /api/patient/current
```

**Description:** Get current patient from CCOW vault and return demographics partial HTML.

**Called:** On initial page load via HTMX (`hx-trigger="load"`)

**Response:** HTML partial (`patient_header.html` rendered)

**Logic:**
1. Query CCOW vault: `GET /ccow/active-patient`
2. If patient found (200 response with ICN):
   - Fetch patient demographics from serving DB using ICN
   - Render `patient_header.html` with `patient` data
3. If no patient (404 response):
   - Render `patient_header.html` with `patient=None`
4. If CCOW error:
   - Log error
   - Render `patient_header.html` with `patient=None`

---

#### 6.2.2 Refresh Patient

```
GET /api/patient/refresh
```

**Description:** Re-query CCOW vault and return updated demographics partial.

**Called:** When user clicks "Refresh Patient" button

**Response:** HTML partial (`patient_header.html` rendered)

**Logic:** Same as `GET /api/patient/current`

---

#### 6.2.3 Set Patient Context

```
POST /api/patient/set-context
Body: { "icn": "100001" }
```

**Description:** Set patient context in CCOW vault and return demographics partial.

**Called:** When user selects a patient from search results

**Response:** HTML partial (`patient_header.html` rendered)

**Logic:**
1. Validate ICN from request body
2. Update CCOW vault: `PUT /ccow/active-patient` with `{"patient_id": icn, "set_by": "med-z1"}`
3. Fetch patient demographics from serving DB
4. Render `patient_header.html` with patient data

---

#### 6.2.4 Search Patients

```
GET /api/patient/search?query={query}&search_type={name|ssn|icn|edipi}
```

**Description:** Search for patients and return results partial HTML.

**Called:** Via HTMX from patient search modal input (`hx-trigger="keyup changed delay:500ms"`)

**Response:** HTML partial (`patient_search_results.html` rendered)

**Query Parameters:**
- `query` (string): Search query string
- `search_type` (string): Type of search - `name`, `ssn`, `icn`, or `edipi`

**Logic:**
1. If query length < 2: Return empty results
2. Query serving DB based on `search_type`:
   - `name`: Match on patient name (case-insensitive, partial match)
   - `ssn`: Match on last 4 digits of SSN
   - `icn`: Exact match on ICN
   - `edipi`: Exact match on EDIPI
3. Return up to 20 matching patients
4. Render `patient_search_results.html` with results

**Example Response Data:**
```json
{
  "results": [
    {
      "icn": "100001",
      "name_display": "DOOREE, Adam",
      "sex": "M",
      "age": 45,
      "dob": "1980-01-02",
      "ssn_last4": "6789",
      "station": "508"
    },
    ...
  ],
  "query": "DOOREE"
}
```

---

#### 6.2.5 Get Patient Demographics (JSON)

```
GET /api/patient/{icn}/demographics
```

**Description:** Get patient demographics as JSON (for future API use).

**Response:** JSON object with patient demographics

**Example Response:**
```json
{
  "icn": "100001",
  "name_display": "DOOREE, Adam",
  "sex": "M",
  "age": 45,
  "dob": "1980-01-02",
  "ssn_last4": "6789",
  "primary_station": "508",
  "primary_station_name": "Portland VA Medical Center"
}
```

---

#### 6.2.6 Get Patient Flags (JSON)

```
GET /api/patient/{icn}/flags
```

**Description:** Get patient flags as JSON.

**Response:** JSON object with flags array and count

**Example Response:**
```json
{
  "flags": [
    {
      "flag_name": "High Risk for Suicide",
      "category": "BEHAVIORAL",
      "narrative": "Patient flagged for suicide risk assessment",
      "active_date": "2024-01-15",
      "review_date": "2025-01-15"
    },
    {
      "flag_name": "Missing Appointments",
      "category": "ADMINISTRATIVE",
      "narrative": "Patient has missed 3 appointments in last 6 months",
      "active_date": "2024-06-01",
      "review_date": null
    }
  ],
  "count": 2
}
```

---

#### 6.2.7 Get Patient Flags Modal Content

```
GET /api/patient/flags-content
```

**Description:** Get patient flags modal content (HTML partial).

**Called:** When patient flags modal is opened (`hx-trigger="revealed"`)

**Response:** HTML partial with formatted flags

**Logic:**
1. Get current patient ICN from CCOW vault
2. If no patient: Return "No active patient selected" message
3. Fetch patient flags from serving DB
4. Render flags as HTML with appropriate styling

---

## 7. Implementation Details

### 7.1 Modified `base.html` Topbar

**File:** `app/templates/base.html`

**Changes:** Replace lines 70-96 with new topbar structure

```html
<!-- app/templates/base.html -->
<!-- Lines 70-96 will be replaced with: -->

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
{% include "partials/patient_search_modal.html" %}
{% include "partials/patient_flags_modal.html" %}
```

### 7.2 Patient Header Partial

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

<script>
    // Enable/update patient flags button
    document.getElementById('btn-patient-flags').disabled = false;

    // Fetch flag count and update badge
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

### 7.3 Patient Search Modal

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
                    <label for="search-query">Search by Name, SSN, ICN, or EDIPI</label>
                    <input
                        type="text"
                        id="search-query"
                        name="query"
                        class="form-control"
                        placeholder="Enter patient name, SSN, ICN..."
                        hx-get="/api/patient/search"
                        hx-trigger="keyup changed delay:500ms"
                        hx-target="#search-results"
                        hx-include="[name='search_type']"
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
                            <input type="radio" name="search_type" value="ssn">
                            SSN
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
                </div>
            </form>

            <div id="search-results" class="search-results">
                <p class="text-muted">Enter search criteria above</p>
            </div>
        </div>
    </div>
</div>
```

### 7.4 Patient Search Results Partial

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

### 7.5 Patient Flags Modal (Placeholder)

**File:** `app/templates/partials/patient_flags_modal.html`

```html
<!-- app/templates/partials/patient_flags_modal.html -->

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
            <p>Loading patient flags...</p>
        </div>
    </div>
</div>
```

---

## 8. CSS Additions

### 8.1 Patient Header Styles

**File:** `app/static/styles.css` (add to end of file)

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

.search-result-item:hover {
    background-color: #f5f5f5;
    border-color: #007bff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
}
```

---

## 9. JavaScript for Modal Handling

### 9.1 Modal Functions

**File:** `app/static/app.js` (add to end of file)

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
```

---

## 10. Backend Route Implementation

### 10.1 CCOW Client Utility

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
        Retrieve the current patient_id from CCOW.

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

### 10.2 Patient Routes

**File:** `app/routes/patient.py`

```python
# app/routes/patient.py

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.utils.ccow_client import ccow_client
# from app.db import get_patient_demographics, search_patients, get_patient_flags
# ^ Placeholder - implement when serving DB is ready

router = APIRouter(prefix="/api/patient", tags=["patient"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/current", response_class=HTMLResponse)
async def get_current_patient(request: Request):
    """
    Get current patient from CCOW vault and return demographics partial.
    Called on initial page load via HTMX.
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

        # Fetch patient demographics from serving DB
        # patient = get_patient_demographics(patient_id)
        # TODO: Replace with actual DB query when serving DB is ready
        patient = {
            "icn": patient_id,
            "name_display": "DOOREE, Adam",
            "sex": "M",
            "age": 45,
            "dob": "1980-01-02",
            "ssn_last4": "6789",
            "primary_station": "508",
            "primary_station_name": "Portland VAMC"
        }

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

        # Fetch patient demographics
        # patient = get_patient_demographics(icn)
        # TODO: Replace with actual DB query
        patient = {
            "icn": icn,
            "name_display": "DOOREE, Adam",
            "sex": "M",
            "age": 45,
            "dob": "1980-01-02",
            "ssn_last4": "6789",
            "primary_station": "508",
            "primary_station_name": "Portland VAMC"
        }

        return templates.TemplateResponse(
            "partials/patient_header.html",
            {"request": request, "patient": patient}
        )

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
    Called via HTMX from patient search modal.
    """
    try:
        if not query or len(query) < 2:
            return templates.TemplateResponse(
                "partials/patient_search_results.html",
                {"request": request, "results": None, "query": None}
            )

        # Query serving DB for matching patients
        # results = search_patients(query, search_type)
        # TODO: Replace with actual DB query
        results = [
            {
                "icn": "100001",
                "name_display": "DOOREE, Adam",
                "sex": "M",
                "age": 45,
                "dob": "1980-01-02",
                "ssn_last4": "6789",
                "station": "508"
            },
            {
                "icn": "100002",
                "name_display": "MIIFAA, Barry",
                "sex": "F",
                "age": 50,
                "dob": "1975-01-02",
                "ssn_last4": "4321",
                "station": "508"
            }
        ]

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
    # patient = get_patient_demographics(icn)
    # TODO: Replace with actual DB query
    patient = {
        "icn": icn,
        "name_display": "DOOREE, Adam",
        "sex": "M",
        "age": 45,
        "dob": "1980-01-02",
        "ssn_last4": "6789",
        "primary_station": "508",
        "primary_station_name": "Portland VAMC"
    }

    return patient


@router.get("/{icn}/flags")
async def get_patient_flags_json(icn: str):
    """
    Get patient flags as JSON.
    """
    # flags = get_patient_flags(icn)
    # TODO: Replace with actual DB query
    flags = [
        {
            "flag_name": "High Risk for Suicide",
            "category": "BEHAVIORAL",
            "narrative": "Patient flagged for suicide risk assessment",
            "active_date": "2024-01-15",
            "review_date": "2025-01-15"
        }
    ]

    return {
        "flags": flags,
        "count": len(flags)
    }


@router.get("/flags-content", response_class=HTMLResponse)
async def get_patient_flags_modal_content(request: Request):
    """
    Get patient flags modal content (HTML partial).
    """
    # Get current patient from CCOW
    patient_id = ccow_client.get_active_patient()

    if not patient_id:
        return "<p>No active patient selected</p>"

    # flags = get_patient_flags(patient_id)
    # TODO: Replace with actual template rendering
    return """
    <div class="flags-list">
        <div class="flag-item flag-item--high-risk">
            <h3>High Risk for Suicide</h3>
            <p><strong>Category:</strong> BEHAVIORAL</p>
            <p><strong>Active Date:</strong> 2024-01-15</p>
            <p><strong>Review Date:</strong> 2025-01-15</p>
            <p>Patient flagged for suicide risk assessment</p>
        </div>
    </div>
    """
```

### 10.3 Include Routes in Main App

**File:** `app/main.py` (modifications)

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

---

## 11. Implementation Checklist

### Phase 1: Setup & Structure (Day 1)
- [ ] Create `app/routes/` directory if it doesn't exist
- [ ] Create `app/routes/__init__.py`
- [ ] Create `app/routes/patient.py` with placeholder endpoints
- [ ] Create `app/utils/` directory if it doesn't exist
- [ ] Create `app/utils/__init__.py`
- [ ] Create `app/utils/ccow_client.py` (from CCOW design doc)
- [ ] Create `app/templates/partials/` directory
- [ ] Create placeholder partial templates (empty files)
- [ ] Update `app/main.py` to include patient routes
- [ ] Test that app starts without errors

### Phase 2: Topbar Redesign (Day 1-2)
- [ ] Backup current `base.html`
- [ ] Modify `base.html` topbar structure (lines 70-96)
- [ ] Add modal includes at end of base.html
- [ ] Add CSS styles for patient header to `styles.css`
- [ ] Add CSS styles for modals to `styles.css`
- [ ] Add CSS styles for forms and search results to `styles.css`
- [ ] Test responsive layout at different screen sizes

### Phase 3: HTMX Integration (Day 2-3)
- [ ] Implement `patient_header.html` partial
- [ ] Implement `GET /api/patient/current` endpoint
- [ ] Test initial load HTMX trigger
- [ ] Implement `GET /api/patient/refresh` endpoint
- [ ] Implement "Refresh Patient" button HTMX
- [ ] Test CCOW integration flow (with CCOW service running)
- [ ] Test graceful fallback (with CCOW service NOT running)

### Phase 4: Patient Search Modal (Day 3-4)
- [ ] Implement `patient_search_modal.html`
- [ ] Implement `patient_search_results.html`
- [ ] Add modal JavaScript handlers to `app.js`
- [ ] Implement `GET /api/patient/search` endpoint
- [ ] Test modal open/close behavior
- [ ] Test search input with HTMX triggers
- [ ] Test patient selection workflow
- [ ] Implement `POST /api/patient/set-context` endpoint
- [ ] Test CCOW vault update on patient selection
- [ ] Test modal auto-close after selection

### Phase 5: Patient Flags Modal (Day 4-5)
- [ ] Implement `patient_flags_modal.html`
- [ ] Implement `GET /api/patient/{icn}/flags` endpoint
- [ ] Implement `GET /api/patient/flags-content` endpoint
- [ ] Add flag count badge logic to patient_header.html
- [ ] Test modal open/close
- [ ] Test flag count badge display
- [ ] Test button enabled/disabled states

### Phase 6: Polish & Testing (Day 5-6)
- [ ] Test all HTMX interactions
- [ ] Test modal behavior (open, close, ESC key)
- [ ] Test button states (enabled/disabled)
- [ ] Test responsive design on mobile/tablet
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Accessibility review (keyboard navigation, ARIA labels)
- [ ] Test with CCOW service running
- [ ] Test with CCOW service NOT running
- [ ] Test error scenarios (network errors, invalid data)
- [ ] Performance testing (page load time, HTMX swap speed)

---

## 12. CSS Improvement Recommendations

### 12.1 Current Observations

Looking at the existing `styles.css` patterns, here are improvement opportunities:

**Strengths:**
- Good use of BEM-like naming (e.g., `topbar__left`, `sidebar__link`)
- Clear visual hierarchy

### 12.2 Suggested Improvements

#### 12.2.1 CSS Custom Properties (Variables)

Add CSS variables for colors, spacing, and typography to make theming and consistency easier:

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

#### 12.2.2 Focus States for Accessibility

Add visible focus indicators for keyboard navigation:

```css
button:focus-visible,
a:focus-visible,
input:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
}
```

#### 12.2.3 Utility Classes

Add reusable utility classes for common patterns:

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

#### 12.2.4 Animation & Transitions

Add smooth transitions for better UX:

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

---

## 13. Testing Strategy

### 13.1 Manual Testing Checklist

#### CCOW Integration
- [ ] Start app with CCOW vault running, patient set → Header shows patient
- [ ] Start app with CCOW vault running, no patient → Header shows "No patient selected"
- [ ] Start app with CCOW vault NOT running → Header shows "No patient selected" (graceful degradation)
- [ ] Start CCOW vault after app is running → Refresh button updates header correctly

#### Patient Selection
- [ ] Click "Select Patient" → Modal opens
- [ ] Type in search field → Results appear after 500ms delay
- [ ] Type < 2 characters → No results shown
- [ ] Click patient in results → Modal closes, header updates, CCOW vault updated
- [ ] Click outside modal (overlay) → Modal closes
- [ ] Press ESC key → Modal closes
- [ ] Change search type radio buttons → Search re-executes with new type

#### Refresh Button
- [ ] Click "Refresh Patient" with patient in CCOW → Header updates
- [ ] Click "Refresh Patient" with no patient in CCOW → Header shows "No patient selected"
- [ ] Change patient in CCOW vault externally → Refresh button loads new patient

#### Patient Flags
- [ ] With no patient selected → "View Patient Flags" button disabled
- [ ] With patient selected (no flags) → Button enabled, no badge
- [ ] With patient selected (with flags) → Button enabled, badge shows count
- [ ] Click "View Patient Flags" → Modal opens with flags
- [ ] Close flags modal → Modal closes properly

#### Responsive Design
- [ ] Test on desktop (1920x1080)
- [ ] Test on laptop (1366x768)
- [ ] Test on tablet (768x1024)
- [ ] Test on mobile (375x667)
- [ ] Test on mobile landscape (667x375)
- [ ] Patient header wraps appropriately on narrow screens
- [ ] Buttons stack vertically on very narrow screens

#### Accessibility
- [ ] Tab through all interactive elements (keyboard navigation works)
- [ ] Shift+Tab navigates backwards correctly
- [ ] ESC key closes modals
- [ ] ARIA labels present on icon-only buttons
- [ ] Screen reader can read patient demographics
- [ ] Color contrast meets WCAG AA standards (use browser dev tools)
- [ ] Focus indicators visible on all interactive elements

#### Error Scenarios
- [ ] CCOW vault returns 500 error → Graceful fallback
- [ ] Search endpoint times out → Error message shown
- [ ] Set context fails → User notified, CCOW not updated
- [ ] Invalid ICN provided → Appropriate error handling

### 13.2 Automated Testing (Future)

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

def test_search_patients():
    """Test patient search endpoint."""
    response = client.get("/api/patient/search?query=DOOREE&search_type=name")
    assert response.status_code == 200
    assert "DOOREE" in response.text

def test_search_patients_short_query():
    """Test that short queries return no results."""
    response = client.get("/api/patient/search?query=D&search_type=name")
    assert response.status_code == 200
    assert "Enter search criteria" in response.text

def test_get_patient_demographics_json():
    """Test patient demographics JSON endpoint."""
    response = client.get("/api/patient/100001/demographics")
    assert response.status_code == 200
    data = response.json()
    assert data["icn"] == "100001"
    assert "name_display" in data

def test_get_patient_flags_json():
    """Test patient flags JSON endpoint."""
    response = client.get("/api/patient/100001/flags")
    assert response.status_code == 200
    data = response.json()
    assert "flags" in data
    assert "count" in data
```

---

## 14. Rollout Plan

### 14.1 Incremental Deployment

**Iteration 1 (Minimum Viable Product)**
- Patient header partial with HTMX
- "No patient selected" state
- Mock demographics data
- Basic styling
- No modals yet

**Iteration 2**
- Patient search modal
- CCOW integration
- Set patient context
- Search functionality

**Iteration 3**
- Patient flags modal
- Flag count badge
- Refresh button
- Polish animations

**Iteration 4**
- Connect to real serving DB
- Real patient data
- Real flag data
- Performance optimization

### 14.2 Feature Flags (Optional)

Add a feature flag to toggle the new topbar for safer rollout:

**File:** `config.py`
```python
# config.py
USE_NEW_TOPBAR = _get_bool("USE_NEW_TOPBAR", default=True)
```

**File:** `.env`
```bash
USE_NEW_TOPBAR=true
```

**File:** `base.html`
```html
<!-- base.html -->
{% if config.USE_NEW_TOPBAR %}
    <!-- New patient-aware topbar -->
    {% include "partials/patient_header.html" %}
{% else %}
    <!-- Old topbar -->
    <div class="topbar__titles">
        <h1 class="topbar__title">{% block header_title %}Overview{% endblock %}</h1>
        <p class="topbar__subtitle">{% block header_subtitle %}...{% endblock %}</p>
    </div>
{% endif %}
```

### 14.3 Rollback Plan

If issues arise during deployment:

1. Set `USE_NEW_TOPBAR=false` in `.env`
2. Restart application
3. Old topbar will be restored
4. Investigate and fix issues
5. Re-enable when ready

---

## 15. Summary & Next Steps

### 15.1 Key Decisions

✅ **Architecture**: HTMX-powered partial templates
✅ **Layout**: Two-line patient header (name bold, demographics subtitle)
✅ **Modals**: Patient search and flags in modal dialogs
✅ **CCOW**: Query on initial load, manual refresh button
✅ **Fallback**: Graceful degradation to "No patient selected"
✅ **Styling**: Follow existing patterns, add improvements
✅ **Testing**: Manual checklist + automated tests (future)

### 15.2 Implementation Phases Summary

| Phase | Focus | Duration | Dependencies |
|-------|-------|----------|--------------|
| 1 | Setup & Structure | 1 day | None |
| 2 | Topbar Redesign | 1-2 days | Phase 1 |
| 3 | HTMX Integration | 2-3 days | Phase 1, 2, CCOW service |
| 4 | Patient Search Modal | 3-4 days | Phase 1, 2, 3 |
| 5 | Patient Flags Modal | 4-5 days | Phase 1, 2, 3 |
| 6 | Polish & Testing | 5-6 days | All phases |

**Total Estimated Duration:** 5-6 working days

### 15.3 Immediate Next Steps

1. **Review this specification** - Confirm approach aligns with vision
2. **Create directory structure** - Set up partials folder, routes folder
3. **Implement Phase 1** - Patient routes with mock data
4. **Build patient header partial** - Get HTMX integration working
5. **Iterate incrementally** - Add modals, then connect real data

### 15.4 Questions for Review

Before beginning implementation, please review and confirm:

1. **Does this plan align with your vision?** Any changes needed?
2. **File structure acceptable?** Should any files be organized differently?
3. **CSS approach acceptable?** Should we use a different styling strategy?
4. **Modal design acceptable?** Should modals work differently?
5. **Implementation phases acceptable?** Should we prioritize differently?
6. **Mock data approach acceptable?** Any specific mock data you want to use?

### 15.5 Prerequisites

Before starting implementation:

- [ ] CCOW Context Vault service is implemented and running
- [ ] `ccow_client.py` pattern from CCOW design doc is reviewed
- [ ] Configuration (`.env`, `config.py`) includes CCOW settings
- [ ] Existing `base.html` and `styles.css` backed up
- [ ] Python virtual environment is activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)

---

## Document History

| Version | Date       | Author | Notes                                      |
|---------|------------|--------|--------------------------------------------|
| v1.0    | 2025-12-07 | Chuck  | Initial specification for topbar redesign  |

---

**End of Document**
