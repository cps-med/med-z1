## 1. Conceptual model (what we’re actually building)

We’ll implement a **“CCOW Vault”** that does just three things:

1. **Maintain the active patient context**

   * A single in-memory object that holds the current active patient identifier (whatever your canonical med-z1 patient key is), plus some metadata (who set it, when).

2. **Expose a tiny HTTP API for other apps**

   * Example: `GET /ccow/active-patient`
     Any app (including med-z1/app) can call this to know which patient is currently selected.

3. **Let med-z1/app update the context**

   * When the user selects a new patient, med-z1/app calls
     `PUT /ccow/active-patient` with the new patient identifier.

We’re *simulating* CCOW, so we’re not doing full context negotiation, subscriptions, or multi-subject contexts. Think of this as:

> “A tiny context manager service that keeps track of the current patient and shares it via HTTP.”

---

## 2. Where it lives and high-level architecture

You said you slightly prefer to keep this inside **med-z1**, not as a separate repo. I’d follow that preference, but structure it as a **clean subsystem** so it *could* be split out later.

### Recommended layout (inside med-z1)

From your project root:

```text
med-z1/
  config.py
  app/                  # existing UI / API subsystem
  ccow_vault/           # NEW subsystem
    __init__.py
    vault.py            # in-memory context manager
    api.py              # HTTP endpoints / router
    schemas.py          # Pydantic models / dataclasses
    tests/
      test_vault.py
      test_api.py
  ...
```

Assuming `app/` is already a Python web app (FastAPI, Flask, etc.), the **ccow_vault** subsystem will just plug into that stack. If `app` is FastAPI, we’ll expose CCOW routes via an `APIRouter` and include it in the main app.

If one day you want it as a dedicated microservice, you can:

* Move `ccow_vault/` into its own repo,
* Add a tiny `main.py` to serve it as a standalone FastAPI app,
* And point med-z1/app to that service via a URL instead of localhost.

---

## 3. Data model for the “CCOW vault”

We’ll keep this intentionally small.

### Active patient context object

At minimum:

* `patient_id`: **string** – your canonical med-z1 patient identifier.
* `source`: **string** – who set this (e.g., `"med-z1/app"` or another client).
* `updated_at`: **datetime** – when it was last changed.

Python-side, this could be a dataclass:

```python
# ccow_vault/schemas.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ActivePatientContext:
    patient_id: str
    source: str
    updated_at: datetime
```

For the API layer, you can mirror this with Pydantic models if you’re using FastAPI.

If you later want more CCOW-ish structure, you could add:

* `user_id` / `workstation_id`
* `session_id`
* `facility_id`

and evolve toward per-user or per-session contexts instead of a single global.

---

## 4. The vault: in-memory, thread-safe singleton

### Responsibility

* Hold the *current* `ActivePatientContext` (or `None`).
* Provide `get_active()` / `set_active()` methods.
* Be **thread-safe** (since your app may serve concurrent requests).

### Sketch

```python
# ccow_vault/vault.py
from datetime import datetime, timezone
from threading import RLock
from typing import Optional

from .schemas import ActivePatientContext


class CcowVault:
    def __init__(self):
        self._lock = RLock()
        self._ctx: Optional[ActivePatientContext] = None

    def get_active(self) -> Optional[ActivePatientContext]:
        with self._lock:
            return self._ctx

    def set_active(self, patient_id: str, source: str) -> ActivePatientContext:
        ctx = ActivePatientContext(
            patient_id=patient_id,
            source=source,
            updated_at=datetime.now(timezone.utc),
        )
        with self._lock:
            self._ctx = ctx
        return ctx

    def clear(self) -> None:
        with self._lock:
            self._ctx = None


# A single shared instance inside this process
shared_vault = CcowVault()
```

**Important constraint:**
This is process-local. If you run multiple app instances (multiple processes or containers), they each get their own “vault.” That’s fine for now. If you later scale out, you can swap this to Redis/PostgreSQL or another shared store behind the same interface.

---

## 5. HTTP API design

Let’s keep the API surface minimal and explicit.

### Endpoints

**Base prefix:** `/ccow` (or `/api/ccow` depending on your existing style)

1. **Get active patient**

   * `GET /ccow/active-patient`
   * Response 200: `{ "patient_id": "...", "source": "...", "updated_at": "..." }`
   * Response 404: if none is set.

2. **Set active patient**

   * `PUT /ccow/active-patient` (or `POST`; I prefer `PUT` for “replace current context”)
     Request body:

   ```json
   {
     "patient_id": "123456",
     "source": "med-z1/app"
   }
   ```

   * Response 200: same as GET (the new active context).

3. **Clear active patient** (optional but handy)

   * `DELETE /ccow/active-patient`
   * Response 204 on success.

