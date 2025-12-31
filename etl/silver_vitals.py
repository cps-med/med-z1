# ---------------------------------------------------------------------
# silver_vitals.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze vitals data
#  - Read Bronze from both CDWWork (VistA) and CDWWork2 (Oracle Health/Cerner)
#  - Clean and validate data
#  - Resolve lookups: VitalType, VitalQualifier, Sta3n (facility names)
#  - Resolve PatientICN for CDWWork (to enable merging with CDWWork2)
#  - Harmonize schemas between CDWWork and CDWWork2
#  - Add data_source column to track origin
#  - Merge and deduplicate across sources
#  - Save to med-z1/silver/vitals as vitals_merged.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_vitals
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG, CDWWORK2_DB_CONFIG
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

    logger.info(f"Loaded {len(patient_icn_df)} PatientSID->ICN mappings")
    return patient_icn_df


def transform_cdwwork_vitals(minio_client, sta3n_lookup, patient_icn_lookup):
    """
    Transform CDWWork (VistA) vitals from Bronze to common Silver schema.
    Returns a polars DataFrame with harmonized vitals.
    """
    logger.info("=" * 70)
    logger.info("Transforming CDWWork (VistA) vitals...")
    logger.info("=" * 70)

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading CDWWork Bronze files...")

    # Read VitalType dimension
    vital_type_path = build_bronze_path("cdwwork", "vital_type_dim", "vital_type_dim_raw.parquet")
    df_vital_type = minio_client.read_parquet(vital_type_path)
    logger.info(f"  - Loaded {len(df_vital_type)} vital types")

    # Read VitalSign fact table
    vital_sign_path = build_bronze_path("cdwwork", "vital_sign", "vital_sign_raw.parquet")
    df_vital_sign = minio_client.read_parquet(vital_sign_path)
    logger.info(f"  - Loaded {len(df_vital_sign)} vital signs")

    # Read VitalQualifier dimension
    vital_qualifier_path = build_bronze_path("cdwwork", "vital_qualifier_dim", "vital_qualifier_dim_raw.parquet")
    df_vital_qualifier = minio_client.read_parquet(vital_qualifier_path)
    logger.info(f"  - Loaded {len(df_vital_qualifier)} vital qualifiers")

    # Read VitalSignQualifier bridge table
    vital_sign_qualifier_path = build_bronze_path("cdwwork", "vital_sign_qualifier", "vital_sign_qualifier_raw.parquet")
    df_vital_sign_qualifier = minio_client.read_parquet(vital_sign_qualifier_path)
    logger.info(f"  - Loaded {len(df_vital_sign_qualifier)} vital sign qualifiers")

    # ==================================================================
    # Step 2: Resolve PatientICN for CDWWork vitals
    # ==================================================================
    logger.info("Step 2: Resolving PatientICN...")

    df_vital_sign = df_vital_sign.join(
        patient_icn_lookup.select([
            pl.col("PatientSID"),
            pl.col("PatientICN").alias("patient_icn")
        ]),
        on="PatientSID",
        how="left"
    )
    logger.info(f"  - Resolved PatientICN for {df_vital_sign.filter(pl.col('patient_icn').is_not_null()).height} vitals")

    # ==================================================================
    # Step 3: Join VitalSign with VitalType
    # ==================================================================
    logger.info("Step 3: Joining VitalSign with VitalType...")

    df = df_vital_sign.join(
        df_vital_type.select([
            pl.col("VitalTypeSID"),
            pl.col("VitalType").str.strip_chars().alias("vital_type"),
            pl.col("Abbreviation").str.strip_chars().alias("vital_abbr"),
            pl.col("UnitOfMeasure").str.strip_chars().alias("unit_of_measure"),
            pl.col("Category").str.strip_chars().alias("category"),
        ]),
        on="VitalTypeSID",
        how="left"
    )
    logger.info(f"  - Joined vital types: {len(df)} records")

    # ==================================================================
    # Step 4: Aggregate Qualifiers per VitalSign
    # ==================================================================
    logger.info("Step 4: Aggregating qualifiers...")

    # Join VitalSignQualifier with VitalQualifier to get qualifier details
    df_qualifiers_detail = df_vital_sign_qualifier.join(
        df_vital_qualifier.select([
            pl.col("VitalQualifierSID"),
            pl.col("VitalQualifier").str.strip_chars().alias("qualifier_name"),
            pl.col("QualifierType").str.strip_chars().alias("qualifier_type"),
        ]),
        on="VitalQualifierSID",
        how="left"
    )

    # Aggregate qualifiers as JSON array per VitalSignSID
    # Build JSON strings manually for each qualifier struct
    df_qualifiers_agg = (
        df_qualifiers_detail
        .with_columns([
            pl.format(
                '{"qualifier_type":"{}","qualifier_name":"{}"}',
                pl.col("qualifier_type"),
                pl.col("qualifier_name")
            ).alias("qualifier_json")
        ])
        .group_by("VitalSignSID")
        .agg([
            pl.col("qualifier_json").alias("qualifier_list")
        ])
        .with_columns([
            pl.concat_str(
                pl.lit("["),
                pl.col("qualifier_list").list.join(","),
                pl.lit("]")
            ).alias("qualifiers")
        ])
        .select(["VitalSignSID", "qualifiers"])
    )

    logger.info(f"  - Aggregated qualifiers for {len(df_qualifiers_agg)} vital signs")

    # ==================================================================
    # Step 5: Join qualifiers to main vitals dataframe
    # ==================================================================
    logger.info("Step 5: Joining qualifiers to vitals...")

    df = df.join(
        df_qualifiers_agg,
        on="VitalSignSID",
        how="left"
    )

    # ==================================================================
    # Step 6: Resolve Sta3n lookups (facility names)
    # ==================================================================
    logger.info("Step 6: Resolving Sta3n lookups...")

    # Cast Sta3n to string for consistent join
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
    # Step 7: Transform to common Silver schema
    # ==================================================================
    logger.info("Step 7: Transforming to common schema...")

    df = df.with_columns([
        # Identity
        pl.col("patient_icn").alias("patient_icn"),

        # Vital info
        pl.col("VitalSignSID").alias("vital_record_id"),
        pl.col("vital_type").alias("vital_type"),
        pl.col("vital_abbr").alias("vital_abbr"),

        # Timing
        pl.col("VitalSignTakenDateTime").alias("taken_datetime"),
        pl.col("VitalSignEnteredDateTime").alias("entered_datetime"),

        # Values (cast to Float64 for consistent schema with CDWWork2)
        pl.col("ResultValue").str.strip_chars().alias("result_value"),
        pl.col("NumericValue").cast(pl.Float64).alias("numeric_value"),
        pl.col("Systolic").cast(pl.Float64).alias("systolic"),
        pl.col("Diastolic").cast(pl.Float64).alias("diastolic"),
        pl.col("MetricValue").cast(pl.Float64).alias("metric_value"),
        pl.col("unit_of_measure").alias("unit_of_measure"),
        pl.col("category").alias("category"),

        # Location info
        pl.col("LocationSID").alias("location_id"),
        pl.col("LocationName").alias("location_name"),
        pl.col("LocationType").alias("location_type"),

        # Staff info
        pl.col("StaffName").alias("entered_by"),

        # Station info (already cast to string in Step 6)
        pl.col("Sta3n").alias("sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Qualifiers (JSON)
        pl.when(pl.col("qualifiers").is_null())
            .then(pl.lit("[]"))
            .otherwise(pl.col("qualifiers"))
            .alias("qualifiers"),

        # Data source
        pl.lit("CDWWork").alias("data_source"),

        # Metadata
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 8: Select final columns
    # ==================================================================
    logger.info("Step 8: Selecting final columns...")

    df = df.select([
        "patient_icn",
        "vital_record_id",
        "vital_type",
        "vital_abbr",
        "taken_datetime",
        "entered_datetime",
        "result_value",
        "numeric_value",
        "systolic",
        "diastolic",
        "metric_value",
        "unit_of_measure",
        "category",
        "qualifiers",
        "location_id",
        "location_name",
        "location_type",
        "entered_by",
        "sta3n",
        "facility_name",
        "data_source",
        "last_updated",
    ])

    logger.info(f"CDWWork transformation complete: {len(df)} vitals")
    return df


def transform_cdwwork2_vitals(minio_client, sta3n_lookup):
    """
    Transform CDWWork2 (Oracle Health/Cerner) vitals from Bronze to common Silver schema.
    Returns a polars DataFrame with harmonized vitals.
    """
    logger.info("=" * 70)
    logger.info("Transforming CDWWork2 (Oracle Health) vitals...")
    logger.info("=" * 70)

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading CDWWork2 Bronze files...")

    # Read VitalResult (already denormalized)
    vital_result_path = build_bronze_path("cdwwork2", "vital_result", "vital_result_raw.parquet")
    df_vital_result = minio_client.read_parquet(vital_result_path)
    logger.info(f"  - Loaded {len(df_vital_result)} vital results")

    # Read CodeValue (for reference)
    code_value_path = build_bronze_path("cdwwork2", "code_value", "code_value_raw.parquet")
    df_code_value = minio_client.read_parquet(code_value_path)
    logger.info(f"  - Loaded {len(df_code_value)} code values")

    # ==================================================================
    # Step 2: Resolve Sta3n lookups (facility names)
    # ==================================================================
    logger.info("Step 2: Resolving Sta3n lookups...")

    df = df_vital_result.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # ==================================================================
    # Step 3: Transform to common Silver schema
    # ==================================================================
    logger.info("Step 3: Transforming to common schema...")

    df = df.with_columns([
        # Identity (CDWWork2 already has PatientICN)
        pl.col("PatientICN").alias("patient_icn"),

        # Vital info
        pl.col("VitalResultSID").alias("vital_record_id"),
        pl.col("VitalTypeName").str.strip_chars().alias("vital_type"),
        pl.lit(None).cast(pl.Utf8).alias("vital_abbr"),  # CDWWork2 doesn't have abbreviations

        # Timing
        pl.col("TakenDateTime").alias("taken_datetime"),
        pl.col("EnteredDateTime").alias("entered_datetime"),

        # Values (cast to Float64 for consistent schema with CDWWork)
        pl.col("ResultValue").str.strip_chars().alias("result_value"),
        pl.col("NumericValue").cast(pl.Float64).alias("numeric_value"),
        pl.col("Systolic").cast(pl.Float64).alias("systolic"),
        pl.col("Diastolic").cast(pl.Float64).alias("diastolic"),
        pl.lit(None).cast(pl.Float64).alias("metric_value"),  # CDWWork2 doesn't have pre-calculated metric
        pl.col("UnitName").str.strip_chars().alias("unit_of_measure"),
        pl.lit(None).cast(pl.Utf8).alias("category"),  # CDWWork2 doesn't have category

        # Location info (CDWWork2 only has LocationName, no LocationSID or LocationType)
        pl.lit(None).cast(pl.Int64).alias("location_id"),
        pl.col("LocationName").str.strip_chars().alias("location_name"),
        pl.lit(None).cast(pl.Utf8).alias("location_type"),

        # Staff info (CDWWork2 doesn't have staff names)
        pl.lit(None).cast(pl.Utf8).alias("entered_by"),

        # Station info
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Qualifiers (CDWWork2 doesn't have qualifiers)
        pl.lit("[]").alias("qualifiers"),

        # Data source
        pl.lit("CDWWork2").alias("data_source"),

        # Metadata
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 4: Select final columns
    # ==================================================================
    logger.info("Step 4: Selecting final columns...")

    df = df.select([
        "patient_icn",
        "vital_record_id",
        "vital_type",
        "vital_abbr",
        "taken_datetime",
        "entered_datetime",
        "result_value",
        "numeric_value",
        "systolic",
        "diastolic",
        "metric_value",
        "unit_of_measure",
        "category",
        "qualifiers",
        "location_id",
        "location_name",
        "location_type",
        "entered_by",
        "sta3n",
        "facility_name",
        "data_source",
        "last_updated",
    ])

    logger.info(f"CDWWork2 transformation complete: {len(df)} vitals")
    return df


def transform_vitals_silver():
    """
    Transform Bronze vitals data from both CDWWork and CDWWork2 to Silver layer.
    Harmonizes schemas, adds data_source tracking, and merges into single dataset.
    """

    logger.info("=" * 70)
    logger.info("Starting Silver vitals transformation (CDWWork + CDWWork2)")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Load shared lookup tables
    sta3n_lookup = load_sta3n_lookup()
    patient_icn_lookup = load_patient_icn_lookup()

    # Transform CDWWork vitals
    df_cdwwork = transform_cdwwork_vitals(minio_client, sta3n_lookup, patient_icn_lookup)

    # Transform CDWWork2 vitals
    df_cdwwork2 = transform_cdwwork2_vitals(minio_client, sta3n_lookup)

    # ==================================================================
    # Merge both sources
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Merging CDWWork and CDWWork2 vitals...")
    logger.info("=" * 70)

    df_merged = pl.concat([df_cdwwork, df_cdwwork2], how="vertical")
    logger.info(f"  - Total vitals after merge: {len(df_merged)}")
    logger.info(f"    - CDWWork: {len(df_cdwwork)}")
    logger.info(f"    - CDWWork2: {len(df_cdwwork2)}")

    # ==================================================================
    # Deduplicate (if needed)
    # ==================================================================
    # In current mock data, there should be no duplicates since CDWWork and CDWWork2
    # have different time periods and facilities. But we'll check anyway.

    # Sort by patient_icn, vital_type, taken_datetime, data_source
    df_merged = df_merged.sort(["patient_icn", "vital_type", "taken_datetime", "data_source"])

    # Check for potential duplicates
    dup_check = df_merged.group_by(["patient_icn", "vital_type", "taken_datetime"]).agg([
        pl.count().alias("count")
    ]).filter(pl.col("count") > 1)

    if len(dup_check) > 0:
        logger.warning(f"Found {len(dup_check)} potential duplicate vital records (same patient + type + time)")
        logger.warning("Keeping all records (no deduplication in Phase 2)")
    else:
        logger.info("No duplicate vitals found (expected for mock data)")

    # ==================================================================
    # Write to Silver layer
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Writing to Silver layer...")
    logger.info("=" * 70)

    silver_path = build_silver_path("vitals", "vitals_merged.parquet")
    minio_client.write_parquet(df_merged, silver_path)

    logger.info("=" * 70)
    logger.info(f"Silver transformation complete: {len(df_merged)} vitals written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{silver_path}")
    logger.info(f"  - CDWWork (VistA): {len(df_cdwwork)} vitals")
    logger.info(f"  - CDWWork2 (Oracle Health): {len(df_cdwwork2)} vitals")
    logger.info("=" * 70)

    return df_merged


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_vitals_silver()
