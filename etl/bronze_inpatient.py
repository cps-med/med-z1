# ---------------------------------------------------------------------
# bronze_inpatient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Inpatient Encounters from CDWWork database.
#  - Extract 1 table:
#    1. Inpat.Inpatient → bronze/cdwwork/inpatient
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_inpatient
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_inpatient():
    """Extract Inpat.Inpatient to Bronze layer."""
    logger.info("Starting Bronze extraction: Inpat.Inpatient")

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

    # Extract query - get all inpatient encounters
    query = """
    SELECT
        InpatientSID,
        PatientSID,
        AdmitDateTime,
        AdmitLocationSID,
        AdmittingProviderSID,
        AdmitDiagnosisICD10,
        DischargeDateTime,
        DischargeDateSID,
        DischargeWardLocationSID,
        DischargeDiagnosisICD10,
        DischargeDiagnosis,
        DischargeDisposition,
        LengthOfStay,
        EncounterStatus,
        Sta3n
    FROM Inpat.Inpatient
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} inpatient encounters from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="inpatient",
        filename="inpatient_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} inpatient encounters written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_all_inpatient_bronze():
    """Extract all inpatient tables to Bronze layer."""
    logger.info("=" * 60)
    logger.info("Starting Bronze extraction for Inpatient Encounters")
    logger.info("=" * 60)

    # Extract inpatient encounters
    inpatient_df = extract_inpatient()

    logger.info("=" * 60)
    logger.info("Bronze extraction complete for Inpatient Encounters")
    logger.info(f"  - Inpatient Encounters: {len(inpatient_df)} rows")
    logger.info("=" * 60)

    return {
        "inpatient": inpatient_df
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_all_inpatient_bronze()
