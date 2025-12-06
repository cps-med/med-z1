# CCOW Context Vault – Design Specification
December 6, 2025 | Document version v1

## 1. Overview

The **CCOW Context Vault** is a lightweight subsystem within med-z1 that implements a simplified version of the HL7 CCOW (Clinical Context Object Workgroup) standard for patient context synchronization. This utility enables med-z1 and other clinical applications to maintain a shared "active patient" context, supporting seamless clinical workflows across multiple applications.

### 1.1 Purpose

- Provide a **single source of truth** for the currently active patient context across multiple applications
- Enable med-z1 to **notify** external systems when the user changes the active patient
- Allow external applications to **query** the current active patient and optionally **set** the context
- Support future integration scenarios where multiple clinical applications need to stay synchronized

### 1.2 Scope

This is a **mock/development implementation** designed to:

- Demonstrate CCOW-like context synchronization patterns
- Support local development and testing scenarios
- Serve as a foundation for future production CCOW integration

**Explicitly Out of Scope (Phase 1):**
- Full CCOW standard compliance (secure context change transactions, participant surveys, etc.)
- Authentication/authorization
- Persistent storage (vault resets on service restart)
- Multi-user or multi-session contexts
- Real-time push notifications to clients (WebSocket/SSE)
- Integration with production VA CCOW infrastructure

---

## 2. Background: CCOW Standard

The HL7 Clinical Context Object Workgroup (CCOW) standard defines how healthcare applications can share clinical context (e.g., current patient, encounter, user) in real-time. Key concepts:

- **Context Manager (Vault)**: A central service that stores and manages the current clinical context
- **Context Participants**: Applications that can read, set, or respond to context changes
- **Context Change Transaction**: A multi-phase protocol where applications can accept or reject proposed context changes

For this implementation, we focus on a **simplified subset**:
- Single global patient context (ICN-based)
- Immediate context updates (no transaction/voting protocol)
- RESTful API for get/set/clear operations

---

## 3. Requirements

### 3.1 Functional Requirements

**FR-1: Active Patient Storage**
- The vault SHALL maintain a single global "active patient" context identified by ICN (Integrated Care Number)

**FR-2: Context Retrieval**
- Any application SHALL be able to retrieve the current active patient context via API

**FR-3: Context Update**
- Any application SHALL be able to set or update the active patient context via API

**FR-4: Context Clearing**
- Any application SHALL be able to clear the active patient context via API

**FR-5: Metadata Tracking**
- The vault SHALL track metadata for each context change:
  - Patient ICN
  - Source application that set the context (`set_by`)
  - Timestamp when context was set (`set_at`)

**FR-6: Change History**
- The vault SHALL maintain an in-memory history of the last 10-20 context changes for debugging and auditing purposes

**FR-7: Health Check**
- The vault SHALL provide a health check endpoint for monitoring

### 3.2 Non-Functional Requirements

**NFR-1: Simplicity**
- Minimal dependencies, straightforward implementation
- In-memory storage (no database required)

**NFR-2: Performance**
- API responses SHALL complete in <100ms under normal load

**NFR-3: Consistency**
- The vault SHALL follow med-z1 architectural patterns (Python 3.11, FastAPI, shared config)

**NFR-4: Availability**
- The vault SHALL run as an independent service on a dedicated port (8001)

---

## 4. Technical Architecture

### 4.1 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                     Clinical Workflow Environment            │
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │  med-z1/app  │      │  External    │      │   CPRS     │ │
│  │   (FastAPI)  │      │  EHR Client  │      │  Emulator  │ │
│  │              │      │              │      │            │ │
│  └──────┬───────┘      └──────┬───────┘      └─────┬──────┘ │
│         │                     │                    │        │
│         │ PUT /ccow/active-   │ GET /ccow/active-  │        │
│         │ patient (on user    │ patient (poll or   │        │
│         │ patient selection)  │ on app focus)      │        │
│         │                     │                    │        │
│         └─────────────────────┼────────────────────┘        │
│                               │                             │
│                               ▼                             │
│                   ┌─────────────────────────┐               │
│                   │   CCOW Context Vault    │               │
│                   │   (FastAPI on :8001)    │               │
│                   │                         │               │
│                   │  - In-memory storage    │               │
│                   │  - REST API             │               │
│                   │  - Change history       │               │
│                   └─────────────────────────┘               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Component Architecture

