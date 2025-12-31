#!/bin/bash
# Load environment variables from project .env file
source ~/swdev/med/med-z1/.env

# Run master creation script for CDWWork2 (Oracle Health/Cerner)
sqlcmd -S 127.0.0.1,1433 -U sa -P "${CDWWORK_DB_PASSWORD}" -C -i _master.sql
