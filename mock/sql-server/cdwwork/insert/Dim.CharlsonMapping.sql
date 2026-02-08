-- Dim.CharlsonMapping - Charlson Comorbidity Index ICD-10 mappings
-- Purpose: Map ICD-10 codes to 19 Charlson conditions with weighted scores
-- Source: Quan et al. (2005) ICD-10 adaptation of Charlson Index
-- Note: Full clinical implementation has 200+ codes; this is representative subset (60 codes)

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting Charlson Comorbidity Index mappings...';
GO

-- 19 Charlson Conditions with Weights:
-- Weight 1: MI, CHF, PVD, CVD, Dementia, COPD, Rheumatic, PUD, Mild Liver, Diabetes (no complications)
-- Weight 2: Hemiplegia, Moderate/Severe Renal, Diabetes with complications, Cancer, Leukemia, Lymphoma
-- Weight 3: Moderate/Severe Liver Disease
-- Weight 6: Metastatic Solid Tumor, AIDS/HIV

-- Format: (CharlsonCondition, CharlsonWeight, ICD10Code, ICD10Description)

INSERT INTO Dim.CharlsonMapping (CharlsonCondition, CharlsonWeight, ICD10Code, ICD10Description)
VALUES
-- 1. Myocardial Infarction (Weight 1) - 5 codes
('Myocardial Infarction', 1, 'I21.0', 'ST elevation (STEMI) myocardial infarction of anterior wall'),
('Myocardial Infarction', 1, 'I21.1', 'ST elevation (STEMI) myocardial infarction of inferior wall'),
('Myocardial Infarction', 1, 'I21.2', 'ST elevation (STEMI) myocardial infarction of other sites'),
('Myocardial Infarction', 1, 'I21.9', 'Acute myocardial infarction, unspecified'),
('Myocardial Infarction', 1, 'I25.2', 'Old myocardial infarction'),

-- 2. Congestive Heart Failure (Weight 1) - 5 codes
('Congestive Heart Failure', 1, 'I50.1', 'Left ventricular failure, unspecified'),
('Congestive Heart Failure', 1, 'I50.20', 'Unspecified systolic (congestive) heart failure'),
('Congestive Heart Failure', 1, 'I50.23', 'Acute on chronic systolic (congestive) heart failure'),
('Congestive Heart Failure', 1, 'I50.30', 'Unspecified diastolic (congestive) heart failure'),
('Congestive Heart Failure', 1, 'I50.9', 'Heart failure, unspecified'),

-- 3. Peripheral Vascular Disease (Weight 1) - 4 codes
('Peripheral Vascular Disease', 1, 'I70.0', 'Atherosclerosis of aorta'),
('Peripheral Vascular Disease', 1, 'I73.9', 'Peripheral vascular disease, unspecified'),
('Peripheral Vascular Disease', 1, 'I74.3', 'Embolism and thrombosis of arteries of the lower extremities'),
('Peripheral Vascular Disease', 1, 'I77.1', 'Stricture of artery'),

-- 4. Cerebrovascular Disease (Weight 1) - 4 codes
('Cerebrovascular Disease', 1, 'I63.9', 'Cerebral infarction, unspecified'),
('Cerebrovascular Disease', 1, 'I69.30', 'Unspecified sequelae of cerebral infarction'),
('Cerebrovascular Disease', 1, 'G45.9', 'Transient cerebral ischemic attack, unspecified'),
('Cerebrovascular Disease', 1, 'I67.9', 'Cerebrovascular disease, unspecified'),

-- 5. Dementia (Weight 1) - 4 codes
('Dementia', 1, 'F01.50', 'Vascular dementia without behavioral disturbance'),
('Dementia', 1, 'F03.90', 'Unspecified dementia without behavioral disturbance'),
('Dementia', 1, 'G30.9', 'Alzheimer disease, unspecified'),
('Dementia', 1, 'G31.84', 'Mild cognitive impairment, so stated'),

-- 6. Chronic Pulmonary Disease (Weight 1) - 5 codes
('Chronic Pulmonary Disease', 1, 'J43.9', 'Emphysema, unspecified'),
('Chronic Pulmonary Disease', 1, 'J44.0', 'Chronic obstructive pulmonary disease with acute lower respiratory infection'),
('Chronic Pulmonary Disease', 1, 'J44.1', 'Chronic obstructive pulmonary disease with (acute) exacerbation'),
('Chronic Pulmonary Disease', 1, 'J44.9', 'Chronic obstructive pulmonary disease, unspecified'),
('Chronic Pulmonary Disease', 1, 'J47.9', 'Bronchiectasis, uncomplicated'),

-- 7. Rheumatic Disease (Weight 1) - 3 codes
('Rheumatic Disease', 1, 'M05.9', 'Rheumatoid arthritis with rheumatoid factor, unspecified'),
('Rheumatic Disease', 1, 'M32.9', 'Systemic lupus erythematosus, unspecified'),
('Rheumatic Disease', 1, 'M34.9', 'Systemic sclerosis, unspecified'),

-- 8. Peptic Ulcer Disease (Weight 1) - 2 codes
('Peptic Ulcer Disease', 1, 'K25.9', 'Gastric ulcer, unspecified as acute or chronic, without hemorrhage or perforation'),
('Peptic Ulcer Disease', 1, 'K26.9', 'Duodenal ulcer, unspecified as acute or chronic, without hemorrhage or perforation'),

