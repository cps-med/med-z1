/*
|--------------------------------------------------------------------------------
| Insert: SPatient.SPatientAddress.sql
|--------------------------------------------------------------------------------
| Insert test data
| SpatientAddressSID => 1001 series
|
*/

PRINT '================================================';
PRINT '====        SPatient.SPatientAddress        ====';
PRINT '================================================';
GO

-- set the active database
USE CDWWork;
GO

/*
|----------------------------------------------------------------------
| Insert Original Set of PatientsAddress records
| ---------------------------------------------------------------------
*/

PRINT 'Inserting Original PatientAddress records';
GO

-- insert data into SPatient.SpatientAddress table
INSERT INTO SPatient.SPatientAddress
(
    SPatientAddressSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber, AddressType, StreetAddress1,
    StreetAddress2, StreetAddress3, City, County, [State], StateSID, Zip, Zip4, PostalCode, Country,
    CountrySID, EmploymentStatus
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

/*
|--------------------------------------------------------------------------------
| Insert Additional Set of PatientsAddress records
|--------------------------------------------------------------------------------
*/

PRINT 'Inserting Additional PatientAddress records';
GO

INSERT INTO SPatient.SPatientAddress
(
    SPatientAddressSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber, AddressType, StreetAddress1,
    StreetAddress2, StreetAddress3, City, County, [State], StateSID, Zip, Zip4, PostalCode, Country,
    CountrySID, EmploymentStatus
)
VALUES
(1016, 1016, 'PtIEN1016', 688, 1, 'HOME', '1234 Constitution Ave NW', 'Apt 5B', '', 'Washington', 'District of Columbia', 'DC', 3561, '20001', '200010016', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1020, 1020, 'PtIEN1020', 688, 1, 'HOME', '5678 Wisconsin Ave NW', '', '', 'Washington', 'District of Columbia', 'DC', 3561, '20016', '200160020', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1024, 1024, 'PtIEN1024', 688, 1, 'HOME', '910 Pennsylvania Ave SE', '', '', 'Washington', 'District of Columbia', 'DC', 3561, '20003', '200030024', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1017, 1017, 'PtIEN1017', 508, 1, 'HOME', '2468 Clairmont Rd', '', '', 'Decatur', 'DeKalb', 'GA', 415, '30033', '300330017', '', 'UNITED STATES', 1200005271, 'UNEMPLOYED'),
(1021, 1021, 'PtIEN1021', 508, 1, 'HOME', '1357 Memorial Dr SE', '', '', 'Atlanta', 'Fulton', 'GA', 415, '30312', '303120021', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1018, 1018, 'PtIEN1018', 516, 1, 'HOME', '753 Kapiolani Blvd', 'Unit 12', '', 'Honolulu', 'Honolulu', 'HI', 1792, '96814', '968140018', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1022, 1022, 'PtIEN1022', 516, 1, 'HOME', '951 Ala Moana Blvd', '', '', 'Honolulu', 'Honolulu', 'HI', 1792, '96814', '968140022', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1025, 1025, 'PtIEN1025', 516, 1, 'HOME', '357 King Street', 'Apt 8C', '', 'Honolulu', 'Honolulu', 'HI', 1792, '96813', '968130025', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1019, 1019, 'PtIEN1019', 552, 1, 'HOME', '246 Oakwood Ave', '', '', 'Dayton', 'Montgomery', 'OH', 4963, '45419', '454190019', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1023, 1023, 'PtIEN1023', 552, 1, 'HOME', '159 Shiloh Springs Rd', '', '', 'Dayton', 'Montgomery', 'OH', 4963, '45415', '454150023', '', 'UNITED STATES', 1200005271, 'RETIRED');
GO

PRINT 'Inserting Additional PatientAddress records';
GO

INSERT INTO SPatient.SPatientAddress
(
    SPatientAddressSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber, AddressType, StreetAddress1,
    StreetAddress2, StreetAddress3, City, County, [State], StateSID, Zip, Zip4, PostalCode, Country,
    CountrySID, EmploymentStatus
)
VALUES
(1011, 1011, 'PtIEN1011', 508, 1, 'HOME', '1234 Peachtree Street NE', '', '', 'Decatur', 'DeKalb', 'GA', 415, '30033', '300330011', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1012, 1012, 'PtIEN1012', 516, 1, 'HOME', '5678 Gulf Boulevard', 'Apt 12B', '', 'Bay Pines', 'Pinellas', 'FL', 1792, '33744', '337440012', '', 'UNITED STATES', 1200002442, 'RETIRED'),
(1013, 1013, 'PtIEN1013', 552, 1, 'HOME', '910 Main Street', '', '', 'Dayton', 'Montgomery', 'OH', 4963, '45402', '454020013', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1014, 1014, 'PtIEN1014', 508, 1, 'HOME', '2468 Buford Highway', '', '', 'Decatur', 'DeKalb', 'GA', 415, '30032', '300320014', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1015, 1015, 'PtIEN1015', 516, 1, 'HOME', '7890 Seminole Boulevard', '', '', 'Bay Pines', 'Pinellas', 'FL', 1792, '33708', '337080015', '', 'UNITED STATES', 1200002442, 'RETIRED');
GO
