/*
|------------------------------------------------------------
| Create: Dim_Sta3n.sql
|------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create Sta3n table in the Dim schema
CREATE TABLE Dim.Sta3n
(
    Sta3n               SMALLINT       NOT NULL,
    Sta3nName           VARCHAR(50)    NULL,
    VISNPreFY15         SMALLINT       NULL,
    VISNFY16            SMALLINT       NULL,
    VISNFY17            SMALLINT       NULL,
    Active              CHAR(1)        NULL,
    NextSta3n           INT            NULL,
    TimeZone            VARCHAR(100)   NULL,
    SiteCode            VARCHAR(100)   NULL,
    RegionFY15          SMALLINT       NULL,
    DistrictNameFY16    VARCHAR(100)   NULL,
    DistrictNumberFY16  VARCHAR(100)   NULL,
    DistrictNameFY17    VARCHAR(100)   NULL,
    DistrictNumberFY17  VARCHAR(100)   NULL,
    City                VARCHAR(100)   NULL,
    StateSID            INT            NULL
);
GO

-- create indexes
CREATE INDEX IX_Sta3n ON Dim.Sta3n (Sta3n);
CREATE INDEX IX_Sta3nName ON Dim.Sta3n (Sta3nName);
GO
