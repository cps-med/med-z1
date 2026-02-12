-- EncMill.FamilyHistory - Cerner-style family-history mock data
-- Includes adult/chronic and pediatric-pattern family-history entries

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting EncMill.FamilyHistory records...';
GO

INSERT INTO EncMill.FamilyHistory (
    EncounterSID, PersonSID, PatientICN, Sta3n,
    RelationshipCodeSID, ConditionCodeSID, StatusCodeSID,
    FamilyMemberName, FamilyMemberAge, OnsetAgeYears, NotedDateTime,
    DocumentedBy, CommentText, IsActive
)
VALUES
    -- Adam Dooree (PersonSID 2001, Portland 648)
    (3002, 2001, 'ICN100001', '648',
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'MOTHER'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'T2DM'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
     'Mother', 68, 51, '2024-07-22 10:40:00', 'Dr. Michael Wong', 'Mother has long-standing diabetes.', 1),

    (3003, 2001, 'ICN100001', '648',
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'FATHER'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'CAD'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'RESOLVED'),
     'Father', NULL, 59, '2024-08-10 14:15:00', 'Dr. Jennifer Martinez', 'Father deceased after coronary disease complications.', 1),

    (3008, 2001, 'ICN100001', '648',
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'SON'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'ASTHMA'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
     'Son', 12, 5, '2024-12-10 08:18:00', 'Dr. Sarah Chen', 'Pediatric pattern: son with childhood asthma.', 1),

    -- Alexander Aminor (PersonSID 2010, Seattle 663)
    (3012, 2010, 'ICN100010', '663',
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'SISTER'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'BREAST_CA'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
     'Sister', 57, 49, '2024-09-25 14:40:00', 'Dr. Emily Rodriguez', 'Sister treated for breast cancer.', 1),

    (3013, 2010, 'ICN100010', '663',
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'MOTHER'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'HTN'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
     'Mother', 80, 45, '2024-10-08 09:10:00', 'Dr. Thomas Lee', 'Maternal hypertension documented.', 1),

    (3016, 2010, 'ICN100010', '663',
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'DAUGHTER'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'ADHD'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'ACTIVE'),
     'Daughter', 9, 7, '2024-11-20 13:12:00', 'Dr. Emily Rodriguez', 'Pediatric pattern: daughter with ADHD diagnosis.', 1),

    (3018, 2010, 'ICN100010', '663',
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_RELATIONSHIP' AND Code = 'PAT_GRANDFATHER'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_CONDITION' AND Code = 'STROKE'),
     (SELECT CodeValueSID FROM NDimMill.CodeValue WHERE CodeSet = 'FAMILY_HISTORY_STATUS' AND Code = 'RESOLVED'),
     'Paternal Grandfather', NULL, 72, '2024-12-18 09:56:00', 'Dr. Emily Rodriguez', 'Paternal grandfather had stroke history.', 1);
GO

PRINT 'Inserted family-history records:';
SELECT COUNT(*) AS CernerFamilyHistoryCount FROM EncMill.FamilyHistory;
GO

PRINT 'Family-history records by patient:';
SELECT PatientICN, COUNT(*) AS EntryCount
FROM EncMill.FamilyHistory
GROUP BY PatientICN
ORDER BY EntryCount DESC, PatientICN;
GO
