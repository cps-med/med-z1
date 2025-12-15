# VistA RPC Broker Simulator - Design Document

**Document Version:** v1.1
**Date:** 2025-12-14
**Status:** Draft - Refinements in Progress

## 1. Overview

### Purpose

The VistA RPC Broker Simulator (`vista` subsystem) provides a lightweight, FastAPI-based service that simulates the VA VistA Remote Procedure Call (RPC) interface. This enables the med-z1 application to develop and test client-side RPC calling logic, response parsing, and multi-site data aggregation without requiring access to real VistA systems.

**Critical Architectural Role**: The vista subsystem simulates **real-time data access (T-0)** from VistA sites, complementing the med-z1's historical data pipeline:

- **Historical Data (T-1 and earlier)**: Mock CDW → ETL → Medallion → PostgreSQL
  - Nightly batch updates, data through yesterday (T-1)
  - Fast, cached, always available

- **Real-Time Data (T-0, today)**: VistA RPC Broker → Med-z1 UI
  - Live queries to VistA sites via RPC
  - Current day data, fresh but slower (simulated 1-3 second latency)

This mirrors the real VA architecture where CDW is updated nightly (always at least 1 day behind) and real-time queries go directly to 140+ VistA sites via RPC.

### Goals

- **Multi-Site Simulation**: Support multiple VistA sites (stations) running concurrently within a single service instance
- **Authentic Format**: Return responses in VistA's native format (caret `^`, pipe `|`, semicolon `;` delimiters)
- **Clinical Domain Coverage**: Initially support four high-priority domains: Demographics, Vitals, Allergies, Medications
- **Temporal Data Separation**: Provide T-0 (today) and T-1 (yesterday) data to complement PostgreSQL's historical data (T-1 and earlier)
- **Realistic Latency**: Simulate VistA RPC call delays (configurable 1-3 seconds) to mimic real network/processing time
- **Simple Development**: Run on a single macOS laptop alongside existing med-z1 services (app on 8000, ccow on 8001)
- **Testability**: Enable med-z1 app developers to craft specific test scenarios with static, predictable data
- **Incremental Evolution**: Start simple (Level 1 fidelity), evolve as needed

### Non-Goals

- Full CCOW/VistA protocol compliance (we use HTTP, not raw TCP)
- VistA security keys, permissions, or menu systems (Level 3 fidelity)
- Connection to real VistA systems or real CDW
- PHI/PII handling (synthetic data only)
- Master Patient Index (MPI) service implementation (future enhancement; Phase 1 uses shared patient registry file)

---

## 2. Architecture Decisions

### 2.1 Dual-Source Data Architecture

**Decision**: Vista uses static JSON files for T-0/T-1 data; PostgreSQL serves T-1 and earlier data

**Architectural Pattern**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Med-z1 Data Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Historical Pipeline (T-1 and earlier):                         │
│  ┌──────────┐    ┌─────┐    ┌──────────┐    ┌──────────────┐    │
│  │ Mock CDW │ →  │ ETL │ →  │ Medallion│ →  │ PostgreSQL   │    │
│  │ (SQL)    │    └─────┘    │ (Parquet)│    │ (Serving DB) │    │
│  └──────────┘               └──────────┘    └──────────────┘    │
│  └─ Data through yesterday (T-1), nightly batch updates         │
│                                                                 │
│  Real-Time Pipeline (T-0, today):                               │
│  ┌──────────────────┐    ┌────────────────────────────┐         │
│  │ VistA RPC Broker │ →  │ Med-z1 UI (on-demand)      │         │
│  │ (JSON files)     │    │ "Refresh from VistA" button│         │
│  └──────────────────┘    └────────────────────────────┘         │
│  └─ Current day data (T-0), live queries with 1-3s latency      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Rationale**:
- **Temporal Separation**: Mirrors real VA architecture where CDW is always T-1 (nightly updates) and VistA provides T-0 (real-time)
- **Realistic Testing**: Med-z1 developers can test both data sources and the boundary between them
- **Performance Trade-offs**: PostgreSQL is fast (cached, indexed) but stale; VistA is fresh but slower (network latency)
- **Independence**: Vista instances are fully independent and self-contained (no database dependencies)
- **Simplified Data Models**: VistA data models are fundamentally different from CDW (M-based vs. relational); JSON easier to manage

**Data Overlap**: Vista provides both T-0 (today) and T-1 (yesterday) data to enable testing of the temporal boundary. Med-z1 can choose to prefer Vista's T-1 data (fresher) over PostgreSQL's T-1 data (batch-updated overnight).

**Patient Consistency**: Same patients (same ICNs) exist in both Mock CDW and Vista, maintained via shared patient registry file (see Section 2.7).

### 2.2 Multi-Site Deployment

**Decision**: Single FastAPI service with site-as-parameter + base class pattern

**Architecture**:
```python
# Conceptual design
class VistaServer:
    """Represents one VistA site (e.g., Alexandria 200, Anchorage 500)"""
    def __init__(self, sta3n: str, name: str, data_path: str):
        self.sta3n = sta3n
        self.name = name
        self.data = load_site_data(data_path)

    async def execute_rpc(self, rpc_name: str, params: list) -> str:
        """Execute an RPC against this site's data"""
        pass

# Single service manages multiple VistaServer instances
vista_cluster = {
    "200": VistaServer("200", "ALEXANDRIA", "vista/data/sites/200/"),
    "500": VistaServer("500", "ANCHORAGE", "vista/data/sites/500/"),
    "630": VistaServer("630", "PALO_ALTO", "vista/data/sites/630/"),
}

@app.post("/rpc/execute")
async def execute_rpc(site: str, request: RpcRequest):
    server = vista_cluster.get(site)
    response = await server.execute_rpc(request.name, request.params)
    return {"response": response}
```

**Rationale**:
- ✅ Single service on port 8003 (easy to run on laptop)
- ✅ Realistic multi-site simulation (each site has independent data)
- ✅ Base class pattern enables per-site customization if needed
- ✅ Site parameter in API makes intent explicit
- ✅ Simple to add/remove sites without code changes (config-driven)

**API Design**: Site number passed as query parameter:
```
POST http://localhost:8003/rpc/execute?site=200
Content-Type: application/json

{
  "name": "ORWPT PTINQ",
  "params": ["1012853550V207686"]
}
```

### 2.3 RPC Implementation Priority

**Phase 1 - High Priority Domains** (4 domains, ~12-15 RPCs):

1. **Demographics** (ORWPT namespace)
   - `ORWPT SELECT` - Select patient by ICN/DFN
   - `ORWPT PTINQ` - Patient inquiry (demographics)
   - `ORWPT ID INFO` - Patient identifiers (SSN, ICN, DFN)

