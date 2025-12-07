# CCOW Context Vault – Consolidated Design & Implementation Guide

December 6, 2025 • Document version v1 (consolidated)

> **Note**  
> This document consolidates and refines the earlier design specs:
> - `ccow-context-vault-design.md`
> - `ccow-design-chatgpt-v3.md`  
> It is intended to be the **single source of truth** for the CCOW Context Vault implementation going forward.

---

## 0. How to Use This Document

This guide is both:

- A **reference manual** – precise, detailed, and implementation-ready
- A **tutorial** – with explanations and “learning notes” to strengthen your architecture and Python/FastAPI skills

If you just want to build the service:

1. Skim **Sections 1–3** (goals, architecture, requirements)
2. Implement code from **Sections 5–8** in the `ccow/` package
3. Wire med-z1 integration from **Section 10**
4. Use **Sections 11–14** for testing, operations, and future enhancements

If you want to learn as you go, read sequentially and don’t skip the **Learning Notes**.

---

## 1. Overview

### 1.1 Purpose

The **CCOW Context Vault** is a lightweight, standalone subsystem within **med-z1** that implements a simplified, CCOW-style mechanism for **patient context synchronization**.

It provides a **single source of truth** for the current “active patient” across multiple applications, so that when one app changes the active patient, other apps can discover and react to that change via a simple HTTP API.

### 1.2 Goals

The CCOW Context Vault will:

1. Maintain a **single global active patient context** identified by `patient_id`
2. Offer a **simple REST API** to:
   - Get the active patient
   - Set the active patient
   - Clear the active patient
   - View recent context change history
   - Check service health
3. Run as an **independent service** on its own port (default **8001**)
4. Live **inside the med-z1 repository** as the `ccow/` subsystem
5. Be **easy to understand, easy to extend**, and friendly for local development

### 1.3 Non-Goals (Phase 1)

This implementation is intentionally **not** a full HL7 CCOW implementation. It **does not** provide:

- Full CCOW transaction protocol, negotiation, or voting
- Multi-subject context (user + patient + encounter, etc.)
- Multi-user/multi-session context isolation
- Authentication/authorization
- Persistent storage (in-memory only)
- Real-time push notifications (WebSockets/SSE)

These are all candidates for **future phases**, once the core patterns are validated.

### 1.4 Why Use a Generic `patient_id`?

In real VA systems, you typically use **ICN (Integrated Care Number)** as the canonical patient identifier. For long-term flexibility, this design uses a generic field name:

- `patient_id` – A generic patient identifier.
  - In med-z1, this will **usually be the ICN**.
  - In other environments, `patient_id` could be a different key (e.g., MRN, enterprise ID).

You can later enforce “this must be an ICN” via validation or documentation without changing the API surface.

---

## 2. Background: HL7 CCOW and the Simplified Model

### 2.1 CCOW in a Nutshell

The **Clinical Context Object Workgroup (CCOW)** standard (by HL7) defines how healthcare apps synchronize context (such as active patient, user, encounter) in real-time. At a high level:

- A **Context Manager (Vault)** stores the shared context
- **Context Participants** (apps) read and propose changes to the context
- A **multi-phase transaction protocol** allows apps to accept or reject changes

### 2.2 What We’re Implementing

We implement a **simplified CCOW-style pattern**:

- Single **global patient context** identified by `patient_id`
- Immediate context updates (no transaction voting)
- Simple REST API for get/set/clear
- In-memory storage with a **bounded history buffer** for auditing/debugging

This is sufficient to:

- Demonstrate core CCOW concepts
- Support med-z1 and mock clients in development and demos
- Serve as a base for future production-ready CCOW integration

---

## 3. Requirements

### 3.1 Functional Requirements

**FR-1: Active Patient Storage**  
The vault SHALL maintain a single global “active patient” context, identified by `patient_id`.

**FR-2: Context Retrieval**  
Any client SHALL be able to retrieve the current active patient via API.

