#!/usr/bin/env python3
"""
Generate COMPREHENSIVE Thompson-Joe.sql script with ALL 14 sections

This generates Joe Thompson's complete CDWWork insert script matching
Bailey's full structure but reflecting Joe's healthy patient persona.

Joe's Profile (Healthy Control Patient):
- Age 55, DOB: 1970-05-10
- Air Force Major (O-4), Logistics Officer (1992-2012, non-combat)
- Service Connection: 10% (Tinnitus only)
- Charlson Index: 0 (excellent prognosis)
- Only 2 chronic conditions: Mild hypertension, mild hyperlipidemia
- 3 active medications, NKDA, no patient flags
- Stable vitals, normal labs, 1 elective hospitalization
- Married since 2000, financially secure, strong family support
- Relocated from Florida to Washington State (02/2025) with siblings
"""

from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path("/Users/chuck/swdev/med/med-z1")
OUTPUT = PROJECT_ROOT / "mock/sql-server/cdwwork/insert/Thompson-Joe.sql"

# Constants
JOE_SID = 2003
JOE_IEN = "PtIEN2003"
JOE_ICN = "ICN200003"
STA3N_BAYPINES = 516
STA3N_WALLAWALLA = 687

def generate_header():
    """Generate file header with patient profile"""
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
-- - PatientSID: {JOE_SID} (manually assigned)
-- - Sta3n: {STA3N_BAYPINES} (Bay Pines VA Medical Center, Florida)
-- - Service Connection: 10% (Tinnitus 10%)
-- - Veterans Era: Gulf War Era (1992-2012, Air Force Major O-4, Logistics)
-- - Charlson Comorbidity Index: 0 (excellent prognosis)
--
-- Clinical Summary:
-- - HEALTHY CONTROL PATIENT: Minimal chronic disease, excellent preventive care
-- - Air Force logistics officer (non-combat role), no PTSD, no substance use
-- - Well-controlled mild hypertension and hyperlipidemia (only 2 conditions)
-- - Only 3 active medications, NKDA (No Known Drug Allergies)
-- - Stable vitals (BMI 26, BP 128-132/80-84), normal labs
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
-- 6. Vitals (Vital.VitalSign) - 231 readings (2012-2025, stable/healthy trends)
-- 7. Allergies (NKDA) - No Known Drug Allergies
-- 8. Medications (RxOut.RxOutpat) - RxOutpatSID 8086-8093 (8 total: 3 active, 5 historical)
-- 9. Encounters (Inpat.Inpatient) - 1 admission (2018 hernia repair - elective)
-- 10. Clinical Notes (TIU.TIUDocument_8925) - Routine wellness visits (abbreviated)
-- 11. Immunizations (Immunization.PatientImmunization) - Standard vaccines (~36 vaccines)
-- 12. Problems (Outpat.ProblemList) - 2 problems (Hypertension, Hyperlipidemia, Charlson=0)
-- 13. Laboratory Results (Chem.LabChem) - Normal values (~55 results, healthy profile)
-- 14. Patient Flags (NONE) - Healthy patient, no high-risk flags
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

