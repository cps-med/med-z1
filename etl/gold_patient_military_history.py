# ---------------------------------------------------------------------
# etl/gold_patient_military_history.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver version
#  - read from med-z1/silver/patient_military_history
#  - save to med-z1/gold/patient_military_history as military_history.parquet
# ---------------------------------------------------------------------
# Version History:
#   v1.0 (2026-02-07): Initial Gold transformation - Military History Enhancement
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a module:
#  $ cd med-z1
#  $ python -m etl.gold_patient_military_history
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def create_gold_military_history():
    """Create Gold patient military history view in MinIO."""

    logger.info("Starting Gold patient military history creation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Silver Parquet from MinIO
    silver_path = build_silver_path("patient_military_history", "military_history_cleaned.parquet")
    df_military = minio_client.read_parquet(silver_path)
    logger.info(f"Silver military history data read: {len(df_military)} records")

    # Create patient_key (use ICN)
    df_military = df_military.with_columns([
        pl.col("icn").alias("patient_key")
    ])

    # Final Gold schema
    df_gold = df_military.select([
        "patient_key",
        "patient_sid",  # Keep for potential joins
        "icn",
        "service_connected_flag",
        "service_connected_percent",
        "agent_orange_exposure",
        "agent_orange_location",
        "ionizing_radiation",
        "pow_status",
        "pow_location",
        "shad_flag",
        "sw_asia_exposure",
        "camp_lejeune_flag",
        "source_system",
        "last_updated",
    ])

    # Build Gold path
    gold_path = build_gold_path(
        "patient_military_history",
        "military_history.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df_gold, gold_path)

    logger.info(
        f"Gold creation complete: {len(df_gold)} military history records written to "
        f"s3://{minio_client.bucket_name}/{gold_path}"
    )

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    create_gold_military_history()
