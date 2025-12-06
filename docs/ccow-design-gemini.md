# Technical Design: CCOW Vault Subsystem

## 1\. Architectural Approach

The CCOW Vault will be implemented as a modular subsystem within the existing `med-z1` application. Rather than creating a standalone microservice with its own repository, we will treat it as a distinct "domain" within your current FastAPI monolith. This simplifies development, deployment, and configuration sharing.

### Key Components

1.  **In-Memory Store (The Vault):** A Singleton-pattern Python class responsible for holding the global state (Active Patient ICN + Metadata).
2.  **API Router:** A FastAPI `APIRouter` that exposes the specific endpoints (`GET`, `PUT`, `DELETE`).
3.  **Data Models:** Pydantic models to ensure strict typing for requests and responses.
4.  **Integration Point:** Mounting the CCOW router into the main `med-z1` FastAPI application instance.

### State Management Strategy

  * **Global Context:** Per your requirement, we will maintain a **Single Global Context**.
  * **Limitations:** Since this uses in-memory Python variables, the context is strictly tied to the running process. If you restart the server, the context is lost (reset to clear). If you run multiple worker processes (e.g., `gunicorn -w 4`), the context will *not* be shared across workers.
      * *Mitigation:* For this utility, we assume a single-worker environment (typical for dev/demos) or that this limitation is acceptable for a "basic implementation."

-----

## 2\. Directory Structure

We will add a new directory `ccow` (or `ccow_vault`) at the project root, keeping it distinct from `app` or `mock` but following the same pattern.

```text
med-z1/
├── config.py              # Shared configuration
├── main.py                # Main application entry point
├── app/                   # Existing application logic
├── mock/                  # Existing mock services
└── ccow/                  # NEW: CCOW Vault Subsystem
    ├── __init__.py
    ├── router.py          # FastAPI route definitions
    ├── schemas.py         # Pydantic models (Request/Response)
    └── store.py           # In-memory logic and state holder
```

-----

## 3\. Core Implementation

### A. Data Models (`ccow/schemas.py`)

We define strict schemas for the API to ensure the payload includes the required metadata.

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ActivePatientPayload(BaseModel):
    """Payload for setting the active patient."""
    icn: str
    user_id: str  # Metadata: Who set the context

class ActivePatientResponse(BaseModel):
    """Response model for the active patient context."""
    icn: Optional[str] = None
    user_id: Optional[str] = None
    set_at: Optional[datetime] = None
    status: str  # "active" or "empty"
```

### B. In-Memory Store (`ccow/store.py`)

This class manages the single global state.

```python
from datetime import datetime, timezone
from typing import Optional

class CCOWVault:
    def __init__(self):
        self._icn: Optional[str] = None
        self._user_id: Optional[str] = None
        self._set_at: Optional[datetime] = None

    def set_context(self, icn: str, user_id: str):
        """Updates the global context."""
        self._icn = icn
        self._user_id = user_id
        self._set_at = datetime.now(timezone.utc)

    def get_context(self):
        """Retrieves the current context."""
        if not self._icn:
            return {"status": "empty", "icn": None, "user_id": None, "set_at": None}
        
        return {
            "status": "active",
            "icn": self._icn,
            "user_id": self._user_id,
            "set_at": self._set_at
        }

    def clear_context(self):
        """Clears the global context."""
        self._icn = None
        self._user_id = None
        self._set_at = None

# Global Singleton Instance
vault = CCOWVault()
```

### C. API Router (`ccow/router.py`)

This connects the HTTP endpoints to the Vault store.

```python
from fastapi import APIRouter, HTTPException, status
from .schemas import ActivePatientPayload, ActivePatientResponse
from .store import vault

router = APIRouter(prefix="/ccow", tags=["CCOW Vault"])

@router.get("/active-patient", response_model=ActivePatientResponse)
async def get_active_patient():
    """
    Retrieve the currently active patient identifier from the vault.
    """
    return vault.get_context()

@router.put("/active-patient", response_model=ActivePatientResponse)
async def set_active_patient(payload: ActivePatientPayload):
    """
    Update the vault with a new active patient.
    Metadata (user_id) is required to track who changed the context.
    """
    vault.set_context(icn=payload.icn, user_id=payload.user_id)
    return vault.get_context()

@router.delete("/active-patient", response_model=ActivePatientResponse)
async def clear_active_patient():
    """
    Clear the current patient context from the vault.
    """
    vault.clear_context()
    return vault.get_context()
```

-----

## 4\. Integration Plan

### Step 1: Mount the Subsystem

In your main application file (likely `med-z1/main.py`), you need to import and include the new router.

```python
# med-z1/main.py

from fastapi import FastAPI
from ccow.router import router as ccow_router
# ... other imports (app_router, mock_router, etc.)

app = FastAPI(title="med-z1")

# Mount existing routers
# app.include_router(app_router)
# app.include_router(mock_router)

# Mount the new CCOW router
app.include_router(ccow_router)
```

### Step 2: Client Integration (med-z1/app UI)

When the UI (or the backend serving the UI) needs to switch patients or check context, it should communicate via these HTTP endpoints.

**Example Scenario: User selects a patient in the UI**

1.  **User Action:** User searches for "John Doe" and clicks "Select" (ICN: `123456789`).
2.  **Frontend/Backend Logic:**
      * The application performs its standard logic.
      * It *also* fires an async HTTP request to the CCOW Vault.

<!-- end list -->

```python
# Example utility function within med-z1/app/services.py
import httpx
from config import BASE_URL # Assuming you have a base URL config

async def notify_ccow_context_change(icn: str, user_id: str):
    url = f"{BASE_URL}/ccow/active-patient"
    payload = {"icn": icn, "user_id": user_id}
    
    try:
        async with httpx.AsyncClient() as client:
            await client.put(url, json=payload)
    except Exception as e:
        print(f"Failed to sync with CCOW vault: {e}")
```

**Example Scenario: Dashboard Polling**

  * The dashboard can poll `GET /ccow/active-patient` every few seconds.
  * If the returned ICN differs from the one currently displayed in the UI, the UI can prompt the user: *"Patient context has changed to ICN 12345. Switch now?"*

-----

## 5\. Summary of API Specifications

| Method | Endpoint | Description | Payload (JSON) |
| :--- | :--- | :--- | :--- |
| **GET** | `/ccow/active-patient` | Returns current active ICN and metadata. | N/A |
| **PUT** | `/ccow/active-patient` | Sets the global active ICN. | `{"icn": "1010101", "user_id": "dr_smith"}` |
| **DELETE** | `/ccow/active-patient` | Clears the context (sets to null). | N/A |

## 6\. Future Considerations (Out of Scope for now)

If you decide to graduate this from a utility/mock to a production feature:

1.  **Concurrency:** Replace the in-memory `CCOWVault` class with a Redis backing store to support multiple worker processes.
2.  **Security:** Add an `x-api-key` header or OAuth token validation to the `router.py` dependencies.
3.  **Context Management:** Add support for "subjects" other than patients (e.g., Encounter, Observation) by expanding the `VaultStore` dictionary.
