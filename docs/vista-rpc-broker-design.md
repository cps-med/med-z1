# VistA RPC Broker Simulator - Design Document

**Document Version:** v1.2
**Date:** 2025-12-15
**Status:** Draft - Critical Architecture Updates Applied

**Changelog v1.2** (2025-12-15):
- ✅ Added **ICN → DFN resolution** strategy (Section 2.7) - Critical for realistic simulation
- ✅ Added **Site Selection Policy** (Section 2.8) - Prevents regression to legacy JLV failure mode
- ✅ Added **Merge/Deduplication Rules** (Section 2.9.1) - Ensures data quality when combining PostgreSQL + Vista
- 🔄 Updated section numbering (2.8 → 2.9, 2.9 → 2.10, etc.)
- 📝 Based on senior solutions architect review feedback

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

**ICN → DFN Resolution** (Critical for Realistic Simulation):

Med-z1 routes use **ICN** as the primary patient identifier (e.g., `/api/patient/{icn}/vitals`), but real VistA RPCs are **DFN-driven** (local to each site). To maintain realism while keeping med-z1 routes clean, the Vista service must translate ICN → DFN internally:

```python
# vista/app/services/data_loader.py
class DataLoader:
    def __init__(self, site_sta3n: str, data_path: str):
        self.site_sta3n = site_sta3n
        self.patients = self._load_json(f"{data_path}/patients.json")
        # Build ICN→DFN lookup for this site
        self.icn_to_dfn = {
            p["icn"]: p["dfn"]
            for p in self.patients.get("patients", [])
        }

    def resolve_icn_to_dfn(self, icn: str) -> Optional[str]:
        """Resolve ICN to DFN for this site. Returns None if not found."""
        return self.icn_to_dfn.get(icn)

# vista/app/services/vista_server.py
class VistaServer:
    async def execute_rpc(self, rpc_name: str, params: list, icn: str = None) -> str:
        """Execute RPC, translating ICN→DFN if provided"""
        # If ICN provided, resolve to DFN for this site
        if icn:
            dfn = self.data_loader.resolve_icn_to_dfn(icn)
            if not dfn:
                return format_rpc_error(
                    f"Patient {icn} not found at site {self.sta3n}"
                )
            # Replace ICN in params with DFN for handler
            params = [dfn if p == icn else p for p in params]

        # Simulate network/processing latency
        if settings.rpc_latency_enabled:
            delay = random.uniform(settings.rpc_latency_min, settings.rpc_latency_max)
            await asyncio.sleep(delay)

        # Dispatch to domain handler (receives DFN, like real VistA)
        response = await self.dispatcher.dispatch(rpc_name, params)
        return response
```

**Contract**:
- **Med-z1 → Vista HTTP API**: Uses ICN (e.g., `POST /rpc/execute?site=200&icn=1012853550V207686`)
- **Vista internal handlers**: Receive DFN (like real VistA RPCs)
- **Vista data files**: Store both ICN and DFN per patient

This approach forces realistic identity complexity into the simulator while keeping med-z1's "ICN everywhere" pattern clean.

**Future Enhancement**: Implement full MPI service (`mpi/` subsystem) that:
- Exposes REST API for patient lookups: `GET /mpi/patient/{icn}`
- Returns list of treating facilities for query optimization
- Handles identity resolution (merged ICNs, duplicate records)

### 2.8 Site Selection Policy (Critical Performance Control)

**Decision**: Strict limits on which sites are queried for real-time data to prevent regression into legacy JLV "fan out to 140+ sites" behavior.

**Rationale**:
- The legacy JLV's primary performance problem is querying all treating facilities in real-time
- Without explicit limits, "refresh from VistA" could silently become "query everything"
- This policy is the **architectural firebreak** that prevents the new system from replicating the old failure mode

**Default Behavior**:
- Query **top 3 most recent treating facilities** for real-time refresh
- Sorted by `last_seen` date (descending) from treating_facilities list
- Ensures bounded query time regardless of patient's treatment history

**Per-Domain Site Limits**:
```python
# Default site limits per clinical domain
DOMAIN_SITE_LIMITS = {
    "vitals": 2,        # Freshest data, typically recent care
    "allergies": 5,     # Safety-critical, small payload, wider search
    "medications": 3,   # Balance freshness + comprehensiveness
    "demographics": 1,  # Typically unchanged, query most recent site only
    "labs": 3,          # Recent results most relevant
    "default": 3,       # Conservative default for new domains
}
```