-- 9. Mild Liver Disease (Weight 1) - 3 codes
('Mild Liver Disease', 1, 'K70.30', 'Alcoholic cirrhosis of liver without ascites'),
('Mild Liver Disease', 1, 'K73.9', 'Chronic hepatitis, unspecified'),
('Mild Liver Disease', 1, 'K74.60', 'Unspecified cirrhosis of liver'),

-- 10. Diabetes without Chronic Complication (Weight 1) - 3 codes
('Diabetes without Chronic Complication', 1, 'E11.9', 'Type 2 diabetes mellitus without complications'),
('Diabetes without Chronic Complication', 1, 'E11.65', 'Type 2 diabetes mellitus with hyperglycemia'),
('Diabetes without Chronic Complication', 1, 'E10.9', 'Type 1 diabetes mellitus without complications'),

-- 11. Diabetes with Chronic Complication (Weight 2) - 4 codes
('Diabetes with Chronic Complication', 2, 'E11.22', 'Type 2 diabetes mellitus with diabetic chronic kidney disease'),
('Diabetes with Chronic Complication', 2, 'E11.42', 'Type 2 diabetes mellitus with diabetic polyneuropathy'),
('Diabetes with Chronic Complication', 2, 'E11.319', 'Type 2 diabetes mellitus with unspecified diabetic retinopathy'),
('Diabetes with Chronic Complication', 2, 'E11.36', 'Type 2 diabetes mellitus with diabetic cataract'),

-- 12. Hemiplegia or Paraplegia (Weight 2) - 3 codes
('Hemiplegia or Paraplegia', 2, 'G81.90', 'Hemiplegia, unspecified affecting unspecified side'),
('Hemiplegia or Paraplegia', 2, 'G82.20', 'Paraplegia, unspecified'),
('Hemiplegia or Paraplegia', 2, 'G83.9', 'Paralytic syndrome, unspecified'),

-- 13. Moderate or Severe Renal Disease (Weight 2) - 4 codes
('Moderate or Severe Renal Disease', 2, 'N18.3', 'Chronic kidney disease, stage 3 (moderate)'),
('Moderate or Severe Renal Disease', 2, 'N18.4', 'Chronic kidney disease, stage 4 (severe)'),
('Moderate or Severe Renal Disease', 2, 'N18.5', 'Chronic kidney disease, stage 5'),
('Moderate or Severe Renal Disease', 2, 'N18.6', 'End stage renal disease'),

-- 14. Malignancy (any, including lymphoma and leukemia, except malignant neoplasm of skin) (Weight 2) - 6 codes
('Malignancy', 2, 'C34.90', 'Malignant neoplasm of unspecified part of unspecified bronchus or lung'),
('Malignancy', 2, 'C61', 'Malignant neoplasm of prostate'),
('Malignancy', 2, 'C50.919', 'Malignant neoplasm of unspecified site of unspecified female breast'),
('Malignancy', 2, 'C18.9', 'Malignant neoplasm of colon, unspecified'),
('Malignancy', 2, 'C90.00', 'Multiple myeloma not having achieved remission'),
('Malignancy', 2, 'C92.10', 'Chronic myeloid leukemia, BCR/ABL-positive, not having achieved remission'),

-- 15. Moderate or Severe Liver Disease (Weight 3) - 2 codes
('Moderate or Severe Liver Disease', 3, 'K72.90', 'Hepatic failure, unspecified without coma'),
('Moderate or Severe Liver Disease', 3, 'I85.00', 'Esophageal varices without bleeding'),

-- 16. Metastatic Solid Tumor (Weight 6) - 4 codes
('Metastatic Solid Tumor', 6, 'C79.51', 'Secondary malignant neoplasm of bone'),
('Metastatic Solid Tumor', 6, 'C78.00', 'Secondary malignant neoplasm of unspecified lung'),
('Metastatic Solid Tumor', 6, 'C78.7', 'Secondary malignant neoplasm of liver and intrahepatic bile duct'),
('Metastatic Solid Tumor', 6, 'C79.31', 'Secondary malignant neoplasm of brain'),

-- 17. AIDS/HIV (Weight 6) - 2 codes
('AIDS/HIV', 6, 'B20', 'Human immunodeficiency virus [HIV] disease'),
('AIDS/HIV', 6, 'B24', 'Unspecified human immunodeficiency virus [HIV] disease');
GO

PRINT 'Inserted 60 Charlson Comorbidity Index mappings covering 17 of 19 conditions.';
GO

-- Verification query
PRINT 'Verification: Charlson condition summary';
SELECT
    CharlsonCondition,
    CharlsonWeight,
    COUNT(*) as ICD10_Count
FROM Dim.CharlsonMapping
GROUP BY CharlsonCondition, CharlsonWeight
ORDER BY CharlsonWeight DESC, CharlsonCondition;
GO

PRINT 'Note: Peptic Ulcer Disease and Rheumatic Disease have limited representation in mock data.';
PRINT 'Hemiplegia/Paraplegia not included in problem list but available in Charlson mapping.';
GO
