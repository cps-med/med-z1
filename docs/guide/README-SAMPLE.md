This is a sample README.md file for a separate project that also uses MS SQL Server. I would like to use the approach described below for creating and populating the CDWWork mock database used by med-z1.

# med-etl

ETL functionality to retreive, process, and store data in a data mart

## Overview

**med-etl** is a subsystem of the med-insight application that provides ETL functionality to retrieve data from external systems and store transformed data in a data mart.  

It performs two primary functions:

* **Data Preparation Pipeline** - Extracts mock VA healthcare data from source systems, transforms/cleans it according to business rules, and loads prepared data into target databases for consumption by downstream applications (e.g., **med-risk** - a future medication risk management application).

* **ASCII Extract Generation** - Generates fixed-width ASCII files for various healthcare domains. This serves as a learning tool for Python, SQL Server, and data processing skill development and will be retained as the application evolves.

### Technology Stack

- **Python 3.11** - Core application language
- **SQL Server 2019** - Source database (CDWWork) and target database (Extract)
- **MinIO** - S3-compatible object storage for Parquet files (future enhancement)
- **Pandas** - Data processing and transformation
- **Docker Desktop** - Container runtime for SQL Server and MinIO

Refer to the sections below for instructions on local development environment setup and configuration.  

## Microsoft SQL Server Database
### Local Setup
Refer to the **med-data** subsystem README.md file for instructions on how to set up, configure, and access Microsoft SQL Server 2019 on your local macOS machine via container images using **Docker Desktop** or **Podman**.

### Data Mart Database Creation
Once Docker, Ubuntu, and Microsft SQL Server are installed and running in a container, proceed to running the SQL scripts located in the `dbscript/sql-server/extract` folder.  

#### Option 1: Run each script using a tool
These scripts can be run using a tool of your choice, such as Azure Data Studio or Visual Studio Code with the Microsoft SQL Server (mssql) extension (**recommended**).  

For either tool, ensure that you have a connection using the proper connection information, for example:  
```text
           Profile Name: sqlserver19-docker
            Server name: 127.0.0.1,1433
Trust server connection: yes
    Authentication type: SQL Login
              User name: sa
               Password: ************
          Save Password: yes
```

Run each of the "create" scripts (database, schemas, tables) within the `create` subfolder.  

> Note that the initial create script, db_database.sql, includes a **drop database** statement, which means that it can be used to completely remove the database, schemas, and tables to start fresh.

#### Option 2: Run from command line
For simplicity and speed, you can use the `_master.sql` scripts in the `create` folder. To do this, install the `sqlcmd` command-line utility (e.g., via homebrew) and run each master script using SQL Server authentication.

> Note: sqlcmd was probably installed as part of the med-data setup. Verify with: `which sqlcmd`.

If `sqlcmd` is _not_ installed, you can install it via Homebrew:
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql mssql-tools
```

After installing, update .zshrc to make sqlcmd available in your PATH:
```bash
export PATH="/usr/local/opt/mssql-tools/bin:$PATH"
```

To see a list of sqlcmd options, run:
```bash
sqlcmd '-?'
```

Then, cd to the `create` folder and run the following script from the command line:
```bash
sqlcmd -S 127.0.0.1,1433 -U sa -P ************ -i _master.sql
```

Alternatively, you can run via the the shell script, _master.sh, located in the "create" and "insert" folders.  
> Note that this script relies on an environment variable (set by .env) for the SQL Server password.  
> Obtain a copy of **med-insight/med-etl/.env** from a peer developer.  
```bash
./_master.sh
```

## Python
For Macbook users, macOS comes with a system version of Python pre-installed, but it is often outdated and not recommended for development.

You can check the version:
```bash
python3 --version
```

If it's an older version, consider a new installation via Homebrew.

Install Homebrew (if not already installed):  
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Python:  
```bash
brew install python
```

Note: After installing via homebrew, the new version may not be recognized. If this is the case, refresh (or open/close) your terminal session.

Verify Installation:  
```bash
python3 --version
pip3 --version
```

This will show the latest Python3 and PIP3 versions, e.g., 3.13.3 and 25.0.1.

### Python Virtual Environment
It is recommended that you set up a Python virtual environment. This provides a self-contained directory with a Python interpreter and a set of installed packages, which isolates the dependencies required for this project.

#### General Setup Instructions
For my local setup, I selected the root `med-etl` folder as the location for the virtual environment.

Create a virtual environment:   
```bash
cd ~/swdev/med/med-insight/med-etl
python3 -m venv mypyenv
```

Replace "mypyenv" with your preferred name for the environment folder that's created. It is common to use "venv" for the name of the environment, so that's what I'll assume for the subsequent steps below.

Activate the virtual environment. Below are the Linux/macOS and Windows commands, respectively.

```bash
# macOS command
source venv/bin/activate

