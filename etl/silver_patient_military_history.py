# ---------------------------------------------------------------------
# etl/silver_patient_military_history.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version for military history
#  - read from med-z1/bronze/cdwwork/patient_disability
#  - read from med-z1/bronze/cdwwork/patient (for ICN resolution)
#  - join and transform data
#  - save to med-z1/silver/patient_military_history as military_history_cleaned.parquet
# ---------------------------------------------------------------------
# Version History:
#   v1.0 (2026-02-07): Initial Silver transformation - Military History Enhancement
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a module:
#  $ cd med-z1
#  $ python -m etl.silver_patient_military_history
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def transform_military_history_silver():
    """Transform Bronze patient disability data to Silver layer for military history."""

    logger.info("Starting Silver patient military history transformation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Bronze Patient Parquet from MinIO (for ICN resolution)
    patient_path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
    df_patient = minio_client.read_parquet(patient_path)
    logger.info(f"Bronze patient data read: {len(df_patient)} records")

    # Read Bronze Patient Disability Parquet from MinIO
    disability_path = build_bronze_path("cdwwork", "patient_disability", "patient_disability_raw.parquet")
    df_disability = minio_client.read_parquet(disability_path)
    logger.info(f"Bronze patient disability data read: {len(df_disability)} records")

    # Transform and clean disability data
    df_disability_cleaned = df_disability.with_columns([
        # Standardize field names
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("ServiceConnectedFlag").str.strip_chars().alias("service_connected_flag"),
        pl.col("ServiceConnectedPercent").alias("service_connected_percent"),

        # Environmental exposures
        pl.col("AgentOrangeExposureCode").str.strip_chars().alias("agent_orange_exposure"),
        pl.col("AgentOrangeLocation").str.strip_chars().alias("agent_orange_location"),
        pl.col("IonizingRadiationCode").str.strip_chars().alias("ionizing_radiation"),
        pl.col("POWStatusCode").str.strip_chars().alias("pow_status"),
        pl.col("POWLocation").str.strip_chars().alias("pow_location"),
        pl.col("SHADFlag").str.strip_chars().alias("shad_flag"),
        pl.col("SWAsiaCode").str.strip_chars().alias("sw_asia_exposure"),
        pl.col("CampLejeuneFlag").str.strip_chars().alias("camp_lejeune_flag"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
    ])

    # Deduplicate: One record per patient (most recent if multiple exist)
    df_disability_cleaned = df_disability_cleaned.unique(subset=["patient_sid"])
    logger.info(f"After deduplication: {len(df_disability_cleaned)} military history records")

    # Join with patient data to get ICN
    df_patient_icn = df_patient.select([
        pl.col("PatientSID"),
        pl.col("PatientICN").alias("icn"),
    ])

    df = df_disability_cleaned.join(
        df_patient_icn,
        left_on="patient_sid",
        right_on="PatientSID",
        how="inner"  # Only keep disability records with valid patient ICN
    )
    logger.info(f"After ICN join: {len(df)} military history records")

    # Add timestamp
    df = df.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Select final columns
    df = df.select([
        "patient_sid",
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

    # Build Silver path
    silver_path = build_silver_path("patient_military_history", "military_history_cleaned.parquet")

    # Write to MinIO
    minio_client.write_parquet(df, silver_path)
    logger.info("Silver Parquet file written to MinIO")

    logger.info(
        f"Silver transformation complete: {len(df)} military history records written to "
        f"s3://{minio_client.bucket_name}/{silver_path}"
    )

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_military_history_silver()
