#!/usr/bin/env python3
"""
Test script to directly call the filtered endpoint to verify backend works.
"""

import sys
sys.path.insert(0, '/Users/chuck/swdev/med/med-z1')

from fastapi.testclient import TestClient
from app.main import app

# Create test client (bypasses middleware)
client = TestClient(app)

print("=" * 80)
print("TEST: Direct API call to filtered endpoint (bypasses auth middleware)")
print("=" * 80)

# Test 1: Filter by influenza
print("\n1. Testing vaccine_group=influenza")
response = client.get("/patient/ICN100001/immunizations/filtered?vaccine_group=influenza")
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    # Count rows in HTML response
    row_count = response.text.count('<tr class="immunization-row">')
    print(f"Table rows returned: {row_count}")
    print("EXPECTED: 4 rows")
    if row_count == 4:
        print("✅ PASS: Correct number of records")
    else:
        print(f"❌ FAIL: Expected 4 rows, got {row_count}")
        print("\nFirst 500 chars of response:")
        print(response.text[:500])
else:
    print(f"❌ FAIL: Got status code {response.status_code}")
    print(f"Response: {response.text[:500]}")

# Test 2: Filter by covid-19
print("\n2. Testing vaccine_group=covid-19")
response = client.get("/patient/ICN100001/immunizations/filtered?vaccine_group=covid-19")
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    row_count = response.text.count('<tr class="immunization-row">')
    print(f"Table rows returned: {row_count}")
    print("EXPECTED: 2 rows")
    if row_count == 2:
        print("✅ PASS: Correct number of records")
    else:
        print(f"❌ FAIL: Expected 2 rows, got {row_count}")
else:
    print(f"❌ FAIL: Got status code {response.status_code}")

# Test 3: No filter (all records)
print("\n3. Testing no filter (all records)")
response = client.get("/patient/ICN100001/immunizations/filtered")
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    row_count = response.text.count('<tr class="immunization-row">')
    print(f"Table rows returned: {row_count}")
    print("EXPECTED: 24 rows")
    if row_count == 24:
        print("✅ PASS: Correct number of records")
    else:
        print(f"❌ FAIL: Expected 24 rows, got {row_count}")
else:
    print(f"❌ FAIL: Got status code {response.status_code}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("If all tests pass, the backend filtering works correctly.")
print("If filter doesn't work in browser, the issue is in frontend (HTMX/JavaScript).")
print("=" * 80)
