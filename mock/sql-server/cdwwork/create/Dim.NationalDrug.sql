---------------------------------------------------------------
-- Create: Dim.NationalDrug.sql
---------------------------------------------------------------
-- National Drug File (NDF) - standardized drug names and NDC codes
-- Represents drugs at the national VA level
-- Used for standardization, reporting, and drug-drug interaction checking
---------------------------------------------------------------

-- Set the active database
USE CDWWork;
GO

-- Create NationalDrug table in the Dim schema
CREATE TABLE Dim.NationalDrug
(
  NationalDrugSID           BIGINT         NOT NULL PRIMARY KEY,
  NationalDrugIEN           VARCHAR(50)    NOT NULL,
  NationalDrugName          VARCHAR(120)   NULL,
  GenericName               VARCHAR(120)   NULL,
  VAGenericName             VARCHAR(120)   NULL,
  TradeName                 VARCHAR(120)   NULL,
  NDCCode                   VARCHAR(20)    NULL,  -- National Drug Code
  DrugClass                 VARCHAR(100)   NULL,
  DrugClassCode             VARCHAR(20)    NULL,
  DEASchedule               VARCHAR(10)    NULL,  -- C-II, C-III, C-IV, C-V
  ControlledSubstanceFlag   CHAR(1)        NULL,  -- Y/N
  ActiveIngredients         VARCHAR(250)   NULL,
  Inactive                  CHAR(1)        NULL,  -- Y/N
  InactiveDate              DATETIME       NULL
);
GO

-- Create indexes for the Dim.NationalDrug table
CREATE INDEX IX_NationalDrugSID ON Dim.NationalDrug (NationalDrugSID);
CREATE INDEX IX_NDCCode ON Dim.NationalDrug (NDCCode);
CREATE INDEX IX_DEASchedule ON Dim.NationalDrug (DEASchedule);
CREATE INDEX IX_NationalDrugName ON Dim.NationalDrug (NationalDrugName);
GO
