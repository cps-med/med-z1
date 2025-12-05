---------------------------------------------------------------
-- Create: SStaff.RadiologyNuclearMedicineReport.sql
-- VA Staff, including providers.
---------------------------------------------------------------

-- set the active database
USE CDWWork;
GO

-- create RadiologyNuclearMedicineReport table in the SStaff schema
CREATE TABLE SStaff.RadiologyNuclearMedicineReport
(
  RadiologyNuclearMedicineReportSID     BIGINT          NOT NULL,
  RadiologyNuclearMedicineReportIEN     VARCHAR(50)     NOT NULL,
  Sta3n                                 SMALLINT        NOT NULL,
  DayCase                               VARCHAR(50)     NULL,
  PatientSID                            INT             NULL,
  ExamDateTime                          DATETIME2(0)    NULL,
  CaseNumber                            DECIMAL(9,4)    NULL,
  ReportStatus                          VARCHAR(50)     NULL,
  RadiologyLocationSID                  INT             NULL
);
GO

-- create indexes for the SPatient.Patient table
CREATE INDEX IX_RadiologyNuclearMedicineReportSID ON SStaff.RadiologyNuclearMedicineReport (RadiologyNuclearMedicineReportSID);
CREATE INDEX IX_RadiologyNuclearMedicineReportIEN ON SStaff.RadiologyNuclearMedicineReport (RadiologyNuclearMedicineReportIEN);
CREATE INDEX IX_Sta3n ON SStaff.RadiologyNuclearMedicineReport (Sta3n);
GO