2. **Vitals** (GMV namespace)
   - `GMV EXTRACT REC` - Extract vital measurements
   - `GMV LATEST VM` - Get latest vitals
   - `GMV MANAGER` - Vitals list with date range

3. **Allergies** (ORQQAL namespace)
   - `ORQQAL LIST` - Get patient allergy list
   - `ORQQAL DETAIL` - Get allergy detail (reactions, severity)
   - `ORQQAL ALLERGY MATCH` - Match allergy by name

4. **Medications** (ORWPS namespace)
   - `ORWPS COVER` - Active outpatient medications (cover sheet)
   - `ORWPS DETAIL` - Medication detail
   - `ORWPS ACTIVE` - Active medications list
   - `PSO SUPPLY` - Pharmacy supply data

**Phase 2 - Medium Priority** (future):
- Patient Flags (DGPF namespace)
- Encounters (ORWCV namespace)

**Phase 3 - Lower Priority** (future):
- Labs, Problems, Orders, Notes, Imaging

### 2.4 Response Fidelity

**Decision**: Level 1 - Data Format Only

**Characteristics**:
- ✅ Correct delimiters (caret `^`, pipe `|`, semicolon `;`)
- ✅ Correct field structure and ordering per ICD documentation
- ✅ Clean, predictable, well-formed responses
- ✅ Basic error handling (e.g., patient not found, invalid RPC)
- ❌ No VistA quirks, edge cases, or inconsistencies (unless needed for specific testing)
- ❌ No security keys, permissions, or context management

**Upgrade Path**: Can evolve to Level 2 (realistic quirks) if med-z1 needs to handle VistA edge cases.

### 2.5 Configuration Strategy

**Decision**: Vista-specific JSON configuration files

**Structure**:
```
vista/
  config/
    sites.json           # Site registry (sta3n, name, ports, metadata)
    rpc_registry.json    # RPC definitions (optional, for validation)
  data/
    sites/
      200/               # Alexandria site data
        patients.json
        vitals.json
        allergies.json
        medications.json
      500/               # Anchorage site data
        patients.json
        vitals.json
        allergies.json
        medications.json
```

**sites.json Example**:
```json
{
  "sites": [
    {
      "sta3n": "200",
      "name": "ALEXANDRIA",
      "full_name": "Alexandria VA Medical Center",
      "state": "VA",
      "enabled": true
    },
    {
      "sta3n": "500",
      "name": "ANCHORAGE",
      "full_name": "Alaska VA Healthcare System",
      "state": "AK",
      "enabled": true
    },
    {
      "sta3n": "630",
      "name": "PALO_ALTO",
      "full_name": "VA Palo Alto Health Care System",
      "state": "CA",
      "enabled": true
    }
  ]
}
```

**Root config.py Extension** (minimal):
```python
# config.py (root)
VISTA_SERVICE_URL = os.getenv("VISTA_SERVICE_URL", "http://localhost:8003")
VISTA_SERVICE_ENABLED = os.getenv("VISTA_SERVICE_ENABLED", "true").lower() == "true"
```

### 2.6 Integration Pattern

**Decision**: Vista client abstraction layer in med-z1 app

**Location**: `app/services/vista_client.py`

**Example Usage**:
```python
# In app/routes/patient.py
from app.services.vista_client import VistaClient

vista = VistaClient()

@router.get("/patient/{patient_icn}/vista-demographics")
async def get_vista_demographics(patient_icn: str):
    """Fetch demographics from all VistA sites for this patient"""

    # Call multiple sites in parallel
    sites = ["200", "500", "630"]
    results = await vista.call_rpc_multi_site(
        sites=sites,
        rpc_name="ORWPT PTINQ",
        params=[patient_icn]
    )

    # Parse and merge responses
    demographics = []
    for site, response in results.items():
        if response.success:
            parsed = vista.parse_ptinq_response(response.data)
            demographics.append({"site": site, "data": parsed})

    return {"patient_icn": patient_icn, "demographics": demographics}
```

**Vista Client API**:
```python
class VistaClient:
    async def call_rpc(self, site: str, rpc_name: str, params: list) -> VistaResponse
    async def call_rpc_multi_site(self, sites: list[str], rpc_name: str, params: list) -> dict
    def parse_ptinq_response(self, raw: str) -> dict
    def parse_vitals_response(self, raw: str) -> dict
    # ... domain-specific parsers
```

### 2.7 Master Patient Index (MPI) Simulation

**Decision**: Shared patient registry file for patient identity consistency

**Background**: The VA uses a Master Patient Index (MPI) to maintain patient identity across 140+ VistA sites. The MPI provides:
- Authoritative patient identifiers (ICN, SSN, DFN per site)
- List of sites where patient has been seen ("treating facilities")
- Identity resolution across sites (same patient, different DFNs)

**Phase 1 Approach**: Simplified shared registry file (`mock/shared/patient_registry.json`)

**Structure**:
```
mock/
  shared/
    patient_registry.json   # Master patient list (ICN, demographics, site list)

mock/sql-server/cdwwork/
  insert/                   # SQL inserts reference patient_registry.json

vista/data/sites/
  200/patients.json         # References patient_registry.json
  500/patients.json         # References patient_registry.json
  630/patients.json         # References patient_registry.json
```

**patient_registry.json Example**:
```json
{
  "patients": [
    {
      "icn": "1012853550V207686",
      "ssn": "666-12-1234",
      "name_last": "SMITH",
      "name_first": "JOHN",
      "name_middle": "Q",
      "dob": "1945-03-15",
      "sex": "M",
      "treating_facilities": [
        {"sta3n": "200", "dfn": "100001", "first_seen": "2020-01-15"},
        {"sta3n": "500", "dfn": "500234", "first_seen": "2022-06-20"},
        {"sta3n": "630", "dfn": "630789", "first_seen": "2023-03-10"}
      ]
    },
    {
      "icn": "1008714701V416111",
      "ssn": "666-23-4567",
      "name_last": "JOHNSON",
      "name_first": "MARY",
      "name_middle": "A",
      "dob": "1967-08-22",
      "sex": "F",
      "treating_facilities": [
        {"sta3n": "200", "dfn": "100002", "first_seen": "2018-05-10"},
        {"sta3n": "500", "dfn": "500567", "first_seen": "2021-11-03"}
      ]
    }
  ]
}
```

**Benefits**:
- ✅ Single source of truth for patient identity
- ✅ Consistent ICNs across Mock CDW and Vista
- ✅ Enables future MPI service implementation
- ✅ Documents which sites each patient has visited

**Usage**:
- Mock CDW SQL insert scripts read from this file to populate `SPatient.SPatient` table
- Vista data files reference this for patient demographics
- Future MPI service can expose this via API (`GET /mpi/patient/{icn}`)

