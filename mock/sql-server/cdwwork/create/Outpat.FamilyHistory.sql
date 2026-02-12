-- Outpat.FamilyHistory - VistA-style family-history fact table
-- Purpose: Patient-centric family-history entries for Family History domain

USE CDWWork;
GO

IF OBJECT_ID('Outpat.FamilyHistory', 'U') IS NOT NULL
    DROP TABLE Outpat.FamilyHistory;
GO

PRINT 'Creating table Outpat.FamilyHistory...';
GO

CREATE TABLE Outpat.FamilyHistory (
    FamilyHistorySID BIGINT PRIMARY KEY IDENTITY(1001,1),
    PatientSID INT NOT NULL,
    PatientICN VARCHAR(50) NOT NULL,
    Sta3n INT NOT NULL,

    FamilyRelationshipSID INT NOT NULL,
    FamilyConditionSID INT NOT NULL,

    FamilyMemberGender CHAR(1) NULL,             -- M/F/U
    OnsetAgeYears INT NULL,                      -- Relative age of onset
    DeceasedFlag CHAR(1) NULL,                   -- Y/N/U
    ClinicalStatus VARCHAR(20) NOT NULL,         -- ACTIVE, RESOLVED, UNKNOWN

    RecordedDateTime DATETIME NOT NULL,
    EnteredDateTime DATETIME NOT NULL,
    ProviderSID INT NULL,
    LocationSID INT NULL,
    CommentText VARCHAR(1000) NULL,
    IsActive CHAR(1) NOT NULL DEFAULT 'Y',

    CreatedDateTime DATETIME NOT NULL DEFAULT GETDATE(),

    -- Note: SPatient.SPatient in this mock environment does not declare
    -- PatientSID as PK/UNIQUE, so we intentionally do not enforce an FK here.
    CONSTRAINT FK_FamilyHistory_Relationship
        FOREIGN KEY (FamilyRelationshipSID) REFERENCES Dim.FamilyRelationship(FamilyRelationshipSID),
    CONSTRAINT FK_FamilyHistory_Condition
        FOREIGN KEY (FamilyConditionSID) REFERENCES Dim.FamilyCondition(FamilyConditionSID)
);
GO

CREATE INDEX IX_FamilyHistory_Patient
    ON Outpat.FamilyHistory(PatientSID, RecordedDateTime DESC);
GO

CREATE INDEX IX_FamilyHistory_ICN
    ON Outpat.FamilyHistory(PatientICN, RecordedDateTime DESC);
GO

CREATE INDEX IX_FamilyHistory_Status
    ON Outpat.FamilyHistory(ClinicalStatus, IsActive);
GO

CREATE INDEX IX_FamilyHistory_RelCondition
    ON Outpat.FamilyHistory(FamilyRelationshipSID, FamilyConditionSID);
GO

PRINT 'Table Outpat.FamilyHistory created successfully.';
GO
