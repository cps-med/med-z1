/*
|---------------------------------------------------------------
| Inpat.Inpatient.sql
|---------------------------------------------------------------
| Create Inpatient Encounters table
| Updated: 2025-12-15 for Encounters domain implementation
|---------------------------------------------------------------
*/

PRINT '================================================';
PRINT '====            Inpat.Inpatient             ====';
PRINT '================================================';
GO

-- Set the active database
USE CDWWork;
GO

/*
|----------------------------------------------------------------------
| Drop existing table if needed (development environment only)
|----------------------------------------------------------------------
*/

PRINT '';
PRINT '==== Dropping existing table if exists ====';
GO

IF OBJECT_ID('Inpat.Inpatient', 'U') IS NOT NULL
BEGIN
    DROP TABLE [Inpat].[Inpatient];
    PRINT 'Table dropped successfully';
END
ELSE
BEGIN
    PRINT 'Table does not exist, proceeding to create';
END
GO

/*
|----------------------------------------------------------------------
| Create Table - Enhanced Inpatient Encounters
|----------------------------------------------------------------------
*/

PRINT '';
PRINT '==== Creating table with enhanced schema ====';
GO

-- Create enhanced Inpatient table with all required fields
CREATE TABLE [Inpat].[Inpatient] (
    -- Primary key
    [InpatientSID] BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Patient reference
    [PatientSID] INT NOT NULL,

    -- Admission details
    [AdmitDateTime] DATETIME2(0) NOT NULL,
    [AdmitLocationSID] INT NULL,
    [AdmittingProviderSID] INT NULL,
    [AdmitDiagnosisICD10] VARCHAR(20) NULL,

    -- Discharge details (NULL if active admission)
    [DischargeDateTime] DATETIME2(0) NULL,
    [DischargeDateSID] INT NULL,
    [DischargeWardLocationSID] INT NULL,
    [DischargeDiagnosisICD10] VARCHAR(20) NULL,
    [DischargeDiagnosis] VARCHAR(100) NULL,
    [DischargeDisposition] VARCHAR(50) NULL,

    -- Calculated fields
    [LengthOfStay] INT NULL,
    [EncounterStatus] VARCHAR(20) NULL, -- 'Active', 'Discharged'

    -- Facility
    [Sta3n] INT NOT NULL
);
GO

PRINT 'Table created successfully';
GO

/*
|----------------------------------------------------------------------
| Create Indexes
|----------------------------------------------------------------------
*/

PRINT '';
PRINT '==== Creating indexes ====';
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Index on PatientSID for patient-centric queries
CREATE NONCLUSTERED INDEX [IX_Inpatient_PatientSID]
    ON [Inpat].[Inpatient] ([PatientSID]);
GO

-- Composite index for common query pattern (patient encounters sorted by date)
CREATE NONCLUSTERED INDEX [IX_Inpatient_PatientSID_AdmitDateTime]
    ON [Inpat].[Inpatient] ([PatientSID], [AdmitDateTime] DESC);
GO

-- Index on AdmitDateTime for date range queries
CREATE NONCLUSTERED INDEX [IX_Inpatient_AdmitDateTime]
    ON [Inpat].[Inpatient] ([AdmitDateTime] DESC);
GO

-- Index on Sta3n for facility-based queries
CREATE NONCLUSTERED INDEX [IX_Inpatient_Sta3n]
    ON [Inpat].[Inpatient] ([Sta3n]);
GO

-- Index on EncounterStatus for active/discharged filtering
CREATE NONCLUSTERED INDEX [IX_Inpatient_EncounterStatus]
    ON [Inpat].[Inpatient] ([EncounterStatus])
    WHERE [EncounterStatus] IS NOT NULL;
GO

PRINT 'Indexes created successfully';
GO

PRINT '';
PRINT '==== Done ====';
GO
