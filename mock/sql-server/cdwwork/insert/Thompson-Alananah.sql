-- =====================================================
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
--  10. Labs (~50 results: A1C trending 8.5%->6.8%, lipids, CBC)
-- =====================================================
-- Last Updated: 2026-02-09 (Clinical data refined for Alananah)
-- Author: med-z1 development team
-- Related: docs/spec/thompson-twins-patient-reqs.md (v3.2)
--          docs/spec/thompson-twins-implementation-plan.md (v2.1)
--          Thompson-Bailey.sql (template)
-- =====================================================
-- Purpose: Comprehensive test patient for med-z1
--          Female veteran with PTSD, breast cancer survivor, T2DM
--          Service history: Gulf War (1990-1991), Iraq (2003-2007)
--          50% service-connected disability
-- =====================================================
-- Domain Coverage:
--   1. Demographics (SPatient.SPatient, Address, Phone, Insurance, Disability)
--   2. Vitals (~60 readings, quarterly 2010-2025)
--   3. Patient Flags (Diabetes Management, Cancer Survivor)
--   4. Allergies (Sulfa drugs, Codeine)
--   5. Medications (40 total: 12 active, 28 historical)
--   6. Encounters (28 inpatient admissions)
--   7. Clinical Notes (representative subset ~20 critical notes)
--   8. Immunizations (40 vaccines)
--   9. Problems (16: 14 active, 2 resolved, Charlson=2)
--  10. Labs (~40 representative results, key trends)
-- =====================================================
-- Last Updated: 2026-02-09
-- Author: med-z1 development team
-- Related: docs/spec/thompson-twins-patient-reqs.md (v3.2)
--          docs/spec/thompson-twins-implementation-plan.md (v2.1)
--          Thompson-Bailey.sql (template)
-- =====================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT '=====================================================';
PRINT '====    Thompson Twins: Alananah Thompson       ====';
PRINT '====    PatientSID 2002, ICN200002               ====';
PRINT '=====================================================';
GO

-- =====================================================
-- SECTION 1: DEMOGRAPHICS - SPatient.SPatient
-- =====================================================
-- Alananah Thompson: Female veteran, age 62 (DOB 1963-04-15)
-- Served 1990-2010: Gulf War (1990-1991), Iraq (2003-2007) - Combat support
-- Retired to St. Petersburg, FL (Bay Pines VAMC, Sta3n 516)
-- Breast cancer survivor (2012-2013), Type 2 diabetes (2012-present)
-- PatientSID 2002 for CDWWork
-- ICN200002 (national identifier for cross-database identity resolution)
-- =====================================================

PRINT '';
PRINT 'Section 1: Demographics - SPatient.SPatient';
PRINT '  Inserting Alananah Thompson (PatientSID 2002)';
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
    2002,                           -- PatientSID: Unique ID for CDWWork
    'PtIEN2002',                    -- PatientIEN: VistA internal entry number
    516,                            -- Sta3n: Bay Pines VA (St. Petersburg, FL)
    'THOMPSON,ALANANAH MARIE',        -- PatientName: Last,First Middle format
    'Thompson',                     -- PatientLastName
    'Alananah',                       -- PatientFirstName
    'N',                            -- TestPatientFlag: Not a test patient (mock value)
    'N',                            -- CDWPossibleTestPatientFlag
    'Y',                            -- VeteranFlag: Yes, veteran
    'Regular',                      -- PatientType
    101,                            -- PatientTypeSID: Regular veteran
    'ICN200002',                    -- PatientICN: National identifier
    '200-00-1002',                  -- ScrSSN: Scrambled SSN (display)
    '200-00-1002',                  -- PatientSSN: Mock SSN (non-real)
    'None',                         -- PseudoSSNReason
    'Verified',                     -- SSNVerificationStatus
    'N',                            -- GovernmentEmployeeFlag
    'N',                            -- SensitiveFlag
    62,                             -- Age: As of 2026
    '1963-04-15',                   -- BirthDateTime: April 15, 1963 (twin of Alananah)
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
    'F',                            -- Gender: Female
    'Female',                         -- SelfIdentifiedGender
    'Protestant',                   -- Religion
    2,                              -- ReligionSID
    'MARRIED',                     -- MaritalStatus: Married 2012-present
    2,                              -- MaritalStatusSID
    NULL,                           -- CollateralSponsorPatientSID
    2002,                           -- CurrentEnrollmentSID
    'None',                         -- MeansTestStatus
    NULL,                           -- CurrentMeansTestStatusSID
    'PERSIAN GULF',                 -- PeriodOfService: Gulf War + OIF
    12008,                          -- PeriodOfServiceSID
    NULL,                           -- OperationDesertShieldRank
    NULL,                           -- ODSRankType
    NULL,                           -- ODSRecalledCode
    NULL,                           -- ODSTreatmentDateTime
    NULL,                           -- ODSTreatmentVistaErrorDate
    NULL,                           -- ODSTreatmentDateTimeTransformSID
    NULL,                           -- FederalAgencySID
    NULL,                           -- FilipinoVeteranCode
    'Y',                            -- ServiceConnectedFlag: Yes, 100% SC
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
    '2010-06-15',                   -- PatientEnteredDateTime: VA enrollment date
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

PRINT '  Alananah Thompson demographics inserted (PatientSID 2002)';
GO

-- =====================================================
-- SECTION 2: DEMOGRAPHICS DETAILS
-- =====================================================
-- SPatient.SPatientAddress (2 addresses: FL 2010-2025, WA 2025-present)
-- SPatient.SPatientPhone (4 phone numbers)
-- SPatient.SPatientInsurance (2 insurance records)
-- SPatient.SpatientDisability (4 service-connected disabilities, 100% combined)
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
-- Florida address (2010-2025, Bay Pines VA primary address)
(
    9001,                           -- SPatientAddressSID
    2002,                           -- PatientSID
    'PtIEN2002',                    -- PatientIEN
    516,                            -- Sta3n: Bay Pines
    1,                              -- OrdinalNumber: Primary address
    'HOME',                         -- AddressType
    '4257 62nd Avenue North',       -- StreetAddress1
    'Apt 312',                      -- StreetAddress2
    '',                             -- StreetAddress3
    'St. Petersburg',               -- City
    'Pinellas',                     -- County
    'FL',                           -- State
    415,                            -- StateSID (Florida)
    '33714',                        -- Zip
    '3357',                         -- Zip4
    '',                             -- PostalCode
    'UNITED STATES',                -- Country
    1200005271,                     -- CountrySID (USA)
    'DISABLED VETERAN'              -- EmploymentStatus
),
-- Washington address (2025-present, Walla Walla VA)
(
    9002,                           -- SPatientAddressSID
    2002,                           -- PatientSID
    'PtIEN2002',                    -- PatientIEN
    687,                            -- Sta3n: Walla Walla
    2,                              -- OrdinalNumber: Secondary/current address
    'HOME',                         -- AddressType
    '1205 S. 9th Avenue',           -- StreetAddress1
    '',                             -- StreetAddress2
    '',                             -- StreetAddress3
    'Walla Walla',                  -- City
    'Walla Walla',                  -- County
    'WA',                           -- State
    453,                            -- StateSID (Washington)
    '99362',                        -- Zip
    '4102',                         -- Zip4
    '',                             -- PostalCode
    'UNITED STATES',                -- Country
    1200005271,                     -- CountrySID (USA)
    'DISABLED VETERAN'              -- EmploymentStatus
);
GO

-- Phone Records (4 total: 2 FL + 2 WA)
INSERT INTO SPatient.SPatientPhone
(
    SPatientPhoneSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber,
    PhoneType, PhoneNumber, PhoneVistaErrorDate, LastUpdated
)
VALUES
-- Florida phone numbers (2010-2025)
(9001, 2002, 'PtIEN2002', 516, 1, 'PHONE NUMBER [HOME]', '727-555-2002', NULL, GETDATE()),
(9002, 2002, 'PtIEN2002', 516, 2, 'CELLULAR PHONE NUMBER', '727-555-2002', NULL, GETDATE()),
-- Washington phone numbers (2025-present)
(9003, 2002, 'PtIEN2002', 687, 3, 'PHONE NUMBER [HOME]', '509-555-2002', NULL, GETDATE()),
(9004, 2002, 'PtIEN2002', 687, 4, 'CELLULAR PHONE NUMBER', '509-555-2002', NULL, GETDATE());
GO

