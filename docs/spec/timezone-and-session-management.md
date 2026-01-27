# Timezone and Session Management - Multi-Application Integration Guide

**Document Version:** v1.0
**Date:** 2026-01-27
**Purpose:** Ensure consistent timezone handling across med-z1, med-z4, CCOW, and all integrated applications

---

## Table of Contents

1. [Overview](#1-overview)
2. [Timezone Standard](#2-timezone-standard)
3. [Session Management Architecture](#3-session-management-architecture)
4. [Database Schema](#4-database-schema)
5. [Application Integration Patterns](#5-application-integration-patterns)
6. [CCOW Integration Requirements](#6-ccow-integration-requirements)
7. [Testing and Validation](#7-testing-and-validation)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Overview

The med-z1 ecosystem uses a **shared authentication database** (`auth.sessions` table) to enable single sign-on (SSO) across multiple applications. All applications must follow consistent timezone and session management practices to ensure proper functionality.

### 1.1 Architectural Principles

```
┌─────────────────────────────────────────────────────────────────┐
│ TIMEZONE STANDARD: All timestamps MUST use UTC                 │
│ - Database: All TIMESTAMP columns store UTC                    │
│ - Application code: Use datetime.now(timezone.utc)            │
│ - Display: Convert to user's local timezone in UI only        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SHARED SESSION TABLE: auth.sessions                            │
│ - Single source of truth for authentication                    │
│ - Shared by: med-z1, med-z4, CCOW Vault, future apps          │
│ - Each app uses its own session cookie name                    │
│ - Session UUIDs are the common identifier                      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Why UTC?

| Reason | Explanation |
|--------|-------------|
| **Cross-timezone users** | Clinicians may work from different time zones |
| **Daylight Saving Time** | UTC never changes, no DST ambiguity |
| **Server migration** | Moving servers across time zones doesn't break sessions |
| **Audit compliance** | Legal/audit requirements need absolute time references |
| **Multi-app consistency** | All apps interpret session expiration identically |

---

## 2. Timezone Standard

### 2.1 Python Code Patterns

**✅ CORRECT - Always use UTC:**

```python
from datetime import datetime, timedelta, timezone

# Creating timestamps
now = datetime.now(timezone.utc)
expires_at = now + timedelta(minutes=15)

# Storing in database
conn.execute(query, {
    "created_at": now,
    "expires_at": expires_at
})
```

**❌ WRONG - Never use naive datetime:**

```python
from datetime import datetime, timedelta

# BAD - Uses local timezone (system dependent)
now = datetime.now()
expires_at = now + timedelta(minutes=15)
```

### 2.2 PostgreSQL Configuration

**Verify PostgreSQL timezone:**

```sql
-- Check server timezone (should be UTC)
SHOW timezone;

-- Verify timestamp storage
SELECT
    session_id,
    created_at,
    expires_at,
    pg_typeof(created_at) as created_type,
    pg_typeof(expires_at) as expires_type
FROM auth.sessions
LIMIT 1;
```

**Expected:**
- `timezone`: `UTC`
- `created_type`: `timestamp without time zone` (stores as UTC)
- `expires_type`: `timestamp without time zone` (stores as UTC)

**Note:** PostgreSQL "timestamp without time zone" stores values as-is. When Python passes UTC datetimes, PostgreSQL stores them correctly. The application layer is responsible for UTC consistency.

### 2.3 Session Expiration Comparison

**Smart comparison pattern (handles both timezone-aware and naive):**

```python
from datetime import datetime, timezone

def is_session_expired(expires_at: datetime) -> bool:
    """
    Check if session has expired, handling both timezone-aware and naive datetimes.

    Args:
        expires_at: Session expiration datetime from database

    Returns:
        True if expired, False if still valid
    """
    if expires_at.tzinfo is None:
        # Timezone-naive (legacy sessions or misconfig)
        now = datetime.now()  # Use naive local time
    else:
        # Timezone-aware (correct approach)
        now = datetime.now(timezone.utc)  # Use UTC

    return expires_at < now
```

**This pattern is used in:**
- `ccow/auth_helper.py` - CCOW session validation
- `app/middleware/auth.py` - med-z1 middleware

---

## 3. Session Management Architecture

### 3.1 Shared Session Table

```
auth.sessions (PostgreSQL)
├── session_id (UUID, PK)         ← Common identifier across apps
├── user_id (UUID, FK)            ← Links to auth.users
├── created_at (TIMESTAMP)        ← UTC timestamp
├── last_activity_at (TIMESTAMP)  ← UTC timestamp, updated on each request
├── expires_at (TIMESTAMP)        ← UTC timestamp, TTL enforcement
├── is_active (BOOLEAN)           ← Manual revocation flag
├── ip_address (VARCHAR)          ← Security audit
└── user_agent (TEXT)             ← Security audit
```

### 3.2 Application-Specific Cookie Names

| Application | Cookie Name | Port | Session Table |
|-------------|-------------|------|---------------|
| med-z1 | `session_id` | 8000 | auth.sessions |
| med-z4 | `med_z4_session_id` | 8002 | auth.sessions |
| CCOW Vault | N/A (accepts both via header/cookie) | 8001 | N/A (reads auth.sessions) |
| Future apps | `<app>_session_id` | TBD | auth.sessions |

**Key Point:** Different cookie names, **same session UUID** in `auth.sessions` table.

### 3.3 Session Lifecycle

```
┌────────────────────────────────────────────────────────────────┐
│ 1. LOGIN (med-z1 or med-z4)                                    │
├────────────────────────────────────────────────────────────────┤
│ - User enters credentials                                      │
│ - App validates against auth.users                            │
│ - App calls create_session(user_id)                           │
│   → INSERT INTO auth.sessions                                 │
│   → created_at = NOW() UTC                                    │
│   → expires_at = NOW() UTC + 15 minutes                       │
│ - App sets cookie (app-specific name, session UUID value)    │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 2. REQUEST WITH SESSION COOKIE                                 │
├────────────────────────────────────────────────────────────────┤
│ - App extracts session_id from cookie                         │
│ - App queries: SELECT * FROM auth.sessions WHERE session_id=? │
│ - App validates:                                               │
│   ✓ is_active = TRUE                                          │
│   ✓ expires_at > NOW() UTC                                    │
│ - App extends session: UPDATE auth.sessions                   │
│   → last_activity_at = NOW() UTC                              │
│   → expires_at = NOW() UTC + 15 minutes                       │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 3. CCOW CONTEXT OPERATIONS                                     │
├────────────────────────────────────────────────────────────────┤
│ - App passes session_id via:                                   │
│   Option A: X-Session-ID header (med-z4)                      │
│   Option B: session_id cookie (med-z1)                        │
│ - CCOW validates session via same auth.sessions table         │
│ - CCOW performs context operation (set/get/clear patient)     │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 4. SESSION EXPIRATION / LOGOUT                                 │
├────────────────────────────────────────────────────────────────┤
│ Expiration (automatic):                                        │
│ - expires_at < NOW() UTC → Session invalid                    │
│ - Middleware/CCOW rejects requests with expired session       │
│                                                                │
│ Logout (explicit):                                             │
│ - UPDATE auth.sessions SET is_active=FALSE                    │
│ - Clear cookie in browser                                      │
│ - CCOW clears patient context for that user                   │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Schema

### 4.1 auth.sessions Table

```sql
CREATE TABLE auth.sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    last_activity_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    ip_address VARCHAR(45),  -- IPv4 or IPv6
    user_agent TEXT
);

-- Index for efficient session lookups
CREATE INDEX idx_sessions_user_id ON auth.sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON auth.sessions(expires_at);
CREATE INDEX idx_sessions_is_active ON auth.sessions(is_active) WHERE is_active = TRUE;
```

### 4.2 Session Cleanup

**Automated cleanup query:**

```sql
-- Delete expired sessions and inactive sessions older than 7 days
DELETE FROM auth.sessions
WHERE expires_at < (NOW() AT TIME ZONE 'UTC')
   OR (is_active = FALSE AND created_at < (NOW() AT TIME ZONE 'UTC') - INTERVAL '7 days');
```

**Cleanup schedule:**
- Med-z1: Run via periodic task (every hour)
- CCOW: Manual cleanup endpoint `/ccow/cleanup` (admin only)

---

## 5. Application Integration Patterns

### 5.1 med-z1 (Reference Implementation)

**Session Creation:**

```python
# app/db/auth.py
from datetime import datetime, timedelta, timezone

def create_session(user_id: str, ip_address: str = None, user_agent: str = None) -> str:
    """Create new session and return session_id."""
    timeout_minutes = 15  # From config
    now = datetime.now(timezone.utc)  # ✅ UTC
    expires_at = now + timedelta(minutes=timeout_minutes)

    query = text("""
        INSERT INTO auth.sessions (user_id, created_at, last_activity_at, expires_at, ip_address, user_agent)
        VALUES (:user_id, :created_at, :last_activity_at, :expires_at, :ip_address, :user_agent)
        RETURNING session_id
    """)

    result = conn.execute(query, {
        "user_id": user_id,
        "created_at": now,
        "last_activity_at": now,
        "expires_at": expires_at,
        "ip_address": ip_address,
        "user_agent": user_agent
    })

    return str(result.fetchone()[0])
```

**Session Validation:**

```python
# app/middleware/auth.py
from datetime import datetime, timezone

def validate_session(session_id: str) -> dict:
    """Validate session and return user info."""
    query = text("""
        SELECT session_id, user_id, expires_at, is_active
        FROM auth.sessions
        WHERE session_id = :session_id
    """)

    row = conn.execute(query, {"session_id": session_id}).fetchone()
    if not row:
        return None

    session_id, user_id, expires_at, is_active = row

    # Validate is_active
    if not is_active:
        return None

    # Validate expiration (handles both timezone-aware and naive)
    if expires_at.tzinfo is None:
        now = datetime.now()  # Graceful fallback for legacy data
    else:
        now = datetime.now(timezone.utc)  # ✅ UTC comparison

    if expires_at < now:
        return None

    return {"user_id": user_id, "session_id": session_id}
```

### 5.2 med-z4 Integration Pattern

**Directory Structure:**

```
med-z4/
├── app/
│   ├── db/
│   │   └── auth.py              # Copy from med-z1 (create_session, get_session)
│   ├── services/
│   │   └── ccow_service.py      # CCOW integration
│   └── main.py
└── config.py                     # DATABASE_URL points to same database
```

**Step 1: Copy Session Functions**

```python
# med-z4/app/db/auth.py
# Copy these functions from med-z1/app/db/auth.py:
# - create_session(user_id, ip_address, user_agent)
# - get_session(session_id)
# - extend_session(session_id)
# - invalidate_session(session_id)

# CRITICAL: Use identical timezone handling (datetime.now(timezone.utc))
```

**Step 2: Configure Database Connection**

```python
# med-z4/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# MUST point to same database as med-z1
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/medz1")

AUTH_CONFIG = {
    "session_timeout_minutes": 15,
    "session_cookie_name": "med_z4_session_id",  # ✅ Unique cookie name
}
```

**Step 3: Implement Login**

```python
# med-z4/app/routes/auth.py
from datetime import timedelta
from fastapi import APIRouter, Response
from app.db import auth as auth_db

router = APIRouter()

@router.post("/login")
async def login(response: Response, email: str, password: str):
    """Login and create session."""
    # 1. Validate credentials
    user = auth_db.validate_credentials(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    # 2. Create session (writes to shared auth.sessions table)
    session_id = auth_db.create_session(
        user_id=user["user_id"],
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # 3. Set cookie with med-z4-specific name
    response.set_cookie(
        key="med_z4_session_id",  # ✅ Unique cookie name
        value=session_id,
        httponly=True,
        max_age=15 * 60,  # 15 minutes
        samesite="lax"
    )

    return {"success": True, "user_id": user["user_id"]}
```

**Step 4: Implement CCOW Integration**

```python
# med-z4/app/services/ccow_service.py
import httpx
from fastapi import Request

CCOW_BASE_URL = "http://localhost:8001"

async def set_active_patient(request: Request, patient_id: str) -> bool:
    """
    Set active patient in CCOW vault using X-Session-ID header.

    Args:
        request: FastAPI request (to extract session cookie)
        patient_id: Patient ICN

    Returns:
        True if successful, False otherwise
    """
    # Extract med-z4's session ID from its cookie
    session_id = request.cookies.get("med_z4_session_id")
    if not session_id:
        return False

    # Call CCOW with X-Session-ID header
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{CCOW_BASE_URL}/ccow/active-patient",
                headers={"X-Session-ID": session_id},  # ✅ Pass session via header
                json={"patient_id": patient_id, "set_by": "med-z4"}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"CCOW set_active_patient failed: {e}")
            return False


async def get_active_patient(request: Request) -> dict:
    """Get active patient from CCOW vault."""
    session_id = request.cookies.get("med_z4_session_id")
    if not session_id:
        return None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CCOW_BASE_URL}/ccow/active-patient",
                headers={"X-Session-ID": session_id}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"CCOW get_active_patient failed: {e}")
            return None
```

### 5.3 Future Applications

**Checklist for New Apps:**

- [ ] Copy session management functions from med-z1 (`app/db/auth.py`)
- [ ] Use `datetime.now(timezone.utc)` for all timestamp operations
- [ ] Configure `DATABASE_URL` to point to shared database
- [ ] Use unique cookie name (e.g., `<app>_session_id`)
- [ ] Pass session via `X-Session-ID` header to CCOW
- [ ] Test timezone handling with expiration scenarios

---

## 6. CCOW Integration Requirements

### 6.1 Authentication Methods

CCOW Vault v2.1 supports two authentication methods:

| Method | When to Use | Example |
|--------|-------------|---------|
| **session_id cookie** | Browser-based apps (med-z1) | Cookie: `session_id=<uuid>` |
| **X-Session-ID header** | Service-to-service, external apps (med-z4) | Header: `X-Session-ID: <uuid>` |

### 6.2 Session Validation Flow

```
┌───────────────────────────────────────────────────────────────┐
│ Client Request to CCOW                                         │
│ - Header: X-Session-ID: abc123 (OR)                          │
│ - Cookie: session_id=abc123                                   │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────────┐
│ CCOW: Extract session_id                                      │
│ Priority: Header > Cookie                                     │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────────┐
│ CCOW: Query auth.sessions table                              │
│ SELECT user_id, expires_at, is_active                        │
│ WHERE session_id = 'abc123'                                  │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────────┐
│ CCOW: Validate Session                                        │
│ ✓ is_active = TRUE                                           │
│ ✓ expires_at > NOW() UTC                                     │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────────┐
│ CCOW: Perform Context Operation                              │
│ - Set active patient for user_id                             │
│ - Get active patient for user_id                             │
│ - Clear active patient for user_id                           │
└───────────────────────────────────────────────────────────────┘
```

### 6.3 Cross-Application Context Synchronization

**Scenario:** User logs into med-z1, then opens med-z4

```
Step 1: User logs into med-z1
- med-z1 creates session in auth.sessions
- med-z1 sets cookie: session_id=<uuid-A>

Step 2: User selects patient in med-z1
- med-z1 calls CCOW: PUT /ccow/active-patient (cookie auth)
- CCOW stores: user_id → patient_id mapping

Step 3: User opens med-z4 (separate tab, different cookie name)
- med-z4 requires separate login (different cookie name)
- med-z4 creates NEW session in auth.sessions
- med-z4 sets cookie: med_z4_session_id=<uuid-B>

Step 4: med-z4 queries CCOW for active patient
- med-z4 calls CCOW: GET /ccow/active-patient (X-Session-ID: <uuid-B>)
- CCOW validates <uuid-B>, extracts user_id
- CCOW returns patient_id for that user_id

Result: Both apps see same patient context (keyed by user_id)
```

**Key Point:** Different sessions (`uuid-A` vs `uuid-B`), same user, same patient context.

---

## 7. Testing and Validation

### 7.1 Timezone Validation Tests

**Test 1: Verify UTC Storage**

```python
# test_timezone_storage.py
from datetime import datetime, timezone
from app.db import auth as auth_db

def test_session_stores_utc():
    """Verify sessions are created with UTC timestamps."""
    # Create session
    session_id = auth_db.create_session(user_id="test-user-id")

    # Query raw database
    session = auth_db.get_session(session_id)

    # Verify expires_at is timezone-aware UTC
    assert session['expires_at'].tzinfo is not None
    assert session['expires_at'].tzinfo == timezone.utc

    print("✅ Session stored with UTC timezone")
```

**Test 2: Cross-Timezone Expiration**

```python
def test_session_expires_correctly():
    """Verify sessions expire correctly regardless of server timezone."""
    from datetime import timedelta

    # Create session with 1-second TTL
    now = datetime.now(timezone.utc)
    session_id = auth_db.create_session(user_id="test-user-id")

    # Immediately validate (should pass)
    session = auth_db.get_session(session_id)
    assert session is not None

    # Wait 2 seconds
    time.sleep(2)

    # Validate again (should fail - expired)
    session = auth_db.get_session(session_id)
    assert session is None

    print("✅ Session expiration works correctly")
```

### 7.2 Multi-Application Integration Tests

**Test 3: med-z1 → CCOW → med-z4**

```python
def test_cross_app_context_sync():
    """Verify patient context syncs across med-z1 and med-z4."""
    import httpx

    # 1. Login to med-z1
    response = httpx.post("http://localhost:8000/login", data={
        "email": "clinician.alpha@va.gov",
        "password": "VaDemo2025!"
    })
    med_z1_cookie = response.cookies["session_id"]

    # 2. Set patient in med-z1
    httpx.put(
        "http://localhost:8001/ccow/active-patient",
        cookies={"session_id": med_z1_cookie},
        json={"patient_id": "ICN100001", "set_by": "med-z1"}
    )

    # 3. Login to med-z4 (same user, different session)
    response = httpx.post("http://localhost:8002/login", data={
        "email": "clinician.alpha@va.gov",
        "password": "VaDemo2025!"
    })
    med_z4_session = response.cookies["med_z4_session_id"]

    # 4. Query CCOW from med-z4
    response = httpx.get(
        "http://localhost:8001/ccow/active-patient",
        headers={"X-Session-ID": med_z4_session}
    )

    # 5. Verify same patient context
    assert response.json()["patient_id"] == "ICN100001"

    print("✅ Patient context synced across med-z1 and med-z4")
```

### 7.3 Manual Testing Checklist

**For Each New Application:**

- [ ] Create session, verify `created_at` is UTC
- [ ] Wait 16 minutes, verify session expires (15 min TTL)
- [ ] Set patient in CCOW, verify context is stored
- [ ] Query CCOW from different app, verify context is retrieved
- [ ] Logout, verify session is marked `is_active=FALSE`
- [ ] Check `auth.sessions` table directly, verify UTC timestamps

---

## 8. Troubleshooting

### 8.1 Common Issues

**Issue 1: "Invalid or expired session" immediately after login**

**Cause:** Timezone mismatch between session creation and validation

**Diagnosis:**
```sql
-- Check sessions in database
SELECT
    session_id,
    created_at,
    expires_at,
    (expires_at - NOW() AT TIME ZONE 'UTC') AS time_until_expiry
FROM auth.sessions
WHERE user_id = '<your-user-id>'
ORDER BY created_at DESC
LIMIT 5;
```

**Fix:** Verify all `datetime.now()` calls use `datetime.now(timezone.utc)`

---

**Issue 2: Sessions not synchronized across med-z1 and med-z4**

**Cause:** Applications using different databases

**Diagnosis:**
```bash
# Check DATABASE_URL in each app
grep DATABASE_URL med-z1/.env
grep DATABASE_URL med-z4/.env

# Should point to same database
```

**Fix:** Ensure both apps use identical `DATABASE_URL`

---

**Issue 3: CCOW returns "Missing authentication" for med-z4**

**Cause:** med-z4 not passing session via header

**Diagnosis:**
```python
# Check CCOW request in med-z4
print(request.headers.get("X-Session-ID"))  # Should print UUID
print(request.cookies.get("med_z4_session_id"))  # Should print UUID
```

**Fix:** Ensure med-z4 extracts session from cookie and passes via header:

```python
session_id = request.cookies.get("med_z4_session_id")
headers = {"X-Session-ID": session_id}
```

---

**Issue 4: Timestamps displayed incorrectly in UI**

**Cause:** UI not converting UTC to user's local timezone

**Fix:** Convert in UI layer only:

```python
# Backend: Always return UTC
{
    "expires_at": "2026-01-27T14:30:00Z"  # ✅ ISO 8601 UTC
}

# Frontend (JavaScript): Convert to local
const utcDate = new Date("2026-01-27T14:30:00Z");
const localDate = utcDate.toLocaleString();  // "1/27/2026, 9:30:00 AM EST"
```

---

## 9. Summary Checklist

### For med-z1 (Reference Implementation) ✅

- [x] Import `timezone` from datetime
- [x] Use `datetime.now(timezone.utc)` for all timestamps
- [x] Session creation uses UTC
- [x] Session validation handles timezone-aware comparison
- [x] CCOW integration uses cookie-based auth

### For med-z4 (External Application)

- [ ] Copy session functions from med-z1 (`app/db/auth.py`)
- [ ] Configure `DATABASE_URL` to shared database
- [ ] Use unique cookie name (`med_z4_session_id`)
- [ ] Implement login with session creation
- [ ] Pass session to CCOW via `X-Session-ID` header
- [ ] Test cross-application context synchronization

### For All Applications

- [ ] Never use `datetime.now()` without `timezone.utc`
- [ ] Store all timestamps as UTC in database
- [ ] Convert to user's local timezone in UI only
- [ ] Validate session expiration using UTC comparison
- [ ] Test with sessions spanning midnight, DST changes

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-01-27 | Initial version - timezone fix and multi-app integration guide |

---

**End of Document**
