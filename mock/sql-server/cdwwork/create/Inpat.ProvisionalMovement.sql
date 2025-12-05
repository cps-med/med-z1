------------------------------------------------------------------------------
-- Create: Inpat.ProvisionalMovement.sql
------------------------------------------------------------------------------
-- ProvisionalMovement (VistA File #41.1)
-- A temporary staging file used to hold patient movement data before it
-- becomes official. Stores in-progress, unsaved, or unverified movements
-- such as: Admissions, Transfers, Discharges, ASIH (absent sick in hospital),
-- and Lodger movements.
-------------------------------------------------------------------------------
-- PatientMovement (VistA File #405)
-- Data is provisional until committed to the PatientMovement file, the primary
-- record of official movements. CDW only provides a ProvisionalMovement view,
-- which I believe incorporates PatientMovement, including PatientMovementIEN.
------------------------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create ProvisionalMovement table in the Inpat schema
CREATE TABLE Inpat.ProvisionalMovement
(
  ProvisionalMovementSID                BIGINT        NOT NULL,
  ProvisionalMovementIEN                VARCHAR(50)   NOT NULL,
  Sta3n                                 SMALLINT      NOT NULL,
  InpatientSID                          BIGINT        NULL,
  OrdinalNumber                         SMALLINT      NULL,
  NextOrdinalNumber                     SMALLINT      NULL,
  PatientSID                            INT           NULL,
  PatientMovementDateTime               DATETIME      NULL,
  PatientMovementVistaErrorDate         VARCHAR(50)   NULL,
  PatientMovementDateTimeTransformSID   BIGINT        NULL,
  MASMovementTypeSID                    INT           NULL,
  MASTransactionTypeSID                 INT           NULL,
  FacilityMovementTypeSID               INT           NULL,
  TransferInstitutionSID                INT           NULL,
  WardLocationSID                       INT           NULL,
  RoomBedSID                            INT           NULL,
  PrimaryPhysicianStaffSID              INT           NULL,
  TreatingSpecialtySID                  INT           NULL,
  AdmittingDiagnosis                    VARCHAR(50)   NULL,
  ASIHAdmissionPatientMovementSID       BIGINT        NULL,
  DischargeCheckOutPatientMovementSID   BIGINT        NULL,
  RelatedPhysicalPatientMovementSID     BIGINT        NULL,
  AttendingPhysicianStaffSID            INT           NULL,
  ASIHTransferPatientMovementSID        BIGINT        NULL,
  ASIHSequence                          SMALLINT      NULL,
  ScheduledAdmissionFlag                CHAR(1)       NULL,
  EnteredByStaffSID                     INT           NULL,
  EnteredOnDateTime                     DATETIME      NULL,
  LastEditedByStaffSID                  INT           NULL,
  LastEditedOnDateTime                  DATETIME      NULL,
  NonVAFacilityFlag                     CHAR(1)       NULL,
  Disposition                           VARCHAR(50)   NULL
);
GO

-- create indexes for the Inpat.ProvisionalMovement table
CREATE INDEX IX_ProvisionalMovementSID ON Inpat.ProvisionalMovement (ProvisionalMovementSID);
CREATE INDEX IX_Sta3n ON Inpat.ProvisionalMovement (Sta3n);
CREATE INDEX IX_InpatientSID ON Inpat.ProvisionalMovement (InpatientSID);
GO
