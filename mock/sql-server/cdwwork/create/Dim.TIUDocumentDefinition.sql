-- =============================================
-- Create Table: Dim.TIUDocumentDefinition
-- Description: TIU (Text Integration Utilities) document type definitions
--              Maps note types to standard VA enterprise titles
-- Author: Claude Code
-- Date: 2026-01-02
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('Dim.TIUDocumentDefinition', 'U') IS NOT NULL
    DROP TABLE Dim.TIUDocumentDefinition;
GO

-- Create TIUDocumentDefinition dimension table
CREATE TABLE Dim.TIUDocumentDefinition (
    DocumentDefinitionSID   INT IDENTITY(1,1) PRIMARY KEY,
    TIUDocumentTitle        VARCHAR(200) NOT NULL,              -- VistA note type (e.g., "GEN MED PROGRESS NOTE")
    DocumentClass           VARCHAR(100),                        -- Classification (e.g., "Progress Notes", "Consults")
    VHAEnterpriseStandardTitle VARCHAR(200),                    -- Standardized VA enterprise title
    IsActive                BIT DEFAULT 1,
    Sta3n                   SMALLINT,                            -- Facility if locally defined
    TIUDocumentDefinitionIEN VARCHAR(50),                       -- VistA file 8925.1 IEN

    CONSTRAINT UQ_TIUDocDef_Title_Sta3n UNIQUE (TIUDocumentTitle, Sta3n)
);
GO

-- Index for common queries
CREATE INDEX IX_TIUDocDef_Class
    ON Dim.TIUDocumentDefinition(DocumentClass, IsActive);
GO

PRINT 'Table Dim.TIUDocumentDefinition created successfully';
GO
