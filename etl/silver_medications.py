# ---------------------------------------------------------------------
# silver_medications.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze medications data
#  - Read Bronze: local_drug_dim, national_drug_dim, rxout_rxoutpat,
#                 rxout_rxoutpatfill, bcma_medicationlog
#  - Clean and validate data
#  - Resolve lookups: LocalDrug → NationalDrug, Sta3n, Staff/Providers
#  - Join RxOutpat with latest RxOutpatFill
#  - Calculate rx_status_computed for outpatient medications
#  - Save to med-z1/silver/medications as:
#    - medications_rxout_cleaned.parquet (outpatient)
#    - medications_bcma_cleaned.parquet (inpatient)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_medications
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

# Note: SQLAlchemy and CDWWORK_DB_CONFIG imports are retained only for
# load_sta3n_lookup() and load_staff_lookup() functions.
# TODO: Future enhancement - extract Sta3n and Staff to Bronze layer
# to fully comply with medallion architecture.

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
        FirstName,
        DEA,
        NPI
    FROM SStaff.SStaff
    """

    with engine.connect() as conn:
        staff_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(staff_df)} staff records for lookup")
    return staff_df


def load_patient_lookup():
    """
    Load Patient lookup table from Bronze layer.
    Returns a polars DataFrame with PatientSID to PatientICN mapping.
    Adheres to medallion architecture: Silver only reads from Bronze Parquet.
    """
    logger.info("Loading Patient lookup table from Bronze layer")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Load Bronze patient data
    patient_path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
    patient_df = minio_client.read_parquet(patient_path)

    # Select only needed columns for lookup
    patient_df = patient_df.select([
        "PatientSID",
        "PatientICN",
        "PatientName",
        "Sta3n"
    ]).filter(
        pl.col("PatientICN").is_not_null()
    )

    logger.info(f"Loaded {len(patient_df)} patient records for ICN lookup from Bronze Parquet")
    return patient_df


def transform_rxout_silver():
    """Transform Bronze RxOut (outpatient) data to Silver layer."""

    logger.info("=" * 70)
    logger.info("Starting Silver RxOut transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading Bronze Parquet files...")

    # Load dimension tables
    local_drug_path = build_bronze_path("cdwwork", "local_drug_dim", "local_drug_dim_raw.parquet")
    df_local_drug = minio_client.read_parquet(local_drug_path)
    logger.info(f"  - Loaded {len(df_local_drug)} local drugs")

    national_drug_path = build_bronze_path("cdwwork", "national_drug_dim", "national_drug_dim_raw.parquet")
    df_national_drug = minio_client.read_parquet(national_drug_path)
    logger.info(f"  - Loaded {len(df_national_drug)} national drugs")

    # Load RxOut fact tables
    rxoutpat_path = build_bronze_path("cdwwork", "rxout_rxoutpat", "rxout_rxoutpat_raw.parquet")
    df_rxoutpat = minio_client.read_parquet(rxoutpat_path)
    logger.info(f"  - Loaded {len(df_rxoutpat)} outpatient prescriptions")

    rxoutpatfill_path = build_bronze_path("cdwwork", "rxout_rxoutpatfill", "rxout_rxoutpatfill_raw.parquet")
    df_rxoutpatfill = minio_client.read_parquet(rxoutpatfill_path)
    logger.info(f"  - Loaded {len(df_rxoutpatfill)} prescription fills")

    # Load RxOutpatSig table (medication directions)
    rxoutpatsig_path = build_bronze_path("cdwwork", "rxout_rxoutpatsig", "rxout_rxoutpatsig_raw.parquet")
    df_rxoutpatsig = minio_client.read_parquet(rxoutpatsig_path)
    logger.info(f"  - Loaded {len(df_rxoutpatsig)} sig records")

    # Load lookup tables
    sta3n_lookup = load_sta3n_lookup()
    staff_lookup = load_staff_lookup()
    patient_lookup = load_patient_lookup()

    # ==================================================================
    # Step 2: Join with patient demographics to get PatientICN
    # ==================================================================
    logger.info("Step 2: Joining with patient demographics to get PatientICN...")

    df_rxoutpat = df_rxoutpat.join(
        patient_lookup.select([
            "PatientSID",
            pl.col("PatientICN").alias("patient_icn"),
        ]),
        on="PatientSID",
        how="left"
    )

    # Log any prescriptions without ICN mapping
    missing_icn_count = df_rxoutpat.filter(pl.col("patient_icn").is_null()).shape[0]
    if missing_icn_count > 0:
        logger.warning(f"  - {missing_icn_count} prescriptions missing PatientICN mapping")
    else:
        logger.info(f"  - All {len(df_rxoutpat)} prescriptions have PatientICN mapping")

    # ==================================================================
    # Step 3: Get latest fill per prescription
    # ==================================================================
    logger.info("Step 3: Determining latest fill per prescription...")

    # Sort by FillDateTime descending and take first record per RxOutpatSID
    df_latest_fill = (
        df_rxoutpatfill
        .sort("FillDateTime", descending=True)
        .group_by("RxOutpatSID")
        .first()
    )

    logger.info(f"  - Found latest fill for {len(df_latest_fill)} prescriptions")

    # ==================================================================
    # Step 4: Join RxOutpat with latest fill
    # ==================================================================
    logger.info("Step 4: Joining prescriptions with latest fills...")

    df = df_rxoutpat.join(
        df_latest_fill.select([
            "RxOutpatSID",
            pl.col("RxOutpatFillSID").alias("latest_fill_sid"),
            pl.col("FillNumber").alias("latest_fill_number"),
            pl.col("FillDateTime").alias("latest_fill_datetime"),
            pl.col("FillStatus").alias("latest_fill_status"),
            pl.col("QuantityDispensed").alias("latest_quantity_dispensed"),
            pl.col("DaysSupplyDispensed").alias("latest_days_supply_dispensed"),
        ]),
        on="RxOutpatSID",
        how="left"
    )

    logger.info(f"  - Joined {len(df)} prescriptions with fill data")

    # ==================================================================
    # Step 4.5: Join with Sig data (medication directions)
    # ==================================================================
    logger.info("Step 4.5: Joining with sig data (medication directions)...")

    # Select relevant sig fields
    df_sig_select = df_rxoutpatsig.select([
        "RxOutpatSID",
        pl.col("CompleteSignature").alias("sig"),
        pl.col("Route").alias("sig_route"),
        pl.col("Schedule").alias("sig_schedule"),
    ])

    # Join sig data (left join since not all prescriptions may have sig records)
    df = df.join(
        df_sig_select,
        on="RxOutpatSID",
        how="left"
    )

    # Log sig join results
    sig_match_count = df.filter(pl.col("sig").is_not_null()).shape[0]
    logger.info(f"  - Matched sig data for {sig_match_count}/{len(df)} prescriptions")

    # ==================================================================
    # Step 5: Resolve LocalDrug lookups
    # ==================================================================
    logger.info("Step 5: Resolving LocalDrug lookups...")

    df = df.join(
        df_local_drug.select([
            "LocalDrugSID",
            pl.col("NationalDrugSID").alias("NationalDrugSID_from_LocalDrug"),  # Use correct mapping
            pl.col("DrugNameWithoutDose").alias("drug_name_local_without_dose"),
            pl.col("DrugNameWithDose").alias("drug_name_local_with_dose"),
            pl.col("GenericName").alias("local_generic_name"),
            pl.col("Strength").alias("drug_strength"),
            pl.col("Unit").alias("drug_unit"),
            pl.col("DosageForm").alias("dosage_form"),
        ]),
        on="LocalDrugSID",
        how="left"
    )

    logger.info(f"  - Resolved local drug names for {len(df)} prescriptions")

    # ==================================================================
    # Step 6: Resolve NationalDrug lookups (using LocalDrug mapping)
    # ==================================================================
    logger.info("Step 6: Resolving NationalDrug lookups...")

    # Use NationalDrugSID from LocalDrug dimension, not from RxOutpat
    # (RxOutpat may have stale/incorrect NationalDrugSID values)
    df = df.join(
        df_national_drug.select([
            "NationalDrugSID",
            pl.col("NationalDrugName").alias("drug_name_national"),
            pl.col("GenericName").alias("national_generic_name"),
            pl.col("VAGenericName").alias("va_generic_name"),
            pl.col("TradeName").alias("trade_name"),
            pl.col("NDCCode").alias("ndc_code"),
            pl.col("DrugClass").alias("drug_class"),
            pl.col("DrugClassCode").alias("drug_class_code"),
            pl.col("DEASchedule").alias("dea_schedule"),
            pl.col("ControlledSubstanceFlag").alias("controlled_substance_flag"),
        ]),
        left_on="NationalDrugSID_from_LocalDrug",
        right_on="NationalDrugSID",
        how="left"
    )

    logger.info(f"  - Resolved national drug names for {len(df)} prescriptions")

    # ==================================================================
    # Step 7: Resolve Sta3n lookups (facility names)
    # ==================================================================
    logger.info("Step 7: Resolving Sta3n lookups...")

    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n"),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # ==================================================================
    # Step 8: Resolve Provider lookups
    # ==================================================================
    logger.info("Step 8: Resolving provider lookups...")

    df = df.join(
        staff_lookup.select([
            "StaffSID",
            pl.col("StaffName").alias("provider_name"),
        ]),
        left_on="ProviderSID",
        right_on="StaffSID",
        how="left"
    )

    # Also resolve ordering provider if different
    df = df.join(
        staff_lookup.select([
            "StaffSID",
            pl.col("StaffName").alias("ordering_provider_name"),
        ]),
        left_on="OrderingProviderSID",
        right_on="StaffSID",
        how="left",
        suffix="_ordering"
    )

    # ==================================================================
    # Step 9: Calculate rx_status_computed
    # ==================================================================
    logger.info("Step 9: Calculating rx_status_computed...")

    current_date = datetime.now()  # Naive datetime to match database datetimes

    df = df.with_columns([
        # rx_status_computed: ACTIVE if not discontinued and not expired
        pl.when(
            (pl.col("DiscontinuedDateTime").is_not_null()) |
            ((pl.col("ExpirationDateTime").is_not_null()) & (pl.col("ExpirationDateTime") < current_date))
        )
        .then(pl.col("RxStatus"))  # Use original status if discontinued or expired
        .otherwise(pl.lit("ACTIVE"))
        .alias("rx_status_computed"),

        # is_controlled_substance: Y if DEASchedule is not null
        pl.when(pl.col("dea_schedule").is_not_null())
        .then(pl.lit("Y"))
        .otherwise(pl.lit("N"))
        .alias("is_controlled_substance"),
    ])

    # ==================================================================
    # Step 10: Clean and standardize fields
    # ==================================================================
    logger.info("Step 10: Cleaning and standardizing fields...")

    df = df.with_columns([
        # Clean string fields
        pl.col("drug_name_local_with_dose").str.strip_chars().alias("drug_name_local_with_dose"),
        pl.col("drug_name_national").str.strip_chars().alias("drug_name_national"),
        pl.col("facility_name").str.strip_chars().alias("facility_name"),
        pl.col("provider_name").str.strip_chars().alias("provider_name"),
        pl.col("PharmacyName").str.strip_chars().alias("pharmacy_name"),

        # Metadata
        pl.lit("CDWWork").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 11: Select final columns
    # ==================================================================
    logger.info("Step 11: Selecting final columns...")

    df = df.select([
        # IDs
        pl.col("RxOutpatSID").alias("rx_outpat_id"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("patient_icn"),
        pl.col("LocalDrugSID").alias("local_drug_id"),
        pl.col("NationalDrugSID_from_LocalDrug").alias("national_drug_id"),

        # Prescription info
        pl.col("PrescriptionNumber").alias("prescription_number"),
        pl.col("IssueDateTime").alias("issue_datetime"),
        pl.col("RxStatus").alias("rx_status_original"),
        pl.col("rx_status_computed"),
        pl.col("RxType").alias("rx_type"),

        # Drug names
        pl.col("drug_name_local_with_dose"),
        pl.col("drug_name_local_without_dose"),
        pl.col("drug_name_national"),
        pl.col("national_generic_name"),
        pl.col("trade_name"),
        pl.col("drug_strength"),
        pl.col("drug_unit"),
        pl.col("dosage_form"),

        # Drug classification
        pl.col("drug_class"),
        pl.col("drug_class_code"),
        pl.col("dea_schedule"),
        pl.col("controlled_substance_flag"),
        pl.col("is_controlled_substance"),
        pl.col("ndc_code"),

        # Prescription details
        pl.col("Quantity").alias("quantity_ordered"),
        pl.col("DaysSupply").alias("days_supply_ordered"),
        pl.col("RefillsAllowed").alias("refills_allowed"),
        pl.col("RefillsRemaining").alias("refills_remaining"),
        pl.col("UnitDose").alias("unit_dose"),

        # Latest fill info
        pl.col("latest_fill_sid"),
        pl.col("latest_fill_number"),
        pl.col("latest_fill_datetime"),
        pl.col("latest_fill_status"),
        pl.col("latest_quantity_dispensed"),
        pl.col("latest_days_supply_dispensed"),

        # Sig (medication directions)
        pl.col("sig"),
        pl.col("sig_route"),
        pl.col("sig_schedule"),

        # Dates
        pl.col("ExpirationDateTime").alias("expiration_datetime"),
        pl.col("DiscontinuedDateTime").alias("discontinued_datetime"),
        pl.col("DiscontinueReason").alias("discontinue_reason"),

        # Providers and locations
        pl.col("ProviderSID").alias("provider_sid"),
        pl.col("provider_name"),
        pl.col("OrderingProviderSID").alias("ordering_provider_sid"),
        pl.col("ordering_provider_name"),
        pl.col("pharmacy_name"),
        pl.col("ClinicName").alias("clinic_name"),

        # Facility
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("facility_name"),

        # Flags
        pl.col("CMOPIndicator").alias("cmop_indicator"),
        pl.col("MailIndicator").alias("mail_indicator"),

        # Metadata
        pl.col("source_system"),
        pl.col("last_updated"),
    ])

    # ==================================================================
    # Step 12: Write to Silver layer
    # ==================================================================
    logger.info("Step 12: Writing to Silver layer...")

    silver_path = build_silver_path("medications", "medications_rxout_cleaned.parquet")
    minio_client.write_parquet(df, silver_path)

    logger.info("=" * 70)
    logger.info(f"Silver RxOut transformation complete: {len(df)} prescriptions written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{silver_path}")
    logger.info("=" * 70)

    return df


def transform_bcma_silver():
    """Transform Bronze BCMA (inpatient) data to Silver layer."""

    logger.info("=" * 70)
    logger.info("Starting Silver BCMA transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading Bronze Parquet files...")

    # Load dimension tables
    local_drug_path = build_bronze_path("cdwwork", "local_drug_dim", "local_drug_dim_raw.parquet")
    df_local_drug = minio_client.read_parquet(local_drug_path)
    logger.info(f"  - Loaded {len(df_local_drug)} local drugs")

    national_drug_path = build_bronze_path("cdwwork", "national_drug_dim", "national_drug_dim_raw.parquet")
    df_national_drug = minio_client.read_parquet(national_drug_path)
    logger.info(f"  - Loaded {len(df_national_drug)} national drugs")

    # Load BCMA fact table
    bcma_path = build_bronze_path("cdwwork", "bcma_medicationlog", "bcma_medicationlog_raw.parquet")
    df_bcma = minio_client.read_parquet(bcma_path)
    logger.info(f"  - Loaded {len(df_bcma)} BCMA medication log entries")

    # Load lookup tables
    sta3n_lookup = load_sta3n_lookup()
    staff_lookup = load_staff_lookup()
    patient_lookup = load_patient_lookup()

    # ==================================================================
    # Step 2: Join with patient demographics to get PatientICN
    # ==================================================================
    logger.info("Step 2: Joining with patient demographics to get PatientICN...")

    df_bcma = df_bcma.join(
        patient_lookup.select([
            "PatientSID",
            pl.col("PatientICN").alias("patient_icn"),
        ]),
        on="PatientSID",
        how="left"
    )

    # Log any administrations without ICN mapping
    missing_icn_count = df_bcma.filter(pl.col("patient_icn").is_null()).shape[0]
    if missing_icn_count > 0:
        logger.warning(f"  - {missing_icn_count} administrations missing PatientICN mapping")
    else:
        logger.info(f"  - All {len(df_bcma)} administrations have PatientICN mapping")

    # ==================================================================
    # Step 3: Resolve LocalDrug lookups
    # ==================================================================
    logger.info("Step 3: Resolving LocalDrug lookups...")

    df = df_bcma.join(
        df_local_drug.select([
            "LocalDrugSID",
            pl.col("NationalDrugSID").alias("NationalDrugSID_from_LocalDrug"),  # Use correct mapping
            pl.col("DrugNameWithoutDose").alias("drug_name_local_without_dose"),
            pl.col("DrugNameWithDose").alias("drug_name_local_with_dose"),
            pl.col("GenericName").alias("local_generic_name"),
            pl.col("Strength").alias("drug_strength"),
            pl.col("Unit").alias("drug_unit"),
            pl.col("DosageForm").alias("dosage_form"),
        ]),
        on="LocalDrugSID",
        how="left"
    )

    logger.info(f"  - Resolved local drug names for {len(df)} administration events")

    # ==================================================================
    # Step 4: Resolve NationalDrug lookups (using LocalDrug mapping)
    # ==================================================================
    logger.info("Step 4: Resolving NationalDrug lookups...")

    # Use NationalDrugSID from LocalDrug dimension, not from BCMA
    # (BCMA may have stale/incorrect NationalDrugSID values)
    df = df.join(
        df_national_drug.select([
            "NationalDrugSID",
            pl.col("NationalDrugName").alias("drug_name_national"),
            pl.col("GenericName").alias("national_generic_name"),
            pl.col("VAGenericName").alias("va_generic_name"),
            pl.col("TradeName").alias("trade_name"),
            pl.col("NDCCode").alias("ndc_code"),
            pl.col("DrugClass").alias("drug_class"),
            pl.col("DrugClassCode").alias("drug_class_code"),
            pl.col("DEASchedule").alias("dea_schedule"),
            pl.col("ControlledSubstanceFlag").alias("controlled_substance_flag"),
        ]),
        left_on="NationalDrugSID_from_LocalDrug",
        right_on="NationalDrugSID",
        how="left"
    )

    logger.info(f"  - Resolved national drug names for {len(df)} administration events")

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
    # Step 6: Resolve Staff lookups (administered by)
    # ==================================================================
    logger.info("Step 6: Resolving staff lookups...")

    df = df.join(
        staff_lookup.select([
            "StaffSID",
            pl.col("StaffName").alias("administered_by_name"),
        ]),
        left_on="AdministeredByStaffSID",
        right_on="StaffSID",
        how="left"
    )

    # Resolve ordering provider
    df = df.join(
        staff_lookup.select([
            "StaffSID",
            pl.col("StaffName").alias("ordering_provider_name"),
        ]),
        left_on="OrderingProviderSID",
        right_on="StaffSID",
        how="left",
        suffix="_ordering"
    )

    # ==================================================================
    # Step 7: Calculate computed fields
    # ==================================================================
    logger.info("Step 7: Calculating computed fields...")

    df = df.with_columns([
        # is_controlled_substance: Y if DEASchedule is not null
        pl.when(pl.col("dea_schedule").is_not_null())
        .then(pl.lit("Y"))
        .otherwise(pl.lit("N"))
        .alias("is_controlled_substance"),

        # has_variance: Y if VarianceFlag is Y
        pl.when(pl.col("VarianceFlag") == "Y")
        .then(pl.lit("Y"))
        .otherwise(pl.lit("N"))
        .alias("has_variance"),
    ])

    # ==================================================================
    # Step 8: Clean and standardize fields
    # ==================================================================
    logger.info("Step 8: Cleaning and standardizing fields...")

    df = df.with_columns([
        # Clean string fields
        pl.col("ActionType").str.strip_chars().str.to_uppercase().alias("action_type"),
        pl.col("ActionStatus").str.strip_chars().str.to_uppercase().alias("action_status"),
        pl.col("drug_name_local_with_dose").str.strip_chars().alias("drug_name_local_with_dose"),
        pl.col("drug_name_national").str.strip_chars().alias("drug_name_national"),
        pl.col("facility_name").str.strip_chars().alias("facility_name"),
        pl.col("administered_by_name").str.strip_chars().alias("administered_by_name"),
        pl.col("ordering_provider_name").str.strip_chars().alias("ordering_provider_name"),
        pl.col("WardName").str.strip_chars().alias("ward_name"),
        pl.col("Route").str.strip_chars().alias("route"),

        # Metadata
        pl.lit("CDWWork").alias("source_system"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # ==================================================================
    # Step 9: Select final columns
    # ==================================================================
    logger.info("Step 9: Selecting final columns...")

    df = df.select([
        # IDs
        pl.col("BCMAMedicationLogSID").alias("bcma_medication_log_id"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("patient_icn"),
        pl.col("InpatientSID").alias("inpatient_sid"),
        pl.col("LocalDrugSID").alias("local_drug_id"),
        pl.col("NationalDrugSID_from_LocalDrug").alias("national_drug_id"),

        # Action info
        pl.col("action_type"),
        pl.col("action_status"),
        pl.col("ActionDateTime").alias("action_datetime"),
        pl.col("ScheduledDateTime").alias("scheduled_datetime"),
        pl.col("OrderedDateTime").alias("ordered_datetime"),
        pl.col("OrderNumber").alias("order_number"),

        # Drug names
        pl.col("drug_name_local_with_dose"),
        pl.col("drug_name_local_without_dose"),
        pl.col("drug_name_national"),
        pl.col("national_generic_name"),
        pl.col("trade_name"),
        pl.col("drug_strength"),
        pl.col("drug_unit"),
        pl.col("dosage_form"),

        # Drug classification
        pl.col("drug_class"),
        pl.col("drug_class_code"),
        pl.col("dea_schedule"),
        pl.col("controlled_substance_flag"),
        pl.col("is_controlled_substance"),
        pl.col("ndc_code"),

        # Administration details
        pl.col("DosageOrdered").alias("dosage_ordered"),
        pl.col("DosageGiven").alias("dosage_given"),
        pl.col("route"),
        pl.col("UnitOfAdministration").alias("unit_of_administration"),
        pl.col("ScheduleType").alias("schedule_type"),
        pl.col("Schedule").alias("schedule"),

        # Variance info
        pl.col("has_variance"),
        pl.col("VarianceType").alias("variance_type"),
        pl.col("VarianceReason").alias("variance_reason"),

        # IV info
        pl.col("IVFlag").alias("iv_flag"),
        pl.col("IVType").alias("iv_type"),
        pl.col("InfusionRate").alias("infusion_rate"),

        # Staff and locations
        pl.col("AdministeredByStaffSID").alias("administered_by_staff_sid"),
        pl.col("administered_by_name"),
        pl.col("OrderingProviderSID").alias("ordering_provider_sid"),
        pl.col("ordering_provider_name"),
        pl.col("ward_name"),

        # Facility
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("facility_name"),

        # Metadata
        pl.col("source_system"),
        pl.col("last_updated"),
    ])

    # ==================================================================
    # Step 10: Write to Silver layer
    # ==================================================================
    logger.info("Step 10: Writing to Silver layer...")

    silver_path = build_silver_path("medications", "medications_bcma_cleaned.parquet")
    minio_client.write_parquet(df, silver_path)

    logger.info("=" * 70)
    logger.info(f"Silver BCMA transformation complete: {len(df)} administration events written to")
    logger.info(f"  s3://{minio_client.bucket_name}/{silver_path}")
    logger.info("=" * 70)

    return df


def transform_all_medications_silver():
    """Transform all medications data from Bronze to Silver."""
    logger.info("=" * 70)
    logger.info("Starting Silver transformation for all Medications")
    logger.info("=" * 70)

    # Transform RxOut (outpatient)
    rxout_df = transform_rxout_silver()

    # Transform BCMA (inpatient)
    bcma_df = transform_bcma_silver()

    logger.info("=" * 70)
    logger.info("Silver transformation complete for all Medications")
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
    transform_all_medications_silver()
