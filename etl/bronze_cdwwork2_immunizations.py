# ---------------------------------------------------------------------
# bronze_cdwwork2_immunizations.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Immunizations from CDWWork2 database (Cerner).
#  - Extract 2 tables:
#    1. ImmunizationMill.VaccineCode → bronze/cdwwork2/immunization_mill/vaccine_code
#    2. ImmunizationMill.VaccineAdmin → bronze/cdwwork2/immunization_mill/vaccine_admin
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_cdwwork2_immunizations
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK2_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_vaccine_code():
    """Extract ImmunizationMill.VaccineCode to Bronze layer."""
    logger.info("Starting Bronze extraction: ImmunizationMill.VaccineCode")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string for CDWWork2
    conn_str = (
        f"mssql+pyodbc://{CDWWORK2_DB_CONFIG['user']}:"
        f"{CDWWORK2_DB_CONFIG['password']}@"
        f"{CDWWORK2_DB_CONFIG['server']}/"
        f"{CDWWORK2_DB_CONFIG['name']}?"
        f"driver={CDWWORK2_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query - get all vaccine codes (including inactive for historical context)
    query = """
    SELECT
        VaccineCodeSID,
        CodeValue,
        Display,
        Definition,
        CVXCode,
        CodeSet,
        IsActive,
        CreatedDateTimeUTC
    FROM ImmunizationMill.VaccineCode
    ORDER BY VaccineCodeSID
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} vaccine codes from CDWWork2.ImmunizationMill.VaccineCode")

    # Add metadata columns (Bronze layer standard)
    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path (note: immunization_mill as subdomain)
    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="immunization_mill",
        filename="vaccine_code_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(f"✓ Bronze extraction complete: {object_key}")
    logger.info(f"  Records: {len(df)}")
    logger.info(f"  Columns: {df.columns}")

    return df


def extract_vaccine_admin():
    """Extract ImmunizationMill.VaccineAdmin to Bronze layer."""
    logger.info("Starting Bronze extraction: ImmunizationMill.VaccineAdmin")

    minio_client = MinIOClient()

    # Create SQLAlchemy connection string for CDWWork2
    conn_str = (
        f"mssql+pyodbc://{CDWWORK2_DB_CONFIG['user']}:"
        f"{CDWWORK2_DB_CONFIG['password']}@"
        f"{CDWWORK2_DB_CONFIG['server']}/"
        f"{CDWWORK2_DB_CONFIG['name']}?"
        f"driver={CDWWORK2_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    # Extract query - join with VaccineCode to get CVX code for harmonization
    # PatientICN is already denormalized in the table
    query = """
    SELECT
        va.VaccineAdminSID,
        va.PersonSID,
        va.EncounterSID,
        va.PatientICN,
        va.VaccineCodeSID,
        vc.CVXCode,
        vc.Display AS VaccineName,
        vc.CodeValue AS CernerCodeValue,
        va.AdministeredDateTime,
        va.SeriesNumber,
        va.TotalInSeries,
        va.DoseAmount,
        va.DoseUnit,
        va.RouteCode,
        va.BodySite,
        va.AdverseReaction,
        va.ProviderSID,
        va.FacilitySID,
        va.IsActive,
        va.CreatedDateTimeUTC
    FROM ImmunizationMill.VaccineAdmin va
    JOIN ImmunizationMill.VaccineCode vc ON va.VaccineCodeSID = vc.VaccineCodeSID
    WHERE va.IsActive = 1
    ORDER BY va.PersonSID, va.AdministeredDateTime DESC
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} immunization records from CDWWork2.ImmunizationMill.VaccineAdmin")

    # Add metadata columns (Bronze layer standard)
    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="immunization_mill",
        filename="vaccine_admin_raw.parquet"
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
    """Run Bronze extraction for Immunizations (CDWWork2/Cerner)."""
    logger.info("=" * 70)
    logger.info("BRONZE ETL: Immunizations (CDWWork2/Cerner)")
    logger.info("=" * 70)

    try:
        # Extract dimension table
        df_vaccine_code = extract_vaccine_code()

        # Extract fact table
        df_vaccine_admin = extract_vaccine_admin()

        logger.info("=" * 70)
        logger.info("✓ Bronze extraction complete for Immunizations (CDWWork2)")
        logger.info("=" * 70)
        logger.info(f"Summary:")
        logger.info(f"  - Vaccine Codes: {len(df_vaccine_code)} records")
        logger.info(f"  - Vaccine Administrations: {len(df_vaccine_admin)} records")
        logger.info(f"  - Output: MinIO bucket 'med-z1' under bronze/cdwwork2/immunization_mill/")

    except Exception as e:
        logger.error(f"✗ Bronze extraction failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
