# med-z1

**med-z1** is a next-generation health data viewer and AI assistant designed to replace and modernize the VA's Joint Longitudinal Viewer (JLV). The application offers a data architecture that dramatically improves response time to historical data (T-1 and earlier), while also offering the ability to view real-time updates from VistA (T-0).

Med-z1 combines data from the legacy VistA-based CDW database, **CDWWork**, the VA new EHR CDW database, **CDWWork2**, and mock **VistA** sites with current data, offering a unified view of the complete VA organization.

Refer to `med-z1/docs/screenshot/` for a set of web app UI screenshots.

## Application Architecture
The figure below, from `med-z1/docs/spec/med-z1-architecture.md`, provides a summary view of the med-z1 application architecture.  

```
┌─────────────────────────────────────────────────────────────────┐
│                        med-z1 System                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐      ┌───────────────┐                      │
│   │   CCOW Vault  │      │ VistA Service │                      │
│   │   (FastAPI)   │◄────►│   (FastAPI)   │                      │
│   │   Port 8001   │      │   Port 8003   │                      │
│   └───────────────┘      └─────┬─────────┘                      │
│             ▲ Active           │ T-0                            │
│             │ Patient          │                                │
│             ▼ Context          ▼                                │
│   ┌──────────────────────────────────┐      ┌───────────────┐   │
│   │              Web UI              │      │     AI/ML     │   │
│   │             (FastAPI)            │◄────►│     Tools     │   │
│   │             Port 8000            │      │  (LangGraph)  │   │
│   └──────────────────────────────────┘      └───────────────┘   │
│             ▲                                                   │
│             │ T-1 and prior                                     │
│   ┌─────────┴───────────────────────────────────────────────┐   │
│   │              PostgreSQL Serving Database                │   │
│   │    (demographics, allergies, labs, vitals, etc.)        │   │
│   └─────────────────────────────────────────────────────────┘   │
│             ▲                                                   │
│             │ ETL Pipeline                                      │
│   ┌─────────┴───────────────────────────────────────────────┐   │
│   │               MinIO Object Storage (S3)                 │   │
│   │           Bronze → Silver → Gold (Parquet)              │   │
│   └─────────────────────────────────────────────────────────┘   │
│             ▲                                                   │
│             │ ETL Pipeline                                      │
│   ┌─────────┴───────────────────────────────────────────────┐   │
│   │               Mock CDW (SQL Server 2019)                │   │
│   │       CDWWork (VistA) + CDWWork2 (Oracle Health)        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Local Environment Setup
Refer to the Developer Setup Guide for information on local development environment setup, and general guidance. This document is located at: `docs/guide/developer-setup-guide.md`.

You may need to reach out to a peer developer to get secret and sensitive information that is not under version control, such as the contents of .env files.  

## Quick Reference Guide.

### Docker Startup

Be sure and start all required Docker services, via CLI or Docker Desktop.  

I typically start the Docker Desktop and then each of the container image services. After starting Docker Desktop, each of the services can be started within the Docker Desktop UI, or via the CLI commands below:  
```bash
docker start sqlserver2019
docker start postgres16
docker start med-insight-minio
 - or -
docker start sqlserver2019 postgres16 med-insight-minio
```

### PostgreSQL Database Setup (First-Time Only)

**IMPORTANT:** Before running any ETL pipelines or setting up user authentication, you must create the `medz1` database. This is a one-time setup step for new developers.

```bash
# Step 1: Connect to the default 'postgres' database
docker exec -it postgres16 psql -U postgres -d postgres

# Step 2: Create the medz1 database (in psql prompt)
CREATE DATABASE medz1;

# Step 3: Verify creation
\l

# Step 4: Exit
\q
```

**Verification:**
```bash
# Connect to the newly created medz1 database
docker exec -it postgres16 psql -U postgres -d medz1

# Verify connection
SELECT current_database();
-- Should return: medz1

# Exit
\q
```

After creating the database, you can run the DDL scripts from `db/ddl/` and seed scripts from `db/seeds/` to set up tables and initial data.

**See also:** `docs/spec/implementation-roadmap.md` (Phase 1, Task 1.1) for detailed PostgreSQL setup instructions.

### PostgreSQL CLI Startup 

#### Tips for Postgres startup and verification

User authorization tables:
```bash
docker exec -it postgres16 psql -U postgres -d medz1
\d auth.users
\d auth.sessions
\d auth.audit_logs
```

### FastAPI Application Startup

The FastAPI services require a number of Python dependencies, so be sure and install the services within your Python virtual environment, ".venv". Then, activate your environment.

#### Python Virtual Environment

From your project root directory:
```bash
source .venv/bin/activate
```

#### FastAPI Services

Each of the three services must be running for the med-z1 application to function properly. Given the dependencies between each of the services, I recommend the following starup order:
```bash
uvicorn vista.app.main:app --reload --port 8003
uvicorn ccow.main:app --reload --port 8001
uvicorn app.main:app --reload --port 8000
```

Note that the main app uses default port 8000 (the --port 8000 argument is optional).

## Mock Users

| Email                     | Display Name                  | Home Site (Sta3n) | Role       |
|---------------------------|-------------------------------|-------------------|------------|
| clinician.alpha@va.gov    | Dr. Alice Anderson, MD        | 508 (Atlanta)     | Physician  |
| clinician.bravo@va.gov    | Dr. Bob Brown, DO             | 648 (Portland)    | Physician  |
| clinician.charlie@va.gov  | Nurse Carol Chen, RN          | 663 (Seattle)     | Nurse      |
| clinician.delta@va.gov    | Dr. David Davis, MD           | 509 (Augusta)     | Physician  |
| clinician.echo@va.gov     | Pharmacist Emma Evans, PharmD | 531 (Boise)       | Pharmacist |
| clinician.foxtrot@va.gov  | Dr. Frank Foster, MD          | 516 (Bay Pines)   | Physician  |
| clinician.golf@va.gov     | Dr. Grace Green, MD           | 552 (Dayton)      | Physician  |

**Password (all users):** `VaDemo2025!`

For complete authentication details, see `docs/guide/mock-users-guide.md`.
