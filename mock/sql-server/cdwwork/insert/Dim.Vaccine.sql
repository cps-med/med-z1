-- Insert data: Dim.Vaccine
-- Purpose: Seed 30 common vaccines with CDC CVX codes
-- Source: CDC CVX (Vaccines Administered) code set
-- URL: https://www2a.cdc.gov/vaccines/iis/iisstandards/vaccines.asp
--
-- IMPORTANT NOTES:
-- 1. CVX codes are ENTERPRISE-WIDE standard (same across all VA sites)
-- 2. VistaIEN values shown are REPRESENTATIVE examples
-- 3. In production, each VistA site has different IEN values for same vaccine
-- 4. Example: CVX 208 (Pfizer COVID) might be IEN 208 at Site 508, IEN 350 at Site 630
-- 5. Silver ETL will map site-specific IENs → CVX codes for standardization

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Insert 30 common vaccines covering pediatric, adult, and seasonal immunizations
-- CVX codes are official CDC standard codes

PRINT 'Inserting 30 vaccines into Dim.Vaccine...';
GO

INSERT INTO Dim.Vaccine (VaccineName, VaccineShortName, CVXCode, VistaIEN, IsInactive)
VALUES
-- Pediatric vaccines
('Hepatitis B, adolescent or pediatric', 'HEP B-PEDS', '008', '8', 'N'),
('Poliovirus, inactivated (IPV)', 'IPV', '010', '10', 'N'),
('Diphtheria, tetanus toxoids and acellular pertussis vaccine (DTaP)', 'DTAP', '020', '20', 'N'),
('Varicella', 'VARICELLA', '021', '21', 'N'),
('Haemophilus influenzae type b vaccine (Hib)', 'HIB', '048', '48', 'N'),
('Hepatitis A, pediatric/adolescent', 'HEP A-PEDS', '083', '83', 'N'),

-- Adult vaccines
('Hepatitis B, adult', 'HEP B-ADULT', '043', '43', 'N'),
('Hepatitis A, adult', 'HEP A-ADULT', '052', '52', 'N'),
('Tetanus toxoid, diphtheria toxoid, and acellular pertussis vaccine (Tdap)', 'TDAP', '115', '115', 'N'),
('Tetanus and diphtheria toxoids (Td), preservative free', 'TD', '113', '113', 'N'),

-- Pneumococcal
('Pneumococcal polysaccharide vaccine, 23 valent (PPSV23)', 'PNEUMO-23', '033', '33', 'N'),
('Pneumococcal conjugate vaccine, 10 valent (PCV10)', 'PCV-10', '152', '152', 'N'),

-- HPV
('Human Papillomavirus vaccine (HPV)', 'HPV', '062', '62', 'N'),

-- Meningococcal
('Meningococcal polysaccharide vaccine (MPSV4)', 'MENING-4', '103', '103', 'N'),

-- Shingles (Zoster)
('Zoster vaccine, live (Zostavax)', 'ZOSTER-LIVE', '121', '121', 'Y'),  -- Discontinued in US
('Zoster vaccine recombinant (Shingrix)', 'SHINGRIX', '187', '187', 'N'),

-- Influenza (multiple formulations, all annual)
('Influenza, unspecified formulation', 'FLU', '088', '88', 'N'),
('Influenza, high dose seasonal, preservative-free', 'FLU-HD', '135', '135', 'N'),
('Influenza, seasonal, injectable, preservative free', 'FLU-INJ-PF', '140', '140', 'N'),
('Influenza, seasonal, injectable', 'FLU-INJ', '141', '141', 'N'),
('Influenza, injectable, quadrivalent, contains preservative', 'FLU-QUAD', '158', '158', 'N'),
('Influenza, injectable, quadrivalent, preservative free', 'FLU-QUAD-PF', '161', '161', 'N'),
('Influenza, seasonal, intradermal, preservative free', 'FLU-ID-PF', '144', '144', 'N'),

-- COVID-19
('COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose (Pfizer-BioNTech)', 'COVID-PFIZER', '208', '208', 'N'),
('COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose (Moderna)', 'COVID-MODERNA', '213', '213', 'N'),

-- Combination vaccines
('Diphtheria, tetanus toxoids and acellular pertussis vaccine, and poliovirus vaccine, inactivated (DTaP-IPV)', 'DTAP-IPV', '110', '110', 'N'),
('Diphtheria, tetanus, and acellular pertussis vaccine (DTaP), 5 pertussis antigens', 'DTAP-5', '106', '106', 'N'),
('Diphtheria, tetanus toxoids and acellular pertussis vaccine, unspecified formulation (DTaP)', 'DTAP-UNK', '107', '107', 'N'),

-- Additional formulations
('Haemophilus influenzae type b vaccine (Hib), PRP-OMP', 'HIB-OMP', '049', '49', 'N'),
('Hepatitis B, unspecified formulation', 'HEP B-UNK', '045', '45', 'N');
GO

-- Verify insertion
DECLARE @VaccineCount INT;
SELECT @VaccineCount = COUNT(*) FROM Dim.Vaccine;
PRINT 'Inserted ' + CAST(@VaccineCount AS VARCHAR(10)) + ' vaccines into Dim.Vaccine';

-- Show sample of vaccines
PRINT 'Sample vaccines:';
SELECT TOP 5 VaccineSID, VaccineShortName, CVXCode, VaccineName
FROM Dim.Vaccine
ORDER BY VaccineSID;
GO
