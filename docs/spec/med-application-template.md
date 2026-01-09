# med-* Application Template – Design Specification

**Document Version:** v1.0
**Date:** 2026-01-08
**Status:** ✅ TEMPLATE (Ready for use)
**Target Audience:** Developers creating new med-* family applications

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Project Structure](#3-project-structure)
4. [Quick Start](#4-quick-start)
5. [Authentication Integration (Keycloak OIDC)](#5-authentication-integration-keycloak-oidc)
6. [CCOW Integration (med-z8)](#6-ccow-integration-med-z8)
7. [Common Patterns](#7-common-patterns)
8. [Configuration](#8-configuration)
9. [Testing](#9-testing)
10. [Deployment](#10-deployment)
11. [Best Practices](#11-best-practices)

---

## 1. Overview

### 1.1 Purpose

This document provides a **template and reference guide** for building new applications in the **med-* family** (med-z1, med-z2, med-z3, etc.). It ensures consistency across applications and provides battle-tested patterns for:

- **Authentication**: Keycloak OIDC (OAuth 2.0 / OpenID Connect)
- **Patient Context**: med-z8 CCOW Context Vault integration
- **Technology Stack**: Python 3.11+, FastAPI, HTMX, Jinja2
- **Deployment**: Docker, Docker Compose, Kubernetes

### 1.2 Architecture Principles

All med-* applications follow these principles:

1. **Shared Identity Provider**: Use Keycloak for authentication (SSO across all apps)
2. **Shared Context Service**: Use med-z8 for patient context synchronization
3. **Stateless Authentication**: JWT bearer tokens (no session database)
4. **Minimal JavaScript**: Prefer HTMX for interactivity (server-side rendering)
5. **API-First**: FastAPI with OpenAPI documentation
6. **Container-Native**: Docker images, docker-compose for dev, Kubernetes for prod

### 1.3 Example Applications

| Application | Port | Purpose |
|-------------|------|---------|
| **med-z1** | 8000 | Longitudinal Health Record Viewer |
| **med-z2** (example) | 8002 | CPRS Simulator |
| **med-z3** (example) | 8003 | Imaging Viewer |
| **med-z8** | 8001 | CCOW Context Vault (shared service) |
| **Keycloak** | 8080 | Identity Provider (shared service) |

### 1.4 When to Use This Template

Use this template when:
- ✅ Building a new clinical application in the VA ecosystem
- ✅ Need SSO integration with existing med-* applications
- ✅ Need patient context synchronization (CCOW)
- ✅ Want to follow established med-* patterns

Do NOT use this template if:
- ❌ Building a standalone app with no SSO requirements
- ❌ Need a different tech stack (not Python/FastAPI)
- ❌ Building a non-clinical application

---

## 2. Prerequisites

### 2.1 Required Services

Before building a med-* application, ensure these services are running:

| Service | Port | Setup Guide |
|---------|------|-------------|
| **Keycloak** | 8080 | See med-z8-ccow-service-design.md, Section 8.1 |
| **med-z8 CCOW** | 8001 | See med-z8-ccow-service-design.md |
| **PostgreSQL** (optional) | 5432 | For application-specific data storage |

### 2.2 Required Configuration

1. **Keycloak Realm**: `va-development` (or your environment-specific realm)
2. **Keycloak Client**: Create a new client for your application (e.g., `med-z2-cprs`)
3. **Redirect URIs**: Configure in Keycloak (e.g., `http://localhost:8002/*`)

### 2.3 Development Tools

- Python 3.11+
- Docker / Docker Compose
- Git
- IDE (VS Code, PyCharm, etc.)

---

## 3. Project Structure

### 3.1 Recommended Directory Structure

```
med-z{N}/                           # Replace {N} with your app number
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── config.py                   # Configuration management
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── oidc.py                 # Keycloak OIDC integration
│   │   └── dependencies.py         # FastAPI auth dependencies
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication middleware
│   │   └── logging.py              # Request logging
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login/logout routes
│   │   ├── dashboard.py            # Main dashboard
│   │   └── patient.py              # Patient-specific routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ccow_client.py          # med-z8 CCOW client
│   │   └── patient_service.py      # Business logic
│   ├── templates/
│   │   ├── base.html               # Base Jinja2 template
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── patient.html
│   └── static/
│       ├── css/
│       │   └── styles.css
│       └── js/
│           └── htmx.min.js
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_routes.py
│   └── test_ccow.py
├── .env.template                   # Environment variables template
├── .env                            # Environment variables (gitignored)
├── .gitignore
├── config.py                       # Root-level config (imports app/config.py)
├── docker-compose.yml              # Local development stack
├── Dockerfile                      # Container image
├── requirements.txt                # Python dependencies
├── pytest.ini                      # pytest configuration
├── README.md                       # Getting started guide
└── docs/
    ├── architecture.md
    └── api.md
```

### 3.2 Core Dependencies

```txt
# requirements.txt

# Web Framework
fastapi==0.108.0
uvicorn[standard]==0.25.0

# Authentication
authlib==1.3.0
httpx==0.26.0

# Templating
jinja2==3.1.2

# Database (optional, if needed)
psycopg2-binary==2.9.9
sqlalchemy==2.0.25

# Utilities
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0

# HTTP Client (for med-z8 CCOW calls)
requests==2.31.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

---

## 4. Quick Start

### 4.1 Create New Application from Template

```bash
# 1. Create project directory
mkdir med-z2-cprs
cd med-z2-cprs

# 2. Create project structure
mkdir -p app/{auth,middleware,routes,services,templates,static/{css,js}}
mkdir -p tests docs

# 3. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 4. Create requirements.txt (copy from Section 3.2)
# 5. Install dependencies
pip install -r requirements.txt

# 6. Copy boilerplate files (see sections below)
```

### 4.2 Register Application in Keycloak

```bash
# Access Keycloak admin console
open http://localhost:8080/admin

# Login: admin / admin
# Realm: va-development
# Clients → Create client

# Client configuration:
# - Client ID: med-z2-cprs
# - Name: CPRS Simulator
# - Client Protocol: openid-connect
# - Access Type: confidential
# - Standard Flow Enabled: ON
# - Direct Access Grants: OFF
# - Valid Redirect URIs: http://localhost:8002/*
# - Web Origins: http://localhost:8002

# Save → Credentials tab → Copy Client Secret
```

### 4.3 Create Configuration

```bash
# Create .env file
cat > .env << 'EOF'
# Application Settings
APP_NAME=med-z2-cprs
APP_PORT=8002
DEBUG=true
LOG_LEVEL=INFO

# Keycloak Configuration
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=va-development
KEYCLOAK_CLIENT_ID=med-z2-cprs
KEYCLOAK_CLIENT_SECRET=<paste-from-keycloak>

# med-z8 CCOW Configuration
CCOW_ENABLED=true
CCOW_URL=http://localhost:8001

# Database (optional, if needed)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/med_z2
EOF
```

---

## 5. Authentication Integration (Keycloak OIDC)

### 5.1 Configuration Module

```python
# config.py (root level)

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)


def _get_bool(key: str, default: bool = False) -> bool:
    """Parse boolean from environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "yes", "1", "on")


# -----------------------------------------------------------
# Application Settings
# -----------------------------------------------------------

APP_NAME = os.getenv("APP_NAME", "med-z-app")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = _get_bool("DEBUG", default=False)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# -----------------------------------------------------------
# Keycloak / OIDC Configuration
# -----------------------------------------------------------

KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "va-development")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "med-z-app")
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

# -----------------------------------------------------------
# med-z8 CCOW Configuration
# -----------------------------------------------------------

CCOW_ENABLED = _get_bool("CCOW_ENABLED", default=True)
CCOW_URL = os.getenv("CCOW_URL", "http://localhost:8001")

CCOW_CONFIG = {
    "enabled": CCOW_ENABLED,
    "url": CCOW_URL,
}

# -----------------------------------------------------------
# Database Configuration (optional)
# -----------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "")
```

### 5.2 OIDC Authentication Module

```python
# app/auth/oidc.py

from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt, JoseError
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
    2. access_token cookie

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
        # Fallback to cookie
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token"
        )

    # Validate JWT
    claims = await validate_jwt(token)

    return {
        "user_id": claims["sub"],
        "email": claims.get("email"),
        "display_name": claims.get("name") or claims.get("preferred_username"),
    }
```

### 5.3 Authentication Routes

```python
# app/routes/auth.py

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.auth.oidc import oauth
from config import OIDC_CONFIG
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


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

        logger.info(f"User logged in: {token.get('userinfo', {}).get('email')}")

        # Create response and set cookies
        response = RedirectResponse(url="/dashboard", status_code=303)

        # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=token["access_token"],
            httponly=True,
            secure=False,  # Set True in production (HTTPS)
            samesite="lax",
            max_age=token.get("expires_in", 900),
        )

        # Set refresh token cookie
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
        return RedirectResponse(url="/login?error=auth_failed", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    """Logout from application and optionally from Keycloak (SSO logout)."""
    # Clear cookies
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    # Optional: SSO logout (uncomment to enable)
    # post_logout_redirect_uri = str(request.url_for("login"))
    # keycloak_logout_url = f"{OIDC_CONFIG['logout_endpoint']}?post_logout_redirect_uri={post_logout_redirect_uri}"
    # return RedirectResponse(keycloak_logout_url)

    return response
```

### 5.4 Authentication Middleware

```python
# app/middleware/auth.py

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import RedirectResponse
from app.auth.oidc import get_current_user_from_jwt
import logging

logger = logging.getLogger(__name__)


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
```

### 5.5 FastAPI Application Setup

```python
# app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.middleware.auth import AuthMiddleware
from app.routes import auth, dashboard
from config import APP_NAME, DEBUG
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    debug=DEBUG,
)

# Add middleware
app.add_middleware(AuthMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(dashboard.router, tags=["Dashboard"])


@app.get("/health")
async def health_check():
    """Health check endpoint (no auth required)."""
    return {"status": "healthy", "service": APP_NAME}


if __name__ == "__main__":
    import uvicorn
    from config import APP_PORT
    uvicorn.run("app.main:app", host="0.0.0.0", port=APP_PORT, reload=DEBUG)
```

---

## 6. CCOW Integration (med-z8)

### 6.1 CCOW Client

```python
# app/services/ccow_client.py

import logging
from typing import Optional, Dict, Any
import requests
from fastapi import Request
from config import CCOW_CONFIG

logger = logging.getLogger(__name__)


class CCOWClient:
    """HTTP client for interacting with med-z8 CCOW Context Vault."""

    def __init__(self, base_url: str = None, enabled: bool = None):
        self.base_url = (base_url or CCOW_CONFIG["url"]).rstrip("/")
        self.enabled = enabled if enabled is not None else CCOW_CONFIG["enabled"]

    def set_active_patient(
        self,
        request: Request,
        patient_id: str,
        set_by: str = None
    ) -> bool:
        """
        Set active patient context in med-z8.

        Args:
            request: FastAPI Request (contains JWT in cookie)
            patient_id: Patient ICN
            set_by: Application name (defaults to APP_NAME from config)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("CCOW is disabled; skipping")
            return False

        try:
            # Extract JWT access token from cookie
            access_token = request.cookies.get("access_token")
            if not access_token:
                logger.error("No access_token cookie found")
                return False

            # Call med-z8 with JWT bearer token
            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={
                    "patient_id": patient_id,
                    "set_by": set_by or CCOW_CONFIG.get("app_name", "med-z-app")
                },
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=2.0,
            )
            response.raise_for_status()

            logger.info(f"Set CCOW active patient context to {patient_id}")
            return True

        except requests.RequestException as exc:
            logger.error(f"Failed to set CCOW context: {exc}")
            return False

    def get_active_patient(self, request: Request) -> Optional[str]:
        """
        Get active patient ICN from med-z8.

        Returns:
            Patient ICN if context exists, None otherwise
        """
        if not self.enabled:
            return None

        try:
            access_token = request.cookies.get("access_token")
            if not access_token:
                return None

            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                headers={"Authorization": f"Bearer {access_token}"},
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

    def get_active_patient_context(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Get full active patient context (with metadata) from med-z8.

        Returns:
            Full PatientContext dict if exists, None otherwise
        """
        if not self.enabled:
            return None

        try:
            access_token = request.cookies.get("access_token")
            if not access_token:
                return None

            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=2.0,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            logger.error(f"Failed to get CCOW context: {exc}")
            return None

    def clear_active_patient(
        self,
        request: Request,
        cleared_by: str = None
    ) -> bool:
        """
        Clear active patient context in med-z8.

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            access_token = request.cookies.get("access_token")
            if not access_token:
                return False

            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by or CCOW_CONFIG.get("app_name", "med-z-app")},
                headers={"Authorization": f"Bearer {access_token}"},
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

### 6.2 Using CCOW Client in Routes

```python
# app/routes/patient.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ccow_client import ccow_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/patient/{patient_id}", response_class=HTMLResponse)
async def patient_overview(patient_id: str, request: Request):
    """
    Patient overview page.

    Sets active patient in CCOW when user navigates to patient.
    """
    # Get user from request.state (injected by AuthMiddleware)
    user = request.state.user

    # Set active patient in CCOW
    ccow_client.set_active_patient(request, patient_id=patient_id, set_by="med-z2-cprs")

    # Fetch patient data (your business logic here)
    patient = {
        "icn": patient_id,
        "name": "John Doe",
        "dob": "1950-01-15",
        # ... other patient data
    }

    return templates.TemplateResponse(
        "patient.html",
        {
            "request": request,
            "user": user,
            "patient": patient,
        }
    )
```

### 6.3 Dashboard with CCOW Context Restoration

```python
# app/routes/dashboard.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ccow_client import ccow_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Main dashboard page.

    Automatically restores active patient from CCOW if available.
    """
    user = request.state.user

    # Try to restore active patient from CCOW
    active_patient_icn = ccow_client.get_active_patient(request)

    active_patient = None
    if active_patient_icn:
        # Fetch patient data for active patient
        active_patient = {
            "icn": active_patient_icn,
            "name": "Jane Smith",  # Replace with actual data fetch
            # ... other patient data
        }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "active_patient": active_patient,
        }
    )
```

---

## 7. Common Patterns

### 7.1 Template Base (Jinja2)

```html
<!-- app/templates/base.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ APP_NAME }}{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    <script src="/static/js/htmx.min.js"></script>
</head>
<body>
    <!-- Top Navigation Bar -->
    <nav class="topbar">
        <div class="topbar-left">
            <h1>{{ APP_NAME }}</h1>
        </div>
        <div class="topbar-right">
            {% if user %}
                <span>{{ user.display_name }} ({{ user.email }})</span>
                <form action="/logout" method="post" style="display: inline;">
                    <button type="submit">Logout</button>
                </form>
            {% endif %}
        </div>
    </nav>

    <!-- Main Content -->
    <main class="content">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer>
        <p>&copy; 2026 VA Healthcare - {{ APP_NAME }}</p>
    </footer>
</body>
</html>
```

### 7.2 Dashboard Template

```html
<!-- app/templates/dashboard.html -->

{% extends "base.html" %}

{% block title %}Dashboard - {{ APP_NAME }}{% endblock %}

{% block content %}
<div class="dashboard">
    <h2>Dashboard</h2>

    {% if active_patient %}
        <div class="active-patient-banner">
            <strong>Active Patient:</strong>
            {{ active_patient.name }} ({{ active_patient.icn }})
            <a href="/patient/{{ active_patient.icn }}">View Details</a>
        </div>
    {% else %}
        <div class="no-active-patient">
            <p>No active patient selected. Search for a patient to begin.</p>
        </div>
    {% endif %}

    <!-- Patient Search -->
    <div class="patient-search">
        <h3>Patient Search</h3>
        <form hx-get="/api/patients/search" hx-target="#search-results">
            <input type="text" name="query" placeholder="Search by name or ICN">
            <button type="submit">Search</button>
        </form>
        <div id="search-results"></div>
    </div>
</div>
{% endblock %}
```

### 7.3 Error Handling

```python
# app/main.py (add exception handlers)

from fastapi import Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions (401, 404, etc.)."""
    if exc.status_code == 401:
        # Redirect to login for unauthenticated requests
        return RedirectResponse(url="/login", status_code=303)

    # For other errors, return JSON or HTML based on Accept header
    if "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "status_code": exc.status_code, "detail": exc.detail},
            status_code=exc.status_code
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

---

## 8. Configuration

### 8.1 Environment Variables Template

```bash
# .env.template (commit to git)

# Application Settings
APP_NAME=med-z{N}-app-name
APP_PORT=800{N}
DEBUG=true
LOG_LEVEL=INFO

# Keycloak Configuration
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=va-development
KEYCLOAK_CLIENT_ID=med-z{N}-app-name
KEYCLOAK_CLIENT_SECRET=<get-from-keycloak-admin>

# med-z8 CCOW Configuration
CCOW_ENABLED=true
CCOW_URL=http://localhost:8001

# Database (optional, if needed)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/med_z{N}

# Redis (optional, if needed)
REDIS_URL=redis://localhost:6379/0
```

### 8.2 Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  # Your application
  app:
    build: .
    container_name: med-z{N}-app
    environment:
      KEYCLOAK_SERVER_URL: http://keycloak:8080
      KEYCLOAK_REALM: va-development
      KEYCLOAK_CLIENT_ID: med-z{N}-app
      KEYCLOAK_CLIENT_SECRET: ${KEYCLOAK_CLIENT_SECRET}
      CCOW_URL: http://med-z8-ccow:8001
    ports:
      - "800{N}:800{N}"
    depends_on:
      - keycloak
      - med-z8-ccow
    networks:
      - med-network

  # Keycloak (shared)
  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    container_name: med-keycloak
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
      KC_HTTP_ENABLED: "true"
      KC_HOSTNAME_STRICT_HTTPS: "false"
    command: start-dev
    ports:
      - "8080:8080"
    networks:
      - med-network

  # med-z8 CCOW (shared)
  med-z8-ccow:
    image: ghcr.io/va/med-z8-ccow:latest
    container_name: med-z8-ccow
    environment:
      KEYCLOAK_SERVER_URL: http://keycloak:8080
      KEYCLOAK_REALM: va-development
    ports:
      - "8001:8001"
    depends_on:
      - keycloak
    networks:
      - med-network

networks:
  med-network:
    driver: bridge
```

---

## 9. Testing

### 9.1 Unit Tests

```python
# tests/test_auth.py

import pytest
from app.auth.oidc import validate_jwt


@pytest.mark.asyncio
async def test_validate_jwt_success(valid_jwt_token, mock_jwks):
    """Test JWT validation with valid token."""
    claims = await validate_jwt(valid_jwt_token)
    assert claims["sub"] == "user-123"
    assert claims["email"] == "user@va.gov"
```

### 9.2 Integration Tests

```python
# tests/test_routes.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint (no auth required)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_unauthenticated_redirect():
    """Test that unauthenticated requests redirect to login."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
```

---

## 10. Deployment

### 10.1 Dockerfile

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY config.py .

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')"

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### 10.2 Kubernetes Deployment

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: med-z{N}-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: med-z{N}-app
  template:
    metadata:
      labels:
        app: med-z{N}-app
    spec:
      containers:
      - name: app
        image: ghcr.io/va/med-z{N}-app:latest
        ports:
        - containerPort: 800{N}
        env:
        - name: KEYCLOAK_SERVER_URL
          value: "https://keycloak.va.gov"
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: med-z{N}-secrets
              key: keycloak-client-secret
        livenessProbe:
          httpGet:
            path: /health
            port: 800{N}
        readinessProbe:
          httpGet:
            path: /health
            port: 800{N}
```

---

## 11. Best Practices

### 11.1 Security Checklist

- [ ] Use HTTPS in production (TLS certificates)
- [ ] Store secrets in environment variables (not code)
- [ ] Validate JWT on every authenticated request
- [ ] Use HttpOnly cookies for tokens
- [ ] Set SameSite=Lax for CSRF protection
- [ ] Implement rate limiting (future)
- [ ] Log authentication events (login, logout, failures)

### 11.2 Code Quality

- [ ] Write unit tests (80%+ coverage target)
- [ ] Write integration tests for all routes
- [ ] Use type hints throughout codebase
- [ ] Run linters (ruff, black, mypy)
- [ ] Document all public functions/classes

### 11.3 Performance

- [ ] Cache JWKS (avoid repeated Keycloak requests)
- [ ] Use async/await for I/O operations
- [ ] Minimize CCOW calls (cache patient context in session if needed)
- [ ] Monitor response times (< 500ms p95 target)

### 11.4 Observability

- [ ] Structured logging (JSON format)
- [ ] Health check endpoint
- [ ] Metrics endpoint (Prometheus format, future)
- [ ] Error tracking (Sentry, future)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-08 | System | Initial template for med-* family applications |

---

**End of Document**
