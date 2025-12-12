"""
Bronze ETL: Extract Dim.AllergySeverity from CDWWork to MinIO

Extracts allergy severity dimension data from SQL Server mock CDW and saves to Bronze layer in MinIO.
Output: med-z1/bronze/cdwwork/allergy_severity/allergy_severity_raw.parquet
"""

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_allergy_severity_bronze():
    """Extract Dim.AllergySeverity to Bronze layer in MinIO."""
    logger.info("Starting Bronze allergy severity extraction")

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
        AllergySeveritySID,
        SeverityName,
        SeverityRank,
        IsActive
    FROM Dim.AllergySeverity
    WHERE IsActive = 1
    ORDER BY SeverityRank
    """

    # Read data using Polars
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} severity levels from CDWWork Dim.AllergySeverity")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="allergy_severity",
        filename="allergy_severity_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} severity levels written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Starting Bronze ETL: Dim.AllergySeverity extraction")
    extract_allergy_severity_bronze()
    logger.info("Bronze ETL: Dim.AllergySeverity extraction complete")
