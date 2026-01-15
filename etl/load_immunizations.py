# ---------------------------------------------------------------------
# load_immunizations.py
# ---------------------------------------------------------------------
# Load Gold immunizations data into PostgreSQL serving database
#  - Read Gold: patient_immunizations_final.parquet
#  - Transform to match PostgreSQL schema
#  - Load into clinical.patient_immunizations table
#  - Truncate and reload (development pattern)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_immunizations
# ---------------------------------------------------------------------

import polars as pl
import logging
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_immunizations_to_postgresql():
    """Load Gold immunizations data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("PostgreSQL Load: Immunizations")
    logger.info("=" * 70)

    try:
        # Initialize MinIO client
        minio_client = MinIOClient()

        # ==================================================================
        # Step 1: Load Gold immunizations
        # ==================================================================
        logger.info("Step 1: Loading Gold immunizations...")

        gold_path = build_gold_path("immunizations", "patient_immunizations_final.parquet")
        df = minio_client.read_parquet(gold_path)
        logger.info(f"  - Loaded {len(df)} immunizations from Gold layer")

        # ==================================================================
        # Step 2: Transform to match PostgreSQL schema
        # ==================================================================
        logger.info("Step 2: Transforming to match PostgreSQL schema...")

        # Select and rename columns to match patient_immunizations table schema
        # Note: PostgreSQL table has immunization_id (auto) + all these columns
        df_pg = df.select([
            pl.col("immunization_sid"),         # Source system ID (unique)
            pl.col("patient_key"),              # ICN
            pl.col("cvx_code"),                 # CDC CVX code
            pl.col("vaccine_name"),             # Standardized name
            pl.col("vaccine_name_local"),       # Original name
            pl.col("administered_datetime"),    # When administered
            pl.col("series"),                   # Display format
            pl.col("dose_number"),              # Parsed dose
            pl.col("total_doses"),              # Parsed total
            pl.col("is_series_complete"),       # Completion flag
            pl.col("dose"),                     # Dose amount
            pl.col("route"),                    # Administration route
            pl.col("site_of_administration"),   # Anatomical site
            pl.col("adverse_reaction"),         # Reaction description
            pl.col("has_adverse_reaction"),     # Reaction flag
            pl.col("provider_name"),            # Administering provider
            pl.col("location_sid").cast(pl.Int32),  # LocationSID (cast to INTEGER)
            pl.col("location_name"),            # Location name
            pl.col("location_type"),            # Location type
            pl.col("station_name"),             # VA facility name
            pl.col("sta3n").cast(pl.Int16),     # Station number (cast to SMALLINT)
            pl.col("comments"),                 # Clinical notes
            pl.col("is_annual_vaccine"),        # Annual flag
            pl.col("is_covid_vaccine"),         # COVID flag
            pl.col("source_system"),            # CDWWork or CDWWork2
            pl.col("last_updated"),             # Timestamp
        ])

        logger.info(f"  - Prepared {len(df_pg)} immunizations for PostgreSQL")

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
        # Step 4: Truncate existing data (development pattern)
        # ==================================================================
        logger.info("Step 4: Truncating existing patient_immunizations table...")

        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE clinical.patient_immunizations;"))
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
            "patient_immunizations",
            engine,
            schema="clinical",
            if_exists="append",
            index=False,
            method="multi",  # Bulk insert for performance
            chunksize=1000
        )

        logger.info(f"  - Loaded {len(df_pandas)} immunizations into patient_immunizations table")

        # ==================================================================
        # Step 6: Verify data
        # ==================================================================
        logger.info("Step 6: Verifying data...")

        with engine.connect() as conn:
            # Total count
            result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_immunizations;"))
            count = result.scalar()
            logger.info(f"  - Verified: {count} rows in patient_immunizations table")

            # Patient count
            result = conn.execute(text("SELECT COUNT(DISTINCT patient_key) FROM clinical.patient_immunizations;"))
            patient_count = result.scalar()
            logger.info(f"  - Patients: {patient_count}")

            # CVX code distribution
            result = conn.execute(text("""
                SELECT cvx_code, COUNT(*) as count
                FROM clinical.patient_immunizations
                GROUP BY cvx_code
                ORDER BY count DESC
                LIMIT 5;
            """))
            logger.info("  - Top 5 vaccine types (CVX):")
            for row in result:
                logger.info(f"    CVX {row[0]}: {row[1]} administrations")

            # Series completion stats
            result = conn.execute(text("""
                SELECT
                    SUM(CASE WHEN is_series_complete = TRUE THEN 1 ELSE 0 END) as complete,
                    SUM(CASE WHEN is_series_complete = FALSE THEN 1 ELSE 0 END) as incomplete,
                    SUM(CASE WHEN is_series_complete IS NULL THEN 1 ELSE 0 END) as unknown
                FROM clinical.patient_immunizations;
            """))
            row = result.fetchone()
            logger.info(f"  - Series completion:")
            logger.info(f"    Complete: {row[0]}")
            logger.info(f"    Incomplete: {row[1]}")
            logger.info(f"    Unknown: {row[2]}")

            # Vaccine type flags
            result = conn.execute(text("""
                SELECT
                    SUM(CASE WHEN is_annual_vaccine = TRUE THEN 1 ELSE 0 END) as annual,
                    SUM(CASE WHEN is_covid_vaccine = TRUE THEN 1 ELSE 0 END) as covid,
                    SUM(CASE WHEN has_adverse_reaction = TRUE THEN 1 ELSE 0 END) as reactions
                FROM clinical.patient_immunizations;
            """))
            row = result.fetchone()
            logger.info(f"  - Vaccine types:")
            logger.info(f"    Annual (Influenza): {row[0]}")
            logger.info(f"    COVID-19: {row[1]}")
            logger.info(f"    Adverse reactions: {row[2]}")

            # Sample records
            result = conn.execute(text("""
                SELECT patient_key, vaccine_name, administered_datetime, series, source_system
                FROM clinical.patient_immunizations
                ORDER BY administered_datetime DESC
                LIMIT 5;
            """))
            logger.info("  - Sample records (most recent 5):")
            for row in result:
                logger.info(f"    {row[0]}: {row[1][:40]}... on {row[2]} ({row[3]}, {row[4]})")

        logger.info("=" * 70)
        logger.info(f"✓ PostgreSQL load complete: {count} immunizations loaded")
        logger.info("=" * 70)

        return count

    except Exception as e:
        logger.error(f"✗ PostgreSQL load failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    load_immunizations_to_postgresql()