**CCOW Vault Service Components:**

```
ccow/
├── main.py           # FastAPI application, endpoint definitions
├── vault.py          # Core vault storage and business logic
├── models.py         # Pydantic request/response models
├── __init__.py       # Package initialization
└── README.md         # Setup, usage, and API documentation
```

**Technology Stack:**
- **Language**: Python 3.11
- **Framework**: FastAPI (consistent with med-z1/app)
- **Validation**: Pydantic v2
- **CORS**: Enabled for cross-origin requests (development scenario)
- **Storage**: In-memory Python dict with thread-safe access (threading.Lock)

**Deployment:**
- Runs as standalone service: `uvicorn ccow.main:app --port 8001`
- Shares virtual environment (`.venv/`) with rest of med-z1 project
- Configuration managed via root `config.py`

---

## 5. Data Models

### 5.1 Active Patient Context

**Python/Pydantic Model:**

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientContext(BaseModel):
    """Represents the active patient context"""
    icn: str = Field(..., description="Patient ICN (Integrated Care Number)")
    set_by: str = Field(..., description="Application or source that set this context")
    set_at: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp when context was set")

    class Config:
        json_schema_extra = {
            "example": {
                "icn": "1234567V890123",
                "set_by": "med-z1",
                "set_at": "2025-12-06T15:30:00.000Z"
            }
        }
```

**JSON Representation:**
```json
{
  "icn": "1234567V890123",
  "set_by": "med-z1",
  "set_at": "2025-12-06T15:30:00.000Z"
}
```

### 5.2 Request Models

**Set Patient Context Request:**
```python
class SetPatientContextRequest(BaseModel):
    """Request body for setting active patient context"""
    icn: str = Field(..., min_length=1, description="Patient ICN")
    set_by: str = Field(..., min_length=1, description="Application name setting the context")
```

**Clear Patient Context Request:**
```python
class ClearPatientContextRequest(BaseModel):
    """Optional request body for clearing context with metadata"""
    cleared_by: Optional[str] = Field(None, description="Application name clearing the context")
```

### 5.3 History Entry Model

```python
class ContextHistoryEntry(BaseModel):
    """Represents a historical context change event"""
    action: str = Field(..., description="Action type: 'set' or 'clear'")
    icn: Optional[str] = Field(None, description="Patient ICN (None if cleared)")
    actor: str = Field(..., description="Application that performed the action")
    timestamp: datetime = Field(..., description="UTC timestamp of the action")
```

### 5.4 Vault State (Internal)

```python
class VaultState:
    """Internal vault state (not exposed via API)"""
    current_context: Optional[PatientContext] = None
    history: list[ContextHistoryEntry] = []  # Max 20 entries, FIFO
```

---

## 6. API Specification

### 6.1 Base URL
```
http://localhost:8001
```

### 6.2 Endpoints

#### 6.2.1 Get Active Patient Context

**Endpoint:** `GET /ccow/active-patient`

**Description:** Retrieves the current active patient context.

**Request:** None (no body)

**Response:**

*Success (200 OK):*
```json
{
  "icn": "1234567V890123",
  "set_by": "med-z1",
  "set_at": "2025-12-06T15:30:00.000Z"
}
```

*No Active Context (404 Not Found):*
```json
{
  "detail": "No active patient context"
}
```

**Example:**
```bash
curl -X GET http://localhost:8001/ccow/active-patient
```

---

#### 6.2.2 Set Active Patient Context

**Endpoint:** `PUT /ccow/active-patient`

**Description:** Sets or updates the active patient context.

**Request Body:**
```json
{
  "icn": "1234567V890123",
  "set_by": "med-z1"
}
```

**Response:**

*Success (200 OK):*
```json
{
  "icn": "1234567V890123",
  "set_by": "med-z1",
  "set_at": "2025-12-06T15:30:00.000Z"
}
```

**Example:**
```bash
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"icn": "1234567V890123", "set_by": "med-z1"}'
```

---

#### 6.2.3 Clear Active Patient Context

**Endpoint:** `DELETE /ccow/active-patient`

**Description:** Clears the active patient context.

**Request Body (Optional):**
```json
{
  "cleared_by": "med-z1"
}
```

**Response:**

*Success (204 No Content):*
- No response body

*No Active Context (404 Not Found):*
```json
{
  "detail": "No active patient context to clear"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"cleared_by": "med-z1"}'
