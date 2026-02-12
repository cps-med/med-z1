-- Create table: reference.ddi
-- Purpose: Drug-drug interaction reference table for AI Clinical Insights DDI checks
-- Source: Gold Parquet ETL output (gold/ddi/ddi_reference.parquet)
-- Usage: Runtime lookup table for DDIAnalyzer

-- Create reference schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS reference;

-- Drop table if exists (development only)
DROP TABLE IF EXISTS reference.ddi CASCADE;

CREATE TABLE reference.ddi (
    ddi_id                   BIGSERIAL PRIMARY KEY,
    drug_1                   TEXT NOT NULL,
    drug_2                   TEXT NOT NULL,
    interaction_description  TEXT NOT NULL,
    source_name              VARCHAR(100) DEFAULT 'DrugBank (Kaggle)',
    last_updated             TIMESTAMP DEFAULT NOW()
);

-- Ensure each interaction pair is loaded once
CREATE UNIQUE INDEX idx_reference_ddi_pair
    ON reference.ddi (drug_1, drug_2);

-- Lookup indexes for future direct SQL checks and diagnostics
CREATE INDEX idx_reference_ddi_drug_1
    ON reference.ddi (drug_1);

CREATE INDEX idx_reference_ddi_drug_2
    ON reference.ddi (drug_2);

-- Basic data quality constraints
ALTER TABLE reference.ddi
    ADD CONSTRAINT chk_reference_ddi_drug_1_nonempty
    CHECK (length(trim(drug_1)) > 0);

ALTER TABLE reference.ddi
    ADD CONSTRAINT chk_reference_ddi_drug_2_nonempty
    CHECK (length(trim(drug_2)) > 0);

ALTER TABLE reference.ddi
    ADD CONSTRAINT chk_reference_ddi_description_nonempty
    CHECK (length(trim(interaction_description)) > 0);

COMMENT ON TABLE reference.ddi IS 'Drug-drug interaction reference data used by AI DDI analysis';
COMMENT ON COLUMN reference.ddi.drug_1 IS 'Normalized lowercase name for first drug in interaction pair';
COMMENT ON COLUMN reference.ddi.drug_2 IS 'Normalized lowercase name for second drug in interaction pair';
COMMENT ON COLUMN reference.ddi.interaction_description IS 'DrugBank interaction description text';
COMMENT ON COLUMN reference.ddi.source_name IS 'Reference data source label';
COMMENT ON COLUMN reference.ddi.last_updated IS 'Row update timestamp';

GRANT SELECT ON reference.ddi TO PUBLIC;
