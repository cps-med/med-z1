-----------------------------------------------------------------------
-- VitalMill.VitalResult.sql (INSERT)
-- Populate vital signs for demo patients at Cerner sites
-- Phase 2: Adam Dooree (Portland 648) and Alexander Aminor (Seattle 663)
-----------------------------------------------------------------------
-- Design Notes:
-- - Links to existing encounters (EncounterSID 3001-3008 Adam, 3011-3018 Alexander)
-- - References NDimMill.CodeValue for vital types and units
-- - Realistic clinical values for 45yo diabetic/HTN patient (Adam) and 59yo cardiac patient (Alexander)
-- - Date range: June-December 2024 (Adam), September-December 2024 (Alexander)
-- - Mix of vital types: BP, Pulse, Temperature, Weight
-----------------------------------------------------------------------

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
SET IDENTITY_INSERT VitalMill.VitalResult ON;
GO

PRINT 'Populating VitalMill.VitalResult with demo patient vitals...';
GO

-- =======================================================================
-- Adam Dooree Vitals at Portland VAMC (648)
-- =======================================================================
-- Background: 45yo male with Type 2 Diabetes and Hypertension
-- Expected vitals: Elevated BP (Stage 1 HTN), slightly elevated weight
-- Timeline: June 2024 - December 2024
-----------------------------------------------------------------------

-- Vital 1: Initial enrollment visit (BP elevated, needs med adjustment)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4001, 3001, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '138/88', NULL, 138, 88,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-06-15 08:45:00', '2024-06-15 08:46:00',
    'Primary Care Clinic', '648', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4002, 3001, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '82', 82.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-06-15 08:45:00', '2024-06-15 08:46:00',
    'Primary Care Clinic', '648', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4003, 3001, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
    '215', 215.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
    '2024-06-15 08:45:00', '2024-06-15 08:46:00',
    'Primary Care Clinic', '648', 1
);

-- Vital 2: Endocrinology follow-up (BP improving with med adjustment)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4004, 3002, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '132/84', NULL, 132, 84,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-07-22 10:30:00', '2024-07-22 10:31:00',
    'Endocrinology Clinic', '648', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4005, 3002, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '78', 78.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-07-22 10:30:00', '2024-07-22 10:31:00',
    'Endocrinology Clinic', '648', 1
);

-- Vital 3: Cardiology visit (BP well-controlled)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4006, 3003, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '128/80', NULL, 128, 80,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-08-10 14:15:00', '2024-08-10 14:16:00',
    'Cardiology Clinic', '648', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4007, 3003, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '74', 74.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-08-10 14:15:00', '2024-08-10 14:16:00',
    'Cardiology Clinic', '648', 1
);

-- Vital 4: Inpatient admission (diabetic crisis - elevated vitals)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4008, 3004, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '145/92', NULL, 145, 92,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-09-05 17:00:00', '2024-09-05 17:01:00',
    'Medical Ward 3B', '648', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4009, 3004, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '96', 96.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-09-05 17:00:00', '2024-09-05 17:01:00',
    'Medical Ward 3B', '648', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4010, 3004, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='TEMP'), 'Temperature',
    '98.8', 98.8, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='DEGF'), '°F',
    '2024-09-05 17:00:00', '2024-09-05 17:01:00',
    'Medical Ward 3B', '648', 1
);

-- Vital 5: Post-discharge follow-up (vitals normalizing)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4011, 3005, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '130/82', NULL, 130, 82,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-09-18 09:45:00', '2024-09-18 09:46:00',
    'Primary Care Clinic', '648', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4012, 3005, 2001, 'ICN100001',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
    '210', 210.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
    '2024-09-18 09:45:00', '2024-09-18 09:46:00',
    'Primary Care Clinic', '648', 1
);

PRINT '  - Inserted 12 vitals for Adam Dooree at Portland VAMC (648)';

-- =======================================================================
-- Alexander Aminor Vitals at Seattle VAMC (663)
-- =======================================================================
-- Background: 59yo male post-Vietnam veteran with cardiac history
-- Expected vitals: Generally stable, occasional elevated BP
-- Timeline: September 2024 - December 2024
-----------------------------------------------------------------------

