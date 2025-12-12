-- Insert seed data: Dim.VitalQualifier
-- Purpose: Populate vital qualifier dimension with common VistA qualifiers

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

SET IDENTITY_INSERT Dim.VitalQualifier ON;
GO

INSERT INTO Dim.VitalQualifier (VitalQualifierSID, VitalQualifier, QualifierType, VitalQualifierIEN, IsActive, Sta3n)
VALUES
    -- Position qualifiers
    (1, 'SITTING', 'POSITION', '1', 1, NULL),
    (2, 'STANDING', 'POSITION', '2', 1, NULL),
    (3, 'LYING', 'POSITION', '3', 1, NULL),
    (4, 'SUPINE', 'POSITION', '4', 1, NULL),

    -- Site qualifiers
    (5, 'LEFT ARM', 'SITE', '5', 1, NULL),
    (6, 'RIGHT ARM', 'SITE', '6', 1, NULL),
    (7, 'LEFT LEG', 'SITE', '7', 1, NULL),
    (8, 'RIGHT LEG', 'SITE', '8', 1, NULL),

    -- Cuff size qualifiers
    (9, 'ADULT', 'CUFF SIZE', '9', 1, NULL),
    (10, 'LARGE ADULT', 'CUFF SIZE', '10', 1, NULL),
    (11, 'PEDIATRIC', 'CUFF SIZE', '11', 1, NULL),
    (12, 'THIGH', 'CUFF SIZE', '12', 1, NULL),

    -- Method qualifiers (for temperature)
    (13, 'ORAL', 'METHOD', '13', 1, NULL),
    (14, 'RECTAL', 'METHOD', '14', 1, NULL),
    (15, 'TYMPANIC', 'METHOD', '15', 1, NULL),
    (16, 'AXILLARY', 'METHOD', '16', 1, NULL);
GO

SET IDENTITY_INSERT Dim.VitalQualifier OFF;
GO

PRINT 'Inserted 16 vital qualifiers into Dim.VitalQualifier';
GO

-- Verify
SELECT VitalQualifierSID, VitalQualifier, QualifierType
FROM Dim.VitalQualifier
ORDER BY QualifierType, VitalQualifierSID;
GO
