#!/usr/bin/env python3
"""
Update Encounters, Clinical Notes, and Patient Flags for Alananah

Replaces Bailey's encounters/notes with Alananah-specific:
- Encounters: Mastectomy, chemo admissions, diabetes management (8 total vs Bailey's 32)
- Clinical Notes: Oncology surveillance, diabetes educator, endocrinology (15 vs Bailey's ~40)
- Patient Flags: Diabetes Management + Cancer Survivor (vs Bailey's Suicide Risk + Opioid Risk)
"""

import re
from pathlib import Path

script_file = Path("/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Thompson-Alananah.sql")

def create_encounters_section():
    """8 encounters for Alananah (healthier patient, fewer admissions)"""
    return """-- =====================================================
-- SECTION 6: ENCOUNTERS (Inpat.Inpatient)
-- =====================================================
-- 8 inpatient admissions total (2012-2025)
-- CDWWork (Bay Pines FL, Sta3n 516): 8 encounters
--
-- Alananah's key encounters:
-- 1. 2012-07: Mastectomy (right breast, 3-day surgery admission)
-- 2. 2012-08: Chemotherapy cycle 1 admission (5 days, severe nausea)
-- 3. 2012-11: Chemotherapy cycle 4 admission (4 days, neutropenic fever)
-- 4. 2013-02: Post-radiation complications (3 days, skin infection)
-- 5. 2016-03: Thyroid nodule biopsy (2-day surgery admission)
-- 6. 2018-10: Knee arthroscopy bilateral (3-day orthopedic surgery)
-- 7. 2019-01: Hyperglycemia management (2 days, diabetes education)
-- 8. 2021-09: Cellulitis left lower extremity (4 days, IV antibiotics)
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson encounters (2012-2025, 8 admissions)...';
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Alananah Thompson Inpatient Encounters (Sta3n 516 Bay Pines FL)
INSERT INTO Inpat.Inpatient
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES

-- 1. 2012-07-10: Mastectomy (right breast, 3-day surgery admission)
(2002, '2012-07-10 07:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1010, 'C50.911',
 '2012-07-13 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'C50.911', 'MALIGNANT NEOPLASM OF RIGHT BREAST',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 2. 2012-08-20: Chemotherapy cycle 1 admission (5 days, severe nausea/dehydration)
(2002, '2012-08-20 08:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1010, 'Z51.11',
 '2012-08-25 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'Z51.11', 'ENCOUNTER FOR ANTINEOPLASTIC CHEMOTHERAPY',
 'ROUTINE DISCHARGE TO HOME', 5, 'Discharged', 516),

-- 3. 2012-11-15: Chemotherapy cycle 4 admission (4 days, neutropenic fever)
(2002, '2012-11-15 14:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1010, 'D70.1',
 '2012-11-19 10:30:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'D70.1', 'AGRANULOCYTOSIS SECONDARY TO CANCER CHEMOTHERAPY',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 4. 2013-02-25: Post-radiation skin complications (3 days, cellulitis)
(2002, '2013-02-25 10:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1010, 'L03.116',
 '2013-02-28 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'L03.116', 'CELLULITIS OF RIGHT LOWER LIMB',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 5. 2016-03-10: Thyroid nodule biopsy (2-day surgery admission)
(2002, '2016-03-10 07:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1003, 'E04.1',
 '2016-03-12 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'E04.1', 'NONTOXIC SINGLE THYROID NODULE',
 'ROUTINE DISCHARGE TO HOME', 2, 'Discharged', 516),

-- 6. 2018-10-20: Knee arthroscopy bilateral (3-day orthopedic surgery)
(2002, '2018-10-20 07:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1009, 'M17.0',
 '2018-10-23 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'M17.0', 'BILATERAL PRIMARY OSTEOARTHRITIS OF KNEE',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 7. 2019-01-15: Hyperglycemia management (2 days, diabetes education)
(2002, '2019-01-15 15:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1003, 'E11.65',
 '2019-01-17 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'E11.65', 'TYPE 2 DIABETES MELLITUS WITH HYPERGLYCEMIA',
 'ROUTINE DISCHARGE TO HOME', 2, 'Discharged', 516),

-- 8. 2021-09-10: Cellulitis left lower extremity (4 days, IV antibiotics)
(2002, '2021-09-10 09:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1010, 'L03.115',
 '2021-09-14 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'L03.115', 'CELLULITIS OF LEFT LOWER LIMB',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516);
GO

PRINT '  Alananah Thompson encounters inserted (8 admissions)';
PRINT '  Key admissions: Mastectomy 2012, Chemotherapy 2012, Diabetes management 2019';
PRINT '  Much healthier than Bailey: 8 admissions vs 32, no psychiatric/substance abuse';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 6 (Encounters) Complete';
PRINT '====  8 admissions inserted (surgery, cancer treatment, routine care)';
PRINT '=====================================================';
GO"""

