#!/usr/bin/env python3
"""
Extract unique missing drugs that need to be added to Dim.LocalDrug.
"""

import re
from collections import defaultdict

# Parse Dim.LocalDrug to get existing drugs
local_drug_map = {}
with open('/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Dim.LocalDrug.sql', 'r') as f:
    content = f.read()
    pattern = r'\((\d+),\s*\'[^\']+\',\s*\d+,\s*\d+,\s*\'[^\']+\',\s*\'([^\']+)\',\s*\'([^\']+)\''
    for match in re.finditer(pattern, content):
        local_drug_sid = int(match.group(1))
        drug_without_dose = match.group(2)
        drug_with_dose = match.group(3)
        local_drug_map[local_drug_sid] = {
            'without_dose': drug_without_dose,
            'with_dose': drug_with_dose
        }

# Get highest LocalDrugSID
max_sid = max(local_drug_map.keys())
print(f"Current highest LocalDrugSID: {max_sid}")

# Parse RxOut.RxOutpat to find stated drugs
prescriptions = []
with open('/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/RxOut.RxOutpat.sql', 'r') as f:
    content = f.read()
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

# Find missing drugs
missing_drugs = set()
for rx in prescriptions:
    stated_with = rx['stated_with']

    # Check if this drug exists in LocalDrug
    found = False
    for drug_info in local_drug_map.values():
        if drug_info['with_dose'] == stated_with:
            found = True
            break

    if not found:
        missing_drugs.add(stated_with)

# Sort and display
missing_drugs_sorted = sorted(missing_drugs)

print(f"\nFound {len(missing_drugs_sorted)} unique missing drugs:")
print("=" * 80)

for drug in missing_drugs_sorted:
    print(f"  - {drug}")

# Parse drug names to extract components
print("\n" + "=" * 80)
print("Preparing LocalDrug INSERT statements")
print("=" * 80)

def parse_drug_name(drug_with_dose):
    """Parse drug name to extract components."""
    # Try to extract: DrugName Strength Unit
    # Examples:
    #   AMIODARONE HCL 200MG TAB
    #   LISINOPRIL 40MG TAB
    #   INSULIN GLARGINE 100 UNIT/ML INJ

    parts = drug_with_dose.split()

    # Find where the strength starts (first part with a digit)
    strength_idx = None
    for i, part in enumerate(parts):
        if any(c.isdigit() for c in part):
            strength_idx = i
            break

    if strength_idx is None:
        # No strength found (e.g., MULTIVITAMIN TAB)
        drug_name = ' '.join(parts[:-1]) if len(parts) > 1 else parts[0]
        strength = ''
        unit = parts[-1] if len(parts) > 1 else 'TAB'
        dosage_form = unit
    else:
        drug_name = ' '.join(parts[:strength_idx])

        # Strength and unit are combined or separate
        if strength_idx < len(parts) - 1:
            # Multiple parts after drug name
            strength_unit = parts[strength_idx]
            unit = parts[-1]

            # Extract just the strength part
            strength = strength_unit
            dosage_form = unit
        else:
            # Last part contains strength and unit
            last_part = parts[strength_idx]
            strength = last_part
            unit = 'TAB'
            dosage_form = 'TAB'

    return drug_name, strength, unit, dosage_form

next_sid = max_sid + 1
next_national_sid = 20050  # Start high to avoid conflicts

print("\nNew LocalDrug entries needed:\n")

for i, drug in enumerate(missing_drugs_sorted):
    drug_name, strength, unit, dosage_form = parse_drug_name(drug)

    sid = next_sid + i
    nat_sid = next_national_sid + i

    # Generic name (simplified - just use first part of drug name)
    generic = drug_name.split()[0] if drug_name else 'UNKNOWN'

    print(f"-- {drug}")
    print(f"({sid}, 'DrugIEN{sid}', 508, {nat_sid}, 'NDFIEN{nat_sid}', '{drug_name}', '{drug}', '{generic}', '{drug_name} {dosage_form}', '{strength}', '{unit}', '{dosage_form}', 'OTHER', 'OTHER', '{drug_name}', 'N', NULL),")
    print()

print(f"\nNext available LocalDrugSID: {next_sid + len(missing_drugs_sorted)}")
print(f"Next available NationalDrugSID: {next_national_sid + len(missing_drugs_sorted)}")