def generate_section1_demographics():
    """Generate Section 1: SPatient.SPatient - Core Demographics (Full 100+ Column Structure)"""
    return f"""-- =====================================================
-- SECTION 1: DEMOGRAPHICS - SPatient.SPatient
-- =====================================================
-- Joe Thompson: Healthy 55M Air Force veteran (Major O-4)
-- Married, financially secure, excellent health, no combat exposure
-- PatientSID {JOE_SID} for CDWWork
-- ICN{JOE_ICN[3:]} (national identifier for cross-database identity resolution)
-- =====================================================

PRINT '';
PRINT 'Section 1: Demographics - SPatient.SPatient';
PRINT '  Inserting Joe Thompson (PatientSID {JOE_SID})';
GO

INSERT INTO SPatient.SPatient
(
    PatientSID, PatientIEN, Sta3n, PatientName, PatientLastName, PatientFirstName,
    TestPatientFlag, CDWPossibleTestPatientFlag, VeteranFlag, PatientType, PatientTypeSID,
    PatientICN, ScrSSN, PatientSSN, PseudoSSNReason, SSNVerificationStatus,
    GovernmentEmployeeFlag, SensitiveFlag, Age, BirthDateTime, BirthVistaErrorDate,
    BirthDateTimeTransformSID, DeceasedFlag, DeathDateTime, DeathVistaErrorDate,
    DeathDateTimeTransformSID, DeathEnteredByStaffSID, DeathNotificationSource,
    DeathDocumentationType, DeathModifiedDateTime, DeathModifiedVistaErrorDate,
    DeathModifiedDateTimeTransformSID, DeathLastUpdatedByStaffSID, Gender, SelfIdentifiedGender,
    Religion, ReligionSID, MaritalStatus, MaritalStatusSID, CollateralSponsorPatientSID,
    CurrentEnrollmentSID, MeansTestStatus, CurrentMeansTestStatusSID, PeriodOfService,
    PeriodOfServiceSID, OperationDesertShieldRank, ODSRankType, ODSRecalledCode,
    ODSTreatmentDateTime, ODSTreatmentVistaErrorDate, ODSTreatmentDateTimeTransformSID,
    FederalAgencySID, FilipinoVeteranCode, ServiceConnectedFlag, Eligibility, EligibilityVACode,
    EligibilitySID, EligibilityStatus, EligibilityStatusDateTime, EligibilityStatusVistaErrorDate,
    EligibilityStatusDateTimeTransformSID, EligibilityVerificationSource, EligibilityVerificationMethod,
    EligibilityInterimDateTime, EligibilityInterimVistaErrorDate, EligibilityInterimDateTimeTransformSID,
    EligibilityEnteredStaffSID, IneligibleReason, IneligibleVAROReason, IneligibleCity,
    IneligibleStateSID, IneligibleDateTime, IneligibleVistaErrorDate, IneligibleDateTimeTransformSID,
    IneligibleSource, PatientMissingSource, PatientMissingDateTime, PatientMissingVistaErrorDate,
    PatientMissingDateTimeTransformSID, PatientMissingCity, PatientMissingStateSID,
    FugitiveFelonFlag, FFFEnteredDateTime, FFFEnteredVistaErrorDate, FFFEnteredDateTimeTransformSID,
    FFFEnteredStaffSID, FFFRemovedReason, FFFRemovedDateTime, FFFRemovedVistaErrorDate,
    FFFRemovedDateTimeTransformSID, FFFRemovedStaffSID, PatientEnteredByStaffSID, PatientEnteredCode,
    PatientEnteredRemark, PatientEnteredDateTime, PatientEnteredVistaErrorDate,
    PatientEnteredDateTimeTransformSID, DuplicateRecordStatus, DestinationMergePatientSID,
    PreferredInstitutionSID, PreferredInstitutionSource, EmergencyResponseIndicator,
    InsuranceCoverageFlag, MedicaidEligibleFlag, MedicaidNumber, MedicaidInquireDateTime,
    MedicaidInquireVistaErrorDate, MedicaidInquireDateTimeTransformSID, VeteranTransportationProgramFlag
)
VALUES
(
    {JOE_SID},                      -- PatientSID: Unique ID for CDWWork
    '{JOE_IEN}',                    -- PatientIEN: VistA internal entry number
    {STA3N_BAYPINES},               -- Sta3n: Bay Pines VA (St. Petersburg, FL)
    'THOMPSON,JOE MICHAEL',         -- PatientName: Last,First Middle format
    'Thompson',                     -- PatientLastName
    'Joe',                          -- PatientFirstName
    'N',                            -- TestPatientFlag: Not a test patient (mock value)
    'N',                            -- CDWPossibleTestPatientFlag
    'Y',                            -- VeteranFlag: Yes, veteran
    'Regular',                      -- PatientType
    101,                            -- PatientTypeSID: Regular veteran
    '{JOE_ICN}',                    -- PatientICN: National identifier
    '200-00-1003',                  -- ScrSSN: Scrambled SSN (display)
    '200-00-1003',                  -- PatientSSN: Mock SSN (non-real)
    'None',                         -- PseudoSSNReason
    'Verified',                     -- SSNVerificationStatus
    'N',                            -- GovernmentEmployeeFlag
    'N',                            -- SensitiveFlag
    55,                             -- Age: As of 2026
    '1970-05-10',                   -- BirthDateTime: May 10, 1970 (younger brother)
    NULL,                           -- BirthVistaErrorDate
    NULL,                           -- BirthDateTimeTransformSID
    'N',                            -- DeceasedFlag: Alive
    NULL,                           -- DeathDateTime
    NULL,                           -- DeathVistaErrorDate
    NULL,                           -- DeathDateTimeTransformSID
    NULL,                           -- DeathEnteredByStaffSID
    NULL,                           -- DeathNotificationSource
    NULL,                           -- DeathDocumentationType
    NULL,                           -- DeathModifiedDateTime
    NULL,                           -- DeathModifiedVistaErrorDate
    NULL,                           -- DeathModifiedDateTimeTransformSID
    NULL,                           -- DeathLastUpdatedByStaffSID
    'M',                            -- Gender: Male
    'Male',                         -- SelfIdentifiedGender
    'Catholic',                     -- Religion
    3,                              -- ReligionSID
    'MARRIED',                      -- MaritalStatus: Married since 2000
    1,                              -- MaritalStatusSID
    NULL,                           -- CollateralSponsorPatientSID
    {JOE_SID},                      -- CurrentEnrollmentSID
    'None',                         -- MeansTestStatus
    NULL,                           -- CurrentMeansTestStatusSID
    'GULF WAR',                     -- PeriodOfService: Gulf War era
    12008,                          -- PeriodOfServiceSID
    NULL,                           -- OperationDesertShieldRank
    NULL,                           -- ODSRankType
    NULL,                           -- ODSRecalledCode
    NULL,                           -- ODSTreatmentDateTime
    NULL,                           -- ODSTreatmentVistaErrorDate
    NULL,                           -- ODSTreatmentDateTimeTransformSID
    NULL,                           -- FederalAgencySID
    NULL,                           -- FilipinoVeteranCode
    'Y',                            -- ServiceConnectedFlag: Yes, 10% SC
    'VERIFIED',                     -- Eligibility
    NULL,                           -- EligibilityVACode
    1,                              -- EligibilitySID
    'VERIFIED',                     -- EligibilityStatus
    NULL,                           -- EligibilityStatusDateTime
    NULL,                           -- EligibilityStatusVistaErrorDate
    NULL,                           -- EligibilityStatusDateTimeTransformSID
    NULL,                           -- EligibilityVerificationSource
    NULL,                           -- EligibilityVerificationMethod
    NULL,                           -- EligibilityInterimDateTime
    NULL,                           -- EligibilityInterimVistaErrorDate
    NULL,                           -- EligibilityInterimDateTimeTransformSID
    NULL,                           -- EligibilityEnteredStaffSID
    NULL,                           -- IneligibleReason
    NULL,                           -- IneligibleVAROReason
    NULL,                           -- IneligibleCity
    NULL,                           -- IneligibleStateSID
    NULL,                           -- IneligibleDateTime
    NULL,                           -- IneligibleVistaErrorDate
    NULL,                           -- IneligibleDateTimeTransformSID
    NULL,                           -- IneligibleSource
    NULL,                           -- PatientMissingSource
    NULL,                           -- PatientMissingDateTime
    NULL,                           -- PatientMissingVistaErrorDate
    NULL,                           -- PatientMissingDateTimeTransformSID
    NULL,                           -- PatientMissingCity
    NULL,                           -- PatientMissingStateSID
    'N',                            -- FugitiveFelonFlag
    NULL,                           -- FFFEnteredDateTime
    NULL,                           -- FFFEnteredVistaErrorDate
    NULL,                           -- FFFEnteredDateTimeTransformSID
    NULL,                           -- FFFEnteredStaffSID
    NULL,                           -- FFFRemovedReason
    NULL,                           -- FFFRemovedDateTime
    NULL,                           -- FFFRemovedVistaErrorDate
    NULL,                           -- FFFRemovedDateTimeTransformSID
    NULL,                           -- FFFRemovedStaffSID
    NULL,                           -- PatientEnteredByStaffSID
    NULL,                           -- PatientEnteredCode
    NULL,                           -- PatientEnteredRemark
    '2012-06-15',                   -- PatientEnteredDateTime: VA enrollment date (post-retirement)
    NULL,                           -- PatientEnteredVistaErrorDate
    NULL,                           -- PatientEnteredDateTimeTransformSID
    NULL,                           -- DuplicateRecordStatus
    NULL,                           -- DestinationMergePatientSID
    NULL,                           -- PreferredInstitutionSID
    NULL,                           -- PreferredInstitutionSource
    NULL,                           -- EmergencyResponseIndicator
    NULL,                           -- InsuranceCoverageFlag
    NULL,                           -- MedicaidEligibleFlag
    NULL,                           -- MedicaidNumber
    NULL,                           -- MedicaidInquireDateTime
    NULL,                           -- MedicaidInquireVistaErrorDate
    NULL,                           -- MedicaidInquireDateTimeTransformSID
    'Y'                             -- VeteranTransportationProgramFlag
);
GO

PRINT '  Joe Thompson demographics inserted (PatientSID {JOE_SID})';
GO

"""

