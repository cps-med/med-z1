-- Create table: reference.vaccine
-- Purpose: CVX code reference table for vaccine standardization and AI compliance checking
-- Source: CDC CVX standard codes (https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp)
-- Usage: Join with clinical.patient_immunizations on cvx_code for lookups

-- Create reference schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS reference;

-- Drop table if exists (development only)
DROP TABLE IF EXISTS reference.vaccine CASCADE;

CREATE TABLE reference.vaccine (
    cvx_code                VARCHAR(10) PRIMARY KEY,    -- CDC CVX code (e.g., "208" for COVID-19 Pfizer)
    vaccine_name            VARCHAR(255) NOT NULL,      -- Full vaccine name (e.g., "COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose")
    vaccine_short_name      VARCHAR(100),               -- Abbreviated name (e.g., "COVID-19 Pfizer")
    vaccine_group           VARCHAR(100),               -- Grouping for UI filters (e.g., "COVID-19", "Influenza", "Hepatitis")
    typical_series_pattern  VARCHAR(50),                -- Expected series (e.g., "2-dose", "3-dose", "Annual", "Single-dose")
    is_active               BOOLEAN DEFAULT TRUE,       -- FALSE if vaccine no longer in use
    notes                   TEXT,                       -- Additional info (e.g., age recommendations, contraindications)
    last_updated            TIMESTAMP DEFAULT NOW()
);

-- Index for vaccine group filtering (UI dropdowns)
CREATE INDEX idx_reference_vaccine_group
    ON reference.vaccine (vaccine_group, vaccine_name)
    WHERE is_active = TRUE;

-- Index for active vaccines only
CREATE INDEX idx_reference_vaccine_active
    ON reference.vaccine (is_active, vaccine_name);

-- =========================================================================
-- Seed Data (30 common vaccines from MVP)
-- =========================================================================

INSERT INTO reference.vaccine (cvx_code, vaccine_name, vaccine_short_name, vaccine_group, typical_series_pattern, is_active, notes)
VALUES
-- Childhood vaccines
('008', 'Hepatitis B, adolescent or pediatric', 'HEP B-PEDS', 'Hepatitis', '3-dose', TRUE, 'Birth series: 0, 1-2, 6-18 months'),
('010', 'Poliovirus, inactivated (IPV)', 'IPV', 'Polio', '4-dose', TRUE, 'Series at 2, 4, 6-18 months, 4-6 years'),
('020', 'Diphtheria, tetanus toxoids and acellular pertussis vaccine (DTaP)', 'DTAP', 'Tdap/DTaP', '5-dose', TRUE, 'Series at 2, 4, 6, 15-18 months, 4-6 years'),
('021', 'Varicella', 'VARICELLA', 'Varicella', '2-dose', TRUE, 'Doses at 12-15 months and 4-6 years'),
('048', 'Haemophilus influenzae type b vaccine (Hib)', 'HIB', 'Hib', '3-4 dose', TRUE, 'Series at 2, 4, 6, 12-15 months (brand-dependent)'),
('083', 'Hepatitis A, pediatric/adolescent', 'HEP A-PEDS', 'Hepatitis', '2-dose', TRUE, 'Doses at 12-23 months, 6-18 months apart'),

-- Adult vaccines
('043', 'Hepatitis B, adult', 'HEP B-ADULT', 'Hepatitis', '3-dose', TRUE, 'Series at 0, 1, 6 months'),
('052', 'Hepatitis A, adult', 'HEP A-ADULT', 'Hepatitis', '2-dose', TRUE, 'Doses 6-12 months apart'),
('062', 'Human Papillomavirus (HPV)', 'HPV', 'HPV', '2-3 dose', TRUE, 'Ages 11-12 (2-dose) or 15-26 (3-dose)'),
('033', 'Pneumococcal polysaccharide vaccine, 23 valent (PPSV23)', 'PPSV23', 'Pneumococcal', 'Single-dose', TRUE, 'Adults 65+ or high-risk adults'),
('113', 'Tetanus and diphtheria toxoids - preservative free (Td)', 'TD', 'Tdap/DTaP', 'Booster', TRUE, 'Every 10 years after initial series'),
('115', 'Tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine (Tdap)', 'TDAP', 'Tdap/DTaP', 'Booster', TRUE, 'One-time booster replacing Td, then Td q10y'),
('187', 'Zoster vaccine recombinant, adjuvanted (Shingrix)', 'SHINGRIX', 'Shingles', '2-dose', TRUE, 'Ages 50+, doses 2-6 months apart'),

