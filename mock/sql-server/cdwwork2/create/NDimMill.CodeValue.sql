-----------------------------------------------------------------------
-- NDimMill.CodeValue.sql
-- Consolidated code value table for Oracle Health (Cerner)
-- Replaces VistA's many dimension tables (Dim.VitalType, Dim.Allergen, etc.)
-- with single unified code set system
-----------------------------------------------------------------------
-- Design Pattern: Cerner uses consolidated code sets where CodeSet
-- identifies the domain (VITAL_TYPE, ALLERGEN, REACTION, etc.) and
-- Code + DisplayText provide the specific value.
--
-- Example rows:
--   CodeSet='VITAL_TYPE', Code='BP', DisplayText='Blood Pressure'
--   CodeSet='ALLERGEN', Code='PEN', DisplayText='Penicillin'
--   CodeSet='REACTION', Code='RASH', DisplayText='Rash'
--   CodeSet='UNIT', Code='MMHG', DisplayText='mmHg'
-----------------------------------------------------------------------

USE CDWWork2;
GO

PRINT 'Creating NDimMill.CodeValue table...';
GO

CREATE TABLE NDimMill.CodeValue (
    CodeValueSID BIGINT PRIMARY KEY IDENTITY(1,1),  -- Surrogate key
    CodeSet VARCHAR(100) NOT NULL,                  -- Code set category (VITAL_TYPE, ALLERGEN, etc.)
    Code VARCHAR(50) NOT NULL,                      -- Internal code identifier
    DisplayText VARCHAR(200) NOT NULL,              -- Human-readable display name
    Description VARCHAR(500) NULL,                  -- Additional descriptive detail
    IsActive BIT NOT NULL DEFAULT 1,                -- Active status flag

    -- Unique constraint: CodeSet + Code must be unique
    CONSTRAINT UQ_CodeValue_CodeSet_Code UNIQUE (CodeSet, Code)
);
GO

-- Index for fast lookup by CodeSet
CREATE INDEX IX_CodeValue_CodeSet
    ON NDimMill.CodeValue (CodeSet, IsActive);
GO

-- Index for display text searches
CREATE INDEX IX_CodeValue_DisplayText
    ON NDimMill.CodeValue (DisplayText);
GO

PRINT '  - CodeValue table created with indexes';
PRINT '';
PRINT 'Phase 1 Code Sets to Populate:';
PRINT '  - VITAL_TYPE: Blood Pressure, Pulse, Temperature, Weight';
PRINT '  - UNIT: mmHg, bpm, °F, lbs';
PRINT '  - ALLERGEN: Penicillin, Aspirin, Sulfa drugs';
PRINT '  - REACTION: Rash, Hives, Anaphylaxis, Nausea';
PRINT '  - SEVERITY: Mild, Moderate, Severe';
GO
