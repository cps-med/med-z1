---------------------------------------------------------------
-- Create: BCMA.BCMASolution.sql
---------------------------------------------------------------
-- Solutions for IV medications in BCMA
-- Contains information about IV solution bags/containers
-- (e.g., Normal Saline 0.9%, Dextrose 5%, Lactated Ringers)
-- Related to BCMA.BCMAMedicationLog
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create BCMASolution table in the BCMA schema
CREATE TABLE BCMA.BCMASolution
(
  BCMASolutionSID                     BIGINT         NOT NULL,
  BCMASolutionIEN                     VARCHAR(50)    NOT NULL,
  BCMAMedicationLogSID                BIGINT         NOT NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  InpatientSID                        BIGINT         NULL,
  InpatientIEN                        VARCHAR(50)    NULL,
  SolutionName                        VARCHAR(120)   NULL,
  SolutionVolume                      NUMERIC(12,4)  NULL,
  SolutionUnit                        VARCHAR(50)    NULL,
  SolutionStrength                    VARCHAR(50)    NULL,
  InfusionRate                        VARCHAR(50)    NULL,
  InfusionRateUnit                    VARCHAR(50)    NULL,
  FlowRate                            NUMERIC(12,4)  NULL,
  FlowRateUnit                        VARCHAR(50)    NULL,
  InfusionDuration                    INT            NULL,
  InfusionDurationUnit                VARCHAR(30)    NULL,
  LocalDrugSID                        BIGINT         NULL,
  LocalDrugIEN                        VARCHAR(50)    NULL,
  NationalDrugSID                     BIGINT         NULL,
  SolutionType                        VARCHAR(50)    NULL,
  IVType                              VARCHAR(30)    NULL,
  OrderNumber                         VARCHAR(50)    NULL,
  SolutionSequence                    INT            NULL
);
GO

-- create indexes for the BCMA.BCMASolution table
CREATE INDEX IX_BCMASolutionSID ON BCMA.BCMASolution (BCMASolutionSID);
CREATE INDEX IX_BCMASolutionIEN ON BCMA.BCMASolution (BCMASolutionIEN);
CREATE INDEX IX_BCMAMedicationLogSID ON BCMA.BCMASolution (BCMAMedicationLogSID);
CREATE INDEX IX_Sta3n ON BCMA.BCMASolution (Sta3n);
CREATE INDEX IX_PatientSID ON BCMA.BCMASolution (PatientSID);
CREATE INDEX IX_InpatientSID ON BCMA.BCMASolution (InpatientSID);
GO
