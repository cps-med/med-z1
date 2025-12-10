# ---------------------------------------------------------------------
# silver_patient_flags.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver versions from Bronze patient flags data
#  - read from med-z1/bronze/cdwwork/patient_record_flag_*
#  - clean, validate, and enrich data
#  - resolve Sta3n lookups to facility names
#  - save to med-z1/silver/patient_record_flag_*
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat as a module:
#  $ cd med-z1
#  $ python -m etl.silver_patient_flags
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def load_sta3n_lookup():
    """
    Load Sta3n lookup table from CDWWork.
    Returns a polars DataFrame with Sta3n code to name mapping.
    """
    logger.info("Loading Sta3n lookup table from CDWWork")

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

    query = """
    SELECT
        Sta3n,
        Sta3nName,
        Active
    FROM Dim.Sta3n
    WHERE Active = 'Y'
    """

    with engine.connect() as conn:
        sta3n_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(sta3n_df)} active stations for lookup")
    return sta3n_df


def transform_flag_dimension(minio_client, sta3n_lookup):
    """Transform Dim.PatientRecordFlag from Bronze to Silver."""
    logger.info("Starting Silver transformation: PatientRecordFlag dimension")

    # Read Bronze Parquet
    bronze_path = build_bronze_path(
        "cdwwork",
        "patient_record_flag_dim",
        "patient_record_flag_dim_raw.parquet"
    )
    df = minio_client.read_parquet(bronze_path)
    logger.info(f"Read {len(df)} flag definitions from Bronze")

    # Clean and standardize
    df = df.with_columns([
        # Standardize field names (snake_case)
        pl.col("PatientRecordFlagSID").alias("flag_sid"),
        pl.col("FlagName").str.strip_chars().alias("flag_name"),
        pl.col("FlagType").str.strip_chars().str.to_uppercase().alias("flag_type"),
        pl.col("FlagCategory").str.strip_chars().alias("flag_category"),
        pl.col("FlagSourceType").str.strip_chars().alias("flag_source_type"),
        pl.col("NationalFlagIEN").alias("national_flag_ien"),
        pl.col("LocalFlagIEN").alias("local_flag_ien"),
        pl.col("ReviewFrequencyDays").alias("review_frequency_days"),
        pl.col("ReviewNotificationDays").alias("review_notification_days"),
        pl.col("IsActive").alias("is_active"),
        pl.col("InactivationDate").cast(pl.Date).alias("inactivation_date"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Select final columns
    df = df.select([
        "flag_sid",
        "flag_name",
        "flag_type",
        "flag_category",
        "flag_source_type",
        "national_flag_ien",
        "local_flag_ien",
        "review_frequency_days",
        "review_notification_days",
        "is_active",
        "inactivation_date",
        "source_system",
        "last_updated",
    ])

    # Write to Silver
    silver_path = build_silver_path(
        "patient_record_flag_dim",
        "patient_record_flag_dim_cleaned.parquet"
    )
    minio_client.write_parquet(df, silver_path)

    logger.info(f"Silver transformation complete: {len(df)} flag definitions")
    return df


def transform_flag_assignments(minio_client, sta3n_lookup):
    """Transform SPatient.PatientRecordFlagAssignment from Bronze to Silver."""
    logger.info("Starting Silver transformation: PatientRecordFlagAssignment")

    # Read Bronze Parquet
    bronze_path = build_bronze_path(
        "cdwwork",
        "patient_record_flag_assignment",
        "patient_record_flag_assignment_raw.parquet"
    )
    df = minio_client.read_parquet(bronze_path)
    logger.info(f"Read {len(df)} flag assignments from Bronze")

    # Clean and standardize
    df = df.with_columns([
        # Standardize field names
        pl.col("PatientRecordFlagAssignmentSID").alias("assignment_sid"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("PatientRecordFlagSID").alias("flag_sid"),
        pl.col("FlagName").str.strip_chars().alias("flag_name"),
        pl.col("FlagCategory").str.strip_chars().alias("flag_category"),
        pl.col("FlagSourceType").str.strip_chars().alias("flag_source_type"),
        pl.col("NationalFlagIEN").alias("national_flag_ien"),
        pl.col("LocalFlagIEN").alias("local_flag_ien"),
        pl.col("IsActive").alias("is_active"),
        pl.col("AssignmentStatus").str.strip_chars().str.to_uppercase().alias("assignment_status"),

        # Handle dates - convert to UTC timestamps
        pl.col("AssignmentDateTime").cast(pl.Datetime).alias("assignment_datetime"),
        pl.col("InactivationDateTime").cast(pl.Datetime).alias("inactivation_datetime"),
        pl.col("LastReviewDateTime").cast(pl.Datetime).alias("last_review_datetime"),
        pl.col("NextReviewDateTime").cast(pl.Datetime).alias("next_review_datetime"),

        # Sta3n fields (will be resolved next)
        pl.col("OwnerSiteSta3n").str.strip_chars().alias("owner_site_sta3n"),
        pl.col("OriginatingSiteSta3n").str.strip_chars().alias("originating_site_sta3n"),
        pl.col("LastUpdateSiteSta3n").str.strip_chars().alias("last_update_site_sta3n"),

        # Review settings
        pl.col("ReviewFrequencyDays").alias("review_frequency_days"),
        pl.col("ReviewNotificationDays").alias("review_notification_days"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Resolve Sta3n lookups - Owner Site
    owner_lookup = sta3n_lookup.select([
        pl.col("Sta3n"),
        pl.col("Sta3nName").alias("owner_site_name")
    ])
    df = df.join(
        owner_lookup,
        left_on="owner_site_sta3n",
        right_on=pl.col("Sta3n").cast(pl.Utf8),
        how="left"
    ).drop("Sta3n")

    # Resolve Sta3n lookups - Originating Site
    orig_lookup = sta3n_lookup.select([
        pl.col("Sta3n"),
        pl.col("Sta3nName").alias("originating_site_name")
    ])
    df = df.join(
        orig_lookup,
        left_on="originating_site_sta3n",
        right_on=pl.col("Sta3n").cast(pl.Utf8),
        how="left"
    ).drop("Sta3n")

    # Resolve Sta3n lookups - Last Update Site
    update_lookup = sta3n_lookup.select([
        pl.col("Sta3n"),
        pl.col("Sta3nName").alias("last_update_site_name")
    ])
    df = df.join(
        update_lookup,
        left_on="last_update_site_sta3n",
        right_on=pl.col("Sta3n").cast(pl.Utf8),
        how="left"
    ).drop("Sta3n")

    # Select final columns
    df = df.select([
        "assignment_sid",
        "patient_sid",
        "flag_sid",
        "flag_name",
        "flag_category",
        "flag_source_type",
        "national_flag_ien",
        "local_flag_ien",
        "is_active",
        "assignment_status",
        "assignment_datetime",
        "inactivation_datetime",
        "owner_site_sta3n",
        "owner_site_name",
        "originating_site_sta3n",
        "originating_site_name",
        "last_update_site_sta3n",
        "last_update_site_name",
        "review_frequency_days",
        "review_notification_days",
        "last_review_datetime",
        "next_review_datetime",
        "source_system",
        "last_updated",
    ])

    # Write to Silver
    silver_path = build_silver_path(
        "patient_record_flag_assignment",
        "patient_record_flag_assignment_cleaned.parquet"
    )
    minio_client.write_parquet(df, silver_path)

    logger.info(f"Silver transformation complete: {len(df)} flag assignments")
    return df


def transform_flag_history(minio_client, sta3n_lookup):
    """Transform SPatient.PatientRecordFlagHistory from Bronze to Silver."""
    logger.info("Starting Silver transformation: PatientRecordFlagHistory")

    # Read Bronze Parquet
    bronze_path = build_bronze_path(
        "cdwwork",
        "patient_record_flag_history",
        "patient_record_flag_history_raw.parquet"
    )
    df = minio_client.read_parquet(bronze_path)
    logger.info(f"Read {len(df)} flag history records from Bronze")

    # Clean and standardize
    df = df.with_columns([
        # Standardize field names
        pl.col("PatientRecordFlagHistorySID").alias("history_sid"),
        pl.col("PatientRecordFlagAssignmentSID").alias("assignment_sid"),
        pl.col("PatientSID").alias("patient_sid"),

        # Handle dates
        pl.col("HistoryDateTime").cast(pl.Datetime).alias("history_datetime"),

        # Action details
        pl.col("ActionCode").alias("action_code"),
        pl.col("ActionName").str.strip_chars().str.to_uppercase().alias("action_name"),

        # Provider information (names already populated in source - no lookup needed)
        pl.col("EnteredByDUZ").alias("entered_by_duz"),
        pl.col("EnteredByName").str.strip_chars().alias("entered_by_name"),
        pl.col("ApprovedByDUZ").alias("approved_by_duz"),
        pl.col("ApprovedByName").str.strip_chars().alias("approved_by_name"),

        # Clinical linkage
        pl.col("TiuDocumentIEN").alias("tiu_document_ien"),

        # SENSITIVE: Narrative text
        pl.col("HistoryComments").alias("history_comments"),

        # Site (will be resolved next)
        pl.col("EventSiteSta3n").str.strip_chars().alias("event_site_sta3n"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Resolve Sta3n lookup for event site
    df = df.join(
        sta3n_lookup.select(["Sta3n", "Sta3nName"]),
        left_on="event_site_sta3n",
        right_on=pl.col("Sta3n").cast(pl.Utf8),
        how="left"
    ).rename({"Sta3nName": "event_site_name"})

    # Select final columns
    df = df.select([
        "history_sid",
        "assignment_sid",
        "patient_sid",
        "history_datetime",
        "action_code",
        "action_name",
        "entered_by_duz",
        "entered_by_name",
        "approved_by_duz",
        "approved_by_name",
        "tiu_document_ien",
        "history_comments",  # SENSITIVE
        "event_site_sta3n",
        "event_site_name",
        "source_system",
        "last_updated",
    ])

    # Write to Silver
    silver_path = build_silver_path(
        "patient_record_flag_history",
        "patient_record_flag_history_cleaned.parquet"
    )
    minio_client.write_parquet(df, silver_path)

    logger.info(f"Silver transformation complete: {len(df)} flag history records")
    return df


def transform_patient_flags_silver():
    """
    Main function to transform all patient flags tables to Silver layer.
    Calls all three transformation functions in sequence.
    """
    logger.info("=" * 70)
    logger.info("Starting Silver Patient Flags Transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Load Sta3n lookup table
    sta3n_lookup = load_sta3n_lookup()

    # Transform all three tables
    dim_df = transform_flag_dimension(minio_client, sta3n_lookup)
    assignment_df = transform_flag_assignments(minio_client, sta3n_lookup)
    history_df = transform_flag_history(minio_client, sta3n_lookup)

    logger.info("=" * 70)
    logger.info("Silver Patient Flags Transformation Complete")
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
    transform_patient_flags_silver()
