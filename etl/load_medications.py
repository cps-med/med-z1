# ---------------------------------------------------------------------
# load_medications.py
# ---------------------------------------------------------------------
# Load Gold medications data into PostgreSQL serving database
#  - Read Gold: medications_rxout_final.parquet, medications_bcma_final.parquet
#  - Transform to match PostgreSQL schema
#  - Load into patient_medications_outpatient and patient_medications_inpatient tables
#  - Use truncate/reload strategy
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_medications
# ---------------------------------------------------------------------

import polars as pl
import logging
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_medications_outpatient_to_postgresql():
    """Load Gold RxOut (outpatient) data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("Starting PostgreSQL load for outpatient medications")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Gold RxOut
    # ==================================================================
    logger.info("Step 1: Loading Gold RxOut...")

    gold_path = build_gold_path("medications", "medications_rxout_final.parquet")
    df = minio_client.read_parquet(gold_path)
    logger.info(f"  - Loaded {len(df)} prescriptions from Gold layer")

    # ==================================================================
    # Step 2: Transform to match PostgreSQL schema
    # ==================================================================
    logger.info("Step 2: Transforming to match PostgreSQL schema...")

    # Select and rename columns to match patient_medications_outpatient table schema
    df_pg = df.select([
        # Patient identity
        pl.col("patient_icn"),
        pl.col("patient_key"),

        # Prescription IDs
        pl.col("rx_outpat_id"),
        pl.col("prescription_number"),
        pl.col("local_drug_id"),
        pl.col("national_drug_id"),

        # Drug names
        pl.col("drug_name_local_with_dose").alias("drug_name_local"),
        pl.col("drug_name_national"),
        pl.col("national_generic_name").alias("generic_name"),
        pl.col("trade_name"),

        # Drug details
        pl.col("drug_strength"),
        pl.col("drug_unit"),
        pl.col("dosage_form"),
        pl.col("drug_class"),
        pl.col("drug_class_code"),
        pl.col("dea_schedule"),
        pl.col("ndc_code"),

        # Prescription info
        pl.col("issue_datetime").alias("issue_date"),
        pl.col("rx_status_original").alias("rx_status"),
        pl.col("rx_status_computed"),
        pl.col("rx_type"),

        # Quantity and refills
        pl.col("quantity_ordered"),
        pl.col("days_supply_ordered").alias("days_supply"),
        pl.col("refills_allowed"),
        pl.col("refills_remaining"),
        pl.col("unit_dose"),

        # Latest fill info
        pl.col("latest_fill_number"),
        pl.col("latest_fill_datetime").alias("latest_fill_date"),
        pl.col("latest_fill_status"),
        pl.col("latest_quantity_dispensed"),
        pl.col("latest_days_supply_dispensed").alias("latest_days_supply"),

        # Dates
        pl.col("expiration_datetime").alias("expiration_date"),
        pl.col("discontinued_datetime").alias("discontinued_date"),
        pl.col("discontinue_reason"),

        # Computed flags
        pl.col("is_controlled_substance"),
        pl.col("is_active"),
        pl.col("days_until_expiration"),

        # Providers and locations
        pl.col("provider_name"),
        pl.col("ordering_provider_name"),
        pl.col("pharmacy_name"),
        pl.col("clinic_name"),
        pl.col("facility_name"),
        pl.col("sta3n"),

        # Other flags
        pl.col("cmop_indicator"),
        pl.col("mail_indicator"),

        # Metadata
        pl.col("source_system"),
    ])

    logger.info(f"  - Prepared {len(df_pg)} prescriptions for PostgreSQL")

    # ==================================================================
    # Step 3: Create PostgreSQL connection
    # ==================================================================
    logger.info("Step 3: Connecting to PostgreSQL...")

    # Create SQLAlchemy connection string
    conn_str = (
        f"postgresql://{POSTGRES_CONFIG['user']}:"
        f"{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:"
        f"{POSTGRES_CONFIG['port']}/"
        f"{POSTGRES_CONFIG['database']}"
    )

    engine = create_engine(conn_str)

    # ==================================================================
    # Step 4: Truncate existing data
    # ==================================================================
    logger.info("Step 4: Truncating existing patient_medications_outpatient table...")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE clinical.patient_medications_outpatient;"))
        conn.commit()

    logger.info("  - Table truncated")

    # ==================================================================
    # Step 5: Load data into PostgreSQL
    # ==================================================================
    logger.info("Step 5: Loading data into PostgreSQL...")

    # Convert Polars DataFrame to Pandas for SQLAlchemy compatibility
    df_pandas = df_pg.to_pandas()

    # Write to PostgreSQL
    df_pandas.to_sql(
        "patient_medications_outpatient",
        engine,
        schema="clinical",
        if_exists="append",
        index=False,
        method="multi",  # Bulk insert for performance
        chunksize=1000
    )

    logger.info(f"  - Loaded {len(df_pandas)} prescriptions into patient_medications_outpatient table")

    # ==================================================================
    # Step 6: Verify data
    # ==================================================================
    logger.info("Step 6: Verifying data...")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_medications_outpatient;"))
        count = result.scalar()
        logger.info(f"  - Verified: {count} rows in patient_medications_outpatient table")

        # Get sample data
        result = conn.execute(text("""
            SELECT patient_icn, drug_name_local, rx_status_computed,
                   is_controlled_substance, issue_date
            FROM clinical.patient_medications_outpatient
            ORDER BY issue_date DESC
            LIMIT 5;
        """))
        logger.info("  - Sample records:")
        for row in result:
            logger.info(f"    {row}")

    logger.info("=" * 70)
    logger.info(f"PostgreSQL load complete: {count} outpatient prescriptions loaded")
    logger.info("=" * 70)

    return count


def load_medications_inpatient_to_postgresql():
    """Load Gold BCMA (inpatient) data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("Starting PostgreSQL load for inpatient medications")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Gold BCMA
    # ==================================================================
    logger.info("Step 1: Loading Gold BCMA...")

    gold_path = build_gold_path("medications", "medications_bcma_final.parquet")
    df = minio_client.read_parquet(gold_path)
    logger.info(f"  - Loaded {len(df)} administration events from Gold layer")

    # ==================================================================
    # Step 2: Transform to match PostgreSQL schema
    # ==================================================================
    logger.info("Step 2: Transforming to match PostgreSQL schema...")

    # Select and rename columns to match patient_medications_inpatient table schema
    df_pg = df.select([
        # Patient identity
        pl.col("patient_icn"),
        pl.col("patient_key"),

        # Administration IDs
        pl.col("bcma_medication_log_id").alias("bcma_log_id"),
        pl.col("inpatient_sid"),
        pl.col("order_number"),
        pl.col("local_drug_id"),
        pl.col("national_drug_id"),

        # Drug names
        pl.col("drug_name_local_with_dose").alias("drug_name_local"),
        pl.col("drug_name_national"),
        pl.col("national_generic_name").alias("generic_name"),
        pl.col("trade_name"),

        # Drug details
        pl.col("drug_strength"),
        pl.col("drug_unit"),
        pl.col("dosage_form"),
        pl.col("drug_class"),
        pl.col("drug_class_code"),
        pl.col("dea_schedule"),
        pl.col("ndc_code"),

        # Administration info
        pl.col("action_type"),
        pl.col("action_status"),
        pl.col("action_datetime"),
        pl.col("scheduled_datetime"),
        pl.col("ordered_datetime"),

        # Dosage and route
        pl.col("dosage_ordered"),
        pl.col("dosage_given"),
        pl.col("route"),
        pl.col("unit_of_administration"),
        pl.col("schedule_type"),
        pl.col("schedule"),

        # Variance info
        pl.col("administration_variance"),
        pl.col("variance_type"),
        pl.col("variance_reason"),

        # IV info
        pl.col("is_iv_medication"),
        pl.col("iv_type"),
        pl.col("infusion_rate"),

        # Computed flags
        pl.col("is_controlled_substance"),

        # Staff and locations
        pl.col("administered_by_name").alias("administered_by"),
        pl.col("ordering_provider_name").alias("ordering_provider"),
        pl.col("ward_name"),
        pl.col("facility_name"),
        pl.col("sta3n"),

        # Metadata
        pl.col("source_system"),
    ])

    logger.info(f"  - Prepared {len(df_pg)} administration events for PostgreSQL")

    # ==================================================================
    # Step 3: Create PostgreSQL connection
    # ==================================================================
    logger.info("Step 3: Connecting to PostgreSQL...")

    # Create SQLAlchemy connection string
    conn_str = (
        f"postgresql://{POSTGRES_CONFIG['user']}:"
        f"{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:"
        f"{POSTGRES_CONFIG['port']}/"
        f"{POSTGRES_CONFIG['database']}"
    )

    engine = create_engine(conn_str)

    # ==================================================================
    # Step 4: Truncate existing data
    # ==================================================================
    logger.info("Step 4: Truncating existing patient_medications_inpatient table...")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE clinical.patient_medications_inpatient;"))
        conn.commit()

    logger.info("  - Table truncated")

    # ==================================================================
    # Step 5: Load data into PostgreSQL
    # ==================================================================
    logger.info("Step 5: Loading data into PostgreSQL...")

    # Convert Polars DataFrame to Pandas for SQLAlchemy compatibility
    df_pandas = df_pg.to_pandas()

    # Write to PostgreSQL
    df_pandas.to_sql(
        "patient_medications_inpatient",
        engine,
        schema="clinical",
        if_exists="append",
        index=False,
        method="multi",  # Bulk insert for performance
        chunksize=1000
    )

    logger.info(f"  - Loaded {len(df_pandas)} administration events into patient_medications_inpatient table")

    # ==================================================================
    # Step 6: Verify data
    # ==================================================================
    logger.info("Step 6: Verifying data...")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_medications_inpatient;"))
        count = result.scalar()
        logger.info(f"  - Verified: {count} rows in patient_medications_inpatient table")

        # Get sample data
        result = conn.execute(text("""
            SELECT patient_icn, drug_name_local, action_type,
                   is_controlled_substance, action_datetime
            FROM clinical.patient_medications_inpatient
            ORDER BY action_datetime DESC
            LIMIT 5;
        """))
        logger.info("  - Sample records:")
        for row in result:
            logger.info(f"    {row}")

    logger.info("=" * 70)
    logger.info(f"PostgreSQL load complete: {count} inpatient administrations loaded")
    logger.info("=" * 70)

    return count


def load_all_medications_to_postgresql():
    """Load all medications data from Gold to PostgreSQL."""
    logger.info("=" * 70)
    logger.info("Starting PostgreSQL load for all Medications")
    logger.info("=" * 70)

    # Load outpatient medications
    outpatient_count = load_medications_outpatient_to_postgresql()

    # Load inpatient medications
    inpatient_count = load_medications_inpatient_to_postgresql()

    logger.info("=" * 70)
    logger.info("PostgreSQL load complete for all Medications")
    logger.info(f"  - Outpatient prescriptions: {outpatient_count}")
    logger.info(f"  - Inpatient administrations: {inpatient_count}")
    logger.info(f"  - Total: {outpatient_count + inpatient_count}")
    logger.info("=" * 70)

    return {
        "outpatient": outpatient_count,
        "inpatient": inpatient_count
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_all_medications_to_postgresql()
