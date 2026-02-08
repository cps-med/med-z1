-----------------------------------------------------------------------
-- db_schemas.sql
-- Create all required schemas for the CDWWork database
-- --------------------------------------------------------------------
-- To see a list of all schemas, run:
-- SELECT name AS SchemaName FROM sys.schemas ORDER BY name;
-----------------------------------------------------------------------

USE CDWWork;
GO

PRINT 'Creating database schemas...';
GO

-- =======================================================================
-- DIMENSION AND REFERENCE DATA SCHEMAS
-- =======================================================================

-- Dimension tables (facilities, locations, drugs, etc.)
CREATE SCHEMA Dim;
GO

-- =======================================================================
-- PATIENT AND STAFF SCHEMAS
-- =======================================================================

-- Patient demographic and administrative data
CREATE SCHEMA SPatient;
GO

-- Staff and provider data
CREATE SCHEMA SStaff;
GO

-- =======================================================================
-- CLINICAL DOMAIN SCHEMAS
-- =======================================================================

-- Inpatient encounters and admissions
CREATE SCHEMA Inpat;
GO

-- Outpatient pharmacy (prescriptions, fills, etc.)
CREATE SCHEMA RxOut;
GO

-- Bar Code Medication Administration
CREATE SCHEMA BCMA;
GO

-- Allergy and adverse reaction data
CREATE SCHEMA Allergy;
GO

-- Vital signs measurements
CREATE SCHEMA Vital;
GO

-- Laboratory chemistry results
CREATE SCHEMA Chem;
GO

-- Clinical notes (Text Integration Utilities)
CREATE SCHEMA TIU;
GO

-- Immunizations
CREATE SCHEMA Immunization;
GO

-- Outpatient problem list
CREATE SCHEMA Outpat;
GO

PRINT 'All schemas created successfully.';
GO
