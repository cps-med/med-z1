------------------------------------------------------------
-- create: Dim_Division.sql
------------------------------------------------------------

-- Set the active database
USE CDWWork;
GO

-- create Division table in the Dim schema
CREATE TABLE Dim.Division
(
    DivisionSID        smallint       NOT NULL,
    DivisionIEN        varchar(50)    NOT NULL,
    Sta3n              smallint       NOT NULL,
    DivisionName       varchar(100)   NULL,
    InstitutionSID     int            NULL,
    Sta6a              varchar(50)    NULL
);
GO

-- create indexes
CREATE INDEX IX_DivisionSID ON Dim.Division (DivisionSID);
CREATE INDEX IX_DivisionIEN ON Dim.Division (DivisionIEN);
CREATE INDEX IX_Sta3n ON Dim.Division (Sta3n);
GO
