# ---------------------------------------------------------------------
# app/routes/family_history.py
# ---------------------------------------------------------------------
# Family History API Routes and Pages
# Handles all family-history API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from typing import Optional
import logging

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db.patient import get_patient_demographics
from app.db.patient_family_history import (
    get_family_history_counts,
    get_patient_family_history,
    get_recent_family_history,
)
from app.utils.ccow_client import ccow_client
from app.utils.template_context import get_base_context

# API router for family-history endpoints
router = APIRouter(prefix="/api/patient", tags=["family-history"])

# Page router for full history pages (no prefix for flexibility)
page_router = APIRouter(tags=["family-history-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/{icn}/history")
async def get_patient_family_history_endpoint(
    icn: str,
    days: Optional[int] = Query(None, ge=1, le=3650),
    relationship: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = False,
):
    """Get patient family-history rows with optional filtering."""
    try:
        rows = get_patient_family_history(
            icn,
            days=days,
            relationship=relationship,
            category=category,
            active_only=active_only,
        )
        counts = get_family_history_counts(icn)

        return {
            "patient_icn": icn,
            "count": len(rows),
            "filters": {
                "days": days,
                "relationship": relationship,
                "category": category,
                "active_only": active_only,
            },
            "counts": counts,
            "history": rows,
        }
    except Exception as exc:
        logger.error("Error fetching family history for %s: %s", icn, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{icn}/history/recent")
async def get_recent_family_history_endpoint(
    icn: str,
    limit: int = Query(5, ge=1, le=50),
):
    """Get recent family-history rows for widget usage."""
    try:
        recent = get_recent_family_history(icn, limit=limit)
        counts = get_family_history_counts(icn)

        return {
            "patient_icn": icn,
            "history": recent,
            "counts": counts,
        }
    except Exception as exc:
        logger.error("Error fetching recent family history for %s: %s", icn, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/dashboard/widget/history/{icn}", response_class=HTMLResponse)
async def get_family_history_widget(request: Request, icn: str):
    """Render Family History widget HTML for the dashboard."""
    try:
        recent = get_recent_family_history(icn, limit=5)
        counts = get_family_history_counts(icn)

        return templates.TemplateResponse(
            "partials/family_history_widget.html",
            {
                "request": request,
                "icn": icn,
                "history": recent,
                "counts": counts,
            },
        )
    except Exception as exc:
        logger.error("Error rendering family-history widget for %s: %s", icn, exc)
        return templates.TemplateResponse(
            "partials/family_history_widget.html",
            {
                "request": request,
                "icn": icn,
                "history": [],
                "counts": {
                    "total": 0,
                    "active": 0,
                    "first_degree": 0,
                    "first_degree_high_risk": 0,
                    "distinct_conditions": 0,
                    "recent_2y": 0,
                    "last_recorded_datetime": None,
                },
                "error": "Failed to load family history",
            },
        )


@page_router.get("/history")
async def history_redirect(request: Request):
    """Redirect to current patient's history page using CCOW context."""
    patient_icn = ccow_client.get_active_patient(request)

    if not patient_icn:
        logger.warning("No active patient in CCOW for history page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/history", status_code=303)


@page_router.get("/patient/{icn}/history", response_class=HTMLResponse)
async def patient_family_history_page(
    request: Request,
    icn: str,
    days: Optional[int] = Query(None, ge=1, le=3650),
    relationship: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = False,
):
    """Render full Family History detail page."""
    try:
        patient = get_patient_demographics(icn)

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        history = get_patient_family_history(
            icn,
            days=days,
            relationship=relationship,
            category=category,
            active_only=active_only,
        )
        counts = get_family_history_counts(icn)

        relationships = sorted(
            {
                row.get("relationship_name")
                for row in history
                if row.get("relationship_name")
            }
        )
        categories = sorted(
            {
                (row.get("condition_category") or row.get("risk_condition_group"))
                for row in history
                if (row.get("condition_category") or row.get("risk_condition_group"))
            }
        )

        context = get_base_context(request)
        context.update(
            {
                "patient": patient,
                "history": history,
                "counts": counts,
                "relationship_options": relationships,
                "category_options": categories,
                "current_filters": {
                    "days": days,
                    "relationship": relationship,
                    "category": category,
                    "active_only": active_only,
                },
                "active_page": "history",
            }
        )

        return templates.TemplateResponse("patient_family_history.html", context)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error rendering family-history page for %s: %s", icn, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@page_router.get("/patient/{icn}/history/filtered", response_class=HTMLResponse)
async def family_history_filtered(
    request: Request,
    icn: str,
    days: Optional[int] = Query(None, ge=1, le=3650),
    relationship: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = False,
):
    """Return filtered Family History rows for HTMX table refresh."""
    try:
        history = get_patient_family_history(
            icn,
            days=days,
            relationship=relationship,
            category=category,
            active_only=active_only,
        )

        return templates.TemplateResponse(
            "partials/family_history_table_rows.html",
            {
                "request": request,
                "history": history,
            },
        )

    except Exception as exc:
        logger.error("Error filtering family history for %s: %s", icn, exc)
        return templates.TemplateResponse(
            "partials/family_history_table_rows.html",
            {
                "request": request,
                "history": [],
                "error": "Failed to filter family history",
            },
        )
