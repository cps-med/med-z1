-- =============================================
-- Create PostgreSQL Serving Database Tables: patient_allergies, patient_allergy_reactions
-- Description: Serving tables for patient allergy data
-- Author: Claude Code
-- Date: 2025-12-12
-- Updated: 2025-12-24 - Moved to clinical schema
-- =============================================

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS clinical.patient_allergy_reactions CASCADE;
DROP TABLE IF EXISTS clinical.patient_allergies CASCADE;

-- =============================================
-- Table: patient_allergies
-- Description: Main patient allergy data (denormalized)
-- =============================================

CREATE TABLE clinical.patient_allergies (
    allergy_id              SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,       -- ICN
    allergy_sid             BIGINT NOT NULL,            -- Source PatientAllergySID
    allergen_local          VARCHAR(255) NOT NULL,      -- Local name entered by clinician
    allergen_standardized   VARCHAR(100) NOT NULL,      -- Standardized allergen name
    allergen_type           VARCHAR(50) NOT NULL,       -- 'DRUG', 'FOOD', 'ENVIRONMENTAL'
    severity                VARCHAR(50),                -- 'MILD', 'MODERATE', 'SEVERE'
    severity_rank           INTEGER,                    -- 1=MILD, 2=MODERATE, 3=SEVERE (for sorting)
    reactions               TEXT,                       -- Comma-separated for display
    reaction_count          INTEGER DEFAULT 0,
    origination_date        TIMESTAMP NOT NULL,
    observed_date           TIMESTAMP,
    historical_or_observed  VARCHAR(20),                -- 'HISTORICAL' or 'OBSERVED'
    originating_site        VARCHAR(10),
    originating_site_name   VARCHAR(100),
    originating_staff       VARCHAR(100),
    comment                 TEXT,                       -- May contain PHI/sensitive info
    is_active               BOOLEAN DEFAULT TRUE,
    verification_status     VARCHAR(30),
    is_drug_allergy         BOOLEAN DEFAULT FALSE,      -- For widget prioritization
    last_updated            TIMESTAMP DEFAULT NOW()
);

-- Indexes for patient_allergies
CREATE INDEX idx_patient_allergies_patient
    ON clinical.patient_allergies (patient_key, is_active);

CREATE INDEX idx_patient_allergies_type
    ON clinical.patient_allergies (allergen_type, severity_rank DESC);

CREATE INDEX idx_patient_allergies_drug
    ON clinical.patient_allergies (patient_key, is_drug_allergy, severity_rank DESC)
    WHERE is_active = TRUE;

CREATE INDEX idx_patient_allergies_severity
    ON clinical.patient_allergies (severity_rank DESC, origination_date DESC)
    WHERE is_active = TRUE;

COMMENT ON TABLE clinical.patient_allergies IS 'Main patient allergy data with denormalized reactions';
COMMENT ON COLUMN clinical.patient_allergies.patient_key IS 'Patient ICN identifier';
COMMENT ON COLUMN clinical.patient_allergies.allergy_sid IS 'Source PatientAllergySID from CDW';
COMMENT ON COLUMN clinical.patient_allergies.allergen_local IS 'Local allergen name as entered (e.g., PENICILLIN VK 500MG)';
COMMENT ON COLUMN clinical.patient_allergies.allergen_standardized IS 'Standardized allergen name (e.g., PENICILLIN)';
COMMENT ON COLUMN clinical.patient_allergies.reactions IS 'Comma-separated reaction names for quick display';
COMMENT ON COLUMN clinical.patient_allergies.comment IS 'Free-text clinical narrative - may contain PHI';
COMMENT ON COLUMN clinical.patient_allergies.is_drug_allergy IS 'TRUE if allergen_type = DRUG (for widget filtering)';

-- =============================================
-- Table: patient_allergy_reactions
-- Description: Detailed reaction data for each allergy (normalized)
-- =============================================

CREATE TABLE clinical.patient_allergy_reactions (
    reaction_id             SERIAL PRIMARY KEY,
    allergy_sid             BIGINT NOT NULL,            -- FK to source PatientAllergySID
    patient_key             VARCHAR(50) NOT NULL,
    reaction_name           VARCHAR(100) NOT NULL,
    created_at              TIMESTAMP DEFAULT NOW()
);

-- Indexes for patient_allergy_reactions
CREATE INDEX idx_allergy_reactions_allergy
    ON clinical.patient_allergy_reactions (allergy_sid);

CREATE INDEX idx_allergy_reactions_patient
    ON clinical.patient_allergy_reactions (patient_key);

COMMENT ON TABLE clinical.patient_allergy_reactions IS 'Individual reactions for each allergy (normalized for granular querying)';
COMMENT ON COLUMN clinical.patient_allergy_reactions.allergy_sid IS 'Links to source PatientAllergySID';

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Tables patient_allergies and patient_allergy_reactions created successfully';
    RAISE NOTICE 'Indexes created for optimal query performance';
END $$;
