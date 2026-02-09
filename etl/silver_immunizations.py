# ---------------------------------------------------------------------
# silver_immunizations.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze immunizations data
#  - Read Bronze from both CDWWork (VistA) and CDWWork2 (Oracle Health/Cerner)
#  - Clean and validate data
#  - Resolve lookups: CVX codes, vaccine names, Sta3n (facility names)
#  - Resolve PatientICN for CDWWork (to enable merging with CDWWork2)
#  - Harmonize schemas between CDWWork and CDWWork2
#  - Parse series information (dose X of Y → dose_number, total_doses, is_complete)
#  - Standardize anatomical sites and routes
#  - Add derived flags (has_adverse_reaction, is_annual_vaccine, is_covid_vaccine)
#  - Deduplicate across sources (same patient + CVX + date → keep most recent)
#  - Save to med-z1/silver/immunizations as immunization_harmonized.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_immunizations
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
import re
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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


def parse_series_info(series_str: str) -> dict:
    """
    Parse series string to extract dose_number, total_doses, is_complete.

    Examples:
        "1 of 2" → {dose_number: 1, total_doses: 2, is_complete: False}
        "2 of 2" → {dose_number: 2, total_doses: 2, is_complete: True}
        "BOOSTER" → {dose_number: None, total_doses: None, is_complete: None}
        "COMPLETE" → {dose_number: None, total_doses: None, is_complete: True}
        "1" → {dose_number: 1, total_doses: 1, is_complete: True}
    """
    if not series_str or series_str.strip() == "":
        return {"dose_number": None, "total_doses": None, "is_complete": None}

    series_str = series_str.strip().upper()

    # Pattern: "1 of 2", "2 of 3", etc.
    match = re.match(r"(\d+)\s+OF\s+(\d+)", series_str)
    if match:
        dose_num = int(match.group(1))
        total = int(match.group(2))
        return {
            "dose_number": dose_num,
            "total_doses": total,
            "is_complete": dose_num >= total
        }

    # Pattern: "COMPLETE"
    if series_str == "COMPLETE":
        return {"dose_number": None, "total_doses": None, "is_complete": True}

    # Pattern: "BOOSTER", "INITIAL", etc. (unknown series)
    if series_str in ["BOOSTER", "INITIAL", "UNKNOWN"]:
        return {"dose_number": None, "total_doses": None, "is_complete": None}

    # Pattern: Single digit (e.g., "1", "2") - assume single-dose or standalone
    if re.match(r"^\d+$", series_str):
        dose_num = int(series_str)
        return {"dose_number": dose_num, "total_doses": dose_num, "is_complete": True}

    # Default: unknown format
    return {"dose_number": None, "total_doses": None, "is_complete": None}


def standardize_anatomical_site(site_str: str) -> str:
    """
    Standardize anatomical site names.

    Examples:
        "L DELTOID" → "Left Deltoid"
        "R DELTOID" → "Right Deltoid"
        "LT ARM" → "Left Arm"
        "RT THIGH" → "Right Thigh"
    """
    if not site_str or site_str.strip() == "":
        return None

    site_str = site_str.strip().upper()

    # Left/Right mappings
    site_str = site_str.replace("L DELTOID", "Left Deltoid")
    site_str = site_str.replace("R DELTOID", "Right Deltoid")
    site_str = site_str.replace("LT DELTOID", "Left Deltoid")
    site_str = site_str.replace("RT DELTOID", "Right Deltoid")
    site_str = site_str.replace("LEFT DELTOID", "Left Deltoid")
    site_str = site_str.replace("RIGHT DELTOID", "Right Deltoid")

    site_str = site_str.replace("L ARM", "Left Arm")
    site_str = site_str.replace("R ARM", "Right Arm")
    site_str = site_str.replace("LT ARM", "Left Arm")
    site_str = site_str.replace("RT ARM", "Right Arm")
    site_str = site_str.replace("LEFT ARM", "Left Arm")
    site_str = site_str.replace("RIGHT ARM", "Right Arm")

    site_str = site_str.replace("L THIGH", "Left Thigh")
    site_str = site_str.replace("R THIGH", "Right Thigh")
    site_str = site_str.replace("LT THIGH", "Left Thigh")
    site_str = site_str.replace("RT THIGH", "Right Thigh")
    site_str = site_str.replace("LEFT THIGH", "Left Thigh")
    site_str = site_str.replace("RIGHT THIGH", "Right Thigh")

    # If no replacement occurred, title case it
    if site_str == site_str.upper():
        site_str = site_str.title()

    return site_str


