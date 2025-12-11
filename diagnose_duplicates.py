#!/usr/bin/env python3
# ---------------------------------------------------------------------
# diagnose_duplicates.py
# ---------------------------------------------------------------------
# Diagnostic script to identify source of duplicate patient records
# ---------------------------------------------------------------------

import polars as pl
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_bronze_patient():
    """Check for duplicates in Bronze patient data."""
    logger.info("=" * 70)
    logger.info("Checking Bronze Patient Data")
    logger.info("=" * 70)

    minio_client = MinIOClient()
    bronze_path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
    df = minio_client.read_parquet(bronze_path)

    logger.info(f"Total rows: {len(df)}")
    logger.info(f"Unique PatientSID: {df.select('PatientSID').n_unique()}")
    logger.info(f"Unique PatientICN: {df.select('PatientICN').n_unique()}")

    # Check for duplicate PatientSIDs
    duplicates = df.group_by("PatientSID").agg(pl.count().alias("count")).filter(pl.col("count") > 1)
    if len(duplicates) > 0:
        logger.warning(f"Found {len(duplicates)} duplicate PatientSIDs in Bronze patient data:")
        print(duplicates)
    else:
        logger.info("✅ No duplicate PatientSIDs in Bronze patient data")

    return df


def check_bronze_address():
    """Check address data for patients."""
    logger.info("\n" + "=" * 70)
    logger.info("Checking Bronze Address Data")
    logger.info("=" * 70)

    minio_client = MinIOClient()
    address_path = build_bronze_path("cdwwork", "patient_address", "patient_address_raw.parquet")
    df = minio_client.read_parquet(address_path)

    logger.info(f"Total address rows: {len(df)}")

    # Filter for primary addresses (OrdinalNumber = 1, AddressType = 'HOME')
    primary = df.filter(
        (pl.col("OrdinalNumber") == 1) &
        (pl.col("AddressType") == "HOME")
    )
    logger.info(f"Primary addresses (OrdinalNumber=1, AddressType='HOME'): {len(primary)}")
    logger.info(f"Unique PatientSID in primary addresses: {primary.select('PatientSID').n_unique()}")

    # Check for patients with multiple primary addresses
    dup_addresses = primary.group_by("PatientSID").agg(pl.count().alias("count")).filter(pl.col("count") > 1)
    if len(dup_addresses) > 0:
        logger.warning(f"Found {len(dup_addresses)} patients with multiple primary addresses:")
        print(dup_addresses)

        # Show details for these patients
        dup_patient_sids = dup_addresses.select("PatientSID").to_series().to_list()
        dup_details = df.filter(pl.col("PatientSID").is_in(dup_patient_sids)).sort("PatientSID", "OrdinalNumber")
        print("\nDetails:")
        print(dup_details.select(["PatientSID", "OrdinalNumber", "AddressType", "StreetAddress1", "City"]))
    else:
        logger.info("✅ No patients with multiple primary addresses")

    return df


def check_bronze_insurance():
    """Check insurance data for patients."""
    logger.info("\n" + "=" * 70)
    logger.info("Checking Bronze Insurance Data")
    logger.info("=" * 70)

    minio_client = MinIOClient()
    insurance_path = build_bronze_path("cdwwork", "patient_insurance", "patient_insurance_raw.parquet")
    df = minio_client.read_parquet(insurance_path)

    logger.info(f"Total insurance rows: {len(df)}")
    logger.info(f"Unique PatientSID: {df.select('PatientSID').n_unique()}")

    # Check for patients with multiple insurance records
    multiple_insurance = df.group_by("PatientSID").agg(pl.count().alias("count")).filter(pl.col("count") > 1)
    if len(multiple_insurance) > 0:
        logger.info(f"Patients with multiple insurance records: {len(multiple_insurance)}")
        logger.info("(This is expected - we select the most recent by PolicyEffectiveDate)")

    return df


def check_silver_patient():
    """Check Silver patient data for duplicates."""
    logger.info("\n" + "=" * 70)
    logger.info("Checking Silver Patient Data")
    logger.info("=" * 70)

    minio_client = MinIOClient()
    silver_path = build_silver_path("patient", "patient_cleaned.parquet")
    df = minio_client.read_parquet(silver_path)

    logger.info(f"Total rows: {len(df)}")
    logger.info(f"Unique patient_sid: {df.select('patient_sid').n_unique()}")
    logger.info(f"Unique icn: {df.select('icn').n_unique()}")

    # Check for duplicate ICNs
    dup_icns = df.group_by("icn").agg(pl.count().alias("count")).filter(pl.col("count") > 1)
    if len(dup_icns) > 0:
        logger.warning(f"Found {len(dup_icns)} duplicate ICNs in Silver data:")
        print(dup_icns)

        # Show details for first few duplicates
        sample_icn = dup_icns.head(3).select("icn").to_series().to_list()
        logger.info(f"\nShowing details for first few duplicates:")
        for icn in sample_icn:
            dup_records = df.filter(pl.col("icn") == icn)
            print(f"\n{icn} ({len(dup_records)} records):")
            print(dup_records.select([
                "patient_sid", "icn", "name_display",
                "address_street1", "address_city", "insurance_company_name"
            ]))

    return df


if __name__ == "__main__":
    logger.info("Starting duplicate diagnosis...\n")

    # Check each layer
    bronze_patient = check_bronze_patient()
    bronze_address = check_bronze_address()
    bronze_insurance = check_bronze_insurance()
    silver_patient = check_silver_patient()

    logger.info("\n" + "=" * 70)
    logger.info("Diagnosis Complete")
    logger.info("=" * 70)
