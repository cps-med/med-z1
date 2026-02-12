-- =====================================================
-- Thompson-Alananah.sql - CDWWork2 (Corrected)
-- Patient: Alananah Marie Thompson
-- ICN: ICN200002, PersonSID: 3002
-- Moderate Complexity Patient (Charlson Index = 2)
-- =====================================================
-- Patient relocated from Bay Pines FL (CDWWork/VistA Sta3n 516)
-- to Walla Walla WA (CDWWork2/Cerner Sta3n 687) in February 2025
-- Demonstrates cross-system data harmonization (VistA → Cerner)
-- =====================================================

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- =====================================================
-- Section 1: Demographics (VeteranMill.SPerson)
-- =====================================================
PRINT 'Inserting demographics for Alananah Thompson (CDWWork2)...';
GO

SET IDENTITY_INSERT VeteranMill.SPerson ON;
GO

INSERT INTO VeteranMill.SPerson (
    PersonSID,
    PatientICN,
    LastName,
    FirstName,
    MiddleName,
    BirthDate,
    Gender,
    SSN,
    HomePhone,
    Email,
    StreetAddress,
    City,
    State,
    ZipCode,
    IsActive,
    CreatedDate,
    LastUpdatedDate
)
VALUES (
    3002,                               -- PersonSID (CDWWork2 identifier)
    'ICN200002',                        -- Shared ICN with CDWWork
    'Thompson',
    'Alananah',
    'Marie',
    '1966-08-22',                       -- Age 59
    'F',
    '200-00-1002',
    '509-555-3002',
    'alananah.thompson@example.com',
    '5678 Walla Walla Blvd',
    'Walla Walla',
    'WA',
    '99362',
    1,                                  -- Active
    '2025-02-01 09:00:00',             -- Enrolled at Walla Walla in February 2025
    '2025-02-01 09:00:00'
);

SET IDENTITY_INSERT VeteranMill.SPerson OFF;
GO
PRINT '  ✓ Demographics inserted (PersonSID 3002)';
GO

-- =====================================================
-- Section 2: Encounters (EncMill.Encounter)
-- =====================================================
PRINT 'Inserting encounters for Alananah Thompson (CDWWork2)...';
GO

SET IDENTITY_INSERT EncMill.Encounter ON;
GO

-- Encounter 1: Initial enrollment visit (2025-02-15)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    6001, 3002, 'ICN200002', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2025-02-15 11:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Jennifer Davis', 1, '2025-02-15 11:00:00'
);

-- Encounter 2: Mid-year follow-up (2025-08-15)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    6002, 3002, 'ICN200002', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2025-08-15 11:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Jennifer Davis', 1, '2025-08-15 11:00:00'
);

-- Encounter 3: 2026-Q1 follow-up (2026-02-01)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    6003, 3002, 'ICN200002', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2026-02-01 11:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Jennifer Davis', 1, '2026-02-01 11:00:00'
);

SET IDENTITY_INSERT EncMill.Encounter OFF;
GO
PRINT '    3 encounters inserted (all outpatient)';
GO

-- =====================================================
-- =====================================================
-- Section 3: Vitals (VitalMill.VitalResult)
-- =====================================================
PRINT 'Inserting vitals for Alananah Thompson (CDWWork2)...';
GO

SET IDENTITY_INSERT VitalMill.VitalResult ON;
GO

-- 2025-Q1 (2025-02-15) - Initial visit
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES
(6001, 6001, 3002, 'ICN200002',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '128/78', NULL, 128, 78,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2025-02-15 11:00:00', '2025-02-15 11:01:00',
 'Primary Care Clinic', '687', 1),
(6002, 6001, 3002, 'ICN200002',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '158', 158.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2025-02-15 11:00:00', '2025-02-15 11:01:00',
 'Primary Care Clinic', '687', 1);

-- 2025-Q3 (2025-08-15)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES
(6003, 6002, 3002, 'ICN200002',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '125/75', NULL, 125, 75,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2025-08-15 11:00:00', '2025-08-15 11:01:00',
 'Primary Care Clinic', '687', 1),
(6004, 6002, 3002, 'ICN200002',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '160', 160.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2025-08-15 11:00:00', '2025-08-15 11:01:00',
 'Primary Care Clinic', '687', 1);

-- 2026-Q1 (2026-02-01) - Most recent
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES
(6005, 6003, 3002, 'ICN200002',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '124/76', NULL, 124, 76,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2026-02-01 11:00:00', '2026-02-01 11:01:00',
 'Primary Care Clinic', '687', 1),
(6006, 6003, 3002, 'ICN200002',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '159', 159.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2026-02-01 11:00:00', '2026-02-01 11:01:00',
 'Primary Care Clinic', '687', 1);

SET IDENTITY_INSERT VitalMill.VitalResult OFF;
GO
PRINT '    6 vital signs inserted (triannual 2025-2026)';
GO

-- =====================================================
-- Section 4: Problems (EncMill.ProblemList)
-- =====================================================
PRINT 'Inserting problems for Alananah Thompson (CDWWork2)...';
GO

