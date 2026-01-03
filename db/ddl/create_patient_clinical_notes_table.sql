-- Create table: patient_clinical_notes
-- Purpose: Serving database table for patient clinical notes
-- Source: Gold layer Parquet files (clinical_notes/*.parquet)
-- Created: 2026-01-02

-- Create clinical schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical;

-- Drop table if exists (development only)
DROP TABLE IF EXISTS clinical.patient_clinical_notes;

CREATE TABLE clinical.patient_clinical_notes (
    note_id                     SERIAL PRIMARY KEY,
    patient_key                 VARCHAR(50) NOT NULL,       -- ICN
    tiu_document_sid            BIGINT NOT NULL UNIQUE,     -- Source TIUDocumentSID
    document_definition_sid     INTEGER NOT NULL,           -- Note type definition ID
    document_title              VARCHAR(200) NOT NULL,      -- e.g., "GEN MED PROGRESS NOTE"
    document_class              VARCHAR(50) NOT NULL,       -- "Progress Notes", "Consults", etc.
    vha_standard_title          VARCHAR(200),               -- VHA enterprise standard title
    status                      VARCHAR(50) NOT NULL,       -- "COMPLETED", etc.
    reference_datetime          TIMESTAMP NOT NULL,         -- Clinical date of note
    entry_datetime              TIMESTAMP NOT NULL,         -- Date note was authored
    days_since_note             INTEGER,                    -- Days since note written
    note_age_category           VARCHAR(20),                -- "<30 days", "30-90 days", etc.
    author_sid                  BIGINT,                     -- AuthorSID
    author_name                 VARCHAR(200),               -- Author full name
    cosigner_sid                BIGINT,                     -- CosignerSID (if applicable)
    cosigner_name               VARCHAR(200),               -- Cosigner full name
    visit_sid                   BIGINT,                     -- Associated visit
    sta3n                       VARCHAR(10),                -- Station number
    facility_name               VARCHAR(200),               -- Facility name
    document_text               TEXT,                       -- Full note narrative text
    text_length                 INTEGER,                    -- Note text character count
    text_preview                VARCHAR(500),               -- First 200 characters
    tiu_document_ien            VARCHAR(50),                -- TIU IEN (VistA identifier)
    source_system               VARCHAR(50),                -- "CDWWork" or "CDWWork2"
    last_updated                TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance

-- Primary query pattern: Get all notes for a patient, sorted by date
CREATE INDEX idx_clinical_notes_patient_date
    ON clinical.patient_clinical_notes (patient_key, reference_datetime DESC);

-- Filter by document class (Progress Notes, Consults, etc.)
CREATE INDEX idx_clinical_notes_class_date
    ON clinical.patient_clinical_notes (document_class, reference_datetime DESC);

-- Filter by note age category
CREATE INDEX idx_clinical_notes_age_category
    ON clinical.patient_clinical_notes (note_age_category, reference_datetime DESC)
    WHERE note_age_category IS NOT NULL;

-- Author queries
CREATE INDEX idx_clinical_notes_author
    ON clinical.patient_clinical_notes (author_sid, reference_datetime DESC)
    WHERE author_sid IS NOT NULL;

-- Facility queries
CREATE INDEX idx_clinical_notes_facility
    ON clinical.patient_clinical_notes (sta3n, reference_datetime DESC);

-- Recent notes for dashboard widget
CREATE INDEX idx_clinical_notes_recent
    ON clinical.patient_clinical_notes (patient_key, document_class, reference_datetime DESC);

-- Full text search (for future use)
-- Note: Full text search index will be added in Phase 2
-- CREATE INDEX idx_clinical_notes_text
--     ON clinical.patient_clinical_notes USING GIN (to_tsvector('english', document_text));

-- Comments
COMMENT ON TABLE clinical.patient_clinical_notes IS 'Patient clinical notes from Gold layer';
COMMENT ON COLUMN clinical.patient_clinical_notes.patient_key IS 'Patient ICN (Integrated Care Number)';
COMMENT ON COLUMN clinical.patient_clinical_notes.tiu_document_sid IS 'Source TIUDocumentSID from CDWWork or CDWWork2';
COMMENT ON COLUMN clinical.patient_clinical_notes.document_class IS 'Note classification: Progress Notes, Consults, Discharge Summaries, Imaging';
COMMENT ON COLUMN clinical.patient_clinical_notes.reference_datetime IS 'Clinical date of the note (primary sort key)';
COMMENT ON COLUMN clinical.patient_clinical_notes.entry_datetime IS 'Date the note was authored/entered';
COMMENT ON COLUMN clinical.patient_clinical_notes.days_since_note IS 'Number of days since note was written (for filtering recent vs. historical)';
COMMENT ON COLUMN clinical.patient_clinical_notes.note_age_category IS 'Age category: <30 days, 30-90 days, 90-180 days, >180 days';
COMMENT ON COLUMN clinical.patient_clinical_notes.document_text IS 'Full narrative text of the clinical note (SOAP format for most notes)';
COMMENT ON COLUMN clinical.patient_clinical_notes.text_preview IS 'First 200 characters of note text for dashboard and list views';
COMMENT ON COLUMN clinical.patient_clinical_notes.vha_standard_title IS 'VHA enterprise-wide standardized title';
COMMENT ON COLUMN clinical.patient_clinical_notes.facility_name IS 'VA medical center or clinic name';

-- Grant permissions
GRANT SELECT ON clinical.patient_clinical_notes TO PUBLIC;
