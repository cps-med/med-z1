#!/usr/bin/env python3
"""
Complete fix for Thompson-Alananah vitals section

Issues found:
1. VitalSignSID range conflicts with Bailey (both use 9001-9231)
2. Corrupted data on lines 401-419 (missing comma, garbage characters)
3. Duplicate VitalSignSID values within Alananah's own data

Solution:
- Extract Bailey's working vitals section
- Renumber VitalSignSID from 10001-10231 (unique range for Alananah)
- Update PatientSID from 2001 to 2002
- Keep Bailey's vitals structure (avoid corruption)
- Then apply Alananah's specific weight updates via separate script
"""

import re
from pathlib import Path

PROJECT_ROOT = Path("/Users/chuck/swdev/med/med-z1")
bailey_file = PROJECT_ROOT / "mock/sql-server/cdwwork/insert/Thompson-Bailey.sql"
alananah_file = PROJECT_ROOT / "mock/sql-server/cdwwork/insert/Thompson-Alananah.sql"

def extract_bailey_vitals():
    """Extract Bailey's complete working vitals section"""
    print("Reading Bailey's vitals section...")
    bailey_content = bailey_file.read_text()

    # Find vitals section between SET IDENTITY_INSERT ON and OFF
    pattern = r"(SET IDENTITY_INSERT Vital\.VitalSign ON;.*?SET IDENTITY_INSERT Vital\.VitalSign OFF;)"
    match = re.search(pattern, bailey_content, re.DOTALL)

    if not match:
        raise ValueError("Could not find Bailey's vitals section")

    bailey_vitals = match.group(1)
    print(f"  ✓ Extracted {len(bailey_vitals)} characters")

    return bailey_vitals

def adapt_for_alananah(bailey_vitals):
    """Adapt Bailey's vitals for Alananah with unique IDs"""
    print("Adapting vitals for Alananah...")

    # Step 1: Renumber VitalSignSID from 9001-9231 to 10001-10231
    def renumber_vital_id(match):
        old_id = int(match.group(1))
        new_id = old_id + 1000  # 9001 -> 10001, etc.
        return f"({new_id},"

    adapted = re.sub(r'\((\d{4}),', renumber_vital_id, bailey_vitals)
    print(f"  ✓ Renumbered VitalSignSID range: 10001-10231")

    # Step 2: Change PatientSID from 2001 to 2002
    adapted = adapted.replace('2001, 5,', '2002, 5,')  # Height vital
    adapted = adapted.replace('2001, 6,', '2002, 6,')  # Weight vital
    adapted = adapted.replace('2001, 7,', '2002, 7,')  # Temp vital
    adapted = adapted.replace('2001, 1,', '2002, 1,')  # BP vital
    adapted = adapted.replace('2001, 2,', '2002, 2,')  # Pulse vital
    adapted = adapted.replace('2001, 3,', '2002, 3,')  # Respiration vital
    adapted = adapted.replace('2001, 9,', '2002, 9,')  # O2 sat vital
    adapted = adapted.replace('2001, 10,', '2002, 10,')  # Pain vital
    print(f"  ✓ Changed PatientSID: 2001 -> 2002")

    # Step 3: Update comment to reflect Alananah
    adapted = adapted.replace(
        'Inserting Bailey Thompson vitals',
        'Inserting Alananah Thompson vitals'
    )
    adapted = adapted.replace(
        'Bailey Thompson vitals inserted',
        'Alananah Thompson vitals inserted (231 readings, 2010-2025 - using Bailey structure)'
    )

    return adapted

def replace_vitals_in_alananah(new_vitals):
    """Replace corrupted vitals section in Alananah file"""
    print("Replacing vitals section in Thompson-Alananah.sql...")

    content = alananah_file.read_text()

    # Find and replace vitals section
    pattern = r"SET IDENTITY_INSERT Vital\.VitalSign ON;.*?SET IDENTITY_INSERT Vital\.VitalSign OFF;"
    content = re.sub(pattern, new_vitals.strip(), content, count=1, flags=re.DOTALL)

    alananah_file.write_text(content)
    print(f"  ✓ Wrote updated file: {alananah_file}")

def main():
    print("=" * 70)
    print("Fixing Thompson-Alananah Vitals Section (Complete Replacement)")
    print("=" * 70)
    print()

    # Step 1: Extract Bailey's working vitals
    bailey_vitals = extract_bailey_vitals()

    # Step 2: Adapt for Alananah with unique IDs
    alananah_vitals = adapt_for_alananah(bailey_vitals)

    # Step 3: Replace in Alananah file
    replace_vitals_in_alananah(alananah_vitals)

    print()
    print("=" * 70)
    print("✅ Vitals section fixed!")
    print("=" * 70)
    print()
    print("Changes made:")
    print("  ✓ VitalSignSID range: 9001-9231 -> 10001-10231 (no conflicts)")
    print("  ✓ PatientSID: 2001 -> 2002")
    print("  ✓ Removed corrupted lines 401-419")
    print("  ✓ Fixed missing comma on line 400")
    print()
    print("Note: This uses Bailey's weight values (male). To apply Alananah's")
    print("      female weight trajectory, run:")
    print("      python3 scripts/update_alananah_vitals_weight.py")
    print()
    print("Next step: Test SQL Server execution")

if __name__ == "__main__":
    main()
