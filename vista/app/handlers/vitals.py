# ---------------------------------------------------------------------
# vista/app/handlers/vitals.py
# ---------------------------------------------------------------------
# Vitals RPC Handlers
# Implements GMV* RPCs for patient vital signs
# ---------------------------------------------------------------------

import logging
from typing import Any, Dict, List
from datetime import datetime

from vista.app.services import RPCHandler, RPCExecutionError
from vista.app.utils import format_rpc_error

logger = logging.getLogger(__name__)


class LatestVitalsHandler(RPCHandler):
    """
    Handler for GMV LATEST VM RPC - Get Latest Vitals.

    Returns most recent vital signs for a patient in VistA format.

    RPC Signature:
        GMV LATEST VM(ICN)

    Parameters:
        params[0]: ICN (Integrated Care Number)

    Returns:
        Multi-line VistA-formatted string (one line per vital):
        TYPE^VALUE^UNITS^DATE_TIME^ENTERED_BY

    Example Response:
        BLOOD PRESSURE^120/80^mmHg^3241217.0930^NURSE,JANE
        TEMPERATURE^98.6^F^3241217.0930^NURSE,JANE
        PULSE^72^/min^3241217.0930^NURSE,JANE
        RESPIRATION^16^/min^3241217.0930^NURSE,JANE
        PULSE OXIMETRY^98^%^3241217.0930^NURSE,JANE

    Date/Time Format: FileMan format (YYYMMDD.HHMM)
        Example: 3241217.0930 = December 17, 2024 at 09:30
    """

    @property
    def rpc_name(self) -> str:
        """RPC name this handler responds to"""
        return "GMV LATEST VM"

    def validate_params(self, params: List[Any]) -> None:
        """
        Validate RPC parameters.

        Args:
            params: RPC parameters

        Raises:
            ValueError: If parameters are invalid
        """
        if not params or len(params) < 1:
            raise ValueError("GMV LATEST VM requires 1 parameter: ICN")

        icn = params[0]
        if not icn or not isinstance(icn, str):
            raise ValueError(f"Invalid ICN parameter: {icn}")

    def execute(self, params: List[Any], context: Dict[str, Any]) -> str:
        """
        Execute get latest vitals RPC.

        Args:
            params: RPC parameters [ICN]
            context: Request context containing:
                - data_loader: DataLoader instance for this site
                - site_sta3n: Station number

        Returns:
            Multi-line VistA-formatted vitals string

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

        logger.info(f"[Site {site_sta3n}] GMV LATEST VM called for ICN: {icn}")

        # Check if patient exists at this site
        patient = data_loader.get_patient_by_icn(icn)
        if not patient:
            logger.warning(f"[Site {site_sta3n}] Patient {icn} not found in registry")
            return format_rpc_error(f"Patient {icn} not found at site {site_sta3n}")

        # Load vitals data for this site
        vitals_data = data_loader.load_vitals()
        if not vitals_data:
            logger.warning(f"[Site {site_sta3n}] No vitals data file found")
            return format_rpc_error(f"No vitals data available at site {site_sta3n}")

        # Get vitals for this patient (by DFN)
        dfn = patient.get("dfn")
        patient_vitals = vitals_data.get("vitals", [])

        # Filter vitals for this patient
        matching_vitals = [v for v in patient_vitals if v.get("dfn") == dfn]

        if not matching_vitals:
            logger.info(f"[Site {site_sta3n}] No vitals found for patient {icn} (DFN: {dfn})")
            return format_rpc_error(f"No vitals found for patient")

        # Format vitals in VistA format (one per line)
        # Format: TYPE^VALUE^UNITS^DATE_TIME^ENTERED_BY
        vital_lines = []
        for vital in matching_vitals:
            vital_type = vital.get("type", "UNKNOWN")
            value = vital.get("value", "")
            units = vital.get("units", "")
            date_time = vital.get("date_time", "")  # FileMan format: YYYMMDD.HHMM
            entered_by = vital.get("entered_by", "")

            line = f"{vital_type}^{value}^{units}^{date_time}^{entered_by}"
            vital_lines.append(line)

        # Join with newlines (VistA multi-line response)
        response = "\n".join(vital_lines)

        logger.info(f"[Site {site_sta3n}] Returning {len(vital_lines)} vitals for patient {icn}")
        return response


# Export handlers
def get_vitals_handlers() -> List[RPCHandler]:
    """
    Get list of vitals RPC handlers.

    Returns:
        List of vitals handler instances
    """
    return [
        LatestVitalsHandler(),
        # Future handlers:
        # ExtractRecordsHandler(),  # GMV EXTRACT REC
        # ManagerHandler(),          # GMV MANAGER
    ]
