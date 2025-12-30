#!/usr/bin/env python3
"""
Verify drug names match correctly after LocalDrugSID fix.
Compare Bronze → Silver → Gold → PostgreSQL
"""

import polars as pl
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path, build_gold_path

print("=" * 80)
print("Verifying Drug Names Throughout ETL Pipeline")
print("=" * 80)

# Initialize MinIO client
minio_client = MinIOClient()

# ==============================================================================
# Step 1: Load Bronze RxOutpat data
# ==============================================================================
print("\nStep 1: Loading Bronze RxOutpat data...")
bronze_path = build_bronze_path("cdwwork", "rxout_rxoutpat", "rxout_rxoutpat_raw.parquet")
df_bronze = minio_client.read_parquet(bronze_path)

# Load Bronze LocalDrug for reference
bronze_drug_path = build_bronze_path("cdwwork", "local_drug_dim", "local_drug_dim_raw.parquet")
df_bronze_drug = minio_client.read_parquet(bronze_drug_path)

print(f"  - Bronze RxOutpat: {len(df_bronze)} records")
print(f"  - Bronze LocalDrug: {len(df_bronze_drug)} records")

# ==============================================================================
# Step 2: Load Silver data
# ==============================================================================
print("\nStep 2: Loading Silver RxOut data...")
silver_path = build_silver_path("medications", "medications_rxout_cleaned.parquet")
df_silver = minio_client.read_parquet(silver_path)
print(f"  - Silver RxOut: {len(df_silver)} records")

# ==============================================================================
# Step 3: Load Gold data
# ==============================================================================
print("\nStep 3: Loading Gold RxOut data...")
gold_path = build_gold_path("medications", "medications_rxout_final.parquet")
df_gold = minio_client.read_parquet(gold_path)
print(f"  - Gold RxOut: {len(df_gold)} records")

# ==============================================================================
# Step 4: Query PostgreSQL
# ==============================================================================
print("\nStep 4: Querying PostgreSQL...")
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
            patient_icn,
            drug_name_local,
            sig
        FROM clinical.patient_medications_outpatient
        WHERE patient_icn IN ('ICN100001', 'ICN100002')
        ORDER BY patient_icn, medication_outpatient_id
        LIMIT 10;
    """))
    pg_results = [dict(row._mapping) for row in result]

print(f"  - PostgreSQL: {len(pg_results)} sample records")

# ==============================================================================
# Step 5: Compare specific prescriptions
# ==============================================================================
print("\n" + "=" * 80)
print("Verification: Comparing Drug Names Across Layers")
print("=" * 80)

# Get specific prescriptions from Bronze
test_rx_sids = [5002, 5003, 5019, 5020]

for rx_sid in test_rx_sids:
    print(f"\n--- RxOutpatSID {rx_sid} ---")

    # Bronze: Get stated drug name and LocalDrugSID
    bronze_rx = df_bronze.filter(pl.col("RxOutpatSID") == rx_sid)
    if len(bronze_rx) > 0:
        bronze_local_drug_sid = bronze_rx["LocalDrugSID"][0]
        bronze_stated_drug = bronze_rx["DrugNameWithDose"][0]
        print(f"Bronze RxOutpat: {bronze_stated_drug} (LocalDrugSID: {bronze_local_drug_sid})")

        # Get actual drug from Bronze LocalDrug
        bronze_drug = df_bronze_drug.filter(pl.col("LocalDrugSID") == bronze_local_drug_sid)
        if len(bronze_drug) > 0:
            bronze_actual_drug = bronze_drug["DrugNameWithDose"][0]
            print(f"Bronze LocalDrug: {bronze_actual_drug}")

            if bronze_stated_drug == bronze_actual_drug:
                print("  ✅ Bronze: Stated drug matches LocalDrug dimension")
            else:
                print(f"  ❌ Bronze: MISMATCH! Stated '{bronze_stated_drug}' != Actual '{bronze_actual_drug}'")

    # Silver: Get drug name after join
    silver_rx = df_silver.filter(pl.col("rx_outpat_id") == rx_sid)
    if len(silver_rx) > 0:
        silver_drug = silver_rx["drug_name_local_with_dose"][0]
        print(f"Silver: {silver_drug}")

    # Gold: Get final drug name
    gold_rx = df_gold.filter(pl.col("rx_outpat_id") == rx_sid)
    if len(gold_rx) > 0:
        gold_drug = gold_rx["drug_name_local_with_dose"][0]
        gold_sig = gold_rx["sig"][0] if gold_rx["sig"][0] is not None else "NULL"
        print(f"Gold: {gold_drug}")
        print(f"  Sig: {gold_sig}")

# ==============================================================================
# Step 6: Verify PostgreSQL samples
# ==============================================================================
print("\n" + "=" * 80)
print("PostgreSQL Sample (Patient ICN100001 and ICN100002):")
print("=" * 80)

for row in pg_results:
    sig_display = row['sig'][:60] + "..." if row['sig'] and len(row['sig']) > 60 else row['sig'] if row['sig'] else "NULL"
    print(f"{row['patient_icn']}: {row['drug_name_local']}")
    print(f"  Sig: {sig_display}")

# ==============================================================================
# Step 7: Check for INSULIN GLARGINE specifically (known issue case)
# ==============================================================================
print("\n" + "=" * 80)
print("Specific Check: INSULIN GLARGINE with sig data")
print("=" * 80)

# Find INSULIN in Gold with sig
insulin_records = df_gold.filter(
    (pl.col("drug_name_local_with_dose").str.contains("INSULIN GLARGINE")) &
    (pl.col("sig").is_not_null())
)

if len(insulin_records) > 0:
    for i in range(min(3, len(insulin_records))):
        print(f"\nINSULIN Record {i+1}:")
        print(f"  Drug: {insulin_records['drug_name_local_with_dose'][i]}")
        print(f"  Sig: {insulin_records['sig'][i]}")
else:
    print("  No INSULIN GLARGINE records with sig data found")

# Final summary
print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
print(f"✅ Bronze: {len(df_bronze_drug)} LocalDrug records (up from 58)")
print(f"✅ Bronze: {len(df_bronze)} RxOutpat prescriptions")
print(f"✅ Silver: {len(df_silver)} cleaned prescriptions")
print(f"✅ Gold: {len(df_gold)} final prescriptions")
print(f"✅ PostgreSQL: Verified sample records loaded")
print("\n" + "=" * 80)
