# ---------------------------------------------------------------------
# silver_vitals.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze vitals data
#  - Read Bronze: vital_type_dim, vital_sign, vital_qualifier_dim, vital_sign_qualifier
#  - Clean and validate data
#  - Resolve lookups: VitalType, VitalQualifier, Sta3n (facility names)
#  - Implement unit conversions (F↔C, lb↔kg already in Bronze as MetricValue)
#  - Join vitals with types and qualifiers
#  - Save to med-z1/silver/vitals as vitals_cleaned.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_vitals
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


def transform_vitals_silver():
    """Transform Bronze vitals data to Silver layer in MinIO."""

    logger.info("=" * 70)
    logger.info("Starting Silver vitals transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading Bronze Parquet files...")

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

    # Load Sta3n lookup
    sta3n_lookup = load_sta3n_lookup()

    # ==================================================================
    # Step 2: Join VitalSign with VitalType
    # ==================================================================
    logger.info("Step 2: Joining VitalSign with VitalType...")

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
    # Step 3: Aggregate Qualifiers per VitalSign
    # ==================================================================
    logger.info("Step 3: Aggregating qualifiers...")

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
    # Step 4: Join qualifiers to main vitals dataframe
    # ==================================================================
    logger.info("Step 4: Joining qualifiers to vitals...")

    df = df.join(
        df_qualifiers_agg,
        on="VitalSignSID",
        how="left"
    )

    # ==================================================================
    # Step 5: Resolve Sta3n lookups (facility names)
    # ==================================================================
    logger.info("Step 5: Resolving Sta3n lookups...")

    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # ==================================================================
    # Step 6: Clean, transform, and standardize fields
    # ==================================================================
    logger.info("Step 6: Cleaning and transforming fields...")

    df = df.with_columns([
        # Standardize column names
        pl.col("VitalSignSID").alias("vital_sign_id"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("VitalTypeSID").alias("vital_type_id"),
        pl.col("VitalSignTakenDateTime").alias("taken_datetime"),
        pl.col("VitalSignEnteredDateTime").alias("entered_datetime"),

        # Clean result value
        pl.col("ResultValue").str.strip_chars().alias("result_value"),

        # Numeric values
        pl.col("NumericValue").alias("numeric_value"),
        pl.col("Systolic").alias("systolic"),
        pl.col("Diastolic").alias("diastolic"),

        # Metric conversions (already calculated in Bronze)
        pl.col("MetricValue").alias("metric_value"),

        # Location info
        pl.col("LocationSID").alias("location_id"),
        pl.col("LocationName").alias("location_name"),
        pl.col("LocationType").alias("location_type"),

        # Station info
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Qualifiers (JSON)
        pl.when(pl.col("qualifiers").is_null())
            .then(pl.lit("[]"))
            .otherwise(pl.col("qualifiers"))
            .alias("qualifiers"),

        # Metadata
        pl.col("SourceSystem").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 7: Select final columns
    # ==================================================================
    logger.info("Step 7: Selecting final columns...")

    df = df.select([
        "vital_sign_id",
        "patient_sid",
        "vital_type_id",
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
        "sta3n",
        "facility_name",
        "source_system",
        "last_updated",
    ])

    # ==================================================================
    # Step 8: Write to Silver layer
    # ==================================================================
    logger.info("Step 8: Writing to Silver layer...")

    silver_path = build_silver_path("vitals", "vitals_cleaned.parquet")
    minio_client.write_parquet(df, silver_path)

    logger.info("=" * 70)
    logger.info(f"Silver transformation complete: {len(df)} vitals written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{silver_path}")
    logger.info("=" * 70)

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_vitals_silver()
