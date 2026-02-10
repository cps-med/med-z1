-- ============================================================================
-- Clinical Task Tracking - Database Schema
-- ============================================================================
-- Purpose: Patient-centric clinical task management system
-- Created: 2026-02-10
-- Phase: Phase 1 - Core Task Management (MVP)
-- ============================================================================

-- Drop existing objects (for clean recreate during development)
DROP TRIGGER IF EXISTS trg_patient_tasks_completed_at ON clinical.patient_tasks;
DROP TRIGGER IF EXISTS trg_patient_tasks_updated_at ON clinical.patient_tasks;
DROP FUNCTION IF EXISTS set_patient_tasks_completed_at();
DROP FUNCTION IF EXISTS update_patient_tasks_updated_at();
DROP TABLE IF EXISTS clinical.patient_tasks;

-- ============================================================================
-- Table: clinical.patient_tasks
-- ============================================================================

CREATE TABLE clinical.patient_tasks (
    -- Primary key
    task_id SERIAL PRIMARY KEY,

    -- Patient association (ICN-based, patient-centric)
    patient_key VARCHAR(50) NOT NULL,  -- ICN, e.g., "ICN100001"

    -- Task content
    title VARCHAR(500) NOT NULL,       -- Brief task description
    description TEXT,                  -- Rich narrative text (optional)
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',  -- HIGH, MEDIUM, LOW
    status VARCHAR(50) NOT NULL DEFAULT 'TODO',      -- TODO, IN_PROGRESS, COMPLETED

    -- User attribution (audit trail)
    created_by_user_id UUID NOT NULL REFERENCES auth.users(user_id),
    created_by_display_name VARCHAR(255),  -- Denormalized for display
    completed_by_user_id UUID REFERENCES auth.users(user_id),
    completed_by_display_name VARCHAR(255),

    -- AI attribution (track AI-generated tasks)
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
    ai_suggestion_source TEXT,  -- Free text: "AI suggested based on overdue A1C screening"

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_priority CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT chk_status CHECK (status IN ('TODO', 'IN_PROGRESS', 'COMPLETED'))
);

-- ============================================================================
-- Indexes
-- ============================================================================

-- Index: Get all tasks for a patient (most common query)
CREATE INDEX idx_patient_tasks_patient_key ON clinical.patient_tasks(patient_key);

-- Index: Get user's created tasks (for "My Tasks" filter)
CREATE INDEX idx_patient_tasks_created_by ON clinical.patient_tasks(created_by_user_id);

-- Index: Get tasks by status (for filtering)
CREATE INDEX idx_patient_tasks_status ON clinical.patient_tasks(status);

-- Composite index: Patient + Status (optimized for dashboard widget)
CREATE INDEX idx_patient_tasks_patient_status ON clinical.patient_tasks(patient_key, status);

-- ============================================================================
-- Triggers: Auto-update timestamps
-- ============================================================================

-- Trigger function: Auto-update updated_at on any column change
CREATE OR REPLACE FUNCTION update_patient_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patient_tasks_updated_at
BEFORE UPDATE ON clinical.patient_tasks
FOR EACH ROW
EXECUTE FUNCTION update_patient_tasks_updated_at();

-- Trigger function: Auto-populate completed_at when status changes to COMPLETED
CREATE OR REPLACE FUNCTION set_patient_tasks_completed_at()
RETURNS TRIGGER AS $$
BEGIN
    -- Only set completed_at when status changes to COMPLETED
    IF NEW.status = 'COMPLETED' AND (OLD.status IS NULL OR OLD.status != 'COMPLETED') THEN
        NEW.completed_at = NOW();
    END IF;

    -- Clear completed_at if status changes away from COMPLETED
    IF NEW.status != 'COMPLETED' AND OLD.status = 'COMPLETED' THEN
        NEW.completed_at = NULL;
        NEW.completed_by_user_id = NULL;
        NEW.completed_by_display_name = NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patient_tasks_completed_at
BEFORE UPDATE ON clinical.patient_tasks
FOR EACH ROW
EXECUTE FUNCTION set_patient_tasks_completed_at();

-- ============================================================================
-- Table Comments (Documentation)
-- ============================================================================

COMMENT ON TABLE clinical.patient_tasks IS 'Patient-centric clinical task tracking system. Phase 1: Core task management (TODO → IN_PROGRESS → COMPLETED lifecycle). Tasks belong to patients, visible to all clinicians viewing that patient. User attribution tracked for audit trail.';

COMMENT ON COLUMN clinical.patient_tasks.task_id IS 'Primary key (auto-increment). Unique identifier for each task.';
COMMENT ON COLUMN clinical.patient_tasks.patient_key IS 'Patient ICN (e.g., ICN100001). Tasks belong to patient, visible to all clinicians viewing patient.';
COMMENT ON COLUMN clinical.patient_tasks.title IS 'Brief task description (max 500 chars). Required field.';
COMMENT ON COLUMN clinical.patient_tasks.description IS 'Rich narrative text with additional context (optional). Supports multi-line text.';
COMMENT ON COLUMN clinical.patient_tasks.priority IS 'Priority level: HIGH (red), MEDIUM (yellow), LOW (gray). Affects sort order in UI.';
COMMENT ON COLUMN clinical.patient_tasks.status IS 'Task lifecycle: TODO → IN_PROGRESS → COMPLETED. Three-state model.';
COMMENT ON COLUMN clinical.patient_tasks.created_by_user_id IS 'User who created task (UUID from auth.users). Required for audit trail. Used for "My Tasks" filter.';
COMMENT ON COLUMN clinical.patient_tasks.created_by_display_name IS 'Denormalized user display name (e.g., "Dr. Alpha"). Avoids JOIN for common queries.';
COMMENT ON COLUMN clinical.patient_tasks.completed_by_user_id IS 'User who completed task (UUID from auth.users). Populated when status → COMPLETED.';
COMMENT ON COLUMN clinical.patient_tasks.completed_by_display_name IS 'Denormalized user display name. Populated when status → COMPLETED.';
COMMENT ON COLUMN clinical.patient_tasks.is_ai_generated IS 'TRUE if task created via AI Insights chatbot "Add to Tasks" button. FALSE if user-created.';
COMMENT ON COLUMN clinical.patient_tasks.ai_suggestion_source IS 'Free text explanation of AI reasoning (e.g., "Active diabetes diagnosis + no A1C in past 6 months"). Only populated if is_ai_generated=TRUE.';
COMMENT ON COLUMN clinical.patient_tasks.created_at IS 'Timestamp when task was created (auto-populated). Default: NOW().';
COMMENT ON COLUMN clinical.patient_tasks.updated_at IS 'Timestamp of last modification (auto-updated via trigger). Tracks any UPDATE to row.';
COMMENT ON COLUMN clinical.patient_tasks.completed_at IS 'Timestamp when task was completed (auto-populated via trigger when status → COMPLETED). NULL if not completed.';

-- ============================================================================
-- Verification Query
-- ============================================================================

-- Verify table structure
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'clinical'
  AND table_name = 'patient_tasks'
ORDER BY ordinal_position;

-- Verify indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'clinical'
  AND tablename = 'patient_tasks';

-- Verify triggers
SELECT
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'clinical'
  AND event_object_table = 'patient_tasks';

-- Success message (PostgreSQL syntax)
DO $$
BEGIN
    RAISE NOTICE 'SUCCESS: clinical.patient_tasks table created with indexes and triggers';
END $$;
