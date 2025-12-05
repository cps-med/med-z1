-------------------------------------------------------------------------
-- Master SQL Script for Creating CDWWork Database
-------------------------------------------------------------------------
-- Run this script from terminal within "create" folder, using command:
-- sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -i _master.sql
-- or using shell script: _master.sh
-------------------------------------------------------------------------

-- Drop and create database
:r db_database.sql

-- Create required schemas
:r db_schemas.sql

-- Create dimension tables
:r Dim.Country.sql
:r Dim.Division.sql
:r Dim.PeriodOfService.sql
:r Dim.Sta3n.sql
:r Dim.State.sql
:r Dim.VistASite.sql
:r Dim.WardLocation.sql

-- Create inpatient tables
:r Inpat.Inpatient.sql
:r Inpat.PatientTransfer.sql
:r Inpat.ProvisionalMovement.sql

-- Create patient tables
:r SPatient.SPatient.sql
:r SPatient.SPatientAddress.sql
:r SPatient.SPatientDisability.sql
:r SPatient.SPatientInsurance.sql

-- Create staff tables
:r SStaff.RadiologyNuclearMedicineReport.sql
:r SStaff.SStaff.sql

-- Create pharmacy outpatient tables
:r RxOut.RxOutpat.sql
:r RxOut.RxOutpatFill.sql
:r RxOut.RxOutpatSig.sql
:r RxOut.RxOutpatMedInstructions.sql

-- Create BCMA (bar code medication administration) tables
:r BCMA.BCMAMedicationLog.sql
:r BCMA.BCMADispensedDrug.sql
:r BCMA.BCMAAdditive.sql
:r BCMA.BCMASolution.sql
