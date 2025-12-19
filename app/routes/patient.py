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
from app.utils.template_context import get_base_context
from app.db.patient import get_patient_demographics, search_patients
from app.db.patient_flags import (
    get_patient_flags,
    get_flag_count,
    get_flag_history,
    get_active_flags_count
)
from app.db.patient_allergies import (
    get_patient_allergies,
    get_critical_allergies,
    get_allergy_details,
    get_allergy_count
)

router = APIRouter(prefix="/api/patient", tags=["patient"])
page_router = APIRouter(tags=["patient-pages"])  # For allergies full page routes
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
            logger.warning("No patient context in CCOW when flags modal opened")
            return "<p class='text-muted'>No active patient selected</p>"

        logger.info(f"Loading flags modal content for patient: {patient_id}")

        # Get all flags for patient
        flags = get_patient_flags(patient_id)

        if not flags:
            return "<p class='text-muted'>No flags for this patient</p>"

        # Separate active and inactive flags
        active_flags = [f for f in flags if f["is_active"]]
        inactive_flags = [f for f in flags if not f["is_active"]]

        # Separate active flags by category (National=I, Local=II)
        national_flags = [f for f in active_flags if f["flag_category"] == "I"]
        local_flags = [f for f in active_flags if f["flag_category"] == "II"]

        total_count = len(active_flags)

        logger.info(f"Found {total_count} active flags for {patient_id} ({len(national_flags)} national, {len(local_flags)} local)")

        # Render using template
        return templates.TemplateResponse(
            "partials/patient_flags_content.html",
            {
                "request": request,
                "patient_icn": patient_id,
                "total_count": total_count,
                "national_flags": national_flags,
                "local_flags": local_flags,
                "inactive_flags": inactive_flags
            }
        )

    except Exception as e:
        logger.error(f"Error getting flags modal content: {e}")
        return f"<p class='text-danger'>Error loading flags: {str(e)}</p>"


@router.get("/{icn}/flags/{assignment_id}/history")
async def get_flag_history_endpoint(request: Request, icn: str, assignment_id: int):
    """
    Get complete history timeline for a specific flag assignment.

    WARNING: Returns SENSITIVE clinical narrative text.

    Returns HTML for HTMX requests, JSON for API consumers.

    Args:
        request: FastAPI request object
        icn: Patient ICN
        assignment_id: Flag assignment ID

    Returns:
        HTML partial (for HTMX) or JSON (for API consumers)
    """
    try:
        history = get_flag_history(assignment_id, icn)

        if not history:
            # Check if HTMX request
            is_htmx = request.headers.get("HX-Request") == "true"
            if is_htmx:
                return HTMLResponse("<p class='text-muted'>No history records available for this flag.</p>")
            else:
                raise HTTPException(
                    status_code=404,
                    detail="No history found for this flag assignment"
                )

        # Check if request is from HTMX (has HX-Request header)
        is_htmx = request.headers.get("HX-Request") == "true"

        if is_htmx:
            # Return HTML partial for HTMX
            return templates.TemplateResponse(
                "partials/flag_history.html",
                {
                    "request": request,
                    "history": history
                }
            )
        else:
            # Return JSON for API consumers
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
        # Check if HTMX request for error response
        is_htmx = request.headers.get("HX-Request") == "true"
        if is_htmx:
            return HTMLResponse(f"<p class='text-danger'>Error loading history: {str(e)}</p>")
        else:
            raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# Allergies Endpoints
# =========================================================================

@router.get("/{icn}/allergies")
async def get_patient_allergies_json(icn: str):
    """
    Get all patient allergies as JSON.

    Returns complete allergy data sorted by:
    1. Drug allergies first
    2. Severity rank (SEVERE > MODERATE > MILD)
    3. Most recent date first

    Args:
        icn: Patient ICN

    Returns:
        JSON with allergy counts and full allergy list
    """
    try:
        # Get all allergies for patient
        allergies = get_patient_allergies(icn)

        # Get allergy counts
        counts = get_allergy_count(icn)

        return {
            "patient_icn": icn,
            "total_allergies": counts["total"],
            "drug_allergies": counts["drug"],
            "food_allergies": counts["food"],
            "environmental_allergies": counts["environmental"],
            "severe_allergies": counts["severe"],
            "allergies": allergies
        }

    except Exception as e:
        logger.error(f"Error getting allergies for patient {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/allergies/critical")
