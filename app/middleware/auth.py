# ---------------------------------------------------------------------
# app/middleware/auth.py
# ---------------------------------------------------------------------
# Authentication Middleware
# Enforces authentication on all routes except public endpoints.
# Validates sessions, extends session timeout on activity, and injects
# user context into request.state for use by routes.
# ---------------------------------------------------------------------

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
import logging

from app.db import auth as auth_db
from config import AUTH_CONFIG

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI.

    Validates user sessions on every request and enforces authentication
    for all routes except public endpoints (login, static assets).
    """

    # Public routes that don't require authentication
    PUBLIC_ROUTES = [
        "/login",           # Login page and form submission
        "/static",          # Static assets (CSS, JS, images)
        "/favicon.ico",     # Browser favicon requests
        "/docs",            # FastAPI auto-generated docs (development)
        "/openapi.json",    # OpenAPI schema (development)
        "/redoc",           # ReDoc documentation (development)
    ]

    async def dispatch(self, request: Request, call_next):
        """
        Process each request through authentication checks.

        Flow:
        1. Check if route is public (skip auth)
        2. Extract session_id from cookie
        3. Validate session (exists, active, not expired)
        4. Extend session timeout on activity
        5. Inject user context into request.state
        6. Continue to route handler
        """

        # Skip authentication for public routes
        if self._is_public_route(request.url.path):
            return await call_next(request)

        # Extract session_id from cookie
        session_id = request.cookies.get(AUTH_CONFIG["cookie_name"])

        if not session_id:
            logger.debug(f"No session cookie found for {request.url.path}")
            return self._redirect_to_login()

        # Validate session
        session = auth_db.get_session(session_id)

        if not session:
            logger.debug(f"Invalid or expired session: {session_id}")
            return self._redirect_to_login_with_cleared_cookie()

        if not session['is_active']:
            logger.debug(f"Inactive session: {session_id}")
            return self._redirect_to_login_with_cleared_cookie()

        # Check if session has expired
        # Compare with UTC if expires_at is timezone-aware, otherwise use timezone-naive comparison
        expires_at = session['expires_at']
        if expires_at.tzinfo is None:
            now = datetime.now()  # Timezone-naive (should not happen after fix, but handle gracefully)
        else:
            now = datetime.now(timezone.utc)  # Timezone-aware UTC

        if expires_at < now:
            logger.info(f"Session expired: {session_id}")
            auth_db.log_audit_event(
                event_type='session_timeout',
                user_id=session['user_id'],
                session_id=session_id,
                success=False,
                failure_reason='Session expired'
            )
            auth_db.invalidate_session(session_id)
            return self._redirect_to_login_with_cleared_cookie()

        # Extend session timeout (user activity detected)
        extended = auth_db.extend_session(session_id)
        if not extended:
            logger.warning(f"Failed to extend session: {session_id}")

        # Get user information
        user = auth_db.get_user_by_id(session['user_id'])

        if not user:
            logger.error(f"User not found for session: {session_id}")
            auth_db.invalidate_session(session_id)
            return self._redirect_to_login_with_cleared_cookie()

        # Check if user account is still active
        if not user['is_active']:
            logger.warning(f"Inactive user attempted access: {user['email']}")
            auth_db.invalidate_session(session_id)
            auth_db.log_audit_event(
                event_type='access_denied',
                user_id=user['user_id'],
                email=user['email'],
                session_id=session_id,
                success=False,
                failure_reason='Account inactive'
            )
            return self._redirect_to_login_with_cleared_cookie()

        # Inject user context into request state
        request.state.user = user
        request.state.session_id = session_id

        # Log successful request (debug level)
        logger.debug(f"Authenticated request: {user['email']} → {request.url.path}")

        # Continue to route handler
        response = await call_next(request)

        return response

    def _is_public_route(self, path: str) -> bool:
        """
        Check if the request path is a public route (no auth required).

        Args:
            path: Request URL path

        Returns:
            True if public route, False if authentication required
        """
        for public_route in self.PUBLIC_ROUTES:
            if path.startswith(public_route):
                return True
        return False

    def _redirect_to_login(self) -> RedirectResponse:
        """
        Redirect to login page.

        Returns:
            RedirectResponse to /login
        """
        return RedirectResponse(url="/login", status_code=303)

    def _redirect_to_login_with_cleared_cookie(self) -> RedirectResponse:
        """
        Redirect to login page and clear session cookie.

        Used when session is invalid/expired to ensure clean state.

        Returns:
            RedirectResponse to /login with cleared cookie
        """
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(
            key=AUTH_CONFIG["cookie_name"],
            httponly=AUTH_CONFIG["cookie_httponly"],
            secure=AUTH_CONFIG["cookie_secure"],
            samesite=AUTH_CONFIG["cookie_samesite"]
        )
        return response
