#!/usr/bin/env python3
"""
Test script to debug immunizations filtering issue.
"""

import sys
sys.path.insert(0, '/Users/chuck/swdev/med/med-z1')

from app.db.patient_immunizations import get_patient_immunizations

# Test 1: Get all immunizations for ICN100001
print("=" * 80)
print("TEST 1: Get ALL immunizations for ICN100001")
print("=" * 80)
all_imms = get_patient_immunizations("ICN100001", limit=500)
print(f"Total records returned: {len(all_imms)}")
print()

# Test 2: Filter by vaccine_group='influenza'
print("=" * 80)
print("TEST 2: Filter by vaccine_group='influenza'")
print("=" * 80)
flu_imms = get_patient_immunizations("ICN100001", limit=500, vaccine_group="influenza")
print(f"Total records returned: {len(flu_imms)}")
if len(flu_imms) > 0:
    print("\nRecords returned:")
    for imm in flu_imms:
        print(f"  - {imm['vaccine_name'][:50]} | Annual: {imm['is_annual_vaccine']} | Date: {imm['administered_datetime']}")
print()

# Test 3: Filter by vaccine_group='covid-19'
print("=" * 80)
print("TEST 3: Filter by vaccine_group='covid-19'")
print("=" * 80)
covid_imms = get_patient_immunizations("ICN100001", limit=500, vaccine_group="covid-19")
print(f"Total records returned: {len(covid_imms)}")
if len(covid_imms) > 0:
    print("\nRecords returned:")
    for imm in covid_imms:
        print(f"  - {imm['vaccine_name'][:50]} | COVID: {imm['is_covid_vaccine']} | Date: {imm['administered_datetime']}")
print()

# Test 4: Check is_annual_vaccine values in all records
print("=" * 80)
print("TEST 4: Check is_annual_vaccine values in ALL records")
print("=" * 80)
annual_count = sum(1 for imm in all_imms if imm['is_annual_vaccine'])
print(f"Records with is_annual_vaccine=True: {annual_count}")
print()

# Test 5: Check is_covid_vaccine values in all records
print("=" * 80)
print("TEST 5: Check is_covid_vaccine values in ALL records")
print("=" * 80)
covid_count = sum(1 for imm in all_imms if imm['is_covid_vaccine'])
print(f"Records with is_covid_vaccine=True: {covid_count}")
print()

print("EXPECTED RESULTS:")
print("- Test 1: Should return 24 records")
print("- Test 2: Should return 4 records (influenza vaccines)")
print("- Test 3: Should return 2 records (COVID vaccines)")
print("- Test 4: Should show 4 records with is_annual_vaccine=True")
print("- Test 5: Should show 2 records with is_covid_vaccine=True")
