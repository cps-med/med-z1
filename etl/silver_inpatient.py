# ---------------------------------------------------------------------
# silver_inpatient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze inpatient data
#  - Read Bronze: inpatient
#  - Clean and validate data
#  - Resolve lookups: Sta3n (facility names), Staff (providers)
#  - Calculate derived fields (is_active, age_of_encounter)
#  - Save to med-z1/silver/inpatient as inpatient_cleaned.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_inpatient
# ---------------------------------------------------------------------

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
        Sta3nName
    FROM Dim.Sta3n
    WHERE Active = 'Y'
    """

    with engine.connect() as conn:
        sta3n_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(sta3n_df)} active stations for lookup")
    return sta3n_df


def load_staff_lookup():
    """
    Load Staff lookup table from CDWWork.
    Returns a polars DataFrame with StaffSID to StaffName mapping.
    """
    logger.info("Loading Staff lookup table from CDWWork")

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
        StaffSID,
        StaffName,
        LastName,
        FirstName
    FROM SStaff.SStaff
    """

    with engine.connect() as conn:
        staff_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(staff_df)} staff records for lookup")
    return staff_df


def transform_inpatient_silver():
    """Transform Bronze inpatient data to Silver layer in MinIO."""

    logger.info("=" * 70)
    logger.info("Starting Silver inpatient transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading Bronze Parquet file...")

    # Read inpatient encounters
    inpatient_path = build_bronze_path("cdwwork", "inpatient", "inpatient_raw.parquet")
    df = minio_client.read_parquet(inpatient_path)
    logger.info(f"  - Loaded {len(df)} inpatient encounters")

    # Load lookup tables
    sta3n_lookup = load_sta3n_lookup()
    staff_lookup = load_staff_lookup()

    # ==================================================================
    # Step 2: Resolve Sta3n lookups (facility names)
    # ==================================================================
    logger.info("Step 2: Resolving Sta3n lookups...")

    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # ==================================================================
    # Step 3: Resolve Staff lookups (admitting provider)
    # ==================================================================
    logger.info("Step 3: Resolving admitting provider lookups...")

    df = df.join(
        staff_lookup.select([
            pl.col("StaffSID"),
            pl.col("StaffName").alias("admitting_provider_name"),
            pl.col("LastName").alias("provider_last_name"),
            pl.col("FirstName").alias("provider_first_name")
        ]),
        left_on="AdmittingProviderSID",
        right_on="StaffSID",
        how="left"
    )

    # ==================================================================
    # Step 4: Clean, transform, and standardize fields
    # ==================================================================
    logger.info("Step 4: Cleaning and transforming fields...")

    df = df.with_columns([
        # Standardize column names - IDs
        pl.col("InpatientSID").alias("inpatient_id"),
        pl.col("PatientSID").alias("patient_sid"),

        # Admission details
        pl.col("AdmitDateTime").alias("admit_datetime"),
        pl.col("AdmitLocationSID").alias("admit_location_id"),
        pl.col("AdmittingProviderSID").alias("admitting_provider_id"),
        pl.col("AdmitDiagnosisICD10").str.strip_chars().alias("admit_diagnosis_code"),

        # Discharge details
        pl.col("DischargeDateTime").alias("discharge_datetime"),
        pl.col("DischargeDateSID").alias("discharge_date_id"),
        pl.col("DischargeWardLocationSID").alias("discharge_location_id"),
        pl.col("DischargeDiagnosisICD10").str.strip_chars().alias("discharge_diagnosis_code"),
        pl.col("DischargeDiagnosis").str.strip_chars().alias("discharge_diagnosis_text"),
        pl.col("DischargeDisposition").str.strip_chars().alias("discharge_disposition"),

        # Calculated fields
        pl.col("LengthOfStay").alias("length_of_stay"),
        pl.col("EncounterStatus").str.strip_chars().alias("encounter_status"),

        # Station info
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Provider info
        pl.col("admitting_provider_name").str.strip_chars().alias("admitting_provider_name"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 5: Add derived fields
    # ==================================================================
    logger.info("Step 5: Adding derived fields...")

    # Convert datetime columns to UTC for consistent timezone handling
    df = df.with_columns([
        pl.col("admit_datetime").dt.replace_time_zone("UTC").alias("admit_datetime"),
        pl.col("discharge_datetime").dt.replace_time_zone("UTC").alias("discharge_datetime"),
    ])

    df = df.with_columns([
        # is_active: True if discharge_datetime is NULL
        pl.when(pl.col("discharge_datetime").is_null())
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("is_active"),

        # days_since_admit: days from admit to now (for active) or to discharge (for discharged)
        pl.when(pl.col("discharge_datetime").is_null())
            .then(
                (pl.lit(datetime.now(timezone.utc)) - pl.col("admit_datetime"))
                .dt.total_days()
            )
            .otherwise(
                (pl.col("discharge_datetime") - pl.col("admit_datetime"))
                .dt.total_days()
            )
            .alias("total_days"),

        # admission_type: Categorize based on length of stay and status
        pl.when(pl.col("encounter_status").str.to_lowercase() == "active")
            .then(pl.lit("Active Admission"))
            .when(pl.col("length_of_stay") == 0)
            .then(pl.lit("Observation"))
            .when(pl.col("length_of_stay") <= 3)
            .then(pl.lit("Short Stay"))
            .when(pl.col("length_of_stay") <= 7)
            .then(pl.lit("Standard Stay"))
            .otherwise(pl.lit("Extended Stay"))
            .alias("admission_category"),
    ])

    # ==================================================================
    # Step 6: Select final columns
    # ==================================================================
    logger.info("Step 6: Selecting final columns...")

    df = df.select([
        # Identifiers
        "inpatient_id",
        "patient_sid",

        # Admission info
        "admit_datetime",
        "admit_location_id",
        "admit_diagnosis_code",
        "admitting_provider_id",
        "admitting_provider_name",

        # Discharge info
        "discharge_datetime",
        "discharge_date_id",
        "discharge_location_id",
        "discharge_diagnosis_code",
        "discharge_diagnosis_text",
        "discharge_disposition",

        # Metrics
        "length_of_stay",
        "total_days",
        "encounter_status",
        "is_active",
        "admission_category",

        # Facility
        "sta3n",
        "facility_name",

        # Metadata
        "source_system",
        "last_updated",
    ])

    # ==================================================================
    # Step 7: Write to Silver layer
    # ==================================================================
    logger.info("Step 7: Writing to Silver layer...")

    silver_path = build_silver_path("inpatient", "inpatient_cleaned.parquet")
    minio_client.write_parquet(df, silver_path)

    logger.info("=" * 70)
    logger.info(f"Silver transformation complete: {len(df)} encounters written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{silver_path}")
    logger.info("=" * 70)

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_inpatient_silver()
