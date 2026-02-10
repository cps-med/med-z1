# ---------------------------------------------------------------------
# load_encounters.py
# ---------------------------------------------------------------------
# Load Gold inpatient encounters data into PostgreSQL serving database
#  - Read Gold: inpatient_final.parquet
#  - Transform to match PostgreSQL schema
#  - Load into patient_encounters table
#  - Use truncate/reload strategy (upsert can be added later)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_encounters
# ---------------------------------------------------------------------

import polars as pl
import logging
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_encounters_to_postgresql():
    """Load Gold inpatient encounters data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("Starting PostgreSQL load for inpatient encounters")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Gold inpatient encounters
    # ==================================================================
    logger.info("Step 1: Loading Gold inpatient encounters...")

    gold_path = build_gold_path("encounters", "encounters_final.parquet")
    df = minio_client.read_parquet(gold_path)
    logger.info(f"  - Loaded {len(df)} encounters from Gold layer")

    # Log data source distribution
    source_dist = df.group_by("data_source").agg(pl.len().alias("count")).sort("data_source")
    logger.info("  - Data source distribution:")
    for row in source_dist.iter_rows(named=True):
        logger.info(f"    {row['data_source']}: {row['count']} encounters")

    # ==================================================================
    # Step 2: Transform to match PostgreSQL schema
    # ==================================================================
    logger.info("Step 2: Transforming to match PostgreSQL schema...")

    # Select and rename columns to match patient_encounters table schema
    # Note: Gold layer now has encounter_id, encounter_datetime, encounter_type, data_source
    df_pg = df.select([
        pl.col("patient_key"),
        pl.col("encounter_id").alias("inpatient_id"),  # Map encounter_id to existing column name
        pl.col("encounter_type"),

        # Admission details
        pl.col("encounter_datetime").alias("admit_datetime"),
        pl.lit(None, dtype=pl.Int32).alias("admit_location_id"),  # Not in new schema
        pl.col("admit_location_name"),
        pl.col("admit_location_type"),
        pl.col("admit_diagnosis_icd10").alias("admit_diagnosis_code"),
        pl.lit(None, dtype=pl.Int32).alias("admitting_provider_id"),  # Not in new schema
        pl.col("provider_name").alias("admitting_provider_name"),

        # Discharge details
        pl.col("discharge_datetime"),
        pl.lit(None, dtype=pl.Int32).alias("discharge_date_id"),  # Not in new schema
        pl.lit(None, dtype=pl.Int32).alias("discharge_location_id"),  # Not in new schema
        pl.col("discharge_location_name"),
        pl.col("discharge_location_type"),
        pl.col("discharge_diagnosis_icd10").alias("discharge_diagnosis_code"),
        pl.col("discharge_diagnosis").alias("discharge_diagnosis_text"),
        pl.col("discharge_disposition"),

        # Metrics
        pl.col("length_of_stay").cast(pl.Int32),
        pl.lit(None, dtype=pl.Int32).alias("total_days"),  # Not in new schema
        pl.col("encounter_status"),
        pl.col("is_active"),
        pl.col("admission_category"),

        # UI flags
        pl.col("is_recent"),
        pl.col("is_extended_stay"),

        # Facility
        pl.col("facility_sta3n").alias("sta3n"),
        pl.col("facility_name"),

        # Data source tracking (NEW!)
        pl.col("data_source"),

        # Metadata - use data_source instead of old source_system
        pl.col("data_source").alias("source_system"),
    ])

    logger.info(f"  - Prepared {len(df_pg)} encounters for PostgreSQL")
    logger.info(f"    - Active admissions: {df_pg.filter(pl.col('is_active') == True).shape[0]}")
    logger.info(f"    - Recent encounters: {df_pg.filter(pl.col('is_recent') == True).shape[0]}")

    # ==================================================================
    # Step 3: Create PostgreSQL connection
    # ==================================================================
    logger.info("Step 3: Connecting to PostgreSQL...")

    # Create SQLAlchemy connection string
    conn_str = (
        f"postgresql://{POSTGRES_CONFIG['user']}:"
        f"{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:"
        f"{POSTGRES_CONFIG['port']}/"
        f"{POSTGRES_CONFIG['database']}"
    )

    engine = create_engine(conn_str)

    # ==================================================================
    # Step 4: Truncate existing data (for now)
    # ==================================================================
    logger.info("Step 4: Truncating existing patient_encounters table...")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE clinical.patient_encounters;"))
        conn.commit()

    logger.info("  - Table truncated")

    # ==================================================================
    # Step 5: Load data into PostgreSQL
    # ==================================================================
    logger.info("Step 5: Loading data into PostgreSQL...")

    # Convert Polars DataFrame to Pandas for SQLAlchemy compatibility
    df_pandas = df_pg.to_pandas()

    # Write to PostgreSQL
    df_pandas.to_sql(
        "patient_encounters",
        engine,
        schema="clinical",
        if_exists="append",
        index=False,
        method="multi",  # Bulk insert for performance
        chunksize=1000
    )

    logger.info(f"  - Loaded {len(df_pandas)} encounters into patient_encounters table")

    # ==================================================================
    # Step 6: Verify data
    # ==================================================================
    logger.info("Step 6: Verifying data...")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_encounters;"))
        count = result.scalar()
        logger.info(f"  - Verified: {count} rows in patient_encounters table")

        # Get active admissions count
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_encounters WHERE is_active = TRUE;"))
        active_count = result.scalar()
        logger.info(f"  - Active admissions: {active_count}")

        # Get recent encounters count
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_encounters WHERE is_recent = TRUE;"))
        recent_count = result.scalar()
        logger.info(f"  - Recent encounters: {recent_count}")

        # Get sample data
        result = conn.execute(text("""
            SELECT patient_key, admit_datetime, discharge_datetime,
                   encounter_status, admission_category, facility_name
            FROM clinical.patient_encounters
            ORDER BY admit_datetime DESC
            LIMIT 5;
        """))
        logger.info("  - Sample records:")
        for row in result:
            logger.info(f"    {row}")

    logger.info("=" * 70)
    logger.info(f"PostgreSQL load complete: {count} encounters loaded")
    logger.info(f"  - Active admissions: {active_count}")
    logger.info(f"  - Recent encounters: {recent_count}")
    logger.info("=" * 70)

    return count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_encounters_to_postgresql()
