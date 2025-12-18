# ---------------------------------------------------------------------
# app/routes/auth.py
# ---------------------------------------------------------------------
# Authentication Routes
# Handles user login, logout, and session management.
# Implements Microsoft Entra ID-style authentication flow.
# ---------------------------------------------------------------------

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging

from app.db import auth as auth_db
from config import AUTH_CONFIG

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    """
    Display login page.

    If user already has valid session, redirect to dashboard.
    Otherwise, show login form (simulated Entra ID style).
    """
    try:
        # Check if user already has valid session
        session_id = request.cookies.get(AUTH_CONFIG["cookie_name"])

        if session_id:
            session = auth_db.get_session(session_id)
            if session and session['is_active']:
                # Already logged in, redirect to dashboard
                logger.info(f"User already logged in (session {session_id}), redirecting to dashboard")
                return RedirectResponse(url="/", status_code=303)

        # Show login page
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": None
            }
        )

    except Exception as e:
        logger.error(f"Error loading login page: {e}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "An error occurred. Please try again."
            }
        )


@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Process login form submission.

    Validates credentials, creates session, sets cookie, redirects to dashboard.
    Logs all authentication events to audit table.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        # 1. Get user by email
        user = auth_db.get_user_by_email(email)

        if not user:
            logger.warning(f"Login attempt for non-existent user: {email}")
            auth_db.log_audit_event(
                event_type='login_failed',
                email=email,
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                failure_reason='User not found'
            )
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Invalid email or password"
                },
                status_code=401
            )

        # 2. Verify password
        if not auth_db.verify_password(password, user['password_hash']):
            logger.warning(f"Invalid password for user: {email}")
            auth_db.log_audit_event(
                event_type='login_failed',
                user_id=user['user_id'],
                email=email,
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                failure_reason='Invalid password'
            )
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Invalid email or password"
                },
                status_code=401
            )

        # 3. Check if account is active
        if not user['is_active']:
            logger.warning(f"Login attempt for inactive account: {email}")
            auth_db.log_audit_event(
                event_type='login_failed',
                user_id=user['user_id'],
                email=email,
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                failure_reason='Account inactive'
            )
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Account is inactive. Please contact administrator."
                },
                status_code=403
            )

        # 4. Check if account is locked
        if user['is_locked']:
            logger.warning(f"Login attempt for locked account: {email}")
            auth_db.log_audit_event(
                event_type='login_failed',
                user_id=user['user_id'],
                email=email,
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                failure_reason='Account locked'
            )
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Account is locked. Please contact administrator."
                },
                status_code=403
            )

        # 5. Invalidate old sessions (single-session enforcement)
        auth_db.invalidate_user_sessions(user['user_id'])
        logger.info(f"Invalidated previous sessions for user: {email}")

        # 6. Create new session
        session_id = auth_db.create_session(
            user_id=user['user_id'],
            ip_address=client_ip,
            user_agent=user_agent
        )

        if not session_id:
            logger.error(f"Failed to create session for user: {email}")
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Failed to create session. Please try again."
                },
                status_code=500
            )

        # 7. Update last login timestamp
        auth_db.update_last_login(user['user_id'])

        # 8. Log successful login
        auth_db.log_audit_event(
            event_type='login',
            user_id=user['user_id'],
            email=email,
            ip_address=client_ip,
            user_agent=user_agent,
            success=True,
            session_id=session_id
        )

        logger.info(f"Successful login for user: {email} (session: {session_id})")

        # 9. Set session cookie and redirect to dashboard
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key=AUTH_CONFIG["cookie_name"],
            value=session_id,
            httponly=AUTH_CONFIG["cookie_httponly"],
            secure=AUTH_CONFIG["cookie_secure"],
            samesite=AUTH_CONFIG["cookie_samesite"],
            max_age=AUTH_CONFIG["cookie_max_age"]
        )

        return response

    except Exception as e:
        logger.error(f"Error during login for {email}: {e}")
        auth_db.log_audit_event(
            event_type='login_failed',
            email=email,
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            failure_reason=f'System error: {str(e)}'
        )
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "An error occurred during login. Please try again."
            },
            status_code=500
        )


@router.post("/logout")
async def post_logout(request: Request):
    """
    Process logout request.

    Invalidates session, clears cookie, redirects to login page.
    Logs logout event to audit table.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        # Get session ID from cookie
        session_id = request.cookies.get(AUTH_CONFIG["cookie_name"])

        if session_id:
            # Get session to log user info
            session = auth_db.get_session(session_id)

            if session:
                # Get user for audit log
                user = auth_db.get_user_by_id(session['user_id'])

                # Invalidate session
                auth_db.invalidate_session(session_id)

                # Log logout event
                auth_db.log_audit_event(
                    event_type='logout',
                    user_id=session['user_id'],
                    email=user['email'] if user else None,
                    ip_address=client_ip,
                    user_agent=user_agent,
                    success=True,
                    session_id=session_id
                )

                logger.info(f"User logged out: {user['email'] if user else 'unknown'} (session: {session_id})")

        # Clear session cookie and redirect to login
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(
            key=AUTH_CONFIG["cookie_name"],
            httponly=AUTH_CONFIG["cookie_httponly"],
            secure=AUTH_CONFIG["cookie_secure"],
            samesite=AUTH_CONFIG["cookie_samesite"]
        )

        return response

    except Exception as e:
        logger.error(f"Error during logout: {e}")

        # Still clear cookie and redirect even on error
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(
            key=AUTH_CONFIG["cookie_name"],
            httponly=AUTH_CONFIG["cookie_httponly"],
            secure=AUTH_CONFIG["cookie_secure"],
            samesite=AUTH_CONFIG["cookie_samesite"]
        )

        return response


@router.get("/logout")
async def get_logout(request: Request):
    """
    GET /logout - redirect to POST /logout for proper logout flow.

    This handles cases where users bookmark or directly access /logout URL.
    """
    # Simply redirect to login page (session will be invalidated by middleware)
    return RedirectResponse(url="/login", status_code=303)
