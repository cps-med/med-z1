# Developer Setup Guide - Review & Feedback

**Document:** `docs/guide/developer-setup-guide.md`
**Reviewed:** 2026-01-03
**Reviewer:** Claude Code
**Status:** Pending Updates

## Executive Summary

The developer setup guide is **well-structured and 85% complete**, providing comprehensive coverage of core setup steps with clear examples and logical flow. However, several critical gaps must be addressed before a new developer can successfully set up the entire med-z1 system.

**Key Strengths:**
- ✅ Comprehensive coverage of core infrastructure (PostgreSQL, SQL Server, MinIO, Docker)
- ✅ Clear separation of macOS and Linux instructions (where present)
- ✅ Good use of code blocks and practical examples
- ✅ Logical progression from environment setup → data setup → running application

**Critical Gaps:**
- ❌ Missing Clinical Notes ETL pipeline (domain exists in codebase)
- ❌ Missing CCOW service startup instructions (required for patient context)
- ❌ Missing .env variable documentation/template reference
- ❌ No final verification checklist for complete setup
- ❌ Platform-specific guidance incomplete (Git, Python versions)

---

## Review Checklist

Use this checklist to track progress as you address each item. Items are organized by priority.

---

## 🔴 CRITICAL ISSUES (Must Fix)

### ⬜ 1. Add Clinical Notes ETL Pipeline

**Location:** Multiple sections

**Issue:**
The Clinical Notes domain is completely omitted from the guide, but the infrastructure exists in the codebase:
- ETL scripts exist: `etl/bronze_clinical_notes_vista.py`, `etl/silver_clinical_notes.py`, `etl/gold_clinical_notes.py`, `etl/load_clinical_notes.py`
- DDL exists: `db/ddl/create_patient_clinical_notes_table.sql`
- Domain is documented in `CLAUDE.md` as added 2026-01-02

**Action Required:**

1. **Add to "Create PostgreSQL Clinical Domain Schemas" section (lines 664-677)**
   ```bash
   docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_clinical_notes_table.sql
   ```

2. **Add to "Verify tables were created" section (line 682)**
   - Add `patient_clinical_notes` to expected output list

3. **Add new section after "Laboratory Results Pipeline" (after line 819)**
   ```markdown
   #### 8. Clinical Notes Pipeline

   ```bash
   # Bronze: Extract clinical notes from VistA
   python -m etl.bronze_clinical_notes_vista

   # Silver: Clean and harmonize
   python -m etl.silver_clinical_notes

   # Gold: Create query-optimized notes
   python -m etl.gold_clinical_notes

   # Load: Insert into PostgreSQL
   python -m etl.load_clinical_notes
   ```
   ```

4. **Update `scripts/run_all_etl.sh`** to include Clinical Notes pipeline

**Reference:** CLAUDE.md lines 225-228 (Clinical Notes Tables documentation)

---

### ⬜ 2. Add CCOW Service Startup Instructions

**Location:** "Next Steps" section (lines 841-858)

**Issue:**
The guide only mentions starting the main app on port 8000, but the CCOW Context Management service (port 8001) is required for patient context synchronization and is not mentioned.

**Action Required:**

Replace the "Next Steps" section with comprehensive service startup:

```markdown
## Running the Application

With the ETL pipelines complete, you now have:
- Mock CDW data in SQL Server (simulates VA production CDW)
- Bronze/Silver/Gold Parquet files in MinIO (data lake)
- Query-optimized data in PostgreSQL (serving database for UI)

The med-z1 application consists of multiple FastAPI services that should be running simultaneously.

### Start All Services

You will need **three terminal windows** (or use a terminal multiplexer like tmux):

**Terminal 1: CCOW Context Vault Service (Required)**
```bash
cd ~/swdev/med/med-z1
source .venv/bin/activate
uvicorn ccow.main:app --reload --port 8001
```

Access CCOW API docs: http://127.0.0.1:8001/docs

**Terminal 2: Main med-z1 Web Application (Required)**
```bash
cd ~/swdev/med/med-z1
source .venv/bin/activate
uvicorn app.main:app --reload
```

Access main app: http://127.0.0.1:8000

**Terminal 3: VistA RPC Broker Simulator (Optional - Future)**
```bash
cd ~/swdev/med/med-z1
source .venv/bin/activate
uvicorn vista.app.main:app --reload --port 8003
```

Note: VistA RPC Broker is under development and not yet required for basic functionality.

### Test the Application

1. Open browser to http://127.0.0.1:8000
2. You should be redirected to the login page
3. Login with test credentials:
   - Email: `clinician.alpha@va.gov`
   - Password: `VaDemo2025!`
4. Search for patient by ICN: `ICN100001`
5. Verify patient dashboard loads with clinical widgets

### Stop Services

To stop each service, press `CTRL+C` in each terminal window.
```

**Reference:** `ccow/README.md` lines 38-53 (Port configuration and service startup)

---

### ⬜ 3. Add .env Variable Documentation Reference

**Location:** "Add and Configure .env File" section (lines 82-88)

**Issue:**
The guide mentions getting `.env` from a peer developer but doesn't explain what variables are required. The docker-compose.yaml uses specific variables (`${CDWWORK_DB_PASSWORD}`, `${MINIO_ACCESS_KEY}`, etc.) that must be present.

**Action Required:**

Expand the .env section:

```markdown
## Add and Configure .env File

The med-z1 application uses a project-wide `.env` file for managing secrets and other sensitive information. This file is not under version control for security reasons.

### Option 1: Get .env from Peer Developer (Recommended)

Ask a peer developer for a copy of the `.env` file and place it in the med-z1 root directory:

```bash
cp .env ~/swdev/med/med-z1/
```

### Option 2: Create .env from Template

If you're the first developer setting up the project, create a `.env` file with the required variables. See `docs/guide/environment-variables-guide.md` for a complete reference.

**Minimum Required Variables:**
```bash
# Database Passwords
CDWWORK_DB_PASSWORD=YourSecurePassword123!
POSTGRES_PASSWORD=yourpassword

# MinIO Configuration
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin#123#2025
MINIO_BUCKET_NAME=med-z1

# CCOW Configuration
CCOW_BASE_URL=http://localhost:8001

# Application Configuration
SECRET_KEY=your-secret-key-here-generate-random-string
```

**Important:** Never commit the `.env` file to version control. It is already in `.gitignore`.

### Verify .env Configuration

After placing the `.env` file in the project root, verify it exists:

```bash
cd ~/swdev/med/med-z1
ls -la .env
```
```

**Reference:** `docs/guide/environment-variables-guide.md` (if it contains template)

---

### ⬜ 4. Fix Platform-Specific Python Version Confusion

**Location:** Lines 5, 90-146

**Issue:**
- Line 5 states: "Python 3.11 on macOS, Python 3.10 on Linux"
- But installation instructions (lines 118-134) only cover Python 3.11
- Line 146 says "Python v3.10 or v3.11" without platform clarification
- This creates confusion about which version to install

**Action Required:**

**Option A (Recommended): Standardize on Python 3.11 for both platforms**

1. Update line 5:
   ```markdown
   **Prerequisite:** This application requires Python version 3.11 for both macOS and Linux environments. Higher versions of Python (3.12+) may have compatibility issues with supporting dependencies such as numpy, pandas, and polars.
   ```

2. Update line 90-98 to clarify Python 3.11 for both platforms

3. Add Linux Python installation instructions after macOS section:
   ```markdown
   **Install Python 3.11 on Linux (Pop!_OS/Ubuntu)**

   ```bash
   # Add deadsnakes PPA for Python 3.11
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt-get update

   # Install Python 3.11
   sudo apt-get install python3.11 python3.11-venv python3.11-dev

   # Verify installation
   python3.11 --version  # Should show 3.11.x
   ```
   ```

