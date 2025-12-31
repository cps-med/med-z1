# ---------------------------------------------------------------------
# bronze_cdwwork2_vitals.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Vitals from CDWWork2 database.
#  - Extract 2 tables:
#    1. VitalMill.VitalResult → bronze/cdwwork2/vital_result
#    2. NDimMill.CodeValue → bronze/cdwwork2/code_value
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_cdwwork2_vitals
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK2_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_vital_result():
    """Extract VitalMill.VitalResult to Bronze layer."""
    logger.info("Starting Bronze extraction: VitalMill.VitalResult")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK2_DB_CONFIG['user']}:"
        f"{CDWWORK2_DB_CONFIG['password']}@"
        f"{CDWWORK2_DB_CONFIG['server']}/"
        f"{CDWWORK2_DB_CONFIG['name']}?"
        f"driver={CDWWORK2_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query - VitalMill.VitalResult already denormalized
    query = """
    SELECT
        VitalResultSID,
        EncounterSID,
        PersonSID,
        PatientICN,
        VitalTypeCodeSID,
        VitalTypeName,
        ResultValue,
        NumericValue,
        Systolic,
        Diastolic,
        UnitCodeSID,
        UnitName,
        TakenDateTime,
        EnteredDateTime,
        LocationName,
        Sta3n,
        IsActive
    FROM VitalMill.VitalResult
    WHERE IsActive = 1
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vital results from CDWWork2")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="vital_result",
        filename="vital_result_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} vital results written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_code_value():
    """Extract NDimMill.CodeValue to Bronze layer (for vital types and units)."""
    logger.info("Starting Bronze extraction: NDimMill.CodeValue")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK2_DB_CONFIG['user']}:"
        f"{CDWWORK2_DB_CONFIG['password']}@"
        f"{CDWWORK2_DB_CONFIG['server']}/"
        f"{CDWWORK2_DB_CONFIG['name']}?"
        f"driver={CDWWORK2_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query - get VITAL_TYPE and UNIT code sets only
    query = """
    SELECT
        CodeValueSID,
        CodeSet,
        Code,
        DisplayText,
        Description,
        IsActive
    FROM NDimMill.CodeValue
    WHERE CodeSet IN ('VITAL_TYPE', 'UNIT') AND IsActive = 1
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} code values from CDWWork2")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="code_value",
        filename="code_value_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} code values written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_all_cdwwork2_vitals_bronze():
    """Extract all CDWWork2 vitals tables to Bronze layer."""
    logger.info("=" * 60)
    logger.info("Starting Bronze extraction for CDWWork2 Vitals tables")
    logger.info("=" * 60)

    # Extract both tables
    vital_result_df = extract_vital_result()
    code_value_df = extract_code_value()

    logger.info("=" * 60)
    logger.info("Bronze extraction complete for CDWWork2 Vitals tables")
    logger.info(f"  - Vital Results: {len(vital_result_df)} rows")
    logger.info(f"  - Code Values: {len(code_value_df)} rows")
    logger.info("=" * 60)

    return {
        "vital_result": vital_result_df,
        "code_value": code_value_df
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_all_cdwwork2_vitals_bronze()
