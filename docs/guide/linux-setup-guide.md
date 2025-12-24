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

## Create and Populate SQL Server Mock Data
Instructions...

## Run ETL Data Pipelines
Instructions
