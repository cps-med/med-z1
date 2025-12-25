-- Create table: patient_labs
-- Purpose: Serving database table for patient laboratory results
-- Source: Gold layer Parquet files (labs/*.parquet)
-- Updated: 2025-12-24 - Moved to clinical schema

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (development only)
DROP TABLE IF EXISTS clinical.patient_labs;

CREATE TABLE clinical.patient_labs (
    lab_id                      SERIAL PRIMARY KEY,
    patient_key                 VARCHAR(50) NOT NULL,       -- ICN
    lab_chem_sid                BIGINT NOT NULL UNIQUE,     -- Source LabChemSID
    lab_test_sid                INTEGER NOT NULL,           -- Test definition ID
    lab_test_name               VARCHAR(200) NOT NULL,      -- e.g., "Sodium"
    lab_test_code               VARCHAR(50),                -- e.g., "NA"
    loinc_code                  VARCHAR(20),                -- Logical Observation Identifier
    panel_name                  VARCHAR(200),               -- e.g., "Basic Metabolic Panel"
    accession_number            VARCHAR(50) NOT NULL,       -- e.g., "CH 20251211-001"
    result_value                VARCHAR(100),               -- Display value (e.g., "142", "Positive")
    result_numeric              DECIMAL(18,6),              -- Numeric result for trending
    result_unit                 VARCHAR(50),                -- "mmol/L", "mg/dL", etc.
    abnormal_flag               VARCHAR(10),                -- 'H', 'L', 'H*', 'L*', 'PANIC'
    is_abnormal                 BOOLEAN,                    -- Quick abnormal check
    is_critical                 BOOLEAN,                    -- Panic/critical values
    ref_range_text              VARCHAR(100),               -- "135 - 145", "Negative"
    ref_range_low               DECIMAL(18,6),              -- Parsed low value
    ref_range_high              DECIMAL(18,6),              -- Parsed high value
    collection_datetime         TIMESTAMP NOT NULL,         -- When specimen collected
    result_datetime             TIMESTAMP NOT NULL,         -- When result available
    location_id                 INTEGER,                    -- LocationSID
    collection_location         VARCHAR(100),               -- Lab location name
    collection_location_type    VARCHAR(50),                -- "Laboratory"
    specimen_type               VARCHAR(50),                -- "Serum", "Whole Blood", etc.
    sta3n                       VARCHAR(10),                -- Station number
    performing_lab_sid          INTEGER,                    -- Lab that performed test
    ordering_provider_sid       INTEGER,                    -- Provider who ordered
    vista_package               VARCHAR(10),                -- "CH" for Chemistry
    last_updated                TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_patient_labs_patient_date
    ON clinical.patient_labs (patient_key, collection_datetime DESC);

CREATE INDEX idx_patient_labs_test_date
    ON clinical.patient_labs (lab_test_name, collection_datetime DESC);

CREATE INDEX idx_patient_labs_panel
    ON clinical.patient_labs (panel_name, collection_datetime DESC)
    WHERE panel_name IS NOT NULL;

-- Index for abnormal/critical results
CREATE INDEX idx_patient_labs_abnormal
    ON clinical.patient_labs (is_abnormal, is_critical, collection_datetime DESC)
    WHERE is_abnormal = TRUE;

-- Index for recent labs widget queries
CREATE INDEX idx_patient_labs_recent
    ON clinical.patient_labs (patient_key, panel_name, collection_datetime DESC);

-- Index for location type filtering
CREATE INDEX idx_patient_labs_location_type
    ON clinical.patient_labs (collection_location_type);

-- Index for accession number grouping (panel results)
CREATE INDEX idx_patient_labs_accession
    ON clinical.patient_labs (accession_number, lab_test_sid);

-- Comments
COMMENT ON TABLE clinical.patient_labs IS 'Patient laboratory results from Gold layer';
COMMENT ON COLUMN clinical.patient_labs.patient_key IS 'Patient ICN (Integrated Care Number)';
COMMENT ON COLUMN clinical.patient_labs.lab_chem_sid IS 'Source LabChemSID from CDWWork';
COMMENT ON COLUMN clinical.patient_labs.loinc_code IS 'Logical Observation Identifiers Names and Codes (LOINC)';
COMMENT ON COLUMN clinical.patient_labs.panel_name IS 'Panel/battery name (e.g., Basic Metabolic Panel, Lipid Panel)';
COMMENT ON COLUMN clinical.patient_labs.is_critical IS 'Critical/panic values requiring immediate clinical attention';
COMMENT ON COLUMN clinical.patient_labs.abnormal_flag IS 'H=High, L=Low, H*=Critical High, L*=Critical Low, PANIC=Panic value';
COMMENT ON COLUMN clinical.patient_labs.collection_location IS 'Laboratory location where specimen was collected';

-- Grant permissions
GRANT SELECT ON clinical.patient_labs TO PUBLIC;
