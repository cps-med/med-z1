-- =============================================================================
-- Dim.LabTest - Laboratory Test Definitions (INSERT)
-- =============================================================================
-- Purpose: Populate laboratory test dimension with 57 test definitions
-- Includes: BMP (7), CBC (8), CMP (14), LFT (6), Lipid (5), Individual (5), Urinalysis (10)
-- All tests include LOINC codes for interoperability
-- =============================================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting laboratory test definitions into Dim.LabTest...';
GO

-- =============================================================================
-- Basic Metabolic Panel (BMP) - 7 Tests
-- =============================================================================

INSERT INTO [Dim].[LabTest] ([LabTestName], [LabTestCode], [LoincCode], [IsPanel], [PanelName], [Units], [RefRangeLow], [RefRangeHigh], [RefRangeText], [VistaPackage])
VALUES
('Sodium', 'NA', '2951-2', 0, 'BMP', 'mmol/L', '135', '145', '135 - 145 mmol/L', 'CH'),
('Potassium', 'K', '2823-3', 0, 'BMP', 'mmol/L', '3.5', '5.0', '3.5 - 5.0 mmol/L', 'CH'),
('Chloride', 'CL', '2075-0', 0, 'BMP', 'mmol/L', '98', '107', '98 - 107 mmol/L', 'CH'),
('Carbon Dioxide', 'CO2', '2028-9', 0, 'BMP', 'mmol/L', '22', '29', '22 - 29 mmol/L', 'CH'),
('Blood Urea Nitrogen', 'BUN', '3094-0', 0, 'BMP', 'mg/dL', '7', '20', '7 - 20 mg/dL', 'CH'),
('Creatinine', 'CREAT', '2160-0', 0, 'BMP', 'mg/dL', '0.7', '1.3', '0.7 - 1.3 mg/dL', 'CH'),
('Glucose', 'GLU', '2345-7', 0, 'BMP', 'mg/dL', '70', '100', '70 - 100 mg/dL', 'CH');
GO

-- =============================================================================
-- Complete Blood Count (CBC) - 8 Tests
-- =============================================================================

INSERT INTO [Dim].[LabTest] ([LabTestName], [LabTestCode], [LoincCode], [IsPanel], [PanelName], [Units], [RefRangeLow], [RefRangeHigh], [RefRangeText], [VistaPackage])
VALUES
('White Blood Cell Count', 'WBC', '6690-2', 0, 'CBC', 'K/uL', '4.5', '11.0', '4.5 - 11.0 K/uL', 'CH'),
('Red Blood Cell Count', 'RBC', '789-8', 0, 'CBC', 'M/uL', '4.5', '5.9', '4.5 - 5.9 M/uL', 'CH'),
('Hemoglobin', 'HGB', '718-7', 0, 'CBC', 'g/dL', '13.5', '17.5', '13.5 - 17.5 g/dL', 'CH'),
('Hematocrit', 'HCT', '4544-3', 0, 'CBC', '%', '40', '52', '40 - 52 %', 'CH'),
('Platelet Count', 'PLT', '777-3', 0, 'CBC', 'K/uL', '150', '400', '150 - 400 K/uL', 'CH'),
('Mean Corpuscular Volume', 'MCV', '787-2', 0, 'CBC', 'fL', '80', '100', '80 - 100 fL', 'CH'),
('Mean Corpuscular Hemoglobin', 'MCH', '785-6', 0, 'CBC', 'pg', '27', '33', '27 - 33 pg', 'CH'),
('Mean Corpuscular Hemoglobin Concentration', 'MCHC', '786-4', 0, 'CBC', 'g/dL', '32', '36', '32 - 36 g/dL', 'CH');
GO

-- =============================================================================
-- Comprehensive Metabolic Panel (CMP) - 14 Tests
-- (Includes all 7 BMP tests + 7 additional tests)
-- =============================================================================

INSERT INTO [Dim].[LabTest] ([LabTestName], [LabTestCode], [LoincCode], [IsPanel], [PanelName], [Units], [RefRangeLow], [RefRangeHigh], [RefRangeText], [VistaPackage])
VALUES
-- CMP-specific tests (BMP tests already inserted above, will reference same tests)
('Calcium', 'CA', '17861-6', 0, 'CMP', 'mg/dL', '8.5', '10.5', '8.5 - 10.5 mg/dL', 'CH'),
('Total Protein', 'TP', '2885-2', 0, 'CMP', 'g/dL', '6.0', '8.3', '6.0 - 8.3 g/dL', 'CH'),
('Albumin', 'ALB', '1751-7', 0, 'CMP', 'g/dL', '3.5', '5.5', '3.5 - 5.5 g/dL', 'CH'),
('Total Bilirubin', 'TBIL', '1975-2', 0, 'CMP', 'mg/dL', '0.1', '1.2', '0.1 - 1.2 mg/dL', 'CH'),
('Alkaline Phosphatase', 'ALP', '6768-6', 0, 'CMP', 'U/L', '30', '120', '30 - 120 U/L', 'CH'),
('Aspartate Aminotransferase', 'AST', '1920-8', 0, 'CMP', 'U/L', '10', '40', '10 - 40 U/L', 'CH'),
('Alanine Aminotransferase', 'ALT', '1742-6', 0, 'CMP', 'U/L', '7', '56', '7 - 56 U/L', 'CH');
GO

-- =============================================================================
-- Liver Function Tests (LFT) - 6 Tests
-- (Some overlap with CMP)
-- =============================================================================

