/*
|----------------------------------------------------------------------
| Inpat.Inpatient.sql
|----------------------------------------------------------------------
| Insert test data for Encounters domain
| Updated: 2025-12-15
|
| Test Data Distribution:
| - 35 total encounters across 36 patients
| - 5 active admissions (no discharge date)
| - 10 recent discharges (<30 days from 2025-12-15)
| - 15 historical discharges (30-365 days ago)
| - 5 old discharges (>365 days ago)
|
| Facility Distribution:
| - Site 508 (Atlanta): 12 encounters
| - Site 516 (Bay Pines): 10 encounters
| - Site 552 (Dayton): 8 encounters
| - Site 688 (Washington DC): 5 encounters
|
| Edge Cases:
| - Patient 1: 6 admissions (frequent readmissions)
| - Patients 10, 11: Same-day admit/discharge
| - Patient 15: Extended LOS (>30 days, active)
| - 3 encounters with missing discharge diagnosis
|----------------------------------------------------------------------
*/

PRINT '================================================';
PRINT '====            Inpat.Inpatient             ====';
PRINT '================================================';
GO

-- Set the active database
USE CDWWork;
GO

PRINT '';
PRINT 'Inserting 35 Inpatient Encounters';
GO

SET QUOTED_IDENTIFIER ON;
GO

/*
|----------------------------------------------------------------------
| ACTIVE ADMISSIONS (5 encounters - No discharge date)
|----------------------------------------------------------------------
*/
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
-- Active #1: Recent admission (2025-12-10) - Site 508
(1, '2025-12-10 14:30:00', 1, 1, 'I50.9',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 508),

-- Active #2: Recent admission (2025-12-12) - Site 516
(2, '2025-12-12 08:15:00', 53, 2, 'J18.9',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 516),

-- Active #3: Recent admission (2025-12-13) - Site 552
(3, '2025-12-13 06:00:00', 105, 3, 'R07.9',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 552),

-- Active #4: Week-old admission (2025-12-08) - Site 688
(4, '2025-12-08 11:20:00', 157, 4, 'N39.0',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 688),

-- Active #5: Extended LOS (>30 days, 2025-11-10) - Site 508 - EDGE CASE
(15, '2025-11-10 09:00:00', 1, 1, 'I21.9',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 508);
GO

/*
|----------------------------------------------------------------------
| RECENT DISCHARGES (<30 days from 2025-12-15) - 10 encounters
|----------------------------------------------------------------------
*/
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
-- Recent Discharge #1: 3 days ago - Site 508
(5, '2025-12-09 07:00:00', 1, 1, 'K92.2',
 '2025-12-12 16:00:00', NULL, 1, 'K92.2', 'GI bleed, resolved', 'Home', 3, 'Discharged', 508),

-- Recent Discharge #2: 5 days ago - Site 516
(6, '2025-12-05 10:30:00', 53, 2, 'I48.91',
 '2025-12-10 14:00:00', NULL, 53, 'I48.91', 'Atrial fibrillation with RVR', 'Home', 5, 'Discharged', 516),

-- Recent Discharge #3: 7 days ago - Site 552
(7, '2025-12-01 13:00:00', 105, 3, 'J44.1',
 '2025-12-08 11:00:00', NULL, 105, 'J44.1', 'COPD exacerbation', 'Home with O2', 7, 'Discharged', 552),

-- Recent Discharge #4: 10 days ago - Site 688
(8, '2025-11-30 06:45:00', 157, 4, 'E11.65',
 '2025-12-05 10:00:00', NULL, 157, 'E11.65', 'Diabetic foot ulcer', 'SNF', 5, 'Discharged', 688),

-- Recent Discharge #5: 12 days ago - Site 508
(9, '2025-11-28 09:00:00', 1, 1, 'S72.001A',
 '2025-12-03 15:00:00', NULL, 1, 'S72.001A', 'Hip fracture, s/p ORIF', 'Rehab', 5, 'Discharged', 508),

-- Recent Discharge #6: 15 days ago (same-day discharge) - Site 516 - EDGE CASE
(10, '2025-11-30 08:00:00', 53, 2, 'R10.9',
 '2025-11-30 18:00:00', NULL, 53, 'R10.9', 'Abdominal pain, observation', 'Home', 0, 'Discharged', 516),

