# ---------------------------------------------------------------------
# silver_inpatient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze inpatient data
#  - Read Bronze: CDWWork inpatient + CDWWork2 encounters
#  - Clean and validate data
#  - Resolve lookups: Sta3n (facility names), Staff (providers), PatientICN
#  - Harmonize schemas between CDWWork (VistA) and CDWWork2 (Cerner)
#  - Calculate derived fields (is_active, length_of_stay)
#  - Add data_source tracking ('CDWWork' vs 'CDWWork2')
#  - Save to med-z1/silver/encounters as encounters_merged.parquet
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

    # Cast Sta3n to string for consistent joins (CDWWork2 uses string)
    sta3n_df = sta3n_df.with_columns([
        pl.col("Sta3n").cast(pl.Utf8).alias("Sta3n")
    ])

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


def load_patient_icn_lookup():
    """
    Load PatientSID to PatientICN mapping from CDWWork.
    Returns a polars DataFrame with PatientSID -> PatientICN mapping.
    """
    logger.info("Loading PatientICN lookup table from CDWWork")

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
        PatientSID,
        PatientICN
    FROM SPatient.SPatient
    WHERE PatientICN IS NOT NULL
    """

    with engine.connect() as conn:
        patient_icn_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(patient_icn_df)} patient ICN mappings")
    return patient_icn_df


def transform_cdwwork_encounters(minio_client, sta3n_lookup, staff_lookup, patient_icn_lookup):
    """
    Transform CDWWork (VistA) inpatient encounters to common Silver schema.

    CDWWork Schema: Inpat.Inpatient (19 columns, inpatient-only)
    - Uses PatientSID (requires ICN lookup)
    - Uses SIDs for locations and providers (requires lookups)
    - Has diagnosis fields (ICD-10)
    - Has discharge disposition
    - Encounter type is implicitly 'INPATIENT'
    """

    logger.info("=" * 70)
    logger.info("Transforming CDWWork encounters...")
    logger.info("=" * 70)

    # ==================================================================
    # Step 1: Load Bronze Parquet file
    # ==================================================================
    logger.info("Step 1: Loading Bronze Parquet file...")

    # Read inpatient encounters from CDWWork
    inpatient_path = build_bronze_path("cdwwork", "inpatient", "inpatient_raw.parquet")
    df = minio_client.read_parquet(inpatient_path)
    logger.info(f"  - Loaded {len(df)} inpatient encounters from CDWWork")

    # ==================================================================
    # Step 2: Resolve PatientSID to PatientICN
    # ==================================================================
    logger.info("Step 2: Resolving PatientICN lookups...")

    df = df.join(
        patient_icn_lookup.select([
            pl.col("PatientSID"),
            pl.col("PatientICN")
        ]),
        on="PatientSID",
        how="left"
    )

    # ==================================================================
    # Step 3: Resolve Sta3n lookups (facility names)
    # ==================================================================
    logger.info("Step 3: Resolving Sta3n lookups...")

    # Cast Sta3n to string for consistent join with lookup table
    df = df.with_columns([
        pl.col("Sta3n").cast(pl.Utf8).alias("Sta3n")
    ])

    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # ==================================================================
    # Step 4: Resolve Staff lookups (admitting provider)
    # ==================================================================
    logger.info("Step 4: Resolving admitting provider lookups...")

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
    # Step 5: Transform to common Silver schema
    # ==================================================================
    logger.info("Step 5: Transforming to common Silver schema...")

    # Convert datetime columns to UTC for consistent timezone handling
    df = df.with_columns([
        pl.col("AdmitDateTime").dt.replace_time_zone("UTC").alias("AdmitDateTime"),
        pl.col("DischargeDateTime").dt.replace_time_zone("UTC").alias("DischargeDateTime"),
    ])

    df = df.with_columns([
        # Identity
        pl.col("PatientICN").alias("patient_icn"),
        pl.col("InpatientSID").alias("encounter_record_id"),

        # Encounter classification (CDWWork is inpatient-only)
        pl.lit("INPATIENT").alias("encounter_type"),

        # Timing - Use AdmitDateTime for both encounter_date and admit_date
        pl.col("AdmitDateTime").alias("encounter_date"),
        pl.col("AdmitDateTime").alias("admit_date"),
        pl.col("DischargeDateTime").alias("discharge_date"),

        # Location info (admit)
        pl.col("AdmitLocationName").alias("admit_location_name"),
        pl.col("AdmitLocationType").alias("admit_location_type"),

        # Location info (discharge) - CDWWork has this, CDWWork2 doesn't
        pl.col("DischargeLocationName").alias("discharge_location_name"),
        pl.col("DischargeLocationType").alias("discharge_location_type"),

        # Provider info
        pl.col("admitting_provider_name").str.strip_chars().alias("provider_name"),

        # Diagnosis fields (CDWWork only - CDWWork2 will be NULL in Phase 2)
        pl.col("AdmitDiagnosisICD10").str.strip_chars().alias("admit_diagnosis_icd10"),
        pl.col("DischargeDiagnosisICD10").str.strip_chars().alias("discharge_diagnosis_icd10"),
        pl.col("DischargeDiagnosis").str.strip_chars().alias("discharge_diagnosis"),

        # Discharge disposition (CDWWork only)
        pl.col("DischargeDisposition").str.strip_chars().alias("discharge_disposition"),

        # Station info
        pl.col("Sta3n").alias("facility_sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Calculated fields
        pl.col("LengthOfStay").alias("length_of_stay"),
        pl.col("EncounterStatus").str.strip_chars().alias("encounter_status"),

        # Data source
        pl.lit("CDWWork").alias("data_source"),

        # Metadata
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 6: Select final columns (common Silver schema)
    # ==================================================================
    logger.info("Step 6: Selecting final columns...")

    df = df.select([
        "patient_icn",
        "encounter_record_id",
        "encounter_type",
        "encounter_date",
        "admit_date",
        "discharge_date",
        "length_of_stay",
        "facility_sta3n",
        "facility_name",
        "admit_location_name",
        "admit_location_type",
        "discharge_location_name",
        "discharge_location_type",
        "provider_name",
        "admit_diagnosis_icd10",
        "discharge_diagnosis_icd10",
        "discharge_diagnosis",
        "discharge_disposition",
        "encounter_status",
        "data_source",
        "last_updated",
    ])

    logger.info(f"CDWWork transformation complete: {len(df)} encounters")
    return df


def transform_cdwwork2_encounters(minio_client, sta3n_lookup):
    """
    Transform CDWWork2 (Cerner) encounters to common Silver schema.

    CDWWork2 Schema: EncMill.Encounter (15 columns, multi-type)
    - Has PatientICN directly (no lookup needed)
    - Has denormalized location/provider names (no lookups needed)
    - Encounter types: INPATIENT, OUTPATIENT, EMERGENCY
    - No diagnosis fields (in separate tables - Phase 2 leaves NULL)
    - No discharge disposition (not tracked - Phase 2 leaves NULL)
    """

    logger.info("=" * 70)
    logger.info("Transforming CDWWork2 encounters...")
    logger.info("=" * 70)

    # ==================================================================
    # Step 1: Load Bronze Parquet file
    # ==================================================================
    logger.info("Step 1: Loading Bronze Parquet file...")

    # Read encounters from CDWWork2
    encounters_path = build_bronze_path("cdwwork2", "encounters", "encounters_raw.parquet")
    df = minio_client.read_parquet(encounters_path)
    logger.info(f"  - Loaded {len(df)} encounters from CDWWork2")

    # ==================================================================
    # Step 2: Resolve Sta3n lookups (facility names)
    # ==================================================================
    logger.info("Step 2: Resolving Sta3n lookups...")

    # CDWWork2 Sta3n is already string, but FacilityName is denormalized
    # We'll use the denormalized name but fallback to lookup if NULL
    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name_lookup")
        ]),
        on="Sta3n",
        how="left"
    )

    # Use FacilityName from CDWWork2 if available, otherwise use lookup
    df = df.with_columns([
        pl.when(pl.col("FacilityName").is_not_null())
            .then(pl.col("FacilityName"))
            .otherwise(pl.col("facility_name_lookup"))
            .alias("facility_name")
    ])

    # ==================================================================
    # Step 3: Transform to common Silver schema
    # ==================================================================
    logger.info("Step 3: Transforming to common Silver schema...")

    # Convert datetime columns to UTC for consistent timezone handling
    df = df.with_columns([
        pl.col("EncounterDate").dt.replace_time_zone("UTC").alias("EncounterDate"),
        pl.when(pl.col("AdmitDate").is_not_null())
            .then(pl.col("AdmitDate").dt.replace_time_zone("UTC"))
            .otherwise(pl.lit(None))
            .alias("AdmitDate"),
        pl.when(pl.col("DischargeDate").is_not_null())
            .then(pl.col("DischargeDate").dt.replace_time_zone("UTC"))
            .otherwise(pl.lit(None))
            .alias("DischargeDate"),
    ])

    # Calculate length of stay for inpatient encounters
    df = df.with_columns([
        pl.when((pl.col("EncounterType") == "INPATIENT") & pl.col("DischargeDate").is_not_null())
            .then(
                (pl.col("DischargeDate") - pl.col("AdmitDate"))
                .dt.total_days()
                .cast(pl.Int64)
            )
            .otherwise(pl.lit(None))
            .alias("calculated_length_of_stay")
    ])

    # Determine encounter status
    df = df.with_columns([
        pl.when(pl.col("DischargeDate").is_null())
            .then(pl.lit("Active"))
            .otherwise(pl.lit("Discharged"))
            .alias("encounter_status_calc")
    ])

    df = df.with_columns([
        # Identity
        pl.col("PatientICN").alias("patient_icn"),  # Already in CDWWork2!
        pl.col("EncounterSID").alias("encounter_record_id"),

        # Encounter classification (explicit in CDWWork2)
        pl.col("EncounterType").alias("encounter_type"),

        # Timing
        pl.col("EncounterDate").alias("encounter_date"),
        pl.col("AdmitDate").alias("admit_date"),
        pl.col("DischargeDate").alias("discharge_date"),
        pl.col("calculated_length_of_stay").alias("length_of_stay"),

        # Location info - CDWWork2 has single location (not separate admit/discharge)
        pl.col("LocationName").alias("admit_location_name"),
        pl.col("LocationType").alias("admit_location_type"),

        # Discharge location - CDWWork2 doesn't track separately (NULL)
        pl.lit(None, dtype=pl.Utf8).alias("discharge_location_name"),
        pl.lit(None, dtype=pl.Utf8).alias("discharge_location_type"),

        # Provider info - Denormalized in CDWWork2
        pl.col("ProviderName").alias("provider_name"),

        # Diagnosis fields - Not in EncMill.Encounter (NULL for Phase 2)
        pl.lit(None, dtype=pl.Utf8).alias("admit_diagnosis_icd10"),
        pl.lit(None, dtype=pl.Utf8).alias("discharge_diagnosis_icd10"),
        pl.lit(None, dtype=pl.Utf8).alias("discharge_diagnosis"),

        # Discharge disposition - Not in EncMill.Encounter (NULL for Phase 2)
        pl.lit(None, dtype=pl.Utf8).alias("discharge_disposition"),

        # Station info
        pl.col("Sta3n").alias("facility_sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Encounter status
        pl.col("encounter_status_calc").alias("encounter_status"),

        # Data source
        pl.lit("CDWWork2").alias("data_source"),

        # Metadata
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 4: Select final columns (common Silver schema)
    # ==================================================================
    logger.info("Step 4: Selecting final columns...")

    df = df.select([
        "patient_icn",
        "encounter_record_id",
        "encounter_type",
        "encounter_date",
        "admit_date",
        "discharge_date",
        "length_of_stay",
        "facility_sta3n",
        "facility_name",
        "admit_location_name",
        "admit_location_type",
        "discharge_location_name",
        "discharge_location_type",
        "provider_name",
        "admit_diagnosis_icd10",
        "discharge_diagnosis_icd10",
        "discharge_diagnosis",
        "discharge_disposition",
        "encounter_status",
        "data_source",
        "last_updated",
    ])

    logger.info(f"CDWWork2 transformation complete: {len(df)} encounters")
    return df


def transform_encounters_silver():
    """
    Transform Bronze encounter data from both CDWWork and CDWWork2 to Silver layer.
    Harmonizes schemas, adds data_source tracking, and merges into single dataset.
    """

    logger.info("=" * 70)
    logger.info("Starting Silver encounters transformation (CDWWork + CDWWork2)")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Load shared lookup tables
    sta3n_lookup = load_sta3n_lookup()
    staff_lookup = load_staff_lookup()
    patient_icn_lookup = load_patient_icn_lookup()

    # Transform CDWWork encounters
    df_cdwwork = transform_cdwwork_encounters(
        minio_client, sta3n_lookup, staff_lookup, patient_icn_lookup
    )

    # Transform CDWWork2 encounters
    df_cdwwork2 = transform_cdwwork2_encounters(minio_client, sta3n_lookup)

    # ==================================================================
    # Merge both sources
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Merging CDWWork and CDWWork2 encounters...")
    logger.info("=" * 70)

    df_merged = pl.concat([df_cdwwork, df_cdwwork2], how="vertical")

    # Sort by patient and encounter date
    df_merged = df_merged.sort(["patient_icn", "encounter_date"], descending=[False, True])

    logger.info(f"  - Total merged encounters: {len(df_merged)}")
    logger.info(f"  - CDWWork: {len(df_cdwwork)} encounters")
    logger.info(f"  - CDWWork2: {len(df_cdwwork2)} encounters")

    # Log data source distribution
    source_dist = df_merged.group_by("data_source").agg(
        pl.len().alias("count")
    ).sort("data_source")

    logger.info("  - Data source distribution:")
    for row in source_dist.iter_rows(named=True):
        logger.info(f"    {row['data_source']}: {row['count']} encounters")

    # ==================================================================
    # Write to Silver layer
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Writing merged encounters to Silver layer...")
    logger.info("=" * 70)

    silver_path = build_silver_path("encounters", "encounters_merged.parquet")
    minio_client.write_parquet(df_merged, silver_path)

    logger.info("=" * 70)
    logger.info(f"Silver transformation complete: {len(df_merged)} encounters")
    logger.info(f"  - Written to: s3://{minio_client.bucket_name}/{silver_path}")
    logger.info("=" * 70)

    return df_merged


# Legacy entry point (for backward compatibility)
def transform_inpatient_silver():
    """
    Legacy entry point - redirects to new dual-source function.
    Maintained for backward compatibility with existing scripts.
    """
    logger.warning("transform_inpatient_silver() is deprecated. Use transform_encounters_silver() instead.")
    return transform_encounters_silver()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_encounters_silver()
