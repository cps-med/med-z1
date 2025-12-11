# ---------------------------------------------------------------------
# bronze_patient_insurance.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Patient Insurance from CDWWork database.
#  - pull from SPatient.SPatientInsurance
#  - save to med-z1/bronze/cdwwork/patient_insurance
#  - as patient_insurance_raw.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a
# module:
#  $ cd med-z1
#  $ python -m etl.bronze_patient_insurance
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine, text
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)

def extract_patient_insurance_bronze():
    """Extract patient insurance data from CDWWork to Bronze layer in MinIO."""
    logger.info("Starting Bronze patient insurance extraction")

    # Initialize MinIO client
    minio_client = MinIOClient()
    logger.info("minio_client created")

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    logger.info(f"Created DB connection string: {conn_str}")

    # Create SQLAlchemy engine
    engine = create_engine(conn_str)

    # Extract query
    query = """
    SELECT
        SPatientInsuranceSID,
        PatientSID,
        PatientIEN,
        SPatientInsuranceIEN,
        Sta3n,
        InsuranceCompanySID,
        EmploymentStatus,
        RetirementDate,
        PolicyEffectiveDate
    FROM SPatient.SPatientInsurance
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} patient insurance records from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="patient_insurance",
        filename="patient_insurance_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} patient insurance records written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_patient_insurance_bronze()
