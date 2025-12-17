# ---------------------------------------------------------------------
# vista/tests/test_api_integration.py
# ---------------------------------------------------------------------
# Integration Tests for VistA RPC Broker FastAPI Endpoints
# Tests end-to-end RPC execution via HTTP API
# ---------------------------------------------------------------------

import pytest
from fastapi.testclient import TestClient

from vista.app.main import app, site_registries, initialize_site, SITES

# Create TestClient with raise_server_exceptions to see actual errors
client = TestClient(app, raise_server_exceptions=True)


@pytest.fixture(scope="module", autouse=True)
def ensure_sites_initialized():
    """
    Initialize all Vista sites before running tests.

    TestClient doesn't trigger startup events, so we manually initialize here.
    """
    # Clear any existing registries
    site_registries.clear()

    # Initialize all sites
    for sta3n in SITES.keys():
        site_registries[sta3n] = initialize_site(sta3n)

    # Verify initialization succeeded
    assert len(site_registries) == 3, f"Expected 3 sites, got {len(site_registries)}"

    yield

    # Cleanup
    site_registries.clear()


class TestRootEndpoint:
    """Test root API information endpoint"""

    def test_root_returns_api_info(self):
        """Test that root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "VistA RPC Broker Simulator"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert data["sites"] == 3  # 200, 500, 630
        assert "endpoints" in data


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test that health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["sites_initialized"] == 3
        assert set(data["sites"]) == {"200", "500", "630"}


class TestSitesEndpoint:
    """Test sites listing endpoint"""

    def test_list_sites(self):
        """Test that /sites returns all available sites"""
        response = client.get("/sites")
        assert response.status_code == 200

        sites = response.json()
        assert len(sites) == 3

        # Check site data structure
        site_200 = next(s for s in sites if s["sta3n"] == "200")
        assert site_200["name"] == "ALEXANDRIA"
        assert site_200["rpcs_registered"] >= 1  # At least ORWPT PTINQ
        assert site_200["patients_registered"] >= 1

    def test_sites_include_all_expected_sites(self):
        """Test that all three sites are present"""
        response = client.get("/sites")
        sites = response.json()

        sta3ns = {site["sta3n"] for site in sites}
        assert sta3ns == {"200", "500", "630"}

        names = {site["name"] for site in sites}
        assert names == {"ALEXANDRIA", "ANCHORAGE", "PALO_ALTO"}


class TestRPCExecution:
    """Test RPC execution endpoint"""

    def test_execute_rpc_patient_inquiry_success(self):
        """Test successful ORWPT PTINQ RPC execution"""
        # ICN100001 should be registered at site 200 per patient_registry.json
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100001"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert data["site"] == "200"
        assert data["rpc"] == "ORWPT PTINQ"
        assert data["error"] is None
        assert data["response"] is not None

        # Check VistA-formatted response
        # Format: NAME^SSN^DOB^SEX^VETERAN_STATUS
        response_str = data["response"]
        fields = response_str.split("^")
        assert len(fields) == 5
        assert "DOOREE" in fields[0]  # Patient name from registry
        assert fields[1]  # SSN present
        assert fields[2]  # DOB in FileMan format
        assert fields[3] in ["M", "F"]  # Sex

    def test_execute_rpc_patient_at_different_site(self):
        """Test querying patient at different sites"""
        # ICN100001 is registered at site 200, 500, and 630
        # Test site 500
        response = client.post(
            "/rpc/execute?site=500",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100001"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["site"] == "500"

    def test_execute_rpc_patient_not_registered_at_site(self):
        """Test querying patient not registered at a specific site"""
        # ICN100013 is only registered at site 630 per patient_registry.json
        # Query at site 200 should return error
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100013"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        # RPC should return error response (not HTTP error)
        # Handler returns VistA error format: "-1^Patient not registered..."
        assert data["success"] is True  # HTTP success
        assert "-1^" in data["response"]  # VistA error format

    def test_execute_rpc_patient_not_found(self):
        """Test querying non-existent patient"""
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN999999"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should return VistA error format
        assert data["success"] is True
        assert "-1^" in data["response"]
        assert "not found" in data["response"].lower()

    def test_execute_rpc_missing_parameters(self):
        """Test RPC execution with missing parameters"""
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "ORWPT PTINQ",
                "params": []  # Missing required ICN parameter
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should return error
        assert data["success"] is False
        assert data["error"] is not None
        assert "parameter" in data["error"].lower() or "requires" in data["error"].lower()

    def test_execute_rpc_invalid_site(self):
        """Test RPC execution with invalid site"""
        response = client.post(
            "/rpc/execute?site=999",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100001"]
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_execute_rpc_unregistered_rpc(self):
        """Test executing RPC that doesn't exist"""
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "NONEXISTENT RPC",
                "params": []
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should return error response
        assert data["success"] is False
        assert data["error"] is not None
        assert "not registered" in data["error"].lower() or "not found" in data["error"].lower()

    def test_execute_rpc_missing_site_parameter(self):
        """Test RPC execution without site query parameter"""
        response = client.post(
            "/rpc/execute",  # Missing ?site=200
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100001"]
            }
        )

        # Should return 422 (validation error - missing required query param)
        assert response.status_code == 422


