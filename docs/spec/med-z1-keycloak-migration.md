# med-z1 Keycloak Migration – Design Specification

**Document Version:** v1.0
**Date:** 2026-01-08
**Status:** 🟡 DESIGN PHASE (Not yet implemented)
**Target Repository:** `med-z1` (existing repository)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Target State Architecture](#3-target-state-architecture)
4. [Requirements](#4-requirements)
5. [Migration Strategy](#5-migration-strategy)
6. [Phase 1: Keycloak OIDC Integration](#6-phase-1-keycloak-oidc-integration)
7. [Phase 2: CCOW Client Update](#7-phase-2-ccow-client-update)
8. [Phase 3: Cleanup and Deprecation](#8-phase-3-cleanup-and-deprecation)
9. [Testing Strategy](#9-testing-strategy)
10. [Rollback Plan](#10-rollback-plan)
11. [Security Considerations](#11-security-considerations)
12. [Implementation Checklist](#12-implementation-checklist)

---

## 1. Executive Summary

### 1.1 Purpose

This document specifies the migration of **med-z1** from custom session-based authentication to **Keycloak OIDC (OAuth 2.0 / OpenID Connect)** authentication, enabling Single Sign-On (SSO) across the med-* family of applications and integration with the new **med-z8 CCOW Context Vault** service.

### 1.2 Goals

1. **Enable SSO**: Users log in once to Keycloak, gain access to med-z1 and all future med-* applications
2. **Integrate with med-z8**: Replace embedded CCOW service with standalone med-z8 service
3. **Maintain Compatibility**: Zero downtime migration with feature flag support
4. **Preserve User Experience**: Minimal UI changes, seamless authentication flow
5. **Future-Proof**: Align with VA enterprise authentication standards (Azure AD patterns)

### 1.3 Success Criteria

| Criterion | Target |
|-----------|--------|
| **Authentication** | Keycloak OIDC login works for all med-z1 users |
| **SSO** | Login to med-z1 → auto-login to CPRS simulator (future) |
| **CCOW Integration** | med-z1 successfully calls med-z8 for patient context |
| **Performance** | No degradation in page load times (< 5% increase) |
| **Rollback** | Can revert to old auth within 1 hour if issues arise |
| **Data Integrity** | No data loss during migration |

### 1.4 Migration Timeline

**Estimated Duration**: 4-6 weeks

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1: Keycloak OIDC Integration | 2-3 weeks | Replace session auth with OIDC |
| Phase 2: CCOW Client Update | 1-2 weeks | Call med-z8 instead of embedded CCOW |
| Phase 3: Cleanup and Deprecation | 1 week | Remove old auth code, embedded CCOW |

---

## 2. Current State Analysis

### 2.1 Current Authentication Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     med-z1 Application                   │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ app/routes/auth.py                             │    │
│  │  - POST /login (username/password)             │    │
│  │  - POST /logout                                │    │
│  │  - Creates session record in PostgreSQL        │    │
│  │  - Sets session_id cookie                      │    │
│  └────────────────────┬───────────────────────────┘    │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────┐    │
│  │ app/middleware/auth.py                         │    │
│  │  - AuthMiddleware validates session_id cookie  │    │
│  │  - Queries auth.sessions table                 │    │
│  │  - Checks is_active, expires_at                │    │
│  │  - Injects request.state.user                  │    │
│  └────────────────────┬───────────────────────────┘    │
│                       │                                  │
│                       ▼                                  │
│              ┌─────────────────┐                        │
│              │  PostgreSQL DB  │                        │
│              │  auth.sessions  │                        │
│              │  auth.users     │                        │
│              └─────────────────┘                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ ccow/ (embedded CCOW service)                  │    │
│  │  - Runs on port 8001                           │    │
│  │  - Validates session_id via PostgreSQL         │    │
│  │  - auth_helper.py → auth.sessions table        │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Current User Flow

1. User visits `http://localhost:8000/dashboard`
2. AuthMiddleware checks for `session_id` cookie
3. If missing/invalid → Redirect to `/login`
4. User enters username/password → POST `/login`
5. med-z1 validates credentials against `auth.users` table
6. med-z1 creates record in `auth.sessions` table
7. med-z1 sets `session_id` cookie (HttpOnly, SameSite=Lax)
8. User redirected to `/dashboard`
9. All subsequent requests carry `session_id` cookie
10. AuthMiddleware validates session on every request

### 2.3 Pain Points and Limitations

| Issue | Impact |
|-------|--------|
| **Custom Auth Logic** | Maintenance burden, not standards-based |
| **PostgreSQL Dependency** | Session validation requires DB query on every request |
| **No SSO** | Users must log in separately to each med-* application |
| **Single-App Scope** | CCOW service tied to med-z1's auth system |
| **Token Management** | No refresh tokens, session timeouts poorly handled |
| **Password Storage** | bcrypt hashing, but custom user management |

### 2.4 Files Requiring Changes

| File | Current Functionality | Change Required |
|------|----------------------|-----------------|
| `app/routes/auth.py` | Custom login/logout | Replace with OIDC flow |
| `app/middleware/auth.py` | Session validation | Replace with JWT validation |
| `app/utils/ccow_client.py` | Calls embedded CCOW (session cookie) | Call med-z8 (JWT bearer token) |
| `ccow/auth_helper.py` | Session validation (PostgreSQL) | Delete (no longer needed) |
| `config.py` | Session config | Add Keycloak/OIDC config |
| `.env` | Session secrets | Add Keycloak URLs, client secrets |

---

## 3. Target State Architecture

### 3.1 Target Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      VA Healthcare Ecosystem                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Keycloak Identity Provider (Port 8080)           │  │
│  │  Realm: va-development                                    │  │
│  │  Users: clinician.alpha@va.gov, clinician.bravo@va.gov   │  │
│  │  Clients: med-z1, med-z8-ccow, cprs-simulator            │  │
│  │  Issues: JWT Access Tokens (15 min expiration)           │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                      │
│        ┌──────────────────┴──────────────────┬──────────┐       │
│        │ OIDC Login                          │ OIDC     │       │
│        ▼                                     ▼          ▼       │
│   ┌─────────┐                          ┌─────────┐  ┌──────┐   │
│   │ med-z1  │                          │  CPRS   │  │Future│   │
│   │ (8000)  │                          │ (8002)  │  │Apps  │   │
│   └────┬────┘                          └────┬────┘  └──┬───┘   │
│        │ JWT Bearer                         │ JWT     │ JWT    │
│        └────────────────┬───────────────────┴─────────┘        │
│                         ▼                                        │
│              ┌──────────────────────┐                           │
│              │      med-z8 CCOW     │                           │
│              │  Context Vault API   │                           │
│              │    (Port 8001)       │                           │
│              │  ✅ JWT validation   │                           │
│              │  ✅ No PostgreSQL    │                           │
│              │  ✅ Stateless        │                           │
│              └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Target User Flow

1. User visits `http://localhost:8000/dashboard`
2. med-z1 AuthMiddleware checks for `access_token` cookie
3. If missing/invalid → Redirect to Keycloak login (`/auth/login`)
4. Keycloak shows login page, user enters credentials
5. Keycloak validates credentials, creates session
6. Keycloak redirects back to med-z1 with **authorization code**
7. med-z1 exchanges code for **JWT access token** (calls Keycloak token endpoint)
8. med-z1 sets `access_token` cookie (HttpOnly, SameSite=Lax)
9. User redirected to `/dashboard`
10. All subsequent requests carry `access_token` cookie (JWT)
11. AuthMiddleware validates JWT signature (**no database query**)
12. CCOW calls to med-z8 include `Authorization: Bearer <JWT>` header

### 3.3 Key Architectural Changes

| Component | Before | After |
|-----------|--------|-------|
| **Authentication** | Custom (username/password) | OIDC (Keycloak) |
| **Session Storage** | PostgreSQL (`auth.sessions`) | Keycloak (server-side sessions) |
| **Token Format** | Opaque session_id (UUID) | JWT (signed, claims-based) |
| **Token Validation** | Database query (auth.sessions) | JWT signature validation (stateless) |
| **User Identity** | PostgreSQL (`auth.users`) | Keycloak (user federation) |
| **CCOW Integration** | Embedded service (session cookie) | Standalone med-z8 (JWT bearer token) |
| **SSO Support** | None | Full SSO across med-* apps |

---

## 4. Requirements

### 4.1 Functional Requirements

**FR-1: OIDC Login**
med-z1 SHALL redirect unauthenticated users to Keycloak for login via OIDC Authorization Code Flow.

**FR-2: JWT Validation**
med-z1 SHALL validate JWT access tokens on every authenticated request without database lookups.

**FR-3: User Profile**
med-z1 SHALL extract user information (user_id, email, display_name) from JWT claims.

**FR-4: SSO Support**
Logging in to med-z1 SHALL create a Keycloak session that enables automatic login to other med-* applications.

**FR-5: Token Refresh**
med-z1 SHALL support automatic token refresh using refresh tokens (background renewal).

**FR-6: CCOW Integration**
med-z1 SHALL call med-z8 CCOW service with JWT bearer tokens instead of session cookies.

**FR-7: Logout**
Logout from med-z1 SHALL optionally trigger Keycloak SSO logout (logging out of all applications).

### 4.2 Non-Functional Requirements

**NFR-1: Performance**
- JWT validation: < 50ms (p95)
- Page load times: No degradation > 5%
- JWKS caching to minimize Keycloak requests

**NFR-2: Compatibility**
- Existing user workflows unchanged (login → dashboard)
- No changes to patient data access patterns
- All routes continue to work

**NFR-3: Security**
- JWT signature validation on every request
- Token expiration enforcement (15 min default)
- HttpOnly cookies for tokens
- TLS/HTTPS in production

**NFR-4: Observability**
- Log all authentication events (login, logout, token refresh)
- Metrics for token validation performance
- Audit trail for CCOW operations

### 4.3 Out of Scope

- ❌ User migration from PostgreSQL to Keycloak (manual user creation acceptable)
- ❌ Multi-factor authentication (MFA)
- ❌ Custom Keycloak themes
- ❌ Keycloak high availability setup (single instance acceptable for dev)

---

## 5. Migration Strategy

### 5.1 Phased Migration Approach

**Phase 1: Keycloak OIDC Integration (Parallel Mode)**
- Install and configure Keycloak
- Implement OIDC authentication in med-z1
- Feature flag: `USE_KEYCLOAK_AUTH` (default: False)
- Test with Keycloak auth while keeping old auth working
- **No changes to CCOW** (embedded CCOW still used)

**Phase 2: CCOW Client Update**
- Deploy med-z8 service
- Update med-z1 CCOW client to call med-z8 (JWT bearer tokens)
- Feature flag: `USE_MED_Z8_CCOW` (default: False)
- Test CCOW integration

**Phase 3: Cutover and Cleanup**
- Enable feature flags permanently
- Remove old session-based auth code
- Remove embedded CCOW service
- Delete `auth.sessions` table (after backup)

### 5.2 Feature Flag Strategy

```python
# config.py

# Feature flags for gradual migration
USE_KEYCLOAK_AUTH = _get_bool("USE_KEYCLOAK_AUTH", default=False)
USE_MED_Z8_CCOW = _get_bool("USE_MED_Z8_CCOW", default=False)

# Authentication configuration
if USE_KEYCLOAK_AUTH:
    # Keycloak OIDC configuration
    AUTH_BACKEND = "oidc"
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "va-development")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "med-z1")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
else:
    # Legacy session-based authentication
    AUTH_BACKEND = "session"
    # ... existing session config

# CCOW configuration
if USE_MED_Z8_CCOW:
    CCOW_URL = "http://localhost:8001"  # med-z8 service
else:
    CCOW_URL = "http://localhost:8001"  # embedded CCOW (same port, different service)
```

### 5.3 Rollback Triggers

Rollback to old authentication if:
- Login failures > 10% of attempts
- Page load times increase > 20%
- CCOW context sync failures > 5%
- Critical bugs discovered in JWT validation
- Keycloak unavailable for > 5 minutes

**Rollback Procedure:**
1. Set `USE_KEYCLOAK_AUTH=false` in `.env`
2. Restart med-z1 application
3. Users revert to session-based auth
4. No data loss (old auth tables still exist)

---

## 6. Phase 1: Keycloak OIDC Integration

### 6.1 Install Dependencies

```bash
# Add to requirements.txt
authlib==1.3.0
httpx==0.26.0
```

### 6.2 Update Configuration

```python
# config.py (add Keycloak configuration)

# -----------------------------------------------------------
# Keycloak / OIDC Configuration
# -----------------------------------------------------------

USE_KEYCLOAK_AUTH = _get_bool("USE_KEYCLOAK_AUTH", default=False)

if USE_KEYCLOAK_AUTH:
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "va-development")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "med-z1")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

    # Computed OIDC endpoints
    KEYCLOAK_ISSUER = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"
    KEYCLOAK_AUTHORIZATION_ENDPOINT = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/auth"
    KEYCLOAK_TOKEN_ENDPOINT = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token"
    KEYCLOAK_USERINFO_ENDPOINT = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/userinfo"
    KEYCLOAK_JWKS_URI = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"
    KEYCLOAK_LOGOUT_ENDPOINT = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/logout"

    OIDC_CONFIG = {
        "issuer": KEYCLOAK_ISSUER,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "authorization_endpoint": KEYCLOAK_AUTHORIZATION_ENDPOINT,
        "token_endpoint": KEYCLOAK_TOKEN_ENDPOINT,
        "userinfo_endpoint": KEYCLOAK_USERINFO_ENDPOINT,
        "jwks_uri": KEYCLOAK_JWKS_URI,
        "logout_endpoint": KEYCLOAK_LOGOUT_ENDPOINT,
    }
```

```bash
# .env (add Keycloak configuration)

# Keycloak Configuration
USE_KEYCLOAK_AUTH=false  # Set to true when ready to test
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=va-development
KEYCLOAK_CLIENT_ID=med-z1
KEYCLOAK_CLIENT_SECRET=<get-from-keycloak-admin-console>
```

### 6.3 Create OIDC Authentication Module

```python
# app/auth/oidc.py (NEW)

from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt, JoseError
from starlette.config import Config as StarletteConfig
from fastapi import Request, HTTPException, status
import httpx
import logging

from config import OIDC_CONFIG

logger = logging.getLogger(__name__)

# Initialize OAuth client
oauth = OAuth()
oauth.register(
    name="keycloak",
    client_id=OIDC_CONFIG["client_id"],
    client_secret=OIDC_CONFIG["client_secret"],
    server_metadata_url=f"{OIDC_CONFIG['issuer']}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Cache for JWKS (Keycloak public keys)
_jwks_cache = None


async def get_jwks():
    """Fetch JSON Web Key Set from Keycloak (cached)."""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(OIDC_CONFIG["jwks_uri"])
            response.raise_for_status()
            _jwks_cache = response.json()
            logger.info("Fetched JWKS from Keycloak")
    return _jwks_cache


async def validate_jwt(token: str) -> dict:
    """
    Validate JWT access token from Keycloak.

    Returns:
        dict with claims (sub, email, name, etc.)

    Raises:
        HTTPException(401) if token is invalid
    """
    try:
        jwks = await get_jwks()
        claims = jwt.decode(token, jwks)

        # Validate claims (exp, nbf, iat)
        claims.validate()

        # Validate issuer
        if claims.get("iss") != OIDC_CONFIG["issuer"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer"
            )

        return claims

    except JoseError as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


async def get_current_user_from_jwt(request: Request) -> dict:
    """
    Extract and validate user from JWT access token.

    Looks for token in:
    1. Authorization: Bearer <token> header
    2. access_token cookie (fallback)

    Returns:
        {
            "user_id": str,       # From 'sub' claim
            "email": str,         # From 'email' claim
            "display_name": str,  # From 'name' or 'preferred_username'
        }
    """
    # Check Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Fallback to cookie (for web app sessions)
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token"
        )

    # Validate JWT
    claims = await validate_jwt(token)

    return {
        "user_id": claims["sub"],  # Subject (unique user ID)
        "email": claims.get("email"),
        "display_name": claims.get("name") or claims.get("preferred_username"),
    }
```

### 6.4 Update Login/Logout Routes

```python
# app/routes/auth.py (replace existing)

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.auth.oidc import oauth
from config import USE_KEYCLOAK_AUTH, OIDC_CONFIG
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


if USE_KEYCLOAK_AUTH:
    # OIDC-based authentication

    @router.get("/login")
    async def login(request: Request):
        """Redirect to Keycloak login page."""
        redirect_uri = request.url_for("auth_callback")
        logger.info(f"Redirecting to Keycloak login, callback: {redirect_uri}")
        return await oauth.keycloak.authorize_redirect(request, redirect_uri)


    @router.get("/auth/callback")
    async def auth_callback(request: Request):
        """
        Handle OAuth callback from Keycloak.

        Flow:
        1. User logs in to Keycloak
        2. Keycloak redirects here with authorization code
        3. Exchange code for access token
        4. Store access token in cookie
        5. Redirect to dashboard
        """
        try:
            # Exchange authorization code for tokens
            token = await oauth.keycloak.authorize_access_token(request)

            # Extract user info from ID token or userinfo endpoint
            user_info = token.get("userinfo")
            if not user_info:
                # Fallback: call userinfo endpoint
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        OIDC_CONFIG["userinfo_endpoint"],
                        headers={"Authorization": f"Bearer {token['access_token']}"}
                    )
                    user_info = response.json()

            logger.info(f"User logged in: {user_info.get('email')}")

            # Create response and set cookies
            response = RedirectResponse(url="/dashboard", status_code=303)

            # Set access token cookie (short-lived)
            response.set_cookie(
                key="access_token",
                value=token["access_token"],
                httponly=True,
                secure=False,  # Set True in production (HTTPS)
                samesite="lax",
                max_age=token.get("expires_in", 900),  # Token lifetime (15 min default)
            )

            # Set refresh token cookie (long-lived) for token renewal
            if "refresh_token" in token:
                response.set_cookie(
                    key="refresh_token",
                    value=token["refresh_token"],
                    httponly=True,
                    secure=False,
                    samesite="lax",
                    max_age=86400,  # 24 hours
                )

            return response

        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed")


    @router.post("/logout")
    async def logout(request: Request):
        """Logout from med-z1 and optionally from Keycloak (SSO logout)."""
        # Clear cookies
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        # Optional: Redirect to Keycloak logout endpoint (SSO logout)
        # This logs user out of ALL applications using Keycloak
        # Uncomment to enable:
        # post_logout_redirect_uri = "http://localhost:8000/login"
        # keycloak_logout_url = f"{OIDC_CONFIG['logout_endpoint']}?post_logout_redirect_uri={post_logout_redirect_uri}"
        # return RedirectResponse(keycloak_logout_url)

        return response

else:
    # Legacy session-based authentication (existing code)
    # ... keep existing login/logout logic unchanged
    pass
```

### 6.5 Update Authentication Middleware

```python
# app/middleware/auth.py (update for dual-mode)

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import RedirectResponse
from config import USE_KEYCLOAK_AUTH
import logging

logger = logging.getLogger(__name__)


if USE_KEYCLOAK_AUTH:
    # OIDC-based authentication
    from app.auth.oidc import get_current_user_from_jwt

    class AuthMiddleware(BaseHTTPMiddleware):
        """Middleware to validate JWT and inject user into request.state."""

        async def dispatch(self, request: Request, call_next):
            # Skip auth for public endpoints
            public_paths = ["/login", "/auth/callback", "/static", "/health", "/favicon.ico"]
            if any(request.url.path.startswith(path) for path in public_paths):
                return await call_next(request)

            try:
                # Validate JWT and extract user info
                user = await get_current_user_from_jwt(request)
                request.state.user = user
            except Exception as e:
                logger.warning(f"Authentication failed: {e}")
                # Redirect to login if token invalid/missing
                return RedirectResponse(url="/login", status_code=303)

            return await call_next(request)

else:
    # Legacy session-based authentication (existing code)
    # ... keep existing AuthMiddleware unchanged
    pass
```

### 6.6 Testing Keycloak Authentication

```bash
# 1. Start Keycloak
docker-compose up -d keycloak

# 2. Configure Keycloak realm and users (see setup script)
python scripts/setup_keycloak.py

# 3. Enable Keycloak auth in med-z1
# Edit .env: USE_KEYCLOAK_AUTH=true

# 4. Restart med-z1
uvicorn app.main:app --reload

# 5. Test login flow
# Visit: http://localhost:8000/dashboard
# → Redirects to Keycloak login
# → Enter credentials: clinician.alpha@va.gov / VaDemo2025!
# → Redirects back to med-z1 dashboard
# → Check for access_token cookie in browser DevTools
```

---

## 7. Phase 2: CCOW Client Update

### 7.1 Update CCOW Client to Call med-z8

```python
# app/utils/ccow_client.py (update for med-z8)

import logging
from typing import Optional, Dict, Any
import requests
from fastapi import Request
from config import CCOW_ENABLED, CCOW_URL, USE_MED_Z8_CCOW, USE_KEYCLOAK_AUTH

logger = logging.getLogger(__name__)


class CCOWClient:
    """HTTP client for interacting with CCOW Context Vault."""

    def __init__(self, base_url: str = CCOW_URL, enabled: bool = CCOW_ENABLED):
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled

    def set_active_patient(
        self,
        request: Request,
        patient_id: str,
        set_by: str = "med-z1"
    ) -> bool:
        """Set active patient context."""
        if not self.enabled:
            logger.debug("CCOW is disabled; skipping")
            return False

        try:
            headers = {}

            if USE_MED_Z8_CCOW and USE_KEYCLOAK_AUTH:
                # Call med-z8 with JWT bearer token
                access_token = request.cookies.get("access_token")
                if not access_token:
                    logger.error("No access_token cookie found")
                    return False
                headers["Authorization"] = f"Bearer {access_token}"

            else:
                # Call embedded CCOW with session cookie
                session_id = request.cookies.get("session_id")
                if session_id:
                    headers["Cookie"] = f"session_id={session_id}"

            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={"patient_id": patient_id, "set_by": set_by},
                headers=headers,
                timeout=2.0,
            )
            response.raise_for_status()

            logger.info(f"Set CCOW active patient context to {patient_id}")
            return True

        except requests.RequestException as exc:
            logger.error(f"Failed to set CCOW context: {exc}")
            return False

    def get_active_patient(self, request: Request) -> Optional[str]:
        """Get active patient ICN from CCOW."""
        if not self.enabled:
            return None

        try:
            headers = {}

            if USE_MED_Z8_CCOW and USE_KEYCLOAK_AUTH:
                # Call med-z8 with JWT bearer token
                access_token = request.cookies.get("access_token")
                if not access_token:
                    return None
                headers["Authorization"] = f"Bearer {access_token}"

            else:
                # Call embedded CCOW with session cookie
                session_id = request.cookies.get("session_id")
                if session_id:
                    headers["Cookie"] = f"session_id={session_id}"

            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                headers=headers,
                timeout=2.0,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()
            return data.get("patient_id")

        except requests.RequestException as exc:
            logger.error(f"Failed to get CCOW context: {exc}")
            return None

    def clear_active_patient(
        self,
        request: Request,
        cleared_by: str = "med-z1"
    ) -> bool:
        """Clear active patient context."""
        if not self.enabled:
            return False

        try:
            headers = {}

            if USE_MED_Z8_CCOW and USE_KEYCLOAK_AUTH:
                # Call med-z8 with JWT bearer token
                access_token = request.cookies.get("access_token")
                if not access_token:
                    return False
                headers["Authorization"] = f"Bearer {access_token}"

            else:
                # Call embedded CCOW with session cookie
                session_id = request.cookies.get("session_id")
                if session_id:
                    headers["Cookie"] = f"session_id={session_id}"

            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by},
                headers=headers,
                timeout=2.0,
            )

            if response.status_code == 404:
                logger.warning("No active CCOW context to clear")
                return False

            response.raise_for_status()
            logger.info("Cleared CCOW active patient context")
            return True

        except requests.RequestException as exc:
            logger.error(f"Failed to clear CCOW context: {exc}")
            return False


# Global client instance
ccow_client = CCOWClient()
```

**No changes needed to route files!** The updated CCOW client handles both modes transparently.

### 7.2 Testing med-z8 Integration

```bash
# 1. Start med-z8 service
cd /path/to/med-z8
docker-compose up -d

# 2. Enable med-z8 integration in med-z1
# Edit .env:
USE_KEYCLOAK_AUTH=true
USE_MED_Z8_CCOW=true

# 3. Restart med-z1
uvicorn app.main:app --reload

# 4. Test CCOW flow
# - Login to med-z1
# - Select a patient
# - Check med-z8 logs: should see "Set context for user_id: ..."
# - Navigate to different pages (vitals, meds)
# - Patient context should persist
```

---

## 8. Phase 3: Cleanup and Deprecation

### 8.1 Remove Legacy Authentication Code

Once Keycloak authentication is stable and all users migrated:

```bash
# 1. Set feature flags permanently
# Edit config.py: Remove USE_KEYCLOAK_AUTH checks, make OIDC default

# 2. Delete legacy auth code
rm -rf app/db/auth.py  # Old session management
# Remove session-based logic from app/routes/auth.py
# Remove session-based logic from app/middleware/auth.py

# 3. Drop old auth tables (after backup!)
psql -U postgres -d med_z1 -c "DROP TABLE IF EXISTS auth.sessions CASCADE;"
# Keep auth.users for reference, or migrate to Keycloak user federation
```

### 8.2 Remove Embedded CCOW Service

```bash
# 1. Delete CCOW subsystem from med-z1
rm -rf ccow/

# 2. Remove CCOW from docker-compose.yml
# (No longer starting embedded CCOW service)

# 3. Update documentation
# - Update CLAUDE.md to reference med-z8
# - Update README.md to remove CCOW setup instructions
```

### 8.3 Update Documentation

| Document | Update Required |
|----------|-----------------|
| `CLAUDE.md` | Remove CCOW subsystem, reference med-z8 |
| `README.md` | Update auth setup (Keycloak), remove session config |
| `docs/architecture.md` | Add ADR for Keycloak migration |
| `app/README.md` | Update authentication patterns |

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# app/tests/test_oidc_auth.py (NEW)

import pytest
from app.auth.oidc import validate_jwt, get_current_user_from_jwt


@pytest.mark.asyncio
async def test_validate_jwt_success(valid_jwt_token, mock_jwks):
    """Test JWT validation with valid token."""
    claims = await validate_jwt(valid_jwt_token)
    assert claims["sub"] == "user-123"
    assert claims["email"] == "user@va.gov"


@pytest.mark.asyncio
async def test_validate_jwt_expired(expired_jwt_token):
    """Test JWT validation rejects expired token."""
    with pytest.raises(HTTPException) as exc_info:
        await validate_jwt(expired_jwt_token)
    assert exc_info.value.status_code == 401
```

### 9.2 Integration Tests

```python
# app/tests/test_auth_integration.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_unauthenticated_redirect_to_login():
    """Test that unauthenticated requests redirect to Keycloak."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_authenticated_access(mock_keycloak_jwt):
    """Test that authenticated requests succeed."""
    response = client.get(
        "/dashboard",
        cookies={"access_token": mock_keycloak_jwt}
    )
    assert response.status_code == 200
```

### 9.3 Manual Testing Checklist

- [ ] Login flow works (redirect to Keycloak → login → redirect back)
- [ ] Dashboard loads after login
- [ ] Patient selection works
- [ ] CCOW context persists across pages
- [ ] Logout clears access_token cookie
- [ ] Token expiration redirects to login (wait 15+ min)
- [ ] SSO works (login to med-z1 → auto-login to CPRS simulator)

---

## 10. Rollback Plan

### 10.1 Rollback Triggers

Rollback to legacy authentication if:
- Login failure rate > 10%
- Page load time increases > 20%
- Critical bugs in JWT validation
- Keycloak service unavailable for > 5 minutes

### 10.2 Rollback Procedure

```bash
# 1. Disable Keycloak authentication
# Edit .env:
USE_KEYCLOAK_AUTH=false
USE_MED_Z8_CCOW=false

# 2. Restart med-z1
pkill -f "uvicorn app.main"
uvicorn app.main:app --reload

# 3. Verify legacy auth works
# Visit: http://localhost:8000/login
# Login with PostgreSQL credentials

# 4. Monitor for stability
# Check logs, page load times, user reports
```

### 10.3 Data Preservation

- **No data loss**: Legacy `auth.users` and `auth.sessions` tables remain intact
- **User passwords**: Unchanged in PostgreSQL
- **Patient data**: Unaffected by authentication changes
- **CCOW context**: Ephemeral (in-memory), no persistence

---

## 11. Security Considerations

### 11.1 Security Comparison

| Aspect | Legacy Auth | Keycloak OIDC |
|--------|-------------|---------------|
| **Password Storage** | bcrypt (PostgreSQL) | Keycloak (bcrypt + salting) |
| **Token Type** | Opaque UUID | JWT (signed, claims-based) |
| **Token Validation** | Database query | Signature validation (stateless) |
| **Session Storage** | PostgreSQL | Keycloak (server-side) |
| **Token Expiration** | Manual (expires_at check) | Automatic (JWT exp claim) |
| **Token Refresh** | Not supported | Refresh tokens supported |
| **SSO** | None | Full SSO across apps |
| **HTTPS** | Required in production | Required in production |

### 11.2 Security Checklist

- [ ] Keycloak served over HTTPS in production
- [ ] JWT signature validated on every request
- [ ] JWT expiration enforced (exp claim)
- [ ] HttpOnly cookies for access_token
- [ ] SameSite=Lax for CSRF protection
- [ ] Client secrets stored in environment variables (not code)
- [ ] JWKS fetched over HTTPS
- [ ] Audit logging enabled (login, logout, token refresh)

---

## 12. Implementation Checklist

### Phase 1: Keycloak OIDC Integration (Weeks 1-3)

- [ ] **Week 1: Setup**
  - [ ] Add Keycloak to docker-compose.yml
  - [ ] Start Keycloak service
  - [ ] Create va-development realm
  - [ ] Create med-z1 client in Keycloak
  - [ ] Migrate users to Keycloak (manual or script)
  - [ ] Install authlib, httpx dependencies

- [ ] **Week 2: Implementation**
  - [ ] Create app/auth/oidc.py (JWT validation)
  - [ ] Update config.py (Keycloak config)
  - [ ] Update .env (Keycloak URLs, secrets)
  - [ ] Update app/routes/auth.py (OIDC login/logout)
  - [ ] Update app/middleware/auth.py (JWT middleware)
  - [ ] Add feature flag: USE_KEYCLOAK_AUTH

- [ ] **Week 3: Testing**
  - [ ] Unit tests for JWT validation
  - [ ] Integration tests for login flow
  - [ ] Manual testing (login, logout, token expiration)
  - [ ] Performance testing (JWT validation latency)
  - [ ] Enable USE_KEYCLOAK_AUTH=true in staging

### Phase 2: CCOW Client Update (Weeks 4-5)

- [ ] **Week 4: med-z8 Deployment**
  - [ ] Deploy med-z8 service (see med-z8-ccow-service-design.md)
  - [ ] Configure med-z8 for Keycloak JWT validation
  - [ ] Test med-z8 independently (curl, Postman)

- [ ] **Week 5: Integration**
  - [ ] Update app/utils/ccow_client.py (JWT bearer tokens)
  - [ ] Add feature flag: USE_MED_Z8_CCOW
  - [ ] Test CCOW integration (patient selection, context sync)
  - [ ] Enable USE_MED_Z8_CCOW=true in staging

### Phase 3: Cleanup and Deprecation (Week 6)

- [ ] Enable feature flags permanently in production
- [ ] Remove legacy auth code
- [ ] Remove embedded CCOW subsystem
- [ ] Drop auth.sessions table (after backup)
- [ ] Update all documentation
- [ ] Announce migration complete to users

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-08 | System | Initial med-z1 Keycloak migration specification |

---

**End of Document**
