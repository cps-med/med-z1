#!/usr/bin/env python3
"""
Comprehensive fix for Thompson siblings INSERT scripts.

This script rewrites Thompson INSERT statements to match the actual CDWWork schema
by using the working INSERT scripts as templates.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Paths
INSERT_DIR = Path("/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert")
BAILEY_FILE = INSERT_DIR / "Thompson-Bailey.sql"
ALANANAH_FILE = INSERT_DIR / "Thompson-Alananah.sql"
JOE_FILE = INSERT_DIR / "Thompson-Joe.sql"

# Map of table names to their working INSERT script files
SCHEMA_REFERENCE_FILES = {
    "SPatient.SPatientAddress": "SPatient.SPatientAddress.sql",
    "SPatient.SPatientPhone": "SPatient.SPatientPhone.sql",
    "SPatient.SPatientInsurance": "SPatient.SPatientInsurance.sql",
    "SPatient.SPatientDisability": "SPatient.SPatientDisability.sql",
    "SPatient.PatientRecordFlagAssignment": "SPatient.PatientRecordFlagAssignment.sql",
    "SPatient.PatientRecordFlagHistory": "SPatient.PatientRecordFlagHistory.sql",
    "Allergy.PatientAllergy": "Allergy.PatientAllergy.sql",
    "Allergy.PatientAllergyReaction": "Allergy.PatientAllergyReaction.sql",
    "RxOut.RxOutpat": "RxOut.RxOutpat.sql",
    "Inpat.Inpatient": "Inpat.Inpatient.sql",
    "TIU.TIUDocument_8925": "TIU.TIUDocument_8925.sql",
    "TIU.TIUDocumentText": "TIU.TIUDocumentText.sql",
    "Immunization.PatientImmunization": "Immunization.PatientImmunization.sql",
    "Outpat.ProblemList": "Outpat.ProblemList.sql",
    "Chem.LabChem": "Chem.LabChem.sql",
    "Vital.VitalSign": "Vital.VitalSign.sql",
}


def extract_column_list(file_path: Path, table_name: str) -> List[str]:
    """Extract the column list from a working INSERT script."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find INSERT INTO pattern
    pattern = rf'INSERT INTO {re.escape(table_name)}\s*\((.*?)\)\s*VALUES'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if not match:
        return []

    column_block = match.group(1)
    # Extract column names, handling square brackets for reserved words
    columns = []
    for line in column_block.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        # Remove trailing comma and split on comma
        parts = re.split(r',\s*', line.rstrip(','))
        for part in parts:
            part = part.strip()
            if part and not part.startswith('--'):
                columns.append(part)

    return columns


def get_correct_schemas() -> Dict[str, List[str]]:
    """Load correct column schemas from working INSERT scripts."""
    schemas = {}

    for table_name, ref_file in SCHEMA_REFERENCE_FILES.items():
        ref_path = INSERT_DIR / ref_file
        if ref_path.exists():
            columns = extract_column_list(ref_path, table_name)
            if columns:
                schemas[table_name] = columns
                print(f"  ✓ Loaded schema for {table_name}: {len(columns)} columns")
            else:
                print(f"  ✗ Could not extract schema for {table_name}")
        else:
            print(f"  ✗ Reference file not found: {ref_file}")

    return schemas


def fix_insert_statement(content: str, table_name: str, correct_columns: List[str]) -> str:
    """
    Fix an INSERT statement to use the correct column list.

    This preserves the VALUES section and comments, just replaces the column list.
    """
    # Find all INSERT INTO blocks for this table
    pattern = rf'(INSERT INTO {re.escape(table_name)}\s*)\((.*?)\)(\s*VALUES)'

    def replace_columns(match):
        prefix = match.group(1)  # "INSERT INTO TableName "
        suffix = match.group(3)  # " VALUES"

        # Build correct column list with nice formatting
        formatted_columns = "(\n    " + ",\n    ".join(correct_columns) + "\n)"

        return prefix + formatted_columns + suffix

    fixed_content = re.sub(pattern, replace_columns, content, flags=re.DOTALL | re.IGNORECASE)

    return fixed_content


def fix_thompson_file(file_path: Path, schemas: Dict[str, List[str]]):
    """Fix all INSERT statements in a Thompson file."""
    print(f"\nProcessing {file_path.name}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes_applied = 0

    for table_name, correct_columns in schemas.items():
        if f"INSERT INTO {table_name}" in content:
            print(f"  Fixing {table_name}...")
            content = fix_insert_statement(content, table_name, correct_columns)
            fixes_applied += 1

    if content != original_content:
        # Create backup
        backup_path = file_path.with_suffix('.sql.backup_schema_fix')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Write fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Fixed {fixes_applied} INSERT statements")
        print(f"  ✓ Backup saved to {backup_path.name}")
    else:
        print(f"  ℹ No changes needed")


def main():
    """Main entry point."""
    print("=" * 70)
    print("  Thompson Siblings Schema Fix - Comprehensive Rewrite")
    print("=" * 70)
    print()
    print("Step 1: Loading correct schemas from working INSERT scripts...")
    print()

    schemas = get_correct_schemas()

    if not schemas:
        print("\n✗ ERROR: Could not load any reference schemas!")
        return 1

    print(f"\n✓ Loaded {len(schemas)} table schemas")
    print()
    print("Step 2: Fixing Thompson siblings INSERT scripts...")

    files_to_fix = [BAILEY_FILE, ALANANAH_FILE, JOE_FILE]

    for file_path in files_to_fix:
        if file_path.exists():
            fix_thompson_file(file_path, schemas)
        else:
            print(f"\n✗ File not found: {file_path}")

    print()
    print("=" * 70)
    print("  Schema fixes complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Review the changes in the Thompson-*.sql files")
    print("  2. Re-run CDWWork INSERT scripts:")
    print("     cd mock/sql-server/cdwwork/insert")
    print("     sqlcmd -S 127.0.0.1,1433 -U sa -P 'MyS3cur3P@ssw0rd' -C -i _master.sql")
    print("  3. Check for any remaining schema errors")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
