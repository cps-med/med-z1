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
PRINT 'STEP 5: Populating immunizations';
PRINT '=======================================================================';
PRINT '';

:r ImmunizationMill.VaccineCode.sql
:r ImmunizationMill.VaccineAdmin.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 6: Populating problems/diagnoses';
PRINT '=======================================================================';
PRINT '';

:r EncMill.ProblemList.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 7: Populating family history';
PRINT '=======================================================================';
PRINT '';

:r EncMill.FamilyHistory.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'STEP 8: Populating Thompson Siblings Test Patients (Simplified Schema)';
PRINT '=======================================================================';
PRINT '';
PRINT 'NOTE: Thompson siblings use simplified CDWWork2 schema for continuation care';
PRINT '      at Walla Walla VAMC (FacilityCode 687) during 2025-2026.';
PRINT '      These patients demonstrate cross-system harmonization (VistA + Cerner).';
PRINT '';

:r Thompson-Bailey.sql
:r Thompson-Alananah.sql
:r Thompson-Joe.sql

PRINT '';
PRINT '=======================================================================';
PRINT 'CDWWork2 Data Population Complete!';
PRINT '=======================================================================';
PRINT '';
PRINT 'Summary:';
PRINT '  - Code Sets: VITAL_TYPE, UNIT, ALLERGEN, REACTION, SEVERITY,';
PRINT '               FAMILY_RELATIONSHIP, FAMILY_HISTORY_CONDITION, FAMILY_HISTORY_STATUS (77 codes)';
PRINT '  - Patients: 5 total';
PRINT '    * 2 Cerner demo patients (Adam Dooree, Alexander Aminor)';
PRINT '    * 3 Thompson siblings (Bailey, Alananah, Joe) - Cross-system test patients';
PRINT '  - Encounters: 16 total (8 per demo patient)';
PRINT '  - Vitals: 22 total (12 for Adam, 10 for Alexander)';
PRINT '  - Vaccine Codes: 15 total (COVID, Flu, Tdap, Shingrix, Hep A/B, HPV, pediatric)';
PRINT '  - Immunizations: 40 total (17 for Adam, 23 for Alexander)';
PRINT '  - Family History: 13 total (3 for Adam, 4 for Alexander, 6 for Thompson siblings)';
PRINT '';
GO
