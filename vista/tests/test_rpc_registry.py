# ---------------------------------------------------------------------
# vista/tests/test_rpc_registry.py
# ---------------------------------------------------------------------
# Unit tests for RPC Registry and Handler infrastructure
# ---------------------------------------------------------------------

import pytest
from typing import Any, Dict, List
from vista.app.services import RPCHandler, RPCRegistry, RPCExecutionError


# Mock RPC Handler for testing
class MockPatientHandler(RPCHandler):
    """Mock handler for patient inquiry RPC"""

    @property
    def rpc_name(self) -> str:
        return "ORWPT PTINQ"

    def execute(self, params: List[Any], context: Dict[str, Any]) -> Any:
        icn = params[0]
        return f"PATIENT^{icn}^DOE,JOHN^19450315^M"


class MockVitalsHandler(RPCHandler):
    """Mock handler for vitals RPC"""

    @property
    def rpc_name(self) -> str:
        return "GMV LATEST VM"

    def execute(self, params: List[Any], context: Dict[str, Any]) -> Any:
        return ["120/80^BLOOD PRESSURE", "98.6^TEMPERATURE"]


class MockFailingHandler(RPCHandler):
    """Mock handler that always fails"""

    @property
    def rpc_name(self) -> str:
        return "FAILING RPC"

    def execute(self, params: List[Any], context: Dict[str, Any]) -> Any:
        raise ValueError("Intentional failure for testing")


class TestRPCHandler:
    """Test suite for RPCHandler base class"""

    def test_handler_has_rpc_name(self):
        """Test that handler exposes rpc_name property"""
        handler = MockPatientHandler()
        assert handler.rpc_name == "ORWPT PTINQ"

    def test_handler_can_execute(self):
        """Test that handler can execute with parameters"""
        handler = MockPatientHandler()
        response = handler.execute(["ICN100001"], {})
        assert "ICN100001" in response
        assert "PATIENT" in response


class TestRPCRegistry:
    """Test suite for RPC Registry"""

    @pytest.fixture
    def registry(self):
        """Create fresh registry for each test"""
        return RPCRegistry()

    @pytest.fixture
    def patient_handler(self):
        """Create patient handler instance"""
        return MockPatientHandler()

    @pytest.fixture
    def vitals_handler(self):
        """Create vitals handler instance"""
        return MockVitalsHandler()

    def test_registry_initialization(self, registry):
        """Test registry initializes empty"""
        assert registry.count() == 0
        assert registry.list_rpcs() == []

    def test_register_handler(self, registry, patient_handler):
        """Test registering a handler"""
        registry.register(patient_handler)
        assert registry.count() == 1
        assert registry.is_registered("ORWPT PTINQ")

    def test_register_multiple_handlers(self, registry, patient_handler, vitals_handler):
        """Test registering multiple handlers"""
        registry.register(patient_handler)
        registry.register(vitals_handler)

        assert registry.count() == 2
        assert registry.is_registered("ORWPT PTINQ")
        assert registry.is_registered("GMV LATEST VM")

    def test_list_rpcs(self, registry, patient_handler, vitals_handler):
        """Test listing all registered RPCs"""
        registry.register(patient_handler)
        registry.register(vitals_handler)

        rpcs = registry.list_rpcs()
        assert len(rpcs) == 2
        assert "ORWPT PTINQ" in rpcs
        assert "GMV LATEST VM" in rpcs
        assert rpcs == sorted(rpcs)  # Should be sorted

    def test_get_handler(self, registry, patient_handler):
        """Test retrieving handler by RPC name"""
        registry.register(patient_handler)

        handler = registry.get_handler("ORWPT PTINQ")
        assert handler is not None
        assert handler.rpc_name == "ORWPT PTINQ"

    def test_get_handler_not_found(self, registry):
        """Test retrieving non-existent handler"""
        handler = registry.get_handler("NONEXISTENT RPC")
        assert handler is None

    def test_is_registered(self, registry, patient_handler):
        """Test checking if RPC is registered"""
        assert not registry.is_registered("ORWPT PTINQ")

        registry.register(patient_handler)
        assert registry.is_registered("ORWPT PTINQ")

    def test_dispatch_success(self, registry, patient_handler):
        """Test successful RPC dispatch"""
        registry.register(patient_handler)

        response = registry.dispatch(
            rpc_name="ORWPT PTINQ",
            params=["ICN100001"],
            context={"site_sta3n": "200"}
        )

        assert response is not None
        assert "ICN100001" in response

    def test_dispatch_not_found(self, registry):
        """Test dispatching non-existent RPC"""
        with pytest.raises(RPCExecutionError) as exc_info:
            registry.dispatch(
                rpc_name="NONEXISTENT RPC",
                params=[],
                context={}
            )

        assert "not registered" in str(exc_info.value)

    def test_dispatch_handler_failure(self, registry):
        """Test dispatching RPC that fails during execution"""
        failing_handler = MockFailingHandler()
        registry.register(failing_handler)

        with pytest.raises(RPCExecutionError) as exc_info:
            registry.dispatch(
                rpc_name="FAILING RPC",
                params=[],
                context={}
            )

        assert "Execution failed" in str(exc_info.value)
        assert exc_info.value.original_error is not None

    def test_unregister_handler(self, registry, patient_handler):
        """Test unregistering a handler"""
        registry.register(patient_handler)
        assert registry.is_registered("ORWPT PTINQ")

        result = registry.unregister("ORWPT PTINQ")
        assert result is True
        assert not registry.is_registered("ORWPT PTINQ")
        assert registry.count() == 0

    def test_unregister_not_found(self, registry):
        """Test unregistering non-existent handler"""
        result = registry.unregister("NONEXISTENT RPC")
        assert result is False

    def test_clear_registry(self, registry, patient_handler, vitals_handler):
        """Test clearing all handlers"""
        registry.register(patient_handler)
        registry.register(vitals_handler)
        assert registry.count() == 2

        registry.clear()
        assert registry.count() == 0
        assert registry.list_rpcs() == []

    def test_overwrite_handler_warning(self, registry, patient_handler):
        """Test that re-registering same RPC overwrites previous handler"""
        registry.register(patient_handler)
        assert registry.count() == 1

        # Register another handler with same RPC name
        another_handler = MockPatientHandler()
        registry.register(another_handler)

        # Should still have only 1 handler (overwrote previous)
        assert registry.count() == 1
        assert registry.is_registered("ORWPT PTINQ")

    def test_invalid_handler_registration(self, registry):
        """Test registering invalid handler raises error"""
        with pytest.raises(ValueError):
            registry.register("not a handler")


class TestRPCExecutionError:
    """Test suite for RPCExecutionError"""

    def test_error_construction(self):
        """Test creating RPCExecutionError"""
        error = RPCExecutionError(
            rpc_name="TEST RPC",
            message="Something went wrong"
        )

        assert error.rpc_name == "TEST RPC"
        assert error.message == "Something went wrong"
        assert "TEST RPC" in str(error)
        assert "Something went wrong" in str(error)

    def test_error_with_original_exception(self):
        """Test RPCExecutionError wrapping original exception"""
        original = ValueError("Original error")
        error = RPCExecutionError(
            rpc_name="TEST RPC",
            message="Wrapper message",
            original_error=original
        )

        assert error.original_error is original
        assert isinstance(error.original_error, ValueError)
