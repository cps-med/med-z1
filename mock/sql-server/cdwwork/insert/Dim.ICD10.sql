-- Dim.ICD10 - ICD-10-CM diagnosis codes data
-- Purpose: Populate 50 common diagnosis codes for mock environment
-- Note: Real CDW has 70,000+ ICD-10 codes; this is a representative subset

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting ICD-10-CM codes into Dim.ICD10...';
GO

-- Insert 50 common diagnosis codes grouped by clinical category
-- Format: (ICD10Code, ICD10Description, ICD10Category, CharlsonCondition, IsChronicCondition)

INSERT INTO Dim.ICD10 (ICD10Code, ICD10Description, ICD10Category, CharlsonCondition, IsChronicCondition)
VALUES
-- Cardiovascular (10 codes)
('I50.9', 'Heart failure, unspecified', 'Cardiovascular', 'Congestive Heart Failure', 'Y'),
('I50.23', 'Acute on chronic systolic (congestive) heart failure', 'Cardiovascular', 'Congestive Heart Failure', 'Y'),
('I10', 'Essential (primary) hypertension', 'Cardiovascular', NULL, 'Y'),
('I25.10', 'Atherosclerotic heart disease of native coronary artery without angina pectoris', 'Cardiovascular', 'Myocardial Infarction', 'Y'),
('I21.9', 'Acute myocardial infarction, unspecified', 'Cardiovascular', 'Myocardial Infarction', 'N'),
('I48.91', 'Unspecified atrial fibrillation', 'Cardiovascular', NULL, 'Y'),
('I63.9', 'Cerebral infarction, unspecified', 'Cardiovascular', 'Cerebrovascular Disease', 'N'),
('I69.30', 'Unspecified sequelae of cerebral infarction', 'Cardiovascular', 'Cerebrovascular Disease', 'Y'),
('I73.9', 'Peripheral vascular disease, unspecified', 'Cardiovascular', 'Peripheral Vascular Disease', 'Y'),
('I11.0', 'Hypertensive heart disease with heart failure', 'Cardiovascular', NULL, 'Y'),

-- Respiratory (6 codes)
('J44.1', 'Chronic obstructive pulmonary disease with (acute) exacerbation', 'Respiratory', 'Chronic Pulmonary Disease', 'Y'),
('J44.0', 'Chronic obstructive pulmonary disease with acute lower respiratory infection', 'Respiratory', 'Chronic Pulmonary Disease', 'Y'),
('J45.909', 'Unspecified asthma, uncomplicated', 'Respiratory', NULL, 'Y'),
('J18.9', 'Pneumonia, unspecified organism', 'Respiratory', NULL, 'N'),
('J96.01', 'Acute respiratory failure with hypoxia', 'Respiratory', NULL, 'N'),
('J43.9', 'Emphysema, unspecified', 'Respiratory', 'Chronic Pulmonary Disease', 'Y'),

-- Endocrine/Metabolic (8 codes)
('E11.9', 'Type 2 diabetes mellitus without complications', 'Endocrine', 'Diabetes without Chronic Complication', 'Y'),
('E11.65', 'Type 2 diabetes mellitus with hyperglycemia', 'Endocrine', 'Diabetes without Chronic Complication', 'Y'),
('E11.22', 'Type 2 diabetes mellitus with diabetic chronic kidney disease', 'Endocrine', 'Diabetes with Chronic Complication', 'Y'),
('E11.42', 'Type 2 diabetes mellitus with diabetic polyneuropathy', 'Endocrine', 'Diabetes with Chronic Complication', 'Y'),
('E11.319', 'Type 2 diabetes mellitus with unspecified diabetic retinopathy', 'Endocrine', 'Diabetes with Chronic Complication', 'Y'),
('E78.5', 'Hyperlipidemia, unspecified', 'Endocrine', NULL, 'Y'),
('E66.9', 'Obesity, unspecified', 'Endocrine', NULL, 'Y'),
('E87.6', 'Hypokalemia', 'Endocrine', NULL, 'N'),

