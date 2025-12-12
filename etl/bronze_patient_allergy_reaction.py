"""
Bronze ETL: Extract Allergy.PatientAllergyReaction from CDWWork to MinIO

Extracts patient allergy reaction bridge data from SQL Server mock CDW and saves to Bronze layer in MinIO.
Output: med-z1/bronze/cdwwork/patient_allergy_reaction/patient_allergy_reaction_raw.parquet
"""

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_patient_allergy_reaction_bronze():
    """Extract Allergy.PatientAllergyReaction to Bronze layer in MinIO."""
    logger.info("Starting Bronze patient allergy reaction extraction")

    # Initialize MinIO client
    minio_client = MinIOClient()
    logger.info("MinIO client created")

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    logger.info("Created DB connection string")

    # Create SQLAlchemy engine
    engine = create_engine(conn_str)

    # Extract query
    query = """
    SELECT
        PatientAllergyReactionSID,
        PatientAllergySID,
        ReactionSID
    FROM Allergy.PatientAllergyReaction
    ORDER BY PatientAllergySID, ReactionSID
    """

    # Read data using Polars
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} patient allergy reactions from CDWWork Allergy.PatientAllergyReaction")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="patient_allergy_reaction",
        filename="patient_allergy_reaction_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} patient allergy reactions written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Starting Bronze ETL: Allergy.PatientAllergyReaction extraction")
    extract_patient_allergy_reaction_bronze()
    logger.info("Bronze ETL: Allergy.PatientAllergyReaction extraction complete")
