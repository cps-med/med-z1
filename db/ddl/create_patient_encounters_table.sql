-- Create table: patient_encounters
-- Purpose: Serving database table for patient inpatient encounters (admissions)
-- Source: Gold layer Parquet files (inpatient/inpatient_final.parquet)

-- Drop table if exists (development only)
DROP TABLE IF EXISTS patient_encounters;

CREATE TABLE patient_encounters (
    encounter_id            SERIAL PRIMARY KEY,
    patient_key             VARCHAR(50) NOT NULL,       -- ICN
    inpatient_id            BIGINT NOT NULL UNIQUE,     -- Source InpatientSID

    -- Admission details
    admit_datetime          TIMESTAMP NOT NULL,         -- Admission date/time
    admit_location_id       INTEGER,                    -- Ward/Location SID at admission
    admit_location_name     VARCHAR(100),               -- Ward/Location name at admission
    admit_location_type     VARCHAR(50),                -- Location type (Inpatient, Emergency, etc.)
    admit_diagnosis_code    VARCHAR(20),                -- ICD-10 admission diagnosis
    admitting_provider_id   INTEGER,                    -- Provider SID
    admitting_provider_name VARCHAR(200),               -- Provider full name

    -- Discharge details
    discharge_datetime      TIMESTAMP,                  -- Discharge date/time (NULL if active)
    discharge_date_id       INTEGER,                    -- Discharge date dimension SID
    discharge_location_id   INTEGER,                    -- Ward/Location SID at discharge
    discharge_location_name VARCHAR(100),               -- Ward/Location name at discharge
    discharge_location_type VARCHAR(50),                -- Location type at discharge
    discharge_diagnosis_code VARCHAR(20),               -- ICD-10 discharge diagnosis
    discharge_diagnosis_text VARCHAR(100),              -- Discharge diagnosis description
    discharge_disposition   VARCHAR(50),                -- e.g., "Home", "SNF", "Rehab", "AMA"

    -- Metrics
    length_of_stay          INTEGER,                    -- LOS in days (from CDW)
    total_days              INTEGER,                    -- Days from admit to discharge (or now if active)
    encounter_status        VARCHAR(20),                -- "Active" or "Discharged"
    is_active               BOOLEAN NOT NULL,           -- True if currently admitted
    admission_category      VARCHAR(30),                -- "Active Admission", "Observation", "Short Stay", etc.

    -- UI flags
    is_recent               BOOLEAN NOT NULL,           -- Admitted or discharged within last 30 days
    is_extended_stay        BOOLEAN NOT NULL,           -- Active admission with total_days > 14

    -- Facility
    sta3n                   VARCHAR(10),                -- VA Station Number (e.g., "508")
    facility_name           VARCHAR(100),               -- Facility name (e.g., "Atlanta VA Medical Center")

    -- Metadata
    source_system           VARCHAR(50),                -- "CDWWork"
    last_updated            TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_patient_encounters_patient_date
    ON patient_encounters (patient_key, admit_datetime DESC);

CREATE INDEX idx_patient_encounters_admit_date
    ON patient_encounters (admit_datetime DESC);

CREATE INDEX idx_patient_encounters_discharge_date
    ON patient_encounters (discharge_datetime DESC)
    WHERE discharge_datetime IS NOT NULL;

-- Index for active admissions (widget and alerts)
CREATE INDEX idx_patient_encounters_active
    ON patient_encounters (patient_key, admit_datetime DESC)
    WHERE is_active = TRUE;

-- Index for recent encounters (last 30 days)
CREATE INDEX idx_patient_encounters_recent
    ON patient_encounters (patient_key, admit_datetime DESC)
    WHERE is_recent = TRUE;

-- Index for facility queries
CREATE INDEX idx_patient_encounters_facility
    ON patient_encounters (sta3n, admit_datetime DESC);

-- Indexes for location type filtering
CREATE INDEX idx_patient_encounters_admit_location_type
    ON patient_encounters (admit_location_type);

CREATE INDEX idx_patient_encounters_discharge_location_type
    ON patient_encounters (discharge_location_type);

-- Comments
COMMENT ON TABLE patient_encounters IS 'Patient inpatient encounters (admissions) from Gold layer';
COMMENT ON COLUMN patient_encounters.patient_key IS 'Patient ICN (Integrated Care Number)';
COMMENT ON COLUMN patient_encounters.inpatient_id IS 'Source InpatientSID from CDWWork';
COMMENT ON COLUMN patient_encounters.is_active IS 'True if patient is currently admitted (no discharge date)';
COMMENT ON COLUMN patient_encounters.is_recent IS 'True if admitted or discharged within last 30 days';
COMMENT ON COLUMN patient_encounters.is_extended_stay IS 'True if active admission with total_days > 14';
COMMENT ON COLUMN patient_encounters.admission_category IS 'Active Admission, Observation, Short Stay, Standard Stay, or Extended Stay';
COMMENT ON COLUMN patient_encounters.discharge_disposition IS 'Where patient went after discharge (Home, SNF, Rehab, AMA, Deceased, etc.)';

-- Grant permissions
GRANT SELECT ON patient_encounters TO PUBLIC;
