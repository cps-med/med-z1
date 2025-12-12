# ---------------------------------------------------------------------
# bronze_vitals.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Vitals from CDWWork database.
#  - Extract 4 tables:
#    1. Dim.VitalType → bronze/cdwwork/vital_type_dim
#    2. Vital.VitalSign → bronze/cdwwork/vital_sign
#    3. Dim.VitalQualifier → bronze/cdwwork/vital_qualifier_dim
#    4. Vital.VitalSignQualifier → bronze/cdwwork/vital_sign_qualifier
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_vitals
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_vital_type_dim():
    """Extract Dim.VitalType to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.VitalType")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query
    query = """
    SELECT
        VitalTypeSID,
        VitalTypeIEN,
        VitalType,
        Abbreviation,
        UnitOfMeasure,
        Category,
        IsActive,
        Sta3n
    FROM Dim.VitalType
    WHERE IsActive = 1
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vital types from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="vital_type_dim",
        filename="vital_type_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} vital types written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_vital_sign():
    """Extract Vital.VitalSign to Bronze layer."""
    logger.info("Starting Bronze extraction: Vital.VitalSign")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query
    query = """
    SELECT
        VitalSignSID,
        PatientSID,
        VitalTypeSID,
        VitalSignTakenDateTime,
        VitalSignEnteredDateTime,
        ResultValue,
        NumericValue,
        Systolic,
        Diastolic,
        MetricValue,
        LocationSID,
        EnteredByStaffSID,
        IsInvalid,
        EnteredInError,
        Sta3n,
        CreatedDateTimeUTC,
        UpdatedDateTimeUTC
    FROM Vital.VitalSign
    WHERE IsInvalid = 'N' AND EnteredInError = 'N'
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vital signs from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="vital_sign",
        filename="vital_sign_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} vital signs written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_vital_qualifier_dim():
    """Extract Dim.VitalQualifier to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.VitalQualifier")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query
    query = """
    SELECT
        VitalQualifierSID,
        VitalQualifier,
        QualifierType,
        VitalQualifierIEN,
        Sta3n,
        IsActive
    FROM Dim.VitalQualifier
    WHERE IsActive = 1
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vital qualifiers from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="vital_qualifier_dim",
        filename="vital_qualifier_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} vital qualifiers written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_vital_sign_qualifier():
    """Extract Vital.VitalSignQualifier to Bronze layer."""
    logger.info("Starting Bronze extraction: Vital.VitalSignQualifier")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query
    query = """
    SELECT
        VitalSignQualifierSID,
        VitalSignSID,
        VitalQualifierSID
    FROM Vital.VitalSignQualifier
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vital sign qualifiers from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="vital_sign_qualifier",
        filename="vital_sign_qualifier_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} vital sign qualifiers written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_all_vitals_bronze():
    """Extract all vitals tables to Bronze layer."""
    logger.info("=" * 60)
    logger.info("Starting Bronze extraction for all Vitals tables")
    logger.info("=" * 60)

    # Extract all 4 tables
    vital_type_df = extract_vital_type_dim()
    vital_sign_df = extract_vital_sign()
    vital_qualifier_df = extract_vital_qualifier_dim()
    vital_sign_qualifier_df = extract_vital_sign_qualifier()

    logger.info("=" * 60)
    logger.info("Bronze extraction complete for all Vitals tables")
    logger.info(f"  - Vital Types: {len(vital_type_df)} rows")
    logger.info(f"  - Vital Signs: {len(vital_sign_df)} rows")
    logger.info(f"  - Vital Qualifiers: {len(vital_qualifier_df)} rows")
    logger.info(f"  - Vital Sign Qualifiers: {len(vital_sign_qualifier_df)} rows")
    logger.info("=" * 60)

    return {
        "vital_type": vital_type_df,
        "vital_sign": vital_sign_df,
        "vital_qualifier": vital_qualifier_df,
        "vital_sign_qualifier": vital_sign_qualifier_df
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_all_vitals_bronze()
