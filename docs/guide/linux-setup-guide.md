# Med-Z1 Setup Guide for Linux

This guide provides instructions for installing, configuring, and running the **med-z1** application on a development machine running the Linux operating system. It is targeted for pop!_OS, but should be useful for other Linux variants.  

For the initial version of this guide, I will sort of run through an install using a _chain of thought_ approach, and will document as I go.

**Prerequistite:** This application is designed to run using Python version 3.11 on macOS machines and version 3.10 on Linux based machines. Higher versions of Python may have incompatibility issues witih some of the supporting dependencies, such as numpy, pandas, and polars.

## Clone med-z1 Repo to Local Dev Machine

Create and CD to the folder where you would like to clone the med-z1 repo, e.g.  
```bash
mkdir -p ~/swdev/med
cd ~/swdev/med
```

Go to the GitHub med-z1 repo  
https://github.com/cps-med/med-z1  

Click the `Code` button and copy the HTTPS URL  
https://github.com/cps-med/med-z1.git  

Ensure that you are in the target folder where you would like to clone the repo, e.g.:
```bash
~/swdev/med
```

Run the git clone command from the terminal command line  
```bash
git clone https://github.com/cps-med/med-z1.git
```

CD to the med-z1 project folder  
```bash
cd med-z1
```

Take a look at the project structure from the terminal:  
```bash
# standard bash command
ls -al

# corutils + alias command
ll

# tree utility
tree -L 1
tree -d -L 2
```

## Add and Configure .env File

The med-z1 applications uses a project-wide .env file for managing secrets and other sensitive information. Ask a peer developer for a copy that you can place in the med-z1 root directory.  

Place .env in the project root folder, or copy/paste contents into .env file
```bash
cp .env ~/swdev/med/med-z1/
```

## Create Python Virtual Environment

The med-z1 application uses a single, shared Python virtual environment. This environment is not under version control, so you will need to create the environmenet locally within your development project using the `requirements.txt` file. This will install all required dependencies into your local environment.  

Note that for performance and compatibility reasons, med-z1 expects Python version 3.11 on macOS and version 3.10 (or 3.11) on Linux.

Create virtual environment (Python v3.10 or v3.11)
```bash
python3 -m venv .venv
```

Activate virtual environment:
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

To ensure compatibility between macOS and Linux, several packages use the `>=` operator, as opposed to `==` for version numbers. This results in the proper versions being downloaded for the respective runtime environments. Plus, one of the original packages was removed from requirements.txt, but will be installed based on a parent dependency.  

The specific items that use this notation are listed below:  

- numpy>=2.0.0
- pandas>=2.0.0
- polars>=1.0.0
- pydantic==2.12.5 (keep)
- pydantic_core==2.41.5 (remove)

To deactivate a Pythone virtual environment:
```bash
deactivate
```

## Install and Run Docker Images

The **med-z1** application uses three core services that run within Docker container images: Microsoft SQL Server 2019, PostgreSQL 16, and MinIO. On macOS, these services are managed using Docker Desktop; however, there are significant performance gains on Linux by managing these services natively through the command line.  

The instructions below are for Docker **native engine** installation.  

Install Docker components
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Run docker-compose.yaml script (from project root directory)
```bash
docker compose up -d
```

Other useful Docker CLI commands:
```bash

# List running processes
docker ps
or
docker ps -q

# Stop Everything
docker stop $(docker ps -q)

# Remove specific containers that are no longer needed
docker ps -a
docker rm <container_name_or_id>

# Remove ALL stopped containers
docker rm $(docker ps -aq)

# Remove Images (Free up Disk Space)
docker images
docker rmi <image_id_or_name>

# The "Nuclear" Option (full environment refresh)
# Delete all stopped containers, unused networks, and dangling images
docker system prune -a

# Verify that Docker Services are running
docker logs sqlserver2019
docker logs postgres16
docker logs med-insight-minio
```

## PostgreSQL Database Setup

Before running any ETL pipelines or setting up user authentication, you must create the `medz1` database.  

