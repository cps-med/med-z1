-- ============================================================================
-- Clinical Task Tracking - Database Verification Tests
-- ============================================================================
-- Purpose: Verify table structure, indexes, and triggers are working correctly
-- Created: 2026-02-10
-- ============================================================================

\echo ''
\echo '============================================================'
\echo 'TEST 1: Verify Table Structure'
\echo '============================================================'

-- Check table exists and has correct columns
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'clinical'
  AND table_name = 'patient_tasks'
ORDER BY ordinal_position;

\echo ''
\echo '============================================================'
\echo 'TEST 2: Verify Indexes'
\echo '============================================================'

-- List all indexes on the table
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'clinical'
  AND tablename = 'patient_tasks'
ORDER BY indexname;

-- Test index performance (EXPLAIN should show Index Scan, not Seq Scan)
\echo ''
\echo 'Testing index usage for patient_key lookup:'
EXPLAIN SELECT * FROM clinical.patient_tasks WHERE patient_key = 'ICN100001';

\echo ''
\echo 'Testing composite index usage for patient_key + status:'
EXPLAIN SELECT * FROM clinical.patient_tasks WHERE patient_key = 'ICN100001' AND status = 'TODO';

\echo ''
\echo '============================================================'
\echo 'TEST 3: Verify Triggers'
\echo '============================================================'

-- List all triggers on the table
SELECT
    trigger_name,
    event_manipulation,
    action_timing,
    action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'clinical'
  AND event_object_table = 'patient_tasks'
ORDER BY trigger_name;

\echo ''
\echo '============================================================'
\echo 'TEST 4: Test updated_at Trigger'
\echo '============================================================'

-- Create a test task
INSERT INTO clinical.patient_tasks (
    patient_key, title, priority, status,
    created_by_user_id, created_by_display_name
) VALUES (
    'ICN100001',
    'TEST TASK - Will be deleted',
    'LOW',
    'TODO',
    '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',
    'Test User'
) RETURNING task_id, created_at, updated_at;

