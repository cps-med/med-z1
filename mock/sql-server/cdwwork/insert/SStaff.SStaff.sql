/*
|--------------------------------------------------------------------------------
| Insert: SStaff.SStaff.sql
|--------------------------------------------------------------------------------
| Insert test data
| SStaffSID => 1001 series
|
*/

PRINT '==== SStaff.SStaff ====';
GO

-- Set the active database
USE CDWWork;
GO

-- Insert data into SStaff.Staff table
INSERT INTO SStaff.SStaff
(
    StaffSID, StaffIEN, Sta3n, StaffName, LastName, FirstName, MiddleName, StaffNamePrefix, StaffNameSuffix, StaffSSN, NetworkUsername, DEA, NPI

)
VALUES
(1001, 'StaffIEN1001', 508, 'Walter Reed', 'Reed', 'Walter', 'Q', '', '', '111111111', 'NetworkUserName', 'DEA1001', 'StaffNPI1001'),
(1002, 'StaffIEN1002', 508, 'Marie Curry', 'Curry', 'Marie', 'Q', '', '', '222222222', 'NetworkUserName', 'DEA1002', 'StaffNPI1002'),
(1003, 'StaffIEN1003', 516, 'Florence Nightengale', 'Nightingale', 'Florence', '', '', '', '333333333', 'NetworkUserName', 'DEA1003', 'StaffNPI1003'),
(1004, 'StaffIEN1004', 516, 'Carl Sagan', 'Sagan', 'Carl', 'Q', '', '', '444444444', 'NetworkUserName', 'DEA1004', 'StaffNPI1004'),
(1005, 'StaffIEN1005', 552, 'Louis Pasteur ', 'Pasteur', 'Louis', '', '', '', '111223333', 'NetworkUserName', 'DEA1005', 'StaffNPI1005'),
(1006, 'StaffIEN1006', 552, 'Julius Hibbert', 'Hibbert', 'Julius', 'M', '', '', '111224444', 'NetworkUserName', 'DEA1006', 'StaffNPI1006');
GO
