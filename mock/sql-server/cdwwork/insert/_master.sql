-- ----------------------------------------------------------------------
-- Master SQL Script for Inserting rows into CDWWork Database Tables
-- ----------------------------------------------------------------------
-- Run this script from terminal within "insert" folder, using command:
-- sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -C -i _master.sql
-- or using shell script: _master.sh
-- ----------------------------------------------------------------------

-- =======================================================================
-- DIMENSION TABLES (must be inserted before fact tables)
-- =======================================================================

-- Geographic and administrative dimensions
:r Dim.Country.sql
:r Dim.Division.sql
:r Dim.Location.sql
:r Dim.PeriodOfService.sql
:r Dim.Sta3n.sql
:r Dim.State.sql
:r Dim.VistASite.sql
:r Dim.WardLocation.sql

-- Allergy dimensions
:r Dim.Allergen.sql
:r Dim.AllergySeverity.sql
:r Dim.Reaction.sql

-- Insurance dimensions
:r Dim.InsuranceCompany.sql

-- Medication/drug dimensions
:r Dim.LocalDrug.sql
:r Dim.NationalDrug.sql

-- Patient flag dimensions
:r Dim.PatientRecordFlag.sql

-- Vital signs dimensions
:r Dim.VitalType.sql
:r Dim.VitalQualifier.sql

-- Laboratory dimensions
:r Dim.LabTest.sql

-- Clinical notes dimensions
:r Dim.TIUDocumentDefinition.sql

-- Immunization dimensions
:r Dim.Vaccine.sql

-- =======================================================================
-- PATIENT TABLES
-- =======================================================================

:r SPatient.SPatient.sql
:r SPatient.SPatientAddress.sql
:r SPatient.SPatientPhone.sql
:r SPatient.SPatientDisability.sql
:r SPatient.SPatientInsurance.sql
:r SPatient.PatientRecordFlagAssignment.sql
:r SPatient.PatientRecordFlagHistory.sql

-- =======================================================================
-- STAFF TABLES
-- =======================================================================

:r SStaff.RadiologyNuclearMedicineReport.sql
:r SStaff.SStaff.sql

-- =======================================================================
-- CLINICAL DOMAIN TABLES
-- =======================================================================

-- Inpatient encounters
:r Inpat.Inpatient.sql
:r Inpat.PatientTransfer.sql
:r Inpat.ProvisionalMovement.sql

-- Outpatient pharmacy (RxOut)
:r RxOut.RxOutpat.sql
:r RxOut.RxOutpatFill.sql
:r RxOut.RxOutpatSig.sql
:r RxOut.RxOutpatMedInstructions.sql

-- Bar code medication administration (BCMA)
:r BCMA.BCMAMedicationLog.sql
:r BCMA.BCMADispensedDrug.sql
:r BCMA.BCMAAdditive.sql
:r BCMA.BCMASolution.sql

-- Allergies
:r Allergy.PatientAllergy.sql
:r Allergy.PatientAllergyReaction.sql

-- Vital signs
:r Vital.VitalSign.sql
:r Vital.VitalSignQualifier.sql

-- Laboratory results
:r Chem.LabChem.sql

-- Clinical Notes (TIU - Text Integration Utilities)
:r TIU.TIUDocument_8925.sql
:r TIU.TIUDocumentText.sql

-- Immunizations
:r Immunization.PatientImmunization.sql

