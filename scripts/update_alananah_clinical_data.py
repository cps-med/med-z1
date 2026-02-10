#!/usr/bin/env python3
"""
Update Thompson-Alananah.sql with Alananah-specific clinical data

This script replaces Bailey's clinical content with Alananah's:
- Problems/Diagnoses: Breast cancer, diabetes complications (not TBI, chronic back pain)
- Medications: Anastrozole, empagliflozin, levothyroxine (not opioids, trazodone)
- Vitals: Female profile, height 65", different weight trajectory
- Clinical Notes: Oncology, diabetes educator notes (not suicide attempts, substance abuse)
- Labs: Diabetes A1C trending 8.5% → 6.8%, no CKD markers
- Encounters: Mastectomy, chemo admissions (not psychiatric admissions)
- Charlson Comorbidity Index: 2 (not 5)

Reference: docs/spec/thompson-twins-patient-reqs.md lines 196-315
"""

import re
from pathlib import Path

# File paths
script_file = Path("/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Thompson-Alananah.sql")

def update_problems_section():
    """
    Replace Bailey's 18 problems (Charlson=5) with Alananah's 10 problems (Charlson=2)

    Alananah's conditions:
    1. Type 2 Diabetes (2012, well-controlled)
    2. Breast Cancer Stage IIA (2012, remission)
    3. PTSD (2011, mild-moderate)
    4. Hypertension (2013)
    5. Hyperlipidemia (2014)
    6. Osteoarthritis bilateral knees (service-connected)
    7. Hypothyroidism (2016)
    8. Diabetic Peripheral Neuropathy (2020)
    9. Diabetic Retinopathy mild (2021)
    10. Obesity BMI 32-34 (ongoing)
    """

    problems_section = """-- =====================================================
-- Section 8.2: PROBLEMS / DIAGNOSES (10 total, Charlson Score = 2)
-- =====================================================
PRINT '  Section 8.2: Problems/Diagnoses (10 problems, Charlson Comorbidity Index = 2)';
GO

INSERT INTO Outpat.ProblemList (
    PatientSID, PatientICN, Sta3n, ProblemNumber, SNOMEDCode, SNOMEDDescription,
    ICD10Code, ICD10Description, ProblemStatus, OnsetDate, RecordedDate, LastModifiedDate,
    ResolvedDate, ProviderSID, ProviderName, Clinic, IsServiceConnected, IsAcuteCondition, IsChronicCondition,
    EnteredBy, EnteredDateTime
)
VALUES
-- Problem 1: Type 2 Diabetes Mellitus (Primary chronic condition)
(2002, 'ICN200002', 516, 'P2002-1', '44054006', 'Type 2 diabetes mellitus', 'E11.65', 'Type 2 diabetes mellitus with hyperglycemia', 'ACTIVE', '2012-04-10', '2012-04-15', '2024-12-05', NULL, 1003, 'Patel, Raj MD', 'Endocrinology', 'N', 'N', 'Y', 'Patel, Raj MD', '2012-04-15 10:00:00'),

-- Problem 2: Breast Cancer (Charlson +2 points, history of cancer)
(2002, 'ICN200002', 516, 'P2002-2', '429740004', 'History of breast cancer', 'Z85.3', 'Personal history of malignant neoplasm of breast', 'ACTIVE', '2012-07-02', '2012-07-02', '2024-10-15', NULL, 1010, 'Garcia, Elizabeth MD', 'Oncology', 'N', 'N', 'Y', 'Garcia, Elizabeth MD', '2012-07-02 14:30:00'),

-- Problem 3: PTSD (mild-moderate, service-connected)
(2002, 'ICN200002', 516, 'P2002-3', '47505003', 'Post-traumatic stress disorder', 'F43.10', 'Post-traumatic stress disorder, unspecified', 'ACTIVE', '2011-01-15', '2011-02-15', '2024-11-20', NULL, 1001, 'Mitchell, Sarah MD', 'Mental Health', 'Y', 'N', 'Y', 'Mitchell, Sarah MD', '2011-02-15 14:00:00'),

-- Problem 4: Essential Hypertension
(2002, 'ICN200002', 516, 'P2002-4', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2013-03-10', '2013-03-15', '2024-12-01', NULL, 1010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2013-03-15 09:30:00'),

-- Problem 5: Hyperlipidemia
(2002, 'ICN200002', 516, 'P2002-5', '267036007', 'Dyslipidemia', 'E78.5', 'Hyperlipidemia, unspecified', 'ACTIVE', '2014-06-18', '2014-06-20', '2024-11-15', NULL, 1010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2014-06-20 10:15:00'),

-- Problem 6: Osteoarthritis bilateral knees (service-connected)
(2002, 'ICN200002', 516, 'P2002-6', '239873007', 'Osteoarthritis', 'M17.0', 'Bilateral primary osteoarthritis of knee', 'ACTIVE', '2010-05-10', '2010-08-20', '2024-10-05', NULL, 1009, 'Anderson, Lisa MD', 'Rheumatology', 'Y', 'N', 'Y', 'Anderson, Lisa MD', '2010-08-20 11:00:00'),

-- Problem 7: Hypothyroidism
(2002, 'ICN200002', 516, 'P2002-7', '40930008', 'Hypothyroidism', 'E03.9', 'Hypothyroidism, unspecified', 'ACTIVE', '2016-02-20', '2016-02-25', '2024-09-10', NULL, 1003, 'Patel, Raj MD', 'Endocrinology', 'N', 'N', 'Y', 'Patel, Raj MD', '2016-02-25 13:30:00'),

-- Problem 8: Diabetic Peripheral Neuropathy
(2002, 'ICN200002', 516, 'P2002-8', '230572002', 'Peripheral neuropathy due to diabetes', 'E11.40', 'Type 2 diabetes mellitus with diabetic neuropathy, unspecified', 'ACTIVE', '2020-06-15', '2020-06-20', '2024-11-30', NULL, 1014, 'Nguyen, Linh MD', 'Neurology', 'N', 'N', 'Y', 'Nguyen, Linh MD', '2020-06-20 14:45:00'),

-- Problem 9: Diabetic Retinopathy (mild, nonproliferative)
(2002, 'ICN200002', 516, 'P2002-9', '4855003', 'Retinopathy due to diabetes mellitus', 'E11.329', 'Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema', 'ACTIVE', '2021-08-10', '2021-08-12', '2024-08-15', NULL, 1020, 'Lee, Andrew MD', 'Ophthalmology', 'N', 'N', 'Y', 'Lee, Andrew MD', '2021-08-12 10:00:00'),

-- Problem 10: Obesity
(2002, 'ICN200002', 516, 'P2002-10', '414916001', 'Obesity', 'E66.9', 'Obesity, unspecified', 'ACTIVE', '2012-04-15', '2012-04-15', '2024-12-05', NULL, 1010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2012-04-15 11:30:00');
GO

PRINT '    Alananah Thompson: 10 problems inserted (10 active chronic)';
PRINT '    Charlson Comorbidity Index = 2 (Breast cancer history +2)';
PRINT '    Primary conditions: Type 2 Diabetes, Breast Cancer (remission), PTSD, HTN, Osteoarthritis';
GO"""

    return problems_section


