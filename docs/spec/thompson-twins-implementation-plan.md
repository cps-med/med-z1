# Thompson Twins Implementation Plan

**Document Version:** v2.1
**Last Updated:** February 9, 2026
**Status:** ✅ Bailey Complete, 🔧 Alananah/Joe In Progress
**Related Documents:**
- Requirements: `docs/spec/thompson-twins-patient-reqs.md` (v3.2)
- Architecture: `docs/spec/med-z1-architecture.md`
- Error Analysis: `docs/spec/thompson-alananah-errors-found.md` (Alananah script corrections needed)

---

## Version History

### v2.1 (2026-02-09)
- **Added schema reference section** with warnings about common INSERT errors
- **Added link to error analysis document** (`thompson-alananah-errors-found.md`)
- **Updated status:** Bailey complete, Alananah/Joe in progress (corrections needed)
- **Cross-referenced** Thompson-Bailey.sql as authoritative template

### v2.0 (2026-02-08)
- **Added third sibling:** Joe Thompson (PatientSID 2003, PersonSID 20003, ICN200003)
  - Very healthy patient (minimal chronic disease)
  - Purpose: Healthy control case for comparison testing
  - Charlson Comorbidity Index: 0 (excellent prognosis)
- **Updated SID allocations:** Added Joe's ranges (RxOutpatSID 8086-8093, etc.)
- **Updated validation queries:** All queries now include PatientSID/PersonSID 2003/20003
- **Updated implementation checklist:** Added Phase 3.5 (CDWWork Joe) and Phase 5.5 (CDWWork2 Joe)
- **Updated estimated totals:** 6 scripts (3 patients × 2 databases), ~1410 total rows

### v1.0 (2026-02-08)
- Initial implementation plan for Bailey and Alananah Thompson
- 4 scripts (2 patients × 2 databases)
- Comprehensive SID allocation strategy and script templates

---

## Important: Schema References

**⚠️ CRITICAL:** Use `mock/sql-server/cdwwork/insert/Thompson-Bailey.sql` as the **authoritative template** for all INSERT statement structures. Bailey's script has been tested and verified to work correctly.