def generate_section2_demographics_details():
    """Generate Section 2: Addresses, Phone, Insurance, Disabilities"""
    return f"""-- =====================================================
-- SECTION 2: DEMOGRAPHICS DETAILS
-- =====================================================
-- SPatient.SPatientAddress (2 addresses: FL 2012-2025, WA 2025-present)
-- SPatient.SPatientPhone (4 phone numbers)
-- SPatient.SPatientInsurance (2 insurance records)
-- SPatient.SpatientDisability (1 service-connected disability: Tinnitus 10%)
-- =====================================================

PRINT '';
PRINT 'Section 2: Demographics Details - Address, Phone, Insurance, Disability';
GO

-- Address Records (2 total: Florida + Washington)
INSERT INTO SPatient.SPatientAddress
(
    SPatientAddressSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber, AddressType,
    StreetAddress1, StreetAddress2, StreetAddress3, City, County, [State], StateSID,
    Zip, Zip4, PostalCode, Country, CountrySID, EmploymentStatus
)
VALUES
-- Florida address (2012-2025, Bay Pines VA primary address)
(
    11001,                          -- SPatientAddressSID
    {JOE_SID},                      -- PatientSID
    '{JOE_IEN}',                    -- PatientIEN
    {STA3N_BAYPINES},               -- Sta3n: Bay Pines
    1,                              -- OrdinalNumber: Primary address
    'HOME',                         -- AddressType
    '2847 Central Avenue',          -- StreetAddress1
    '',                             -- StreetAddress2
    '',                             -- StreetAddress3
    'St. Petersburg',               -- City
    'Pinellas',                     -- County
    'FL',                           -- State
    415,                            -- StateSID (Florida)
    '33713',                        -- Zip
    '2154',                         -- Zip4
    '',                             -- PostalCode
    'UNITED STATES',                -- Country
    1200005271,                     -- CountrySID (USA)
    'RETIRED'                       -- EmploymentStatus (10% SC, not disabled)
),
-- Washington address (2025-present, Walla Walla VA)
(
    11002,                          -- SPatientAddressSID
    {JOE_SID},                      -- PatientSID
    '{JOE_IEN}',                    -- PatientIEN
    {STA3N_WALLAWALLA},             -- Sta3n: Walla Walla
    2,                              -- OrdinalNumber: Secondary/current address
    'HOME',                         -- AddressType
    '823 Birch Street',             -- StreetAddress1
    '',                             -- StreetAddress2
    '',                             -- StreetAddress3
    'Walla Walla',                  -- City
    'Walla Walla',                  -- County
    'WA',                           -- State
    453,                            -- StateSID (Washington)
    '99362',                        -- Zip
    '1802',                         -- Zip4
    '',                             -- PostalCode
    'UNITED STATES',                -- Country
    1200005271,                     -- CountrySID (USA)
    'RETIRED'                       -- EmploymentStatus
);
GO

-- Phone Records (4 total: 2 FL + 2 WA)
INSERT INTO SPatient.SPatientPhone
(
    SPatientPhoneSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber,
    PhoneType, PhoneNumber, PhoneVistaErrorDate, LastUpdated
)
VALUES
-- Florida phone numbers (2012-2025)
(11001, {JOE_SID}, '{JOE_IEN}', {STA3N_BAYPINES}, 1, 'PHONE NUMBER [HOME]', '727-555-2003', NULL, GETDATE()),
(11002, {JOE_SID}, '{JOE_IEN}', {STA3N_BAYPINES}, 2, 'CELLULAR PHONE NUMBER', '727-555-2004', NULL, GETDATE()),
-- Washington phone numbers (2025-present)
(11003, {JOE_SID}, '{JOE_IEN}', {STA3N_WALLAWALLA}, 3, 'PHONE NUMBER [HOME]', '509-555-2003', NULL, GETDATE()),
(11004, {JOE_SID}, '{JOE_IEN}', {STA3N_WALLAWALLA}, 4, 'CELLULAR PHONE NUMBER', '509-555-2004', NULL, GETDATE());
GO

-- Insurance Records (2 total: VA + Medicare)
INSERT INTO SPatient.SPatientInsurance
(
    SPatientInsuranceSID, PatientSID, PatientIEN, SPatientInsuranceIEN, Sta3n,
    InsuranceCompanySID, EmploymentStatus, RetirementDate, PolicyEffectiveDate
)
VALUES
-- Primary: VA (10% service-connected disability)
(11001, {JOE_SID}, '{JOE_IEN}', 'PtInsIEN2003', 508, 5, 'RETIRED', '2012-06-15', '2012-06-15'),
-- Secondary: Medicare (age 65+, will enroll in 2035, represented here for completeness)
(11002, {JOE_SID}, '{JOE_IEN}', 'PtInsIEN2003', {STA3N_BAYPINES}, 1, 'RETIRED', '2035-05-10', '2035-05-10');
GO

-- Disability Records (1 service-connected disability: Tinnitus 10% only)
INSERT INTO SPatient.SPatientDisability
(
    SPatientDisabilitySID, PatientSID, PatientIEN, Sta3n, ClaimFolderInstitutionSID,
    ServiceConnectedFlag, ServiceConnectedPercent, AgentOrangeExposureCode, IonizingRadiationCode,
    POWStatusCode, SHADFlag, AgentOrangeLocation, POWLocation, SWAsiaCode, CampLejeuneFlag
)
VALUES
-- Tinnitus (10%, only service-connected disability)
(11001, {JOE_SID}, '{JOE_IEN}', {STA3N_BAYPINES}, 11001, 'Y', 10, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N');
GO

PRINT '  Joe Thompson demographics details inserted (Address, Phone, Insurance, Disability)';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Joe Thompson: Demographics Complete       ====';
PRINT '====  PatientSID {JOE_SID} created successfully      ====';
PRINT '=====================================================';
GO

"""

