/*
|----------------------------------------------------------------------
| Inpat.Inpatient.sql
|----------------------------------------------------------------------
| Insert test data
| InpatientSID => 1638001 series
|----------------------------------------------------------------------
*/

PRINT '================================================';
PRINT '====            Inpat.Inpatient             ====';
PRINT '================================================';
GO

-- set the active database
USE CDWWork;
GO

/*
|----------------------------------------------------------------------
| Original set of 10 Inpatient records
| ---------------------------------------------------------------------
*/

PRINT 'Adding 10 original Inpatient records';
GO

-- insert data into the Inpat.Inpatient table
INSERT INTO Inpat.Inpatient
(
 InpatientSID, PTFIEN, Sta3n, PatientSID, MeansTestIndicator, PatientFirstName,
 AdmitDateTime, AdmitDateSID, AdmitSourceSID, AdmitEligibilitySID, TransferFromFacility,
 ASIHDays, AdmitMASMovementTypeSID, AdmitFacilityMovementTypeSID, AdmitFromInstitutionSID,
 AdmitWardLocationSID, AdmitRoomBedSID, AdmitDiagnosis, ProviderSID, HeadNeckCancerFlag,
 IonizingRadiationFlag, SHADFlag, PatientSSN, PseudoSSNReason, SSNVerificationStatus,
 GovernmentEmployeeFlag, SensitiveFlag, Age, BirthDateTime
)
VALUES
-- original records for Sta3n 508
(1638001, 'PFIEN001', 508, 1001, 'MeansTestIndicator', 'Adam',     '2025-01-01 03:30:25', 20250101, 8001, 3001, 508, 3, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1001, 'N', 'N', 'N', '123456789', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 45, '1980-01-01 00:00:00'),
(1638002, 'PFIEN002', 508, 1002, 'MeansTestIndicator', 'Barry',    '2025-01-02 11:11:06', 20250102, 8001, 3001, 508, 5, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '987654321', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 64, '1961-01-02 00:00:00'),
(1638003, 'PFIEN003', 508, 1003, 'MeansTestIndicator', 'Carol',    '2025-01-02 13:22:30', 20250102, 8001, 3001, 508, 5, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1003, 'N', 'N', 'N', '111111111', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 35, '1990-01-02 00:00:00'),
(1638004, 'PFIEN004', 508, 1004, 'MeansTestIndicator', 'Debby',    '2025-01-01 12:25:06', 20250101, 8001, 3001, 508, 4, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1004, 'N', 'N', 'N', '111112222', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 71, '1954-01-02 00:00:00'),
(1638005, 'PFIEN005', 508, 1005, 'MeansTestIndicator', 'Edward',   '2025-01-03 12:35:30', 20250103, 8001, 3001, 508, 2, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1005, 'N', 'N', 'N', '111111105', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),
(1638006, 'PFIEN006', 508, 1006, 'MeansTestIndicator', 'Francine', '2025-01-02 09:01:06', 20250102, 8001, 3001, 508, 5, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1006, 'N', 'N', 'N', '111111106', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),

-- original records for Sta3n 516
(1638007, 'PFIEN007', 516, 1007, 'MeansTestIndicator', 'Adam',     '2025-01-02 09:01:06', 20250102, 8001, 3001, 516, 5, 100001, 100001, 100001, 2002, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '111221007', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),
(1638008, 'PFIEN008', 516, 1008, 'MeansTestIndicator', 'Barry',    '2025-01-01 15:30:00', 20250101, 8001, 3001, 516, 5, 100001, 100001, 100001, 2002, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '111221007', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 44, '1981-05-15 00:00:00'),

-- additional records using VistA test patients
(1638021, 'PFIEN006', 508, 1606021, 'MeansTestIndicator', 'DONN',  '2025-01-03 04:01:02', 20250103, 8001, 3001, 508, 3, 100001, 100001, 100001, 2001, 100001, 'AdmitDiagnosis', 1001, 'N', 'N', 'N', '000005288', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 83, '1942-01-01 00:00:00'),
(1638026, 'PFIEN001', 516, 1606026, 'MeansTestIndicator', 'ZZ',    '2025-01-03 05:02:03', 20250103, 8001, 3001, 516, 3, 100001, 100001, 100001, 2002, 100001, 'AdmitDiagnosis', 1002, 'N', 'N', 'N', '000008887', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 83, '1942-01-01 00:00:00');
GO

/*
|----------------------------------------------------------------------
| Aditional set of 5 Inpatient records
| ---------------------------------------------------------------------
*/

PRINT '';
PRINT 'Adding Inpatient Stays (5 total)';
GO

INSERT INTO Inpat.Inpatient
(
 InpatientSID, PTFIEN, Sta3n, PatientSID, MeansTestIndicator, PatientFirstName,
 AdmitDateTime, AdmitDateSID, AdmitSourceSID, AdmitEligibilitySID, TransferFromFacility,
 ASIHDays, AdmitMASMovementTypeSID, AdmitFacilityMovementTypeSID, AdmitFromInstitutionSID,
 AdmitWardLocationSID, AdmitRoomBedSID, AdmitDiagnosis, ProviderSID, HeadNeckCancerFlag,
 IonizingRadiationFlag, SHADFlag, PatientSSN, PseudoSSNReason, SSNVerificationStatus,
 GovernmentEmployeeFlag, SensitiveFlag, Age, BirthDateTime
)
VALUES
(1638011, 'PFIEN1011', 508, 1011, 'MeansTestIndicator', 'George',  '2025-02-10 08:30:00', 20250210, 8001, 3001, 508, 5, 100001, 100001, 100001, 2001, 100001, 'Atrial Fibrillation exacerbation', 1001, 'N', 'N', 'N', '222221011', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 72, '1953-03-15 00:00:00'),
(1638012, 'PFIEN1012', 516, 1012, 'MeansTestIndicator', 'Helen',   '2025-03-05 14:15:00', 20250305, 8001, 3001, 516, 3, 100001, 100001, 100001, 2002, 100001, 'Chest pain r/o MI', 1003, 'N', 'N', 'N', '333331012', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 68, '1957-07-22 00:00:00'),
(1638013, 'PFIEN1013', 552, 1013, 'MeansTestIndicator', 'Irving',  '2025-04-01 06:45:00', 20250401, 8001, 3001, 552, 7, 100001, 100001, 100001, 2003, 100001, 'CHF exacerbation', 1004, 'N', 'N', 'N', '444441013', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 77, '1948-11-05 00:00:00'),
(1638014, 'PFIEN1014', 508, 1014, 'MeansTestIndicator', 'Joyce',   '2025-02-28 11:20:00', 20250228, 8001, 3001, 508, 4, 100001, 100001, 100001, 2001, 100001, 'Acute on chronic pain management', 1001, 'N', 'N', 'N', '555551014', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 70, '1955-02-18 00:00:00'),
(1638015, 'PFIEN1015', 516, 1015, 'MeansTestIndicator', 'Kenneth', '2025-05-15 03:30:00', 20250515, 8001, 3001, 516, 6, 100001, 100001, 100001, 2002, 100001, 'TIA workup', 1003, 'N', 'N', 'N', '666661015', 'PseudoSSNReason', 'SSNVerificationStatus', 'N', 'N', 82, '1943-06-10 00:00:00');
GO

-- To-Do: consider addng records for Sta3n 552 (and maybe 688 WashDC)
