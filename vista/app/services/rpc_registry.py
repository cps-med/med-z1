# ---------------------------------------------------------------------
# vista/app/services/rpc_registry.py
# ---------------------------------------------------------------------
# RPC Handler Registry
# Maps RPC names to handler instances and dispatches requests
# ---------------------------------------------------------------------

import logging
from typing import Dict, Optional, List, Any
from .rpc_handler import RPCHandler, RPCExecutionError

logger = logging.getLogger(__name__)


class RPCRegistry:
    """
    Registry for VistA RPC handlers.

    Maintains a mapping of RPC names to handler instances and provides
    dispatch functionality to route incoming RPC requests to the correct handler.

    Example:
        registry = RPCRegistry()
        registry.register(PatientInquiryHandler(data_loader))
        registry.register(VitalsHandler(data_loader))

        # Dispatch RPC
        response = registry.dispatch("ORWPT PTINQ", ["ICN100001"], context)
    """

    def __init__(self):
        """Initialize empty RPC registry"""
        self._handlers: Dict[str, RPCHandler] = {}
        logger.info("RPCRegistry initialized")

    def register(self, handler: RPCHandler) -> None:
        """
        Register an RPC handler.

        Args:
            handler: RPCHandler instance to register

        Raises:
            ValueError: If handler is invalid
        """
        if not isinstance(handler, RPCHandler):
            raise ValueError(f"Handler must be instance of RPCHandler, got {type(handler)}")

        rpc_name = handler.rpc_name
        if not rpc_name:
            raise ValueError("Handler must specify non-empty rpc_name")

        if rpc_name in self._handlers:
            logger.warning(f"Overwriting existing handler for RPC: {rpc_name}")

        self._handlers[rpc_name] = handler
        logger.info(f"Registered handler for RPC: {rpc_name}")

    def get_handler(self, rpc_name: str) -> Optional[RPCHandler]:
        """
        Get handler for a specific RPC name.

        Args:
            rpc_name: VistA RPC name

        Returns:
            RPCHandler instance or None if not found
        """
        return self._handlers.get(rpc_name)

    def dispatch(self, rpc_name: str, params: List[Any], context: Dict[str, Any]) -> Any:
        """
        Dispatch RPC request to appropriate handler.

        Args:
            rpc_name: VistA RPC name
            params: RPC parameters
            context: Request context (site, data_loader, etc.)

        Returns:
            RPC response from handler

        Raises:
            RPCExecutionError: If RPC not found or execution fails
        """
        handler = self.get_handler(rpc_name)

        if handler is None:
            logger.error(f"RPC not found: {rpc_name}")
            raise RPCExecutionError(
                rpc_name=rpc_name,
                message=f"RPC '{rpc_name}' not registered. Available RPCs: {', '.join(self.list_rpcs())}"
            )

        try:
            # Validate parameters if handler implements validation
            if hasattr(handler, 'validate_params'):
                handler.validate_params(params)

            # Execute RPC
            logger.debug(f"Dispatching RPC: {rpc_name} with params: {params}")
            response = handler.execute(params, context)
            logger.debug(f"RPC {rpc_name} executed successfully")

            return response

        except RPCExecutionError:
            # Re-raise RPC execution errors as-is
            raise

        except Exception as e:
            logger.error(f"RPC {rpc_name} execution failed: {e}", exc_info=True)
            raise RPCExecutionError(
                rpc_name=rpc_name,
                message=f"Execution failed: {str(e)}",
                original_error=e
            )

    def list_rpcs(self) -> List[str]:
        """
        List all registered RPC names.

        Returns:
            Sorted list of RPC names
        """
        return sorted(self._handlers.keys())

    def is_registered(self, rpc_name: str) -> bool:
        """
        Check if RPC is registered.

        Args:
            rpc_name: VistA RPC name

        Returns:
            True if RPC is registered, False otherwise
        """
        return rpc_name in self._handlers

    def count(self) -> int:
        """
        Get count of registered RPCs.

        Returns:
            Number of registered handlers
        """
        return len(self._handlers)

    def unregister(self, rpc_name: str) -> bool:
        """
        Unregister an RPC handler.

        Args:
            rpc_name: VistA RPC name to unregister

        Returns:
            True if handler was unregistered, False if not found
        """
        if rpc_name in self._handlers:
            del self._handlers[rpc_name]
            logger.info(f"Unregistered handler for RPC: {rpc_name}")
            return True
        return False

    def clear(self) -> None:
        """Clear all registered handlers"""
        count = len(self._handlers)
        self._handlers.clear()
        logger.info(f"Cleared {count} RPC handlers from registry")