-- Recent Discharge #7: 18 days ago (same-day discharge) - Site 552 - EDGE CASE
(11, '2025-11-27 14:00:00', 105, 3, 'R55',
 '2025-11-27 22:00:00', NULL, 105, 'R55', 'Syncope, observation', 'Home', 0, 'Discharged', 552),

-- Recent Discharge #8: 20 days ago - Site 688
(12, '2025-11-25 11:00:00', 157, 4, 'N18.3',
 '2025-11-25 15:00:00', NULL, 157, NULL, NULL, 'Home', 0, 'Discharged', 688),

-- Recent Discharge #9: 25 days ago - Site 508
(13, '2025-11-20 16:00:00', 1, 1, 'G89.29',
 '2025-11-24 10:00:00', NULL, 1, 'G89.29', 'Chronic pain management', 'Home', 4, 'Discharged', 508),

-- Recent Discharge #10: 28 days ago - Site 516
(14, '2025-11-17 12:00:00', 53, 2, 'I63.9',
 '2025-11-22 09:00:00', NULL, 53, 'I63.9', 'CVA with mild residual deficits', 'SNF', 5, 'Discharged', 516);
GO

/*
|----------------------------------------------------------------------
| HISTORICAL DISCHARGES (30-365 days ago) - 15 encounters
|----------------------------------------------------------------------
*/
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
-- Historical #1: 35 days ago (Patient 1, admission #2) - Site 508
(1, '2025-11-08 10:00:00', 1, 1, 'I50.9',
 '2025-11-10 14:00:00', NULL, 1, 'I50.9', 'CHF exacerbation', 'Home', 2, 'Discharged', 508),

-- Historical #2: 60 days ago - Site 516
(16, '2025-10-16 08:30:00', 53, 2, 'J96.01',
 '2025-10-20 16:00:00', NULL, 53, 'J96.01', 'Acute respiratory failure', 'Home with O2', 4, 'Discharged', 516),

-- Historical #3: 90 days ago - Site 552
(17, '2025-09-16 14:00:00', 105, 3, 'K80.00',
 '2025-09-19 11:00:00', NULL, 105, 'K80.00', 'Cholelithiasis, s/p cholecystectomy', 'Home', 3, 'Discharged', 552),

-- Historical #4: 120 days ago (Patient 1, admission #3) - Site 508
(1, '2025-08-17 06:00:00', 1, 1, 'I48.0',
 '2025-08-20 10:00:00', NULL, 1, 'I48.0', 'Atrial flutter, cardioversion', 'Home', 3, 'Discharged', 508),

-- Historical #5: 150 days ago - Site 688
(18, '2025-07-18 13:00:00', 157, 4, 'L03.115',
 '2025-07-23 15:00:00', NULL, 157, 'L03.115', 'Cellulitis of right lower extremity', 'Home', 5, 'Discharged', 688),

-- Historical #6: 180 days ago - Site 508
(19, '2025-06-18 09:00:00', 1, 1, 'M54.5',
 '2025-06-21 12:00:00', NULL, 1, NULL, NULL, 'Home', 3, 'Discharged', 508),

-- Historical #7: 210 days ago (Patient 1, admission #4) - Site 516
(1, '2025-05-19 11:00:00', 53, 2, 'N17.9',
 '2025-05-25 08:00:00', NULL, 53, 'N17.9', 'Acute kidney injury', 'Home', 6, 'Discharged', 516),

-- Historical #8: 240 days ago - Site 552
(20, '2025-04-19 07:30:00', 105, 3, 'F32.9',
 '2025-04-22 14:00:00', NULL, 105, 'F32.9', 'Major depressive disorder, stabilized', 'Home', 3, 'Discharged', 552),

-- Historical #9: 270 days ago - Site 688
(21, '2025-03-20 15:00:00', 157, 4, 'G40.909',
 '2025-03-24 10:00:00', NULL, 157, 'G40.909', 'Seizure disorder, medication adjustment', 'Home', 4, 'Discharged', 688),