**Option B: Keep platform-specific versions (more complex)**

If you choose this option, clearly separate macOS (3.11) and Linux (3.10) instructions throughout the document.

---

### ⬜ 5. Add Final Verification Checklist

**Location:** End of document (after line 858)

**Issue:**
No comprehensive checklist exists to verify complete setup. Developers need confidence they've completed all steps correctly.

**Action Required:**

Add new section at the end:

```markdown
## Setup Verification Checklist

Use this checklist to verify your complete med-z1 development environment is properly configured.

### Infrastructure Services

```bash
# Verify all Docker containers are running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected containers:
- ⬜ `sqlserver2019` - Up, port 1433
- ⬜ `postgres16` - Up, port 5432
- ⬜ `med-insight-minio` - Up, ports 9000-9001

### Database Setup

```bash
# Verify PostgreSQL database and schemas
docker exec -it postgres16 psql -U postgres -d medz1 -c "\dn"
```

Expected schemas:
- ⬜ `auth` - User authentication schema
- ⬜ `clinical` - Clinical domain tables
- ⬜ `public` - Default schema

```bash
# Verify clinical tables exist
docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt clinical.*"
```

Expected tables (10 total):
- ⬜ `patient_demographics`
- ⬜ `patient_vitals`
- ⬜ `patient_allergies`
- ⬜ `patient_allergy_reactions`
- ⬜ `patient_medications_outpatient`
- ⬜ `patient_medications_inpatient`
- ⬜ `patient_flags`
- ⬜ `patient_flag_history`
- ⬜ `patient_encounters`
- ⬜ `patient_labs`
- ⬜ `patient_clinical_notes` (when implemented)

```bash
# Verify mock users loaded
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM auth.users;"
```

Expected output:
- ⬜ 5 mock users loaded

```bash
# Verify SQL Server CDWWork database
sqlcmd -S 127.0.0.1,1433 -U sa -P 'YourPassword' -C -Q "SELECT name FROM sys.databases WHERE name='CDWWork';"
```

Expected output:
- ⬜ CDWWork database exists

### ETL Pipeline Verification

```bash
# Verify MinIO buckets and Parquet files exist
# Login to MinIO console: http://localhost:9001
```

- ⬜ MinIO `med-z1` bucket exists
- ⬜ `bronze/` folder contains Parquet files (7+ domains)
- ⬜ `silver/` folder contains Parquet files (7+ domains)
- ⬜ `gold/` folder contains Parquet files (7+ domains)

```bash
# Verify PostgreSQL data loaded
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_demographics;"
```

Expected counts:
- ⬜ Patient demographics: 20 patients
- ⬜ Patient vitals: 80+ records
- ⬜ Patient allergies: 25+ records
- ⬜ Patient medications: 30+ records
- ⬜ Patient encounters: 15+ records
- ⬜ Patient labs: 58+ results

### Application Services

Start all services in separate terminals:

- ⬜ CCOW service starts without errors (port 8001)
- ⬜ Main app starts without errors (port 8000)
- ⬜ No port conflict errors
- ⬜ No database connection errors

### UI Verification

- ⬜ Navigate to http://127.0.0.1:8000/
- ⬜ Redirected to login page
- ⬜ Can login with: `clinician.alpha@va.gov` / `VaDemo2025!`
- ⬜ Can search for patient ICN: `ICN100001`
- ⬜ Patient dashboard loads successfully
- ⬜ Clinical widgets display data:
  - ⬜ Demographics widget
  - ⬜ Vitals widget (with chart)
  - ⬜ Allergies widget
  - ⬜ Medications widget
  - ⬜ Encounters widget
  - ⬜ Labs widget (when implemented)
- ⬜ "View Flags" button in topbar shows flag count
- ⬜ Can navigate to dedicated domain pages (Vitals, Allergies, etc.)

### CCOW Service Verification

```bash
# Test CCOW API
curl http://localhost:8001/ccow/health
```

