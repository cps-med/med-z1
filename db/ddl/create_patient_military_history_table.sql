-- ---------------------------------------------------------------------
-- create_patient_military_history_table.sql
-- ---------------------------------------------------------------------
-- Create patient_military_history table in PostgreSQL for med-z1 serving DB
-- This table stores military service history and environmental exposures
-- ---------------------------------------------------------------------
-- Version History:
--   v1.0 (2026-02-07): Initial schema - Military History Enhancement
-- ---------------------------------------------------------------------

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (for development - use migrations in production)
DROP TABLE IF EXISTS clinical.patient_military_history CASCADE;

-- Create patient military history table
CREATE TABLE clinical.patient_military_history (
    patient_key VARCHAR(50) PRIMARY KEY,
    icn VARCHAR(50) NOT NULL,

    -- Service Connection
    service_connected_flag CHAR(1),
    service_connected_percent DECIMAL(5,2),

    -- Environmental Exposures
    agent_orange_exposure CHAR(1),
    agent_orange_location VARCHAR(50),
    ionizing_radiation CHAR(1),
    pow_status CHAR(1),
    pow_location VARCHAR(50),
    shad_flag CHAR(1),  -- Shipboard Hazard and Defense
    sw_asia_exposure CHAR(1),  -- Southwest Asia (Gulf War)
    camp_lejeune_flag CHAR(1),

    -- Metadata
    source_system VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_military_history_icn ON clinical.patient_military_history(icn);
CREATE INDEX idx_military_history_sc_percent ON clinical.patient_military_history(service_connected_percent);
CREATE INDEX idx_military_history_agent_orange ON clinical.patient_military_history(agent_orange_exposure) WHERE agent_orange_exposure = 'Y';
CREATE INDEX idx_military_history_pow ON clinical.patient_military_history(pow_status) WHERE pow_status = 'Y';
CREATE INDEX idx_military_history_gulf_war ON clinical.patient_military_history(sw_asia_exposure) WHERE sw_asia_exposure = 'Y';

-- Add comments for documentation
COMMENT ON TABLE clinical.patient_military_history IS 'Patient military service history and environmental exposures from Gold layer';
COMMENT ON COLUMN clinical.patient_military_history.patient_key IS 'Internal unique identifier (currently same as ICN)';
COMMENT ON COLUMN clinical.patient_military_history.service_connected_flag IS 'Y=Service Connected, N=Not Service Connected';
COMMENT ON COLUMN clinical.patient_military_history.service_connected_percent IS 'VA disability rating percentage (0-100)';
COMMENT ON COLUMN clinical.patient_military_history.agent_orange_exposure IS 'Y=Exposed to Agent Orange (Vietnam era), N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.agent_orange_location IS 'Location of Agent Orange exposure (e.g., VIETNAM)';
COMMENT ON COLUMN clinical.patient_military_history.ionizing_radiation IS 'Y=Exposed to ionizing radiation, N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.pow_status IS 'Y=Former Prisoner of War, N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.pow_location IS 'Location of POW captivity';
COMMENT ON COLUMN clinical.patient_military_history.shad_flag IS 'Shipboard Hazard and Defense exposure flag';
COMMENT ON COLUMN clinical.patient_military_history.sw_asia_exposure IS 'Y=Southwest Asia (Gulf War) service, N=No, U=Unknown';
COMMENT ON COLUMN clinical.patient_military_history.camp_lejeune_flag IS 'Y=Camp Lejeune water contamination exposure, N=No';

-- Verify table creation
SELECT 'patient_military_history table created successfully in clinical schema (v1.0)' AS status;
