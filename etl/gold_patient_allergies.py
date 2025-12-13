"""
gold_patient_allergies.py

Create Gold layer patient allergies from Silver layer data.
- Read from med-z1/silver/patient_allergies
- Join with Gold patient demographics to get ICN (patient_key)
- Add station name lookups
- Sort allergies (drug first, severity desc, date desc)
- Save to med-z1/gold/patient_allergies as patient_allergies.parquet

To run this script from the project root folder:
  $ cd med-z1
  $ python -m etl.gold_patient_allergies
"""

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def create_gold_patient_allergies():
    """Create Gold patient allergies view in MinIO."""

    logger.info("Starting Gold patient allergies creation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # =========================================================================
    # Read Silver patient allergies from MinIO
    # =========================================================================

    silver_path = build_silver_path("patient_allergies", "patient_allergies_cleaned.parquet")
    df_allergies = minio_client.read_parquet(silver_path)
    logger.info(f"Read {len(df_allergies)} allergy records from Silver layer")

    # =========================================================================
    # Read Gold patient demographics to get ICN mapping
    # =========================================================================

    patient_gold_path = build_gold_path("patient_demographics", "patient_demographics.parquet")
    df_patient = minio_client.read_parquet(patient_gold_path)
    logger.info(f"Read {len(df_patient)} patient records from Gold patient demographics")

    # Select only needed fields from patient demographics
    df_patient_lookup = df_patient.select([
        pl.col("patient_sid"),
        pl.col("patient_key"),  # This is the ICN
    ])

    # =========================================================================
    # Join allergies with patient demographics to get patient_key (ICN)
    # =========================================================================

    df = df_allergies.join(
        df_patient_lookup,
        on="patient_sid",
        how="inner"
    )
    logger.info(f"Joined allergies with patient demographics: {len(df)} records")

    # =========================================================================
    # Add station name lookups
    # =========================================================================

    station_names = {
        "442": "Cheyenne VA Medical Center",
        "518": "Northport VA Medical Center",
        "589": "VA Loma Linda Healthcare System",
        "640": "VA Palo Alto Health Care System",
    }

    df = df.with_columns([
        pl.col("originating_site_sta3n")
            .replace_strict(station_names, default="Unknown Facility")
            .alias("originating_site_name")
    ])

    # =========================================================================
    # Sort allergies for optimal display
    # Sort order: drug allergies first, then by severity (SEVERE first), then by date (most recent first)
    # =========================================================================

    # Prepare sorting: fill null severity ranks with 0
    df = df.with_columns([
        pl.col("severity_rank").fill_null(0).alias("severity_rank"),
    ])

    # Sort with descending order for all columns
    df = df.sort(
        [
            pl.col("is_drug_allergy").cast(pl.Int8),  # Drug allergies first (TRUE=1, FALSE=0)
            pl.col("severity_rank"),                   # SEVERE (3) > MODERATE (2) > MILD (1)
            pl.col("origination_datetime"),            # Most recent first
        ],
        descending=[True, True, True]
    )
    logger.info("Sorted allergies: drug first, severity desc, date desc")

    # =========================================================================
    # Select final Gold schema
    # =========================================================================

    df_gold = df.select([
        "patient_key",                  # ICN (primary identifier for UI)
        "patient_allergy_sid",          # Source system key
        "allergen_local",               # What clinician entered
        "allergen_name",                # Standardized allergen name
        "allergen_type",                # DRUG, FOOD, ENVIRONMENTAL
        "severity_name",                # MILD, MODERATE, SEVERE
        "severity_rank",                # 1, 2, 3
        "reactions",                    # Comma-separated string
        "reaction_count",               # Number of reactions
        "origination_datetime",         # When allergy was recorded
        "observed_datetime",            # When reaction was observed (if applicable)
        "historical_or_observed",       # HISTORICAL or OBSERVED
        "originating_site_sta3n",       # Station number
        "originating_site_name",        # Station name (resolved)
        "comment",                      # Free-text narrative (may be large)
        "verification_status",          # VERIFIED, UNVERIFIED, etc.
        "is_drug_allergy",              # TRUE for drug allergies
        "source_system",                # CDWWork
        "last_updated",                 # Timestamp
    ])

    # =========================================================================
    # Write to Gold layer in MinIO
    # =========================================================================

    gold_path = build_gold_path(
        "patient_allergies",
        "patient_allergies.parquet"
    )

    minio_client.write_parquet(df_gold, gold_path)

    logger.info(
        f"Gold creation complete: {len(df_gold)} allergies written to "
        f"s3://{minio_client.bucket_name}/{gold_path}"
    )

    # Log summary statistics
    drug_count = df_gold.filter(pl.col("is_drug_allergy") == True).shape[0]
    food_count = df_gold.filter(pl.col("allergen_type") == "FOOD").shape[0]
    env_count = df_gold.filter(pl.col("allergen_type") == "ENVIRONMENTAL").shape[0]
    severe_count = df_gold.filter(pl.col("severity_name") == "SEVERE").shape[0]

    logger.info(f"Summary: {len(df_gold)} total allergies")
    logger.info(f"  - Drug: {drug_count}")
    logger.info(f"  - Food: {food_count}")
    logger.info(f"  - Environmental: {env_count}")
    logger.info(f"  - Severe: {severe_count}")

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Starting Gold ETL: Patient Allergies")
    create_gold_patient_allergies()
    logger.info("Gold ETL: Patient Allergies complete")