INSERT INTO EncMill.ProblemList (
    PatientKey, PatientICN, FacilityCode, ProblemID, DiagnosisCode, DiagnosisDescription,
    ClinicalTermCode, ClinicalTermDescription, StatusCode, OnsetDateTime, RecordDateTime,
    LastUpdateDateTime, ResolvedDateTime, ResponsibleProviderID, ResponsibleProviderName, RecordingLocation,
    ServiceConnectedFlag, AcuteFlag, ChronicFlag, CreatedByUserID, CreatedByUserName, CreatedDateTime
)
VALUES
-- Problem 1: Type 2 Diabetes Mellitus
(3002, 'ICN200002', 687, 'C3002-1', 'E11.9', 'Type 2 diabetes mellitus without complications', '44054006', 'Type 2 diabetes mellitus', 'A', '2016-02-10 00:00:00', '2016-02-10 10:30:00', '2025-02-01 09:00:00', NULL, 30004, 'Davis, Jennifer MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30004, 'Davis, Jennifer MD', '2016-02-10 10:30:00'),
-- Problem 2: Personal History of Breast Cancer (In Remission)
(3002, 'ICN200002', 687, 'C3002-2', 'Z85.3', 'Personal history of malignant neoplasm of breast', '429740004', 'Personal history of breast cancer', 'A', '2018-03-15 00:00:00', '2018-03-15 14:15:00', '2025-02-01 09:00:00', NULL, 30005, 'Martinez, Carlos MD', 'Walla Walla VAMC Oncology', 'Y', 'N', 'Y', 30005, 'Martinez, Carlos MD', '2018-03-15 14:15:00'),
-- Problem 3: Hypertension
(3002, 'ICN200002', 687, 'C3002-3', 'I10', 'Essential (primary) hypertension', '38341003', 'Essential hypertension', 'A', '2016-05-20 00:00:00', '2016-05-20 09:45:00', '2025-02-01 09:00:00', NULL, 30004, 'Davis, Jennifer MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30004, 'Davis, Jennifer MD', '2016-05-20 09:45:00'),
-- Problem 4: Hyperlipidemia
(3002, 'ICN200002', 687, 'C3002-4', 'E78.5', 'Hyperlipidemia, unspecified', '267036007', 'Dyslipidemia', 'A', '2016-08-10 00:00:00', '2016-08-10 11:00:00', '2025-02-01 09:00:00', NULL, 30004, 'Davis, Jennifer MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30004, 'Davis, Jennifer MD', '2016-08-10 11:00:00'),
-- Problem 5: GERD
(3002, 'ICN200002', 687, 'C3002-5', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', '235595009', 'Gastroesophageal reflux disease', 'A', '2019-04-12 00:00:00', '2019-04-12 10:15:00', '2025-02-01 09:00:00', NULL, 30004, 'Davis, Jennifer MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30004, 'Davis, Jennifer MD', '2019-04-12 10:15:00'),
-- Problem 6: Osteoarthritis
(3002, 'ICN200002', 687, 'C3002-6', 'M19.90', 'Unspecified osteoarthritis, unspecified site', '396275006', 'Osteoarthritis', 'A', '2020-06-15 00:00:00', '2020-06-15 14:30:00', '2025-02-01 09:00:00', NULL, 30006, 'Brown, Michael MD', 'Walla Walla VAMC Rheumatology', 'Y', 'N', 'Y', 30006, 'Brown, Michael MD', '2020-06-15 14:30:00'),
-- Problem 7: Tinnitus (Service Connected 10%)
(3002, 'ICN200002', 687, 'C3002-7', 'H93.11', 'Tinnitus, right ear', '60862001', 'Tinnitus', 'A', '2012-08-20 00:00:00', '2012-08-20 10:00:00', '2025-02-01 09:00:00', NULL, 30004, 'Davis, Jennifer MD', 'Walla Walla VAMC Audiology', 'Y', 'N', 'Y', 30004, 'Davis, Jennifer MD', '2012-08-20 10:00:00');

GO
PRINT '    7 problems inserted (Charlson Index = 2)';
GO

-- =====================================================
-- Section 5: Family History (EncMill.FamilyHistory)
-- =====================================================
PRINT 'Inserting family history for Alananah Thompson (CDWWork2)...';
GO

INSERT INTO EncMill.FamilyHistory (
    EncounterSID, PersonSID, PatientICN, Sta3n,
    RelationshipCodeSID, ConditionCodeSID, StatusCodeSID,
    FamilyMemberName, FamilyMemberAge, OnsetAgeYears, NotedDateTime,
    DocumentedBy, CommentText, IsActive
)
VALUES
-- Brother with metabolic risk (cross-patient context)
(6002, 3002, 'ICN200002', '687',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'BROTHER'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'T2DM'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
 'Bailey Thompson', 62, 55, '2025-08-15 11:12:00',
 'Dr. Jennifer Davis', 'Brother with type 2 diabetes and chronic kidney disease.', 1),
-- Maternal hypertension history
(6003, 3002, 'ICN200002', '687',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'MOTHER'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'HTN'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
 'Mother', NULL, 49, '2026-02-01 11:14:00',
 'Dr. Jennifer Davis', 'Maternal hypertension documented.', 1);
GO
PRINT '    2 family-history records inserted';
GO

-- =====================================================
-- COMPLETION SUMMARY
-- =====================================================
PRINT '';
PRINT '==========================================';
PRINT 'ALANANAH THOMPSON CDWWork2 DATA COMPLETE';
PRINT '==========================================';
PRINT 'Patient: Alananah Marie Thompson';
PRINT 'ICN: ICN200002 (same as CDWWork)';
PRINT 'PersonSID: 3002 (CDWWork2 identifier)';
PRINT 'Facility: 687 (Walla Walla VAMC)';
PRINT 'Period: 2025-02-01 to 2026-02-09 (1 year)';
PRINT 'Demographics: 1 record';
PRINT 'Vitals: 6 records (triannual 2025-2026)';
PRINT 'Encounters: 3 records (all outpatient)';
PRINT 'Problems: 7 records (Charlson=2)';
PRINT 'Family History: 2 records';
PRINT 'Purpose: Demonstrate cross-system harmonization (VistA → Cerner)';
PRINT '==========================================';
GO
