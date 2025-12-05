/*
|--------------------------------------------------------------------------------
| Insert: Dim.Sta3n.sql
|--------------------------------------------------------------------------------
| Insert sample data into table:  Dim_Sta3n
|
*/

PRINT '==== Dim.Station ====';
GO

-- set the active database
USE CDWWork;
GO

-- insert data into Dim.Sta3n table
INSERT INTO Dim.Sta3n
(
    Sta3n, Sta3nName, VISNPreFY15, VISNFY16, VISNFY17, Active, NextSta3n, TimeZone, SiteCode, RegionFY15, DistrictNameFY16, DistrictNumberFY16, DistrictNameFY17, DistrictNumberFY17, City, StateSID
)
VALUES
(528, '(528) Upstate New York HCS', 2, 2, 2, 'Y', NULL, 'Eastern Standard Time', 'ALN', 4, 'North Atlantic', 1, 'North Atlantic', 1, ' Albany', 57),
(503, '(503) Altoona, PA', 4, 4, 4, 'Y', NULL, 'Eastern Standard Time', 'ALT', 4, 'North Atlantic', 1, 'North Atlantic', 1, ' Altoona', 97),
(506, '(506) Ann Arbor, MI', 11, 10, 10, 'Y', NULL, 'Eastern Standard Time', 'ANN', 3, 'Midwest', 3, 'Midwest', 3, ' Ann Arbor', 226),
(508, '(508) Atlanta, GA', 7, 7, 7, 'Y', NULL, 'Eastern Standard Time', 'ATG', 3, 'Southeast', 2, 'Southeast', 2, ' Decatur', 415),
(405, '(405) White River Junction, VT', 1, 1, 1, 'Y', NULL, 'Eastern Standard Time', 'WRJ', 4, 'North Atlantic', 1, 'North Atlantic', 1, ' White River Junction', 1462),
(512, '(512) Maryland HCS (Baltimore MD)', 5, 5, 5, 'Y', NULL, 'Eastern Standard Time', 'BAL', 4, 'North Atlantic', 1, 'North Atlantic', 1, ' Baltimore', 1617),
(515, '(515) Battle Creek, MI', 11, 10, 10, 'Y', NULL, 'Eastern Standard Time', 'BAC', 3, 'Midwest', 3, 'Midwest', 3, ' Battle Creek', 1697),
(516, '(516) Bay Pines, FL', 8, 8, 8, 'Y', NULL, 'Eastern Standard Time', 'BAY', 3, 'Southeast', 2, 'Southeast', 2, ' Bay Pines', 1792),
(626, '(626) Tennessee Valley HCS (Nashville TN)', 9, 9, 9, 'Y', NULL, 'Central Standard Time', 'TVH', 3, 'Southeast', 2, 'Southeast', 2, ' Nashville', 2726),
(442, '(442) Cheyenne, WY', 19, 19, 19, 'Y', NULL, 'Mountain Standard Time', 'CHY', 1, 'Continental', 4, 'Continental', 4, ' Cheyenne', 4331),
(575, '(575) Grand Junction, CO', 19, 19, 19, 'Y', NULL, 'Mountain Standard Time', 'GRJ', 1, 'Continental', 4, 'Continental', 4, ' Grand Junction', 4568),
(552, '(552) Dayton, OH', 10, 10, 10, 'Y', NULL, 'Eastern Standard Time', 'DAY', 3, 'Midwest', 3, 'Midwest', 3, ' Dayton', 4963),
(578, '(578) Hines, IL', 12, 12, 12, 'Y', NULL, 'Central Standard Time', 'HIN', 2, 'Midwest', 3, 'Midwest', 3, ' Chicago', 5702),
(660, '(660) Salt Lake City HCS (Salt Lake City UT)', 19, 19, 19, 'Y', NULL, 'Mountain Standard Time', 'SLC', 1, 'Continental', 4, 'Continental', 4, ' Salt Lake City', 5787),
(688, '(688) Washington, DC', 5, 5, 5, 'Y', NULL, 'Eastern Standard Time', 'WAS', 4, 'North Atlantic', 1, 'North Atlantic', 1, ' Washington', 7262),
(663, '(663) Puget Sound HCS (Seattle WA) (CACHE 5.0)', 20, 20, 20, 'Y', NULL, 'Pacific Standard Time', 'PUG', 1, 'Pacific', 5, 'Pacific', 5, ' Seattle', 7394),
(668, '(668) Spokane, WA', 20, 20, 20, 'Y', NULL, 'Pacific Standard Time', 'SPO', 1, 'Pacific', 5, 'Pacific', 5, ' Spokane', 8913),
(687, '(687) Walla Walla, WA', 20, 20, 20, 'Y', NULL, 'Pacific Standard Time', 'WWW', 1, 'Pacific', 5, 'Pacific', 5, ' Walla Walla', 8992),
(670, '(670) Syracuse, NY (inactivated 4/1/2000)', 2, 2, 2, 'N', 528, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL),
(677, '(677) Topeka, KS', 15, 15, 15, 'N', 589, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL),
(622, '(622) Murfreesboro, TN', 9, 9, 9, 'N', 626, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL),
(532, '(532) Canandaigua, NY (inactivated 10/1/1999)', 2, 2, 2, 'N', 528, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL),
(647, '(647) Poplar Bluff, MO', 15, 15, 15, 'N', 657, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL),
(500, '(500) Albany (inactivated 7/1/2000)', 2, 2, 2, 'N', 528, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL),
(452, '(452) Wichita (inactivated 10/1/2001)', 15, 15, 15, 'N', 589, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL);
GO
