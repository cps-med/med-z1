-- =====================================================
-- Thompson Twins Test Patient Data - CDWWork2
-- Patient: Bailey James Thompson (Male)
-- ICN: ICN200001
-- Database: CDWWork2 (Walla Walla VAMC, Cerner/Oracle Health, 2025-2026)
-- =====================================================
--
-- Patient Profile:
-- - Name: Bailey James Thompson
-- - Gender: Male
-- - DOB: 04/15/1963 (Age 62)
-- - ICN: ICN200001 (SAME as CDWWork - demonstrates cross-system identity)
-- - PatientKey: PK200001 (CDWWork2 uses PatientKey instead of PatientSID)
-- - Facility: 687 (Walla Walla VAMC, Washington)
-- - Service Connection: 100% (PTSD 70%, Chronic Pain 40%, TBI 10%, Tinnitus 10%)
-- - Veterans Era: Gulf War, Iraq (2009-2010)
--
-- Clinical Summary (2025-2026 at Walla Walla):
-- - Relocated from Bay Pines FL to Walla Walla WA (02/2025)
-- - Established care at new facility (Cerner/Oracle Health system)
-- - Continuation of existing care: PTSD, chronic pain (non-opioid), DM2, HTN, CKD
-- - 2 hospitalizations (2025-2026): pain crisis, COPD exacerbation
-- - Demonstrates harmonization challenge: different column names, table structures
--
-- CDWWork2 Schema Differences (Cerner-style):
-- - Uses "PatientKey" instead of "PatientSID"
-- - Uses "FacilityCode" instead of "Sta3n"
-- - Different table/column naming conventions (e.g., "EncounterKey" vs "InpatientSID")
-- - Demonstrates Silver-layer harmonization requirements
--
-- Data Sections:
-- 1. Patient Demographics (limited - new enrollment data only)
-- 2. Vitals (quarterly 2025-2026)
-- 3. Medications (active meds at Walla Walla)
-- 4. Encounters (2 admissions)
-- 5. Problems (carried forward from CDWWork)
-- 6. Laboratory Results (quarterly labs)
--
-- NOTE: CDWWork2 scripts are intentionally smaller/simpler than CDWWork
-- to reflect the shorter timeframe (1 year vs 15 years) and demonstrate
-- cross-system data harmonization in the Silver layer.
--
-- =====================================================

USE CDWWork2;
GO

-- =====================================================
-- Section 1: Patient - Core Demographics (Cerner-style)
-- =====================================================
-- CDWWork2 uses different column names to simulate Cerner/Oracle Health

PRINT 'Inserting demographics for Bailey Thompson (CDWWork2)...';

INSERT INTO Patient.Patient
(PatientKey, PatientICN, PatientName, BirthDate, Gender,
 FacilityCode, FacilityName, EnrollmentDate, EnrollmentStatus,
 ServiceConnectedPercent, CombatVeteranFlag)
VALUES
('PK200001', 'ICN200001', 'Bailey James Thompson', '1963-04-15', 'M',
 687, 'WALLA WALLA VAMC', '2025-02-01', 'ACTIVE',
 100, 'Y');

GO
PRINT 'Completed: Demographics for Bailey Thompson (CDWWork2).';
GO

-- =====================================================
-- Section 2: Vitals - Quarterly readings (2025-2026)
-- =====================================================

PRINT 'Inserting vitals for Bailey Thompson (CDWWork2)...';

-- 2025-Q1 (2025-02-15) - Initial visit at Walla Walla
INSERT INTO Vital.VitalSign
(VitalKey, PatientKey, PatientICN, FacilityCode,
 VitalType, VitalDateTime, VitalValue, VitalValueNumeric,
 Systolic, Diastolic, LocationName)
VALUES
('VK200001001', 'PK200001', 'ICN200001', 687,
 'PULSE', '2025-02-15 10:00:00', '70', 70.0, NULL, NULL, 'Primary Care'),
