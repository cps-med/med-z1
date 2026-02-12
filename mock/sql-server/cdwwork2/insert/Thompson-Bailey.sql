-- =====================================================
-- Thompson-Bailey.sql - CDWWork2 (Corrected)
-- Patient: Bailey James Thompson
-- ICN: ICN200001, PersonSID: 3001
-- Complex Patient (Charlson Index = 5)
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
PRINT 'Inserting demographics for Bailey Thompson (CDWWork2)...';
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
    3001,                               -- PersonSID (CDWWork2 identifier)
    'ICN200001',                        -- Shared ICN with CDWWork
    'Thompson',
    'Bailey',
    'James',
    '1963-04-15',                       -- Age 62
    'M',
    '200-00-1001',
    '509-555-3001',
    'bailey.thompson@example.com',
    '1234 Walla Walla Ave',
    'Walla Walla',
    'WA',
    '99362',
    1,                                  -- Active
    '2025-02-01 08:30:00',             -- Enrolled at Walla Walla in February 2025
    '2025-02-01 08:30:00'
);

SET IDENTITY_INSERT VeteranMill.SPerson OFF;
GO
PRINT '    Demographics inserted (PersonSID 3001)';
GO

-- =====================================================
-- Section 2: Encounters (EncMill.Encounter)
-- =====================================================
PRINT 'Inserting encounters for Bailey Thompson (CDWWork2)...';
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
    5001, 3001, 'ICN200001', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2025-02-15 10:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Christine Baker', 1, '2025-02-15 10:00:00'
);

-- Encounter 2: Q2 follow-up (2025-05-15)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    5002, 3001, 'ICN200001', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2025-05-15 10:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Christine Baker', 1, '2025-05-15 10:00:00'
);

-- Encounter 3: Inpatient admission - chronic pain crisis (2025-07-10 to 2025-07-12)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, AdmitDate, DischargeDate,
    LocationName, LocationType, ProviderName, IsActive, CreatedDate
)
VALUES (
    5003, 3001, 'ICN200001', '687', 'Walla Walla VAMC',
    'INPATIENT', '2025-07-10 18:00:00', '2025-07-10 18:00:00', '2025-07-12 11:00:00',
    'Medical Ward 2B', 'WARD', 'Dr. Michael Chen', 1, '2025-07-10 18:00:00'
);

-- Encounter 4: Q3 follow-up (2025-08-15)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    5004, 3001, 'ICN200001', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2025-08-15 10:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Christine Baker', 1, '2025-08-15 10:00:00'
);

-- Encounter 5: Inpatient admission - COPD exacerbation (2025-10-08 to 2025-10-13)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, AdmitDate, DischargeDate,
    LocationName, LocationType, ProviderName, IsActive, CreatedDate
)
VALUES (
    5005, 3001, 'ICN200001', '687', 'Walla Walla VAMC',
    'INPATIENT', '2025-10-08 14:00:00', '2025-10-08 14:00:00', '2025-10-13 10:00:00',
    'Medical Ward 2B', 'WARD', 'Dr. Sarah Martinez', 1, '2025-10-08 14:00:00'
);

-- Encounter 6: Q4 follow-up (2025-11-15)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    5006, 3001, 'ICN200001', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2025-11-15 10:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Christine Baker', 1, '2025-11-15 10:00:00'
);

-- Encounter 7: 2026-Q1 follow-up (2026-02-01)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    5007, 3001, 'ICN200001', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2026-02-01 10:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Christine Baker', 1, '2026-02-01 10:00:00'
);

SET IDENTITY_INSERT EncMill.Encounter OFF;
GO
PRINT '    7 encounters inserted (5 outpatient, 2 inpatient)';
GO

-- =====================================================
-- =====================================================
-- Section 3: Vitals (VitalMill.VitalResult)
-- =====================================================
PRINT 'Inserting vitals for Bailey Thompson (CDWWork2)...';
GO

SET IDENTITY_INSERT VitalMill.VitalResult ON;
GO

-- 2025-Q1 (2025-02-15) - Initial visit at Walla Walla
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES
(5001, 5001, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '135/85', NULL, 135, 85,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2025-02-15 10:00:00', '2025-02-15 10:01:00',
 'Primary Care Clinic', '687', 1),
(5002, 5001, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
 '70', 70.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
 '2025-02-15 10:00:00', '2025-02-15 10:01:00',
 'Primary Care Clinic', '687', 1),
(5003, 5001, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '220', 220.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2025-02-15 10:00:00', '2025-02-15 10:01:00',
 'Primary Care Clinic', '687', 1);

-- 2025-Q2 (2025-05-15)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES
(5004, 5002, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '218', 218.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2025-05-15 10:00:00', '2025-05-15 10:01:00',
 'Primary Care Clinic', '687', 1),
