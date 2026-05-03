# AWS Deployment Guide

This guide details the process, prerequisites, and information needed to deploy the med-z1 application to the AWS cloud. The initial deployment approach will be deliberately simple, so that the basics are covered prior to defining a more elaborate architecture.  

## AWS Target Environment

### Create and Configure a Single EC2 Instance

The initial plan is to create a single EC2 Instance running Ubuntu Linux, which will mirror the developer desktop setup and configuation. Later, a multi-EC2 setup will be considered.

Begin by logging into the AWS Management Console using an IAM user. Then, launch the EC2 page and select "Launch instance".

**Original EC2 Instance**
This configuration proved to be underpowered. Was not able to completely install Python dependencies from requirements.txt. System froze and had to be termination. Below are the specs used for this unsuccessful attempt.

| Item | Value |
| ---- | ----- |
| AWS Account ID      | (refer to 1Password) |
| IAM User Name       | cps-admin            |
| IAM User Password   | (refer to 1Password) |
| EC2 Username        | ec2-user             |
| EC2 Instance ID     | i-01cf01376b12ab3ed  |
| Public IPv4 address | 54.173.64.80         |
| Public DNS          | ec2-54-173-64-80.compute-1.amazonaws.com        |
| AMI Name            | al2023-ami-2023.11.20260406.2-kernel-6.1-x86_64 |
| EC2 Instance Name   | cps-ec2-01           |
| Instance Type       | t3.micro             |
| Block Device        | 8 GiB                |
| Operating System    | Amazon Linux 2023    |
| Security Group      | launch-wizard-2      |

**Connect to Original EC2 Instance via SSH**  
```bash
# EC2 Instance ID
i-01cf01376b12ab3ed

# Protect key / file access privilige
chmod 400 "cps-ec2-01-keypair.pem"

# Connect via SSH
ssh -i "~/swdev/tmp/aws-ec2-keypair/cps-ec2-01-keypair.pem" \
ec2-user@ec2-54-173-64-80.compute-1.amazonaws.com
```

**Second Try EC2 Instance**
This configuration also proved to be insufficient. Experienced a similar issue when installing Python dependencies, especially the AI/ML packages, which can be quite large. Below are the specs used for this unsuccessful attempt.

| Item | Value |
| ---- | ----- |
| AWS Account ID       | (refer to 1Password) |
| IAM User Name        | cps-admin            |
| IAM User Password    | (refer to 1Password) |
| EC2 Username         | ec2-user             |
| EC2 Instance ID      | i-0fc48fe55972c67d3  |
| Public IPv4 address  | 54.167.88.223        |
| Private IPv4 address | 172.31.27.135        |
| Public DNS           | ec2-54-167-88-223.compute-1.amazonaws.com       |
| Private DNS          | ip-172-31-27-135.ec2.internal                   |
| VPC ID               | vpc-0a13e1f96cdc52027                           |
| AMI Name             | al2023-ami-2023.11.20260406.2-kernel-6.1-x86_64 |
| EC2 Instance Name    | cps-ec2-02           |
| Operating System     | Ubuntu 24.04 LTS     |
| Instance Type        | t3.xlarge            |
| Block Device         | 8 GiB                |
| Security Group       | launch-wizard-3      |


**Connect to Second Try EC2 Instance via SSH**  
```bash
# EC2 Instance ID
i-01cf01376b12ab3ed

# Protect key / file access privilige
chmod 400 "cps-ec2-02-keypair.pem"

# Connect via SSH
ssh -i "~/swdev/tmp/aws-ec2-keypair/cps-ec2-02-keypair.pem" \
ubuntu@ec2-54-167-88-223.compute-1.amazonaws.com
```

**Third Try EC2 Instance**
So far, this configuration is working. It made it past the Python requirements.txt dependency installation, though several AI/ML packages are commented out. Below are the specs used for this attempt, which is still being verified as I continue with the full AWS installation and configuration.