**User Override Mechanism**:
- **Primary UX**: Per-domain "Refresh from VistA" button queries default site limit
- **Secondary UX**: "More sites..." button opens modal with:
  - Checkbox list of all treating facilities
  - Hard maximum of 10 sites per query
  - Staged refresh with progress indicator ("Querying site 2 of 5...")
  - Hard time budget (15 seconds max, then show partial results)

**Implementation**:
```python
# app/services/vista_client.py (or future realtime_overlay.py)
def get_target_sites(
    icn: str,
    domain: str,
    max_sites: int = None,
    user_selected_sites: list[str] = None
) -> list[str]:
    """
    Get list of sites to query for real-time data.

    Args:
        icn: Patient ICN
        domain: Clinical domain (vitals, allergies, etc.)
        max_sites: Override default limit (e.g., for "More sites..." action)
        user_selected_sites: Explicit site selection from UI

    Returns:
        List of sta3n values to query, ordered by priority
    """
    # If user explicitly selected sites, use those (up to hard limit)
    if user_selected_sites:
        return user_selected_sites[:10]  # Hard limit: 10 sites

    # Get treating facilities from patient registry
    patient = get_patient_from_registry(icn)
    treating_facilities = patient.get("treating_facilities", [])

    # Sort by last_seen descending (most recent first)
    sorted_facilities = sorted(
        treating_facilities,
        key=lambda x: x.get("last_seen", ""),
        reverse=True
    )

    # Apply domain-specific limit
    limit = max_sites or DOMAIN_SITE_LIMITS.get(domain, DOMAIN_SITE_LIMITS["default"])

    return [fac["sta3n"] for fac in sorted_facilities[:limit]]
```

**API Contract Update**:
```python
# Med-z1 routes specify site selection strategy
@router.get("/patient/{icn}/vitals-realtime")
async def get_vitals_realtime(
    icn: str,
    max_sites: int = None,  # Optional override for "More sites..."
    sites: str = None        # Comma-separated explicit site list
):
    """Fetch real-time vitals from VistA"""
    user_selected_sites = sites.split(",") if sites else None

    target_sites = get_target_sites(
        icn=icn,
        domain="vitals",
        max_sites=max_sites,
        user_selected_sites=user_selected_sites
    )

    # Call only selected sites
    vista_results = await vista.call_rpc_multi_site(
        sites=target_sites,
        rpc_name="GMV LATEST VM",
        params=[icn]  # Will be translated to DFN per site
    )
    ...
```

**Benefits**:
- ✅ **Performance bounded by default** (max 3 sites × 3 seconds = 9 seconds worst case)
- ✅ **User control without footguns** (explicit action required for wider queries)
- ✅ **Domain-specific tuning** (safety-critical domains can query more sites)
- ✅ **Prevents architectural regression** (impossible to accidentally query all 140+ sites)

**Success Metrics**:
- 90th percentile "Refresh from VistA" response time: <10 seconds
- No domain should ever query >10 sites by default
- User must take explicit action (2+ clicks) to query >5 sites

### 2.9 Temporal Data Strategy (T-0, T-1, T-2 Date Format)

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

#### 2.9.1 Merge and Deduplication Rules (Critical Data Quality Control)

**Problem**: Vista intentionally provides both T-0 (today) and T-1 (yesterday) data, and PostgreSQL also has T-1 data from CDW. Without explicit merge rules, the UI will show duplicate or contradictory values.

**Solution**: Define deterministic merge semantics per domain.

**Canonical Event Key**:

Each clinical event must have a unique identifier composed of:
```python
# Domain-specific canonical keys
CANONICAL_KEYS = {
    "vitals": ("date_time", "type", "sta3n", "vital_id"),
    "allergies": ("allergen", "allergen_type", "sta3n", "allergy_id"),
    "medications": ("rx_number", "sta3n"),
    "labs": ("specimen_date_time", "test_name", "sta3n", "lab_id"),
}

# Example for vitals:
# Key = ("2024-12-14 09:30:00", "BLOOD PRESSURE", "200", "12345")
```

**Merge Priority Rules**:

