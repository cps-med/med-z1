# ---------------------------------------------------------------------
# bronze_medications.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Medications from CDWWork database.
#  - Extract 5 tables:
#    1. Dim.LocalDrug → bronze/cdwwork/local_drug_dim
#    2. Dim.NationalDrug → bronze/cdwwork/national_drug_dim
#    3. RxOut.RxOutpat → bronze/cdwwork/rxout_rxoutpat
#    4. RxOut.RxOutpatFill → bronze/cdwwork/rxout_rxoutpatfill
#    5. BCMA.BCMAMedicationLog → bronze/cdwwork/bcma_medicationlog
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_medications
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)


def extract_local_drug_dim():
    """Extract Dim.LocalDrug to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.LocalDrug")

    minio_client = MinIOClient()

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

    # Extract query - get all active local drugs
    query = """
    SELECT
        LocalDrugSID,
        LocalDrugIEN,
        Sta3n,
        NationalDrugSID,
        NationalDrugIEN,
        DrugNameWithoutDose,
        DrugNameWithDose,
        GenericName,
        VAProductName,
        Strength,
        Unit,
        DosageForm,
        DrugClass,
        DrugClassCode,
        ActiveIngredient,
        Inactive,
        InactiveDate
    FROM Dim.LocalDrug
    WHERE Inactive = 'N' OR Inactive IS NULL
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} local drugs from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="local_drug_dim",
        filename="local_drug_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} local drugs written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_national_drug_dim():
    """Extract Dim.NationalDrug to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.NationalDrug")

    minio_client = MinIOClient()

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

    # Extract query - get all active national drugs
    query = """
    SELECT
        NationalDrugSID,
        NationalDrugIEN,
        NationalDrugName,
        GenericName,
        VAGenericName,
        TradeName,
        NDCCode,
        DrugClass,
        DrugClassCode,
        DEASchedule,
        ControlledSubstanceFlag,
        ActiveIngredients,
        Inactive,
        InactiveDate
    FROM Dim.NationalDrug
    WHERE Inactive = 'N' OR Inactive IS NULL
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} national drugs from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="national_drug_dim",
        filename="national_drug_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} national drugs written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_rxout_rxoutpat():
    """Extract RxOut.RxOutpat to Bronze layer."""
    logger.info("Starting Bronze extraction: RxOut.RxOutpat")

    minio_client = MinIOClient()

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

    # Extract query - get all outpatient prescriptions
    query = """
    SELECT
        RxOutpatSID,
        RxOutpatIEN,
        Sta3n,
        PatientSID,
        PatientIEN,
        LocalDrugSID,
        LocalDrugIEN,
        NationalDrugSID,
        DrugNameWithoutDose,
        DrugNameWithDose,
        PrescriptionNumber,
        IssueDateTime,
        IssueVistaErrorDate,
        IssueDateTimeTransformSID,
        ProviderSID,
        ProviderIEN,
        OrderingProviderSID,
        OrderingProviderIEN,
        EnteredByStaffSID,
        EnteredByStaffIEN,
        PharmacySID,
        PharmacyIEN,
        PharmacyName,
        RxStatus,
        RxType,
        Quantity,
        DaysSupply,
        RefillsAllowed,
        RefillsRemaining,
        MaxRefills,
        UnitDose,
        ExpirationDateTime,
        ExpirationVistaErrorDate,
        ExpirationDateTimeTransformSID,
        DiscontinuedDateTime,
        DiscontinuedVistaErrorDate,
        DiscontinuedDateTimeTransformSID,
        DiscontinueReason,
        DiscontinuedByStaffSID,
        LoginDateTime,
        LoginVistaErrorDate,
        LoginDateTimeTransformSID,
        ClinicSID,
        ClinicIEN,
        ClinicName,
        DEASchedule,
        ControlledSubstanceFlag,
        CMOPIndicator,
        MailIndicator
    FROM RxOut.RxOutpat
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} outpatient prescriptions from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="rxout_rxoutpat",
        filename="rxout_rxoutpat_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} outpatient prescriptions written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_rxout_rxoutpatfill():
    """Extract RxOut.RxOutpatFill to Bronze layer."""
    logger.info("Starting Bronze extraction: RxOut.RxOutpatFill")

    minio_client = MinIOClient()

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

    # Extract query - get all prescription fills
    query = """
    SELECT
        RxOutpatFillSID,
        RxOutpatFillIEN,
        RxOutpatSID,
        Sta3n,
        PatientSID,
        PatientIEN,
        LocalDrugSID,
        NationalDrugSID,
        FillNumber,
        FillDateTime,
        FillVistaErrorDate,
        FillDateTimeTransformSID,
        ReleasedDateTime,
        ReleasedVistaErrorDate,
        ReleasedDateTimeTransformSID,
        DispensingPharmacistSID,
        DispensingPharmacistIEN,
        VerifyingPharmacistSID,
        VerifyingPharmacistIEN,
        PharmacySID,
        PharmacyIEN,
        PharmacyName,
        FillStatus,
        FillType,
        FillCost,
        DispensedDrugCost,
        QuantityDispensed,
        DaysSupplyDispensed,
        DispenseUnit,
        MailTrackingNumber,
        RoutingLocation,
        PrintedDateTime,
        PrintedVistaErrorDate,
        PrintedDateTimeTransformSID,
        PartialFillFlag,
        PartialFillReason,
        CMOPIndicator,
        CMOPEventNumber,
        CMOPDispenseDate,
        MailIndicator,
        WindowIndicator,
        ReturnedToStockFlag,
        ReturnedToStockDateTime,
        ReturnedToStockVistaErrorDate,
        ReturnedToStockDateTimeTransformSID
    FROM RxOut.RxOutpatFill
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} prescription fills from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="rxout_rxoutpatfill",
        filename="rxout_rxoutpatfill_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} prescription fills written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_rxout_rxoutpatsig():
    """Extract RxOut.RxOutpatSig to Bronze layer."""
    logger.info("Starting Bronze extraction: RxOut.RxOutpatSig")

    minio_client = MinIOClient()

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

    # Extract query - get all sig records
    query = """
    SELECT
        RxOutpatSigSID,
        RxOutpatSigIEN,
        RxOutpatSID,
        RxOutpatFillSID,
        Sta3n,
        PatientSID,
        PatientIEN,
        SegmentNumber,
        DosageOrdered,
        Verb,
        DispenseUnitsPerDose,
        Noun,
        Route,
        Schedule,
        ScheduleType,
        ScheduleTypeIEN,
        Duration,
        Conjunction,
        AdminTimes,
        CompleteSignature,
        SigSequence,
        LocalDrugSID,
        NationalDrugSID
    FROM RxOut.RxOutpatSig
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} sig records from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="rxout_rxoutpatsig",
        filename="rxout_rxoutpatsig_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} sig records written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_bcma_medicationlog():
    """Extract BCMA.BCMAMedicationLog to Bronze layer."""
    logger.info("Starting Bronze extraction: BCMA.BCMAMedicationLog")

    minio_client = MinIOClient()

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

    # Extract query - get all medication administration events
    query = """
    SELECT
        BCMAMedicationLogSID,
        BCMAMedicationLogIEN,
        Sta3n,
        PatientSID,
        PatientIEN,
        InpatientSID,
        InpatientIEN,
        ActionType,
        ActionStatus,
        ActionDateTime,
        ActionVistaErrorDate,
        ActionDateTimeTransformSID,
        ScheduledDateTime,
        ScheduledVistaErrorDate,
        ScheduledDateTimeTransformSID,
        OrderedDateTime,
        OrderedVistaErrorDate,
        OrderedDateTimeTransformSID,
        AdministeredByStaffSID,
        AdministeredByStaffIEN,
        OrderingProviderSID,
        OrderingProviderIEN,
        LocalDrugSID,
        LocalDrugIEN,
        NationalDrugSID,
        DrugNameWithoutDose,
        DrugNameWithDose,
        OrderNumber,
        DosageOrdered,
        DosageGiven,
        Route,
        RouteIEN,
        UnitOfAdministration,
        ScheduleType,
        Schedule,
        AdministrationUnit,
        WardLocationSID,
        WardLocationIEN,
        WardName,
        VarianceFlag,
        VarianceType,
        VarianceReason,
        VarianceComment,
        IVFlag,
        IVType,
        InfusionRate,
        TransactionDateTime,
        TransactionVistaErrorDate,
        TransactionDateTimeTransformSID
    FROM BCMA.BCMAMedicationLog
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} medication administration events from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="bcma_medicationlog",
        filename="bcma_medicationlog_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(
        f"Bronze extraction complete: {len(df)} medication administration events written to "
        f"s3://{minio_client.bucket_name}/{object_key}"
    )

    return df


