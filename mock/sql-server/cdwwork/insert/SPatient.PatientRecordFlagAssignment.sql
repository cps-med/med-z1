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

-- Ensure QUOTED_IDENTIFIER is ON for tables with filtered indexes
SET QUOTED_IDENTIFIER ON;
GO

-- Sample assignments for several patients
-- PatientSID values: 1001-1036 (36 total patients)
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
    -- Patient 1001: Active High Risk for Suicide flag (Cat I, CURRENT status)
    (1001, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-11-15 09:30:00', NULL,
     '518', '518', '518', 90, 7, '2025-01-15 10:00:00', '2025-04-15 10:00:00'),

    -- Patient 1002: Inactive Behavioral flag (Cat I, resolved)
    (1002, 2, 'BEHAVIORAL', 'I', 'N', 2, NULL,
     0, 'INACTIVE', '2023-08-01 14:00:00', '2024-03-10 11:45:00',
     '663', '663', '663', 730, 30, '2024-02-01 09:00:00', NULL),

    -- Patient 1003: Active Violence Prevention flag (Cat I, CURRENT status)
    (1003, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-06-20 13:15:00', NULL,
     '528', '528', '528', 365, 30, '2024-12-01 14:00:00', '2025-06-20 14:00:00'),

    -- Patient 1005: Active Research Study flag (Cat II local, CURRENT status)
    (1005, 7, 'RESEARCH STUDY', 'II', 'L', NULL, 5,
     1, 'ACTIVE', '2024-09-10 08:00:00', NULL,
     '442', '442', '442', 365, 30, NULL, '2025-09-10 08:00:00'),

    -- Patient 1007: Active Drug Seeking Behavior (Cat II local, DUE SOON - review in 10 days)
    (1007, 8, 'DRUG SEEKING BEHAVIOR', 'II', 'L', NULL, 6,
     1, 'ACTIVE', '2024-06-15 16:30:00', NULL,
     '589', '589', '589', 180, 14, NULL, '2025-12-17 16:30:00'),

    -- Patient 1009: Active Crisis Note (Cat I, OVERDUE for review)
    (1009, 3, 'CRISIS NOTE', 'I', 'N', 3, NULL,
     1, 'ACTIVE', '2024-05-20 10:00:00', NULL,
     '640', '640', '640', 180, 14, '2024-08-15 09:00:00', '2024-11-15 09:00:00'),

    -- Patient 1010: Multiple flags (both active)
    -- Flag 1: High Risk for Suicide (Cat I, CURRENT)
    (1010, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-07-22 11:00:00', NULL,
     '640', '640', '640', 90, 7, '2024-12-05 09:30:00', '2025-03-05 09:30:00'),

    -- Patient 1010: Flag 2: Violence Prevention (Cat I, CURRENT)
    (1010, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-07-22 11:15:00', NULL,
     '640', '640', '640', 365, 30, NULL, '2025-07-22 11:15:00'),

    -- Patient 1012: Active Elopement Risk (Cat II local, DUE SOON)
    (1012, 9, 'ELOPEMENT RISK', 'II', 'L', NULL, 7,
     1, 'ACTIVE', '2024-09-20 14:30:00', NULL,
     '528', '528', '528', 90, 7, NULL, '2025-12-19 14:30:00'),

    -- Patient 1014: Active Disruptive Behavior (Cat I, CURRENT)
    (1014, 6, 'DISRUPTIVE BEHAVIOR', 'I', 'N', 6, NULL,
     1, 'ACTIVE', '2024-08-10 13:00:00', NULL,
     '688', '688', '688', 365, 30, NULL, '2025-08-10 13:00:00'),

    -- Patient 1016: Inactive Patient Advocate Referral (Cat II local, resolved)
    (1016, 10, 'PATIENT ADVOCATE REFERRAL', 'II', 'L', NULL, 8,
     0, 'INACTIVE', '2024-01-15 09:00:00', '2024-06-20 10:30:00',
     '663', '663', '663', 365, 30, '2024-04-10 09:00:00', NULL),

    -- Patient 1018: Active Communicable Disease (Cat I, CURRENT)
    (1018, 5, 'COMMUNICABLE DISEASE', 'I', 'N', 5, NULL,
     1, 'ACTIVE', '2024-10-05 08:30:00', NULL,
     '512', '512', '512', 365, 30, NULL, '2025-10-05 08:30:00'),

    -- Patient 1020: Active Special Handling Required (Cat II local, CURRENT)
    (1020, 11, 'SPECIAL HANDLING REQUIRED', 'II', 'L', NULL, 9,
     1, 'ACTIVE', '2024-11-01 10:00:00', NULL,
     '552', '552', '552', 180, 14, NULL, '2025-05-01 10:00:00'),

    -- Patient 1022: Active Combat Veteran PTSD (Cat II local, DUE SOON)
    (1022, 12, 'COMBAT VETERAN PTSD', 'II', 'L', NULL, 10,
     1, 'ACTIVE', '2024-06-25 15:00:00', NULL,
     '578', '578', '578', 180, 14, NULL, '2025-12-23 15:00:00'),

    -- Patient 1024: Inactive High Risk for Suicide (Cat I, successfully resolved)
    (1024, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     0, 'INACTIVE', '2024-03-10 11:00:00', '2024-09-15 10:00:00',
     '660', '660', '660', 90, 7, '2024-06-10 09:00:00', NULL),

    -- Patient 1026: Margaret E Wilson - DECEASED (Palliative Care flag, inactivated at death)
    -- Added 2026-02-04 - Flag activated Oct 2024 when goals of care shifted to comfort, inactivated at death Dec 1, 2024
    (1026, 13, 'PALLIATIVE CARE', 'II', 'L', NULL, 11,
     0, 'INACTIVE', '2024-10-15 09:00:00', '2024-12-01 14:35:00',
     '508', '508', '508', 30, 7, '2024-11-15 10:00:00', NULL),

    -- Patient 1027: Robert J Anderson - DECEASED (High Risk for Suicide flag, active at time of death)
    -- Added 2026-02-04 - Flag activated after 2019 suicide attempt, remained active through death Nov 15, 2024
    (1027, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     0, 'INACTIVE', '2019-06-21 14:00:00', '2024-11-15 08:30:00',
     '528', '528', '528', 90, 7, '2024-11-14 15:00:00', NULL),

    -- Patient 1028: Active High Risk for Suicide (Cat I, CURRENT)
    (1028, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-10-20 09:00:00', NULL,
     '687', '687', '687', 90, 7, NULL, '2025-01-18 09:00:00'),

    -- Patient 1030: Active Violence Prevention (Cat I, CURRENT)
    (1030, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-09-15 11:30:00', NULL,
     '528', '528', '528', 365, 30, NULL, '2025-09-15 11:30:00'),

    -- Patient 1032: Inactive Drug Seeking Behavior (Cat II local, resolved)
    (1032, 8, 'DRUG SEEKING BEHAVIOR', 'II', 'L', NULL, 6,
     0, 'INACTIVE', '2024-02-20 16:00:00', '2024-08-25 15:30:00',
     '589', '589', '589', 180, 14, '2024-05-18 10:00:00', NULL);
GO
