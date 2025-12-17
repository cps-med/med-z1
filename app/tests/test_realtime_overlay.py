# ---------------------------------------------------------------------
# app/tests/test_realtime_overlay.py
# ---------------------------------------------------------------------
# Unit tests for Real-Time Data Overlay Service
# Tests merge logic, deduplication, and Vista data parsing
# ---------------------------------------------------------------------

import pytest
from datetime import datetime
from app.services.realtime_overlay import (
    parse_fileman_datetime,
    parse_vista_vitals,
    create_canonical_key,
    merge_vitals_data,
)


class TestFileManDateTimeParsing:
    """Test FileMan date/time format parsing"""

    def test_parse_valid_datetime(self):
        """Test parsing valid FileMan datetime"""
        # 3241217.0930 = December 17, 2024 at 09:30
        result = parse_fileman_datetime("3241217.0930")
        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 17
        assert result.hour == 9
        assert result.minute == 30

    def test_parse_different_year(self):
        """Test parsing different year"""
        # 3230101.1200 = January 1, 2023 at 12:00
        result = parse_fileman_datetime("3230101.1200")
        assert result is not None
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1

    def test_parse_invalid_format(self):
        """Test parsing invalid format returns None"""
        assert parse_fileman_datetime("invalid") is None
        assert parse_fileman_datetime("") is None
        assert parse_fileman_datetime(None) is None
        assert parse_fileman_datetime("12345") is None  # No decimal

    def test_parse_midnight(self):
        """Test parsing midnight time"""
        result = parse_fileman_datetime("3241217.0000")
        assert result is not None
        assert result.hour == 0
        assert result.minute == 0


class TestVistaVitalsParsing:
    """Test parsing Vista RPC responses"""

    def test_parse_single_vital(self):
        """Test parsing single vital from Vista"""
        response = "BLOOD PRESSURE^120/80^mmHg^3241217.0930^NURSE,JANE"
        vitals = parse_vista_vitals(response, "200")

        assert len(vitals) == 1
        vital = vitals[0]

        assert vital["vital_type"] == "BLOOD PRESSURE"
        assert vital["result_value"] == "120/80"
        assert vital["unit_of_measure"] == "mmHg"
        assert vital["entered_by"] == "NURSE,JANE"
        assert vital["systolic"] == 120
        assert vital["diastolic"] == 80
        assert vital["source"] == "vista"
        assert vital["source_site"] == "200"

    def test_parse_multiple_vitals(self):
        """Test parsing multiple vitals from Vista"""
        response = """BLOOD PRESSURE^128/82^mmHg^3241217.0845^NURSE,SARAH
TEMPERATURE^98.4^F^3241217.0845^NURSE,SARAH
PULSE^76^/min^3241217.0845^NURSE,SARAH"""

        vitals = parse_vista_vitals(response, "200")

        assert len(vitals) == 3
        assert vitals[0]["vital_type"] == "BLOOD PRESSURE"
        assert vitals[1]["vital_type"] == "TEMPERATURE"
        assert vitals[2]["vital_type"] == "PULSE"

        # All should have same timestamp
        for vital in vitals:
            assert "2024-12-17 08:45:00" in vital["taken_datetime"]

    def test_parse_error_response(self):
        """Test parsing error response"""
        response = "-1^Patient not found"
        vitals = parse_vista_vitals(response, "200")

        assert len(vitals) == 0

    def test_parse_empty_response(self):
        """Test parsing empty response"""
        vitals = parse_vista_vitals("", "200")
        assert len(vitals) == 0

        vitals = parse_vista_vitals(None, "200")
        assert len(vitals) == 0

    def test_parse_temperature_numeric_value(self):
        """Test numeric value extraction for temperature"""
        response = "TEMPERATURE^98.6^F^3241217.0930^NURSE,JANE"
        vitals = parse_vista_vitals(response, "200")

        assert vitals[0]["numeric_value"] == 98.6

    def test_parse_sets_abbreviations(self):
        """Test vital abbreviations are set correctly"""
        response = """BLOOD PRESSURE^120/80^mmHg^3241217.0930^NURSE,JANE
TEMPERATURE^98.6^F^3241217.0930^NURSE,JANE
PULSE^72^/min^3241217.0930^NURSE,JANE
PULSE OXIMETRY^98^%^3241217.0930^NURSE,JANE"""

        vitals = parse_vista_vitals(response, "200")

        assert vitals[0]["vital_abbr"] == "BP"
        assert vitals[1]["vital_abbr"] == "T"
        assert vitals[2]["vital_abbr"] == "P"
        assert vitals[3]["vital_abbr"] == "POX"


