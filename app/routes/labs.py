# ---------------------------------------------------------------------
# app/routes/labs.py
# ---------------------------------------------------------------------
# Laboratory Results API Routes and Pages
# Handles all lab results API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.db.labs import (
    get_recent_panels,
    get_trending_tests,
    get_all_lab_results,
    get_test_trend,
    get_lab_counts
)
from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context

# API router for labs endpoints
router = APIRouter(prefix="/api/patient", tags=["labs"])

# Page router for full labs pages (no prefix for flexibility)
page_router = APIRouter(tags=["labs-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


# ============================================
# API Endpoints (JSON responses)
# ============================================

@router.get("/{icn}/labs")
async def get_patient_labs_endpoint(
    icn: str,
    limit: Optional[int] = Query(100, ge=1, le=500),
    offset: Optional[int] = Query(0, ge=0),
    panel_filter: Optional[str] = None,
    abnormal_only: Optional[bool] = False,
    days: Optional[int] = None
):
    """
    Get all lab results for a patient with optional filters.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of results to return (1-500, default 100)
        offset: Number of results to skip for pagination (default 0)
        panel_filter: Filter by panel name (e.g., "BMP", "CBC")
        abnormal_only: If True, return only abnormal results (default False)
        days: If specified, only return results from last N days

    Returns:
        JSON with list of lab results
    """
    try:
        labs = get_all_lab_results(
            icn,
            limit=limit,
            offset=offset,
            panel_filter=panel_filter,
            abnormal_only=abnormal_only,
            days=days
        )

        return {
            "patient_icn": icn,
            "count": len(labs),
            "filters": {
                "panel": panel_filter,
                "abnormal_only": abnormal_only,
                "days": days
            },
            "labs": labs
        }

    except Exception as e:
        logger.error(f"Error fetching labs for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/labs/recent-panels")
async def get_recent_panels_endpoint(
    icn: str,
    limit: Optional[int] = Query(3, ge=1, le=10)
):
    """
    Get the most recent lab panels for a patient.
    Used for dashboard widget to show current panel results.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of panels to return (default 3 for 3x1 widget)

    Returns:
        JSON with panel data including all results per panel
    """
    try:
        panels = get_recent_panels(icn, limit=limit)
        counts = get_lab_counts(icn)

        return {
            "patient_icn": icn,
            "panel_count": len(panels),
            "panels": panels,
            "counts": counts
        }

    except Exception as e:
        logger.error(f"Error fetching recent panels for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/labs/trending")
async def get_trending_tests_endpoint(
    icn: str,
    test_names: Optional[str] = Query(None),
    days: Optional[int] = Query(90, ge=1, le=365)
):
    """
    Get trending data for specific lab tests.
    Used for widget sparklines and trending graphs.

    Args:
        icn: Integrated Care Number
        test_names: Comma-separated list of test names (e.g., "Glucose,Creatinine")
        days: Number of days to look back (default 90)

    Returns:
        JSON with trending data keyed by test name
    """
    try:
        # Parse test_names from comma-separated string
        test_list = None
        if test_names:
            test_list = [name.strip() for name in test_names.split(",")]

        trending = get_trending_tests(icn, test_names=test_list, days=days)

        return {
            "patient_icn": icn,
            "test_count": len(trending),
            "days": days,
            "trending": trending
        }

    except Exception as e:
        logger.error(f"Error fetching trending tests for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/labs/trend/{test_name}")
async def get_test_trend_endpoint(
    icn: str,
    test_name: str,
    days: Optional[int] = Query(365, ge=1, le=730)
):
    """
    Get historical trend data for a specific lab test.
    Used for graphing a single test over time on the full page view.

    Args:
        icn: Integrated Care Number
        test_name: Name of the lab test (e.g., "Glucose", "Creatinine")
        days: Number of days to look back (default 365)

    Returns:
        JSON with test trend data sorted by date
    """
    try:
        trend = get_test_trend(icn, test_name, days=days)

        return {
            "patient_icn": icn,
            "test_name": test_name,
            "days": days,
            "count": len(trend),
            "trend": trend
        }

    except Exception as e:
        logger.error(f"Error fetching test trend for {icn}, test {test_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Widget Endpoint (HTML partial)
# ============================================

@router.get("/dashboard/widget/labs/{icn}", response_class=HTMLResponse)
async def get_labs_widget(request: Request, icn: str):
    """
    Render labs widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing recent lab panels (3x1 widget).

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for labs widget
    """
    try:
        # Get recent panels (3 for 3x1 widget layout)
        panels = get_recent_panels(icn, limit=3)

        # Get trending data for sparklines (key tests)
        trending_tests = ["Glucose", "Creatinine", "Hemoglobin"]
        trending = get_trending_tests(icn, test_names=trending_tests, days=90)

        return templates.TemplateResponse(
            "partials/labs_widget.html",
            {
                "request": request,
                "icn": icn,
                "panels": panels,
                "trending": trending,
                "has_labs": len(panels) > 0
            }
        )

    except Exception as e:
        logger.error(f"Error rendering labs widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/labs_widget.html",
            {
                "request": request,
                "icn": icn,
                "panels": [],
                "trending": {},
                "has_labs": False,
                "error": str(e)
            }
        )


# ============================================
# Full Page Routes
# ============================================

@page_router.get("/labs")
async def labs_redirect():
    """
    Redirect to current patient's labs page.
    Gets patient from CCOW and redirects to /patient/{icn}/labs.
    If no patient selected, redirects to dashboard.
    """
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient()

    if not patient_icn:
        logger.warning("No active patient in CCOW for labs page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/labs", status_code=303)


@page_router.get("/patient/{icn}/labs", response_class=HTMLResponse)
async def get_labs_page(
    request: Request,
    icn: str,
    panel_filter: Optional[str] = None,
    abnormal_only: Optional[bool] = False,
    days: Optional[int] = None,
    sort_by: Optional[str] = Query("collection_datetime", regex="^(collection_datetime|lab_test_name|abnormal_flag)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$")
):
    """
    Render full labs page for a patient.
    Shows comprehensive lab results with filtering, sorting, and charting.

    Args:
        icn: Integrated Care Number
        panel_filter: Filter by panel name (e.g., "BMP", "CBC")
        abnormal_only: If True, show only abnormal results
        days: If specified, show only results from last N days
        sort_by: Sort column (default: collection_datetime)
        sort_order: Sort direction (asc/desc, default: desc)

    Returns:
        HTML page for lab results
    """
    try:
        # Get patient demographics
        patient = get_patient_demographics(icn)

        if not patient:
            return templates.TemplateResponse(
                "patient_labs.html",
                get_base_context(
                    request,
                    error=f"Patient not found: {icn}",
                    patient=None
                )
            )

        # Get all lab results with filters and sorting
        labs = get_all_lab_results(
            icn,
            limit=100,
            panel_filter=panel_filter,
            abnormal_only=abnormal_only,
            days=days,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Get panel counts for filter pills
        counts = get_lab_counts(icn)

        # Calculate total count
        total_count = sum(counts.values())

        # Calculate abnormal count from current results
        abnormal_count = sum(1 for lab in labs if lab.get('is_abnormal', False))

        return templates.TemplateResponse(
            "patient_labs.html",
            get_base_context(
                request,
                patient=patient,
                labs=labs,
                counts=counts,
                total_count=total_count,
                abnormal_count=abnormal_count,
                panel_filter=panel_filter,
                abnormal_only=abnormal_only,
                days=days,
                sort_by=sort_by,
                sort_order=sort_order,
                active_page="labs"
            )
        )

    except Exception as e:
        logger.error(f"Error rendering labs page for {icn}: {e}")
        return templates.TemplateResponse(
            "patient_labs.html",
            get_base_context(
                request,
                error=str(e),
                patient=None
            )
        )
