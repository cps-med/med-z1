/*
|----------------------------------------------------------------------
| Inpat.Inpatient.sql
|----------------------------------------------------------------------
| Insert test data for Encounters domain
| Updated: 2026-02-04 - FIXED: Corrected PatientSID values to match SPatient.SPatient
|
| IMPORTANT FIX (2026-02-04):
| - Original script used PatientSID 1-30 (WRONG - patients don't exist)
| - Corrected to PatientSID 1001-1025 (matches actual patients in database)
| - PatientSID 26-30 mapped to 1021-1025 (distributes old encounters among existing patients)
|
| Test Data Distribution:
| - 35 total encounters across 25 existing patients
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
| - Patient 1001: 30 admissions total (frequent readmissions, pagination testing)
| - Patient 1004: 15 admissions total (pagination testing)
| - Patients 1010, 1011: Same-day admit/discharge
| - Patient 1015: Extended LOS (>30 days, active)
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
(1001, '2025-12-10 14:30:00', 1, 1001, 'I50.9',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 508),

-- Active #2: Recent admission (2025-12-12) - Site 516
(1002, '2025-12-12 08:15:00', 53, 1002, 'J18.9',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 516),

-- Active #3: Recent admission (2025-12-13) - Site 552
(1003, '2025-12-13 06:00:00', 105, 1003, 'R07.9',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 552),

-- Active #4: Week-old admission (2025-12-08) - Site 688
(1004, '2025-12-08 11:20:00', 157, 1004, 'N39.0',
 NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 688),

-- Active #5: Extended LOS (>30 days, 2025-11-10) - Site 508 - EDGE CASE
(1015, '2025-11-10 09:00:00', 1, 1001, 'I21.9',
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
(1005, '2025-12-09 07:00:00', 1, 1001, 'K92.2',
 '2025-12-12 16:00:00', NULL, 1, 'K92.2', 'GI bleed, resolved', 'Home', 3, 'Discharged', 508),

-- Recent Discharge #2: 5 days ago - Site 516
(1006, '2025-12-05 10:30:00', 53, 1002, 'I48.91',
 '2025-12-10 14:00:00', NULL, 53, 'I48.91', 'Atrial fibrillation with RVR', 'Home', 5, 'Discharged', 516),

-- Recent Discharge #3: 7 days ago - Site 552
(1007, '2025-12-01 13:00:00', 105, 1003, 'J44.1',
 '2025-12-08 11:00:00', NULL, 105, 'J44.1', 'COPD exacerbation', 'Home with O2', 7, 'Discharged', 552),

-- Recent Discharge #4: 10 days ago - Site 688
(1008, '2025-11-30 06:45:00', 157, 1003, 'E11.65',
 '2025-12-05 10:00:00', NULL, 157, 'E11.65', 'Diabetic foot ulcer', 'SNF', 5, 'Discharged', 688),

-- Recent Discharge #5: 12 days ago - Site 508
(1009, '2025-11-28 09:00:00', 1, 1003, 'S72.001A',
 '2025-12-03 15:00:00', NULL, 1, 'S72.001A', 'Hip fracture, s/p ORIF', 'Rehab', 5, 'Discharged', 508),

-- Recent Discharge #6: 15 days ago (same-day discharge) - Site 516 - EDGE CASE
(1010, '2025-11-30 08:00:00', 53, 1002, 'R10.9',
 '2025-11-30 18:00:00', NULL, 53, 'R10.9', 'Abdominal pain, observation', 'Home', 0, 'Discharged', 516),

-- Recent Discharge #7: 18 days ago (same-day discharge) - Site 552 - EDGE CASE
(1011, '2025-11-27 14:00:00', 105, 1003, 'R55',
 '2025-11-27 22:00:00', NULL, 105, 'R55', 'Syncope, observation', 'Home', 0, 'Discharged', 552),

-- Recent Discharge #8: 20 days ago - Site 688
(1012, '2025-11-25 11:00:00', 157, 1004, 'N18.3',
 '2025-11-25 15:00:00', NULL, 157, NULL, NULL, 'Home', 0, 'Discharged', 688),

-- Recent Discharge #9: 25 days ago - Site 508
(1013, '2025-11-20 16:00:00', 1, 1001, 'G89.29',
 '2025-11-24 10:00:00', NULL, 1, 'G89.29', 'Chronic pain management', 'Home', 4, 'Discharged', 508),

-- Recent Discharge #10: 28 days ago - Site 516
(1014, '2025-11-17 12:00:00', 53, 1002, 'I63.9',
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
(1001, '2025-11-08 10:00:00', 1, 1001, 'I50.9',
 '2025-11-10 14:00:00', NULL, 1, 'I50.9', 'CHF exacerbation', 'Home', 2, 'Discharged', 508),

-- Historical #2: 60 days ago - Site 516
(1016, '2025-10-16 08:30:00', 53, 1002, 'J96.01',
 '2025-10-20 16:00:00', NULL, 53, 'J96.01', 'Acute respiratory failure', 'Home with O2', 4, 'Discharged', 516),

-- Historical #3: 90 days ago - Site 552
(1017, '2025-09-16 14:00:00', 105, 1003, 'K80.00',
 '2025-09-19 11:00:00', NULL, 105, 'K80.00', 'Cholelithiasis, s/p cholecystectomy', 'Home', 3, 'Discharged', 552),

-- Historical #4: 120 days ago (Patient 1, admission #3) - Site 508
(1001, '2025-08-17 06:00:00', 1, 1003, 'I48.0',
 '2025-08-20 10:00:00', NULL, 1, 'I48.0', 'Atrial flutter, cardioversion', 'Home', 3, 'Discharged', 508),

-- Historical #5: 150 days ago - Site 688
(1018, '2025-07-18 13:00:00', 157, 1004, 'L03.115',
 '2025-07-23 15:00:00', NULL, 157, 'L03.115', 'Cellulitis of right lower extremity', 'Home', 5, 'Discharged', 688),

-- Historical #6: 180 days ago - Site 508
(1019, '2025-06-18 09:00:00', 1, 1003, 'M54.5',
 '2025-06-21 12:00:00', NULL, 1, NULL, NULL, 'Home', 3, 'Discharged', 508),

-- Historical #7: 210 days ago (Patient 1, admission #4) - Site 516
(1001, '2025-05-19 11:00:00', 53, 1002, 'N17.9',
 '2025-05-25 08:00:00', NULL, 53, 'N17.9', 'Acute kidney injury', 'Home', 6, 'Discharged', 516),

-- Historical #8: 240 days ago - Site 552
(1020, '2025-04-19 07:30:00', 105, 1003, 'F32.9',
 '2025-04-22 14:00:00', NULL, 105, 'F32.9', 'Major depressive disorder, stabilized', 'Home', 3, 'Discharged', 552),

-- Historical #9: 270 days ago - Site 688
(1021, '2025-03-20 15:00:00', 157, 1004, 'G40.909',
 '2025-03-24 10:00:00', NULL, 157, 'G40.909', 'Seizure disorder, medication adjustment', 'Home', 4, 'Discharged', 688),

-- Historical #10: 300 days ago (Patient 1, admission #5) - Site 508
(1001, '2025-02-18 08:00:00', 1, 1001, 'K56.60',
 '2025-02-23 16:00:00', NULL, 1, 'K56.60', 'Bowel obstruction, resolved', 'Home', 5, 'Discharged', 508),

-- Historical #11: 320 days ago - Site 516
(1022, '2025-01-29 10:00:00', 53, 1002, 'M25.511',
 '2025-02-02 11:00:00', NULL, 53, 'M25.511', 'Pain in right shoulder, PT', 'Home', 4, 'Discharged', 516),

-- Historical #12: 340 days ago - Site 552
(1023, '2025-01-09 12:00:00', 105, 1003, 'R00.0',
 '2025-01-11 09:00:00', NULL, 105, NULL, NULL, 'Home', 2, 'Discharged', 552),

-- Historical #13: 350 days ago - Site 508
(1024, '2024-12-30 14:00:00', 1, 1004, 'Z51.11',
 '2025-01-03 10:00:00', NULL, 1, 'Z51.11', 'Chemotherapy encounter', 'Home', 4, 'Discharged', 508),

-- Historical #14: 355 days ago - Site 516
(1025, '2024-12-25 06:00:00', 53, 1005, 'T84.050A',
 '2024-12-29 15:00:00', NULL, 53, 'T84.050A', 'Periprosthetic osteolysis', 'Rehab', 4, 'Discharged', 516),

-- Historical #15: 360 days ago (Patient 1, admission #6) - Site 552 (frequent readmissions)
(1001, '2024-12-20 09:00:00', 105, 1003, 'I50.9',
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
(1021, '2024-11-10 10:00:00', 1, 1, 'I25.10',
 '2024-11-15 12:00:00', NULL, 1, 'I25.10', 'CAD, s/p cardiac cath', 'Home', 5, 'Discharged', 508),

-- Old #2: 450 days ago - Site 516
(1022, '2024-09-21 08:00:00', 53, 2, 'M17.11',
 '2024-09-25 14:00:00', NULL, 53, 'M17.11', 'Osteoarthritis, s/p TKR', 'Rehab', 4, 'Discharged', 516),

-- Old #3: 500 days ago - Site 552
(1023, '2024-08-02 11:00:00', 105, 3, 'C34.90',
 '2024-08-08 16:00:00', NULL, 105, 'C34.90', 'Lung cancer, initiate treatment', 'Home', 6, 'Discharged', 552),

-- Old #4: 550 days ago - Site 688
(1024, '2024-06-13 09:00:00', 157, 4, 'I60.9',
 '2024-06-20 11:00:00', NULL, 157, 'I60.9', 'Subarachnoid hemorrhage, stabilized', 'SNF', 7, 'Discharged', 688),

-- Old #5: 600 days ago - Site 508
(1025, '2024-04-24 07:00:00', 1, 1, 'J81.0',
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
PRINT '  Patient 1001 (ICN100001): 6 admissions in first 35 records (frequent readmissions)';
PRINT '  Patients 1010, 1011: Same-day admit/discharge';
PRINT '  Patient 1015: Extended LOS >30 days (active)';
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
(1001, '2025-12-06 00:00:00', 6, 1006, 'I50.9',
 '2025-12-09 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 3, 'Discharged', 508),
(1001, '2025-12-02 00:00:00', 6, 1006, 'J44.1',
 '2025-12-05 00:00:00', NULL, 6, 'J44.1', 'COPD exacerbation', 'Home with O2', 3, 'Discharged', 516),
(1001, '2025-11-28 00:00:00', 6, 1006, 'I48.91',
 '2025-12-01 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 3, 'Discharged', 552),
(1001, '2025-11-24 00:00:00', 9, 1006, 'N17.9',
 '2025-11-27 00:00:00', NULL, 9, 'N17.9', 'Acute kidney injury', 'Rehab', 3, 'Discharged', 688),
(1001, '2025-11-20 00:00:00', 6, 1006, 'E11.65',
 '2025-11-23 00:00:00', NULL, 6, 'E11.65', 'Diabetic complications', 'Home', 3, 'Discharged', 508),
(1001, '2025-11-01 00:00:00', 6, 1006, 'I50.9',
 '2025-11-05 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 4, 'Discharged', 508),
(1001, '2025-10-12 00:00:00', 6, 1006, 'J44.1',
 '2025-10-16 00:00:00', NULL, 6, 'J44.1', 'COPD exacerbation', 'Home with O2', 4, 'Discharged', 516),
(1001, '2025-09-22 00:00:00', 6, 1006, 'I48.91',
 '2025-09-26 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 4, 'Discharged', 552),
(1001, '2025-09-02 00:00:00', 9, 1006, 'N17.9',
 '2025-09-06 00:00:00', NULL, 9, 'N17.9', 'Acute kidney injury', 'Rehab', 4, 'Discharged', 688),
(1001, '2025-08-13 00:00:00', 6, 1006, 'E11.65',
 '2025-08-17 00:00:00', NULL, 6, 'E11.65', 'Diabetic complications', 'Home', 4, 'Discharged', 508),
(1001, '2025-07-24 00:00:00', 6, 1006, 'K92.2',
 '2025-07-28 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'Home', 4, 'Discharged', 516),
(1001, '2025-07-04 00:00:00', 6, 1006, 'J18.9',
 '2025-07-08 00:00:00', NULL, 6, 'J18.9', 'Pneumonia', 'Home with O2', 4, 'Discharged', 552),
(1001, '2025-06-14 00:00:00', 9, 1006, 'I21.9',
 '2025-06-18 00:00:00', NULL, 9, 'I21.9', 'Acute MI', 'SNF', 4, 'Discharged', 688),
(1001, '2025-05-25 00:00:00', 6, 1006, 'G40.909',
 '2025-05-29 00:00:00', NULL, 6, 'G40.909', 'Seizure disorder', 'Rehab', 4, 'Discharged', 508),
(1001, '2025-05-05 00:00:00', 6, 1006, 'M54.5',
 '2025-05-09 00:00:00', NULL, 6, 'M54.5', 'Low back pain', 'Home', 4, 'Discharged', 516),
(1001, '2025-04-15 00:00:00', 6, 1006, 'I50.9',
 '2025-04-19 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 4, 'Discharged', 552),
(1001, '2025-03-26 00:00:00', 9, 1006, 'J44.1',
 '2025-03-30 00:00:00', NULL, 9, 'J44.1', 'COPD exacerbation', 'Home with O2', 4, 'Discharged', 688),
(1001, '2025-03-06 00:00:00', 6, 1006, 'I48.91',
 '2025-03-10 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 4, 'Discharged', 508),
(1001, '2025-02-14 00:00:00', 6, 1006, 'N17.9',
 '2025-02-18 00:00:00', NULL, 6, 'N17.9', 'Acute kidney injury', 'Rehab', 4, 'Discharged', 516),
(1001, '2025-01-25 00:00:00', 6, 1006, 'E11.65',
 '2025-01-29 00:00:00', NULL, 6, 'E11.65', 'Diabetic complications', 'Home', 4, 'Discharged', 552),
(1001, '2024-11-05 00:00:00', 6, 1006, 'I50.9',
 '2024-11-10 00:00:00', NULL, 6, 'I50.9', 'CHF exacerbation', 'Home', 5, 'Discharged', 508),
(1001, '2024-09-06 00:00:00', 6, 1006, 'J44.1',
 '2024-09-11 00:00:00', NULL, 6, 'J44.1', 'COPD exacerbation', 'Home with O2', 5, 'Discharged', 516),
(1001, '2024-07-08 00:00:00', 6, 1006, 'I48.91',
 '2024-07-13 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'SNF', 5, 'Discharged', 552),
(1001, '2024-05-09 00:00:00', 9, 1006, 'N17.9',
 '2024-05-14 00:00:00', NULL, 9, 'N17.9', 'Acute kidney injury', 'Rehab', 5, 'Discharged', 688);
GO

-- Additional encounters for Patient 4 (14 more)
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
(1004, '2025-12-04 00:00:00', 6, 1004, 'N17.9',
 '2025-12-07 00:00:00', NULL, 6, 'N17.9', 'Acute kidney injury', 'Home', 3, 'Discharged', 552),
(1004, '2025-11-29 00:00:00', 9, 1004, 'E11.65',
 '2025-12-02 00:00:00', NULL, 9, 'E11.65', 'Diabetic complications', 'Home with O2', 3, 'Discharged', 688),
(1004, '2025-11-24 00:00:00', 6, 1004, 'K92.2',
 '2025-11-27 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'SNF', 3, 'Discharged', 508),
(1004, '2025-10-22 00:00:00', 6, 1004, 'I48.91',
 '2025-10-26 00:00:00', NULL, 6, 'I48.91', 'Atrial fibrillation', 'Home', 4, 'Discharged', 516),
(1004, '2025-09-22 00:00:00', 6, 1004, 'N17.9',
 '2025-09-26 00:00:00', NULL, 6, 'N17.9', 'Acute kidney injury', 'Home with O2', 4, 'Discharged', 552),
(1004, '2025-08-23 00:00:00', 9, 1004, 'E11.65',
 '2025-08-27 00:00:00', NULL, 9, 'E11.65', 'Diabetic complications', 'SNF', 4, 'Discharged', 688),
(1004, '2025-07-24 00:00:00', 6, 1004, 'K92.2',
 '2025-07-28 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'Rehab', 4, 'Discharged', 508),
(1004, '2025-06-24 00:00:00', 6, 1004, 'J18.9',
 '2025-06-28 00:00:00', NULL, 6, 'J18.9', 'Pneumonia', 'Home', 4, 'Discharged', 516),
(1004, '2025-05-25 00:00:00', 6, 1004, 'I21.9',
 '2025-05-29 00:00:00', NULL, 6, 'I21.9', 'Acute MI', 'Home', 4, 'Discharged', 552),
(1004, '2025-04-25 00:00:00', 9, 1004, 'G40.909',
 '2025-04-29 00:00:00', NULL, 9, 'G40.909', 'Seizure disorder', 'Home with O2', 4, 'Discharged', 688),
(1004, '2025-03-26 00:00:00', 6, 1004, 'M54.5',
 '2025-03-30 00:00:00', NULL, 6, 'M54.5', 'Low back pain', 'SNF', 4, 'Discharged', 508),
(1004, '2024-10-16 00:00:00', 6, 1005, 'K92.2',
 '2024-10-21 00:00:00', NULL, 6, 'K92.2', 'GI bleed', 'Home', 5, 'Discharged', 508),
(1004, '2024-08-07 00:00:00', 6, 1005, 'J18.9',
 '2024-08-12 00:00:00', NULL, 6, 'J18.9', 'Pneumonia', 'Home with O2', 5, 'Discharged', 516),
(1004, '2024-05-29 00:00:00', 6, 1005, 'I21.9',
 '2024-06-03 00:00:00', NULL, 6, 'I21.9', 'Acute MI', 'SNF', 5, 'Discharged', 552);
GO

PRINT '';
PRINT '==== Added 38 Additional Encounters for Pagination Testing ====';
PRINT '  Patient 1001 (ICN100001): 24 more encounters (30 total)';
PRINT '  Patient 1004 (ICN100004): 14 more encounters (15 total)';
PRINT '';
PRINT '==== Total Dataset: 73 Encounters (Patients 1001-1026) ====';
GO

/*
|----------------------------------------------------------------------
| DECEASED PATIENT ENCOUNTERS
|----------------------------------------------------------------------
| Patient 1026: Margaret E Wilson - DECEASED 2024-12-01
| Final hospitalization with death during admission
|----------------------------------------------------------------------
*/