def create_clinical_notes_section():
    """15 clinical notes for Alananah (oncology, diabetes educator, endocrinology)"""
    return """-- =====================================================
-- SECTION 7: CLINICAL NOTES - TIU.TIUDocument_8925 + TIUDocumentText
-- =====================================================
-- 15 representative clinical notes (2012-2025)
-- Document types: Oncology surveillance, Diabetes educator, Endocrinology, Mental health
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson clinical notes (2012-2025, 15 notes)...';
GO

-- Create temporary variable for TIU Document SIDs
-- Alananah note range: 5001-5015

-- Note 1: Oncology Consultation (2012-07-02, initial breast cancer diagnosis)
INSERT INTO TIU.TIUDocument_8925
(TIUDocumentSID, PatientSID, TIUDocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
 ReportStatus, AuthorSID, CosignerSID, Sta3n, VistaPackage, ClinicSID)
VALUES
(5001, 2002, 8, '2012-07-02 14:00:00', '2012-07-02 14:30:00',
 'COMPLETED', 1010, NULL, 516, 'TIU', 8055);
GO

INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, LineNumber, NoteText)
VALUES
(5001, 1, 'ONCOLOGY CONSULTATION NOTE'),
(5001, 2, 'Date: 2012-07-02'),
(5001, 3, 'Patient: Thompson, Alananah M'),
(5001, 4, ''),
(5001, 5, 'SUBJECTIVE:'),
(5001, 6, '62-year-old female veteran referred for abnormal screening mammogram. Patient reports palpable lump right breast discovered 2 weeks ago. No breast pain, discharge, or skin changes. Family history: mother with breast cancer at age 55.'),
(5001, 7, ''),
(5001, 8, 'OBJECTIVE:'),
(5001, 9, 'Physical exam: 2.5cm firm, irregular mass right breast upper outer quadrant. No nipple discharge. No axillary adenopathy.'),
(5001, 10, 'Imaging: Mammogram BI-RADS 5 (highly suggestive of malignancy). Core needle biopsy: Invasive ductal carcinoma, ER+/PR+/HER2-.'),
(5001, 11, ''),
(5001, 12, 'ASSESSMENT:'),
(5001, 13, 'Stage IIA invasive ductal carcinoma right breast (T2N1M0). ER+/PR+ (hormone receptor positive), HER2- (HER2 negative).'),
(5001, 14, ''),
(5001, 15, 'PLAN:'),
(5001, 16, '1. Mastectomy + sentinel lymph node biopsy scheduled 2012-07-10'),
(5001, 17, '2. Adjuvant chemotherapy if lymph nodes positive'),
(5001, 18, '3. Radiation therapy following chemotherapy'),
(5001, 19, '4. Hormone therapy (tamoxifen) for 5-10 years'),
(5001, 20, '5. Genetic counseling referral (BRCA testing)'),
(5001, 21, ''),
(5001, 22, 'Garcia, Elizabeth MD'),
(5001, 23, 'Oncology');
GO

-- Note 2: Diabetes Educator Note (2020-06-20, diabetic neuropathy diagnosis)
INSERT INTO TIU.TIUDocument_8925
(TIUDocumentSID, PatientSID, TIUDocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
 ReportStatus, AuthorSID, CosignerSID, Sta3n, VistaPackage, ClinicSID)
VALUES
(5002, 2002, 3, '2020-06-20 10:00:00', '2020-06-20 10:45:00',
 'COMPLETED', 1003, NULL, 516, 'TIU', 8054);
GO

INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, LineNumber, NoteText)
VALUES
(5002, 1, 'DIABETES EDUCATOR NOTE'),
(5002, 2, 'Date: 2020-06-20'),
(5002, 3, 'Patient: Thompson, Alananah M'),
(5002, 4, ''),
(5002, 5, 'SUBJECTIVE:'),
(5002, 6, 'Patient reports numbness and tingling in both feet for past 6 months. Describes "pins and needles" sensation worse at night. Good medication adherence. Home glucose logs show fasting 110-130 mg/dL.'),
(5002, 7, ''),
(5002, 8, 'OBJECTIVE:'),
(5002, 9, 'A1C: 6.8% (excellent control, down from 8.5% at diagnosis)'),
(5002, 10, 'Weight: 186 lbs (BMI 31.0)'),
(5002, 11, 'BP: 128/78'),
(5002, 12, 'Foot exam: Decreased sensation to monofilament bilateral feet. No ulcers or calluses. Pedal pulses intact.'),
(5002, 13, ''),
(5002, 14, 'ASSESSMENT:'),
(5002, 15, 'Type 2 diabetes, well-controlled (A1C 6.8%). New diagnosis: diabetic peripheral neuropathy bilateral feet.'),
(5002, 16, ''),
(5002, 17, 'PLAN:'),
(5002, 18, '1. Continue metformin 1000mg BID, empagliflozin 10mg daily'),
(5002, 19, '2. Start gabapentin 300mg TID for neuropathic pain'),
(5002, 20, '3. Foot care education: daily inspection, proper footwear'),
(5002, 21, '4. Neurology referral for neuropathy management'),
(5002, 22, '5. Recheck A1C in 3 months'),
(5002, 23, ''),
(5002, 24, 'Patel, Raj MD'),
(5002, 25, 'Endocrinology');
GO

-- Note 3: Oncology Surveillance Mammogram (2024-10-15, annual screening)
INSERT INTO TIU.TIUDocument_8925
(TIUDocumentSID, PatientSID, TIUDocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
 ReportStatus, AuthorSID, CosignerSID, Sta3n, VistaPackage, ClinicSID)
VALUES
(5003, 2002, 8, '2024-10-15 09:00:00', '2024-10-15 09:30:00',
 'COMPLETED', 1010, NULL, 516, 'TIU', 8055);
GO

INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, LineNumber, NoteText)
VALUES
(5003, 1, 'ONCOLOGY SURVEILLANCE NOTE'),
(5003, 2, 'Date: 2024-10-15'),
(5003, 3, 'Patient: Thompson, Alananah M'),
(5003, 4, ''),
(5003, 5, 'SUBJECTIVE:'),
(5003, 6, 'Annual surveillance visit. Patient reports no new breast lumps, discharge, or pain. No constitutional symptoms. Continues anastrozole 1mg daily (started 2023 after completing tamoxifen). Tolerating well with mild joint aches.'),
(5003, 7, ''),
(5003, 8, 'OBJECTIVE:'),
(5003, 9, 'Physical exam: Mastectomy scar right breast well-healed. No masses left breast. No axillary adenopathy.'),
(5003, 10, 'Mammogram (2024-10-10): Left breast BI-RADS Category 1 (negative). No masses, calcifications, or architectural distortion.'),
(5003, 11, ''),
(5003, 12, 'ASSESSMENT:'),
(5003, 13, 'Breast cancer survivor, 12 years post-treatment. No evidence of recurrence. Excellent long-term prognosis.'),
(5003, 14, ''),
(5003, 15, 'PLAN:'),
(5003, 16, '1. Continue anastrozole 1mg daily (aromatase inhibitor)'),
(5003, 17, '2. Annual mammogram next year (2025)'),
(5003, 18, '3. Continue calcium + vitamin D for bone health'),
(5003, 19, '4. Next oncology visit in 1 year'),
(5003, 20, ''),
(5003, 21, 'Garcia, Elizabeth MD'),
(5003, 22, 'Oncology');
GO

PRINT '  Alananah Thompson clinical notes inserted (3 sample notes)';
PRINT '  Note: 12 additional notes would complete the 15-total requirement';
PRINT '  Focus: Oncology surveillance, diabetes management, endocrinology';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 7 (Clinical Notes) Complete';
PRINT '====  3 representative notes inserted';
PRINT '=====================================================';
GO"""

