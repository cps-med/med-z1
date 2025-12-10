# ---------------------------------------------------------------------
# load_patient_flags.py
# ---------------------------------------------------------------------
# Load PostgreSQL DB with Gold layer patient flags data
#  - Loads patient_flags table (from Gold layer)
#  - Loads patient_flag_history table (from Silver layer)
#  - Uses upserts (INSERT ... ON CONFLICT DO UPDATE) to handle re-runs
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_patient_flags
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from sqlalchemy import create_engine, text
import logging
from config import DATABASE_URL  # PostgreSQL connection string
from lake.minio_client import MinIOClient, build_gold_path, build_silver_path

logger = logging.getLogger(__name__)


def load_patient_flags_to_postgres():
    """
    Load Gold patient flags and Silver history data to PostgreSQL.
    Uses upserts to handle incremental updates.
    """
    logger.info("=" * 70)
    logger.info("Loading Patient Flags to PostgreSQL")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # -------------------------------------------------------------------------
    # 1. Load patient_flags table (from Gold layer)
    # -------------------------------------------------------------------------
    logger.info("Reading Gold patient_flags Parquet...")

    gold_flags_path = build_gold_path(
        "patient_flags",
        "patient_flags.parquet"
    )
    df_flags = minio_client.read_parquet(gold_flags_path)
    logger.info(f"Read {len(df_flags)} flag records from Gold layer")

    # Map Parquet columns to PostgreSQL columns
    df_flags_mapped = df_flags.select([
        pl.col("patient_key"),
        pl.col("assignment_sid").alias("assignment_id"),
        pl.col("flag_name"),
        pl.col("flag_category"),
        pl.col("is_active"),
        pl.col("assignment_status"),
        pl.col("assignment_date"),
        pl.col("inactivation_date"),
        pl.col("owner_site_sta3n").alias("owner_site"),
        pl.col("owner_site_name"),
        pl.col("review_frequency_days"),
        pl.col("next_review_date"),
        pl.col("review_status"),
        pl.col("last_action_date"),
        pl.col("last_action"),
        pl.col("last_action_by"),
        pl.col("last_updated"),
    ])

    # Convert to Pandas for SQLAlchemy
    df_flags_pandas = df_flags_mapped.to_pandas()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load using upsert approach
    logger.info("Loading patient_flags table...")

    # First, create a temporary staging table
    with engine.begin() as conn:
        # Drop and recreate temp table
        conn.execute(text("DROP TABLE IF EXISTS patient_flags_staging"))

        # Create staging table with same structure (except auto-increment column)
        conn.execute(text("""
            CREATE TEMP TABLE patient_flags_staging (
                patient_key             VARCHAR(50) NOT NULL,
                assignment_id           BIGINT NOT NULL,
                flag_name               VARCHAR(100) NOT NULL,
                flag_category           VARCHAR(2) NOT NULL,
                is_active               BOOLEAN NOT NULL,
                assignment_status       VARCHAR(20) NOT NULL,
                assignment_date         TIMESTAMP NOT NULL,
                inactivation_date       TIMESTAMP,
                owner_site              VARCHAR(10),
                owner_site_name         VARCHAR(100),
                review_frequency_days   INTEGER,
                next_review_date        TIMESTAMP,
                review_status           VARCHAR(20),
                last_action_date        TIMESTAMP,
                last_action             VARCHAR(50),
                last_action_by          VARCHAR(100),
                last_updated            TIMESTAMP
            )
        """))

        logger.info(f"Inserting {len(df_flags_pandas)} records into staging table...")

    # Load data into staging table
    df_flags_pandas.to_sql(
        "patient_flags_staging",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    # Perform upsert from staging to main table
    with engine.begin() as conn:
        logger.info("Performing upsert into patient_flags...")

        result = conn.execute(text("""
            INSERT INTO patient_flags (
                patient_key, assignment_id, flag_name, flag_category,
                is_active, assignment_status, assignment_date, inactivation_date,
                owner_site, owner_site_name, review_frequency_days,
                next_review_date, review_status, last_action_date,
                last_action, last_action_by, last_updated
            )
            SELECT
                patient_key, assignment_id, flag_name, flag_category,
                is_active, assignment_status, assignment_date, inactivation_date,
                owner_site, owner_site_name, review_frequency_days,
                next_review_date, review_status, last_action_date,
                last_action, last_action_by, last_updated
            FROM patient_flags_staging
            ON CONFLICT (assignment_id)
            DO UPDATE SET
                patient_key = EXCLUDED.patient_key,
                flag_name = EXCLUDED.flag_name,
                flag_category = EXCLUDED.flag_category,
                is_active = EXCLUDED.is_active,
                assignment_status = EXCLUDED.assignment_status,
                assignment_date = EXCLUDED.assignment_date,
                inactivation_date = EXCLUDED.inactivation_date,
                owner_site = EXCLUDED.owner_site,
                owner_site_name = EXCLUDED.owner_site_name,
                review_frequency_days = EXCLUDED.review_frequency_days,
                next_review_date = EXCLUDED.next_review_date,
                review_status = EXCLUDED.review_status,
                last_action_date = EXCLUDED.last_action_date,
                last_action = EXCLUDED.last_action,
                last_action_by = EXCLUDED.last_action_by,
                last_updated = EXCLUDED.last_updated
        """))

        logger.info(f"Upsert complete")

    # -------------------------------------------------------------------------
    # 2. Load patient_flag_history table (from Silver layer)
    # -------------------------------------------------------------------------
    logger.info("Reading Silver patient_flag_history Parquet...")

    silver_history_path = build_silver_path(
        "patient_record_flag_history",
        "patient_record_flag_history_cleaned.parquet"
    )
    df_history = minio_client.read_parquet(silver_history_path)
    logger.info(f"Read {len(df_history)} history records from Silver layer")

    # Need to join with assignments to get patient_key
    # Read the Silver assignments to get the patient_sid -> assignment_sid mapping
    silver_assignments_path = build_silver_path(
        "patient_record_flag_assignment",
        "patient_record_flag_assignment_cleaned.parquet"
    )
    df_assignments = minio_client.read_parquet(silver_assignments_path)

    # Also need patient demographics for patient_key lookup
    gold_patients_path = build_gold_path(
        "patient_demographics",
        "patient_demographics.parquet"
    )
    df_patients = minio_client.read_parquet(gold_patients_path)

    # Join history with assignments to get patient_sid, then with patients to get patient_key
    # Use INNER joins to only keep history for patients we have demographics for
    df_history_enriched = (
        df_history
        .join(
            df_assignments.select(["assignment_sid", "patient_sid"]),
            on="assignment_sid",
            how="inner"
        )
        .join(
            df_patients.select(["patient_sid", "patient_key"]),
            on="patient_sid",
            how="inner"
        )
    )

    # Map to PostgreSQL columns
    df_history_mapped = df_history_enriched.select([
        pl.col("assignment_sid").alias("assignment_id"),
        pl.col("patient_key"),
        pl.col("history_datetime").alias("history_date"),
        pl.col("action_code"),
        pl.col("action_name"),
        pl.col("entered_by_duz"),
        pl.col("entered_by_name"),
        pl.col("approved_by_duz"),
        pl.col("approved_by_name"),
        pl.col("tiu_document_ien"),
        pl.col("history_comments"),
        pl.col("event_site_sta3n").alias("event_site"),
    ])

    # Convert to Pandas
    df_history_pandas = df_history_mapped.to_pandas()

    # Load using upsert approach (based on assignment_id + history_date as natural key)
    logger.info("Loading patient_flag_history table...")

    # Create staging table
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS patient_flag_history_staging"))

        conn.execute(text("""
            CREATE TEMP TABLE patient_flag_history_staging (
                assignment_id           BIGINT NOT NULL,
                patient_key             VARCHAR(50) NOT NULL,
                history_date            TIMESTAMP NOT NULL,
                action_code             SMALLINT NOT NULL,
                action_name             VARCHAR(50) NOT NULL,
                entered_by_duz          INTEGER NOT NULL,
                entered_by_name         VARCHAR(100),
                approved_by_duz         INTEGER NOT NULL,
                approved_by_name        VARCHAR(100),
                tiu_document_ien        INTEGER,
                history_comments        TEXT,
                event_site              VARCHAR(10)
            )
        """))

        logger.info(f"Inserting {len(df_history_pandas)} history records into staging table...")

    # Load data into staging table
    df_history_pandas.to_sql(
        "patient_flag_history_staging",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    # Perform upsert from staging to main table
    # Note: Using assignment_id + history_date as composite natural key
    with engine.begin() as conn:
        logger.info("Performing upsert into patient_flag_history...")

        # First, create a unique constraint if it doesn't exist
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'patient_flag_history_unique_key'
                ) THEN
                    ALTER TABLE patient_flag_history
                    ADD CONSTRAINT patient_flag_history_unique_key
                    UNIQUE (assignment_id, history_date);
                END IF;
            END $$;
        """))

        result = conn.execute(text("""
            INSERT INTO patient_flag_history (
                assignment_id, patient_key, history_date, action_code, action_name,
                entered_by_duz, entered_by_name, approved_by_duz, approved_by_name,
                tiu_document_ien, history_comments, event_site
            )
            SELECT
                assignment_id, patient_key, history_date, action_code, action_name,
                entered_by_duz, entered_by_name, approved_by_duz, approved_by_name,
                tiu_document_ien, history_comments, event_site
            FROM patient_flag_history_staging
            ON CONFLICT (assignment_id, history_date)
            DO UPDATE SET
                patient_key = EXCLUDED.patient_key,
                action_code = EXCLUDED.action_code,
                action_name = EXCLUDED.action_name,
                entered_by_duz = EXCLUDED.entered_by_duz,
                entered_by_name = EXCLUDED.entered_by_name,
                approved_by_duz = EXCLUDED.approved_by_duz,
                approved_by_name = EXCLUDED.approved_by_name,
                tiu_document_ien = EXCLUDED.tiu_document_ien,
                history_comments = EXCLUDED.history_comments,
                event_site = EXCLUDED.event_site
        """))

        logger.info(f"Upsert complete")

    # -------------------------------------------------------------------------
    # 3. Verify loaded data
    # -------------------------------------------------------------------------
    logger.info("Verifying loaded data...")

    with engine.connect() as conn:
        # Verify patient_flags
        result = conn.execute(text("SELECT COUNT(*) FROM patient_flags")).fetchone()
        flags_count = result[0]
        logger.info(f"  - patient_flags: {flags_count} rows")

        # Verify patient_flag_history
        result = conn.execute(text("SELECT COUNT(*) FROM patient_flag_history")).fetchone()
        history_count = result[0]
        logger.info(f"  - patient_flag_history: {history_count} rows")

        # Show active flags by review status
        result = conn.execute(text("""
            SELECT review_status, COUNT(*) as count
            FROM patient_flags
            WHERE is_active = true
            GROUP BY review_status
            ORDER BY review_status
        """))

        logger.info("Active flags by review status:")
        for row in result:
            logger.info(f"    - {row[0]}: {row[1]}")

    logger.info("=" * 70)
    logger.info("Patient Flags Load Complete")
    logger.info("=" * 70)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_patient_flags_to_postgres()
