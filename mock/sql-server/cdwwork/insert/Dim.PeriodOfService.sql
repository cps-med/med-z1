/*
|--------------------------------------------------------------------------------
| Insert: Dim.PeriodOfService.sql
|--------------------------------------------------------------------------------
| Insert test data
| StateSID => 12001 series
|
*/

PRINT '==== Dim.PeriodOfService ====';
GO

-- set the active database
USE CDWWork;
GO

-- insert data into Dim.PeriodOfService table
INSERT INTO Dim.PeriodOfService
(
    PeriodOfServiceSID, PeriodOfServiceIEN, Sta3n, PeriodOfService, PeriodOfServiceAbbreviation, PeriodOfServiceCode
)
VALUES
(12001, '508101', 508, 'KOREAN', 'K', '0'),
(12002, '508102', 508, 'WORLD WAR I', 'WWI', '1'),
(12003, '508103', 508, 'WORLD WAR II', 'WWII', '2'),
(12004, '508104', 508, 'VIETNAM ERA', 'VE', '7'),
(12005, '508105', 508, 'POST-VIETNAM', 'PV', '8'),
(12006, '516101', 516, 'KOREAN', 'K', '0'),
(12007, '516102', 516, 'WORLD WAR I', 'WWI', '1'),
(12008, '516103', 516, 'WORLD WAR II', 'WWII', '2'),
(12009, '516104', 516, 'VIETNAM ERA', 'VE', '7'),
(12010, '516105', 516, 'POST-VIETNAM', 'PV', '8'),
(12011, '522101', 522, 'KOREAN', 'K', '0'),
(12012, '522102', 522, 'WORLD WAR I', 'WWI', '1'),
(12013, '522103', 522, 'WORLD WAR II', 'WWII', '2'),
(12014, '522104', 522, 'VIETNAM ERA', 'VE', '7'),
(12015, '522105', 522, 'POST-VIETNAM', 'PV', '8');
GO