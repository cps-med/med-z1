-- =============================================================================
-- Add Location Name Columns to patient_encounters Table
-- =============================================================================
-- Purpose: Add admit and discharge location name columns for better UI display
-- Date: 2025-12-16
-- =============================================================================

-- Add admit location name columns
ALTER TABLE patient_encounters
ADD COLUMN IF NOT EXISTS admit_location_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS admit_location_type VARCHAR(50);

-- Add discharge location name columns
ALTER TABLE patient_encounters
ADD COLUMN IF NOT EXISTS discharge_location_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS discharge_location_type VARCHAR(50);

-- Create indexes for location name queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_patient_encounters_admit_location_type
ON patient_encounters (admit_location_type);

CREATE INDEX IF NOT EXISTS idx_patient_encounters_discharge_location_type
ON patient_encounters (discharge_location_type);

-- Verify the changes
\d patient_encounters
