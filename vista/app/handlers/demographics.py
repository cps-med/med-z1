# ---------------------------------------------------------------------
# vista/app/handlers/demographics.py
# ---------------------------------------------------------------------
# Demographics RPC Handlers
# Implements ORWPT* RPCs for patient demographics
# ---------------------------------------------------------------------

import logging
from typing import Any, Dict, List

from vista.app.services import RPCHandler, RPCExecutionError
from vista.app.utils import format_patient_inquiry_response, format_rpc_error

logger = logging.getLogger(__name__)


class PatientInquiryHandler(RPCHandler):
    """
    Handler for ORWPT PTINQ RPC - Patient Inquiry.

    Returns basic patient demographics in VistA format.

    RPC Signature:
        ORWPT PTINQ(ICN)

    Parameters:
        params[0]: ICN (Integrated Care Number)

    Returns:
        VistA-formatted string: NAME^SSN^DOB^SEX^VETERAN_STATUS

    Example Response:
        "SMITH,JOHN Q^666-12-1234^2450315^M^VETERAN"
    """

    @property
    def rpc_name(self) -> str:
        """RPC name this handler responds to"""
        return "ORWPT PTINQ"

    def validate_params(self, params: List[Any]) -> None:
        """
        Validate RPC parameters.

        Args:
            params: RPC parameters

        Raises:
            ValueError: If parameters are invalid
        """
        if not params or len(params) < 1:
            raise ValueError("ORWPT PTINQ requires 1 parameter: ICN")

        icn = params[0]
        if not icn or not isinstance(icn, str):
            raise ValueError(f"Invalid ICN parameter: {icn}")

    def execute(self, params: List[Any], context: Dict[str, Any]) -> str:
        """
        Execute patient inquiry RPC.

        Args:
            params: RPC parameters [ICN]
            context: Request context containing:
                - data_loader: DataLoader instance for this site
                - site_sta3n: Station number

        Returns:
            VistA-formatted patient demographics string

        Raises:
            RPCExecutionError: If patient not found or execution fails
        """
        # Validate parameters
        self.validate_params(params)

        icn = params[0]
        data_loader = context.get("data_loader")
        site_sta3n = context.get("site_sta3n", "UNKNOWN")

        if not data_loader:
            logger.error("DataLoader not provided in context")
            raise RPCExecutionError(
                rpc_name=self.rpc_name,
                message="DataLoader not available"
            )

        try:
            # Get patient info from registry
            patient = data_loader.get_patient_info(icn)

            if not patient:
                logger.info(f"Patient {icn} not found in registry")
                return format_rpc_error(f"Patient {icn} not found", code="-1")

            # Check if patient is registered at this site
            if not data_loader.is_patient_registered(icn):
                logger.info(f"Patient {icn} not registered at site {site_sta3n}")
                return format_rpc_error(
                    f"Patient {icn} not registered at site {site_sta3n}",
                    code="-1"
                )

            # Format patient response in VistA format
            response = format_patient_inquiry_response(patient)

            logger.debug(
                f"ORWPT PTINQ for {icn} at site {site_sta3n}: {response}"
            )

            return response

        except Exception as e:
            logger.error(f"Error executing ORWPT PTINQ for {icn}: {e}", exc_info=True)
            raise RPCExecutionError(
                rpc_name=self.rpc_name,
                message=f"Failed to retrieve patient data: {str(e)}",
                original_error=e
            )
