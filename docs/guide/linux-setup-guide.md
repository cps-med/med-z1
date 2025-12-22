# Med-Z1 Setup Guide for Linux

This guide provides instructions for installing, configuring, and running the **med-z1** application on a development machine running the Linux operating system. This guide it targeted for the popOS variant, but should be useful for other Linux versions.  

For the initial version of this guide, I will sort of run through an install using a _chain of thought_ approach, and will document as I go.

## Step 1: Clone med-z1 repo to local dev machine

- Create and CD to the folder where you would like to clone the med-z1 repo, e.g.  
`mkdir -p ~/swdev/med`
`cd ~/swdev/med`

- Go to the GitHub med-z1 repo  
https://github.com/cps-med/med-z1  

- Click the `Code` button and copy the HTTPS URL  
https://github.com/cps-med/med-z1.git  

- Ensure that you are in the target folder where you would like to clone the repo, e.g.:
`~/swdev/med`

- Run the git clone command from the terminal command line  
`git clone https://github.com/cps-med/med-z1.git`

- CD to the med-z1 project folder  
`cd med-z1`

- Take a look at the project structure  
standard bash command: `ls -alG`  
corutils + alias command: `ll`  
tree utility: `tree -L 1` or `tree -d -L 2`  

## Step 2: Add .env file to root directory

The med-z1 applications uses a project-wide .env file for managing secrets and other sensitive information. Ask a peer developer for a copy that you can place in the med-z1 root directory.  

- Place .env in the project root folder  
`cp .env ~/swdev/med/med-z1/`  
(or simply copy/paste contents into .env file)  

## Step 3: Python Setup and Validation

The med-z1 application uses a single, shared Python virtual environment. This environment is not under version control, so you will need to create the environmenet locally within your development project using the **requirements.txt** file. This will install all required dependencies into your local environment. Note that for performance and compatibility reasons, med-z1 expects Python version 3.11 on macOS and 3.10 or 3.11 on Linux.

- Create virtual environment (Python v3.10 or v3.11)
`python3 -m venv .venv`

- Activate virtual environment
macOS/Linux: `source .venv/bin/activate`  
Windows: `.venv\Scripts\activate`  

- Install dependencies
`pip install -r requirements.txt`  

**Big Warning and Action Needed:**

You will likely run into package compatibility issues when using requirements.txt, since it was built with macOS and Python 3.11 in minde. To mitigate version incompatibility risks, edit your requirements.txt to use "compatible release" operators (~=) or minimum versions (>=) instead of strict equality (==). This allows pip to find the best version for Pop!_OS.  

Update these specific lines in your file:  
- Change: numpy==2.3.5 to numpy>=2.0.0
- Change: pandas==2.3.3 to pandas>=2.0.0
- Change: polars==1.18.0 to polars>=1.0.0
- Keep this line: pydantic==2.12.5
- Remove this line: pydantic_core==2.41.5 

## Step 4: Docker and Docker Images Setup

work on this section next...
