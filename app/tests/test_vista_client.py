# ---------------------------------------------------------------------
# app/tests/test_vista_client.py
# ---------------------------------------------------------------------
# Unit Tests for VistA Client Site Selection Logic
# Tests intelligent site selection, T-notation parsing, domain limits
# ---------------------------------------------------------------------

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from app.services.vista_client import (
    VistaClient,
    DOMAIN_SITE_LIMITS,
    MAX_SITES_ABSOLUTE,
)


@pytest.fixture
def mock_patient_registry():
    """Mock patient registry with test data"""
    return {
        "patients": [
            {
                "icn": "ICN100001",
                "treating_facilities": [
                    {
                        "sta3n": "200",
                        "name": "ALEXANDRIA",
                        "dfn": "100001",
                        "last_seen": "T-7"  # Most recent
                    },
                    {
                        "sta3n": "500",
                        "name": "ANCHORAGE",
                        "dfn": "500001",
                        "last_seen": "T-30"  # Second most recent
                    },
                    {
                        "sta3n": "630",
                        "name": "PALO_ALTO",
                        "dfn": "630001",
                        "last_seen": "T-90"  # Oldest
                    },
                    {
                        "sta3n": "402",
                        "name": "TOGUS",
                        "dfn": "402001",
                        "last_seen": "T-365"  # Very old
                    },
                    {
                        "sta3n": "405",
                        "name": "WHITE_RIVER_JUNCTION",
                        "dfn": "405001",
                        "last_seen": "T-730"  # Ancient
                    }
                ]
            },
            {
                "icn": "ICN100013",
                "treating_facilities": [
                    {
                        "sta3n": "630",
                        "name": "PALO_ALTO",
                        "dfn": "630013",
                        "last_seen": "T-0"  # Today
                    }
                ]
            },
            {
                "icn": "ICN_MANY_SITES",
                "treating_facilities": [
                    {"sta3n": f"{i:03d}", "dfn": f"{i}001", "last_seen": f"T-{i}"}
                    for i in range(15)  # 15 sites to test hard limit
                ]
            }
        ]
    }


@pytest.fixture
def vista_client(mock_patient_registry):
    """Create VistaClient with mocked patient registry"""
    with patch.object(VistaClient, '_load_patient_registry', return_value=mock_patient_registry):
        client = VistaClient()
        return client


class TestTNotationParsing:
    """Test T-notation date parsing (_parse_t_notation)"""

    def test_parse_t_zero_today(self, vista_client):
        """Test T-0 parses to today"""
        result = vista_client._parse_t_notation("T-0")
        expected = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        actual = result.replace(hour=0, minute=0, second=0, microsecond=0)
        assert actual == expected

    def test_parse_t_seven_days_ago(self, vista_client):
        """Test T-7 parses to 7 days ago"""
        result = vista_client._parse_t_notation("T-7")
        expected = datetime.now() - timedelta(days=7)
        # Compare dates only (ignore time)
        assert result.date() == expected.date()

    def test_parse_t_thirty_days_ago(self, vista_client):
        """Test T-30 parses to 30 days ago"""
        result = vista_client._parse_t_notation("T-30")
        expected = datetime.now() - timedelta(days=30)
        assert result.date() == expected.date()

    def test_parse_t_365_days_ago(self, vista_client):
        """Test T-365 parses to 1 year ago"""
        result = vista_client._parse_t_notation("T-365")
        expected = datetime.now() - timedelta(days=365)
        assert result.date() == expected.date()

    def test_parse_invalid_t_notation(self, vista_client):
        """Test invalid T-notation returns very old date"""
        result = vista_client._parse_t_notation("T-invalid")
        assert result == datetime(1900, 1, 1)

    def test_parse_missing_t_notation(self, vista_client):
        """Test missing T-notation returns very old date"""
        result = vista_client._parse_t_notation("")
        assert result == datetime(1900, 1, 1)

    def test_parse_none_t_notation(self, vista_client):
        """Test None T-notation returns very old date"""
        result = vista_client._parse_t_notation(None)
        assert result == datetime(1900, 1, 1)

    def test_parse_iso_date_string(self, vista_client):
        """Test ISO date string parsing"""
        result = vista_client._parse_t_notation("2024-01-15")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15


class TestGetTreatingFacilities:
    """Test _get_patient_treating_facilities helper"""

    def test_get_treating_facilities_existing_patient(self, vista_client):
        """Test getting treating facilities for existing patient"""
        facilities = vista_client._get_patient_treating_facilities("ICN100001")
        assert len(facilities) == 5
        assert facilities[0]["sta3n"] == "200"
        assert facilities[0]["last_seen"] == "T-7"

    def test_get_treating_facilities_single_site_patient(self, vista_client):
        """Test patient with single treating facility"""
        facilities = vista_client._get_patient_treating_facilities("ICN100013")
        assert len(facilities) == 1
        assert facilities[0]["sta3n"] == "630"
        assert facilities[0]["last_seen"] == "T-0"

    def test_get_treating_facilities_nonexistent_patient(self, vista_client):
        """Test non-existent patient returns empty list"""
        facilities = vista_client._get_patient_treating_facilities("ICN999999")
        assert facilities == []


