------------------------------------------------------------
-- Create: Dim.Country.sql
------------------------------------------------------------

PRINT '================================================';
PRINT '====              Dim.Country               ====';
PRINT '================================================';
GO

-- set the active database
USE CDWWork;
GO

-- create Country table in the Dim schema
CREATE TABLE Dim.Country
(
    CountrySID           int             NOT NULL,
    CountryIEN           varchar(50)     NOT NULL,
    Sta3n                smallint        NOT NULL,
    CountryCode          varchar(50)     NULL,
    NumericCode          varchar(50)     NULL,
    PostalName           varchar(100)    NULL,
    PostalDescription    varchar(100)    NULL
);
GO

-- create indexes
CREATE INDEX IX_CountrySID ON Dim.Country (CountrySID);
CREATE INDEX IX_CountryIEN ON Dim.Country (CountryIEN);
CREATE INDEX IX_Sta3n ON Dim.Country (Sta3n);
CREATE INDEX IX_CountryCode ON Dim.Country (CountryCode);
GO