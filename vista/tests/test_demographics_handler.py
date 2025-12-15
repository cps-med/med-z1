# ---------------------------------------------------------------------
# vista/tests/test_demographics_handler.py
# ---------------------------------------------------------------------
# Unit tests for Demographics RPC Handlers
# ---------------------------------------------------------------------

import pytest
from pathlib import Path
from vista.app.handlers import PatientInquiryHandler
from vista.app.services import RPCExecutionError, DataLoader


class TestPatientInquiryHandler:
    """Test suite for ORWPT PTINQ RPC handler"""

    @pytest.fixture
    def registry_path(self):
        """Path to patient_registry.json"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "mock" / "shared" / "patient_registry.json")

    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        return PatientInquiryHandler()

    @pytest.fixture
    def data_loader_200(self, registry_path):
        """Create DataLoader for site 200"""
        return DataLoader(site_sta3n="200", registry_path=registry_path)

    @pytest.fixture
    def data_loader_500(self, registry_path):
        """Create DataLoader for site 500"""
        return DataLoader(site_sta3n="500", registry_path=registry_path)

    @pytest.fixture
    def data_loader_630(self, registry_path):
        """Create DataLoader for site 630"""
        return DataLoader(site_sta3n="630", registry_path=registry_path)

    @pytest.fixture
    def context_200(self, data_loader_200):
        """Create context for site 200"""
        return {
            "data_loader": data_loader_200,
            "site_sta3n": "200"
        }

    @pytest.fixture
    def context_500(self, data_loader_500):
        """Create context for site 500"""
        return {
            "data_loader": data_loader_500,
            "site_sta3n": "500"
        }

    @pytest.fixture
    def context_630(self, data_loader_630):
        """Create context for site 630"""
        return {
            "data_loader": data_loader_630,
            "site_sta3n": "630"
        }

    def test_handler_rpc_name(self, handler):
        """Test handler reports correct RPC name"""
        assert handler.rpc_name == "ORWPT PTINQ"

    def test_validate_params_valid(self, handler):
        """Test parameter validation with valid params"""
        # Should not raise exception
        handler.validate_params(["ICN100001"])

    def test_validate_params_missing(self, handler):
        """Test parameter validation with missing params"""
        with pytest.raises(ValueError) as exc_info:
            handler.validate_params([])
        assert "requires 1 parameter" in str(exc_info.value)

    def test_validate_params_none(self, handler):
        """Test parameter validation with None"""
        with pytest.raises(ValueError) as exc_info:
            handler.validate_params(None)
        assert "requires 1 parameter" in str(exc_info.value)

    def test_validate_params_invalid_icn(self, handler):
        """Test parameter validation with invalid ICN"""
        with pytest.raises(ValueError) as exc_info:
            handler.validate_params([None])
        assert "Invalid ICN" in str(exc_info.value)

    def test_execute_patient_found_site_200(self, handler, context_200):
        """Test successful patient inquiry at site 200"""
        # ICN100001 is registered at site 200
        response = handler.execute(["ICN100001"], context_200)

        # Response should be VistA-formatted string
        assert isinstance(response, str)
        assert "^" in response  # Contains field delimiters

        # Should contain patient data
        assert "DOOREE" in response.upper()
        assert "ADAM" in response.upper()

    def test_execute_patient_found_site_500(self, handler, context_500):
        """Test successful patient inquiry at site 500"""
        # ICN100010 is registered at site 500
        response = handler.execute(["ICN100010"], context_500)

        assert isinstance(response, str)
        assert "^" in response
        assert "AMINOR" in response.upper()

    def test_execute_patient_found_site_630(self, handler, context_630):
        """Test successful patient inquiry at site 630"""
        # ICN100013 is registered at site 630
        response = handler.execute(["ICN100013"], context_630)

        assert isinstance(response, str)
        assert "^" in response
        assert "THOMPSON" in response.upper()

    def test_execute_patient_not_in_registry(self, handler, context_200):
        """Test patient inquiry for non-existent patient"""
        response = handler.execute(["ICN999999"], context_200)

        # Should return error response
        assert "-1^" in response
        assert "not found" in response.lower()

    def test_execute_patient_not_at_site(self, handler, context_200):
        """Test patient inquiry for patient not registered at this site"""
        # ICN100013 is only at site 630, not at site 200
        response = handler.execute(["ICN100013"], context_200)

        # Should return error response
        assert "-1^" in response
        assert "not registered" in response.lower()

    def test_execute_missing_data_loader(self, handler):
        """Test execution fails without DataLoader in context"""
        context = {"site_sta3n": "200"}  # Missing data_loader

        with pytest.raises(RPCExecutionError) as exc_info:
            handler.execute(["ICN100001"], context)

        assert "DataLoader not available" in str(exc_info.value)

    def test_execute_multi_site_patient(self, handler, context_200, context_500):
        """Test patient registered at multiple sites returns correct data"""
        # ICN100001 is registered at sites 200, 500, 630
        response_200 = handler.execute(["ICN100001"], context_200)
        response_500 = handler.execute(["ICN100001"], context_500)

        # Both should succeed
        assert "DOOREE" in response_200.upper()
        assert "DOOREE" in response_500.upper()

        # Both should be valid responses (not errors)
        assert not response_200.startswith("-1^")
        assert not response_500.startswith("-1^")

    def test_execute_response_format(self, handler, context_200):
        """Test response has correct VistA format"""
        response = handler.execute(["ICN100001"], context_200)

        # Split by caret to check format
        fields = response.split("^")

        # Should have 5 fields: NAME^SSN^DOB^SEX^VETERAN_STATUS
        assert len(fields) == 5

        # Field 1: Name (should contain comma)
        assert "," in fields[0]

        # Field 2: SSN (should be formatted)
        assert len(fields[1]) > 0

        # Field 3: DOB (should be FileMan format - 7 digits)
        # Format: YYYMMDD where YYY = year - 1700
        dob = fields[2]
        if dob:  # May be empty if no DOB
            assert len(dob) == 7
            assert dob.isdigit()

        # Field 4: Sex (M or F)
        assert fields[3] in ["M", "F", ""]

        # Field 5: Veteran status
        assert len(fields[4]) > 0

    def test_execute_fileman_date_format(self, handler, context_200):
        """Test DOB is converted to FileMan format"""
        response = handler.execute(["ICN100001"], context_200)
        fields = response.split("^")
        dob_fileman = fields[2]

        # ICN100001 has DOB 1980-01-02
        # FileMan: 1980 - 1700 = 280, so 2800102
        assert dob_fileman == "2800102"

    def test_response_contains_all_fields(self, handler, context_200):
        """Test response contains all required demographic fields"""
        response = handler.execute(["ICN100001"], context_200)

        # Should contain name
        assert "DOOREE" in response.upper() or "ADAM" in response.upper()

        # Should contain SSN (check for hyphen or digits)
        assert any(char.isdigit() for char in response)

        # Should contain sex indicator
        assert "M" in response or "F" in response

    def test_invalid_params_raises_execution_error(self, handler, context_200):
        """Test that invalid params raise RPCExecutionError"""
        # Empty params should fail validation and raise RPCExecutionError
        with pytest.raises((ValueError, RPCExecutionError)):
            handler.execute([], context_200)