**Creation:**  
```bash
# Connect to the default 'postgres' database
docker exec -it postgres16 psql -U postgres -d postgres

# Create the medz1 database from psql prompt
CREATE DATABASE medz1;

# Verify creation
\l

# Exit
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

## PostgreSQL User Authentication Setup

This section guides you through setting up the user authentication schema and tables within the PostgreSQL `medz1` database and populating these tables with mock user data.

Create Authentication Schema and Tables
```bash
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_auth_tables.sql
```

Expected Output
```text
CREATE SCHEMA
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
...
GRANT
               status
-----------------------------------------
 Authentication tables created successfully.
(1 row)
```

Verify that schema and tables were created
```bash
# Start postgres with medz1 database
docker exec -it postgres16 psql -U postgres -d medz1

# Run the following from the psql promt
-- List all schemas
\dn

-- List all tables in the auth schema
\dt auth.*

-- View auth.users table structure
\d auth.users

-- View auth.sessions table structure
\d auth.sessions

-- View auth.audit_logs table structure
\d auth.audit_logs

-- Exit psql
\q
```

Load Mock User Data
```bash
docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql
```

Expected Output:
```text
TRUNCATE TABLE
TRUNCATE TABLE
DELETE 0
INSERT 0 7
              email          |       display_name             | home_site_sta3n | is_active
-----------------------------+--------------------------------+-----------------+-----------
 clinician.alpha@va.gov      | Dr. Alice Anderson, MD         |             508 | t
 clinician.bravo@va.gov      | Dr. Bob Brown, DO              |             648 | t
 clinician.charlie@va.gov    | Nurse Carol Chen, RN           |             663 | t
 clinician.delta@va.gov      | Dr. David Davis, MD            |             509 | t
 clinician.echo@va.gov       | Pharmacist Emma Evans, PharmD  |             531 | t
 clinician.foxtrot@va.gov    | Dr. Frank Foster, MD           |             516 | t
 clinician.golf@va.gov       | Dr. Grace Green, MD            |             552 | t
(7 rows)

       summary
---------------------
 Inserted 7 mock users
(1 row)
```

Verify Mock Users Were Loaded via SQL Query
```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT email, display_name, home_site_sta3n, is_active FROM auth.users ORDER BY email;"
```

Expected Output:
```text
Table showing user list
(7 rows)
```

You can now test the authentication system by logging into the med-z1 application.

- Start the FastAPI application using Uvicorn
- Navigate to `http://127.0.0.1:8000/`
- You should be redirected to the login page where you can use these credentials


Test Credentials (all users share same password)
```text
Email: clinician.alpha@va.gov
Password: VaDemo2025!
```

## MinIO Setup and Bucket Creation

The med-z1 application uses MinIO as an S3-compatible object storage system for the data lake. MinIO must be properly configured before running ETL pipelines, as the pipelines write and read Parquet files from MinIO.  

The MinIO service should already be running from the `docker compose up -d` command executed earlier.  

Verify the container status
```bash
# Check that MinIO container is running
docker ps | grep minio

# View MinIO logs
docker logs med-insight-minio
```

Expected output should show the MinIO container is running on port 9000 (API) and port 9001 (console).

MinIO provides a web-based console for managing buckets and objects.

Open your web browser and navigate to:
```
http://localhost:9001
```

Login with credentials from your `.env` file:
```
Username: admin
Password: {admin password}
```

The ETL pipelines expect a bucket named `med-z1` (or name specified in `.env` file as `MINIO_BUCKET_NAME`).

Create the med-z1 bucket via web console
```text
2. Click "Create Bucket" button
3. Enter bucket name: med-z1
4. Click "Create Bucket"
5. Verify the bucket appears in the bucket list
```

**Test MinIO Connectivity**
Use the provided test script to verify Python can connect to MinIO and perform basic read/write operations:

```bash
# Ensure you're in the project root and virtual environment is activated
cd ~/swdev/med/med-z1
source .venv/bin/activate

# Run MinIO connectivity test (using -m flag to run as module)
python -m scripts.minio_test
```

Expected output:
```text
VERIFYING MINIO...

✓ Connected to MinIO at localhost:9000
✓ Using bucket: med-z1
✓ Test passed: 3 rows
```

## Install SQL Server Command-Line Tools (Recommended)

