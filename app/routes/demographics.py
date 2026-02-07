# ---------------------------------------------------------------------
# app/routes/demographics.py
# ---------------------------------------------------------------------
# Demographics Domain Routes
# Handles full demographics page and related endpoints
# ---------------------------------------------------------------------
# Pattern B: Dedicated router for domains with full page views
# ---------------------------------------------------------------------

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.patient import get_patient_demographics
from app.db.military_history import get_patient_military_history, get_priority_group
from app.utils.template_context import get_base_context
import logging

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

# Page router for full demographics page
page_router = APIRouter(tags=["demographics-pages"])


@page_router.get("/patient/{icn}/demographics", response_class=HTMLResponse)
async def get_patient_demographics_page(request: Request, icn: str):
    """
    Full Demographics page for a specific patient.

    Displays comprehensive demographic information including:
    - Basic demographics (name, DOB, age, sex, SSN, ICN)
    - Contact information (phone, address)
    - Insurance information
    - Marital status, religion
    - Service connected percentage with priority group
    - Environmental exposures (Agent Orange, radiation, POW, etc.)
    - Deceased status and date (if applicable)

    Args:
        request: FastAPI Request object
        icn: Patient ICN

    Returns:
        HTMLResponse with patient demographics page

    Raises:
        HTTPException: 404 if patient not found
    """
    logger.info(f"Demographics page requested for patient ICN: {icn}")

    # Get patient demographics from database
    patient = get_patient_demographics(icn)

    if not patient:
        logger.warning(f"Patient not found for ICN: {icn}")
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get military history (if available)
    military_history = get_patient_military_history(icn)

    # Determine priority group based on service connected percentage
    priority_group = None
    if military_history and military_history.get('service_connected_percent') is not None:
        priority_group = get_priority_group(military_history['service_connected_percent'])

    # Render full demographics page template
    return templates.TemplateResponse(
        "patient_demographics.html",
        get_base_context(
            request,
            patient=patient,
            military_history=military_history,
            priority_group=priority_group,
            active_page="demographics"
        )
    )


@page_router.get("/demographics")
async def demographics_redirect(request: Request):
    """
    Redirect to current patient's demographics page.

    Gets the current patient from CCOW context and redirects
    to their demographics page. If no patient is selected, redirects
    to dashboard.

    Args:
        request: FastAPI Request object

    Returns:
        RedirectResponse to patient demographics page or dashboard
    """
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient(request)

    if not patient_icn:
        logger.warning("No active patient in CCOW for demographics page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/demographics", status_code=303)