class TestSiteSelectionBasic:
    """Test basic site selection logic"""

    def test_site_selection_default_limit(self, vista_client):
        """Test default site limit (3 sites)"""
        sites = vista_client.get_target_sites("ICN100001", "unknown_domain")
        assert len(sites) == 3
        # Should return most recent 3 sites
        assert sites == ["200", "500", "630"]

    def test_site_selection_sorted_by_last_seen(self, vista_client):
        """Test sites are sorted by last_seen descending"""
        sites = vista_client.get_target_sites("ICN100001", "default", max_sites=5)
        # Expected order: T-7, T-30, T-90, T-365, T-730
        assert sites == ["200", "500", "630", "402", "405"]

    def test_site_selection_single_site_patient(self, vista_client):
        """Test patient with only one treating facility"""
        sites = vista_client.get_target_sites("ICN100013", "default")
        assert len(sites) == 1
        assert sites == ["630"]

    def test_site_selection_nonexistent_patient(self, vista_client):
        """Test non-existent patient returns empty list"""
        sites = vista_client.get_target_sites("ICN999999", "default")
        assert sites == []


class TestDomainSpecificLimits:
    """Test domain-specific site limits"""

    def test_vitals_domain_limit_2_sites(self, vista_client):
        """Test vitals domain limit (2 sites)"""
        sites = vista_client.get_target_sites("ICN100001", "vitals")
        assert len(sites) == DOMAIN_SITE_LIMITS["vitals"]
        assert len(sites) == 2
        assert sites == ["200", "500"]

    def test_allergies_domain_limit_5_sites(self, vista_client):
        """Test allergies domain limit (5 sites)"""
        sites = vista_client.get_target_sites("ICN100001", "allergies")
        assert len(sites) == DOMAIN_SITE_LIMITS["allergies"]
        assert len(sites) == 5
        assert sites == ["200", "500", "630", "402", "405"]

    def test_medications_domain_limit_3_sites(self, vista_client):
        """Test medications domain limit (3 sites)"""
        sites = vista_client.get_target_sites("ICN100001", "medications")
        assert len(sites) == DOMAIN_SITE_LIMITS["medications"]
        assert len(sites) == 3
        assert sites == ["200", "500", "630"]

    def test_demographics_domain_limit_1_site(self, vista_client):
        """Test demographics domain limit (1 site - most recent only)"""
        sites = vista_client.get_target_sites("ICN100001", "demographics")
        assert len(sites) == DOMAIN_SITE_LIMITS["demographics"]
        assert len(sites) == 1
        assert sites == ["200"]  # Most recent site only

    def test_labs_domain_limit_3_sites(self, vista_client):
        """Test labs domain limit (3 sites)"""
        sites = vista_client.get_target_sites("ICN100001", "labs")
        assert len(sites) == DOMAIN_SITE_LIMITS["labs"]
        assert len(sites) == 3

    def test_unknown_domain_uses_default_limit(self, vista_client):
        """Test unknown domain uses default limit (3)"""
        sites = vista_client.get_target_sites("ICN100001", "unknown_new_domain")
        assert len(sites) == DOMAIN_SITE_LIMITS["default"]
        assert len(sites) == 3


class TestHardMaximumLimit:
    """Test hard maximum of 10 sites (architectural firebreak)"""

    def test_hard_max_enforced_15_sites_available(self, vista_client):
        """Test hard maximum enforced even with 15 sites available"""
        sites = vista_client.get_target_sites("ICN_MANY_SITES", "default")
        assert len(sites) <= MAX_SITES_ABSOLUTE
        assert len(sites) == 3  # Default limit is 3

    def test_hard_max_enforced_with_override(self, vista_client):
        """Test hard maximum enforced even with max_sites override"""
        sites = vista_client.get_target_sites("ICN_MANY_SITES", "default", max_sites=15)
        assert len(sites) == MAX_SITES_ABSOLUTE
        assert len(sites) == 10

    def test_hard_max_enforced_allergies_domain(self, vista_client):
        """Test hard maximum enforced for allergies (normally 5 sites)"""
        sites = vista_client.get_target_sites("ICN_MANY_SITES", "allergies")
        assert len(sites) == DOMAIN_SITE_LIMITS["allergies"]
        assert len(sites) == 5  # Allergies limit is 5, which is < 10


