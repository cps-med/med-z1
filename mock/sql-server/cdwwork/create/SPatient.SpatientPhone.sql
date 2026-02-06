/*
|---------------------------------------------------------------
| Create: SPatient.SPatientPhone.sql
|---------------------------------------------------------------
| 2/6/2026: added table, so that mock data and resulting
| PostgreSQL database will include phone number values.
|---------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

PRINT '================================================';
PRINT '====           SPatient.SPatientPhone       ====';
PRINT '================================================';
GO

-- create SPatientPhone table in the SPatient schema

PRINT '';
PRINT '==== Create Table ===='
GO

CREATE TABLE SPatient.SPatientPhone
(
  SPatientPhoneSID          int           NOT NULL,
  PatientSID                int           NULL,
  PatientIEN                varchar(50)   NOT NULL,
  Sta3n                     smallint      NOT NULL,
  OrdinalNumber             smallint      NOT NULL,
  PhoneType                 varchar(50)   NULL,  -- e.g., 'PHONE NUMBER [HOME]', 'WORK PHONE NUMBER'
  PhoneNumber               varchar(50)   NULL,  -- Accommodates text, formatting, and extensions
  PhoneVistaErrorDate       varchar(50)   NULL,  -- Mimics CDW handling of malformed VistA dates if applicable
  LastUpdated               datetime      NULL
);
GO

-- create indicies for the SPatient.SPatientPhone table

PRINT '';
PRINT '==== Create Indices ===='
GO

CREATE INDEX IX_SPatientPhoneSID ON SPatient.SPatientPhone (SPatientPhoneSID);
CREATE INDEX IX_PatientSID ON SPatient.SPatientPhone (PatientSID);
CREATE INDEX IX_PatientIEN ON SPatient.SPatientPhone (PatientIEN);
CREATE INDEX IX_Sta3n ON SPatient.SPatientPhone (Sta3n);
GO

PRINT '';
PRINT '==== Done ===='
GO