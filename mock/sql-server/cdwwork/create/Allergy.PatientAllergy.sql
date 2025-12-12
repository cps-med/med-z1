-- =============================================
-- Create Schema: Allergy
-- Create Table: Allergy.PatientAllergy
-- Description: Patient allergy fact table
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Create Allergy schema if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Allergy')
BEGIN
    EXEC('CREATE SCHEMA Allergy');
    PRINT 'Schema Allergy created successfully';
END
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Allergy.PatientAllergy', 'U') IS NOT NULL
    DROP TABLE Allergy.PatientAllergy;
GO

-- Create PatientAllergy fact table
CREATE TABLE Allergy.PatientAllergy (
    PatientAllergySID       BIGINT IDENTITY(1,1) PRIMARY KEY,
    PatientSID              BIGINT NOT NULL,
    AllergenSID             INT NOT NULL,                   -- FK to Dim.Allergen (standardized)
    AllergySeveritySID      INT NULL,                       -- FK to Dim.AllergySeverity
    LocalAllergenName       VARCHAR(255) NOT NULL,          -- What clinician typed (e.g., "PENICILLIN VK 500MG")

    -- Dates
    OriginationDateTime     DATETIME2(3) NOT NULL,          -- When allergy was recorded
    ObservedDateTime        DATETIME2(3),                   -- When reaction was observed (if applicable)

    -- Staff and location
    OriginatingStaffSID     INT NULL,                       -- Staff who entered
    OriginatingSiteSta3n    SMALLINT,                       -- Facility where entered

    -- Details
    Comment                 NVARCHAR(MAX),                  -- Free-text narrative (may contain PHI)
    HistoricalOrObserved    VARCHAR(20),                    -- "HISTORICAL" or "OBSERVED"

    -- Status
    IsActive                BIT DEFAULT 1,                  -- Soft delete flag
    VerificationStatus      VARCHAR(30),                    -- "VERIFIED", "UNVERIFIED", "ENTERED IN ERROR"

    -- Metadata
    Sta3n                   SMALLINT,
    CreatedDateTimeUTC      DATETIME2(3) DEFAULT GETUTCDATE(),
    UpdatedDateTimeUTC      DATETIME2(3),

    CONSTRAINT FK_Allergy_Allergen FOREIGN KEY (AllergenSID)
        REFERENCES Dim.Allergen(AllergenSID),
    CONSTRAINT FK_Allergy_Severity FOREIGN KEY (AllergySeveritySID)
        REFERENCES Dim.AllergySeverity(AllergySeveritySID)
);
GO

-- Indexing (Critical for performance)
CREATE INDEX IX_PatientAllergy_Patient
    ON Allergy.PatientAllergy(PatientSID, IsActive, OriginationDateTime DESC);
GO

CREATE INDEX IX_PatientAllergy_Allergen
    ON Allergy.PatientAllergy(AllergenSID);
GO

PRINT 'Table Allergy.PatientAllergy created successfully';
GO
