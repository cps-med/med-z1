-----------------------------------------------------------------------
-- VitalMill.VitalResult.sql
-- Vital signs results for Oracle Health (Cerner)
-- Corresponds to CDWWork's Vital.VitalSign
-----------------------------------------------------------------------
-- Design Notes:
-- - Links to NDimMill.CodeValue for vital types (BP, pulse, temp, weight)
-- - Links to NDimMill.CodeValue for units (mmHg, bpm, °F, lbs)
-- - Encounter-linked (Cerner pattern vs VistA patient-linked)
-- - Phase 1: Blood Pressure, Pulse, Temperature, Weight for 2 demo patients
-----------------------------------------------------------------------

USE CDWWork2;
GO

PRINT 'Creating VitalMill.VitalResult table...';
GO

CREATE TABLE VitalMill.VitalResult (
    VitalResultSID BIGINT PRIMARY KEY IDENTITY(1,1),  -- Cerner-specific vital result ID
    EncounterSID BIGINT NOT NULL,                      -- FK to EncMill.Encounter
    PersonSID BIGINT NOT NULL,                         -- FK to VeteranMill.SPerson
    PatientICN VARCHAR(50) NOT NULL,                   -- Denormalized for performance

    -- Vital type (FK to CodeValue where CodeSet='VITAL_TYPE')
    VitalTypeCodeSID BIGINT NOT NULL,                  -- FK to NDimMill.CodeValue
    VitalTypeName VARCHAR(200) NULL,                   -- Denormalized: 'Blood Pressure', 'Pulse', etc.

    -- Result values
    ResultValue VARCHAR(200) NOT NULL,                 -- Text representation (e.g., '120/80')
    NumericValue DECIMAL(10,2) NULL,                   -- Numeric value for single-value vitals
    Systolic INT NULL,                                 -- For BP
    Diastolic INT NULL,                                -- For BP

    -- Unit (FK to CodeValue where CodeSet='UNIT')
    UnitCodeSID BIGINT NULL,                           -- FK to NDimMill.CodeValue
    UnitName VARCHAR(50) NULL,                         -- Denormalized: 'mmHg', 'bpm', etc.

    -- Timing
    TakenDateTime DATETIME NOT NULL,                   -- When vital was measured
    EnteredDateTime DATETIME NOT NULL DEFAULT GETDATE(), -- When recorded in system

    -- Location
    LocationName VARCHAR(200) NULL,                    -- Where vital was taken
    Sta3n VARCHAR(10) NULL,                            -- Site/facility (denormalized)

    -- Administrative
    IsActive BIT NOT NULL DEFAULT 1,

    -- Foreign key constraints
    CONSTRAINT FK_VitalResult_Encounter
        FOREIGN KEY (EncounterSID) REFERENCES EncMill.Encounter(EncounterSID),
    CONSTRAINT FK_VitalResult_Person
        FOREIGN KEY (PersonSID) REFERENCES VeteranMill.SPerson(PersonSID),
    CONSTRAINT FK_VitalResult_VitalType
        FOREIGN KEY (VitalTypeCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID),
    CONSTRAINT FK_VitalResult_Unit
        FOREIGN KEY (UnitCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID)
);
GO

-- Index for patient vital lookups
CREATE INDEX IX_VitalResult_Person
    ON VitalMill.VitalResult (PersonSID, TakenDateTime DESC);
GO

-- Index for ICN lookups (cross-database queries)
CREATE INDEX IX_VitalResult_ICN
    ON VitalMill.VitalResult (PatientICN, TakenDateTime DESC);
GO

-- Index for encounter-based lookups (Cerner pattern)
CREATE INDEX IX_VitalResult_Encounter
    ON VitalMill.VitalResult (EncounterSID, TakenDateTime DESC);
GO

-- Index for vital type filtering
CREATE INDEX IX_VitalResult_VitalType
    ON VitalMill.VitalResult (VitalTypeCodeSID, TakenDateTime DESC);
GO

PRINT '  - VitalResult table created with indexes';
PRINT '  - Ready for BP, Pulse, Temperature, Weight data';
PRINT '  - Phase 1: 5-10 vitals per demo patient at Portland (648) and Seattle (663)';
GO
