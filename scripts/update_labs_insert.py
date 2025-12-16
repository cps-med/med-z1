#!/usr/bin/env python3
"""
Update Chem.LabChem INSERT script to include valid LocationSID values.

Changes:
- Sta3n 508 → LocationSID 33 (Laboratory - Main Lab)
- Sta3n 516 → LocationSID 85 (Laboratory - Main Lab)
- Sta3n 552 → LocationSID 137 (Laboratory - Main Lab)

This script updates the INSERT column list to include LocationSID and
updates all 84 lab result records with appropriate location values.
"""

import re

# LocationSID mapping based on Sta3n
LOCATION_MAPPING = {
    '508': '33',   # Laboratory - Main Lab, Sta3n 508
    '516': '85',   # Laboratory - Main Lab, Sta3n 516
    '552': '137'   # Laboratory - Main Lab, Sta3n 552
}

input_file = '/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Chem.LabChem.sql'
output_file = input_file  # Overwrite in place

print(f"Reading {input_file}...")

with open(input_file, 'r') as f:
    content = f.read()

# Count original INSERT statements
original_insert_count = content.count("INSERT INTO [Chem].[LabChem]")
print(f"Found {original_insert_count} INSERT statements")

# ============================================================================
# Step 1: Update INSERT column list to include LocationSID
# ============================================================================
print("\nStep 1: Updating INSERT column list to include LocationSID...")

old_columns = (
    "INSERT INTO [Chem].[LabChem] "
    "([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], "
    "[ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], "
    "[VistaPackage], [Sta3n], [SpecimenType])"
)

new_columns = (
    "INSERT INTO [Chem].[LabChem] "
    "([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], "
    "[ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], "
    "[VistaPackage], [LocationSID], [Sta3n], [SpecimenType])"
)

content = content.replace(old_columns, new_columns)
print(f"  - Updated INSERT column list ({content.count(new_columns)} occurrences)")

# ============================================================================
# Step 2: Update VALUES rows to include LocationSID based on Sta3n
# ============================================================================
print("\nStep 2: Updating VALUES rows with LocationSID...")

changes_made = 0

for sta3n, location_sid in LOCATION_MAPPING.items():
    # Pattern: 'CH', <sta3n>, 'Serum'
    # Replace with: 'CH', <location_sid>, <sta3n>, 'Serum'
    old_pattern = f"'CH', {sta3n}, 'Serum'"
    new_pattern = f"'CH', {location_sid}, {sta3n}, 'Serum'"

    count = content.count(old_pattern)
    content = content.replace(old_pattern, new_pattern)
    changes_made += count

    print(f"  - Sta3n {sta3n} → LocationSID {location_sid}: {count} records updated")

# ============================================================================
# Step 3: Write updated file
# ============================================================================
print(f"\nStep 3: Writing updated file to {output_file}...")

with open(output_file, 'w') as f:
    f.write(content)

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print(f"Updated {changes_made} lab result records with LocationSID values")
print(f"Location mapping applied:")
for sta3n, location_sid in LOCATION_MAPPING.items():
    print(f"  - Sta3n {sta3n} → LocationSID {location_sid} (Laboratory - Main Lab)")
print("=" * 70)