- ⬜ CCOW health check returns 200 OK
- ⬜ CCOW API docs accessible at http://127.0.0.1:8001/docs

---

## Troubleshooting

If any checklist item fails, see the Troubleshooting section below.
```

---

## 🟠 MAJOR ISSUES (Should Fix)

### ⬜ 6. Fix Git Setup for Linux Platforms

**Location:** "GIT Setup" section (lines 7-37)

**Issue:**
Section only covers macOS (`xcode-select --install`), but guide claims to support "macOS or Linux." Linux users don't need xcode-select and git is typically pre-installed.

**Action Required:**

Add platform-specific Git setup:

```markdown
## GIT Setup

Prior to getting started, ensure that you have a current version of git installed and configured on your local machine.

### macOS Setup

For macOS environments, it is recommended that you use the standard Apple Xcode developer tools. Installation of the Xcode app is not required. Instead, you can install the **Command Line Tools** via the command below:

```bash
# Install macOS Developer Tools
xcode-select --install
```

Verify installation:
```bash
# Check git version
git --version

# Check the path to the active developer directory
xcode-select -p
```

### Linux Setup

Most Linux distributions (including Pop!_OS) come with git pre-installed.  

Verify installation:
```bash
# Check git version
git --version
```

If git is not installed (unlikely), install via apt:
```bash
sudo apt-get update
sudo apt-get install git
```

### Configure Git (All Platforms)

Set up basic information about yourself:
```bash
git config --global user.name "Your Name"
git config --global user.email your.email@example.com
git config --global color.ui true
```

To display your Git settings:
```bash
git config --list
git config --local --list
git config --global --list
```
```

---

### ⬜ 7. Fix Docker Setup - PostgreSQL Password Consistency

**Location:** "Pull and Create PostgreSQL Container" section (lines 246-261)

**Issue:**
Manual `docker run` command shows hardcoded password (`-e POSTGRES_PASSWORD=yourpassword`), but docker-compose.yaml uses `${POSTGRES_PASSWORD}` from .env. Should be consistent.

**Action Required:**

Update PostgreSQL container creation instructions:

```markdown
**Pull and Create PostgreSQL Container**

PostgreSQL is the **serving database** for med-z1, providing low-latency access to Gold-layer data.

**Note:** Ensure your `.env` file contains `POSTGRES_PASSWORD` before proceeding.

```bash
# Create PostgreSQL container using password from .env
# Replace ${POSTGRES_PASSWORD} with the actual password from your .env file
docker run -d \
    --name postgres16 \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    -p 5432:5432 \
    -v postgres16-data:/var/lib/postgresql/data \
    postgres:16

# Verify container is running
docker ps | grep postgres16
```

**For Linux users:** The docker-compose.yaml will automatically use the POSTGRES_PASSWORD from your .env file.
```

---

### ⬜ 8. Fix MinIO Password Inconsistencies

**Location:** Lines 266-272, line 829

**Issue:**
Multiple different passwords shown for MinIO:
- Line 269: `MINIO_ROOT_PASSWORD=password`
- Line 829: `admin / admin#123#2025`
- docker-compose.yaml: `${MINIO_SECRET_KEY}` from .env

**Action Required:**

1. **Standardize MinIO credentials throughout document**

2. **Update line 266-272:**
   ```markdown
   **Pull and Create MinIO Container**

   MinIO provides S3-compatible object storage for the data lake (Parquet files).

   **Note:** Ensure your `.env` file contains `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY` before proceeding.

   ```bash
   # Create MinIO container using credentials from .env
   # Replace values with actual credentials from your .env file
   docker run -d --name med-insight-minio \
     -p 9000:9000 -p 9001:9001 \
     -e MINIO_ROOT_USER=${MINIO_ACCESS_KEY} \
     -e MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY} \
     -v $HOME/minio-data:/data \
     quay.io/minio/minio server /data --console-address ":9001"
   ```
   ```

