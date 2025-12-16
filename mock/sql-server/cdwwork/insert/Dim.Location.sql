-- =============================================================================
-- Dim.Location - Location Dimension (INSERT)
-- =============================================================================
-- Purpose: Populate location dimension with realistic VA locations
-- Includes: Inpatient wards, Outpatient clinics, Emergency, Ancillary services
-- Stations: 508, 516, 552, 688 (4 VA facilities)
-- Strategy: Exact duplicates across all facilities (Option A)
-- =============================================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting location data into Dim.Location...';
GO

-- =============================================================================
-- STA3N 508 - VA MEDICAL CENTER
-- =============================================================================

PRINT 'Inserting locations for Sta3n 508...';
GO

-- Inpatient Wards
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor], [RoomNumber])
VALUES
('Medicine Ward 5A', 'Inpatient', 508, 'Main Hospital', '5', NULL),
('Medicine Ward 5B', 'Inpatient', 508, 'Main Hospital', '5', NULL),
('Medicine Ward 6A', 'Inpatient', 508, 'Main Hospital', '6', NULL),
('Surgery Ward 7A', 'Inpatient', 508, 'Main Hospital', '7', NULL),
('Surgery Ward 7B', 'Inpatient', 508, 'Main Hospital', '7', NULL),
('Medical ICU', 'Inpatient', 508, 'Main Hospital', '4', NULL),
('Surgical ICU', 'Inpatient', 508, 'Main Hospital', '4', NULL),
('Cardiac ICU', 'Inpatient', 508, 'Main Hospital', '4', NULL),
('Cardiology Ward 3A', 'Inpatient', 508, 'Main Hospital', '3', NULL),
('Oncology Ward 8A', 'Inpatient', 508, 'Main Hospital', '8', NULL),
('Neurology Ward 6B', 'Inpatient', 508, 'Main Hospital', '6', NULL),
('Psychiatry Ward 2A', 'Inpatient', 508, 'Building 2', '2', NULL);
GO

-- Outpatient Clinics
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Primary Care Clinic A', 'Outpatient', 508, 'Ambulatory Care', '1'),
('Primary Care Clinic B', 'Outpatient', 508, 'Ambulatory Care', '1'),
('Primary Care Clinic C', 'Outpatient', 508, 'Ambulatory Care', '1'),
('Cardiology Clinic', 'Outpatient', 508, 'Specialty Clinic', '2'),
('Endocrinology Clinic', 'Outpatient', 508, 'Specialty Clinic', '2'),
('Gastroenterology Clinic', 'Outpatient', 508, 'Specialty Clinic', '2'),
('Pulmonology Clinic', 'Outpatient', 508, 'Specialty Clinic', '3'),
('Nephrology Clinic', 'Outpatient', 508, 'Specialty Clinic', '3'),
('Oncology Clinic', 'Outpatient', 508, 'Specialty Clinic', '3'),
('Neurology Clinic', 'Outpatient', 508, 'Specialty Clinic', '3'),
('General Surgery Clinic', 'Outpatient', 508, 'Surgical Specialties', '1'),
('Orthopedics Clinic', 'Outpatient', 508, 'Surgical Specialties', '1'),
('Urology Clinic', 'Outpatient', 508, 'Surgical Specialties', '2'),
('Mental Health Clinic', 'Outpatient', 508, 'Mental Health', '1'),
('PTSD Clinic', 'Outpatient', 508, 'Mental Health', '2'),
('Physical Therapy', 'Outpatient', 508, 'Rehabilitation', '1'),
('Occupational Therapy', 'Outpatient', 508, 'Rehabilitation', '1');
GO

-- Emergency Department
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Emergency Department', 'Emergency', 508, 'Main Hospital', '1'),
('Emergency Department Triage', 'Emergency', 508, 'Main Hospital', '1'),
('Emergency Department Trauma Bay', 'Emergency', 508, 'Main Hospital', '1');
GO

-- Laboratory Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Laboratory - Main Lab', 'Laboratory', 508, 'Main Hospital', '1'),
('Laboratory - Phlebotomy Station A', 'Laboratory', 508, 'Ambulatory Care', '1'),
('Laboratory - Phlebotomy Station B', 'Laboratory', 508, 'Main Hospital', '1'),
('Laboratory - Point of Care Testing', 'Laboratory', 508, 'Main Hospital', '1');
GO

-- Radiology Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Radiology - X-Ray', 'Radiology', 508, 'Main Hospital', '1'),
('Radiology - CT Scan', 'Radiology', 508, 'Main Hospital', '1'),
('Radiology - MRI', 'Radiology', 508, 'Main Hospital', 'B1'),
('Radiology - Ultrasound', 'Radiology', 508, 'Main Hospital', '1'),
('Radiology - Nuclear Medicine', 'Radiology', 508, 'Main Hospital', 'B1');
GO

