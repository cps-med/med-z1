#!/usr/bin/env python3
"""
Check BCMA source data for ICN100004 to find missing drug names.
"""

import polars as pl
from lake.minio_client import MinIOClient, build_bronze_path

print("=" * 80)
print("Checking Bronze BCMA Data for ICN100004")
print("=" * 80)

minio_client = MinIOClient()

# Load Bronze BCMA
bronze_bcma_path = build_bronze_path("cdwwork", "bcma_medicationlog", "bcma_medicationlog_raw.parquet")
df_bcma = minio_client.read_parquet(bronze_bcma_path)

# Load Bronze LocalDrug for reference
bronze_drug_path = build_bronze_path("cdwwork", "local_drug_dim", "local_drug_dim_raw.parquet")
df_drug = minio_client.read_parquet(bronze_drug_path)

# Get patient SID for ICN100004 (should be 1004 based on pattern)
patient_sid = 1004

# Filter BCMA for this patient
df_patient_bcma = df_bcma.filter(pl.col("PatientSID") == patient_sid)

print(f"\nFound {len(df_patient_bcma)} BCMA records for PatientSID {patient_sid} (ICN100004):")
print("-" * 80)

if len(df_patient_bcma) > 0:
    for i in range(len(df_patient_bcma)):
        bcma_sid = df_patient_bcma["BCMAMedicationLogSID"][i]
        local_drug_sid = df_patient_bcma["LocalDrugSID"][i]
        action_type = df_patient_bcma["ActionType"][i]
        action_dt = df_patient_bcma["ActionDateTime"][i]

        print(f"\nBCMA Log SID: {bcma_sid}")
        print(f"  LocalDrugSID: {local_drug_sid}")
        print(f"  Action: {action_type} at {action_dt}")

        # Look up drug in LocalDrug dimension
        if local_drug_sid is not None:
            df_drug_match = df_drug.filter(pl.col("LocalDrugSID") == local_drug_sid)
            if len(df_drug_match) > 0:
                drug_name = df_drug_match["DrugNameWithDose"][0]
                print(f"  ✅ Drug Found in LocalDrug: {drug_name}")
            else:
                print(f"  ❌ LocalDrugSID {local_drug_sid} NOT FOUND in LocalDrug dimension!")
        else:
            print(f"  ❌ LocalDrugSID is NULL in BCMA table!")

else:
    print("  No BCMA records found for this patient!")

# Also check what LocalDrugSIDs exist in our dimension
print("\n" + "=" * 80)
print("Available LocalDrugSID range in Bronze LocalDrug:")
print("=" * 80)
print(f"  Min: {df_drug['LocalDrugSID'].min()}")
print(f"  Max: {df_drug['LocalDrugSID'].max()}")
print(f"  Count: {len(df_drug)}")

# Check if there are any BCMA records with NULL LocalDrugSID
null_drug_bcma = df_bcma.filter(pl.col("LocalDrugSID").is_null())
print(f"\n{len(null_drug_bcma)} BCMA records have NULL LocalDrugSID across all patients")

# Check if there are any BCMA records with LocalDrugSID not in our dimension
all_bcma_drug_sids = df_bcma["LocalDrugSID"].unique().drop_nulls()
all_local_drug_sids = df_drug["LocalDrugSID"].unique()

missing_sids = []
for sid in all_bcma_drug_sids:
    if sid not in all_local_drug_sids.to_list():
        missing_sids.append(sid)

if missing_sids:
    print(f"\n❌ Found {len(missing_sids)} LocalDrugSIDs in BCMA that are missing from LocalDrug dimension:")
    for sid in missing_sids[:10]:
        # Find which BCMA records use this SID
        bcma_using_sid = df_bcma.filter(pl.col("LocalDrugSID") == sid)
        print(f"  LocalDrugSID {sid}: Used in {len(bcma_using_sid)} BCMA records")
else:
    print("\n✅ All LocalDrugSIDs in BCMA exist in LocalDrug dimension")

print("\n" + "=" * 80)
