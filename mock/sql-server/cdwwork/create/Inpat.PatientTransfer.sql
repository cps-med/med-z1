---------------------------------------------------------------
-- Create: Inpat_PatientTransfer.sql
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create PatientTransfer table in the Inpat schema
CREATE TABLE Inpat.PatientTransfer
(
  PatientTransferSID                    BIGINT        NOT NULL,
  PatientMovementIEN                    VARCHAR(50)   NOT NULL,
  Sta3n                                 SMALLINT      NOT NULL,
  InpatientSID                          BIGINT        NULL,
  OrdinalNumber                         SMALLINT      NULL,
  PatientSID                            INT           NULL,
  PatientTransferDateTime               DATETIME      NULL,
  PatientTransferVistaErrorDate         VARCHAR(50)   NULL,
  PatientTransferDateTimeTransformSID   BIGINT        NULL,
  PatientTransferDateSID                INT           NULL,
  MASMovementTypeSID                    INT           NULL,
  FacilityMovementTypeSID               INT           NULL,
  TransferInstitutionSID                INT           NULL,
  GainingWardLocationSID                INT           NULL,
  RoomBedSID                            INT           NULL,
  PrimaryPhysicianStaffSID              INT           NULL,
  ASIHInpatientSID                      BIGINT        NULL,
  AttendingPhysicianStaffSID            INT           NULL,
  ASIHSequence                          SMALLINT      NULL,
  EnteredByStaffSID                     INT           NULL,
  EnteredOnDateTime                     DATETIME      NULL,
  LastEditedByStaffSID                  INT           NULL,
  LastEditedOnDateTime                  DATETIME      NULL,
  MPCRChangeFlag                        CHAR(1)       NULL,
  AdmitDateTime                         DATETIME      NULL,
  AdmitVistaErrorDate                   VARCHAR(50)   NULL,
  AdmitDateTimeTransformSID             BIGINT        NULL,
  DischargeDateTime                     DATETIME      NULL,
  DischargeVistaErrorDate               VARCHAR(50)   NULL,
  DischargeDateTimeTransformSID         BIGINT        NULL,
  LosingSpecialtySID                    INT           NULL,
  LosingWardLocationSID                 INT           NULL,
  LosingWardCDR                         SMALLINT      NULL,
  LeaveDays                             SMALLINT      NULL,
  PassDays                              SMALLINT      NULL,
  DischargeMovementFlag                 CHAR(1)       NULL,
  TransmitFlag                          CHAR(1)       NULL
);
GO

-- create indexes for the Inpat.PatientTransfer table
CREATE INDEX IX_PatientTransferSID ON Inpat.PatientTransfer (PatientTransferSID);
CREATE INDEX IX_Sta3n ON Inpat.PatientTransfer (Sta3n);
CREATE INDEX IX_InpatientSID ON Inpat.PatientTransfer (InpatientSID);
GO