-- Pharmacy Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Pharmacy - Inpatient', 'Pharmacy', 508, 'Main Hospital', 'B1'),
('Pharmacy - Outpatient', 'Pharmacy', 508, 'Ambulatory Care', '1'),
('Pharmacy - Window Pickup', 'Pharmacy', 508, 'Ambulatory Care', '1');
GO

-- Other Ancillary Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Operating Room 1', 'Surgery', 508, 'Main Hospital', '2'),
('Operating Room 2', 'Surgery', 508, 'Main Hospital', '2'),
('Operating Room 3', 'Surgery', 508, 'Main Hospital', '2'),
('Post Anesthesia Care Unit', 'Surgery', 508, 'Main Hospital', '2'),
('Dialysis Center', 'Dialysis', 508, 'Specialty Clinic', '1'),
('Sleep Lab', 'Diagnostic', 508, 'Specialty Clinic', '2'),
('Endoscopy Suite', 'Procedure', 508, 'Main Hospital', '1'),
('Cardiac Catheterization Lab', 'Procedure', 508, 'Main Hospital', '3');
GO

-- =============================================================================
-- STA3N 516 - VA MEDICAL CENTER
-- =============================================================================

PRINT 'Inserting locations for Sta3n 516...';
GO

-- Inpatient Wards
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor], [RoomNumber])
VALUES
('Medicine Ward 5A', 'Inpatient', 516, 'Main Hospital', '5', NULL),
('Medicine Ward 5B', 'Inpatient', 516, 'Main Hospital', '5', NULL),
('Medicine Ward 6A', 'Inpatient', 516, 'Main Hospital', '6', NULL),
('Surgery Ward 7A', 'Inpatient', 516, 'Main Hospital', '7', NULL),
('Surgery Ward 7B', 'Inpatient', 516, 'Main Hospital', '7', NULL),
('Medical ICU', 'Inpatient', 516, 'Main Hospital', '4', NULL),
('Surgical ICU', 'Inpatient', 516, 'Main Hospital', '4', NULL),
('Cardiac ICU', 'Inpatient', 516, 'Main Hospital', '4', NULL),
('Cardiology Ward 3A', 'Inpatient', 516, 'Main Hospital', '3', NULL),
('Oncology Ward 8A', 'Inpatient', 516, 'Main Hospital', '8', NULL),
('Neurology Ward 6B', 'Inpatient', 516, 'Main Hospital', '6', NULL),
('Psychiatry Ward 2A', 'Inpatient', 516, 'Building 2', '2', NULL);
GO

-- Outpatient Clinics
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Primary Care Clinic A', 'Outpatient', 516, 'Ambulatory Care', '1'),
('Primary Care Clinic B', 'Outpatient', 516, 'Ambulatory Care', '1'),
('Primary Care Clinic C', 'Outpatient', 516, 'Ambulatory Care', '1'),
('Cardiology Clinic', 'Outpatient', 516, 'Specialty Clinic', '2'),
('Endocrinology Clinic', 'Outpatient', 516, 'Specialty Clinic', '2'),
('Gastroenterology Clinic', 'Outpatient', 516, 'Specialty Clinic', '2'),
('Pulmonology Clinic', 'Outpatient', 516, 'Specialty Clinic', '3'),
('Nephrology Clinic', 'Outpatient', 516, 'Specialty Clinic', '3'),
('Oncology Clinic', 'Outpatient', 516, 'Specialty Clinic', '3'),
('Neurology Clinic', 'Outpatient', 516, 'Specialty Clinic', '3'),
('General Surgery Clinic', 'Outpatient', 516, 'Surgical Specialties', '1'),
('Orthopedics Clinic', 'Outpatient', 516, 'Surgical Specialties', '1'),
('Urology Clinic', 'Outpatient', 516, 'Surgical Specialties', '2'),
('Mental Health Clinic', 'Outpatient', 516, 'Mental Health', '1'),
('PTSD Clinic', 'Outpatient', 516, 'Mental Health', '2'),
('Physical Therapy', 'Outpatient', 516, 'Rehabilitation', '1'),
('Occupational Therapy', 'Outpatient', 516, 'Rehabilitation', '1');
GO

-- Emergency Department
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Emergency Department', 'Emergency', 516, 'Main Hospital', '1'),
('Emergency Department Triage', 'Emergency', 516, 'Main Hospital', '1'),
('Emergency Department Trauma Bay', 'Emergency', 516, 'Main Hospital', '1');
GO

