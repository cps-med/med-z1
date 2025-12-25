# ---------------------------------------------------------------------
# load_labs.py
# ---------------------------------------------------------------------
# Load Gold labs data into PostgreSQL serving database
#  - Read Gold: labs_final.parquet
#  - Transform to match PostgreSQL schema
#  - Load into patient_labs table
#  - Use truncate/load for now (upsert in future phases)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_labs
# ---------------------------------------------------------------------

import polars as pl
import logging
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_labs_to_postgresql():
    """Load Gold labs data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("Starting PostgreSQL load for laboratory results")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Gold labs
    # ==================================================================
    logger.info("Step 1: Loading Gold labs...")

    gold_path = build_gold_path("labs", "labs_final.parquet")
    df = minio_client.read_parquet(gold_path)
    logger.info(f"  - Loaded {len(df)} lab results from Gold layer")

    # ==================================================================
    # Step 2: Transform to match PostgreSQL schema
    # ==================================================================
    logger.info("Step 2: Transforming to match PostgreSQL schema...")

    # Select and rename columns to match patient_labs table schema
    # Note: patient_labs table has these columns:
    #   lab_id (auto), patient_key, lab_chem_sid, lab_test_sid, lab_test_name,
    #   lab_test_code, loinc_code, panel_name, accession_number,
    #   result_value, result_numeric, result_unit, abnormal_flag, is_abnormal, is_critical,
    #   ref_range_text, ref_range_low, ref_range_high,
    #   collection_datetime, result_datetime,
    #   location_id, collection_location, collection_location_type,
    #   specimen_type, sta3n, performing_lab_sid, ordering_provider_sid,
    #   vista_package, last_updated
    df_pg = df.select([
        pl.col("lab_chem_sid"),
        pl.col("patient_key"),
        pl.col("lab_test_sid"),
        pl.col("lab_test_name"),
        pl.col("lab_test_code"),
        pl.col("loinc_code"),
        pl.col("panel_name"),
        pl.col("accession_number"),
        pl.col("result_value"),
        pl.col("result_numeric"),
        pl.col("result_unit"),
        pl.col("abnormal_flag"),
        pl.col("is_abnormal"),
        pl.col("is_critical"),
        pl.col("ref_range_text"),
        pl.col("ref_range_low"),
        pl.col("ref_range_high"),
        pl.col("collection_datetime"),
        pl.col("result_datetime"),
        pl.col("location_id").cast(pl.Int32),
        pl.col("collection_location"),
        pl.col("collection_location_type"),
        pl.col("specimen_type"),
        pl.col("sta3n"),
        pl.col("performing_lab_sid").cast(pl.Int32),
        pl.col("ordering_provider_sid").cast(pl.Int32),
        pl.col("vista_package"),
    ])

    logger.info(f"  - Prepared {len(df_pg)} lab results for PostgreSQL")

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
    logger.info("Step 4: Truncating existing patient_labs table...")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE clinical.patient_labs;"))
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
        "patient_labs",
        engine,
        schema="clinical",
        if_exists="append",
        index=False,
        method="multi",  # Bulk insert for performance
        chunksize=1000
    )

    logger.info(f"  - Loaded {len(df_pandas)} lab results into patient_labs table")

    # ==================================================================
    # Step 6: Verify data
    # ==================================================================
    logger.info("Step 6: Verifying data...")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_labs;"))
        count = result.scalar()
        logger.info(f"  - Verified: {count} rows in patient_labs table")

        # Get sample data
        result = conn.execute(text("""
            SELECT patient_key, lab_test_name, result_value, abnormal_flag,
                   collection_location, collection_datetime
            FROM clinical.patient_labs
            LIMIT 5;
        """))
        logger.info("  - Sample records:")
        for row in result:
            logger.info(f"    {row}")

        # Count by location
        result = conn.execute(text("""
            SELECT collection_location, COUNT(*) as count
            FROM clinical.patient_labs
            GROUP BY collection_location
            ORDER BY count DESC;
        """))
        logger.info("  - Results by collection location:")
        for row in result:
            logger.info(f"    {row[0]}: {row[1]} results")

    logger.info("=" * 70)
    logger.info(f"PostgreSQL load complete: {count} lab results loaded")
    logger.info("=" * 70)

    return count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_labs_to_postgresql()
