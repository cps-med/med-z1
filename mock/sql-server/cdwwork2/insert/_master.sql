-------------------------------------------------------------------------
-- Master SQL Script for Populating CDWWork2 Database
-- Oracle Health (Cerner Millennium) Demo Data
-------------------------------------------------------------------------
-- Run this script from terminal within "insert" folder, using command:
-- sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -C -i _master.sql
--
-- Phase 1 Demo Data:
-- - Code value system (vitals, allergies, units, reactions, severity)
-- - 2 demo patients (Adam Dooree, Alexander Aminor)
-- - 8 encounters per patient at Cerner sites (Portland 648, Seattle 663)
-- - Vitals and Allergies data to be populated in Phases 2-3
-------------------------------------------------------------------------

PRINT '';
PRINT '=======================================================================';
PRINT 'CDWWork2 Data Population - Phase 1 Foundation';
PRINT 'Oracle Health (Cerner Millennium) Demo Data';
PRINT '=======================================================================';
PRINT '';

-- =======================================================================
-- STEP 1: Code Value System (Foundation for all clinical data)
-- =======================================================================

PRINT 'STEP 1: Populating code value system...';
PRINT '';

:r NDimMill.CodeValue.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 2: Populating patient demographics';
PRINT '=======================================================================';
PRINT '';

:r VeteranMill.SPerson.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 3: Populating encounters';
PRINT '=======================================================================';
PRINT '';

:r EncMill.Encounter.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 4: Populating vital signs';
PRINT '=======================================================================';
PRINT '';

:r VitalMill.VitalResult.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'CDWWork2 Data Population Complete!';
PRINT '=======================================================================';
PRINT '';
PRINT 'Summary:';
PRINT '  - Code Sets: VITAL_TYPE, UNIT, ALLERGEN, REACTION, SEVERITY (48 codes)';
PRINT '  - Patients: 2 (Adam Dooree at Portland, Alexander Aminor at Seattle)';
PRINT '  - Encounters: 16 total (8 per patient)';
PRINT '  - Vitals: 22 total (12 for Adam, 10 for Alexander)';
PRINT '';
PRINT 'Next Steps:';
PRINT '  - Phase 2: Implement Bronze/Silver/Gold ETL for vitals';
PRINT '  - Phase 3 (Days 6-8): Populate AllergyMill tables with allergy data';
PRINT '  - Test: View vitals in med-z1 UI with source badges';
PRINT '';
PRINT 'Demo Patients:';
PRINT '  - Adam Dooree (ICN100001): CDWWork PatientSID 1001 → CDWWork2 PersonSID 2001';
PRINT '    VistA vitals (20+ at Atlanta 508) + Cerner vitals (12 at Portland 648)';
PRINT '  - Alexander Aminor (ICN100010): CDWWork PatientSID 1010 → CDWWork2 PersonSID 2010';
PRINT '    VistA vitals (multiple at Dayton 552) + Cerner vitals (10 at Seattle 663)';
PRINT '';
GO
