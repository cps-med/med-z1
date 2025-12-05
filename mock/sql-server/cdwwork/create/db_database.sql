-------------------------------------------------------------------------
-- db_database.sql
-- Cleanly drop and recreate the CDWWork database with terminal logging
-------------------------------------------------------------------------

USE master;
GO

-- Check if database exists
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'CDWWork')
BEGIN
    PRINT '==> CDWWork exists. Terminating active connections...';
    -- Terminate connections and drop the database
    ALTER DATABASE CDWWork SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE CDWWork;
    PRINT '==> CDWWork database dropped.';
END
ELSE
BEGIN
    PRINT '==> CDWWork does not exist.';
END
GO

-- Create database
PRINT '==> Creating database CDWWork...';
CREATE DATABASE CDWWork;
GO

PRINT '==> Database CDWWork created successfully.';
GO
