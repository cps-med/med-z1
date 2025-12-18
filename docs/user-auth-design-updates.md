# User Authentication Design Updates

**Date**: 2025-12-18
**Version**: v1.1
**Changes**: Updated file locations and organizational strategy

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

**Document Version History:**
- v1.0 (2025-12-17): Initial design with `mock/users/` approach
- v1.1 (2025-12-18): Updated to `db/seeds/` approach for semantic correctness