**FR-3: Context Update**  
Any client SHALL be able to set or update the active patient via API.

**FR-4: Context Clearing**  
Any client SHALL be able to clear the active patient via API.

**FR-5: Metadata Tracking**  
The vault SHALL track metadata for each active patient context, including:

- `patient_id`
- `set_by` – application that set the context
- `set_at` – UTC timestamp when it was set

**FR-6: Change History**  
The vault SHALL maintain an in-memory history of recent context changes (10–20 entries) including:

- Action (`"set"` or `"clear"`)
- `patient_id` (if applicable)
- Actor (`set_by` / `cleared_by`)
- Timestamp

**FR-7: Health Check**  
The vault SHALL expose a health check endpoint for monitoring.

---

### 3.2 Non-Functional Requirements

**NFR-1: Simplicity**  
- Minimal dependencies (FastAPI, Pydantic, standard library)
- In-memory storage (no DB, no Redis)

**NFR-2: Performance**  
- Requests should complete in **< 100ms** under normal local development load

**NFR-3: Consistency**  
- Python 3.11+
- FastAPI + Pydantic v2
- Consistent with med-z1 project conventions

**NFR-4: Availability**  
- Runs as an **independent service** on dedicated port (default `8001`)
- Can be started/stopped independently of `med-z1/app`

**NFR-5: Developer Experience**  
- Easy to understand
- Clear separation of concerns
- Good test coverage and logging

---

## 4. Architecture Overview

### 4.1 System Context

```text
┌───────────────────────────────────────────────────────────┐
│                 Clinical Workflow Environment             │
│                                                           │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │  med-z1/app  │   │ External App │   │ CPRS Emulator│   │
│  │   (FastAPI)  │   │  (any tech)  │   │   (optional) │   │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   │
│         │                  │                  │           │
│   PUT/GET/DELETE      GET/PUT/DELETE       GET/PUT        │
│  /ccow/active-patient /ccow/* endpoints    /ccow/*        │
│         │                  │                  │           │
│         └──────────────────┼──────────────────┘           │
│                            │                              │
│                            ▼                              │
│              ┌───────────────────────────────┐            │
│              │       CCOW Context Vault      │            │
│              │    (FastAPI on port 8001)     │            │
│              │ - In-memory patient context   │            │
│              │ - REST API                    │            │
│              │ - History + health            │            │
│              └───────────────────────────────┘            │
└───────────────────────────────────────────────────────────┘
````

### 4.2 Processes & Ports

Two key services:

| Service           | Port | Command Example                              | Purpose                    |
| ----------------- | ---- | -------------------------------------------- | -------------------------- |
| `med-z1/app`      | 8000 | `uvicorn app.main:app --reload --port 8000`  | Main med-z1 application    |
| `ccow` (this svc) | 8001 | `uvicorn ccow.main:app --reload --port 8001` | CCOW Context Vault service |

They communicate via HTTP (`http://localhost:8001`) and can be started/stopped independently.

### 4.3 Repository Structure

From the med-z1 project root:

```text
med-z1/
  config.py                     # Global config (includes CCOW config)
  .env                          # Environment variables

  app/
    main.py                     # Main med-z1 FastAPI app
    ccow_client.py              # Helper client to call CCOW services
    ...

  ccow/
    __init__.py
    main.py                     # FastAPI app & endpoints
    vault.py                    # Thread-safe in-memory vault
    models.py                   # Pydantic models (requests, responses, history)
    README.md                   # CCOW-specific README (optional)

  docs/
    ccow-vault-design.md        # THIS document
```

> **Design Choice:**
> To keep things simple, we do **not** split endpoints into a separate `api.py` router file. `ccow/main.py` both defines the FastAPI app and the endpoints. You can always refactor to `api.py` later if the service grows.

---

## 5. Data Model & Pydantic

### 5.1 Core Models (Pydantic v2)

