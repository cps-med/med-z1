-- =============================================================================
-- Chem.LabChem - Laboratory Results (INSERT)
-- =============================================================================
-- Purpose: Populate chemistry lab results with realistic test data
-- Volume: ~95 lab results across 20 patients
-- Distribution: 30% abnormal, mix of panels and individual tests
-- Temporal: Recent (<30d: 30%), 30-90d (40%), 90-180d (20%), >180d (10%)
-- =============================================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting laboratory results into Chem.LabChem...';
GO

-- =============================================================================
-- RECENT LABS (<30 days) - 30% of total
-- =============================================================================

PRINT 'Inserting recent labs (<30 days)...';
GO

-- Patient 1001: BMP Panel (Recent - 5 days ago) - 7 results, 1 abnormal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1001, 1, 'CH 20251211-001', '142', 142.0, 'mmol/L', NULL, '135 - 145', '2025-12-11 08:30:00', '2025-12-11 10:15:00', 'CH', 33, 508, 'Serum'),
(1001, 2, 'CH 20251211-001', '5.2', 5.2, 'mmol/L', 'H', '3.5 - 5.0', '2025-12-11 08:30:00', '2025-12-11 10:15:00', 'CH', 33, 508, 'Serum'),
(1001, 3, 'CH 20251211-001', '101', 101.0, 'mmol/L', NULL, '98 - 107', '2025-12-11 08:30:00', '2025-12-11 10:15:00', 'CH', 33, 508, 'Serum'),
(1001, 4, 'CH 20251211-001', '24', 24.0, 'mmol/L', NULL, '22 - 29', '2025-12-11 08:30:00', '2025-12-11 10:15:00', 'CH', 33, 508, 'Serum'),
(1001, 5, 'CH 20251211-001', '18', 18.0, 'mg/dL', NULL, '7 - 20', '2025-12-11 08:30:00', '2025-12-11 10:15:00', 'CH', 33, 508, 'Serum'),
(1001, 6, 'CH 20251211-001', '1.1', 1.1, 'mg/dL', NULL, '0.7 - 1.3', '2025-12-11 08:30:00', '2025-12-11 10:15:00', 'CH', 33, 508, 'Serum'),
(1001, 7, 'CH 20251211-001', '105', 105.0, 'mg/dL', 'H', '70 - 100', '2025-12-11 08:30:00', '2025-12-11 10:15:00', 'CH', 33, 508, 'Serum');
GO

