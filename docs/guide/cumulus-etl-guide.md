# Cumulus ETL — Developer Guide

This guide provides a product overview, macOS local development setup instructions, and a mini-plan for getting started with [**cumulus-etl**](https://github.com/smart-on-fhir/cumulus-etl), the FHIR data ingestion engine of the Cumulus population health platform. It is written from the perspective of a med-z1 developer who wants to build complementary skills for VA EHR modernization and Oracle Health consulting work.

**Official documentation:** [https://docs.smarthealthit.org/cumulus/etl/](https://docs.smarthealthit.org/cumulus/etl/)  
**GitHub repository:** [https://github.com/smart-on-fhir/cumulus-etl](https://github.com/smart-on-fhir/cumulus-etl)  
**Current release:** v4.3.3 (April 21, 2026)  
**License:** Apache 2.0  
**Developed by:** SMART Health IT team at Boston Children's Hospital (ONC/CDC/ARPA-H funded)  

---

## 1. Product Overview

### What Problem It Solves

Cumulus ETL enables **population-scale clinical research from EHR data without exposing PHI outside institutional boundaries.** The 21st Century Cures Act mandates that all certified EHR vendors (Epic, Oracle Health/Cerner, VA systems) support the SMART/HL7 Bulk FHIR Access API, which means cumulus-etl can ingest data from any compliant EHR with no custom connector work. It was piloted across five academic health system + public health department dyads and is actively used in production.

The pipeline solves three interconnected problems:
1. **Extraction at scale** — bulk export of thousands of patients' FHIR resources efficiently
2. **De-identification before data leaves the firewall** — PHI never reaches cloud storage
3. **NLP on clinical notes** — structured codes extracted from free text before the notes are discarded

### Architecture: Extract → Transform → Load

```
EHR FHIR Server (Epic, Oracle Health, VA Lighthouse)
    ↓  [smart-fetch]
NDJSON Bulk FHIR files   ← PHI present, stays on-premises
    ↓  [cumulus-etl]
De-identified Delta Lake tables in S3/MinIO   ← No PHI
PHI build artifacts (ID mapping)              ← PHI, restricted path
    ↓  [cumulus-library]
Aggregate counts per research study
    ↓  [cumulus-aggregator]  (optional multi-site)
Combined multi-site aggregate counts
    ↓  [cumulus-app / dashboard]
Population health visualization
```

**Phase 1 — Extract:** Reads NDJSON bulk FHIR export files (from a local folder or S3 bucket). No direct EHR connection — use SMART Fetch for that step.

**Phase 2 — Transform (De-identification):** Drops PHI fields, HMAC-SHA256 hashes all resource IDs (patient, encounter, etc.), truncates birthdates to year only, generalizes zip codes to 3 digits. De-identification runs automatically on every ETL execution.

**Phase 3 — Transform (NLP, optional):** Clinical note attachments in `DiagnosticReport` and `DocumentReference` resources are downloaded, analyzed by NLP models, and then discarded. NLP output is stored as FHIR `Observation` resources.

**Phase 4 — Load:** Writes de-identified output as **Delta Lake** tables (columnar Parquet + transaction log) to an S3-compatible destination (AWS S3 or local MinIO).

### Relationship to med-z1

| med-z1 Component | cumulus-etl Equivalent |
|---|---|
| MinIO + Parquet (Bronze/Silver/Gold) | AWS S3 + Delta Lake |
| Multi-site VA architecture | Federated network of academic medical centers |
| Clinical NLP (LangGraph + GPT-4) | cTAKES, BERT negation, LLM prompting via Docker REST |
| ETL pipeline in Python | Production async Python ETL with incremental processing |
| FHIR data handling | Deep Bulk FHIR R4, NDJSON, US Core profiles |

Studying cumulus-etl is essentially studying the production-grade version of the medallion data architecture patterns you are building in med-z1.

### FHIR Resource Types Processed

AllergyIntolerance, Condition, Device, DiagnosticReport, DocumentReference, Encounter, EpisodeOfCare, Immunization, Location, Medication, MedicationDispense, MedicationRequest, Observation, Organization, Patient, Practitioner, PractitionerRole, Procedure, ServiceRequest, Specimen

---

## 2. The Cumulus Ecosystem

Cumulus ETL is one component in a larger platform. Understanding the full ecosystem helps you see where each tool fits.

### SMART Fetch (`smart-on-fhir/smart-fetch`)

The step **before** cumulus-etl. Connects to a live FHIR server (authenticated via SMART Backend Services), triggers a bulk FHIR export, downloads the resulting NDJSON files, and optionally hydrates them (inlines clinical note attachments, fetches linked resources). Produces a `log.ndjson` that cumulus-etl reads for group name and export timestamp metadata.

```bash
# Install
pipx install smart-fetch

# Export from a FHIR server
smart-fetch export --fhir-url https://your-fhir-server/fhir /tmp/my-export

# Hydrate (inline note attachments, fetch linked resources)
smart-fetch hydrate --tasks inline /tmp/my-export
```

### Cumulus Library (`smart-on-fhir/cumulus-library`)

The step **after** cumulus-etl. A framework for running SQL-based research "studies" against the de-identified Delta Lake tables in AWS Athena. Produces aggregate counts for population health research. Installable via `pip install cumulus-library`.

### Cumulus Aggregator (`smart-on-fhir/cumulus-aggregator`)

An AWS serverless application that receives aggregate counts from multiple institutions and combines them into a multi-site dataset. Only aggregate counts (no patient-level data) cross institutional boundaries. Used by the five pilot sites to share population health data with public health departments.

### Cumulus Dashboard (`smart-on-fhir/cumulus-app`)

A TypeScript web application for visualizing aggregated population health data served by the Cumulus Aggregator.

---

## 3. System Requirements (macOS)

### Required

| Component | Version | Notes |
|---|---|---|
| Docker Desktop | 27.x recommended | Older 24.x has known bugs. Primary delivery mechanism. |
| Docker Compose v2 | Bundled with Docker Desktop | Uses `compose.yaml` |
| macOS | Apple Silicon (M-series) or Intel | M-series runs some images under Rosetta emulation |

### Required for Local Python Development Only

| Component | Version | Notes |
|---|---|---|
| Python | >= 3.11 | Match med-z1's Python version |
| Java JDK | 21 (LTS) | Required for Delta Lake / Delta Spark |

Any OpenJDK 21 distribution works — Delta Spark only needs a compliant JVM on `JAVA_HOME`. Two recommended options:

```bash
# Option A: Eclipse Temurin 21 — matches the JRE bundled in the cumulus-etl Docker image
brew install --cask temurin

# Option B: Amazon Corretto 21 — good fit if targeting AWS infrastructure (S3, Athena)
brew install --cask corretto21
```

Both are free, TCK-certified, and provide long-term support for JDK 21. If you have used Corretto on prior projects, continue with it — there is no functional difference for this use case. Avoid `brew install openjdk` (Oracle reference builds), which only receives 6 months of updates per release and lacks long-term support.

### Hardware

| RAM | Recommended `--batch-size` |
|---|---|
| 16 GB | 100,000 (default) |
| 32 GB | 1,000,000 |

For local development and learning with 10–100 synthetic patients, a MacBook with 16 GB RAM is sufficient. NLP on large datasets benefits significantly from GPU, but is not needed for getting started.

### Notes for Apple Silicon (M-series Macs)

Some Docker images in the NLP profiles (`cnlpt-term-exists`) are pinned to `platform: linux/amd64` and run under Rosetta emulation on M-series Macs. This is slower but functional for learning purposes. The core ETL (no NLP) runs natively without any platform issues.

---

## 4. Installation

### Method 1: Docker Only (Recommended for Getting Started)

This is the official approach. You do not `pip install` anything.

```bash
# Step 1: Install Docker Desktop
# https://www.docker.com/products/docker-desktop/

# Step 2: Create a working directory
mkdir ~/cumulus-work && cd ~/cumulus-work

# Step 3: Get the compose.yaml (all you need to run cumulus-etl)
curl -O https://raw.githubusercontent.com/smart-on-fhir/cumulus-etl/refs/heads/main/compose.yaml

# Docker images are pulled automatically on first run
```

If you have already forked the repo on GitHub (see Section 13), clone your fork instead. This gives you access to the sample test data, documentation source, and the built-in test profile:

```bash
git clone https://github.com/your-username/cumulus-etl.git
cd cumulus-etl
```

### Method 2: Python Package Install (For Local Development / Contribution)

Fork the repo on GitHub first, then clone your fork (see Section 13 for the full one-time setup). Once you have your fork cloned locally:

```bash
cd cumulus-etl

# Create and activate a virtual environment (Python 3.11)
python3.11 -m venv .venv
source .venv/bin/activate

# Install with dev and test extras
pip install .[dev,tests]

# Install pre-commit hooks (enforces ruff linting)
pre-commit install
```

### Key Python Dependencies

For reference, the core dependencies installed with the package:

```
boto3 >= 1.34.131          # AWS S3 / MinIO access
ctakesclient >= 5.1        # cTAKES NLP client
cumulus-fhir-support >= 1.12  # FHIR utilities from the Cumulus team
delta-spark >= 4, < 5      # Delta Lake read/write (requires JVM)
httpx                      # Async HTTP
openai                     # LLM-based NLP studies
pyarrow                    # Parquet/Arrow serialization
pydantic                   # Data validation
rich                       # Terminal output formatting
```

---

## 5. Quick Start: Running Against Synthetic Data

This is the fastest path to seeing cumulus-etl work end-to-end. It uses a pre-built Synthea dataset (no PHI, no EHR needed).

### Step 1: Download the Sample Dataset

```bash
cd ~/cumulus-work

# Download 10-patient Synthea bulk FHIR dataset
curl -LO https://github.com/smart-on-fhir/sample-bulk-fhir-datasets/archive/refs/heads/10-patients.zip
unzip 10-patients.zip
# Creates: ./sample-bulk-fhir-datasets-10-patients/
```

The dataset contains standard FHIR R4 NDJSON files (`Patient.ndjson`, `Condition.ndjson`, etc.) generated by Synthea. These represent fictional patients with no real PHI.

### Step 2: Initialize the Output Folder

```bash
docker compose run --rm \
  --volume "$(pwd)":/host \
  cumulus-etl init \
  /host/output
```

This creates the empty Delta Lake table structure in `./output/`.

### Step 3: Run the ETL

```bash
docker compose run --rm \
  --volume "$(pwd)":/host \
  cumulus-etl etl \
  /host/sample-bulk-fhir-datasets-10-patients \
  /host/output \
  /host/phi
```

**What happens:**
- Input NDJSON files in `./sample-bulk-fhir-datasets-10-patients/` are read
- Each resource is de-identified (IDs hashed, dates truncated, zip codes generalized)
- De-identified records are written as Delta Lake Parquet files to `./output/`
- PHI build artifacts (ID mapping table) are written to `./phi/`

**Note:** When running against a folder without a `log.ndjson` (which SMART Fetch generates), you must add `--export-group` and `--export-timestamp`:

```bash
docker compose run --rm \
  --volume "$(pwd)":/host \
  cumulus-etl etl \
  /host/sample-bulk-fhir-datasets-10-patients \
  /host/output \
  /host/phi \
  --export-group "test-group" \
  --export-timestamp "2026-01-01T00:00:00Z"
```

### Step 4: Inspect the Output

```bash
ls output/
# patient/  condition/  observation/  encounter/ ...

ls output/patient/
# _delta_log/  part-00000-*.parquet  ...
```

You can read the Parquet output directly with DuckDB or pandas:

```python
import duckdb

# Query de-identified patient data
duckdb.sql("SELECT * FROM read_parquet('output/patient/*.parquet') LIMIT 10").show()

# Count conditions by code
duckdb.sql("""
    SELECT
        code.coding[1].code AS icd_code,
        code.coding[1].display AS condition,
        COUNT(*) AS patient_count
    FROM read_parquet('output/condition/*.parquet')
    GROUP BY 1, 2
    ORDER BY 3 DESC
""").show()
```

---

## 6. Running Against a Local FHIR Server

Cumulus ETL does **not** connect directly to FHIR servers. Direct EHR connection functionality was removed in favor of the separate `smart-fetch` tool. The workflow is:

```
Local FHIR Server  →  smart-fetch  →  NDJSON files  →  cumulus-etl
```

### Option A: HAPI FHIR Server + Synthea Data

This gives you the most realistic local development workflow.

**Step 1: Start a local HAPI FHIR server**

```bash
docker run -p 8080:8080 hapiproject/hapi:latest
# FHIR base URL: http://localhost:8080/fhir
```

**Step 2: Generate and load Synthea patients**

```bash
# Download Synthea
curl -LO https://github.com/synthetichealth/synthea/releases/latest/download/synthea-with-dependencies.jar

# Generate 20 patients (Massachusetts, for realistic VA-region data)
java -jar synthea-with-dependencies.jar -p 20 Massachusetts

# Load into HAPI FHIR (requires HAPI's $import or individual PUT/POST)
# Simplest approach: use the hapi-fhir-cli upload tool
```

**Step 3: Install and run smart-fetch**

```bash
pipx install smart-fetch

# Export from local HAPI (unauthenticated, dev mode)
smart-fetch export \
  --fhir-url http://localhost:8080/fhir \
  /tmp/hapi-export

# Hydrate (inline note attachments)
smart-fetch hydrate --tasks inline /tmp/hapi-export
```

**Step 4: Run cumulus-etl against the export**

```bash
docker compose run --rm \
  --volume /tmp:/host \
  cumulus-etl init /host/cumulus-output

docker compose run --rm \
  --volume /tmp:/host \
  cumulus-etl etl \
  /host/hapi-export \
  /host/cumulus-output \
  /host/cumulus-phi
```

### Option B: Skip the Live Server (Fastest Path)

For learning cumulus-etl's ETL logic and output format, you do not need a live FHIR server at all. Use the pre-built Synthea NDJSON datasets directly (see Section 5). This skips smart-fetch entirely and lets you focus on understanding the ETL transformation and output.

### Option C: Use the Built-in Test Profile

The repository includes a Docker Compose test profile that uses the repo's own small test dataset:

```bash
cd cumulus-etl   # must have your fork cloned locally (see Section 13)

# Runs ETL against tests/data/simple/ndjson-input/
# Output written to ./example-output/ and ./example-phi-build/
docker compose --profile test run cumulus-etl-test
```

---

## 7. Output to Local MinIO (S3-Compatible)

Cumulus ETL uses boto3 for all S3 operations. MinIO is a drop-in S3-compatible object store, making it the ideal local equivalent of the AWS S3 destination used in production — and directly analogous to med-z1's MinIO setup.

### Step 1: Start MinIO

```bash
docker run -d \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  --name minio \
  quay.io/minio/minio server /data --console-address ":9001"
```

Access the MinIO console at http://localhost:9001. Create a bucket named `cumulus-output`.

### Step 2: Set Environment Variables

```bash
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:9000
```

### Step 3: Initialize and Run ETL to MinIO

```bash
# Initialize the output bucket path
docker compose run --rm \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION \
  -e AWS_ENDPOINT_URL \
  --volume "$(pwd)":/host \
  cumulus-etl init \
  s3://cumulus-output/etl-output/

# Run ETL with S3 output
docker compose run --rm \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION \
  -e AWS_ENDPOINT_URL \
  --volume "$(pwd)":/host \
  cumulus-etl etl \
  /host/sample-bulk-fhir-datasets-10-patients \
  s3://cumulus-output/etl-output/ \
  s3://cumulus-output/phi-build/
```

**Note:** The default `compose.yaml` passes `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, and `AWS_DEFAULT_REGION` through from the host environment automatically. `AWS_ENDPOINT_URL` must be passed explicitly with `-e`.

### Step 4: Query with DuckDB

```python
import duckdb

conn = duckdb.connect()
conn.execute("""
    SET s3_endpoint='localhost:9000';
    SET s3_access_key_id='minioadmin';
    SET s3_secret_access_key='minioadmin';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

conn.sql("SELECT * FROM read_parquet('s3://cumulus-output/etl-output/patient/*.parquet')").show()
```

---

## 8. CLI Reference

The `cumulus-etl` CLI (via Docker Compose) supports the following subcommands:

| Subcommand | Purpose |
|---|---|
| `etl` | Run the main ETL pipeline (also the default when no subcommand is given) |
| `init` | Initialize output folder with empty Delta Lake tables |
| `nlp` | Run NLP-only tasks on already-exported NDJSON |
| `convert` | Convert between output formats |
| `sample` | Sample / subset data |
| `upload-notes` | Upload clinical notes to Label Studio for chart review |

**Key `etl` flags:**

| Flag | Purpose |
|---|---|
| `--task TASK` | Only run specific resource tasks (comma-separated). Use `--task help` for list. |
| `--input-format` | `ndjson` (default) or `i2b2` |
| `--output-format` | `deltalake` (default) or `ndjson` |
| `--batch-size SIZE` | Rows per batch (default: 100,000; use 1,000,000 for 32 GB RAM) |
| `--export-group NAME` | FHIR Group name (required if input lacks `log.ndjson`) |
| `--export-timestamp` | Export timestamp ISO-8601 (required if input lacks `log.ndjson`) |
| `--philter` | Run philter PHI scrubbing on freeform text fields |
| `--errors-to DIR` | Path to write unprocessable resources for inspection |
| `--allow-missing-resources` | Run tasks even if a resource type file is absent |
| `--no-table-optimization` | Skip Delta Lake compaction (faster for large bulk runs) |
| `--comment TEXT` | Add a comment to the run log |
| `--s3-region REGION` | AWS region for S3 paths |
| `--s3-kms-key KEY` | KMS key ARN for S3-side encryption |

**Removed flags (will produce fatal errors in v4.x):**

- `--fhir-url`, `--smart-client-id`, `--smart-key`, `--since`, `--until` → Use `smart-fetch` instead
- `export` and `inline` subcommands → Use `smart-fetch bulk` and `smart-fetch hydrate --tasks inline`

---

## 9. NLP Studies

NLP in cumulus-etl is **study-specific** — each clinical research question is a named study. Studies live in `cumulus_etl/etl/studies/` and are invoked via the `nlp` subcommand.

### Built-in Studies

| Study | NLP Approach | Clinical Domain |
|---|---|---|
| `covid_symptom` | cTAKES + BERT negation | COVID symptom extraction from ED notes |
| `irae` | LLM (GPT-4 class) | Immune-related adverse events |
| `ibd` | LLM (GPT-4 class) | Inflammatory bowel disease |
| `glioma` | LLM (GPT-4 class) | Glioma-related extraction |
| `example` | LLM (template) | Template for building new studies |

### LLM-Based Study Configuration

Newer studies use a `tasks.toml` file and a JSON schema defining the expected LLM response structure. Supported models: `claude-sonnet45`, `gpt4`, `gpt4o`, `gpt5`, `gpt-oss-120b`, `llama4-scout`. Supported providers: `azure`, `bedrock`, `local`.

This architecture is directly analogous to med-z1's LangGraph AI tool framework — worth studying for the prompt engineering and structured output patterns.

### cTAKES-Based (covid_symptom)

Requires a UMLS API key (free registration at https://uts.nlm.nih.gov/). Run via Docker Compose profiles:

```bash
# CPU profile
docker compose --profile covid-symptom up -d
docker compose run cumulus-etl nlp --task covid_symptom ...

# GPU profile (NVIDIA GPU required)
docker compose --profile covid-symptom-gpu up -d
```

---

## 10. Delta Lake Output Structure

After a successful `init` + `etl` run, the output directory contains one Delta Lake table per FHIR resource type:

```
output/
  allergyintolerance/
    _delta_log/           ← Delta transaction log (JSON)
    part-00000-*.parquet  ← Parquet data files
  condition/
  device/
  diagnosticreport/
  documentreference/
  encounter/
  encounter__completion/  ← Encounter completion tracking (ETL-specific)
  episodeofcare/
  immunization/
  location/
  medication/
  medicationdispense/
  medicationrequest/
  observation/
  organization/
  patient/
  practitioner/
  practitionerrole/
  procedure/
  servicerequest/
  specimen/
```

Each folder is a self-contained Delta Lake table. The Parquet files contain de-identified FHIR resources in a flattened/nested format derived from the original FHIR JSON structure.

---

## 11. Project Structure (Key Files)

```
cumulus-etl/
  compose.yaml                      # Primary delivery mechanism (Docker Compose)
  Dockerfile                        # Builds smartonfhir/cumulus-etl image
  pyproject.toml                    # Python package config (Python >= 3.11)
  CONTRIBUTING.md
  cumulus_etl/
    cli.py                          # CLI entry point; defines all subcommands
    deid/                           # De-identification logic
    etl/
      cli.py                        # ETL subcommand implementation
      tasks/
        basic_tasks.py              # Standard FHIR resource task classes (list of supported types)
        task_factory.py             # Task discovery and selection
      studies/                      # NLP study definitions
        covid_symptom/              # cTAKES-based COVID study
        irae/                       # LLM-based adverse events study
        ibd/                        # LLM-based IBD study
        glioma/                     # LLM-based glioma study
        example/
          tasks.toml                # Template study config (start here for new studies)
          age.json                  # Example JSON schema for LLM response
          ndjson/                   # Example input data
    formats/                        # Output format writers (Delta Lake, NDJSON, Parquet)
    loaders/                        # Input format readers (FHIR NDJSON, i2b2)
    nlp/                            # NLP utilities
  docs/
    local-setup.md                  # Official local quickstart guide ← START HERE
    bulk-exports.md
    deid.md                         # De-identification explanation
    performance.md                  # Hardware tuning
    vendors.md                      # EHR vendor tips (Epic, Cerner)
  tests/
    data/simple/ndjson-input/       # Small test dataset used by test Docker profile
```

---

## 12. Development Setup (Contribution)

**Important note from CONTRIBUTING.md:** The project does not currently accept code contributions generated by AI tools due to licensing concerns and reviewer burden. This does not affect using the tool or writing documentation.

Fork the repo and clone your fork first (see Section 13 for the full one-time setup). Once you have your fork cloned locally:

```bash
cd cumulus-etl

# Install Java JDK 21 (required for Delta Lake) — Temurin or Corretto, either works
brew install --cask temurin     # matches the Docker image JRE
# or: brew install --cask corretto21

# Set up Python environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install .[dev,tests]

# Install pre-commit hooks (ruff linting)
pre-commit install

# Verify setup by running the test suite
pytest
```

---

## 13. Open Source Contribution Workflow

This section covers the **fork-based workflow** required for contributing to open source projects where you are not a core maintainer. Fork is the standard approach for all GitHub-hosted open source projects, including cumulus-etl.

### Clone vs. Fork: The Core Distinction

| | Clone only | Fork + Clone |
|---|---|---|
| Creates a local copy | Yes | Yes (clone of your fork) |
| Creates a copy under your GitHub account | No | Yes |
| Push access | Only if you are a project maintainer | Always (to your own fork) |
| How changes reach upstream | Direct push (maintainers only) | Pull Request from your fork |
| **Use when** | Running or studying a project | Contributing back to a project |

**For open source contribution: always use fork.** Cloning the upstream directly is appropriate only for running and studying the code.

### Repository Relationships

```
upstream (smart-on-fhir/cumulus-etl)   ← source of truth; you cannot push here
    ↓  fork  (GitHub UI, one time)
origin (your-username/cumulus-etl)     ← your personal copy on GitHub; you own this
    ↓  clone (one time)
local machine                          ← where you write code and run tests
```

---

### One-Time Setup

Perform these steps once when you begin contributing to cumulus-etl.

**Step 1: Fork on GitHub**

1. Log in to GitHub
2. Go to https://github.com/smart-on-fhir/cumulus-etl
3. Click the **Fork** button (top right corner)
4. Accept the defaults and click **Create fork**

GitHub creates `https://github.com/your-username/cumulus-etl` — your personal copy of the repository.

**Step 2: Clone your fork locally**

Clone *your fork*, not the upstream. GitHub sets your fork as the `origin` remote automatically.

```bash
git clone https://github.com/your-username/cumulus-etl.git
cd cumulus-etl
```

**Step 3: Add upstream as a second remote**

This connects your local clone back to the original project so you can pull in future updates as the project evolves. This step is commonly missed by first-time contributors.

```bash
git remote add upstream https://github.com/smart-on-fhir/cumulus-etl.git
```

Verify both remotes are configured:

```bash
git remote -v
# origin    https://github.com/your-username/cumulus-etl.git (fetch)
# origin    https://github.com/your-username/cumulus-etl.git (push)
# upstream  https://github.com/smart-on-fhir/cumulus-etl.git (fetch)
# upstream  https://github.com/smart-on-fhir/cumulus-etl.git (push)
```

**Step 4: Complete the development environment setup**

Follow Section 12 (Development Setup) to install Java, Python dependencies, and pre-commit hooks.

---

### Per-Contribution Workflow

Repeat these steps for every new contribution — bug fix, documentation update, or new feature.

**Step 1: Sync your main branch with upstream**

Always do this before starting a new contribution. It ensures you branch from the latest state of the project, not a stale copy.

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main       # keep your fork's main in sync on GitHub too
```

**Step 2: Create a feature branch**

Never commit directly to `main`. All work happens on a dedicated branch. Use a short, descriptive name.

```bash
# Examples:
git checkout -b docs-va-fhir-vendor-tips
git checkout -b fix-encounter-task-missing-field
git checkout -b add-test-for-immunization-task
```

**Step 3: Do your work and test**

Make your changes, then run the test suite to confirm nothing is broken:

```bash
# Run the full pytest suite
pytest

# Run a specific test file
pytest tests/test_etl.py

# Run the Docker end-to-end test profile
docker compose --profile test run cumulus-etl-test
```

Pre-commit hooks (installed in Section 12) run `ruff` automatically on each commit and will reject code that fails linting.

**Step 4: Commit your changes**

```bash
git add path/to/changed-file.py    # prefer named files over git add -A
git commit -m "Add VA Lighthouse endpoint tips to vendors.md"
```

Write commit messages in the present tense. Describe *what* the change does and *why*, not *how* the code works.

**Step 5: Push your branch to your fork**

```bash
git push origin docs-va-fhir-vendor-tips
```

**Step 6: Open a Pull Request on GitHub**

1. Go to `https://github.com/your-username/cumulus-etl`
2. GitHub displays a **"Compare & pull request"** banner — click it
3. Confirm the PR is targeting the correct repositories and branches:
   - **base repository:** `smart-on-fhir/cumulus-etl`  ← upstream
   - **base branch:** `main`
   - **head repository:** `your-username/cumulus-etl`   ← your fork
   - **compare:** `docs-va-fhir-vendor-tips`             ← your branch
4. Write a clear title and description explaining what the change does and why
5. Click **Create pull request**

**Step 7: Respond to review feedback**

Maintainers may request changes. Push additional commits to the same branch — the PR updates automatically:

```bash
# Address feedback, then:
git add path/to/file.py
git commit -m "Address review: clarify VA Lighthouse base URL format"
git push origin docs-va-fhir-vendor-tips
```

**Step 8: After merge — clean up**

Once your PR is merged, delete the feature branch and re-sync your main:

```bash
# Delete the branch on your fork (GitHub remote)
git push origin --delete docs-va-fhir-vendor-tips

# Delete the local branch
git branch -d docs-va-fhir-vendor-tips

# Sync your local main with the newly merged changes
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

---

### Keeping an In-Progress Branch Current

If upstream `main` advances while you have work in progress, use `rebase` to replay your commits on top of the latest upstream. This produces a cleaner history than merging.

```bash
git checkout docs-va-fhir-vendor-tips
git fetch upstream
git rebase upstream/main
```

If Git pauses with conflicts, resolve each conflicting file, then continue:

```bash
# After resolving conflicts in each file:
git add path/to/resolved-file.py
git rebase --continue
```

After a rebase, force-push your branch. Use `--force-with-lease` instead of `--force` — it fails safely if someone else has pushed to your branch since your last pull:

```bash
git push origin docs-va-fhir-vendor-tips --force-with-lease
```

---

### Contribution Strategy for cumulus-etl

**Before starting any contribution:**

1. Read `CONTRIBUTING.md` in the repo root — the team documents their specific expectations there
2. Browse open issues for `good first issue` or `help wanted` labels
3. Comment on the issue before starting work (e.g., "I'd like to take a look at this") to signal intent and avoid duplicate effort
4. Wait for a maintainer acknowledgment before investing significant time

**AI-generated code policy:** The cumulus-etl `CONTRIBUTING.md` explicitly states the project does not currently accept code contributions generated by AI tools, due to licensing concerns and reviewer burden. This applies to code contributions. Documentation and test contributions that you write yourself are appropriate.

**High-value first contribution ideas:**

| Contribution | Type | Why It Fits |
|---|---|---|
| Add VA FHIR / VA Lighthouse endpoint tips to `docs/vendors.md` | Documentation | VA context is absent from their vendor docs; directly leverages your med-z1 work |
| Write a test case for a FHIR resource type | Testing | Well-scoped, low risk, demonstrates code familiarity |
| Fix a typo or unclear passage in existing documentation | Documentation | Smallest possible PR; good for establishing rapport with maintainers |
| Report a well-documented bug via GitHub Issues | Issue report | Valued contribution that does not require a PR |

---

## 14. Mini-Plan: Getting Started

A suggested learning progression, roughly one session per step.

### Step 1 — Read the Official Docs (30 min)

Start with the official local setup guide:
- https://docs.smarthealthit.org/cumulus/etl/ (overview)
- `docs/local-setup.md` in your local fork (the quickstart)
- `docs/deid.md` (understand the de-identification approach)

### Step 2 — First Run with Synthea Data (1–2 hours)

Follow Section 5 of this guide:
1. Fork the repo on GitHub and clone your fork (see Section 13)
2. Download the 10-patient Synthea dataset
3. Run `init` then `etl` using Docker
4. Inspect the output Parquet files with DuckDB or pandas
5. Compare a raw input NDJSON record to its de-identified output record — understand exactly what fields are dropped, hashed, and truncated

**Goal:** Understand what the tool produces and how de-identification works in practice.

### Step 3 — Wire to Local MinIO (1–2 hours)

Follow Section 7 of this guide:
1. Start a local MinIO instance (same Docker image med-z1 uses)
2. Run the ETL with `s3://` output paths pointing to MinIO
3. Query the output from MinIO using DuckDB

**Goal:** Close the loop between cumulus-etl's output format and med-z1's existing MinIO/Parquet medallion architecture. The data model is now real to you.

### Step 4 — Trace the Codebase (2–3 hours)

With Python dev setup from Section 12:
1. Read `cumulus_etl/etl/tasks/basic_tasks.py` — understand how FHIR resources are mapped to output schemas
2. Read `cumulus_etl/deid/` — understand the de-identification pipeline implementation
3. Run `pytest` to see how the test suite is structured
4. Read `cumulus_etl/etl/studies/example/tasks.toml` — understand how LLM-based NLP studies are configured

**Goal:** Understand the Python architecture well enough to trace how a Patient NDJSON record flows from input to de-identified Delta Lake output.

### Step 5 — Local FHIR Server Workflow (2–4 hours)

Follow Section 6 of this guide:
1. Start a HAPI FHIR server locally with Docker
2. Install `smart-fetch` via pipx
3. Load Synthea-generated patients into HAPI FHIR
4. Use `smart-fetch export` to produce a bulk FHIR export
5. Feed the export to cumulus-etl

**Goal:** Experience the full Extract → Transform → Load pipeline end-to-end, using the same approach you would use against a real Oracle Health or VA FHIR endpoint.

### Step 6 — Study an NLP Example (Optional, 2–3 hours)

1. Read `cumulus_etl/etl/studies/example/tasks.toml` and `age.json`
2. Read `docs/` for any study-related documentation
3. Trace through the `irae` study (LLM-based) to understand how prompts and structured output schemas are defined
4. Compare to med-z1's LangGraph tool definitions in `ai/`

**Goal:** Understand how a research study is defined and how the LLM prompt engineering patterns compare to what you've built in med-z1's AI insight layer.

### Step 7 — Make Your First Contribution

Follow Section 13 (Open Source Contribution Workflow):
1. Fork the repo on GitHub and configure the `upstream` remote
2. Browse open issues for `good first issue` labels
3. Comment on the issue to signal your intent
4. Create a feature branch, make your change, run `pytest`
5. Push to your fork and open a Pull Request

**Goal:** Complete the full fork → branch → PR cycle at least once. A documentation improvement (e.g., adding VA Lighthouse tips to `docs/vendors.md`) is an ideal first PR.

---

## 15. Environment Variable Reference

```bash
# AWS / MinIO credentials (passed through from host by compose.yaml)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
AWS_DEFAULT_REGION=us-east-1

# Custom S3 endpoint (MinIO; must be passed explicitly with -e)
AWS_ENDPOINT_URL=http://localhost:9000

# UMLS API key (required for covid_symptom cTAKES study only)
# Register free at https://uts.nlm.nih.gov/
UMLS_API_KEY=

# Azure OpenAI (for LLM-based NLP studies using Azure provider)
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
```

---

## 16. References

| Resource | URL |
|---|---|
| Official ETL Docs | https://docs.smarthealthit.org/cumulus/etl/ |
| GitHub: cumulus-etl | https://github.com/smart-on-fhir/cumulus-etl |
| GitHub: smart-fetch | https://github.com/smart-on-fhir/smart-fetch |
| GitHub: cumulus-library | https://github.com/smart-on-fhir/cumulus-library |
| Sample FHIR Datasets (Synthea) | https://github.com/smart-on-fhir/sample-bulk-fhir-datasets |
| Cumulus Platform Overview | https://smarthealthit.org/cumulus/ |
| PMC Paper: Cumulus Federated EHR Platform | https://pmc.ncbi.nlm.nih.gov/articles/PMC10871375/ |
| HAPI FHIR Server | https://hapifhir.io/ |
| Synthea Patient Generator | https://github.com/synthetichealth/synthea |
| UMLS API Key Registration | https://uts.nlm.nih.gov/ |
| HL7 Bulk Data Access Spec | https://hl7.org/fhir/uv/bulkdata/ |
