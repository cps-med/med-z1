# ---------------------------------------------------------------------
# gold_labs.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver labs data
#  - Read Silver: lab_chem.parquet and lab_test_dim.parquet
#  - Add patient identity lookup (PatientSID → PatientICN → PatientKey)
#  - Enrich with facility/location information
#  - Add derived fields (IsAbnormal, IsCritical, DaysSinceCollection)
#  - Create patient-centric denormalized view
#  - Save to med-z1/gold/labs as labs_final.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.gold_labs
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


def transform_labs_gold():
    """Transform Silver labs data to Gold layer in MinIO."""

    logger.info("=" * 70)
    logger.info("Starting Gold labs transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver Parquet files
    # ==================================================================
    logger.info("Step 1: Loading Silver Parquet files...")

    # Read lab results
    lab_chem_path = build_silver_path("lab_chem", "lab_chem.parquet")
    df = minio_client.read_parquet(lab_chem_path)
    logger.info(f"  - Loaded {len(df)} lab results from Silver layer")

    # Read lab test definitions (for reference, but already joined in Silver)
    lab_test_path = build_silver_path("lab_test_dim", "lab_test_dim.parquet")
    df_lab_test = minio_client.read_parquet(lab_test_path)
    logger.info(f"  - Loaded {len(df_lab_test)} lab test definitions from Silver layer")

    # ==================================================================
    # Step 2: Load patient identity lookup
    # ==================================================================
    logger.info("Step 2: Loading patient identity lookup...")

    patient_lookup = load_patient_icn_lookup()

    # Join to get PatientICN (should already be in Silver, but verify)
    if "PatientICN" not in df.columns or df.filter(pl.col("PatientICN").is_null()).height > 0:
        logger.warning("PatientICN missing or NULL for some records - adding from lookup")
        df = df.join(
            patient_lookup.select([
                pl.col("PatientSID"),
                pl.col("PatientICN").alias("PatientICN_lookup")
            ]),
            on="PatientSID",
            how="left"
        )

        # Use lookup value if original is NULL
        df = df.with_columns([
            pl.when(pl.col("PatientICN").is_null())
                .then(pl.col("PatientICN_lookup"))
                .otherwise(pl.col("PatientICN"))
                .alias("PatientICN")
        ]).drop("PatientICN_lookup")

    # Create PatientKey (same as ICN for Phase 1)
    df = df.with_columns([
        pl.col("PatientICN").alias("patient_key")
    ])

    logger.info(f"  - Patient identity resolution complete")

    # ==================================================================
    # Step 3: Load facility lookup
    # ==================================================================
    logger.info("Step 3: Loading facility lookup...")

    sta3n_lookup = load_sta3n_lookup()

    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n").cast(pl.Int32),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # ==================================================================
    # Step 4: Standardize column names and add derived fields
    # ==================================================================
    logger.info("Step 4: Standardizing column names and adding derived fields...")

    df = df.with_columns([
        # Primary IDs
        pl.col("LabChemSID").alias("lab_chem_sid"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("patient_key").alias("patient_key"),
        pl.col("PatientICN").alias("patient_icn"),

        # Test identifiers
        pl.col("LabTestSID").alias("lab_test_sid"),
        pl.col("LabTestName").alias("lab_test_name"),
        pl.col("LabTestCode").alias("lab_test_code"),
        pl.col("LoincCode").alias("loinc_code"),
        pl.col("PanelName").alias("panel_name"),

        # Order info
        pl.col("LabOrderSID").alias("lab_order_sid"),
        pl.col("AccessionNumber").alias("accession_number"),

        # Results
        pl.col("Result").alias("result_value"),
        pl.col("ResultNumericParsed").alias("result_numeric"),
        pl.col("ResultUnit").alias("result_unit"),

        # Abnormal flags
        pl.col("AbnormalFlagStd").alias("abnormal_flag"),
        pl.col("IsAbnormal").alias("is_abnormal"),
        pl.col("IsCritical").alias("is_critical"),

        # Reference ranges
        pl.col("RefRange").alias("ref_range_text"),
        pl.col("RefRangeLowNumeric").alias("ref_range_low"),
        pl.col("RefRangeHighNumeric").alias("ref_range_high"),

        # Date/time
        pl.col("CollectionDateTime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias("collection_datetime"),
        pl.col("ResultDateTime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias("result_datetime"),
        pl.col("DaysSinceCollection").alias("days_since_collection"),

        # Location info
        pl.col("LocationSID").alias("location_id"),
        pl.col("CollectionLocation").alias("collection_location"),
        pl.col("CollectionLocationType").alias("collection_location_type"),

        # Facility/station
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Provider/lab info
        pl.col("PerformingLabSID").alias("performing_lab_sid"),
        pl.col("OrderingProviderSID").alias("ordering_provider_sid"),

        # Specimen
        pl.col("SpecimenType").alias("specimen_type"),

        # Metadata
        pl.col("VistaPackage").alias("vista_package"),
        pl.lit("CDWWork").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 5: Select final columns for Gold layer
    # ==================================================================
    logger.info("Step 5: Selecting final columns for Gold layer...")

    df = df.select([
        # Primary identifiers
        "lab_chem_sid",
        "patient_sid",
        "patient_icn",
        "patient_key",

        # Test identifiers
        "lab_test_sid",
        "lab_test_name",
        "lab_test_code",
        "loinc_code",
        "panel_name",

        # Order information
        "lab_order_sid",
        "accession_number",

        # Results
        "result_value",
        "result_numeric",
        "result_unit",

        # Abnormal flags
        "abnormal_flag",
        "is_abnormal",
        "is_critical",

        # Reference ranges
        "ref_range_text",
        "ref_range_low",
        "ref_range_high",

        # Date/time
        "collection_datetime",
        "result_datetime",
        "days_since_collection",

        # Location
        "location_id",
        "collection_location",
        "collection_location_type",

        # Facility
        "sta3n",
        "facility_name",

        # Provider/lab
        "performing_lab_sid",
        "ordering_provider_sid",

        # Specimen
        "specimen_type",

        # Metadata
        "vista_package",
        "source_system",
        "last_updated",
    ])

    logger.info(f"  - Selected {len(df.columns)} columns for Gold layer")

    # ==================================================================
    # Step 6: Write to Gold layer
    # ==================================================================
    logger.info("Step 6: Writing to Gold layer...")

    gold_path = build_gold_path("labs", "labs_final.parquet")
    minio_client.write_parquet(df, gold_path)

    logger.info("=" * 70)
    logger.info(f"Gold transformation complete: {len(df)} lab results written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{gold_path}")
    logger.info("=" * 70)

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_labs_gold()
