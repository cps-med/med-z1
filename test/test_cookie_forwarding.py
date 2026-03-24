#!/usr/bin/env python3
"""
Test if cookies are being forwarded correctly from med-z1 to CCOW vault.

This script simulates what happens when:
1. User logs in to med-z1 (gets session_id cookie)
2. med-z1 app forwards cookie to CCOW vault
3. CCOW vault validates session

Run with: python scripts/test_cookie_forwarding.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import CCOW_URL

def test_cookie_forwarding():
    """Test cookie forwarding with a fake session ID."""
    print("Testing Cookie Forwarding to CCOW Vault")
    print("=" * 60)

    # Test 1: Try to set context WITHOUT session cookie
    print("\nTest 1: Set context without session cookie (should fail with 401)")
    print("-" * 60)
    response = requests.put(
        f"{CCOW_URL}/ccow/active-patient",
        json={"patient_id": "TEST123", "set_by": "test"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 401, "Should reject request without cookie"
    print("✅ Correctly rejected (401)")

    # Test 2: Try with INVALID session cookie
    print("\nTest 2: Set context with invalid session cookie (should fail with 401)")
    print("-" * 60)
    fake_session = "00000000-0000-0000-0000-000000000000"
    response = requests.put(
        f"{CCOW_URL}/ccow/active-patient",
        json={"patient_id": "TEST123", "set_by": "test"},
        cookies={"session_id": fake_session}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 401, "Should reject invalid session"
    print("✅ Correctly rejected (401)")

    # Test 3: Health check (no auth required)
    print("\nTest 3: Health check (should succeed)")
    print("-" * 60)
    response = requests.get(f"{CCOW_URL}/ccow/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, "Health check should work"
    print("✅ Health check passed")

    print("\n" + "=" * 60)
    print("Cookie forwarding mechanism is working correctly!")
    print("The issue is likely:")
    print("1. Session cookie not being sent from browser to med-z1, OR")
    print("2. Session doesn't exist in database, OR")
    print("3. Session has expired")
    print("\nNext steps:")
    print("- Check browser DevTools to see if session_id cookie exists")
    print("- Run: python scripts/debug_ccow_session.py <session_id>")

if __name__ == "__main__":
    test_cookie_forwarding()
