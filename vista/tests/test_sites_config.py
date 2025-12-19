# ---------------------------------------------------------------------
# vista/tests/test_sites_config.py
# ---------------------------------------------------------------------
# Unit tests for sites.json configuration loading
# ---------------------------------------------------------------------

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

# Import the function we're testing
# We need to import it before the module-level SITES = load_sites_config() runs
import sys
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))


class TestLoadSitesConfig:
    """Test suite for load_sites_config() function"""

    def test_load_valid_sites_config(self):
        """Test loading a valid sites.json configuration"""
        # Create valid JSON data
        valid_config = {
            "sites": [
                {"sta3n": "200", "name": "ALEXANDRIA", "description": "Alexandria VA"},
                {"sta3n": "500", "name": "ANCHORAGE", "description": "Anchorage VA"},
                {"sta3n": "630", "name": "PALO_ALTO", "description": "Palo Alto VA"}
            ],
            "metadata": {"version": "1.0"}
        }

        # Mock the file read operation
        with patch("builtins.open", mock_open(read_data=json.dumps(valid_config))):
            from vista.app.main import load_sites_config

            sites = load_sites_config()

            # Verify correct number of sites loaded
            assert len(sites) == 3

            # Verify site 200 details
            assert "200" in sites
            assert sites["200"]["name"] == "ALEXANDRIA"
            assert sites["200"]["sta3n"] == "200"
            assert sites["200"]["description"] == "Alexandria VA"

            # Verify site 500 details
            assert "500" in sites
            assert sites["500"]["name"] == "ANCHORAGE"

            # Verify site 630 details
            assert "630" in sites
            assert sites["630"]["name"] == "PALO_ALTO"

    def test_load_sites_without_description(self):
        """Test loading sites.json when description field is missing"""
        # Description is optional, should default to empty string
        config_without_desc = {
            "sites": [
                {"sta3n": "200", "name": "ALEXANDRIA"},
                {"sta3n": "500", "name": "ANCHORAGE"}
            ]
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(config_without_desc))):
            from vista.app.main import load_sites_config

            sites = load_sites_config()

            assert len(sites) == 2
            assert sites["200"]["description"] == ""
            assert sites["500"]["description"] == ""

    def test_load_empty_sites_list(self):
        """Test loading sites.json with empty sites array"""
        empty_config = {
            "sites": [],
            "metadata": {"version": "1.0"}
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(empty_config))):
            from vista.app.main import load_sites_config

            sites = load_sites_config()

            assert len(sites) == 0
            assert sites == {}

    def test_file_not_found(self):
        """Test handling of missing sites.json file"""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            from vista.app.main import load_sites_config

            with pytest.raises(FileNotFoundError):
                load_sites_config()

    def test_invalid_json(self):
        """Test handling of malformed JSON in sites.json"""
        invalid_json = "{ invalid json content"

        with patch("builtins.open", mock_open(read_data=invalid_json)):
            from vista.app.main import load_sites_config

            with pytest.raises(json.JSONDecodeError):
                load_sites_config()

    def test_missing_required_field_sta3n(self):
        """Test handling of missing required field (sta3n)"""
        missing_sta3n = {
            "sites": [
                {"name": "ALEXANDRIA", "description": "Alexandria VA"}
                # Missing sta3n field
            ]
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(missing_sta3n))):
            from vista.app.main import load_sites_config

            with pytest.raises(KeyError):
                load_sites_config()

    def test_missing_required_field_name(self):
        """Test handling of missing required field (name)"""
        missing_name = {
            "sites": [
                {"sta3n": "200", "description": "Alexandria VA"}
                # Missing name field
            ]
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(missing_name))):
            from vista.app.main import load_sites_config

            with pytest.raises(KeyError):
                load_sites_config()

    def test_duplicate_sta3n(self):
        """Test handling of duplicate sta3n values (last one wins)"""
        duplicate_config = {
            "sites": [
                {"sta3n": "200", "name": "ALEXANDRIA", "description": "First"},
                {"sta3n": "200", "name": "DUPLICATE", "description": "Second"}
            ]
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(duplicate_config))):
            from vista.app.main import load_sites_config

            sites = load_sites_config()

            # Last occurrence should win
            assert len(sites) == 1
            assert sites["200"]["name"] == "DUPLICATE"
            assert sites["200"]["description"] == "Second"

    def test_actual_sites_json_file(self):
        """Integration test: Load the actual sites.json file"""
        # This test reads the real file to ensure it's valid
        from vista.app.main import load_sites_config

        sites = load_sites_config()

        # Verify expected sites from actual file
        assert len(sites) >= 3  # At least 3 sites
        assert "200" in sites
        assert "500" in sites
        assert "630" in sites

        # Verify structure
        for sta3n, site_data in sites.items():
            assert "name" in site_data
            assert "sta3n" in site_data
            assert "description" in site_data
            assert site_data["sta3n"] == sta3n  # Consistency check


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
