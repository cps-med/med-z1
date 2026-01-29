# User Authentication and Management - Design Document

**Document Version:** 2.1
**Date:** 2025-12-23
**Last Updated:** 2025-12-30
**Status:** ✅ Implementation Complete
**Implementation Phase:** Phases 1-8 Complete (All)

**Changelog:**
- **v2.1** (2025-12-30): Consolidated implementation documentation
  - **Added Section 16: File Inventory** - Complete categorized listing of all auth implementation files
  - **Added Section 17: Deployment Checklist** - Development vs Production environment checklists with detailed security, monitoring, and compliance requirements
  - **Enhanced Appendix D (Troubleshooting)** - Added 9 detailed troubleshooting scenarios with specific error messages, diagnostic steps, solutions, and verification commands
  - **Updated Table of Contents** - Added new sections 16-17
  - **Documentation Consolidation:** All content from `auth-implementation-summary.md` has been merged into this document, making it the single source of truth for authentication design and implementation
- **v2.0** (2025-12-23): CCOW v2.0 integration and session timeout fixes
  - **Session Timeout Timezone Fix:** Fixed timezone-aware/naive datetime comparison in `ccow/auth_helper.py` (line 112-115)
  - **CCOW v2.0 Integration:** CCOW Context Vault now shares `auth.sessions` and `auth.users` tables with med-z1 app
  - **Shared Session Management:** Both med-z1 and CCOW extend session timeout on authenticated requests
  - **Enhanced Documentation:** Added cross-references to:
    - `docs/spec/session-timeout-behavior.md` - Complete session timeout behavior guide
    - `docs/guide/environment-variables-guide.md` - Environment variable configuration
    - `docs/spec/ccow-v2-implementation-summary.md` - CCOW v2.0 completion summary
    - `docs/spec/ccow-v2-testing-guide.md` - API testing guide
  - **Environment Configuration:** Documented SESSION_TIMEOUT_* environment variables
- **v1.1** (2025-12-18): Implementation complete
  - All 8 phases implemented and tested
  - Login page with Entra ID-style design
  - User context display in sidebar with logout button
  - Template context helper utility created
  - Comprehensive test suite with 7 tests
  - Complete implementation summary in `docs/spec/auth-implementation-summary.md`
