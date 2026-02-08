# ---------------------------------------------------------------------
# bronze_problems.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Problems/Diagnoses from both CDWWork databases.
#  - Extract 4 tables:
#    1. Dim.ICD10 → bronze/cdwwork/icd10_dim
#    2. Dim.CharlsonMapping → bronze/cdwwork/charlson_mapping
#    3. Outpat.ProblemList → bronze/cdwwork/outpat_problemlist
#    4. EncMill.ProblemList → bronze/cdwwork2/encmill_problemlist
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_problems
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG, CDWWORK2_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_icd10_dim():
    """Extract Dim.ICD10 reference data to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.ICD10")

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

    # Extract query - get all ICD-10 codes
    query = """
    SELECT
        ICD10SID,
        ICD10Code,
        ICD10Description,
        ICD10Category,
        IsChronicCondition,
        CharlsonCondition,
        CreatedDate
    FROM Dim.ICD10
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} ICD-10 codes from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="icd10_dim",
        filename="icd10_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} ICD-10 codes written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_charlson_mapping():
    """Extract Dim.CharlsonMapping to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.CharlsonMapping")

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

    # Extract query - get all Charlson comorbidity mappings
    query = """
    SELECT
        CharlsonMappingSID,
        CharlsonCondition,
        CharlsonWeight,
        ICD10Code,
        ICD10Description,
        CreatedDate
    FROM Dim.CharlsonMapping
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} Charlson mappings from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="charlson_mapping",
        filename="charlson_mapping_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} Charlson mappings written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_outpat_problemlist():
    """Extract Outpat.ProblemList (VistA) to Bronze layer."""
    logger.info("Starting Bronze extraction: Outpat.ProblemList")

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

    # Extract query - get all VistA problem list records
    query = """
    SELECT
        ProblemSID,
        PatientSID,
        PatientICN,
        Sta3n,
        ProblemNumber,
        SNOMEDCode,
        SNOMEDDescription,
        ICD10Code,
        ICD10Description,
        ProblemStatus,
        OnsetDate,
        RecordedDate,
        LastModifiedDate,
        ResolvedDate,
        ProviderSID,
        ProviderName,
        Clinic,
        IsServiceConnected,
        IsAcuteCondition,
        IsChronicCondition,
        EnteredBy,
        EnteredDateTime
    FROM Outpat.ProblemList
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} VistA problem records from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit("VistA").alias("SourceEHR"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="outpat_problemlist",
        filename="outpat_problemlist_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} VistA problem records written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_encmill_problemlist():
    """Extract EncMill.ProblemList (Cerner) to Bronze layer."""
    logger.info("Starting Bronze extraction: EncMill.ProblemList")

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

    # Extract query - get all Cerner problem list records
    query = """
    SELECT
        DiagnosisSID,
        PatientKey,
        PatientICN,
        FacilityCode,
        ProblemID,
        DiagnosisCode,
        DiagnosisDescription,
        ClinicalTermCode,
        ClinicalTermDescription,
        StatusCode,
        OnsetDateTime,
        RecordDateTime,
        LastUpdateDateTime,
        ResolvedDateTime,
        ResponsibleProviderID,
        ResponsibleProviderName,
        RecordingLocation,
        ServiceConnectedFlag,
        AcuteFlag,
        ChronicFlag,
        CreatedByUserID,
        CreatedByUserName,
        CreatedDateTime
    FROM EncMill.ProblemList
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} Cerner problem records from CDWWork2")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit("Cerner").alias("SourceEHR"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="encmill_problemlist",
        filename="encmill_problemlist_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} Cerner problem records written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_all_problems_bronze():
    """Extract all problem/diagnosis tables to Bronze layer."""
    logger.info("=" * 70)
    logger.info("Starting Bronze extraction for all Problems/Diagnoses tables")
    logger.info("=" * 70)

    # Extract reference data (CDWWork)
    icd10_df = extract_icd10_dim()
    charlson_df = extract_charlson_mapping()

    # Extract clinical data (CDWWork + CDWWork2)
    vista_problems_df = extract_outpat_problemlist()
    cerner_problems_df = extract_encmill_problemlist()

    logger.info("=" * 70)
    logger.info("Bronze extraction complete for all Problems/Diagnoses tables")
    logger.info(f"  - ICD-10 Codes: {len(icd10_df)} rows")
    logger.info(f"  - Charlson Mappings: {len(charlson_df)} rows")
    logger.info(f"  - VistA Problems (CDWWork): {len(vista_problems_df)} rows")
    logger.info(f"  - Cerner Problems (CDWWork2): {len(cerner_problems_df)} rows")
    logger.info(f"  - Total Problem Records: {len(vista_problems_df) + len(cerner_problems_df)}")
    logger.info("=" * 70)

    return {
        "icd10": icd10_df,
        "charlson": charlson_df,
        "vista_problems": vista_problems_df,
        "cerner_problems": cerner_problems_df
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_all_problems_bronze()
