# Changelog - December 16, 2025

## Patient Information Display Restructuring

### Summary
Restructured how patient demographic information is displayed across the application to reduce redundancy and improve readability.

### Changes Made

#### 1. Topbar Patient Header (`app/templates/partials/patient_header.html`)

**Before:**
```
DOOREE, ADAM (M, 45)
ICN: ICN100001 | SSN: ***-**-1234 | DOB: 1980-01-02 | Station: 508 (Atlanta, GA VA Medical Center)
```

**After:**
```
DOOREE, ADAM (M, 45)
```

**Rationale:**
- Reduced visual clutter in the topbar
- Patient identification details moved to page-level subtitles where they're more contextually relevant
- SSN removed entirely from the UI per security best practices

#### 2. Page Subtitles (Dashboard and All Clinical Domain Pages)

**Before:**
```
Clinical summary for Dooree, Adam
```
or
```
Dooree, Adam (ICN100001)
```

**After:**
```
Dooree, Adam (ICN100001)  |  1980-01-02  |  508 (Atlanta, GA VA Medical Center)
```

**Implementation:**
- Updated all page subtitles to show: Name (ICN) | DOB | Station (Station Name)
- Used `&nbsp;&nbsp;` for proper spacing around pipe separators (HTML collapses multiple spaces)
- Applied consistently across:
  - Dashboard (`dashboard.html`)
  - Demographics (`patient_demographics.html`)
  - Vitals (`patient_vitals.html`, `partials/vitals_refresh_area.html`)
  - Allergies (`allergies.html`)
  - Medications (`patient_medications.html`)
  - Encounters (`patient_encounters.html`)
  - Labs (`patient_labs.html`)

#### 3. Date Formatting Fix (`app/db/patient.py`)

**Before:**
```python
"dob": str(result[6]) if result[6] else None,
# Resulted in: "1980-01-02 00:00:00"
```

**After:**
```python
"dob": result[6].strftime("%Y-%m-%d") if result[6] else None,
# Results in: "1980-01-02"
```

**Impact:** Clean date display without timestamp across all pages and widgets.

---

## VistA UI Integration (Vitals Page)

### Summary
Completed VistA "Refresh from VistA" button implementation on the Vitals page with proper spacing and layout.

### Changes Made

#### 1. VistA Refresh Controls (`patient_vitals.html`)

**Added:**
- Page header breadcrumb section with left-aligned breadcrumbs (Dashboard > Vital Signs)
- Right-aligned VistA refresh controls section containing:
  - Data freshness indicator: "Data current through: [date] ([freshness])"
  - "Refresh from VistA" button (secondary style with rotate icon)
  - Loading spinner (hidden by default, shown during HTMX request)

**HTMX Integration:**
```html
<button
    hx-get="/patient/{{ patient.icn }}/vitals/realtime"
    hx-target="#vista-refresh-area"
    hx-swap="outerHTML"
    hx-indicator="#vista-loading"
    class="btn btn--secondary vista-refresh-btn">
    <i class="fa-solid fa-rotate"></i> Refresh from VistA
</button>
```

#### 2. Partial Template (`partials/vitals_refresh_area.html`)

**Created:** New partial template for HTMX swap containing:
- Page title section
- Filters and controls (vital type pills, sort dropdown, view toggle)
- Vitals table
- Charts view section
- Out-of-band swap for freshness message update

**Out-of-Band Swap:**
```html
<span class="data-freshness" hx-swap-oob="true" id="freshness-message">
    {% if vista_refreshed %}
        Data current through: {{ data_current_through }} (today)
        <span class="last-updated">Last updated: {{ last_updated }}</span>
    {% endif %}
</span>
```

#### 3. Backend Route (`app/routes/vitals.py`)

