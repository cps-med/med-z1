---------------------------------------------------------------
-- Create: BCMA.BCMADispensedDrug.sql
---------------------------------------------------------------
-- Dispensed drug details for BCMA medication administration
-- Contains information about drugs dispensed from pharmacy
-- for inpatient administration
-- Related to BCMA.BCMAMedicationLog as child table
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create BCMADispensedDrug table in the BCMA schema
CREATE TABLE BCMA.BCMADispensedDrug
(
  BCMADispensedDrugSID                BIGINT         NOT NULL,
  BCMADispensedDrugIEN                VARCHAR(50)    NOT NULL,
  BCMAMedicationLogSID                BIGINT         NOT NULL,
  Sta3n                               SMALLINT       NOT NULL,
  PatientSID                          INT            NOT NULL,
  PatientIEN                          VARCHAR(50)    NULL,
  InpatientSID                        BIGINT         NULL,
  InpatientIEN                        VARCHAR(50)    NULL,
  LocalDrugSID                        BIGINT         NULL,
  LocalDrugIEN                        VARCHAR(50)    NULL,
  NationalDrugSID                     BIGINT         NULL,
  DrugNameWithoutDose                 VARCHAR(120)   NULL,
  DrugNameWithDose                    VARCHAR(150)   NULL,
  Dosage                              VARCHAR(100)   NULL,
  DosageUnit                          VARCHAR(50)    NULL,
  Strength                            VARCHAR(50)    NULL,
  UnitOfMeasure                       VARCHAR(50)    NULL,
  Quantity                            NUMERIC(12,4)  NULL,
  QuantityUnit                        VARCHAR(50)    NULL,
  DispensedDateTime                   DATETIME       NULL,
  DispensedVistaErrorDate             VARCHAR(50)    NULL,
  DispensedDateTimeTransformSID       BIGINT         NULL,
  PharmacySID                         INT            NULL,
  PharmacyIEN                         VARCHAR(50)    NULL,
  PharmacyName                        VARCHAR(100)   NULL,
  DispensingPharmacistSID             INT            NULL,
  DispensingPharmacistIEN             VARCHAR(50)    NULL,
  OrderNumber                         VARCHAR(50)    NULL,
  UnitDoseMedicationRoute             VARCHAR(50)    NULL,
  UnitDoseMedicationRouteIEN          VARCHAR(50)    NULL,
  UnitDoseScheduleType                VARCHAR(30)    NULL,
  DrugClass                           VARCHAR(100)   NULL,
  DrugClassIEN                        VARCHAR(50)    NULL
);
GO

-- create indexes for the BCMA.BCMADispensedDrug table
CREATE INDEX IX_BCMADispensedDrugSID ON BCMA.BCMADispensedDrug (BCMADispensedDrugSID);
CREATE INDEX IX_BCMADispensedDrugIEN ON BCMA.BCMADispensedDrug (BCMADispensedDrugIEN);
CREATE INDEX IX_BCMAMedicationLogSID ON BCMA.BCMADispensedDrug (BCMAMedicationLogSID);
CREATE INDEX IX_Sta3n ON BCMA.BCMADispensedDrug (Sta3n);
CREATE INDEX IX_PatientSID ON BCMA.BCMADispensedDrug (PatientSID);
CREATE INDEX IX_InpatientSID ON BCMA.BCMADispensedDrug (InpatientSID);
CREATE INDEX IX_DispensedDateTime ON BCMA.BCMADispensedDrug (DispensedDateTime);
GO