```python
# app/services/realtime_overlay.py (or app/db/<domain>.py)
def merge_postgresql_and_vista_data(
    postgresql_data: list,
    vista_data: list,
    domain: str
) -> list:
    """
    Merge PostgreSQL (historical) and Vista (real-time) data.

    Rules:
    1. For dates >= T-1: Prefer Vista (fresher, real-time)
    2. For dates < T-1: Use PostgreSQL only (Vista doesn't have older data)
    3. If duplicate key exists in both: Keep Vista version, log conflict
    4. Sort final result by date descending
    """
    from datetime import datetime, timedelta

    # Calculate T-1 boundary (yesterday at 00:00)
    t_minus_1 = (datetime.now() - timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Build canonical key function
    key_fields = CANONICAL_KEYS[domain]

    def get_key(item: dict) -> tuple:
        return tuple(item.get(field) for field in key_fields)

    # Index Vista data by key for fast lookup
    vista_by_key = {get_key(item): item for item in vista_data}

    # Merge logic
    merged = []
    duplicates_found = []

    # Add PostgreSQL data, checking for Vista overlaps
    for pg_item in postgresql_data:
        item_date = datetime.fromisoformat(pg_item["date_time"])
        item_key = get_key(pg_item)

        # If date >= T-1 and Vista has this key, skip PostgreSQL version
        if item_date >= t_minus_1 and item_key in vista_by_key:
            duplicates_found.append({
                "key": item_key,
                "kept": "vista",
                "discarded": "postgresql"
            })
            continue  # Skip PostgreSQL version

        # Otherwise, keep PostgreSQL version
        merged.append({**pg_item, "source": "postgresql"})

    # Add all Vista data (already prioritized)
    for vista_item in vista_data:
        merged.append({**vista_item, "source": "vista"})

    # Log duplicates for debugging
    if duplicates_found:
        logger.info(f"Merged {domain}: {len(duplicates_found)} duplicates resolved")
        logger.debug(f"Duplicate details: {duplicates_found}")

    # Sort by date descending (most recent first)
    merged.sort(key=lambda x: x["date_time"], reverse=True)

    return merged
```

**Deduplication Within Vista Results** (multiple sites):

```python
def dedupe_vista_multi_site_results(
    vista_results: dict[str, list],
    domain: str
) -> list:
    """
    Deduplicate results from multiple Vista sites.

    Rules:
    1. Same event at multiple sites: Keep one (arbitrary but deterministic)
    2. Different events at same datetime: Keep all (legitimate duplicates)
    """
    key_fields = CANONICAL_KEYS[domain]

    def get_key(item: dict) -> tuple:
        return tuple(item.get(field) for field in key_fields)

    seen_keys = set()
    deduped = []

    # Flatten all site results
    all_items = []
    for site, items in vista_results.items():
        for item in items:
            all_items.append({**item, "source_site": site})

    # Dedupe by canonical key
    for item in all_items:
        key = get_key(item)
        if key not in seen_keys:
            seen_keys.add(key)
            deduped.append(item)

    return deduped
```

**UI Presentation**:

```html
<!-- Optionally show data source for transparency -->
<div class="vital-entry" data-source="{{ vital.source }}">
    <span class="vital-date">Dec 14, 09:30 AM</span>
    <span class="vital-value">120/80 mm[Hg]</span>
    {% if show_sources %}
        <span class="source-badge">{{ vital.source }}</span>
    {% endif %}
</div>
```

**Benefits**:
- ✅ **No duplicate data shown** (clean UI, prevents confusion)
- ✅ **Deterministic merge** (same result every time, testable)
- ✅ **Prefer freshness** (Vista data prioritized for recent dates)
- ✅ **Audit trail** (log conflicts for debugging)

**Testing**:
```python
# Unit test for merge logic
def test_merge_postgresql_and_vista():
    pg_data = [
        {"date_time": "2024-12-13 10:00:00", "type": "BP", "sta3n": "200", "vital_id": "1"},
        {"date_time": "2024-12-14 09:00:00", "type": "BP", "sta3n": "200", "vital_id": "2"},
    ]
    vista_data = [
        {"date_time": "2024-12-14 09:00:00", "type": "BP", "sta3n": "200", "vital_id": "2"},
        {"date_time": "2024-12-14 14:00:00", "type": "BP", "sta3n": "200", "vital_id": "3"},
    ]

    merged = merge_postgresql_and_vista_data(pg_data, vista_data, "vitals")

    # Expect: 3 items (1 from pg for T-2, 2 from vista for T-0, duplicate removed)
    assert len(merged) == 3
    assert merged[0]["date_time"] == "2024-12-14 14:00:00"  # Most recent first
    assert merged[0]["source"] == "vista"
```

