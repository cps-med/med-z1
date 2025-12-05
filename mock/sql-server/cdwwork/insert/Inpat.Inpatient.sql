-----------------------------------------------------------------------
-- Inpat.Inpatient.sql
-- Insert test data
-- InpatientSID => 1638001 series
-----------------------------------------------------------------------

PRINT '==== Inpat.Inpatient ====';
GO

-- set the active database
USE CDWWork;
GO

-- insert data into the Inpat.Inpatient table
INSERT INTO Inpat.Inpatient
(
 InpatientSID, PTFIEN, Sta3n, PatientSID, MeansTestIndicator, PatientFirstName, AdmitDateTime, AdmitDateSID, AdmitSourceSID, AdmitEligibilitySID, TransferFromFacility, ASIHDays, AdmitMASMovementTypeSID, AdmitFacilityMovementTypeSID, AdmitFromInstitutionSID, AdmitWardLocationSID, AdmitRoomBedSID, AdmitDiagnosis, ProviderSID, HeadNeckCancerFlag, IonizingRadiationFlag, SHADFlag, PatientSSN, PseudoSSNReason, SSNVerificationStatus, GovernmentEmployeeFlag, SensitiveFlag, Age, BirthDateTime
)
VALUES
-- original records for 508
(1638001, 'PFIEN001', 508, 1001, 'MeansTestIndicator', 'Adam',     '2025-01-01 03:30:25', 20250101, 8001, 3001, 508, 3, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1001, 'N', 'N', 'N', '123456789', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 45, '1980-01-01 00:00:00'),
(1638002, 'PFIEN002', 508, 1002, 'MeansTestIndicator', 'Barry',    '2025-01-02 11:11:06', 20250102, 8001, 3001, 508, 5, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '987654321', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 64, '1961-01-02 00:00:00'),
(1638003, 'PFIEN003', 508, 1003, 'MeansTestIndicator', 'Carol',    '2025-01-02 13:22:30', 20250102, 8001, 3001, 508, 5, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1003, 'N', 'N', 'N', '111111111', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 35, '1990-01-02 00:00:00'),
(1638004, 'PFIEN004', 508, 1004, 'MeansTestIndicator', 'Debby',    '2025-01-01 12:25:06', 20250101, 8001, 3001, 508, 4, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1004, 'N', 'N', 'N', '111112222', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 71, '1954-01-02 00:00:00'),
(1638005, 'PFIEN005', 508, 1005, 'MeansTestIndicator', 'Edward',   '2025-01-03 12:35:30', 20250103, 8001, 3001, 508, 2, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1005, 'N', 'N', 'N', '111111105', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),
(1638006, 'PFIEN006', 508, 1006, 'MeansTestIndicator', 'Francine', '2025-01-02 09:01:06', 20250102, 8001, 3001, 508, 5, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1006, 'N', 'N', 'N', '111111106', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),

-- original records for 516
(1638007, 'PFIEN007', 516, 1007, 'MeansTestIndicator', 'Adam',     '2025-01-02 09:01:06', 20250102, 8001, 3001, 516, 5, 100001, 100001, 100001, 2002, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '111221007', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),
(1638008, 'PFIEN008', 516, 1008, 'MeansTestIndicator', 'Barry',    '2025-01-01 15:30:00', 20250101, 8001, 3001, 516, 5, 100001, 100001, 100001, 2002, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '111221007', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),

-- additional records using VistA test patients
(1638021, 'PFIEN006', 508, 1606021, 'MeansTestIndicator', 'DONN',  '2025-01-03 04:01:02', 20250103, 8001, 3001, 508, 3, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1001, 'N', 'N', 'N', '000005288', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 83, '1942-01-01 00:00:00'),
(1638026, 'PFIEN001', 516, 1606026, 'MeansTestIndicator', 'ZZ',    '2025-01-03 05:02:03', 20250103, 8001, 3001, 516, 3, 100001, 100001, 100001, 2002, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '000008887', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 83, '1942-01-01 00:00:00');
GO
