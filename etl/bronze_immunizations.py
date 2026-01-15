# ---------------------------------------------------------------------
# bronze_immunizations.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Immunizations from CDWWork database (VistA).
#  - Extract 2 tables:
#    1. Dim.Vaccine → bronze/cdwwork/vaccine_dim
#    2. Immunization.PatientImmunization → bronze/cdwwork/immunization
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_immunizations
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_dim_vaccine():
    """Extract Dim.Vaccine to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.Vaccine")

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

    # Extract query - get all vaccines (including inactive for historical context)
    query = """
    SELECT
        VaccineSID,
        VaccineName,
        VaccineShortName,
        CVXCode,
        MVXCode,
        VistaIEN,
        IsInactive,
        CreatedDateTimeUTC
    FROM Dim.Vaccine
    ORDER BY VaccineSID
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vaccines from CDWWork.Dim.Vaccine")

    # Add metadata columns (Bronze layer standard)
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path (suffix pattern: vaccine_dim)
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="vaccine_dim",
        filename="vaccine_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(f"✓ Bronze extraction complete: {object_key}")
    logger.info(f"  Records: {len(df)}")
    logger.info(f"  Columns: {df.columns}")

    return df


def extract_patient_immunization():
    """Extract Immunization.PatientImmunization to Bronze layer."""
    logger.info("Starting Bronze extraction: Immunization.PatientImmunization")

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

    # Extract query - join with patient to get ICN and vaccine for CVX code
    # This denormalization helps with Silver layer processing
    query = """
    SELECT
        pi.PatientImmunizationSID,
        pi.PatientSID,
        p.PatientICN,
        pi.VaccineSID,
        v.CVXCode,
        v.VaccineName,
        v.VaccineShortName,
        pi.VisitSID,
        pi.AdministeredDateTime,
        pi.Series,
        pi.Dose,
        pi.Route,
        pi.SiteOfAdministration,
        pi.Reaction,
        pi.OrderingProviderSID,
        pi.AdministeringProviderSID,
        pi.LocationSID,
        pi.Sta3n,
        pi.LotNumber,
        pi.Comments,
        pi.IsActive,
        pi.CreatedDateTimeUTC,
        pi.ModifiedDateTimeUTC
    FROM Immunization.PatientImmunization pi
    JOIN SPatient.SPatient p ON pi.PatientSID = p.PatientSID
    JOIN Dim.Vaccine v ON pi.VaccineSID = v.VaccineSID
    WHERE pi.IsActive = 1
    ORDER BY pi.PatientSID, pi.AdministeredDateTime DESC
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} immunization records from CDWWork.Immunization.PatientImmunization")

    # Add metadata columns (Bronze layer standard)
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="immunization",
        filename="patient_immunization_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(f"✓ Bronze extraction complete: {object_key}")
    logger.info(f"  Records: {len(df)}")
    logger.info(f"  Columns: {df.columns}")
    logger.info(f"  Date range: {df.select('AdministeredDateTime').min().item()} to {df.select('AdministeredDateTime').max().item()}")

    # Show sample patient counts
    patient_counts = df.group_by("PatientICN").agg(
        pl.count().alias("ImmunizationCount")
    ).sort("ImmunizationCount", descending=True)

    logger.info(f"  Patient distribution:")
    for row in patient_counts.iter_rows(named=True):
        logger.info(f"    {row['PatientICN']}: {row['ImmunizationCount']} immunizations")

    return df


def main():
    """Run Bronze extraction for Immunizations (CDWWork/VistA)."""
    logger.info("=" * 70)
    logger.info("BRONZE ETL: Immunizations (CDWWork/VistA)")
    logger.info("=" * 70)

    try:
        # Extract dimension table
        df_vaccine = extract_dim_vaccine()

        # Extract fact table
        df_immunization = extract_patient_immunization()

        logger.info("=" * 70)
        logger.info("✓ Bronze extraction complete for Immunizations (CDWWork)")
        logger.info("=" * 70)
        logger.info(f"Summary:")
        logger.info(f"  - Vaccines: {len(df_vaccine)} records")
        logger.info(f"  - Immunizations: {len(df_immunization)} records")
        logger.info(f"  - Output: MinIO bucket 'med-z1' under bronze/cdwwork/")

    except Exception as e:
        logger.error(f"✗ Bronze extraction failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