### 2.10 Simulated Network Latency

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

**Med-z1 UI Integration**: Add loading spinner and "Fetching real-time data from VistA..." indicator (see Section 2.11).

**Testing**: Set `VISTA_RPC_LATENCY_ENABLED=false` to disable delay for unit tests.

### 2.11 UI/UX Integration Pattern (Hybrid Approach)

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
- **Data source hidden**: UI doesn't explicitly show "CDW" vs "VistA" labels (preserves clean aesthetic)
- **Freshness indicator**: "Data current through: [date]" and "Last updated: [time]"
- **Processing feedback**: Spinner + status message during VistA queries
- **Partial failure transparency**: Show completeness indicator when some sites fail
  - Success: "Data current through: Dec 14, 2025 (today, real-time)"
  - Partial: "Data current through: Dec 14, 2025 (real-time refresh incomplete - 2 of 3 sites responded)"
  - Failure: "Unable to fetch real-time data. [Retry]"
- **Error handling**: Graceful degradation - show partial results with clear indicators

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
POST /rpc/execute?site={sta3n}&icn={icn}
Content-Type: application/json

Request Body:
{
  "name": "ORWPT PTINQ",
  "params": ["1012853550V207686"]
}

Note: If 'icn' query parameter is provided, the Vista service will automatically
resolve ICN → DFN for the specified site before executing the RPC handler.
RPC handlers receive DFN (like real VistA), but callers use ICN.

