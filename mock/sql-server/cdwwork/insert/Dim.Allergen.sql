-- =============================================
-- Insert Data: Dim.Allergen
-- Description: Seed allergen dimension with common allergens
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Enable IDENTITY_INSERT for explicit SID values
SET IDENTITY_INSERT Dim.Allergen ON;
GO

-- Insert allergen seed data
INSERT INTO Dim.Allergen (AllergenSID, AllergenName, AllergenType, IsActive)
VALUES
    -- Drug allergens (most critical for VA population)
    (1, 'PENICILLIN', 'DRUG', 1),
    (2, 'CEPHALOSPORINS', 'DRUG', 1),
    (3, 'SULFA DRUGS', 'DRUG', 1),
    (4, 'ASPIRIN', 'DRUG', 1),
    (5, 'NSAIDS', 'DRUG', 1),
    (6, 'CODEINE', 'DRUG', 1),
    (7, 'MORPHINE', 'DRUG', 1),
    (8, 'LATEX', 'DRUG', 1),
    (9, 'IODINE CONTRAST', 'DRUG', 1),
    (10, 'TETRACYCLINE', 'DRUG', 1),
    (11, 'ERYTHROMYCIN', 'DRUG', 1),
    (12, 'ACE INHIBITORS', 'DRUG', 1),
    (13, 'STATINS', 'DRUG', 1),
    (14, 'HYDROCODONE', 'DRUG', 1),
    (15, 'TRAMADOL', 'DRUG', 1),
    (16, 'GABAPENTIN', 'DRUG', 1),
    (17, 'LISINOPRIL', 'DRUG', 1),
    (18, 'METFORMIN', 'DRUG', 1),
    (19, 'AMOXICILLIN', 'DRUG', 1),

    -- Food allergens
    (20, 'PEANUTS', 'FOOD', 1),
    (21, 'TREE NUTS', 'FOOD', 1),
    (22, 'SHELLFISH', 'FOOD', 1),
    (23, 'FISH', 'FOOD', 1),
    (24, 'EGGS', 'FOOD', 1),
    (25, 'MILK', 'FOOD', 1),
    (26, 'SOY', 'FOOD', 1),
    (27, 'WHEAT', 'FOOD', 1),
    (28, 'SESAME', 'FOOD', 1),

    -- Environmental allergens
    (30, 'POLLEN', 'ENVIRONMENTAL', 1),
    (31, 'DUST MITES', 'ENVIRONMENTAL', 1),
    (32, 'MOLD', 'ENVIRONMENTAL', 1),
    (33, 'PET DANDER', 'ENVIRONMENTAL', 1),
    (34, 'BEE STINGS', 'ENVIRONMENTAL', 1),
    (35, 'INSECT BITES', 'ENVIRONMENTAL', 1);
GO

-- Disable IDENTITY_INSERT
SET IDENTITY_INSERT Dim.Allergen OFF;
GO

PRINT '35 allergen records inserted successfully';
GO
