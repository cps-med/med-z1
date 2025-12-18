# PostgreSQL Schema Guidance for med-z1

**Document Version**: v1.0
**Last Updated**: 2025-12-18
**Purpose**: Explain PostgreSQL schema concept and provide recommendations for med-z1 serving database organization

---

## 1. What is a PostgreSQL Schema?

A **schema** in PostgreSQL is a **namespace** that contains database objects (tables, views, indexes, functions, etc.). Think of it as a **folder** or **logical grouping** within a database.

### 1.1 Basic Concept

```
Database: medz1
  ├── Schema: public (default)
  │   ├── Table: patient_demographics
  │   ├── Table: patient_vitals
  │   └── Table: patient_encounters
  │
  ├── Schema: auth
  │   ├── Table: users
  │   ├── Table: sessions
  │   └── Table: audit_logs
  │
  └── Schema: clinical (proposed)
      ├── Table: demographics
      ├── Table: vitals
      └── Table: encounters
```

### 1.2 The Default "public" Schema

**Important**: When you create tables in PostgreSQL without specifying a schema, they go into the **`public`** schema by default.

Your current tables (created without schema prefix):
```sql
CREATE TABLE patient_demographics (...);  -- Actually creates: public.patient_demographics
CREATE TABLE patient_vitals (...);        -- Actually creates: public.patient_vitals
```

These are **already in a schema** - the `public` schema! You've been using schemas all along without realizing it.

### 1.3 Schema vs Database vs Table

| Concept      | Analogy           | Purpose                                  | Example                |
|--------------|-------------------|------------------------------------------|------------------------|
| **Database** | File cabinet      | Highest level container                  | `medz1`                |
| **Schema**   | Drawer/folder     | Logical grouping of related objects      | `auth`, `clinical`     |
| **Table**    | File              | Actual data storage                      | `users`, `vitals`      |

**Full qualified name**: `database.schema.table`
- Example: `medz1.auth.users`
- Example: `medz1.public.patient_demographics`

---

## 2. Why Use Schemas?

### 2.1 Benefits

**1. Logical Organization** (Domain Separation)
```
auth schema        → Authentication, sessions, audit logs
clinical schema    → Patient data, clinical observations
admin schema       → System configuration, feature flags
```

**2. Namespace Isolation** (Prevent Naming Conflicts)
```sql
-- Without schemas (naming conflict):
CREATE TABLE users;           -- Which users? Auth users or patient users?
CREATE TABLE clinical_users;  -- Have to use prefixes everywhere

-- With schemas (clear separation):
CREATE TABLE auth.users;      -- Authentication users
CREATE TABLE clinical.users;  -- Clinical staff registry
```

**3. Permission Management** (Grant/Revoke at Schema Level)
```sql
-- Grant all permissions on auth schema to app user
GRANT ALL ON SCHEMA auth TO med_z1_user;
GRANT ALL ON ALL TABLES IN SCHEMA auth TO med_z1_user;

-- Read-only access to clinical data for reporting user
GRANT USAGE ON SCHEMA clinical TO reporting_user;
GRANT SELECT ON ALL TABLES IN SCHEMA clinical TO reporting_user;
```

**4. Backup/Restore Flexibility**
```bash
# Backup only auth schema (users, sessions, audit logs)
pg_dump -n auth medz1 > auth_backup.sql

# Backup only clinical schema (patient data)
pg_dump -n clinical medz1 > clinical_backup.sql
```

**5. Multi-Tenancy / Modularity**
```
auth schema      → User management module (independent)
clinical schema  → Clinical data module (can be deployed separately)
ai schema        → AI/ML models and embeddings (future)
```

### 2.2 When Schemas Are Most Valuable

✅ **High Value** (Recommended Use Cases):
- **Functional boundaries**: Authentication vs clinical data vs AI/ML
- **Security boundaries**: Different access control requirements
- **Lifecycle boundaries**: Auth tables rarely change, clinical tables evolve frequently
- **Deployment boundaries**: Components that might be deployed/updated independently

