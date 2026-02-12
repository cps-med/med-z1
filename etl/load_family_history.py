# ---------------------------------------------------------------------
# load_family_history.py
# ---------------------------------------------------------------------
# Load Gold family history data into PostgreSQL serving database
#  - Read Gold: patient_family_history/patient_family_history_final.parquet
#  - Transform to match clinical.patient_family_history schema
#  - Load into clinical.patient_family_history table
#  - Truncate and reload (development pattern)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_family_history
# ---------------------------------------------------------------------

import logging

import polars as pl
from sqlalchemy import create_engine, text

from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_family_history_to_postgresql():
    """Load Gold family history data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("PostgreSQL Load: Family History")
    logger.info("=" * 70)

    try:
        # ==================================================================
        # Step 1: Load Gold family history
        # ==================================================================
        logger.info("Step 1: Loading Gold family history...")

        minio_client = MinIOClient()
        gold_path = build_gold_path("patient_family_history", "patient_family_history_final.parquet")
        df = minio_client.read_parquet(gold_path)
        logger.info(f"  - Loaded {len(df)} family-history records from Gold layer")

        # ==================================================================
        # Step 2: Transform to match PostgreSQL schema
        # ==================================================================
        logger.info("Step 2: Transforming to match PostgreSQL schema...")

        df_pg = df.select([
            pl.col("patient_icn"),
            pl.col("patient_icn").alias("patient_key"),
            pl.col("source_system"),
            pl.col("source_ehr"),
            pl.col("record_id").alias("source_record_id"),
            pl.col("relationship_code"),
            pl.col("relationship_name"),
            pl.col("relationship_degree"),
            pl.col("condition_code"),
            pl.col("condition_name"),
            pl.col("snomed_code"),
            pl.col("icd10_code"),
            pl.col("condition_category"),
            pl.col("risk_condition_group"),
            pl.col("hereditary_risk_flag").cast(pl.Boolean),
            pl.col("first_degree_relative_flag").cast(pl.Boolean),
            pl.col("clinical_status"),
            pl.col("is_active").cast(pl.Boolean),
            pl.col("family_member_gender"),
            pl.col("family_member_age").cast(pl.Int32),
            pl.col("family_member_deceased").cast(pl.Boolean),
            pl.col("onset_age_years").cast(pl.Int32),
            pl.col("recorded_datetime"),
            pl.col("entered_datetime"),
            pl.col("encounter_sid").cast(pl.Int64),
            pl.col("facility_id"),
            pl.col("provider_id").cast(pl.Int64),
            pl.col("provider_name"),
            pl.col("location_id").cast(pl.Int64),
            pl.col("comment_text"),
            pl.col("family_history_count_total").cast(pl.Int32),
            pl.col("family_history_count_active").cast(pl.Int32),
            pl.col("family_history_first_degree_count").cast(pl.Int32),
            pl.col("family_history_first_degree_high_risk_count").cast(pl.Int32),
            pl.col("silver_load_datetime"),
            pl.col("gold_load_datetime"),
            pl.col("silver_schema_version"),
            pl.col("gold_schema_version"),
        ])

        logger.info(f"  - Prepared {len(df_pg)} family-history records for PostgreSQL")

        # ==================================================================
        # Step 3: Connect to PostgreSQL
        # ==================================================================
        logger.info("Step 3: Connecting to PostgreSQL...")

        conn_str = (
            f"postgresql://{POSTGRES_CONFIG['user']}:"
            f"{POSTGRES_CONFIG['password']}@"
            f"{POSTGRES_CONFIG['host']}:"
            f"{POSTGRES_CONFIG['port']}/"
            f"{POSTGRES_CONFIG['database']}"
        )
        engine = create_engine(conn_str)

        # ==================================================================
        # Step 4: Truncate existing data
        # ==================================================================
        logger.info("Step 4: Truncating existing patient_family_history table...")

        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE clinical.patient_family_history RESTART IDENTITY;"))
            conn.commit()

        logger.info("  - Table truncated")

        # ==================================================================
        # Step 5: Load data into PostgreSQL
        # ==================================================================
        logger.info("Step 5: Loading data into PostgreSQL...")

        df_pandas = df_pg.to_pandas()
        df_pandas.to_sql(
            "patient_family_history",
            engine,
            schema="clinical",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

        logger.info(f"  - Loaded {len(df_pandas)} family-history records into patient_family_history table")

        # ==================================================================
        # Step 6: Verify data
        # ==================================================================
        logger.info("Step 6: Verifying data...")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_family_history;"))
            count = result.scalar()
            logger.info(f"  - Verified: {count} rows in patient_family_history table")

            result = conn.execute(text("SELECT COUNT(DISTINCT patient_icn) FROM clinical.patient_family_history;"))
            patient_count = result.scalar()
            logger.info(f"  - Patients: {patient_count}")

            result = conn.execute(text("""
                SELECT source_system, COUNT(*) as count
                FROM clinical.patient_family_history
                GROUP BY source_system
                ORDER BY count DESC;
            """))
            logger.info("  - Records by source:")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]}")

            result = conn.execute(text("""
                SELECT
                    SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_count,
                    SUM(CASE WHEN first_degree_relative_flag = TRUE THEN 1 ELSE 0 END) as first_degree_count,
                    SUM(CASE WHEN first_degree_relative_flag = TRUE AND COALESCE(hereditary_risk_flag, FALSE) = TRUE
                        THEN 1 ELSE 0 END) as high_risk_count
                FROM clinical.patient_family_history;
            """))
            row = result.fetchone()
            logger.info(f"  - Active findings: {row[0] or 0}")
            logger.info(f"  - First-degree findings: {row[1] or 0}")
            logger.info(f"  - First-degree high-risk findings: {row[2] or 0}")

            result = conn.execute(text("""
                SELECT patient_icn, relationship_name, condition_name, recorded_datetime, source_system
                FROM clinical.patient_family_history
                ORDER BY recorded_datetime DESC NULLS LAST
                LIMIT 5;
            """))
            logger.info("  - Sample records (most recent 5):")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]} - {row[2]} ({row[3]}, {row[4]})")

        logger.info("=" * 70)
        logger.info(f"PostgreSQL load complete: {count} family-history records loaded")
        logger.info("=" * 70)

        return count

    except Exception as exc:
        logger.error(f"PostgreSQL load failed: {exc}", exc_info=True)
        raise


if __name__ == "__main__":
    load_family_history_to_postgresql()
