-- Dim.CharlsonMapping - Charlson Comorbidity Index (CCI) reference table
-- Purpose: Map ICD-10 codes to Charlson conditions with weighted scores
-- Source: Charlson et al. (1987) + Quan et al. (2005) ICD-10 adaptation
-- Usage: Calculate patient comorbidity burden for mortality prediction

USE CDWWork;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Dim.CharlsonMapping', 'U') IS NOT NULL
    DROP TABLE Dim.CharlsonMapping;
GO

PRINT 'Creating table Dim.CharlsonMapping...';
GO

CREATE TABLE Dim.CharlsonMapping (
    CharlsonMappingSID INT PRIMARY KEY IDENTITY(1,1),
    CharlsonCondition VARCHAR(100) NOT NULL,
    CharlsonWeight INT NOT NULL,
    ICD10Code VARCHAR(10) NOT NULL,
    ICD10Description VARCHAR(500),
    CreatedDate DATETIME DEFAULT GETDATE()
);
GO

-- Create indexes for common queries
CREATE INDEX IX_Charlson_ICD10 ON Dim.CharlsonMapping(ICD10Code);
CREATE INDEX IX_Charlson_Condition ON Dim.CharlsonMapping(CharlsonCondition);
CREATE INDEX IX_Charlson_Weight ON Dim.CharlsonMapping(CharlsonWeight);
GO

PRINT 'Table Dim.CharlsonMapping created successfully.';
GO
