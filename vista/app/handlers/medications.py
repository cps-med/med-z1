# ---------------------------------------------------------------------
# vista/app/handlers/medications.py
# ---------------------------------------------------------------------
# Medications RPC Handlers
# Implements ORWPS* RPCs for patient medications (outpatient pharmacy)
# ---------------------------------------------------------------------

import logging
from typing import Any, Dict, List
from datetime import datetime

from vista.app.services import RPCHandler, RPCExecutionError
from vista.app.utils import format_rpc_error

logger = logging.getLogger(__name__)


class MedicationsCoverHandler(RPCHandler):
    """
    Handler for ORWPS COVER RPC - Active Outpatient Medications (Cover Sheet).

    Returns active outpatient prescriptions for a patient in VistA format.

    RPC Signature:
        ORWPS COVER(ICN)

    Parameters:
        params[0]: ICN (Integrated Care Number)

    Returns:
        Multi-line VistA-formatted string (one line per medication):
        RX_NUMBER^DRUG_NAME^STATUS^QUANTITY/DAYS_SUPPLY^REFILLS_REMAINING^ISSUE_DATE^EXPIRATION_DATE

    Example Response:
        2860066^LISINOPRIL 10MG TAB^ACTIVE^60/90^3^3260106.1035^3270106
        2860067^METFORMIN HCL 500MG TAB^ACTIVE^120/180^5^3260106.1030^3270106
        2860070^ASPIRIN 81MG TAB^ACTIVE^90/90^0^3260101.1420^3270101

    Date/Time Format: FileMan format (YYYMMDD.HHMM or YYYMMDD)
        Example: 3260106.1035 = January 6, 2026 at 10:35
        Example: 3270106 = January 6, 2027 (date only)
    """

    @property
    def rpc_name(self) -> str:
        """RPC name this handler responds to"""
        return "ORWPS COVER"

    def validate_params(self, params: List[Any]) -> None:
        """
        Validate RPC parameters.

        Args:
            params: RPC parameters

        Raises:
            ValueError: If parameters are invalid
        """
        if not params or len(params) < 1:
            raise ValueError("ORWPS COVER requires 1 parameter: ICN")

        icn = params[0]
        if not icn or not isinstance(icn, str):
            raise ValueError(f"Invalid ICN parameter: {icn}")

    def execute(self, params: List[Any], context: Dict[str, Any]) -> str:
        """
        Execute get active medications RPC (cover sheet).

        Args:
            params: RPC parameters [ICN]
            context: Request context containing:
                - data_loader: DataLoader instance for this site
                - site_sta3n: Station number

        Returns:
            Multi-line VistA-formatted medications string (empty string if no meds)

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

        logger.info(f"[Site {site_sta3n}] ORWPS COVER called for ICN: {icn}")

        # Check if patient exists at this site
        patient = data_loader.get_patient_by_icn(icn)
        if not patient:
            logger.warning(f"[Site {site_sta3n}] Patient {icn} not found in registry")
            # For medications, return empty string if patient not found (not an error)
            return ""

        # Load medications data for this site
        medications_data = data_loader.load_medications()
        if not medications_data:
            logger.warning(f"[Site {site_sta3n}] No medications data file found")
            return ""

        # Get medications for this patient (by DFN)
        dfn = patient.get("dfn")
        all_medications = medications_data.get("medications", [])

        # Filter medications for this patient and status=ACTIVE
        patient_medications = [
            m for m in all_medications
            if m.get("dfn") == dfn and m.get("status") == "ACTIVE"
        ]

        if not patient_medications:
            logger.info(f"[Site {site_sta3n}] No active medications found for patient {icn} (DFN: {dfn})")
            return ""

        # Format medications in VistA format (one per line)
        # Format: RX_NUMBER^DRUG_NAME^STATUS^QUANTITY/DAYS_SUPPLY^REFILLS_REMAINING^ISSUE_DATE^EXPIRATION_DATE
        med_lines = []
        for med in patient_medications:
            rx_number = med.get("rx_number", "")
            drug_name = med.get("drug_name", "")
            status = med.get("status", "ACTIVE")
            quantity = med.get("quantity", "")
            days_supply = med.get("days_supply", "")
            refills_remaining = med.get("refills_remaining", "")
            issue_date = med.get("issue_date", "")  # T-notation or FileMan
            expiration_date = med.get("expiration_date", "")  # T-notation or FileMan

            # Convert T-notation dates to FileMan format
            issue_date_fm = data_loader.parse_t_notation_to_fileman(issue_date)
            expiration_date_fm = data_loader.parse_t_notation_to_fileman(expiration_date)

            # Build caret-delimited line
            # QUANTITY/DAYS_SUPPLY format (e.g., "60/90")
            qty_days = f"{quantity}/{days_supply}"

            line = f"{rx_number}^{drug_name}^{status}^{qty_days}^{refills_remaining}^{issue_date_fm}^{expiration_date_fm}"
            med_lines.append(line)

        # Join with newlines (VistA multi-line response)
        response = "\n".join(med_lines)

        logger.info(f"[Site {site_sta3n}] Returning {len(med_lines)} active medications for patient {icn}")
        return response


# Export handlers
def get_medications_handlers() -> List[RPCHandler]:
    """
    Get list of medications RPC handlers.

    Returns:
        List of medications handler instances
    """
    return [
        MedicationsCoverHandler(),
        # Future handlers:
        # MedicationsDetailHandler(),  # ORWPS DETAIL
        # MedicationsActiveHandler(),   # ORWPS ACTIVE
        # PharmacySupplyHandler(),      # PSO SUPPLY
    ]
