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
from datetime import datetime, timedelta

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
            f"Initialized for site {site_sta3n}: "
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

    def get_patient_by_icn(self, icn: str) -> Optional[Dict[str, Any]]:
        """
        Get patient information including site-specific DFN.

        Args:
            icn: Integrated Care Number

        Returns:
            Dictionary with patient info including DFN for this site, or None if not registered
        """
        # Check if patient is registered at this site
        dfn = self.resolve_icn_to_dfn(icn)
        if not dfn:
            return None

        # Get full patient info from registry
        patient_info = self.get_patient_info(icn)
        if not patient_info:
            return None

        # Add site-specific DFN to patient info
        return {
            **patient_info,
            "dfn": dfn,
            "site_sta3n": self.site_sta3n
        }

    @staticmethod
    def parse_t_notation_to_fileman(t_notation: str) -> str:
        """
        Parse T-notation date/time to FileMan format.

        T-notation format: "T±N.HHMM" or "T±N" where N is days offset from today
        Examples:
            "T-0.0845" = Today at 08:45
            "T-1.1030" = Yesterday at 10:30
            "T-7.1400" = 7 days ago at 14:00
            "T+358" = 358 days in the future (date only)
            "T+30.1200" = 30 days in the future at 12:00

        FileMan format: YYYMMDD.HHMM or YYYMMDD where YYY = year - 1700
        Examples:
            "3251217.0845" = December 17, 2025 at 08:45
            "3270106" = January 6, 2027 (date only)

        Args:
            t_notation: T-notation string (e.g., "T-0.0845" or "T+358")

        Returns:
            FileMan format string (e.g., "3251217.0845" or "3270106")
        """
        try:
            # Check if this is T-notation
            if not (t_notation.startswith("T-") or t_notation.startswith("T+")):
                # Not T-notation, return as-is (already in FileMan format)
                return t_notation

            # Determine if past (T-) or future (T+)
            is_future = t_notation.startswith("T+")

            # Split on '.' to get date offset and optional time
            parts = t_notation.split('.')

            if len(parts) == 1:
                # No time component (e.g., "T+358")
                date_part = parts[0]
                time_part = None
            elif len(parts) == 2:
                # Has time component (e.g., "T-7.1400")
                date_part = parts[0]
                time_part = parts[1]
            else:
                logger.warning(f"Invalid T-notation format: {t_notation}")
                return t_notation  # Return as-is if not T-notation

            # Extract offset (days)
            offset_str = date_part[2:]  # Remove "T-" or "T+" prefix
            days_offset = int(offset_str)

            # Calculate target date (today ± offset)
            if is_future:
                target_date = datetime.now() + timedelta(days=days_offset)
            else:
                target_date = datetime.now() - timedelta(days=days_offset)

            # Convert to FileMan date format: YYYMMDD
            # YYY = year - 1700
            yyy = target_date.year - 1700
            mm = target_date.month
            dd = target_date.day

            # Format as YYYMMDD.HHMM or YYYMMDD (depending on time_part)
            if time_part:
                fileman_date = f"{yyy:03d}{mm:02d}{dd:02d}.{time_part}"
            else:
                fileman_date = f"{yyy:03d}{mm:02d}{dd:02d}"

            logger.debug(f"Converted T-notation {t_notation} → FileMan {fileman_date}")
            return fileman_date

        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse T-notation '{t_notation}': {e}")
            return t_notation  # Return as-is if parsing fails

    def load_vitals(self) -> Optional[Dict[str, Any]]:
        """
        Load vitals data for this site from JSON file.

        Supports both FileMan format and T-notation for date_time fields.
        T-notation dates are automatically converted to today's equivalent FileMan format.

        Returns:
            Dictionary with vitals data, or None if file not found

        File location: vista/app/data/sites/{sta3n}/vitals.json
        """
        try:
            # Construct path to vitals data file
            # Assume structure: vista/app/data/sites/{sta3n}/vitals.json
            vista_root = Path(__file__).parent.parent
            vitals_path = vista_root / "data" / "sites" / self.site_sta3n / "vitals.json"

            if not vitals_path.exists():
                logger.warning(f"Vitals data file not found: {vitals_path}")
                return None

            with open(vitals_path, 'r') as f:
                vitals_data = json.load(f)

            # Convert T-notation dates to FileMan format
            vitals_list = vitals_data.get("vitals", [])
            for vital in vitals_list:
                if "date_time" in vital:
                    original = vital["date_time"]
                    converted = self.parse_t_notation_to_fileman(original)
                    vital["date_time"] = converted

            logger.debug(f"Loaded vitals data from {vitals_path}")
            return vitals_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in vitals data file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading vitals data: {e}")
            return None

    def load_encounters(self) -> Optional[Dict[str, Any]]:
        """
        Load encounters data for this site from JSON file.

        Supports both FileMan format and T-notation for date_time fields.
        T-notation dates are automatically converted to today's equivalent FileMan format.

        Returns:
            Dictionary with encounters data, or None if file not found

        File location: vista/app/data/sites/{sta3n}/encounters.json
        """
        try:
            # Construct path to encounters data file
            # Assume structure: vista/app/data/sites/{sta3n}/encounters.json
            vista_root = Path(__file__).parent.parent
            encounters_path = vista_root / "data" / "sites" / self.site_sta3n / "encounters.json"

            if not encounters_path.exists():
                logger.warning(f"Encounters data file not found: {encounters_path}")
                return None

            with open(encounters_path, 'r') as f:
                encounters_data = json.load(f)

            # Convert T-notation dates to FileMan format
            encounters_list = encounters_data.get("encounters", [])
            for encounter in encounters_list:
                # Convert admit_datetime
                if "admit_datetime" in encounter:
                    original = encounter["admit_datetime"]
                    converted = self.parse_t_notation_to_fileman(original)
                    encounter["admit_datetime"] = converted

                # Convert discharge_datetime (may be empty for active admissions)
                if "discharge_datetime" in encounter and encounter["discharge_datetime"]:
                    original = encounter["discharge_datetime"]
                    converted = self.parse_t_notation_to_fileman(original)
                    encounter["discharge_datetime"] = converted

            logger.debug(f"Loaded encounters data from {encounters_path}")
            return encounters_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in encounters data file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading encounters data: {e}")
            return None

    def load_allergies(self) -> Optional[Dict[str, Any]]:
        """
        Load allergies data for this site from JSON file.

        Supports both FileMan format and T-notation for reaction_datetime fields.
        T-notation dates are automatically converted to today's equivalent FileMan format.

        Returns:
            Dictionary with allergies data, or None if file not found

        File location: vista/app/data/sites/{sta3n}/allergies.json
        """
        try:
            # Construct path to allergies data file
            # Assume structure: vista/app/data/sites/{sta3n}/allergies.json
            vista_root = Path(__file__).parent.parent
            allergies_path = vista_root / "data" / "sites" / self.site_sta3n / "allergies.json"

            if not allergies_path.exists():
                logger.warning(f"Allergies data file not found: {allergies_path}")
                return None

            with open(allergies_path, 'r') as f:
                allergies_data = json.load(f)

            # Convert T-notation dates to FileMan format
            allergies_list = allergies_data.get("allergies", [])
            for allergy in allergies_list:
                # Convert reaction_datetime
                if "reaction_datetime" in allergy:
                    original = allergy["reaction_datetime"]
                    converted = self.parse_t_notation_to_fileman(original)
                    allergy["reaction_datetime"] = converted

            logger.debug(f"Loaded allergies data from {allergies_path}")
            return allergies_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in allergies data file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading allergies data: {e}")
            return None

    def load_medications(self) -> Optional[Dict[str, Any]]:
        """
        Load medications data for this site from JSON file.

        Supports both FileMan format and T-notation for date fields.
        T-notation dates are automatically converted to today's equivalent FileMan format.

        Returns:
            Dictionary with medications data, or None if file not found

        File location: vista/app/data/sites/{sta3n}/medications.json
        """
        try:
            # Construct path to medications data file
            # Assume structure: vista/app/data/sites/{sta3n}/medications.json
            vista_root = Path(__file__).parent.parent
            medications_path = vista_root / "data" / "sites" / self.site_sta3n / "medications.json"

            if not medications_path.exists():
                logger.warning(f"Medications data file not found: {medications_path}")
                return None

            with open(medications_path, 'r') as f:
                medications_data = json.load(f)

            # Convert T-notation dates to FileMan format
            medications_list = medications_data.get("medications", [])
            for medication in medications_list:
                # Convert issue_date
                if "issue_date" in medication:
                    original = medication["issue_date"]
                    converted = self.parse_t_notation_to_fileman(original)
                    medication["issue_date"] = converted

                # Convert expiration_date
                if "expiration_date" in medication:
                    original = medication["expiration_date"]
                    converted = self.parse_t_notation_to_fileman(original)
                    medication["expiration_date"] = converted

            logger.debug(f"Loaded medications data from {medications_path}")
            return medications_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in medications data file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading medications data: {e}")
            return None