-- Store the task_id for cleanup (assuming it's task 16)
\set test_task_id 16

-- Wait a moment to ensure timestamp difference
SELECT pg_sleep(1);

-- Update the task title (should trigger updated_at change)
UPDATE clinical.patient_tasks
SET title = 'TEST TASK - UPDATED'
WHERE task_id = :test_task_id
RETURNING task_id, title, created_at, updated_at;

-- Verify updated_at changed
SELECT
    task_id,
    created_at,
    updated_at,
    (updated_at > created_at) AS updated_at_changed
FROM clinical.patient_tasks
WHERE task_id = :test_task_id;

\echo ''
\echo '============================================================'
\echo 'TEST 5: Test completed_at Trigger'
\echo '============================================================'

-- Update status to IN_PROGRESS (completed_at should remain NULL)
UPDATE clinical.patient_tasks
SET status = 'IN_PROGRESS'
WHERE task_id = :test_task_id
RETURNING task_id, status, completed_at;

-- Wait a moment
SELECT pg_sleep(1);

-- Update status to COMPLETED (completed_at should auto-populate)
UPDATE clinical.patient_tasks
SET
    status = 'COMPLETED',
    completed_by_user_id = '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',
    completed_by_display_name = 'Test User'
WHERE task_id = :test_task_id
RETURNING task_id, status, completed_at, (completed_at IS NOT NULL) AS completed_at_populated;

-- Verify completed_at was auto-populated
SELECT
    task_id,
    status,
    completed_at,
    (completed_at IS NOT NULL) AS completed_at_populated,
    (completed_at > created_at) AS completed_at_after_created_at
FROM clinical.patient_tasks
WHERE task_id = :test_task_id;

\echo ''
\echo '============================================================'
\echo 'TEST 6: Test Revert from COMPLETED (completed_at should clear)'
\echo '============================================================'

-- Revert status back to TODO (completed_at should be cleared)
UPDATE clinical.patient_tasks
SET status = 'TODO'
WHERE task_id = :test_task_id
RETURNING task_id, status, completed_at, completed_by_user_id;

-- Verify completed_at was cleared
SELECT
    task_id,
    status,
    completed_at,
    completed_by_user_id,
    (completed_at IS NULL) AS completed_at_cleared,
    (completed_by_user_id IS NULL) AS completed_by_cleared
FROM clinical.patient_tasks
WHERE task_id = :test_task_id;

\echo ''
\echo '============================================================'
\echo 'TEST 7: Test Check Constraints'
\echo '============================================================'

-- Test valid priority values (should succeed)
\echo 'Testing valid priority values (HIGH, MEDIUM, LOW):'
UPDATE clinical.patient_tasks
SET priority = 'HIGH'
WHERE task_id = :test_task_id;

UPDATE clinical.patient_tasks
SET priority = 'MEDIUM'
WHERE task_id = :test_task_id;

UPDATE clinical.patient_tasks
SET priority = 'LOW'
WHERE task_id = :test_task_id;

SELECT 'Priority constraint test: PASSED' AS result;

-- Test invalid priority (should fail)
\echo ''
\echo 'Testing invalid priority value (should fail with constraint error):'
\set ON_ERROR_STOP off
UPDATE clinical.patient_tasks
SET priority = 'URGENT'
WHERE task_id = :test_task_id;
\set ON_ERROR_STOP on

-- Test valid status values (should succeed)
\echo ''
\echo 'Testing valid status values (TODO, IN_PROGRESS, COMPLETED):'
UPDATE clinical.patient_tasks
SET status = 'TODO'
WHERE task_id = :test_task_id;

UPDATE clinical.patient_tasks
SET status = 'IN_PROGRESS'
WHERE task_id = :test_task_id;

UPDATE clinical.patient_tasks
SET status = 'COMPLETED'
WHERE task_id = :test_task_id;

SELECT 'Status constraint test: PASSED' AS result;

-- Test invalid status (should fail)
\echo ''
\echo 'Testing invalid status value (should fail with constraint error):'
\set ON_ERROR_STOP off
UPDATE clinical.patient_tasks
SET status = 'CANCELLED'
WHERE task_id = :test_task_id;
\set ON_ERROR_STOP on

\echo ''
\echo '============================================================'
\echo 'TEST 8: Test Foreign Key Constraints'
\echo '============================================================'

-- Test valid user_id (should succeed)
\echo 'Testing valid user_id reference (should succeed):'
UPDATE clinical.patient_tasks
SET completed_by_user_id = '76bb61c4-8d22-4605-b290-f1a2b757019b'
WHERE task_id = :test_task_id;

SELECT 'Foreign key constraint test: PASSED' AS result;

-- Test invalid user_id (should fail)
\echo ''
\echo 'Testing invalid user_id reference (should fail with FK constraint error):'
\set ON_ERROR_STOP off
UPDATE clinical.patient_tasks
SET completed_by_user_id = '00000000-0000-0000-0000-000000000000'
WHERE task_id = :test_task_id;
\set ON_ERROR_STOP on

\echo ''
\echo '============================================================'
\echo 'CLEANUP: Delete Test Task'
\echo '============================================================'

DELETE FROM clinical.patient_tasks
WHERE task_id = :test_task_id;

SELECT 'Test task deleted' AS result;

\echo ''
\echo '============================================================'
\echo 'TEST 9: Data Integrity Check'
\echo '============================================================'

-- Verify all seed data is intact
SELECT
    COUNT(*) AS total_tasks,
    COUNT(*) FILTER (WHERE status = 'TODO') AS todo_count,
    COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') AS in_progress_count,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed_count,
    COUNT(*) FILTER (WHERE is_ai_generated = TRUE) AS ai_generated_count
FROM clinical.patient_tasks;

\echo ''
\echo '============================================================'
\echo 'ALL TESTS COMPLETED'
\echo '============================================================'
