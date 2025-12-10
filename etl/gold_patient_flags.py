# ---------------------------------------------------------------------
# gold_patient_flags.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver patient flags data
#  - read from med-z1/silver/patient_record_flag_*
#  - join tables, calculate review status
#  - create patient-centric denormalized view
#  - map PatientSID to PatientICN/PatientKey
#  - save to med-z1/gold/patient_flags
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a
# module:
#  $ cd med-z1
#  $ python -m etl.gold_patient_flags
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone, timedelta
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def calculate_review_status(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate review status based on next_review_datetime and review_notification_days.

    Status categories:
    - CURRENT: next_review_date > (today + notification_days)
    - DUE SOON: today <= next_review_date <= (today + notification_days)
    - OVERDUE: next_review_date < today
    - N/A: No review date set
    """
    # Use timezone-naive datetime for comparison (Silver layer datetimes are naive)
    today = datetime.now()

    df = df.with_columns([
        pl.when(pl.col("next_review_datetime").is_null())
          .then(pl.lit("N/A"))
          .when(pl.col("next_review_datetime") < today)
          .then(pl.lit("OVERDUE"))
          .when(
              pl.col("next_review_datetime") <=
              (pl.lit(today) + pl.duration(days=pl.col("review_notification_days")))
          )
          .then(pl.lit("DUE SOON"))
          .otherwise(pl.lit("CURRENT"))
          .alias("review_status")
    ])

    return df


def create_gold_patient_flags():
    """
    Create Gold patient flags view in MinIO.
    Joins assignments with dimension and latest history, maps to patient ICN.
    """
    logger.info("=" * 70)
    logger.info("Starting Gold Patient Flags Creation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # -------------------------------------------------------------------------
    # 1. Read Silver Parquet files
    # -------------------------------------------------------------------------
    logger.info("Reading Silver Parquet files...")

    # Read assignments
    assignments_path = build_silver_path(
        "patient_record_flag_assignment",
        "patient_record_flag_assignment_cleaned.parquet"
    )
    df_assignments = minio_client.read_parquet(assignments_path)
    logger.info(f"Read {len(df_assignments)} assignments from Silver")

    # Read dimension
    dimension_path = build_silver_path(
        "patient_record_flag_dim",
        "patient_record_flag_dim_cleaned.parquet"
    )
    df_dimension = minio_client.read_parquet(dimension_path)
    logger.info(f"Read {len(df_dimension)} flag definitions from Silver")

    # Read history
    history_path = build_silver_path(
        "patient_record_flag_history",
        "patient_record_flag_history_cleaned.parquet"
    )
    df_history = minio_client.read_parquet(history_path)
    logger.info(f"Read {len(df_history)} history records from Silver")

    # Read patient demographics (for PatientSID -> ICN mapping)
    patient_demographics_path = build_gold_path(
        "patient_demographics",
        "patient_demographics.parquet"
    )
    df_patients = minio_client.read_parquet(patient_demographics_path)
    logger.info(f"Read {len(df_patients)} patients from Gold demographics")

    # -------------------------------------------------------------------------
    # 2. Get most recent history action for each assignment
    # -------------------------------------------------------------------------
    logger.info("Getting most recent history for each assignment...")

    # Get the most recent history record per assignment
    df_latest_history = (
        df_history
        .sort("history_datetime", descending=True)
        .group_by("assignment_sid")
        .first()
        .select([
            "assignment_sid",
            pl.col("history_datetime").alias("last_action_date"),
            pl.col("action_name").alias("last_action"),
            pl.col("entered_by_name").alias("last_action_by")
        ])
    )
    logger.info(f"Extracted {len(df_latest_history)} latest history records")

    # -------------------------------------------------------------------------
    # 3. Join assignments with latest history
    # -------------------------------------------------------------------------
    logger.info("Joining assignments with latest history...")

    df = df_assignments.join(
        df_latest_history,
        on="assignment_sid",
        how="left"
    )

    # -------------------------------------------------------------------------
    # 4. Calculate review status
    # -------------------------------------------------------------------------
    logger.info("Calculating review status...")
    df = calculate_review_status(df)

    # -------------------------------------------------------------------------
    # 5. Map PatientSID to patient_key (ICN)
    # -------------------------------------------------------------------------
    logger.info("Mapping PatientSID to patient_key (ICN)...")

    # Create a lookup from patient_sid to patient_key
    # Ensure patient_sid is Int64 for consistent join
    patient_lookup = df_patients.select([
        pl.col("patient_sid").cast(pl.Int64),
        pl.col("patient_key")
    ])

    # Ensure patient_sid in flags is also Int64
    df = df.with_columns([
        pl.col("patient_sid").cast(pl.Int64)
    ])

    # Debug: Log sample values before join
    logger.info(f"Sample patient_sid from flags: {df.select('patient_sid').head(5)['patient_sid'].to_list()}")
    logger.info(f"Sample patient_sid from demographics: {patient_lookup.select('patient_sid').head(5)['patient_sid'].to_list()}")
    logger.info(f"Total unique patient_sid in flags: {df.select('patient_sid').n_unique()}")
    logger.info(f"Total unique patient_sid in demographics: {patient_lookup.select('patient_sid').n_unique()}")

    df = df.join(
        patient_lookup,
        on="patient_sid",
        how="inner"  # Only keep flags for patients we have demographics for
    )

    logger.info(f"Mapped {len(df)} assignments to patient_key")

    # -------------------------------------------------------------------------
    # 6. Create final Gold schema (denormalized, patient-centric)
    # -------------------------------------------------------------------------
    logger.info("Creating final Gold schema...")

    df_gold = df.select([
        "patient_key",
        "assignment_sid",
        "flag_name",
        "flag_category",
        "flag_source_type",
        "is_active",
        "assignment_status",
        pl.col("assignment_datetime").alias("assignment_date"),
        pl.col("inactivation_datetime").alias("inactivation_date"),
        "owner_site_sta3n",
        "owner_site_name",
        "originating_site_sta3n",
        "originating_site_name",
        "review_frequency_days",
        "review_notification_days",
        pl.col("next_review_datetime").alias("next_review_date"),
        "review_status",
        "last_action_date",
        "last_action",
        "last_action_by",
        pl.col("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated")
    ])

    # -------------------------------------------------------------------------
    # 7. Sort by patient and category (National first, then Local)
    # -------------------------------------------------------------------------
    df_gold = df_gold.sort(
        ["patient_key", "flag_category", "assignment_date"],
        descending=[False, False, True]  # patient asc, category asc, date desc
    )

    # -------------------------------------------------------------------------
    # 8. Write to Gold layer
    # -------------------------------------------------------------------------
    gold_path = build_gold_path(
        "patient_flags",
        "patient_flags.parquet"
    )

    minio_client.write_parquet(df_gold, gold_path)

    logger.info("=" * 70)
    logger.info("Gold Patient Flags Creation Complete")
    logger.info(f"  - Total flags: {len(df_gold)} records")
    logger.info(f"  - Active flags: {df_gold.filter(pl.col('is_active')).height}")
    logger.info(f"  - Output: s3://{minio_client.bucket_name}/{gold_path}")
    logger.info("=" * 70)

    # Log review status distribution
    status_counts = df_gold.group_by("review_status").agg(pl.len().alias("count")).sort("review_status")
    logger.info("Review Status Distribution:")
    for row in status_counts.iter_rows(named=True):
        logger.info(f"  - {row['review_status']}: {row['count']}")

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    create_gold_patient_flags()