For better developer experience, install Microsoft SQL Server command-line tools natively on your Linux machine. This allows you to run `sqlcmd` directly from your host terminal without using `docker exec`.

### Install mssql-tools18 on Pop!_OS/Ubuntu

```bash
# Import the public repository GPG keys
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc

# Register the Microsoft Ubuntu repository
# For Pop!_OS 22.04 (based on Ubuntu 22.04):
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Update package lists
sudo apt-get update

# Install mssql-tools18 (includes sqlcmd and bcp)
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools18 unixodbc-dev
```

**Note:** The `ACCEPT_EULA=Y` environment variable accepts the Microsoft EULA automatically. You can also install interactively without this flag.

### Add sqlcmd to PATH

```bash
# Add to your ~/.bashrc
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc

# Reload your shell configuration
source ~/.bashrc

# Verify installation
sqlcmd -?
```

Expected output: You should see the sqlcmd help text showing version 18.x.

### Test Connection to SQL Server

```bash
# Test connection to your Docker SQL Server instance
sqlcmd -S 127.0.0.1,1433 -U sa -P 'MyS3cur3P@ssw0rd' -C -Q "SELECT @@VERSION"
```

**Note:** The `-C` flag is required for sqlcmd 18+ to trust the server certificate.

Expected output: SQL Server version information.

## Create and Populate SQL Server Mock Data

The **med-z1** application uses Microsoft SQL Server 2019 to simulate the VA Corporate Data Warehouse (CDW) for local development. The mock CDW contains synthetic patient data across multiple clinical domains including demographics, vitals, medications, allergies, encounters, and laboratory results.

This section guides you through creating the **CDWWork** database schema and populating it with mock patient data.

### Overview of CDWWork Database

The CDWWork database simulates VistA-sourced data with the following major schemas:

- **Dim** - Dimension tables (facilities, states, flags, drug definitions, etc.)
- **SPatient** - Patient demographics, addresses, insurance, flags
- **SStaff** - Staff and provider information
- **Vital** - Vital signs measurements
- **Allergy** - Patient allergies and reactions
- **RxOut** - Outpatient medications and prescriptions
- **BCMA** - Bar Code Medication Administration records
- **Inpat** - Inpatient admissions and encounters
- **Chem** - Laboratory chemistry results

### Verify SQL Server Container is Running

```bash
# Check that SQL Server container is running
docker ps | grep sqlserver

# View SQL Server logs (should show "SQL Server is now ready for client connections")
docker logs sqlserver2019 | tail -20
```

### Create Database and Tables

The project provides `_master.sql` scripts in the `create/` folder that orchestrate the creation of all tables in the correct dependency order.

#### Option 1: Using Shell Script with .env Password (Recommended)

```bash
# Navigate to the create scripts directory
cd ~/swdev/med/med-z1/mock/sql-server/cdwwork/create

# Run the shell script (sources password from .env)
./_master.sh
```

The `_master.sh` script loads the `CDWWORK_DB_PASSWORD` environment variable from your `.env` file and executes the `_master.sql` script.

#### Option 2: Direct sqlcmd Command

```bash
# Navigate to the create scripts directory
cd ~/swdev/med/med-z1/mock/sql-server/cdwwork/create

# Run sqlcmd directly with password
sqlcmd -S 127.0.0.1,1433 -U sa -P 'MyS3cur3P@ssw0rd' -C -i _master.sql
```

Replace `'MyS3cur3P@ssw0rd'` with your actual SQL Server password from the `.env` file.

#### Option 3: Using VS Code with mssql Extension

These scripts can also be run using Visual Studio Code with the Microsoft SQL Server (mssql) extension.

1. Ensure you have a connection profile configured:
   ```text
   Profile Name: sqlserver19-docker
   Server name: 127.0.0.1,1433
   Trust server certificate: yes
   Authentication type: SQL Login
   User name: sa
   Password: ************
   Save Password: yes
   ```

2. Navigate to `mock/sql-server/cdwwork/create/`
3. Open `_master.sql`
4. Right-click in editor and select "Execute Query"

**Note:** The `-C` flag in sqlcmd (or "Trust server certificate" in VS Code) is required for SQL Server 2019+.