**Future Enhancement**: Implement full MPI service (`mpi/` subsystem) that:
- Exposes REST API for patient lookups
- Returns list of treating facilities for query optimization (Section 2.6 Option B)
- Handles identity resolution (merged ICNs, duplicate records)

### 2.8 Temporal Data Strategy (T-0, T-1, T-2 Date Format)

**Decision**: Vista data files use relative date notation (T-0, T-1, T-2, etc.)

**Rationale**:
- Data always appears "fresh" relative to current date
- No manual updates required to keep data current
- Enables testing of temporal boundary (CDW vs Vista data source selection)
- Realistic simulation of "today's data" vs "yesterday's data"

**Date Notation**:
- `T-0` = Today (current date)
- `T-1` = Yesterday (1 day ago)
- `T-2` = 2 days ago
- `T-7` = 1 week ago
- `T-30` = 1 month ago

**Time Specification**:
- `T-0@09:30` = Today at 09:30
- `T-1@14:15` = Yesterday at 14:15
- `T-0@now` = Current timestamp

**Vista Data Coverage**:
- **Primary Focus**: T-0 (today) data
- **Overlap Period**: T-1 (yesterday) data for boundary testing
- **Optional**: T-2 to T-7 for richer test scenarios

**Example (vitals.json)**:
```json
{
  "vitals": [
    {
      "icn": "1012853550V207686",
      "measurements": [
        {
          "date_time": "T-0@09:30",
          "type": "BLOOD PRESSURE",
          "value": "120/80",
          "units": "mm[Hg]"
        },
        {
          "date_time": "T-0@14:15",
          "type": "BLOOD PRESSURE",
          "value": "118/76",
          "units": "mm[Hg]"
        },
        {
          "date_time": "T-1@10:00",
          "type": "BLOOD PRESSURE",
          "value": "122/82",
          "units": "mm[Hg]"
        }
      ]
    }
  ]
}
```

**Implementation**: Vista service parses T-N notation at runtime, converting to actual dates/FileMan format before returning RPC responses.

**Conversion Logic** (`vista/app/utils/temporal.py`):
```python
from datetime import datetime, timedelta
import re

def parse_relative_date(relative_str: str) -> datetime:
    """Parse T-N@HH:MM format to absolute datetime"""
    # Example: "T-0@09:30" or "T-1@14:15"
    match = re.match(r'T-(\d+)@([\d:]+|now)', relative_str)
    if not match:
        raise ValueError(f"Invalid relative date format: {relative_str}")

    days_offset = int(match.group(1))
    time_str = match.group(2)

    target_date = datetime.now().date() - timedelta(days=days_offset)

    if time_str == "now":
        return datetime.now()
    else:
        hour, minute = map(int, time_str.split(':'))
        return datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
```

### 2.9 Simulated Network Latency

**Decision**: Configurable artificial delay (1-3 seconds) for all RPC calls

**Rationale**:
- Real VistA RPC calls have network latency, database query time, and M-code execution time
- Typical real-world RPC response time: 1-5 seconds (varies by RPC complexity and network conditions)
- Med-z1 UI should handle async loading states, spinners, and timeouts
- Enables testing of concurrent multi-site queries (3 sites × 2 seconds = observable delay)

**Configuration**:
```python
# vista/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Simulated latency (seconds)
    rpc_latency_min: float = 1.0   # Minimum delay
    rpc_latency_max: float = 3.0   # Maximum delay
    rpc_latency_enabled: bool = True  # Toggle for testing

    class Config:
        env_file = ".env"

settings = Settings()
```

**Environment Variables** (root `.env`):
```bash
# Vista RPC Broker Configuration
VISTA_RPC_LATENCY_MIN=1.0
VISTA_RPC_LATENCY_MAX=3.0
VISTA_RPC_LATENCY_ENABLED=true
```

**Implementation** (`vista/app/services/vista_server.py`):
```python
import asyncio
import random
from app.config import settings

class VistaServer:
    async def execute_rpc(self, rpc_name: str, params: list) -> str:
        # Simulate network/processing latency
        if settings.rpc_latency_enabled:
            delay = random.uniform(settings.rpc_latency_min, settings.rpc_latency_max)
            await asyncio.sleep(delay)

        # Execute RPC logic
        response = await self.dispatcher.dispatch(rpc_name, params)
        return response
```

**Med-z1 UI Integration**: Add loading spinner and "Fetching real-time data from VistA..." indicator (see Section 2.10).

**Testing**: Set `VISTA_RPC_LATENCY_ENABLED=false` to disable delay for unit tests.

### 2.10 UI/UX Integration Pattern (Hybrid Approach)

**Decision**: Show PostgreSQL data by default with "Refresh from VistA" button for real-time updates

**User Experience Flow**:

1. **Initial Page Load** (Fast, <1 second):
   ```
   Patient: SMITH, JOHN (ICN: 1012853550V207686)

   Vitals (Last 7 Days)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Data current through: Dec 13, 2025 (yesterday)

   [Refresh from VistA] button

   Blood Pressure:
   Dec 7:  120/80
   Dec 8:  118/76
   Dec 9:  122/82
   ...
   Dec 13: 120/78
   ```

2. **User Clicks "Refresh from VistA"** (Processing indicator appears):
   ```
   Vitals (Last 7 Days)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🔄 Fetching real-time data from VistA sites...

   [Processing spinner]
   ```

3. **After 1-3 seconds** (Real-time data merged):
   ```
   Vitals (Last 7 Days)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Data current through: Dec 14, 2025 (today, real-time)
   Last updated: 2:34 PM

   [Refresh from VistA] button (enabled again)

   Blood Pressure:
   Dec 7:  120/80           (CDW)
   Dec 8:  118/76           (CDW)
   ...
   Dec 13: 120/78           (CDW)
   Dec 14: 118/74 ← NEW    (VistA Site 200, today 9:30 AM)
   Dec 14: 122/80 ← NEW    (VistA Site 200, today 2:15 PM)
   ```

**Implementation Notes**:
- **No automatic real-time fetching**: Avoids slow page loads, gives user control
- **Data source hidden**: UI doesn't explicitly show "CDW" vs "VistA" labels (per Section 2.7 preference)
- **Freshness indicator**: "Data current through: [date]" and "Last updated: [time]"
- **Processing feedback**: Spinner + status message during VistA queries
- **Error handling**: If VistA call fails, show "Unable to fetch real-time data" with option to retry

