-- =============================================
-- Create Table: Dim.Allergen
-- Description: Allergen dimension table (standardized allergen names)
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Dim.Allergen', 'U') IS NOT NULL
    DROP TABLE Dim.Allergen;
GO

-- Create Allergen dimension table
CREATE TABLE Dim.Allergen (
    AllergenSID         INT IDENTITY(1,1) PRIMARY KEY,
    AllergenName        VARCHAR(100) NOT NULL,          -- Standardized name (e.g., "PENICILLIN")
    AllergenType        VARCHAR(50) NOT NULL,           -- "DRUG", "FOOD", "ENVIRONMENTAL"
    VAAllergenFileIEN   VARCHAR(50),                    -- Link to VistA file 120.82
    Sta3n               SMALLINT,                       -- If locally defined
    IsActive            BIT DEFAULT 1,

    CONSTRAINT UQ_Allergen_Name UNIQUE (AllergenName, AllergenType)
);
GO

PRINT 'Table Dim.Allergen created successfully';
GO