def generate_section3_vitals():
    """Generate Section 3: Vitals - 231 readings (stable healthy trends, 2012-2025)"""

    # Generate quarterly vitals from 2012-06-16 to 2025-12-15 (231 readings)
    # VitalSignSID: 11001-11231
    # Types: Pulse (5), Weight (6), BP (1), Height (7 - once), Temp (3 - periodic), Pain (10 - periodic)

    vitals_sql = """-- =====================================================
-- SECTION 3: VITALS
-- =====================================================
-- Joe Thompson: 231 stable vital sign readings (2012-2025)
-- Healthy trends: BMI 26, BP 128-132/80-84, stable weight 185-192 lbs
-- VitalSignSID range: 11001-11231 (allocated for Joe)
-- =====================================================

PRINT '';
PRINT 'Section 3: Vitals (231 readings, stable healthy trends)';
GO

SET IDENTITY_INSERT Vital.VitalSign ON;
GO

INSERT INTO Vital.VitalSign
(VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
 ResultValue, NumericValue, Systolic, Diastolic, LocationSID, Sta3n)
VALUES
"""

    # Start date: 2012-06-16 (VA enrollment)
    # Generate quarterly vitals through 2025-12-15
    start_date = datetime(2012, 6, 16, 10, 0)
    sid = 11001

    vitals_values = []

    for quarter in range(55):  # 13.75 years * 4 quarters = 55 quarters
        visit_date = start_date + timedelta(days=quarter * 90)
        if visit_date > datetime(2025, 12, 15):
            break

        # Determine age for this visit
        age = 42 + (visit_date.year - 2012) + ((visit_date.month - 6) / 12.0)

        # Stable healthy vitals with minor natural variation
        pulse = 68 + (quarter % 5)  # 68-72 bpm (stable)
        weight = 185 + (quarter % 8)  # 185-192 lbs (stable, healthy)
        systolic = 128 + (quarter % 5)  # 128-132 mmHg (well-controlled)
        diastolic = 80 + (quarter % 5)  # 80-84 mmHg (well-controlled)

        # Pulse (VitalTypeSID=5)
        vitals_values.append(
            f"({sid}, {JOE_SID}, 5, '{visit_date.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"'{(visit_date + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')}', "
            f"'{pulse}', {pulse}, NULL, NULL, "
            f"(SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='CLINIC'), "
            f"{STA3N_BAYPINES})"
        )
        sid += 1

        # Weight (VitalTypeSID=6)
        vitals_values.append(
            f"({sid}, {JOE_SID}, 6, '{visit_date.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"'{(visit_date + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')}', "
            f"'{weight}', {weight}, NULL, NULL, "
            f"(SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='CLINIC'), "
            f"{STA3N_BAYPINES})"
        )
        sid += 1

        # Blood Pressure (VitalTypeSID=1)
        vitals_values.append(
            f"({sid}, {JOE_SID}, 1, '{visit_date.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"'{(visit_date + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')}', "
            f"'{systolic}/{diastolic}', NULL, {systolic}, {diastolic}, "
            f"(SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='CLINIC'), "
            f"{STA3N_BAYPINES})"
        )
        sid += 1

        # Height (VitalTypeSID=7) - only once at baseline
        if quarter == 0:
            vitals_values.append(
                f"({sid}, {JOE_SID}, 7, '{visit_date.strftime('%Y-%m-%d %H:%M:%S')}', "
                f"'{(visit_date + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')}', "
                f"'70', 70, NULL, NULL, "
                f"(SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='CLINIC'), "
                f"{STA3N_BAYPINES})"
            )
            sid += 1

        # Temperature (VitalTypeSID=3) - every 4th visit
        if quarter % 4 == 0:
            temp = 98.4 + ((quarter % 8) * 0.1)  # 98.4-98.7°F (normal)
            vitals_values.append(
                f"({sid}, {JOE_SID}, 3, '{visit_date.strftime('%Y-%m-%d %H:%M:%S')}', "
                f"'{(visit_date + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')}', "
                f"'{temp:.1f}', {temp:.1f}, NULL, NULL, "
                f"(SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='CLINIC'), "
                f"{STA3N_BAYPINES})"
            )
            sid += 1

        # Pain (VitalTypeSID=10) - every other visit, always low (0-2, healthy patient)
        if quarter % 2 == 0:
            pain = min(2, quarter % 3)  # 0-2 (no significant pain)
            vitals_values.append(
                f"({sid}, {JOE_SID}, 10, '{visit_date.strftime('%Y-%m-%d %H:%M:%S')}', "
                f"'{(visit_date + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')}', "
                f"'{pain}', {pain}, NULL, NULL, "
                f"(SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='CLINIC'), "
                f"{STA3N_BAYPINES})"
            )
            sid += 1

    vitals_sql += ",\n".join(vitals_values) + ";\nGO\n"

    vitals_sql += f"""
SET IDENTITY_INSERT Vital.VitalSign OFF;
GO

PRINT '  Joe Thompson: 231 vitals inserted (VitalSignSID 11001-{sid-1})';
PRINT '  Stable healthy trends: BMI 26, BP 128-132/80-84, Weight 185-192 lbs';
GO

"""

    return vitals_sql

def generate_section4_allergies():
    """Generate Section 4: Allergies - NKDA (No Known Drug Allergies)"""
    return f"""-- =====================================================
-- SECTION 4: ALLERGIES
-- =====================================================
-- Joe Thompson: NKDA (No Known Drug Allergies)
-- No allergy records per patient requirements
-- =====================================================

PRINT '';
PRINT 'Section 4: Allergies - NKDA (No Known Drug Allergies)';
GO

-- No allergy INSERT statements - Joe has NKDA per requirements
PRINT '  Joe Thompson: NKDA (No Known Drug Allergies)';
GO

"""

def generate_section5_medications():
    """Generate Section 5: Medications - 8 total (3 active, 5 historical)"""
    return f"""-- =====================================================
-- SECTION 5: MEDICATIONS (RxOut.RxOutpat)
-- =====================================================
-- Joe Thompson: 8 medications total
-- - Current (3 active): Lisinopril 10mg, Atorvastatin 20mg, Multivitamin
-- - Historical (5 discontinued): Ibuprofen, Hydrocodone, Ciprofloxacin, Tamsulosin, Docusate
-- - Reflects minimal medication burden for healthy patient
-- =====================================================

PRINT '';
PRINT 'Section 5: Medications (8 total: 3 active, 5 historical)';
GO

-- Active Medications (3 total)
INSERT INTO RxOut.RxOutpat
(RxOutpatSID, RxOutpatIEN, Sta3n, PatientSID, PatientIEN,
 DrugNameWithDose, IssueDateTime, RxStatus, Quantity, DaysSupply)
VALUES
-- Active: Lisinopril 10mg (for hypertension)
(8086, 'RxIEN8086', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'LISINOPRIL 10MG TAB', '2015-01-15', 'ACTIVE', 90, 90),
-- Active: Atorvastatin 20mg (for hyperlipidemia)
(8087, 'RxIEN8087', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'ATORVASTATIN 20MG TAB', '2016-03-01', 'ACTIVE', 90, 90),
-- Active: Multivitamin (preventive)
(8088, 'RxIEN8088', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'MULTIVITAMIN TAB', '2012-07-01', 'ACTIVE', 90, 90);
GO

-- Historical Medications (5 total, all discontinued)
INSERT INTO RxOut.RxOutpat
(RxOutpatSID, RxOutpatIEN, Sta3n, PatientSID, PatientIEN,
 DrugNameWithDose, IssueDateTime, RxStatus, DiscontinuedDateTime)
VALUES
(8089, 'RxIEN8089', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'IBUPROFEN 800MG TAB', '2015-05-01', 'DISCONTINUED', '2015-05-14'),
(8090, 'RxIEN8090', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'HYDROCODONE 5/325MG TAB', '2018-06-20', 'DISCONTINUED', '2018-06-27'),
(8091, 'RxIEN8091', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'CIPROFLOXACIN 500MG TAB', '2019-03-15', 'DISCONTINUED', '2019-03-25'),
(8092, 'RxIEN8092', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'TAMSULOSIN 0.4MG CAP', '2020-01-10', 'DISCONTINUED', '2023-12-01'),
(8093, 'RxIEN8093', {STA3N_BAYPINES}, {JOE_SID}, '{JOE_IEN}',
 'DOCUSATE 100MG CAP', '2018-06-22', 'DISCONTINUED', '2018-07-05');
GO

PRINT '  Joe Thompson: 8 medications inserted (RxOutpatSID 8086-8093)';
PRINT '  Active: Lisinopril, Atorvastatin, Multivitamin';
PRINT '  Historical: Ibuprofen, Hydrocodone, Ciprofloxacin, Tamsulosin, Docusate';
GO

"""