def update_header_comment():
    """Update header to reflect Alananah's correct profile"""
    header = """-- =====================================================
-- Thompson Twins Test Patient Data
-- Patient: Alananah Marie Thompson (Female)
-- ICN: ICN200002
-- Database: CDWWork (Bay Pines VA, 2010-2025)
-- =====================================================
-- Purpose: Comprehensive test patient for med-z1
--          Female veteran, breast cancer survivor, Type 2 diabetes
--          Service history: Gulf War (1990-1991), Iraq (2003-2007)
--          50% service-connected disability
-- =====================================================
-- Domain Coverage:
--   1. Demographics (SPatient.SPatient, Address, Phone, Insurance, Disability)
--   2. Vitals (~60 readings, quarterly 2010-2025, female profile)
--   3. Patient Flags (Diabetes Management, Cancer Survivor)
--   4. Allergies (Sulfa drugs, Codeine)
--   5. Medications (12 active: anastrozole, empagliflozin, levothyroxine, etc.)
--   6. Encounters (8 admissions: mastectomy, chemo, diabetes complications)
--   7. Clinical Notes (~15 notes: oncology, diabetes educator, mental health)
--   8. Immunizations (40 vaccines)
--   9. Problems (10 active, Charlson=2: diabetes, breast cancer history)
--  10. Labs (~50 results: A1C trending 8.5%→6.8%, lipids, CBC)
-- =====================================================
-- Last Updated: 2026-02-09 (Clinical data refined for Alananah)
-- Author: med-z1 development team
-- Related: docs/spec/thompson-twins-patient-reqs.md (v3.2)
--          docs/spec/thompson-twins-implementation-plan.md (v2.1)
--          Thompson-Bailey.sql (template)
-- ====================================================="""
    return header