4. **Health check** (optional)

   * `GET /ccow/health` → `{"status": "ok"}`

### FastAPI-style implementation sketch

```python
# ccow_vault/api.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .vault import shared_vault

router = APIRouter(prefix="/ccow", tags=["ccow"])


class ActivePatientIn(BaseModel):
    patient_id: str
    source: str = "med-z1/app"  # default if not specified


class ActivePatientOut(BaseModel):
    patient_id: str
    source: str
    updated_at: datetime


@router.get("/active-patient", response_model=ActivePatientOut)
def get_active_patient():
    ctx = shared_vault.get_active()
    if ctx is None:
        raise HTTPException(status_code=404, detail="No active patient set")
    return ctx


@router.put("/active-patient", response_model=ActivePatientOut)
def put_active_patient(payload: ActivePatientIn):
    ctx = shared_vault.set_active(
        patient_id=payload.patient_id,
        source=payload.source,
    )
    return ctx


@router.delete("/active-patient", status_code=204)
def clear_active_patient():
    shared_vault.clear()
    return None
```

And in your **main app**:

```python
# app/main.py (or wherever your FastAPI app is defined)
from fastapi import FastAPI
from ccow_vault.api import router as ccow_router

app = FastAPI()

# ... your existing routes ...

app.include_router(ccow_router)
```

(If you’re not using FastAPI, the same idea carries over to Flask, etc.—just different decorator syntax.)

---

## 6. How med-z1/app uses the CCOW vault

### When the UI changes the active patient

In your UI subsystem (med-z1/app), wherever you currently handle “user selects a patient”:

1. Your server-side handler sets the active patient with a simple call to the vault (if it runs in the same process):

   ```python
   from ccow_vault.vault import shared_vault

   def on_patient_selected(patient_id: str, user_id: str | None = None):
       shared_vault.set_active(
           patient_id=patient_id,
           source="med-z1/app",
       )
       # then continue with your usual UI logic
   ```

   **OR**, if med-z1/app is separate from the vault process, make an HTTP call:

   ```python
   import requests

   def on_patient_selected(patient_id: str):
       requests.put(
           "http://localhost:8000/ccow/active-patient",
           json={"patient_id": patient_id, "source": "med-z1/app"},
           timeout=1.0,
       )
   ```

2. Your UI state is now consistent with the vault’s active context.

### When med-z1/app wants to know the current context

On initial load or when switching views:

* Server-side: call `shared_vault.get_active()` directly (if same process).
* Client-side: call `GET /ccow/active-patient` via JavaScript/HTMX and render the selected patient banner, etc.

If there’s no active patient (404), you can show your “No patient selected” view.

---

## 7. How external applications use it

Any other local or remote application can:

* **GET** `http://<med-z1-host>/ccow/active-patient` to know the current patient
* (Potentially) **PUT** `.../active-patient` if you trust it to change context

Later you can add:

* Simple authentication (API key, JWT, mTLS, etc.).
* “Read-only” clients vs “full” clients by endpoint or auth.

---

## 8. Implementation plan (step-by-step)

Here’s a pragmatic plan you can knock out in small increments:

1. **Create the subsystem skeleton**

   * Add `ccow_vault/` directory in med-z1 root.
   * Add `__init__.py`, `schemas.py`, `vault.py`, `api.py`, empty `tests/`.

2. **Implement the vault class**

   * Add `ActivePatientContext` dataclass in `schemas.py`.
   * Implement `CcowVault` and `shared_vault` in `vault.py`.
   * Add simple unit tests for `set_active`, `get_active`, `clear`.

3. **Implement the API router**

   * In `api.py`, create an `APIRouter` with endpoints:

     * `GET /ccow/active-patient`
     * `PUT /ccow/active-patient`
     * `DELETE /ccow/active-patient`
   * Unit-test via FastAPI’s `TestClient` (if using FastAPI).

4. **Wire into med-z1/app**

   * Include the router in your `main.py` / app entrypoint.
   * Verify `GET /ccow/health` (if you add it) and `GET /ccow/active-patient` via curl or browser.

5. **Hook med-z1/app UI to the vault**

   * On patient selection:

     * Server-side: call `shared_vault.set_active(...)` **or** HTTP `PUT`.
   * On page load:

     * Retrieve and display currently active patient, or show “none selected”.

6. **Add basic logging**

   * In `vault.set_active`, log something like:

     * `"CCOW: active patient set to {patient_id} by {source} at {updated_at}"`.
   * This is useful for debugging and for tracing context changes when you’re testing with multiple apps.

7. **(Optional) Add small enhancements**

   * `GET /ccow/context-history` if you’d like a simple in-memory list of the last N changes.
   * Support multiple contexts by channel/session ID:

     * e.g., `GET /ccow/channels/{channel_id}/active-patient`.
