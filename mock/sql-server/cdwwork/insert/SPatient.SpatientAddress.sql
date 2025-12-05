/*
|--------------------------------------------------------------------------------
| Insert: SPatient.SPatientAddress.sql
|--------------------------------------------------------------------------------
| Insert test data
| SpatientAddressSID => 1001 series
|
*/

-- set the active database
USE CDWWork;
GO

-- insert data into SPatient.SpatientAddress table
INSERT INTO SPatient.SPatientAddress
(
    SPatientAddressSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber, AddressType, StreetAddress1, StreetAddress2, StreetAddress3, City, County, [State], StateSID, Zip, Zip4, PostalCode, Country, CountrySID, EmploymentStatus
)
VALUES
(1001, 1001, 'PtIEN15401', 508, 1, 'HOME', '110 Main St', 'Apt 1', '', 'Atlanta', 'Dekalb', 'GA', 415, '30303', '303031001', '', 'UNITED STATES', 1200005271, 'EMPLOYED FULL TIME'),
(1002, 1002, 'PtIEN15402', 508, 1, 'HOME', '110 Main St', 'Apt 2', '', 'Atlanta', 'Dekalb', 'GA', 415, '30303', '303031002', '', 'UNITED STATES', 1200005271, 'EMPLOYED FULL TIME'),
(1003, 1003, 'PtIEN15403', 508, 1, 'HOME', '110 Main St', 'Apt 3', '', 'Atlanta', 'Dekalb', 'GA', 415, '30303', '303031003', '', 'UNITED STATES', 1200005271, 'EMPLOYED PART TIME'),
(1004, 1004, 'PtIEN15404', 508, 1, 'HOME', '110 Main St', 'Apt 4', '', 'Atlanta', 'Dekalb', 'GA', 415, '30303', '303031004', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1005, 1006, 'PtIEN15406', 516, 1, 'HOME', '110 Beach Ln', 'Apt 5', '', 'St. Petersburg', 'Pinellas', 'FL', 1792, '33744', '337441005', '', 'UNITED STATES', 1200002442, 'RETIRED'),
(1006, 1007, 'PtIEN15405', 516, 1, 'HOME', '110 Beach Ln', 'Apt 5', '', 'St. Petersburg', 'Pinellas', 'FL', 1792, '33744', '337441005', '', 'UNITED STATES', 1200002442, 'RETIRED'),
(1007, 1007, 'PtIEN15405', 516, 2, 'HOME', '210 Beach Ln', 'Apt 1', '', 'St. Petersburg', 'Pinellas', 'FL', 1792, '33744', '337441005', '', 'UNITED STATES', 1200002442, 'RETIRED'),
(1008, 1001, 'PtIEN15401', 508, 2, 'HOME', '110 Dogwood Dr', '', '', 'Atlanta', 'Fulton', 'GA', 415, '30303', '303031001', '', 'UNITED STATES', 1200005271, 'EMPLOYED FULL TIME'),
(1009, 1001, 'PtIEN15401', 508, 3, 'HOME', '210 Dogwood Dr', '', '', 'Atlanta', 'Fulton', 'GA', 415, '30303', '303031001', '', 'UNITED STATES', 1200005271, 'EMPLOYED FULL TIME'),
(1010, 1005, 'PtIEN15405', 508, 1, 'HOME', '901 Avery St', 'Apt 101', '', 'Decatur', 'Dekalb', 'GA', 415, '30303', '303031001', '', 'UNITED STATES', 1200005271, 'RETIRED'),

-- Add address for Donn Duck
(10211, 1606021, 'PtIEN887021', 508, 1, 'HOME', '121 Disney Ave', 'Apt 101', '', 'Druid Hills', 'Dekalb', 'GA', 415, '30321', '303021001', '', 'UNITED STATES', 1200005271, 'EMPLOYED PART TIME'),
(10212, 1606021, 'PtIEN887021', 508, 2, 'HOME', '121 Disney Ave', 'Apt 102', '', 'Druid Hills', 'Dekalb', 'GA', 415, '30321', '303021001', '', 'UNITED STATES', 1200005271, 'EMPLOYED PART TIME'),
(10213, 1606021, 'PtIEN887021', 508, 3, 'HOME', '121 Disney Ave', 'Apt 103', '', 'Druid Hills', 'Dekalb', 'GA', 415, '30321', '303021001', '', 'UNITED STATES', 1200005271, 'EMPLOYED PART TIME'),

-- Add address for ZZZ TEST
(10221, 1606026, 'PtIEN887026', 516, 1, 'HOME', '305 ZZ Circle', '', '', 'St. Petersburg', 'Pinellas', 'FL', 1792, '33744', '337441026', '', 'UNITED STATES', 1200005271, 'RETIRED');
GO