('VK200001002', 'PK200001', 'ICN200001', 687,
 'WEIGHT', '2025-02-15 10:05:00', '220', 220.0, NULL, NULL, 'Primary Care'),
('VK200001003', 'PK200001', 'ICN200001', 687,
 'BLOOD PRESSURE', '2025-02-15 10:10:00', '135/85', NULL, 135, 85, 'Primary Care'),
('VK200001004', 'PK200001', 'ICN200001', 687,
 'PAIN', '2025-02-15 10:15:00', '6', 6.0, NULL, NULL, 'Primary Care');

-- 2025-Q2 (2025-05-15)
INSERT INTO Vital.VitalSign
(VitalKey, PatientKey, PatientICN, FacilityCode,
 VitalType, VitalDateTime, VitalValue, VitalValueNumeric,
 Systolic, Diastolic, LocationName)
VALUES
('VK200001005', 'PK200001', 'ICN200001', 687,
 'WEIGHT', '2025-05-15 10:00:00', '218', 218.0, NULL, NULL, 'Primary Care'),
('VK200001006', 'PK200001', 'ICN200001', 687,
 'BLOOD PRESSURE', '2025-05-15 10:05:00', '132/82', NULL, 132, 82, 'Primary Care'),
('VK200001007', 'PK200001', 'ICN200001', 687,
 'PAIN', '2025-05-15 10:10:00', '5', 5.0, NULL, NULL, 'Primary Care');

-- 2025-Q3 (2025-08-15)
INSERT INTO Vital.VitalSign
(VitalKey, PatientKey, PatientICN, FacilityCode,
 VitalType, VitalDateTime, VitalValue, VitalValueNumeric,
 Systolic, Diastolic, LocationName)
VALUES
('VK200001008', 'PK200001', 'ICN200001', 687,
 'WEIGHT', '2025-08-15 10:00:00', '219', 219.0, NULL, NULL, 'Primary Care'),
('VK200001009', 'PK200001', 'ICN200001', 687,
 'BLOOD PRESSURE', '2025-08-15 10:05:00', '130/80', NULL, 130, 80, 'Primary Care'),
('VK200001010', 'PK200001', 'ICN200001', 687,
 'PAIN', '2025-08-15 10:10:00', '6', 6.0, NULL, NULL, 'Primary Care');

-- 2025-Q4 (2025-11-15)
INSERT INTO Vital.VitalSign
(VitalKey, PatientKey, PatientICN, FacilityCode,
 VitalType, VitalDateTime, VitalValue, VitalValueNumeric,
 Systolic, Diastolic, LocationName)
VALUES
('VK200001011', 'PK200001', 'ICN200001', 687,
 'WEIGHT', '2025-11-15 10:00:00', '221', 221.0, NULL, NULL, 'Primary Care'),
('VK200001012', 'PK200001', 'ICN200001', 687,
 'BLOOD PRESSURE', '2025-11-15 10:05:00', '134/84', NULL, 134, 84, 'Primary Care'),
('VK200001013', 'PK200001', 'ICN200001', 687,
 'PAIN', '2025-11-15 10:10:00', '7', 7.0, NULL, NULL, 'Primary Care');

-- 2026-Q1 (2026-02-01) - Most recent
INSERT INTO Vital.VitalSign
(VitalKey, PatientKey, PatientICN, FacilityCode,
 VitalType, VitalDateTime, VitalValue, VitalValueNumeric,
 Systolic, Diastolic, LocationName)
VALUES
('VK200001014', 'PK200001', 'ICN200001', 687,
 'WEIGHT', '2026-02-01 10:00:00', '220', 220.0, NULL, NULL, 'Primary Care'),
('VK200001015', 'PK200001', 'ICN200001', 687,
 'BLOOD PRESSURE', '2026-02-01 10:05:00', '133/82', NULL, 133, 82, 'Primary Care'),
('VK200001016', 'PK200001', 'ICN200001', 687,
 'PAIN', '2026-02-01 10:10:00', '6', 6.0, NULL, NULL, 'Primary Care');

