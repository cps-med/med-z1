# VistA RPC Broker - Manual Testing Guide

This guide shows you how to manually test the VistA RPC Broker service using three different methods.

---

## Prerequisites

1. **Start the Vista RPC Broker service:**

```bash
# From project root
source .venv/bin/activate
uvicorn vista.app.main:app --reload --port 8003
```

2. **Verify service is running:**

```bash
curl http://localhost:8003/health
```

Expected output:
```json
{
  "status": "healthy",
  "sites_initialized": 3,
  "sites": ["200", "500", "630"]
}
```

---

## Method 1: Python Test Script (Recommended)

The most comprehensive test - validates site selection, multi-site queries, and integration with the Vista service.

### Run the automated manual test script:

```bash
# From project root
source .venv/bin/activate
python app/services/test_vista_manual.py
```

**What it tests:**
- ✅ Basic site selection for different domains
- ✅ Single-site patient handling
- ✅ Hard maximum enforcement (10 sites)
- ✅ User-selected sites override
- ✅ Multi-site RPC execution
- ✅ Error handling for non-existent patients
- ✅ Site sorting by last_seen date

**Expected output:**
```
╔════════════════════════════════════════════════════════════════════╗
║                   VistaClient Manual Testing Suite                 ║
║                    Phase 2: Multi-Site Selection                   ║
╚════════════════════════════════════════════════════════════════════╝

======================================================================
  Test 1: Basic Site Selection (ICN100001)
======================================================================
...
[42/42 tests pass]
```

---

## Method 2: curl Commands (Quick Testing)

Use curl to test individual endpoints directly from the command line.

### Test 1: Health Check

```bash
curl -s http://localhost:8003/health | python -m json.tool
```

Expected:
```json
{
    "status": "healthy",
    "sites_initialized": 3,
    "sites": ["200", "500", "630"]
}
```

---

### Test 2: List Available Sites

```bash
curl -s http://localhost:8003/sites | python -m json.tool
```

Expected:
```json
[
  {
    "sta3n": "200",
    "name": "ALEXANDRIA",
    "rpcs_registered": 1,
    "patients_registered": 2
  },
  {
    "sta3n": "500",
    "name": "ANCHORAGE",
    "rpcs_registered": 1,
    "patients_registered": 2
  },
  {
    "sta3n": "630",
    "name": "PALO_ALTO",
    "rpcs_registered": 1,
    "patients_registered": 2
  }
]
```

---

### Test 3: Execute Patient Inquiry RPC (Success Case)

Query patient ICN100001 at site 200 (patient exists at this site):

```bash
curl -s -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ORWPT PTINQ",
    "params": ["ICN100001"]
  }' | python -m json.tool
```

Expected:
```json
{
    "success": true,
    "response": "DOOREE,ADAM^666-12-6789^2800102^M^VETERAN",
    "error": null,
    "site": "200",
    "rpc": "ORWPT PTINQ"
}
```

**Response Format:** `NAME^SSN^DOB^SEX^VETERAN_STATUS`

---

### Test 4: Execute RPC with Patient Not Registered at Site

Query patient ICN100013 at site 200 (patient only registered at site 630):

```bash
curl -s -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ORWPT PTINQ",
    "params": ["ICN100013"]
  }' | python -m json.tool
```

Expected (VistA error format):
```json
{
    "success": true,
    "response": "-1^Patient ICN100013 not registered at site 200",
    "error": null,
    "site": "200",
    "rpc": "ORWPT PTINQ"
}
```

**VistA Error Format:** `-1^Error message`

---

### Test 5: Execute RPC with Non-Existent Patient

```bash
curl -s -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ORWPT PTINQ",
    "params": ["ICN999999"]
  }' | python -m json.tool
```

Expected (VistA error format):
```json
{
    "success": true,
    "response": "-1^Patient ICN999999 not found in registry",
    "error": null,
    "site": "200",
    "rpc": "ORWPT PTINQ"
}
```

---

### Test 6: Execute RPC with Invalid Site

```bash
curl -s -X POST 'http://localhost:8003/rpc/execute?site=999' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ORWPT PTINQ",
    "params": ["ICN100001"]
  }' | python -m json.tool
```

Expected (HTTP 404):
```json
{
    "detail": "Site 999 not found"
}
```

---

### Test 7: Execute RPC with Missing Site Parameter

```bash
curl -s -X POST 'http://localhost:8003/rpc/execute' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ORWPT PTINQ",
    "params": ["ICN100001"]
  }' | python -m json.tool
```

Expected (HTTP 422 - validation error):
```json
{
    "detail": [
        {
            "loc": ["query", "site"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

---

### Test 8: Execute RPC with Missing Parameters

```bash
curl -s -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ORWPT PTINQ",
    "params": []
  }' | python -m json.tool
```

Expected:
```json
{
    "success": false,
    "response": null,
    "error": "ORWPT PTINQ requires 1 parameter (ICN), got 0",
    "site": "200",
    "rpc": "ORWPT PTINQ"
}
```

---

### Test 9: Execute Unregistered RPC

```bash
curl -s -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "NONEXISTENT RPC",
    "params": []
  }' | python -m json.tool