# Windows command
venv\Scripts\activate
```

For Git Bash, use a slightly different command:
```bash
source venv\Scripts\Activate
```

After activation, you’ll notice the environment name `(venv)` appears in your terminal prompt. You can invoke Python with the command, `python` (as opposed to `python3`).

You can then install packages as normal using `pip` or install all packages from `requirements.txt`.

#### Create and Initialize Dependencies from Requirements file
To create and activate an environment and install from the `requirements.txt` file:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Update requirements.txt (as necessary)
After installing python packages via pip, you should update the requirements.txt file so that it contains all of the existing plus the new packages. This is done via the command:

```bash
pip freeze > requirements.txt
```

### Python Database Server Dependencies
Now that you have installed SQL Server as a Docker image, created your database, and populated the tables with sample data, you will need to configure your Python program (which uses the pyodbc library) to work with the database server. This entails installing several dependencies.

Add Microsoft's Homebrew Tap, which allows you to install the official Microsoft ODBC driver for SQL Server.

> Note: sqlcmd was probably installed as part of the med-data setup. Verify with: `which sqlcmd`.

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
```

Install ODBC Driver for SQL Server (e.g., version 18). 

```bash
brew install msodbcsql18
```

Install `unixODBC`, the ODBC driver manager that pyodbc relies on.

```bash
brew install unixodbc
```

Verify driver installation by listing installed ODBC drivers.

```bash
odbcinst -q -d
```

You should see something like: [ODBC Driver 18 for SQL Server]  

If you see that multiple drivers have been installed, for example one or more older versions, that's okay, since the Python code specifies which driver to use when connecting to SQL Server.

### Python dotenv Module
The med-etl application uses the Python `dotenv` module, provided by the `python-dotenv` package. Use of this module requires a `.env` file to be placed in the root med-etl folder. This file is not under source control, so you will need to ask a peer developer for information on file contents, or to get a copy for your local development environment.

Below are the contents of a sample .env file, with sensitive values removed.

```txt
# Python dotenv variables

# CDWWork database configuration (local)
CDWWORK_DB_ENGINE=MS_SQL_SERVER_2019
CDWWORK_DB_DRIVER="ODBC Driver 18 for SQL Server"
CDWWORK_DB_SERVER=127.0.0.1,1433
CDWWORK_DB_NAME=CDWWork
CDWWORK_DB_USER=sa
CDWWORK_DB_PASSWORD=
TRUST_CONNECTION=yes
TRUST_CERT=yes

# Extract database configuration (local)
EXTRACT_DB_ENGINE=MS_SQL_SERVER_2019
EXTRACT_DB_DRIVER="ODBC Driver 18 for SQL Server"
EXTRACT_DB_SERVER=127.0.0.1,1433
EXTRACT_DB_NAME=Extract
EXTRACT_DB_USER=sa
EXTRACT_DB_PASSWORD=
TRUST_CONNECTION=yes
TRUST_CERT=yes

# MinIO S3-compatible storage configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=
MINIO_BUCKET_NAME=med-sandbox
MINIO_USE_SSL=false

# Other configuration settings
ASCII_EXTRACT_FOLDER="~/swdev/med/med-output/_extract/"
LOG_DIRECTORY_PATH="/Users/chuck/swdev/med/med-output/_log/"
```

or (an older version that is tailored for external hosted SQL Server)

```txt
# Database configuration
DB_SERVER=vhacdwdwhsql33.vha.med.va.gov/
DB_NAME=CDWWork
DB_USER=VHAMASTER\VHAISWSYLVEC
DB_PASSWORD=

# Other configuration settings
ASCII_EXTRACT_FOLDER="~/swdev/med/_extract/"
```

----
----

# med-etl
(original readme content below)

## Prerequisites

Before setting up med-etl, ensure you have completed the **med-data** setup, which provides the shared infrastructure and source data. The med-data setup includes:

- ✅ Docker Desktop (or Podman) installed and running
- ✅ SQL Server 2019 container (`sqlserver2019`) created and running
- ✅ CDWWork database created and populated with mock data
- ✅ MinIO container (`med-insight-minio`) created and running
- ✅ Python 3.11 installed via Homebrew
- ✅ SQL Server command-line tools (`sqlcmd`, ODBC drivers) installed
- ✅ `.env` file obtained from peer developer

