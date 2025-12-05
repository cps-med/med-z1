---------------------------------------------------------------
-- Create: RxOut.RxOutpatMedInstructions.sql
---------------------------------------------------------------
-- Additional patient instructions and provider comments
-- Contains free-text instructions that supplement the sig
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create RxOutpatMedInstructions table in the RxOut schema
CREATE TABLE RxOut.RxOutpatMedInstructions
(
  RxOutpatMedInstructionsSID          BIGINT         NOT NULL,
  RxOutpatMedInstructionsIEN          VARCHAR(50)    NOT NULL,
  RxOutpatSID                         BIGINT         NOT NULL,
  RxOutpatFillSID                     BIGINT         NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  InstructionType                     VARCHAR(30)    NULL,
  InstructionSequence                 INT            NULL,
  InstructionText                     VARCHAR(500)   NULL,
  SourceType                          VARCHAR(30)    NULL,
  EnteredByStaffSID                   INT            NULL,
  EnteredByStaffIEN                   VARCHAR(50)    NULL,
  EnteredDateTime                     DATETIME       NULL,
  EnteredVistaErrorDate               VARCHAR(50)    NULL,
  EnteredDateTimeTransformSID         BIGINT         NULL,
  LocalDrugSID                        BIGINT         NULL,
  NationalDrugSID                     BIGINT         NULL
);
GO

-- create indexes for the RxOut.RxOutpatMedInstructions table
CREATE INDEX IX_RxOutpatMedInstructionsSID ON RxOut.RxOutpatMedInstructions (RxOutpatMedInstructionsSID);
CREATE INDEX IX_RxOutpatMedInstructionsIEN ON RxOut.RxOutpatMedInstructions (RxOutpatMedInstructionsIEN);
CREATE INDEX IX_RxOutpatSID ON RxOut.RxOutpatMedInstructions (RxOutpatSID);
CREATE INDEX IX_RxOutpatFillSID ON RxOut.RxOutpatMedInstructions (RxOutpatFillSID);
CREATE INDEX IX_Sta3n ON RxOut.RxOutpatMedInstructions (Sta3n);
CREATE INDEX IX_PatientSID ON RxOut.RxOutpatMedInstructions (PatientSID);
CREATE INDEX IX_InstructionType ON RxOut.RxOutpatMedInstructions (InstructionType);
GO
