# ---------------------------------------------------------------------
# bronze_patient_flags.py
# ---------------------------------------------------------------------
# Create MinIO Parquet versions of Patient Flags from CDWWork database.
#  - pull from Dim.PatientRecordFlag
#  - pull from SPatient.PatientRecordFlagAssignment
#  - pull from SPatient.PatientRecordFlagHistory
#  - save to med-z1/bronze/cdwwork/patient_record_flag_*
#  - minimal transformation (Bronze layer)
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a
# module:
#  $ cd med-z1
#  $ python -m etl.bronze_patient_flags
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine, text
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_flag_dimension():
    """Extract Dim.PatientRecordFlag table to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.PatientRecordFlag")

    # Initialize MinIO client
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

    # Create SQLAlchemy engine
    engine = create_engine(conn_str)

    # Extract query - get all active flag definitions
    query = """
    SELECT
        PatientRecordFlagSID,
        FlagName,
        FlagType,
        FlagCategory,
        FlagSourceType,
        NationalFlagIEN,
        LocalFlagIEN,
        ReviewFrequencyDays,
        ReviewNotificationDays,
        IsActive,
        InactivationDate,
        CreatedDateTimeUTC,
        UpdatedDateTimeUTC
    FROM Dim.PatientRecordFlag
    WHERE IsActive = 1
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} flag definitions from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="patient_record_flag_dim",
        filename="patient_record_flag_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} flag definitions written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_flag_assignments():
    """Extract SPatient.PatientRecordFlagAssignment table to Bronze layer."""
    logger.info("Starting Bronze extraction: SPatient.PatientRecordFlagAssignment")

    # Initialize MinIO client
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

    # Create SQLAlchemy engine
    engine = create_engine(conn_str)

    # Extract query - get all flag assignments
    query = """
    SELECT
        PatientRecordFlagAssignmentSID,
        PatientSID,
        PatientRecordFlagSID,
        FlagName,
        FlagCategory,
        FlagSourceType,
        NationalFlagIEN,
        LocalFlagIEN,
        IsActive,
        AssignmentStatus,
        AssignmentDateTime,
        InactivationDateTime,
        OwnerSiteSta3n,
        OriginatingSiteSta3n,
        LastUpdateSiteSta3n,
        ReviewFrequencyDays,
        ReviewNotificationDays,
        LastReviewDateTime,
        NextReviewDateTime,
        CreatedDateTimeUTC,
        UpdatedDateTimeUTC
    FROM SPatient.PatientRecordFlagAssignment
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} flag assignments from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="patient_record_flag_assignment",
        filename="patient_record_flag_assignment_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} flag assignments written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_flag_history():
    """Extract SPatient.PatientRecordFlagHistory table to Bronze layer."""
    logger.info("Starting Bronze extraction: SPatient.PatientRecordFlagHistory")

    # Initialize MinIO client
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

    # Create SQLAlchemy engine
    engine = create_engine(conn_str)

    # Extract query - get all flag history records (includes sensitive narrative)
    query = """
    SELECT
        PatientRecordFlagHistorySID,
        PatientRecordFlagAssignmentSID,
        PatientSID,
        HistoryDateTime,
        ActionCode,
        ActionName,
        EnteredByDUZ,
        EnteredByName,
        ApprovedByDUZ,
        ApprovedByName,
        TiuDocumentIEN,
        HistoryComments,
        EventSiteSta3n,
        CreatedDateTimeUTC
    FROM SPatient.PatientRecordFlagHistory
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} flag history records from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="patient_record_flag_history",
        filename="patient_record_flag_history_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} flag history records written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_patient_flags_bronze():
    """
    Main function to extract all patient flags tables to Bronze layer.
    Calls all three extraction functions in sequence.
    """
    logger.info("=" * 70)
    logger.info("Starting Bronze Patient Flags Extraction")
    logger.info("=" * 70)

    # Extract all three tables
    dim_df = extract_flag_dimension()
    assignment_df = extract_flag_assignments()
    history_df = extract_flag_history()

    logger.info("=" * 70)
    logger.info("Bronze Patient Flags Extraction Complete")
    logger.info(f"  - Flag Definitions: {len(dim_df)} records")
    logger.info(f"  - Flag Assignments: {len(assignment_df)} records")
    logger.info(f"  - Flag History: {len(history_df)} records")
    logger.info("=" * 70)

    return {
        "dimension": dim_df,
        "assignments": assignment_df,
        "history": history_df
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_patient_flags_bronze()
