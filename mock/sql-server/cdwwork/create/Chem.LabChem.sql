-- =============================================================================
-- Chem.LabChem - Laboratory Results Fact Table
-- =============================================================================
-- Purpose: Stores chemistry lab results (high-volume fact table)
-- Source: VistA File #63 (LAB DATA)
-- Phase: 1 (Chemistry labs only, VistaPackage = 'CH')
-- =============================================================================

USE CDWWork;
GO

-- Create Chem schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Chem')
BEGIN
    EXEC('CREATE SCHEMA Chem');
END
GO

-- Drop existing table if needed (development environment only)
IF OBJECT_ID('Chem.LabChem', 'U') IS NOT NULL
    DROP TABLE [Chem].[LabChem];
GO

PRINT 'Creating Chem.LabChem table...';
GO

-- Create LabChem fact table
CREATE TABLE [Chem].[LabChem] (
    -- Primary key
    [LabChemSID] BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Foreign keys
    [PatientSID] INT NOT NULL,           -- FK to SPatient.SPatient
    [LabTestSID] INT NOT NULL,           -- FK to Dim.LabTest
    [LabOrderSID] INT NULL,              -- FK to Lab.LabOrder (optional)

    -- Panel grouping
    [AccessionNumber] VARCHAR(50),       -- Critical for grouping panel results (e.g., "CH 1234")

    -- Result data
    [Result] VARCHAR(100),               -- Text representation (e.g., "140", "Positive", "<5.0")
    [ResultNumeric] DECIMAL(18,4),       -- Parsed numeric value for graphing (NULL if non-numeric)
    [ResultUnit] VARCHAR(50),            -- Unit at time of result (may differ from default)

    -- Flags and ranges
    [AbnormalFlag] VARCHAR(10),          -- 'H' (High), 'L' (Low), 'H*' (Critical High), 'L*' (Critical Low), 'Panic'
    [RefRange] VARCHAR(50),              -- Range string at time of result (e.g., "135 - 145")

    -- Temporal data
    [CollectionDateTime] DATETIME2(0),   -- When specimen was collected (clinical relevance)
    [ResultDateTime] DATETIME2(0),       -- When result was verified/reported

    -- Administrative
    [VistaPackage] VARCHAR(10) DEFAULT 'CH',  -- CH=Chemistry, MI=Micro, CY=Cyto, AP=Anatomic Path
    [LocationSID] INT,                   -- Collection location (Inpatient Ward, Outpatient Clinic, ER)
    [Sta3n] INT NOT NULL,                -- VA Station Number

    -- Metadata
    [PerformingLabSID] INT,              -- Lab that performed the test
    [OrderingProviderSID] INT,           -- Provider who ordered the test
    [SpecimenType] VARCHAR(50)           -- Specimen type (e.g., "Blood", "Serum", "Urine")
);
GO

PRINT 'Chem.LabChem table created successfully.';
GO

-- Create indexes for query performance
SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Creating indexes on Chem.LabChem...';
GO

-- Index on PatientSID for patient-centric queries
CREATE NONCLUSTERED INDEX [IX_LabChem_PatientSID]
    ON [Chem].[LabChem] ([PatientSID]);
GO

-- Composite index for patient labs sorted by date (most common query pattern)
CREATE NONCLUSTERED INDEX [IX_LabChem_PatientSID_CollectionDateTime]
    ON [Chem].[LabChem] ([PatientSID], [CollectionDateTime] DESC);
GO

-- Index on CollectionDateTime for date range queries
CREATE NONCLUSTERED INDEX [IX_LabChem_CollectionDateTime]
    ON [Chem].[LabChem] ([CollectionDateTime] DESC);
GO

-- Index on AccessionNumber for panel grouping
CREATE NONCLUSTERED INDEX [IX_LabChem_AccessionNumber]
    ON [Chem].[LabChem] ([AccessionNumber])
    WHERE [AccessionNumber] IS NOT NULL;
GO

-- Index on LabTestSID for test-specific queries
CREATE NONCLUSTERED INDEX [IX_LabChem_LabTestSID]
    ON [Chem].[LabChem] ([LabTestSID]);
GO

-- Index on AbnormalFlag for filtering abnormal results
CREATE NONCLUSTERED INDEX [IX_LabChem_AbnormalFlag]
    ON [Chem].[LabChem] ([AbnormalFlag])
    WHERE [AbnormalFlag] IS NOT NULL;
GO

-- Composite index for patient + test trending queries
CREATE NONCLUSTERED INDEX [IX_LabChem_PatientSID_LabTestSID_CollectionDateTime]
    ON [Chem].[LabChem] ([PatientSID], [LabTestSID], [CollectionDateTime] DESC);
GO

PRINT 'Indexes created successfully.';
PRINT 'Chem.LabChem table setup complete.';
GO
