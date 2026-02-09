-- =====================================================
-- Thompson Twins Test Patient Data
-- Patient: Alananah Marie Thompson (Female)
-- ICN: ICN200002
-- Database: CDWWork (Bay Pines VA, 2010-2025)
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
-- Alananah Thompson: Male veteran, age 62 (DOB 1963-04-15)
-- Served 1990-2010: Gulf War (1990-1991), Iraq (2003-2010)
-- Retired to St. Petersburg, FL (Bay Pines VAMC, Sta3n 516)
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
-- Weight trend: 185 lbs (2010) → 245 lbs (2019 peak) → 220 lbs (2025 stable)
-- BP trend: 125/78 (2010) → 145/92 (2015 HTN) → 135/85 (2025 controlled)
-- Pain: Consistently 4-8/10 (chronic lumbar radiculopathy)
-- VitalSignSID range: 9001-9240 (allocated for Bailey)
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
    (9001, 2002, 5, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '70', 70, NULL, NULL, 177.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9002, 2002, 6, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '185', 185, NULL, NULL, 84.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9003, 2002, 1, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '125/78', NULL, 125, 78, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9004, 2002, 3, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '72', 72, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9005, 2002, 2, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '98.4', 98.4, NULL, NULL, 36.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9006, 2002, 10, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '26.6', 26.6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2010-09-20: Follow-up
    (9007, 2002, 6, '2010-09-20 10:15:00', '2010-09-20 10:18:00', '187', 187, NULL, NULL, 84.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9008, 2002, 1, '2010-09-20 10:15:00', '2010-09-20 10:18:00', '128/80', NULL, 128, 80, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9009, 2002, 3, '2010-09-20 10:15:00', '2010-09-20 10:18:00', '74', 74, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2010-12-15: End of year
    (9010, 2002, 6, '2010-12-15 14:20:00', '2010-12-15 14:23:00', '189', 189, NULL, NULL, 85.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9011, 2002, 1, '2010-12-15 14:20:00', '2010-12-15 14:23:00', '130/82', NULL, 130, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9012, 2002, 7, '2010-12-15 14:20:00', '2010-12-15 14:23:00', '2', 2, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2011-03-22: Post-deployment stress emerging
    (9013, 2002, 6, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '195', 195, NULL, NULL, 88.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9014, 2002, 1, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '135/85', NULL, 135, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9015, 2002, 3, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '78', 78, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9016, 2002, 7, '2011-03-22 11:00:00', '2011-03-22 11:05:00', '4', 4, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2011-06-18: Back pain worsening
    (9017, 2002, 6, '2011-06-18 13:45:00', '2011-06-18 13:48:00', '198', 198, NULL, NULL, 89.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9018, 2002, 1, '2011-06-18 13:45:00', '2011-06-18 13:48:00', '138/88', NULL, 138, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9019, 2002, 7, '2011-06-18 13:45:00', '2011-06-18 13:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2011-09-12
    (9020, 2002, 6, '2011-09-12 09:20:00', '2011-09-12 09:23:00', '202', 202, NULL, NULL, 91.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9021, 2002, 1, '2011-09-12 09:20:00', '2011-09-12 09:23:00', '140/90', NULL, 140, 90, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9022, 2002, 7, '2011-09-12 09:20:00', '2011-09-12 09:23:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2011-12-08
    (9023, 2002, 6, '2011-12-08 15:30:00', '2011-12-08 15:33:00', '205', 205, NULL, NULL, 93.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9024, 2002, 1, '2011-12-08 15:30:00', '2011-12-08 15:33:00', '142/92', NULL, 142, 92, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9025, 2002, 7, '2011-12-08 15:30:00', '2011-12-08 15:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2012-03-15: Weight gain continuing
    (9026, 2002, 6, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '210', 210, NULL, NULL, 95.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9027, 2002, 1, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '145/92', NULL, 145, 92, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9028, 2002, 3, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '82', 82, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9029, 2002, 7, '2012-03-15 10:00:00', '2012-03-15 10:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2012-06-20
    (9030, 2002, 6, '2012-06-20 14:15:00', '2012-06-20 14:18:00', '215', 215, NULL, NULL, 97.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9031, 2002, 1, '2012-06-20 14:15:00', '2012-06-20 14:18:00', '148/94', NULL, 148, 94, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9032, 2002, 7, '2012-06-20 14:15:00', '2012-06-20 14:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2012-09-25
    (9033, 2002, 6, '2012-09-25 11:30:00', '2012-09-25 11:33:00', '218', 218, NULL, NULL, 98.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9034, 2002, 1, '2012-09-25 11:30:00', '2012-09-25 11:33:00', '146/93', NULL, 146, 93, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9035, 2002, 7, '2012-09-25 11:30:00', '2012-09-25 11:33:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2012-12-10: HTN diagnosed, started on lisinopril
    (9036, 2002, 6, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9037, 2002, 1, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '150/95', NULL, 150, 95, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9038, 2002, 3, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '84', 84, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9039, 2002, 7, '2012-12-10 09:45:00', '2012-12-10 09:48:00', '8', 8, NULL, NULL, NULL,
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
    (9040, 2002, 6, '2013-03-18 13:00:00', '2013-03-18 13:03:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9041, 2002, 1, '2013-03-18 13:00:00', '2013-03-18 13:03:00', '142/88', NULL, 142, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9042, 2002, 7, '2013-03-18 13:00:00', '2013-03-18 13:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2013-06-22
    (9043, 2002, 6, '2013-06-22 10:30:00', '2013-06-22 10:33:00', '225', 225, NULL, NULL, 102.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9044, 2002, 1, '2013-06-22 10:30:00', '2013-06-22 10:33:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9045, 2002, 7, '2013-06-22 10:30:00', '2013-06-22 10:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2013-09-15
    (9046, 2002, 6, '2013-09-15 14:45:00', '2013-09-15 14:48:00', '228', 228, NULL, NULL, 103.4,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9047, 2002, 1, '2013-09-15 14:45:00', '2013-09-15 14:48:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9048, 2002, 7, '2013-09-15 14:45:00', '2013-09-15 14:48:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2013-12-08
    (9049, 2002, 6, '2013-12-08 11:15:00', '2013-12-08 11:18:00', '230', 230, NULL, NULL, 104.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9050, 2002, 1, '2013-12-08 11:15:00', '2013-12-08 11:18:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9051, 2002, 7, '2013-12-08 11:15:00', '2013-12-08 11:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2014-03-20
    (9052, 2002, 6, '2014-03-20 09:00:00', '2014-03-20 09:03:00', '235', 235, NULL, NULL, 106.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9053, 2002, 1, '2014-03-20 09:00:00', '2014-03-20 09:03:00', '140/88', NULL, 140, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9054, 2002, 7, '2014-03-20 09:00:00', '2014-03-20 09:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2014-06-18: Sleep apnea diagnosed
    (9055, 2002, 6, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '238', 238, NULL, NULL, 108.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9056, 2002, 1, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '142/90', NULL, 142, 90, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9057, 2002, 8, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '92', 92, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9058, 2002, 7, '2014-06-18 13:30:00', '2014-06-18 13:33:00', '8', 8, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2014-09-12
    (9059, 2002, 6, '2014-09-12 10:45:00', '2014-09-12 10:48:00', '240', 240, NULL, NULL, 108.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9060, 2002, 1, '2014-09-12 10:45:00', '2014-09-12 10:48:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9061, 2002, 7, '2014-09-12 10:45:00', '2014-09-12 10:48:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2014-12-15: Peak weight approaching
    (9062, 2002, 6, '2014-12-15 14:00:00', '2014-12-15 14:03:00', '242', 242, NULL, NULL, 109.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9063, 2002, 1, '2014-12-15 14:00:00', '2014-12-15 14:03:00', '142/88', NULL, 142, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9064, 2002, 7, '2014-12-15 14:00:00', '2014-12-15 14:03:00', '8', 8, NULL, NULL, NULL,
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
    (9065, 2002, 6, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '245', 245, NULL, NULL, 111.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9066, 2002, 1, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '145/92', NULL, 145, 92, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9067, 2002, 9, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '148', 148, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9068, 2002, 7, '2015-03-22 11:30:00', '2015-03-22 11:33:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2015-06-15
    (9069, 2002, 6, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '245', 245, NULL, NULL, 111.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9070, 2002, 1, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '143/90', NULL, 143, 90, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9071, 2002, 9, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '132', 132, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9072, 2002, 7, '2015-06-15 09:15:00', '2015-06-15 09:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2015-09-20
    (9073, 2002, 6, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '243', 243, NULL, NULL, 110.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9074, 2002, 1, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '140/88', NULL, 140, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9075, 2002, 9, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '125', 125, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9076, 2002, 7, '2015-09-20 13:00:00', '2015-09-20 13:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2015-12-10
    (9077, 2002, 6, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '240', 240, NULL, NULL, 108.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9078, 2002, 1, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9079, 2002, 9, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9080, 2002, 7, '2015-12-10 10:30:00', '2015-12-10 10:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2016-03-18: Post suicide attempt (March 2016)
    (9081, 2002, 6, '2016-03-18 14:45:00', '2016-03-18 14:48:00', '238', 238, NULL, NULL, 108.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
        1003, 'N', 'N', 516),
    (9082, 2002, 1, '2016-03-18 14:45:00', '2016-03-18 14:48:00', '135/82', NULL, 135, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
        1003, 'N', 'N', 516),
    (9083, 2002, 7, '2016-03-18 14:45:00', '2016-03-18 14:48:00', '8', 8, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
        1003, 'N', 'N', 516),

    -- 2016-06-20
    (9084, 2002, 6, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '235', 235, NULL, NULL, 106.6,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9085, 2002, 1, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9086, 2002, 9, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '115', 115, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9087, 2002, 7, '2016-06-20 11:00:00', '2016-06-20 11:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2016-09-15
    (9088, 2002, 6, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '232', 232, NULL, NULL, 105.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9089, 2002, 1, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9090, 2002, 9, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9091, 2002, 7, '2016-09-15 09:30:00', '2016-09-15 09:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2016-12-12
    (9092, 2002, 6, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '230', 230, NULL, NULL, 104.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9093, 2002, 1, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9094, 2002, 9, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9095, 2002, 7, '2016-12-12 13:15:00', '2016-12-12 13:18:00', '7', 7, NULL, NULL, NULL,
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
    (9096, 2002, 6, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '228', 228, NULL, NULL, 103.4,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9097, 2002, 1, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '140/88', NULL, 140, 88, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9098, 2002, 9, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '125', 125, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9099, 2002, 7, '2017-03-20 10:00:00', '2017-03-20 10:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2017-06-18
    (9100, 2002, 6, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '225', 225, NULL, NULL, 102.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9101, 2002, 1, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9102, 2002, 9, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9103, 2002, 7, '2017-06-18 14:30:00', '2017-06-18 14:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2017-09-12
    (9104, 2002, 6, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9105, 2002, 1, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9106, 2002, 9, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9107, 2002, 7, '2017-09-12 11:45:00', '2017-09-12 11:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2017-12-08: Opioid taper beginning (2018)
    (9108, 2002, 6, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9109, 2002, 1, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9110, 2002, 9, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9111, 2002, 7, '2017-12-08 09:00:00', '2017-12-08 09:03:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2018-03-15: Opioid taper in progress
    (9112, 2002, 6, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '218', 218, NULL, NULL, 98.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9113, 2002, 1, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '140/86', NULL, 140, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9114, 2002, 9, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9115, 2002, 7, '2018-03-15 13:20:00', '2018-03-15 13:23:00', '7', 7, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2018-06-20: Opioid taper complete
    (9116, 2002, 6, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '215', 215, NULL, NULL, 97.5,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9117, 2002, 1, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9118, 2002, 9, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9119, 2002, 7, '2018-06-20 10:30:00', '2018-06-20 10:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2018-09-15
    (9120, 2002, 6, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '212', 212, NULL, NULL, 96.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9121, 2002, 1, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9122, 2002, 9, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '115', 115, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9123, 2002, 7, '2018-09-15 14:45:00', '2018-09-15 14:48:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2018-12-10
    (9124, 2002, 6, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '210', 210, NULL, NULL, 95.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9125, 2002, 1, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9126, 2002, 9, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9127, 2002, 7, '2018-12-10 11:00:00', '2018-12-10 11:03:00', '6', 6, NULL, NULL, NULL,
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
    (9128, 2002, 6, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '208', 208, NULL, NULL, 94.3,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9129, 2002, 1, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9130, 2002, 9, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9131, 2002, 7, '2019-03-18 09:30:00', '2019-03-18 09:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2019-06-15: CKD Stage 3a diagnosed
    (9132, 2002, 6, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '205', 205, NULL, NULL, 93.0,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9133, 2002, 1, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '138/84', NULL, 138, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9134, 2002, 9, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9135, 2002, 7, '2019-06-15 13:45:00', '2019-06-15 13:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2019-09-20
    (9136, 2002, 6, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '203', 203, NULL, NULL, 92.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9137, 2002, 1, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '135/82', NULL, 135, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9138, 2002, 9, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9139, 2002, 7, '2019-09-20 10:00:00', '2019-09-20 10:03:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2019-12-12
    (9140, 2002, 6, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '200', 200, NULL, NULL, 90.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9141, 2002, 1, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '136/83', NULL, 136, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9142, 2002, 9, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9143, 2002, 7, '2019-12-12 14:20:00', '2019-12-12 14:23:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2020-03-16: Alcohol use disorder remission (2020)
    (9144, 2002, 6, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '225', 225, NULL, NULL, 102.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9145, 2002, 1, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9146, 2002, 9, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '115', 115, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9147, 2002, 7, '2020-03-16 11:15:00', '2020-03-16 11:18:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2020-06-18
    (9148, 2002, 6, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '223', 223, NULL, NULL, 101.2,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9149, 2002, 1, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9150, 2002, 9, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9151, 2002, 7, '2020-06-18 09:00:00', '2020-06-18 09:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2020-09-15
    (9152, 2002, 6, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9153, 2002, 1, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9154, 2002, 9, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9155, 2002, 7, '2020-09-15 13:30:00', '2020-09-15 13:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2020-12-10
    (9156, 2002, 6, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '218', 218, NULL, NULL, 98.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9157, 2002, 1, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '135/83', NULL, 135, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9158, 2002, 9, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9159, 2002, 7, '2020-12-10 10:45:00', '2020-12-10 10:48:00', '6', 6, NULL, NULL, NULL,
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
    (9160, 2002, 6, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9161, 2002, 1, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9162, 2002, 9, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9163, 2002, 7, '2021-03-20 14:00:00', '2021-03-20 14:03:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2021-06-18
    (9164, 2002, 6, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9165, 2002, 1, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9166, 2002, 9, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9167, 2002, 7, '2021-06-18 11:30:00', '2021-06-18 11:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2021-09-15
    (9168, 2002, 6, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9169, 2002, 1, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9170, 2002, 9, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9171, 2002, 7, '2021-09-15 09:45:00', '2021-09-15 09:48:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2021-12-12
    (9172, 2002, 6, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '218', 218, NULL, NULL, 98.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9173, 2002, 1, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9174, 2002, 9, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9175, 2002, 7, '2021-12-12 13:00:00', '2021-12-12 13:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2022-03-18
    (9176, 2002, 6, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9177, 2002, 1, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9178, 2002, 9, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9179, 2002, 7, '2022-03-18 10:15:00', '2022-03-18 10:18:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2022-06-20
    (9180, 2002, 6, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9181, 2002, 1, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '135/83', NULL, 135, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9182, 2002, 9, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9183, 2002, 7, '2022-06-20 14:30:00', '2022-06-20 14:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2022-09-15
    (9184, 2002, 6, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9185, 2002, 1, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9186, 2002, 9, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9187, 2002, 7, '2022-09-15 11:45:00', '2022-09-15 11:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2022-12-10
    (9188, 2002, 6, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '218', 218, NULL, NULL, 98.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9189, 2002, 1, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9190, 2002, 9, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9191, 2002, 7, '2022-12-10 09:00:00', '2022-12-10 09:03:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2023-03-20
    (9192, 2002, 6, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9193, 2002, 1, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9194, 2002, 9, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9195, 2002, 7, '2023-03-20 13:20:00', '2023-03-20 13:23:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2023-06-18
    (9196, 2002, 6, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9197, 2002, 1, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9198, 2002, 9, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9199, 2002, 7, '2023-06-18 10:30:00', '2023-06-18 10:33:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2023-09-15
    (9200, 2002, 6, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9201, 2002, 1, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9202, 2002, 9, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9203, 2002, 7, '2023-09-15 14:45:00', '2023-09-15 14:48:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2023-12-10
    (9204, 2002, 6, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '218', 218, NULL, NULL, 98.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9205, 2002, 1, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '135/83', NULL, 135, 83, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9206, 2002, 9, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9207, 2002, 7, '2023-12-10 11:00:00', '2023-12-10 11:03:00', '5', 5, NULL, NULL, NULL,
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
    (9208, 2002, 6, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9209, 2002, 1, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '136/84', NULL, 136, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9210, 2002, 9, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9211, 2002, 7, '2024-03-18 09:30:00', '2024-03-18 09:33:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2024-06-20 (Bay Pines FL)
    (9212, 2002, 6, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9213, 2002, 1, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '138/86', NULL, 138, 86, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9214, 2002, 9, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),
    (9215, 2002, 7, '2024-06-20 13:45:00', '2024-06-20 13:48:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1003, 'N', 'N', 516),

    -- 2024-09-15 (Bay Pines FL - last visit before relocation)
    (9216, 2002, 6, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9217, 2002, 1, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9218, 2002, 9, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '122', 122, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9219, 2002, 7, '2024-09-15 10:00:00', '2024-09-15 10:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),

    -- 2024-12-10 (Bay Pines FL - final visit before move)
    (9220, 2002, 6, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '218', 218, NULL, NULL, 98.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9221, 2002, 1, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '136/82', NULL, 136, 82, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9222, 2002, 9, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),
    (9223, 2002, 7, '2024-12-10 14:20:00', '2024-12-10 14:23:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1002, 'N', 'N', 516),

    -- 2025-02-15 (Walla Walla WA - first visit after relocation)
    (9224, 2002, 6, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '220', 220, NULL, NULL, 99.8,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),
    (9225, 2002, 1, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '138/85', NULL, 138, 85, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),
    (9226, 2002, 9, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '118', 118, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),
    (9227, 2002, 7, '2025-02-15 11:00:00', '2025-02-15 11:03:00', '6', 6, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1001, 'N', 'N', 687),

    -- 2025-05-20 (Walla Walla WA - current)
    (9228, 2002, 6, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '222', 222, NULL, NULL, 100.7,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687),
    (9229, 2002, 1, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '135/84', NULL, 135, 84, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687),
    (9230, 2002, 9, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '120', 120, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687),
    (9231, 2002, 7, '2025-05-20 09:15:00', '2025-05-20 09:18:00', '5', 5, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 687 AND LocationType = 'CLINIC' ORDER BY LocationSID),
        1002, 'N', 'N', 687);
GO

SET IDENTITY_INSERT Vital.VitalSign OFF;
GO

PRINT '  Alananah Thompson vitals inserted (231 readings, 2010-2025)';
PRINT '  Weight trend: 185 lbs (2010) → 245 lbs (2015 peak) → 220 lbs (2025 stable)';
PRINT '  BP trend: 125/78 (2010 baseline) → 150/95 (2012 HTN dx) → 135/84 (2025 controlled)';
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
-- PatientAllergySID range: 9001-9002 (allocated for Bailey)
-- PatientAllergyReactionSID range: 9001-9003 (allocated for Bailey)
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
    (9001, 2002, 1, 2, 'PENICILLIN',
        '2010-06-16 10:00:00', NULL, 516,
        'Patient reports childhood rash with penicillin. No anaphylaxis. Never re-exposed. Avoid penicillins, use alternative antibiotics (fluoroquinolones, macrolides acceptable).',
        'HISTORICAL', 1, 'UNVERIFIED', 516),

    -- Allergy 2: MORPHINE (severe nausea/vomiting, confirmed 2016)
    (9002, 2002, 7, 3, 'MORPHINE SULFATE',
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
    -- Allergy 9001: PENICILLIN - Rash
    (9001, 9001, 2),   -- RASH

    -- Allergy 9002: MORPHINE - Nausea, Vomiting
    (9002, 9002, 20),  -- NAUSEA
    (9003, 9002, 21);  -- VOMITING
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
-- 32 inpatient admissions total (2010-2025)
-- CDWWork (Bay Pines FL, Sta3n 516): 30 encounters
-- CDWWork2 (Walla Walla WA, Sta3n 687): 2 encounters (would be in Thompson-Bailey-CDWWork2.sql)
--
-- Key encounters (from requirements):
-- 1. 2011-02: Initial PTSD evaluation (7 days)
-- 2. 2012-08: Uncontrolled hypertension (5 days)
-- 3. 2013-11: Major depressive episode (3 days)
-- 4. 2014-03: Lumbar epidural steroid injections (5 days)
-- 5. 2015-03: Diabetes diagnosis (4 days)
-- 6. 2016-03: SUICIDE ATTEMPT (psychiatric admission, 7 days) **KEY EVENT**
-- 7. 2016-06: Post-attempt follow-up (3 days)
-- 8. 2017-08: Chronic pain exacerbation (4 days)
-- 9. 2018-06: Opioid taper final phase (5 days)
-- 10. 2019-10: Alcohol treatment program (7 days)
-- 11. 2020-02: Spinal cord stimulator trial (4 days)
-- 12. 2021-05: Acute kidney injury (4 days)
-- 13. 2022-11: Diabetic ketoacidosis (4 days)
-- 14. 2023-03: Atrial fibrillation (3 days)
-- 15-32: Additional encounters (infections, procedures, chronic disease management)
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson encounters (2010-2025, 32 admissions)...';
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Alananah Thompson Inpatient Encounters (Sta3n 516 Bay Pines FL)
INSERT INTO Inpat.Inpatient
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES

-- 1. 2011-02-10: Initial PTSD evaluation (7-day psychiatry admission)
(2002, '2011-02-10 14:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1003, 'F43.10',
 '2011-02-17 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'F43.10', 'POST-TRAUMATIC STRESS DISORDER, UNSPECIFIED',
 'ROUTINE DISCHARGE TO HOME', 7, 'Discharged', 516),

-- 2. 2012-08-15: Uncontrolled hypertension (5-day medicine admission)
(2002, '2012-08-15 08:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'I10',
 '2012-08-20 11:30:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'I10', 'ESSENTIAL (PRIMARY) HYPERTENSION',
 'ROUTINE DISCHARGE TO HOME', 5, 'Discharged', 516),

-- 3. 2013-11-05: Major depressive episode, SI (3-day psychiatry)
(2002, '2013-11-05 22:15:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1003, 'F33.2',
 '2013-11-08 15:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'F33.2', 'MAJOR DEPRESSIVE DISORDER, RECURRENT SEVERE WITHOUT PSYCHOTIC FEATURES',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 4. 2014-03-20: Lumbar epidural steroid injections (5-day pain management)
(2002, '2014-03-20 07:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 1002, 'M54.5',
 '2014-03-25 14:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 'M54.5', 'LOW BACK PAIN',
 'ROUTINE DISCHARGE TO HOME', 5, 'Discharged', 516),

-- 5. 2015-03-25: Diabetes diagnosis workup (4-day endocrine admission)
(2002, '2015-03-25 10:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'E11.9',
 '2015-03-29 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'E11.9', 'TYPE 2 DIABETES MELLITUS WITHOUT COMPLICATIONS',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 6. 2016-03-18: SUICIDE ATTEMPT - opioid overdose (7-day psychiatry) **KEY EVENT**
(2002, '2016-03-18 03:45:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1003, 'T40.2X2A',
 '2016-03-25 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'T40.2X2A', 'POISONING BY OTHER OPIOIDS, INTENTIONAL SELF-HARM, INITIAL ENCOUNTER',
 'ROUTINE DISCHARGE TO HOME WITH SERVICES', 7, 'Discharged', 516),

-- 7. 2016-06-10: Post-attempt psychiatric follow-up (3 days)
(2002, '2016-06-10 11:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1003, 'F43.10',
 '2016-06-13 14:30:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'F43.10', 'POST-TRAUMATIC STRESS DISORDER, UNSPECIFIED',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 8. 2017-08-22: Chronic pain exacerbation (4 days)
(2002, '2017-08-22 16:20:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1002, 'M54.5',
 '2017-08-26 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'M54.5', 'LOW BACK PAIN',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 9. 2018-06-15: Opioid taper final phase monitoring (5 days)
(2002, '2018-06-15 09:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1003, 'F11.20',
 '2018-06-20 13:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'F11.20', 'OPIOID DEPENDENCE, UNCOMPLICATED',
 'ROUTINE DISCHARGE TO HOME WITH SERVICES', 5, 'Discharged', 516),

-- 10. 2019-10-05: Residential alcohol treatment program (7 days)
(2002, '2019-10-05 08:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 1003, 'F10.20',
 '2019-10-12 14:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 'F10.20', 'ALCOHOL DEPENDENCE, UNCOMPLICATED',
 'COMPLETED PROGRAM DISCHARGE', 7, 'Discharged', 516),

-- 11. 2020-02-14: Spinal cord stimulator trial (4 days, unsuccessful)
(2002, '2020-02-14 07:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 1002, 'M54.5',
 '2020-02-18 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 'M54.5', 'LOW BACK PAIN',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 12. 2021-05-20: Acute kidney injury (4 days)
(2002, '2021-05-20 18:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'N17.9',
 '2021-05-24 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'N17.9', 'ACUTE KIDNEY FAILURE, UNSPECIFIED',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 13. 2022-11-10: Diabetic ketoacidosis (4 days)
(2002, '2022-11-10 05:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'E11.10',
 '2022-11-14 14:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'E11.10', 'TYPE 2 DIABETES MELLITUS WITH KETOACIDOSIS WITHOUT COMA',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 14. 2023-03-18: Atrial fibrillation (3 days)
(2002, '2023-03-18 12:45:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'I48.91',
 '2023-03-21 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'I48.91', 'UNSPECIFIED ATRIAL FIBRILLATION',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- ADDITIONAL ENCOUNTERS (15-32): Routine admissions for chronic disease management

-- 15. 2011-08-10: Pneumonia (4 days)
(2002, '2011-08-10 20:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'J18.9',
 '2011-08-14 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'J18.9', 'PNEUMONIA, UNSPECIFIED ORGANISM',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 16. 2012-04-18: Cellulitis left leg (3 days)
(2002, '2012-04-18 14:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'L03.116',
 '2012-04-21 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'L03.116', 'CELLULITIS OF LEFT LOWER LIMB',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 17. 2013-06-05: UTI/urosepsis (3 days)
(2002, '2013-06-05 16:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'N39.0',
 '2013-06-08 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'N39.0', 'URINARY TRACT INFECTION, SITE NOT SPECIFIED',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 18. 2014-09-12: COPD exacerbation (4 days)
(2002, '2014-09-12 11:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'J44.1',
 '2014-09-16 13:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'J44.1', 'CHRONIC OBSTRUCTIVE PULMONARY DISEASE WITH ACUTE EXACERBATION',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 19. 2015-10-20: Acute gastritis/GI bleed (3 days)
(2002, '2015-10-20 22:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'K29.70',
 '2015-10-23 14:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'K29.70', 'GASTRITIS, UNSPECIFIED, WITHOUT BLEEDING',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 20. 2016-11-15: Diabetic foot infection (5 days)
(2002, '2016-11-15 13:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'E11.621',
 '2016-11-20 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'E11.621', 'TYPE 2 DIABETES MELLITUS WITH FOOT ULCER',
 'ROUTINE DISCHARGE TO HOME WITH HOME HEALTH', 5, 'Discharged', 516),

-- 21. 2017-03-10: Sleep study/OSA diagnosis (2 days)
(2002, '2017-03-10 18:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 1001, 'G47.33',
 '2017-03-12 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
 'G47.33', 'OBSTRUCTIVE SLEEP APNEA',
 'ROUTINE DISCHARGE TO HOME', 2, 'Discharged', 516),

-- 22. 2018-01-22: Hypertensive urgency (2 days)
(2002, '2018-01-22 19:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'I16.0',
 '2018-01-24 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'I16.0', 'HYPERTENSIVE URGENCY',
 'ROUTINE DISCHARGE TO HOME', 2, 'Discharged', 516),

-- 23. 2019-02-14: Acute bronchitis (3 days)
(2002, '2019-02-14 15:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'J20.9',
 '2019-02-17 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'J20.9', 'ACUTE BRONCHITIS, UNSPECIFIED',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 24. 2019-07-08: CKD Stage 3a workup (3 days)
(2002, '2019-07-08 10:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'N18.3',
 '2019-07-11 13:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'N18.3', 'CHRONIC KIDNEY DISEASE, STAGE 3 (MODERATE)',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516),

-- 25. 2020-08-20: COVID-19 pneumonia (6 days)
(2002, '2020-08-20 17:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'U07.1',
 '2020-08-26 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'U07.1', 'COVID-19',
 'ROUTINE DISCHARGE TO HOME', 6, 'Discharged', 516),

-- 26. 2021-01-15: Pyelonephritis (4 days)
(2002, '2021-01-15 21:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'N10',
 '2021-01-19 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'N10', 'ACUTE PYELONEPHRITIS',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 27. 2021-09-22: Diverticulitis (4 days)
(2002, '2021-09-22 12:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'K57.32',
 '2021-09-26 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'K57.32', 'DIVERTICULITIS OF LARGE INTESTINE WITHOUT PERFORATION OR ABSCESS WITHOUT BLEEDING',
 'ROUTINE DISCHARGE TO HOME', 4, 'Discharged', 516),

-- 28. 2022-03-15: CHF exacerbation (5 days)
(2002, '2022-03-15 08:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'I50.9',
 '2022-03-20 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'I50.9', 'HEART FAILURE, UNSPECIFIED',
 'ROUTINE DISCHARGE TO HOME', 5, 'Discharged', 516),

-- 29. 2023-07-10: Syncope workup (2 days)
(2002, '2023-07-10 16:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'R55',
 '2023-07-12 11:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'R55', 'SYNCOPE AND COLLAPSE',
 'ROUTINE DISCHARGE TO HOME', 2, 'Discharged', 516),

-- 30. 2024-05-18: Hypoglycemia (2 days)
(2002, '2024-05-18 04:30:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'E11.649',
 '2024-05-20 10:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'E11.649', 'TYPE 2 DIABETES MELLITUS WITH HYPOGLYCEMIA WITHOUT COMA',
 'ROUTINE DISCHARGE TO HOME', 2, 'Discharged', 516),

-- 31. 2024-10-12: Acute respiratory failure (4 days)
(2002, '2024-10-12 19:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'J96.00',
 '2024-10-16 13:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'J96.00', 'ACUTE RESPIRATORY FAILURE, UNSPECIFIED WHETHER WITH HYPOXIA OR HYPERCAPNIA',
 'ROUTINE DISCHARGE TO HOME WITH HOME HEALTH', 4, 'Discharged', 516),

-- 32. 2025-01-10: Pre-relocation comprehensive workup (3 days)
(2002, '2025-01-10 09:00:00',
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 1001, 'Z00.00',
 '2025-01-13 12:00:00', NULL,
 (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'WARD'),
 'Z00.00', 'ENCOUNTER FOR GENERAL ADULT MEDICAL EXAMINATION WITHOUT ABNORMAL FINDINGS',
 'ROUTINE DISCHARGE TO HOME', 3, 'Discharged', 516);
GO

PRINT '  Alananah Thompson encounters inserted (32 admissions, 2010-2025)';
PRINT '  Key encounters: PTSD (2011), HTN crisis (2012), Suicide attempt (2016), Opioid taper (2018), Alcohol treatment (2019)';
PRINT '  Total hospital days: 120 days over 15 years (avg 8 days/year)';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 6 (Encounters) Complete';
PRINT '====  32 inpatient admissions inserted (2010-2025)';
PRINT '=====================================================';
GO
-- =====================================================
-- SECTION 7: CLINICAL NOTES - TIU.TIUDocument_8925 + TIUDocumentText
-- =====================================================
-- Alananah Thompson: Representative subset of clinical notes
-- Full implementation would include ~220 notes total:
--   - Discharge Summaries (32, one per encounter)
--   - Progress Notes (~120, quarterly primary care + specialty)
--   - Consult Notes (~40, specialty consultations)
--   - Procedure Notes (~15)
--   - Emergency Notes (~10)
--
-- This implementation creates key clinical notes aligned with major encounters
-- Focus: Critical events (suicide attempt, substance use, diabetes dx)
-- =====================================================
-- NOTE STRATEGY:
--   - Use IDENTITY for TIUDocumentSID (auto-assign, do NOT specify)
--   - Link discharge summaries to InpatientSID using subquery
--   - Progress notes have NULL InpatientSID (outpatient context)
--   - DocumentDefinitionSID lookup from Dim.TIUDocumentDefinition
--   - ReferenceDateTime = clinical date (when note is about)
--   - EntryDateTime = when note was written (usually same day or 1-2 days later)
-- =====================================================

PRINT '';
PRINT '=====================================================';
PRINT 'Section 7: Clinical Notes';
PRINT '  Creating representative subset of Alananah Thompson clinical notes';
PRINT '  Linked to key encounters and outpatient visits';
PRINT '=====================================================';
GO

-- Insert TIU document metadata (representative sample)
-- Will capture TIUDocumentSIDs using OUTPUT clause for text insertion

DECLARE @BaileyNotes TABLE (
    TIUDocumentSID BIGINT,
    NoteSequence INT,
    NoteType VARCHAR(50)
);

-- Note 1: Psychiatry Progress Note (Post-Suicide Attempt, 2016-09-20)
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
OUTPUT INSERTED.TIUDocumentSID, 1, 'Psychiatry Progress' INTO @BaileyNotes
VALUES (
    2002,  -- PatientSID
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2016-09-20 14:30:00',  -- ReferenceDateTime (clinical date)
    '2016-09-20 15:45:00',  -- EntryDateTime (when note was written)
    'COMPLETED',
    1001,  -- AuthorSID (mock provider)
    1002,  -- CosignerSID (attending psychiatrist)
    (SELECT TOP 1 InpatientSID FROM Inpat.Inpatient WHERE PatientSID = 2002 AND CAST(AdmitDateTime AS DATE) = '2016-09-12'),  -- Link to suicide attempt admission
    516,  -- Sta3n (Bay Pines)
    'BaileyTIU001'
);

-- Note 2: Discharge Summary (Suicide Attempt, 2016-09-24)
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
OUTPUT INSERTED.TIUDocumentSID, 2, 'Discharge Summary' INTO @BaileyNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Discharge Summaries'),
    '2016-09-24 11:00:00',
    '2016-09-24 16:30:00',
    'COMPLETED',
    1002,  -- Attending psychiatrist
    NULL,
    (SELECT TOP 1 InpatientSID FROM Inpat.Inpatient WHERE PatientSID = 2002 AND CAST(AdmitDateTime AS DATE) = '2016-09-12'),
    516,
    'BaileyTIU002'
);

-- Note 3: Primary Care Progress Note (Diabetes Diagnosis, 2019-01-05)
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
OUTPUT INSERTED.TIUDocumentSID, 3, 'Primary Care Progress' INTO @BaileyNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2019-01-05 10:00:00',
    '2019-01-05 11:30:00',
    'COMPLETED',
    1001,
    NULL,
    NULL,  -- Outpatient visit, no InpatientSID
    516,
    'BaileyTIU003'
);

-- Note 4: Discharge Summary (Diabetic Ketoacidosis, 2022-11-14)
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
OUTPUT INSERTED.TIUDocumentSID, 4, 'DKA Discharge' INTO @BaileyNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Discharge Summaries'),
    '2022-11-14 15:00:00',
    '2022-11-14 18:00:00',
    'COMPLETED',
    1003,  -- Endocrinology attending
    NULL,
    (SELECT TOP 1 InpatientSID FROM Inpat.Inpatient WHERE PatientSID = 2002 AND CAST(AdmitDateTime AS DATE) = '2022-11-10'),
    516,
    'BaileyTIU004'
);

-- Note 5: Substance Use Consult (Alcohol Use Disorder, 2019-01-25)
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
OUTPUT INSERTED.TIUDocumentSID, 5, 'Substance Use Consult' INTO @BaileyNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Consults'),
    '2019-01-25 09:00:00',
    '2019-01-25 12:00:00',
    'COMPLETED',
    1004,  -- Addiction medicine specialist
    1002,
    (SELECT TOP 1 InpatientSID FROM Inpat.Inpatient WHERE PatientSID = 2002 AND CAST(AdmitDateTime AS DATE) = '2019-01-22'),
    516,
    'BaileyTIU005'
);

-- Note 6: Cardiology Consult (Hypertensive Crisis Workup, 2012-03-20)
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
OUTPUT INSERTED.TIUDocumentSID, 6, 'Cardiology Consult' INTO @BaileyNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Consults'),
    '2012-03-20 11:00:00',
    '2012-03-20 14:30:00',
    'COMPLETED',
    1005,  -- Cardiologist
    NULL,
    (SELECT TOP 1 InpatientSID FROM Inpat.Inpatient WHERE PatientSID = 2002 AND CAST(AdmitDateTime AS DATE) = '2012-03-18'),
    516,
    'BaileyTIU006'
);

-- Note 7: Pain Management Progress Note (Opioid Taper, 2018-06-15)
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
OUTPUT INSERTED.TIUDocumentSID, 7, 'Pain Management Progress' INTO @BaileyNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Progress Notes'),
    '2018-06-15 13:00:00',
    '2018-06-15 14:15:00',
    'COMPLETED',
    1006,  -- Pain management specialist
    NULL,
    NULL,  -- Outpatient visit
    516,
    'BaileyTIU007'
);

-- Note 8: Nephrology Consult (CKD Stage 3a Diagnosis, 2019-07-10)
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
OUTPUT INSERTED.TIUDocumentSID, 8, 'Nephrology Consult' INTO @BaileyNotes
VALUES (
    2002,
    (SELECT TOP 1 DocumentDefinitionSID FROM Dim.TIUDocumentDefinition WHERE DocumentClass = 'Consults'),
    '2019-07-10 10:00:00',
    '2019-07-10 13:00:00',
    'COMPLETED',
    1007,  -- Nephrologist
    NULL,
    (SELECT TOP 1 InpatientSID FROM Inpat.Inpatient WHERE PatientSID = 2002 AND CAST(AdmitDateTime AS DATE) = '2019-07-08'),
    516,
    'BaileyTIU008'
);

-- Removing GO statements below to preserve @BaileyNotes for the inserts below
-- GO

-- PRINT '  Alananah Thompson: 8 clinical note metadata records inserted';
-- GO

-- =====================================================
-- Insert Clinical Note Text Content (SOAP format)
-- =====================================================
-- Apostrophes are escaped by doubling ('')
-- All clinical content is synthetic and does not contain real PHI/PII
-- =====================================================

-- Note 1 Text: Psychiatry Progress Note (Suicide Attempt Follow-up)
INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, DocumentText, TextLength)
SELECT TIUDocumentSID, 
'PSYCHIATRY PROGRESS NOTE
Date: 2016-09-20
Patient: Alananah Marie Thompson (ICN200002)
Author: Dr. Sarah Mitchell, MD (Psychiatry)

SUBJECTIVE:
Patient is a 53-year-old male veteran with combat-related PTSD, chronic pain, and major depressive disorder. Admitted 9/12 after suicide attempt via intentional opioid overdose (oxycodone 30mg x 20 tablets). Reports feeling overwhelmed by chronic pain, financial stress, and divorce proceedings. States "I just wanted the pain to stop." Admits to passive suicidal ideation over past 3 months but denies specific plan prior to 9/12. Reports regret about overdose, states "I scared my kids."

OBJECTIVE:
Mental Status Exam:
- Appearance: Disheveled, fair hygiene
- Mood: Dysphoric, tearful at times
- Affect: Congruent, flat at baseline
- Speech: Normal rate, low volume
- Thought Process: Logical, goal-directed
- Thought Content: Denies current SI/HI, no psychosis
- Insight: Fair, acknowledges depression and need for treatment
- Judgment: Improving, engaged in safety planning

Assessment Scales:
- PHQ-9: 24 (severe depression)
- PCL-5: 62 (severe PTSD symptoms)
- Pain VAS: 7/10 (chronic lumbar pain)

ASSESSMENT:
1. Suicide attempt (T50.905A - Poisoning by opioids, intentional self-harm)
2. Major depressive disorder, recurrent, severe (F33.2)
3. Post-traumatic stress disorder, chronic (F43.10)
4. Opioid use disorder, in remission (F11.21) - Patient taking meds as prescribed, overdose was acute crisis
5. Chronic pain syndrome (M54.16)

HIGH RISK FOR REPEAT SUICIDE ATTEMPT. Multiple risk factors: recent attempt, severe MDD, PTSD, chronic pain, psychosocial stressors (divorce, financial strain), social isolation.

PLAN:
1. Medication Management:
   - Continue sertraline 200mg daily (therapeutic dose)
   - ADD prazosin 5mg nightly for PTSD nightmares (start tonight)
   - Pain management consult for opioid taper (high suicide risk with current opioid access)

2. Safety Planning:
   - Safety plan reviewed and updated with patient
   - Means restriction: Sister Alananah will secure all firearms from patient''s home
   - Opioid prescription will be limited to 7-day supply with weekly visits
   - Emergency contact card provided (Crisis Line 988, VA Suicide Prevention Hotline)

3. Follow-Up:
   - Weekly therapy with Dr. Rodriguez (cognitive processing therapy for PTSD)
   - Psychiatry follow-up in 1 week (9/27)
   - Pain management consult scheduled for 9/22

4. Flags:
   - HIGH RISK FOR SUICIDE FLAG ACTIVATED (Cat I National)
   - Opioid Risk flag to be reviewed (consider taper to reduce access)

5. Disposition:
   - Continue inpatient psychiatric care for 2-3 more days
   - Transition to Intensive Outpatient Program (IOP) upon discharge
   - Family meeting scheduled for 9/21 (sister Alananah)

Discussed case with Dr. Chen (Attending Psychiatrist). Patient is stabilizing but remains high-risk. Close follow-up essential.

Electronically signed: Dr. Sarah Mitchell, MD (Psychiatry)
Co-signed: Dr. Robert Chen, MD (Attending Psychiatrist)',
LEN('PSYCHIATRY PROGRESS NOTE
Date: 2016-09-20
Patient: Alananah Marie Thompson (ICN200002)
Author: Dr. Sarah Mitchell, MD (Psychiatry)

SUBJECTIVE:
Patient is a 53-year-old male veteran with combat-related PTSD, chronic pain, and major depressive disorder. Admitted 9/12 after suicide attempt via intentional opioid overdose (oxycodone 30mg x 20 tablets). Reports feeling overwhelmed by chronic pain, financial stress, and divorce proceedings. States "I just wanted the pain to stop." Admits to passive suicidal ideation over past 3 months but denies specific plan prior to 9/12. Reports regret about overdose, states "I scared my kids."

OBJECTIVE:
Mental Status Exam:
- Appearance: Disheveled, fair hygiene
- Mood: Dysphoric, tearful at times
- Affect: Congruent, flat at baseline
- Speech: Normal rate, low volume
- Thought Process: Logical, goal-directed
- Thought Content: Denies current SI/HI, no psychosis
- Insight: Fair, acknowledges depression and need for treatment
- Judgment: Improving, engaged in safety planning

Assessment Scales:
- PHQ-9: 24 (severe depression)
- PCL-5: 62 (severe PTSD symptoms)
- Pain VAS: 7/10 (chronic lumbar pain)

ASSESSMENT:
1. Suicide attempt (T50.905A - Poisoning by opioids, intentional self-harm)
2. Major depressive disorder, recurrent, severe (F33.2)
3. Post-traumatic stress disorder, chronic (F43.10)
4. Opioid use disorder, in remission (F11.21) - Patient taking meds as prescribed, overdose was acute crisis
5. Chronic pain syndrome (M54.16)

HIGH RISK FOR REPEAT SUICIDE ATTEMPT. Multiple risk factors: recent attempt, severe MDD, PTSD, chronic pain, psychosocial stressors (divorce, financial strain), social isolation.

PLAN:
1. Medication Management:
   - Continue sertraline 200mg daily (therapeutic dose)
   - ADD prazosin 5mg nightly for PTSD nightmares (start tonight)
   - Pain management consult for opioid taper (high suicide risk with current opioid access)

2. Safety Planning:
   - Safety plan reviewed and updated with patient
   - Means restriction: Sister Alananah will secure all firearms from patient''s home
   - Opioid prescription will be limited to 7-day supply with weekly visits
   - Emergency contact card provided (Crisis Line 988, VA Suicide Prevention Hotline)

3. Follow-Up:
   - Weekly therapy with Dr. Rodriguez (cognitive processing therapy for PTSD)
   - Psychiatry follow-up in 1 week (9/27)
   - Pain management consult scheduled for 9/22

4. Flags:
   - HIGH RISK FOR SUICIDE FLAG ACTIVATED (Cat I National)
   - Opioid Risk flag to be reviewed (consider taper to reduce access)

5. Disposition:
   - Continue inpatient psychiatric care for 2-3 more days
   - Transition to Intensive Outpatient Program (IOP) upon discharge
   - Family meeting scheduled for 9/21 (sister Alananah)

Discussed case with Dr. Chen (Attending Psychiatrist). Patient is stabilizing but remains high-risk. Close follow-up essential.

Electronically signed: Dr. Sarah Mitchell, MD (Psychiatry)
Co-signed: Dr. Robert Chen, MD (Attending Psychiatrist)')
FROM @BaileyNotes WHERE NoteSequence = 1;
-- GO

-- Note 2 Text: Discharge Summary (Suicide Attempt)
INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, DocumentText, TextLength)
SELECT TIUDocumentSID,
'PSYCHIATRIC DISCHARGE SUMMARY

Patient: Alananah Marie Thompson, ICN200002
DOB: 1963-04-15 (Age 53)
Admission Date: 2016-09-12
Discharge Date: 2016-09-24
Length of Stay: 12 days
Attending: Dr. Robert Chen, MD (Psychiatry)

CHIEF COMPLAINT:
"I took too many pills."

HISTORY OF PRESENT ILLNESS:
Mr. Thompson is a 53-year-old male veteran with history of PTSD, major depressive disorder, and chronic pain who presented to Emergency Department on 9/12/2016 after intentional overdose of oxycodone. Patient reportedly ingested approximately 600mg oxycodone (20 tablets x 30mg) at home around 6:00 AM. Patient''s sister Alananah found him unresponsive around 9:00 AM and called 911. EMS administered 2mg naloxone IV with improved responsiveness. Patient transported to Bay Pines VA for further care.

In ED, patient was somnolent but arousable. Vital signs stable after naloxone. Denied intent to repeat attempt but acknowledged ongoing passive suicidal ideation. Psychiatric consultation recommended admission to inpatient psychiatry for safety and stabilization.

PAST PSYCHIATRIC HISTORY:
- Post-traumatic stress disorder (combat-related, Gulf War + Iraq OIF)
- Major depressive disorder, recurrent
- Prior suicide attempt 2004 (gunshot, survived TBI)
- Multiple psychiatric hospitalizations 2004-2011
- Outpatient treatment: Psychiatry clinic (Dr. Mitchell), weekly therapy

PAST MEDICAL HISTORY:
- Chronic lumbar radiculopathy (IED blast injury 2004)
- Traumatic brain injury, sequelae (2004 gunshot)
- Chronic tinnitus, bilateral
- Hypertension
- Obesity
- Obstructive sleep apnea

SOCIAL HISTORY:
- Retired U.S. Army (1990-2010), Gulf War + OIF veteran
- 50% service-connected disability
- Divorced 2018 (ongoing financial stress, custody issues)
- Lives alone in St. Petersburg, FL
- Tobacco: Denies
- Alcohol: Reports increased use (4-6 beers/night) over past 6 months
- Substance use: Denies illicit drugs

FAMILY HISTORY:
- Father: Suicide (1998)
- Sister: Alananah Thompson (breast cancer survivor, supportive)

MEDICATIONS ON ADMISSION:
1. Sertraline 200mg PO daily
2. Prazosin 5mg PO nightly
3. Oxycodone 30mg PO Q6H PRN pain
4. Gabapentin 800mg PO TID
5. Lisinopril 20mg PO daily
6. CPAP for sleep apnea

HOSPITAL COURSE:
Patient admitted to psychiatry ward 2A. Initial 72-hour hold placed for danger to self. Patient was cooperative with treatment, participated in group therapy, individual therapy sessions, and medication management. Safety plan developed collaboratively with patient, social work, and family.

Key interventions:
1. Medication optimization: Continued sertraline 200mg daily, prazosin dose confirmed
2. Opioid management: Consulted pain management service. Recommendation to initiate slow opioid taper given suicide risk. Patient agreeable to taper plan starting after discharge.
3. Alcohol use: Patient screened positive for alcohol use disorder (AUDIT score 18). Referred to substance use disorder clinic for evaluation and treatment.
4. Safety planning: Means restriction - sister Alananah removed firearms from patient''s home. Opioid prescriptions limited to 7-day supply with weekly clinic visits during taper.
5. Family support: Family meeting held 9/21 with sister Alananah. Sister committed to weekly phone check-ins and will assist with medication management.
6. Flag activation: HIGH RISK FOR SUICIDE flag (Cat I National) activated in patient record.

MENTAL STATUS AT DISCHARGE:
- Alert, oriented x 3
- Mood: "Better, but still struggling"
- Affect: Euthymic, appropriate
- Thought process: Goal-directed, logical
- Thought content: Denies SI/HI, future-oriented
- Insight: Good, acknowledges need for ongoing treatment
- Judgment: Improved

DISCHARGE DIAGNOSES:
1. Suicide attempt via opioid overdose (T50.905A)
2. Major depressive disorder, recurrent, severe without psychotic features (F33.2)
3. Post-traumatic stress disorder, chronic (F43.10)
4. Alcohol use disorder, moderate (F10.20)
5. Opioid use disorder, mild (prescribed opioids, risk for misuse)
6. Chronic pain syndrome (M54.16)

DISCHARGE CONDITION:
Stable for discharge to outpatient care. Suicide risk reduced from high to moderate. Patient verbalized safety plan, has crisis resources, and committed to follow-up appointments.

DISCHARGE MEDICATIONS:
1. Sertraline 200mg PO daily
2. Prazosin 5mg PO nightly
3. Oxycodone 30mg PO Q6H PRN pain (7-day supply only, weekly refills during taper)
4. Gabapentin 800mg PO TID
5. Lisinopril 20mg PO daily

DISCHARGE PLAN:
1. Follow-up appointments:
   - Psychiatry (Dr. Mitchell): 9/27/2016 (3 days post-discharge)
   - Pain Management: 9/29/2016 (opioid taper initiation)
   - Substance Use Disorder Clinic: 10/05/2016
   - Primary Care: 10/15/2016

2. Therapy: Continue weekly individual therapy (CPT for PTSD)

3. Intensive Outpatient Program (IOP): Enrolled, starts 9/26/2016

4. Safety resources:
   - VA Crisis Line: 988, then press 1
   - Emergency contact: Sister Alananah (phone on file)
   - Return to ED if SI/HI or crisis

5. Monitoring: Weekly phone check-ins from psychiatry RN for first 4 weeks

PROGNOSIS:
Guarded. Patient has multiple risk factors for suicide (prior attempts, severe MDD, PTSD, chronic pain, substance use, social stressors). However, patient engaged in treatment, has supportive family, and committed to safety plan. Close outpatient follow-up essential.

Electronically signed: Dr. Robert Chen, MD
Bay Pines VA Healthcare System
Department of Psychiatry
Date: 2016-09-24 16:30',
LEN('PSYCHIATRIC DISCHARGE SUMMARY

Patient: Alananah Marie Thompson, ICN200002
DOB: 1963-04-15 (Age 53)
Admission Date: 2016-09-12
Discharge Date: 2016-09-24
Length of Stay: 12 days
Attending: Dr. Robert Chen, MD (Psychiatry)

CHIEF COMPLAINT:
"I took too many pills."

HISTORY OF PRESENT ILLNESS:
Mr. Thompson is a 53-year-old male veteran with history of PTSD, major depressive disorder, and chronic pain who presented to Emergency Department on 9/12/2016 after intentional overdose of oxycodone. Patient reportedly ingested approximately 600mg oxycodone (20 tablets x 30mg) at home around 6:00 AM. Patient''s sister Alananah found him unresponsive around 9:00 AM and called 911. EMS administered 2mg naloxone IV with improved responsiveness. Patient transported to Bay Pines VA for further care.

In ED, patient was somnolent but arousable. Vital signs stable after naloxone. Denied intent to repeat attempt but acknowledged ongoing passive suicidal ideation. Psychiatric consultation recommended admission to inpatient psychiatry for safety and stabilization.

PAST PSYCHIATRIC HISTORY:
- Post-traumatic stress disorder (combat-related, Gulf War + Iraq OIF)
- Major depressive disorder, recurrent
- Prior suicide attempt 2004 (gunshot, survived TBI)
- Multiple psychiatric hospitalizations 2004-2011
- Outpatient treatment: Psychiatry clinic (Dr. Mitchell), weekly therapy

PAST MEDICAL HISTORY:
- Chronic lumbar radiculopathy (IED blast injury 2004)
- Traumatic brain injury, sequelae (2004 gunshot)
- Chronic tinnitus, bilateral
- Hypertension
- Obesity
- Obstructive sleep apnea

SOCIAL HISTORY:
- Retired U.S. Army (1990-2010), Gulf War + OIF veteran
- 50% service-connected disability
- Divorced 2018 (ongoing financial stress, custody issues)
- Lives alone in St. Petersburg, FL
- Tobacco: Denies
- Alcohol: Reports increased use (4-6 beers/night) over past 6 months
- Substance use: Denies illicit drugs

FAMILY HISTORY:
- Father: Suicide (1998)
- Sister: Alananah Thompson (breast cancer survivor, supportive)

MEDICATIONS ON ADMISSION:
1. Sertraline 200mg PO daily
2. Prazosin 5mg PO nightly
3. Oxycodone 30mg PO Q6H PRN pain
4. Gabapentin 800mg PO TID
5. Lisinopril 20mg PO daily
6. CPAP for sleep apnea

HOSPITAL COURSE:
Patient admitted to psychiatry ward 2A. Initial 72-hour hold placed for danger to self. Patient was cooperative with treatment, participated in group therapy, individual therapy sessions, and medication management. Safety plan developed collaboratively with patient, social work, and family.

Key interventions:
1. Medication optimization: Continued sertraline 200mg daily, prazosin dose confirmed
2. Opioid management: Consulted pain management service. Recommendation to initiate slow opioid taper given suicide risk. Patient agreeable to taper plan starting after discharge.
3. Alcohol use: Patient screened positive for alcohol use disorder (AUDIT score 18). Referred to substance use disorder clinic for evaluation and treatment.
4. Safety planning: Means restriction - sister Alananah removed firearms from patient''s home. Opioid prescriptions limited to 7-day supply with weekly clinic visits during taper.
5. Family support: Family meeting held 9/21 with sister Alananah. Sister committed to weekly phone check-ins and will assist with medication management.
6. Flag activation: HIGH RISK FOR SUICIDE flag (Cat I National) activated in patient record.

MENTAL STATUS AT DISCHARGE:
- Alert, oriented x 3
- Mood: "Better, but still struggling"
- Affect: Euthymic, appropriate
- Thought process: Goal-directed, logical
- Thought content: Denies SI/HI, future-oriented
- Insight: Good, acknowledges need for ongoing treatment
- Judgment: Improved

DISCHARGE DIAGNOSES:
1. Suicide attempt via opioid overdose (T50.905A)
2. Major depressive disorder, recurrent, severe without psychotic features (F33.2)
3. Post-traumatic stress disorder, chronic (F43.10)
4. Alcohol use disorder, moderate (F10.20)
5. Opioid use disorder, mild (prescribed opioids, risk for misuse)
6. Chronic pain syndrome (M54.16)

DISCHARGE CONDITION:
Stable for discharge to outpatient care. Suicide risk reduced from high to moderate. Patient verbalized safety plan, has crisis resources, and committed to follow-up appointments.

DISCHARGE MEDICATIONS:
1. Sertraline 200mg PO daily
2. Prazosin 5mg PO nightly
3. Oxycodone 30mg PO Q6H PRN pain (7-day supply only, weekly refills during taper)
4. Gabapentin 800mg PO TID
5. Lisinopril 20mg PO daily

DISCHARGE PLAN:
1. Follow-up appointments:
   - Psychiatry (Dr. Mitchell): 9/27/2016 (3 days post-discharge)
   - Pain Management: 9/29/2016 (opioid taper initiation)
   - Substance Use Disorder Clinic: 10/05/2016
   - Primary Care: 10/15/2016

2. Therapy: Continue weekly individual therapy (CPT for PTSD)

3. Intensive Outpatient Program (IOP): Enrolled, starts 9/26/2016

4. Safety resources:
   - VA Crisis Line: 988, then press 1
   - Emergency contact: Sister Alananah (phone on file)
   - Return to ED if SI/HI or crisis

5. Monitoring: Weekly phone check-ins from psychiatry RN for first 4 weeks

PROGNOSIS:
Guarded. Patient has multiple risk factors for suicide (prior attempts, severe MDD, PTSD, chronic pain, substance use, social stressors). However, patient engaged in treatment, has supportive family, and committed to safety plan. Close outpatient follow-up essential.

Electronically signed: Dr. Robert Chen, MD
Bay Pines VA Healthcare System
Department of Psychiatry
Date: 2016-09-24 16:30')
FROM @BaileyNotes WHERE NoteSequence = 2;
GO

PRINT '  Alananah Thompson: Clinical note text inserted (2 detailed notes: Psychiatry Progress + Discharge Summary)';
GO

PRINT '';
PRINT '=====================================================';
PRINT '====  Alananah Thompson: Section 7 (Clinical Notes) Complete';
PRINT '====  8 note metadata records + 2 full text notes inserted';
PRINT '====  Representative subset created (production would have ~220 total)';
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
-- Section 8.2: PROBLEMS / DIAGNOSES (18 total, Charlson Score = 5)
-- =====================================================
PRINT '  Section 8.2: Problems/Diagnoses (16 problems, Charlson Comorbidity Index = 2)';
GO

INSERT INTO Outpat.ProblemList (
    PatientSID, PatientICN, Sta3n, ProblemNumber, SNOMEDCode, SNOMEDDescription,
    ICD10Code, ICD10Description, ProblemStatus, OnsetDate, RecordedDate, LastModifiedDate,
    ResolvedDate, ProviderSID, ProviderName, Clinic, IsServiceConnected, IsAcuteCondition, IsChronicCondition,
    EnteredBy, EnteredDateTime
)
VALUES
-- Active chronic conditions (15 total)
(2002, 'ICN200002', 516, 'P2002-1', '47505003', 'Post-traumatic stress disorder', 'F43.10', 'Post-traumatic stress disorder, unspecified', 'ACTIVE', '2004-04-12', '2011-02-15', '2024-10-20', NULL, 1001, 'Mitchell, Sarah MD', 'Mental Health', 'Y', 'N', 'Y', 'Mitchell, Sarah MD', '2011-02-15 14:30:00'),
(2002, 'ICN200002', 516, 'P2002-2', '90560007', 'Chronic lower back pain', 'M54.16', 'Radiculopathy, lumbar region', 'ACTIVE', '2004-04-12', '2010-06-20', '2024-09-15', NULL, 1006, 'Rodriguez, Juan MD', 'Pain Management', 'Y', 'N', 'Y', 'Rodriguez, Juan MD', '2010-06-20 13:00:00'),
(2002, 'ICN200002', 516, 'P2002-3', '127295002', 'Traumatic brain injury, sequelae', 'S06.9X9S', 'Unspecified intracranial injury with loss of consciousness of unspecified duration, sequela', 'ACTIVE', '2004-04-12', '2010-06-20', '2024-11-10', NULL, 1014, 'Nguyen, Linh MD', 'Neurology', 'Y', 'N', 'Y', 'Nguyen, Linh MD', '2010-06-20 15:45:00'),
(2002, 'ICN200002', 516, 'P2002-4', '15188001', 'Hearing loss, bilateral', 'H93.13', 'Tinnitus, bilateral', 'ACTIVE', '2004-04-12', '2011-05-10', '2024-08-25', NULL, 1020, 'Harper, Susan MD', 'Audiology', 'Y', 'N', 'Y', 'Harper, Susan MD', '2011-05-10 10:15:00'),
(2002, 'ICN200002', 516, 'P2002-5', '370143000', 'Major depressive disorder', 'F33.1', 'Major depressive disorder, recurrent, moderate', 'ACTIVE', '2011-02-10', '2011-02-15', '2024-10-15', NULL, 1001, 'Mitchell, Sarah MD', 'Mental Health', 'Y', 'N', 'Y', 'Mitchell, Sarah MD', '2011-02-15 14:45:00'),
(2002, 'ICN200002', 516, 'P2002-6', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2012-03-18', '2012-03-20', '2025-01-05', NULL, 1005, 'Baker, Christine MD', 'Cardiology', 'N', 'N', 'Y', 'Baker, Christine MD', '2012-03-20 10:00:00'),
(2002, 'ICN200002', 516, 'P2002-7', '267036007', 'Dyslipidemia', 'E78.2', 'Mixed hyperlipidemia', 'ACTIVE', '2012-06-15', '2012-06-20', '2024-12-01', NULL, 1010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2012-06-20 09:30:00'),
(2002, 'ICN200002', 516, 'P2002-8', '44054006', 'Type 2 diabetes mellitus', 'E11.9', 'Type 2 diabetes mellitus without complications', 'ACTIVE', '2019-01-05', '2019-01-05', '2024-12-15', NULL, 1003, 'Patel, Raj MD', 'Endocrinology', 'N', 'N', 'Y', 'Patel, Raj MD', '2019-01-05 10:45:00'),
(2002, 'ICN200002', 516, 'P2002-9', '46177005', 'Chronic kidney disease', 'N18.3', 'Chronic kidney disease, stage 3a (moderate)', 'ACTIVE', '2019-07-08', '2019-07-10', '2025-01-08', NULL, 1007, 'Kim, Jennifer MD', 'Nephrology', 'N', 'N', 'Y', 'Kim, Jennifer MD', '2019-07-10 14:15:00'),
(2002, 'ICN200002', 516, 'P2002-10', '78275009', 'Obstructive sleep apnea', 'G47.33', 'Obstructive sleep apnea', 'ACTIVE', '2013-05-20', '2013-05-25', '2024-11-20', NULL, 1011, 'Garcia, Maria MD', 'Sleep Medicine', 'Y', 'N', 'Y', 'Garcia, Maria MD', '2013-05-25 11:00:00'),
(2002, 'ICN200002', 516, 'P2002-11', '235595009', 'Gastroesophageal reflux disease', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'ACTIVE', '2014-08-10', '2014-08-15', '2024-10-05', NULL, 1008, 'Martinez, Carlos MD', 'Gastroenterology', 'N', 'N', 'Y', 'Martinez, Carlos MD', '2014-08-15 10:00:00'),
(2002, 'ICN200002', 516, 'P2002-12', '414916001', 'Obesity', 'E66.9', 'Obesity, unspecified', 'ACTIVE', '2010-06-16', '2010-06-16', '2024-11-10', NULL, 1010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2010-06-16 10:15:00'),
(2002, 'ICN200002', 516, 'P2002-13', '53741008', 'Coronary atherosclerosis', 'I25.10', 'Atherosclerotic heart disease of native coronary artery without angina pectoris', 'ACTIVE', '2015-11-20', '2015-11-25', '2024-12-10', NULL, 1005, 'Baker, Christine MD', 'Cardiology', 'N', 'N', 'Y', 'Baker, Christine MD', '2015-11-25 11:30:00'),
(2002, 'ICN200002', 516, 'P2002-14', '239873007', 'Osteoarthritis', 'M19.90', 'Unspecified osteoarthritis, unspecified site', 'ACTIVE', '2010-01-01', '2010-08-15', '2024-10-20', NULL, 1009, 'Anderson, Lisa MD', 'Rheumatology', 'Y', 'N', 'Y', 'Anderson, Lisa MD', '2010-08-15 13:15:00'),
(2002, 'ICN200002', 516, 'P2002-15', '49436004', 'Atrial fibrillation', 'I48.91', 'Unspecified atrial fibrillation', 'ACTIVE', '2020-06-10', '2020-06-15', '2024-12-05', NULL, 1005, 'Baker, Christine MD', 'Cardiology', 'N', 'N', 'Y', 'Baker, Christine MD', '2020-06-15 10:15:00'),

-- Resolved/inactive conditions (3 total)
(2002, 'ICN200002', 516, 'P2002-16', '191889009', 'Alcohol use disorder', 'F10.20', 'Alcohol dependence, uncomplicated', 'INACTIVE', '2016-09-12', '2019-01-25', '2020-06-30', NULL, 1004, 'Brown, Michael PhD', 'Substance Use Disorder', 'N', 'N', 'N', 'Brown, Michael PhD', '2019-01-25 12:00:00'),
(2002, 'ICN200002', 516, 'P2002-17', '55822004', 'Hyperlipidemia', 'E78.5', 'Hyperlipidemia, unspecified', 'RESOLVED', '2010-06-16', '2010-06-16', '2012-06-20', '2012-06-20', 1010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'N', 'Taylor, Kevin MD', '2010-06-16 09:45:00'),
(2002, 'ICN200002', 516, 'P2002-18', '233604007', 'Pneumonia', 'J18.9', 'Pneumonia, unspecified organism', 'RESOLVED', '2020-08-20', '2020-08-20', '2020-08-26', '2020-08-26', 1006, 'Miller, James MD', 'Emergency', 'N', 'Y', 'N', 'Miller, James MD', '2020-08-20 08:30:00');
GO

PRINT '    Alananah Thompson: 18 problems inserted (15 active chronic, 3 resolved/inactive)';
PRINT '    Charlson Comorbidity Index = 2 (Breast cancer history +2)';
GO

-- =====================================================
-- Section 8.3: LABORATORY RESULTS (Representative subset ~40 results)
-- =====================================================
-- NOTE: Full implementation would have ~160 results (quarterly BMP, annual A1C/lipids)
-- This creates representative samples across 2010-2025
-- =====================================================
PRINT '  Section 8.3: Laboratory Results (representative subset)';
GO

-- BMP Panel 1 (2024-12-05, recent - showing diabetic control)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 1, 'CH 20241205-2002', '140', 140.0, 'mmol/L', NULL, '135 - 145', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 2, 'CH 20241205-2002', '4.8', 4.8, 'mmol/L', NULL, '3.5 - 5.0', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 3, 'CH 20241205-2002', '102', 102.0, 'mmol/L', NULL, '98 - 107', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 4, 'CH 20241205-2002', '26', 26.0, 'mmol/L', NULL, '22 - 29', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 5, 'CH 20241205-2002', '22', 22.0, 'mg/dL', 'H', '7 - 20', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 6, 'CH 20241205-2002', '1.4', 1.4, 'mg/dL', 'H', '0.7 - 1.3', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 7, 'CH 20241205-2002', '142', 142.0, 'mg/dL', 'H', '70 - 100', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum');
GO

-- HbA1c results (diabetes monitoring, quarterly 2019-2024)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 28, 'CH 20191005-A1C', '8.2', 8.2, '%', 'H', '4.0 - 5.6', '2019-01-05 08:00:00', '2019-01-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20190415-A1C', '7.8', 7.8, '%', 'H', '4.0 - 5.6', '2019-04-15 08:00:00', '2019-04-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20190715-A1C', '7.4', 7.4, '%', 'H', '4.0 - 5.6', '2019-07-15 08:00:00', '2019-07-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20200215-A1C', '7.0', 7.0, '%', 'H', '4.0 - 5.6', '2020-01-15 08:00:00', '2020-01-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20210615-A1C', '6.8', 6.8, '%', 'H', '4.0 - 5.6', '2021-06-15 08:00:00', '2021-06-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20220815-A1C', '6.9', 6.9, '%', 'H', '4.0 - 5.6', '2022-08-15 08:00:00', '2022-08-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20231120-A1C', '7.1', 7.1, '%', 'H', '4.0 - 5.6', '2023-11-20 08:00:00', '2023-11-20 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20241205-A1C', '6.8', 6.8, '%', 'H', '4.0 - 5.6', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood');
GO

-- Lipid panel (2024-06-15, annual)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 23, 'CH 20240615-LIP', '195', 195.0, 'mg/dL', NULL, '0 - 200', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 24, 'CH 20240615-LIP', '108', 108.0, 'mg/dL', 'H', '0 - 100', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 25, 'CH 20240615-LIP', '42', 42.0, 'mg/dL', NULL, '40 - 60', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 26, 'CH 20240615-LIP', '225', 225.0, 'mg/dL', 'H', '0 - 150', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 27, 'CH 20240615-LIP', '45', 45.0, 'mg/dL', NULL, '5 - 40', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum');
GO

-- CBC Panel (2024-09-10)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 8, 'CH 20240910-CBC', '6.8', 6.8, 'K/uL', NULL, '4.5 - 11.0', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 9, 'CH 20240910-CBC', '4.2', 4.2, 'M/uL', 'L', '4.5 - 5.9', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 10, 'CH 20240910-CBC', '13.0', 13.0, 'g/dL', 'L', '13.5 - 17.5', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 11, 'CH 20240910-CBC', '39', 39.0, '%', 'L', '40 - 52', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 12, 'CH 20240910-CBC', '230', 230.0, 'K/uL', NULL, '150 - 400', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood');
GO

PRINT '    Alananah Thompson: 40 lab results inserted (BMP, A1C, Lipids, CBC)';
PRINT '    NOTE: Full implementation would have ~160 results (quarterly panels 2010-2025)';
GO

-- =====================================================
-- Section 8.4: PATIENT FLAGS (2 total)
-- =====================================================
PRINT '  Section 8.4: Patient Flags (2 flags: High Risk for Suicide - ACTIVE, Opioid Risk - INACTIVE)';
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
-- Flag 1: HIGH RISK FOR SUICIDE (Category I National, ACTIVE)
(2002, 1, 'DIABETES MANAGEMENT', 'I', 'N', 1, NULL,
 1, 'ACTIVE', '2016-09-20 14:30:00', NULL,
 '516', '516', '516', 90, 7, '2024-12-01 10:00:00', '2025-03-01 10:00:00'),

-- Flag 2: OPIOID RISK TOOL (Category II Local, INACTIVE - deactivated after taper completion)
(2002, NULL, 'OPIOID RISK TOOL', 'II', 'L', NULL, 100,
 0, 'INACTIVE', '2016-09-22 09:00:00', '2019-01-05 12:00:00',
 '516', '516', '516', 180, 14, '2018-10-15 09:00:00', NULL);
GO

PRINT '    Alananah Thompson: 2 patient flags inserted';
PRINT '      - HIGH RISK FOR SUICIDE (Cat I National, ACTIVE since 2016-09-20, suicide attempt)';
PRINT '      - OPIOID RISK TOOL (Cat II Local, INACTIVE, deactivated 2019-01-05 after taper)';
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
PRINT '  Test patient ready for ETL Bronze/Silver/Gold → PostgreSQL';
PRINT '  UI testing: http://127.0.0.1:8000/patient/ICN200002';
PRINT '=====================================================';
GO

