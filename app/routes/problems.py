# ---------------------------------------------------------------------
# app/routes/problems.py
# ---------------------------------------------------------------------
# Problems/Diagnoses API Routes and Pages
# Handles all patient problems API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.db.patient_problems import (
    get_patient_problems,
    get_problems_summary,
    get_problems_grouped_by_category,
    get_charlson_score,
    has_chronic_condition,
    get_chronic_conditions_summary
)
from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context
from app.utils.ccow_client import ccow_client

# API router for problems endpoints
router = APIRouter(prefix="/api/patient", tags=["problems"])

# Page router for full problems pages (no prefix for flexibility)
page_router = APIRouter(tags=["problems-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/{icn}/problems")
async def get_patient_problems_endpoint(
    icn: str,
    status: Optional[str] = Query(None, description="Filter by status (Active, Inactive, Resolved)"),
    category: Optional[str] = Query(None, description="Filter by ICD-10 category"),
    service_connected_only: bool = Query(False, description="Only service-connected problems")
):
    """
    Get all problems for a patient with optional filtering.

    Args:
        icn: Integrated Care Number
        status: Optional filter by status (Active, Inactive, Resolved)
        category: Optional filter by ICD-10 category
        service_connected_only: If True, only return service-connected problems

    Returns:
        JSON with list of patient problems
    """
    try:
        problems = get_patient_problems(
            icn,
            status=status,
            category=category,
            service_connected_only=service_connected_only
        )

        return {
            "patient_icn": icn,
            "count": len(problems),
            "filters": {
                "status": status,
                "category": category,
                "service_connected_only": service_connected_only
            },
            "problems": problems
        }

    except Exception as e:
        logger.error(f"Error fetching problems for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/problems/summary")
async def get_problems_summary_endpoint(
    icn: str,
    limit: int = Query(8, ge=1, le=50)
):
    """
    Get problems summary for dashboard widget.
    Returns top N active problems plus aggregate statistics.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of problems to return (default 8)

    Returns:
        JSON with problems list and summary statistics
    """
    try:
        summary = get_problems_summary(icn, limit=limit)

        return {
            "patient_icn": icn,
            **summary
        }

    except Exception as e:
        logger.error(f"Error fetching problems summary for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/problems/grouped")
async def get_problems_grouped_endpoint(
    icn: str,
    status: str = Query("Active", description="Filter by status (default Active)")
):
    """
    Get problems grouped by ICD-10 category.
    Used for organized display in full page view.

    Args:
        icn: Integrated Care Number
        status: Filter by status (default "Active")

    Returns:
        JSON with problems grouped by category
    """
    try:
        grouped = get_problems_grouped_by_category(icn, status=status)

        return {
            "patient_icn": icn,
            "status": status,
            "categories": list(grouped.keys()),
            "category_count": len(grouped),
            "grouped_problems": grouped
        }

    except Exception as e:
        logger.error(f"Error fetching grouped problems for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/problems/charlson")
async def get_charlson_score_endpoint(icn: str):
    """
    Get Charlson Comorbidity Index score for a patient.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with Charlson score and risk level
    """
    try:
        score = get_charlson_score(icn)

        # Determine risk level based on score
        if score == 0:
            risk_level = "None"
        elif score <= 2:
            risk_level = "Low"
        elif score <= 4:
            risk_level = "Moderate"
        elif score <= 6:
            risk_level = "High"
        else:
            risk_level = "Very High"

        return {
            "patient_icn": icn,
            "charlson_index": score,
            "risk_level": risk_level
        }

    except Exception as e:
        logger.error(f"Error fetching Charlson score for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/problems/conditions")
async def get_chronic_conditions_endpoint(icn: str):
    """
    Get chronic conditions summary for a patient.
    Returns boolean flags for 15 tracked chronic conditions.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with chronic condition flags
    """
    try:
        conditions = get_chronic_conditions_summary(icn)

        return {
            "patient_icn": icn,
            "conditions": conditions,
            "count": sum(1 for v in conditions.values() if v)
        }

    except Exception as e:
        logger.error(f"Error fetching chronic conditions for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widget/problems/{icn}", response_class=HTMLResponse)
async def get_problems_widget(request: Request, icn: str):
    """
    Render problems widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing top active problems with Charlson score.

    Widget shows:
    - Charlson Comorbidity Index badge (color-coded by risk)
    - Top 8 active problems (Charlson conditions prioritized)
    - Critical condition indicators (CHF, COPD, CKD, diabetes)
    - Summary counts (total active, chronic conditions)

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for problems widget
    """
    try:
        # Get problems summary (top 8 active + stats)
        summary = get_problems_summary(icn, limit=8)

        # Determine Charlson risk level and badge color
        charlson_score = summary.get("charlson_index", 0)
        if charlson_score == 0:
            risk_level = "None"
            badge_class = "badge--success"
        elif charlson_score <= 2:
            risk_level = "Low"
            badge_class = "badge--success"
        elif charlson_score <= 4:
            risk_level = "Moderate"
            badge_class = "badge--warning"
        elif charlson_score <= 6:
            risk_level = "High"
            badge_class = "badge--warning"
        else:
            risk_level = "Very High"
            badge_class = "badge--danger"

        return templates.TemplateResponse(
            "partials/problems_widget.html",
            {
                "request": request,
                "icn": icn,
                "problems": summary.get("problems", []),
                "total_active": summary.get("total_active", 0),
                "total_chronic": summary.get("total_chronic", 0),
                "charlson_score": charlson_score,
                "risk_level": risk_level,
                "badge_class": badge_class,
                "has_chf": summary.get("has_chf", False),
                "has_copd": summary.get("has_copd", False),
                "has_ckd": summary.get("has_ckd", False),
                "has_diabetes": summary.get("has_diabetes", False),
                "has_critical_conditions": summary.get("has_critical_conditions", False),
                "has_problems": len(summary.get("problems", [])) > 0
            }
        )

    except Exception as e:
        logger.error(f"Error rendering problems widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/problems_widget.html",
            {
                "request": request,
                "icn": icn,
                "problems": [],
                "total_active": 0,
                "total_chronic": 0,
                "charlson_score": 0,
                "risk_level": "Unknown",
                "badge_class": "badge--secondary",
                "has_chf": False,
                "has_copd": False,
                "has_ckd": False,
                "has_diabetes": False,
                "has_critical_conditions": False,
                "has_problems": False,
                "error": str(e)
            }
        )


@router.get("/{icn}/problems/{problem_id}/detail", response_class=HTMLResponse)
async def get_problem_detail(request: Request, icn: str, problem_id: int):
    """
    Get problem detail modal content.
    Returns HTML partial for HTMX modal display.

    Args:
        icn: Patient ICN
        problem_id: Problem ID (primary key)

    Returns:
        HTML partial with detailed problem information
    """
    try:
        # Get all problems for patient and find the specific one
        problems = get_patient_problems(icn)
        problem = next((p for p in problems if p.get("problem_id") == problem_id), None)

        if not problem:
            return templates.TemplateResponse(
                "partials/problem_detail_content.html",
                {
                    "request": request,
                    "problem": None,
                    "error": f"Problem {problem_id} not found for patient {icn}"
                }
            )

        return templates.TemplateResponse(
            "partials/problem_detail_content.html",
            {
                "request": request,
                "problem": problem,
                "error": None
            }
        )

    except Exception as e:
        logger.error(f"Error fetching problem detail {problem_id} for {icn}: {e}")
        return templates.TemplateResponse(
            "partials/problem_detail_content.html",
            {
                "request": request,
                "problem": None,
                "error": str(e)
            }
        )


# ============================================
# Full Page Routes
# ============================================

@page_router.get("/problems")
async def problems_redirect(request: Request):
    """
    Redirect to current patient's problems page.
    Gets patient from CCOW and redirects to /patient/{icn}/problems.
    If no patient selected, redirects to dashboard.
    """
    try:
        # Get active patient from CCOW
        patient_id = ccow_client.get_active_patient(request)

        if not patient_id:
            logger.warning("No active patient in CCOW, redirecting to dashboard")
            return RedirectResponse(url="/", status_code=303)

        # Redirect to patient-specific problems page
        return RedirectResponse(url=f"/patient/{patient_id}/problems", status_code=303)

    except Exception as e:
        logger.error(f"Error redirecting to problems page: {e}")
        return RedirectResponse(url="/", status_code=303)


@page_router.get("/patient/{icn}/problems", response_class=HTMLResponse)
async def patient_problems_page(
    request: Request,
    icn: str,
    status: Optional[str] = Query("Active", description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    service_connected_only: bool = Query(False, description="Service-connected only")
):
    """
    Render full patient problems page with filtering.

    Shows:
    - Problems grouped by ICD-10 category (collapsible sections)
    - Charlson Comorbidity Index summary
    - Chronic conditions indicators
    - Filters for status, category, service-connected
    - "Refresh VistA" button for real-time overlay

    Args:
        icn: Integrated Care Number
        status: Filter by status (Active, Inactive, Resolved, or All)
        category: Optional filter by ICD-10 category
        service_connected_only: If True, show only service-connected problems

    Returns:
        Full HTML page with problems display
    """
    try:
        # Get patient demographics
        patient = get_patient_demographics(icn)

        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {icn} not found")

        # Get all problems from PostgreSQL (no filters yet - need all for potential merge)
        all_problems = get_patient_problems(icn, status=None, category=None, service_connected_only=False)

        # Check if we have cached Vista responses to merge with PG data
        from app.services.vista_cache import VistaSessionCache
        from app.services.realtime_overlay import merge_problems_data

        problems_cache = VistaSessionCache.get_cached_data(request, icn, "problems")

        if problems_cache and "vista_responses" in problems_cache:
            # Merge PG data with cached Vista responses
            logger.info(f"Merging PG data with cached Vista responses from sites: {problems_cache.get('sites')}")
            all_problems, merge_stats = merge_problems_data(all_problems, problems_cache["vista_responses"], icn)
            logger.info(f"Merged: {merge_stats['total_merged']} problems ({merge_stats['pg_count']} PG + {merge_stats['vista_count']} Vista)")
        else:
            logger.debug(f"No cached Vista data for {icn}/problems - using PostgreSQL only")

        # Apply filters AFTER merge
        filtered_problems = all_problems

        # Apply status filter
        if status and status != "All":
            filtered_problems = [p for p in filtered_problems if p.get("problem_status") == status]

        # Apply category filter
        if category:
            filtered_problems = [p for p in filtered_problems if p.get("icd10_category") == category]

        # Apply service-connected filter
        if service_connected_only:
            filtered_problems = [p for p in filtered_problems if p.get("service_connected")]

        # Group by category
        grouped = {}
        for p in filtered_problems:
            cat = p.get("icd10_category") or "Other"
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(p)

        # Calculate summary statistics from merged data (not just PostgreSQL)
        # Use all_problems (merged) for accurate stats, not filtered_problems
        total_active = sum(1 for p in all_problems if p.get("problem_status") == "Active")
        total_chronic = sum(1 for p in all_problems if p.get("is_chronic"))

        # Calculate Charlson score from merged data
        charlson_score = sum(p.get("charlson_weight", 0) for p in all_problems if p.get("charlson_condition"))

        # Determine risk level from Charlson score
        if charlson_score == 0:
            risk_level = "None"
            badge_class = "badge--success"
        elif charlson_score <= 2:
            risk_level = "Low"
            badge_class = "badge--success"
        elif charlson_score <= 4:
            risk_level = "Moderate"
            badge_class = "badge--warning"
        elif charlson_score <= 6:
            risk_level = "High"
            badge_class = "badge--warning"
        else:
            risk_level = "Very High"
            badge_class = "badge--danger"

        # Calculate chronic condition flags from merged data
        has_chf = any("CHF" in (p.get("problem_text") or "") or "heart failure" in (p.get("problem_text") or "").lower() for p in all_problems if p.get("problem_status") == "Active")
        has_copd = any("COPD" in (p.get("problem_text") or "") or p.get("icd10_code", "").startswith("J44") for p in all_problems if p.get("problem_status") == "Active")
        has_ckd = any("CKD" in (p.get("problem_text") or "") or "chronic kidney" in (p.get("problem_text") or "").lower() for p in all_problems if p.get("problem_status") == "Active")
        has_diabetes = any("diabetes" in (p.get("problem_text") or "").lower() or p.get("icd10_code", "").startswith(("E10", "E11")) for p in all_problems if p.get("problem_status") == "Active")
        has_critical_conditions = has_chf or has_copd or has_ckd or has_diabetes

        # Get all unique categories for filter dropdown (from merged data)
        all_categories = sorted(set(p.get("icd10_category") or "Other" for p in all_problems))

        # Calculate data freshness based on VistA cache presence
        from datetime import datetime, timedelta
        if problems_cache:
            # We have Vista data - current through today
            now = datetime.now()
            data_current_through = now.strftime("%b %d, %Y")
            data_freshness_label = "today"
        else:
            # PostgreSQL only - current through yesterday
            yesterday = datetime.now() - timedelta(days=1)
            data_current_through = yesterday.strftime("%b %d, %Y")
            data_freshness_label = "yesterday"

        vista_cached = problems_cache is not None
        cache_sites = problems_cache.get("sites", []) if problems_cache else []

        # Build context
        context = get_base_context(request)
        context.update({
            "patient": patient,
            "icn": icn,
            "grouped_problems": grouped,
            "category_count": len(grouped),
            "total_problems": sum(len(probs) for probs in grouped.values()),
            "charlson_score": charlson_score,
            "risk_level": risk_level,
            "badge_class": badge_class,
            "total_active": total_active,
            "total_chronic": total_chronic,
            "has_chf": has_chf,
            "has_copd": has_copd,
            "has_ckd": has_ckd,
            "has_diabetes": has_diabetes,
            "has_critical_conditions": has_critical_conditions,
            # Filters
            "status_filter": status or "Active",
            "category_filter": category,
            "service_connected_filter": service_connected_only,
            "all_categories": all_categories,
            # VistA cache metadata
            "data_current_through": data_current_through,
            "data_freshness_label": data_freshness_label,
            "vista_refreshed": False,  # Only True after "Refresh VistA" button click
            "vista_cached": vista_cached,
            "cache_sites": cache_sites,
        })

        return templates.TemplateResponse(
            "patient_problems.html",
            context
        )

    except Exception as e:
        logger.error(f"Error rendering problems page for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@page_router.get("/patient/{icn}/problems/realtime", response_class=HTMLResponse)
async def get_problems_realtime(
    request: Request,
    icn: str,
    status: Optional[str] = Query("Active", description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    service_connected_only: bool = Query(False, description="Service-connected only")
):
    """
    VistA real-time refresh endpoint for problems.

    Fetches today's problems from VistA sites and merges with historical PostgreSQL data.
    Returns only the page content div (for HTMX swap).

    Args:
        icn: Patient ICN
        status: Filter by status (Active, Inactive, Resolved, or All)
        category: Optional filter by ICD-10 category
        service_connected_only: If True, show only service-connected problems

    Returns:
        HTML partial containing problems content (filters + grouped problems)
    """
    try:
        from datetime import datetime
        logger.info(f"VistA realtime refresh requested for problems - {icn}")

        # Get patient demographics for page title
        patient = get_patient_demographics(icn)
        if not patient:
            logger.warning(f"Patient {icn} not found during realtime refresh")
            patient = {"icn": icn, "name_display": "Unknown Patient"}

        # Fetch real-time data from VistA
        from app.services.vista_client import VistaClient
        from app.services.realtime_overlay import merge_problems_data

        vista_client = VistaClient()

        # Get target sites for problems (limit per domain policy)
        target_sites = vista_client.get_target_sites(icn, domain="problems")
        logger.info(f"Querying {len(target_sites)} VistA sites for problems: {target_sites}")

        # Call ORQQPL LIST RPC at all target sites
        vista_results_raw = await vista_client.call_rpc_multi_site(
            sites=target_sites,
            rpc_name="ORQQPL LIST",
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
        pg_problems = get_patient_problems(icn, status=None)  # Get all for merge

        # Merge PostgreSQL + Vista data
        problems, merge_stats = merge_problems_data(pg_problems, vista_results, icn)

        # Cache Vista RPC responses (NOT merged data) to avoid cookie size limit
        from app.services.vista_cache import VistaSessionCache

        # Store raw Vista responses (small - just strings), not merged data
        VistaSessionCache.set_cached_data(
            request=request,
            patient_icn=icn,
            domain="problems",
            vista_responses=vista_results,  # Raw RPC response strings
            sites=list(vista_results.keys()),
            stats=merge_stats
        )

        logger.info(
            f"Merge complete: {merge_stats['total_merged']} problems "
            f"({merge_stats['pg_count']} PG + {merge_stats['vista_count']} Vista) - Vista responses cached in session"
        )

        # Apply filters AFTER merge
        filtered_problems = problems

        if status and status != "All":
            filtered_problems = [p for p in filtered_problems if p.get("problem_status") == status]

        if category:
            filtered_problems = [p for p in filtered_problems if p.get("icd10_category") == category]

        if service_connected_only:
            filtered_problems = [p for p in filtered_problems if p.get("service_connected")]

        # Group by category
        grouped = {}
        for p in filtered_problems:
            cat = p.get("icd10_category") or "Other"
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(p)

        # Calculate summary statistics from merged data (not just PostgreSQL)
        total_active = sum(1 for p in problems if p.get("problem_status") == "Active")
        total_chronic = sum(1 for p in problems if p.get("is_chronic"))
        has_chf = any("CHF" in (p.get("problem_text") or "") or "heart failure" in (p.get("problem_text") or "").lower() for p in problems if p.get("problem_status") == "Active")
        has_copd = any("COPD" in (p.get("problem_text") or "") or p.get("icd10_code", "").startswith("J44") for p in problems if p.get("problem_status") == "Active")
        has_ckd = any("CKD" in (p.get("problem_text") or "") or "chronic kidney" in (p.get("problem_text") or "").lower() for p in problems if p.get("problem_status") == "Active")
        has_diabetes = any("diabetes" in (p.get("problem_text") or "").lower() or p.get("icd10_code", "").startswith(("E10", "E11")) for p in problems if p.get("problem_status") == "Active")
        has_critical_conditions = has_chf or has_copd or has_ckd or has_diabetes

        # Calculate Charlson score from merged data
        charlson_score = sum(p.get("charlson_weight", 0) for p in problems if p.get("charlson_condition"))

        # Determine risk level
        if charlson_score == 0:
            risk_level = "None"
            badge_class = "badge--success"
        elif charlson_score <= 2:
            risk_level = "Low"
            badge_class = "badge--success"
        elif charlson_score <= 4:
            risk_level = "Moderate"
            badge_class = "badge--warning"
        elif charlson_score <= 6:
            risk_level = "High"
            badge_class = "badge--warning"
        else:
            risk_level = "Very High"
            badge_class = "badge--danger"

        # Get all unique categories for filter dropdown
        all_categories = sorted(set(p.get("icd10_category") or "Other" for p in problems))

        # Calculate data freshness (today's date after VistA refresh)
        now = datetime.now()
        data_current_through = now.strftime("%b %d, %Y")
        last_updated = now.strftime("%I:%M %p")

        # Calculate Vista success rate
        successful_sites = len(vista_results)
        total_sites_attempted = len(target_sites)
        vista_success_rate = f"{successful_sites} of {total_sites_attempted} sites" if total_sites_attempted > 0 else "no sites"

        logger.info(
            f"VistA refresh complete for problems {icn}: {len(problems)} problems "
            f"({vista_success_rate} successful)"
        )

        # Return only the content portion (for HTMX outerHTML swap)
        return templates.TemplateResponse(
            "partials/problems_refresh_area.html",
            {
                "request": request,
                "patient": patient,
                "icn": icn,
                "grouped_problems": grouped,
                "category_count": len(grouped),
                "total_problems": sum(len(probs) for probs in grouped.values()),
                "charlson_score": charlson_score,
                "risk_level": risk_level,
                "badge_class": badge_class,
                "total_active": total_active,
                "total_chronic": total_chronic,
                "has_chf": has_chf,
                "has_copd": has_copd,
                "has_ckd": has_ckd,
                "has_diabetes": has_diabetes,
                "has_critical_conditions": has_critical_conditions,
                # Filters
                "status_filter": status or "Active",
                "category_filter": category,
                "service_connected_filter": service_connected_only,
                "all_categories": all_categories,
                # Vista metadata
                "vista_refreshed": True,
                "vista_cached": True,  # Just cached the data!
                "cache_sites": list(vista_results.keys()),  # Sites we cached from
                "data_current_through": data_current_through,
                "last_updated": last_updated,
                "vista_success_rate": vista_success_rate,
                "vista_sites": target_sites,
                "merge_stats": merge_stats,
            }
        )

    except Exception as e:
        logger.error(f"Error during VistA refresh for problems {icn}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