-- Historical #10: 300 days ago (Patient 1, admission #5) - Site 508
(1, '2025-02-18 08:00:00', 1, 1, 'K56.60',
 '2025-02-23 16:00:00', NULL, 1, 'K56.60', 'Bowel obstruction, resolved', 'Home', 5, 'Discharged', 508),

-- Historical #11: 320 days ago - Site 516
(22, '2025-01-29 10:00:00', 53, 2, 'M25.511',
 '2025-02-02 11:00:00', NULL, 53, 'M25.511', 'Pain in right shoulder, PT', 'Home', 4, 'Discharged', 516),

-- Historical #12: 340 days ago - Site 552
(23, '2025-01-09 12:00:00', 105, 3, 'R00.0',
 '2025-01-11 09:00:00', NULL, 105, NULL, NULL, 'Home', 2, 'Discharged', 552),

-- Historical #13: 350 days ago - Site 508
(24, '2024-12-30 14:00:00', 1, 1, 'Z51.11',
 '2025-01-03 10:00:00', NULL, 1, 'Z51.11', 'Chemotherapy encounter', 'Home', 4, 'Discharged', 508),

-- Historical #14: 355 days ago - Site 516
(25, '2024-12-25 06:00:00', 53, 2, 'T84.050A',
 '2024-12-29 15:00:00', NULL, 53, 'T84.050A', 'Periprosthetic osteolysis', 'Rehab', 4, 'Discharged', 516),

-- Historical #15: 360 days ago (Patient 1, admission #6) - Site 552 (frequent readmissions)
(1, '2024-12-20 09:00:00', 105, 3, 'I50.9',
 '2024-12-24 13:00:00', NULL, 105, 'I50.9', 'CHF exacerbation', 'Home', 4, 'Discharged', 552);
GO

/*
|----------------------------------------------------------------------
| OLD DISCHARGES (>365 days ago) - 5 encounters
|----------------------------------------------------------------------
*/
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
-- Old #1: 400 days ago - Site 508
(26, '2024-11-10 10:00:00', 1, 1, 'I25.10',
 '2024-11-15 12:00:00', NULL, 1, 'I25.10', 'CAD, s/p cardiac cath', 'Home', 5, 'Discharged', 508),

-- Old #2: 450 days ago - Site 516
(27, '2024-09-21 08:00:00', 53, 2, 'M17.11',
 '2024-09-25 14:00:00', NULL, 53, 'M17.11', 'Osteoarthritis, s/p TKR', 'Rehab', 4, 'Discharged', 516),

-- Old #3: 500 days ago - Site 552
(28, '2024-08-02 11:00:00', 105, 3, 'C34.90',
 '2024-08-08 16:00:00', NULL, 105, 'C34.90', 'Lung cancer, initiate treatment', 'Home', 6, 'Discharged', 552),

-- Old #4: 550 days ago - Site 688
(29, '2024-06-13 09:00:00', 157, 4, 'I60.9',
 '2024-06-20 11:00:00', NULL, 157, 'I60.9', 'Subarachnoid hemorrhage, stabilized', 'SNF', 7, 'Discharged', 688),

-- Old #5: 600 days ago - Site 508
(30, '2024-04-24 07:00:00', 1, 1, 'J81.0',
 '2024-04-29 10:00:00', NULL, 1, 'J81.0', 'Acute pulmonary edema', 'Home with O2', 5, 'Discharged', 508);
GO

PRINT '';
PRINT '==== Inserted 35 Inpatient Encounters ====';
PRINT 'Active Admissions: 5';
PRINT 'Recent Discharges (<30d): 10';
PRINT 'Historical Discharges (30-365d): 15';
PRINT 'Old Discharges (>365d): 5';
PRINT '';
PRINT 'Facility Distribution:';
PRINT '  Site 508 (Atlanta): 12 encounters';
PRINT '  Site 516 (Bay Pines): 10 encounters';
PRINT '  Site 552 (Dayton): 8 encounters';
PRINT '  Site 688 (Washington DC): 5 encounters';
PRINT '';
PRINT '==== Edge Cases ====';
PRINT '  Patient 1: 6 total admissions (frequent readmissions)';
PRINT '  Patients 10, 11: Same-day admit/discharge';
PRINT '  Patient 15: Extended LOS >30 days (active)';
PRINT '  3 encounters with missing discharge diagnosis';
PRINT '';
PRINT '==== Done ====';
GO

