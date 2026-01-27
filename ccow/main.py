# ---------------------------------------------------------------------
# main.py
# ---------------------------------------------------------------------
# FastAPI application providing HTTP REST API for CCOW Context Vault.
#
# Version: v2.1 (Cross-Application Authentication Enhancement)
# Date: 2026-01-27
#
# Exposes the shared ContextVault singleton (from vault.py) via HTTP
# endpoints, enabling distributed applications to synchronize patient
# context across the med-z1 ecosystem. Each authenticated user maintains
# an independent patient context.
#
# v2.1 REST API Endpoints:
# - GET  /                          - Service info
# - GET  /ccow/health               - Health check
# - GET  /ccow/active-patient       - Get current user's patient context
# - PUT  /ccow/active-patient       - Set current user's patient context
# - DELETE /ccow/active-patient     - Clear current user's patient context
# - GET  /ccow/history?scope=user|global  - Get context change history
# - GET  /ccow/active-patients      - Get all active contexts (admin)
# - POST /ccow/cleanup              - Trigger stale context cleanup (admin)
#
# v2.1 Key Changes (2026-01-27):
# - Added X-Session-ID header support for cross-application integration
# - Enables external CCOW-aware apps (med-z4, CPRS) to authenticate
# - Maintains backward compatibility with session_id cookie
# - Session validation uses UTC timestamps (via auth_helper)
# - Smart timezone handling (supports both timezone-aware and naive datetimes)
#
# v2.0 Key Changes (2025-12-20):
# - All endpoints (except health) require authentication
# - user_id extracted from validated session (not trusted from request body)
# - Context operations are user-scoped (multi-user isolation)
# - History can be filtered by user or global scope
#
# Authentication Methods (v2.1):
# 1. X-Session-ID header (priority) - for external CCOW-aware applications
# 2. session_id cookie (fallback) - for med-z1 browser-based sessions
#
# Both methods validate against shared auth.sessions table (PostgreSQL):
# - Session UUIDs are validated for existence, active status, expiration
# - Timezone-aware expiration checks (UTC standard)
# - user_id extracted from database, not request parameters
# - Prevents user_id spoofing attacks
#
# Session Management:
# - All applications (med-z1, med-z4) write to same auth.sessions table
# - Session timestamps use UTC for consistency across timezones
# - See: docs/spec/timezone-and-session-management.md for integration details
#
# Auto-generated API docs available at:
# - Swagger UI: http://localhost:8001/docs
# - ReDoc: http://localhost:8001/redoc
# ---------------------------------------------------------------------

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from .vault import vault
from .auth_helper import get_user_from_session
from .models import (
    PatientContext,
    SetPatientContextRequest,
    ClearPatientContextRequest,
    GetAllActiveContextsResponse,
    GetHistoryResponse,
    CleanupResponse,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CCOW Context Vault",
    description="Multi-user CCOW-style patient context synchronization service (v2.1)",
    version="2.1.0",
)

# CORS configuration (development-friendly; tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, restrict to known frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# Authentication Dependency
# ---------------------------------------------------------------------