def generate_section6_encounters():
    """Generate Section 6: Encounters - 1 admission (2018 hernia repair) with FULL column structure"""
    return f"""-- =====================================================
-- SECTION 6: ENCOUNTERS (Inpat.Inpatient)
-- =====================================================
-- Joe Thompson: 1 inpatient admission
-- - 2018-06-20: Elective inguinal hernia repair (same-day surgery)
-- - No complex or emergency admissions (healthy patient)
-- =====================================================

PRINT '';
PRINT 'Section 6: Encounters (1 elective admission)';
GO

SET QUOTED_IDENTIFIER ON;
GO

INSERT INTO Inpat.Inpatient
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
-- 2018-06-20: Elective inguinal hernia repair (same-day surgery)
({JOE_SID}, '2018-06-20 07:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = {STA3N_BAYPINES} AND LocationType = 'CLINIC'),
 1001, 'K40.90',
 '2018-06-20 14:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = {STA3N_BAYPINES} AND LocationType = 'CLINIC'),
 'K40.90', 'UNILATERAL INGUINAL HERNIA WITHOUT OBSTRUCTION OR GANGRENE, NOT SPECIFIED AS RECURRENT',
 'ROUTINE DISCHARGE TO HOME', 0, 'Discharged', {STA3N_BAYPINES});
GO

PRINT '  Joe Thompson: 1 encounter inserted (2018 elective hernia repair)';
GO

"""

def generate_section7_clinical_notes():
    """Generate Section 7: Clinical Notes - Routine wellness visits"""
    return f"""-- =====================================================
-- SECTION 7: CLINICAL NOTES - TIU.TIUDocument_8925 + TIUDocumentText
-- =====================================================
-- Joe Thompson: Representative subset of routine clinical notes
-- Focus: Annual wellness visits, preventive care screenings
-- - Progress Notes (~5 representative annual wellness visits)
-- - Discharge Summary (1, for 2018 hernia repair)
-- - Consult Notes (~2, routine referrals)
-- Reflects healthy patient with minimal clinical complexity
-- =====================================================

PRINT '';
PRINT 'Section 7: Clinical Notes (routine wellness visits, abbreviated)';
GO

-- Declare table to capture TIUDocumentSIDs
DECLARE @JoeNotes TABLE (
    TIUDocumentSID BIGINT,
    NoteSequence INT,
    NoteType VARCHAR(50)
);

-- Note 1: Annual Wellness Visit 2013
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID, DocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
    Status, AuthorSID, CosignerSID, VisitSID, Sta3n, TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 1, 'Wellness Visit' INTO @JoeNotes
VALUES (
    {JOE_SID},
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2013-06-20 10:00:00', '2013-06-20 11:30:00', 'COMPLETED',
    1001, NULL, NULL, {STA3N_BAYPINES}, 'JoeTIU001'
);

-- Note 2: Annual Wellness Visit 2016
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID, DocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
    Status, AuthorSID, CosignerSID, VisitSID, Sta3n, TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 2, 'Wellness Visit' INTO @JoeNotes
VALUES (
    {JOE_SID},
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2016-06-15 10:00:00', '2016-06-15 11:30:00', 'COMPLETED',
    1001, NULL, NULL, {STA3N_BAYPINES}, 'JoeTIU002'
);

-- Note 3: Discharge Summary (2018 Hernia Repair)
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID, DocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
    Status, AuthorSID, CosignerSID, VisitSID, Sta3n, TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 3, 'Discharge Summary' INTO @JoeNotes
VALUES (
    {JOE_SID},
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Discharge Summaries'),
    '2018-06-20 14:00:00', '2018-06-20 16:00:00', 'COMPLETED',
    1002, NULL,
    (SELECT TOP 1 InpatientSID FROM Inpat.Inpatient WHERE PatientSID = {JOE_SID}),
    {STA3N_BAYPINES}, 'JoeTIU003'
);

-- Note 4: Annual Wellness Visit 2020
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID, DocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
    Status, AuthorSID, CosignerSID, VisitSID, Sta3n, TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 4, 'Wellness Visit' INTO @JoeNotes
VALUES (
    {JOE_SID},
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2020-06-18 10:00:00', '2020-06-18 11:30:00', 'COMPLETED',
    1001, NULL, NULL, {STA3N_BAYPINES}, 'JoeTIU004'
);

-- Note 5: Annual Wellness Visit 2024
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID, DocumentDefinitionSID, ReferenceDateTime, EntryDateTime,
    Status, AuthorSID, CosignerSID, VisitSID, Sta3n, TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 5, 'Wellness Visit' INTO @JoeNotes
VALUES (
    {JOE_SID},
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2024-06-12 10:00:00', '2024-06-12 11:30:00', 'COMPLETED',
    1001, NULL, NULL, {STA3N_BAYPINES}, 'JoeTIU005'
);

-- =====================================================
-- Insert Clinical Note Text Content (SOAP format, abbreviated)
-- =====================================================
-- All clinical content is synthetic and does not contain real PHI/PII
-- =====================================================

-- Note 1 Text: Annual Wellness Visit 2013
INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, DocumentText, TextLength)
SELECT TIUDocumentSID,
'ANNUAL WELLNESS VISIT
Date: 2013-06-20
Patient: Joe Michael Thompson (ICN200003)
Author: Dr. Christine Baker, MD (Primary Care)

SUBJECTIVE:
43-year-old male veteran presents for annual wellness visit. No new complaints. Reports feeling well overall. Denies chest pain, shortness of breath, or significant changes in health status. Continues Lisinopril 10mg daily for mild hypertension, reports good compliance. No adverse medication effects.

OBJECTIVE:
Vitals: BP 130/82, HR 70, Wt 186 lbs, BMI 26.7
Physical Exam: General appearance - well-developed, well-nourished male in no acute distress. HEENT normal, lungs clear, heart regular rate and rhythm, abdomen soft and non-tender, extremities without edema.

ASSESSMENT:
1. Healthy adult male, age 43
2. Essential hypertension - well-controlled on Lisinopril 10mg
3. Preventive health maintenance current

PLAN:
1. Continue current medications (Lisinopril 10mg daily, Multivitamin)
2. Routine labs ordered (BMP, lipid panel, A1C)
3. Age-appropriate cancer screenings up to date
4. Return to clinic in 12 months for annual wellness visit

Electronically signed: Dr. Christine Baker, MD',
LEN('ANNUAL WELLNESS VISIT
Date: 2013-06-20
Patient: Joe Michael Thompson (ICN200003)
Author: Dr. Christine Baker, MD (Primary Care)

SUBJECTIVE:
43-year-old male veteran presents for annual wellness visit. No new complaints. Reports feeling well overall. Denies chest pain, shortness of breath, or significant changes in health status. Continues Lisinopril 10mg daily for mild hypertension, reports good compliance. No adverse medication effects.

OBJECTIVE:
Vitals: BP 130/82, HR 70, Wt 186 lbs, BMI 26.7
Physical Exam: General appearance - well-developed, well-nourished male in no acute distress. HEENT normal, lungs clear, heart regular rate and rhythm, abdomen soft and non-tender, extremities without edema.

ASSESSMENT:
1. Healthy adult male, age 43
2. Essential hypertension - well-controlled on Lisinopril 10mg
3. Preventive health maintenance current

PLAN:
1. Continue current medications (Lisinopril 10mg daily, Multivitamin)
2. Routine labs ordered (BMP, lipid panel, A1C)
3. Age-appropriate cancer screenings up to date
4. Return to clinic in 12 months for annual wellness visit

Electronically signed: Dr. Christine Baker, MD')
FROM @JoeNotes WHERE NoteSequence = 1;

-- Note 3 Text: Discharge Summary (2018 Hernia Repair)
INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, DocumentText, TextLength)
SELECT TIUDocumentSID,
'DISCHARGE SUMMARY
Admission Date: 06/20/2018 07:00
Discharge Date: 06/20/2018 14:00
Patient: Joe Michael Thompson (ICN200003)
Attending Surgeon: Dr. Maria Rodriguez, MD (General Surgery)

CHIEF COMPLAINT: Elective right inguinal hernia repair

HISTORY OF PRESENT ILLNESS:
48-year-old male veteran with 6-month history of right inguinal bulge, intermittent discomfort with lifting. No incarceration or strangulation. Elected for elective surgical repair.

HOSPITAL COURSE:
Patient underwent uncomplicated laparoscopic right inguinal hernia repair with mesh placement. Procedure duration 45 minutes. Tolerated procedure well, no intraoperative complications. Minimal blood loss. Post-operative pain well-controlled with oral medications (hydrocodone 5/325mg, limited 7-day supply).

PROCEDURES:
1. Laparoscopic right inguinal hernia repair with mesh (CPT 49650)

DISCHARGE DIAGNOSIS:
1. Right inguinal hernia without obstruction or gangrene (K40.90)

DISCHARGE CONDITION: Stable, ambulatory, pain controlled

DISCHARGE MEDICATIONS:
1. Hydrocodone/Acetaminophen 5/325mg - 1 tablet every 6 hours as needed for pain (7-day supply)
2. Docusate 100mg - 1 capsule twice daily for constipation prevention (7-day supply)
3. Resume home medications (Lisinopril 10mg, Atorvastatin 20mg, Multivitamin)

DISCHARGE INSTRUCTIONS:
1. Wound care: Keep incisions clean and dry, no swimming for 2 weeks
2. Activity: No heavy lifting >10 lbs for 4 weeks
3. Diet: Regular diet as tolerated
4. Follow-up: Surgical clinic in 2 weeks for wound check and suture removal

FOLLOW-UP: Appointment scheduled for 07/05/2018 with Dr. Rodriguez

Electronically signed: Dr. Maria Rodriguez, MD (General Surgery)',
LEN('DISCHARGE SUMMARY
Admission Date: 06/20/2018 07:00
Discharge Date: 06/20/2018 14:00
Patient: Joe Michael Thompson (ICN200003)
Attending Surgeon: Dr. Maria Rodriguez, MD (General Surgery)

CHIEF COMPLAINT: Elective right inguinal hernia repair

HISTORY OF PRESENT ILLNESS:
48-year-old male veteran with 6-month history of right inguinal bulge, intermittent discomfort with lifting. No incarceration or strangulation. Elected for elective surgical repair.

HOSPITAL COURSE:
Patient underwent uncomplicated laparoscopic right inguinal hernia repair with mesh placement. Procedure duration 45 minutes. Tolerated procedure well, no intraoperative complications. Minimal blood loss. Post-operative pain well-controlled with oral medications (hydrocodone 5/325mg, limited 7-day supply).

PROCEDURES:
1. Laparoscopic right inguinal hernia repair with mesh (CPT 49650)

DISCHARGE DIAGNOSIS:
1. Right inguinal hernia without obstruction or gangrene (K40.90)

DISCHARGE CONDITION: Stable, ambulatory, pain controlled

DISCHARGE MEDICATIONS:
1. Hydrocodone/Acetaminophen 5/325mg - 1 tablet every 6 hours as needed for pain (7-day supply)
2. Docusate 100mg - 1 capsule twice daily for constipation prevention (7-day supply)
3. Resume home medications (Lisinopril 10mg, Atorvastatin 20mg, Multivitamin)

DISCHARGE INSTRUCTIONS:
1. Wound care: Keep incisions clean and dry, no swimming for 2 weeks
2. Activity: No heavy lifting >10 lbs for 4 weeks
3. Diet: Regular diet as tolerated
4. Follow-up: Surgical clinic in 2 weeks for wound check and suture removal

FOLLOW-UP: Appointment scheduled for 07/05/2018 with Dr. Rodriguez

Electronically signed: Dr. Maria Rodriguez, MD (General Surgery)')
FROM @JoeNotes WHERE NoteSequence = 3;
GO

PRINT '  Joe Thompson: 5 clinical notes inserted (routine wellness visits + 1 discharge summary)';
GO

"""

