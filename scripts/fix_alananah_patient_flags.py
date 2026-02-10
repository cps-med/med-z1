#!/usr/bin/env python3
"""
Fix Patient Flags section in Thompson-Alananah.sql

Issues:
1. Using subqueries with non-existent Sta3n column in Dim.PatientRecordFlag
2. Should use direct PatientRecordFlagSID values (14 and 15) for new flags

Solution:
- Use PatientRecordFlagSID = 14 for 'DIABETIC PATIENT'
- Use PatientRecordFlagSID = 15 for 'CANCER HISTORY'
- Use LocalFlagIEN = 12 and 13 (matching the dimension table)
- Remove Sta3n from subqueries
- Follow Bailey's proven pattern
"""

import re
from pathlib import Path

PROJECT_ROOT = Path("/Users/chuck/swdev/med/med-z1")
alananah_file = PROJECT_ROOT / "mock/sql-server/cdwwork/insert/Thompson-Alananah.sql"

def fix_patient_flags():
    """Replace Patient Flags section with corrected version"""
    print("Reading Thompson-Alananah.sql...")
    content = alananah_file.read_text()

    print("Replacing Patient Flags section...")

    # New corrected Patient Flags section based on Bailey's pattern
    new_flags_section = """-- Section 8.4: PATIENT FLAGS (2 total)
-- =====================================================
PRINT '  Section 8.4: Patient Flags (2 flags: Diabetes Management - ACTIVE, Cancer Survivor - ACTIVE)';
GO

INSERT INTO SPatient.PatientRecordFlagAssignment
(
    PatientSID, PatientRecordFlagSID, FlagName, FlagCategory, FlagSourceType,
    NationalFlagIEN, LocalFlagIEN, IsActive, AssignmentStatus,
    AssignmentDateTime, InactivationDateTime,
    OwnerSiteSta3n, OriginatingSiteSta3n, LastUpdateSiteSta3n,
    ReviewFrequencyDays, ReviewNotificationDays, LastReviewDateTime, NextReviewDateTime
)
VALUES
-- Flag 1: DIABETIC PATIENT (Category II Local, ACTIVE)
(2002, 14, 'DIABETIC PATIENT', 'II', 'L', NULL, 12,
 1, 'ACTIVE', '2012-04-15 10:00:00', NULL,
 '516', '516', '516', 90, 7, '2024-12-01 10:00:00', '2025-03-01 10:00:00'),

-- Flag 2: CANCER HISTORY (Category II Local, ACTIVE)
(2002, 15, 'CANCER HISTORY', 'II', 'L', NULL, 13,
 1, 'ACTIVE', '2012-07-02 14:00:00', NULL,
 '516', '516', '516', 365, 30, '2024-10-01 10:00:00', '2025-10-01 10:00:00');
GO

PRINT '    Alananah Thompson: 2 patient flags inserted';
PRINT '    Flag 1: DIABETIC PATIENT (Cat II Local) - ACTIVE';
PRINT '    Flag 2: CANCER HISTORY (Cat II Local) - ACTIVE';
GO"""

    # Find and replace the Patient Flags section
    # Pattern starts with "-- Section 8.4: PATIENT FLAGS" and ends before next section or final prints
    pattern = r"-- Section 8\.4: PATIENT FLAGS.*?PRINT '    Flag 2: Cancer Survivor.*?GO"

    content = re.sub(pattern, new_flags_section, content, count=1, flags=re.DOTALL)
    print("  ✓ Patient Flags section replaced")

    print("Writing updated file...")
    alananah_file.write_text(content)
    print(f"  ✓ File updated: {alananah_file}")

def main():
    print("=" * 70)
    print("Fixing Patient Flags in Thompson-Alananah.sql")
    print("=" * 70)
    print()

    fix_patient_flags()

    print()
    print("=" * 70)
    print("✅ Patient Flags fixed!")
    print("=" * 70)
    print()
    print("Changes made:")
    print("  ✓ Removed subqueries with invalid Sta3n reference")
    print("  ✓ Using direct PatientRecordFlagSID values:")
    print("    - SID 14: 'DIABETIC PATIENT' (LocalFlagIEN 12)")
    print("    - SID 15: 'CANCER HISTORY' (LocalFlagIEN 13)")
    print("  ✓ Added all required columns matching Bailey's pattern")
    print("  ✓ Removed PatientRecordFlagHistory inserts (simplified)")
    print()
    print("Note: These flags require the updated Dim.PatientRecordFlag.sql")
    print("      to be loaded first (which adds SIDs 14 and 15)")
    print()
    print("Next: Re-run create + insert master scripts")

if __name__ == "__main__":
    main()
