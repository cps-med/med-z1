/*
|--------------------------------------------------------------------------------
| Insert: SPatient.SPatientInsurance.sql
|--------------------------------------------------------------------------------
| Insert test data
| SPatientInsuranceSID => 1001 series
|
*/

-- Set the active database
USE CDWWork;
GO

-- Insert data into SPatient.SpatientInsurance table
INSERT INTO SPatient.SPatientInsurance
(
    SPatientInsuranceSID, PatientSID, PatientIEN, SPatientInsuranceIEN, Sta3n, InsuranceCompanySID, EmploymentStatus, RetirementDate, PolicyEffectiveDate
)
VALUES
(1001, 1001, 'PtIEN15401', 'PtInsIEN0001', 508, 130001, 'FULL TIME', '2021-01-02', '1998-02-15'),
(1002, 1002, 'PtIEN15402', 'PtInsIEN0002', 508, 130001, 'FULL TIME', '2021-02-02', '1998-02-15'),
(1003, 1003, 'PtIEN15403', 'PtInsIEN0003', 508, 130001, 'PART TIME', '2021-03-02', '1998-02-15'),
(1004, 1004, 'PtIEN15404', 'PtInsIEN0004', 508, 130001, 'RETIRED', '2021-04-02', '1998-02-15'),
(1005, 1005, 'PtIEN15405', 'PtInsIEN0005', 508, 130001, 'RETIRED', '2021-05-02', '1998-02-15'),
(1006, 1001, 'PtIEN15401', 'PtInsIEN0001', 508, 130001, 'FULL TIME', '2021-01-02', '1999-07-15'),
(1007, 1006, 'PtIEN15406', 'PtInsIEN0006', 516, 130001, 'FULL TIME', '2021-01-02', '1999-07-15'),
(1008, 1007, 'PtIEN15407', 'PtInsIEN0007', 516, 130001, 'FULL TIME', '2021-01-02', '1999-07-15'),
(1009, 1008, 'PtIEN15408', 'PtInsIEN0008', 516, 130001, 'FULL TIME', '2021-01-02', '1999-07-15'),
(1026, 1606026, 'PtIEN887026', 'PtInsIEN0008', 516, 130001, 'FULL TIME', '2021-01-02', '1999-07-15');
GO