/*
|----------------------------------------------------------------------
| Additional Encounters for Pagination Testing
|----------------------------------------------------------------------
| Patient 1 (ICN100001): 24 additional encounters (30 total)
| Patient 4 (ICN100004): 14 additional encounters (15 total)
|----------------------------------------------------------------------
*/

PRINT 'Inserting additional encounters for pagination testing...';
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Additional encounters for Patient 1 (24 more)
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
(1, '2025-12-06 00:00:00', 6, 1, 'I50.9',
 '2025-12-09 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 3, 'Discharged', 508),
(1, '2025-12-02 00:00:00', 6, 1, 'J44.1',
 '2025-12-05 00:00:00', NULL, 6, 'J44.1', 'COPD exacerbation', 'Home with O2', 3, 'Discharged', 516),
(1, '2025-11-28 00:00:00', 6, 1, 'I48.91',
 '2025-12-01 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 3, 'Discharged', 552),
(1, '2025-11-24 00:00:00', 9, 1, 'N17.9',
 '2025-11-27 00:00:00', NULL, 9, 'N17.9', 'Acute kidney injury', 'Rehab', 3, 'Discharged', 688),
(1, '2025-11-20 00:00:00', 6, 1, 'E11.65',
 '2025-11-23 00:00:00', NULL, 6, 'E11.65', 'Diabetic complications', 'Home', 3, 'Discharged', 508),
(1, '2025-11-01 00:00:00', 6, 1, 'I50.9',
 '2025-11-05 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 4, 'Discharged', 508),
(1, '2025-10-12 00:00:00', 6, 1, 'J44.1',
 '2025-10-16 00:00:00', NULL, 6, 'J44.1', 'COPD exacerbation', 'Home with O2', 4, 'Discharged', 516),
(1, '2025-09-22 00:00:00', 6, 1, 'I48.91',
 '2025-09-26 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 4, 'Discharged', 552),
(1, '2025-09-02 00:00:00', 9, 1, 'N17.9',
 '2025-09-06 00:00:00', NULL, 9, 'N17.9', 'Acute kidney injury', 'Rehab', 4, 'Discharged', 688),
(1, '2025-08-13 00:00:00', 6, 1, 'E11.65',
 '2025-08-17 00:00:00', NULL, 6, 'E11.65', 'Diabetic complications', 'Home', 4, 'Discharged', 508),
(1, '2025-07-24 00:00:00', 6, 1, 'K92.2',
 '2025-07-28 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'Home', 4, 'Discharged', 516),
(1, '2025-07-04 00:00:00', 6, 1, 'J18.9',
 '2025-07-08 00:00:00', NULL, 6, 'J18.9', 'Pneumonia', 'Home with O2', 4, 'Discharged', 552),
(1, '2025-06-14 00:00:00', 9, 1, 'I21.9',
 '2025-06-18 00:00:00', NULL, 9, 'I21.9', 'Acute MI', 'SNF', 4, 'Discharged', 688),
(1, '2025-05-25 00:00:00', 6, 1, 'G40.909',
 '2025-05-29 00:00:00', NULL, 6, 'G40.909', 'Seizure disorder', 'Rehab', 4, 'Discharged', 508),
(1, '2025-05-05 00:00:00', 6, 1, 'M54.5',
 '2025-05-09 00:00:00', NULL, 6, 'M54.5', 'Low back pain', 'Home', 4, 'Discharged', 516),
(1, '2025-04-15 00:00:00', 6, 1, 'I50.9',
 '2025-04-19 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 4, 'Discharged', 552),
(1, '2025-03-26 00:00:00', 9, 1, 'J44.1',
 '2025-03-30 00:00:00', NULL, 9, 'J44.1', 'COPD exacerbation', 'Home with O2', 4, 'Discharged', 688),
(1, '2025-03-06 00:00:00', 6, 1, 'I48.91',
 '2025-03-10 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 4, 'Discharged', 508),
(1, '2025-02-14 00:00:00', 6, 1, 'N17.9',
 '2025-02-18 00:00:00', NULL, 6, 'N17.9', 'Acute kidney injury', 'Rehab', 4, 'Discharged', 516),
(1, '2025-01-25 00:00:00', 6, 1, 'E11.65',
 '2025-01-29 00:00:00', NULL, 6, 'E11.65', 'Diabetic complications', 'Home', 4, 'Discharged', 552),
(1, '2024-11-05 00:00:00', 6, 1, 'I50.9',
 '2024-11-10 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 5, 'Discharged', 508),
(1, '2024-09-06 00:00:00', 6, 1, 'J44.1',
 '2024-09-11 00:00:00', NULL, 6, 'J44.1', 'COPD exacerbation', 'Home with O2', 5, 'Discharged', 516),
(1, '2024-07-08 00:00:00', 6, 1, 'I48.91',
 '2024-07-13 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 5, 'Discharged', 552),
(1, '2024-05-09 00:00:00', 9, 1, 'N17.9',
 '2024-05-14 00:00:00', NULL, 9, 'N17.9', 'Acute kidney injury', 'Rehab', 5, 'Discharged', 688);
GO

-- Additional encounters for Patient 4 (14 more)
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
(4, '2025-12-04 00:00:00', 6, 4, 'N17.9',
 '2025-12-07 00:00:00', NULL, 6, 'N17.9', 'Acute kidney injury', 'Home', 3, 'Discharged', 552),
(4, '2025-11-29 00:00:00', 9, 4, 'E11.65',
 '2025-12-02 00:00:00', NULL, 9, 'E11.65', 'Diabetic complications', 'Home with O2', 3, 'Discharged', 688),
(4, '2025-11-24 00:00:00', 6, 4, 'K92.2',
 '2025-11-27 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'SNF', 3, 'Discharged', 508),
(4, '2025-10-22 00:00:00', 6, 4, 'I48.91',
 '2025-10-26 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'Home', 4, 'Discharged', 516),
(4, '2025-09-22 00:00:00', 6, 4, 'N17.9',
 '2025-09-26 00:00:00', NULL, 6, 'N17.9', 'Acute kidney injury', 'Home with O2', 4, 'Discharged', 552),
(4, '2025-08-23 00:00:00', 9, 4, 'E11.65',
 '2025-08-27 00:00:00', NULL, 9, 'E11.65', 'Diabetic complications', 'SNF', 4, 'Discharged', 688),
(4, '2025-07-24 00:00:00', 6, 4, 'K92.2',
 '2025-07-28 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'Rehab', 4, 'Discharged', 508),
(4, '2025-06-24 00:00:00', 6, 4, 'J18.9',
 '2025-06-28 00:00:00', NULL, 6, 'J18.9', 'Pneumonia', 'Home', 4, 'Discharged', 516),
(4, '2025-05-25 00:00:00', 6, 4, 'I21.9',
 '2025-05-29 00:00:00', NULL, 6, 'I21.9', 'Acute MI', 'Home', 4, 'Discharged', 552),
(4, '2025-04-25 00:00:00', 9, 4, 'G40.909',
 '2025-04-29 00:00:00', NULL, 9, 'G40.909', 'Seizure disorder', 'Home with O2', 4, 'Discharged', 688),
(4, '2025-03-26 00:00:00', 6, 4, 'M54.5',
 '2025-03-30 00:00:00', NULL, 6, 'M54.5', 'Low back pain', 'SNF', 4, 'Discharged', 508),
(4, '2024-10-16 00:00:00', 6, 4, 'K92.2',
 '2024-10-21 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'Home', 5, 'Discharged', 508),
(4, '2024-08-07 00:00:00', 6, 4, 'J18.9',
 '2024-08-12 00:00:00', NULL, 6, 'J18.9', 'Pneumonia', 'Home with O2', 5, 'Discharged', 516),
(4, '2024-05-29 00:00:00', 6, 4, 'I21.9',
 '2024-06-03 00:00:00', NULL, 6, 'I21.9', 'Acute MI', 'SNF', 5, 'Discharged', 552);
GO

PRINT '';
PRINT '==== Added 38 Additional Encounters for Pagination Testing ====';
PRINT '  Patient 1 (ICN100001): 24 more encounters (30 total)';
PRINT '  Patient 4 (ICN100004): 14 more encounters (15 total)';
PRINT '';
PRINT '==== Total Dataset: 73 Encounters ====';
GO

