-- =====================================================
-- Mock User Data for med-z1 Authentication
-- =====================================================
-- Password for all users: VaDemo2025!
-- Bcrypt rounds: 12
-- Generated hash: $2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2
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
-- User 1: Dr. Alice Anderson, MD
(
    'clinician.alpha@va.gov',
    '$2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2',  -- VaDemo2025!
    'Dr. Alice Anderson, MD',
    'Alice',
    'Anderson',
    508,
    TRUE,
    'mock_data_script'
),

-- User 2: Dr. Bob Brown, DO
(
    'clinician.bravo@va.gov',
    '$2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2',  -- VaDemo2025!
    'Dr. Bob Brown, DO',
    'Bob',
    'Brown',
    648,
    TRUE,
    'mock_data_script'
),

-- User 3: Nurse Carol Chen, RN
(
    'clinician.charlie@va.gov',
    '$2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2',  -- VaDemo2025!
    'Nurse Carol Chen, RN',
    'Carol',
    'Chen',
    663,
    TRUE,
    'mock_data_script'
),

-- User 4: Dr. David Davis, MD
(
    'clinician.delta@va.gov',
    '$2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2',  -- VaDemo2025!
    'Dr. David Davis, MD',
    'David',
    'Davis',
    509,
    TRUE,
    'mock_data_script'
),

-- User 5: Pharmacist Emma Evans, PharmD
(
    'clinician.echo@va.gov',
    '$2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2',  -- VaDemo2025!
    'Pharmacist Emma Evans, PharmD',
    'Emma',
    'Evans',
    531,
    TRUE,
    'mock_data_script'
),

-- User 6: Dr. Frank Foster, MD
(
    'clinician.foxtrot@va.gov',
    '$2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2',  -- VaDemo2025!
    'Dr. Frank Foster, MD',
    'Frank',
    'Foster',
    516,
    TRUE,
    'mock_data_script'
),

-- User 7: Dr. Grace Green, MD
(
    'clinician.golf@va.gov',
    '$2b$12$ismpK2xjpSpnrZFVDMKZQ.R6gyAN684O/dNfEZoxzwDKKPXOG13T2',  -- VaDemo2025!
    'Dr. Grace Green, MD',
    'Grace',
    'Green',
    552,
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

-- =====================================================
-- Copy the above SQL and save to:
--   db/seeds/auth_users.sql
-- =====================================================