class TestCanonicalKeyCreation:
    """Test deduplication key creation"""

    def test_create_key_basic(self):
        """Test creating canonical key"""
        vital = {
            "vital_type": "BLOOD PRESSURE",
            "taken_datetime": "2024-12-17 09:30:00",
            "location_name": "Alexandria VAMC"
        }

        key = create_canonical_key(vital)

        # Should include type, date to hour, and location
        assert "BLOOD PRESSURE" in key
        assert "2024121709" in key  # YYYYMMDDHH
        assert "Alexandria VAMC" in key

    def test_create_key_same_hour_same_location(self):
        """Test vitals in same hour at same location get same key"""
        vital1 = {
            "vital_type": "BLOOD PRESSURE",
            "taken_datetime": "2024-12-17 09:15:00",
            "location_name": "Site 200"
        }

        vital2 = {
            "vital_type": "BLOOD PRESSURE",
            "taken_datetime": "2024-12-17 09:45:00",  # Different minute, same hour
            "location_name": "Site 200"
        }

        key1 = create_canonical_key(vital1)
        key2 = create_canonical_key(vital2)

        # Should be same key (hour-level fuzzy matching)
        assert key1 == key2

    def test_create_key_different_location(self):
        """Test vitals at different locations get different keys"""
        vital1 = {
            "vital_type": "BLOOD PRESSURE",
            "taken_datetime": "2024-12-17 09:30:00",
            "location_name": "Site 200"
        }

        vital2 = {
            "vital_type": "BLOOD PRESSURE",
            "taken_datetime": "2024-12-17 09:30:00",
            "location_name": "Site 500"
        }

        key1 = create_canonical_key(vital1)
        key2 = create_canonical_key(vital2)

        assert key1 != key2

    def test_create_key_with_source_site(self):
        """Test key creation uses source_site if location_name missing"""
        vital = {
            "vital_type": "TEMPERATURE",
            "taken_datetime": "2024-12-17 09:30:00",
            "source_site": "200"
        }

        key = create_canonical_key(vital)

        assert "TEMPERATURE" in key
        assert "200" in key


