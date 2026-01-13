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
from datetime import datetime

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
    medication_type: Optional[str] = Query("all", regex="^(outpatient|inpatient|all)$"),
    status: Optional[str] = Query("all"),
    date_range: Optional[str] = Query("all"),
    sort_by: Optional[str] = Query("date_desc", regex="^(date_desc|date_asc|drug_name|type)$")
):
    """
    Full medications page for a patient.

    Shows comprehensive table/timeline of all medications (outpatient + inpatient)
    with filtering and sorting. Supports HTMX partial updates.

    Args:
        icn: Patient ICN
        medication_type: Filter by type ('outpatient', 'inpatient', 'all', default: 'all')
        status: Filter by status (for outpatient medications, default: 'all')
        date_range: Show medications from date range ('30', '90', '180', '365', 'all', default: '90')
        sort_by: Combined sort field and order ('date_desc', 'date_asc', 'drug_name', 'type', default: 'date_desc')

    Returns:
        Full HTML page with medications timeline table (or partial for HTMX)
    """
    try:
        # Parse combined sort_by parameter
        if sort_by == "date_desc":
            sort_field, sort_order = "date", "desc"
        elif sort_by == "date_asc":
            sort_field, sort_order = "date", "asc"
        elif sort_by == "drug_name":
            sort_field, sort_order = "drug_name", "asc"
        elif sort_by == "type":
            sort_field, sort_order = "type", "asc"
        else:
            sort_field, sort_order = "date", "desc"

        # Convert date_range to days
        days_map = {"30": 30, "90": 90, "180": 180, "365": 365, "all": 3650}
        days_filter = days_map.get(date_range, 90)

        # Auto-reset status when medication_type is inpatient
        if medication_type == "inpatient":
            status = None
        elif status == "all":
            status = None

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

        # Check for cached Vista data (persists after "Refresh from Vista" click)
        from app.services.vista_cache import VistaSessionCache
        from app.services.realtime_overlay import merge_medications_data

        cached_vista = VistaSessionCache.get_cached_data(request, icn, "medications")

        if cached_vista:
            # Vista data cached - merge with PostgreSQL for consistent filtering
            logger.info(f"Using cached Vista data for medications filtering (age: {cached_vista.get('timestamp')})")

            # Fetch PostgreSQL data (all types, all statuses, all time)
            pg_medications = get_patient_medications(
                icn,
                limit=500,
                medication_type=None,  # Get both types for merge
                status=None,  # Get all statuses for merge
                days=3650  # Get all historical data
            )

            # Merge with cached Vista responses
            vista_responses = cached_vista.get("vista_responses", {})
            medications, _ = merge_medications_data(pg_medications, vista_responses, icn)

            # Get counts from merged data
            all_outpatient = [m for m in medications if m.get("type") == "outpatient"]
            all_inpatient = [m for m in medications if m.get("type") == "inpatient"]

            counts = {
                "outpatient_total": len(all_outpatient),
                "inpatient_total": len(all_inpatient),
                "outpatient_active": len([m for m in all_outpatient if m.get("status") == "ACTIVE"]),
                "outpatient_controlled": len([m for m in all_outpatient if m.get("is_controlled_substance")]),
                "inpatient_controlled": len([m for m in all_inpatient if m.get("is_controlled_substance")])
            }

            # Apply filters to merged data
            if medication_type != "all":
                medications = [m for m in medications if m.get("type") == medication_type]

            # Apply status filter only to outpatient (inpatient uses different status field)
            if status:
                medications = [m for m in medications if m.get("type") == "inpatient" or m.get("status") == status]

            # Apply date range filter
            if days_filter < 3650:
                from datetime import timedelta
                cutoff_date = (datetime.now() - timedelta(days=days_filter)).strftime("%Y-%m-%d")
                medications = [m for m in medications if (m.get("date") or m.get("issue_date") or "")[:10] >= cutoff_date]

            vista_refreshed = True
            cache_sites = cached_vista.get("sites", [])
            vista_cached = True
        else:
            # No cached Vista data - use PostgreSQL only (original behavior)
            med_type_for_query = None if medication_type == "all" else medication_type

            medications = get_patient_medications(
                icn,
                limit=500,
                medication_type=med_type_for_query,
                status=status,
                days=days_filter
            )

            # Get medication counts for filter dropdowns
            counts = get_medication_counts(icn)

            vista_refreshed = False
            cache_sites = []
            vista_cached = False

        # Sort medications
        reverse = (sort_order == "desc")

        if sort_field == "date":
            medications = sorted(medications, key=lambda m: m.get("date") or m.get("issue_date") or "", reverse=reverse)
        elif sort_field == "drug_name":
            medications = sorted(medications, key=lambda m: m.get("drug_name_local") or m.get("drug_name") or "", reverse=reverse)
        elif sort_field == "type":
            medications = sorted(medications, key=lambda m: m.get("type") or "", reverse=reverse)

        logger.info(f"Loaded medications page for {icn}: {len(medications)} medications, type={medication_type}, days={days_filter}, sort={sort_field} {sort_order}, vista_cached={vista_cached}")

        # Calculate data freshness
        from datetime import timedelta
        if vista_refreshed:
            # Vista data included - show today's date
            data_current_through = datetime.now().strftime("%b %d, %Y")
            data_freshness_label = "today"
            last_updated = datetime.now().strftime("%I:%M %p")
        else:
            # PostgreSQL only - show yesterday's date
            yesterday = datetime.now() - timedelta(days=1)
            data_current_through = yesterday.strftime("%b %d, %Y")
            data_freshness_label = "yesterday"
            last_updated = None

        return templates.TemplateResponse(
            "patient_medications.html",
            get_base_context(
                request,
                patient=patient,
                medications=medications,
                counts=counts,
                medication_type_filter=medication_type,
                status_filter=status,
                days_filter=days_filter,
                date_range_filter=date_range,
                sort_by=sort_field,
                sort_order=sort_order,
                total_count=len(medications),
                active_page="medications",
                data_current_through=data_current_through,
                data_freshness_label=data_freshness_label,
                vista_refreshed=vista_refreshed,
                last_updated=last_updated,
                vista_cached=vista_cached,
                cache_sites=cache_sites
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


@page_router.get("/patient/{icn}/medications/realtime", response_class=HTMLResponse)
async def get_medications_realtime(
    request: Request,
    icn: str,
    medication_type: Optional[str] = Query("all", regex="^(outpatient|inpatient|all)$"),
    status: Optional[str] = Query("all"),
    date_range: Optional[str] = Query("all"),
    sort_by: Optional[str] = Query("date_desc", regex="^(date_desc|date_asc|drug_name|type)$")
):
    """
    VistA real-time refresh endpoint for medications.

    Fetches today's active outpatient medications from VistA sites and merges with historical PostgreSQL data.
    Returns only the page content div (for HTMX swap).

    Args:
        icn: Patient ICN
        medication_type: Filter by type ('outpatient', 'inpatient', 'all', default: 'all')
        status: Filter by status (for outpatient medications, default: 'all')
        date_range: Date range filter ('30', '90', '180', '365', 'all', default: 'all')
        sort_by: Combined sort field and order ('date_desc', 'date_asc', 'drug_name', 'type', default: 'date_desc')

    Returns:
        HTML partial containing medications content (filters + table)
    """
    try:
        logger.info(f"VistA realtime refresh requested for medications - patient {icn}")

        # Get patient demographics for page title
        patient = get_patient_demographics(icn)
        if not patient:
            logger.warning(f"Patient {icn} not found during realtime refresh")
            patient = {"icn": icn, "name_display": "Unknown Patient"}

        # Fetch real-time data from VistA
        from app.services.vista_client import VistaClient
        from app.services.realtime_overlay import merge_medications_data

        vista_client = VistaClient()

        # Get target sites for medications (limit 3 sites per domain policy)
        target_sites = vista_client.get_target_sites(icn, domain="medications")
        logger.info(f"Querying {len(target_sites)} VistA sites for medications: {target_sites}")

        # Call ORWPS COVER RPC at all target sites
        vista_results_raw = await vista_client.call_rpc_multi_site(
            sites=target_sites,
            rpc_name="ORWPS COVER",
            params=[icn]
        )

        # Extract successful responses (site -> response string)
        vista_results = {}
        for site, response in vista_results_raw.items():
            if response.get("success"):
                vista_results[site] = response.get("response", "")
            else:
                logger.warning(f"Vista RPC failed at site {site}: {response.get('error')}")

        # Get historical data from PostgreSQL (T-1 and earlier)
        # Get all types for merge, filter after
        pg_medications = get_patient_medications(
            icn,
            limit=500,
            medication_type=None,  # Get both outpatient and inpatient
            status=None,  # Get all statuses for merge
            days=3650  # Get all historical data
        )

        # Merge PostgreSQL + Vista data
        medications, merge_stats = merge_medications_data(pg_medications, vista_results, icn)

        # Cache Vista RPC responses (NOT merged data) to avoid cookie size limit
        from app.services.vista_cache import VistaSessionCache

        # Store raw Vista responses (small - just strings), not merged data
        VistaSessionCache.set_cached_data(
            request=request,
            patient_icn=icn,
            domain="medications",
            vista_responses=vista_results,  # Raw RPC response strings
            sites=list(vista_results.keys()),
            stats=merge_stats
        )

        logger.info(
            f"Merge complete: {merge_stats['total_merged']} medications "
            f"({merge_stats['pg_count']} PG + {merge_stats['vista_count']} Vista) - Vista responses cached in session"
        )

        # Recalculate counts from ALL merged data (before any filtering)
        all_merged_medications = medications.copy()
        all_outpatient = [m for m in all_merged_medications if m.get("type") == "outpatient"]
        all_inpatient = [m for m in all_merged_medications if m.get("type") == "inpatient"]

        counts = {
            "outpatient_total": len(all_outpatient),
            "inpatient_total": len(all_inpatient),
            "outpatient_active": len([m for m in all_outpatient if m.get("status") == "ACTIVE"]),
            "outpatient_controlled": len([m for m in all_outpatient if m.get("controlled_substance")]),
            "inpatient_controlled": len([m for m in all_inpatient if m.get("controlled_substance")])
        }

        # Parse combined sort_by parameter
        if sort_by == "date_desc":
            sort_field, sort_order = "date", "desc"
        elif sort_by == "date_asc":
            sort_field, sort_order = "date", "asc"
        elif sort_by == "drug_name":
            sort_field, sort_order = "drug_name", "asc"
        elif sort_by == "type":
            sort_field, sort_order = "type", "asc"
        else:
            sort_field, sort_order = "date", "desc"

        # Convert date_range to days
        days_map = {"30": 30, "90": 90, "180": 180, "365": 365, "all": 3650}
        days_filter = days_map.get(date_range, 3650)

        # Apply filters AFTER merge and counts calculation
        # Auto-reset status when medication_type is inpatient
        if medication_type == "inpatient":
            status = None
        elif status == "all":
            status = None

        # Apply filters
        if medication_type != "all":
            medications = [m for m in medications if m.get("type") == medication_type]

        # Apply status filter only to outpatient medications (inpatient uses different status field)
        if status:
            medications = [m for m in medications if m.get("type") == "inpatient" or m.get("status") == status]

        # Apply date range filter (based on date or issue_date field)
        if days_filter < 3650:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days_filter)).strftime("%Y-%m-%d")
            medications = [m for m in medications if (m.get("date") or m.get("issue_date") or "")[:10] >= cutoff_date]

        # Sort medications (same logic as initial page load)
        reverse = (sort_order == "desc")

        if sort_field == "date":
            medications = sorted(medications, key=lambda m: m.get("date") or m.get("issue_date") or "", reverse=reverse)
        elif sort_field == "drug_name":
            medications = sorted(medications, key=lambda m: m.get("drug_name_local") or m.get("drug_name") or "", reverse=reverse)
        elif sort_field == "type":
            medications = sorted(medications, key=lambda m: m.get("type") or "", reverse=reverse)

        # Calculate data freshness (today's date after VistA refresh)
        now = datetime.now()
        data_current_through = now.strftime("%b %d, %Y")
        last_updated = now.strftime("%I:%M %p")

        # Calculate Vista success rate
        successful_sites = len(vista_results)
        total_sites_attempted = len(target_sites)
        vista_success_rate = f"{successful_sites} of {total_sites_attempted} sites" if total_sites_attempted > 0 else "no sites"

        logger.info(
            f"VistA refresh complete for medications {icn}: {len(medications)} medications "
            f"({vista_success_rate} successful)"
        )

        # Return only the content portion (for HTMX outerHTML swap)
        # Note: This returns the refresh area + out-of-band freshness update
        return templates.TemplateResponse(
            "partials/medications_refresh_area.html",
            get_base_context(
                request,
                patient=patient,
                medications=medications,
                counts=counts,
                medication_type_filter=medication_type,
                status_filter=status,
                days_filter=days_filter,
                date_range_filter=date_range,
                sort_by=sort_field,
                sort_order=sort_order,
                total_count=len(medications),
                active_page="medications",
                # Real-time refresh metadata
                vista_refreshed=True,
                vista_sites_queried=target_sites,
                vista_sites_successful=list(vista_results.keys()),
                vista_success_rate=vista_success_rate,
                data_current_through=data_current_through,
                last_updated=last_updated,
                merge_stats=merge_stats
            )
        )

    except Exception as e:
        logger.error(f"Error during Vista realtime refresh for medications: {e}", exc_info=True)
        # Return error state
        return templates.TemplateResponse(
            "partials/medications_refresh_area.html",
            get_base_context(
                request,
                patient={"icn": icn, "name_display": "Unknown Patient"},
                medications=[],
                counts={},
                error=f"VistA refresh failed: {str(e)}",
                active_page="medications"
            )
        )
