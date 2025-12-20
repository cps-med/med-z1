# Environment Variables Guide

## Overview

This document explains which environment variables should be configured in `.env` and provides guidance on when to use environment variables vs. hard-coded defaults.

---

## Current .env Configuration

All variables in `.env` are loaded by `config.py` at application startup. The `.env` file is the **single source of truth** for environment-specific configuration.

---

## Variable Categories

### 1. Database Credentials (REQUIRED in .env)

**Why:** Passwords and connection strings vary by environment and should NEVER be committed to version control.

```bash
# CDWWork (Mock CDW)
CDWWORK_DB_PASSWORD="your-password"

# Extract Database
EXTRACT_DB_PASSWORD="your-password"

# PostgreSQL Serving Database
POSTGRES_PASSWORD="your-password"

# MinIO S3 Storage
MINIO_SECRET_KEY="your-secret-key"
```

**Best Practice:**
- ✅ Always in `.env`
- ✅ Never commit passwords to Git
- ✅ Use `.env.template` for structure (without actual secrets)

---

### 2. Authentication & Session Configuration (RECOMMENDED in .env)

**Why:** Session behavior varies between development and production, and should be easily configurable.

```bash
# Session timeout in minutes (default: 15)
SESSION_TIMEOUT_MINUTES=15

# Session cookie configuration
SESSION_COOKIE_NAME=session_id
SESSION_COOKIE_SECURE=false        # true in production (HTTPS only)
SESSION_COOKIE_HTTPONLY=true       # XSS protection
SESSION_COOKIE_SAMESITE=lax        # CSRF protection
```

**Development vs. Production:**

| Variable | Development | Production |
|----------|-------------|------------|
| `SESSION_TIMEOUT_MINUTES` | 15 (short, for testing) | 30-60 (longer) |
| `SESSION_COOKIE_SECURE` | false (HTTP allowed) | true (HTTPS only) |
| `SESSION_COOKIE_HTTPONLY` | true | true |
| `SESSION_COOKIE_SAMESITE` | lax | strict or lax |

**Security Notes:**
- `SESSION_COOKIE_SECURE=true` prevents cookies from being sent over HTTP (production only)
- `SESSION_COOKIE_HTTPONLY=true` prevents JavaScript from accessing cookies (XSS protection)
- `SESSION_COOKIE_SAMESITE=lax` prevents CSRF attacks (blocks cross-site POST requests)

---

### 3. Service URLs & Ports (RECOMMENDED in .env)

**Why:** Service endpoints vary between local development, staging, and production.

```bash
# CCOW Context Vault
CCOW_ENABLED=true
CCOW_URL=http://localhost:8001
CCOW_VAULT_PORT=8001

# VistA RPC Broker Simulator
VISTA_ENABLED=true
VISTA_SERVICE_URL=http://localhost:8003
VISTA_TIMEOUT=30
```

**Environment-Specific Values:**

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| `CCOW_URL` | http://localhost:8001 | http://ccow.staging.va.gov | https://ccow.va.gov |
| `VISTA_SERVICE_URL` | http://localhost:8003 | http://vista.staging.va.gov | https://vista.va.gov |
| `POSTGRES_HOST` | localhost | postgres.staging | postgres.prod |

---

### 4. Database Connection Parameters (OPTIONAL in .env)

**Why:** Default values are usually fine for development, but production needs different settings.

```bash
# PostgreSQL
POSTGRES_HOST=localhost     # Default: localhost
POSTGRES_PORT=5432          # Default: 5432
POSTGRES_DB=medz1           # Default: medz1
POSTGRES_USER=postgres      # Default: postgres

# MinIO
MINIO_ENDPOINT=localhost:9000   # Default: localhost:9000
MINIO_BUCKET_NAME=med-z1        # Default: med-sandbox
```

**When to Override:**
- Production uses different hostnames
- Docker deployments use container names
- Multi-tenant environments use different bucket names

---

### 5. Feature Flags (RECOMMENDED in .env)

**Why:** Enable/disable features without code changes.

```bash
# CCOW Context Management
CCOW_ENABLED=true

# VistA Real-Time Data
VISTA_ENABLED=true
VISTA_RPC_LATENCY_ENABLED=true

# Storage Backend
USE_MINIO=true    # false for AWS S3 in production
```

**Usage:**
- Development: Enable all features for testing
- Staging: Mirror production configuration
- Production: Disable experimental features

---

### 6. Performance Tuning (OPTIONAL in .env)

**Why:** Fine-tune behavior without redeploying code.

```bash
# VistA Simulated Latency (development only)
VISTA_RPC_LATENCY_MIN=1.0
VISTA_RPC_LATENCY_MAX=3.0

# Session Configuration
SESSION_TIMEOUT_MINUTES=15
```

**When to Configure:**
- Testing different timeout values
- Simulating network conditions
- Performance benchmarking

---

### 7. File Paths (OPTIONAL in .env)

**Why:** Output directories vary by developer workstation and deployment environment.

```bash
# Output directories
ASCII_EXTRACT_FOLDER="~/swdev/med/med-output/extract/"
LOG_DIRECTORY_PATH="/Users/chuck/swdev/med/med-output/log/"
```

**When to Override:**
- Developer workstations (different home directories)
- Docker containers (volume mounts)
- Production servers (dedicated storage)

---

## Variables NOT in .env (Hard-Coded Defaults)

Some variables should **remain hard-coded** in `config.py` with defaults:

