# Thompson Siblings - Integration and Silver Layer Harmonization Notes

**Document Version:** v1.0
**Date:** 2026-02-08
**Status:** ✅ Complete - Ready for ETL Integration

---

## Executive Summary

This document provides technical guidance for integrating the Thompson siblings test patients into the med-z1 Silver layer ETL pipeline. The Thompson siblings - Bailey and Alananah (twins, born April 15, 1963), and their younger brother Joe (born May 10, 1970) - are comprehensive test patients designed to demonstrate:

1. **Cross-system data harmonization** (VistA CDWWork + Cerner CDWWork2)
2. **Longitudinal patient history** (15 years at Bay Pines FL + 1 year at Walla Walla WA)
3. **Clinical complexity spectrum** (Charlson Index: 5, 2, 0)
4. **Identity resolution** (same ICN across both systems)

---

## 1. Patient Identity and Key Allocation

### 1.1 Cross-System Identity Resolution

| Patient | CDWWork (VistA) | CDWWork2 (Cerner) | Birth Date | Age | Notes |
|---------|-----------------|-------------------|------------|-----|-------|
| Bailey James Thompson | PatientSID: 2001 | PatientKey: PK200001 | 1963-04-15 | 62 | Twin of Alananah |
| Alananah Marie Thompson | PatientSID: 2002 | PatientKey: PK200002 | 1963-04-15 | 62 | Twin of Bailey |
| Joe Michael Thompson | PatientSID: 2003 | PatientKey: PK200003 | 1970-05-10 | 55 | Younger brother |

**Common Identifier:** All three patients share the same `PatientICN` across both systems:
- Bailey: **ICN200001**
- Alananah: **ICN200002**
- Joe: **ICN200003**

### 1.2 Manually Allocated SID Ranges (CDWWork Only)

The following SID ranges were manually allocated to avoid conflicts with IDENTITY auto-increment sequences:

| SID Type | Bailey (2001) | Alananah (2002) | Joe (2003) |
|----------|---------------|-----------------|------------|
| PatientSID | 2001 | 2002 | 2003 |
| RxOutpatSID | 8001-8045 (45 meds) | 8046-8085 (40 meds) | 8086-8093 (8 meds) |

**All other SIDs use IDENTITY auto-increment** and do not require manual tracking.

---

## 2. Data Coverage and Timeframes

### 2.1 CDWWork (VistA) - Bay Pines VA (Sta3n 516, Florida)

**Timeframe:** 2010-01-01 to 2025-02-01 (15 years)
**Clinical Domains:** 10 domains fully populated

| Domain | Bailey | Alananah | Joe |
|--------|--------|----------|-----|
| Demographics | Complete | Complete | Complete |
| Addresses | 2 (FL + WA, effective 2025-02-01) | 2 (FL + WA, effective 2025-02-01) | 2 (FL + WA, effective 2025-02-01) |
| Phone Numbers | 4 (2 FL + 2 WA) | 4 (2 FL + 2 WA) | 4 (2 FL + 2 WA) |
| Vitals | 32 records (quarterly) | 27 records (quarterly) | 8 records (annual) |
| Patient Flags | 2 flags (Suicide Risk + Opioid Risk) | 2 flags (Suicide Risk + MST) | None |
| Allergies | 2 (Penicillin + Morphine) | 2 (Penicillin + Sulfa) | 1 (Penicillin) |
| Medications | 45 (8001-8045) | 40 (8046-8085) | 8 (8086-8093) |
| Encounters | 32 inpatient admissions | 18 inpatient admissions | 4 inpatient admissions |
| Clinical Notes | 48 notes (Progress, Discharge, Psych) | 24 notes (Progress, Discharge) | 6 notes (Progress) |
| Immunizations | 18 vaccines | 12 vaccines | 8 vaccines |
| Problems | 8 active problems | 6 active problems | 6 active problems |
| Lab Results | 15 results (quarterly) | 10 results (quarterly) | 3 results (annual) |

### 2.2 CDWWork2 (Cerner) - Walla Walla VAMC (FacilityCode 687, Washington)

**Timeframe:** 2025-02-01 to 2026-02-01 (1 year, continuation care)
**Clinical Domains:** 5 simplified domains

