# ---------------------------------------------------------------------
# silver_patient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze version
#  - read from from med-z1/bronze/cdwwork/patient
#  - save to med-z1/silver/patient
#  - as patient_cleaned.parquet
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

    # Read Bronze Parquet from MinIO
    bronze_path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
    df = minio_client.read_parquet(bronze_path)
    logger.info("Bronze Parquet read into DataFrame")

    # Prep to calculate current age from DOB
    today = datetime.now(timezone.utc).date()

    #Transform and clean data
    df = df.with_columns([
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

         # Metadata
         pl.col("SourceSystem").alias("source_system"),
         pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Select final columns
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