```

---

#### 6.2.4 Get Context Change History

**Endpoint:** `GET /ccow/history`

**Description:** Retrieves the recent context change history (last 10-20 entries).

**Request:** None

**Response:**

*Success (200 OK):*
```json
{
  "history": [
    {
      "action": "set",
      "icn": "1234567V890123",
      "actor": "med-z1",
      "timestamp": "2025-12-06T15:30:00.000Z"
    },
    {
      "action": "clear",
      "icn": null,
      "actor": "external-app",
      "timestamp": "2025-12-06T14:20:00.000Z"
    },
    {
      "action": "set",
      "icn": "9876543V210987",
      "actor": "cprs-emulator",
      "timestamp": "2025-12-06T14:15:00.000Z"
    }
  ]
}
```

**Example:**
```bash
curl -X GET http://localhost:8001/ccow/history
```

---

#### 6.2.5 Health Check

**Endpoint:** `GET /ccow/health`

**Description:** Returns service health status.

**Request:** None

**Response:**

*Success (200 OK):*
```json
{
  "status": "healthy",
  "service": "ccow-vault",
  "version": "1.0.0",
  "timestamp": "2025-12-06T15:30:00.000Z"
}
```

**Example:**
```bash
curl -X GET http://localhost:8001/ccow/health
```

---

## 7. Implementation Details

### 7.1 Vault Storage (vault.py)

**Core Implementation:**

```python
import threading
from typing import Optional
from datetime import datetime
from collections import deque
from .models import PatientContext, ContextHistoryEntry

class ContextVault:
    """Thread-safe in-memory vault for patient context"""

    def __init__(self, max_history: int = 20):
        self._lock = threading.Lock()
        self._current: Optional[PatientContext] = None
        self._history: deque[ContextHistoryEntry] = deque(maxlen=max_history)

    def get_current(self) -> Optional[PatientContext]:
        """Retrieve current active patient context"""
        with self._lock:
            return self._current

    def set_context(self, icn: str, set_by: str) -> PatientContext:
        """Set active patient context"""
        with self._lock:
            context = PatientContext(
                icn=icn,
                set_by=set_by,
                set_at=datetime.utcnow()
            )
            self._current = context

            # Add to history
            self._history.append(ContextHistoryEntry(
                action="set",
                icn=icn,
                actor=set_by,
                timestamp=context.set_at
            ))

            return context

    def clear_context(self, cleared_by: Optional[str] = None) -> bool:
        """Clear active patient context. Returns True if context was cleared."""
        with self._lock:
            if self._current is None:
                return False

            self._current = None

            # Add to history
            self._history.append(ContextHistoryEntry(
                action="clear",
                icn=None,
                actor=cleared_by or "unknown",
                timestamp=datetime.utcnow()
            ))

            return True

    def get_history(self) -> list[ContextHistoryEntry]:
        """Retrieve context change history"""
        with self._lock:
            return list(self._history)

# Global vault instance
vault = ContextVault(max_history=20)
```

### 7.2 FastAPI Application (main.py)

**Core Application Structure:**

```python
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

from .vault import vault
from .models import (
    PatientContext,
    SetPatientContextRequest,
    ClearPatientContextRequest,
    ContextHistoryEntry
)

app = FastAPI(
    title="CCOW Context Vault",
    description="Simplified CCOW-like patient context synchronization service",
    version="1.0.0"
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ccow/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ccow-vault",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/ccow/active-patient", response_model=PatientContext)
async def get_active_patient():
    """Get current active patient context"""
    context = vault.get_current()
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context"
        )
    return context

@app.put("/ccow/active-patient", response_model=PatientContext)
async def set_active_patient(request: SetPatientContextRequest):
    """Set active patient context"""
    context = vault.set_context(icn=request.icn, set_by=request.set_by)
    return context

@app.delete("/ccow/active-patient", status_code=status.HTTP_204_NO_CONTENT)
async def clear_active_patient(request: Optional[ClearPatientContextRequest] = None):
    """Clear active patient context"""
    cleared_by = request.cleared_by if request else None
    cleared = vault.clear_context(cleared_by=cleared_by)

    if not cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context to clear"
        )

    return None

@app.get("/ccow/history")
async def get_context_history():
    """Get recent context change history"""
    history = vault.get_history()
    return {"history": history}
