# ---------------------------------------------------------------------
# silver_problems.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze problems/diagnoses data
#  - Read Bronze: icd10_dim, charlson_mapping, outpat_problemlist (VistA),
#                 encmill_problemlist (Cerner)
#  - Harmonize VistA and Cerner schema differences
#  - Deduplicate problems across both systems (same ICN + ICD-10 + onset date)
#  - Join with ICD-10 and Charlson reference data
#  - Save to med-z1/silver/problems as:
#    - problems_harmonized.parquet (unified VistA + Cerner)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_problems
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def transform_problems_silver():
    """Transform Bronze problems to Silver layer with harmonization and deduplication."""

    logger.info("=" * 70)
    logger.info("Starting Silver Problems transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Bronze Parquet files
    # ==================================================================
    logger.info("Step 1: Loading Bronze Parquet files...")

    # Load reference data
    icd10_path = build_bronze_path("cdwwork", "icd10_dim", "icd10_dim_raw.parquet")
    df_icd10 = minio_client.read_parquet(icd10_path)
    logger.info(f"  - Loaded {len(df_icd10)} ICD-10 codes")

    charlson_path = build_bronze_path("cdwwork", "charlson_mapping", "charlson_mapping_raw.parquet")
    df_charlson = minio_client.read_parquet(charlson_path)
    logger.info(f"  - Loaded {len(df_charlson)} Charlson mappings")

    # Load clinical data (VistA + Cerner)
    vista_path = build_bronze_path("cdwwork", "outpat_problemlist", "outpat_problemlist_raw.parquet")
    df_vista = minio_client.read_parquet(vista_path)
    logger.info(f"  - Loaded {len(df_vista)} VistA problem records")

    cerner_path = build_bronze_path("cdwwork2", "encmill_problemlist", "encmill_problemlist_raw.parquet")
    df_cerner = minio_client.read_parquet(cerner_path)
    logger.info(f"  - Loaded {len(df_cerner)} Cerner problem records")

    # ==================================================================
    # Step 2: Harmonize VistA schema
    # ==================================================================
    logger.info("Step 2: Harmonizing VistA schema...")

    df_vista_harmonized = df_vista.select([
        pl.col("ProblemSID").alias("problem_id"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("PatientICN").alias("patient_icn"),
        pl.col("Sta3n").cast(pl.Utf8).alias("facility_id"),
        pl.col("ProblemNumber").alias("problem_number"),
        pl.col("ICD10Code").str.strip_chars().str.to_uppercase().alias("icd10_code"),
        pl.col("ICD10Description").alias("diagnosis_description"),
        pl.col("SNOMEDCode").str.strip_chars().alias("snomed_code"),
        pl.col("SNOMEDDescription").alias("snomed_description"),
        # Standardize status values: ACTIVE → Active, INACTIVE → Inactive, RESOLVED → Resolved
        pl.when(pl.col("ProblemStatus") == "ACTIVE")
          .then(pl.lit("Active"))
          .when(pl.col("ProblemStatus") == "INACTIVE")
          .then(pl.lit("Inactive"))
          .when(pl.col("ProblemStatus") == "RESOLVED")
          .then(pl.lit("Resolved"))
          .otherwise(pl.col("ProblemStatus"))
          .alias("problem_status"),
        pl.col("OnsetDate").cast(pl.Date).alias("onset_date"),
        pl.col("RecordedDate").cast(pl.Date).alias("recorded_date"),
        pl.col("LastModifiedDate").cast(pl.Date).alias("last_modified_date"),
        pl.col("ResolvedDate").cast(pl.Date).alias("resolved_date"),
        pl.col("ProviderSID").alias("provider_id"),
        pl.col("ProviderName").alias("provider_name"),
        pl.col("Clinic").alias("clinic_location"),
        # Standardize boolean flags: Y/N → True/False
        pl.when(pl.col("IsServiceConnected") == "Y")
          .then(pl.lit(True))
          .when(pl.col("IsServiceConnected") == "N")
          .then(pl.lit(False))
          .otherwise(None)
          .alias("service_connected"),
        pl.when(pl.col("IsAcuteCondition") == "Y")
          .then(pl.lit(True))
          .when(pl.col("IsAcuteCondition") == "N")
          .then(pl.lit(False))
          .otherwise(None)
          .alias("acute_condition"),
        pl.when(pl.col("IsChronicCondition") == "Y")
          .then(pl.lit(True))
          .when(pl.col("IsChronicCondition") == "N")
          .then(pl.lit(False))
          .otherwise(None)
          .alias("chronic_condition"),
        pl.col("EnteredBy").alias("entered_by_name"),
        pl.col("EnteredDateTime").cast(pl.Datetime).alias("entered_datetime"),
        pl.lit("VistA").alias("source_ehr"),
        pl.lit("CDWWork").alias("source_system"),
    ])

    logger.info(f"  - Harmonized {len(df_vista_harmonized)} VistA records")

    # ==================================================================
    # Step 3: Harmonize Cerner schema
    # ==================================================================
    logger.info("Step 3: Harmonizing Cerner schema...")

    df_cerner_harmonized = df_cerner.select([
        pl.col("DiagnosisSID").alias("problem_id"),
        pl.col("PatientKey").alias("patient_sid"),
        pl.col("PatientICN").alias("patient_icn"),
        pl.col("FacilityCode").cast(pl.Utf8).alias("facility_id"),
        pl.col("ProblemID").alias("problem_number"),
        pl.col("DiagnosisCode").str.strip_chars().str.to_uppercase().alias("icd10_code"),
        pl.col("DiagnosisDescription").alias("diagnosis_description"),
        pl.col("ClinicalTermCode").str.strip_chars().alias("snomed_code"),
        pl.col("ClinicalTermDescription").alias("snomed_description"),
        # Standardize status values: A → Active, I → Inactive, R → Resolved
        pl.when(pl.col("StatusCode") == "A")
          .then(pl.lit("Active"))
          .when(pl.col("StatusCode") == "I")
          .then(pl.lit("Inactive"))
          .when(pl.col("StatusCode") == "R")
          .then(pl.lit("Resolved"))
          .otherwise(pl.col("StatusCode"))
          .alias("problem_status"),
        pl.col("OnsetDateTime").cast(pl.Date).alias("onset_date"),
        pl.col("RecordDateTime").cast(pl.Date).alias("recorded_date"),
        pl.col("LastUpdateDateTime").cast(pl.Date).alias("last_modified_date"),
        pl.col("ResolvedDateTime").cast(pl.Date).alias("resolved_date"),
        pl.col("ResponsibleProviderID").alias("provider_id"),
        pl.col("ResponsibleProviderName").alias("provider_name"),
        pl.col("RecordingLocation").alias("clinic_location"),
        # Standardize boolean flags: Y/N → True/False
        pl.when(pl.col("ServiceConnectedFlag") == "Y")
          .then(pl.lit(True))
          .when(pl.col("ServiceConnectedFlag") == "N")
          .then(pl.lit(False))
          .otherwise(None)
          .alias("service_connected"),
        pl.when(pl.col("AcuteFlag") == "Y")
          .then(pl.lit(True))
          .when(pl.col("AcuteFlag") == "N")
          .then(pl.lit(False))
          .otherwise(None)
          .alias("acute_condition"),
        pl.when(pl.col("ChronicFlag") == "Y")
          .then(pl.lit(True))
          .when(pl.col("ChronicFlag") == "N")
          .then(pl.lit(False))
          .otherwise(None)
          .alias("chronic_condition"),
        pl.col("CreatedByUserName").alias("entered_by_name"),
        pl.col("CreatedDateTime").cast(pl.Datetime).alias("entered_datetime"),
        pl.lit("Cerner").alias("source_ehr"),
        pl.lit("CDWWork2").alias("source_system"),
    ])

    logger.info(f"  - Harmonized {len(df_cerner_harmonized)} Cerner records")

    # ==================================================================
    # Step 4: Union VistA + Cerner
    # ==================================================================
    logger.info("Step 4: Combining VistA and Cerner records...")

    df_combined = pl.concat([df_vista_harmonized, df_cerner_harmonized], how="vertical")
    logger.info(f"  - Combined {len(df_combined)} total problem records")

    # ==================================================================
    # Step 5: Deduplication logic
    # ==================================================================
    logger.info("Step 5: Deduplicating problems across both systems...")

    # Deduplication rule: Same ICN + Same ICD-10 Code + Same Onset Date = Duplicate
    # Prefer VistA for active problems (authoritative source)
    # Sort by: ICN, ICD-10, OnsetDate, then by source_ehr (VistA before Cerner alphabetically)

    df_deduplicated = (
        df_combined
        .sort([
            "patient_icn",
            "icd10_code",
            "onset_date",
            "source_ehr"  # "Cerner" < "VistA" alphabetically, so reverse needed
        ], descending=[False, False, False, True])  # VistA first (descending=True makes "VistA" come before "Cerner")
        .unique(subset=["patient_icn", "icd10_code", "onset_date"], keep="first", maintain_order=True)
    )

    duplicates_removed = len(df_combined) - len(df_deduplicated)
    logger.info(f"  - Removed {duplicates_removed} duplicate problems")
    logger.info(f"  - Retained {len(df_deduplicated)} unique problems")

    # ==================================================================
    # Step 6: Join with ICD-10 reference data
    # ==================================================================
    logger.info("Step 6: Enriching with ICD-10 reference data...")

    # Select relevant ICD-10 columns for join
    df_icd10_lookup = df_icd10.select([
        pl.col("ICD10Code").str.strip_chars().str.to_uppercase().alias("icd10_code"),
        pl.col("ICD10Category").alias("icd10_category"),
        pl.col("IsChronicCondition").alias("icd10_chronic_flag"),
        pl.col("CharlsonCondition").alias("icd10_charlson_condition"),
    ])

    df_enriched = df_deduplicated.join(
        df_icd10_lookup,
        on="icd10_code",
        how="left"
    )

    # Log ICD-10 join statistics
    missing_icd10_count = df_enriched.filter(pl.col("icd10_category").is_null()).shape[0]
    if missing_icd10_count > 0:
        logger.warning(f"  - {missing_icd10_count} problems missing ICD-10 reference data")
    else:
        logger.info(f"  - All {len(df_enriched)} problems have ICD-10 reference data")

    # ==================================================================
    # Step 7: Add Silver metadata
    # ==================================================================
    logger.info("Step 7: Adding Silver metadata...")

    df_silver = df_enriched.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("silver_load_datetime"),
        pl.lit("v1.0").alias("silver_schema_version"),
    ])

    # ==================================================================
    # Step 8: Write to Silver layer
    # ==================================================================
    logger.info("Step 8: Writing to Silver layer...")

    silver_path = build_silver_path("problems", "problems_harmonized.parquet")
    minio_client.write_parquet(df_silver, silver_path)

    logger.info(
        f"Silver transformation complete: {len(df_silver)} problems written to "
        f"s3://{minio_client.bucket_name}/{silver_path}"
    )

    # ==================================================================
    # Summary statistics
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Silver Problems Transformation Summary")
    logger.info("=" * 70)

    # Count by source EHR
    source_counts = df_silver.group_by("source_ehr").agg(
        pl.count().alias("count")
    ).sort("source_ehr")
    for row in source_counts.iter_rows(named=True):
        logger.info(f"  - {row['source_ehr']}: {row['count']} problems")

    # Count by problem status
    status_counts = df_silver.group_by("problem_status").agg(
        pl.count().alias("count")
    ).sort("count", descending=True)
    for row in status_counts.iter_rows(named=True):
        logger.info(f"  - {row['problem_status']}: {row['count']} problems")

    # Count chronic conditions
    chronic_count = df_silver.filter(pl.col("chronic_condition") == True).shape[0]
    logger.info(f"  - Chronic conditions: {chronic_count}")

    # Count service-connected
    service_connected_count = df_silver.filter(pl.col("service_connected") == True).shape[0]
    logger.info(f"  - Service-connected: {service_connected_count}")

    # Count with Charlson Index mapping
    charlson_count = df_silver.filter(pl.col("icd10_charlson_condition").is_not_null()).shape[0]
    logger.info(f"  - Problems with Charlson Index mapping: {charlson_count}")

    logger.info("=" * 70)

    return df_silver


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transform_problems_silver()
