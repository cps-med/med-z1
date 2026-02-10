#!/usr/bin/env python3
"""
Generate corrected Thompson-Joe.sql script

This script generates a complete, syntactically correct SQL insert script for
Joe Thompson (PatientSID 2003, ICN200003) using Thompson-Bailey.sql as the
authoritative template.

Joe Thompson Profile:
- Healthy control patient (Charlson Index = 0)
- Age 55 (DOB: 1970-05-10)
- Air Force Major (O-4), Logistics Officer (1992-2012)
- Service Connection: 10% (Tinnitus only)
- Medical: Mild hypertension, mild hyperlipidemia
- Medications: 3 active (Lisinopril, Atorvastatin, Multivitamin)
- Allergies: NKDA (No Known Drug Allergies)
- No patient flags
- Stable vitals, normal labs

Usage:
    python3 scripts/generate_thompson_joe_corrected.py

Output:
    mock/sql-server/cdwwork/insert/Thompson-Joe-CORRECTED.sql
"""

from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path("/Users/chuck/swdev/med/med-z1")
BAILEY_SCRIPT = PROJECT_ROOT / "mock/sql-server/cdwwork/insert/Thompson-Bailey.sql"
OUTPUT_SCRIPT = PROJECT_ROOT / "mock/sql-server/cdwwork/insert/Thompson-Joe-CORRECTED.sql"

# Joe Thompson identifiers
JOE_PATIENT_SID = 2003
JOE_PATIENT_IEN = "PtIEN2003"
JOE_ICN = "ICN200003"
JOE_SSN = "200-00-1003"
JOE_SCR_SSN = "200-00-1003"

# Joe's unique SID ranges (following +1000 pattern from Bailey/Alananah)
JOE_VITAL_SID_START = 11001
JOE_VITAL_SID_END = 11231  # 231 vitals over 13 years (2012-2025)
JOE_ALLERGY_SID_START = None  # NKDA - no allergies
JOE_RX_SID_START = 8086
JOE_RX_SID_END = 8093  # 8 medications total (3 active, 5 historical)

# Facility info
STA3N = 516  # Bay Pines VA Medical Center

def generate_header():
    """Generate script header with Joe's profile"""
    return f"""-- =====================================================
-- Thompson Twins Test Patient Data
-- Patient: Joe Michael Thompson (Male)
-- ICN: {JOE_ICN}
-- Database: CDWWork (Bay Pines VA, 2012-2025)
-- =====================================================
--
-- Patient Profile:
-- - Name: Joe Michael Thompson
-- - Gender: Male
-- - DOB: 05/10/1970 (Age 55, younger brother of Bailey & Alananah)
-- - ICN: {JOE_ICN}
-- - PatientSID: {JOE_PATIENT_SID} (manually assigned)
-- - Sta3n: {STA3N} (Bay Pines VA Medical Center, Florida)
-- - Service Connection: 10% (Tinnitus 10%)
-- - Veterans Era: Gulf War Era (1992-2012, Air Force Major O-4)
-- - Charlson Comorbidity Index: 0 (excellent prognosis)
--
-- Clinical Summary:
-- - HEALTHY CONTROL PATIENT: Minimal chronic disease, excellent preventive care
-- - Air Force logistics officer (non-combat role), no PTSD, no substance use
-- - Well-controlled mild hypertension and hyperlipidemia (only 2 conditions)
-- - Only 3 active medications, NKDA (No Known Drug Allergies)
-- - Stable vitals (BMI 26, BP 130-138/80-85), normal labs
-- - 1 elective hospitalization (2018 hernia repair)
-- - Strong family support (married 25+ years), financially secure
-- - Relocated from Florida to Washington State (02/2025) with siblings Bailey & Alananah
--
-- Data Sections:
-- 1. Demographics (SPatient.SPatient)
-- 2. Addresses (SPatient.SPatientAddress) - 2 addresses (FL + WA)
-- 3. Phone Numbers (SPatient.SPatientPhone) - 4 numbers (2 FL + 2 WA)
-- 4. Insurance (SPatient.SPatientInsurance) - 2 policies (VA + Medicare)
-- 5. Disabilities (SPatient.SpatientDisability) - 1 disability (Tinnitus 10%)
-- 6. Vitals (Vital.VitalSign) - {JOE_VITAL_SID_END - JOE_VITAL_SID_START + 1} readings (2012-2025, stable/healthy trends)
-- 7. Patient Flags (NONE) - Healthy patient, no high-risk flags
-- 8. Allergies (NONE) - NKDA (No Known Drug Allergies)
-- 9. Medications (RxOut.RxOutpat) - RxOutpatSID {JOE_RX_SID_START}-{JOE_RX_SID_END} (8 total: 3 active, 5 historical)
-- 10. Encounters (Inpat.Inpatient) - 1 admission (2018 hernia repair - elective)
-- 11. Clinical Notes (TIU.TIUDocument_8925) - Routine wellness visits (abbreviated)
-- 12. Immunizations (Immunization.PatientImmunization) - Standard vaccines (~36 vaccines)
-- 13. Problems (Outpat.ProblemList) - 2 problems (Hypertension, Hyperlipidemia, Charlson=0)
-- 14. Laboratory Results (Chem.LabChem) - Normal values (~55 results, healthy profile)
--
-- Script Execution:
-- This script is designed to be run via sqlcmd or SQL Server Management Studio
-- after dimension tables have been populated.
-- =====================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO
"""

