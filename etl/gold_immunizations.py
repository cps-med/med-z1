# ---------------------------------------------------------------------
# gold_immunizations.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver immunizations data
#  - Read Silver: immunization_harmonized.parquet (merged CDWWork + CDWWork2)
#  - Join with Gold patient demographics (PatientSID → patient_key/ICN)
#  - Join with Dim.Location (LocationSID → location_name, location_type)
#  - Join with SStaff.Provider (ProviderSID → provider_name)
#  - Add station name lookup (Sta3n → station_name)
#  - Sort by patient_key, administered_datetime DESC (most recent first)
#  - Save to med-z1/gold/immunizations as patient_immunizations_final.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.gold_immunizations
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_location_lookup():
    """
    Load Location lookup table from CDWWork.
    Returns a polars DataFrame with LocationSID to location_name, location_type mapping.
    """
    logger.info("Loading Location lookup table from CDWWork")

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
        LocationSID,
        LocationName,
        LocationType
    FROM Dim.Location
    """

    with engine.connect() as conn:
        location_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(location_df)} locations for lookup")
    return location_df


def load_provider_lookup():
    """
    Load Provider lookup table from CDWWork.
    Returns a polars DataFrame with StaffSID to provider_name mapping.
    """
    logger.info("Loading Provider lookup table from CDWWork")

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
        StaffName
    FROM SStaff.SStaff
    """

    with engine.connect() as conn:
        provider_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(provider_df)} providers for lookup")
    return provider_df


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

    # Cast Sta3n to string for consistent joins
    sta3n_df = sta3n_df.with_columns([
        pl.col("Sta3n").cast(pl.Utf8).alias("Sta3n")
    ])

    logger.info(f"Loaded {len(sta3n_df)} active stations for lookup")
    return sta3n_df


