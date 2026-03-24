#!/usr/bin/env python3
# ---------------------------------------------------------------------
# scripts/test_auth_flow.py
# ---------------------------------------------------------------------
# Test Authentication Flow
# Manual test script to verify the complete authentication flow.
#
# Usage:
#   python scripts/test_auth_flow.py
#
# Prerequisites:
#   - PostgreSQL database running with auth schema populated
#   - FastAPI application running on http://127.0.0.1:8000
# ---------------------------------------------------------------------

import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_unauthenticated_access():
    """Test that unauthenticated users are redirected to login."""
    print_section("Test 1: Unauthenticated Access")

    response = requests.get(f"{BASE_URL}/", allow_redirects=False)

    print(f"GET /")
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 303 (redirect to /login)")

    if response.status_code == 303:
        print(f"✅ PASS - Redirected to: {response.headers.get('location')}")
    else:
        print(f"❌ FAIL - Expected redirect, got {response.status_code}")

    return response.status_code == 303


def test_login_page_loads():
    """Test that login page loads successfully."""
    print_section("Test 2: Login Page Loads")

    response = requests.get(f"{BASE_URL}/login")

    print(f"GET /login")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200 and "Sign in" in response.text:
        print("✅ PASS - Login page loaded successfully")
        return True
    else:
        print("❌ FAIL - Login page did not load properly")
        return False


def test_invalid_login():
    """Test login with invalid credentials."""
    print_section("Test 3: Invalid Login Attempt")

    response = requests.post(
        f"{BASE_URL}/login",
        data={
            "email": "invalid@va.gov",
            "password": "WrongPassword123!"
        },
        allow_redirects=False
    )

    print(f"POST /login (invalid credentials)")
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 401 (Unauthorized)")

    if response.status_code == 401:
        print("✅ PASS - Invalid login rejected")
        return True
    else:
        print(f"❌ FAIL - Expected 401, got {response.status_code}")
        return False


def test_valid_login():
    """Test login with valid credentials and session creation."""
    print_section("Test 4: Valid Login and Session Creation")

    # Create session to maintain cookies
    session = requests.Session()

    response = session.post(
        f"{BASE_URL}/login",
        data={
            "email": "clinician.alpha@va.gov",
            "password": "VaDemo2025!"
        },
        allow_redirects=False
    )

    print(f"POST /login (valid credentials)")
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 303 (redirect to /)")

    # Check for session cookie
    session_cookie = session.cookies.get("session_id")

    if response.status_code == 303 and session_cookie:
        print(f"✅ PASS - Login successful")
        print(f"   Session Cookie: {session_cookie[:16]}...")
        print(f"   Redirect Location: {response.headers.get('location')}")
        return session, True
    else:
        print(f"❌ FAIL - Login failed")
        return None, False


def test_authenticated_access(session):
    """Test that authenticated users can access protected routes."""
    print_section("Test 5: Authenticated Access to Dashboard")

    if not session:
        print("⚠️  SKIP - No session available")
        return False

    response = session.get(f"{BASE_URL}/")

    print(f"GET / (with session)")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200 and "dashboard" in response.text.lower():
        print("✅ PASS - Authenticated user can access dashboard")
        return True
    else:
        print(f"❌ FAIL - Dashboard access failed")
        return False


def test_logout(session):
    """Test logout functionality."""
    print_section("Test 6: Logout")

    if not session:
        print("⚠️  SKIP - No session available")
        return False

    response = session.post(f"{BASE_URL}/logout", allow_redirects=False)

    print(f"POST /logout")
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 303 (redirect to /login)")

    # Check that session cookie is cleared
    session_cookie = session.cookies.get("session_id")

    if response.status_code == 303 and not session_cookie:
        print("✅ PASS - Logout successful, cookie cleared")
        return True
    else:
        print(f"❌ FAIL - Logout failed")
        return False


def test_post_logout_access(session):
    """Test that logged-out users cannot access protected routes."""
    print_section("Test 7: Post-Logout Access Denied")

    if not session:
        print("⚠️  SKIP - No session available")
        return False

    response = session.get(f"{BASE_URL}/", allow_redirects=False)

    print(f"GET / (after logout)")
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 303 (redirect to /login)")

    if response.status_code == 303:
        print("✅ PASS - Post-logout access denied")
        return True
    else:
        print(f"❌ FAIL - Expected redirect, got {response.status_code}")
        return False


def main():
    """Run all authentication flow tests."""
    print(f"\n{'#'*60}")
    print(f"  Authentication Flow Test Suite")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}\n")

    print(f"Testing against: {BASE_URL}")
    print(f"Ensure FastAPI server is running before proceeding.\n")

    results = []

    # Run tests
    results.append(("Unauthenticated Access Redirect", test_unauthenticated_access()))
    results.append(("Login Page Loads", test_login_page_loads()))
    results.append(("Invalid Login Rejected", test_invalid_login()))

    session, login_success = test_valid_login()
    results.append(("Valid Login", login_success))

    results.append(("Authenticated Access", test_authenticated_access(session)))
    results.append(("Logout", test_logout(session)))
    results.append(("Post-Logout Access Denied", test_post_logout_access(session)))

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{'='*60}")
    print(f"  {passed}/{total} tests passed")
    print(f"{'='*60}\n")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to FastAPI server")
        print("   Please ensure the server is running: uvicorn app.main:app --reload")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
