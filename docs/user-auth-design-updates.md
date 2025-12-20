# User Authentication Design Updates

**Date**: 2025-12-20
**Version**: v1.2
**Changes**: Added session timeout timezone fix and CCOW v2.0 integration updates

---

## Summary of Changes

The user-auth-design.md document has been updated to use the `db/seeds/` approach for mock user data instead of `mock/users/`. This change better aligns with the semantic purpose of each subsystem in the med-z1 project.

## File Location Changes

### Before (v1.0):
```
mock/
  users/
    MOCK_USER_CREDENTIALS.md    # Credentials documentation
    insert_mock_users.sql       # SQL insert script
```

### After (v1.1):
```
db/
  seeds/
    auth_users.sql              # SQL insert script

docs/
  mock-users.md                 # Credentials documentation

scripts/
  generate_password_hash.py     # Hash generation utility
```

## Rationale

### Why `db/seeds/` Instead of `mock/`?

**Auth users are application infrastructure, not clinical source data:**

1. **No ETL transformation needed**
   - Mock CDW data goes through Bronze → Silver → Gold pipeline
   - Auth users are created directly in final PostgreSQL form
   - No transformation or harmonization required

2. **Different semantic purpose**
   - `mock/` = VA clinical data sources (CDWWork, CDWWork2, VistA)
   - `db/seeds/` = Application test data (users, configurations)

3. **Database-first pattern**
   - `db/ddl/` contains schema structure
   - `db/seeds/` contains test/development data content
   - Clean separation of concerns

4. **Lifecycle independence**
   - Clinical mock data evolves with VA CDW schema changes
   - Auth users evolve with application authentication requirements
   - Different update cadences, different purposes

## Updated Commands

### Creating Auth Schema:
```bash
# Updated command (correct container name)
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_auth_tables.sql
```

### Loading Mock Users:
```bash
# Old path
docker exec -i postgres16 psql -U postgres -d medz1 < mock/users/insert_mock_users.sql

# New path
docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql
```

### Generating Password Hashes:
```bash
# Script location unchanged
python scripts/generate_password_hash.py --generate-sql > db/seeds/auth_users.sql
```

### Viewing Credentials:
```bash
# Old location
cat mock/users/MOCK_USER_CREDENTIALS.md

# New location
cat docs/mock-users.md
```

## Sections Updated in user-auth-design.md

1. **Section 5.5** - Schema Creation Script (usage comment)
2. **Section 9.0** - NEW: Data Organization Strategy (added)
3. **Section 9.2** - SQL Insert Script file path
4. **Section 9.3** - Mock User Password Management (file paths)
5. **Section 9.4** - Password Hash Generation Script (output paths)
6. **Section 9.5** - Workflow: Adding New Mock Users (file paths)
7. **Section 13.1** - Implementation Roadmap Phase 2 (file paths)

## Docker Container Name

All references to `postgres` container have been updated to `postgres16` (the actual running container name in med-z1 environment).

## Next Steps

With the design document updated, implementation can proceed with Phase 2:

1. Create `db/seeds/` directory
2. Create `scripts/generate_password_hash.py` utility
3. Generate `db/seeds/auth_users.sql` with 5 mock users
4. Create `docs/mock-users.md` credential documentation
5. Load mock users into PostgreSQL

---

---

## v1.2 Updates (December 20, 2025)

### Session Timeout Timezone Fix

**Issue**: Session expiry validation was comparing timezone-naive `expires_at` (from PostgreSQL) with timezone-aware `now()` (UTC), causing comparison errors.

**Fix Location**: `ccow/auth_helper.py` line 112-115

**Solution**:
```python
# Use timezone-naive comparison if expires_at is timezone-naive
if expires_at.tzinfo is None:
    now = datetime.now()  # Local time, no timezone
else:
    now = datetime.now(timezone.utc)  # UTC time
```

**Impact**:
- CCOW Context Vault v2.0 session validation now works correctly
- Session timeout properly enforces 15-minute sliding window
- All manual and automated tests passing

### CCOW v2.0 Integration

**Integration Points**:
1. CCOW vault calls `ccow/auth_helper.py::get_user_from_session()` to validate sessions
2. Shares same `auth.sessions` and `auth.users` tables with med-z1 app
3. Same session validation logic (active, not expired, user active)
4. Session timeout extends on every authenticated request in both med-z1 app AND CCOW vault

**New Documentation**:
- `docs/session-timeout-behavior.md` - Complete session timeout behavior guide
- `docs/environment-variables-guide.md` - Environment variable configuration
- `docs/ccow-v2-implementation-summary.md` - CCOW v2.0 completion summary
- `docs/ccow-v2-testing-guide.md` - API testing guide for curl/Insomnia

### Configuration Updates

**New Environment Variables** (added to `.env`):
```bash
# Session timeout configuration
SESSION_TIMEOUT_MINUTES=15
SESSION_COOKIE_NAME=session_id
SESSION_COOKIE_SECURE=false        # true in production
SESSION_COOKIE_HTTPONLY=true       # XSS protection
SESSION_COOKIE_SAMESITE=lax        # CSRF protection
```

**See**: `docs/environment-variables-guide.md` for complete guide

---

**Document Version History:**
- v1.0 (2025-12-17): Initial design with `mock/users/` approach
- v1.1 (2025-12-18): Updated to `db/seeds/` approach for semantic correctness
- v1.2 (2025-12-20): Added session timeout timezone fix and CCOW v2.0 integration details
