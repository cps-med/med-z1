-- Insert data: ImmunizationMill.VaccineCode
-- Purpose: Seed Cerner vaccine codes mapped to CDC CVX codes
-- Subset of vaccines (15 common vaccines vs 30 in CDWWork)
-- CodeValue = Cerner internal codes (simulated)
--
-- IMPORTANT NOTES:
-- 1. CodeValue numbers are Cerner-specific (different from VistA IENs)
-- 2. CVXCode provides the mapping bridge to VistA data
-- 3. Display names may differ from VistA (Cerner nomenclature)
-- 4. Subset intentionally smaller than CDWWork to simulate real-world variance

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting 15 vaccine codes into ImmunizationMill.VaccineCode...';
GO

-- Insert 15 common vaccines with Cerner CodeValue mappings
INSERT INTO ImmunizationMill.VaccineCode (CodeValue, Display, Definition, CVXCode, CodeSet, IsActive)
VALUES
-- COVID-19 vaccines (most common in Cerner systems)
(9000208, 'COVID-19 (PFIZER-BIONTECH)', 'COVID-19 mRNA vaccine, Pfizer 30mcg dose', '208', 100, 1),
(9000213, 'COVID-19 (MODERNA)', 'COVID-19 mRNA vaccine, Moderna 100mcg dose', '213', 100, 1),

-- Influenza vaccines
(9000088, 'INFLUENZA VACCINE', 'Influenza, unspecified formulation', '088', 100, 1),
(9000135, 'INFLUENZA HIGH DOSE', 'Influenza, high dose seasonal, preservative-free', '135', 100, 1),
(9000141, 'INFLUENZA INJECTABLE', 'Influenza, seasonal, injectable', '141', 100, 1),

-- Adult vaccines
(9000115, 'TDAP VACCINE', 'Tetanus, diphtheria, acellular pertussis (Tdap)', '115', 100, 1),
(9000113, 'TD VACCINE', 'Tetanus and diphtheria toxoids (Td)', '113', 100, 1),

-- Shingles
(9000187, 'SHINGRIX', 'Zoster vaccine recombinant (Shingrix)', '187', 100, 1),

-- Pneumococcal
(9000033, 'PNEUMOVAX 23', 'Pneumococcal polysaccharide vaccine, 23 valent (PPSV23)', '033', 100, 1),

-- Hepatitis
(9000043, 'HEPATITIS B ADULT', 'Hepatitis B, adult formulation', '043', 100, 1),
(9000052, 'HEPATITIS A ADULT', 'Hepatitis A, adult formulation', '052', 100, 1),

-- HPV
(9000062, 'HPV VACCINE', 'Human Papillomavirus vaccine (HPV)', '062', 100, 1),

-- Pediatric vaccines
(9000008, 'HEPATITIS B PEDIATRIC', 'Hepatitis B, adolescent or pediatric', '008', 100, 1),
(9000020, 'DTAP', 'Diphtheria, tetanus toxoids and acellular pertussis (DTaP)', '020', 100, 1),
(9000010, 'IPV', 'Poliovirus, inactivated (IPV)', '010', 100, 1);
GO

-- Verification
DECLARE @VaccineCodeCount INT;
SELECT @VaccineCodeCount = COUNT(*) FROM ImmunizationMill.VaccineCode;
PRINT 'Inserted ' + CAST(@VaccineCodeCount AS VARCHAR(10)) + ' vaccine codes into ImmunizationMill.VaccineCode';

-- Show sample
PRINT 'Sample vaccine codes:';
SELECT TOP 5 VaccineCodeSID, CodeValue, Display, CVXCode
FROM ImmunizationMill.VaccineCode
ORDER BY VaccineCodeSID;
GO
