# Vista RPC Broker - Comprehensive Testing Guide

**Last Updated:** 2025-12-19
**Version:** 2.1

## Table of Contents

1. [Quick Reference: Test Patients](#quick-reference-test-patients)
2. [Vitals Testing](#vitals-testing)
3. [Encounters Testing](#encounters-testing)
4. [Allergies Testing](#allergies-testing)
5. [Testing Methods](#testing-methods)

---

## Quick Reference: Test Patients

### Patient 1: ICN100001 (DOOREE, ADAM)
- **SSN:** 666-12-6789
- **DOB:** 1980-01-02
- **Total Vista Vitals:** 15 (across 3 sites)
- **Total Vista Encounters:** 8 (across 3 sites)
- **Total Vista Allergies:** 9 (across 3 sites)
- **Sites:** 200, 500, 630
- **DFNs:** 100001 (site 200), 500001 (site 500), 630001 (site 630)

### Patient 2: ICN100010 (AMINOR, ALEXANDER) ✅ Updated 2025-12-19
- **SSN:** 666-23-1010
- **DOB:** 1965-07-15
- **Total Vista Vitals:** 20 (across 2 sites, multiple DFNs)
- **Total Vista Encounters:** 5 (across 2 sites)
- **Total Vista Allergies:** 9 (across 2 sites)
- **Sites:** 200, 500
- **DFNs:**
  - Site 200: 100010 (correct registry DFN), 100002 (mapped orphan)
  - Site 500: 500010 (correct registry DFN), 200001 (mapped orphan)

### Patient 3: ICN100013 (THOMPSON, IRVING) ✅ Updated 2025-12-19
- **SSN:** 666-34-1013
- **DOB:** 1948-11-05
- **Total Vista Vitals:** 30 (across 3 sites, multiple DFNs)
- **Total Vista Encounters:** 5 (site 630 only, multiple DFNs)
- **Total Vista Allergies:** 5 (site 630 only, multiple DFNs)
- **Sites:** 200, 500, 630
- **DFNs:**
  - Site 200: 100003 (mapped orphan)
  - Site 500: 200002 (mapped orphan)
  - Site 630: 630013 (correct registry DFN), 300001, 300002, 630002 (mapped orphans)

---

## Vitals Testing

## GMV LATEST VM RPC - Latest Vital Signs

### Testing Methods

### Method 1: curl Commands (Manual Testing)

```bash
# Start Vista service
python -m uvicorn vista.app.main:app --port 8003

# Test ICN100001 at site 200
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "GMV LATEST VM", "params": ["ICN100001"]}'

# Expected response:
# {
#   "success": true,
#   "response": "3251219.0845^BLOOD PRESSURE^128/82^mmHg^NURSE,SARAH\n...",
#   "site": "200",
#   "rpc": "GMV LATEST VM"
# }
```

### Method 2: Python Script

```python
import requests

def test_vista_vitals(icn, site):
    """Test Vista RPC vitals retrieval"""
    response = requests.post(
        f'http://localhost:8003/rpc/execute?site={site}',
        json={'name': 'GMV LATEST VM', 'params': [icn]}
    )

    data = response.json()

    if data['success']:
        vitals_lines = data['response'].split('\n')
        print(f"✅ {icn} at site {site}: {len(vitals_lines)} vitals")
        return vitals_lines
    else:
        print(f"❌ {icn} at site {site}: {data['error']}")
        return None

# Test all patients
test_vista_vitals('ICN100001', '200')
test_vista_vitals('ICN100010', '200')
test_vista_vitals('ICN100013', '630')
```

### Method 3: Analysis Script

```bash
# Run comprehensive analysis
python scripts/analyze_vista_vitals.py

# Shows:
# - All patients with vitals data
# - Sites with data for each patient
# - DFN mappings (including orphaned data)
# - Ready-to-use test commands
```

---

## Complete Test Matrix

| Patient | ICN | Site 200 | Site 500 | Site 630 | Total Vitals |
|---------|-----|----------|----------|----------|--------------|
| DOOREE, ADAM | ICN100001 | ✅ 5 vitals | ✅ 5 vitals | ✅ 5 vitals | 15 |
| AMINOR, ALEXANDER | ICN100010 | ✅ 10 vitals | ✅ 10 vitals | ❌ No data | 20 |
| THOMPSON, IRVING | ICN100013 | ✅ 5 vitals | ✅ 5 vitals | ✅ 20 vitals | 30 |

**Total:** 3 patients, 65 vitals records across 3 sites

---

## Test Scenarios

### Scenario 1: Single Patient, Single Site
```bash
# Test ICN100001 at primary site (200)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "GMV LATEST VM", "params": ["ICN100001"]}'
```

### Scenario 2: Multi-Site Patient
```bash
# Test ICN100001 across all 3 sites
for site in 200 500 630; do
  curl -s -X POST "http://localhost:8003/rpc/execute?site=$site" \
    -H 'Content-Type: application/json' \
    -d '{"name": "GMV LATEST VM", "params": ["ICN100001"]}' | \
    jq -r '.response' | wc -l
done
# Expected: 5 vitals from each site
```

### Scenario 3: Patient Not at Site
```bash
# Test ICN100010 at site 630 (not registered there)
curl -X POST 'http://localhost:8003/rpc/execute?site=630' \
  -H 'Content-Type: application/json' \
  -d '{"name": "GMV LATEST VM", "params": ["ICN100010"]}'

# Expected: "-1^Patient ICN100010 not registered at site 630"
```

### Scenario 4: Invalid ICN
```bash
# Test non-existent patient
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "GMV LATEST VM", "params": ["ICN999999"]}'

# Expected: "-1^Patient ICN999999 not found"
```

---

## Data Architecture Notes

### Dual-Source Pattern

Each patient can have vitals from two sources:

1. **Correct Registry DFNs** (Added 2025-12-19)
   - ICN100010: DFN 100010 (site 200), DFN 500010 (site 500)
   - ICN100013: DFN 630013 (site 630)

2. **Mapped Orphaned DFNs** (Mapped 2025-12-19)
   - Previously orphaned vitals data now accessible via ICN
   - Enables comprehensive multi-site testing
   - Total: 35 vitals records rescued from orphaned state

### Why Multiple DFNs per Site?

Some patients have multiple DFNs at the same site:
- **Original DFN:** From patient registry (e.g., ICN100010 → DFN 100010)
- **Mapped Orphaned DFN:** Vitals data that existed but wasn't linked to an ICN

This is realistic for Vista simulation as patients can have:
- Historical visits under different identifiers
- Transferred records
- Merged patient identities

---

## VistA Response Format

Vitals are returned in native VistA format (caret-delimited):

```
FileManDate.Time^VitalType^Value^Units^EnteredBy
```

**Example:**
```
3251219.0845^BLOOD PRESSURE^128/82^mmHg^NURSE,SARAH
3251219.0845^TEMPERATURE^98.4^F^NURSE,SARAH
3251219.0845^PULSE^76^/min^NURSE,SARAH
3251219.0845^RESPIRATION^18^/min^NURSE,SARAH
3251219.0845^PULSE OXIMETRY^97^%^NURSE,SARAH
```

**FileMan Date Format:**
- `YYYMMDD.HHMM` where YYY = year - 1700
- Example: `3251219` = December 19, 2025 (2025 - 1700 = 325)

---

## Automated Test Suite

Run Vista tests to verify vitals retrieval:

```bash
# Run all Vista tests
pytest vista/tests/ -v

# Run only vitals handler tests
pytest vista/tests/test_vitals_handler.py -v

# Run only API integration tests
pytest vista/tests/test_api_integration.py -v
```

**Expected:** 129 tests passing (including vitals tests)

---

## Troubleshooting

### Patient Shows "Not Found"
**Problem:** `-1^Patient ICN100001 not found`

**Solution:** Check `mock/shared/patient_registry.json` - patient must be registered globally

---

### Patient Shows "Not Registered at Site"
**Problem:** `-1^Patient ICN100010 not registered at site 630`

**Solution:** Check `treating_facilities` in registry - patient must have a DFN for that site

---

### No Vitals Returned (Empty Response)
**Problem:** Response is `""`

**Solution:** Check `vista/app/data/sites/{sta3n}/vitals.json` - DFN must have vitals data

---

### Service Won't Start
**Problem:** Port 8003 already in use

**Solution:**
```bash
# Find process
lsof -i :8003

# Kill it
kill -9 <PID>

# Or use different port
uvicorn vista.app.main:app --port 8004
```

---

## Encounters Testing

### ORWCV ADMISSIONS RPC - Inpatient Encounters

**Purpose:** Returns inpatient encounters/admissions for a patient within a specified lookback period (default 90 days).

### Testing Methods

#### Method 1: curl Commands (Manual Testing)

```bash
# Start Vista service
python -m uvicorn vista.app.main:app --port 8003

# Test ICN100001 at site 200 (recent discharge + active admission)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWCV ADMISSIONS", "params": ["ICN100001", 90]}'

# Expected response (caret-delimited encounters):
# {
#   "success": true,
#   "response": "285001^3251212.1430^7A MED/SURG^DISCHARGED^3251217.1015^HOME^5^I50.9^DOE,JOHN\n285023^3251219.0830^TELEMETRY^ACTIVE^^^^^I21.9^WILSON,CHRISTOPHER",
#   "site": "200",
#   "rpc": "ORWCV ADMISSIONS"
# }
```

#### Method 2: Python Script

```python
import requests

def test_vista_encounters(icn, site, days_back=90):
    """Test Vista RPC encounters retrieval"""
    response = requests.post(
        f'http://localhost:8003/rpc/execute?site={site}',
        json={'name': 'ORWCV ADMISSIONS', 'params': [icn, days_back]}
    )

    data = response.json()

    if data['success']:
        encounters = data['response'].split('\n')
        active = [e for e in encounters if '^ACTIVE^' in e]
        discharged = [e for e in encounters if '^DISCHARGED^' in e]
        print(f"✅ {icn} at site {site}: {len(active)} active, {len(discharged)} discharged")
        return encounters
    else:
        print(f"❌ {icn} at site {site}: {data['error']}")
        return None

# Test all patients
test_vista_encounters('ICN100001', '200')  # Recent discharge + active
test_vista_encounters('ICN100010', '500')  # Active MI admission
test_vista_encounters('ICN100013', '630')  # Multiple encounters including COPD
```

### Complete Encounters Test Matrix

| Patient | ICN | Site 200 | Site 500 | Site 630 | Total Encounters |
|---------|-----|----------|----------|----------|------------------|
| DOOREE, ADAM | ICN100001 | ✅ 3 (1 active, 2 discharged) | ✅ 2 (1 discharged) | ✅ 3 (1 discharged) | 8 |
| AMINOR, ALEXANDER | ICN100010 | ✅ 2 (1 active, 1 discharged) | ✅ 2 (1 active, 1 discharged) | ❌ No data | 4 |
| THOMPSON, IRVING | ICN100013 | ❌ No data | ❌ No data | ✅ 5 (1 discharged today, 4 past) | 5 |

**Total:** 3 patients, 18 encounter records across 3 sites

### Test Scenarios

#### Scenario 1: Active Admissions
```bash
# Test ICN100010 at site 500 (active MI admission)
curl -X POST 'http://localhost:8003/rpc/execute?site=500' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWCV ADMISSIONS", "params": ["ICN100010", 90]}'

# Look for: ^ACTIVE^ with empty discharge_datetime and discharge_location
```

#### Scenario 2: Recent Discharges
```bash
# Test ICN100013 at site 630 (COPD discharge today)
curl -X POST 'http://localhost:8003/rpc/execute?site=630' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWCV ADMISSIONS", "params": ["ICN100013", 90]}'

# Look for: ^DISCHARGED^ with populated discharge fields
```

#### Scenario 3: Days Back Parameter
```bash
# Test with 30-day lookback (fewer results)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWCV ADMISSIONS", "params": ["ICN100001", 30]}'

# Test with 90-day lookback (more results)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWCV ADMISSIONS", "params": ["ICN100001", 90]}'
```

#### Scenario 4: Patient Not at Site
```bash
# Test ICN100013 at site 200 (not registered there)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWCV ADMISSIONS", "params": ["ICN100013", 90]}'

# Expected: "-1^Patient ICN100013 not registered at site 200"
```

### VistA Encounters Response Format

Encounters are returned in native VistA format (caret-delimited):

```
InpatientID^AdmitDateTime^AdmitLocation^Status^DischargeDateTime^DischargeLocation^LOS^DiagnosisCode^AdmitProvider
```

**Example (Active Admission):**
```
590078^3251219.1430^TELEMETRY^ACTIVE^^^^^I21.9^WILSON,CHRISTOPHER
```

**Example (Discharged):**
```
730089^3250920.0815^4A GENERAL MED^DISCHARGED^3250925.1215^HOME^5^N18.3^MARTINEZ,JENNIFER
```

**Field Descriptions:**
1. **InpatientID** - Unique encounter identifier
2. **AdmitDateTime** - FileMan date/time of admission
3. **AdmitLocation** - Ward/unit where admitted
4. **Status** - "ACTIVE" or "DISCHARGED"
5. **DischargeDateTime** - FileMan date/time (empty if active)
6. **DischargeLocation** - Disposition (empty if active)
7. **LOS** - Length of stay in days (0 if active)
8. **DiagnosisCode** - ICD-10 diagnosis code
9. **AdmitProvider** - Admitting provider name

**FileMan Date Format:**
- `YYYMMDD.HHMM` where YYY = year - 1700
- Example: `3251219` = December 19, 2025 (2025 - 1700 = 325)

### Automated Test Suite

Run Vista encounters tests:

```bash
# Run all Vista tests
pytest vista/tests/ -v

# Run only encounters handler tests
pytest vista/tests/test_encounters_handler.py -v
```

**Expected:** 24 encounters tests passing (part of 150 total)

---

## Allergies Testing

### ORQQAL LIST RPC - Patient Allergy List

**Purpose:** Returns all documented allergies and adverse reactions for a patient.

### Testing Methods

#### Method 1: curl

```bash
# Test ICN100001 at site 200 (has Penicillin, Shellfish, Latex allergies)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORQQAL LIST", "params": ["ICN100001"]}'

# Expected response (caret-delimited allergies):
# {
#   "success": true,
#   "response": "PENICILLIN^SEVERE^3251219.0930^HIVES,ITCHING,RASH^DRUG^200^PHARMACIST,JOHN\nSHELLFISH^MODERATE^3251219.1445^NAUSEA,VOMITING^FOOD^200^NURSE,SARAH\nLATEX^MILD^3251219.1020^CONTACT DERMATITIS^ENVIRONMENTAL^200^NURSE,MICHAEL",
#   "site": "200",
#   "rpc": "ORQQAL LIST"
# }
```

#### Method 2: Python Script

```python
import requests

def get_patient_allergies(icn, site='200'):
    """Get patient allergies from Vista RPC Broker"""
    response = requests.post(
        f'http://localhost:8003/rpc/execute?site={site}',
        json={'name': 'ORQQAL LIST', 'params': [icn]}
    )

    data = response.json()

    if data['success']:
        print(f"\n✅ Patient {icn} at Site {site}:")
        print(f"Response:\n{data['response']}")

        # Parse allergies
        allergies = data['response'].split('\n')
        print(f"\nTotal allergies: {len(allergies)}")

        for allergy in allergies:
            fields = allergy.split('^')
            if len(fields) == 7:
                print(f"  - {fields[0]} ({fields[4]}) - {fields[1]} severity")
    else:
        print(f"❌ Error: {data.get('error')}")

# Test all patients
get_patient_allergies('ICN100001', '200')
get_patient_allergies('ICN100010', '500')
get_patient_allergies('ICN100013', '630')
```

### Complete Allergies Test Matrix

| Patient | ICN | Site 200 | Site 500 | Site 630 | Total Allergies |
|---------|-----|----------|----------|----------|------------------|
| DOOREE, ADAM | ICN100001 | ✅ 3 (PENICILLIN, SHELLFISH, LATEX) | ✅ 3 (SULFA, CODEINE, TREE POLLEN) | ✅ 3 (PENICILLIN, EGGS, MOLD) | 9 |
| AMINOR, ALEXANDER | ICN100010 | ✅ 3 (SULFA, PEANUTS, BEE STINGS) | ✅ 3 (PENICILLIN, DAIRY, DUST MITES) | ❌ No data | 6 |
| THOMPSON, IRVING | ICN100013 | ❌ 1 (ASPIRIN - mapped orphan) | ❌ 1 (IODINE - mapped orphan) | ✅ 5 (SULFA, WHEAT, RAGWEED, MORPHINE, PENICILLIN, NSAIDS) | 7 |

### Common Testing Scenarios

#### Scenario 1: Drug Allergies (Critical)

```bash
# Test for Penicillin allergy at site 200
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORQQAL LIST", "params": ["ICN100001"]}'

# Look for: PENICILLIN^SEVERE with reactions
```

#### Scenario 2: Multiple Allergy Types

```bash
# Test ICN100001 at site 630 (has DRUG, FOOD, ENVIRONMENTAL)
curl -X POST 'http://localhost:8003/rpc/execute?site=630' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORQQAL LIST", "params": ["ICN100001"]}'

# Should return mix of allergy types
```

#### Scenario 3: Patient Not at Site

```bash
# Test ICN100013 at site 200 (not registered there)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORQQAL LIST", "params": ["ICN100013"]}'

# Expected: "-1^Patient ICN100013 not registered at site 200"
```

#### Scenario 4: No Known Allergies

```bash
# Test ICN100002 at site 200 (has no allergies in test data)
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORQQAL LIST", "params": ["ICN100002"]}'

# Expected: Empty string (not an error - valid clinical state)
```

### VistA Allergies Response Format

Allergies are returned in native VistA format (caret-delimited):

```
AllergenName^Severity^ReactionDateTime^Reactions^AllergyType^OriginatingSite^EnteredBy
```

**Field Definitions:**
1. **AllergenName** - Allergen (e.g., "PENICILLIN", "SHELLFISH", "LATEX")
2. **Severity** - MILD | MODERATE | SEVERE
3. **ReactionDateTime** - FileMan format (YYYMMDD.HHMM)
4. **Reactions** - Comma-separated reactions (e.g., "HIVES,ITCHING")
5. **AllergyType** - DRUG | FOOD | ENVIRONMENTAL
6. **OriginatingSite** - Site where allergy was first documented
7. **EnteredBy** - Staff member who entered the allergy

**Example Response:**
```
PENICILLIN^SEVERE^3251120.0930^HIVES,ITCHING,RASH^DRUG^200^PHARMACIST,JOHN
SHELLFISH^MODERATE^3250815.1445^NAUSEA,VOMITING^FOOD^200^NURSE,SARAH
SULFA DRUGS^MODERATE^3241030.0800^RASH,FEVER^DRUG^200^DOCTOR,EMILY
```

### Testing T-Notation Date Conversion

Allergy test data uses T-notation (relative dates) that are converted to FileMan format at runtime:

```bash
# Get allergies and verify dates are in FileMan format
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORQQAL LIST", "params": ["ICN100001"]}'

# Verify reaction_datetime field (field 3) is in FileMan format: YYYMMDD.HHMM
# Example: 3251219.0930 = December 19, 2025 at 09:30
```

### Unit Testing

```bash
# Run only allergies handler tests
pytest vista/tests/test_allergies_handler.py -v
```

**Expected:** 21 allergies tests passing (part of 150 total)

---

## Integration with med-z1 App

When the med-z1 app calls Vista RPC Broker:

1. **User clicks "Refresh from VistA"** on Vitals, Encounters, or Allergies page
2. **App calls `app/services/vista_client.py`** with ICN
3. **Vista client determines target sites** (default: 3 sites for encounters, 2 for vitals)
4. **Makes parallel RPC calls** to each site
5. **Merges responses** with PostgreSQL T-1 data
6. **Deduplicates** based on canonical event keys
7. **Displays complete timeline** to user

---

## Summary

✅ **3 patients** fully testable
✅ **65 total vitals** across all sites
✅ **18 total encounters** across all sites
✅ **Multi-site scenarios** supported
✅ **Orphaned data** rescued and accessible
✅ **Clean data model** with correct registry DFNs
✅ **Both active and discharged encounters** for realistic testing

**Ready for comprehensive Vista RPC Broker testing!**