class TestMergeVitalsData:
    """Test merge logic"""

    def test_merge_empty_lists(self):
        """Test merging empty data"""
        merged, stats = merge_vitals_data([], {}, "ICN100001")

        assert len(merged) == 0
        assert stats["pg_count"] == 0
        assert stats["vista_count"] == 0
        assert stats["total_merged"] == 0

    def test_merge_pg_only(self):
        """Test merging only PostgreSQL data"""
        pg_vitals = [
            {
                "vital_type": "BLOOD PRESSURE",
                "taken_datetime": "2024-12-16 10:00:00",
                "result_value": "120/80",
                "location_name": "Alexandria VAMC"
            }
        ]

        merged, stats = merge_vitals_data(pg_vitals, {}, "ICN100001")

        assert len(merged) == 1
        assert stats["pg_count"] == 1
        assert stats["vista_count"] == 0
        assert merged[0]["source"] == "postgresql"

    def test_merge_vista_only(self):
        """Test merging only Vista data"""
        vista_data = {
            "200": "BLOOD PRESSURE^120/80^mmHg^3241217.0930^NURSE,JANE"
        }

        merged, stats = merge_vitals_data([], vista_data, "ICN100001")

        assert len(merged) == 1
        assert stats["pg_count"] == 0
        assert stats["vista_count"] == 1
        assert merged[0]["source"] == "vista"
        assert merged[0]["source_site"] == "200"

    def test_merge_multiple_sites(self):
        """Test merging Vista data from multiple sites"""
        vista_data = {
            "200": "BLOOD PRESSURE^120/80^mmHg^3241217.0930^NURSE,JANE",
            "500": "TEMPERATURE^98.6^F^3241217.1000^NURSE,ROBERT",
            "630": "PULSE^72^/min^3241217.1100^NURSE,LISA"
        }

        merged, stats = merge_vitals_data([], vista_data, "ICN100001")

        assert len(merged) == 3
        assert stats["vista_count"] == 3
        assert stats["vista_sites"] == ["200", "500", "630"]

    def test_merge_deduplication_vista_preferred(self):
        """Test Vista data preferred over PG for same vital"""
        # PostgreSQL vital from yesterday
        pg_vitals = [
            {
                "vital_type": "BLOOD PRESSURE",
                "taken_datetime": "2024-12-17 09:30:00",  # Same hour
                "result_value": "130/85",  # Different value
                "location_name": "VistA Site 200"
            }
        ]

        # Vista vital from today (same hour, same location concept)
        vista_data = {
            "200": "BLOOD PRESSURE^120/80^mmHg^3241217.0945^NURSE,JANE"
        }

        merged, stats = merge_vitals_data(pg_vitals, vista_data, "ICN100001")

        # Should only have 1 vital (Vista preferred)
        assert len(merged) == 1
        assert stats["duplicates_removed"] == 1

        # Verify Vista data was kept
        assert merged[0]["source"] == "vista"
        assert merged[0]["result_value"] == "120/80"

    def test_merge_different_vital_types(self):
        """Test merging different vital types (no deduplication)"""
        pg_vitals = [
            {
                "vital_type": "BLOOD PRESSURE",
                "taken_datetime": "2024-12-17 09:00:00",
                "result_value": "120/80",
                "location_name": "Alexandria VAMC"
            }
        ]

        vista_data = {
            "200": "TEMPERATURE^98.6^F^3241217.0900^NURSE,JANE"
        }

        merged, stats = merge_vitals_data(pg_vitals, vista_data, "ICN100001")

        # Should have both (different types)
        assert len(merged) == 2
        assert stats["duplicates_removed"] == 0

    def test_merge_sorting_descending(self):
        """Test merged vitals are sorted by date descending"""
        pg_vitals = [
            {
                "vital_type": "BLOOD PRESSURE",
                "taken_datetime": "2024-12-15 10:00:00",
                "location_name": "Alexandria VAMC"
            }
        ]

        vista_data = {
            "200": "TEMPERATURE^98.6^F^3241217.0900^NURSE,JANE"
        }

        merged, stats = merge_vitals_data(pg_vitals, vista_data, "ICN100001")

        # Most recent first (Vista from 12/17 should be before PG from 12/15)
        assert merged[0]["vital_type"] == "TEMPERATURE"  # 12/17
        assert merged[1]["vital_type"] == "BLOOD PRESSURE"  # 12/15

    def test_merge_sets_patient_icn(self):
        """Test patient ICN is set on Vista vitals"""
        vista_data = {
            "200": "PULSE^72^/min^3241217.0930^NURSE,JANE"
        }

        merged, stats = merge_vitals_data([], vista_data, "ICN100001")

        assert merged[0]["patient_key"] == "ICN100001"

    def test_merge_complex_scenario(self):
        """Test complex merge with multiple sites and deduplication"""
        # 2 PG vitals from yesterday
        pg_vitals = [
            {
                "vital_type": "BLOOD PRESSURE",
                "taken_datetime": "2024-12-16 10:00:00",
                "result_value": "125/82",
                "location_name": "Alexandria VAMC"
            },
            {
                "vital_type": "TEMPERATURE",
                "taken_datetime": "2024-12-17 09:00:00",
                "result_value": "98.4",
                "location_name": "VistA Site 200"
            }
        ]

        # Vista data: 1 new vital, 1 duplicate with PG
        vista_data = {
            "200": "TEMPERATURE^98.6^F^3241217.0915^NURSE,JANE\nPULSE^75^/min^3241217.0915^NURSE,JANE",
            "500": "BLOOD PRESSURE^130/85^mmHg^3241217.1000^NURSE,ROBERT"
        }

        merged, stats = merge_vitals_data(pg_vitals, vista_data, "ICN100001")

        # Should have 4 vitals total:
        # - 2 Vista TEMP + PULSE from site 200 (TEMP replaces PG duplicate)
        # - 1 Vista BP from site 500
        # - 1 PG BP from 12/16 (unique)
        assert len(merged) == 4
        assert stats["pg_count"] == 2
        assert stats["vista_count"] == 3
        assert stats["duplicates_removed"] == 1
