/*
|---------------------------------------------------------------
| SPatient.SPatient.sql
|---------------------------------------------------------------
| Create table
|---------------------------------------------------------------
*/

PRINT '================================================';
PRINT '====           SPatient.SPatient            ====';
PRINT '================================================';
GO

-- set the active database
USE CDWWork;
GO

/*
|----------------------------------------------------------------------
| Create Table
| ---------------------------------------------------------------------
*/

PRINT '';
PRINT '==== Create Table ===='
GO

-- create SPatient table in the SPatient schema
CREATE TABLE SPatient.SPatient
(
  PatientSID                              INT           NOT NULL,
  PatientIEN                              VARCHAR(50)   NOT NULL,
  Sta3n                                   SMALLINT      NOT NULL,
  PatientName                             VARCHAR(30)   NULL,
  PatientLastName                         VARCHAR(30)   NULL,
  PatientFirstName                        VARCHAR(30)   NULL,
  TestPatientFlag                         CHAR(1)       NULL,
  CDWPossibleTestPatientFlag              CHAR(1)       NULL,
  VeteranFlag                             CHAR(1)       NULL,
  PatientType                             VARCHAR(30)   NULL,
  PatientTypeSID                          INT           NULL,
  PatientICN                              VARCHAR(50)   NULL,
  ScrSSN                                  VARCHAR(20)   NULL,
  PatientSSN                              VARCHAR(20)   NULL,
  PseudoSSNReason                         VARCHAR(50)   NULL,
  SSNVerificationStatus                   VARCHAR(50)   NULL,
  GovernmentEmployeeFlag                  CHAR(1)       NULL,
  SensitiveFlag                           CHAR(1)       NULL,
  Age                                     NUMERIC(9)    NULL,
  BirthDateTime                           DATETIME      NULL,
  BirthVistaErrorDate                     VARCHAR(50)   NULL,
  BirthDateTimeTransformSID               BIGINT        NULL,
  DeceasedFlag                            CHAR(1)       NULL,
  DeathDateTime                           DATETIME      NULL,
  DeathVistaErrorDate                     VARCHAR(50)   NULL,
  DeathDateTimeTransformSID               BIGINT        NULL,
  DeathEnteredByStaffSID                  INT           NULL,
  DeathNotificationSource                 VARCHAR(30)   NULL,
  DeathDocumentationType                  VARCHAR(30)   NULL,
  DeathModifiedDateTime                   DATETIME      NULL,
  DeathModifiedVistaErrorDate             VARCHAR(30)   NULL,
  DeathModifiedDateTimeTransformSID       BIGINT        NULL,
  DeathLastUpdatedByStaffSID              INT           NULL,
  Gender                                  CHAR(1)       NULL,
  SelfIdentifiedGender                    VARCHAR(20)   NULL,
  Religion                                VARCHAR(20)   NULL,
  ReligionSID                             INT           NULL,
  MaritalStatus                           VARCHAR(25)   NULL,
  MaritalStatusSID                        INT           NULL,
  CollateralSponsorPatientSID             INT           NULL,
  CurrentEnrollmentSID                    BIGINT        NULL,
  MeansTestStatus                         VARCHAR(30)   NULL,
  CurrentMeansTestStatusSID               INT           NULL,
  PeriodOfService                         VARCHAR(30)   NULL,
  PeriodOfServiceSID                      INT           NULL,
  OperationDesertShieldRank               VARCHAR(30)   NULL,
  ODSRankType                             VARCHAR(20)   NULL,
  ODSRecalledCode                         VARCHAR(20)   NULL,
  ODSTreatmentDateTime                    DATETIME      NULL,
  ODSTreatmentVistaErrorDate              VARCHAR(30)   NULL,
  ODSTreatmentDateTimeTransformSID        BIGINT        NULL,
  FederalAgencySID                        INT           NULL,
  FilipinoVeteranCode                     VARCHAR(30)   NULL,
  ServiceConnectedFlag                    CHAR(1)       NULL,
  Eligibility                             VARCHAR(50)   NULL,
  EligibilityVACode                       VARCHAR(30)   NULL,
  EligibilitySID                          INT           NULL,
  EligibilityStatus                       VARCHAR(30)   NULL,
  EligibilityStatusDateTime               DATETIME      NULL,
  EligibilityStatusVistaErrorDate         VARCHAR(50)   NULL,
  EligibilityStatusDateTimeTransformSID   BIGINT        NULL,
  EligibilityVerificationSource           VARCHAR(50)   NULL,
  EligibilityVerificationMethod           VARCHAR(50)   NULL,
  EligibilityInterimDateTime              DATETIME      NULL,
  EligibilityInterimVistaErrorDate        VARCHAR(30)   NULL,
  EligibilityInterimDateTimeTransformSID  BIGINT        NULL,
  EligibilityEnteredStaffSID              INT           NULL,
  IneligibleReason                        VARCHAR(50)   NULL,
  IneligibleVAROReason                    VARCHAR(50)   NULL,
  IneligibleCity                          VARCHAR(30)   NULL,
  IneligibleStateSID                      INT           NULL,
  IneligibleDateTime                      DATETIME      NULL,
  IneligibleVistaErrorDate                VARCHAR(30)   NULL,
  IneligibleDateTimeTransformSID          BIGINT        NULL,
  IneligibleSource                        VARCHAR(30)   NULL,
  PatientMissingSource                    VARCHAR(30)   NULL,
  PatientMissingDateTime                  DATETIME      NULL,
  PatientMissingVistaErrorDate            VARCHAR(30)   NULL,
  PatientMissingDateTimeTransformSID      BIGINT        NULL,
  PatientMissingCity                      VARCHAR(30)   NULL,
  PatientMissingStateSID                  INT           NULL,
  FugitiveFelonFlag                       CHAR(1)       NULL,
  FFFEnteredDateTime                      DATETIME      NULL,
  FFFEnteredVistaErrorDate                VARCHAR(30)   NULL,
  FFFEnteredDateTimeTransformSID          BIGINT        NULL,
  FFFEnteredStaffSID                      INT           NULL,
  FFFRemovedReason                        VARCHAR(30)   NULL,
  FFFRemovedDateTime                      DATETIME      NULL,
  FFFRemovedVistaErrorDate                VARCHAR(30)   NULL,
  FFFRemovedDateTimeTransformSID          BIGINT        NULL,
  FFFRemovedStaffSID                      INT           NULL,
  PatientEnteredByStaffSID                INT           NULL,
  PatientEnteredCode                      VARCHAR(50)   NULL,
  PatientEnteredRemark                    VARCHAR(50)   NULL,
  PatientEnteredDateTime                  DATETIME      NULL,
  PatientEnteredVistaErrorDate            VARCHAR(30)   NULL,
  PatientEnteredDateTimeTransformSID      BIGINT        NULL,
  DuplicateRecordStatus                   VARCHAR(30)   NULL,
  DestinationMergePatientSID              INT           NULL,
  PreferredInstitutionSID                 INT           NULL,
  PreferredInstitutionSource              VARCHAR(30)   NULL,
  EmergencyResponseIndicator              VARCHAR(20)   NULL,
  InsuranceCoverageFlag                   CHAR(1)       NULL,
  MedicaidEligibleFlag                    CHAR(1)       NULL,
  MedicaidNumber                          VARCHAR(30)   NULL,
  MedicaidInquireDateTime                 DATETIME      NULL,
  MedicaidInquireVistaErrorDate           VARCHAR(30)   NULL,
  MedicaidInquireDateTimeTransformSID     BIGINT        NULL,
  VeteranTransportationProgramFlag        CHAR(1)       NULL
);
GO

/*
|----------------------------------------------------------------------
| Create Indicies
| ---------------------------------------------------------------------
*/

PRINT '';
PRINT '==== Create Indicies ===='
GO

-- create indexes for the SPatient.Patient table
CREATE INDEX IX_PatientSID ON SPatient.SPatient (PatientSID);
CREATE INDEX IX_PatientIEN ON SPatient.SPatient (PatientIEN);
CREATE INDEX IX_Sta3n ON SPatient.SPatient (Sta3n);
GO

PRINT '';
PRINT '==== Done ===='
GO