```

### 7.3 Configuration Integration

**Add to root `config.py`:**

```python
# CCOW Context Vault Configuration
CCOW_ENABLED: bool = os.getenv("CCOW_ENABLED", "true").lower() == "true"
CCOW_URL: str = os.getenv("CCOW_URL", "http://localhost:8001")
CCOW_VAULT_PORT: int = int(os.getenv("CCOW_VAULT_PORT", "8001"))
```

**Add to root `.env`:**

```bash
# CCOW Context Vault
CCOW_ENABLED=true
CCOW_URL=http://localhost:8001
CCOW_VAULT_PORT=8001
```

---

## 8. Integration with med-z1/app

### 8.1 Client Utility Module

**Create:** `app/utils/ccow_client.py`

```python
"""
CCOW Context Vault Client Utility

Provides convenience functions for med-z1/app to interact with the CCOW vault.
"""

import requests
from typing import Optional
from datetime import datetime
import logging

from config import CCOW_ENABLED, CCOW_URL

logger = logging.getLogger(__name__)

class CCOWClient:
    """Client for interacting with CCOW Context Vault"""

    def __init__(self, base_url: str = CCOW_URL, enabled: bool = CCOW_ENABLED):
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled

    def set_active_patient(self, icn: str, set_by: str = "med-z1") -> bool:
        """
        Notify CCOW vault of active patient change.

        Args:
            icn: Patient ICN
            set_by: Application name (default: "med-z1")

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("CCOW is disabled, skipping set_active_patient")
            return False

        try:
            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={"icn": icn, "set_by": set_by},
                timeout=2.0
            )
            response.raise_for_status()
            logger.info(f"Set active patient context: {icn}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to set CCOW context: {e}")
            return False

    def get_active_patient(self) -> Optional[str]:
        """
        Retrieve current active patient ICN from CCOW vault.

        Returns:
            Patient ICN if set, None otherwise
        """
        if not self.enabled:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                timeout=2.0
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return data.get("icn")
        except requests.RequestException as e:
            logger.error(f"Failed to get CCOW context: {e}")
            return None

    def clear_active_patient(self, cleared_by: str = "med-z1") -> bool:
        """
        Clear active patient context in CCOW vault.

        Args:
            cleared_by: Application name (default: "med-z1")

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by},
                timeout=2.0
            )
            if response.status_code == 404:
                logger.warning("No active patient context to clear")
                return False
            response.raise_for_status()
            logger.info("Cleared active patient context")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to clear CCOW context: {e}")
            return False

# Global client instance
ccow_client = CCOWClient()
```

### 8.2 Integration Points in med-z1/app

**Example: Update patient route handler**

```python
from app.utils.ccow_client import ccow_client

@app.get("/patient/{icn}")
async def patient_overview(icn: str, request: Request):
    """Patient overview page"""

    # ... existing logic to fetch patient data ...

    # Notify CCOW vault of active patient change
    ccow_client.set_active_patient(icn=icn, set_by="med-z1")

    # ... render template ...
```

**Example: User logout or session end**

```python
@app.post("/logout")
async def logout():
    """User logout"""

    # Clear CCOW context when user logs out
    ccow_client.clear_active_patient(cleared_by="med-z1")

    # ... existing logout logic ...
```

---

## 9. Project Structure

```
med-z1/
├── ccow/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application
│   ├── vault.py                 # Vault storage implementation
│   ├── models.py                # Pydantic models
│   └── README.md                # Documentation and usage guide
│
├── app/
│   ├── utils/
│   │   ├── ccow_client.py       # CCOW client utility (NEW)
│   │   └── ...
│   └── ...
│
├── config.py                    # Add CCOW configuration
├── .env                         # Add CCOW environment variables
├── requirements.txt             # No new dependencies needed
└── docs/
    └── ccow-context-vault-design.md  # This document