def transform_cdwwork_immunizations(minio_client, patient_icn_lookup):
    """
    Transform CDWWork (VistA) immunizations from Bronze to common Silver schema.
    Returns a polars DataFrame with harmonized immunizations.
    """
    logger.info("=" * 70)
    logger.info("Transforming CDWWork (VistA) immunizations...")
    logger.info("=" * 70)

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading CDWWork Bronze files...")

    # Read Vaccine dimension
    vaccine_dim_path = build_bronze_path("cdwwork", "vaccine_dim", "vaccine_dim_raw.parquet")
    df_vaccine = minio_client.read_parquet(vaccine_dim_path)
    logger.info(f"  - Loaded {len(df_vaccine)} vaccines from Dim.Vaccine")

    # Read PatientImmunization fact table
    immunization_path = build_bronze_path("cdwwork", "immunization", "patient_immunization_raw.parquet")
    df_immunization = minio_client.read_parquet(immunization_path)
    logger.info(f"  - Loaded {len(df_immunization)} immunization records from PatientImmunization")

    # ==================================================================
    # Step 2: Resolve PatientICN for CDWWork immunizations
    # ==================================================================
    logger.info("Step 2: Resolving PatientICN...")

    df_immunization = df_immunization.join(
        patient_icn_lookup.select([
            pl.col("PatientSID"),
            pl.col("PatientICN").alias("patient_icn")
        ]),
        on="PatientSID",
        how="left"
    )
    logger.info(f"  - Resolved PatientICN for {df_immunization.filter(pl.col('patient_icn').is_not_null()).height} immunizations")

    # ==================================================================
    # Step 3: Join with Vaccine dimension (get CVX code, vaccine name)
    # ==================================================================
    logger.info("Step 3: Joining with Vaccine dimension...")

    df = df_immunization.join(
        df_vaccine.select([
            pl.col("VaccineSID"),
            pl.col("VaccineName").str.strip_chars().alias("vaccine_name_local"),
            pl.col("VaccineShortName").str.strip_chars().alias("vaccine_short_name"),
            pl.col("CVXCode").str.strip_chars().alias("cvx_code"),
        ]),
        on="VaccineSID",
        how="left"
    )
    logger.info(f"  - Joined vaccine names: {len(df)} records")

    # ==================================================================
    # Step 4: Parse series information
    # ==================================================================
    logger.info("Step 4: Parsing series information...")

    # Apply parse_series_info to Series column
    # Extract dose_number, total_doses, is_complete
    df = df.with_columns([
        pl.col("Series").map_elements(
            lambda s: parse_series_info(s)["dose_number"],
            return_dtype=pl.Int32
        ).alias("dose_number"),
        pl.col("Series").map_elements(
            lambda s: parse_series_info(s)["total_doses"],
            return_dtype=pl.Int32
        ).alias("total_doses"),
        pl.col("Series").map_elements(
            lambda s: parse_series_info(s)["is_complete"],
            return_dtype=pl.Boolean
        ).alias("is_series_complete"),
    ])

    logger.info(f"  - Parsed series for {len(df)} records")
    logger.info(f"    - Complete series: {df.filter(pl.col('is_series_complete') == True).height}")
    logger.info(f"    - Incomplete series: {df.filter(pl.col('is_series_complete') == False).height}")
    logger.info(f"    - Unknown series: {df.filter(pl.col('is_series_complete').is_null()).height}")

    # ==================================================================
    # Step 5: Standardize anatomical sites
    # ==================================================================
    logger.info("Step 5: Standardizing anatomical sites...")

    df = df.with_columns([
        pl.col("SiteOfAdministration").map_elements(
            lambda s: standardize_anatomical_site(s) if s else None,
            return_dtype=pl.Utf8
        ).alias("site_of_administration_standardized")
    ])

    # ==================================================================
    # Step 6: Add derived flags
    # ==================================================================
    logger.info("Step 6: Adding derived flags...")

    # Has adverse reaction
    df = df.with_columns([
        (pl.col("Reaction").is_not_null() & (pl.col("Reaction").str.strip_chars() != "")).alias("has_adverse_reaction")
    ])

    # Annual vaccines (Influenza): CVX codes 88, 135, 140, 141, 144, 150, 153, 158, 161, 166, 168, 171, 185, 186, 197, 205
    annual_flu_cvx = ["88", "135", "140", "141", "144", "150", "153", "158", "161", "166", "168", "171", "185", "186", "197", "205"]
    df = df.with_columns([
        pl.col("cvx_code").is_in(annual_flu_cvx).alias("is_annual_vaccine")
    ])

    # COVID vaccines: CVX codes 207, 208, 210, 211, 212, 213, 217, 218, 219, 221, 225, 226, 228, 229, 230, 300, 301, 302, 500, 501, 502, 510, 511
    covid_cvx = ["207", "208", "210", "211", "212", "213", "217", "218", "219", "221", "225", "226", "228", "229", "230", "300", "301", "302", "500", "501", "502", "510", "511"]
    df = df.with_columns([
        pl.col("cvx_code").is_in(covid_cvx).alias("is_covid_vaccine")
    ])

    logger.info(f"  - Has adverse reaction: {df.filter(pl.col('has_adverse_reaction') == True).height}")
    logger.info(f"  - Annual vaccines: {df.filter(pl.col('is_annual_vaccine') == True).height}")
    logger.info(f"  - COVID vaccines: {df.filter(pl.col('is_covid_vaccine') == True).height}")

    # ==================================================================
    # Step 7: Standardize vaccine names (UPPERCASE for consistency)
    # ==================================================================
    logger.info("Step 7: Standardizing vaccine names...")

    df = df.with_columns([
        pl.col("vaccine_name_local").str.to_uppercase().alias("vaccine_name_standardized")
    ])

    # ==================================================================
    # Step 8: Select and rename columns to Silver schema
    # ==================================================================
    logger.info("Step 8: Mapping to Silver schema...")

    df_silver = df.select([
        # Prefix with 'V-' for VistA to ensure global uniqueness across source systems
        pl.concat_str([pl.lit("V-"), pl.col("PatientImmunizationSID").cast(pl.Utf8)]).alias("immunization_sid"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("patient_icn"),
        pl.col("cvx_code"),
        pl.col("vaccine_name_standardized"),
        pl.col("vaccine_name_local"),
        pl.col("AdministeredDateTime").alias("administered_datetime"),
        pl.col("Series").alias("series_original"),
        pl.col("dose_number"),
        pl.col("total_doses"),
        pl.col("is_series_complete"),
        pl.col("Reaction").alias("adverse_reaction"),
        pl.col("has_adverse_reaction"),
        pl.col("site_of_administration_standardized").alias("site_of_administration"),
        pl.col("Route").str.strip_chars().alias("route"),
        pl.col("Dose").str.strip_chars().alias("dose"),
        pl.col("OrderingProviderSID").alias("ordering_provider_sid"),
        pl.col("AdministeringProviderSID").alias("administering_provider_sid"),
        pl.col("LocationSID").alias("location_sid"),
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("Comments").alias("comments"),
        pl.lit("CDWWork").alias("source_system"),
        pl.col("SourceSystem").alias("source_system_original"),
        pl.col("LoadDateTime").alias("extraction_datetime"),
        pl.col("is_annual_vaccine"),
        pl.col("is_covid_vaccine"),
    ])

    logger.info(f"Silver transformation complete (CDWWork): {len(df_silver)} immunization records")
    return df_silver


def transform_cdwwork2_immunizations(minio_client):
    """
    Transform CDWWork2 (Cerner) immunizations from Bronze to common Silver schema.
    Returns a polars DataFrame with harmonized immunizations.
    """
    logger.info("=" * 70)
    logger.info("Transforming CDWWork2 (Cerner) immunizations...")
    logger.info("=" * 70)

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading CDWWork2 Bronze files...")

    # Read VaccineCode dimension
    vaccine_code_path = build_bronze_path("cdwwork2", "immunization_mill", "vaccine_code_raw.parquet")
    df_vaccine_code = minio_client.read_parquet(vaccine_code_path)
    logger.info(f"  - Loaded {len(df_vaccine_code)} vaccine codes from VaccineCode")

    # Read VaccineAdmin fact table
    vaccine_admin_path = build_bronze_path("cdwwork2", "immunization_mill", "vaccine_admin_raw.parquet")
    df_vaccine_admin = minio_client.read_parquet(vaccine_admin_path)
    logger.info(f"  - Loaded {len(df_vaccine_admin)} vaccine administrations from VaccineAdmin")

    # ==================================================================
    # Step 2: Join with VaccineCode dimension (get CVX code)
    # ==================================================================
    logger.info("Step 2: Joining with VaccineCode dimension...")

    df = df_vaccine_admin.join(
        df_vaccine_code.select([
            pl.col("VaccineCodeSID"),
            pl.col("CVXCode").str.strip_chars().alias("cvx_code"),
            pl.col("Display").str.strip_chars().alias("vaccine_name_local"),
        ]),
        on="VaccineCodeSID",
        how="left"
    )
    logger.info(f"  - Joined vaccine codes: {len(df)} records")

    # ==================================================================
    # Step 3: Parse series information (Cerner has separate fields)
    # ==================================================================
    logger.info("Step 3: Parsing series information...")

    # Cerner has SeriesNumber and TotalInSeries as separate fields
    # SeriesNumber can be:
    #   - Numeric: "1", "2", "3" (multi-dose series)
    #   - Text: "ANNUAL 2024", "BOOSTER", "BOOSTER 1", "SINGLE"

    # Combine them into series_original format: "1 of 2" or keep as-is
    df = df.with_columns([
        pl.when(
            pl.col("SeriesNumber").is_not_null() & pl.col("TotalInSeries").is_not_null()
        ).then(
            pl.concat_str([
                pl.col("SeriesNumber"),
                pl.lit(" of "),
                pl.col("TotalInSeries")
            ])
        ).otherwise(pl.col("SeriesNumber")).alias("series_original")
    ])

    # Parse to dose_number, total_doses, is_complete
    # Try to cast SeriesNumber to Int32, but handle failures gracefully
    df = df.with_columns([
        pl.col("SeriesNumber").str.extract(r"^(\d+)$", 1).cast(pl.Int32, strict=False).alias("dose_number"),
        pl.col("TotalInSeries").cast(pl.Int32, strict=False).alias("total_doses"),
    ])

    # Calculate is_series_complete
    df = df.with_columns([
        pl.when(
            pl.col("dose_number").is_not_null() & pl.col("total_doses").is_not_null()
        ).then(
            pl.col("dose_number") >= pl.col("total_doses")
        ).otherwise(None).alias("is_series_complete")
    ])

    logger.info(f"  - Parsed series for {len(df)} records")
    logger.info(f"    - Complete series: {df.filter(pl.col('is_series_complete') == True).height}")
    logger.info(f"    - Incomplete series: {df.filter(pl.col('is_series_complete') == False).height}")
    logger.info(f"    - Unknown series: {df.filter(pl.col('is_series_complete').is_null()).height}")

    # ==================================================================
    # Step 4: Standardize anatomical sites
    # ==================================================================
    logger.info("Step 4: Standardizing anatomical sites...")

    df = df.with_columns([
        pl.col("BodySite").map_elements(
            lambda s: standardize_anatomical_site(s) if s else None,
            return_dtype=pl.Utf8
        ).alias("site_of_administration_standardized")
    ])

    # ==================================================================
    # Step 5: Add derived flags
    # ==================================================================
    logger.info("Step 5: Adding derived flags...")

    # Has adverse reaction
    df = df.with_columns([
        (pl.col("AdverseReaction").is_not_null() & (pl.col("AdverseReaction").str.strip_chars() != "")).alias("has_adverse_reaction")
    ])

    # Annual vaccines (Influenza)
    annual_flu_cvx = ["88", "135", "140", "141", "144", "150", "153", "158", "161", "166", "168", "171", "185", "186", "197", "205"]
    df = df.with_columns([
        pl.col("cvx_code").is_in(annual_flu_cvx).alias("is_annual_vaccine")
    ])

    # COVID vaccines
    covid_cvx = ["207", "208", "210", "211", "212", "213", "217", "218", "219", "221", "225", "226", "228", "229", "230", "300", "301", "302", "500", "501", "502", "510", "511"]
    df = df.with_columns([
        pl.col("cvx_code").is_in(covid_cvx).alias("is_covid_vaccine")
    ])

    logger.info(f"  - Has adverse reaction: {df.filter(pl.col('has_adverse_reaction') == True).height}")
    logger.info(f"  - Annual vaccines: {df.filter(pl.col('is_annual_vaccine') == True).height}")
    logger.info(f"  - COVID vaccines: {df.filter(pl.col('is_covid_vaccine') == True).height}")

    # ==================================================================
    # Step 6: Standardize vaccine names (UPPERCASE for consistency)
    # ==================================================================
    logger.info("Step 6: Standardizing vaccine names...")

    df = df.with_columns([
        pl.col("vaccine_name_local").str.to_uppercase().alias("vaccine_name_standardized")
    ])

    # ==================================================================
    # Step 7: Combine dose amount and unit (Cerner stores separately)
    # ==================================================================
    logger.info("Step 7: Combining dose amount and unit...")

    df = df.with_columns([
        pl.when(
            pl.col("DoseAmount").is_not_null() & pl.col("DoseUnit").is_not_null()
        ).then(
            pl.concat_str([
                pl.col("DoseAmount"),
                pl.lit(" "),
                pl.col("DoseUnit")
            ])
        ).otherwise(pl.col("DoseAmount")).alias("dose_combined")
    ])

    # ==================================================================
    # Step 8: Select and rename columns to Silver schema
    # ==================================================================
    logger.info("Step 8: Mapping to Silver schema...")

    df_silver = df.select([
        # Prefix with 'C-' for Cerner to ensure global uniqueness across source systems
        pl.concat_str([pl.lit("C-"), pl.col("VaccineAdminSID").cast(pl.Utf8)]).alias("immunization_sid"),
        pl.col("PersonSID").alias("patient_sid"),
        pl.col("PatientICN").alias("patient_icn"),
        pl.col("cvx_code"),
        pl.col("vaccine_name_standardized"),
        pl.col("vaccine_name_local"),
        pl.col("AdministeredDateTime").alias("administered_datetime"),
        pl.col("series_original"),
        pl.col("dose_number"),
        pl.col("total_doses"),
        pl.col("is_series_complete"),
        pl.col("AdverseReaction").alias("adverse_reaction"),
        pl.col("has_adverse_reaction"),
        pl.col("site_of_administration_standardized").alias("site_of_administration"),
        pl.col("RouteCode").str.strip_chars().alias("route"),
        pl.col("dose_combined").alias("dose"),
        pl.col("ProviderSID").alias("ordering_provider_sid"),
        pl.lit(None, dtype=pl.Int64).alias("administering_provider_sid"),  # Cerner doesn't have this
        pl.col("FacilitySID").alias("location_sid"),
        pl.lit(None, dtype=pl.Utf8).alias("sta3n"),  # Cerner doesn't use Sta3n
        pl.lit(None, dtype=pl.Utf8).alias("comments"),  # Cerner doesn't have comments in mock data
        pl.lit("CDWWork2").alias("source_system"),
        pl.col("SourceSystem").alias("source_system_original"),
        pl.col("LoadDateTime").alias("extraction_datetime"),
        pl.col("is_annual_vaccine"),
        pl.col("is_covid_vaccine"),
    ])

    logger.info(f"Silver transformation complete (CDWWork2): {len(df_silver)} immunization records")
    return df_silver


def merge_and_deduplicate(df_cdwwork, df_cdwwork2):
    """
    Merge CDWWork and CDWWork2 immunizations and deduplicate.
    Deduplication rule: Same patient_icn + cvx_code + administered_datetime (within 1 hour) → keep CDWWork2 (most recent).
    """
    logger.info("=" * 70)
    logger.info("Merging and deduplicating CDWWork and CDWWork2 immunizations...")
    logger.info("=" * 70)

    # ==================================================================
    # Step 1: Concatenate both DataFrames
    # ==================================================================
    logger.info("Step 1: Concatenating CDWWork and CDWWork2...")

    df_merged = pl.concat([df_cdwwork, df_cdwwork2], how="vertical")
    logger.info(f"  - Total records before deduplication: {len(df_merged)}")

    # ==================================================================
    # Step 2: Create deduplication key
    # ==================================================================
    logger.info("Step 2: Creating deduplication key...")

    # Key: patient_icn + cvx_code + administered_date (date only, not time)
    df_merged = df_merged.with_columns([
        pl.col("administered_datetime").cast(pl.Date).alias("administered_date"),
        pl.concat_str([
            pl.col("patient_icn"),
            pl.lit("_"),
            pl.col("cvx_code"),
            pl.lit("_"),
            pl.col("administered_datetime").cast(pl.Date).cast(pl.Utf8)
        ]).alias("dedup_key")
    ])

    # ==================================================================
    # Step 3: Deduplicate - keep CDWWork2 when duplicates exist
    # ==================================================================
    logger.info("Step 3: Deduplicating (prioritizing CDWWork2)...")

    # Sort by dedup_key, then by source_system (CDWWork2 before CDWWork alphabetically)
    # Then take first record per dedup_key
    df_deduped = (
        df_merged
        .sort(["dedup_key", "source_system"], descending=[False, True])  # CDWWork2 > CDWWork
        .unique(subset=["dedup_key"], keep="first")
    )

    logger.info(f"  - Records after deduplication: {len(df_deduped)}")
    logger.info(f"  - Duplicates removed: {len(df_merged) - len(df_deduped)}")

    # ==================================================================
    # Step 4: Drop temporary columns
    # ==================================================================
    df_deduped = df_deduped.drop(["administered_date", "dedup_key"])

    # ==================================================================
    # Step 5: Sort by patient_icn, administered_datetime DESC
    # ==================================================================
    logger.info("Step 4: Sorting by patient and date...")

    df_deduped = df_deduped.sort(["patient_icn", "administered_datetime"], descending=[False, True])

    # ==================================================================
    # Step 6: Add last_updated timestamp
    # ==================================================================
    df_deduped = df_deduped.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("last_updated")
    ])

    return df_deduped


