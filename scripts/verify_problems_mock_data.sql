-- Verification Script: Problems/Diagnoses Mock Data
-- Purpose: Verify all Problems/Diagnoses tables and data are properly created
-- Usage: Run after executing CDWWork and CDWWork2 master CREATE and INSERT scripts
--
-- Run from terminal:
-- sqlcmd -S 127.0.0.1,1433 -U sa -P MyS3cur3P@ssw0rd -C -i verify_problems_mock_data.sql

SET NOCOUNT ON;
GO

PRINT '';
PRINT '=======================================================================';
PRINT 'VERIFICATION: Problems/Diagnoses Mock Data';
PRINT '=======================================================================';
PRINT '';

-- =======================================================================
-- CDWWork (VistA) Verification
-- =======================================================================

PRINT '-----------------------------------------------------------------------';
PRINT 'CDWWork (VistA) - Dimension Tables';
PRINT '-----------------------------------------------------------------------';
PRINT '';

USE CDWWork;
GO

-- 1. Verify Dim.ICD10
PRINT '1. Dim.ICD10 (ICD-10-CM Codes)';
SELECT
    COUNT(*) as TotalCodes,
    COUNT(DISTINCT ICD10Category) as CategoryCount,
    SUM(CASE WHEN IsChronicCondition = 'Y' THEN 1 ELSE 0 END) as ChronicCodes,
    SUM(CASE WHEN CharlsonCondition IS NOT NULL THEN 1 ELSE 0 END) as CharlsonMappedCodes
FROM Dim.ICD10;

SELECT TOP 5 ICD10Code, ICD10Description, ICD10Category, CharlsonCondition
FROM Dim.ICD10
ORDER BY ICD10Category, ICD10Code;
PRINT '';

-- 2. Verify Dim.CharlsonMapping
PRINT '2. Dim.CharlsonMapping (Charlson Comorbidity Index)';
SELECT
    COUNT(*) as TotalMappings,
    COUNT(DISTINCT CharlsonCondition) as ConditionCount,
    COUNT(DISTINCT ICD10Code) as UniqueICD10Codes
FROM Dim.CharlsonMapping;

SELECT CharlsonCondition, CharlsonWeight, COUNT(*) as ICD10Count
FROM Dim.CharlsonMapping
GROUP BY CharlsonCondition, CharlsonWeight
ORDER BY CharlsonWeight DESC, CharlsonCondition;
PRINT '';

PRINT '-----------------------------------------------------------------------';
PRINT 'CDWWork (VistA) - Problem List Data';
PRINT '-----------------------------------------------------------------------';
PRINT '';

-- 3. Verify Outpat.ProblemList
PRINT '3. Outpat.ProblemList (VistA Problem List)';
SELECT
    COUNT(*) as TotalProblems,
    COUNT(DISTINCT PatientICN) as PatientCount,
    SUM(CASE WHEN ProblemStatus = 'ACTIVE' THEN 1 ELSE 0 END) as ActiveProblems,
    SUM(CASE WHEN ProblemStatus = 'INACTIVE' THEN 1 ELSE 0 END) as InactiveProblems,
    SUM(CASE WHEN ProblemStatus = 'RESOLVED' THEN 1 ELSE 0 END) as ResolvedProblems,
    SUM(CASE WHEN IsChronicCondition = 'Y' THEN 1 ELSE 0 END) as ChronicProblems,
    SUM(CASE WHEN IsServiceConnected = 'Y' THEN 1 ELSE 0 END) as ServiceConnectedProblems
FROM Outpat.ProblemList;
PRINT '';

-- Problems by patient (top 10)
PRINT 'Problems by Patient (Top 10):';
SELECT TOP 10
    PatientICN,
    COUNT(*) as TotalProblems,
    SUM(CASE WHEN ProblemStatus = 'ACTIVE' THEN 1 ELSE 0 END) as Active,
    SUM(CASE WHEN IsChronicCondition = 'Y' THEN 1 ELSE 0 END) as Chronic
FROM Outpat.ProblemList
GROUP BY PatientICN
ORDER BY TotalProblems DESC;
PRINT '';

-- Charlson conditions represented
PRINT 'Charlson Conditions in Problem List:';
SELECT
    c.CharlsonCondition,
    c.CharlsonWeight,
    COUNT(DISTINCT pl.PatientICN) as PatientCount,
    COUNT(*) as ProblemCount
FROM Outpat.ProblemList pl
INNER JOIN Dim.CharlsonMapping c ON pl.ICD10Code = c.ICD10Code
WHERE pl.ProblemStatus = 'ACTIVE'
GROUP BY c.CharlsonCondition, c.CharlsonWeight
ORDER BY c.CharlsonWeight DESC, PatientCount DESC;
PRINT '';

-- =======================================================================
-- CDWWork2 (Cerner) Verification
-- =======================================================================

PRINT '-----------------------------------------------------------------------';
PRINT 'CDWWork2 (Cerner) - Problem List Data';
PRINT '-----------------------------------------------------------------------';
PRINT '';

USE CDWWork2;
GO

