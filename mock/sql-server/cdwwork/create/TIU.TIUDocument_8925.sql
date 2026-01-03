-- =============================================
-- Create Schema: TIU
-- Create Table: TIU.TIUDocument_8925
-- Description: TIU (Text Integration Utilities) document fact table
--              Contains clinical note metadata (VistA file 8925)
-- Author: Claude Code
-- Date: 2026-01-02
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Create TIU schema if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'TIU')
BEGIN
    EXEC('CREATE SCHEMA TIU');
    PRINT 'Schema TIU created successfully';
END
GO

-- Drop table if exists (for development)
IF OBJECT_ID('TIU.TIUDocument_8925', 'U') IS NOT NULL
    DROP TABLE TIU.TIUDocument_8925;
GO

-- Create TIUDocument_8925 fact table
CREATE TABLE TIU.TIUDocument_8925 (
    TIUDocumentSID          BIGINT IDENTITY(1,1) PRIMARY KEY,
    PatientSID              BIGINT NOT NULL,                    -- FK to SPatient.Patient
    DocumentDefinitionSID   INT NOT NULL,                       -- FK to Dim.TIUDocumentDefinition

    -- Temporal data
    ReferenceDateTime       DATETIME2(3) NOT NULL,              -- Clinical date (primary sort)
    EntryDateTime           DATETIME2(3) NOT NULL,              -- When note was entered/authored

    -- Status and workflow
    Status                  VARCHAR(50) NOT NULL,               -- 'COMPLETED', 'UNSIGNED', 'RETRACTED', 'AMENDED'

    -- Authorship
    AuthorSID               BIGINT NULL,                        -- FK to SStaff.Staff (author)
    CosignerSID             BIGINT NULL,                        -- FK to SStaff.Staff (cosigner, if required)

    -- Context
    VisitSID                BIGINT NULL,                        -- FK to encounter/visit (if applicable)

    -- Administrative
    Sta3n                   SMALLINT NOT NULL,                  -- Facility
    TIUDocumentIEN          VARCHAR(50),                        -- VistA file 8925 IEN

    -- Metadata
    CreatedDateTimeUTC      DATETIME2(3) DEFAULT GETUTCDATE(),
    UpdatedDateTimeUTC      DATETIME2(3)
);
GO

-- Indexing (Critical for performance)
-- Primary index: Patient + Date (most common query pattern)
CREATE INDEX IX_TIUDocument_Patient_Date
    ON TIU.TIUDocument_8925(PatientSID, ReferenceDateTime DESC)
    WHERE Status = 'COMPLETED';  -- Filtered index for completed notes only
GO

-- Index for note type queries
CREATE INDEX IX_TIUDocument_Definition
    ON TIU.TIUDocument_8925(DocumentDefinitionSID, ReferenceDateTime DESC);
GO

-- Index for facility queries
CREATE INDEX IX_TIUDocument_Facility
    ON TIU.TIUDocument_8925(Sta3n, ReferenceDateTime DESC);
GO

-- Index for status queries (unsigned notes, etc.)
CREATE INDEX IX_TIUDocument_Status
    ON TIU.TIUDocument_8925(Status, ReferenceDateTime DESC);
GO

PRINT 'Table TIU.TIUDocument_8925 created successfully';
GO