3. **Update line 440-444 (MinIO login section):**
   ```markdown
   Login with credentials from your `.env` file:
   ```
   Username: (value of MINIO_ACCESS_KEY from .env)
   Password: (value of MINIO_SECRET_KEY from .env)
   ```

   Example if using default values:
   - Username: `admin`
   - Password: `admin#123#2025`
   ```

---

### ⬜ 9. Add Reference to Architecture Documentation

**Location:** After "Clone med-z1 Repo" section (after line 79)

**Issue:**
New developers should understand the system architecture before diving into setup. No reference to design documents is provided.

**Action Required:**

Add new section after cloning repo:

```markdown
## Understanding the Architecture (Recommended)

Before setting up your development environment, we recommend reviewing the architecture documentation to understand how med-z1 is structured.

**Key Documents:**
- **`docs/spec/architecture.md`** - System architecture, patterns, and ADRs (Architecture Decision Records)
- **`docs/spec/med-z1-plan.md`** - Product roadmap and development phases
- **`CLAUDE.md`** - Project overview and coding guidelines (in project root)

**Domain-Specific Designs:**
- `docs/spec/demographics-design.md` - Patient demographics
- `docs/spec/vitals-design.md` - Vital signs
- `docs/spec/allergies-design.md` - Allergy tracking
- `docs/spec/medications-design.md` - Medication history
- `docs/spec/patient-flags-design.md` - Patient record flags
- `docs/spec/encounters-design.md` - Inpatient encounters
- `docs/spec/lab-results-design.md` - Laboratory results
- `docs/spec/clinical-notes-design.md` - Clinical notes

**Infrastructure Designs:**
- `docs/spec/ccow-vault-design.md` - Patient context management
- `docs/spec/vista-rpc-broker-design.md` - Real-time VistA data (future)
- `docs/spec/user-auth-design.md` - Authentication system

**Optional but Helpful:** Reviewing `docs/spec/architecture.md` will help you understand:
- Why we use FastAPI + HTMX instead of React
- How the medallion data architecture (Bronze/Silver/Gold) works
- API routing patterns (when to use Pattern A vs Pattern B)
- Design decisions and their rationale

You can proceed with setup now and refer to these documents as needed.
```

---

### ⬜ 10. Add Comprehensive Service Verification Section

**Location:** After Docker setup sections (after line 325)

**Issue:**
Individual container verification exists, but no single command showing all services running together.

**Action Required:**

Add new section after Docker CLI commands:

```markdown
### Verify All Containers Running

After starting all containers, verify they are all running correctly:

```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected output should show all three containers:
```
NAMES                  STATUS              PORTS
sqlserver2019          Up X minutes        0.0.0.0:1433->1433/tcp
postgres16             Up X minutes        0.0.0.0:5432->5432/tcp
med-insight-minio      Up X minutes        0.0.0.0:9000-9001->9000-9001/tcp
```

Verify container health:
```bash
# Check SQL Server logs (should show "SQL Server is now ready for client connections")
docker logs sqlserver2019 | tail -20

# Check PostgreSQL logs
docker logs postgres16 | tail -20

# Check MinIO logs
docker logs med-insight-minio | tail -20
```

**If any containers are not running:**
- Check for port conflicts: `lsof -i :1433`, `lsof -i :5432`, `lsof -i :9000`
- Review container logs: `docker logs <container_name>`
- Ensure .env file contains required passwords
- See Troubleshooting section (end of document)
```

---

### ⬜ 11. Add VistA RPC Broker Service Note

**Location:** "Running the Application" section (within the new service startup section)

**Issue:**
VistA RPC Broker service exists in codebase (`vista/app/main.py`) and is documented in design specs, but not mentioned in setup guide.

**Action Required:**

Already addressed in item #2 (CCOW Service Startup Instructions). Ensure the note about VistA being "under development and not yet required" is included.

---

### ⬜ 12. Add Troubleshooting Section

**Location:** End of document (after verification checklist)

**Issue:**
No troubleshooting guidance for common setup issues.

**Action Required:**

Add new section:

