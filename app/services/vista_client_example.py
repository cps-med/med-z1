# ---------------------------------------------------------------------
# app/services/vista_client_example.py
# ---------------------------------------------------------------------
# Example Usage of VistaClient for Real-Time Data Integration
# Demonstrates how to integrate Vista RPC Broker into FastAPI routes
# ---------------------------------------------------------------------

"""
Example patterns for using VistaClient to fetch real-time data (T-0)
from Vista RPC Broker and merge with PostgreSQL historical data (T-1+).

This file is for reference only - not imported by the application.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from app.services.vista_client import get_vista_client

router = APIRouter()


# ---------------------------------------------------------------------
# Example 1: Basic Single-Domain Query
# ---------------------------------------------------------------------

async def get_vitals_realtime_basic(icn: str) -> Dict[str, Any]:
    """
    Example: Fetch vitals from Vista using automatic site selection.

    This is the simplest pattern - let VistaClient automatically
    select sites based on domain-specific limits.
    """
    vista_client = get_vista_client()

    # Get target sites for vitals domain (defaults to 2 sites)
    sites = vista_client.get_target_sites(icn, domain="vitals")

    if not sites:
        return {
            "success": False,
            "error": "No treating facilities found for patient"
        }

    # Call ORWPT VITALS RPC at all selected sites in parallel
    results = await vista_client.call_rpc_multi_site(
        sites=sites,
        rpc_name="ORWPT VITALS",
        params=[icn]
    )

    return {
        "success": True,
        "sites_queried": sites,
        "results": results
    }


# ---------------------------------------------------------------------
# Example 2: Domain-Specific Site Selection
# ---------------------------------------------------------------------

async def get_allergies_realtime_demo(icn: str) -> Dict[str, Any]:
    """
    Example: Fetch allergies using domain-specific site limit.

    Allergies domain queries up to 5 sites (safety-critical data).
    """
    vista_client = get_vista_client()

    # Allergies domain automatically uses 5-site limit
    sites = vista_client.get_target_sites(icn, domain="allergies")

    results = await vista_client.call_rpc_multi_site(
        sites=sites,
        rpc_name="ORWPT ALLERGY",
        params=[icn]
    )

    # Extract successful responses
    successful_results = []
    for site, result in results.items():
        if result.get("success"):
            successful_results.append({
                "site": site,
                "data": result.get("response")
            })

    return {
        "success": True,
        "sites_queried": len(sites),
        "sites_succeeded": len(successful_results),
        "allergies": successful_results
    }


# ---------------------------------------------------------------------
# Example 3: User-Controlled Site Selection (UI Override)
# ---------------------------------------------------------------------

async def get_vitals_user_selected_sites(
    icn: str,
    user_selected_sites: List[str]
) -> Dict[str, Any]:
    """
    Example: Allow user to explicitly select sites from UI.

    Use case: "More sites..." button that lets clinician choose
    which facilities to query.
    """
    vista_client = get_vista_client()

    # User selection overrides automatic selection (up to 10 sites max)
    sites = vista_client.get_target_sites(
        icn=icn,
        domain="vitals",
        user_selected_sites=user_selected_sites
    )

    results = await vista_client.call_rpc_multi_site(
        sites=sites,
        rpc_name="ORWPT VITALS",
        params=[icn]
    )

    return {
        "success": True,
        "user_selected": True,
        "sites_queried": sites,
        "results": results
    }


# ---------------------------------------------------------------------
# Example 4: Merge PostgreSQL (T-1+) + Vista (T-0) Data
# ---------------------------------------------------------------------

async def get_vitals_merged(icn: str, db_session) -> Dict[str, Any]:
    """
    Example: Merge historical data from PostgreSQL with real-time Vista data.

    This is the full pattern for displaying complete patient data:
    1. Query PostgreSQL for historical data (T-1 and earlier)
    2. Query Vista for today's data (T-0)
    3. Merge results, deduplicating by canonical event key
    4. Sort combined results chronologically
    """
    vista_client = get_vista_client()

    # Step 1: Get historical vitals from PostgreSQL (T-1 and earlier)
    # (Assume we have a function to query the serving database)
    historical_vitals = await get_vitals_from_postgres(icn, db_session)

    # Step 2: Get today's vitals from Vista (T-0)
    sites = vista_client.get_target_sites(icn, domain="vitals")
    vista_results = await vista_client.call_rpc_multi_site(
        sites=sites,
        rpc_name="ORWPT VITALS",
        params=[icn]
    )

    # Step 3: Parse Vista results and merge with historical data
    merged_vitals = historical_vitals.copy()

    for site, result in vista_results.items():
        if result.get("success"):
            vista_vitals = parse_vista_vitals_response(
                result.get("response"),
                site=site
            )
            merged_vitals.extend(vista_vitals)

    # Step 4: Deduplicate by canonical event key
    # Format: "{site}:{datetime}:{vital_type}"
    seen_keys = set()
    deduplicated_vitals = []

    for vital in merged_vitals:
        key = f"{vital['site']}:{vital['datetime']}:{vital['type']}"
        if key not in seen_keys:
            seen_keys.add(key)
            deduplicated_vitals.append(vital)

    # Step 5: Sort chronologically (most recent first)
    deduplicated_vitals.sort(key=lambda v: v['datetime'], reverse=True)

    return {
        "success": True,
        "total_count": len(deduplicated_vitals),
        "historical_count": len(historical_vitals),
        "realtime_count": len(merged_vitals) - len(historical_vitals),
        "vitals": deduplicated_vitals
    }


# ---------------------------------------------------------------------
# Example 5: Error Handling and Partial Results
# ---------------------------------------------------------------------

async def get_medications_with_error_handling(icn: str) -> Dict[str, Any]:
    """
    Example: Proper error handling for multi-site queries.

    Some sites may fail or timeout - always handle partial results.
    """
    vista_client = get_vista_client()

    # Medications domain uses 3-site limit
    sites = vista_client.get_target_sites(icn, domain="medications")

    if not sites:
        raise HTTPException(
            status_code=404,
            detail="No treating facilities found for patient"
        )

    try:
        results = await vista_client.call_rpc_multi_site(
            sites=sites,
            rpc_name="ORWPT MEDS",
            params=[icn]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vista RPC call failed: {str(e)}"
        )

    # Separate successful and failed results
    successful = []
    failed = []

    for site, result in results.items():
        if result.get("success"):
            successful.append({
                "site": site,
                "data": result.get("response")
            })
        else:
            failed.append({
                "site": site,
                "error": result.get("error", "Unknown error")
            })

    # Return partial results with warnings
    return {
        "success": len(successful) > 0,  # Success if ANY site responded
        "sites_queried": len(sites),
        "sites_succeeded": len(successful),
        "sites_failed": len(failed),
        "medications": successful,
        "errors": failed if failed else None,
        "warning": f"{len(failed)} of {len(sites)} sites failed" if failed else None
    }


# ---------------------------------------------------------------------
# Example 6: Override Site Limit for "More Sites..." Feature
# ---------------------------------------------------------------------

async def get_labs_with_override(
    icn: str,
    max_sites: int = None
) -> Dict[str, Any]:
    """
    Example: Allow UI to override default site limit.

    Use case: User clicks "More sites..." button to expand search.
    Default: 3 sites (labs domain)
    Override: Up to 10 sites (hard maximum)
    """
    vista_client = get_vista_client()

    # If max_sites provided, override domain default
    # Hard maximum of 10 sites is still enforced
    sites = vista_client.get_target_sites(
        icn=icn,
        domain="labs",
        max_sites=max_sites  # None uses default (3), or override up to 10
    )

    results = await vista_client.call_rpc_multi_site(
        sites=sites,
        rpc_name="ORWPT LAB",
        params=[icn]
    )

    return {
        "success": True,
        "using_default_limit": max_sites is None,
        "sites_queried": len(sites),
        "results": results
    }


# ---------------------------------------------------------------------
# Example 7: Single-Site Query (Demographics)
# ---------------------------------------------------------------------

async def get_demographics_realtime(icn: str) -> Dict[str, Any]:
    """
    Example: Demographics queries only most recent site (limit=1).

    Demographics typically don't change, so we only query the
    site where the patient was seen most recently.
    """
    vista_client = get_vista_client()

    # Demographics domain automatically uses 1-site limit
    sites = vista_client.get_target_sites(icn, domain="demographics")

    if not sites:
        raise HTTPException(
            status_code=404,
            detail="No treating facilities found for patient"
        )

    # Single site - use call_rpc instead of call_rpc_multi_site
    result = await vista_client.call_rpc(
        site=sites[0],
        rpc_name="ORWPT PTINQ",
        params=[icn]
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"Vista RPC failed: {result.get('error')}"
        )

    return {
        "success": True,
        "site": sites[0],
        "demographics": parse_patient_inquiry_response(result.get("response"))
    }


# ---------------------------------------------------------------------
# Helper Functions (would be in separate module)
# ---------------------------------------------------------------------

async def get_vitals_from_postgres(icn: str, db_session) -> List[Dict[str, Any]]:
    """Mock function - would query PostgreSQL serving database"""
    # In real implementation:
    # SELECT * FROM patient_vitals WHERE icn = :icn AND date < CURRENT_DATE
    return []


def parse_vista_vitals_response(
    vista_response: str,
    site: str
) -> List[Dict[str, Any]]:
    """Mock function - would parse VistA-formatted response"""
    # In real implementation: parse Vista caret-delimited format
    return []


def parse_patient_inquiry_response(vista_response: str) -> Dict[str, Any]:
    """Mock function - would parse ORWPT PTINQ response"""
    # Format: NAME^SSN^DOB^SEX^VETERAN_STATUS
    fields = vista_response.split("^")
    return {
        "name": fields[0] if len(fields) > 0 else None,
        "ssn": fields[1] if len(fields) > 1 else None,
        "dob": fields[2] if len(fields) > 2 else None,
        "sex": fields[3] if len(fields) > 3 else None,
        "veteran_status": fields[4] if len(fields) > 4 else None
    }


# ---------------------------------------------------------------------
# FastAPI Route Example
# ---------------------------------------------------------------------

@router.get("/patient/{icn}/vitals-realtime")
async def vitals_realtime_endpoint(icn: str):
    """
    Example FastAPI route using VistaClient.

    This would be added to app/routes/patient.py or app/routes/vitals.py
    """
    try:
        result = await get_vitals_realtime_basic(icn)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch realtime vitals: {str(e)}"
        )


# ---------------------------------------------------------------------
# Summary of Domain-Specific Site Limits
# ---------------------------------------------------------------------

"""
Domain-Specific Site Limits (from DOMAIN_SITE_LIMITS):

- vitals: 2 sites (freshest data, typically recent care)
- allergies: 5 sites (safety-critical, small payload, wider search)
- medications: 3 sites (balance freshness + comprehensiveness)
- demographics: 1 site (typically unchanged, query most recent only)
- labs: 3 sites (recent results most relevant)
- default: 3 sites (conservative default for new domains)

Hard Maximum: 10 sites (architectural firebreak - prevents fan-out to all 140+ VA facilities)

Site Selection Algorithm:
1. Get patient's treating facilities from patient_registry.json
2. Sort by last_seen descending (most recent first)
3. Apply domain-specific limit
4. Enforce hard maximum of 10 sites
5. Return top N sites by recency
"""