Expected output will show table creation messages for all schemas and tables. The script will:
1. Drop and recreate the CDWWork database
2. Create all required schemas (Dim, SPatient, SStaff, Vital, Allergy, RxOut, BCMA, Inpat, Chem)
3. Create all dimension tables
4. Create all fact/transaction tables

### Populate Mock Data

After creating the database structure, populate the tables with synthetic patient data.

#### Option 1: Using Shell Script with .env Password (Recommended)

```bash
# Navigate to the insert scripts directory
cd ~/swdev/med/med-z1/mock/sql-server/cdwwork/insert

# Run the shell script (sources password from .env)
./_master.sh
```

#### Option 2: Direct sqlcmd Command

```bash
# Navigate to the insert scripts directory
cd ~/swdev/med/med-z1/mock/sql-server/cdwwork/insert

# Run sqlcmd directly with password
sqlcmd -S 127.0.0.1,1433 -U sa -P 'MyS3cur3P@ssw0rd' -C -i _master.sql
```

#### Option 3: Using VS Code with mssql Extension

1. Navigate to `mock/sql-server/cdwwork/insert/`
2. Open `_master.sql`
3. Right-click in editor and select "Execute Query"

Expected output will show INSERT confirmation messages with row counts. The script populates data for approximately 15 synthetic patients across all clinical domains.

### Verify Database Creation

You can verify that the database and tables were created using one of several methods:

#### Verification via sqlcmd (Command Line)

```bash
# Connect to SQL Server interactively
sqlcmd -S 127.0.0.1,1433 -U sa -P 'MyS3cur3P@ssw0rd' -C
```

From the sqlcmd prompt, run verification queries:

```sql
-- List all databases (should see CDWWork)
SELECT name FROM sys.databases;
GO

-- Switch to CDWWork database
USE CDWWork;
GO

-- List all schemas
SELECT name FROM sys.schemas WHERE name IN ('Dim', 'SPatient', 'Vital', 'Allergy', 'RxOut', 'BCMA', 'Inpat', 'Chem');
GO

-- Count patients in SPatient.SPatient
SELECT COUNT(*) AS patient_count FROM SPatient.SPatient;
GO

-- Count vitals records
SELECT COUNT(*) AS vitals_count FROM Vital.VitalSign;
GO

-- Count medications records
SELECT COUNT(*) AS meds_count FROM RxOut.RxOutpat;
GO

-- Count lab results
SELECT COUNT(*) AS labs_count FROM Chem.LabChem;
GO

-- View sample patient data
SELECT TOP 5 PatientSID, PatientICN, PatientName, BirthDateTime, GenderName
FROM SPatient.SPatient;
GO

-- Exit sqlcmd
EXIT
```

#### Verification via VS Code mssql Extension

1. Open Command Palette (Ctrl+Shift+P)
2. Select "MSSQL: Connect" using your `sqlserver19-docker` profile
3. Open a new SQL query window
4. Run verification queries (same as above, without `GO` statements)

Expected row counts (approximate):
- Patients: 15-20
- Vitals: 200+
- Medications: 100+
- Allergies: 30+
- Encounters: 20+
- Labs: 50+

### Troubleshooting

**Issue: "sqlcmd: command not found"**
- Verify sqlcmd is installed: `which sqlcmd`
- Ensure PATH includes `/opt/mssql-tools18/bin`
- Reload your shell: `source ~/.bashrc`
- If not installed, see "Install SQL Server Command-Line Tools" section above

**Issue: "Login failed for user 'sa'"**
- Verify password matches the one in your `.env` file (`CDWWORK_DB_PASSWORD`)
- Check the password in `docker-compose.yaml` (typically `MyS3cur3P@ssw0rd`)
- Ensure the SQL Server container is running: `docker ps | grep sqlserver`

**Issue: "Cannot open server '127.0.0.1,1433'"**
- Verify SQL Server container is running: `docker ps | grep sqlserver2019`
- Check container logs: `docker logs sqlserver2019 | tail -20`
- Verify port mapping: `docker port sqlserver2019`

