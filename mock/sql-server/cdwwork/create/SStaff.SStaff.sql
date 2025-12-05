---------------------------------------------------------------
-- Create: SStaff.SStaff.sql
-- VA Staff, including providers.
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create SStaff table in the SStaff schema
CREATE TABLE SStaff.SStaff
(
  StaffSID             INT           NOT NULL,
  StaffIEN             VARCHAR(50)   NOT NULL,
  Sta3n                SMALLINT      NOT NULL,
  StaffName            VARCHAR(100)  NULL,
  LastName             VARCHAR(50)   NULL,
  FirstName            VARCHAR(50)   NULL,
  MiddleName           VARCHAR(50)   NULL,
  StaffNamePrefix      VARCHAR(50)   NULL,
  StaffNameSuffix      VARCHAR(50)   NULL,  
  StaffSSN             VARCHAR(50)   NULL,
  NetworkUsername      VARCHAR(100)   NULL,
  DEA                  VARCHAR(50)   NULL,
  NPI                  VARCHAR(50)   NULL
);
GO

-- create indexes for the SPatient.Patient table
CREATE INDEX IX_StaffSID ON SStaff.SStaff (StaffSID);
CREATE INDEX IX_StaffIEN ON SStaff.SStaff (StaffIEN);
CREATE INDEX IX_Sta3n ON SStaff.SStaff (Sta3n);
GO
