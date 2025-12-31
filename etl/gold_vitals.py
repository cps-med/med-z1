# ---------------------------------------------------------------------
# gold_vitals.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver vitals data
#  - Read Silver: vitals_merged.parquet (merged CDWWork + CDWWork2)
#  - Preserve data_source column (CDWWork, CDWWork2, CALCULATED)
#  - Add patient identity lookup (PatientSID → PatientICN for CDWWork)
#  - Calculate BMI from height/weight pairs
#  - Calculate abnormal flags based on reference ranges
#  - Create patient-centric denormalized view
#  - Save to med-z1/gold/vitals as vitals_final.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.gold_vitals
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def load_patient_icn_lookup():
    """
    Load PatientSID to PatientICN lookup from CDWWork.
    Returns a polars DataFrame with PatientSID to PatientICN mapping.
    """
    logger.info("Loading PatientSID to PatientICN lookup from CDWWork")

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
        patient_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(patient_df)} patient ICN mappings")
    return patient_df


def calculate_abnormal_flag(vital_abbr: str, numeric_value: float, systolic: float = None, diastolic: float = None) -> str:
    """
    Calculate abnormal flag based on vital type and value.

    Reference Ranges:
    - BP Systolic: 100-139 (normal), 90-99 (low), 140-179 (high), <90 or ≥180 (critical)
    - BP Diastolic: 70-89 (normal), 60-69 (low), 90-119 (high), <60 or ≥120 (critical)
    - Temperature: 97.0-99.9°F (normal), 95.0-96.9 (low), 100.5-103.0 (high), <95.0 or >103.0 (critical)
    - Pulse: 60-100 (normal), 40-59 (low), 101-130 (high), <40 or >130 (critical)
    - Respiration: 12-20 (normal), 8-11 (low), 21-28 (high), <8 or >28 (critical)
    - Pulse Ox: ≥92% (normal), 88-91 (low), <88 (critical)
    - Pain: 0-3 (normal), 4-7 (high), 8-10 (critical)

    Returns: 'NORMAL', 'LOW', 'HIGH', 'CRITICAL', or None
    """
    if vital_abbr == "BP":
        # Check both systolic and diastolic
        if systolic is None or diastolic is None:
            return None

        # Critical
        if systolic < 90 or systolic >= 180 or diastolic < 60 or diastolic >= 120:
            return "CRITICAL"
        # High
        elif systolic >= 140 or diastolic >= 90:
            return "HIGH"
        # Low
        elif systolic < 100 or diastolic < 70:
            return "LOW"
        # Normal
        else:
            return "NORMAL"

    elif vital_abbr == "T":
        if numeric_value is None:
            return None
        # Assume Fahrenheit (temperature should be in F)
        if numeric_value < 95.0 or numeric_value > 103.0:
            return "CRITICAL"
        elif numeric_value >= 100.5:
            return "HIGH"
        elif numeric_value < 97.0:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "P":
        if numeric_value is None:
            return None
        if numeric_value < 40 or numeric_value > 130:
            return "CRITICAL"
        elif numeric_value > 100:
            return "HIGH"
        elif numeric_value < 60:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "R":
        if numeric_value is None:
            return None
        if numeric_value < 8 or numeric_value > 28:
            return "CRITICAL"
        elif numeric_value > 20:
            return "HIGH"
        elif numeric_value < 12:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "POX":
        if numeric_value is None:
            return None
        if numeric_value < 88:
            return "CRITICAL"
        elif numeric_value < 92:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "PN":
        if numeric_value is None:
            return None
        if numeric_value >= 8:
            return "CRITICAL"
        elif numeric_value >= 4:
            return "HIGH"
        else:
            return "NORMAL"

    elif vital_abbr == "BMI":
        if numeric_value is None:
            return None
        # BMI ranges (CDC/WHO adult guidelines):
        # < 18.5: Underweight (LOW)
        # 18.5-24.9: Normal weight (NORMAL)
        # 25.0-29.9: Overweight (HIGH)
        # 30.0-39.9: Obese (HIGH)
        # ≥ 40.0: Severely obese (CRITICAL)
        if numeric_value >= 40.0:
            return "CRITICAL"
        elif numeric_value >= 25.0:
            return "HIGH"
        elif numeric_value < 18.5:
            return "LOW"
        else:
            return "NORMAL"

    # For HT, WT, BG - no abnormal flags
    else:
        return None


