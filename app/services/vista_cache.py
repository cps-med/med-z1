# ---------------------------------------------------------------------
# app/services/vista_cache.py
# ---------------------------------------------------------------------
# Session-Based Vista Data Cache
# Stores Vista RPC data fetched during user session for reuse across pages.
# Enables "Refresh from Vista" data to persist across navigation and be
# available to Dashboard, Clinical Domain pages, and AI Clinical Insights.
# ---------------------------------------------------------------------

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import Request

logger = logging.getLogger(__name__)

# Vista cache TTL (Time To Live) - data expires after this many minutes
CACHE_TTL_MINUTES = 30


class VistaSessionCache:
    """
    Manages Vista data caching in user sessions.

    Purpose:
    - When user clicks "Refresh from Vista" on any clinical domain page,
      the fetched Vista data is stored in their session
    - This cached data persists across page navigation, refreshes, and is
      available to all parts of the application (Dashboard, Clinical pages, AI)
    - Cache expires after CACHE_TTL_MINUTES or when session ends

    Cache Structure (stored in request.session):
    {
        "vista_cache": {
            "ICN100001": {                      # Patient ICN
                "vitals": {
                    "vista_responses": {        # Raw Vista RPC responses (SMALL - just strings)
                        "200": "BP^120/80...",  # Response from site 200
                        "500": "BP^118/78..."   # Response from site 500
                    },
                    "timestamp": "2025-12-30T08:30:00",
                    "sites": ["200", "500"],    # Vista sites queried
                    "stats": {                  # Merge statistics
                        "pg_count": 45,
                        "vista_count": 12,
                        "total_merged": 57
                    }
                },
                "allergies": { ... },
                "demographics": { ... }
            }
        }
    }

    IMPORTANT: We store raw Vista RPC responses (not merged data) to avoid
    exceeding the 4096-byte cookie size limit. Merged data is reconstructed
    on-demand by fetching PG data + cached Vista responses.

    Usage Example:
        # In route handler (after "Refresh from Vista" button click)
        VistaSessionCache.set_cached_data(
            request=request,
            patient_icn="ICN100001",
            domain="vitals",
            merged_data=merged_vitals,
            sites=["200", "500"],
            stats=merge_stats
        )

        # Later, in any route or service (AI tools, Dashboard, etc.)
        cached = VistaSessionCache.get_cached_data(request, "ICN100001", "vitals")
        if cached:
            vitals_data = cached["data"]  # Use cached data (no Vista refetch)
        else:
            vitals_data = query_postgresql()  # Fallback to PostgreSQL only
    """

    @staticmethod
    def get_cached_data(
        request: Request,
        patient_icn: str,
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached Vista data for patient/domain.

        Args:
            request: FastAPI request object (contains session)
            patient_icn: Patient Integrated Care Number
            domain: Clinical domain (vitals, allergies, demographics, encounters, medications)

        Returns:
            Dict with cached data structure:
            {
                "data": [...],           # Merged data
                "timestamp": "...",      # When cached
                "sites": [...],          # Vista sites queried
                "stats": {...}           # Merge statistics
            }
            Returns None if:
            - No cached data exists for this patient/domain
            - Cached data has expired (older than CACHE_TTL_MINUTES)
        """
        # Get Vista cache from session
        vista_cache = request.session.get("vista_cache", {})
        patient_cache = vista_cache.get(patient_icn, {})
        domain_cache = patient_cache.get(domain)

        if not domain_cache:
            logger.debug(f"No cached Vista data for {patient_icn}/{domain}")
            return None

        # Check if cache has expired
        timestamp_str = domain_cache.get("timestamp")
        if timestamp_str:
            try:
                cached_time = datetime.fromisoformat(timestamp_str)
                age_minutes = (datetime.now() - cached_time).total_seconds() / 60

                if age_minutes > CACHE_TTL_MINUTES:
                    logger.info(
                        f"Vista cache EXPIRED for {patient_icn}/{domain} "
                        f"(age: {age_minutes:.1f} min, TTL: {CACHE_TTL_MINUTES} min)"
                    )
                    return None

                logger.info(
                    f"Using cached Vista data for {patient_icn}/{domain} "
                    f"(age: {age_minutes:.1f} min, sites: {domain_cache.get('sites')})"
                )
                return domain_cache

            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid cache timestamp format: {e}")
                return None

        return domain_cache

    @staticmethod
    def set_cached_data(
        request: Request,
        patient_icn: str,
        domain: str,
        vista_responses: Dict[str, str],
        sites: List[str],
        stats: Dict[str, Any]
    ) -> None:
        """
        Store Vista RPC responses in session cache.

        IMPORTANT: We store only the raw Vista RPC response strings (not the full
        merged dataset) to avoid exceeding the 4096-byte cookie size limit.
        The merged data can be reconstructed on-demand by calling the merge
        function with PG data + cached Vista responses.

        This is called after "Refresh from Vista" fetches data from Vista sites.
        The cached responses will be available across all pages for this session.

        Args:
            request: FastAPI request object
            patient_icn: Patient ICN
            domain: Clinical domain
            vista_responses: Dict of site_id -> raw RPC response string (e.g., {"200": "BP^120/80..."})
            sites: List of Vista sites that were queried (e.g., ["200", "500"])
            stats: Merge statistics dict (pg_count, vista_count, total_merged, etc.)
        """
        # Initialize cache structure if not present
        if "vista_cache" not in request.session:
            request.session["vista_cache"] = {}

        vista_cache = request.session["vista_cache"]

        if patient_icn not in vista_cache:
            vista_cache[patient_icn] = {}

        # Store Vista responses (NOT merged data) to keep cookie small
        vista_cache[patient_icn][domain] = {
            "vista_responses": vista_responses,  # Raw RPC responses (small)
            "timestamp": datetime.now().isoformat(),
            "sites": sites,
            "stats": stats
        }

        # Trigger session update (important for session middleware to persist)
        request.session["vista_cache"] = vista_cache

        # Calculate approximate cache size for logging
        total_response_size = sum(len(resp) for resp in vista_responses.values())

        logger.info(
            f"✓ Cached Vista responses for {patient_icn}/{domain}: "
            f"{len(sites)} sites, ~{total_response_size} bytes "
            f"(Vista: {stats.get('vista_count', 0)} records)"
        )

    @staticmethod
    def clear_patient_cache(request: Request, patient_icn: str) -> None:
        """
        Clear all cached Vista data for a specific patient.

        Use when:
        - User switches to different patient
        - Explicit "Clear Cache" action
        - Patient data is known to be stale

        Args:
            request: FastAPI request object
            patient_icn: Patient ICN whose cache should be cleared
        """
        vista_cache = request.session.get("vista_cache", {})

        if patient_icn in vista_cache:
            domain_count = len(vista_cache[patient_icn])
            del vista_cache[patient_icn]
            request.session["vista_cache"] = vista_cache
            logger.info(f"Cleared Vista cache for patient {patient_icn} ({domain_count} domains)")
        else:
            logger.debug(f"No Vista cache to clear for patient {patient_icn}")

    @staticmethod
    def clear_domain_cache(
        request: Request,
        patient_icn: str,
        domain: str
    ) -> None:
        """
        Clear cached Vista data for specific patient/domain combination.

        Use when:
        - User explicitly re-fetches Vista data for a domain
        - Domain-specific data needs refresh

        Args:
            request: FastAPI request object
            patient_icn: Patient ICN
            domain: Clinical domain to clear
        """
        vista_cache = request.session.get("vista_cache", {})
        patient_cache = vista_cache.get(patient_icn, {})

        if domain in patient_cache:
            del patient_cache[domain]
            vista_cache[patient_icn] = patient_cache
            request.session["vista_cache"] = vista_cache
            logger.info(f"Cleared Vista cache for {patient_icn}/{domain}")
        else:
            logger.debug(f"No Vista cache to clear for {patient_icn}/{domain}")

    @staticmethod
    def clear_all_cache(request: Request) -> None:
        """
        Clear entire Vista cache for the session.

        Use when:
        - User logs out
        - Session reset requested
        - Testing/debugging

        Args:
            request: FastAPI request object
        """
        if "vista_cache" in request.session:
            cache_size = sum(
                len(domains)
                for domains in request.session["vista_cache"].values()
            )
            del request.session["vista_cache"]
            logger.info(f"Cleared entire Vista cache ({cache_size} domain caches)")
        else:
            logger.debug("No Vista cache to clear")

    @staticmethod
    def get_cache_info(request: Request, patient_icn: str) -> Dict[str, Any]:
        """
        Get information about cached Vista data for a patient.

        Returns cache status for all domains, including:
        - Whether data is cached
        - Age of cached data
        - Vista sites that were queried
        - Record counts
        - Expiration status

        Args:
            request: FastAPI request object
            patient_icn: Patient ICN

        Returns:
            Dict with cache status per domain:
            {
                "vitals": {
                    "cached": True,
                    "age_minutes": 5.2,
                    "sites": ["200", "500"],
                    "record_count": 57,
                    "expired": False
                },
                "allergies": {
                    "cached": False
                },
                ...
            }
        """
        vista_cache = request.session.get("vista_cache", {})
        patient_cache = vista_cache.get(patient_icn, {})

        # Check all supported domains
        supported_domains = ["vitals", "allergies", "demographics", "encounters", "medications"]
        cache_info = {}

        for domain in supported_domains:
            domain_cache = patient_cache.get(domain)

            if domain_cache:
                timestamp_str = domain_cache.get("timestamp")

                try:
                    cached_time = datetime.fromisoformat(timestamp_str)
                    age_minutes = (datetime.now() - cached_time).total_seconds() / 60
                    is_expired = age_minutes > CACHE_TTL_MINUTES

                    cache_info[domain] = {
                        "cached": True,
                        "age_minutes": round(age_minutes, 1),
                        "sites": domain_cache.get("sites", []),
                        "record_count": domain_cache.get("stats", {}).get("total_merged", 0),  # Use stats, not data length
                        "expired": is_expired,
                        "stats": domain_cache.get("stats", {})
                    }

                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid timestamp in cache for {domain}: {e}")
                    cache_info[domain] = {"cached": False}
            else:
                cache_info[domain] = {"cached": False}

        return cache_info

    @staticmethod
    def has_any_cached_data(request: Request, patient_icn: str) -> bool:
        """
        Quick check if patient has any cached Vista data (any domain).

        Args:
            request: FastAPI request object
            patient_icn: Patient ICN

        Returns:
            True if any domain has non-expired cached data
        """
        cache_info = VistaSessionCache.get_cache_info(request, patient_icn)

        return any(
            info.get("cached") and not info.get("expired")
            for info in cache_info.values()
        )