**If you have not completed the med-data setup**, please refer to the **med-data** `README.md` file for detailed instructions on setting up the shared development environment.

### med-etl Specific Requirements

Once the med-data environment is ready, you'll need:

- [ ] **Extract database** - Target database for transformed data (created in this setup)
- [ ] **Python virtual environment** - Isolated environment for med-etl dependencies
- [ ] **med-etl .env file** - Configuration for both CDWWork and Extract databases

### Time Estimate
- **First-time setup** (with med-data already configured): 15-20 minutes
- **Daily startup**: 2-3 minutes

---

## Quick Start

For developers who have already completed the med-data setup and want to get med-etl running quickly:

```bash
# 1. Ensure Docker and containers are running
docker ps  # Should show sqlserver2019 and med-insight-minio running

# 2. Navigate to project directory
cd ~/swdev/med/med-etl

# 3. Create output directory structure
mkdir -p ~/swdev/med/med-output/extract
mkdir -p ~/swdev/med/med-output/log

# 4. Create Extract database
cd dbscript/sql-server/extract/create
./_master.sh

# 5. Create and activate Python virtual environment
cd ~/swdev/med/med-etl
python3 -m venv .venv
source .venv/bin/activate

# 6. Install dependencies
pip install -r requirements.txt

# 7. Verify .env file is in place
ls -la .env

# 8. Run the application
python main.py
```

Follow the interactive prompts to select ETL function, station, extract type, date range, and status.

---

## Extract Database Setup

The **Extract** database is the target database where med-etl stores transformed and prepared data. This database is separate from the **CDWWork** source database (created by med-data).

### Database Purpose

- **CDWWork** (source) - Mock VA Corporate Data Warehouse data, created by med-data
- **Extract** (target) - Prepared/transformed data for downstream applications, created by med-etl

Both databases run in the same SQL Server 2019 Docker container but maintain clear separation between raw mock data and prepared data.

### Create Extract Database

The Extract database includes:
- Database structure with `Data` schema
- Tables: `Data.ADM`, `Data.LBB`, `Data.RAD`, `Data.CLI` (and future tables)
- Metadata columns for tracking ETL runs

#### Option 1: Command Line (Recommended)

```bash
cd ~/swdev/med/med-etl/dbscript/sql-server/extract/create
./_master.sh
```

The `_master.sh` script uses the `EXTRACT_DB_PASSWORD` environment variable from your `.env` file.

#### Option 2: Manual sqlcmd Execution

```bash
cd ~/swdev/med/med-etl/dbscript/sql-server/extract/create
sqlcmd -S 127.0.0.1,1433 -U sa -P 'YourPassword' -i _master.sql
```

Replace `YourPassword` with your SQL Server password.

#### Option 3: Using VS Code with mssql Extension

1. Open Command Palette (Cmd+Shift+P)
2. Select "MSSQL: Connect"
3. Use your existing connection profile (or create one):
   - Server: `127.0.0.1,1433` (note the comma)
   - Database: `Extract`
   - Authentication: SQL Login
   - Username: `sa`
   - Password: (from your .env file)
4. Navigate to `dbscript/sql-server/extract/create/`
5. Open `_master.sql`
6. Right-click in editor and select "Execute Query" (or Cmd+Shift+E)

**Note**: The `db_database.sql` script includes `DROP DATABASE IF EXISTS` - this allows you to start fresh if needed.

### Verify Extract Database

```bash
# Verify database exists
sqlcmd -S 127.0.0.1,1433 -U sa -P 'YourPassword' -d Extract -Q "
SELECT name AS SchemaName FROM sys.schemas WHERE name = 'Data'"

# Verify tables exist
sqlcmd -S 127.0.0.1,1433 -U sa -P 'YourPassword' -d Extract -Q "
SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'Data' ORDER BY TABLE_NAME"
```

---

## Output Directory Structure

The med-etl application generates output files during ETL processing and stores them in a dedicated output directory separate from the application code.

### Directory Location

```
~/swdev/med/med-output/
├── extract/    # ASCII extract files generated by ETL process
└── log/        # Application log files
```

### Create Output Directories

Users must manually create this directory structure before running the application:

```bash
# Create the parent output directory and subdirectories
mkdir -p ~/swdev/med/med-output/extract
mkdir -p ~/swdev/med/med-output/log
```

The `-p` flag creates parent directories as needed and doesn't error if directories already exist.

### Verify Directory Structure

```bash
# Verify directories were created
ls -la ~/swdev/med/med-output/

# Expected output should show:
# drwxr-xr-x  extract/
# drwxr-xr-x  log/
```

### Configuration