-- 4. Verify EncMill.ProblemList
PRINT '4. EncMill.ProblemList (Cerner Problem List)';
SELECT
    COUNT(*) as TotalProblems,
    COUNT(DISTINCT PatientICN) as PatientCount,
    SUM(CASE WHEN StatusCode = 'A' THEN 1 ELSE 0 END) as ActiveProblems,
    SUM(CASE WHEN StatusCode = 'I' THEN 1 ELSE 0 END) as InactiveProblems,
    SUM(CASE WHEN StatusCode = 'R' THEN 1 ELSE 0 END) as ResolvedProblems,
    SUM(CASE WHEN ChronicFlag = 'Y' THEN 1 ELSE 0 END) as ChronicProblems,
    SUM(CASE WHEN ServiceConnectedFlag = 'Y' THEN 1 ELSE 0 END) as ServiceConnectedProblems
FROM EncMill.ProblemList;
PRINT '';

-- Problems by patient
PRINT 'Problems by Patient (Cerner):';
SELECT
    PatientICN,
    COUNT(*) as TotalProblems,
    SUM(CASE WHEN StatusCode = 'A' THEN 1 ELSE 0 END) as Active,
    SUM(CASE WHEN ChronicFlag = 'Y' THEN 1 ELSE 0 END) as Chronic
FROM EncMill.ProblemList
GROUP BY PatientICN
ORDER BY TotalProblems DESC;
PRINT '';

-- =======================================================================
-- Cross-Database Analysis
-- =======================================================================

PRINT '-----------------------------------------------------------------------';
PRINT 'Cross-Database Summary';
PRINT '-----------------------------------------------------------------------';
PRINT '';

-- Create temp table to store counts (persists across USE statements)
CREATE TABLE #CrossDBCounts (
    DatabaseName VARCHAR(50),
    ProblemCount INT,
    PatientCount INT
);

-- Get CDWWork counts
USE CDWWork;
INSERT INTO #CrossDBCounts (DatabaseName, ProblemCount, PatientCount)
SELECT 'CDWWork', COUNT(*), COUNT(DISTINCT PatientICN)
FROM Outpat.ProblemList;

-- Get CDWWork2 counts
USE CDWWork2;
INSERT INTO #CrossDBCounts (DatabaseName, ProblemCount, PatientCount)
SELECT 'CDWWork2', COUNT(*), COUNT(DISTINCT PatientICN)
FROM EncMill.ProblemList;

-- Display summary
SELECT
    SUM(CASE WHEN DatabaseName = 'CDWWork' THEN ProblemCount ELSE 0 END) as CDWWork_Problems,
    SUM(CASE WHEN DatabaseName = 'CDWWork' THEN PatientCount ELSE 0 END) as CDWWork_Patients,
    SUM(CASE WHEN DatabaseName = 'CDWWork2' THEN ProblemCount ELSE 0 END) as CDWWork2_Problems,
    SUM(CASE WHEN DatabaseName = 'CDWWork2' THEN PatientCount ELSE 0 END) as CDWWork2_Patients,
    SUM(ProblemCount) as Total_Problems,
    SUM(PatientCount) as Total_Patients
FROM #CrossDBCounts;

-- Cleanup
DROP TABLE #CrossDBCounts;

PRINT '';

-- =======================================================================
-- Sample Data Preview
-- =======================================================================

USE CDWWork;

PRINT '-----------------------------------------------------------------------';
PRINT 'Sample Data: Patient ICN100001 (Adam Dooree) - High Complexity';
PRINT '-----------------------------------------------------------------------';
PRINT '';

SELECT TOP 5
    ProblemNumber,
    ICD10Code,
    ICD10Description,
    ProblemStatus,
    OnsetDate,
    IsChronicCondition,
    IsServiceConnected
FROM Outpat.ProblemList
WHERE PatientICN = 'ICN100001'
ORDER BY
    CASE ProblemStatus
        WHEN 'ACTIVE' THEN 1
        WHEN 'INACTIVE' THEN 2
        WHEN 'RESOLVED' THEN 3
    END,
    OnsetDate DESC;
PRINT '';

-- =======================================================================
-- Schema Difference Notes
-- =======================================================================

PRINT '-----------------------------------------------------------------------';
PRINT 'Schema Harmonization Notes (Silver Layer ETL will address)';
PRINT '-----------------------------------------------------------------------';
PRINT '';
PRINT 'Key Differences Between VistA and Cerner:';
PRINT '  - Primary Key: ProblemSID (VistA) vs DiagnosisSID (Cerner)';
PRINT '  - Status Field: ProblemStatus = ACTIVE/INACTIVE/RESOLVED (VistA) vs StatusCode = A/I/R (Cerner)';
PRINT '  - ICD-10 Field: ICD10Code (VistA) vs DiagnosisCode (Cerner)';
PRINT '  - SNOMED Field: SNOMEDCode (VistA) vs ClinicalTermCode (Cerner)';
PRINT '  - Date Type: DATE (VistA) vs DATETIME (Cerner)';
PRINT '  - Patient FK: PatientSID (VistA) vs PatientKey (Cerner)';
PRINT '';

PRINT '=======================================================================';
PRINT 'Verification Complete!';
PRINT '=======================================================================';
PRINT '';
PRINT 'Next Steps:';
PRINT '  1. Review counts and sample data above';
PRINT '  2. If all looks correct, proceed with ETL pipeline creation';
PRINT '  3. Bronze ETL will extract from both databases';
PRINT '  4. Silver ETL will harmonize schema differences';
PRINT '  5. Gold ETL will calculate Charlson Index and aggregate metrics';
PRINT '';
GO
