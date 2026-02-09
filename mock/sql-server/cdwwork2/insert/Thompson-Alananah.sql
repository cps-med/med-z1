-- =====================================================
-- Thompson Twins Test Patient Data - CDWWork2
-- Patient: Alananah Marie Thompson (Female)
-- ICN: ICN200002
-- Database: CDWWork2 (Walla Walla VAMC, Cerner/Oracle Health, 2025-2026)
-- =====================================================

USE CDWWork2;
GO

-- Demographics
INSERT INTO Patient.Patient
(PatientKey, PatientICN, PatientName, BirthDate, Gender,
 FacilityCode, FacilityName, EnrollmentDate, EnrollmentStatus,
 ServiceConnectedPercent, CombatVeteranFlag)
VALUES
('PK200002', 'ICN200002', 'Alananah Marie Thompson', '1963-04-15', 'F',
 687, 'WALLA WALLA VAMC', '2025-02-01', 'ACTIVE',
 80, 'Y');

-- Vitals (quarterly 2025-2026)
INSERT INTO Vital.VitalSign
(VitalKey, PatientKey, PatientICN, FacilityCode,
 VitalType, VitalDateTime, VitalValue, VitalValueNumeric,
 Systolic, Diastolic, LocationName)
VALUES
('VK200002001', 'PK200002', 'ICN200002', 687, 'WEIGHT', '2025-02-15 10:00:00', '141', 141.0, NULL, NULL, 'Primary Care'),
('VK200002002', 'PK200002', 'ICN200002', 687, 'BLOOD PRESSURE', '2025-02-15 10:05:00', '124/78', NULL, 124, 78, 'Primary Care'),
('VK200002003', 'PK200002', 'ICN200002', 687, 'WEIGHT', '2025-11-15 10:00:00', '142', 142.0, NULL, NULL, 'Primary Care'),
('VK200002004', 'PK200002', 'ICN200002', 687, 'BLOOD PRESSURE', '2025-11-15 10:05:00', '125/80', NULL, 125, 80, 'Primary Care'),
('VK200002005', 'PK200002', 'ICN200002', 687, 'WEIGHT', '2026-02-01 10:00:00', '141', 141.0, NULL, NULL, 'Primary Care'),
('VK200002006', 'PK200002', 'ICN200002', 687, 'BLOOD PRESSURE', '2026-02-01 10:05:00', '124/78', NULL, 124, 78, 'Primary Care');

-- Medications (active)
INSERT INTO Pharmacy.Medication
(MedicationKey, PatientKey, PatientICN, FacilityCode,
 DrugName, Strength, OrderDate, Status, DaysSupply, RefillsRemaining)
VALUES
('MK200002001', 'PK200002', 'ICN200002', 687, 'TAMOXIFEN', '20MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200002002', 'PK200002', 'ICN200002', 687, 'SERTRALINE', '100MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200002003', 'PK200002', 'ICN200002', 687, 'LEVOTHYROXINE', '75MCG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200002004', 'PK200002', 'ICN200002', 687, 'LISINOPRIL', '10MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200002005', 'PK200002', 'ICN200002', 687, 'ATORVASTATIN', '20MG TAB', '2025-02-15', 'ACTIVE', 90, 3);

-- Problems (active)
INSERT INTO Problem.ProblemList
(ProblemKey, PatientKey, PatientICN, FacilityCode,
 ProblemName, ICD10Code, Status, OnsetDate, ServiceConnected)
VALUES
('PROB200002001', 'PK200002', 'ICN200002', 687, 'HISTORY OF BREAST CANCER', 'Z85.3', 'ACTIVE', '2012-07-02', 'Y'),
('PROB200002002', 'PK200002', 'ICN200002', 687, 'PTSD', 'F43.10', 'ACTIVE', '1995-06-01', 'Y'),
('PROB200002003', 'PK200002', 'ICN200002', 687, 'HYPERTENSION', 'I10', 'ACTIVE', '2013-09-01', 'N'),
('PROB200002004', 'PK200002', 'ICN200002', 687, 'HYPOTHYROIDISM', 'E03.9', 'ACTIVE', '2015-01-15', 'N'),
('PROB200002005', 'PK200002', 'ICN200002', 687, 'HYPERLIPIDEMIA', 'E78.5', 'ACTIVE', '2014-06-15', 'N');

-- Laboratory Results (quarterly)
INSERT INTO Lab.LabResult
(LabResultKey, PatientKey, PatientICN, FacilityCode,
 LabTestName, CollectionDateTime, ResultDateTime,
 ResultValue, ResultNumeric, Units, ReferenceRange, AbnormalFlag)
VALUES
('LAB200002001', 'PK200002', 'ICN200002', 687, 'TSH', '2025-02-15 08:00:00', '2025-02-15 12:00:00', '2.8', 2.8, 'mIU/L', '0.4-4.0', ''),
('LAB200002002', 'PK200002', 'ICN200002', 687, 'CEA', '2025-02-15 08:00:00', '2025-02-15 12:00:00', '2.1', 2.1, 'ng/mL', '<5.0', ''),
('LAB200002003', 'PK200002', 'ICN200002', 687, 'TSH', '2026-02-01 08:00:00', '2026-02-01 12:00:00', '2.7', 2.7, 'mIU/L', '0.4-4.0', ''),
('LAB200002004', 'PK200002', 'ICN200002', 687, 'CEA', '2026-02-01 08:00:00', '2026-02-01 12:00:00', '2.0', 2.0, 'ng/mL', '<5.0', '');

GO
PRINT 'ALANANAH THOMPSON CDWWork2 DATA COMPLETE';
GO
