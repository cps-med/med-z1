# med-z4 Integration Quick Start Guide

**Purpose:** Get med-z4 working with shared auth.sessions and CCOW in 30 minutes
**Date:** 2026-01-27
**Prerequisites:** med-z1 running, PostgreSQL accessible, CCOW Vault running

---

## 1. Copy Session Functions (5 minutes)

**From med-z1 to med-z4:**

```bash
# Copy entire auth.py module
cp med-z1/app/db/auth.py med-z4/app/db/auth.py

# These functions are now available:
# - create_session(user_id, ip_address, user_agent)
# - get_session(session_id)
# - extend_session(session_id)
# - invalidate_session(session_id)
# - validate_credentials(email, password)
```

**✅ All timezone handling is already fixed (uses UTC)**

---

## 2. Configure Database (2 minutes)

```python
# med-z4/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/medz1  # ✅ Same as med-z1

# med-z4/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

AUTH_CONFIG = {
    "session_timeout_minutes": 15,
    "session_cookie_name": "med_z4_session_id",  # ✅ Unique name
}
```

---

## 3. Implement Login (5 minutes)

```python
# med-z4/app/routes/auth.py
from fastapi import APIRouter, Response, Request, HTTPException
from app.db import auth as auth_db
from config import AUTH_CONFIG

router = APIRouter()

@router.post("/login")
async def login(request: Request, response: Response, email: str, password: str):
    """Login user and create session."""
    # 1. Validate credentials
    user = auth_db.validate_credentials(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    # 2. Create session in shared auth.sessions table
    session_id = auth_db.create_session(
        user_id=user["user_id"],
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # 3. Set med-z4-specific cookie
    response.set_cookie(
        key=AUTH_CONFIG["session_cookie_name"],  # med_z4_session_id
        value=session_id,
        httponly=True,
        max_age=AUTH_CONFIG["session_timeout_minutes"] * 60,
        samesite="lax"
    )

    return {"success": True, "user_id": user["user_id"]}


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user and invalidate session."""
    session_id = request.cookies.get(AUTH_CONFIG["session_cookie_name"])
    if session_id:
        auth_db.invalidate_session(session_id)

    response.delete_cookie(AUTH_CONFIG["session_cookie_name"])
    return {"success": True}
```

---

## 4. Implement Authentication Middleware (5 minutes)

```python
# med-z4/app/middleware/auth.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
from app.db import auth as auth_db
from config import AUTH_CONFIG

class AuthMiddleware(BaseHTTPMiddleware):
    """Validate session on every request."""

    PUBLIC_PATHS = ["/login", "/logout", "/static", "/health"]

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)

        # Extract session from med-z4-specific cookie
        session_id = request.cookies.get(AUTH_CONFIG["session_cookie_name"])
        if not session_id:
            return RedirectResponse("/login", status_code=303)

        # Validate session
        session = auth_db.get_session(session_id)
        if not session:
            return RedirectResponse("/login", status_code=303)

        # Extend session on activity
        auth_db.extend_session(session_id)

        # Inject user into request state
        request.state.user = session

        return await call_next(request)


# Register middleware in main.py
from app.middleware.auth import AuthMiddleware
app.add_middleware(AuthMiddleware)
```

---

## 5. Implement CCOW Integration (10 minutes)

```python
# med-z4/app/services/ccow_service.py
import httpx
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

CCOW_BASE_URL = "http://localhost:8001"  # CCOW Vault


async def set_active_patient(request: Request, patient_id: str) -> bool:
    """
    Set active patient in CCOW vault.

    Args:
        request: FastAPI request (to extract session)
        patient_id: Patient ICN

    Returns:
        True if successful, False otherwise
    """
    # Extract med-z4 session from cookie
    session_id = request.cookies.get("med_z4_session_id")
    if not session_id:
        logger.warning("No session found for CCOW set_active_patient")
        return False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.put(
                f"{CCOW_BASE_URL}/ccow/active-patient",
                headers={"X-Session-ID": session_id},  # ✅ Pass via header
                json={"patient_id": patient_id, "set_by": "med-z4"}
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"CCOW set_active_patient failed: {e}")
        return False


async def get_active_patient(request: Request) -> dict:
    """
    Get active patient from CCOW vault.

    Returns:
        Patient context dict or None
    """
    session_id = request.cookies.get("med_z4_session_id")
    if not session_id:
        return None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{CCOW_BASE_URL}/ccow/active-patient",
                headers={"X-Session-ID": session_id}
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None  # No active patient
            else:
                logger.error(f"CCOW get_active_patient failed: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"CCOW get_active_patient failed: {e}")
        return None


async def clear_active_patient(request: Request) -> bool:
    """Clear active patient from CCOW vault."""
    session_id = request.cookies.get("med_z4_session_id")
    if not session_id:
        return False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.delete(
                f"{CCOW_BASE_URL}/ccow/active-patient",
                headers={"X-Session-ID": session_id},
                json={"cleared_by": "med-z4"}
            )
            return response.status_code == 204
    except Exception as e:
        logger.error(f"CCOW clear_active_patient failed: {e}")
        return False
```