-- Laboratory Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Laboratory - Main Lab', 'Laboratory', 516, 'Main Hospital', '1'),
('Laboratory - Phlebotomy Station A', 'Laboratory', 516, 'Ambulatory Care', '1'),
('Laboratory - Phlebotomy Station B', 'Laboratory', 516, 'Main Hospital', '1'),
('Laboratory - Point of Care Testing', 'Laboratory', 516, 'Main Hospital', '1');
GO

-- Radiology Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Radiology - X-Ray', 'Radiology', 516, 'Main Hospital', '1'),
('Radiology - CT Scan', 'Radiology', 516, 'Main Hospital', '1'),
('Radiology - MRI', 'Radiology', 516, 'Main Hospital', 'B1'),
('Radiology - Ultrasound', 'Radiology', 516, 'Main Hospital', '1'),
('Radiology - Nuclear Medicine', 'Radiology', 516, 'Main Hospital', 'B1');
GO

-- Pharmacy Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Pharmacy - Inpatient', 'Pharmacy', 516, 'Main Hospital', 'B1'),
('Pharmacy - Outpatient', 'Pharmacy', 516, 'Ambulatory Care', '1'),
('Pharmacy - Window Pickup', 'Pharmacy', 516, 'Ambulatory Care', '1');
GO

-- Other Ancillary Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Operating Room 1', 'Surgery', 516, 'Main Hospital', '2'),
('Operating Room 2', 'Surgery', 516, 'Main Hospital', '2'),
('Operating Room 3', 'Surgery', 516, 'Main Hospital', '2'),
('Post Anesthesia Care Unit', 'Surgery', 516, 'Main Hospital', '2'),
('Dialysis Center', 'Dialysis', 516, 'Specialty Clinic', '1'),
('Sleep Lab', 'Diagnostic', 516, 'Specialty Clinic', '2'),
('Endoscopy Suite', 'Procedure', 516, 'Main Hospital', '1'),
('Cardiac Catheterization Lab', 'Procedure', 516, 'Main Hospital', '3');
GO

-- =============================================================================
-- STA3N 552 - VA MEDICAL CENTER
-- =============================================================================

PRINT 'Inserting locations for Sta3n 552...';
GO

-- Inpatient Wards
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor], [RoomNumber])
VALUES
('Medicine Ward 5A', 'Inpatient', 552, 'Main Hospital', '5', NULL),
('Medicine Ward 5B', 'Inpatient', 552, 'Main Hospital', '5', NULL),
('Medicine Ward 6A', 'Inpatient', 552, 'Main Hospital', '6', NULL),
('Surgery Ward 7A', 'Inpatient', 552, 'Main Hospital', '7', NULL),
('Surgery Ward 7B', 'Inpatient', 552, 'Main Hospital', '7', NULL),
('Medical ICU', 'Inpatient', 552, 'Main Hospital', '4', NULL),
('Surgical ICU', 'Inpatient', 552, 'Main Hospital', '4', NULL),
('Cardiac ICU', 'Inpatient', 552, 'Main Hospital', '4', NULL),
('Cardiology Ward 3A', 'Inpatient', 552, 'Main Hospital', '3', NULL),
('Oncology Ward 8A', 'Inpatient', 552, 'Main Hospital', '8', NULL),
('Neurology Ward 6B', 'Inpatient', 552, 'Main Hospital', '6', NULL),
('Psychiatry Ward 2A', 'Inpatient', 552, 'Building 2', '2', NULL);
GO

-- Outpatient Clinics
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Primary Care Clinic A', 'Outpatient', 552, 'Ambulatory Care', '1'),
('Primary Care Clinic B', 'Outpatient', 552, 'Ambulatory Care', '1'),
('Primary Care Clinic C', 'Outpatient', 552, 'Ambulatory Care', '1'),
('Cardiology Clinic', 'Outpatient', 552, 'Specialty Clinic', '2'),
('Endocrinology Clinic', 'Outpatient', 552, 'Specialty Clinic', '2'),
('Gastroenterology Clinic', 'Outpatient', 552, 'Specialty Clinic', '2'),
('Pulmonology Clinic', 'Outpatient', 552, 'Specialty Clinic', '3'),
('Nephrology Clinic', 'Outpatient', 552, 'Specialty Clinic', '3'),
('Oncology Clinic', 'Outpatient', 552, 'Specialty Clinic', '3'),
('Neurology Clinic', 'Outpatient', 552, 'Specialty Clinic', '3'),
('General Surgery Clinic', 'Outpatient', 552, 'Surgical Specialties', '1'),
('Orthopedics Clinic', 'Outpatient', 552, 'Surgical Specialties', '1'),
('Urology Clinic', 'Outpatient', 552, 'Surgical Specialties', '2'),
('Mental Health Clinic', 'Outpatient', 552, 'Mental Health', '1'),
('PTSD Clinic', 'Outpatient', 552, 'Mental Health', '2'),
('Physical Therapy', 'Outpatient', 552, 'Rehabilitation', '1'),
('Occupational Therapy', 'Outpatient', 552, 'Rehabilitation', '1');
GO

