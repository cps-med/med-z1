---------------------------------------------------------------
-- Create: Dim.LocalDrug.sql
---------------------------------------------------------------
-- Local facility drug file - maps to VA Formulary local drug definitions
-- Represents drugs as they appear in local facility formularies
-- Links to Dim.NationalDrug for standardization
---------------------------------------------------------------

-- Set the active database
USE CDWWork;
GO

-- Create LocalDrug table in the Dim schema
CREATE TABLE Dim.LocalDrug
(
  LocalDrugSID              BIGINT         NOT NULL PRIMARY KEY,
  LocalDrugIEN              VARCHAR(50)    NOT NULL,
  Sta3n                     SMALLINT       NOT NULL,
  NationalDrugSID           BIGINT         NULL,
  NationalDrugIEN           VARCHAR(50)    NULL,
  DrugNameWithoutDose       VARCHAR(120)   NULL,
  DrugNameWithDose          VARCHAR(150)   NULL,
  GenericName               VARCHAR(120)   NULL,
  VAProductName             VARCHAR(150)   NULL,
  Strength                  VARCHAR(50)    NULL,
  Unit                      VARCHAR(50)    NULL,
  DosageForm                VARCHAR(50)    NULL,  -- TAB, CAP, INJ, SOLN, etc.
  DrugClass                 VARCHAR(100)   NULL,  -- e.g., "ANTIHYPERTENSIVE"
  DrugClassCode             VARCHAR(20)    NULL,
  ActiveIngredient          VARCHAR(120)   NULL,
  Inactive                  CHAR(1)        NULL,  -- Y/N
  InactiveDate              DATETIME       NULL
);
GO

-- Create indexes for the Dim.LocalDrug table
CREATE INDEX IX_LocalDrugSID ON Dim.LocalDrug (LocalDrugSID);
CREATE INDEX IX_NationalDrugSID ON Dim.LocalDrug (NationalDrugSID);
CREATE INDEX IX_Sta3n ON Dim.LocalDrug (Sta3n);
CREATE INDEX IX_DrugNameWithDose ON Dim.LocalDrug (DrugNameWithDose);
GO
