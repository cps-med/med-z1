# ---------------------------------------------------------------------
# gold_patient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver version
#  - read from from med-z1/silver/patient
#  - save to med-z1/gold/patient_demographics
#  - as patient_demographics.parquet
# ---------------------------------------------------------------------
# Updated 2025-12-11 to include address, phone, and insurance fields
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a
# module (for now... there are other options to consider later).
#  $ cd med-z1
#  $ python -m etl.gold_patient
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def create_gold_patient_demographics():
    """Create Gold patient demographics view in MinIO."""

    logger.info("Starting Gold patient demographics creation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Silver Parquet from MinIO
    silver_path = build_silver_path("patient", "patient_cleaned.parquet")
    df_patient = minio_client.read_parquet(silver_path)

    # Add station names (simplified for Phase 1)
    station_names = {
        "508": "Atlanta, GA VA Medical Center",
        "516": "Bay Pines, FL VA Medical Center",
        "552": "Dayton, OH VA Medical Center",
        "688": "Washington, DC VA Medical Center",
    }

    df_patient = df_patient.with_columns([
        pl.col("primary_station").replace_strict(station_names, default="Unknown Facility")
            .alias("primary_station_name")
    ])

    # Create patient_key (use ICN)
    df_patient = df_patient.with_columns([
        pl.col("icn").alias("patient_key")
    ])

    # Final Gold schema
    df_gold = df_patient.select([
        "patient_key",
        "patient_sid",      # Keep for joins with other Gold tables
        "icn",
        "ssn",
        "ssn_last4",
        "name_last",
        "name_first",
        "name_display",
        "dob",
        "age",
        "sex",
        "primary_station",
        "primary_station_name",
        "address_street1",
        "address_street2",
        "address_city",
        "address_state",
        "address_zip",
        "phone_primary",
        "insurance_company_name",
        "source_system",
        "last_updated",
    ])

    # Build Gold path
    gold_path = build_gold_path(
        "patient_demographics",
        "patient_demographics.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df_gold, gold_path)

    logger.info(
        f"Gold creation complete: {len(df_gold)} patients written to "
        f"s3://{minio_client.bucket_name}/{gold_path}"
    )

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    create_gold_patient_demographics()