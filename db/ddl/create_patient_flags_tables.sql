/*
|---------------------------------------------------------------
| create_patient_flags_tables.sql
|---------------------------------------------------------------
| PostgreSQL DDL for Patient Flags serving database tables
| Part of med-z1 Phase 3 implementation
|---------------------------------------------------------------
| Creates two tables:
|   1. patient_flags - Denormalized flag assignments for queries
|   2. patient_flag_history - Complete audit trail with narratives
|---------------------------------------------------------------
| Usage:
|   psql -h localhost -U postgres -d medz1 -f db/ddl/create_patient_flags_tables.sql
|   OR
|   docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_flags_tables.sql
|---------------------------------------------------------------
*/

-- Set client encoding
SET client_encoding = 'UTF8';

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS clinical.patient_flag_history CASCADE;
DROP TABLE IF EXISTS clinical.patient_flags CASCADE;

\echo 'Creating patient_flags table...'

-- Main patient flags table (denormalized for query performance)
CREATE TABLE clinical.patient_flags (
    flag_id                 SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,   -- ICN
    assignment_id           BIGINT NOT NULL UNIQUE, -- Unique for upserts
    flag_name               VARCHAR(100) NOT NULL,
    flag_category           VARCHAR(2) NOT NULL,    -- 'I' or 'II'
    flag_type               VARCHAR(30),
    is_active               BOOLEAN NOT NULL,
    assignment_status       VARCHAR(20) NOT NULL,
    assignment_date         TIMESTAMP NOT NULL,
    inactivation_date       TIMESTAMP,
    owner_site              VARCHAR(10),
    owner_site_name         VARCHAR(100),
    review_frequency_days   INTEGER,
    next_review_date        TIMESTAMP,
    review_status           VARCHAR(20),            -- 'CURRENT', 'DUE SOON', 'OVERDUE'
    last_action_date        TIMESTAMP,
    last_action             VARCHAR(50),
    last_action_by          VARCHAR(100),
    last_updated            TIMESTAMP DEFAULT NOW()
);

\echo 'Creating indexes on patient_flags...'

-- Indexes for patient-centric queries
CREATE INDEX idx_patient_flags_patient ON clinical.patient_flags (patient_key, is_active);
CREATE INDEX idx_patient_flags_review ON clinical.patient_flags (review_status, next_review_date);

\echo 'Creating patient_flag_history table...'

-- History table with sensitive narrative text
CREATE TABLE clinical.patient_flag_history (
    history_id              SERIAL PRIMARY KEY,
    assignment_id           BIGINT NOT NULL,
    patient_key             VARCHAR(50) NOT NULL,
    history_date            TIMESTAMP NOT NULL,
    action_code             SMALLINT NOT NULL,      -- 1-5
    action_name             VARCHAR(50) NOT NULL,
    entered_by_duz          INTEGER NOT NULL,
    entered_by_name         VARCHAR(100),
    approved_by_duz         INTEGER NOT NULL,
    approved_by_name        VARCHAR(100),
    tiu_document_ien        INTEGER,
    history_comments        TEXT,                   -- SENSITIVE narrative
    event_site              VARCHAR(10),
    created_at              TIMESTAMP DEFAULT NOW()
);

\echo 'Creating indexes on patient_flag_history...'

-- Indexes for history queries
CREATE INDEX idx_flag_history_assignment ON clinical.patient_flag_history (assignment_id, history_date DESC);
CREATE INDEX idx_flag_history_patient ON clinical.patient_flag_history (patient_key, history_date DESC);

\echo 'Patient flags tables created successfully!'

-- Verify tables exist
SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE tablename LIKE 'patient_flag%'
ORDER BY tablename;
