# ---------------------------------------------------------------------
# gold_inpatient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver inpatient data
#  - Read Silver: inpatient_cleaned.parquet
#  - Add patient identity (PatientSID → PatientICN)
#  - Ensure computed fields are final (is_active, admission_category)
#  - Create patient-centric denormalized view
#  - Save to med-z1/gold/inpatient as inpatient_final.parquet
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


def transform_inpatient_gold():
    """Transform Silver inpatient data to Gold layer."""

    logger.info("=" * 70)
    logger.info("Starting Gold inpatient transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver inpatient
    # ==================================================================
    logger.info("Step 1: Loading Silver inpatient...")

    silver_path = build_silver_path("inpatient", "inpatient_cleaned.parquet")
    df = minio_client.read_parquet(silver_path)
    logger.info(f"  - Loaded {len(df)} encounters from Silver layer")

    # ==================================================================
    # Step 2: Generate patient ICN from patient_sid
    # ==================================================================
    logger.info("Step 2: Generating patient ICN from patient_sid...")

    # Patient ICN Resolution Strategy (same pattern as vitals/medications):
    # PatientSID in different tables may have different ranges, but they map
    # to the same ICN using: ICN = "ICN" + str(100000 + patient_sid)
    #
    # For inpatient encounters:
    #   patient_sid=1001 → ICN100001
    #   patient_sid=1002 → ICN100002
    #   ...
    #   patient_sid=1036 → ICN100036
    df = df.with_columns([
        pl.format("ICN{}", (100000 + pl.col("patient_sid"))).alias("patient_icn"),
        pl.format("ICN{}", (100000 + pl.col("patient_sid"))).alias("patient_key"),
    ])

    logger.info(f"  - Generated patient ICN for all {len(df)} encounters")
    logger.info(f"  - Sample ICNs: {df.select('patient_icn').unique().head(5)['patient_icn'].to_list()}")

    # ==================================================================
    # Step 3: Calculate encounter statistics
    # ==================================================================
    logger.info("Step 3: Calculating encounter statistics...")

    active_count = df.filter(pl.col("is_active") == True).shape[0]
    discharged_count = df.filter(pl.col("is_active") == False).shape[0]

    logger.info(f"  - Active admissions: {active_count}")
    logger.info(f"  - Discharged encounters: {discharged_count}")

    # Count admission categories
    category_counts = df.group_by("admission_category").agg(pl.len()).sort("len", descending=True)
    logger.info(f"  - Admission categories:")
    for row in category_counts.iter_rows(named=True):
        logger.info(f"    - {row['admission_category']}: {row['len']}")

    # ==================================================================
    # Step 4: Add priority flag (for UI highlighting)
    # ==================================================================
    logger.info("Step 4: Adding priority flags...")

    df = df.with_columns([
        # is_recent: admitted or discharged within last 30 days
        pl.when(
            (pl.col("is_active") == True) |
            ((pl.col("discharge_datetime").is_not_null()) &
             ((pl.lit(datetime.now(timezone.utc)) - pl.col("discharge_datetime")).dt.total_days() <= 30))
        )
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("is_recent"),

        # is_extended: active admission with LOS > 14 days
        pl.when(
            (pl.col("is_active") == True) &
            (pl.col("total_days") > 14)
        )
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("is_extended_stay"),
    ])

    recent_count = df.filter(pl.col("is_recent") == True).shape[0]
    extended_count = df.filter(pl.col("is_extended_stay") == True).shape[0]

    logger.info(f"  - Recent encounters (last 30 days): {recent_count}")
    logger.info(f"  - Extended stay (active >14 days): {extended_count}")

    # ==================================================================
    # Step 5: Sort by admit_datetime descending
    # ==================================================================
    logger.info("Step 5: Sorting by admit_datetime...")

    df = df.sort("admit_datetime", descending=True)

    # ==================================================================
    # Step 6: Select final columns for Gold layer
    # ==================================================================
    logger.info("Step 6: Selecting final columns...")

    df = df.select([
        # Patient identity
        "patient_icn",
        "patient_key",
        "patient_sid",

        # Encounter ID
        "inpatient_id",

        # Admission info
        "admit_datetime",
        "admit_location_id",
        "admit_location_name",
        "admit_location_type",
        "admit_diagnosis_code",
        "admitting_provider_id",
        "admitting_provider_name",

        # Discharge info
        "discharge_datetime",
        "discharge_date_id",
        "discharge_location_id",
        "discharge_location_name",
        "discharge_location_type",
        "discharge_diagnosis_code",
        "discharge_diagnosis_text",
        "discharge_disposition",

        # Metrics
        "length_of_stay",
        "total_days",
        "encounter_status",
        "is_active",
        "admission_category",

        # Flags for UI
        "is_recent",
        "is_extended_stay",

        # Facility
        "sta3n",
        "facility_name",

        # Metadata
        "source_system",
        "last_updated",
    ])

    # ==================================================================
    # Step 7: Write to Gold layer
    # ==================================================================
    logger.info("Step 7: Writing to Gold layer...")

    gold_path = build_gold_path("inpatient", "inpatient_final.parquet")
    minio_client.write_parquet(df, gold_path)

    logger.info("=" * 70)
    logger.info(f"Gold transformation complete: {len(df)} encounters written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{gold_path}")
    logger.info(f"  - Active admissions: {active_count}")
    logger.info(f"  - Recent encounters: {recent_count}")
    logger.info(f"  - Extended stays: {extended_count}")
    logger.info("=" * 70)

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_inpatient_gold()
