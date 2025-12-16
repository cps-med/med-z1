#!/usr/bin/env python3
"""
Update Vital.VitalSign INSERT script to include valid LocationSID and Sta3n values.

Changes:
- Sta3n 402 → 508 (Atlanta), LocationSID NULL → 13 (Primary Care Clinic A)
- Sta3n 518 → 516 (Bay Pines), LocationSID NULL → 65 (Primary Care Clinic A)
- Sta3n 528 → 552 (Dayton), LocationSID NULL → 117 (Primary Care Clinic A)
- Sta3n 589 → 688 (Washington DC), LocationSID NULL → 169 (Primary Care Clinic A)
"""

import re

# Sta3n mapping: old → new
STA3N_MAPPING = {
    '402': '508',
    '518': '516',
    '528': '552',
    '589': '688'
}

# LocationSID mapping based on new Sta3n
LOCATION_MAPPING = {
    '508': '13',   # Primary Care Clinic A, Sta3n 508
    '516': '65',   # Primary Care Clinic A, Sta3n 516
    '552': '117',  # Primary Care Clinic A, Sta3n 552
    '688': '169'   # Primary Care Clinic A, Sta3n 688
}

input_file = '/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Vital.VitalSign.sql'
output_file = input_file  # Overwrite in place

print(f"Reading {input_file}...")

with open(input_file, 'r') as f:
    lines = f.readlines()

updated_lines = []
changes_made = 0

for line in lines:
    # Check if this is a data row (contains vital measurements)
    # Pattern: ends with 'N', 'N', <sta3n>),
    match = re.search(r"'N', 'N', (\d+)\)", line)

    if match:
        old_sta3n = match.group(1)

        if old_sta3n in STA3N_MAPPING:
            new_sta3n = STA3N_MAPPING[old_sta3n]
            new_location = LOCATION_MAPPING[new_sta3n]

            # Replace Sta3n value
            line = re.sub(
                r"'N', 'N', " + old_sta3n + r"\)",
                f"'N', 'N', {new_sta3n})",
                line
            )

            # Replace NULL LocationSID with valid value
            # Pattern: NULL, <staff_id>, 'N', 'N', <sta3n>)
            line = re.sub(
                r'NULL, (\d+), \'N\', \'N\', ' + new_sta3n + r'\)',
                f'{new_location}, \\1, \'N\', \'N\', {new_sta3n})',
                line
            )

            changes_made += 1

    updated_lines.append(line)

print(f"Writing updated file...")
with open(output_file, 'w') as f:
    f.writelines(updated_lines)

print(f"✅ Complete! Updated {changes_made} vital sign records")
print(f"   - Sta3n values mapped: {STA3N_MAPPING}")
print(f"   - LocationSID values assigned: {LOCATION_MAPPING}")
