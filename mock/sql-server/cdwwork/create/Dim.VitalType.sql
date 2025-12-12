-- Create table: Dim.VitalType
-- Purpose: Normalizes vital type strings (e.g., "BLOOD PRESSURE" vs "BP")
-- VistA alignment: File #120.51 (GMRV VITAL TYPE)

USE CDWWork;
GO

-- Create Vital schema if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Vital')
BEGIN
    EXEC('CREATE SCHEMA Vital');
    PRINT 'Schema Vital created successfully';
END
GO

CREATE TABLE Dim.VitalType (
    VitalTypeSID        INT IDENTITY(1,1) PRIMARY KEY,
    VitalTypeIEN        VARCHAR(50),                    -- VistA File 120.51 IEN
    VitalType           VARCHAR(100) NOT NULL,          -- e.g., "BLOOD PRESSURE"
    Abbreviation        VARCHAR(10) NOT NULL,           -- e.g., "BP"
    UnitOfMeasure       VARCHAR(20),                    -- e.g., "mmHg", "F", "lb"
    Category            VARCHAR(30),                    -- e.g., "VITAL SIGN", "MEASUREMENT"
    IsActive            BIT DEFAULT 1,
    Sta3n               SMALLINT,                       -- If locally defined

    CONSTRAINT UQ_VitalType_Abbr UNIQUE (Abbreviation)
);
GO

PRINT 'Table Dim.VitalType created successfully';
GO
