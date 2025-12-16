# ---------------------------------------------------------------------
# bronze_labs.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Laboratory Results from CDWWork database.
#  - Extract 2 tables:
#    1. Dim.LabTest → bronze/cdwwork/lab_test_dim
#    2. Chem.LabChem → bronze/cdwwork/lab_chem (with JOINs)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_labs
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_lab_test_dim():
    """Extract Dim.LabTest to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.LabTest")

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
        LabTestSID,
        LabTestName,
        LabTestCode,
        LoincCode,
        IsPanel,
        PanelName,
        Units,
        RefRangeLow,
        RefRangeHigh,
        RefRangeText,
        VistaPackage,
        CreatedDate,
        IsActive
    FROM Dim.LabTest
    WHERE IsActive = 1
      AND VistaPackage = 'CH'
    ORDER BY PanelName, LabTestName
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} lab test definitions from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="lab_test_dim",
        filename="lab_test_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(f"Bronze layer written to MinIO: {object_key}")
    return len(df)


def extract_lab_chem():
    """Extract Chem.LabChem with JOINs to Bronze layer."""
    logger.info("Starting Bronze extraction: Chem.LabChem")

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

    # Extract query with JOINs to get patient info, test definitions, and location
    query = """
    SELECT
        lc.LabChemSID,
        lc.PatientSID,
        lc.LabTestSID,
        lc.LabOrderSID,
        lc.AccessionNumber,
        lc.Result,
        lc.ResultNumeric,
        lc.ResultUnit,
        lc.AbnormalFlag,
        lc.RefRange,
        lc.CollectionDateTime,
        lc.ResultDateTime,
        lc.VistaPackage,
        lc.LocationSID,
        lc.Sta3n,
        lc.PerformingLabSID,
        lc.OrderingProviderSID,
        lc.SpecimenType,
        -- Patient info
        p.PatientICN,
        p.PatientName,
        -- Test info
        lt.LabTestName,
        lt.LabTestCode,
        lt.LoincCode,
        lt.PanelName,
        lt.Units AS DefaultUnits,
        lt.RefRangeLow AS DefaultRefRangeLow,
        lt.RefRangeHigh AS DefaultRefRangeHigh,
        lt.RefRangeText AS DefaultRefRangeText,
        -- Location info
        loc.LocationName AS CollectionLocation,
        loc.LocationType AS CollectionLocationType
    FROM Chem.LabChem lc
    LEFT JOIN SPatient.SPatient p ON lc.PatientSID = p.PatientSID
    LEFT JOIN Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
    LEFT JOIN Dim.Location loc ON lc.LocationSID = loc.LocationSID
    WHERE lc.VistaPackage = 'CH'
    ORDER BY lc.CollectionDateTime DESC, lc.PatientSID, lc.AccessionNumber
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} lab results from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="lab_chem",
        filename="lab_chem_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(f"Bronze layer written to MinIO: {object_key}")
    return len(df)


def main():
    """Execute Bronze ETL for Laboratory Results."""
    logger.info("=" * 70)
    logger.info("BRONZE ETL: Laboratory Results (Chemistry)")
    logger.info("=" * 70)

    try:
        # Extract Dim.LabTest
        test_count = extract_lab_test_dim()
        logger.info(f"✅ Lab Test Definitions extracted: {test_count}")

        # Extract Chem.LabChem
        result_count = extract_lab_chem()
        logger.info(f"✅ Lab Results extracted: {result_count}")

        logger.info("=" * 70)
        logger.info("BRONZE ETL COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Bronze ETL failed: {e}")
        raise


if __name__ == "__main__":
    main()