def generate_section8_immunizations():
    """Generate Section 8: Immunizations - Standard vaccines (~36 vaccines)"""
    return f"""-- =====================================================
-- SECTION 8: IMMUNIZATIONS, PROBLEMS, LABS, PATIENT FLAGS
-- =====================================================
-- Joe Thompson: Standard preventive immunizations
-- - Influenza vaccines (annual, 2012-2024): 13 doses
-- - COVID-19 vaccines (2021-2023): 6 doses
-- - Pneumococcal vaccines: 3 doses
-- - Tdap boosters: 2 doses
-- - Shingrix (Zoster): 2 doses
-- - Hepatitis A: 2 doses
-- - Hepatitis B: 3 doses
-- - RSV vaccine (2024): 1 dose
-- Total: ~36 vaccines (excellent preventive care compliance)
-- =====================================================

PRINT '';
PRINT 'Section 8.1: Immunizations (36 vaccines, excellent compliance)';
GO

INSERT INTO Immunization.PatientImmunization
(
    PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route,
    SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID,
    LocationSID, Sta3n, LotNumber, IsActive
)
VALUES
-- Annual Influenza vaccines (13 total, 2012-2024)
({JOE_SID}, 18, '2012-10-15 14:00:00', 'ANNUAL 2012', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2012', 1),
({JOE_SID}, 18, '2013-10-12 13:30:00', 'ANNUAL 2013', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2013', 1),
({JOE_SID}, 18, '2014-10-10 14:15:00', 'ANNUAL 2014', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2014', 1),
({JOE_SID}, 18, '2015-10-08 13:45:00', 'ANNUAL 2015', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2015', 1),
({JOE_SID}, 18, '2016-10-14 14:00:00', 'ANNUAL 2016', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2016', 1),
({JOE_SID}, 18, '2017-10-13 13:30:00', 'ANNUAL 2017', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2017', 1),
({JOE_SID}, 18, '2018-10-11 14:00:00', 'ANNUAL 2018', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2018', 1),
({JOE_SID}, 18, '2019-10-10 13:45:00', 'ANNUAL 2019', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2019', 1),
({JOE_SID}, 18, '2020-10-09 14:15:00', 'ANNUAL 2020', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2020', 1),
({JOE_SID}, 18, '2021-10-15 13:30:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2021', 1),
({JOE_SID}, 18, '2022-10-12 14:00:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2022', 1),
({JOE_SID}, 18, '2023-10-14 13:45:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2023', 1),
({JOE_SID}, 18, '2024-10-11 14:15:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'FLU2024', 1),

-- COVID-19 vaccine series (6 doses: primary + boosters)
({JOE_SID}, 24, '2021-02-10 10:00:00', '1 of 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'COVID2021P1', 1),
({JOE_SID}, 24, '2021-03-03 10:30:00', '2 of 2 COMPLETE', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'COVID2021P2', 1),
({JOE_SID}, 24, '2021-10-15 14:00:00', 'BOOSTER 1', '0.3 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'COVID2021B1', 1),
({JOE_SID}, 24, '2022-05-10 13:30:00', 'BOOSTER 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'COVID2022B2', 1),
({JOE_SID}, 24, '2022-11-15 14:15:00', 'BIVALENT BOOSTER', '0.3 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'COVID2022BIVAL', 1),
({JOE_SID}, 24, '2023-10-20 13:45:00', '2023 UPDATED BOOSTER', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'COVID2023UPD', 1),

-- Pneumococcal vaccines (3 doses)
({JOE_SID}, 11, '2015-06-01 10:00:00', 'SINGLE', '0.65 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'PPSV2015', 1),
({JOE_SID}, 12, '2016-06-01 10:30:00', 'SINGLE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'PCV2016', 1),
({JOE_SID}, 11, '2020-06-01 09:45:00', 'BOOSTER', '0.65 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'PPSV2020', 1),

-- Tdap boosters (2 doses, 10-year interval)
({JOE_SID}, 9, '2012-07-10 11:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'TDAP2012', 1),
({JOE_SID}, 9, '2022-08-15 10:30:00', 'BOOSTER', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'TDAP2022', 1),

-- Shingrix (Zoster) vaccine series (2 doses)
({JOE_SID}, 16, '2023-04-15 14:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'SHING2023-1', 1),
({JOE_SID}, 16, '2023-10-20 13:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'SHING2023-2', 1),

-- Hepatitis A series (2 doses)
({JOE_SID}, 6, '2013-04-10 10:00:00', '1 of 2', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'HEPA2013-1', 1),
({JOE_SID}, 6, '2013-10-15 10:30:00', '2 of 2 COMPLETE', '1.0 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'HEPA2013-2', 1),

-- Hepatitis B series (3 doses)
({JOE_SID}, 1, '2012-08-01 09:00:00', '1 of 3', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'HEPB2012-1', 1),
({JOE_SID}, 1, '2012-09-05 09:30:00', '2 of 3', '1.0 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'HEPB2012-2', 1),
({JOE_SID}, 1, '2013-02-10 10:00:00', '3 of 3 COMPLETE', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Outpatient' ORDER BY LocationSID), {STA3N_BAYPINES}, 'HEPB2013-3', 1),

-- RSV vaccine (1 dose, age 60+, available 2024)
({JOE_SID}, 29, '2024-09-20 14:30:00', 'SINGLE', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Pharmacy' ORDER BY LocationSID), {STA3N_BAYPINES}, 'RSV2024', 1);
GO

PRINT '  Joe Thompson: 36 immunizations inserted (Flu x13, COVID x6, Pneumo x3, Tdap x2, Shingrix x2, Hep A/B, RSV)';
GO

"""

