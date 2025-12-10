/*
|---------------------------------------------------------------
| Dim.PatientRecordFlag.sql
|---------------------------------------------------------------
| Create table
|---------------------------------------------------------------
*/

PRINT '================================================';
PRINT '====       Dim.PatientRecordFlag            ====';
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

-- Flag Definitions Dimension Table
-- Combines National (Cat I) and Local (Cat II) flags
-- Source: VistA files #26.15 (PRF NATIONAL FLAG) and #26.11 (PRF LOCAL FLAG)
CREATE TABLE Dim.PatientRecordFlag
(
    PatientRecordFlagSID        INT IDENTITY(1,1) PRIMARY KEY,

    -- Flag identification
    FlagName                    NVARCHAR(100) NOT NULL,
    FlagType                    VARCHAR(30)   NULL,       -- 'CLINICAL', 'BEHAVIORAL', 'RESEARCH', 'ADMINISTRATIVE'
    FlagCategory                CHAR(2)       NOT NULL,   -- 'I' (National) or 'II' (Local)
    FlagSourceType              CHAR(1)       NOT NULL,   -- 'N' (National file 26.15) or 'L' (Local file 26.11)

    -- VistA pointers
    NationalFlagIEN             INT           NULL,       -- IEN in file 26.15 (if National)
    LocalFlagIEN                INT           NULL,       -- IEN in file 26.11 (if Local)

    -- Review rules (from 26.11 or 26.15)
    ReviewFrequencyDays         INT           NULL,       -- How often flag must be reviewed
    ReviewNotificationDays      INT           NULL,       -- Days before review to notify

    -- Status
    IsActive                    BIT           NOT NULL DEFAULT 1,
    InactivationDate            DATE          NULL,

    -- Audit
    CreatedDateTimeUTC          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedDateTimeUTC          DATETIME2     NULL
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

-- Ensure QUOTED_IDENTIFIER is ON for index creation
SET QUOTED_IDENTIFIER ON;
GO

CREATE INDEX IX_FlagName ON Dim.PatientRecordFlag (FlagName);
CREATE INDEX IX_FlagCategory ON Dim.PatientRecordFlag (FlagCategory, IsActive);
GO

PRINT '';
PRINT '==== Done ====';
GO
