# ---------------------------------------------------------------------
# gold_inpatient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver encounters data
#  - Read Silver: encounters_merged.parquet (dual-source)
#  - Ensure computed fields are final (is_active, is_recent)
#  - Create patient-centric denormalized view
#  - Preserve data_source tracking ('CDWWork' vs 'CDWWork2')
#  - Save to med-z1/gold/encounters as encounters_final.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.gold_inpatient
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def transform_encounters_gold():
    """
    Transform Silver encounters data to Gold layer.

    Silver layer now contains merged CDWWork + CDWWork2 encounters with:
    - patient_icn already resolved (no lookup needed!)
    - data_source column tracking ('CDWWork' vs 'CDWWork2')
    - Harmonized schema across both sources
    """

    logger.info("=" * 70)
    logger.info("Starting Gold encounters transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver encounters (merged dual-source)
    # ==================================================================
    logger.info("Step 1: Loading Silver encounters...")

    silver_path = build_silver_path("encounters", "encounters_merged.parquet")
    df = minio_client.read_parquet(silver_path)
    logger.info(f"  - Loaded {len(df)} encounters from Silver layer")

    # Log data source distribution
    source_dist = df.group_by("data_source").agg(pl.len().alias("count")).sort("data_source")
    logger.info("  - Data source distribution:")
    for row in source_dist.iter_rows(named=True):
        logger.info(f"    {row['data_source']}: {row['count']} encounters")

    # ==================================================================
    # Step 2: Add patient_key alias (for consistency with other domains)
    # ==================================================================
    logger.info("Step 2: Adding patient_key alias...")

    df = df.with_columns([
        pl.col("patient_icn").alias("patient_key")
    ])

    # Check for any encounters without ICN (should be none)
    missing_icn = df.filter(pl.col("patient_icn").is_null()).shape[0]
    if missing_icn > 0:
        logger.warning(f"  - WARNING: {missing_icn} encounters missing PatientICN")
    else:
        logger.info(f"  - All {len(df)} encounters have PatientICN")

    logger.info(f"  - Sample ICNs: {df.select('patient_icn').unique().head(5)['patient_icn'].to_list()}")

    # ==================================================================
    # Step 3: Calculate encounter statistics
    # ==================================================================
    logger.info("Step 3: Calculating encounter statistics...")

    # Calculate is_active based on discharge_date
    df = df.with_columns([
        pl.when(pl.col("discharge_date").is_null())
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("is_active")
    ])

    active_count = df.filter(pl.col("is_active") == True).shape[0]
    discharged_count = df.filter(pl.col("is_active") == False).shape[0]

    logger.info(f"  - Active admissions: {active_count}")
    logger.info(f"  - Discharged encounters: {discharged_count}")

    # Count by encounter type
    type_counts = df.group_by("encounter_type").agg(pl.len().alias("count")).sort("count", descending=True)
    logger.info(f"  - Encounter types:")
    for row in type_counts.iter_rows(named=True):
        logger.info(f"    - {row['encounter_type']}: {row['count']}")

    # ==================================================================
    # Step 4: Add priority flags (for UI highlighting)
    # ==================================================================
    logger.info("Step 4: Adding priority flags...")

    df = df.with_columns([
        # is_recent: admitted or discharged within last 30 days
        pl.when(
            (pl.col("is_active") == True) |
            ((pl.col("discharge_date").is_not_null()) &
             ((pl.lit(datetime.now(timezone.utc)) - pl.col("discharge_date")).dt.total_days() <= 30))
        )
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("is_recent"),

        # is_extended: active admission with LOS > 14 days (inpatient only)
        pl.when(
            (pl.col("encounter_type") == "INPATIENT") &
            (pl.col("is_active") == True) &
            (pl.col("length_of_stay").is_not_null()) &
            (pl.col("length_of_stay") > 14)
        )
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("is_extended_stay"),

        # admission_category: Categorize based on LOS and status
        pl.when(pl.col("encounter_type") != "INPATIENT")
            .then(pl.col("encounter_type"))  # OUTPATIENT, EMERGENCY
        .when(pl.col("encounter_status").str.to_lowercase() == "active")
            .then(pl.lit("Active Admission"))
        .when(pl.col("length_of_stay").is_null())
            .then(pl.lit("Unknown"))
        .when(pl.col("length_of_stay") == 0)
            .then(pl.lit("Observation"))
        .when(pl.col("length_of_stay") <= 3)
            .then(pl.lit("Short Stay"))
        .when(pl.col("length_of_stay") <= 7)
            .then(pl.lit("Standard Stay"))
        .otherwise(pl.lit("Extended Stay"))
        .alias("admission_category"),
    ])

    recent_count = df.filter(pl.col("is_recent") == True).shape[0]
    extended_count = df.filter(pl.col("is_extended_stay") == True).shape[0]

    logger.info(f"  - Recent encounters (last 30 days): {recent_count}")
    logger.info(f"  - Extended stay (active >14 days): {extended_count}")

    # ==================================================================
    # Step 5: Sort by encounter_date descending
    # ==================================================================
    logger.info("Step 5: Sorting by encounter_date...")

    df = df.sort(["patient_icn", "encounter_date"], descending=[False, True])

    # ==================================================================
    # Step 6: Select final columns for Gold layer
    # ==================================================================
    logger.info("Step 6: Selecting final columns...")

    df = df.select([
        # Patient identity
        "patient_icn",
        "patient_key",

        # Encounter ID
        pl.col("encounter_record_id").alias("encounter_id"),

        # Encounter classification
        "encounter_type",

        # Timing
        pl.col("encounter_date").alias("encounter_datetime"),
        pl.col("admit_date").alias("admit_datetime"),
        pl.col("discharge_date").alias("discharge_datetime"),
        "length_of_stay",

        # Location info
        "admit_location_name",
        "admit_location_type",
        "discharge_location_name",
        "discharge_location_type",

        # Provider
        "provider_name",

        # Diagnosis (may be NULL for CDWWork2)
        "admit_diagnosis_icd10",
        "discharge_diagnosis_icd10",
        "discharge_diagnosis",

        # Discharge disposition (may be NULL for CDWWork2)
        "discharge_disposition",

        # Status and categories
        "encounter_status",
        "is_active",
        "admission_category",

        # Flags for UI
        "is_recent",
        "is_extended_stay",

        # Facility
        "facility_sta3n",
        "facility_name",

        # Data source tracking (CDWWork vs CDWWork2)
        "data_source",

        # Metadata
        "last_updated",
    ])

    # ==================================================================
    # Step 7: Write to Gold layer
    # ==================================================================
    logger.info("Step 7: Writing to Gold layer...")

    gold_path = build_gold_path("encounters", "encounters_final.parquet")
    minio_client.write_parquet(df, gold_path)

    logger.info("=" * 70)
    logger.info(f"Gold transformation complete: {len(df)} encounters written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{gold_path}")
    logger.info(f"  - Active admissions: {active_count}")
    logger.info(f"  - Recent encounters: {recent_count}")
    logger.info(f"  - Extended stays: {extended_count}")
    logger.info("=" * 70)

    return df


# Legacy entry point (for backward compatibility)
def transform_inpatient_gold():
    """
    Legacy entry point - redirects to new dual-source function.
    Maintained for backward compatibility with existing scripts.
    """
    logger.warning("transform_inpatient_gold() is deprecated. Use transform_encounters_gold() instead.")
    return transform_encounters_gold()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_encounters_gold()
