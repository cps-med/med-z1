# ---------------------------------------------------------------------
# gold_patient_medications.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver medications data
#  - Read Silver: medications_rxout_cleaned.parquet, medications_bcma_cleaned.parquet
#  - Add patient identity (PatientSID → PatientICN)
#  - Calculate computed fields (is_active, days_until_expiration, etc.)
#  - Create patient-centric denormalized views
#  - Save to med-z1/gold/medications as:
#    - medications_rxout_final.parquet (outpatient)
#    - medications_bcma_final.parquet (inpatient)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.gold_patient_medications
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone, timedelta
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def transform_rxout_gold():
    """Transform Silver RxOut (outpatient) data to Gold layer."""

    logger.info("=" * 70)
    logger.info("Starting Gold RxOut transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver RxOut
    # ==================================================================
    logger.info("Step 1: Loading Silver RxOut...")

    silver_path = build_silver_path("medications", "medications_rxout_cleaned.parquet")
    df = minio_client.read_parquet(silver_path)
    logger.info(f"  - Loaded {len(df)} prescriptions from Silver layer")

    # ==================================================================
    # Step 2: Validate patient ICN from Silver layer
    # ==================================================================
    logger.info("Step 2: Validating patient ICN from Silver layer...")

    # Patient ICN is already resolved in Silver layer via join with SPatient.SPatient
    # Just create patient_key as alias to patient_icn for consistency
    df = df.with_columns([
        pl.col("patient_icn").alias("patient_key"),
    ])

    # Log any prescriptions without ICN
    missing_icn_count = df.filter(pl.col("patient_icn").is_null()).shape[0]
    if missing_icn_count > 0:
        logger.warning(f"  - {missing_icn_count} prescriptions missing PatientICN")
    else:
        logger.info(f"  - All {len(df)} prescriptions have PatientICN")

    # ==================================================================
    # Step 3: Calculate is_active flag
    # ==================================================================
    logger.info("Step 3: Calculating is_active flag...")

    current_date = datetime.now()

    df = df.with_columns([
        # is_active: not discontinued AND not expired
        pl.when(
            (pl.col("discontinued_datetime").is_null()) &
            ((pl.col("expiration_datetime").is_null()) | (pl.col("expiration_datetime") > current_date))
        )
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("is_active")
    ])

    active_count = df.filter(pl.col("is_active") == True).shape[0]
    logger.info(f"  - {active_count} active prescriptions out of {len(df)}")

    # ==================================================================
    # Step 4: Calculate days_until_expiration
    # ==================================================================
    logger.info("Step 4: Calculating days_until_expiration...")

    df = df.with_columns([
        pl.when(
            (pl.col("is_active") == True) & (pl.col("expiration_datetime").is_not_null())
        )
        .then((pl.col("expiration_datetime") - pl.lit(current_date)).dt.total_days().cast(pl.Int32))
        .otherwise(None)
        .alias("days_until_expiration")
    ])

    # ==================================================================
    # Step 5: Calculate is_controlled_substance (already in Silver, but ensure boolean)
    # ==================================================================
    logger.info("Step 5: Ensuring is_controlled_substance is boolean...")

    df = df.with_columns([
        (pl.col("is_controlled_substance") == "Y").alias("is_controlled_substance")
    ])

    controlled_count = df.filter(pl.col("is_controlled_substance") == True).shape[0]
    logger.info(f"  - {controlled_count} controlled substance prescriptions")

    # ==================================================================
    # Step 6: Sort by issue_datetime descending
    # ==================================================================
    logger.info("Step 6: Sorting by issue_datetime...")

    df = df.sort("issue_datetime", descending=True)

    # ==================================================================
    # Step 7: Select final columns for Gold layer
    # ==================================================================
    logger.info("Step 7: Selecting final columns...")

    df = df.select([
        # Patient identity
        "patient_icn",
        "patient_key",
        "patient_sid",

        # Prescription IDs
        "rx_outpat_id",
        "local_drug_id",
        "national_drug_id",
        "prescription_number",

        # Drug names
        "drug_name_local_with_dose",
        "drug_name_local_without_dose",
        "drug_name_national",
        "national_generic_name",
        "trade_name",

        # Drug details
        "drug_strength",
        "drug_unit",
        "dosage_form",
        "drug_class",
        "drug_class_code",
        "dea_schedule",
        "ndc_code",

        # Prescription info
        "issue_datetime",
        "rx_status_original",
        "rx_status_computed",
        "rx_type",

        # Quantity and refills
        "quantity_ordered",
        "days_supply_ordered",
        "refills_allowed",
        "refills_remaining",
        "unit_dose",

        # Latest fill info
        "latest_fill_sid",
        "latest_fill_number",
        "latest_fill_datetime",
        "latest_fill_status",
        "latest_quantity_dispensed",
        "latest_days_supply_dispensed",

        # Sig (medication directions)
        "sig",
        "sig_route",
        "sig_schedule",

        # Dates
        "expiration_datetime",
        "discontinued_datetime",
        "discontinue_reason",

        # Computed flags
        "is_controlled_substance",
        "is_active",
        "days_until_expiration",

        # Providers and locations
        "provider_sid",
        "provider_name",
        "ordering_provider_sid",
        "ordering_provider_name",
        "pharmacy_name",
        "clinic_name",
        "sta3n",
        "facility_name",

        # Other flags
        "cmop_indicator",
        "mail_indicator",

        # Metadata
        "source_system",
        "last_updated",
    ])

    # ==================================================================
    # Step 8: Write to Gold layer
    # ==================================================================
    logger.info("Step 8: Writing to Gold layer...")

    gold_path = build_gold_path("medications", "medications_rxout_final.parquet")
    minio_client.write_parquet(df, gold_path)

    logger.info("=" * 70)
    logger.info(f"Gold RxOut transformation complete: {len(df)} prescriptions written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{gold_path}")
    logger.info(f"  - {active_count} active prescriptions")
    logger.info(f"  - {controlled_count} controlled substance prescriptions")
    logger.info("=" * 70)

    return df


def transform_bcma_gold():
    """Transform Silver BCMA (inpatient) data to Gold layer."""

    logger.info("=" * 70)
    logger.info("Starting Gold BCMA transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver BCMA
    # ==================================================================
    logger.info("Step 1: Loading Silver BCMA...")

    silver_path = build_silver_path("medications", "medications_bcma_cleaned.parquet")
    df = minio_client.read_parquet(silver_path)
    logger.info(f"  - Loaded {len(df)} administration events from Silver layer")

    # ==================================================================
    # Step 2: Validate patient ICN from Silver layer
    # ==================================================================
    logger.info("Step 2: Validating patient ICN from Silver layer...")

    # Patient ICN is already resolved in Silver layer via join with SPatient.SPatient
    # Just create patient_key as alias to patient_icn for consistency
    df = df.with_columns([
        pl.col("patient_icn").alias("patient_key"),
    ])

    # Log any administrations without ICN
    missing_icn_count = df.filter(pl.col("patient_icn").is_null()).shape[0]
    if missing_icn_count > 0:
        logger.warning(f"  - {missing_icn_count} administrations missing PatientICN")
    else:
        logger.info(f"  - All {len(df)} administrations have PatientICN")

    # ==================================================================
    # Step 3: Calculate administration_variance flag (boolean)
    # ==================================================================
    logger.info("Step 3: Calculating administration_variance flag...")

    df = df.with_columns([
        (pl.col("has_variance") == "Y").alias("administration_variance")
    ])

    variance_count = df.filter(pl.col("administration_variance") == True).shape[0]
    logger.info(f"  - {variance_count} administration events with variances")

    # ==================================================================
    # Step 4: Calculate is_iv_medication flag (boolean)
    # ==================================================================
    logger.info("Step 4: Calculating is_iv_medication flag...")

    df = df.with_columns([
        (pl.col("iv_flag") == "Y").alias("is_iv_medication")
    ])

    iv_count = df.filter(pl.col("is_iv_medication") == True).shape[0]
    logger.info(f"  - {iv_count} IV medication administrations")

    # ==================================================================
    # Step 5: Calculate is_controlled_substance (already in Silver, but ensure boolean)
    # ==================================================================
    logger.info("Step 5: Ensuring is_controlled_substance is boolean...")

    df = df.with_columns([
        (pl.col("is_controlled_substance") == "Y").alias("is_controlled_substance")
    ])

    controlled_count = df.filter(pl.col("is_controlled_substance") == True).shape[0]
    logger.info(f"  - {controlled_count} controlled substance administrations")

    # ==================================================================
    # Step 6: Sort by action_datetime descending
    # ==================================================================
    logger.info("Step 6: Sorting by action_datetime...")

    df = df.sort("action_datetime", descending=True)

    # ==================================================================
    # Step 7: Select final columns for Gold layer
    # ==================================================================
    logger.info("Step 7: Selecting final columns...")

    df = df.select([
        # Patient identity
        "patient_icn",
        "patient_key",
        "patient_sid",
        "inpatient_sid",

        # Administration IDs
        "bcma_medication_log_id",
        "local_drug_id",
        "national_drug_id",
        "order_number",

        # Drug names
        "drug_name_local_with_dose",
        "drug_name_local_without_dose",
        "drug_name_national",
        "national_generic_name",
        "trade_name",

        # Drug details
        "drug_strength",
        "drug_unit",
        "dosage_form",
        "drug_class",
        "drug_class_code",
        "dea_schedule",
        "ndc_code",

        # Administration info
        "action_type",
        "action_status",
        "action_datetime",
        "scheduled_datetime",
        "ordered_datetime",

        # Dosage and route
        "dosage_ordered",
        "dosage_given",
        "route",
        "unit_of_administration",
        "schedule_type",
        "schedule",

        # Variance info
        "administration_variance",
        "variance_type",
        "variance_reason",

        # IV info
        "is_iv_medication",
        "iv_type",
        "infusion_rate",

        # Computed flags
        "is_controlled_substance",

        # Staff and locations
        "administered_by_staff_sid",
        "administered_by_name",
        "ordering_provider_sid",
        "ordering_provider_name",
        "ward_name",
        "sta3n",
        "facility_name",

        # Metadata
        "source_system",
        "last_updated",
    ])

    # ==================================================================
    # Step 8: Write to Gold layer
    # ==================================================================
    logger.info("Step 8: Writing to Gold layer...")

    gold_path = build_gold_path("medications", "medications_bcma_final.parquet")
    minio_client.write_parquet(df, gold_path)

    logger.info("=" * 70)
    logger.info(f"Gold BCMA transformation complete: {len(df)} administration events written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{gold_path}")
    logger.info(f"  - {variance_count} administrations with variances")
    logger.info(f"  - {iv_count} IV medication administrations")
    logger.info(f"  - {controlled_count} controlled substance administrations")
    logger.info("=" * 70)

    return df


def transform_all_medications_gold():
    """Transform all medications data from Silver to Gold."""
    logger.info("=" * 70)
    logger.info("Starting Gold transformation for all Medications")
    logger.info("=" * 70)

    # Transform RxOut (outpatient)
    rxout_df = transform_rxout_gold()

    # Transform BCMA (inpatient)
    bcma_df = transform_bcma_gold()

    logger.info("=" * 70)
    logger.info("Gold transformation complete for all Medications")
    logger.info(f"  - RxOut (Outpatient): {len(rxout_df)} prescriptions")
    logger.info(f"  - BCMA (Inpatient): {len(bcma_df)} administration events")
    logger.info("=" * 70)

    return {
        "rxout": rxout_df,
        "bcma": bcma_df
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_all_medications_gold()
