# -----------------------------------------------------------
# main.py
# -----------------------------------------------------------
# med-z1 / app UI and Dashboard
#
# Dependencies:
# pip install fastapi "uvicorn[standard]" jinja2 python-multipart python-dotenv
#
# How to Run using Uvicorn:
# cd to med-z1 root directory
# uvicorn app.main:app --reload
# Access in browser: http://127.0.0.1:8000/
#
# To stop server:
#   CTRL + C
# -----------------------------------------------------------

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

# Explicit imports from root-level config.py
from config import (
    PROJECT_ROOT,
    CDWWORK_DB_CONFIG,
    MINIO_CONFIG,
    USE_MINIO,
    SESSION_SECRET_KEY,
    SESSION_COOKIE_MAX_AGE,
)

# Import routers
from app.routes import patient, dashboard, vitals, medications, demographics, encounters, labs, auth, insight, notes, immunizations

# Import middleware
from app.middleware.auth import AuthMiddleware

app = FastAPI(title="med-z1")

# Add session middleware for Vista data caching
# Session middleware must be added BEFORE auth middleware (executed AFTER in request flow)
# This enables Vista cache storage in user sessions across page navigation
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    max_age=SESSION_COOKIE_MAX_AGE,  # Session expires after timeout (15 min default)
    https_only=False,                # Set to True in production with HTTPS
    same_site="lax",                 # CSRF protection
    path="/"                         # Ensure cookie is sent with all requests
    # Note: Cookie name is always "session" (hardcoded in Starlette)
)

# Add authentication middleware
# IMPORTANT: Middleware is applied in reverse order - last added is executed first
# AuthMiddleware must be added BEFORE routes are accessed
app.add_middleware(AuthMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth.router)               # Authentication routes (login/logout)
app.include_router(dashboard.router)          # Dashboard handles / and /dashboard
app.include_router(patient.router)
app.include_router(patient.page_router)       # Patient pages (Allergies full page)
app.include_router(vitals.router)
app.include_router(vitals.page_router)        # Vitals full page routes
app.include_router(medications.router)
app.include_router(medications.page_router)   # Medications full page routes
app.include_router(demographics.page_router)  # Demographics full page routes
app.include_router(encounters.router)         # Encounters API routes
app.include_router(encounters.page_router)    # Encounters full page routes
app.include_router(labs.router)               # Labs API routes
app.include_router(labs.page_router)          # Labs full page routes
app.include_router(notes.router)              # Clinical Notes API routes
app.include_router(notes.page_router)         # Clinical Notes full page routes
app.include_router(immunizations.router)      # Immunizations API routes
app.include_router(immunizations.page_router) # Immunizations full page routes
app.include_router(insight.page_router)       # AI Insights full page routes

# Configure logging for the entire application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Base directory for this file
BASE_DIR = Path(__file__).resolve().parent

logger.info("med-z1 application starting up")

# Templates and static dirs, using BASE_DIR
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/time", response_class=HTMLResponse)
async def get_time(request: Request):
    """Return a small HTML snippet with the current time."""
    now = datetime.now().strftime("%H:%M:%S")

    # We return a partial template that ONLY contains the snippet HTMX will swap in.
    return templates.TemplateResponse(
        "partials/time.html",
        {
            "request": request,
            "now": now,
        },
    )


@app.get("/htmx", response_class=HTMLResponse)
async def htmx_page(request: Request):
    """Render the main HTMX page."""
    return templates.TemplateResponse(
        "htmx.html",
        {
            "request": request,
            "active_page": "htmx",
        },
    )


@app.get("/timer", response_class=HTMLResponse)
async def timer_page(request: Request):
    """Render the main Timer page."""
    return templates.TemplateResponse(
        "timer.html",
        {
            "request": request,
            "active_page": "timer",
        },
    )


@app.get("/patient-test", response_class=HTMLResponse)
async def patient_test_page(request: Request):
    """Render the patient header test page (temporary dev tool)."""
    return templates.TemplateResponse(
        "patient_test.html",
        {
            "request": request,
        },
    )


@app.get("/test-session")
async def test_session(request: Request):
    """Test endpoint to verify SessionMiddleware is working."""
    # Try to write to session
    if "test_count" not in request.session:
        request.session["test_count"] = 0

    request.session["test_count"] += 1

    # Get all cookies that came with the request
    incoming_cookies = dict(request.cookies)

    # Check what's in the session
    session_contents = dict(request.session)

    return {
        "session_works": True,
        "test_count": request.session["test_count"],
        "session_data": session_contents,
        "incoming_cookies": incoming_cookies,
        "incoming_cookie_names": list(incoming_cookies.keys()),
        "session_cookie_name_expected": "session",  # Starlette default
        "session_cookie_present": "session" in incoming_cookies,
        "session_id_cookie_present": "session_id" in incoming_cookies,
        "note": "SessionMiddleware stores data IN the cookie itself (signed), not in a database"
    }


@app.post("/timer/start", response_class=HTMLResponse)
async def start_timer(request: Request):
    """
    Triggered when 'Start' is clicked.
    Returns the 'Running' partial.
    """
    now = datetime.now()

    return templates.TemplateResponse(
        "partials/timer_running.html",
        {
            "request": request,
            # Formatted for display (e.g., "02:30:45 PM")
            "start_time_display": now.strftime("%I:%M:%S %p"),
            # ISO format for the hidden input value (machine readable)
            "start_timestamp": now.isoformat(),
        },
    )


@app.post("/timer/stop", response_class=HTMLResponse)
async def stop_timer(request: Request, start_timestamp: str = Form(...)):
    """
    Triggered when 'Stop' is clicked.
    Calculates duration and returns the 'Stopped' partial.
    """
    stop_dt = datetime.now()
    start_dt = datetime.fromisoformat(start_timestamp)

    # Calculate duration
    delta = stop_dt - start_dt

    # Format duration (removing microseconds for cleaner display)
    # str(delta) usually looks like "0:00:05.123456"
    duration_str = str(delta).split(".")[0]

    return templates.TemplateResponse(
        "partials/timer_stopped.html",
        {
            "request": request,
            "start_time_display": start_dt.strftime("%I:%M:%S %p"),
            "stop_time_display": stop_dt.strftime("%I:%M:%S %p"),
            "duration": duration_str,
        },
    )
