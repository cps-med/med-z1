/*
|------------------------------------------------------------
| Create: Dim.State.sql
|------------------------------------------------------------
*/

-- set the active database
USE CDWWork;
GO

-- create State table in the Dim schema
CREATE TABLE Dim.[State]
(
    StateSID          int            NOT NULL,
    StateIEN          varchar(50)    NOT NULL,
    Sta3n             smallint       NOT NULL,
    [State]           varchar(50)    NULL,
    StateAbbrev       varchar(5)     NULL,
    VAStateCode       varchar(10)    NULL
);
GO

-- create indexes
CREATE INDEX IX_StateSID ON Dim.[State] (StateSID);
CREATE INDEX IX_StateIEN ON Dim.[State] (StateIEN);
CREATE INDEX IX_Sta3n ON Dim.[State] (Sta3n);
CREATE INDEX IX_State ON Dim.[State] ([State]);
GO
