-- Insert data: ImmunizationMill.VaccineAdmin
-- Purpose: Seed Cerner immunization administration records for 2 test patients
-- Test Scenario: Cross-system patient overlap with CDWWork
-- Total: ~40 records
--
-- IMPORTANT NOTES:
-- 1. PersonSID 2001 (ICN100001) - overlaps with CDWWork PatientSID 1001
-- 2. PersonSID 2010 (ICN100010) - overlaps with CDWWork PatientSID 1010
-- 3. PatientICN denormalized for cross-system joins in Silver ETL
-- 4. Series stored as SeriesNumber + TotalInSeries (Cerner pattern)
-- 5. DoseAmount + DoseUnit separated (vs VistA combined)
-- 6. VaccineCodeSID references will resolve once VaccineCode data is loaded

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting immunization administration records for 2 test patients...';
GO

-- Helper: VaccineCodeSID values will auto-increment starting at 1
-- CodeValue mapping:
--   1 = COVID Pfizer (CVX 208)
--   2 = COVID Moderna (CVX 213)
--   3 = Flu generic (CVX 088)
--   4 = Flu HD (CVX 135)
--   5 = Flu injectable (CVX 141)
--   6 = Tdap (CVX 115)
--   7 = Td (CVX 113)
--   8 = Shingrix (CVX 187)
--   9 = PPSV23 (CVX 033)
--  10 = Hep B adult (CVX 043)
--  11 = Hep A adult (CVX 052)
--  12 = HPV (CVX 062)
--  13 = Hep B peds (CVX 008)
--  14 = DTaP (CVX 020)
--  15 = IPV (CVX 010)

-- =============================================================================
-- PATIENT 2001 (ICN100001, Adam Dooree, Age 67)
-- Scenario: Portland VAMC (Cerner) recent care, overlaps with Atlanta VAMC (VistA)
-- Records: ~20 vaccines (recent adult vaccines from 2020-2024)
-- =============================================================================

INSERT INTO ImmunizationMill.VaccineAdmin
(PersonSID, PatientICN, VaccineCodeSID, AdministeredDateTime, SeriesNumber, TotalInSeries, DoseAmount, DoseUnit, RouteCode, BodySite, AdverseReaction, IsActive)
VALUES
-- COVID-19 series (Pfizer) - 2021 primary series
(2001, 'ICN100001', 1, '2021-03-20 10:00:00', '1', '2', '0.3', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2001, 'ICN100001', 1, '2021-04-17 10:30:00', '2', '2', '0.3', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),

-- COVID-19 boosters
(2001, 'ICN100001', 1, '2022-01-15 11:00:00', 'BOOSTER 1', NULL, '0.3', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),
(2001, 'ICN100001', 1, '2023-04-10 11:30:00', 'BOOSTER 2', NULL, '0.3', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),

