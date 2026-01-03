-- =============================================
-- Create Table: TIU.TIUDocumentText
-- Description: TIU document text storage table
--              Contains full clinical note narrative text
-- Author: Claude Code
-- Date: 2026-01-02
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('TIU.TIUDocumentText', 'U') IS NOT NULL
    DROP TABLE TIU.TIUDocumentText;
GO

-- Create TIUDocumentText table
CREATE TABLE TIU.TIUDocumentText (
    TIUDocumentSID          BIGINT PRIMARY KEY,                 -- FK to TIU.TIUDocument_8925 (1:1 relationship)
    DocumentText            VARCHAR(MAX),                        -- Full clinical note text

    -- Metadata
    TextLength              INT,                                 -- Computed: length of text for quick reference
    CreatedDateTimeUTC      DATETIME2(3) DEFAULT GETUTCDATE(),
    UpdatedDateTimeUTC      DATETIME2(3),

    -- Foreign key constraint
    CONSTRAINT FK_TIUDocText_TIUDocument FOREIGN KEY (TIUDocumentSID)
        REFERENCES TIU.TIUDocument_8925(TIUDocumentSID)
        ON DELETE CASCADE  -- If note deleted, delete text too
);
GO

PRINT 'Table TIU.TIUDocumentText created successfully';
GO