def main():
    """Run Silver transformation for Immunizations."""
    logger.info("=" * 70)
    logger.info("SILVER ETL: Immunizations")
    logger.info("=" * 70)

    try:
        minio_client = MinIOClient()

        # Load lookup tables
        sta3n_lookup = load_sta3n_lookup()
        patient_icn_lookup = load_patient_icn_lookup()

        # Transform CDWWork (VistA) immunizations
        df_cdwwork = transform_cdwwork_immunizations(minio_client, patient_icn_lookup)

        # Transform CDWWork2 (Cerner) immunizations
        df_cdwwork2 = transform_cdwwork2_immunizations(minio_client)

        # Merge and deduplicate
        df_silver = merge_and_deduplicate(df_cdwwork, df_cdwwork2)

        # Write to Silver layer
        silver_path = build_silver_path("immunizations", "immunization_harmonized.parquet")
        minio_client.write_parquet(df_silver, silver_path)

        logger.info("=" * 70)
        logger.info("✓ Silver transformation complete for Immunizations")
        logger.info("=" * 70)
        logger.info(f"Summary:")
        logger.info(f"  - CDWWork records: {len(df_cdwwork)}")
        logger.info(f"  - CDWWork2 records: {len(df_cdwwork2)}")
        logger.info(f"  - Total after merge: {len(df_silver)}")
        logger.info(f"  - Output: s3://med-z1/{silver_path}")
        logger.info(f"  - Patients: {df_silver.select('patient_icn').n_unique()}")
        logger.info(f"  - Date range: {df_silver.select('administered_datetime').min().item()} to {df_silver.select('administered_datetime').max().item()}")

        # Show sample distribution
        patient_counts = df_silver.group_by("patient_icn").agg(
            pl.len().alias("ImmunizationCount")
        ).sort("ImmunizationCount", descending=True)

        logger.info(f"  - Patient distribution (top 10):")
        for row in patient_counts.head(10).iter_rows(named=True):
            logger.info(f"    {row['patient_icn']}: {row['ImmunizationCount']} immunizations")

    except Exception as e:
        logger.error(f"✗ Silver transformation failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
