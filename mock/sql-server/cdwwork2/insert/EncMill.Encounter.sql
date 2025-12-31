-----------------------------------------------------------------------
-- EncMill.Encounter.sql (INSERT)
-- Populate encounters for demo patients at Cerner sites
-- Phase 1: 5-10 encounters per patient (Adam at Portland, Alexander at Seattle)
-----------------------------------------------------------------------

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
SET IDENTITY_INSERT EncMill.Encounter ON;
GO

PRINT 'Populating EncMill.Encounter with demo patient encounters...';
GO

-- =======================================================================
-- Adam Dooree Encounters at Portland VAMC (648)
-- =======================================================================
-- Enrolled: June 2024
-- Encounters: Mix of outpatient visits and 1 inpatient admission
-----------------------------------------------------------------------

-- Encounter 1: Initial enrollment visit (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3001, 2001, 'ICN100001', '648', 'Portland VAMC',
    'OUTPATIENT', '2024-06-15 08:30:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Sarah Chen', 1, '2024-06-15 08:30:00'
);

-- Encounter 2: Follow-up diabetes management (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3002, 2001, 'ICN100001', '648', 'Portland VAMC',
    'OUTPATIENT', '2024-07-22 10:15:00', 'Endocrinology Clinic', 'CLINIC',
    'Dr. Michael Wong', 1, '2024-07-22 10:15:00'
);

-- Encounter 3: Hypertension check (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3003, 2001, 'ICN100001', '648', 'Portland VAMC',
    'OUTPATIENT', '2024-08-10 14:00:00', 'Cardiology Clinic', 'CLINIC',
    'Dr. Jennifer Martinez', 1, '2024-08-10 14:00:00'
);

-- Encounter 4: Inpatient admission for diabetic management
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, AdmitDate, DischargeDate,
    LocationName, LocationType, ProviderName, IsActive, CreatedDate
)
VALUES (
    3004, 2001, 'ICN100001', '648', 'Portland VAMC',
    'INPATIENT', '2024-09-05 16:45:00', '2024-09-05 16:45:00', '2024-09-08 11:30:00',
    'Medical Ward 3B', 'WARD', 'Dr. Robert Johnson', 1, '2024-09-05 16:45:00'
);

-- Encounter 5: Post-discharge follow-up (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3005, 2001, 'ICN100001', '648', 'Portland VAMC',
    'OUTPATIENT', '2024-09-18 09:30:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Sarah Chen', 1, '2024-09-18 09:30:00'
);

-- Encounter 6: Routine diabetes check (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3006, 2001, 'ICN100001', '648', 'Portland VAMC',
    'OUTPATIENT', '2024-10-15 11:00:00', 'Endocrinology Clinic', 'CLINIC',
    'Dr. Michael Wong', 1, '2024-10-15 11:00:00'
);

-- Encounter 7: Medication review (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3007, 2001, 'ICN100001', '648', 'Portland VAMC',
    'OUTPATIENT', '2024-11-12 13:45:00', 'Pharmacy Clinic', 'CLINIC',
    'PharmD Lisa Thompson', 1, '2024-11-12 13:45:00'
);

-- Encounter 8: Annual physical exam (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3008, 2001, 'ICN100001', '648', 'Portland VAMC',
    'OUTPATIENT', '2024-12-10 08:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Sarah Chen', 1, '2024-12-10 08:00:00'
);

PRINT '  - Inserted 8 encounters for Adam Dooree at Portland VAMC (648)';

-- =======================================================================
-- Alexander Aminor Encounters at Seattle VAMC (663)
-- =======================================================================
-- Enrolled: September 2024
-- Encounters: Mix of outpatient visits and 1 inpatient admission
-----------------------------------------------------------------------

-- Encounter 1: Initial enrollment visit (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3011, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'OUTPATIENT', '2024-09-10 10:15:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Emily Rodriguez', 1, '2024-09-10 10:15:00'
);

-- Encounter 2: Follow-up general health (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3012, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'OUTPATIENT', '2024-09-25 14:30:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Emily Rodriguez', 1, '2024-09-25 14:30:00'
);

-- Encounter 3: Specialty cardiology visit (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3013, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'OUTPATIENT', '2024-10-08 09:00:00', 'Cardiology Clinic', 'CLINIC',
    'Dr. Thomas Lee', 1, '2024-10-08 09:00:00'
);

-- Encounter 4: Inpatient admission for chest pain evaluation
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, AdmitDate, DischargeDate,
    LocationName, LocationType, ProviderName, IsActive, CreatedDate
)
VALUES (
    3014, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'INPATIENT', '2024-10-22 18:30:00', '2024-10-22 18:30:00', '2024-10-25 10:00:00',
    'Cardiac Care Unit', 'WARD', 'Dr. Thomas Lee', 1, '2024-10-22 18:30:00'
);

-- Encounter 5: Post-discharge cardiology follow-up (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3015, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'OUTPATIENT', '2024-11-05 11:15:00', 'Cardiology Clinic', 'CLINIC',
    'Dr. Thomas Lee', 1, '2024-11-05 11:15:00'
);

-- Encounter 6: Routine primary care visit (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3016, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'OUTPATIENT', '2024-11-20 13:00:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Emily Rodriguez', 1, '2024-11-20 13:00:00'
);

-- Encounter 7: Medication management (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3017, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'OUTPATIENT', '2024-12-03 10:30:00', 'Pharmacy Clinic', 'CLINIC',
    'PharmD David Kim', 1, '2024-12-03 10:30:00'
);

-- Encounter 8: Recent primary care visit (Outpatient)
INSERT INTO EncMill.Encounter (
    EncounterSID, PersonSID, PatientICN, Sta3n, FacilityName,
    EncounterType, EncounterDate, LocationName, LocationType,
    ProviderName, IsActive, CreatedDate
)
VALUES (
    3018, 2010, 'ICN100010', '663', 'Seattle VAMC',
    'OUTPATIENT', '2024-12-18 09:45:00', 'Primary Care Clinic', 'CLINIC',
    'Dr. Emily Rodriguez', 1, '2024-12-18 09:45:00'
);

PRINT '  - Inserted 8 encounters for Alexander Aminor at Seattle VAMC (663)';

SET IDENTITY_INSERT EncMill.Encounter OFF;
GO

-- =======================================================================
-- Verification
-- =======================================================================

PRINT '';
PRINT 'Encounter population complete:';
SELECT
    e.EncounterSID,
    p.LastName + ', ' + p.FirstName AS PatientName,
    e.PatientICN,
    e.Sta3n,
    e.EncounterType,
    CONVERT(VARCHAR, e.EncounterDate, 120) AS EncounterDate,
    e.LocationName
FROM EncMill.Encounter e
JOIN VeteranMill.SPerson p ON e.PersonSID = p.PersonSID
ORDER BY e.PersonSID, e.EncounterDate;

PRINT '';
PRINT 'Encounter summary by patient:';
SELECT
    p.LastName + ', ' + p.FirstName AS PatientName,
    e.PatientICN,
    e.Sta3n,
    COUNT(*) AS EncounterCount
FROM EncMill.Encounter e
JOIN VeteranMill.SPerson p ON e.PersonSID = p.PersonSID
GROUP BY p.LastName, p.FirstName, e.PatientICN, e.Sta3n
ORDER BY p.LastName;
GO
