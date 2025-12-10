/*
|--------------------------------------------------------------------------------
| Insert: SPatient.PatientRecordFlagAssignment.sql
|--------------------------------------------------------------------------------
| Insert sample data into table:  SPatient.PatientRecordFlagAssignment
|
| Sample patient flag assignments for testing med-z1 UI
| Covers ~16 patients out of 36 total patients
| Mix of National and Local flags, active and inactive states
|--------------------------------------------------------------------------------
*/

PRINT '==== SPatient.PatientRecordFlagAssignment ====';
GO

-- set the active database
USE CDWWork;
GO

-- Sample assignments for several patients
-- PatientSID values: 100001-100036 (36 total patients)
-- Assigning flags to ~16 patients to create realistic distribution
INSERT INTO SPatient.PatientRecordFlagAssignment
(
    PatientSID, PatientRecordFlagSID, FlagName, FlagCategory, FlagSourceType,
    NationalFlagIEN, LocalFlagIEN, IsActive, AssignmentStatus,
    AssignmentDateTime, InactivationDateTime,
    OwnerSiteSta3n, OriginatingSiteSta3n, LastUpdateSiteSta3n,
    ReviewFrequencyDays, ReviewNotificationDays, LastReviewDateTime, NextReviewDateTime
)
VALUES
    -- Patient 100001: Active High Risk for Suicide flag (Cat I, CURRENT status)
    (100001, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-11-15 09:30:00', NULL,
     '518', '518', '518', 90, 7, '2025-01-15 10:00:00', '2025-04-15 10:00:00'),

    -- Patient 100002: Inactive Behavioral flag (Cat I, resolved)
    (100002, 2, 'BEHAVIORAL', 'I', 'N', 2, NULL,
     0, 'INACTIVE', '2023-08-01 14:00:00', '2024-03-10 11:45:00',
     '663', '663', '663', 730, 30, '2024-02-01 09:00:00', NULL),

    -- Patient 100003: Active Violence Prevention flag (Cat I, CURRENT status)
    (100003, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-06-20 13:15:00', NULL,
     '528', '528', '528', 365, 30, '2024-12-01 14:00:00', '2025-06-20 14:00:00'),

    -- Patient 100005: Active Research Study flag (Cat II local, CURRENT status)
    (100005, 7, 'RESEARCH STUDY', 'II', 'L', NULL, 5,
     1, 'ACTIVE', '2024-09-10 08:00:00', NULL,
     '442', '442', '442', 365, 30, NULL, '2025-09-10 08:00:00'),

    -- Patient 100007: Active Drug Seeking Behavior (Cat II local, DUE SOON - review in 10 days)
    (100007, 8, 'DRUG SEEKING BEHAVIOR', 'II', 'L', NULL, 6,
     1, 'ACTIVE', '2024-06-15 16:30:00', NULL,
     '589', '589', '589', 180, 14, NULL, '2025-12-17 16:30:00'),

    -- Patient 100009: Active Crisis Note (Cat I, OVERDUE for review)
    (100009, 3, 'CRISIS NOTE', 'I', 'N', 3, NULL,
     1, 'ACTIVE', '2024-05-20 10:00:00', NULL,
     '640', '640', '640', 180, 14, '2024-08-15 09:00:00', '2024-11-15 09:00:00'),

    -- Patient 100010: Multiple flags (both active)
    -- Flag 1: High Risk for Suicide (Cat I, CURRENT)
    (100010, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-07-22 11:00:00', NULL,
     '640', '640', '640', 90, 7, '2024-12-05 09:30:00', '2025-03-05 09:30:00'),

    -- Patient 100010: Flag 2: Violence Prevention (Cat I, CURRENT)
    (100010, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-07-22 11:15:00', NULL,
     '640', '640', '640', 365, 30, NULL, '2025-07-22 11:15:00'),

    -- Patient 100012: Active Elopement Risk (Cat II local, DUE SOON)
    (100012, 9, 'ELOPEMENT RISK', 'II', 'L', NULL, 7,
     1, 'ACTIVE', '2024-09-20 14:30:00', NULL,
     '528', '528', '528', 90, 7, NULL, '2025-12-19 14:30:00'),

    -- Patient 100014: Active Disruptive Behavior (Cat I, CURRENT)
    (100014, 6, 'DISRUPTIVE BEHAVIOR', 'I', 'N', 6, NULL,
     1, 'ACTIVE', '2024-08-10 13:00:00', NULL,
     '688', '688', '688', 365, 30, NULL, '2025-08-10 13:00:00'),

    -- Patient 100016: Inactive Patient Advocate Referral (Cat II local, resolved)
    (100016, 10, 'PATIENT ADVOCATE REFERRAL', 'II', 'L', NULL, 8,
     0, 'INACTIVE', '2024-01-15 09:00:00', '2024-06-20 10:30:00',
     '663', '663', '663', 365, 30, '2024-04-10 09:00:00', NULL),

    -- Patient 100018: Active Communicable Disease (Cat I, CURRENT)
    (100018, 5, 'COMMUNICABLE DISEASE', 'I', 'N', 5, NULL,
     1, 'ACTIVE', '2024-10-05 08:30:00', NULL,
     '512', '512', '512', 365, 30, NULL, '2025-10-05 08:30:00'),

    -- Patient 100020: Active Special Handling Required (Cat II local, CURRENT)
    (100020, 11, 'SPECIAL HANDLING REQUIRED', 'II', 'L', NULL, 9,
     1, 'ACTIVE', '2024-11-01 10:00:00', NULL,
     '552', '552', '552', 180, 14, NULL, '2025-05-01 10:00:00'),

    -- Patient 100022: Active Combat Veteran PTSD (Cat II local, DUE SOON)
    (100022, 12, 'COMBAT VETERAN PTSD', 'II', 'L', NULL, 10,
     1, 'ACTIVE', '2024-06-25 15:00:00', NULL,
     '578', '578', '578', 180, 14, NULL, '2025-12-23 15:00:00'),

    -- Patient 100024: Inactive High Risk for Suicide (Cat I, successfully resolved)
    (100024, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     0, 'INACTIVE', '2024-03-10 11:00:00', '2024-09-15 10:00:00',
     '660', '660', '660', 90, 7, '2024-06-10 09:00:00', NULL),

    -- Patient 100026: Active Behavioral (Cat I, OVERDUE for review)
    (100026, 2, 'BEHAVIORAL', 'I', 'N', 2, NULL,
     1, 'ACTIVE', '2022-11-01 14:00:00', NULL,
     '668', '668', '668', 730, 30, '2023-05-15 10:00:00', '2024-10-30 10:00:00'),

    -- Patient 100028: Active High Risk for Suicide (Cat I, CURRENT)
    (100028, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-10-20 09:00:00', NULL,
     '687', '687', '687', 90, 7, NULL, '2025-01-18 09:00:00'),

    -- Patient 100030: Active Violence Prevention (Cat I, CURRENT)
    (100030, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-09-15 11:30:00', NULL,
     '528', '528', '528', 365, 30, NULL, '2025-09-15 11:30:00'),

    -- Patient 100032: Inactive Drug Seeking Behavior (Cat II local, resolved)
    (100032, 8, 'DRUG SEEKING BEHAVIOR', 'II', 'L', NULL, 6,
     0, 'INACTIVE', '2024-02-20 16:00:00', '2024-08-25 15:30:00',
     '589', '589', '589', 180, 14, '2024-05-18 10:00:00', NULL);
GO