def calculate_bmi_for_patient(vitals_df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate BMI for each patient where both height and weight are available.
    Adds BMI as virtual vital signs to the dataframe.

    BMI = weight(kg) / (height(m))^2

    Note: Uses patient_icn instead of patient_sid for consistency with merged data
    """
    logger.info("Calculating BMI for patients with height and weight data...")

    # Get most recent height per patient (using patient_icn)
    height_df = (
        vitals_df
        .filter(pl.col("vital_abbr") == "HT")
        .sort("taken_datetime", descending=True)
        .group_by("patient_icn")
        .agg([
            pl.col("metric_value").first().cast(pl.Float64).alias("height_cm"),
            pl.col("taken_datetime").first().alias("height_date")
        ])
    )

    # Get weight measurements per patient (using patient_icn)
    weight_df = (
        vitals_df
        .filter(pl.col("vital_abbr") == "WT")
        .select([
            "patient_icn",
            "taken_datetime",
            pl.col("metric_value").cast(pl.Float64).alias("weight_kg")
        ])
    )

    # Join height with weights for same patient
    bmi_df = (
        weight_df
        .join(height_df, on="patient_icn", how="inner")
        .with_columns([
            # Calculate BMI: weight(kg) / (height(m))^2
            # height_cm is in centimeters, need to convert to meters
            (pl.col("weight_kg") / ((pl.col("height_cm") / 100) ** 2)).alias("bmi_value")
        ])
        .select([
            "patient_icn",
            pl.col("taken_datetime").alias("weight_datetime"),
            "bmi_value",
            "height_cm",
            "weight_kg"
        ])
    )

    logger.info(f"Calculated {len(bmi_df)} BMI values")

    return bmi_df


def transform_vitals_gold():
    """Transform Silver vitals data to Gold layer."""

    logger.info("=" * 70)
    logger.info("Starting Gold vitals transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver vitals (merged CDWWork + CDWWork2)
    # ==================================================================
    logger.info("Step 1: Loading Silver vitals...")

    silver_path = build_silver_path("vitals", "vitals_merged.parquet")
    df = minio_client.read_parquet(silver_path)
    logger.info(f"  - Loaded {len(df)} vitals from Silver layer")

    # Check data source distribution
    source_counts = df.group_by("data_source").agg([pl.len().alias("count")])
    logger.info(f"  - Data sources: {source_counts.to_dicts()}")

    # ==================================================================
    # Step 2: Ensure patient_icn is populated for all vitals
    # ==================================================================
    logger.info("Step 2: Ensuring patient_icn is populated...")

    # Patient ICN Resolution Strategy:
    # --------------------------------
    # CDWWork2 (Oracle Health): patient_icn already present from Silver layer
    # CDWWork (VistA): patient_icn may be null, generate from patient_sid if needed
    #
    # For CDWWork, we generate ICN deterministically using the established pattern:
    #   ICN = "ICN" + str(100000 + patient_sid)
    #
    # This correctly resolves to:
    #   patient_sid=1  → ICN100001 (matches patient PatientSID=1001)
    #   patient_sid=2  → ICN100002 (matches patient PatientSID=1002)
    #   ...
    #   patient_sid=36 → ICN100036 (matches patient PatientSID=1036)

    # Check how many need ICN generation
    null_icn_count = df.filter(pl.col("patient_icn").is_null()).height

    if null_icn_count > 0:
        logger.info(f"  - {null_icn_count} vitals need patient_icn generated from patient_sid")
        # Generate ICN where it's null (CDWWork vitals)
        df = df.with_columns([
            pl.when(pl.col("patient_icn").is_null())
                .then(pl.format("ICN{}", (100000 + pl.col("vital_record_id"))))
                .otherwise(pl.col("patient_icn"))
                .alias("patient_icn")
        ])
    else:
        logger.info(f"  - All vitals already have patient_icn (from Silver layer)")

    # Verify all vitals now have ICN
    remaining_null = df.filter(pl.col("patient_icn").is_null()).height
    logger.info(f"  - Vitals with ICN: {len(df) - remaining_null}/{len(df)}")
    if remaining_null > 0:
        logger.warning(f"  - WARNING: {remaining_null} vitals still missing patient_icn")

    # ==================================================================
    # Step 3: Generate vital_abbr for CDWWork2 (Oracle Health) vitals
    # ==================================================================
    logger.info("Step 3: Generating vital_abbr for CDWWork2 vitals...")

    # CDWWork2 doesn't have abbreviations, so generate them from vital_type
    # Use a mapping of common vital types to standard abbreviations
    df = df.with_columns([
        pl.when(pl.col("vital_abbr").is_null())
            .then(
                pl.when(pl.col("vital_type").str.to_uppercase() == "BLOOD PRESSURE")
                    .then(pl.lit("BP"))
                .when(pl.col("vital_type").str.to_uppercase() == "PULSE")
                    .then(pl.lit("P"))
                .when(pl.col("vital_type").str.to_uppercase() == "TEMPERATURE")
                    .then(pl.lit("T"))
                .when(pl.col("vital_type").str.to_uppercase() == "WEIGHT")
                    .then(pl.lit("WT"))
                .when(pl.col("vital_type").str.to_uppercase() == "HEIGHT")
                    .then(pl.lit("HT"))
                .when(pl.col("vital_type").str.to_uppercase() == "RESPIRATION")
                    .then(pl.lit("R"))
                .when(pl.col("vital_type").str.to_uppercase() == "PULSE OXIMETRY")
                    .then(pl.lit("POX"))
                .when(pl.col("vital_type").str.to_uppercase() == "PAIN")
                    .then(pl.lit("PN"))
                .when(pl.col("vital_type").str.to_uppercase() == "BLOOD GLUCOSE")
                    .then(pl.lit("BG"))
                .otherwise(pl.col("vital_type").str.slice(0, 3).str.to_uppercase())  # First 3 letters as fallback
            )
            .otherwise(pl.col("vital_abbr"))
            .alias("vital_abbr")
    ])

    abbr_generated_count = df.filter((pl.col("data_source") == "CDWWork2") & (pl.col("vital_abbr").is_not_null())).height
    logger.info(f"  - Generated abbreviations for {abbr_generated_count} CDWWork2 vitals")

    # ==================================================================
    # Step 4: Calculate abnormal flags
    # ==================================================================
    logger.info("Step 4: Calculating abnormal flags...")

    # Apply abnormal flag calculation using when-then logic
    df = df.with_columns([
        pl.when(pl.col("vital_abbr") == "BP")
            .then(
                pl.when((pl.col("systolic") < 90) | (pl.col("systolic") >= 180) |
                       (pl.col("diastolic") < 60) | (pl.col("diastolic") >= 120))
                    .then(pl.lit("CRITICAL"))
                .when((pl.col("systolic") >= 140) | (pl.col("diastolic") >= 90))
                    .then(pl.lit("HIGH"))
                .when((pl.col("systolic") < 100) | (pl.col("diastolic") < 70))
                    .then(pl.lit("LOW"))
                .otherwise(pl.lit("NORMAL"))
            )
        .when(pl.col("vital_abbr") == "T")
            .then(
                pl.when((pl.col("numeric_value") < 95.0) | (pl.col("numeric_value") > 103.0))
                    .then(pl.lit("CRITICAL"))
                .when(pl.col("numeric_value") >= 100.5)
                    .then(pl.lit("HIGH"))
                .when(pl.col("numeric_value") < 97.0)
                    .then(pl.lit("LOW"))
                .otherwise(pl.lit("NORMAL"))
            )
        .when(pl.col("vital_abbr") == "P")
            .then(
                pl.when((pl.col("numeric_value") < 40) | (pl.col("numeric_value") > 130))
                    .then(pl.lit("CRITICAL"))
                .when(pl.col("numeric_value") > 100)
                    .then(pl.lit("HIGH"))
                .when(pl.col("numeric_value") < 60)
                    .then(pl.lit("LOW"))
                .otherwise(pl.lit("NORMAL"))
            )
        .when(pl.col("vital_abbr") == "R")
            .then(
                pl.when((pl.col("numeric_value") < 8) | (pl.col("numeric_value") > 28))
                    .then(pl.lit("CRITICAL"))
                .when(pl.col("numeric_value") > 20)
                    .then(pl.lit("HIGH"))
                .when(pl.col("numeric_value") < 12)
                    .then(pl.lit("LOW"))
                .otherwise(pl.lit("NORMAL"))
            )
        .when(pl.col("vital_abbr") == "POX")
            .then(
                pl.when(pl.col("numeric_value") < 88)
                    .then(pl.lit("CRITICAL"))
                .when(pl.col("numeric_value") < 92)
                    .then(pl.lit("LOW"))
                .otherwise(pl.lit("NORMAL"))
            )
        .when(pl.col("vital_abbr") == "PN")
            .then(
                pl.when(pl.col("numeric_value") >= 8)
                    .then(pl.lit("CRITICAL"))
                .when(pl.col("numeric_value") >= 4)
                    .then(pl.lit("HIGH"))
                .otherwise(pl.lit("NORMAL"))
            )
        .otherwise(None)
        .alias("abnormal_flag")
    ])

    abnormal_count = df.filter(pl.col("abnormal_flag").is_in(["LOW", "HIGH", "CRITICAL"])).shape[0]
    logger.info(f"  - Calculated abnormal flags: {abnormal_count} abnormal vitals found")

    # ==================================================================
    # Step 5: Calculate BMI
    # ==================================================================
    logger.info("Step 5: Calculating BMI...")

    bmi_df = calculate_bmi_for_patient(df)

    # Create BMI vital sign records
    if len(bmi_df) > 0:
        bmi_vitals = bmi_df.with_columns([
            pl.lit(None).cast(pl.Int64).alias("vital_record_id"),  # No vital_record_id for calculated BMI
            "patient_icn",  # Already present from BMI calculation
            pl.lit("BMI").alias("vital_type"),
            pl.lit("BMI").alias("vital_abbr"),
            pl.col("weight_datetime").alias("taken_datetime"),
            pl.col("weight_datetime").alias("entered_datetime"),
            pl.col("bmi_value").round(1).cast(pl.Utf8).alias("result_value"),
            pl.col("bmi_value").alias("numeric_value"),
            pl.lit(None).cast(pl.Float64).alias("systolic"),
            pl.lit(None).cast(pl.Float64).alias("diastolic"),
            pl.col("bmi_value").alias("metric_value"),  # BMI is unit-less
            pl.lit("kg/m2").alias("unit_of_measure"),
            pl.lit("CALCULATED").alias("category"),
            pl.lit("[]").alias("qualifiers"),
            pl.lit(None).cast(pl.Int64).alias("location_id"),
            pl.lit(None).cast(pl.Utf8).alias("location_name"),
            pl.lit(None).cast(pl.Utf8).alias("location_type"),
            pl.lit(None).cast(pl.Utf8).alias("entered_by"),
            pl.lit(None).cast(pl.Utf8).alias("sta3n"),
            pl.lit(None).cast(pl.Utf8).alias("facility_name"),
            pl.lit("CALCULATED").alias("data_source"),  # BMI is calculated, not from CDWWork or CDWWork2
            pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
            # Compute BMI abnormal flag based on CDC/WHO ranges
            pl.when(pl.col("bmi_value") >= 40.0)
                .then(pl.lit("CRITICAL"))  # Severely obese
            .when(pl.col("bmi_value") >= 25.0)
                .then(pl.lit("HIGH"))  # Overweight/Obese
            .when(pl.col("bmi_value") < 18.5)
                .then(pl.lit("LOW"))  # Underweight
            .otherwise(pl.lit("NORMAL"))  # Normal weight (18.5-24.9)
                .alias("abnormal_flag"),
        ])

        # Append BMI vitals to main dataframe
        # Use diagonal_relaxed to handle schema differences
        df = pl.concat([df, bmi_vitals], how="diagonal_relaxed")
        logger.info(f"  - Added {len(bmi_vitals)} calculated BMI vitals")
    else:
        logger.info("  - No BMI calculations (no patients with both height and weight)")

    # ==================================================================
    # Step 6: Create patient key for consistency
    # ==================================================================
    logger.info("Step 6: Creating patient_key...")

    df = df.with_columns([
        # patient_key is same as patient_icn (already has ICN prefix)
        pl.col("patient_icn").alias("patient_key")
    ])

    # ==================================================================
    # Step 7: Select final columns for Gold layer
    # ==================================================================
    logger.info("Step 7: Selecting final columns...")

    df = df.select([
        "vital_record_id",
        "patient_icn",
        "patient_key",
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
        "abnormal_flag",
        "qualifiers",
        "location_id",
        "location_name",
        "location_type",
        "entered_by",
        "sta3n",
        "facility_name",
        "data_source",  # Track origin: CDWWork, CDWWork2, or CALCULATED
        "last_updated",
    ])

    # ==================================================================
    # Step 8: Write to Gold layer
    # ==================================================================
    logger.info("Step 8: Writing to Gold layer...")

    gold_path = build_gold_path("vitals", "vitals_final.parquet")
    minio_client.write_parquet(df, gold_path)

    logger.info("=" * 70)
    logger.info(f"Gold transformation complete: {len(df)} vitals written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{gold_path}")
    logger.info(f"  - {abnormal_count} abnormal vitals flagged")
    logger.info(f"  - {len(bmi_df) if len(bmi_df) > 0 else 0} BMI calculations added")
    logger.info("=" * 70)

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_vitals_gold()