```markdown
## Troubleshooting

### Common Issues and Solutions

#### Port Already in Use Errors

**Symptom:** Error message: "bind: address already in use" or "port is already allocated"

**Solution:**
```bash
# Find process using the port (example: port 1433)
lsof -i :1433

# Kill the process
kill -9 <PID>

# Or stop the conflicting container
docker stop <container_name>
```

**Common ports:**
- 1433 - SQL Server
- 5432 - PostgreSQL
- 8000 - Main med-z1 app
- 8001 - CCOW service
- 8003 - VistA service (future)
- 9000, 9001 - MinIO

---

#### SQL Server Permission Errors on Apple Silicon

**Symptom:** SQL Server container fails to start or shows permission errors on M1/M2 Macs

**Solution:**
1. Ensure you're using SQL Server 2019 (not 2022)
2. Include `--platform linux/amd64` flag in docker run command
3. Verify Rosetta 2 is installed: `softwareupdate --install-rosetta`

---

#### PostgreSQL Connection Refused

**Symptom:** "connection refused" or "could not connect to server"

**Solution:**
```bash
# Verify container is running
docker ps | grep postgres

# Check container logs
docker logs postgres16

# Verify port is listening
lsof -i :5432

# Test connection manually
docker exec -it postgres16 psql -U postgres -d postgres
```

---

#### MinIO Bucket Creation Fails

**Symptom:** Cannot create `med-z1` bucket via web console

**Solution:**
1. Verify MinIO container is running: `docker ps | grep minio`
2. Check MinIO logs: `docker logs med-insight-minio`
3. Verify login credentials match .env file
4. Try creating bucket via MinIO CLI (mc) if web console fails

---

#### Python Dependency Conflicts

**Symptom:** pip install fails with version conflicts for numpy, pandas, or polars

**Solution:**
```bash
# Ensure you're using Python 3.11 (not 3.12+)
python3 --version

# Recreate virtual environment
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

#### ETL Pipeline Fails - "Connection to database failed"

**Symptom:** ETL scripts fail with database connection errors

**Solution:**
1. Verify .env file exists and contains correct database passwords
2. Verify all containers are running: `docker ps`
3. Test SQL Server connection: `sqlcmd -S 127.0.0.1,1433 -U sa -P 'YourPassword' -C -Q "SELECT @@VERSION"`
4. Test PostgreSQL connection: `docker exec -it postgres16 psql -U postgres -d medz1`
5. Test MinIO connection: `python -m scripts.minio_test`

---

#### ETL Pipeline Fails - "MinIO bucket not found"

**Symptom:** ETL scripts fail with "bucket 'med-z1' does not exist"

**Solution:**
1. Login to MinIO console: http://localhost:9001
2. Verify `med-z1` bucket exists
3. If not, create bucket via console or MinIO CLI
4. Verify MINIO_BUCKET_NAME in .env matches actual bucket name

---

#### Login Fails - "Invalid credentials"

**Symptom:** Cannot login to med-z1 application

**Solution:**
1. Verify auth tables were created: `docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt auth.*"`
2. Verify mock users were loaded: `docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT email FROM auth.users;"`
3. Use correct credentials: `clinician.alpha@va.gov` / `VaDemo2025!`
4. Check application logs for detailed error messages

---

#### CCOW Service Not Running

**Symptom:** Application shows context management errors

**Solution:**
1. Verify CCOW service is running on port 8001
2. Check CCOW_BASE_URL in .env matches: `http://localhost:8001`
3. Test CCOW health: `curl http://localhost:8001/ccow/health`
4. Restart CCOW service: `uvicorn ccow.main:app --reload --port 8001`

---

#### Dashboard Shows "No Data" Despite Successful ETL

**Symptom:** Patient dashboard loads but widgets show no data

**Solution:**
1. Verify data loaded into PostgreSQL:
   ```bash
   docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_demographics;"
   ```
