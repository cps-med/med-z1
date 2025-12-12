-- =============================================
-- Insert Data: Dim.AllergySeverity
-- Description: Seed severity dimension with standard severity levels
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Enable IDENTITY_INSERT for explicit SID values
SET IDENTITY_INSERT Dim.AllergySeverity ON;
GO

-- Insert severity seed data
INSERT INTO Dim.AllergySeverity (AllergySeveritySID, SeverityName, SeverityRank, IsActive)
VALUES
    (1, 'MILD', 1, 1),
    (2, 'MODERATE', 2, 1),
    (3, 'SEVERE', 3, 1);
GO

-- Disable IDENTITY_INSERT
SET IDENTITY_INSERT Dim.AllergySeverity OFF;
GO

PRINT '3 severity records inserted successfully';
GO
