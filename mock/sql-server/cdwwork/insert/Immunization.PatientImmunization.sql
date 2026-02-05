-- Insert data: Immunization.PatientImmunization
-- Purpose: Seed realistic immunization histories for 8 test patients (~147 records)
-- Test Scenarios: Complete series, incomplete series, adverse reactions, gap analysis

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting immunization records for 8 test patients...';
GO

-- Helper: All VaccineSIDs will be looked up based on CVX codes
-- We'll use direct VaccineSID references since we know the identity seed starts at 1

-- =============================================================================
-- PATIENT 1001 (ICN100001, Adam Dooree, Age 67)
-- Scenario: Complete adult history, recent flu, complete Shingrix (25 vaccines)
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Childhood vaccines (historical, 1960s)
(1001, 1, '1958-03-15 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'LOT195801', 1),  -- Hep B pediatric (Walter Reed ordering, Marie Curry admin) @ Primary Care A
(1001, 1, '1958-05-20 10:00:00', '2 of 3', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 14, 508, 'LOT195802', 1),
(1001, 1, '1958-11-15 10:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 13, 508, 'LOT195803', 1),
(1001, 2, '1958-04-10 10:00:00', '1 of 4', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 15, 508, 'LOT195804', 1),  -- IPV (Florence ordering, Carl admin)
(1001, 2, '1958-06-12 10:00:00', '2 of 4', '0.5 ML', 'IM', 'R THIGH', NULL, 1003, 1004, 13, 508, 'LOT195805', 1),
(1001, 2, '1958-12-08 10:00:00', '3 of 4', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 14, 508, 'LOT195806', 1),
(1001, 2, '1963-03-15 10:00:00', '4 of 4 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1003, 1004, 15, 508, 'LOT196301', 1),
(1001, 3, '1958-04-15 10:00:00', '1 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 13, 508, 'LOT195807', 1),  -- DTaP (Louis ordering, Julius admin)
(1001, 3, '1958-06-20 10:00:00', '2 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 14, 508, 'LOT195808', 1),
(1001, 3, '1958-08-25 10:00:00', '3 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 15, 508, 'LOT195809', 1),
(1001, 3, '1959-04-10 10:00:00', '4 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 13, 508, 'LOT195901', 1),
(1001, 3, '1963-03-20 10:00:00', '5 of 5 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1005, 1006, 14, 508, 'LOT196302', 1),
(1001, 4, '1959-05-10 10:00:00', '1 of 2', '0.5 ML', 'SC', 'L ARM', NULL, 1001, 1002, 15, 508, 'LOT195902', 1),  -- Varicella
(1001, 4, '1963-06-15 10:00:00', '2 of 2 COMPLETE', '0.5 ML', 'SC', 'R ARM', NULL, 1001, 1002, 13, 508, 'LOT196303', 1),

-- Adult boosters
(1001, 9, '2015-08-10 14:30:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 44, 508, 'LOT201501', 1),  -- Tdap booster @ Pharmacy
(1001, 11, '2018-09-15 09:00:00', 'SINGLE', '0.65 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 13, 508, 'LOT201801', 1),  -- PPSV23
(1001, 16, '2020-10-05 11:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'LOT202001', 1),  -- Shingrix @ Pharmacy
(1001, 16, '2021-02-10 10:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 44, 508, 'LOT202102', 1),

-- Annual flu vaccines (last 5 years)
(1001, 18, '2020-10-15 13:00:00', 'ANNUAL 2020', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 44, 508, 'FLU2020HD', 1),  -- Flu HD @ Pharmacy
(1001, 18, '2021-10-12 14:00:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 44, 508, 'FLU2021HD', 1),
(1001, 18, '2022-10-08 13:30:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 44, 508, 'FLU2022HD', 1),
(1001, 18, '2023-10-10 14:15:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 44, 508, 'FLU2023HD', 1),
(1001, 18, '2024-10-05 13:45:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'FLU2024HD', 1),

-- COVID-19 series
(1001, 24, '2021-03-15 10:00:00', '1 of 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'COVID2021P1', 1),  -- Pfizer @ Pharmacy
(1001, 24, '2021-04-12 10:30:00', '2 of 2 COMPLETE', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'COVID2021P2', 1);
GO

-- =============================================================================
-- PATIENT 1002 (ICN100002, Barry Miifaa, Age 42)
-- Scenario: Incomplete Shingrix (1 of 2), adverse reaction to flu (18 vaccines)
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Childhood vaccines
(1002, 1, '1983-05-10 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 14, 508, 'LOT198301', 1),
(1002, 1, '1983-07-15 10:00:00', '2 of 3', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 15, 508, 'LOT198302', 1),
(1002, 1, '1984-01-20 10:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 13, 508, 'LOT198401', 1),
(1002, 3, '1983-06-01 10:00:00', '1 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 14, 508, 'LOT198303', 1),
(1002, 3, '1983-08-05 10:00:00', '2 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 15, 508, 'LOT198304', 1),
(1002, 3, '1983-10-10 10:00:00', '3 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 13, 508, 'LOT198305', 1),
(1002, 3, '1984-06-01 10:00:00', '4 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 14, 508, 'LOT198402', 1),
(1002, 3, '1988-07-01 10:00:00', '5 of 5 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1005, 1006, 15, 508, 'LOT198801', 1),

-- Adult vaccines
(1002, 9, '2020-05-15 14:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'LOT202003', 1),  -- Tdap
(1002, 13, '2019-06-20 11:00:00', '1 of 2', '1.0 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 14, 508, 'HPV201901', 1),  -- HPV
(1002, 13, '2019-12-15 11:30:00', '2 of 2 COMPLETE', '1.0 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 15, 508, 'HPV201902', 1),

-- Shingrix incomplete (CRITICAL: Only 1 of 2!)
(1002, 16, '2023-08-10 10:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'SHING2023', 1),

-- Flu vaccines (NOTE: 2023 has adverse reaction!)
(1002, 17, '2021-10-15 13:00:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'FLU2021', 1),
(1002, 17, '2022-10-12 13:30:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 44, 508, 'FLU2022', 1),
(1002, 17, '2023-10-08 13:15:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'L DELTOID', 'Severe arm soreness, fever 101F for 24 hours', 1003, 1004, 44, 508, 'FLU2023', 1),  -- ADVERSE REACTION

-- COVID-19
(1002, 25, '2021-04-20 14:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'COVID2021M1', 1),  -- Moderna
(1002, 25, '2021-05-25 14:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'COVID2021M2', 1),
(1002, 25, '2022-03-10 10:00:00', 'BOOSTER 1', '0.25 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 44, 508, 'COVID2022MB', 1);
GO

-- =============================================================================
-- PATIENT 1003 (ICN100003, Carol Soolaa, Age 8)
-- Scenario: Childhood series (DTaP, IPV, MMR), some incomplete (22 vaccines)
-- Note: Design says age 8, creating appropriate childhood series
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Birth to 2 months
(1003, 1, '2017-01-15 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L THIGH', NULL, 1001, 1002, 13, 508, 'HEPB201701', 1),  -- Hep B
(1003, 1, '2017-03-20 10:30:00', '2 of 3', '0.5 ML', 'IM', 'R THIGH', NULL, 1001, 1002, 14, 508, 'HEPB201702', 1),
(1003, 1, '2017-08-15 11:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'L THIGH', NULL, 1001, 1002, 15, 508, 'HEPB201703', 1),

-- DTaP series (5-dose)
(1003, 3, '2017-03-15 10:00:00', '1 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 13, 508, 'DTAP201701', 1),
(1003, 3, '2017-05-15 10:30:00', '2 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1003, 1004, 14, 508, 'DTAP201702', 1),
(1003, 3, '2017-07-15 11:00:00', '3 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 15, 508, 'DTAP201703', 1),
(1003, 3, '2018-01-20 10:00:00', '4 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1003, 1004, 13, 508, 'DTAP201801', 1),
(1003, 3, '2021-03-10 10:30:00', '5 of 5 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1003, 1004, 14, 508, 'DTAP202101', 1),

-- IPV series (4-dose)
(1003, 2, '2017-03-15 10:15:00', '1 of 4', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 15, 508, 'IPV201701', 1),
(1003, 2, '2017-05-15 10:45:00', '2 of 4', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 13, 508, 'IPV201702', 1),
(1003, 2, '2018-01-20 10:15:00', '3 of 4', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 14, 508, 'IPV201801', 1),
(1003, 2, '2021-03-10 10:45:00', '4 of 4 COMPLETE', '0.5 ML', 'IM', 'R ARM', NULL, 1005, 1006, 15, 508, 'IPV202101', 1),

-- Hib series (3-dose)
(1003, 5, '2017-03-15 10:30:00', '1 of 3', '0.5 ML', 'IM', 'L THIGH', NULL, 1001, 1002, 13, 508, 'HIB201701', 1),
(1003, 5, '2017-05-15 11:00:00', '2 of 3', '0.5 ML', 'IM', 'R THIGH', NULL, 1001, 1002, 14, 508, 'HIB201702', 1),
(1003, 5, '2018-01-20 10:30:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'R THIGH', NULL, 1001, 1002, 15, 508, 'HIB201801', 1),

-- Hep A pediatric series (2-dose)
(1003, 6, '2018-07-15 10:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 13, 508, 'HEPA201801', 1),
(1003, 6, '2019-01-20 10:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 14, 508, 'HEPA201902', 1),

-- Varicella (INCOMPLETE: Only 1 of 2!)
(1003, 4, '2018-07-15 10:15:00', '1 of 2', '0.5 ML', 'SC', 'L ARM', NULL, 1005, 1006, 15, 508, 'VAR201801', 1),

-- Annual flu vaccines (last 3 years)
(1003, 17, '2022-10-15 14:00:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'L ARM', NULL, 1001, 1002, 44, 508, 'FLU2022PED', 1),
(1003, 17, '2023-10-12 14:30:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R ARM', NULL, 1001, 1002, 44, 508, 'FLU2023PED', 1),
(1003, 17, '2024-10-10 15:00:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L ARM', NULL, 1001, 1002, 44, 508, 'FLU2024PED', 1);
GO

-- =============================================================================
-- PATIENT 1004 (ICN100004, Debby Tiidoo, Age 55)
-- Scenario: No Shingrix, no recent flu (gap analysis test) (15 vaccines)
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Historical childhood vaccines (1970s)
(1004, 1, '1970-05-10 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 13, 508, 'LOT197001', 1),
(1004, 1, '1970-07-15 10:00:00', '2 of 3', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 14, 508, 'LOT197002', 1),
(1004, 1, '1971-01-20 10:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 15, 508, 'LOT197101', 1),
(1004, 3, '1970-05-15 10:00:00', '1 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 13, 508, 'LOT197003', 1),
(1004, 3, '1970-07-20 10:00:00', '2 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 14, 508, 'LOT197004', 1),
(1004, 3, '1970-09-25 10:00:00', '3 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 15, 508, 'LOT197005', 1),
(1004, 3, '1971-05-10 10:00:00', '4 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 13, 508, 'LOT197102', 1),
(1004, 3, '1975-06-15 10:00:00', '5 of 5 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1005, 1006, 14, 508, 'LOT197501', 1),

-- Adult vaccines (but missing recent ones!)
(1004, 9, '2015-07-10 14:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'LOT201502', 1),  -- Tdap
(1004, 11, '2018-08-15 10:00:00', 'SINGLE', '0.65 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 14, 508, 'LOT201802', 1),  -- PPSV23

-- COVID-19 (minimal - just primary series)
(1004, 24, '2021-05-10 11:00:00', '1 of 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'COVID2021P3', 1),
(1004, 24, '2021-06-07 11:30:00', '2 of 2 COMPLETE', '0.3 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'COVID2021P4', 1),

-- Old flu vaccines (NOT recent - last one was 2020!)
(1004, 17, '2019-10-15 13:00:00', 'ANNUAL 2019', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'FLU2019', 1),
(1004, 17, '2020-10-12 13:30:00', 'ANNUAL 2020', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 44, 508, 'FLU2020', 1);
-- NOTE: Missing 2021-2024 flu vaccines (gap)!
-- NOTE: Missing Shingrix (should have at age 55)!
GO

-- =============================================================================
-- PATIENT 1005 (ICN100005, Edward Dooree, Age 28)
-- Scenario: COVID-19 primary + booster, Tdap, recent flu (12 vaccines)
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Limited childhood history (just key vaccines)
(1005, 1, '1997-06-10 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 13, 508, 'LOT199701', 1),
(1005, 1, '1997-08-15 10:00:00', '2 of 3', '0.5 ML', 'IM', 'R THIGH', NULL, 1003, 1004, 14, 508, 'LOT199702', 1),
(1005, 1, '1998-02-20 10:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 15, 508, 'LOT199801', 1),

-- Recent adult vaccines
(1005, 9, '2022-06-15 14:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 13, 508, 'TDAP202201', 1),  -- Tdap

-- COVID-19 series with booster
(1005, 25, '2021-05-20 10:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'COVID2021M3', 1),  -- Moderna
(1005, 25, '2021-06-24 10:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'COVID2021M4', 1),
(1005, 25, '2022-04-10 11:00:00', 'BOOSTER 1', '0.25 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 44, 508, 'COVID2022MB2', 1),
(1005, 25, '2023-09-15 11:30:00', 'BOOSTER 2', '0.25 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'COVID2023MB', 1),

-- Recent flu vaccines
(1005, 17, '2022-10-15 13:00:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 44, 508, 'FLU2022YA', 1),
(1005, 17, '2023-10-12 13:30:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 44, 508, 'FLU2023YA', 1),
(1005, 17, '2024-10-08 14:00:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 44, 508, 'FLU2024YA', 1);
GO

-- =============================================================================
-- PATIENT 1009 (ICN100009, Claire Cmajor, Age 72)
-- Scenario: Multiple flu vaccines (annual pattern), pneumococcal (20 vaccines)
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Historical childhood (1950s)
(1009, 1, '1953-05-10 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L ARM', NULL, 1001, 1002, 65, 516, 'LOT195301', 1),
(1009, 1, '1953-07-15 10:00:00', '2 of 3', '0.5 ML', 'IM', 'R ARM', NULL, 1001, 1002, 66, 516, 'LOT195302', 1),
(1009, 1, '1954-01-20 10:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1001, 1002, 67, 516, 'LOT195401', 1),

-- Adult boosters
(1009, 9, '2012-08-10 14:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 65, 516, 'LOT201201', 1),  -- Tdap
(1009, 11, '2017-09-15 10:00:00', 'SINGLE', '0.65 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 66, 516, 'PPSV201701', 1),  -- PPSV23
(1009, 12, '2018-03-20 10:30:00', '1 of 4', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 67, 516, 'PCV201801', 1),  -- PCV10

-- Shingrix complete
(1009, 16, '2019-10-10 10:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 96, 516, 'SHING201901', 1),
(1009, 16, '2020-02-15 10:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 96, 516, 'SHING202001', 1),

-- Annual flu vaccines (EVERY YEAR from 2017-2024, 8 total)
(1009, 18, '2017-10-15 13:00:00', 'ANNUAL 2017', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 96, 516, 'FLUHD2017', 1),
(1009, 18, '2018-10-12 13:30:00', 'ANNUAL 2018', '0.5 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 96, 516, 'FLUHD2018', 1),
(1009, 18, '2019-10-10 14:00:00', 'ANNUAL 2019', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 96, 516, 'FLUHD2019', 1),
(1009, 18, '2020-10-08 13:45:00', 'ANNUAL 2020', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 96, 516, 'FLUHD2020', 1),
(1009, 18, '2021-10-15 14:15:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 96, 516, 'FLUHD2021', 1),
(1009, 18, '2022-10-12 13:30:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 96, 516, 'FLUHD2022', 1),
(1009, 18, '2023-10-10 14:00:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 96, 516, 'FLUHD2023', 1),
(1009, 18, '2024-10-08 13:45:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 96, 516, 'FLUHD2024', 1),

-- COVID-19
(1009, 24, '2021-03-20 10:00:00', '1 of 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 96, 516, 'COVID2021P5', 1),
(1009, 24, '2021-04-17 10:30:00', '2 of 2 COMPLETE', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 96, 516, 'COVID2021P6', 1);
GO

-- =============================================================================
-- PATIENT 1010 (ICN100010, Alexander Aminor, Age 35)
-- Scenario: Hepatitis B series (3-dose), HPV series incomplete (16 vaccines)
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Childhood vaccines (1990s)
(1010, 1, '1990-08-10 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 117, 552, 'LOT199001', 1),
(1010, 1, '1990-10-15 10:00:00', '2 of 3', '0.5 ML', 'IM', 'R THIGH', NULL, 1003, 1004, 118, 552, 'LOT199002', 1),
(1010, 1, '1991-04-20 10:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'L THIGH', NULL, 1003, 1004, 119, 552, 'LOT199101', 1),
(1010, 3, '1990-08-15 10:00:00', '1 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 117, 552, 'LOT199003', 1),
(1010, 3, '1990-10-20 10:00:00', '2 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 118, 552, 'LOT199004', 1),
(1010, 3, '1990-12-25 10:00:00', '3 of 5', '0.5 ML', 'IM', 'R THIGH', NULL, 1005, 1006, 119, 552, 'LOT199005', 1),
(1010, 3, '1991-08-10 10:00:00', '4 of 5', '0.5 ML', 'IM', 'L THIGH', NULL, 1005, 1006, 117, 552, 'LOT199102', 1),
(1010, 3, '1995-09-01 10:00:00', '5 of 5 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1005, 1006, 118, 552, 'LOT199501', 1),

-- Adult Hepatitis B series (complete)
(1010, 7, '2020-06-10 14:00:00', '1 of 3', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 119, 552, 'HEPB202001', 1),  -- Hep B adult
(1010, 7, '2020-08-15 14:30:00', '2 of 3', '1.0 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 117, 552, 'HEPB202002', 1),
(1010, 7, '2021-02-20 15:00:00', '3 of 3 COMPLETE', '1.0 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 118, 552, 'HEPB202101', 1),

-- HPV series (INCOMPLETE: Only 1 of 2!)
(1010, 13, '2021-05-15 11:00:00', '1 of 2', '1.0 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 119, 552, 'HPV202101', 1),

-- Recent vaccines
(1010, 9, '2022-07-20 14:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 117, 552, 'TDAP202202', 1),  -- Tdap
(1010, 17, '2023-10-15 13:00:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 118, 552, 'FLU2023', 1),
(1010, 17, '2024-10-12 13:30:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 119, 552, 'FLU2024', 1);
GO

-- =============================================================================
-- PATIENT 1013 (ICN100013, Irving Thompson, Age 61)
-- Scenario: Shingrix eligible (age 50+), COVID-19 boosters (19 vaccines)
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Historical childhood (1960s)
(1013, 1, '1964-05-10 10:00:00', '1 of 3', '0.5 ML', 'IM', 'L ARM', NULL, 1005, 1006, 117, 552, 'LOT196401', 1),
(1013, 1, '1964-07-15 10:00:00', '2 of 3', '0.5 ML', 'IM', 'R ARM', NULL, 1005, 1006, 118, 552, 'LOT196402', 1),
(1013, 1, '1965-01-20 10:00:00', '3 of 3 COMPLETE', '0.5 ML', 'IM', 'L ARM', NULL, 1005, 1006, 119, 552, 'LOT196501', 1),

-- Adult boosters
(1013, 9, '2018-09-10 14:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 117, 552, 'TDAP201801', 1),  -- Tdap
(1013, 11, '2020-08-15 10:00:00', 'SINGLE', '0.65 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 118, 552, 'PPSV202001', 1),  -- PPSV23

-- Shingrix complete (age 50+ eligible)
(1013, 16, '2021-09-10 10:00:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 119, 552, 'SHING202101', 1),
(1013, 16, '2022-01-15 10:30:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 117, 552, 'SHING202201', 1),

-- COVID-19 with multiple boosters
(1013, 24, '2021-04-10 11:00:00', '1 of 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 118, 552, 'COVID2021P7', 1),  -- Pfizer
(1013, 24, '2021-05-08 11:30:00', '2 of 2 COMPLETE', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 119, 552, 'COVID2021P8', 1),
(1013, 24, '2022-05-15 12:00:00', 'BOOSTER 1', '0.3 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 117, 552, 'COVID2022PB1', 1),
(1013, 24, '2023-04-20 12:30:00', 'BOOSTER 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 118, 552, 'COVID2023PB2', 1),
(1013, 24, '2024-03-25 13:00:00', 'BOOSTER 3', '0.3 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 119, 552, 'COVID2024PB3', 1),

-- Annual flu vaccines (last 5 years)
(1013, 18, '2020-10-15 13:00:00', 'ANNUAL 2020', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 117, 552, 'FLUHD2020A', 1),
(1013, 18, '2021-10-12 13:30:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 118, 552, 'FLUHD2021A', 1),
(1013, 18, '2022-10-10 14:00:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 119, 552, 'FLUHD2022A', 1),
(1013, 18, '2023-10-08 13:45:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 117, 552, 'FLUHD2023A', 1),
(1013, 18, '2024-10-05 14:15:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 118, 552, 'FLUHD2024A', 1);
GO

-- =============================================================================
-- PATIENT 1026 (ICN100016, Margaret E Wilson - DECEASED, Age 87)
-- Scenario: Elderly veteran, complete adult immunization history (12 vaccines)
-- Added 2026-02-04 - Historical immunizations for deceased patient
-- =============================================================================

INSERT INTO Immunization.PatientImmunization
(PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive)
VALUES
-- Tetanus booster (Tdap) - 10 years ago
(1026, 9, '2014-06-15 14:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'TDAP201401', 1),

-- Pneumococcal vaccines (PCV13 and PPSV23) - standard for elderly
(1026, 10, '2016-09-20 10:30:00', 'SINGLE', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 13, 508, 'PCV132016', 1),  -- PCV13 first
(1026, 11, '2017-10-05 11:00:00', 'SINGLE', '0.65 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 13, 508, 'PPSV2017', 1),  -- PPSV23 one year later

-- Shingrix series (zoster vaccine) - 2 dose series
(1026, 16, '2018-08-10 09:30:00', '1 of 2', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'SHING201801', 1),
(1026, 16, '2019-02-15 10:00:00', '2 of 2 COMPLETE', '0.5 ML', 'IM', 'R DELTOID', NULL, 1001, 1002, 13, 508, 'SHING201902', 1),

-- Annual flu vaccines (high-dose for seniors 65+) - last 5 years including final year
(1026, 18, '2020-10-20 13:30:00', 'ANNUAL 2020', '0.5 ML', 'IM', 'L DELTOID', NULL, 1003, 1004, 13, 508, 'FLUHD2020MW', 1),
(1026, 18, '2021-10-15 14:00:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'R DELTOID', NULL, 1005, 1006, 13, 508, 'FLUHD2021MW', 1),
(1026, 18, '2022-10-18 13:45:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'FLUHD2022MW', 1),
(1026, 18, '2023-10-12 14:15:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'R DELTOID', NULL, 1003, 1004, 13, 508, 'FLUHD2023MW', 1),
(1026, 18, '2024-10-08 13:30:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'L DELTOID', NULL, 1005, 1006, 13, 508, 'FLUHD2024MW', 1),  -- Final flu vaccine, ~2 months before death

-- COVID-19 series (Pfizer) - initial series in 2021
(1026, 24, '2021-03-20 10:00:00', '1 of 2', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'COVID2021P1MW', 1),
(1026, 24, '2021-04-17 10:30:00', '2 of 2 COMPLETE', '0.3 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, 13, 508, 'COVID2021P2MW', 1),

-- =============================================================================
-- Patient 1027: Robert J Anderson - DECEASED 2024-11-15 (8 immunizations)
-- 46 yo M combat veteran - deployment vaccines + routine adult vaccines
-- Added 2026-02-04
-- =============================================================================

-- Military deployment vaccines (pre-deployment 2006)
(1027, 26, '2006-02-10 08:00:00', '1 of 3', '0.5 ML', 'SC', 'L ARM', NULL, 1007, 1008, 14, 528, 'HEPAB200601', 1),  -- Hepatitis A/B series
(1027, 26, '2006-03-15 08:00:00', '2 of 3', '0.5 ML', 'SC', 'R ARM', NULL, 1007, 1008, 14, 528, 'HEPAB200602', 1),
(1027, 26, '2006-08-20 08:00:00', '3 of 3 COMPLETE', '0.5 ML', 'SC', 'L ARM', NULL, 1007, 1008, 14, 528, 'HEPAB200603', 1),

-- Tdap booster (post-discharge)
(1027, 9, '2015-04-15 10:00:00', 'BOOSTER', '0.5 ML', 'IM', 'L DELTOID', NULL, 1004, 1005, 14, 528, 'TDAP201501', 1),

-- Annual flu vaccines (last 4 years including final year)
(1027, 18, '2021-10-12 14:00:00', 'ANNUAL 2021', '0.5 ML', 'IM', 'L DELTOID', NULL, 1004, 1005, 14, 528, 'FLU2021MW', 1),
(1027, 18, '2022-10-18 13:30:00', 'ANNUAL 2022', '0.5 ML', 'IM', 'R DELTOID', NULL, 1004, 1005, 14, 528, 'FLU2022MW', 1),
(1027, 18, '2023-10-15 14:15:00', 'ANNUAL 2023', '0.5 ML', 'IM', 'L DELTOID', NULL, 1004, 1005, 14, 528, 'FLU2023MW', 1),
(1027, 18, '2024-10-10 13:45:00', 'ANNUAL 2024', '0.5 ML', 'IM', 'R DELTOID', NULL, 1004, 1005, 14, 528, 'FLU2024MW', 1);  -- Final flu vaccine, ~1 month before death
GO

-- =============================================================================
-- Verification queries
-- =============================================================================

PRINT '';
PRINT '=== Verification Summary ===';
PRINT '';

-- Total count
DECLARE @TotalCount INT;
SELECT @TotalCount = COUNT(*) FROM Immunization.PatientImmunization;
PRINT 'Total immunization records: ' + CAST(@TotalCount AS VARCHAR(10));

-- Count by patient
PRINT '';
PRINT 'Records by patient:';
SELECT
    p.PatientICN,
    COUNT(*) AS ImmunizationCount
FROM Immunization.PatientImmunization pi
JOIN SPatient.SPatient p ON pi.PatientSID = p.PatientSID
GROUP BY p.PatientICN
ORDER BY p.PatientICN;

-- Sample records
PRINT '';
PRINT 'Sample immunization records:';
SELECT TOP 5
    pi.PatientImmunizationSID,
    p.PatientICN,
    v.VaccineShortName,
    v.CVXCode,
    pi.AdministeredDateTime,
    pi.Series
FROM Immunization.PatientImmunization pi
JOIN SPatient.SPatient p ON pi.PatientSID = p.PatientSID
JOIN Dim.Vaccine v ON pi.VaccineSID = v.VaccineSID
ORDER BY pi.PatientImmunizationSID;

PRINT '';
PRINT 'Immunization data insertion complete!';
GO