2. Check if using correct ICN for test patient: `ICN100001`
3. Review application logs for database query errors
4. Verify all ETL pipelines completed successfully (check last "Load" step)

---

### Getting Help

If you encounter issues not covered here:
1. Review application logs in terminal where services are running
2. Check Docker container logs: `docker logs <container_name>`
3. Consult design documents in `docs/spec/` for architecture context
4. Review CLAUDE.md for coding patterns and project structure
```

---

## 🟡 MINOR ISSUES (Polish)

### ⬜ 13. Fix Typo: "Prerequistite" → "Prerequisite"

**Location:** Line 5

**Current:**
```markdown
**Prerequistite:** This application is designed...
```

**Corrected:**
```markdown
**Prerequisite:** This application is designed...
```

---

### ⬜ 14. Fix Typo: "witih" → "with"

**Location:** Line 5

**Current:**
```markdown
...may have incompatibility issues witih some of the supporting dependencies...
```

**Corrected:**
```markdown
...may have incompatibility issues with some of the supporting dependencies...
```

---

### ⬜ 15. Fix Typo: "Pythone" → "Python"

**Location:** Line 177

**Current:**
```markdown
To deactivate a Pythone virtual environment:
```

**Corrected:**
```markdown
To deactivate a Python virtual environment:
```

---

### ⬜ 16. Fix Typo in docker-compose.yaml Comment

**Location:** docker-compose.yaml line 4

**Current:**
```yaml
# • not used by macOS environment (uses Docker Desketop)
```

**Corrected:**
```yaml
# • not used by macOS environment (uses Docker Desktop)
```

---

### ⬜ 17. Clarify SQL Server 2019 Requirement

**Location:** Line 216

**Current:**
```markdown
It is best to use SQL Server 2019, not 2022. SQL Server 2022 has issues on Apple Silicon.
```

**Suggested:**
```markdown
**Important:** Use SQL Server 2019, not 2022. SQL Server 2022 has compatibility issues on Apple Silicon (M1/M2) chips and may fail to start or exhibit permission errors. SQL Server 2019 runs via Rosetta 2 emulation and is the recommended version for development.
```

---

### ⬜ 18. Consider Renaming MinIO Container for Consistency

**Location:** Lines 267, 272, and throughout

**Current:** `med-insight-minio`
**Suggested:** `med-z1-minio`

**Rationale:** Container name should match project name (med-z1) for consistency. "med-insight" appears to be from an earlier project iteration.

**Action Required:** If renaming:
1. Update all references in developer guide
2. Update docker-compose.yaml
3. Update any scripts that reference container name
4. Document migration path for existing developers

---

## 🔵 STRUCTURAL RECOMMENDATIONS (Enhancement)

### ⬜ 19. Add Quick Start Section

**Location:** Near top of document (after table of contents, if present)

**Action Required:**

Add quick reference for experienced developers:

```markdown
## Quick Start (Experienced Developers)

For developers familiar with Python, Docker, and PostgreSQL who want to get started quickly:

```bash
# 1. Prerequisites: Python 3.11, Docker Desktop/Engine, git
python3.11 --version && docker --version && git --version

# 2. Clone and configure
git clone https://github.com/cps-med/med-z1.git
cd med-z1
# Get .env file from peer developer and place in project root

# 3. Start infrastructure (choose one)
docker compose up -d              # Linux with docker-compose.yaml
# OR manually start 3 containers  # macOS with Docker Desktop

# 4. Create databases
docker exec -it postgres16 psql -U postgres -c "CREATE DATABASE medz1;"
cd mock/sql-server/cdwwork/create && ./_master.sh  # Create CDWWork schema
cd ../insert && ./_master.sh                        # Populate CDWWork data

# 5. Setup Python environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 6. Setup PostgreSQL schemas
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_auth_tables.sql
docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql
# Run all clinical domain DDL scripts (see full guide)

# 7. Run ETL pipelines
./scripts/run_all_etl.sh

# 8. Start services (3 terminals)
uvicorn ccow.main:app --reload --port 8001      # Terminal 1
uvicorn app.main:app --reload                   # Terminal 2

# 9. Access application
# http://127.0.0.1:8000
# Login: clinician.alpha@va.gov / VaDemo2025!
# Search patient: ICN100001
```

