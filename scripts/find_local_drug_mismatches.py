#!/usr/bin/env python3
"""
Find LocalDrugSID mismatches in RxOut.RxOutpat INSERT script.
Compares drug names stated in RxOutpat vs actual LocalDrugSID mappings.
"""

import re
from collections import defaultdict

# Parse Dim.LocalDrug to build the LocalDrugSID → Drug mapping
print("=" * 80)
print("Step 1: Building LocalDrugSID → Drug Name mapping from Dim.LocalDrug")
print("=" * 80)

local_drug_map = {}
with open('/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Dim.LocalDrug.sql', 'r') as f:
    content = f.read()

    # Pattern: (LocalDrugSID, ..., 'DrugNameWithoutDose', 'DrugNameWithDose', ...)
    pattern = r'\((\d+),\s*\'[^\']+\',\s*\d+,\s*\d+,\s*\'[^\']+\',\s*\'([^\']+)\',\s*\'([^\']+)\''

    for match in re.finditer(pattern, content):
        local_drug_sid = int(match.group(1))
        drug_without_dose = match.group(2)
        drug_with_dose = match.group(3)

        local_drug_map[local_drug_sid] = {
            'without_dose': drug_without_dose,
            'with_dose': drug_with_dose
        }

print(f"Found {len(local_drug_map)} LocalDrug records")
print("\nSample mappings:")
for sid in sorted(local_drug_map.keys())[:5]:
    print(f"  LocalDrugSID {sid}: {local_drug_map[sid]['with_dose']}")

# Parse RxOut.RxOutpat to find prescriptions
print("\n" + "=" * 80)
print("Step 2: Analyzing RxOut.RxOutpat prescriptions")
print("=" * 80)

prescriptions = []
with open('/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/RxOut.RxOutpat.sql', 'r') as f:
    content = f.read()

    # Pattern: (RxOutpatSID, ..., LocalDrugSID, ..., 'DrugNameWithoutDose', 'DrugNameWithDose', ...)
    # Field order from CREATE TABLE:
    # RxOutpatSID, RxIEN, Sta3n, PatientSID, PatientICN, LocalDrugSID, LocalDrugIEN, NationalDrugSID,
    # DrugNameWithoutDose, DrugNameWithDose, ...

    pattern = r'\((\d+),\s*\'[^\']+\',\s*\d+,\s*\d+,\s*\'[^\']+\',\s*(\d+),\s*\'[^\']+\',\s*\d+,\s*\'([^\']+)\',\s*\'([^\']+)\''

    for match in re.finditer(pattern, content):
        rx_sid = int(match.group(1))
        local_drug_sid = int(match.group(2))
        stated_drug_without = match.group(3)
        stated_drug_with = match.group(4)

        prescriptions.append({
            'rx_sid': rx_sid,
            'local_drug_sid': local_drug_sid,
            'stated_without': stated_drug_without,
            'stated_with': stated_drug_with
        })

print(f"Found {len(prescriptions)} prescriptions")

# Compare stated drug names vs actual LocalDrugSID mappings
print("\n" + "=" * 80)
print("Step 3: Finding mismatches")
print("=" * 80)

mismatches = []
correct_count = 0

for rx in prescriptions:
    rx_sid = rx['rx_sid']
    local_drug_sid = rx['local_drug_sid']
    stated_with = rx['stated_with']

    if local_drug_sid not in local_drug_map:
        mismatches.append({
            'rx_sid': rx_sid,
            'local_drug_sid': local_drug_sid,
            'issue': 'MISSING_MAPPING',
            'stated_drug': stated_with,
            'actual_drug': 'N/A - LocalDrugSID not found in Dim.LocalDrug',
            'correct_sid': None
        })
        continue

    actual_drug = local_drug_map[local_drug_sid]['with_dose']

    if stated_with != actual_drug:
        # Find the correct LocalDrugSID
        correct_sid = None
        for sid, drug_info in local_drug_map.items():
            if drug_info['with_dose'] == stated_with:
                correct_sid = sid
                break

        mismatches.append({
            'rx_sid': rx_sid,
            'local_drug_sid': local_drug_sid,
            'issue': 'MISMATCH',
            'stated_drug': stated_with,
            'actual_drug': actual_drug,
            'correct_sid': correct_sid
        })
    else:
        correct_count += 1

print(f"\nResults:")
print(f"  ✅ Correct: {correct_count}")
print(f"  ❌ Mismatches: {len(mismatches)}")

if mismatches:
    print("\n" + "=" * 80)
    print("MISMATCHES FOUND:")
    print("=" * 80)

    for mm in mismatches:
        print(f"\nRxOutpatSID {mm['rx_sid']}:")
        print(f"  Current LocalDrugSID: {mm['local_drug_sid']}")
        print(f"  Stated drug: {mm['stated_drug']}")
        print(f"  Actual drug (via LocalDrugSID): {mm['actual_drug']}")
        if mm['correct_sid']:
            print(f"  ✅ Correct LocalDrugSID should be: {mm['correct_sid']}")
        else:
            print(f"  ⚠️  No matching LocalDrugSID found for stated drug!")

    # Generate corrections summary
    print("\n" + "=" * 80)
    print("CORRECTIONS NEEDED:")
    print("=" * 80)
    print("\nIn file: mock/sql-server/cdwwork/insert/RxOut.RxOutpat.sql")
    print("\nChange the following LocalDrugSID values:\n")

    for mm in sorted(mismatches, key=lambda x: x['rx_sid']):
        if mm['correct_sid']:
            print(f"RxOutpatSID {mm['rx_sid']}: Change LocalDrugSID from {mm['local_drug_sid']} → {mm['correct_sid']}")
            print(f"  ({mm['actual_drug']} → {mm['stated_drug']})")
        else:
            print(f"RxOutpatSID {mm['rx_sid']}: ⚠️ Cannot find LocalDrugSID for '{mm['stated_drug']}'")
else:
    print("\n✅ All prescriptions have correct LocalDrugSID mappings!")

print("\n" + "=" * 80)
