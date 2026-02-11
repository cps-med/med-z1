# Demographics Design Specification - med-z1

**Document Version:** 2.2
**Date:** 2025-12-14
**Status:** ✅ Complete - Widget and Full Page Implemented
**Implementation Phase:** Widget Complete (v1.1 - 2025-12-11), Full Page Complete (v2.2 - 2025-12-14)

**Implementation Status Source:** `docs/spec/implementation-status.md`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Prerequisites](#3-prerequisites)
4. [Data Architecture](#4-data-architecture)
5. [Database Schema](#5-database-schema)
6. [ETL Pipeline Design](#6-etl-pipeline-design)
7. [API Endpoints](#7-api-endpoints)
8. [UI/UX Design](#8-uiux-design)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Testing Strategy](#10-testing-strategy)
11. [Security and Privacy](#11-security-and-privacy)
12. [Appendices](#12-appendices)

---

## 1. Overview

### 1.1 Purpose

The **Demographics** domain provides comprehensive access to patient demographic and administrative data, enabling clinicians to:
- View core patient identifiers and demographics at a glance (dashboard widget)
- Access complete demographic, contact, insurance, and military service information (full demographics page)
- Verify patient identity using multiple identifiers (name, DOB, SSN, ICN)
- Understand patient's eligibility, service connection status, and special considerations
- Access critical safety information (deceased status, marital status for next of kin coordination)

Demographics data is the **foundation** for all other clinical domains, providing the patient context needed for safe, coordinated care.

### 1.2 Scope

**In Scope for Demographics Domain:**

**Phase 1: Dashboard Widget** ✅ **Complete (2025-12-11)**
- Basic demographics: Name, DOB, Age, Sex, SSN
- Primary contact information: Phone, Address
- Primary insurance information: Insurance company name
- VA facility information: Primary station
- Widget display on patient dashboard (1x1 size)
- HTMX-based widget loading

**Phase 2: Full Demographics Page** 🚧 **Design Complete (2025-12-14)**
- Comprehensive demographic display with multi-section layout
- Additional fields beyond widget:
  - Marital Status
  - Religion
  - Service Connected Percentage
  - Deceased Status and Death Date (with visual indicator)
- Two-column layout for efficient space usage
- Read-only display (consistent with other domains)
- "View Full Demographics" link from widget
- Dedicated page route: `/patient/{icn}/demographics`
- Sidebar navigation link

**Out of Scope for Initial Implementation:**
- Self-Identified Gender (SIGI) - VA has moved away from this field
- Edit/update capabilities (read-only domain)
- Detailed disability exposures (Agent Orange, POW, radiation - defer to Disability domain if needed)
- Emergency Contact / Next of Kin (table not yet in CDWWork)
- Multiple phone numbers (home, work, mobile)
- Email address
- Preferred language
- Race/Ethnicity data
- Print/Export functionality
- Historical demographics changes (audit trail)

### 1.3 Key Design Decisions

**Decision 1: Two-Phase Implementation**
- **Phase 1 (Complete):** Enhanced widget with contact and insurance
- **Phase 2 (Pending):** Full demographics page with additional fields

**Decision 2: Curated Field Selection (Option B)**
- Focus on **clinically relevant** demographics
- Include: Marital status, religion, service connected %, deceased status
- Exclude: Detailed disability exposures, race/ethnicity, language preferences
- Rationale: Balance comprehensive information with usability

**Decision 3: Read-Only Display**
- Demographics page is **read-only** (consistent with Vitals, Allergies, Medications)
- Editing demographics is a separate workflow (not in scope for med-z1 viewer)
- Rationale: med-z1 is a **viewer**, not a full EHR

**Decision 4: Visual Treatment**
- **Deceased patients:** Visual indicator (e.g., badge, icon, color)
- **Service Connected %:** Standard display (no special highlighting)
- **Missing data:** Display as "Not Available" (not hidden)

**Decision 5: Multi-Section Layout (Two Columns)**
- Sections: Personal Information, Contact, Insurance, Military Service, Additional Information
- Two-column format within sections for space efficiency
- Follows Vitals/Allergies/Medications page pattern

---

## 2. Objectives and Success Criteria

### 2.1 Objectives

**Primary Objectives:**
1. Provide **comprehensive demographic information** in a full-page view
2. Enable **quick access** to key demographics via dashboard widget
3. Support **patient identity verification** using multiple identifiers
4. Display **critical safety information** (deceased status, service connected %)
5. Maintain **consistency** with other clinical domain pages

**Secondary Objectives:**
1. Serve as **foundation** for other clinical domains (all domains reference patient demographics)
2. Demonstrate **medallion architecture** with additional demographic fields
3. Establish **reusable patterns** for read-only domain pages

### 2.2 Success Criteria

**Functional Requirements:**
- ✅ Demographics widget displays on dashboard with basic info + contact + insurance
- ✅ "View Full Demographics" link navigates to dedicated demographics page
- ✅ Full page displays all curated demographic fields in multi-section layout
- ✅ Deceased patients have clear visual indicator
- ✅ Missing data displays as "Not Available" (not blank or hidden)
- ✅ Page loads in < 500ms for typical patient
- ✅ Responsive design works on desktop, tablet, mobile

**Data Quality Requirements:**
- ✅ 100% of patients have basic demographics (name, DOB, sex, ICN)
- ✅ 90%+ of patients have address information
- ✅ 80%+ of patients have insurance information
- ✅ Service connected % accurately reflects patient eligibility

**UX Requirements:**
- ✅ Two-column layout efficiently uses screen space
- ✅ Sections are clearly labeled and visually separated
- ✅ Typography and styling consistent with Vitals/Allergies pages
- ✅ Navigation from widget → full page is intuitive

---

## 3. Prerequisites

### 3.1 Completed Work (Phase 1 - Widget Enhancement)

**Database Schema:**
- ✅ `Dim.InsuranceCompany` table created (17 insurance companies)
- ✅ `SPatient.SPatientAddress` table populated (100% patient coverage)
- ✅ `SPatient.SPatientInsurance` table populated (89% patient coverage)
- ✅ PostgreSQL `patient_demographics` table updated with address, phone, insurance fields

**ETL Pipeline:**
- ✅ Bronze ETL: `bronze_patient_address.py`, `bronze_patient_insurance.py`, `bronze_insurance_company.py`
- ✅ Silver ETL: `silver_patient.py` (updated with address/insurance joins)
- ✅ Gold ETL: `gold_patient.py` (updated schema)
- ✅ PostgreSQL Load: `load_postgres_patient.py` (automatic)

**Application:**
- ✅ `app/db/patient.py` - Query function returns address/insurance fields
- ✅ `app/templates/partials/demographics_widget.html` - Widget displays contact + insurance
- ✅ Demographics widget integrated into dashboard

### 3.2 Dependencies for Phase 2 (Full Page)

**Database Schema:**
- 🚧 Add fields to PostgreSQL `patient_demographics` table:
  - `marital_status` VARCHAR(25)
  - `religion` VARCHAR(50)
  - `service_connected_percent` DECIMAL(5,2)
  - `deceased_flag` CHAR(1)
  - `death_date` DATE

**ETL Pipeline:**
- 🚧 Update Silver ETL to extract marital status, religion from `SPatient.SPatient`
- 🚧 Update Silver ETL to extract service connected % from `SPatient.SPatientDisability`
- 🚧 Update Silver ETL to extract deceased flag and death date from `SPatient.SPatient`
- 🚧 Update Gold ETL to include new fields in final schema
- 🚧 Update PostgreSQL load script (automatic if using Polars → Pandas)

**Application:**
- 🚧 Create `app/routes/demographics.py` - Dedicated router (Pattern B)
- 🚧 Update `app/db/patient.py` - Add function to get complete demographics
- 🚧 Create `app/templates/patient_demographics.html` - Full page template
- 🚧 Add "View Full Demographics" link to widget footer
- 🚧 Add Demographics link to sidebar navigation

---

## 4. Data Architecture

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

### 4.1 Source Systems (Mock CDW)

**Primary Source Table:**
- **`SPatient.SPatient`** - Patient master demographic record
  - PatientSID, PatientICN, PatientSSN, ScrSSN
  - PatientName, PatientLastName, PatientFirstName
  - BirthDateTime, Age, Gender
  - DeceasedFlag, DeathDateTime
  - MaritalStatus, Religion
  - VeteranFlag, ServiceConnectedFlag
  - Sta3n (primary station)

**Related Tables:**
- **`SPatient.SPatientAddress`** - Patient addresses (home, work, temporary)
- **`SPatient.SPatientInsurance`** - Patient insurance policies
- **`SPatient.SPatientDisability`** - Service connected disability information
  - ServiceConnectedPercent (0-100%)
  - ServiceConnectedFlag
  - Agent Orange, POW, Radiation exposure (out of scope for Phase 2)
- **`Dim.InsuranceCompany`** - Insurance company names
- **`Dim.Sta3n`** - Station/facility names

### 4.2 Field Mappings

**Basic Demographics:**
| UI Field | Source Field | Source Table | Notes |
|----------|--------------|--------------|-------|
| Name | PatientLastName, PatientFirstName | SPatient.SPatient | Display as "LAST, First" |
| Date of Birth | BirthDateTime | SPatient.SPatient | Format as MM/DD/YYYY |
| Age | Age (calculated) | SPatient.SPatient | Recalculated in Silver ETL |
| Sex | Gender | SPatient.SPatient | M/F/U |
| SSN | PatientSSN | SPatient.SPatient | Display last 4 only |
| ICN | PatientICN | SPatient.SPatient | Full ICN |

**Contact Information:**
| UI Field | Source Field | Source Table | Notes |
|----------|--------------|--------------|-------|
| Phone | N/A | N/A | Hardcoded "Not available" (no phone table yet) |
| Address Line 1 | AddressLine1 | SPatient.SPatientAddress | Primary address |
| Address Line 2 | AddressLine2 | SPatient.SPatientAddress | Optional |
| City | City | SPatient.SPatientAddress | |
| State | StateProvince | SPatient.SPatientAddress | 2-letter abbreviation |
| ZIP | PostalCode | SPatient.SPatientAddress | |

**Insurance Information:**
| UI Field | Source Field | Source Table | Notes |
|----------|--------------|--------------|-------|
| Insurance Company | InsuranceCompanyName | Dim.InsuranceCompany | Via SPatientInsurance FK |

**Military Service & Eligibility (Phase 2):**
| UI Field | Source Field | Source Table | Notes |
|----------|--------------|--------------|-------|
| Service Connected % | ServiceConnectedPercent | SPatient.SPatientDisability | 0-100% |
| Primary Station | Sta3n | SPatient.SPatient | Joined to Dim.Sta3n for name |

**Additional Information (Phase 2):**
| UI Field | Source Field | Source Table | Notes |
|----------|--------------|--------------|-------|
| Marital Status | MaritalStatus | SPatient.SPatient | Single, Married, Divorced, etc. |
| Religion | Religion | SPatient.SPatient | For spiritual care coordination |
| Deceased | DeceasedFlag | SPatient.SPatient | Y/N flag |
| Date of Death | DeathDateTime | SPatient.SPatient | Only if deceased |

### 4.3 Data Quality Rules

**Primary Address Selection Logic:**
1. Prefer address with `IsActive = 1` (if available)
2. Prefer address with `AddressType = 'HOME'`
3. If multiple qualify, select most recent by `ModifiedDateTime`
4. If no addresses exist, display "Not Available"

**Primary Insurance Selection Logic:**
1. Prefer insurance with `Priority = 1` (if available)
2. If no priority set, select most recent by `PolicyEffectiveDate`
3. If no insurance exists, display "Not Available"

**Service Connected % Logic:**
1. Select record from `SPatient.SPatientDisability` matching `PatientSID`
2. If multiple records, select most recent
3. If no record exists, display "Not Available"
4. Display as integer percentage (e.g., "50%")

**Deceased Status Logic:**
1. If `DeceasedFlag = 'Y'`, display visual indicator (badge/icon)
2. If deceased, also display `DeathDateTime` formatted as MM/DD/YYYY
3. If `DeceasedFlag = 'N'` or NULL, no indicator

---

## 5. Database Schema

### 5.1 Current PostgreSQL Schema (Phase 1 Complete)

**Table:** `patient_demographics`

```sql
CREATE TABLE patient_demographics (
    patient_key VARCHAR(50) PRIMARY KEY,
    icn VARCHAR(50) UNIQUE NOT NULL,
    ssn VARCHAR(64),
    ssn_last4 VARCHAR(4),
    name_last VARCHAR(100),
    name_first VARCHAR(100),
    name_display VARCHAR(200),
    dob DATE,
    age INTEGER,
    sex VARCHAR(1),
    gender VARCHAR(50),
    primary_station VARCHAR(10),
    primary_station_name VARCHAR(200),

    -- Address fields (Phase 1 ✅)
    address_street1 VARCHAR(100),
    address_street2 VARCHAR(100),
    address_city VARCHAR(100),
    address_state VARCHAR(2),
    address_zip VARCHAR(10),

    -- Contact fields (Phase 1 ✅)
    phone_primary VARCHAR(20),

    -- Insurance fields (Phase 1 ✅)
    insurance_company_name VARCHAR(100),

    veteran_status VARCHAR(50),
    source_system VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
```sql
CREATE INDEX idx_patient_icn ON patient_demographics(icn);
CREATE INDEX idx_patient_name_last ON patient_demographics(name_last);
CREATE INDEX idx_patient_name_first ON patient_demographics(name_first);
CREATE INDEX idx_patient_ssn_last4 ON patient_demographics(ssn_last4);
CREATE INDEX idx_patient_station ON patient_demographics(primary_station);
CREATE INDEX idx_patient_dob ON patient_demographics(dob);
```

### 5.2 Planned Schema Updates (Phase 2)

**New Columns to Add:**

```sql
-- Phase 2: Additional demographic fields
ALTER TABLE patient_demographics
ADD COLUMN marital_status VARCHAR(25),
ADD COLUMN religion VARCHAR(50),
ADD COLUMN service_connected_percent DECIMAL(5,2),
ADD COLUMN deceased_flag CHAR(1),
ADD COLUMN death_date DATE;
```

**Updated Comments:**
```sql
COMMENT ON COLUMN patient_demographics.marital_status IS 'Marital status (Single, Married, Divorced, etc.)';
COMMENT ON COLUMN patient_demographics.religion IS 'Religion for spiritual care coordination';
COMMENT ON COLUMN patient_demographics.service_connected_percent IS 'Service connected disability percentage (0-100)';
COMMENT ON COLUMN patient_demographics.deceased_flag IS 'Deceased flag (Y/N)';
COMMENT ON COLUMN patient_demographics.death_date IS 'Date of death (if deceased)';
```

**Alternative: DDL Script (Drop/Recreate)**

For development, can use drop/recreate approach:

```sql
DROP TABLE IF EXISTS patient_demographics CASCADE;

CREATE TABLE patient_demographics (
    patient_key VARCHAR(50) PRIMARY KEY,
    icn VARCHAR(50) UNIQUE NOT NULL,
    ssn VARCHAR(64),
    ssn_last4 VARCHAR(4),
    name_last VARCHAR(100),
    name_first VARCHAR(100),
    name_display VARCHAR(200),
    dob DATE,
    age INTEGER,
    sex VARCHAR(1),
    primary_station VARCHAR(10),
    primary_station_name VARCHAR(200),

    -- Contact Information
    address_street1 VARCHAR(100),
    address_street2 VARCHAR(100),
    address_city VARCHAR(100),
    address_state VARCHAR(2),
    address_zip VARCHAR(10),
    phone_primary VARCHAR(20),

    -- Insurance Information
    insurance_company_name VARCHAR(100),

    -- Additional Demographics (Phase 2)
    marital_status VARCHAR(25),
    religion VARCHAR(50),

    -- Military Service (Phase 2)
    service_connected_percent DECIMAL(5,2),

    -- Critical Information (Phase 2)
    deceased_flag CHAR(1),
    death_date DATE,

    -- Metadata
    veteran_status VARCHAR(50),
    source_system VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. ETL Pipeline Design

### 6.1 Bronze Layer (Current State)

**Existing Bronze Extractors (Phase 1 ✅):**
- `etl/bronze_patient.py` - SPatient.SPatient table
- `etl/bronze_patient_address.py` - SPatient.SPatientAddress table
- `etl/bronze_patient_insurance.py` - SPatient.SPatientInsurance table
- `etl/bronze_insurance_company.py` - Dim.InsuranceCompany dimension

**Output:** Raw Parquet files in MinIO `bronze/` layer

### 6.2 Bronze Layer Updates (Phase 2)

**New Bronze Extractor:**
- `etl/bronze_patient_disability.py` - Extract from `SPatient.SPatientDisability`
  - Output: `bronze/cdwwork/patient_disability/patient_disability_raw.parquet`
  - Fields needed: `PatientSID`, `ServiceConnectedPercent`, `ServiceConnectedFlag`

**No changes needed to existing Bronze extractors** - marital_status, religion, deceased_flag, death_date already extracted in `bronze_patient.py` from `SPatient.SPatient`

### 6.3 Silver Layer (Current State)

**Current Implementation (Phase 1 ✅):**
- `etl/silver_patient.py`
  - Joins Bronze patient, address, insurance, insurance company
  - Selects primary address using logic (IsActive, AddressType='HOME', most recent)
  - Selects primary insurance using logic (Priority=1, most recent)
  - Hardcodes `phone_primary = "Not available"`
  - Outputs: `silver/patient/patient_cleaned.parquet`

### 6.4 Silver Layer Updates (Phase 2)

**Updates to `etl/silver_patient.py`:**

1. **Read Bronze patient_disability:**
   ```python
   df_disability = minio_client.read_parquet(
       build_bronze_path("cdwwork", "patient_disability", "patient_disability_raw.parquet")
   )
   ```

2. **Join disability data:**
   ```python
   df_patient = df_patient.join(
       df_disability.select(["PatientSID", "ServiceConnectedPercent"]),
       on="PatientSID",
       how="left"
   )
   ```

3. **Add new fields to Silver schema:**
   ```python
   df = df.with_columns([
       pl.col("MaritalStatus").str.strip_chars().alias("marital_status"),
       pl.col("Religion").str.strip_chars().alias("religion"),
       pl.col("ServiceConnectedPercent").alias("service_connected_percent"),
       pl.col("DeceasedFlag").alias("deceased_flag"),
       pl.col("DeathDateTime").cast(pl.Date).alias("death_date"),
   ])
   ```

4. **Update final column selection:**
   ```python
   df = df.select([
       # ... existing columns ...
       "marital_status",
       "religion",
       "service_connected_percent",
       "deceased_flag",
       "death_date",
   ])
   ```

### 6.5 Gold Layer Updates (Phase 2)

**Updates to `etl/gold_patient.py`:**

Simply include new fields in final Gold schema selection:
```python
df_gold = df_patient.select([
    "patient_key",
    "icn",
    # ... existing fields ...
    "marital_status",
    "religion",
    "service_connected_percent",
    "deceased_flag",
    "death_date",
    "source_system",
    "last_updated",
])
```

### 6.6 PostgreSQL Load (Phase 2)

**No code changes needed** - `etl/load_postgres_patient.py` automatically handles new columns when converting Polars → Pandas → PostgreSQL (via `.to_sql()`).

**Prerequisite:** PostgreSQL schema must be updated first (ALTER TABLE or DROP/CREATE).

---

## 7. API Endpoints

### 7.1 Current Endpoints (Phase 1 ✅)

**Widget Endpoint:**
- `GET /api/dashboard/widget/demographics/{icn}` - Returns HTML widget partial
  - Handler: `app/routes/patient.py::get_demographics_widget()`
  - Template: `app/templates/partials/demographics_widget.html`
  - Returns: Demographics widget HTML with contact + insurance sections

**Database Query Function:**
- `app/db/patient.py::get_patient_demographics(icn: str)`
  - Returns dictionary with all patient demographics fields
  - Currently includes: name, DOB, age, sex, SSN, address, phone, insurance, station

### 7.2 New Endpoints (Phase 2)

#### 7.2.1 Full Demographics Page Route

**Endpoint:** `GET /patient/{icn}/demographics`

**Purpose:** Display full demographics page for patient

**Handler:** `app/routes/demographics.py::get_patient_demographics_page(icn: str)`

**Implementation:**
```python
# app/routes/demographics.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.db.patient import get_patient_demographics

page_router = APIRouter(tags=["demographics-pages"])

@page_router.get("/patient/{icn}/demographics", response_class=HTMLResponse)
async def get_patient_demographics_page(request: Request, icn: str):
    """
    Full Demographics page for a specific patient.

    Displays comprehensive demographic information including:
    - Basic demographics (name, DOB, age, sex, SSN, ICN)
    - Contact information (phone, address)
    - Insurance information
    - Marital status, religion
    - Service connected percentage
    - Deceased status and date (if applicable)
    """
    # Get patient demographics from database
    patient = get_patient_demographics(icn)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Render full demographics page template
    return request.app.state.templates.TemplateResponse(
        "patient_demographics.html",
        {
            "request": request,
            "patient": patient,
            "active_page": "demographics"
        }
    )
```

**Registration in `app/main.py`:**
```python
from app.routes.demographics import page_router as demographics_page_router

app.include_router(demographics_page_router)
```

#### 7.2.2 Demographics Redirect Route (Optional)

**Endpoint:** `GET /demographics`

**Purpose:** Redirect to current patient's demographics (from CCOW context)

**Handler:** `app/routes/demographics.py::demographics_redirect()`

**Implementation:**
```python
@page_router.get("/demographics")
async def demographics_redirect(request: Request):
    """Redirect to current patient's demographics page."""
    # Get current patient from CCOW or session
    patient = await get_current_patient(request)

    if not patient:
        # Redirect to dashboard with message
        return RedirectResponse(url="/?message=no_patient_selected")

    return RedirectResponse(url=f"/patient/{patient['icn']}/demographics")
```

### 7.3 Updated Database Query Function (Phase 2)

**Function:** `app/db/patient.py::get_patient_demographics(icn: str)`

**Current Return Fields (Phase 1 ✅):**
```python
{
    "patient_key": str,
    "icn": str,
    "ssn_last4": str,
    "name_last": str,
    "name_first": str,
    "name_display": str,
    "dob": str,
    "age": int,
    "sex": str,
    "primary_station": str,
    "primary_station_name": str,
    "address_street1": str,
    "address_street2": str,
    "address_city": str,
    "address_state": str,
    "address_zip": str,
    "phone_primary": str,
    "insurance_company_name": str,
    "source_system": str,
    "last_updated": str
}
```

**Updated Return Fields (Phase 2):**
Add the following fields:
```python
{
    # ... existing fields ...
    "marital_status": str,
    "religion": str,
    "service_connected_percent": float,
    "deceased_flag": str,
    "death_date": str,
}
```

**Updated SQL Query:**
```sql
SELECT
    patient_key, icn, ssn_last4,
    name_last, name_first, name_display,
    dob, age, sex,
    primary_station, primary_station_name,
    address_street1, address_street2, address_city, address_state, address_zip,
    phone_primary,
    insurance_company_name,
    marital_status,
    religion,
    service_connected_percent,
    deceased_flag,
    death_date,
    source_system, last_updated
FROM patient_demographics
WHERE icn = :icn
```

---

## 8. UI/UX Design

### 8.1 Demographics Widget (Current Implementation ✅)

**Location:** Dashboard grid, position varies (currently row 1, column 1)

**Size:** 1x1 (standard widget)

**Template:** `app/templates/partials/demographics_widget.html`

**Sections:**
1. **Primary Info** (always visible)
   - Name, DOB, Gender, SSN
2. **Contact** (conditional - visible if address exists)
   - Phone, Address (multi-line)
3. **Insurance** (conditional - visible if insurance exists)
   - Provider (insurance company name)

**Widget Footer (Phase 2 Update):**
Add "View Full Demographics" link:
```html
<!-- Widget Footer -->
<div class="widget__footer">
    <a href="/patient/{{ patient.icn }}/demographics" class="widget__link">
        View Full Demographics <i class="fa-solid fa-arrow-right"></i>
    </a>
</div>
```

**Current Implementation Status:** ✅ Complete (minus footer link)

### 8.2 Full Demographics Page (Phase 2 Design)

**Route:** `/patient/{icn}/demographics`

**Template:** `app/templates/patient_demographics.html`

**Layout Pattern:** Follows Vitals/Allergies/Medications page structure

#### 8.2.1 Page Structure

```html
{% extends "base.html" %}

{% block title %}Demographics - {{ patient.name_display }}{% endblock %}

{% block content %}
<div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
        <div class="page-header__title-group">
            <i class="fa-solid fa-user page-header__icon"></i>
            <div>
                <h1 class="page-header__title">Patient Demographics</h1>
                <p class="page-header__subtitle">{{ patient.name_display }}</p>
            </div>
        </div>

        <!-- Deceased Indicator (if applicable) -->
        {% if patient.deceased_flag == 'Y' %}
        <div class="deceased-badge">
            <i class="fa-solid fa-cross"></i>
            Deceased
            {% if patient.death_date %}
            - {{ patient.death_date }}
            {% endif %}
        </div>
        {% endif %}
    </div>

    <!-- Demographics Content -->
    <div class="demographics-content">
        <!-- Section 1: Personal Information -->
        <div class="demo-section-card">
            <h2 class="demo-section-card__title">
                <i class="fa-solid fa-id-card"></i>
                Personal Information
            </h2>
            <div class="demo-grid">
                <div class="demo-field">
                    <span class="demo-field__label">Full Name</span>
                    <span class="demo-field__value">{{ patient.name_display }}</span>
                </div>
                <div class="demo-field">
                    <span class="demo-field__label">ICN</span>
                    <span class="demo-field__value">{{ patient.icn }}</span>
                </div>
                <div class="demo-field">
                    <span class="demo-field__label">Date of Birth</span>
                    <span class="demo-field__value">{{ patient.dob }} ({{ patient.age }} years old)</span>
                </div>
                <div class="demo-field">
                    <span class="demo-field__label">SSN</span>
                    <span class="demo-field__value">***-**-{{ patient.ssn_last4 }}</span>
                </div>
                <div class="demo-field">
                    <span class="demo-field__label">Sex</span>
                    <span class="demo-field__value">{{ patient.sex }}</span>
                </div>
                <div class="demo-field">
                    <span class="demo-field__label">Marital Status</span>
                    <span class="demo-field__value">{{ patient.marital_status or "Not Available" }}</span>
                </div>
                <div class="demo-field">
                    <span class="demo-field__label">Religion</span>
                    <span class="demo-field__value">{{ patient.religion or "Not Available" }}</span>
                </div>
                <div class="demo-field">
                    <span class="demo-field__label">Primary Facility</span>
                    <span class="demo-field__value">{{ patient.primary_station_name }}</span>
                </div>
            </div>
        </div>

        <!-- Section 2: Contact Information -->
        <div class="demo-section-card">
            <h2 class="demo-section-card__title">
                <i class="fa-solid fa-address-book"></i>
                Contact Information
            </h2>
            <div class="demo-grid">
                <div class="demo-field demo-field--full-width">
                    <span class="demo-field__label">Phone</span>
                    <span class="demo-field__value">{{ patient.phone_primary or "Not Available" }}</span>
                </div>
                <div class="demo-field demo-field--full-width">
                    <span class="demo-field__label">Address</span>
                    <span class="demo-field__value">
                        {% if patient.address_street1 %}
                            {{ patient.address_street1 }}<br>
                            {% if patient.address_street2 %}{{ patient.address_street2 }}<br>{% endif %}
                            {{ patient.address_city }}{% if patient.address_city and patient.address_state %}, {% endif %}{{ patient.address_state }} {{ patient.address_zip }}
                        {% else %}
                            Not Available
                        {% endif %}
                    </span>
                </div>
            </div>
        </div>

        <!-- Section 3: Insurance Information -->
        <div class="demo-section-card">
            <h2 class="demo-section-card__title">
                <i class="fa-solid fa-shield-halved"></i>
                Insurance Information
            </h2>
            <div class="demo-grid">
                <div class="demo-field">
                    <span class="demo-field__label">Primary Insurance</span>
                    <span class="demo-field__value">{{ patient.insurance_company_name or "Not Available" }}</span>
                </div>
            </div>
        </div>

        <!-- Section 4: Military Service & Eligibility -->
        <div class="demo-section-card">
            <h2 class="demo-section-card__title">
                <i class="fa-solid fa-flag-usa"></i>
                Military Service & Eligibility
            </h2>
            <div class="demo-grid">
                <div class="demo-field">
                    <span class="demo-field__label">Service Connected %</span>
                    <span class="demo-field__value">
                        {% if patient.service_connected_percent is not none %}
                            {{ patient.service_connected_percent }}%
                        {% else %}
                            Not Available
                        {% endif %}
                    </span>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### 8.2.2 CSS Styling

**New CSS Classes Needed:**

```css
/* Demographics Page Specific Styles */

/* Deceased Badge in Page Header */
.deceased-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #fee2e2;
    border: 1px solid #fca5a5;
    border-radius: 0.375rem;
    color: #991b1b;
    font-weight: 600;
    font-size: 0.875rem;
}

.deceased-badge i {
    font-size: 1rem;
}

/* Demographics Content Container */
.demographics-content {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Demographics Section Cards */
.demo-section-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.5rem;
}

.demo-section-card__title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 1.25rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e5e7eb;
}

.demo-section-card__title i {
    color: #4f46e5;
    font-size: 1.25rem;
}

/* Demographics Field Grid (Two Columns) */
.demo-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
}

.demo-field {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
}

.demo-field--full-width {
    grid-column: span 2;
}

.demo-field__label {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}

.demo-field__value {
    font-size: 0.9375rem;
    color: #111827;
    line-height: 1.5;
}

/* Responsive: Mobile (single column) */
@media (max-width: 767px) {
    .demo-grid {
        grid-template-columns: 1fr;
    }

    .demo-field--full-width {
        grid-column: span 1;
    }

    .demo-section-card {
        padding: 1rem;
    }
}
```

#### 8.2.3 Visual Design Notes

**Typography:**
- Section titles: 1.125rem, font-weight 600
- Field labels: 0.8125rem, uppercase, letter-spaced, muted gray
- Field values: 0.9375rem, normal weight, dark gray

**Colors:**
- Section cards: White background, light gray border
- Section titles: Primary blue icon (#4f46e5), dark text (#111827)
- Field labels: Muted gray (#6b7280)
- Field values: Dark text (#111827)
- Deceased badge: Red background (#fee2e2), dark red text (#991b1b)

**Spacing:**
- Section cards: 1.5rem gap between cards
- Card padding: 1.5rem
- Field grid gap: 1.25rem
- Field label-value gap: 0.375rem

**Responsive Behavior:**
- Desktop: 2-column grid for fields
- Tablet: 2-column grid maintained
- Mobile: Single column grid

---

## 9. Implementation Roadmap

### 9.1 Phase 1: Widget Enhancement ✅ Complete (2025-12-11)

**Tasks Completed:**
1. ✅ Created `Dim.InsuranceCompany` table (17 companies)
2. ✅ Populated `SPatient.SPatientAddress` (100% coverage - 37 patients)
3. ✅ Populated `SPatient.SPatientInsurance` (89% coverage - 33 patients)
4. ✅ Created Bronze ETL scripts (address, insurance, insurance company)
5. ✅ Updated Silver ETL with address/insurance joins
6. ✅ Updated Gold ETL with new fields
7. ✅ Updated PostgreSQL schema (address, phone, insurance columns)
8. ✅ Updated `app/db/patient.py` query function
9. ✅ Updated `app/templates/partials/demographics_widget.html`
10. ✅ Tested end-to-end (CDW → ETL → PostgreSQL → UI)

### 9.2 Phase 2: Full Demographics Page ✅ Complete (2025-12-14)

**Estimated Duration:** 3-4 days
**Status:** ✅ Complete - All Days (1-4) Implemented (2025-12-14)

#### Day 1: Database Schema & Bronze ETL ✅ Complete (2025-12-14)

**Tasks Completed:**
1. Create `etl/bronze_patient_disability.py`
   - Extract from `SPatient.SPatientDisability`
   - Output Bronze Parquet
2. Run Bronze extraction
3. Verify Parquet file in MinIO
4. Update PostgreSQL schema (ADD COLUMN or DROP/CREATE)
   - Add: marital_status, religion, service_connected_percent, deceased_flag, death_date
5. Execute DDL in serving database

**Deliverables:**
- ✅ `etl/bronze_patient_disability.py` - Created
- ✅ Bronze Parquet: `bronze/cdwwork/patient_disability/patient_disability_raw.parquet` (10 records)
- ✅ Updated `db/ddl/patient_demographics.sql` (v3.0)
- ✅ PostgreSQL schema updated with 5 new columns

**Testing Results:**
- ✅ Bronze Parquet row count: 10 (matches source table)
- ✅ PostgreSQL new columns verified: marital_status, religion, service_connected_percent, deceased_flag, death_date

#### Day 2: Silver & Gold ETL Updates ✅ Complete (2025-12-14)

**Tasks Completed:**
1. Update `etl/silver_patient.py`
   - Read Bronze patient_disability
   - Join disability data (service connected %)
   - Extract marital_status, religion, deceased_flag, death_date from existing patient Bronze
   - Add new fields to Silver schema
2. Update `etl/gold_patient.py`
   - Include new fields in Gold schema
3. Run Silver and Gold ETL
4. Verify output Parquet files

**Deliverables:**
- ✅ Updated `etl/silver_patient.py` (v3.0) with disability join
- ✅ Updated `etl/gold_patient.py` (v3.0) with Phase 2 fields
- ✅ Silver Parquet with 23 columns (18 original + 5 Phase 2)
- ✅ Gold Parquet with 27 columns (22 original + 5 Phase 2)

**Testing Results:**
- ✅ Silver join correctly maps service_connected_percent (10 patients)
- ✅ All Phase 2 fields present with valid data (marital_status, religion, etc.)
- ✅ 36 patients processed successfully through Silver and Gold

#### Day 3: PostgreSQL Load & API Endpoints ✅ Complete (2025-12-14)

**Tasks Completed:**
1. Run `etl/load_postgres_patient.py` to load updated Gold data
2. Verify data in PostgreSQL
3. Update `app/db/patient.py::get_patient_demographics()` query
   - Add 5 new fields to SELECT statement
   - Add 5 new fields to return dictionary
4. Create `app/routes/demographics.py`
   - Implement page_router
   - Implement `get_patient_demographics_page()` handler
   - Implement optional redirect route
5. Register demographics router in `app/main.py`
6. Test API endpoints

**Deliverables:**
- ✅ Data loaded in PostgreSQL (36 patients with 27 columns including Phase 2 fields)
- ✅ Updated `app/db/patient.py::get_patient_demographics()` - Returns all 25 fields
- ✅ Created `app/routes/demographics.py` - Pattern B router with page routes
- ✅ Updated `app/main.py` - Registered demographics router

**Testing Results:**
- ✅ PostgreSQL verified: All Phase 2 fields present with data
- ✅ Query function test PASSED: Returns all fields correctly (marital_status: DIVORCED, religion: Christian, service_connected_percent: 51.0, etc.)
- ✅ API endpoint created: `GET /patient/{icn}/demographics` (template pending)
- ✅ Router registered and accessible

#### Day 4: Full Page Template & Styling ✅ Complete (2025-12-14)

**Tasks Completed:**
1. ✅ Created `app/templates/patient_demographics.html`
   - Implemented multi-section layout (4 sections: Personal, Contact, Insurance, Military)
   - Implemented two-column responsive field grid
   - Implemented deceased badge (conditional display)
   - Handled "Not Available" for missing fields
2. ✅ Added CSS to `app/static/styles.css`
   - Demographics page specific styles (~90 lines)
   - Deceased badge styles (.deceased-badge)
   - Responsive grid styles (.demo-grid, .demo-field)
   - Section card styles (.demo-section-card)
3. ✅ Updated `app/templates/partials/demographics_widget.html`
   - Added "View Full Demographics" link using widget-action pattern
   - Added minimal footer for visual spacing (0.25rem padding)
4. ✅ Tested full page in UI

**Deliverables:**
- ✅ `app/templates/patient_demographics.html` - 4-section responsive layout
- ✅ Updated `app/static/styles.css` - Added ~90 lines for demographics page
- ✅ Updated `app/templates/partials/demographics_widget.html` - Added widget-action link and footer
- ✅ Updated `app/routes/demographics.py` - Fixed template rendering

**Testing Results:**
- ✅ Viewed demographics page for deceased patient (ICN1011530429) - Badge displays correctly
- ✅ Viewed page for patient with service_connected_percent (ICN100003) - 51.0% displayed
- ✅ Viewed page for patient without service_connected_percent (ICN100009) - "Not Available" displayed
- ✅ Responsive design verified (desktop 2-col, mobile 1-col)
- ✅ "View Full Demographics" link works from widget
- ✅ All Phase 2 fields display correctly

#### Day 5: Integration Testing & Documentation

**Tasks:**
1. End-to-end testing (CDW → ETL → serving DB → UI)
2. Test edge cases:
   - Patient with all fields populated
   - Patient with minimal fields (no insurance, no address, no service connected %)
   - Deceased patient
   - Patient with very long address
3. Update documentation
   - Mark Phase 2 as complete in this document
   - Update `docs/implementation-roadmap.md`
   - Update sidebar link status in `base.html`

**Deliverables:**
- Test results documented
- Updated design document (status: "Complete")
- Updated roadmap document

**Success Criteria:**
- ✅ Full demographics page displays correctly for all test patients
- ✅ All new fields populated correctly
- ✅ Deceased badge appears for deceased patients only
- ✅ "Not Available" displays for missing optional fields
- ✅ Page loads in < 500ms
- ✅ Responsive design works on all screen sizes
- ✅ Widget → full page navigation works

---

## 10. Testing Strategy

### 10.1 Unit Tests

**Database Layer:**
- Test `get_patient_demographics()` returns all fields including Phase 2 additions
- Test NULL/None handling for optional fields
- Test deceased_flag logic

**ETL Layer:**
- Test Bronze extraction for patient_disability
- Test Silver join logic (disability data)
- Test service_connected_percent calculation
- Test deceased patient data flow

### 10.2 Integration Tests

**End-to-End Flow:**
1. Insert/update test data in CDWWork
2. Run Bronze/Silver/Gold ETL
3. Load into serving database
4. Query via application
5. Render in full demographics page

**Test Cases:**

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| Patient with full data | All fields populated | All sections display with data |
| Patient without insurance | No insurance record | Insurance shows "Not Available" |
| Patient without address | No address record | Contact shows "Not Available" |
| Deceased patient | DeceasedFlag = 'Y' | Deceased badge appears with death date |
| Service connected patient | ServiceConnectedPercent = 50 | "50%" displays in Military Service section |
| Non-service connected | No disability record | Service Connected shows "Not Available" |
| Missing marital status | MaritalStatus NULL | Marital Status shows "Not Available" |
| Missing religion | Religion NULL | Religion shows "Not Available" |
| Long address | Address exceeds typical length | Address wraps correctly, no overflow |

### 10.3 UI Testing

**Manual Testing:**
- View full demographics page for 10+ different patients
- Test navigation: widget → full page link
- Test navigation: sidebar → demographics page
- Verify all sections display correctly
- Verify two-column grid on desktop
- Verify single-column stack on mobile
- Verify deceased badge styling
- Verify "Not Available" styling matches design

**Accessibility Testing:**
- Keyboard navigation works
- Screen reader announces sections correctly
- Color contrast meets WCAG AA standards
- Focus indicators visible

---

## 11. Security and Privacy

### 11.1 Data Protection

**PHI/PII Fields:**
- Full SSN (encrypted/hashed in production)
- Full address
- Phone number
- Insurance information
- Religion (sensitive personal information)

**Access Control (Future):**
- Require authentication to view demographics
- Log all demographics page views (audit trail)
- Role-based access control for sensitive fields

### 11.2 Display Conventions

**SSN Display:**
- Always display as `***-**-{last4}` in UI
- Never display full SSN in HTML source or browser console

**Deceased Patient Handling:**
- Clearly indicate deceased status (patient safety)
- Display death date if available
- Consider UI implications (graying out deceased patients in search results - future enhancement)

---

## 12. Appendices

### 12.1 Related Documents

- `docs/patient-dashboard-design.md` - Dashboard widget specification
- `docs/spec/med-z1-architecture.md` - Routing patterns and architectural decisions
- `docs/implementation-roadmap.md` - Overall project roadmap
- `docs/vitals-design.md` - Vitals page pattern (template for demographics page)
- `docs/allergies-design.md` - Allergies page pattern (template for demographics page)

### 12.2 Mock Data Coverage

**Current Mock Data (37 patients):**
- ✅ 100% have basic demographics (name, DOB, sex, ICN, SSN)
- ✅ 100% have address (37/37 patients)
- ✅ 89% have insurance (33/37 patients)
- 🚧 TBD: % with marital status populated
- 🚧 TBD: % with religion populated
- 🚧 TBD: % with service connected % populated
- 🚧 TBD: # of deceased patients in mock data

### 12.3 Future Enhancements (Post-MVP)

**Phase 3 Enhancements (Potential):**
- Emergency Contact / Next of Kin information
- Multiple phone numbers (home, work, mobile) with type labels
- Email address
- Preferred language
- Race/Ethnicity (if required for reporting)
- Multiple addresses with type (home, work, temporary)
- Multiple insurance policies (primary, secondary, tertiary)
- Insurance plan details (member ID, group number, effective dates)
- Service history timeline (deployment dates, discharge type)
- Detailed disability information page (separate from demographics)

**UI Enhancements (Potential):**
- Print-friendly view
- Export to PDF
- "Edit Demographics" button (requires full EHR integration)
- Historical demographics changes (audit trail view)
- Comparison view (previous vs. current demographics)

---

**End of Document**