GO
PRINT 'Completed: 16 vital signs for Bailey Thompson (CDWWork2).';
GO

-- =====================================================
-- Section 3: Medications - Active at Walla Walla
-- =====================================================

PRINT 'Inserting medications for Bailey Thompson (CDWWork2)...';

INSERT INTO Pharmacy.Medication
(MedicationKey, PatientKey, PatientICN, FacilityCode,
 DrugName, Strength, OrderDate, Status, DaysSupply, RefillsRemaining)
VALUES
-- Continuation of existing meds from CDWWork
('MK200001001', 'PK200001', 'ICN200001', 687,
 'SERTRALINE', '200MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001002', 'PK200001', 'ICN200001', 687,
 'PRAZOSIN', '5MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001003', 'PK200001', 'ICN200001', 687,
 'TRAZODONE', '100MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001004', 'PK200001', 'ICN200001', 687,
 'GABAPENTIN', '800MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001005', 'PK200001', 'ICN200001', 687,
 'DULOXETINE', '60MG CAP', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001006', 'PK200001', 'ICN200001', 687,
 'LISINOPRIL', '20MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001007', 'PK200001', 'ICN200001', 687,
 'METOPROLOL SUCCINATE', '50MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001008', 'PK200001', 'ICN200001', 687,
 'AMLODIPINE', '5MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001009', 'PK200001', 'ICN200001', 687,
 'ATORVASTATIN', '40MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001010', 'PK200001', 'ICN200001', 687,
 'METFORMIN', '1000MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001011', 'PK200001', 'ICN200001', 687,
 'INSULIN GLARGINE', '100 UNIT/ML SOLN', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001012', 'PK200001', 'ICN200001', 687,
 'OMEPRAZOLE', '20MG CAP', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001013', 'PK200001', 'ICN200001', 687,
 'ASPIRIN', '81MG EC TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001014', 'PK200001', 'ICN200001', 687,
 'ACETAMINOPHEN', '500MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200001015', 'PK200001', 'ICN200001', 687,
 'LIDOCAINE PATCH', '5% PATCH', '2025-02-15', 'ACTIVE', 90, 3);

GO
PRINT 'Completed: 15 active medications for Bailey Thompson (CDWWork2).';
GO

-- =====================================================
-- Section 4: Encounters - Inpatient Admissions (2025-2026)
-- =====================================================

PRINT 'Inserting encounters for Bailey Thompson (CDWWork2)...';

INSERT INTO Encounter.InpatientEncounter
(EncounterKey, PatientKey, PatientICN, FacilityCode,
 AdmitDateTime, DischargeDateTime, LengthOfStay,
 PrimaryDiagnosis, DischargeDisposition, EncounterType)
VALUES
-- Encounter 1: Chronic pain crisis (2025-07-10 to 2025-07-12)
('EK200001001', 'PK200001', 'ICN200001', 687,
 '2025-07-10 18:00:00', '2025-07-12 11:00:00', 2,
 'M54.16 - RADICULOPATHY, LUMBAR REGION', 'TO HOME', 'INPATIENT'),
-- Encounter 2: COPD exacerbation (2025-10-08 to 2025-10-13)
('EK200001002', 'PK200001', 'ICN200001', 687,
 '2025-10-08 14:00:00', '2025-10-13 10:00:00', 5,
 'J44.1 - COPD WITH ACUTE EXACERBATION', 'TO HOME', 'INPATIENT');

GO
PRINT 'Completed: 2 encounters for Bailey Thompson (CDWWork2).';
GO

-- =====================================================
-- Section 5: Problems - Carried forward from CDWWork
-- =====================================================

PRINT 'Inserting problems for Bailey Thompson (CDWWork2)...';

INSERT INTO Problem.ProblemList
(ProblemKey, PatientKey, PatientICN, FacilityCode,
 ProblemName, ICD10Code, Status, OnsetDate, ServiceConnected)