-- Renal (4 codes)
('N18.3', 'Chronic kidney disease, stage 3 (moderate)', 'Renal', 'Moderate or Severe Renal Disease', 'Y'),
('N18.4', 'Chronic kidney disease, stage 4 (severe)', 'Renal', 'Moderate or Severe Renal Disease', 'Y'),
('N18.5', 'Chronic kidney disease, stage 5', 'Renal', 'Moderate or Severe Renal Disease', 'Y'),
('N17.9', 'Acute kidney failure, unspecified', 'Renal', NULL, 'N'),

-- Gastrointestinal/Hepatic (5 codes)
('K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'Gastrointestinal', NULL, 'Y'),
('K70.30', 'Alcoholic cirrhosis of liver without ascites', 'Gastrointestinal', 'Mild Liver Disease', 'Y'),
('K74.60', 'Unspecified cirrhosis of liver', 'Gastrointestinal', 'Moderate or Severe Liver Disease', 'Y'),
('K92.2', 'Gastrointestinal hemorrhage, unspecified', 'Gastrointestinal', NULL, 'N'),
('K50.90', 'Crohn''s disease, unspecified, without complications', 'Gastrointestinal', NULL, 'Y'),

-- Oncology (6 codes)
('C34.90', 'Malignant neoplasm of unspecified part of unspecified bronchus or lung', 'Oncology', 'Malignancy', 'Y'),
('C61', 'Malignant neoplasm of prostate', 'Oncology', 'Malignancy', 'Y'),
('C50.919', 'Malignant neoplasm of unspecified site of unspecified female breast', 'Oncology', 'Malignancy', 'Y'),
('C18.9', 'Malignant neoplasm of colon, unspecified', 'Oncology', 'Malignancy', 'Y'),
('C90.00', 'Multiple myeloma not having achieved remission', 'Oncology', 'Malignancy', 'Y'),
('C79.51', 'Secondary malignant neoplasm of bone', 'Oncology', 'Metastatic Solid Tumor', 'Y'),

-- Mental Health (5 codes)
('F31.9', 'Bipolar disorder, unspecified', 'Mental Health', NULL, 'Y'),
('F32.9', 'Major depressive disorder, single episode, unspecified', 'Mental Health', NULL, 'N'),
('F33.1', 'Major depressive disorder, recurrent, moderate', 'Mental Health', NULL, 'Y'),
('F43.10', 'Post-traumatic stress disorder, unspecified', 'Mental Health', NULL, 'Y'),
('F10.20', 'Alcohol dependence, uncomplicated', 'Mental Health', NULL, 'Y'),

-- Hematologic (2 codes)
('D50.9', 'Iron deficiency anemia, unspecified', 'Hematologic', NULL, 'Y'),
('D64.9', 'Anemia, unspecified', 'Hematologic', NULL, 'N'),

-- Rheumatologic (2 codes)
('M05.9', 'Rheumatoid arthritis with rheumatoid factor, unspecified', 'Rheumatologic', 'Rheumatic Disease', 'Y'),
('M32.9', 'Systemic lupus erythematosus, unspecified', 'Rheumatologic', NULL, 'Y'),

-- Neurologic (2 codes)
('G40.909', 'Epilepsy, unspecified, not intractable, without status epilepticus', 'Neurologic', NULL, 'Y'),
('G30.9', 'Alzheimer disease, unspecified', 'Neurologic', 'Dementia', 'Y');
GO

PRINT 'Inserted 50 ICD-10-CM codes into Dim.ICD10.';
GO

-- Verification query
PRINT 'Verification: ICD-10 code counts by category';
SELECT
    ICD10Category,
    COUNT(*) as CodeCount,
    SUM(CASE WHEN IsChronicCondition = 'Y' THEN 1 ELSE 0 END) as ChronicCount,
    SUM(CASE WHEN CharlsonCondition IS NOT NULL THEN 1 ELSE 0 END) as CharlsonCount
FROM Dim.ICD10
GROUP BY ICD10Category
ORDER BY ICD10Category;
GO
