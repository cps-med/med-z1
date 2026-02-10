#!/usr/bin/env python3
"""
Update Thompson-Alananah.sql Medications section

Alananah's current medications (12 active):
1. Metformin 1000mg BID (diabetes)
2. Empagliflozin 10mg daily (diabetes, SGLT2 inhibitor) - **KEY DIFFERENCE**
3. Lisinopril 10mg daily (hypertension, renal protection)
4. Atorvastatin 20mg nightly (hyperlipidemia)
5. Aspirin 81mg daily (cardiovascular protection)
6. Anastrozole 1mg daily (aromatase inhibitor, breast cancer prevention) - **KEY DIFFERENCE**
7. Levothyroxine 75mcg daily (hypothyroidism) - **KEY DIFFERENCE**
8. Gabapentin 300mg TID (neuropathic pain)
9. Sertraline 100mg daily (PTSD/anxiety)
10. Calcium + Vitamin D (bone health)
11. Celecoxib 200mg BID PRN (knee pain)
12. Multivitamin daily

Key medications NOT in Bailey's regimen:
- Anastrozole (breast cancer survivorship)
- Empagliflozin (SGLT2 inhibitor for diabetes)
- Levothyroxine (hypothyroidism)
- Lower dose gabapentin (300mg vs 1200mg)
- Lower dose sertraline (100mg vs 200mg)

Medications Bailey has but Alananah DOES NOT:
- Prazosin (PTSD nightmares)
- Duloxetine (pain/depression)
- Trazodone (insomnia)
- Pantoprazole/Omeprazole (GERD)
- Opioids (no chronic pain management history)
"""

from pathlib import Path
import re

script_file = Path("/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Thompson-Alananah.sql")

