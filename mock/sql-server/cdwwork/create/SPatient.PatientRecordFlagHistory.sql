/*
|---------------------------------------------------------------
| SPatient.PatientRecordFlagHistory.sql
|---------------------------------------------------------------
| Create table
|---------------------------------------------------------------
*/

PRINT '================================================';
PRINT '====  SPatient.PatientRecordFlagHistory     ====';
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

-- History/Audit Table
-- One row per event (new assignment, review, inactivation, etc.)
-- Contains SENSITIVE narrative text
-- Source: VistA file #26.14 (PRF ASSIGNMENT HISTORY)
CREATE TABLE SPatient.PatientRecordFlagHistory
(
    PatientRecordFlagHistorySID     BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Relationships
    PatientRecordFlagAssignmentSID  BIGINT        NOT NULL,   -- FK to Assignment table
    PatientSID                      BIGINT        NOT NULL,   -- Denormalized for easier querying

    -- Event details (direct mapping from VistA file 26.14)
    HistoryDateTime                 DATETIME2     NOT NULL,   -- .02 DATE/TIME
    ActionCode                      TINYINT       NOT NULL,   -- .03 ACTION (1-5)
    ActionName                      VARCHAR(50)   NOT NULL,   -- Decoded action name

    -- User tracking (VistA NEW PERSON file #200 IENs)
    EnteredByDUZ                    INT           NOT NULL,   -- .04 ENTERED BY
    EnteredByName                   VARCHAR(100)  NULL,       -- Resolved name for display
    ApprovedByDUZ                   INT           NOT NULL,   -- .05 APPROVED BY
    ApprovedByName                  VARCHAR(100)  NULL,       -- Resolved name for display

    -- Clinical documentation linkage
    TiuDocumentIEN                  INT           NULL,       -- .06 TIU PN LINK (Progress Note #8925)

    -- SENSITIVE: Narrative text explaining the action
    HistoryComments                 NVARCHAR(MAX) NULL,       -- 1;0 HISTORY COMMENTS (word-processing field)

    -- Facility context
    EventSiteSta3n                  VARCHAR(10)   NULL,       -- Site where this event occurred

    -- Audit
    CreatedDateTimeUTC              DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
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

-- Indexes for timeline queries
CREATE INDEX IX_PRFHist_Assignment
    ON SPatient.PatientRecordFlagHistory (PatientRecordFlagAssignmentSID, HistoryDateTime);

CREATE INDEX IX_PRFHist_Patient
    ON SPatient.PatientRecordFlagHistory (PatientSID, HistoryDateTime);

CREATE INDEX IX_PRFHist_Action
    ON SPatient.PatientRecordFlagHistory (ActionCode, HistoryDateTime);
GO

PRINT '';
PRINT '==== Done ====';
GO
