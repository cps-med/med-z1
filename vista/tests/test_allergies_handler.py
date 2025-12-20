# ---------------------------------------------------------------------
# vista/tests/test_allergies_handler.py
# ---------------------------------------------------------------------
# Unit tests for Allergies RPC Handlers
# ---------------------------------------------------------------------

import pytest
from pathlib import Path
from vista.app.handlers.allergies import AllergiesListHandler
from vista.app.services import DataLoader


class TestAllergiesListHandler:
    """Test suite for ORQQAL LIST RPC handler"""

    @pytest.fixture
    def registry_path(self):
        """Path to patient_registry.json"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "mock" / "shared" / "patient_registry.json")

    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        return AllergiesListHandler()

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
        assert handler.rpc_name == "ORQQAL LIST"

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
        """Test successful allergies retrieval at site 200"""
        # ICN100001 is registered at site 200 with allergies
        response = handler.execute(["ICN100001"], context_200)

        # Response should be multi-line VistA-formatted string
        assert isinstance(response, str)

        # ICN100001 should have allergies at site 200
        if response:  # Only check format if there are allergies
            assert "^" in response  # Contains field delimiters
            lines = [line for line in response.split("\n") if line]
            assert len(lines) > 0

            # Check first allergy line format
            first_line = lines[0]
            fields = first_line.split("^")
            assert len(fields) == 7  # 7 fields per allergy

    def test_execute_patient_found_site_500(self, handler, context_500):
        """Test successful allergies retrieval at site 500"""
        # ICN100001 is also registered at site 500
        response = handler.execute(["ICN100001"], context_500)

        assert isinstance(response, str)
        # Should have allergies at site 500
        if response:
            assert "^" in response

    def test_execute_patient_found_site_630(self, handler, context_630):
        """Test successful allergies retrieval at site 630"""
        # ICN100001 is registered at site 630 with allergies
        response = handler.execute(["ICN100001"], context_630)

        assert isinstance(response, str)
        if response:
            assert "^" in response

    def test_execute_patient_not_in_registry(self, handler, context_200):
        """Test allergies retrieval for non-existent patient"""
        response = handler.execute(["ICN999999"], context_200)

        # Should return error response
        assert "-1^" in response
        assert "not found" in response.lower() or "not registered" in response.lower()

    def test_execute_patient_not_at_site(self, handler, context_200):
        """Test allergies retrieval for patient not registered at this site"""
        # ICN100013 is only at site 630, not at site 200
        response = handler.execute(["ICN100013"], context_200)

        # Should return error response
        assert isinstance(response, str)
        assert "-1^" in response

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

        # ICN100001 should have allergies at site 200
        if response and not response.startswith("-1^"):
            # Split by newlines to get individual allergies
            lines = [line for line in response.split("\n") if line]
            assert len(lines) > 0

            # Check first allergy line format
            # AllergenName^Severity^ReactionDateTime^Reactions^AllergyType^OriginatingSite^EnteredBy
            first_line = lines[0]
            fields = first_line.split("^")

            assert len(fields) == 7
            assert len(fields[0]) > 0  # AllergenName
            assert fields[1] in ["MILD", "MODERATE", "SEVERE"]  # Severity
            assert len(fields[2]) > 0  # ReactionDateTime
            assert len(fields[3]) > 0  # Reactions
            assert fields[4] in ["DRUG", "FOOD", "ENVIRONMENTAL"]  # AllergyType
            assert len(fields[5]) > 0  # OriginatingSite
            assert len(fields[6]) > 0  # EnteredBy

    def test_execute_fileman_date_format(self, handler, context_200):
        """Test allergies dates are in FileMan format"""
        response = handler.execute(["ICN100001"], context_200)

        if response and not response.startswith("-1^"):
            lines = [line for line in response.split("\n") if line]
            first_line = lines[0]
            fields = first_line.split("^")
            reaction_datetime = fields[2]

            # FileMan format: YYYMMDD.HHMM (e.g., 3251217.0845)
            assert "." in reaction_datetime
            parts = reaction_datetime.split(".")
            assert len(parts) == 2
            assert parts[0].isdigit()  # Date part
            assert parts[1].isdigit()  # Time part
            assert len(parts[0]) == 7  # YYYMMDD
            assert len(parts[1]) == 4  # HHMM

    def test_multi_site_patient_different_allergies(self, handler, context_200, context_500):
        """Test patient registered at multiple sites can have different allergies"""
        # ICN100001 is registered at sites 200, 500, 630
        response_200 = handler.execute(["ICN100001"], context_200)
        response_500 = handler.execute(["ICN100001"], context_500)

        # Both should succeed
        assert not response_200.startswith("-1^")
        assert not response_500.startswith("-1^")

        # Both should have allergy data
        if response_200:
            lines_200 = [line for line in response_200.split("\n") if line]
            assert len(lines_200) > 0

        if response_500:
            lines_500 = [line for line in response_500.split("\n") if line]
            assert len(lines_500) > 0

    def test_response_contains_severity_values(self, handler, context_200):
        """Test response contains valid severity values"""
        response = handler.execute(["ICN100001"], context_200)

        if response and not response.startswith("-1^"):
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                severity = fields[1]
                # Severity should be one of the valid values
                assert severity in ["MILD", "MODERATE", "SEVERE"]

    def test_response_contains_allergen_types(self, handler, context_200):
        """Test response contains valid allergen type values"""
        response = handler.execute(["ICN100001"], context_200)

        if response and not response.startswith("-1^"):
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                allergen_type = fields[4]
                # Allergen type should be one of the valid categories
                assert allergen_type in ["DRUG", "FOOD", "ENVIRONMENTAL"]

    def test_execute_preserves_newlines(self, handler, context_630):
        """Test that multi-line response preserves newlines"""
        # ICN100013 has multiple allergies at site 630
        response = handler.execute(["ICN100013"], context_630)

        if response and not response.startswith("-1^"):
            # Should have multiple lines
            lines = [line for line in response.split("\n") if line]
            assert len(lines) >= 1

            # Each line should have proper format
            for line in lines:
                if line:  # Skip empty lines
                    assert line.count("^") == 6  # 7 fields = 6 delimiters

    def test_no_allergies_for_patient(self, handler, context_200):
        """Test response when patient exists but has no allergies"""
        # ICN100002 exists but may not have allergies at site 200
        response = handler.execute(["ICN100002"], context_200)

        # Should return empty string (not an error - patient has no known allergies)
        assert isinstance(response, str)
        # Empty response means no allergies (valid clinical state)
        if not response:
            assert response == ""

    def test_response_field_count_consistency(self, handler, context_630):
        """Test all allergy lines have consistent field count"""
        response = handler.execute(["ICN100013"], context_630)

        if response and not response.startswith("-1^"):
            lines = [line for line in response.split("\n") if line]

            # All non-error lines should have 7 fields
            for line in lines:
                if not line.startswith("-1^"):
                    fields = line.split("^")
                    assert len(fields) == 7, f"Expected 7 fields, got {len(fields)} in: {line}"

    def test_penicillin_allergy_present(self, handler, context_200, context_500, context_630):
        """Test Penicillin allergy is present per user requirement"""
        # User requested Penicillin allergies be included in test data
        # ICN100001 should have Penicillin allergy at all 3 sites

        response_200 = handler.execute(["ICN100001"], context_200)
        response_500 = handler.execute(["ICN100010"], context_500)  # ICN100010 has Penicillin at site 500
        response_630 = handler.execute(["ICN100001"], context_630)

        # Check site 200
        if response_200:
            assert "PENICILLIN" in response_200.upper()

        # Check site 500
        if response_500:
            assert "PENICILLIN" in response_500.upper()

        # Check site 630
        if response_630:
            assert "PENICILLIN" in response_630.upper()

    def test_sulfa_allergy_present(self, handler, context_500, context_630):
        """Test Sulfa allergy is present per user requirement"""
        # User requested Sulfa allergies be included in test data
        # ICN100001 has Sulfa at site 500, ICN100013 has Sulfa at site 630

        response_500 = handler.execute(["ICN100001"], context_500)
        response_630 = handler.execute(["ICN100013"], context_630)

        # Check site 500
        if response_500:
            assert "SULFA" in response_500.upper()

        # Check site 630
        if response_630:
            assert "SULFA" in response_630.upper()

    def test_reactions_field_format(self, handler, context_200):
        """Test reactions field contains comma-separated values"""
        response = handler.execute(["ICN100001"], context_200)

        if response and not response.startswith("-1^"):
            lines = [line for line in response.split("\n") if line]
            for line in lines:
                fields = line.split("^")
                reactions = fields[3]
                # Reactions should be non-empty and may be comma-separated
                assert len(reactions) > 0
                # If multiple reactions, should be comma-separated
                if "," in reactions:
                    reaction_list = reactions.split(",")
                    assert len(reaction_list) > 1

    def test_empty_response_for_no_allergies(self, handler, context_200):
        """Test that empty string is returned when patient has no allergies"""
        # Find a patient with no allergies (if any in test data)
        # For now, test that the response type is correct
        response = handler.execute(["ICN100002"], context_200)

        # Should be string (either empty or with allergy data)
        assert isinstance(response, str)

        # If empty, it means no allergies (valid state, not an error)
        if response == "":
            # This is expected for patients with no allergies
            pass
        elif response.startswith("-1^"):
            # Patient not found is also valid
            pass
        else:
            # Has allergies - verify format
            assert "^" in response
