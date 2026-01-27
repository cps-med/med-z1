# CCOW Context Vault – Multi-User Enhancement Design

**Document Version:** v2.1.1
**Date:** 2026-01-27 (Updated)
**Original Date:** 2025-12-20
**Status:** ✅ IMPLEMENTATION COMPLETE (v2.1.1 - January 27, 2026)
**Parent Document:** `ccow-vault-design.md` (v1.1 baseline)

> ** Document Purpose**
> This document specifies the **v2.0 multi-user enhancement** to the CCOW Context Vault.
>
> **Prerequisites:** Read `ccow-vault-design.md` first to understand the baseline architecture (v1.1).
> That document covers foundational concepts (FastAPI patterns, threading, Pydantic models, core CCOW patterns).
>
> **This document focuses on:** The changes from v1.1 (single global context) → v2.0 (per-user context isolation).

---

> **Summary**
> This document specifies the enhancement of the CCOW Context Vault from a single global patient context to a **multi-user, per-user patient context** system. Each authenticated user will maintain their own active patient context, isolated from other users, while preserving context across login/logout cycles within med-z1 and supporting true multi-application CCOW synchronization.

> **✅ IMPLEMENTATION STATUS: COMPLETE (v2.1.1)**
> All planned features have been successfully implemented and tested.
> - **v2.0** (2025-12-20): Multi-user context isolation
> - **v2.1** (2026-01-27): Cross-application authentication (X-Session-ID header)
> - **v2.1.1** (2026-01-27): Timezone fix and session management standardization
>
> **Testing Guides:**
> - **CCOW v2.1 Testing:** See `docs/guide/ccow-v2.1-testing-guide.md`
> - **Session Integration:** See `docs/spec/session-timeout-behavior.md`
> - **Multi-App Integration:** See `docs/spec/timezone-and-session-management.md`
> - **med-z4 Quick Start:** See `docs/spec/med-z4-integration-quickstart.md`
>
> **Key Achievements:**
> - ✅ Per-user context isolation (multi-user support) - v2.0
> - ✅ Session-based authentication with PostgreSQL validation - v2.0
> - ✅ Context persistence across logout/login cycles - v2.0
> - ✅ History tracking (user/global scoping) - v2.0
> - ✅ X-Session-ID header authentication (cross-app) - v2.1
> - ✅ UTC timezone standardization (session management) - v2.1.1
> - ✅ All 7 route files updated - v2.0
> - ✅ 21 unit tests + 14 integration tests (comprehensive coverage) - v2.0
> - ✅ Manual testing successful with multiple users - v2.0
> - ✅ Cross-application testing (med-z1 ↔ CCOW ↔ med-z4) - v2.1

---

## Table of Contents

