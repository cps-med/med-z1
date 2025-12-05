---------------------------------------------------------------
-- Create: BCMA.BCMAAdditive.sql
---------------------------------------------------------------
-- Additives for IV medications in BCMA
-- Contains information about drugs/medications added to IV solutions
-- (e.g., potassium chloride added to IV bag, medications added to TPN)
-- Related to BCMA.BCMAMedicationLog and BCMA.BCMADispensedDrug
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create BCMAAdditive table in the BCMA schema
CREATE TABLE BCMA.BCMAAdditive
(
  BCMAAdditiveSID                     BIGINT         NOT NULL,
  BCMAAdditiveIEN                     VARCHAR(50)    NOT NULL,
  BCMAMedicationLogSID                BIGINT         NOT NULL,
  BCMADispensedDrugSID                BIGINT         NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  InpatientSID                        BIGINT         NULL,
  InpatientIEN                        VARCHAR(50)    NULL,
  AdditiveName                        VARCHAR(120)   NULL,
  AdditiveStrength                    VARCHAR(50)    NULL,
  AdditiveAmount                      NUMERIC(12,4)  NULL,
  AdditiveUnit                        VARCHAR(50)    NULL,
  AdditiveSequence                    INT            NULL,
  LocalDrugSID                        BIGINT         NULL,
  LocalDrugIEN                        VARCHAR(50)    NULL,
  NationalDrugSID                     BIGINT         NULL,
  AdditiveType                        VARCHAR(50)    NULL,
  OrderNumber                         VARCHAR(50)    NULL
);
GO

-- create indexes for the BCMA.BCMAAdditive table
CREATE INDEX IX_BCMAAdditiveSID ON BCMA.BCMAAdditive (BCMAAdditiveSID);
CREATE INDEX IX_BCMAAdditiveIEN ON BCMA.BCMAAdditive (BCMAAdditiveIEN);
CREATE INDEX IX_BCMAMedicationLogSID ON BCMA.BCMAAdditive (BCMAMedicationLogSID);
CREATE INDEX IX_BCMADispensedDrugSID ON BCMA.BCMAAdditive (BCMADispensedDrugSID);
CREATE INDEX IX_Sta3n ON BCMA.BCMAAdditive (Sta3n);
CREATE INDEX IX_PatientSID ON BCMA.BCMAAdditive (PatientSID);
CREATE INDEX IX_InpatientSID ON BCMA.BCMAAdditive (InpatientSID);
GO