def generate_demographics():
    """Generate Section 1: SPatient.SPatient using Bailey's exact column structure"""
    return f"""-- =====================================================
-- Section 1: SPatient.SPatient - Core Demographics
-- =====================================================
-- Joe Thompson: Healthy 55M Air Force veteran (Major O-4)
-- Married, financially secure, excellent health, no combat exposure
-- =====================================================

PRINT 'Section 1: Inserting core demographics for Joe Thompson...';
GO

INSERT INTO SPatient.SPatient
(
    PatientSID,
    PatientIEN,
    Sta3n,
    PatientName,
    PatientLastName,
    PatientFirstName,
    PatientMiddleName,
    PatientNameSuffix,
    PatientNameComponents,
    PatientICN,
    TestPatientFlag,
    CDWPossibleTestPatientFlag,
    VeteranFlag,
    PatientType,
    PatientTypeSID,
    ScrSSN,
    PatientSSN,
    PseudoSSNReason,
    SSNVerificationStatus,
    GovernmentEmployeeFlag,
    SensitiveFlag,
    Age,
    BirthDateTime,
    BirthVistaErrorDate,
    BirthDateTimeTransformSID,
    DeceasedFlag,
    DeathDateTime,
    DeathVistaErrorDate,
    DeathDateTimeTransformSID,
    DeathEnteredByStaffSID,
    DeathNotificationSource,
    DeathDocumentationType,
    DeathModifiedDateTime,
    DeathModifiedVistaErrorDate,
    DeathModifiedDateTimeTransformSID,
    DeathLastUpdatedByStaffSID,
    Gender,
    SelfIdentifiedGender,
    Religion,
    ReligionSID,
    MaritalStatus,
    MaritalStatusSID,
    CollateralSponsorPatientSID,
    CurrentEnrollmentSID,
    MeansTestStatus,
    CurrentMeansTestStatusSID,
    PeriodOfService,
    PeriodOfServiceSID,
    OperationDesertShieldRank,
    ODSRankType,
    ODSRecalledCode,
    ODSTreatmentDateTime,
    ODSTreatmentVistaErrorDate,
    ODSTreatmentDateTimeTransformSID,
    FederalAgencySID,
    FilipinoVeteranCode,
    ServiceConnectedFlag,
    Eligibility,
    EligibilityVACode,
    EligibilitySID,
    EligibilityStatus,
    EligibilityStatusDateTime,
    EligibilityStatusVistaErrorDate,
    EligibilityStatusDateTimeTransformSID,
    EligibilityVerificationSource,
    EligibilityVerificationMethod,
    EligibilityInterimDateTime,
    EligibilityInterimVistaErrorDate,
    EligibilityInterimDateTimeTransformSID,
    EligibilityEnteredStaffSID,
    IneligibleReason,
    IneligibleVAROReason,
    IneligibleCity,
    IneligibleStateSID,
    IneligibleDateTime,
    IneligibleVistaErrorDate,
    IneligibleDateTimeTransformSID,
    IneligibleSource,
    PatientMissingSource,
    PatientMissingDateTime,
    PatientMissingVistaErrorDate,
    PatientMissingDateTimeTransformSID,
    PatientMissingCity,
    PatientMissingStateSID,
    FugitiveFelonFlag,
    FFFEnteredDateTime,
    FFFEnteredVistaErrorDate,
    FFFEnteredDateTimeTransformSID,
    FFFEnteredStaffSID,
    FFFRemovedReason,
    FFFRemovedDateTime,
    FFFRemovedVistaErrorDate,
    FFFRemovedDateTimeTransformSID,
    FFFRemovedStaffSID,
    PatientEnteredByStaffSID,
    PatientEnteredCode,
    PatientEnteredRemark,
    PatientEnteredDateTime,
    PatientEnteredVistaErrorDate,
    PatientEnteredDateTimeTransformSID,
    DuplicateRecordStatus,
    DestinationMergePatientSID,
    PreferredInstitutionSID,
    PreferredInstitutionSource,
    EmergencyResponseIndicator,
    InsuranceCoverageFlag,
    MedicaidEligibleFlag,
    MedicaidNumber,
    MedicaidInquireDateTime,
    MedicaidInquireVistaErrorDate,
    MedicaidInquireDateTimeTransformSID,
    VeteranTransportationProgramFlag
)
VALUES
(
    {JOE_PATIENT_SID},                  -- PatientSID: Unique ID for CDWWork
    '{JOE_PATIENT_IEN}',                -- PatientIEN: VistA internal entry number
    {STA3N},                            -- Sta3n: Bay Pines VA (St. Petersburg, FL)
    'THOMPSON,JOE MICHAEL',             -- PatientName: Last,First Middle format
    'Thompson',                         -- PatientLastName
    'Joe',                              -- PatientFirstName
    'Michael',                          -- PatientMiddleName
    NULL,                               -- PatientNameSuffix
    NULL,                               -- PatientNameComponents
    '{JOE_ICN}',                        -- PatientICN: National identifier
    'N',                                -- TestPatientFlag: Not a test patient (mock value)
    'N',                                -- CDWPossibleTestPatientFlag
    'Y',                                -- VeteranFlag: Yes, veteran
    'Regular',                          -- PatientType
    101,                                -- PatientTypeSID: Regular veteran
    '{JOE_SCR_SSN}',                    -- ScrSSN: Scrambled SSN (display)
    '{JOE_SSN}',                        -- PatientSSN: Mock SSN (non-real)
    'None',                             -- PseudoSSNReason
    'Verified',                         -- SSNVerificationStatus
    'N',                                -- GovernmentEmployeeFlag
    'N',                                -- SensitiveFlag
    55,                                 -- Age: As of 2026
    '1970-05-10',                       -- BirthDateTime: May 10, 1970
    NULL,                               -- BirthVistaErrorDate
    NULL,                               -- BirthDateTimeTransformSID
    'N',                                -- DeceasedFlag: Alive
    NULL,                               -- DeathDateTime
    NULL,                               -- DeathVistaErrorDate
    NULL,                               -- DeathDateTimeTransformSID
    NULL,                               -- DeathEnteredByStaffSID
    NULL,                               -- DeathNotificationSource
    NULL,                               -- DeathDocumentationType
    NULL,                               -- DeathModifiedDateTime
    NULL,                               -- DeathModifiedVistaErrorDate
    NULL,                               -- DeathModifiedDateTimeTransformSID
    NULL,                               -- DeathLastUpdatedByStaffSID
    'M',                                -- Gender: Male
    'Male',                             -- SelfIdentifiedGender
    'Catholic',                         -- Religion
    3,                                  -- ReligionSID
    'MARRIED',                          -- MaritalStatus: Married since 2000
    1,                                  -- MaritalStatusSID
    NULL,                               -- CollateralSponsorPatientSID
    {JOE_PATIENT_SID},                  -- CurrentEnrollmentSID
    'None',                             -- MeansTestStatus
    NULL,                               -- CurrentMeansTestStatusSID
    'GULF WAR',                         -- PeriodOfService: Gulf War era
    12008,                              -- PeriodOfServiceSID
    NULL,                               -- OperationDesertShieldRank
    NULL,                               -- ODSRankType
    NULL,                               -- ODSRecalledCode
    NULL,                               -- ODSTreatmentDateTime
    NULL,                               -- ODSTreatmentVistaErrorDate
    NULL,                               -- ODSTreatmentDateTimeTransformSID
    NULL,                               -- FederalAgencySID
    NULL,                               -- FilipinoVeteranCode
    'Y',                                -- ServiceConnectedFlag: Yes, 10% SC
    'VERIFIED',                         -- Eligibility
    NULL,                               -- EligibilityVACode
    1,                                  -- EligibilitySID
    'VERIFIED',                         -- EligibilityStatus
    NULL,                               -- EligibilityStatusDateTime
    NULL,                               -- EligibilityStatusVistaErrorDate
    NULL,                               -- EligibilityStatusDateTimeTransformSID
    NULL,                               -- EligibilityVerificationSource
    NULL,                               -- EligibilityVerificationMethod
    NULL,                               -- EligibilityInterimDateTime
    NULL,                               -- EligibilityInterimVistaErrorDate
    NULL,                               -- EligibilityInterimDateTimeTransformSID
    NULL,                               -- EligibilityEnteredStaffSID
    NULL,                               -- IneligibleReason
    NULL,                               -- IneligibleVAROReason
    NULL,                               -- IneligibleCity
    NULL,                               -- IneligibleStateSID
    NULL,                               -- IneligibleDateTime
    NULL,                               -- IneligibleVistaErrorDate
    NULL,                               -- IneligibleDateTimeTransformSID
    NULL,                               -- IneligibleSource
    NULL,                               -- PatientMissingSource
    NULL,                               -- PatientMissingDateTime
    NULL,                               -- PatientMissingVistaErrorDate
    NULL,                               -- PatientMissingDateTimeTransformSID
    NULL,                               -- PatientMissingCity
    NULL,                               -- PatientMissingStateSID
    'N',                                -- FugitiveFelonFlag
    NULL,                               -- FFFEnteredDateTime
    NULL,                               -- FFFEnteredVistaErrorDate
    NULL,                               -- FFFEnteredDateTimeTransformSID
    NULL,                               -- FFFEnteredStaffSID
    NULL,                               -- FFFRemovedReason
    NULL,                               -- FFFRemovedDateTime
    NULL,                               -- FFFRemovedVistaErrorDate
    NULL,                               -- FFFRemovedDateTimeTransformSID
    NULL,                               -- FFFRemovedStaffSID
    NULL,                               -- PatientEnteredByStaffSID
    NULL,                               -- PatientEnteredCode
    NULL,                               -- PatientEnteredRemark
    '2012-06-15',                       -- PatientEnteredDateTime: VA enrollment date (post-retirement)
    NULL,                               -- PatientEnteredVistaErrorDate
    NULL,                               -- PatientEnteredDateTimeTransformSID
    NULL,                               -- DuplicateRecordStatus
    NULL,                               -- DestinationMergePatientSID
    NULL,                               -- PreferredInstitutionSID
    NULL,                               -- PreferredInstitutionSource
    NULL,                               -- EmergencyResponseIndicator
    NULL,                               -- InsuranceCoverageFlag
    NULL,                               -- MedicaidEligibleFlag
    NULL,                               -- MedicaidNumber
    NULL,                               -- MedicaidInquireDateTime
    NULL,                               -- MedicaidInquireVistaErrorDate
    NULL,                               -- MedicaidInquireDateTimeTransformSID
    'Y'                                 -- VeteranTransportationProgramFlag
);
GO

PRINT '  Completed: Core demographics inserted for Joe Thompson (PatientSID {JOE_PATIENT_SID}).';
GO
"""

