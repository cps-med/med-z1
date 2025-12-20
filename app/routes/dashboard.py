# ---------------------------------------------------------------------
# app/routes/dashboard.py
# ---------------------------------------------------------------------
# Dashboard Routes
# Handles main dashboard page and widget endpoints.
# Provides patient-centric summary view across all clinical domains.
# ---------------------------------------------------------------------

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.utils.ccow_client import ccow_client
from app.utils.template_context import get_base_context
from app.db.patient import get_patient_demographics
from app.db.patient_flags import get_patient_flags

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """
    Main dashboard page - displays patient summary widgets.

    Shows empty state if no patient selected, otherwise displays
    clinical domain widgets for the active patient.
    """
    try:
        # Get current patient from CCOW (v2.0: pass request for session cookie)
        patient_id = ccow_client.get_active_patient(request)

        patient = None
        if patient_id:
            # Fetch patient demographics for context
            patient = get_patient_demographics(patient_id)
            if patient:
                logger.info(f"Dashboard loaded for patient: {patient_id}")
            else:
                logger.warning(f"Patient {patient_id} in CCOW but not found in database")
        else:
            logger.debug("Dashboard loaded with no patient selected (empty state)")

        return templates.TemplateResponse(
            "dashboard.html",
            get_base_context(
                request,
                patient=patient,
                active_page="dashboard"
            )
        )

    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return templates.TemplateResponse(
            "dashboard.html",
            get_base_context(
                request,
                patient=None,
                error=str(e),
                active_page="dashboard"
            )
        )


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_alternate(request: Request):
    """
    Alternate route for dashboard (supports both / and /dashboard).
    """
    return await get_dashboard(request)


# ============================================
# Widget Endpoints
# ============================================

@router.get("/api/dashboard/widget/demographics/{patient_icn}", response_class=HTMLResponse)
async def get_demographics_widget(request: Request, patient_icn: str):
    """
    Demographics widget endpoint.

    Returns patient demographics in widget format for dashboard display.
    """
    try:
        patient = get_patient_demographics(patient_icn)

        if not patient:
            return templates.TemplateResponse(
                "partials/widget_base.html",
                {
                    "request": request,
                    "size": "2x1",
                    "icon": "fa-solid fa-user",
                    "title": "Demographics",
                    "error": "Patient not found"
                }
            )

        return templates.TemplateResponse(
            "partials/demographics_widget.html",
            {
                "request": request,
                "patient": patient
            }
        )

    except Exception as e:
        logger.error(f"Error loading demographics widget for {patient_icn}: {e}")
        return templates.TemplateResponse(
            "partials/widget_base.html",
            {
                "request": request,
                "size": "2x1",
                "icon": "fa-solid fa-user",
                "title": "Demographics",
                "error": f"Error loading demographics: {str(e)}"
            }
        )


@router.get("/api/dashboard/widget/flags/{patient_icn}", response_class=HTMLResponse)
async def get_flags_widget(request: Request, patient_icn: str):
    """
    Patient Flags widget endpoint.

    Returns active patient flags in widget format for dashboard display.
    """
    try:
        flags = get_patient_flags(patient_icn)

        # Filter to active flags only
        active_flags = [f for f in flags if f.get("is_active", False)]

        # Categorize by type
        national_flags = [f for f in active_flags if f.get("flag_category") == "I"]
        local_flags = [f for f in active_flags if f.get("flag_category") == "II"]

        # Count overdue flags
        overdue_count = sum(1 for f in active_flags if f.get("review_status") == "OVERDUE")

        return templates.TemplateResponse(
            "partials/flags_widget.html",
            {
                "request": request,
                "active_flags": active_flags,
                "national_flags": national_flags,
                "local_flags": local_flags,
                "total_count": len(active_flags),
                "overdue_count": overdue_count
            }
        )

    except Exception as e:
        logger.error(f"Error loading flags widget for {patient_icn}: {e}")
        return templates.TemplateResponse(
            "partials/widget_base.html",
            {
                "request": request,
                "size": "1x1",
                "icon": "fa-solid fa-flag",
                "title": "Flags",
                "error": f"Error loading flags: {str(e)}"
            }
        )
