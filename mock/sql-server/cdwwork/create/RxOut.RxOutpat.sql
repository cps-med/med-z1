---------------------------------------------------------------
-- Create: RxOut.RxOutpat.sql
---------------------------------------------------------------
-- Main prescription/order table for outpatient pharmacy
-- Contains prescription orders with drug, provider, and prescription metadata
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create RxOutpat table in the RxOut schema
CREATE TABLE RxOut.RxOutpat
(
  RxOutpatSID                         BIGINT         NOT NULL,
  RxOutpatIEN                         VARCHAR(50)    NOT NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  LocalDrugSID                        BIGINT         NULL,
  LocalDrugIEN                        VARCHAR(50)    NULL,
  NationalDrugSID                     BIGINT         NULL,
  DrugNameWithoutDose                 VARCHAR(120)   NULL,
  DrugNameWithDose                    VARCHAR(150)   NULL,
  PrescriptionNumber                  VARCHAR(50)    NULL,
  IssueDateTime                       DATETIME       NULL,
  IssueVistaErrorDate                 VARCHAR(50)    NULL,
  IssueDateTimeTransformSID           BIGINT         NULL,
  ProviderSID                         INT            NULL,
  ProviderIEN                         VARCHAR(50)    NULL,
  OrderingProviderSID                 INT            NULL,
  OrderingProviderIEN                 VARCHAR(50)    NULL,
  EnteredByStaffSID                   INT            NULL,
  EnteredByStaffIEN                   VARCHAR(50)    NULL,
  PharmacySID                         INT            NULL,
  PharmacyIEN                         VARCHAR(50)    NULL,
  PharmacyName                        VARCHAR(100)   NULL,
  RxStatus                            VARCHAR(30)    NULL,
  RxType                              VARCHAR(30)    NULL,
  Quantity                            NUMERIC(12,4)  NULL,
  DaysSupply                          INT            NULL,
  RefillsAllowed                      INT            NULL,
  RefillsRemaining                    INT            NULL,
  MaxRefills                          INT            NULL,
  UnitDose                            VARCHAR(50)    NULL,
  ExpirationDateTime                  DATETIME       NULL,
  ExpirationVistaErrorDate            VARCHAR(50)    NULL,
  ExpirationDateTimeTransformSID      BIGINT         NULL,
  DiscontinuedDateTime                DATETIME       NULL,
  DiscontinuedVistaErrorDate          VARCHAR(50)    NULL,
  DiscontinuedDateTimeTransformSID    BIGINT         NULL,
  DiscontinueReason                   VARCHAR(100)   NULL,
  DiscontinuedByStaffSID              INT            NULL,
  LoginDateTime                       DATETIME       NULL,
  LoginVistaErrorDate                 VARCHAR(50)    NULL,
  LoginDateTimeTransformSID           BIGINT         NULL,
  ClinicSID                           INT            NULL,
  ClinicIEN                           VARCHAR(50)    NULL,
  ClinicName                          VARCHAR(100)   NULL,
  DEASchedule                         VARCHAR(10)    NULL,
  ControlledSubstanceFlag             CHAR(1)        NULL,
  CMOPIndicator                       CHAR(1)        NULL,
  MailIndicator                       CHAR(1)        NULL
);
GO

-- create indexes for the RxOut.RxOutpat table
CREATE INDEX IX_RxOutpatSID ON RxOut.RxOutpat (RxOutpatSID);
CREATE INDEX IX_RxOutpatIEN ON RxOut.RxOutpat (RxOutpatIEN);
CREATE INDEX IX_Sta3n ON RxOut.RxOutpat (Sta3n);
CREATE INDEX IX_PatientSID ON RxOut.RxOutpat (PatientSID);
CREATE INDEX IX_ProviderSID ON RxOut.RxOutpat (ProviderSID);
CREATE INDEX IX_IssueDateTime ON RxOut.RxOutpat (IssueDateTime);
CREATE INDEX IX_RxStatus ON RxOut.RxOutpat (RxStatus);
GO
