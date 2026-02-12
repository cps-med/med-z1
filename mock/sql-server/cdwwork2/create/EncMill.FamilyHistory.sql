-- EncMill.FamilyHistory - Cerner-style family history fact table
-- Purpose: Encounter-centric family-history entries for CDWWork2

USE CDWWork2;
GO

IF OBJECT_ID('EncMill.FamilyHistory', 'U') IS NOT NULL
    DROP TABLE EncMill.FamilyHistory;
GO

PRINT 'Creating table EncMill.FamilyHistory...';
GO

CREATE TABLE EncMill.FamilyHistory (
    FamilyHistorySID BIGINT PRIMARY KEY IDENTITY(4001,1),
    EncounterSID BIGINT NOT NULL,               -- FK to EncMill.Encounter
    PersonSID BIGINT NOT NULL,                  -- FK to VeteranMill.SPerson
    PatientICN VARCHAR(50) NOT NULL,            -- Denormalized identity
    Sta3n VARCHAR(10) NOT NULL,                 -- Site/facility

    RelationshipCodeSID BIGINT NOT NULL,        -- FK to NDimMill.CodeValue (FAMILY_RELATIONSHIP)
    ConditionCodeSID BIGINT NOT NULL,           -- FK to NDimMill.CodeValue (FAMILY_HISTORY_CONDITION)
    StatusCodeSID BIGINT NOT NULL,              -- FK to NDimMill.CodeValue (FAMILY_HISTORY_STATUS)

    FamilyMemberName VARCHAR(150) NULL,
    FamilyMemberAge INT NULL,
    OnsetAgeYears INT NULL,
    NotedDateTime DATETIME NOT NULL,
    DocumentedBy VARCHAR(200) NULL,
    CommentText VARCHAR(1000) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDateTime DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_EncFamilyHistory_Encounter
        FOREIGN KEY (EncounterSID) REFERENCES EncMill.Encounter(EncounterSID),
    CONSTRAINT FK_EncFamilyHistory_Person
        FOREIGN KEY (PersonSID) REFERENCES VeteranMill.SPerson(PersonSID),
    CONSTRAINT FK_EncFamilyHistory_RelationshipCode
        FOREIGN KEY (RelationshipCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID),
    CONSTRAINT FK_EncFamilyHistory_ConditionCode
        FOREIGN KEY (ConditionCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID),
    CONSTRAINT FK_EncFamilyHistory_StatusCode
        FOREIGN KEY (StatusCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID)
);
GO

CREATE INDEX IX_EncFamilyHistory_Person
    ON EncMill.FamilyHistory(PersonSID, NotedDateTime DESC);
GO

CREATE INDEX IX_EncFamilyHistory_ICN
    ON EncMill.FamilyHistory(PatientICN, NotedDateTime DESC);
GO

CREATE INDEX IX_EncFamilyHistory_Encounter
    ON EncMill.FamilyHistory(EncounterSID);
GO

CREATE INDEX IX_EncFamilyHistory_CodeSets
    ON EncMill.FamilyHistory(RelationshipCodeSID, ConditionCodeSID, StatusCodeSID);
GO

PRINT 'Table EncMill.FamilyHistory created successfully.';
GO