At its core, **Pydantic** is a library for **data validation** and **settings management** using Python type annotations. While standard Python is dynamically typed, Pydantic enforces strict types at runtime. If you tell Pydantic "this variable must be an integer," it will either convert the incoming data to an integer or raise an error if it fails.  

Pydantic acts as a strict **gatekeeper** for data. Most validation libraries just check if data is correct. Pydantic actually **parses** it. If you pass the string "123" to a field defined as an int, Pydantic will automatically convert it to the integer 123 for you. This guarantees that once data is inside a Pydantic model, it is exactly the type you expect it to be.  

Pydantic is excellent for managing in-memory data structures. It serves as a rigorous **schema for your runtime objects**.

Create `ccow/models.py`:

```python
# ccow/models.py

from datetime import datetime, timezone
from typing import Optional, Literal

from pydantic import BaseModel, Field


class PatientContext(BaseModel):
    """Represents the active patient context stored in the vault."""

    patient_id: str = Field(..., description="Canonical patient identifier (e.g., ICN)")
    set_by: str = Field(..., description="Application or source that set this context")
    set_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the context was last set",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "1234567V890123",
                "set_by": "med-z1",
                "set_at": "2025-12-06T15:30:00.000Z",
            }
        }


class SetPatientContextRequest(BaseModel):
    """Request body for setting the active patient context."""

    patient_id: str = Field(..., min_length=1, description="Patient identifier")
    set_by: str = Field(
        default="med-z1",
        min_length=1,
        description="Application name setting the context",
    )


class ClearPatientContextRequest(BaseModel):
    """Optional request body for clearing context with metadata."""

    cleared_by: Optional[str] = Field(
        default=None,
        description="Application name clearing the context",
    )


class ContextHistoryEntry(BaseModel):
    """Represents a historical context change event."""

    action: Literal["set", "clear"] = Field(
        ...,
        description="Type of action performed: 'set' or 'clear'",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Patient identifier (None if context was cleared)",
    )
    actor: str = Field(
        ...,
        description="Application that performed the action",
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of the action",
    )
```

> **Learning Note – Why Pydantic?**
> Pydantic gives you:
>
> * **Validation** – ensure `patient_id` and `set_by` are non-empty strings
> * **Serialization** – convert Python `datetime` to ISO 8601 JSON automatically
> * **Schema generation** – FastAPI uses these models to generate OpenAPI docs
>   This keeps your code clean and your API self-documented.

---

## 6. HTTP API Specification

### 6.1 Base URL

```text
http://localhost:8001
```

All CCOW endpoints live under the `/ccow` prefix.

### 6.2 Summary of Endpoints

| Endpoint               | Method | Description                            |
| ---------------------- | ------ | -------------------------------------- |
| `/ccow/active-patient` | GET    | Get current active patient context     |
| `/ccow/active-patient` | PUT    | Set/update active patient context      |
| `/ccow/active-patient` | DELETE | Clear active patient context           |
| `/ccow/history`        | GET    | Retrieve recent context change history |
| `/ccow/health`         | GET    | Health check                           |
| `/`                    | GET    | Root info endpoint (service metadata)  |

All responses are JSON.

---

### 6.3 Get Active Patient

**Endpoint:** `GET /ccow/active-patient`

**Description:** Retrieve the current active patient context.

**Responses:**

* **200 OK** – Active context present:

  ```json
  {
    "patient_id": "1234567V890123",
    "set_by": "med-z1",
    "set_at": "2025-12-06T15:30:00.000Z"
  }
  ```

* **404 Not Found** – No active context set:

  ```json
  {
    "detail": "No active patient context"
  }
  ```

**Example curl:**

```bash
curl -X GET http://localhost:8001/ccow/active-patient
```

---

### 6.4 Set Active Patient

**Endpoint:** `PUT /ccow/active-patient`

**Description:** Set or update the active patient.

**Request Body:**

