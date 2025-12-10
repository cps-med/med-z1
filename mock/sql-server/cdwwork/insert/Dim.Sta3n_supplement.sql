/*
|--------------------------------------------------------------------------------
| Insert: Dim.Sta3n_supplement.sql
|--------------------------------------------------------------------------------
| Supplement Dim.Sta3n with additional stations used in patient flags data
| Run this AFTER the main Dim.Sta3n.sql insert script
|--------------------------------------------------------------------------------
*/

PRINT '==== Dim.Sta3n Supplement (Patient Flags) ====';
GO

-- set the active database
USE CDWWork;
GO

-- Add missing stations referenced in patient flags data
INSERT INTO Dim.Sta3n
(
    Sta3n, Sta3nName, VISNPreFY15, VISNFY16, VISNFY17, Active, NextSta3n, TimeZone, SiteCode, RegionFY15, DistrictNameFY16, DistrictNumberFY16, DistrictNameFY17, DistrictNumberFY17, City, StateSID
)
VALUES
-- Station 518 - Northport (Long Island)
(518, '(518) Northport VA Medical Center', 2, 2, 2, 'Y', NULL, 'Eastern Standard Time', 'NOR', 4, 'North Atlantic', 1, 'North Atlantic', 1, 'Northport', 57),

-- Station 589 - VA Western Colorado HCS (Grand Junction)
(589, '(589) VA Western Colorado HCS (Wichita KS)', 15, 15, 15, 'Y', NULL, 'Central Standard Time', 'WIC', 2, 'Midwest', 3, 'Midwest', 3, 'Wichita', 226),

-- Station 640 - VA Palo Alto HCS (Palo Alto, CA)
(640, '(640) VA Palo Alto HCS', 21, 21, 21, 'Y', NULL, 'Pacific Standard Time', 'PAL', 1, 'Pacific', 5, 'Pacific', 5, 'Palo Alto', 97);

GO

PRINT 'Supplement complete - 3 stations added';
GO
