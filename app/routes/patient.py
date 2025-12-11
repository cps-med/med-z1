# ---------------------------------------------------------------------
# app/routes/patient.py
# ---------------------------------------------------------------------
# Patient API Routes
# Handles all patient-related API endpoints for the topbar UI.
# Returns HTML partials for HTMX swapping and JSON for API consumers.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.utils.ccow_client import ccow_client
from app.db.patient import get_patient_demographics, search_patients
from app.db.patient_flags import (
    get_patient_flags,
    get_flag_count,
    get_flag_history,
    get_active_flags_count
)

router = APIRouter(prefix="/api/patient", tags=["patient"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/current", response_class=HTMLResponse)
async def get_current_patient(request: Request):
    """
    Get current patient from CCOW vault and return demographics partial.
    Called on initial page load via HTMX (hx-trigger="load").
    """
    try:
        # Query CCOW vault
        patient_id = ccow_client.get_active_patient()

        if not patient_id:
            # No active patient in vault
            return templates.TemplateResponse(
                "partials/patient_header.html",
                {"request": request, "patient": None}
            )

        # Fetch patient demographics from PostgreSQL
        patient = get_patient_demographics(patient_id)

        if not patient:
            logger.warning(f"Patient {patient_id} from CCOW not found in database")
            return templates.TemplateResponse(
                "partials/patient_header.html",
                {"request": request, "patient": None}
            )

        return templates.TemplateResponse(
            "partials/patient_header.html",
            {"request": request, "patient": patient}
        )

    except Exception as e:
        logger.error(f"Error getting current patient: {e}")
        return templates.TemplateResponse(
            "partials/patient_header.html",
            {"request": request, "patient": None}
        )


@router.get("/refresh", response_class=HTMLResponse)
async def refresh_patient(request: Request):
    """
    Re-query CCOW vault and return updated demographics partial.
    Called when user clicks "Refresh Patient" button.
    """
    # Same logic as get_current_patient
    return await get_current_patient(request)


@router.post("/set-context", response_class=HTMLResponse)
async def set_patient_context(request: Request):
    """
    Set patient context in CCOW vault and return demographics partial.
    Called when user selects a patient from search results.
    """
    try:
        form_data = await request.form()
        icn = form_data.get("icn")

        if not icn:
            raise HTTPException(status_code=400, detail="ICN required")

        # Update CCOW vault
        success = ccow_client.set_active_patient(patient_id=icn, set_by="med-z1")

        if not success:
            logger.warning(f"Failed to set CCOW context for {icn}")

        # Fetch patient demographics from PostgreSQL
        patient = get_patient_demographics(icn)

        if not patient:
            logger.error(f"Patient {icn} not found in database")
            raise HTTPException(status_code=404, detail="Patient not found")

        return templates.TemplateResponse(
            "partials/patient_header.html",
            {"request": request, "patient": patient}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting patient context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=HTMLResponse)
async def search_patients_endpoint(
    request: Request,
    query: str = "",
    search_type: str = "name"
):
    """
    Search for patients and return results partial.
    Called via HTMX from patient search modal (hx-trigger="keyup changed delay:500ms").

    Supported search types: name, icn, edipi (NOT ssn per VA policy)
    """
    try:
        if not query or len(query) < 2:
            return templates.TemplateResponse(
                "partials/patient_search_results.html",
                {"request": request, "results": None, "query": None}
            )

        # Query PostgreSQL for matching patients
        results = search_patients(query, search_type, limit=20)

        return templates.TemplateResponse(
            "partials/patient_search_results.html",
            {"request": request, "results": results, "query": query}
        )

    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/demographics")
async def get_patient_demographics_json(icn: str):
    """
    Get patient demographics as JSON (for future API use).
    """
    patient = get_patient_demographics(icn)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@router.get("/{icn}/flags")
async def get_patient_flags_json(icn: str):
    """
    Get patient flags as JSON.

    Returns complete flag data including counts and all flag details.
    Used by UI for badge display and future API consumers.
    """
    try:
        # Get all flags for patient
        flags = get_patient_flags(icn)

        # Get flag counts
        counts = get_flag_count(icn)

        # Calculate derived counts
        active_flags = [f for f in flags if f["is_active"]]

        return {
            "patient_icn": icn,
            "total_flags": counts["total"],
            "active_flags": counts["total"],
            "inactive_flags": len(flags) - counts["total"],
            "national_flags": counts["national"],
            "local_flags": counts["local"],
            "overdue_count": counts["overdue"],
            "flags": flags
        }

    except Exception as e:
        logger.error(f"Error getting flags for patient {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flags-content", response_class=HTMLResponse)
async def get_patient_flags_modal_content(request: Request):
    """
    Get patient flags modal content (HTML partial).
    Called when patient flags modal is opened (hx-trigger="revealed").

    Returns formatted HTML with all patient flags (active and inactive).
    """
    try:
        # Get current patient from CCOW
        patient_id = ccow_client.get_active_patient()

        if not patient_id:
            return "<p class='text-muted'>No active patient selected</p>"

        # Get all flags for patient
        flags = get_patient_flags(patient_id)
        counts = get_flag_count(patient_id)

        if not flags:
            return "<p class='text-muted'>No flags for this patient</p>"

        # Separate active and inactive flags
        active_flags = [f for f in flags if f["is_active"]]
        inactive_flags = [f for f in flags if not f["is_active"]]

        # Render using template
        return templates.TemplateResponse(
            "partials/patient_flags_content.html",
            {
                "request": request,
                "patient_icn": patient_id,
                "flags": flags,
                "active_flags": active_flags,
                "inactive_flags": inactive_flags,
                "counts": counts
            }
        )

    except Exception as e:
        logger.error(f"Error getting flags modal content: {e}")
        return f"<p class='text-danger'>Error loading flags: {str(e)}</p>"


@router.get("/{icn}/flags/{assignment_id}/history")
async def get_flag_history_json(icn: str, assignment_id: int):
    """
    Get complete history timeline for a specific flag assignment.

    WARNING: Returns SENSITIVE clinical narrative text.

    Args:
        icn: Patient ICN
        assignment_id: Flag assignment ID

    Returns:
        List of history records with narrative text
    """
    try:
        history = get_flag_history(assignment_id, icn)

        if not history:
            raise HTTPException(
                status_code=404,
                detail="No history found for this flag assignment"
            )

        return {
            "patient_icn": icn,
            "assignment_id": assignment_id,
            "history_count": len(history),
            "history": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting flag history for assignment {assignment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))