| Item | Value |
| ---- | ----- |
| AWS Account ID         | (refer to 1Password)                            |
| IAM User Name          | cps-admin                                       |
| IAM User Password      | (refer to 1Password)                            |
| EC2 Instance Name      | cps-ec2-04                                      |
| Application & OS Image | Ubuntu                                          |
| Operating System       | Ubuntu 24.04 LTS                                |
| Architecture           | 64-bit (x86)                                    |
| Instance Type          | t3.xlarge                                       |
| Key pair (login)       | cps-ec2-04-keypair                              |
| Key pair type          | RSA                                             |
| Key pair format        | .pem                                            |
| Security Group         | launch-wizard-5                                 |
| Allow SSH traffic      | My IP                                           |
| Allow HTTP traffic     | from the internet                               |
| Block Device           | 16 GiB                                          |
| EC2 Username           | ubuntu                                          |
| EC2 Instance ID        | i-06cf8d066a13187f7                             |
| Public IPv4 address    | 54.88.161.8                                     |
| Private IPv4 address   | 172.31.42.92                                    |
| Public DNS             | ec2-54-88-161-8.compute-1.amazonaws.com         |
| Private DNS            | ip-172-31-42-92.ec2.internal                    |
| VPC ID                 | vpc-0a13e1f96cdc52027                           |
| AMI Name               | al2023-ami-2023.11.20260406.2-kernel-6.1-x86_64 |

**Connect to Third Try EC2 Instance via SSH**  
```bash
# EC2 Instance ID
i-06cf8d066a13187f7

# Protect key / file access privilige
chmod 400 "~/swdev/tmp/aws-ec2-keypair/cps-ec2-04-keypair.pem"

# Connect via SSH
ssh -i "~/swdev/tmp/aws-ec2-keypair/cps-ec2-04-keypair.pem" \
ubuntu@ec2-54-88-161-8.compute-1.amazonaws.com
```

## AWS CLI Cheatsheet
Initial content here will be random notes that I make as I'm learning...

Get AWS CLI Version
```bash
aws --version
```

List Users
```bash
aws iam list-users
```

## med-z1 Installation

### Git Setup

**Amazon Linux 2023**  
The AL2023 image does not come with Git pre-installed, so you will need to install it using the **DNF** (Dandified YUM) package manager. 

Update your package database (recommended):
```bash
sudo dnf update -y
```

Install Git:
```bash
sudo dnf install git -y
```

Verify the installation:
```bash
git --version
```

**Ubuntu**  
Ubuntu comes with Git v2.43.0 preinstalled.

### Clone med-z1 Repo to AWS EC2 Instance

Since this is a public repository and I do not plan to push any updates from the EC2 instance back to GitHub, no SSH or PAT setup is necessary. This simplifies the GitHub setup tasks.

Create and go to the folder where you would like to clone the med-z1 repo, e.g.  
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

# standard GNU verions of ls supports:
ls -al --group-directories-first

# tree utility (several variants)
tree -L 1
tree -L 1 -F
tree -d -L 2
```

### Add and Configure .env File

The med-z1 applications uses a project-wide .env file for managing secrets and other sensitive information. Ask a peer developer for a copy that you can place in the med-z1 root directory.  

Place .env in the project root folder, or copy/paste contents into .env file
```bash
cp .env ~/swdev/med/med-z1/
```

No additional configuration is required at this time. Once you have obtain the project-wide .env file and placed it in the project root directory, you should be good to go.  

## Verify Python v3.10 (or higher) Availability

### Amazon Linux 2023

Amazon Linux 2023 comes with Python v3.9.x, so it needs to be updated to at least v3.10.

You can check the version:
```bash
python3 --version
```

Since I prefer the `.venv` naming convention and want to keep the system Python (3.9) untouched, the process becomes very clean. This is the professional standard for deploying FastAPI applications on AWS, as it ensures your application remains isolated from the OS.

**Install Python 3.11 and Dependencies**  
First, ensure the Python 3.11 interpreter and the necessary tools for building PostgreSQL drivers are present on the system.

```bash
# Update the package manager
sudo dnf update -y

# Install Python 3.11, its pip, and development headers
# python3.11-devel is often required for compiled packages like psycopg2
sudo dnf install python3.11 python3.11-pip python3.11-devel libpq-devel -y
```

**Initialize the Application Directory**  
Assuming your code is already on the instance (or you are about to pull it), navigate to your project root.

```bash
cd ~/med-z1
```

**Create and Activate the `.venv`**  
By using the specific `python3.11` binary to create the environment, the virtual environment will "lock" itself to that version.

```bash
# Create the virtual environment named .venv
python3.11 -m venv .venv

# Activate the environment
source .venv/bin/activate
```

**Verify the Local Environment**  
Once activated, your shell prompt should reflect `(.venv)`. Verify that `python` now points to 3.11 within this context:

```bash
python --version
# Expected Output: Python 3.11.x