def get_session_id_from_request(request: Request) -> Optional[str]:
    """
    Extract session_id from request, supporting multiple auth methods.

    Priority order:
    1. X-Session-ID header (for cross-application CCOW integration)
    2. session_id cookie (for med-z1 internal routes)

    This enables:
    - med-z1 (port 8000): Cookie-based auth (browser sessions)
    - med-z4 (port 8002): Header-based auth (httpx client)
    - CPRS/external apps: Either method

    Args:
        request: FastAPI Request object

    Returns:
        Session UUID string, or None if not found

    Example Usage:
        # med-z1 (cookie-based):
        GET /ccow/active-patient
        Cookie: session_id=<uuid>

        # med-z4 (header-based):
        GET /ccow/active-patient
        X-Session-ID: <uuid>
    """
    # Check header first (explicit cross-app authentication)
    session_id = request.headers.get("X-Session-ID")
    if session_id:
        logger.debug("Session extracted from X-Session-ID header")
        return session_id

    # Fall back to cookie (med-z1 browser-based sessions)
    session_id = request.cookies.get("session_id")
    if session_id:
        logger.debug("Session extracted from session_id cookie")
        return session_id

    return None


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and validate user from session.

    Supports authentication via:
    - X-Session-ID header (external CCOW-aware apps like med-z4)
    - session_id cookie (med-z1 internal use)

    This function:
    1. Extracts session_id from header (priority) or cookie (fallback)
    2. Validates session against auth.sessions table
    3. Checks session is active and not expired
    4. Returns user information (user_id, email, display_name)

    Raises:
        HTTPException(401) if session is missing, invalid, or expired

    Returns:
        Dictionary with user info:
        {
            "user_id": str,        # User UUID (authoritative)
            "email": str,          # User email
            "display_name": str,   # User display name
        }
    """
    session_id = get_session_id_from_request(request)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication: X-Session-ID header or session_id cookie required"
        )

    user = get_user_from_session(session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return user


# ---------------------------------------------------------------------
# Public Endpoints (No Authentication Required)
# ---------------------------------------------------------------------

@app.get("/")
async def root():
    """Root endpoint for quick service introspection."""
    return {
        "service": "ccow",
        "message": "CCOW Context Vault v2.1 (Multi-User + Cross-App Auth) is running",
        "version": "2.1.0",
    }


@app.get("/ccow/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ccow-vault",
        "version": "2.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "active_contexts": vault.get_context_count(),
    }


# ---------------------------------------------------------------------
# User Context Endpoints (Authentication Required)
# ---------------------------------------------------------------------

@app.get("/ccow/active-patient", response_model=PatientContext)
async def get_active_patient(user: Dict = Depends(get_current_user)):
    """
    Get the current user's active patient context.

    Authentication:
        - X-Session-ID header (external apps), OR
        - session_id cookie (med-z1)

    Returns:
        PatientContext for the current user

    Raises:
        401: If session is invalid or expired
        404: If user has no active patient context
    """
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
    """
    Set or update the current user's active patient context.

    Authentication:
        - X-Session-ID header (external apps), OR
        - session_id cookie (med-z1)

    Request Body:
        {
            "patient_id": str,  # Patient ICN
            "set_by": str       # Application name (default: "med-z1")
        }

    Returns:
        PatientContext with user_id, patient_id, timestamps

    Security Note:
        user_id is extracted from validated session, NOT from request body.
        This prevents user_id spoofing attacks.
    """
    context = vault.set_context(
        user_id=user["user_id"],
        patient_id=request.patient_id,
        set_by=request.set_by,
        email=user.get("email"),
    )
    return context


@app.delete("/ccow/active-patient", status_code=status.HTTP_204_NO_CONTENT)
async def clear_active_patient(
    request: Optional[ClearPatientContextRequest] = None,
    user: Dict = Depends(get_current_user)
):
    """
    Clear the current user's active patient context.

    Authentication:
        - X-Session-ID header (external apps), OR
        - session_id cookie (med-z1)

    Request Body (optional):
        {
            "cleared_by": str  # Application name (default: "unknown")
        }

    Returns:
        204 No Content on success

    Raises:
        401: If session is invalid or expired
        404: If user has no active patient context to clear
    """
    cleared_by = request.cleared_by if request else None
    cleared = vault.clear_context(
        user_id=user["user_id"],
        cleared_by=cleared_by,
        email=user.get("email"),
    )

    if not cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context to clear",
        )

    return None


# ---------------------------------------------------------------------
# History Endpoints (Authentication Required)
# ---------------------------------------------------------------------

@app.get("/ccow/history", response_model=GetHistoryResponse)
async def get_context_history(
    scope: str = "user",
    user: Dict = Depends(get_current_user)
):
    """
    Get context change history, filtered by scope.

    Authentication:
        - X-Session-ID header (external apps), OR
        - session_id cookie (med-z1)

    Query Parameters:
        - scope: str (default: "user")
            - "user": Only events for current user
            - "global": All events from all users (admin/debugging)

    Returns:
        GetHistoryResponse with:
        - history: List of ContextHistoryEntry objects
        - scope: str ("user" or "global")
        - total_count: int
        - user_id: str (if scope="user")

    Raises:
        401: If session is invalid or expired
        400: If scope is invalid
    """
    if scope not in ("user", "global"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope: {scope}. Must be 'user' or 'global'",
        )

    try:
        history = vault.get_history(
            user_id=user["user_id"] if scope == "user" else None,
            scope=scope
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return GetHistoryResponse(
        history=history,
        scope=scope,
        total_count=len(history),
        user_id=user["user_id"] if scope == "user" else None,
    )


# ---------------------------------------------------------------------
# Admin Endpoints (Authentication Required)
# ---------------------------------------------------------------------

@app.get("/ccow/active-patients", response_model=GetAllActiveContextsResponse)
async def get_all_active_patients(user: Dict = Depends(get_current_user)):
    """
    Get all active patient contexts across all users (admin/debugging).

    Authentication:
        - X-Session-ID header (external apps), OR
        - session_id cookie (med-z1)

    Returns:
        GetAllActiveContextsResponse with:
        - contexts: List of all PatientContext objects
        - total_count: int

    Note:
        This endpoint returns ALL users' contexts. In a production system,
        this should be restricted to admin users only via RBAC.
    """
    contexts = vault.get_all_contexts()
    return GetAllActiveContextsResponse(
        contexts=contexts,
        total_count=len(contexts),
    )


@app.post("/ccow/cleanup", response_model=CleanupResponse)
async def cleanup_stale_contexts(user: Dict = Depends(get_current_user)):
    """
    Trigger manual cleanup of stale contexts (admin/debugging).

    Authentication:
        - X-Session-ID header (external apps), OR
        - session_id cookie (med-z1)

    Returns:
        CleanupResponse with:
        - removed_count: Number of stale contexts removed
        - message: Success message

    Note:
        Removes contexts that haven't been accessed in 24 hours.
        In a production system, this should be restricted to admin users
        only via RBAC, or run automatically via scheduled task.
    """
    removed_count = vault.cleanup_stale_contexts()
    return CleanupResponse(
        removed_count=removed_count,
        message=f"Cleaned up {removed_count} stale context{'s' if removed_count != 1 else ''}"
    )
