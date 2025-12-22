# Patient Dashboard Design Specification - med-z1

**Document Version:** 1.1
**Last Updated:** 2025-12-11
**Phase:** Phase 3.5 - Patient Dashboard/Home Page Implementation
**Duration Estimate:** 3-4 days
**Status:** Functional Implementation Complete (Days 1-3 Complete)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Prerequisites](#3-prerequisites)
4. [Architecture and Design](#4-architecture-and-design)
5. [Widget Specifications](#5-widget-specifications)
6. [UI/UX Design](#6-uiux-design)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Testing Strategy](#8-testing-strategy)
9. [Future Enhancements](#9-future-enhancements)
10. [Appendices](#10-appendices)

---

## 1. Overview

### 1.1 Purpose

The **Patient Dashboard** (home page) provides a holistic, at-a-glance summary view of all implemented clinical domains for the currently selected patient. It serves as the primary landing page after user authentication and patient selection, enabling clinicians to quickly assess the patient's overall status across multiple care domains without navigating to individual detail pages.

### 1.2 Scope

**In Scope for Initial Implementation:**
- Dashboard layout with responsive widget grid (2-3 columns, multiple rows)
- Widget system supporting two standard sizes (1x1 and 2x1)
- Functional widgets for currently implemented domains:
  - Patient Demographics (summary)
  - Patient Flags (count and status)
- Placeholder widgets for planned domains:
  - Medications
  - Laboratory Results
  - Vitals
  - Allergies
  - Problems/Diagnoses
  - Orders
  - Notes/Documents
  - Radiology/Imaging
- Empty state when no patient is selected
- Auto-refresh when patient context changes
- Loading states for widget data
- Sticky topbar and static sidebar navigation
- Responsive design (mobile/tablet stack to 1 column)

**Out of Scope for Initial Implementation:**
- Clickable/actionable widgets (display only)
- User-customizable widget arrangement (drag-and-drop)
- Widget-level filtering or date range selection
- Real-time streaming data updates
- Widget export or print functionality
- Progressive/lazy widget loading (noted for future consideration)

### 1.3 Key Design Decisions

1. **Widget-Based Architecture:** Modular, reusable widget components for each clinical domain
2. **Fixed Layout:** Widgets arranged by clinical importance, matching sidebar navigation order
3. **Two Standard Sizes:** Widgets use either 1x1 or 2x1 grid cells based on content needs
4. **Display-Only Widgets:** MVP focuses on read-only summary display; interactivity deferred to detail pages
5. **Patient Context Dependency:** Dashboard shows data only when patient is selected; empty state otherwise
6. **Unified Styling:** All widgets share consistent color scheme and design language
7. **Auto-Refresh:** Widget data updates immediately when patient context changes via CCOW
8. **CSS Grid Layout:** Modern, flexible grid system for responsive widget arrangement

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Provide holistic patient view:** Enable clinicians to see summary information across all clinical domains in one place
2. **Reduce navigation burden:** Minimize clicks required to assess patient status
3. **Establish scalable pattern:** Create reusable widget framework for future domain additions
4. **Maintain performance:** Ensure dashboard loads quickly (<5 seconds target, <2 seconds ideal)

### 2.2 Success Criteria

**Layout & Responsiveness:**
- [x] Dashboard displays 2-3 widgets horizontally on desktop (≥1024px width)
- [x] Dashboard displays 1 widget per row on mobile/tablet (<1024px width)
- [x] Topbar remains sticky during vertical scrolling
- [x] Sidebar navigation remains static (does not scroll with content)
- [x] Vertical scrolling works smoothly when widgets exceed viewport height

**Widget Functionality:**
- [x] Demographics widget displays patient name, DOB, age, ICN, **address, phone, insurance** (enhanced)
- [x] Flags widget displays active flag count and highest severity status
- [x] Placeholder widgets visible for unimplemented domains
- [x] All widgets update when patient context changes
- [x] Loading indicators display when widget data fetch exceeds 1-2 seconds

**Patient Context:**
- [x] Empty state displays "Select a patient to begin" when no patient selected
- [x] Dashboard automatically refreshes when patient selected via CCOW
- [x] Widgets clear when patient context is cleared

**Navigation:**
- [x] Dashboard has dedicated nav item in sidebar (e.g., "Dashboard" or "Overview")
- [ ] Clicking domain in sidebar navigates to domain-specific detail page (Next: Allergies, Medications)
- [x] Current page highlighted in sidebar navigation

**Performance:**
- [x] Dashboard page loads in <5 seconds (acceptable)
- [x] Dashboard page loads in <2 seconds (ideal)
- [x] Widget data fetches execute in parallel (not sequential)

**Quality:**
- [x] Code follows established patterns from Phases 2-3
- [x] Responsive design tested on desktop, tablet, mobile
- [x] Error handling for failed widget data fetches
- [x] Logging for debugging widget load issues

---

## 3. Prerequisites

### 3.1 Completed Work

Before starting dashboard implementation, ensure the following are complete:

- ✅ Phase 2: Patient Topbar with patient selection and CCOW integration
- ✅ Phase 3: Patient Flags domain with full UI
- ✅ Patient Demographics data available in serving database
- ✅ FastAPI application running with HTMX templating

### 3.2 Environment Setup

**Required:**
- PostgreSQL serving database with patient data
- FastAPI application (port 8000)
- CCOW vault service (port 8001)
- Patient demographics and flags data loaded

**Verify:**
```bash
# Check patient demographics available
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM patient_demographics;"

# Check patient flags available
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM patient_flags;"

# Check FastAPI running
curl http://localhost:8000/
```

---

## 4. Architecture and Design

### 4.1 Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│ TOPBAR (sticky)                                             │
│ [Patient: John Doe | Select Patient | View Flags]           │
└─────────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────────────────────────────────┐
│          │  DASHBOARD CONTENT AREA (scrollable)             │
│  SIDEBAR │  ┌─────────────┬─────────────┬─────────────┐     │
│  (static)│  │  Widget 1   │  Widget 2   │  Widget 3   │     │
│          │  │ (1x1)       │ (1x1)       │ (2x1)       │     │
│ ☰ Menu   │  └─────────────┴─────────────┴─────────────┘    │
│ 🏠 Home  │  ┌─────────────┬─────────────┬─────────────┐     │
│ 👤 Demo  │  │  Widget 4   │  Widget 5   │  Widget 6   │     │
│ 🚩 Flags │  │ (1x1)       │ (2x1)       │ (1x1)       │     │
│ 💊 Meds  │  └─────────────┴─────────────┴─────────────┘     │
│ 🧪 Labs  │  ┌─────────────┬─────────────┐                   │
│ ...      │  │  Widget 7   │  Widget 8   │                   │
│          │  │ (1x1)       │ (1x1)       │                   │
│          │  └─────────────┴─────────────┘                   │
│          │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

### 4.2 Widget Architecture

**Widget Components:**
- **Widget Container:** Outer card/panel with consistent styling and fixed height
- **Widget Header:** Domain icon, title, and optional status indicator (fixed at top)
- **Widget Body:** Domain-specific summary content (scrollable if content exceeds height)
- **Widget Footer:** Optional metadata (last updated, source, etc.) (fixed at bottom)

**Widget Sizes:**
- **1x1 (Standard):** Single grid cell, ~300-400px width, ~200-250px height
- **2x1 (Wide):** Two grid cells wide, ~600-800px width, ~200-250px height

**Widget Content Scrolling:**
- Widget body content is **vertically scrollable** when content exceeds widget height
- Widget has fixed dimensions (height and width) - not resizable in MVP
- Scroll behavior allows displaying more items (e.g., 5-8 medications) while maintaining consistent dashboard layout
- Content should remain **minimal and "at-a-glance"** - scrolling is for overflow, not extensive lists
- Scrollbar appears automatically when content exceeds widget body height

**Widget Types:**
1. **Functional Widget:** Displays real data from implemented domain
2. **Placeholder Widget:** Shows "Coming Soon" or "Not Yet Implemented" message

### 4.3 Data Flow

```
User Selects Patient
       ↓
CCOW Context Updated
       ↓
Dashboard Detects Context Change (via htmx:afterSwap or custom event)
       ↓
Dashboard Triggers Widget Refresh
       ↓
Each Widget Fetches Data from API (parallel requests)
       ↓
Widgets Render with Data or Show Loading State
       ↓
User Views Complete Dashboard
```

### 4.4 Technology Stack

- **Backend:** FastAPI (Python 3.11)
- **Templating:** Jinja2
- **Interactive UX:** HTMX for dynamic widget loading
- **Layout:** CSS Grid for responsive widget arrangement
- **Styling:** Custom CSS following established patterns
- **Icons:** Font Awesome for domain icons

---

## 5. Widget Specifications

### 5.1 Clinical Domains and Widget Order

**Fixed Order by Clinical Importance:**

| Order | Domain | Widget Size | Status | Priority |
|-------|--------|-------------|--------|----------|
| 1 | Patient Demographics | 2x1 | ✅ Implemented | High |
| 2 | Patient Flags | 1x1 | ✅ Implemented | High |
| 3 | Allergies | 1x1 | 🔲 Placeholder | High |
| 4 | Medications | 2x1 | 🔲 Next to Implement | High |
| 5 | Vitals | 1x1 | 🔲 Placeholder | Medium |
| 6 | Laboratory Results | 2x1 | 🔲 Placeholder | Medium |
| 7 | Problems/Diagnoses | 1x1 | 🔲 Placeholder | Medium |
| 8 | Orders | 1x1 | 🔲 Placeholder | Medium |
| 9 | Notes/Documents | 1x1 | 🔲 Placeholder | Low |
| 10 | Radiology/Imaging | 1x1 | 🔲 Placeholder | Low |

**Note:** Sidebar navigation should list domains in the same order as widgets appear on dashboard.

### 5.2 Widget Content Specifications

#### 5.2.1 Patient Demographics Widget (2x1 - Wide)

**Purpose:** Display essential patient identification and demographic information

**Content:**
- Patient name (formatted: LAST, First Middle)
- Date of Birth (MM/DD/YYYY) and Age (calculated)
- Sex/Gender
- ICN (Integrated Care Number)
- SSN (masked: ***-**-1234)
- Primary station/facility
- Contact information (primary phone, address if space permits)

**API Endpoint:** `GET /api/patient/{icn}/demographics-summary`

**Example Display:**
```
┌─────────────────────────────────────────────────┐
│ 👤 Patient Demographics                         │
├─────────────────────────────────────────────────┤
│ DOE, John Allen                                 │
│ DOB: 03/15/1965 (59 years) | Male               │
│ ICN: ICN100001 | SSN: ***-**-5678               │
│ Primary Station: 518 - Northport VA Medical Ctr │
└─────────────────────────────────────────────────┘
```

#### 5.2.2 Patient Flags Widget (1x1 - Standard)

**Purpose:** Show active flag count and highest severity status

**Content:**
- Total active flags count
- Highest severity flag name (if any)
- Visual indicator for overdue flags (red badge)
- Category I (National) and Category II (Local) counts

**API Endpoint:** `GET /api/patient/{icn}/flags-summary`

**Example Display:**
```
┌─────────────────────────┐
│ 🚩 Patient Flags        │
├─────────────────────────┤
│ 2 Active Flags          │
│                         │
│ ⚠️  HIGH RISK FOR       │
│     SUICIDE (Overdue)   │
│                         │
│ National: 1 | Local: 1  │
└─────────────────────────┘
```

#### 5.2.3 Medications Widget (2x1 - Wide)

**Purpose:** Display recently prescribed medications

**Content:** (Placeholder for now, to be implemented next)
- List of active medications (3-5 most recent)
- Drug name (generic and brand)
- Dosage and frequency
- Prescribing station
- Last fill date

**API Endpoint:** `GET /api/patient/{icn}/medications-summary` (to be implemented)

**Example Display:**
```
┌─────────────────────────────────────────────────┐
│ 💊 Medications (Active)                         │
├─────────────────────────────────────────────────┤
│ • Lisinopril 10mg - Once daily (Sta3n: 518)    │
│   Last fill: 11/15/2024                         │
│ • Metformin 500mg - Twice daily (Sta3n: 518)   │
│   Last fill: 11/20/2024                         │
│ • Atorvastatin 20mg - Once daily (Sta3n: 589)  │
│   Last fill: 11/10/2024                         │
└─────────────────────────────────────────────────┘
```

#### 5.2.4 Vitals Widget

**Note:** Two widget size options are provided. Final selection to be made before implementation.

---

##### Option A: Vitals Widget 1x1 (Standard Size)

**Purpose:** Display most recent vital signs measurements in compact format

**Widget Size:** 1x1 (Standard)

**Content:**
- 4-6 most critical recent vitals (BP, T, P, R, POX, Pain)
- Display format: Abbreviation, Value, Unit
- Visual abnormal indicators (colored icons/badges for critical/abnormal values)
- Measurement timestamp (relative: "2h ago" or absolute date/time)
- "View All Vitals" link to full vitals page

**API Endpoint:** `GET /api/dashboard/widget/vitals/{patient_icn}?size=1x1`

**Example Display (Normal Values):**
```
┌─────────────────────────┐
│ ❤️  Vitals              │
├─────────────────────────┤
│ BP          T           │
│ 128/82      98.6°F      │
│ 2h ago      2h ago      │
│                         │
│ P           R           │
│ 72 bpm      16/min      │
│ 2h ago      2h ago      │
│                         │
│ POX         Pain        │
│ 98% ✓       2/10        │
│ 2h ago      1d ago      │
│                         │
│ [View All Vitals →]     │
└─────────────────────────┘
```

**Example Display (Abnormal Values):**
```
┌─────────────────────────┐
│ ❤️  Vitals       ⚠️  1  │
├─────────────────────────┤
│ BP          T           │
│ 158/95 ⚠️   99.8°F      │
│ HIGH        1h ago      │
│ 1h ago                  │
│                         │
│ P           R           │
│ 88 bpm      18/min      │
│ 1h ago      1h ago      │
│                         │
│ [View All Vitals →]     │
└─────────────────────────┘
```

**Design Notes:**
- Widget displays in 2-column grid (2 vitals per row)
- Priority order: BP, T, P, R, POX, Pain, WT (shows first 4-6 available)
- Abnormal values highlighted with:
  - 🔴 RED background + "CRITICAL" text for critical values
  - 🟡 YELLOW background + "HIGH"/"LOW" text for abnormal values
  - ✓ Green checkmark for normal values
- Widget header shows badge with count of critical/abnormal vitals
- Empty state: "No vitals recorded" if no data available
- Loading state: Skeleton/spinner while fetching data

---

##### Option B: Vitals Widget 2x1 (Wide Size)

**Purpose:** Display more vitals with mini-trend indicators for key measurements

**Widget Size:** 2x1 (Wide)

**Content:**
- 6-8 recent vitals (BP, T, P, R, POX, Pain, WT, HT if available)
- Display format: Table with columns (Vital, Value, Trend, Taken)
- Visual abnormal indicators (colored row backgrounds and inline badges)
- **Mini-trend sparklines** for BP, Weight, and Pain (last 7 days)
- BMI displayed if height/weight available
- Qualifiers shown as small tags (e.g., "Sitting, L Arm")
- "View All Vitals & Trends" link to full page

**API Endpoint:** `GET /api/dashboard/widget/vitals/{patient_icn}?size=2x1`

**Example Display:**
```
┌──────────────────────────────────────────────────────────┐
│ ❤️  Vitals                                    ⚠️  1      │
├──────────────────────────────────────────────────────────┤
│ Vital    │ Value          │ Trend        │ Taken        │
├──────────┼────────────────┼──────────────┼──────────────┤
│ BP       │ 158/95 mmHg    │ ───/──       │ 1h ago       │
│ Sitting, │ HIGH           │              │              │
│ L Arm    │                │              │              │
├──────────┼────────────────┼──────────────┼──────────────┤
│ T        │ 98.6 °F        │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ P        │ 88 bpm         │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ R        │ 18 /min        │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ POX      │ 97 %           │ —            │ 1h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ Pain     │ 3 /10          │ ──▲─▼        │ 2h ago       │
├──────────┼────────────────┼──────────────┼──────────────┤
│ WT       │ 185 lb         │ ──▲──        │ 3d ago       │
│          │ (BMI: 27.3)    │              │              │
└──────────┴────────────────┴──────────────┴──────────────┘
│ [View All Vitals & Trends →]                            │
└──────────────────────────────────────────────────────────┘
```

**Design Notes:**
- Widget displays as table with header row
- Trend column shows mini sparkline charts (Chart.js) for BP, Pain, and Weight
- Qualifiers displayed as small tags below vital abbreviation
- BMI calculated and shown with weight (if height available)
- Abnormal rows have colored backgrounds (red for critical, yellow for abnormal)
- More information density than 1x1 option
- Requires Chart.js library for sparklines

---

##### Design Comparison: Option A vs Option B

| Feature | Option A (1x1) | Option B (2x1) |
|---------|---------------|----------------|
| **Space Used** | 1 grid cell | 2 grid cells |
| **Vitals Shown** | 4-6 vitals | 6-8 vitals |
| **Layout** | 2-column grid | Table format |
| **Trends** | No | Yes (sparklines for BP, Pain, WT) |
| **BMI** | No | Yes (if available) |
| **Qualifiers** | No | Yes (as small tags) |
| **Timestamp** | Below each vital | Right column |
| **Information Density** | Lower | Higher |
| **At-a-Glance Scanning** | Easier | More detailed |
| **Best For** | Quick vital check | Detailed vital review |
| **Chart.js Required** | No | Yes |

**Recommendation:**
- **Option A (1x1):** Best for standard dashboard where space is at premium and user wants quick vital status
- **Option B (2x1):** Best when vitals are high priority and user benefits from trends and more detail without navigating away

---

**Data Requirements (Both Options):**
- Source: `patient_vitals` table in PostgreSQL serving database
- Query: Most recent measurement per vital type for patient
- Abnormal flag logic:
  - BP: Critical if Systolic >180 or <90, Diastolic >120 or <60; High if Systolic 140-180, Diastolic 90-120
  - Temp: Critical if >103°F or <95°F; High if 100.5-103°F
  - Pulse: Critical if >130 or <40; High if 100-130; Low if 40-60
  - Respiration: Critical if >28 or <8; High if 20-28
  - POX: Critical if <88%; Low if 88-92%
  - Pain: High if 8-10; Moderate if 4-7
- Trend data (Option B only): Last 7 days of measurements for BP, Pain, and Weight

**Related Documentation:**
- See `docs/vitals-design.md` for complete Vitals implementation specification (including both widget options)
- See Section 5.1 for widget ordering (Vitals is Order #5)

#### 5.2.5 Placeholder Widget Template (1x1 or 2x1)

**Purpose:** Indicate planned domain not yet implemented

**Content:**
- Domain icon and name
- "Coming Soon" message
- Optional: Brief description of what will be shown

**Example Display:**
```
┌─────────────────────────┐
│ 🧪 Laboratory Results   │
├─────────────────────────┤
│                         │
│   Coming Soon           │
│                         │
│ Recent lab results and  │
│ trends will appear here │
│                         │
└─────────────────────────┘
```

### 5.3 Widget State Management

**Widget States:**
1. **Loading:** Showing skeleton/spinner while data fetches
2. **Loaded:** Displaying data successfully
3. **Empty:** No data available for patient (e.g., no meds prescribed)
4. **Error:** Data fetch failed (show error message with retry option)
5. **Placeholder:** Domain not yet implemented (show "Coming Soon")

### 5.4 Widget Footer Design (Design Decision 2025-12-14)

**Purpose:** Provide subtle visual breathing room at the bottom of all widgets without wasting vertical space.

**Implementation Details:**
- **Footer Type:** Minimal empty footer (standard component across all widgets)
- **Padding:** `0.25rem` vertical (top/bottom), `1rem` horizontal (left/right)
- **Total Height:** ~9px (8px padding + 1px border)
- **Border:** 1px solid top border (`#f3f4f6`) for subtle visual separation
- **Content:** Empty (provides spacing only)

**Rationale:**
- **Original footer** had `0.75rem` padding = 24px vertical space
- **First iteration** reduced to `0.375rem` = 12px (50% reduction)
- **Final decision** reduced to `0.25rem` = 8px (62.5% total reduction)
- Testing confirmed this provides adequate breathing room without feeling cramped
- Maximizes scrollable content area while maintaining professional appearance

**Applied To:**
- Vitals widget (`app/templates/partials/vitals_widget.html`)
- Allergies widget (`app/templates/partials/allergies_widget.html`)
- Medications widget (`app/templates/partials/medications_widget.html`)
- Demographics widget (`app/templates/partials/demographics_widget.html`)

**CSS Classes:**
```css
.widget__footer {
    padding: 0.25rem 1rem;
    border-top: 1px solid #f3f4f6;
    flex-shrink: 0;
    min-height: 0;  /* Allow empty footers to collapse to minimal height */
}
```

**Widget Body Adjustments:**
Widget body max-heights were adjusted to account for footer space:
- Desktop: 221px (vs 180px original = +41px gain)
- Tablet: 201px (vs 160px original = +41px gain)
- Mobile: 171px (vs 130px original = +41px gain)

**Net Result:** 23% more scrollable content area vs original design while maintaining visual comfort.

**Link Placement:**
"View All" / "View Full" links remain inside `widget__body` using the `widget-action` pattern (centered, with top border separator), not in the footer. Footer provides spacing only.

---

## 6. UI/UX Design

### 6.1 Layout Grid System

**Desktop (≥1024px):**
- CSS Grid with 3 columns
- 1x1 widget occupies 1 column
- 2x1 widget occupies 2 columns
- Auto-fit rows based on widget height
- Gap between widgets: 1rem (16px)

**CSS Grid Configuration:**
```css
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    padding: 1.5rem;
}

.widget--1x1 {
    grid-column: span 1;
}

.widget--2x1 {
    grid-column: span 2;
}
```

**Tablet (768px - 1023px):**
- CSS Grid with 2 columns
- 1x1 widget occupies 1 column
- 2x1 widget occupies 2 columns (full width)

**Mobile (<768px):**
- CSS Grid with 1 column
- All widgets occupy full width (1 column)
- Stack vertically in order

### 6.2 Widget Card Styling

**Base Widget Styles:**
```css
.widget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    min-height: 200px;
}

.widget__header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
}

.widget__icon {
    font-size: 1.25rem;
    color: #6b7280;
}

.widget__title {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
}

.widget__body {
    flex: 1;
    overflow-y: auto;  /* Enable vertical scrolling when content exceeds height */
    overflow-x: hidden; /* Prevent horizontal scrolling */
    max-height: 180px;  /* Limit body height to ensure consistent widget size */
    padding-right: 0.5rem; /* Space for scrollbar */
}

/* Custom scrollbar styling (webkit browsers) */
.widget__body::-webkit-scrollbar {
    width: 6px;
}

.widget__body::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.widget__body::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.widget__body::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

.widget__footer {
    margin-top: 0.75rem;
    padding-top: 0.5rem;
    border-top: 1px solid #f3f4f6;
    font-size: 0.75rem;
    color: #6b7280;
}
```

**Placeholder Widget Styles:**
```css
.widget--placeholder {
    background: #f9fafb;
    border-style: dashed;
}

.widget--placeholder .widget__body {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #9ca3af;
}
```

**Loading State:**
```css
.widget--loading .widget__body {
    display: flex;
    align-items: center;
    justify-content: center;
}

.widget__spinner {
    border: 3px solid #f3f4f6;
    border-top: 3px solid #0066cc;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}
```

### 6.3 Widget Scrolling Behavior

**Scrollable Content Design:**

Widgets support **vertical scrolling** for content that exceeds the widget body height. This allows displaying more data items (e.g., 5-8 medications) while maintaining a consistent dashboard layout.

**Design Principles:**
1. **Fixed Widget Dimensions:** Widgets have fixed height (~200-250px total) to maintain grid alignment
2. **Scrollable Body Only:** Header and footer remain fixed; only the body content scrolls
3. **Automatic Scrollbars:** Scrollbar appears only when content exceeds available space
4. **Minimal Content First:** Design widgets for "at-a-glance" viewing; scrolling is for overflow only
5. **Smooth Scrolling:** Use custom scrollbar styling for better UX (thinner, styled scrollbars)

**Content Guidelines by Widget Type:**

| Widget | Recommended Items | Max Items (with scroll) |
|--------|------------------|-------------------------|
| Demographics | 6-8 fields | 8-10 fields |
| Flags | 2-3 flags | 4-6 flags |
| Medications | 3-4 medications | 6-8 medications |
| Lab Results | 3-5 recent results | 8-10 results |
| Vitals | 4-6 vital signs | 6-8 vital signs |

**Scroll Indicators:**
- Subtle gradient at bottom of widget body when content is scrollable
- Visible scrollbar (styled, not obtrusive)
- Optional: "Scroll for more" hint on first load

**Example - Widget with Scrollable Content:**
```
┌─────────────────────────────────────────────────┐
│ 💊 Medications (Active)                    ▲    │ ← Fixed header
├─────────────────────────────────────────────────┤
│ • Lisinopril 10mg - Once daily            │║   │ ← Scrollable
│   Last fill: 11/15/2024                   │║   │    body
│ • Metformin 500mg - Twice daily           │║   │    (6 items,
│   Last fill: 11/20/2024                   │█   │    scrollbar
│ • Atorvastatin 20mg - Once daily          │║   │    visible)
│   Last fill: 11/10/2024                   │║   │
│ • Lisinopril 10mg - Once daily            │║   │
│   Last fill: 11/05/2024                   │║   │
│ • Aspirin 81mg - Once daily               │║   │
│   Last fill: 11/01/2024                   │▼   │
├─────────────────────────────────────────────────┤
│ Last updated: 12/11/2024 09:30                  │ ← Fixed footer
└─────────────────────────────────────────────────┘
```

**Accessibility Considerations:**
- Keyboard scrolling (arrow keys, Page Up/Down) works within focused widget
- Screen readers announce scrollable regions
- Touch/swipe scrolling on mobile devices
- Sufficient color contrast for scrollbar visibility

### 6.4 Empty State Design

**When No Patient Selected:**
```html
<div class="dashboard-empty">
    <div class="dashboard-empty__icon">
        <i class="fa-regular fa-user"></i>
    </div>
    <h2 class="dashboard-empty__title">No Patient Selected</h2>
    <p class="dashboard-empty__message">
        Select a patient from the topbar to view their clinical summary
    </p>
    <button class="btn btn--primary" data-modal-open="patient-search-modal">
        <i class="fa-solid fa-magnifying-glass"></i>
        Select Patient
    </button>
</div>
```

### 6.5 Sidebar Navigation Updates

**Add Dashboard Item:**
```html
<nav class="sidebar__nav">
    <a href="/" class="sidebar__link sidebar__link--active">
        <i class="fa-solid fa-house"></i>
        <span>Dashboard</span>
    </a>
    <a href="/demographics" class="sidebar__link">
        <i class="fa-solid fa-user"></i>
        <span>Demographics</span>
    </a>
    <a href="/flags" class="sidebar__link">
        <i class="fa-solid fa-flag"></i>
        <span>Patient Flags</span>
    </a>
    <a href="/medications" class="sidebar__link">
        <i class="fa-solid fa-pills"></i>
        <span>Medications</span>
    </a>
    <!-- Additional domains... -->
</nav>
```

**Note:** Domain order in sidebar should match dashboard widget order.

### 6.6 Responsive Behavior

**Breakpoints:**
- Desktop: ≥1024px (3 columns)
- Tablet: 768px - 1023px (2 columns)
- Mobile: <768px (1 column)

**Mobile Optimizations:**
- Reduce widget padding (0.75rem instead of 1rem)
- Stack all widgets vertically
- Reduce font sizes slightly for readability
- Maintain minimum touch target size (44x44px for buttons)

---

## 7. Implementation Roadmap

### 7.1 Timeline Overview

**Total Duration:** 3-4 days

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Dashboard page structure and routing | Base HTML template, routing configured |
| 2 | Widget framework and grid layout | Reusable widget components, CSS grid |
| 3 | Functional widgets (Demographics, Flags) | Working widgets with real data |
| 4 | Placeholder widgets, testing, polish | Complete dashboard, responsive tested |

### 7.2 Day-by-Day Plan

#### Day 1: Dashboard Structure and Routing

**Tasks:**
1. Create dashboard route in FastAPI (`app/routes/dashboard.py`)
2. Create base dashboard template (`app/templates/dashboard.html`)
3. Update sidebar navigation to include Dashboard link
4. Implement empty state (no patient selected)
5. Test routing and empty state display

**Deliverables:**
- Dashboard accessible at `/` or `/dashboard`
- Empty state displays when no patient selected
- Sidebar navigation updated with Dashboard link
- Basic page structure in place

**Files to Create:**
- `app/routes/dashboard.py`
- `app/templates/dashboard.html`

**Files to Modify:**
- `app/main.py` (register dashboard router)
- `app/templates/base.html` (sidebar navigation)

#### Day 2: Widget Framework and Grid Layout ✅ COMPLETE

**Tasks:**
1. ✅ Create widget base template (`app/templates/partials/widget_base.html`)
2. ✅ Implement CSS Grid layout for dashboard
3. ✅ Add widget CSS styles to `app/static/styles.css`
4. ✅ Create loading state component
5. ✅ Implement widget refresh mechanism (HTMX or JavaScript)
6. ✅ Test responsive layout on different screen sizes

**Deliverables:**
- ✅ Reusable widget component structure
- ✅ Responsive CSS Grid layout (3/2/1 columns)
- ✅ Widget loading states functional
- ✅ Dashboard refreshes when patient context changes

**Files Created:**
- `app/templates/partials/widget_base.html` - Jinja2 macros for widget and placeholder_widget

**Files Modified:**
- `app/static/styles.css` - Added ~200 lines of widget/dashboard styles with responsive breakpoints
- `app/templates/dashboard.html` - Added widget grid with 2 functional + 10 placeholder widgets
- `app/static/app.js` - Added refreshDashboardWidgets() function for patient context changes

#### Day 3: Functional Widgets Implementation ✅ COMPLETE

**Tasks:**
1. ✅ Create Demographics widget endpoint and template
   - `GET /api/dashboard/widget/demographics/{patient_icn}`
   - `app/templates/partials/demographics_widget.html`
2. ✅ Create Flags widget endpoint and template
   - `GET /api/dashboard/widget/flags/{patient_icn}`
   - `app/templates/partials/flags_widget.html`
3. ✅ Implement widget data fetching (HTMX integration)
4. ✅ Add error handling for failed data fetches
5. ✅ Test with multiple patients
6. ✅ **BONUS**: Enhanced Demographics widget with address, phone, insurance data
7. ✅ Fixed duplicate patient rows issue in ETL pipeline

**Deliverables:**
- ✅ Demographics widget displays patient summary (name, DOB, age, gender, SSN, address, phone, insurance)
- ✅ Flags widget displays flag count, category breakdown, and top 3 active flags
- ✅ Widgets load data when patient selected
- ✅ Error states handled gracefully
- ✅ Demographics enhancement complete (full ETL pipeline updated)

**Files Created:**
- `app/templates/partials/demographics_widget.html`
- `app/templates/partials/flags_widget.html`
- `etl/bronze_patient_address.py`
- `etl/bronze_patient_insurance.py`
- `etl/bronze_insurance_company.py`
- `mock/sql-server/cdwwork/create/Dim.InsuranceCompany.sql`
- `mock/sql-server/cdwwork/insert/Dim.InsuranceCompany.sql`
- `docs/demographics-enhancement-design.md`

**Files Modified:**
- `app/routes/dashboard.py` (added widget endpoints)
- `app/db/patient.py` (updated query with address/phone/insurance fields)
- `app/static/styles.css` (added widget content styles, optimized spacing)
- `etl/silver_patient.py` (added address/insurance joins, deduplication fix)
- `etl/gold_patient.py` (added new fields to Gold schema)
- `db/ddl/patient_demographics.sql` (added address/phone/insurance columns)
- `mock/sql-server/cdwwork/insert/SPatient.SPatientAddress.sql` (added 12 missing addresses)
- `mock/sql-server/cdwwork/insert/SPatient.SPatientInsurance.sql` (updated with correct foreign keys)

#### Day 4: Placeholder Widgets and Testing

**Tasks:**
1. Create placeholder widget template
2. Add placeholder widgets for planned domains:
   - Allergies
   - Medications
   - Vitals
   - Laboratory Results
   - Problems/Diagnoses
   - Orders
   - Notes/Documents
   - Radiology/Imaging
3. Test responsive design (desktop, tablet, mobile)
4. Test empty state and patient switching
5. Performance testing (page load time)
6. Code review and cleanup
7. Update documentation

**Deliverables:**
- All planned domain placeholders visible
- Responsive design verified
- Performance targets met (<5 seconds)
- Dashboard ready for production use

**Files to Create:**
- `app/templates/partials/widget_placeholder.html`

**Files to Modify:**
- `app/templates/dashboard.html` (add all widget instances)

---

## 8. Testing Strategy

### 8.1 Manual Testing Checklist

**Layout & Responsiveness:**
- [ ] Dashboard displays 3 columns on desktop (≥1024px)
- [ ] Dashboard displays 2 columns on tablet (768-1023px)
- [ ] Dashboard displays 1 column on mobile (<768px)
- [ ] Widgets maintain aspect ratio and readability at all sizes
- [ ] Topbar remains sticky during vertical scroll
- [ ] Sidebar remains static during vertical scroll
- [ ] Scrolling is smooth with many widgets

**Patient Context:**
- [ ] Empty state displays when no patient selected
- [ ] Widgets load when patient selected
- [ ] Widgets clear when patient context cleared
- [ ] Dashboard auto-refreshes when patient changes
- [ ] Loading states appear for slow widget loads (>1-2 seconds)

**Widget Functionality:**
- [ ] Demographics widget shows correct patient info
- [ ] Flags widget shows correct flag count and status
- [ ] Placeholder widgets display "Coming Soon" message
- [ ] Widget data updates when patient changes

**Navigation:**
- [ ] Dashboard link in sidebar navigates to dashboard
- [ ] Domain links in sidebar navigate to detail pages
- [ ] Current page highlighted in sidebar
- [ ] All navigation links functional

**Error Handling:**
- [ ] Widget shows error message if data fetch fails
- [ ] Dashboard handles missing patient gracefully
- [ ] Console shows no JavaScript errors

**Performance:**
- [ ] Dashboard page loads in <5 seconds (acceptable)
- [ ] Dashboard page loads in <2 seconds (ideal)
- [ ] Widget data fetches execute in parallel

### 8.2 Browser Compatibility

**Test in:**
- Chrome/Edge (Chromium-based)
- Firefox
- Safari (macOS/iOS)

**Minimum Supported Versions:**
- Chrome: Last 2 major versions
- Firefox: Last 2 major versions
- Safari: Last 2 major versions

### 8.3 Accessibility Testing

**508 Compliance:**
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Screen reader can read widget titles and content
- [ ] Color contrast meets WCAG AA standards
- [ ] Focus indicators visible on interactive elements
- [ ] No content conveyed by color alone

---

## 9. Future Enhancements

**Phase 2 Enhancements (Post-MVP):**

1. **Progressive/Lazy Widget Loading**
   - Load above-the-fold widgets first
   - Lazy load below-the-fold widgets as user scrolls
   - Improve perceived performance

2. **Clickable Widgets**
   - Click widget to navigate to domain detail page
   - Or expand widget in-place (modal or slide-out)

3. **User Customization**
   - Drag-and-drop widget rearrangement
   - Show/hide individual widgets
   - Save user preferences per user account

4. **Widget-Level Filtering**
   - Date range selection per widget
   - Facility filtering
   - Status filtering (e.g., active/inactive)

5. **Real-Time Updates**
   - WebSocket or Server-Sent Events for live data updates
   - Notification when new data available

6. **Widget Actions**
   - Refresh individual widget
   - Export widget data (PDF, CSV)
   - Print widget

7. **Variable Widget Sizes**
   - Support 1x1, 2x1, 1x2, 2x2 sizes
   - Domain-specific sizing based on content needs

8. **Dashboard Presets**
   - Pre-configured dashboard layouts for different specialties
   - "Primary Care View", "Mental Health View", etc.

9. **Widget Analytics**
   - Track which widgets users view most
   - Inform future default layouts

---

## 10. Appendices

### Appendix A: Widget API Response Formats

**Demographics Summary:**
```json
{
  "patient_icn": "ICN100001",
  "name_display": "DOE, John Allen",
  "dob": "1965-03-15",
  "age": 59,
  "sex": "Male",
  "ssn_last4": "5678",
  "primary_station": "518",
  "primary_station_name": "Northport VA Medical Center"
}
```

**Flags Summary:**
```json
{
  "patient_icn": "ICN100001",
  "total_flags": 2,
  "national_flags": 1,
  "local_flags": 1,
  "overdue_flags": 1,
  "highest_severity_flag": {
    "flag_name": "HIGH RISK FOR SUICIDE",
    "review_status": "OVERDUE"
  }
}
```

### Appendix B: File Structure

```
med-z1/
  app/
    routes/
      dashboard.py                    # Dashboard routes and widget endpoints
    templates/
      dashboard.html                  # Main dashboard page
      partials/
        widget_base.html              # Reusable widget structure
        widget_demographics.html      # Demographics widget
        widget_flags.html             # Flags widget
        widget_placeholder.html       # Placeholder widget template
    static/
      styles.css                      # Add dashboard/widget styles (~200 lines)
      app.js                          # Add dashboard refresh logic
  docs/
    patient-dashboard-design.md       # This document
```

### Appendix C: CSS Variables for Widgets

```css
:root {
    --widget-bg: #ffffff;
    --widget-border: #e5e7eb;
    --widget-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    --widget-padding: 1rem;
    --widget-gap: 1rem;
    --widget-border-radius: 0.5rem;
    --widget-header-border: #e5e7eb;
    --widget-title-color: #1f2937;
    --widget-icon-color: #6b7280;
    --widget-footer-bg: #f9fafb;
    --widget-placeholder-bg: #f9fafb;
    --widget-placeholder-border: dashed 1px #d1d5db;
    --widget-loading-spinner: #0066cc;
}
```

### Appendix D: Sample Dashboard HTML Structure

```html
<!-- app/templates/dashboard.html -->
{% extends "base.html" %}

{% block content %}
<div class="dashboard">
    {% if patient %}
        <div class="dashboard-grid">
            <!-- Demographics Widget (2x1) -->
            <div class="widget widget--2x1"
                 hx-get="/api/dashboard/widget/demographics/{{ patient.icn }}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                <div class="widget__loading">Loading...</div>
            </div>

            <!-- Flags Widget (1x1) -->
            <div class="widget widget--1x1"
                 hx-get="/api/dashboard/widget/flags/{{ patient.icn }}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                <div class="widget__loading">Loading...</div>
            </div>

            <!-- Placeholder Widgets -->
            {% include "partials/widget_placeholder.html" with context {"domain": "Allergies", "size": "1x1"} %}
            {% include "partials/widget_placeholder.html" with context {"domain": "Medications", "size": "2x1"} %}
            <!-- Additional placeholders... -->
        </div>
    {% else %}
        <!-- Empty State -->
        <div class="dashboard-empty">
            <div class="dashboard-empty__icon">
                <i class="fa-regular fa-user fa-4x"></i>
            </div>
            <h2 class="dashboard-empty__title">No Patient Selected</h2>
            <p class="dashboard-empty__message">
                Select a patient from the topbar to view their clinical summary
            </p>
            <button class="btn btn--primary" data-modal-open="patient-search-modal">
                <i class="fa-solid fa-magnifying-glass"></i>
                Select Patient
            </button>
        </div>
    {% endif %}
</div>
{% endblock %}
```

---

## 11. Enhancements and Future Work

### 11.1 Demographics Widget Enhancement (Post-Day 4)

**Status:** Design phase (2025-12-11)

After completing the initial dashboard implementation (Days 1-4), the Demographics widget will be enhanced to include additional patient information:

**Enhancements:**
- **Address**: Primary address (street, city, state, zip)
- **Phone**: Primary phone (placeholder "Not available" for MVP)
- **Insurance**: Primary insurance company name

**Technical Design:**
See `docs/demographics-enhancement-design.md` for complete implementation plan, including:
- New CDWWork dimension table (`Dim.InsuranceCompany`)
- ETL pipeline updates (Bronze/Silver/Gold layers)
- PostgreSQL serving database schema updates
- Application query and template updates

**Implementation Timeline:** 6 days (after dashboard Days 1-4 complete)

**Priority:** High - Required for MVP to display comprehensive patient context

### 11.2 Future Widget Enhancements

**Near-Term (Phase 5):**
- Medications widget (medication list, reconciliation status)
- Vitals widget (recent vital signs with trends)
- Allergies widget (known allergies and adverse reactions)

**Long-Term:**
- Laboratory Results widget with trending graphs
- Problems/Diagnoses widget with active problem list
- Orders widget with pending/completed orders
- Notes/Documents widget with recent clinical notes
- Radiology/Imaging widget with study results

---

## 11. Current Status and Next Steps

### 11.1 Implementation Status (as of 2025-12-11)

**Completed Work:**
- ✅ Days 1-3 Complete: Dashboard framework and functional widgets
- ✅ Demographics widget enhanced with address, phone, insurance
- ✅ Flags widget displaying active flags with review status
- ✅ UI spacing optimized for 16" MacBook Pro (1496 x 967)
- ✅ ETL pipeline updated for new demographic fields
- ✅ Duplicate patient rows issue resolved
- ✅ Full integration tested and working

**Current Configuration:**
- Widget height: 275px
- Widget grid gap: 1.25rem
- Content padding: 0rem (top/bottom), 1.75rem (left/right)
- Two full rows of widgets visible on standard laptop displays
- 36 unique patients with complete demographic data

### 11.2 Next Steps

**Immediate (Next Session):**
1. Allergies widget implementation
2. Medications widget implementation
3. Create dedicated domain pages (clickable from sidebar)

**Future Enhancements:**
- Implement remaining domain widgets (Vitals, Labs, Orders, Notes, etc.)
- Add interactivity to widgets (click to navigate to detail page)
- Performance optimization for widget data loading
- User preference storage for layout customization

---

**End of Specification**

**Document Status:** Days 1-3 Complete + Demographics Enhancement Complete (2025-12-11)
**Document Version:** 1.1
**Related Documents:**
- `docs/demographics-enhancement-design.md` - Complete implementation details
- `docs/patient-flags-design.md` - Patient Flags system specification
