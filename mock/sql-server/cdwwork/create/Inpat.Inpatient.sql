---------------------------------------------------------------
-- Create: Inpat.Inpatient.sql
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create Inpatient table in the Inpat schema
CREATE TABLE Inpat.Inpatient
(
  InpatientSID                        BIGINT          NOT NULL,
  PTFIEN                              VARCHAR(50)     NOT NULL,
  Sta3n                               SMALLINT        NOT NULL,
  PatientSID                          INT             NULL,
  MeansTestIndicator                  VARCHAR(50)     NULL,
  PatientFirstName                    VARCHAR(30)     NULL,
  AdmitDateTime                       DATETIME2(0)    NULL,
  AdmitDateSID                        INT             NULL,
  AdmitSourceSID                      INT             NULL,
  AdmitEligibilitySID                 INT             NULL,
  TransferFromFacility                SMALLINT        NULL,
  ASIHDays                            SMALLINT        NULL,
  AdmitMASMovementTypeSID             INT             NULL,
  AdmitFacilityMovementTypeSID        INT             NULL,
  AdmitFromInstitutionSID             INT             NULL,
  AdmitWardLocationSID                INT             NULL,
  AdmitRoomBedSID                     INT             NULL,
  AdmitDiagnosis                      VARCHAR(50)     NULL,
  ProviderSID                         INT             NULL,
  HeadNeckCancerFlag                  CHAR(1)         NULL,
  IonizingRadiationFlag               CHAR(1)         NULL,
  SHADFlag                            CHAR(1)         NULL,
  PatientSSN                          VARCHAR(20)     NULL,
  PseudoSSNReason                     VARCHAR(50)     NULL,
  SSNVerificationStatus               VARCHAR(50)     NULL,
  GovernmentEmployeeFlag              CHAR(1)         NULL,
  SensitiveFlag                       CHAR(1)         NULL,
  Age                                 NUMERIC(9)      NULL,
  BirthDateTime                       DATETIME        NULL
);
GO

-- create indexes for the SPatient.Patient table
CREATE INDEX IX_InpatientSID ON Inpat.Inpatient (InpatientSID);
CREATE INDEX IX_PatientSID ON Inpat.Inpatient (PatientSID);
CREATE INDEX IX_Sta3n ON Inpat.Inpatient (Sta3n);
GO