VALUES
('PROB200001001', 'PK200001', 'ICN200001', 687,
 'POST-TRAUMATIC STRESS DISORDER', 'F43.10', 'ACTIVE', '2009-03-01', 'Y'),
('PROB200001002', 'PK200001', 'ICN200001', 687,
 'ALCOHOL DEPENDENCE', 'F10.20', 'ACTIVE', '2010-02-01', 'N'),
('PROB200001003', 'PK200001', 'ICN200001', 687,
 'MAJOR DEPRESSIVE DISORDER, RECURRENT', 'F33.1', 'ACTIVE', '2010-06-01', 'N'),
('PROB200001004', 'PK200001', 'ICN200001', 687,
 'CHRONIC LUMBAR RADICULOPATHY', 'M54.16', 'ACTIVE', '2009-03-15', 'Y'),
('PROB200001005', 'PK200001', 'ICN200001', 687,
 'TYPE 2 DIABETES MELLITUS', 'E11.9', 'ACTIVE', '2014-05-12', 'N'),
('PROB200001006', 'PK200001', 'ICN200001', 687,
 'ESSENTIAL HYPERTENSION', 'I10', 'ACTIVE', '2010-06-15', 'N'),
('PROB200001007', 'PK200001', 'ICN200001', 687,
 'CHRONIC KIDNEY DISEASE STAGE 3A', 'N18.3', 'ACTIVE', '2015-10-20', 'N'),
('PROB200001008', 'PK200001', 'ICN200001', 687,
 'HYPERLIPIDEMIA', 'E78.5', 'ACTIVE', '2012-03-15', 'N'),
('PROB200001009', 'PK200001', 'ICN200001', 687,
 'OBESITY', 'E66.9', 'ACTIVE', '2010-06-15', 'N'),
('PROB200001010', 'PK200001', 'ICN200001', 687,
 'GERD', 'K21.9', 'ACTIVE', '2010-12-01', 'N'),
('PROB200001011', 'PK200001', 'ICN200001', 687,
 'NICOTINE DEPENDENCE', 'F17.210', 'ACTIVE', '1982-06-15', 'N'),
('PROB200001012', 'PK200001', 'ICN200001', 687,
 'COPD', 'J44.1', 'ACTIVE', '2020-06-15', 'N'),
('PROB200001013', 'PK200001', 'ICN200001', 687,
 'TINNITUS, BILATERAL', 'H93.11', 'ACTIVE', '2009-03-15', 'Y'),
('PROB200001014', 'PK200001', 'ICN200001', 687,
 'TRAUMATIC BRAIN INJURY, SEQUELA', 'S06.0X9S', 'ACTIVE', '2009-03-15', 'Y'),
('PROB200001015', 'PK200001', 'ICN200001', 687,
 'INSOMNIA', 'G47.00', 'ACTIVE', '2009-06-01', 'N');

GO
PRINT 'Completed: 15 active problems for Bailey Thompson (CDWWork2).';
GO

-- =====================================================
-- Section 6: Laboratory Results (2025-2026)
-- =====================================================

PRINT 'Inserting laboratory results for Bailey Thompson (CDWWork2)...';

-- 2025-Q1 Labs (2025-02-15) - Initial labs at Walla Walla
INSERT INTO Lab.LabResult
(LabResultKey, PatientKey, PatientICN, FacilityCode,
 LabTestName, CollectionDateTime, ResultDateTime,
 ResultValue, ResultNumeric, Units, ReferenceRange, AbnormalFlag)
VALUES
('LAB200001001', 'PK200001', 'ICN200001', 687,
 'HEMOGLOBIN A1C', '2025-02-15 08:00:00', '2025-02-15 12:00:00',
 '7.9', 7.9, '%', '<5.7', 'H'),
('LAB200001002', 'PK200001', 'ICN200001', 687,
 'CREATININE', '2025-02-15 08:00:00', '2025-02-15 12:00:00',
 '1.5', 1.5, 'mg/dL', '0.7-1.3', 'H'),
