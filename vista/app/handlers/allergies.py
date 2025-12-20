# ---------------------------------------------------------------------
# vista/app/handlers/allergies.py
# ---------------------------------------------------------------------
# Allergies RPC Handlers
# Implements ORQQAL* RPCs for patient allergies and adverse reactions
# ---------------------------------------------------------------------

import logging
from typing import Any, Dict, List
from datetime import datetime

from vista.app.services import RPCHandler, RPCExecutionError
from vista.app.utils import format_rpc_error

logger = logging.getLogger(__name__)


class AllergiesListHandler(RPCHandler):
    """
    Handler for ORQQAL LIST RPC - Get Patient Allergy List.

    Returns patient allergy data in VistA format.

    RPC Signature:
        ORQQAL LIST(ICN)

    Parameters:
        params[0]: ICN (Integrated Care Number)

    Returns:
        Multi-line VistA-formatted string (one line per allergy):
        AllergenName^Severity^ReactionDateTime^Reactions^AllergyType^OriginatingSite^EnteredBy

    Example Response:
        PENICILLIN^SEVERE^3251120.0930^HIVES,ITCHING,RASH^DRUG^200^PHARMACIST,JOHN
        SHELLFISH^MODERATE^3250815.1445^NAUSEA,VOMITING^FOOD^200^NURSE,SARAH
        SULFA DRUGS^MILD^3241030.0800^RASH^DRUG^500^DOCTOR,EMILY
        LATEX^MODERATE^3230405.1020^CONTACT DERMATITIS^ENVIRONMENTAL^630^NURSE,MICHAEL

    Date/Time Format: FileMan format (YYYMMDD.HHMM)
        Example: 3251219.1430 = December 19, 2025 at 14:30
    """

    @property
    def rpc_name(self) -> str:
        """RPC name this handler responds to"""
        return "ORQQAL LIST"

    def validate_params(self, params: List[Any]) -> None:
        """
        Validate RPC parameters.

        Args:
            params: RPC parameters

        Raises:
            ValueError: If parameters are invalid
        """
        if not params or len(params) < 1:
            raise ValueError("ORQQAL LIST requires 1 parameter: ICN")

        icn = params[0]
        if not icn or not isinstance(icn, str):
            raise ValueError(f"Invalid ICN parameter: {icn}")

    def execute(self, params: List[Any], context: Dict[str, Any]) -> str:
        """
        Execute get allergy list RPC.

        Args:
            params: RPC parameters [ICN]
            context: Request context containing:
                - data_loader: DataLoader instance for this site
                - site_sta3n: Station number

        Returns:
            Multi-line VistA-formatted allergies string

        Raises:
            RPCExecutionError: If patient not found or execution fails
        """
        # Validate parameters
        self.validate_params(params)

        icn = params[0]

        data_loader = context.get("data_loader")
        site_sta3n = context.get("site_sta3n", "UNKNOWN")

        if not data_loader:
            logger.error("DataLoader not found in context")
            return format_rpc_error("Internal error: DataLoader not available")

        logger.info(f"[Site {site_sta3n}] ORQQAL LIST called for ICN: {icn}")

        # Check if patient exists at this site
        patient = data_loader.get_patient_by_icn(icn)
        if not patient:
            logger.warning(f"[Site {site_sta3n}] Patient {icn} not found in registry")
            return format_rpc_error(f"Patient {icn} not registered at site {site_sta3n}")

        # Load allergies data for this site
        allergies_data = data_loader.load_allergies()
        if not allergies_data:
            logger.warning(f"[Site {site_sta3n}] No allergies data file found")
            return format_rpc_error(f"No allergies data available at site {site_sta3n}")

        # Get allergies for this patient (by DFN)
        dfn = patient.get("dfn")
        all_allergies = allergies_data.get("allergies", [])

        # Filter allergies for this patient
        matching_allergies = [a for a in all_allergies if a.get("dfn") == dfn]

        if not matching_allergies:
            logger.info(f"[Site {site_sta3n}] No allergies found for patient {icn} (DFN: {dfn})")
            # Return empty response (not an error - patient has no known allergies)
            return ""

        # Format allergies in VistA format (one per line)
        # Format: AllergenName^Severity^ReactionDateTime^Reactions^AllergyType^OriginatingSite^EnteredBy
        allergy_lines = []
        for allergy in matching_allergies:
            allergen_name = allergy.get("allergen_name", "")
            severity = allergy.get("severity", "")
            reaction_datetime = allergy.get("reaction_datetime", "")
            reactions = allergy.get("reactions", "")
            allergy_type = allergy.get("allergy_type", "")
            originating_site = allergy.get("originating_site", site_sta3n)
            entered_by = allergy.get("entered_by", "")

            line = f"{allergen_name}^{severity}^{reaction_datetime}^{reactions}^{allergy_type}^{originating_site}^{entered_by}"
            allergy_lines.append(line)

        # Join with newlines (VistA multi-line response)
        response = "\n".join(allergy_lines)

        logger.info(f"[Site {site_sta3n}] Returning {len(allergy_lines)} allergies for patient {icn}")
        return response


# Export handlers
__all__ = ["AllergiesListHandler"]
