# Vista RPC Broker - Vitals Testing Guide

**Last Updated:** 2025-12-19
**Version:** 1.0

## Quick Reference: Test Patients with Vitals Data

### Patient 1: ICN100001 (DOOREE, ADAM)
- **SSN:** 666-12-6789
- **DOB:** 1980-01-02
- **Total Vista Vitals:** 15 (across 3 sites)
- **Sites:** 200, 500, 630
- **DFNs:** 100001 (site 200), 500001 (site 500), 630001 (site 630)

### Patient 2: ICN100010 (AMINOR, ALEXANDER) ✅ Updated 2025-12-19
- **SSN:** 666-23-1010
- **DOB:** 1965-07-15
- **Total Vista Vitals:** 20 (across 2 sites, multiple DFNs)
- **Sites:** 200, 500
- **DFNs:**
  - Site 200: 100010 (correct registry DFN), 100002 (mapped orphan)
  - Site 500: 500010 (correct registry DFN), 200001 (mapped orphan)

### Patient 3: ICN100013 (THOMPSON, IRVING) ✅ Updated 2025-12-19
- **SSN:** 666-34-1013
- **DOB:** 1948-11-05
- **Total Vista Vitals:** 30 (across 3 sites, multiple DFNs)
- **Sites:** 200, 500, 630
- **DFNs:**
  - Site 200: 100003 (mapped orphan)
  - Site 500: 200002 (mapped orphan)
  - Site 630: 630013 (correct registry DFN), 300001, 300002, 630002 (mapped orphans)

---

## Testing Methods

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

## Integration with med-z1 App

When the med-z1 app calls Vista RPC Broker:

1. **User clicks "Refresh from VistA"** on Vitals page
2. **App calls `app/services/vista_client.py`** with ICN
3. **Vista client determines target sites** (default: 2 sites for vitals)
4. **Makes parallel RPC calls** to each site
5. **Merges responses** with PostgreSQL T-1 data
6. **Deduplicates** based on canonical event keys
7. **Displays complete timeline** to user

---

## Summary

✅ **3 patients** fully testable
✅ **65 total vitals** across all sites
✅ **Multi-site scenarios** supported
✅ **Orphaned data** rescued and accessible
✅ **Clean data model** with correct registry DFNs

**Ready for comprehensive Vista RPC Broker testing!**