```

---

## 10. Implementation Plan

### Phase 1: Core Vault Service (Est. 1-1.5 hours)

**Tasks:**
1. Create `ccow/` directory structure
2. Implement `ccow/models.py` with Pydantic models
3. Implement `ccow/vault.py` with thread-safe storage
4. Implement `ccow/main.py` with FastAPI endpoints
5. Add health check endpoint
6. Manual testing with curl/Postman

**Deliverables:**
- Functional CCOW vault service
- All API endpoints working
- History tracking operational

### Phase 2: Configuration & Client (Est. 0.5-1 hour)

**Tasks:**
7. Add CCOW configuration to root `config.py`
8. Add CCOW settings to `.env`
9. Create `app/utils/ccow_client.py` client utility
10. Add error handling and logging

**Deliverables:**
- Reusable client utility
- Configuration-driven enablement
- Graceful degradation if CCOW service unavailable

### Phase 3: Documentation (Est. 0.5 hours)

**Tasks:**
11. Create comprehensive `ccow/README.md` with:
    - Quick start guide
    - API documentation
    - Example usage scenarios
    - Integration patterns
12. Update root `README.md` with CCOW subsystem overview
13. Update `app/README.md` with CCOW integration notes

**Deliverables:**
- Complete subsystem documentation
- Integration examples

### Phase 4: Testing & Validation (Est. 0.5 hours)

**Tasks:**
14. Create simple test script demonstrating cross-app context sharing
15. Test med-z1/app integration
16. Verify history tracking
17. Test error conditions (service unavailable, invalid requests)

**Deliverables:**
- Working demo script
- Validated integration

**Total Estimated Effort:** 2.5-3 hours

---

## 11. Running the CCOW Vault

### 11.1 Starting the Service

**From project root:**

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Start CCOW vault service
uvicorn ccow.main:app --port 8001 --reload

# Output:
# INFO:     Uvicorn running on http://127.0.0.1:8001
# INFO:     Application startup complete.
```

### 11.2 Verifying Service is Running

```bash
# Health check
curl http://localhost:8001/ccow/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "ccow-vault",
#   "version": "1.0.0",
#   "timestamp": "2025-12-06T15:30:00.000Z"
# }
```

### 11.3 Example Workflow

```bash
# 1. Check if there's an active patient (initially none)
curl http://localhost:8001/ccow/active-patient
# Response: 404 Not Found

# 2. Set active patient from med-z1
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"icn": "1234567V890123", "set_by": "med-z1"}'
# Response: 200 OK with context data

# 3. External app queries current patient
curl http://localhost:8001/ccow/active-patient
# Response: {"icn": "1234567V890123", "set_by": "med-z1", "set_at": "..."}

# 4. View history
curl http://localhost:8001/ccow/history
# Response: {"history": [...]}

# 5. Clear context
curl -X DELETE http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"cleared_by": "med-z1"}'
# Response: 204 No Content
```

---

## 12. Future Enhancements

### 12.1 Phase 2+ Features (Not in Initial Implementation)

**Real-time Notifications:**
- Add WebSocket endpoint for push notifications when context changes
- Clients subscribe to context change events
- med-z1/app auto-updates UI when external app changes context

**Persistent Storage:**
- Add optional Redis backend for context persistence across restarts
- Retain history in SQLite or PostgreSQL
- Configuration flag to enable persistence

**Multi-User Contexts:**
- Support per-user or per-session contexts (keyed by user ID or session token)
- CCOW participants specify their context identifier

**Enhanced Security:**
- API key authentication
- Rate limiting
- Audit logging

**CCOW Transaction Protocol:**
- Implement pending context change flow
- Allow participants to accept/reject context changes
- Survey mechanism for context change coordination

**Additional Context Types:**
- Support encounter context (visit/appointment ID)
- Support user/clinician context
- Support location/facility context

**Observability:**
- Prometheus metrics (context change rate, active participants, etc.)
- Structured logging with correlation IDs
- OpenTelemetry integration

### 12.2 Integration Enhancements

**med-z1/app UI Auto-Update:**
- When external app changes context, show notification in med-z1 UI
- Optionally auto-navigate to the new patient
- User preference to enable/disable auto-context switching

**CPRS Emulator Integration:**
- Build lightweight CPRS emulator that uses CCOW vault
- Demonstrate cross-app context sync in realistic clinical scenario

**Browser Extension:**
- Simple Chrome/Firefox extension to view/set CCOW context
- Useful for testing and demonstrations

---

## 13. Testing Strategy

### 13.1 Unit Tests

**Vault Storage Tests:**
- Test thread-safe get/set/clear operations
- Verify history tracking (FIFO, max size)
- Test concurrent access scenarios

**API Endpoint Tests:**
- Test all endpoints with valid/invalid inputs
- Verify response codes and payloads
- Test error conditions