⚠️ **Low Value** (Avoid Overuse):
- Grouping by domain when all tables have same permissions
- Creating schemas for every clinical domain (demographics, vitals, labs, etc.)
- Using schemas as a substitute for proper naming conventions

---

## 3. Current med-z1 Database Structure

### 3.1 What You Have Now (Implicit `public` Schema)

```sql
-- All tables currently in public schema (default)
public.patient_demographics
public.patient_vitals
public.patient_flags
public.patient_allergies
public.patient_medications
public.patient_encounters
public.patient_labs
```

**Access Pattern**:
```sql
-- Both work identically:
SELECT * FROM patient_demographics;
SELECT * FROM public.patient_demographics;
```

**Search Path** (determines which schema PostgreSQL searches by default):
```sql
SHOW search_path;
-- Result: "$user", public
-- Meaning: PostgreSQL looks in public schema by default
```

### 3.2 What user-auth-design Proposes

```sql
-- New auth schema (explicitly created)
auth.users
auth.sessions
auth.audit_logs
```

**Why a separate schema for auth?**
- **Different lifecycle**: Auth tables are infrastructure, clinical tables are domain data
- **Different permissions**: Auth tables need tighter access control
- **Different backup cadence**: Auth tables backed up more frequently (audit compliance)
- **Logical separation**: Authentication is a distinct subsystem

---

## 4. Recommendations for med-z1

### 4.1 Recommended Approach: Hybrid Strategy

**Use schemas for MAJOR SUBSYSTEMS, not individual domains.**

```
medz1 database
  │
  ├── public schema           (keep current clinical tables here)
  │   ├── patient_demographics
  │   ├── patient_vitals
  │   ├── patient_flags
  │   ├── patient_allergies
  │   ├── patient_medications
  │   ├── patient_encounters
  │   └── patient_labs
  │
  ├── auth schema             (user authentication and authorization)
  │   ├── users
  │   ├── sessions
  │   └── audit_logs
  │
  ├── ai schema (future)      (AI/ML models, embeddings, RAG)
  │   ├── patient_embeddings
  │   ├── chart_summaries
  │   └── ddi_cache
  │
  └── admin schema (future)   (system configuration, feature flags)
      ├── feature_flags
      ├── system_settings
      └── user_preferences
```

### 4.2 Why NOT Create Schemas for Each Clinical Domain?

**Don't do this** (over-engineering):
```
clinical.demographics      ❌ Too granular
clinical.vitals            ❌ Too granular
clinical.labs              ❌ Too granular
clinical.encounters        ❌ Too granular
```

**Reasons**:
1. **Same permissions**: All clinical tables have same access control (read/write for app user)
2. **Same lifecycle**: All clinical tables evolve together with UI features
3. **Same backup policy**: All clinical data backed up together
4. **Same deployment**: Clinical tables deployed as a unit
5. **Query complexity**: Makes queries harder to write and maintain
   ```sql
   -- With excessive schemas:
   SELECT d.name_display, v.result_value
   FROM demographics.patient_demographics d
   JOIN vitals.patient_vitals v ON d.icn = v.patient_key;  -- Verbose, annoying

   -- With all in public schema:
   SELECT d.name_display, v.result_value
   FROM patient_demographics d
   JOIN patient_vitals v ON d.icn = v.patient_key;  -- Clean, simple
   ```

### 4.3 Should You Move Existing Tables into a Schema?

**Recommendation: NO - Keep them in `public` schema.**

**Rationale**:
1. ✅ **No functional problem**: `public` schema works perfectly for clinical tables
2. ✅ **Avoids breaking changes**: All existing queries/code continue to work
3. ✅ **Simplifies queries**: Default search path includes `public`
4. ✅ **Follows PostgreSQL convention**: Public schema is the standard location for application tables
5. ✅ **Reduces cognitive load**: Developers don't need to remember which schema

