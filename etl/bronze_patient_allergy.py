"""
Bronze ETL: Extract Allergy.PatientAllergy from CDWWork to MinIO

Extracts patient allergy fact data from SQL Server mock CDW and saves to Bronze layer in MinIO.
Output: med-z1/bronze/cdwwork/patient_allergy/patient_allergy_raw.parquet
"""

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_patient_allergy_bronze():
    """Extract Allergy.PatientAllergy to Bronze layer in MinIO."""
    logger.info("Starting Bronze patient allergy extraction")

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
        PatientAllergySID,
        PatientSID,
        AllergenSID,
        AllergySeveritySID,
        LocalAllergenName,
        OriginationDateTime,
        ObservedDateTime,
        OriginatingStaffSID,
        OriginatingSiteSta3n,
        Comment,
        HistoricalOrObserved,
        IsActive,
        VerificationStatus,
        Sta3n,
        CreatedDateTimeUTC,
        UpdatedDateTimeUTC
    FROM Allergy.PatientAllergy
    WHERE IsActive = 1
    ORDER BY PatientSID, OriginationDateTime DESC
    """

    # Read data using Polars
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} patient allergies from CDWWork Allergy.PatientAllergy")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="patient_allergy",
        filename="patient_allergy_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} patient allergies written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Starting Bronze ETL: Allergy.PatientAllergy extraction")
    extract_patient_allergy_bronze()
    logger.info("Bronze ETL: Allergy.PatientAllergy extraction complete")
