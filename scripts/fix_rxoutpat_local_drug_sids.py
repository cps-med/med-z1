#!/usr/bin/env python3
"""
Generate corrected RxOut.RxOutpat.sql with fixed LocalDrugSID values.
"""

import re

# Build LocalDrugSID → Drug mapping from Dim.LocalDrug
local_drug_map = {}
drug_to_sid_map = {}

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
        drug_to_sid_map[drug_with_dose] = local_drug_sid

print(f"Loaded {len(local_drug_map)} LocalDrug mappings")

# Read RxOutpat file
with open('/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/RxOut.RxOutpat.sql', 'r') as f:
    rxoutpat_content = f.read()

# Split into header and data sections
lines = rxoutpat_content.split('\n')

# Find where INSERT VALUES starts
insert_start_idx = None
values_start_idx = None
for i, line in enumerate(lines):
    if 'INSERT INTO' in line:
        insert_start_idx = i
    if 'VALUES' in line and insert_start_idx is not None:
        values_start_idx = i
        break

# Build corrected file
output_lines = lines[:values_start_idx + 1]  # Keep header up to VALUES

# Pattern to extract fields from each prescription row
# (RxOutpatSID, RxIEN, Sta3n, PatientSID, PatientICN, LocalDrugSID, LocalDrugIEN, NationalDrugSID, DrugNameWithoutDose, DrugNameWithDose, ...)
row_pattern = re.compile(
    r'^\('
    r'(\d+),\s*'  # RxOutpatSID
    r'\'([^\']+)\',\s*'  # RxIEN
    r'(\d+),\s*'  # Sta3n
    r'(\d+),\s*'  # PatientSID
    r'\'([^\']+)\',\s*'  # PatientICN
    r'(\d+),\s*'  # LocalDrugSID
    r'\'([^\']+)\',\s*'  # LocalDrugIEN
    r'(\d+),\s*'  # NationalDrugSID
    r'\'([^\']+)\',\s*'  # DrugNameWithoutDose
    r'\'([^\']+)\','  # DrugNameWithDose
    r'(.*)'  # Rest of the row
    r'$'
)

corrections_made = 0
warnings = []

# Process data rows
for i in range(values_start_idx + 1, len(lines)):
    line = lines[i].strip()

    if not line or line.startswith('--') or line.startswith('GO') or line.startswith('PRINT'):
        output_lines.append(lines[i])
        continue

    match = row_pattern.match(line)
    if not match:
        # Not a data row, keep as-is
        output_lines.append(lines[i])
        continue

    # Extract fields
    rx_sid = match.group(1)
    rx_ien = match.group(2)
    sta3n = match.group(3)
    patient_sid = match.group(4)
    patient_icn = match.group(5)
    current_local_drug_sid = match.group(6)
    local_drug_ien = match.group(7)
    national_drug_sid = match.group(8)
    drug_without = match.group(9)
    drug_with = match.group(10)
    rest_of_row = match.group(11)

    # Find correct LocalDrugSID
    if drug_with in drug_to_sid_map:
        correct_local_drug_sid = drug_to_sid_map[drug_with]

        if int(current_local_drug_sid) != correct_local_drug_sid:
            corrections_made += 1
            print(f"RxOutpatSID {rx_sid}: Correcting LocalDrugSID {current_local_drug_sid} → {correct_local_drug_sid} ({drug_with})")

            # Build corrected row
            corrected_line = f"({rx_sid}, '{rx_ien}', {sta3n}, {patient_sid}, '{patient_icn}', {correct_local_drug_sid}, '{local_drug_ien}', {national_drug_sid}, '{drug_without}', '{drug_with}',{rest_of_row}"
            output_lines.append(corrected_line)
        else:
            # Already correct
            output_lines.append(lines[i])
    else:
        warnings.append(f"RxOutpatSID {rx_sid}: Drug '{drug_with}' not found in LocalDrug table!")
        output_lines.append(lines[i])

# Write corrected file
output_path = '/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/RxOut.RxOutpat.sql'
with open(output_path, 'w') as f:
    f.write('\n'.join(output_lines))

print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
print(f"Total corrections made: {corrections_made}")
print(f"Warnings: {len(warnings)}")

if warnings:
    print("\nWarnings:")
    for warning in warnings:
        print(f"  {warning}")

print(f"\nCorrected file written to: {output_path}")
