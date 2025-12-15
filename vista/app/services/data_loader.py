# ---------------------------------------------------------------------
# vista/app/services/data_loader.py
# ---------------------------------------------------------------------
# Patient Registry Data Loader
# Provides ICN→DFN resolution for VistA site simulation
# ---------------------------------------------------------------------

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads patient registry and provides ICN→DFN resolution for a specific VistA site.

    Each VistA site gets its own DataLoader instance that resolves ICNs to
    site-specific DFNs based on the patient_registry.json.

    Example:
        loader = DataLoader(site_sta3n="200")
        dfn = loader.resolve_icn_to_dfn("ICN100001")  # Returns "100001"
    """

    def __init__(self, site_sta3n: str, registry_path: str = None):
        """
        Initialize DataLoader for a specific VistA site.

        Args:
            site_sta3n: Station number for this VistA site (e.g., "200", "500", "630")
            registry_path: Path to patient_registry.json (defaults to mock/shared/patient_registry.json)
        """
        self.site_sta3n = site_sta3n

        # Default to mock/shared/patient_registry.json if not specified
        if registry_path is None:
            # Assume we're running from project root or vista/ directory
            # Try both locations
            project_root = Path(__file__).parent.parent.parent.parent
            registry_path = project_root / "mock" / "shared" / "patient_registry.json"
        else:
            registry_path = Path(registry_path)

        self.registry_path = registry_path

        # Load patient registry
        self.registry = self._load_registry()

        # Build ICN→DFN lookup for this site
        self.icn_to_dfn = self._build_icn_dfn_map()

        logger.info(
            f"DataLoader initialized for site {site_sta3n}: "
            f"{len(self.icn_to_dfn)} patients registered"
        )

    def _load_registry(self) -> Dict[str, Any]:
        """Load patient registry from JSON file."""
        try:
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            logger.debug(f"Loaded patient registry from {self.registry_path}")
            return registry
        except FileNotFoundError:
            logger.error(f"Patient registry not found at {self.registry_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in patient registry: {e}")
            raise

    def _build_icn_dfn_map(self) -> Dict[str, str]:
        """
        Build ICN→DFN lookup dictionary for this site.

        Returns:
            Dictionary mapping ICN to DFN for patients registered at this site
        """
        icn_dfn_map = {}

        patients = self.registry.get("patients", [])

        for patient in patients:
            icn = patient.get("icn")
            if not icn:
                logger.warning(f"Patient record missing ICN: {patient}")
                continue

            # Find this patient's DFN at this site
            treating_facilities = patient.get("treating_facilities", [])

            for facility in treating_facilities:
                if facility.get("sta3n") == self.site_sta3n:
                    dfn = facility.get("dfn")
                    if dfn:
                        icn_dfn_map[icn] = dfn
                        logger.debug(f"Site {self.site_sta3n}: Mapped {icn} → {dfn}")
                    break

        return icn_dfn_map

    def resolve_icn_to_dfn(self, icn: str) -> Optional[str]:
        """
        Resolve ICN to site-specific DFN.

        Args:
            icn: Integrated Care Number (enterprise-wide patient identifier)

        Returns:
            DFN (site-specific patient identifier) or None if patient not registered at this site
        """
        dfn = self.icn_to_dfn.get(icn)

        if dfn:
            logger.debug(f"Site {self.site_sta3n}: Resolved {icn} → {dfn}")
        else:
            logger.info(
                f"Site {self.site_sta3n}: Patient {icn} not registered at this site"
            )

        return dfn

    def get_patient_info(self, icn: str) -> Optional[Dict[str, Any]]:
        """
        Get full patient information from registry.

        Args:
            icn: Integrated Care Number

        Returns:
            Patient dictionary or None if not found
        """
        patients = self.registry.get("patients", [])

        for patient in patients:
            if patient.get("icn") == icn:
                return patient

        return None

    def get_registered_patients(self) -> List[str]:
        """
        Get list of ICNs for all patients registered at this site.

        Returns:
            List of ICNs
        """
        return list(self.icn_to_dfn.keys())

    def is_patient_registered(self, icn: str) -> bool:
        """
        Check if patient is registered at this site.

        Args:
            icn: Integrated Care Number

        Returns:
            True if patient is registered at this site, False otherwise
        """
        return icn in self.icn_to_dfn
