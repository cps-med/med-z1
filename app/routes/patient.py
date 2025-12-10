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
from app.db.patient import get_patient_demographics, search_patients, get_patient_flags

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

    NOTE: Phase 3 implementation - currently returns placeholder data.
    """
    flags_data = get_patient_flags(icn)
    return flags_data


@router.get("/flags-content", response_class=HTMLResponse)
async def get_patient_flags_modal_content(request: Request):
    """
    Get patient flags modal content (HTML partial).
    Called when patient flags modal is opened (hx-trigger="revealed").

    NOTE: Phase 3 implementation - currently returns placeholder HTML.
    """
    # Get current patient from CCOW
    patient_id = ccow_client.get_active_patient()

    if not patient_id:
        return "<p class='text-muted'>No active patient selected</p>"

    # Get flags (Phase 3 placeholder)
    flags_data = get_patient_flags(patient_id)
    flags = flags_data.get("flags", [])

    if not flags:
        return "<p class='text-muted'>No active flags for this patient</p>"

    # Render flags HTML (Phase 3 - use proper template)
    html = '<div class="flags-list">'
    for flag in flags:
        html += f'''
        <div class="flag-item flag-item--high-risk">
            <h3>{flag["flag_name"]}</h3>
            <p><strong>Category:</strong> {flag["category"]}</p>
            <p><strong>Active Date:</strong> {flag["active_date"]}</p>
            <p><strong>Review Date:</strong> {flag.get("review_date", "N/A")}</p>
            <p>{flag["narrative"]}</p>
        </div>
        '''
    html += '</div>'
    html += '<p class="text-muted"><em>Note: Full flags implementation in Phase 3</em></p>'

    return html