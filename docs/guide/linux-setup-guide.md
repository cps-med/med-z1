# Med-Z1 Setup Guide for Linux

This guide provides instructions for installing, configuring, and running the **med-z1** application on a development machine running the Linux operating system. It is targeted for pop!_OS, but should be useful for other Linux variants.  

For the initial version of this guide, I will sort of run through an install using a _chain of thought_ approach, and will document as I go.

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
- standard bash command: `ls -alG`  
- corutils + alias command: `ll`  
- tree utility: `tree -L 1` or `tree -d -L 2`  

## Add and Configure .env File

The med-z1 applications uses a project-wide .env file for managing secrets and other sensitive information. Ask a peer developer for a copy that you can place in the med-z1 root directory.  

Place .env in the project root folder, or copy/paste contents into .env file
```bash
cp .env ~/swdev/med/med-z1/
```

## Create Python Virtual Environment

The med-z1 application uses a single, shared Python virtual environment. This environment is not under version control, so you will need to create the environmenet locally within your development project using the **requirements.txt** file. This will install all required dependencies into your local environment.  

Note that for performance and compatibility reasons, med-z1 expects Python version 3.11 on macOS and 3.10 or 3.11 on Linux.

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

The **med-z1** application uses several core services that run within Docker container images. On macOS, these services are managed using Docker Desktop; however, there are significant performance gains on Linux by managing these services natively through the command line.  

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

<br><br><br><br>