**HTMX Implementation Example** (`app/templates/patient/vitals.html`):
```html
<div id="vitals-container">
  <h3>Vitals (Last 7 Days)</h3>
  <p class="data-freshness">Data current through: {{ data_current_through }}</p>

  <button
    hx-get="/patient/{{ patient_icn }}/vitals-realtime"
    hx-target="#vitals-container"
    hx-swap="outerHTML"
    hx-indicator="#vitals-spinner"
    class="btn-refresh">
    Refresh from VistA
  </button>

  <div id="vitals-spinner" class="htmx-indicator">
    🔄 Fetching real-time data from VistA sites...
  </div>

  <!-- Vitals table/chart -->
</div>
```

**Backend Route** (`app/routes/patient.py`):
```python
@router.get("/patient/{patient_icn}/vitals-realtime")
async def get_vitals_realtime(patient_icn: str):
    # Fetch historical from PostgreSQL (T-7 to T-2)
    historical = await db.get_vitals(patient_icn, days=7, exclude_today=True)

    # Fetch real-time from VistA (T-0, today)
    vista = VistaClient()
    vista_results = await vista.call_rpc_multi_site(
        sites=["200", "500", "630"],
        rpc_name="GMV LATEST VM",
        params=[patient_icn, "1"]  # Get today's vitals only
    )

    # Parse and merge
    today_vitals = []
    for site, response in vista_results.items():
        if response.success:
            parsed = vista.parse_vitals_response(response.data)
            today_vitals.extend(parsed)

    # Combine historical + today
    all_vitals = historical + today_vitals

    return templates.TemplateResponse("patient/vitals.html", {
        "request": request,
        "patient_icn": patient_icn,
        "vitals": all_vitals,
        "data_current_through": datetime.now().strftime("%b %d, %Y"),
        "last_updated": datetime.now().strftime("%I:%M %p")
    })
```

---

## 3. System Architecture

