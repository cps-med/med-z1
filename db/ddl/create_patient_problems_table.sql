-- =============================================
-- Create PostgreSQL Serving Database Table: patient_problems
-- Description: Patient problem list and diagnoses from VistA and Cerner sources
--              with Charlson Comorbidity Index and chronic condition flags
-- Author: Claude Code
-- Date: 2026-02-07
-- =============================================

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (for development)
DROP TABLE IF EXISTS clinical.patient_problems CASCADE;

-- =============================================
-- Table: patient_problems
-- Description: Unified patient problem list with dual coding (ICD-10 + SNOMED),
--              Charlson Index, and chronic condition flags for AI/ML
-- =============================================

CREATE TABLE clinical.patient_problems (
    -- Primary keys and identifiers
    problem_id              SERIAL PRIMARY KEY,
    problem_sid             BIGINT NOT NULL,                -- Source ProblemSID from CDW
    patient_sid             BIGINT,                         -- Source PatientSID for joins
    patient_icn             VARCHAR(50) NOT NULL,           -- ICN (primary patient identifier)
    patient_key             VARCHAR(50) NOT NULL,           -- Same as ICN (for consistency with other tables)

    -- Problem identification
    problem_number          VARCHAR(50),                    -- Source system problem identifier

    -- Dual coding system (ICD-10 + SNOMED)
    icd10_code              VARCHAR(20),                    -- ICD-10-CM code (e.g., I50.9, E11.9)
    icd10_description       VARCHAR(255),                   -- ICD-10 description
    icd10_category          VARCHAR(100),                   -- ICD-10 category (e.g., 'Cardiovascular', 'Endocrine')
    snomed_code             VARCHAR(50),                    -- SNOMED CT concept code
    snomed_description      VARCHAR(255),                   -- SNOMED CT description
    diagnosis_description   VARCHAR(255),                   -- Primary diagnosis description (from source)

    -- Problem status and classification
    problem_status          VARCHAR(20) NOT NULL,           -- 'Active', 'Inactive', 'Resolved'
    acute_condition         BOOLEAN DEFAULT FALSE,
    chronic_condition       BOOLEAN DEFAULT FALSE,
    service_connected       BOOLEAN DEFAULT FALSE,          -- VA service-connected disability

    -- Temporal tracking
    onset_date              DATE,                           -- When problem first occurred
    recorded_date           DATE,                           -- When problem was first documented
    last_modified_date      DATE,                           -- Last update to problem
    resolved_date           DATE,                           -- When problem was resolved
    entered_datetime        TIMESTAMP,                      -- Full timestamp of entry

    -- Provider and location
    provider_id             VARCHAR(50),
    provider_name           VARCHAR(100),
    clinic_location         VARCHAR(100),
    facility_id             VARCHAR(10),                    -- Sta3n or FacilityCode

    -- Entered by information
    entered_by_name         VARCHAR(100),

    -- Source system tracking
    source_ehr              VARCHAR(20) NOT NULL,           -- 'VistA' or 'Cerner'
    source_system           VARCHAR(20) NOT NULL,           -- 'CDWWork' or 'CDWWork2'

    -- ICD-10 reference enrichment (from Dim.ICD10)
    icd10_chronic_flag      VARCHAR(1),                     -- 'Y' if ICD-10 is marked chronic
    icd10_charlson_condition VARCHAR(100),                  -- Charlson condition name (if applicable)

    -- Patient-level Charlson Index aggregations (denormalized for performance)
    charlson_index              INTEGER DEFAULT 0,          -- Total Charlson score (0-37+)
    charlson_condition_count    INTEGER DEFAULT 0,          -- Number of unique Charlson conditions

    -- Patient-level problem count aggregations
    total_problem_count         INTEGER DEFAULT 0,
    active_problem_count        INTEGER DEFAULT 0,
    inactive_problem_count      INTEGER DEFAULT 0,
    resolved_problem_count      INTEGER DEFAULT 0,
    chronic_problem_count       INTEGER DEFAULT 0,
    service_connected_count     INTEGER DEFAULT 0,

    -- Chronic condition flags (for AI/ML and clinical decision support)
    -- Cardiovascular
    has_chf                 BOOLEAN DEFAULT FALSE,          -- Congestive Heart Failure
    has_cad                 BOOLEAN DEFAULT FALSE,          -- Coronary Artery Disease
    has_afib                BOOLEAN DEFAULT FALSE,          -- Atrial Fibrillation
    has_hypertension        BOOLEAN DEFAULT FALSE,          -- Essential Hypertension

    -- Respiratory
    has_copd                BOOLEAN DEFAULT FALSE,          -- Chronic Obstructive Pulmonary Disease
    has_asthma              BOOLEAN DEFAULT FALSE,          -- Asthma

    -- Endocrine/Metabolic
    has_diabetes            BOOLEAN DEFAULT FALSE,          -- Type 2 Diabetes Mellitus
    has_hyperlipidemia      BOOLEAN DEFAULT FALSE,          -- Hyperlipidemia

    -- Renal
    has_ckd                 BOOLEAN DEFAULT FALSE,          -- Chronic Kidney Disease

    -- Mental Health
    has_depression          BOOLEAN DEFAULT FALSE,          -- Major Depressive Disorder
    has_ptsd                BOOLEAN DEFAULT FALSE,          -- Post-Traumatic Stress Disorder
    has_anxiety             BOOLEAN DEFAULT FALSE,          -- Anxiety Disorders

    -- Oncology
    has_cancer              BOOLEAN DEFAULT FALSE,          -- Active malignant neoplasms

    -- Musculoskeletal
    has_osteoarthritis      BOOLEAN DEFAULT FALSE,          -- Osteoarthritis
    has_back_pain           BOOLEAN DEFAULT FALSE,          -- Chronic Back Pain

    -- Metadata timestamps
    silver_load_datetime    TIMESTAMP,
    gold_load_datetime      TIMESTAMP,
    last_updated            TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- Indexes for optimal query performance
-- =============================================

-- Primary patient lookups
CREATE INDEX idx_problems_patient_icn
    ON clinical.patient_problems (patient_icn);

CREATE INDEX idx_problems_patient_key
    ON clinical.patient_problems (patient_key);

-- Active problems (most common query pattern)
CREATE INDEX idx_problems_patient_active
    ON clinical.patient_problems (patient_icn, problem_status, onset_date DESC)
    WHERE problem_status = 'Active';

-- Status filtering
CREATE INDEX idx_problems_status
    ON clinical.patient_problems (problem_status, onset_date DESC);

-- Code-based lookups
CREATE INDEX idx_problems_icd10
    ON clinical.patient_problems (icd10_code)
    WHERE icd10_code IS NOT NULL;

CREATE INDEX idx_problems_snomed
    ON clinical.patient_problems (snomed_code)
    WHERE snomed_code IS NOT NULL;

-- Category grouping (for UI filtering)
CREATE INDEX idx_problems_category
    ON clinical.patient_problems (icd10_category, problem_status);

-- Charlson Index queries
CREATE INDEX idx_problems_charlson
    ON clinical.patient_problems (patient_icn, charlson_index DESC)
    WHERE charlson_index > 0;

-- Chronic condition flags (for AI/ML feature extraction)
CREATE INDEX idx_problems_chronic_flags
    ON clinical.patient_problems (patient_icn)
    WHERE has_chf = TRUE OR has_diabetes = TRUE OR has_copd = TRUE OR has_ckd = TRUE;

-- Service-connected problems
CREATE INDEX idx_problems_service_connected
    ON clinical.patient_problems (patient_icn, service_connected)
    WHERE service_connected = TRUE;

-- Temporal queries (onset date range filtering)
CREATE INDEX idx_problems_onset_date
    ON clinical.patient_problems (onset_date DESC)
    WHERE onset_date IS NOT NULL;

-- Source system tracking
CREATE INDEX idx_problems_source
    ON clinical.patient_problems (source_ehr, source_system);

-- =============================================
-- Comments for documentation
-- =============================================

COMMENT ON TABLE clinical.patient_problems IS
'Unified patient problem list and diagnoses from VistA and Cerner sources. Includes Charlson Comorbidity Index and chronic condition flags for AI/ML.';

COMMENT ON COLUMN clinical.patient_problems.patient_icn IS
'Patient Integrated Care Number (ICN) - primary patient identifier across VA systems';

COMMENT ON COLUMN clinical.patient_problems.icd10_code IS
'ICD-10-CM diagnosis code (e.g., I50.9 = Heart failure unspecified, E11.9 = Type 2 diabetes without complications)';

COMMENT ON COLUMN clinical.patient_problems.snomed_code IS
'SNOMED CT concept code for clinical terminology (preferred for clinical use)';

COMMENT ON COLUMN clinical.patient_problems.problem_status IS
'Current status: Active (ongoing treatment), Inactive (not being treated), Resolved (no longer present)';

COMMENT ON COLUMN clinical.patient_problems.charlson_index IS
'Charlson Comorbidity Index score (0-37+). Higher score = more complex patient. Score interpretation: 0 = No comorbidities, 1-2 = Low, 3-4 = Moderate, 5+ = High complexity. Predicts 1-year mortality risk.';

COMMENT ON COLUMN clinical.patient_problems.charlson_condition_count IS
'Number of unique Charlson conditions (out of 19 possible). Different from total problems - multiple ICD-10 codes can map to same Charlson condition.';

COMMENT ON COLUMN clinical.patient_problems.service_connected IS
'TRUE if problem is related to military service (eligible for VA disability compensation)';

COMMENT ON COLUMN clinical.patient_problems.chronic_condition IS
'TRUE if problem is chronic (long-lasting, typically 1+ year duration)';

COMMENT ON COLUMN clinical.patient_problems.source_ehr IS
'Source EHR system: VistA (legacy VA system) or Cerner (Oracle Health, newer VA system)';

COMMENT ON COLUMN clinical.patient_problems.has_chf IS
'Patient has Congestive Heart Failure (ICD-10: I50.x) - AI/ML feature flag';

COMMENT ON COLUMN clinical.patient_problems.has_diabetes IS
'Patient has Type 2 Diabetes Mellitus (ICD-10: E11.x) - AI/ML feature flag';

COMMENT ON COLUMN clinical.patient_problems.has_copd IS
'Patient has Chronic Obstructive Pulmonary Disease (ICD-10: J44.x) - AI/ML feature flag';

COMMENT ON COLUMN clinical.patient_problems.has_ckd IS
'Patient has Chronic Kidney Disease (ICD-10: N18.x) - AI/ML feature flag';

COMMENT ON COLUMN clinical.patient_problems.has_ptsd IS
'Patient has Post-Traumatic Stress Disorder (ICD-10: F43.10) - AI/ML feature flag';

-- =============================================
-- Success message
-- =============================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Table clinical.patient_problems created successfully';
    RAISE NOTICE 'Indexes created for optimal query performance';
    RAISE NOTICE 'Schema supports:';
    RAISE NOTICE '  - Dual coding (ICD-10 + SNOMED)';
    RAISE NOTICE '  - Charlson Comorbidity Index calculation';
    RAISE NOTICE '  - 15 chronic condition flags for AI/ML';
    RAISE NOTICE '  - Multi-source harmonization (VistA + Cerner)';
    RAISE NOTICE '  - Patient-level aggregations (denormalized for performance)';
    RAISE NOTICE '=================================================================';
END $$;