Response (200 OK):
{
  "site": "200",
  "rpc": "ORWPT PTINQ",
  "response": "SMITH,JOHN Q^1012853550V207686^19450315^M^666-12-1234^...",
  "timestamp": "2025-12-14T10:30:00Z",
  "elapsed_ms": 1234
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

**Goal**: Single-site, single-RPC working end-to-end with ICN → DFN resolution

**Critical Requirements** (from v1.2 design updates):
- ✅ ICN → DFN resolution implemented (Section 2.7)
- ✅ Patient registry file created with ICN/DFN mappings

**Tasks**:
1. Create `vista/` directory structure
2. Create `mock/shared/patient_registry.json` with 3 test patients (ICN + DFN per site)
3. Implement `DataLoader` with `resolve_icn_to_dfn()` method (reads `patients.json`)
4. Implement `VistaServer` base class (site 200 only)
   - Accept `icn` query parameter
   - Translate ICN → DFN before dispatching to handlers
   - Return error if ICN not found at site
5. Implement `RpcDispatcher` with one RPC: `ORWPT PTINQ`
6. Implement `M-Serializer` basic functions
7. Create `vista/data/sites/200/patients.json` with 3 test patients (include both ICN and DFN)
8. Implement FastAPI `main.py` with `/rpc/execute?site={sta3n}&icn={icn}` endpoint
9. Write unit tests for ICN resolution, dispatcher, and serializer
10. Manual testing: curl commands using ICN (not DFN) to verify RPC execution

**Success Criteria**:
- ✅ `POST /rpc/execute?site=200&icn=1012853550V207686` returns valid VistA-formatted response
- ✅ ICN → DFN resolution works correctly (handler receives DFN)
- ✅ Patient data correctly loaded from JSON
- ✅ Response format matches VistA ICD specification
- ✅ Error returned for ICN not found at site

### Phase 2: Multi-Site Support (Week 2)

**Goal**: Multiple sites (200, 500, 630) with site-specific data and site selection policy

**Critical Requirements** (from v1.2 design updates):
- ✅ Site selection policy implemented (Section 2.8)
- ✅ Default to top 3 most recent treating facilities
- ✅ Per-domain site limits enforced
- ✅ Hard maximum of 10 sites per query

**Tasks**:
1. Implement `VistaCluster` to manage multiple `VistaServer` instances
2. Create `vista/config/sites.json`
3. Update `mock/shared/patient_registry.json` with `treating_facilities` list (include `last_seen` dates)
4. Create data files for sites 500 and 630 (patients, with ICN/DFN mappings)
5. Implement `get_target_sites()` function in `app/services/vista_client.py` (or `app/services/`)
   - Read treating facilities from patient registry
   - Sort by `last_seen` descending
   - Apply per-domain limits (`DOMAIN_SITE_LIMITS` dict)
   - Enforce hard maximum of 10 sites
6. Implement `/sites` endpoint to list available sites
7. Implement `/health` endpoint
8. Update `VistaServer` to load site config from `sites.json`
9. Test RPC calls to all three sites with different patient data
10. Test site selection logic with mock patients

**Success Criteria**:
- ✅ Three sites (200, 500, 630) running in single service
- ✅ Each site has unique patient data with ICN/DFN mappings
- ✅ `GET /sites` returns all configured sites
- ✅ RPC calls correctly routed to appropriate site
- ✅ Site selection policy returns correct sites based on domain and treating facilities
- ✅ Hard maximum of 10 sites enforced even if user attempts to override

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

**Goal**: Complete Phase 1 domain coverage with merge/dedupe implementation

**Critical Requirements** (from v1.2 design updates):
- ✅ Merge/deduplication rules implemented (Section 2.9.1)
- ✅ PostgreSQL + Vista data merging logic
- ✅ Multi-site Vista data deduplication
- ✅ Canonical event keys per domain

**Tasks**:
1. Implement allergies RPCs (`ORQQAL LIST`, `ORQQAL DETAIL`, `ORQQAL ALLERGY MATCH`)
2. Implement medications RPCs (`ORWPS COVER`, `ORWPS DETAIL`, `ORWPS ACTIVE`, `PSO SUPPLY`)
3. Create `allergies.json` and `medications.json` for all sites (include T-0 and T-1 data)
4. Implement `merge_postgresql_and_vista_data()` function
   - Define canonical event keys for each domain
   - Implement merge priority rules (Vista preferred for T-1+, PostgreSQL for older)
   - Add deduplication logic for multi-site Vista results
5. Implement `dedupe_vista_multi_site_results()` function
6. Add T-0/T-1 temporal data to JSON files using relative notation
7. Unit tests for both domains
8. Unit tests for merge/dedupe logic (test cases from Section 2.9.1)
9. Integration testing: call all RPCs for a patient across all sites, verify no duplicates

**Success Criteria**:
- ✅ All Phase 1 RPCs (15 total) implemented and tested
- ✅ All four domains (demographics, vitals, allergies, medications) working
- ✅ Merge logic correctly combines PostgreSQL and Vista data without duplicates
- ✅ T-1 overlap period handled correctly (Vista preferred over PostgreSQL)
- ✅ Multi-site Vista results deduplicated properly

### Phase 6: Med-z1 Integration (Week 5)

**Goal**: Med-z1 app successfully calls vista service with UI integration

**Critical Requirements** (from v1.2 design updates):
- ✅ "Refresh from VistA" button UI pattern (Section 2.11)
- ✅ Partial failure transparency in UI
- ✅ Shared HTTP client with connection pooling
- ✅ Site selection policy enforced from med-z1 side

**Tasks**:
1. Create `app/services/vista_client.py` in med-z1 app
2. Implement `VistaClient` class with shared `httpx.AsyncClient`
   - `call_rpc()` and `call_rpc_multi_site()` methods
   - Connection pooling configuration
   - Timeout and error handling
3. Implement domain-specific parsers in `VistaClient`
4. Add `VISTA_SERVICE_URL` to root `config.py`
5. Create real-time routes for 2-3 domains:
   - `/patient/{icn}/vitals-realtime`
   - `/patient/{icn}/allergies-realtime`
   - Use `get_target_sites()` for site selection
   - Call `merge_postgresql_and_vista_data()` for data merge
6. Add "Refresh from VistA" button to domain pages
   - HTMX implementation with loading spinner
   - Freshness indicator ("Data current through: [date]")
   - Partial failure indicator ("2 of 3 sites responded")
7. Test multi-site aggregation (patient with data at multiple sites)
8. Test partial failure scenarios (1 site down, 2 sites respond)
9. Document integration patterns in `app/README.md`

**Success Criteria**:
- ✅ Med-z1 app can call vista service using ICN (not DFN)
- ✅ Multi-site queries return aggregated results with no duplicates
- ✅ Parsed responses integrate with med-z1 UI
- ✅ "Refresh from VistA" button works on 2+ domain pages
- ✅ Partial failures show clear UI indicators without breaking page
- ✅ HTTP client reuses connections (no new client per request)
- ✅ Site selection policy correctly limits sites queried

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

### 9.6 Mock CDW Site Alignment

**Context**: The Vista RPC Broker simulates three VistA sites: Alexandria (200), Anchorage (500), and Palo Alto (630). For realistic merge/dedupe testing, it's helpful (but not required) to have at least one test patient whose primary station in mock CDW matches a Vista site.

**Key Principle**: Vista JSON data files are **independent of mock CDW**. You can create Vista data for any site regardless of CDW coverage. However, having some overlap enables testing the PostgreSQL + Vista merge logic.

#### Pre-Implementation Validation

**Step 1: Check what sites have data in mock CDW**

```sql
-- Find which sites have the most patient activity
USE CDWWork;

SELECT
    d.Sta3n,
    d.Sta3nName,
    COUNT(DISTINCT sp.PatientSID) as patient_count,
    COUNT(DISTINCT v.VitalSignTakenDateTime) as vitals_count,
    COUNT(DISTINCT rx.LocalDrugSID) as meds_count
FROM Dim.Sta3n d
LEFT JOIN SPatient.SPatient sp ON sp.Sta3n = d.Sta3n
LEFT JOIN Vital.VitalSign v ON v.Sta3n = d.Sta3n
LEFT JOIN RxOut.RxOutpat rx ON rx.Sta3n = d.Sta3n
GROUP BY d.Sta3n, d.Sta3nName
ORDER BY patient_count DESC, vitals_count DESC;
```

**Step 2: Check which test patients exist and their primary stations**

```sql
USE CDWWork;

SELECT
    sp.PatientICN,
    sp.PatientSID,
    sp.Sta3n,
    d.Sta3nName,
    sp.PatientLastName,
    sp.PatientFirstName,
    COUNT(DISTINCT v.VitalSignTakenDateTime) as vitals_count,
    COUNT(DISTINCT a.AllergyIEN) as allergies_count,
    COUNT(DISTINCT rx.RxOutpatSID) as meds_count
FROM SPatient.SPatient sp
LEFT JOIN Dim.Sta3n d ON d.Sta3n = sp.Sta3n
LEFT JOIN Vital.VitalSign v ON v.PatientSID = sp.PatientSID
LEFT JOIN SPatient.Allergy a ON a.PatientSID = sp.PatientSID
LEFT JOIN RxOut.RxOutpat rx ON rx.PatientSID = sp.PatientSID
WHERE sp.PatientICN IS NOT NULL  -- Only patients with ICNs
GROUP BY sp.PatientICN, sp.PatientSID, sp.Sta3n, d.Sta3nName,
         sp.PatientLastName, sp.PatientFirstName
ORDER BY vitals_count + allergies_count + meds_count DESC;
```

**Step 3: Identify your richest test patient**

```sql
-- Quick check for a specific ICN
USE CDWWork;

SELECT
    PatientICN,
    PatientSID,
    Sta3n,
    PatientLastName,
    PatientFirstName
FROM SPatient.SPatient
WHERE PatientICN = '1012853550V207686';  -- Replace with your test patient's ICN
```

#### Alignment Options

**Option A: Sites 200, 500, 630 have good CDW data**
- ✅ **Action:** Use them as-is. No changes needed.

**Option B: Sites 200, 500, 630 exist but have sparse CDW data**
- ✅ **Action:** Still use them. Create rich Vista JSON data independently.
- 📝 **Note:** Some patients may only have Vista data at certain sites (valid test scenario).

**Option C: Sites 200, 500, 630 don't exist in CDW**
- ✅ **Action (Recommended):** Update one test patient's primary station to 200.
- ⚠️ **Alternative:** Use different sites that already have CDW data (update design doc site list).

#### Updating a Patient's Primary Station (If Needed)

If your richest test patient's primary station doesn't match 200, 500, or 630, you can realign:

```sql
USE CDWWork;

-- Update test patient's primary station to 200 (Alexandria)
UPDATE SPatient.SPatient
SET Sta3n = '200'
WHERE PatientICN = '1012853550V207686';  -- Replace with your test patient's ICN

-- Verify the change
SELECT
    PatientICN,
    PatientSID,
    Sta3n,
    PatientLastName,
    PatientFirstName
FROM SPatient.SPatient
WHERE PatientICN = '1012853550V207686';

-- Optional: Verify the station name
SELECT s.Sta3n, s.Sta3nName
FROM Dim.Sta3n s
WHERE s.Sta3n = '200';
```

**After updating:**
1. Re-run Bronze/Silver/Gold ETL pipeline for patient demographics
2. Reload PostgreSQL serving database: `patient_demographics` table
3. Verify in PostgreSQL:
   ```sql
   SELECT patient_icn, patient_key, name_display, primary_station, primary_station_name
   FROM patient_demographics
   WHERE patient_icn = '1012853550V207686';
   ```

#### Patient Registry Mapping

Once you've confirmed at least one test patient has a primary station that matches a Vista site, create the patient registry:

```json
// mock/shared/patient_registry.json
{
  "patients": [
    {
      "icn": "1012853550V207686",  // Your test patient from CDW
      "ssn": "666-12-1234",
      "name_last": "SMITH",
      "name_first": "JOHN",
      "name_middle": "Q",
      "dob": "1945-03-15",
      "sex": "M",
      "treating_facilities": [
        // At least ONE should match patient's CDW Sta3n for merge/dedupe testing
        {"sta3n": "200", "dfn": "100001", "last_seen": "T-7"},    // Recent visit
        {"sta3n": "500", "dfn": "500234", "last_seen": "T-30"},   // 1 month ago
        {"sta3n": "630", "dfn": "630789", "last_seen": "T-180"}   // 6 months ago
      ]
    }
  ]
}
```

#### Testing Scenarios Enabled

**Scenario 1: Patient has CDW data + Vista data at site 200**
- PostgreSQL has historical vitals (T-7 through T-2)
- Vista has real-time vitals (T-0, T-1)
- **Tests:** Merge/dedupe logic, T-1 overlap handling, canonical event keys

**Scenario 2: Patient has Vista data only at sites 500 and 630**
- PostgreSQL has no data for these sites
- Vista has real-time data
- **Tests:** Vista-only data flow, multi-site aggregation

**Scenario 3: Patient has CDW data but no Vista data at some sites**
- PostgreSQL has data
- Vista returns "patient not found at site"
- **Tests:** Partial failure handling, graceful degradation

#### Recommendation Summary

1. ✅ **Stick with sites 200, 500, 630** (design consistency, recognizable VA sites)
2. ✅ **Run validation queries** above to check current CDW coverage
3. ✅ **If needed:** Update one test patient's Sta3n to '200' (simple SQL UPDATE)
4. ✅ **Create patient_registry.json** mapping existing ICNs to DFNs at each Vista site
5. ✅ **Vista JSON data is independent** - control what exists per site regardless of CDW

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

### Realtime Overlay Service (Priority: Phase 6-7)

**Purpose:** Centralize real-time data orchestration logic to keep route handlers thin and maintainable.

**Rationale:** Based on architectural review feedback (2025-12-15), the multi-site query pattern, merge/dedupe logic, and site selection policy should not be embedded in individual route handlers. A dedicated service layer will:
- Prevent code duplication across domains (vitals, allergies, medications, labs, etc.)
- Enforce site selection policy consistently
- Apply merge/dedupe rules uniformly
- Handle partial failures gracefully
- Simplify testing and mocking

**Proposed Location:** `app/services/realtime_overlay.py`

**API Design:**
```python
class RealtimeOverlayService:
    """Orchestrates real-time data fetching from Vista and merging with PostgreSQL"""

    async def get_domain_with_overlay(
        icn: str,
        domain: str,
        days: int = 7,
        include_realtime: bool = True,
        max_sites: int = None,
        user_selected_sites: list[str] = None
    ) -> DomainOverlayResult:
        """
        Fetch historical data from PostgreSQL and optionally overlay real-time Vista data.

        Returns:
            DomainOverlayResult with:
            - data: Merged and deduplicated list
            - sources: Dict of site responses (success/failure)
            - completeness: "complete", "partial", or "failed"
            - timestamp: When refresh occurred
        """
        pass

    async def refresh_domain(
        icn: str,
        domain: str,
        site_policy: SitePolicy = SitePolicy.TOP_3
    ) -> RefreshResult:
        """Execute real-time refresh for a domain using site selection policy"""
        pass
```

**Implementation Dependencies:**
- Site selection policy (Section 2.8)
- Merge/dedupe rules (Section 2.9.1)
- ICN → DFN resolution (Section 2.7)
- VistaClient multi-site orchestration (Section 2.6)

**Benefits:**
- ✅ Routes stay thin (consistent with med-z1 routing patterns)
- ✅ Single place to update site limits or merge logic
- ✅ Easier to add new domains (reuse existing service)
- ✅ Clear separation of concerns (routing vs orchestration vs data access)

**Timeline:** Implement after 2-3 domains have established the pattern (Phase 6-7), then refactor existing routes to use the service.

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
