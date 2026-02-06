/*
|---------------------------------------------------------------
| Create: SPatient.SPatientAddress.sql
|---------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create SPatientAddress table in the SPatient schema
CREATE TABLE SPatient.SPatientAddress
(
  SPatientAddressSID        int           NOT NULL,
  PatientSID                int           NULL,
  PatientIEN                varchar(50)   NOT NULL,
  Sta3n                     smallint      NOT NULL,
  OrdinalNumber             smallint      NOT NULL,
  AddressType               varchar(50)   NULL,
  StreetAddress1            varchar(50)   NULL,
  StreetAddress2            varchar(50)   NULL,
  StreetAddress3            varchar(50)   NULL,
  City                      varchar(50)   NULL,
  County                    varchar(50)   NULL,
  [State]                   varchar(30)   NULL,
  StateSID                  int           NULL,
  Zip                       varchar(50)   NULL,
  Zip4                      varchar(50)   NULL,
  PostalCode                varchar(50)   NULL,
  Country                   varchar(100)  NULL,
  CountrySID                int           NULL,
  EmploymentStatus          varchar(50)   NULL                  
);
GO

-- create indexes for the SPatient.PatientAddress table
CREATE INDEX IX_SPatientAddressSID ON SPatient.SPatientAddress (SPatientAddressSID);
CREATE INDEX IX_PatientSID ON SPatient.SPatientAddress (PatientSID);
CREATE INDEX IX_PatientIEN ON SPatient.SPatientAddress (PatientIEN);
CREATE INDEX IX_Sta3n ON SPatient.SPatientAddress (Sta3n);
GO