-- Emergency Department
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Emergency Department', 'Emergency', 552, 'Main Hospital', '1'),
('Emergency Department Triage', 'Emergency', 552, 'Main Hospital', '1'),
('Emergency Department Trauma Bay', 'Emergency', 552, 'Main Hospital', '1');
GO

-- Laboratory Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Laboratory - Main Lab', 'Laboratory', 552, 'Main Hospital', '1'),
('Laboratory - Phlebotomy Station A', 'Laboratory', 552, 'Ambulatory Care', '1'),
('Laboratory - Phlebotomy Station B', 'Laboratory', 552, 'Main Hospital', '1'),
('Laboratory - Point of Care Testing', 'Laboratory', 552, 'Main Hospital', '1');
GO

-- Radiology Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Radiology - X-Ray', 'Radiology', 552, 'Main Hospital', '1'),
('Radiology - CT Scan', 'Radiology', 552, 'Main Hospital', '1'),
('Radiology - MRI', 'Radiology', 552, 'Main Hospital', 'B1'),
('Radiology - Ultrasound', 'Radiology', 552, 'Main Hospital', '1'),
('Radiology - Nuclear Medicine', 'Radiology', 552, 'Main Hospital', 'B1');
GO

-- Pharmacy Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Pharmacy - Inpatient', 'Pharmacy', 552, 'Main Hospital', 'B1'),
('Pharmacy - Outpatient', 'Pharmacy', 552, 'Ambulatory Care', '1'),
('Pharmacy - Window Pickup', 'Pharmacy', 552, 'Ambulatory Care', '1');
GO

-- Other Ancillary Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Operating Room 1', 'Surgery', 552, 'Main Hospital', '2'),
('Operating Room 2', 'Surgery', 552, 'Main Hospital', '2'),
('Operating Room 3', 'Surgery', 552, 'Main Hospital', '2'),
('Post Anesthesia Care Unit', 'Surgery', 552, 'Main Hospital', '2'),
('Dialysis Center', 'Dialysis', 552, 'Specialty Clinic', '1'),
('Sleep Lab', 'Diagnostic', 552, 'Specialty Clinic', '2'),
('Endoscopy Suite', 'Procedure', 552, 'Main Hospital', '1'),
('Cardiac Catheterization Lab', 'Procedure', 552, 'Main Hospital', '3');
GO

-- =============================================================================
-- STA3N 688 - VA MEDICAL CENTER
-- =============================================================================

PRINT 'Inserting locations for Sta3n 688...';
GO

-- Inpatient Wards
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor], [RoomNumber])
VALUES
('Medicine Ward 5A', 'Inpatient', 688, 'Main Hospital', '5', NULL),
('Medicine Ward 5B', 'Inpatient', 688, 'Main Hospital', '5', NULL),
('Medicine Ward 6A', 'Inpatient', 688, 'Main Hospital', '6', NULL),
('Surgery Ward 7A', 'Inpatient', 688, 'Main Hospital', '7', NULL),
('Surgery Ward 7B', 'Inpatient', 688, 'Main Hospital', '7', NULL),
('Medical ICU', 'Inpatient', 688, 'Main Hospital', '4', NULL),
('Surgical ICU', 'Inpatient', 688, 'Main Hospital', '4', NULL),
('Cardiac ICU', 'Inpatient', 688, 'Main Hospital', '4', NULL),
('Cardiology Ward 3A', 'Inpatient', 688, 'Main Hospital', '3', NULL),
('Oncology Ward 8A', 'Inpatient', 688, 'Main Hospital', '8', NULL),
('Neurology Ward 6B', 'Inpatient', 688, 'Main Hospital', '6', NULL),
('Psychiatry Ward 2A', 'Inpatient', 688, 'Building 2', '2', NULL);
GO