def generate_footer():
    """Generate script footer"""
    return f"""-- =====================================================
-- END OF JOE THOMPSON DATA INSERT SCRIPT
-- =====================================================

PRINT '========================================';
PRINT 'JOE THOMPSON DATA INSERTION COMPLETE';
PRINT '========================================';
PRINT 'Patient: Joe Michael Thompson (Male, DOB 05/10/1970, Age 55)';
PRINT 'ICN: {JOE_ICN}';
PRINT 'PatientSID: {JOE_PATIENT_SID}';
PRINT 'Service Connection: 10% (Tinnitus 10%)';
PRINT 'Charlson Comorbidity Index: 0 (excellent prognosis)';
PRINT 'Clinical Profile: Healthy Air Force veteran with minimal chronic disease';
PRINT 'Total Sections: 14 (Demographics through Laboratory Results)';
PRINT '========================================';
GO
"""

def generate_note_placeholder():
    """Generate placeholder for sections to be completed"""
    return """
-- =====================================================
-- NOTE: Additional sections to be added:
-- - Section 2: Addresses (2 addresses: FL + WA)
-- - Section 3: Phone Numbers (4 phone numbers)
-- - Section 4: Insurance (2 policies: VA + Medicare)
-- - Section 5: Disabilities (1 disability: Tinnitus 10%)
-- - Section 6: Vitals (231 readings, stable/healthy trends)
-- - Section 7: Patient Flags (NONE)
-- - Section 8: Allergies (NKDA - No Known Drug Allergies)
-- - Section 9: Medications (8 total: 3 active, 5 historical)
-- - Section 10: Encounters (1 admission: 2018 hernia repair)
-- - Section 11: Clinical Notes (routine wellness visits)
-- - Section 12: Immunizations (~36 vaccines)
-- - Section 13: Problems (2 problems: Hypertension, Hyperlipidemia)
-- - Section 14: Laboratory Results (~55 results, all normal)
--
-- This initial version provides the core demographics section.
-- Remaining sections will be added systematically using Bailey's
-- proven template patterns.
-- =====================================================
"""