def extract_all_medications_bronze():
    """Extract all medication tables to Bronze layer."""
    logger.info("=" * 60)
    logger.info("Starting Bronze extraction for all Medications tables")
    logger.info("=" * 60)

    # Extract all 6 tables
    local_drug_df = extract_local_drug_dim()
    national_drug_df = extract_national_drug_dim()
    rxoutpat_df = extract_rxout_rxoutpat()
    rxoutpatfill_df = extract_rxout_rxoutpatfill()
    rxoutpatsig_df = extract_rxout_rxoutpatsig()
    bcma_medicationlog_df = extract_bcma_medicationlog()

    logger.info("=" * 60)
    logger.info("Bronze extraction complete for all Medications tables")
    logger.info(f"  - Local Drugs: {len(local_drug_df)} rows")
    logger.info(f"  - National Drugs: {len(national_drug_df)} rows")
    logger.info(f"  - Outpatient Prescriptions: {len(rxoutpat_df)} rows")
    logger.info(f"  - Prescription Fills: {len(rxoutpatfill_df)} rows")
    logger.info(f"  - Sig Records: {len(rxoutpatsig_df)} rows")
    logger.info(f"  - BCMA Medication Log: {len(bcma_medicationlog_df)} rows")
    logger.info("=" * 60)

    return {
        "local_drug": local_drug_df,
        "national_drug": national_drug_df,
        "rxoutpat": rxoutpat_df,
        "rxoutpatfill": rxoutpatfill_df,
        "rxoutpatsig": rxoutpatsig_df,
        "bcma_medicationlog": bcma_medicationlog_df
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_all_medications_bronze()
