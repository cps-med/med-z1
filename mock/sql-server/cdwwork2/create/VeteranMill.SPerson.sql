-----------------------------------------------------------------------
-- VeteranMill.SPerson.sql
-- Patient/Veteran demographics for Oracle Health (Cerner)
-- Corresponds to CDWWork's SPatient.SPatient
-----------------------------------------------------------------------
-- Design Notes:
-- - Cerner uses "Person" terminology instead of "Patient"
-- - PersonSID is surrogate key (may differ from CDWWork PatientSID)
-- - PatientICN is the shared identity key for cross-database joins
-- - Minimal fields for Phase 1 demo (2 patients: Adam Dooree, Alexander Aminor)
-----------------------------------------------------------------------

USE CDWWork2;
GO

PRINT 'Creating VeteranMill.SPerson table...';
GO

CREATE TABLE VeteranMill.SPerson (
    PersonSID BIGINT PRIMARY KEY IDENTITY(1,1),    -- Cerner-specific surrogate key
    PatientICN VARCHAR(50) NOT NULL,                -- Shared ICN (key for cross-DB identity)
    LastName VARCHAR(100) NOT NULL,
    FirstName VARCHAR(100) NOT NULL,
    MiddleName VARCHAR(100) NULL,
    BirthDate DATE NOT NULL,
    Gender CHAR(1) NOT NULL,                        -- M, F
    SSN VARCHAR(11) NULL,                           -- Format: XXX-XX-XXXX
    HomePhone VARCHAR(20) NULL,
    Email VARCHAR(100) NULL,

    -- Address fields (minimal for Phase 1)
    StreetAddress VARCHAR(200) NULL,
    City VARCHAR(100) NULL,
    State CHAR(2) NULL,
    ZipCode VARCHAR(10) NULL,

    -- Administrative fields
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    LastUpdatedDate DATETIME NOT NULL DEFAULT GETDATE(),

    -- Unique constraint on ICN
    CONSTRAINT UQ_SPerson_ICN UNIQUE (PatientICN)
);
GO

-- Index for ICN lookups (critical for cross-database joins)
CREATE INDEX IX_SPerson_ICN
    ON VeteranMill.SPerson (PatientICN);
GO

-- Index for name searches
CREATE INDEX IX_SPerson_Name
    ON VeteranMill.SPerson (LastName, FirstName);
GO

PRINT '  - SPerson table created with indexes';
PRINT '  - Ready for demo patients: Adam Dooree (ICN100001), Alexander Aminor (ICN100010)';
GO
