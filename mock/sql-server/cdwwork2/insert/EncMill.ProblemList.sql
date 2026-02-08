-- EncMill.ProblemList - Cerner/Oracle Health Problem List mock data
-- Purpose: Populate Cerner-based problem list for harmonization testing
-- Strategy: Use different schema/naming to test Silver-layer mapping
-- Patients: ICN100001 (Adam Dooree) and ICN100010 (Alexander Aminor) - existing CDWWork2 patients

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting Cerner Problem List records...';
GO

-- Format: (PatientKey, PatientICN, FacilityCode, ProblemID, DiagnosisCode, DiagnosisDescription,
--          ClinicalTermCode, ClinicalTermDescription, StatusCode, OnsetDateTime, RecordDateTime,
--          LastUpdateDateTime, ResolvedDateTime, ResponsibleProviderID, ResponsibleProviderName, RecordingLocation,
--          ServiceConnectedFlag, AcuteFlag, ChronicFlag, CreatedByUserID, CreatedByUserName, CreatedDateTime)

-- Note: Using existing CDWWork2 patients (ICN100001 at Portland 648, ICN100010 at Seattle 663)
-- PatientKey values match the patient_key from VeteranMill.SPerson

INSERT INTO EncMill.ProblemList (
    PatientKey, PatientICN, FacilityCode, ProblemID, DiagnosisCode, DiagnosisDescription,
    ClinicalTermCode, ClinicalTermDescription, StatusCode, OnsetDateTime, RecordDateTime,
    LastUpdateDateTime, ResolvedDateTime, ResponsibleProviderID, ResponsibleProviderName, RecordingLocation,
    ServiceConnectedFlag, AcuteFlag, ChronicFlag, CreatedByUserID, CreatedByUserName, CreatedDateTime
)
VALUES
-- ==================================================================================
-- PATIENT: ICN100001 (Adam Dooree) - Portland VAMC (648)
-- Cerner representation of cardiovascular disease cluster
-- Age 77, CHF, CAD, HTN, Diabetes (Moderate-High Charlson ~7)
-- ==================================================================================
(1001, 'ICN100001', 648, 'C1001-1', 'I50.23', 'Acute on chronic systolic (congestive) heart failure', '42343007', 'Congestive heart failure', 'A', '2019-05-10 00:00:00', '2019-05-10 10:30:00', '2024-12-15 09:00:00', NULL, 20001, 'Wilson, Robert MD', 'Portland VAMC Cardiology', 'Y', 'N', 'Y', 20001, 'Wilson, Robert MD', '2019-05-10 10:30:00'),
(1001, 'ICN100001', 648, 'C1001-2', 'I25.10', 'Atherosclerotic heart disease of native coronary artery without angina pectoris', '53741008', 'Coronary atherosclerosis', 'A', '2017-08-15 00:00:00', '2017-08-15 14:15:00', '2024-11-20 10:30:00', NULL, 20001, 'Wilson, Robert MD', 'Portland VAMC Cardiology', 'Y', 'N', 'Y', 20001, 'Wilson, Robert MD', '2017-08-15 14:15:00'),
(1001, 'ICN100001', 648, 'C1001-3', 'I10', 'Essential (primary) hypertension', '38341003', 'Essential hypertension', 'A', '2010-01-01 00:00:00', '2010-03-20 09:45:00', '2025-01-05 09:00:00', NULL, 20002, 'Davis, Jennifer MD', 'Portland VAMC Primary Care', 'N', 'N', 'Y', 20002, 'Davis, Jennifer MD', '2010-03-20 09:45:00'),
(1001, 'ICN100001', 648, 'C1001-4', 'E11.22', 'Type 2 diabetes mellitus with diabetic chronic kidney disease', '44054006', 'Type 2 diabetes mellitus', 'A', '2012-06-10 00:00:00', '2012-06-10 11:00:00', '2024-12-10 10:15:00', NULL, 20003, 'Thompson, Sarah MD', 'Portland VAMC Endocrinology', 'Y', 'N', 'Y', 20003, 'Thompson, Sarah MD', '2012-06-10 11:00:00'),
(1001, 'ICN100001', 648, 'C1001-5', 'N18.3', 'Chronic kidney disease, stage 3 (moderate)', '46177005', 'End stage renal disease', 'A', '2020-02-15 00:00:00', '2020-02-15 14:30:00', '2024-12-08 11:00:00', NULL, 20003, 'Thompson, Sarah MD', 'Portland VAMC Nephrology', 'N', 'N', 'Y', 20003, 'Thompson, Sarah MD', '2020-02-15 14:30:00'),
(1001, 'ICN100001', 648, 'C1001-6', 'I48.91', 'Unspecified atrial fibrillation', '49436004', 'Atrial fibrillation', 'A', '2021-11-20 00:00:00', '2021-11-20 10:15:00', '2024-12-05 09:30:00', NULL, 20001, 'Wilson, Robert MD', 'Portland VAMC Cardiology', 'N', 'N', 'Y', 20001, 'Wilson, Robert MD', '2021-11-20 10:15:00'),
(1001, 'ICN100001', 648, 'C1001-7', 'E78.5', 'Hyperlipidemia, unspecified', '267036007', 'Dyslipidemia', 'A', '2010-01-01 00:00:00', '2010-03-20 10:00:00', '2024-11-15 09:45:00', NULL, 20002, 'Davis, Jennifer MD', 'Portland VAMC Primary Care', 'N', 'N', 'Y', 20002, 'Davis, Jennifer MD', '2010-03-20 10:00:00'),
(1001, 'ICN100001', 648, 'C1001-8', 'J18.9', 'Pneumonia, unspecified organism', '233604007', 'Pneumonia', 'R', '2024-01-15 00:00:00', '2024-01-15 07:45:00', '2024-02-10 09:00:00', '2024-02-10 09:00:00', 20004, 'Martinez, Carlos MD', 'Portland VAMC Emergency', 'N', 'Y', 'N', 20004, 'Martinez, Carlos MD', '2024-01-15 07:45:00'),

