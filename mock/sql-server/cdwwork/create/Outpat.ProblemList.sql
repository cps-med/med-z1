-- Outpat.ProblemList - VistA Problem List (File #9000011)
-- Purpose: Patient longitudinal problem list with dual coding (SNOMED CT + ICD-10)
-- Source: VistA Problem List (GMD namespace)
-- Scope: Chronic conditions and active problems managed in VistA outpatient environment

USE CDWWork;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Outpat.ProblemList', 'U') IS NOT NULL
    DROP TABLE Outpat.ProblemList;
GO

PRINT 'Creating table Outpat.ProblemList...';
GO

CREATE TABLE Outpat.ProblemList (
    ProblemSID BIGINT PRIMARY KEY IDENTITY(1001,1),
    PatientSID INT NOT NULL,
    PatientICN VARCHAR(50),
    Sta3n INT NOT NULL,

    -- Problem identification
    ProblemNumber VARCHAR(20),
    SNOMEDCode VARCHAR(20),
    SNOMEDDescription VARCHAR(500),
    ICD10Code VARCHAR(10),
    ICD10Description VARCHAR(500),

    -- Problem metadata
    ProblemStatus VARCHAR(20) NOT NULL,  -- ACTIVE, INACTIVE, RESOLVED
    OnsetDate DATE,
    RecordedDate DATE NOT NULL,
    LastModifiedDate DATE,
    ResolvedDate DATE,

    -- Clinical context
    ProviderSID INT,
    ProviderName VARCHAR(200),
    Clinic VARCHAR(200),
    ProblemComment VARCHAR(1000),

    -- Annotations
    IsServiceConnected CHAR(1) DEFAULT 'N',
    IsAcuteCondition CHAR(1) DEFAULT 'N',
    IsChronicCondition CHAR(1) DEFAULT 'N',

    -- Audit fields
    EnteredBy VARCHAR(200),
    EnteredDateTime DATETIME,
    ModifiedBy VARCHAR(200),
    ModifiedDateTime DATETIME
);
GO

-- Create indexes for common queries
CREATE INDEX IX_ProblemList_Patient ON Outpat.ProblemList(PatientSID, ProblemStatus);
CREATE INDEX IX_ProblemList_ICN ON Outpat.ProblemList(PatientICN);
CREATE INDEX IX_ProblemList_ICD10 ON Outpat.ProblemList(ICD10Code);
CREATE INDEX IX_ProblemList_SNOMED ON Outpat.ProblemList(SNOMEDCode);
CREATE INDEX IX_ProblemList_Status ON Outpat.ProblemList(ProblemStatus);
CREATE INDEX IX_ProblemList_Onset ON Outpat.ProblemList(OnsetDate);
CREATE INDEX IX_ProblemList_Chronic ON Outpat.ProblemList(IsChronicCondition) WHERE IsChronicCondition = 'Y';
GO

PRINT 'Table Outpat.ProblemList created successfully.';
GO
