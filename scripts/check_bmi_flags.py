#!/usr/bin/env python3
"""Quick script to check BMI abnormal flags in Gold layer."""

import polars as pl
from lake.minio_client import MinIOClient, build_gold_path

# Initialize MinIO client
minio_client = MinIOClient()

# Read Gold vitals
gold_path = build_gold_path("vitals", "vitals_final.parquet")
df = minio_client.read_parquet(gold_path)

# Filter BMI vitals
bmi_df = df.filter(pl.col("vital_abbr") == "BMI").select([
    "patient_icn",
    "vital_abbr",
    "result_value",
    "numeric_value",
    "abnormal_flag"
]).head(10)

print("BMI vitals in Gold layer:")
print(bmi_df)