**When to reconsider**:
- If you need different permissions for different table groups
- If you implement multi-tenancy (different customers/sites)
- If clinical data grows to need independent backup/restore

### 4.4 Naming Convention Recommendation

**Keep your current naming pattern for clinical tables** (table name includes domain):

```sql
-- Current pattern (RECOMMENDED - keep this):
patient_demographics  ✅ Clear, self-documenting
patient_vitals        ✅ Clear, self-documenting
patient_encounters    ✅ Clear, self-documenting

-- Don't change to schema-based organization:
clinical.demographics  ❌ Not needed, adds complexity
clinical.vitals        ❌ Not needed, adds complexity
```

**Why this works**:
- Table names are self-documenting (`patient_vitals` clearly indicates domain)
- No need for additional schema layer when naming convention is clear
- Easier to search, autocomplete, and reference in code

---

## 5. Schema Implementation for user-auth

### 5.1 How user-auth Will Use `auth` Schema

**Create schema**:
```sql
CREATE SCHEMA IF NOT EXISTS auth;
```

**Create tables with schema prefix**:
```sql
CREATE TABLE auth.users (...);
CREATE TABLE auth.sessions (...);
CREATE TABLE auth.audit_logs (...);
```

**Query with full qualification**:
```sql
-- Must specify schema (auth is not in default search_path):
SELECT * FROM auth.users WHERE email = 'clinician.alpha@va.gov';

-- Or add auth to search path:
SET search_path TO public, auth;
SELECT * FROM users;  -- Now finds auth.users
```

### 5.2 Python/SQLAlchemy Code Implications

**Database functions** (in `app/db/auth.py`):
```python
# Must specify schema in SQL queries:
query = text("""
    SELECT user_id, email, password_hash, display_name, is_active
    FROM auth.users
    WHERE email = :email
    LIMIT 1
""")
```

**SQLAlchemy models** (if using ORM in future):
```python
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}  # Specify schema here

    user_id = Column(UUID, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    # ...
```

### 5.3 Schema Permissions

**Grant usage on schema** (required before accessing tables):
```sql
GRANT USAGE ON SCHEMA auth TO med_z1_user;
```

**Grant table permissions**:
```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.users TO med_z1_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.sessions TO med_z1_user;
GRANT SELECT, INSERT ON auth.audit_logs TO med_z1_user;  -- Read + append only
```

**Why clinical tables don't need explicit schema grants**:
```sql
-- public schema has USAGE granted to PUBLIC role by default:
-- No need to run: GRANT USAGE ON SCHEMA public TO med_z1_user;

-- Just grant table permissions:
GRANT SELECT, INSERT, UPDATE, DELETE ON patient_demographics TO med_z1_user;
```

---

## 6. Common Schema Patterns

### 6.1 Search Path Configuration

**Default search path**:
```sql
SHOW search_path;
-- Result: "$user", public
```

**Add auth schema to search path** (so you can omit `auth.` prefix):
```sql
-- Per session:
SET search_path TO public, auth;

-- Per user (persistent):
ALTER ROLE med_z1_user SET search_path TO public, auth;

-- Per database (global):
ALTER DATABASE medz1 SET search_path TO public, auth;
```

**Recommendation for med-z1**: Keep default search path, always qualify `auth.` tables explicitly.
- **Why**: Makes it crystal clear when you're accessing auth tables vs clinical tables
- **Example**: `SELECT * FROM auth.users` (explicit) vs `SELECT * FROM users` (ambiguous)

### 6.2 Cross-Schema Joins

**Joining tables from different schemas**:
```sql
-- Join clinical table (public schema) with auth table (auth schema):
SELECT
    d.name_display,
    u.email,
    u.home_site_sta3n
FROM patient_demographics d
JOIN auth.users u ON d.primary_station = CAST(u.home_site_sta3n AS VARCHAR);
```