-- ==================================================================================
-- PATIENT: ICN100010 (Alexander Aminor) - Seattle VAMC (663)
-- Cerner representation of respiratory disease cluster
-- Age 59, COPD, Asthma, Hypertension, Diabetes (Moderate Charlson ~4)
-- ==================================================================================
(1010, 'ICN100010', 663, 'C1010-1', 'J44.1', 'Chronic obstructive pulmonary disease with (acute) exacerbation', '13645005', 'Chronic obstructive pulmonary disease', 'A', '2014-04-10 00:00:00', '2014-04-10 10:30:00', '2025-01-08 10:00:00', NULL, 20005, 'Lee, David MD', 'Seattle VAMC Pulmonary', 'Y', 'N', 'Y', 20005, 'Lee, David MD', '2014-04-10 10:30:00'),
(1010, 'ICN100010', 663, 'C1010-2', 'J45.909', 'Unspecified asthma, uncomplicated', '195967001', 'Asthma', 'A', '1990-01-01 00:00:00', '2010-08-15 09:45:00', '2024-11-20 10:15:00', NULL, 20005, 'Lee, David MD', 'Seattle VAMC Pulmonary', 'N', 'N', 'Y', 20005, 'Lee, David MD', '2010-08-15 09:45:00'),
(1010, 'ICN100010', 663, 'C1010-3', 'I10', 'Essential (primary) hypertension', '38341003', 'Essential hypertension', 'A', '2008-01-01 00:00:00', '2008-06-20 09:00:00', '2024-12-10 09:30:00', NULL, 20002, 'Davis, Jennifer MD', 'Seattle VAMC Primary Care', 'N', 'N', 'Y', 20002, 'Davis, Jennifer MD', '2008-06-20 09:00:00'),
(1010, 'ICN100010', 663, 'C1010-4', 'E11.9', 'Type 2 diabetes mellitus without complications', '44054006', 'Type 2 diabetes mellitus', 'A', '2018-03-15 00:00:00', '2018-03-15 11:00:00', '2024-11-25 10:00:00', NULL, 20003, 'Thompson, Sarah MD', 'Seattle VAMC Endocrinology', 'N', 'N', 'Y', 20003, 'Thompson, Sarah MD', '2018-03-15 11:00:00'),
(1010, 'ICN100010', 663, 'C1010-5', 'E78.5', 'Hyperlipidemia, unspecified', '267036007', 'Dyslipidemia', 'A', '2010-01-01 00:00:00', '2010-08-15 10:15:00', '2024-10-20 09:45:00', NULL, 20002, 'Davis, Jennifer MD', 'Seattle VAMC Primary Care', 'N', 'N', 'Y', 20002, 'Davis, Jennifer MD', '2010-08-15 10:15:00'),
(1010, 'ICN100010', 663, 'C1010-6', 'K21.9', 'Gastro-esophageal reflux disease without esophagitis', '235595009', 'Gastroesophageal reflux disease', 'A', '2015-02-10 00:00:00', '2015-02-10 09:30:00', '2024-09-15 10:00:00', NULL, 20006, 'Singh, Priya MD', 'Seattle VAMC Gastroenterology', 'N', 'N', 'Y', 20006, 'Singh, Priya MD', '2015-02-10 09:30:00'),
(1010, 'ICN100010', 663, 'C1010-7', 'M05.9', 'Rheumatoid arthritis with rheumatoid factor, unspecified', '69896004', 'Rheumatoid arthritis', 'A', '2016-05-20 00:00:00', '2016-05-20 14:00:00', '2024-11-10 13:30:00', NULL, 20007, 'Brown, Michael MD', 'Seattle VAMC Rheumatology', 'Y', 'N', 'Y', 20007, 'Brown, Michael MD', '2016-05-20 14:00:00'),
(1010, 'ICN100010', 663, 'C1010-8', 'N18.4', 'Chronic kidney disease, stage 4 (severe)', '46177005', 'End stage renal disease', 'A', '2019-08-10 00:00:00', '2019-08-10 14:30:00', '2024-12-05 11:00:00', NULL, 20003, 'Thompson, Sarah MD', 'Seattle VAMC Nephrology', 'N', 'N', 'Y', 20003, 'Thompson, Sarah MD', '2019-08-10 14:30:00'),
(1010, 'ICN100010', 663, 'C1010-9', 'F43.10', 'Post-traumatic stress disorder, unspecified', '47505003', 'Post-traumatic stress disorder', 'A', '2015-01-01 00:00:00', '2018-08-15 13:45:00', '2024-11-20 14:00:00', NULL, 20008, 'Lee, Susan PhD', 'Seattle VAMC Mental Health', 'Y', 'N', 'Y', 20008, 'Lee, Susan PhD', '2018-08-15 13:45:00'),
(1010, 'ICN100010', 663, 'C1010-10', 'M54.5', 'Low back pain', '90560007', 'Chronic lower back pain', 'A', '2010-01-01 00:00:00', '2016-06-10 13:00:00', '2024-09-30 14:00:00', NULL, 20009, 'Rodriguez, Juan MD', 'Seattle VAMC Pain Management', 'Y', 'N', 'Y', 20009, 'Rodriguez, Juan MD', '2016-06-10 13:00:00');
GO

