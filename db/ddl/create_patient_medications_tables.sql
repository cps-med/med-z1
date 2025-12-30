-- Create tables: patient_medications_outpatient and patient_medications_inpatient
-- Purpose: Serving database tables for patient medications
-- Source: Gold layer Parquet files (medications/*.parquet)
-- Updated: 2025-12-24 - Moved to clinical schema

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- ==================================================================
-- TABLE 1: patient_medications_outpatient (RxOut - Outpatient)
-- ==================================================================

-- Drop table if exists (development only)
DROP TABLE IF EXISTS clinical.patient_medications_outpatient CASCADE;

CREATE TABLE clinical.patient_medications_outpatient (
    -- Primary key and patient identity
    medication_outpatient_id    SERIAL PRIMARY KEY,
    patient_icn                 VARCHAR(50) NOT NULL,       -- Patient ICN
    patient_key                 VARCHAR(50) NOT NULL,       -- Same as patient_icn

    -- Prescription IDs
    rx_outpat_id                BIGINT NOT NULL,            -- Source RxOutpatSID (duplicates exist in mock data)
    prescription_number         VARCHAR(50),                -- Prescription number
    local_drug_id               BIGINT,                     -- LocalDrugSID
    national_drug_id            BIGINT,                     -- NationalDrugSID

    -- Drug names
    drug_name_local             VARCHAR(150),               -- Local drug name with dose
    drug_name_national          VARCHAR(120),               -- National drug name
    generic_name                VARCHAR(120),               -- Generic name
    trade_name                  VARCHAR(120),               -- Trade name

    -- Drug details
    drug_strength               VARCHAR(50),                -- e.g., "500MG"
    drug_unit                   VARCHAR(50),                -- e.g., "TAB", "CAP"
    dosage_form                 VARCHAR(50),                -- e.g., "TABLET", "CAPSULE"
    drug_class                  VARCHAR(100),               -- e.g., "ANTIDIABETIC"
    drug_class_code             VARCHAR(20),                -- e.g., "HS502"
    dea_schedule                VARCHAR(10),                -- e.g., "C-II", "C-IV"
    ndc_code                    VARCHAR(20),                -- National Drug Code

    -- Prescription info
    issue_date                  TIMESTAMP,                  -- When prescription was issued
    rx_status                   VARCHAR(30),                -- Original status
    rx_status_computed          VARCHAR(30),                -- Computed status
    rx_type                     VARCHAR(30),                -- Prescription type

    -- Quantity and refills
    quantity_ordered            DECIMAL(12,4),              -- Quantity ordered
    days_supply                 INTEGER,                    -- Days supply
    refills_allowed             INTEGER,                    -- Refills allowed
    refills_remaining           INTEGER,                    -- Refills remaining
    unit_dose                   VARCHAR(50),                -- Unit dose

    -- Latest fill info
    latest_fill_number          INTEGER,                    -- Latest fill number
    latest_fill_date            TIMESTAMP,                  -- Latest fill date
    latest_fill_status          VARCHAR(30),                -- Latest fill status
    latest_quantity_dispensed   DECIMAL(12,4),              -- Latest quantity dispensed
    latest_days_supply          INTEGER,                    -- Latest days supply dispensed

    -- Sig (medication directions)
    sig                         TEXT,                       -- Complete signature/directions
    sig_route                   VARCHAR(50),                -- Route (e.g., "ORAL", "TOPICAL")
    sig_schedule                VARCHAR(50),                -- Schedule (e.g., "BID", "TID", "PRN")

    -- Dates
    expiration_date             TIMESTAMP,                  -- Expiration date
    discontinued_date           TIMESTAMP,                  -- Discontinued date
    discontinue_reason          VARCHAR(100),               -- Reason for discontinuation

    -- Computed flags
    is_controlled_substance     BOOLEAN DEFAULT FALSE,      -- DEA controlled substance
    is_active                   BOOLEAN DEFAULT FALSE,      -- Currently active
    days_until_expiration       INTEGER,                    -- Days until expiration

    -- Providers and locations
    provider_name               VARCHAR(100),               -- Prescribing provider
    ordering_provider_name      VARCHAR(100),               -- Ordering provider
    pharmacy_name               VARCHAR(100),               -- Pharmacy name
    clinic_name                 VARCHAR(100),               -- Clinic name
    facility_name               VARCHAR(100),               -- Facility name
    sta3n                       VARCHAR(10),                -- Station number

    -- Other flags
    cmop_indicator              CHAR(1),                    -- CMOP (mail-order)
    mail_indicator              CHAR(1),                    -- Mail delivery

    -- Metadata
    source_system               VARCHAR(50) DEFAULT 'CDWWork',
    last_updated                TIMESTAMP DEFAULT NOW()
);

-- Indexes for patient_medications_outpatient
CREATE INDEX idx_patient_medications_out_patient_date
    ON clinical.patient_medications_outpatient (patient_icn, issue_date DESC);

CREATE INDEX idx_patient_medications_out_active
    ON clinical.patient_medications_outpatient (patient_icn, is_active, issue_date DESC)
    WHERE is_active = TRUE;

CREATE INDEX idx_patient_medications_out_controlled
    ON clinical.patient_medications_outpatient (patient_icn, is_controlled_substance, issue_date DESC)
    WHERE is_controlled_substance = TRUE;

CREATE INDEX idx_patient_medications_out_drug_class
    ON clinical.patient_medications_outpatient (drug_class, issue_date DESC);

CREATE INDEX idx_patient_medications_out_rx_status
    ON clinical.patient_medications_outpatient (rx_status_computed, issue_date DESC);

-- Comments on patient_medications_outpatient
COMMENT ON TABLE clinical.patient_medications_outpatient IS 'Outpatient prescriptions from RxOut data';
COMMENT ON COLUMN clinical.patient_medications_outpatient.patient_icn IS 'Patient ICN (Integrated Care Number)';
COMMENT ON COLUMN clinical.patient_medications_outpatient.rx_outpat_id IS 'Source RxOutpatSID from CDWWork';
COMMENT ON COLUMN clinical.patient_medications_outpatient.is_controlled_substance IS 'DEA controlled substance (Schedule II-V)';
COMMENT ON COLUMN clinical.patient_medications_outpatient.is_active IS 'Currently active (not discontinued, not expired)';

-- ==================================================================
-- TABLE 2: patient_medications_inpatient (BCMA - Inpatient)
-- ==================================================================

-- Drop table if exists (development only)
DROP TABLE IF EXISTS clinical.patient_medications_inpatient CASCADE;

CREATE TABLE clinical.patient_medications_inpatient (
    -- Primary key and patient identity
    medication_inpatient_id     SERIAL PRIMARY KEY,
    patient_icn                 VARCHAR(50) NOT NULL,       -- Patient ICN
    patient_key                 VARCHAR(50) NOT NULL,       -- Same as patient_icn

    -- Administration IDs
    bcma_log_id                 BIGINT NOT NULL,            -- Source BCMAMedicationLogSID
    inpatient_sid               BIGINT,                     -- Inpatient stay SID
    order_number                VARCHAR(50),                -- Order number
    local_drug_id               BIGINT,                     -- LocalDrugSID
    national_drug_id            BIGINT,                     -- NationalDrugSID

    -- Drug names
    drug_name_local             VARCHAR(150),               -- Local drug name with dose
    drug_name_national          VARCHAR(120),               -- National drug name
    generic_name                VARCHAR(120),               -- Generic name
    trade_name                  VARCHAR(120),               -- Trade name

    -- Drug details
    drug_strength               VARCHAR(50),                -- e.g., "500MG"
    drug_unit                   VARCHAR(50),                -- e.g., "TAB", "CAP"
    dosage_form                 VARCHAR(50),                -- e.g., "TABLET", "CAPSULE"
    drug_class                  VARCHAR(100),               -- e.g., "ANTIDIABETIC"
    drug_class_code             VARCHAR(20),                -- e.g., "HS502"
    dea_schedule                VARCHAR(10),                -- e.g., "C-II", "C-IV"
    ndc_code                    VARCHAR(20),                -- National Drug Code

    -- Administration info
    action_type                 VARCHAR(30),                -- GIVEN, HELD, REFUSED, MISSING DOSE
    action_status               VARCHAR(30),                -- COMPLETED, etc.
    action_datetime             TIMESTAMP,                  -- When action occurred
    scheduled_datetime          TIMESTAMP,                  -- When scheduled
    ordered_datetime            TIMESTAMP,                  -- When ordered

    -- Dosage and route
    dosage_ordered              VARCHAR(100),               -- Dosage ordered
    dosage_given                VARCHAR(100),               -- Dosage given
    route                       VARCHAR(50),                -- Route (PO, IV, IM, etc.)
    unit_of_administration      VARCHAR(50),                -- Unit
    schedule_type               VARCHAR(30),                -- Schedule type
    schedule                    VARCHAR(50),                -- Schedule (e.g., "BID", "QID")

    -- Variance info
    administration_variance     BOOLEAN DEFAULT FALSE,      -- Variance occurred
    variance_type               VARCHAR(50),                -- Type of variance
    variance_reason             VARCHAR(100),               -- Reason for variance

    -- IV info
    is_iv_medication            BOOLEAN DEFAULT FALSE,      -- IV medication
    iv_type                     VARCHAR(30),                -- IV type
    infusion_rate               VARCHAR(50),                -- Infusion rate

    -- Computed flags
    is_controlled_substance     BOOLEAN DEFAULT FALSE,      -- DEA controlled substance

    -- Staff and locations
    administered_by             VARCHAR(100),               -- Staff who administered
    ordering_provider           VARCHAR(100),               -- Ordering provider
    ward_name                   VARCHAR(100),               -- Ward name
    facility_name               VARCHAR(100),               -- Facility name
    sta3n                       VARCHAR(10),                -- Station number

    -- Metadata
    source_system               VARCHAR(50) DEFAULT 'CDWWork',
    last_updated                TIMESTAMP DEFAULT NOW()
);

-- Indexes for patient_medications_inpatient
CREATE INDEX idx_patient_medications_inp_patient_date
    ON clinical.patient_medications_inpatient (patient_icn, action_datetime DESC);

CREATE INDEX idx_patient_medications_inp_action_type
    ON clinical.patient_medications_inpatient (action_type, action_datetime DESC);

CREATE INDEX idx_patient_medications_inp_controlled
    ON clinical.patient_medications_inpatient (patient_icn, is_controlled_substance, action_datetime DESC)
    WHERE is_controlled_substance = TRUE;

CREATE INDEX idx_patient_medications_inp_variance
    ON clinical.patient_medications_inpatient (patient_icn, administration_variance, action_datetime DESC)
    WHERE administration_variance = TRUE;

CREATE INDEX idx_patient_medications_inp_iv
    ON clinical.patient_medications_inpatient (patient_icn, is_iv_medication, action_datetime DESC)
    WHERE is_iv_medication = TRUE;

CREATE INDEX idx_patient_medications_inp_drug_class
    ON clinical.patient_medications_inpatient (drug_class, action_datetime DESC);

-- Comments on patient_medications_inpatient
COMMENT ON TABLE clinical.patient_medications_inpatient IS 'Inpatient medication administration from BCMA data';
COMMENT ON COLUMN clinical.patient_medications_inpatient.patient_icn IS 'Patient ICN (Integrated Care Number)';
COMMENT ON COLUMN clinical.patient_medications_inpatient.bcma_log_id IS 'Source BCMAMedicationLogSID from CDWWork';
COMMENT ON COLUMN clinical.patient_medications_inpatient.action_type IS 'GIVEN, HELD, REFUSED, or MISSING DOSE';
COMMENT ON COLUMN clinical.patient_medications_inpatient.administration_variance IS 'Variance occurred during administration';
COMMENT ON COLUMN clinical.patient_medications_inpatient.is_iv_medication IS 'IV (intravenous) medication';
COMMENT ON COLUMN clinical.patient_medications_inpatient.is_controlled_substance IS 'DEA controlled substance (Schedule II-V)';

-- Grant permissions
GRANT SELECT ON clinical.patient_medications_outpatient TO PUBLIC;
GRANT SELECT ON clinical.patient_medications_inpatient TO PUBLIC;
