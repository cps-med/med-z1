-----------------------------------------------------------------------
-- VeteranMill.SPerson.sql (INSERT)
-- Populate demo patients for Oracle Health (Cerner)
-- Phase 1: Adam Dooree and Alexander Aminor
-----------------------------------------------------------------------
-- Identity Mapping:
--   Adam Dooree: CDWWork PatientSID 1001 → CDWWork2 PersonSID 2001, ICN100001
--   Alexander Aminor: CDWWork PatientSID 1010 → CDWWork2 PersonSID 2010, ICN100010
--
-- Note: PersonSID differs from CDWWork PatientSID to simulate real-world
-- scenario where different EHR systems use different internal IDs.
-- PatientICN is the shared identity key for cross-database joins.
-----------------------------------------------------------------------

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
SET IDENTITY_INSERT VeteranMill.SPerson ON;
GO

PRINT 'Populating VeteranMill.SPerson with demo patients...';
GO

-- =======================================================================
-- Demo Patient 1: Adam Dooree
-- =======================================================================
-- Background: 45-year-old male veteran with diabetes and hypertension
-- Historical care at Atlanta VAMC (VistA) - CDWWork PatientSID 1001
-- Current care at Portland VAMC (Cerner) - CDWWork2 PersonSID 2001
-- Relocated to Portland in mid-2024
-----------------------------------------------------------------------

INSERT INTO VeteranMill.SPerson (
    PersonSID,
    PatientICN,
    LastName,
    FirstName,
    MiddleName,
    BirthDate,
    Gender,
    SSN,
    HomePhone,
    Email,
    StreetAddress,
    City,
    State,
    ZipCode,
    IsActive,
    CreatedDate,
    LastUpdatedDate
)
VALUES (
    2001,                               -- PersonSID (Cerner-specific)
    'ICN100001',                        -- Shared ICN with CDWWork
    'Dooree',
    'Adam',
    'James',
    '1980-01-02',                       -- Age 45
    'M',
    '123-45-1001',
    '503-555-0101',
    'adam.dooree@example.com',
    '1234 NW Portland Ave',
    'Portland',
    'OR',
    '97209',
    1,                                  -- Active
    '2024-06-15 08:30:00',             -- Enrolled at Portland in June 2024
    '2024-12-20 14:22:00'
);

PRINT '  - Inserted Adam Dooree (ICN100001, PersonSID 2001)';

-- =======================================================================
-- Demo Patient 2: Alexander Aminor
-- =======================================================================
-- Background: 59-year-old male veteran, post-Vietnam service
-- Historical care at Dayton VAMC (VistA) - CDWWork PatientSID 1010
-- Current care at Seattle VAMC (Cerner) - CDWWork2 PersonSID 2010
-- Relocated to Seattle in late 2024
-----------------------------------------------------------------------

INSERT INTO VeteranMill.SPerson (
    PersonSID,
    PatientICN,
    LastName,
    FirstName,
    MiddleName,
    BirthDate,
    Gender,
    SSN,
    HomePhone,
    Email,
    StreetAddress,
    City,
    State,
    ZipCode,
    IsActive,
    CreatedDate,
    LastUpdatedDate
)
VALUES (
    2010,                               -- PersonSID (Cerner-specific)
    'ICN100010',                        -- Shared ICN with CDWWork
    'Aminor',
    'Alexander',
    'Lee',
    '1966-03-15',                       -- Age 59
    'M',
    '234-56-1010',
    '206-555-0110',
    'alex.aminor@example.com',
    '5678 Capitol Hill Blvd',
    'Seattle',
    'WA',
    '98102',
    1,                                  -- Active
    '2024-09-10 10:15:00',             -- Enrolled at Seattle in September 2024
    '2024-12-18 09:45:00'
);

PRINT '  - Inserted Alexander Aminor (ICN100010, PersonSID 2010)';

SET IDENTITY_INSERT VeteranMill.SPerson OFF;
GO

-- =======================================================================
-- Verification
-- =======================================================================

PRINT '';
PRINT 'Patient population complete:';
SELECT PersonSID, PatientICN, LastName, FirstName, BirthDate, Gender, City, State
FROM VeteranMill.SPerson
ORDER BY PersonSID;

PRINT '';
PRINT 'Total patients inserted:';
SELECT COUNT(*) AS TotalPatients FROM VeteranMill.SPerson;
GO
