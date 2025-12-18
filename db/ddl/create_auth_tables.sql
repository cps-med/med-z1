-- =====================================================
-- med-z1 Authentication Schema
-- =====================================================
-- Creates users, sessions, and audit_logs tables
-- for user authentication and session management.
--
-- Usage:
--   docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_auth_tables.sql
-- =====================================================

-- Create auth schema
CREATE SCHEMA IF NOT EXISTS auth;

-- =====================================================
-- Table: auth.users
-- =====================================================

CREATE TABLE IF NOT EXISTS auth.users (
    user_id                 UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    email                   VARCHAR(255)    UNIQUE NOT NULL,
    password_hash           VARCHAR(255)    NOT NULL,

    -- Profile Information
    display_name            VARCHAR(255)    NOT NULL,
    first_name              VARCHAR(100),
    last_name               VARCHAR(100),
    home_site_sta3n         INTEGER,

    -- Account Status
    is_active               BOOLEAN         DEFAULT TRUE,
    is_locked               BOOLEAN         DEFAULT FALSE,
    failed_login_attempts   INTEGER         DEFAULT 0,
    last_login_at           TIMESTAMP,

    -- Audit Fields
    created_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    created_by              VARCHAR(100)    DEFAULT 'system'
);

CREATE INDEX idx_users_email ON auth.users(email);
CREATE INDEX idx_users_home_site ON auth.users(home_site_sta3n);
CREATE INDEX idx_users_active ON auth.users(is_active);

COMMENT ON TABLE auth.users IS 'User credentials and profile information for med-z1 application';
COMMENT ON COLUMN auth.users.email IS 'User email address (username for login)';
COMMENT ON COLUMN auth.users.password_hash IS 'Bcrypt hash of user password (never store plaintext)';
COMMENT ON COLUMN auth.users.home_site_sta3n IS 'Primary VA site assignment (Sta3n code)';

-- =====================================================
-- Table: auth.sessions
-- =====================================================

CREATE TABLE IF NOT EXISTS auth.sessions (
    session_id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID            NOT NULL REFERENCES auth.users(user_id) ON DELETE CASCADE,

    -- Session Lifecycle
    created_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    last_activity_at        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    expires_at              TIMESTAMP       NOT NULL,

    -- Session Status
    is_active               BOOLEAN         DEFAULT TRUE,

    -- Session Metadata
    ip_address              VARCHAR(45),
    user_agent              TEXT
);

CREATE INDEX idx_sessions_user ON auth.sessions(user_id, is_active);
CREATE INDEX idx_sessions_expiry ON auth.sessions(expires_at, is_active);
CREATE INDEX idx_sessions_activity ON auth.sessions(last_activity_at);

COMMENT ON TABLE auth.sessions IS 'Active user sessions with timeout enforcement';
COMMENT ON COLUMN auth.sessions.last_activity_at IS 'Updated on every request to track inactivity timeout';
COMMENT ON COLUMN auth.sessions.expires_at IS 'Calculated as last_activity_at + configured timeout minutes';

-- =====================================================
-- Table: auth.audit_logs
-- =====================================================

CREATE TABLE IF NOT EXISTS auth.audit_logs (
    audit_id                BIGSERIAL       PRIMARY KEY,
    user_id                 UUID            REFERENCES auth.users(user_id) ON DELETE SET NULL,

    -- Event Information
    event_type              VARCHAR(50)     NOT NULL,
    event_timestamp         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    -- Event Context
    email                   VARCHAR(255),
    ip_address              VARCHAR(45),
    user_agent              TEXT,

    -- Event Details
    success                 BOOLEAN,
    failure_reason          TEXT,
    session_id              UUID
);

CREATE INDEX idx_audit_user ON auth.audit_logs(user_id, event_timestamp DESC);
CREATE INDEX idx_audit_type ON auth.audit_logs(event_type, event_timestamp DESC);
CREATE INDEX idx_audit_timestamp ON auth.audit_logs(event_timestamp DESC);

COMMENT ON TABLE auth.audit_logs IS 'Audit trail of all authentication events';
COMMENT ON COLUMN auth.audit_logs.event_type IS 'Event types: login, logout, login_failed, session_timeout, session_invalidated';

-- =====================================================
-- Grant Permissions
-- =====================================================

-- Grant usage on auth schema
GRANT USAGE ON SCHEMA auth TO postgres;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.users TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.sessions TO postgres;
GRANT SELECT, INSERT ON auth.audit_logs TO postgres;

-- Grant sequence permissions
GRANT USAGE, SELECT ON SEQUENCE auth.audit_logs_audit_id_seq TO postgres;

-- Verification
SELECT 'Authentication tables created successfully.' AS status;
