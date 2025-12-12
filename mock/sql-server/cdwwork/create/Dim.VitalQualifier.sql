-- Create table: Dim.VitalQualifier
-- Purpose: Normalizes qualifiers (position, cuff size, site, method)
-- VistA alignment: File #120.52 (GMRV VITAL QUALIFIER)

USE CDWWork;
GO

CREATE TABLE Dim.VitalQualifier (
    VitalQualifierSID   INT IDENTITY(1,1) PRIMARY KEY,
    VitalQualifier      VARCHAR(100) NOT NULL,          -- e.g., "SITTING", "LEFT ARM"
    QualifierType       VARCHAR(50) NOT NULL,           -- e.g., "POSITION", "SITE", "CUFF SIZE"
    VitalQualifierIEN   VARCHAR(50),                    -- VistA IEN
    Sta3n               SMALLINT,
    IsActive            BIT DEFAULT 1
);
GO

PRINT 'Table Dim.VitalQualifier created successfully';
GO