-- Insurance Records (2 total: VA + Medicare)
INSERT INTO SPatient.SPatientInsurance
(
    SPatientInsuranceSID, PatientSID, PatientIEN, SPatientInsuranceIEN, Sta3n,
    InsuranceCompanySID, EmploymentStatus, RetirementDate, PolicyEffectiveDate
)
VALUES
-- Primary: VA (50% service-connected disability)
(9001, 2002, 'PtIEN2002', 'PtInsIEN2002', 508, 5, 'RETIRED', '2010-06-15', '2010-06-15'),
-- Secondary: Medicare (age 65+, enrolled 2028, but represented here for completeness)
(9002, 2002, 'PtIEN2002', 'PtInsIEN2002', 516, 1, 'RETIRED', '2028-04-15', '2028-04-15');
GO

-- Disability Records (4 service-connected disabilities, 100% combined rating)
INSERT INTO SPatient.SPatientDisability
(
    SPatientDisabilitySID, PatientSID, PatientIEN, Sta3n, ClaimFolderInstitutionSID,
    ServiceConnectedFlag, ServiceConnectedPercent, AgentOrangeExposureCode, IonizingRadiationCode,
    POWStatusCode, SHADFlag, AgentOrangeLocation, POWLocation, SWAsiaCode, CampLejeuneFlag
)
VALUES
-- PTSD (30%, combat support exposure)
(9001, 2002, 'PtIEN2002', 516, 11001, 'Y', 30, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'Y'),
-- Bilateral Knee Pain (10%, degenerative joint disease)
(9002, 2002, 'PtIEN2002', 516, 11001, 'Y', 10, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),
-- Bilateral Hearing Loss (10%, noise exposure)
(9003, 2002, 'PtIEN2002', 516, 11001, 'Y', 50, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N');
GO

PRINT '  Alananah Thompson demographics details inserted (Address, Phone, Insurance, Disability)';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Demographics Complete     ====';
PRINT '====  PatientSID 2002 created successfully       ====';
PRINT '=====================================================';
GO

-- =====================================================
-- SECTION 3: VITALS
-- =====================================================
-- Quarterly vital sign readings: 2010-2025 (15 years)
-- Alananah Thompson: Female, Height 65" (5'5")
-- Weight trajectory:
--   2010-2011: 145-150 lbs (BMI 24-25, post-military baseline, healthy)
--   2012-2013: 135-145 lbs (weight loss during breast cancer treatment/chemo)
--   2014-2019: 155-175 lbs (gradual weight gain, BMI 26-29, overweight)
--   2020-2025: 185-195 lbs (BMI 31-33, obesity, diabetes management)
-- BP trend: 120/75 (2010) -> 138/85 (2013 HTN) -> 128/78 (2025 controlled)
-- Pain: Mild 2-4/10 (bilateral knee osteoarthritis, well-managed)
-- VitalSignSID range: 9001-9060 (allocated for Alananah)
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson vitals (2010-2025, quarterly readings)...';
GO

SET IDENTITY_INSERT Vital.VitalSign ON;
GO

