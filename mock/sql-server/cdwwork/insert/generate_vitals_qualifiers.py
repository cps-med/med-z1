#!/usr/bin/env python3
"""
Generate mock vital sign qualifier link data for CDWWork database
Links vitals to qualifiers (position, site, cuff size, method)
Approximately 60-70% of vitals will have qualifiers
"""

import random
from typing import List, Tuple

# Estimate: ~36 patients * ~40 vitals average * ~6 vital types = ~8,640 vitals
# We'll estimate VitalSignSID range based on the generation script
# For simplicity, we'll generate qualifiers for VitalSignSIDs 1-10000

# Qualifier patterns by vital type:
# BP (VitalTypeSID=1): Position + Site + Cuff Size (common)
# Temperature (VitalTypeSID=2): Method
# Others: Less common qualifiers

# Qualifiers (from Dim.VitalQualifier)
POSITION_QUALIFIERS = [1, 2, 3, 4]  # SITTING, STANDING, LYING, SUPINE
SITE_QUALIFIERS = [5, 6, 7, 8]      # LEFT ARM, RIGHT ARM, LEFT LEG, RIGHT LEG
CUFF_SIZE_QUALIFIERS = [9, 10, 11, 12]  # ADULT, LARGE ADULT, PEDIATRIC, THIGH
METHOD_QUALIFIERS = [13, 14, 15, 16]    # ORAL, RECTAL, TYMPANIC, AXILLARY

def generate_bp_qualifiers(vital_sign_sid: int) -> List[Tuple[int, int]]:
    """Generate qualifiers for BP measurement"""
    qualifiers = []

    # 80% of BP measurements have qualifiers
    if random.random() < 0.80:
        # Position (always if qualified)
        qualifiers.append((vital_sign_sid, random.choice(POSITION_QUALIFIERS)))

        # Site (always if qualified)
        qualifiers.append((vital_sign_sid, random.choice(SITE_QUALIFIERS)))

        # Cuff size (70% of time)
        if random.random() < 0.70:
            qualifiers.append((vital_sign_sid, random.choice(CUFF_SIZE_QUALIFIERS)))

    return qualifiers

def generate_temperature_qualifiers(vital_sign_sid: int) -> List[Tuple[int, int]]:
    """Generate qualifiers for Temperature measurement"""
    qualifiers = []

    # 70% of temp measurements have method qualifier
    if random.random() < 0.70:
        qualifiers.append((vital_sign_sid, random.choice(METHOD_QUALIFIERS)))

    return qualifiers

def generate_other_qualifiers(vital_sign_sid: int) -> List[Tuple[int, int]]:
    """Generate qualifiers for other vital types (less common)"""
    qualifiers = []

    # 30% of other vitals have position qualifier
    if random.random() < 0.30:
        qualifiers.append((vital_sign_sid, random.choice(POSITION_QUALIFIERS)))

    return qualifiers

def generate_qualifiers_by_vital_type():
    """
    Generate qualifiers for all vitals
    We need to know which VitalSignSID corresponds to which VitalTypeSID
    For simplicity, we'll use a pattern-based approach
    """
    qualifiers = []

    # From the vitals generation script, we know:
    # - ~36 patients
    # - ~30-50 vitals per patient
    # - Each vital can have multiple measurements (BP, T, P, R, WT, HT, PN, POX)
    #
    # Actual total from generate_vitals_data.py: 7,801 VitalSign records
    # We'll apply qualifiers based on a rough distribution:
    # - VitalSignSIDs with pattern mod 8 = 1 → BP (get BP qualifiers)
    # - VitalSignSIDs with pattern mod 8 = 2 → Temperature (get method qualifiers)
    # - Others → occasional position qualifiers

    max_vital_sign_sid = 7801  # Actual count from vitals generation

    for vital_sign_sid in range(1, max_vital_sign_sid + 1):
        # Determine vital type based on pattern (rough approximation)
        pattern = vital_sign_sid % 8

        if pattern == 1:  # ~12.5% are BP
            qualifiers.extend(generate_bp_qualifiers(vital_sign_sid))
        elif pattern == 2:  # ~12.5% are Temperature
            qualifiers.extend(generate_temperature_qualifiers(vital_sign_sid))
        else:  # Others
            qualifiers.extend(generate_other_qualifiers(vital_sign_sid))

    return qualifiers

def main():
    """Generate SQL INSERT script for vital sign qualifiers"""
    print("-- Insert seed data: Vital.VitalSignQualifier")
    print("-- Links vitals to qualifiers (position, site, cuff size, method)")
    print("-- Approximately 60-70% of vitals have qualifiers")
    print("")
    print("USE CDWWork;")
    print("GO")
    print("")
    print("SET QUOTED_IDENTIFIER ON;")
    print("GO")
    print("")
    print("SET IDENTITY_INSERT Vital.VitalSignQualifier ON;")
    print("GO")
    print("")

    qualifiers = generate_qualifiers_by_vital_type()

    # Generate INSERT statements in batches of 1000
    batch_size = 1000
    total_qualifiers = len(qualifiers)

    qualifier_sid = 1
    for batch_start in range(0, total_qualifiers, batch_size):
        batch_end = min(batch_start + batch_size, total_qualifiers)
        batch = qualifiers[batch_start:batch_end]

        print(f"-- Batch {batch_start // batch_size + 1} (qualifiers {batch_start + 1} - {batch_end})")
        print("INSERT INTO Vital.VitalSignQualifier")
        print("    (VitalSignQualifierSID, VitalSignSID, VitalQualifierSID)")
        print("VALUES")

        for i, (vital_sign_sid, vital_qualifier_sid) in enumerate(batch):
            if i < len(batch) - 1:
                print(f"    ({qualifier_sid}, {vital_sign_sid}, {vital_qualifier_sid}),")
            else:
                print(f"    ({qualifier_sid}, {vital_sign_sid}, {vital_qualifier_sid});")
            qualifier_sid += 1

        print("GO")
        print("")

    print("SET IDENTITY_INSERT Vital.VitalSignQualifier OFF;")
    print("GO")
    print("")
    print(f"PRINT 'Inserted {total_qualifiers} vital sign qualifiers';")
    print("GO")
    print("")
    print("-- Verify")
    print("SELECT vq.QualifierType, COUNT(*) as QualifierCount")
    print("FROM Vital.VitalSignQualifier vsq")
    print("JOIN Dim.VitalQualifier vq ON vsq.VitalQualifierSID = vq.VitalQualifierSID")
    print("GROUP BY vq.QualifierType")
    print("ORDER BY vq.QualifierType;")
    print("GO")

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()
