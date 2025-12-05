---------------------------------------------------------------------
-- Dim.Division.sql
-- Insert test data
-- DivisionSID => 2001 series
---------------------------------------------------------------------

PRINT '==== Dim.Division ====';
GO

-- set the active database
USE CDWWork;
GO

-- insert data into Dim.Sta3n table
INSERT INTO Dim.Division
(
    DivisionSID, DivisionIEN, Sta3n, DivisionName, InstitutionSID, Sta6a
)
VALUES
(2001, '1',  508, 'ATLANTA VAMC',                     21066,      '508'),
(2002, '1',  516, 'BAY PINES',                        65664,      '516'),
(2003, '1',  552, 'DAYTON',                           134399,     '552'),
(2004, '1',  575, 'GRAND JUNCTION',                   582563,     '575'),
(2005, '10', 508, 'NEWNAN CBOC',                      733718,     '508GI'),
(2006, '10', 552, 'WRIGHT PATTERSON AFB',             134522,     '552GF'),
(2007, '10', 575, 'GRAND JUNCTION 28 ROAD VA CLINIC', 800131985,  '575QD'),
(2008, '11', 575, 'GRAND JUNCTION VA DOMICILIARY',    1600011539, '575BU'),
(2009, '11', 508, 'BLAIRSVILLE CBOC',                 756307,     '508GJ'),
(2010, '11', 516, 'HIGHLANDS CBOC',                   48055,      '516GH'),
(2011, '14', 508, 'ATLANTA DOM',                      1200013927, '508BU'),
(2012, '15', 508, 'ATLANTA VA COMM LIVING CTR',       30323,      '5089AA'),
(2013, '5',  516, 'ST. PETERSBURG CBOC',              40663,      '516GB'),
(2014, '7',  552, 'IDES WRIGHT PATTERSON AFB',        1200006021, '552MA'),
(2015, '7',  508, 'LAWRENCEVILLE CBOC',               92248,      '508GH'),
(2016, '7',  516, 'MANATEE CBOC',                     48016,      '516GD'),
(2017, '8',  552, 'DAY CLC',                          159653,     '5529AA'),
(2018, '9',  552, 'DAYTON VA MOBILE CLINIC',          1200032778, '552QA'),
(2019, '9',  575, 'WESTERN COLORADO MOBILE CLINIC',   -1,         '575QE'),
(2020, '9',  508, 'STOCKBRIDGE CBOC',                 723062,     '508GG'),
(2021, '9',  516, 'CHARLOTTE CBOC',                   48034,      '516GE');
GO