-- Outpatient Clinics
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Primary Care Clinic A', 'Outpatient', 688, 'Ambulatory Care', '1'),
('Primary Care Clinic B', 'Outpatient', 688, 'Ambulatory Care', '1'),
('Primary Care Clinic C', 'Outpatient', 688, 'Ambulatory Care', '1'),
('Cardiology Clinic', 'Outpatient', 688, 'Specialty Clinic', '2'),
('Endocrinology Clinic', 'Outpatient', 688, 'Specialty Clinic', '2'),
('Gastroenterology Clinic', 'Outpatient', 688, 'Specialty Clinic', '2'),
('Pulmonology Clinic', 'Outpatient', 688, 'Specialty Clinic', '3'),
('Nephrology Clinic', 'Outpatient', 688, 'Specialty Clinic', '3'),
('Oncology Clinic', 'Outpatient', 688, 'Specialty Clinic', '3'),
('Neurology Clinic', 'Outpatient', 688, 'Specialty Clinic', '3'),
('General Surgery Clinic', 'Outpatient', 688, 'Surgical Specialties', '1'),
('Orthopedics Clinic', 'Outpatient', 688, 'Surgical Specialties', '1'),
('Urology Clinic', 'Outpatient', 688, 'Surgical Specialties', '2'),
('Mental Health Clinic', 'Outpatient', 688, 'Mental Health', '1'),
('PTSD Clinic', 'Outpatient', 688, 'Mental Health', '2'),
('Physical Therapy', 'Outpatient', 688, 'Rehabilitation', '1'),
('Occupational Therapy', 'Outpatient', 688, 'Rehabilitation', '1');
GO

-- Emergency Department
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Emergency Department', 'Emergency', 688, 'Main Hospital', '1'),
('Emergency Department Triage', 'Emergency', 688, 'Main Hospital', '1'),
('Emergency Department Trauma Bay', 'Emergency', 688, 'Main Hospital', '1');
GO

-- Laboratory Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Laboratory - Main Lab', 'Laboratory', 688, 'Main Hospital', '1'),
('Laboratory - Phlebotomy Station A', 'Laboratory', 688, 'Ambulatory Care', '1'),
('Laboratory - Phlebotomy Station B', 'Laboratory', 688, 'Main Hospital', '1'),
('Laboratory - Point of Care Testing', 'Laboratory', 688, 'Main Hospital', '1');
GO

-- Radiology Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Radiology - X-Ray', 'Radiology', 688, 'Main Hospital', '1'),
('Radiology - CT Scan', 'Radiology', 688, 'Main Hospital', '1'),
('Radiology - MRI', 'Radiology', 688, 'Main Hospital', 'B1'),
('Radiology - Ultrasound', 'Radiology', 688, 'Main Hospital', '1'),
('Radiology - Nuclear Medicine', 'Radiology', 688, 'Main Hospital', 'B1');
GO

-- Pharmacy Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Pharmacy - Inpatient', 'Pharmacy', 688, 'Main Hospital', 'B1'),
('Pharmacy - Outpatient', 'Pharmacy', 688, 'Ambulatory Care', '1'),
('Pharmacy - Window Pickup', 'Pharmacy', 688, 'Ambulatory Care', '1');
GO

-- Other Ancillary Services
INSERT INTO [Dim].[Location] ([LocationName], [LocationType], [Sta3n], [BuildingName], [Floor])
VALUES
('Operating Room 1', 'Surgery', 688, 'Main Hospital', '2'),
('Operating Room 2', 'Surgery', 688, 'Main Hospital', '2'),
('Operating Room 3', 'Surgery', 688, 'Main Hospital', '2'),
('Post Anesthesia Care Unit', 'Surgery', 688, 'Main Hospital', '2'),
('Dialysis Center', 'Dialysis', 688, 'Specialty Clinic', '1'),
('Sleep Lab', 'Diagnostic', 688, 'Specialty Clinic', '2'),
('Endoscopy Suite', 'Procedure', 688, 'Main Hospital', '1'),
('Cardiac Catheterization Lab', 'Procedure', 688, 'Main Hospital', '3');
GO

-- =============================================================================
-- VERIFICATION
-- =============================================================================

PRINT 'Location data inserted successfully.';
GO

PRINT 'Verification by Sta3n and LocationType:';
SELECT
    Sta3n,
    LocationType,
    COUNT(*) AS LocationCount
FROM Dim.Location
GROUP BY Sta3n, LocationType
ORDER BY Sta3n, LocationType;
GO

PRINT 'Summary by Sta3n:';
SELECT
    Sta3n,
    COUNT(*) AS TotalLocations
FROM Dim.Location
GROUP BY Sta3n
ORDER BY Sta3n;
GO

SELECT COUNT(*) AS GrandTotalLocations FROM Dim.Location;
GO

PRINT 'Dim.Location data load complete (4 facilities).';
GO