```json
{
  "patient_id": "1234567V890123",
  "set_by": "med-z1"
}
```

* `set_by` is optional; defaults to `"med-z1"`.

**Response (200 OK):**

```json
{
  "patient_id": "1234567V890123",
  "set_by": "med-z1",
  "set_at": "2025-12-06T15:30:00.000Z"
}
```

**Example curl:**

```bash
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "1234567V890123", "set_by": "med-z1"}'
```

---

### 6.5 Clear Active Patient

**Endpoint:** `DELETE /ccow/active-patient`

**Description:** Clear the active patient context.

**Request Body (optional):**

```json
{
  "cleared_by": "med-z1"
}
```

If omitted, `cleared_by` will be treated as `"unknown"`.

**Responses:**

* **204 No Content** – Context cleared successfully or previously set
* **404 Not Found** – No active context to clear

**Example curl:**

```bash
curl -X DELETE http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"cleared_by": "med-z1"}'
```

---

### 6.6 Get Context History

**Endpoint:** `GET /ccow/history`

**Description:** Retrieve the recent context change history (up to the configured max, default 20 events).

**Response (200 OK):**

```json
{
  "history": [
    {
      "action": "set",
      "patient_id": "1234567V890123",
      "actor": "med-z1",
      "timestamp": "2025-12-06T15:30:00.000Z"
    },
    {
      "action": "clear",
      "patient_id": null,
      "actor": "external-app",
      "timestamp": "2025-12-06T14:20:00.000Z"
    },
    {
      "action": "set",
      "patient_id": "9876543V210987",
      "actor": "cprs-emulator",
      "timestamp": "2025-12-06T14:15:00.000Z"
    }
  ]
}
```

**Example curl:**

```bash
curl -X GET http://localhost:8001/ccow/history
```

---

### 6.7 Health Check

**Endpoint:** `GET /ccow/health`

**Description:** Verify that the service is up and responsive.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "ccow-vault",
  "version": "1.0.0",
  "timestamp": "2025-12-06T15:30:00.000Z"
}
```

**Example curl:**

```bash
curl -X GET http://localhost:8001/ccow/health
```

---

### 6.8 Root Endpoint

**Endpoint:** `GET /`

**Description:** Lightweight service info endpoint.

**Response (200 OK):**

```json
{
  "service": "ccow",
  "message": "CCOW Context Vault is running",
  "version": "1.0.0"
}
```

---

## 7. Implementation – Vault Storage (`vault.py`)

Create `ccow/vault.py`:

```python
# ccow/vault.py

import threading
from collections import deque
from datetime import datetime, timezone
from typing import Optional

from .models import PatientContext, ContextHistoryEntry


class ContextVault:
    """Thread-safe in-memory vault for active patient context."""

    def __init__(self, max_history: int = 20):
        self._lock = threading.Lock()
        self._current: Optional[PatientContext] = None
        self._history: deque[ContextHistoryEntry] = deque(maxlen=max_history)

    def get_current(self) -> Optional[PatientContext]:
        """Retrieve the current active patient context, or None if not set."""
        with self._lock:
            return self._current

    def set_context(self, patient_id: str, set_by: str) -> PatientContext:
        """Set the active patient context and record a history entry."""
        with self._lock:
            context = PatientContext(
                patient_id=patient_id,
                set_by=set_by,
                set_at=datetime.now(timezone.utc),
            )

            self._current = context

            self._history.append(
                ContextHistoryEntry(
                    action="set",
                    patient_id=patient_id,
                    actor=set_by,
                    timestamp=context.set_at,
                )
            )

            return context

    def clear_context(self, cleared_by: Optional[str] = None) -> bool:
        """
        Clear the active patient context.

        Returns:
            True if there was an active context that was cleared,
            False if there was no active context.
        """
        with self._lock:
            if self._current is None:
                return False

            self._current = None
            self._history.append(
                ContextHistoryEntry(
                    action="clear",
                    patient_id=None,
                    actor=cleared_by or "unknown",
                    timestamp=datetime.now(timezone.utc),
                )
            )
            return True

    def get_history(self) -> list[ContextHistoryEntry]:
        """Return a snapshot list of historical context change events."""
        with self._lock:
            return list(self._history)