(5005, 5002, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '132/82', NULL, 132, 82,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2025-05-15 10:00:00', '2025-05-15 10:01:00',
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
(5006, 5003, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '219', 219.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2025-08-15 10:00:00', '2025-08-15 10:01:00',
 'Primary Care Clinic', '687', 1),
(5007, 5003, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '130/80', NULL, 130, 80,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2025-08-15 10:00:00', '2025-08-15 10:01:00',
 'Primary Care Clinic', '687', 1);

-- 2025-Q4 (2025-11-15)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES
(5008, 5004, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '221', 221.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2025-11-15 10:00:00', '2025-11-15 10:01:00',
 'Primary Care Clinic', '687', 1),
(5009, 5004, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '134/84', NULL, 134, 84,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2025-11-15 10:00:00', '2025-11-15 10:01:00',
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
(5010, 5005, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '220', 220.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2026-02-01 10:00:00', '2026-02-01 10:01:00',
 'Primary Care Clinic', '687', 1),
(5011, 5005, 3001, 'ICN200001',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '133/82', NULL, 133, 82,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2026-02-01 10:00:00', '2026-02-01 10:01:00',
 'Primary Care Clinic', '687', 1);

SET IDENTITY_INSERT VitalMill.VitalResult OFF;
GO
PRINT '  ✓ 11 vital signs inserted (quarterly 2025-2026)';
GO

-- =====================================================
-- Section 4: Problems (EncMill.ProblemList)
-- =====================================================
PRINT 'Inserting problems for Bailey Thompson (CDWWork2)...';
GO

INSERT INTO EncMill.ProblemList (
    PatientKey, PatientICN, FacilityCode, ProblemID, DiagnosisCode, DiagnosisDescription,
    ClinicalTermCode, ClinicalTermDescription, StatusCode, OnsetDateTime, RecordDateTime,
    LastUpdateDateTime, ResolvedDateTime, ResponsibleProviderID, ResponsibleProviderName, RecordingLocation,
    ServiceConnectedFlag, AcuteFlag, ChronicFlag, CreatedByUserID, CreatedByUserName, CreatedDateTime
)
VALUES
-- Problem 1: PTSD (Service Connected 70%)
(3001, 'ICN200001', 687, 'C3001-1', 'F43.10', 'Post-traumatic stress disorder, unspecified', '47505003', 'Post-traumatic stress disorder', 'A', '2009-03-01 00:00:00', '2009-03-01 10:30:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Mental Health', 'Y', 'N', 'Y', 30001, 'Baker, Christine MD', '2009-03-01 10:30:00'),
-- Problem 2: Alcohol Dependence
(3001, 'ICN200001', 687, 'C3001-2', 'F10.20', 'Alcohol dependence, uncomplicated', '7200002', 'Alcoholism', 'A', '2010-02-01 00:00:00', '2010-02-01 14:15:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Mental Health', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2010-02-01 14:15:00'),
-- Problem 3: Major Depressive Disorder
(3001, 'ICN200001', 687, 'C3001-3', 'F33.1', 'Major depressive disorder, recurrent, moderate', '370143000', 'Major depressive disorder', 'A', '2010-06-01 00:00:00', '2010-06-01 09:45:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Mental Health', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2010-06-01 09:45:00'),
-- Problem 4: Chronic Lumbar Radiculopathy (Service Connected 40%)
(3001, 'ICN200001', 687, 'C3001-4', 'M54.16', 'Radiculopathy, lumbar region', '12867004', 'Lumbar radiculopathy', 'A', '2009-03-15 00:00:00', '2009-03-15 11:00:00', '2025-02-01 09:00:00', NULL, 30002, 'Chen, Michael MD', 'Walla Walla VAMC Pain Management', 'Y', 'N', 'Y', 30002, 'Chen, Michael MD', '2009-03-15 11:00:00'),
-- Problem 5: Type 2 Diabetes Mellitus
(3001, 'ICN200001', 687, 'C3001-5', 'E11.9', 'Type 2 diabetes mellitus without complications', '44054006', 'Type 2 diabetes mellitus', 'A', '2014-05-12 00:00:00', '2014-05-12 14:30:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2014-05-12 14:30:00'),
-- Problem 6: Essential Hypertension
(3001, 'ICN200001', 687, 'C3001-6', 'I10', 'Essential (primary) hypertension', '38341003', 'Essential hypertension', 'A', '2010-06-15 00:00:00', '2010-06-15 10:15:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2010-06-15 10:15:00'),
-- Problem 7: CKD Stage 3A
(3001, 'ICN200001', 687, 'C3001-7', 'N18.3', 'Chronic kidney disease, stage 3 (moderate)', '46177005', 'End stage renal disease', 'A', '2015-10-20 00:00:00', '2015-10-20 14:30:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Nephrology', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2015-10-20 14:30:00'),
-- Problem 8: Hyperlipidemia
(3001, 'ICN200001', 687, 'C3001-8', 'E78.5', 'Hyperlipidemia, unspecified', '267036007', 'Dyslipidemia', 'A', '2012-03-15 00:00:00', '2012-03-15 10:00:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2012-03-15 10:00:00'),
-- Problem 9: Obesity
(3001, 'ICN200001', 687, 'C3001-9', 'E66.9', 'Obesity, unspecified', '414915002', 'Obesity', 'A', '2010-06-15 00:00:00', '2010-06-15 10:30:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2010-06-15 10:30:00'),
-- Problem 10: GERD
(3001, 'ICN200001', 687, 'C3001-10', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', '235595009', 'Gastroesophageal reflux disease', 'A', '2010-12-01 00:00:00', '2010-12-01 09:30:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2010-12-01 09:30:00'),
-- Problem 11: Nicotine Dependence
(3001, 'ICN200001', 687, 'C3001-11', 'F17.210', 'Nicotine dependence, cigarettes, uncomplicated', '266919005', 'Nicotine dependence', 'A', '1982-06-15 00:00:00', '2010-06-15 10:45:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2010-06-15 10:45:00'),
-- Problem 12: COPD
(3001, 'ICN200001', 687, 'C3001-12', 'J44.1', 'Chronic obstructive pulmonary disease with (acute) exacerbation', '13645005', 'Chronic obstructive pulmonary disease', 'A', '2020-06-15 00:00:00', '2020-06-15 11:00:00', '2025-02-01 09:00:00', NULL, 30003, 'Martinez, Sarah MD', 'Walla Walla VAMC Pulmonary', 'N', 'N', 'Y', 30003, 'Martinez, Sarah MD', '2020-06-15 11:00:00'),
-- Problem 13: Tinnitus (Service Connected 10%)
(3001, 'ICN200001', 687, 'C3001-13', 'H93.11', 'Tinnitus, right ear', '60862001', 'Tinnitus', 'A', '2009-03-15 00:00:00', '2009-03-15 10:15:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Audiology', 'Y', 'N', 'Y', 30001, 'Baker, Christine MD', '2009-03-15 10:15:00'),
-- Problem 14: TBI Sequela (Service Connected 10%)
(3001, 'ICN200001', 687, 'C3001-14', 'S06.0X9S', 'Concussion with loss of consciousness of unspecified duration, sequela', '82271004', 'Injury of head', 'A', '2009-03-15 00:00:00', '2009-03-15 10:30:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Neurology', 'Y', 'N', 'Y', 30001, 'Baker, Christine MD', '2009-03-15 10:30:00'),
-- Problem 15: Insomnia
(3001, 'ICN200001', 687, 'C3001-15', 'G47.00', 'Insomnia, unspecified', '193462001', 'Insomnia', 'A', '2009-06-01 00:00:00', '2009-06-01 09:00:00', '2025-02-01 09:00:00', NULL, 30001, 'Baker, Christine MD', 'Walla Walla VAMC Mental Health', 'N', 'N', 'Y', 30001, 'Baker, Christine MD', '2009-06-01 09:00:00');

GO
PRINT '  ✓ 15 problems inserted (Charlson Index = 5)';
GO

-- =====================================================
-- Section 5: Family History (EncMill.FamilyHistory)
-- =====================================================
PRINT 'Inserting family history for Bailey Thompson (CDWWork2)...';
GO

INSERT INTO EncMill.FamilyHistory (
    EncounterSID, PersonSID, PatientICN, Sta3n,
    RelationshipCodeSID, ConditionCodeSID, StatusCodeSID,
    FamilyMemberName, FamilyMemberAge, OnsetAgeYears, NotedDateTime,
    DocumentedBy, CommentText, IsActive
)
VALUES
-- Update at Walla Walla: sister cancer history reconfirmed
(5006, 3001, 'ICN200001', '687',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'SISTER'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'BREAST_CA'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
 'Alananah Thompson', 59, 46, '2025-11-15 10:10:00',
 'Dr. Christine Baker', 'Twin sister with prior breast cancer; currently in remission.', 1),
-- Father cardiovascular history
(5007, 3001, 'ICN200001', '687',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'FATHER'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'CAD'),
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'RESOLVED'),
 'Father', NULL, 58, '2026-02-01 10:12:00',
 'Dr. Christine Baker', 'Father deceased with coronary artery disease history.', 1);
GO
PRINT '  ✓ 2 family-history records inserted';
GO

-- =====================================================
-- COMPLETION SUMMARY
-- =====================================================
PRINT '';
PRINT '========================================';
PRINT 'BAILEY THOMPSON CDWWork2 DATA COMPLETE';
PRINT '========================================';
PRINT 'Patient: Bailey James Thompson';
PRINT 'ICN: ICN200001 (same as CDWWork)';
PRINT 'PersonSID: 3001 (CDWWork2 identifier)';
PRINT 'Facility: 687 (Walla Walla VAMC)';
PRINT 'Period: 2025-02-01 to 2026-02-09 (1 year)';
PRINT 'Demographics: 1 record';
PRINT 'Vitals: 11 records (quarterly 2025-2026)';
PRINT 'Encounters: 7 records (5 outpatient, 2 inpatient)';
PRINT 'Problems: 15 records (Charlson=5)';
PRINT 'Family History: 2 records';
PRINT 'Purpose: Demonstrate cross-system harmonization (VistA → Cerner)';
PRINT '========================================';
GO