1. [Overview](#1-overview)
2. [Requirements and Goals](#2-requirements-and-goals)
3. [Architecture Changes](#3-architecture-changes)
4. [Data Model Updates](#4-data-model-updates)
5. [Vault Implementation Changes](#5-vault-implementation-changes)
6. [API Specification Updates](#6-api-specification-updates)
7. [Integration with med-z1 Authentication](#7-integration-with-med-z1-authentication)
8. [CCOW Client Updates](#8-ccow-client-updates)
9. [Migration Strategy](#9-migration-strategy)
10. [Testing Strategy](#10-testing-strategy)
11. [Security Considerations](#11-security-considerations)
12. [Future Enhancements](#12-future-enhancements)
13. [Implementation Checklist](#13-implementation-checklist)
14. [Cross-Application Authentication (v2.1)](#14-cross-application-authentication-v21-enhancement)
15. [Timezone and Session Management (v2.1.1)](#15-timezone-and-session-management-v21-enhancement)

---

## 1. Overview

### 1.1 Current State (Single Global Context)

The current CCOW vault implementation (v1.1) maintains a **single global active patient context** shared across all users and applications:

```python
# Current vault storage (in-memory)
_current: Optional[PatientContext] = None  # Single global context

# Current API behavior
GET  /ccow/active-patient  → Returns the one global patient
PUT  /ccow/active-patient  → Updates the one global patient
DELETE /ccow/active-patient → Clears the one global patient
```

**Problem:**
- Multiple clinicians using med-z1 simultaneously would overwrite each other's active patient
- Dr. Alice selects Patient P1 → Dr. Bob selects Patient P2 → Dr. Alice sees P2 (incorrect)
- Not suitable for multi-user production deployment

---

### 1.2 Target State (Multi-User Contexts)

The enhanced CCOW vault will maintain **per-user active patient contexts**, keyed by `user_id` from the authentication system:

```python
# Enhanced vault storage (in-memory)
_contexts: Dict[str, PatientContext] = {}  # Keyed by user_id

# Enhanced API behavior (user_id extracted from session)
GET  /ccow/active-patient  → Returns active patient for current user
PUT  /ccow/active-patient  → Updates active patient for current user
DELETE /ccow/active-patient → Clears active patient for current user
```

**Benefits:**
- Each clinician maintains independent patient context ✅
- Context persists across med-z1 login/logout cycles ✅
- True multi-application CCOW synchronization (med-z1, CPRS, imaging) ✅
- Production-ready multi-user support ✅

---

### 1.3 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Use `user_id` (not `session_id`) as context key** | Context should persist across med-z1 sessions and be shared with other CCOW-aware applications (CPRS, imaging). Using `session_id` would destroy context on logout. |
| **Keep context alive on med-z1 logout** | Logout from one application (med-z1) should not clear patient context for other applications (CPRS). Context is a **cross-application** concern, separate from individual app sessions. |
| **Auto-restore context on med-z1 login** | When user logs back into med-z1, dashboard should automatically load the active patient from CCOW vault (seamless user experience). |
| **Extract `user_id` from authenticated request** | Leverage existing `AuthMiddleware` that injects `request.state.user`. CCOW vault receives `user_id` via cookie-based session (no explicit passing in API calls). |
| **Breaking API change acceptable** | med-z1 is in development phase, not production. Clean break is better than maintaining backward compatibility. |
| **Session-scoped history by default** | Privacy-focused: users see only their own history by default, with admin override for global view. |

---

## 2. Requirements and Goals

### 2.1 Functional Requirements

**FR-1: Per-User Context Isolation**
Each authenticated user SHALL have an independent active patient context, identified by their `user_id` from `auth.users`.

**FR-2: Context Persistence Across Sessions**
A user's active patient context SHALL persist when they log out of med-z1 and SHALL be automatically restored when they log back in.

**FR-3: Multi-Application Context Sharing**
A user's active patient context SHALL be shared across all CCOW-aware applications (med-z1, CPRS, imaging, etc.) for the same `user_id`.

**FR-4: Session-Independent Context Lifecycle**
Logging out of med-z1 SHALL NOT clear the user's active patient context in the CCOW vault (preserves context for other applications).

**FR-5: User-Scoped History**
The vault SHALL maintain per-user context change history, with default API returning only the current user's history.

**FR-6: Admin/Debug Global History**
The vault SHALL support querying all users' context history via query parameter (e.g., `?scope=global`) for debugging and auditing.

**FR-7: Backward Compatibility (Breaking Change)**
The API SHALL change from global context to user-scoped context. Existing clients (med-z1 routes) SHALL be updated to pass `user_id`.

---

### 2.2 Non-Functional Requirements

**NFR-1: Thread Safety**
The vault SHALL remain thread-safe using existing locking mechanisms, now protecting a dictionary instead of a single value.

**NFR-2: Performance**
User context lookups SHALL complete in < 50ms (in-memory dictionary lookup, O(1) average case).

**NFR-3: Memory Management**
The vault SHALL implement automatic cleanup of stale user contexts (e.g., users inactive for > 24 hours) to prevent unbounded memory growth.

**NFR-4: Authentication Dependency**
The CCOW vault SHALL require valid user authentication (enforced by med-z1's `AuthMiddleware`). Unauthenticated requests SHALL NOT reach CCOW endpoints.

**NFR-5: Observability**
All context changes SHALL be logged with `user_id`, `patient_id`, and timestamp for audit and debugging.

---

### 2.3 Non-Goals (Out of Scope)

- ❌ Real-time push notifications (WebSocket/SSE) – Future enhancement
- ❌ Persistent storage (PostgreSQL/Redis) – Future enhancement
- ❌ Multi-session per user with independent contexts – Current design assumes single session enforcement
- ❌ Role-based access control (RBAC) for CCOW operations – All authenticated users have equal access
- ❌ Context expiration policies – Contexts remain until explicitly cleared (future: add TTL)

---

## 3. Architecture Changes

### 3.1 Current Architecture (v1.1)

```
┌─────────────────────────────────────────────────────────────┐
│                      CCOW Context Vault                      │
│                                                              │
│   ┌──────────────────────────────────────────────────┐     │
│   │  ContextVault (vault.py)                          │     │
│   │  ┌────────────────────────────────────────────┐  │     │
│   │  │  _current: Optional[PatientContext]        │  │     │
│   │  │    patient_id: "P1"                        │  │     │
│   │  │    set_by: "med-z1"                        │  │     │
│   │  │    set_at: "2025-12-20T10:00:00Z"          │  │     │
│   │  └────────────────────────────────────────────┘  │     │
│   │                                                    │     │
│   │  _history: deque[ContextHistoryEntry]            │     │
│   │    [10-20 recent events, all users mixed]        │     │
│   └──────────────────────────────────────────────────┘     │
│                                                              │
│   FastAPI Endpoints:                                        │
│   - GET  /ccow/active-patient  → Returns _current          │
│   - PUT  /ccow/active-patient  → Updates _current          │
│   - DELETE /ccow/active-patient → Clears _current          │
│   - GET  /ccow/history          → Returns _history         │
└─────────────────────────────────────────────────────────────┘

                              │
                              │ HTTP (no user context)
                              ▼

┌─────────────────────────────────────────────────────────────┐
│                      med-z1 Application                      │
│                                                              │
│   ccow_client.set_active_patient(patient_id, set_by)       │
│   (No user_id passed)                                       │
└─────────────────────────────────────────────────────────────┘
```

**Issues:**
- Single `_current` context shared by all users
- No user identification in vault
- History mixes all users' events

---

### 3.2 Enhanced Architecture (v2.0)

```
┌─────────────────────────────────────────────────────────────┐
│                      CCOW Context Vault                      │
│                                                              │
│   ┌──────────────────────────────────────────────────┐     │
│   │  ContextVault (vault.py)                          │     │
│   │  ┌────────────────────────────────────────────┐  │     │
│   │  │  _contexts: Dict[str, PatientContext]      │  │     │
│   │  │    {                                        │  │     │
│   │  │      "user_123": PatientContext(           │  │     │
│   │  │        user_id="user_123",                 │  │     │
│   │  │        patient_id="P1",                    │  │     │
│   │  │        set_by="med-z1"                     │  │     │
│   │  │      ),                                     │  │     │
│   │  │      "user_456": PatientContext(           │  │     │
│   │  │        user_id="user_456",                 │  │     │
│   │  │        patient_id="P2",                    │  │     │
│   │  │        set_by="cprs"                       │  │     │
│   │  │      )                                      │  │     │
│   │  │    }                                        │  │     │
│   │  └────────────────────────────────────────────┘  │     │
│   │                                                    │     │
│   │  _history: deque[ContextHistoryEntry]            │     │
│   │    [Events tagged with user_id for filtering]    │     │
│   └──────────────────────────────────────────────────┘     │
│                                                              │
│   FastAPI Endpoints (extract user_id from cookie):         │
│   - GET  /ccow/active-patient  → Returns _contexts[user_id]│
│   - PUT  /ccow/active-patient  → Updates _contexts[user_id]│
│   - DELETE /ccow/active-patient → Clears _contexts[user_id]│
│   - GET  /ccow/history?scope=user|global                   │
└─────────────────────────────────────────────────────────────┘

                              │
                              │ HTTP with session_id cookie
                              │ (CCOW extracts user_id from session)
                              ▼

┌─────────────────────────────────────────────────────────────┐
│                      med-z1 Application                      │
│                                                              │
│   AuthMiddleware:                                           │
│     - Validates session_id cookie                           │
│     - Queries auth.sessions → gets user_id                  │
│     - Injects request.state.user = {user_id, email, ...}   │
│                                                              │
│   CCOW Client (updated):                                    │
│     - Extracts user_id from request.state.user              │
│     - Makes HTTP call with session_id cookie                │
│     - CCOW vault extracts user_id from session              │
└─────────────────────────────────────────────────────────────┘
```

**Key Changes:**
1. ✅ Vault stores `Dict[user_id, PatientContext]` instead of single `_current`
2. ✅ CCOW endpoints extract `user_id` from session cookie (via med-z1 auth)
3. ✅ History entries tagged with `user_id` for filtering
4. ✅ Auto-cleanup of stale contexts (inactive users)

---

### 3.3 User Identification Flow

```
┌──────────┐                ┌───────────────┐              ┌──────────────┐
│  Browser │                │   med-z1 App  │              │  CCOW Vault  │
└────┬─────┘                └───────┬───────┘              └──────┬───────┘
     │                              │                             │
     │  1. Request with             │                             │
     │     session_id cookie        │                             │
     ├─────────────────────────────>│                             │
     │                              │                             │
     │  2. AuthMiddleware validates │                             │
     │     session_id cookie        │                             │
     │                              ├──────────────────────────>  │
     │                              │  Query auth.sessions        │
     │                              │<──────────────────────────┤ │
     │                              │  {user_id, email, ...}      │
     │                              │                             │
     │  3. Inject request.state.user│                             │
     │     = {user_id, ...}         │                             │
     │                              │                             │
     │  4. Route handler extracts   │                             │
     │     user_id from             │                             │
     │     request.state.user       │                             │
     │                              │                             │
     │  5. Call CCOW with           │                             │
     │     session_id cookie        │                             │
     │                              ├────────────────────────────>│
     │                              │  PUT /ccow/active-patient   │
     │                              │  Cookie: session_id=xyz     │
     │                              │  Body: {patient_id, set_by} │
     │                              │                             │
     │  6. CCOW validates session   │                             │
     │     cookie (same process)    │                             │
     │                              │<────────────────────────────┤
     │                              │  Extract user_id from       │
     │                              │  session_id cookie          │
     │                              │                             │
     │  7. Store context for user   │                             │
     │     _contexts[user_id] = ... │                             │
     │                              │                             │
```

**Critical Design Decision:**
CCOW vault will **NOT** trust user_id passed in request body. Instead, it will:
1. Receive `session_id` cookie from med-z1
2. Validate session against med-z1's `auth.sessions` table (or trust med-z1's validation)
3. Extract `user_id` from validated session
4. Use that `user_id` as the context key

**Security Implication:**
This prevents a malicious user from setting another user's context by forging `user_id` in the request body.

---

## 4. Data Model Updates

### 4.1 Updated PatientContext Model

**Current Model (v1.1):**
```python
# ccow/models.py

class PatientContext(BaseModel):
    """Represents the active patient context stored in the vault."""

    patient_id: str = Field(..., description="Canonical patient identifier (e.g., ICN)")
    set_by: str = Field(..., description="Application or source that set this context")
    set_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the context was last set",
    )
```

**Enhanced Model (v2.0):**
```python
# ccow/models.py

class PatientContext(BaseModel):
    """Represents the active patient context for a specific user."""

    # NEW: User identification
    user_id: str = Field(..., description="User UUID from auth.users.user_id")
    email: Optional[str] = Field(None, description="User email for display/debugging")

    # Existing fields (unchanged)
    patient_id: str = Field(..., description="Canonical patient identifier (e.g., ICN)")
    set_by: str = Field(..., description="Application or source that set this context")
    set_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the context was last set",
    )

    # NEW: Context lifecycle tracking
    last_accessed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last access (for cleanup)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "clinician.alpha@va.gov",
                "patient_id": "1012845331V153053",
                "set_by": "med-z1",
                "set_at": "2025-12-20T15:30:00.000Z",
                "last_accessed_at": "2025-12-20T15:45:00.000Z"
            }
        }
```

**Changes:**
- ✅ Added `user_id` (required) - Key for context isolation
- ✅ Added `email` (optional) - For debugging/audit trails
- ✅ Added `last_accessed_at` - For stale context cleanup
- ✅ Updated example to show multi-user scenario

---

### 4.2 Updated Request Models

**SetPatientContextRequest (v2.0):**
```python
# ccow/models.py

class SetPatientContextRequest(BaseModel):
    """Request body for setting the active patient context."""

    patient_id: str = Field(..., min_length=1, description="Patient identifier (ICN)")
    set_by: str = Field(
        default="med-z1",
        min_length=1,
        description="Application name setting the context",
    )

    # NOTE: user_id is NOT in request body - extracted from session cookie
    # This prevents user_id spoofing attacks
```

**ClearPatientContextRequest (v2.0):**
```python
# ccow/models.py

class ClearPatientContextRequest(BaseModel):
    """Optional request body for clearing context with metadata."""

    cleared_by: Optional[str] = Field(
        default=None,
        description="Application name clearing the context",
    )

    # NOTE: user_id extracted from session, not request body
```

**No changes needed** - `user_id` comes from authentication, not request body.

---

### 4.3 Updated History Model

**Enhanced ContextHistoryEntry (v2.0):**
```python
# ccow/models.py

class ContextHistoryEntry(BaseModel):
    """Represents a historical context change event."""

    action: Literal["set", "clear"] = Field(
        ...,
        description="Type of action performed: 'set' or 'clear'",
    )

    # NEW: User identification for filtering
    user_id: str = Field(
        ...,
        description="User UUID who performed the action",
    )
    email: Optional[str] = Field(
        None,
        description="User email for display (optional)",
    )

    # Existing fields (unchanged)
    patient_id: Optional[str] = Field(
        default=None,
        description="Patient identifier (None if context was cleared)",
    )
    actor: str = Field(
        ...,
        description="Application that performed the action (e.g., 'med-z1', 'cprs')",
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of the action",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "action": "set",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "clinician.alpha@va.gov",
                "patient_id": "1012845331V153053",
                "actor": "med-z1",
                "timestamp": "2025-12-20T15:30:00.000Z"
            }
        }
```

**Changes:**
- ✅ Added `user_id` (required) - Enable user-scoped history filtering
- ✅ Added `email` (optional) - For display in admin views
- ✅ Updated example to show user context

---

### 4.4 New Response Models

**GetActivePatientResponse (v2.0):**
```python
# ccow/models.py

class GetActivePatientResponse(BaseModel):
    """Response for GET /ccow/active-patient - returns current user's context."""

    user_id: str = Field(..., description="User UUID")
    email: Optional[str] = Field(None, description="User email")
    patient_id: str = Field(..., description="Active patient ICN")
    set_by: str = Field(..., description="Application that set context")
    set_at: datetime = Field(..., description="When context was set")
    last_accessed_at: datetime = Field(..., description="Last access timestamp")
```

**GetAllActiveContextsResponse (v2.0 - NEW):**
```python
# ccow/models.py

class GetAllActiveContextsResponse(BaseModel):
    """Response for GET /ccow/active-patients (admin/debugging)."""

    contexts: List[PatientContext] = Field(
        ...,
        description="All active user contexts"
    )
    total_count: int = Field(..., description="Number of active contexts")

    class Config:
        json_schema_extra = {
            "example": {
                "contexts": [
                    {
                        "user_id": "user_123",
                        "email": "clinician.alpha@va.gov",
                        "patient_id": "P1",
                        "set_by": "med-z1",
                        "set_at": "2025-12-20T10:00:00Z",
                        "last_accessed_at": "2025-12-20T10:30:00Z"
                    },
                    {
                        "user_id": "user_456",
                        "email": "clinician.bravo@va.gov",
                        "patient_id": "P2",
                        "set_by": "cprs",
                        "set_at": "2025-12-20T09:45:00Z",
                        "last_accessed_at": "2025-12-20T10:15:00Z"
                    }
                ],
                "total_count": 2
            }
        }
```

**GetHistoryResponse (v2.0 - Enhanced):**
```python
# ccow/models.py

class GetHistoryResponse(BaseModel):
    """Response for GET /ccow/history with scope filtering."""

    history: List[ContextHistoryEntry] = Field(..., description="Context change events")
    scope: Literal["session", "user", "global"] = Field(
        ...,
        description="Scope of history returned"
    )
    total_count: int = Field(..., description="Number of events returned")
    user_id: Optional[str] = Field(
        None,
        description="User ID if scope=session or scope=user"
    )
```

---

## 5. Vault Implementation Changes

### 5.1 Current Vault Implementation (v1.1)

```python
# ccow/vault.py (current)

import threading
from collections import deque
from datetime import datetime, timezone
from typing import Optional

from .models import PatientContext, ContextHistoryEntry


class ContextVault:
    """Thread-safe in-memory vault for active patient context."""

    def __init__(self, max_history: int = 20):
        self._lock = threading.Lock()
        self._current: Optional[PatientContext] = None  # Single global context
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
        """Clear the active patient context."""
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


# Global singleton instance
vault = ContextVault(max_history=20)
```

---

### 5.2 Enhanced Vault Implementation (v2.0)

```python
# ccow/vault.py (enhanced)

import threading
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List

from .models import PatientContext, ContextHistoryEntry


class ContextVault:
    """
    Thread-safe in-memory vault for per-user active patient contexts.

    Each user (identified by user_id from auth.users) maintains an independent
    active patient context. Contexts persist across med-z1 login/logout cycles
    and are shared across CCOW-aware applications (med-z1, CPRS, imaging).

    Key Design Choices:
    - user_id (not session_id) as key: Context survives app logout
    - Auto-cleanup of stale contexts: Prevent unbounded memory growth
    - User-scoped history: Privacy-focused, with admin override
    """

    def __init__(self, max_history: int = 100, cleanup_threshold_hours: int = 24):
        """
        Initialize the vault.

        Args:
            max_history: Maximum number of history entries to retain (default 100)
            cleanup_threshold_hours: Remove contexts inactive for this many hours (default 24)
        """
        self._lock = threading.Lock()

        # Core storage: user_id -> PatientContext
        self._contexts: Dict[str, PatientContext] = {}

        # History: All events from all users (tagged with user_id for filtering)
        self._history: deque[ContextHistoryEntry] = deque(maxlen=max_history)

        # Configuration
        self._cleanup_threshold = timedelta(hours=cleanup_threshold_hours)

    # -------------------------------------------------------------------------
    # Core Context Operations
    # -------------------------------------------------------------------------

    def get_context(self, user_id: str) -> Optional[PatientContext]:
        """
        Retrieve the active patient context for a specific user.

        Args:
            user_id: User UUID from auth.users.user_id

        Returns:
            PatientContext if user has active context, None otherwise
        """
        with self._lock:
            context = self._contexts.get(user_id)
            if context:
                # Update last_accessed_at (for cleanup logic)
                context.last_accessed_at = datetime.now(timezone.utc)
            return context

    def set_context(
        self,
        user_id: str,
        patient_id: str,
        set_by: str,
        email: Optional[str] = None
    ) -> PatientContext:
        """
        Set the active patient context for a specific user.

        Args:
            user_id: User UUID from auth.users.user_id
            patient_id: Patient ICN
            set_by: Application name (e.g., 'med-z1', 'cprs')
            email: User email for display/debugging (optional)

        Returns:
            The created PatientContext
        """
        with self._lock:
            now = datetime.now(timezone.utc)

            context = PatientContext(
                user_id=user_id,
                email=email,
                patient_id=patient_id,
                set_by=set_by,
                set_at=now,
                last_accessed_at=now,
            )

            # Store context for this user
            self._contexts[user_id] = context

            # Record in history
            self._history.append(
                ContextHistoryEntry(
                    action="set",
                    user_id=user_id,
                    email=email,
                    patient_id=patient_id,
                    actor=set_by,
                    timestamp=now,
                )
            )

            return context

    def clear_context(
        self,
        user_id: str,
        cleared_by: Optional[str] = None,
        email: Optional[str] = None
    ) -> bool:
        """
        Clear the active patient context for a specific user.

        Args:
            user_id: User UUID from auth.users.user_id
            cleared_by: Application name that cleared context (optional)
            email: User email for audit trail (optional)

        Returns:
            True if context was cleared, False if no context existed
        """
        with self._lock:
            if user_id not in self._contexts:
                return False

            # Remove context for this user
            del self._contexts[user_id]

            # Record in history
            self._history.append(
                ContextHistoryEntry(
                    action="clear",
                    user_id=user_id,
                    email=email,
                    patient_id=None,
                    actor=cleared_by or "unknown",
                    timestamp=datetime.now(timezone.utc),
                )
            )

            return True

    # -------------------------------------------------------------------------
    # History Operations
    # -------------------------------------------------------------------------

    def get_history(
        self,
        user_id: Optional[str] = None,
        scope: str = "user"
    ) -> List[ContextHistoryEntry]:
        """
        Retrieve context change history, optionally filtered by user.

        Args:
            user_id: User UUID to filter by (required if scope='user')
            scope: Scope of history to return:
                - 'user': Only events for specified user_id
                - 'global': All events from all users

        Returns:
            List of ContextHistoryEntry objects (most recent first)
        """
        with self._lock:
            if scope == "global":
                # Return all history
                return list(self._history)
            elif scope == "user":
                # Filter history for specific user
                if not user_id:
                    raise ValueError("user_id required for scope='user'")
                return [
                    entry for entry in self._history
                    if entry.user_id == user_id
                ]
            else:
                raise ValueError(f"Invalid scope: {scope}. Must be 'user' or 'global'")

    # -------------------------------------------------------------------------
    # Admin / Debugging Operations
    # -------------------------------------------------------------------------

    def get_all_contexts(self) -> List[PatientContext]:
        """
        Retrieve all active user contexts (admin/debugging).

        Returns:
            List of all PatientContext objects
        """
        with self._lock:
            return list(self._contexts.values())

    def get_context_count(self) -> int:
        """Get the number of active user contexts."""
        with self._lock:
            return len(self._contexts)

    # -------------------------------------------------------------------------
    # Cleanup Operations
    # -------------------------------------------------------------------------

    def cleanup_stale_contexts(self) -> int:
        """
        Remove contexts that haven't been accessed in cleanup_threshold_hours.

        This prevents unbounded memory growth from users who never explicitly
        clear their context.

        Returns:
            Number of contexts removed
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            stale_threshold = now - self._cleanup_threshold

            # Find stale user_ids
            stale_user_ids = [
                user_id for user_id, ctx in self._contexts.items()
                if ctx.last_accessed_at < stale_threshold
            ]

            # Remove stale contexts
            for user_id in stale_user_ids:
                context = self._contexts[user_id]
                del self._contexts[user_id]

                # Log cleanup in history
                self._history.append(
                    ContextHistoryEntry(
                        action="clear",
                        user_id=user_id,
                        email=context.email,
                        patient_id=None,
                        actor="system:cleanup",
                        timestamp=now,
                    )
                )

            return len(stale_user_ids)


# Global singleton instance
vault = ContextVault(max_history=100, cleanup_threshold_hours=24)
```

**Key Changes:**
1. ✅ `_contexts: Dict[str, PatientContext]` replaces `_current`
2. ✅ All methods take `user_id` parameter
3. ✅ `get_history()` supports user-scoped and global filtering
4. ✅ `cleanup_stale_contexts()` prevents memory leaks
5. ✅ `get_all_contexts()` for admin/debugging
6. ✅ Increased default `max_history` from 20 to 100 (multi-user scenario)

---

## 6. API Specification Updates

### 6.1 Authentication Flow for CCOW Endpoints

All CCOW endpoints will require authentication via `session_id` cookie:

```
1. Browser sends request to CCOW endpoint with session_id cookie
2. CCOW vault validates session (calls med-z1 auth or trusts reverse proxy)
3. CCOW extracts user_id from validated session
4. CCOW performs operation for that user_id
```

**Implementation Options:**

**Option A: CCOW validates session directly** (Recommended)
- CCOW imports `app.db.auth.get_session()` and validates session_id
- Pro: Independent, no external dependency
- Con: Tight coupling with med-z1 auth schema

**Option B: CCOW trusts med-z1 middleware** (Simpler)
- med-z1 acts as reverse proxy, validates session before forwarding to CCOW
- Adds `X-User-ID` header to CCOW requests
- Pro: Loose coupling, CCOW doesn't need DB access
- Con: Requires reverse proxy setup

**Recommendation: Option A for initial implementation** (CCOW validates session directly)

---

### 6.2 Updated Endpoints

#### 6.2.1 GET /ccow/active-patient

**Description:** Get the active patient context for the authenticated user.

**Authentication:** Required (session_id cookie)

**Request:**
```http
GET /ccow/active-patient HTTP/1.1
Cookie: session_id=abc123-def456-...
```

**Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "clinician.alpha@va.gov",
  "patient_id": "1012845331V153053",
  "set_by": "med-z1",
  "set_at": "2025-12-20T15:30:00.000Z",
  "last_accessed_at": "2025-12-20T15:45:00.000Z"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "No active patient context for user"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or missing session"
}
```

**Example (curl):**
```bash
curl -X GET http://localhost:8001/ccow/active-patient \
  --cookie "session_id=abc123-def456-..."
```

---

#### 6.2.2 PUT /ccow/active-patient

**Description:** Set or update the active patient context for the authenticated user.

**Authentication:** Required (session_id cookie)

**Request:**
```http
PUT /ccow/active-patient HTTP/1.1
Cookie: session_id=abc123-def456-...
Content-Type: application/json

{
  "patient_id": "1012845331V153053",
  "set_by": "med-z1"
}
```

**Note:** `user_id` is NOT in the request body - it's extracted from the session cookie.

**Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "clinician.alpha@va.gov",
  "patient_id": "1012845331V153053",
  "set_by": "med-z1",
  "set_at": "2025-12-20T15:30:00.000Z",
  "last_accessed_at": "2025-12-20T15:30:00.000Z"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or missing session"
}
```

**Example (curl):**
```bash
curl -X PUT http://localhost:8001/ccow/active-patient \
  --cookie "session_id=abc123-def456-..." \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "1012845331V153053", "set_by": "med-z1"}'
```

---

#### 6.2.3 DELETE /ccow/active-patient

**Description:** Clear the active patient context for the authenticated user.

**Authentication:** Required (session_id cookie)

**Request:**
```http
DELETE /ccow/active-patient HTTP/1.1
Cookie: session_id=abc123-def456-...
Content-Type: application/json

{
  "cleared_by": "med-z1"
}
```

**Response (204 No Content):**
(Empty response body)

**Response (404 Not Found):**
```json
{
  "detail": "No active patient context to clear"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or missing session"
}
```

**Example (curl):**
```bash
curl -X DELETE http://localhost:8001/ccow/active-patient \
  --cookie "session_id=abc123-def456-..." \
  -H "Content-Type: application/json" \
  -d '{"cleared_by": "med-z1"}'
```

---

#### 6.2.4 GET /ccow/history

**Description:** Get context change history, filtered by scope.

**Authentication:** Required (session_id cookie)

**Query Parameters:**
- `scope` (optional, default: `user`): Scope of history to return
  - `user`: Only events for authenticated user
  - `global`: All events from all users (admin/debugging)

**Request:**
```http
GET /ccow/history?scope=user HTTP/1.1
Cookie: session_id=abc123-def456-...
```

**Response (200 OK):**
```json
{
  "history": [
    {
      "action": "set",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "clinician.alpha@va.gov",
      "patient_id": "1012845331V153053",
      "actor": "med-z1",
      "timestamp": "2025-12-20T15:30:00.000Z"
    },
    {
      "action": "clear",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "clinician.alpha@va.gov",
      "patient_id": null,
      "actor": "med-z1",
      "timestamp": "2025-12-20T14:20:00.000Z"
    }
  ],
  "scope": "user",
  "total_count": 2,
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Example (curl):**
```bash
# User-scoped history (default)
curl -X GET "http://localhost:8001/ccow/history?scope=user" \
  --cookie "session_id=abc123-def456-..."

# Global history (all users)
curl -X GET "http://localhost:8001/ccow/history?scope=global" \
  --cookie "session_id=abc123-def456-..."
```

---

#### 6.2.5 GET /ccow/active-patients (NEW)

**Description:** Get all active patient contexts across all users (admin/debugging).

**Authentication:** Required (session_id cookie)

**Request:**
```http
GET /ccow/active-patients HTTP/1.1
Cookie: session_id=abc123-def456-...
```

**Response (200 OK):**
```json
{
  "contexts": [
    {
      "user_id": "123e4567-...",
      "email": "clinician.alpha@va.gov",
      "patient_id": "1012845331V153053",
      "set_by": "med-z1",
      "set_at": "2025-12-20T10:00:00.000Z",
      "last_accessed_at": "2025-12-20T10:30:00.000Z"
    },
    {
      "user_id": "456e7890-...",
      "email": "clinician.bravo@va.gov",
      "patient_id": "1013012345V678901",
      "set_by": "cprs",
      "set_at": "2025-12-20T09:45:00.000Z",
      "last_accessed_at": "2025-12-20T10:15:00.000Z"
    }
  ],
  "total_count": 2
}
```

**Example (curl):**
```bash
curl -X GET http://localhost:8001/ccow/active-patients \
  --cookie "session_id=abc123-def456-..."
```

---

#### 6.2.6 POST /ccow/cleanup (NEW)

**Description:** Trigger manual cleanup of stale contexts (admin/debugging).

**Authentication:** Required (session_id cookie)

**Request:**
```http
POST /ccow/cleanup HTTP/1.1
Cookie: session_id=abc123-def456-...
```

**Response (200 OK):**
```json
{
  "removed_count": 3,
  "message": "Cleaned up 3 stale contexts"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8001/ccow/cleanup \
  --cookie "session_id=abc123-def456-..."
```

---

### 6.3 API Summary Table

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/ccow/active-patient` | GET | ✅ | Get current user's active patient |
| `/ccow/active-patient` | PUT | ✅ | Set current user's active patient |
| `/ccow/active-patient` | DELETE | ✅ | Clear current user's active patient |
| `/ccow/history?scope=user\|global` | GET | ✅ | Get context change history |
| `/ccow/active-patients` | GET | ✅ | Get all active contexts (admin) |
| `/ccow/cleanup` | POST | ✅ | Trigger stale context cleanup (admin) |
| `/ccow/health` | GET | ❌ | Health check (unchanged) |
| `/` | GET | ❌ | Service info (unchanged) |

---

## 7. Integration with med-z1 Authentication

### 7.1 Session Validation in CCOW

CCOW vault needs to validate the `session_id` cookie and extract `user_id`. Two implementation approaches:

#### Approach A: Direct Database Access (Recommended)

**CCOW imports med-z1's auth module:**

```python
# ccow/auth_helper.py (NEW)

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)


def get_user_from_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Validate session and retrieve user information.

    Args:
        session_id: Session UUID from cookie

    Returns:
        Dictionary with user info, or None if session invalid
    """
    query = text("""
        SELECT
            s.user_id,
            s.is_active,
            s.expires_at,
            u.email,
            u.display_name
        FROM auth.sessions s
        JOIN auth.users u ON s.user_id = u.user_id
        WHERE s.session_id = CAST(:session_id AS UUID)
        LIMIT 1
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"session_id": session_id})
            row = result.fetchone()

            if not row:
                return None

            # Validate session
            if not row[1]:  # is_active
                logger.warning(f"Session {session_id} is not active")
                return None

            if row[2] < datetime.now():  # expires_at
                logger.warning(f"Session {session_id} has expired")
                return None

            return {
                "user_id": str(row[0]),
                "email": row[3],
                "display_name": row[4],
            }

    except Exception as e:
        logger.error(f"Error validating session {session_id}: {e}")
        return None
```

**Use in CCOW endpoints:**

```python
# ccow/main.py (updated)

from fastapi import Request, HTTPException, status
from .auth_helper import get_user_from_session


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to extract and validate user from session cookie.

    Raises:
        HTTPException(401) if session invalid or missing
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session cookie"
        )

    user = get_user_from_session(session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return user


@app.get("/ccow/active-patient", response_model=PatientContext)
async def get_active_patient(user: Dict = Depends(get_current_user)):
    """Get the current user's active patient context."""
    context = vault.get_context(user["user_id"])
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context for user",
        )
    return context


@app.put("/ccow/active-patient", response_model=PatientContext)
async def set_active_patient(
    request: SetPatientContextRequest,
    user: Dict = Depends(get_current_user)
):
    """Set the current user's active patient context."""
    context = vault.set_context(
        user_id=user["user_id"],
        patient_id=request.patient_id,
        set_by=request.set_by,
        email=user.get("email"),
    )
    return context
```

**Pros:**
- ✅ CCOW can run independently (no reverse proxy needed)
- ✅ Direct session validation (authoritative)
- ✅ Consistent with med-z1 auth patterns

**Cons:**
- ⚠️ CCOW depends on med-z1 database schema
- ⚠️ Code duplication (session validation logic)

---

#### Approach B: Trust med-z1 Middleware (Alternative)

**med-z1 acts as reverse proxy:**

```python
# app/middleware/ccow_proxy.py (NEW)

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import httpx


class CCOWProxyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate session and forward to CCOW with X-User-ID header.
    """

    async def dispatch(self, request: Request, call_next):
        # Only proxy /ccow/* routes
        if not request.url.path.startswith("/ccow/"):
            return await call_next(request)

        # Session already validated by AuthMiddleware
        if not hasattr(request.state, "user"):
            return Response(status_code=401, content="Unauthorized")

        # Forward to CCOW with user_id header
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"http://localhost:8001{request.url.path}",
                headers={
                    **request.headers,
                    "X-User-ID": request.state.user["user_id"],
                    "X-User-Email": request.state.user["email"],
                },
                content=await request.body(),
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response.headers,
            )
```

**CCOW trusts X-User-ID header:**

```python
# ccow/main.py (alternative)

@app.get("/ccow/active-patient")
async def get_active_patient(request: Request):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user identification")

    context = vault.get_context(user_id)
    # ...
```

**Pros:**
- ✅ Loose coupling (CCOW doesn't need DB access)
- ✅ Single point of auth validation (med-z1)

**Cons:**
- ⚠️ CCOW can't run standalone (requires med-z1 proxy)
- ⚠️ Less secure (trusts HTTP headers)
- ⚠️ More complex deployment

---

**Recommendation: Use Approach A (Direct Database Access)** for initial implementation.

---

### 7.2 med-z1 Route Updates

Update med-z1 routes to work with user-scoped CCOW:

```python
# app/routes/patient.py (updated)

from fastapi import APIRouter, Request, HTTPException
from app.utils.ccow_client import ccow_client
from app.templates import templates

router = APIRouter()


@router.get("/patient/{icn}")
async def patient_overview(icn: str, request: Request):
    """Patient overview page - sets active patient in CCOW."""

    # request.state.user injected by AuthMiddleware
    user = request.state.user

    # Fetch patient data (existing logic)
    patient = get_patient_data(icn)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Set active patient in CCOW (automatic user_id extraction via cookie)
    # No explicit user_id needed - session cookie carries it
    ccow_client.set_active_patient(
        patient_id=icn,
        set_by="med-z1"
    )

    # Render template
    return templates.TemplateResponse(
        "patient_overview.html",
        {
            "request": request,
            "patient": patient,
            "user": user,  # Available for display
        },
    )


@router.get("/")
async def dashboard(request: Request):
    """Dashboard - restores active patient from CCOW if available."""

    user = request.state.user

    # Try to get active patient from CCOW (auto user_id from cookie)
    active_patient_icn = ccow_client.get_active_patient()

    active_patient = None
    if active_patient_icn:
        active_patient = get_patient_data(active_patient_icn)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "active_patient": active_patient,  # May be None
        },
    )
```

**Key Change:** Routes no longer need to explicitly pass `user_id` - it's carried by the `session_id` cookie.

---

## 8. CCOW Client Updates

### 8.1 Current CCOW Client (v1.1)

```python
# app/utils/ccow_client.py (current)

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
        """Notify CCOW vault of an active patient change."""
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
        """Retrieve the current patient_id from CCOW."""
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
        """Clear the active patient context in CCOW."""
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


# Global client instance
ccow_client = CCOWClient()
```

---

### 8.2 Enhanced CCOW Client (v2.0)

The client needs to **pass session cookies** to CCOW endpoints. Two approaches:

#### Option A: Pass Request Object (Recommended)

```python
# app/utils/ccow_client.py (enhanced v2.0)

import logging
from typing import Optional, Dict, Any
import requests
from fastapi import Request
from config import CCOW_ENABLED, CCOW_URL

logger = logging.getLogger(__name__)


class CCOWClient:
    """
    HTTP client for interacting with the CCOW Context Vault.

    v2.0 changes:
    - Accepts Request object to forward session cookies
    - CCOW extracts user_id from session (no explicit passing)
    - Returns full context objects (not just patient_id)
    """

    def __init__(self, base_url: str = CCOW_URL, enabled: bool = CCOW_ENABLED):
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled

    def set_active_patient(
        self,
        request: Request,
        patient_id: str,
        set_by: str = "med-z1"
    ) -> bool:
        """
        Set the active patient context for the current user.

        Args:
            request: FastAPI Request object (contains session cookie)
            patient_id: Patient ICN
            set_by: Application name (default: "med-z1")

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("CCOW is disabled; skipping set_active_patient call")
            return False

        try:
            # Extract session cookie from request
            session_id = request.cookies.get("session_id")
            if not session_id:
                logger.error("No session_id cookie found in request")
                return False

            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={"patient_id": patient_id, "set_by": set_by},
                cookies={"session_id": session_id},  # Forward session cookie
                timeout=2.0,
            )
            response.raise_for_status()

            user_email = request.state.user.get("email", "unknown")
            logger.info(
                "Set CCOW active patient context to %s for user %s",
                patient_id,
                user_email
            )
            return True

        except requests.RequestException as exc:
            logger.error("Failed to set CCOW context: %s", exc)
            return False

    def get_active_patient(self, request: Request) -> Optional[str]:
        """
        Retrieve the current user's active patient ICN from CCOW.

        Args:
            request: FastAPI Request object (contains session cookie)

        Returns:
            Patient ICN if context exists, None otherwise
        """
        if not self.enabled:
            return None

        try:
            session_id = request.cookies.get("session_id")
            if not session_id:
                logger.error("No session_id cookie found in request")
                return None

            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                cookies={"session_id": session_id},
                timeout=2.0,
            )

            if response.status_code == 404:
                return None  # No active context for this user

            response.raise_for_status()
            data = response.json()
            return data.get("patient_id")

        except requests.RequestException as exc:
            logger.error("Failed to get CCOW context: %s", exc)
            return None

    def get_active_patient_context(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Retrieve the full active patient context (including metadata).

        Args:
            request: FastAPI Request object (contains session cookie)

        Returns:
            Full PatientContext dict if exists, None otherwise
        """
        if not self.enabled:
            return None

        try:
            session_id = request.cookies.get("session_id")
            if not session_id:
                return None

            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                cookies={"session_id": session_id},
                timeout=2.0,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            logger.error("Failed to get CCOW context: %s", exc)
            return None

    def clear_active_patient(
        self,
        request: Request,
        cleared_by: str = "med-z1"
    ) -> bool:
        """
        Clear the active patient context for the current user.

        Args:
            request: FastAPI Request object (contains session cookie)
            cleared_by: Application name (default: "med-z1")

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            session_id = request.cookies.get("session_id")
            if not session_id:
                logger.error("No session_id cookie found in request")
                return False

            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by},
                cookies={"session_id": session_id},
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


# Global client instance
ccow_client = CCOWClient()
```

**Usage in routes:**

```python
# app/routes/patient.py

@router.get("/patient/{icn}")
async def patient_overview(icn: str, request: Request):
    # Pass request object to CCOW client
    ccow_client.set_active_patient(request, patient_id=icn, set_by="med-z1")
    # ...

@router.get("/")
async def dashboard(request: Request):
    # Pass request object to get active patient
    active_patient_icn = ccow_client.get_active_patient(request)
    # ...
```

**Pros:**
- ✅ Clean API (no explicit user_id passing)
- ✅ Secure (uses same session cookie as med-z1)
- ✅ Simple to implement

**Cons:**
- ⚠️ Requires passing `request` object to all CCOW client calls

---

#### Option B: Session Manager Class (Alternative)

```python
# app/utils/ccow_client.py (alternative)

class CCOWSession:
    """User-specific CCOW session bound to a Request."""

    def __init__(self, request: Request, client: CCOWClient):
        self.request = request
        self.client = client

    def set_active_patient(self, patient_id: str, set_by: str = "med-z1") -> bool:
        return self.client._set(self.request, patient_id, set_by)

    def get_active_patient(self) -> Optional[str]:
        return self.client._get(self.request)


class CCOWClient:
    # ...

    def for_request(self, request: Request) -> CCOWSession:
        """Create a session-bound CCOW client."""
        return CCOWSession(request, self)


# Usage
@router.get("/patient/{icn}")
async def patient_overview(icn: str, request: Request):
    ccow = ccow_client.for_request(request)
    ccow.set_active_patient(icn)
```

**Pros:**
- ✅ Cleaner call sites (no request parameter)

**Cons:**
- ⚠️ More complex implementation
- ⚠️ Less explicit

---

**Recommendation: Use Option A (Pass Request Object)** - simpler and more explicit.

---

## 9. Migration Strategy

### 9.1 Breaking Changes

The v2.0 enhancement introduces **breaking API changes**:

| Component | v1.1 (Current) | v2.0 (Enhanced) | Breaking? |
|-----------|----------------|-----------------|-----------|
| **Vault Storage** | `_current: Optional[PatientContext]` | `_contexts: Dict[str, PatientContext]` | ✅ Yes |
| **API Endpoints** | Global context (no user_id) | User-scoped context (user_id from session) | ✅ Yes |
| **CCOW Client** | `set_active_patient(patient_id, set_by)` | `set_active_patient(request, patient_id, set_by)` | ✅ Yes |
| **Request Model** | No authentication required | Session cookie required | ✅ Yes |

**Impact:**
- All med-z1 routes calling CCOW client must be updated
- CCOW vault cannot be hot-swapped (requires restart)
- No backward compatibility with v1.1 API

---

### 9.2 Migration Steps

Since med-z1 is in development (not production), use a **clean break** migration:

#### Step 1: Update CCOW Vault

```bash
# 1. Stop CCOW service
pkill -f "uvicorn ccow.main"

# 2. Update code files
#    - ccow/models.py (add user_id, email, last_accessed_at)
#    - ccow/vault.py (change to dict-based storage)
#    - ccow/main.py (add session validation, update endpoints)
#    - ccow/auth_helper.py (NEW - session validation)

# 3. Restart CCOW service
uvicorn ccow.main:app --reload --port 8001
```

#### Step 2: Update CCOW Client

```bash
# 1. Update app/utils/ccow_client.py (pass request object)

# 2. Verify configuration (no changes needed)
grep CCOW .env
```

#### Step 3: Update med-z1 Routes

```bash
# Update all route files that call CCOW client:
#   - app/routes/patient.py
#   - app/routes/dashboard.py
#   - app/routes/demographics.py
#   - app/routes/vitals.py
#   - app/routes/medications.py
#   - app/routes/allergies.py
#   - app/routes/encounters.py
#   - app/routes/labs.py

# Pattern:
# OLD: ccow_client.set_active_patient(patient_id, "med-z1")
# NEW: ccow_client.set_active_patient(request, patient_id, "med-z1")
```

#### Step 4: Test

```bash
# 1. Start CCOW service
uvicorn ccow.main:app --reload --port 8001

# 2. Start med-z1 app
uvicorn app.main:app --reload --port 8000

# 3. Run manual tests (see Section 10)
```

---

### 9.3 Rollback Plan

If issues arise, rollback to v1.1:

```bash
# 1. Stop both services
pkill -f "uvicorn"

# 2. Git revert changes
git revert <commit-hash>

# 3. Restart services
uvicorn ccow.main:app --reload --port 8001 &
uvicorn app.main:app --reload --port 8000 &
```

**Data Loss:** Context data is in-memory, so rollback causes no persistent data loss.

---

## 10. Testing Strategy

### 10.1 Unit Tests (CCOW Vault)

```python
# ccow/tests/test_vault_multiuser.py

from ccow.vault import ContextVault


def test_multiple_users_independent_contexts():
    """Test that users have independent patient contexts."""
    vault = ContextVault()

    # User 1 sets patient P1
    ctx1 = vault.set_context(
        user_id="user_123",
        patient_id="P1",
        set_by="med-z1",
        email="user1@va.gov"
    )
    assert ctx1.patient_id == "P1"

    # User 2 sets patient P2
    ctx2 = vault.set_context(
        user_id="user_456",
        patient_id="P2",
        set_by="cprs",
        email="user2@va.gov"
    )
    assert ctx2.patient_id == "P2"

    # Verify independence
    assert vault.get_context("user_123").patient_id == "P1"
    assert vault.get_context("user_456").patient_id == "P2"


def test_user_scoped_history():
    """Test that history can be filtered by user."""
    vault = ContextVault()

    # User 1 activity
    vault.set_context("user_123", "P1", "med-z1", "user1@va.gov")
    vault.set_context("user_123", "P2", "med-z1", "user1@va.gov")

    # User 2 activity
    vault.set_context("user_456", "P3", "cprs", "user2@va.gov")

    # User 1 should see only their events
    user1_history = vault.get_history(user_id="user_123", scope="user")
    assert len(user1_history) == 2
    assert all(entry.user_id == "user_123" for entry in user1_history)

    # Global history should show all events
    global_history = vault.get_history(scope="global")
    assert len(global_history) == 3


def test_stale_context_cleanup():
    """Test that stale contexts are removed."""
    vault = ContextVault(cleanup_threshold_hours=0)  # Immediate cleanup

    # Set context
    vault.set_context("user_123", "P1", "med-z1")
    assert vault.get_context_count() == 1

    # Cleanup (threshold=0 means all contexts are stale)
    removed = vault.cleanup_stale_contexts()
    assert removed == 1
    assert vault.get_context_count() == 0


def test_context_persistence_across_operations():
    """Test that user context persists across multiple operations."""
    vault = ContextVault()

    # User 1 sets context
    vault.set_context("user_123", "P1", "med-z1")

    # User 2 sets different context (shouldn't affect user 1)
    vault.set_context("user_456", "P2", "cprs")

    # User 1 context still intact
    assert vault.get_context("user_123").patient_id == "P1"

    # Clear user 2 (shouldn't affect user 1)
    vault.clear_context("user_456")

    # User 1 context still intact
    assert vault.get_context("user_123").patient_id == "P1"
```

---

### 10.2 Integration Tests (FastAPI)

```python
# ccow/tests/test_api_multiuser.py

from fastapi.testclient import TestClient
from ccow.main import app
from ccow.vault import vault

client = TestClient(app)


def setup_function(_):
    """Reset vault before each test."""
    vault._contexts.clear()
    vault._history.clear()


def test_unauthenticated_request_returns_401():
    """Test that requests without session cookie are rejected."""
    response = client.get("/ccow/active-patient")
    assert response.status_code == 401


def test_authenticated_users_have_independent_contexts():
    """Test multi-user context isolation."""

    # Simulate two different session cookies
    session_1 = create_test_session(user_id="user_123")
    session_2 = create_test_session(user_id="user_456")

    # User 1 sets patient P1
    response = client.put(
        "/ccow/active-patient",
        json={"patient_id": "P1", "set_by": "med-z1"},
        cookies={"session_id": session_1}
    )
    assert response.status_code == 200

    # User 2 sets patient P2
    response = client.put(
        "/ccow/active-patient",
        json={"patient_id": "P2", "set_by": "cprs"},
        cookies={"session_id": session_2}
    )
    assert response.status_code == 200

    # User 1 gets P1
    response = client.get(
        "/ccow/active-patient",
        cookies={"session_id": session_1}
    )
    assert response.status_code == 200
    assert response.json()["patient_id"] == "P1"

    # User 2 gets P2
    response = client.get(
        "/ccow/active-patient",
        cookies={"session_id": session_2}
    )
    assert response.status_code == 200
    assert response.json()["patient_id"] == "P2"


def test_history_scope_filtering():
    """Test user-scoped vs global history."""

    session_1 = create_test_session(user_id="user_123")
    session_2 = create_test_session(user_id="user_456")

    # User 1 activity
    client.put(
        "/ccow/active-patient",
        json={"patient_id": "P1", "set_by": "med-z1"},
        cookies={"session_id": session_1}
    )

    # User 2 activity
    client.put(
        "/ccow/active-patient",
        json={"patient_id": "P2", "set_by": "cprs"},
        cookies={"session_id": session_2}
    )

    # User 1 sees only their history
    response = client.get(
        "/ccow/history?scope=user",
        cookies={"session_id": session_1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scope"] == "user"
    assert data["total_count"] == 1
    assert data["history"][0]["user_id"] == "user_123"

    # Global history shows all events
    response = client.get(
        "/ccow/history?scope=global",
        cookies={"session_id": session_1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scope"] == "global"
    assert data["total_count"] == 2


# Helper function
def create_test_session(user_id: str) -> str:
    """Create a test session in the database and return session_id."""
    # Implementation depends on database setup
    # For now, mock/stub this
    pass
```

---

### 10.3 Manual Test Scenarios

#### Scenario 1: Multi-User Context Isolation

```bash
# Terminal 1: Login as Dr. Alice
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c alice_cookies.txt

# Set active patient P1 as Dr. Alice
curl -X PUT http://localhost:8001/ccow/active-patient \
  -b alice_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "1012845331V153053", "set_by": "med-z1"}'

# Terminal 2: Login as Dr. Bob
curl -X POST http://localhost:8000/login \
  -d "email=clinician.bravo@va.gov&password=VaDemo2025!" \
  -c bob_cookies.txt

# Set active patient P2 as Dr. Bob
curl -X PUT http://localhost:8001/ccow/active-patient \
  -b bob_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "1013012345V678901", "set_by": "med-z1"}'

# Verify isolation: Dr. Alice should still see P1
curl -X GET http://localhost:8001/ccow/active-patient \
  -b alice_cookies.txt
# Expected: {"patient_id": "1012845331V153053", ...}

# Verify isolation: Dr. Bob should see P2
curl -X GET http://localhost:8001/ccow/active-patient \
  -b bob_cookies.txt
# Expected: {"patient_id": "1013012345V678901", ...}
```

---

#### Scenario 2: Context Persistence Across Logout/Login

```bash
# Login as Dr. Alice
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c alice_cookies.txt

# Set active patient P1
curl -X PUT http://localhost:8001/ccow/active-patient \
  -b alice_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "1012845331V153053", "set_by": "med-z1"}'

# Logout
curl -X POST http://localhost:8000/logout \
  -b alice_cookies.txt

# Login again (new session)
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c alice_cookies_new.txt

# Verify patient context restored
curl -X GET http://localhost:8001/ccow/active-patient \
  -b alice_cookies_new.txt
# Expected: {"patient_id": "1012845331V153053", ...}
# Context should persist across sessions!
```

---

#### Scenario 3: User-Scoped History

```bash
# Login as Dr. Alice
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c alice_cookies.txt

# Alice sets P1, then P2
curl -X PUT http://localhost:8001/ccow/active-patient \
  -b alice_cookies.txt \
  -d '{"patient_id": "P1", "set_by": "med-z1"}'

curl -X PUT http://localhost:8001/ccow/active-patient \
  -b alice_cookies.txt \
  -d '{"patient_id": "P2", "set_by": "med-z1"}'

# Login as Dr. Bob
curl -X POST http://localhost:8000/login \
  -d "email=clinician.bravo@va.gov&password=VaDemo2025!" \
  -c bob_cookies.txt

# Bob sets P3
curl -X PUT http://localhost:8001/ccow/active-patient \
  -b bob_cookies.txt \
  -d '{"patient_id": "P3", "set_by": "cprs"}'

# Alice's user-scoped history (should show 2 events)
curl -X GET "http://localhost:8001/ccow/history?scope=user" \
  -b alice_cookies.txt
# Expected: {"scope": "user", "total_count": 2, ...}

# Global history (should show 3 events)
curl -X GET "http://localhost:8001/ccow/history?scope=global" \
  -b alice_cookies.txt
# Expected: {"scope": "global", "total_count": 3, ...}
```

---

## 11. Security Considerations

### 11.1 Session Validation

**Threat:** User spoofs `user_id` to access another user's context

**Mitigation:**
- ✅ CCOW validates `session_id` cookie against `auth.sessions` table
- ✅ `user_id` extracted from validated session (not trusted from request body)
- ✅ Session validation includes `is_active` and `expires_at` checks

```python
# ccow/auth_helper.py

def get_user_from_session(session_id: str) -> Optional[Dict]:
    """
    Validate session and extract user_id.

    Security checks:
    1. Session exists in database
    2. Session is active (is_active = TRUE)
    3. Session has not expired (expires_at > NOW())
    """
    # Implementation in Section 7.1
```

---

### 11.2 Cookie Security

**Threat:** Session cookie stolen via XSS or network interception

**Mitigation:**
- ✅ `HttpOnly` flag: Prevents JavaScript access
- ✅ `Secure` flag: HTTPS-only in production
- ✅ `SameSite=Lax`: CSRF protection

```python
# app/routes/auth.py (existing - no changes needed)

response.set_cookie(
    key="session_id",
    value=str(session_id),
    httponly=True,        # XSS protection
    secure=True,          # HTTPS only (production)
    samesite="lax",       # CSRF protection
    max_age=900           # 15 minutes
)
```

---

### 11.3 Authorization

**Current State:** All authenticated users have equal access to CCOW operations.

**Future Enhancement (Out of Scope):**
- Role-based access control (RBAC) for admin endpoints
- `GET /ccow/active-patients` restricted to admin role
- `POST /ccow/cleanup` restricted to admin role

```python
# Future: app/middleware/rbac.py

def require_admin(request: Request):
    user = request.state.user
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
```

---

### 11.4 Audit Logging

**All context changes are logged with:**
- ✅ `user_id` and `email` - Who performed the action
- ✅ `patient_id` - Which patient context was affected
- ✅ `timestamp` - When the action occurred
- ✅ `actor` - Which application performed the action

**Logs stored in:**
- In-memory `_history` deque (last 100 events)
- Future: PostgreSQL `ccow.audit_logs` table for long-term retention

---

## 12. Future Enhancements

### 12.1 Persistent Storage (Phase 2)

**Current:** In-memory storage (data lost on restart)

**Future:** PostgreSQL-backed context storage

```sql
-- db/ddl/create_ccow_tables.sql

CREATE SCHEMA IF NOT EXISTS ccow;

CREATE TABLE ccow.user_contexts (
    user_id             UUID            PRIMARY KEY REFERENCES auth.users(user_id) ON DELETE CASCADE,
    patient_id          VARCHAR(20)     NOT NULL,
    set_by              VARCHAR(50)     NOT NULL,
    set_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ccow.context_history (
    history_id          BIGSERIAL       PRIMARY KEY,
    user_id             UUID            NOT NULL REFERENCES auth.users(user_id) ON DELETE SET NULL,
    action              VARCHAR(10)     NOT NULL,  -- 'set' or 'clear'
    patient_id          VARCHAR(20),
    actor               VARCHAR(50)     NOT NULL,
    timestamp           TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_contexts_user_id ON ccow.user_contexts(user_id);
CREATE INDEX idx_context_history_user_id ON ccow.context_history(user_id, timestamp DESC);
```

**Benefits:**
- Context survives CCOW service restarts
- Long-term audit history
- Easier horizontal scaling

---

### 12.2 Real-Time Notifications (Phase 3)

**Current:** Polling-based context sync (apps must poll `/ccow/active-patient`)

**Future:** WebSocket/SSE-based push notifications

```python
# ccow/main.py (future)

from fastapi import WebSocket

@app.websocket("/ccow/subscribe")
async def subscribe_to_context_changes(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time context change notifications.

    When user's context changes (set by any app), push notification to all
    subscribed clients for that user.
    """
    await websocket.accept()
    # Subscribe to user-specific context changes
    # ...
```

**Use Case:**
- User selects Patient P1 in CPRS
- CPRS calls `PUT /ccow/active-patient` (user_123 → P1)
- med-z1 (subscribed via WebSocket) receives notification
- med-z1 auto-refreshes dashboard to show Patient P1

---

### 12.3 Multi-Session Per User (Phase 4)

**Current:** Single session enforcement (new login invalidates old session)

**Future:** Allow multiple concurrent sessions with independent contexts

**Architecture Change:**
- Key contexts by `session_id` instead of `user_id`
- Each session maintains independent patient context
- User can work on different patients at different workstations

**Use Case:**
- Dr. Alice at Workstation A (session_1) viewing Patient P1
- Dr. Alice at Workstation B (session_2) viewing Patient P2
- Both sessions remain active simultaneously

**Trade-off:**
- More complex cleanup logic (orphaned session contexts)
- Higher memory usage (more contexts to track)

---

### 12.4 Context Expiration Policies (Phase 5)

**Current:** Contexts remain until explicitly cleared

**Future:** Auto-expire contexts after TTL

```python
# ccow/vault.py (future)

class ContextVault:
    def __init__(self, context_ttl_hours: int = 8):
        self._context_ttl = timedelta(hours=context_ttl_hours)

    def get_context(self, user_id: str) -> Optional[PatientContext]:
        context = self._contexts.get(user_id)
        if context:
            # Check TTL
            if datetime.now(timezone.utc) - context.set_at > self._context_ttl:
                # Expired, auto-clear
                self.clear_context(user_id, cleared_by="system:ttl")
                return None
        return context
```

**Benefits:**
- Prevents stale contexts (e.g., clinician forgot to clear patient at end of day)
- Privacy: reduces risk of context leakage across shifts

---

## 13. Implementation Checklist

Use this checklist to track implementation progress:

### Phase 1: Core Vault Updates ✅

- [ ] Update `ccow/models.py`
  - [ ] Add `user_id`, `email`, `last_accessed_at` to `PatientContext`
  - [ ] Add `user_id`, `email` to `ContextHistoryEntry`
  - [ ] Create `GetAllActiveContextsResponse` model
  - [ ] Create `GetHistoryResponse` model

- [ ] Update `ccow/vault.py`
  - [ ] Change `_current` to `_contexts: Dict[str, PatientContext]`
  - [ ] Update `get_context(user_id)` method
  - [ ] Update `set_context(user_id, patient_id, set_by, email)` method
  - [ ] Update `clear_context(user_id, cleared_by, email)` method
  - [ ] Update `get_history(user_id, scope)` method
  - [ ] Add `get_all_contexts()` method
  - [ ] Add `cleanup_stale_contexts()` method

- [ ] Create `ccow/auth_helper.py`
  - [ ] Implement `get_user_from_session(session_id)` function
  - [ ] Add session validation logic (is_active, expires_at)

- [ ] Update `ccow/main.py`
  - [ ] Create `get_current_user()` dependency
  - [ ] Update `GET /ccow/active-patient` endpoint
  - [ ] Update `PUT /ccow/active-patient` endpoint
  - [ ] Update `DELETE /ccow/active-patient` endpoint
  - [ ] Update `GET /ccow/history` endpoint (add scope parameter)
  - [ ] Add `GET /ccow/active-patients` endpoint (admin)
  - [ ] Add `POST /ccow/cleanup` endpoint (admin)

### Phase 2: CCOW Client Updates ✅

- [ ] Update `app/utils/ccow_client.py`
  - [ ] Update `set_active_patient(request, patient_id, set_by)` signature
  - [ ] Update `get_active_patient(request)` signature
  - [ ] Add `get_active_patient_context(request)` method
  - [ ] Update `clear_active_patient(request, cleared_by)` signature
  - [ ] Add session cookie forwarding logic

### Phase 3: Route Updates ✅

- [ ] Update `app/routes/dashboard.py`
  - [ ] Pass `request` to `ccow_client.get_active_patient()`
  - [ ] Handle None return value (no active context)

- [ ] Update `app/routes/patient.py`
  - [ ] Pass `request` to `ccow_client.set_active_patient()`

- [ ] Update other clinical domain routes (if they use CCOW)
  - [ ] `app/routes/demographics.py`
  - [ ] `app/routes/vitals.py`
  - [ ] `app/routes/medications.py`
  - [ ] `app/routes/allergies.py`
  - [ ] `app/routes/encounters.py`
  - [ ] `app/routes/labs.py`

### Phase 4: Testing ✅

- [ ] Unit Tests
  - [ ] `ccow/tests/test_vault_multiuser.py` (create new file)
  - [ ] Test multi-user context isolation
  - [ ] Test user-scoped history
  - [ ] Test stale context cleanup
  - [ ] Test context persistence

- [ ] Integration Tests
  - [ ] `ccow/tests/test_api_multiuser.py` (create new file)
  - [ ] Test unauthenticated requests (401)
  - [ ] Test multi-user API isolation
  - [ ] Test history scope filtering
  - [ ] Test admin endpoints

- [ ] Manual Testing
  - [ ] Scenario 1: Multi-user context isolation
  - [ ] Scenario 2: Context persistence across logout/login
  - [ ] Scenario 3: User-scoped history

### Phase 5: Documentation ✅

- [ ] Update `docs/ccow-vault-design.md`
  - [ ] Add reference to this multi-user enhancement document
  - [ ] Update Section 13.1 (mark multi-user as complete)
  - [ ] Update version number to v2.0

- [ ] Update `ccow/README.md`
  - [ ] Document new API endpoints
  - [ ] Document authentication requirements
  - [ ] Add multi-user usage examples

- [ ] Update `CLAUDE.md`
  - [ ] Note CCOW v2.0 multi-user support
  - [ ] Update architecture diagrams (if present)

### Phase 6: Deployment ✅

- [ ] Configuration
  - [ ] Verify `CCOW_ENABLED`, `CCOW_URL` in `.env`
  - [ ] No new config needed (uses existing auth)

- [ ] Service Restart
  - [ ] Stop CCOW service
  - [ ] Deploy v2.0 code
  - [ ] Restart CCOW service
  - [ ] Verify health endpoint

- [ ] Smoke Tests
  - [ ] Login as two different users
  - [ ] Verify context isolation
  - [ ] Verify history filtering

---

## 14. Cross-Application Authentication (v2.1 Enhancement)

**Status:** ✅ Implemented (2026-01-27)

### 14.1 Overview

CCOW Vault v2.1 adds support for cross-application authentication to enable integration with external CCOW-aware applications (med-z4, CPRS emulator, imaging systems, etc.) that use different session cookie names.

**Problem Solved:**
- med-z1 uses `session_id` cookie
- med-z4 uses `med_z4_session_id` cookie
- Both write to the same `auth.sessions` table (session UUIDs are compatible)
- CCOW Vault needs to accept sessions from both applications

**Solution:**
Added `X-Session-ID` header support as an explicit cross-application authentication method, while maintaining backward compatibility with cookie-based authentication.

### 14.2 Authentication Methods

CCOW Vault now supports two authentication methods with clear priority:

#### Method 1: X-Session-ID Header (Priority)
**Use Case:** External CCOW-aware applications (med-z4, CPRS, imaging systems)

```http
GET /ccow/active-patient HTTP/1.1
Host: localhost:8001
X-Session-ID: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

**Advantages:**
- ✅ Explicit cross-application authentication (clear intent)
- ✅ No cookie name conflicts
- ✅ Standard HTTP header convention
- ✅ Works with any HTTP client (httpx, requests, curl)

#### Method 2: session_id Cookie (Fallback)
**Use Case:** med-z1 internal browser-based sessions

```http
GET /ccow/active-patient HTTP/1.1
Host: localhost:8001
Cookie: session_id=550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

**Advantages:**
- ✅ Backward compatible with existing med-z1 code
- ✅ Automatic browser cookie handling
- ✅ Zero changes required to med-z1 routes

### 14.3 Priority Order

If both are present, **header takes priority**:

```python
# Implementation in ccow/main.py
def get_session_id_from_request(request: Request) -> Optional[str]:
    # 1. Check X-Session-ID header first
    session_id = request.headers.get("X-Session-ID")
    if session_id:
        return session_id

    # 2. Fall back to session_id cookie
    return request.cookies.get("session_id")
```

### 14.4 Security Model

Both authentication methods use **identical validation**:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Extract session_id (header or cookie)                    │
│    ↓                                                         │
│ 2. Validate against auth.sessions table                     │
│    - Session exists?                                         │
│    - is_active = TRUE?                                       │
│    - expires_at > NOW()?                                     │
│    ↓                                                         │
│ 3. Extract user_id from validated session                   │
│    ↓                                                         │
│ 4. Perform CCOW operation for that user_id                  │
└─────────────────────────────────────────────────────────────┘
```

**Security Properties:**
- ✅ No additional attack surface (same validation for both paths)
- ✅ Session reuse prevention (TTL enforced by auth.sessions)
- ✅ No user_id spoofing (extracted from database, not request)

### 14.5 Integration Examples

#### med-z1 (Cookie-Based) - No Changes Required

```python
# app/routes/patient.py (unchanged)
@router.get("/patient/{icn}")
async def patient_overview(icn: str, request: Request):
    # session_id cookie automatically sent by browser
    ccow_client.set_active_patient(request, patient_id=icn, set_by="med-z1")
    # ...
```

#### med-z4 (Header-Based) - New Capability

```python
# med-z4/services/ccow_service.py
import httpx
from fastapi import Request

async def set_active_patient(request: Request, patient_id: str) -> bool:
    """Set active patient in CCOW vault using header-based auth."""

    # Extract med-z4's session_id from med_z4_session_id cookie
    session_id = request.cookies.get("med_z4_session_id")
    if not session_id:
        return False

    # Call CCOW vault with X-Session-ID header
    async with httpx.AsyncClient() as client:
        response = await client.put(
            "http://localhost:8001/ccow/active-patient",
            headers={"X-Session-ID": session_id},  # Pass session via header
            json={"patient_id": patient_id, "set_by": "med-z4"}
        )
        return response.status_code == 200
```

#### CPRS Emulator (Either Method)

```python
# cprs/ccow_integration.py

# Option A: Header-based (recommended for non-browser clients)
requests.put(
    "http://localhost:8001/ccow/active-patient",
    headers={"X-Session-ID": cprs_session_id},
    json={"patient_id": "ICN100001", "set_by": "cprs"}
)

# Option B: Cookie-based (if using browser/session cookies)
requests.put(
    "http://localhost:8001/ccow/active-patient",
    cookies={"session_id": cprs_session_id},
    json={"patient_id": "ICN100001", "set_by": "cprs"}
)
```

### 14.6 Testing

#### Test 1: Cookie-Based Auth (Regression Test)

```bash
# Login to med-z1
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c cookies.txt

# Set active patient via cookie (med-z1 existing behavior)
curl -X PUT http://localhost:8001/ccow/active-patient \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "ICN100001", "set_by": "med-z1"}'

# Expected: 200 OK (no regression)
```

#### Test 2: Header-Based Auth (New Feature)

```bash
# Extract session_id from any authenticated med-z1 or med-z4 session
SESSION_ID="550e8400-e29b-41d4-a716-446655440000"

# Set active patient via header (med-z4 new capability)
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "ICN100001", "set_by": "med-z4"}'

# Expected: 200 OK (new feature works)
```

#### Test 3: Priority Order (Header > Cookie)

```bash
# Pass both header and cookie with different session IDs
curl -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: <valid-session-1>" \
  -b "session_id=<valid-session-2>"

# Expected: Uses session-1 from header (header takes priority)
# Response will contain user_id from session-1
```

### 14.7 Implementation Files

| File | Change | Status |
|------|--------|--------|
| `ccow/main.py` | Added `get_session_id_from_request()` helper | ✅ Complete |
| `ccow/main.py` | Updated `get_current_user()` to use helper | ✅ Complete |
| `ccow/main.py` | Updated all endpoint docstrings | ✅ Complete |
| `ccow/main.py` | Version bump: 2.0.0 → 2.1.0 | ✅ Complete |
| `docs/spec/ccow-multi-user-enhancement.md` | Added Section 14 (this section) | ✅ Complete |

### 14.8 Backward Compatibility

**✅ Zero Breaking Changes:**
- med-z1 continues using cookie-based auth (no code changes required)
- All existing med-z1 routes work exactly as before
- Same session validation logic for both paths
- No database schema changes
- No configuration changes

**✅ Additive Enhancement:**
- New capability (header-based auth) added alongside existing capability
- Clear priority order (header > cookie) eliminates ambiguity
- Future-proof for additional CCOW-aware applications (med-z5, med-z6, etc.)

---

## 15. Timezone and Session Management (v2.1 Enhancement)

**Status:** ✅ Implemented (2026-01-27)

### 15.1 Overview

During the v2.1 implementation, a timezone inconsistency was identified and fixed in the session management layer. While CCOW Vault has always used UTC for timestamps (since v2.0), the underlying `app/db/auth.py` session creation functions were using local timezone, which could cause issues in multi-application deployments.

**Issue Identified:**
- `app/db/auth.py` used `datetime.now()` (local timezone)
- This predated the v2.1 CCOW refactoring (existed since Dec 18)
- Could cause session expiration issues across different server timezones
- Could cause DST-related bugs

**Solution:**
- Fixed all `datetime.now()` calls to use `datetime.now(timezone.utc)`
- Updated both session creation and validation logic
- Maintains backward compatibility with smart timezone-aware/naive comparison

### 15.2 Files Modified

| File | Functions Fixed | Status |
|------|----------------|--------|
| `app/db/auth.py` | `create_session()` | ✅ Fixed |
| `app/db/auth.py` | `extend_session()` | ✅ Fixed |
| `app/db/auth.py` | `update_last_login()` | ✅ Fixed |
| `app/db/auth.py` | `log_audit_event()` | ✅ Fixed |
| `app/db/auth.py` | `cleanup_expired_sessions()` | ✅ Fixed |
| `app/middleware/auth.py` | Session expiration check | ✅ Enhanced |
| `ccow/auth_helper.py` | Session validation | ✅ Already correct |

### 15.3 Timezone Standard

**Principle:** All timestamps in the med-z1 ecosystem use UTC

```python
# ✅ CORRECT - Always use UTC
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
expires_at = now + timedelta(minutes=15)

# ❌ WRONG - Never use naive datetime
from datetime import datetime
now = datetime.now()  # Uses local timezone (system-dependent)
```

### 15.4 Session Validation Pattern

CCOW and med-z1 use smart validation that handles both timezone-aware and naive datetimes:

```python
# ccow/auth_helper.py (lines 112-115)
if expires_at.tzinfo is None:
    now = datetime.now()  # Graceful fallback for legacy data
else:
    now = datetime.now(timezone.utc)  # UTC comparison

if expires_at < now:
    # Session expired
    return None
```

**Why this pattern?**
- Backward compatible with any existing timezone-naive sessions
- Works correctly with new UTC-aware sessions
- No breaking changes during transition

### 15.5 Multi-Application Integration

**Shared Session Table:** `auth.sessions` (PostgreSQL)

All applications write to the same table with UTC timestamps:

| Application | Cookie Name | Session Table | Timezone |
|-------------|-------------|---------------|----------|
| med-z1 | `session_id` | auth.sessions | UTC ✅ |
| med-z4 | `med_z4_session_id` | auth.sessions | UTC ✅ |
| CCOW Vault | N/A (reads only) | auth.sessions | UTC ✅ |

**Key Requirements for External Apps:**
1. Copy session functions from `med-z1/app/db/auth.py` (includes UTC fix)
2. Configure `DATABASE_URL` to point to shared database
3. Use unique cookie name (e.g., `med_z4_session_id`)
4. Pass session to CCOW via `X-Session-ID` header

### 15.6 Benefits

| Benefit | Impact |
|---------|--------|
| **Timezone Consistency** | Sessions work identically worldwide |
| **DST Safety** | No bugs during daylight saving transitions |
| **Multi-App SSO** | Shared sessions work correctly across med-z1, med-z4 |
| **Audit Compliance** | Absolute UTC timestamps for legal requirements |
| **Cloud Ready** | Deploy to any region without code changes |

### 15.7 Testing Validation

**Verify UTC Storage:**

```sql
-- Check recent sessions
SELECT
    session_id,
    created_at,
    expires_at,
    (expires_at - NOW() AT TIME ZONE 'UTC') AS time_remaining
FROM auth.sessions
ORDER BY created_at DESC
LIMIT 5;
```

**Expected:** `time_remaining` should show ~14-15 minutes for fresh sessions

**Test Session Expiration:**

```bash
# 1. Login
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov&password=VaDemo2025!" \
  -c cookies.txt

# 2. Verify session valid
curl -X GET http://localhost:8001/ccow/active-patient -b cookies.txt
# Expected: 200 OK or 404 (no context)

# 3. Wait 16 minutes

# 4. Verify session expired
curl -X GET http://localhost:8001/ccow/active-patient -b cookies.txt
# Expected: 401 Unauthorized (session expired)
```

### 15.8 Related Documentation

For detailed integration guidance, see:
- **`docs/spec/timezone-and-session-management.md`** - Comprehensive 40-page guide
  - Complete timezone standard
  - Session management architecture
  - Multi-application integration patterns
  - Testing and validation procedures
  - Troubleshooting guide

- **`docs/spec/med-z4-integration-quickstart.md`** - Quick start guide
  - 30-minute implementation guide
  - Copy-paste ready code examples
  - Testing procedures
  - Common issues and fixes

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v2.0 | 2025-12-20 | System | Initial multi-user enhancement design |
| v2.1 | 2026-01-27 | System | Added Section 14: Cross-application authentication (X-Session-ID header support) |
| v2.1.1 | 2026-01-27 | System | Added Section 15: Timezone and session management fix |

---

**End of Document**
