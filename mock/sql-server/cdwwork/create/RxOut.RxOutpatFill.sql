---------------------------------------------------------------
-- Create: RxOut.RxOutpatFill.sql
---------------------------------------------------------------
-- Fill/refill records for outpatient prescriptions
-- Contains individual fill transactions for each prescription
-- Related to RxOut.RxOutpat as child table (1:many)
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create RxOutpatFill table in the RxOut schema
CREATE TABLE RxOut.RxOutpatFill
(
  RxOutpatFillSID                     BIGINT         NOT NULL,
  RxOutpatFillIEN                     VARCHAR(50)    NOT NULL,
  RxOutpatSID                         BIGINT         NOT NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  LocalDrugSID                        BIGINT         NULL,
  NationalDrugSID                     BIGINT         NULL,
  FillNumber                          INT            NULL,
  FillDateTime                        DATETIME       NULL,
  FillVistaErrorDate                  VARCHAR(50)    NULL,
  FillDateTimeTransformSID            BIGINT         NULL,
  ReleasedDateTime                    DATETIME       NULL,
  ReleasedVistaErrorDate              VARCHAR(50)    NULL,
  ReleasedDateTimeTransformSID        BIGINT         NULL,
  DispensingPharmacistSID             INT            NULL,
  DispensingPharmacistIEN             VARCHAR(50)    NULL,
  VerifyingPharmacistSID              INT            NULL,
  VerifyingPharmacistIEN              VARCHAR(50)    NULL,
  PharmacySID                         INT            NULL,
  PharmacyIEN                         VARCHAR(50)    NULL,
  PharmacyName                        VARCHAR(100)   NULL,
  FillStatus                          VARCHAR(30)    NULL,
  FillType                            VARCHAR(30)    NULL,
  FillCost                            NUMERIC(12,2)  NULL,
  DispensedDrugCost                   NUMERIC(12,2)  NULL,
  QuantityDispensed                   NUMERIC(12,4)  NULL,
  DaysSupplyDispensed                 INT            NULL,
  DispenseUnit                        VARCHAR(50)    NULL,
  MailTrackingNumber                  VARCHAR(50)    NULL,
  RoutingLocation                     VARCHAR(100)   NULL,
  PrintedDateTime                     DATETIME       NULL,
  PrintedVistaErrorDate               VARCHAR(50)    NULL,
  PrintedDateTimeTransformSID         BIGINT         NULL,
  PartialFillFlag                     CHAR(1)        NULL,
  PartialFillReason                   VARCHAR(100)   NULL,
  CMOPIndicator                       CHAR(1)        NULL,
  CMOPEventNumber                     VARCHAR(50)    NULL,
  CMOPDispenseDate                    DATETIME       NULL,
  MailIndicator                       CHAR(1)        NULL,
  WindowIndicator                     CHAR(1)        NULL,
  ReturnedToStockFlag                 CHAR(1)        NULL,
  ReturnedToStockDateTime             DATETIME       NULL,
  ReturnedToStockVistaErrorDate       VARCHAR(50)    NULL,
  ReturnedToStockDateTimeTransformSID BIGINT         NULL
);
GO

-- create indexes for the RxOut.RxOutpatFill table
CREATE INDEX IX_RxOutpatFillSID ON RxOut.RxOutpatFill (RxOutpatFillSID);
CREATE INDEX IX_RxOutpatFillIEN ON RxOut.RxOutpatFill (RxOutpatFillIEN);
CREATE INDEX IX_RxOutpatSID ON RxOut.RxOutpatFill (RxOutpatSID);
CREATE INDEX IX_Sta3n ON RxOut.RxOutpatFill (Sta3n);
CREATE INDEX IX_PatientSID ON RxOut.RxOutpatFill (PatientSID);
CREATE INDEX IX_FillDateTime ON RxOut.RxOutpatFill (FillDateTime);
CREATE INDEX IX_FillNumber ON RxOut.RxOutpatFill (FillNumber);
CREATE INDEX IX_FillStatus ON RxOut.RxOutpatFill (FillStatus);
GO