-- Annual influenza vaccines (high dose for 65+)
(2001, 'ICN100001', 4, '2021-10-15 14:00:00', 'ANNUAL 2021', NULL, '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2001, 'ICN100001', 4, '2022-10-12 14:30:00', 'ANNUAL 2022', NULL, '0.5', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),
(2001, 'ICN100001', 4, '2023-10-10 13:45:00', 'ANNUAL 2023', NULL, '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2001, 'ICN100001', 4, '2024-10-08 14:15:00', 'ANNUAL 2024', NULL, '0.5', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),

-- Shingrix series (complete)
(2001, 'ICN100001', 8, '2021-09-15 10:00:00', '1', '2', '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2001, 'ICN100001', 8, '2022-01-20 10:30:00', '2', '2', '0.5', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),

-- Pneumococcal
(2001, 'ICN100001', 9, '2020-08-15 09:00:00', 'SINGLE', NULL, '0.65', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),

-- Tdap booster
(2001, 'ICN100001', 6, '2020-06-10 14:30:00', 'BOOSTER', NULL, '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),

-- Hepatitis A (travel-related, recent)
(2001, 'ICN100001', 11, '2023-05-15 11:00:00', '1', '2', '1.0', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2001, 'ICN100001', 11, '2023-11-20 11:30:00', '2', '2', '1.0', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),

-- Hepatitis B (catch-up series, 2022-2023)
(2001, 'ICN100001', 10, '2022-06-10 14:00:00', '1', '3', '1.0', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2001, 'ICN100001', 10, '2022-08-15 14:30:00', '2', '3', '1.0', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),
(2001, 'ICN100001', 10, '2023-02-20 15:00:00', '3', '3', '1.0', 'ML', 'IM', 'LEFT DELTOID', NULL, 1);
GO

-- =============================================================================
-- PATIENT 2010 (ICN100010, Alexander Aminor, Age 35)
-- Scenario: Recent Cerner facility care, some overlap with VistA
-- Records: ~23 vaccines (mix of recent + some historical)
-- =============================================================================

INSERT INTO ImmunizationMill.VaccineAdmin
(PersonSID, PatientICN, VaccineCodeSID, AdministeredDateTime, SeriesNumber, TotalInSeries, DoseAmount, DoseUnit, RouteCode, BodySite, AdverseReaction, IsActive)
VALUES
-- COVID-19 series (Moderna) - 2021 primary + booster
(2010, 'ICN100010', 2, '2021-05-15 10:00:00', '1', '2', '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2010, 'ICN100010', 2, '2021-06-19 10:30:00', '2', '2', '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2010, 'ICN100010', 2, '2022-03-10 11:00:00', 'BOOSTER 1', NULL, '0.25', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),

-- Annual influenza vaccines
(2010, 'ICN100010', 5, '2021-10-20 13:00:00', 'ANNUAL 2021', NULL, '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2010, 'ICN100010', 5, '2022-10-18 13:30:00', 'ANNUAL 2022', NULL, '0.5', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),
(2010, 'ICN100010', 5, '2023-10-15 14:00:00', 'ANNUAL 2023', NULL, '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2010, 'ICN100010', 5, '2024-10-12 14:30:00', 'ANNUAL 2024', NULL, '0.5', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),

-- Tdap booster
(2010, 'ICN100010', 6, '2022-07-25 14:00:00', 'BOOSTER', NULL, '0.5', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),

-- Hepatitis B series (complete) - adult catch-up
(2010, 'ICN100010', 10, '2021-06-15 14:00:00', '1', '3', '1.0', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),
(2010, 'ICN100010', 10, '2021-08-20 14:30:00', '2', '3', '1.0', 'ML', 'IM', 'RIGHT DELTOID', NULL, 1),
(2010, 'ICN100010', 10, '2022-02-25 15:00:00', '3', '3', '1.0', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),

-- HPV series (INCOMPLETE - only 1 of 2)
(2010, 'ICN100010', 12, '2022-05-20 11:00:00', '1', '2', '1.0', 'ML', 'IM', 'LEFT DELTOID', NULL, 1),

-- Historical childhood vaccines (limited records from Cerner migration)
(2010, 'ICN100010', 13, '1991-08-15 10:00:00', '1', '3', '0.5', 'ML', 'IM', 'LEFT THIGH', NULL, 1),
(2010, 'ICN100010', 13, '1991-10-20 10:00:00', '2', '3', '0.5', 'ML', 'IM', 'RIGHT THIGH', NULL, 1),
(2010, 'ICN100010', 13, '1992-04-25 10:00:00', '3', '3', '0.5', 'ML', 'IM', 'LEFT THIGH', NULL, 1),

(2010, 'ICN100010', 14, '1991-08-20 10:00:00', '1', '5', '0.5', 'ML', 'IM', 'RIGHT THIGH', NULL, 1),
(2010, 'ICN100010', 14, '1991-10-25 10:00:00', '2', '5', '0.5', 'ML', 'IM', 'LEFT THIGH', NULL, 1),
(2010, 'ICN100010', 14, '1991-12-30 10:00:00', '3', '5', '0.5', 'ML', 'IM', 'RIGHT THIGH', NULL, 1),
(2010, 'ICN100010', 14, '1992-08-15 10:00:00', '4', '5', '0.5', 'ML', 'IM', 'LEFT THIGH', NULL, 1),
(2010, 'ICN100010', 14, '1996-09-01 10:00:00', '5', '5', '0.5', 'ML', 'IM', 'LEFT ARM', NULL, 1),

(2010, 'ICN100010', 15, '1991-08-20 10:15:00', '1', '4', '0.5', 'ML', 'IM', 'LEFT THIGH', NULL, 1),
(2010, 'ICN100010', 15, '1991-10-25 10:15:00', '2', '4', '0.5', 'ML', 'IM', 'RIGHT THIGH', NULL, 1),
(2010, 'ICN100010', 15, '1992-08-15 10:15:00', '3', '4', '0.5', 'ML', 'IM', 'RIGHT THIGH', NULL, 1);
GO

-- =============================================================================
-- Verification queries
-- =============================================================================

PRINT '';
PRINT '=== Verification Summary ===';
PRINT '';

-- Total count
DECLARE @TotalCount INT;
SELECT @TotalCount = COUNT(*) FROM ImmunizationMill.VaccineAdmin;
PRINT 'Total immunization administration records: ' + CAST(@TotalCount AS VARCHAR(10));

-- Count by patient
PRINT '';
PRINT 'Records by patient (ICN):';
SELECT
    PatientICN,
    COUNT(*) AS ImmunizationCount
FROM ImmunizationMill.VaccineAdmin
GROUP BY PatientICN
ORDER BY PatientICN;

-- Sample records
PRINT '';
PRINT 'Sample immunization administration records:';
SELECT TOP 5
    va.VaccineAdminSID,
    va.PatientICN,
    vc.Display AS VaccineName,
    vc.CVXCode,
    va.AdministeredDateTime,
    va.SeriesNumber,
    va.TotalInSeries
FROM ImmunizationMill.VaccineAdmin va
JOIN ImmunizationMill.VaccineCode vc ON va.VaccineCodeSID = vc.VaccineCodeSID
ORDER BY va.AdministeredDateTime DESC;

PRINT '';
PRINT 'Immunization administration data insertion complete!';
GO