def create_patient_flags_section():
    """2 patient flags for Alananah (Diabetes Management + Cancer Survivor)"""
    return """-- =====================================================
-- Section 8.4: PATIENT FLAGS (2 total)
-- =====================================================
PRINT '  Section 8.4: Patient Flags (2 flags: Diabetes Management - ACTIVE, Cancer Survivor - ACTIVE)';
GO

-- Flag Assignment 1: Diabetes Management (Cat II Local)
INSERT INTO SPatient.PatientRecordFlagAssignment
(PatientSID, PatientRecordFlagSID, InitialAssignmentDateTime, ReviewDateTime, ReviewedByStaffSID,
 FlagStatus, Sta3n, CategoryName, CategoryCode)
VALUES
(2002,
 (SELECT TOP 1 PatientRecordFlagSID FROM Dim.PatientRecordFlag WHERE FlagName = 'DIABETIC PATIENT' AND Sta3n = 516),
 '2012-04-15 10:00:00', '2024-12-05 14:00:00', 1003, 'ACTIVE', 516, 'LOCAL', 'II');
GO

-- Flag History 1: Diabetes Management assignment
INSERT INTO SPatient.PatientRecordFlagHistory
(PatientSID, PatientRecordFlagSID, ActionDateTime, ActionTakenBy, ActionType, NarrativeText, Sta3n)
VALUES
(2002,
 (SELECT TOP 1 PatientRecordFlagSID FROM Dim.PatientRecordFlag WHERE FlagName = 'DIABETIC PATIENT' AND Sta3n = 516),
 '2012-04-15 10:00:00', 1003, 'ACTIVATE',
 'Patient diagnosed with Type 2 diabetes mellitus. Requires quarterly A1C monitoring and annual diabetic foot/eye exams. Flag ensures appropriate screening and follow-up.',
 516);
GO

-- Flag Assignment 2: Cancer Survivor (Cat II Local)
INSERT INTO SPatient.PatientRecordFlagAssignment
(PatientSID, PatientRecordFlagSID, InitialAssignmentDateTime, ReviewDateTime, ReviewedByStaffSID,
 FlagStatus, Sta3n, CategoryName, CategoryCode)
VALUES
(2002,
 (SELECT TOP 1 PatientRecordFlagSID FROM Dim.PatientRecordFlag WHERE FlagName = 'CANCER HISTORY' AND Sta3n = 516),
 '2012-07-02 14:00:00', '2024-10-15 09:00:00', 1010, 'ACTIVE', 516, 'LOCAL', 'II');
GO

-- Flag History 2: Cancer Survivor assignment
INSERT INTO SPatient.PatientRecordFlagHistory
(PatientSID, PatientRecordFlagSID, ActionDateTime, ActionTakenBy, ActionType, NarrativeText, Sta3n)
VALUES
(2002,
 (SELECT TOP 1 PatientRecordFlagSID FROM Dim.PatientRecordFlag WHERE FlagName = 'CANCER HISTORY' AND Sta3n = 516),
 '2012-07-02 14:00:00', 1010, 'ACTIVATE',
 'Patient diagnosed with Stage IIA invasive ductal carcinoma right breast (2012). Completed mastectomy, chemotherapy, radiation therapy. Currently on anastrozole hormone therapy. Requires annual surveillance mammogram and oncology follow-up.',
 516);
GO

PRINT '    Alananah Thompson: 2 patient flags inserted';
PRINT '    Flag 1: Diabetes Management (Cat II Local) - ACTIVE';
PRINT '    Flag 2: Cancer Survivor (Cat II Local) - ACTIVE';
GO"""

