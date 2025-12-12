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

# Explicit imports from root-level config.py
from config import (
    PROJECT_ROOT,
    CDWWORK_DB_CONFIG,
    MINIO_CONFIG,
    USE_MINIO,
)

# Import routers
from app.routes import patient, dashboard, vitals

app = FastAPI(title="med-z1")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(dashboard.router)  # Dashboard handles / and /dashboard
app.include_router(patient.router)
app.include_router(vitals.router)
app.include_router(vitals.page_router)  # Vitals full page routes

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


# NOTE: Dashboard route (/) now handled by app.routes.dashboard
# Old index route commented out - replaced with patient-centric dashboard

# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     """Render the main dashboard page."""
#     # In a real app, pull these from a database or ETL process
#     summary = {
#         "total_records": 15423,
#         "jobs_running": 3,
#         "last_run": "Today 07:32",
#         "alerts": 2,
#         # Example: surface a few config values for sanity/debug
#         "cdwwork_db_server": CDWWORK_DB_CONFIG["server"],
#         "use_minio": USE_MINIO,
#         "minio_bucket": MINIO_CONFIG["bucket_name"],
#         "cps_comment": "This is only a test..."
#     }
#
#     recent_activity = [
#         "Job #42 completed successfully.",
#         "New dataset 'dd_interactions_2025.parquet' loaded.",
#         "Alert resolved: Missing values in lab_results.",
#         "User 'csylvester' updated ETL configuration.",
#     ]
#
#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "summary": summary,
#             "recent_activity": recent_activity,
#             "active_page": "overview",
#         },
#     )


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