class TestMultiPatientScenarios:
    """Test multiple patients across different sites"""

    def test_patient_with_multi_site_registration(self):
        """Test patient registered at multiple sites"""
        # ICN100001 is registered at sites 200, 500, and 630
        sites_to_test = ["200", "500", "630"]

        for site in sites_to_test:
            response = client.post(
                f"/rpc/execute?site={site}",
                json={
                    "name": "ORWPT PTINQ",
                    "params": ["ICN100001"]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True, f"Failed at site {site}"
            assert data["site"] == site
            assert "DOOREE" in data["response"]

    def test_patient_with_single_site_registration(self):
        """Test patient only registered at one site"""
        # ICN100013 is only registered at site 630

        # Should succeed at site 630
        response = client.post(
            "/rpc/execute?site=630",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100013"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "THOMPSON" in data["response"]

        # Should return error at site 200 (not registered)
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100013"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "-1^" in data["response"]  # VistA error format

    def test_different_patients_at_same_site(self):
        """Test querying different patients at the same site"""
        # Site 200 should have ICN100001 and ICN100010 registered
        test_patients = [
            ("ICN100001", "DOOREE"),
            ("ICN100010", "AMINOR")
        ]

        for icn, expected_name in test_patients:
            response = client.post(
                "/rpc/execute?site=200",
                json={
                    "name": "ORWPT PTINQ",
                    "params": [icn]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert expected_name in data["response"]


class TestResponseFormat:
    """Test VistA response format compliance"""

    def test_patient_inquiry_response_format(self):
        """Test that ORWPT PTINQ returns correct VistA format"""
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN100001"]
            }
        )

        data = response.json()
        vista_response = data["response"]

        # VistA format: NAME^SSN^DOB^SEX^VETERAN_STATUS
        fields = vista_response.split("^")
        assert len(fields) == 5, "ORWPT PTINQ should return 5 fields"

        # Validate field types
        name = fields[0]
        ssn = fields[1]
        dob_fileman = fields[2]
        sex = fields[3]
        veteran_status = fields[4]

        assert "," in name, "Name should be LAST,FIRST format"
        assert len(ssn) > 0, "SSN should be present"
        assert len(dob_fileman) == 7, "DOB should be 7-digit FileMan format (YYYMMDD)"
        assert sex in ["M", "F", "U"], "Sex should be M, F, or U"
        assert len(veteran_status) > 0, "Veteran status should be present"

    def test_error_response_format(self):
        """Test that errors return VistA error format"""
        response = client.post(
            "/rpc/execute?site=200",
            json={
                "name": "ORWPT PTINQ",
                "params": ["ICN999999"]
            }
        )

        data = response.json()
        vista_response = data["response"]

        # VistA error format: CODE^MESSAGE
        assert vista_response.startswith("-"), "Error responses should start with negative code"
        assert "^" in vista_response, "Error should use VistA delimiter"

        fields = vista_response.split("^", 1)  # Split only on first ^
        error_code = fields[0]
        error_message = fields[1] if len(fields) > 1 else ""

        assert error_code.startswith("-"), "Error code should be negative"
        assert len(error_message) > 0, "Error message should be present"


class TestAPIDocumentation:
    """Test that API documentation is available"""

    def test_openapi_docs_accessible(self):
        """Test that /docs endpoint is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json_schema(self):
        """Test that OpenAPI schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert schema["info"]["title"] == "VistA RPC Broker Simulator"
        assert schema["info"]["version"] == "1.0.0"
        assert "/rpc/execute" in schema["paths"]
        assert "/sites" in schema["paths"]
        assert "/health" in schema["paths"]