```

Expected:
```json
{
    "success": false,
    "response": null,
    "error": "RPC 'NONEXISTENT RPC' is not registered",
    "site": "200",
    "rpc": "NONEXISTENT RPC"
}
```

---

## Method 3: Browser-Based Testing (Interactive API Docs)

The Vista service includes interactive OpenAPI/Swagger documentation.

### Access the API Documentation:

1. **Start Vista service** (if not already running)
2. **Open browser:** http://localhost:8003/docs
3. **Explore available endpoints:**
   - `GET /` - API information
   - `GET /health` - Health check
   - `GET /sites` - List sites
   - `POST /rpc/execute` - Execute RPC

### Try an RPC call via the UI:

1. **Click on `POST /rpc/execute`**
2. **Click "Try it out"**
3. **Fill in parameters:**
   - `site`: `200`
   - Request body:
     ```json
     {
       "name": "ORWPT PTINQ",
       "params": ["ICN100001"]
     }
     ```
4. **Click "Execute"**
5. **View response** in the browser

---

## Test Data Reference

### Available Patients

From `mock/shared/patient_registry.json`:

| ICN | Name | Sites | Last Seen |
|-----|------|-------|-----------|
| **ICN100001** | DOOREE, ADAM | 200, 500, 630 | 200: T-7<br>500: T-30<br>630: T-180 |
| **ICN100010** | AMINOR, BOB | 200 | T-14 |
| **ICN100013** | THOMPSON, CHARLIE | 630 | T-3 |

### Available Sites

| sta3n | Name | Patients |
|-------|------|----------|
| **200** | ALEXANDRIA | ICN100001, ICN100010 |
| **500** | ANCHORAGE | ICN100001 |
| **630** | PALO_ALTO | ICN100001, ICN100013 |

### Available RPCs

| RPC Name | Parameters | Returns |
|----------|------------|---------|
| **ORWPT PTINQ** | ICN (string) | Patient demographics in VistA format:<br>`NAME^SSN^DOB^SEX^VETERAN_STATUS` |

---

## Quick Test Scenarios

### Scenario 1: Happy Path

**Goal:** Verify basic RPC execution works

```bash
# Start service
uvicorn vista.app.main:app --reload --port 8003

# Query patient at their primary site
curl -s -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name":"ORWPT PTINQ","params":["ICN100001"]}' \
  | python -m json.tool
```

**Expected:** Success response with patient data

---

### Scenario 2: Patient at Multiple Sites

**Goal:** Verify patient exists at multiple sites

```bash
# Query same patient at different sites
for site in 200 500 630; do
  echo "=== Site $site ==="
  curl -s -X POST "http://localhost:8003/rpc/execute?site=$site" \
    -H 'Content-Type: application/json' \
    -d '{"name":"ORWPT PTINQ","params":["ICN100001"]}' \
    | python -m json.tool | grep -A1 '"success"'
  echo ""
done
```

**Expected:** All three sites return success

---

### Scenario 3: Patient Not Registered at Site

**Goal:** Verify error handling for patient not at specific site

```bash
# ICN100013 only exists at site 630, query at site 200
curl -s -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name":"ORWPT PTINQ","params":["ICN100013"]}' \
  | python -m json.tool
```

**Expected:** Response with `-1^Patient not registered...` in VistA format

---

### Scenario 4: VistaClient Integration Test

**Goal:** Test site selection + RPC execution end-to-end

```bash
# From project root
cat > /tmp/test_vista.py << 'EOF'
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from app.services.vista_client import get_vista_client

async def test():
    vista_client = get_vista_client()

    # Test site selection
    icn = "ICN100001"
    sites = vista_client.get_target_sites(icn, "demographics")
    print(f"Site selection: {sites}")

    # Test RPC call
    result = await vista_client.call_rpc(
        site="200",
        rpc_name="ORWPT PTINQ",
        params=[icn]
    )

    if result.get("success"):
        print(f"✓ RPC Success: {result.get('response')[:60]}...")
    else:
        print(f"✗ RPC Failed: {result.get('error')}")

    await vista_client.close()

asyncio.run(test())
EOF

python /tmp/test_vista.py
```

**Expected:**
```
Site selection: ['200']
✓ RPC Success: DOOREE,ADAM^666-12-6789^2800102^M^VETERAN...
```

---

## Troubleshooting

### Service Won't Start

**Error:** `ModuleNotFoundError: No module named 'vista'`

**Solution:** Run from project root, not from vista/ directory:
```bash
# ✗ Wrong (from vista/ directory)
cd vista && uvicorn app.main:app --port 8003

# ✓ Correct (from project root)
uvicorn vista.app.main:app --reload --port 8003
```

---

### Connection Refused

**Error:** `Connection refused` when running curl

**Check:** Is the service running?
```bash
# Check if port 8003 is listening
lsof -i :8003

# Or try health check
curl http://localhost:8003/health
```

**Solution:** Start the service first

---

### Empty Response

**Error:** curl returns empty response

**Check:** Did you include the site parameter?
```bash
# ✗ Missing site parameter (returns 422 error)
curl -X POST 'http://localhost:8003/rpc/execute' ...

# ✓ Include site parameter
curl -X POST 'http://localhost:8003/rpc/execute?site=200' ...
```

---

## Next Steps

After manual testing, you can:

1. **Run automated integration tests:**
   ```bash
   pytest vista/tests/test_api_integration.py -v
   ```

2. **Run all Vista unit tests:**
   ```bash
   pytest vista/tests/ -v
   ```

3. **Run Phase 2 site selection tests:**
   ```bash
   pytest app/tests/test_vista_client.py -v
   ```

4. **Review test coverage:**
   ```bash
   pytest vista/tests/ --cov=vista --cov-report=term-missing
   ```

---

## Documentation Links

- **Phase 2 Completion Summary:** `app/services/PHASE2_COMPLETE.md`
- **Vista Design Document:** `docs/spec/vista-rpc-broker-design.md`
- **Integration Test Code:** `vista/tests/test_api_integration.py`
- **VistaClient Usage Examples:** `app/services/vista_client_example.py`
- **Automated Manual Test Script:** `app/services/test_vista_manual.py`

---

**Last Updated:** 2026-02-11
**Status:** Superseded status text. See `docs/spec/implementation-status.md` and `docs/spec/vista-rpc-broker-design.md` for current implementation state.
