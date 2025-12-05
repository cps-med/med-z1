/*
|--------------------------------------------------------------------------------
| Insert: Inpat.ProvisionalMovement.sql
|--------------------------------------------------------------------------------
| Insert test data
| ProvisionalMovementSID => 5001 series
|
| Still working on creating this test data set... not ready for master script.
|
*/

PRINT '==> Inpat.ProvisionalMovement...';
GO

-- set the active database
USE CDWWork;
GO

-- insert data into the Inpat.PatientTransfer table
INSERT INTO Inpat.ProvisionalMovement
(
 ProvisionalMovementSID, ProvisionalMovementIEN, Sta3n, InpatientSID, OrdinalNumber, NextOrdinalNumber, PatientSID, PatientMovementDateTime, PatientMovementVistaErrorDate, PatientMovementDateTimeTransformSID, MASMovementTypeSID, MASTransactionTypeSID, FacilityMovementTypeSID, TransferInstitutionSID, WardLocationSID, RoomBedSID, PrimaryPhysicianStaffSID, TreatingSpecialtySID, AdmittingDiagnosis, ASIHAdmissionPatientMovementSID, DischargeCheckOutPatientMovementSID, RelatedPhysicalPatientMovementSID, AttendingPhysicianStaffSID, ASIHTransferPatientMovementSID, ASIHSequence, ScheduledAdmissionFlag, EnteredByStaffSID, EnteredOnDateTime, LastEditedByStaffSID, LastEditedOnDateTime, NonVAFacilityFlag, Disposition
)
VALUES
(5001, 'IEN05001', 508, 1638001, NULL, NULL, 1001,    '2025-01-01 10:10:05', 'vista_error_date', 330033001, 101, 101, 101, -1, 2001, 3010001,    -1, 990000001, 'PNEUMONIA',            1001,  0, 60000001,   1006, 999, 1, 'X', 1006, '2025-01-01 09:30:00', 1005,       '2025-01-01 08:00:00', 'X', 'disposition'),
(5002, 'IEN05002', 508, 1638002, NULL, NULL, 1002,    '2025-01-02 11:11:06', 'vista_error_date', 330033002, 102, 102, 102, -1, 2001, 3010002,    -1, 990000001, 'COPD',                 1001,  1, 60000002,   1006, 999, 1, 'X', 1006, '2025-01-02 09:00:00', 70000002,   '2025-01-02 09:30:00', 'X', 'disposition'),
(5003, 'IEN05003', 508, 1638003, NULL, NULL, 1003,    '2025-01-02 13:22:04', 'vista_error_date', 330033003, 103, 103, 103, -1, 2001, 1200062221, -1, -1,        'RENAL FAILURE',        1002,  0, 1621550001, 1006, 999, 1, 'X', 1006, '2025-01-02 13:22:05', 1621550001, '2025-01-02 13:22:25', 'X', 'disposition'),
(5004, 'IEN05004', 508, 1638004, NULL, NULL, 1004,    '2025-01-01 12:25:05', 'vista_error_date', 330033004, 104, 104, 104, -1, 2001, 3010004,    -1, 990000001, 'ELEVATED BLOOD COUNT', 1002,  0, 60000004,   1006, 999, 1, 'X', 1006, '2025-01-01 09:00:00', 70000004,   '2025-01-01 09:30:00', 'X', 'disposition'),
(5005, 'IEN05005', 508, 1638005, NULL, NULL, 1005,    '2025-01-03 12:35:30', 'vista_error_date', 330033005, 105, 105, 105, -1, 2001, 3010004,    -1, 990000001, 'CHEST PAIN',           1002,  0, 60000004,   1006, 999, 1, 'X', 1006, '2025-01-01 09:00:00', 70000005,   '2025-01-01 09:30:00', 'X', 'disposition'),
(5006, 'IEN05006', 508, 1638006, NULL, NULL, 1006,    '2025-01-02 09:01:02', 'vista_error_date', 330033006, 105, 105, 105, -1, 2001, 3010004,    -1, 990000001, 'DEPRESSION',           1002,  0, 60000004,   1006, 999, 1, 'X', 1006, '2025-02-01 09:01:02', 70000004,   '2025-01-02 09:30:00', 'X', 'disposition'),
(5007, 'IEN05007', 516, 1638007, NULL, NULL, 1007,    '2025-01-01 08:35:27', 'vista_error_date', 330033007, 106, 106, 106, -1, 2006, 3010004,    -1, 990000001, 'COPD',                 1001,  0, 60000001,   1006, 999, 1, 'X', 1006, '2025-01-01 09:10:10', 70000001,   '2025-01-01 13:30:25', 'X', 'disposition'),
(5008, 'IEN05008', 516, 1638008, NULL, NULL, 1008,    '2025-01-01 09:25:25', 'vista_error_date', 330033008, 106, 106, 106, -1, 2006, 3010001,    -1, 990000001, 'ELEVATED BLOOD COUNT', 1001,  0, 60000001,   1006, 999, 1, 'X', 1006, '2025-01-01 09:11:12', 70000001,   '2025-01-01 15:01:01', 'X', 'disposition'),
(5010, 'IEN05010', 552, 1638010, NULL, NULL, 1010,    '2025-01-03 04:01:02', 'vista_error_date', 330033010, 106, 106, 106, -1, 2006, 3010001,    -1, 990000001, 'CHEST PAIN',           1001,  0, 60000001,   1006, 999, 1, 'X', 1006, '2025-01-03 09:11:12', 70000001,   '2025-01-03 15:01:01', 'X', 'disposition'),
(5021, 'IEN05021', 508, 1638021, NULL, NULL, 1606021, '2025-01-03 04:01:02', 'vista_error_date', 330033010, 106, 106, 106, -1, 2001, 3010001,    -1, 990000001, 'PNEUMONIA',            1001,  0, 60000001,   1006, 999, 1, 'X', 1006, '2025-01-03 09:11:12', 70000002,   '2025-01-03 15:01:01', 'X', 'disposition'),
(5026, 'IEN05026', 516, 1638026, NULL, NULL, 1606026, '2025-01-03 05:02:03', 'vista_error_date', 330033011, 106, 106, 106, -1, 2006, 3010001,    -1, 990000001, 'RENAL FAILURE',        1001,  0, 60000001,   1006, 999, 1, 'X', 1006, '2025-01-03 10:11:12', 70000005,   '2025-01-03 15:01:01', 'X', 'disposition');
GO
