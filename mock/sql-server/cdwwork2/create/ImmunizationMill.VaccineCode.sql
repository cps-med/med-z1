-- Create table: ImmunizationMill.VaccineCode
-- Purpose: Cerner vaccine code dimension (CODE_VALUE table subset)
-- Maps Cerner internal codes to CDC CVX codes
-- Cerner/Oracle Health alignment: CODE_VALUE table, Code Set 100 (Immunizations)
--
-- IMPORTANT NOTES:
-- 1. CodeValue = Cerner internal code (enterprise-wide within Cerner)
-- 2. CVXCode = CDC standard for mapping to VistA data
-- 3. Display names follow Cerner nomenclature (may differ from VistA)
-- 4. Silver ETL harmonizes Cerner + VistA via CVX code joins

USE CDWWork2;
GO

-- Create ImmunizationMill schema if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'ImmunizationMill')
BEGIN
    EXEC('CREATE SCHEMA ImmunizationMill');
    PRINT 'Schema ImmunizationMill created successfully';
END
GO

-- Cerner CODE_VALUE subset for vaccines
CREATE TABLE ImmunizationMill.VaccineCode (
    VaccineCodeSID      BIGINT IDENTITY(1,1) PRIMARY KEY,
    CodeValue           BIGINT NOT NULL,                -- Cerner internal code (enterprise-wide)
    Display             VARCHAR(255) NOT NULL,          -- Display name (Cerner nomenclature)
    Definition          VARCHAR(500),                   -- Code definition/description
    CVXCode             VARCHAR(10),                    -- Mapped to CDC CVX (CRITICAL for harmonization)
    CodeSet             INT DEFAULT 100,                -- Code set identifier (100 = Immunizations)
    IsActive            BIT DEFAULT 1,
    CreatedDateTimeUTC  DATETIME2(3) DEFAULT GETUTCDATE(),

    CONSTRAINT UQ_VaccineCode_CodeValue UNIQUE (CodeValue)
);
GO

-- Index for CVX code lookups (used in Silver ETL joins)
SET QUOTED_IDENTIFIER ON;
GO

CREATE INDEX IX_VaccineCode_CVX ON ImmunizationMill.VaccineCode (CVXCode)
    WHERE CVXCode IS NOT NULL;
GO

PRINT 'Table ImmunizationMill.VaccineCode created successfully with indexes';
GO