**Issue: "Certificate validation failed"**
- Always use `-C` flag with sqlcmd 18+ to trust self-signed certificates
- Example: `sqlcmd -S 127.0.0.1,1433 -U sa -P 'password' -C`

**Issue: "Incorrect syntax near ':r'" when running _master.sql**
- The `:r` command requires you to run sqlcmd from the same directory as the script
- Always `cd` to the `create/` or `insert/` directory before running `sqlcmd -i _master.sql`

**Issue: Tables already exist errors**
- The master create script drops and recreates the database, so this shouldn't occur
- If running individual scripts, manually drop tables first or truncate data

**Issue: Foreign key constraint errors during INSERT**
- Ensure dimension tables are populated before fact tables
- The master insert script handles dependency order automatically
- If running individual scripts, follow this order: Dim tables → SPatient → SStaff → clinical domain tables

## Run ETL Data Pipelines

The **med-z1** ETL (Extract, Transform, Load) pipelines transform raw data from the SQL Server mock CDW into curated, query-optimized data for the PostgreSQL serving database. The pipelines follow the **medallion architecture** with three layers stored as Parquet files in MinIO, followed by loading into PostgreSQL.

**Pipeline Flow:**
1. **Bronze:** Extract raw data from SQL Server → Write Parquet files to MinIO
2. **Silver:** Read Bronze Parquet → Clean, harmonize, unify → Write Silver Parquet to MinIO
3. **Gold:** Read Silver Parquet → Optimize for queries → Write Gold Parquet to MinIO
4. **Load:** Read Gold Parquet → Insert into PostgreSQL serving database

### Prerequisites Checklist

Before running ETL pipelines, ensure the following are complete:

- ✅ PostgreSQL container running with `medz1` database created
- ✅ PostgreSQL auth schema and tables created (from previous section)
- ✅ MinIO container running with `med-z1` bucket created
- ✅ MinIO connectivity tested successfully (`python -m scripts.minio_test`)
- ✅ SQL Server container running with CDWWork database populated
- ✅ Python virtual environment activated (`source .venv/bin/activate`)

### Create PostgreSQL Clinical Domain Schemas

Before loading data, create the PostgreSQL table schemas for each clinical domain:

```bash
# Ensure you're in project root with virtual environment activated
cd ~/swdev/med/med-z1
source .venv/bin/activate

# Create patient demographics tables
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/patient_demographics.sql

# Create vitals table
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_vitals_table.sql

# Create allergies tables
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_allergies_tables.sql

# Create medications tables
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_medications_tables.sql

# Create patient flags tables
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_flags_tables.sql

# Create encounters table
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_encounters_table.sql

# Create laboratory results table
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_patient_labs_table.sql
```

Verify schemas were created:
```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt clinical.*"
```

Expected output should list tables: `patient_demographics`, `patient_vitals`, `patient_allergies`, `patient_allergy_reactions`, `patient_medications`, `patient_flags`, `patient_flag_assignments`, `patient_encounters`, `patient_labs`

### Running ETL Pipelines by Domain

Each clinical domain has a complete pipeline (Bronze → Silver → Gold → Load). Run pipelines in the order shown below to respect data dependencies.

All ETL scripts are run as Python modules from the project root:

```bash
# Ensure you're in project root
cd ~/swdev/med/med-z1
source .venv/bin/activate
```

#### 1. Patient Demographics Pipeline

```bash
# Bronze: Extract raw patient data from SQL Server
python -m etl.bronze_patient
python -m etl.bronze_patient_address
python -m etl.bronze_patient_disability
python -m etl.bronze_patient_insurance
python -m etl.bronze_insurance_company

# Silver: Clean and harmonize
python -m etl.silver_patient

# Gold: Create query-optimized demographics
python -m etl.gold_patient

# Load: Insert into PostgreSQL
python -m etl.load_postgres_patient
```

#### 2. Vitals Pipeline

```bash
# Bronze: Extract vitals from SQL Server
python -m etl.bronze_vitals

# Silver: Clean and harmonize
python -m etl.silver_vitals

# Gold: Create query-optimized vitals
python -m etl.gold_vitals

# Load: Insert into PostgreSQL
python -m etl.load_vitals
```