These directories are referenced in the `.env` file via:
- `ASCII_EXTRACT_FOLDER` - Points to the extract folder
- `LOG_DIRECTORY_PATH` - Points to the log folder

See the **Environment Configuration** section for details.

---

## Python Environment

### Create Python Virtual Environment

A virtual environment provides an isolated Python environment with project-specific dependencies.

```bash
cd ~/swdev/med/med-etl
python3 -m venv .venv
```

The `.venv` directory name keeps the environment hidden but discoverable.

### Activate Virtual Environment

**macOS/Linux**:
```bash
source .venv/bin/activate
```

**Windows**:
```bash
.venv\Scripts\activate
```

**Git Bash**:
```bash
source .venv/Scripts/Activate
```

After activation, your prompt shows `(.venv)` and you can use `python` instead of `python3`.

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies installed**:
- `pyodbc` - SQL Server connectivity
- `pandas`, `pyarrow` - Data processing and Parquet file handling
- `boto3`, `s3fs` - S3-compatible storage (MinIO, for future use)
- `python-dotenv` - Environment variable management

### Verify Installation

```bash
# Verify Python packages
python -c "import pyodbc, pandas; print('Dependencies OK')"

# Verify ODBC driver (should already be installed from med-data setup)
odbcinst -q -d
# Should see: [ODBC Driver 18 for SQL Server]
```

### Deactivate Virtual Environment

When done working:
```bash
deactivate
```

### Update requirements.txt (Maintenance)

After installing new packages via pip:
```bash
pip freeze > requirements.txt
```

---

## Environment Configuration (.env)

The med-etl application uses environment variables for configuration, keeping sensitive credentials out of version control.

### Setup Instructions

1. **Obtain .env file** from peer developer or team lead
2. **Place in project root**: `~/swdev/med/med-etl/.env`
3. **Never commit to version control** (already in .gitignore)

### .env File Structure

Create a `.env` file in the project root with the following content:

```bash
# -----------------------------------------------------------------------
# Source Database Configuration (CDWWork - created by med-data)
# -----------------------------------------------------------------------
CDWWORK_DB_DRIVER=ODBC Driver 18 for SQL Server
CDWWORK_DB_SERVER=127.0.0.1,1433
CDWWORK_DB_NAME=CDWWork
CDWWORK_DB_USER=sa
CDWWORK_DB_PASSWORD=YourSecurePassword123!

# -----------------------------------------------------------------------
# Target Database Configuration (Extract - created by med-etl)
# -----------------------------------------------------------------------
EXTRACT_DB_DRIVER=ODBC Driver 18 for SQL Server
EXTRACT_DB_SERVER=127.0.0.1,1433
EXTRACT_DB_NAME=Extract
EXTRACT_DB_USER=sa
EXTRACT_DB_PASSWORD=YourSecurePassword123!

# -----------------------------------------------------------------------
# Database Connection Settings
# -----------------------------------------------------------------------
TRUST_CONNECTION=no
TRUST_CERT=yes

# -----------------------------------------------------------------------
# MinIO S3-Compatible Storage Configuration (Future Enhancement)
# -----------------------------------------------------------------------
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=YourMinIOPassword123!
MINIO_BUCKET_NAME=med-sandbox
MINIO_USE_SSL=false

# -----------------------------------------------------------------------
# Application Configuration
# -----------------------------------------------------------------------
ASCII_EXTRACT_FOLDER=~/swdev/med/med-output/extract
LOG_DIRECTORY_PATH=~/swdev/med/med-output/log
```

### Configuration Notes

**Database Prefix Pattern**:
- `CDWWORK_*` prefix for source database (mock data from med-data)
- `EXTRACT_*` prefix for target database (prepared data for downstream apps)
- The `db_config.py` module uses these prefixes: `create_connection("CDWWork")` or `create_connection("Extract")`

**SQL Server Passwords**:
- Both `CDWWORK_DB_PASSWORD` and `EXTRACT_DB_PASSWORD` should use the same password (the SQL Server `sa` password)
- Minimum 8 characters with uppercase, lowercase, numbers, and special characters

**MinIO Configuration** (for future use):
- `MINIO_ENDPOINT`: Host and port without protocol
- `MINIO_BUCKET_NAME`: Bucket for source Parquet files
- `MINIO_USE_SSL`: Set to `false` for local development

**Application Output Paths**:
- `ASCII_EXTRACT_FOLDER`: Directory where ASCII extract files are generated
- `LOG_DIRECTORY_PATH`: Directory where application log files are written
- Both support `~` expansion for home directory
- Users must manually create these directories (see **Output Directory Structure** section)
- Defaults:
  - Extract: `~/swdev/med/med-output/extract`
  - Logs: `~/swdev/med/med-output/log`