PRINT 'Inserted 18 Cerner problem records for 2 patients (ICN100001, ICN100010).';
GO

-- ==================================================================================
-- Verification Queries
-- ==================================================================================
PRINT '';
PRINT '=============================================================';
PRINT 'VERIFICATION: Cerner Problem List Summary Statistics';
PRINT '=============================================================';

-- Total record count
SELECT COUNT(*) as TotalProblems FROM EncMill.ProblemList;

-- Problems by status (Cerner uses A/I/R codes)
SELECT StatusCode, COUNT(*) as ProblemCount
FROM EncMill.ProblemList
GROUP BY StatusCode
ORDER BY ProblemCount DESC;

-- Problems by patient
SELECT
    PatientICN,
    COUNT(*) as ProblemCount,
    SUM(CASE WHEN StatusCode = 'A' THEN 1 ELSE 0 END) as ActiveCount,
    SUM(CASE WHEN ChronicFlag = 'Y' THEN 1 ELSE 0 END) as ChronicCount
FROM EncMill.ProblemList
GROUP BY PatientICN
ORDER BY ProblemCount DESC;

-- Schema comparison note
PRINT '';
PRINT 'Schema Differences (Cerner vs VistA):';
PRINT '- Cerner: DiagnosisSID (vs ProblemSID)';
PRINT '- Cerner: StatusCode = A/I/R (vs ProblemStatus = ACTIVE/INACTIVE/RESOLVED)';
PRINT '- Cerner: DiagnosisCode (vs ICD10Code)';
PRINT '- Cerner: ClinicalTermCode (vs SNOMEDCode)';
PRINT '- Cerner: DateTime fields (vs Date fields)';
PRINT '- Cerner: PatientKey (vs PatientSID)';
PRINT 'Silver-layer ETL will harmonize these differences.';
GO

PRINT '';
PRINT 'Cerner Problem List mock data insertion complete.';
GO
