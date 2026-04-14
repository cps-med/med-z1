# AWS Deployment Guide

This guide details the process, prerequisites, and information needed to deploy the med-z1 application to the AWS cloud. The initial deployment approach will be deliberately simple, so that the basics are covered prior to defining a more elaborate architecture.  

## AWS Target Environment

**Original EC2 Instance (too small)**

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

## Connect to Original EC2 Instance via SSH

```bash
# EC2 Instance ID
i-01cf01376b12ab3ed

# Protect key / file access privilige
chmod 400 "cps-ec2-01-keypair.pem"

# Connect via SSH
ssh -i "~/swdev/tmp/aws-ec2-keypair/cps-ec2-01-keypair.pem" \
ec2-user@ec2-54-173-64-80.compute-1.amazonaws.com
```

**Second Try EC2 Instance (trying it out...)**

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


## Connect to Second Try EC2 Instance via SSH

```bash
# EC2 Instance ID
i-01cf01376b12ab3ed

# Protect key / file access privilige
chmod 400 "cps-ec2-02-keypair.pem"

# Connect via SSH
ssh -i "~/swdev/tmp/aws-ec2-keypair/cps-ec2-02-keypair.pem" \
ubuntu@ec2-54-167-88-223.compute-1.amazonaws.com
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

## Verify Python v3.11 Availability

AWS Linux 2023 comes with Python v3.9.x, so it needs to be updated to at least v3.10.

You can check the version:
```bash
python3 --version
```

Since I prefer the `.venv` naming convention and want to keep the system Python (3.9) untouched, the process becomes very clean. This is the professional standard for deploying FastAPI applications on AWS, as it ensures your application remains isolated from the OS.

### 1. Install Python 3.11 and Dependencies
First, ensure the Python 3.11 interpreter and the necessary tools for building PostgreSQL drivers are present on the system.

```bash
# Update the package manager
sudo dnf update -y

# Install Python 3.11, its pip, and development headers
# python3.11-devel is often required for compiled packages like psycopg2
sudo dnf install python3.11 python3.11-pip python3.11-devel libpq-devel -y
```

## 2. Initialize the Application Directory
Assuming your code is already on the instance (or you are about to pull it), navigate to your project root.

```bash
cd ~/med-z1
```

## 3. Create and Activate the `.venv`
By using the specific `python3.11` binary to create the environment, the virtual environment will "lock" itself to that version.

```bash
# Create the virtual environment named .venv
python3.11 -m venv .venv

# Activate the environment
source .venv/bin/activate
```

## 4. Verify the Local Environment
Once activated, your shell prompt should reflect `(.venv)`. Verify that `python` now points to 3.11 within this context:

```bash
python --version
# Expected Output: Python 3.11.x

which python
# Expected Output: /home/ec2-user/med-z1/.venv/bin/python
```

## 5. Install Project Requirements
Now you can install your FastAPI/HTMX stack. Since you are using PostgreSQL, ensure your `requirements.txt` includes your preferred adapter (like `psycopg[binary]` or `psycopg2-binary`).

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Deployment Tip: Systemd Integration
When you eventually set up a **systemd** service to keep your FastAPI app running in the background, you don't need to "activate" the environment in the script. Instead, you point the `ExecStart` directly to the python binary inside your `.venv`:

```ini
[Service]
# Example systemd snippet
WorkingDirectory=/home/ec2-user/med-z1
ExecStart=/home/ec2-user/med-z1/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

This ensures that even after a reboot, your **med-z1** app starts up automatically using Python 3.11 without any manual intervention.