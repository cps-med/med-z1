-- =============================================================================
-- Dim.Location - Location Dimension Table
-- =============================================================================
-- Purpose: Stores physical locations where clinical activities occur
-- Used by: Labs, Encounters, Vitals, Orders, Medications, etc.
-- =============================================================================

USE CDWWork;
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Dim.Location', 'U') IS NOT NULL
    DROP TABLE [Dim].[Location];
GO

PRINT 'Creating Dim.Location table...';
GO

-- Create Location dimension table
CREATE TABLE [Dim].[Location] (
    -- Primary key
    [LocationSID] INT IDENTITY(1,1) PRIMARY KEY,

    -- Core attributes
    [LocationName] VARCHAR(100) NOT NULL,
    [LocationType] VARCHAR(50) NOT NULL,  -- Inpatient, Outpatient, Emergency, Laboratory, etc.
    [Sta3n] INT NOT NULL,                 -- VA Station Number

    -- Optional physical attributes
    [BuildingName] VARCHAR(50),
    [Floor] VARCHAR(10),
    [RoomNumber] VARCHAR(20),

    -- Metadata
    [IsActive] BIT DEFAULT 1,
    [CreatedDate] DATETIME2(0) DEFAULT GETDATE(),
    [ModifiedDate] DATETIME2(0) DEFAULT GETDATE()
);
GO

PRINT 'Dim.Location table created successfully.';
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Creating indexes on Dim.Location...';
GO

-- Index on LocationName for lookups
CREATE NONCLUSTERED INDEX [IX_Location_LocationName]
    ON [Dim].[Location] ([LocationName]);
GO

-- Index on LocationType for filtering
CREATE NONCLUSTERED INDEX [IX_Location_LocationType]
    ON [Dim].[Location] ([LocationType]);
GO

-- Index on Sta3n for facility-based queries
CREATE NONCLUSTERED INDEX [IX_Location_Sta3n]
    ON [Dim].[Location] ([Sta3n]);
GO

-- Composite index for Sta3n + LocationType (common query pattern)
CREATE NONCLUSTERED INDEX [IX_Location_Sta3n_LocationType]
    ON [Dim].[Location] ([Sta3n], [LocationType]);
GO

PRINT 'Indexes created successfully.';
PRINT 'Dim.Location table setup complete.';
GO
