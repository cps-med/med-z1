"""
Integration tests for multi-user CCOW Context Vault API (v2.0)

Tests the FastAPI endpoints with authentication, session validation,
and multi-user context isolation.

Prerequisites:
- PostgreSQL running with auth.sessions and auth.users tables
- CCOW vault service running on port 8001
- Test users created in database
- Valid session cookies for test users

Run with: pytest scripts/test_api_multiuser.py -v
"""

import pytest
import requests
import uuid
from datetime import datetime, timezone, timedelta


# CCOW API base URL
CCOW_BASE_URL = "http://localhost:8001"

# Test user sessions (replace with actual session IDs from database)
# You can create these by logging in as test users via the med-z1 app
TEST_USER1_SESSION = None  # Set via fixture
TEST_USER2_SESSION = None  # Set via fixture
TEST_USER3_SESSION = None  # Set via fixture


@pytest.fixture(scope="module")
def test_sessions():
    """
    Fixture to provide test user session IDs.

    In a real test environment, you would:
    1. Create test users in auth.users
    2. Create valid sessions in auth.sessions
    3. Return session IDs for testing

    For now, this is a placeholder that skips tests if sessions not available.
    """
    # TODO: Implement session creation for testing
    # This would typically:
    # 1. Connect to test database
    # 2. Create test users if not exist
    # 3. Create valid sessions with future expires_at
    # 4. Return session IDs

    return {
        "user1": TEST_USER1_SESSION,
        "user2": TEST_USER2_SESSION,
        "user3": TEST_USER3_SESSION,
    }


@pytest.fixture
def cleanup_vault():
    """Fixture to cleanup vault state after each test."""
    yield
    # Cleanup logic here if needed
    # For now, stale contexts will auto-cleanup after 24 hours


class TestCCOWAPIAuthentication:
    """Test authentication and session validation."""

    def test_health_endpoint_no_auth(self):
        """Health endpoint should work without authentication."""
        response = requests.get(f"{CCOW_BASE_URL}/ccow/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ccow-vault"
        assert data["version"] == "2.0.0"

    def test_root_endpoint_no_auth(self):
        """Root endpoint should work without authentication."""
        response = requests.get(f"{CCOW_BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "ccow"
        assert data["version"] == "2.0.0"

    def test_get_active_patient_no_session(self):
        """Getting active patient without session should return 401."""
        response = requests.get(f"{CCOW_BASE_URL}/ccow/active-patient")
        assert response.status_code == 401
        assert "session" in response.json()["detail"].lower()

    def test_set_active_patient_no_session(self):
        """Setting active patient without session should return 401."""
        response = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": "1012853550V207686", "set_by": "test"}
        )
        assert response.status_code == 401

    def test_clear_active_patient_no_session(self):
        """Clearing active patient without session should return 401."""
        response = requests.delete(f"{CCOW_BASE_URL}/ccow/active-patient")
        assert response.status_code == 401

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_invalid_session_id(self):
        """Invalid session ID should return 401."""
        invalid_session = str(uuid.uuid4())
        response = requests.get(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            cookies={"session_id": invalid_session}
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()


class TestCCOWAPIMultiUserContext:
    """Test multi-user context isolation."""

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_set_and_get_context_single_user(self, test_sessions, cleanup_vault):
        """User should be able to set and retrieve their context."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        patient_icn = "1012853550V207686"

        # Set context
        response = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": patient_icn, "set_by": "test"},
            cookies={"session_id": session1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_icn
        assert "user_id" in data
        assert "set_at" in data

        # Get context
        response = requests.get(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            cookies={"session_id": session1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_icn

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_context_isolation_between_users(self, test_sessions, cleanup_vault):
        """Each user should have independent context."""
        session1 = test_sessions["user1"]
        session2 = test_sessions["user2"]
        if not (session1 and session2):
            pytest.skip("Test sessions not available")

        patient1_icn = "1012853550V207686"
        patient2_icn = "1012853551V207687"

        # User 1 sets patient A
        response1 = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": patient1_icn, "set_by": "test"},
            cookies={"session_id": session1}
        )
        assert response1.status_code == 200

        # User 2 sets patient B
        response2 = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": patient2_icn, "set_by": "test"},
            cookies={"session_id": session2}
        )
        assert response2.status_code == 200

        # User 1 should still see patient A
        response1_get = requests.get(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            cookies={"session_id": session1}
        )
        assert response1_get.json()["patient_id"] == patient1_icn

        # User 2 should see patient B
        response2_get = requests.get(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            cookies={"session_id": session2}
        )
        assert response2_get.json()["patient_id"] == patient2_icn

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_update_own_context(self, test_sessions, cleanup_vault):
        """User should be able to update their own context."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        patient1_icn = "1012853550V207686"
        patient2_icn = "1012853551V207687"

        # Set initial context
        requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": patient1_icn, "set_by": "test"},
            cookies={"session_id": session1}
        )

        # Update to different patient
        response = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": patient2_icn, "set_by": "test"},
            cookies={"session_id": session1}
        )
        assert response.status_code == 200

        # Should now see updated patient
        response_get = requests.get(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            cookies={"session_id": session1}
        )
        assert response_get.json()["patient_id"] == patient2_icn

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_clear_own_context(self, test_sessions, cleanup_vault):
        """User should be able to clear their own context."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        patient_icn = "1012853550V207686"

        # Set context
        requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": patient_icn, "set_by": "test"},
            cookies={"session_id": session1}
        )

        # Clear context
        response = requests.delete(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"cleared_by": "test"},
            cookies={"session_id": session1}
        )
        assert response.status_code == 204

        # Should now get 404
        response_get = requests.get(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            cookies={"session_id": session1}
        )
        assert response_get.status_code == 404

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_clear_nonexistent_context(self, test_sessions, cleanup_vault):
        """Clearing non-existent context should return 404."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        # Try to clear without setting first
        response = requests.delete(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            cookies={"session_id": session1}
        )
        assert response.status_code == 404


