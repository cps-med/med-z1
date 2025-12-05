-----------------------------------------------------------------------
-- db_schemas.sql
-- Create all ofthe required schemas for the CDWWork database
-- --------------------------------------------------------------------
-- To see a list of all schemas, run:
-- SELECT name AS SchemaName FROM sys.schemas ORDER BY name;
-----------------------------------------------------------------------

USE CDWWork;
GO

-- create schema for Dimension tables
CREATE SCHEMA Dim;
GO

-- create schema for Inpatient tables
CREATE SCHEMA Inpat;
GO

-- create schema for SPatient tables
CREATE SCHEMA SPatient;
GO

-- create schema for SStaff tables
CREATE SCHEMA SStaff;
GO

-- create schema for RxOut (pharmacy outpatient) tables
CREATE SCHEMA RxOut;
GO

-- create schema for BCMA (bar code medication administration) tables
CREATE SCHEMA BCMA;
GO