---

## 6. Use CCOW in Routes (3 minutes)

```python
# med-z4/app/routes/patient.py
from fastapi import APIRouter, Request, Depends
from app.services import ccow_service

router = APIRouter()

@router.get("/patient/{icn}")
async def patient_overview(icn: str, request: Request):
    """Display patient overview and set in CCOW."""
    # Set active patient in CCOW
    await ccow_service.set_active_patient(request, icn)

    # ... rest of route logic
    return {"patient_id": icn, "name": "..."}


@router.get("/dashboard")
async def dashboard(request: Request):
    """Dashboard shows currently active patient from CCOW."""
    # Get active patient from CCOW
    context = await ccow_service.get_active_patient(request)

    if context:
        patient_id = context["patient_id"]
        # Load patient data...
    else:
        # Show "select patient" prompt
        pass

    return {"active_patient": context}
```

---

## 7. Testing (5 minutes)

### Test 1: Login and Session Creation

```bash
# Login to med-z4
curl -X POST http://localhost:8002/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c cookies_z4.txt \
  -v

# Verify cookie set
grep med_z4_session_id cookies_z4.txt
```

### Test 2: CCOW Integration

```bash
# Extract session ID
SESSION_ID=$(grep -oP 'med_z4_session_id\s+\K[^\s]+' cookies_z4.txt)

# Set patient in CCOW (via med-z4 session)
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID" \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100001", "set_by": "med-z4"}'

# Expected: 200 OK with patient context
```

### Test 3: Cross-Application Context

```bash
# Login to med-z1 (different session)
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c cookies_z1.txt

# Query CCOW from med-z1
curl -X GET http://localhost:8001/ccow/active-patient \
  -b cookies_z1.txt

# Expected: Returns ICN100001 set by med-z4
# (Same user, different sessions, shared context)
```

---

## Checklist

**Before You Start:**
- [ ] med-z1 is running (port 8000)
- [ ] PostgreSQL is accessible
- [ ] CCOW Vault is running (port 8001)
- [ ] You have test user credentials

**Implementation Steps:**
- [ ] Copied auth.py from med-z1 to med-z4
- [ ] Configured DATABASE_URL (same as med-z1)
- [ ] Set unique cookie name (med_z4_session_id)
- [ ] Implemented login/logout routes
- [ ] Implemented authentication middleware
- [ ] Implemented CCOW service layer
- [ ] Tested login creates session
- [ ] Tested CCOW set/get/clear operations
- [ ] Tested cross-application context sync

**Verification:**
- [ ] Database query shows sessions from both apps:
  ```sql
  SELECT session_id, user_id, created_at
  FROM auth.sessions
  ORDER BY created_at DESC
  LIMIT 5;
  ```
- [ ] CCOW shows patient context from med-z4
- [ ] med-z1 can see patient context set by med-z4
- [ ] Sessions expire after 15 minutes of inactivity

---

## Common Issues

**Issue:** "Invalid or expired session" immediately after login
- **Cause:** DATABASE_URL pointing to different database
- **Fix:** Verify both apps use same DATABASE_URL

**Issue:** "Missing authentication" from CCOW
- **Cause:** Not passing X-Session-ID header
- **Fix:** Ensure `headers={"X-Session-ID": session_id}` in CCOW requests

**Issue:** Context not synchronized between apps
- **Cause:** Different user_id values
- **Fix:** Verify both apps use same email/password for login

---

## Reference Documentation

- **Comprehensive Guide:** `docs/spec/timezone-and-session-management.md`
- **CCOW Testing:** `docs/guide/ccow-v2.1-testing-guide.md`
- **CCOW Design:** `docs/spec/ccow-multi-user-enhancement.md` (Section 14)

---

## Quick Reference: Key Patterns

```python
# 1. Create session (always UTC)
from datetime import datetime, timezone
now = datetime.now(timezone.utc)

# 2. Query session
session = auth_db.get_session(session_id)

# 3. CCOW request (header auth)
headers = {"X-Session-ID": session_id}
httpx.put(f"{CCOW_URL}/ccow/active-patient", headers=headers, json=data)

# 4. Extract cookie
session_id = request.cookies.get("med_z4_session_id")
```

---

**Estimated Time:** 30 minutes total

**Result:** med-z4 fully integrated with med-z1 authentication and CCOW context synchronization

---

**End of Quick Start Guide**
