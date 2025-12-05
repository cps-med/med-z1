/*
|--------------------------------------------------------------------------------
| Insert: Dim.State.sql
|--------------------------------------------------------------------------------
| Insert test data
| StateSID => 5001 series
|
*/

PRINT '==== Dim.State ====';
GO

-- set the active database
USE CDWWork;
GO

-- insert data into Dim.Sta3n table
INSERT INTO Dim.[State]
(
    StateSID, StateIEN, Sta3n, [State], StateAbbrev, VAStateCode
)
VALUES
(425,  '1',  508, 'ALABAMA',   'AL', '01'),
(135,  '1',  503, 'ALABAMA',   'AL', '01'),
(3841, '1',  521, 'ALABAMA',   'AL', '01'),
(1174, '2',  620, 'ALASKA',    'AK', '02'),
(617,  '4',  635, 'ARIZONA',   'AZ', '04'),
(1792, '12', 516, 'FLORIDA',   'FL', '12'),
(1166, '12', 620, 'FLORIDA',   'FL', '12'),
(610,  '12', 635, 'FLORIDA',   'FL', '12'),
(415,  '13', 508, 'GEORGIA',   'GA', '13'),
(330,  '13', 637, 'GEORGIA',   'GA', '13'),
(1274, '39', 650, 'OHIO',      'OH', '39'),
(4956, '47', 552, 'TENNESSEE', 'TN', '47'),
(294,  '51', 637, 'VIRGINIA',  'VA', '51'),
(911,  '56', 438, 'WYOMING',   'WY', '56'),
(4948, '56', 552, 'WYOMING',   'WY', '56');
GO
