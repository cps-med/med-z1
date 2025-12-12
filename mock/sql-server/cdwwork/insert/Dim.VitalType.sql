-- Insert seed data: Dim.VitalType
-- Purpose: Populate vital type dimension with standard VistA vital types

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

SET IDENTITY_INSERT Dim.VitalType ON;
GO

INSERT INTO Dim.VitalType (VitalTypeSID, VitalTypeIEN, VitalType, Abbreviation, UnitOfMeasure, Category, IsActive, Sta3n)
VALUES
    (1, '1', 'BLOOD PRESSURE', 'BP', 'mmHg', 'VITAL SIGN', 1, NULL),
    (2, '2', 'TEMPERATURE', 'T', 'F', 'VITAL SIGN', 1, NULL),
    (3, '3', 'PULSE', 'P', '/min', 'VITAL SIGN', 1, NULL),
    (4, '4', 'RESPIRATION', 'R', '/min', 'VITAL SIGN', 1, NULL),
    (5, '5', 'HEIGHT', 'HT', 'in', 'MEASUREMENT', 1, NULL),
    (6, '6', 'WEIGHT', 'WT', 'lb', 'MEASUREMENT', 1, NULL),
    (7, '7', 'PAIN', 'PN', '0-10', 'VITAL SIGN', 1, NULL),
    (8, '8', 'PULSE OXIMETRY', 'POX', '%', 'VITAL SIGN', 1, NULL),
    (9, '9', 'BLOOD GLUCOSE', 'BG', 'mg/dL', 'MEASUREMENT', 1, NULL),
    (10, '10', 'BMI', 'BMI', 'kg/m^2', 'CALCULATED', 1, NULL);
GO

SET IDENTITY_INSERT Dim.VitalType OFF;
GO

PRINT 'Inserted 10 vital types into Dim.VitalType';
GO

-- Verify
SELECT VitalTypeSID, VitalType, Abbreviation, UnitOfMeasure, Category
FROM Dim.VitalType
ORDER BY VitalTypeSID;
GO
