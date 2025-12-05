/*
|--------------------------------------------------------------------------------
| Insert: SPatient.SPatientDisability.sql
|--------------------------------------------------------------------------------
| Insert test data
| SPatientDisabilitySID => 1001 series
|
*/

-- Set the active database
USE CDWWork;
GO

-- Insert data into SPatient.SpatientInsurance table
INSERT INTO SPatient.SPatientDisability
(
    SPatientDisabilitySID, PatientSID, PatientIEN, Sta3n, ClaimFolderInstitutionSID, ServiceConnectedFlag, ServiceConnectedPercent, AgentOrangeExposureCode, IonizingRadiationCode, POWStatusCode, SHADFlag, AgentOrangeLocation, POWLocation, SWAsiaCode, CampLejeuneFlag
)
VALUES
(1001, 1001,    'PtIEN15401',  508, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1002, 1002,    'PtIEN15402',  508, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1003, 1003,    'PtIEN15403',  508, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1004, 1004,    'PtIEN15404',  508, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1005, 1005,    'PtIEN15405',  508, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1006, 1006,    'PtIEN15406',  516, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1007, 1007,    'PtIEN15407',  516, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1008, 1008,    'PtIEN15408',  516, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1021, 1606021, 'PtIEN887021', 508, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N'),
(1026, 1606026, 'PtIEN887026', 516, 11001, 'Y', 50.5, 'U', 'U', 'U', 'U', 'O', '6', 'U', 'N');
GO