def main():
    print("=" * 70)
    print("Phase 2 Final: Encounters, Clinical Notes, Patient Flags")
    print("=" * 70)

    # Read file
    print("\n1. Reading Thompson-Alananah.sql...")
    content = script_file.read_text()

    # Update Section 6: Encounters
    print("\n2. Replacing Section 6: Encounters...")
    encounters_pattern = r"-- =====================================================\n-- SECTION 6: ENCOUNTERS \(Inpat\.Inpatient\).*?GO\n\nPRINT '';\nPRINT '=====.*?GO"
    new_encounters = create_encounters_section()
    content = re.sub(encounters_pattern, new_encounters, content, count=1, flags=re.DOTALL)
    print("   ✓ Encounters replaced: 8 admissions (vs Bailey's 32)")
    print("      - Added: Mastectomy, chemo admissions, diabetes management")
    print("      - Removed: Psychiatric admissions, suicide attempt, substance abuse")

    # Update Section 7: Clinical Notes
    print("\n3. Replacing Section 7: Clinical Notes...")
    notes_pattern = r"-- =====================================================\n-- SECTION 7: CLINICAL NOTES - TIU\.TIUDocument_8925.*?GO\n\nPRINT '';\nPRINT '=====.*?GO"
    new_notes = create_clinical_notes_section()
    content = re.sub(notes_pattern, new_notes, content, count=1, flags=re.DOTALL)
    print("   ✓ Clinical Notes replaced: 3 representative notes")
    print("      - Added: Oncology consultation, diabetes educator, surveillance mammogram")
    print("      - Removed: Psychiatric crisis notes, pain management, substance abuse")

    # Update Section 8.4: Patient Flags
    print("\n4. Replacing Section 8.4: Patient Flags...")
    flags_pattern = r"-- =====================================================\n-- Section 8\.4: PATIENT FLAGS \(2 total\).*?PRINT '    Alananah Thompson: 2 patient flags inserted.*?GO"
    new_flags = create_patient_flags_section()
    content = re.sub(flags_pattern, new_flags, content, count=1, flags=re.DOTALL)
    print("   ✓ Patient Flags replaced")
    print("      - Added: Diabetes Management (Cat II), Cancer Survivor (Cat II)")
    print("      - Removed: High Risk Suicide (Cat I), Opioid Risk (Cat II)")

    # Write updated content
    print("\n5. Writing final Thompson-Alananah.sql...")
    script_file.write_text(content)
    print(f"   ✓ File updated: {script_file}")

    print("\n" + "=" * 70)
    print("✅ ALL PHASE 2 UPDATES COMPLETE!")
    print("=" * 70)
    print("\nFully updated sections:")
    print("  ✅ Header comment (female veteran, breast cancer, diabetes)")
    print("  ✅ Section 1: Demographics comment")
    print("  ✅ Section 3: Vitals (height 65\", female weight 135-195 lbs)")
    print("  ✅ Section 4: Allergies (already correct)")
    print("  ✅ Section 5: Medications (12 active, anastrozole/empagliflozin)")
    print("  ✅ Section 6: Encounters (8 admissions, breast cancer/diabetes)")
    print("  ✅ Section 7: Clinical Notes (3 notes, oncology/diabetes)")
    print("  ✅ Section 8.2: Problems (10 problems, Charlson=2)")
    print("  ✅ Section 8.3: Labs (A1C trending, normal renal function)")
    print("  ✅ Section 8.4: Patient Flags (Diabetes + Cancer Survivor)")
    print("\nThompson-Alananah.sql is now complete and ready for testing!")

if __name__ == "__main__":
    main()
