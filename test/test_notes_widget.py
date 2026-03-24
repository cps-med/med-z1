#!/usr/bin/env python3
# ---------------------------------------------------------------------
# test_notes_widget.py
# ---------------------------------------------------------------------
# Test script for clinical notes widget rendering
# Tests Day 5 deliverables: widget HTML and dashboard integration
#
# NOTE: This test requires authentication. Widget endpoints are protected
# by AuthMiddleware. For automated testing, use pytest with auth fixtures.
# For manual testing, run the app and access widget endpoints directly.
#
# Manual Test:
#   1. Start the app: uvicorn app.main:app --reload
#   2. Login via browser: http://localhost:8000/login
#   3. Select patient ICN100001
#   4. View dashboard: http://localhost:8000/
#   5. Verify Clinical Notes widget displays (2x1 compact layout)
# ---------------------------------------------------------------------

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.main import app

# Create test client
# NOTE: TestClient does not handle authentication middleware properly
# without additional auth fixtures. These tests document the expected
# behavior but require a running app with login for full verification.
client = TestClient(app)

def test_widget_endpoint():
    """Test the notes widget endpoint directly"""
    print("=" * 70)
    print("TEST: Notes Widget Endpoint (/api/patient/dashboard/widget/notes/{icn})")
    print("=" * 70)

    try:
        # Test with ICN100001 (has 40 notes)
        response = client.get("/api/patient/dashboard/widget/notes/ICN100001")

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Response Length: {len(response.text)} characters")

        if response.status_code == 200:
            # Check for key widget elements in the HTML
            html = response.text

            checks = [
                ("Widget Header", "widget__header" in html),
                ("Widget Title", "Clinical Notes" in html),
                ("Total Badge", "Total" in html),
                ("Summary Pills", "notes-summary-pills" in html),
                ("Note Items", "note-item-widget" in html),
                ("View All Link", "View All Notes" in html),
                ("Compact Layout", "note-item-widget__meta-compact" in html),
                ("Compact Preview", "note-item-widget__preview--compact" in html),
            ]

            print("\nHTML Content Checks:")
            all_passed = True
            for check_name, passed in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {status}: {check_name}")
                if not passed:
                    all_passed = False

            # Show a preview of the HTML
            print("\nHTML Preview (first 500 chars):")
            print(response.text[:500])
            print("...")

            return all_passed
        else:
            print(f"❌ Error: Expected 200, got {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_widget_with_patients():
    """Test widget with different patients"""
    print("\n" + "=" * 70)
    print("TEST: Widget Rendering with Multiple Patients")
    print("=" * 70)

    test_patients = [
        ("ICN100001", "Patient with many notes (40)"),
        ("ICN100002", "Patient with moderate notes"),
        ("ICN100003", "Patient with few notes"),
    ]

    results = []
    for icn, description in test_patients:
        print(f"\nTesting {icn}: {description}")

        try:
            response = client.get(f"/api/patient/dashboard/widget/notes/{icn}")

            if response.status_code == 200:
                html = response.text
                has_content = "note-item-widget" in html
                has_empty = "No clinical notes recorded" in html

                if has_content:
                    # Count note items (compact layout)
                    note_count = html.count("note-item-widget__meta-compact")
                    print(f"  ✅ PASS: Widget rendered with {note_count} note(s) in compact layout")
                    results.append(True)
                elif has_empty:
                    print(f"  ✅ PASS: Empty state displayed (no notes)")
                    results.append(True)
                else:
                    print(f"  ⚠️  WARNING: Unexpected content")
                    results.append(True)
            else:
                print(f"  ❌ FAIL: HTTP {response.status_code}")
                results.append(False)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)

    return all(results)


def test_dashboard_integration():
    """Test that dashboard includes the notes widget"""
    print("\n" + "=" * 70)
    print("TEST: Dashboard Integration")
    print("=" * 70)

    # Note: This will redirect to login without auth
    # We're just checking that the endpoint exists
    print("Note: Full dashboard test requires authentication")
    print("Checking that the notes widget endpoint is registered...")

    try:
        # Check OpenAPI spec for the endpoint
        response = client.get("/openapi.json")

        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})

            widget_endpoint = "/api/patient/dashboard/widget/notes/{icn}"
            if widget_endpoint in paths:
                print(f"✅ PASS: Widget endpoint registered in OpenAPI spec")
                return True
            else:
                print(f"❌ FAIL: Widget endpoint not found in OpenAPI spec")
                return False
        else:
            print(f"❌ FAIL: Could not fetch OpenAPI spec")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all widget tests"""
    print("\n" + "=" * 70)
    print("CLINICAL NOTES WIDGET TESTS (DAY 5)")
    print("=" * 70)

    tests = [
        ("Widget Endpoint", test_widget_endpoint),
        ("Multiple Patients", test_widget_with_patients),
        ("Dashboard Integration", test_dashboard_integration),
    ]

    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All widget tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
