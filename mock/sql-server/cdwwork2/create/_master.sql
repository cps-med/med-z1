-------------------------------------------------------------------------
-- Master SQL Script for Creating CDWWork2 Database
-- Oracle Health (Cerner Millennium) Mock Database Structure
-------------------------------------------------------------------------
-- Run this script from terminal within "create" folder, using command:
-- sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -C -i _master.sql
--
-- Phase 1 Implementation: Foundation (Days 1-2)
-- - Database and schemas
-- - Code value system (NDimMill)
-- - Patient demographics (2 demo patients)
-- - Encounters (5-10 per patient at Cerner sites)
-- - Vitals schema (data to be populated in Day 3-5)
-- - Allergies schema (data to be populated in Day 6-8)
-------------------------------------------------------------------------

PRINT '';
PRINT '=======================================================================';
PRINT 'CDWWork2 Database Creation - Phase 1 Foundation';
PRINT 'Oracle Health (Cerner Millennium) Mock Database';
PRINT '=======================================================================';
PRINT '';

-- =======================================================================
-- STEP 1: Database and Schemas
-- =======================================================================

PRINT 'STEP 1: Creating database and schemas...';
PRINT '';

-- Drop and create database
:r db_database.sql

-- Create required schemas
:r db_schemas.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 2: Creating dimension tables (Code Value System)';
PRINT '=======================================================================';
PRINT '';

-- Consolidated code value system (replaces VistA's many Dim tables)
:r NDimMill.CodeValue.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 3: Creating patient and encounter tables';
PRINT '=======================================================================';
PRINT '';

-- Patient demographics
:r VeteranMill.SPerson.sql

-- Encounters (Cerner is encounter-centric)
:r EncMill.Encounter.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 4: Creating clinical domain tables';
PRINT '=======================================================================';
PRINT '';

-- Vital signs
:r VitalMill.VitalResult.sql

-- Allergies and reactions
:r AllergyMill.PersonAllergy.sql
:r AllergyMill.AdverseReaction.sql

-- Immunizations
:r ImmunizationMill.VaccineCode.sql
:r ImmunizationMill.VaccineAdmin.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'CDWWork2 Database Creation Complete!';
PRINT '=======================================================================';
PRINT '';
PRINT 'Next Steps:';
PRINT '  1. Run insert/_master.sql to populate demo data';
PRINT '';
GO
