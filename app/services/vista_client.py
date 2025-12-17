# ---------------------------------------------------------------------
# app/services/vista_client.py
# ---------------------------------------------------------------------
# Vista RPC Broker HTTP Client
# Handles site selection, RPC calls, and response aggregation
# ---------------------------------------------------------------------

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import httpx

from config import VISTA_SERVICE_URL

logger = logging.getLogger(__name__)

# Per-domain site limits (Section 2.8 of Vista RPC Broker design)
DOMAIN_SITE_LIMITS = {
    "vitals": 2,        # Freshest data, typically recent care
    "allergies": 5,     # Safety-critical, small payload, wider search
    "medications": 3,   # Balance freshness + comprehensiveness
    "demographics": 1,  # Typically unchanged, query most recent site only
    "labs": 3,          # Recent results most relevant
    "default": 3,       # Conservative default for new domains
}

# Hard maximum sites per query (architectural firebreak)
MAX_SITES_ABSOLUTE = 10


class VistaClient:
    """
    HTTP client for Vista RPC Broker service.

    Handles intelligent site selection, multi-site RPC calls,
    and response aggregation.
    """

    def __init__(self, vista_base_url: str = None):
        """
        Initialize Vista client.

        Args:
            vista_base_url: Base URL for Vista service (defaults to config)
        """
        self.base_url = vista_base_url or VISTA_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

        # Load patient registry for site selection
        self.patient_registry = self._load_patient_registry()

    def _load_patient_registry(self) -> Dict[str, Any]:
        """
        Load patient registry from shared JSON file.

        Returns:
            Dictionary with patient registry data
        """
        registry_path = Path(__file__).parent.parent.parent / "mock" / "shared" / "patient_registry.json"

        try:
            with open(registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load patient registry: {e}")
            return {"patients": []}

    def _get_patient_treating_facilities(self, icn: str) -> List[Dict[str, Any]]:
        """
        Get treating facilities for a patient.

        Args:
            icn: Patient ICN

        Returns:
            List of treating facility dictionaries with sta3n, last_seen, etc.
        """
        for patient in self.patient_registry.get("patients", []):
            if patient.get("icn") == icn:
                return patient.get("treating_facilities", [])

        logger.warning(f"Patient {icn} not found in registry")
        return []

    def _parse_t_notation(self, t_notation: str) -> datetime:
        """
        Parse T-notation date (T-0, T-7, T-30, etc.) to actual date.

        Args:
            t_notation: Date in T-notation format (e.g., "T-7")

        Returns:
            Datetime object representing the date
        """
        if not t_notation or not t_notation.startswith("T-"):
            # If not T-notation, try parsing as regular date
            try:
                return datetime.fromisoformat(t_notation)
            except:
                # Default to very old date if unparseable
                return datetime(1900, 1, 1)

        try:
            days_ago = int(t_notation.split("-")[1])
            return datetime.now() - timedelta(days=days_ago)
        except (IndexError, ValueError) as e:
            logger.warning(f"Failed to parse T-notation '{t_notation}': {e}")
            return datetime(1900, 1, 1)

    def get_target_sites(
        self,
        icn: str,
        domain: str,
        max_sites: Optional[int] = None,
        user_selected_sites: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get list of sites to query for real-time data.

        Implements intelligent site selection based on:
        - Patient's treating facilities
        - Last seen dates (sorted descending - most recent first)
        - Per-domain site limits
        - Hard maximum of 10 sites

        Args:
            icn: Patient ICN
            domain: Clinical domain (vitals, allergies, medications, etc.)
            max_sites: Override default limit (for "More sites..." UI action)
            user_selected_sites: Explicit site selection from UI

        Returns:
            List of sta3n values to query, ordered by priority (most recent first)
        """
        # If user explicitly selected sites, use those (up to hard limit)
        if user_selected_sites:
            selected = user_selected_sites[:MAX_SITES_ABSOLUTE]
            logger.info(f"Using user-selected sites for {icn}/{domain}: {selected}")
            return selected

        # Get treating facilities from patient registry
        treating_facilities = self._get_patient_treating_facilities(icn)

        if not treating_facilities:
            logger.warning(f"No treating facilities found for patient {icn}")
            return []

        # Sort by last_seen descending (most recent first)
        sorted_facilities = sorted(
            treating_facilities,
            key=lambda x: self._parse_t_notation(x.get("last_seen", "T-999")),
            reverse=True
        )

        # Apply domain-specific limit
        limit = max_sites if max_sites is not None else DOMAIN_SITE_LIMITS.get(domain, DOMAIN_SITE_LIMITS["default"])

        # Ensure limit is non-negative
        limit = max(0, limit)

        # Enforce hard maximum
        limit = min(limit, MAX_SITES_ABSOLUTE)

        # Extract sta3n values
        target_sites = [fac["sta3n"] for fac in sorted_facilities[:limit]]

        logger.info(
            f"Selected {len(target_sites)} sites for {icn}/{domain}: {target_sites} "
            f"(limit={limit}, available={len(treating_facilities)})"
        )

        return target_sites

    async def call_rpc(
        self,
        site: str,
        rpc_name: str,
        params: List[Any]
    ) -> Dict[str, Any]:
        """
        Call a single RPC at a specific site.

        Args:
            site: Site station number (sta3n)
            rpc_name: RPC name (e.g., "ORWPT PTINQ")
            params: RPC parameters

        Returns:
            Dictionary with success, response, error, site, rpc
        """
        url = f"{self.base_url}/rpc/execute"

        try:
            response = await self.client.post(
                url,
                params={"site": site},
                json={
                    "name": rpc_name,
                    "params": params
                }
            )

            response.raise_for_status()
            result = response.json()

            logger.debug(f"RPC {rpc_name} at site {site}: success={result.get('success')}")
            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling RPC {rpc_name} at site {site}: {e}")
            return {
                "success": False,
                "response": None,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "site": site,
                "rpc": rpc_name
            }
        except Exception as e:
            logger.error(f"Error calling RPC {rpc_name} at site {site}: {e}")
            return {
                "success": False,
                "response": None,
                "error": str(e),
                "site": site,
                "rpc": rpc_name
            }

    async def call_rpc_multi_site(
        self,
        sites: List[str],
        rpc_name: str,
        params: List[Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Call an RPC at multiple sites in parallel.

        Args:
            sites: List of site station numbers (sta3n)
            rpc_name: RPC name (e.g., "ORWPT PTINQ")
            params: RPC parameters

        Returns:
            Dictionary mapping site -> response dict
            Example: {"200": {"success": True, ...}, "500": {...}}
        """
        import asyncio

        logger.info(f"Calling {rpc_name} at {len(sites)} sites: {sites}")

        # Create tasks for all sites
        tasks = [
            self.call_rpc(site, rpc_name, params)
            for site in sites
        ]

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dictionary
        result_dict = {}
        for site, result in zip(sites, results):
            if isinstance(result, Exception):
                logger.error(f"Exception calling {rpc_name} at site {site}: {result}")
                result_dict[site] = {
                    "success": False,
                    "response": None,
                    "error": str(result),
                    "site": site,
                    "rpc": rpc_name
                }
            else:
                result_dict[site] = result

        # Log summary
        successful = sum(1 for r in result_dict.values() if r.get("success"))
        logger.info(f"{rpc_name} completed: {successful}/{len(sites)} sites succeeded")

        return result_dict

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance for easy import
_vista_client_instance: Optional[VistaClient] = None


def get_vista_client() -> VistaClient:
    """
    Get or create singleton Vista client instance.

    Returns:
        VistaClient instance
    """
    global _vista_client_instance
    if _vista_client_instance is None:
        _vista_client_instance = VistaClient()
    return _vista_client_instance
