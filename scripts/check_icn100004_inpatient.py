#!/usr/bin/env python3
"""
Check inpatient medication data for patient ICN100004.
"""

from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
import polars as pl
from lake.minio_client import MinIOClient, build_gold_path

print("=" * 80)
print("Investigating ICN100004 Inpatient Medication Data Issue")
print("=" * 80)

# ==============================================================================
# Step 1: Check PostgreSQL
# ==============================================================================
print("\nStep 1: Checking PostgreSQL data...")

conn_str = (
    f"postgresql://{POSTGRES_CONFIG['user']}:"
    f"{POSTGRES_CONFIG['password']}@"
    f"{POSTGRES_CONFIG['host']}:"
    f"{POSTGRES_CONFIG['port']}/"
    f"{POSTGRES_CONFIG['database']}"
)
engine = create_engine(conn_str)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            medication_inpatient_id,
            patient_icn,
            drug_name_local,
            action_type,
            action_datetime,
            is_iv_medication,
            schedule,
            administered_by
        FROM clinical.patient_medications_inpatient
        WHERE patient_icn = 'ICN100004'
        ORDER BY action_datetime DESC;
    """))

    rows = [dict(row._mapping) for row in result]

    print(f"\nFound {len(rows)} inpatient medication records for ICN100004 in PostgreSQL:")
    print("-" * 80)

    for row in rows:
        drug_name = row['drug_name_local'] if row['drug_name_local'] else "NULL/BLANK"
        print(f"\nID: {row['medication_inpatient_id']}")
        print(f"  Drug Name: {drug_name}")
        print(f"  Action: {row['action_type']} at {row['action_datetime']}")
        print(f"  IV: {row['is_iv_medication']}, Schedule: {row['schedule']}")
        print(f"  By: {row['administered_by']}")

# ==============================================================================
# Step 2: Check Gold Layer
# ==============================================================================
print("\n" + "=" * 80)
print("Step 2: Checking Gold Layer (Parquet)...")
print("=" * 80)

minio_client = MinIOClient()
gold_path = build_gold_path("medications", "medications_bcma_final.parquet")
df_gold = minio_client.read_parquet(gold_path)

# Filter for ICN100004
df_icn4 = df_gold.filter(pl.col("patient_icn") == "ICN100004")

print(f"\nFound {len(df_icn4)} inpatient medication records for ICN100004 in Gold:")
print("-" * 80)

if len(df_icn4) > 0:
    for i in range(len(df_icn4)):
        print(f"\nRecord {i+1}:")
        print(f"  BCMA Log ID: {df_icn4['bcma_medication_log_id'][i]}")
        print(f"  Drug Name (Local): {df_icn4['drug_name_local_with_dose'][i]}")
        print(f"  Drug Name (National): {df_icn4['drug_name_national'][i]}")
        print(f"  Action: {df_icn4['action_type'][i]} at {df_icn4['action_datetime'][i]}")
        print(f"  IV: {df_icn4['is_iv_medication'][i]}, Schedule: {df_icn4['schedule'][i]}")
        print(f"  By: {df_icn4['administered_by_name'][i]}")
else:
    print("  No records found in Gold layer!")

# ==============================================================================
# Step 3: Compare with other patients
# ==============================================================================
print("\n" + "=" * 80)
print("Step 3: Comparing with other patients...")
print("=" * 80)

# Get a working patient for comparison
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            patient_icn,
            drug_name_local,
            action_type,
            action_datetime
        FROM clinical.patient_medications_inpatient
        WHERE patient_icn IN ('ICN100001', 'ICN100002')
        ORDER BY action_datetime DESC
        LIMIT 3;
    """))

    comparison_rows = [dict(row._mapping) for row in result]

    print("\nComparison - Other patients' inpatient meds:")
    for row in comparison_rows:
        drug_name = row['drug_name_local'] if row['drug_name_local'] else "NULL/BLANK"
        print(f"  {row['patient_icn']}: {drug_name} ({row['action_type']})")

# ==============================================================================
# Step 4: Check raw BCMA data in CDW
# ==============================================================================
print("\n" + "=" * 80)
print("Step 4: Checking mock CDW source data...")
print("=" * 80)

import pyodbc
from config import CDWWORK_CONFIG

# Connect to SQL Server
conn_str_sql = (
    f"DRIVER={{{CDWWORK_CONFIG['driver']}}};"
    f"SERVER={CDWWORK_CONFIG['server']};"
    f"DATABASE={CDWWORK_CONFIG['database']};"
    f"UID={CDWWORK_CONFIG['username']};"
    f"PWD={CDWWORK_CONFIG['password']};"
    f"TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str_sql)
cursor = conn.cursor()

# Get patient SID for ICN100004
cursor.execute("""
    SELECT PatientSID, PatientICN
    FROM SPatient.SPatient
    WHERE PatientICN = 'ICN100004'
""")
patient = cursor.fetchone()

if patient:
    patient_sid = patient[0]
    print(f"\nPatient ICN100004 has PatientSID: {patient_sid}")

    # Get BCMA records
    cursor.execute("""
        SELECT TOP 10
            b.BCMAMedicationLogSID,
            b.PatientSID,
            b.LocalDrugSID,
            b.ActionType,
            b.ActionDateTime,
            ld.DrugNameWithDose,
            ld.LocalDrugSID as LDSIDFromDim
        FROM BCMA.BCMAMedicationLog b
        LEFT JOIN Dim.LocalDrug ld ON b.LocalDrugSID = ld.LocalDrugSID
        WHERE b.PatientSID = ?
        ORDER BY b.ActionDateTime DESC
    """, patient_sid)

    bcma_records = cursor.fetchall()

    print(f"\nFound {len(bcma_records)} BCMA records in mock CDW:")
    for row in bcma_records:
        drug_name = row[5] if row[5] else "NULL"
        print(f"\n  BCMA Log SID: {row[0]}")
        print(f"    LocalDrugSID (BCMA): {row[2]}")
        print(f"    LocalDrugSID (Dim): {row[6]}")
        print(f"    Drug Name: {drug_name}")
        print(f"    Action: {row[3]} at {row[4]}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("Investigation Complete")
print("=" * 80)