-- Annual vaccines (Influenza)
('088', 'Influenza virus vaccine, unspecified formulation', 'FLU', 'Influenza', 'Annual', TRUE, 'Seasonal vaccine, September-March'),
('135', 'Influenza, high dose seasonal, preservative-free', 'FLU-HD', 'Influenza', 'Annual', TRUE, 'Adults 65+, higher antigen content'),
('140', 'Influenza, seasonal, injectable, preservative free', 'FLU-PF', 'Influenza', 'Annual', TRUE, 'Preservative-free formulation'),
('141', 'Influenza, seasonal, injectable', 'FLU-INJ', 'Influenza', 'Annual', TRUE, 'Standard dose, all ages'),
('144', 'Influenza, seasonal, intradermal, preservative free', 'FLU-ID', 'Influenza', 'Annual', TRUE, 'Intradermal administration'),
('150', 'Influenza, injectable, quadrivalent, preservative free', 'FLU-QUAD-PF', 'Influenza', 'Annual', TRUE, '4-strain protection'),
('153', 'Influenza, injectable, Madin Darby Canine Kidney, preservative free', 'FLU-MDCK', 'Influenza', 'Annual', TRUE, 'Cell culture-based'),
('158', 'Influenza, injectable, quadrivalent, contains preservative', 'FLU-QUAD', 'Influenza', 'Annual', TRUE, '4-strain with preservative'),
('161', 'Influenza, injectable, quadrivalent, preservative free, pediatric', 'FLU-QUAD-PF-PEDS', 'Influenza', 'Annual', TRUE, 'Pediatric dose'),
('166', 'Influenza, intradermal, quadrivalent, preservative free, injectable', 'FLU-ID-QUAD', 'Influenza', 'Annual', TRUE, 'Intradermal quadrivalent'),
('168', 'Influenza, trivalent, adjuvanted', 'FLU-TRI-ADJ', 'Influenza', 'Annual', TRUE, 'With adjuvant for enhanced response'),

-- COVID-19 vaccines (most common)
('207', 'COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5mL dose or 50 mcg/0.25mL dose', 'COVID-19 Moderna', 'COVID-19', '2-dose', TRUE, 'mRNA vaccine, primary series'),
('208', 'COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose', 'COVID-19 Pfizer', 'COVID-19', '2-dose', TRUE, 'mRNA vaccine, primary series'),
('210', 'COVID-19 vaccine, vector-nr, rS-ChAdOx1, PF, 0.5 mL', 'COVID-19 AstraZeneca', 'COVID-19', '2-dose', TRUE, 'Viral vector vaccine'),
('212', 'COVID-19 vaccine, vector-nr, rS-Ad26, PF, 0.5 mL', 'COVID-19 Janssen', 'COVID-19', 'Single-dose', TRUE, 'Single-dose viral vector'),
('213', 'COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose, tris-sucrose', 'COVID-19 Pfizer (tris-sucrose)', 'COVID-19', '2-dose', TRUE, 'Pfizer with tris-sucrose buffer'),
('217', 'COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose, pediatric', 'COVID-19 Pfizer Pediatric', 'COVID-19', '2-dose', TRUE, 'Ages 5-11');

-- =========================================================================
-- Comments for Documentation
-- =========================================================================

COMMENT ON TABLE reference.vaccine IS 'CDC CVX code reference table for vaccine standardization';
COMMENT ON COLUMN reference.vaccine.cvx_code IS 'CDC CVX code - primary identifier for vaccines';
COMMENT ON COLUMN reference.vaccine.vaccine_name IS 'Official CDC vaccine name (full descriptive name)';
COMMENT ON COLUMN reference.vaccine.vaccine_short_name IS 'Abbreviated name for UI display';
COMMENT ON COLUMN reference.vaccine.vaccine_group IS 'Vaccine family grouping (for UI filters: Influenza, COVID-19, Hepatitis, etc.)';
COMMENT ON COLUMN reference.vaccine.typical_series_pattern IS 'Expected series pattern (e.g., 2-dose, 3-dose, Annual, Booster, Single-dose)';
COMMENT ON COLUMN reference.vaccine.is_active IS 'FALSE if vaccine is no longer in use or has been superseded';
COMMENT ON COLUMN reference.vaccine.notes IS 'Additional information (age recommendations, contraindications, CDC guidance)';

-- =========================================================================
-- Grant Permissions
-- =========================================================================

GRANT SELECT ON reference.vaccine TO PUBLIC;