def create_medications_section():
    """
    Generate Alananah's medication section with 12 active medications
    RxOutpatSID range: 8046-8085 (40 total slots allocated)
    """

    medications = """-- =====================================================
-- SECTION 5: MEDICATIONS (RxOut.RxOutpat)
-- =====================================================
-- 12 active medications (2025-2026)
-- RxOutpatSID range: 8046-8085 (allocated for Alananah)
-- Timeline: 2012-2025 (13 years of medication history)
-- Clinical themes:
--   - 2012+: Diabetes management (metformin → metformin + SGLT2i)
--   - 2013+: Breast cancer hormone therapy (tamoxifen 2013-2023, anastrozole 2023+)
--   - 2013+: HTN management (lisinopril)
--   - 2014+: Lipid management (atorvastatin)
--   - 2016+: Hypothyroidism (levothyroxine)
--   - 2020+: Diabetic neuropathy (gabapentin)
--   - 2011+: PTSD (sertraline, stable dose)
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson medications (2012-2025, 12 active)...';
GO

-- NOTE: Some medications may need to be added to Dim.LocalDrug:
-- - Empagliflozin 10mg (SGLT2 inhibitor) - using closest available or placeholder
-- - Anastrozole 1mg (aromatase inhibitor)
-- - Levothyroxine 75mcg
-- - Celecoxib 200mg PRN
-- If not available, use substitutes with comments

-- Alananah Thompson medications (Sta3n 516 Bay Pines FL, 2012-2024)
INSERT INTO RxOut.RxOutpat
(
  RxOutpatSID, RxOutpatIEN, Sta3n, PatientSID, PatientIEN, LocalDrugSID, LocalDrugIEN, NationalDrugSID,
  DrugNameWithoutDose, DrugNameWithDose, PrescriptionNumber, IssueDateTime, IssueVistaErrorDate, IssueDateTimeTransformSID,
  ProviderSID, ProviderIEN, OrderingProviderSID, OrderingProviderIEN, EnteredByStaffSID, EnteredByStaffIEN,
  PharmacySID, PharmacyIEN, PharmacyName, RxStatus, RxType, Quantity, DaysSupply, RefillsAllowed, RefillsRemaining, MaxRefills,
  UnitDose, ExpirationDateTime, ExpirationVistaErrorDate, ExpirationDateTimeTransformSID,
  DiscontinuedDateTime, DiscontinuedVistaErrorDate, DiscontinuedDateTimeTransformSID, DiscontinueReason, DiscontinuedByStaffSID,
  LoginDateTime, LoginVistaErrorDate, LoginDateTimeTransformSID, ClinicSID, ClinicIEN, ClinicName, DEASchedule, ControlledSubstanceFlag, CMOPIndicator, MailIndicator
)
VALUES

-- =====================================================
-- CURRENT ACTIVE MEDICATIONS (2025-2026, 12 total)
-- =====================================================

-- 1. Metformin 1000mg BID (diabetes - first-line therapy since 2012)
(8046, 'RxIEN9046', 516, 2002, 'PtIEN2002', 10027, 'DrugIEN10027', 20001,
 'METFORMIN HCL', 'METFORMIN HCL 1000MG TAB', '2025-001-8046',
 '2025-01-15 10:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 180, 90, 5, 5, 5, '1 TAB BID', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 2. Empagliflozin 10mg daily (SGLT2 inhibitor, added 2020 for cardio protection)
-- NOTE: Using Glipizide as placeholder if Empagliflozin not in Dim.LocalDrug
(8047, 'RxIEN9047', 516, 2002, 'PtIEN2002', 10046, 'DrugIEN10046', 20040,
 'GLIPIZIDE', 'GLIPIZIDE 10MG TAB (PLACEHOLDER FOR EMPAGLIFLOZIN)', '2025-001-8047',
 '2025-01-15 10:05:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB QD', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:05:00', NULL, NULL, 8054, 'ClinicIEN8054', 'ENDOCRINOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),

-- 3. Lisinopril 10mg daily (hypertension, renal protection - lower dose than Bailey)
(8048, 'RxIEN9048', 516, 2002, 'PtIEN2002', 10028, 'DrugIEN10028', 20003,
 'LISINOPRIL', 'LISINOPRIL 10MG TAB', '2025-001-8048',
 '2025-01-15 10:10:00', NULL, NULL, 1010, 'StaffIEN1010', 1010, 'StaffIEN1010', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:10:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 4. Atorvastatin 20mg nightly (hyperlipidemia - lower dose than Bailey)
(8049, 'RxIEN9049', 516, 2002, 'PtIEN2002', 10010, 'DrugIEN10010', 20023,
 'ATORVASTATIN CALCIUM', 'ATORVASTATIN CALCIUM 20MG TAB', '2025-001-8049',
 '2025-01-15 10:15:00', NULL, NULL, 1010, 'StaffIEN1010', 1010, 'StaffIEN1010', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB QHS', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:15:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 5. Aspirin 81mg daily (cardiovascular protection)
(8050, 'RxIEN9050', 516, 2002, 'PtIEN2002', 10033, 'DrugIEN10033', 20027,
 'ASPIRIN', 'ASPIRIN 81MG TAB EC', '2025-001-8050',
 '2025-01-15 10:20:00', NULL, NULL, 1010, 'StaffIEN1010', 1010, 'StaffIEN1010', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:20:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 6. Anastrozole 1mg daily (aromatase inhibitor, breast cancer prevention - KEY MEDICATION)
-- NOTE: Using Tamoxifen as placeholder if Anastrozole not in Dim.LocalDrug
(8051, 'RxIEN9051', 516, 2002, 'PtIEN2002', 10053, 'DrugIEN10053', 20048,
 'TAMOXIFEN CITRATE', 'TAMOXIFEN CITRATE 20MG TAB (PLACEHOLDER FOR ANASTROZOLE 1MG)', '2025-001-8051',
 '2025-01-15 10:25:00', NULL, NULL, 1010, 'StaffIEN1010', 1010, 'StaffIEN1010', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '0.05 TAB QD (simulating 1mg dose)', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:25:00', NULL, NULL, 8055, 'ClinicIEN8055', 'ONCOLOGY CLINIC', NULL, 'N', 'N', 'Y', 'Y'),

-- 7. Levothyroxine 75mcg daily (hypothyroidism - KEY MEDICATION)
-- NOTE: Using Levothyroxine 50mcg as placeholder if 75mcg not available
(8052, 'RxIEN9052', 516, 2002, 'PtIEN2002', 10056, 'DrugIEN10056', 20051,
 'LEVOTHYROXINE SODIUM', 'LEVOTHYROXINE SODIUM 50MCG TAB (PLACEHOLDER FOR 75MCG)', '2025-001-8052',
 '2025-01-15 10:30:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1.5 TAB QAM (simulating 75mcg)', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:30:00', NULL, NULL, 8054, 'ClinicIEN8054', 'ENDOCRINOLOGY CLINIC', NULL, 'N', 'N', 'Y', 'Y'),

-- 8. Gabapentin 300mg TID (neuropathic pain - diabetic neuropathy, lower dose than Bailey)
(8053, 'RxIEN9053', 516, 2002, 'PtIEN2002', 10075, 'DrugIEN10075', 20066,
 'GABAPENTIN', 'GABAPENTIN 300MG CAP', '2025-001-8053',
 '2025-01-15 10:35:00', NULL, NULL, 1014, 'StaffIEN1014', 1014, 'StaffIEN1014', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 270, 90, 5, 5, 5, '1 CAP TID', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:35:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 9. Sertraline 100mg daily (PTSD/anxiety - lower dose than Bailey)
(8054, 'RxIEN9054', 516, 2002, 'PtIEN2002', 10036, 'DrugIEN10036', 20024,
 'SERTRALINE HCL', 'SERTRALINE HCL 100MG TAB', '2025-001-8054',
 '2025-01-15 10:40:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:40:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- 10. Calcium + Vitamin D (bone health, aromatase inhibitor side effect mitigation)
(8055, 'RxIEN9055', 516, 2002, 'PtIEN2002', 10092, 'DrugIEN10092', 20083,
 'CALCIUM CARBONATE WITH VITAMIN D', 'CALCIUM CARBONATE 500MG WITH VITAMIN D 200 UNITS', '2025-001-8055',
 '2025-01-15 10:45:00', NULL, NULL, 1010, 'StaffIEN1010', 1010, 'StaffIEN1010', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'OTC',
 180, 90, 5, 5, 5, '2 TAB QD', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:45:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N'),

-- 11. Celecoxib 200mg BID PRN (osteoarthritis knee pain)
-- NOTE: Using Ibuprofen as placeholder if Celecoxib not in Dim.LocalDrug
(8056, 'RxIEN9056', 516, 2002, 'PtIEN2002', 10069, 'DrugIEN10069', 20060,
 'IBUPROFEN', 'IBUPROFEN 800MG TAB (PLACEHOLDER FOR CELECOXIB 200MG)', '2025-001-8056',
 '2025-01-15 10:50:00', NULL, NULL, 1009, 'StaffIEN1009', 1009, 'StaffIEN1009', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 60, 30, 5, 5, 5, '0.25 TAB BID PRN (simulating 200mg dose)', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:50:00', NULL, NULL, 8056, 'ClinicIEN8056', 'RHEUMATOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),

-- 12. Multivitamin daily (general health)
(8057, 'RxIEN9057', 516, 2002, 'PtIEN2002', 10093, 'DrugIEN10093', 20084,
 'MULTIVITAMIN', 'MULTIVITAMIN TAB', '2025-001-8057',
 '2025-01-15 10:55:00', NULL, NULL, 1010, 'StaffIEN1010', 1010, 'StaffIEN1010', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'OTC',
 90, 90, 5, 5, 5, '1 TAB QD', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:55:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N');
GO

PRINT '    Alananah Thompson: 12 active medications inserted';
PRINT '    Key medications: Anastrozole (breast cancer), Empagliflozin (diabetes), Levothyroxine (hypothyroid)';
PRINT '    Note: Some medications use placeholders - update Dim.LocalDrug for full accuracy';
GO"""

    return medications


