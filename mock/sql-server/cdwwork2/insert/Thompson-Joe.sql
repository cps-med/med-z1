-- =====================================================
-- Thompson Twins Test Patient Data - CDWWork2
-- Patient: Joe Michael Thompson (Male)
-- ICN: ICN200003
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
('PK200003', 'ICN200003', 'Joe Michael Thompson', '1970-05-10', 'M',
 687, 'WALLA WALLA VAMC', '2025-02-01', 'ACTIVE',
 10, 'Y');

-- Vitals (quarterly 2025-2026)
INSERT INTO Vital.VitalSign
(VitalKey, PatientKey, PatientICN, FacilityCode,
 VitalType, VitalDateTime, VitalValue, VitalValueNumeric,
 Systolic, Diastolic, LocationName)
VALUES
('VK200003001', 'PK200003', 'ICN200003', 687, 'WEIGHT', '2025-02-15 10:00:00', '190', 190.0, NULL, NULL, 'Primary Care'),
('VK200003002', 'PK200003', 'ICN200003', 687, 'BLOOD PRESSURE', '2025-02-15 10:05:00', '130/82', NULL, 130, 82, 'Primary Care'),
('VK200003003', 'PK200003', 'ICN200003', 687, 'WEIGHT', '2025-11-15 10:00:00', '191', 191.0, NULL, NULL, 'Primary Care'),
('VK200003004', 'PK200003', 'ICN200003', 687, 'BLOOD PRESSURE', '2025-11-15 10:05:00', '132/84', NULL, 132, 84, 'Primary Care'),
('VK200003005', 'PK200003', 'ICN200003', 687, 'WEIGHT', '2026-02-01 10:00:00', '190', 190.0, NULL, NULL, 'Primary Care'),
('VK200003006', 'PK200003', 'ICN200003', 687, 'BLOOD PRESSURE', '2026-02-01 10:05:00', '130/82', NULL, 130, 82, 'Primary Care');

-- Medications (active)
INSERT INTO Pharmacy.Medication
(MedicationKey, PatientKey, PatientICN, FacilityCode,
 DrugName, Strength, OrderDate, Status, DaysSupply, RefillsRemaining)
VALUES
('MK200003001', 'PK200003', 'ICN200003', 687, 'LISINOPRIL', '20MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200003002', 'PK200003', 'ICN200003', 687, 'ATORVASTATIN', '40MG TAB', '2025-02-15', 'ACTIVE', 90, 3),
('MK200003003', 'PK200003', 'ICN200003', 687, 'TAMSULOSIN', '0.4MG CAP', '2025-02-15', 'ACTIVE', 90, 3),
('MK200003004', 'PK200003', 'ICN200003', 687, 'ASPIRIN', '81MG EC TAB', '2025-02-15', 'ACTIVE', 90, 3);

-- Problems (active)
INSERT INTO Problem.ProblemList
(ProblemKey, PatientKey, PatientICN, FacilityCode,
 ProblemName, ICD10Code, Status, OnsetDate, ServiceConnected)
VALUES
('PROB200003001', 'PK200003', 'ICN200003', 687, 'HYPERTENSION', 'I10', 'ACTIVE', '2011-09-01', 'N'),
('PROB200003002', 'PK200003', 'ICN200003', 687, 'HYPERLIPIDEMIA', 'E78.5', 'ACTIVE', '2013-06-01', 'N'),
('PROB200003003', 'PK200003', 'ICN200003', 687, 'BPH', 'N40.1', 'ACTIVE', '2015-11-01', 'N'),
('PROB200003004', 'PK200003', 'ICN200003', 687, 'TINNITUS BILATERAL', 'H93.13', 'ACTIVE', '2005-01-01', 'Y');

-- Laboratory Results (quarterly)
INSERT INTO Lab.LabResult
(LabResultKey, PatientKey, PatientICN, FacilityCode,
 LabTestName, CollectionDateTime, ResultDateTime,
 ResultValue, ResultNumeric, Units, ReferenceRange, AbnormalFlag)
VALUES
('LAB200003001', 'PK200003', 'ICN200003', 687, 'GLUCOSE', '2025-02-15 08:00:00', '2025-02-15 12:00:00', '96', 96.0, 'mg/dL', '70-100', ''),
('LAB200003002', 'PK200003', 'ICN200003', 687, 'PSA', '2025-02-15 08:00:00', '2025-02-15 12:00:00', '2.1', 2.1, 'ng/mL', '<4.0', ''),
('LAB200003003', 'PK200003', 'ICN200003', 687, 'GLUCOSE', '2026-02-01 08:00:00', '2026-02-01 12:00:00', '95', 95.0, 'mg/dL', '70-100', ''),
('LAB200003004', 'PK200003', 'ICN200003', 687, 'PSA', '2026-02-01 08:00:00', '2026-02-01 12:00:00', '2.2', 2.2, 'ng/mL', '<4.0', '');

GO
PRINT 'JOE THOMPSON CDWWork2 DATA COMPLETE';
GO
