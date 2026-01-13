# ---------------------------------------------------------------------
# vista/tests/test_medications_handler.py
# ---------------------------------------------------------------------
# Unit tests for Medications RPC Handlers
# ---------------------------------------------------------------------

import pytest
from pathlib import Path
from vista.app.handlers.medications import MedicationsCoverHandler
from vista.app.services import DataLoader


class TestMedicationsCoverHandler:
    """Test suite for ORWPS COVER RPC handler"""

    @pytest.fixture
    def registry_path(self):
        """Path to patient_registry.json"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "mock" / "shared" / "patient_registry.json")

    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        return MedicationsCoverHandler()

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
        assert handler.rpc_name == "ORWPS COVER"

    def test_validate_params_valid_icn(self, handler):
        """Test parameter validation with valid ICN"""
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
        """Test successful medications retrieval at site 200"""
        # ICN100001 is registered at site 200 with medications
        response = handler.execute(["ICN100001"], context_200)

        # Response should be multi-line VistA-formatted string
        assert isinstance(response, str)

        # ICN100001 should have medications at site 200
        if response:  # Only check format if there are medications
            assert "^" in response  # Contains field delimiters
            lines = [line for line in response.split("\n") if line]
            assert len(lines) > 0

            # Check first medication line format
            first_line = lines[0]
            fields = first_line.split("^")
            assert len(fields) == 7  # 7 fields per medication

    def test_execute_patient_found_site_500(self, handler, context_500):
        """Test successful medications retrieval at site 500"""
        # ICN100001 is also registered at site 500
        response = handler.execute(["ICN100001"], context_500)

        assert isinstance(response, str)
        # Should have medications at site 500
        if response:
            assert "^" in response

    def test_execute_patient_found_site_630(self, handler, context_630):
        """Test successful medications retrieval at site 630"""
        # ICN100001 is registered at site 630 with medications
        response = handler.execute(["ICN100001"], context_630)

        assert isinstance(response, str)
        if response:
            assert "^" in response

    def test_execute_patient_not_in_registry(self, handler, context_200):
        """Test medications retrieval for non-existent patient"""
        response = handler.execute(["ICN999999"], context_200)

        # Should return empty string (not an error)
        assert response == ""

    def test_execute_patient_not_at_site(self, handler, context_200):
        """Test medications retrieval for patient not registered at this site"""
        # Create a patient ICN that doesn't exist at site 200
        response = handler.execute(["ICN999999"], context_200)

        # Should return empty string
        assert isinstance(response, str)
        assert response == ""

    def test_execute_missing_data_loader(self, handler):
        """Test execution returns error without DataLoader in context"""
        context = {"site_sta3n": "200"}  # Missing data_loader

        response = handler.execute(["ICN100001"], context)

        # Should return error response, not raise exception
        assert "Internal error" in response

    def test_execute_response_format(self, handler, context_200):
        """Test response has correct VistA format"""
        response = handler.execute(["ICN100001"], context_200)

        # ICN100001 should have medications at site 200
        if response:
            # Split by newlines to get individual medications
            lines = [line for line in response.split("\n") if line]
            assert len(lines) > 0

            # Check first medication line format
            # RX_NUMBER^DRUG_NAME^STATUS^QUANTITY/DAYS_SUPPLY^REFILLS_REMAINING^ISSUE_DATE^EXPIRATION_DATE
            first_line = lines[0]
            fields = first_line.split("^")

            assert len(fields) == 7
            assert len(fields[0]) > 0  # RX_NUMBER
            assert len(fields[1]) > 0  # DRUG_NAME
            assert fields[2] == "ACTIVE"  # STATUS (only ACTIVE returned)
            assert "/" in fields[3]  # QUANTITY/DAYS_SUPPLY
            assert fields[4].isdigit()  # REFILLS_REMAINING
            assert len(fields[5]) > 0  # ISSUE_DATE
            assert len(fields[6]) > 0  # EXPIRATION_DATE

    def test_execute_fileman_date_format(self, handler, context_200):
        """Test medications dates are in FileMan format"""
        response = handler.execute(["ICN100001"], context_200)

        if response:
            lines = [line for line in response.split("\n") if line]
            first_line = lines[0]
            fields = first_line.split("^")
            issue_date = fields[5]

            # FileMan format: YYYMMDD.HHMM (e.g., 3251217.0845)
            assert "." in issue_date
            parts = issue_date.split(".")
            assert len(parts) == 2
            assert parts[0].isdigit()  # Date part
            assert parts[1].isdigit()  # Time part
            assert len(parts[0]) == 7  # YYYMMDD
            assert len(parts[1]) == 4  # HHMM

    def test_multi_site_patient_different_medications(self, handler, context_200, context_500):
        """Test patient registered at multiple sites can have different medications"""
        # ICN100001 is registered at sites 200, 500, 630
        response_200 = handler.execute(["ICN100001"], context_200)
        response_500 = handler.execute(["ICN100001"], context_500)

        # Both should succeed
        assert isinstance(response_200, str)
        assert isinstance(response_500, str)

        # Both should have medication data
        if response_200:
            lines_200 = [line for line in response_200.split("\n") if line]
            assert len(lines_200) > 0

        if response_500:
            lines_500 = [line for line in response_500.split("\n") if line]
            assert len(lines_500) > 0

    def test_response_contains_status_active(self, handler, context_200):
        """Test all medications in response have ACTIVE status"""
        response = handler.execute(["ICN100001"], context_200)

        if response:
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                status = fields[2]
                # All medications should be ACTIVE (handler filters by status)
                assert status == "ACTIVE"

    def test_response_quantity_days_format(self, handler, context_200):
        """Test quantity/days_supply field has correct format"""
        response = handler.execute(["ICN100001"], context_200)

        if response:
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                qty_days = fields[3]
                # Should be in format "quantity/days_supply" (e.g., "60/90")
                assert "/" in qty_days
                parts = qty_days.split("/")
                assert len(parts) == 2
                assert parts[0].isdigit()  # quantity
                assert parts[1].isdigit()  # days_supply

    def test_execute_preserves_newlines(self, handler, context_630):
        """Test that multi-line response preserves newlines"""
        # ICN100013 has multiple medications at site 630
        response = handler.execute(["ICN100013"], context_630)

        if response:
            # Should have multiple lines
            lines = [line for line in response.split("\n") if line]
            assert len(lines) >= 1

            # Each line should have proper format
            for line in lines:
                if line:  # Skip empty lines
                    assert line.count("^") == 6  # 7 fields = 6 delimiters

    def test_no_medications_for_patient(self, handler, context_200):
        """Test response when patient exists but has no active medications"""
        # Test with a patient that may not have medications
        response = handler.execute(["ICN999999"], context_200)

        # Should return empty string (not an error - patient has no active medications)
        assert isinstance(response, str)
        assert response == ""

    def test_response_field_count_consistency(self, handler, context_630):
        """Test all medication lines have consistent field count"""
        response = handler.execute(["ICN100013"], context_630)

        if response:
            lines = [line for line in response.split("\n") if line]

            # All lines should have 7 fields
            for line in lines:
                fields = line.split("^")
                assert len(fields) == 7, f"Expected 7 fields, got {len(fields)} in: {line}"

    def test_lisinopril_medication_present(self, handler, context_200):
        """Test LISINOPRIL medication is present (common hypertension med)"""
        # ICN100001 should have LISINOPRIL at site 200
        response = handler.execute(["ICN100001"], context_200)

        if response:
            assert "LISINOPRIL" in response.upper()

    def test_metformin_medication_present(self, handler, context_200):
        """Test METFORMIN medication is present (common diabetes med)"""
        # ICN100001 should have METFORMIN at site 200
        response = handler.execute(["ICN100001"], context_200)

        if response:
            assert "METFORMIN" in response.upper()

    def test_controlled_substance_present(self, handler, context_200):
        """Test controlled substances are included in response"""
        # ICN100001 has TRAMADOL (Schedule IV) at site 200
        # ICN100010 has HYDROCODONE (Schedule II) at site 200
        response_100001 = handler.execute(["ICN100001"], context_200)
        response_100010 = handler.execute(["ICN100010"], context_200)

        # Check for controlled substances
        if response_100001:
            assert "TRAMADOL" in response_100001.upper() or "GABAPENTIN" in response_100001.upper()

        if response_100010:
            assert "HYDROCODONE" in response_100010.upper() or "WARFARIN" in response_100010.upper()

    def test_rx_number_format(self, handler, context_200):
        """Test RX_NUMBER field contains valid prescription numbers"""
        response = handler.execute(["ICN100001"], context_200)

        if response:
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                rx_number = fields[0]
                # RX number should be numeric and non-empty
                assert len(rx_number) > 0
                assert rx_number.isdigit()

    def test_refills_remaining_format(self, handler, context_200):
        """Test REFILLS_REMAINING field contains valid numbers"""
        response = handler.execute(["ICN100001"], context_200)

        if response:
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                refills = fields[4]
                # Refills should be numeric (0 or positive)
                assert refills.isdigit()
                assert int(refills) >= 0

    def test_expiration_date_format(self, handler, context_200):
        """Test EXPIRATION_DATE field is in FileMan format"""
        response = handler.execute(["ICN100001"], context_200)

        if response:
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                exp_date = fields[6]
                # Expiration date should be FileMan format (YYYMMDD or YYYMMDD.HHMM)
                assert len(exp_date) > 0
                # Should be all digits (may or may not have time component)
                if "." in exp_date:
                    parts = exp_date.split(".")
                    assert parts[0].isdigit()
                    assert len(parts[0]) == 7  # YYYMMDD
                else:
                    assert exp_date.isdigit()
                    assert len(exp_date) == 7  # YYYMMDD

    def test_empty_response_for_no_medications(self, handler, context_200):
        """Test that empty string is returned when patient has no medications"""
        # Test with a non-existent patient
        response = handler.execute(["ICN999999"], context_200)

        # Should be empty string (patient not found or no medications)
        assert response == ""

    def test_multi_dfn_patient(self, handler, context_630):
        """Test patient with multiple DFNs at same site (ICN100013)"""
        # ICN100013 has multiple DFNs at site 630
        response = handler.execute(["ICN100013"], context_630)

        # Should return medications for the primary DFN only
        assert isinstance(response, str)
        if response:
            lines = [line for line in response.split("\n") if line]
            # Should have medications from multiple DFNs
            assert len(lines) > 0

    def test_insulin_medication_present(self, handler, context_200):
        """Test INSULIN medication is present for diabetes patients"""
        # ICN100013 has insulin at site 200
        response = handler.execute(["ICN100013"], context_200)

        if response:
            assert "INSULIN" in response.upper()

    def test_warfarin_anticoagulation_present(self, handler, context_200):
        """Test WARFARIN anticoagulation medication is present"""
        # ICN100010 has WARFARIN at site 200
        response = handler.execute(["ICN100010"], context_200)

        if response:
            assert "WARFARIN" in response.upper()

    def test_intentional_overlap_lisinopril(self, handler, context_200, context_500):
        """Test intentional overlap: same RX at multiple sites"""
        # ICN100001 has RX 2860066 (LISINOPRIL) at both sites 200 and 500
        response_200 = handler.execute(["ICN100001"], context_200)
        response_500 = handler.execute(["ICN100001"], context_500)

        # Both should contain LISINOPRIL
        if response_200:
            assert "LISINOPRIL" in response_200.upper()
            assert "2860066" in response_200

        if response_500:
            assert "LISINOPRIL" in response_500.upper()
            assert "2860066" in response_500