### 13.2 Integration Tests

**med-z1/app Integration:**
- Test CCOWClient utility functions
- Verify patient selection triggers context update
- Test graceful degradation when vault unavailable

**Cross-Application Scenarios:**
- Simulate multiple apps setting/getting context
- Verify history reflects all changes correctly

### 13.3 Manual Testing

**Interactive Demo Script:**
- Create simple Python script that simulates multiple apps
- Demonstrate context synchronization workflow
- Useful for stakeholder demos

---

## 14. Security Considerations

### 14.1 Development Environment (Current)

- **No authentication required** (open API)
- CORS enabled for all origins
- Suitable for local development only

### 14.2 Production Considerations (Future)

**If deployed to production-like environment:**

- **Authentication:** API key, OAuth 2.0, or mutual TLS
- **Authorization:** Role-based access control (which apps can set vs. read context)
- **Network Security:** Run on internal network only, not internet-facing
- **Audit Logging:** Log all context changes with source IP, user identity
- **Data Validation:** Strict validation of ICN format, application identifiers
- **Rate Limiting:** Prevent abuse/DoS
- **Encryption:** TLS for all API calls

**PHI/PII Handling:**
- The ICN is considered PII
- Production deployment would require compliance with VA privacy/security policies
- Audit trails must be retained and protected

---

## 15. Operational Considerations

### 15.1 Monitoring

**Health Checks:**
- `/ccow/health` endpoint for service availability monitoring
- Integrate with monitoring tools (Prometheus, Datadog, etc.)

**Metrics to Track:**
- Context change frequency (sets/clears per minute)
- Active patient query rate
- Error rate (4xx, 5xx responses)
- Average response time

### 15.2 Logging

**Log Events:**
- Service startup/shutdown
- Context set/clear actions (with actor and ICN)
- API errors and exceptions
- Configuration changes

**Log Format:**
- Structured JSON logs for easy parsing
- Include timestamps, log level, message, context data

### 15.3 Troubleshooting

**Common Issues:**

| Issue | Possible Cause | Resolution |
|-------|----------------|------------|
| 404 on all endpoints | Service not running | Start with `uvicorn ccow.main:app --port 8001` |
| Connection refused | Wrong port or firewall | Verify port 8001 is open, check CCOW_URL config |
| 404 on GET active-patient | No context set yet | Normal behavior; set context first with PUT |
| Context not persisting | Service restarted | Expected behavior; in-memory storage only |

---

## 16. Comparison to Real CCOW

### 16.1 What This Implementation Includes

✅ Central vault for active patient context
✅ RESTful API for get/set/clear operations
✅ Metadata tracking (who set context, when)
✅ Change history
✅ Simple, lightweight design

### 16.2 What Real CCOW Includes (Not Implemented Here)

❌ Secure context change transaction protocol
❌ Context participant survey/voting
❌ Authentication and authorization
❌ Support for multiple context types (encounter, user, location)
❌ Persistent storage
❌ Multi-user/multi-session contexts
❌ Real-time push notifications
❌ HL7 CCOW standard compliance

**This implementation is a simplified, developer-friendly subset suitable for:**
- Local development and testing
- Demonstrating context synchronization concepts
- Foundation for future production CCOW integration

---

## 17. References

### 17.1 CCOW Standard

- HL7 CCOW Standard: https://www.hl7.org/implement/standards/product_brief.cfm?product_id=1
- CCOW Overview: https://en.wikipedia.org/wiki/CCOW

### 17.2 Related Documentation

- `docs/med-z1-plan.md` - Overall med-z1 architecture and plan
- `app/README.md` - med-z1 FastAPI application documentation
- `mock/README.md` - Mock data subsystem overview

### 17.3 Technologies

- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- Uvicorn: https://www.uvicorn.org/

---

## 18. Glossary

| Term | Definition |
|------|------------|
| **CCOW** | Clinical Context Object Workgroup - HL7 standard for context synchronization |
| **ICN** | Integrated Care Number - unique patient identifier in VA systems |
| **Context** | The currently active clinical object (e.g., patient) shared across applications |
| **Vault** | Central service that stores and manages the active context |
| **Context Participant** | Application that can read or set the shared context |
| **med-z1** | Next-generation longitudinal health record viewer for VA |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1 | 2025-12-06 | Claude Code | Initial design specification |

---

**End of Document**