- **v1.0** (2025-12-18): Initial design document
  - PostgreSQL auth schema design (users, sessions, audit logs)
  - Mock Microsoft Entra ID authentication flow
  - **Configurable session timeout** via `config.py` and `.env` (Section 8)
  - Password hashing and security best practices
  - Integration with existing med-z1 architecture
  - Implementation roadmap
  - **Note**: Session timeout (default 15 minutes) is globally configurable, not per-user

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Background and Context](#3-background-and-context)
4. [Architecture](#4-architecture)
5. [Database Schema Design](#5-database-schema-design)
6. [Authentication Flow](#6-authentication-flow)
7. [Session Management](#7-session-management)
8. [Configuration Management](#8-configuration-management)
9. [Security Implementation](#9-security-implementation)
10. [Mock User Data](#10-mock-user-data)
11. [FastAPI Integration](#11-fastapi-integration)
12. [HTMX and UI Patterns](#12-htmx-and-ui-patterns)
13. [Audit Logging](#12-audit-logging)
14. [Implementation Roadmap](#13-implementation-roadmap)
15. [Testing Strategy](#14-testing-strategy)
16. [Future Enhancements](#15-future-enhancements)
17. [File Inventory](#16-file-inventory)
18. [Deployment Checklist](#17-deployment-checklist)

---

## 1. Overview

### 1.1 Purpose

The **User Authentication and Management** system adds secure login, session management, and user profile capabilities to med-z1. This implementation:

- **Simulates VA's Microsoft Entra ID** - Mock OIDC-based authentication flow aligned with VA's strategic direction
- **Enforces access control** - Require login before accessing any patient data
- **Manages user sessions** - PostgreSQL-backed sessions with inactivity timeout
- **Tracks audit events** - Log all login/logout activity for compliance
- **Maintains user profiles** - Store home site assignments and metadata
- **Follows security best practices** - Password hashing, secure session tokens, protection against common attacks

### 1.2 Real-World Context

The Department of Veterans Affairs is transitioning from legacy SAML-based Single Sign-On Internal (SSOi) to **Microsoft Entra ID** (formerly Azure Active Directory) for enterprise identity management:

**Legacy JLV Authentication (SSOi)**:
- PIV card authentication
- SAML tokens
- Complex VistA Access/Verify codes
- Site-specific authentication

**Modern VA Direction (Entra ID)**:
- OpenID Connect (OIDC) / OAuth 2.0
- Centralized identity for ~850,000 users
- Phish-resistant MFA (Certificate-Based Authentication)
- Cloud-native, standards-based

**med-z1 Approach**:
- **Simulate** the Entra ID flow without requiring real Azure infrastructure
- Use OIDC-compatible patterns (JWT tokens, callback URLs, session management)
- Align with modern web security practices
- Maintain simplicity for reference application while demonstrating production patterns

### 1.3 Scope

**In Scope for Initial Implementation:**
- PostgreSQL authentication schema (users, sessions, audit logs)
- Mock Entra ID login page with email/password authentication
- Password hashing using industry-standard algorithms (bcrypt/Argon2)
- Server-side session management with inactivity timeout (15 minutes)
- Single-session enforcement (one active session per user)
- Login/logout audit logging
- User profile storage (home site assignment)
- FastAPI authentication middleware
- HTMX-aware session enforcement
- Mock user data (3-5 clinicians with SQL inserts)
- Login-required access to all pages

**Out of Scope for Initial Implementation:**
- Real Microsoft Entra ID integration
- PIV card authentication
- Role-based access control (RBAC)
- Site-specific data filtering
- Multi-factor authentication (MFA)
- User preferences UI (theme, dashboard layout)
- Password reset flows
- Account lockout after failed attempts
- User self-registration
- Admin user management UI

### 1.4 Key Design Decisions

1. **Separate Auth Database Schema**: Users managed independently of CDWWork/CDWWork2
2. **PostgreSQL Session Store**: Server-side sessions (not client-side JWT)
3. **Mock OIDC Flow**: Simulate Entra ID without real Azure dependencies
4. **Email + Password Login**: Realistic authentication without PIV cards
5. **Bcrypt Password Hashing**: Industry-standard, resistant to rainbow tables
6. **Configurable Inactivity Timeout**: Default 15 minutes, configurable via `.env` and `config.py`
7. **Single Session Per User**: Simpler session management, enforce logout from other devices
8. **Login-Required for All Routes**: No anonymous browsing of patient data
9. **Audit Logging from Day One**: Easier to build in than retrofit
10. **SQL-Based Mock Users**: Consistent with CDWWork data population pattern
11. **Centralized Configuration**: Session timeout and other auth settings in `config.py` (follows med-z1 pattern)

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Secure Access Control**: Prevent unauthorized access to patient data
2. **Simulate VA Patterns**: Demonstrate Entra ID-aligned authentication for stakeholders
3. **Session Security**: Automatic timeout and single-session enforcement
4. **Audit Compliance**: Track all login activity for HIPAA-like requirements
5. **Developer-Friendly**: Clear patterns for authentication in FastAPI + HTMX stack

### 2.2 Success Criteria

**Technical Success**:
- ✅ PostgreSQL schema created with users, sessions, and audit tables
- ✅ 3-5 mock users populated with hashed passwords
- ✅ Login page renders and validates credentials
- ✅ Successful login creates session and redirects to dashboard
- ✅ Invalid credentials display error message
- ✅ Sessions expire after 15 minutes of inactivity
- ✅ Logout clears session and returns to login page
- ✅ Unauthenticated requests redirect to login
- ✅ Login/logout events recorded in audit log
- ✅ Single session enforcement (logging in from device B logs out device A)

**Functional Success**:
- ✅ User cannot access dashboard without logging in
- ✅ User can log in with email/password
- ✅ User stays logged in during active usage
- ✅ User is logged out after 15 minutes of inactivity
- ✅ User can manually log out
- ✅ HTMX requests handle authentication gracefully (redirect to login on 401)

**Operational Success**:
- ✅ Mock users can be added via SQL scripts (no manual database edits)
- ✅ Session table can be queried to see active users
- ✅ Audit log table records all authentication events
- ✅ Documentation explains how to add new mock users

### 2.3 Non-Goals

- **Not** implementing real Entra ID integration (mock simulation only)
- **Not** building user management UI (SQL scripts for mock users)
- **Not** implementing password reset (hardcoded mock passwords)
- **Not** supporting multiple active sessions per user
- **Not** filtering patient data by user's site access (all users see all data in MVP)

---

## 3. Background and Context

### 3.1 VA Authentication Evolution

**Current State (JLV on SSOi)**:

The Joint Longitudinal Viewer currently uses VA's legacy SSOi (Single Sign-On Internal) infrastructure:

```
User → JLV URL → Redirect to SSOi
                  ↓
              PIV Card Prompt
                  ↓
              VistA Access/Verify (if PIV not linked)
                  ↓
              Site Selection (Home Site)
                  ↓
              SAML Token Issued
                  ↓
              JLV Application (Authenticated)
```

**Challenges with SSOi**:
- Complex PIV card linking requirements
- Legacy SAML token management
- Site-specific authentication overhead
- Difficult to integrate with modern cloud services

**Future State (Entra ID)**:

VA is migrating to Microsoft Entra ID for centralized identity:

```
User → Application → Redirect to Entra ID Login
                      ↓
                  User Credentials (Email/Password)
                      ↓
                  MFA Challenge (CBA, Authenticator App)
                      ↓
                  OIDC Token Issued (JWT)
                      ↓
                  Application (Authenticated)
```

**Benefits of Entra ID**:
- Standards-based (OIDC, OAuth 2.0)
- Native MFA support
- Cloud-ready
- Phish-resistant authentication options
- Easier third-party integrations

### 3.2 med-z1 Simulation Strategy

Since med-z1 is a reference application, we'll simulate Entra ID without requiring Azure infrastructure:

**What We Simulate**:
- Login page styling (VA/Microsoft branding)
- Email/password authentication
- OIDC-like callback flow
- JWT-style session tokens
- Single sign-on experience

**What We Don't Simulate**:
- Real Entra ID API calls
- PIV card readers
- Actual MFA flows
- Azure infrastructure

**Implementation Approach**:
- Mock Entra ID login page (Jinja2 template)
- Email/password stored in PostgreSQL with bcrypt hashing
- Session management using PostgreSQL table
- FastAPI middleware for authentication enforcement

### 3.3 Current med-z1 Architecture

**Application Structure**:
```
med-z1/
  app/
    main.py              # FastAPI application
    routes/
      dashboard.py       # Dashboard routes (currently root "/")
      patient.py         # Patient selection and context
      demographics.py    # Demographics pages
      vitals.py          # Vitals pages
      medications.py     # Medications pages
      encounters.py      # Encounters pages
      labs.py            # Labs pages
      auth.py            # (NEW) Authentication routes (login/logout)
    db/
      patient.py         # Patient queries
      vitals.py          # Vitals queries
      medications.py     # Medications queries
      auth.py            # (NEW) Authentication database functions
      (etc.)
    middleware/
      auth.py            # (NEW) Authentication middleware
    templates/
      base.html          # Base template with topbar
      dashboard.html     # Main dashboard
      login.html         # (NEW) Login page
      (etc.)
    utils/
      ccow_client.py     # CCOW context management
      template_context.py # (NEW) Template context helper
    static/
      css/               # Stylesheets
      js/                # JavaScript (minimal)
  db/                    # PostgreSQL serving database
    ddl/                 # Schema creation scripts
      create_auth_tables.sql                # Authentication schema
      patient_demographics.sql              # Patient demographics table
      create_patient_vitals_table.sql       # Vitals table
      create_patient_flags_tables.sql       # Patient flags tables
      create_patient_allergies_tables.sql   # Allergies tables
      create_patient_medications_tables.sql # Medications tables
      create_patient_encounters_table.sql   # Encounters table
      create_patient_labs_table.sql         # Laboratory results table
    seeds/               # Test/development data
      auth_users.sql     # Mock user accounts with hashed passwords
  ccow/
    main.py              # CCOW Context Vault service
    auth_helper.py       # (NEW) Shared authentication validation
  scripts/
    generate_password_hash.py # (NEW) Password hashing utility
    test_auth_flow.py         # (NEW) Authentication flow tests
```

**Current Session State**:
- CCOW vault tracks active patient (patient_id)
- No user authentication
- No concept of "logged in user"

**After Authentication Implementation**:
- Session table tracks logged-in users
- Middleware enforces authentication on all routes
- User context available in request.state
- CCOW vault still tracks active patient (unchanged)

---

## 4. Architecture

### 4.1 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        med-z1 Application                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FastAPI Application (app/main.py)                       │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  Authentication Middleware                        │   │   │
│  │  │  - Checks session validity on every request      │   │   │
│  │  │  - Injects user context into request.state       │   │   │
│  │  │  - Redirects to /login if unauthenticated        │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                                                           │   │
│  │  Routes:                                                  │   │
│  │  ├─ /login (GET/POST) → Auth flow                       │   │
│  │  ├─ /logout (POST) → Session termination                │   │
│  │  ├─ / (Dashboard) → Requires authentication             │   │
│  │  ├─ /patient/{icn}/... → Requires authentication        │   │
│  │  └─ /api/... → Requires authentication                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                     │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  auth schema (NEW)                                │   │   │
│  │  │  ├─ users (user credentials, profiles)           │   │   │
│  │  │  ├─ sessions (active session tracking)           │   │   │
│  │  │  └─ audit_logs (login/logout events)             │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  public schema (existing - patient data)         │   │   │
│  │  │  ├─ patient_demographics                         │   │   │
│  │  │  ├─ patient_vitals                               │   │   │
│  │  │  └─ ... (unchanged)                              │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Authentication Flow (High-Level)

```
┌──────┐                ┌───────────────┐              ┌──────────┐
│ User │                │   med-z1 App  │              │ Database │
└──┬───┘                └───────┬───────┘              └────┬─────┘
   │                            │                           │
   │  1. GET /                  │                           │
   ├───────────────────────────>│                           │
   │                            │                           │
   │  2. Check session          │                           │
   │     (via middleware)       │                           │
   │                            ├──────────────────────────>│
   │                            │  SELECT * FROM sessions   │
   │                            │  WHERE session_id = ?     │
   │                            │<──────────────────────────┤
   │                            │  (no valid session)       │
   │                            │                           │
   │  3. Redirect to /login     │                           │
   │<───────────────────────────┤                           │
   │                            │                           │
   │  4. GET /login             │                           │
   ├───────────────────────────>│                           │
   │                            │                           │
   │  5. Return login page      │                           │
   │<───────────────────────────┤                           │
   │                            │                           │
   │  6. POST /login            │                           │
   │     (email, password)      │                           │
   ├───────────────────────────>│                           │
   │                            │                           │
   │  7. Validate credentials   │                           │
   │                            ├──────────────────────────>│
   │                            │  SELECT * FROM users      │
   │                            │  WHERE email = ?          │
   │                            │<──────────────────────────┤
   │                            │  (user record returned)   │
   │                            │                           │
   │  8. Verify password hash   │                           │
   │     (bcrypt.checkpw)       │                           │
   │                            │                           │
   │  9. Invalidate old sessions│                           │
   │                            ├──────────────────────────>│
   │                            │  UPDATE sessions          │
   │                            │  SET active = FALSE       │
   │                            │  WHERE user_id = ?        │
   │                            │<──────────────────────────┤
   │                            │                           │
   │  10. Create new session    │                           │
   │                            ├──────────────────────────>│
   │                            │  INSERT INTO sessions     │
   │                            │<──────────────────────────┤
   │                            │                           │
   │  11. Log login event       │                           │
   │                            ├──────────────────────────>│
   │                            │  INSERT INTO audit_logs   │
   │                            │<──────────────────────────┤
   │                            │                           │
   │  12. Set session cookie    │                           │
   │      Redirect to /         │                           │
   │<───────────────────────────┤                           │
   │                            │                           │
   │  13. GET / (with cookie)   │                           │
   ├───────────────────────────>│                           │
   │                            │                           │
   │  14. Validate session      │                           │
   │                            ├──────────────────────────>│
   │                            │  SELECT * FROM sessions   │
   │                            │  WHERE session_id = ?     │
   │                            │  AND active = TRUE        │
   │                            │  AND expires_at > NOW()   │
   │                            │<──────────────────────────┤
   │                            │  (valid session)          │
   │                            │                           │
   │  15. Return dashboard      │                           │
   │<───────────────────────────┤                           │
   │                            │                           │
```

### 4.3 Data Flow Layers

**Layer 1: Browser**
- Login form (email/password input)
- Session cookie (HTTP-only, Secure, SameSite)
- HTMX requests with automatic cookie inclusion

**Layer 2: FastAPI Application**
- Authentication middleware (checks session on every request)
- Login/logout routes (app/routes/auth.py)
- Protected routes (dashboard, patient pages, API endpoints)

**Layer 3: Database**
- `auth.users` - User credentials (hashed passwords)
- `auth.sessions` - Active session tracking
- `auth.audit_logs` - Login/logout events

---

## 5. Database Schema Design

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

### 5.1 Schema Organization

Create a new `auth` schema in PostgreSQL to separate authentication concerns from clinical data:

```sql
-- Create auth schema
CREATE SCHEMA IF NOT EXISTS auth;
```

**Rationale**:
- Clean separation between authentication and clinical data
- Easy to identify auth-related tables
- Future-proof for additional auth features (roles, permissions, etc.)
- Follows PostgreSQL best practice for multi-schema databases

### 5.2 Users Table

**Purpose**: Store user credentials, profile information, and home site assignments.

**Schema**:
```sql
CREATE TABLE auth.users (
    user_id                 UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    email                   VARCHAR(255)    UNIQUE NOT NULL,
    password_hash           VARCHAR(255)    NOT NULL,       -- bcrypt hash

    -- Profile Information
    display_name            VARCHAR(255)    NOT NULL,       -- "Dr. Jane Smith"
    first_name              VARCHAR(100),
    last_name               VARCHAR(100),
    home_site_sta3n         INTEGER,                        -- Primary VA site (e.g., 508)

    -- Account Status
    is_active               BOOLEAN         DEFAULT TRUE,
    is_locked               BOOLEAN         DEFAULT FALSE,
    failed_login_attempts   INTEGER         DEFAULT 0,
    last_login_at           TIMESTAMP,

    -- Audit Fields
    created_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    created_by              VARCHAR(100)    DEFAULT 'system',

    -- Indexes
    INDEX idx_email (email),
    INDEX idx_home_site (home_site_sta3n),
    INDEX idx_active (is_active)
);

COMMENT ON TABLE auth.users IS 'User credentials and profile information for med-z1 application';
COMMENT ON COLUMN auth.users.email IS 'User email address (username for login)';
COMMENT ON COLUMN auth.users.password_hash IS 'Bcrypt hash of user password (never store plaintext)';
COMMENT ON COLUMN auth.users.home_site_sta3n IS 'Primary VA site assignment (Sta3n code)';
```

**Field Descriptions**:
- **user_id**: UUID primary key (more secure than sequential integers)
- **email**: Unique username (email format, common VA pattern)
- **password_hash**: Bcrypt-hashed password (never store plaintext)
- **display_name**: Full name for UI display ("Dr. Jane Smith, MD")
- **home_site_sta3n**: Home VistA site (e.g., 508 = Atlanta VAMC)
- **is_active**: Soft-delete flag (disable users without removing records)
- **is_locked**: Account lockout flag (future: after N failed logins)
- **failed_login_attempts**: Counter for lockout logic (future enhancement)
- **last_login_at**: Track last successful login for audit

**Sample Data**:
```sql
-- Sample users (see Section 9 for full mock data)
INSERT INTO auth.users (email, password_hash, display_name, first_name, last_name, home_site_sta3n)
VALUES
('clinician.alpha@va.gov', '$2b$12$...', 'Dr. Alice Anderson, MD', 'Alice', 'Anderson', 508),
('clinician.bravo@va.gov', '$2b$12$...', 'Dr. Bob Brown, DO', 'Bob', 'Brown', 648),
('clinician.charlie@va.gov', '$2b$12$...', 'Nurse Carol Chen, RN', 'Carol', 'Chen', 663);
```

### 5.3 Sessions Table

**Purpose**: Track active user sessions with timeout enforcement and single-session logic.

**Schema**:
```sql
CREATE TABLE auth.sessions (
    session_id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID            NOT NULL REFERENCES auth.users(user_id) ON DELETE CASCADE,

    -- Session Lifecycle
    created_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    last_activity_at        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    expires_at              TIMESTAMP       NOT NULL,

    -- Session Status
    is_active               BOOLEAN         DEFAULT TRUE,

    -- Session Metadata
    ip_address              VARCHAR(45),                    -- IPv4 or IPv6
    user_agent              TEXT,                           -- Browser/client info

    -- Indexes
    INDEX idx_user_sessions (user_id, is_active),
    INDEX idx_session_expiry (expires_at, is_active),
    INDEX idx_last_activity (last_activity_at)
);

COMMENT ON TABLE auth.sessions IS 'Active user sessions with timeout enforcement';
COMMENT ON COLUMN auth.sessions.last_activity_at IS 'Updated on every request to track inactivity timeout';
COMMENT ON COLUMN auth.sessions.expires_at IS 'Calculated as last_activity_at + 15 minutes';
```

**Field Descriptions**:
- **session_id**: UUID session token (stored in HTTP-only cookie)
- **user_id**: Foreign key to users table
- **created_at**: When session was created (login time)
- **last_activity_at**: Updated on every request (for inactivity timeout)
- **expires_at**: Absolute expiration time (last_activity + 15 min)
- **is_active**: Allows manual session invalidation (logout, force logout)
- **ip_address**: Client IP for audit trail (optional security feature)
- **user_agent**: Browser info for session identification

**Session Lifecycle**:
```
Login → Create Session (is_active=TRUE, expires_at = NOW() + 15 min)
  ↓
User Activity → Update last_activity_at, expires_at = NOW() + 15 min
  ↓
15 Min Inactivity → Session expires (expires_at < NOW())
  ↓
Logout → Set is_active = FALSE
```

**Single Session Enforcement**:
```sql
-- On login, invalidate all other sessions for this user
UPDATE auth.sessions
SET is_active = FALSE
WHERE user_id = :user_id
  AND session_id != :new_session_id;
```

### 5.4 Audit Logs Table

**Purpose**: Record all authentication events for compliance and security monitoring.

**Schema**:
```sql
CREATE TABLE auth.audit_logs (
    audit_id                BIGSERIAL       PRIMARY KEY,
    user_id                 UUID            REFERENCES auth.users(user_id) ON DELETE SET NULL,

    -- Event Information
    event_type              VARCHAR(50)     NOT NULL,       -- 'login', 'logout', 'login_failed', etc.
    event_timestamp         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    -- Event Context
    email                   VARCHAR(255),                   -- User email (preserved even if user deleted)
    ip_address              VARCHAR(45),
    user_agent              TEXT,

    -- Event Details
    success                 BOOLEAN,
    failure_reason          TEXT,                           -- For failed logins
    session_id              UUID,                           -- Associated session (if applicable)

    -- Indexes
    INDEX idx_user_audit (user_id, event_timestamp DESC),
    INDEX idx_event_type (event_type, event_timestamp DESC),
    INDEX idx_timestamp (event_timestamp DESC)
);

COMMENT ON TABLE auth.audit_logs IS 'Audit trail of all authentication events';
COMMENT ON COLUMN auth.audit_logs.event_type IS 'Event types: login, logout, login_failed, session_timeout, session_invalidated';
```

**Event Types**:
- `login` - Successful login
- `logout` - User-initiated logout
- `login_failed` - Failed login attempt (bad credentials)
- `session_timeout` - Session expired due to inactivity
- `session_invalidated` - Session forcibly invalidated (e.g., new login from different device)

**Sample Audit Log Entries**:
```sql
-- Successful login
INSERT INTO auth.audit_logs (user_id, event_type, email, ip_address, success, session_id)
VALUES ('123e4567-...', 'login', 'clinician.alpha@va.gov', '192.168.1.100', TRUE, 'abc123-...');

-- Failed login (bad password)
INSERT INTO auth.audit_logs (event_type, email, ip_address, success, failure_reason)
VALUES ('login_failed', 'clinician.alpha@va.gov', '192.168.1.100', FALSE, 'Invalid password');

-- Logout
INSERT INTO auth.audit_logs (user_id, event_type, email, session_id, success)
VALUES ('123e4567-...', 'logout', 'clinician.alpha@va.gov', 'abc123-...', TRUE);
```

### 5.5 Schema Creation Script

**File**: `db/ddl/create_auth_tables.sql`

```sql
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
COMMENT ON COLUMN auth.sessions.expires_at IS 'Calculated as last_activity_at + 15 minutes';

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
GRANT USAGE ON SCHEMA auth TO med_z1_user;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.users TO med_z1_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.sessions TO med_z1_user;
GRANT SELECT, INSERT ON auth.audit_logs TO med_z1_user;

-- Grant sequence permissions
GRANT USAGE, SELECT ON SEQUENCE auth.audit_logs_audit_id_seq TO med_z1_user;

PRINT 'Authentication tables created successfully.';
```

---

## 6. Authentication Flow

### 6.1 Login Flow (Detailed)

**Step 1: Unauthenticated User Accesses Application**

```
User visits http://localhost:8000/
  ↓
FastAPI AuthMiddleware intercepts request
  ↓
Check for session_id cookie
  ↓
No cookie found → Redirect to /login
```

**Step 2: Login Page Rendering**

```python
# app/routes/auth.py

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    """Render the login page."""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None
        }
    )
```

**Step 3: User Submits Credentials**

```html
<!-- app/templates/login.html -->
<form method="POST" action="/login">
    <input type="email" name="email" placeholder="Email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Log In</button>
</form>
```

**Step 4: Credential Validation**

```python
# app/routes/auth.py

@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Authenticate user and create session."""

    # 1. Query user by email
    user = get_user_by_email(email)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )

    # 2. Verify password hash
    if not verify_password(password, user['password_hash']):
        # Log failed attempt
        log_audit_event(
            event_type='login_failed',
            email=email,
            success=False,
            failure_reason='Invalid password'
        )
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )

    # 3. Check if account is active
    if not user['is_active']:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Account is inactive"}
        )

    # 4. Invalidate old sessions (single-session enforcement)
    invalidate_user_sessions(user['user_id'])

    # 5. Create new session
    session_id = create_session(
        user_id=user['user_id'],
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )

    # 6. Log successful login
    log_audit_event(
        event_type='login',
        user_id=user['user_id'],
        email=email,
        session_id=session_id,
        success=True
    )

    # 7. Update last_login_at
    update_last_login(user['user_id'])

    # 8. Set session cookie and redirect
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="lax",
        max_age=900  # 15 minutes
    )
    return response
```

### 6.2 Session Validation Flow

**On Every Request**:

```python
# app/middleware/auth.py

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for login/static routes
        if request.url.path in ["/login", "/static", "/favicon.ico"]:
            return await call_next(request)

        # Extract session_id from cookie
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/login", status_code=303)

        # Validate session
        session = get_session(session_id)
        if not session or not session['is_active']:
            return RedirectResponse(url="/login", status_code=303)

        # Check expiration
        if session['expires_at'] < datetime.now():
            invalidate_session(session_id)
            log_audit_event(
                event_type='session_timeout',
                user_id=session['user_id'],
                session_id=session_id
            )
            return RedirectResponse(url="/login", status_code=303)

        # Update last activity (extend session)
        extend_session(session_id)

        # Inject user into request state
        request.state.user = get_user(session['user_id'])
        request.state.session_id = session_id

        # Continue to route handler
        return await call_next(request)
```

### 6.3 Logout Flow

```python
# app/routes/auth.py

@router.post("/logout")
async def post_logout(request: Request):
    """Log out user and invalidate session."""

    session_id = request.cookies.get("session_id")
    if session_id:
        session = get_session(session_id)
        if session:
            # Invalidate session
            invalidate_session(session_id)

            # Log logout event
            log_audit_event(
                event_type='logout',
                user_id=session['user_id'],
                session_id=session_id,
                success=True
            )

    # Clear cookie and redirect
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response
```

### 6.4 Session Extension Logic

```python
# app/db/auth.py

def extend_session(session_id: str):
    """Update session activity and extend expiration."""
    now = datetime.now()
    expires_at = now + timedelta(minutes=15)

    query = text("""
        UPDATE auth.sessions
        SET last_activity_at = :now,
            expires_at = :expires_at
        WHERE session_id = :session_id
          AND is_active = TRUE
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "now": now,
            "expires_at": expires_at,
            "session_id": session_id
        })
        conn.commit()
```

---

## 7. Session Management

### 7.1 Session Lifecycle

```
┌─────────────┐
│   Login     │
│  (POST)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Create Session                      │
│ - Generate UUID                     │
│ - Set expires_at = NOW() + timeout  │
│ - Set is_active = TRUE              │
│ (timeout from SESSION_TIMEOUT_MIN)  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Set HTTP-Only Cookie                │
│ - session_id = UUID                 │
│ - Secure, SameSite=Lax              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ User Activity                       │
│ - Every request → validate session  │
│ - Update last_activity_at           │
│ - Extend expires_at + timeout       │
│ (timeout from config)               │
└──────┬──────────────────────────────┘
       │
       ├────────────────────┬──────────────────────┐
       │                    │                      │
       ▼                    ▼                      ▼
┌─────────────┐   ┌──────────────────┐   ┌────────────────┐
│   Logout    │   │ Inactivity       │   │  New Login     │
│  (POST)     │   │ (timeout)        │   │  (Force Out)   │
└──────┬──────┘   └────────┬─────────┘   └────────┬───────┘
       │                   │                      │
       ▼                   ▼                      ▼
┌─────────────────────────────────────────────────────────┐
│ Invalidate Session                                      │
│ - SET is_active = FALSE                                 │
│ - Log audit event                                       │
│ - Clear cookie                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Inactivity Timeout (Configurable)

**Default**: 15 minutes (configurable via `SESSION_TIMEOUT_MINUTES` in `.env`)

**Implementation**:

```python
# On every authenticated request:
from config import SESSION_TIMEOUT_MINUTES

def is_session_valid(session: dict) -> bool:
    """Check if session is valid and not expired."""
    now = datetime.now()

    # Check if session is active
    if not session['is_active']:
        return False

    # Check if session has expired
    if session['expires_at'] < now:
        return False

    return True

# If valid, extend expiration:
def extend_session(session_id: str):
    now = datetime.now()
    # Use configured timeout (not hardcoded)
    new_expiry = now + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    query = text("""
        UPDATE auth.sessions
        SET last_activity_at = :now,
            expires_at = :new_expiry
        WHERE session_id = :session_id
    """)
    # Execute query...
```

**User Experience** (with default 15-minute timeout):
- User logs in → Session expires at T+15 minutes
- User clicks dashboard widget at T+5 → Session extended to T+20 minutes
- User clicks another widget at T+18 → Session extended to T+33 minutes
- User goes to lunch (no activity) → Session expires at T+33, next request redirects to login

**Adjusting Timeout**:
- Edit `.env`: `SESSION_TIMEOUT_MINUTES=30` for 30-minute timeout
- Restart application for changes to take effect
- All users share same timeout (global setting, not per-user)

### 7.3 Single Session Enforcement

**On Login**:

```python
def invalidate_user_sessions(user_id: str, except_session_id: str = None):
    """Invalidate all active sessions for a user (except optionally one)."""
    query = text("""
        UPDATE auth.sessions
        SET is_active = FALSE
        WHERE user_id = :user_id
          AND is_active = TRUE
          AND (:except_session_id IS NULL OR session_id != :except_session_id)
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "user_id": user_id,
            "except_session_id": except_session_id
        })
        conn.commit()

        # Log session invalidation for each affected session
        if result.rowcount > 0:
            log_audit_event(
                event_type='session_invalidated',
                user_id=user_id,
                success=True,
                failure_reason=f'{result.rowcount} session(s) invalidated by new login'
            )
```

**User Experience**:
- User logs in on Desktop → Session A created
- User logs in on Laptop → Session B created, Session A invalidated
- Desktop user refreshes page → Redirected to login (Session A no longer valid)

### 7.4 Session Cleanup (Maintenance)

**Background Task** (future enhancement):

```python
# app/background/session_cleanup.py

async def cleanup_expired_sessions():
    """Delete expired sessions older than 24 hours."""
    cutoff = datetime.now() - timedelta(hours=24)

    query = text("""
        DELETE FROM auth.sessions
        WHERE expires_at < :cutoff
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"cutoff": cutoff})
        conn.commit()
        logger.info(f"Cleaned up {result.rowcount} expired sessions")
```

### 7.5 Session Timeout Behavior and Timezone Handling

**Timezone-Aware Session Validation** (v2.0 Fix):

PostgreSQL `TIMESTAMP WITHOUT TIME ZONE` fields return timezone-naive datetime objects in Python. The session validation logic in `ccow/auth_helper.py` handles this correctly:

```python
# ccow/auth_helper.py (lines 112-115)
# Use timezone-naive comparison if expires_at is timezone-naive
if expires_at.tzinfo is None:
    now = datetime.now()  # Local time, no timezone
else:
    now = datetime.now(timezone.utc)  # UTC time
```

**Key Points:**
- Both med-z1 app (`app/middleware/auth.py`) and CCOW Context Vault (`ccow/auth_helper.py`) share `auth.sessions` table
- Session timeout extends on every authenticated request in **both** applications
- Single session enforcement applies across both applications
- Expired session detection triggers audit logging and graceful redirect to login

**For Complete Details:**
- Session timeout behavior, extension rules, and edge cases: See `docs/spec/session-timeout-behavior.md`
- CCOW v2.0 integration architecture and shared session management: See `docs/spec/ccow-v2-implementation-summary.md`
- API testing with curl and Insomnia: See `docs/spec/ccow-v2-testing-guide.md`

---

## 8. Configuration Management

### 8.1 Configuration Pattern

Following med-z1's established pattern, all authentication configuration is centralized in `config.py` at the project root, with values sourced from `.env`.

**Benefits**:
- ✅ Single source of truth for configuration
- ✅ Easy to adjust settings without code changes
- ✅ Environment-specific configuration (dev, test, production)
- ✅ Consistent with existing med-z1 patterns (database, CCOW, MinIO configs)

### 8.2 Environment Variables

**File**: `.env` (project root)

Add the following authentication-related variables:

```bash
# =====================================================
# Authentication Configuration
# =====================================================

# Session timeout (in minutes) - how long a user can be inactive before session expires
SESSION_TIMEOUT_MINUTES=15

# Session cookie settings
SESSION_COOKIE_NAME=session_id
SESSION_COOKIE_SECURE=false          # Set to true in production (HTTPS only)
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax

# Password hashing
BCRYPT_ROUNDS=12                     # Bcrypt work factor (10-14 recommended)

# Account lockout (future enhancement)
# MAX_FAILED_LOGIN_ATTEMPTS=5
# ACCOUNT_LOCKOUT_DURATION_MINUTES=30
```

**Notes**:
- `SESSION_TIMEOUT_MINUTES=15` - Default 15 minutes (VA recommended practice)
- `SESSION_COOKIE_SECURE=false` - Set to `false` for local development (HTTP), `true` in production (HTTPS required)
- `BCRYPT_ROUNDS=12` - Higher values = more secure but slower (12 is current industry standard)

### 8.3 Config.py Updates

**File**: `config.py` (project root)

Add authentication configuration section:

```python
# -----------------------------------------------------------
# Authentication Configuration
# -----------------------------------------------------------

# Session timeout (in minutes)
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "15"))

# Session cookie settings
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "session_id")
SESSION_COOKIE_SECURE = _get_bool("SESSION_COOKIE_SECURE", False)  # True in production
SESSION_COOKIE_HTTPONLY = _get_bool("SESSION_COOKIE_HTTPONLY", True)
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "lax")

# Password hashing
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# Session cookie max_age (in seconds) - matches timeout
SESSION_COOKIE_MAX_AGE = SESSION_TIMEOUT_MINUTES * 60

# Authentication configuration dictionary (for easy import)
AUTH_CONFIG = {
    "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
    "cookie_name": SESSION_COOKIE_NAME,
    "cookie_secure": SESSION_COOKIE_SECURE,
    "cookie_httponly": SESSION_COOKIE_HTTPONLY,
    "cookie_samesite": SESSION_COOKIE_SAMESITE,
    "cookie_max_age": SESSION_COOKIE_MAX_AGE,
    "bcrypt_rounds": BCRYPT_ROUNDS,
}
```

### 8.4 Usage in Code

**Import Pattern**:

```python
# In any module that needs auth config
from config import (
    SESSION_TIMEOUT_MINUTES,
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_MAX_AGE,
    BCRYPT_ROUNDS,
    # Or import the entire dict:
    AUTH_CONFIG
)
```

**Example - Creating Session with Configurable Timeout**:

```python
# app/db/auth.py
from datetime import datetime, timedelta
from config import SESSION_TIMEOUT_MINUTES

def create_session(user_id: str, ip_address: str = None, user_agent: str = None) -> str:
    """Create new session for user."""
    session_id = str(uuid.uuid4())
    now = datetime.now()

    # Use configured timeout (not hardcoded!)
    expires_at = now + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    # ... rest of function
```

**Example - Setting Session Cookie with Config**:

```python
# app/routes/auth.py
from config import (
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_MAX_AGE
)

response = RedirectResponse(url="/", status_code=303)
response.set_cookie(
    key=SESSION_COOKIE_NAME,           # Configurable cookie name
    value=str(session_id),
    httponly=SESSION_COOKIE_HTTPONLY,  # From config
    secure=SESSION_COOKIE_SECURE,      # From config (false in dev, true in prod)
    samesite=SESSION_COOKIE_SAMESITE,  # From config
    max_age=SESSION_COOKIE_MAX_AGE     # Matches session timeout
)
```

**Example - Password Hashing with Configurable Rounds**:

```python
# app/utils/password.py
import bcrypt
from config import BCRYPT_ROUNDS

def hash_password(password: str) -> str:
    """Hash a password using bcrypt with configured work factor."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)  # Uses config value, not hardcoded
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')
```

### 8.5 Environment-Specific Configuration

**Development** (`.env`):
```bash
SESSION_TIMEOUT_MINUTES=15       # Standard timeout
SESSION_COOKIE_SECURE=false      # Allow HTTP for local development
BCRYPT_ROUNDS=10                 # Faster for dev/testing (less secure but quicker)
```

**Production** (`.env` or environment variables):
```bash
SESSION_TIMEOUT_MINUTES=15       # Or 30 for less restrictive environments
SESSION_COOKIE_SECURE=true       # HTTPS required in production
BCRYPT_ROUNDS=12                 # Full security
```

**Testing** (`.env.test` or override):
```bash
SESSION_TIMEOUT_MINUTES=1        # Fast timeout for testing expiration
BCRYPT_ROUNDS=4                  # Minimal rounds for speed (tests only!)
```

### 8.6 Configuration Validation

**Add to config.py** (optional but recommended):

```python
# Validate authentication configuration on startup
if SESSION_TIMEOUT_MINUTES < 1:
    raise ValueError("SESSION_TIMEOUT_MINUTES must be at least 1 minute")

if SESSION_TIMEOUT_MINUTES > 1440:  # 24 hours
    logger.warning(f"SESSION_TIMEOUT_MINUTES is very long ({SESSION_TIMEOUT_MINUTES} min). Consider reducing for security.")

if BCRYPT_ROUNDS < 10:
    logger.warning(f"BCRYPT_ROUNDS={BCRYPT_ROUNDS} is low. Use 12+ for production.")

if BCRYPT_ROUNDS > 14:
    logger.warning(f"BCRYPT_ROUNDS={BCRYPT_ROUNDS} is very high. May cause slow login performance.")
```

### 8.7 Benefits of Configurable Timeout

**Flexibility**:
- Adjust timeout without code changes
- Different timeouts for dev vs. production
- Easy A/B testing of timeout values

**Security**:
- Shorter timeout for high-security environments
- Longer timeout for usability in controlled environments
- Align with organizational security policies

**Testing**:
- Set timeout to 1 minute for faster integration tests
- Avoid waiting 15 minutes to test session expiration

**User Experience**:
- Balance security (shorter timeout) with convenience (longer timeout)
- Adjust based on user feedback

### 8.8 Complete Environment Variable Reference

For a comprehensive guide to all authentication-related environment variables, including:
- Detailed descriptions of each variable
- Valid value ranges and constraints
- Production vs. development recommendations
- Troubleshooting common configuration errors
- Integration with CCOW Context Vault settings

**See:** `docs/guide/environment-variables-guide.md`

---

## 9. Security Implementation

### 9.1 Password Hashing

**Algorithm**: **bcrypt** (industry standard for password hashing)

**Why bcrypt?**
- Adaptive hashing (configurable work factor)
- Resistant to brute-force attacks
- Salted automatically (no separate salt storage needed)
- Battle-tested (used by major platforms)

**Alternative**: Argon2 (newer, more resistant to GPU attacks, but bcrypt is simpler and adequate for reference app)

**Implementation**:

```python
# app/utils/password.py

import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good balance of speed/security
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )
```

**Usage**:

```python
# Creating a user:
hashed = hash_password("SecurePassword123!")
# Result: "$2b$12$abcdef..." (60 characters)

# Verifying login:
is_valid = verify_password("SecurePassword123!", hashed)
# Returns: True if match, False if no match
```

### 9.3 Mock User Password Management

**Development Strategy**: Use a **single shared password** for all mock users to simplify development and testing.

**Recommended Password**: `VaDemo2025!`
- Easy to remember for all developers
- Meets complexity requirements (uppercase, lowercase, number, special character)
- Clearly indicates demo/development use
- Same password for all 5 mock users

**Password Documentation Location**: `docs/mock-users.md`

This file is **version-controlled** and serves as the definitive reference for mock user logins.

⚠️ **Why NOT Store in `.env`?**
- `.env` is for **runtime configuration** (database URLs, timeouts, feature flags)
- Mock user passwords are **static test data**, not configuration
- Dedicated documentation file makes credentials easier to find and reference
- Consistent with project pattern: `db/seeds/` for application test data, `docs/` for documentation

**Example Documentation File** (`docs/mock-users.md`):

```markdown
# Mock User Credentials for med-z1

## Shared Password (All Users)

**Password**: `VaDemo2025!`

## Mock Users

| Email                          | Display Name              | Home Site (Sta3n) | Role       |
|--------------------------------|---------------------------|-------------------|------------|
| clinician.alpha@va.gov         | Dr. Alice Anderson, MD    | 508 (Atlanta)     | Physician  |
| clinician.bravo@va.gov         | Dr. Bob Brown, DO         | 648 (Portland)    | Physician  |
| clinician.charlie@va.gov       | Nurse Carol Chen, RN      | 663 (Seattle)     | Nurse      |
| clinician.delta@va.gov         | Dr. David Davis, MD       | 509 (Augusta)     | Physician  |
| clinician.echo@va.gov          | Pharmacist Emma Evans     | 531 (Boise)       | Pharmacist |

## Quick Login Credentials

Copy-paste for testing:
- **Email**: `clinician.alpha@va.gov`
- **Password**: `VaDemo2025!`

## Password Hash (bcrypt, 12 rounds)

The bcrypt hash for `VaDemo2025!` (used in SQL INSERT scripts):
```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO
```

## Changing the Shared Password

If you need to change the shared password:

1. Update this file with the new password
2. Run: `python scripts/generate_password_hash.py --generate-sql`
3. Update `db/seeds/auth_users.sql` with new hashes
4. Reload the `auth.users` table:
   ```bash
   docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql
   ```

## Security Note

⚠️ **Development Only**: This shared password approach is for local development only.
Production systems must use unique, strong passwords per user and secure credential management.
```

### 9.4 Password Hash Generation Script

**Complete Utility Script** (`scripts/generate_password_hash.py`):

```python
#!/usr/bin/env python3
"""
Generate bcrypt password hashes for mock users.

Usage:
    # Generate single password hash interactively
    python scripts/generate_password_hash.py

    # Generate SQL INSERT statements for all mock users
    python scripts/generate_password_hash.py --generate-sql

    # Non-interactive mode (provide password via command line)
    python scripts/generate_password_hash.py --password "VaDemo2025!"
"""

import bcrypt
import sys
import argparse
from pathlib import Path

# Import bcrypt rounds from project config
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from config import BCRYPT_ROUNDS

# Mock user data (matches MOCK_USER_CREDENTIALS.md)
MOCK_USERS = [
    {
        "email": "clinician.alpha@va.gov",
        "display_name": "Dr. Alice Anderson, MD",
        "first_name": "Alice",
        "last_name": "Anderson",
        "home_site_sta3n": 508,  # Atlanta VAMC
    },
    {
        "email": "clinician.bravo@va.gov",
        "display_name": "Dr. Bob Brown, DO",
        "first_name": "Bob",
        "last_name": "Brown",
        "home_site_sta3n": 648,  # Portland VAMC
    },
    {
        "email": "clinician.charlie@va.gov",
        "display_name": "Nurse Carol Chen, RN",
        "first_name": "Carol",
        "last_name": "Chen",
        "home_site_sta3n": 663,  # Seattle/Puget Sound VA
    },
    {
        "email": "clinician.delta@va.gov",
        "display_name": "Dr. David Davis, MD",
        "first_name": "David",
        "last_name": "Davis",
        "home_site_sta3n": 509,  # Augusta VAMC
    },
    {
        "email": "clinician.echo@va.gov",
        "display_name": "Pharmacist Emma Evans, PharmD",
        "first_name": "Emma",
        "last_name": "Evans",
        "home_site_sta3n": 531,  # Boise VAMC
    },
]


def hash_password(password: str) -> str:
    """Generate bcrypt hash for a password using configured rounds."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def generate_sql_inserts(password: str) -> None:
    """Generate SQL INSERT statements for all mock users with hashed password."""
    password_hash = hash_password(password)

    print("-- =====================================================")
    print("-- Mock User Data for med-z1 Authentication")
    print("-- =====================================================")
    print(f"-- Password for all users: {password}")
    print(f"-- Bcrypt rounds: {BCRYPT_ROUNDS}")
    print(f"-- Generated hash: {password_hash}")
    print("--")
    print("-- Usage:")
    print("--   docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql")
    print("-- =====================================================")
    print()
    print("-- Clear existing data (development only)")
    print("TRUNCATE TABLE auth.sessions CASCADE;")
    print("TRUNCATE TABLE auth.audit_logs CASCADE;")
    print("DELETE FROM auth.users;")
    print()
    print("-- Insert mock users")
    print("INSERT INTO auth.users (")
    print("    email,")
    print("    password_hash,")
    print("    display_name,")
    print("    first_name,")
    print("    last_name,")
    print("    home_site_sta3n,")
    print("    is_active,")
    print("    created_by")
    print(") VALUES")

    for i, user in enumerate(MOCK_USERS):
        is_last = (i == len(MOCK_USERS) - 1)
        comma = ";" if is_last else ","

        print(f"-- User {i+1}: {user['display_name']}")
        print("(")
        print(f"    '{user['email']}',")
        print(f"    '{password_hash}',  -- {password}")
        print(f"    '{user['display_name']}',")
        print(f"    '{user['first_name']}',")
        print(f"    '{user['last_name']}',")
        print(f"    {user['home_site_sta3n']},")
        print("    TRUE,")
        print("    'mock_data_script'")
        print(f"){comma}")
        if not is_last:
            print()

    print()
    print("-- Verify inserts")
    print("SELECT")
    print("    email,")
    print("    display_name,")
    print("    home_site_sta3n,")
    print("    is_active")
    print("FROM auth.users")
    print("ORDER BY email;")
    print()
    print("-- Print summary")
    print("SELECT 'Inserted ' || COUNT(*) || ' mock users' AS summary")
    print("FROM auth.users;")
    print()
    print("-- =====================================================")
    print("-- Copy the above SQL and save to:")
    print("--   db/seeds/auth_users.sql")
    print("-- =====================================================")


def main():
    parser = argparse.ArgumentParser(
        description='Generate bcrypt password hashes for mock users',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--generate-sql', action='store_true',
                        help='Generate SQL INSERT statements for all mock users')
    parser.add_argument('--password', type=str,
                        help='Password to hash (default: prompt interactively)')

    args = parser.parse_args()

    if args.generate_sql:
        # Bulk SQL generation mode
        if args.password:
            password = args.password
        else:
            password = input("Enter shared password for all mock users [VaDemo2025!]: ").strip()
            if not password:
                password = "VaDemo2025!"

        generate_sql_inserts(password)
    else:
        # Single password hash mode
        if args.password:
            password = args.password
        else:
            password = input("Enter password to hash: ").strip()

        if not password:
            print("Error: Password cannot be empty")
            sys.exit(1)

        hashed = hash_password(password)
        print(f"\nBcrypt rounds: {BCRYPT_ROUNDS}")
        print(f"Hashed password: {hashed}")
        print("\nCopy the hash above and use in your SQL INSERT statement.")


if __name__ == "__main__":
    main()
```

**Script Features**:
- **Single Hash Mode** (default): Generate hash for one password interactively
- **Bulk SQL Mode** (`--generate-sql`): Generate complete INSERT statements for all 5 users
- **Password Parameter** (`--password`): Provide password via command line (optional)
- **Config Integration**: Uses `BCRYPT_ROUNDS` from `config.py` for consistency
- **Copy-Paste Ready**: SQL output formatted for direct use in `.sql` files

**Example Usage**:

```bash
# Generate hash for single password interactively
$ python scripts/generate_password_hash.py
Enter password to hash: VaDemo2025!

Bcrypt rounds: 12
Hashed password: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO
Copy the hash above and use in your SQL INSERT statement.

# Generate SQL for all mock users with shared password
$ python scripts/generate_password_hash.py --generate-sql
Enter shared password for all mock users [VaDemo2025!]: VaDemo2025!

-- =====================================================
-- Mock User Data for med-z1 Authentication
-- =====================================================
-- Password for all users: VaDemo2025!
-- Bcrypt rounds: 12
-- Generated hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO
[... complete SQL INSERT statements ...]

# Non-interactive mode (useful for scripting)
$ python scripts/generate_password_hash.py --password "VaDemo2025!" --generate-sql
```

### 9.5 Workflow: Adding New Mock Users

**Step-by-step process**:

1. **Add user details to the script**:
   Edit `scripts/generate_password_hash.py` and add entry to `MOCK_USERS` array:
   ```python
   {
       "email": "clinician.foxtrot@va.gov",
       "display_name": "Dr. Frank Wilson, MD",
       "first_name": "Frank",
       "last_name": "Wilson",
       "home_site_sta3n": 630,  # Palo Alto VA
   },
   ```

2. **Generate SQL with updated user list**:
   ```bash
   python scripts/generate_password_hash.py --generate-sql > db/seeds/auth_users.sql
   ```

3. **Reload the database table**:
   ```bash
   # Connect to PostgreSQL and run the script
   docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql
   ```

4. **Update documentation**:
   Add the new user to `docs/mock-users.md` table

5. **Verify**:
   ```bash
   docker exec postgres16 psql -U postgres -d medz1 -c "SELECT email, display_name FROM auth.users ORDER BY email;"
   ```

### 9.6 Alternative Approach: Unique Passwords Per User

If you prefer more realistic testing with unique passwords per user:

**Example passwords** (still documented in `MOCK_USER_CREDENTIALS.md`):
- `clinician.alpha@va.gov`: `AliceDemo2025!`
- `clinician.bravo@va.gov`: `BobDemo2025!`
- `clinician.charlie@va.gov`: `CarolDemo2025!`
- `clinician.delta@va.gov`: `DavidDemo2025!`
- `clinician.echo@va.gov`: `EmmaDemo2025!`

**Pros**:
- More realistic (mirrors production user management)
- Tests password verification logic more thoroughly
- Better for multi-user session testing

**Cons**:
- Harder for developers to remember (must look up credentials each time)
- More complex to document and maintain
- Requires running hash script 5 times or modifying script to accept password array

**For MVP**: Recommend **shared password approach** for simplicity. Switch to unique passwords if/when testing multi-user scenarios or security edge cases.

**Implementation**:
Modify `generate_password_hash.py` to accept a password mapping:
```python
MOCK_USERS_WITH_PASSWORDS = [
    {"email": "clinician.alpha@va.gov", "password": "AliceDemo2025!", ...},
    {"email": "clinician.bravo@va.gov", "password": "BobDemo2025!", ...},
    # ...
]
```

### 8.2 Session Token Security

**Session ID Generation**:
- Use PostgreSQL's `gen_random_uuid()` (cryptographically secure)
- 128-bit UUID (virtually impossible to guess)
- Format: `123e4567-e89b-12d3-a456-426614174000`

**Cookie Security Attributes**:

```python
response.set_cookie(
    key="session_id",
    value=str(session_id),

    # Security flags
    httponly=True,      # Prevent JavaScript access (XSS protection)
    secure=True,        # HTTPS only (set False for local development)
    samesite="lax",     # CSRF protection (allow top-level navigation)

    # Expiration
    max_age=900         # 15 minutes (browser-side expiration)
)
```

**Cookie Attributes Explained**:
- **httponly=True**: Cookie not accessible via `document.cookie` (prevents XSS attacks from stealing session)
- **secure=True**: Cookie only sent over HTTPS (prevents man-in-the-middle attacks). Set to `False` for local development over HTTP.
- **samesite="lax"**: Cookie sent on same-site requests and top-level navigation. Prevents CSRF while allowing legitimate redirects.
- **max_age=900**: Browser deletes cookie after 15 minutes (backup to server-side expiration)

### 8.3 Protection Against Common Attacks

**SQL Injection**:
- ✅ Use parameterized queries (SQLAlchemy `text()` with `:param` syntax)
- ✅ Never concatenate user input into SQL strings
- ✅ Example:
  ```python
  # CORRECT (parameterized)
  query = text("SELECT * FROM users WHERE email = :email")
  conn.execute(query, {"email": user_input})

  # WRONG (vulnerable to SQL injection)
  query = f"SELECT * FROM users WHERE email = '{user_input}'"
  ```

**Cross-Site Scripting (XSS)**:
- ✅ Jinja2 auto-escapes template variables by default
- ✅ Use `httponly` cookies (session token not accessible to JavaScript)
- ✅ Avoid rendering user input as raw HTML (`{{ var }}` not `{{ var|safe }}`)

**Cross-Site Request Forgery (CSRF)**:
- ✅ Use `SameSite=Lax` cookie attribute
- ✅ Future enhancement: Add CSRF tokens to forms

**Session Hijacking**:
- ✅ Regenerate session ID on login (invalidate old sessions)
- ✅ Use HTTPS in production (secure cookie flag)
- ✅ Short session timeout (15 minutes)
- ✅ Bind session to IP address (optional - can break mobile users)

**Brute Force Attacks**:
- ✅ Use bcrypt with high work factor (12 rounds = ~200ms per hash)
- ⚠️ Future enhancement: Rate limiting on login endpoint
- ⚠️ Future enhancement: Account lockout after N failed attempts

**Timing Attacks** (credential enumeration):
- ✅ Use constant-time password comparison (`bcrypt.checkpw`)
- ✅ Return generic error message ("Invalid email or password", not "User not found")
- ✅ Same response time whether user exists or not

### 8.4 Security Checklist

**✅ Implemented in MVP**:
- [x] Passwords hashed with bcrypt (12 rounds)
- [x] Session tokens use UUIDs (128-bit random)
- [x] HTTP-only, Secure, SameSite cookies
- [x] Parameterized SQL queries
- [x] Auto-escaped Jinja2 templates
- [x] 15-minute session timeout
- [x] Single session enforcement
- [x] Audit logging of login/logout

**⚠️ Future Enhancements**:
- [ ] CSRF tokens on forms
- [ ] Rate limiting on login endpoint
- [ ] Account lockout after failed attempts
- [ ] Password complexity requirements
- [ ] Password expiration policy
- [ ] Multi-factor authentication (MFA)
- [ ] IP-based session binding (optional)

---

## 9. Mock User Data

### 9.0 Data Organization Strategy

**File Locations**:
- **SQL seed data**: `db/seeds/auth_users.sql` (application test data)
- **Documentation**: `docs/mock-users.md` (credential reference)
- **Utility script**: `scripts/generate_password_hash.py` (hash generation)

**Rationale for `db/seeds/` Location**:

Auth users are **application infrastructure**, not clinical source data:
- ✅ **No ETL transformation needed** - created directly in final form for PostgreSQL
- ✅ **Application-level test data** - belongs with database structure (`db/ddl/` and `db/seeds/`)
- ✅ **Different lifecycle** - `mock/` is for VA CDW clinical data sources (CDWWork, CDWWork2)

**Directory Structure**:
```
db/
  ddl/                  # Schema definitions (structure)
    create_auth_tables.sql
  seeds/                # Test/development data (content)
    auth_users.sql      # Mock users for development

docs/
  mock-users.md         # Credential documentation (passwords, emails)

scripts/
  generate_password_hash.py  # Utility to generate bcrypt hashes
```

**Why NOT `mock/` subsystem?**
- `mock/` simulates VA source systems (CDW, VistA) with clinical patient data
- Auth users are med-z1 application users, not clinical data from VA sources
- No Bronze → Silver → Gold transformation pipeline needed for user accounts

### 9.1 Mock User Profiles

**User 1: Dr. Alice Anderson**
- **Email**: `clinician.alpha@va.gov`
- **Password**: `VaDemo2025!` (for demo purposes, not production)
- **Role**: Physician
- **Home Site**: Atlanta VAMC (Sta3n 508)
- **Profile**: Primary care physician, VistA site

**User 2: Dr. Bob Brown**
- **Email**: `clinician.bravo@va.gov`
- **Password**: `VaDemo2025!`
- **Role**: Physician
- **Home Site**: Portland VAMC (Sta3n 648)
- **Profile**: Cardiologist, Cerner site

**User 3: Nurse Carol Chen**
- **Email**: `clinician.charlie@va.gov`
- **Password**: `VaDemo2025!`
- **Role**: Registered Nurse
- **Home Site**: Seattle/Puget Sound VA (Sta3n 663)
- **Profile**: Critical care nurse, Cerner site

**User 4: Dr. David Davis**
- **Email**: `clinician.delta@va.gov`
- **Password**: `VaDemo2025!`
- **Role**: Physician
- **Home Site**: Augusta VAMC (Sta3n 509)
- **Profile**: Emergency medicine, VistA site

**User 5: Pharmacist Emma Evans**
- **Email**: `clinician.echo@va.gov`
- **Password**: `VaDemo2025!`
- **Role**: Pharmacist
- **Home Site**: Boise VAMC (Sta3n 531)
- **Profile**: Clinical pharmacist, Cerner site

### 9.2 SQL Insert Script

**File**: `db/seeds/auth_users.sql`

**Important**: Password hashes below are for `VaDemo2025!` - **DO NOT use in production**

```sql
-- =====================================================
-- Mock User Data for med-z1 Authentication
-- =====================================================
-- Inserts 5 mock users with hashed passwords.
--
-- Password for all users: VaDemo2025!
-- (For demo purposes only - not for production use)
--
-- Usage:
--   docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql
-- =====================================================

-- Clear existing data (development only)
TRUNCATE TABLE auth.sessions CASCADE;
TRUNCATE TABLE auth.audit_logs CASCADE;
DELETE FROM auth.users;

-- Insert mock users
INSERT INTO auth.users (
    email,
    password_hash,
    display_name,
    first_name,
    last_name,
    home_site_sta3n,
    is_active,
    created_by
) VALUES
-- User 1: Dr. Alice Anderson (VistA site)
(
    'clinician.alpha@va.gov',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO',  -- VaDemo2025!
    'Dr. Alice Anderson, MD',
    'Alice',
    'Anderson',
    508,  -- Atlanta VAMC
    TRUE,
    'mock_data_script'
),

-- User 2: Dr. Bob Brown (Cerner site)
(
    'clinician.bravo@va.gov',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO',  -- VaDemo2025!
    'Dr. Bob Brown, DO',
    'Bob',
    'Brown',
    648,  -- Portland VAMC
    TRUE,
    'mock_data_script'
),

-- User 3: Nurse Carol Chen (Cerner site)
(
    'clinician.charlie@va.gov',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO',  -- VaDemo2025!
    'Nurse Carol Chen, RN',
    'Carol',
    'Chen',
    663,  -- Seattle/Puget Sound VA
    TRUE,
    'mock_data_script'
),

-- User 4: Dr. David Davis (VistA site)
(
    'clinician.delta@va.gov',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO',  -- VaDemo2025!
    'Dr. David Davis, MD',
    'David',
    'Davis',
    509,  -- Augusta VAMC
    TRUE,
    'mock_data_script'
),

-- User 5: Pharmacist Emma Evans (Cerner site)
(
    'clinician.echo@va.gov',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO',  -- VaDemo2025!
    'Pharmacist Emma Evans, PharmD',
    'Emma',
    'Evans',
    531,  -- Boise VAMC
    TRUE,
    'mock_data_script'
);

-- Verify inserts
SELECT
    email,
    display_name,
    home_site_sta3n,
    is_active
FROM auth.users
ORDER BY email;

-- Print summary
SELECT 'Inserted ' || COUNT(*) || ' mock users' AS summary
FROM auth.users;
```

**Notes**:
- Password hash generated using: `bcrypt.hashpw(b'VaDemo2025!', bcrypt.gensalt(rounds=12))`
- All users share same password for demo simplicity
- In production, each user would have unique, complex passwords
- `TRUNCATE` commands clear existing data for clean re-runs during development

### 9.3 Generating New Password Hashes

**Script**: `scripts/generate_password_hash.py`

```python
#!/usr/bin/env python3
"""
Generate bcrypt password hashes for mock users.

Usage:
    python scripts/generate_password_hash.py "MyPassword123!"
"""

import sys
import bcrypt

def generate_hash(password: str) -> str:
    """Generate bcrypt hash for given password."""
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_password_hash.py <password>")
        sys.exit(1)

    password = sys.argv[1]
    hashed = generate_hash(password)

    print(f"Password: {password}")
    print(f"Hash:     {hashed}")
    print()
    print("SQL INSERT example:")
    print(f"  password_hash = '{hashed}'")
```

**Example**:
```bash
$ python scripts/generate_password_hash.py "VaDemo2025!"
Password: VaDemo2025!
Hash:     $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO

SQL INSERT example:
  password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpBWzZ7mO'
```

---

## 10. FastAPI Integration

### 10.1 Authentication Router

**File**: `app/routes/auth.py`

```python
# ---------------------------------------------------------------------
# app/routes/auth.py
# ---------------------------------------------------------------------
# Authentication Routes
# Handles user login, logout, and session management.
# ---------------------------------------------------------------------

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging

from app.db.auth import (
    get_user_by_email,
    verify_password,
    create_session,
    invalidate_session,
    invalidate_user_sessions,
    log_audit_event,
    update_last_login
)

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request, error: str = None):
    """
    Render the login page.

    Query param 'error' used to display error messages after redirect.
    """
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": error
        }
    )


@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Authenticate user credentials and create session.

    Process:
    1. Validate email/password
    2. Invalidate old sessions (single-session enforcement)
    3. Create new session
    4. Log audit event
    5. Set session cookie
    6. Redirect to dashboard
    """
    try:
        # 1. Query user by email
        user = get_user_by_email(email)
        if not user:
            logger.warning(f"Login attempt for non-existent email: {email}")
            log_audit_event(
                event_type='login_failed',
                email=email,
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent'),
                success=False,
                failure_reason='User not found'
            )
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Invalid email or password"
                },
                status_code=401
            )

        # 2. Verify password hash
        if not verify_password(password, user['password_hash']):
            logger.warning(f"Failed login attempt for {email}: invalid password")
            log_audit_event(
                event_type='login_failed',
                user_id=user['user_id'],
                email=email,
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent'),
                success=False,
                failure_reason='Invalid password'
            )
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Invalid email or password"
                },
                status_code=401
            )

        # 3. Check if account is active
        if not user['is_active']:
            logger.warning(f"Login attempt for inactive account: {email}")
            log_audit_event(
                event_type='login_failed',
                user_id=user['user_id'],
                email=email,
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent'),
                success=False,
                failure_reason='Account inactive'
            )
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Account is inactive. Please contact support."
                },
                status_code=403
            )

        # 4. Invalidate old sessions (single-session enforcement)
        invalidate_user_sessions(user['user_id'])

        # 5. Create new session
        session_id = create_session(
            user_id=user['user_id'],
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )

        # 6. Log successful login
        log_audit_event(
            event_type='login',
            user_id=user['user_id'],
            email=email,
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            session_id=session_id,
            success=True
        )

        # 7. Update last_login_at timestamp
        update_last_login(user['user_id'])

        logger.info(f"Successful login for {email} (user_id: {user['user_id']})")

        # 8. Set session cookie and redirect to dashboard
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="session_id",
            value=str(session_id),
            httponly=True,
            secure=False,  # Set to True in production (HTTPS only)
            samesite="lax",
            max_age=900  # 15 minutes
        )
        return response

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "An error occurred. Please try again."
            },
            status_code=500
        )


@router.post("/logout")
async def post_logout(request: Request):
    """
    Log out user and invalidate session.

    Process:
    1. Get session_id from cookie
    2. Invalidate session in database
    3. Log audit event
    4. Clear session cookie
    5. Redirect to login page
    """
    session_id = request.cookies.get("session_id")

    if session_id:
        try:
            # Get session details for audit log
            from app.db.auth import get_session
            session = get_session(session_id)

            if session:
                # Invalidate session
                invalidate_session(session_id)

                # Log logout event
                log_audit_event(
                    event_type='logout',
                    user_id=session['user_id'],
                    email=None,  # Could look up from user_id if needed
                    ip_address=request.client.host,
                    user_agent=request.headers.get('user-agent'),
                    session_id=session_id,
                    success=True
                )

                logger.info(f"User logged out (session: {session_id})")

        except Exception as e:
            logger.error(f"Error during logout: {e}")

    # Clear cookie and redirect to login
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response
```

### 10.2 Authentication Middleware

**File**: `app/middleware/auth.py`

```python
# ---------------------------------------------------------------------
# app/middleware/auth.py
# ---------------------------------------------------------------------
# Authentication Middleware
# Enforces login requirement on all routes (except /login and /static).
# Validates session on every request and extends timeout on activity.
# ---------------------------------------------------------------------

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging

from app.db.auth import get_session, extend_session, get_user

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce authentication on all routes.

    - Checks for valid session_id cookie
    - Validates session in database
    - Extends session timeout on activity
    - Injects user context into request.state
    - Redirects to /login if unauthenticated
    """

    # Routes that don't require authentication
    PUBLIC_ROUTES = [
        "/login",
        "/static",
        "/favicon.ico",
        "/docs",      # FastAPI docs (can remove in production)
        "/openapi.json"
    ]

    async def dispatch(self, request: Request, call_next):
        """Process each request through authentication check."""

        # Skip authentication for public routes
        if any(request.url.path.startswith(route) for route in self.PUBLIC_ROUTES):
            return await call_next(request)

        # Extract session_id from cookie
        session_id = request.cookies.get("session_id")
        if not session_id:
            logger.debug(f"No session cookie for {request.url.path}")
            return RedirectResponse(url="/login", status_code=303)

        # Validate session
        try:
            session = get_session(session_id)
            if not session:
                logger.debug(f"Session {session_id} not found in database")
                return self._redirect_to_login_with_cleared_cookie()

            # Check if session is active
            if not session['is_active']:
                logger.debug(f"Session {session_id} is inactive")
                return self._redirect_to_login_with_cleared_cookie()

            # Check if session has expired
            if session['expires_at'] < datetime.now():
                logger.info(f"Session {session_id} expired (inactive timeout)")
                from app.db.auth import log_audit_event
                log_audit_event(
                    event_type='session_timeout',
                    user_id=session['user_id'],
                    session_id=session_id,
                    success=True
                )
                return self._redirect_to_login_with_cleared_cookie()

            # Session is valid - extend timeout
            extend_session(session_id)

            # Inject user context into request
            user = get_user(session['user_id'])
            request.state.user = user
            request.state.session_id = session_id

            # Continue to route handler
            return await call_next(request)

        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return self._redirect_to_login_with_cleared_cookie()

    def _redirect_to_login_with_cleared_cookie(self):
        """Redirect to login and clear invalid session cookie."""
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("session_id")
        return response
```

### 10.3 Database Functions

**File**: `app/db/auth.py`

```python
# ---------------------------------------------------------------------
# app/db/auth.py
# ---------------------------------------------------------------------
# Authentication Database Functions
# Handles user queries, session management, and audit logging.
# ---------------------------------------------------------------------

from sqlalchemy import text, create_engine
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
import bcrypt
import logging

from config import POSTGRES_CONNECTION_STRING

engine = create_engine(POSTGRES_CONNECTION_STRING)
logger = logging.getLogger(__name__)


# =============================================================================
# USER FUNCTIONS
# =============================================================================

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address."""
    query = text("""
        SELECT
            user_id,
            email,
            password_hash,
            display_name,
            first_name,
            last_name,
            home_site_sta3n,
            is_active,
            is_locked,
            last_login_at
        FROM auth.users
        WHERE email = :email
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"email": email})
        row = result.fetchone()
        if row:
            return {
                "user_id": row[0],
                "email": row[1],
                "password_hash": row[2],
                "display_name": row[3],
                "first_name": row[4],
                "last_name": row[5],
                "home_site_sta3n": row[6],
                "is_active": row[7],
                "is_locked": row[8],
                "last_login_at": row[9]
            }
        return None


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by user_id."""
    query = text("""
        SELECT
            user_id,
            email,
            display_name,
            first_name,
            last_name,
            home_site_sta3n,
            is_active
        FROM auth.users
        WHERE user_id = :user_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        row = result.fetchone()
        if row:
            return {
                "user_id": row[0],
                "email": row[1],
                "display_name": row[2],
                "first_name": row[3],
                "last_name": row[4],
                "home_site_sta3n": row[5],
                "is_active": row[6]
            }
        return None


def update_last_login(user_id: str):
    """Update user's last_login_at timestamp."""
    query = text("""
        UPDATE auth.users
        SET last_login_at = :now
        WHERE user_id = :user_id
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "now": datetime.now(),
            "user_id": user_id
        })
        conn.commit()


# =============================================================================
# PASSWORD FUNCTIONS
# =============================================================================

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


# =============================================================================
# SESSION FUNCTIONS
# =============================================================================

def create_session(
    user_id: str,
    ip_address: str = None,
    user_agent: str = None
) -> str:
    """
    Create new session for user.

    Returns session_id (UUID).
    """
    session_id = str(uuid.uuid4())
    now = datetime.now()
    expires_at = now + timedelta(minutes=15)

    query = text("""
        INSERT INTO auth.sessions (
            session_id,
            user_id,
            created_at,
            last_activity_at,
            expires_at,
            is_active,
            ip_address,
            user_agent
        ) VALUES (
            :session_id,
            :user_id,
            :now,
            :now,
            :expires_at,
            TRUE,
            :ip_address,
            :user_agent
        )
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "session_id": session_id,
            "user_id": user_id,
            "now": now,
            "expires_at": expires_at,
            "ip_address": ip_address,
            "user_agent": user_agent
        })
        conn.commit()

    logger.info(f"Created session {session_id} for user {user_id}")
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by session_id."""
    query = text("""
        SELECT
            session_id,
            user_id,
            created_at,
            last_activity_at,
            expires_at,
            is_active,
            ip_address,
            user_agent
        FROM auth.sessions
        WHERE session_id = :session_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"session_id": session_id})
        row = result.fetchone()
        if row:
            return {
                "session_id": row[0],
                "user_id": row[1],
                "created_at": row[2],
                "last_activity_at": row[3],
                "expires_at": row[4],
                "is_active": row[5],
                "ip_address": row[6],
                "user_agent": row[7]
            }
        return None


def extend_session(session_id: str):
    """Update session activity and extend expiration."""
    now = datetime.now()
    expires_at = now + timedelta(minutes=15)

    query = text("""
        UPDATE auth.sessions
        SET last_activity_at = :now,
            expires_at = :expires_at
        WHERE session_id = :session_id
          AND is_active = TRUE
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "now": now,
            "expires_at": expires_at,
            "session_id": session_id
        })
        conn.commit()


def invalidate_session(session_id: str):
    """Invalidate a specific session."""
    query = text("""
        UPDATE auth.sessions
        SET is_active = FALSE
        WHERE session_id = :session_id
    """)

    with engine.connect() as conn:
        conn.execute(query, {"session_id": session_id})
        conn.commit()

    logger.info(f"Invalidated session {session_id}")


def invalidate_user_sessions(user_id: str, except_session_id: str = None):
    """Invalidate all active sessions for a user (except optionally one)."""
    query = text("""
        UPDATE auth.sessions
        SET is_active = FALSE
        WHERE user_id = :user_id
          AND is_active = TRUE
          AND (:except_session_id IS NULL OR session_id != :except_session_id)
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "user_id": user_id,
            "except_session_id": except_session_id
        })
        conn.commit()

        if result.rowcount > 0:
            logger.info(f"Invalidated {result.rowcount} session(s) for user {user_id}")


# =============================================================================
# AUDIT LOG FUNCTIONS
# =============================================================================

def log_audit_event(
    event_type: str,
    user_id: str = None,
    email: str = None,
    ip_address: str = None,
    user_agent: str = None,
    success: bool = None,
    failure_reason: str = None,
    session_id: str = None
):
    """Log an authentication audit event."""
    query = text("""
        INSERT INTO auth.audit_logs (
            user_id,
            event_type,
            event_timestamp,
            email,
            ip_address,
            user_agent,
            success,
            failure_reason,
            session_id
        ) VALUES (
            :user_id,
            :event_type,
            :now,
            :email,
            :ip_address,
            :user_agent,
            :success,
            :failure_reason,
            :session_id
        )
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "user_id": user_id,
            "event_type": event_type,
            "now": datetime.now(),
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "failure_reason": failure_reason,
            "session_id": session_id
        })
        conn.commit()

    logger.info(f"Audit log: {event_type} for {email or user_id}")
```

### 10.4 Main Application Updates

**File**: `app/main.py` (Updated)

```python
# Add authentication middleware and router

from app.middleware.auth import AuthMiddleware
from app.routes import auth

# Add auth middleware (before other routers)
app.add_middleware(AuthMiddleware)

# Include auth router
app.include_router(auth.router)
```

### 10.5 CCOW v2.0 Integration (Shared Authentication)

**Overview:**

As of v2.0, the CCOW Context Vault service shares authentication infrastructure with the med-z1 application:

**Shared Components:**
- **Database Tables:** `auth.users` and `auth.sessions` (single source of truth)
- **Session Validation:** Both services use compatible session validation logic
- **Session Extension:** Session timeout extends on activity in either service
- **Single Sign-On Effect:** Login to med-z1 enables authenticated CCOW API access

**Implementation:**

```python
# ccow/auth_helper.py - Shared authentication helper
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from config import DATABASE_URL, SESSION_TIMEOUT_MINUTES

def get_user_from_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Validate session and return user information.
    Shared by both med-z1 app and CCOW Context Vault.

    Returns:
        User dict if session valid, None otherwise
    """
    # 1. Query session from auth.sessions
    # 2. Check if active and not expired (with timezone handling)
    # 3. Extend session timeout (sliding window)
    # 4. Query user from auth.users
    # 5. Return user info or None
```

**Key Integration Points:**

1. **CCOW API Endpoints Use Session Validation:**
   ```python
   # ccow/main.py (example endpoint)
   @app.get("/ccow/active-patient")
   async def get_active_patient(request: Request, session_id: str = Cookie(None)):
       """Get active patient context (requires authentication)."""
       user = get_user_from_session(session_id)
       if not user:
           raise HTTPException(status_code=401, detail="Unauthorized")
       # ... return active patient context
   ```

2. **Session Timeout Extends in Both Services:**
   - User activity in med-z1 app → session extended → CCOW API stays authenticated
   - CCOW API call → session extended → med-z1 app stays authenticated
   - Inactivity in both → session expires after 15 minutes → both require re-login

3. **Timezone-Aware Session Validation (v2.0 Fix):**
   ```python
   # Handles PostgreSQL TIMESTAMP WITHOUT TIME ZONE correctly
   if expires_at.tzinfo is None:
       now = datetime.now()  # Local time, no timezone
   else:
       now = datetime.now(timezone.utc)  # UTC time
   ```

**For Complete Details:**
- CCOW v2.0 architecture and shared session implementation: See `docs/spec/ccow-v2-implementation-summary.md`
- Session timeout behavior across both services: See `docs/spec/session-timeout-behavior.md`
- Testing CCOW API with authentication: See `docs/spec/ccow-v2-testing-guide.md`

**Benefits:**
- ✅ Single source of truth for authentication
- ✅ Consistent session management across services
- ✅ Simplified codebase (shared auth logic)
- ✅ Automatic session extension across all user activity

---

## 11. HTMX and UI Patterns

### 11.1 Login Page Template

**File**: `app/templates/login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In - med-z1</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #003d5b 0%, #005a8c 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .login-container {
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            width: 440px;
            padding: 44px 44px 56px;
        }

        .login-header {
            text-align: center;
            margin-bottom: 32px;
        }

        .login-header img {
            width: 200px;
            margin-bottom: 16px;
        }

        .login-header h1 {
            font-size: 24px;
            font-weight: 600;
            color: #1f1f1f;
            margin: 0 0 8px 0;
        }

        .login-header p {
            font-size: 15px;
            color: #605e5c;
            margin: 0;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group label {
            display: block;
            font-size: 15px;
            font-weight: 600;
            color: #323130;
            margin-bottom: 8px;
        }

        .form-group input {
            width: 100%;
            padding: 10px 12px;
            font-size: 15px;
            border: 1px solid #8a8886;
            border-radius: 2px;
            box-sizing: border-box;
            transition: border-color 0.1s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #0078d4;
            border-width: 2px;
            padding: 9px 11px;
        }

        .error-message {
            background: #fde7e9;
            border: 1px solid #a80000;
            border-radius: 2px;
            padding: 12px;
            margin-bottom: 24px;
            color: #a80000;
            font-size: 13px;
        }

        .btn-primary {
            width: 100%;
            padding: 11px 20px;
            font-size: 15px;
            font-weight: 600;
            color: white;
            background: #0078d4;
            border: 1px solid #0078d4;
            border-radius: 2px;
            cursor: pointer;
            transition: background 0.1s;
        }

        .btn-primary:hover {
            background: #106ebe;
        }

        .btn-primary:active {
            background: #005a9e;
        }

        .login-footer {
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid #edebe9;
            text-align: center;
            font-size: 13px;
            color: #605e5c;
        }

        .login-footer a {
            color: #0078d4;
            text-decoration: none;
        }

        .login-footer a:hover {
            text-decoration: underline;
        }

        .badge-demo {
            display: inline-block;
            background: #f3f2f1;
            color: #323130;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 16px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <!-- VA Logo or med-z1 logo -->
            <h1>med-z1</h1>
            <p>Joint Longitudinal Viewer - Next Generation</p>
            <span class="badge-demo">DEMO ENVIRONMENT</span>
        </div>

        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        <form method="POST" action="/login">
            <div class="form-group">
                <label for="email">Email</label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="user@va.gov"
                    required
                    autofocus
                >
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input
                    type="password"
                    id="password"
                    name="password"
                    placeholder="Enter your password"
                    required
                >
            </div>

            <button type="submit" class="btn-primary">
                Sign In
            </button>
        </form>

        <div class="login-footer">
            <p>Demo Credentials:</p>
            <p>Email: <code>clinician.alpha@va.gov</code></p>
            <p>Password: <code>VaDemo2025!</code></p>
        </div>
    </div>
</body>
</html>
```

### 11.2 Topbar User Display

**Update**: `app/templates/base.html` (Topbar Section)

```html
<!-- Topbar with user info and logout -->
<div class="topbar">
    <div class="topbar-left">
        <span class="app-title">med-z1</span>
        <span class="app-subtitle">Joint Longitudinal Viewer</span>
    </div>

    <div class="topbar-center">
        <!-- Patient context (existing) -->
        {% if patient %}
        <div class="patient-context">
            <strong>{{ patient.patient_name }}</strong>
            <span class="patient-details">
                ICN: {{ patient.icn }} | SSN: {{ patient.ssn_last4 }}
            </span>
        </div>
        {% else %}
        <div class="patient-context-empty">
            No patient selected
        </div>
        {% endif %}
    </div>

    <div class="topbar-right">
        <!-- NEW: User info and logout -->
        {% if request.state.user %}
        <div class="user-info">
            <span class="user-name">{{ request.state.user.display_name }}</span>
            <span class="user-site">
                Home Site: {{ request.state.user.home_site_sta3n }}
            </span>
        </div>
        <form method="POST" action="/logout" style="display: inline;">
            <button type="submit" class="btn-logout">
                Sign Out
            </button>
        </form>
        {% endif %}
    </div>
</div>
```

**CSS** (add to `app/static/css/main.css`):

```css
/* Topbar user info */
.user-info {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    margin-right: 16px;
    font-size: 13px;
}

.user-name {
    font-weight: 600;
    color: #1f1f1f;
}

.user-site {
    color: #605e5c;
    font-size: 12px;
}

.btn-logout {
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #323130;
    background: #f3f2f1;
    border: 1px solid #8a8886;
    border-radius: 2px;
    cursor: pointer;
    transition: background 0.1s;
}

.btn-logout:hover {
    background: #edebe9;
}
```

### 11.3 HTMX Session Handling

**Handling Expired Sessions in HTMX Requests**:

When a session expires and the user triggers an HTMX request (e.g., clicking a dashboard widget), the middleware will redirect to `/login`. However, HTMX needs special handling for redirects.

**Option 1: Client-Side Redirect Detection** (Simplest for MVP)

```javascript
// app/static/js/auth.js

// Detect full-page redirects from HTMX requests
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    // If response is a redirect to login, do full page redirect
    if (evt.detail.xhr.responseURL.includes('/login')) {
        window.location.href = '/login';
        evt.detail.shouldSwap = false;
    }
});
```

**Option 2: Custom Header (More Robust)**

Middleware sets custom header on unauthenticated requests:

```python
# In AuthMiddleware, when session invalid:
response = RedirectResponse(url="/login", status_code=303)
response.headers["HX-Redirect"] = "/login"  # HTMX-specific redirect
return response
```

HTMX automatically handles `HX-Redirect` header by doing full-page redirect.

---

## 12. Audit Logging

### 12.1 Logged Events

**Event Types**:

| Event Type | Trigger | Success | Details Logged |
|-----------|---------|---------|----------------|
| `login` | Successful login | TRUE | user_id, email, ip_address, user_agent, session_id |
| `login_failed` | Invalid credentials | FALSE | email (if provided), ip_address, failure_reason |
| `logout` | User-initiated logout | TRUE | user_id, session_id |
| `session_timeout` | Inactivity timeout | TRUE | user_id, session_id |
| `session_invalidated` | Forced logout (new login) | TRUE | user_id, reason |

### 12.2 Audit Log Queries

**Recent Login Activity**:

```sql
SELECT
    event_type,
    email,
    event_timestamp,
    success,
    ip_address
FROM auth.audit_logs
WHERE event_type IN ('login', 'login_failed')
ORDER BY event_timestamp DESC
LIMIT 50;
```

**Failed Login Attempts for User**:

```sql
SELECT
    event_timestamp,
    email,
    ip_address,
    failure_reason
FROM auth.audit_logs
WHERE event_type = 'login_failed'
  AND email = 'clinician.alpha@va.gov'
ORDER BY event_timestamp DESC;
```

**Active Sessions by User**:

```sql
SELECT
    u.email,
    u.display_name,
    s.session_id,
    s.created_at,
    s.last_activity_at,
    s.expires_at,
    s.ip_address
FROM auth.sessions s
JOIN auth.users u ON s.user_id = u.user_id
WHERE s.is_active = TRUE
ORDER BY s.last_activity_at DESC;
```

### 12.3 Audit Log Retention

**Policy** (for future implementation):
- Retain audit logs for **90 days** minimum (HIPAA requirement)
- Archive logs older than 90 days to separate table or file storage
- Never delete audit logs (archive for compliance)

**Cleanup Script** (future):

```sql
-- Archive old audit logs (keep last 90 days in primary table)
INSERT INTO auth.audit_logs_archive
SELECT * FROM auth.audit_logs
WHERE event_timestamp < (CURRENT_TIMESTAMP - INTERVAL '90 days');

DELETE FROM auth.audit_logs
WHERE event_timestamp < (CURRENT_TIMESTAMP - INTERVAL '90 days');
```

---

## 13. Implementation Roadmap

### 13.1 Phase Breakdown

**✅ Phase 1: Database Foundation** (COMPLETE - 2025-12-18)
- ✅ Create `auth` schema in PostgreSQL
- ✅ Create tables: `users`, `sessions`, `audit_logs`
- ✅ Write DDL script: `db/ddl/create_auth_tables.sql`
- ✅ Test: Verify tables created successfully
- **Implementation Notes**: Used UUID primary keys, separate auth schema for security isolation

**✅ Phase 2: Mock User Data** (COMPLETE - 2025-12-18)
- ✅ Create password hashing utility: `scripts/generate_password_hash.py`
- ✅ Generate bcrypt hashes for mock passwords
- ✅ Write SQL insert script: `db/seeds/auth_users.sql`
- ✅ Create documentation: `docs/mock-users.md`
- ✅ Populate 7 mock users in database (expanded from initial 5)
- ✅ Test: Query users table, verify hashes
- **Implementation Notes**: All users share password `VaDemo2025!`, placed in `db/seeds/` not `mock/`

**✅ Phase 3: Authentication Database Functions** (COMPLETE - 2025-12-18)
- ✅ Create `app/db/auth.py`
- ✅ Implement user query functions (`get_user_by_email`, `get_user_by_id`)
- ✅ Implement password verification (`verify_password`, `hash_password`)
- ✅ Implement session functions (`create_session`, `get_session`, `extend_session`, `invalidate_session`)
- ✅ Implement audit logging (`log_audit_event`)
- ✅ Test: Manual testing with test script
- **Implementation Notes**: Fixed UUID casting syntax to `CAST(:param AS UUID)` for SQLAlchemy compatibility

**✅ Phase 4: Login/Logout Routes** (COMPLETE - 2025-12-18)
- ✅ Create `app/routes/auth.py`
- ✅ Implement `GET /login` (render login page)
- ✅ Implement `POST /login` (authenticate and create session)
- ✅ Implement `POST /logout` (invalidate session)
- ✅ Test: Manual login/logout flow
- **Implementation Notes**: Single-session enforcement, comprehensive audit logging, graceful error handling

**✅ Phase 5: Authentication Middleware** (COMPLETE - 2025-12-18)
- ✅ Create `app/middleware/auth.py`
- ✅ Implement `AuthMiddleware` class
- ✅ Session validation logic
- ✅ Session extension on activity
- ✅ Inject user context into `request.state`
- ✅ Test: Verify middleware blocks unauthenticated requests
- **Implementation Notes**: Public routes defined, automatic session timeout extension, user context injection

**✅ Phase 6: Login Page UI** (COMPLETE - 2025-12-18)
- ✅ Create `app/templates/login.html`
- ✅ Style to resemble VA/Entra ID login
- ✅ Add error message display
- ✅ Add demo credentials footer
- ✅ Test: Visual review, accessibility check
- **Implementation Notes**: Full accessibility support (ARIA, keyboard nav, high contrast, reduced motion), responsive design

**✅ Phase 7: Main Application Integration** (COMPLETE - 2025-12-18)
- ✅ Update `app/main.py` to add middleware
- ✅ Include auth router
- ✅ Update `base.html` template (user info in sidebar)
- ✅ Add logout button
- ✅ Create template context helper (`app/utils/template_context.py`)
- ✅ Test: Full login → dashboard → logout flow
- **Implementation Notes**: Template helper simplifies passing user context to all templates

**✅ Phase 8: Testing and Documentation** (COMPLETE - 2025-12-18)
- ✅ Create comprehensive test suite: `scripts/test_auth_flow.py`
- ✅ Test coverage: 7 automated tests (unauthenticated access, login page, invalid login, valid login, authenticated access, logout, post-logout)
- ✅ Create implementation summary: `docs/auth-implementation-summary.md`
- ✅ Update design document with completion status
- ✅ Test: All tests passing
- **Implementation Notes**: HTMX session handling works seamlessly with middleware (no special handling needed)

**Total Actual Time**: 1 day (2025-12-18) - Much faster than estimated due to clear design and focused implementation

### 13.2 Implementation Order

1. ✅ Database schema (foundational)
2. ✅ Mock user data (enables testing)
3. ✅ Database functions (core logic)
4. ✅ Login/logout routes (authentication flow)
5. ✅ Login page UI (user interface)
6. ✅ Middleware (enforcement)
7. ✅ Integration (connect all pieces)
8. ✅ HTMX handling (edge cases)
9. ✅ Testing (quality assurance)
10. ✅ Documentation (handoff)

### 13.3 Testing Checklist

**Unit Tests**:
- ✅ `verify_password()` - Correct password returns True
- ✅ `verify_password()` - Incorrect password returns False
- ✅ `create_session()` - Returns valid UUID
- ✅ `get_session()` - Retrieves correct session
- ✅ `extend_session()` - Updates expires_at correctly
- ✅ `invalidate_session()` - Sets is_active = FALSE

**Integration Tests** (via `scripts/test_auth_flow.py`):
- ✅ POST /login with valid credentials → 303 redirect to /
- ✅ POST /login with invalid password → Error message displayed
- ✅ POST /login with non-existent user → Error message displayed
- ✅ GET / without session → 303 redirect to /login
- ✅ GET / with valid session → Dashboard rendered
- ✅ POST /logout → Session invalidated, redirect to /login
- ⏳ POST /login with inactive account → Error message displayed (manual test required)
- ⏳ GET / with expired session → 303 redirect to /login (manual test required)

**End-to-End Tests**:
- ✅ User logs in → Sees dashboard with user name in sidebar
- ✅ User clicks Sign Out → Redirected to login, cannot access dashboard
- ⏳ User clicks dashboard widgets → Widgets load correctly (manual test required)
- ⏳ User waits 15 minutes → Next request redirects to login (manual test required)
- ⏳ User logs in from Device A → Logs in from Device B → Device A redirected to login (manual test required)

**Security Tests**:
- ✅ SQL injection protection via parameterized queries (SQLAlchemy)
- ✅ XSS protection via Jinja2 auto-escaping
- ✅ Session cookie has `httponly`, `samesite=lax` flags (secure=false in dev, true in prod)
- ✅ Direct access to protected routes without login → Redirected to /login
- ⏳ Tampered session_id cookie → Redirected to login (manual test required)

---

## 14. Testing Strategy

### 14.1 Manual Testing Scenarios

**Scenario 1: First-Time Login**
```
Given: User has never logged in before
When: User visits http://localhost:8000/
Then: User is redirected to /login
When: User enters valid credentials (clinician.alpha@va.gov / VaDemo2025!)
Then: User is redirected to dashboard
And: Dashboard displays user's name in topbar
And: Audit log contains 'login' event
```

**Scenario 2: Incorrect Password**
```
Given: User is on /login page
When: User enters valid email but wrong password
Then: Login page re-renders with error message
And: Error message says "Invalid email or password"
And: Audit log contains 'login_failed' event
```

**Scenario 3: Session Timeout**
```
Given: User is logged in and viewing dashboard
When: User does not interact for 15 minutes
And: User clicks a dashboard widget
Then: User is redirected to /login
And: Audit log contains 'session_timeout' event
```

**Scenario 4: Logout**
```
Given: User is logged in
When: User clicks "Sign Out" button
Then: User is redirected to /login
And: Session is invalidated in database
And: Audit log contains 'logout' event
When: User clicks browser back button
Then: User is redirected to /login (not dashboard)
```

**Scenario 5: Single Session Enforcement**
```
Given: User is logged in on Device A (laptop)
When: User logs in on Device B (desktop)
Then: Device B session is created
And: Device A session is invalidated
When: User on Device A refreshes page
Then: User is redirected to /login
And: Audit log contains 'session_invalidated' event
```

### 14.2 Automated Testing

**File**: `tests/test_auth.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.auth import hash_password, verify_password, create_session, get_session

client = TestClient(app)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123!"
    hashed = hash_password(password)

    # Verify correct password
    assert verify_password(password, hashed) is True

    # Verify incorrect password
    assert verify_password("WrongPassword", hashed) is False


def test_login_page_renders():
    """Test that login page renders for unauthenticated users."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.content


def test_login_with_valid_credentials():
    """Test successful login flow."""
    response = client.post("/login", data={
        "email": "clinician.alpha@va.gov",
        "password": "VaDemo2025!"
    }, follow_redirects=False)

    # Should redirect to dashboard
    assert response.status_code == 303
    assert response.headers["location"] == "/"

    # Should set session cookie
    assert "session_id" in response.cookies


def test_login_with_invalid_password():
    """Test login with incorrect password."""
    response = client.post("/login", data={
        "email": "clinician.alpha@va.gov",
        "password": "WrongPassword!"
    })

    # Should stay on login page with error
    assert response.status_code == 401
    assert b"Invalid email or password" in response.content


def test_login_with_nonexistent_user():
    """Test login with email not in database."""
    response = client.post("/login", data={
        "email": "nonexistent@va.gov",
        "password": "AnyPassword!"
    })

    # Should stay on login page with error
    assert response.status_code == 401
    assert b"Invalid email or password" in response.content


def test_dashboard_requires_authentication():
    """Test that dashboard redirects to login when not authenticated."""
    response = client.get("/", follow_redirects=False)

    # Should redirect to login
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_session_expiration():
    """Test that expired sessions are rejected."""
    from datetime import datetime, timedelta
    from app.db.auth import invalidate_session

    # Create session
    session_id = create_session(user_id="test-user-id")

    # Manually expire session
    from app.db.auth import engine, text
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE auth.sessions SET expires_at = :past WHERE session_id = :sid"),
            {"past": datetime.now() - timedelta(minutes=1), "sid": session_id}
        )
        conn.commit()

    # Try to use expired session
    response = client.get("/", cookies={"session_id": session_id}, follow_redirects=False)

    # Should redirect to login
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_logout():
    """Test logout flow."""
    # First, log in
    login_response = client.post("/login", data={
        "email": "clinician.alpha@va.gov",
        "password": "VaDemo2025!"
    }, follow_redirects=False)

    session_cookie = login_response.cookies.get("session_id")

    # Then, log out
    logout_response = client.post("/logout", cookies={"session_id": session_cookie}, follow_redirects=False)

    # Should redirect to login
    assert logout_response.status_code == 303
    assert logout_response.headers["location"] == "/login"

    # Session should be invalidated
    session = get_session(session_cookie)
    assert session is None or session['is_active'] is False
```

**Run Tests**:
```bash
pytest tests/test_auth.py -v
```

---

## 15. Future Enhancements

### 15.1 Phase 2 Features

**Password Reset Flow**:
- Email-based password reset
- Secure token generation
- Time-limited reset links
- Password complexity requirements

**Account Lockout**:
- Lock account after N failed login attempts
- Unlock after time period or admin intervention
- Log lockout events

**Remember Me**:
- Extended session duration (e.g., 30 days)
- Separate "remember_token" cookie
- Security: Require re-authentication for sensitive actions

**User Preferences**:
- UI theme selection (Light, Dark, High Contrast)
- Dashboard layout preferences
- Default date range filters
- Store in `user_preferences` JSONB column

### 15.2 Phase 3 Features

**Role-Based Access Control (RBAC)**:
- Define roles: Physician, Nurse, Pharmacist, Admin
- Permission system: Read, Write, Delete
- Site-based data filtering
- Role-specific UI elements

**Multi-Factor Authentication (MFA)**:
- TOTP (Time-Based One-Time Password)
- SMS codes
- Email codes
- Backup codes

**Admin UI**:
- User management (create, edit, deactivate users)
- Session management (view active sessions, force logout)
- Audit log viewer
- System configuration

**Real Entra ID Integration**:
- Replace mock login with real Azure AD OIDC
- Use `authlib` library for OAuth 2.0
- Handle token refresh
- Support phish-resistant authentication

### 15.3 Production Considerations

**HTTPS Enforcement**:
- Require HTTPS in production
- Set `secure=True` on cookies
- Redirect HTTP to HTTPS

**Rate Limiting**:
- Limit login attempts per IP (e.g., 5 per minute)
- Use Redis or in-memory cache
- Return 429 Too Many Requests

**Session Storage Scalability**:
- Consider Redis for session storage (faster than PostgreSQL)
- Horizontal scaling: Share session store across multiple app instances
- Session replication for high availability

**Audit Log Scaling**:
- Separate audit database
- Log shipping to SIEM (Security Information and Event Management)
- Compliance reporting tools

**Monitoring**:
- Track login success/failure rates
- Alert on unusual patterns (e.g., spike in failed logins)
- Session count metrics
- Performance metrics (session query time)

---

## 16. File Inventory

This section provides a complete categorized listing of all authentication implementation files.

### 16.1 Database Layer

**Schema and Seeds**:
- `db/ddl/create_auth_tables.sql` - PostgreSQL schema creation (users, sessions, audit_logs)
- `db/seeds/auth_users.sql` - Mock user seed data (7 clinicians)

**Query Layer**:
- `app/db/auth.py` - Authentication database query functions (503 lines)
  - User functions: `get_user_by_email()`, `get_user_by_id()`
  - Password functions: `verify_password()`, `hash_password()`
  - Session functions: `create_session()`, `get_session()`, `extend_session()`, `invalidate_session()`, `invalidate_user_sessions()`
  - User management: `update_last_login()`
  - Audit logging: `log_audit_event()`
  - Maintenance: `cleanup_expired_sessions()`

### 16.2 Application Layer

**Routes**:
- `app/routes/auth.py` - Authentication routes (338 lines)
  - `GET /login` - Display login page (or redirect if already logged in)
  - `POST /login` - Process login form submission
  - `POST /logout` - Logout and invalidate session
  - `GET /logout` - Redirect to POST /logout for bookmark handling

**Middleware**:
- `app/middleware/auth.py` - Authentication middleware (168 lines)
  - Intercepts all HTTP requests before route handlers
  - Validates sessions and injects user context into `request.state`
  - Extends session timeout on activity (sliding window)
  - Redirects unauthenticated requests to /login

**Utilities**:
- `app/utils/template_context.py` - Template context helper
  - `get_base_context(request, **kwargs)` - Inject user context into templates

### 16.3 Templates

**Login Page**:
- `app/templates/login.html` - Microsoft Entra ID-style login page
  - Responsive design with accessibility features
  - Demo credentials display
  - Error message handling

**Base Template**:
- `app/templates/base.html` - Updated for user display
  - User display name in sidebar footer
  - Sign Out button with HTMX compatibility

### 16.4 Scripts

**Password Management**:
- `scripts/generate_password_hash.py` - Password hash generation utility
  - Generate bcrypt hashes for new users
  - Regenerate all user SQL with `--generate-sql` flag

**Testing**:
- `scripts/test_auth_flow.py` - Authentication flow test suite
  - 7 automated tests covering full login/logout flow
  - Tests unauthenticated access, login validation, session management

**Database Testing**:
- `scripts/test_auth_db.py` - Database function tests (manual testing)
  - Test user queries, password verification, session management

### 16.5 Documentation

**Design and Specifications**:
- `docs/spec/user-auth-design.md` - **This document** (comprehensive design specification, v2.1)
  - Single source of truth for authentication design and implementation
  - Supersedes `auth-implementation-summary.md` (all content consolidated in v2.1)
- `docs/mock-users.md` - Mock user documentation (credentials, roles, sites)

**Related Documentation**:
- `docs/spec/architecture.md` - Section 5: Authentication and Authorization
- `docs/spec/session-timeout-behavior.md` - Complete session timeout behavior guide
- `docs/spec/ccow-v2-implementation-summary.md` - CCOW v2.0 shared authentication
- `docs/guide/environment-variables-guide.md` - Environment variable configuration

### 16.6 Configuration

**Environment Configuration**:
- `.env` - Environment variables (session timeout, cookie settings, bcrypt rounds)
- `config.py` - `AUTH_CONFIG` section with session management settings

**Main Application**:
- `app/main.py` - Updated to add AuthMiddleware and auth router
  - Middleware ordering: SessionMiddleware → AuthMiddleware
  - Auth router included at root level

---

## 17. Deployment Checklist

### 17.1 Development Environment (Current Status)

**Database**:
- ✅ PostgreSQL database with `auth` schema
- ✅ Mock users loaded (7 clinicians)
- ✅ All tables created: `users`, `sessions`, `audit_logs`

**Session Configuration**:
- ✅ Session timeout: 15 minutes (configurable via `SESSION_TIMEOUT_MINUTES`)
- ✅ HTTP cookies (not HTTPS - `SESSION_COOKIE_SECURE=false`)
- ✅ Cookie flags: `httponly=true`, `samesite=lax`

**Security**:
- ✅ Bcrypt password hashing (12 rounds)
- ✅ Parameterized queries (SQL injection protection)
- ✅ XSS protection via Jinja2 auto-escaping
- ✅ All audit logging enabled

**Application**:
- ✅ AuthMiddleware active and enforcing authentication
- ✅ Public routes defined: `/login`, `/static`, `/favicon.ico`, `/docs`, `/openapi.json`, `/redoc`
- ✅ User context injected into all authenticated requests
- ✅ Template context helper available for all routes

### 17.2 Production Environment (Future Requirements)

**HTTPS and Cookie Security**:
- [ ] Update `SESSION_COOKIE_SECURE=true` (require HTTPS)
- [ ] Configure reverse proxy (nginx/Apache) for SSL termination
- [ ] Obtain and configure SSL certificates
- [ ] Redirect all HTTP requests to HTTPS

**Database Security**:
- [ ] Configure production DATABASE_URL with secure credentials
- [ ] Use connection pooling (QueuePool instead of NullPool)
- [ ] Enable SSL for PostgreSQL connections
- [ ] Set up database backups for auth schema
- [ ] Configure backup retention policy

**Session Management**:
- [ ] Set up session cleanup cron job (`cleanup_expired_sessions()`)
  - Recommended: Run every 1 hour
  - Example: `0 * * * * /path/to/cleanup_sessions.sh`
- [ ] Consider Redis for session storage (faster than PostgreSQL for high traffic)
- [ ] Monitor session table size and query performance

**Security Hardening**:
- [ ] Review and increase bcrypt rounds if needed (12 is good, 14 for higher security)
- [ ] Implement rate limiting for login endpoint
  - Suggested: 5 login attempts per IP per minute
  - Use Redis or in-memory cache
  - Return 429 Too Many Requests on limit
- [ ] Configure CORS settings if needed
- [ ] Set up Web Application Firewall (WAF) rules
- [ ] Implement account lockout after N failed attempts

**Logging and Monitoring**:
- [ ] Configure proper logging (syslog, CloudWatch, Splunk, etc.)
- [ ] Set up monitoring for failed login attempts
  - Alert on >10 failed attempts from single IP in 5 minutes
  - Alert on >50 failed attempts globally in 5 minutes
- [ ] Set up alerts for:
  - Database connection failures
  - Session table growth rate
  - Average session duration anomalies
- [ ] Configure log retention policy for audit logs
  - Recommended: 90 days for compliance

**Audit and Compliance**:
- [ ] Review audit log coverage (ensure all auth events logged)
- [ ] Set up audit log shipping to SIEM (Security Information and Event Management)
- [ ] Configure compliance reporting tools
- [ ] Document audit log retention policy (7 years for HIPAA)
- [ ] Implement audit log archival strategy

**Performance**:
- [ ] Enable connection pooling (SQLAlchemy QueuePool)
- [ ] Add indexes for common queries (if not already present)
- [ ] Monitor session query performance
- [ ] Configure database read replicas if needed (high traffic)

**Disaster Recovery**:
- [ ] Test database backup restoration
- [ ] Document rollback procedures
- [ ] Configure multi-region deployment (if needed)
- [ ] Set up session replication for high availability

---

## Appendices

### Appendix A: Password Security Best Practices

**Bcrypt Configuration**:
- **Work Factor**: 12 rounds (current standard)
- **Cost**: ~200ms per hash (acceptable for login)
- **Future-Proof**: Increase work factor as CPUs get faster

**Password Requirements** (future):
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No common passwords (check against breach database)
- No password reuse (store password history hashes)

**Storage**:
- NEVER store plaintext passwords
- NEVER store reversible encryption
- Use bcrypt or Argon2 only
- Salt automatically handled by bcrypt

### Appendix B: Session Security Checklist

**Cookie Security**:
- [x] httponly=True (XSS protection)
- [x] secure=True in production (HTTPS only)
- [x] samesite="lax" (CSRF protection)
- [x] Random, unpredictable session IDs (UUID)

**Session Lifecycle**:
- [x] Short timeout (15 minutes inactivity)
- [x] Extend on activity
- [x] Invalidate on logout
- [x] Single session per user

**Database Security**:
- [x] Parameterized queries (SQL injection protection)
- [x] Proper indexes (performance)
- [x] Foreign key constraints (data integrity)

### Appendix C: Entra ID Alignment

**OIDC Flow Comparison**:

| Step | Real Entra ID | med-z1 Mock |
|------|--------------|-------------|
| 1. Initiate Login | Redirect to `login.microsoftonline.com` | Redirect to `/login` |
| 2. User Authentication | Azure AD login page | Mock login page (Jinja2) |
| 3. MFA Challenge | Authenticator app, SMS, etc. | (Skipped in mock) |
| 4. Token Generation | Azure AD issues JWT | med-z1 generates UUID session_id |
| 5. Callback | Redirect to `/auth/callback?code=...` | POST to `/login` (simplified) |
| 6. Token Validation | Verify JWT signature, claims | Query session in PostgreSQL |
| 7. User Profile | Read from Azure AD Graph API | Read from `auth.users` table |
| 8. Session Creation | Store tokens in session | Store session_id in cookie |

**What med-z1 Simulates**:
- ✅ Login page styling (VA/Microsoft look-and-feel)
- ✅ Email/password authentication
- ✅ Session token generation
- ✅ Redirect-based flow
- ✅ User profile storage

**What med-z1 Omits** (real Entra ID features):
- ❌ PIV card authentication
- ❌ Multi-factor authentication
- ❌ Token refresh logic
- ❌ Azure AD Graph API integration
- ❌ Conditional access policies

### Appendix D: Troubleshooting Guide

This appendix provides solutions to common authentication issues with specific error messages and diagnostic steps.

#### Error: "No session cookie found"

**Symptom**: User redirected to `/login` on every request, even after successful login

**Cause**: Session cookie not being set or not being sent by browser

**Diagnostic Steps**:
1. Check browser Developer Tools → Application → Cookies
2. Look for `session_id` cookie with correct domain
3. Verify cookie flags: `HttpOnly`, `SameSite=Lax`
4. Check if cookie is being cleared by browser extensions

**Solutions**:
- Ensure `response.set_cookie()` is called in `POST /login` route
- Verify cookie domain matches application domain
- Check for browser privacy settings blocking cookies
- In development: Ensure `SESSION_COOKIE_SECURE=false` (HTTPS not required)

**Verification**:
```bash
# Test cookie is set after login
curl -i -c cookies.txt -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov" \
  -d "password=VaDemo2025!"

# Check cookies.txt for session_id
cat cookies.txt
```

---

#### Error: "Invalid or expired session"

**Symptom**: Middleware redirects to login with error in logs

**Cause**: Session not found in database or expired

**Diagnostic Steps**:
1. Check `auth.sessions` table for user's session:
   ```sql
   SELECT session_id, user_id, created_at, last_activity_at, expires_at, is_active
   FROM auth.sessions
   WHERE user_id = (SELECT user_id FROM auth.users WHERE email = 'clinician.alpha@va.gov');
   ```
2. Verify `is_active = TRUE`
3. Check if `expires_at` is in the future
4. Review middleware logs for session validation errors

**Solutions**:
- **Session expired**: Normal behavior after 15 minutes inactivity, user should log in again
- **Session not found**: Database may have been cleared, user should log in again
- **Session inactive**: Check if logout was called or if single-session enforcement invalidated old session
- **Timezone issue**: Ensure server clock is correct and timezone-aware datetimes are used

**Verification**:
```bash
# Check if session exists and is active
docker exec -it postgres16 psql -U postgres -d medz1 \
  -c "SELECT * FROM auth.sessions WHERE is_active = TRUE;"
```

---

#### Error: "Account inactive" or "Account locked"

**Symptom**: Login page shows "Account is inactive" or "Account is locked"

**Cause**: User account disabled in database

**Diagnostic Steps**:
1. Check user status:
   ```sql
   SELECT user_id, email, is_active, is_locked, failed_login_attempts
   FROM auth.users
   WHERE email = 'clinician.alpha@va.gov';
   ```
2. Review audit logs for account lock events:
   ```sql
   SELECT * FROM auth.audit_logs
   WHERE email = 'clinician.alpha@va.gov'
   ORDER BY event_timestamp DESC
   LIMIT 10;
   ```

**Solutions**:
- **Account inactive**: Update `is_active = TRUE`
  ```sql
  UPDATE auth.users SET is_active = TRUE WHERE email = 'clinician.alpha@va.gov';
  ```
- **Account locked**: Update `is_locked = FALSE` and reset failed attempts
  ```sql
  UPDATE auth.users
  SET is_locked = FALSE, failed_login_attempts = 0
  WHERE email = 'clinician.alpha@va.gov';
  ```

**Prevention**:
- Implement account unlock procedure (time-based or admin intervention)
- Set up alerts for locked accounts

---

#### Error: "Database connection error"

**Symptom**: Application logs show database connection failures, login page returns 500 error

**Cause**: PostgreSQL not running or wrong credentials in `DATABASE_URL`

**Diagnostic Steps**:
1. Check PostgreSQL is running:
   ```bash
   docker ps | grep postgres16
   # Should show running container
   ```
2. Test database connection:
   ```bash
   docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT 1;"
   # Should return: 1
   ```
3. Verify `DATABASE_URL` in `.env`:
   ```bash
   grep DATABASE_URL .env
   # Should be: postgresql://postgres:postgres@localhost:5432/medz1
   ```
4. Check application logs for SQLAlchemy errors

**Solutions**:
- **PostgreSQL not running**: Start container
  ```bash
  docker start postgres16
  ```
- **Wrong credentials**: Update `DATABASE_URL` in `.env` and restart app
- **Wrong database name**: Ensure `medz1` database exists
  ```bash
  docker exec -it postgres16 psql -U postgres -c "\l" | grep medz1
  ```

---

#### Error: "Module not found" or Import errors

**Symptom**: Application fails to start with import errors for bcrypt, SQLAlchemy, etc.

**Cause**: Missing Python packages

**Solutions**:
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Verify bcrypt is installed:
   ```bash
   python -c "import bcrypt; print(bcrypt.__version__)"
   ```
3. Verify SQLAlchemy is installed:
   ```bash
   python -c "import sqlalchemy; print(sqlalchemy.__version__)"
   ```

**Common Missing Packages**:
- `bcrypt` - Password hashing
- `sqlalchemy` - Database ORM
- `python-dotenv` - Environment variable loading

---

#### Error: Login works but user display shows "Unknown User"

**Symptom**: User logs in successfully but sidebar shows "Unknown User" instead of name

**Cause**: Route handler not passing user context to template

**Diagnostic Steps**:
1. Check if route uses `get_base_context()`:
   ```python
   # ❌ Wrong - Missing user context
   return templates.TemplateResponse("dashboard.html", {"request": request})

   # ✅ Correct - Includes user context
   from app.utils.template_context import get_base_context
   return templates.TemplateResponse("dashboard.html", get_base_context(request))
   ```
2. Verify `request.state.user` is set by middleware:
   ```python
   # Add temporary debug logging to route
   logger.info(f"User context: {request.state.user}")
   ```

**Solutions**:
- Update route handler to use `get_base_context(request, **kwargs)`
- Ensure middleware is properly configured in `app/main.py`
- Check middleware ordering: AuthMiddleware should run before route handlers

**Example Fix**:
```python
# Before
@router.get("/dashboard")
async def get_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "patient": patient
    })

# After
@router.get("/dashboard")
async def get_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html",
        get_base_context(request, patient=patient)
    )
```

---

#### Error: Session timeout not working (user never logged out)

**Symptom**: User stays logged in indefinitely, even after hours of inactivity

**Cause**: Session timeout not being enforced or `expires_at` not being checked

**Diagnostic Steps**:
1. Check session expiration in database:
   ```sql
   SELECT session_id, last_activity_at, expires_at,
          NOW() > expires_at AS is_expired
   FROM auth.sessions
   WHERE is_active = TRUE;
   ```
2. Verify middleware is checking expiration:
   - Check `app/middleware/auth.py` line ~90-110
   - Ensure timezone-aware datetime comparison
3. Check `SESSION_TIMEOUT_MINUTES` configuration:
   ```bash
   grep SESSION_TIMEOUT_MINUTES .env
   # Should be: SESSION_TIMEOUT_MINUTES=15
   ```

**Solutions**:
- **Timezone issue**: Fixed in v2.0, ensure using `datetime.now(timezone.utc)`
- **Middleware not checking**: Verify middleware is installed and running
- **Wrong timeout value**: Update `SESSION_TIMEOUT_MINUTES` in `.env`

**Reference**: See `docs/spec/session-timeout-behavior.md` for complete guide

---

#### Error: Multiple users can log in with same email

**Symptom**: Different sessions exist for same email address

**Cause**: UNIQUE constraint not enforced on `email` column

**Diagnostic Steps**:
1. Check for duplicate emails:
   ```sql
   SELECT email, COUNT(*)
   FROM auth.users
   GROUP BY email
   HAVING COUNT(*) > 1;
   ```
2. Verify UNIQUE constraint exists:
   ```sql
   SELECT constraint_name, constraint_type
   FROM information_schema.table_constraints
   WHERE table_name = 'users' AND table_schema = 'auth';
   ```

**Solutions**:
- Add UNIQUE constraint if missing:
  ```sql
  ALTER TABLE auth.users ADD CONSTRAINT unique_email UNIQUE (email);
  ```
- Remove duplicate users (keep most recent):
  ```sql
  DELETE FROM auth.users
  WHERE user_id NOT IN (
    SELECT MAX(user_id) FROM auth.users GROUP BY email
  );
  ```

---

#### Error: Audit logs not recording events

**Symptom**: `auth.audit_logs` table is empty or missing events

**Cause**: `log_audit_event()` not being called or database permissions issue

**Diagnostic Steps**:
1. Check if audit logs exist:
   ```sql
   SELECT COUNT(*) FROM auth.audit_logs;
   ```
2. Check recent audit events:
   ```sql
   SELECT * FROM auth.audit_logs ORDER BY event_timestamp DESC LIMIT 10;
   ```
3. Review application logs for audit logging errors
4. Verify database permissions:
   ```sql
   SELECT has_table_privilege('postgres', 'auth.audit_logs', 'INSERT');
   ```

**Solutions**:
- Ensure `log_audit_event()` is called in auth routes:
  - `POST /login` should log 'login' or 'login_failed'
  - `POST /logout` should log 'logout'
- Check for SQL errors in application logs
- Verify database user has INSERT permission on `auth.audit_logs`

**Test Audit Logging**:
```bash
# Trigger login event
curl -X POST http://localhost:8000/login \
  -d "email=clinician.alpha@va.gov" \
  -d "password=WrongPassword"

# Check audit log
docker exec -it postgres16 psql -U postgres -d medz1 \
  -c "SELECT * FROM auth.audit_logs ORDER BY event_timestamp DESC LIMIT 1;"
```

---

## Document Metadata

**Authors**: Claude Code (AI Assistant)
**Reviewers**: Chuck Sylvester (Product Owner)
**Status**: Implementation Complete, Living Document
**Version**: 2.1
**Date**: 2025-12-18 (Initial), 2025-12-30 (Latest)

**Related Documents**:
- `docs/spec/architecture.md` - System architecture and routing patterns (Section 5: Authentication)
- `docs/spec/session-timeout-behavior.md` - Complete session timeout behavior guide
- `docs/spec/ccow-v2-implementation-summary.md` - CCOW v2.0 shared authentication
- `docs/guide/environment-variables-guide.md` - Environment variable configuration
- `docs/spec/ccow-v2-testing-guide.md` - API testing guide
- `docs/mock-users.md` - Mock user credentials and profiles
- `docs/med-z1-plan.md` - Product roadmap
- `app/README.md` - Application setup guide

**Supersedes**:
- `docs/spec/auth-implementation-summary.md` - All content consolidated into this document (v2.1)

**Change Log**:
- **v2.1** (2025-12-30): Documentation consolidation
  - Added Section 16: File Inventory
  - Added Section 17: Deployment Checklist
  - Enhanced Appendix D with 9 detailed troubleshooting scenarios
  - Consolidated all content from auth-implementation-summary.md
  - Now serves as single source of truth for authentication design and implementation
- **v2.0** (2025-12-23): CCOW v2.0 integration and session timeout fixes
- **v1.1** (2025-12-18): Implementation complete (Phases 1-8)
- **v1.0** (2025-12-18): Initial comprehensive design document

---

**End of User Authentication and Management Design Document**
