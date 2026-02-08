-- Dim.ICD10 - ICD-10-CM diagnosis codes dimension table
-- Purpose: Reference table for diagnosis code lookups
-- Source: ICD-10-CM (International Classification of Diseases, 10th Revision, Clinical Modification)
-- Scope: 50 common codes covering top diagnostic categories for mock environment

USE CDWWork;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Dim.ICD10', 'U') IS NOT NULL
    DROP TABLE Dim.ICD10;
GO

PRINT 'Creating table Dim.ICD10...';
GO

CREATE TABLE Dim.ICD10 (
    ICD10SID INT PRIMARY KEY IDENTITY(1,1),
    ICD10Code VARCHAR(10) NOT NULL UNIQUE,
    ICD10Description VARCHAR(500) NOT NULL,
    ICD10Category VARCHAR(100) NOT NULL,
    CharlsonCondition VARCHAR(100),
    IsChronicCondition CHAR(1) DEFAULT 'N',
    CreatedDate DATETIME DEFAULT GETDATE()
);
GO

-- Create indexes for common queries
CREATE INDEX IX_ICD10_Code ON Dim.ICD10(ICD10Code);
CREATE INDEX IX_ICD10_Category ON Dim.ICD10(ICD10Category);
CREATE INDEX IX_ICD10_Charlson ON Dim.ICD10(CharlsonCondition) WHERE CharlsonCondition IS NOT NULL;
CREATE INDEX IX_ICD10_Chronic ON Dim.ICD10(IsChronicCondition) WHERE IsChronicCondition = 'Y';
GO

PRINT 'Table Dim.ICD10 created successfully.';
GO