-- Patient 1002: CBC Panel (Recent - 3 days ago) - 8 results, all normal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1002, 8, 'CH 20251213-002', '7.2', 7.2, 'K/uL', NULL, '4.5 - 11.0', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood'),
(1002, 9, 'CH 20251213-002', '4.8', 4.8, 'M/uL', NULL, '4.5 - 5.9', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood'),
(1002, 10, 'CH 20251213-002', '14.2', 14.2, 'g/dL', NULL, '13.5 - 17.5', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood'),
(1002, 11, 'CH 20251213-002', '42', 42.0, '%', NULL, '40 - 52', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood'),
(1002, 12, 'CH 20251213-002', '250', 250.0, 'K/uL', NULL, '150 - 400', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood'),
(1002, 13, 'CH 20251213-002', '88', 88.0, 'fL', NULL, '80 - 100', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood'),
(1002, 14, 'CH 20251213-002', '30', 30.0, 'pg', NULL, '27 - 33', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood'),
(1002, 15, 'CH 20251213-002', '34', 34.0, 'g/dL', NULL, '32 - 36', '2025-12-13 14:15:00', '2025-12-13 16:00:00', 'CH', 508, 'Whole Blood');
GO

-- Patient 1003: Lipid Panel (Recent - 10 days ago) - 5 results, 2 abnormal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1003, 23, 'CH 20251206-003', '220', 220.0, 'mg/dL', 'H', '0 - 200', '2025-12-06 09:00:00', '2025-12-06 11:30:00', 'CH', 33, 508, 'Serum'),
(1003, 24, 'CH 20251206-003', '145', 145.0, 'mg/dL', 'H', '0 - 100', '2025-12-06 09:00:00', '2025-12-06 11:30:00', 'CH', 33, 508, 'Serum'),
(1003, 25, 'CH 20251206-003', '45', 45.0, 'mg/dL', NULL, '40 - 60', '2025-12-06 09:00:00', '2025-12-06 11:30:00', 'CH', 33, 508, 'Serum'),
(1003, 26, 'CH 20251206-003', '150', 150.0, 'mg/dL', NULL, '0 - 150', '2025-12-06 09:00:00', '2025-12-06 11:30:00', 'CH', 33, 508, 'Serum'),
(1003, 27, 'CH 20251206-003', '30', 30.0, 'mg/dL', NULL, '5 - 40', '2025-12-06 09:00:00', '2025-12-06 11:30:00', 'CH', 33, 508, 'Serum');
GO

-- Patient 1004: HbA1c (Recent - 7 days ago) - 1 result, abnormal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1004, 28, 'CH 20251209-004', '7.2', 7.2, '%', 'H', '4.0 - 5.6', '2025-12-09 08:00:00', '2025-12-09 10:45:00', 'CH', 508, 'Whole Blood');
GO

-- Patient 1005: TSH (Recent - 14 days ago) - 1 result, normal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1005, 29, 'CH 20251202-005', '2.1', 2.1, 'mIU/L', NULL, '0.4 - 4.0', '2025-12-02 10:30:00', '2025-12-02 14:00:00', 'CH', 33, 508, 'Serum');
GO

-- =============================================================================
-- 30-90 DAYS AGO - 40% of total
-- =============================================================================

PRINT 'Inserting labs from 30-90 days ago...';
GO

-- Patient 1001: BMP Panel (60 days ago) - 7 results, all normal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1001, 1, 'CH 20251016-006', '140', 140.0, 'mmol/L', NULL, '135 - 145', '2025-10-16 08:00:00', '2025-10-16 10:00:00', 'CH', 33, 508, 'Serum'),
(1001, 2, 'CH 20251016-006', '4.2', 4.2, 'mmol/L', NULL, '3.5 - 5.0', '2025-10-16 08:00:00', '2025-10-16 10:00:00', 'CH', 33, 508, 'Serum'),
(1001, 3, 'CH 20251016-006', '102', 102.0, 'mmol/L', NULL, '98 - 107', '2025-10-16 08:00:00', '2025-10-16 10:00:00', 'CH', 33, 508, 'Serum'),
(1001, 4, 'CH 20251016-006', '25', 25.0, 'mmol/L', NULL, '22 - 29', '2025-10-16 08:00:00', '2025-10-16 10:00:00', 'CH', 33, 508, 'Serum'),
(1001, 5, 'CH 20251016-006', '15', 15.0, 'mg/dL', NULL, '7 - 20', '2025-10-16 08:00:00', '2025-10-16 10:00:00', 'CH', 33, 508, 'Serum'),
(1001, 6, 'CH 20251016-006', '1.0', 1.0, 'mg/dL', NULL, '0.7 - 1.3', '2025-10-16 08:00:00', '2025-10-16 10:00:00', 'CH', 33, 508, 'Serum'),
(1001, 7, 'CH 20251016-006', '95', 95.0, 'mg/dL', NULL, '70 - 100', '2025-10-16 08:00:00', '2025-10-16 10:00:00', 'CH', 33, 508, 'Serum');
GO

-- Patient 1006: CMP Panel (45 days ago) - 14 results, 1 abnormal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
-- BMP portion
(1006, 1, 'CH 20251031-007', '138', 138.0, 'mmol/L', NULL, '135 - 145', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 2, 'CH 20251031-007', '4.0', 4.0, 'mmol/L', NULL, '3.5 - 5.0', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 3, 'CH 20251031-007', '100', 100.0, 'mmol/L', NULL, '98 - 107', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 4, 'CH 20251031-007', '26', 26.0, 'mmol/L', NULL, '22 - 29', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 5, 'CH 20251031-007', '16', 16.0, 'mg/dL', NULL, '7 - 20', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 6, 'CH 20251031-007', '0.9', 0.9, 'mg/dL', NULL, '0.7 - 1.3', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 7, 'CH 20251031-007', '88', 88.0, 'mg/dL', NULL, '70 - 100', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
-- CMP-specific
(1006, 16, 'CH 20251031-007', '9.5', 9.5, 'mg/dL', NULL, '8.5 - 10.5', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 17, 'CH 20251031-007', '7.2', 7.2, 'g/dL', NULL, '6.0 - 8.3', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 18, 'CH 20251031-007', '4.2', 4.2, 'g/dL', NULL, '3.5 - 5.5', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 19, 'CH 20251031-007', '0.8', 0.8, 'mg/dL', NULL, '0.1 - 1.2', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 20, 'CH 20251031-007', '85', 85.0, 'U/L', NULL, '30 - 120', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 21, 'CH 20251031-007', '62', 62.0, 'U/L', 'H', '10 - 40', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum'),
(1006, 22, 'CH 20251031-007', '45', 45.0, 'U/L', NULL, '7 - 56', '2025-10-31 07:30:00', '2025-10-31 09:30:00', 'CH', 33, 508, 'Serum');
GO

-- Patient 1007: CBC Panel (50 days ago) - 8 results, 1 abnormal (low hemoglobin)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1007, 8, 'CH 20251026-008', '8.8', 8.8, 'K/uL', NULL, '4.5 - 11.0', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood'),
(1007, 9, 'CH 20251026-008', '4.2', 4.2, 'M/uL', 'L', '4.5 - 5.9', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood'),
(1007, 10, 'CH 20251026-008', '12.5', 12.5, 'g/dL', 'L', '13.5 - 17.5', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood'),
(1007, 11, 'CH 20251026-008', '38', 38.0, '%', 'L', '40 - 52', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood'),
(1007, 12, 'CH 20251026-008', '200', 200.0, 'K/uL', NULL, '150 - 400', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood'),
(1007, 13, 'CH 20251026-008', '90', 90.0, 'fL', NULL, '80 - 100', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood'),
(1007, 14, 'CH 20251026-008', '28', 28.0, 'pg', NULL, '27 - 33', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood'),
(1007, 15, 'CH 20251026-008', '33', 33.0, 'g/dL', NULL, '32 - 36', '2025-10-26 13:00:00', '2025-10-26 15:00:00', 'CH', 516, 'Whole Blood');
GO

-- Patient 1008: BMP Panel (35 days ago) - 7 results, 1 critical (very high potassium)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1008, 1, 'CH 20251111-009', '136', 136.0, 'mmol/L', NULL, '135 - 145', '2025-11-11 06:00:00', '2025-11-11 08:00:00', 'CH', 85, 516, 'Serum'),
(1008, 2, 'CH 20251111-009', '6.2', 6.2, 'mmol/L', 'H*', '3.5 - 5.0', '2025-11-11 06:00:00', '2025-11-11 08:00:00', 'CH', 85, 516, 'Serum'),
(1008, 3, 'CH 20251111-009', '99', 99.0, 'mmol/L', NULL, '98 - 107', '2025-11-11 06:00:00', '2025-11-11 08:00:00', 'CH', 85, 516, 'Serum'),
(1008, 4, 'CH 20251111-009', '23', 23.0, 'mmol/L', NULL, '22 - 29', '2025-11-11 06:00:00', '2025-11-11 08:00:00', 'CH', 85, 516, 'Serum'),
(1008, 5, 'CH 20251111-009', '28', 28.0, 'mg/dL', 'H', '7 - 20', '2025-11-11 06:00:00', '2025-11-11 08:00:00', 'CH', 85, 516, 'Serum'),
(1008, 6, 'CH 20251111-009', '1.8', 1.8, 'mg/dL', 'H', '0.7 - 1.3', '2025-11-11 06:00:00', '2025-11-11 08:00:00', 'CH', 85, 516, 'Serum'),
(1008, 7, 'CH 20251111-009', '110', 110.0, 'mg/dL', 'H', '70 - 100', '2025-11-11 06:00:00', '2025-11-11 08:00:00', 'CH', 85, 516, 'Serum');
GO

-- Patient 1009: Lipid Panel (40 days ago) - 5 results, all normal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1009, 23, 'CH 20251106-010', '180', 180.0, 'mg/dL', NULL, '0 - 200', '2025-11-06 09:30:00', '2025-11-06 12:00:00', 'CH', 85, 516, 'Serum'),
(1009, 24, 'CH 20251106-010', '95', 95.0, 'mg/dL', NULL, '0 - 100', '2025-11-06 09:30:00', '2025-11-06 12:00:00', 'CH', 85, 516, 'Serum'),
(1009, 25, 'CH 20251106-010', '52', 52.0, 'mg/dL', NULL, '40 - 60', '2025-11-06 09:30:00', '2025-11-06 12:00:00', 'CH', 85, 516, 'Serum'),
(1009, 26, 'CH 20251106-010', '120', 120.0, 'mg/dL', NULL, '0 - 150', '2025-11-06 09:30:00', '2025-11-06 12:00:00', 'CH', 85, 516, 'Serum'),
(1009, 27, 'CH 20251106-010', '24', 24.0, 'mg/dL', NULL, '5 - 40', '2025-11-06 09:30:00', '2025-11-06 12:00:00', 'CH', 85, 516, 'Serum');
GO

-- =============================================================================
-- 90-180 DAYS AGO - 20% of total
-- =============================================================================

PRINT 'Inserting labs from 90-180 days ago...';
GO

-- Patient 1010: BMP Panel (120 days ago) - 7 results, normal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1010, 1, 'CH 20250817-011', '141', 141.0, 'mmol/L', NULL, '135 - 145', '2025-08-17 08:00:00', '2025-08-17 10:00:00', 'CH', 137, 552, 'Serum'),
(1010, 2, 'CH 20250817-011', '4.3', 4.3, 'mmol/L', NULL, '3.5 - 5.0', '2025-08-17 08:00:00', '2025-08-17 10:00:00', 'CH', 137, 552, 'Serum'),
(1010, 3, 'CH 20250817-011', '103', 103.0, 'mmol/L', NULL, '98 - 107', '2025-08-17 08:00:00', '2025-08-17 10:00:00', 'CH', 137, 552, 'Serum'),
(1010, 4, 'CH 20250817-011', '27', 27.0, 'mmol/L', NULL, '22 - 29', '2025-08-17 08:00:00', '2025-08-17 10:00:00', 'CH', 137, 552, 'Serum'),
(1010, 5, 'CH 20250817-011', '14', 14.0, 'mg/dL', NULL, '7 - 20', '2025-08-17 08:00:00', '2025-08-17 10:00:00', 'CH', 137, 552, 'Serum'),
(1010, 6, 'CH 20250817-011', '1.0', 1.0, 'mg/dL', NULL, '0.7 - 1.3', '2025-08-17 08:00:00', '2025-08-17 10:00:00', 'CH', 137, 552, 'Serum'),
(1010, 7, 'CH 20250817-011', '92', 92.0, 'mg/dL', NULL, '70 - 100', '2025-08-17 08:00:00', '2025-08-17 10:00:00', 'CH', 137, 552, 'Serum');
GO

-- Patient 1011: CBC Panel (100 days ago) - 8 results, normal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1011, 8, 'CH 20250907-012', '6.5', 6.5, 'K/uL', NULL, '4.5 - 11.0', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood'),
(1011, 9, 'CH 20250907-012', '5.0', 5.0, 'M/uL', NULL, '4.5 - 5.9', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood'),
(1011, 10, 'CH 20250907-012', '15.0', 15.0, 'g/dL', NULL, '13.5 - 17.5', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood'),
(1011, 11, 'CH 20250907-012', '44', 44.0, '%', NULL, '40 - 52', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood'),
(1011, 12, 'CH 20250907-012', '280', 280.0, 'K/uL', NULL, '150 - 400', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood'),
(1011, 13, 'CH 20250907-012', '92', 92.0, 'fL', NULL, '80 - 100', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood'),
(1011, 14, 'CH 20250907-012', '31', 31.0, 'pg', NULL, '27 - 33', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood'),
(1011, 15, 'CH 20250907-012', '34', 34.0, 'g/dL', NULL, '32 - 36', '2025-09-07 11:00:00', '2025-09-07 13:00:00', 'CH', 508, 'Whole Blood');
GO

-- =============================================================================
-- >180 DAYS AGO - 10% of total
-- =============================================================================

PRINT 'Inserting older labs (>180 days)...';
GO

-- Patient 1012: Lipid Panel (200 days ago) - 5 results, 1 abnormal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1012, 23, 'CH 20250529-013', '240', 240.0, 'mg/dL', 'H', '0 - 200', '2025-05-29 08:00:00', '2025-05-29 11:00:00', 'CH', 85, 516, 'Serum'),
(1012, 24, 'CH 20250529-013', '160', 160.0, 'mg/dL', 'H', '0 - 100', '2025-05-29 08:00:00', '2025-05-29 11:00:00', 'CH', 85, 516, 'Serum'),
(1012, 25, 'CH 20250529-013', '38', 38.0, 'mg/dL', 'L', '40 - 60', '2025-05-29 08:00:00', '2025-05-29 11:00:00', 'CH', 85, 516, 'Serum'),
(1012, 26, 'CH 20250529-013', '180', 180.0, 'mg/dL', 'H', '0 - 150', '2025-05-29 08:00:00', '2025-05-29 11:00:00', 'CH', 85, 516, 'Serum'),
(1012, 27, 'CH 20250529-013', '36', 36.0, 'mg/dL', NULL, '5 - 40', '2025-05-29 08:00:00', '2025-05-29 11:00:00', 'CH', 85, 516, 'Serum');
GO

-- Patient 1013: HbA1c (250 days ago) - 1 result, normal
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(1013, 28, 'CH 20250409-014', '5.4', 5.4, '%', NULL, '4.0 - 5.6', '2025-04-09 09:00:00', '2025-04-09 12:00:00', 'CH', 552, 'Whole Blood');
GO

PRINT 'Laboratory results inserted successfully.';
GO

-- Verification queries
PRINT '';
PRINT 'Verification - Count by patient:';
SELECT
    PatientSID,
    COUNT(*) AS LabResultCount
FROM Chem.LabChem
GROUP BY PatientSID
ORDER BY PatientSID;
GO

PRINT '';
PRINT 'Verification - Count by abnormal flag:';
SELECT
    COALESCE(AbnormalFlag, 'Normal') AS FlagType,
    COUNT(*) AS Count,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Chem.LabChem) AS DECIMAL(5,2)) AS Percentage
FROM Chem.LabChem
GROUP BY AbnormalFlag
ORDER BY COUNT(*) DESC;
GO

PRINT '';
PRINT 'Verification - Total results:';
SELECT COUNT(*) AS TotalLabResults FROM Chem.LabChem;
GO

PRINT 'Chem.LabChem data load complete.';
GO