async def get_patient_critical_allergies_json(icn: str, limit: int = 6):
    """
    Get critical allergies for dashboard widget display.

    Prioritizes drug allergies with highest severity.

    Args:
        icn: Patient ICN
        limit: Maximum number of allergies to return (default 6)

    Returns:
        JSON with critical allergy list (limited)
    """
    try:
        # Get critical allergies (drug first, severity desc, date desc)
        allergies = get_critical_allergies(icn, limit=limit)

        # Get counts for badge display
        counts = get_allergy_count(icn)

        return {
            "patient_icn": icn,
            "total_allergies": counts["total"],
            "drug_allergies": counts["drug"],
            "severe_allergies": counts["severe"],
            "displayed_count": len(allergies),
            "allergies": allergies
        }

    except Exception as e:
        logger.error(f"Error getting critical allergies for patient {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/allergies/{allergy_sid}/details")
async def get_allergy_details_json(icn: str, allergy_sid: int):
    """
    Get detailed information for a specific allergy.

    Includes full details including comment field (may be large).

    Args:
        icn: Patient ICN (for security validation)
        allergy_sid: Allergy SID (surrogate ID)

    Returns:
        JSON with complete allergy details
    """
    try:
        allergy = get_allergy_details(allergy_sid, icn)

        if not allergy:
            raise HTTPException(
                status_code=404,
                detail=f"Allergy {allergy_sid} not found for patient {icn}"
            )

        return allergy

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting allergy details for SID {allergy_sid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# Allergies Page Routes
# =========================================================================

@page_router.get("/allergies", response_class=HTMLResponse)
async def allergies_redirect(request: Request):
    """
    Redirect to current patient's allergies page.
    Gets patient from CCOW and redirects to /patient/{icn}/allergies.
    If no patient selected, redirects to dashboard.
    """
    from fastapi.responses import RedirectResponse

    patient_icn = ccow_client.get_active_patient()

    if not patient_icn:
        logger.warning("No active patient in CCOW for allergies page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/allergies", status_code=303)


@page_router.get("/patient/{icn}/allergies", response_class=HTMLResponse)
async def get_allergies_page(request: Request, icn: str):
    """
    Full allergies page for a patient.

    Shows card-based view with sections for Drug, Food, and Environmental allergies.

    Args:
        icn: Patient ICN

    Returns:
        Full HTML page with allergies cards
    """
    try:
        # Get patient demographics for header
        patient = get_patient_demographics(icn)

        if not patient:
            logger.warning(f"Patient {icn} not found")
            return templates.TemplateResponse(
                "allergies.html",
                get_base_context(
                    request,
                    patient=None,
                    error="Patient not found"
                )
            )

        # Get all allergies for patient
        allergies = get_patient_allergies(icn)

        # Get counts for summary
        counts = get_allergy_count(icn)

        # Separate allergies by type
        drug_allergies = [a for a in allergies if a["allergen_type"] == "DRUG"]
        food_allergies = [a for a in allergies if a["allergen_type"] == "FOOD"]
        environmental_allergies = [a for a in allergies if a["allergen_type"] == "ENVIRONMENTAL"]

        logger.info(f"Loaded allergies page for {icn}: {len(allergies)} allergies ({counts['drug']} drug, {counts['food']} food, {counts['environmental']} environmental)")

        return templates.TemplateResponse(
            "allergies.html",
            get_base_context(
                request,
                patient=patient,
                allergies=allergies,
                drug_allergies=drug_allergies,
                food_allergies=food_allergies,
                environmental_allergies=environmental_allergies,
                total_count=counts["total"],
                drug_count=counts["drug"],
                food_count=counts["food"],
                environmental_count=counts["environmental"],
                severe_count=counts["severe"],
                active_page="allergies"
            )
        )

    except Exception as e:
        logger.error(f"Error loading allergies page for {icn}: {e}")
        return templates.TemplateResponse(
            "allergies.html",
            get_base_context(
                request,
                patient=None,
                error=str(e),
                active_page="allergies"
            )
        )


# =========================================================================
# Allergies Widget Route
# =========================================================================

@router.get("/dashboard/widget/allergies/{icn}", response_class=HTMLResponse)
async def get_allergies_widget(request: Request, icn: str):
    """
    Render allergies widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing critical allergies (drug allergies prioritized).

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for allergies widget
    """
    try:
        # Get critical allergies (top 6, drug allergies prioritized)
        allergies = get_critical_allergies(icn, limit=6)

        # Get counts for summary stats
        counts = get_allergy_count(icn)

        return templates.TemplateResponse(
            "partials/allergies_widget.html",
            {
                "request": request,
                "icn": icn,
                "allergies": allergies,
                "total_count": counts["total"],
                "drug_count": counts["drug"],
                "severe_count": counts["severe"],
                "displayed_count": len(allergies)
            }
        )

    except Exception as e:
        logger.error(f"Error rendering allergies widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/allergies_widget.html",
            {
                "request": request,
                "icn": icn,
                "allergies": [],
                "total_count": 0,
                "drug_count": 0,
                "severe_count": 0,
                "displayed_count": 0,
                "error": str(e)
            }
        )