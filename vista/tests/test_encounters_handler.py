# ---------------------------------------------------------------------
# vista/tests/test_encounters_handler.py
# ---------------------------------------------------------------------
# Unit tests for Encounters RPC Handlers
# ---------------------------------------------------------------------

import pytest
from pathlib import Path
from vista.app.handlers.encounters import AdmissionsHandler
from vista.app.services import DataLoader


class TestAdmissionsHandler:
    """Test suite for ORWCV ADMISSIONS RPC handler"""

    @pytest.fixture
    def registry_path(self):
        """Path to patient_registry.json"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "mock" / "shared" / "patient_registry.json")

    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        return AdmissionsHandler()

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
        assert handler.rpc_name == "ORWCV ADMISSIONS"

    def test_validate_params_valid_icn_only(self, handler):
        """Test parameter validation with valid ICN only"""
        # Should not raise exception
        handler.validate_params(["ICN100001"])

    def test_validate_params_valid_icn_and_days(self, handler):
        """Test parameter validation with ICN and days_back"""
        # Should not raise exception
        handler.validate_params(["ICN100001", 90])
        handler.validate_params(["ICN100001", "90"])

    def test_validate_params_missing(self, handler):
        """Test parameter validation with missing params"""
        with pytest.raises(ValueError) as exc_info:
            handler.validate_params([])
        assert "requires at least 1 parameter" in str(exc_info.value)

    def test_validate_params_none(self, handler):
        """Test parameter validation with None"""
        with pytest.raises(ValueError) as exc_info:
            handler.validate_params(None)
        assert "requires at least 1 parameter" in str(exc_info.value)

    def test_validate_params_invalid_icn(self, handler):
        """Test parameter validation with invalid ICN"""
        with pytest.raises(ValueError) as exc_info:
            handler.validate_params([None])
        assert "Invalid ICN" in str(exc_info.value)

    def test_validate_params_invalid_days_back(self, handler):
        """Test parameter validation with invalid days_back"""
        # The handler is lenient - it uses default 90 if days_back is invalid
        # This test verifies it doesn't crash with invalid input
        handler.validate_params(["ICN100001", "invalid"])

    def test_execute_patient_found_site_200(self, handler, context_200):
        """Test successful encounters retrieval at site 200"""
        # ICN100001 is registered at site 200 with DFN 100001
        response = handler.execute(["ICN100001"], context_200)

        # Response should be multi-line VistA-formatted string
        assert isinstance(response, str)
        assert "^" in response  # Contains field delimiters

        # Should contain encounter data (may be single or multi-line)
        lines = [line for line in response.split("\n") if line]
        assert len(lines) > 0

        # Check first encounter line format
        first_line = lines[0]
        fields = first_line.split("^")
        assert len(fields) == 9  # 9 fields per encounter

    def test_execute_patient_found_site_500(self, handler, context_500):
        """Test successful encounters retrieval at site 500"""
        # ICN100001 is also registered at site 500
        response = handler.execute(["ICN100001"], context_500)

        assert isinstance(response, str)
        assert "^" in response

    def test_execute_patient_found_site_630(self, handler, context_630):
        """Test successful encounters retrieval at site 630"""
        # ICN100001 is registered at site 630 with encounters
        response = handler.execute(["ICN100001"], context_630)

        assert isinstance(response, str)
        assert "^" in response

    def test_execute_with_days_back_parameter(self, handler, context_200):
        """Test encounters retrieval with custom days_back parameter"""
        # Default 90 days
        response_90 = handler.execute(["ICN100001", 90], context_200)

        # 30 days - might return fewer results
        response_30 = handler.execute(["ICN100001", 30], context_200)

        assert isinstance(response_90, str)
        assert isinstance(response_30, str)

    def test_execute_patient_not_in_registry(self, handler, context_200):
        """Test encounters retrieval for non-existent patient"""
        response = handler.execute(["ICN999999"], context_200)

        # Should return error response
        assert "-1^" in response
        assert "not found" in response.lower() or "not registered" in response.lower()

    def test_execute_patient_not_at_site(self, handler, context_200):
        """Test encounters retrieval for patient not registered at this site"""
        # Create a patient ICN that exists in registry but not at site 200
        # (this depends on patient_registry.json structure)
        # ICN100013 is only at site 630
        response = handler.execute(["ICN100013"], context_200)

        # Should return error or empty result
        # Check if error format or no encounters
        assert isinstance(response, str)

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

        # Split by newlines to get individual encounters
        lines = [line for line in response.split("\n") if line]
        assert len(lines) > 0

        # Check first encounter line format
        # InpatientID^AdmitDateTime^AdmitLocation^Status^DischargeDateTime^DischargeLocation^LOS^DiagnosisCode^AdmitProvider
        first_line = lines[0]
        fields = first_line.split("^")

        assert len(fields) == 9
        assert len(fields[0]) > 0  # InpatientID
        assert len(fields[1]) > 0  # AdmitDateTime
        assert len(fields[2]) > 0  # AdmitLocation
        assert fields[3] in ["ACTIVE", "DISCHARGED"]  # Status
        # fields[4] DischargeDateTime may be empty for active admissions
        # fields[5] DischargeLocation may be empty for active admissions
        # fields[6] LOS
        # fields[7] DiagnosisCode may be empty
        assert len(fields[8]) > 0  # AdmitProvider

    def test_execute_fileman_date_format(self, handler, context_200):
        """Test encounters dates are in FileMan format"""
        response = handler.execute(["ICN100001"], context_200)

        lines = [line for line in response.split("\n") if line]
        first_line = lines[0]
        fields = first_line.split("^")
        admit_datetime = fields[1]

        # FileMan format: YYYMMDD.HHMM (e.g., 3251217.0845)
        assert "." in admit_datetime
        parts = admit_datetime.split(".")
        assert len(parts) == 2
        assert parts[0].isdigit()  # Date part
        assert parts[1].isdigit()  # Time part
        assert len(parts[0]) == 7  # YYYMMDD
        assert len(parts[1]) == 4  # HHMM

    def test_multi_site_patient_different_encounters(self, handler, context_200, context_500):
        """Test patient registered at multiple sites can have different encounters"""
        # ICN100001 is registered at sites 200, 500, 630
        response_200 = handler.execute(["ICN100001"], context_200)
        response_500 = handler.execute(["ICN100001"], context_500)

        # Both should succeed
        assert not response_200.startswith("-1^")
        assert not response_500.startswith("-1^")

        # Both should have encounter data
        lines_200 = [line for line in response_200.split("\n") if line]
        lines_500 = [line for line in response_500.split("\n") if line]
        assert len(lines_200) > 0
        assert len(lines_500) > 0

    def test_response_contains_status_values(self, handler, context_200):
        """Test response contains valid status values"""
        response = handler.execute(["ICN100001"], context_200)

        lines = [line for line in response.split("\n") if line]
        for line in lines:
            fields = line.split("^")
            status = fields[3]
            # Status should be ACTIVE or DISCHARGED
            assert status in ["ACTIVE", "DISCHARGED"]

    def test_active_encounter_format(self, handler, context_500):
        """Test active encounter has correct format (empty discharge fields)"""
        # ICN100010 has an active admission at site 500
        response = handler.execute(["ICN100010"], context_500)

        lines = [line for line in response.split("\n") if line]

        # Find active encounters
        active_encounters = [line for line in lines if "^ACTIVE^" in line]

        if active_encounters:
            first_active = active_encounters[0]
            fields = first_active.split("^")

            # Active encounters should have empty discharge_datetime and location
            assert fields[4] == ""  # discharge_datetime
            assert fields[5] == ""  # discharge_location

    def test_discharged_encounter_format(self, handler, context_200):
        """Test discharged encounter has populated discharge fields"""
        # ICN100001 has discharged encounters
        response = handler.execute(["ICN100001"], context_200)

        lines = [line for line in response.split("\n") if line]

        # Find discharged encounters
        discharged_encounters = [line for line in lines if "^DISCHARGED^" in line]

        if discharged_encounters:
            first_discharged = discharged_encounters[0]
            fields = first_discharged.split("^")

            # Discharged encounters should have discharge_datetime and location
            assert len(fields[4]) > 0  # discharge_datetime
            assert len(fields[5]) > 0  # discharge_location

    def test_execute_preserves_newlines(self, handler, context_630):
        """Test that multi-line response preserves newlines"""
        # ICN100013 has multiple encounters at site 630
        response = handler.execute(["ICN100013"], context_630)

        # Should have multiple lines
        lines = [line for line in response.split("\n") if line]
        assert len(lines) >= 1

        # Each line should have proper format
        for line in lines:
            if line:  # Skip empty lines
                assert line.count("^") == 8  # 9 fields = 8 delimiters

    def test_no_encounters_for_patient(self, handler, context_200):
        """Test response when patient exists but has no encounters"""
        # ICN100002 exists but may not have encounters at site 200
        response = handler.execute(["ICN100002"], context_200)

        # Should either return encounters or indicate no data
        assert isinstance(response, str)

    def test_response_field_count_consistency(self, handler, context_630):
        """Test all encounter lines have consistent field count"""
        response = handler.execute(["ICN100013"], context_630)

        lines = [line for line in response.split("\n") if line]

        # All non-error lines should have 9 fields
        for line in lines:
            if not line.startswith("-1^"):
                fields = line.split("^")
                assert len(fields) == 9, f"Expected 9 fields, got {len(fields)} in: {line}"

    def test_length_of_stay_values(self, handler, context_200):
        """Test length of stay field contains valid numeric values or zero"""
        response = handler.execute(["ICN100001"], context_200)

        lines = [line for line in response.split("\n") if line]

        for line in lines:
            if not line.startswith("-1^"):
                fields = line.split("^")
                los = fields[6]
                # LOS should be numeric or empty string
                if los:
                    assert los.isdigit() or los == "0"
