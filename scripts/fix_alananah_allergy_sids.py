#!/usr/bin/env python3
"""
Fix Allergy SID conflicts in Thompson-Alananah.sql

Issue: Alananah is reusing Bailey's allergy SID ranges
- PatientAllergySID: 9001-9002 (Bailey's range)
- PatientAllergyReactionSID: 9001-9003 (Bailey's range)

Solution: Renumber to unique ranges
- PatientAllergySID: 10001-10002 (Alananah's unique range)
- PatientAllergyReactionSID: 10001-10003 (Alananah's unique range)
"""

import re
from pathlib import Path

PROJECT_ROOT = Path("/Users/chuck/swdev/med/med-z1")
alananah_file = PROJECT_ROOT / "mock/sql-server/cdwwork/insert/Thompson-Alananah.sql"

def fix_allergy_sids():
    """Renumber allergy SIDs from 9001-9002 to 10001-10002"""
    print("Reading Thompson-Alananah.sql...")
    content = alananah_file.read_text()

    print("Fixing Allergy SID conflicts...")

    # Step 1: Update comment header
    content = content.replace(
        '-- PatientAllergySID range: 9001-9002 (allocated for Bailey)',
        '-- PatientAllergySID range: 10001-10002 (allocated for Alananah)'
    )
    content = content.replace(
        '-- PatientAllergyReactionSID range: 9001-9003 (allocated for Bailey)',
        '-- PatientAllergyReactionSID range: 10001-10003 (allocated for Alananah)'
    )
    print("  ✓ Updated comment headers")

    # Step 2: Find and replace PatientAllergySID values in INSERT
    # Pattern: (9001, 2002, 1, 2, 'PENICILLIN',
    # Replace: (10001, 2002, 1, 2, 'PENICILLIN',
    content = content.replace('(9001, 2002, 1, 2, \'PENICILLIN\'',
                              '(10001, 2002, 1, 2, \'PENICILLIN\'')
    content = content.replace('(9002, 2002, 7, 3, \'MORPHINE SULFATE\'',
                              '(10002, 2002, 7, 3, \'MORPHINE SULFATE\'')
    print("  ✓ Renumbered PatientAllergySID: 9001→10001, 9002→10002")

    # Step 3: Find and replace PatientAllergyReactionSID values
    # Pattern: (9001, 9001, 2),   -- RASH
    # Replace: (10001, 10001, 2),   -- RASH

    # Find the allergy reactions section
    reactions_pattern = r'INSERT INTO Allergy\.PatientAllergyReaction \(PatientAllergyReactionSID, PatientAllergySID, ReactionSID\)\s*VALUES\s*(.*?);'

    def renumber_reactions(match):
        reactions_block = match.group(1)
        # Replace (9001, 9001, -> (10001, 10001,
        reactions_block = reactions_block.replace('(9001, 9001,', '(10001, 10001,')
        # Replace (9002, 9002, -> (10002, 10002,
        reactions_block = reactions_block.replace('(9002, 9002,', '(10002, 10002,')
        # Replace (9003, 9002, -> (10003, 10002,
        reactions_block = reactions_block.replace('(9003, 9002,', '(10003, 10002,')
        return f'INSERT INTO Allergy.PatientAllergyReaction (PatientAllergyReactionSID, PatientAllergySID, ReactionSID)\nVALUES\n{reactions_block};'

    content = re.sub(reactions_pattern, renumber_reactions, content, flags=re.DOTALL)
    print("  ✓ Renumbered PatientAllergyReactionSID: 9001-9003 → 10001-10003")

    # Step 4: Update comments in reactions section
    content = content.replace('-- Allergy 9001: PENICILLIN', '-- Allergy 10001: PENICILLIN')
    content = content.replace('-- Allergy 9002: MORPHINE', '-- Allergy 10002: MORPHINE')
    print("  ✓ Updated comments")

    print("Writing updated file...")
    alananah_file.write_text(content)
    print(f"  ✓ File updated: {alananah_file}")

def main():
    print("=" * 70)
    print("Fixing Allergy SID Conflicts in Thompson-Alananah.sql")
    print("=" * 70)
    print()

    fix_allergy_sids()

    print()
    print("=" * 70)
    print("✅ Allergy SIDs fixed!")
    print("=" * 70)
    print()
    print("Changes made:")
    print("  ✓ PatientAllergySID: 9001-9002 → 10001-10002")
    print("  ✓ PatientAllergyReactionSID: 9001-9003 → 10001-10003")
    print()
    print("Bailey's ranges (unchanged):")
    print("  - PatientAllergySID: 9001-9002")
    print("  - PatientAllergyReactionSID: 9001-9003")
    print()
    print("Alananah's ranges (new, no conflicts):")
    print("  - PatientAllergySID: 10001-10002")
    print("  - PatientAllergyReactionSID: 10001-10003")
    print()
    print("Next: Re-run insert/_master.sql to reload data")

if __name__ == "__main__":
    main()
