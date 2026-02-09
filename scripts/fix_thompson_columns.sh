#!/usr/bin/env bash
#
# Fix Thompson siblings INSERT scripts - correct column names to match CDWWork schema
#
# This script fixes schema mismatches that cause "Invalid column name" errors
# when inserting Thompson siblings test patient data.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================================================="
echo "  Fixing Thompson Siblings INSERT Scripts - Schema Corrections"
echo "======================================================================="
echo ""

# Navigate to insert directory
cd /Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert

# Backup original files
echo -e "${YELLOW}Creating backups...${NC}"
for file in Thompson-Bailey.sql Thompson-Alananah.sql Thompson-Joe.sql; do
    if [ -f "$file" ]; then
        cp "$file" "$file.backup_$(date +%Y%m%d_%H%M%S)"
        echo "  ✓ Backed up: $file"
    fi
done
echo ""

echo -e "${YELLOW}Applying schema fixes...${NC}"

# Fix all three files with the same corrections
for file in Thompson-Bailey.sql Thompson-Alananah.sql Thompson-Joe.sql; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}  ✗ File not found: $file${NC}"
        continue
    fi

    echo "  Processing: $file"

    # SPatient.SPatientAddress fixes
    sed -i '' 's/PatientAddressSID,/SPatientAddressSID,/g' "$file"
    sed -i '' 's/PatientAddressSID (/SPatientAddressSID (/g' "$file"
    sed -i '' 's/AddressLine1,/StreetAddress1,/g' "$file"
    sed -i '' 's/AddressLine2,/StreetAddress2,/g' "$file"
    sed -i '' 's/AddressLine3,/StreetAddress3,/g' "$file"

    # Vital.VitalSign fixes
    sed -i '' 's/VitalResultNumeric,/NumericValue,/g' "$file"
    sed -i '' 's/VitalResult,/ResultValue,/g' "$file"

    # RxOut.RxOutpat fixes
    sed -i '' 's/PrescribingProviderSID,/OrderingProviderSID,/g' "$file"
    sed -i '' 's/PrescribingProviderName,/OrderingProviderSID,/g' "$file"
    sed -i '' 's/PrescribingProviderIEN,/OrderingProviderIEN,/g' "$file"

    echo -e "${GREEN}  ✓ Fixed: $file${NC}"
done

echo ""
echo -e "${GREEN}=======================================================================${NC}"
echo -e "${GREEN}  Schema corrections applied successfully!${NC}"
echo -e "${GREEN}=======================================================================${NC}"
echo ""
echo "Summary of fixes applied:"
echo "  1. PatientAddressSID → SPatientAddressSID"
echo "  2. AddressLine1/2/3 → StreetAddress1/2/3"
echo "  3. VitalResultNumeric → NumericValue"
echo "  4. VitalResult → ResultValue"
echo "  5. PrescribingProvider* → OrderingProvider*"
echo ""
echo "Next steps:"
echo "  1. Re-run CDWWork INSERT scripts:"
echo "     cd /Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert"
echo "     sqlcmd -S 127.0.0.1,1433 -U sa -P 'MyS3cur3P@ssw0rd' -C -i _master.sql"
echo ""
echo "  2. Verify no schema errors in output"
echo ""
echo "  3. Run ETL pipeline:"
echo "     cd /Users/chuck/swdev/med/med-z1"
echo "     ./scripts/run_all_etl.sh"
echo ""
