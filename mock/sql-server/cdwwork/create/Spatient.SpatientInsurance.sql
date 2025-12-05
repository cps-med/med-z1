/*
|---------------------------------------------------------------
| Create: SPatient.SPatientInsurance.sql
|---------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create SPatientInsurance table in the SPatient schema
CREATE TABLE SPatient.SPatientInsurance
(
  SPatientInsuranceSID      int           NOT NULL,
  PatientSID                int           NULL,
  PatientIEN                varchar(50)   NOT NULL,
  SPatientInsuranceIEN      varchar(50)   NOT NULL,
  Sta3n                     smallint      NOT NULL,
  InsuranceCompanySID       int           NULL,
  EmploymentStatus          varchar(50)   NULL,
  RetirementDate            date          NULL,
  PolicyEffectiveDate       date          NULL
);
GO

-- create indexes for the SPatient.PatientInsurance table
CREATE INDEX IX_SPatientInsuranceSID ON SPatient.SPatientInsurance (SPatientInsuranceSID);
CREATE INDEX IX_PatientSID ON SPatient.SPatientInsurance (PatientSID);
CREATE INDEX IX_PatientIEN ON SPatient.SPatientInsurance (PatientIEN);
CREATE INDEX IX_Sta3n ON SPatient.SPatientInsurance (Sta3n);
GO
