-----------------------------------------------------------------------
-- db_schemas.sql
-- Create all required schemas for the CDWWork2 database
-- CDWWork2 simulates Oracle Health (Cerner Millennium) data structure
-- --------------------------------------------------------------------
-- To see a list of all schemas, run:
-- SELECT name AS SchemaName FROM sys.schemas ORDER BY name;
-----------------------------------------------------------------------

USE CDWWork2;
GO

PRINT 'Creating Oracle Health (Cerner) database schemas...';
GO

-- =======================================================================
-- DIMENSION AND REFERENCE DATA SCHEMAS
-- =======================================================================

-- Normalized dimension tables - Cerner uses consolidated code value system
-- All code sets (vitals, allergies, reactions, etc.) stored in CodeValue
CREATE SCHEMA NDimMill;
GO

-- =======================================================================
-- PATIENT AND ENCOUNTER SCHEMAS
-- =======================================================================

-- Veteran/Patient demographic and administrative data
-- Cerner terminology: "Person" instead of "Patient"
CREATE SCHEMA VeteranMill;
GO

-- Encounter-based clinical data (Cerner is encounter-centric vs VistA patient-centric)
CREATE SCHEMA EncMill;
GO

-- =======================================================================
-- CLINICAL DOMAIN SCHEMAS
-- =======================================================================

-- Vital signs measurements
CREATE SCHEMA VitalMill;
GO

-- Allergy and adverse reaction data
CREATE SCHEMA AllergyMill;
GO

-- Immunizations (vaccines and administration)
CREATE SCHEMA ImmunizationMill;
GO

PRINT 'All Oracle Health (Cerner) schemas created successfully.';
PRINT '';
PRINT 'Implemented Schemas:';
PRINT '  - NDimMill: Consolidated code sets (vitals, allergies, units, reactions)';
PRINT '  - VeteranMill: Patient demographics';
PRINT '  - EncMill: Encounters and problem list';
PRINT '  - VitalMill: Vital signs results';
PRINT '  - AllergyMill: Allergy and reaction data';
PRINT '  - ImmunizationMill: Vaccine codes and administration records';
GO