**For detailed step-by-step instructions, continue reading below.**

---

## Table of Contents
(existing content continues...)
```

---

### ⬜ 20. Reorganize Document Structure

**Current Structure:**
1. GIT Setup
2. Clone Repo
3. Add .env
4. Verify Python
5. Create Virtual Environment
6. Install Docker
7. PostgreSQL Setup
8. PostgreSQL Auth Setup
9. MinIO Setup
10. SQL Server Tools
11. Create SQL Server Data
12. Run ETL
13. Next Steps

**Suggested Structure (More Logical Flow):**
1. **Prerequisites Overview** (what you need before starting)
2. **Development Environment Setup**
   - Git configuration
   - Python installation
   - Docker installation
3. **Clone Repository & Configuration**
   - Clone repo
   - Configure .env
   - Understand architecture (references to docs)
4. **Infrastructure Services Setup**
   - Docker containers (all three together)
   - Verification of all services
5. **Database Setup**
   - PostgreSQL (create DB + auth schema)
   - SQL Server (CDWWork creation + population)
   - MinIO (bucket creation)
6. **Python Environment**
   - Virtual environment
   - Dependencies
7. **Data Pipeline Execution**
   - Create PostgreSQL clinical schemas
   - Run ETL pipelines (all domains)
   - Verify data loaded
8. **Running the Application**
   - Start all services (CCOW + main app)
   - Test login and patient search
9. **Verification Checklist**
   - Complete setup verification
10. **Troubleshooting**
    - Common issues and solutions

**Action Required:** Consider reorganizing sections to follow this flow for better developer experience.

---

### ⬜ 21. Add Visual Indicators and Formatting

**Action Required:**

Add consistent symbols throughout the document:
- ✅ for completed prerequisites or verification steps
- ⚠️ for important warnings
- 💡 for helpful tips
- 🔧 for troubleshooting notes
- 📖 for documentation references

**Example:**
```markdown
⚠️ **Important:** Use SQL Server 2019, not 2022. SQL Server 2022 has compatibility issues on Apple Silicon.

💡 **Tip:** You can verify all Docker containers at once with: `docker ps`

📖 **Reference:** See `docs/spec/architecture.md` for detailed design rationale.
```

---

## Implementation Priority

**Phase 1: Critical Fixes (Complete First)**
1. ✅ Clinical Notes ETL Pipeline (#1)
2. ✅ CCOW Service Startup (#2)
3. ✅ .env Documentation (#3)
4. ✅ Python Version Clarity (#4)
5. ✅ Final Verification Checklist (#5)

**Phase 2: Major Improvements (Complete Second)**
6. ✅ Git Setup for Linux (#6)
7. ✅ PostgreSQL Password Consistency (#7)
8. ✅ MinIO Password Consistency (#8)
9. ✅ Architecture Documentation Reference (#9)
10. ✅ Service Verification Section (#10)
11. ✅ VistA Note (covered in #2)
12. ✅ Troubleshooting Section (#12)

**Phase 3: Polish (Complete Last)**
13-18. ✅ All typos and minor fixes

**Phase 4: Enhancements (Optional)**
19-21. ✅ Structural improvements (quick start, reorganization, visual indicators)

---

## Next Steps

1. Review this feedback document
2. Address Critical Issues (Phase 1) first
3. Test each change as you make it
4. Have another developer test the updated guide on a fresh machine
5. Update this review document's status as items are completed

---

## Notes

- This review is based on codebase state as of 2026-01-03
- Clinical Notes ETL pipelines exist but are not yet integrated into run_all_etl.sh
- VistA RPC Broker service is documented but may not be fully implemented
- Consider creating a companion "Quick Troubleshooting" one-pager for common issues