#### 3. Allergies Pipeline

```bash
# Bronze: Extract allergies and related dimension data
python -m etl.bronze_allergen
python -m etl.bronze_reaction
python -m etl.bronze_allergy_severity
python -m etl.bronze_patient_allergy
python -m etl.bronze_patient_allergy_reaction

# Silver: Clean and harmonize
python -m etl.silver_patient_allergies

# Gold: Create query-optimized allergies
python -m etl.gold_patient_allergies

# Load: Insert into PostgreSQL
python -m etl.load_patient_allergies
```

#### 4. Medications Pipeline

```bash
# Bronze: Extract medications from SQL Server
python -m etl.bronze_medications

# Silver: Clean and harmonize
python -m etl.silver_medications

# Gold: Create query-optimized medications
python -m etl.gold_patient_medications

# Load: Insert into PostgreSQL
python -m etl.load_medications
```

#### 5. Patient Flags Pipeline

```bash
# Bronze: Extract patient flags
python -m etl.bronze_patient_flags

# Silver: Clean and harmonize
python -m etl.silver_patient_flags

# Gold: Create query-optimized flags
python -m etl.gold_patient_flags

# Load: Insert into PostgreSQL
python -m etl.load_patient_flags
```

#### 6. Encounters (Inpatient) Pipeline

```bash
# Bronze: Extract inpatient encounters
python -m etl.bronze_inpatient

# Silver: Clean and harmonize
python -m etl.silver_inpatient

# Gold: Create query-optimized encounters
python -m etl.gold_inpatient

# Load: Insert into PostgreSQL
python -m etl.load_encounters
```

#### 7. Laboratory Results Pipeline

```bash
# Bronze: Extract lab results
python -m etl.bronze_labs

# Silver: Clean and harmonize
python -m etl.silver_labs

# Gold: Create query-optimized labs
python -m etl.gold_labs

# Load: Insert into PostgreSQL
python -m etl.load_labs
```

### Verify ETL Pipeline Results

After running pipelines, verify data was successfully loaded into PostgreSQL:

```bash
# Check row counts for all clinical domain tables
docker exec -it postgres16 psql -U postgres -d medz1 -c "
SELECT
  'patient_demographics' AS table_name, COUNT(*) AS row_count FROM clinical.patient_demographics
UNION ALL
SELECT 'patient_vitals', COUNT(*) FROM clinical.patient_vitals
UNION ALL
SELECT 'patient_allergies', COUNT(*) FROM clinical.patient_allergies
UNION ALL
SELECT 'patient_medications', COUNT(*) FROM clinical.patient_medications
UNION ALL
SELECT 'patient_flags', COUNT(*) FROM clinical.patient_flags
UNION ALL
SELECT 'patient_flag_assignments', COUNT(*) FROM clinical.patient_flag_assignments
UNION ALL
SELECT 'patient_encounters', COUNT(*) FROM clinical.patient_encounters
UNION ALL
SELECT 'patient_labs', COUNT(*) FROM clinical.patient_labs
ORDER BY table_name;
"
```

Expected row counts (approximate):
```
         table_name         | row_count
----------------------------+-----------
 patient_allergies          |        30
 patient_demographics       |        15
 patient_encounters         |        20
 patient_flag_assignments   |        12
 patient_flags              |         8
 patient_labs               |        58
 patient_medications        |       100
 patient_vitals             |       200
```

### Verify MinIO Parquet Files

You can also verify that Parquet files were created in MinIO:

**Via MinIO Web Console:**
1. Navigate to http://localhost:9001
2. Login (admin / admin#123#2025)
3. Click "Buckets" → "med-z1"
4. Browse folders: `bronze/`, `silver/`, `gold/`
5. You should see Parquet files organized by domain

**Via Python Script:**
```bash
# List all objects in MinIO bucket
python -c "
from lake.minio_client import MinIOClient
client = MinIOClient()
# List all objects (requires adding a list method or using boto3 directly)
import boto3
s3 = client.s3_client
response = s3.list_objects_v2(Bucket='med-z1', Prefix='bronze/')
for obj in response.get('Contents', []):
    print(obj['Key'])
"
```

### Running All Pipelines with a Shell Script (Optional)

For convenience, you can create a shell script to run all ETL pipelines sequentially:

```bash
# Create a script: scripts/run_all_etl.sh
cat > scripts/run_all_etl.sh << 'EOF'
#!/bin/bash
# Run all ETL pipelines for med-z1

set -e  # Exit on error

echo "Starting ETL pipelines..."

# Patient Demographics
echo ">>> Running Patient Demographics pipeline..."
python -m etl.bronze_patient
python -m etl.bronze_patient_address
python -m etl.bronze_patient_disability
python -m etl.bronze_patient_insurance
python -m etl.bronze_insurance_company
python -m etl.silver_patient
python -m etl.gold_patient
python -m etl.load_postgres_patient

# Vitals
echo ">>> Running Vitals pipeline..."
python -m etl.bronze_vitals
python -m etl.silver_vitals
python -m etl.gold_vitals
python -m etl.load_vitals

# Allergies
echo ">>> Running Allergies pipeline..."
python -m etl.bronze_allergen
python -m etl.bronze_reaction
python -m etl.bronze_allergy_severity
python -m etl.bronze_patient_allergy
python -m etl.bronze_patient_allergy_reaction
python -m etl.silver_patient_allergies
python -m etl.gold_patient_allergies
python -m etl.load_patient_allergies

# Medications
echo ">>> Running Medications pipeline..."
python -m etl.bronze_medications
python -m etl.silver_medications
python -m etl.gold_patient_medications
python -m etl.load_medications

# Patient Flags
echo ">>> Running Patient Flags pipeline..."
python -m etl.bronze_patient_flags
python -m etl.silver_patient_flags
python -m etl.gold_patient_flags
python -m etl.load_patient_flags

# Encounters
echo ">>> Running Encounters pipeline..."
python -m etl.bronze_inpatient
python -m etl.silver_inpatient
python -m etl.gold_inpatient
python -m etl.load_encounters

# Laboratory Results
echo ">>> Running Laboratory Results pipeline..."
python -m etl.bronze_labs
python -m etl.silver_labs
python -m etl.gold_labs
python -m etl.load_labs

echo "All ETL pipelines completed successfully!"
EOF

# Make it executable
chmod +x scripts/run_all_etl.sh

# Run it
./scripts/run_all_etl.sh
```

### Troubleshooting ETL Issues

**Issue: "Connection refused" to SQL Server or PostgreSQL**
- Verify containers are running: `docker ps`
- Check `.env` file has correct connection strings
- Verify network connectivity: `docker network ls`

**Issue: "Bucket does not exist" error**
- Verify MinIO bucket exists: check web console at http://localhost:9001
- Verify bucket name in `.env` matches the bucket you created

**Issue: "Table does not exist" in PostgreSQL**
- Ensure you ran all DDL scripts in `db/ddl/` before running load scripts
- Check table exists: `docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt clinical.*"`

**Issue: ETL script fails with "column does not exist"**
- This typically means the SQL Server mock data schema doesn't match what the ETL script expects
- Check that you ran the latest `_master.sql` scripts for both CREATE and INSERT
- Verify the source table structure in SQL Server matches the Bronze extraction query

**Issue: Data loaded but row counts are zero**
- Check SQL Server has data: `docker exec -it sqlserver2019 /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'MyS3cur3P@ssw0rd' -C -Q "USE CDWWork; SELECT COUNT(*) FROM SPatient.SPatient;"`
- Check MinIO has Parquet files via web console
- Review ETL script logs for errors

### Next Steps

With the ETL pipelines complete, you now have:
- ✅ Mock CDW data in SQL Server (simulates VA production CDW)
- ✅ Bronze/Silver/Gold Parquet files in MinIO (data lake)
- ✅ Query-optimized data in PostgreSQL (serving database for UI)

You can now start the FastAPI application and view patient data in the UI:

```bash
# Start the main med-z1 web application
uvicorn app.main:app --reload

# Open browser to http://127.0.0.1:8000
# Login with: clinician.alpha@va.gov / VaDemo2025!
# Search for patient by ICN (e.g., 1000000001)
```
