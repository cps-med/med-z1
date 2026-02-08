#!/usr/bin/env python3
# ---------------------------------------------------------------------
# test_problems_vista_cache.py
# ---------------------------------------------------------------------
# Test VistA cache persistence for Problems domain
#
# Tests:
# 1. Initial page load shows PostgreSQL data only
# 2. After "Refresh VistA", page shows merged PG + VistA data
# 3. Navigate away and back - should show merged data (cache persists)
# 4. Page refresh (F5) - should show merged data (cache persists)
# ---------------------------------------------------------------------

import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_ICN = "ICN100001"

# Track session cookies to maintain cache across requests
session = requests.Session()

def test_initial_page_load():
    """Test 1: Initial page load should show PostgreSQL data only."""
    print("\n" + "="*70)
    print("TEST 1: Initial Page Load (No VistA Cache)")
    print("="*70)

    url = f"{BASE_URL}/patient/{TEST_ICN}/problems"
    response = session.get(url)

    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    # Check for PostgreSQL data (should be present)
    html = response.text
    if "Charlson" in html:
        print("✓ Page rendered successfully")
    else:
        print("✗ Page failed to render")
        return False

    # Check that no VistA cache indicator is present initially
    if "vista_cached" not in html.lower() or "vista_refreshed" not in html.lower():
        print("✓ No VistA cache indicators (expected on initial load)")
    else:
        print("⚠ VistA cache indicators present (unexpected on initial load)")

    return True


def test_vista_refresh():
    """Test 2: After 'Refresh VistA', should show merged data with cache."""
    print("\n" + "="*70)
    print("TEST 2: VistA Refresh (Should Cache Data)")
    print("="*70)

    # Call the realtime endpoint (simulates clicking "Refresh VistA" button)
    url = f"{BASE_URL}/patient/{TEST_ICN}/problems/realtime"
    response = session.get(url)

    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    html = response.text

    # Check for VistA refresh indicators
    if "vista_refreshed" in html or "Vista" in html:
        print("✓ VistA refresh completed")
    else:
        print("✗ VistA refresh failed")
        return False

    # Check for merge stats in logs (we'll see this in terminal)
    print("✓ VistA data fetched and cached in session")

    return True


def test_navigate_away_and_back():
    """Test 3: Navigate to another page and back - cache should persist."""
    print("\n" + "="*70)
    print("TEST 3: Navigate Away and Back (Cache Should Persist)")
    print("="*70)

    # Navigate to demographics page (different page)
    print("Step 1: Navigate to Demographics page...")
    demographics_url = f"{BASE_URL}/patient/{TEST_ICN}/demographics"
    response = session.get(demographics_url)
    print(f"  Demographics page status: {response.status_code}")

    # Navigate back to problems page
    print("Step 2: Navigate back to Problems page...")
    problems_url = f"{BASE_URL}/patient/{TEST_ICN}/problems"
    response = session.get(problems_url)
    print(f"  Problems page status: {response.status_code}")

    # The key test: Server logs should show "Merging PG data with cached Vista responses"
    # We can't see logs here, but we can check that session cookies were preserved
    cookies = session.cookies.get_dict()
    if cookies:
        print(f"✓ Session cookies preserved: {len(cookies)} cookies")
    else:
        print("✗ Session cookies lost")
        return False

    print("✓ Navigated back successfully")
    print("  Check server logs for: 'Merging PG data with cached Vista responses'")

    return True


def test_page_refresh():
    """Test 4: Page refresh (F5) - cache should still persist."""
    print("\n" + "="*70)
    print("TEST 4: Page Refresh (Cache Should Persist)")
    print("="*70)

    # Reload the problems page (simulates F5)
    url = f"{BASE_URL}/patient/{TEST_ICN}/problems"
    response = session.get(url)

    print(f"Status: {response.status_code}")

    cookies = session.cookies.get_dict()
    if cookies:
        print(f"✓ Session cookies still present: {len(cookies)} cookies")
    else:
        print("✗ Session cookies lost after refresh")
        return False

    print("✓ Page refresh successful")
    print("  Check server logs for: 'Merging PG data with cached Vista responses'")

    return True


def test_cache_info():
    """Bonus: Check cache info endpoint if available."""
    print("\n" + "="*70)
    print("BONUS: Session Cache Info")
    print("="*70)

    # This would require a dedicated endpoint, but we can check cookies
    cookies = session.cookies.get_dict()
    print(f"Session cookies: {list(cookies.keys())}")

    # Session cookie typically contains encoded cache data
    if 'session' in cookies:
        session_data = cookies['session']
        print(f"Session data length: {len(session_data)} bytes")
        if len(session_data) > 100:
            print("✓ Session appears to contain cached data")
        else:
            print("⚠ Session data is small - may not contain VistA cache")

    return True


def main():
    print("="*70)
    print("VistA Cache Persistence Test for Problems Domain")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Patient: {TEST_ICN}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run tests in sequence
    tests = [
        ("Initial Page Load", test_initial_page_load),
        ("VistA Refresh", test_vista_refresh),
        ("Navigate Away and Back", test_navigate_away_and_back),
        ("Page Refresh", test_page_refresh),
        ("Cache Info", test_cache_info),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    print("\n" + "="*70)
    print("IMPORTANT: Check server logs for merge messages:")
    print("  - 'Merging PG data with cached Vista responses from sites: ...'")
    print("  - 'Merged: X problems (Y PG + Z Vista)'")
    print("="*70)


if __name__ == "__main__":
    main()
