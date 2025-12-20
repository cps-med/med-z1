# ---------------------------------------------------------------------
# app/routes/medications.py
# ---------------------------------------------------------------------
# Medications API Routes and Pages
# Handles all medications API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# Integrates both outpatient (RxOut) and inpatient (BCMA) medications.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.db.medications import (
    get_patient_medications,
    get_recent_medications,
    get_medication_counts
)
from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context

# API router for medications endpoints
router = APIRouter(prefix="/api/patient", tags=["medications"])

# Page router for full medications pages (no prefix for flexibility)
page_router = APIRouter(tags=["medications-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/{icn}/medications")
async def get_patient_medications_endpoint(
    icn: str,
    limit: Optional[int] = Query(100, ge=1, le=500),
    medication_type: Optional[str] = Query(None, regex="^(outpatient|inpatient)$"),
    status: Optional[str] = None,
    days: Optional[int] = Query(None, ge=1, le=3650)
):
    """
    Get all medications for a patient (both outpatient and inpatient).

    Args:
        icn: Integrated Care Number
        limit: Maximum number of medications to return (1-500, default 100)
        medication_type: Optional filter by type ('outpatient', 'inpatient', or None for both)
        status: Optional filter by status (for outpatient: 'ACTIVE', 'DISCONTINUED', etc.)
        days: Optional filter to last N days (1-3650, default: all)

    Returns:
        JSON with list of medications from both sources
    """
    try:
        medications = get_patient_medications(
            icn,
            limit=limit,
            medication_type=medication_type,
            status=status,
            days=days
        )

        # Get counts for metadata
        counts = get_medication_counts(icn)

        return {
            "patient_icn": icn,
            "count": len(medications),
            "filters": {
                "medication_type": medication_type,
                "status": status,
                "days": days
            },
            "counts": counts,
            "medications": medications
        }

    except Exception as e:
        logger.error(f"Error fetching medications for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/medications/recent")
async def get_recent_medications_endpoint(icn: str):
    """
    Get recent medications for dashboard widget.
    Returns both outpatient and inpatient medications separately (last 90 days).
    Used for 2x1 widget with two-column layout.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with separate lists for outpatient and inpatient medications
    """
    try:
        recent = get_recent_medications(icn, limit=8)
        counts = get_medication_counts(icn)

        return {
            "patient_icn": icn,
            "outpatient": recent["outpatient"],
            "inpatient": recent["inpatient"],
            "counts": counts
        }

    except Exception as e:
        logger.error(f"Error fetching recent medications for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/medications/{medication_id}/details")
async def get_medication_details_endpoint(icn: str, medication_id: str):
    """
    Get full details for a specific medication.
    medication_id format: "rxout_{id}" or "bcma_{id}"

    Args:
        icn: Integrated Care Number
        medication_id: Medication identifier (e.g., "rxout_123" or "bcma_456")

    Returns:
        JSON with full medication details
    """
    try:
        # Parse medication_id to determine type and ID
        if medication_id.startswith("rxout_"):
            med_type = "outpatient"
            # For now, get all outpatient meds and filter
            # In production, would optimize with direct query
            all_meds = get_patient_medications(icn, medication_type="outpatient", limit=500)
        elif medication_id.startswith("bcma_"):
            med_type = "inpatient"
            all_meds = get_patient_medications(icn, medication_type="inpatient", limit=500)
        else:
            raise HTTPException(status_code=400, detail="Invalid medication_id format")

        # Find the specific medication
        medication = next((m for m in all_meds if m["medication_id"] == medication_id), None)

        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")

        return {
            "patient_icn": icn,
            "medication": medication
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching medication details for {icn}, med_id {medication_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widget/medications/{icn}", response_class=HTMLResponse)
async def get_medications_widget(request: Request, icn: str):
    """
    Render medications widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing recent medications in 2x1 two-column layout.
    Left column: Outpatient medications
    Right column: Inpatient medications

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for medications widget (2x1 wide format)
    """
    try:
        # Get recent medications (split between outpatient and inpatient)
        recent = get_recent_medications(icn, limit=8)
        counts = get_medication_counts(icn)

        return templates.TemplateResponse(
            "partials/medications_widget.html",
            {
                "request": request,
                "icn": icn,
                "outpatient": recent["outpatient"],
                "inpatient": recent["inpatient"],
                "counts": counts,
                "has_outpatient": len(recent["outpatient"]) > 0,
                "has_inpatient": len(recent["inpatient"]) > 0
            }
        )

    except Exception as e:
        logger.error(f"Error rendering medications widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/medications_widget.html",
            {
                "request": request,
                "icn": icn,
                "outpatient": [],
                "inpatient": [],
                "counts": {},
                "has_outpatient": False,
                "has_inpatient": False,
                "error": str(e)
            }
        )


# ============================================
# Full Page Routes
# ============================================

@page_router.get("/medications")
async def medications_redirect(request: Request):
    """
    Redirect to current patient's medications page.
    Gets patient from CCOW and redirects to /patient/{icn}/medications.
    If no patient selected, redirects to dashboard.
    """
    from fastapi.responses import RedirectResponse
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient(request)

    if not patient_icn:
        logger.warning("No active patient in CCOW for medications page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/medications", status_code=303)


@page_router.get("/patient/{icn}/medications", response_class=HTMLResponse)
async def get_medications_page(
    request: Request,
    icn: str,
    medication_type: Optional[str] = Query(None, regex="^(outpatient|inpatient|all)$"),
    status: Optional[str] = None,
    days: Optional[int] = Query(90, ge=1, le=3650),
    sort_by: Optional[str] = Query("date", regex="^(date|drug_name|type|status)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$")
):
    """
    Full medications page for a patient.

    Shows comprehensive table/timeline of all medications (outpatient + inpatient)
    with filtering and sorting.

    Args:
        icn: Patient ICN
        medication_type: Filter by type ('outpatient', 'inpatient', 'all', default: 'all')
        status: Filter by status (for outpatient medications)
        days: Show last N days (default: 90)
        sort_by: Column to sort by (date, drug_name, type, status)
        sort_order: Sort order (asc or desc, default: desc)

    Returns:
        Full HTML page with medications timeline table
    """
    try:
        # Get patient demographics for header
        patient = get_patient_demographics(icn)

        if not patient:
            logger.warning(f"Patient {icn} not found")
            return templates.TemplateResponse(
                "patient_medications.html",
                get_base_context(
                    request,
                    patient=None,
                    error="Patient not found"
                )
            )

        # Normalize medication_type filter
        if medication_type == "all":
            medication_type = None

        # Get all medications for patient (limit 500 for page view)
        medications = get_patient_medications(
            icn,
            limit=500,
            medication_type=medication_type,
            status=status,
            days=days
        )

        # Get medication counts for filter pills
        counts = get_medication_counts(icn)

        # Sort medications
        reverse = (sort_order == "desc")

        if sort_by == "date":
            medications = sorted(medications, key=lambda m: m.get("date") or "", reverse=reverse)
        elif sort_by == "drug_name":
            medications = sorted(medications, key=lambda m: m.get("drug_name_local") or "", reverse=reverse)
        elif sort_by == "type":
            medications = sorted(medications, key=lambda m: m.get("type") or "", reverse=reverse)
        elif sort_by == "status":
            # For outpatient: status, for inpatient: action_type
            def get_status(m):
                if m.get("type") == "outpatient":
                    return m.get("status") or ""
                else:
                    return m.get("action_type") or ""
            medications = sorted(medications, key=get_status, reverse=reverse)

        logger.info(f"Loaded medications page for {icn}: {len(medications)} medications, type={medication_type}, days={days}, sort={sort_by} {sort_order}")

        return templates.TemplateResponse(
            "patient_medications.html",
            get_base_context(
                request,
                patient=patient,
                medications=medications,
                counts=counts,
                medication_type_filter=medication_type or "all",
                status_filter=status,
                days_filter=days,
                sort_by=sort_by,
                sort_order=sort_order,
                total_count=len(medications),
                active_page="medications"
            )
        )

    except Exception as e:
        logger.error(f"Error loading medications page for {icn}: {e}")
        return templates.TemplateResponse(
            "patient_medications.html",
            get_base_context(
                request,
                patient=None,
                error=str(e),
                active_page="medications"
            )
        )
