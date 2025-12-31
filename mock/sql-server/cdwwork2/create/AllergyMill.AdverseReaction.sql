-----------------------------------------------------------------------
-- AllergyMill.AdverseReaction.sql
-- Adverse reactions linked to allergies for Oracle Health (Cerner)
-- Corresponds to CDWWork's Allergy.PatientAllergyReaction
-----------------------------------------------------------------------
-- Design Notes:
-- - Many-to-one relationship with PersonAllergy
-- - Links to NDimMill.CodeValue for reaction types (CodeSet='REACTION')
-- - One allergy can have multiple reactions (e.g., Penicillin → Rash, Hives)
-- - Phase 1: 1-3 reactions per allergy
-----------------------------------------------------------------------

USE CDWWork2;
GO

PRINT 'Creating AllergyMill.AdverseReaction table...';
GO

CREATE TABLE AllergyMill.AdverseReaction (
    AdverseReactionSID BIGINT PRIMARY KEY IDENTITY(1,1), -- Cerner-specific reaction ID
    PersonAllergySID BIGINT NOT NULL,                     -- FK to PersonAllergy
    PersonSID BIGINT NOT NULL,                            -- FK to VeteranMill.SPerson (denormalized)
    PatientICN VARCHAR(50) NOT NULL,                      -- Denormalized for performance

    -- Reaction (FK to CodeValue where CodeSet='REACTION')
    ReactionCodeSID BIGINT NOT NULL,                      -- FK to NDimMill.CodeValue
    ReactionName VARCHAR(200) NOT NULL,                   -- Denormalized: 'Rash', 'Hives', etc.

    -- Timing
    OnsetDateTime DATETIME NULL,                          -- When reaction occurred
    EnteredDateTime DATETIME NOT NULL DEFAULT GETDATE(),  -- When recorded

    -- Comments
    Comments VARCHAR(500) NULL,                           -- Additional details

    -- Foreign key constraints
    CONSTRAINT FK_AdverseReaction_PersonAllergy
        FOREIGN KEY (PersonAllergySID) REFERENCES AllergyMill.PersonAllergy(PersonAllergySID),
    CONSTRAINT FK_AdverseReaction_Person
        FOREIGN KEY (PersonSID) REFERENCES VeteranMill.SPerson(PersonSID),
    CONSTRAINT FK_AdverseReaction_Reaction
        FOREIGN KEY (ReactionCodeSID) REFERENCES NDimMill.CodeValue(CodeValueSID)
);
GO

-- Index for allergy-based lookups
CREATE INDEX IX_AdverseReaction_Allergy
    ON AllergyMill.AdverseReaction (PersonAllergySID);
GO

-- Index for patient-based lookups
CREATE INDEX IX_AdverseReaction_Person
    ON AllergyMill.AdverseReaction (PersonSID);
GO

-- Index for reaction type searches
CREATE INDEX IX_AdverseReaction_ReactionType
    ON AllergyMill.AdverseReaction (ReactionCodeSID);
GO

PRINT '  - AdverseReaction table created with indexes';
PRINT '  - Phase 1: 1-3 reactions per allergy';
GO