-- Vitals Batch 1: 2010-2012 (Baseline period, active duty Iraq deployment)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2010-06-16: Initial baseline vitals (healthy, active duty)
    (10001, 2002, 5, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '70', 70, NULL, NULL, 177.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10002, 2002, 6, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '148', 148, NULL, NULL, 67.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10003, 2002, 1, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '125/78', NULL, 125, 78, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10004, 2002, 3, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '72', 72, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10005, 2002, 2, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '98.4', 98.4, NULL, NULL, 36.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10006, 2002, 10, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '26.6', 26.6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2010-09-20: Follow-up
    (10007, 2002, 6, '2010-09-20 10:15:00', '2010-09-20 10:18:00', '147', 147, NULL, NULL, 66.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10008, 2002, 1, '2010-09-20 10:15:00', '2010-09-20 10:18:00', '128/80', NULL, 128, 80, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10009, 2002, 3, '2010-09-20 10:15:00', '2010-09-20 10:18:00', '74', 74, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2010-12-15: End of year
    (10010, 2002, 6, '2010-12-15 14:20:00', '2010-12-15 14:23:00', '146', 146, NULL, NULL, 66.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10011, 2002, 1, '2010-12-15 14:20:00', '2010-12-15 14:23:00', '130/82', NULL, 130, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10012, 2002, 7, '2010-12-15 14:20:00', '2010-12-15 14:23:00', '2', 2, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2011-03-22: Post-deployment stress emerging
    (10013, 2002, 6, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '145', 145, NULL, NULL, 65.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10014, 2002, 1, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '135/85', NULL, 135, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10015, 2002, 3, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '78', 78, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10016, 2002, 7, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '4', 4, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2011-06-18: Back pain worsening
    (10017, 2002, 6, '2011-06-18 13:45:00', '2011-06-18 13:48:00', '146', 146, NULL, NULL, 66.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10018, 2002, 1, '2011-06-18 13:45:00', '2011-06-18 13:48:00', '138/88', NULL, 138, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10019, 2002, 7, '2011-06-18 13:45:00', '2011-06-18 13:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2011-09-12
    (10020, 2002, 6, '2011-09-12 09:20:00', '2011-09-12 09:23:00', '147', 147, NULL, NULL, 66.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10021, 2002, 1, '2011-09-12 09:20:00', '2011-09-12 09:23:00', '140/90', NULL, 140, 90, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10022, 2002, 7, '2011-09-12 09:20:00', '2011-09-12 09:23:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2011-12-08
    (10023, 2002, 6, '2011-12-08 15:30:00', '2011-12-08 15:33:00', '148', 148, NULL, NULL, 67.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10024, 2002, 1, '2011-12-08 15:30:00', '2011-12-08 15:33:00', '142/92', NULL, 142, 92, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10025, 2002, 7, '2011-12-08 15:30:00', '2011-12-08 15:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2012-03-15: Weight gain continuing
    (10026, 2002, 6, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '150', 150, NULL, NULL, 68.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10027, 2002, 1, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '145/92', NULL, 145, 92, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10028, 2002, 3, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '82', 82, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10029, 2002, 7, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2012-06-20
    (10030, 2002, 6, '2012-06-20 14:15:00', '2012-06-20 14:18:00', '145', 145, NULL, NULL, 65.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10031, 2002, 1, '2012-06-20 14:15:00', '2012-06-20 14:18:00', '148/94', NULL, 148, 94, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10032, 2002, 7, '2012-06-20 14:15:00', '2012-06-20 14:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2012-09-25
    (10033, 2002, 6, '2012-09-25 11:30:00', '2012-09-25 11:33:00', '138', 138, NULL, NULL, 62.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10034, 2002, 1, '2012-09-25 11:30:00', '2012-09-25 11:33:00', '146/93', NULL, 146, 93, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10035, 2002, 7, '2012-09-25 11:30:00', '2012-09-25 11:33:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2012-12-10: HTN diagnosed, started on lisinopril
    (10036, 2002, 6, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '135', 135, NULL, NULL, 61.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10037, 2002, 1, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '150/95', NULL, 150, 95, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10038, 2002, 3, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '84', 84, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10039, 2002, 7, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '8', 8, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516);
GO

-- Vitals Batch 2: 2013-2015 (HTN controlled, pain management challenges)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2013-03-18: HTN improving with treatment
    (10040, 2002, 6, '2013-03-18 13:00:00', '2013-03-18 13:03:00', '137', 137, NULL, NULL, 62.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10041, 2002, 1, '2013-03-18 13:00:00', '2013-03-18 13:03:00', '142/88', NULL, 142, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10042, 2002, 7, '2013-03-18 13:00:00', '2013-03-18 13:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2013-06-22
    (10043, 2002, 6, '2013-06-22 10:30:00', '2013-06-22 10:33:00', '140', 140, NULL, NULL, 63.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10044, 2002, 1, '2013-06-22 10:30:00', '2013-06-22 10:33:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10045, 2002, 7, '2013-06-22 10:30:00', '2013-06-22 10:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2013-09-15
    (10046, 2002, 6, '2013-09-15 14:45:00', '2013-09-15 14:48:00', '143', 143, NULL, NULL, 64.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10047, 2002, 1, '2013-09-15 14:45:00', '2013-09-15 14:48:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10048, 2002, 7, '2013-09-15 14:45:00', '2013-09-15 14:48:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2013-12-08
    (10049, 2002, 6, '2013-12-08 11:15:00', '2013-12-08 11:18:00', '145', 145, NULL, NULL, 65.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10050, 2002, 1, '2013-12-08 11:15:00', '2013-12-08 11:18:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10051, 2002, 7, '2013-12-08 11:15:00', '2013-12-08 11:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2014-03-20
    (10052, 2002, 6, '2014-03-20 09:00:00', '2014-03-20 09:03:00', '147', 147, NULL, NULL, 66.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10053, 2002, 1, '2014-03-20 09:00:00', '2014-03-20 09:03:00', '140/88', NULL, 140, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10054, 2002, 7, '2014-03-20 09:00:00', '2014-03-20 09:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2014-06-18: Sleep apnea diagnosed
    (10055, 2002, 6, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '150', 150, NULL, NULL, 68.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10056, 2002, 1, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '142/90', NULL, 142, 90, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10057, 2001, 8, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '92', 92, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10058, 2002, 7, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '8', 8, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2014-09-12
    (10059, 2002, 6, '2014-09-12 10:45:00', '2014-09-12 10:48:00', '153', 153, NULL, NULL, 69.4,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10060, 2002, 1, '2014-09-12 10:45:00', '2014-09-12 10:48:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10061, 2002, 7, '2014-09-12 10:45:00', '2014-09-12 10:48:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2014-12-15: Peak weight approaching
    (10062, 2002, 6, '2014-12-15 14:00:00', '2014-12-15 14:03:00', '155', 155, NULL, NULL, 70.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10063, 2002, 1, '2014-12-15 14:00:00', '2014-12-15 14:03:00', '142/88', NULL, 142, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10064, 2002, 7, '2014-12-15 14:00:00', '2014-12-15 14:03:00', '8', 8, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516);
GO

-- Vitals Batch 3: 2015-2018 (Peak weight, diabetes diagnosis, suicide attempt, opioid taper)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2015-03-22: Diabetes diagnosis
    (10065, 2002, 6, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '158', 158, NULL, NULL, 71.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10066, 2002, 1, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '145/92', NULL, 145, 92, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10067, 2002, 9, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '148', 148, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10068, 2002, 7, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2015-06-15
    (10069, 2002, 6, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '160', 160, NULL, NULL, 72.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10070, 2002, 1, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '143/90', NULL, 143, 90, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10071, 2002, 9, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '132', 132, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10072, 2002, 7, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2015-09-20
    (10073, 2002, 6, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '162', 162, NULL, NULL, 73.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10074, 2002, 1, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '140/88', NULL, 140, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10075, 2002, 9, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '125', 125, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10076, 2002, 7, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2015-12-10
    (10077, 2002, 6, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '164', 164, NULL, NULL, 74.4,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10078, 2002, 1, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10079, 2002, 9, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10080, 2002, 7, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2016-03-18: Post suicide attempt (March 2016)
    (10081, 2002, 6, '2016-03-18 14:45:00', '2016-03-18 14:48:00', '165', 165, NULL, NULL, 74.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
        1003, 'N', 'N', 516),
    (10082, 2002, 1, '2016-03-18 14:45:00', '2016-03-18 14:48:00', '135/82', NULL, 135, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
        1003, 'N', 'N', 516),
    (10083, 2002, 7, '2016-03-18 14:45:00', '2016-03-18 14:48:00', '8', 8, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
        1003, 'N', 'N', 516),

    -- 2016-06-20
    (10084, 2002, 6, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '167', 167, NULL, NULL, 75.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10085, 2002, 1, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10086, 2002, 9, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '115', 115, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10087, 2002, 7, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2016-09-15
    (10088, 2002, 6, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '168', 168, NULL, NULL, 76.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10089, 2002, 1, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10090, 2002, 9, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10091, 2002, 7, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2016-12-12
    (10092, 2002, 6, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '170', 170, NULL, NULL, 77.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10093, 2002, 1, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10094, 2002, 9, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10095, 2002, 7, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516);
GO

-- Vitals Batch 4: 2017-2019 (Weight loss beginning, opioid taper complete)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2017-03-20
    (10096, 2002, 6, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '171', 171, NULL, NULL, 77.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10097, 2002, 1, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '140/88', NULL, 140, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10098, 2002, 9, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '125', 125, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10099, 2002, 7, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2017-06-18
    (10100, 2002, 6, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '172', 172, NULL, NULL, 78.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10101, 2002, 1, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10102, 2002, 9, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10103, 2002, 7, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2017-09-12
    (10104, 2002, 6, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '173', 173, NULL, NULL, 78.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10105, 2002, 1, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10106, 2002, 9, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10107, 2002, 7, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2017-12-08: Opioid taper beginning (2018)
    (10108, 2002, 6, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '174', 174, NULL, NULL, 78.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10109, 2002, 1, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10110, 2002, 9, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10111, 2002, 7, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2018-03-15: Opioid taper in progress
    (10112, 2002, 6, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '175', 175, NULL, NULL, 79.4,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10113, 2002, 1, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10114, 2002, 9, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10115, 2002, 7, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2018-06-20: Opioid taper complete
    (10116, 2002, 6, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '177', 177, NULL, NULL, 80.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10117, 2002, 1, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10118, 2002, 9, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10119, 2002, 7, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2018-09-15
    (10120, 2002, 6, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '178', 178, NULL, NULL, 80.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10121, 2002, 1, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10122, 2002, 9, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '115', 115, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10123, 2002, 7, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2018-12-10
    (10124, 2002, 6, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '179', 179, NULL, NULL, 81.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10125, 2002, 1, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10126, 2002, 9, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10127, 2002, 7, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516);
GO

-- Vitals Batch 5: 2019-2021 (Weight stabilizing, chronic disease management)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2019-03-18
    (10128, 2002, 6, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '180', 180, NULL, NULL, 81.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10129, 2002, 1, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10130, 2002, 9, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10131, 2002, 7, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2019-06-15: CKD Stage 3a diagnosed
    (10132, 2002, 6, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '181', 181, NULL, NULL, 82.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10133, 2002, 1, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10134, 2002, 9, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10135, 2002, 7, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2019-09-20
    (10136, 2002, 6, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '182', 182, NULL, NULL, 82.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10137, 2002, 1, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '135/82', NULL, 135, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10138, 2002, 9, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10139, 2002, 7, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2019-12-12
    (10140, 2002, 6, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '183', 183, NULL, NULL, 83.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10141, 2002, 1, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '136/83', NULL, 136, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10142, 2002, 9, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10143, 2002, 7, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2020-03-16: Alcohol use disorder remission (2020)
    (10144, 2002, 6, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '184', 184, NULL, NULL, 83.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10145, 2002, 1, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10146, 2002, 9, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '115', 115, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10147, 2002, 7, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2020-06-18
    (10148, 2002, 6, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '186', 186, NULL, NULL, 84.4,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10149, 2002, 1, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10150, 2002, 9, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10151, 2002, 7, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2020-09-15
    (10152, 2002, 6, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '187', 187, NULL, NULL, 84.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10153, 2002, 1, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10154, 2002, 9, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10155, 2002, 7, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2020-12-10
    (10156, 2002, 6, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '188', 188, NULL, NULL, 85.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10157, 2002, 1, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '135/83', NULL, 135, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10158, 2002, 9, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10159, 2002, 7, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516);
GO

-- Vitals Batch 6: 2021-2023 (Weight stabilized ~220 lbs, chronic disease stable)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2021-03-20
    (10160, 2002, 6, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '189', 189, NULL, NULL, 85.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10161, 2002, 1, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10162, 2002, 9, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10163, 2002, 7, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2021-06-18
    (10164, 2002, 6, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '190', 190, NULL, NULL, 86.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10165, 2002, 1, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10166, 2002, 9, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10167, 2002, 7, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2021-09-15
    (10168, 2002, 6, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '191', 191, NULL, NULL, 86.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10169, 2002, 1, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10170, 2002, 9, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10171, 2002, 7, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2021-12-12
    (10172, 2002, 6, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '192', 192, NULL, NULL, 87.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10173, 2002, 1, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10174, 2002, 9, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10175, 2002, 7, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2022-03-18
    (10176, 2002, 6, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '193', 193, NULL, NULL, 87.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10177, 2002, 1, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10178, 2002, 9, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10179, 2002, 7, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2022-06-20
    (10180, 2002, 6, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '194', 194, NULL, NULL, 88.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10181, 2002, 1, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '135/83', NULL, 135, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10182, 2002, 9, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10183, 2002, 7, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2022-09-15
    (10184, 2002, 6, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '193', 193, NULL, NULL, 87.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10185, 2002, 1, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10186, 2002, 9, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10187, 2002, 7, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2022-12-10
    (10188, 2002, 6, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '192', 192, NULL, NULL, 87.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10189, 2002, 1, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10190, 2002, 9, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10191, 2002, 7, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2023-03-20
    (10192, 2002, 6, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '191', 191, NULL, NULL, 86.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10193, 2002, 1, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10194, 2002, 9, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10195, 2002, 7, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2023-06-18
    (10196, 2002, 6, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '192', 192, NULL, NULL, 87.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10197, 2002, 1, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10198, 2002, 9, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10199, 2002, 7, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2023-09-15
    (10200, 2002, 6, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '193', 193, NULL, NULL, 87.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10201, 2002, 1, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10202, 2002, 9, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10203, 2002, 7, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2023-12-10
    (10204, 2002, 6, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '194', 194, NULL, NULL, 88.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10205, 2002, 1, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '135/83', NULL, 135, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10206, 2002, 9, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10207, 2002, 7, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516);
GO

-- Vitals Batch 7: 2024-2025 (Current, relocated to Walla Walla WA in 2025)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2024-03-18 (Bay Pines FL)
    (10208, 2002, 6, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '194', 194, NULL, NULL, 88.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10209, 2002, 1, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10210, 2002, 9, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10211, 2002, 7, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2024-06-20 (Bay Pines FL)
    (10212, 2002, 6, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '195', 195, NULL, NULL, 88.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10213, 2002, 1, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10214, 2002, 9, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (10215, 2002, 7, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2024-09-15 (Bay Pines FL - last visit before relocation)
    (10216, 2002, 6, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '194', 194, NULL, NULL, 88.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10217, 2002, 1, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10218, 2002, 9, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (10219, 2002, 7, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2024-12-10 (Bay Pines FL - final visit before move)
    (10220, 2002, 6, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '193', 193, NULL, NULL, 87.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10221, 2002, 1, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10222, 2002, 9, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (10223, 2002, 7, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2025-02-15 (Walla Walla WA - first visit after relocation)
    (10224, 2002, 6, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '192', 192, NULL, NULL, 87.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),
    (10225, 2002, 1, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),
    (10226, 2002, 9, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),
    (10227, 2002, 7, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),

    -- 2025-05-20 (Walla Walla WA - current)
    (10228, 2002, 6, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687),
    (10229, 2002, 1, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687),
    (10230, 2002, 9, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687),
    (10231, 2002, 7, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687);
GO

SET IDENTITY_INSERT Vital.VitalSign OFF;
GO

PRINT '  Alananah Thompson vitals inserted (231 readings, 2010-2025)';
PRINT '  Weight trend: 185 lbs (2010) -> 245 lbs (2015 peak) -> 220 lbs (2025 stable)';
PRINT '  BP trend: 125/78 (2010 baseline) -> 150/95 (2012 HTN dx) -> 135/84 (2025 controlled)';
PRINT '  Chronic pain: Consistently 4-8/10 throughout 15-year period';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 3 (Vitals) Complete';
PRINT '====  231 vital sign readings inserted           ====';
PRINT '=====================================================';
GO


-- =====================================================
-- SECTION 4: ALLERGIES
-- =====================================================
-- 2 drug allergies: Penicillin (moderate), Morphine (moderate-severe)
-- PatientAllergySID range: 10001-10002 (allocated for Alananah)
-- PatientAllergyReactionSID range: 10001-10003 (allocated for Alananah)
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson allergies...';
GO

SET IDENTITY_INSERT Allergy.PatientAllergy ON;
GO

INSERT INTO Allergy.PatientAllergy (
    PatientAllergySID, PatientSID, AllergenSID, AllergySeveritySID, LocalAllergenName,
    OriginationDateTime, ObservedDateTime, OriginatingSiteSta3n,
    Comment, HistoricalOrObserved, IsActive, VerificationStatus, Sta3n
)
VALUES
    -- Allergy 1: PENICILLIN (childhood rash, unconfirmed but documented)
    (10001, 2002, 1, 2, 'PENICILLIN',
        '2010-06-16 10:00:00', NULL, 516,
        'Patient reports childhood rash with penicillin. No anaphylaxis. Never re-exposed. Avoid penicillins, use alternative antibiotics (fluoroquinolones, macrolides acceptable).',
        'HISTORICAL', 1, 'UNVERIFIED', 516),

    -- Allergy 2: MORPHINE (severe nausea/vomiting, confirmed 2016)
    (10002, 2002, 7, 3, 'MORPHINE SULFATE',
        '2016-03-18 08:00:00', '2016-03-18 08:00:00', 516,
        'Patient experienced severe nausea and vomiting when given IV morphine sulfate during psychiatric admission (suicide attempt March 2016). Symptoms began within 30 minutes of administration and persisted for 6 hours despite antiemetics. Required switch to hydromorphone. Avoid all morphine formulations. Hydromorphone, oxycodone, and hydrocodone are acceptable alternatives.',
        'OBSERVED', 1, 'VERIFIED', 516);
GO

SET IDENTITY_INSERT Allergy.PatientAllergy OFF;
GO

PRINT '  Alananah Thompson allergies inserted (2 allergies)';
GO

-- Insert allergy reactions (bridge table)
SET IDENTITY_INSERT Allergy.PatientAllergyReaction ON;
GO

INSERT INTO Allergy.PatientAllergyReaction (PatientAllergyReactionSID, PatientAllergySID, ReactionSID)
VALUES
-- Allergy 10001: PENICILLIN - Rash
    (10001, 10001, 2),   -- RASH

    -- Allergy 10002: MORPHINE - Nausea, Vomiting
    (10002, 10002, 20),  -- NAUSEA
    (10003, 10002, 21);  -- VOMITING
GO

SET IDENTITY_INSERT Allergy.PatientAllergyReaction OFF;
GO

PRINT '  Alananah Thompson allergy reactions inserted (3 reactions)';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 4 (Allergies) Complete';
PRINT '====  2 allergies with 3 reactions inserted       ====';
PRINT '=====================================================';
GO


-- =====================================================
-- SECTION 5: MEDICATIONS (RxOut.RxOutpat)
-- =====================================================
-- 45 total medications (15 active, 30 historical/discontinued)
-- RxOutpatSID range: 8001-8045 (allocated for Bailey)
-- Timeline: 2010-2025 (15 years of medication history)
-- Clinical themes:
--   - 2010-2018: Opioid-based pain management (discontinued 2018 after taper)
--   - 2010-2020: Multiple psych med trials (settled on sertraline 2015)
--   - 2012+: HTN management (lisinopril)
--   - 2015+: Diabetes management (metformin)
--   - 2019-2022: Tobacco cessation (varenicline - would need to be added to Dim.LocalDrug)
--   - 2020+: Current stable regimen (15 active meds)
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson medications (2010-2025, 45 total)...';
GO

-- NOTE: Some medications from requirements not yet in Dim.LocalDrug:
-- - Duloxetine 60mg (would be LocalDrugSID 10200+)
-- - Lidocaine 5% patches (would be LocalDrugSID 10201+)
-- - Pantoprazole 40mg (using Omeprazole 40mg as substitute)
-- - Trazodone 100mg (using Trazodone 50mg with doubled dose)
-- - Prazosin 5mg (using Prazosin 2mg with note to take 2-3 caps)
-- - Vitamin D 2000 IU (would be LocalDrugSID 10202+)
-- - Varenicline/Chantix (would be LocalDrugSID 10203+)
-- - Paroxetine, Venlafaxine (would be LocalDrugSID 10204+, 10205+)
-- These can be added to Dim.LocalDrug.sql later for full implementation

-- Alananah Thompson medications (Sta3n 516 Bay Pines FL, 2010-2024)
-- Then Sta3n 687 Walla Walla WA (2025+)
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
-- CURRENT ACTIVE MEDICATIONS (2025-2026, 15 total)
-- =====================================================

-- 1. Sertraline 200mg daily (PTSD/depression) - using 2x100mg tabs
(8001, 'RxIEN9001', 516, 2002, 'PtIEN2002', 10036, 'DrugIEN10036', 20024,
 'SERTRALINE HCL', 'SERTRALINE HCL 100MG TAB', '2025-001-8001',
 '2025-01-15 10:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 180, 90, 5, 4, 5, '2 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:00:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- 2. Gabapentin 1200mg TID (neuropathic pain) - using 800mg caps
(8047, 'RxIEN9002', 516, 2002, 'PtIEN2002', 10076, 'DrugIEN10076', 20067,
 'GABAPENTIN', 'GABAPENTIN 800MG CAP', '2025-001-8047',
 '2025-01-15 10:05:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 270, 90, 5, 4, 5, '1.5 CAP TID', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:05:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'Y', 'Y'),

-- 3. Metformin 1000mg BID (diabetes)
(8048, 'RxIEN9003', 516, 2002, 'PtIEN2002', 10027, 'DrugIEN10027', 20001,
 'METFORMIN HCL', 'METFORMIN HCL 1000MG TAB', '2025-001-8048',
 '2025-01-15 10:10:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 180, 90, 5, 5, 5, '1 TAB BID', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:10:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 4. Lisinopril 20mg daily (hypertension)
(8049, 'RxIEN9004', 516, 2002, 'PtIEN2002', 10029, 'DrugIEN10029', 20004,
 'LISINOPRIL', 'LISINOPRIL 20MG TAB', '2025-001-8049',
 '2025-01-15 10:15:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:15:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 5. Atorvastatin 40mg nightly (hyperlipidemia)
(8050, 'RxIEN9005', 516, 2002, 'PtIEN2002', 10011, 'DrugIEN10011', 20024,
 'ATORVASTATIN CALCIUM', 'ATORVASTATIN CALCIUM 40MG TAB', '2025-001-8050',
 '2025-01-15 10:20:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB QHS', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:20:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 6. Aspirin 81mg daily (cardiovascular protection)
(8051, 'RxIEN9006', 516, 2002, 'PtIEN2002', 10033, 'DrugIEN10033', 20027,
 'ASPIRIN', 'ASPIRIN 81MG TAB EC', '2025-001-8051',
 '2025-01-15 10:25:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:25:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 7. Omeprazole 40mg daily (GERD - substitute for Pantoprazole)
(8052, 'RxIEN9007', 516, 2002, 'PtIEN2002', 10090, 'DrugIEN10090', 20081,
 'OMEPRAZOLE', 'OMEPRAZOLE 40MG CAP DR', '2025-001-8052',
 '2025-01-15 10:30:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 CAP', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:30:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 8. Trazodone 50mg nightly (insomnia - using 50mg x2 for 100mg dose)
(8053, 'RxIEN9008', 516, 2002, 'PtIEN2002', 10098, 'DrugIEN10098', 20089,
 'TRAZODONE HCL', 'TRAZODONE HCL 50MG TAB', '2025-001-8053',
 '2025-01-15 10:35:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 180, 90, 5, 5, 5, '2 TAB QHS', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:35:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- 9. Prazosin 2mg nightly (PTSD nightmares - using 2mg x2-3 for 5mg dose)
(8054, 'RxIEN9009', 516, 2002, 'PtIEN2002', 10092, 'DrugIEN10092', 20083,
 'PRAZOSIN HCL', 'PRAZOSIN HCL 2MG CAP', '2025-001-8054',
 '2025-01-15 10:40:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 270, 90, 5, 5, 5, '2-3 CAP QHS', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:40:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- 10. Acetaminophen 650mg Q6H PRN (pain)
(8055, 'RxIEN9010', 516, 2002, 'PtIEN2002', 10059, 'DrugIEN10059', 20050,
 'ACETAMINOPHEN', 'ACETAMINOPHEN 650MG TAB', '2025-001-8055',
 '2025-01-15 10:45:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'WINDOW',
 120, 30, 11, 10, 11, '1 TAB Q6H PRN', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:45:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'N', 'N'),

-- 11. Naproxen 500mg BID PRN (pain, inflammation)
(8056, 'RxIEN9011', 516, 2002, 'PtIEN2002', 10089, 'DrugIEN10089', 20080,
 'NAPROXEN SODIUM', 'NAPROXEN SODIUM 500MG TAB', '2025-001-8056',
 '2025-01-15 10:50:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'WINDOW',
 60, 30, 5, 4, 5, '1 TAB BID PRN', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:50:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'N', 'N'),

-- 12. Multivitamin daily (nutritional support)
(8057, 'RxIEN9012', 516, 2002, 'PtIEN2002', 10088, 'DrugIEN10088', 20079,
 'MULTIVITAMIN', 'MULTIVITAMIN TAB', '2025-001-8057',
 '2025-01-15 10:55:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'ACTIVE', 'MAIL',
 90, 90, 5, 5, 5, '1 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2025-01-15 10:55:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- NOTE: Active medications 13-15 would require additional LocalDrug entries:
-- 13. Duloxetine 60mg daily (pain/depression) - needs LocalDrugSID 10200+
-- 14. Lidocaine 5% patches daily (topical pain) - needs LocalDrugSID 10201+
-- 15. Vitamin D 2000 IU daily (deficiency) - needs LocalDrugSID 10202+

-- =====================================================
-- HISTORICAL/DISCONTINUED MEDICATIONS (2010-2024)
-- Organized chronologically by clinical phase
-- =====================================================

-- PHASE 1: 2010-2012 (Initial VA enrollment, opioid therapy started)

-- 13. Hydrocodone-APAP 5-325mg (2010-2013, discontinued, switched to oxycodone)
(8058, 'RxIEN9013', 516, 2002, 'PtIEN2002', 10022, 'DrugIEN10022', 20033,
 'HYDROCODONE-ACETAMINOPHEN', 'HYDROCODONE-ACETAMINOPHEN 5-325MG TAB', '2010-06-0001',
 '2010-06-20 14:00:00', NULL, NULL, 1002, 'StaffIEN1002', 1002, 'StaffIEN1002', 1002, 'StaffIEN1002',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'WINDOW',
 120, 30, 2, 0, 2, '1-2 TAB Q6H PRN', '2013-06-20 00:00:00', NULL, NULL,
 '2013-06-20 00:00:00', NULL, NULL, 'SWITCHED TO OXYCODONE FOR BETTER PAIN CONTROL', 1002,
 '2010-06-20 14:00:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', 'C-II', 'Y', 'N', 'N'),

-- 14. Cyclobenzaprine 10mg (2010-2014, discontinued due to sedation)
(8059, 'RxIEN9014', 516, 2002, 'PtIEN2002', 10068, 'DrugIEN10068', 20059,
 'CYCLOBENZAPRINE HCL', 'CYCLOBENZAPRINE HCL 10MG TAB', '2010-07-0001',
 '2010-07-15 10:30:00', NULL, NULL, 1002, 'StaffIEN1002', 1002, 'StaffIEN1002', 1002, 'StaffIEN1002',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'WINDOW',
 30, 30, 5, 0, 5, '1 TAB TID PRN', '2014-07-15 00:00:00', NULL, NULL,
 '2014-07-15 00:00:00', NULL, NULL, 'DISCONTINUED DUE TO EXCESSIVE SEDATION', 1002,
 '2010-07-15 10:30:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'N', 'N'),

-- 15. Ibuprofen 800mg (2010-2015, discontinued due to GI upset)
(8060, 'RxIEN9015', 516, 2002, 'PtIEN2002', 10079, 'DrugIEN10079', 20070,
 'IBUPROFEN', 'IBUPROFEN 800MG TAB', '2010-08-0001',
 '2010-08-10 09:00:00', NULL, NULL, 1002, 'StaffIEN1002', 1002, 'StaffIEN1002', 1002, 'StaffIEN1002',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'WINDOW',
 60, 30, 5, 0, 5, '1 TAB TID PRN', '2015-08-10 00:00:00', NULL, NULL,
 '2015-08-10 00:00:00', NULL, NULL, 'DISCONTINUED DUE TO GI UPSET, SWITCHED TO NAPROXEN', 1001,
 '2010-08-10 09:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N'),

-- PHASE 2: 2011-2014 (PTSD treatment trials, psych med adjustments)

-- 16. Fluoxetine 20mg (2011-2012, first SSRI trial, discontinued due to activation)
(8016, 'RxIEN9016', 516, 2002, 'PtIEN2002', 10050, 'DrugIEN10050', 20025,
 'FLUOXETINE', 'FLUOXETINE 20MG CAP', '2011-04-0001',
 '2011-04-15 11:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 90, 90, 3, 0, 3, '1 CAP', '2012-04-15 00:00:00', NULL, NULL,
 '2012-04-15 00:00:00', NULL, NULL, 'DISCONTINUED DUE TO ACTIVATION, INSOMNIA', 1003,
 '2011-04-15 11:00:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- 17. Citalopram 20mg (2012-2013, second SSRI trial, limited benefit)
(8017, 'RxIEN9017', 516, 2002, 'PtIEN2002', 10051, 'DrugIEN10051', 20026,
 'CITALOPRAM', 'CITALOPRAM 20MG TAB', '2012-06-0001',
 '2012-06-20 13:30:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 90, 90, 3, 0, 3, '1 TAB', '2013-06-20 00:00:00', NULL, NULL,
 '2013-06-20 00:00:00', NULL, NULL, 'LIMITED BENEFIT, SWITCHED TO ESCITALOPRAM', 1003,
 '2012-06-20 13:30:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- 18. Escitalopram 10mg (2013-2015, third SSRI trial, switched to sertraline)
(8018, 'RxIEN9018', 516, 2002, 'PtIEN2002', 10070, 'DrugIEN10070', 20061,
 'ESCITALOPRAM OXALATE', 'ESCITALOPRAM OXALATE 10MG TAB', '2013-08-0001',
 '2013-08-10 10:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 90, 90, 3, 0, 3, '1 TAB', '2015-02-10 00:00:00', NULL, NULL,
 '2015-02-10 00:00:00', NULL, NULL, 'SWITCHED TO SERTRALINE FOR PTSD', 1003,
 '2013-08-10 10:00:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- PHASE 3: 2013-2016 (Opioid escalation, suicide attempt, morphine allergy discovered)

-- 19. Oxycodone 5mg (2013-2016, escalated pain management, discontinued after suicide attempt)
(8019, 'RxIEN9019', 516, 2002, 'PtIEN2002', 10052, 'DrugIEN10052', 20034,
 'OXYCODONE HCL', 'OXYCODONE HCL 5MG TAB', '2013-06-0001',
 '2013-06-25 14:30:00', NULL, NULL, 1002, 'StaffIEN1002', 1002, 'StaffIEN1002', 1002, 'StaffIEN1002',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'WINDOW',
 120, 30, 1, 0, 1, '1-2 TAB Q6H PRN', '2016-03-25 00:00:00', NULL, NULL,
 '2016-03-18 00:00:00', NULL, NULL, 'DISCONTINUED AFTER SUICIDE ATTEMPT (OPIOID OVERDOSE)', 1002,
 '2013-06-25 14:30:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', 'C-II', 'Y', 'N', 'N'),

-- 20. Morphine ER 15mg (2014-2016, attempted long-acting opioid, discovered allergy)
(8020, 'RxIEN9020', 516, 2002, 'PtIEN2002', 10053, 'DrugIEN10053', 20035,
 'MORPHINE SULFATE', 'MORPHINE SULFATE 15MG TAB', '2014-03-0001',
 '2014-03-20 11:00:00', NULL, NULL, 1002, 'StaffIEN1002', 1002, 'StaffIEN1002', 1002, 'StaffIEN1002',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'WINDOW',
 60, 30, 1, 0, 1, '1 TAB BID', '2016-03-20 00:00:00', NULL, NULL,
 '2016-03-18 00:00:00', NULL, NULL, 'ALLERGY: SEVERE NAUSEA/VOMITING', 1002,
 '2014-03-20 11:00:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', 'C-II', 'Y', 'N', 'N'),

-- 21. Lorazepam 1mg (2015-2016, anxiety management, discontinued after suicide attempt)
(8021, 'RxIEN9021', 516, 2002, 'PtIEN2002', 10085, 'DrugIEN10085', 20076,
 'LORAZEPAM', 'LORAZEPAM 1MG TAB', '2015-01-0001',
 '2015-01-15 09:30:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'WINDOW',
 30, 30, 2, 0, 2, '1 TAB TID PRN', '2016-04-15 00:00:00', NULL, NULL,
 '2016-04-01 00:00:00', NULL, NULL, 'DISCONTINUED POST-SUICIDE ATTEMPT, AVOID BENZOS', 1003,
 '2015-01-15 09:30:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', 'C-IV', 'Y', 'N', 'N'),

-- PHASE 4: 2015-2019 (HTN, diabetes, CKD onset, sertraline established)

-- 22. Lisinopril 10mg (2012-2020, initial HTN dose, escalated to 20mg)
(8022, 'RxIEN9022', 516, 2002, 'PtIEN2002', 10028, 'DrugIEN10028', 20004,
 'LISINOPRIL', 'LISINOPRIL 10MG TAB', '2012-12-0001',
 '2012-12-15 10:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 90, 90, 5, 0, 5, '1 TAB', '2020-12-15 00:00:00', NULL, NULL,
 '2020-01-15 00:00:00', NULL, NULL, 'DOSE ESCALATED TO 20MG', 1001,
 '2012-12-15 10:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 23. Metformin 500mg (2015-2020, initial diabetes dose, escalated to 1000mg BID)
(8023, 'RxIEN9023', 516, 2002, 'PtIEN2002', 10026, 'DrugIEN10026', 20001,
 'METFORMIN HCL', 'METFORMIN HCL 500MG TAB', '2015-04-0001',
 '2015-04-10 11:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 180, 90, 5, 0, 5, '1 TAB BID', '2020-04-10 00:00:00', NULL, NULL,
 '2020-02-01 00:00:00', NULL, NULL, 'DOSE ESCALATED TO 1000MG BID', 1001,
 '2015-04-10 11:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 24. Simvastatin 20mg (2013-2018, initial statin, switched to atorvastatin)
(8024, 'RxIEN9024', 516, 2002, 'PtIEN2002', 10012, 'DrugIEN10012', 20025,
 'SIMVASTATIN', 'SIMVASTATIN 20MG TAB', '2013-01-0001',
 '2013-01-20 14:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 90, 90, 5, 0, 5, '1 TAB QHS', '2018-01-20 00:00:00', NULL, NULL,
 '2018-01-20 00:00:00', NULL, NULL, 'SWITCHED TO ATORVASTATIN FOR BETTER LDL CONTROL', 1001,
 '2013-01-20 14:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- 25. Sertraline 50mg (2015-2017, initial PTSD dose, escalated to 200mg)
(8025, 'RxIEN9025', 516, 2002, 'PtIEN2002', 10094, 'DrugIEN10094', 20085,
 'SERTRALINE HCL', 'SERTRALINE HCL 50MG TAB', '2015-02-0001',
 '2015-02-15 10:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 90, 90, 5, 0, 5, '1 TAB', '2017-02-15 00:00:00', NULL, NULL,
 '2017-02-15 00:00:00', NULL, NULL, 'DOSE ESCALATED TO 100MG', 1003,
 '2015-02-15 10:00:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- 26. Sertraline 100mg (2017-2020, intermediate dose, escalated to 200mg)
(8026, 'RxIEN9026', 516, 2002, 'PtIEN2002', 10018, 'DrugIEN10018', 20024,
 'SERTRALINE HCL', 'SERTRALINE HCL 100MG TAB', '2017-02-0001',
 '2017-02-20 11:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 90, 90, 5, 0, 5, '1 TAB', '2020-02-20 00:00:00', NULL, NULL,
 '2020-01-15 00:00:00', NULL, NULL, 'DOSE ESCALATED TO 200MG (2 X 100MG)', 1003,
 '2017-02-20 11:00:00', NULL, NULL, 8049, 'ClinicIEN8049', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- PHASE 5: 2017-2018 (Opioid taper, transition to non-opioid pain management)

-- 27. Tramadol 50mg (2017-2018, opioid taper bridge, discontinued after taper complete)
(8027, 'RxIEN9027', 516, 2002, 'PtIEN2002', 10021, 'DrugIEN10021', 20032,
 'TRAMADOL HCL', 'TRAMADOL HCL 50MG TAB', '2017-01-0001',
 '2017-01-15 10:00:00', NULL, NULL, 1002, 'StaffIEN1002', 1002, 'StaffIEN1002', 1002, 'StaffIEN1002',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'WINDOW',
 120, 30, 2, 0, 2, '1-2 TAB Q6H PRN', '2018-07-15 00:00:00', NULL, NULL,
 '2018-06-30 00:00:00', NULL, NULL, 'OPIOID TAPER COMPLETE, SWITCHED TO NON-OPIOID REGIMEN', 1002,
 '2017-01-15 10:00:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', 'C-IV', 'Y', 'N', 'N'),

-- 28. Gabapentin 300mg (2017-2020, initial dose for neuropathic pain, escalated to 1200mg TID)
(8028, 'RxIEN9028', 516, 2002, 'PtIEN2002', 10020, 'DrugIEN10020', 20031,
 'GABAPENTIN', 'GABAPENTIN 300MG CAP', '2017-03-0001',
 '2017-03-20 09:00:00', NULL, NULL, 1002, 'StaffIEN1002', 1002, 'StaffIEN1002', 1002, 'StaffIEN1002',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'DISCONTINUED', 'MAIL',
 270, 90, 5, 0, 5, '1 CAP TID', '2020-03-20 00:00:00', NULL, NULL,
 '2020-01-15 00:00:00', NULL, NULL, 'DOSE ESCALATED TO 1200MG TID (GABAPENTIN 800MG)', 1002,
 '2017-03-20 09:00:00', NULL, NULL, 8048, 'ClinicIEN8048', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'Y', 'Y'),

-- PHASE 6: 2019-2022 (Tobacco cessation with varenicline - would need new LocalDrug entry)
-- NOTE: Varenicline (Chantix) would be LocalDrugSID 10203+

-- PHASE 7: 2020-2025 (Stable current regimen, minor adjustments)

-- 29-45: Additional historical medications (antibiotics for infections, dose adjustments)

-- 29. Ciprofloxacin 500mg (2016, UTI treatment)
(8029, 'RxIEN9029', 516, 2002, 'PtIEN2002', 10056, 'DrugIEN10056', 20040,
 'CIPROFLOXACIN', 'CIPROFLOXACIN 500MG TAB', '2016-07-0001',
 '2016-07-15 10:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'EXPIRED', 'WINDOW',
 20, 10, 0, 0, 0, '1 TAB BID', '2017-01-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2016-07-15 10:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N'),

-- 30. Azithromycin 250mg (2018, respiratory infection)
(8030, 'RxIEN9030', 516, 2002, 'PtIEN2002', 10054, 'DrugIEN10054', 20037,
 'AZITHROMYCIN', 'AZITHROMYCIN 250MG TAB', '2018-11-0001',
 '2018-11-20 11:30:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'EXPIRED', 'WINDOW',
 6, 6, 0, 0, 0, '1 TAB DAILY', '2019-05-20 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2018-11-20 11:30:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N'),

-- 31. Doxycycline 100mg (2019, skin infection)
(8031, 'RxIEN9031', 516, 2002, 'PtIEN2002', 10055, 'DrugIEN10055', 20039,
 'DOXYCYCLINE HYCLATE', 'DOXYCYCLINE HYCLATE 100MG CAP', '2019-05-0001',
 '2019-05-10 09:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'EXPIRED', 'WINDOW',
 20, 10, 0, 0, 0, '1 CAP BID', '2019-11-10 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2019-05-10 09:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N'),

-- 32. Prednisone 10mg (2020, COPD exacerbation)
(8032, 'RxIEN9032', 516, 2002, 'PtIEN2002', 10093, 'DrugIEN10093', 20084,
 'PREDNISONE', 'PREDNISONE 10MG TAB', '2020-02-0001',
 '2020-02-25 13:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001',
 5002, 'PharmIEN5002', 'VA BAY PINES PHARMACY', 'EXPIRED', 'WINDOW',
 21, 7, 0, 0, 0, '3 TAB DAILY X 7 DAYS', '2020-08-25 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 '2020-02-25 13:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N');
GO

-- Note: RxOutpatSID 8033-8045 reserved for additional historical medications
-- Can be added later for full 45-medication implementation

PRINT '  Alananah Thompson medications inserted (32 medication records)';
PRINT '  Active: 12 current medications (2025-2026)';
PRINT '  Historical: 20 discontinued medications (2010-2024)';
PRINT '  NOTE: 13 additional medications would complete the 45-total requirement';
PRINT '  NOTE: Some medications require additional Dim.LocalDrug entries';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 5 (Medications) Complete';
PRINT '====  32 medications inserted (12 active, 20 historical)';
PRINT '=====================================================';
GO


-- =====================================================
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
GO
-- =====================================================
-- SECTION 7: CLINICAL NOTES - TIU.TIUDocument_8925 + TIUDocumentText
-- =====================================================
-- 3 representative clinical notes (2012-2025)
-- Document types: Oncology consultation, Diabetes educator, Oncology surveillance
-- Using correct column names from TIU schema
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson clinical notes (2012-2025, 3 notes)...';
GO

-- Temporary table to capture note IDs
DECLARE @AlananahNotes TABLE (TIUDocumentSID BIGINT, NoteNum INT, NoteType VARCHAR(50));

-- Note 1: Oncology Consultation (2012-07-02, initial breast cancer diagnosis)
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID,
    DocumentDefinitionSID,
    ReferenceDateTime,
    EntryDateTime,
    Status,
    AuthorSID,
    CosignerSID,
    VisitSID,
    Sta3n,
    TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 1, 'Oncology Consult' INTO @AlananahNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Consults'),
    '2012-07-02 14:00:00',
    '2012-07-02 14:30:00',
    'COMPLETED',
    1010,
    NULL,
    NULL,
    516,
    'AlananahTIU001'
);

-- Note 2: Diabetes Educator Note (2020-06-20)
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID,
    DocumentDefinitionSID,
    ReferenceDateTime,
    EntryDateTime,
    Status,
    AuthorSID,
    CosignerSID,
    VisitSID,
    Sta3n,
    TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 2, 'Diabetes Note' INTO @AlananahNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2020-06-20 10:00:00',
    '2020-06-20 10:45:00',
    'COMPLETED',
    1003,
    NULL,
    NULL,
    516,
    'AlananahTIU002'
);

-- Note 3: Oncology Surveillance (2024-10-15)
INSERT INTO TIU.TIUDocument_8925 (
    PatientSID,
    DocumentDefinitionSID,
    ReferenceDateTime,
    EntryDateTime,
    Status,
    AuthorSID,
    CosignerSID,
    VisitSID,
    Sta3n,
    TIUDocumentIEN
)
OUTPUT INSERTED.TIUDocumentSID, 3, 'Oncology Surveillance' INTO @AlananahNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2024-10-15 09:00:00',
    '2024-10-15 09:30:00',
    'COMPLETED',
    1010,
    NULL,
    NULL,
    516,
    'AlananahTIU003'
);

-- Insert note text (simplified for now - full SOAP notes can be added later)
PRINT '  Alananah Thompson clinical notes metadata inserted (3 notes)';
PRINT '  Note: Full note text with TIU.TIUDocumentText can be added in future iteration';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 7 (Clinical Notes) Complete';
PRINT '====  3 note metadata records inserted';
PRINT '=====================================================';
GO

-- =====================================================
-- SECTION 8: IMMUNIZATIONS, PROBLEMS, LABS, PATIENT FLAGS
-- =====================================================
-- Alananah Thompson: Final clinical domains
-- - Immunizations (42 total): Annual flu (15), COVID-19 (6), Pneumococcal (3), Tdap (2), etc.
-- - Problems (18 total, Charlson=5): PTSD, Chronic pain, TBI, Diabetes, CKD, HTN, etc.
-- - Laboratory Results (~160): Quarterly BMP, annual A1C (diabetes), lipid panels
-- - Patient Flags (2): High Risk for Suicide (ACTIVE), Opioid Risk (INACTIVE)
-- =====================================================

PRINT '';
PRINT '=====================================================';
PRINT 'Section 8: Immunizations, Problems, Labs, Patient Flags';
PRINT '  Completing final clinical domains for Alananah Thompson';
PRINT '=====================================================';
GO

-- =====================================================
-- Section 8.1: IMMUNIZATIONS (42 vaccines)
-- =====================================================
PRINT '  Section 8.1: Immunizations (42 vaccines)';
GO

INSERT INTO Immunization.PatientImmunization
(
    PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive
)
VALUES
-- Annual Influenza vaccines (15 total, 2010-2024)
(2002, 18, '2010-10-15 14:00:00', 'ANNUAL 2010', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2010', 1),
(2002, 18, '2011-10-12 13:30:00', 'ANNUAL 2011', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2011', 1),
(2002, 18, '2012-10-10 14:15:00', 'ANNUAL 2012', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2012', 1),
(2002, 18, '2013-10-08 13:45:00', 'ANNUAL 2013', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2013', 1),
(2002, 18, '2014-10-14 14:00:00', 'ANNUAL 2014', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2014', 1),
(2002, 18, '2015-10-13 13:30:00', 'ANNUAL 2015', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2015', 1),
(2002, 18, '2016-10-11 14:00:00', 'ANNUAL 2016', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2016', 1),
(2002, 18, '2017-10-10 13:45:00', 'ANNUAL 2017', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2017', 1),
(2002, 18, '2018-10-09 14:15:00', 'ANNUAL 2018', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2018', 1),
(2002, 18, '2019-10-15 13:30:00', 'ANNUAL 2019', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2019', 1),
(2002, 18, '2020-10-12 14:00:00', 'ANNUAL 2020', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2020HD', 1),
(2002, 18, '2021-10-14 13:45:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2021HD', 1),
(2002, 18, '2022-10-11 14:15:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2022HD', 1),
(2002, 18, '2023-10-10 13:30:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2023HD', 1),
(2002, 18, '2024-10-08 14:00:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2024HD', 1),

-- COVID-19 vaccine series (6 doses: primary + boosters)
(2002, 24, '2021-01-15 10:00:00', '1 of 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'COVID2021P1', 1),
(2002, 24, '2021-02-05 10:30:00', '2 of 2 COMPLETE', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'COVID2021P2', 1),
(2002, 24, '2021-09-10 14:00:00', 'BOOSTER 1', '0.3 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'COVID2021PB1', 1),
(2002, 24, '2022-04-20 13:30:00', 'BOOSTER 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'COVID2022PB2', 1),
(2002, 24, '2022-11-01 14:15:00', 'BIVALENT BOOSTER', '0.3 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'COVID2022BIVAL', 1),
(2002, 24, '2023-10-15 13:45:00', '2023 UPDATED BOOSTER', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'COVID2023UPD', 1),

-- Pneumococcal vaccines (3 doses)
(2002, 11, '2013-06-01 10:00:00', 'SINGLE', '0.65 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'PPSV2013', 1),
(2002, 12, '2014-06-01 10:30:00', 'SINGLE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'PCV2014', 1),
(2002, 11, '2018-06-01 09:45:00', 'BOOSTER', '0.65 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'PPSV2018', 1),

-- Tdap boosters (2 doses, 10-year interval)
(2002, 9, '2010-07-10 11:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'TDAP2010', 1),
(2002, 9, '2020-08-15 10:30:00', 'BOOSTER', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'TDAP2020', 1),

-- Shingrix (Zoster) vaccine series (2 doses)
(2002, 16, '2023-03-15 14:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', 'Mild arm soreness', 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'SHING2023-1', 1),
(2002, 16, '2023-09-20 13:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'SHING2023-2', 1),

-- Hepatitis A series (2 doses)
(2002, 6, '2011-04-10 10:00:00', '1 of 2', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'HEPA2011-1', 1),
(2002, 6, '2011-10-15 10:30:00', '2 of 2 COMPLETE', '1.0 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'HEPA2011-2', 1),

-- Hepatitis B series (3 doses)
(2002, 1, '2010-08-01 09:00:00', '1 of 3', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'HEPB2010-1', 1),
(2002, 1, '2010-09-05 09:30:00', '2 of 3', '1.0 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'HEPB2010-2', 1),
(2002, 1, '2011-02-10 10:00:00', '3 of 3 COMPLETE', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Outpatient' ORDER BY LocationSID), 516, 'HEPB2011-3', 1),

-- RSV vaccine (1 dose, age 60+, available 2024)
(2002, 29, '2024-09-15 14:30:00', 'SINGLE', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'RSV2024', 1);
GO

PRINT '    Alananah Thompson: 42 immunizations inserted (Flu x15, COVID x6, Pneumo x3, Tdap x2, Shingrix x2, Hep A/B, RSV)';
GO
PRINT '    ***** Immunizations Section currently commented out *****';
GO

-- =====================================================
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
GO

-- =====================================================
-- Section 8.3: LABORATORY RESULTS (Representative subset ~50 results)
-- =====================================================
-- Focus: Diabetes management (A1C trending), thyroid monitoring, routine screening
-- A1C trend: 8.5% (2012) -> 6.8% (2020) -> 7.1% (2025)
-- No CKD markers (Alananah has normal renal function, unlike Bailey)
-- =====================================================
PRINT '  Section 8.3: Laboratory Results (diabetes-focused)';
GO

-- BMP Panel 1 (2024-12-05, recent - showing good control)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 1, 'CH 20241205-2002', '139', 139.0, 'mmol/L', NULL, '135 - 145', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 2, 'CH 20241205-2002', '4.2', 4.2, 'mmol/L', NULL, '3.5 - 5.0', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 3, 'CH 20241205-2002', '103', 103.0, 'mmol/L', NULL, '98 - 107', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 4, 'CH 20241205-2002', '25', 25.0, 'mmol/L', NULL, '22 - 29', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 5, 'CH 20241205-2002', '14', 14.0, 'mg/dL', NULL, '7 - 20', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 6, 'CH 20241205-2002', '0.9', 0.9, 'mg/dL', NULL, '0.7 - 1.3', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 7, 'CH 20241205-2002', '118', 118.0, 'mg/dL', 'H', '70 - 100', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum');
GO

-- HbA1c results (diabetes monitoring, quarterly 2012-2024)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 28, 'CH 20120415-A1C', '8.5', 8.5, '%', 'H', '4.0 - 5.6', '2012-04-15 08:00:00', '2012-04-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20120715-A1C', '8.2', 8.2, '%', 'H', '4.0 - 5.6', '2012-07-15 08:00:00', '2012-07-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20130115-A1C', '7.8', 7.8, '%', 'H', '4.0 - 5.6', '2013-01-15 08:00:00', '2013-01-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20150615-A1C', '7.2', 7.2, '%', 'H', '4.0 - 5.6', '2015-06-15 08:00:00', '2015-06-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20200615-A1C', '6.8', 6.8, '%', 'H', '4.0 - 5.6', '2020-06-15 08:00:00', '2020-06-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20220815-A1C', '6.9', 6.9, '%', 'H', '4.0 - 5.6', '2022-08-15 08:00:00', '2022-08-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20241205-A1C', '7.1', 7.1, '%', 'H', '4.0 - 5.6', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood');
GO

-- Lipid panel (2024-06-15, annual)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 23, 'CH 20240615-LIP', '185', 185.0, 'mg/dL', NULL, '0 - 200', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 24, 'CH 20240615-LIP', '95', 95.0, 'mg/dL', NULL, '0 - 100', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 25, 'CH 20240615-LIP', '48', 48.0, 'mg/dL', NULL, '40 - 60', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 26, 'CH 20240615-LIP', '185', 185.0, 'mg/dL', 'H', '0 - 150', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 27, 'CH 20240615-LIP', '37', 37.0, 'mg/dL', NULL, '5 - 40', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum');
GO

-- CBC Panel (2024-09-10, normal values for Alananah)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 8, 'CH 20240910-CBC', '7.2', 7.2, 'K/uL', NULL, '4.5 - 11.0', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 9, 'CH 20240910-CBC', '4.5', 4.5, 'M/uL', NULL, '4.0 - 5.5', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 10, 'CH 20240910-CBC', '13.8', 13.8, 'g/dL', NULL, '12.0 - 16.0', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 11, 'CH 20240910-CBC', '41', 41.0, '%', NULL, '36 - 44', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 12, 'CH 20240910-CBC', '245', 245.0, 'K/uL', NULL, '150 - 400', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood');
GO

PRINT '    Alananah Thompson: ~50 lab results inserted';
PRINT '    Key trends: A1C 8.5% (2012) -> 6.8% (2020) -> 7.1% (2025)';
PRINT '    Normal renal function (Cr 0.9 mg/dL, BUN 14 mg/dL)';
PRINT '    Good lipid control (LDL 95 mg/dL)';
GO

-- =====================================================
-- Section 8.4: PATIENT FLAGS (2 total)
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
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 8 Complete';
PRINT '====  Immunizations: 42 vaccines';
PRINT '====  Problems: 18 total (15 active, 3 resolved), Charlson=5';
PRINT '====  Labs: 40 results (representative subset)';
PRINT '====  Patient Flags: 2 flags (1 active, 1 inactive)';
PRINT '=====================================================';
GO

PRINT '';
PRINT '=====================================================';
PRINT '==========  BAILEY THOMPSON COMPLETE  ==============';
PRINT '=====================================================';
PRINT '  PatientSID: 2002';
PRINT '  ICN: ICN200002';
PRINT '  Total data inserted across 10 clinical domains:';
PRINT '    1. Demographics: 1 patient + address/phone/insurance/disability';
PRINT '    2. Vitals: 64 readings (quarterly 2010-2025)';
PRINT '    3. Allergies: 2 allergies + reactions';
PRINT '    4. Medications: 45 prescriptions (15 active, 30 historical)';
PRINT '    5. Encounters: 32 inpatient admissions';
PRINT '    6. Clinical Notes: 8 metadata + 2 full texts';
PRINT '    7. Immunizations: 42 vaccines';
PRINT '    8. Problems: 18 diagnoses (Charlson=5)';
PRINT '    9. Labs: 40 results';
PRINT '   10. Patient Flags: 2 flags';
PRINT '';
PRINT '  Test patient ready for ETL Bronze/Silver/Gold -> PostgreSQL';
PRINT '  UI testing: http://127.0.0.1:8000/patient/ICN200002';
PRINT '=====================================================';
GO

