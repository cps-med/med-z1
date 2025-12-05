---------------------------------------------------------------
-- Create: RxOut.RxOutpatSig.sql
---------------------------------------------------------------
-- Structured medication directions (sig) for prescriptions
-- Contains discrete components of dosing instructions
-- (DOSAGE, VERB, ROUTE, SCHEDULE, DURATION, etc.)
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create RxOutpatSig table in the RxOut schema
CREATE TABLE RxOut.RxOutpatSig
(
  RxOutpatSigSID                      BIGINT         NOT NULL,
  RxOutpatSigIEN                      VARCHAR(50)    NOT NULL,
  RxOutpatSID                         BIGINT         NOT NULL,
  RxOutpatFillSID                     BIGINT         NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  SegmentNumber                       INT            NULL,
  DosageOrdered                       VARCHAR(50)    NULL,
  Verb                                VARCHAR(50)    NULL,
  DispenseUnitsPerDose                VARCHAR(50)    NULL,
  Noun                                VARCHAR(50)    NULL,
  Route                               VARCHAR(50)    NULL,
  Schedule                            VARCHAR(50)    NULL,
  ScheduleType                        VARCHAR(30)    NULL,
  ScheduleTypeIEN                     VARCHAR(50)    NULL,
  Duration                            VARCHAR(50)    NULL,
  Conjunction                         VARCHAR(20)    NULL,
  AdminTimes                          VARCHAR(100)   NULL,
  CompleteSignature                   VARCHAR(500)   NULL,
  SigSequence                         INT            NULL,
  LocalDrugSID                        BIGINT         NULL,
  NationalDrugSID                     BIGINT         NULL
);
GO

-- create indexes for the RxOut.RxOutpatSig table
CREATE INDEX IX_RxOutpatSigSID ON RxOut.RxOutpatSig (RxOutpatSigSID);
CREATE INDEX IX_RxOutpatSigIEN ON RxOut.RxOutpatSig (RxOutpatSigIEN);
CREATE INDEX IX_RxOutpatSID ON RxOut.RxOutpatSig (RxOutpatSID);
CREATE INDEX IX_RxOutpatFillSID ON RxOut.RxOutpatSig (RxOutpatFillSID);
CREATE INDEX IX_Sta3n ON RxOut.RxOutpatSig (Sta3n);
CREATE INDEX IX_PatientSID ON RxOut.RxOutpatSig (PatientSID);
GO