-- Vital 1: Initial enrollment visit
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4013, 3011, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '135/86', NULL, 135, 86,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-09-10 10:30:00', '2024-09-10 10:31:00',
    'Primary Care Clinic', '663', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4014, 3011, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '72', 72.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-09-10 10:30:00', '2024-09-10 10:31:00',
    'Primary Care Clinic', '663', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4015, 3011, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='WEIGHT'), 'Weight',
    '185', 185.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='LBS'), 'lbs',
    '2024-09-10 10:30:00', '2024-09-10 10:31:00',
    'Primary Care Clinic', '663', 1
);

-- Vital 2: Cardiology specialty visit
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4016, 3013, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '130/80', NULL, 130, 80,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-10-08 09:15:00', '2024-10-08 09:16:00',
    'Cardiology Clinic', '663', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4017, 3013, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '68', 68.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-10-08 09:15:00', '2024-10-08 09:16:00',
    'Cardiology Clinic', '663', 1
);

-- Vital 3: Inpatient admission for chest pain evaluation
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4018, 3014, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '142/88', NULL, 142, 88,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-10-22 18:45:00', '2024-10-22 18:46:00',
    'Cardiac Care Unit', '663', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4019, 3014, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '88', 88.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-10-22 18:45:00', '2024-10-22 18:46:00',
    'Cardiac Care Unit', '663', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4020, 3014, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='TEMP'), 'Temperature',
    '98.6', 98.6, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='DEGF'), '°F',
    '2024-10-22 18:45:00', '2024-10-22 18:46:00',
    'Cardiac Care Unit', '663', 1
);

-- Vital 4: Post-discharge cardiology follow-up (stable)
INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4021, 3015, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='BP'), 'Blood Pressure',
    '128/78', NULL, 128, 78,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='MMHG'), 'mmHg',
    '2024-11-05 11:30:00', '2024-11-05 11:31:00',
    'Cardiology Clinic', '663', 1
);

INSERT INTO VitalMill.VitalResult (
    VitalResultSID, EncounterSID, PersonSID, PatientICN,
    VitalTypeCodeSID, VitalTypeName,
    ResultValue, NumericValue, Systolic, Diastolic,
    UnitCodeSID, UnitName,
    TakenDateTime, EnteredDateTime,
    LocationName, Sta3n, IsActive
)
VALUES (
    4022, 3015, 2010, 'ICN100010',
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='VITAL_TYPE' AND Code='PULSE'), 'Pulse',
    '70', 70.0, NULL, NULL,
    (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet='UNIT' AND Code='BPM'), 'bpm',
    '2024-11-05 11:30:00', '2024-11-05 11:31:00',
    'Cardiology Clinic', '663', 1
);

PRINT '  - Inserted 10 vitals for Alexander Aminor at Seattle VAMC (663)';

SET IDENTITY_INSERT VitalMill.VitalResult OFF;
GO

-- =======================================================================
-- Verification
-- =======================================================================

PRINT '';
PRINT 'Vital signs population complete:';
SELECT
    p.LastName + ', ' + p.FirstName AS PatientName,
    vr.PatientICN,
    vr.Sta3n,
    vr.VitalTypeName,
    vr.ResultValue,
    CONVERT(VARCHAR, vr.TakenDateTime, 120) AS TakenDateTime,
    vr.LocationName
FROM VitalMill.VitalResult vr
JOIN VeteranMill.SPerson p ON vr.PersonSID = p.PersonSID
ORDER BY p.PersonSID, vr.TakenDateTime;

PRINT '';
PRINT 'Vitals summary by patient:';
SELECT
    p.LastName + ', ' + p.FirstName AS PatientName,
    vr.PatientICN,
    vr.Sta3n,
    COUNT(*) AS VitalCount
FROM VitalMill.VitalResult vr
JOIN VeteranMill.SPerson p ON vr.PersonSID = p.PersonSID
GROUP BY p.LastName, p.FirstName, vr.PatientICN, vr.Sta3n
ORDER BY p.LastName;

PRINT '';
PRINT 'Total vitals inserted:';
SELECT COUNT(*) AS TotalVitals FROM VitalMill.VitalResult;
GO