**Common Errors to Avoid:**
- ❌ Incorrect field order in VALUES clause
- ❌ Wrong data types (strings where integers expected)
- ❌ Missing or extra fields in VALUES
- ❌ Using field names from other tables (e.g., 'PtIEN' doesn't belong in Immunization.PatientImmunization)

**Schema Definition Files (for field names and data types):**
- CDWWork: `mock/sql-server/cdwwork/create/*.sql`
- CDWWork2: `mock/sql-server/cdwwork2/create/*.sql`

**Known Issues:**
- `Thompson-Alananah.sql` (draft) contains structural errors in INSERT statements - see `docs/spec/thompson-alananah-errors-found.md` for details
- Always verify VALUES clause matches column list exactly

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Schema Analysis](#schema-analysis)
3. [SID Allocation Strategy](#sid-allocation-strategy)
4. [Dimension Table Mappings](#dimension-table-mappings)
5. [Date Generation Algorithms](#date-generation-algorithms)
6. [Implementation Sequence](#implementation-sequence)
7. [Script Templates](#script-templates)
8. [Validation Procedures](#validation-procedures)

---

## Executive Summary

This implementation plan provides detailed technical guidance for creating SQL insert scripts for the Thompson Twins test patients (Bailey, Alananah, and Joe Thompson). The plan covers:

- **SID range allocation** to avoid collisions with existing data
- **Dimension table mappings** for foreign key references
- **Date generation strategies** for historical (fixed) and current (relative) data
- **Implementation sequencing** to respect table dependencies
- **Script templates** with inline documentation patterns

**Key Facts:**
- **6 total scripts:** 3 patients × 2 databases (CDWWork, CDWWork2)
- **10 clinical domains** per patient
- **~900-1200 total INSERT statements** (estimated)
- **Estimated effort:** 3-4 days for script development, 1 day for testing

---

## Schema Analysis

### 1.1 CDWWork (VistA-based, Bay Pines 2010-2025)

**Primary Key Patterns:**

| Table | Primary Key | Type | Strategy |
|-------|-------------|------|----------|
| `SPatient.SPatient` | PatientSID | Manual | Use 2001/2002/2003 |
| `Vital.VitalSign` | VitalSignSID | IDENTITY(1,1) | Auto-increment (start ~60001+) |
| `Inpat.Inpatient` | InpatientSID | IDENTITY(1,1) | Auto-increment (start ~70001+) |
| `RxOut.RxOutpat` | RxOutpatSID | Manual | Use 8000+ series |
| `Allergy.PatientAllergy` | PatientAllergySID | IDENTITY(1,1) | Auto-increment |
| `TIU.TIUDocument_8925` | TIUDocumentSID | IDENTITY(1,1) | Auto-increment (start ~90001+) |
| `Immunization.PatientImmunization` | PatientImmunizationSID | IDENTITY(1,1) | Auto-increment |
| `Outpat.ProblemList` | ProblemSID | IDENTITY(1,1) | Auto-increment |
| `Chem.LabChem` | LabChemSID | IDENTITY(1,1) | Auto-increment |

**Key Observations:**
- ✅ Most tables use IDENTITY columns → We do NOT specify SIDs in INSERT statements
- ⚠️ `RxOutpat.RxOutpatSID` and `SPatient.PatientSID` are manual → We must assign specific values
- ✅ Foreign keys reference dimension tables (Sta3n 516 for Bay Pines)

### 1.2 CDWWork2 (Cerner-based, Walla Walla 2025-2026)

**Primary Key Patterns:**

| Table | Primary Key | Type | Strategy |
|-------|-------------|------|----------|
| `VeteranMill.SPerson` | PersonSID | IDENTITY(1,1) | Use SET IDENTITY_INSERT ON, specify 20001/20002/20003 |
| `VitalMill.VitalResult` | VitalResultSID | IDENTITY(1,1) | Auto-increment |
| `EncMill.Encounter` | EncounterSID | IDENTITY(1,1) | Auto-increment |
| `EncMill.ProblemList` | ProblemSID | IDENTITY(1,1) | Auto-increment |
| `ImmunizationMill.VaccineAdmin` | VaccineAdminSID | IDENTITY(1,1) | Auto-increment |

**Key Observations:**
- ✅ Cerner schema has fewer tables (domains like Medications, Labs, Clinical Notes NOT YET implemented in CDWWork2)
- ⚠️ **Scope Reduction:** Only implement Demographics, Vitals, Encounters, Problems, Immunizations for CDWWork2
- ✅ Sta3n 687 for Walla Walla

### 1.3 Missing CDWWork2 Tables

**Not yet implemented in CDWWork2 (skip for Thompson Twins initial implementation):**
- Medications (no RxMill schema)
- Clinical Notes (no DocumentMill schema)
- Laboratory Results (no LabMill schema)
- Allergies (no AllergyMill schema fully populated)
- Patient Flags (no FlagMill schema)

**Recommendation:** Populate only CDWWork for comprehensive data, CDWWork2 for limited domains per existing schema.

---

## SID Allocation Strategy

### 2.1 Allocation Principles

1. **Avoid Collisions:** Thompson Twins data uses SID ranges ABOVE existing test patients
2. **Clear Ranges:** Each patient gets dedicated SID ranges within each domain
3. **Predictable Patterns:** Bailey uses lower range (2001), Alananah uses middle range (2002), Joe uses upper range (2003)
4. **Future-Proof:** Leave gaps for future test patients

### 2.2 Existing SID Ranges (Summary)

Based on analysis of existing insert scripts:

- **PatientSID:** 1001-1027 (existing), 1606020-1606030 (test patients)
- **RxOutpatSID:** 5001-5080 (existing)
- **InpatientSID:** 1638001-1638010 (existing, limited BCMA test data)
- **VitalSignSID:** IDENTITY (auto-increment from 1+)
- **TIUDocumentSID:** IDENTITY (auto-increment)

### 2.3 Thompson Twins SID Allocation Table

| Domain | Table | Bailey Range | Alananah Range | Joe Range | Notes |
|--------|-------|--------------|----------------|-----------|-------|
| **Demographics** | SPatient.SPatient | PatientSID = 2001 | PatientSID = 2002 | PatientSID = 2003 | Manual assignment |
| **Demographics (CDWWork2)** | VeteranMill.SPerson | PersonSID = 20001 | PersonSID = 20002 | PersonSID = 20003 | Use IDENTITY_INSERT ON |
| **Vitals** | Vital.VitalSign | Auto (~60001-60064) | Auto (~60065-60128) | Auto (~60129-60184) | IDENTITY column |
| **Medications** | RxOut.RxOutpat | 8001-8045 (45 meds) | 8046-8085 (40 meds) | 8086-8093 (8 meds) | Manual assignment |
| **Encounters** | Inpat.Inpatient | Auto (~70001-70032) | Auto (~70033-70060) | Auto (~70061-70063) | IDENTITY column |
| **Clinical Notes** | TIU.TIUDocument_8925 | Auto (~90001-90220) | Auto (~90221-90400) | Auto (~90401-90460) | IDENTITY column |
| **Immunizations** | Immunization.PatientImmunization | Auto (Bailey's 42) | Auto (Alananah's 40) | Auto (Joe's 40) | IDENTITY column |
| **Problems** | Outpat.ProblemList | Auto (Bailey's 18) | Auto (Alananah's 16) | Auto (Joe's 2) | IDENTITY column |
| **Labs** | Chem.LabChem | Auto (Bailey's 160) | Auto (Alananah's 140) | Auto (Joe's 60) | IDENTITY column |
| **Allergies** | Allergy.PatientAllergy | Auto (Bailey's 2) | Auto (Alananah's 2) | N/A (Joe: NKDA) | IDENTITY column |
| **Patient Flags** | SPatient.PatientRecordFlagAssignment | Auto (Bailey's 2) | Auto (Alananah's 2) | N/A (Joe: 0 flags) | IDENTITY column |

**Total Estimated Rows:**
- **Bailey:** ~600 rows across all domains
- **Alananah:** ~540 rows across all domains
- **Joe:** ~270 rows across all domains (healthy patient, minimal data)
- **Combined:** ~1410 rows (CDWWork only)

### 2.4 How to Handle IDENTITY Columns

For tables with IDENTITY columns, we have two approaches:

**Approach A: Let SQL Server auto-assign SIDs (RECOMMENDED)**
```sql
-- DO NOT specify VitalSignSID in column list or VALUES
INSERT INTO Vital.VitalSign (
    PatientSID,
    VitalTypeSID,
    VitalSignTakenDateTime,
    NumericValue,
    Sta3n
)
VALUES
    (2001, 6, '2010-06-16', 185.0, 516),  -- Weight, SID auto-assigned
    (2001, 1, '2010-06-16', NULL, 516);    -- BP, SID auto-assigned (use ResultValue for "125/78")
```

**Approach B: Explicitly set IDENTITY values (for specific SID control)**
```sql
SET IDENTITY_INSERT Vital.VitalSign ON;
GO

INSERT INTO Vital.VitalSign (
    VitalSignSID,      -- NOW we CAN specify it
    PatientSID,
    VitalTypeSID,
    ...
)
VALUES
    (60001, 2001, 6, '2010-06-16', 185.0, 516);

SET IDENTITY_INSERT Vital.VitalSign OFF;
GO
```

**Recommendation:** Use Approach A (auto-assign) for simplicity. Only use Approach B if you need specific SIDs for testing/debugging.

---

## Dimension Table Mappings

### 3.1 Station Numbers (Dim.Sta3n)

**Available Sta3n values (from existing data):**

| Sta3n | Facility Name | Use For |
|-------|---------------|---------|
| 508 | Atlanta, GA | Existing test patients |
| 516 | **Bay Pines, FL** | **Thompson Twins (CDWWork 2010-2025)** ✅ |
| 552 | Dayton, OH | Existing test patients |
| 687 | **Walla Walla, WA** | **Thompson Twins (CDWWork2 2025-2026)** ✅ |
| 688 | Washington, DC | Existing test patients |

**Usage:**
- Use `Sta3n = 516` for ALL CDWWork records (Bay Pines)
- Use `Sta3n = 687` for ALL CDWWork2 records (Walla Walla)

### 3.2 Location Dimension (Dim.Location)

**Critical:** Locations are facility-specific (duplicated per Sta3n with same names).

**To find LocationSID for a specific location:**
```sql
-- Bay Pines (Sta3n 516) - Primary Care Clinic A
SELECT LocationSID, LocationName, LocationType, Sta3n
FROM Dim.Location
WHERE Sta3n = 516 AND LocationName = 'Primary Care Clinic A';
-- Result: LocationSID = (will vary, use query to find)

-- Walla Walla (Sta3n 687) - Primary Care Clinic A
SELECT LocationSID, LocationName, LocationType, Sta3n
FROM Dim.Location
WHERE Sta3n = 687 AND LocationName = 'Primary Care Clinic A';
-- Result: LocationSID = (different from 516)
```

**Common locations available (per Sta3n):**

**Inpatient Wards:**
- Medicine Ward 5A, 5B, 6A (Inpatient)
- Surgery Ward 7A, 7B (Inpatient)
- Medical ICU, Surgical ICU, Cardiac ICU (Inpatient)
- Cardiology Ward 3A (Inpatient)
- Oncology Ward 8A (Inpatient)
- Neurology Ward 6B (Inpatient)
- Psychiatry Ward 2A (Inpatient)

**Outpatient Clinics:**
- Primary Care Clinic A, B, C (Outpatient)
- Cardiology Clinic, Endocrinology Clinic, Gastroenterology Clinic (Outpatient)
- Mental Health Clinic, PTSD Clinic (Outpatient)
- Oncology Clinic, Pulmonology Clinic, Nephrology Clinic (Outpatient)

**Other:**
- Emergency Department (Emergency)
- Laboratory - Main Lab, Phlebotomy Station A/B (Laboratory)
- Pharmacy - Outpatient (Pharmacy)

**Recommendation:** For Thompson Twins scripts, use subqueries to dynamically look up LocationSID:
```sql
-- Example for Inpatient Encounter (Psychiatry admission)
INSERT INTO Inpat.Inpatient (
    PatientSID,
    AdmitDateTime,
    AdmitLocationSID,
    ...
)
VALUES (
    2001,
    '2016-09-12 08:30:00',
    (SELECT LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationName = 'Psychiatry Ward 2A' AND LocationType = 'Inpatient'),
    ...
);
```

This approach avoids hardcoding LocationSIDs and works even if `LocationSID` IDENTITY values change.

### 3.3 Vital Type Dimension (Dim.VitalType)

**Available VitalTypeSIDs (standardized, no Sta3n dependency):**

| VitalTypeSID | VitalType | Abbreviation | UnitOfMeasure | Usage |
|--------------|-----------|--------------|---------------|-------|
| 1 | BLOOD PRESSURE | BP | mmHg | Use `ResultValue = '125/78'`, leave `Systolic/Diastolic` populated |
| 2 | TEMPERATURE | T | F | Use `NumericValue = 98.6` |
| 3 | PULSE | P | /min | Use `NumericValue = 72` |
| 4 | RESPIRATION | R | /min | Use `NumericValue = 16` |
| 5 | HEIGHT | HT | in | Use `NumericValue = 70` |
| 6 | WEIGHT | WT | lb | Use `NumericValue = 185.0` |
| 7 | PAIN | PN | 0-10 | Use `NumericValue = 5` |
| 8 | PULSE OXIMETRY | POX | % | Use `NumericValue = 98` |
| 9 | BLOOD GLUCOSE | BG | mg/dL | Use `NumericValue = 110` |
| 10 | BMI | BMI | kg/m^2 | Use `NumericValue = 26.5` (calculated) |

**Typical vital sign set (per patient visit):**
```sql
-- Example: Quarterly vitals for Bailey Thompson
-- Visit Date: 2010-06-16 (initial VA enrollment)

-- Height (once, doesn't change for adults)
INSERT INTO Vital.VitalSign (...) VALUES (..., 5, ..., 70.0, ...);  -- 70 inches

-- Weight (every visit)
INSERT INTO Vital.VitalSign (...) VALUES (..., 6, ..., 185.0, ...);  -- 185 lbs

-- Blood Pressure
INSERT INTO Vital.VitalSign (...) VALUES (..., 1, ..., NULL, ..., 125, 78, ...);  -- 125/78

-- Pulse
INSERT INTO Vital.VitalSign (...) VALUES (..., 3, ..., 72, ...);  -- 72 bpm

-- Temperature (if sick visit)
INSERT INTO Vital.VitalSign (...) VALUES (..., 2, ..., 98.6, ...);  -- 98.6 F

-- Pain (chronic pain patients)
INSERT INTO Vital.VitalSign (...) VALUES (..., 7, ..., 5, ...);  -- Pain 5/10

-- Pulse Ox (if respiratory/sleep apnea)
INSERT INTO Vital.VitalSign (...) VALUES (..., 8, ..., 96, ...);  -- 96%

-- BMI (calculated from height/weight)
INSERT INTO Vital.VitalSign (...) VALUES (..., 10, ..., 26.5, ...);  -- BMI 26.5
```

### 3.4 Drug Dimension (Dim.LocalDrug, Dim.NationalDrug)

**Challenge:** Medications require LocalDrugSID and NationalDrugSID from dimension tables.

**Options:**

**Option A: Reference existing drugs (if available)**
```sql
-- Query to find existing drug SIDs
SELECT LocalDrugSID, LocalDrugName, NationalDrugSID
FROM Dim.LocalDrug
WHERE LocalDrugName LIKE '%SERTRALINE%';
```

**Option B: Insert new drug definitions first**
```sql
-- Insert into Dim.LocalDrug and Dim.NationalDrug BEFORE medications
-- (Include in Thompson Twins scripts, or separate dimension update script)

SET IDENTITY_INSERT Dim.LocalDrug ON;
INSERT INTO Dim.LocalDrug (LocalDrugSID, LocalDrugName, NationalDrugSID, Sta3n, ...)
VALUES
    (9001, 'SERTRALINE 200MG TAB', 4001, 516, ...),
    (9002, 'GABAPENTIN 1200MG TAB', 4002, 516, ...);
SET IDENTITY_INSERT Dim.LocalDrug OFF;

-- Then reference in medications
INSERT INTO RxOut.RxOutpat (RxOutpatSID, LocalDrugSID, DrugNameWithDose, ...)
VALUES
    (8001, 9001, 'SERTRALINE 200MG TAB', ...);
```

**Recommendation:** Use Option B. Create a "Drug Definitions" section at the top of each Thompson Twins script to insert all required drugs first.

### 3.5 TIU Document Definition (Dim.TIUDocumentDefinition)

**Available document types (from existing data):**

| DocumentType | Usage | Example |
|--------------|-------|---------|
| Progress Note | Routine clinic visits | Primary care, specialty follow-ups |
| Consult Note | Specialist consultations | Psychiatry, cardiology, oncology consults |
| Discharge Summary | Inpatient discharge | Post-hospitalization summaries |
| Admission Note | Inpatient admission | Initial admission H&P |
| Procedure Note | Interventions | Injections, catheterizations, surgeries |

**Query to find TIUDocumentDefinitionSID:**
```sql
SELECT TIUDocumentDefinitionSID, DocumentType, DocumentName
FROM Dim.TIUDocumentDefinition
WHERE DocumentType = 'Progress Note';
```

**Recommendation:** Use subqueries or pre-query dimension tables to get SIDs.

### 3.6 Vaccine/CVX Codes (Dim.Vaccine, ImmunizationMill.VaccineCode)

**Common vaccines for Thompson Twins (2010-2026 timeline):**

| Vaccine Name | CVX Code | Series | Notes |
|--------------|----------|--------|-------|
| Influenza | 88 (seasonal), 141 (H1N1) | Annual | 15+ doses each patient |
| COVID-19 | 207 (Moderna), 208 (Pfizer), 212 (Janssen) | Primary + boosters | 6-8 doses each patient |
| Pneumococcal | 33 (PPSV23), 133 (PCV13), 152 (PCV20) | Per guidelines | 2-3 doses each patient |
| Tdap | 115 (Tdap), 09 (Td) | 10-year booster | 2 doses each patient |
| Zoster (Shingles) | 121 (Zostavax live), 187 (Shingrix) | Age 50+ | 2-3 doses each patient |
| Hepatitis A | 83 (Hep A adult), 31 (Hep A pediatric) | 2-dose series | 2 doses each patient |
| Hepatitis B | 43 (Hep B adult), 08 (Hep B pediatric) | 3-dose series | 3 doses each patient |
| RSV | 307 (RSV adult) | Single dose | 1 dose each patient (2025+) |

**Query vaccine dimension:**
```sql
SELECT VaccineSID, CVXCode, VaccineName
FROM Dim.Vaccine
WHERE CVXCode IN (88, 207, 208, 33, 115, 187);
```

**Recommendation:** Create vaccine mapping table at top of script, use subqueries for VaccineSID lookups.

### 3.7 ICD-10 and Problem Codes (Dim.ICD10)

**Thompson Twins key diagnoses:**

**Bailey Thompson:**
- F43.10 (PTSD)
- M54.16 (Chronic lumbar pain)
- S06.9X9S (TBI sequelae)
- H93.13 (Tinnitus bilateral)
- F33.1 (Major depressive disorder, recurrent, moderate)
- I10 (Essential hypertension)
- E78.2 (Hyperlipidemia)
- E11.9 (Type 2 diabetes)
- N18.3 (CKD Stage 3a)
- G47.33 (Obstructive sleep apnea)
- K21.9 (GERD)
- E66.9 (Obesity)

**Alananah Thompson:**
- E11.65 (Type 2 diabetes with hyperglycemia)
- E11.40 (Diabetic peripheral neuropathy)
- E11.329 (Diabetic retinopathy, nonproliferative)
- Z85.3 (Personal history of breast cancer)
- F43.10 (PTSD)
- I10 (Essential hypertension)
- E78.2 (Hyperlipidemia)
- E03.9 (Hypothyroidism)
- M17.0 (Osteoarthritis, bilateral knees)
- H90.3 (Hearing loss, bilateral sensorineural)

**Query ICD-10 dimension:**
```sql
SELECT ICD10SID, ICD10Code, ICD10Description
FROM Dim.ICD10
WHERE ICD10Code IN ('F43.10', 'E11.9', 'N18.3', 'Z85.3');
```

**Recommendation:** If ICD-10 codes don't exist in dimension table, insert them first.

---

## Date Generation Algorithms

### 4.1 Date Strategy Overview

**CDWWork (Bay Pines 2010-2025):** **Fixed dates** (Option A from requirements)
- Retirement date: `'2010-06-15'` (military retirement, both patients)
- All dates are literal strings, NOT relative to `GETDATE()`
- Rationale: Historical data should remain constant for reproducibility

**CDWWork2 (Walla Walla 2025-2026):** **Relative dates** using `DATEADD()` functions
- Move date: `DATEADD(YEAR, -1, GETDATE())` (1 year ago)
- Recent vitals: `DATEADD(MONTH, -2, GETDATE())` (2 months ago)
- Rationale: Keeps current data "fresh" relative to script execution date

### 4.2 CDWWork Date Algorithms (2010-2025)

**Vitals Domain (Quarterly, ~60 readings over 15 years)**

Strategy: Generate vitals every ~3 months (4 per year × 15 years = 60 total)

```sql
-- Pseudocode for Bailey Thompson vitals dates
-- Base date: 2010-06-16 (day after retirement enrollment)
-- Pattern: Add 90 days (quarterly) for each subsequent vital

2010-06-16  -- Initial vital (retirement enrollment)
2010-09-14  -- +90 days
2010-12-13  -- +90 days
2011-03-13  -- +90 days
2011-06-11  -- +90 days
... (continue pattern)
2024-12-05  -- Final Bay Pines vital (before move)
```

**Implementation:**
```sql
-- Manual generation (most straightforward for 60 dates)
INSERT INTO Vital.VitalSign (..., VitalSignTakenDateTime, ...) VALUES
    (..., '2010-06-16', ...),
    (..., '2010-09-14', ...),
    (..., '2010-12-13', ...),
    -- ... continue for all 60 dates
    (..., '2024-12-05', ...);
```

**Alternative (if using helper script):**
```python
# Python helper to generate 60 quarterly dates
from datetime import datetime, timedelta

start = datetime(2010, 6, 16)
dates = []
for i in range(60):
    date = start + timedelta(days=90 * i)
    dates.append(date.strftime('%Y-%m-%d'))
    print(f"'{date.strftime('%Y-%m-%d')}',")
```

**Encounters Domain (Specific dates per requirements)**

Bailey Thompson encounters (32 total):

```sql
-- Major encounters with specific dates (from requirements v2.0)
'2011-02-10'  -- Psychiatry - Initial PTSD evaluation
'2016-09-12'  -- Psychiatry - **SUICIDE ATTEMPT** (critical event)
'2019-01-22'  -- Substance Use - Alcohol detox
'2022-11-10'  -- Medicine - Diabetic ketoacidosis

-- Fill remaining ~28 encounters with dates spread across 2010-2025
-- Strategy: 2-3 encounters per year, clustered around major events
```

**Clinical Notes Domain (~220 notes)**

Strategy: Link notes to encounters + add progress notes

```sql
-- 1. Discharge summary for EACH encounter (32 notes)
-- Use encounter dates + 1-7 days for discharge

-- 2. Progress notes (routine visits, ~12 per year = 180 notes)
-- Use quarterly pattern (aligned with vitals)

-- 3. Consult notes (~40 notes)
-- Use dates between encounters for specialty consultations

-- 4. Emergency department notes (~10 notes)
-- Use dates for ER visits (chest pain, back pain, mental health crises)
```

**Medications Domain (45 total for Bailey)**

```sql
-- Strategy: Issue dates reflect when medication started
-- Active meds (15): Issued 2020-2025 (current)
-- Historical meds (30): Issued 2010-2020, some discontinued

-- Example:
'2010-06-20'  -- Oxycodone (initial chronic pain management)
'2018-12-31'  -- Discontinue date for opioids (taper complete)
'2020-01-15'  -- Sertraline 200mg (current dose)
'2023-06-01'  -- Metformin 1000mg BID (diabetes dx 2019)
```

**Immunizations Domain (42 for Bailey)**

```sql
-- Strategy: Annual influenza + event-based vaccines

-- Annual flu shots (15 total, 2010-2024)
'2010-10-15', '2011-10-15', '2012-10-15', ... '2024-10-15'

-- COVID-19 series (6 doses, 2021-2024)
'2021-01-15'  -- Pfizer dose 1
'2021-02-05'  -- Pfizer dose 2
'2021-09-10'  -- Booster 1
'2022-04-20'  -- Booster 2
'2022-11-01'  -- Bivalent booster
'2023-10-15'  -- 2023 updated booster

-- Pneumococcal (3 doses)
'2013-06-01'  -- PPSV23 (age 50)
'2014-06-01'  -- PCV13
'2018-06-01'  -- PPSV23 booster (5 years later)

-- etc.
```

**Problems Domain (18 problems)**

```sql
-- Strategy: Onset dates match when condition first diagnosed/documented

'2011-02-15'  -- PTSD diagnosis date
'2004-04-12'  -- Chronic back pain (IED blast injury)
'2015-08-10'  -- Hypertension diagnosis
'2019-01-05'  -- Type 2 diabetes diagnosis
'2021-05-12'  -- CKD Stage 3a diagnosis
```

**Laboratory Results Domain (~160 results)**

```sql
-- Strategy: Annual comprehensive metabolic panel + disease-specific monitoring

-- Annual BMP/CMP (15 years = 15 panels, each with ~8 individual results)
'2010-06-17', '2011-06-17', '2012-06-17', ... '2024-06-17'

-- Quarterly A1C (diabetes monitoring, 2019-2025)
'2019-03-15', '2019-06-15', '2019-09-15', ... '2025-12-15'

-- Annual lipid panels (15 years)
'2010-06-17', '2011-06-17', ... '2024-06-17'
```

### 4.3 CDWWork2 Date Algorithms (2025-2026)

**Move Date:** 1 year ago from script execution
```sql
DECLARE @MoveDate DATETIME = DATEADD(YEAR, -1, GETDATE());  -- ~2025-02-08 if run on 2026-02-08
```

**Vitals (4 quarterly readings):**
```sql
-- Most recent vital: 1 month ago
DATEADD(MONTH, -1, GETDATE())

-- Previous vitals: 4, 7, 10 months ago (quarterly pattern)
DATEADD(MONTH, -4, GETDATE())
DATEADD(MONTH, -7, GETDATE())
DATEADD(MONTH, -10, GETDATE())
```

**Encounters (2 admissions):**
```sql
-- Recent admission: 3 months ago
DATEADD(MONTH, -3, GETDATE())

-- Prior admission: 8 months ago
DATEADD(MONTH, -8, GETDATE())
```

**Immunizations (4 recent vaccines):**
```sql
-- Annual flu: 4 months ago (October/November timeframe)
DATEADD(MONTH, -4, GETDATE())

-- COVID booster: 3 months ago
DATEADD(MONTH, -3, GETDATE())

-- RSV vaccine: 3 months ago (same visit as COVID)
DATEADD(MONTH, -3, GETDATE())

-- Pneumococcal PCV20: Scheduled future (use NULL or future date)
DATEADD(MONTH, +1, GETDATE())  -- 1 month from now
```

### 4.4 Date Generation Helper Functions (Optional SQL)

```sql
-- Helper function to generate quarterly dates (if needed)
DECLARE @StartDate DATE = '2010-06-16';
DECLARE @EndDate DATE = '2024-12-31';
DECLARE @QuarterlyDates TABLE (VisitDate DATE);

DECLARE @CurrentDate DATE = @StartDate;
WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO @QuarterlyDates VALUES (@CurrentDate);
    SET @CurrentDate = DATEADD(DAY, 90, @CurrentDate);
END

SELECT * FROM @QuarterlyDates;
-- Use this temporary table in subsequent INSERTs
```

**Recommendation:** For simplicity, hard-code dates in INSERT statements. Use helper scripts only if generating >100 dates.

---

## Implementation Sequence

### 5.1 Dependency Order

**CRITICAL:** Tables must be populated in dependency order to avoid foreign key violations.

**Phase 1: Dimension Tables (Optional - if adding new drugs/locations)**
```
1. Dim.LocalDrug (if new medications)
2. Dim.NationalDrug (if new medications)
3. Dim.ICD10 (if new diagnosis codes)
4. Dim.TIUDocumentDefinition (if new note types)
5. Dim.Vaccine (if new vaccines)
```

**Phase 2: Patient Demographics (No dependencies)**
```
6. SPatient.SPatient (PatientSID 2001, 2002, 2003)
7. SPatient.SPatientAddress (references PatientSID)
8. SPatient.SpatientPhone (references PatientSID)
9. SPatient.SPatientInsurance (references PatientSID)
10. SPatient.SpatientDisability (references PatientSID) - Military service-connected disabilities
```

**Phase 3: Simple Clinical Domains (Patient dependencies only)**
```
11. Vital.VitalSign (references PatientSID, VitalTypeSID, LocationSID)
12. Allergy.PatientAllergy (references PatientSID)
13. Allergy.PatientAllergyReaction (references PatientAllergySID)
14. RxOut.RxOutpat (references PatientSID, LocalDrugSID)
15. RxOut.RxOutpatFill (references RxOutpatSID) - Refill history
16. Immunization.PatientImmunization (references PatientSID, VaccineSID)
17. Outpat.ProblemList (references PatientSID, ICD10SID)
```

**Phase 4: Encounter-Dependent Domains**
```
18. Inpat.Inpatient (references PatientSID, LocationSID)
19. TIU.TIUDocument_8925 (references PatientSID, InpatientSID, TIUDocumentDefinitionSID)
20. TIU.TIUDocumentText (references TIUDocumentSID)
```

**Phase 5: Patient Flags (References Encounters and Problems)**
```
21. SPatient.PatientRecordFlagAssignment (references PatientSID, PatientRecordFlagSID)
22. SPatient.PatientRecordFlagHistory (references PatientRecordFlagAssignmentSID)
```

**Phase 6: Laboratory Results (Patient dependencies only)**
```
23. Chem.LabChem (references PatientSID, LabTestSID, LocationSID)
```

### 5.2 Recommended Script Structure

Each of the 6 Thompson Twins scripts should follow this structure:

```sql
-- =====================================================
-- Thompson-Bailey.sql (CDWWork, Bay Pines 2010-2025)
-- =====================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- =====================================================
-- SECTION 1: DIMENSION TABLE UPDATES (if needed)
-- =====================================================
-- Add any new drugs, ICD-10 codes, or other dimension data

-- =====================================================
-- SECTION 2: DEMOGRAPHICS
-- =====================================================
-- SPatient.SPatient (PatientSID 2001)
-- SPatient.SPatientAddress
-- SPatient.SpatientPhone
-- SPatient.SPatientInsurance
-- SPatient.SpatientDisability

-- =====================================================
-- SECTION 3: VITALS
-- =====================================================
-- Vital.VitalSign (~60 readings)

-- =====================================================
-- SECTION 4: ALLERGIES
-- =====================================================
-- Allergy.PatientAllergy (2 allergies)
-- Allergy.PatientAllergyReaction

-- =====================================================
-- SECTION 5: MEDICATIONS
-- =====================================================
-- RxOut.RxOutpat (45 prescriptions)
-- RxOut.RxOutpatFill (refill records)

-- =====================================================
-- SECTION 6: ENCOUNTERS
-- =====================================================
-- Inpat.Inpatient (32 encounters)

-- =====================================================
-- SECTION 7: CLINICAL NOTES
-- =====================================================
-- TIU.TIUDocument_8925 (220 notes)
-- TIU.TIUDocumentText (220 note texts)

-- =====================================================
-- SECTION 8: IMMUNIZATIONS
-- =====================================================
-- Immunization.PatientImmunization (42 vaccines)

-- =====================================================
-- SECTION 9: PROBLEMS/DIAGNOSES
-- =====================================================
-- Outpat.ProblemList (18 problems)

-- =====================================================
-- SECTION 10: LABORATORY RESULTS
-- =====================================================
-- Chem.LabChem (~160 results)

-- =====================================================
-- SECTION 11: PATIENT FLAGS
-- =====================================================
-- SPatient.PatientRecordFlagAssignment (2 flags)
-- SPatient.PatientRecordFlagHistory (review history)

PRINT 'Bailey Thompson (CDWWork): All data inserted successfully';
GO
```

### 5.3 Execution Order (Master Plan)

```
1. Execute: mock/sql-server/cdwwork/insert/Thompson-Bailey.sql
2. Execute: mock/sql-server/cdwwork/insert/Thompson-Alananah.sql
3. Execute: mock/sql-server/cdwwork/insert/Thompson-Joe.sql
4. Verify: Query CDWWork to confirm data (PatientSID 2001, 2002, 2003)
5. Execute: mock/sql-server/cdwwork2/insert/Thompson-Bailey.sql
6. Execute: mock/sql-server/cdwwork2/insert/Thompson-Alananah.sql
7. Execute: mock/sql-server/cdwwork2/insert/Thompson-Joe.sql
8. Verify: Query CDWWork2 to confirm data (PersonSID 20001, 20002, 20003)
9. Test: Run ETL Bronze → Silver → Gold → PostgreSQL
10. Test: View patients in med-z1 UI (ICN200001, ICN200002, ICN200003)
```

---

## Script Templates

### 6.1 Header Template

```sql
-- =====================================================
-- Thompson Twins Test Patient Data
-- Patient: Bailey James Thompson (Male)
-- ICN: ICN200001
-- Database: CDWWork (Bay Pines VA, 2010-2025)
-- =====================================================
-- Purpose: Comprehensive test patient for med-z1
--          Male veteran with PTSD, chronic pain, TBI
--          Service history: Gulf War, Iraq (IED injury)
--          100% service-connected disability
-- =====================================================
-- Domain Coverage:
--   1. Demographics (SPatient.SPatient, Address, Phone, Insurance, Disability)
--   2. Vitals (~60 readings, quarterly 2010-2025)
--   3. Patient Flags (High Risk Suicide, Opioid Risk-inactive)
--   4. Allergies (Penicillin, Morphine)
--   5. Medications (45 total: 15 active, 30 historical)
--   6. Encounters (32 inpatient admissions)
--   7. Clinical Notes (220 notes: progress, consults, discharge)
--   8. Immunizations (42 vaccines)
--   9. Problems (18: 15 active, 3 resolved, Charlson=5)
--  10. Labs (160 results: BMP, A1C, lipids, CBC, LFTs)
-- =====================================================
-- Last Updated: 2026-02-08
-- Author: med-z1 development team
-- Related: docs/spec/thompson-twins-patient-reqs.md (v3.0)
-- =====================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO
```

### 6.2 Section Template (with Documentation)

```sql
-- =====================================================
-- SECTION 2: DEMOGRAPHICS - SPatient.SPatient
-- =====================================================
-- Bailey Thompson: Male veteran, age 62 (DOB 1963-04-15)
-- Served 1990-2010 (Gulf War, Iraq), retired to St. Petersburg, FL
-- PatientSID 2001 for CDWWork (Bay Pines, Sta3n 516)
-- ICN200001 (national identifier for cross-database identity resolution)
-- =====================================================
-- FIELD RATIONALE:
--   PatientSID = 2001           -- Explicit SID (manual assignment)
--   PatientIEN = 'PtIEN2001'    -- VistA internal entry number (mock)
--   Sta3n = 516                  -- Bay Pines VA Healthcare System
--   PatientICN = 'ICN200001'     -- Integration Control Number (national ID)
--   BirthDateTime = '1963-04-15' -- Age 62 as of 2026
--   Gender = 'M'                 -- Male
--   VeteranFlag = 'Y'            -- Veteran
--   ServiceConnectedFlag = 'Y'   -- 100% service-connected disability
--   PeriodOfService = 'PERSIAN GULF' -- Gulf War + OIF veteran
-- =====================================================

INSERT INTO SPatient.SPatient (
    PatientSID,
    PatientIEN,
    Sta3n,
    PatientName,
    PatientLastName,
    PatientFirstName,
    TestPatientFlag,
    CDWPossibleTestPatientFlag,
    VeteranFlag,
    PatientType,
    PatientTypeSID,
    PatientICN,
    ScrSSN,
    PatientSSN,
    SSNVerificationStatus,
    Age,
    BirthDateTime,
    DeceasedFlag,
    Gender,
    SelfIdentifiedGender,
    Religion,
    ReligionSID,
    MaritalStatus,
    MaritalStatusSID,
    ServiceConnectedFlag,
    PeriodOfService,
    PeriodOfServiceSID,
    PatientEnteredDateTime
)
VALUES (
    2001,                           -- PatientSID: Unique ID for CDWWork
    'PtIEN2001',                    -- PatientIEN: VistA internal entry number
    516,                            -- Sta3n: Bay Pines VA (St. Petersburg, FL)
    'THOMPSON,BAILEY JAMES',        -- PatientName: Last,First Middle format
    'Thompson',                     -- PatientLastName
    'Bailey',                       -- PatientFirstName
    'N',                            -- TestPatientFlag: Not a test patient (mock value)
    'N',                            -- CDWPossibleTestPatientFlag
    'Y',                            -- VeteranFlag: Yes, veteran
    'Regular',                      -- PatientType
    101,                            -- PatientTypeSID: Regular veteran
    'ICN200001',                    -- PatientICN: National identifier
    '200-00-1001',                  -- ScrSSN: Scrambled SSN (display)
    '200-00-1001',                  -- PatientSSN: Mock SSN (non-real)
    'Verified',                     -- SSNVerificationStatus
    62,                             -- Age: As of 2026
    '1963-04-15',                   -- BirthDateTime: April 15, 1963
    'N',                            -- DeceasedFlag: Alive
    'M',                            -- Gender: Male
    'Male',                         -- SelfIdentifiedGender
    'Protestant',                   -- Religion
    2,                              -- ReligionSID
    'DIVORCED',                     -- MaritalStatus: Divorced 2018
    2,                              -- MaritalStatusSID
    'Y',                            -- ServiceConnectedFlag: Yes, 100% SC
    'PERSIAN GULF',                 -- PeriodOfService: Gulf War + OIF
    12008,                          -- PeriodOfServiceSID
    '2010-06-15'                    -- PatientEnteredDateTime: VA enrollment date
);
GO

PRINT 'Bailey Thompson: Demographics inserted (PatientSID 2001)';
GO
```

### 6.3 Vitals Section Template (with Date Pattern)

```sql
-- =====================================================
-- SECTION 3: VITALS - Vital.VitalSign
-- =====================================================
-- Bailey Thompson: ~60 vital sign readings (2010-2025)
-- Pattern: Quarterly visits (every ~90 days)
-- Weight trend: 185 lbs (2010) → 245 lbs (2019, alcohol/sedentary peak)
--              → 220 lbs (2025, post-sobriety/diabetes management)
-- BP trend: Normal (2010) → Pre-HTN (2014) → Controlled on meds (2015+)
-- Pain scores: Chronic 5-8/10 (lumbar radiculopathy)
-- =====================================================
-- DATE STRATEGY:
--   Base: 2010-06-16 (day after enrollment)
--   Pattern: Add ~90 days (quarterly) for each visit
--   Rationale: Aligns with typical chronic disease follow-up schedule
-- =====================================================

-- Visit 1: 2010-06-16 (Initial enrollment vital)
INSERT INTO Vital.VitalSign (
    PatientSID, VitalTypeSID, VitalSignTakenDateTime,
    NumericValue, Systolic, Diastolic, ResultValue,
    LocationSID, Sta3n
)
VALUES
    -- Height (constant for adults)
    (2001, 5, '2010-06-16 09:00:00', 70.0, NULL, NULL, '70',
        (SELECT LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationName='Primary Care Clinic A' AND LocationType='Outpatient'),
        516),

    -- Weight
    (2001, 6, '2010-06-16 09:05:00', 185.0, NULL, NULL, '185',
        (SELECT LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationName='Primary Care Clinic A' AND LocationType='Outpatient'),
        516),

    -- Blood Pressure
    (2001, 1, '2010-06-16 09:10:00', NULL, 125, 78, '125/78',
        (SELECT LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationName='Primary Care Clinic A' AND LocationType='Outpatient'),
        516),

    -- Pulse
    (2001, 3, '2010-06-16 09:10:00', 72, NULL, NULL, '72',
        (SELECT LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationName='Primary Care Clinic A' AND LocationType='Outpatient'),
        516),

    -- Pain
    (2001, 7, '2010-06-16 09:15:00', 6, NULL, NULL, '6',
        (SELECT LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationName='Primary Care Clinic A' AND LocationType='Outpatient'),
        516),

    -- BMI (calculated from height/weight)
    (2001, 10, '2010-06-16 09:15:00', 26.5, NULL, NULL, '26.5',
        (SELECT LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationName='Primary Care Clinic A' AND LocationType='Outpatient'),
        516);
GO

-- Visit 2: 2010-09-14 (+90 days)
INSERT INTO Vital.VitalSign (...) VALUES (...);
-- ... (Continue for all 60 quarterly visits)
GO

PRINT 'Bailey Thompson: Vitals inserted (~60 readings, quarterly 2010-2025)';
GO
```

### 6.4 Medications Section Template

```sql
-- =====================================================
-- SECTION 5: MEDICATIONS - RxOut.RxOutpat
-- =====================================================
-- Bailey Thompson: 45 medications total
--   - Active (15): Current chronic disease management (2020-2025)
--   - Historical (30): Discontinued/replaced medications (2010-2020)
-- =====================================================
-- MEDICATION TIMELINE:
--   2010-2018: Chronic opioid therapy (oxycodone, morphine ER)
--   2018-2019: Opioid taper (transition to non-opioid pain management)
--   2019+: Non-opioid regimen (gabapentin, duloxetine, lidocaine)
--   2020+: Current stable medication list (15 active meds)
-- =====================================================
-- DRUG DIMENSION STRATEGY:
--   Option: Reference existing Dim.LocalDrug entries
--   If drug doesn't exist, insert into Dim.LocalDrug first
-- =====================================================

-- Active Medications (15 total)

-- 1. Sertraline 200mg (PTSD/Depression) - Active since 2020
INSERT INTO RxOut.RxOutpat (
    RxOutpatSID,
    RxOutpatIEN,
    Sta3n,
    PatientSID,
    PatientIEN,
    LocalDrugSID,
    NationalDrugSID,
    DrugNameWithoutDose,
    DrugNameWithDose,
    PrescriptionNumber,
    IssueDateTime,
    RxStatus,
    RxType,
    Quantity,
    DaysSupply,
    RefillsAllowed,
    RefillsRemaining,
    MaxRefills
)
VALUES (
    8001,                               -- RxOutpatSID (manual assignment, 8000 series)
    'RxIEN8001',                        -- RxOutpatIEN
    516,                                -- Sta3n: Bay Pines
    2001,                               -- PatientSID
    'PtIEN2001',                        -- PatientIEN
    (SELECT LocalDrugSID FROM Dim.LocalDrug WHERE LocalDrugName LIKE '%SERTRALINE 200MG%' AND Sta3n=516), -- Lookup drug
    4001,                               -- NationalDrugSID (mock)
    'SERTRALINE',                       -- DrugNameWithoutDose
    'SERTRALINE 200MG TAB',             -- DrugNameWithDose
    'RX2001-001',                       -- PrescriptionNumber
    '2020-01-15',                       -- IssueDateTime (when prescribed)
    'ACTIVE',                           -- RxStatus
    'REFILL',                           -- RxType
    90.0,                               -- Quantity: 90 tablets
    90,                                 -- DaysSupply: 90 days (3-month supply)
    11,                                 -- RefillsAllowed: 11 refills
    8,                                  -- RefillsRemaining
    11                                  -- MaxRefills
);
GO

-- 2. Gabapentin 1200mg TID (Neuropathic Pain) - Active since 2019
INSERT INTO RxOut.RxOutpat (...) VALUES (...);
GO

-- ... (Continue for all 15 active medications)

-- Historical Medications (30 total - discontinued)

-- 31. Oxycodone 30mg Q6H (Chronic Pain) - Discontinued 2018
INSERT INTO RxOut.RxOutpat (
    RxOutpatSID,
    ...,
    IssueDateTime,
    RxStatus,
    DiscontinuedDateTime,
    DiscontinueReason
)
VALUES (
    8031,
    ...,
    '2010-07-01',
    'DISCONTINUED',
    '2018-12-31',
    'Opioid taper completed, transitioned to non-opioid pain management'
);
GO

-- ... (Continue for all 30 historical medications)

PRINT 'Bailey Thompson: Medications inserted (45 total: 15 active, 30 historical)';
GO
```

### 6.5 Clinical Notes Template (with SOAP Format)

```sql
-- =====================================================
-- SECTION 7: CLINICAL NOTES - TIU.TIUDocument_8925 + TIUDocumentText
-- =====================================================
-- Bailey Thompson: 220 clinical notes total
--   - Progress Notes (~100): Primary care, psychiatry, pain management
--   - Consult Notes (~40): Specialty consultations
--   - Discharge Summaries (~30): Inpatient discharge summaries
--   - Procedure Notes (~15): Injections, procedures
--   - Emergency Notes (~10): ER visits
--   - Other (~25): Miscellaneous
-- =====================================================
-- NOTE LINKAGE:
--   - Discharge summaries linked to Inpat.Inpatient.InpatientSID
--   - Progress notes linked to outpatient visits (no InpatientSID)
-- =====================================================

-- Note 1: Psychiatry Progress Note (2016-09-20, post-suicide attempt)
-- This is a CRITICAL note documenting suicide attempt and high-risk flag activation

INSERT INTO TIU.TIUDocument_8925 (
    -- TIUDocumentSID is IDENTITY, omit from column list
    PatientSID,
    InpatientSID,                       -- Link to psychiatric admission
    TIUDocumentDefinitionSID,
    DocumentDateTime,
    AuthorStaffSID,
    CosignerStaffSID,
    DocumentStatus,
    DocumentTitle,
    Sta3n
)
VALUES (
    2001,                               -- PatientSID
    (SELECT InpatientSID FROM Inpat.Inpatient WHERE PatientSID=2001 AND AdmitDateTime='2016-09-12'),  -- Link to suicide attempt admission
    (SELECT TIUDocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentType='Progress Note'),
    '2016-09-20 14:30:00',             -- Document date
    2001,                               -- AuthorStaffSID (mock provider)
    2002,                               -- CosignerStaffSID (attending psychiatrist)
    'COMPLETED',                        -- DocumentStatus
    'PSYCHIATRY PROGRESS NOTE',         -- DocumentTitle
    516                                 -- Sta3n: Bay Pines
);
GO

-- Capture the TIUDocumentSID that was just auto-generated
DECLARE @TIUDoc1SID BIGINT = SCOPE_IDENTITY();

-- Insert note text (SOAP format)
INSERT INTO TIU.TIUDocumentText (
    TIUDocumentSID,
    NoteText,
    Sta3n
)
VALUES (
    @TIUDoc1SID,
    'PSYCHIATRY PROGRESS NOTE
Date: 2016-09-20
Patient: Bailey James Thompson (ICN200001)
Author: Dr. Sarah Mitchell, MD (Psychiatry)

SUBJECTIVE:
Patient is a 53M veteran with combat-related PTSD, chronic pain, and major depressive disorder. Admitted 9/12 after suicide attempt via intentional opioid overdose (oxycodone 30mg x 20 tablets). Reports feeling overwhelmed by chronic pain, financial stress, and divorce proceedings. States "I just wanted the pain to stop." Admits to passive suicidal ideation over past 3 months but denies specific plan prior to 9/12. Reports regret about overdose, states "I scared my kids."

OBJECTIVE:
Mental Status Exam:
- Appearance: Disheveled, fair hygiene
- Mood: Dysphoric, tearful at times
- Affect: Congruent, flat at baseline
- Speech: Normal rate, low volume
- Thought Process: Logical, goal-directed
- Thought Content: Denies current SI/HI, no psychosis
- Insight: Fair, acknowledges depression and need for treatment
- Judgment: Improving, engaged in safety planning

Assessment Scales:
- PHQ-9: 24 (severe depression)
- PCL-5: 62 (severe PTSD symptoms)
- Pain VAS: 7/10 (chronic lumbar pain)

ASSESSMENT:
1. Suicide attempt (T50.905A - Poisoning by opioids, intentional self-harm)
2. Major depressive disorder, recurrent, severe (F33.2)
3. Post-traumatic stress disorder, chronic (F43.10)
4. Opioid use disorder, in remission (F11.21) - Patient taking meds as prescribed, overdose was acute crisis
5. Chronic pain syndrome (M54.16)

HIGH RISK FOR REPEAT SUICIDE ATTEMPT. Multiple risk factors: recent attempt, severe MDD, PTSD, chronic pain, psychosocial stressors (divorce, financial strain), social isolation.

PLAN:
1. **Medication Management:**
   - Continue sertraline 200mg daily (therapeutic dose)
   - ADD prazosin 5mg nightly for PTSD nightmares (start tonight)
   - Pain management consult for opioid taper (high suicide risk with current opioid access)

2. **Safety Planning:**
   - Safety plan reviewed and updated with patient
   - Means restriction: Sister Alananah will secure all firearms from patient''s home
   - Opioid prescription will be limited to 7-day supply with weekly visits
   - Emergency contact card provided (Crisis Line 988, VA Suicide Prevention Hotline)

3. **Follow-Up:**
   - Weekly therapy with Dr. Rodriguez (cognitive processing therapy for PTSD)
   - Psychiatry follow-up in 1 week (9/27)
   - Pain management consult scheduled for 9/22

4. **Flags:**
   - **HIGH RISK FOR SUICIDE FLAG ACTIVATED** (Cat I National)
   - Opioid Risk flag to be reviewed (consider taper to reduce access)

5. **Disposition:**
   - Continue inpatient psychiatric care for 2-3 more days
   - Transition to Intensive Outpatient Program (IOP) upon discharge
   - Family meeting scheduled for 9/21 (sister Alananah)

Discussed case with Dr. Chen (Attending Psychiatrist). Patient is stabilizing but remains high-risk. Close follow-up essential.

Electronically signed: Dr. Sarah Mitchell, MD (Psychiatry)
Co-signed: Dr. Robert Chen, MD (Attending Psychiatrist)',
    516
);
GO

PRINT 'Bailey Thompson: Clinical note 1 inserted (Psychiatry Progress Note, suicide attempt)';
GO

-- Note 2: Primary Care Progress Note (2022-12-15, diabetes diagnosis)
-- ... (Continue for all 220 notes)

PRINT 'Bailey Thompson: Clinical Notes inserted (220 total)';
GO
```

### 6.6 Error Handling Template (Optional)

```sql
-- =====================================================
-- ERROR HANDLING: Check for existing data before inserting
-- =====================================================
-- Use this pattern if scripts may be run multiple times

IF NOT EXISTS (SELECT 1 FROM SPatient.SPatient WHERE PatientSID = 2001)
BEGIN
    INSERT INTO SPatient.SPatient (...) VALUES (...);
    PRINT 'Bailey Thompson: Demographics inserted';
END
ELSE
BEGIN
    PRINT 'Bailey Thompson: Demographics already exist (skipped)';
END
GO
```

---

## Validation Procedures

### 7.1 Post-Insert Verification Queries

After running each script, execute these verification queries:

**1. Patient Record Exists:**
```sql
-- Verify patient demographics
SELECT PatientSID, PatientICN, PatientName, BirthDateTime, Gender, Sta3n
FROM SPatient.SPatient
WHERE PatientSID IN (2001, 2002, 2003);
-- Expected: 3 rows (Bailey, Alananah, Joe)
```

**2. Domain Record Counts:**
```sql
-- Verify data volume per domain
SELECT
    'Vitals' AS Domain,
    COUNT(*) AS RecordCount
FROM Vital.VitalSign
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Medications',
    COUNT(*)
FROM RxOut.RxOutpat
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Encounters',
    COUNT(*)
FROM Inpat.Inpatient
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Clinical Notes',
    COUNT(*)
FROM TIU.TIUDocument_8925
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Immunizations',
    COUNT(*)
FROM Immunization.PatientImmunization
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Problems',
    COUNT(*)
FROM Outpat.ProblemList
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Labs',
    COUNT(*)
FROM Chem.LabChem
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Allergies',
    COUNT(*)
FROM Allergy.PatientAllergy
WHERE PatientSID IN (2001, 2002, 2003)

UNION ALL

SELECT
    'Patient Flags',
    COUNT(*)
FROM SPatient.PatientRecordFlagAssignment
WHERE PatientSID IN (2001, 2002, 2003);

-- Expected results (Bailey + Alananah + Joe combined):
-- Vitals: 184 (64+64+56)
-- Medications: 93 (45+40+8)
-- Encounters: 63 (32+28+3)
-- Clinical Notes: 460 (220+180+60)
-- Immunizations: 122 (42+40+40)
-- Problems: 36 (18+16+2)
-- Labs: 360 (160+140+60)
-- Allergies: 4 (2+2+0 NKDA)
-- Patient Flags: 4 (2+2+0)
```

**3. Foreign Key Integrity:**
```sql
-- Check for orphaned records (LocationSID references)
SELECT
    v.VitalSignSID,
    v.LocationSID,
    l.LocationName
FROM Vital.VitalSign v
LEFT JOIN Dim.Location l ON v.LocationSID = l.LocationSID
WHERE v.PatientSID IN (2001, 2002, 2003)
  AND l.LocationSID IS NULL;
-- Expected: 0 rows (no orphaned LocationSIDs)

-- Check for orphaned InpatientSID references in clinical notes
SELECT
    t.TIUDocumentSID,
    t.InpatientSID,
    i.InpatientSID AS VerifiedInpatientSID
FROM TIU.TIUDocument_8925 t
LEFT JOIN Inpat.Inpatient i ON t.InpatientSID = i.InpatientSID
WHERE t.PatientSID IN (2001, 2002, 2003)
  AND t.InpatientSID IS NOT NULL
  AND i.InpatientSID IS NULL;
-- Expected: 0 rows (all InpatientSIDs valid)
```

**4. Date Range Validation:**
```sql
-- Verify vitals dates are within expected range (2010-2025 for CDWWork)
SELECT
    MIN(VitalSignTakenDateTime) AS EarliestVital,
    MAX(VitalSignTakenDateTime) AS LatestVital
FROM Vital.VitalSign
WHERE PatientSID IN (2001, 2002, 2003);
-- Expected: Min ~2010-06-16 (Bailey/Alananah) or ~2012-06-16 (Joe), Max ~2024-12-xx

-- Verify encounters dates
SELECT
    MIN(AdmitDateTime) AS EarliestAdmit,
    MAX(DischargeDateTime) AS LatestDischarge
FROM Inpat.Inpatient
WHERE PatientSID IN (2001, 2002, 2003);
-- Expected: Min ~2011-02-10, Max ~2025-xx-xx
```

**5. Specific Clinical Validations:**
```sql
-- Verify Bailey Thompson has High Risk Suicide flag
SELECT
    p.PatientName,
    f.FlagName,
    a.ActiveFlag,
    a.AssignmentDateTime
FROM SPatient.PatientRecordFlagAssignment a
JOIN SPatient.SPatient p ON a.PatientSID = p.PatientSID
JOIN Dim.PatientRecordFlag f ON a.PatientRecordFlagSID = f.PatientRecordFlagSID
WHERE p.PatientSID = 2001
  AND f.FlagName LIKE '%SUICIDE%';
-- Expected: 1 row (High Risk for Suicide flag, active)

-- Verify Alananah Thompson has Breast Cancer Survivor flag
SELECT
    p.PatientName,
    f.FlagName,
    a.ActiveFlag
FROM SPatient.PatientRecordFlagAssignment a
JOIN SPatient.SPatient p ON a.PatientSID = p.PatientSID
JOIN Dim.PatientRecordFlag f ON a.PatientRecordFlagSID = f.PatientRecordFlagSID
WHERE p.PatientSID = 2002
  AND f.FlagName LIKE '%CANCER%';
-- Expected: 1 row (Cancer Survivor flag, active)
```

### 7.2 CDWWork2 Validation Queries

```sql
-- Verify CDWWork2 patient records
USE CDWWork2;
GO

SELECT PersonSID, PatientICN, LastName, FirstName, BirthDate, Gender
FROM VeteranMill.SPerson
WHERE PersonSID IN (20001, 20002, 20003);
-- Expected: 3 rows

-- Verify vitals count (should be ~4 for Bailey/Alananah, ~1 for Joe = ~9 total)
SELECT COUNT(*) AS VitalsCount
FROM VitalMill.VitalResult
WHERE PersonSID IN (20001, 20002, 20003);
-- Expected: ~9 rows
```

### 7.3 ETL Pipeline Validation

After loading data into PostgreSQL:

```sql
-- PostgreSQL queries to verify Thompson Twins in serving database

-- Verify patient demographics
SELECT patient_key, icn, patient_name, date_of_birth, gender
FROM patient_demographics
WHERE icn IN ('ICN200001', 'ICN200002', 'ICN200003');

-- Verify vitals
SELECT patient_key, COUNT(*) AS vitals_count
FROM patient_vitals
WHERE patient_key IN (
    SELECT patient_key FROM patient_demographics WHERE icn IN ('ICN200001', 'ICN200002', 'ICN200003')
)
GROUP BY patient_key;
-- Expected: ~64 for Bailey, ~64 for Alananah, ~56 for Joe
```

---

## Implementation Checklist

Use this checklist to track progress:

### Phase 1: Preparation
- [ ] Review requirements document (v3.0)
- [ ] Review this implementation plan
- [ ] Set up SQL Server development environment
- [ ] Verify access to CDWWork and CDWWork2 databases

### Phase 2: CDWWork - Bailey Thompson
- [ ] Create `mock/sql-server/cdwwork/insert/Thompson-Bailey.sql`
- [ ] Implement demographics section (PatientSID 2001)
- [ ] Implement vitals section (~60 readings)
- [ ] Implement allergies section (2 allergies)
- [ ] Implement medications section (45 meds, RxOutpatSID 8001-8045)
- [ ] Implement encounters section (32 admissions)
- [ ] Implement clinical notes section (220 notes)
- [ ] Implement immunizations section (42 vaccines)
- [ ] Implement problems section (18 problems, Charlson=5)
- [ ] Implement labs section (~160 results)
- [ ] Implement patient flags section (2 flags)
- [ ] Test script execution in clean SQL Server
- [ ] Run validation queries

### Phase 3: CDWWork - Alananah Thompson
- [ ] Create `mock/sql-server/cdwwork/insert/Thompson-Alananah.sql`
- [ ] Implement demographics section (PatientSID 2002)
- [ ] Implement vitals section (~60 readings)
- [ ] Implement allergies section (2 allergies)
- [ ] Implement medications section (40 meds, RxOutpatSID 8046-8085)
- [ ] Implement encounters section (28 admissions)
- [ ] Implement clinical notes section (180 notes)
- [ ] Implement immunizations section (40 vaccines)
- [ ] Implement problems section (16 problems, Charlson=4)
- [ ] Implement labs section (~140 results)
- [ ] Implement patient flags section (2 flags)
- [ ] Test script execution
- [ ] Run validation queries

### Phase 3.5: CDWWork - Joe Thompson
- [ ] Create `mock/sql-server/cdwwork/insert/Thompson-Joe.sql`
- [ ] Implement demographics section (PatientSID 2003)
- [ ] Implement vitals section (~55 readings, stable trends)
- [ ] Implement allergies section (NKDA - No Known Drug Allergies)
- [ ] Implement medications section (8 meds, RxOutpatSID 8086-8093)
- [ ] Implement encounters section (3 admissions, mostly outpatient)
- [ ] Implement clinical notes section (60 notes, preventive care focus)
- [ ] Implement immunizations section (40 vaccines)
- [ ] Implement problems section (2 problems, Charlson=0)
- [ ] Implement labs section (~60 results, all normal/near-normal)
- [ ] Implement patient flags section (0 flags - healthy patient)
- [ ] Test script execution
- [ ] Run validation queries

### Phase 4: CDWWork2 - Bailey Thompson
- [ ] Create `mock/sql-server/cdwwork2/insert/Thompson-Bailey.sql`
- [ ] Implement demographics section (PersonSID 20001, relative dates)
- [ ] Implement vitals section (~4 readings, DATEADD functions)
- [ ] Implement encounters section (~2 admissions)
- [ ] Implement problems section (active problems only)
- [ ] Implement immunizations section (~4 recent vaccines)
- [ ] Test script execution
- [ ] Run validation queries

### Phase 5: CDWWork2 - Alananah Thompson
- [ ] Create `mock/sql-server/cdwwork2/insert/Thompson-Alananah.sql`
- [ ] Implement demographics section (PersonSID 20002)
- [ ] Implement vitals section (~4 readings)
- [ ] Implement encounters section (~2 admissions)
- [ ] Implement problems section (active problems only)
- [ ] Implement immunizations section (~4 recent vaccines)
- [ ] Test script execution
- [ ] Run validation queries

### Phase 5.5: CDWWork2 - Joe Thompson
- [ ] Create `mock/sql-server/cdwwork2/insert/Thompson-Joe.sql`
- [ ] Implement demographics section (PersonSID 20003)
- [ ] Implement vitals section (~1 reading, relative dates)
- [ ] Implement encounters section (~2 admissions: colonoscopy, wellness visit)
- [ ] Implement problems section (2 active problems only)
- [ ] Implement immunizations section (~4 recent vaccines)
- [ ] Test script execution
- [ ] Run validation queries

### Phase 6: Integration & Testing
- [ ] Update `mock/sql-server/cdwwork/insert/_master.sql` with Thompson Twins scripts
- [ ] Update `mock/sql-server/cdwwork2/insert/_master.sql` with Thompson Twins scripts
- [ ] Test full database rebuild (run both master scripts)
- [ ] Run ETL Bronze extraction (CDWWork → Parquet)
- [ ] Run ETL Bronze extraction (CDWWork2 → Parquet)
- [ ] Run ETL Silver transformation (identity resolution ICN200001/ICN200002/ICN200003)
- [ ] Run ETL Gold curation
- [ ] Run ETL Load (Parquet → PostgreSQL)
- [ ] Verify Thompson Twins in PostgreSQL serving database
- [ ] Test UI display (http://127.0.0.1:8000/)
  - [ ] Bailey Thompson dashboard (all 10 domains, Charlson=5)
  - [ ] Alananah Thompson dashboard (all 10 domains, Charlson=4)
  - [ ] Joe Thompson dashboard (all 10 domains, Charlson=0, healthy control)
  - [ ] Patient flags modal (Bailey: High Risk; Alananah: Cancer Survivor; Joe: 0 flags)
  - [ ] Vitals charts (Bailey: weight trends, Alananah: weight trends, Joe: stable)
  - [ ] Medications page (active/historical split)
  - [ ] Encounters pagination
  - [ ] Clinical notes filtering
  - [ ] Problems page (Charlson badge)
  - [ ] AI Insight tool queries (test all 3 patients)

### Phase 7: Documentation
- [ ] Mark implementation plan as "Complete"
- [ ] Update requirements document with "Implementation Complete" status
- [ ] Document any deviations from plan
- [ ] Create implementation summary (lessons learned)
- [ ] Update CLAUDE.md with Thompson Twins test patient references

---

## End of Implementation Plan

**Next Steps:**
1. Review this plan with stakeholders
2. Begin Phase 2 (CDWWork - Bailey Thompson script development)
3. Iterate and refine as needed

**Questions/Issues:**
- Contact: Development team
- Related: `docs/spec/thompson-twins-patient-reqs.md` (v3.0)
