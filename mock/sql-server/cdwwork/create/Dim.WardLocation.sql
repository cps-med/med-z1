/*
|------------------------------------------------------------
| Create: Dim_WardLocation.sql
|------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create WardLocation table in the Dim schema
CREATE TABLE Dim.WardLocation
(
    WardLocationSID    int            NOT NULL,
    WardLocationIEN    varchar(50)    NOT NULL,
    Sta3n              smallint       NOT NULL,
    WardLocationName   varchar(50)    NULL,
    DivisionSID        smallint       NULL,
    DivisionName       varchar(100)   NULL,
    Sta6a              varchar(50)    NULL,
    SpecialtySID       int            NULL,
    Specialty          varchar(50)    NULL,
    BedSection         varchar(50)    NULL,
    MedicalService     varchar(50)    NULL,
    PrimaryLocation    varchar(50)    NULL,
    NursingService     varchar(50)    NULL,
    GLOrder            decimal        NULL,
    LocationSID        int            NULL
);
GO

-- create indexes
CREATE INDEX IX_WardLocationSID ON Dim.WardLocation (WardLocationSID);
CREATE INDEX IX_WardLocationIEN ON Dim.WardLocation (WardLocationIEN);
CREATE INDEX IX_Sta3n ON Dim.WardLocation (Sta3n);
CREATE INDEX IX_DivisionSID ON Dim.WardLocation (DivisionSID);
CREATE INDEX IX_DivisionName ON Dim.WardLocation (DivisionName);
GO
