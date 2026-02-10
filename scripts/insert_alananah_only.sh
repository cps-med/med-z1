#!/bin/bash
# Insert Thompson-Alananah data only (does not rebuild database)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SQL_DIR="$PROJECT_ROOT/mock/sql-server/cdwwork/insert"

echo "============================================================"
echo "Inserting Thompson-Alananah data into SQL Server"
echo "============================================================"

docker exec sqlserver2019 /opt/mssql-tools18/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P 'AllieD-1993-2025-z1' \
    -d CDWWork \
    -i /var/opt/mssql/Thompson-Alananah.sql \
    -C

echo ""
echo "============================================================"
echo "Verifying Thompson-Alananah data in SQL Server"
echo "============================================================"

docker exec sqlserver2019 /opt/mssql-tools18/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P 'AllieD-1993-2025-z1' \
    -d CDWWork \
    -Q "
SELECT 'Demographics' as Domain, COUNT(*) as Count FROM SPatient.SPatient WHERE PatientSID = 2002
UNION ALL SELECT 'Vitals', COUNT(*) FROM Vital.VitalSign WHERE PatientSID = 2002
UNION ALL SELECT 'Problems', COUNT(*) FROM Outpat.ProblemList WHERE PatientSID = 2002
UNION ALL SELECT 'Medications', COUNT(*) FROM RxOut.RxOutpat WHERE PatientSID = 2002
UNION ALL SELECT 'Encounters', COUNT(*) FROM Inpat.Inpatient WHERE PatientSID = 2002
UNION ALL SELECT 'Clinical Notes', COUNT(*) FROM TIU.TIUDocument_8925 WHERE PatientSID = 2002
UNION ALL SELECT 'Patient Flags', COUNT(*) FROM SPatient.PatientRecordFlagAssignment WHERE PatientSID = 2002
UNION ALL SELECT 'Immunizations', COUNT(*) FROM Immunization.PatientImmunization WHERE PatientSID = 2002
ORDER BY Domain;
" \
    -C

echo ""
echo "✅ Thompson-Alananah data inserted successfully"
