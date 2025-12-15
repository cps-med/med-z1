# VistA RPC Broker Simulator

**Version:** 1.0.0
**Status:** Phase 1 Complete - Production Ready for Single RPC
**Port:** 8003

> **📝 Note:** When updating implementation or design, keep these docs in sync:
> - This file (`vista/README.md`) - Practical guide (update: API endpoints, capabilities, examples, test coverage)
> - `docs/vista-rpc-broker-design.md` - Design decisions (update: architecture, implementation plan)
> - `docs/implementation-roadmap.md` Section 11.3 - Progress tracking

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Reference](#api-reference)
4. [Development Guide](#development-guide)
5. [Testing Guide](#testing-guide)
6. [Operations Guide](#operations-guide)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What It Is

The VistA RPC Broker Simulator is a FastAPI-based HTTP service that simulates the VA VistA Remote Procedure Call (RPC) interface. It enables the med-z1 application to develop and test real-time data access (T-0, today) without requiring connection to actual VistA systems.

### Why It Exists

**Problem:** VA's Corporate Data Warehouse (CDW) is updated nightly, so data is always at least T-1 (yesterday). For current-day clinical data, applications must query VistA sites directly via RPC.

**Solution:** This simulator provides:
- **Real-time data layer** - Simulates T-0 (today) data from VistA sites
- **Multi-site support** - Simulates 3 VistA sites (200, 500, 630)
- **Authentic responses** - Returns data in native VistA format (caret-delimited strings)
- **ICN → DFN resolution** - Automatically translates enterprise ICN to site-specific DFN
- **Development safety** - Uses synthetic data only (no PHI/PII)

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Med-z1 App (Port 8000)                         │
│  ┌───────────────────────────────────────────┐  │
│  │ "Refresh from VistA" button               │  │
│  │  ↓                                        │  │
│  │ app/services/vista_client.py              │  │
│  │  - call_rpc_multi_site()                  │  │
│  │  - Merge PostgreSQL + Vista data          │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────┘
                      │ HTTP POST
                      │ /rpc/execute?site=200
                      ▼
┌─────────────────────────────────────────────────┐
│  VistA RPC Broker (Port 8003)                   │
│  ┌───────────────────────────────────────────┐  │
│  │ FastAPI Service (vista/app/main.py)       │  │
│  └───────────────────┬───────────────────────┘  │
│                      │                          │
│  ┌───────────────────┴─────────────────────┐    │
│  │ Site 200 | Site 500 | Site 630          │    │
│  │ ────────────────────────────────────    │    │
│  │ DataLoader (ICN→DFN)                    │    │
│  │ RPCRegistry                             │    │
│  │  - ORWPT PTINQ (Patient Inquiry)        │    │
│  │  - (Future: Vitals, Allergies, Meds)    │    │
│  └─────────────────────────────────────────┘    │
│                     │                           │
│  ┌──────────────────┴─────────────────────┐     │
│  │ mock/shared/patient_registry.json      │     │
│  │  - ICN → DFN mappings                  │     │
│  │  - 3 real test patients                │     │
│  └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

### Current Capabilities (Phase 1)

**Sites:**
- 200 (ALEXANDRIA)
- 500 (ANCHORAGE)
- 630 (PALO_ALTO)

**RPCs Implemented:**
- ✅ ORWPT PTINQ - Patient demographics inquiry

**Test Patients:**
- ICN100001 (Dooree, Adam) - Sites 200, 500, 630
- ICN100010 (Aminor, Alexander) - Sites 200, 500
- ICN100013 (Thompson, Irving) - Site 630 only

---

## Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment activated (`.venv`)
- Dependencies installed (`pip install -r requirements.txt`)

### Start the Service

```bash
# From project root
python -m uvicorn vista.app.main:app --port 8003 --reload

# Or run directly
cd vista
python -m app.main
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Site 200 initialized: 1 RPCs, 2 patients
INFO:     Site 500 initialized: 1 RPCs, 2 patients
INFO:     Site 630 initialized: 1 RPCs, 2 patients
INFO:     VistA RPC Broker ready: 3 sites initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8003
```

### Verify Service

```bash
# Health check
curl http://localhost:8003/health

# List sites
curl http://localhost:8003/sites

# Execute patient inquiry
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100001"]}'
```

**Success response:**
```json
{
  "success": true,
  "response": "DOOREE,ADAM^666-12-6789^2800102^M^VETERAN",
  "error": null,
  "site": "200",
  "rpc": "ORWPT PTINQ"
}
```

---

## API Reference

### Base URL

```
http://localhost:8003
```

### Endpoints

#### 1. GET `/` - Service Information

**Description:** Returns service metadata and available endpoints.

**Request:**
```bash
curl http://localhost:8003/
```

**Response:**
```json
{
  "service": "VistA RPC Broker Simulator",
  "version": "1.0.0",
  "status": "running",
  "sites": 3,
  "endpoints": {
    "rpc_execute": "POST /rpc/execute?site={sta3n}",
    "sites": "GET /sites",
    "health": "GET /health",
    "docs": "GET /docs"
  }
}
```

---

#### 2. GET `/health` - Health Check

**Description:** Returns service health status and initialized sites.

**Request:**
```bash
curl http://localhost:8003/health
```

**Response:**
```json
{
  "status": "healthy",
  "sites_initialized": 3,
  "sites": ["200", "500", "630"]
}
```

---

#### 3. GET `/sites` - List Sites

**Description:** Returns details about all configured VistA sites.

**Request:**
```bash
curl http://localhost:8003/sites
```

**Response:**
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

#### 4. POST `/rpc/execute` - Execute RPC

**Description:** Execute a VistA RPC at a specific site.

**Parameters:**
- `site` (query, required) - Site station number (200, 500, or 630)

**Request Body:**
```json
{
  "name": "ORWPT PTINQ",
  "params": ["ICN100001"]
}
```

**Request:**
```bash
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100001"]}'
```

**Success Response:**
```json
{
  "success": true,
  "response": "DOOREE,ADAM^666-12-6789^2800102^M^VETERAN",
  "error": null,
  "site": "200",
  "rpc": "ORWPT PTINQ"
}
```

**Error Response (Patient Not Found):**
```json
{
  "success": true,
  "response": "-1^Patient ICN999999 not found",
  "error": null,
  "site": "200",
  "rpc": "ORWPT PTINQ"
}
```

**Error Response (Invalid Site):**
```json
{
  "detail": "Site 999 not found. Available sites: ['200', '500', '630']"
}
```

---

### RPC: ORWPT PTINQ (Patient Inquiry)

**Description:** Returns patient demographics in VistA format.

**VistA Format:** `NAME^SSN^DOB^SEX^VETERAN_STATUS`

**Parameters:**
- `params[0]`: ICN (Integrated Care Number)

**Examples:**

**Patient at Site 200:**
```bash
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100001"]}'
```
Response: `"DOOREE,ADAM^666-12-6789^2800102^M^VETERAN"`

**Patient at Site 500:**
```bash
curl -X POST 'http://localhost:8003/rpc/execute?site=500' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100010"]}'
```
Response: `"AMINOR,ALEXANDER^666-23-1010^2650715^M^VETERAN"`

**Patient Not at Site:**
```bash
# ICN100013 is only at site 630
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100013"]}'
```
Response: `"-1^Patient ICN100013 not registered at site 200"`

---

## Development Guide

### Project Structure

```
vista/
  app/
    main.py                    # FastAPI application
    services/
      data_loader.py           # ICN→DFN resolution, patient registry
      rpc_handler.py           # Base RPC handler interface
      rpc_registry.py          # Handler registration and dispatch
    handlers/
      demographics.py          # ORWPT* RPCs
      # Future: vitals.py, allergies.py, medications.py
    utils/
      m_serializer.py          # VistA format conversion
  tests/
    test_data_loader.py
    test_rpc_registry.py
    test_m_serializer.py
    test_demographics_handler.py
  README.md                    # This file
```

### Adding a New RPC Handler

**Step 1: Create the Handler**

```python
# vista/app/handlers/vitals.py
from typing import Any, Dict, List
from vista.app.services import RPCHandler, RPCExecutionError
from vista.app.utils import pack_vista_list

class LatestVitalsHandler(RPCHandler):
    """Handler for GMV LATEST VM - Get latest vitals"""

    @property
    def rpc_name(self) -> str:
        return "GMV LATEST VM"

    def execute(self, params: List[Any], context: Dict[str, Any]) -> str:
        icn = params[0]
        data_loader = context["data_loader"]

        # Get patient vitals (implement data loading)
        vitals = self._get_vitals(icn, data_loader)

        # Format as VistA multi-line response
        response = pack_vista_list(
            vitals,
            field_order=["date", "type", "value", "unit"]
        )

        return response
```

**Step 2: Register the Handler**

```python
# vista/app/main.py
from vista.app.handlers import PatientInquiryHandler
from vista.app.handlers.vitals import LatestVitalsHandler  # Add import

def initialize_site(sta3n: str) -> Dict[str, Any]:
    # ... existing code ...

    # Register handlers
    registry.register(PatientInquiryHandler())
    registry.register(LatestVitalsHandler())  # Add registration

    return {...}
```

**Step 3: Create Tests**

```python
# vista/tests/test_vitals_handler.py
import pytest
from vista.app.handlers.vitals import LatestVitalsHandler

class TestLatestVitalsHandler:
    def test_handler_rpc_name(self):
        handler = LatestVitalsHandler()
        assert handler.rpc_name == "GMV LATEST VM"

    def test_execute_success(self, context_200):
        handler = LatestVitalsHandler()
        response = handler.execute(["ICN100001"], context_200)
        assert "^" in response  # Check VistA format
```

### VistA Format Reference

**Common Delimiters:**
- `^` (caret) - Field separator
- `\n` (newline) - List item separator
- `;` (semicolon) - Sub-field separator

**Helper Functions:**
```python
from vista.app.utils import (
    pack_vista_string,     # Single line: field1^field2^field3
    pack_vista_list,       # Multi-line list
    pack_vista_array,      # Key=value pairs
    format_rpc_error,      # -1^Error message
)

# Single line
response = pack_vista_string(["SMITH", "123", "M"])
# Returns: "SMITH^123^M"

# Multi-line list
items = [
    {"date": "3241201", "type": "BP", "value": "120/80"},
    {"date": "3241202", "type": "TEMP", "value": "98.6"}
]
response = pack_vista_list(items, ["date", "type", "value"])
# Returns: "3241201^BP^120/80\n3241202^TEMP^98.6"

# Error
response = format_rpc_error("Patient not found", code="-1")
# Returns: "-1^Patient not found"
```

---

## Testing Guide

### Run All Tests

```bash
# From project root
python -m pytest vista/tests/ -v

# With coverage
python -m pytest vista/tests/ --cov=vista --cov-report=html
```

**Expected output:**
```
===== 82 passed in 0.03s =====
```

### Run Specific Test Suite

```bash
# Data loader tests
python -m pytest vista/tests/test_data_loader.py -v

# RPC registry tests
python -m pytest vista/tests/test_rpc_registry.py -v

# M-Serializer tests
python -m pytest vista/tests/test_m_serializer.py -v

# Demographics handler tests
python -m pytest vista/tests/test_demographics_handler.py -v
```

### Integration Testing

**Start the service:**
```bash
python -m uvicorn vista.app.main:app --port 8003
```

**Run manual tests:**
```bash
# Test patient at each site
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100001"]}'

curl -X POST 'http://localhost:8003/rpc/execute?site=500' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100010"]}'

curl -X POST 'http://localhost:8003/rpc/execute?site=630' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100013"]}'

# Test error conditions
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN999999"]}'  # Not found

curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -H 'Content-Type: application/json' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100013"]}'  # Not at this site
```

### Test Coverage

**Current coverage (Phase 1):**
- DataLoader: 13 tests (100% coverage)
- RPCRegistry: 19 tests (100% coverage)
- M-Serializer: 34 tests (100% coverage)
- Demographics Handler: 16 tests (100% coverage)

**Total: 82 tests, 100% pass rate**

---

## Operations Guide

### Running in Development

```bash
# With auto-reload (detects code changes)
python -m uvicorn vista.app.main:app --port 8003 --reload

# With custom log level
python -m uvicorn vista.app.main:app --port 8003 --log-level debug
```

### Running in Production

```bash
# With multiple workers (production)
python -m uvicorn vista.app.main:app --port 8003 --workers 4

# With Gunicorn
gunicorn vista.app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8003
```

### Monitoring

**Health check endpoint:**
```bash
curl http://localhost:8003/health
```

**Metrics to monitor:**
- Service uptime
- Sites initialized (should be 3)
- RPC execution success rate
- Response time per RPC

**Logging:**
```python
# Logs are written to stdout
# Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s

# Example log messages:
# INFO: Site 200 initialized: 1 RPCs, 2 patients
# INFO: RPC executed successfully: 200:ORWPT PTINQ
# ERROR: RPC execution error: 200:ORWPT PTINQ - Patient not found
```

### Configuration

**Port configuration:**
```python
# vista/app/main.py
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
```

**Site configuration:**
```python
# vista/app/main.py
SITES = {
    "200": {"name": "ALEXANDRIA", "sta3n": "200"},
    "500": {"name": "ANCHORAGE", "sta3n": "500"},
    "630": {"name": "PALO_ALTO", "sta3n": "630"},
}
```

**Patient registry location:**
```
mock/shared/patient_registry.json
```

### API Documentation

FastAPI provides automatic interactive documentation:

**Swagger UI:**
```
http://localhost:8003/docs
```

**ReDoc:**
```
http://localhost:8003/redoc
```

---

## Troubleshooting

### Service won't start

**Problem:** Port 8003 already in use

**Solution:**
```bash
# Find process using port 8003
lsof -i :8003

# Kill the process
kill -9 <PID>

# Or use a different port
python -m uvicorn vista.app.main:app --port 8004
```

---

### Patient registry not found

**Problem:** `FileNotFoundError: patient_registry.json`

**Solution:**
```bash
# Verify file exists
ls -la mock/shared/patient_registry.json

# Check you're running from project root
pwd  # Should be: /path/to/med-z1
```

---

### RPC returns error "-1^Patient not found"

**Problem:** Patient ICN doesn't exist in registry

**Solution:**
```bash
# Check which patients are in the registry
cat mock/shared/patient_registry.json | grep "icn"

# Use valid ICNs:
# - ICN100001 (sites 200, 500, 630)
# - ICN100010 (sites 200, 500)
# - ICN100013 (site 630)
```

---

### RPC returns "Patient not registered at site"

**Problem:** Patient exists but not at requested site

**Example:**
```bash
# ICN100013 only at site 630
curl -X POST 'http://localhost:8003/rpc/execute?site=200' \
  -d '{"name": "ORWPT PTINQ", "params": ["ICN100013"]}'
# Returns: "-1^Patient ICN100013 not registered at site 200"
```

**Solution:** Check `treating_facilities` in `patient_registry.json` to see which sites have this patient.

---

### Import errors

**Problem:** `ModuleNotFoundError: No module named 'vista'`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run from project root (not vista/ directory)
cd /path/to/med-z1
python -m uvicorn vista.app.main:app --port 8003
```

---

### Tests failing

**Problem:** Tests can't find `patient_registry.json`

**Solution:**
```bash
# Run tests from project root
cd /path/to/med-z1
python -m pytest vista/tests/ -v

# Don't run from vista/ directory
```

---

## Next Steps (Future Phases)

**Phase 2-5 Roadmap:**
- ✅ Phase 1: Single RPC (ORWPT PTINQ) - **COMPLETE**
- ⏳ Phase 2: Multi-site support enhancements
- ⏳ Phase 3: Demographics domain (3 RPCs total)
- ⏳ Phase 4: Vitals domain (GMV* RPCs)
- ⏳ Phase 5: Allergies & Medications domains
- ⏳ Phase 6: Med-z1 integration (VistaClient)

---

## References

**Design Document:**
- `docs/vista-rpc-broker-design.md` - Complete architecture and design decisions

**Related Documentation:**
- `app/README.md` - Med-z1 FastAPI application guide
- `mock/shared/patient_registry.json` - Patient ICN/DFN mappings
- `docs/implementation-roadmap.md` - Overall project roadmap

**External Resources:**
- VistA RPC Documentation: VA FileMan documentation
- FastAPI: https://fastapi.tiangolo.com/
- Uvicorn: https://www.uvicorn.org/

---

**Last Updated:** 2025-12-15
**Phase:** 1 (Complete)
**Version:** 1.0.0
