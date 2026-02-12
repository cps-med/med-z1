# ---------------------------------------------------------------------
# load_ddi.py
# ---------------------------------------------------------------------
# Load Gold DDI reference data into PostgreSQL serving database
#  - Read Gold: ddi_reference.parquet
#  - Transform to match PostgreSQL schema
#  - Load into reference.ddi table
#  - Truncate and reload (development pattern)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_ddi
# ---------------------------------------------------------------------

import logging

import polars as pl
from sqlalchemy import create_engine, text

from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_ddi_to_postgresql():
    """Load Gold DDI reference data into PostgreSQL reference.ddi table."""
    logger.info("=" * 70)
    logger.info("PostgreSQL Load: DDI Reference")
    logger.info("=" * 70)

    try:
        minio_client = MinIOClient()

        # ------------------------------------------------------------------
        # Step 1: Load Gold DDI Parquet
        # ------------------------------------------------------------------
        logger.info("Step 1: Loading Gold DDI reference...")

        gold_path = build_gold_path("ddi", "ddi_reference.parquet")
        df = minio_client.read_parquet(gold_path)
        logger.info(f"  - Loaded {len(df)} DDI rows from Gold layer")

        # ------------------------------------------------------------------
        # Step 2: Transform and validate for PostgreSQL schema
        # ------------------------------------------------------------------
        logger.info("Step 2: Transforming to match PostgreSQL schema...")

        required_cols = {"drug_1", "drug_2", "interaction_description"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Gold DDI data missing required columns: {sorted(missing)}")

        df_pg = (
            df.select([
                pl.col("drug_1").cast(pl.Utf8),
                pl.col("drug_2").cast(pl.Utf8),
                pl.col("interaction_description").cast(pl.Utf8),
            ])
            .drop_nulls()
            .unique(subset=["drug_1", "drug_2"])
            .sort(["drug_1", "drug_2"])
        )

        logger.info(f"  - Prepared {len(df_pg)} unique DDI pairs for PostgreSQL")

        # ------------------------------------------------------------------
        # Step 3: Connect to PostgreSQL
        # ------------------------------------------------------------------
        logger.info("Step 3: Connecting to PostgreSQL...")

        conn_str = (
            f"postgresql://{POSTGRES_CONFIG['user']}:"
            f"{POSTGRES_CONFIG['password']}@"
            f"{POSTGRES_CONFIG['host']}:"
            f"{POSTGRES_CONFIG['port']}/"
            f"{POSTGRES_CONFIG['database']}"
        )
        engine = create_engine(conn_str)

        # ------------------------------------------------------------------
        # Step 4: Truncate existing data (development pattern)
        # ------------------------------------------------------------------
        logger.info("Step 4: Truncating reference.ddi...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE reference.ddi RESTART IDENTITY;"))
            conn.commit()
        logger.info("  - Table truncated")

        # ------------------------------------------------------------------
        # Step 5: Load to PostgreSQL
        # ------------------------------------------------------------------
        logger.info("Step 5: Loading DDI data into PostgreSQL...")
        df_pandas = df_pg.to_pandas()
        df_pandas.to_sql(
            "ddi",
            engine,
            schema="reference",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
        logger.info(f"  - Loaded {len(df_pandas)} rows into reference.ddi")

        # ------------------------------------------------------------------
        # Step 6: Verify
        # ------------------------------------------------------------------
        logger.info("Step 6: Verifying loaded data...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM reference.ddi;"))
            count = result.scalar()
            logger.info(f"  - Verified: {count} rows in reference.ddi")

            result = conn.execute(text("""
                SELECT drug_1, drug_2
                FROM reference.ddi
                ORDER BY ddi_id
                LIMIT 5;
            """))
            logger.info("  - Sample pairs:")
            for row in result:
                logger.info(f"    {row[0]} + {row[1]}")

        logger.info("=" * 70)
        logger.info(f"✓ PostgreSQL load complete: {count} DDI rows loaded")
        logger.info("=" * 70)

        return count

    except Exception as e:
        logger.error(f"✗ PostgreSQL DDI load failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    load_ddi_to_postgresql()
