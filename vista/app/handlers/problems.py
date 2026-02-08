# ---------------------------------------------------------------------
# vista/app/handlers/problems.py
# ---------------------------------------------------------------------
# Problems RPC Handlers
# Implements ORQQPL* RPCs for patient problem list
# ---------------------------------------------------------------------

import logging
from typing import Any, Dict, List
from datetime import datetime

from vista.app.services import RPCHandler, RPCExecutionError
from vista.app.utils import format_rpc_error

logger = logging.getLogger(__name__)


class ProblemsListHandler(RPCHandler):
    """
    Handler for ORQQPL LIST RPC - Get Patient Problem List.

    Returns all active problems with metadata including whether the problem
    was updated today (T-0).

    RPC Signature:
        ORQQPL LIST(ICN)

    Parameters:
        params[0]: ICN (Integrated Care Number)

    Returns:
        Multi-line VistA-formatted string (one line per problem):
        PROBLEM_IEN^PROBLEM_TEXT^ICD10_CODE^STATUS^ONSET_DATE^SERVICE_CONNECTED^SNOMED_CODE^UPDATED_TODAY

    Example Response:
        123^Diabetes mellitus type 2^E11.9^Active^3230115^1^44054006^0
        456^Acute exacerbation of COPD^J44.1^Active^3260207^0^195951007^1
        789^Hypertension^I10^Active^3220601^1^38341003^0

    Date Format: FileMan format (YYYMMDD)
        Example: 3230115 = January 15, 2023
        Example: 3260207 = February 7, 2026 (today)

    Updated Today Flag: 1 = updated today (T-0), 0 = not updated today
    Service Connected: 1 = service connected, 0 = not service connected
    """

    @property
    def rpc_name(self) -> str:
        """RPC name this handler responds to"""
        return "ORQQPL LIST"

    def validate_params(self, params: List[Any]) -> None:
        """
        Validate RPC parameters.

        Args:
            params: RPC parameters

        Raises:
            ValueError: If parameters are invalid
        """
        if not params or len(params) < 1:
            raise ValueError("ORQQPL LIST requires 1 parameter: ICN")

        icn = params[0]
        if not icn or not isinstance(icn, str):
            raise ValueError(f"Invalid ICN parameter: {icn}")

    def execute(self, params: List[Any], context: Dict[str, Any]) -> str:
        """
        Execute get patient problem list RPC.

        Args:
            params: RPC parameters [ICN]
            context: Request context containing:
                - data_loader: DataLoader instance for this site
                - site_sta3n: Station number

        Returns:
            Multi-line VistA-formatted problems string (empty string if no problems)

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

        logger.info(f"[Site {site_sta3n}] ORQQPL LIST called for ICN: {icn}")

        # Check if patient exists at this site
        patient = data_loader.get_patient_by_icn(icn)
        if not patient:
            logger.warning(f"[Site {site_sta3n}] Patient {icn} not found in registry")
            # For problems, return empty string if patient not found (not an error)
            return ""

        # Load problems data for this site
        problems_data = data_loader.load_problems()
        if not problems_data:
            logger.warning(f"[Site {site_sta3n}] No problems data file found")
            return ""

        # Get problems for this patient (by DFN)
        dfn = patient.get("dfn")
        all_problems = problems_data.get("problems", [])

        # Filter problems for this patient (all statuses - Active, Inactive, Resolved)
        patient_problems = [
            p for p in all_problems
            if p.get("dfn") == dfn
        ]

        if not patient_problems:
            logger.info(f"[Site {site_sta3n}] No problems found for patient {icn} (DFN: {dfn})")
            return ""

        # Format problems in VistA format (one per line)
        # Format: PROBLEM_IEN^PROBLEM_TEXT^ICD10_CODE^STATUS^ONSET_DATE^SERVICE_CONNECTED^SNOMED_CODE^UPDATED_TODAY
        problem_lines = []
        for problem in patient_problems:
            problem_ien = problem.get("problem_ien", "")
            problem_text = problem.get("problem_text", "")
            icd10_code = problem.get("icd10_code", "")
            status = problem.get("problem_status", "Active")
            onset_date = problem.get("onset_date", "")  # T-notation or FileMan
            service_connected = "1" if problem.get("service_connected", False) else "0"
            snomed_code = problem.get("snomed_code", "")
            updated_today = "1" if problem.get("updated_today", False) else "0"

            # Convert T-notation date to FileMan format
            onset_date_fm = data_loader.parse_t_notation_to_fileman(onset_date)

            # Build caret-delimited line
            line = f"{problem_ien}^{problem_text}^{icd10_code}^{status}^{onset_date_fm}^{service_connected}^{snomed_code}^{updated_today}"
            problem_lines.append(line)

        # Join with newlines (VistA multi-line response)
        response = "\n".join(problem_lines)

        logger.info(f"[Site {site_sta3n}] Returning {len(problem_lines)} problems for patient {icn}")
        return response


# Export handlers
def get_problems_handlers() -> List[RPCHandler]:
    """
    Get list of problems RPC handlers.

    Returns:
        List of problems handler instances
    """
    return [
        ProblemsListHandler(),
        # Future handlers:
        # ProblemsDetailHandler(),  # ORQQPL DETAIL
        # ProblemsAddHandler(),     # ORQQPL ADD SAVE
        # ProblemsEditHandler(),    # ORQQPL EDIT SAVE
    ]
