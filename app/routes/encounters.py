# ---------------------------------------------------------------------
# app/routes/encounters.py
# ---------------------------------------------------------------------
# Encounters API Routes and Pages
# Handles all inpatient encounter API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime, timedelta
import logging
import math

from app.db.encounters import (
    get_patient_encounters,
    get_recent_encounters,
    get_active_admissions,
    get_encounter_counts,
    get_encounter_by_id
)
from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context

# API router for encounters endpoints
router = APIRouter(prefix="/api/patient", tags=["encounters"])

# Page router for full encounters pages (no prefix for flexibility)
page_router = APIRouter(tags=["encounters-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/{icn}/encounters")
async def get_patient_encounters_endpoint(
    icn: str,
    limit: Optional[int] = Query(100, ge=1, le=500),
    offset: Optional[int] = Query(0, ge=0),
    active_only: Optional[bool] = Query(False),
    recent_only: Optional[bool] = Query(False)
):
    """
    Get all encounters for a patient.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of encounters to return (1-500, default 100)
        offset: Number of encounters to skip (for pagination, default 0)
        active_only: If True, return only active admissions
        recent_only: If True, return only recent encounters (last 30 days)

    Returns:
        JSON with list of encounters
    """
    try:
        encounters = get_patient_encounters(
            icn,
            limit=limit,
            offset=offset,
            active_only=active_only,
            recent_only=recent_only
        )
        counts = get_encounter_counts(icn)

        return {
            "patient_icn": icn,
            "count": len(encounters),
            "offset": offset,
            "limit": limit,
            "total_encounters": counts["total_encounters"],
            "encounters": encounters,
            "counts": counts
        }

    except Exception as e:
        logger.error(f"Error fetching encounters for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/encounters/recent")
async def get_recent_encounters_endpoint(
    icn: str,
    limit: Optional[int] = Query(5, ge=1, le=20)
):
    """
    Get the most recent encounters for a patient (active and recently discharged).
    Used for dashboard widget to show current admission status.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of encounters to return (1-20, default 5)

    Returns:
        JSON with recent encounters
    """
    try:
        encounters = get_recent_encounters(icn, limit=limit)
        counts = get_encounter_counts(icn)

        return {
            "patient_icn": icn,
            "count": len(encounters),
            "encounters": encounters,
            "counts": counts
        }

    except Exception as e:
        logger.error(f"Error fetching recent encounters for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/encounters/active")
async def get_active_admissions_endpoint(icn: str):
    """
    Get currently active admissions for a patient.
    Used for alerts and current admission status.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with active admissions
    """
    try:
        admissions = get_active_admissions(icn)

        return {
            "patient_icn": icn,
            "count": len(admissions),
            "active_admissions": admissions
        }

    except Exception as e:
        logger.error(f"Error fetching active admissions for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widget/encounters/{icn}", response_class=HTMLResponse)
async def get_encounters_widget(request: Request, icn: str):
    """
    Render encounters widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing recent encounters.

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for encounters widget
    """
    try:
        # Get recent encounters (up to 4 for widget display)
        encounters = get_recent_encounters(icn, limit=4)
        counts = get_encounter_counts(icn)

        return templates.TemplateResponse(
            "partials/encounters_widget.html",
            {
                "request": request,
                "icn": icn,
                "encounters": encounters,
                "counts": counts,
                "has_encounters": len(encounters) > 0
            }
        )

    except Exception as e:
        logger.error(f"Error rendering encounters widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/encounters_widget.html",
            {
                "request": request,
                "icn": icn,
                "encounters": [],
                "counts": {},
                "has_encounters": False,
                "error": str(e)
            }
        )


# ============================================
# Full Page Routes
# ============================================

@page_router.get("/encounters")
async def encounters_redirect():
    """
    Redirect to current patient's encounters page.
    Gets patient from CCOW and redirects to /patient/{icn}/encounters.
    If no patient selected, redirects to dashboard.
    """
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient()

    if not patient_icn:
        logger.warning("No active patient in CCOW for encounters page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/encounters", status_code=303)


@page_router.get("/patient/{icn}/encounters", response_class=HTMLResponse)
async def get_encounters_page(
    request: Request,
    icn: str,
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(20, ge=10, le=100),
    filter_active: Optional[bool] = Query(False),
    filter_recent: Optional[bool] = Query(False)
):
    """
    Full encounters page for a patient with pagination.

    Shows comprehensive table of all encounters with filtering and pagination.
    This is the first domain in med-z1 to use pagination (ADR-005).

    Args:
        icn: Patient ICN
        page: Page number (default 1, starts at 1)
        page_size: Number of encounters per page (10-100, default 20)
        filter_active: If True, show only active admissions
        filter_recent: If True, show only recent encounters

    Returns:
        Full HTML page with encounters table and pagination
    """
    try:
        # Get patient demographics for header
        patient = get_patient_demographics(icn)

        if not patient:
            logger.warning(f"Patient {icn} not found")
            return templates.TemplateResponse(
                "patient_encounters.html",
                get_base_context(
                    request,
                    patient=None,
                    error="Patient not found"
                )
            )

        # Get encounter counts for stats
        counts = get_encounter_counts(icn)

        # Calculate offset for pagination
        offset = (page - 1) * page_size

        # Get encounters for current page
        encounters = get_patient_encounters(
            icn,
            limit=page_size,
            offset=offset,
            active_only=filter_active,
            recent_only=filter_recent
        )

        # Determine total count based on filters
        if filter_active:
            total_count = counts["active_admissions"]
        elif filter_recent:
            total_count = counts["recent_encounters"]
        else:
            total_count = counts["total_encounters"]

        # Calculate pagination info
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
        has_prev = page > 1
        has_next = page < total_pages

        logger.info(
            f"Loaded encounters page for {icn}: page {page}/{total_pages}, "
            f"{len(encounters)} encounters, filters: active={filter_active}, recent={filter_recent}"
        )

        # Calculate data freshness (yesterday's date for PostgreSQL data)
        yesterday = datetime.now() - timedelta(days=1)
        data_current_through = yesterday.strftime("%b %d, %Y")
        data_freshness_label = "yesterday"

        return templates.TemplateResponse(
            "patient_encounters.html",
            get_base_context(
                request,
                patient=patient,
                encounters=encounters,
                counts=counts,
                filter_active=filter_active,
                filter_recent=filter_recent,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_prev=has_prev,
                has_next=has_next,
                active_page="encounters",
                data_current_through=data_current_through,
                data_freshness_label=data_freshness_label,
                vista_refreshed=False
            )
        )

    except Exception as e:
        logger.error(f"Error loading encounters page for {icn}: {e}")
        return templates.TemplateResponse(
            "patient_encounters.html",
            get_base_context(
                request,
                patient=None,
                error=str(e),
                active_page="encounters"
            )
        )


@page_router.get("/patient/{icn}/encounters/realtime", response_class=HTMLResponse)
async def get_encounters_realtime(
    request: Request,
    icn: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=10, le=100),
    filter_active: Optional[bool] = Query(False),
    filter_recent: Optional[bool] = Query(False)
):
    """
    VistA real-time refresh endpoint for encounters.

    Fetches today's encounters from VistA sites and merges with historical PostgreSQL data.
    Returns HTML partial for HTMX swap.

    Args:
        icn: Patient ICN
        page: Page number for pagination
        page_size: Number of encounters per page
        filter_active: Filter to active admissions only
        filter_recent: Filter to recent encounters only

    Returns:
        HTML partial containing encounters refresh area
    """
    try:
        logger.info(f"VistA realtime refresh requested for encounters - patient {icn}")

        # Get patient demographics
        patient = get_patient_demographics(icn)
        if not patient:
            logger.warning(f"Patient {icn} not found during realtime refresh")
            patient = {"icn": icn, "name_display": "Unknown Patient"}

        # Fetch real-time data from VistA
        from app.services.vista_client import VistaClient

        vista_client = VistaClient()

        # Get target sites for encounters (3 sites per domain policy)
        target_sites = vista_client.get_target_sites(icn, domain="encounters")
        logger.info(f"Querying {len(target_sites)} VistA sites for encounters: {target_sites}")

        # Call ORWCV ADMISSIONS RPC at all target sites
        vista_results_raw = await vista_client.call_rpc_multi_site(
            sites=target_sites,
            rpc_name="ORWCV ADMISSIONS",
            params=[icn, 90]  # ICN + 90 days lookback
        )

        # Extract successful responses
        vista_results = {}
        for site_sta3n, result in vista_results_raw.items():
            if result.get("success") and result.get("response"):
                vista_results[site_sta3n] = result["response"]

        logger.info(f"Vista query complete: {len(vista_results)} successful sites")

        # Parse Vista encounters from caret-delimited format
        from app.services.realtime_overlay import parse_fileman_datetime

        vista_encounters = []
        for site_sta3n, response_text in vista_results.items():
            # Skip error responses
            if response_text.startswith("-1^"):
                logger.warning(f"Vista error from site {site_sta3n}: {response_text}")
                continue

            # Parse each line (one encounter per line)
            for line in response_text.strip().split('\n'):
                if not line:
                    continue

                fields = line.split('^')
                if len(fields) >= 9:
                    # Convert FileMan dates to ISO format (YYYY-MM-DD HH:MM:SS)
                    admit_dt = parse_fileman_datetime(fields[1])
                    admit_datetime_iso = admit_dt.strftime("%Y-%m-%d %H:%M:%S") if admit_dt else fields[1]

                    discharge_dt = parse_fileman_datetime(fields[4]) if fields[4] else None
                    discharge_datetime_iso = discharge_dt.strftime("%Y-%m-%d %H:%M:%S") if discharge_dt else None

                    encounter = {
                        "inpatient_id": fields[0],
                        "admit_datetime": admit_datetime_iso,
                        "admit_location_name": fields[2],
                        "encounter_status": fields[3],
                        "discharge_datetime": discharge_datetime_iso,
                        "discharge_location_name": fields[5] if fields[5] else None,
                        "length_of_stay": int(fields[6]) if fields[6] else 0,
                        "admit_diagnosis_code": fields[7],
                        "admitting_provider_name": fields[8],
                        "facility_name": f"Site {site_sta3n}",
                        "sta3n": site_sta3n,
                        "source": "vista"
                    }
                    vista_encounters.append(encounter)

        logger.info(f"Parsed {len(vista_encounters)} encounters from Vista")

        # Get PostgreSQL encounters (T-1 and earlier)
        pg_encounters = get_patient_encounters(
            icn,
            limit=1000,  # Get all for merging
            offset=0,
            active_only=filter_active,
            recent_only=filter_recent
        )

        # Mark PostgreSQL encounters
        for enc in pg_encounters:
            enc["source"] = "postgresql"

        # Merge encounters (simple append for now - Vista data comes first)
        all_encounters = vista_encounters + pg_encounters

        # Sort by admit_datetime descending (most recent first)
        all_encounters.sort(
            key=lambda x: x.get("admit_datetime", ""),
            reverse=True
        )

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_encounters = all_encounters[start_idx:end_idx]

        # Get counts
        counts = get_encounter_counts(icn)

        # Determine total count
        if filter_active:
            total_count = counts["active_admissions"]
        elif filter_recent:
            total_count = counts["recent_encounters"]
        else:
            total_count = len(all_encounters)

        # Calculate pagination
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
        has_prev = page > 1
        has_next = page < total_pages

        logger.info(f"Returning {len(paginated_encounters)} encounters (page {page}/{total_pages})")

        # Calculate data freshness (today's date after Vista refresh)
        now = datetime.now()
        data_current_through = now.strftime("%b %d, %Y")
        last_updated = now.strftime("%I:%M %p")

        # Return partial template for HTMX swap
        return templates.TemplateResponse(
            "partials/encounters_content.html",
            get_base_context(
                request,
                patient=patient,
                encounters=paginated_encounters,
                counts=counts,
                filter_active=filter_active,
                filter_recent=filter_recent,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_prev=has_prev,
                has_next=has_next,
                vista_refreshed=True,
                data_current_through=data_current_through,
                last_updated=last_updated,
                active_page="encounters"
            )
        )

    except Exception as e:
        logger.error(f"Error during Vista realtime refresh for encounters: {e}", exc_info=True)
        # Return error partial
        return templates.TemplateResponse(
            "partials/encounters_content.html",
            get_base_context(
                request,
                patient=patient if 'patient' in locals() else None,
                encounters=[],
                error=f"Error fetching real-time data: {str(e)}",
                active_page="encounters"
            )
        )