def main():
    print("=" * 60)
    print("Updating Thompson-Alananah.sql Medications Section")
    print("=" * 60)

    # Read current file
    print("\n1. Reading Thompson-Alananah.sql...")
    content = script_file.read_text()

    # Find and replace medications section
    print("\n2. Replacing Medications section (SECTION 5)...")
    # Pattern to match from "-- SECTION 5: MEDICATIONS" to the end of the GO statement after the medications
    medications_pattern = r"-- =====================================================\n-- SECTION 5: MEDICATIONS \(RxOut\.RxOutpat\).*?GO\n\nPRINT '    Alananah Thompson: \d+ (?:active )?medications inserted.*?(?:GO|$)"

    new_medications = create_medications_section()
    content = re.sub(medications_pattern, new_medications + "\n", content, count=1, flags=re.DOTALL)
    print("   ✓ Medications section replaced")
    print("      - Bailey's 15+ medications → Alananah's 12 medications")
    print("      - Removed: Opioids, prazosin, duloxetine, trazodone, omeprazole")
    print("      - Added: Anastrozole, empagliflozin, levothyroxine")
    print("      - Adjusted: Lower sertraline (100mg vs 200mg), lower gabapentin (300mg vs 1200mg)")

    # Write updated content
    print("\n3. Writing updated Thompson-Alananah.sql...")
    script_file.write_text(content)
    print(f"   ✓ File updated: {script_file}")

    print("\n" + "=" * 60)
    print("✅ Medications section updated successfully!")
    print("=" * 60)
    print("\nCompleted sections:")
    print("  ✅ Header comment")
    print("  ✅ Section 1 demographics comment")
    print("  ✅ Section 8.2 Problems/Diagnoses (10 problems, Charlson=2)")
    print("  ✅ Section 5 Medications (12 active medications)")
    print("\nRemaining sections:")
    print("  ⏳ Section 3 Vitals (female profile, height 65\")")
    print("  ⏳ Section 7 Clinical Notes (oncology, diabetes educator)")
    print("  ⏳ Section 8.3 Labs (A1C trending, no CKD markers)")
    print("  ⏳ Section 6 Encounters (mastectomy, chemo admissions)")
    print("  ⏳ Section 4 Allergies (already correct)")
    print("  ⏳ Section 8.4 Patient Flags (already correct)")

if __name__ == "__main__":
    main()
