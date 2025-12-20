# ---------------------------------------------------------------------
# vista/app/handlers/encounters.py
# ---------------------------------------------------------------------
# Encounters RPC Handlers
# Implements ORWCV* RPCs for patient inpatient encounters/admissions
# ---------------------------------------------------------------------

import logging
from typing import Any, Dict, List
from datetime import datetime

from vista.app.services import RPCHandler, RPCExecutionError
from vista.app.utils import format_rpc_error

logger = logging.getLogger(__name__)


class AdmissionsHandler(RPCHandler):
    """
    Handler for ORWCV ADMISSIONS RPC - Get Inpatient Admissions/Discharges.

    Returns inpatient encounter data for a patient in VistA format.

    RPC Signature:
        ORWCV ADMISSIONS(ICN, [DAYS_BACK])

    Parameters:
        params[0]: ICN (Integrated Care Number)
        params[1]: DAYS_BACK (optional, default 90) - Number of days to look back

    Returns:
        Multi-line VistA-formatted string (one line per encounter):
        InpatientID^AdmitDateTime^AdmitLocation^Status^DischargeDateTime^DischargeLocation^LOS^DiagnosisCode^AdmitProvider

    Example Response:
        285001^3251215.1430^7A MED/SURG^DISCHARGED^3251220.1015^DISCHARGE UNIT^5^I50.9^DOE,JOHN
        285023^3251218.0830^ICU^ACTIVE^^^0^J18.9^SMITH,JANE
        284987^3251201.2130^EMERGENCY^DISCHARGED^3251203.0945^HOME^2^R07.9^WILLIAMS,ROBERT

    Date/Time Format: FileMan format (YYYMMDD.HHMM)
        Example: 3251219.1430 = December 19, 2025 at 14:30
    """

    @property
    def rpc_name(self) -> str:
        """RPC name this handler responds to"""
        return "ORWCV ADMISSIONS"

    def validate_params(self, params: List[Any]) -> None:
        """
        Validate RPC parameters.

        Args:
            params: RPC parameters

        Raises:
            ValueError: If parameters are invalid
        """
        if not params or len(params) < 1:
            raise ValueError("ORWCV ADMISSIONS requires at least 1 parameter: ICN")

        icn = params[0]
        if not icn or not isinstance(icn, str):
            raise ValueError(f"Invalid ICN parameter: {icn}")

        # DAYS_BACK is optional (params[1])
        if len(params) > 1:
            days_back = params[1]
            if days_back is not None and not isinstance(days_back, (int, str)):
                raise ValueError(f"Invalid DAYS_BACK parameter: {days_back}")

    def execute(self, params: List[Any], context: Dict[str, Any]) -> str:
        """
        Execute get admissions/encounters RPC.

        Args:
            params: RPC parameters [ICN, optional DAYS_BACK]
            context: Request context containing:
                - data_loader: DataLoader instance for this site
                - site_sta3n: Station number

        Returns:
            Multi-line VistA-formatted encounters string

        Raises:
            RPCExecutionError: If patient not found or execution fails
        """
        # Validate parameters
        self.validate_params(params)

        icn = params[0]
        days_back = int(params[1]) if len(params) > 1 and params[1] else 90  # Default 90 days

        data_loader = context.get("data_loader")
        site_sta3n = context.get("site_sta3n", "UNKNOWN")

        if not data_loader:
            logger.error("DataLoader not found in context")
            return format_rpc_error("Internal error: DataLoader not available")

        logger.info(f"[Site {site_sta3n}] ORWCV ADMISSIONS called for ICN: {icn} (days_back: {days_back})")

        # Check if patient exists at this site
        patient = data_loader.get_patient_by_icn(icn)
        if not patient:
            logger.warning(f"[Site {site_sta3n}] Patient {icn} not found in registry")
            return format_rpc_error(f"Patient {icn} not registered at site {site_sta3n}")

        # Load encounters data for this site
        encounters_data = data_loader.load_encounters()
        if not encounters_data:
            logger.warning(f"[Site {site_sta3n}] No encounters data file found")
            return format_rpc_error(f"No encounters data available at site {site_sta3n}")

        # Get encounters for this patient (by DFN)
        dfn = patient.get("dfn")
        all_encounters = encounters_data.get("encounters", [])

        # Filter encounters for this patient
        matching_encounters = [e for e in all_encounters if e.get("dfn") == dfn]

        if not matching_encounters:
            logger.info(f"[Site {site_sta3n}] No encounters found for patient {icn} (DFN: {dfn})")
            return format_rpc_error(f"No encounters found for patient")

        # Format encounters in VistA format (one per line)
        # Format: InpatientID^AdmitDateTime^AdmitLocation^Status^DischargeDateTime^DischargeLocation^LOS^DiagnosisCode^AdmitProvider
        encounter_lines = []
        for enc in matching_encounters:
            inpatient_id = enc.get("inpatient_id", "")
            admit_datetime = enc.get("admit_datetime", "")
            admit_location = enc.get("admit_location", "")
            status = enc.get("status", "")
            discharge_datetime = enc.get("discharge_datetime", "")
            discharge_location = enc.get("discharge_location", "")
            los = enc.get("length_of_stay", "0")
            diagnosis_code = enc.get("diagnosis_code", "")
            admit_provider = enc.get("admit_provider", "")

            line = f"{inpatient_id}^{admit_datetime}^{admit_location}^{status}^{discharge_datetime}^{discharge_location}^{los}^{diagnosis_code}^{admit_provider}"
            encounter_lines.append(line)

        # Join with newlines (VistA multi-line response)
        response = "\n".join(encounter_lines)

        logger.info(f"[Site {site_sta3n}] Returning {len(encounter_lines)} encounters for patient {icn}")
        return response


# Export handlers
def get_encounters_handlers() -> List[RPCHandler]:
    """
    Get list of encounters RPC handlers.

    Returns:
        List of encounters handler instances
    """
    return [
        AdmissionsHandler(),
        # Future handlers:
        # VisitListHandler(),    # ORWCV VST
        # DetailHandler(),       # ORWCV DETAIL
    ]
