# ---------------------------------------------------------------------
# app/routes/immunizations.py
# ---------------------------------------------------------------------
# Immunizations API Routes and Pages
# Handles all immunizations API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.db.patient_immunizations import (
    get_patient_immunizations,
    get_recent_immunizations,
    get_immunization_counts,
    get_vaccine_reference
)
from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context

# API router for immunizations endpoints
router = APIRouter(prefix="/api/patient", tags=["immunizations"])

# Page router for full immunizations pages (no prefix for flexibility)
page_router = APIRouter(tags=["immunizations-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/{icn}/immunizations")
async def get_patient_immunizations_endpoint(
    icn: str,
    limit: Optional[int] = Query(100, ge=1, le=500),
    vaccine_group: Optional[str] = None,
    cvx_code: Optional[str] = None,
    days: Optional[int] = Query(None, ge=1, le=3650),
    incomplete_only: Optional[bool] = False,
    adverse_reactions_only: Optional[bool] = False
):
    """
    Get all immunizations for a patient.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of immunizations to return (1-500, default 100)
        vaccine_group: Optional filter by vaccine group ('Influenza', 'COVID-19', 'Hepatitis', etc.)
        cvx_code: Optional filter by CVX code
        days: Optional filter to last N days (1-3650, default: all)
        incomplete_only: Filter to incomplete series only (default: False)
        adverse_reactions_only: Filter to records with adverse reactions (default: False)

    Returns:
        JSON with list of immunizations
    """
    try:
        immunizations = get_patient_immunizations(
            icn,
            limit=limit,
            vaccine_group=vaccine_group,
            cvx_code=cvx_code,
            days=days,
            incomplete_only=incomplete_only,
            adverse_reactions_only=adverse_reactions_only
        )

        # Get counts for metadata
        counts = get_immunization_counts(icn)

        return {
            "patient_icn": icn,
            "count": len(immunizations),
            "filters": {
                "vaccine_group": vaccine_group,
                "cvx_code": cvx_code,
                "days": days,
                "incomplete_only": incomplete_only,
                "adverse_reactions_only": adverse_reactions_only
            },
            "counts": counts,
            "immunizations": immunizations
        }

    except Exception as e:
        logger.error(f"Error fetching immunizations for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/immunizations/recent")
async def get_recent_immunizations_endpoint(icn: str):
    """
    Get recent immunizations for dashboard widget (last 2 years).

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with recent immunizations
    """
    try:
        recent = get_recent_immunizations(icn, limit=5)
        counts = get_immunization_counts(icn)

        return {
            "patient_icn": icn,
            "immunizations": recent,
            "counts": counts
        }

    except Exception as e:
        logger.error(f"Error fetching recent immunizations for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widget/immunizations/{icn}", response_class=HTMLResponse)
async def get_immunizations_widget(request: Request, icn: str):
    """
    Get immunizations widget HTML for dashboard (HTMX partial).

    Args:
        request: FastAPI request object
        icn: Integrated Care Number

    Returns:
        HTML partial for 1x1 widget
    """
    try:
        recent = get_recent_immunizations(icn, limit=5)
        counts = get_immunization_counts(icn)

        return templates.TemplateResponse(
            "partials/immunizations_widget.html",
            {
                "request": request,
                "icn": icn,
                "immunizations": recent,
                "counts": counts
            }
        )

    except Exception as e:
        logger.error(f"Error rendering immunizations widget for {icn}: {e}")
        return templates.TemplateResponse(
            "partials/immunizations_widget.html",
            {
                "request": request,
                "icn": icn,
                "immunizations": [],
                "counts": {"total": 0, "annual": 0, "covid": 0, "incomplete": 0, "with_reactions": 0, "recent_2y": 0},
                "error": "Failed to load immunizations"
            }
        )


@page_router.get("/immunizations")
async def immunizations_redirect(request: Request):
    """
    Redirect to current patient's immunizations page.
    Gets patient from CCOW and redirects to /patient/{icn}/immunizations.
    If no patient selected, redirects to dashboard.
    """
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient(request)

    if not patient_icn:
        logger.warning("No active patient in CCOW for immunizations page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/immunizations", status_code=303)


@page_router.get("/patient/{icn}/immunizations", response_class=HTMLResponse)
async def immunizations_page(request: Request, icn: str):
    """
    Full immunizations page with filtering and complete history.

    Args:
        request: FastAPI request object
        icn: Integrated Care Number

    Returns:
        Full HTML page
    """
    try:
        # Get patient demographics for context
        patient = get_patient_demographics(icn)

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Get all immunizations (no filters initially)
        immunizations = get_patient_immunizations(icn, limit=500)
        counts = get_immunization_counts(icn)

        # Get vaccine reference data for filters
        vaccines = get_vaccine_reference()

        # Extract unique vaccine groups for filter dropdown
        vaccine_groups = sorted(set([v["vaccine_group"] for v in vaccines if v["vaccine_group"]]))

        context = get_base_context(request)
        context.update({
            "patient": patient,
            "immunizations": immunizations,
            "counts": counts,
            "vaccine_groups": vaccine_groups,
            "current_filters": {},
            "active_page": "immunizations"
        })

        return templates.TemplateResponse(
            "patient_immunizations.html",
            context
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering immunizations page for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@page_router.get("/patient/{icn}/immunizations/filtered", response_class=HTMLResponse)
async def immunizations_filtered(
    request: Request,
    icn: str,
    vaccine_group: Optional[str] = None,
    days: Optional[int] = None,
    incomplete_only: Optional[bool] = False,
    adverse_reactions_only: Optional[bool] = False
):
    """
    Filtered immunizations results (HTMX partial for table body).

    Args:
        request: FastAPI request object
        icn: Integrated Care Number
        vaccine_group: Optional vaccine group filter
        days: Optional days filter
        incomplete_only: Filter to incomplete series
        adverse_reactions_only: Filter to adverse reactions

    Returns:
        HTML partial (table rows)
    """
    try:
        immunizations = get_patient_immunizations(
            icn,
            limit=500,
            vaccine_group=vaccine_group,
            days=days,
            incomplete_only=incomplete_only,
            adverse_reactions_only=adverse_reactions_only
        )

        return templates.TemplateResponse(
            "partials/immunizations_table_rows.html",
            {
                "request": request,
                "immunizations": immunizations
            }
        )

    except Exception as e:
        logger.error(f"Error filtering immunizations for {icn}: {e}")
        return templates.TemplateResponse(
            "partials/immunizations_table_rows.html",
            {
                "request": request,
                "immunizations": [],
                "error": "Failed to filter immunizations"
            }
        )
