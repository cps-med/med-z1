-- ---------------------------------------------------------------------
-- create_patient_family_history_table.sql
-- ---------------------------------------------------------------------
-- Create patient_family_history table in PostgreSQL for med-z1 serving DB
-- This table stores harmonized family-history rows from VistA + Cerner
-- ---------------------------------------------------------------------
-- Version History:
--   v1.0 (2026-02-12): Initial schema - Family History Enhancement (Phase 3)
-- ---------------------------------------------------------------------

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (for development - use migrations in production)
DROP TABLE IF EXISTS clinical.patient_family_history CASCADE;

-- Create patient family history table
CREATE TABLE clinical.patient_family_history (
    family_history_id BIGSERIAL PRIMARY KEY,

    -- Patient and source identity
    patient_icn VARCHAR(50) NOT NULL,
    patient_key VARCHAR(50) NOT NULL,
    source_system VARCHAR(20) NOT NULL,
    source_ehr VARCHAR(20),
    source_record_id VARCHAR(50),

    -- Relationship and condition
    relationship_code VARCHAR(50),
    relationship_name VARCHAR(100) NOT NULL,
    relationship_degree VARCHAR(30),
    condition_code VARCHAR(50),
    condition_name VARCHAR(255) NOT NULL,
    snomed_code VARCHAR(50),
    icd10_code VARCHAR(20),
    condition_category VARCHAR(80),
    risk_condition_group VARCHAR(80),

    -- Clinical flags and status
    hereditary_risk_flag BOOLEAN,
    first_degree_relative_flag BOOLEAN,
    clinical_status VARCHAR(30),
    is_active BOOLEAN DEFAULT TRUE,

    -- Family member detail
    family_member_gender VARCHAR(20),
    family_member_age INTEGER,
    family_member_deceased BOOLEAN,
    onset_age_years INTEGER,

    -- Encounter/provenance detail
    recorded_datetime TIMESTAMP,
    entered_datetime TIMESTAMP,
    encounter_sid BIGINT,
    facility_id VARCHAR(20),
    provider_id BIGINT,
    provider_name VARCHAR(120),
    location_id BIGINT,
    comment_text TEXT,

    -- Patient-level denormalized metrics from Gold
    family_history_count_total INTEGER,
    family_history_count_active INTEGER,
    family_history_first_degree_count INTEGER,
    family_history_first_degree_high_risk_count INTEGER,

    -- ETL metadata
    silver_load_datetime TIMESTAMP,
    gold_load_datetime TIMESTAMP,
    silver_schema_version VARCHAR(20),
    gold_schema_version VARCHAR(20),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Prevent duplicate source rows on reload or replay
CREATE UNIQUE INDEX uq_patient_family_history_source
    ON clinical.patient_family_history(source_system, source_record_id)
    WHERE source_record_id IS NOT NULL;

-- Common patient timeline queries
CREATE INDEX idx_family_history_patient_recorded
    ON clinical.patient_family_history(patient_icn, recorded_datetime DESC);

-- Active-only and first-degree risk queries
CREATE INDEX idx_family_history_patient_active
    ON clinical.patient_family_history(patient_icn, is_active)
    WHERE is_active = TRUE;

CREATE INDEX idx_family_history_patient_first_degree
    ON clinical.patient_family_history(patient_icn, first_degree_relative_flag)
    WHERE first_degree_relative_flag = TRUE;

-- Clinical category and relationship filtering
CREATE INDEX idx_family_history_patient_category
    ON clinical.patient_family_history(patient_icn, condition_category);

CREATE INDEX idx_family_history_patient_relationship
    ON clinical.patient_family_history(patient_icn, relationship_name);

-- Data lineage filtering
CREATE INDEX idx_family_history_source
    ON clinical.patient_family_history(source_system, source_ehr);

-- Add comments for documentation
COMMENT ON TABLE clinical.patient_family_history IS 'Patient family-history findings harmonized from CDWWork (VistA) and CDWWork2 (Cerner) Gold output';
COMMENT ON COLUMN clinical.patient_family_history.patient_icn IS 'Patient Integrated Care Number (ICN)';
COMMENT ON COLUMN clinical.patient_family_history.patient_key IS 'Patient key alias for consistency with other clinical.* tables (same as ICN)';
COMMENT ON COLUMN clinical.patient_family_history.source_record_id IS 'Source FamilyHistory SID from CDWWork/CDWWork2';
COMMENT ON COLUMN clinical.patient_family_history.relationship_degree IS 'FIRST_DEGREE, SECOND_DEGREE, or NULL/UNKNOWN';
COMMENT ON COLUMN clinical.patient_family_history.hereditary_risk_flag IS 'Source-derived flag indicating clinically relevant hereditary risk';
COMMENT ON COLUMN clinical.patient_family_history.first_degree_relative_flag IS 'Derived Gold flag for first-degree relatives';
COMMENT ON COLUMN clinical.patient_family_history.family_history_first_degree_high_risk_count IS 'Denormalized patient-level count for first-degree + hereditary-risk entries';

-- Verify table creation
SELECT 'patient_family_history table created successfully in clinical schema (v1.0)' AS status;
