/*
|---------------------------------------------------------------
| SPatient.PatientRecordFlagAssignment.sql
|---------------------------------------------------------------
| Create table
|---------------------------------------------------------------
*/

PRINT '================================================';
PRINT '==== SPatient.PatientRecordFlagAssignment ====';
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
PRINT '==== Create Table ====';
GO

-- Core Assignment Table (Fact)
-- One row per active or historical assignment of a flag to a patient
-- Source: VistA file #26.13 (PRF ASSIGNMENT)
CREATE TABLE SPatient.PatientRecordFlagAssignment
(
    PatientRecordFlagAssignmentSID  BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Core relationships
    PatientSID                      BIGINT        NOT NULL,   -- FK to SPatient.SPatient
    PatientRecordFlagSID            INT           NULL,       -- FK to Dim.PatientRecordFlag (optional)

    -- Denormalized flag info (for queries without joining to Dim)
    FlagName                        NVARCHAR(100) NOT NULL,
    FlagCategory                    CHAR(1)       NOT NULL,   -- 'I' or 'II'
    FlagSourceType                  CHAR(1)       NOT NULL,   -- 'N' or 'L'
    NationalFlagIEN                 INT           NULL,
    LocalFlagIEN                    INT           NULL,

    -- Assignment state
    IsActive                        BIT           NOT NULL,
    AssignmentStatus                VARCHAR(20)   NOT NULL,   -- 'ACTIVE', 'INACTIVE', 'ENTERED IN ERROR'
    AssignmentDateTime              DATETIME2     NOT NULL,   -- When flag was initially assigned
    InactivationDateTime            DATETIME2     NULL,       -- When flag was inactivated (if applicable)

    -- Ownership and facility tracking
    OwnerSiteSta3n                  VARCHAR(10)   NULL,       -- Owning facility (3-digit station number)
    OriginatingSiteSta3n            VARCHAR(10)   NULL,       -- Site that created the flag
    LastUpdateSiteSta3n             VARCHAR(10)   NULL,       -- Site of last change

    -- Review metadata
    ReviewFrequencyDays             INT           NULL,       -- From flag definition
    ReviewNotificationDays          INT           NULL,       -- From flag definition
    LastReviewDateTime              DATETIME2     NULL,       -- Last time flag was reviewed
    NextReviewDateTime              DATETIME2     NULL,       -- When flag must be reviewed next

    -- Audit trail
    CreatedDateTimeUTC              DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedDateTimeUTC              DATETIME2     NULL
);
GO

/*
|----------------------------------------------------------------------
| Create Indexes
| ---------------------------------------------------------------------
*/

PRINT '';
PRINT '==== Create Indexes ====';
GO

-- Critical indexes for patient-centric queries
CREATE INDEX IX_PRFAssign_Patient
    ON SPatient.PatientRecordFlagAssignment (PatientSID, IsActive, FlagCategory);

CREATE INDEX IX_PRFAssign_Review
    ON SPatient.PatientRecordFlagAssignment (NextReviewDateTime, IsActive)
    WHERE NextReviewDateTime IS NOT NULL;

CREATE INDEX IX_PRFAssign_Site
    ON SPatient.PatientRecordFlagAssignment (OwnerSiteSta3n, IsActive);
GO

PRINT '';
PRINT '==== Done ====';
GO
