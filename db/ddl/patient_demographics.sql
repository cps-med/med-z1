-- ---------------------------------------------------------------------
-- patient_demographics.sql
-- ---------------------------------------------------------------------
-- Create patient_demographics table in PostgreSQL for med-z1 serving DB
-- This table stores Gold layer patient demographics optimized for UI queries
-- ---------------------------------------------------------------------
-- Version History:
--   v1.0 (2025-12-10): Initial schema with basic demographics
--   v2.0 (2025-12-11): Added address, phone, and insurance fields
--   v3.0 (2025-12-14): Added marital_status, religion, service_connected_percent,
--                       deceased_flag, death_date (Demographics full page - Phase 2)
-- ---------------------------------------------------------------------

-- Drop table if exists (for development - use migrations in production)
DROP TABLE IF EXISTS patient_demographics CASCADE;

-- Create patient demographics table
CREATE TABLE patient_demographics (
    patient_key VARCHAR(50) PRIMARY KEY,
    icn VARCHAR(50) UNIQUE NOT NULL,
    ssn VARCHAR(64),  -- Encrypted or hashed in production
    ssn_last4 VARCHAR(4),
    name_last VARCHAR(100),
    name_first VARCHAR(100),
    name_display VARCHAR(200),
    dob DATE,
    age INTEGER,
    sex VARCHAR(1),
    gender VARCHAR(50),
    primary_station VARCHAR(10),
    primary_station_name VARCHAR(200),

    -- Address fields (primary address)
    address_street1 VARCHAR(100),
    address_street2 VARCHAR(100),
    address_city VARCHAR(100),
    address_state VARCHAR(2),
    address_zip VARCHAR(10),

    -- Contact fields
    phone_primary VARCHAR(20),

    -- Insurance fields (primary insurance)
    insurance_company_name VARCHAR(100),

    -- Additional Demographics (Phase 2)
    marital_status VARCHAR(25),
    religion VARCHAR(50),

    -- Military Service (Phase 2)
    service_connected_percent DECIMAL(5,2),

    -- Critical Information (Phase 2)
    deceased_flag CHAR(1),
    death_date DATE,

    -- Metadata
    veteran_status VARCHAR(50),
    source_system VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_patient_icn ON patient_demographics(icn);
CREATE INDEX idx_patient_name_last ON patient_demographics(name_last);
CREATE INDEX idx_patient_name_first ON patient_demographics(name_first);
CREATE INDEX idx_patient_ssn_last4 ON patient_demographics(ssn_last4);
CREATE INDEX idx_patient_station ON patient_demographics(primary_station);
CREATE INDEX idx_patient_dob ON patient_demographics(dob);

-- Add comments for documentation
COMMENT ON TABLE patient_demographics IS 'Patient demographics from Gold layer - optimized for UI queries';
COMMENT ON COLUMN patient_demographics.patient_key IS 'Internal unique identifier (currently same as ICN)';
COMMENT ON COLUMN patient_demographics.icn IS 'Integrated Care Number - primary VA patient identifier';
COMMENT ON COLUMN patient_demographics.ssn_last4 IS 'Last 4 digits of SSN for display/verification';
COMMENT ON COLUMN patient_demographics.name_display IS 'Formatted name for UI display (LAST, First)';
COMMENT ON COLUMN patient_demographics.age IS 'Current age calculated from DOB';
COMMENT ON COLUMN patient_demographics.address_street1 IS 'Primary address street line 1';
COMMENT ON COLUMN patient_demographics.address_city IS 'Primary address city';
COMMENT ON COLUMN patient_demographics.address_state IS 'Primary address state abbreviation';
COMMENT ON COLUMN patient_demographics.address_zip IS 'Primary address ZIP code';
COMMENT ON COLUMN patient_demographics.phone_primary IS 'Primary phone number (placeholder in MVP)';
COMMENT ON COLUMN patient_demographics.insurance_company_name IS 'Primary insurance company name';
COMMENT ON COLUMN patient_demographics.marital_status IS 'Marital status (Single, Married, Divorced, Widowed, etc.)';
COMMENT ON COLUMN patient_demographics.religion IS 'Religion for spiritual care coordination';
COMMENT ON COLUMN patient_demographics.service_connected_percent IS 'Service connected disability percentage (0-100)';
COMMENT ON COLUMN patient_demographics.deceased_flag IS 'Deceased flag (Y/N)';
COMMENT ON COLUMN patient_demographics.death_date IS 'Date of death (if deceased)';

-- Verify table creation
SELECT 'patient_demographics table created successfully (v3.0 - Phase 2)' AS status;