**Updated Initial Page Route:**
- Calculate `data_current_through` (yesterday's date for PostgreSQL data)
- Set `data_freshness_label` = "yesterday"
- Set `vista_refreshed` = False

**New Realtime Route** (`/patient/{icn}/vitals/realtime`):
- Accepts same filters and sort parameters as main page
- Simulates VistA delay with `await asyncio.sleep(2)` (remove when VistA service ready)
- Returns `partials/vitals_refresh_area.html` fragment
- Sets `vista_refreshed` = True
- Calculates today's date and last updated timestamp
- Includes TODO comments for future VistA RPC Broker integration

#### 4. CSS Styling (`app/static/styles.css`)

**Added:**
- `.page-header-breadcrumb` - Flexbox layout (breadcrumbs left, controls right)
- `.breadcrumb-nav` - Breadcrumb styling with separators
- `.vista-controls` - Right-aligned controls container with flexbox gap
- `.data-freshness` - Freshness message styling
- `.vista-refresh-btn` - Button with darker secondary color for contrast
- `.htmx-indicator` - Loading spinner (hidden by default)
- Disabled button state styling (40% opacity, wait cursor, light gray background)
- Responsive media queries for mobile (two-line stacked layout)

#### 5. Spacing Adjustments

**Final Spacing Configuration:**
```css
/* Breadcrumb bottom margin */
.page-header-breadcrumb {
    margin-bottom: 1.5rem;
}

/* Title group pushed up */
#vista-refresh-area {
    margin-top: -0.5rem;
}

/* Breathing room below subtitle */
#vista-refresh-area .page-header__title-group {
    margin-bottom: 1.5rem;
}

/* No extra spacing above filters */
#vista-refresh-area .vitals-controls {
    margin-top: 0;
}
```

**Rationale:** Creates proper breathing room between subtitle and filters while maintaining consistent overall page spacing (matches Encounters and other pages).

---

## Vitals Chart Bug Fix

### Issue
Vitals page charts were displaying as blank containers after the patient information restructuring changes.

### Root Cause
The `getCurrentPatientICN()` function in `vitals.js` was not executing properly, though the exact reason remains unknown. The function call was completing without error, but console.log statements inside the function never executed, suggesting a JavaScript scoping or execution context issue.

### Solution
Inlined the ICN extraction code directly into the `initializeCharts()` function, bypassing the separate function call entirely.

**Before:**
```javascript
function getCurrentPatientICN() {
    const path = window.location.pathname;
    const match = path.match(/\/patient\/([^\/]+)\/vitals/);
    return match ? match[1] : null;
}

function initializeCharts() {
    const patientICN = getCurrentPatientICN();
    if (!patientICN) {
        console.error('No patient ICN found in URL');
        return;
    }
    // ... chart initialization
}
```

**After:**
```javascript
function initializeCharts() {
    // Extract ICN directly from URL
    const path = window.location.pathname;
    const match = path.match(/\/patient\/([^\/]+)\/vitals/);
    const patientICN = match ? match[1] : null;

    if (!patientICN) {
        console.error('No patient ICN found in URL');
        return;
    }
    // ... chart initialization
}
```

**Changed Files:**
- `app/static/vitals.js` - Inlined ICN extraction, removed unused function
- `app/templates/patient_vitals.html` - Added cache-busting parameter (`?v=4`)

**Result:** Charts now render correctly with all trend data visible (Blood Pressure, Weight, Pain Score).

---

## Files Modified

### Templates
- `app/templates/base.html` - No changes (uses patient header partial)
- `app/templates/partials/patient_header.html` - Removed ICN/SSN/DOB/Station subtitle
- `app/templates/dashboard.html` - Expanded subtitle format
- `app/templates/patient_vitals.html` - VistA UI controls, expanded subtitle, cache-busting
- `app/templates/partials/vitals_refresh_area.html` - New partial for HTMX swap
- `app/templates/patient_demographics.html` - Expanded subtitle format
- `app/templates/allergies.html` - Expanded subtitle format
- `app/templates/patient_medications.html` - Expanded subtitle format
- `app/templates/patient_encounters.html` - Expanded subtitle format
- `app/templates/patient_labs.html` - Expanded subtitle format

### Backend
- `app/db/patient.py` - Fixed DOB formatting (strftime)
- `app/routes/vitals.py` - Added realtime route, data freshness calculation

### Frontend
- `app/static/styles.css` - VistA UI styles, spacing adjustments
- `app/static/vitals.js` - Inlined ICN extraction, removed broken function

---

## Testing Verification

### Patient Information Display
- ✅ Topbar shows only: "DOOREE, ADAM (M, 45)"
- ✅ Dashboard subtitle shows full format with proper spacing
- ✅ All clinical domain page subtitles show full format with proper spacing
- ✅ DOB displays as "1980-01-02" (no timestamp)
- ✅ Pipe separators have two spaces on each side
- ✅ SSN no longer appears anywhere in the UI

### VistA Refresh UI (Vitals)
- ✅ Breadcrumbs and controls properly aligned (left/right)
- ✅ "Refresh from VistA" button functional with HTMX
- ✅ Loading spinner appears during 2-second simulated delay
- ✅ Button disabled state clearly visible (40% opacity, wait cursor)
- ✅ Freshness message updates after refresh
- ✅ Filters, sort, and table update correctly
- ✅ Spacing matches other clinical domain pages (2rem total)
- ✅ Responsive layout works (mobile two-line stacking)

### Vitals Charts
- ✅ Blood Pressure chart displays correctly
- ✅ Weight chart displays correctly
- ✅ Pain Score chart displays correctly
- ✅ Charts toggle properly with "View Charts" button
- ✅ No console errors during chart initialization

---

## Future Work

### VistA Service Integration (Phase 8)
When the VistA RPC Broker service is ready, update `app/routes/vitals.py`:

1. Remove `await asyncio.sleep(2)` simulation
2. Integrate actual VistA RPC calls:
   ```python
   from app.services.vista_client import VistaClient

   vista = VistaClient()
   vista_results = await vista.call_rpc_multi_site(
       sites=["200", "500", "630"],
       rpc_name="GMV LATEST VM",
       params=[icn, "1"]  # "1" = today's vitals only
   )
   ```
3. Implement data merging (PostgreSQL T-1+ data + VistA T-0 data)
4. Add partial success handling (e.g., "2 of 3 sites responded")
5. Implement error recovery and retry mechanisms

**Reference:** `docs/vista-rpc-broker-design.md` Section 2.11

### Other Clinical Domain Pages
Apply same VistA refresh pattern to:
- Labs page
- Medications page
- Allergies page
- Encounters page (when applicable)

---

## Notes

- Cache-busting parameter (`?v=4`) used for vitals.js to force browser reload during debugging
- Consider implementing automatic version hashing for production deployments
- The `getCurrentPatientICN()` function issue remains unexplained; may be worth investigating in the future, but inlined solution is working and more efficient