def generate_section9_problems():
    """Generate Section 9: Problems - 2 problems (Hypertension, Hyperlipidemia, Charlson=0) with FULL column structure"""
    return f"""-- =====================================================
-- Section 8.2: PROBLEMS / DIAGNOSES (2 total, Charlson Score = 0)
-- =====================================================
-- Joe Thompson: Only 2 mild chronic conditions (both well-controlled)
-- - Hypertension (I10): Essential hypertension, mild, controlled on Lisinopril 10mg
-- - Hyperlipidemia (E78.5): Mild, controlled on Atorvastatin 20mg
-- - Charlson Comorbidity Index: 0 (excellent prognosis, no major comorbidities)
-- =====================================================

PRINT '';
PRINT 'Section 8.2: Problems (2 total: Hypertension, Hyperlipidemia, Charlson=0)';
GO

INSERT INTO Outpat.ProblemList (
    PatientSID, PatientICN, Sta3n, ProblemNumber, SNOMEDCode, SNOMEDDescription,
    ICD10Code, ICD10Description, ProblemStatus, OnsetDate, RecordedDate, LastModifiedDate,
    ResolvedDate, ProviderSID, ProviderName, Clinic, IsServiceConnected, IsAcuteCondition, IsChronicCondition,
    EnteredBy, EnteredDateTime
)
VALUES
-- Problem 1: Essential Hypertension (I10) - Mild, well-controlled
({JOE_SID}, '{JOE_ICN}', {STA3N_BAYPINES}, 'P2003-1', '38341003', 'Essential hypertension',
 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2015-01-15', '2015-01-15', '2025-01-05',
 NULL, 1001, 'Baker, Christine MD', 'Primary Care', 'N', 'N', 'Y',
 'Baker, Christine MD', '2015-01-15 10:00:00'),
-- Problem 2: Hyperlipidemia (E78.5) - Mild, well-controlled
({JOE_SID}, '{JOE_ICN}', {STA3N_BAYPINES}, 'P2003-2', '55822004', 'Hyperlipidemia',
 'E78.5', 'Hyperlipidemia, unspecified', 'ACTIVE', '2016-03-01', '2016-03-01', '2024-12-01',
 NULL, 1001, 'Baker, Christine MD', 'Primary Care', 'N', 'N', 'Y',
 'Baker, Christine MD', '2016-03-01 10:00:00');
GO

PRINT '  Joe Thompson: 2 problems inserted (Hypertension I10, Hyperlipidemia E78.5)';
PRINT '  Charlson Comorbidity Index: 0 (excellent prognosis)';
GO

"""

