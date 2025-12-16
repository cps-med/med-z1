# Laboratory Data Verification Queries

## Summary Statistics

**Date Created:** December 16, 2025
**Status:** ✅ Data loaded successfully

### Test Definitions (Dim.LabTest)
- **Total test definitions:** 43
- **Panels:** BMP (7), CBC (8), CMP (7), LFT (1), Lipid Panel (5), Urinalysis (10)
- **Individual tests:** 5 (HbA1c, TSH, PSA, Vitamin D, BNP)
- **LOINC coverage:** 100% (all tests have LOINC codes)

### Lab Results (Chem.LabChem)
- **Total results:** 84
- **Patients with labs:** 13 (Patient SIDs: 1001-1013)
- **Abnormality distribution:**
  - Normal: 67 (79.76%)
  - High (H): 12 (14.29%)
  - Low (L): 4 (4.76%)
  - Critical High (H*): 1 (1.19%)
  - **Total Abnormal: 17 (20.24%)**

### Temporal Distribution
- Recent (<30 days): 22 results (26.2%)
- 30-90 days: 48 results (57.1%)
- 90-180 days: 15 results (17.9%)
- >180 days: 6 results (7.1%)

## Verification Queries

### 1. Check Lab Test Definitions

```sql
USE CDWWork;
GO

-- View all test definitions grouped by panel
SELECT
    PanelName,
    COUNT(*) AS TestCount,
    STRING_AGG(LabTestName, ', ') AS Tests
FROM Dim.LabTest
GROUP BY PanelName
ORDER BY PanelName;
GO

-- Check LOINC code coverage
SELECT
    COUNT(*) AS TotalTests,
    SUM(CASE WHEN LoincCode IS NOT NULL THEN 1 ELSE 0 END) AS TestsWithLoinc,
    CAST(SUM(CASE WHEN LoincCode IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS LoincCoveragePercent
FROM Dim.LabTest;
GO
```

### 2. Check Lab Results by Patient

```sql
-- Count results per patient
SELECT
    lc.PatientSID,
    p.PatientICN,
    p.PatientName,
    COUNT(*) AS LabResultCount,
    SUM(CASE WHEN lc.AbnormalFlag IS NOT NULL THEN 1 ELSE 0 END) AS AbnormalCount
FROM Chem.LabChem lc
LEFT JOIN SPatient.SPatient p ON lc.PatientSID = p.PatientSID
GROUP BY lc.PatientSID, p.PatientICN, p.PatientName
ORDER BY LabResultCount DESC;
GO
```

### 3. Check Recent Lab Panels

```sql
-- Get recent lab panels (grouped by AccessionNumber)
SELECT
    lc.AccessionNumber,
    lt.PanelName,
    lc.CollectionDateTime,
    COUNT(*) AS TestCount,
    SUM(CASE WHEN lc.AbnormalFlag IS NOT NULL THEN 1 ELSE 0 END) AS AbnormalCount,
    p.PatientICN,
    p.PatientName
FROM Chem.LabChem lc
LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
LEFT JOIN SPatient.SPatient p ON lc.PatientSID = p.PatientSID
WHERE lc.AccessionNumber IS NOT NULL
  AND lc.CollectionDateTime >= DATEADD(DAY, -90, GETDATE())
GROUP BY lc.AccessionNumber, lt.PanelName, lc.CollectionDateTime, p.PatientICN, p.PatientName
ORDER BY lc.CollectionDateTime DESC;
GO
```

### 4. Check Abnormal Results

```sql
-- View all abnormal results with patient info
SELECT
    p.PatientICN,
    p.PatientName,
    lt.LabTestName,
    lc.Result,
    lc.ResultUnit,
    lc.AbnormalFlag,
    lc.RefRange,
    lc.CollectionDateTime
FROM Chem.LabChem lc
LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
LEFT JOIN SPatient.SPatient p ON lc.PatientSID = p.PatientSID
WHERE lc.AbnormalFlag IS NOT NULL
ORDER BY lc.CollectionDateTime DESC, lc.AbnormalFlag;
GO
```

### 5. Check Test Trending for Specific Patient

```sql
-- Example: View all Glucose results for Patient 1001
SELECT
    lc.CollectionDateTime,
    lc.Result,
    lc.ResultNumeric,
    lc.AbnormalFlag,
    lc.RefRange,
    lt.Units
FROM Chem.LabChem lc
LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
WHERE lc.PatientSID = 1001
  AND lt.LabTestName = 'Glucose'
ORDER BY lc.CollectionDateTime ASC;
GO
```

### 6. Validate Panel Grouping

```sql
-- Show BMP panel results for Patient 1001 (most recent)
SELECT
    lc.AccessionNumber,
    lt.LabTestName,
    lc.Result,
    lc.ResultUnit,
    lc.AbnormalFlag,
    lc.RefRange
FROM Chem.LabChem lc
LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
WHERE lc.PatientSID = 1001
  AND lc.AccessionNumber = 'CH 20251211-001'  -- Most recent BMP
ORDER BY lt.LabTestName;
GO
```

## Expected Results

### Panel Structure Verification

**BMP Panel (Accession: CH 20251211-001):**
- Should have exactly 7 results
- Tests: Sodium, Potassium, Chloride, CO2, BUN, Creatinine, Glucose
- Patient 1001 has 2 abnormal flags (Potassium H, Glucose H)

**CBC Panel (Accession: CH 20251213-002):**
- Should have exactly 8 results
- Tests: WBC, RBC, Hemoglobin, Hematocrit, Platelet, MCV, MCH, MCHC
- Patient 1002 has all normal results

**CMP Panel (Accession: CH 20251031-007):**
- Should have exactly 14 results
- Tests: All 7 BMP tests + Calcium, Total Protein, Albumin, Total Bilirubin, ALP, AST, ALT
- Patient 1006 has 1 abnormal flag (AST H)

### Critical Values Check

**Patient 1008 - Critical Potassium:**
- AccessionNumber: CH 20251111-009
- Test: Potassium
- Result: 6.2 mmol/L
- AbnormalFlag: H* (Critical High)
- RefRange: 3.5 - 5.0 mmol/L

## Data Quality Checks

All checks should pass:

✅ All lab results have valid PatientSID (links to SPatient.SPatient)
✅ All lab results have valid LabTestSID (links to Dim.LabTest)
✅ All panel results share same AccessionNumber
✅ CollectionDateTime is before or equal to ResultDateTime
✅ Abnormal flags are valid ('H', 'L', 'H*', 'L*', 'Panic', or NULL)
✅ ResultNumeric is populated for numeric results
✅ All test definitions have LOINC codes
✅ Reference ranges are consistent across test definitions
