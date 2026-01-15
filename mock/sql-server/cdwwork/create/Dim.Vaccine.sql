-- Create table: Dim.Vaccine
-- Purpose: Enterprise-wide vaccine definitions for immunization tracking
-- VistA alignment: File #9999999.14 (IMMUNIZATION definitions)
-- CDC CVX codes: https://www2a.cdc.gov/vaccines/iis/iisstandards/vaccines.asp
--
-- IMPORTANT NOTES:
-- 1. CVX Code is the ENTERPRISE-WIDE standard (CDC Vaccines Administered code set)
-- 2. VistaIEN values are SITE-SPECIFIC in production (IEN 100 at Site 508 ≠ IEN 100 at Site 630)
-- 3. For MVP: VistaIEN stored as representative/example value
-- 4. Phase 3 Enhancement: Add Dim.VaccineVistaMapping table for multi-site IEN mappings
-- 5. CVX codes are the PRIMARY KEY for vaccine identity across all VistA sites

USE CDWWork;
GO

-- Create Immunization schema if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Immunization')
BEGIN
    EXEC('CREATE SCHEMA Immunization');
    PRINT 'Schema Immunization created successfully';
END
GO

CREATE TABLE Dim.Vaccine (
    VaccineSID          INT IDENTITY(1,1) PRIMARY KEY,
    VaccineName         VARCHAR(255) NOT NULL,          -- Full vaccine name
    VaccineShortName    VARCHAR(100),                   -- Abbreviated name
    CVXCode             VARCHAR(10),                    -- CDC CVX code (ENTERPRISE-WIDE standard, source of truth)
    MVXCode             VARCHAR(10),                    -- Manufacturer code (optional)
    VistaIEN            VARCHAR(50),                    -- VistA File #9999999.14 IEN (SITE-SPECIFIC in production, representative value in MVP)
    IsInactive          CHAR(1) DEFAULT 'N',            -- Y/N inactive flag
    CreatedDateTimeUTC  DATETIME2(3) DEFAULT GETUTCDATE(),

    CONSTRAINT UQ_Vaccine_CVX UNIQUE (CVXCode)          -- CVX is unique enterprise-wide identifier
);
GO

-- Index for CVX code lookups (most common query pattern)
SET QUOTED_IDENTIFIER ON;
GO

CREATE INDEX IX_Vaccine_CVX ON Dim.Vaccine (CVXCode)
    WHERE CVXCode IS NOT NULL;
GO

-- Index for active vaccines
CREATE INDEX IX_Vaccine_Active ON Dim.Vaccine (IsInactive, VaccineName)
    WHERE IsInactive = 'N';
GO

PRINT 'Table Dim.Vaccine created successfully with indexes';
GO
