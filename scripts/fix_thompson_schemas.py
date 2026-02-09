#!/usr/bin/env python3
"""
Fix Thompson siblings INSERT scripts to match CDWWork schema.

This script corrects column names in Thompson-Bailey.sql, Thompson-Alananah.sql,
and Thompson-Joe.sql to match the actual CDWWork database schema.

The Thompson INSERT scripts were written with incorrect column names that don't
match the CREATE scripts, causing hundreds of "Invalid column name" errors.
"""

import re
from pathlib import Path

# Base directory for CDWWork INSERT scripts
INSERT_DIR = Path("/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert")

# File paths
BAILEY_FILE = INSERT_DIR / "Thompson-Bailey.sql"
ALANANAH_FILE = INSERT_DIR / "Thompson-Alananah.sql"
JOE_FILE = INSERT_DIR / "Thompson-Joe.sql"

# Schema fixes: map of incorrect column names to correct ones
SCHEMA_FIXES = {
    # SPatient.SPatientAddress fixes
    "PatientAddressSID": "SPatientAddressSID",
    "AddressLine1": "StreetAddress1",
    "AddressLine2": "StreetAddress2",
    "AddressLine3": "StreetAddress3",

    # Vital.VitalSign fixes (if any)
    "VitalResultNumeric": "VitalResult",  # Check actual schema

    # RxOut.RxOutpat fixes (if any)
    "LocalDrugNameWithDose": "LocalDrugNameWithDose",  # May be correct, need to verify
    "PrescribingProviderSID": "OrderingProviderSID",  # Check actual schema
    "PrescribingProviderName": "OrderingProviderName",
}

def fix_address_insert_block(content: str, patient_sid: int, patient_ien: str, sta3n_map: dict) -> str:
    """
    Fix SPatient.SPatientAddress INSERT block to match correct schema.

    Args:
        content: File content
        patient_sid: PatientSID for this patient (2001, 2002, 2003)
        patient_ien: PatientIEN for this patient ('PtIEN2001', etc.)
        sta3n_map: Dictionary mapping address ordinal to Sta3n codes

    Returns:
        Fixed content
    """
    # Find the SPatient.SPatientAddress INSERT block
    pattern = r'INSERT INTO SPatient\.SPatientAddress\s*\([^)]+\)\s*VALUES[^;]+;'

    def replace_address_block(match):
        block = match.group(0)

        # Replace column list
        new_columns = """INSERT INTO SPatient.SPatientAddress
(
    SPatientAddressSID,
    PatientSID,
    PatientIEN,
    Sta3n,
    OrdinalNumber,
    AddressType,
    StreetAddress1,
    StreetAddress2,
    StreetAddress3,
    City,
    County,
    [State],
    StateSID,
    Zip,
    Zip4,
    PostalCode,
    Country,
    CountrySID,
    EmploymentStatus
)"""
        # Extract VALUES section
        values_match = re.search(r'VALUES(.+)', block, re.DOTALL)
        if values_match:
            return new_columns + "\nVALUES" + values_match.group(1)
        return block

    return re.sub(pattern, replace_address_block, content, flags=re.DOTALL)

def apply_simple_fixes(content: str) -> str:
    """Apply simple find-and-replace fixes for column names."""
    for old_name, new_name in SCHEMA_FIXES.items():
        # Only replace in column lists (lines with commas or in parentheses)
        # Don't replace in comments
        content = re.sub(
            rf'\b{old_name}\b(?=\s*[,)])',  # Match column name followed by comma or close paren
            new_name,
            content
        )
    return content

def fix_thompson_file(file_path: Path):
    """Fix a single Thompson siblings INSERT script."""
    print(f"Processing {file_path.name}...")

    # Read original content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Apply fixes
    fixed_content = original_content

    # Simple column name fixes
    fixed_content = apply_simple_fixes(fixed_content)

    # TODO: Add more complex fixes for specific sections if needed
    # For now, let's just handle the simple column name replacements

    # Write fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    # Count replacements
    changes = sum(1 for old in SCHEMA_FIXES.keys() if old in original_content and old not in fixed_content)
    print(f"  ✓ Applied {changes} schema fixes")

def main():
    """Fix all three Thompson siblings INSERT scripts."""
    print("=" * 60)
    print("Fixing Thompson Siblings INSERT Scripts")
    print("=" * 60)
    print()

    files_to_fix = [BAILEY_FILE, ALANANAH_FILE, JOE_FILE]

    for file_path in files_to_fix:
        if not file_path.exists():
            print(f"  ✗ File not found: {file_path}")
            continue

        try:
            fix_thompson_file(file_path)
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")

    print()
    print("=" * 60)
    print("Schema fixes complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Re-run CDWWork INSERT scripts to verify fixes")
    print("2. Check for any remaining schema errors")
    print("3. Run complete ETL pipeline if inserts succeed")

if __name__ == "__main__":
    main()
