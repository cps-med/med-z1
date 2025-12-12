-- =============================================
-- Create Table: Allergy.PatientAllergyReaction
-- Description: Bridge table linking allergies to reactions (one-to-many)
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Allergy.PatientAllergyReaction', 'U') IS NOT NULL
    DROP TABLE Allergy.PatientAllergyReaction;
GO

-- Create PatientAllergyReaction bridge table
CREATE TABLE Allergy.PatientAllergyReaction (
    PatientAllergyReactionSID   BIGINT IDENTITY(1,1) PRIMARY KEY,
    PatientAllergySID           BIGINT NOT NULL,            -- FK to Allergy.PatientAllergy
    ReactionSID                 INT NOT NULL,               -- FK to Dim.Reaction

    CONSTRAINT FK_AllergyReaction_Allergy FOREIGN KEY (PatientAllergySID)
        REFERENCES Allergy.PatientAllergy(PatientAllergySID),
    CONSTRAINT FK_AllergyReaction_Reaction FOREIGN KEY (ReactionSID)
        REFERENCES Dim.Reaction(ReactionSID)
);
GO

-- Index for fast retrieval of reactions for a specific allergy
CREATE INDEX IX_PatientAllergyReaction_Allergy
    ON Allergy.PatientAllergyReaction(PatientAllergySID);
GO

PRINT 'Table Allergy.PatientAllergyReaction created successfully';
GO