class TestUserSelectedSites:
    """Test user-selected sites override automatic selection"""

    def test_user_selected_sites_override(self, vista_client):
        """Test explicit site selection from UI"""
        user_sites = ["630", "402", "405"]
        sites = vista_client.get_target_sites(
            "ICN100001",
            "vitals",
            user_selected_sites=user_sites
        )
        assert sites == user_sites

    def test_user_selected_sites_respect_hard_max(self, vista_client):
        """Test user selection respects 10-site hard maximum"""
        user_sites = [f"{i:03d}" for i in range(15)]  # 15 sites
        sites = vista_client.get_target_sites(
            "ICN100001",
            "vitals",
            user_selected_sites=user_sites
        )
        assert len(sites) == MAX_SITES_ABSOLUTE
        assert len(sites) == 10

    def test_user_selected_sites_empty_list(self, vista_client):
        """Test empty user selection falls back to automatic selection"""
        sites = vista_client.get_target_sites(
            "ICN100001",
            "vitals",
            user_selected_sites=[]
        )
        # Empty list is falsy, should fall back to automatic selection
        assert len(sites) == DOMAIN_SITE_LIMITS["vitals"]
        assert len(sites) == 2

    def test_user_selected_sites_none(self, vista_client):
        """Test None user selection falls back to automatic selection"""
        sites = vista_client.get_target_sites(
            "ICN100001",
            "vitals",
            user_selected_sites=None
        )
        assert len(sites) == DOMAIN_SITE_LIMITS["vitals"]
        assert len(sites) == 2


class TestMaxSitesOverride:
    """Test max_sites parameter override"""

    def test_max_sites_override_increase(self, vista_client):
        """Test max_sites parameter can increase default limit"""
        sites = vista_client.get_target_sites("ICN100001", "vitals", max_sites=4)
        assert len(sites) == 4
        assert sites == ["200", "500", "630", "402"]

    def test_max_sites_override_decrease(self, vista_client):
        """Test max_sites parameter can decrease default limit"""
        sites = vista_client.get_target_sites("ICN100001", "allergies", max_sites=2)
        assert len(sites) == 2
        assert sites == ["200", "500"]

    def test_max_sites_override_respects_hard_max(self, vista_client):
        """Test max_sites override still respects hard maximum"""
        sites = vista_client.get_target_sites("ICN_MANY_SITES", "default", max_sites=20)
        assert len(sites) == MAX_SITES_ABSOLUTE
        assert len(sites) == 10


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_no_treating_facilities_empty_list(self, vista_client):
        """Test patient with no treating facilities"""
        with patch.object(vista_client, '_get_patient_treating_facilities', return_value=[]):
            sites = vista_client.get_target_sites("ICN000000", "default")
            assert sites == []

    def test_treating_facility_missing_last_seen(self, vista_client):
        """Test facility with missing last_seen field"""
        # Mock treating facilities with missing last_seen
        with patch.object(vista_client, '_get_patient_treating_facilities', return_value=[
            {"sta3n": "200", "dfn": "100001"},  # Missing last_seen
            {"sta3n": "500", "dfn": "500001", "last_seen": "T-7"}
        ]):
            sites = vista_client.get_target_sites("ICN_TEST", "default")
            # Site with last_seen should come first
            assert sites == ["500", "200"]

    def test_treating_facility_invalid_last_seen(self, vista_client):
        """Test facility with invalid last_seen value"""
        with patch.object(vista_client, '_get_patient_treating_facilities', return_value=[
            {"sta3n": "200", "dfn": "100001", "last_seen": "INVALID"},
            {"sta3n": "500", "dfn": "500001", "last_seen": "T-7"}
        ]):
            sites = vista_client.get_target_sites("ICN_TEST", "default")
            # Valid T-notation should come first
            assert sites == ["500", "200"]

    def test_zero_max_sites_returns_empty(self, vista_client):
        """Test max_sites=0 returns empty list"""
        sites = vista_client.get_target_sites("ICN100001", "default", max_sites=0)
        assert sites == []

    def test_negative_max_sites_returns_empty(self, vista_client):
        """Test negative max_sites returns empty list"""
        sites = vista_client.get_target_sites("ICN100001", "default", max_sites=-1)
        assert sites == []


class TestDomainSiteLimitsConfiguration:
    """Test DOMAIN_SITE_LIMITS configuration is valid"""

    def test_domain_limits_all_positive(self):
        """Test all domain limits are positive integers"""
        for domain, limit in DOMAIN_SITE_LIMITS.items():
            assert isinstance(limit, int)
            assert limit > 0
            assert limit <= MAX_SITES_ABSOLUTE

    def test_domain_limits_has_default(self):
        """Test configuration has default domain"""
        assert "default" in DOMAIN_SITE_LIMITS

    def test_domain_limits_has_expected_domains(self):
        """Test configuration has expected clinical domains"""
        expected_domains = ["vitals", "allergies", "medications", "demographics", "labs", "default"]
        for domain in expected_domains:
            assert domain in DOMAIN_SITE_LIMITS

    def test_max_sites_absolute_is_10(self):
        """Test hard maximum is set to 10"""
        assert MAX_SITES_ABSOLUTE == 10

    def test_demographics_is_most_restrictive(self):
        """Test demographics has most restrictive limit (1 site)"""
        assert DOMAIN_SITE_LIMITS["demographics"] == 1

    def test_allergies_has_highest_limit(self):
        """Test allergies has highest limit (safety-critical)"""
        allergies_limit = DOMAIN_SITE_LIMITS["allergies"]
        for domain, limit in DOMAIN_SITE_LIMITS.items():
            if domain != "allergies":
                assert allergies_limit >= limit
