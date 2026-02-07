# ---------------------------------------------------------------------
# etl/load_military_history.py
# ---------------------------------------------------------------------
# Load PostgreSQL DB with Gold layer patient military history data
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a module:
#  $ cd med-z1
#  $ python -m etl.load_military_history
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from sqlalchemy import create_engine, text
import logging
from config import DATABASE_URL  # PostgreSQL connection string
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_military_history_to_postgres():
    """Load Gold patient military history from MinIO to PostgreSQL."""

    logger.info("Loading patient military history to PostgreSQL...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Gold Parquet from MinIO
    gold_path = build_gold_path(
        "patient_military_history",
        "military_history.parquet"
    )
    df = minio_client.read_parquet(gold_path)

    logger.info(f"Read {len(df)} military history records from Gold layer")

    # Convert Polars to Pandas (for SQLAlchemy compatibility)
    df_pandas = df.to_pandas()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load to PostgreSQL (truncate and reload)
    df_pandas.to_sql(
        "patient_military_history",
        engine,
        schema="clinical",
        if_exists="replace",
        index=False,
        method="multi",
    )

    logger.info(f"Loaded {len(df)} military history records to PostgreSQL")

    # Verify
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_military_history")).fetchone()
        logger.info(f"Verification: {result[0]} rows in patient_military_history table")

        # Summary stats
        result = conn.execute(text("""
            SELECT
                COUNT(*) as total_records,
                SUM(CASE WHEN service_connected_flag = 'Y' THEN 1 ELSE 0 END) as service_connected_count,
                SUM(CASE WHEN agent_orange_exposure = 'Y' THEN 1 ELSE 0 END) as agent_orange_count,
                SUM(CASE WHEN pow_status = 'Y' THEN 1 ELSE 0 END) as pow_count,
                SUM(CASE WHEN sw_asia_exposure = 'Y' THEN 1 ELSE 0 END) as gulf_war_count,
                SUM(CASE WHEN camp_lejeune_flag = 'Y' THEN 1 ELSE 0 END) as camp_lejeune_count
            FROM clinical.patient_military_history
        """)).fetchone()
        logger.info(f"Summary: {result[1]} service connected, {result[2]} Agent Orange, "
                   f"{result[3]} POW, {result[4]} Gulf War, {result[5]} Camp Lejeune")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_military_history_to_postgres()