# Global singleton instance used by the FastAPI app
vault = ContextVault(max_history=20)
```

> **Learning Note – Thread Safety**
> Even though FastAPI is async, it typically runs on an ASGI server (like Uvicorn) with a **thread pool**. Using `threading.Lock()` around shared mutable state is the simplest, safe pattern for this in-memory vault. If you later move to Redis/PostgreSQL, the lock becomes less critical, but this pattern still keeps your code clean and explicit.

---

## 8. Implementation – FastAPI App (`main.py`)

Create `ccow/main.py`:

```python
# ccow/main.py

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .vault import vault
from .models import (
    PatientContext,
    SetPatientContextRequest,
    ClearPatientContextRequest,
    ContextHistoryEntry,
)

app = FastAPI(
    title="CCOW Context Vault",
    description="Simplified CCOW-style patient context synchronization service",
    version="1.0.0",
)

# CORS configuration (development-friendly; tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, restrict to known frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint for quick service introspection."""
    return {
        "service": "ccow",
        "message": "CCOW Context Vault is running",
        "version": "1.0.0",
    }


@app.get("/ccow/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ccow-vault",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.get("/ccow/active-patient", response_model=PatientContext)
async def get_active_patient():
    """Get the current active patient context."""
    context = vault.get_current()
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context",
        )
    return context


@app.put("/ccow/active-patient", response_model=PatientContext)
async def set_active_patient(request: SetPatientContextRequest):
    """Set or update the active patient context."""
    context = vault.set_context(
        patient_id=request.patient_id,
        set_by=request.set_by,
    )
    return context


@app.delete("/ccow/active-patient", status_code=status.HTTP_204_NO_CONTENT)
async def clear_active_patient(request: Optional[ClearPatientContextRequest] = None):
    """Clear the active patient context."""
    cleared_by = request.cleared_by if request else None
    cleared = vault.clear_context(cleared_by=cleared_by)

    if not cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context to clear",
        )

    return None


@app.get("/ccow/history")
async def get_context_history():
    """Get recent context change history."""
    history: list[ContextHistoryEntry] = vault.get_history()
    return {"history": history}
```

> **Learning Note – Response Models**
> FastAPI is clever enough to serialize Pydantic models and lists of models automatically. Returning `{"history": history}` where `history` is a `list[ContextHistoryEntry]` “just works” and produces predictable JSON.

---

## 9. Configuration & Running the Service

### 9.1 Configuration in `config.py`

Add CCOW-specific config to the root `config.py`:

```python
# config.py

import os

# ... existing config ...

# CCOW Context Vault configuration
CCOW_ENABLED: bool = os.getenv("CCOW_ENABLED", "true").lower() == "true"
CCOW_URL: str = os.getenv("CCOW_URL", "http://localhost:8001")
CCOW_VAULT_PORT: int = int(os.getenv("CCOW_VAULT_PORT", "8001"))
```

### 9.2 Environment Variables (`.env`)

```bash
# CCOW Context Vault
CCOW_ENABLED=true
CCOW_URL=http://localhost:8001
CCOW_VAULT_PORT=8001
```

### 9.3 Starting the Service

From the med-z1 project root:

```bash
# Activate your virtual environment
source .venv/bin/activate  # or equivalent on Windows