### Application Constants

```python
# Hard-coded in config.py - DO NOT add to .env
APP_NAME = "med-z1"
APP_VERSION = "0.1.0"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
```

**Why:** These are application constants that should be consistent across all environments.

### Default Port Numbers

```python
# Hard-coded defaults in config.py
# Only override in .env if needed
int(os.getenv("CCOW_VAULT_PORT", "8001"))
int(os.getenv("POSTGRES_PORT", "5432"))
```

**Why:** Standard defaults work for 99% of cases. Only override when ports conflict.

---

## Best Practices

### 1. Use .env for Secrets

✅ **DO:**
- Passwords
- API keys
- Secret tokens
- Private certificates

❌ **DON'T:**
- Commit `.env` to Git
- Share `.env` files via email/Slack
- Use same passwords across environments

### 2. Use .env for Environment-Specific Config

✅ **DO:**
- Database hostnames (localhost vs. prod server)
- Service URLs (http://localhost vs. https://prod.va.gov)
- Feature flags (enable experimental features in dev only)
- File paths (developer workstations differ)

❌ **DON'T:**
- Application logic (use code)
- Business rules (use code)
- Default values that work everywhere (use config.py defaults)

### 3. Provide Sensible Defaults in config.py

```python
# GOOD: Sensible default, overridable via .env
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "15"))

# GOOD: No default for secrets (forces explicit configuration)
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")  # Raises error if missing

# BAD: Hard-coded value, no .env support
SESSION_TIMEOUT_MINUTES = 15  # Can't be changed without code change
```

### 4. Document Variables

Every variable in `.env` should have:
- ✅ Comment explaining purpose
- ✅ Default value (if applicable)
- ✅ Environment-specific guidance (dev vs. prod)
- ✅ Security notes (if sensitive)

**Example:**
```bash
# Session timeout in minutes (default: 15)
# Development: 15 (short, for rapid testing)
# Production: 30-60 (balance security vs. convenience)
SESSION_TIMEOUT_MINUTES=15
```

---

## .env Template

Create `.env.template` (committed to Git) with placeholders:

```bash
# -------------------------------------------------------
# .env.template - Copy to .env and fill in values
# -------------------------------------------------------

# CDWWork Database
CDWWORK_DB_PASSWORD="REPLACE_WITH_YOUR_PASSWORD"

# PostgreSQL Database
POSTGRES_PASSWORD="REPLACE_WITH_YOUR_PASSWORD"

# MinIO S3 Storage
MINIO_SECRET_KEY="REPLACE_WITH_YOUR_SECRET_KEY"

# Authentication & Session
SESSION_TIMEOUT_MINUTES=15
SESSION_COOKIE_SECURE=false  # Set to true in production
```

**Usage:**
```bash
# New developer setup
cp .env.template .env
# Edit .env with actual values
```

---

## Security Considerations

### Development (.env)
```bash
SESSION_COOKIE_SECURE=false        # HTTP allowed (localhost)
POSTGRES_PASSWORD="simple-dev-pw"  # Simple password OK for local DB
```

### Production (.env)
```bash
SESSION_COOKIE_SECURE=true         # HTTPS only
POSTGRES_PASSWORD="$(vault read secret/medz1/db)"  # Retrieved from secrets manager
```

**Production Security:**
- ✅ Use secrets management (HashiCorp Vault, AWS Secrets Manager)
- ✅ Rotate passwords regularly
- ✅ Use different passwords per environment
- ✅ Enable HTTPS (SESSION_COOKIE_SECURE=true)
- ✅ Use strict SameSite cookies (SESSION_COOKIE_SAMESITE=strict)

---

## Testing Configuration

To verify `.env` is loaded correctly:

```bash
python -c "from config import SESSION_TIMEOUT_MINUTES, POSTGRES_PASSWORD; print(f'Timeout: {SESSION_TIMEOUT_MINUTES}'); print('DB password configured' if POSTGRES_PASSWORD else 'DB password MISSING')"
```

Expected output:
```
Timeout: 15
DB password configured
```

---

## Migration Checklist

When adding a new environment variable:

1. ✅ Add to `config.py` with sensible default
2. ✅ Add to `.env` if environment-specific
3. ✅ Add to `.env.template` with placeholder
4. ✅ Document in this guide
5. ✅ Update relevant subsystem READMEs
6. ✅ Test with default value (no .env override)
7. ✅ Test with .env override

---

## Summary Table

| Variable Type | In .env? | In config.py? | Example |
|---------------|----------|---------------|---------|
| Secrets (passwords, keys) | ✅ Required | ✅ Read from env | `POSTGRES_PASSWORD` |
| Environment-specific URLs | ✅ Recommended | ✅ With default | `CCOW_URL` |
| Session configuration | ✅ Recommended | ✅ With default | `SESSION_TIMEOUT_MINUTES` |
| Feature flags | ✅ Recommended | ✅ With default | `CCOW_ENABLED` |
| Application constants | ❌ No | ✅ Hard-coded | `APP_NAME`, `APP_VERSION` |
| Standard ports | ⚠️ Optional | ✅ With default | `POSTGRES_PORT=5432` |

---

## Related Documentation

- `config.py` - Central configuration module
- `.env` - Environment-specific values (not committed)
- `.env.template` - Template for new developers (committed)
- `docs/user-auth-design.md` - Session management architecture
- `docs/ccow-vault-design.md` - CCOW configuration
