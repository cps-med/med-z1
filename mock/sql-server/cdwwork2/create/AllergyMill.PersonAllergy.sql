-----------------------------------------------------------------------
-- AllergyMill.PersonAllergy.sql
-- Patient allergy assignments for Oracle Health (Cerner)
-- Corresponds to CDWWork's Allergy.PatientAllergy
-----------------------------------------------------------------------
-- Design Notes:
-- - Links to NDimMill.CodeValue for allergen (CodeSet='ALLERGEN')
-- - Links to NDimMill.CodeValue for severity (CodeSet='SEVERITY')
-- - Reactions stored in separate AllergyMill.AdverseReaction table
-- - Encounter-linked (Cerner pattern)
-- - Phase 1: 2-3 allergies per demo patient
-----------------------------------------------------------------------

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Creating AllergyMill.PersonAllergy table...';
GO

CREATE TABLE AllergyMill.PersonAllergy (
    PersonAllergySID BIGINT PRIMARY KEY IDENTITY(1,1), -- Cerner-specific allergy ID
    EncounterSID BIGINT NOT NULL,                       -- FK to EncMill.Encounter (where documented)
    PersonSID BIGINT NOT NULL,                          -- FK to VeteranMill.SPerson
    PatientICN VARCHAR(50) NOT NULL,                    -- Denormalized for performance

    -- Allergen (FK to CodeValue where CodeSet='ALLERGEN')
    AllergenCodeSID BIGINT NOT NULL,                    -- FK to NDimMill.CodeValue
    AllergenName VARCHAR(200) NOT NULL,                 -- Denormalized: 'Penicillin', 'Aspirin', etc.
    AllergyType VARCHAR(50) NULL,                       -- 'Drug', 'Food', 'Environmental'

    -- Severity (FK to CodeValue where CodeSet='SEVERITY')
    SeverityCodeSID BIGINT NULL,                        -- FK to NDimMill.CodeValue
    SeverityName VARCHAR(50) NULL,                      -- Denormalized: 'Mild', 'Moderate', 'Severe'

    -- Status
    Status VARCHAR(50) NOT NULL DEFAULT 'Active',       -- Active, Inactive, Resolved
    IsActive BIT NOT NULL DEFAULT 1,

    -- Timing
    OnsetDate DATE NULL,                                -- When allergy first occurred
    DocumentedDateTime DATETIME NOT NULL,               -- When documented in system
    EnteredDateTime DATETIME NOT NULL DEFAULT GETDATE(),

    -- Source
    Sta3n VARCHAR(10) NULL,                             -- Site where documented
    SourceProvider VARCHAR(200) NULL,                   -- Who documented

    -- Comments
    Comments VARCHAR(1000) NULL,                        -- Free-text notes

    -- Foreign key constraints
    CONSTRAINT FK_PersonAllergy_Encounter
        FOREIGN KEY (EncounterSID) REFERENCES EncMill.Encounter(EncounterSID),
    CONSTRAINT FK_PersonAllergy_Person
        FOREIGN KEY (PersonSID) REFERENCES VeteranMill.SPerson(PersonSID),
    CONSTRAINT FK_PersonAllergy_Allergen
        FOREIGN KEY (AllergenCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID),
    CONSTRAINT FK_PersonAllergy_Severity
        FOREIGN KEY (SeverityCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID)
);
GO

-- Index for patient allergy lookups
CREATE INDEX IX_PersonAllergy_Person
    ON AllergyMill.PersonAllergy (PersonSID, DocumentedDateTime DESC);
GO

-- Index for ICN lookups (cross-database queries)
CREATE INDEX IX_PersonAllergy_ICN
    ON AllergyMill.PersonAllergy (PatientICN, DocumentedDateTime DESC);
GO

-- Index for active allergies
CREATE INDEX IX_PersonAllergy_Active
    ON AllergyMill.PersonAllergy (PersonSID, IsActive)
    WHERE IsActive = 1;
GO

-- Index for allergen-based searches
CREATE INDEX IX_PersonAllergy_Allergen
    ON AllergyMill.PersonAllergy (AllergenCodeSID);
GO

PRINT '  - PersonAllergy table created with indexes';
PRINT '  - Phase 1: 2-3 allergies per demo patient';
GO