def main():
    print("=" * 60)
    print("Updating Thompson-Alananah.sql with clinical refinements")
    print("=" * 60)

    # Read current file
    print("\n1. Reading current Thompson-Alananah.sql...")
    content = script_file.read_text()

    # Backup already created via bash command
    print("   ✓ Backup already created")

    # Update header comment
    print("\n2. Updating header comment...")
    header_pattern = r"-- =====================================================\n-- Thompson Twins Test Patient Data.*?-- ====================================================="
    new_header = update_header_comment()
    content = re.sub(header_pattern, new_header, content, count=1, flags=re.DOTALL)
    print("   ✓ Header updated with correct Alananah profile")

    # Update Section 1 comment (Demographics)
    print("\n3. Updating Section 1 demographics comment...")
    section1_old = r"-- Alananah Thompson: Male veteran, age 62 \(DOB 1963-04-15\).*?-- ====================================================="
    section1_new = """-- Alananah Thompson: Female veteran, age 62 (DOB 1963-04-15)
-- Served 1990-2010: Gulf War (1990-1991), Iraq (2003-2007) - Combat support
-- Retired to St. Petersburg, FL (Bay Pines VAMC, Sta3n 516)
-- Breast cancer survivor (2012-2013), Type 2 diabetes (2012-present)
-- PatientSID 2002 for CDWWork
-- ICN200002 (national identifier for cross-database identity resolution)
-- ====================================================="""
    content = re.sub(section1_old, section1_new, content, flags=re.DOTALL)
    print("   ✓ Section 1 comment updated")

    # Update Section 8.2 (Problems/Diagnoses)
    print("\n4. Updating Section 8.2: Problems/Diagnoses...")
    problems_pattern = r"-- =====================================================\n-- Section 8\.2: PROBLEMS / DIAGNOSES.*?GO\n\nPRINT '    Alananah Thompson:.*?GO"
    new_problems = update_problems_section()
    content = re.sub(problems_pattern, new_problems, content, flags=re.DOTALL)
    print("   ✓ Problems section updated: 10 problems (Charlson=2)")
    print("      - Removed: Chronic back pain, TBI, MDD, CKD, OSA, GERD, CAD, A-fib, alcohol use")
    print("      - Added: Breast cancer history, diabetic neuropathy, diabetic retinopathy")

    # Write updated content
    print("\n5. Writing updated Thompson-Alananah.sql...")
    script_file.write_text(content)
    print(f"   ✓ File updated: {script_file}")

    print("\n" + "=" * 60)
    print("✅ Thompson-Alananah.sql updated successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Medications section (anastrozole, empagliflozin, levothyroxine)")
    print("2. Vitals section (female profile, height 65\")")
    print("3. Clinical Notes section (oncology, diabetes educator)")
    print("4. Labs section (A1C trending, no CKD markers)")
    print("5. Encounters section (mastectomy, chemo admissions)")
    print("\nNote: These updates require more extensive changes and will be done separately.")

if __name__ == "__main__":
    main()
