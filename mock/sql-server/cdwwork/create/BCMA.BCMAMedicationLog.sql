---------------------------------------------------------------
-- Create: BCMA.BCMAMedicationLog.sql
---------------------------------------------------------------
-- Main medication administration log table for inpatient BCMA
-- Tracks medication administration events including:
-- - Scheduled and actual administration times
-- - Administration actions (Given, Held, Refused, etc.)
-- - Variances and deviations from ordered medication schedule
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create BCMAMedicationLog table in the BCMA schema
CREATE TABLE BCMA.BCMAMedicationLog
(
  BCMAMedicationLogSID                BIGINT         NOT NULL,
  BCMAMedicationLogIEN                VARCHAR(50)    NOT NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  InpatientSID                        BIGINT         NULL,
  InpatientIEN                        VARCHAR(50)    NULL,
  ActionType                          VARCHAR(30)    NULL,
  ActionStatus                        VARCHAR(30)    NULL,
  ActionDateTime                      DATETIME       NULL,
  ActionVistaErrorDate                VARCHAR(50)    NULL,
  ActionDateTimeTransformSID          BIGINT         NULL,
  ScheduledDateTime                   DATETIME       NULL,
  ScheduledVistaErrorDate             VARCHAR(50)    NULL,
  ScheduledDateTimeTransformSID       BIGINT         NULL,
  OrderedDateTime                     DATETIME       NULL,
  OrderedVistaErrorDate               VARCHAR(50)    NULL,
  OrderedDateTimeTransformSID         BIGINT         NULL,
  AdministeredByStaffSID              INT            NULL,
  AdministeredByStaffIEN              VARCHAR(50)    NULL,
  OrderingProviderSID                 INT            NULL,
  OrderingProviderIEN                 VARCHAR(50)    NULL,
  LocalDrugSID                        BIGINT         NULL,
  LocalDrugIEN                        VARCHAR(50)    NULL,
  NationalDrugSID                     BIGINT         NULL,
  DrugNameWithoutDose                 VARCHAR(120)   NULL,
  DrugNameWithDose                    VARCHAR(150)   NULL,
  OrderNumber                         VARCHAR(50)    NULL,
  DosageOrdered                       VARCHAR(100)   NULL,
  DosageGiven                         VARCHAR(100)   NULL,
  Route                               VARCHAR(50)    NULL,
  RouteIEN                            VARCHAR(50)    NULL,
  UnitOfAdministration                VARCHAR(50)    NULL,
  ScheduleType                        VARCHAR(30)    NULL,
  Schedule                            VARCHAR(50)    NULL,
  AdministrationUnit                  VARCHAR(50)    NULL,
  WardLocationSID                     INT            NULL,
  WardLocationIEN                     VARCHAR(50)    NULL,
  WardName                            VARCHAR(100)   NULL,
  VarianceFlag                        CHAR(1)        NULL,
  VarianceType                        VARCHAR(50)    NULL,
  VarianceReason                      VARCHAR(100)   NULL,
  VarianceComment                     VARCHAR(500)   NULL,
  IVFlag                              CHAR(1)        NULL,
  IVType                              VARCHAR(30)    NULL,
  InfusionRate                        VARCHAR(50)    NULL,
  TransactionDateTime                 DATETIME       NULL,
  TransactionVistaErrorDate           VARCHAR(50)    NULL,
  TransactionDateTimeTransformSID     BIGINT         NULL
);
GO

-- create indexes for the BCMA.BCMAMedicationLog table
CREATE INDEX IX_BCMAMedicationLogSID ON BCMA.BCMAMedicationLog (BCMAMedicationLogSID);
CREATE INDEX IX_BCMAMedicationLogIEN ON BCMA.BCMAMedicationLog (BCMAMedicationLogIEN);
CREATE INDEX IX_Sta3n ON BCMA.BCMAMedicationLog (Sta3n);
CREATE INDEX IX_PatientSID ON BCMA.BCMAMedicationLog (PatientSID);
CREATE INDEX IX_InpatientSID ON BCMA.BCMAMedicationLog (InpatientSID);
CREATE INDEX IX_ActionDateTime ON BCMA.BCMAMedicationLog (ActionDateTime);
CREATE INDEX IX_ActionType ON BCMA.BCMAMedicationLog (ActionType);
CREATE INDEX IX_AdministeredByStaffSID ON BCMA.BCMAMedicationLog (AdministeredByStaffSID);
CREATE INDEX IX_OrderingProviderSID ON BCMA.BCMAMedicationLog (OrderingProviderSID);
GO
