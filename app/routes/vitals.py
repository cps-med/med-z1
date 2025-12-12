# ---------------------------------------------------------------------
# app/routes/vitals.py
# ---------------------------------------------------------------------
# Vitals API Routes and Pages
# Handles all vital signs API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.db.vitals import (
    get_patient_vitals,
    get_recent_vitals,
    get_vital_type_history,
    get_vital_counts
)
from app.db.patient import get_patient_demographics

# API router for vitals endpoints
router = APIRouter(prefix="/api/patient", tags=["vitals"])

# Page router for full vitals pages (no prefix for flexibility)
page_router = APIRouter(tags=["vitals-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/{icn}/vitals")
async def get_patient_vitals_endpoint(
    icn: str,
    limit: Optional[int] = Query(100, ge=1, le=500),
    vital_type: Optional[str] = None
):
    """
    Get all vitals for a patient.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of vitals to return (1-500, default 100)
        vital_type: Optional filter by vital type (e.g., "BLOOD PRESSURE")

    Returns:
        JSON with list of vital signs
    """
    try:
        vitals = get_patient_vitals(icn, limit=limit, vital_type=vital_type)

        return {
            "patient_icn": icn,
            "count": len(vitals),
            "vitals": vitals
        }

    except Exception as e:
        logger.error(f"Error fetching vitals for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/vitals/recent")
async def get_recent_vitals_endpoint(icn: str):
    """
    Get the most recent vital sign measurement per vital type.
    Used for dashboard widget to show current status.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with vital_abbr as keys and vital data as values
    """
    try:
        recent = get_recent_vitals(icn)
        counts = get_vital_counts(icn)

        return {
            "patient_icn": icn,
            "vitals": recent,
            "counts": counts
        }

    except Exception as e:
        logger.error(f"Error fetching recent vitals for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/vitals/{vital_type}/history")
async def get_vital_history_endpoint(
    icn: str,
    vital_type: str,
    limit: Optional[int] = Query(50, ge=1, le=200)
):
    """
    Get historical timeline for a specific vital type.
    Used for trending and graphing.

    Args:
        icn: Integrated Care Number
        vital_type: Vital type (e.g., "BLOOD PRESSURE", "TEMPERATURE")
        limit: Maximum number of measurements (1-200, default 50)

    Returns:
        JSON with historical vital measurements sorted by date (oldest first)
    """
    try:
        history = get_vital_type_history(icn, vital_type, limit=limit)

        return {
            "patient_icn": icn,
            "vital_type": vital_type,
            "count": len(history),
            "history": history
        }

    except Exception as e:
        logger.error(f"Error fetching vital history for {icn}, type {vital_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widget/vitals/{icn}", response_class=HTMLResponse)
async def get_vitals_widget(request: Request, icn: str):
    """
    Render vitals widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing recent vital signs.

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for vitals widget
    """
    try:
        # Get recent vitals (one per type)
        recent = get_recent_vitals(icn)

        # Define priority vital types to display in widget (most important first)
        priority_vitals = ["BP", "T", "P", "R", "POX", "PN"]

        # Filter to only priority vitals that exist, maintaining priority order
        widget_vitals = []
        for abbr in priority_vitals:
            if abbr in recent:
                widget_vitals.append(recent[abbr])

        return templates.TemplateResponse(
            "partials/vitals_widget.html",
            {
                "request": request,
                "icn": icn,
                "vitals": widget_vitals,
                "has_vitals": len(widget_vitals) > 0
            }
        )

    except Exception as e:
        logger.error(f"Error rendering vitals widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/vitals_widget.html",
            {
                "request": request,
                "icn": icn,
                "vitals": [],
                "has_vitals": False,
                "error": str(e)
            }
        )


# ============================================
# Full Page Routes
# ============================================

@page_router.get("/vitals")
async def vitals_redirect():
    """
    Redirect to current patient's vitals page.
    Gets patient from CCOW and redirects to /patient/{icn}/vitals.
    If no patient selected, redirects to dashboard.
    """
    from fastapi.responses import RedirectResponse
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient()

    if not patient_icn:
        logger.warning("No active patient in CCOW for vitals page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/vitals", status_code=303)


@page_router.get("/patient/{icn}/vitals", response_class=HTMLResponse)
async def get_vitals_page(
    request: Request,
    icn: str,
    vital_type: Optional[str] = None,
    sort_by: Optional[str] = Query("taken_datetime", regex="^(taken_datetime|vital_type|abnormal_flag)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$")
):
    """
    Full vitals page for a patient.

    Shows comprehensive table/grid of all vitals with filtering and sorting.

    Args:
        icn: Patient ICN
        vital_type: Optional filter by vital type (e.g., "BLOOD PRESSURE")
        sort_by: Column to sort by (taken_datetime, vital_type, abnormal_flag)
        sort_order: Sort order (asc or desc)

    Returns:
        Full HTML page with vitals table
    """
    try:
        # Get patient demographics for header
        patient = get_patient_demographics(icn)

        if not patient:
            logger.warning(f"Patient {icn} not found")
            return templates.TemplateResponse(
                "patient_vitals.html",
                {
                    "request": request,
                    "patient": None,
                    "error": "Patient not found"
                }
            )

        # Get all vitals for patient (limit 500 for page view)
        vitals = get_patient_vitals(icn, limit=500, vital_type=vital_type)

        # Get vital counts for filter pills
        counts = get_vital_counts(icn)

        # Sort vitals
        reverse = (sort_order == "desc")

        if sort_by == "taken_datetime":
            vitals = sorted(vitals, key=lambda v: v.get("taken_datetime") or "", reverse=reverse)
        elif sort_by == "vital_type":
            vitals = sorted(vitals, key=lambda v: v.get("vital_type") or "", reverse=reverse)
        elif sort_by == "abnormal_flag":
            # Custom sort: CRITICAL > HIGH > LOW > NORMAL > None
            flag_order = {"CRITICAL": 4, "HIGH": 3, "LOW": 2, "NORMAL": 1, None: 0}
            vitals = sorted(vitals, key=lambda v: flag_order.get(v.get("abnormal_flag"), 0), reverse=reverse)

        logger.info(f"Loaded vitals page for {icn}: {len(vitals)} vitals, filter={vital_type}, sort={sort_by} {sort_order}")

        return templates.TemplateResponse(
            "patient_vitals.html",
            {
                "request": request,
                "patient": patient,
                "vitals": vitals,
                "counts": counts,
                "vital_type_filter": vital_type,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "total_count": len(vitals),
                "active_page": "vitals"
            }
        )

    except Exception as e:
        logger.error(f"Error loading vitals page for {icn}: {e}")
        return templates.TemplateResponse(
            "patient_vitals.html",
            {
                "request": request,
                "patient": None,
                "error": str(e),
                "active_page": "vitals"
            }
        )
