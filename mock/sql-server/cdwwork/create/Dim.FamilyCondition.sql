-- Dim.FamilyCondition - family-history condition dimension
-- Purpose: Standardized condition catalog for family-history entries

USE CDWWork;
GO

IF OBJECT_ID('Dim.FamilyCondition', 'U') IS NOT NULL
    DROP TABLE Dim.FamilyCondition;
GO

PRINT 'Creating table Dim.FamilyCondition...';
GO

CREATE TABLE Dim.FamilyCondition (
    FamilyConditionSID INT PRIMARY KEY IDENTITY(1,1),
    ConditionCode VARCHAR(30) NOT NULL UNIQUE,
    ConditionName VARCHAR(255) NOT NULL,
    SNOMEDCode VARCHAR(20) NULL,
    ICD10Code VARCHAR(10) NULL,
    ConditionCategory VARCHAR(80) NOT NULL,   -- Cancer, Cardio, Metabolic, Neuro, Behavioral, Other
    HereditaryRiskFlag CHAR(1) NOT NULL DEFAULT 'N',
    IsActive CHAR(1) NOT NULL DEFAULT 'Y',
    CreatedDateTime DATETIME NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_FamilyCondition_Code
    ON Dim.FamilyCondition(ConditionCode);
GO

CREATE INDEX IX_FamilyCondition_Category
    ON Dim.FamilyCondition(ConditionCategory, HereditaryRiskFlag);
GO

PRINT 'Table Dim.FamilyCondition created successfully.';
GO