### 3.1 Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     med-z1 Application (Port 8000)               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐      │
│  │  app/services/vista_client.py                          │      │
│  │  ┌──────────────────────────────────────────────────┐  │      │
│  │  │ VistaClient                                      │  │      │
│  │  │  - call_rpc(site, rpc_name, params)              │  │      │
│  │  │  - call_rpc_multi_site(sites, rpc_name, params)  │  │      │
│  │  │  - parse_*_response() parsers                    │  │      │
│  │  └──────────────────────────────────────────────────┘  │      │
│  └────────────────────────────────────────────────────────┘      │
│                          │                                       │
│                          │ HTTP POST /rpc/execute?site=200       │
│                          │ {"name": "ORWPT PTINQ", "params": ...}│
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│             VistA RPC Broker Simulator (Port 8003)              │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  FastAPI Application (vista/app/main.py)               │     │
│  │                                                        │     │
│  │  POST /rpc/execute?site={sta3n}                        │     │
│  │  GET  /sites (list available sites)                    │     │
│  │  GET  /health                                          │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  VistaCluster (vista/app/services/cluster.py)          │     │
│  │                                                        │     │
│  │  vista_servers = {                                     │     │
│  │    "200": VistaServer("200", "ALEXANDRIA", ...),       │     │
│  │    "500": VistaServer("500", "ANCHORAGE", ...),        │     │
│  │    "630": VistaServer("630", "PALO_ALTO", ...),        │     │
│  │  }                                                     │     │
│  │                                                        │     │
│  │  def get_server(site: str) -> VistaServer              │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  VistaServer (vista/app/services/vista_server.py)      │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │ Base class representing one VistA site           │  │     │
│  │  │                                                  │  │     │
│  │  │ Properties:                                      │  │     │
│  │  │  - sta3n: str                                    │  │     │
│  │  │  - name: str                                     │  │     │
│  │  │  - data_loader: DataLoader                       │  │     │
│  │  │  - rpc_dispatcher: RpcDispatcher                 │  │     │
│  │  │                                                  │  │     │
│  │  │ Methods:                                         │  │     │
│  │  │  - async execute_rpc(name, params) -> str        │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  RpcDispatcher (vista/app/services/dispatcher.py)      │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │ Routes RPC calls to domain handlers              │  │     │
│  │  │                                                  │  │     │
│  │  │ RPC_REGISTRY = {                                 │  │     │
│  │  │   "ORWPT PTINQ": demographics.ptinq,             │  │     │
│  │  │   "GMV LATEST VM": vitals.latest_vm,             │  │     │
│  │  │   "ORQQAL LIST": allergies.list_allergies,       │  │     │
│  │  │   "ORWPS COVER": medications.cover_sheet,        │  │     │
│  │  │ }                                                │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Domain Handlers (vista/app/handlers/)                 │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │ demographics.py  - ORWPT* RPCs                   │  │     │
│  │  │ vitals.py        - GMV* RPCs                     │  │     │
│  │  │ allergies.py     - ORQQAL* RPCs                  │  │     │
│  │  │ medications.py   - ORWPS*, PSO* RPCs             │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  DataLoader (vista/app/services/data_loader.py)        │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │ Loads JSON data for a specific site              │  │     │
│  │  │                                                  │  │     │
│  │  │ Methods:                                         │  │     │
│  │  │  - get_patient(icn) -> dict                      │  │     │
│  │  │  - get_vitals(icn, date_range) -> list           │  │     │
│  │  │  - get_allergies(icn) -> list                    │  │     │
│  │  │  - get_medications(icn) -> list                  │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  M-Serializer (vista/app/utils/m_serializer.py)        │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │ Converts Python data -> VistA format             │  │     │
│  │  │                                                  │  │     │
│  │  │ Functions:                                       │  │     │
│  │  │  - pack_vista_response(parts, delim="^")         │  │     │
│  │  │  - pack_list_response(items, field_maps)         │  │     │
│  │  │  - format_rpc_error(message, code="-1")          │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Data Files (vista/data/sites/{sta3n}/*.json)           │    │
│  │                                                         │    │
│  │  200/                                                   │    │
│  │    patients.json      [{"icn": "...", "name": ...}]     │    │
│  │    vitals.json        [{"icn": "...", "date": ...}]     │    │
│  │    allergies.json     [{"icn": "...", "allergen": ...}] │    │
│  │    medications.json   [{"icn": "...", "drug": ...}]     │    │
│  │                                                         │    │
│  │  500/ ... (same structure)                              │    │
│  │  630/ ... (same structure)                              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Request Flow

**Example: Fetch patient demographics from site 200**

1. **med-z1 app** receives request for patient ICN `1012853550V207686`
2. **VistaClient** calls `call_rpc("200", "ORWPT PTINQ", ["1012853550V207686"])`
3. **HTTP POST** to `http://localhost:8003/rpc/execute?site=200`
4. **FastAPI main.py** receives request, extracts `site=200`
5. **VistaCluster** looks up `VistaServer` instance for site 200
6. **VistaServer.execute_rpc()** called with `"ORWPT PTINQ"` and params
7. **RpcDispatcher** routes to `demographics.ptinq()` handler
8. **Handler** calls `data_loader.get_patient("1012853550V207686")`
9. **DataLoader** reads `vista/data/sites/200/patients.json`
10. **Handler** formats patient data as Python dict
11. **M-Serializer** converts dict to VistA string: `"SMITH,JOHN^1012853550V207686^19450315^M^..."`
12. **VistaServer** returns formatted string
13. **FastAPI** returns `{"response": "SMITH,JOHN^1012853550V207686^..."}`
14. **VistaClient** receives response, parses with `parse_ptinq_response()`
15. **med-z1 app** receives structured Python dict, renders in UI

---

## 4. Directory Structure

```
vista/
├── __init__.py
├── README.md                      # Vista subsystem documentation
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Vista service configuration (latency, site loading)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── rpc_request.py         # Pydantic models for API
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cluster.py             # VistaCluster (manages multiple VistaServer instances)
│   │   ├── vista_server.py        # VistaServer base class (one per site)
│   │   ├── dispatcher.py          # RpcDispatcher (routes RPC calls to handlers)
│   │   └── data_loader.py         # DataLoader (reads JSON data for a site)
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── demographics.py        # ORWPT* RPCs
│   │   ├── vitals.py              # GMV* RPCs
│   │   ├── allergies.py           # ORQQAL* RPCs
│   │   └── medications.py         # ORWPS*, PSO* RPCs
│   │
│   └── utils/
│       ├── __init__.py
│       ├── m_serializer.py        # VistA format serialization (^ | ;)
│       ├── temporal.py            # T-0/T-1 date parsing and FileMan conversion
│       └── vista_datetime.py      # FileMan date/time utilities
│
├── config/
│   ├── sites.json                 # Site registry (sta3n, names, metadata)
│   └── rpc_registry.json          # (Optional) RPC definitions for validation
│
├── data/
│   └── sites/
│       ├── 200/                   # Alexandria
│       │   ├── patients.json
│       │   ├── vitals.json
│       │   ├── allergies.json
│       │   └── medications.json
│       │
│       ├── 500/                   # Anchorage
│       │   ├── patients.json
│       │   ├── vitals.json
│       │   ├── allergies.json
│       │   └── medications.json
│       │
│       └── 630/                   # Palo Alto
│           ├── patients.json
│           ├── vitals.json
│           ├── allergies.json
│           └── medications.json
│
└── tests/
    ├── __init__.py
    ├── test_rpc_dispatcher.py
    ├── test_demographics.py
    ├── test_vitals.py
    └── test_m_serializer.py
```

---

## 5. Data Models

### 5.1 Configuration Files

**vista/config/sites.json**:
```json
{
  "sites": [
    {
      "sta3n": "200",
      "name": "ALEXANDRIA",
      "full_name": "Alexandria VA Medical Center",
      "state": "VA",
      "enabled": true
    },
    {
      "sta3n": "500",
      "name": "ANCHORAGE",
      "full_name": "Alaska VA Healthcare System",
      "state": "AK",
      "enabled": true
    },
    {
      "sta3n": "630",
      "name": "PALO_ALTO",
      "full_name": "VA Palo Alto Health Care System",
      "state": "CA",
      "enabled": true
    }
  ]
}
```

### 5.2 Patient Data Files

**vista/data/sites/200/patients.json**:
```json
{
  "patients": [
    {
      "icn": "1012853550V207686",
      "dfn": "100001",
      "ssn": "666-12-1234",
      "name_last": "SMITH",
      "name_first": "JOHN",
      "name_middle": "Q",
      "dob": "1945-03-15",
      "sex": "M",
      "veteran_yn": "Y",
      "sc_percent": "50",
      "address_street": "123 Main St",
      "address_city": "Alexandria",
      "address_state": "VA",
      "address_zip": "22314",
      "phone_home": "703-555-1234"
    }
  ]
}
```

**vista/data/sites/200/vitals.json** (using T-0/T-1 relative date notation):
```json
{
  "vitals": [
    {
      "icn": "1012853550V207686",
      "dfn": "100001",
      "measurements": [
        {
          "date_time": "T-0@09:30",
          "type": "BLOOD PRESSURE",
          "value": "120/80",
          "units": "mm[Hg]",
          "location": "PRIMARY CARE CLINIC",
          "entered_by": "NURSE,JANE"
        },
        {
          "date_time": "T-0@14:15",
          "type": "BLOOD PRESSURE",
          "value": "118/76",
          "units": "mm[Hg]",
          "location": "PRIMARY CARE CLINIC",
          "entered_by": "NURSE,JANE"
        },
        {
          "date_time": "T-1@10:00",
          "type": "BLOOD PRESSURE",
          "value": "122/82",
          "units": "mm[Hg]",
          "location": "PRIMARY CARE CLINIC",
          "entered_by": "NURSE,JANE"
        },
        {
          "date_time": "T-0@09:30",
          "type": "PULSE",
          "value": "72",
          "units": "/min",
          "location": "PRIMARY CARE CLINIC",
          "entered_by": "NURSE,JANE"
        },
        {
          "date_time": "T-0@09:30",
          "type": "TEMPERATURE",
          "value": "98.6",
          "units": "F",
          "location": "PRIMARY CARE CLINIC",
          "entered_by": "NURSE,JANE"
        }
      ]
    }
  ]
}
```

**Note**: Date_time uses relative notation (see Section 2.8). Vista service converts T-0/T-1 to actual dates/FileMan format at runtime.

**vista/data/sites/200/allergies.json**:
```json
{
  "allergies": [
    {
      "icn": "1012853550V207686",
      "dfn": "100001",
      "allergy_list": [
        {
          "allergen": "PENICILLIN",
          "allergen_type": "DRUG",
          "reaction": "HIVES",
          "severity": "MODERATE",
          "verified": "Y",
          "verified_date": "2020-01-15",
          "origination_date": "2020-01-15",
          "originator": "PROVIDER,JANE"
        },
        {
          "allergen": "PEANUTS",
          "allergen_type": "FOOD",
          "reaction": "ANAPHYLAXIS",
          "severity": "SEVERE",
          "verified": "Y",
          "verified_date": "2019-05-20",
          "origination_date": "2019-05-20",
          "originator": "PROVIDER,JOHN"
        }
      ]
    }
  ]
}
```

**vista/data/sites/200/medications.json**:
```json
{
  "medications": [
    {
      "icn": "1012853550V207686",
      "dfn": "100001",
      "active_meds": [
        {
          "rx_number": "2860066",
          "drug_name": "LISINOPRIL 10MG TAB",
          "status": "ACTIVE",
          "last_fill_date": "2024-11-15",
          "qty_remaining": "60",
          "qty_total": "90",
          "refills_remaining": "3",
          "expires": "2025-11-15",
          "sig": "TAKE ONE TABLET BY MOUTH DAILY",
          "provider": "PROVIDER,JANE",
          "pharmacy": "ALEXANDRIA VAMC PHARMACY"
        },
        {
          "rx_number": "2860067",
          "drug_name": "METFORMIN 500MG TAB",
          "status": "ACTIVE",
          "last_fill_date": "2024-11-15",
          "qty_remaining": "120",
          "qty_total": "180",
          "refills_remaining": "5",
          "expires": "2025-11-15",
          "sig": "TAKE ONE TABLET BY MOUTH TWICE DAILY WITH MEALS",
          "provider": "PROVIDER,JANE",
          "pharmacy": "ALEXANDRIA VAMC PHARMACY"
        }
      ]
    }
  ]
}
```

---

## 6. RPC Registry (Phase 1 - High Priority)

### 6.1 Demographics (ORWPT Namespace)

| RPC Name | Purpose | Parameters | Response Format |
|----------|---------|------------|-----------------|
| `ORWPT SELECT` | Select patient context | `[ICN or DFN]` | `DFN^NAME^SSN^DOB` |
| `ORWPT PTINQ` | Patient inquiry (demographics) | `[DFN]` | `NAME^ICN^DOB^SEX^SSN^ADDR^...` |
| `ORWPT ID INFO` | Patient identifiers | `[DFN]` | `SSN^ICN^DFN` |

**Example Response (ORWPT PTINQ)**:
```
SMITH,JOHN Q^1012853550V207686^19450315^M^666-12-1234^123 Main St^Alexandria^VA^22314^703-555-1234
```

### 6.2 Vitals (GMV Namespace)

| RPC Name | Purpose | Parameters | Response Format |
|----------|---------|------------|-----------------|
| `GMV LATEST VM` | Get latest vitals for patient | `[DFN, NUM_RESULTS]` | Multi-line: `TYPE^VALUE^UNITS^DATE` |
| `GMV EXTRACT REC` | Extract vitals for date range | `[DFN, START_DATE, END_DATE]` | Multi-line vitals |
| `GMV MANAGER` | Vitals list with metadata | `[DFN]` | Structured list with headers |

**Example Response (GMV LATEST VM)**:
```
BLOOD PRESSURE^120/80^mm[Hg]^3241201.0930^NURSE,JANE
PULSE^72^/min^3241201.0930^NURSE,JANE
TEMPERATURE^98.6^F^3241201.0930^NURSE,JANE
```

### 6.3 Allergies (ORQQAL Namespace)

| RPC Name | Purpose | Parameters | Response Format |
|----------|---------|------------|-----------------|
| `ORQQAL LIST` | Get patient allergy list | `[DFN]` | Multi-line: `ALLERGEN^TYPE^REACTIONS^SEVERITY` |
| `ORQQAL DETAIL` | Get allergy detail | `[DFN, ALLERGY_ID]` | Detailed allergy info |
| `ORQQAL ALLERGY MATCH` | Match allergy by name | `[SEARCH_STRING]` | List of matching allergens |

**Example Response (ORQQAL LIST)**:
```
PENICILLIN^DRUG^HIVES^MODERATE^VERIFIED
PEANUTS^FOOD^ANAPHYLAXIS^SEVERE^VERIFIED
```

### 6.4 Medications (ORWPS, PSO Namespaces)

| RPC Name | Purpose | Parameters | Response Format |
|----------|---------|------------|-----------------|
| `ORWPS COVER` | Active outpatient meds (cover sheet) | `[DFN]` | Multi-line: `RX^DRUG^STATUS^QTY^REFILLS` |
| `ORWPS DETAIL` | Medication detail | `[DFN, RX_NUMBER]` | Detailed med info with SIG |
| `ORWPS ACTIVE` | Active medications list | `[DFN]` | Active meds with dates |
| `PSO SUPPLY` | Pharmacy supply data | `[DFN, RX_NUMBER]` | Supply/refill details |

**Example Response (ORWPS COVER)**:
```
2860066^LISINOPRIL 10MG TAB^ACTIVE^60/90^3^2024-11-15^2025-11-15
2860067^METFORMIN 500MG TAB^ACTIVE^120/180^5^2024-11-15^2025-11-15
```

---

## 7. API Design

### 7.1 Vista Service Endpoints

**Base URL**: `http://localhost:8003`

#### Execute RPC
```
POST /rpc/execute?site={sta3n}
Content-Type: application/json

Request Body:
{
  "name": "ORWPT PTINQ",
  "params": ["100001"]
}

Response (200 OK):
{
  "site": "200",
  "rpc": "ORWPT PTINQ",
  "response": "SMITH,JOHN Q^1012853550V207686^19450315^M^666-12-1234^...",
  "timestamp": "2025-12-14T10:30:00Z"
}

Response (404 Not Found - Invalid Site):
{
  "detail": "Site 999 not found. Available sites: 200, 500, 630"
}

Response (400 Bad Request - Invalid RPC):
{
  "detail": "RPC 'INVALID RPC' not registered"
}
```

#### List Sites
```
GET /sites

Response (200 OK):
{
  "sites": [
    {
      "sta3n": "200",
      "name": "ALEXANDRIA",
      "full_name": "Alexandria VA Medical Center",
      "state": "VA",
      "enabled": true
    },
    {
      "sta3n": "500",
      "name": "ANCHORAGE",
      "full_name": "Alaska VA Healthcare System",
      "state": "AK",
      "enabled": true
    }
  ]
}
```

#### Health Check
```
GET /health

Response (200 OK):
{
  "status": "healthy",
  "service": "vista-rpc-broker",
  "version": "0.1.0",
  "sites_loaded": 3,
  "rpcs_registered": 15
}
```

### 7.2 Med-z1 Integration (VistaClient)

**Location**: `app/services/vista_client.py`

```python
from typing import List, Dict, Optional
import httpx
from pydantic import BaseModel
from config import VISTA_SERVICE_URL


class VistaResponse(BaseModel):
    """Parsed response from VistA RPC call"""
    success: bool
    site: str
    rpc: str
    data: str  # Raw VistA-formatted response
    error: Optional[str] = None


class VistaClient:
    """Client for calling VistA RPC Broker simulator"""

    def __init__(self, base_url: str = VISTA_SERVICE_URL):
        self.base_url = base_url
        self.timeout = 10.0

    async def call_rpc(
        self,
        site: str,
        rpc_name: str,
        params: List[str]
    ) -> VistaResponse:
        """Call a single RPC at one site"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/rpc/execute",
                    params={"site": site},
                    json={"name": rpc_name, "params": params}
                )
                response.raise_for_status()
                data = response.json()
                return VistaResponse(
                    success=True,
                    site=site,
                    rpc=rpc_name,
                    data=data["response"]
                )
            except Exception as e:
                return VistaResponse(
                    success=False,
                    site=site,
                    rpc=rpc_name,
                    data="",
                    error=str(e)
                )

    async def call_rpc_multi_site(
        self,
        sites: List[str],
        rpc_name: str,
        params: List[str]
    ) -> Dict[str, VistaResponse]:
        """Call same RPC at multiple sites in parallel"""
        import asyncio

        tasks = [
            self.call_rpc(site, rpc_name, params)
            for site in sites
        ]
        results = await asyncio.gather(*tasks)
        return {r.site: r for r in results}

    # Domain-specific parsers

    def parse_ptinq_response(self, raw: str) -> Dict:
        """Parse ORWPT PTINQ response"""
        parts = raw.split("^")
        if len(parts) < 9:
            return {}
        return {
            "name": parts[0],
            "icn": parts[1],
            "dob": parts[2],
            "sex": parts[3],
            "ssn": parts[4],
            "address_street": parts[5],
            "address_city": parts[6],
            "address_state": parts[7],
            "address_zip": parts[8],
        }

    def parse_vitals_response(self, raw: str) -> List[Dict]:
        """Parse GMV LATEST VM response (multi-line)"""
        vitals = []
        for line in raw.strip().split("\n"):
            parts = line.split("^")
            if len(parts) >= 4:
                vitals.append({
                    "type": parts[0],
                    "value": parts[1],
                    "units": parts[2],
                    "date_time": parts[3],
                    "entered_by": parts[4] if len(parts) > 4 else ""
                })
        return vitals

    def parse_allergies_response(self, raw: str) -> List[Dict]:
        """Parse ORQQAL LIST response (multi-line)"""
        allergies = []
        for line in raw.strip().split("\n"):
            parts = line.split("^")
            if len(parts) >= 4:
                allergies.append({
                    "allergen": parts[0],
                    "type": parts[1],
                    "reaction": parts[2],
                    "severity": parts[3],
                    "verified": parts[4] if len(parts) > 4 else ""
                })
        return allergies

    def parse_medications_response(self, raw: str) -> List[Dict]:
        """Parse ORWPS COVER response (multi-line)"""
        medications = []
        for line in raw.strip().split("\n"):
            parts = line.split("^")
            if len(parts) >= 6:
                medications.append({
                    "rx_number": parts[0],
                    "drug_name": parts[1],
                    "status": parts[2],
                    "qty": parts[3],
                    "refills": parts[4],
                    "last_fill_date": parts[5],
                    "expires": parts[6] if len(parts) > 6 else ""
                })
        return medications
```

---

## 8. Implementation Plan

### Phase 1: Walking Skeleton (Week 1)

**Goal**: Single-site, single-RPC working end-to-end

**Tasks**:
1. Create `vista/` directory structure
2. Implement `VistaServer` base class (site 200 only)
3. Implement `RpcDispatcher` with one RPC: `ORWPT PTINQ`
4. Implement `DataLoader` (read `patients.json`)
5. Implement `M-Serializer` basic functions
6. Create `vista/data/sites/200/patients.json` with 3 test patients
7. Implement FastAPI `main.py` with `/rpc/execute` endpoint
8. Write unit tests for dispatcher and serializer
9. Manual testing: curl commands to verify RPC execution

**Success Criteria**:
- ✅ `POST /rpc/execute?site=200` with `ORWPT PTINQ` returns valid VistA-formatted response
- ✅ Patient data correctly loaded from JSON
- ✅ Response format matches VistA ICD specification

### Phase 2: Multi-Site Support (Week 2)

**Goal**: Multiple sites (200, 500, 630) with site-specific data

**Tasks**:
1. Implement `VistaCluster` to manage multiple `VistaServer` instances
2. Create `vista/config/sites.json`
3. Create data files for sites 500 and 630
4. Implement `/sites` endpoint to list available sites
5. Implement `/health` endpoint
6. Update `VistaServer` to load site config from `sites.json`
7. Test RPC calls to all three sites with different patient data

**Success Criteria**:
- ✅ Three sites (200, 500, 630) running in single service
- ✅ Each site has unique patient data
- ✅ `GET /sites` returns all configured sites
- ✅ RPC calls correctly routed to appropriate site

### Phase 3: Demographics Domain (Week 2-3)

**Goal**: Complete demographics RPC coverage

**Tasks**:
1. Implement `ORWPT SELECT` RPC
2. Implement `ORWPT ID INFO` RPC
3. Enhance `patients.json` with complete demographic fields
4. Add unit tests for all demographics RPCs
5. Document demographics RPC responses in `vista/README.md`

**Success Criteria**:
- ✅ All 3 demographics RPCs implemented and tested
- ✅ Responses match VistA format per ICD

### Phase 4: Vitals Domain (Week 3)

**Goal**: Vitals RPC coverage with date-range queries

**Tasks**:
1. Implement `GMV LATEST VM` RPC
2. Implement `GMV EXTRACT REC` RPC with date filtering
3. Implement `GMV MANAGER` RPC
4. Create `vista/data/sites/{sta3n}/vitals.json` for all sites
5. Add date parsing/filtering logic in vitals handler
6. Unit tests for vitals RPCs

**Success Criteria**:
- ✅ All 3 vitals RPCs implemented
- ✅ Date-range filtering works correctly
- ✅ Multi-line vitals responses formatted correctly

### Phase 5: Allergies & Medications Domains (Week 4)

**Goal**: Complete Phase 1 domain coverage

**Tasks**:
1. Implement allergies RPCs (`ORQQAL LIST`, `ORQQAL DETAIL`, `ORQQAL ALLERGY MATCH`)
2. Implement medications RPCs (`ORWPS COVER`, `ORWPS DETAIL`, `ORWPS ACTIVE`, `PSO SUPPLY`)
3. Create `allergies.json` and `medications.json` for all sites
4. Unit tests for both domains
5. Integration testing: call all RPCs for a patient across all sites

**Success Criteria**:
- ✅ All Phase 1 RPCs (15 total) implemented and tested
- ✅ All four domains (demographics, vitals, allergies, medications) working

### Phase 6: Med-z1 Integration (Week 5)

**Goal**: Med-z1 app successfully calls vista service

**Tasks**:
1. Create `app/services/vista_client.py` in med-z1 app
2. Implement `VistaClient` class with `call_rpc()` and `call_rpc_multi_site()`
3. Implement domain-specific parsers in `VistaClient`
4. Add `VISTA_SERVICE_URL` to root `config.py`
5. Create example route in med-z1: `/patient/{icn}/vista-demographics`
6. Test multi-site aggregation (patient with data at multiple sites)
7. Document integration patterns in `app/README.md`

**Success Criteria**:
- ✅ Med-z1 app can call vista service
- ✅ Multi-site queries return aggregated results
- ✅ Parsed responses integrate with med-z1 UI

### Phase 7: Documentation & Hardening (Ongoing)

**Tasks**:
1. Write comprehensive `vista/README.md`
2. Add API documentation (OpenAPI/Swagger)
3. Add error handling for edge cases (patient not found, invalid params)
4. Add request/response logging
5. Performance testing (latency, concurrent requests)
6. Update `CLAUDE.md` with vista subsystem details

---

## 9. Technical Notes

### 9.1 VistA Date/Time Format

VistA uses FileMan date/time format: `YYYMMDD.HHMM` (e.g., `3241201.0930` = Dec 1, 2024 at 09:30)

**Conversion Utilities**:
```python
# vista/app/utils/vista_datetime.py
from datetime import datetime

def to_fileman_datetime(dt: datetime) -> str:
    """Convert Python datetime to FileMan format"""
    year_offset = dt.year - 1700
    return f"{year_offset:03d}{dt.month:02d}{dt.day:02d}.{dt.hour:02d}{dt.minute:02d}"

def from_fileman_datetime(fm: str) -> datetime:
    """Convert FileMan format to Python datetime"""
    parts = fm.split(".")
    date_part = parts[0]
    time_part = parts[1] if len(parts) > 1 else "0000"

    year = 1700 + int(date_part[:3])
    month = int(date_part[3:5])
    day = int(date_part[5:7])
    hour = int(time_part[:2])
    minute = int(time_part[2:4])

    return datetime(year, month, day, hour, minute)
```

### 9.2 Multi-Line Response Format

Some RPCs return multi-line responses (vitals, allergies, medications). Use newline `\n` as the line delimiter.

**Example**:
```python
# vista/app/utils/m_serializer.py
def pack_multi_line_response(items: List[str]) -> str:
    """Join multiple lines for list-based RPC responses"""
    return "\n".join(items)
```

### 9.3 Error Handling

**Standard VistA Error Format**: `"-1^Error message"`

```python
# vista/app/utils/m_serializer.py
def format_rpc_error(message: str, code: str = "-1") -> str:
    return f"{code}^{message}"

# Usage in handlers
if not patient:
    return format_rpc_error("Patient not found")
```

### 9.4 Running Vista Service

**Development (macOS laptop)**:
```bash
# From project root
cd vista
source ../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

**Access**:
- API Base: `http://localhost:8003`
- OpenAPI Docs: `http://localhost:8003/docs`
- Health Check: `http://localhost:8003/health`

**Running Alongside Med-z1**:
```bash
# Terminal 1: med-z1 app
uvicorn app.main:app --reload --port 8000

# Terminal 2: CCOW service
uvicorn ccow.main:app --reload --port 8001

# Terminal 3: Vista service
cd vista && uvicorn app.main:app --reload --port 8003
```

### 9.5 Testing Multi-Site Calls

**Example curl command**:
```bash
# Call site 200 (Alexandria)
curl -X POST "http://localhost:8003/rpc/execute?site=200" \
  -H "Content-Type: application/json" \
  -d '{"name": "ORWPT PTINQ", "params": ["1012853550V207686"]}'

# Call site 500 (Anchorage)
curl -X POST "http://localhost:8003/rpc/execute?site=500" \
  -H "Content-Type: application/json" \
  -d '{"name": "ORWPT PTINQ", "params": ["1012853550V207686"]}'
```

**Example Python test (multi-site)**:
```python
import asyncio
from app.services.vista_client import VistaClient

async def test_multi_site():
    vista = VistaClient()

    # Call all sites in parallel
    results = await vista.call_rpc_multi_site(
        sites=["200", "500", "630"],
        rpc_name="ORWPT PTINQ",
        params=["1012853550V207686"]
    )

    for site, response in results.items():
        if response.success:
            demographics = vista.parse_ptinq_response(response.data)
            print(f"Site {site}: {demographics['name']} - {demographics['icn']}")
        else:
            print(f"Site {site}: Error - {response.error}")

asyncio.run(test_multi_site())
```

---

## 10. Future Enhancements (Post-Phase 1)

### Level 2 Response Fidelity
- Add VistA-style headers (`LIST[0]` counts for multi-line responses)
- Handle edge cases (missing data, partial records)
- Authentic VistA error codes and messages

### Authentication Simulation
- Implement `XUS SIGNON SETUP` and `XUS AV CODE` for login flow
- Session/context management (if needed for testing)

### Additional Domains
- Patient Flags (DGPF namespace)
- Encounters (ORWCV namespace)
- Labs, Problems, Orders, Notes, Imaging

### Performance Optimization
- Add caching layer (Redis) for frequently accessed data
- Implement request rate limiting
- Add metrics/monitoring (Prometheus)

### Advanced Multi-Site Features
- Patient identity resolution across sites (if patient has different DFNs at different sites)
- Simulated network latency per site
- Site-specific outages/errors for testing resilience

---

## 11. Open Questions

1. **Patient Data Overlap**: Should the same patient (same ICN) exist at multiple sites, or should each site have unique patients?
   - **Recommendation**: Same patients at multiple sites (more realistic for testing)

2. **Date Ranges for Test Data**: How far back should vitals/medications/allergies data go?
   - **Recommendation**: 2-3 years of data per patient

3. **RPC Parameter Validation**: Should vista strictly validate RPC parameters, or be permissive?
   - **Recommendation**: Permissive initially (return errors for missing data, not invalid params)

4. **Docker Deployment**: Should vista be added to docker-compose.yml alongside SQL Server, MinIO, etc.?
   - **Recommendation**: Yes, but optional for Phase 1 (manual uvicorn fine for initial development)

---

## 12. Success Metrics

**Phase 1 Completion Criteria**:
- ✅ 15 RPCs implemented across 4 domains
- ✅ 3 sites (200, 500, 630) with unique patient data
- ✅ Med-z1 app successfully calls vista service
- ✅ Multi-site aggregation working (patient data from multiple sites)
- ✅ All responses match VistA format per ICD specification
- ✅ Unit test coverage >80%
- ✅ Integration tests for end-to-end flow (med-z1 → vista → response)
- ✅ Documentation complete (`vista/README.md`, API docs, integration guide)

---

## 13. References

- VA JLV ICD (Interface Control Document) - RPC specifications
- VistA RPC Broker documentation
- FileMan date/time format specification
- Prior research: `docs/vista-rpc-broker-research.md`

---

**End of Design Document**