PRINT '';
PRINT 'Inserting encounter for Patient 1026 (Margaret Wilson - DECEASED)...';
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Patient 1026: Margaret E Wilson - Final hospitalization ending in death
-- Added 2026-02-04 - Admitted 2024-11-25 for acute decompensation, died 2024-12-01
-- Diagnosis: Multi-organ failure in setting of advanced CHF, COPD, DM2
-- Disposition: EXPIRED (death during hospitalization)
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
(1026, '2024-11-25 08:00:00', 1, 1001, 'I50.9',
 '2024-12-01 14:35:00', NULL, 1, 'R57.9',
 'Multi-organ failure, comfort care measures', 'EXPIRED', 6, 'Discharged', 508);
GO

PRINT '';
PRINT '==== Added 1 Encounter for Patient 1026 (Margaret Wilson - DECEASED) ====';
PRINT '  PatientSID 1026 (ICN100016): Final admission Nov 25 - Dec 1, 2024';
PRINT '  Disposition: EXPIRED (death during hospitalization)';
PRINT '';

-- Patient 1027: Robert J Anderson - Psychiatric hospitalizations and final ED visit
-- Added 2026-02-04 - Combat veteran with PTSD, MDD, substance use disorder
-- 3 psychiatric encounters including suicide attempt and final death

