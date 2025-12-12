#!/bin/zsh
# Cleanup script to drop Vitals tables before re-running setup
# Run from project root: ./mock/sql-server/cdwwork/vitals_cleanup.sh

# Load environment variables
if [ -f .env ]; then
    source .env
elif [ -f ~/swdev/med/med-insight/.env ]; then
    source ~/swdev/med/med-insight/.env
else
    echo "Error: .env file not found"
    exit 1
fi

echo "================================================"
echo "Cleaning up Vitals tables in CDWWork database"
echo "================================================"
echo ""

# SQL Server connection details
SQL_SERVER="127.0.0.1,1433"
SQL_USER="sa"
SQL_PASSWORD="${CDWWORK_DB_PASSWORD}"

echo "Dropping Vitals tables..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -Q "
USE CDWWork;

-- Drop tables in reverse order (foreign keys first)
IF OBJECT_ID('Vital.VitalSignQualifier', 'U') IS NOT NULL
    DROP TABLE Vital.VitalSignQualifier;

IF OBJECT_ID('Vital.VitalSign', 'U') IS NOT NULL
    DROP TABLE Vital.VitalSign;

IF OBJECT_ID('Dim.VitalQualifier', 'U') IS NOT NULL
    DROP TABLE Dim.VitalQualifier;

IF OBJECT_ID('Dim.VitalType', 'U') IS NOT NULL
    DROP TABLE Dim.VitalType;

PRINT 'Vitals tables dropped successfully';
"

echo ""
echo "✓ Cleanup complete"
echo "You can now run: ./mock/sql-server/cdwwork/vitals_setup.sh"
