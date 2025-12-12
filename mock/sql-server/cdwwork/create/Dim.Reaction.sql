-- =============================================
-- Create Table: Dim.Reaction
-- Description: Reaction dimension table (allergy symptoms/reactions)
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Dim.Reaction', 'U') IS NOT NULL
    DROP TABLE Dim.Reaction;
GO

-- Create Reaction dimension table
CREATE TABLE Dim.Reaction (
    ReactionSID         INT IDENTITY(1,1) PRIMARY KEY,
    ReactionName        VARCHAR(100) NOT NULL,          -- e.g., "HIVES", "ANAPHYLAXIS"
    VistAIEN            VARCHAR(50),                    -- Link to VistA file 120.83
    Sta3n               SMALLINT,
    IsActive            BIT DEFAULT 1
);
GO

PRINT 'Table Dim.Reaction created successfully';
GO
