-- =====================================================
-- med-z1 AI Infrastructure Schema
-- =====================================================
-- Creates LangGraph checkpoints tables for conversation memory
-- in AI Clinical Insights feature.
--
-- Purpose:
--   - Enable persistent conversation history across page refreshes
--   - Maintain session-scoped chat memory (25-minute login session)
--   - Isolate conversations by user session + patient ICN
--   - Auto-clear history on patient changes or session expiration
--
-- Usage:
--   docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_ai_checkpoints_tables.sql
--
-- Related:
--   - Phase 6: Conversation Memory (docs/spec/ai-insight-design.md)
--   - ADR-007: PostgreSQL Schema Organization
--   - LangGraph AsyncPostgresSaver documentation
-- =====================================================

-- Create ai schema for AI/ML infrastructure tables
CREATE SCHEMA IF NOT EXISTS ai;

-- =====================================================
-- Table: ai.checkpoints
-- =====================================================
-- Stores LangGraph conversation state snapshots
-- Each checkpoint represents agent state at a point in conversation
--
-- Thread ID Format: {session_id}_{patient_icn}
--   Example: 7f3d8e2a4b9c1f5e_ICN100010
--
-- Storage: ~50KB per conversation thread (typical)

CREATE TABLE IF NOT EXISTS ai.checkpoints (
    thread_id       TEXT NOT NULL,
    checkpoint_id   TEXT NOT NULL,
    parent_id       TEXT,
    checkpoint      JSONB NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- Index for efficient thread lookup
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
    ON ai.checkpoints(thread_id);

-- Index for parent traversal (conversation history)
CREATE INDEX IF NOT EXISTS idx_checkpoints_parent
    ON ai.checkpoints(parent_id)
    WHERE parent_id IS NOT NULL;

-- Comments
COMMENT ON TABLE ai.checkpoints IS 'LangGraph conversation checkpoints for AI Clinical Insights feature';
COMMENT ON COLUMN ai.checkpoints.thread_id IS 'Format: {session_id}_{patient_icn} for session+patient isolation';
COMMENT ON COLUMN ai.checkpoints.checkpoint_id IS 'Unique identifier for this checkpoint (UUID v4)';
COMMENT ON COLUMN ai.checkpoints.parent_id IS 'Previous checkpoint_id in conversation chain (null for first message)';
COMMENT ON COLUMN ai.checkpoints.checkpoint IS 'JSONB snapshot of agent state (messages, tool calls, intermediate steps)';
COMMENT ON COLUMN ai.checkpoints.metadata IS 'Additional metadata (timestamp, user_agent, etc.)';

-- =====================================================
-- Table: ai.checkpoint_writes
-- =====================================================
-- Stores pending writes during checkpoint creation
-- Used by LangGraph for transactional checkpoint updates
--
-- Internal LangGraph table - managed automatically by AsyncPostgresSaver

CREATE TABLE IF NOT EXISTS ai.checkpoint_writes (
    thread_id       TEXT NOT NULL,
    checkpoint_id   TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    idx             INTEGER NOT NULL,
    channel         TEXT NOT NULL,
    value           JSONB,
    PRIMARY KEY (thread_id, checkpoint_id, task_id, idx)
);

-- Index for efficient thread+checkpoint lookup
CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_thread_checkpoint
    ON ai.checkpoint_writes(thread_id, checkpoint_id);

-- Comments
COMMENT ON TABLE ai.checkpoint_writes IS 'LangGraph checkpoint pending writes (internal LangGraph infrastructure)';
COMMENT ON COLUMN ai.checkpoint_writes.task_id IS 'LangGraph task identifier for parallel execution tracking';
COMMENT ON COLUMN ai.checkpoint_writes.idx IS 'Write index for ordering within a task';
COMMENT ON COLUMN ai.checkpoint_writes.channel IS 'LangGraph channel name (messages, tool_calls, etc.)';
COMMENT ON COLUMN ai.checkpoint_writes.value IS 'Pending write value (JSONB)';

-- =====================================================
-- Grant Permissions
-- =====================================================

-- Grant schema usage
GRANT USAGE ON SCHEMA ai TO postgres;

-- Grant table permissions
-- Note: LangGraph requires INSERT, UPDATE, DELETE for checkpoint management
GRANT SELECT, INSERT, UPDATE, DELETE ON ai.checkpoints TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai.checkpoint_writes TO postgres;

-- =====================================================
-- Cleanup Helper Functions (Optional)
-- =====================================================

-- Function to delete old checkpoints by session_id prefix
-- Useful for session expiration cleanup
CREATE OR REPLACE FUNCTION ai.cleanup_checkpoints_by_session(session_prefix TEXT)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM ai.checkpoints
    WHERE thread_id LIKE session_prefix || '%';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ai.cleanup_checkpoints_by_session IS 'Delete all checkpoints for a given session_id prefix (e.g., on session expiration)';

-- Function to get checkpoint statistics
CREATE OR REPLACE FUNCTION ai.get_checkpoint_stats()
RETURNS TABLE(
    total_threads BIGINT,
    total_checkpoints BIGINT,
    avg_checkpoints_per_thread NUMERIC,
    total_storage_mb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT thread_id)::BIGINT AS total_threads,
        COUNT(*)::BIGINT AS total_checkpoints,
        ROUND(COUNT(*)::NUMERIC / NULLIF(COUNT(DISTINCT thread_id), 0), 2) AS avg_checkpoints_per_thread,
        ROUND(pg_total_relation_size('ai.checkpoints')::NUMERIC / 1024 / 1024, 2) AS total_storage_mb
    FROM ai.checkpoints;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ai.get_checkpoint_stats IS 'Get statistics on checkpoint storage (threads, checkpoints, storage size)';

-- =====================================================
-- Verification
-- =====================================================

-- Verify tables created
DO $$
DECLARE
    checkpoint_count INTEGER;
    writes_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO checkpoint_count
    FROM information_schema.tables
    WHERE table_schema = 'ai' AND table_name = 'checkpoints';

    SELECT COUNT(*) INTO writes_count
    FROM information_schema.tables
    WHERE table_schema = 'ai' AND table_name = 'checkpoint_writes';

    IF checkpoint_count = 1 AND writes_count = 1 THEN
        RAISE NOTICE 'AI infrastructure tables created successfully.';
        RAISE NOTICE 'Schema: ai';
        RAISE NOTICE 'Tables: checkpoints (% rows), checkpoint_writes (% rows)',
            (SELECT COUNT(*) FROM ai.checkpoints),
            (SELECT COUNT(*) FROM ai.checkpoint_writes);
    ELSE
        RAISE EXCEPTION 'Table creation failed. Expected 2 tables, found %', checkpoint_count + writes_count;
    END IF;
END $$;
