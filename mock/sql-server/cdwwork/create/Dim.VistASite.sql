/*
|------------------------------------------------------------
| Create: Dim_VistASite.sql
|------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create VistASite table in the Dim schema
CREATE TABLE Dim.VistASite
(
    Sta3n               SMALLINT       NOT NULL,
    Facility            VARCHAR(50)    NULL,
    VISN                SMALLINT       NULL,
    Active              CHAR(1)        NULL,
    NextSta3n           INT            NULL,
    Region              SMALLINT       NULL,
    TimeZone            VARCHAR(100)   NULL,
    SiteCode            VARCHAR(100)   NULL,
    DistrictNumber      VARCHAR(100)   NULL,
    DistrictName        VARCHAR(100)   NULL,
    City                VARCHAR(100)   NULL,
    StateSID            INT            NULL
);
GO

-- create indexes
CREATE INDEX IX_Sta3n ON Dim.VistASite (Sta3n);
CREATE INDEX IX_Facility ON Dim.VistASite (Facility);
GO
