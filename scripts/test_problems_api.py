#!/usr/bin/env python3
"""
Test Problems API Endpoints

Quick test to verify all problems API endpoints are accessible.
This script should be run with the FastAPI server running.

Usage:
  # Terminal 1: Start the server
  uvicorn app.main:app --reload

  # Terminal 2: Run this test
  python scripts/test_problems_api.py
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"
TEST_ICN = "ICN100001"


def test_endpoint(name: str, url: str, expected_status: int = 200):
    """Test an API endpoint."""
    print(f"\nTesting {name}...")
    print(f"  URL: {url}")

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == expected_status:
            print(f"  ✅ Status: {response.status_code}")

            # Try to parse as JSON if it's a JSON endpoint
            if "application/json" in response.headers.get("content-type", ""):
                data = response.json()
                print(f"  📊 Keys: {list(data.keys())}")
            elif "text/html" in response.headers.get("content-type", ""):
                print(f"  📄 HTML length: {len(response.text)} chars")

            return True
        else:
            print(f"  ❌ Status: {response.status_code} (expected {expected_status})")
            print(f"  Response: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection Error: Is the server running at {BASE_URL}?")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run all API endpoint tests."""
    print("=" * 60)
    print("Testing Problems/Diagnoses API Endpoints")
    print("=" * 60)

    tests = [
        # JSON API Endpoints
        ("Get Patient Problems (JSON)", f"{BASE_URL}/api/patient/{TEST_ICN}/problems"),
        ("Get Problems Summary (JSON)", f"{BASE_URL}/api/patient/{TEST_ICN}/problems/summary"),
        ("Get Grouped Problems (JSON)", f"{BASE_URL}/api/patient/{TEST_ICN}/problems/grouped"),
        ("Get Charlson Score (JSON)", f"{BASE_URL}/api/patient/{TEST_ICN}/problems/charlson"),
        ("Get Chronic Conditions (JSON)", f"{BASE_URL}/api/patient/{TEST_ICN}/problems/conditions"),

        # Widget Endpoint (HTML)
        ("Problems Widget (HTML)", f"{BASE_URL}/api/patient/dashboard/widget/problems/{TEST_ICN}"),

        # Full Page Endpoints (HTML)
        ("Problems Page (HTML)", f"{BASE_URL}/patient/{TEST_ICN}/problems"),
    ]

    results = []
    for name, url in tests:
        results.append(test_endpoint(name, url))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Failed: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
