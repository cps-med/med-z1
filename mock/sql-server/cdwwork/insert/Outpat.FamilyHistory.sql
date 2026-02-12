-- Outpat.FamilyHistory - VistA-style family history mock data
-- Includes adult/chronic and pediatric-pattern family-history entries

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting Outpat.FamilyHistory records...';
GO

INSERT INTO Outpat.FamilyHistory (
    PatientSID, PatientICN, Sta3n, FamilyRelationshipSID, FamilyConditionSID,
    FamilyMemberGender, OnsetAgeYears, DeceasedFlag, ClinicalStatus,
    RecordedDateTime, EnteredDateTime, ProviderSID, LocationSID, CommentText, IsActive
)
VALUES
    -- ICN100001 (Adam Dooree)
    (1001, 'ICN100001', 508,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'MOTHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'T2DM'),
     'F', 52, 'N', 'ACTIVE', '2024-11-01 09:20:00', '2024-11-01 09:21:00', 11003, NULL, 'Mother diagnosed in early 50s.', 'Y'),
    (1001, 'ICN100001', 508,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'FATHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'MI'),
     'M', 61, 'Y', 'RESOLVED', '2024-11-01 09:22:00', '2024-11-01 09:23:00', 11001, NULL, 'Father deceased from myocardial infarction.', 'Y'),

    -- ICN100002 (Barry Miifaa)
    (1002, 'ICN100002', 508,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'SISTER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'BREAST_CA'),
     'F', 44, 'N', 'ACTIVE', '2024-12-12 10:10:00', '2024-12-12 10:11:00', 11010, NULL, 'Sister treated for early stage breast cancer.', 'Y'),
    (1002, 'ICN100002', 508,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'MAT_GRANDFATHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'STROKE'),
     'M', 73, 'Y', 'RESOLVED', '2024-12-12 10:12:00', '2024-12-12 10:13:00', 11010, NULL, 'Maternal grandfather had stroke in his 70s.', 'Y'),

    -- ICN100005 (Edward Dooree)
    (1005, 'ICN100005', 508,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'SON'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'ASTHMA'),
     'M', 6, 'N', 'ACTIVE', '2025-01-08 14:00:00', '2025-01-08 14:01:00', 11002, NULL, 'Childhood asthma reported for son.', 'Y'),
    (1005, 'ICN100005', 508,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'DAUGHTER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'ADHD'),
     'F', 8, 'N', 'ACTIVE', '2025-01-08 14:02:00', '2025-01-08 14:03:00', 11013, NULL, 'Daughter diagnosed during elementary school.', 'Y'),

    -- ICN100006 (Francine Miifaa)
    (1006, 'ICN100006', 508,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'BROTHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'SUBSTANCE_USE'),
     'M', 23, 'N', 'ACTIVE', '2024-10-19 11:30:00', '2024-10-19 11:31:00', 11013, NULL, 'Brother with long-standing alcohol use disorder.', 'Y'),

    -- ICN100007 (Adam Amajor)
    (1007, 'ICN100007', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'FATHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'ALZHEIMERS'),
     'M', 78, 'Y', 'RESOLVED', '2024-09-20 09:15:00', '2024-09-20 09:16:00', 11005, NULL, 'Father had progressive dementia late in life.', 'Y'),
    (1007, 'ICN100007', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'PAT_GRANDMOTHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'COLON_CA'),
     'F', 69, 'Y', 'RESOLVED', '2024-09-20 09:17:00', '2024-09-20 09:18:00', 11008, NULL, 'Paternal grandmother with colon cancer history.', 'Y'),

    -- ICN100010 (Alexander Aminor)
    (1010, 'ICN100010', 552,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'MOTHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'HTN'),
     'F', 46, 'N', 'ACTIVE', '2024-12-02 15:10:00', '2024-12-02 15:11:00', 12004, NULL, 'Maternal history of hypertension.', 'Y'),
    (1010, 'ICN100010', 552,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'SON'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'AUTISM'),
     'M', 4, 'N', 'ACTIVE', '2024-12-02 15:12:00', '2024-12-02 15:13:00', 12004, NULL, 'Son has autism spectrum disorder diagnosis.', 'Y'),

    -- Thompson siblings - historical VistA-era family history (Bay Pines, Sta3n 516)
    (2001, 'ICN200001', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'SISTER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'BREAST_CA'),
     'F', 46, 'N', 'ACTIVE', '2018-07-12 10:05:00', '2018-07-12 10:06:00', 1001, NULL, 'Twin sister with breast cancer history in remission.', 'Y'),
    (2001, 'ICN200001', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'FATHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'CAD'),
     'M', 58, 'Y', 'RESOLVED', '2018-07-12 10:07:00', '2018-07-12 10:08:00', 1001, NULL, 'Father had coronary artery disease.', 'Y'),

    (2002, 'ICN200002', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'BROTHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'T2DM'),
     'M', 55, 'N', 'ACTIVE', '2017-04-22 13:10:00', '2017-04-22 13:11:00', 1003, NULL, 'Brother with type 2 diabetes and CKD.', 'Y'),
    (2002, 'ICN200002', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'MOTHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'HTN'),
     'F', 49, 'N', 'ACTIVE', '2017-04-22 13:12:00', '2017-04-22 13:13:00', 1003, NULL, 'Maternal hypertension history.', 'Y'),

    (2003, 'ICN200003', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'FATHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'COLON_CA'),
     'M', 61, 'Y', 'RESOLVED', '2019-06-10 09:20:00', '2019-06-10 09:21:00', 1001, NULL, 'Father had colon cancer; early screening advised.', 'Y'),
    (2003, 'ICN200003', 516,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'MOTHER'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'HTN'),
     'F', 52, 'N', 'ACTIVE', '2019-06-10 09:22:00', '2019-06-10 09:23:00', 1001, NULL, 'Mother with chronic hypertension.', 'Y'),

    -- ICN100016 (Marcus Johnson)
    (1016, '1016V123456', 688,
     (SELECT FamilyRelationshipSID FROM Dim.FamilyRelationship WHERE RelationshipCode = 'UNKNOWN'),
     (SELECT FamilyConditionSID FROM Dim.FamilyCondition WHERE ConditionCode = 'NONE_REPORTED'),
     'U', NULL, 'U', 'UNKNOWN', '2025-01-16 08:45:00', '2025-01-16 08:46:00', 12007, NULL, 'Patient unsure of biological family history.', 'Y');
GO

PRINT 'Inserted family-history records:';
SELECT COUNT(*) AS FamilyHistoryCount FROM Outpat.FamilyHistory;
GO

PRINT 'Family-history records by patient:';
SELECT PatientICN, COUNT(*) AS EntryCount
FROM Outpat.FamilyHistory
GROUP BY PatientICN
ORDER BY EntryCount DESC, PatientICN;
GO
