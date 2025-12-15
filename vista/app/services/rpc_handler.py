# ---------------------------------------------------------------------
# vista/app/services/rpc_handler.py
# ---------------------------------------------------------------------
# Base RPC Handler Interface
# All VistA RPC handlers inherit from this abstract base class
# ---------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class RPCHandler(ABC):
    """
    Abstract base class for all VistA RPC handlers.

    Each RPC handler implements the logic for a specific VistA Remote Procedure Call.
    Handlers receive parameters, execute the RPC logic, and return VistA-formatted responses.

    Example:
        class PatientInquiryHandler(RPCHandler):
            @property
            def rpc_name(self) -> str:
                return "ORWPT PTINQ"

            def execute(self, params: List[Any], context: Dict[str, Any]) -> Any:
                icn = params[0]
                patient = self.data_loader.get_patient_info(icn)
                return self._format_vista_response(patient)
    """

    @property
    @abstractmethod
    def rpc_name(self) -> str:
        """
        The VistA RPC name this handler responds to.

        Returns:
            RPC name (e.g., "ORWPT PTINQ", "GMV LATEST VM")
        """
        pass

    @abstractmethod
    def execute(self, params: List[Any], context: Dict[str, Any]) -> Any:
        """
        Execute the RPC with given parameters.

        Args:
            params: List of RPC parameters (order matches VistA RPC signature)
            context: Request context containing:
                - site_sta3n: Station number for this site
                - data_loader: DataLoader instance for ICN/DFN resolution
                - request_id: Unique request identifier (for logging)

        Returns:
            RPC response data in VistA format (string, list, or dict)

        Raises:
            RPCExecutionError: If RPC execution fails
        """
        pass

    def validate_params(self, params: List[Any]) -> None:
        """
        Validate RPC parameters before execution.

        Override this method to implement parameter validation.

        Args:
            params: RPC parameters to validate

        Raises:
            ValueError: If parameters are invalid
        """
        pass


class RPCExecutionError(Exception):
    """Exception raised when RPC execution fails"""

    def __init__(self, rpc_name: str, message: str, original_error: Optional[Exception] = None):
        self.rpc_name = rpc_name
        self.message = message
        self.original_error = original_error
        super().__init__(f"RPC '{rpc_name}' failed: {message}")
