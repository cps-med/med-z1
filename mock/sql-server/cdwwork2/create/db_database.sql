-------------------------------------------------------------------------
-- db_database.sql
-- Cleanly drop and recreate the CDWWork2 database with terminal logging
-- CDWWork2 simulates Oracle Health (Cerner Millennium) data structure
-------------------------------------------------------------------------

USE master;
GO

-- Check if database exists
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'CDWWork2')
BEGIN
    PRINT '==> CDWWork2 exists. Terminating active connections...';
    -- Terminate connections and drop the database
    ALTER DATABASE CDWWork2 SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE CDWWork2;
    PRINT '==> CDWWork2 database dropped.';
END
ELSE
BEGIN
    PRINT '==> CDWWork2 does not exist.';
END
GO

-- Create database
PRINT '==> Creating database CDWWork2...';
CREATE DATABASE CDWWork2;
GO

PRINT '==> Database CDWWork2 created successfully.';
GO