**Note**: Works seamlessly - schemas don't create barriers, just namespaces.

### 6.3 Schema Information Queries

**List all schemas in database**:
```sql
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT LIKE 'pg_%'
  AND schema_name != 'information_schema';
-- Result: public, auth
```

**List all tables in auth schema**:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'auth';
-- Result: users, sessions, audit_logs
```

**List all tables in public schema**:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
-- Result: patient_demographics, patient_vitals, patient_flags, ...
```

---

## 7. Decision Summary for med-z1

### 7.1 Schema Strategy

| Schema     | Purpose                          | Tables                                               | Rationale                              |
|------------|----------------------------------|------------------------------------------------------|----------------------------------------|
| `public`   | Clinical patient data            | patient_demographics, patient_vitals, patient_flags, patient_allergies, patient_medications, patient_encounters, patient_labs | Default location, simple queries       |
| `auth`     | User authentication/authorization| users, sessions, audit_logs                          | Separate subsystem, different permissions |
| `ai`       | AI/ML models and embeddings      | (future: patient_embeddings, chart_summaries)        | Separate subsystem, optional feature   |
| `admin`    | System configuration             | (future: feature_flags, system_settings)             | Operational data, different lifecycle  |

### 7.2 Why This Approach Works

✅ **Simplicity**: Clinical tables stay in public schema (no migration needed)
✅ **Separation**: Auth/AI/Admin are truly separate subsystems
✅ **Flexibility**: Easy to add new clinical tables without schema decisions
✅ **Clarity**: Schema usage signals "this is a different subsystem"
✅ **Performance**: No impact - schemas are just namespaces
✅ **Maintainability**: Matches PostgreSQL community best practices

### 7.3 What NOT to Do

❌ **Don't** create schemas for each clinical domain (vitals, labs, encounters)
❌ **Don't** move existing tables from public to a new schema without clear benefit
❌ **Don't** use schemas to replace proper table naming conventions
❌ **Don't** add schemas to search_path indiscriminately (keep queries explicit)

---

## 8. Implementation Checklist

When implementing the auth schema (per user-auth-design.md):

- [ ] Create `auth` schema in PostgreSQL
- [ ] Create `auth.users`, `auth.sessions`, `auth.audit_logs` tables
- [ ] Grant `USAGE` on `auth` schema to `med_z1_user`
- [ ] Grant table permissions on auth tables
- [ ] Update `app/db/auth.py` queries to use `auth.` prefix
- [ ] Leave clinical tables in `public` schema (no changes needed)
- [ ] Document schema usage in README files

---

## 9. Further Reading

**PostgreSQL Documentation**:
- [Schemas](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Schema Search Path](https://www.postgresql.org/docs/current/ddl-schemas.html#DDL-SCHEMAS-PATH)
- [Privileges](https://www.postgresql.org/docs/current/ddl-priv.html)

**Best Practices**:
- Use schemas for major subsystems, not fine-grained organization
- Keep clinical domain tables in `public` schema with clear naming
- Use explicit schema qualification in queries (avoid search_path complexity)
- Grant permissions at schema level when appropriate

---

## Appendix: Quick Reference

### Common Schema Commands

```sql
-- Create schema
CREATE SCHEMA auth;

-- Create table in specific schema
CREATE TABLE auth.users (...);

-- Drop schema (cascade removes all objects)
DROP SCHEMA auth CASCADE;

-- List tables in schema
\dt auth.*

-- Show search path
SHOW search_path;

-- Set search path
SET search_path TO public, auth;

-- Grant schema usage
GRANT USAGE ON SCHEMA auth TO med_z1_user;

-- Grant all permissions on all tables in schema
GRANT ALL ON ALL TABLES IN SCHEMA auth TO med_z1_user;

-- Query across schemas
SELECT * FROM public.patient_demographics d
JOIN auth.users u ON d.primary_station = CAST(u.home_site_sta3n AS VARCHAR);
```