which python
# Expected Output: /home/ec2-user/med-z1/.venv/bin/python
```

**Install Project Requirements**  
Now you can install your FastAPI/HTMX stack. Since you are using PostgreSQL, ensure your `requirements.txt` includes your preferred adapter (like `psycopg[binary]` or `psycopg2-binary`).

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Ubuntu Linux

Ubunto comes with Python 3.12 preinstalled. But, some of the supporting libraries are not preinstalled, so you need to install them globally.

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev libpq-dev build-essential
```

**Next Steps:** follow the remaining Python setup steps listed in the Amazon Linux section above.  

## Docker Setup

The official Docker repositories are not yet known to the new Ubuntu instance. While Ubuntu's default repositories sometimes carry a version of Docker (called `docker.io`), the specific packages needed—`docker-ce` (Community Edition), the CLI, and the modern plugins—are hosted directly by Docker.  

On a "vanilla" AWS Ubuntu image, you have to manually add Docker’s official GPG key and repository.

### Step 1: Set up the Repository
Run these commands to prepare your system and add the Docker source list:

```bash
# Update the apt package index and install packages to allow apt to use a repository over HTTPS:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg

# Add Docker’s official GPG key:
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Step 2: Install Docker Engine
Now that the system knows where to look, update your index again and run your original command:

```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Step 3: Manage Docker as a Non-Root User
Since you are logged in as the `ubuntu` user, you’ll find it annoying to type `sudo` before every Docker command. You can add yourself to the `docker` group to fix this:

1.  **Add your user to the group:**
    ```bash
    sudo usermod -aG docker $USER
    ```
2.  **Apply the changes:**
    Log out of your SSH session and log back in, or run:
    ```bash
    newgrp docker 
    ```

### Verifying the Setup
You can confirm everything is working by checking the version and running a test container:

```bash
docker --version
docker compose version
docker run hello-world
```

## Installing and Running Docker Images in a Container

The instructions below are for Docker **native engine** installation, using a **docker-compose.yaml** script.

The Linux intallation uses a docker compose yaml file, which is under version control and located in the project root directory. this file, `docker-compose.yaml`, is used to define and start the required conatiner images.  

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

Before running any ETL pipelines or setting up user authentication, you must create the `medz1` database. The instructions below are for creating the database only; steps for creating the required schemas and tables are provided later.  

**Creation:**  
```bash
# Connect to the default 'postgres' database
docker exec -it postgres16 psql -U postgres -d postgres

# List the current set of databases within the postgress server
# For firsttime setup, the list will not include medz1.
\l

# Create the medz1 database from psql prompt
CREATE DATABASE medz1;

# Verify creation
# Should now include medz1
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

**Dropping an Existing Database:**  
If you need to completely remove an existing database, e.g., to begin a fresh installation, follow the instructions below:  

```bash
-- Connect to the default 'postgres' database
\c postgres

-- Drop the existing database (forcing active connections to close)
DROP DATABASE medz1 WITH (FORCE);
```

## PostgreSQL User Authentication Setup

This section guides you through setting up the user authentication schema and tables within the PostgreSQL `medz1` database and populating these tables with mock user data. This one-line command uses the PostgreSQL DDL script shown below.

Create Authentication Schema and Tables
```bash
docker exec -i postgres16 psql -U postgres -d medz1 < db/ddl/create_auth_tables.sql
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

Verify Mock Users Were Loaded via SQL Query
```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c \
"SELECT email, display_name, home_site_sta3n, is_active FROM auth.users ORDER BY email;"
```

You can now test the authentication system by logging into the med-z1 application.

Start the FastAPI application using Uvicorn
```bash
uvicorn app.main:app --reload --port 8001
```

Start a browser and navigate to
```bash
http://127.0.0.1:8001/
```
You should be redirected to the login page where you can use these credentials

Test Credentials (all users share same password)
```text
Email: clinician.alpha@va.gov
Password: VaDemo2025!
```

## PostgreSQL AI Infrastructure Setup

This section explains the AI infrastructure tables within the PostgreSQL `medz1` database. These tables support the AI Clinical Insights feature, specifically enabling **conversation memory** using LangGraph's PostgreSQL checkpointer.

**Note: Auto-Created Tables (No Manual Setup Required)**    

The LangGraph checkpoint tables are **automatically created** when the FastAPI application starts. The `AsyncPostgresSaver.setup()` method in the lifespan handler creates these tables in the `public` schema if they don't exist.

No manual DDL execution is required, simply start the application:

```bash
# Tables are auto-created during application startup
uvicorn app.main:app --reload --port 8001
```

