-- =====================================================================
-- Diagnostic queries for medications display issue on Linux
-- =====================================================================
-- Purpose: Compare medications data between macOS (working) and Linux (not working)
-- Run this script on the Linux system to gather diagnostic information
-- =====================================================================

-- Query 1: Check current schema search path
\echo '==================================================================='
\echo 'Query 1: PostgreSQL schema search path'
\echo '==================================================================='
SHOW search_path;
\echo ''

-- Query 2: Verify medications tables exist in clinical schema
\echo '==================================================================='
\echo 'Query 2: Verify medications tables exist'
\echo '==================================================================='
SELECT schemaname, tablename
FROM pg_tables
WHERE tablename IN ('patient_medications_outpatient', 'patient_medications_inpatient')
ORDER BY schemaname, tablename;
\echo ''

-- Query 3: Count total rows in both medications tables
\echo '==================================================================='
\echo 'Query 3: Count rows in medications tables'
\echo '==================================================================='
SELECT
    'Outpatient' AS table_type,
    COUNT(*) AS row_count
FROM clinical.patient_medications_outpatient
UNION ALL
SELECT
    'Inpatient' AS table_type,
    COUNT(*) AS row_count
FROM clinical.patient_medications_inpatient;
\echo ''

-- Query 4: Check distinct patient ICNs in medications tables
\echo '==================================================================='
\echo 'Query 4: Distinct patient ICNs in medications'
\echo '==================================================================='
SELECT
    'Outpatient' AS table_type,
    COUNT(DISTINCT patient_icn) AS distinct_patients,
    COUNT(*) AS total_rows
FROM clinical.patient_medications_outpatient
UNION ALL
SELECT
    'Inpatient' AS table_type,
    COUNT(DISTINCT patient_icn) AS distinct_patients,
    COUNT(*) AS total_rows
FROM clinical.patient_medications_inpatient;
\echo ''

-- Query 5: Show sample ICNs from medications tables
\echo '==================================================================='
\echo 'Query 5: Sample ICNs from medications tables (first 10)'
\echo '==================================================================='
SELECT DISTINCT patient_icn
FROM (
    SELECT patient_icn FROM clinical.patient_medications_outpatient
    UNION
    SELECT patient_icn FROM clinical.patient_medications_inpatient
) AS all_meds
ORDER BY patient_icn
LIMIT 10;
\echo ''

-- Query 6: Compare ICNs in medications vs demographics
\echo '==================================================================='
\echo 'Query 6: ICN format comparison (medications vs demographics)'
\echo '==================================================================='
SELECT
    'Demographics' AS source,
    patient_key,
    LENGTH(patient_key) AS icn_length
FROM clinical.patient_demographics
WHERE patient_key LIKE 'ICN%'
ORDER BY patient_key
LIMIT 5;

SELECT
    'Medications (Outpatient)' AS source,
    patient_icn,
    LENGTH(patient_icn) AS icn_length
FROM clinical.patient_medications_outpatient
ORDER BY patient_icn
LIMIT 5;
\echo ''

-- Query 7: Check for medications for specific test patient (ICN100001)
\echo '==================================================================='
\echo 'Query 7: Medications for test patient ICN100001'
\echo '==================================================================='
SELECT
    'Outpatient' AS med_type,
    patient_icn,
    drug_name_local,
    issue_date,
    rx_status_computed
FROM clinical.patient_medications_outpatient
WHERE patient_icn = 'ICN100001'
ORDER BY issue_date DESC
LIMIT 3;

SELECT
    'Inpatient' AS med_type,
    patient_icn,
    drug_name_local,
    action_datetime,
    action_type
FROM clinical.patient_medications_inpatient
WHERE patient_icn = 'ICN100001'
ORDER BY action_datetime DESC
LIMIT 3;
\echo ''

-- Query 8: Check for case sensitivity issues with patient_icn column
\echo '==================================================================='
\echo 'Query 8: Column name case sensitivity check'
\echo '==================================================================='
SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_schema = 'clinical'
  AND table_name IN ('patient_medications_outpatient', 'patient_medications_inpatient')
  AND column_name ILIKE '%patient%icn%'
ORDER BY table_name, column_name;
\echo ''

-- Query 9: Check PostgreSQL version
\echo '==================================================================='
\echo 'Query 9: PostgreSQL version'
\echo '==================================================================='
SELECT version();
\echo ''

-- Query 10: Check for any NULL patient_icn values
\echo '==================================================================='
\echo 'Query 10: NULL patient_icn check'
\echo '==================================================================='
SELECT
    'Outpatient' AS table_type,
    COUNT(*) FILTER (WHERE patient_icn IS NULL) AS null_count,
    COUNT(*) FILTER (WHERE patient_icn IS NOT NULL) AS not_null_count
FROM clinical.patient_medications_outpatient
UNION ALL
SELECT
    'Inpatient' AS table_type,
    COUNT(*) FILTER (WHERE patient_icn IS NULL) AS null_count,
    COUNT(*) FILTER (WHERE patient_icn IS NOT NULL) AS not_null_count
FROM clinical.patient_medications_inpatient;
\echo ''

\echo '==================================================================='
\echo 'Diagnostic queries complete!'
\echo 'Please save this output and compare with macOS results.'
\echo '==================================================================='
