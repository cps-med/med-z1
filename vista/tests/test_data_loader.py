# ---------------------------------------------------------------------
# vista/tests/test_data_loader.py
# ---------------------------------------------------------------------
# Unit tests for DataLoader service
# ---------------------------------------------------------------------

import pytest
from pathlib import Path
from vista.app.services.data_loader import DataLoader


class TestDataLoader:
    """Test suite for DataLoader ICN→DFN resolution"""

    @pytest.fixture
    def registry_path(self):
        """Path to patient_registry.json"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "mock" / "shared" / "patient_registry.json")

    def test_init_site_200(self, registry_path):
        """Test DataLoader initialization for site 200"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)
        assert loader.site_sta3n == "200"
        assert len(loader.icn_to_dfn) > 0

    def test_init_site_500(self, registry_path):
        """Test DataLoader initialization for site 500"""
        loader = DataLoader(site_sta3n="500", registry_path=registry_path)
        assert loader.site_sta3n == "500"
        assert len(loader.icn_to_dfn) > 0

    def test_init_site_630(self, registry_path):
        """Test DataLoader initialization for site 630"""
        loader = DataLoader(site_sta3n="630", registry_path=registry_path)
        assert loader.site_sta3n == "630"
        assert len(loader.icn_to_dfn) > 0

    def test_resolve_icn_to_dfn_site_200(self, registry_path):
        """Test ICN→DFN resolution for patient at site 200"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)

        # Patient ICN100001 should be registered at site 200 with DFN 100001
        dfn = loader.resolve_icn_to_dfn("ICN100001")
        assert dfn == "100001"

    def test_resolve_icn_to_dfn_site_500(self, registry_path):
        """Test ICN→DFN resolution for patient at site 500"""
        loader = DataLoader(site_sta3n="500", registry_path=registry_path)

        # Patient ICN100010 should be registered at site 500 with DFN 500010
        dfn = loader.resolve_icn_to_dfn("ICN100010")
        assert dfn == "500010"

    def test_resolve_icn_to_dfn_site_630(self, registry_path):
        """Test ICN→DFN resolution for patient at site 630"""
        loader = DataLoader(site_sta3n="630", registry_path=registry_path)

        # Patient ICN100013 should be registered at site 630 with DFN 630013
        dfn = loader.resolve_icn_to_dfn("ICN100013")
        assert dfn == "630013"

    def test_resolve_icn_not_registered(self, registry_path):
        """Test ICN→DFN resolution for patient not registered at site"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)

        # Patient ICN100013 is NOT registered at site 200 (only at site 630)
        dfn = loader.resolve_icn_to_dfn("ICN100013")
        assert dfn is None

    def test_resolve_icn_invalid(self, registry_path):
        """Test ICN→DFN resolution for non-existent patient"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)

        # Non-existent patient
        dfn = loader.resolve_icn_to_dfn("ICN999999")
        assert dfn is None

    def test_get_patient_info(self, registry_path):
        """Test retrieving full patient information"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)

        patient = loader.get_patient_info("ICN100001")
        assert patient is not None
        assert patient["icn"] == "ICN100001"
        assert patient["name_last"] == "DOOREE"
        assert patient["name_first"] == "ADAM"

    def test_get_patient_info_not_found(self, registry_path):
        """Test retrieving patient info for non-existent patient"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)

        patient = loader.get_patient_info("ICN999999")
        assert patient is None

    def test_get_registered_patients(self, registry_path):
        """Test getting list of registered patients at site"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)

        patients = loader.get_registered_patients()
        assert isinstance(patients, list)
        assert len(patients) > 0
        assert "ICN100001" in patients
        assert "ICN100010" in patients

    def test_is_patient_registered(self, registry_path):
        """Test checking if patient is registered at site"""
        loader = DataLoader(site_sta3n="200", registry_path=registry_path)

        # Patient registered at this site
        assert loader.is_patient_registered("ICN100001") is True

        # Patient NOT registered at this site
        assert loader.is_patient_registered("ICN100013") is False

        # Non-existent patient
        assert loader.is_patient_registered("ICN999999") is False

    def test_multi_site_patient(self, registry_path):
        """Test patient registered at multiple sites has different DFNs"""
        loader_200 = DataLoader(site_sta3n="200", registry_path=registry_path)
        loader_500 = DataLoader(site_sta3n="500", registry_path=registry_path)

        # Patient ICN100001 is registered at both sites with different DFNs
        dfn_200 = loader_200.resolve_icn_to_dfn("ICN100001")
        dfn_500 = loader_500.resolve_icn_to_dfn("ICN100001")

        assert dfn_200 == "100001"
        assert dfn_500 == "500001"
        assert dfn_200 != dfn_500  # Different DFNs at different sites
