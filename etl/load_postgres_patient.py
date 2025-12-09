# ---------------------------------------------------------------------
# load_postgres_patient.py
# ---------------------------------------------------------------------
# Load PostgreSQL DB with Gold layer patient demographics data
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a
# module (for now... there are other options to consider later).
#  $ cd med-z1
#  $ python -m etl.load_postgres_patient
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from sqlalchemy import create_engine, text
import logging
from config import DATABASE_URL  # PostgreSQL connection string
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_patient_demographics_to_postgres():
    """Load Gold patient demographics from MinIO to PostgreSQL."""

    logger.info("Loading patient demographics to PostgreSQL...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Gold Parquet from MinIO
    gold_path = build_gold_path(
        "patient_demographics",
        "patient_demographics.parquet"
    )
    df = minio_client.read_parquet(gold_path)

    logger.info(f"Read {len(df)} patient records from Gold layer")

    # Convert Polars to Pandas (for SQLAlchemy compatibility)
    df_pandas = df.to_pandas()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load to PostgreSQL (truncate and reload)
    df_pandas.to_sql(
        "patient_demographics",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
    )

    logger.info(f"Loaded {len(df)} patients to PostgreSQL")

    # Verify
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM patient_demographics")).fetchone()
        logger.info(f"Verification: {result[0]} rows in patient_demographics table")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_patient_demographics_to_postgres()