class TestCCOWAPIHistory:
    """Test context history endpoints."""

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_get_user_history(self, test_sessions, cleanup_vault):
        """User should see their own history."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        patient_icn = "1012853550V207686"

        # Set context
        requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": patient_icn, "set_by": "test"},
            cookies={"session_id": session1}
        )

        # Get user-scoped history
        response = requests.get(
            f"{CCOW_BASE_URL}/ccow/history?scope=user",
            cookies={"session_id": session1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["scope"] == "user"
        assert data["total_count"] >= 1
        assert len(data["history"]) >= 1
        assert data["history"][0]["action"] == "set"
        assert data["history"][0]["patient_id"] == patient_icn

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_get_global_history(self, test_sessions, cleanup_vault):
        """User should see global history from all users."""
        session1 = test_sessions["user1"]
        session2 = test_sessions["user2"]
        if not (session1 and session2):
            pytest.skip("Test sessions not available")

        # User 1 sets context
        requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": "1012853550V207686", "set_by": "test"},
            cookies={"session_id": session1}
        )

        # User 2 sets context
        requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": "1012853551V207687", "set_by": "test"},
            cookies={"session_id": session2}
        )

        # Get global history (from either user)
        response = requests.get(
            f"{CCOW_BASE_URL}/ccow/history?scope=global",
            cookies={"session_id": session1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["scope"] == "global"
        assert data["total_count"] >= 2

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_history_invalid_scope(self, test_sessions):
        """Invalid scope parameter should return 400."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        response = requests.get(
            f"{CCOW_BASE_URL}/ccow/history?scope=invalid",
            cookies={"session_id": session1}
        )
        assert response.status_code == 400


class TestCCOWAPIAdmin:
    """Test admin endpoints."""

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_get_all_contexts(self, test_sessions, cleanup_vault):
        """Should return all active contexts."""
        session1 = test_sessions["user1"]
        session2 = test_sessions["user2"]
        if not (session1 and session2):
            pytest.skip("Test sessions not available")

        # User 1 sets context
        requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": "1012853550V207686", "set_by": "test"},
            cookies={"session_id": session1}
        )

        # User 2 sets context
        requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": "1012853551V207687", "set_by": "test"},
            cookies={"session_id": session2}
        )

        # Get all contexts
        response = requests.get(
            f"{CCOW_BASE_URL}/ccow/active-patients",
            cookies={"session_id": session1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 2
        assert len(data["contexts"]) >= 2

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_manual_cleanup(self, test_sessions):
        """Manual cleanup should work."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        response = requests.post(
            f"{CCOW_BASE_URL}/ccow/cleanup",
            cookies={"session_id": session1}
        )
        assert response.status_code == 200
        data = response.json()
        assert "removed_count" in data
        assert "message" in data


class TestCCOWAPIErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_malformed_patient_id(self, test_sessions, cleanup_vault):
        """Malformed patient ID should still be accepted (validation is client-side)."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        # API doesn't validate ICN format, just stores it
        response = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": "invalid-icn", "set_by": "test"},
            cookies={"session_id": session1}
        )
        assert response.status_code == 200

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_missing_patient_id(self, test_sessions):
        """Missing patient_id should return 422."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        response = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"set_by": "test"},  # Missing patient_id
            cookies={"session_id": session1}
        )
        assert response.status_code == 422

    @pytest.mark.skip(reason="Requires valid test sessions")
    def test_empty_patient_id(self, test_sessions):
        """Empty patient_id should return 422."""
        session1 = test_sessions["user1"]
        if not session1:
            pytest.skip("Test session not available")

        response = requests.put(
            f"{CCOW_BASE_URL}/ccow/active-patient",
            json={"patient_id": "", "set_by": "test"},
            cookies={"session_id": session1}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    print("CCOW Multi-User API Integration Tests")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. CCOW vault service running on http://localhost:8001")
    print("2. PostgreSQL with auth.sessions and auth.users tables")
    print("3. Test users created in database")
    print("4. Valid session cookies (update TEST_USER*_SESSION constants)")
    print("\nRun with: pytest scripts/test_api_multiuser.py -v")
    print("\nNote: Most tests are skipped by default. Update fixtures")
    print("with valid session IDs to enable full test suite.")
