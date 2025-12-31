-----------------------------------------------------------------------
-- EncMill.Encounter.sql
-- Encounter data for Oracle Health (Cerner)
-- Cerner is encounter-centric vs VistA patient-centric model
-----------------------------------------------------------------------
-- Design Notes:
-- - Cerner organizes clinical data around encounters
-- - All vitals, allergies, labs, etc. linked to an encounter
-- - Phase 1: Minimal fields for 5-10 encounters per patient at Cerner sites
-- - Sites: 648 (Portland), 663 (Seattle)
-----------------------------------------------------------------------

USE CDWWork2;
GO

PRINT 'Creating EncMill.Encounter table...';
GO

CREATE TABLE EncMill.Encounter (
    EncounterSID BIGINT PRIMARY KEY IDENTITY(1,1),  -- Cerner-specific encounter ID
    PersonSID BIGINT NOT NULL,                       -- FK to VeteranMill.SPerson
    PatientICN VARCHAR(50) NOT NULL,                 -- Denormalized for query performance
    Sta3n VARCHAR(10) NOT NULL,                      -- Site/facility (648, 663)
    FacilityName VARCHAR(200) NULL,                  -- Portland VAMC, Seattle VAMC

    -- Encounter details
    EncounterType VARCHAR(50) NOT NULL,              -- INPATIENT, OUTPATIENT, EMERGENCY
    EncounterDate DATETIME NOT NULL,                 -- Primary encounter date/time
    AdmitDate DATETIME NULL,                         -- For inpatient encounters
    DischargeDate DATETIME NULL,                     -- For inpatient encounters

    -- Location
    LocationName VARCHAR(200) NULL,                  -- Clinic or ward name
    LocationType VARCHAR(50) NULL,                   -- CLINIC, WARD, ED

    -- Provider
    ProviderName VARCHAR(200) NULL,                  -- Attending or primary provider
    ProviderSID BIGINT NULL,                         -- FK to provider table (future)

    -- Administrative
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),

    -- Foreign key constraint
    CONSTRAINT FK_Encounter_Person
        FOREIGN KEY (PersonSID) REFERENCES VeteranMill.SPerson(PersonSID)
);
GO

-- Index for patient encounter lookups
CREATE INDEX IX_Encounter_Person
    ON EncMill.Encounter (PersonSID, EncounterDate DESC);
GO

-- Index for ICN lookups (cross-database queries)
CREATE INDEX IX_Encounter_ICN
    ON EncMill.Encounter (PatientICN, EncounterDate DESC);
GO

-- Index for site-based queries
CREATE INDEX IX_Encounter_Site
    ON EncMill.Encounter (Sta3n, EncounterDate DESC);
GO

PRINT '  - Encounter table created with indexes';
PRINT '  - Phase 1: Will populate 5-10 encounters per demo patient';
PRINT '  - Sites: 648 (Portland), 663 (Seattle)';
GO
