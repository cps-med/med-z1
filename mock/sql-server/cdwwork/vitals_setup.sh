#!/bin/zsh
# Master script to execute all Vitals-related SQL scripts in CDWWork database
# Run from project root: ./mock/sql-server/cdwwork/vitals_setup.sh

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
echo "Setting up Vitals tables in CDWWork database"
echo "================================================"
echo ""

# SQL Server connection details
SQL_SERVER="127.0.0.1,1433"
SQL_USER="sa"
SQL_PASSWORD="${CDWWORK_DB_PASSWORD}"

# Base path for SQL scripts
BASE_PATH="mock/sql-server/cdwwork"

# Step 1: Create Dim.VitalType table
echo "[1/8] Creating Dim.VitalType table..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/create/Dim.VitalType.sql
if [ $? -ne 0 ]; then
    echo "Error creating Dim.VitalType table"
    exit 1
fi
echo "✓ Dim.VitalType table created"
echo ""

# Step 2: Insert Dim.VitalType data
echo "[2/8] Inserting Dim.VitalType data..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/insert/Dim.VitalType.sql
if [ $? -ne 0 ]; then
    echo "Error inserting Dim.VitalType data"
    exit 1
fi
echo "✓ Dim.VitalType data inserted"
echo ""

# Step 3: Create Vital.VitalSign table
echo "[3/8] Creating Vital.VitalSign table..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/create/Vital.VitalSign.sql
if [ $? -ne 0 ]; then
    echo "Error creating Vital.VitalSign table"
    exit 1
fi
echo "✓ Vital.VitalSign table created"
echo ""

# Step 4: Create Dim.VitalQualifier table
echo "[4/8] Creating Dim.VitalQualifier table..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/create/Dim.VitalQualifier.sql
if [ $? -ne 0 ]; then
    echo "Error creating Dim.VitalQualifier table"
    exit 1
fi
echo "✓ Dim.VitalQualifier table created"
echo ""

# Step 5: Insert Dim.VitalQualifier data
echo "[5/8] Inserting Dim.VitalQualifier data..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/insert/Dim.VitalQualifier.sql
if [ $? -ne 0 ]; then
    echo "Error inserting Dim.VitalQualifier data"
    exit 1
fi
echo "✓ Dim.VitalQualifier data inserted"
echo ""

# Step 6: Create Vital.VitalSignQualifier table
echo "[6/8] Creating Vital.VitalSignQualifier table..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/create/Vital.VitalSignQualifier.sql
if [ $? -ne 0 ]; then
    echo "Error creating Vital.VitalSignQualifier table"
    exit 1
fi
echo "✓ Vital.VitalSignQualifier table created"
echo ""

# Step 7: Insert Vital.VitalSign data (large file - may take a few minutes)
echo "[7/8] Inserting Vital.VitalSign data (this may take 2-3 minutes)..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/insert/Vital.VitalSign.sql
if [ $? -ne 0 ]; then
    echo "Error inserting Vital.VitalSign data"
    exit 1
fi
echo "✓ Vital.VitalSign data inserted"
echo ""

# Step 8: Insert Vital.VitalSignQualifier data
echo "[8/8] Inserting Vital.VitalSignQualifier data..."
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -i ${BASE_PATH}/insert/Vital.VitalSignQualifier.sql
if [ $? -ne 0 ]; then
    echo "Error inserting Vital.VitalSignQualifier data"
    exit 1
fi
echo "✓ Vital.VitalSignQualifier data inserted"
echo ""

echo "================================================"
echo "Vitals tables setup complete!"
echo "================================================"
echo ""
echo "Verification:"
sqlcmd -S ${SQL_SERVER} -U ${SQL_USER} -P ${SQL_PASSWORD} -Q "
USE CDWWork;
SELECT 'VitalTypes' as TableName, COUNT(*) as RowCount FROM Dim.VitalType
UNION ALL
SELECT 'VitalSigns', COUNT(*) FROM Vital.VitalSign
UNION ALL
SELECT 'VitalQualifiers', COUNT(*) FROM Dim.VitalQualifier
UNION ALL
SELECT 'VitalSignQualifiers', COUNT(*) FROM Vital.VitalSignQualifier;
"

echo ""
echo "Next steps:"
echo "1. Run ETL Bronze layer: python -m etl.bronze_vitals"
echo "2. Create PostgreSQL table: Execute db/ddl/create_patient_vitals_table.sql"
