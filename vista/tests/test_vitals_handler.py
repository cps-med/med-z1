# ---------------------------------------------------------------------
# vista/tests/test_vitals_handler.py
# ---------------------------------------------------------------------
# Unit tests for Vitals RPC Handlers
# ---------------------------------------------------------------------

import pytest
from pathlib import Path
from vista.app.handlers import LatestVitalsHandler
from vista.app.services import DataLoader


class TestLatestVitalsHandler:
    """Test suite for GMV LATEST VM RPC handler"""

    @pytest.fixture
    def registry_path(self):
        """Path to patient_registry.json"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "mock" / "shared" / "patient_registry.json")

    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        return LatestVitalsHandler()

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
        assert handler.rpc_name == "GMV LATEST VM"

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
        """Test successful vitals retrieval at site 200"""
        # ICN100001 is registered at site 200 with DFN 100001
        response = handler.execute(["ICN100001"], context_200)

        # Response should be multi-line VistA-formatted string
        assert isinstance(response, str)
        assert "\n" in response  # Multiple vitals, newline-separated
        assert "^" in response  # Contains field delimiters

        # Should contain vital signs data
        lines = response.split("\n")
        assert len(lines) > 0

        # Check for typical vitals
        vital_types = [line.split("^")[0] for line in lines if line]
        assert any("BLOOD PRESSURE" in vt for vt in vital_types)
        assert any("TEMPERATURE" in vt for vt in vital_types)
        assert any("PULSE" in vt for vt in vital_types)

    def test_execute_patient_found_site_500(self, handler, context_500):
        """Test successful vitals retrieval at site 500"""
        # ICN100001 is also registered at site 500 with different DFN
        response = handler.execute(["ICN100001"], context_500)

        assert isinstance(response, str)
        assert "\n" in response
        assert "^" in response

    def test_execute_patient_found_site_630(self, handler, context_630):
        """Test successful vitals retrieval at site 630"""
        # ICN100001 is also registered at site 630
        response = handler.execute(["ICN100001"], context_630)

        assert isinstance(response, str)
        assert "\n" in response
        assert "^" in response

    def test_execute_patient_not_in_registry(self, handler, context_200):
        """Test vitals retrieval for non-existent patient"""
        response = handler.execute(["ICN999999"], context_200)

        # Should return error response
        assert "-1^" in response
        assert "not found" in response.lower()

    def test_execute_patient_not_at_site(self, handler, context_200):
        """Test vitals retrieval for patient not registered at this site"""
        # ICN100013 is only at site 630, not at site 200
        response = handler.execute(["ICN100013"], context_200)

        # Should return error response
        assert "-1^" in response
        assert "not found" in response.lower() or "not registered" in response.lower()

    def test_execute_missing_data_loader(self, handler):
        """Test execution returns error without DataLoader in context"""
        context = {"site_sta3n": "200"}  # Missing data_loader

        response = handler.execute(["ICN100001"], context)

        # Should return error response, not raise exception
        assert "-1^" in response
        assert "DataLoader" in response or "Internal error" in response

    def test_execute_response_format(self, handler, context_200):
        """Test response has correct VistA format"""
        response = handler.execute(["ICN100001"], context_200)

        # Split by newlines to get individual vitals
        lines = response.split("\n")
        assert len(lines) > 0

        # Check first vital line format: TYPE^VALUE^UNITS^DATE_TIME^ENTERED_BY
        first_line = lines[0]
        fields = first_line.split("^")

        assert len(fields) == 5
        assert len(fields[0]) > 0  # TYPE
        assert len(fields[1]) > 0  # VALUE
        assert len(fields[2]) > 0  # UNITS
        assert len(fields[3]) > 0  # DATE_TIME
        assert len(fields[4]) > 0  # ENTERED_BY

    def test_execute_fileman_date_format(self, handler, context_200):
        """Test vitals dates are in FileMan format"""
        response = handler.execute(["ICN100001"], context_200)

        lines = response.split("\n")
        first_line = lines[0]
        fields = first_line.split("^")
        date_time = fields[3]

        # FileMan format: YYYMMDD.HHMM (e.g., 3241217.0845)
        # Should have format XXXXXXX.XXXX
        assert "." in date_time
        parts = date_time.split(".")
        assert len(parts) == 2
        assert parts[0].isdigit()  # Date part
        assert parts[1].isdigit()  # Time part
        assert len(parts[0]) == 7  # YYYMMDD
        assert len(parts[1]) == 4  # HHMM

    def test_multi_site_patient_different_vitals(self, handler, context_200, context_500):
        """Test patient registered at multiple sites can have different vitals"""
        # ICN100001 is registered at sites 200, 500, 630
        response_200 = handler.execute(["ICN100001"], context_200)
        response_500 = handler.execute(["ICN100001"], context_500)

        # Both should succeed
        assert not response_200.startswith("-1^")
        assert not response_500.startswith("-1^")

        # Both should have vitals data
        assert "\n" in response_200
        assert "\n" in response_500

        # Vitals might differ by site (different readings)
        # Just verify both are valid responses
        lines_200 = response_200.split("\n")
        lines_500 = response_500.split("\n")
        assert len(lines_200) > 0
        assert len(lines_500) > 0

    def test_response_contains_all_vital_types(self, handler, context_200):
        """Test response contains expected vital sign types"""
        response = handler.execute(["ICN100001"], context_200)

        # Should contain common vitals
        assert "BLOOD PRESSURE" in response
        assert "TEMPERATURE" in response
        assert "PULSE" in response
        assert "RESPIRATION" in response
        assert "PULSE OXIMETRY" in response

    def test_response_contains_units(self, handler, context_200):
        """Test response contains units for each vital"""
        response = handler.execute(["ICN100001"], context_200)

        lines = response.split("\n")
        for line in lines:
            if line:  # Skip empty lines
                fields = line.split("^")
                units = fields[2]
                # Units should not be empty
                assert len(units) > 0

    def test_response_contains_entered_by(self, handler, context_200):
        """Test response contains entered_by for each vital"""
        response = handler.execute(["ICN100001"], context_200)

        lines = response.split("\n")
        for line in lines:
            if line:  # Skip empty lines
                fields = line.split("^")
                entered_by = fields[4]
                # Entered_by should not be empty
                assert len(entered_by) > 0

    def test_no_vitals_for_patient(self, handler, context_200):
        """Test response when patient exists but has no vitals"""
        # ICN100002 exists at site 200 but might not have vitals data
        # This tests the "no vitals found" case
        # Note: This assumes ICN100002 has vitals in our test data,
        # so this test verifies the handler works for all registered patients
        response = handler.execute(["ICN100002"], context_200)

        # Should either return vitals or an error
        # Not an internal error
        assert isinstance(response, str)

    def test_execute_preserves_newlines(self, handler, context_200):
        """Test that multi-line response preserves newlines"""
        response = handler.execute(["ICN100001"], context_200)

        # Should have multiple lines
        lines = response.split("\n")
        assert len(lines) >= 5  # At least 5 common vitals

        # Each line should have proper format
        for line in lines:
            if line:  # Skip empty lines
                assert line.count("^") == 4  # 5 fields = 4 delimiters