| Domain | Bailey | Alananah | Joe |
|--------|--------|----------|-----|
| Demographics | Complete | Complete | Complete |
| Vitals | 6 quarterly readings | 6 quarterly readings | 6 quarterly readings |
| Medications | 5 active | 5 active | 4 active |
| Problems | 5 active | 5 active | 4 active |
| Lab Results | 4 quarterly | 4 quarterly | 4 quarterly |

**Note:** CDWWork2 uses simplified schema (Patient.Patient, Vital.VitalSign, etc.) compared to full Cerner Millennium schema used by demo patients (VeteranMill.SPerson, etc.).

---

## 3. Silver Layer Harmonization Requirements

### 3.1 Schema Differences to Reconcile

| Concept | CDWWork (VistA) | CDWWork2 (Cerner) |
|---------|-----------------|-------------------|
| Patient Key | PatientSID (INT) | PatientKey (VARCHAR) |
| Facility | Sta3n (INT) | FacilityCode (INT) |
| Date/Time | Separate date + time columns | Combined DATETIME |
| Medication Key | RxOutpatSID | MedicationKey (VARCHAR) |
| Problem Key | ProblemSID | ProblemKey (VARCHAR) |
| Encounter Key | InpatientSID | EncounterKey (VARCHAR) |

### 3.2 Address History Handling (Option B Implementation)

All three patients have **complete address history in CDWWork** with proper effective dates:

**Florida Address (Primary):**
- AddressEffectiveDateTime: 2010-01-01
- AddressExpireDateTime: 2025-01-31
- AddressActiveYN: 'N' (expired)

**Washington Address (Current):**
- AddressEffectiveDateTime: 2025-02-01
- AddressExpireDateTime: NULL (still active)
- AddressActiveYN: 'Y'

**Silver Layer Action:** Use `AddressEffectiveDateTime` and `AddressExpireDateTime` to determine address at any point in time. Do NOT rely solely on `AddressActiveYN` flag.

### 3.3 Medication Reconciliation

**Challenge:** Same patient may have overlapping medications in both systems during transition period (2025-02-01).

**Recommended Approach:**
1. Use `IssueDateTime` / `OrderDate` as the authoritative timestamp
2. Deduplicate by drug name + strength + issue date (±7 day tolerance)
3. Prefer CDWWork2 (Cerner) data for dates ≥ 2025-02-01
4. Preserve historical CDWWork (VistA) data for dates < 2025-02-01

### 3.4 Problem List Harmonization

**Key Considerations:**
- Same conditions may have different ICD-10 codes or descriptions between systems
- CDWWork uses `OnsetDate`, CDWWork2 uses `OnsetDate` (same field name, good!)
- Service-connected flags should match across systems (these are patient-level, not facility-level)

**Example Reconciliation:**

| Condition | CDWWork ICD-10 | CDWWork2 ICD-10 | Action |
|-----------|----------------|-----------------|--------|
| Hypertension | I10 | I10 | Exact match, merge by onset date |
| PTSD | F43.10 | F43.10 | Exact match, merge by onset date |
| Tinnitus | H93.13 (Joe) | H93.13 | Exact match, merge by onset date |

### 3.5 Charlson Comorbidity Index

Charlson scores are calculated in CDWWork based on problem list:

| Patient | Charlson Score | Key Conditions |
|---------|----------------|----------------|
| Bailey | 5 | Substance abuse (1) + Depression (1) + Chronic Pain (1) + Diabetes (1) + COPD (1) |
| Alananah | 2 | History of Breast Cancer (2012, in remission) |
| Joe | 0 | No Charlson-qualifying conditions |

**Silver Layer Action:** Recalculate Charlson scores from merged problem list to ensure consistency.

---

## 4. Data Quality Checks

### 4.1 Required Validation Checks

1. **Identity Resolution:**
   - Verify ICN200001, ICN200002, ICN200003 resolve to single patients
   - Verify PatientSID (CDWWork) and PatientKey (CDWWork2) map to same ICN

2. **Date Continuity:**
   - CDWWork data should end around 2025-02-01
   - CDWWork2 data should begin around 2025-02-01
   - No gaps or overlaps > 7 days