('LAB200001003', 'PK200001', 'ICN200001', 687,
 'EGFR', '2025-02-15 08:00:00', '2025-02-15 12:00:00',
 '53', 53.0, 'mL/min/1.73m2', '>60', 'L'),
('LAB200001004', 'PK200001', 'ICN200001', 687,
 'LDL CHOLESTEROL', '2025-02-15 08:00:00', '2025-02-15 12:00:00',
 '96', 96.0, 'mg/dL', '<100', '');

-- 2025-Q2 Labs (2025-05-15)
INSERT INTO Lab.LabResult
(LabResultKey, PatientKey, PatientICN, FacilityCode,
 LabTestName, CollectionDateTime, ResultDateTime,
 ResultValue, ResultNumeric, Units, ReferenceRange, AbnormalFlag)
VALUES
('LAB200001005', 'PK200001', 'ICN200001', 687,
 'HEMOGLOBIN A1C', '2025-05-15 08:00:00', '2025-05-15 12:00:00',
 '7.8', 7.8, '%', '<5.7', 'H'),
('LAB200001006', 'PK200001', 'ICN200001', 687,
 'CREATININE', '2025-05-15 08:00:00', '2025-05-15 12:00:00',
 '1.5', 1.5, 'mg/dL', '0.7-1.3', 'H');

-- 2025-Q4 Labs (2025-11-15)
INSERT INTO Lab.LabResult
(LabResultKey, PatientKey, PatientICN, FacilityCode,
 LabTestName, CollectionDateTime, ResultDateTime,
 ResultValue, ResultNumeric, Units, ReferenceRange, AbnormalFlag)
VALUES
('LAB200001007', 'PK200001', 'ICN200001', 687,
 'HEMOGLOBIN A1C', '2025-11-15 08:00:00', '2025-11-15 12:00:00',
 '7.7', 7.7, '%', '<5.7', 'H'),
('LAB200001008', 'PK200001', 'ICN200001', 687,
 'CREATININE', '2025-11-15 08:00:00', '2025-11-15 12:00:00',
 '1.5', 1.5, 'mg/dL', '0.7-1.3', 'H');

-- 2026-Q1 Labs (2026-02-01) - Most recent
INSERT INTO Lab.LabResult
(LabResultKey, PatientKey, PatientICN, FacilityCode,
 LabTestName, CollectionDateTime, ResultDateTime,
 ResultValue, ResultNumeric, Units, ReferenceRange, AbnormalFlag)
VALUES
('LAB200001009', 'PK200001', 'ICN200001', 687,
 'HEMOGLOBIN A1C', '2026-02-01 08:00:00', '2026-02-01 12:00:00',
 '7.8', 7.8, '%', '<5.7', 'H'),
('LAB200001010', 'PK200001', 'ICN200001', 687,
 'CREATININE', '2026-02-01 08:00:00', '2026-02-01 12:00:00',
 '1.5', 1.5, 'mg/dL', '0.7-1.3', 'H'),
('LAB200001011', 'PK200001', 'ICN200001', 687,
 'EGFR', '2026-02-01 08:00:00', '2026-02-01 12:00:00',
 '52', 52.0, 'mL/min/1.73m2', '>60', 'L');

GO
PRINT 'Completed: 11 laboratory results for Bailey Thompson (CDWWork2).';
GO

-- =====================================================
-- END OF BAILEY THOMPSON CDWWork2 DATA
-- =====================================================

PRINT '========================================';
PRINT 'BAILEY THOMPSON CDWWork2 DATA COMPLETE';
PRINT '========================================';
PRINT 'Patient: Bailey James Thompson';
PRINT 'ICN: ICN200001 (same as CDWWork)';
PRINT 'PatientKey: PK200001 (CDWWork2 identifier)';
PRINT 'Facility: 687 (Walla Walla VAMC)';
PRINT 'Period: 2025-02-01 to 2026-02-08 (1 year)';
PRINT 'Purpose: Demonstrate cross-system harmonization (VistA -> Cerner)';
PRINT '========================================';
GO