def main():
    """Generate corrected Thompson-Joe.sql script"""
    print("=" * 70)
    print("Generating Corrected Thompson-Joe.sql Script")
    print("=" * 70)
    print()
    print("Patient: Joe Michael Thompson")
    print(f"PatientSID: {JOE_PATIENT_SID}")
    print(f"ICN: {JOE_ICN}")
    print(f"Profile: Healthy control patient (Charlson Index = 0)")
    print()

    # Generate script content
    print("Generating script sections...")
    script_content = []

    # Add header
    script_content.append(generate_header())
    print("  ✓ Header generated")

    # Add Section 1: Demographics
    script_content.append(generate_demographics())
    print("  ✓ Section 1: Demographics generated")

    # Add placeholder note
    script_content.append(generate_note_placeholder())
    print("  ✓ Placeholder note added")

    # Add footer
    script_content.append(generate_footer())
    print("  ✓ Footer generated")

    # Write output file
    print()
    print(f"Writing output file: {OUTPUT_SCRIPT}")
    OUTPUT_SCRIPT.write_text("".join(script_content))
    print(f"  ✓ File written: {OUTPUT_SCRIPT}")
    print()

    # Summary
    print("=" * 70)
    print("✅ INITIAL VERSION COMPLETE")
    print("=" * 70)
    print()
    print("Generated file:")
    print(f"  {OUTPUT_SCRIPT}")
    print()
    print("Status:")
    print("  ✅ Section 1: Demographics (complete with 100+ columns)")
    print("  ⏳ Sections 2-14: Placeholders (to be completed)")
    print()
    print("Next steps:")
    print("  1. Review generated demographics section")
    print("  2. Decide on approach for remaining sections:")
    print("     a) Generate all sections now (full script)")
    print("     b) Generate incrementally (section by section)")
    print("  3. Test demographics section first before proceeding")
    print()

if __name__ == "__main__":
    main()
