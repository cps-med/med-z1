-- Create table: patient_vitals
-- Purpose: Serving database table for patient vital signs
-- Source: Gold layer Parquet files (patient_vitals/*.parquet)

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (development only)
DROP TABLE IF EXISTS clinical.patient_vitals;

CREATE TABLE clinical.patient_vitals (
    vital_id                SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,       -- ICN
    vital_sign_id           BIGINT NOT NULL UNIQUE,     -- Source VitalSignSID
    vital_type              VARCHAR(100) NOT NULL,      -- e.g., "BLOOD PRESSURE"
    vital_abbr              VARCHAR(10) NOT NULL,       -- e.g., "BP"
    taken_datetime          TIMESTAMP NOT NULL,         -- When vital was taken
    entered_datetime        TIMESTAMP,                  -- When entered into VistA
    result_value            VARCHAR(50),                -- Display value (e.g., "120/80", "98.6")
    numeric_value           DECIMAL(10,2),              -- For single-value vitals
    systolic                INTEGER,                    -- BP only
    diastolic               INTEGER,                    -- BP only
    metric_value            DECIMAL(10,2),              -- Converted value (temp in C, weight in kg)
    unit_of_measure         VARCHAR(20),                -- "mmHg", "F", "lb", etc.
    qualifiers              JSONB,                      -- Store as JSON array
    location_id             INTEGER,                    -- LocationSID
    location_name           VARCHAR(100),               -- Hospital location name
    location_type           VARCHAR(50),                -- Location type (Outpatient, Inpatient, etc.)
    entered_by              VARCHAR(100),               -- Staff name
    abnormal_flag           VARCHAR(20),                -- 'CRITICAL', 'HIGH', 'LOW', 'NORMAL'
    bmi                     DECIMAL(5,2),               -- Calculated BMI (if WT and HT available)
    last_updated            TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_patient_vitals_patient_date
    ON clinical.patient_vitals (patient_key, taken_datetime DESC);

CREATE INDEX idx_patient_vitals_type_date
    ON clinical.patient_vitals (vital_type, taken_datetime DESC);

-- Index for recent vitals widget queries
CREATE INDEX idx_patient_vitals_recent
    ON clinical.patient_vitals (patient_key, vital_abbr, taken_datetime DESC);

-- Index for abnormal vitals queries
CREATE INDEX idx_patient_vitals_abnormal
    ON clinical.patient_vitals (abnormal_flag, taken_datetime DESC)
    WHERE abnormal_flag IN ('CRITICAL', 'HIGH');

-- Index for location type filtering
CREATE INDEX idx_patient_vitals_location_type
    ON clinical.patient_vitals (location_type);

-- Comments
COMMENT ON TABLE clinical.patient_vitals IS 'Patient vital signs data from Gold layer';
COMMENT ON COLUMN clinical.patient_vitals.patient_key IS 'Patient ICN (Integrated Care Number)';
COMMENT ON COLUMN clinical.patient_vitals.vital_sign_id IS 'Source VitalSignSID from CDWWork';
COMMENT ON COLUMN clinical.patient_vitals.qualifiers IS 'JSON array of qualifiers (position, site, method, cuff size)';
COMMENT ON COLUMN clinical.patient_vitals.abnormal_flag IS 'CRITICAL, HIGH, LOW, or NORMAL based on clinical thresholds';
COMMENT ON COLUMN clinical.patient_vitals.bmi IS 'Body Mass Index calculated from height and weight';

-- Grant permissions
GRANT SELECT ON clinical.patient_vitals TO PUBLIC;