def create_gold_immunizations():
    """Create Gold patient immunizations view in MinIO."""

    logger.info("=" * 70)
    logger.info("GOLD ETL: Immunizations")
    logger.info("=" * 70)

    try:
        # Initialize MinIO client
        minio_client = MinIOClient()

        # ==================================================================
        # Step 1: Read Silver immunizations from MinIO
        # ==================================================================
        logger.info("Step 1: Loading Silver immunizations...")

        silver_path = build_silver_path("immunizations", "immunization_harmonized.parquet")
        df_immunizations = minio_client.read_parquet(silver_path)
        logger.info(f"  - Read {len(df_immunizations)} immunization records from Silver layer")

        # ==================================================================
        # Step 2: Read Gold patient demographics to get ICN mapping
        # ==================================================================
        logger.info("Step 2: Loading Gold patient demographics...")

        patient_gold_path = build_gold_path("patient_demographics", "patient_demographics.parquet")
        df_patient = minio_client.read_parquet(patient_gold_path)
        logger.info(f"  - Read {len(df_patient)} patient records from Gold patient demographics")

        # Select only needed fields from patient demographics
        df_patient_lookup = df_patient.select([
            pl.col("patient_sid"),
            pl.col("patient_key"),  # This is the ICN
        ])

        # ==================================================================
        # Step 3: Join immunizations with patient demographics to get patient_key (ICN)
        # ==================================================================
        logger.info("Step 3: Joining with patient demographics...")

        df = df_immunizations.join(
            df_patient_lookup,
            on="patient_sid",
            how="left"  # Keep all immunizations even if patient not in Gold
        )
        logger.info(f"  - Joined immunizations with patient demographics: {len(df)} records")

        # Filter to only patients with valid ICN (should be all in mock data)
        df = df.filter(pl.col("patient_key").is_not_null())
        logger.info(f"  - Filtered to patients with valid ICN: {len(df)} records")

        # ==================================================================
        # Step 4: Load lookup tables from SQL Server
        # ==================================================================
        logger.info("Step 4: Loading lookup tables...")

        location_lookup = load_location_lookup()
        provider_lookup = load_provider_lookup()
        sta3n_lookup = load_sta3n_lookup()

        # ==================================================================
        # Step 5: Join with Location lookup
        # ==================================================================
        logger.info("Step 5: Joining with Location lookup...")

        df = df.join(
            location_lookup.select([
                pl.col("LocationSID"),
                pl.col("LocationName").str.strip_chars().alias("location_name"),
                pl.col("LocationType").str.strip_chars().alias("location_type"),
            ]),
            left_on="location_sid",
            right_on="LocationSID",
            how="left"
        )
        logger.info(f"  - Joined with locations: {df.filter(pl.col('location_name').is_not_null()).height} have location names")

        # ==================================================================
        # Step 6: Join with Provider lookup (ordering provider)
        # ==================================================================
        logger.info("Step 6: Joining with Provider lookup (ordering provider)...")

        df = df.join(
            provider_lookup.select([
                pl.col("StaffSID"),
                pl.col("StaffName").str.strip_chars().alias("ordering_provider_name"),
            ]),
            left_on="ordering_provider_sid",
            right_on="StaffSID",
            how="left"
        )
        logger.info(f"  - Joined with ordering providers: {df.filter(pl.col('ordering_provider_name').is_not_null()).height} have provider names")

        # ==================================================================
        # Step 7: Join with Provider lookup (administering provider)
        # ==================================================================
        logger.info("Step 7: Joining with Provider lookup (administering provider)...")

        df = df.join(
            provider_lookup.select([
                pl.col("StaffSID"),
                pl.col("StaffName").str.strip_chars().alias("administering_provider_name"),
            ]),
            left_on="administering_provider_sid",
            right_on="StaffSID",
            how="left"
        )
        logger.info(f"  - Joined with administering providers: {df.filter(pl.col('administering_provider_name').is_not_null()).height} have provider names")

        # ==================================================================
        # Step 8: Join with Sta3n lookup
        # ==================================================================
        logger.info("Step 8: Joining with Sta3n lookup...")

        df = df.join(
            sta3n_lookup.select([
                pl.col("Sta3n"),
                pl.col("Sta3nName").str.strip_chars().alias("station_name"),
            ]),
            left_on="sta3n",
            right_on="Sta3n",
            how="left"
        )
        logger.info(f"  - Joined with stations: {df.filter(pl.col('station_name').is_not_null()).height} have station names")

        # ==================================================================
        # Step 9: Combine provider names (use administering if available, else ordering)
        # ==================================================================
        logger.info("Step 9: Combining provider names...")

        df = df.with_columns([
            pl.when(pl.col("administering_provider_name").is_not_null())
            .then(pl.col("administering_provider_name"))
            .otherwise(pl.col("ordering_provider_name"))
            .alias("provider_name")
        ])

        # ==================================================================
        # Step 10: Sort by patient_key, administered_datetime DESC (most recent first)
        # ==================================================================
        logger.info("Step 10: Sorting immunizations...")

        df = df.sort(
            ["patient_key", "administered_datetime"],
            descending=[False, True]
        )
        logger.info(f"  - Sorted {len(df)} immunizations by patient and date")

        # ==================================================================
        # Step 11: Select final Gold schema
        # ==================================================================
        logger.info("Step 11: Mapping to Gold schema...")

        df_gold = df.select([
            pl.col("immunization_sid"),
            pl.col("patient_key"),
            pl.col("cvx_code"),
            pl.col("vaccine_name_standardized").alias("vaccine_name"),
            pl.col("vaccine_name_local"),
            pl.col("administered_datetime"),
            pl.col("series_original").alias("series"),
            pl.col("dose_number"),
            pl.col("total_doses"),
            pl.col("is_series_complete"),
            pl.col("adverse_reaction"),
            pl.col("has_adverse_reaction"),
            pl.col("site_of_administration"),
            pl.col("route"),
            pl.col("dose"),
            pl.col("provider_name"),
            pl.col("location_sid"),
            pl.col("location_name"),
            pl.col("location_type"),
            pl.col("station_name"),
            pl.col("sta3n"),
            pl.col("comments"),
            pl.col("source_system"),
            pl.col("is_annual_vaccine"),
            pl.col("is_covid_vaccine"),
            pl.col("last_updated"),
        ])

        logger.info(f"  - Final Gold schema: {len(df_gold.columns)} columns, {len(df_gold)} records")

        # ==================================================================
        # Step 12: Write to Gold layer in MinIO
        # ==================================================================
        logger.info("Step 12: Writing to Gold layer...")

        gold_path = build_gold_path("immunizations", "patient_immunizations_final.parquet")
        minio_client.write_parquet(df_gold, gold_path)

        logger.info("=" * 70)
        logger.info("✓ Gold transformation complete for Immunizations")
        logger.info("=" * 70)
        logger.info(f"Summary:")
        logger.info(f"  - Total immunizations: {len(df_gold)}")
        logger.info(f"  - Patients: {df_gold.select('patient_key').n_unique()}")
        logger.info(f"  - Output: s3://med-z1/{gold_path}")
        logger.info(f"  - Date range: {df_gold.select('administered_datetime').min().item()} to {df_gold.select('administered_datetime').max().item()}")

        # Show sample distribution
        patient_counts = df_gold.group_by("patient_key").agg(
            pl.len().alias("ImmunizationCount")
        ).sort("ImmunizationCount", descending=True)

        logger.info(f"  - Patient distribution:")
        for row in patient_counts.head(10).iter_rows(named=True):
            logger.info(f"    {row['patient_key']}: {row['ImmunizationCount']} immunizations")

        # Show series completion stats
        logger.info(f"  - Series completion:")
        logger.info(f"    Complete: {df_gold.filter(pl.col('is_series_complete') == True).height}")
        logger.info(f"    Incomplete: {df_gold.filter(pl.col('is_series_complete') == False).height}")
        logger.info(f"    Unknown: {df_gold.filter(pl.col('is_series_complete').is_null()).height}")

        # Show vaccine type stats
        logger.info(f"  - Vaccine types:")
        logger.info(f"    Annual (Influenza): {df_gold.filter(pl.col('is_annual_vaccine') == True).height}")
        logger.info(f"    COVID-19: {df_gold.filter(pl.col('is_covid_vaccine') == True).height}")
        logger.info(f"    Adverse reactions: {df_gold.filter(pl.col('has_adverse_reaction') == True).height}")

    except Exception as e:
        logger.error(f"✗ Gold transformation failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    create_gold_immunizations()
