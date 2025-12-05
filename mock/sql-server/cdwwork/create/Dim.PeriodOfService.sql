/*
|------------------------------------------------------------
| Create: Dim.PeriodOfService.sql
|------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create PeriodOfService table in the Dim schema
CREATE TABLE Dim.PeriodOfService
(
    PeriodOfServiceSID              int             NOT NULL,
    PeriodOfServiceIEN              varchar(50)     NOT NULL,
    Sta3n                           smallint        NOT NULL,
    PeriodOfService                 varchar(50)     NULL,
    PeriodOfServiceAbbreviation     varchar(50)     NULL,
    PeriodOfServiceCode             varchar(50)     NULL,
);
GO

-- create indexes
CREATE INDEX IX_PeriodOfServiceSID ON Dim.PeriodOfService (PeriodOfServiceSID);
CREATE INDEX IX_PeriodOfServiceIEN ON Dim.PeriodOfService (PeriodOfServiceIEN);
CREATE INDEX IX_Sta3n ON Dim.PeriodOfService (Sta3n);
CREATE INDEX IX_PeriodOfServiceCode ON Dim.PeriodOfService (PeriodOfServiceCode);
GO