-- Encounter 1: 2019 suicide attempt
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
(1027, '2019-06-20 06:30:00', 2, 1004, 'T14.91XA',
 '2019-06-28 10:00:00', NULL, 2, 'F32.9',
 'Suicide attempt by overdose, Major Depressive Disorder, Acute stress reaction', 'TRANSFERRED TO MENTAL HEALTH UNIT', 8, 'Discharged', 528);
GO

-- Encounter 2: 2023 psychiatric stabilization
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
(1027, '2023-03-10 14:00:00', 2, 1004, 'F43.10',
 '2023-03-17 11:00:00', NULL, 2, 'F43.10',
 'PTSD exacerbation, Acute suicidal ideation with plan, Safety stabilization', 'HOME WITH OUTPATIENT FOLLOW-UP', 7, 'Discharged', 528);
GO

-- Encounter 3: 2024-11-15 final ED visit ending in death
INSERT INTO [Inpat].[Inpatient]
(PatientSID, AdmitDateTime, AdmitLocationSID, AdmittingProviderSID, AdmitDiagnosisICD10,
 DischargeDateTime, DischargeDateSID, DischargeWardLocationSID, DischargeDiagnosisICD10,
 DischargeDiagnosis, DischargeDisposition, LengthOfStay, EncounterStatus, Sta3n)
VALUES
(1027, '2024-11-15 07:00:00', 2, 1006, 'T14.91XA',
 '2024-11-15 08:30:00', NULL, 2, 'X71.9XXA',
 'Intentional self-harm, Suicide completed, Emergency resuscitation unsuccessful', 'EXPIRED', 0, 'Discharged', 528);
GO

PRINT '';
PRINT '==== Added 3 Encounters for Patient 1027 (Robert Anderson - DECEASED) ====';
PRINT '  PatientSID 1027 (ICN100017): 2019 suicide attempt, 2023 stabilization, 2024 death';
PRINT '  Disposition: EXPIRED (death in ED on Nov 15, 2024)';
PRINT '';
PRINT '==== Total Dataset: 77 Encounters (Patients 1001-1027) ====';
PRINT '';
PRINT '==== IMPORTANT FIX APPLIED (2026-02-04) ====';
PRINT '  All PatientSID values corrected from 1-30 to 1001-1026';
PRINT '  Data now correctly references existing patients in SPatient.SPatient';
GO

