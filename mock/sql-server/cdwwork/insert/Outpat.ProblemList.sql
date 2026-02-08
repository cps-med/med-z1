-- Outpat.ProblemList - VistA Problem List mock data
-- Purpose: Populate 400+ problem records across 30 test patients
-- Strategy: Age-stratified clinical patterns (young, middle, elderly)
-- Clinical realism: Charlson conditions, chronic disease clusters, acute episodes

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting VistA Problem List records...';
GO

-- Format: (PatientSID, PatientICN, Sta3n, ProblemNumber, SNOMEDCode, SNOMEDDescription,
--          ICD10Code, ICD10Description, ProblemStatus, OnsetDate, RecordedDate, LastModifiedDate,
--          ResolvedDate, ProviderSID, ProviderName, Clinic, ProblemComment,
--          IsServiceConnected, IsAcuteCondition, IsChronicCondition,
--          EnteredBy, EnteredDateTime, ModifiedBy, ModifiedDateTime)

INSERT INTO Outpat.ProblemList (
    PatientSID, PatientICN, Sta3n, ProblemNumber, SNOMEDCode, SNOMEDDescription,
    ICD10Code, ICD10Description, ProblemStatus, OnsetDate, RecordedDate, LastModifiedDate,
    ResolvedDate, ProviderSID, ProviderName, Clinic, IsServiceConnected, IsAcuteCondition, IsChronicCondition,
    EnteredBy, EnteredDateTime
)
VALUES
-- ==================================================================================
-- PATIENT 1001: ICN100001 (Adam Dooree) - 90% SC, Agent Orange, Complex elderly patient
-- Age 77, CHF, COPD, Diabetes, CKD, PTSD (High Charlson Score ~9)
-- ==================================================================================
(1001, 'ICN100001', 508, 'P1001-1', '42343007', 'Congestive heart failure', 'I50.23', 'Acute on chronic systolic (congestive) heart failure', 'ACTIVE', '2018-03-15', '2018-03-15', '2024-11-10', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'Y', 'N', 'Y', 'Smith, Robert MD', '2018-03-15 09:30:00'),
(1001, 'ICN100001', 508, 'P1001-2', '13645005', 'Chronic obstructive pulmonary disease', 'J44.1', 'Chronic obstructive pulmonary disease with (acute) exacerbation', 'ACTIVE', '2015-06-20', '2015-06-20', '2025-01-05', NULL, 11002, 'Johnson, Emily MD', 'Pulmonary', 'Y', 'N', 'Y', 'Johnson, Emily MD', '2015-06-20 14:15:00'),
(1001, 'ICN100001', 508, 'P1001-3', '44054006', 'Type 2 diabetes mellitus', 'E11.22', 'Type 2 diabetes mellitus with diabetic chronic kidney disease', 'ACTIVE', '2010-02-10', '2010-02-10', '2024-12-20', NULL, 11003, 'Williams, Sarah MD', 'Endocrinology', 'Y', 'N', 'Y', 'Williams, Sarah MD', '2010-02-10 10:45:00'),
(1001, 'ICN100001', 508, 'P1001-4', '46177005', 'End stage renal disease', 'N18.5', 'Chronic kidney disease, stage 5', 'ACTIVE', '2020-08-15', '2020-08-15', '2025-01-10', NULL, 11003, 'Williams, Sarah MD', 'Nephrology', 'N', 'N', 'Y', 'Williams, Sarah MD', '2020-08-15 11:20:00'),
(1001, 'ICN100001', 508, 'P1001-5', '47505003', 'Post-traumatic stress disorder', 'F43.10', 'Post-traumatic stress disorder, unspecified', 'ACTIVE', '1975-01-01', '2012-05-10', '2024-10-15', NULL, 11004, 'Brown, Michael PhD', 'Mental Health', 'Y', 'N', 'Y', 'Brown, Michael PhD', '2012-05-10 13:30:00'),
(1001, 'ICN100001', 508, 'P1001-6', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2005-01-15', '2005-01-15', '2025-01-02', NULL, 11001, 'Smith, Robert MD', 'Primary Care', 'N', 'N', 'Y', 'Smith, Robert MD', '2005-01-15 09:00:00'),
(1001, 'ICN100001', 508, 'P1001-7', '49436004', 'Atrial fibrillation', 'I48.91', 'Unspecified atrial fibrillation', 'ACTIVE', '2019-11-20', '2019-11-20', '2024-12-15', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'N', 'N', 'Y', 'Smith, Robert MD', '2019-11-20 10:15:00'),
(1001, 'ICN100001', 508, 'P1001-8', '26929004', 'Alzheimer disease', 'G30.9', 'Alzheimer disease, unspecified', 'ACTIVE', '2022-06-10', '2022-06-10', '2024-11-30', NULL, 11005, 'Davis, Jennifer MD', 'Neurology', 'N', 'N', 'Y', 'Davis, Jennifer MD', '2022-06-10 14:00:00'),
(1001, 'ICN100001', 508, 'P1001-9', '233604007', 'Pneumonia', 'J18.9', 'Pneumonia, unspecified organism', 'RESOLVED', '2024-02-01', '2024-02-01', '2024-02-28', '2024-02-28', 11006, 'Miller, James MD', 'Emergency', 'N', 'Y', 'N', 'Miller, James MD', '2024-02-01 08:30:00'),
(1001, 'ICN100001', 508, 'P1001-10', '271737000', 'Anemia', 'D64.9', 'Anemia, unspecified', 'INACTIVE', '2023-05-10', '2023-05-10', '2024-01-15', NULL, 11007, 'Wilson, Patricia MD', 'Hematology', 'N', 'N', 'N', 'Wilson, Patricia MD', '2023-05-10 11:00:00'),
(1001, 'ICN100001', 508, 'P1001-11', '235595009', 'Gastroesophageal reflux disease', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'ACTIVE', '2015-03-20', '2015-03-20', '2024-12-01', NULL, 11008, 'Martinez, Carlos MD', 'Gastroenterology', 'N', 'N', 'Y', 'Martinez, Carlos MD', '2015-03-20 09:45:00'),
(1001, 'ICN100001', 508, 'P1001-12', '239873007', 'Osteoarthritis', 'M19.90', 'Unspecified osteoarthritis, unspecified site', 'ACTIVE', '2010-01-01', '2010-08-15', '2024-10-20', NULL, 11009, 'Anderson, Lisa MD', 'Rheumatology', 'Y', 'N', 'Y', 'Anderson, Lisa MD', '2010-08-15 13:15:00'),
(1001, 'ICN100001', 508, 'P1001-13', '53741008', 'Coronary atherosclerosis', 'I25.10', 'Atherosclerotic heart disease of native coronary artery without angina pectoris', 'ACTIVE', '2016-09-10', '2016-09-10', '2024-12-05', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'Y', 'N', 'Y', 'Smith, Robert MD', '2016-09-10 10:30:00'),
(1001, 'ICN100001', 508, 'P1001-14', '399211009', 'History of myocardial infarction', 'I25.2', 'Old myocardial infarction', 'INACTIVE', '2016-08-01', '2016-08-15', '2020-01-10', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'Y', 'Y', 'N', 'Smith, Robert MD', '2016-08-15 11:00:00'),

-- ==================================================================================
-- PATIENT 1002: ICN100002 (Barry Miifaa) - 50% SC, Gulf War veteran, Middle-aged
-- Age 52, Hypertension, Diabetes, Sleep Apnea, PTSD (Moderate Charlson ~3)
-- ==================================================================================
(1002, 'ICN100002', 508, 'P1002-1', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2015-04-10', '2015-04-10', '2025-01-05', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2015-04-10 09:15:00'),
(1002, 'ICN100002', 508, 'P1002-2', '44054006', 'Type 2 diabetes mellitus', 'E11.9', 'Type 2 diabetes mellitus without complications', 'ACTIVE', '2018-06-15', '2018-06-15', '2024-12-20', NULL, 11003, 'Williams, Sarah MD', 'Endocrinology', 'N', 'N', 'Y', 'Williams, Sarah MD', '2018-06-15 10:30:00'),
(1002, 'ICN100002', 508, 'P1002-3', '78275009', 'Obstructive sleep apnea', 'G47.33', 'Obstructive sleep apnea', 'ACTIVE', '2020-02-20', '2020-02-20', '2024-11-15', NULL, 11011, 'Garcia, Maria MD', 'Sleep Medicine', 'Y', 'N', 'Y', 'Garcia, Maria MD', '2020-02-20 14:00:00'),
(1002, 'ICN100002', 508, 'P1002-4', '47505003', 'Post-traumatic stress disorder', 'F43.10', 'Post-traumatic stress disorder, unspecified', 'ACTIVE', '2010-01-01', '2013-08-10', '2024-10-20', NULL, 11004, 'Brown, Michael PhD', 'Mental Health', 'Y', 'N', 'Y', 'Brown, Michael PhD', '2013-08-10 11:45:00'),
(1002, 'ICN100002', 508, 'P1002-5', '267036007', 'Dyslipidemia', 'E78.5', 'Hyperlipidemia, unspecified', 'ACTIVE', '2016-03-15', '2016-03-15', '2024-12-01', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2016-03-15 09:30:00'),
(1002, 'ICN100002', 508, 'P1002-6', '414916001', 'Obesity', 'E66.9', 'Obesity, unspecified', 'ACTIVE', '2015-01-01', '2015-04-10', '2024-11-10', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2015-04-10 10:15:00'),
(1002, 'ICN100002', 508, 'P1002-7', '90560007', 'Chronic lower back pain', 'M54.5', 'Low back pain', 'ACTIVE', '2008-01-01', '2014-05-10', '2024-09-15', NULL, 11012, 'Rodriguez, Juan MD', 'Pain Management', 'Y', 'N', 'Y', 'Rodriguez, Juan MD', '2014-05-10 13:00:00'),
(1002, 'ICN100002', 508, 'P1002-8', '235595009', 'Gastroesophageal reflux disease', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'ACTIVE', '2017-02-10', '2017-02-10', '2024-10-05', NULL, 11008, 'Martinez, Carlos MD', 'Gastroenterology', 'N', 'N', 'Y', 'Martinez, Carlos MD', '2017-02-10 10:00:00'),
(1002, 'ICN100002', 508, 'P1002-9', '53741008', 'Coronary atherosclerosis', 'I25.10', 'Atherosclerotic heart disease of native coronary artery without angina pectoris', 'ACTIVE', '2023-07-15', '2023-07-15', '2024-12-10', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'N', 'N', 'Y', 'Smith, Robert MD', '2023-07-15 11:30:00'),

-- ==================================================================================
-- PATIENT 1003: ICN100003 (Carol Soola) - 0% SC, Not service-connected, Middle-aged
-- Age 54, Asthma, Depression, Migraines (Low Charlson ~0)
-- ==================================================================================
(1003, 'ICN100003', 508, 'P1003-1', '195967001', 'Asthma', 'J45.909', 'Unspecified asthma, uncomplicated', 'ACTIVE', '1995-01-01', '2010-03-15', '2024-11-20', NULL, 11002, 'Johnson, Emily MD', 'Pulmonary', 'N', 'N', 'Y', 'Johnson, Emily MD', '2010-03-15 09:45:00'),
(1003, 'ICN100003', 508, 'P1003-2', '370143000', 'Major depressive disorder', 'F33.1', 'Major depressive disorder, recurrent, moderate', 'ACTIVE', '2015-06-10', '2015-06-10', '2024-10-15', NULL, 11013, 'Lee, Susan PhD', 'Mental Health', 'N', 'N', 'Y', 'Lee, Susan PhD', '2015-06-10 14:30:00'),
(1003, 'ICN100003', 508, 'P1003-3', '37796009', 'Migraine', 'G43.909', 'Migraine, unspecified, not intractable, without status migrainosus', 'ACTIVE', '2005-01-01', '2012-08-20', '2024-09-10', NULL, 11014, 'Nguyen, Linh MD', 'Neurology', 'N', 'N', 'Y', 'Nguyen, Linh MD', '2012-08-20 10:15:00'),
(1003, 'ICN100003', 508, 'P1003-4', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2020-02-15', '2020-02-15', '2024-12-01', NULL, 11015, 'Thompson, Mark MD', 'Primary Care', 'N', 'N', 'Y', 'Thompson, Mark MD', '2020-02-15 09:00:00'),
(1003, 'ICN100003', 508, 'P1003-5', '235595009', 'Gastroesophageal reflux disease', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'ACTIVE', '2018-04-10', '2018-04-10', '2024-10-20', NULL, 11008, 'Martinez, Carlos MD', 'Gastroenterology', 'N', 'N', 'Y', 'Martinez, Carlos MD', '2018-04-10 11:00:00'),

-- ==================================================================================
-- PATIENT 1010: ICN100010 (Alexander Aminor) - 90% SC, Gulf War + Radiation
-- Age 59, COPD, CKD, Diabetes, Hypertension, Gulf War Illness (Moderate-High Charlson ~6)
-- ==================================================================================
(1010, 'ICN100010', 688, 'P1010-1', '13645005', 'Chronic obstructive pulmonary disease', 'J44.9', 'Chronic obstructive pulmonary disease, unspecified', 'ACTIVE', '2010-05-15', '2010-05-15', '2024-12-15', NULL, 12001, 'Lee, David MD', 'Pulmonary', 'Y', 'N', 'Y', 'Lee, David MD', '2010-05-15 10:30:00'),
(1010, 'ICN100010', 688, 'P1010-2', '46177005', 'End stage renal disease', 'N18.4', 'Chronic kidney disease, stage 4 (severe)', 'ACTIVE', '2018-08-20', '2018-08-20', '2025-01-08', NULL, 12002, 'Kim, Jennifer MD', 'Nephrology', 'N', 'N', 'Y', 'Kim, Jennifer MD', '2018-08-20 14:15:00'),
(1010, 'ICN100010', 688, 'P1010-3', '44054006', 'Type 2 diabetes mellitus', 'E11.42', 'Type 2 diabetes mellitus with diabetic polyneuropathy', 'ACTIVE', '2012-03-10', '2012-03-10', '2024-11-20', NULL, 12003, 'Patel, Raj MD', 'Endocrinology', 'Y', 'N', 'Y', 'Patel, Raj MD', '2012-03-10 09:45:00'),
(1010, 'ICN100010', 688, 'P1010-4', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2008-01-15', '2008-01-15', '2024-12-10', NULL, 12004, 'Chen, Wei MD', 'Primary Care', 'N', 'N', 'Y', 'Chen, Wei MD', '2008-01-15 10:00:00'),
(1010, 'ICN100010', 688, 'P1010-5', '69896004', 'Rheumatoid arthritis', 'M05.9', 'Rheumatoid arthritis with rheumatoid factor, unspecified', 'ACTIVE', '2015-06-20', '2015-06-20', '2024-10-15', NULL, 12005, 'O''Connor, Brian MD', 'Rheumatology', 'Y', 'N', 'Y', 'O''Connor, Brian MD', '2015-06-20 11:30:00'),
(1010, 'ICN100010', 688, 'P1010-6', '267036007', 'Dyslipidemia', 'E78.5', 'Hyperlipidemia, unspecified', 'ACTIVE', '2010-01-01', '2010-05-15', '2024-11-01', NULL, 12004, 'Chen, Wei MD', 'Primary Care', 'N', 'N', 'Y', 'Chen, Wei MD', '2010-05-15 11:00:00'),
(1010, 'ICN100010', 688, 'P1010-7', '195662009', 'Acute respiratory failure', 'J96.01', 'Acute respiratory failure with hypoxia', 'RESOLVED', '2024-03-10', '2024-03-10', '2024-03-25', '2024-03-25', 12006, 'Hernandez, Sofia MD', 'Emergency', 'N', 'Y', 'N', 'Hernandez, Sofia MD', '2024-03-10 07:45:00'),
(1010, 'ICN100010', 688, 'P1010-8', '73595000', 'Chronic pain syndrome', 'G89.29', 'Other chronic pain', 'ACTIVE', '2005-01-01', '2013-07-15', '2024-09-20', NULL, 12007, 'Jackson, Tyler MD', 'Pain Management', 'Y', 'N', 'Y', 'Jackson, Tyler MD', '2013-07-15 13:45:00'),
(1010, 'ICN100010', 688, 'P1010-9', '53741008', 'Coronary atherosclerosis', 'I25.10', 'Atherosclerotic heart disease of native coronary artery without angina pectoris', 'ACTIVE', '2020-11-15', '2020-11-15', '2024-12-08', NULL, 12008, 'Baker, Christine MD', 'Cardiology', 'N', 'N', 'Y', 'Baker, Christine MD', '2020-11-15 10:15:00'),
(1010, 'ICN100010', 688, 'P1010-10', '235595009', 'Gastroesophageal reflux disease', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'ACTIVE', '2014-02-10', '2014-02-10', '2024-10-12', NULL, 12009, 'Singh, Priya MD', 'Gastroenterology', 'N', 'N', 'Y', 'Singh, Priya MD', '2014-02-10 09:30:00'),

-- ==================================================================================
-- YOUNG PATIENTS (Ages 25-45) - Limited chronic conditions, some acute/resolved
-- ==================================================================================
-- PATIENT 1005 (ICN100005) - Age 32, Depression, Anxiety
(1005, 'ICN100005', 508, 'P1005-1', '370143000', 'Major depressive disorder', 'F32.9', 'Major depressive disorder, single episode, unspecified', 'ACTIVE', '2022-05-10', '2022-05-10', '2024-11-15', NULL, 11013, 'Lee, Susan PhD', 'Mental Health', 'N', 'N', 'Y', 'Lee, Susan PhD', '2022-05-10 14:00:00'),
(1005, 'ICN100005', 508, 'P1005-2', '197480006', 'Anxiety disorder', 'F41.9', 'Anxiety disorder, unspecified', 'ACTIVE', '2021-03-15', '2021-03-15', '2024-10-20', NULL, 11013, 'Lee, Susan PhD', 'Mental Health', 'N', 'N', 'Y', 'Lee, Susan PhD', '2021-03-15 13:30:00'),
(1005, 'ICN100005', 508, 'P1005-3', '195967001', 'Asthma', 'J45.909', 'Unspecified asthma, uncomplicated', 'ACTIVE', '2000-01-01', '2015-06-20', '2024-09-10', NULL, 11002, 'Johnson, Emily MD', 'Pulmonary', 'N', 'N', 'Y', 'Johnson, Emily MD', '2015-06-20 10:15:00'),

-- PATIENT 1006 (ICN100006) - Age 38, Hypertension, Pre-diabetes
(1006, 'ICN100006', 508, 'P1006-1', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2020-08-15', '2020-08-15', '2024-12-05', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2020-08-15 09:30:00'),
(1006, 'ICN100006', 508, 'P1006-2', '714628002', 'Prediabetes', 'R73.03', 'Prediabetes', 'ACTIVE', '2023-04-10', '2023-04-10', '2024-11-20', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2023-04-10 10:00:00'),
(1006, 'ICN100006', 508, 'P1006-3', '414916001', 'Obesity', 'E66.9', 'Obesity, unspecified', 'ACTIVE', '2018-01-01', '2020-08-15', '2024-10-15', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2020-08-15 10:15:00'),

-- ==================================================================================
-- ELDERLY PATIENTS (Ages 70-85) - Multiple chronic conditions, high Charlson scores
-- ==================================================================================
-- PATIENT 1007 (ICN100007) - Age 78, Former POW, Complex polypharmacy patient
(1007, 'ICN100007', 508, 'P1007-1', '42343007', 'Congestive heart failure', 'I50.9', 'Heart failure, unspecified', 'ACTIVE', '2016-04-15', '2016-04-15', '2024-11-25', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'Y', 'N', 'Y', 'Smith, Robert MD', '2016-04-15 09:45:00'),
(1007, 'ICN100007', 508, 'P1007-2', '49436004', 'Atrial fibrillation', 'I48.91', 'Unspecified atrial fibrillation', 'ACTIVE', '2018-09-20', '2018-09-20', '2024-12-10', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'Y', 'N', 'Y', 'Smith, Robert MD', '2018-09-20 10:30:00'),
(1007, 'ICN100007', 508, 'P1007-3', '38341003', 'Essential hypertension', 'I10', 'Essential (primary) hypertension', 'ACTIVE', '2000-01-01', '2005-03-10', '2024-12-01', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2005-03-10 09:00:00'),
(1007, 'ICN100007', 508, 'P1007-4', '44054006', 'Type 2 diabetes mellitus', 'E11.319', 'Type 2 diabetes mellitus with unspecified diabetic retinopathy', 'ACTIVE', '2008-06-15', '2008-06-15', '2024-11-15', NULL, 11003, 'Williams, Sarah MD', 'Endocrinology', 'Y', 'N', 'Y', 'Williams, Sarah MD', '2008-06-15 11:00:00'),
(1007, 'ICN100007', 508, 'P1007-5', '46177005', 'End stage renal disease', 'N18.3', 'Chronic kidney disease, stage 3 (moderate)', 'ACTIVE', '2019-02-10', '2019-02-10', '2024-12-08', NULL, 11003, 'Williams, Sarah MD', 'Nephrology', 'N', 'N', 'Y', 'Williams, Sarah MD', '2019-02-10 14:30:00'),
(1007, 'ICN100007', 508, 'P1007-6', '13645005', 'Chronic obstructive pulmonary disease', 'J44.0', 'Chronic obstructive pulmonary disease with acute lower respiratory infection', 'ACTIVE', '2010-08-20', '2010-08-20', '2025-01-05', NULL, 11002, 'Johnson, Emily MD', 'Pulmonary', 'Y', 'N', 'Y', 'Johnson, Emily MD', '2010-08-20 10:00:00'),
(1007, 'ICN100007', 508, 'P1007-7', '47505003', 'Post-traumatic stress disorder', 'F43.10', 'Post-traumatic stress disorder, unspecified', 'ACTIVE', '1950-01-01', '2006-05-15', '2024-10-20', NULL, 11004, 'Brown, Michael PhD', 'Mental Health', 'Y', 'N', 'Y', 'Brown, Michael PhD', '2006-05-15 13:00:00'),
(1007, 'ICN100007', 508, 'P1007-8', '26929004', 'Alzheimer disease', 'G30.9', 'Alzheimer disease, unspecified', 'ACTIVE', '2021-11-10', '2021-11-10', '2024-11-30', NULL, 11005, 'Davis, Jennifer MD', 'Neurology', 'N', 'N', 'Y', 'Davis, Jennifer MD', '2021-11-10 15:00:00'),
(1007, 'ICN100007', 508, 'P1007-9', '267036007', 'Dyslipidemia', 'E78.5', 'Hyperlipidemia, unspecified', 'ACTIVE', '2005-01-01', '2005-03-10', '2024-11-10', NULL, 11010, 'Taylor, Kevin MD', 'Primary Care', 'N', 'N', 'Y', 'Taylor, Kevin MD', '2005-03-10 10:00:00'),
(1007, 'ICN100007', 508, 'P1007-10', '87433001', 'Pulmonary hypertension', 'I27.20', 'Pulmonary hypertension, unspecified', 'ACTIVE', '2020-03-15', '2020-03-15', '2024-12-05', NULL, 11001, 'Smith, Robert MD', 'Cardiology', 'N', 'N', 'Y', 'Smith, Robert MD', '2020-03-15 11:15:00'),
(1007, 'ICN100007', 508, 'P1007-11', '235595009', 'Gastroesophageal reflux disease', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'ACTIVE', '2010-01-01', '2010-08-20', '2024-10-15', NULL, 11008, 'Martinez, Carlos MD', 'Gastroenterology', 'N', 'N', 'Y', 'Martinez, Carlos MD', '2010-08-20 09:30:00');
GO

PRINT 'Inserted 55 problem records for 6 patients (ICN100001-100003, 100005-100007, 100010).';
GO

-- ==================================================================================
-- Verification Queries
-- ==================================================================================
PRINT '';
PRINT '=============================================================';
PRINT 'VERIFICATION: Problem List Summary Statistics';
PRINT '=============================================================';

-- Total record count
SELECT COUNT(*) as TotalProblems FROM Outpat.ProblemList;

-- Problems by status
SELECT ProblemStatus, COUNT(*) as ProblemCount
FROM Outpat.ProblemList
GROUP BY ProblemStatus
ORDER BY ProblemCount DESC;

-- Problems by patient
SELECT
    PatientICN,
    COUNT(*) as ProblemCount,
    SUM(CASE WHEN ProblemStatus = 'ACTIVE' THEN 1 ELSE 0 END) as ActiveCount,
    SUM(CASE WHEN IsChronicCondition = 'Y' THEN 1 ELSE 0 END) as ChronicCount
FROM Outpat.ProblemList
GROUP BY PatientICN
ORDER BY ProblemCount DESC;

-- Problems by ICD-10 category (join with Dim.ICD10)
SELECT
    i.ICD10Category,
    COUNT(*) as ProblemCount,
    SUM(CASE WHEN pl.ProblemStatus = 'ACTIVE' THEN 1 ELSE 0 END) as ActiveCount
FROM Outpat.ProblemList pl
INNER JOIN Dim.ICD10 i ON pl.ICD10Code = i.ICD10Code
GROUP BY i.ICD10Category
ORDER BY ProblemCount DESC;

-- Charlson conditions represented
SELECT
    c.CharlsonCondition,
    c.CharlsonWeight,
    COUNT(DISTINCT pl.PatientICN) as PatientCount,
    COUNT(*) as ProblemCount
FROM Outpat.ProblemList pl
INNER JOIN Dim.CharlsonMapping c ON pl.ICD10Code = c.ICD10Code
WHERE pl.ProblemStatus = 'ACTIVE'
GROUP BY c.CharlsonCondition, c.CharlsonWeight
ORDER BY c.CharlsonWeight DESC, c.CharlsonCondition;

PRINT '';
PRINT 'Problem List mock data insertion complete.';
PRINT 'Total: 55 problems across 6 test patients.';
PRINT 'Patients: ICN100001 (14 problems), ICN100002 (9), ICN100003 (5), ICN100005 (3), ICN100006 (3), ICN100007 (11), ICN100010 (10)';
GO
