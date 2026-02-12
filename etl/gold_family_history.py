# ---------------------------------------------------------------------
# gold_family_history.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver family-history data.
#  - Add patient-level metrics (active count, first-degree count, high-risk count)
#  - Derive first-degree flags for clinical risk context and AI consumption
#  - Keep row-level detail for UI timeline/table rendering
#  - Save to gold/patient_family_history/patient_family_history_final.parquet
# ---------------------------------------------------------------------

import logging
from datetime import datetime, timezone

import polars as pl

from lake.minio_client import MinIOClient, build_gold_path, build_silver_path

logger = logging.getLogger(__name__)


FIRST_DEGREE_CODES = ["MOTHER", "FATHER", "SISTER", "BROTHER", "SON", "DAUGHTER"]


def transform_family_history_gold():
    logger.info("=" * 70)
    logger.info("Starting Gold Family History transformation")
    logger.info("=" * 70)

    minio_client = MinIOClient()

    # ------------------------------------------------------------------
    # Step 1: Load Silver family history
    # ------------------------------------------------------------------
    logger.info("Step 1: Loading Silver family-history...")
    silver_path = build_silver_path("family_history", "family_history_harmonized.parquet")
    df = minio_client.read_parquet(silver_path)
    logger.info(f"  - Loaded {len(df)} family-history rows")

    # ------------------------------------------------------------------
    # Step 2: Derive row-level risk flags
    # ------------------------------------------------------------------
    logger.info("Step 2: Deriving row-level risk flags...")

    df = df.with_columns([
        (
            (pl.col("relationship_degree") == "FIRST_DEGREE")
            | pl.col("relationship_code").is_in(FIRST_DEGREE_CODES)
        ).alias("first_degree_relative_flag"),
        pl.col("condition_category")
        .fill_null("Unknown")
        .alias("risk_condition_group"),
        pl.col("clinical_status")
        .fill_null("UNKNOWN")
        .str.to_uppercase()
        .alias("clinical_status"),
        pl.col("is_active").fill_null(True).alias("is_active"),
    ])

    # ------------------------------------------------------------------
    # Step 3: Build patient-level counts and join back
    # ------------------------------------------------------------------
    logger.info("Step 3: Calculating patient-level family-history metrics...")

    df_patient_counts = (
        df.group_by("patient_icn")
        .agg([
            pl.len().alias("family_history_count_total"),
            pl.col("is_active").cast(pl.Int8).sum().alias("family_history_count_active"),
            pl.col("first_degree_relative_flag").cast(pl.Int8).sum().alias("family_history_first_degree_count"),
            (
                pl.col("first_degree_relative_flag") & pl.col("hereditary_risk_flag").fill_null(False)
            ).cast(pl.Int8).sum().alias("family_history_first_degree_high_risk_count"),
        ])
    )

    df_gold = df.join(df_patient_counts, on="patient_icn", how="left")

    # ------------------------------------------------------------------
    # Step 4: Add Gold metadata and write output
    # ------------------------------------------------------------------
    logger.info("Step 4: Writing Gold output...")

    df_gold = df_gold.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("gold_load_datetime"),
        pl.lit("v1.0").alias("gold_schema_version"),
    ])

    # Keep a stable, patient-timeline friendly ordering
    df_gold = df_gold.sort(["patient_icn", "recorded_datetime"], descending=[False, True])

    gold_path = build_gold_path("patient_family_history", "patient_family_history_final.parquet")
    minio_client.write_parquet(df_gold, gold_path)

    logger.info(
        f"Gold transformation complete: {len(df_gold)} records written to "
        f"s3://{minio_client.bucket_name}/{gold_path}"
    )

    patient_count = df_gold.select(pl.col("patient_icn")).n_unique()
    logger.info(f"  - Unique patients: {patient_count}")
    logger.info(f"  - Active entries: {df_gold.filter(pl.col('is_active') == True).height}")
    logger.info(
        "  - First-degree entries: "
        f"{df_gold.filter(pl.col('first_degree_relative_flag') == True).height}"
    )

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    transform_family_history_gold()

