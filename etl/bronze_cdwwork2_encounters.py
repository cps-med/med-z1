#!/usr/bin/env python3
"""
Bronze extraction: CDWWork2 Encounters (EncMill.Encounter)

Extracts all encounter types from Cerner/Oracle Health CDWWork2 database.
Expected to extract 12 Thompson patient encounters from Walla Walla VAMC (Sta3n 687):
- Bailey Thompson (ICN200001): 7 encounters
- Alananah Thompson (ICN200002): 3 encounters
- Joe Thompson (ICN200003): 2 encounters

To run:
    python -m etl.bronze_cdwwork2_encounters
"""

import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine
import polars as pl

from config import CDWWORK2_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_encounters():
    """Extract EncMill.Encounter to Bronze layer."""

    logger.info("=" * 70)
    logger.info("Extracting CDWWork2 Encounters (EncMill.Encounter)...")
    logger.info("=" * 70)

    # Build connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK2_DB_CONFIG['user']}:"
        f"{CDWWORK2_DB_CONFIG['password']}@"
        f"{CDWWORK2_DB_CONFIG['server']}/"
        f"{CDWWORK2_DB_CONFIG['name']}?"
        f"driver={CDWWORK2_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query - EncMill.Encounter fields
    query = """
    SELECT
        EncounterSID,
        PersonSID,
        PatientICN,
        Sta3n,
        FacilityName,
        EncounterType,
        EncounterDate,
        AdmitDate,
        DischargeDate,
        LocationName,
        LocationType,
        ProviderName,
        ProviderSID,
        IsActive,
        CreatedDate
    FROM EncMill.Encounter
    WHERE IsActive = 1
    ORDER BY EncounterDate DESC
    """

    logger.info("Executing query...")

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"  - Extracted {len(df)} encounters")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Log encounter distribution
    if len(df) > 0:
        encounter_dist = df.group_by("PatientICN").agg(
            pl.len().alias("EncounterCount")
        ).sort("PatientICN")

        logger.info("  - Encounter distribution by patient:")
        for row in encounter_dist.iter_rows(named=True):
            logger.info(f"    {row['PatientICN']}: {row['EncounterCount']} encounters")

    # Build Bronze path
    minio_client = MinIOClient()
    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="encounters",
        filename="encounters_raw.parquet"
    )

    logger.info(f"Writing to MinIO: {object_key}")
    minio_client.write_parquet(df, object_key)

    logger.info("=" * 70)
    logger.info(f"Bronze extraction complete: {len(df)} encounters")
    logger.info(f"  - Written to: s3://{minio_client.bucket_name}/{object_key}")
    logger.info("=" * 70)

    engine.dispose()
    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_encounters()
