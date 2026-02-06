/*
|---------------------------------------------------------------
| Insert: SPatient.SPatientPhone.sql
|---------------------------------------------------------------
| 2/6/26: Added insert script to flesh out mock data
|---------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

PRINT '==============================================';
PRINT '====        SPatient.SPatientPhone        ====';
PRINT '==============================================';
GO

/*
|----------------------------------------------------------------------
| Insert Data
| ---------------------------------------------------------------------
*/

PRINT '';
PRINT '==== Insert Data ===='
GO

INSERT INTO SPatient.SPatientPhone
(
    SPatientPhoneSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber,
    PhoneType, PhoneNumber, PhoneVistaErrorDate, LastUpdated
)
VALUES
-- Patient 1: Standard Home and Cell
(1001, 1001, 'PtIEN1001', 500, 1, 'PHONE NUMBER [HOME]', '404-555-1212', NULL, GETDATE()),
(1002, 1001, 'PtIEN1001', 500, 2, 'CELLULAR PHONE NUMBER', '4045559876', NULL, GETDATE()),

-- Patient 2: Work number with Extension (Common in CDW)
(1003, 1002, 'PtIEN1002', 640, 1, 'PHONE NUMBER [HOME]', '650-555-0199', NULL, GETDATE()),
(1004, 1002, 'PtIEN1002', 640, 2, 'WORK PHONE NUMBER', '650-555-0100 EXT 443', NULL, GETDATE()),

-- Patient 3: Unformatted/Raw string
(1005, 1003, 'PtIEN1003', 442, 1, 'PHONE NUMBER [HOME]', '2125554321', NULL, GETDATE()),

-- Patient 4: Older VistA style with parentheses
(1006, 1004, 'PtIEN1004', 528, 1, 'PHONE NUMBER [HOME]', '(716) 555-8812', NULL, GETDATE()),

-- Patient 5: No home phone, only Cell
(1007, 1005, 'PtIEN1005', 612, 1, 'CELLULAR PHONE NUMBER', '312-555-7766', NULL, GETDATE()),

-- Patient 6: Generic info
(1008, 1006, 'PtIEN1006', 508, 1, 'PHONE NUMBER [HOME]', '555-555-1006', NULL, GETDATE()),

-- Patient 7: Generic info
(1009, 1007, 'PtIEN1007', 508, 1, 'PHONE NUMBER [HOME]', '555-555-1007', NULL, GETDATE()),

-- Patient 8: Generic info
(1010, 1008, 'PtIEN1008', 516, 1, 'PHONE NUMBER [HOME]', '555-555-1008', NULL, GETDATE()),

-- Patient 9: Generic info
(1011, 1009, 'PtIEN1009', 516, 1, 'PHONE NUMBER [HOME]', '555-555-1009', NULL, GETDATE()),

-- Patient 10: Generic info
(1012, 1010, 'PtIEN1010', 552, 1, 'PHONE NUMBER [HOME]', '555-555-1010', NULL, GETDATE()),

-- Patient 11: Generic info (2 records)
(1013, 1026, 'PtIEN1026', 508, 1, 'PHONE NUMBER [HOME]', '555-555-1026', NULL, GETDATE()),
(1014, 1026, 'PtIEN1026', 508, 2, 'CELLULAR PHONE NUMBER', '444-444-1026', NULL, GETDATE()),

-- Patient 12: Generic info
(1015, 1027, 'PtIEN1027', 528, 1, 'PHONE NUMBER [HOME]', '555-555-1027', NULL, GETDATE());
GO

PRINT '';
PRINT '==== Done ===='
GO