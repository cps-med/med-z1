-- =============================================
-- Create Table: Dim.AllergySeverity
-- Description: Allergy severity dimension table
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Dim.AllergySeverity', 'U') IS NOT NULL
    DROP TABLE Dim.AllergySeverity;
GO

-- Create AllergySeverity dimension table
CREATE TABLE Dim.AllergySeverity (
    AllergySeveritySID  INT IDENTITY(1,1) PRIMARY KEY,
    SeverityName        VARCHAR(50) NOT NULL,           -- "MILD", "MODERATE", "SEVERE"
    SeverityRank        INT,                            -- For sorting (1=MILD, 2=MODERATE, 3=SEVERE)
    IsActive            BIT DEFAULT 1
);
GO

PRINT 'Table Dim.AllergySeverity created successfully';
GO