# Start CCOW vault on port 8001
uvicorn ccow.main:app --port 8001 --reload
```

You should see something like:

```text
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete.
```

### 9.4 Smoke Test

```bash
curl http://localhost:8001/ccow/health
```

Expected output (example):

```json
{
  "status": "healthy",
  "service": "ccow-vault",
  "version": "1.0.0",
  "timestamp": "2025-12-06T15:30:00.000Z"
}
```

---

## 10. Integration with `med-z1/app`

### 10.1 CCOW Client Utility (`app/utils/ccow_client.py`)

Create `app/utils/ccow_client.py`:

```python
# app/utils/ccow_client.py

"""
CCOW Context Vault Client Utility

Provides convenience functions for med-z1/app to interact with the CCOW vault.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

from config import CCOW_ENABLED, CCOW_URL

logger = logging.getLogger(__name__)


class CCOWClient:
    """Simple HTTP client for interacting with the CCOW Context Vault."""

    def __init__(self, base_url: str = CCOW_URL, enabled: bool = CCOW_ENABLED):
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled

    def set_active_patient(self, patient_id: str, set_by: str = "med-z1") -> bool:
        """
        Notify CCOW vault of an active patient change.

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            logger.debug("CCOW is disabled; skipping set_active_patient call")
            return False

        try:
            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={"patient_id": patient_id, "set_by": set_by},
                timeout=2.0,
            )
            response.raise_for_status()
            logger.info("Set CCOW active patient context to %s", patient_id)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to set CCOW context: %s", exc)
            return False

    def get_active_patient(self) -> Optional[str]:
        """
        Retrieve the current patient_id from CCOW.

        Returns:
            patient_id if set, or None if no active context or on error.
        """
        if not self.enabled:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                timeout=2.0,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return data.get("patient_id")
        except requests.RequestException as exc:
            logger.error("Failed to get CCOW context: %s", exc)
            return None

    def clear_active_patient(self, cleared_by: str = "med-z1") -> bool:
        """
        Clear the active patient context in CCOW.

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            return False

        try:
            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by},
                timeout=2.0,
            )
            if response.status_code == 404:
                logger.warning("No active CCOW patient context to clear")
                return False

            response.raise_for_status()
            logger.info("Cleared CCOW active patient context")
            return True
        except requests.RequestException as exc:
            logger.error("Failed to clear CCOW context: %s", exc)
            return False


# Global client instance for convenience
ccow_client = CCOWClient()
```

> **Learning Note – Graceful Degradation**
> Notice that all methods:
>
> * Respect `CCOW_ENABLED`
> * Return `None`/`False` on failure instead of raising errors into your UI
> * Log failures for debugging
>   This prevents CCOW issues from taking down your main app.

---

### 10.2 Wiring Into med-z1 Routes

#### 10.2.1 When a User Selects a Patient

```python
# Example: app/routes/patient.py

from fastapi import APIRouter, Request
from app.utils.ccow_client import ccow_client

router = APIRouter()

@router.get("/patient/{patient_id}")
async def patient_overview(patient_id: str, request: Request):
    """Patient overview page."""

    # 1. Fetch patient data (existing logic)
    patient = get_patient_data(patient_id)

    # 2. Notify CCOW service
    ccow_client.set_active_patient(patient_id=patient_id, set_by="med-z1")

    # 3. Render template
    return templates.TemplateResponse(
        "patient_overview.html",
        {"request": request, "patient": patient},
    )
```

#### 10.2.2 Showing Current Context on a Dashboard

```python
# Example: app/routes/dashboard.py

from fastapi import APIRouter, Request
from app.utils.ccow_client import ccow_client

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request):
    """Main dashboard page."""

    ccow_patient_id = ccow_client.get_active_patient()
    active_patient = None

    if ccow_patient_id:
        active_patient = get_patient_data(ccow_patient_id)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_patient": active_patient,
        },
    )
```

#### 10.2.3 Clearing Context on Logout

```python
# Example: app/routes/auth.py

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.utils.ccow_client import ccow_client

router = APIRouter()

@router.post("/logout")
async def logout():
    """User logout handler."""

    # Clear CCOW context when user logs out
    ccow_client.clear_active_patient(cleared_by="med-z1")

    # Existing logout logic ...
    return RedirectResponse("/login", status_code=303)
```

---

## 11. Testing Strategy

### 11.1 Unit Tests for Vault (`ccow/tests/test_vault.py`)

```python
# ccow/tests/test_vault.py

from ccow.vault import ContextVault


def test_vault_initially_empty():
    vault = ContextVault()
    assert vault.get_current() is None


def test_set_and_get_active_context():
    vault = ContextVault()
    ctx = vault.set_context(patient_id="P1", set_by="test-app")

    assert ctx.patient_id == "P1"
    assert ctx.set_by == "test-app"
    assert vault.get_current() is not None
    assert vault.get_current().patient_id == "P1"


def test_clear_context():
    vault = ContextVault()
    vault.set_context(patient_id="P1", set_by="test-app")
    cleared = vault.clear_context(cleared_by="test-app")

    assert cleared is True
    assert vault.get_current() is None


def test_clear_when_none_returns_false():
    vault = ContextVault()
    cleared = vault.clear_context(cleared_by="test-app")

    assert cleared is False


def test_history_tracks_set_and_clear():
    vault = ContextVault(max_history=10)

    vault.set_context(patient_id="P1", set_by="app1")
    vault.set_context(patient_id="P2", set_by="app2")
    vault.clear_context(cleared_by="app3")

    history = vault.get_history()
    assert len(history) == 3

    assert history[0].action == "set"
    assert history[0].patient_id == "P1"
    assert history[1].action == "set"
    assert history[1].patient_id == "P2"
    assert history[2].action == "clear"
    assert history[2].patient_id is None


def test_history_respects_max_length():
    vault = ContextVault(max_history=3)

    for i in range(5):
        vault.set_context(patient_id=f"P{i}", set_by="test")

    history = vault.get_history()
    assert len(history) == 3
    assert history[-1].patient_id == "P4"
```

### 11.2 API Tests with FastAPI TestClient (`ccow/tests/test_api.py`)

```python
# ccow/tests/test_api.py

from fastapi.testclient import TestClient

from ccow.main import app
from ccow.vault import vault

client = TestClient(app)


def setup_function(_):
    # Ensure vault is in a clean state before each test
    vault.clear_context(cleared_by="test-setup")


def test_health_check():
    response = client.get("/ccow/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_active_patient_when_none():
    response = client.get("/ccow/active-patient")
    assert response.status_code == 404


def test_put_and_get_active_patient():
    payload = {"patient_id": "P1", "set_by": "test-app"}

    # Set
    response = client.put("/ccow/active-patient", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "P1"

    # Get
    response = client.get("/ccow/active-patient")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "P1"


def test_delete_active_patient():
    payload = {"patient_id": "P1", "set_by": "test-app"}
    client.put("/ccow/active-patient", json=payload)

    response = client.delete("/ccow/active-patient", json={"cleared_by": "test-app"})
    # NOTE: typo "active-pient" here is intentional to illustrate that tests should
    # match the actual route. In your implementation, be sure to use the correct path:
    # "/ccow/active-patient".
    assert response.status_code in (204, 404)  # adjust once route is corrected
```

> **Note:** Fix the path typo when you paste this into your repo – it should be `/ccow/active-patient` in the test as well.

A corrected version:

```python
def test_delete_active_patient():
    payload = {"patient_id": "P1", "set_by": "test-app"}
    client.put("/ccow/active-patient", json=payload)

    response = client.delete("/ccow/active-patient", json={"cleared_by": "test-app"})
    assert response.status_code == 204

    response = client.get("/ccow/active-patient")
    assert response.status_code == 404
```

```python
def test_get_history_after_changes():
    client.put("/ccow/active-patient", json={"patient_id": "A", "set_by": "app1"})
    client.put("/ccow/active-patient", json={"patient_id": "B", "set_by": "app2"})
    client.delete("/ccow/active-patient", json={"cleared_by": "app3"})

    response = client.get("/ccow/history")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert len(data["history"]) == 3
```

### 11.3 Running Tests

From the project root:

```bash
pytest ccow/tests/ -v
```

---

## 12. Operational Considerations

### 12.1 Logging

**What to log:**

* Context set events (`patient_id`, `set_by`, timestamp)
* Context clear events (`cleared_by`, timestamp)
* API errors (via FastAPI/uvicorn logs)
* Service startup/shutdown

For now, basic logging via `logging` and uvicorn console output is sufficient. Later, you can add structured JSON logging and ship logs to a centralized system.

### 12.2 Monitoring

Use the `/ccow/health` endpoint for basic liveness checks in any monitoring system. Over time, you may add:

* Request count and latency metrics
* Error rate tracking (4xx vs 5xx)
* Context change rate metrics

### 12.3 Scaling & Persistence (Future)

Current design uses **in-memory storage**, which implies:

* One process = one context instance
* Multiple worker processes or containers would have separate contexts

For horizontal scaling or resilience:

* Replace `ContextVault` with a Redis- or database-backed implementation
* Keep the same public methods (`get_current`, `set_context`, etc.) so the rest of the code doesn’t change

---

## 13. Future Enhancements (Roadmap)

These are explicitly **out of scope** for the initial implementation but align with both original design docs.

### 13.1 Near-Term

* **Multi-user contexts** – per-user or per-session patient context
* **Persistent history** – store history in a database for longer-term auditing
* **API authentication** – e.g., API key for write operations

### 13.2 Medium-Term

* **Real-time notifications** – WebSocket/SSE so apps can subscribe to context changes
* **Multiple context types** – patient, encounter, user, location
* **Enhanced history querying** – filter by date range, actor, patient_id

### 13.3 Long-Term

* **Full CCOW transaction protocol** – proposal, vote, commit/rollback
* **Multi-channel support** – separate contexts per channel/workstation
* **Production hardening** – rate limiting, circuit breakers, advanced security and compliance

---

## 14. Quick Reference (Cheat Sheet)

### 14.1 Start Services

```bash
# Terminal 1: CCOW Context Vault
uvicorn ccow.main:app --reload --port 8001

# Terminal 2: med-z1 main app
uvicorn app.main:app --reload --port 8000
```

### 14.2 Key Endpoints

```bash
# Health
curl http://localhost:8001/ccow/health

# Get active patient
curl http://localhost:8001/ccow/active-patient

# Set active patient
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "1234567V890123", "set_by": "med-z1"}'

# Clear active patient
curl -X DELETE http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"cleared_by": "med-z1"}'

# History
curl http://localhost:8001/ccow/history
```

### 14.3 Files to Implement

* `ccow/models.py`
* `ccow/vault.py`
* `ccow/main.py`
* `app/utils/ccow_client.py`
* `ccow/tests/test_vault.py`
* `ccow/tests/test_api.py`
* Updates to `config.py` and `.env`

---

## 15. Glossary

| Term               | Definition                                                          |
| ------------------ | ------------------------------------------------------------------- |
| **CCOW**           | Clinical Context Object Workgroup (HL7) – standard for context sync |
| **Context**        | Shared clinical “focus”, e.g., current patient                      |
| **Vault**          | Central service that stores the active context                      |
| **Context Change** | Event representing set/clear of the active context                  |
| **patient_id**     | Generic patient identifier (ICN in med-z1)                          |
| **ICN**            | Integrated Care Number – VA’s enterprise patient identifier         |
| **Participant**    | Any application that reads or writes context via the CCOW service   |

---

## 16. Document History

| Version | Date       | Author | Notes                                      |
| ------- | ---------- | ------ | ------------------------------------------ |
| v1      | 2025-12-06 | You    | Consolidated design for CCOW Context Vault |

---

**End of Document**

```
