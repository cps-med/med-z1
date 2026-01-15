-- Create table: patient_immunizations
-- Purpose: Serving database table for patient immunization records
-- Source: Gold layer Parquet files (immunizations/patient_immunizations_final.parquet)
-- Note: Includes CVX-coded vaccines for AI compliance checking and gap analysis

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (development only)
DROP TABLE IF EXISTS clinical.patient_immunizations CASCADE;

CREATE TABLE clinical.patient_immunizations (
    immunization_id         SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,       -- ICN (Integrated Care Number)
    immunization_sid        BIGINT NOT NULL UNIQUE,     -- Source system ID (PatientImmunizationSID or VaccineAdminSID)

    -- Vaccine identification (CVX-coded for AI/compliance)
    cvx_code                VARCHAR(10),                -- CDC CVX code (https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp)
    vaccine_name            VARCHAR(255),               -- Standardized vaccine name (UPPERCASE)
    vaccine_name_local      VARCHAR(255),               -- As entered by clinician (original)

    -- Administration details
    administered_datetime   TIMESTAMP NOT NULL,         -- When vaccine was administered
    series                  VARCHAR(50),                -- Display format ("1 of 2", "BOOSTER", "ANNUAL 2024")
    dose_number             INTEGER,                    -- Parsed dose number (1, 2, 3)
    total_doses             INTEGER,                    -- Parsed total in series (2, 3)
    is_series_complete      BOOLEAN,                    -- TRUE if dose_number >= total_doses
    dose                    VARCHAR(50),                -- Dose amount ("0.5 ML")
    route                   VARCHAR(50),                -- Administration route (IM, SC, PO, etc.)
    site_of_administration  VARCHAR(100),               -- Anatomical site (Left Deltoid, Right Thigh, etc.)

    -- Safety tracking
    adverse_reaction        VARCHAR(255),               -- Adverse reaction description
    has_adverse_reaction    BOOLEAN,                    -- TRUE if adverse_reaction is not null

    -- Clinical context
    provider_name           VARCHAR(100),               -- Administering provider name
    location_sid            INTEGER,                    -- LocationSID from source system
    location_name           VARCHAR(100),               -- Hospital/clinic location name
    location_type           VARCHAR(50),                -- Location type (Outpatient, Inpatient, etc.)
    station_name            VARCHAR(100),               -- VA facility name (Sta3n lookup)
    sta3n                   SMALLINT,                   -- VA station number

    -- Additional details
    comments                TEXT,                       -- Free-text clinical notes

    -- Derived flags for filtering/UI
    is_annual_vaccine       BOOLEAN,                    -- TRUE for annual influenza vaccines
    is_covid_vaccine        BOOLEAN,                    -- TRUE for COVID-19 vaccines

    -- Metadata
    source_system           VARCHAR(20),                -- "CDWWork" (VistA) or "CDWWork2" (Cerner)
    last_updated            TIMESTAMP DEFAULT NOW()
);

-- =========================================================================
-- Indexes for Performance
-- =========================================================================

-- Primary index: Patient lookups sorted by date (most common query pattern)
CREATE INDEX idx_immunizations_patient_date
    ON clinical.patient_immunizations (patient_key, administered_datetime DESC);

-- CVX code index for AI/compliance queries
CREATE INDEX idx_immunizations_cvx
    ON clinical.patient_immunizations (cvx_code, administered_datetime DESC);

-- Series tracking index (for identifying dose sequences)
CREATE INDEX idx_immunizations_series
    ON clinical.patient_immunizations (patient_key, cvx_code, dose_number, administered_datetime DESC);

-- Incomplete series index (for compliance checking and care gap alerts)
CREATE INDEX idx_immunizations_incomplete
    ON clinical.patient_immunizations (patient_key, is_series_complete, administered_datetime DESC)
    WHERE is_series_complete = FALSE;

-- Adverse reaction index (for safety queries)
CREATE INDEX idx_immunizations_reactions
    ON clinical.patient_immunizations (patient_key, has_adverse_reaction, administered_datetime DESC)
    WHERE has_adverse_reaction = TRUE;

-- Vaccine family indexes (for filtering UI by vaccine type)
CREATE INDEX idx_immunizations_annual
    ON clinical.patient_immunizations (patient_key, administered_datetime DESC)
    WHERE is_annual_vaccine = TRUE;

CREATE INDEX idx_immunizations_covid
    ON clinical.patient_immunizations (patient_key, administered_datetime DESC)
    WHERE is_covid_vaccine = TRUE;

-- Index for location type filtering
CREATE INDEX idx_immunizations_location_type
    ON clinical.patient_immunizations (location_type);

-- Index for data source filtering (VistA vs Cerner)
CREATE INDEX idx_immunizations_data_source
    ON clinical.patient_immunizations (source_system);

-- =========================================================================
-- Comments for Documentation
-- =========================================================================

COMMENT ON TABLE clinical.patient_immunizations IS 'Patient immunization records from Gold layer';
COMMENT ON COLUMN clinical.patient_immunizations.patient_key IS 'Patient ICN (Integrated Care Number) - universal identifier';
COMMENT ON COLUMN clinical.patient_immunizations.immunization_sid IS 'Source system surrogate key (PatientImmunizationSID from CDWWork or VaccineAdminSID from CDWWork2)';
COMMENT ON COLUMN clinical.patient_immunizations.cvx_code IS 'CDC CVX code for vaccine identification (https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp)';
COMMENT ON COLUMN clinical.patient_immunizations.vaccine_name IS 'Standardized vaccine name (UPPERCASE for consistency)';
COMMENT ON COLUMN clinical.patient_immunizations.vaccine_name_local IS 'Original vaccine name as entered by clinician';
COMMENT ON COLUMN clinical.patient_immunizations.is_series_complete IS 'TRUE if patient has received all doses in series (e.g., 2 of 2)';
COMMENT ON COLUMN clinical.patient_immunizations.has_adverse_reaction IS 'TRUE if adverse reaction was documented';
COMMENT ON COLUMN clinical.patient_immunizations.is_annual_vaccine IS 'TRUE for annual influenza vaccines (CVX codes 88, 135, 140, 141, etc.)';
COMMENT ON COLUMN clinical.patient_immunizations.is_covid_vaccine IS 'TRUE for COVID-19 vaccines (CVX codes 207, 208, 210, 211, 212, 213, etc.)';
COMMENT ON COLUMN clinical.patient_immunizations.source_system IS 'Data origin: CDWWork (VistA) or CDWWork2 (Cerner/Oracle Health)';

-- =========================================================================
-- Grant Permissions
-- =========================================================================

GRANT SELECT ON clinical.patient_immunizations TO PUBLIC;