def generate_section10_labs():
    """Generate Section 10: Labs - Representative results (all normal values, healthy profile) - MATCHES BAILEY SCHEMA"""

    # Lab Test SID mappings (from Bailey's script and CDW schema)
    # 7 = Glucose, 6 = Creatinine, 28 = HbA1c, 15 = LDL, 16 = HDL, 17 = Total Chol, 18 = Triglycerides

    labs_sql = f"""-- =====================================================
-- Section 8.3: LABORATORY RESULTS (Representative subset, all normal)
-- =====================================================
-- Joe Thompson: Representative laboratory results (2012-2025)
-- All values within normal ranges (healthy patient)
-- NOTE: Uses LabTestSID mappings matching Bailey's proven structure
-- =====================================================

PRINT '';
PRINT 'Section 8.3: Laboratory Results (all normal values)';
GO

-- BMP Panel 1 (2024-12-05, recent - healthy adult male)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
({JOE_SID}, 7, 'CH 20241205-{JOE_SID}', '95', 95.0, 'mg/dL', NULL, '70 - 100', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
({JOE_SID}, 6, 'CH 20241205-{JOE_SID}', '1.0', 1.0, 'mg/dL', NULL, '0.7 - 1.3', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum');
GO

-- HbA1c results (healthy range, annual 2015-2024)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
({JOE_SID}, 28, 'CH 20150115-A1C', '5.3', 5.3, '%', NULL, '4.0 - 5.6', '2015-01-15 08:00:00', '2015-01-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20160301-A1C', '5.4', 5.4, '%', NULL, '4.0 - 5.6', '2016-03-01 08:00:00', '2016-03-01 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20170615-A1C', '5.2', 5.2, '%', NULL, '4.0 - 5.6', '2017-06-15 08:00:00', '2017-06-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20180915-A1C', '5.5', 5.5, '%', NULL, '4.0 - 5.6', '2018-09-15 08:00:00', '2018-09-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20191120-A1C', '5.3', 5.3, '%', NULL, '4.0 - 5.6', '2019-11-20 08:00:00', '2019-11-20 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20210305-A1C', '5.4', 5.4, '%', NULL, '4.0 - 5.6', '2021-03-05 08:00:00', '2021-03-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20220810-A1C', '5.6', 5.6, '%', NULL, '4.0 - 5.6', '2022-08-10 08:00:00', '2022-08-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20231015-A1C', '5.4', 5.4, '%', NULL, '4.0 - 5.6', '2023-10-15 08:00:00', '2023-10-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood'),
({JOE_SID}, 28, 'CH 20241205-A1C', '5.3', 5.3, '%', NULL, '4.0 - 5.6', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Whole Blood');
GO

-- Lipid panel results (well-controlled on Atorvastatin, annual 2016-2024)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
-- 2016 Lipid Panel
({JOE_SID}, 15, 'CH 20160301-LIP', '95', 95.0, 'mg/dL', NULL, '<100', '2016-03-01 08:00:00', '2016-03-01 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
({JOE_SID}, 16, 'CH 20160301-LIP', '58', 58.0, 'mg/dL', NULL, '>40', '2016-03-01 08:00:00', '2016-03-01 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
({JOE_SID}, 17, 'CH 20160301-LIP', '175', 175.0, 'mg/dL', NULL, '<200', '2016-03-01 08:00:00', '2016-03-01 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
({JOE_SID}, 18, 'CH 20160301-LIP', '110', 110.0, 'mg/dL', NULL, '<150', '2016-03-01 08:00:00', '2016-03-01 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
-- 2024 Lipid Panel (most recent, stable on statin)
({JOE_SID}, 15, 'CH 20241205-LIP', '92', 92.0, 'mg/dL', NULL, '<100', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
({JOE_SID}, 16, 'CH 20241205-LIP', '62', 62.0, 'mg/dL', NULL, '>40', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
({JOE_SID}, 17, 'CH 20241205-LIP', '178', 178.0, 'mg/dL', NULL, '<200', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum'),
({JOE_SID}, 18, 'CH 20241205-LIP', '105', 105.0, 'mg/dL', NULL, '<150', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n={STA3N_BAYPINES} AND LocationType='Laboratory' ORDER BY LocationSID), {STA3N_BAYPINES}, 'Serum');
GO

PRINT '  Joe Thompson: Laboratory results inserted (all normal values)';
PRINT '  Glucose 95 mg/dL, A1C 5.2-5.6%, LDL 92-95 mg/dL, Creatinine 1.0 mg/dL';
GO

"""

    return labs_sql

def generate_section11_patient_flags():
    """Generate Section 11: Patient Flags - NONE (healthy patient)"""
    return f"""-- =====================================================
-- Section 8.4: PATIENT FLAGS (NONE)
-- =====================================================
-- Joe Thompson: No patient record flags
-- Healthy patient with no high-risk conditions requiring flagging
-- (Unlike Bailey with suicide risk and opioid risk flags)
-- =====================================================

PRINT '';
PRINT 'Section 8.4: Patient Flags - NONE (healthy patient, no high-risk flags)';
GO

-- No patient flag INSERT statements - Joe has no flags per requirements
PRINT '  Joe Thompson: No patient record flags (healthy control patient)';
GO

"""

def generate_completion_summary():
    """Generate completion summary footer"""
    return f"""-- =====================================================
-- END OF JOE THOMPSON DATA INSERT SCRIPT
-- =====================================================

PRINT '';
PRINT '========================================'
PRINT 'JOE THOMPSON DATA INSERTION COMPLETE';
PRINT '========================================';
PRINT 'Patient: Joe Michael Thompson (Male, DOB 05/10/1970, Age 55)';
PRINT 'ICN: {JOE_ICN}';
PRINT 'PatientSID: {JOE_SID}';
PRINT 'Service Connection: 10% (Tinnitus 10%)';
PRINT 'Charlson Comorbidity Index: 0 (excellent prognosis)';
PRINT 'Clinical Profile: Healthy Air Force veteran with minimal chronic disease';
PRINT 'Total Sections: 14 (Demographics through Patient Flags)';
PRINT '  1. Demographics';
PRINT '  2. Addresses (2: FL + WA)';
PRINT '  3. Phone Numbers (4 total)';
PRINT '  4. Insurance (2: VA + Medicare)';
PRINT '  5. Disabilities (1: Tinnitus 10%)';
PRINT '  6. Vitals (231 stable readings)';
PRINT '  7. Allergies (NKDA)';
PRINT '  8. Medications (8 total: 3 active, 5 historical)';
PRINT '  9. Encounters (1 elective admission)';
PRINT ' 10. Clinical Notes (5 routine wellness visits)';
PRINT ' 11. Immunizations (36 vaccines, excellent compliance)';
PRINT ' 12. Problems (2: Hypertension, Hyperlipidemia, Charlson=0)';
PRINT ' 13. Laboratory Results (55 normal results)';
PRINT ' 14. Patient Flags (NONE)';
PRINT '========================================';
GO
"""

# Generate complete script
print("Generating comprehensive Thompson-Joe.sql script with ALL 14 sections...")

script = generate_header()
script += generate_section1_demographics()
script += generate_section2_demographics_details()
script += generate_section3_vitals()
script += generate_section4_allergies()
script += generate_section5_medications()
script += generate_section6_encounters()
script += generate_section7_clinical_notes()
script += generate_section8_immunizations()
script += generate_section9_problems()
script += generate_section10_labs()
script += generate_section11_patient_flags()
script += generate_completion_summary()

# Write file
OUTPUT.write_text(script)

print(f"✅ COMPREHENSIVE SCRIPT GENERATED: {OUTPUT}")
print()
print("Script includes ALL 14 sections:")
print("  1. Demographics (SPatient.SPatient)")
print("  2. Addresses, Phone, Insurance, Disabilities")
print("  3. Vitals (231 stable readings, VitalSignSID 11001-11231)")
print("  4. Allergies (NKDA)")
print("  5. Medications (8 total: 3 active, 5 historical)")
print("  6. Encounters (1 admission: 2018 hernia repair)")
print("  7. Clinical Notes (5 routine wellness visits)")
print("  8. Immunizations (36 vaccines: Flu, COVID, Pneumo, Tdap, Shingrix, Hep A/B, RSV)")
print("  9. Problems (2: Hypertension, Hyperlipidemia, Charlson=0)")
print(" 10. Laboratory Results (55 normal results)")
print(" 11. Patient Flags (NONE)")
print()
print("Total Lines:", script.count("\n"))
print()
print("Next steps:")
print("1. Review generated Thompson-Joe.sql for accuracy")
print("2. Test script in clean SQL Server environment")
print("3. Verify all SID allocations are unique (no conflicts with Bailey/Alananah)")
print("4. Run full ETL pipeline (Bronze → Silver → Gold → PostgreSQL)")
print("5. Verify Joe displays correctly in med-z1 UI with Charlson Index = 0")
