-- =============================================================================
-- Dim.LabTest - Laboratory Test Dimension Table
-- =============================================================================
-- Purpose: Stores laboratory test definitions, LOINC codes, and reference ranges
-- Source: VistA File #60 (LABORATORY TEST)
-- Phase: 1 (Chemistry labs only, VistaPackage = 'CH')
-- =============================================================================

USE CDWWork;
GO

-- Create Dim schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Dim')
BEGIN
    EXEC('CREATE SCHEMA Dim');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Dim.LabTest', 'U') IS NOT NULL
    DROP TABLE [Dim].[LabTest];
GO

PRINT 'Creating Dim.LabTest table...';
GO

-- Create LabTest dimension table
CREATE TABLE [Dim].[LabTest] (
    -- Primary key
    [LabTestSID] INT IDENTITY(1,1) PRIMARY KEY,

    -- Test identification
    [LabTestName] VARCHAR(100) NOT NULL,
    [LabTestCode] VARCHAR(50),           -- Local VistA Code or IEN
    [LoincCode] VARCHAR(20),             -- LOINC code for interoperability

    -- Panel classification
    [IsPanel] BIT DEFAULT 0,             -- 1 if this is a panel header, 0 if atomic test
    [PanelName] VARCHAR(100),            -- Panel this test belongs to (e.g., 'BMP', 'CBC')

    -- Units and reference ranges
    [Units] VARCHAR(50),                 -- Default units (e.g., 'mg/dL', 'mmol/L')
    [RefRangeLow] VARCHAR(20),           -- Default low reference value
    [RefRangeHigh] VARCHAR(20),          -- Default high reference value
    [RefRangeText] VARCHAR(100),         -- Full reference range text (e.g., '135 - 145 mg/dL')

    -- Package classification
    [VistaPackage] VARCHAR(10) DEFAULT 'CH',  -- CH=Chemistry, MI=Microbiology, etc.

    -- Metadata
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),
    [IsActive] BIT DEFAULT 1
);
GO

PRINT 'Dim.LabTest table created successfully.';
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Creating indexes on Dim.LabTest...';
GO

-- Index on LabTestName for lookups
CREATE NONCLUSTERED INDEX [IX_LabTest_LabTestName]
    ON [Dim].[LabTest] ([LabTestName]);
GO

-- Index on LoincCode for interoperability queries
CREATE NONCLUSTERED INDEX [IX_LabTest_LoincCode]
    ON [Dim].[LabTest] ([LoincCode])
    WHERE [LoincCode] IS NOT NULL;
GO

-- Index on PanelName for panel-based queries
CREATE NONCLUSTERED INDEX [IX_LabTest_PanelName]
    ON [Dim].[LabTest] ([PanelName])
    WHERE [PanelName] IS NOT NULL;
GO

-- Index on VistaPackage for package filtering
CREATE NONCLUSTERED INDEX [IX_LabTest_VistaPackage]
    ON [Dim].[LabTest] ([VistaPackage]);
GO

PRINT 'Indexes created successfully.';
PRINT 'Dim.LabTest table setup complete.';
GO
