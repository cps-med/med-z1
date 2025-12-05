/*
|--------------------------------------------------------------------------------
| Insert: SStaff.RadiologyNuclearMedicineReport.sql
|--------------------------------------------------------------------------------
| Insert test data
| RadiologyNuclearMedicineReportSID => 2001 series
|
*/

-- Set the active database
USE CDWWork;
GO

-- Insert data into SStaff.RadiologyNuclearMedicineReport table
INSERT INTO SStaff.RadiologyNuclearMedicineReport
(
    RadiologyNuclearMedicineReportSID, RadiologyNuclearMedicineReportIEN, Sta3n, DayCase, PatientSID, ExamDateTime, CaseNumber, ReportStatus, RadiologyLocationSID

)
VALUES
(2001, 'RadNucMedRepIEN1001', 508, '111-222222-3001', 1001, '2025-01-01 09:05:01', 4001.0000, 'V', 1001),
(2002, 'RadNucMedRepIEN1002', 508, '111-222222-3002', 1002, '2025-01-01 09:05:02', 4002.0000, 'V', 1002),
(2003, 'RadNucMedRepIEN1003', 508, '111-222222-3003', 1003, '2025-01-01 09:05:03', 4003.0000, 'V', 1003),
(2004, 'RadNucMedRepIEN1004', 508, '111-222222-3004', 1004, '2025-01-01 09:05:04', 4004.0000, 'V', 1004),
(2005, 'RadNucMedRepIEN1005', 508, '111-222222-3005', 1005, '2025-02-01 09:05:05', 4005.0000, 'V', 1005),
(2006, 'RadNucMedRepIEN1006', 516, '111-222222-3006', 1006, '2025-02-01 09:05:06', 4006.0000, 'V', 1006),
(2007, 'RadNucMedRepIEN1007', 516, '111-222222-3006', 1007, '2025-02-01 09:05:06', 4007.0000, 'V', 1007),
(2008, 'RadNucMedRepIEN1008', 516, '111-222222-3006', 1008, '2025-02-01 09:05:06', 4008.0000, 'V', 1008);
GO
