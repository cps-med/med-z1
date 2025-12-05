-- ----------------------------------------------------------------------
-- Master SQL Script for Inserting rows into CDWWork Database Tables
-- ----------------------------------------------------------------------
-- Run this script from terminal within "insert" folder, using command:
-- sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -i _master.sql
-- or using shell script: _master.sh
-- ----------------------------------------------------------------------

-- Insert into dimension tables
:r Dim.Country.sql
:r Dim.Division.sql
:r Dim.PeriodOfService.sql
:r Dim.Sta3n.sql
:r Dim.State.sql
:r Dim.VistASite.sql
:r Dim.WardLocation.sql

-- Insert into inpatient tables
:r Inpat.Inpatient.sql
:r Inpat.PatientTransfer.sql
:r Inpat.ProvisionalMovement.sql

-- Insert into patient tables
:r SPatient.SPatient.sql
:r SPatient.SPatientAddress.sql
:r SPatient.SPatientDisability.sql
:r SPatient.SPatientInsurance.sql

-- Insert into staff tables
:r SStaff.RadiologyNuclearMedicineReport.sql
:r SStaff.SStaff.sql

-- Insert into pharmacy outpatient tables
:r RxOut.RxOutpat.sql
:r RxOut.RxOutpatFill.sql
:r RxOut.RxOutpatSig.sql
:r RxOut.RxOutpatMedInstructions.sql

-- Insert into BCMA (bar code medication administration) tables
:r BCMA.BCMAMedicationLog.sql
:r BCMA.BCMADispensedDrug.sql
:r BCMA.BCMAAdditive.sql
:r BCMA.BCMASolution.sql

-- Run scripts to add elderly and expansion patients
:r add_elderly_patients.sql
:r add_expansion_patients.sql
