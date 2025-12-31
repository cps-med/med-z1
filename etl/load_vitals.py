# ---------------------------------------------------------------------
# load_vitals.py
# ---------------------------------------------------------------------
# Load Gold vitals data into PostgreSQL serving database
#  - Read Gold: vitals_final.parquet
#  - Transform to match PostgreSQL schema
#  - Load into patient_vitals table
#  - Use upsert (ON CONFLICT) to handle re-runs
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_vitals
# ---------------------------------------------------------------------

import polars as pl
import logging
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_vitals_to_postgresql():
    """Load Gold vitals data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("Starting PostgreSQL load for vitals")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Gold vitals
    # ==================================================================
    logger.info("Step 1: Loading Gold vitals...")

    gold_path = build_gold_path("vitals", "vitals_final.parquet")
    df = minio_client.read_parquet(gold_path)
    logger.info(f"  - Loaded {len(df)} vitals from Gold layer")

    # ==================================================================
    # Step 2: Transform to match PostgreSQL schema
    # ==================================================================
    logger.info("Step 2: Transforming to match PostgreSQL schema...")

    # Handle overlapping vital_record_id values from dual sources (CDWWork + CDWWork2)
    # CDWWork2 IDs need offset to avoid collision with CDWWork IDs
    # Strategy: Add 10,000,000 to CDWWork2 vital_record_ids
    logger.info(f"  - Offsetting CDWWork2 vital_record_ids to avoid collisions...")

    df = df.with_columns([
        pl.when(pl.col("data_source") == "CDWWork2")
            .then(pl.col("vital_record_id") + 10000000)  # Offset CDWWork2 IDs
            .otherwise(pl.col("vital_record_id"))
            .alias("vital_record_id")
    ])

    # For calculated BMI records that have NULL vital_record_id, generate synthetic IDs
    # starting from a high number (20000000+) to avoid conflicts with real IDs
    max_real_vital_record_id = df.filter(pl.col("vital_record_id").is_not_null()).select(pl.col("vital_record_id").max())[0, 0]
    logger.info(f"  - Max real vital_record_id after offsetting: {max_real_vital_record_id}")

    # Generate synthetic IDs for BMI records
    df = df.with_columns([
        pl.when(pl.col("vital_record_id").is_null())
            .then(20000000 + pl.int_range(pl.len()).over("vital_record_id"))  # Start at 20M
            .otherwise(pl.col("vital_record_id"))
            .alias("vital_record_id")
    ])

    # Select and rename columns to match patient_vitals table schema
    # Note: patient_vitals table has these columns:
    #   vital_id (auto), patient_key, vital_sign_id, vital_type, vital_abbr,
    #   taken_datetime, entered_datetime, result_value, numeric_value,
    #   systolic, diastolic, metric_value, unit_of_measure, qualifiers,
    #   location_id, location_name, location_type, entered_by, abnormal_flag, bmi, data_source, last_updated
    df_pg = df.select([
        pl.col("vital_record_id").alias("vital_sign_id"),  # Renamed from vital_sign_id to vital_record_id in Gold
        pl.col("patient_key"),
        pl.col("vital_type"),
        pl.col("vital_abbr"),
        pl.col("taken_datetime"),
        pl.col("entered_datetime"),
        pl.col("result_value"),
        pl.col("numeric_value"),
        pl.col("systolic").cast(pl.Int32),  # PostgreSQL expects INTEGER
        pl.col("diastolic").cast(pl.Int32),  # PostgreSQL expects INTEGER
        pl.col("metric_value"),
        pl.col("unit_of_measure"),
        pl.col("qualifiers"),  # Already JSON string, will be cast to JSONB
        pl.col("location_id").cast(pl.Int32),
        pl.col("location_name"),
        pl.col("location_type"),
        pl.col("entered_by"),  # Staff name from Gold layer
        pl.col("abnormal_flag"),
        pl.lit(None).cast(pl.Float64).alias("bmi"),  # BMI is in vitals as separate rows, not a column
        pl.col("data_source"),  # Track origin: CDWWork, CDWWork2, or CALCULATED
    ])

    logger.info(f"  - Prepared {len(df_pg)} vitals for PostgreSQL (including {df.filter(pl.col('vital_abbr') == 'BMI').shape[0]} BMI records)")

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
    logger.info("Step 4: Truncating existing patient_vitals table...")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE clinical.patient_vitals;"))
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
        "patient_vitals",
        engine,
        schema="clinical",
        if_exists="append",
        index=False,
        method="multi",  # Bulk insert for performance
        chunksize=1000
    )

    logger.info(f"  - Loaded {len(df_pandas)} vitals into patient_vitals table")

    # ==================================================================
    # Step 6: Verify data
    # ==================================================================
    logger.info("Step 6: Verifying data...")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_vitals;"))
        count = result.scalar()
        logger.info(f"  - Verified: {count} rows in patient_vitals table")

        # Get sample data
        result = conn.execute(text("""
            SELECT patient_key, vital_type, result_value, abnormal_flag, taken_datetime
            FROM clinical.patient_vitals
            LIMIT 5;
        """))
        logger.info("  - Sample records:")
        for row in result:
            logger.info(f"    {row}")

    logger.info("=" * 70)
    logger.info(f"PostgreSQL load complete: {count} vitals loaded")
    logger.info("=" * 70)

    return count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_vitals_to_postgresql()