**What happens at startup:**
1. Application initializes LangGraph `AsyncPostgresSaver`
2. Calls `checkpointer.setup()` (idempotent - safe to run multiple times)
3. Creates 4 checkpoint tables in `public` schema if missing
4. Application logs confirm successful initialization

**Expected startup logs:**
```
============================================================
med-z1 application startup: Initializing components
============================================================
Initializing LangGraph AsyncPostgresSaver for conversation memory...
Checkpoint URL: postgresql://***@localhost:5432/medz1
✅ LangGraph checkpointer initialized successfully
   - Schema: public (LangGraph default)
   - Tables: checkpoints, checkpoint_writes, checkpoint_blobs, checkpoint_migrations
   - Conversation memory enabled
✅ AI Clinical Insights Agent initialized successfully
   - Tools: 4 tools available
   - Conversation memory: ENABLED
============================================================
```

### **Verify Tables Were Created**

After starting the application, verify the checkpoint tables:

```bash
# List checkpoint tables in public schema
docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt public.*point*"
```

**Expected output:**
```
                List of relations
 Schema |         Name          | Type  |  Owner
--------+-----------------------+-------+----------
 public | checkpoint_blobs      | table | postgres
 public | checkpoint_migrations | table | postgres
 public | checkpoint_writes     | table | postgres
 public | checkpoints           | table | postgres
(4 rows)
```

**View table structures:**
```bash
# View checkpoints table structure
docker exec -it postgres16 psql -U postgres -d medz1 -c "\d public.checkpoints"

# View checkpoint_blobs table structure
docker exec -it postgres16 psql -U postgres -d medz1 -c "\d public.checkpoint_blobs"
```



## MinIO Setup and Bucket Creation

The med-z1 application uses MinIO as an S3-compatible object storage system for the data lake. The primary file types that will be managed within MinIO are csv and Parquet. MinIO must be properly configured before running ETL pipelines, as the pipelines read and write parquet files to and from MinIO.  

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

---

AWS Specific Instructions

---

To access your MinIO web console from your MacBook, you need to ensure that the network path is open across three specific layers: the Docker container mapping, the EC2 instance's security settings, and the browser URL.

Based on your `docker-compose.yaml`, here is the step-by-step to get the console running.

## 1. Verify Port Mapping
In your provided YAML file, you have correctly mapped the MinIO Console port:
* **API Port:** `9000:9000`
* **Console Port:** `9001:9001`

The first number is the **host port** (the EC2 instance) and the second is the **container port**. Since you mapped `9001` to `9001`, your EC2 instance is currently listening for web traffic on port `9001`.

---

## 2. Update AWS Security Group
Even if Docker is listening, AWS acts as a firewall. You mentioned you allowed "http access," but standard HTTP typically only opens port `80`. You must explicitly open the MinIO ports:

1.  Log into your **AWS Management Console**.
2.  Navigate to **EC2 > Instances** and select your instance.
3.  Click the **Security** tab and click on the active **Security Group**.
4.  Edit **Inbound Rules** and add the following:

| Type | Protocol | Port Range | Source |
| :--- | :--- | :--- | :--- |
| Custom TCP | TCP | `9001` | Your MacBook IP /32 |
| Custom TCP | TCP | `9000` | Your MacBook IP /32 (Optional: for API access) |

---

## 3. Accessing the Console
Once the security group is updated, open your browser on your MacBook and use the **Public IP** of your EC2 instance.

**The URL format:**
`http://<EC2_PUBLIC_IP>:9001`

> **Note:** Do not use `localhost` or the private IP, as your MacBook is outside the AWS VPC network.

---

## 4. Credentials
To log in, use the environment variables you defined in your `.env` file that correspond to these keys in your YAML:
* **Username:** `${MINIO_ACCESS_KEY}`
* **Password:** `${MINIO_SECRET_KEY}`

### Troubleshooting Tips
* **Check Logs:** Run `docker compose logs minio` on the EC2 instance to ensure the server started without errors and is indeed bound to `:9001`.
* **Verify Binding:** Run `netstat -tulpn | grep 9001` on the EC2 instance to confirm Docker is listening on that port.
* **Public IP:** Ensure you are using the **IPv4 Public IP** found in the EC2 dashboard, not the Private IP (which usually starts with `10.x`, `172.x`, or `192.x`).

---

## Useful Linux Shell Commands
```bash
# Display Free Disk Info
df -Th

# Display Docker-Specific Disk Info
docker system df

# Display Free Memory Info
free -h

# Show Virtual Memory Stats
vmstat -s

```