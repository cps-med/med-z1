/*
|--------------------------------------------------------------------------------
| Insert: Dim.PatientRecordFlag.sql
|--------------------------------------------------------------------------------
| Insert sample data into table:  Dim.PatientRecordFlag
|
| Flag definitions for National (Category I) and Local (Category II) flags
| Source: VistA files #26.15 (National) and #26.11 (Local)
|--------------------------------------------------------------------------------
*/

PRINT '==== Dim.PatientRecordFlag ====';
GO

-- set the active database
USE CDWWork;
GO

-- Insert common National (Category I) and Local (Category II) flags
INSERT INTO Dim.PatientRecordFlag
(
    FlagName, FlagType, FlagCategory, FlagSourceType, NationalFlagIEN, LocalFlagIEN, ReviewFrequencyDays, ReviewNotificationDays, IsActive
)
VALUES
    -- Category I (National) Flags
    ('HIGH RISK FOR SUICIDE', 'CLINICAL', 'I', 'N', 1, NULL, 90, 7, 1),
    ('BEHAVIORAL', 'BEHAVIORAL', 'I', 'N', 2, NULL, 730, 30, 1),
    ('CRISIS NOTE', 'CLINICAL', 'I', 'N', 3, NULL, 180, 14, 1),
    ('VIOLENCE PREVENTION', 'BEHAVIORAL', 'I', 'N', 4, NULL, 365, 30, 1),
    ('COMMUNICABLE DISEASE', 'CLINICAL', 'I', 'N', 5, NULL, 365, 30, 1),
    ('DISRUPTIVE BEHAVIOR', 'BEHAVIORAL', 'I', 'N', 6, NULL, 365, 30, 1),

    -- Category II (Local) Flags
    ('RESEARCH STUDY', 'RESEARCH', 'II', 'L', NULL, 5, 365, 30, 1),
    ('DRUG SEEKING BEHAVIOR', 'BEHAVIORAL', 'II', 'L', NULL, 6, 180, 14, 1),
    ('ELOPEMENT RISK', 'CLINICAL', 'II', 'L', NULL, 7, 90, 7, 1),
    ('PATIENT ADVOCATE REFERRAL', 'ADMINISTRATIVE', 'II', 'L', NULL, 8, 365, 30, 1),
    ('SPECIAL HANDLING REQUIRED', 'ADMINISTRATIVE', 'II', 'L', NULL, 9, 180, 14, 1),
    ('COMBAT VETERAN PTSD', 'CLINICAL', 'II', 'L', NULL, 10, 180, 14, 1),
    ('PALLIATIVE CARE', 'CLINICAL', 'II', 'L', NULL, 11, 30, 7, 1),  -- Added 2026-02-04 for end-of-life care tracking
    ('DIABETIC PATIENT', 'CLINICAL', 'II', 'L', NULL, 12, 90, 7, 1),  -- Added 2026-02-09 for diabetes care management
    ('CANCER HISTORY', 'CLINICAL', 'II', 'L', NULL, 13, 365, 30, 1);  -- Added 2026-02-09 for cancer survivor follow-up
GO