3. **Medication Reconciliation:**
   - Active medications in CDWWork (status='ACTIVE', issue date recent) should appear in CDWWork2
   - Check for duplicate entries (same drug + strength within 7 days)

4. **Problem List Consistency:**
   - Active problems in CDWWork should appear in CDWWork2
   - Service-connected percentages should match

5. **Address Transition:**
   - Florida address should be active until 2025-01-31
   - Washington address should be active from 2025-02-01
   - No overlapping active addresses

### 4.2 Expected Record Counts (Gold Layer)

After Silver harmonization and Gold transformation, expected record counts per patient:

| Domain | Bailey | Alananah | Joe |
|--------|--------|----------|-----|
| Demographics | 1 | 1 | 1 |
| Addresses (all time) | 2 | 2 | 2 |
| Vitals | 38 (32+6) | 33 (27+6) | 14 (8+6) |
| Medications (all time) | ~50 (45+5) | ~45 (40+5) | ~12 (8+4) |
| Encounters | 32 | 18 | 4 |
| Problems | 8-10 | 6-8 | 4-6 |
| Lab Results | 19 (15+4) | 14 (10+4) | 7 (3+4) |

---

## 5. File Locations and Execution Order

### 5.1 CDWWork Insert Scripts

**Location:** `/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/`

**Files:**
1. `Thompson-Bailey.sql` - 1,600+ lines, 16 sections
2. `Thompson-Alananah.sql` - 1,200+ lines, 16 sections
3. `Thompson-Joe.sql` - 800+ lines, 14 sections

**Master Script:** `_master.sql` (updated to include Thompson siblings in new section)

**Execution Order:**
1. Run dimension table scripts first (via `_master.sql`)
2. Run Thompson scripts in any order (no dependencies between siblings)
3. Verify with: `SELECT * FROM SPatient.SPatient WHERE PatientSID IN (2001, 2002, 2003)`

### 5.2 CDWWork2 Insert Scripts

**Location:** `/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork2/insert/`

**Files:**
1. `Thompson-Bailey.sql` - 350 lines, 5 sections
2. `Thompson-Alananah.sql` - 280 lines, 5 sections
3. `Thompson-Joe.sql` - 280 lines, 5 sections

**Master Script:** `_master.sql` (updated to include Thompson siblings after Step 6)

**Execution Order:**
1. Run Cerner demo patient scripts first (via `_master.sql` Steps 1-6)
2. Run Thompson scripts (Step 7 in `_master.sql`)
3. Verify with: `SELECT * FROM Patient.Patient WHERE PatientICN LIKE 'ICN2000%'`

---

## 6. Known Limitations and Future Enhancements

### 6.1 Current Limitations

1. **CDWWork2 Simplified Schema:** Thompson siblings use simplified schema (Patient.Patient) instead of full Cerner Millennium schema (VeteranMill.SPerson). This is intentional for Phase 1 but may need alignment in future phases.

2. **Abbreviated Sections:** Some clinical domains have abbreviated data in CDWWork2 (e.g., no immunizations, no clinical notes). This reflects typical "continuation of care" pattern where historical data stays in origin system.

3. **Manual SID Allocation:** RxOutpatSID ranges 8001-8093 are manually allocated. Future test patients should use ranges starting at 8094+ to avoid conflicts.

### 6.2 Future Enhancements

1. **DoD/CHCS Integration:** Add third data source for military treatment facility (MTF) records
2. **Community Care Partners:** Add commercial EHR data (e.g., Epic, AllScripts)
3. **Encounter Diagnoses:** Currently only Problem List is populated; add episodic encounter diagnoses
4. **Outpatient Visits:** Currently only inpatient encounters; add outpatient clinic visits
5. **Imaging Studies:** Add radiology reports and DICOM metadata
6. **Orders:** Add medication orders, lab orders, consult orders

---

## 7. Contact and Support

**Data Steward:** Chuck (med-z1 project lead)
**Documentation:**
- Requirements: `docs/spec/thompson-twins-patient-reqs.md` (v3.0)
- Implementation Plan: `docs/spec/thompson-twins-implementation-plan.md` (v2.0)
- This Document: `docs/spec/thompson-twins-integration-notes.md` (v1.0)

**Last Updated:** 2026-02-08
**Review Cycle:** Quarterly or upon major ETL changes