---

## Running the Application

The med-etl application provides an interactive command-line interface for selecting ETL operations.

### Start the Application

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Run the main application
python main.py
```

### Interactive Prompts

The application will guide you through the following selections:

**1. ETL Function**
- `1` - Get Data (Extract & Load): Fetch records from source systems, transform, and load into Extract database
- `2` - Create File (ASCII Extract): Query Extract database and generate fixed-width ASCII files

**2. Station Number**
- Enter a valid VistA station: `508`, `516`, `442`, or `552`

**3. Extract Type**
- `ADM` - Admissions/Inpatient data
- `LBB` - Lab Blood Bank data
- `RAD` - Radiology data
- `CLI` - Clinic data (placeholder, not fully implemented)

**4. Date Range**
- Start Date: `YYYY-MM-DD` format (e.g., `2024-01-01`)
- End Date: `YYYY-MM-DD` format (e.g., `2024-12-31`)
- Range must be ≤365 days
- No future dates allowed

**5. Extract Status**
- `audit` - Test/development processing
- `final` - Production processing

**6. Confirmation**
- Review your selections and confirm to proceed

### Example Session

```text
=== med-etl Data Pipeline ===

Select ETL Function:
  1 - Get Data (Extract & Load)
  2 - Create File (ASCII Extract)
Enter choice (1 or 2): 1

Enter Station Number (508, 516, 442, 552): 508

Enter Extract Type (ADM, LBB, RAD, CLI): LBB

Enter Start Date (YYYY-MM-DD): 2024-01-01
Enter End Date (YYYY-MM-DD): 2024-12-31

Enter Extract Status (audit or final): audit

=== Confirmation ===
ETL Function: Get Data
Station: 508
Extract Type: LBB
Date Range: 2024-01-01 to 2024-12-31
Status: audit

Proceed? (Y/N): Y

Processing...
```

---

## Daily Development Workflow

### Starting Your Development Session

```bash
# 1. Start Docker Desktop (if not already running)
# Open Docker Desktop app from Applications

# 2. Start containers (if not already running)
docker start sqlserver2019 med-insight-minio

# 3. Verify containers are running
docker ps
# Should show both containers with STATUS "Up"

# 4. Navigate to project directory
cd ~/swdev/med/med-etl

# 5. Activate Python virtual environment
source .venv/bin/activate

# 6. Run the application
python main.py
```

### Working with Databases

**Via VS Code mssql extension** (recommended):
1. Open Command Palette (Cmd+Shift+P)
2. Select "MSSQL: Connect"
3. Choose your saved connection profile
4. Execute queries with Cmd+Shift+E

**Via command line**:
```bash
# Query CDWWork (source) database
sqlcmd -S 127.0.0.1,1433 -U sa -P "$CDWWORK_DB_PASSWORD" -d CDWWork -Q "
SELECT COUNT(*) FROM Inpat.Inpatient"

# Query Extract (target) database
sqlcmd -S 127.0.0.1,1433 -U sa -P "$EXTRACT_DB_PASSWORD" -d Extract -Q "
SELECT COUNT(*) FROM Data.ADM"
```

### Ending Your Development Session

```bash
# 1. Deactivate Python virtual environment
deactivate

# 2. Stop containers (optional - can leave running)
docker stop sqlserver2019 med-insight-minio

# 3. Quit Docker Desktop (optional - can leave running in background)
# Click Docker icon in menu bar → Quit Docker Desktop
```

---

## Extract Types

The application currently supports four extract types, with more planned:

### ADM - Admissions/Inpatient Data
- **Source**: CDWWork database (SQL queries)
- **Tables**: Multiple inpatient tables joined with patient demographics
- **Implementation**: Multi-step SQL queries using global temp tables
- **Status**: Fully implemented

### LBB - Lab Blood Bank Data
- **Source**: MinIO Parquet files
- **Path**: `s3://med-sandbox/extract-file/lbb/`
- **Implementation**: Pandas read_parquet with S3 storage options
- **Status**: Fully implemented

### RAD - Radiology Data
- **Source**: MinIO Parquet files
- **Path**: `s3://med-sandbox/extract-file/rad/`
- **Implementation**: Pandas read_parquet with S3 storage options
- **Status**: Fully implemented

### CLI - Clinic Data
- **Source**: Not yet defined
- **Status**: Placeholder, not fully implemented

### Coming Soon: Med/Rx - Medications/Prescriptions
The next planned extract domain will support medication and prescription data for downstream risk management applications.
