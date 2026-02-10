-- =====================================================
-- Thompson-Joe.sql - CDWWork2 (Corrected)
-- Patient: Joe Michael Thompson
-- ICN: ICN200003, PersonSID: 3003
-- Healthy Control Patient (Charlson Index = 0)
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
PRINT 'Inserting demographics for Joe Thompson (CDWWork2)...';
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
    3003,                               -- PersonSID (CDWWork2 identifier)
    'ICN200003',                        -- Shared ICN with CDWWork
    'Thompson',
    'Joe',
    'Michael',
    '1970-05-10',                       -- Age 55
    'M',
    '200-00-1003',
    '509-555-3003',
    'joe.thompson@example.com',
    '9012 Walla Walla Way',
    'Walla Walla',
    'WA',
    '99362',
    1,                                  -- Active
    '2025-02-01 10:00:00',             -- Enrolled at Walla Walla in February 2025
    '2025-02-01 10:00:00'
);

SET IDENTITY_INSERT VeteranMill.SPerson OFF;
GO
PRINT '    Demographics inserted (PersonSID 3003)';
GO

-- =====================================================
-- Section 2: Encounters (EncMill.Encounter)
-- =====================================================
PRINT 'Inserting encounters for Joe Thompson (CDWWork2)...';
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
    7001, 3003, 'ICN200003', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2025-02-15 12:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Robert Taylor', 1, '2025-02-15 12:00:00'
);

-- Encounter 2: Annual follow-up (2026-02-01)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    7002, 3003, 'ICN200003', '687', 'Walla Walla VAMC',
    'OUTPATIENT', '2026-02-01 12:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Robert Taylor', 1, '2026-02-01 12:00:00'
);

SET IDENTITY_INSERT EncMill.Encounter OFF;
GO
PRINT '    2 encounters inserted (all outpatient)';
GO

-- =====================================================
-- =====================================================
-- Section 3: Vitals (VitalMill.VitalResult)
-- =====================================================
PRINT 'Inserting vitals for Joe Thompson (CDWWork2)...';
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
(7001, 7001, 3003, 'ICN200003',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '128/80', NULL, 128, 80,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2025-02-15 12:00:00', '2025-02-15 12:01:00',
 'Primary Care Clinic', '687', 1),
(7002, 7001, 3003, 'ICN200003',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '190', 190.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2025-02-15 12:00:00', '2025-02-15 12:01:00',
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
(7003, 7002, 3003, 'ICN200003',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
 '130/82', NULL, 130, 82,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
 '2026-02-01 12:00:00', '2026-02-01 12:01:00',
 'Primary Care Clinic', '687', 1),
(7004, 7002, 3003, 'ICN200003',
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
 '191', 191.0, NULL, NULL,
 (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
 '2026-02-01 12:00:00', '2026-02-01 12:01:00',
 'Primary Care Clinic', '687', 1);

SET IDENTITY_INSERT VitalMill.VitalResult OFF;
GO
PRINT '  ✓ 4 vital signs inserted (annual 2025-2026)';
GO

-- =====================================================
-- Section 4: Problems (EncMill.ProblemList)
-- =====================================================
PRINT 'Inserting problems for Joe Thompson (CDWWork2)...';
GO

INSERT INTO EncMill.ProblemList (
    PatientKey, PatientICN, FacilityCode, ProblemID, DiagnosisCode, DiagnosisDescription,
    ClinicalTermCode, ClinicalTermDescription, StatusCode, OnsetDateTime, RecordDateTime,
    LastUpdateDateTime, ResolvedDateTime, ResponsibleProviderID, ResponsibleProviderName, RecordingLocation,
    ServiceConnectedFlag, AcuteFlag, ChronicFlag, CreatedByUserID, CreatedByUserName, CreatedDateTime
)
VALUES
-- Problem 1: Hypertension (mild, well-controlled)
(3003, 'ICN200003', 687, 'C3003-1', 'I10', 'Essential (primary) hypertension', '38341003', 'Essential hypertension', 'A', '2015-01-15 00:00:00', '2015-01-15 10:30:00', '2025-02-01 09:00:00', NULL, 30007, 'Taylor, Robert MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30007, 'Taylor, Robert MD', '2015-01-15 10:30:00'),
-- Problem 2: Hyperlipidemia (mild, well-controlled)
(3003, 'ICN200003', 687, 'C3003-2', 'E78.5', 'Hyperlipidemia, unspecified', '267036007', 'Dyslipidemia', 'A', '2016-03-01 00:00:00', '2016-03-01 11:00:00', '2025-02-01 09:00:00', NULL, 30007, 'Taylor, Robert MD', 'Walla Walla VAMC Primary Care', 'N', 'N', 'Y', 30007, 'Taylor, Robert MD', '2016-03-01 11:00:00');

GO
PRINT '  ✓ 2 problems inserted (Charlson Index = 0)';
GO

-- =====================================================
-- COMPLETION SUMMARY
-- =====================================================
PRINT '';
PRINT '======================================';
PRINT 'JOE THOMPSON CDWWork2 DATA COMPLETE';
PRINT '======================================';
PRINT 'Patient: Joe Michael Thompson';
PRINT 'ICN: ICN200003 (same as CDWWork)';
PRINT 'PersonSID: 3003 (CDWWork2 identifier)';
PRINT 'Facility: 687 (Walla Walla VAMC)';
PRINT 'Period: 2025-02-01 to 2026-02-09 (1 year)';
PRINT 'Demographics: 1 record';
PRINT 'Vitals: 4 records (annual 2025-2026)';
PRINT 'Encounters: 2 records (all outpatient)';
PRINT 'Problems: 2 records (Charlson=0)';
PRINT 'Purpose: Demonstrate cross-system harmonization (VistA → Cerner)';
PRINT 'Profile: Healthy control patient';
PRINT '======================================';
GO
