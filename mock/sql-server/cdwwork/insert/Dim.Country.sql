-----------------------------------------------------------------------------
-- Dim.Country.sql
-- Insert Test data
-- CountrySID => 1200009999 series
-----------------------------------------------------------------------------

PRINT '================================================';
PRINT '====              Dim.Country               ====';
PRINT '================================================';
GO

-- set the active database
USE CDWWork;
GO

-- insert data into Dim table
INSERT INTO Dim.Country
(
    CountrySID, CountryIEN, Sta3n, CountryCode, NumericCode, PostalName, PostalDescription
)
VALUES
(1200005295, '27',  508, 'BRA', '076', 'BRAZIL',         'Brazil'),
(1200005149, '39',  508, 'CAN', '124', 'CANADA',         'Canada'),
(1200005304, '221', 508, 'GBR', '826', 'UNITED KINGDOM', 'United Kingdom'),
(1200005271, '1',   508, 'USA', '840', 'UNITED STATES',  'United States'),

(1200002466, '27',  516, 'BRA', '076', 'BRAZIL',         'Brazil'),
(1200002478, '39',  516, 'CAN', '124', 'CANADA',         'Canada'),
(1200000196, '221', 516, 'GBR', '826', 'UNITED KINGDOM', 'United Kingdom'),
(1200002442, '1',   516, 'USA', '840', 'UNITED STATES',  'United States'),

(1200002798, '27',  552, 'BRA', '076', 'BRAZIL',         'Brazil'),
(1200002810, '39',  552, 'CAN', '124', 'CANADA',         'Canada'),
(1200003022, '221', 552, 'GBR', '826', 'UNITED KINGDOM', 'United Kingdom'),
(1200002774, '1',   552, 'USA', '840', 'UNITED STATES',  'United States');
GO
