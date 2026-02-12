-- Dim.FamilyCondition - seed family-history conditions
-- Includes adult/chronic risk conditions and pediatric-pattern conditions

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting Dim.FamilyCondition values...';
GO

INSERT INTO Dim.FamilyCondition (
    ConditionCode, ConditionName, SNOMEDCode, ICD10Code, ConditionCategory, HereditaryRiskFlag, IsActive
)
VALUES
    -- Cardio/metabolic
    ('HTN', 'Hypertension', '38341003', 'I10', 'Cardio', 'Y', 'Y'),
    ('CAD', 'Coronary artery disease', '53741008', 'I25.10', 'Cardio', 'Y', 'Y'),
    ('MI', 'Myocardial infarction', '22298006', 'I21.9', 'Cardio', 'Y', 'Y'),
    ('STROKE', 'Cerebrovascular accident', '230690007', 'I63.9', 'Cardio', 'Y', 'Y'),
    ('T2DM', 'Type 2 diabetes mellitus', '44054006', 'E11.9', 'Metabolic', 'Y', 'Y'),
    ('HYPERLIPIDEMIA', 'Hyperlipidemia', '55822004', 'E78.5', 'Metabolic', 'Y', 'Y'),

    -- Cancer
    ('BREAST_CA', 'Breast cancer', '254837009', 'C50.919', 'Cancer', 'Y', 'Y'),
    ('COLON_CA', 'Colon cancer', '363406005', 'C18.9', 'Cancer', 'Y', 'Y'),
    ('OVARIAN_CA', 'Ovarian cancer', '363443007', 'C56.9', 'Cancer', 'Y', 'Y'),
    ('PROSTATE_CA', 'Prostate cancer', '399068003', 'C61', 'Cancer', 'Y', 'Y'),

    -- Neuro/behavioral
    ('ALZHEIMERS', 'Alzheimer disease', '26929004', 'G30.9', 'Neuro', 'Y', 'Y'),
    ('EPILEPSY', 'Epilepsy', '84757009', 'G40.909', 'Neuro', 'Y', 'Y'),
    ('DEPRESSION', 'Major depressive disorder', '370143000', 'F33.1', 'Behavioral', 'Y', 'Y'),
    ('SUBSTANCE_USE', 'Substance use disorder', '66214007', 'F19.20', 'Behavioral', 'Y', 'Y'),

    -- Pediatric-pattern family conditions
    ('ASTHMA', 'Asthma', '195967001', 'J45.909', 'Other', 'Y', 'Y'),
    ('AUTISM', 'Autism spectrum disorder', '35919005', 'F84.0', 'Neuro', 'Y', 'Y'),
    ('ADHD', 'Attention-deficit/hyperactivity disorder', '406506008', 'F90.9', 'Behavioral', 'Y', 'Y'),
    ('SICKLE_CELL', 'Sickle cell disease', '127040003', 'D57.1', 'Other', 'Y', 'Y'),
    ('CYSTIC_FIBROSIS', 'Cystic fibrosis', '190905008', 'E84.9', 'Other', 'Y', 'Y'),
    ('NONE_REPORTED', 'No known family history reported', NULL, 'Z84.9', 'Other', 'N', 'Y');
GO

PRINT 'Inserted condition rows:';
SELECT COUNT(*) AS FamilyConditionCount FROM Dim.FamilyCondition;
GO