INSERT INTO [Dim].[LabTest] ([LabTestName], [LabTestCode], [LoincCode], [IsPanel], [PanelName], [Units], [RefRangeLow], [RefRangeHigh], [RefRangeText], [VistaPackage])
VALUES
('Direct Bilirubin', 'DBIL', '1968-7', 0, 'LFT', 'mg/dL', '0.0', '0.3', '0.0 - 0.3 mg/dL', 'CH');
-- Note: Total Bilirubin, ALP, AST, ALT, Total Protein already defined for CMP
-- LFT will reference those same tests
GO

-- =============================================================================
-- Lipid Panel - 5 Tests
-- =============================================================================

INSERT INTO [Dim].[LabTest] ([LabTestName], [LabTestCode], [LoincCode], [IsPanel], [PanelName], [Units], [RefRangeLow], [RefRangeHigh], [RefRangeText], [VistaPackage])
VALUES
('Total Cholesterol', 'CHOL', '2093-3', 0, 'Lipid Panel', 'mg/dL', '0', '200', '0 - 200 mg/dL', 'CH'),
('LDL Cholesterol', 'LDL', '18262-6', 0, 'Lipid Panel', 'mg/dL', '0', '100', '0 - 100 mg/dL', 'CH'),
('HDL Cholesterol', 'HDL', '2085-9', 0, 'Lipid Panel', 'mg/dL', '40', '60', '40 - 60 mg/dL', 'CH'),
('Triglycerides', 'TRIG', '2571-8', 0, 'Lipid Panel', 'mg/dL', '0', '150', '0 - 150 mg/dL', 'CH'),
('VLDL Cholesterol', 'VLDL', '13457-7', 0, 'Lipid Panel', 'mg/dL', '5', '40', '5 - 40 mg/dL', 'CH');
GO

-- =============================================================================
-- Individual Tests (Not Part of Panels) - 5 Tests
-- =============================================================================

INSERT INTO [Dim].[LabTest] ([LabTestName], [LabTestCode], [LoincCode], [IsPanel], [PanelName], [Units], [RefRangeLow], [RefRangeHigh], [RefRangeText], [VistaPackage])
VALUES
('Hemoglobin A1c', 'HBA1C', '4548-4', 0, NULL, '%', '4.0', '5.6', '4.0 - 5.6 %', 'CH'),
('Thyroid Stimulating Hormone', 'TSH', '3016-3', 0, NULL, 'mIU/L', '0.4', '4.0', '0.4 - 4.0 mIU/L', 'CH'),
('Prostate Specific Antigen', 'PSA', '2857-1', 0, NULL, 'ng/mL', '0.0', '4.0', '0.0 - 4.0 ng/mL', 'CH'),
('Vitamin D, 25-Hydroxy', 'VITD', '1989-3', 0, NULL, 'ng/mL', '30', '100', '30 - 100 ng/mL', 'CH'),
('B-Type Natriuretic Peptide', 'BNP', '30934-4', 0, NULL, 'pg/mL', '0', '100', '0 - 100 pg/mL', 'CH');
GO

-- =============================================================================
-- Urinalysis - 10 Tests
-- =============================================================================

INSERT INTO [Dim].[LabTest] ([LabTestName], [LabTestCode], [LoincCode], [IsPanel], [PanelName], [Units], [RefRangeLow], [RefRangeHigh], [RefRangeText], [VistaPackage])
VALUES
('Urine Color', 'UCOLOR', '5778-6', 0, 'Urinalysis', NULL, NULL, NULL, 'Yellow', 'CH'),
('Urine Clarity', 'UCLARITY', '5767-9', 0, 'Urinalysis', NULL, NULL, NULL, 'Clear', 'CH'),
('Urine Specific Gravity', 'USG', '5811-5', 0, 'Urinalysis', NULL, '1.005', '1.030', '1.005 - 1.030', 'CH'),
('Urine pH', 'UPH', '5803-2', 0, 'Urinalysis', NULL, '4.5', '8.0', '4.5 - 8.0', 'CH'),
('Urine Protein', 'UPROT', '5804-0', 0, 'Urinalysis', NULL, NULL, NULL, 'Negative', 'CH'),
('Urine Glucose', 'UGLU', '5792-7', 0, 'Urinalysis', NULL, NULL, NULL, 'Negative', 'CH'),
('Urine Ketones', 'UKET', '5797-6', 0, 'Urinalysis', NULL, NULL, NULL, 'Negative', 'CH'),
('Urine Blood', 'UBLOOD', '5794-3', 0, 'Urinalysis', NULL, NULL, NULL, 'Negative', 'CH'),
('Urine Leukocyte Esterase', 'ULE', '5799-2', 0, 'Urinalysis', NULL, NULL, NULL, 'Negative', 'CH'),
('Urine Nitrite', 'UNIT', '5802-4', 0, 'Urinalysis', NULL, NULL, NULL, 'Negative', 'CH');
GO

PRINT 'Laboratory test definitions inserted successfully.';
GO

-- Verify insert counts
PRINT 'Verification:';
SELECT
    PanelName,
    COUNT(*) AS TestCount
FROM Dim.LabTest
GROUP BY PanelName
ORDER BY PanelName;
GO

SELECT COUNT(*) AS TotalTestDefinitions FROM Dim.LabTest;
GO

PRINT 'Dim.LabTest data load complete.';
GO
