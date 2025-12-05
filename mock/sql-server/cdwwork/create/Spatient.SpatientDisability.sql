/*
|---------------------------------------------------------------
| Create: SPatient.SPatientDisability.sql
|---------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create SPatientDisability table in the SPatient schema
CREATE TABLE SPatient.SPatientDisability
(
  SPatientDisabilitySID      int           NOT NULL,
  PatientSID                 int           NULL,
  PatientIEN                 varchar(50)   NOT NULL,
  Sta3n                      smallint      NOT NULL,
  ClaimFolderInstitutionSID  int           NULL,
  ServiceConnectedFlag       char(1)       NULL,
  ServiceConnectedPercent    decimal(9,0)  NULL,
  AgentOrangeExposureCode    varchar(50)   NULL,
  IonizingRadiationCode      varchar(50)   NULL,
  POWStatusCode              varchar(50)   NULL,
  SHADFlag                   char(1)       NULL,
  AgentOrangeLocation        varchar(50)   NULL,
  POWLocation                varchar(50)   NULL,
  SWAsiaCode                 varchar(50)   NULL,
  CampLejeuneFlag            char(1)       NULL
);
GO

-- create indexes for the SPatient.PatientInsurance table
CREATE INDEX IX_SPatientDisabilitySID ON SPatient.SPatientDisability (SPatientDisabilitySID);
CREATE INDEX IX_PatientSID ON SPatient.SPatientDisability (PatientSID);
CREATE INDEX IX_PatientIEN ON SPatient.SPatientDisability (PatientIEN);
CREATE INDEX IX_Sta3n ON SPatient.SPatientDisability (Sta3n);
GO
