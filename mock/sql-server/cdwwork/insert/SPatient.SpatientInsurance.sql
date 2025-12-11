/*
|--------------------------------------------------------------------------------
| Insert: SPatient.SPatientInsurance.sql
|--------------------------------------------------------------------------------
| Insert test data with correct InsuranceCompanySID values
| Updated 2025-12-11 to use Dim.InsuranceCompany foreign keys
| SPatientInsuranceSID => 1001 series
|--------------------------------------------------------------------------------
*/

PRINT '================================================';
PRINT '====     SPatient.SPatientInsurance         ====';
PRINT '================================================';
GO

-- Set the active database
USE CDWWork;
GO

-- Clear existing data
DELETE FROM SPatient.SPatientInsurance;
GO

-- Insert data into SPatient.SPatientInsurance table
-- Using InsuranceCompanySID values from Dim.InsuranceCompany:
--   1=Medicare, 2=Medicaid, 3=TRICARE, 4=VA, 5=Veterans Affairs
--   10=BCBS, 11=Aetna, 12=UnitedHealthcare, 13=Cigna, 14=Humana
--   20=Kaiser, 21=Anthem, 22=Centene, 23=Molina
--   90=Uninsured, 91=Unknown, 92=Self-Pay

INSERT INTO SPatient.SPatientInsurance
(
    SPatientInsuranceSID, PatientSID, PatientIEN, SPatientInsuranceIEN, Sta3n,
    InsuranceCompanySID, EmploymentStatus, RetirementDate, PolicyEffectiveDate
)
VALUES
-- Patients with Medicare (government program for elderly/disabled)
(1001, 1001, 'PtIEN1001', 'PtInsIEN0001', 508, 1, 'FULL TIME', '2021-01-02', '2010-02-15'),
(1002, 1011, 'PtIEN1011', 'PtInsIEN0011', 508, 1, 'RETIRED', '2020-03-15', '2018-03-20'),
(1003, 1012, 'PtIEN1012', 'PtInsIEN0012', 516, 1, 'RETIRED', '2022-07-22', '2019-08-01'),
(1004, 1013, 'PtIEN1013', 'PtInsIEN0013', 552, 1, 'RETIRED', '2015-11-05', '2016-01-01'),
(1005, 1015, 'PtIEN1015', 'PtInsIEN0015', 516, 1, 'RETIRED', '2010-06-10', '2011-01-01'),

-- Patients with Medicaid (government program for low-income)
(1006, 1002, 'PtIEN1002', 'PtInsIEN0002', 508, 2, 'FULL TIME', NULL, '2015-03-10'),
(1007, 1606020, 'PtIEN887020', 'PtInsIEN0020', 508, 2, 'EMPLOYED', NULL, '2020-10-15'),

-- Patients with TRICARE (military)
(1008, 1006, 'PtIEN1006', 'PtInsIEN0006', 508, 3, 'FULL TIME', NULL, '2005-05-15'),
(1009, 1007, 'PtIEN1007', 'PtInsIEN0007', 516, 3, 'FULL TIME', '2008-01-02', '2006-01-02'),

-- Patients with VA/Veterans Affairs
(1010, 1014, 'PtIEN1014', 'PtInsIEN0014', 508, 4, 'RETIRED', '2021-02-18', '2021-03-01'),
(1011, 1606026, 'PtIEN887026', 'PtInsIEN0026', 516, 5, 'FULL TIME', NULL, '2022-07-15'),

-- Patients with Blue Cross Blue Shield
(1012, 1003, 'PtIEN1003', 'PtInsIEN0003', 508, 10, 'FULL TIME', NULL, '2012-01-02'),
(1013, 1016, 'PtIEN1016', 'PtInsIEN1016', 688, 10, 'EMPLOYED', NULL, '2023-03-15'),
(1014, 1020, 'PtIEN1020', 'PtInsIEN1020', 688, 10, 'EMPLOYED', NULL, '2018-09-30'),

-- Patients with Aetna
(1015, 1004, 'PtIEN1004', 'PtInsIEN0004', 508, 11, 'RETIRED', '2019-01-02', '2019-02-01'),
(1016, 1017, 'PtIEN1017', 'PtInsIEN1017', 508, 11, 'EMPLOYED', NULL, '2022-07-22'),

-- Patients with UnitedHealthcare
(1017, 1005, 'PtIEN1005', 'PtInsIEN0005', 508, 12, 'RETIRED', '2020-05-15', '2020-06-01'),
(1018, 1018, 'PtIEN1018', 'PtInsIEN1018', 516, 12, 'EMPLOYED', NULL, '2021-11-08'),
(1019, 1024, 'PtIEN1024', 'PtInsIEN1024', 688, 12, 'RETIRED', '2018-02-11', '2018-03-01'),

-- Patients with Cigna
(1020, 1008, 'PtIEN1008', 'PtInsIEN0008', 516, 13, 'EMPLOYED', NULL, '2016-01-02'),
(1021, 1019, 'PtIEN1019', 'PtInsIEN1019', 552, 13, 'EMPLOYED', NULL, '2020-05-14'),

-- Patients with Humana
(1022, 1009, 'PtIEN1009', 'PtInsIEN0009', 516, 14, 'RETIRED', '2018-01-02', '2018-02-01'),
(1023, 1021, 'PtIEN1021', 'PtInsIEN1021', 508, 14, 'RETIRED', '2021-12-03', '2022-01-01'),

-- Patients with Kaiser Permanente
(1024, 1010, 'PtIEN1010', 'PtInsIEN0010', 552, 20, 'EMPLOYED', NULL, '2019-07-15'),

-- Patients with Anthem
(1025, 1022, 'PtIEN1022', 'PtInsIEN1022', 516, 21, 'EMPLOYED', NULL, '2017-04-17'),
(1026, 1025, 'PtIEN1025', 'PtInsIEN1025', 516, 21, 'RETIRED', '2012-06-19', '2012-07-01'),

-- Patients with Centene
(1027, 1023, 'PtIEN1023', 'PtInsIEN1023', 552, 22, 'EMPLOYED', NULL, '2015-08-25'),

-- Patients who are Uninsured
(1028, 1606022, 'PtIEN887022', 'PtInsIEN0022', 508, 90, 'UNEMPLOYED', NULL, '2024-10-02'),
(1029, 1606024, 'PtIEN887024', 'PtInsIEN0024', 508, 90, 'EMPLOYED', NULL, '2020-01-27'),

-- Patients with Unknown insurance
(1030, 1606023, 'PtIEN887023', 'PtInsIEN0023', 508, 91, 'EMPLOYED', NULL, '2023-08-22'),
(1031, 1606027, 'PtIEN887027', 'PtInsIEN0027', 552, 91, 'EMPLOYED', NULL, '2024-07-19'),

-- Patients with Self-Pay
(1032, 1606025, 'PtIEN887025', 'PtInsIEN0025', 508, 92, 'RETIRED', '2010-01-01', '2010-02-01'),
(1033, 1606030, 'PtIEN887030', 'PtInsIEN0030', 552, 92, 'RETIRED', '2012-01-01', '2012-02-01');
GO

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' insurance records with correct InsuranceCompanySID values';
GO

-- Verify data
SELECT TOP 10
    si.SPatientInsuranceSID,
    si.PatientSID,
    si.InsuranceCompanySID,
    ic.InsuranceCompanyName,
    si.PolicyEffectiveDate
FROM SPatient.SPatientInsurance si
LEFT JOIN Dim.InsuranceCompany ic ON si.InsuranceCompanySID = ic.InsuranceCompanySID
ORDER BY si.SPatientInsuranceSID;
GO
