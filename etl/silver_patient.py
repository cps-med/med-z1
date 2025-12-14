# ---------------------------------------------------------------------
# silver_patient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze version
#  - read from med-z1/bronze/cdwwork/patient
#  - read from med-z1/bronze/cdwwork/patient_address
#  - read from med-z1/bronze/cdwwork/patient_insurance
#  - read from med-z1/bronze/cdwwork/insurance_company_dim
#  - read from med-z1/bronze/cdwwork/patient_disability (Phase 2)
#  - join and transform data
#  - save to med-z1/silver/patient as patient_cleaned.parquet
# ---------------------------------------------------------------------
# Version History:
#   v1.0 (2025-12-10): Initial Silver transformation
#   v2.0 (2025-12-11): Added address, phone, and insurance data
#   v3.0 (2025-12-14): Added marital_status, religion, service_connected_percent,
#                       deceased_flag, death_date (Demographics Phase 2)
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a
# module (for now... there are other options to consider later).
#  $ cd med-z1
#  $ python -m etl.silver_patient
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def transform_patient_silver():
    """Transform Bronze patient data to Silver layer in MinIO."""

    logger.info("Starting Silver patient transformation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # Read Bronze Patient Parquet from MinIO
    patient_path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
    df_patient = minio_client.read_parquet(patient_path)
    logger.info(f"Bronze patient data read: {len(df_patient)} records")

    # Read Bronze Patient Address Parquet from MinIO
    address_path = build_bronze_path("cdwwork", "patient_address", "patient_address_raw.parquet")
    df_address = minio_client.read_parquet(address_path)
    logger.info(f"Bronze patient address data read: {len(df_address)} records")

    # Read Bronze Patient Insurance Parquet from MinIO
    insurance_path = build_bronze_path("cdwwork", "patient_insurance", "patient_insurance_raw.parquet")
    df_insurance = minio_client.read_parquet(insurance_path)
    logger.info(f"Bronze patient insurance data read: {len(df_insurance)} records")

    # Read Bronze Insurance Company Dimension Parquet from MinIO
    insurance_company_path = build_bronze_path("cdwwork", "insurance_company_dim", "insurance_company_dim_raw.parquet")
    df_insurance_company = minio_client.read_parquet(insurance_company_path)
    logger.info(f"Bronze insurance company dimension data read: {len(df_insurance_company)} records")

    # Read Bronze Patient Disability Parquet from MinIO (Phase 2)
    disability_path = build_bronze_path("cdwwork", "patient_disability", "patient_disability_raw.parquet")
    df_disability = minio_client.read_parquet(disability_path)
    logger.info(f"Bronze patient disability data read: {len(df_disability)} records")

    # Prep to calculate current age from DOB
    today = datetime.now(timezone.utc).date()

    # Transform and clean patient data
    df_patient = df_patient.with_columns([
        # Standardize field names
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("PatientICN").alias("icn"),
        pl.col("PatientSSN").alias("ssn"),

        # Clean name fields
        pl.col("PatientLastName").str.strip_chars().alias("name_last"),
        pl.col("PatientFirstName").str.strip_chars().alias("name_first"),

        # Create display name
        (pl.col("PatientLastName").str.strip_chars() + ", " +
         pl.col("PatientFirstName").str.strip_chars()).alias("name_display"),

         # Handle dates
         pl.col("BirthDateTime").cast(pl.Date).alias("dob"),

         # Calculate age
         ((pl.lit(today).cast(pl.Date) - pl.col("BirthDateTime").cast(pl.Date)).dt.total_days() / 365.25) \
            .cast(pl.Int32).alias("age"),

         # Standardize sex
         pl.col("Gender").str.strip_chars().alias("sex"),

         # Extract SSN last 4
         pl.col("PatientSSN").str.slice(-4).alias("ssn_last4"),

         # Station
         pl.col("Sta3n").cast(pl.Utf8).alias("primary_station"),

         # Phase 2: Additional demographics
         pl.col("MaritalStatus").str.strip_chars().alias("marital_status"),
         pl.col("Religion").str.strip_chars().alias("religion"),
         pl.col("DeceasedFlag").str.strip_chars().alias("deceased_flag"),
         pl.col("DeathDateTime").cast(pl.Date).alias("death_date"),

         # Metadata
         pl.col("SourceSystem").alias("source_system"),
    ])

    # Select primary address for each patient
    # Logic: OrdinalNumber = 1 AND AddressType = 'HOME'
    # Note: .unique() added to handle duplicate addresses in Bronze layer
    df_primary_address = (
        df_address
        .filter(
            (pl.col("OrdinalNumber") == 1) &
            (pl.col("AddressType") == "HOME")
        )
        .select([
            pl.col("PatientSID").alias("patient_sid_addr"),
            pl.col("StreetAddress1").str.strip_chars().alias("address_street1"),
            pl.col("StreetAddress2").str.strip_chars().alias("address_street2"),
            pl.col("City").str.strip_chars().alias("address_city"),
            pl.col("State").str.strip_chars().alias("address_state"),
            pl.col("Zip").str.strip_chars().alias("address_zip"),
        ])
        .unique(subset=["patient_sid_addr"])  # Deduplicate: one address per patient
    )
    logger.info(f"Selected {len(df_primary_address)} primary addresses (after deduplication)")

    # Select primary insurance for each patient
    # Logic: Most recent PolicyEffectiveDate
    df_primary_insurance = (
        df_insurance
        .sort("PolicyEffectiveDate", descending=True)
        .group_by("PatientSID")
        .agg([
            pl.col("InsuranceCompanySID").first().alias("insurance_company_sid"),
            pl.col("PolicyEffectiveDate").first().alias("policy_effective_date"),
        ])
        .select([
            pl.col("PatientSID").alias("patient_sid_ins"),
            pl.col("insurance_company_sid"),
            pl.col("policy_effective_date"),
        ])
    )
    logger.info(f"Selected {len(df_primary_insurance)} primary insurance records")

    # Join insurance company names
    df_primary_insurance = df_primary_insurance.join(
        df_insurance_company.select([
            pl.col("InsuranceCompanySID"),
            pl.col("InsuranceCompanyName").str.strip_chars().alias("insurance_company_name"),
        ]),
        left_on="insurance_company_sid",
        right_on="InsuranceCompanySID",
        how="left"
    )
    logger.info("Joined insurance company names to insurance records")

    # Select service connected percent from disability (Phase 2)
    # Logic: One record per patient (most recent if multiple exist)
    df_service_connected = (
        df_disability
        .select([
            pl.col("PatientSID").alias("patient_sid_disability"),
            pl.col("ServiceConnectedPercent").alias("service_connected_percent"),
        ])
        .unique(subset=["patient_sid_disability"])  # Deduplicate: one record per patient
    )
    logger.info(f"Selected {len(df_service_connected)} service connected records")

    # Join primary address to patient (left join - not all patients may have addresses)
    df = df_patient.join(
        df_primary_address,
        left_on="patient_sid",
        right_on="patient_sid_addr",
        how="left"
    )
    logger.info("Joined primary addresses to patient records")

    # Join primary insurance to patient (left join - not all patients may have insurance)
    df = df.join(
        df_primary_insurance,
        left_on="patient_sid",
        right_on="patient_sid_ins",
        how="left"
    )
    logger.info("Joined primary insurance to patient records")

    # Join service connected data to patient (left join - not all patients may have disability records)
    df = df.join(
        df_service_connected,
        left_on="patient_sid",
        right_on="patient_sid_disability",
        how="left"
    )
    logger.info("Joined service connected data to patient records")

    # Add phone placeholder (hardcoded for MVP)
    df = df.with_columns([
        pl.lit("Not available").alias("phone_primary"),
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Select final columns (v3.0 - includes Phase 2 fields)
    df = df.select([
        "patient_sid",
        "icn",
        "ssn",
        "ssn_last4",
        "name_last",
        "name_first",
        "name_display",
        "dob",
        "age",
        "sex",
        "primary_station",
        "address_street1",
        "address_street2",
        "address_city",
        "address_state",
        "address_zip",
        "phone_primary",
        "insurance_company_name",
        "marital_status",
        "religion",
        "service_connected_percent",
        "deceased_flag",
        "death_date",
        "source_system",
        "last_updated",
    ])

    # Build Silver path
    silver_path = build_silver_path("patient", "patient_cleaned.parquet")

    # Write to MinIO
    minio_client.write_parquet(df, silver_path)
    logger.info("Silver Parquet file written to MinIO")

    logger.info(
        f"Silver transformation complete: {len(df)} patients written to "
        f"s3://{minio_client.bucket_name}/{silver_path}"
    )

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_patient_silver()
